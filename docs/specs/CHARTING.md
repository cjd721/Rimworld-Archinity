# Charting

## Purpose and scope

> **Boundary correction — 2026-09-13.** Charting never builds, upgrades, finances or
> times roads. Those behaviors belong to world infrastructure. The reach-rung registry
> may consume completed mobility state if cross-spec integration later selects that
> relationship, but it is not a road-system contract and does not determine road tiers.

How the discovery system in [`docs/requirements/CHARTING.md`](../requirements/CHARTING.md)
will be built: the apparatus, the two work accumulators, search-band placement, spine
ordering, travel- and tenure-based discovery, the inspectable lore inside the sites it places,
and the persistence they need.

This document owns the machinery. What a discovery *is*, when it becomes eligible and what
the player may see or refuse is requirements and stays there.
[Currencies](CURRENCIES.md) owns the Intel that reading site lore pays out; §10 supplies the
object that calls `Credit` and does not duplicate the store.
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

**§10 adds one more subclass and it is VEF's, not vanilla's** — `StudiableBuilding`, for the
lore a site contains once the player is standing in it. Still no Harmony.

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
integers and a condition**, and neither needs to know the band exists.
`docs/specs/WORLD-INFRASTRUCTURE.md` § *Charting reach rungs — offered, not selected* offers
per-tier `ReachRungExtension` rung shapes against it rather than a `float` factor of its own;
whether any of them ships is [#118](https://github.com/cjd721/Rimworld-Archinity/issues/118)'s.

> **What roads can actually carry today.** Road **presence** is a real signal and worth a
> rung: a road edge costs `0.5` against `1f` off-road, a flat 2× on travel time. Road
> **tier** carries no information at all — **T-42**: all five vanilla `RoadDef`s ship
> `movementCostMultiplier 0.5`, so upgrading a road is a silent no-op and a per-tier rung
> ladder would be describing a difference the engine does not make. WORLD-INFRASTRUCTURE offers
> the rung shapes and #118 decides whether any ships; until T-42 is addressed, expect one
> presence rung rather than a ladder.

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
| **Lore records already read** | `WorldComponent_Charting`, `HashSet<string>` of `loreKey` | **World-scoped, not per-`Thing`** — a re-entered site regenerates its map and its murals; see §10 |
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
| Site lore read | `JobDriver_StudyBuilding.MakeNewToils`'s `tickIntervalAction` → `StudiableBuilding.Study(Pawn)` | **[V]** VEF's shipped job driver; the override is ours. See §10 |
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
- **Site lore, once the player goes and reads it** — an archived letter and a read-variant
  `<description>`, plus VEF's pulsing overlay, which marks *designated*, not *unread*. That
  is §10's business and is priced there.
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

**§10 adds ~50 to the committed figure, taking it to ~555.** Its rows are tabled in that
section rather than folded in here, because the lore verb is separable from the discovery
engine — it is what a site *contains*, not how a site is *found* — and a reader pricing the
engine alone should be able to stop at this table.

So: **~505 committed, ~530 with the ring, ~555 counting #40's root node**, of which ~120 is
the travel/outpost half that could be deferred. Every figure is an estimate **[I]**; the
mechanisms they price are **[V]**.

**The three apparatus tiers cost no C# at all.** **[V]** `WorkGiverDef.scannerDef` is a plain
XML field — `LongRangeScan` and `GroundPenetratingScan` differ in exactly that field — so a
tier is one `ThingDef` + one `WorkGiverDef` + one `ResearchProjectDef`, with
`scanFindMtbDays`, `scanFindGuaranteedDays` and `maxAcceptedBand` carrying everything that
changes. **One building line, three defs, one comp class.**

### 10. Inspectable site lore

Absorbed from [#80](https://github.com/cjd721/Rimworld-Archinity/issues/80). Its cost rows
are additive to §9's table and are stated at the end of this section.

**The verb has a carrier we already depend on. The readout has none, and the readout is the
feature** — so this is a build, and it is one override. `docs/requirements/GLITTERTECH.md`
asks that *"Glitterite sites contain murals, terminals, persona records, strange writings,
conversations and environmental evidence that the player can inspect if interested"*, and
that *"optional investigation can provide Intel progress/bonuses"*. The first half is a
**readout**; a mechanism that consumes a pawn-hour and shows the player nothing has not
implemented it. What VEF supplies and what it does not is surveyed below the build.

#### The build — one `Study` override, and the readout is ours

**Mechanism.** `Archinity.Sites.LoreRecord : VEF.Buildings.StudiableBuilding`, overriding the
`public virtual void Study(Pawn)` seam, plus a `LoreRecordExtension : DefModExtension` carrying
`string loreKey`, `int intelAmount`, `string signalTag` and `bool letterOnRead`.

**[V] Existence proof, shipped and 1.6.** `VanillaQuestsExpandedAncients.Building_BroadcastingStation
: VEF.Buildings.StudiableBuilding` (`3618306875/1.6/Assemblies/VanillaQuestsExpandedAncients.dll`)
overrides `Study(Pawn)`, resolves `Map.Parent` as a `Site` — falling back through
`PocketMapParent.sourceMap.Parent` exactly as `LootableBuilding.Open` does — sends
`QuestUtility.SendQuestTargetSignals(site.questTags, "VQE_BroadcastingStationIntercepted", …)`,
then calls `base.Study(pawn)`. **Copy its shape, but copy `LootableBuilding.Open`'s signal
*pair*:** VQE Ancients sends only the quest-target half, so a plain
`Find.SignalManager` listener would still miss it.

The override, in order: resolve the site `MapParent`; send both signals under
`<signalTag>`; if `loreKey` is unread, `Credit` the Intel and mark it read; raise the readout;
remove the instance from `studiables_InMap` — **T-59**, and still required even though this
build never designates anything, because the base class's own leak is what it closes; then
`base.Study(pawn)` for the `buildingLeft` swap and the sound.

**State, and why it is world-scoped rather than per-`Thing`.** The requirement is *"a
re-visited site does not pay twice."* A scribed `bool` on the building does not deliver that:
a site whose map has been abandoned is **regenerated** on re-entry, and the mural that comes
back is a new `Thing` with a fresh `false`. The one-shot therefore lives in
`WorldComponent_Charting` as `HashSet<string> readLore`, keyed on `loreKey` — the component
§6 already establishes, and the same component the Waystone `bool` sits in. `<buildingLeft>`
handles *"this mural, in this map, is now read"* for free and needs no state at all.

**Persistence.** `Scribe_Collections.Look(ref readLore, "readLore", LookMode.Value)` —
**strings, not `LookMode.Def`**, per the T-04 note in *Persistence and multiplayer*. Added to a
save that predates it, the set loads empty: every record reads unread, which is the safe
default, because the failure direction is "the player may read a mural again" and not "the
player is silently charged twice."

**Change.** `JobDriver_StudyBuilding.MakeNewToils`'s `tickIntervalAction` calls
`Building.Study(pawn)` once `totalTimer > 1200` **[V]** — an already-existing hook on the
synced tick.

**The job arrives by the player's right-click order, and that is the only path that works
for this object.** **[V]** `WorkGiver_StudyBuilding.HasJobOnThing` returns **false when
`t.Faction != pawn.Faction`**, and a mural on a Charting site carries a null or hostile
faction, so the work-giver never issues the job no matter what is designated — **T-62**.
`StudiableBuilding.GetFloatMenuOptions`' `TryTakeOrderedJob` path is unaffected by that test
and is also the path Multiplayer already synchronises (*Persistence and multiplayer*). Two
consequences for `LoreRecord`, and the cheap one is sufficient: **drop VEF's designation
gizmo in our `GetGizmos` override**, since it can only produce a designation that is never
worked and scribed state that is never synced. Keeping the gizmo instead means shipping
*both* an MP registration **and** our own `WorkGiver` subclass without the faction test —
roughly ~40 further lines **[I]**, and not costed below, because the build does not take it.

**The Intel itself is not ours.** It is `WorldComponent_Currencies.Credit(CurrencyDef, int,
string)`, owned by [`docs/specs/CURRENCIES.md`](CURRENCIES.md) — its establishing ticket
[#54](https://github.com/cjd721/Rimworld-Archinity/issues/54) is **closed**, so the spec,
not the ticket, is the destination. That document's *Credit C* names this caller: **a
`Study` override calling `Credit` directly, not `CompUseEffect_GainCurrency`**, which fires
only from `CompUsable` / `JobDriver_UseItem` and is never reached from
`StudiableBuilding.Study` **[V]**. This section supplies the studiable object; it does not
duplicate the store.

**Display — and `StudiableBuilding` supplies none of it.** An earlier draft counted the
pulsing overlay as a free "unread" marker. It is not one: `StudiableBuilding.DrawAt` draws
the `<overlayTexture>` `MetaOverlay` **only while the thing sits in `studiables_InMap`**
**[V]**, which is a *designated-for-study* marker — the player sees it only after acting on
an object they have already noticed, and never before. **The Display leg therefore stands on
the two surfaces that are ours anyway**, the archived letter and the read-variant
`<description>`; both persist, and neither depends on the overlay. A genuine unread marker,
if #61 wants one, is a `DrawAt` override on `LoreRecord` keyed on `readLore` rather than on
the designated set — ~10 lines **[I]**, optional, and not in the committed figure below.

- **The passage itself — an archived letter.** `Find.LetterStack.ReceiveLetter(label, text,
  LetterDefOf.NeutralEvent, this)`. **[V]** `Verse.LetterStack.ReceiveLetter(Letter, …)` calls
  `Find.Archive.Add(let)`, so the passage is permanently re-readable from the History tab, by
  **both** players, and is scribed with the game. It is the only surface that survives the
  colony leaving the site, and `lookTargets` jumps back to the object. Raised from the synced
  tick, so both clients receive it identically and it needs no `[SyncMethod]`.
  > This is not the mandatory-letter exposition the requirements exclude. That doctrine
  > constrains *"the mandatory research/completion messages"*; this letter exists only because
  > a player ordered a pawn to go and read something. **Which surface carries the passage is
  > nonetheless a requirements question, not a capability one** — see *Outstanding decisions*.
- **The permanent in-world record — `<buildingLeft>`, zero code.** The spent mural is replaced
  by a "read" `ThingDef` whose `<description>` carries the lore and renders in the inspect pane
  and the info card. **[V]** VQE Ancients ships exactly this idiom:
  `VQEA_AncientBroadcastingStation` → `VQEA_AncientBroadcastingStation_Off`, whose description
  reads *"Seems that whatever information it stored is long gone."* One extra `ThingDef` per
  record, no C#.
- **The designated marker — free, and it is not the unread marker.** `<overlayTexture>`
  pulses a `MetaOverlay` over any object sitting in `studiables_InMap` **[V]**. That reads as
  *"a pawn has been told to read this"*, not *"there is something here you have not read"*.
  Worth having; it is not the surface the requirement asks for.
- **A progress line while reading — free.** `<showProgressBar>true</showProgressBar>`.

Optionally, and cheaply: `readLore.Count` against the count of `loreKey`s declared in the
`DefDatabase` is an "N of M records recovered" line for whatever surface
[#61](https://github.com/cjd721/Rimworld-Archinity/issues/61) settles on. ~5 lines. It reads
only defs and a scribed set, so unlike the Waystone readout it is safe from client-local code
(**T-39** does not apply — no `CanRun` on this path).

**Cost, additive to §9.**

| Piece | Kind | Lines | Lands in |
|---|---|---|---|
| `LoreRecord : StudiableBuilding` + `LoreRecordExtension` | new C# | ~45 | `ArchinityAltar.dll` |
| `GetGizmos` override dropping VEF's designation gizmo (see *Persistence and multiplayer*) | new C# | ~5 | same |
| `readLore` set on `WorldComponent_Charting` | new C# | ~5 | **counted in §9's `WorldComponent_Charting` row, not added again here** |
| Per record: the `ThingDef`, its read variant, the extension block | XML | ~35 each | authoring, [#47](https://github.com/cjd721/Rimworld-Archinity/issues/47) |
| An unread-before-designation marker (`DrawAt` override) | new C# | +10 | optional, #61's call |
| "N of M records recovered" | new C# | +5 | optional, #61's call |

**~50 lines of new C# on the committed route — the first two rows — taking this document's
committed total from ~505 to ~555. [I]** on the estimate; the mechanisms are **[V]**. The
previous headline of ~55 / ~560 double-counted the `readLore` row, which is marked as living
inside §9's `WorldComponent_Charting` row and must not also be added to this one. Neither
optional row is in the ~555.

**If VEF leaves in [#15](https://github.com/cjd721/Rimworld-Archinity/issues/15), the
replacement is ~120 lines and is understood.** What would have to be rewritten is
`JobDriver_StudyBuilding` (~50), `WorkGiver_StudyBuilding` (~40) and the map component that
holds the designated set (~30) — all five types were read for this section and none of them is
subtle. The `Study` override, the extension, the world-scoped key and every display surface
above are ours already and do not change. **This capability is therefore a soft VEF
dependency, not one of the four hard ones.**

#### The survey behind it: what `StudiableBuilding` supplies, and what it does not

**[V]** Read end to end in
`steamapps/workshop/content/294100/2023507013/1.6/Assemblies/VEF.dll` —
`VEF.Buildings.StudiableBuilding`, `StudiableBuildingDetails`, `JobDriver_StudyBuilding`,
`WorkGiver_StudyBuilding` and `MapComponent_InteractableBuildingsInMap`. **The root is named
because it has to be:** VEF is one of the six mods whose two 1.6 copies on disk are not
byte-identical (**T-22** — `VEF.dll` differs by md5 between the workshop root and
`steamapps/common/RimWorld/Mods/`), so a bare `2023507013/…` path is ambiguous about which
file was decompiled. **Every claim in this section was checked against both copies and holds
in both.** Had any of them differed, this section would owe the reader a statement of which
copy the game actually loads — which, per T-22, the mod list does not tell you.

| Wanted | Supplied | Anchor |
|---|---|---|
| A pawn spends time at the object | **yes, on the ordered-job path** — walk, face, effecter, optional progress bar. **Not on the work-giver path for our object**: `HasJobOnThing` returns false when `t.Faction != pawn.Faction` — **T-62** | `JobDriver_StudyBuilding.MakeNewToils`; `WorkGiver_StudyBuilding.HasJobOnThing` |
| Optional and player-initiated | **yes** — nothing happens until the player orders it by right-click, or designates it by gizmo. **Only the gizmo adds to `studiables_InMap`**; the float-menu path makes the job directly and touches the set not at all | `StudiableBuilding.GetGizmos`, `.GetFloatMenuOptions` |
| An "unread" marker in the world | **no — a *designated-for-study* marker.** `DrawAt` draws the overlay only while the thing is in `studiables_InMap`, so nothing is visible before the player designates | `StudiableBuilding.DrawAt` |
| The spent object becomes a different object | **yes** — `<buildingLeft>`, pure XML | `StudiableBuilding.Study` |
| Skill matters | **XP only** — `skills.Learn(skillForStudying, 0.025f * delta)`; the duration does not scale | `JobDriver_StudyBuilding.MakeNewToils` |
| One-shot per instance | **by destruction, not by state** | `StudiableBuilding.Study` |
| **A quest signal** | **no** — **T-60** | below |
| **Any lore text, anywhere** | **no** | — |
| **Any reward but `Inspired_Creativity`** | **no** | `StudiableBuilding.Study` |
| **A configurable duration** | **no** — `public const int totalTime = 1200`, compared against a literal `1200` | `JobDriver_StudyBuilding` |

> **[V] T-62, stated once because it is the row that changes the build.** A site mural with a
> null or hostile faction **can** be designated — the gizmo appears, the overlay draws, the
> thing enters the scribed set, and under Multiplayer the two clients disagree about it — and
> is then **never worked**, because the work-giver refuses every thing whose faction is not
> the pawn's. The failure is visible action followed by silence, with no error and no log
> line. It is why the build routes on `TryTakeOrderedJob` and drops the gizmo.

**[V] No Anomaly coupling — the worry that sank the Analysis carrier does not apply here.**
Nothing in those five types references `ModsConfig.AnomalyActive`, `KnowledgeCategoryDef` or
`anomalyKnowledge`. `RimWorld.CompStudiable` is unrelated to VEF's studiable, and only its Anomaly branch is
Anomaly-bound: `AnomalyKnowledge` and `KnowledgeCategory` return early on
`!ModsConfig.AnomalyActive`, but its Core branch (`studyPoints`, `WorkGiver_StudyInteract`) has
no Anomaly dependency ([#115](https://github.com/cjd721/Rimworld-Archinity/issues/115)). VEF's
studiable is not a reskin of it and inherits none of
[#67](https://github.com/cjd721/Rimworld-Archinity/issues/67)'s problem.

> **[V] The signal split is real, and it is worse than `LootableBuilding_Custom`'s — T-60.**
> `StudiableBuilding.Study(Pawn)` is `public virtual` and is, in full: spawn `buildingLeft`,
> play `deconstructSound`, optionally
> `TryStartInspiration(InspirationDefOf.Inspired_Creativity)`, `DeSpawn`. It sends
> **neither** `Find.SignalManager.SendSignal` **nor** `QuestUtility.SendQuestTargetSignals`,
> where `LootableBuilding.Open()` sends **both**. A beat authored with
> `<inSignal>site.SomethingStudied</inSignal>` fires never, with no error. This confirms the
> hazard `docs/data/PARTS-BIN.md` §7.3 records for the lootable pair and extends it to the
> studiable, which that section currently describes only as *"the 'spend time at the site'
> verb, also XML."*

#### The other half: a record taken home

*Persona records* and *encrypted archives* are the requirements' own words, and they are
objects the colony carries away rather than murals read in place. The carrier for those is
**vanilla, not VEF**, and it is worth naming here because it is core, is not Anomaly-gated,
and needs no site at all:

**[V] `Verse.Book` is core.** `title` and `description` are **scribed per-instance strings —
and both fields are `private`** (a public `Title` getter exists; there is no setter for
either);
`DescriptionDetailed` renders them in the info card; `GenerateBook(Pawn, long?)` is
`public virtual`; `OnBookReadTick` runs every `BookOutcomeDoer` scaled by
`StatDefOf.ReadingSpeed`; vanilla ships `BookOutcomeProperties_GainResearch` and
`BookOutcomeProperties_GiveQuest`. Only its mental-break branch consults
`ModsConfig.AnomalyActive`. `VanillaBooksExpanded.Newspaper : Book`
(`2193152410/1.6/Assemblies/VanillaBooksExpanded.dll`) is the shipped 1.6 subclassing
precedent, overriding `Tick`, `GetInspectString` and `ExposeData`.

> **[V] The trap on that route, and it costs code.** `Book.PostPostMake` and
> `Book.PostQualitySet` both call `GenerateBook()`, which overwrites `title` and
> `description` from the grammar packs. An authored string assigned to a `Book` instance is
> silently replaced — and **the obvious escape hatch does not work**: overriding
> `GenerateBook` suppresses the overwrite but cannot supply the text, because a subclass
> **cannot write its base class's `private` fields**. Authoring a book's prose therefore
> takes **reflection (`AccessTools.FieldRefAccess`) or a Harmony patch**, in addition to the
> subclass or instead of it. No mod in the corpus authors book text — Medieval Overhaul's
> `CompProperties_DefinableBook` only adds a `qualityRange`, and its `Book_GenerateBook_Patch`
> sets the *author*, not the prose — which is consistent with the fields being closed.

A `Book` def in a `LootableBuilding`'s `<contents>` list is therefore an authored record that
is looted (with the signal), hauled home, read for research or Intel, and kept — **but not at
zero C#.** An earlier draft priced the item itself at nothing; the private fields make it
**~20 lines [I]**: a `Book` subclass whose `GenerateBook` override stops the grammar pass,
plus a reflected write of `title` and `description` from a `DefModExtension`. Once written,
persistence is free — both fields are scribed per instance **[V]**. **That ~20 is not in this
document's committed ~555**: this half is flagged, not designed. What those records say is
[#47](https://github.com/cjd721/Rimworld-Archinity/issues/47)'s (open); whether Intel arrives
from reading rather than from decoding is [`CURRENCIES.md`](CURRENCIES.md)'s *Credit B*
`CompUseEffect_GainCurrency` route — valid **here**, because a carried book is used through
`CompUsable`, unlike the studiable object in the build above. Its ticket
[#54](https://github.com/cjd721/Rimworld-Archinity/issues/54) is closed; the spec owns it.

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

**[V] §10's lore route breaks that "no state-writing gizmo" rule, and it is inherited rather
than ours.** `VEF.Buildings.StudiableBuilding.GetGizmos` builds a `Command_Action` whose
`action` calls `MapComponent_InteractableBuildingsInMap.AddStudiablesToMap(this)`, and that
`HashSet<Thing>` is scribed — `Scribe_Collections.Look(ref studiables_InMap, "studiables_InMap",
LookMode.Reference)`. **No Multiplayer Compat patch registers it — T-61.** Every ASCII and
UTF-16 string literal in 1.6's `Multiplayer_Compat.dll` and `Multiplayer_Compat_Referenced.dll`
was extracted byte-exactly, in **both** encodings, from the **md5-identical** copies under both
corpus roots: **65 distinct `VEF.*` names are present — 11 of them `VEF.Buildings.*`** — while
`StudiableBuilding`, `LootableBuilding`, `AddStudiablesToMap` and
`MapComponent_InteractableBuildingsInMap` are all **absent**. (An earlier draft said
"forty-odd", which understated the control set and therefore the strength of the negative.)
Unsynced, one client designates a mural and the other's colonists never see it, and the
divergence is in the save.

Two consequences, and the first is the cheap one:

- **[V] The right-click path is already safe and the gizmo is not.**
  `StudiableBuilding.GetFloatMenuOptions` ends in
  `selPawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(InternalDefOf.VFE_StudyBuilding, this), …)`,
  and `Multiplayer.Client.SyncMethods` registers
  `SyncMethod.Register(typeof(Pawn_JobTracker), "TryTakeOrderedJob").SetContext(...).ExposeParameter(0)`.
  Ordering a pawn to read a mural is synced by Multiplayer generically; *designating* one is not.
- **We drop the gizmo on our own subclass, rather than register it.** **[V]** Registration is
  per **concrete type** by lambda ordinal — the same fact this document already records for
  `CompLongRangeMineralScanner` — so **a subclass inherits nothing**, and `GetGizmos` on
  `LoreRecord` has to be overridden either way. Registering it would be the fix **if the
  designation did anything**; for a site mural it does not, because `WorkGiver_StudyBuilding`
  refuses a thing whose faction is not the pawn's (**T-62**, §10). So the override removes the
  command instead: no unsynced scribed write, no designation that is never worked, and the
  right-click order above remains the one path — already synced, already working.
  Multiplayer Compat *does* register such a gizmo for a third-party studiable —
  `MpCompat.RegisterLambdaMethod("VanillaQuestsExpandedTheGenerator.Building_Genetron_Studiable",
  "GetGizmos", 0)`, at **lambda ordinal 0** and notably **without** `.SetDebugOnly()`, so MP
  treats a study designation as a real sync surface — which is the evidence that leaving VEF's
  gizmo live and unregistered is a genuine desync, not a theoretical one. **[I]** that that
  type derives from VEF's `StudiableBuilding`; the mod is not on disk and the inference is from
  the name and the registration shape.

> **The build has no *other* state-writing gizmo, deliberately.** There is no target to select,
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
  tick and threat points.** `CanRun` → `root.TestRun(...)` → `TileFinder.TryFindNewSiteTile` →
  `list.RandomElement()`, with the result cached in `[Unsaved]` tick/points fields. Calling
  it from any client-local path makes two clients draw a different number of values in the
  same tick. The name reads as a pure predicate and is not one. This build has three `CanRun`
  call sites — `TickDoesFind`, `GetNextSubquestDef` and, forbidden, the Waystone inspect
  string. The first two are on the synced tick and are fine; the constraint on the third is
  stated at the readout in §8.

**Four more this build inherits from VEF, all found on
[#80](https://github.com/cjd721/Rimworld-Archinity/issues/80) and all now in the register as
T-59 to T-62.**

- **T-59 — `StudiableBuilding.Study` leaks its own entry out of the designated set.** **[V]** `Study`
  ends in `DeSpawn(DestroyMode.Vanish)`, and only the `Destroy` and `Kill` overrides call
  `RemoveStudiablesFromMap`. `Thing.Destroy` calls `DeSpawn`, never the reverse, so a *studied*
  building is never removed: it stays in a `HashSet<Thing>` scribed with `LookMode.Reference`,
  `WorkGiver_StudyBuilding.ShouldSkip` never short-circuits again on that map, and the set
  accumulates references to things no `ThingOwner` saves. **[V]** VQE Ancients'
  `Building_BroadcastingStation` inherits it by calling `base.Study(pawn)`. No error, no log
  line. **Fix in our override: call `InteractablesMapComp?.RemoveStudiablesFromMap(this)`
  explicitly**, which `LoreRecord` must do anyway because it does not always want the despawn.
- **T-60 — `StudiableBuilding.Study` sends no quest signal**, where `LootableBuilding.Open`
  sends both. Covered in §10; it is listed here because the failure is a beat that never
  completes, with nothing on screen and nothing in the log.
- **T-61 — VEF's study-designation gizmo writes scribed `MapComponent` state that no
  Multiplayer Compat patch covers.** **[V]** on the write — `AddStudiablesToMap` puts the
  thing into `studiables_InMap`, scribed `LookMode.Reference`, from a `Command_Action`. The
  absence is a full literal extraction of both compat assemblies rather than a sweep hit,
  with 65 `VEF.*` names as its control. The right-click path is safe only
  because MP registers `Pawn_JobTracker.TryTakeOrderedJob` generically. See *Persistence and
  multiplayer*; the build drops the gizmo.
- **T-62 — `WorkGiver_StudyBuilding.HasJobOnThing` returns false when
  `t.Faction != pawn.Faction`.** **[V]** A designation on a null- or hostile-faction building
  — which is every mural on a Charting site — succeeds visibly and is never worked. Gizmo,
  overlay and scribed set all behave; no pawn ever comes, and nothing is logged. This is the
  trap that decides §10's job path.

**One authoring hazard, not a code failure.** A lore record's `<loreKey>` is the identity the
one-shot rests on. Renaming a key between saves re-opens that record for a second payment;
reusing a key across two different records silently makes the second one unreadable. Keys are
strings by design (**T-04**), so nothing validates them — the same class of author-time hazard
as a removed `ChartingBeatDef` in the table above.

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

§10 was added on [#80](https://github.com/cjd721/Rimworld-Archinity/issues/80), evidence class
**READ**, against `VEF.dll`, `VanillaQuestsExpandedAncients.dll`, `VanillaBooksExpanded.dll`,
`MedievalOverhaul.dll`, `Multiplayer.dll`, `Multiplayer_Compat{,_Referenced}.dll` and
`Assembly-CSharp.dll`. **It corrects its own ticket on one load-bearing point:** #80 held that
*"a carrier exists and is already a dependency… so this reduces to a verification rather than a
build."* The carrier exists for the verb only. It sends no quest signal, awards nothing but
`Inspired_Creativity`, and displays no text anywhere — so the half of the requirement that is
actually a readout has no carrier at all, and this is a build of ~50 lines rather than a
verification. The audit of that section additionally established that VEF's designation path
is **inert** for a site mural (**T-62**) and that its pulsing overlay marks *designated*, not
*unread* — so the readout's own surfaces, the archived letter and the read variant, are all
of it.

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

**Positives, §10.** `VEF.Buildings.StudiableBuilding` (the study verb, player-initiated,
XML-configured, `<buildingLeft>` swap, a pulsing *designated* overlay, no Anomaly coupling —
but an inert work-giver path for a non-player-faction thing, **T-62**);
`Verse.LetterStack.ReceiveLetter` → `Find.Archive.Add` (a permanently re-readable passage);
`Verse.Book` (per-instance scribed `title`/`description`, `ReadingSpeed`-scaled
outcome doers, core rather than Anomaly — **but both fields `private`, so authoring the prose
costs reflection or a Harmony patch**); `Multiplayer.Client.SyncMethods`'
`Pawn_JobTracker.TryTakeOrderedJob` registration (the right-click study order is synced free).

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

**A fourth, for §10, swept with the null-interleaved form rather than the broken one.**
**Nothing in the corpus carries an authored-lore readout on a site object.** `StudiableBuilding`
appears in exactly two mods — VEF, which defines it, and VQE Ancients, which subclasses it once
for a quest signal (`3618306875`); both roots and `Data/` searched, `-g '!**/obj/**'`, and the
sweep validated against `LootableBuildingOpened` as a control hit in both encodings.
`CompLore`, `LoreDef`, `CompDatalog` and `CompTerminal` return nothing at all. `CompReadable`
returned three mods and **evaporated on decompilation** — neither Vanilla Books Expanded nor
Medieval Overhaul defines such a type, which is the *metadata hit is [I], not [V]* rule paying
for itself. Vanilla's `Book` is the nearest shipped mechanism and is a carried item, not a site
fixture; see §10.

**Not taken for §10.** `RimWorld.CompStudiable` (Core branch) / `CompAnalyzable` — not
Anomaly-bound ([#115](https://github.com/cjd721/Rimworld-Archinity/issues/115)); not taken because
the selected route already carries the study verb on VEF's studiable, with the readout ours either
way. `WorkGiver_StudyInteract.HasJobOnThing` has no faction test, so T-62 would not apply to it.
`Verse.Dialog_NodeTree` — a real authored-passage window shipped by ten mods, but a per-client
`Window` whose options run client-local code; usable only with a single read-only Close option,
at which point the archived letter is strictly better because it persists.

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

**Two narrow RUN items remain**, and both are confirmations rather than open questions:

1. **That the two-accumulator override behaves.** With no eligible return-pool beat,
   `daysWorkingSinceLastFinding` must stay at zero while `surveyDaysWorking` climbs at the
   full rate; a return find must zero only the return accumulator. This is the one place the
   design leans on `Used`'s internal ordering rather than on a documented contract.
2. **That a `LoreRecord` on a real site is readable at all (§10).** Right-click a mural on a
   generated Charting site with a colonist selected, confirm the pawn walks, reads and that
   the letter and the read variant appear. **T-62** says the work-giver path cannot do this
   for a non-player-faction thing; this check confirms the ordered-job path can, which is the
   whole of the build's job routing.

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
- **Where a lore passage actually appears to the player, and whether reading one is worth
  Intel at all.** `docs/requirements/GLITTERTECH.md` says the player *"can inspect if
  interested"* and that investigation *"can provide Intel progress/bonuses"*, and never says
  which surface carries the text or what the bonus is. §10 builds the archived letter plus the
  read-variant description because something must be chosen and those two are the surfaces that
  persist; the choice is a requirement and the amount is a balance number.
  **This is a gap with no owner.** [#47](https://github.com/cjd721/Rimworld-Archinity/issues/47)
  is open and authors *what the lore says*; the currency is
  [`CURRENCIES.md`](CURRENCIES.md)'s, its ticket
  [#54](https://github.com/cjd721/Rimworld-Archinity/issues/54) being **closed**. Neither
  owns the surface — which is the same shape of hole
  [#52](https://github.com/cjd721/Rimworld-Archinity/issues/52) fell into, so it is written down
  here rather than deferred to a ticket that does not exist. The mechanism does not wait on it.
- **Whether a lore record may be read more than once for no further reward, or should become
  inert.** §10 assumes the former — the passage stays readable, the payment does not repeat —
  because *"the richer history remains in the places being raided"* reads as a standing
  invitation rather than a consumable. A requirement, one line, currently unwritten.
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
