# Faction politics

## Purpose and scope

How the political consequences in [`docs/requirements/POLITICS.md`](../requirements/POLITICS.md)
will be built. This document owns two capabilities, kept in separate parts below:

- **The political ripple** — propagating a single player act along a faction's alliances and
  rivalries, and the faction-relation graph it reads. Everything up to *Outstanding decisions*.
- **[The faction demand](#the-faction-demand)** — the ask, the deadline, the consequence, and
  moving a second faction on resolution. The final part of this document.

It does not own Reverence, which is a second per-faction axis and belongs to
[`RELIGION.md`](RELIGION.md).

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
not own **standing as a gate** ([#93](https://github.com/cjd721/Rimworld-Archinity/issues/93)),
though `QuestPart_RequirementsToAccept` is the surface such a gate would use.

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
| **A pawn skill threshold** | New. No `QuestPart_RequirementsToAcceptSkill` exists [V]. ~35 lines copying `QuestPart_RequirementsToAcceptColonistWithTitle` exactly: `CanAccept()` sweeps `PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive_Colonists`, `CanPawnAccept(p)` tests the skill, `RequiresAccepter => true` makes the accepter pawn the specialist [V on the donor, I on the composition]. Display is free — `MainTabWindow_Quests.DoAcceptanceRequirementInfo` draws the red box and disables Accept [V]. |
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
