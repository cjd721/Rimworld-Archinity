# Gravship and substructure

What substructure affords, what will and will not fly on it, and how the launch
budget is actually counted.

Verified against decompiled RimWorld 1.6.4871 unless an entry says otherwise.
These are *verified available mechanisms*, not commitments to use them —
selection happens in `docs/specs/`.

---

## Substructure affordances

`Substructure` is `ParentName="FloorBase"` and `XmlInheritance` appends (see
`docs/TRAPS.md` T-05), so its resolved affordances are
`[Light, Medium, Heavy, Walkable, Substructure]`. `GridsUtility.GetAffordances`
returns the **foundation** list, overriding any floor laid on top.

`TerrainDef.IsSubstructure` is `HasTag("Substructure")` and nothing else, so a
modded terrain joins the system by declaring that tag — see **Substructure that
does not count**, below.

## What flies and what does not

- **A thing flies only if every cell of its `OccupiedRect` is valid
  substructure.** `Gravship.AddThing` gates on
  `Building_GravEngine.OnValidSubstructure`. The one exception is
  `building.isAttachment`, which tests the wall the thing hangs on instead —
  so wall attachments (`OxygenPump`, in-wall `Cooler`/`Heater`) cost **zero
  floor cells** and still fly.
- `Heavy` buildings fly fine. **`Diggable` and `SmoothableStone` do not**, so
  `DiggingSpot` and `MiningSpot` are unbuildable on substructure. Same reason
  graves cannot fly.
- `MedievalOverhaul.PlaceWorker_WaterWheel.AllowsPlacing` has an explicit
  `WaterCellsPresent` check, so the water mill is impossible on a gravship.
- `GardeningBox` works (`Light` affordance, own `fertility 0.8` via the edifice
  branch) — **but 0.8 is unusable at colony scale.** `HydroponicsBasin` is 2.8
  and `VGE_Agrocell` is 3.2, so the gardening box is 3.5–4× worse per cell. It
  is the pre-industrial answer and belongs nowhere near a Spacer deck. `Post`
  does not work at all; its `DankPyon_GrowSoilVine` affordance is never patched
  onto `Substructure`.
- **`LargeThruster`'s `exclusionAreaSize (2,0,7)` must be clear *and must not be
  substructure*** (`CompGravshipThruster.IsBlocked`, `blockedBySubstructure`),
  and the thruster should be outdoors. That is **14 cells — two wide by seven
  deep**, at `exclusionAreaOffset (0,0,-7)`; `SmallThruster`'s `(1,0,5)` is 5.
  Thrusters therefore live on external pods pointing out of the hull, which
  costs their own cells but constrains the hull shape more than the budget.

## The launch budget

- **Budget is cells, not mass.** `MaxLaunchWeight` does not exist. Un-patched,
  `GravEngine` gives `SubstructureSupport 500` and up to 6 `GravFieldExtender`
  add 250 each, so **2000 cells in pure Odyssey**.
- **Never quote those numbers under a mod set.** Both are replaced by patches,
  silently, and a budget computed from the def values is wrong. This is
  `docs/TRAPS.md` **T-50**. What the two gravship mods actually do:

  | Load order | Offsets | Multiplier | Ceiling |
  |---|---|---|---|
  | Odyssey alone | 500 + 6 × 250 = 2,000 | 1.00 | **2,000** |
  | + `als.gravtech`, no VGE | + 3 × `GravFieldPylon` 500 + `AdvShip_GravReactor` 1,000 | 1.00 | **4,500** |
  | `vanillaexpanded.gravship` alone | 250 + 10 × 100 = **1,250** | 1.30 with six `LargeThruster` | **≈1,625 — *lower* than vanilla** |
  | GravTech **and** VGE | 250 + 10 × 100 + 3 × 130 + 500 = **2,140** | 1.80 – 2.10 | **≈3,850 – 4,500** |

  The patches, all verified in the raw XML:

  - `VGE 1.6/Patches/VanillaGravEngineLinking.xml` — `GravEngine`
    `SubstructureSupport` **500 → 250**, footprint radius **18.9 → 11.9**, and
    the engine gains `CompAffectedByConstantGravshipFacilityBonus`.
  - `VGE 1.6/Patches/GravFieldExtender.xml` — extender **250 → 100**,
    `maxSimultaneous` **6 → 10**, `maxDistance` **→ 500**, footprint radius
    **16.9 → 12.9**, place worker → `PlaceWorker_InRangeOfGravSource`.
  - `VGE 1.6/Patches/VanillaThrusters.xml` — adds
    `CompProperties_ConstantGravshipFacilityBonus`:
    **`LargeThruster` +0.05** each (max 6), **`SmallThruster` +0.01** each
    (max 10). VGE's own `VGE_GiantThruster` (3×3) carries **+0.10** (max 4).
  - `als.gravtech 1.6/Mods/VanillaGravshipExpanded/Patches/VGE_Patch_GravTech.xml`
    — restats **both** GravTech facilities: `GravFieldPylon` **500 → 130** with
    a **+0.10** multiplier, and `AdvShip_GravReactor` **1,000 → 500** with a
    **+0.50** multiplier (its power also moves −150,000 → −120,000 and its
    footprint radius to 49.9). The reactor restat is easy to miss because the
    pylon restat is the one everybody quotes.

  The multiplier path: VGE's `Patches/Stats.xml` adds
  `VGE_SubstructureSupportMultiplier` to the `SubstructureSupport` StatDef's
  `statFactors`, and `StatWorker.GetValueUnfinalized` applies comp offsets and
  *then* multiplies by `req.Thing.GetStatValue(statFactors[i])`.
  `CompAffectedByConstantGravshipFacilityBonus.GetStatOffset` sums
  `CompConstantGravshipFacilityBonus.statOffsets` over every linked facility —
  including inactive ones.

  **Read the composed number off the engine's stat page. Do not sum defs.**
- **`VGE_GravFieldAmplifier` is the largest single lever** and is easy to
  overlook: 3×3, `SubstructureSupport` **+200**, `maxSimultaneous 4`, footprint
  radius 22.9, `maxDistance 500`, `AdvancedGravtech`, **2 `Gravcore` each**. It
  carries no multiplier of its own, so four of them add 800 to the offsets —
  worth roughly +1,440 to +1,680 of composed ceiling.
- **Geometry does not bind before the stat does — if the extenders are spread.**
  Un-patched, extenders must sit within 18.9 cells of the engine
  (`PlaceWorker_InRangeOfGravEngine`). Six of them **at that limit** give a
  buildable footprint union of ~3,550 cells, inside which the largest
  axis-aligned rectangle is ~2,400; a 2000-cell rectangular deck fits with room
  over. Six of them **bunched beside the engine** collapse that union to ~1,290
  cells and the largest rectangle to ~780. The difference matters because
  `GravshipUtility.GetConnectedSubstructure` runs with
  `requireInsideFootprint: true` — substructure outside the union is not
  connected at all, whatever the stat says. Extender placement is a hull-shape
  decision.
- **The cap is a flood-fill limit, not a placement check.**
  `GravshipUtility.GetConnectedSubstructure` is
  `Map.floodFiller.FloodFill(engine.Position, …, maxCells)`, so cell 2001 builds,
  walks, holds buildings — and is simply absent from `validSubstructure`.
  It is dropped on launch, outermost first, with no message. This is
  `docs/TRAPS.md` **T-46**.
- **`Building_GravEngine.GetOrbitalWarnings` states the engine's own sizing
  rules**: it warns below `ValidSubstructure.Count / 400` `CompOxygenPusher`s
  and below `ValidSubstructure.Count / 250` strong heat sources
  (`Building_Heater`, or any `CompHeatPusher` with `heatPerSecond > 20`). For a
  2000-cell ship that is **5 oxygen pumps and 8 heaters**. Warnings on the
  launch dialog, not gates.

## Substructure that does not count

`vanillaexpanded.gravship` ships `VGE_GravshipSubscaffold`, a terrain that
declares `<tags><li>Substructure</li></tags>` — so it is `IsSubstructure`, is
flood-filled, and counts as sealed floor for `VacuumUtility.IsRoomAirtight` —
while a Harmony prefix on `GravshipUtility.GetConnectedSubstructure`
(`VanillaGravshipExpanded.GravshipUtility_GetConnectedSubstructure_Patch`) raises
`maxCells` by one for **every subscaffold cell the fill reaches**. Subscaffold is
therefore free against the budget. Its `affordances` are `[Walkable]` only, so
nothing can be built on it: it is corridor and open-deck floor, and the walls
flanking a subscaffold corridor still cost real substructure.

This exemption is load-bearing, not a nicety. VGE lowers the engine and extender
offsets far enough that a VGE-only ship has a *smaller* budget than a vanilla
one; a deck that fits under VGE generally fits because its corridors are
subscaffold and are not being charged.

## Pressurisation

**There are two rules, with different callers, and conflating them is how an
orbital station gets declared vacuum.** [V]

- **Breathability — `Room.Vacuum` / `Room.ExposedToSpace` →
  `District.ExposedVacuumCount`.** `Room.ExposedToSpace` is
  `Map.Biome.inVacuum && (TouchesMapEdge || ExposedCountStopAt(1) > 0)`, and
  `District.ExposedVacuumCount` counts a cell only if it is **unroofed** or its
  terrain sets `exposesToVacuum`. **Roof and terrain flag, nothing else.** This
  is the rule that decides whether pawns take `VacuumExposure`, and it governs
  orbital platforms, asteroid bases and every in-vacuum map. `TerrainDefOf.Space`
  sets `exposesToVacuum`; Odyssey's `OrbitalPlatform` terrain does not.
- **The gravship cell-budget question — `VacuumUtility.IsRoomAirtight` →
  `IsRoomDirectlyOpenToOutside`.** It fails the room if it touches the map edge,
  has any open roof cell, **and additionally** if it contains any cell whose
  `terrainGrid.FoundationAt` is not `IsSubstructure`. `TerrainDef.IsSubstructure`
  is `HasTag("Substructure")`, which orbital-platform terrain does not set, so
  **`IsRoomAirtight` is false for every orbital-platform room — and that does not
  mean the room is vacuum-exposed.** On a gravship the same clause is what makes
  every interior cell of a pressurised room come out of the same cell budget as
  the walls around it.

The half the two rules share is the wall:

`Building.IsAirtight` is `def.building.isAirtight ||
(def.building.isStuffableAirtight && Stuff.stuffProps.isAirtight)`, and in the
whole vanilla + DLC stuff table only **Steel, Plasteel, Silver, Gold and
Uranium** set `stuffProps.isAirtight`. Stone, wood, jade, fabrics and — despite
being in the `Metallic` stuff category — **`Obsidian`** do not. See
`docs/TRAPS.md` **T-47**, which cites `IsRoomAirtight` for this wall half and is
correct there. `GravshipHull` sets `building.isAirtight` outright and sidesteps
the question.

**A breach kills the crop; it does not merely stall it.**
`Plant.GrowthPerTick` returns 0 outright when the plant's cell is at vacuum ≥ 0.5
and the plant is not `vacuumResistant` — but the same condition also makes
`Plant.DyingBecauseExposedToVacuum` true, which feeds
`Plant.CurrentDyingDamagePerTick` until the plant dies and posts
`MessagePlantDiedOfRot_ExposedToVacuum`. Recovery from a hull breach in a farm is
therefore *seal and resow*, and costs a full grow cycle, not the minutes the
breach was open.

## Gravcore supply

`Gravcore` is the gravship's real currency: 1 per `GravFieldExtender`, 1 per
`SignalJammer`, 1 per `GravcorePowerCell`, 2 per VGE `GravFieldAmplifier`, 2 per
GravTech `GravFieldPylon`, 10 per `AdvShip_GravReactor`. It has
`genericMarketSellable: false`, so it is not bought. Supply is
`QuestPart_SubquestGenerator_Gravcores`, which requires a colonist-owned
`GravEngine` on some map and enforces `MinTimeBetweenSubquests 900000` /
`MaxTimeBetweenSubquests 1800000` ticks after the first — **one gravcore site
every 15–30 days**, one gravcore per site
(`SitePartDef … requiredGravcoreRooms 1`). Any plan that spends gravcores is
spending calendar time at that rate.

---

The full deck accounting, life support, food and defense analysis for a
permanently inhabited ship lives in
[`docs/specs/GRAVSHIP.md`](../specs/GRAVSHIP.md); what the orbit layer does to
the incident pool is `docs/TRAPS.md` T-48, and the `Map.IsPlayerHome`
consequences are in that spec's *Living on the orbit layer*.

See also `docs/engine/mods/medieval-overhaul.md` for the Medieval Overhaul
buildings named above, and `docs/engine/world-time-and-layers.md` for the orbit
layer's geometry.

## Landing hooks, and which one can measure a move

`WorldComponent_GravshipController.InitiateTakeoff(engine, targetTile)` → `TakeoffEnded()`
→ `GravshipUtility.TravelTo(Gravship, PlanetTile oldTile, PlanetTile newTile)` → arrival →
`LandingEnded()` → `Find.Scenario.PostGravshipLanded(map)`. All [V].

**`PostGravshipLanded` takes only a `Map`.** There is no parameter and no state reachable
from it that says where the ship came from, so no distance test can be written against it.
Odyssey's own `ScenPart_PursuingMechanoids.PostGravshipLanded` reflects this — it resets
its timers unconditionally, with no distance check anywhere. [V]

**`takeoffTile` and `landingTile` survive.** Both are `private` on the controller but are
`Scribe_Values`-persisted as `"takeoffTile"` and `"targetTile"`, and `ResetCutscene()` —
`Find.ScreenshotModeHandler.Active = false; cutsceneInProgress = false; landingMap = null;`
— touches neither. [V] They are reachable by `AccessTools.Field` after the landing and
after a reload. `MapParent.Abandon(wasGravshipLaunch: true)` also leaves a `GravshipLaunch`
world object at the old surface tile, carrying `creationGameTicks`. [V]

**`TravelTo` mutates its own `oldTile` parameter** on a cross-layer move [V] — a postfix
reads the projection, not the origin.

**The whole path is frame-driven, and Multiplayer protects only half of it — T-78.**

**Distance:** `Find.WorldGrid.TraversalDistanceBetween(PlanetTile, PlanetTile)` is
layer-aware and is what `GravshipUtility.TryGetPathFuelCost` uses [V], so it is the number
the player already sees when launching.

Established on [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56); the system built on
it is `docs/specs/TRACE.md` § *The escape rule*. 1.6.4871.
