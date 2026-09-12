# World infrastructure

## Purpose and scope

How the world's road network satisfies
[`docs/plot/INDUSTRIAL.md`](../plot/INDUSTRIAL.md) § *Roads and Mobility* — *"the vanilla
map should not begin covered in modern paved roads… Neolithic travel uses paths and dirt
tracks; Medieval powers begin maintaining routes; Industrial civilization paves and expands
them"* — and [`docs/plot/MEDIEVAL.md`](../plot/MEDIEVAL.md)'s *"roads become political
infrastructure."*

This document owns the **world-map road network**: what exists at worldgen, what changes it
during play, who is recorded as having built it, and the transport signal it publishes.

It does not own **vehicles** ([#69](https://github.com/cjd721/Rimworld-Archinity/issues/69)),
which are the other half of the mobility ladder. It does not own **Charting's reach band**
([#57](https://github.com/cjd721/Rimworld-Archinity/issues/57) and
[`CHARTING.md`](CHARTING.md) **§4 — *The reach band*** own that outright) — this document
supplies rungs in the form that section defines and nothing more. It does not own
**settlement ownership**, which is
[#8](https://github.com/cjd721/Rimworld-Archinity/issues/8)'s era rite; roads ride that
command rather than owning one.

One thing the plot asks for is **not** answered here and is not deferred to a design that
exists: *"finance, **protect**, capture and benefit from"* infrastructure. Finance, capture
and benefit are below. **Protect is a gap** — see *Outstanding decisions*, handed to
the balance deferral in [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2).

## The build

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
`VehicleDef.properties.customRoadCosts[roadDef]` override it, lower winning [V]. A vehicle
that declares `customRoadCosts` therefore **bypasses the ladder silently** — the ladder
still lands for caravans on foot and for every vehicle that declares nothing, but VF's
per-vehicle table is a second, independent dial over the same tiers. **`customRoadCosts` is
handed to [#69](https://github.com/cjd721/Rimworld-Archinity/issues/69) by name**: whoever
sets the vehicle ladder must set it against this table, not only against `RoadDef`.

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
| `ReachRungExtension` rows for [#57](https://github.com/cjd721/Rimworld-Archinity/issues/57) | **XML** — one `<modExtensions>` block per rung def | ~8 lines each | `Defs/RoadBuildingDefs.xml` |
| — *optional road-presence rung* | new C#, one `workerClass` | ~15 lines | `Archinity.Core` |

**Two builds, and what separates them.** *Build A* ships VFE Classical and inherits the
player-financed half plus its multiplayer sync for nothing. *Build B* reimplements ~70 lines
in `Archinity.Core` and registers one `SyncMethod`. The deciding question is not technical —
it is whether [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) wants VFE
Classical for its own sake (three republics, senators, classical research). **Build A is
recommended while VFE Classical is in the set**; Build B is the fallback and is cheap, so
nothing here blocks on the sourcing call.

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
- **No campaign softlock exists here.** Roads are a speed modifier and a piece of scenery.
  The worst outcome of every failure above is a slower or uglier world map.

## Status

**Evidence class: READ.** Settled from `Core` defs and decompiled 1.6 assemblies
(1.6.4871 rev590). Established by
[#68](https://github.com/cjd721/Rimworld-Archinity/issues/68) and re-verified by the
adversarial audit of 2026-09-12, which returned **SOLID WITH FIXES**; the fixes are folded
into this document.

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

**Proposed, marked [I] by construction:** the tier ladder values, the era→tier mapping, the
era rite's proximity selection rule and its `N`, the ledger component, the era-rite upgrade
pass, and the `ReachRungExtension` rows below. The mechanisms each composes are [V]; the
claim that they compose into the wanted behaviour is [I] until built.

**Two premises in the ticket were wrong and are corrected here:**
`RoadDef.worldTransitionPathCostFactor` **does not exist** — the field is
`movementCostMultiplier`; and `World.grid.roads` does not exist in 1.6 — roads live on
`SurfaceTile.potentialRoads`, reached through `WorldGrid.OverlayRoad` / `GetRoadDef`.

**One claim in the resolution was wrong and is struck here:** removing the `AncientRoads`
gen step does **not** suppress `GenStep_ScatterRoadDebris`. See §2.

## Available mechanisms

### Vanilla and DLC — the whole model is here

Five `RoadDef`s in `Core/Defs/RoadDefs/RoadDefs.xml` and **no others anywhere in the
corpus** [V] — not one of the 155 mods ships a `<RoadDef>`. `DirtPath` (priority 10),
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

### Multiplayer Compatibility — the sync, at a nonstandard path

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
| **Vehicle Framework** `smashphil.vehicleframework` | `1.6/Assemblies/` | `Vehicles.RoadCostHelper.GetRoadMovementDifficultyMultiplier(List<VehicleDef>, RoadDef)` — takes `roadDef.movementCostMultiplier` as a base, overridden per vehicle by `VehicleDef.properties.customRoadCosts[roadDef]`, lower winning [V] | **A third reader of the field, and a silent bypass of the ladder.** [#69](https://github.com/cjd721/Rimworld-Archinity/issues/69)'s, by name |
| **Better Traders Guild** `shunter.bettertradersguild` (`3684587591`) | `1.6/Assemblies/BetterTradersGuild.dll`, present under **both** roots | One `GetRoadMovementDifficultyMultiplier` reference [V] (byte scan); apparently read-only for its own caravan costing [I] — not decompiled | None. Recorded for completeness of the reader set; no verdict changes |
| **Rim War** `torann.rimwar` | `v1.6/Assemblies/` | One read-only `GetRoadMovementDifficultyMultiplier` reference; writes no roads [V] | Already barred and declined (`MOD-VERDICTS.md`); nothing here reopens it |
| **Map Mode Framework** `nozome.mapmodeframework` | `1.6/Assemblies/` | References `WorldDrawLayer_Roads` as a layer name [I] | Not a road feature |

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
> null-interleaved byte scan, and **they hold** [V]. What is retracted is the claim that the
> sweep was validated before its negatives were trusted. Any future re-run of this survey
> must use the null-interleaved form.

`corpus.py --check` reported the corpus matching the snapshot at 155 mods at the start and
the end of the pass [V].

**Field-reader claims are exhaustive, not sampled — within `Assembly-CSharp`.**
`Assembly-CSharp.dll` was decompiled whole (`ilspycmd -o`) and every reader of `ancientOnly`
(1), `movementCostMultiplier` (2), `allowRoads` (2) and `OverlayRoad` (2 callers) was
enumerated in the decompiled source [V]. Mod assemblies were **not** decompiled wholesale;
Vehicle Framework's third read of `movementCostMultiplier` is the reason that distinction
now appears in §1.

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

## Outstanding decisions

- **The ladder values are a requirement, not a mechanism, and they now have an owner.**
  §1's five numbers, the era→tier mapping and the era rite's proximity radius `N` are
  starting proposals. What travel time *should* feel like per era belongs to
  **the balance deferral in [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2)**,
  which owns world mobility and travel time generally. It pairs with
  [#69](https://github.com/cjd721/Rimworld-Archinity/issues/69)'s vehicle ladder, because
  the two multiply — and because VF's `customRoadCosts` can override the road ladder
  outright, the two must be set together.
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
  reads them is [#57](https://github.com/cjd721/Rimworld-Archinity/issues/57)'s to decide
  and the requirement needs restoring or retiring by whoever owns Charting's requirements.
  This document does not edit either Charting file.
- **Whether routes can degrade.** The build says capture, not degrade. If requirements
  later ask for a contested route physically decaying, it is ~15 lines of direct
  `potentialRoads` mutation and it cannot go through `OverlayRoad` (T-43).
- **Build A versus Build B** waits on
  [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s call on VFE Classical.

### The rungs this document publishes to [#57](https://github.com/cjd721/Rimworld-Archinity/issues/57)

**Charting's reach band is #57's outright**, and its interface is fixed by
[`CHARTING.md`](CHARTING.md) **§4 — *The reach band*, § *The rung registry***. That section
is the contract; this document conforms to it rather than proposing an alternative. An
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
