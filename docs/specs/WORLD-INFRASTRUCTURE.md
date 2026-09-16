# World infrastructure

## Purpose and scope

How the world's road network satisfies
[`docs/requirements/WORLD-INFRASTRUCTURE.md`](../requirements/WORLD-INFRASTRUCTURE.md):
completing an era capstone advances the road quality available to civilizations; every
civilization then builds or upgrades routes between its own settlements and the settlements of
allied neighboring factions, **visibly and over time** (about thirty in-game days as a starting
target), world-wide rather than in a radius around the player; the player may **fund** a planned
route to finish it sooner or extend it farther, and may **build roads directly**. It carries the
same beat in [`docs/plot/MEDIEVAL.md`](../plot/MEDIEVAL.md) — *"On each era advance,
civilizations begin upgrading routes to allied neighbors over time"* — and
[`docs/plot/INDUSTRIAL.md`](../plot/INDUSTRIAL.md) § *Roads and Mobility* — *"the vanilla map
should not begin covered in modern paved roads… other factions also build it."*

This document owns the **world-map mobility ladder**: what road tiers mean for travel (§1), what
exists at worldgen (§2), the era-driven construction process and the player's two verbs (§3), and
**vehicles** ([#69](https://github.com/cjd721/Rimworld-Archinity/issues/69), §4), which multiply
with roads and cannot be tuned apart from them.

It does **not** own:

- **The era clock or its trigger.** [`ERA.md`](ERA.md)
  ([#109](https://github.com/cjd721/Rimworld-Archinity/issues/109)) owns `GameComponent_Era`;
  [#113](https://github.com/cjd721/Rimworld-Archinity/issues/113) settled that completing the
  capstone research project calls `AdvanceEra()` exactly once. §3 **reads** that clock and adds no
  trigger of its own.
- **The alliance graph.** [`POLITICS.md`](POLITICS.md) § *The build* §1 seeds the NPC↔NPC
  alliance edges; vanilla creates none (§3b). §3 reads the graph and writes nothing to it.
- **Charting.** [`docs/requirements/CHARTING.md`](../requirements/CHARTING.md) (*Road construction
  is not a Charting decision*): Charting never builds, upgrades, finances or prices a road. Whether
  completed mobility later contributes a reach rung is cross-spec integration
  ([#118](https://github.com/cjd721/Rimworld-Archinity/issues/118)); the rung shapes at the end of
  this document are offered, not selected.
- **Numbers.** Tier speeds, which tier each era unlocks, build duration, neighbor radius and
  funding prices belong to the balance deferral in
  [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2).

One plot verb is still unanswered: *"finance, **protect**, capture and benefit from"*
infrastructure. Finance, capture and benefit are below; **protect is a gap**, carried on the map's
fog as *Protecting infrastructure*.

## The build

**Roads are a shipped engine system with a broken dial and no builder.** Vanilla carries five
tiers, per-edge storage, free persistence, a world draw layer, an A\* world pather that already
prefers existing roads, and three inspect surfaces. VFE Classical carries direct player road
building and Multiplayer Compatibility syncs it. **Nothing in the corpus grows NPC roads over
time** — the only two mods that write roads at runtime are both player-initiated (*Available
mechanisms*). So the road half is three XML repairs (§1, §2, §4c) plus **one new `WorldComponent`
of ours**, `WorldComponent_RoadNetwork`, which turns an era advance into a queue of route projects
and lays them edge by edge on the synced world tick (§3).

**Vehicles are the reverse.** The content, the gating and the world-travel maths all ship and
work; what is missing is **determinism under Multiplayer**, which costs three Harmony prefixes and
about sixty lines of C# that nobody else is going to write (§4).

### 1. Differentiate the tiers — the change everything else rests on

**All five vanilla `RoadDef`s ship `movementCostMultiplier 0.5`** [V]
(`Core/Defs/RoadDefs/RoadDefs.xml`). A dirt path is exactly as fast as an ancient asphalt
highway. Road *tier* changes the world-map texture, the terrain laid on a generated map and
`tilesPerSegment` — and changes travel time by nothing at all.

Until that is fixed, "the world physically becomes connected" has no mechanical referent,
road *tier* carries zero information to any consumer, and upgrading a road is a silent
no-op (**T-42**).

**In `Assembly-CSharp` the field has exactly two readers** [V] —
`WorldGrid.GetRoadMovementDifficultyMultiplier` and
`WorldGrid.FindMostReasonableAdjacentTileForDisplayedPathCost` — enumerated from a whole-
assembly decompile, not sampled. `Caravan_PathFollower.CostToMove` reads it **live, per
edge, per call** [V]; there is no cache, so nothing needs invalidating and a cached copy
would be a bug of **the T-20 class**.

**The "no blast radius" claim is scoped to `Assembly-CSharp`, and there are two more readers
in the corpus — both in Vehicle Framework, and §4c is what makes them obey.**
`Vehicles.RoadCostHelper.GetRoadMovementDifficultyMultiplier` exists in **two `RoadDef`
overloads, not one** [V] — `(List<VehicleDef>, RoadDef)` and `(List<VehiclePawn>, RoadDef)`,
byte-for-byte the same loop. The `VehiclePawn` overload is the one a live caravan takes;
an earlier draft of this section named only the `VehicleDef` one. Both take
`roadDef.movementCostMultiplier` as a **base** and let
`VehicleDef.properties.customRoadCosts[roadDef]` **replace** it [V]. The replacement is
**unconditional and works in either direction**: the loop is
`if (customRoadCosts.TryGetValue(roadDef, out value) && (!flag || value < num))`, so the *first*
declaring vehicle overwrites the `RoadDef` base whatever its value — `!flag` short-circuits the
comparison — and "lower wins" applies only *among* declaring vehicles. A declaring vehicle can
therefore be **slower** than the ladder says, not only faster.

**As shipped that bypasses the ladder silently, and §4c closes it.** Fourteen of VVE's
twenty-three vehicles declare `customRoadCosts`, so for most of the roster every tier resolves
to one flat number and this section's five-step ladder is invisible. §4c hangs
`Vehicles.CustomCostDefModExtension` on each of the five `RoadDef`s and overwrites that table
with the ladder's own values, for every vehicle in the database. **§4c is selected, not
optional**: without it the table below changes travel time only for caravans on foot, and the
vehicle half of the mobility ladder reads a constant. §4c carries the full reading, the
alternatives and the cost; this section states the dependency once and does not restate it as a
caveat.

A ladder, as a `PatchOperationReplace` per def (values are a starting proposal, not a
balance ruling — the balance deferral in [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2) owns the
numbers; see *Outstanding decisions*):

| `RoadDef` | ships | proposed | reads as |
|---|---|---|---|
| `DirtPath` | 0.50 | 0.75 | a trail someone walks |
| `DirtRoad` | 0.50 | 0.60 | a maintained track |
| `StoneRoad` | 0.50 | 0.45 | a medieval power's route |
| `AncientAsphaltRoad` | 0.50 | 0.35 | industrial paving |
| `AncientAsphaltHighway` | 0.50 | 0.25 | a highway |

Pure XML, five operations. **Not a freeze item** — `RoadDef` is a def, read live at every
`CostToMove`, so the ladder is free to retune at any point in the campaign.

### 2. Suppress the asphalt at worldgen — two PatchOperations, no C#

Two world gen steps place roads, both attached to
`PlanetLayerDef[defName="Surface"]/worldGenSteps` [V]
(`Core/Defs/PlanetLayerDefs/PlanetLayers.xml`):

- **`AncientRoads`** (order 400) → `WorldGenStep_AncientRoads`, which hard-codes
  `RoadDefOf.AncientAsphaltRoad` and `RoadDefOf.AncientAsphaltHighway` between ancient
  sites [V]. **This is the source of "modern paved roads at start."** There is no XML field
  selecting which def it lays.
- **`Roads`** (order 600) → `WorldGenStep_Roads`, which links settlements and extra nodes,
  and picks the tier with
  `DefDatabase<RoadDef>.AllDefsListForReading.Where(rd => !rd.ancientOnly).RandomElementWithFallback()`
  [V] — a **uniform random draw**, with no faction, tech level or biome input at all.

So the suppression is:

```xml
<!-- expect: 1 -->
<Operation Class="PatchOperationRemove">
  <xpath>/Defs/PlanetLayerDef[defName="Surface"]/worldGenSteps/li[text()="AncientRoads"]</xpath>
</Operation>

<!-- expect: 1 -->
<Operation Class="PatchOperationAdd">
  <xpath>/Defs/RoadDef[defName="StoneRoad"]</xpath>
  <value><ancientOnly>true</ancientOnly></value>
</Operation>
```

> **Both xpaths are UNRUN.** [I] The target nodes are confirmed present — `<li>AncientRoads</li>`
> under `PlanetLayerDef[defName="Surface"]/worldGenSteps` in
> `Core/Defs/PlanetLayerDefs/PlanetLayers.xml`, and `StoneRoad` with no existing
> `<ancientOnly>` [V] — so both *should* match at `expect: 1`, but neither has been dry-run
> and the `expect: 1` annotations are an assertion, not a measurement.
> **[#102](https://github.com/cjd721/Rimworld-Archinity/issues/102) must land before they
> can be**: `tools/defdb.py`'s `_apply_leaf` evaluates patch xpaths *relative to* `<Defs>`,
> so a leading-`Defs/` xpath — which both of these are — matches nothing while
> `report.patch_ops_applied` still increments and the tool reports success. A STUB run
> today would report a pass it did not perform.

The first removes every asphalt road and highway from the generated world. The second takes
`StoneRoad` out of the worldgen draw, leaving `WorldGenStep_Roads` to pick uniformly between
`DirtPath` and `DirtRoad`. **`ancientOnly` has exactly one reader in the whole assembly** —
that `Where` clause [V] — so it is a precise, single-effect lever and not a repurposing.

**It does not remove road debris, and an earlier draft of this document was wrong to say it
did.** `GenStep_ScatterRoadDebris.Generate` computes
`count = (mapHasRoads ? VehicleRangeRoadMap : VehicleRangeNonRoadMap).RandomInRange`, and
`VehicleRangeNonRoadMap = new IntRange(1, 2)` [V] — a roadless map still spawns **1–2
ancient vehicle wrecks**. Worse, `CanScatterAt`'s `!c.GetTerrain(map).IsRoad` rejection has
nothing to reject, so the wrecks **scatter map-wide** instead of hugging the road line.
Removing `AncientRoads` therefore makes road debris *less* localised, not absent. **If car
wrecks are unwanted on a Neolithic map that is a separate lever** — the
`GenStep_ScatterRoadDebris` entry in the map generator's step list — and it has not been
investigated. Named as a gap in *Outstanding decisions*.

Otherwise the result is the Neolithic map the plot asks for: paths and dirt tracks between
settlements, no stone, no asphalt, no ruined highways.

**A third lever exists and is deliberately not used globally.** VEF ships
`FactionDefExtension.neverConnectToRoads`, a per-`FactionDef` boolean whose postfix on
`WorldGenStep_Roads`'s endpoint predicate drops that faction's settlements from the road
network [V] (`VEF.Factions.VanillaExpandedFramework_GenerateRoadEndpoints_Patch`). It is
pure XML and already ships. It is the wrong instrument for a *global* suppression, because
`GenerateRoadEndpoints` also seeds 30–50 extra road nodes per 100k tiles from
`TileFinder.RandomSettlementTileFor` [V], which are not world objects and survive the
extension entirely — so setting it everywhere yields a road network attached to nothing.
Used **selectively** it is exactly right: the anima tribe and the high-tech strongholds
([#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) § *the exemption*) should have
no road reaching them, and one XML field per faction says so.

### 3. Era-driven route construction — `WorldComponent_RoadNetwork`

> **This section replaces the era-rite build of 2026-09-12** — an instantaneous re-overlay of road
> links within a proximity radius, run inside [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8)'s
> synced command — which the requirement correction of 2026-09-13 superseded. Everything it
> rested on was **re-read against the 1.6 assemblies** by #68's second reopen rather than
> inherited: `SurfaceTile.potentialRoads`, `WorldGrid.OverlayRoad`, the `SurfaceLayer`
> persistence, VFE Classical and its Multiplayer Compatibility sync. Its ledger is folded into
> §3f.

**Mechanism.** One `WorldComponent` in `Archinity.Core`. When the era advances it **plans** one
route project per allied settlement pair (§3b). On the world tick it spends a daily work budget on
each project and writes each finished edge with `WorldGrid.OverlayRoad` (§3c). **The road on the
map is the progress bar**: a half-built route is the built prefix of its path. The player can pour
resources into a project (§3d) or pave on their own with a caravan (§3e). Every mechanism named
below is [V]; **the claim that they compose into this behaviour is [I]** until something is built.

#### 3a. Trigger — read the era clock, add no second one

[#113](https://github.com/cjd721/Rimworld-Archinity/issues/113) settled the trigger: the capstone
`ResearchProjectDef`'s completion calls `GameComponent_Era.AdvanceEra(next)` once, on the
synchronized research-completion path ([`ERA.md`](ERA.md) § *The build* § 3, *What calls it*).
Roads observe the result:

```
WorldComponent_RoadNetwork.WorldComponentTick — every 2500 ticks (one in-game hour):
    era = Current.Game.GetComponent<GameComponent_Era>().CurrentEra
    if era > lastPlannedEra:
        EnqueuePlan(era)          // §3b; cancels lower-tier unfinished projects
        lastPlannedEra = era
```

**Why a poll of our own clock rather than a fifth line inside `AdvanceEra()`.** `CurrentEra` is
the last row of an append-only boundary log that only `AdvanceEra()` writes ([`ERA.md`](ERA.md)
§ *The build* § 2). Reading it adds no caller to the single writer, heals a missed notification
on the next hour, and sits on the synced tick. [`ERA.md`](ERA.md) § *Available mechanisms* rejects
VFE Tribals' poll because it polls a **def mutation** any mod can make; this polls the
authoritative log. The alternative — `AdvanceEra()` calling `Notify_EraAdvanced(next)` directly —
is one line but edits a method this document does not own. **Poll recommended** [I].

#### 3b. Planning — who connects to whom

Runs once per era advance, entirely from synchronized world state, and **draws no random number**.

1. **Tier.** The highest-`priority` `RoadDef` whose `Archinity.RoadEraExtension.era ≤ era`. One
   `DefModExtension` per `RoadDef`, pure XML. Which tier each era gets is Balance. §3 plans only on an advance, so it
   never lays a Neolithic tier — `DirtPath`/`DirtRoad` are §2's worldgen roads. The standing
   proposal, in era-entered terms: `StoneRoad` on entering Medieval, `AncientAsphaltRoad` on
   entering Industrial, `AncientAsphaltHighway` on entering Spacer.
2. **Civilizations.** `Find.FactionManager.AllFactionsListForReading`, filtered to
   `!IsPlayer && !Hidden && !defeated && !temporary` with at least one `Settlement`, **ordered by
   `loadID`**. A faction whose def carries VEF's `FactionDefExtension.neverConnectToRoads` is
   skipped, so §2's isolated factions stay unconnected at runtime as well as at worldgen.
3. **Allied neighbors.** For builder A, the partner factions are A itself and every B with
   `A.RelationKindWith(B) == FactionRelationKind.Ally` [V, `RimWorld.Faction.RelationKindWith`].
   **Vanilla supplies no such B.** `Faction.TryMakeInitialRelationsWith`'s local
   `GetInitialGoodwill` returns only −100, −80 or 0, and the relation is made `Ally` only at ≥ 75,
   so a fresh world holds no NPC↔NPC alliance at all [V, re-read this session; the same finding is
   [`POLITICS.md`](POLITICS.md) § *The graph is empty*]. The edges come from
   [`POLITICS.md`](POLITICS.md) § *The build* §1, *Seed the edges*. **Until that seed ships, §3
   builds intra-faction routes only.**
4. **Neighbor.** For each settlement *s* of A, ordered by `ID`: up to **k** partner settlements
   within **R** tiles by `WorldGrid.ApproxDistanceInTiles`, nearest first, ties broken by `ID`.
   Unordered pairs are deduplicated. **k and R are Balance; the rule is the mechanism.** Whether
   intra-faction pairs count, and whether player colonies are eligible partners, are requirement
   questions (*Outstanding decisions*).
5. **Path.** `s.Tile.Layer.Pather.FindPath(s.Tile, t.Tile, caravan: null)` [V,
   `RimWorld.Planet.WorldPathing.FindPath`]. The edge cost is
   `3300 × layerMovementDifficulty[tile] × WorldGrid.GetRoadMovementDifficultyMultiplier(from, to)`,
   so **the live road multiplier is inside the cost and new routes run along existing roads**. That
   is the "pave the tracks already there" property the superseded build got by refusing to path at
   all, now obtained by pathing — and it is exactly how vanilla lays its own network:
   `WorldGenStep_Roads.DrawLinksOnWorld` calls `layer.Pather.FindPath(a, b, null)` and overlays
   every edge of the result [V]. **Release every result with `WorldPath.ReleaseToPool()`**:
   `WorldPathPool.GetEmptyWorldPath` force-clears the pool with
   *"WorldPathPool leak: more paths than caravans"* once it holds more paths than caravans + 2 +
   route-planner waypoints [V]. An unreachable pair returns `WorldPath.NotFound` and plans nothing.
6. **Work.** An edge is *pending* when `GetRoadDef(a, b, visibleOnly: false)` is null or has
   `priority` below the tier. Edges already at tier cost nothing — the idea is RimPacts'
   `PayableSegments` (*Available mechanisms*). The project's rate is
   `edgesPerDay = max(minRate, pendingEdges / buildDays)`, so a route finishes in about
   `buildDays` whatever its length. **The alternative is a constant per-edge speed** — RimPacts
   uses 0.25 days per tile — which makes long routes take longer. Which one "about thirty days"
   means is Balance's call; the component supports both with one branch.

**Planning is spread, not bunched.** Pairs enter a scribed pending queue and one A\* runs per
tick until it drains, so an advance with dozens of pairs costs no single tick a stall. Ordering is
fixed by steps 2 and 4, so the spread changes nothing about the result. [I]

#### 3c. The construction clock — partial progress

```
RouteProject : IExposable
    int id;  Faction builder;  Settlement from, to;  RoadDef tier
    List<int> pathTileIds          // surface-layer tile ids, in walking order
    int nextEdge                   // edges [0, nextEdge) are laid
    float workDone, fundedWork, edgesPerDay
    int startedTick, completedTick
    RouteState state               // Building, Paused, Complete, Cancelled
```

Every 2500 ticks, per `Building` project, in `id` order:
`workDone += edgesPerDay / 24 + drain(fundedWork)`; while `workDone ≥ 1` and edges remain,
`Find.WorldGrid.OverlayRoad(path[nextEdge], path[nextEdge + 1], tier)`, `nextEdge++`,
`workDone -= 1`. After the pass, one `Find.World.renderer.SetDirty<WorldDrawLayer_Roads>(layer)`.

- **Upgrade-only is the collision rule, and it is free.** `OverlayRoad` returns when the existing
  road *is* the new def, returns silently when its `priority` is ≥ the new one (**T-43**), and
  otherwise removes both symmetric links before adding the new pair [V,
  `RimWorld.Planet.WorldGrid.OverlayRoad`]. Two projects sharing an edge, a project crossing a
  player-paved road, and a later era's project over an earlier one therefore cannot downgrade
  anything and need no coordination.
- **Redraw narrowly — never `SetAllLayersDirty()` on a clock.** VFE Classical and RimPacts both
  call `SetAllLayersDirty()` after a road write [V]. That dirties `WorldDrawLayer_Terrain`, and
  `WorldRenderer.DrawWorldLayers` → `RegenerateLayersIfDirtyInLongEvent` queues a
  `"GeneratingPlanet"` long event whenever a visible terrain layer is dirty [V,
  `WorldRenderer.ShouldRegenerateDirtyLayersInLongEvent`]. `SetDirty<WorldDrawLayer_Roads>` flags
  only the roads layer (`WorldDrawLayer_Roads : WorldDrawLayer_Paths : WorldDrawLayer`), which
  `WorldDrawLayerBase.Render` regenerates inline on its next draw [V]. The long event queues only from `DrawWorldLayers`,
  when a visible `WorldDrawLayer_Terrain` is dirty, so a clock landing edges while the world map is
  open could re-trigger it; the narrow form avoids it [I — the code path is read, the hitch is not
  observed].
- **Invalidation, checked each pass.** An endpoint destroyed or unspawned, an endpoint's faction
  changed, or the pair's relation no longer `Ally` moves the project to `Paused` or `Cancelled` —
  which of the two is a requirement question. Laid edges stay: there is no removal path (**T-43**).
- **A later era supersedes.** Planning for the next era cancels unfinished lower-tier projects and
  re-plans; the new paths prefer the edges already laid (step 5), so the old prefix is upgraded in
  turn rather than abandoned.
- **No-roads biomes are crossed, as vanilla crosses them.** `FindPath` rejects only
  `World.Impassable` tiles and never consults `BiomeDef.allowRoads` [V], so a route can pass
  through a biome whose roads are drawn but inert (**T-44**). Vanilla worldgen lays its network
  through the same call with the same result [V]. Accepted and listed under *Failure and recovery*.

#### 3d. Funding — the player's first verb

*"Contribute resources to a planned route to complete it sooner or extend it farther."*

- **Sooner.** Contributed goods convert to `fundedWork` at a per-tier price
  (`RoadEraExtension.fundingCosts`, a `List<ThingDefCountClass>` per edge — XML). The clock drains
  `fundedWork` at up to a capped extra rate per pass, so funding **accelerates** a project rather
  than completing it on the click. The cap is Balance; no cap means an instant finish.
- **Farther.** `Extend(projectId, targetTile)` paths from the project's far endpoint to the target
  with the same `FindPath`, appends the tiles, and prices the new pending edges. What a player may
  extend *to* — another settlement, their own colony, any tile — is a requirement question.
- **Where the player does it: a caravan gizmo** [I]. A postfix on `Caravan.GetGizmos` offers
  *Fund road project* when the caravan stands on, or next to, a tile of a `Building` project's path
  or one of its endpoint settlements. A local window picks the amount; the commit is

  ```csharp
  [SyncMethod] static void SyncedFund(Caravan caravan, int projectId, int units);
  [SyncMethod] static void SyncedExtend(Caravan caravan, int projectId, int targetTileId);
  ```

  Both **re-validate inside the synced call** — the project still exists and is `Building`, the
  caravan still holds the goods — and **remove the goods there**, never in the UI delegate. That is
  the shape Multiplayer Compatibility gives VFE Classical: targeting client-local, commit synced
  [V, §3e]. Both donors that already sell road work get it wrong: RimPacts spends silver inside a
  confirmation dialog's delegate and Faction Territories spends points from a `Widgets.ButtonText`,
  neither synced (*Available mechanisms*).
- **The alternative is a comms-console option** on the builder faction's dialogue.
  `docs/engine/determinism.md` § *MP serialises the comms-console dialogue, options included*
  says an appended option needs no `[SyncMethod]` of ours, but **T-82** makes it sync by the
  option's **index**, and the goods would come from beacons rather than a caravan. What separates
  the two is whether funding requires physical presence — a requirement call. Caravan recommended.

#### 3e. Direct construction — the second verb, shipped

**VFE Classical carries it** [V, `2787850474/1.6/Assemblies/VFEC.dll`, re-read; the on-disk source
is 1.3/1.4 only]:

| Piece | What it is |
|---|---|
| `VFEC.RoadBuildingDef` | A `Def` with `road` (`RoadDef`), `workRequired` (`int`), `iconPath`. Three ship in `1.6/Defs/Misc.xml`. **Pure XML — we author our own tiers.** |
| `WorldComponent_RoadBuilding.AddRoadGizmos` | `Caravan.GetGizmos` postfix. Yields nothing unless `VFEC_DefOf.VFEC_RoadBuilding.IsFinished`, the caravan is not `pather.MovingNow`, and it has no job running; then one `Command_Action` per def, opening `Find.WorldTargeter.BeginTargeting` restricted to `WorldGrid.IsNeighbor`. The target callback adds a `WorkInfo` to `WorkInfos`. |
| `WorldComponent_RoadBuilding.PostTick` | `Caravan.TickInterval` postfix on `Gen.IsHashIntervalTick(caravan, 250)`: adds one work per free, alive, non-downed, non-mental colonist; **moving or leaving the tile cancels the job**; on completion `OverlayRoad`, `SetAllLayersDirty()`, `pather.StartPath` to the target tile, and a message. |
| `ExposeData` | `Scribe_Collections.Look(ref WorkInfos, "workInfos", LookMode.Reference, LookMode.Deep, …)`. |
| `AddToString` | `Caravan.GetInspectString` postfix: tier, percent, work done/total. |

**Multiplayer Compatibility syncs it** [V]. `Multiplayer.Compat.VanillaFactionsClassical` registers
`RegisterLambdaDelegate(typeof(WorldComponent_RoadBuilding), "AddRoadGizmos", [1])` — the targeter
callback that writes the `WorkInfo` — and postfixes that lambda with `StopTargeter` so the local
targeter closes on every client. The class is compiled into
`1629973374/1.6/Referenced/Multiplayer_Compat_Referenced.dll`, and **that assembly is loaded**:
`Multiplayer.Compat.MpCompatLoader.LoadConditional` reads it with Mono.Cecil, removes every type
whose `MpCompatFor` mod is not running, and `AppDomain.CurrentDomain.Load`s the rest [V].

**It needs no integration with §3.** A player-paved edge at or above a project's tier is skipped
at planning (§3b step 6) and refused by `OverlayRoad` at write time. Two costs of taking it as
shipped, neither blocking: it paves **one edge per order** (adjacent tile only), and every finished
edge calls `SetAllLayersDirty()`. **Build B**, if
[#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) declines VFE Classical, reimplements it
in ~70 lines and one `[SyncMethod]`, and uses the narrow redraw.

#### 3f. State

```
WorldComponent_RoadNetwork : WorldComponent
    TechLevel lastPlannedEra
    int nextProjectId
    List<RouteProject> projects         // Building, Paused, and the Complete record
    List<PendingPair> planQueue         // Settlement refs + tier; drains one per tick
```

**The roads themselves are engine state** in `SurfaceTile.potentialRoads`. The component holds only
what the engine cannot: which projects exist, how far each has got, and who built what. **A
`Complete` project is the attribution record** the superseded ledger was for, so there is one store,
not two.

**Capture, do not degrade — unchanged.** A road's value follows the settlements at its ends, and
`OverlayRoad` cannot remove or downgrade a link (**T-43**). *Capturing a corridor is capturing the
settlements on it*; the completed record is what lets a letter say whose road was taken.

#### 3g. Display

- **The growing road itself.** `WorldDrawLayer_Roads.Regenerate` draws each tier from its
  `worldRenderSteps` [V]; a half-built route is visibly half a road.
- **One letter per era plan** naming the number of routes and linking their endpoints; a message,
  not a letter, per completed project.
- **`Settlement.GetInspectString` postfix** [V target] on each endpoint:
  *"Stone road to Ashvale (Kingdom of Ruen): 12 / 30 segments, about 9 days."*
- **The funding gizmo's tooltip** carries the price and the days saved.
- **Vanilla's tile inspect** already names the highest-priority road on a tile [V].

### 4. Vehicles — the second half of the mobility ladder

**Established by [#69](https://github.com/cjd721/Rimworld-Archinity/issues/69). Evidence class
READ**, from `Vehicles.dll` / `SmashTools.dll` (`3014915404/1.6/Assemblies/`),
`VanillaVehiclesExpanded.dll` (`3014906877/1.6/Assemblies/`) and `Multiplayer_Compat.dll` /
`Multiplayer_Compat_Referenced.dll` (`1629973374/1.6/`). Vehicle Framework has no `Mods/`
duplicate, so **T-22** does not bite; VVE's on-disk source is 1.4 only (⚠ in
`MOD-SNAPSHOT.md`) and the 1.6 assembly is what was read.

#### 4a. Put vehicle pathing back on the synced tick — three Harmony prefixes

**Mechanism.** Three prefixes in `Archinity.Core`, one file, all the same shape: *when
`MP.IsInMultiplayer`, do the work synchronously and return `false`.*

| # | Target | Today | With the prefix |
|---|---|---|---|
| **P1** | `Vehicles.VehiclePathingSystem.InitThread` | creates the `DedicatedThread` | returns `false` ⇒ `dedicatedThread` stays `null` ⇒ `ThreadAvailable` is false at **all** of its readers, so every enqueue site takes the synchronous branch VF already ships |
| **P2** | `Vehicles.VehiclePathFollower.RequestNewPath` | `TaskManager.Run(AsyncPathFindAction.Invoke, token)` — `Task.Run` on the .NET thread pool | runs the same `AsyncPathFindAction` inline with `CancellationToken.None` |
| **P3** | `Vehicles.WorldVehiclePathGrid.RecalculateAllPathCostsAsync` | `TaskManager.Run(…)` — thread pool | invokes the private `RecalculateAllPerceivedPathCosts(CancellationToken.None)` inline |

**P1 is what the settings flag was supposed to buy. P2 and P3 are the load-bearing half**, and
neither the flag nor the compat layer reaches them — see *Available mechanisms*.

**State.** None of ours. All three prefixes redirect control flow and write nothing. The only
state involved is VF's own, and VF already populates all of it on its synchronous branch.

**Persistence.** Nothing to scribe, deliberately. `VehiclePathingSystem.ExposeData` calls
`InitThread()` on load when `dedicatedThread == null` [V]; P1 intercepts that like any other
call, so a save taken with the prefixes active is byte-identical to one taken without. **The
gate is `MP.IsInMultiplayer`, evaluated live and never written down**, so a save that predates
the prefixes loads normally and single-player keeps its threads. No migration, no freeze item.

**Change.** Nothing increments. Each prefix fires from a hook that already exists:
`Map.FinalizeInit` and `MapComponent.ExposeData` for P1,
`VehiclePawn.BaseTickOptimized → VehiclePathFollower.PatherTick → TryEnterNextPathCell` for P2,
`WorldVehiclePathGrid.WorldComponentTick` for P3 — all on the synced tick or inside a synced
load [V] (`docs/engine/determinism.md` § *What is on the synced tick*). That is the whole
point: the work moves onto a tick both clients execute in the same order.

**Display.** Nothing new — this is a correctness patch. What the player gets is VF's own
existing signal: with no thread, `InitThread` logs *"Loading map without DedicatedThread. This
will cause performance issues. Map={map}."* once per map [V]. **That line is the observable
confirmation the harness is live**, and it is why the check in *Verification* is a one-client
log read rather than a two-client soak. The real cost to the player is frame time on large
maps with many vehicle defs; VF's author says so in that same warning.

**Both gates pass.** *Divergence*: the prefixes read `MP.IsInMultiplayer` and nothing else —
no `ModSettings`, no viewport, no `Find.CurrentMap`, no unkeyed cache. They **remove** three
divergence sources and add none. *Loudness*: a Harmony prefix on a renamed target throws at
startup, and VF's no-thread warning is a positive confirmation in the log.

> **One behavioural side effect, and it is symmetric.**
> `VehiclePathingSystem.MapComponentTick` gates `deferredGridGeneration.DoIncrementalPass()` on
> `ThreadAlive` [V], so with P1 the daily pass that prunes grids for vehicle defs unused for
> three days never runs. That is a memory cost, not a divergence — `ThreadAlive` is false on
> **both** clients identically — and grids are still generated lazily by `RequestGridsFor` on
> vehicle spawn.

#### 4b. The ladder itself — XML

**The rungs already ship as data** [V]. World travel time is
`VehicleCaravanTicksPerMoveUtility.GetTicksPerMove`, which takes
`vehiclePawn.GetStatValue(VehicleStatDefOf.MoveSpeed) * WorldSpeedMultiplier / 60f` per vehicle
and converts to ticks. So the per-vehicle rung values are `vehicleStats/MoveSpeed`,
`properties/worldSpeedMultiplier` and — for air vehicles — `vehicleStats/FlightSpeed`, every
one a `PatchOperationReplace`. The **numbers** belong to the balance deferral in
[map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2), with
§1's road ladder; the *shape* is settled.

**The one re-gate the ladder needs is two operations.** As shipped, `VVE_Frog` and `VVE_Toad`
— both `<vehicleType>Air</vehicleType>` — are gated on `VVE_BasicVehicles`, the same research
that unlocks the first ground vehicle [V]. **VVE's own gating collapses the two rungs
INDUSTRIAL.md asks for into one.** Move their `researchPrerequisites` to `VVE_AerialVehicles`
and the ladder is restored.

#### 4c. The interaction with §1 — the road-cost override, and the fix that closes it

This is the item §1 handed to #69 by name. **The fix below is selected**, re-derived against
`3014915404/1.6/Assemblies/Vehicles.dll` and `3014906877/1.6/` rather than inherited.

##### What the assembly does

- **The override rule in full, and there are two overloads, not one.**
  `Vehicles.RoadCostHelper.GetRoadMovementDifficultyMultiplier` takes a `RoadDef` in **both**
  a `(List<VehicleDef>, RoadDef)` and a `(List<VehiclePawn>, RoadDef)` form — identical
  bodies, and the `VehiclePawn` one is what a live caravan reaches [V]. Each takes
  `roadDef.movementCostMultiplier` as a base and lets
  `VehicleDef.properties.customRoadCosts[roadDef]` **replace** it [V] — **not "lower
  winning"**, which an earlier draft of §1 asserted and which is withdrawn there rather than
  merely contradicted here. The loop is
  `if (customRoadCosts.TryGetValue(roadDef, out value) && (!flag || value < num))`: `!flag`
  short-circuits the comparison on the first declaring vehicle, so the **first declaring
  vehicle replaces the `RoadDef` base unconditionally, in either direction**, and "lower wins"
  applies only *among* declaring vehicles. A vehicle can make itself **slower** than the ladder
  says, not only faster.
- **Fourteen of VVE's twenty-three vehicles declare `customRoadCosts` with
  `AssignDefaults="…"`** — one flat number applied to *every* road def, ranging 0.25 to 0.85
  [V] (`3014906877/1.6/Defs/VehicleDefs/`; Tier1 BangBus, Bunsen, Highwayman, Mule, Roadkill,
  Scytheman, Traveller; Tier2 Bulldog, Charley, Roadrunner, Snatcher, Tango, Wagon, Wisent).
  `VehicleProperties.PostDefDatabase` calls
  `XmlHelper.FillDefaults_Def<RoadDef, float>`, which `TryAdd`s the value for every def in
  `DefDatabase<RoadDef>` [V]. **So for those fourteen vehicles a dirt path and an ancient
  asphalt highway are the same speed, and §1's five-step ladder is invisible.** The Traveller
  reads 0.25 on every tier — better than §1's proposed *highway* value, on a dirt track.
- **There is a second dial, and §1 does not name it.** Off-road, `RoadCostHelper` returns
  `MaxRoadMultiplier(vehicles, VehicleOffRoadMultiplier)` — per-vehicle
  `properties.offRoadMultiplier`, further offset by the `OffRoadMultiplier` upgrade stat [V].
  **The clamp is not where an earlier statement put it.** Only the
  `VehicleOffRoadMultiplier(VehiclePawn)` overload clamps **0.01–10**; the **`VehicleDef` path is
  unclamped**, and `MaxRoadMultiplier` clamps its own result **0.01–100** [V]. A `VehicleDef`
  value outside 0.01–10 therefore survives into the caravan maths. Note the asymmetry too:
  **on-road takes the min across the *declaring* vehicles (a non-declaring vehicle contributes
  nothing to that min), off-road takes the max across all of them (the slowest governs)** [V].
  Three VVE vehicles declare it (0.8, 0.8, 1.2); the rest inherit the base.

##### The build — five XML operations, not fourteen

VF ships `Vehicles.CustomCostDefModExtension { List<VehicleDef> vehicles; float cost; }`, hung
on the **cost def** — here the `RoadDef` — and applied by
`Vehicles.PathingHelper.LoadDefModExtensionCosts<RoadDef>` (the `float` overload) with a
**direct assignment** (`dictFromVehicle(vehicleDef)[roadDef] = cost`), not `TryAdd` [V].
**An empty or null `vehicles` list means every `VehicleDef`** — the method falls back to
`DefDatabase<VehicleDef>.AllDefsListForReading` [V]. That is what makes five operations sound:
without it the fix would be per-vehicle and would not cover a vehicle a later mod adds.

**The ordering is right, and it is the load-bearing fact.**
`Vehicles.VehicleHarmony`'s `[StaticConstructorOnStartup]` constructor runs
`PostDefDatabaseCalls` — which performs the `AssignDefaults` `TryAdd` fill — **before**
`ApplyAllDefModExtensions`, which is where `LoadDefModExtensionCosts<RoadDef>` is called from
[V]. The extension therefore overwrites the `AssignDefaults` fill rather than losing to it,
and `TryAdd`-versus-indexer is what decides it. Both run once per launch, before any save
loads.

**The indexer write cannot NRE, and that is load-bearing rather than incidental.**
`LoadDefModExtensionCosts` writes `dictFromVehicle(vehicleDef)[roadDef] = cost` into
**every** `VehicleDef` in the database, including the nine VVE vehicles and every modded
vehicle that declares no `customRoadCosts` at all.
`Vehicles.VehicleProperties.ResolveReferences(VehicleDef)` news up
`customRoadCosts = new SimpleDictionary<RoadDef, float>()` whenever the field is null [V],
during def loading and therefore long before `VehicleHarmony`'s static constructor runs. A
non-declaring vehicle presents an empty dictionary, not a null one, so the write lands. Were
that not so, A would throw on the first non-declaring vehicle in the database and take VF's
whole startup with it.

**Five operations cover the entire corpus, not merely vanilla.** `rg -l '<RoadDef[ >]' -g '*.xml'`
over both corpus roots returns **zero** [V]; the only file in the game that declares a `RoadDef`
is `Core/Defs/RoadDefs/RoadDefs.xml`, and the pattern would also have caught one added inside a
`PatchOperationAdd` `<value>`. So the five tiers are not a subset we are choosing to cover — they
are the complete `RoadDef` vocabulary on disk, and A is exhaustive over it by construction rather
than by luck. The `vehicles`-empty fallback extends that completeness forward over *vehicles*; this
sweep is what closes it over *roads*.

One extension per `RoadDef`, `vehicles` left empty to mean *all*, restores §1's ladder for
every vehicle in the set **and for any vehicle a later mod adds**:

```xml
<!-- expect: 1 -->
<Operation Class="PatchOperationAddModExtension">
  <xpath>/Defs/RoadDef[defName="DirtPath"]</xpath>
  <value>
    <li Class="Vehicles.CustomCostDefModExtension">
      <cost>0.75</cost>
    </li>
  </value>
</Operation>
```

…and four more, one per tier, tracking §1's table — **~50 lines** with the `<?xml?>`/`<Patch>`
wrapper. **The `<cost>` values are [I] and are §1's numbers, not new ones** — they exist to make
the vehicle see the same ladder a caravan on foot sees, and the balance deferral owns both.
**They must be set in the same sitting as §1's `movementCostMultiplier` values and §4b's
per-vehicle rungs**, because after this fix the two tables are required to hold the same numbers
and a drift between them is invisible in play.

> **Whoever sets those numbers must know that §1's proposal *as written* is a large road-speed
> nerf, and A is what delivers it.** §1 proposes `DirtPath` **0.75**. The fourteen declaring
> vehicles read their own flat number on that tier today, so adopting §1 verbatim makes
> **seven of them 3× slower on a dirt path** (BangBus, Highwayman, Traveller, Charley,
> Roadrunner, Snatcher, Wagon — all `0.25` → `0.75`), Mule 2.5×, Roadkill/Bulldog/Tango
> 1.9×, Bunsen/Wisent 1.5×, and the Scytheman alone slightly **faster** (`0.85` → `0.75`)
> [V, from VVE's declared values]. On `AncientAsphaltHighway` §1 proposes `0.25` and those
> same vehicles already read 0.25, so the top rung is **unchanged**. The whole effect of
> A + §1 as proposed is therefore to *compress vehicles down onto the low rungs*, not to
> speed them up anywhere. That may well be what the campaign wants — it is what makes paving
> matter — but it is a balance decision with a 3× magnitude and it must be taken knowingly,
> not inherited from a table that reads like a refinement.

**Use `PatchOperationAddModExtension`, not a raw `PatchOperationAdd` of a `<modExtensions>`
block.** `Verse.PatchOperationAddModExtension` creates `<modExtensions>` when the def has none
and appends into it when it does [V]; a bare `PatchOperationAdd` appends a **second sibling**
`<modExtensions>` element if anything else patched one in first, and
`DirectXmlToObject.ObjectFromXmlReflection` then assigns the field twice, last block winning.
That failure is **loud** — it logs `"XML … defines the same field twice: modExtensions"` [V] —
so it is fragility rather than a trap, but it costs the same line count to avoid. No vanilla
`RoadDef` carries `<modExtensions>` today [V], and **nothing in either corpus root hangs a
`Vehicles.CustomCostDefModExtension` on a `RoadDef`** — VVE is the only third party that uses
the extension at all and hangs it on two `ThingDef`s (`VVE_TankTrap` and, by patch, vanilla
`AncientTankTrap`, both `cost 10000`) **[I]**, a corpus sweep rather than a read.

##### The alternatives, and what separates them

| | Build | Kind | Preserves VVE's per-vehicle road dial? | Covers a vehicle a later mod adds? |
|---|---|---|---|---|
| **A** | **This one** — `CustomCostDefModExtension` × 5 `RoadDef`s, empty `vehicles` | XML, 5 ops | **no** — every vehicle reads exactly the tier | **yes** |
| B | Harmony postfix on both `RoadCostHelper.GetRoadMovementDifficultyMultiplier(…, RoadDef)` overloads, recomputing `movementCostMultiplier × (declared ÷ 0.5)` | C#, ~25 lines | yes | yes |
| C | Strip the 14 `<customRoadCosts AssignDefaults="…"/>` nodes so every vehicle falls through to the base | XML, 14 ops | no | **no** |
| D | Replace each of the 14 `AssignDefaults` attributes with an explicit five-entry dictionary | XML, 14 ops × 5 values | yes | **no** |

**A is recommended.** What separates it from B and D — the two that keep the vehicle dial — is
that **the campaign has not asked for one.** The mobility ladder INDUSTRIAL.md describes is
per *era*, not per vehicle-on-road, and per-vehicle speed differentiation survives A untouched:
it lives in `vehicleStats/MoveSpeed` and `properties/worldSpeedMultiplier`, which
`VehicleCaravanTicksPerMoveUtility.GetTicksPerMove` folds into `ticksPerMove` **before** the
road multiplier is applied in `Vehicles.VehicleCaravan_PathFollower.CostToMove` [V]. A flattens
the *road-tier response*, which is the thing we want uniform, and leaves the *vehicle* response,
which is §4b's, alone. B's cost is not its 25 lines but its hidden constant: `0.5` is VVE's
authoring baseline and appears nowhere in any def, so B silently mis-scales if VVE ever
re-authors. **If balance later wants road quality to matter differently per vehicle, B is the
upgrade path and A is not in its way** — B would postfix over whatever the table holds.

**C is strictly dominated by A** — same behavioural outcome, nine more operations, no coverage
of future vehicles, and one latent silent failure (below). **D is the only XML build that keeps
both dials** and is the fallback if balance rules that it wants them; it costs ~170 lines and
14 defName couplings.

##### The six, for A

| | |
|---|---|
| **Mechanism** | Five `PatchOperationAddModExtension`s hanging `Vehicles.CustomCostDefModExtension` on the five vanilla `RoadDef`s, `vehicles` empty. No C#, no Harmony, no def of ours. |
| **State** | None of ours. The value lands in VF's own `VehicleDef.properties.customRoadCosts`, rebuilt from defs at every launch. |
| **Persistence** | Nothing scribed, and nothing to migrate. `customRoadCosts` is populated in `VehicleHarmony`'s static constructor before any save loads, so a save taken before or after the patch is byte-identical and reads the current table on load. |
| **Change** | Nothing at runtime. Written once per launch by `ApplyAllDefModExtensions`; never mutated afterwards [V]. |
| **Display** | Already there. `RoadCostHelper` writes `"{road.LabelCap}: {multiplier.ToStringPercent()}"` into the caravan tile-cost explanation [V] — the same tooltip line a foot caravan gets, on the vehicle code path. Without A it reads the same percentage on all five tiers. |
| **Cost** | **XML, 5 operations, ~50 lines**, in `Patches/Roads_VehicleCosts.xml`. |

##### Multiplayer

**A introduces nothing unsynced, and it does not touch T-74.** The patch is def data, merged
identically on both clients from identical files and read at
`[StaticConstructorOnStartup]`-time; there is no `Rand`, no tick, no `SyncMethod` and nothing
written at runtime. **`customRoadCosts` is *not* read through `SettingsCache`** [V] — unlike
`offRoadMultiplier` and `worldSpeedMultiplier`, both of which are — so A's values cannot be
diverged by one player's `config/ModSettings/` and A **narrows** the T-18 surface §4b widens.

**A's data does not reach the thread-pool path at all**, and the reason is the one
*The removal alternative* establishes below. `Vehicles.World.WorldVehiclePathGrid`'s async
chain — `RecalculateAllPathCostsAsync` → `TaskManager.Run` →
`RecalculateAllPerceivedPathCosts` → `RecalculateAllPerceivedPathCostsFor` →
`CalculatedMovementDifficultyAt` — is the one place off the synced tick that touches
`customRoadCosts`, and it touches it **only** through `PassableRoad`, which is reached only
under `defaultImpassable & DefaultImpassable.Roads`. **No vehicle in the corpus sets that
flag** [V], so the read never executes. Even if one did, what A writes is immutable read-only
def data identical on both clients, so the strongest available statement is also the true one:
**A puts nothing new on the unsynced path, and contributes nothing to the divergence that path
already has.** That divergence is **T-74**, it is §4a's to fix, and the #69 finding behind it —
`TaskManager.Run` landing on `Verse.Rand`'s unlocked global state via
`VehicleRegionCostCalculator` — is on the **map** pathfind, which A touches no part of.

##### The removal alternative, and why the stated reason for rejecting it was wrong

> **An earlier draft of this section said:** *"a vehicle with no entry for a road gets **no road
> benefit on the world map at all**. Override the values; never remove the keys."* **The
> conclusion holds; that reason does not.**
>
> `PassableRoad` — `vehicleDef.properties.customRoadCosts.ContainsKey(roadLink.road)` — is a
> local function inside
> `Vehicles.World.WorldVehiclePathGrid.CalculatedMovementDifficultyAt`, and it is reached
> **only** under `(vehicleDef.properties.defaultImpassable & DefaultImpassable.Roads) != 0`
> [V]. **No vehicle in Vehicle Framework or VVE sets `Roads`** — there are exactly three
> `defaultImpassable` declarations between the two mods: VF's `BaseSeaVehicle` declares
> `Terrain` and `Biomes`, and VVE's `VVE_Smuggler` and `VVE_Warbird` declare **`Biomes` only**
> [V] — so the key-presence requirement does not bite today at all. Where it *does* fire, the
> consequence is also stronger than "no benefit": the tile
> returns **`1000f`, impassable**, not a lost multiplier. Absent a `Roads` flag, a vehicle with
> an empty `customRoadCosts` simply falls through to `roadDef.movementCostMultiplier` — which
> is §1's ladder, exactly.
>
> So build C *works* on today's roster. It is rejected for the reasons in the table above —
> nine more operations, no coverage of a future vehicle, and 14 defName couplings — plus this:
> it arms a silent failure. The day any vehicle ships `<defaultImpassable><li>Roads</li>`, C
> makes every road tile impassable for it with no message. A cannot do that, because A
> guarantees a key on every road for every vehicle.

> **The `expect: 1` annotations above are UNRUN**, for the same reason §2's are:
> [#102](https://github.com/cjd721/Rimworld-Archinity/issues/102) must land before
> `tools/patch_check.py` can measure a leading-`Defs/` xpath.
>
> **One shared-instrument caveat.** `LoadDefModExtensionCosts` reads the extension with
> `Def.GetModExtension<CustomCostDefModExtension>()`, which returns the **first** match and
> leaves a second inert — **T-06**. Only one `CustomCostDefModExtension` per `RoadDef` is ever
> read, whoever authored it, which is also why builds B and D exist: per-vehicle-group costs
> **cannot** be expressed as several extensions on one road def.

### Cost

| Piece | Kind | Estimate | Lands in |
|---|---|---|---|
| Tier speed ladder | XML, 5 `PatchOperationReplace` | ~25 lines | `Patches/Roads_Speed.xml` |
| Worldgen suppression | XML, 2 PatchOperations | ~12 lines | `Patches/Roads_Worldgen.xml` |
| `neverConnectToRoads` on isolated factions | XML, 1 field per faction | ~3 lines each | the faction's own def |
| **§3** `RoadEraExtension` — `era`, `fundingCosts` | C# ~15 + XML, 5 `PatchOperationAddModExtension` | ~15 C# + ~40 XML | `Archinity.Core`; `Patches/Roads_Era.xml` |
| **§3** `WorldComponent_RoadNetwork` + `RouteProject` — state, scribing, the era poll | new C# | ~110 lines | `Archinity.Core` |
| **§3** Planner — civilizations, alliance filter, neighbor rule, `FindPath`, pending-edge count, spread queue | new C# | ~110 lines | `Archinity.Core` |
| **§3** Construction clock — edge writes, narrow redraw, invalidation, supersession, completion | new C# | ~80 lines | `Archinity.Core` |
| **§3** Funding — `Caravan.GetGizmos` postfix, amount window, `SyncedFund` / `SyncedExtend` | new C#, **1 Harmony postfix, 2 `SyncMethod`s** | ~100 lines | `Archinity.Core` |
| **§3** Display — `Settlement.GetInspectString` postfix, era letter, completion message | new C#, **1 Harmony postfix** | ~40 lines | `Archinity.Core` |
| Direct-construction tiers | XML, `VFEC.RoadBuildingDef` ×N + 1–3 `ResearchProjectDef` | ~60 lines | `Defs/RoadBuildingDefs.xml` |
| Direct-construction mechanism | **none** — VFE Classical ships it, MP Compat syncs it | 0 | — |
| — *if VFE Classical is declined by [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)* | new C# | ~70 lines + 1 `SyncMethod` | `Archinity.Core` |
| `ReachRungExtension` rows for [`CHARTING.md`](CHARTING.md) §4 | **offered, not selected** — [#118](https://github.com/cjd721/Rimworld-Archinity/issues/118) | ~8 lines each if taken | `Defs/RoadBuildingDefs.xml` |
| **§4a** P1 `InitThread` prefix | new C# | ~8 lines | `Archinity.Core` |
| **§4a** P2 `RequestNewPath` prefix (private `vehicle` field ⇒ `AccessTools.FieldRefAccess`) | new C# | ~20 lines | `Archinity.Core` |
| **§4a** P3 `RecalculateAllPathCostsAsync` prefix (sync entry is `private` ⇒ `AccessTools.Method`) | new C# | ~15 lines | `Archinity.Core` |
| **§4a** `MP.IsInMultiplayer` gate and Harmony wiring | new C# | ~15 lines | `Archinity.Core` |
| **§4b** air-rung re-gate, `VVE_Frog` / `VVE_Toad` | XML, 2 `PatchOperationReplace` | ~10 lines | `Patches/Vehicles_Gating.xml` |
| **§4b** per-vehicle rung values (`MoveSpeed`, `worldSpeedMultiplier`, `FlightSpeed`) | XML, 1 op per value | ~5 lines each | `Patches/Vehicles_Ladder.xml` |
| **§4c** `CustomCostDefModExtension` on the five `RoadDef`s | XML, 5 `PatchOperationAddModExtension` | ~50 lines | `Patches/Roads_VehicleCosts.xml` |
| **§4** vehicle content, gating research, world-travel maths, MP sync of caravans and flight | **none** — VF and VVE ship it, MP Compat syncs it | 0 | — |

**§3 in one line: ~455 lines of C# in the assembly we already ship, two Harmony postfixes, two
`SyncMethod`s, ~40 lines of XML, and one new saved `WorldComponent`.** It replaces two rows of the
superseded build — the era-rite upgrade pass (~45) and the attribution ledger (~50) — and is
roughly four times their size, because the requirement now asks for a schedule, a planner, partial
progress and a funding verb that the rite never had.

#### Three road scopes — priced options, not a selection

**§3 as specified is the current build. Two narrower scopes are verified available mechanisms and
are recorded here, priced, so a later ticket can pick one without re-running this research.**
Which scope ships is a story-beat decision Conrad will take later; nothing below changes the build
above. **Every line count is [I]** — an estimate of unwritten code.

| Option | C# | Harmony | `SyncMethod` | Clauses lost | MP risk |
|---|---|---|---|---|---|
| **Minimal** | ~140 | 1 | 0 | *derived civilizations* (routes hand-authored); *"extend farther"* | lowest |
| **Middle** | ~270 | 2 | 1 | none | low |
| **As specified** | ~455 | 2 | 2 | none | low |

**Where the ~455 goes, mapped to the clause that requires it** [I estimates]:

| Piece | Lines | Required by, or comfort |
|---|---|---|
| Component + scribing + hourly era poll | 110 | required; **≈15 of it is the poll, and the poll is comfort** (3a) |
| Planner — faction enumeration, ally filter, *k*/*R* neighbours, `FindPath`, pending-edge count, spread queue | 110 | required by *every civilization… allied neighbouring* |
| Construction clock — `float workDone` / `edgesPerDay` / `fundedWork` | 80 | **≈30 required by *over time*; ≈50 is comfort** (see the integer alternative below) |
| Funding gizmo + window + 2 `SyncMethod`s | 100 | the *clause* is required; **the mechanism is ~75 dearer than it needs to be** (see the gift alternative below) |
| Display postfix + letters | 40 | comfort — **the half-built road is already the progress bar** (3g) |
| `RoadEraExtension` | 15 C# + 40 XML | required |

**Mechanism findings behind those numbers** [V unless marked]:

- **Keep `WorldPathing.FindPath`.** It is one public call, and vanilla lays its own network through
  it — `WorldGenStep_Roads.DrawLinksOnWorld` calls `layer.Pather.FindPath(a, b, null)` and overlays
  every edge of the result. A hand-rolled `GetTileNeighbors` walk is *more* code (~35 lines) and
  loses both the road-preferring edge cost and the `World.Impassable` rejection.
  `GenWorldClosest.TryFindClosestTile` and `Verse.WorldFloodFiller.FloodFill` answer *"nearest tile
  matching a predicate"*, not *"route A→B"*, so neither substitutes. **The planner's 110 lines are
  selection, not pathing** — swapping the pather saves nothing.
- **Progress: an integer `nextEdge` stepped once per day is ~30 lines and replaces the 80-line float
  clock.** What cannot be cut is *visible* progress: a pure `finishTick` — RimPacts' precedent,
  which lays the whole path at `finishTick` — is invisible for ~30 days and then instant, which
  fails *unfolds visibly over time*.
- **VFE Classical cannot be driven for NPCs, so it is not a cheaper §3.** `WorkInfos` is
  `Dictionary<Caravan, WorkInfo>`; `WorkInfo` carries no faction field; and `PostTick` accrues
  `WorkDone` by counting `p.IsFreeColonist`, where `IsColonist` requires `Faction.IsPlayer`. **A
  non-player caravan accrues zero, silently, forever.** There is no road-work `WorldObject` to hang
  NPC progress on, and `IncidentWorker_RoadWorks` is a **MoreFactionInteraction** literal inside MP
  Compat — MFI is not on disk. VFEC still covers the **player's** direct-build verb at 0 lines (3e).
- **Funding can reuse vanilla gifts for ~25 lines and no `SyncMethod` of ours.**
  `CaravanArrivalAction_OfferGifts` → `Dialog_Trade(giftsOnly)` → `TradeDeal.TryExecute` → the
  public static `FactionGiftUtility.GiveGift(List<Tradeable>, Faction, GlobalTargetInfo)`, with
  `GetGoodwillChange` already pricing the goods; Multiplayer syncs the session itself
  (`MpTradeSession.giftMode`, `[SyncMethod] TryExecute()`). **Its costs:** the player funds a
  **faction**, not a chosen route, and *extend farther* is dropped — and that clause is then the
  **only** surviving reason to own a `SyncMethod` at all (~35 lines + 1 `SyncMethod` if kept). It
  also answers requirements question 4 (funding presence) as *"physical caravan presence
  required"*, for free.
- **The hourly era poll is cuttable, ~15 lines.** `AdvanceEra()` is ours and is called once on the
  synced research path ([`ERA.md`](ERA.md)); polling only buys self-heal on a missed notification.

**Traps, per option** [V]:

- **T-42 and T-87 bite all three.** §1's five XML replaces and §4c's five operations are
  non-negotiable under every scope — without them a road *tier* is a silent no-op and upgrading a
  road changes nothing observable.
- **T-100 bites Middle and As-specified.** Both plan **zero** routes, silently, until
  [`POLITICS.md`](POLITICS.md) seeds NPC↔NPC alliances, so **keep the route-count letter as the
  detection surface** even where display is otherwise cut. **Minimal dodges it** by never reading
  the alliance graph.
- **T-43 makes every option collision-safe** — `OverlayRoad` is upgrade-only, so overlapping
  projects, player-paved edges and later-era re-plans need no coordination.
- **Prefer `SetDirty<WorldDrawLayer_Roads>` to `SetAllLayersDirty()`** under every option. VFE
  Classical and RimPacts both get this wrong.
- **Determinism:** select the funded project by `loadID` / `ID`, never by `Find.CurrentMap` or
  selection state.

**Any option that keeps a `SyncMethod` still owes the two-client Async-Time funding test**
(*Verification*). Minimal is the only scope that removes that obligation, because it has no
`SyncMethod` of ours to test.

**Two builds for direct construction, and what separates them.** *Build A* ships VFE Classical and
inherits the verb plus its multiplayer sync for nothing. *Build B* reimplements ~70 lines and
registers one `SyncMethod`. The deciding question is not technical — it is whether
[#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) wants VFE Classical for its own sake.
**Build A is recommended while VFE Classical is in the set**; B is cheap, so nothing here blocks on
the sourcing call. §3's own component is needed under either.

**§4 has no Build B, and that is the finding.** There is no alternative vehicle framework in
the corpus and no third party patching VF's asynchronous pathing (*Available mechanisms*). The
choice is *ship vehicles with §4a* or *no Industrial mobility rung at all* — because shipping
vehicles **without** §4a is not a third option: it is a live desync source on every vehicle
move order, and it fails silently until the trace names some unrelated pawn. Whether vehicles
ship is [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s call; **the price it
is choosing between changed**, from the one settings flag
[#17](https://github.com/cjd721/Rimworld-Archinity/issues/17) recorded to ~60 lines of C# in
the assembly we already ship.

## Persistence and multiplayer

- **The road network needs no `Scribe` code of ours.** `SurfaceLayer.ExposeData` →
  `DataExposeUtility.LookByteArray` on `tileRoadOrigins`, `tileRoadAdjacency` and `tileRoadDef`;
  `SurfaceLayer.SerializeRoads` writes each link once (from the lower tile id) with the def's
  `shortHash`, and `SurfaceLayer.DeserializeRoads` rebuilds both symmetric links on load [V,
  re-read]. **Every edge §3 or VFE Classical lays persists for free.**
- **`WorldComponent_RoadNetwork` scribes its own four fields.** `Scribe_Values` for
  `lastPlannedEra` and `nextProjectId`; `Scribe_Collections … LookMode.Deep` for `projects` and
  `planQueue`. Inside `RouteProject`: `Scribe_References` for `builder`, `from` and `to`,
  `Scribe_Defs` for `tier`, `Scribe_Collections … LookMode.Value` for `pathTileIds`. Tiles are
  stored as surface-layer `int` ids, not `PlanetTile` — `PlanetTile` is a `readonly struct` with a
  `FromString`, but whether `Scribe_Values` round-trips it has not been checked [I], and ints
  certainly do.
- **A save that predates the component loads cleanly.** `World.FillComponents` — called from `World.ExposeComponents` on load and
  `World.ConstructComponents` for a new world [V] — walks
  `typeof(WorldComponent).AllSubclassesNonAbstract()` and `Activator.CreateInstance(type, this)`
  for every subclass the save lacks [V, `RimWorld.Planet.World.FillComponents`], so it appears
  empty — provided it declares a `(World world)` constructor. On that first load
  `lastPlannedEra` is seeded to the **current** era *without* planning, so an old save does not
  start a retroactive construction wave. Whether it *should* is a requirement question.
- **A reference that loads null** — a settlement destroyed before the save — marks its project
  `Cancelled` on the first pass. Laid edges are unaffected.
- **Def-level suppression is not retroactive.** The byte arrays are written from the tiles that
  existed at generation, not re-derived from defs. See *the freeze*, below.

### Multiplayer — every write is on the synced tick or inside a synced method

- **The trigger is already synced.** `AdvanceEra()` runs on the synchronized research-completion
  path ([`ERA.md`](ERA.md) § *Persistence and multiplayer*). §3 reads its result in
  `WorldComponentTick`, which runs inside `TickManager.DoSingleTick()`
  ([`docs/engine/determinism.md`](../engine/determinism.md) § *What is on the synced tick and what
  is not*). Under Async Time the world is still driven through that method:
  `Multiplayer.Client.AsyncTime.AsyncWorldTimeComp.Tick` calls `Find.TickManager.DoSingleTick()` [V,
  `2606448745/1.6/AssembliesCustom/Multiplayer.dll`].
- **No `Rand` anywhere in the road path.** `WorldPathing.FindPath` and
  `WorldPathing.FloodPathsWithCost` draw none [V, whole type read]; the planner orders by `loadID`
  and `ID` and never takes an order from a hash container. Vanilla's `WorldGenStep_Roads` *does*
  draw `Rand` — to hide links and to pick the tier, under a seed push [V] — so §3 copies its
  pathing and **not** its link or tier selection. If variety is ever wanted, push a seed built from
  the project id and the era.
- **The planner's inputs are identical on both clients.** `layerMovementDifficulty` is recomputed
  by `WorldPathGrid.WorldPathGridTick`, which `World.WorldTick` calls **before**
  `WorldComponentUtility.WorldComponentTick` [V], keyed on the day of year from `TicksAbs`.
  Relations, settlements and existing roads are simulation state.
- **No cache to invalidate after a road write.** `WorldPathGrid` holds no road term — the type
  never references a road [V] — and both `WorldPathing.FindPath` and
  `Caravan_PathFollower.CostToMove` call `GetRoadMovementDifficultyMultiplier` live per edge [V].
  A road changes no tile's `World.Impassable`, so `WorldReachability`'s cache is untouched. A
  caravan already travelling keeps its old path until it re-paths; that is cosmetic. Do not add a
  cache — a per-client snapshot of derived world state is the **T-20 class** of bug.
- **Redraw is presentation.** `WorldDrawLayerBase.SetDirty` sets a flag and regeneration happens in
  the draw [V]; nothing in the simulation reads the mesh, so it may differ between clients freely.
- **The funding verbs are two `[SyncMethod]`s** from `Multiplayer.API`, which no-op without
  Multiplayer ([`ERA.md`](ERA.md) § *Persistence and multiplayer*). **Direct construction is synced
  by Multiplayer Compatibility** (§3e). Nothing here reads a `ModSettings` field (**T-18**).
- **Multiplayer's world-grid cache patches are dormant in 1.6, and a Multiplayer update is the
  re-check.** `Multiplayer.Client.WorldGridExposeDataPatch` is a prefix on `WorldGrid.ExposeData`
  that, when its static `copyFrom` is set, copies every tile's `potentialRoads` from a cached grid
  **instead of** loading the save; `WorldGridCachePatch` and `WorldRendererCachePatch` are its
  siblings. **The only writes to any of the three `copyFrom` fields are `copyFrom = null` inside
  their own prefixes** (IL `stsfld`), and no string literal names the field in either Multiplayer
  or Multiplayer Compatibility [V]. So the prefixes always fall through to vanilla and the save's
  road arrays are what load. Were a future build to re-arm them, runtime roads would reload from
  whatever grid was cached rather than from the save.
- **Vehicles add no persistent state of ours, and §4a adds none at all.** VF and VVE scribe
  their own; `VehiclePathingSystem.ExposeData` re-creates the dedicated thread on load when
  it is null, which P1 intercepts like any other call [V]. A save is byte-identical with the
  prefixes active or absent, in both directions, because the gate is `MP.IsInMultiplayer` and
  is never written down.
- **Vehicle Framework carries no `System.Random` and no `UnityEngine.Random`** [V] — zero
  constructions and zero call sites in `Vehicles.dll`, enumerated from a whole-assembly
  decompile. **T-33** and **T-51** do not bite here. Its 99 `Verse.Rand` call sites are all
  reached from the synced tick, which `CODING_STANDARDS.md` § *The two gates* rules safe.
  (`SmashTools.dll` carries one `UnityEngine.Random.ColorHSV`, already counted in
  `docs/engine/determinism.md`'s corpus census as the animation-editor colour.)
- **The world-map vehicle feature is synced for free; only the determinism underneath it is
  not.** `Multiplayer.Compat.VehicleFramework` registers vehicle caravan launch, aerial flight
  (`OrderFlyToTiles` — the MP-Compat-side method is **`SyncedOrderFlyToTiles`**, and there is
  **no bare `MoveForward`** — plus `ResumePathPostLoad`), a `LoadVehicleCargoSession`, a
  `FlyingVehicleTargetedLandingSession`, turret targeting and firing, fuel, refuelling,
  disembarking and banishment [V]. **We register nothing of our own for vehicles.**

### The freeze — this belongs to [#18](https://github.com/cjd721/Rimworld-Archinity/issues/18)

> **"No paved roads at start" is a pre-worldgen decision, not a runtime one.** Both
> suppression PatchOperations are read at world creation and never again. Applying them
> after the world exists does nothing and says nothing: the asphalt is already in
> `tileRoadOrigins`/`tileRoadAdjacency`/`tileRoadDef` and is read back from the save rather
> than re-derived from the defs. Same for `neverConnectToRoads` on any faction.
>
> **The speed ladder is the opposite and is explicitly not a freeze item.** `RoadDef` is a
> def read live at every `CostToMove`, so the multipliers can be retuned at any point in the
> campaign with no save consequence.

## Failure and recovery

- **A downgrade written through `OverlayRoad` is a silent no-op** (**T-43**). §3 relies on exactly
  that as its collision rule. Any future degradation feature must mutate `potentialRoads` on both
  endpoint tiles directly; `OverlayRoad` cannot express it.
- **A road in a biome with `allowRoads = false` is drawn but inert** (**T-44**).
  `WorldDrawLayer_Roads.Regenerate` reads `potentialRoads` directly, while `SurfaceTile.Roads` —
  the getter every gameplay reader uses — returns `null` when the biome forbids roads [V]. **§3's
  routes do cross such biomes**, because `WorldPathing.FindPath` rejects only `World.Impassable`
  tiles [V]; vanilla worldgen does the same. The player sees a stretch of road that gives no speed
  benefit, with no message. RimPacts ships a postfix on that getter to work around it.
- **Road tier is a silent no-op until §1 lands** (**T-42**), and for vehicles until §4c
  (**T-87**). Every consumer of tier — a §3 project replacing dirt with stone, VFE Classical's
  1000-work stone road, any Charting rung — reads a constant until the five
  `PatchOperationReplace`s ship.
- **No alliances, no inter-faction network — and nothing says so** (**T-100**). Vanilla creates no
  NPC↔NPC `Ally` relation (§3b step 3), so until [`POLITICS.md`](POLITICS.md)'s seed ships, each faction's
  only partner is itself. If the requirement excludes intra-faction links, an era advance plans
  **zero** routes silently. **Detection is ours**: the era letter states the route count, and the
  planner logs a warning naming the era when it plans none.
- **An unreachable pair plans nothing.** `FindPath` returns `WorldPath.NotFound`; it logs a warning
  only when its frontier empties or it passes 500,000 tiles [V]. The planner skips the pair.
- **An endpoint changes hands, or an alliance breaks, mid-build.** The project goes `Paused` or
  `Cancelled` at the next pass; the laid prefix remains as a stub road. Not a softlock.
- **Funding spent in UI code desyncs.** Both donors that sell road work do it (*Available
  mechanisms*). §3's rule: goods leave the caravan inside `SyncedFund` and nowhere else.
- **`SetAllLayersDirty()` on every finished edge** queues a `"GeneratingPlanet"` long event on the
  next world-map draw (§3c). VFE Classical does it per player-paved edge, which is tolerable at the
  rate a caravan paves; §3's clock must use the narrow form.
- **A worldgen patch matching zero nodes is silent in game, and is currently *also* silent
  under the tooling.** A `PatchOperation` that matches nothing logs nothing at runtime. The
  `<!-- expect: 1 -->` annotations exist so that `tools/patch_check.py` catches drift — but
  per [#102](https://github.com/cjd721/Rimworld-Archinity/issues/102) that check does not
  presently work for a leading-`Defs/` xpath, which both of ours are. Until #102 lands the
  annotations are documentation, not a gate.
- **Losing the component loses projects and attribution, not roads.** The network is engine state.
- **Vehicles shipped without §4a desync silently, and the compat layer's own failure message
  will not fire — T-74.** Multiplayer Compatibility's `ReplaceThreadAvailable` transpiler logs
  *"Failed to patch VehiclePathingSystem.ThreadAvailable calls for method …"* only when it
  cannot bind — and it binds fine. It simply never covers
  `VehiclePathFollower.RequestNewPath` or `WorldVehiclePathGrid.RecalculateAllPathCostsAsync`,
  because neither consults `ThreadAvailable` at all. **Everything in the log says the mod is
  handled.** `SmashTools.TaskManager.Run` is a bare `Task.Run` reached from the synced tick,
  landing on `Verse.Rand`'s unlocked global state and on the shared static
  `VehicleRegionCostCalculator.pathCostSamples` (*Available mechanisms*). Registered as
  **T-74**; the register entry is `docs/TRAPS.md`'s, not this document's.
- **`Vehicles.SectionDebug.debugUseMultithreading` cannot be set, and a plan priced against it
  is priced against nothing — T-75.** Its `Scribe_Values.Look` is inside `if (DebugProperties.Debug)`
  and `Vehicles.DebugProperties.Debug` is `internal static readonly bool = false` in the
  shipped build [V], so the field is never written to `config/ModSettings/`, never read back,
  and resets to `true` every launch. No settings UI draws it, and
  `SectionDebug.RevalidateAllMapThreads` — the only method that would act on it being false —
  is referenced from nowhere in the assembly [V]. A hand-edited settings file is discarded on
  load without a message. Registered as **T-75**; the register entry is `docs/TRAPS.md`'s.
- **§4c failing is silent and looks like §1 failing.** If the `CustomCostDefModExtension`
  blocks do not land, vehicles keep VVE's flat `AssignDefaults` value and road *tier* carries
  no information to them — indistinguishable in play from **T-42**, and it survives §1
  landing correctly.
- **Vehicle field overrides are client-local and reach world-travel cost.**
  `SettingsCache.TryGetValue` reads `VehicleMod.settings.vehicles.fieldSettings` — per-def
  field overrides stored in `ModSettings` — at **33 call sites**, including
  `VehicleDefOffRoadMultiplier` [V], and `VehicleMod.settings.main.modifiableSettings`
  defaults to `true` with a settings checkbox [V]. MP Compat syncs exactly one VF settings
  field (`showAllCargoItems`) [V], so the rest are a **T-18** surface: two players with
  different `config/ModSettings/` get different caravan speeds. The mitigation is T-18's —
  copy the file, never re-click it — not code.
- **No campaign softlock exists here.** Roads are a speed modifier and a piece of scenery, and
  a vehicle that cannot path is a vehicle that stands still. The worst outcome of every
  failure above except the desync ones is a slower or uglier world map; the desync ones cost
  a rollback, which is why §4a is not optional if vehicles ship.

## Status

**Evidence class: READ.** Settled from `Core` defs and decompiled 1.6 assemblies
(1.6.4871 rev590). §1–§2 established by
[#68](https://github.com/cjd721/Rimworld-Archinity/issues/68) and re-verified by the adversarial
audit of 2026-09-12 (**SOLID WITH FIXES**). **§3 was re-resolved by #68's second reopen
(2026-09-15)** against `Assembly-CSharp.dll`, `VFEC.dll`, `Multiplayer_Compat.dll` and
`Multiplayer_Compat_Referenced.dll`, `Multiplayer.dll`, `RimPacts.dll` and
`FactionTerritories.dll`, with one narrow RUN item (*Verification* 8). §4 established by
[#69](https://github.com/cjd721/Rimworld-Archinity/issues/69), also **READ**, with one narrow RUN
item; §4c selected by #68's first reopen.

**A provenance note the first resolution got wrong.** #68 flagged that `docs/TRAPS.md`'s
provenance lines still read 1.6.4566. **`docs/TRAPS.md` carries no version line at all** —
the 1.6.4566 markers are in `docs/traps/world-creation.md` (ten entries) and the header of
`docs/engine/factions-and-worldgen.md` [V]. **None of them touches roads.** Re-verifying those ten
entries is [#107](https://github.com/cjd721/Rimworld-Archinity/issues/107).

**Verified available mechanisms** — not yet selected:

- The vanilla road model end to end — storage, persistence, worldgen, draw layer, inspect — and
  `WorldPathing.FindPath` as a road-preferring, `Rand`-free world pather.
- `Faction.RelationKindWith` as the alliance read, and the fact that vanilla supplies no NPC↔NPC
  alliance for it to find.
- VFE Classical's `WorldComponent_RoadBuilding` + `RoadBuildingDef`, and Multiplayer
  Compatibility's sync of it, loaded from `Referenced/`.
- VEF's `FactionDefExtension.neverConnectToRoads`.
- Vehicle Framework's whole vehicle model: `VehicleDef`, `VehiclePathFollower`,
  `VehicleCaravan`, `AerialVehicleInFlight`, `CompVehicleLauncher`, the upgrade trees, and
  `VehicleCaravanTicksPerMoveUtility` as the world-travel maths.
- VVE's 23 vehicles, four research projects and five air vehicles.
- Multiplayer Compatibility's sync of vehicle caravans, aerial flight, cargo sessions,
  targeted landing, turrets, fuel and banishment.

**Verified *and* selected** — the one item that has passed out of the list above:

- `Vehicles.CustomCostDefModExtension` as the per-`RoadDef` override lever
  ([#68](https://github.com/cjd721/Rimworld-Archinity/issues/68)'s first reopen; §4c). §1's ladder
  reaches no vehicle without it, so §4c ships whenever §1 does. **The second reopen leaves it
  untouched**: it is def data about road *speed* and is independent of who builds roads or when.

**Proposed, marked [I] by construction:** the tier ladder values; the era→tier mapping; all of
§3 — the era poll, the planner and its neighbor rule, the construction clock, the funding verbs
and caravan gizmo, the display postfixes; the three §4a prefixes; §4b's rung values and re-gate;
§4c's five `<cost>` values; and the `ReachRungExtension` rows, which are offered, not selected. The
mechanisms each composes are [V]; the claim that they compose into the wanted behaviour is [I]
until built.

**Superseded.** The era-rite build — an instantaneous re-overlay of road links within proximity
radius *N* of each climbing faction's settlements, run inside #8's synced command — and the
separate attribution ledger beside it. The requirement correction of 2026-09-13 retired the
behaviour; #68's second reopen replaced the build with §3, whose completed-project record does
the ledger's job.

**Two premises in #68's ticket were wrong and are corrected here:**
`RoadDef.worldTransitionPathCostFactor` **does not exist** — the field is
`movementCostMultiplier`; and `World.grid.roads` does not exist in 1.6 — roads live on
`SurfaceTile.potentialRoads`, reached through `WorldGrid.OverlayRoad` / `GetRoadDef`.

**One claim in #68's first resolution was wrong and is struck here:** removing the `AncientRoads`
gen step does **not** suppress `GenStep_ScatterRoadDebris`. See §2.

**Two claims corrected, one addition, by #68's second reopen:**

1. **RimPacts does not build NPC roads.** An earlier draft called it "NPC settlement road
   construction", declined because #8 rejected an incremental. It is a **player-financed** route
   from the player's colony to any non-hostile faction's settlement, bought from an inspect tab and laid all at once
   (*Available mechanisms*). Both halves of the old verdict are withdrawn: it is not an NPC
   builder, and the requirement now *asks* for the incremental.
2. **Multiplayer Compatibility's `Referenced/` assembly is loaded at runtime.** This document's
   citation of the VFE Classical sync there was right. `docs/agents/capability-research.md` once
   said `Multiplayer_Compat_Referenced.dll` "is never loaded"; it is —
   `MpCompatLoader.LoadConditional` loads it — and that file now carries the correction.

**Addition.** Faction Territories carries a vassal road-investment component (`FactionTerritories.Vassalise.VassalRoadProgressComponent`) that mirrors Roads of the Rim construction sites by reflection (`EnsureSyncedForFaction`), is funded by the UI call `TryInvestRoadPoints`, and writes no road itself (0 `OverlayRoad`/`potentialRoads` in IL); Roads of the Rim is on neither corpus root. The mod stays declined ([#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) session 2; recorded as settled on [#35](https://github.com/cjd721/Rimworld-Archinity/issues/35); [map #2](https://github.com/cjd721/Rimworld-Archinity/issues/2) *Out of scope*).

**Three claims inherited by #69 were wrong and are corrected here:**

1. **`docs/data/MOD-VERDICTS.md` § *Real*, the Vehicle Framework row** — the row
   [#17](https://github.com/cjd721/Rimworld-Archinity/issues/17) admitted VF on — is wrong in
   three places [V]. `debugUseMultithreading` is **not** a scribed bool (the `Scribe` line is
   behind `DebugProperties.Debug`, which is `false`); the `ReleaseThread()` path it names is
   `SectionDebug.RevalidateAllMapThreads`, which **nothing calls**; and *"every enqueue site
   takes its synchronous fallback"* is false, because two dispatch paths never consult
   `ThreadAvailable` at all. The row's **conclusion** — VF is admissible at the **Real** tier —
   survives; its **price** does not. Correcting that file is the orchestrator's, not this
   document's.
2. **`PARTS-BIN.md` §7's *"VVE covered, VVE-Upgrades not"*** is accurate about MP Compat's
   class list and misleading as a hazard. **VVE-Upgrades ships no assembly and no C# source at
   all** [V] — 32 XML files, 153 PNGs, and one `.txt` and one `.md`. The 32 XML resolve to **28
   defs (14 of them duplicated across the 1.5 and 1.6 load folders), 2 comp patches, `About.xml`
   and `LoadFolders.xml`** [V]. There is nothing to cover; the upgrade *mechanism* is
   Vehicle Framework's, and VF is what MP Compat covers.
3. **§1's *"lower winning"* description of `customRoadCosts`** was imprecise, and the
   imprecision hid the real problem. **§1 has been corrected in place** — the first declaring
   vehicle replaces the `RoadDef` base unconditionally, in either direction — so the document no
   longer states both sides of the claim. The full reading is §4c's.

## Available mechanisms

### Vanilla and DLC — the whole model is here

Five `RoadDef`s in `Core/Defs/RoadDefs/RoadDefs.xml` and **no others anywhere in the corpus**
[V] — `rg -l '<RoadDef[ >]' -g '*.xml'` over both corpus roots returns **zero**, and that file
is the only hit under `Data/`. This is a direct read of the def files rather than a
metadata-heap inference, and the pattern also catches a `RoadDef` declared inside a
`PatchOperationAdd` `<value>`. §4c depends on it: it is what makes five operations *exhaustive*
over the road vocabulary rather than merely a choice to cover vanilla. `DirtPath` (priority 10),
`DirtRoad` (20), `StoneRoad` (30), `AncientAsphaltRoad` (40, `ancientOnly`) and
`AncientAsphaltHighway` (50, `ancientOnly`). The five vanilla tiers are the entire vocabulary
the campaign has to work with, and that is sufficient.

`RoadDef` carries `priority`, `ancientOnly`, `movementCostMultiplier`, `tilesPerSegment`,
`pathingMode`, `roadGenSteps` (what terrain a generated map lays), `worldRenderSteps` (what
the world map draws) and `worldTransitionGroup` [V].

**Storage and the write API, re-read for §3** [V]. `SurfaceTile.potentialRoads` is a
`List<RoadLink { PlanetTile neighbor; RoadDef road; }>`, written on **both** endpoint tiles.
`WorldGrid.OverlayRoad(from, to, def)` is the only writer: null def → `Log.ErrorOnce`; same def →
return; existing `priority` ≥ new → return silently; otherwise remove both old links and add both
new ones. It marks no draw layer dirty — every caller does that itself.
`WorldGrid.GetRoadDef(from, to, visibleOnly)` reads either `Roads` (biome-gated) or
`potentialRoads`.

### Vanilla world pathing — the planner's pather

`RimWorld.Planet.WorldPathing`, one per planet layer as `PlanetLayer.Pather` [V]:

- **`FindPath(start, dest, caravan, terminator)`** — A\* over a per-layer
  `NativeArray<PathFinderNodeFast>` and `NativePriorityQueue`. Edge cost is
  `ticksPerMove × WorldPathGrid.layerMovementDifficulty[tile] × WorldGrid.GetRoadMovementDifficultyMultiplier(from, to)`,
  with 3300 standing in for a null caravan. It rejects `World.Impassable` tiles and nothing else,
  checks `WorldReachability.CanReach` first, stops at 500,000 tiles, and returns a pooled
  `WorldPath`. **No `Rand`.**
- **`FloodPathsWithCost(starts, costFunc, impassable, terminator)`** — Dijkstra with a
  caller-supplied cost. Also no `Rand`.
- **The buffers are per-layer instance state**, so the pather is single-threaded by construction;
  the tick is.
- **`WorldGenStep_Roads` is the worked example** [V]: `FloodPathsWithCost` with
  `Caravan_PathFollower.CostToMove(3300, …, perceivedStatic: true)` to prospect up to eight links
  per node, a union-find spanning tree with `Rand` hiding 10% of links and adding 1.5% extras, then
  `FindPath` per link and `OverlayRoad` along it, with the tier drawn uniformly from the
  non-`ancientOnly` defs.
- **`WorldPathGrid`** caches perceived tile difficulty per layer and refreshes it from
  `WorldPathGridTick` once per day of year, called by `World.WorldTick` [V]. It carries no road
  term.

### Faction relations — the alliance read

`Faction.RelationWith(other, allowNull)` and `RelationKindWith(other)` read one
`FactionRelation { other, baseGoodwill, kind }` [V]. `FactionRelation`'s kind moves to `Ally` at
goodwill ≥ 75 and to `Hostile` at ≤ −75 [V]. **At world creation no NPC pair can be `Ally`**:
`Faction.TryMakeInitialRelationsWith` sets goodwill from a local `GetInitialGoodwill` returning
−100, −80 or 0 [V]. [`POLITICS.md`](POLITICS.md) § *The graph is empty* adds that no vanilla goodwill
write targets an NPC↔NPC pair; its § *The build* §1 is where the edges are seeded.

### VFE Classical — direct construction, shipped and synced

Covered in §3e. The finding that matters is that it is **research-gated by construction**, so an
era gate on player road-building costs one `ResearchProjectDef` and no code. Read it at
`1.6/Assemblies/VFEC.dll` — the source on disk is 1.3/1.4 only (⚠ in `MOD-SNAPSHOT.md`).

### Multiplayer Compatibility — the VFE Classical road sync, loaded from a nonstandard path

`Multiplayer.Compat.VanillaFactionsClassical`, in
`294100/1629973374/1.6/Referenced/Multiplayer_Compat_Referenced.dll` [V]. **Not** in
`1.6/Assemblies/`, which holds only `Multiplayer_Compat.dll`. **It runs**:
`Multiplayer.Compat.MpCompatLoader.LoadConditional` finds `Referenced/Multiplayer_Compat_Referenced.dll`,
reads it with Mono.Cecil, removes every type whose `MpCompatFor` / `MpCompatRequireMod` target is
not a running mod, writes the rest to a stream and `AppDomain.CurrentDomain.Load`s it [V]. **A sweep
that excludes `Referenced/`** — as the method prescribes, to keep the stub's borrowed metadata out
of the results — **also hides these real registrations**, so confirm any MP Compat negative
against that assembly by path.

### VEF — worldgen endpoint suppression, in XML

`FactionDefExtension.neverConnectToRoads`, applied through a postfix on
`WorldGenStep_Roads`'s endpoint predicate [V]. Per-faction; does not reach the extra random
road nodes. §3b reads the same field so that a faction left off the worldgen network is also left
off the runtime one.

### The other corpus readers of the road API

Neither is a donor; both are recorded because the ladder in §1 is a global change and this
is who else sees it.

| Mod | Path | Carries | Bearing on the build |
|---|---|---|---|
| **Vehicle Framework** `smashphil.vehicleframework` | `1.6/Assemblies/` | `Vehicles.RoadCostHelper.GetRoadMovementDifficultyMultiplier` in **two** `RoadDef` overloads, `(List<VehicleDef>, …)` and `(List<VehiclePawn>, …)` — each takes `roadDef.movementCostMultiplier` as a base, **replaced** per vehicle by `VehicleDef.properties.customRoadCosts[roadDef]`, unconditionally and in either direction [V] | **Two more readers of the field, and a silent bypass of the ladder — closed by §4c**, which reads the override loop in full, finds that 14 VVE vehicles flatten all five tiers, and is **selected** |
| **Better Traders Guild** `shunter.bettertradersguild` (`3684587591`) | `1.6/Assemblies/BetterTradersGuild.dll`, present under **both** roots | One `GetRoadMovementDifficultyMultiplier` reference **[I]** — a corpus byte-scan hit, which is an inference and not a read; apparently read-only for its own caravan costing [I] — not decompiled | None. Recorded for completeness of the reader set; no verdict changes |
| **Rim War** `torann.rimwar` | `v1.6/Assemblies/` | One read-only `GetRoadMovementDifficultyMultiplier` reference; writes no roads [V] | Already barred and declined (`MOD-VERDICTS.md`); nothing here reopens it |
| **Map Mode Framework** `nozome.mapmodeframework` | `1.6/Assemblies/` | References `WorldDrawLayer_Roads` as a layer name [I] | Not a road feature |

### Vehicle Framework — the vehicle model, and the determinism gap underneath it

`smashphil.vehicleframework`, read at `3014915404/1.6/Assemblies/{Vehicles,SmashTools}.dll`.
No `Mods/` duplicate (**T-22** does not bite) and no source shipped at all, so the assembly is
the only reading.

**What it supplies** [V]: `Vehicles.VehicleDef` (a `ThingDef` subtype whose pawns are
`VehiclePawn`), `VehiclePathFollower` for map movement, `VehicleCaravan` +
`VehicleCaravan_PathFollower` + `WorldVehiclePathGrid` for world movement,
`CompVehicleLauncher` + `AerialVehicleInFlight` + `LaunchProtocol` for flight,
`CompUpgradeTree` / `UpgradeTreeDef` for upgrades, and a `Caravan.TicksPerMove` prefix
(`Patch_CaravanHandling.VehicleCaravanTicksPerMove`) routing to
`VehicleCaravanTicksPerMoveUtility`. It is the only vehicle framework in the corpus.

**Where the determinism gap is.** VF has two distinct asynchrony mechanisms and the switches
only reach one of them:

| Mechanism | Gate | Covered? |
|---|---|---|
| `SmashTools.Performance.DedicatedThread`, one per player-home map, fed by six `AsyncAction` subclasses | `VehiclePathingSystem.ThreadAvailable`, itself gated on `InitThread`'s read of `debugUseMultithreading` | **partly** — MP Compat transpiles 3 of the 8 `ThreadAvailable` sites; §4a's P1 closes the rest by never creating the thread |
| `SmashTools.TaskManager.Run` — a bare `Task.Run` on the .NET thread pool | **none** | **no** — §4a's P2 and P3 |

`TaskManager.Run` has three call sites [V]. Two are simulation:
`VehiclePathFollower.RequestNewPath` and
`WorldVehiclePathGrid.RecalculateAllPathCostsAsync`. The pathfinding task walks
`VehicleRegionCostCalculator.RegionMedianPathCost`, which calls `Rand.PushState()` /
`Rand.Seed = …` / eleven `region.RandomCell` draws / `Rand.PopState()` on `Verse.Rand`'s
**unlocked process-global state** [V] — and `TryEnterNextPathCell` opens with
`if (RequestStatus == PathRequestStatus.Calculating) return;`, so a vehicle stalls for a
scheduling-dependent number of ticks with no RNG involved at all. The world grid's
`PerceivedMovementDifficultyAt` is an unlocked array read against a grid that task rewrites
once per in-game day [V].

**A second race sits on the same path and is independent of `Verse.Rand`.**
`VehicleRegionCostCalculator.pathCostSamples` is a **`private static int[11]`** — one array
shared across every instance — filled and sorted in place by `RegionMedianPathCost`, which runs
inside that same async pathfind task [V]. Two vehicles pathing concurrently interleave writes
into the same eleven slots, so the median each reads back is scheduling-dependent even with the
RNG held perfectly still. **#69 did not carry this one.** It adds no new conclusion; it
strengthens the existing one, because the remedy for both is the same — take the work off the
thread pool (§4a's P2), not seed it.

> **Why the frame-loop region rebuild is *not* on that list.** `VehiclePathingSystem.UpdateRegions`
> runs from `MapComponentUpdate` and looks like the same bug. It is not: **vanilla rebuilds
> dirty regions from `Map.MapUpdate()` too** [V], and VF copies vanilla's safety valve —
> `VehicleRegionGrid.GetValidRegionAt(cell, rebuild: true)` calls
> `regionUpdater.TryRebuildVehicleRegions()` before returning, exactly as
> `Verse.RegionGrid.GetValidRegionAt` does [V]. Every simulation read forces the rebuild, so
> the frame-loop call is an optimisation. **It stops being one the moment the rebuild is on
> another thread**, because `VehicleRegionAndRoomUpdater.UpdatingRegion` is a plain unlocked
> instance bool and `TryRebuildVehicleRegions` returns immediately when it is set [V] — the
> tick then reads a half-rebuilt grid. §4a's P1 restores the vanilla-shaped guarantee.

**What is *not* wrong with it**, worth stating because the framing invites a broader worry:
zero `System.Random` constructions, zero `UnityEngine.Random` call sites, and 99 `Verse.Rand`
sites all reached from the synced tick [V]. `Parallel.ForEach` in
`VehiclePathingSystem.GenerateRegionsParallel` is **safe** — it blocks until every partition
completes, so the tick sees a finished result. Fan-out is not the hazard; fire-and-forget is.

### Vanilla Vehicles Expanded — the content, and the aircraft rung

`oskarpotocki.vanillavehiclesexpanded`, read at
`3014906877/1.6/Assemblies/VanillaVehiclesExpanded.dll` (⚠ the on-disk source is 1.4 only).

**23 `Vehicles.VehicleDef`s, every one `techLevel Industrial`** [V] — 17 Land, 2 Sea, 5 Air —
gated on four `ResearchProjectDef`s: `VVE_BasicVehicles` (Industrial, 1000, after
`BiofuelRefining`), and `VVE_ComplexVehicles` / `VVE_AerialVehicles` / `VVE_CombatVehicles`
(1500 each, after `VVE_BasicVehicles` + `Fabrication`).

**The aircraft rung has a carrier** [V] — `INDUSTRIAL.md` asks for helicopters and aircraft,
and five vehicles carry `<vehicleType>Air</vehicleType>`, a `CompProperties_VehicleLauncher`
and a `FlightSpeed` stat:

| defName | Category | `FlightSpeed` | Research **as shipped** |
|---|---|---|---|
| `VVE_Frog` | Transport | 50 | `VVE_BasicVehicles` ← §4b re-gates |
| `VVE_Toad` | Combat | 50 | `VVE_BasicVehicles` ← §4b re-gates |
| `VVE_Warbird` | Transport | 30 | `VVE_CombatVehicles` |
| `VVE_Smuggler` | Transport | 22 | `VVE_AerialVehicles` |
| `VVE_Mosquito` | Transport | 10.5 | `VVE_AerialVehicles` |

All five carry `<canCaravan LockSetting="True">false</canCaravan>` — they fly as
`AerialVehicleInFlight`, not as `VehicleCaravan`, and MP Compat syncs that path [V].

**The assembly is clean** [V]: no threads, no `Task.Run`, no `System.Random`, no
`UnityEngine.Random`, six `Verse.Rand` sites. `Multiplayer.Compat.VanillaVehiclesExpanded`
(in `Multiplayer_Compat.dll`, **not** the `Referenced` one) syncs its door and reload gizmos.

### Vanilla Vehicles Expanded — Upgrades — no code, therefore no multiplayer cost

`oskarpotocki.vanillavehiclesexpandedupgrades` (`3302208420`) **ships no assembly and no C#
source at all** [V]: 32 XML files, 153 PNGs, one `.txt` and one `.md`. The 32 XML are **28 defs
— 14 of them the same defs duplicated across the 1.5 and 1.6 load folders — plus 2 comp patches,
`About.xml` and `LoadFolders.xml`** [V], so the distinct def count is smaller than the file count
suggests.
The upgrade *mechanism* is Vehicle Framework's (`CompUpgradeTree`, `UpgradeNode`,
`JobDriver_UpgradeVehicle`, `WorkGiver_WorkOnUpgrade`), so its determinism question is VF's,
and VF is what MP Compat covers. **Verified available at no additional multiplayer cost.**

### Multiplayer Compatibility — VF's sync, and the exact shape of its thread patch

`Multiplayer.Compat.VehicleFramework` lives in
**`294100/1629973374/1.6/Referenced/Multiplayer_Compat_Referenced.dll`** — the same
nonstandard path the Classical compat class uses, and not `1.6/Assemblies/`, which holds only
`Multiplayer_Compat.dll`.

It carries `NoThreadInMp(VehiclePathingSystem mapping)`, returning `mapping.ThreadAvailable`
in single-player and **`false` in multiplayer** [V], and a transpiler
`ReplaceThreadAvailable` that rewrites calls to the `ThreadAvailable` getter into calls to it
— logging *"Failed to patch VehiclePathingSystem.ThreadAvailable calls for method …"* when it
cannot bind, so that half fails loudly.

**It is applied to exactly three methods** [V]: `PathingHelper.RecalculatePerceivedPathCostAt`,
`PathingHelper.ThingAffectingRegionsOrientationChanged`,
`PathingHelper.ThingAffectingRegionsStateChange`. `ThreadAvailable` has eight occurrences in
`Vehicles.dll`, one of which is the property itself; the five uncovered readers are
`VehiclePathingSystem.UpdateRegions` and the three `DeferredGridGeneration` entry points. §4a's
P1 closes all five at once and needs no transpiler.

### RimPacts — a player-financed route to a non-hostile settlement, not an NPC builder

`wowgag.rimpacts`, `3762723122/Assemblies/RimPacts.dll` — a root `Assemblies/`, which
`LoadFolders.xml` loads for 1.6 through `<li>/</li>`; no source [V].

- **Who starts it: the player.** `RimPacts.WITab_RptTrade`, a world-object inspect tab, draws a
  *build road* button whose only faction gate is
  `FactionUtility.HostileTo(faction, Faction.OfPlayer)` — no treaty is required; its `Dialog_MessageBox.CreateConfirmation`
  delegate calls `RptSilverUtility.TryConsumeSilver(cost)` and then
  `WorldComponent_RimPacts.StartRoadWork(settlement, pathTiles, nextTier, payableSegments)` [V].
  No code path starts a road for an NPC faction.
- **Where it goes.** `WorldComponent_RimPacts.RoadPathTo` paths from the player's colonies to the
  settlement with `RptRoadPather.FindPath` — a Dijkstra over a `List<HeapNode>` whose step cost is
  `PerceivedMovementDifficultyAt(to)` × 0.15 on a road already at tier and × 0.6 on a lesser one,
  bounded by `RoadMaxTiles` — falling back to vanilla `FindPath` [V].
- **How it progresses: it doesn't, visibly.** `RoadWork { settlement, pathTiles, finishTick, tier }`
  with `finishTick = now + payableSegments × 0.25 days`; `ProcessRoadWorks` overlays **the whole
  path at once** when the tick passes, calls `SetAllLayersDirty()`, and grants trust and goodwill
  [V]. Price is `RptTuning.RoadTierCostPerTile` = 80/150/250/400/600 silver per pending edge [V].
- **Multiplayer: none.** MP Compat's 1.6 assemblies carry no `rimpacts` string in either encoding
  [V], and the spend runs in a UI delegate. The assembly holds no `System.Random`, thread,
  `Task.Run` or `UnityEngine.Random` [V, whole decompile].
- **Donor value:** `WorldComponent_RimPacts.PayableSegments`, which counts only edges below tier
  (§3b step 6), the road-discounted step cost, and the cost table as balance input. Nothing to ship.

### Faction Territories and Vassalage — road investment for a mod that is not on disk

`jaeger972.factionterritories`, `3626725895/Assemblies/FactionTerritories.dll`; no source [V].

- **`FactionTerritories.Vassalise.VassalRoadProgressComponent : GameComponent`** keeps one private
  `RoadProject { factionId, roadDefName, progressPerTile, currentTileProgress, List<int> tileQueue }`
  per faction — per-tile progress over a tile queue [V].
- **It writes no road.** The whole decompile contains no `OverlayRoad` and no `potentialRoads` [V].
  Its projects mirror **Roads of the Rim**'s construction sites by reflection (`EnsureSyncedForFaction`): `EnsureRotRReflection` resolves
  `AccessTools.TypeByName("RoadConstructionSite")` and `WorldObjectComp_ConstructionSite`'s
  `GetLeft` / `GetCost` / `ReduceLeft` / `UpdateProgress`, and `RoadsOfTheRimAvailable` is false
  when they are missing [V].
- **Roads of the Rim is not in either corpus root.** `RoadConstructionSite` hits only this
  reflection literal, and no `About.xml` names the mod [I — a sweep].
- **Investment spends vassalage points from `Widgets.ButtonText`** through `TryInvestRoadPoints`,
  unsynced [V].
- **Declined outright** — *"dropped entirely — the mod and its territory sim"* on
  [#35](https://github.com/cjd721/Rimworld-Archinity/issues/35), and listed in map #2's *Out of scope*;
  `docs/data/MOD-VERDICTS.md` records Conrad declining it as a dependency in #8 session 2. **Donor value:** `RoadProject`'s tile
  queue is the same shape as §3c's `RouteProject`.

### More Faction Interaction — named, not present

MP Compat 1.6 carries the literal `MoreFactionInteraction.IncidentWorker_RoadWorks` [V], but no
assembly in either root defines `MoreFactionInteraction` — its only ASCII hits are MP Compat's
own [I — a sweep]. Not on disk, not assessed.

### What does not exist anywhere, and where it shaped the build

- **NPC road growth over time.** The corpus has exactly two runtime road writers: `OverlayRoad`
  appears as a member reference only in VFE Classical and RimPacts, both player-initiated, and
  `potentialRoads` only in RimPacts (its draw patch, `Patch_IceRoadOverlay`) and Multiplayer (the
  dormant cache copy). Neither name appears as a string literal anywhere, so nothing reaches them
  by reflection [I — a sweep; the three assemblies were read]. **This negative is why §3 is a
  build**; its nearest donors are vanilla's worldgen road step for the pathing and Faction
  Territories' tile queue for the progress.
- **Road ownership, contest or capture.** No hits across both corpus roots. This is why the
  build reduces "contest a corridor" to "capture the settlements on it" and keeps only a
  completed-project record.
- **Any era or tech-level input to road tier.** `WorldGenStep_Roads` picks uniformly at
  random from the non-`ancientOnly` set; nothing in the corpus changes that. This is why
  suppression is `ancientOnly` on `StoneRoad`, and why §3 carries its own `RoadEraExtension`.
- **Any road-building designator vocabulary.** `Designator_Road`, `BuildRoad`, `PaveRoad`,
  `WorldObject_Road`, `CaravanRoad` and `RoadNetwork` return nothing; `RoadProject` and
  `RoadConstruct` hit only Faction Territories, and `RoadWork` only it and RimPacts. Road
  building is a caravan gizmo, a UI purchase, or nothing.
- **A downgrade or removal path.** Neither vanilla nor any mod removes a road link.
- **A second vehicle framework, or any third party patching VF's asynchronous pathing.**
  `VehiclePathFollower`, `RequestNewPath`, `RecalculateAllPathCostsAsync`,
  `WorldVehiclePathGrid` and `DedicatedThread` resolve to Vehicle Framework and Vanilla
  Vehicles Expanded only, ASCII and UTF-16LE, across both roots **[I]** — a corpus sweep, not a
  read. **This is why §4 has no Build B.** `debugUseMultithreading` appears in no assembly but
  `Vehicles.dll` **[I]**, same basis — nothing externally sets it, and nothing could.
- **Any competition for the world-speed lever.** `CaravanTicksPerMove` has two corpus readers,
  Vehicle Framework and RimPacts **[I]** (sweep), so VF's `Caravan.TicksPerMove` prefix fights
  nobody.
- **A pre-Industrial vehicle anywhere in the corpus.** Every one of VVE's 23 vehicles is
  `techLevel Industrial`, the Wagon and the Wisent included [V]; that no *other* mod ships one
  is a sweep result and **[I]**. **The mobility ladder below
  Industrial is roads and feet**, which is what §1–§3 supply and what the plot asks for; there
  is no Medieval cart rung to build on, and inventing one is not this document's.

## Verification

**The second reopen's pass (2026-09-15), which §3's negatives rest on.**
`rg -a -g '*.dll' -g '!**/obj/**' -g '!**/Referenced/**' -i` over both corpus roots, each symbol
run twice — ASCII, and null-interleaved with the `\x00` escapes typed literally into the pattern,
never through `$(…)`. `python tools/corpus.py --check` → *Corpus matches the snapshot. 155 mods.*

| Symbol | ASCII (`#Strings`) | Null-interleaved (`#US`) |
|---|---|---|
| `OverlayRoad` | VFE Classical, RimPacts | 0 |
| `potentialRoads` | RimPacts, Multiplayer | 0 |
| `RoadLink` | RimPacts, Vehicle Framework, Multiplayer; VEF and KCSG (map-generation readers of `Roads`); Medieval Overhaul at `3219596926/1.5` only, not 1.6 | — |
| `RoadWork` | RimPacts, Faction Territories | RimPacts; MP Compat (`MoreFactionInteraction.IncidentWorker_RoadWorks`) |
| `RoadProject` | Faction Territories | Faction Territories |
| `RoadConstruct` / `RoadConstructionSite` | Faction Territories / Faction Territories (field `type_RoadConstructionSite`) | — / Faction Territories |
| `RoadBuild` | VFE Classical | RimPacts |
| `RoadsOfTheRim` | Faction Territories, Vehicle Framework | Vehicle Framework |
| `MoreFactionInteraction` | MP Compat | — |
| `BuildRoad`, `PaveRoad`, `RoadNetwork` | 0 | — |

**Validated against a same-heap positive before any negative was believed.** The `OverlayRoad`
ASCII result is a member-reference name in `#Strings`; its control, `OverlayRoad` over
`2787850474`, returns all four `VFEC.dll` copies [V]. The null-interleaved zeros' control is
`IncidentWorker_RoadWorks`, a string literal, which returns
`1629973374/1.6/Assemblies/Multiplayer_Compat.dll` [V]. A separate literal sweep for `copyFrom` over
`2606448745/1.6` and `1629973374/1.6` backs the dormant-cache finding. `OverlayRoad` over
`1629973374` with `Referenced/` included also returns nothing.

**A tooling hazard met on the way, stated narrowly.** Three single-mod hits — `RoadProject` and
`RoadConstruct` in ASCII, `RoadBuild` null-interleaved — came back blank when piped through
`corpus.py --which -` and a row filter, and the same `rg` found them when run raw;
`corpus.py --which` also answered *"No mod owns that path"* for Faction Territories' dll given in
`/c/…` form. The cause was not isolated. **Every entry in the table above is raw `rg` output.**

**Read, not swept:** `WorldGrid.OverlayRoad` / `GetRoadDef` /
`GetRoadMovementDifficultyMultiplier`, `SurfaceTile`, `SurfaceLayer`'s road serialisation,
`WorldPathing`, `WorldPathPool`, `WorldPathGrid`, `WorldGenStep_Roads`, `WorldRenderer`,
`WorldDrawLayerBase`, `World.WorldTick` / `FillComponents` / `ExposeComponents` / `ConstructComponents`, `Faction`'s relation
members and `FactionRelation`; `VFEC.WorldComponent_RoadBuilding` and `RoadBuildingDef`;
`Multiplayer.Compat.MpCompatLoader` and `VanillaFactionsClassical`; `RimPacts.dll` and
`FactionTerritories.dll` decompiled whole and read at their road members; `Multiplayer.dll`
decompiled whole, with its IL searched for every write to the three grid-cache `copyFrom` fields.

**How the survey was run — and the correction the audit forced.** `rg -a -g '*.dll'
-g '!**/obj/**'` over both corpus roots — `steamapps/workshop/content/294100` (145 mods) and
`steamapps/common/RimWorld/Mods` (83) — attributed with `python tools/corpus.py --which -`.
Symbols: `RoadDef`, `WorldGenStep_Roads`, `WorldDrawLayer_Roads`, `OverlayRoad`,
`potentialRoads`, `GetRoadDef`, `RoadWorldLayerDef`, `GetRoadMovementDifficultyMultiplier`,
`tileRoadOrigins`, plus the builder vocabulary and the five road defNames.

> **The wide half of that sweep used a technique now known to be broken, and the stated
> validation could not have caught it.**
> [#103](https://github.com/cjd721/Rimworld-Archinity/issues/103). The original pass ran the
> pattern set a second time with `rg -a --encoding utf-16le`, and validated it against an
> **ASCII** positive in `Assembly-CSharp.dll` — a control that exercises none of the UTF-16
> path. `rg -a --encoding utf-16le "AddRoadGizmos"` returns **no match** on
> `1629973374/1.6/Referenced/Multiplayer_Compat_Referenced.dll` while the string is provably
> present as UTF-16LE in that file, and the same command *does* find it in the 1.3 and 1.4
> copies of the same assembly [V]. `--no-mmap` does not help.
> `rg -a "A\x00d\x00d\x00R\x00o\x00a\x00d\x00"` finds it [V]. Every UTF-16LE negative
> asserted by #68 was originally produced by the broken form.
>
> **The conclusions survive; the stated evidence did not.** The auditor re-ran this
> document's negatives — no mod-authored `<RoadDef>`, no road ownership/contest/capture
> vocabulary, no road-building designator vocabulary, no downgrade or removal path — by
> null-interleaved byte scan, and **they hold** **[I]** — a sweep negative is an inference
> however carefully the sweep is built. What is retracted is the claim that the
> sweep was validated before its negatives were trusted. Any future re-run of this survey
> must use the null-interleaved form.
>
> **One of those four has since been upgraded to [V].** "No mod-authored `<RoadDef>`" was
> re-run by #68's reopen as a direct XML read — `rg -l '<RoadDef[ >]' -g '*.xml'` over both
> roots, zero hits — which is a read of the def files rather than a byte scan of assemblies.
> See *Vanilla and DLC*, above. The other three remain [I].

**§4's pass ran the same way and validated its UTF-16 half before trusting a negative.**
Symbols: `VehiclePawn`, `VehiclePathFollower`, `RequestNewPath`,
`RecalculateAllPathCostsAsync`, `WorldVehiclePathGrid`, `DedicatedThread`,
`debugUseMultithreading`, `CaravanTicksPerMove`, `CompProperties_VehicleLauncher`,
`customRoadCosts`. Control: `AddRoadGizmos` returns **8** files ASCII and **16**
null-interleaved UTF-16LE [V] — the form
[#103](https://github.com/cjd721/Rimworld-Archinity/issues/103) prescribes, exercised on a
known positive before any negative above was believed.

`corpus.py --check` reported the corpus matching the snapshot at 155 mods at the start and
the end of both passes [V].

**Field-reader claims are exhaustive, not sampled — within `Assembly-CSharp`.**
`Assembly-CSharp.dll` was decompiled whole (`ilspycmd -o`) and every reader of `ancientOnly`
(1), `movementCostMultiplier` (2), `allowRoads` (2) and `OverlayRoad` (2 callers) was
enumerated in the decompiled source [V]. Mod assemblies were **not** decompiled wholesale for
§1–§3; Vehicle Framework's third read of `movementCostMultiplier` is the reason that
distinction now appears in §1.

**`Vehicles.dll` *was* decompiled whole for §4**, and its counts are enumerated rather than
sampled [V]: `ThreadAvailable` 8, `ThreadAlive` 8, `dedicatedThread` 32, `TaskManager.Run` 3,
`Parallel.ForEach` 2, `debugUseMultithreading` 5 (four in `SectionDebug`, one in
`InitThread`), `Verse.Rand` 99, `System.Random` 0, `UnityEngine.Random` 0.

**`tools/defdb.py` was used nowhere in §4 and no verdict rests on it**
([#102](https://github.com/cjd721/Rimworld-Archinity/issues/102)).

**What still needs a check** — none of it blocking:

1. **The two worldgen PatchOperations have never been dry-run** [I]. Their target nodes are
   confirmed to exist, but `expect: 1` is asserted, not measured, and
   [#102](https://github.com/cjd721/Rimworld-Archinity/issues/102) must land before
   `tools/patch_check.py` can measure a leading-`Defs/` xpath at all.
2. After the two worldgen PatchOperations, generate a world and confirm the map carries
   dirt paths and dirt tracks only. Observable on the world map with no dev mode. Confirm
   separately whether 1–2 map-wide ancient wrecks per map are acceptable (§2).
3. After the speed ladder, send one caravan across a `DirtPath` edge and one across a
   `StoneRoad` edge and confirm the tile-cost tooltip's road line differs. The tooltip
   already prints `{road.LabelCap}: {multiplier.ToStringPercent()}` [V], so this needs no
   instrumentation.
4. **§4a's RUN item is a single one-client log check.**
   Launch one client, load a map with at least one `VehicleDef` in the database, and confirm
   the log contains *"Loading map without DedicatedThread. This will cause performance
   issues."* once per map. That string is emitted by `InitThread` on **exactly the branch P1
   forces** [V], so its presence proves the prefix bound and no thread was created; its
   absence means P1 missed — the prefix did not apply, or `MP.IsInMultiplayer` read false —
   and that is the only outcome reading cannot distinguish. **No two-client soak is required**:
   the determinism argument is settled by reading, and a soak would only re-observe it.
5. After §4c, hover a **vehicle** caravan on a `DirtPath` edge and a `StoneRoad` edge and
   confirm the road line differs. Same tooltip, different code path —
   `RoadCostHelper.GetRoadMovementDifficultyMultiplier` writes its own explanation line [V].
   Without §4c the two read identical for 14 of VVE's 23 vehicles, which is the bug.
6. After §4b's re-gate, confirm `VVE_Frog` and `VVE_Toad` are unbuildable until
   `VVE_AerialVehicles` finishes.
7. **§3 — the era plan.** In dev mode, finish the capstone project. Within one in-game hour one
   letter names *N* routes, and `WorldComponent_RoadNetwork` holds *N* `Building` projects. With no
   alliance seed, every project's two endpoints share a faction.
8. **§3's RUN item — two clients, narrow.** Host and client in a Multiplayer session with Async
   Time on. Advance the era on the host, let three in-game days pass, then fund one project **from
   the client's** caravan. Observe: no desync, and the same laid edges on both world maps along the
   routes the letter names. Reading cannot settle two things this observes — that `Caravan`
   serialises as a `[SyncMethod]` argument, and that nothing the planner reads is client-local.
9. **§3 — partial progress and redraw.** After about five days an endpoint's inspect string shows
   laid segments and those edges are drawn; edges landing while the world map is open do not
   bring up the *"GeneratingPlanet"* loading screen.
10. **§3 — persistence.** Save mid-build and reload: each project's `nextEdge` and the drawn edges
    are unchanged, and no second era letter fires.
11. **§3 — collision.** With VFE Classical, pave an edge on a project's path at a tier at or above
    the project's. The project skips it, and the edge keeps the player's tier.

## Outstanding decisions

- **The numbers are a requirement, not a mechanism, and they have an owner.** §1's five
  multipliers, the era→tier mapping, §3's `buildDays` (about thirty), whether that means a
  per-route duration or a per-edge speed, the neighbor count *k* and radius *R*, the funding prices
  and cap, §4b's per-vehicle `MoveSpeed` / `worldSpeedMultiplier` / `FlightSpeed` values and §4c's
  five `<cost>` values are all starting proposals. They belong to
  **the balance deferral in [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2)**.
  **The road ladder and the vehicle ladder must be set in one sitting**, because they multiply and
  `customRoadCosts` overrides the road ladder outright (§4c).
- **Requirements gaps, handed back to
  [`docs/requirements/WORLD-INFRASTRUCTURE.md`](../requirements/WORLD-INFRASTRUCTURE.md).** No open
  ticket owns that document, so these are reported as gaps rather than assigned. Each is a
  one-branch switch in §3; none blocks the build.
  1. Does *"between its own settlements and the settlements of allied neighboring factions"*
     include own-settlement ↔ own-settlement routes, or only routes to allies?
  2. Is a player colony an eligible partner for an NPC civilization allied to the player?
  3. What may *"extend them farther"* target — another settlement, the player's colony, any tile?
  4. Which resources fund a route, and must the player be physically present (caravan) or may
     they fund remotely (comms console)?
  5. When an alliance breaks or an endpoint changes hands mid-build, does the project pause or
     cancel?
  6. Does loading a save that predates the feature start construction for the current era, or wait
     for the next advance?
- **§3 depends on [`POLITICS.md`](POLITICS.md)'s alliance seed.** Until § *The build* §1 ships,
  vanilla supplies no NPC↔NPC alliance and §3 plans intra-faction routes only. POLITICS owns the
  seed; this is a build-order dependency, not an ownership gap.
- **"Protect" is unanswered.** `docs/plot/INDUSTRIAL.md` § *Roads and Mobility* asks that
  the player be able to *"finance, **protect**, capture and benefit from"* infrastructure.
  This document answers finance (§3d, §3e), capture (the settlements at a route's ends) and
  benefit (the speed ladder). **Protect has no mechanism and no design here** — nothing in the
  corpus models a road as a thing that can be threatened, and `OverlayRoad` cannot express
  damage. It sits on the map's fog as *Protecting infrastructure*.
- **Road debris on a roadless map is an open lever with no owner.** Suppressing
  `AncientRoads` leaves 1–2 ancient vehicle wrecks per map and spreads them map-wide (§2).
  Removing them means reaching the `GenStep_ScatterRoadDebris` entry in the map generator's
  step list, which has not been investigated. **A gap, not a hand-off** — no ticket owns it.
- **Whether completed mobility feeds Charting's reach is
  [#118](https://github.com/cjd721/Rimworld-Archinity/issues/118)'s.**
  [`docs/requirements/CHARTING.md`](../requirements/CHARTING.md) now says outright that Charting
  never creates, upgrades or pays for a road and that a mobility rung is a later cross-spec choice.
  The rung shapes at the end of this document are kept as input to that pass and are not selected.
- **Whether routes can degrade.** The build says capture, not degrade. If requirements
  later ask for a contested route physically decaying, it is ~15 lines of direct
  `potentialRoads` mutation and it cannot go through `OverlayRoad` (T-43).
- **Build A versus Build B** for direct construction waits on
  [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s call on VFE Classical.
- **Whether vehicles ship at all is
  [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s, and the price it is
  choosing between has changed.**
  [#17](https://github.com/cjd721/Rimworld-Archinity/issues/17) admitted Vehicle Framework at
  the **Real** tier for *one settings flag*. That flag does not exist at runtime, and the true
  price is §4a's ~60 lines of C#. The verdict is unchanged — VF carries the Industrial
  mobility rung and nothing else in the corpus does — but **there is no cheap configuration
  option here, and §4a is not optional if vehicles ship.**
- **Two traps, now allocated: T-74 and T-75.** **T-74** is VF's thread-pool pathfinding that
  neither its own switch nor MP Compat's `NoThreadInMp` reaches — `SmashTools.TaskManager.Run`
  as a bare `Task.Run` off the synced tick, onto `Verse.Rand`'s unlocked global state and the
  shared static `VehicleRegionCostCalculator.pathCostSamples`. **T-75** is
  `Vehicles.SectionDebug.debugUseMultithreading` being unsettable. **The register bodies are
  `docs/TRAPS.md` / `docs/traps/`'s and this document does not write them.** An engine
  entry is proposed alongside them, for `docs/engine/determinism.md` § *Why threads are the
  one thing that bars a mod*: **the bar's question should widen from *"does it create
  threads"* to *"does any simulation path leave the tick"***, because a `Task.Run` creates no
  named thread and is invisible to a thread-creation sweep. This document edits neither file.
- **Vehicle settings overrides are a standing T-18 surface with no owner.** VF's
  `SettingsCache` reads per-def field overrides from client-local `ModSettings` at 33 call
  sites, `modifiableSettings` defaults on, and MP Compat syncs one VF settings field [V]. The
  mitigation is procedural (copy `config/ModSettings/`, never re-click) and belongs to the
  same place T-18 does; **nothing here makes it worse and nothing here fixes it.**
- **Outposts already handles vehicles arriving at an outpost.** `VEF`'s `Outposts.dll` carries
  `VehiclePawnType` and `VehicleRemoveAllPawns` [V]. Noted for whoever takes Charting's
  outpost tenure work — its discovery hook is `Outposts.Outpost.Produce()`. **#57 is closed
  and no ticket currently owns this**; not investigated further here.

### Charting reach rungs — offered, not selected

> **Not selected — 2026-09-15.** Requirements make roads world infrastructure and Charting, at
> most, a later *reader* of completed mobility
> ([`docs/requirements/CHARTING.md`](../requirements/CHARTING.md), *Road construction is not a
> Charting decision*). Nothing below builds, prices or times a road, and nothing in §3 reads it.
> Whether any of these rungs ships — and whether a completed-route rung (the optional worker
> below) should replace the research-gated rows — is cross-spec integration,
> [#118](https://github.com/cjd721/Rimworld-Archinity/issues/118). The shape conforms to
> [`CHARTING.md`](CHARTING.md) §4 and is kept so that pass need not re-derive it.

**The reach band's interface is fixed by [`CHARTING.md`](CHARTING.md) §4 — *The reach band*,
§ *The rung registry*.** That section, not a ticket, is the contract this document conforms to.
**#57, which established it, is closed**, so where the text below says "#57 wants" or "#57 may",
read it as *whoever picks Charting's reach work up* — there is no open ticket to hand the choice
to. This document conforms to §4 rather than proposing an alternative. An
earlier draft published `static float RoadReachFactor(PlanetTile)` and explicitly refused a
band or tier enum. **That is withdrawn.** Nothing in Charting consumes a float, and the band
is an element-wise max over integer rungs.

The published form is therefore the one CHARTING §4 defines:

```
Archinity.ReachRungExtension : DefModExtension
    int  minTiles;      // usually 0 or 1
    int  maxTiles;      // what this rung reaches
    Type workerClass;   // optional; the escape hatch
```

hung on a def by `<modExtensions>`, with satisfaction read off the def's own type and the
band the element-wise max over satisfied rungs. **The band's code does not change.**

**Roads carry their rungs on the research that unlocks each tier, so the whole publication
is XML.** CHARTING §4 already reads a `ResearchProjectDef` rung as satisfied when
`IsFinished`, and VFE Classical already gates player road-building on a `ResearchProjectDef`
(§3) — so the rung and the build gate are the same def and no `workerClass` is needed.

Proposed rows — **the integers are [I] and belong to
the balance deferral in [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2)**, not to this document; the
*shape* is the contract:

| Tier the rung represents | Def carrying `<modExtensions>` | Satisfied when | `minTiles` | `maxTiles` |
|---|---|---|---|---|
| `DirtPath` / `DirtRoad` | the Neolithic road-building `ResearchProjectDef` | `IsFinished` | 0 | 12 |
| `StoneRoad` | the Medieval road `ResearchProjectDef` | `IsFinished` | 0 | 18 |
| `AncientAsphaltRoad` | the Industrial paving `ResearchProjectDef` | `IsFinished` | 0 | 26 |
| `AncientAsphaltHighway` | the Industrial capstone `ResearchProjectDef` | `IsFinished` | 0 | 34 |

**Vehicles publish their rungs the same way, and for free.** `docs/requirements/CHARTING.md`
§ *Reach* asks that *"you reach Industrial, you get vehicles, the reachable world explodes
outward"*, and VVE already gates every vehicle on a `ResearchProjectDef` — which CHARTING §4
already reads as satisfied when `IsFinished`. So the vehicle rungs are `<modExtensions>`
blocks on VVE's own research defs, no `workerClass`, no code:

| Rung | Def carrying `<modExtensions>` | Satisfied when | `minTiles` | `maxTiles` |
|---|---|---|---|---|
| ground vehicles | `VVE_BasicVehicles` | `IsFinished` | 0 | 40 |
| long-range ground | `VVE_ComplexVehicles` | `IsFinished` | 0 | 55 |
| aircraft | `VVE_AerialVehicles` | `IsFinished` | 0 | 90 |

**The integers are [I] and belong to the balance deferral**, as the road rows' do. Two things
about the shape are not balance and are stated here deliberately:

- **The ground rung and the aircraft rung must not be the same rung**, and as shipped they
  effectively are — `VVE_Frog` and `VVE_Toad` fly on `VVE_BasicVehicles` [V]. §4b's re-gate is
  what makes the two rows above distinguishable in play, so **the rungs depend on §4b landing**
  the way the graded road rungs depend on §1.
- **The element-wise max does the right thing without an interaction term.** A colony with
  `VVE_AerialVehicles` and only dirt paths takes the aircraft rung's 90 over the road rung's
  12; a colony with highways and no vehicles takes 34. **Both are pre-clamp figures and a
  reader must not take them as delivered reach.** [`CHARTING.md`](CHARTING.md) §4 makes the
  band *"the element-wise max over satisfied rungs, **clamped above by
  `CompProperties_ChartingApparatus.maxAcceptedBand`**"*, so what either colony actually gets
  is `Mathf.Min(90, maxAcceptedBand)` and `Mathf.Min(34, maxAcceptedBand)` — **whichever
  apparatus is standing decides, and a colony with 90 rungs' worth of vehicles and a low-tier
  apparatus reaches exactly what that apparatus allows.** The rung integers in the two tables
  above are therefore ceilings this document *offers*, not distances it *delivers*. That is
  CHARTING § *Reach*'s *"two knobs with no interaction term"* working as designed — the era
  knob is the rung, the apparatus knob is `maxAcceptedBand` — and it is why neither ladder
  needs to know the other exists at the band level, even though at the *travel time* level
  §4c makes them multiply.

**An optional fifth rung, if #57 wants roads that exist rather than roads that can be
built.** A research rung says the player *may* pave; it does not say a road is actually
there. If #57 wants the stronger signal, one `workerClass` supplies it —
`Archinity.ReachRungWorker_RoadFromColony`, satisfied when an edge leaving any player
colony tile carries a road of at least the named tier, read live via
`WorldGrid.GetRoadDef(from, to, visibleOnly: true)`. ~15 lines, no state.

- **Roads register nothing and push nothing.** The rungs are data on defs; #57's band code
  scans for them. Roads do not know the band exists, and adding a tier is one
  `<modExtensions>` block.
- **Read live, never stored.** If the optional worker ships, it must recompute per call.
  `CostToMove` recomputes the underlying multiplier per edge per call and there is no cache
  anywhere in the road system. A stale per-client snapshot feeding placement is the **T-20
  class** of bug exactly.
- **The continuous primitive stays public if #57 ever wants it.**
  `WorldGrid.GetRoadMovementDifficultyMultiplier(from, to)` is public, is per *edge* not per
  tile, and is the same number `Caravan_PathFollower.CostToMove` multiplies tile difficulty
  by. This document does not publish a wrapper around it; #57 may call it directly.
- **What §1 does and does not gate.** *Tier* carries no information today: all five defs
  return `0.5f`, so no ladder means no ordering between the four rungs above (**T-42**), and
  the five-step rung ladder is the part that depends on §1 landing. **Road *presence* is
  already a real signal** — `GetRoadMovementDifficultyMultiplier` returns `0.5` on any road
  edge and `1f` off-road [V], a genuine 2× difference that exists in the shipped game.
  **#57 should keep a road/no-road term regardless of whether the ladder ships.** Only the
  graded five-step version waits on §1.
- **Vehicle *presence* is a far larger signal than road tier, and it is real today.** Vehicle
  caravan speed is `MoveSpeed × worldSpeedMultiplier` per vehicle, converted by
  `VehicleCaravanTicksPerMoveUtility` [V], and VVE's fastest ground vehicle is several times a
  walking caravan. No patch is needed for that difference to exist. **It is the signal
  `docs/requirements/CHARTING.md` § *Reach* is actually describing** — *"you reach Industrial,
  you get vehicles, the reachable world explodes outward"* — which is why the vehicle rungs
  are worth more to the band than the road rungs are. Only the **ground vs air** distinction
  waits on §4b, and only the *travel-time* effect of road tier on vehicles waits on §4c.
