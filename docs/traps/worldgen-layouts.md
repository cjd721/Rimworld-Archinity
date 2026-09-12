# Traps: worldgen layouts

KCSG structure and settlement authoring, the shipped siege that never fires, the
road model whose tier dial is wired to nothing, and what a planet layer quietly
removes from the game. KCSG mechanisms in `docs/engine/mods/kcsg.md`.

Part of the trap register. **The index at `docs/TRAPS.md` is the file you read
before a diff**; this one carries the full entries for this group. Every entry here
fails with no error message. Cite by ID.

## Worldgen layouts

### T-29 — Layout rows and cells beyond `layouts[0]` are dropped silently

A `StructureLayoutDef`'s size derives from `layouts[0]`; rows and cells beyond that
are dropped with no message, so part of a hand-authored structure does not spawn.
Size every layer to the first layer, and re-export rather than hand-editing a grid's
width.

*`docs/engine/mods/kcsg.md`. 1.6.4871.*

### T-30 — `defenseOptions` is dead below Industrial

`SymbolResolver_EdgeDefenseCustomizable` gates `addTurrets` and `addMortars` on
`faction.def.techLevel >= Industrial` (4); Medieval is 3. Only `addSandbags` and
`pawnGroupMultiplier` take effect below Industrial — siege engines have to live
inside the layout grid instead.

*1.6.4871.*

### T-31 — `DankPyon_MedievalSiege` cannot fire as shipped

Its worker requires `RaidStrategyWorker_Siege.CanUseWith` (i.e.
`FactionDef.canSiege`) **and** a `MedievalOverhaul.FactionSiegeExtension` with
`medievalSiege: true` **and** `techLevel == Medieval`. The extension is on
`DankPyon_BrigandFactionBase` and `DankPyon_NobleHouseFactionBase`; **neither sets
`canSiege`**, which has **zero hits across all of Medieval Overhaul** (1.4/1.5/1.6,
defs, patches and assembly). Core `FactionBase` does not set it and the field
defaults `false`. Empty intersection — a shipped raid strategy that never occurs and
never explains itself. No VFEM2 faction sets `canSiege` either.

Fixing it is not a one-liner: `canSiege` must go onto **both** abstract defs, and
`RaidStrategyWorker.CanUseWith` adds further gates — the def's curve is
`(500,0) → (1000,1.6)`, so it needs **>500 threat points**, plus the Surface layer
and no blocking tile mutator. That makes it *possible*, not frequent.

What it would buy: the def already ships `LordJob_MedievalSiege` with its own supply
generation and **trebuchets** — `DankPyon_Turret_Trebuchet` is the only holder of
`ArtilleryMedieval_BaseDestroyer`. *(MO's own arrival text says "catapults"; that is
flavour copy, not the def.)*

*`docs/engine/mods/medieval-overhaul.md`. MO 1.6.*

### T-32 — Rotated KCSG symbol variants are not defs and cannot be patched

`_North` / `_East` / `_South` / `_West` variants are generated at runtime by
`HotGenerateRotationSymbols` and never enter the def database, so a patch targeting
one matches nothing. Patch the base symbol. Related:
`StartupActions.CreateSymbols` auto-generates symbols **only** for Core, DLC, VFE
Props and Decor — every other modded ThingDef needs a hand-written SymbolDef.

*Same shape as the `USH_GlittershipChunk_North` finding. 1.6.4871.*

### T-42 — Road tier changes travel time by nothing

All five vanilla `RoadDef`s ship `movementCostMultiplier 0.5` — `DirtPath` (priority
10), `DirtRoad` (20), `StoneRoad` (30), `AncientAsphaltRoad` (40, `ancientOnly`) and
`AncientAsphaltHighway` (50, `ancientOnly`), every one of them at 0.5
(`Core/Defs/RoadDefs/RoadDefs.xml`). A dirt path is exactly as fast as an ancient
asphalt highway. **Upgrading a road is a silent no-op**: nothing says so, and the tile
tooltip prints the same 50% before and after.

Tier is not inert — it changes the world-map texture, the terrain laid on a generated
map, `tilesPerSegment`, `pathingMode` and `worldTransitionGroup`. It changes travel
time by nothing. Any design that treats road quality as a capability is reading a
constant until it patches the ladder itself. **No mod in the corpus ships or patches a
`RoadDef`**, so the ladder is ours to set and nothing will fight us for it.

Differentiating it is safe because the field's readers are enumerable and few. In
`Assembly-CSharp` there are **exactly two**, both on `WorldGrid`:
`GetRoadMovementDifficultyMultiplier` and
`FindMostReasonableAdjacentTileForDisplayedPathCost`. There is a third, out of
assembly: `Vehicles.RoadCostHelper.GetRoadMovementDifficultyMultiplier` takes the def's
value as its base and lets `VehicleDef.properties.customRoadCosts` undercut it per road
def — so under Vehicle Framework the two ladders multiply, and a patched road tier is
read there too.

*[#68](https://github.com/cjd721/Rimworld-Archinity/issues/68),
`docs/specs/WORLD-INFRASTRUCTURE.md`. 1.6.4871.*

### T-43 — `OverlayRoad` refuses to downgrade a road, and the refusal is silent

`WorldGrid.OverlayRoad(from, to, roadDef)` is the only road-writing API in the
assembly, and it is upgrade-only. It logs in exactly one case: handed a **null**
`RoadDef` it calls `Log.ErrorOnce("Attempted to remove road with overlayRoad; not
supported")` — loud, and easy to mistake for the whole story. Handed a real def whose
`priority` is **less than or equal to** the existing road's, it takes a bare `return`
— no log, no message, and no return value to check. So "the war destroyed the highway"
written through `OverlayRoad` does nothing at all, quietly.

There is no vanilla road-removal path to fall back on either: `RemoveRoad`,
`DowngradeRoad` and `DestroyRoad` return **zero hits corpus-wide**, `Assembly-CSharp`
included. Degradation or removal has to mutate `SurfaceTile.potentialRoads` directly on
**both** endpoint tiles — the link is stored symmetrically — and `OverlayRoad` cannot
express it.

The guard is the right behaviour for an era-advance pass, which can then be re-run or
run out of order without clobbering anything; it is a defect for every other purpose.

*[#68](https://github.com/cjd721/Rimworld-Archinity/issues/68). 1.6.4871.*

### T-44 — A road in a no-roads biome is drawn but inert

`SurfaceTile.Roads` returns `null` when `!PrimaryBiome.allowRoads`, and that getter is
what every gameplay reader goes through — `WorldGrid.GetRoadDef(visibleOnly: true)`,
`GetRoadMovementDifficultyMultiplier`, `FindMostReasonableAdjacentTileForDisplayedPathCost`,
`CaravanExitMapUtility.RandomBestExitTileFrom` and the terrain inspect surfaces. But
`WorldDrawLayer_Roads.Regenerate` reads `surfaceTile.potentialRoads` **directly**,
bypassing the gate.

So a road written into such a tile is **painted on the world map and does nothing**: no
movement bonus, no inspect line, no message. The player sees a road and is simply
wrong about it. RimPacts ships a postfix on exactly that getter
(`RimPacts.Patch_SurfaceTile_Roads`) to work around it — independent corroboration that
the behaviour bites in practice.

*[#68](https://github.com/cjd721/Rimworld-Archinity/issues/68). 1.6.4871.*

### T-48 — On an orbit layer the content pool collapses without a word

`PlanetLayerDef` `Orbit` inherits `onlyAllowWhitelistedIncidents`,
`onlyAllowWhitelistedGameConditions`, `onlyAllowWhitelistedArrivals` and
`onlyAllowWhitelistedArrivalModes` from the abstract `OrbitLayer`, along with
`canFormCaravans false` and `isSpace true`. `IncidentWorker.CanFireNow` then returns
false for any def that is neither `canOccurOnAllPlanetLayers` nor carries the layer in
its `layerWhitelist`, and quest generation applies the same test to `QuestScriptDef`.

Across the merged Core-plus-five-DLC database that leaves **18 of 91 `IncidentDef`s and
18 of 139 `QuestScriptDef`s** orbit-legal. A campaign act played from an orbital home
therefore loses wanderers, refugees, visitors, manhunter packs, infestations, solar
flares, toxic fallout and every walk-in social event — not by a design decision but by
a def field nobody set. **The storyteller keeps running; it simply has almost nothing
to pick, and nothing anywhere reports the narrowing.** Patch `layerWhitelist` onto every
def the campaign needs in orbit, and re-count after every mod addition.

Three supporting facts belong with it, because they close the exits an author would
reach for. The `Space` biome is `constantOutdoorTemperature -75` and `inVacuum true`,
and sets `canExitMap false`. `Verse.ExitMapGrid.MapUsesExitGridNow` is false for
`IsPlayerHome`, for `IsPocketMap` **and** for `map.Biome.inVacuum` — in orbit all three
apply. Nobody walks on and nobody walks off; every arrival and departure is a shuttle
or the gravship.

*[#71](https://github.com/cjd721/Rimworld-Archinity/issues/71),
`docs/specs/ORBIT.md`. 1.6.4871.*
