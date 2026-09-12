# World infrastructure

## Purpose and scope

How the world's road network satisfies
[`docs/plot/INDUSTRIAL.md`](../plot/INDUSTRIAL.md) § *Roads and Mobility* — *"the vanilla
map should not begin covered in modern paved roads… Neolithic travel uses paths and dirt
tracks; Medieval powers begin maintaining routes; Industrial civilization paves and expands
them"* — and [`docs/plot/MEDIEVAL.md`](../plot/MEDIEVAL.md)'s *"roads become political
infrastructure."*

It also satisfies [`docs/plot/INDUSTRIAL.md`](../plot/INDUSTRIAL.md) § *Roads and Mobility* —
*"the progression is not merely movement speed. It is the size of the political world the
player can practically participate in"* — and
[`docs/requirements/CHARTING.md`](../requirements/CHARTING.md) § *Reach*'s *"you reach
Industrial, you get vehicles, the reachable world explodes outward."*

This document owns the **world-map mobility ladder**: the road network — what exists at
worldgen, what changes it during play, who is recorded as having built it — and **vehicles**
([#69](https://github.com/cjd721/Rimworld-Archinity/issues/69)), the second half of that
ladder. The two are one system because they multiply: a vehicle's `customRoadCosts` table
overrides the road tier outright (§4), so neither can be tuned without the other.

It does not own **Charting's reach band** ([`CHARTING.md`](CHARTING.md) **§4 — *The reach
band*** owns that outright; #57, the ticket that established it, is **closed**, so §4 is the
standing contract and there is no open ticket to hand a reach question to) — this document
supplies rungs in the form that section defines and nothing more. It does not own
**settlement ownership**, which is
[#8](https://github.com/cjd721/Rimworld-Archinity/issues/8)'s era rite; roads ride that
command rather than owning one.

One thing the plot asks for is **not** answered here and is not deferred to a design that
exists: *"finance, **protect**, capture and benefit from"* infrastructure. Finance, capture
and benefit are below. **Protect is a gap** — see *Outstanding decisions*, handed to
the balance deferral in [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2).

## The build

**Both halves are shipped systems that need repair rather than construction, and the repairs
are opposite in kind.** Roads are pure XML — a broken dial and a missing clock (§1–§3).
Vehicles are the reverse: the content, the gating and the world-travel maths all ship and
work, and what is missing is **determinism under Multiplayer**, which costs three Harmony
prefixes and about sixty lines of C# that nobody else is going to write (§4).

**Roads are a shipped engine system with a broken dial and a missing clock.** Vanilla
already carries five road tiers, per-edge storage, free persistence, a world-map draw layer
and three inspect surfaces. VFE Classical already carries the whole player-financed
build-a-road feature, and Multiplayer Compatibility already syncs it. What is missing is
(a) a speed difference between tiers, (b) suppression of asphalt at worldgen, and (c) a
clock that advances road quality as the world climbs. All three are cheap, and the first is
the one everything else depends on.

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

**The "no blast radius" claim is scoped to `Assembly-CSharp`, and there is a third reader
in the corpus.** Vehicle Framework's
`Vehicles.RoadCostHelper.GetRoadMovementDifficultyMultiplier(List<VehicleDef>, RoadDef)`
takes `roadDef.movementCostMultiplier` as a **base** and lets
`VehicleDef.properties.customRoadCosts[roadDef]` **replace** it [V]. The replacement is
**unconditional and works in either direction**: the loop is
`if (customRoadCosts.TryGetValue(roadDef, out value) && (!flag || value < num))`, so the *first*
declaring vehicle overwrites the `RoadDef` base whatever its value, and "lower wins" applies only
*among* declaring vehicles. A declaring vehicle can therefore be **slower** than the ladder says,
not only faster. §4c carries the full reading and the fix; this section states it once and does
not restate it as a caveat. A vehicle that declares `customRoadCosts` **bypasses the ladder
silently** — the ladder still lands for caravans on foot and for every vehicle that declares
nothing, but VF's per-vehicle table is a second, independent dial over the same tiers, and
whoever sets the vehicle ladder must set it against this table and not only against `RoadDef`.

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

### 3. Advance the network on the era rite — reuse, do not invent

**State.** None for the roads themselves. Road links live in
`SurfaceTile.potentialRoads` as `List<RoadLink> { PlanetTile neighbor; RoadDef road; }`,
written symmetrically on both endpoint tiles [V].

**Persistence — free, and this is the best fact in the ticket.** `SurfaceLayer` serialises
roads into three parallel byte arrays every save: `tileRoadOrigins` (int tile id),
`tileRoadAdjacency` (byte neighbour index) and `tileRoadDef` (`RoadDef.shortHash`), built by
`SerializeRoads()` from `potentialRoads` and rebuilt by `DeserializeRoads()` on load [V].
**A road written at runtime persists with no `Scribe` code of ours**, and a save that
predates any of this reads its existing roads back normally.

**Change — the era rite, and nothing else.**
[#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) settled that the world ages in
one visible movement rather than by increments — Conrad: *"I don't need a tiny incremental…
you wave the magic wand"* — and the same synced command that swaps `Faction.def` and
`SetFaction`s settlements upgrades that faction's routes.

The mechanism is one call:

```csharp
Find.WorldGrid.OverlayRoad(fromTile, toTile, tierForEra);
```

**`OverlayRoad` only ever upgrades**: it early-returns when the existing road's `priority`
is greater than or equal to the new one [V]. That is a defect for any other purpose
(**T-43**) and is exactly the behaviour wanted here — the rite can be re-run, run out of
order, or run over a route the player already paved, and it will never downgrade anything.

**Do not path new routes. Upgrade the ones already on the grid.** Re-overlay existing links
at the era's tier, reading each with `WorldGrid.GetRoadDef(from, to, visibleOnly: false)`.
This consumes **no `Rand` at all** — the same property that makes #8's minimal command safe.
The fiction is better too: the Church does not invent roads, it paves the tracks that were
already there.

> **Which links are "that faction's"? Nothing in the engine says.** [V] A road is not
> attributed to anyone: `SurfaceTile.RoadLink` is `{ PlanetTile neighbor; RoadDef road; }`
> and the save arrays carry origin, adjacency and def only. The
> `WorldComponent_RoadNetwork` ledger below records **only routes built at runtime**, so on
> the first era rite every worldgen road is unattributed and *"that faction's routes"* has
> no referent at all. The rite must therefore carry an explicit **selection rule**, and
> this document states one rather than leaving it implied:
>
> **Selection rule [I] — proximity, not ownership.** For the climbing faction, take every
> road link both of whose endpoint tiles lie within **N** tiles of one of that faction's
> `Settlement`s (`Find.WorldObjects.Settlements.Where(s => s.Faction == f)`, then a bounded
> breadth-first walk of `WorldGrid` neighbours out to N, collecting `potentialRoads` on the
> tiles reached). Plus, unconditionally, every route the ledger already attributes to that
> faction. `N` is a tuning value and belongs to
> the balance deferral in [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2) with the ladder numbers.
>
> **The rejected alternative, and why it is rejected.** Re-pathing between each pair of that
> faction's settlements and upgrading the resulting corridor is the intuitive rule and is
> the *wrong* one here: it reintroduces exactly the `layer.Pather` cost this section claims
> to avoid — a path search inside the synced command, reasoning about a cost function — and
> it can pave a corridor no road ever occupied, which contradicts "upgrade what exists".
> The proximity walk touches only links already on the grid and runs once per rite.

The tier per era is the one already differentiated in §1 — Neolithic `DirtPath`/`DirtRoad`,
Medieval `StoneRoad`, Industrial `AncientAsphaltRoad`, and `AncientAsphaltHighway` reserved
for the Industrial capstone so that the map's final state is visibly different from its
Medieval one.

**Multiplayer.** Nothing is covered for free. `Multiplayer.dll` carries exactly one road
reference (`potentialRoads`) and registers no `SyncMethod` for `OverlayRoad` or any road
mutation [V]. We register our own, the same shape #8 registered for the era rite — and
because the road upgrade sits *inside* that command, it costs no second registration.

**A player-financed route: take the shipped one.** VFE Classical ships the entire feature
[V]:

| Piece | What it is |
|---|---|
| `VFEC.RoadBuildingDef` | A `Def` with `road` (a `RoadDef`), `workRequired` (int) and `iconPath`. Three ship: `BuildPath`/`DirtPath`/50, `BuildDirtRoad`/`DirtRoad`/200, `BuildStoneRoad`/`StoneRoad`/1000. **Pure XML — we author our own tiers.** |
| `WorldComponent_RoadBuilding.AddRoadGizmos` | A `Caravan.GetGizmos` postfix, one `Command_Action` per def, gated on `VFEC_DefOf.VFEC_RoadBuilding.IsFinished` — **a `ResearchProjectDef`, so the era gate is already a research gate.** Targets via `Find.WorldTargeter.BeginTargeting` restricted to `WorldGrid.IsNeighbor`. |
| `WorldComponent_RoadBuilding.PostTick` | A `Caravan.TickInterval` postfix on `IsHashIntervalTick(250)`, accumulating one work point per free, alive, non-downed, non-mental colonist; on completion calls `OverlayRoad`, `SetAllLayersDirty()`, messages the player and walks the caravan onto the new road. |
| `ExposeData` | `Scribe_Collections.Look<Caravan, WorkInfo>(ref WorkInfos, "workInfos", Reference, Deep)` on the `WorldComponent`. |
| `AddToString` | A `Caravan.GetInspectString` postfix showing tier and percent complete. |

And **Multiplayer Compatibility already syncs it** [V] — the type is
`Multiplayer.Compat.VanillaFactionsClassical`, and it lives at
**`294100/1629973374/1.6/Referenced/Multiplayer_Compat_Referenced.dll`**, *not* under the
method's usual `<mod>/1.6/Assemblies/` convention. MP Compat's layout is genuinely
nonstandard — `1.6/Assemblies/` holds only `Multiplayer_Compat.dll`, alongside
`AssembliesCustom/` and `1.6/Lunar/Components/` — and a reader following the convention
finds nothing. It registers the `AddRoadGizmos` lambda at index 1 — the `WorldTargeter`
callback that writes the `WorkInfo` — as the synced call, and postfixes it with
`StopTargeter` so the local targeter closes on every client. **The targeting UI is
client-local; the commit is the synced write.** That is the correct shape and it is the
shape ours copies if we write our own.

**Contest and capture: capture, do not degrade.** `MEDIEVAL.md` asks that powers *"contest
trade corridors."* Nothing in the corpus models road ownership, and `OverlayRoad` cannot
remove or downgrade a road at all — passing `null` logs *"Attempted to remove road with
overlayRoad; not supported"*, and a lower-priority def returns **silently** [V]. So
degradation is not free. It is also not needed: a road's value follows the settlements at
its ends, and #8's rite already transfers those by `SetFaction`. **Capturing a corridor is
capturing the settlements on it**, which the campaign already does, and the ledger below is
what lets the letter say whose road you just took.

**The ledger — the only new state.** One `WorldComponent_RoadNetwork` in `Archinity.Core`
holding `Dictionary<long, RouteRecord>` keyed on the ordered tile pair, with
`Faction builder` and `int builtTick`. It records *who paid*, nothing else; the road itself
is engine state. **It records only runtime construction** — worldgen roads enter the world
unattributed and stay that way unless a rite or a caravan touches them, which is why §3's
era rite needs the proximity rule above rather than a ledger query. A save predating the
component gets an empty ledger and degrades to "the roads exist and nobody is recorded as
having built them", which is correct rather than broken.

**Display — already there, three times over** [V]:

- `WorldDrawLayer_Roads` draws each tier from its `worldRenderSteps` and
  `worldTransitionGroup`, so a stone road looks like a stone road with no work from us.
- `WITab_Terrain.ListGeometricDetails` prints `"Road".Translate()` with the tile's road
  labels.
- The world tile inspect string names the highest-`priority` road on the tile.

What we add is the era-rite letter naming which power paved what, plus one line on the
ledger's owner where a route is politically load-bearing. Redraw after a mutation is
`Find.World.renderer.SetDirty<WorldDrawLayer_Roads>(layer)` — the narrow form; VFE Classical
uses `SetAllLayersDirty()`, which also works and is more expensive.

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

#### 4c. The interaction with §1 — vehicles currently flatten the road ladder entirely

This is the item §1 handed to #69 by name, and the finding is worse than §1 expected.

- **The override rule in full. §1 now states the same thing, and the two agree.**
  `Vehicles.RoadCostHelper.GetRoadMovementDifficultyMultiplier(List<VehicleDef>, RoadDef)`
  takes `roadDef.movementCostMultiplier` as a base and lets
  `VehicleDef.properties.customRoadCosts[roadDef]` **replace** it [V] — **not "lower
  winning"**, which an earlier draft of §1 asserted and which is withdrawn there rather than
  merely contradicted here. The loop is
  `if (customRoadCosts.TryGetValue(roadDef, out value) && (!flag || value < num))`: the
  **first declaring vehicle replaces the `RoadDef` base unconditionally, in either
  direction**, and "lower wins" applies only *among* declaring vehicles. A vehicle can make
  itself **slower** than the ladder says, not only faster.
- **Fourteen of VVE's twenty-three vehicles declare `customRoadCosts` with
  `AssignDefaults="…"`** — one flat number applied to *every* road def, ranging 0.25 to 0.85
  [V]. `VehicleProperties.PostDefDatabase` calls
  `XmlHelper.FillDefaults_Def<RoadDef, float>`, which `TryAdd`s the value for every def in
  `DefDatabase<RoadDef>`. **So for those fourteen vehicles a dirt path and an ancient asphalt
  highway are the same speed, and §1's five-step ladder is invisible.** The Traveller reads
  0.25 on every tier — better than §1's proposed *highway* value, on a dirt track.
- **There is a second dial, and §1 does not name it.** Off-road, `RoadCostHelper` returns
  `MaxRoadMultiplier(vehicles, VehicleOffRoadMultiplier)` — per-vehicle
  `properties.offRoadMultiplier`, further offset by the `OffRoadMultiplier` upgrade stat [V].
  **The clamp is not where an earlier statement put it.** Only the
  `VehicleOffRoadMultiplier(VehiclePawn)` overload clamps **0.01–10**; the **`VehicleDef` path is
  unclamped**, and `MaxRoadMultiplier` clamps its own result **0.01–100** [V]. A `VehicleDef`
  value outside 0.01–10 therefore survives into the caravan maths. Note the asymmetry too:
  **on-road takes the min across the
  caravan (the fastest vehicle governs), off-road takes the max (the slowest governs)** [V].
  Three VVE vehicles declare it (0.8, 0.8, 1.2); the rest inherit the base.

**The fix is five XML operations, not fourteen.** VF ships
`Vehicles.CustomCostDefModExtension { List<VehicleDef> vehicles; float cost; }`, hung on the
**cost def** — here the `RoadDef` — and applied by
`PathingHelper.LoadDefModExtensionCosts<RoadDef>` with a **direct assignment**
(`dictFromVehicle(vehicleDef)[roadDef] = cost`), not `TryAdd` [V]. **An empty `vehicles` list
means every `VehicleDef`** — `LoadDefModExtensionCosts` falls back to the whole
`DefDatabase<VehicleDef>` when the list is null or empty [V, confirmed]. That is what makes five
operations sound: without it the fix would be per-vehicle and would not cover a vehicle a later
mod adds. The ordering is right:
`VehicleHarmony`'s static constructor runs `PostDefDatabaseCalls` **before**
`ApplyAllDefModExtensions` [V], so the extension overwrites the `AssignDefaults` fill rather
than losing to it. One `<modExtensions>` block per `RoadDef`, `vehicles` left empty to mean
*all*, restores §1's ladder for every vehicle in the set **and for any vehicle a later mod
adds**:

```xml
<!-- expect: 1 -->
<Operation Class="PatchOperationAdd">
  <xpath>/Defs/RoadDef[defName="DirtPath"]</xpath>
  <value>
    <modExtensions>
      <li Class="Vehicles.CustomCostDefModExtension">
        <cost>0.75</cost>
      </li>
    </modExtensions>
  </value>
</Operation>
```

…and four more, one per tier, tracking §1's table. **The `<cost>` values are [I] and are §1's
numbers, not new ones** — they exist to make the vehicle see the same ladder a caravan on foot
sees, and the balance deferral owns both.

> **Do not "fix" this by removing `customRoadCosts` instead.** The world path grid's
> `PassableRoad` local function is
> `vehicleDef.properties.customRoadCosts.ContainsKey(roadLink.road)` [V] — a vehicle with no
> entry for a road gets **no road benefit on the world map at all**. Override the values;
> never remove the keys.
>
> **The `expect: 1` annotations above are UNRUN**, for the same reason §2's are:
> [#102](https://github.com/cjd721/Rimworld-Archinity/issues/102) must land before
> `tools/patch_check.py` can measure a leading-`Defs/` xpath.

### Cost

| Piece | Kind | Estimate | Lands in |
|---|---|---|---|
| Tier speed ladder | XML, 5 `PatchOperationReplace` | ~25 lines | `Patches/Roads_Speed.xml` |
| Worldgen suppression | XML, 2 PatchOperations | ~12 lines | `Patches/Roads_Worldgen.xml` |
| `neverConnectToRoads` on isolated factions | XML, 1 field per faction | ~3 lines each | the faction's own def |
| Player-built tiers | XML, `VFEC.RoadBuildingDef` ×N + 1–3 `ResearchProjectDef` | ~60 lines | `Defs/RoadBuildingDefs.xml` |
| Player-built mechanism | **none** — VFE Classical ships it, MP Compat syncs it | 0 | — |
| — *if VFE Classical is declined by [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)* | new C# | ~70 lines + 1 `SyncMethod` | `Archinity.Core` |
| Era-rite road upgrade, incl. the proximity selection walk | new C#, inside #8's existing synced command | ~45 lines | `Archinity.Core` |
| `WorldComponent_RoadNetwork` ledger | new C# | ~50 lines | `Archinity.Core` |
| `ReachRungExtension` rows for [`CHARTING.md`](CHARTING.md) §4's reach band | **XML** — one `<modExtensions>` block per rung def | ~8 lines each | `Defs/RoadBuildingDefs.xml` |
| — *optional road-presence rung* | new C#, one `workerClass` | ~15 lines | `Archinity.Core` |
| **§4a** P1 `InitThread` prefix | new C# | ~8 lines | `Archinity.Core` |
| **§4a** P2 `RequestNewPath` prefix (private `vehicle` field ⇒ `AccessTools.FieldRefAccess`) | new C# | ~20 lines | `Archinity.Core` |
| **§4a** P3 `RecalculateAllPathCostsAsync` prefix (sync entry is `private` ⇒ `AccessTools.Method`) | new C# | ~15 lines | `Archinity.Core` |
| **§4a** `MP.IsInMultiplayer` gate and Harmony wiring | new C# | ~15 lines | `Archinity.Core` |
| **§4b** air-rung re-gate, `VVE_Frog` / `VVE_Toad` | XML, 2 `PatchOperationReplace` | ~10 lines | `Patches/Vehicles_Gating.xml` |
| **§4b** per-vehicle rung values (`MoveSpeed`, `worldSpeedMultiplier`, `FlightSpeed`) | XML, 1 op per value | ~5 lines each | `Patches/Vehicles_Ladder.xml` |
| **§4c** `CustomCostDefModExtension` on the five `RoadDef`s | XML, 5 `PatchOperationAdd` | ~35 lines | `Patches/Roads_VehicleCosts.xml` |
| **§4** vehicle content, gating research, world-travel maths, MP sync of caravans and flight | **none** — VF and VVE ship it, MP Compat syncs it | 0 | — |

**Two builds, and what separates them.** *Build A* ships VFE Classical and inherits the
player-financed half plus its multiplayer sync for nothing. *Build B* reimplements ~70 lines
in `Archinity.Core` and registers one `SyncMethod`. The deciding question is not technical —
it is whether [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) wants VFE
Classical for its own sake (three republics, senators, classical research). **Build A is
recommended while VFE Classical is in the set**; Build B is the fallback and is cheap, so
nothing here blocks on the sourcing call.

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
  `ExposeBody` → `DataExposeUtility.LookByteArray` on `tileRoadOrigins`, `tileRoadAdjacency`
  and `tileRoadDef`, populated from `potentialRoads` by `SerializeRoads()` at save and
  restored by `DeserializeRoads()` at load [V]. Runtime writes persist for free.
- **Back-compatibility is clean in both directions.** Roads added to a save that predates
  the feature load normally (they are just more entries in the same byte arrays). The
  ledger `WorldComponent` is constructed empty on a save that predates it, and an empty
  ledger means "unattributed", not "broken".
- **Def-level suppression is not retroactive.** The byte arrays are written from the tiles
  that existed at generation, not re-derived from defs. See *the freeze*, below.
- **Every mutation is inside a synced command.** The era rite is #8's; the player-financed
  route is MP Compat's synced `AddRoadGizmos` lambda (or ours in Build B). Neither consumes
  `Rand` — the upgrade path re-overlays existing links and the player path targets one
  named neighbour — so the *Divergence* gate in `CODING_STANDARDS.md` passes without a
  `Rand.PushState` argument at all.
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
- **No cache to invalidate.** `GetRoadMovementDifficultyMultiplier` is read per edge inside
  `CostToMove` [V]; `WorldPathGrid`'s cached per-tile difficulty does **not** include the
  road multiplier, so a road write needs no `RecalculateLayerPerceivedPathCosts`. Do not add
  a cache — a per-client snapshot of derived world state is the **T-20 class** of bug.

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

- **A downgrade written through `OverlayRoad` is a silent no-op** (**T-43**). Any
  future degradation feature must mutate `potentialRoads` on both endpoint tiles directly;
  `OverlayRoad` cannot express it.
- **A road in a biome with `allowRoads = false` is drawn but inert** (**T-44**).
  `WorldDrawLayer_Roads.Regenerate` reads `potentialRoads` directly, while `SurfaceTile.Roads`
  — the getter every gameplay reader uses — returns `null` when the biome forbids roads [V].
  Build across such a biome and the player sees a road that gives no speed benefit, with no
  message. RimPacts ships a postfix on exactly this getter to work around it, which is
  independent corroboration.
- **Road tier is a silent no-op until §1 lands** (**T-42**). Every consumer of tier — the
  era rite's visible upgrade, the Charting rungs below, VFE Classical's 1000-work stone road
  — is reading a constant until the five `PatchOperationReplace`s ship.
- **A worldgen patch matching zero nodes is silent in game, and is currently *also* silent
  under the tooling.** A `PatchOperation` that matches nothing logs nothing at runtime. The
  `<!-- expect: 1 -->` annotations exist so that `tools/patch_check.py` catches drift — but
  per [#102](https://github.com/cjd721/Rimworld-Archinity/issues/102) that check does not
  presently work for a leading-`Defs/` xpath, which both of ours are. Until #102 lands the
  annotations are documentation, not a gate.
- **Losing the ledger loses attribution, not roads.** The network is engine state; the
  component only records who paid.
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
(1.6.4871 rev590). §1–§3 established by
[#68](https://github.com/cjd721/Rimworld-Archinity/issues/68) and re-verified by the
adversarial audit of 2026-09-12, which returned **SOLID WITH FIXES**; the fixes are folded
into this document. §4 established by
[#69](https://github.com/cjd721/Rimworld-Archinity/issues/69), also **READ**, with one narrow
RUN item named in *Verification*.

**A provenance note the resolution got wrong.** #68 flagged that `docs/TRAPS.md`'s
provenance lines still read 1.6.4566. **`docs/TRAPS.md` carries no version line at all** —
the 1.6.4566 markers are in `docs/traps/world-creation.md` (ten entries) and the header of
`docs/engine/factions-and-worldgen.md` [V]. **None of them touches roads, and nothing in
#68 is invalidated by the version skew.** Re-verifying those ten entries against 1.6.4871
is [#107](https://github.com/cjd721/Rimworld-Archinity/issues/107).

**Verified available mechanisms** — not yet selected:

- The vanilla road model end to end: storage, persistence, worldgen, draw layer, inspect.
- VFE Classical's `WorldComponent_RoadBuilding` + `RoadBuildingDef`, and Multiplayer
  Compatibility's sync of it.
- VEF's `FactionDefExtension.neverConnectToRoads`.
- Vehicle Framework's whole vehicle model: `VehicleDef`, `VehiclePathFollower`,
  `VehicleCaravan`, `AerialVehicleInFlight`, `CompVehicleLauncher`, the upgrade trees, and
  `VehicleCaravanTicksPerMoveUtility` as the world-travel maths.
- VVE's 23 vehicles, four research projects and five air vehicles.
- `Vehicles.CustomCostDefModExtension` as the per-`RoadDef` override lever (§4c).
- Multiplayer Compatibility's sync of vehicle caravans, aerial flight, cargo sessions,
  targeted landing, turrets, fuel and banishment.

**Proposed, marked [I] by construction:** the tier ladder values, the era→tier mapping, the
era rite's proximity selection rule and its `N`, the ledger component, the era-rite upgrade
pass, the three §4a prefixes, §4b's rung values and re-gate, §4c's five `<cost>` values, and
the `ReachRungExtension` rows below. The mechanisms each composes are [V]; the claim that they
compose into the wanted behaviour is [I] until built.

**Two premises in #68's ticket were wrong and are corrected here:**
`RoadDef.worldTransitionPathCostFactor` **does not exist** — the field is
`movementCostMultiplier`; and `World.grid.roads` does not exist in 1.6 — roads live on
`SurfaceTile.potentialRoads`, reached through `WorldGrid.OverlayRoad` / `GetRoadDef`.

**One claim in #68's resolution was wrong and is struck here:** removing the `AncientRoads`
gen step does **not** suppress `GenStep_ScatterRoadDebris`. See §2.

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

Five `RoadDef`s in `Core/Defs/RoadDefs/RoadDefs.xml` [V] and **no others anywhere in the
corpus** **[I]** — not one of the 155 mods ships a `<RoadDef>`, on a corpus sweep, which is an
inference and not a read. `DirtPath` (priority 10),
`DirtRoad` (20), `StoneRoad` (30), `AncientAsphaltRoad` (40, `ancientOnly`) and
`AncientAsphaltHighway` (50, `ancientOnly`). The five vanilla tiers are the entire
vocabulary the campaign has to work with, and that is sufficient: one per era with the
highway held back for the capstone.

`RoadDef` carries `priority`, `ancientOnly`, `movementCostMultiplier`, `tilesPerSegment`,
`pathingMode`, `roadGenSteps` (what terrain a generated map lays), `worldRenderSteps` (what
the world map draws) and `worldTransitionGroup` [V].

### VFE Classical — the player-financed half, shipped and synced

Covered under *The build*. The finding that matters is that it is **research-gated by
construction**, so an era gate on player road-building costs one `ResearchProjectDef` and no
code. Read it at `1.6/Assemblies/VFEC.dll` — the source on disk is 1.3/1.4 only (⚠ in
`MOD-SNAPSHOT.md`).

### Multiplayer Compatibility — the VFE Classical road sync, at a nonstandard path

`Multiplayer.Compat.VanillaFactionsClassical`, in
`294100/1629973374/1.6/Referenced/Multiplayer_Compat_Referenced.dll` [V]. **Not** in
`1.6/Assemblies/`, which holds only `Multiplayer_Compat.dll`. The mod also ships
`AssembliesCustom/` and `1.6/Lunar/Components/`; any sweep or citation that assumes
`<mod>/1.6/Assemblies/` will miss its compat layer entirely.

### VEF — worldgen endpoint suppression, in XML

`FactionDefExtension.neverConnectToRoads`, applied through a postfix on
`WorldGenStep_Roads`'s endpoint predicate [V]. Per-faction; does not reach the extra random
road nodes.

### The other corpus readers of the road API

Neither is a donor; both are recorded because the ladder in §1 is a global change and this
is who else sees it.

| Mod | Path | Carries | Bearing on the build |
|---|---|---|---|
| **Vehicle Framework** `smashphil.vehicleframework` | `1.6/Assemblies/` | `Vehicles.RoadCostHelper.GetRoadMovementDifficultyMultiplier(List<VehicleDef>, RoadDef)` — takes `roadDef.movementCostMultiplier` as a base, **replaced** per vehicle by `VehicleDef.properties.customRoadCosts[roadDef]`, unconditionally and in either direction [V] | **A third reader of the field, and a silent bypass of the ladder — resolved in §4c**, which reads the override loop in full and finds that 14 VVE vehicles flatten all five tiers |
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

### RimPacts — the surveyed alternative for the NPC half, and it is declined

RimPacts ships NPC road construction: `RoadWork` (a `Settlement`, a `List<int> pathTiles`, a
`finishTick` and a `tier`), a Dijkstra `RptRoadPather`, a cost table
(`RptTuning.RoadTierCostPerTile` = 80/150/250/400/600 per tile across the five vanilla
tiers), `RoadDaysPerTile = 0.25f`, and a `Patch_SurfaceTile_Roads` postfix that restores
`SurfaceTile.Roads` for tiles it built in biomes that forbid roads [V].

**It is the shape #8 explicitly declined.** Conrad: *"I don't need a tiny incremental. Every
in-game day we do a count, and then every ten in-game days another faction gets taken
over."* RimPacts advances roads on a `finishTick` clock inside `WorldComponentTick`; the era
rite advances them in one visible movement. Taking RimPacts for roads alone would import a
parallel world model for a feature the rite gives us for ~30 lines. Its **tier table and
per-tile cost are worth stealing as balance input** if player-financed roads ever get a
silver price.

### Faction Territories and Vassalage — context only

Declined outright ([#35](https://github.com/cjd721/Rimworld-Archinity/issues/35),
`MOD-VERDICTS.md`). It ships a `RoadConstruction` symbol and weights roads in a Dijkstra
pass; neither is a candidate.

### What does not exist anywhere, and where it shaped the build

- **Road ownership, contest or capture.** No hits across both corpus roots. This is why the
  build reduces "contest a corridor" to "capture the settlements on it", keeps only an
  attribution ledger, and why §3's era rite must select routes by proximity rather than by
  owner.
- **Any era or tech-level input to road tier.** `WorldGenStep_Roads` picks uniformly at
  random from the non-`ancientOnly` set; nothing in the corpus changes that. This is why
  suppression is `ancientOnly` on `StoneRoad` rather than a weighting patch.
- **Any road-building designator vocabulary** — `Designator_Road`, `BuildRoad`,
  `ConstructRoad`, `PaveRoad`, `WorldObject_Road`, `CaravanRoad` all return nothing. Road
  building is a caravan gizmo or it is nothing.
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
4. **§4a is the one RUN item in this document, and it is a single one-client log check.**
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

## Outstanding decisions

- **The ladder values are a requirement, not a mechanism, and they now have an owner.**
  §1's five numbers, the era→tier mapping, the era rite's proximity radius `N`, §4b's
  per-vehicle `MoveSpeed` / `worldSpeedMultiplier` / `FlightSpeed` values and §4c's five
  `<cost>` values are all starting proposals. What travel time *should* feel like per era
  belongs to
  **the balance deferral in [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2)**,
  which owns world mobility and travel time generally. **The road ladder and the vehicle
  ladder must be set in one sitting**, because they multiply and because `customRoadCosts`
  overrides the road ladder outright (§4c). One owner, one decision.
- **"Protect" is unanswered.** `docs/plot/INDUSTRIAL.md` § *Roads and Mobility* asks that
  the player be able to *"finance, **protect**, capture and benefit from"* infrastructure.
  This document answers finance (VFE Classical's caravan gizmo), capture (the settlements at
  a route's ends, via #8's rite) and benefit (the speed ladder). **Protect has no mechanism
  and no design here** — nothing in the corpus models a road as a thing that can be
  threatened, and `OverlayRoad` cannot express damage. Handed to
  the balance deferral in [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2) as part of what world
  mobility must mean.
- **Road debris on a roadless map is an open lever with no owner.** Suppressing
  `AncientRoads` leaves 1–2 ancient vehicle wrecks per map and spreads them map-wide (§2).
  Removing them means reaching the `GenStep_ScatterRoadDebris` entry in the map generator's
  step list, which has not been investigated. **A gap, not a hand-off** — no ticket owns it.
- **`docs/requirements/CHARTING.md` does not currently state that road quality feeds the
  reach band.** The text #68 cited (*"maintained roads and vehicles widen the region"*) is
  from a superseded revision. Roads publish rungs regardless (below), but whether reach
  reads them is a Charting-requirements decision, and **it has no open owner** — #57, the
  ticket this would have been handed to, is closed and nothing has replaced it. The
  requirement needs restoring or retiring by whoever picks Charting's requirements up; stated
  here as a gap and left to be routed. This document does not edit either Charting file.
- **Whether routes can degrade.** The build says capture, not degrade. If requirements
  later ask for a contested route physically decaying, it is ~15 lines of direct
  `potentialRoads` mutation and it cannot go through `OverlayRoad` (T-43).
- **Build A versus Build B** waits on
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

### The rungs this document publishes to Charting's reach band

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
  `VVE_AerialVehicles` and only dirt paths reaches 90; a colony with highways and no vehicles
  reaches 34. That matches CHARTING § *Reach*'s *"two knobs with no interaction term"*, and it
  is why neither ladder needs to know the other exists at the band level — even though, at the
  *travel time* level, §4c says they multiply.

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
