# Faction politics

## Purpose and scope

How the political consequences in [`docs/requirements/POLITICS.md`](../requirements/POLITICS.md)
will be built. This document owns three capabilities, kept in separate parts below:

- **The political ripple** — propagating a single player act along a faction's alliances and
  rivalries, and the faction-relation graph it reads. Everything up to *Outstanding decisions*.
- **[The faction demand](#the-faction-demand)** — the ask, the deadline, the consequence, and
  moving a second faction on resolution.
- **[Standing as a content gate](#standing-as-a-content-gate)** — refusing an action until the
  player's standing on some axis reaches a threshold, and showing the threshold before it is
  reached. The final part of this document.

It does not own Reverence, which is a second per-faction axis and belongs to
[`RELIGION.md`](RELIGION.md) — but the **gate** that reads Reverence is here, not there, and
`RELIGION.md` links to it rather than restating it.

## The build

The capability is two pieces, and the second is the one that was missing.

**1. Seed the edges.** A one-time pass at game start writing designed rivalry and alliance
goodwill between the campaign's hand-authored factions. This is where the NPC↔NPC write
machinery actually earns its keep. Because both drift functions short-circuit on non-player
pairs, **whatever is seeded stays exactly as written, forever, and is serialised for free**
by `Faction.relations` [V]. Zero maintenance, zero new saved state. `requirements/POLITICS.md`
notes "only a handful of hand-authored factions carry the campaign" — exactly the scale at
which a hand-authored seed table beats a procedural one.

**2. Run the ripple.** Read edges, write player↔X.

**Reading the graph: no cache, no reflection.** `Faction.relations` is private, but
`RelationWith(Faction, allowNull)` plus `FactionManager.AllFactionsListForReading` is enough.
Every ally/enemy helper on `FactionManager` filters on `PlayerRelationKind` and is therefore
player-relative and useless for an arbitrary A [V]. The enumeration is O(n²) in **faction
count** — vanilla's world-creation UI caps at 12 — so at n≈20 that is ~400 reference
comparisons, cheaper than one pathfinding call, and it runs per political act, not per tick.
Vanilla does the same shape in `SettlementDefeatUtility.CheckDefeated` [V].
**Do not cache**: a cache would need invalidating from `Notify_RelationKindChanged`, and a
stale per-client cache feeding simulation is **T-20** exactly.

**Where the rules live: Harmony postfixes on the `Faction.Notify_*` act hooks.** The options
the ticket named are ruled out [V]:

- **A `HistoryEventDef` listener does not exist.** `HistoryEventsManager.RecordEvent`
  dispatches to exactly one place and has no listener registry. Worse,
  `TryAffectGoodwillWith` only records a `HistoryEvent` when the player is a party, so a
  `RecordEvent` postfix cannot see NPC↔NPC changes at all.
- **A `QuestPart`** is right for quest-scoped consequences and wrong as the home of a standing
  rule — it exists only while its quest does.
- **A `WorldComponent`** is tick-safe but the ripple is event-driven; nothing needs polling.

The act hooks are already vanilla's convergence point, and several carry the actor [V]:

| Hook | Carries the actor? |
|---|---|
| `Notify_MemberCaptured(Pawn, Faction violator)` | **Yes** — `violator` |
| `Notify_MemberStripped(Pawn, Faction violator)` | **Yes** — `violator` |
| `Notify_MemberTookDamage(Pawn, DamageInfo)` | via `dinfo.Instigator.Faction` |
| `Notify_MemberDied(...)` | via `dinfo` |
| `Notify_BuildingTookDamage(Building, DamageInfo)` | via `dinfo` |

**Compounding is bounded structurally, not by a budget.** The runaway exists only if the hook
listens to the *effect*. **Do not postfix `TryAffectGoodwillWith`** — every ripple write is
one, so a postfix re-enters on its own output, unbounded [V]. **Postfix the act hooks**: a
ripple write is not an arrest, a death or a strip, so it raises no act hook and cannot
re-enter. One hop becomes a property of the design rather than a counter someone has to get
right [I].

Two residual paths, named rather than ignored:

- **The gameplay loop is real but is the game working** — a ripple crossing −75 flips kind,
  lords re-evaluate, someone gets shot, `Notify_MemberTookDamage` fires. It is mediated by
  simulated combat over many ticks [V on the mechanism, I on the assessment].
- **Hysteresis makes negative ripples sticky.** `CheckKindThresholds` goes Hostile at ≤−75 but
  returns to Neutral only at ≥0 — a 75-point climb back [V]. That argues for a per-faction
  ripple cooldown, and for hostility crossings being authored rather than accumulated.

**Observing the acts** [V]: kidnap, harm, kill and strip are **free** — the hooks exist and
carry both operands. "Built something noxious" needs new detection, but
`SettlementProximityGoodwillUtility.AppendProximityGoodwillOffsets` is `public static` and
takes an arbitrary tile, so the distance maths is reusable and only the trigger needs
authoring. "Served a faction" is a quest outcome and is *[The faction demand](#the-faction-demand)*
below — it needs none of this machinery, because its second-faction write is player↔X.

**What the player sees**: VEF's queue already sends a letter naming the faction and the
magnitude, on the tick the impact lands — see *Available mechanisms*. That is the display half,
and it ships.

⚠ **One vanilla quirk to not inherit** [V]: `Notify_MemberCaptured` hardcodes `OfPlayer` as
the offender **regardless of `violator`**. If an NPC faction arrests another faction's pawn,
vanilla charges the player. Harmless today; live the moment we seed NPC hostility and their
lords start taking prisoners. **A ripple built on this hook must read `violator` itself.**

### Cost

| Piece | Cost |
|---|---|
| Ripple tunables, seed table | **XML** — two new Def types |
| `permanentEnemy` audit on our own faction defs | **XML**, but **T-07** — before world creation, not patchable after |
| Reading the graph | **New C#**, ~20 lines |
| Applying the ripple, with letter, delay and persistence | **Free** — VEF carries it |
| Observing kidnap / harm / kill / strip | **Patch** — 4 Harmony postfixes |
| Seeding the edges at game start | **New C#**, ~30 lines |
| Persistence | **Free**, except a cooldown ledger |
| Multiplayer | **Free**, if the constraints below hold |

**Aggregate: two new Def types, ~80–100 lines of C# in the existing `ArchinityAltar.dll`,
four Harmony postfixes.** No new assembly — `Archinity.Altar` already ships a Harmony
instance and references `Assembly-CSharp` and `0Harmony` [V].

**The expensive item is not code: authoring the seed table.** A rivalry graph that reads as
politics rather than noise is design work over the campaign's hand-authored factions.

## Persistence and multiplayer

**Multiplayer syncs no goodwill at all** — `Multiplayer.dll` syncs exactly two `Faction`
members, `allowRoyalFavorRewards` and `allowGoodwillRewards`, and there is no `SyncMethod` for
`TryAffectGoodwillWith` [V]. Confirmed from the other direction: zero hits across every
assembly in the Multiplayer and MP-Compat folders.

**No explicit synced command is needed for the ripple**, and the requirement to wrap every
write in one is stricter than the real rule. `docs/engine/determinism.md` § *Why `Rand` inside
a synced tick is safe*: the hazard is a mod consuming the shared stream a different number of
times per client. The ripple is **already downstream of a synced action** — an arrest is
simulated identically on both clients, so `Notify_MemberCaptured` fires on both at the same
tick in the same order [V on the model, I that this ripple qualifies].

What must hold:

1. **No `Rand` in the ripple path.** `TryAffectGoodwillWith`, `CheckKindThresholds` and
   `Notify_RelationKindChanged` consume none [V].
2. **No `ModSettings` read during simulation** — **T-18**. Every tunable is a Def.
3. **Deterministic iteration order.** `AllFactionsListForReading` is insertion-ordered.
   **Never iterate a `Dictionary` or `HashSet` of factions** to build the ripple set [I].
4. **No cached ally/enemy set** — T-20 exactly.
5. **A player-facing "run the ripple" button would need a synced command**, because a UI click
   is not a simulated event. That is the case the "every write is synced" rule is actually
   about [I].

One shared player faction means one goodwill number per NPC faction, so letters are shared and
any per-player filtering is draw-time only (**T-21**).

## Failure and recovery

- **The alliance ripple silently does nothing until edges are seeded.** This is the failure
  mode most likely to ship: the mechanism reads as green, and produces a feature that never
  fires. Seeding is a prerequisite, not a polish step.
- **Gate E swallows writes silently.** A ripple that reports "−6 with B" in a letter while
  `TryAffectGoodwillWith` returned `false` is a lie to the player. **Check the `bool` before
  writing the letter** — the requirement's legibility clause depends on it [V]. VEF's
  `DoImpact` gets this wrong and must be overridden.
- **Magnitudes are not applied literally.** `CalculateAdjustedGoodwillChange` amplifies any
  change moving toward natural goodwill by 25% of the remaining gap; a −6 ripple can land as
  more than −6 [V]. And `GoodwillWith` is clamped by `GetMaxGoodwill`, so a positive ripple
  into a faction already at its situation cap is a silent no-op [V].
- **Two of our own factions cannot participate**, by their own defs, and it is **T-07** — not
  patchable after worldgen.

## Status

**Verified available mechanism. Not an implementation commitment.**

Established by [Multi-faction goodwill writes and the political ripple](https://github.com/cjd721/Rimworld-Archinity/issues/90),
evidence class **READ** — a fresh decompile of `Assembly-CSharp.dll` (1.6.4871 rev590, the
version `docs/data/MOD-SNAPSHOT.md` pins), plus `Multiplayer.dll`, `VEF.dll` and
`FactionTerritories.dll`, shipped DLC XML, and a wide pass over all 155 mods.

Three findings reframe the capability, and each is load-bearing:

1. **The ripple barely needs NPC↔NPC writes.** It *reads* the NPC graph and *writes*
   player↔X.
2. **The graph it reads is empty.** No NPC↔NPC alliance exists in a fresh world, so the
   alliance ripple cannot fire at all. Seeding the edges is the real NPC↔NPC write, and it
   was never costed.
3. **The apply half already ships** in VEF, a mod the campaign already depends on.

## Available mechanisms

### The goodwill pipeline, with the gates stated correctly

`Faction.TryAffectGoodwillWith` has no "one side must be the player" requirement, and its
write and mirror are unconditional [V]. `CheckKindThresholds` flips relation kind at ≤−75
Hostile and ≥+75 Ally for any parties, and the tail of `Notify_RelationKindChanged`
(`attackTargetsCache.Notify_FactionHostilityChanged` plus `Lord.Notify_FactionRelationsChanged`
on every map) is ungated — so NPC pawns really do re-target [V]. NPC↔NPC goodwill never
drifts: `CalculateAdjustedGoodwillChange` and `CheckReachNaturalGoodwill` both short-circuit
on non-player pairs, so whatever is written stays written [V].
`SetRelationDirect` `Log.Error`s when both sides `HasGoodwill`; use `TryAffectGoodwillWith` [V].

**`CanChangeGoodwillFor` gates on more than `HasGoodwill` / `permanentEnemy` / `defeated`.**
The full set [V]:

| Gate | Condition | Scope |
|---|---|---|
| A | `def.permanentEnemyToEveryoneExceptPlayer && !other.IsPlayer` | NPC↔NPC only |
| B | `other.def.permanentEnemyToEveryoneExceptPlayer && !IsPlayer` | NPC↔NPC only |
| C / C' | `permanentEnemyToEveryoneExcept` — an **allow-list**, evaluated symmetrically | NPC↔NPC only |
| D | positive changes blocked while the player assaults a settlement | player only |
| E | `QuestUtility.IsGoodwillLockedByQuest(a, b)` | **any pair** |

**Gate C already fires on our own content** [V], and this is a campaign fact, not a detail:

| Faction | Flag | Consequence |
|---|---|---|
| `Empire` (Royalty) | `permanentEnemyToEveryoneExcept`, 9 entries | **Empire↔Glitterites and Empire↔Free Companies are unwritable in both directions, forever.** Player↔Empire is fine |
| `Archinity.Glitterites` | `permanentEnemy` | **No goodwill write to or from them ever succeeds**, player included |
| Archons (patched) | `permanentEnemy`, deliberately | Same |
| `Archinity.Drifters` free companies | neither, deliberately | Neutral and fully writable |

**Gate E applies to arbitrary pairs**, so a live `QuestPart_FactionGoodwillLocked` silently
no-ops a ripple write.

### The graph is empty

`Faction.TryMakeInitialRelationsWith` is the only def-driven relation setup, and its
`GetInitialGoodwill` returns exactly one of `-100`, `-80`, or `0` [V].

**It can therefore never return ≥75, so it can never produce `FactionRelationKind.Ally`.
There is not one NPC↔NPC alliance edge anywhere in a fresh vanilla world, and nothing in
vanilla ever creates one** — all 48 `TryAffectGoodwillWith` call sites have `Faction.OfPlayer`
on a side. **The alliance ripple has zero edges to follow.** [V]

The rivalry side is not empty but is useless as a political signal: the only negative edges
are the blanket `naturalEnemy` (−80, hostile to everyone) and `permanentEnemy` (−100, and
unwritable) flags on rough/savage/pirate bases [V]. Those express "this faction hates
everybody", never "A hates B specifically". `permanentEnemyToEveryoneExcept` is the only XML
lever expressing targeted hostility, and its side effect is to make the relation
**unwritable** — so it cannot author a rivalry we then intend to move [V].

### VEF already carries the apply half

**`VEF.WorldComponent_FactionGoodwillImpactManager`** [V] — in VEF, which four other
capabilities already hang on ([#15](https://github.com/cjd721/Rimworld-Archinity/issues/15)). Its
`GoodwillImpactDelayed : IExposable` carries `impactInTicks`, `goodwillImpact`,
`factionToImpact`, a `HistoryEventDef`, letter label/desc/type, and a `virtual DoImpact()`
that writes `Faction.OfPlayer.TryAffectGoodwillWith(...)` and sends the letter. The component
scribes the queue `LookMode.Deep` and fires due entries from `WorldComponentTick`.

That is the ripple's write half complete: **a persisted queue, a tick delay, a
`HistoryEventDef`, a letter naming the faction, on a tick-safe apply point.** Three things
make it a fit rather than a coincidence:

1. It writes **player↔X only**, which is exactly what the ripple needs, and structurally
   cannot be misused for the NPC↔NPC half.
2. **`impactInTicks` is the gossip** — staggering allies hearing about the kidnapping over
   the following day is a field, not a design problem.
3. It is queued, not immediate, so it cannot re-enter the hook that queued it.

⚠ **One defect to override.** `DoImpact` sends the letter **unconditionally**, ignoring the
`bool` `TryAffectGoodwillWith` returned. Against gate E or a situation cap it announces a
goodwill change that did not happen. `DoImpact` is `virtual` — override it and check the
return.

### Prior art, and why none of it ships

- **RimPacts** is the only full autonomous NPC diplomacy sim in the corpus, with genuine
  broadcast ripples ([V] on defs and docs, [I] on method bodies). Already assessed: 623 types
  and a **57-field settings surface gating `Rand` inside its ticking component** — **T-18** at
  maximum scale — plus a second competing authority over the same relations.
- **Rim War** writes NPC↔NPC goodwill directly, but consumes `Rand` on threads and on the GUI
  thread, and **fully replaces `Faction.RelationWith` with a Harmony prefix** — the exact
  method this design depends on. It also models *drift*, not propagation of the player's acts,
  so it would fill the empty graph with noise attributable to nothing the player did.
- **Faction Territories' `AffectAlliedFactionGoodwill` is not a graph walk** — it resolves one
  stored ally id [V]. Recorded because the name is misleading enough to catch the next agent.

## Verification

READ-class throughout, from decompiled 1.6 assemblies at the pinned versions. The wide pass
covered both corpus roots, searching `.cs`, `.xml` and the `#Strings` metadata heap of every
`.dll`, then decompiling the hits — which killed two of the three candidates it surfaced.

Still open: a **STUB** pass loading a seeded relation set to confirm `CheckKindThresholds`
flips NPC pairs and their lords actually re-target; and a two-client smoke test for the desync
claim only, which belongs to
[the multiplayer verification regime](https://github.com/cjd721/Rimworld-Archinity/issues/16).
RimPacts' method bodies are [I] — identified from metadata names, not read.

## Outstanding decisions

1. **Whether Reverence modulates the ripple.** `requirements/POLITICS.md` says Reverence is
   "an input to this system, not a part of it", asserting a coupling without specifying it.
   **The owner is [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97)** — *Reverence
   and Goodwill, how the two axes touch* — which is open and carries exactly this question;
   [`RELIGION.md`](RELIGION.md) § *Outstanding decisions* hands it the same one from the other
   side. The two capability tickets that established the halves, **#90 and #98, are both closed**
   and are named here as provenance, never as owners: #90 established propagation along the
   relationship graph writing Goodwill, and #98 established Reverence as a quantity, the events
   that change it and its display, with `RELIGION.md` as its spec (superseding #52 and #74).
2. **The seed table's content** — which faction hates or loves which, and by how much. Design
   work, and the real cost of this capability.
3. **The `permanentEnemy` audit**, before world creation. T-07.

---

## The faction demand

A demand is a faction asking the colony for something specific, on a clock, with a stated
consequence for failing. This part owns the shape of one demand: the ask, the deadline, the
consequence, refusal, and the second faction that moves when the demand resolves.

It does not own **how large** a retaliation raid is — that is
[the storyteller](https://github.com/cjd721/Rimworld-Archinity/issues/60)'s, and §4 takes the
carrier [`PRESSURE.md`](PRESSURE.md) names so that the magnitude stays a def field #60 tunes.

⚠ **It does own the cap on concurrent pending demands, and this reverses an earlier
disclaimer.** An earlier draft said this document "does not own how often demands arrive —
##60's", and then built `QuestNode_DemandBudget` (§5), which is a frequency cap. Meanwhile
`PRESSURE.md`'s scope claims only *magnitude* for #91 — *"#91 says what a refusal fires, this
document says how big it is"* — so both documents were disclaiming the same thing. **The cap is
claimed here**: the mechanism, its evaluation point and its failure mode are §5's, and only the
*number* is a requirement (*Outstanding decisions* 1). What remains genuinely unowned is
narrower and is recorded as a gap there: the **arrival cadence** — how often the storyteller
offers a demand in the first place — which `PRESSURE.md` does not claim for #91 and this
document does not build.

It does not own the
**ally-aid battle at a tile** ([#92](https://github.com/cjd721/Rimworld-Archinity/issues/92)),
which is a demand wearing this shell plus a world object and an in-absentia resolution. It does
not own **standing as a gate**, which is [the final part of this document](#standing-as-a-content-gate)
— and that part confirms the guess made here: `QuestPart_RequirementsToAccept` is the surface,
and the skill-threshold ask in §3 below is the same build with a different predicate.

### The build

**The demand is XML. Only the refusal is code** — and that is the reverse of what was assumed.

Four of the five pieces the capability needs ship today, in pure XML:

| Piece | Carrier |
|---|---|
| The ask | `QuestScriptDef` + `QuestNode_Sequence` over ~215 XML-authorable `QuestNode_*` blocks [V] |
| The deadline | `QuestScriptDef.expireDaysRange` before accept; `QuestNode_Delay { isQuestTimeout }` after [V] |
| The countdown the player sees | `Alert_QuestExpiresSoon`, the Quests-tab countdown, `QuestPart_Delay`'s red alert — automatic [V] |
| **Goodwill with a faction other than the asker** | `QuestNode_ChangeFactionGoodwill`, naming any faction. Free [V] |

**The fourth line is the one that was wrong everywhere else.** `QuestPart_FactionGoodwillChange`
calls `Faction.OfPlayer.TryAffectGoodwillWith(faction, …)`. The hardcoded operand is the
**player's** side; `faction` is a plain public field the XML node sets, guarded only against
self-writes [V]. `SlateRef<Faction>` accepts a bare `FactionDef` defName, so `<faction>Empire</faction>`
is legal [V, `Verse.ConvertHelper`]. *Serving A costs standing with B* is one XML node, and it needs
none of the ripple's machinery — it is a player↔B write, not NPC↔NPC.

Attribution comes with it for free. `Faction.TryAffectGoodwillWith` emits
`MessageGoodwillChangedWithReason` — faction, before, after and the `HistoryEventDef` label —
whenever a `reason` is passed and one party is the player [V]. `<reason>` is an XML field on the
node. POLITICS.md's legibility clause is satisfied by authoring, not by code.

Reference file to copy: `Data/Core/Defs/QuestScriptDefs/Script_TradeRequest.xml` — 100% XML, a
faction-flavoured deadline-bearing delivery quest.

#### 1. Refusal — `QuestPart_DemandRefused` + `QuestNode_DemandConsequence`

Declining a demand means letting the offer expire, and **vanilla emits nothing when it does**.
`ChoiceLetter.Option_Reject` only removes the letter; `Quest.dismissed` is a UI hide toggle;
`Quest.QuestTick` calls `CleanupQuestParts()` on expiry and returns without a signal [V].

**Mechanism.** `QuestPart.Cleanup()` is `virtual`, and `Quest.CleanupQuestParts()` is the single
convergence point for every terminal transition — offer expiry and `Quest.End` alike [V].
`Quest.State` returns `EndedOfferExpired` exactly when `TicksUntilExpiry == 0 && acceptanceTick < 0`,
which is the condition `QuestTick` fires cleanup on, so a state read inside `Cleanup()` is the
discriminator between *refused*, *failed* and *succeeded* [V]. No signal is needed, and that is
what makes this work at all.

**State.** On the part: `Faction asker`, a short `List<GoodwillDelta>` (faction, amount,
`HistoryEventDef`), and an optional `QuestScriptDef retaliation`. Nothing global, nothing new
in the world.

**Persistence.** `QuestPart.ExposeData`, scribed inside the quest [V]. A save predating the part
has no such part — no migration, nothing to back-compat.

**Change.** `Cleanup()`, once, guarded on `quest.State`. Each delta goes through
`Faction.OfPlayer.TryAffectGoodwillWith(f, amount, canSendMessage: true, reason: def)`.
**Check the returned `bool` before telling the player anything** — gates C and E and the
`GetMaxGoodwill` clamp all no-op silently (see *Available mechanisms* in the ripple part above).

**Display.** Override `QuestPart.DescriptionPart` to state the consequence in the Quests tab
while the offer is still live; `MainTabWindow_Quests` reads `DescriptionPart` straight off the
parts list, ungated by `signalListenMode` [V]. The prose consequence also goes in
`questDescriptionRules`, which is what the offer letter shows.

**The XML alternative, and why it loses.** `QuestScriptDef.failedOrExpiredHistoryEvent` *does*
fire on `EndedOfferExpired` — `CleanupQuestParts` calls `IdeoUtility.Notify_QuestCleanedUp`
unconditionally and its `EndedOfferExpired` branch records the event [V]. But the event is
constructed as `new HistoryEvent(def)` with **no faction argument** [V], so a
`HistoryEventsManager.RecordEvent` postfix cannot tell which faction was refused without one
`HistoryEventDef` per (demand × faction) pair. Recorded because the field looks like the answer.

#### 2. Paired rival demands — `QuestNode_RivalDemands` over `QuestPart_Choice`

POLITICS.md calls paired demands from rivals "the sharpest instrument found". **Two separate
quests cannot express it**: `QuestGen.GenerateNewSignal` stamps every in-quest signal `Quest{id}.`
and `Quest.Notify_SignalReceived` drops any non-`global` tag that does not start with its own
prefix, so quest A cannot hear quest B [V]. Exactly four `global: true` signals exist in the whole
assembly [V].

So make it **one quest with two branches**. `QuestPart_Choice` is vanilla's accept-time chooser:
`Choose(choice)` deletes the non-chosen choices' `QuestPart`s from the quest [V],
`PreventsAutoAccept` is true at two or more choices [V], and each `Choice` carries an arbitrary
`List<QuestPart>`. Put a pair of `QuestPart_FactionGoodwillChange` in each branch — serve A: +A,
−B; serve B: +B, −A. One letter, one tab row, and **the player is told before choosing because
the choice UI is the accept UI**.

Multiplayer already syncs it: `PatchQuestChoices.Choose` is a registered `SyncMethod` [V]. There
is no `QuestNode_` wrapper for `QuestPart_Choice` — only `QuestNode_GiveRewards.variants` builds
one — so the node is ours, ~35 lines.

**Open:** the choice UI renders each branch through its `Reward`s, so a branch with none may draw
empty **[I]**. Give each branch a real reward; that reward is the demand's payment anyway.

**Rejected:** two quests plus a `QuestPart_ExclusiveGroup` ending its siblings. It needs the
cross-quest wiring the engine deliberately forbids, and doubles the notification cost the
requirement is trying to cap.

#### 3. Asks pointed at capability

| Ask | Verdict |
|---|---|
| **Silver** | Free. The deliberately boring control case. |
| **Delivery to a named tile** | Free. `Script_TradeRequest.xml`, 100% XML [V]. |
| **A loaned colonist for a duration** | Ships. `QuestNode_LendColonistsToFaction` is XML-reachable [V]. Two constraints: it reads the pawns out of a `Thing` with a `CompTransporter`, and `Complete()` returns them by shuttle only for `Faction.OfEmpire`, otherwise by drop pod [V]. The mechanism is sound; the fiction is wrong for a neolithic asker. |
| **A pawn skill threshold** | New. No `QuestPart_RequirementsToAcceptSkill` exists [V]. ~35 lines copying `QuestPart_RequirementsToAcceptColonistWithTitle` exactly: `CanAccept()` sweeps `PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive_Colonists`, `CanPawnAccept(p)` tests the skill, `RequiresAccepter => true` makes the accepter pawn the specialist [V on the donor, I on the composition]. Display is free — `MainTabWindow_Quests.DoAcceptanceRequirementInfo` draws the red box, and `QuestUtility.CanAcceptQuest` refuses the accept [V]. **The button is greyed, not disabled** — `DoAcceptButton` sets `GUI.color = Color.grey` plus a warning tooltip while `Widgets.ButtonText` still fires; the refusal is one layer down in `AcceptQuestByInterface`, which emits `"MessageCannotAcceptQuest"` [V]. See [*Standing as a content gate*](#standing-as-a-content-gate) §2. |
| **An embargo on trading with a third faction** | New. Nothing hears trading; `Faction.Notify_PlayerTraded(float, Pawn)` is the sole convergence point and raises no signal [V]. One ~6-line Harmony postfix broadcasting a global signal, plus a listener part — see *The `Quest.` prefix*, below. |

#### 4. The refusal raid — what fires it, not how big it is

`QuestPart_DemandRefused.Cleanup()` on the expiry path; `QuestNode_End { Fail }` on the
post-accept path. **Magnitude and composition belong to
[#60](https://github.com/cjd721/Rimworld-Archinity/issues/60)**, whose spec is
[`PRESSURE.md`](PRESSURE.md), and are not settled here. This document owns the **trigger** and
nothing else about the raid.

**The carrier is the one `PRESSURE.md` names, and this resolves a contradiction rather than
stating a preference.** `PRESSURE.md` § *The build* selects
`VEF.Storyteller.IncidentWorker_RaidEnemySpecial` plus a `VEF.Storyteller.IncidentDefExtension`
carrying `forcedFaction`, `forcedStrategy` and `forcedPointsRange`, and names *"a faction
demand's refusal raid"* as one of its intended users [V]. An authored `IncidentDef` on that
worker is pure XML, and — the load-bearing part — **its magnitude is a def field
(`forcedPointsRange`) that #60 owns and tunes without touching anything in this document.**
The refusal path's job is to fire that `IncidentDef`; the seam that fires it from a quest is
the one piece not yet read — **[I]**, and the only open item in this section.

> ⚠ **Inherit `PRESSURE.md`'s sentinel with the worker.** `IncidentDefExtension.forcedPointsRange`
> defaults to `IntRange.Zero` while `ResolveRaidPoints`'s fall-through test is `== IntRange.One`,
> so an `IncidentDef` on this worker **without** an explicit `forcedPointsRange` gets a raid
> budget of zero and reports nothing [V, `PRESSURE.md`]. A refusal that silently fires an empty
> raid is worse than one that fires none.

**Rejected as the primary route: VFE Medieval 2's raid-on-fail node — and the reason is
ownership, not quality.** `QuestNode_SpawnRaidOnFail` / `QuestPart_SpawnRaidOnFail`
(`oskarpotocki.vfe.medieval2`, `1.6/Assemblies/VFEMedieval.dll`) is XML-reachable and composes
`IncidentParms` + `raidArrivalMode` + `raidStrategy` **directly**, rather than going through
`IncidentWorker_RaidEnemy.TryExecuteWorker` [V]. That is exactly what disqualifies it here:
on that path `forcedPointsRange` never applies, and the shipped scaling is a hardcoded
`QuestUtils.GeneratePawnKindList(faction, points * 1.5f, site)` [V]. Reimplementing it would
put a magnitude constant in the section that says magnitude is #60's — which is the
contradiction the audit caught, and `PRESSURE.md` is right on ownership.

It stays recorded as the **fallback**, because it also reads `site` / `siteFaction` / `map` off
the slate and so is the shape a *site-shaped* demand would want —
[#92](https://github.com/cjd721/Rimworld-Archinity/issues/92)'s ally-aid battle is the obvious
candidate. **If that fallback is ever taken, the `× 1.5` is handed to #60 as an open parameter,
not reimplemented as a literal**: it ships as a def field with no default of ours, and #60 sets
it alongside every other magnitude. The reimplementation is ~25 lines in the same shape.

#### 5. The notification budget — `QuestNode_DemandBudget`

XML gives two partial caps and no category cap:

- `QuestScriptDef.minRefireDays` — blocks re-selection of the **same root** within N days and
  counts `NotYetAccepted` quests [V]. Evaluated only in `NaturalRandomQuestChooser`.
- `QuestNode_QuestUnique` — dedupes by tag, optionally per faction, but tests only
  `State == Ongoing`, so a pending offer does not block a second [V].
- VEF's `GameComponent_QuestChains.TryScheduleQuest` refuses while any quest with the same root
  is `Ongoing` **or** `NotYetAccepted` [V] — the better per-script cap, if demands are chain-granted.

The build is a `QuestNode` whose `TestRunInt` counts `Find.QuestManager.QuestsListForReading` for
`State == NotYetAccepted` carrying a demand tag and returns `false` above a cap held in a Def
**instance** — not a new Def type; an existing settings-style Def carries the field, which is
what keeps it out of `ModSettings` (**T-18**). Deterministic, allocation-free, no `Rand`.
~15 lines.

**This document owns the cap.** It is a frequency control and *Purpose and scope* now says so:
`PRESSURE.md` claims only magnitude for #91, so leaving this disclaimed would have stranded it
between two specs. **Only the number is a requirement** — see *Outstanding decisions* 1, which
also records the one frequency question neither document owns.

⚠ **The cap holds only on the paths that call `TestRun`.** A chain-granted demand never does —
**T-71** — so if demands are granted through VEF's chain component, the cap must be enforced in
the grant path as well or it is inert exactly where it is most needed. VEF's own
`GameComponent_QuestChains.TryScheduleQuest` refusal (above) is the per-script cap that applies
there; a *category* cap on that path is not built.

#### 6. VEF quest chains — what they buy and what they do not

`QuestChainExtension`, a `DefModExtension` on a `QuestScriptDef`, gives XML `conditionSucceedQuests`,
`conditionFailQuests`, `conditionEither`, `conditionSucceedQuestsCount`, `conditionMinDaysSinceStart`,
`requiredResearch`, `isRepeatable` / `mtbDaysRepeat`, `grantAgain{OnFailure,OnSuccess,OnExpiry}` and
`delayTicksAfterTriggering` [V]. `GameComponent_QuestChains` prefixes `Quest.CleanupQuestParts` and
already distinguishes `EndedOfferExpired` from success and failure [V].

That is cross-quest **conditioning** in pure XML — a retaliation or follow-up demand granted after
an earlier one resolved. It is not cross-quest **exclusion**, which is why paired demands are one
quest (§2). Three defects make the refusal path unusable as shipped — **T-71**, **T-72** and
**T-73**; see *Failure and recovery*.

#### The `Quest.` prefix — how XML hears a world event

`QuestGenUtility.HardcodedSignalWithQuestID` returns a signal string **verbatim** when it starts
with `"Quest"` and contains a `'.'`; every other form gets stamped `Quest{id}.` [V]. Independently,
`Quest.Notify_SignalReceived` accepts any signal whose `global` flag is set, regardless of prefix
[V]. So a signal broadcast as `new Signal("Quest.ArchinityPlayerTraded", args, global: true)` is
the one shape an arbitrary `QuestScriptDef` can put in an `<inSignal>` and actually receive.
`signalListenMode` still gates the receiving part.

This is the general bridge from any Harmony-observed act to XML quest logic, and it is what the
embargo ask and any future "we noticed you did X" demand run on. [V on both halves, **[I]** on the
composition — nothing has been built on it yet.]

#### Cost

| Piece | Cost |
|---|---|
| The demand — ask, deadline, countdown, alert, letter | **XML** — copy `Script_TradeRequest.xml` |
| Moving a second faction on resolution, with attribution | **XML** — `QuestNode_ChangeFactionGoodwill` with `<reason>`. Free |
| Refusal as an act, with its consequence | **New C#**, ~65 lines |
| Paired mutually-exclusive rival demands | **New C#**, ~35 lines |
| Skill-threshold ask | **New C#**, ~35 lines |
| Embargo ask | **Patch** — 1 Harmony postfix (~6 lines) + listener part (~20) |
| Refusal raid | **XML** — an `IncidentDef` on VEF's `IncidentWorker_RaidEnemySpecial` (§4). Magnitude → #60. The site-shaped fallback is ~25 lines, and hands its `× 1.5` to #60 as a def field |
| Category cap on pending demands | **New C#**, ~15 lines; the number → requirements. **Owned here** |
| Loaned specialist, delivery to a tile, silver | **Free** — vanilla |
| Persistence | **Free** — `QuestPart.ExposeData` |
| Multiplayer | **Free** |

**Aggregate: ~176 lines of C# in the existing `ArchinityAltar.dll` (65 + 35 + 35 + 26 + 15),
one Harmony postfix, and no new Def types.** No new assembly.

**The aggregate was wrong in both figures and the table is what corrects it.** An earlier draft
claimed "two Harmony postfixes, two new Def types", carried over from the ripple part's
aggregate above. This part specifies exactly **one** postfix — `Faction.Notify_PlayerTraded`,
for the embargo ask — and **zero** new Def *types*: the demand budget's cap is a field on a Def
**instance** (§5), and everything else is a `QuestScriptDef`, a `QuestPart` or an `IncidentDef`,
all of which are existing types. The line estimate was sound and is unchanged.

**The expensive item is not code: authoring the demands.** An ask that is "inconvenient and
pointed at something the colony could build but has not" is design work per faction per era.

### Persistence and multiplayer (the demand)

Every piece of demand state is a `QuestPart` scribed inside its quest [V]. Nothing new is added
to the world, nothing needs seeding, and a save that predates the feature loads unchanged.

`SyncMethod.Register(typeof(Quest), "Accept")` is bare — **either founder can accept any demand,
with no faction predicate** [V]. `SyncFields.SyncQuestDismissed` watches `Quest.dismissed` from
`MainTabWindow_Quests.DoDismissButton` [V], so **one founder dismissing a demand hides it for
both**. `PatchQuestChoices.Choose` is synced [V], so the rival-demand branch pick is MP-safe for
free. Whether any of that needs an ownership or consent step is a *requirement* — see below.

Everything in this build runs inside `QuestManagerTick` or `Quest.CleanupQuestParts`, already on
the synced tick, and consumes no `Rand`, no `ModSettings` (**T-18**) and no client-local cache
(**T-20**). Every tunable ships as a Def.

Under async time, `MultiplayerAsyncQuest.TryGetQuestMap` binds a quest to a map only when it
carries a whitelisted `QuestPart` type with a `mapParent` field pointing at a player home map [V].
None of our parts are on that list, so a demand ticks at **world** speed — right for a diplomatic
clock. The hazard is the reverse: a demand that also carries, say, `QuestPart_PawnsArrive` silently
binds to that map's clock and its deadline then runs at that map's speed [V on the mechanism,
**[I]** on the consequence].

### Failure and recovery (the demand)

- **A refusal consequence written in XML against a not-yet-accepted quest is silently dropped.**
  `QuestNode_End` sets `signalListenMode` on the `QuestPart_QuestEnd` it builds but not on the
  `QuestPart_FactionGoodwillChange` it builds alongside, which keeps the `OngoingOnly` default [V].
  This is the failure most likely to ship, because the combination looks sanctioned — shipped
  Royalty XML uses `NotYetAcceptedOnly` in three files. **T-70.**
- **A chain-granted demand bypasses every XML gate.** VEF's `QuestUtils.CreateQuest` reaches
  `QuestGen.Generate`, which calls `root.Run()` and never `TestRun`, so `QuestScriptDef.CanRun` is
  never consulted and `QuestNode_QuestUnique`, the budget node and `minRefireDays` are all inert on
  that path [V]. Any cap that must hold for chain-granted demands has to be enforced in the grant
  path too. **T-71.**

  ⚠ **One supporting claim behind that trap was wrong; the trap is not.** An earlier draft
  supported it with *"only `IncidentWorker_GiveQuest.CanFireNowSub` and `NaturalRandomQuestChooser`
  run `CanRun`"* and marked it [V]. That is false: **14 further non-debug vanilla callers** run
  `CanRun`, among them `CompHackable`, `CompDissolutionEffect_Goodwill`, `FactionDialogMaker`,
  `Pawn_RoyaltyTracker`, three `QuestPart_SubquestGenerator_*`, `RoyalTitleUtility` and
  `StorytellerComp_RandomEpicQuest` [V]. **None of them is on VEF's chain-grant path**, which is
  why the trap's core — that a chain-granted quest reaches `QuestGen.Generate` without ever
  running `TestRun` / `CanRun` — is unaffected and confirmed. The corrected statement is *"the
  chain-grant path runs neither"*, not *"almost nothing runs `CanRun`"*.
- **VEF's `conditionFailQuests` never matches an expired offer.** `QuestExpired` writes only
  `tickExpired`; `QuestIsCompletedAndFailed` tests `outcome == QuestEndOutcome.Fail`, which only
  `QuestCompleted` writes [V]. A retaliation quest keyed that way is dead for exactly the refusal
  path a demand needs. **T-72.**
- **VEF's `grantAgainOnExpiry` is dead.** `TryGrantAgainOnExpiry` passes a tick count into
  `ScheduleQuestMTB`'s `mtbDays`, which becomes `Rand.MTBEventOccurs(300000, …)` for a five-day
  setting [V]. Its two siblings use `ScheduleQuestInTicks` correctly. **T-73.**
- **A goodwill write that silently no-ops still sends its message.** `TryAffectGoodwillWith`
  returns `false` under gates C/E and clamps at `GetMaxGoodwill`. The refusal part must read the
  `bool`; the XML node cannot, so a demand whose penalty targets a `permanentEnemy` faction is a
  lie told in a letter.

### Status (the demand)

**Verified available mechanism. Not an implementation commitment.**

Established by [The faction demand — ask, deadline, consequence](https://github.com/cjd721/Rimworld-Archinity/issues/91),
evidence class **READ** — a fresh decompile of `Assembly-CSharp.dll` (1.6.4871 rev590, the version
`docs/data/MOD-SNAPSHOT.md` pins), plus `Multiplayer.dll`, `VEF.dll` and `VFEMedieval.dll`, shipped
DLC XML, and a wide pass over both corpus roots.

Three findings reframe the capability:

1. **Moving a faction other than the asker is free in XML.** The prior framing — that every
   goodwill `QuestPart` is locked to one faction — mistook the *player's* hardcoded operand for the
   other side's. This deletes most of the assumed cost.
2. **The expensive half is refusal**, because vanilla has no decline verb and emits no signal on
   offer expiry. `QuestPart.Cleanup()` is the hook, and it is the only one.
3. **Cross-quest exclusion is structurally forbidden**, so paired rival demands are one quest, and
   `QuestPart_Choice` — already MP-synced — is the primitive.

### Available mechanisms (the demand)

#### Vanilla: the quest as a demand carrier

`QuestScriptDef` is fully XML-authorable — 87 shipped scripts use `<root Class="QuestNode_Sequence">`
with zero custom C#. Deadlines come in two independent systems: `expireDaysRange` before accept
(with `Alert_QuestExpiresSoon`, the tab countdown and `"LetterQuestRequiresAcceptance"` on the offer
letter, all free) and `QuestNode_Delay { isQuestTimeout }` after, which carries `alertLabel`,
`alertExplanation` and `ticksLeftAlertCritical` for a right-side alert that turns red [V]. There is
no `outSignalExpired` on either; the post-accept failure branch is the `<node>` nested in the delay,
and the pre-accept one does not exist.

`QuestNode_ChangeFactionGoodwill` fields: `inSignal`, `faction`, `factionOf`, `change`,
`canSendLetter`, `canSendMessage`, `ensureHostile`, `reason` [V]. `QuestNode_End` additionally
carries `goodwillChangeAmount` / `goodwillChangeFactionOf` / `goodwillChangeReason`, but
`goodwillChangeFactionOf` is a `SlateRef<Thing>` rather than a faction [V].

The two `QuestPart`s that take an arbitrary `(faction1, faction2)` pair —
`QuestPart_FactionGoodwillLocked` and `QuestPart_FactionRelationKind` — are a lock and a watcher,
never a writer [V].

#### Vanilla: what a demand cannot do

No decline verb [V]. No signal on offer expiry [V]. No cross-quest signalling [V]. No skill
acceptance requirement [V]. No trade detector [V]. No cap on pending offers [V]. `QuestManager`
itself caps nothing and `QuestManagerTick` merely ticks every quest [V].

#### VEF — quest chains

See §6 above. VEF's `VEF.Storyteller` namespace carries `QuestChainDef`, `QuestChainExtension`,
`GameComponent_QuestChains`, `FutureQuestInfo` and Harmony patches on `QuestManager.Add`,
`Quest.End` and `Quest.CleanupQuestParts` [V]. VEF is already a campaign dependency
([#15](https://github.com/cjd721/Rimworld-Archinity/issues/15)).

#### VFE Medieval 2 — the raid-on-fail node

See §4 above [V]. Surveyed and kept as the **site-shaped fallback only**: it bypasses
`IncidentWorker_RaidEnemy.TryExecuteWorker`, so `forcedPointsRange` never applies on its path
and magnitude would land here instead of with #60. The selected carrier is VEF's
`IncidentWorker_RaidEnemySpecial`, which [`PRESSURE.md`](PRESSURE.md) already names.

#### Prior art, and why none of it ships

- **RimPacts** (`wowgag.rimpacts`) ships a complete ultimatum system — `OpenUltimatumMenu`,
  `ConfirmUltimatum`, `UltimatumRefusedGoodwill`, `UltimatumAcceptGoodwill`,
  `UltimatumRefuseRaidChance`, `UltimatumCedeCooldownDays` **[I** — metadata names, not read**]**.
  Already rejected in the ripple part above: 623 types and a 57-field settings surface gating `Rand`
  inside its ticking component (**T-18** at maximum scale), plus a competing authority over the same
  relations.
- **Rim War** (`torann.rimwar`) ships `IncidentWorker_WarObjectDemand`, `GenerateDemands`,
  `TryGenerateItemsDemand`, `TryGenerateColonistOrPrisonerDemand` **[I** — metadata names**]**.
  Already rejected for threaded `Rand` and a Harmony prefix replacing `Faction.RelationWith`.
- **VFE Empire** and **Better Traders Guild** are the only other corpus assemblies referencing
  `QuestPart_FactionGoodwillChange` **[I]** — a metadata-heap hit names a string, not a call
  site, so it is an identification and never a read; both appear to use it and neither appears to
  extend it.

### Verification (the demand)

READ-class throughout, from decompiled 1.6 assemblies at the pinned versions. The wide pass covered
both corpus roots with `-a` over `*.dll` and `-g '!**/obj/**'`, attributed through
`tools/corpus.py --which`, and was validated against a control string before any negative was
trusted. Five separate sweeps for a declinable-quest verb (`*RejectQuest*`, `*DeclineQuest*`,
`*QuestReject*`, `*QuestDecline*`, `QuestPart_*Refus*`) returned **zero** across the corpus.

Still open, and cheap:

- **One in-game look** at how `QuestPart_Choice` renders a branch carrying no `Reward` — the only
  **[I]** in the paired-demand design.
- A two-client check that a demand's deadline runs at world speed under async time, which belongs to
  [the multiplayer verification regime](https://github.com/cjd721/Rimworld-Archinity/issues/16),
  together with VEF's `TryScheduleQuests()` call from `LoadedGame()` consuming `Rand` outside a
  synced tick [V on the call, **[I]** on whether it can desync a join].

Observable checks that the requirements are satisfied: a demand appears with a named faction and a
visible countdown; refusing it produces a message naming the *other* faction, the magnitude and the
reason; satisfying one rival demand visibly removes the other before the player commits.

### Outstanding decisions (the demand)

1. **"A manageable number of live diplomatic situations" names no number and no unit.** Concurrent
   offers or concurrent ongoing demands? Per faction, globally, or per era? The mechanism is ~15
   lines and is specified in §5, **and this document owns it** (*Purpose and scope*); only the
   number is outstanding, handed to
   [`requirements/POLITICS.md`](../requirements/POLITICS.md).

   ⚠ **A narrower frequency question has no owner at all.** The cap is on demands *pending at
   once*; nothing states how often a demand should be **offered**. This document does not build
   an arrival cadence, and [`PRESSURE.md`](PRESSURE.md) scopes itself to *magnitude* for #91 —
   *"#91 says what a refusal fires, this document says how big it is"* — so
   [#60](https://github.com/cjd721/Rimworld-Archinity/issues/60) does not claim it either.
   **Gap, no owner.** It is recorded rather than handed off, because handing it to a ticket
   whose own spec disclaims it is how the previous draft lost it.
2. **Nothing keeps the stated consequence and the actual consequence in sync.** There is no
   structured consequence field in the engine: what the player reads before answering is prose in
   `questDescriptionRules`, what fires is a `QuestPart`, and no tool compares them. An
   authoring-discipline requirement, currently unowned.
3. **Quest-board ownership under Multiplayer** is already an open question on
   `requirements/POLITICS.md` (from [#12](https://github.com/cjd721/Rimworld-Archinity/issues/12)).
   It now also covers **dismiss** — `Quest.dismissed` is synced, so either founder can hide a live
   demand from the other [V], which the current phrasing does not reach.
4. **Which demands exist, and what each asks for.** The real cost of this capability, and design
   work over the campaign's hand-authored factions.

---

## Standing as a content gate

Refusing an action until the player's standing with a faction reaches a threshold —
*"you may not accept this until you are at +50 with the Reach"* — and, per
[`requirements/POLITICS.md`](../requirements/POLITICS.md) § *Player information and agency*,
**showing the threshold before it is reached: a locked row with its number, not an absent one.**

This part owns the **gate mechanism** for every standing axis the campaign has — Goodwill here,
Reverence and Exaltation in [`RELIGION.md`](RELIGION.md), Influence, Intel and Trace in
[`CURRENCIES.md`](CURRENCIES.md). Those documents own their numbers; **the thing that refuses an
action on a number, and draws the refusal, is one mechanism and it is specified here once.**
`RELIGION.md` § *The build — religious institutions inside foreign factions* is the first
consumer and links back rather than restating.

It does not own **what is behind any particular gate** — which quest, which diplomatic action,
which threshold. Those are authoring, and the thresholds themselves are balance.

### The build

**Vanilla ships the enforcement seam, the display and a worked numeric-goodwill gate. What it
does not ship is a gate on a *number* at quest-accept time, or any XML reach to either.** The
build is one axis resolver plus two thin adapters, and it adds **no Harmony patch** beyond the
one [`RELIGION.md`](RELIGION.md) already costs for the comms console.

#### 0. Two premises in the ticket, re-verified — one holds, one does not

**Holds [V]:** there is no XML `QuestNode` wrapper for
`RimWorld.QuestPart_RequirementsToAcceptFactionRelation`. Vanilla ships **twelve**
`QuestPart_RequirementsToAccept` subclasses and exactly **four** `QuestNode_` wrappers —
`Bedroom`, `ColonistWithTitle`, `PlanetLayer`, `Research`. The faction-relation part can only be
added from C#.

**Does not hold, and it is the load-bearing half [V]:** the gate that exists **cannot express
the ticket's own question.** `QuestPart_RequirementsToAcceptFactionRelation.CanAccept()` tests

```
Faction.OfPlayer.RelationKindWith(otherFaction) == relationKind
```

— an equality against a **three-valued enum** (`Ally` / `Neutral` / `Hostile`), plus an
`acceptIfDefeated` escape. There is no threshold in it. Its `ReasonText` is one of three fixed
keys (`QuestAlliedTo` / `QuestNeutralTo` / `QuestHostileTo`) and **carries no number**, so even
its display half cannot show a carrot. *"+50 with the Reach"* is not expressible on this part and
never was.

⚠ **And the enum it tests is not a function of the number, which makes the substitution people
reach for wrong.** `Faction.RelationKindWith` reads the latched `FactionRelation.kind`, and
`CheckKindThresholds` flips to `Hostile` at ≤ −75, to `Ally` at ≥ 75, and back to `Neutral` only
on crossing **0** [V]. A faction sitting at +74 is `Ally` if it came down from 80 and `Neutral` if
it came up from 10. **"Ally" is not "goodwill ≥ 75"**, so authoring a standing gate as a relation
gate produces a threshold the player cannot reason about — and this is the hysteresis the ripple
part above already flags from the other side.

Its three call sites are all Archonexus victory nodes, all passing `acceptIfDefeated: true`, and
its sole constructor helper `QuestGen_Requirements.RequirementsToAcceptFactionRelation` is the only
member of that static class [V]. It is endgame plumbing, not a general mechanism.

**And *"relations barely gate anything in vanilla"* is wrong about the surface that matters
most.** `RimWorld.FactionDialogMaker.RequestAICoreQuest` does exactly what the ticket asks for,
today, in shipped code [V]:

```
if (faction.PlayerGoodwill < 40) { diaOption.Disable("NeedGoodwill".Translate(40.ToString("F0"))); }
```

`NeedGoodwill` is a shipped translation key — *"need {0} goodwill"* —
in `Core/Languages/English/Keyed/Dialog_Trees.xml` [V]. Three further options —
`RequestTraderOption`, `RequestOrbitalTraderOption`, `RequestMilitaryAidOption` — gate on
`Disable("MustBeAlly")`, carry a `Disable("WaitTime")` cooldown keyed on the scribed
`Faction.lastTraderRequestTick` / `lastMilitaryAidRequestTick`, and **all three spend goodwill**,
with the price rendered into the option label from
`-Faction.OfPlayer.CalculateAdjustedGoodwillChange(faction, -30)` [V]. So vanilla already ships
*a numeric standing threshold, shown before it is reached, on an action that costs standing to
take* — which is the whole of this capability and, separately, the whole of #73's price.

The correct conclusion is narrower and more useful than the ticket's: **the gate is not missing,
the *generality* is.** Every instance above is hand-compiled against `PlayerGoodwill`.

#### 1. The axis resolver — `StandingAxisDef`, one `switch`, ~25 lines

One `Def` type naming an axis, and one static resolver:

```
float Archinity.Altar.Standing.Of(Faction f, StandingAxisDef axis)
```

| Axis | Source | Evidence |
|---|---|---|
| Goodwill | `Faction.PlayerGoodwill => GoodwillWith(OfPlayer)` | [V] |
| Reverence | the per-faction record on `WorldComponent_Reverence` ([`RELIGION.md`](RELIGION.md) § *The build — Reverence* §1) | [V] on the component shape, [I] on the composition |
| Exaltation | `Pawn_RoyaltyTracker.GetFavor(faction)` ([`RELIGION.md`](RELIGION.md) § *The build — Exaltation*) | [V] |
| Influence / Intel / Trace | [`CURRENCIES.md`](CURRENCIES.md) | not read here |

The Def carries the axis's **label and its formatting**, so one gate produces *"need 50 goodwill
with the Reach"* and another *"need 40 Reverence with the Reach"* from the same code path.
**This is the only piece that is genuinely new**, and it is a `switch`.

`StandingGate` is the XML-loadable value both adapters take: an axis, a faction (a
`SlateRef<Faction>` on the quest side, a live `Faction` on the dialogue side), and a `float min`.

#### 2. Quest accept — `QuestPart_RequirementsToAcceptStanding` + its `QuestNode`

**The part. ~25 lines, and the donor is not the relation gate — it is the *wealth* gate.**
`RimWorld.QuestPart_RequirementsToAcceptPlayerWealth` is already the numeric-threshold shape [V]:
one `float requiredPlayerWealth`, a `CanAccept()` comparing it against a live number, an
`AcceptanceReport` carrying the threshold in its message, and a two-line `ExposeData`. Copy it,
replacing `WealthUtility.PlayerWealth` with `Standing.Of(faction, axis)` and adding a
`Scribe_References.Look` for the faction.

`QuestPart_RequirementsToAccept` is a 12-line abstract base — `CanAccept()`, `CanPawnAccept(Pawn)`,
`ShowInRequirementBox`, `Culprits` [V].

**The XML wrapper is ~20 lines, not a rabbit hole**, and this answers the ticket's first question
directly. `RimWorld.QuestGen.QuestNode_RequirementsToAcceptResearch` is the whole pattern [V]: a
`SlateRef<T>`, a `RunInt()` that does `QuestGen.quest.AddPart(new …{…})`, and a `TestRunInt(Slate)`
returning `false` when the requirement is already impossible so the quest is not offered at all.
Ours takes the three `StandingGate` fields and does the same. *(Copy the shape, not the spelling:
its XML field is `<reserach>`, misspelt identically in the C# field and in the two shipped Odyssey
quest defs that use it [V].)*

> **Give `TestRunInt` the deliberate answer, not the obvious one.** Returning `false` when standing
> is below the threshold means the quest is never *offered* — which deletes the carrot this
> capability exists to show. Return `true` unconditionally and let `CanAccept()` refuse, so the
> offer arrives visibly locked. Vanilla's research node returns `false` because a research-gated
> quest has no carrot value; a standing-gated one is the opposite case. `TestRunInt` is inert on
> VEF's chain-grant path in any case — **T-71**.

**Enforcement and display are both free, and both are vanilla's** [V]:

- `RimWorld.QuestUtility.CanAcceptQuest(Quest)` walks every `QuestPart_RequirementsToAccept` on the
  quest and returns the **first failing `AcceptanceReport`**. It is the single enforcement point;
  nothing else is consulted.
- `MainTabWindow_Quests.DoAcceptanceRequirementInfo` runs **only while
  `!selected.EverAccepted && !selected.Historical`** — precisely while the offer is pending —
  collects the unmet reasons through `ListUnmetAcceptRequirements()`, and draws them in a coloured
  info box under `"QuestAcceptanceRequirementsDescription"`, highlighting culprits. **Whatever
  string our `AcceptanceReport` returns is the locked row's threshold text**, for free, before the
  player accepts. That is `requirements/POLITICS.md`'s carrot clause satisfied by vanilla's own UI
  at zero cost.

⚠ **One precision, and *The faction demand* §3 above has been corrected to match.** That section
used to say the requirement box *"disables Accept"*. It does not literally:
`MainTabWindow_Quests.DoAcceptButton` sets `GUI.color = Color.grey` and attaches the reason as a
warning tooltip, but `Widgets.ButtonText` still fires. The **refusal** is in
`AcceptQuestByInterface`, which re-runs `QuestUtility.CanAcceptQuest` and emits
`"MessageCannotAcceptQuest"` [V]. The gate is enforced; the button is greyed rather than dead.
Nothing in either design depends on the difference, but a Harmony patch aimed at the wrong one
produces a visually correct, functionally open gate.

⚠ **`ShowInRequirementBox` is the anti-pattern to avoid, and vanilla ships one instance of it.**
`QuestUtility.CanAcceptQuest` consults **every** `QuestPart_RequirementsToAccept` regardless of the
flag, while `ListUnmetAcceptRequirements` skips the ones that set it false — so a part can enforce
while rendering nothing. `QuestPart_RequirementsToAcceptPlanetLayer` is the only vanilla override
and it is deliberate [V]. A standing gate that copies it is invisible and silent, which is exactly
the failure the legibility requirement is written against. Leave it at its default.

#### 3. The diplomatic action — a gated `DiaOption`, ~15 lines

For anything reached from the comms console — establishing an institution, calling a revolt,
asking for a specialist — the gate is `DiaOption.Disable(reason)`, which is **vanilla's own idiom,
on this exact surface, for this exact purpose** (§0). One helper called from the
`FactionDialogMaker.FactionDialogFor` postfix that [`RELIGION.md`](RELIGION.md) §
*The build — Reverence* D2 already costs:

```
opt.Disable(axis.needKey.Translate(min, Standing.Of(f, axis), f.Name));
```

**How it actually renders, because it is not a tooltip** [V]. `DiaOption.OptOnGUI` sets the label
colour to `DisabledOptionColor` (mid-grey) and **concatenates the reason into the label in
parentheses** — *"Establish a monastery with the Reach (cost: 40 goodwill) (need 60 Reverence)"* —
then passes `active: false` to `Widgets.ButtonText`. There is no `TooltipHandler` and no hover
behaviour: the whole gate is one grey, unclickable, fully legible line. That is exactly the
requirement's *"a locked row with its threshold"*, and it is free.

⚠ **`Disable` is last-writer-wins, and `FactionDialogMaker` has a near-blanket writer.**
`Disable(reason)` is a two-line setter, and the local `AddAndDecorateOption` inside
`FactionDialogFor` calls `opt.Disable("WorkTypeDisablesOption".Translate(…))` when the negotiator's
Social work type is disabled — **overwriting any reason already set** — but only for options passed
`needsSocial: true` [V]. `Disconnect`, the dev-mode debug options and `RequestRoyalHeirChangeOption`
pass `false` and are never touched. **This makes the conclusion stronger, not weaker:** a postfix
that *appends* its own options runs after that closure has finished with vanilla's, so our reasons
always survive; only a postfix that *modifies* an existing `needsSocial` option must not assume its
reason is the one that will show. `Disable(null)` greys with no text at all.

**The disabled half carries no delegate and is therefore free of every Multiplayer constraint** —
`disabled` and `disabledReason` scribe as plain values
([`docs/engine/determinism.md`](../engine/determinism.md) § *MP serialises the comms-console
dialogue*) [V]. The **enabled** action behind it is the constrained half, and that constraint is in
*Persistence and multiplayer*, below.

**The surrounding window already shows the axis the gate reads**, for Goodwill at least:
`Dialog_Negotiation.DoWindowContents` prints `Faction.GetInfoText` — *"goodwill: +N"* — in the same
window, and `Faction.CommFloatMenuOption` appends *"(Neutral, +12)"* to the console's float-menu row
before the dialogue is even opened [V]. A Reverence gate has no such companion until
[`RELIGION.md`](RELIGION.md)'s D1/D2 or [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61)
ships one, which is why the gate's reason string must name **both** the threshold and the current
value rather than the threshold alone.

#### 4. A third surface exists, and it is the ritual gizmo

`RitualBehaviorDef.workerClass` → **`RitualBehaviorWorker.CanStartRitualNow(TargetInfo, Precept_Ritual, Pawn, Dictionary)` returns a `string`**, and `Command_Ritual.ValidateDisabledState` re-runs it
**every GUI frame**, greying the gizmo and showing the returned text as its disabled reason [V].
That is a per-frame, arbitrary-predicate, reason-carrying gate on a surface the player is already
looking at — and it is a `workerClass`, so it takes any predicate including a standing threshold.
Three companions round it out [V]:

- `RitualObligationTargetFilter.CanUseTargetInternal` returns a `RitualTargetUseReport`, and
  `ShouldShowGizmo` is true when `canUse` is false **but `failReason` is non-empty** — vanilla
  deliberately keeps drawing the locked row.
- `RitualObligationTargetFilter.ShouldGrayOut(Pawn, …, out TaggedString)` greys a portrait and
  attaches a red tooltip.
- `RitualOutcomeComp.GetQualityFactor` returns a `QualityFactor` whose `count` is literally
  `have + " / " + need`, drawn by `Dialog_BeginLordJob.DrawQualityFactor` in green or red with a
  tick or a cross. **It is the cleanest have/need widget vanilla ships**, and it is the one to copy
  if a standing threshold ever needs a numeric readout of its own.

⚠ **But `CanStartRitualNow` is not sufficient on its own.** `Precept_Ritual.GetRitualBeginWindow`
calls it, fires a `RejectInput` message when the reason is non-empty — **and then returns the
dialog anyway** [V]. The gate re-asserts silently inside `RitualBehaviorWorker.TryExecuteOn`. Belt
and braces: also yield the reason from `RitualOutcomeComp.BlockingIssues`, which is what makes
`Dialog_BeginLordJob.CanBegin` return false.

This surface matters to [`RELIGION.md`](RELIGION.md) — Exaltation's title rite and the altar's
rites are gated things — and is recorded here because the gate mechanism is this document's.

#### 5. The surfaces that read nothing relation-shaped, and what to do instead

A negative worth stating, because four of them look like they should work [V]:

| Surface | Verdict |
|---|---|
| `ResearchProjectDef` | `CanStartNow` is exactly eight clauses — not finished, prerequisites, techprints, bench, mechanitor, analysed things, **not hidden**, inspection — and **not one reads faction standing**. `heldByFactionCategoryTags` is consumed only by `TechprintUtility.GetResearchProjectsNeedingTechprintsNow`, comparing against the immutable `FactionDef.categoryTag`; it decides which faction's traders **stock** a techprint. The one real coupling is indirect and binary: `IncidentWorker_NeutralGroup.FactionCanBeGroupSource` rejects a faction hostile to the player, so a faction's techprints stop arriving at goodwill ≤ −75 — **a cliff, invisible in the research tab.** |
| `ThingDef` buildability | `Designator_Build.Visible` gates on god mode, `min/maxTechLevelToBuild` against the player `FactionDef`'s static tech level, research, monolith level, difficulty, `PlaceWorker`, building and discovery prerequisites, and grav-engine inspection. **No relation term**, and `Visible` **filters out** rather than disables — so unbuildable content is invisible *in vanilla*, and the Architect menu shows no carrot. ⚠ **That is a fact about `Visible`, not a structural limit** — see §5a below, which corrects an earlier claim here. |
| Trader stock | `TraderKindDef` has no relation field, `StockGenerator.HandlesThingDef(ThingDef)` takes no faction and is structurally incapable of one, and all 15 subclasses are clean of `goodwill` / `RelationKind` / `HostileTo`. `Settlement_TraderTracker.TraderKind` is a deterministic hash of the settlement. Relation enters trade only as binary `HostileTo`. **But the template we want is here:** `Settlement.GetInspectString` prints `"RequiresTradePermission"` **with the required title named, beside the live relation kind and goodwill number** — vanilla's one pre-announced, pre-reached trade gate, and the shape a standing-gated stock tier should copy. |
| `GoodwillSituationDef` | **Not a gate and not a display.** `FactionUIUtility.GetNaturalGoodwillExplanation` lists only situations whose `naturalGoodwillOffset != 0`, `GetOngoingEvents` only those whose `maxGoodwill < 100` [V, and independently re-confirmed here] — so a situation worker becomes visible **exactly when, and only when, it moves goodwill.** It is a coupling mechanism; whether we want that coupling is [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97)'s. Five vanilla workers, all blanket flags: `AttackingSettlement`, `MemeCompatibility`, `NaturalEnemy`, `PermanentEnemy`, `SameIdeo`. |
| `QuestNode_GetFaction` | Generation-time **selection**, not a gate: `storeAs`, `allowEnemy`/`allowNeutral`/`allowAlly`/`allowAskerFaction`/`allowPermanentEnemy`, `mustBePermanentEnemy`, `mustBeHostileToFactionOf`, `leaderMustBeSafe`, `exclude` and six more — **no goodwill range field**, and every relation flag is an exclusion. The player never sees a quest that was not generated, so it cannot show a carrot. |
| `QuestNode_GetFieldValue` | The one generic reflection reader — `GetField(name, Instance\|Public\|NonPublic)` into the slate — and it **cannot reach goodwill**: `Faction.PlayerGoodwill` is a *property*, and the backing `List<FactionRelation> relations` is private and not a number. Combined with `QuestNode_Greater` / `_Less` / `_Equal` and their `OrFail` variants, this is the closest XML comes to a generic standing predicate, and it stops one step short. |

**So the answer to *"gating surfaces other than quest accept"* is: three that carry a reason string
today, and a fourth that could.** The pending quest offer, the comms-console dialogue and the
ritual gizmo all refuse *with a reason* out of the box. The Architect menu can be made to (§5a) but
vanilla never does. Research and trader stock cannot be reached at all without reimplementing their
locked-reason lists.

**So everything else the campaign wants gated should be *reached through* one of the three** — a
quest that grants the thing, a dialogue option that does, or a rite that does — rather than gated
at its own surface. Not because the other surfaces are incapable, but because those three cost
nothing and the others cost a patch each.

**A cross-checking scan, so the negative is not a sampling** [V]: all 231 non-root `QuestNode_*`
types — 301 `QuestNode_*` types in total, 70 of them `QuestNode_Root_*` — were enumerated and
searched for both `RequirementsToAcceptFactionRelation` and `PlayerGoodwill`. Zero hits for
either. **No quest node anywhere in vanilla reads a goodwill number.**

##### 5a. The Architect menu — an earlier claim here was wrong, and it foreclosed a real option

⚠ **This section previously asserted, marked [V], that `Designator_Build` has "no `Disabled` /
`disabledReason` member at all" and that the Architect menu "cannot show a carrot even in
principle". Both are false, and the second is the damaging one.** The correction [V]:

`Designator_Build : Designator_Place : Designator : Command : Gizmo`, and **`Verse.Gizmo` itself
declares `protected bool disabled`, `public string disabledReason`, `public virtual bool Disabled`
and `public void Disable(string reason = null)`.** `ArchitectCategoryTab.DesignationTabOnGUI`
draws the palette through `GizmoGridDrawer.DrawGizmoGrid`, and `Command.GizmoOnGUI` renders a
disabled gizmo greyed, appends
`"DisabledCommand".Translate() + ": " + disabledReason` to its tooltip colourised
`ColorLibrary.RedReadable`, and on click emits that same string as a `RejectInput` message.

**So a Harmony gate on `Designator_Build` can produce exactly the locked-row-with-its-threshold the
legibility requirement asks for.** The Architect menu is a fourth viable surface, not an impossible
one.

**The routing recommendation above is unchanged**, and now rests on the defensible reason rather
than a false one: vanilla's own buildability gate is `Designator_Build.Visible`, which *filters*
rather than disables, so nothing in vanilla ever greys a building with a reason — and
`Designator_Build` reads no relation term, so the whole gate would be ours. Reaching a building
through a quest or a dialogue option remains cheaper and needs no patch. But if a *building* is
ever the thing that must visibly unlock at a standing threshold, **the surface exists and costs one
`Disable` call inside a postfix**, and this document should not have said otherwise.

#### Cost

| Piece | Cost |
|---|---|
| `StandingAxisDef` — axis label, formatting, `needKey` | **XML** — one new Def type |
| The axis resolver | **New C#**, ~25 lines |
| `QuestPart_RequirementsToAcceptStanding` | **New C#**, ~25 lines, copying `QuestPart_RequirementsToAcceptPlayerWealth` |
| `QuestNode_RequirementsToAcceptStanding` — **the missing XML wrapper** | **New C#**, ~20 lines, copying `QuestNode_RequirementsToAcceptResearch` |
| Gate enforcement at accept | **Free** — `QuestUtility.CanAcceptQuest` |
| The locked row with its threshold, on a pending offer | **Free** — `MainTabWindow_Quests.DoAcceptanceRequirementInfo` |
| `DiaOption` gate helper | **New C#**, ~15 lines |
| The `FactionDialogFor` postfix that hosts it | **Already costed** by [`RELIGION.md`](RELIGION.md) D2 — not double-counted here |
| The ritual gate (§4) | **XML** — a `workerClass` on an existing `RitualBehaviorDef`; the worker is ~10 lines calling the same resolver, plus its `BlockingIssues` twin |
| Multiplayer | **Free** — see below |
| Thresholds | **Requirements / balance**, not here |

**Aggregate: one new Def type, ~95 lines of C# in the existing `ArchinityAltar.dll`, and no new
Harmony patch.** No new assembly. The mechanisms are [V]; **the claim that they compose into the
behaviour the requirement describes is [I]**, as every proposed build is until something is built.

**There is no second plausible build for the quest half** — `QuestUtility.CanAcceptQuest` consults
`QuestPart_RequirementsToAccept` and nothing else, so any accept-time gate is a subclass of it or
it does not exist. **There are two for the dialogue half**, separated in *Available mechanisms*: a
`FactionDialogFor` postfix (selected), or a `RoyalTitlePermitDef` worker, which vanilla already
uses to inject options into that same dialogue but whose gate is welded to holding a title in that
faction.

### Persistence and multiplayer (the gate)

**Nothing new is persisted.** The quest part scribes inside its quest (`QuestPart.ExposeData`) and
a save predating it simply has no such part. The dialogue gate stores nothing at all — it is a
predicate evaluated at draw time. The axes themselves persist wherever their owning system keeps
them.

**The gate is read-only over world state, so it is deterministic by construction.** Goodwill,
Reverence and favour are all world state both clients agree on, evaluated at the same moment on
both. It consumes no `Rand`, reads no `ModSettings` (**T-18**) and holds no cache (**T-20**).

**Quest acceptance is already synced.** `SyncMethod.Register(typeof(Quest), "Accept")` is bare [V]
— either founder can accept any quest, and the gate is re-evaluated inside `AcceptQuestByInterface`
on the accepting client before the command goes out.

**A comms-console `DiaOption` click is already a synced command, and this is stronger than the
"wrap every player write" rule assumed.** Two independent mechanisms in `Multiplayer.dll` [V]:

- `Multiplayer.Client.NodeTreeDialogSync` is a **Harmony prefix on `DiaOption.Activate`**. It
  suppresses the local activation and routes it through
  `[SyncMethod] SyncDialogOptionByIndex(int position)` — which re-activates the option at that
  index on every client — but **only when `Multiplayer.session != null`, `SyncUtil.isDialogNodeTreeOpen`
  is set, and the option's own `dialog` is a `Dialog_NodeTree`** [V]. Outside those three
  conditions the prefix clears the flag and lets the vanilla activation run locally, which is why a
  `DiaOption` reached from anywhere other than an open node-tree dialog is **not** synced by this
  path.
- `Multiplayer.Client.PersistentDialog.Click(int ver, int opt)` is `[SyncMethod]` and runs
  `Dialog.curNode.options[opt].Activate()` behind a `ver` guard that drops a click made against a
  stale node.

So **#73's institution-planting option, and every other gated diplomatic action, need no
`[SyncMethod]` of ours.** [`RELIGION.md`](RELIGION.md) § *Persistence and multiplayer* §
*Reverence* says these "are the ones that need synced commands"; the *rule* is right and this
*instance* is already covered.

⚠ **But the sync is positional, and that is a hazard nothing in the repo records.** Both mechanisms
identify the clicked option by its **index in `curNode.options`** [V]. A postfix that appends
options to the faction dialogue must therefore build **the same list, in the same order, on both
clients** — otherwise index *n* activates one action on one machine and a different action on the
other. A standing gate is safe: it reads world state, so both clients compute the same `disabled`
flag and, critically, `Disable` **keeps the option in the list** rather than removing it.
**Omitting an unavailable option instead of disabling it is what breaks this** — and it breaks
silently, with no error on either client. Disable, never skip. *(Proposed trap; unnumbered, the
orchestrator allocates.)*

**The enabled action's host type is constrained, and the constraint is real.**
`DelegateSerialization.CheckMethodAllowed` walks the delegate method's **outermost** declaring type
and then its base chain, requiring a member of a fixed fifteen-type array — `Ability`,
`AbilityComp`, `Command`, `ThingComp`, `Dialog_BeginRitual`, `LordToil`, `Precept`,
`SocialCardUtility`, `Letter`, `FactionDialogMaker`, `GenGameEnd`, `IncidentWorker`, `QuestPart`,
`ResearchManager`, `ShipUtility` — and throws `"Delegate deserialization: method not allowed"`
otherwise [V]. `FactionDialogMaker` is on the list but is a static class and cannot be derived
from, so **our option actions must be static methods declared on a type deriving from one of the
derivable entries** — `QuestPart`, `Command`, `Letter` and `ThingComp` are the realistic hosts.
Full mechanism: [`docs/engine/determinism.md`](../engine/determinism.md) § *MP serialises the
comms-console dialogue*. **`Disable(reason)` is exempt** — it involves no delegate — so the *gate*
is free and only the *action* pays.

One shared player faction means one standing number per axis per faction, seen by both players and
actionable by either (**T-21**). No per-player gate is possible, and none is wanted.

### Failure and recovery (the gate)

- **A gate whose axis resolver returns a default for an unknown axis fails open.** `Standing.Of`
  must throw or log on an axis it does not handle; returning `0f` silently makes every gate on that
  axis permanent and `float.MaxValue` silently opens every one. Neither says anything. Pick loud.
- **A `StandingGate` whose faction resolves to null.** `QuestPart_RequirementsToAccept` subclasses
  must override `Notify_FactionRemoved` — `QuestPart_RequirementsToAcceptFactionRelation` does,
  nulling its `otherFaction` [V]. A gate on a null faction must refuse loudly, not accept silently;
  vanilla's relation gate returns its reason text when `otherFaction == null`, which is the right
  default.
- **`ShowInRequirementBox: false` makes the gate invisible and still enforcing** — the exact
  failure the legibility requirement exists to prevent (§2).
- **A `TestRunInt` returning `false` on an unmet gate deletes the carrot** rather than locking it
  (§2). The quest is never offered, the player never learns the threshold exists, and nothing is
  logged.
- **Omitting a gated dialogue option rather than disabling it desyncs the option index** under
  Multiplayer, silently (*Persistence and multiplayer*).
- **The threshold in the reason string and the threshold in the predicate are two separate
  literals.** Nothing compares them; a gate that says "need 50" and tests 60 is a lie with no
  error. Build the string from the same field the predicate reads — the `StandingGate` value —
  which is the entire reason §1 puts the formatting on the axis Def rather than in call sites.
- **A ritual gate written only in `CanStartRitualNow` does not block.** The begin-window path
  messages and opens anyway; the reason must also appear in `RitualOutcomeComp.BlockingIssues`
  (§4).
- ⚠ **Two silent defects in `GoodwillSituationDef`, and one loud one, if that route is ever taken
  for the coupling #97 owns** [V]. **Silent:** `baseMaxGoodwill` is **declared and read nowhere in
  the assembly** — the identifier appears exactly once, at its own declaration — so setting it in
  XML does nothing, with no error; and `PreceptComp_GoodwillSituation` is **inert in 1.6**, its
  only reader appending to `Ideo.cachedPossibleGoodwillSituations`, a list that is only `Clear`ed,
  `Contains`-tested and `Add`ed to and never read, with no vanilla XML using the comp. **Both are
  proposed traps** (unnumbered; the orchestrator allocates). **Loud, and therefore an engine note
  rather than a trap:** `workerClass` defaults to the **abstract** `GoodwillSituationWorker`, so an
  omitted `workerClass` throws in `Activator.CreateInstance` rather than producing a config error.

### Status (the gate)

**Verified available mechanism. Not an implementation commitment.**

Established by [Standing as a content gate](https://github.com/cjd721/Rimworld-Archinity/issues/93),
evidence class **READ** — a fresh decompile of `Assembly-CSharp.dll` at the version
`docs/data/MOD-SNAPSHOT.md` pins, plus `Multiplayer.dll`, `VFEEmpire.dll` and `VFED.dll` (the
**1.6** files), `RimPacts.dll`, `FactionTerritories.dll`, shipped DLC XML and keyed language files,
and a wide pass over both corpus roots in ASCII and in a hand-typed null-interleaved UTF-16LE form.

Three findings reframe the capability:

1. **The one gate the ticket names cannot express the question the ticket asks.** It is an enum
   equality with no number and no threshold in its reason text (§0).
2. **Vanilla already ships a numeric goodwill gate with its threshold rendered before it is
   reached**, on the comms console, with a shipped translation key — and three more that spend
   goodwill with the price in the label (§0). What is missing is generality, not the mechanism.
3. **The whole accept-time gating surface is one abstract base with one virtual method**, and both
   the enforcement and the locked-row display are free (§2). The XML wrapper the ticket worried
   might be a rabbit hole is ~20 lines.
4. **There are three free gating surfaces, not one.** Quest accept, the comms dialogue and the
   ritual gizmo all refuse with a reason out of the box; research and trader stock read nothing
   relation-shaped and have no reachable locked-reason seam (§4, §5). That, not the quest gate, is
   what decides where campaign content has to be *reached from*. ⚠ An earlier draft made this
   finding stronger than the evidence by claiming the Architect menu "cannot show a carrot even in
   principle" — **false**, and corrected in §5a: `Designator_Build` inherits `Gizmo.Disable(string)`
   and `Command.GizmoOnGUI` renders the reason. It is a fourth viable surface that costs a patch,
   not an impossible one.

**Verdict for the sourcing ledger ([#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)):**

| Piece | Verdict |
|---|---|
| `QuestPart_RequirementsToAccept` + `QuestUtility.CanAcceptQuest` + the requirement box | **reuse as-is** — carrier is base RimWorld |
| `DiaOption.Disable` + `FactionDialogMaker`'s own gate idiom | **reuse as-is** — base RimWorld |
| RimPacts' `TreatyDef` / `TreatyWorker.CanSign` | **actively blocked** — the shape is right and the mod is not (below) |
| Faction Territories' vassalage gate | **not the donor for the gate**; its *object* half is [`RELIGION.md`](RELIGION.md)'s candidate donor for #73 |
| `RitualBehaviorWorker.CanStartRitualNow` as the rite-side gate | **reuse as-is** — base RimWorld, a `workerClass` |
| The axis resolver and the three adapters | **author from nothing** — ~95 lines |

### Available mechanisms (the gate)

#### Vanilla — the enforcement seam, stated exactly

Twelve `QuestPart_RequirementsToAccept` subclasses ship [V]: `Bedroom`, `ColonistWithTitle`,
`FactionRelation`, `NoDanger`, `NoOngoingBestowingCeremony`, `PawnOnColonyMap`, `PlanetLayer`,
`PlayerWealth`, `Research`, `ThingStudied`, `ThingStudied_ArchotechStructures`, `ThroneRoom`. Four
have `QuestNode_` wrappers. **Two are numeric-threshold gates** — `PlayerWealth` and
`ColonistWithTitle` — and `PlayerWealth` is the donor (§2).

`QuestUtility.CanAcceptQuest` is the sole enforcement point and consults only this base class [V].
`MainTabWindow_Quests.DoAcceptanceRequirementInfo` is the sole locked-row renderer, and it runs
only on an unaccepted, non-historical quest [V].

#### Vanilla — the dialogue gate, and the second route into it

`FactionDialogMaker.FactionDialogFor` builds the comms node and gates four of its own options on
standing (§0) [V]. **It also carries a def-driven injection point that is not a Harmony patch**:
for each `RoyalTitle` the negotiator holds in that faction, it calls
`permit.Worker.GetFactionCommDialogOptions(map, negotiator, faction)` on every
`RoyalTitlePermitDef` on that title, and appends whatever comes back [V]. That is a shipped,
`workerClass`-backed way to put an arbitrary gated option on the faction dialogue with no patch at
all — and **no vanilla `RoyalTitlePermitWorker` overrides it; the base returns `null`.** It is a
pure, unused mod seam.

**It is not selected, for two reasons.** Its gate is *"the negotiator holds a title in this
faction"*, which is the wrong predicate for a Reverence or Goodwill threshold and ties every gated
action to the Exaltation ladder; and `RoyalTitlePermitWorker` is **not** on Multiplayer's
fifteen-type delegate whitelist [V], so an option built there carries an action MP will refuse.
Recorded because it looks like the free answer and is the shape a *title*-gated action would
legitimately use — which is [`RELIGION.md`](RELIGION.md)'s Exaltation business, not this one.

**Permit *acquisition* is not a seam either.** `RoyalTitlePermitDef.AvailableForPawn` — has-permit,
prerequisite, permit points, `currentTitle.seniority >= minTitle.seniority` — is **non-virtual**,
and `PermitsCardUtility` calls it on the static type [V]. Gating permit acquisition on anything of
ours needs Harmony, not a `workerClass`.

#### Vanilla — where a threshold is already drawn before it is reached

Six surfaces, and the two worth copying are not the obvious ones [V]:

| Surface | Method | Shows a number? |
|---|---|---|
| Research tab, per node | `MainTabWindow_Research.DrawBottomRow` → `GetTechprintsInfoCached`, `applied + " / " + total`, red until met, with icon | ✅ **the best numeric template** |
| Ritual dialog | `RitualOutcomeComp.GetQualityFactor` → `have + " / " + need`, drawn by `Dialog_BeginLordJob.DrawQualityFactor` green/red with tick or cross | ✅ **the cleanest have/need widget** |
| Comms console | `DiaOption.OptOnGUI`, via `FactionDialogMaker.RequestAICoreQuest` | ✅ the only goodwill number |
| Permits tab | `PermitsCardUtility.DoLeftRect` → one line per requirement, `.Colorize(met ? Color.white : ColorLibrary.RedReadable)` | ✅ favour and title |
| Quests tab | `MainTabWindow_Quests.DoAcceptanceRequirementInfo` | prose — the wealth variant prints money |
| Factions tab | `FactionUIUtility.DrawFactionRow`, whose tooltip states the literal −75 / +75 thresholds | ✅ but purely **retrospective** — never "at N you unlock X" |
| Architect menu | — | ❌ **no surface at all** |

Two gaps in vanilla's own work, both worth not reproducing:

- **`permitPointCost` gates `AvailableForPawn` and is never printed** [V]. An unaffordable permit
  simply loses its Accept button, with no line saying how many points it wants. Half a gate.
- **`MainTabWindow_Research.DrawStartButton` composes its locked reasons from a hardcoded
  if-chain**, and `Log.ErrorOnce`s if a project is locked with no reason in that list [V]. A
  Harmony-added research gate must add to the chain or it produces a silent lock plus a log error —
  which is another reason §5 routes research gating through a quest instead.

#### Prior art — the right shape in the wrong mod

**RimPacts' `TreatyDef` is the only def-level standing gate in the entire 155-mod corpus** [V].
`RimPacts.TreatyDef : Def` carries `minTrust`, `minGoodwill`, `silverCost`, `durationDays`,
`breakTrustPenalty`, `breakGoodwillPenalty`, `TreatyDef requiresTreaty` and `empireAllowed`; the
enforcement is `RimPacts.TreatyWorker.CanSign(...)`, which returns an **`AcceptanceReport`** —
vanilla's own type — carrying `Rpt_CantSign_Goodwill` with the threshold substituted in, after
softening it by 10 when leader favour is ≥ 60. Its shipped ladder is a genuine standing ladder:
NonAggression −20 / trust 20 / 300 silver → Passage 0/15 → Trade +10/30 → Defense +40/50
(requiring NonAggression) → Alliance +75/60.

**That is this capability, built, by someone else — and the mod stays rejected.** The grounds are
the ripple part's, unchanged: 623 types, a 57-field settings surface gating `Rand` inside a ticking
component (**T-18** at maximum scale), and a second competing authority over the same faction
relations. The value here is the **convergence**: an independent implementation of the same
requirement reached for the same `AcceptanceReport` seam and the same
`Def` + `Worker.CanSign` + threshold-in-the-reason-string shape this build proposes. A design
nobody has tried is a risk; a design shipped independently in the corpus is not.

**Faction Territories' vassalage gate is the second instance** [V]:
`VassaliseUtility.GetSettlementVassaliseGoodwillCost()` clamps a configured cost to 10–100, then
`if (faction.PlayerGoodwill < cost)` produces a *"Requires N goodwill with …"* fail reason, guards
on `Faction.CanChangeGoodwillFor`, and on execution **spends** the standing through
`TryAffectGoodwillWith(Faction.OfPlayer, -cost, …)` with a `+cost` rollback on failure.
⚠ The cost comes from **`ModSettings`** — **T-18** — which is the piece not to copy.

#### Prior art — the display half in the mods, best and worst

Three shipped idioms for *"locked, and here is why"*, of markedly different quality [V]:

- **Best ladder:** VFE Deserters' `DeserterTabWorker_Plots.DoLeftPart` draws **every** future plot,
  wired top to bottom, swapping `RoyalTitleDefExtension.Icon` for its paired `GreyIcon` when
  unreached; the row is inert but fully legible, with its name and target visible. That is
  `requirements/POLITICS.md`'s *"a locked row with its threshold, not an absent one"* in shipped
  form.
- **Best threshold text:** VFE Empire's `RoyaltyTabWorker_Permits.DoLeftRect` colourises each
  requirement line white or `ColorLibrary.RedReadable` by whether it is met, and **omits the action
  button entirely** rather than disabling it.
- **The anti-pattern:** VFE Deserters' `DesertersUIUtility.DoPurchaseButton` greys the button
  **cosmetically** — it still fires, and the refusal arrives afterwards as a red toast — and
  `DeserterTabWorker_Services.DrawService` gives an unaffordable service no visual gate at all. Do
  not copy either.

**Nothing in either mod carries a generic gate primitive.** VFE Empire's closest thing,
`RoyalTitleDefExtension`, is a `DefModExtension` holding three *lists of requirement objects* each
read by a separate hand-compiled worker, and none of them is a threshold on a number. Its three
`QuestPart_RequirementsToAccept` subclasses gate on **rooms and shuttle landing zones**, never on
honour or title level [V]. VFE Deserters' `VisibilityLevelDef` bands **scale prices and flip
incidents and carry no min-band field anywhere** — "locked until band N" is not a shipped pattern
there [V].

#### The wide pass

Both corpus roots plus vanilla and the DLC, `.cs`, `.xml` and every `.dll` with `-a` and
`-g '!**/obj/**'`, each vocabulary swept twice — ASCII, then a **hand-typed null-interleaved
literal** for the `#US` heap (**never** `--encoding utf-16le`,
[#103](https://github.com/cjd721/Rimworld-Archinity/issues/103)). Validated against
`GoodwillSituationWorker` (11 files) and `TryAffectGoodwillWith` before any negative was trusted.

| Vocabulary | Result |
|---|---|
| `MinGoodwill` / `minGoodwill` / `GoodwillThreshold` | RimPacts, Rim War only |
| `RequiredGoodwill`, `goodwillRequired`, `FactionRequirement`, `RelationRequirement`, `requiredRelation`, `minRelation`, `StandingRequirement`, `QuestNode_Requirement` | **zero, in both heaps** |
| XML def fields `minFactionRelation`, `requiredGoodwill`, `factionRelation` | **zero**. `requiresFaction` (56 hits) is vanilla `SitePartDef`'s *does this site need a faction* flag; every `goodwill*` XML field in the corpus is an **effect**, not a gate |
| `RequirementsToAccept` | VEF, VFE Empire, Multiplayer |
| All 113 distinct `QuestNode_*` names in the corpus | none faction-standing-shaped |

**Residual gap, stated:** a mod could express a standing gate as a comparison inside a generically
named worker with no distinctive identifier, and no vocabulary sweep would find it. Bounded by the
two def-level hits above, both of which *do* name their fields; unlikely to hide a better donor
than RimPacts, which is already rejected on other grounds.

### Verification (the gate)

READ-class throughout. Every mechanism claim above was read from a decompiled 1.6 assembly and is
cited by `Type.Method`; the translation keys were read from
`Core/Languages/English/Keyed/Dialog_Trees.xml`.

**What still needs the game: nothing to settle the mechanism.** Two cheap confirmations are owed
before the build is relied on, and neither is a RUN:

- A **STUB**-class check that a `QuestScriptDef` carrying the new node offers the quest with the
  requirement box populated and the Accept button greyed — observable in one single-player session,
  and it also proves the `TestRunInt` choice in §2 is the one that shipped.
- The positional-`DiaOption` hazard belongs to the two-client regime on
  [#16](https://github.com/cjd721/Rimworld-Archinity/issues/16) as one observation: **with a gated
  option present and disabled on both clients, clicking the option below it activates the same
  action on both.** That is the check that would catch an option list built differently per client,
  and it is the only multiplayer claim here that reading cannot close.

Observable checks that the requirement is satisfied: an offered quest the player cannot yet accept
states its threshold and the player's current value, in the requirement box, before accepting; a
comms-console action below its threshold is present, greyed, and names the number it wants.

### Outstanding decisions (the gate)

1. **Every threshold is a balance number and none has an owner.** What "+50 with the Reach"
   actually is, per gate and per era, is `docs/requirements/POLITICS.md`'s and
   `docs/requirements/RELIGION.md`'s. The build does not wait on them — they are Def fields by
   construction — but **the same gap [`RELIGION.md`](RELIGION.md) § *Outstanding decisions* §
   *Reverence* item 4 records applies here**, and it is still a gap rather than a hand-off:
   [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97)'s scope is the coupling, not the
   values.
2. **Whether standing gates are ever *spent* rather than merely read.** Vanilla's own precedent is
   both at once — `RequestTraderOption` gates on ally status **and** charges 15 goodwill [V] — and
   `requirements/RELIGION.md` asks for exactly that split for institutions: *"Reverence unlocks the
   diplomatic option; normal Goodwill remains the spend lever."* The mechanism supports either;
   **which axis is checked and which is charged is authoring, per action.**
   [`RELIGION.md`](RELIGION.md) § *The build — religious institutions* makes the first such call.
3. **Whether a gate should ever hide rather than lock.** The requirement says show the carrot, and
   this build always shows it. A campaign beat that must stay secret until it is reachable needs
   the opposite behaviour, its mechanism is different — `TestRunInt` returning `false`, §2 — and it
   is deliberately not the default. No ticket owns the question of which beats, if any, want it.
