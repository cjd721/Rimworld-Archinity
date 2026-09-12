# Charting

## Purpose and scope

How the discovery system in [`docs/requirements/CHARTING.md`](../requirements/CHARTING.md)
will be built: the apparatus, the two work accumulators, search-band placement, spine
ordering, travel- and tenure-based discovery, and the persistence they need.

This document owns the machinery. What a discovery *is*, when it becomes eligible and what
the player may see or refuse is requirements and stays there.
[Quests](../requirements/QUESTS.md) owns quest presentation and the parent/sub-quest
relationship; [the Chronicle's authoring mechanism](https://github.com/cjd721/Rimworld-Archinity/issues/40)
owns which def carries an individual beat and the parent quest's root node;
[the political and campaign UI surfaces](https://github.com/cjd721/Rimworld-Archinity/issues/61)
owns whether the player sees Charting progress, given that this document establishes they
*can*.

## The build

**Three vanilla classes are subclassed, nothing is Harmony-patched, and the spine's cursor
is not stored at all.** Established on
[the Charting discovery engine](https://github.com/cjd721/Rimworld-Archinity/issues/57),
evidence class READ. Mechanisms are **[V]**; the claim that they compose into Charting is
**[I]** until something compiles.

**Neither of the requirements document's named fallbacks is needed.** Two independent
accumulators are expressible, and a hard min/max search band is expressible. Capability
does not force either degraded alternative; whether they stay on the books as accepted
degradations is the requirements document's call, not this one's.

### 1. The apparatus — `CompChartingApparatus : CompScanner`

**[V]** `RimWorld.CompScanner` is `abstract`, and its only unimplemented member is
`protected abstract void DoFind(Pawn worker)`. **The payload selector is not fused to the
comp; it is an abstract method.** Everything the requirements wanted from the grammar —
operator labor, `ResearchSpeed`-scaled work, MTB probabilistic success, a guaranteed pity
timer, scribed progress, a progress readout — lives in `CompScanner` and
`CompProperties_Scanner`. Everything precious-lump lives one class down in
`CompLongRangeMineralScanner`, which we do not inherit.

| Seam | Base signature | Our use |
|---|---|---|
| `DoFind` | `protected abstract void DoFind(Pawn)` | Dispatch the return-pool find |
| `TickDoesFind` | `protected virtual bool TickDoesFind(float)` | Run both accumulators; dispatch the survey find |
| `CanUseNow` | `public virtual AcceptanceReport` | Lift or keep the roof ban |
| `CompInspectStringExtra` | `ThingComp` virtual | Two bars, no estimate |
| `daysWorkingSinceLastFinding` | `protected float` | The return-pool accumulator |

**[V] The method we override, in full**, because two of its gates are easy to drop from a
paraphrase and the override inherits both:

```csharp
protected virtual bool TickDoesFind(float scanSpeed)
{
    if (parent.IsHashIntervalTick(59)
        && (Rand.MTBEventOccurs(Props.scanFindMtbDays / scanSpeed, 60000f, 59f)
            || (Props.scanFindGuaranteedDays > 0f
                && daysWorkingSinceLastFinding >= Props.scanFindGuaranteedDays)))
    {
        return true;
    }
    return false;
}
```

Two consequences for the override. `parent.IsHashIntervalTick(59)` wraps **both** branches, so
the guaranteed find is not checked every tick either — the pity timer resolves on the next
hash-interval tick after it matures, and an override that hoists the guarantee out of that gate
changes vanilla's pacing. And `Props.scanFindGuaranteedDays > 0f` is the switch that turns the
pity timer off: a pool whose properties leave it at `0` has an MTB and no guarantee, which is
**not** what the requirements want for either pool (*"each pool carries its own guarantee"*), so
both pairs on `CompProperties_ChartingApparatus` must be set.

**Existence proof, shipped and 1.6.** **[V]** `MedievalOverhaul.CompQuestFinder : CompScanner`
emits an arbitrary `QuestScriptDef` drawn from a pool assembled by scanning
`DefDatabase<QuestScriptDef>.AllDefs` for a `DefModExtension`, and MO's own
`1.6/Patches/ToggleOptions/MOSetting_VanillaMineables.xml` joins **vanilla's**
`LongRangeMineralScannerLump` to that pool with a `PatchOperationAdd` and no C#. We write our
own rather than reuse it — MO's comp has one accumulator, no band, and **[V]** no Multiplayer
coverage while its gizmos write scribed state.

**Two accumulators from one comp.** The return pool uses the inherited
`daysWorkingSinceLastFinding`, because `Used`'s unconditional
`daysWorkingSinceLastFinding = 0f` after a successful `DoFind` is exactly *"a find consumes
its pool's accumulator"*. The survey pool uses our own `surveyDaysWorking`, advanced and
reset inside `TickDoesFind`, which returns `true` only for a return-pool find.

**Work does not bank** is one line: `Used` adds `lastUserSpeed / 60000f` to
`daysWorkingSinceLastFinding` *before* calling `TickDoesFind` **[V]**, so `TickDoesFind`
subtracts that increment back off and adds it to `surveyDaysWorking` whenever no return-pool
beat is eligible.

**Eligibility is tested before the accumulator is consumed, never after** — see **T-38** in
*Failure and recovery*.

> **[V] The roof ban is the comp's, not the ThingDef's.** `CompScanner.CanUseNow` returns
> `"CannotUseScannerRoofed"` on `RoofUtility.IsAnyCellUnderRoof(parent)` unconditionally and
> never consults `ThingDef.canBeUsedUnderRoof`. Every `CompScanner` subclass inherits an
> outdoors-only building. For a Star Table that reads the stars this is free flavour;
> `CanUseNow` is `public virtual` if a later tier must be indoors.

### 2. The return pool — `QuestPart_ChartingSpine : QuestPart_SubquestGenerator`

**[V]** `RimWorld.QuestPart_SubquestGenerator` is `abstract : QuestPartActivable` and
supplies five things — **four of them outright, and the fifth only while its tick runs**:

| Requirement | What the base class does | Anchor |
|---|---|---|
| The spine cursor | `protected int SuccessfulSubquestCount => quest.GetSubquests(QuestState.EndedSuccess).Count()` | `QuestPart_SubquestGenerator.SuccessfulSubquestCount` |
| Active-site dedup — **conditionally**; see the `QuestPartTick` override | `PendingSubquestCount` counts `Ongoing` + `NotYetAccepted`; `CanGenerateSubquest` refuses at `maxActiveSubquests`. **[V] But only `QuestPartTick` and the debug window consult it — `TryGenerateSubquest()` never does** | `QuestPart_SubquestGenerator.CanGenerateSubquest` |
| Nesting under a parent | `TryGenerateSubquest` does `GenerateQuestAndMakeAvailable`, then `quest.parent = base.quest` | `QuestPart_SubquestGenerator.TryGenerateSubquest` |
| Chain progress readout | `ExpiryInfoPart => $"{key.Translate()} {SuccessfulSubquestCount} / {maxSuccessfulSubquests}"` | same class |
| The band injection point | `protected abstract Slate InitSlate()` | same class |

**The cursor is derived, not stored.** `QuestUtility.GetSubquests(this Quest, QuestState?)`
filters `Find.QuestManager.questsInDisplayOrder` on `q.parent == quest` **[V]**, and
`Quest.parent` is `Scribe_References.Look(ref parent, "parent")` **[V]**. The spine's
position is recomputed from state the `QuestManager` already persists: nothing to migrate
into an existing save, nothing to keep consistent, nothing to desync.

Two recovery requirements fall out by construction: a beat is consumed by **resolution**
because only `EndedSuccess` counts; a lost site never costs a beat its place because a
non-success end does not advance the count. The third — *an already-active objective is not
re-granted* — is **not** free, because the only code path that reads `PendingSubquestCount` is
the one this build switches off. See the `QuestPartTick` override immediately below.

**Vanilla ships the ordered variant, and it already tests before it consumes.** **[V]**
`QuestPart_SubquestGenerator_ArchonexusVictory.GetNextSubquestDef` in full:

```csharp
protected override QuestScriptDef GetNextSubquestDef()
{
    int index = quest.GetSubquests(QuestState.EndedSuccess).Count() % subquestDefs.Count;
    QuestScriptDef questScriptDef = subquestDefs[index];
    if (!questScriptDef.CanRun(InitSlate(), Find.World))
    {
        return null;
    }
    return questScriptDef;
}
```

Fixed list order, no roll — `_RelicHunt` shuffles and `_Gravcores` weights; Archonexus is the
one we copy. **The `CanRun` guard is load-bearing twice over.** It is vanilla already doing the
*test before consuming* that **T-38** prescribes: a cursor beat that cannot generate returns
`null` rather than being handed to `TryGenerateSubquest` to fail inside. And it is a **second
`CanRun` call site**, so `GetNextSubquestDef` — like anything else that reaches `CanRun` — is
tick-path code and must never be reached from per-client render code (**T-39**).

Four overrides:

- `public override void QuestPartTick() { }` — the base self-fires on an `IntRange interval`
  timer **[V]**. Charting is labor, not a clock; the timer is switched off and a
  `public bool TryFindNow()` wrapper drives the base's `protected virtual TryGenerateSubquest()`.
  **That single override is the whole of "discovery becomes labor" at the mechanism level —
  and it takes three things out with it, none of which `TryGenerateSubquest` replaces.** **[V]**
  `CanGenerateSubquest` gates only the *scheduling* of `currentInterval`;
  `TryGenerateSubquest()` never consults it, and `QuestPartTick` is its only non-debug caller.
  So:
  - **`TryFindNow()` must test `CanGenerateSubquest` itself** before calling
    `TryGenerateSubquest()`. Omit it and the return pool bypasses `maxActiveSubquests` *and*
    `maxSuccessfulSubquests` outright — the dedup billed as free in the table above is gone,
    and the spine can overrun its own length. **[I]**
  - **The override must re-derive the pending count.** **[V]** `PendingSubquestCount` is
    `private`, not `protected`; a subclass cannot reuse it and must recount
    `quest.GetSubquests()` on `Ongoing` / `NotYetAccepted` for itself — which is where the
    per-beat widening below lands anyway. (`SuccessfulSubquestCount` *is* `protected` and is
    reused as-is.)
  - **Chain completion is re-added or deliberately waived.** **[V]** the emptied tick also
    drops `if (maxSuccessfulSubquests > 0 && SuccessfulSubquestCount >= maxSuccessfulSubquests) Complete();`
    — the only place the parent quest ever completes. A spine with an end must call
    `Complete()` from `TryFindNow()` after a successful generation; a spine that runs to the
    end of the campaign waives it on purpose and says so on the `QuestScriptDef`. Silently
    inheriting neither leaves the Chronicle quest open forever.
- `GetNextSubquestDef` — spine beat at the cursor if eligible, else the highest-weight
  eligible significant side discovery, else `null` (and the tick's work routes to the survey
  pool).
- `InitSlate` — sets `points` and `siteDistRange`.
- `CanGenerateSubquest` — widened to count **per beat**. The base's `maxActiveSubquests` is a
  single global count, and leaving it global is a quiet stall; see *Failure and recovery*.

**[#40](https://github.com/cjd721/Rimworld-Archinity/issues/40) owns the parent quest** — a
`QuestScriptDef` with `isRootSpecial`, `autoAccept` and no `expireDaysRange`, plus the
bespoke `QuestNode_Root_*` (~25 lines) that instantiates our part.
`docs/engine/quests.md` establishes that `QuestPart_SubquestGenerator` has no generic
XML-drivable root node; this is confirmed against 1.6.

### 3. The survey pool

`ChartingSurveyExtension : DefModExtension { IntRange band; }` on `QuestScriptDef`, with
membership by `DefDatabase<QuestScriptDef>.AllDefs.Where(d => d.GetModExtension<...>() != null)`.
Any vanilla or mod quest joins from a one-line `PatchOperationAdd`. **T-06 applies:**
`GetModExtension` returns the FIRST match.

**Selection reuses vanilla's own pacing.**
`NaturalRandomQuestChooser.GetNaturalRandomSelectionWeight(quest, points, storyState)` is
**`public static`** **[V]** and already applies `rootSelectionWeight`,
`rootSelectionWeightFactorFromPointsCurve`, `rootMinPoints`, `rootEarliestDay`,
`rootMinProgressScore`, `minRefireDays` and `StoryState.RecentRandomQuests` anti-repetition.
*"Survey finds arrive at roughly the rate vanilla reveals comparable content"* costs one
method call, not a tuning pass.

Odyssey's `CompOrbitalScanner` does the same scan through
`QuestUtility.GetGiverQuests(QuestGiverTag.OrbitalScanner)`, and **we cannot reuse its
marker**: `QuestGiverTag` is a C# `enum` with no XML extension point, and `GetGiverQuests`
short-circuits on `!ModsConfig.OdysseyActive` **[V]**.

### 4. The reach band

**[V] The band is a hard min/max filter and it is expressible today.**
`QuestNode_GetSiteTile.TryFindTile` reads `slate.TryGet<IntRange>("siteDistRange", out var)`
— defaulting to `IntRange(7, 27)` — and passes `var.min`, `var.max` into
`TileFinder.TryFindNewSiteTile`, which enforces both through
`FastTileFinder.TileQueryParams(nearTile, minDist, maxDist, ...)` and again through
`TryFindPassableTileWithTraversalDistance` on the fallback path. Nine vanilla quest scripts
set it with a plain `QuestNode_Set`.

Writing it from `InitSlate()` imposes the band on **every** beat script whether or not that
script knows bands exist. A beat wanting a narrower band declares one on its
`ChartingBeatDef` and we intersect.

Two further facts, one of which was previously stated too strongly:

- **[V] The draw inside the band is uniform on the path our sites actually take, and the
  requirements' weighting wish is therefore UNMET.** An earlier draft claimed
  `TileFinderMode.Near` weights the band by
  `1f - (traversalDistance - minDist) / ((maxDist - minDist) + 0.01f)` and that
  *"weighting the draw within a band is desirable, not required"* was satisfied by a `bool`.
  **That weight exists only in `TileFinder.TryFindPassableTileWithTraversalDistance` and
  `TileFinder.TryFindTileWithDistance`.** `TryFindNewSiteTile`'s **primary** path is
  `layer.FastTileFinder.Query(query, null, allowedLandmarks)`, an optional `validator` sweep,
  then `tile = list.RandomElement()` — **uniform over every tile in the band**. The
  `tileFinderMode` argument reaches the weighted code only through the private
  `TryFillFindTile`, which runs solely on the `list.Empty()` fallback. So a band that has any
  valid tiles at all is drawn from flat, and `tileFinderMode` is dead weight there.
  **Consequence:** the requirements' *"weighting the draw within a band is desirable, not
  required"* stands **re-opened as unmet**, not satisfied. It is still optional by its own
  wording, and buying it costs a `validator` predicate biased by distance or a bespoke draw
  over the returned list — not a `bool`. **[I]** on the cost, **[V]** on the mechanism.
- **[V]** Content can narrow the band itself: `clampRangeBySiteParts` walks `sitePartDefs`
  and `Mathf.Min`s each `conditionCauserDef`'s
  `CompProperties_CausesGameCondition.worldRange` into both ends.

**`siteDistRange` is the only distance lever in the game** — the only distance string in the
assembly, `SitePartDef` exposes no distance field, and a corpus sweep found **zero
assemblies** carrying it in either encoding. Three mods set it statically in XML; nobody
drives it dynamically **[V]** — subject to the sweep caveat in *Available mechanisms*
([#103](https://github.com/cjd721/Rimworld-Archinity/issues/103)).

#### The rung registry

```
Archinity.ReachRungExtension : DefModExtension
    int  minTiles;      // usually 0 or 1
    int  maxTiles;      // what this rung reaches
    Type workerClass;   // optional; the escape hatch
```

Attached by `<modExtensions>` to any def. Satisfaction is read off the def's own type — a
`ResearchProjectDef` rung when `IsFinished`, a `ThingDef` rung when a powered one stands on a
player map — and anything those cannot express ships a `workerClass`. The band is the
element-wise max over satisfied rungs, clamped above by
`CompProperties_ChartingApparatus.maxAcceptedBand`.

**A new mobility rung is one `<modExtensions>` block on a def that already exists. The
band's code does not change.** That is this document's contract with
[roads (#68)](https://github.com/cjd721/Rimworld-Archinity/issues/68) and
[vehicles (#69)](https://github.com/cjd721/Rimworld-Archinity/issues/69): **they report two
integers and a condition**, and neither needs to know the band exists. This contract is the
settled one — `docs/specs/WORLD-INFRASTRUCTURE.md` publishes per-tier `ReachRungExtension`
rows against it rather than a `float` factor of its own.

> **What roads can actually carry today.** Road **presence** is a real signal and worth a
> rung: a road edge costs `0.5` against `1f` off-road, a flat 2× on travel time. Road
> **tier** carries no information at all — **T-42**: all five vanilla `RoadDef`s ship
> `movementCostMultiplier 0.5`, so upgrading a road is a silent no-op and a per-tier rung
> ladder would be describing a difference the engine does not make. #68 supplies the rungs;
> until T-42 is addressed there, expect one presence rung rather than a ladder.

Precedents: **[V]** `RimWorld.SitePartDef.ExtraGenSteps` is vanilla's "scan `DefDatabase<X>`
for the defs pointing at me, cache in `[Unsaved(false)]`" idiom; **[V]** World Tech Level's
`WorldTechLevel.DefTechLevels` is the max-reducing version over
`DefDatabase<TechLevelConfigDef>.AllDefs`; **[V]**
`VanillaGravshipExpanded.LaunchBoonDef.Worker` is the `Def` + `workerClass` + cached-worker
triple if the rung set ever outgrows an extension.

*Two knobs with no interaction term* is a `Mathf.Min`: the era knob is a rung on a
`ResearchProjectDef`, the apparatus knob is `maxAcceptedBand`.

> **[V] The seam that is NOT available.** A colony-scoped `StatDef` is not expressible in
> 1.6: `RimWorld.StatRequest` has six factories and **none takes a `Faction`**. This is why
> Ludeon hung `GravshipRange` on `Building_GravEngine` rather than on the player faction,
> and why the reach band is a def scan rather than a stat.

### 5. Travel and outpost discovery

Absorbed from [#89](https://github.com/cjd721/Rimworld-Archinity/issues/89). **The
load-bearing negative first, because it sets the cost.**

> **[V] No per-tile "the colony has been here" state exists anywhere — not in vanilla, not
> in any DLC, not in any of the 155 mods on disk.** `Tile.ExposeData` scribes `biome`,
> `tile`, `elevation`, `hilliness`, `temperature`, `rainfall`, `swampiness`, `pollution`,
> `feature`, `mutatorDefs` — no visited bit. `World`'s twenty public fields hold no
> exploration tracker. There is no world-map fog of war. `WorldLandmarks` stores
> `{def, name, isComboLandmark}` and every landmark is visible from turn one. The nearest
> miss in the corpus is `Settlement.EverVisited`, which belongs to the trade tracker.

So #39's constraint — that a find must correspond to the colony *having actually been
somewhere* — cannot be met by reading a shipped seen-bit. **Whatever records presence is
ours.**

**The hooks exist, three ways.**

- **[V]** `WorldObject.PositionChanged(PlanetTile previous, PlanetTile current)` —
  `protected virtual`, empty body, called from the `Tile` setter, **not overridden by
  `Caravan`**. One patch covers vehicle caravans and every other mover.
- **[V]** A `WorldObjectComp` ticks on caravans (`WorldObject.TickInterval` loops
  `comps[i].CompTickInterval`; `Caravan.TickInterval` calls `base` first). Core's `Caravan`
  `WorldObjectDef` ships no `<comps>` node, and **Rim War ships the exact XML idiom** for
  creating one (`2222935097/v1.6/Patches/RimWarCompsx.xml`). **Zero Harmony.**
- **[V]** `FactionTerritories.CaravanTerritoryIncidents.Caravan_PathFollower_TryEnterNextPathTile_Postfix`
  is the shipped travel → tile → consequence donor. **Read it for the seam, not the state**:
  its cooldown is an un-scribed `private static Dictionary<int,int>` keyed on
  `WorldObject.ID`, driving a `Rand.Chance` — stale across a reload and per-client under
  Multiplayer.

**Outposts are a separate and better answer.** **[V]** `Outposts.Outpost.TickInterval`
calls `Produce()` when `ticksTillProduction` hits zero; `Produce()` and `ProducedThings()`
are `public virtual`, the cadence is `OutpostExtension.TicksPerProduction` (XML, default
900000 ticks = 15 days), and the extension seam is `WorldObjectDef.worldObjectClass`. The
yield *list* is not extensible — `Outposts.ResultOption` has no `workerClass` and is fused to
`Thing.Make` — but the *class* is, and **`VOE.Outpost_Artillery.Fire` already calls
`WorldObjectMaker.MakeWorldObject`**, which is exactly the shape needed. Tenure needs no new
state: it is the `Produce()` call count. Cost: **VEF becomes a compile-time dependency** for
this half only.

> **[V] The tenure cadence is a mod setting, which puts it in T-18 territory.**
> `Outposts.Outpost` does not use `TicksPerProduction` directly — both the initial value and
> every reset are
> `ticksTillProduction = Mathf.RoundToInt((float)TicksPerProduction * OutpostsMod.Settings.TimeMultiplier)`.
> Mod settings are part of the Multiplayer sync surface (**T-18**), they live per-installation
> rather than per-save, and `ticksTillProduction` is scribed **after** the multiplier has been
> folded in. Two clients whose Outposts `TimeMultiplier` differs schedule tenure finds at
> different intervals, and neither the setting nor the resulting cadence surfaces anywhere the
> player would look. This is the one place the travel/tenure half is not simply *"on the synced
> tick, therefore fine"*, and it is inherited rather than ours: `Outpost_Charting.Produce()`
> cannot fix it, only avoid depending on the interval's exact value.

**It feeds the survey pool, and there is no case for the return pool.** The return pool's
contents are selected against a cursor and a declared band; a caravan has neither. Routing
it there would let a beat fire from a source with no eligibility check, reintroducing the
out-of-order firing the spine exists to prevent.

**The spawn primitive is Odyssey's, and it is XML-driven.** **[V]**
`WorldComponent_LocationGenerator.GenerateLocationForLayer` weight-picks a
`GeneratedLocationDef`, calls `WorldObjectMaker.MakeWorldObject`, names it if
`INameableWorldObject`, sets `PreciousResource` if `IResourceWorldObject`, sets
`ExpireAtTicks` if `IExpirableWorldObject`, then adds it. `GeneratedLocationDef` exposes
`layerDefs`, `layerMaximum`, `worldObjectDef`, `preciousResources`, `TimeoutRangeDays`,
`weight`. **`IExpirableWorldObject` is where the requirements' *"persistence and expiry are
both supported; each beat chooses"* lands for a non-quest find.**

### 6. Where state lives

| State | Lives in | Why |
|---|---|---|
| Survey + return work accumulated | `CompChartingApparatus` | Follows the building; vanilla already scribes one of the two |
| **The spine cursor** | **Nowhere — derived** from `Quest.parent` | `SuccessfulSubquestCount` |
| **Resolved / standing beats** | **Nowhere — derived** | `GetSubquests(EndedSuccess)`, `PendingSubquestCount` |
| Per-tile colony presence | `WorldComponent_Charting`, `Dictionary<PlanetTile,int>` | Nothing shipped carries it |
| Caravan's last tile + cooldown | `Comp_ChartingPresence.PostExposeData` | The one place Faction Territories got wrong |
| Waystone presence | `WorldComponent_Charting`, `bool` | Requirements: colony-level, not a hauled item |
| Current reach | **Nowhere — derived**, cached `[Unsaved]` | A stored band is how a stale band strands a beat |

### 7. What changes it

Every writer runs from a hook that already exists. **Zero Harmony patches on this route.**

| What changes it | From | Evidence |
|---|---|---|
| Both accumulators | `JobDriver_OperateScanner.MakeNewToils`'s `work.tickAction` → `CompScanner.Used(actor)` | **[V]** every tick a pawn is at the interaction cell |
| Which pawn scales it | `worker.GetStatValue(Props.scanSpeedStat)` inside `Used`, into `lastUserSpeed` | **[V]** plain XML `StatDef` field; `ResearchSpeed` is *"better researchers compress the clock"* |
| The return find | our `DoFind` → `QuestPart_ChartingSpine.TryFindNow()` → base `TryGenerateSubquest` | **[V]** does `GenerateQuestAndMakeAvailable`, `quest.parent =`, then `SendLetterQuestAvailable` |
| The survey find | our `TickDoesFind` → `GenerateQuestAndMakeAvailable(chosen, slate)` | **[V]** the vanilla lump path, unchanged |
| The band on either | `slate.Set("siteDistRange", IntRange)` in `InitSlate` | **[V]** `QuestNode_GetSiteTile.TryFindTile` |
| The cursor | **nothing** — it is `GetSubquests(EndedSuccess).Count()` | **[V]** |
| Travel presence | `Comp_ChartingPresence.CompTickInterval` compares `parent.Tile` to `lastTile` | **[V]** `WorldObject.TickInterval` loops `comps[i].CompTickInterval` |
| Outpost tenure | `Outpost_Charting.Produce()` → `base.Produce()`, then offer a find | **[V]** `public virtual`; cadence is XML × a mod setting, see the T-18 note in §5 |
| Recovery | `QuestNode_WorldObjectTimeout` + `QuestNode_NoWorldObject`, both already in the lump script | **[V]** both end the quest non-success, so the cursor does not advance |

**The requirements' *"skill scales find count, never find quality"* needs no code.** **[V]**
`CompProperties_Scanner.scanSpeedStat` is a plain XML `StatDef` field; `CompScanner.Used`
reads it once into `lastUserSpeed`, adds `lastUserSpeed / 60000f` to the accumulator and
passes the same value to `TickDoesFind` as `scanSpeed`, where it divides `scanFindMtbDays`.
It therefore moves **only the rate**. Nothing downstream of the rate — `GetNextSubquestDef`,
the survey weight from `GetNaturalRandomSelectionWeight`, `InitSlate`'s band, the tile draw —
ever sees `scanSpeed` or the worker. A better researcher gets more finds and the same finds.
**Preserving that is a constraint on the override**, and the one way to break it is to let the
payload selector read `lastUserSpeed`.

### 8. Where the player sees it

**[V]** `CompScanner.CompInspectStringExtra` already renders
`"ScanningProgressToGuaranteedFind" : (daysWorkingSinceLastFinding /
Props.scanFindGuaranteedDays).ToStringPercent()`. Our override emits it twice, once per pool,
and **drops vanilla's `ScanAverageInterval` line** — an explicit days-to-next-find estimate,
which the requirements forbid. ~12 lines; no window, no `ITab`, no Harmony.

**[V]** The quest tab gives the chain readout free: `ExpiryInfoPart` renders `3 / 9` on the
parent quest and children indent 10px beneath it.

Three further surfaces, all required and all cheap:

- **The Waystone's out-of-reach signal** — a `CompInspectStringExtra` reporting that returns
  exist the current instrument cannot resolve, computed as "some `ChartingBeatDef` is
  eligible but its band exceeds `maxAcceptedBand`". ~10 lines, and it is the only thing
  separating *the apparatus is insufficient* from *you have done every eligible beat*.

  > **Constraint, on this readout specifically: "eligible" here means the beat's declared
  > band and its own condition workers, and nothing else. This code path must never call
  > `QuestScriptDef.CanRun`.** An inspect string is per-client render code — it runs on
  > selection, on one machine, at a tick the other machine is not rendering — and `CanRun`
  > is not the pure predicate its name suggests: it reaches `Rand` through
  > `root.TestRun(...)` → `TileFinder` → `list.RandomElement()` and memoises the answer in
  > `[Unsaved]` tick/points fields, so the two clients draw a different number of values in
  > the same tick. **T-39.** Everywhere else in this build `CanRun` is correct and required —
  > inside `TickDoesFind` (**T-38**) and inside `GetNextSubquestDef`, both on the synced tick.
  > This readout is the one place the same call is a desync, which is exactly why it is
  > written down at the readout and not only in the register.
  >
  > The cheap consequence: a beat whose band the apparatus *can* accept but whose site cannot
  > be placed is invisible to this signal, because only the tick path knows that. That is the
  > right trade — the signal answers *"is the instrument the problem"*, and the instrument is
  > the only thing it is allowed to read.
- **The arrival letter's reason** — **[V]**
  `QuestUtility.SendLetterQuestAvailable(quest, discoveryMethod)` takes free text landing in
  the letter body; Odyssey passes `"QuestDiscoveredFromOrbitalScanner"`. One translation key
  satisfies QUESTS.md's *"a quest states plainly why it is happening"*.
- **The band itself, if wanted** — **[V]**
  `CompPilotConsole.StartChoosingDestination_NewTemp` draws
  `GenDraw.DrawWorldRadiusRing(tile, radius, mat)` twice with different materials. A min/max
  band is the same call twice, ~25 lines.

**Whether the player should see any of it is
[#61](https://github.com/cjd721/Rimworld-Archinity/issues/61)'s call.** This document
establishes only that all of it is expressible, cheaply, at the fidelity the requirements
want.

### 9. Cost

| Piece | Kind | Lines | Lands in |
|---|---|---|---|
| `CompChartingApparatus` + `CompProperties_ChartingApparatus` | new C# | ~150 | `ArchinityAltar.dll` |
| `QuestPart_ChartingSpine` (4 overrides + `TryFindNow`) | new C# | ~60 | same |
| `ChartingBeatDef` + condition workers | new C# | ~70 | same |
| `ReachRungExtension` + the max reducer | new C# | ~60 | same |
| `ChartingSurveyExtension` + survey selector | new C# | ~30 | same |
| Waystone inspect comp | new C# | ~15 | same |
| `WorldComponent_Charting` | new C# | ~60 | same |
| `Comp_ChartingPresence` + properties (travel) | new C# | ~35 | same |
| `Outpost_Charting` (tenure) | new C# | ~25 | same |
| Two-ring band display | new C# | ~25 | optional, #61's call |
| `QuestNode_Root_Chronicle` (the parent quest) | new C# | ~25 | **#40** |
| 3 apparatus `ThingDef`s + 3 `WorkGiverDef`s + 3 `ResearchProjectDef`s | XML | ~180 | new def files |
| `ReachRungExtension` per mobility rung | XML | ~6 each | defs that already exist |
| Caravan `<comps>` patch (Rim War's idiom) | XML patch | ~15 | new patch file |
| Survey-pool opt-in per existing quest | XML patch | 1 op each | new patch file |
| `ChartingBeatDef`s + beat `QuestScriptDef`s | XML | per beat | authoring, #40 |

**[I] ~505 lines of C# in the one assembly we already ship, and zero Harmony patches.** The
table sums to that, and the arithmetic is worth stating because the previous headline of
~485 did not match it:

| Slice | Lines | Rows |
|---|---|---|
| Core mechanism — apparatus, spine, beats, reach, survey, Waystone readout | **385** | the first six new-C# rows |
| Travel and tenure — `WorldComponent_Charting` + presence comp + outpost | **120** | the deferrable half |
| **Subtotal, this build** | **505** | |
| Two-ring band display | +25 | optional, #61's call |
| `QuestNode_Root_Chronicle` | +25 | **not ours** — #40 |

So: **~505 committed, ~530 with the ring, ~555 counting #40's root node**, of which ~120 is
the travel/outpost half that could be deferred. Every figure is an estimate **[I]**; the
mechanisms they price are **[V]**.

**The three apparatus tiers cost no C# at all.** **[V]** `WorkGiverDef.scannerDef` is a plain
XML field — `LongRangeScan` and `GroundPenetratingScan` differ in exactly that field — so a
tier is one `ThingDef` + one `WorkGiverDef` + one `ResearchProjectDef`, with
`scanFindMtbDays`, `scanFindGuaranteedDays` and `maxAcceptedBand` carrying everything that
changes. **One building line, three defs, one comp class.**

### Alternatives, and what separates them

1. **Copy `CompScanner`'s ~90 lines into a standalone `ThingComp`** and hold the two
   accumulators symmetrically. Cleaner to read; costs the `JobDriver_OperateScanner` /
   `WorkGiver_OperateScanner` / `JobDefOf.OperateScanner` / `WorkGiverDef.scannerDef` stack,
   because **[V]** both the driver and the giver resolve through `TryGetComp<CompScanner>()`.
   Rejected — reimplementing a work giver and a job driver to avoid one asymmetric field is
   the wrong trade.
2. **Redirect Medieval Overhaul's `CompProperties_QuestFinder` with `<compClass>`.** No
   Harmony, but it makes MO a hard dependency for a comp with one accumulator, no band and no
   MP coverage. Rejected — MO stays the existence proof.
3. **Use VEF's `GameComponent_QuestChains` / `QuestChainExtension` for eligibility.** A full
   XML-driven gate engine already in the load order, whose `conditionSucceedQuestsCount` is a
   literal *"requires progress >= N"*. **Free, and it should be used for gated optional
   content.** Wrong for the spine: it schedules and fires on its own MTB, so discovery would
   not be labor, and it has no player-facing UI — `QuestChainsDevWindow` is dev-mode only.
   **Recommended split: VEF's extension for gated side content, `QuestPart_SubquestGenerator`
   for the spine.** A recommendation, not a selection — nothing in this document is an
   implementation commitment, per *Status*.
4. **Postfix `WorldObject.PositionChanged` instead of a caravan comp.** Exact arrival rather
   than polling, covers every mover; costs one Harmony patch and still needs its state parked
   in a comp. Rejected — polling imprecision is invisible at world-map timescales, and the
   comp deletes the un-scribed-static failure class Faction Territories demonstrates.

## Persistence and multiplayer

**The return pool's entire state is derived**, which is the single biggest difference between
this build and the one this document previously anticipated. There is no cursor to scribe, no
resolved-beat set to migrate, and no version skew to handle.

What is scribed: the comp's accumulators (`CompScanner.PostExposeData`'s three
`Scribe_Values` plus ours), the Waystone `bool`, the per-tile presence dictionary
(`Scribe_Collections.Look(..., LookMode.Value, LookMode.Value)`; `WorldLandmarks.ExposeData`
is the shipped `Dictionary<PlanetTile, T>` precedent **[V]**), and the caravan comp's last
tile.

**Added to a save that predates it: safe, by vanilla's own mechanism.** **[V]**
`World.ExposeComponents` calls `FillComponents()` *after*
`Scribe_Collections.Look(ref components, "components", LookMode.Deep, this)`, so a
`WorldComponent` absent from the save is constructed with default fields. The presence
dictionary loads empty — every tile reads unvisited, wrong but harmless; `FinalizeInit(fromLoad: true)`
can seed it from player settlement tiles, as `WorldComponent_LocationGenerator.FinalizeInit`
does for its own bootstrap.

> Where a set of defNames *is* needed, scribe **strings, not `LookMode.Def`**: **T-04** means
> an unresolvable def reference is omitted rather than nulled, which would silently shrink
> the set.

### Multiplayer

**The whole find path is on the synced tick, and needs no `[SyncMethod]`.** **[V]**
`CompScanner.Used` is called only from `JobDriver_OperateScanner`'s `work.tickAction`, inside
`DoSingleTick`. Per `docs/engine/determinism.md`, `Rand` reached from an already-synced tick
is deterministic by construction; every draw on this path — `Rand.MTBEventOccurs`, everything
`QuestGen.Generate` consumes, `list.RandomElement()` inside `TileFinder` — sits at the same
stream position on both machines. Both writers in the travel/tenure half
(`WorldObject.TickInterval`, `Outpost.TickInterval`) are likewise on the synced tick.

- **[V] MP already hardens the tile finder.**
  `Multiplayer.Client.Patches.FastTileFinderQueryDeterminismPatch` transpiles
  `FastTileFinder.Query`, replacing `UnityData.GetIdealBatchCount` with a version that
  returns the full `length` whenever `Multiplayer.Client != null` — forcing the parallel
  query into one deterministic batch. Site placement is specifically covered.
- **[V]** `TileFinder.TryFindNewSiteTile`'s landmark roll is `Rand.ChanceSeeded(...,
  Gen.HashCombineInt(Find.TickManager.TicksGame, 18271))`, which push/pops its own state and
  cannot perturb the shared stream.
- **[V]** Vanilla seeds map generation and MP inherits it; **T-33** is the one escape, carried
  by `rwmt.multiplayercompatibility`'s `VanillaExpandedFramework.PatchKCSG`. **Design lever
  from [#88](https://github.com/cjd721/Rimworld-Archinity/issues/88), and it should be
  taken:** authoring Charting sites with `structureLayoutDefs` / `tiledStructures` rather
  than `settlementLayoutDefs` makes them immune to T-33 by construction, since neither branch
  of `GenStep_CustomStructureGen.Generate` reaches `KCSG.SettlementGenUtils.Sampling.Sample`.
  Belt-and-braces on top of the compat layer, not instead of it.

**The one real sync surface, and it is easy to miss.** **[V]** MP registers
`SyncDelegate.Lambda(typeof(CompLongRangeMineralScanner), "CompGetGizmosExtra", 1, ...)` **by
lambda ordinal on that concrete type**, and `SyncMethod.Lambda(typeof(CompScanner),
"CompGetGizmosExtra", 0, ...)` is `.SetDebugOnly()`. Registration is per-type, so **a
subclass's gizmos inherit nothing.** Any gizmo, float menu or tab control on the apparatus
that writes state must be registered through the Multiplayer API, and a miss is silent and
persistent because it writes scribed state.

> **The build has no state-writing gizmo, deliberately.** There is no target to select,
> because the pool is chosen by eligibility rather than by the player. **Keeping it that way
> is a design constraint, not an accident** — it is the difference between zero MP work and a
> sync surface. Medieval Overhaul is the cautionary case: its quest-select and mineral-select
> gizmos both write scribed fields and **[V]** it is covered by neither
> `Multiplayer_Compat.dll` nor `Multiplayer_Compat_Referenced.dll`.

## Failure and recovery

| Failure | Detection | Recovery |
|---|---|---|
| A beat's site expires unresolved | `QuestNode_WorldObjectTimeout` ends the quest `Fail` | Free — the count does not advance, the same beat is next |
| A beat's site is destroyed | `QuestNode_NoWorldObject` → `QuestNode_End` | Free — as above |
| Player techs past an undone near beat | — | The band's **min** never rises at runtime; each beat declares its own band on its `ChartingBeatDef`, never derived from the cursor |
| No valid tile in a beat's band | `CanRun` returns false | `TickDoesFind` never returns true; the accumulator is untouched and the tick's work routes to the survey pool |
| The apparatus is destroyed | — | Nothing is lost — the cursor is derived from quest state. Only the two accumulators reset |
| The Waystone is lost | — | A `bool` in the `WorldComponent`; no raid, fire or caravan wipe touches it |
| A `ChartingBeatDef` is removed between saves | — | The cursor counts successes, not def identities, so the index still resolves — but **every later beat silently renumbers.** Author-time hazard, flagged not solved |

**Two silent failures this build must not inherit**, both found on #57 and both now in the
register:

- **T-38 — a `CompScanner` find that generates no quest still zeroes the guaranteed-find
  timer.** `CompScanner.Used` runs `if (TickDoesFind(...)) { DoFind(worker);
  daysWorkingSinceLastFinding = 0f; }` — the reset is unconditional and outside `DoFind`,
  while `CompLongRangeMineralScanner.DoFind` only generates when `CanRun` passes. The player
  loses a full pity cycle with no message and no log line. **Fix: test `CanRun` inside
  `TickDoesFind`, before returning true.** Vanilla's own ordered generator already works this
  way — see `QuestPart_SubquestGenerator_ArchonexusVictory.GetNextSubquestDef` in §2.
- **T-39 — `QuestScriptDef.CanRun` consumes the shared `Rand` stream and memoises per
  tick.** `CanRun` → `root.TestRun(...)` → `TileFinder.TryFindNewSiteTile` →
  `list.RandomElement()`, with the result cached in `[Unsaved]` tick/points fields. Calling
  it from any client-local path makes two clients draw a different number of values in the
  same tick. The name reads as a pure predicate and is not one. This build has three `CanRun`
  call sites — `TickDoesFind`, `GetNextSubquestDef` and, forbidden, the Waystone inspect
  string. The first two are on the synced tick and are fine; the constraint on the third is
  stated at the readout in §8.

**One softlock this build could reintroduce.** `QuestPart_SubquestGenerator.CanGenerateSubquest`
gates on a single **global** `maxActiveSubquests` **[V]**. Left at the default of 2, a
standing spine site plus a standing significant side discovery jam the whole return pool. The
override to per-beat counting is the requirement *"deduplication is by beat, not by site"*;
omitting it is a quiet stall, not a cosmetic flaw.

## Status

**Verified available mechanism. Nothing here is an implementation commitment.**

Evidence class **READ**, established on
[the Charting discovery engine](https://github.com/cjd721/Rimworld-Archinity/issues/57)
against `Assembly-CSharp.dll` (1.6.4871), `Multiplayer.dll`, `VanillaGravshipExpanded.dll`,
`MedievalOverhaul.dll`, `VFED.dll`, `VEF.dll`, `Outposts.dll`, `Vehicles.dll`,
`WorldTechLevel.dll`, `FactionTerritories.dll` and
`Multiplayer_Compat{,_Referenced}.dll`, decompiled with `ilspycmd` 8.2.0 at the versions
pinned in `docs/data/MOD-SNAPSHOT.md`, plus the shipped XML under `common/RimWorld/Data/`.

What changed relative to this document's previous draft:

- The scanner grammar is **confirmed in all six links** and should not be re-checked.
- The payload selector is **an abstract method**, not something to be worked around.
- The spine cursor is **derived, not stored** — the `WorldComponent` that was going to hold
  it is not needed for that purpose.
- **Neither named fallback is needed.** Two accumulators and a hard band filter are both
  expressible. Whether the requirements document retires the fallbacks is its call, not
  this document's.
- Vanilla's inspect string **shows an estimate the requirements forbid** and must be
  overridden rather than adopted.
- **The band is filtered but not weighted** on the path our sites take. Corrected in §4
  against an earlier draft that claimed otherwise; the requirements' optional weighting wish
  is unmet, not satisfied.

## Available mechanisms

Everything above cites its carrier inline. The survey behind the build, condensed to what
shaped it:

**Positives.** `CompScanner` (abstract payload selector, pity timer, scribed progress,
inspect readout); `QuestPart_SubquestGenerator` (ordered cursor, dedup, nesting, `N / M`);
`QuestNode_GetSiteTile` + `TileFinder` (`siteDistRange`, hard min/max, **uniform** within the
band on the primary path — see §4);
`NaturalRandomQuestChooser.GetNaturalRandomSelectionWeight` (vanilla pacing, `public
static`); `WorldComponent_LocationGenerator` + `GeneratedLocationDef` (XML-driven periodic
world-object spawn with expiry); `Outposts.Outpost.Produce()` (tenure); `WorldObjectComp` on
`Caravan` (travel); `GenDraw.DrawWorldRadiusRing` (band display);
`GravshipUtility.MaxDistForFuel` (the one vanilla "how far can we travel").

**Existence proofs.** `MedievalOverhaul.CompQuestFinder : CompScanner`;
`VanillaGravshipExpanded.CompScannerCluster` with research-gated pluggable modules declaring
`scanFindMtbDaysOverride` / `scanFindGuaranteedDaysOverride` — **question 6's apparatus
ladder, already built by somebody else**; `VOE.Outpost_Artillery.Fire`;
`FactionTerritories.CaravanTerritoryIncidents`.

**Three clean negatives, each of which shaped the build.** All swept over both corpus roots
with `-a -g '*.dll' -g '!**/obj/**'`, repeated under `--encoding utf-16le`, attributed with
`corpus.py --which`, and validated against known hits:

1. **No per-tile colony-presence state exists anywhere** — the travel half's whole cost.
2. **No tech-level → world-distance coupling exists anywhere** — the reach band's whole cost.
3. **Nobody drives `siteDistRange` from code** — zero assemblies, either encoding.

> **Caveat on the sweep, not on the conclusions.** The wide pass above used
> `rg -a --encoding utf-16le`, and that form is now known to miss strings provably present in
> the `#US` heap, non-uniformly —
> [#103](https://github.com/cjd721/Rimworld-Archinity/issues/103). All three negatives were
> also validated against known hits and negative 1 rests additionally on reading
> `Tile.ExposeData` and `World`'s fields firsthand, so none of them is thought to be wrong.
> They are, however, **swept negatives taken with a tool that under-reports**, and a
> re-sweep with a null-interleaved pattern is the cheap way to make them safe to lean on.

**Ruled out.** `QuestGiverTag` (a C# enum, Odyssey-gated, not XML-extensible);
`VFED.WorldComponent_Deserters.PlotMissions` (a real ordered chain, but hardcoded to the
Empire title ladder and not XML-drivable); a colony-scoped `StatDef` (no
`StatRequest.For(Faction)`); Vehicle Framework's `VehicleStatDef` set (no range stat);
*Vanilla Exploration Expanded*, which despite the name is a tile-mutator pack carrying
nothing for discovery.

## Verification

**One narrow RUN item remains**, and it is a confirmation rather than an open question:

1. **That the two-accumulator override behaves.** With no eligible return-pool beat,
   `daysWorkingSinceLastFinding` must stay at zero while `surveyDaysWorking` climbs at the
   full rate; a return find must zero only the return accumulator. This is the one place the
   design leans on `Used`'s internal ordering rather than on a documented contract.

It is a one-client check. The two-client Multiplayer test belongs to
[#16](https://github.com/cjd721/Rimworld-Archinity/issues/16), the standing regime.

**Settled by reading, no longer a RUN: that a `CompScanner` subclass binds its
`WorkGiverDef`.** An earlier draft carried this as a second RUN because the failure mode
(*"the pawn never comes"*) is silent. It is not a risk, on three counts, all **[V]**:

- `Verse.ThingWithComps.GetComp<T>()` misses in `compsByType.TryGetValue(typeof(T))` for a
  subclass, but only *returns* on that miss when `typeof(T).IsSealedWithCache()`; otherwise it
  falls through to a linear `comps[i] is T` scan. `CompScanner` is `abstract`, so a subclass
  instance is found by `GetComp<CompScanner>()`.
- `WorkGiver_OperateScanner.HasJobOnThing` calls exactly
  `building.TryGetComp<CompScanner>().CanUseNow`, which is the same resolution.
- `WorkGiver_OperateScanner.PotentialWorkThingRequest => ThingRequest.ForDef(def.scannerDef)`
  binds by `ThingDef`, not by comp class, and this build already gives each apparatus tier its
  own `WorkGiverDef` pointing at its own `ThingDef` (§9).

## Outstanding decisions

- **Whether the player sees Charting progress, and on which surfaces** —
  [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61). This document establishes
  that all of it is expressible cheaply; the choice is not ours.
- **Which def carries a beat, and the parent quest's root node** —
  [#40](https://github.com/cjd721/Rimworld-Archinity/issues/40).
- **The reach-rung table's numbers** — which minTiles/maxTiles each rung reaches, and where
  the rungs sit relative to travel time. Parameters, not mechanism, and they sit in the
  **balance deferral** on [map #2](https://github.com/cjd721/Rimworld-Archinity/issues/2)
  — *"costs, durations, threat magnitudes and progression rates. Last, after the structure is
  concrete."* Shared with `docs/specs/WORLD-INFRASTRUCTURE.md` and with roads (#68); the
  mechanism does not wait on them.
- **The apparatus ladder's numbers** — `scanFindMtbDays`, `scanFindGuaranteedDays` and
  `maxAcceptedBand` per tier. `docs/progression/` is where they belong and is currently empty
  — the same gap [#87](https://github.com/cjd721/Rimworld-Archinity/issues/87) found.
- **Whether the draw inside a band should be distance-weighted at all.** Re-opened by §4's
  correction: the requirements call it *desirable, not required*, and the engine does not
  supply it on our path. Nobody owns the answer; it is a gap, and a small one.
- **The rules for travel and tenure discovery** — probability per tile entered, per tenure
  cycle, whether re-entering a known tile re-rolls, whether travel discovery is band-limited
  at all. **These are requirements, and this is a gap with no owner.**
  [#39](https://github.com/cjd721/Rimworld-Archinity/issues/39) is closed and **its successor
  does not exist** — no ticket has been opened for these rules. Saying "a successor ticket
  owns it" would be a hand-off to nothing; it is flagged here rather than invented, and the
  mechanism half is built and waiting for numbers.
- **Whether map generation must be cross-client identical.** Nothing in `docs/requirements/`
  states it, [#88](https://github.com/cjd721/Rimworld-Archinity/issues/88) named the hole, and
  it is now owned by
  [#104 — must both clients generate the same map](https://github.com/cjd721/Rimworld-Archinity/issues/104).
  Load-bearing for every Charting site, and the reason the T-33 authoring lever in
  *Persistence and multiplayer* is worth taking regardless of how #104 lands.
- **The mundane table** — a Waystone-less apparatus feeding only the survey pool. Open in the
  requirements document; mechanically it is one more `ThingDef` + `WorkGiverDef` with
  `maxAcceptedBand` set and the return pool disabled, so capability does not constrain the
  narrative choice.
