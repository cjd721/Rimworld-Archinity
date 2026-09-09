# Religion

## Purpose and scope

How the religious systems in [`docs/requirements/RELIGION.md`](../requirements/RELIGION.md)
will be built. This document currently owns **Reverence** — where the number lives, how it
persists, how it decays, and how it becomes visible beside Goodwill.

It does not own **propagation**: whether conversion, prisoner release and pilgrim arrival
can be observed at all belongs to
[Reverence propagation events](https://github.com/cjd721/Rimworld-Archinity/issues/74).
It does not own the **Reverence UI**, which is a separate ticket. Exaltation, Influence and
the institution mechanism will land here as their capability tickets resolve.

Goodwill and the political ripple are
[`POLITICS.md`](POLITICS.md)'s; the two systems are separate axes by requirement, and the
seam between them is named in *Outstanding decisions*.

## Status

**Verified available mechanism. Nothing here is an implementation commitment.**

Established by [Reverence — what carries it](https://github.com/cjd721/Rimworld-Archinity/issues/52),
evidence class **READ** — vanilla and mod claims below rest on 1.6 assemblies decompiled
with `ilspycmd`, at the versions pinned in `docs/data/MOD-SNAPSHOT.md`.

The headline is a **confirmed negative**: nothing in the 155-mod corpus carries a
per-faction ideology-penetration measure, and the wide pass ran in both string encodings
to justify it. Reverence is entirely new saved state.

## Available mechanisms

### There is no donor for the measure itself

Vanilla stores faction↔ideo as **set membership, never a weight** [V]:

- `RimWorld.FactionIdeosTracker` holds exactly `Ideo primaryIdeo` and
  `List<Ideo> ideosMinor`, scribed as a reference and a reference-collection. No count,
  weight or percentage attaches to membership.
- `FactionIdeosTracker.RecalculateIdeosBasedOnPlayerPawns` does build a
  `Dictionary<Ideo,int>` of believers, but it is a `private static` scratch field, cleared
  at the end of the method, never scribed, and it runs only for the player faction.
- `Ideo.colonistBelieverCountCached` counts **the player's own colonists only** and is
  absent from `Ideo.ExposeData` — a session cache, not save state.
- `Pawn_IdeoTracker.Certainty` is per-pawn and nothing sums or averages it across a faction.
- `IdeoDevelopmentTracker` persists `points` / `reformCount`, but scoped to the ideoligion
  and measuring reform progress, not penetration.
- `Faction.ExposeData`'s only per-other-faction persisted structure is
  `relations` (`List<FactionRelation>`). **There is no ideo analogue of `relations`.**

Across the corpus, likewise nothing — see the wide pass on the issue.

### The donor that does exist: `GoodwillSituationManager`

`RimWorld.GoodwillSituationManager` is the architecture Reverence wants, minus the
persistence [V]:

- `Dictionary<Faction, List<CachedSituation>>`, recached every 1000 ticks from
  `FactionManager.FactionManagerTick`.
- `GoodwillSituationDef` is a plain Def carrying `workerClass`, `baseMaxGoodwill`,
  `naturalGoodwillOffset` and `versusAll`, with the worker instantiated reflectively.
- **Vanilla already ships an ideology one** — `GoodwillSituationWorker_SameIdeo` returns
  an offset when the player's primary ideo matches the faction's. That is a *binary*
  same-ideo check: the crudest possible version of what Reverence measures, and precisely
  the gap this system fills.
- It is a **pure derived cache** — not `IExposable`, no `ExposeData`.

So vanilla supplies the per-faction *derived modifier* pipeline for free, Def-extensible
via `workerClass`. It does not supply the stored number.

### Vanilla's decay precedent

`Faction.CheckReachNaturalGoodwill` is the shape to copy [V]: a deadband of
`NaturalGoodwill ± 50`, a `naturalGoodwillTimer` that resets inside the band, a threshold
of 3,000,000 ticks, and a step capped at `Mathf.Min(10, …)` attributed to a
`HistoryEventDef`. The timer is scribed in `Faction.ExposeData`.

### Two corrections to the sibling systems

The requirement's framing of Reverence as the odd one out is partly wrong [V]:

- **Empire Honor is not a scalar.** In the 1.6 `VFEEmpire.dll` it is a per-**pawn**
  collection of discrete achievement objects, scribed `LookMode.Deep`, with no running
  total and **no decay at all**. It is a thresholds-and-titles precedent, not a currency
  one.
- **Deserters Visibility is a single global `int`**, clamped 0–100. There is no
  `Dictionary<Faction, …>` anywhere in `VFED.dll`.

**Reverence is not uniquely donorless — it is the only one of the five that needs a
per-faction key, and none of the donors has one.** The meter, its bands and its decay all
have precedent; the per-faction dimension is the new work.

## Technical approach

**State lives in a `WorldComponent`.** The alternatives are ruled out [V]:

- **A per-faction extension does not exist.** `RimWorld.Faction` has **no comps list**;
  there is no vanilla extension point on a faction instance.
- **A `DefModExtension` cannot hold it.** A `FactionDef` is shared across faction
  instances and defs are not scribed. This is **T-11** exactly, and it fails silently.
- **A `GameComponent` would work**, but the state is world-scoped and `GameComponent`s
  scribe by class name, a vendoring hazard not worth taking on.

Mechanics [V]: `WorldComponent` requires a `(World world)` constructor;
`World.FillComponents` instantiates every non-abstract subclass reflectively;
`World.ExposeComponents` scribes `LookMode.Deep` and then calls `FillComponents()` **again
on load**, backfilling component types absent from the save. **Adding the component
mid-campaign is therefore safe — it initialises empty rather than erroring**, which is the
answer to surviving a months-long save.

**Storage shape.** `Faction` is `ILoadReferenceable`, so both shipped idioms are open: a
list of nested `IExposable` records (RimPacts, VEF) or a two-buffer
`Scribe_Collections.Look<Faction, float>` dictionary with `LookMode.Reference` keys (VFED
does this keyed by `Site`). The list-of-records form is the more common in the corpus [V];
whether that reflects a cross-reference-resolution preference or taste is not established [I].

**Bands are XML.** The attention ladder is pure data on the `VisibilityLevelDef` pattern —
an `IntRange` per band plus a polymorphic list of effects. Only the effect workers are C#.

**Visibility beside Goodwill costs a Def and one class, not a Harmony patch.** Reverence
stores its own value and feeds vanilla's existing pipeline by adding a
`GoodwillSituationDef` whose `workerClass` reads it. That expresses "Reverence and Goodwill
are separate axes" inside vanilla's own explanation UI without touching goodwill maths. The
faction row itself is `WorldFactionsUIUtility`, which VEF already demonstrates is
patchable — but the UI is a separate ticket.

**Cost: new C# (small) plus XML.** Not reachable by patch, not reachable by XML alone.

| Piece | Cost |
|---|---|
| Per-faction store, decay, save | **New C#** — one `WorldComponent` |
| Attention bands and their effects | **XML Defs**, `VisibilityLevelDef` pattern |
| Showing it beside Goodwill, gating diplomacy | **New C#, cheap** — a `GoodwillSituationDef` + `workerClass` |
| Storyteller attention weight | **New C# per consumer — the expensive one** |

**The storyteller half does not come cheap.** VFED's five `…_ByVisibility` comps are each a
bespoke `StorytellerComp` subclass reading the raw scalar and applying its own hardcoded
lerp, with every endpoint constant compiled in [V]. **There is no generic "Def field =
weight curve keyed on a custom stat" mechanism to borrow.** A `SimpleCurve` field on our own
`StorytellerCompProperties` subclass would be an improvement on the donor, not a copy of it.
Budget one subclass per storyteller behaviour Reverence is meant to move.

## Persistence and multiplayer

- **`WorldComponentTick` runs inside `DoSingleTick` and is safe to write simulation state
  from** (`docs/engine/determinism.md` § *What is on the synced tick and what is not*).
  `WorldComponentUpdate` is the Unity frame loop and is not.
- A decay tick that draws no RNG is trivially clean. The hazard was never "uses `Rand`" but
  "consumes the shared stream a different number of times per client".
- **Every tunable ships as a Def, never a `ModSettings` field** — **T-18**. The named donor
  is a live worked example of getting this wrong: `WorldComponent_Deserters.WorldComponentTick`
  reads `DesertersSettings.VisibilityChangePerDay`, a client-local setting with an in-game
  slider, **inside its tick** [V]. **Copy the skeleton, reject the knob.**
- Player-initiated writes — establishing an institution, calling a revolt — are UI-originated
  and must be synced commands.
- If Reverence ever hooks faction-ideo recalculation, note that Multiplayer already brackets
  `RecalculateIdeosBasedOnPlayerPawns` with a `FactionContext` push/pop [V].
- **Neither donor ships MP compat** — a full binary search of the 1.6 `VFEEmpire.dll` and
  `VFED.dll` for `Multiplayer`, `SyncMethod`, `SyncWorker` returns zero hits [V]. Nothing to
  inherit, nothing to conflict with.

## Failure and recovery

- **Reverence is keyed by `Faction`, so it inherits T-07** — the faction roster must be final
  before world creation. A faction added later cannot acquire a Reverence history.
- The component **must tolerate a `Faction` key resolving to null on load**, for a faction
  removed via `FactionManager.toRemove`. What *should* happen to that record is a requirements
  question, below.
- A settings-driven decay rate would desync silently and is forbidden by construction (T-18).
- **Name collision, recorded so it is not walked into:** `ReverenceUtility`, `Gene_Reverence`
  and `GeneGizmo_ResourceReverence` exist in the wider ecosystem — Biotech Expansion: Mythic,
  late-bound by string through MP-Compat's `AccessTools.TypeByName`. That mod is **not on
  disk**, and its Reverence is a per-pawn gene resource, not a donor [V]. But the name is
  taken: a `ReverenceUtility` or `Gene_Reverence` of ours would collide if it were ever added.

## Verification

Everything above is READ-class, from decompiled 1.6 assemblies. The wide pass covered all 155
mods, active and inactive, in ASCII and UTF-16LE.

**The residual gap, stated honestly:** a `Dictionary<Faction, float>` inside a generically
named component is invisible to text search, because generic instantiations live in the
`#Blob` heap as signatures rather than readable strings. It was bounded by enumerating every
assembly that references `FactionIdeosTracker` at all and checking each. Closing it fully
needs a Mono.Cecil metadata scan listing fields whose type signature mentions `Faction` —
worth building as a `tools/` mode, since the same question recurs across #53–#56.

## Outstanding decisions

Handed to requirements rather than settled here, per
`docs/agents/capability-research.md` § *Requirements stay where they live*:

1. **Is Reverence per (faction × ideo), or per faction against the player's current primary
   ideo?** `requirements/RELIGION.md` reads as the latter, but it matters concretely: if the
   player reforms a fluid ideo mid-campaign, the stored value either follows or resets. The
   one-key form is much cheaper. Owner: the RELIGION requirements ticket.
2. **What happens to a faction's Reverence when the faction is removed or goes permanently
   hostile** — persist, zero, or drop. T-07 and the `toRemove` path make this a real load-time
   case, not a hypothetical.
3. **Whether Reverence *modulates* the Goodwill ripple.** `requirements/POLITICS.md` says
   Reverence is "an input to this system, not a part of it", which asserts a coupling without
   specifying it. **Unowned by both #52 and #90.** No mechanism blocks either reading — the
   ripple's magnitude is computed in our code, so a Reverence term is a formula change, not a
   capability change [I].
