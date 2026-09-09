# Faction politics

## Purpose and scope

How the political consequences in [`docs/requirements/POLITICS.md`](../requirements/POLITICS.md)
will be built. This document owns the **political ripple**: propagating a single player act
along a faction's alliances and rivalries, and the faction-relation graph it reads.

It does not own Reverence, which is a second per-faction axis and belongs to
[`RELIGION.md`](RELIGION.md). It does not own quest-scoped consequences: "served a faction"
is a quest outcome and belongs to
[the faction demand](https://github.com/cjd721/Rimworld-Archinity/issues/91).

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
authoring. "Served a faction" is a quest outcome and belongs to #91.

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
   **Unowned by both #90 and #98** — a requirements question, handed to POLITICS.md and
   RELIGION.md. The boundary that *is* settled: #90 owns propagation along the relationship
   graph, writing Goodwill; [#98](https://github.com/cjd721/Rimworld-Archinity/issues/98) owns
   Reverence as a quantity, the events that change it and its display, with
   [`RELIGION.md`](RELIGION.md) as its spec. It supersedes #52 and #74.
2. **The seed table's content** — which faction hates or loves which, and by how much. Design
   work, and the real cost of this capability.
3. **The `permanentEnemy` audit**, before world creation. T-07.
