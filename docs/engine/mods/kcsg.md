# KCSG (Vanilla Expanded Framework)

Settlement and structure authoring: the in-game exporter, the two layout def
schemas, what already ships as reusable medieval vocabulary, and how siege
engines and garrisons get onto a map.

Verified against decompiled RimWorld 1.6.4871 source and workshop files on disk.
These are *verified available mechanisms*, not commitments to use them —
selection happens in `docs/specs/`.

---

## The exporter exists in 1.6

`KCSG.Designator_ExportToXml` and `Designator_ExportToXmlFromArea`, injected by
VEF into `DesignationCategoryDef[defName="Orders"]/specialDesignatorClasses`.

**Reach it:** dev mode, then Architect, then **Orders**, then **Export**, then
drag a rectangle. `Dialog_ExportWindow` gives a defName field, tag add/remove,
and toggles (`exportNatural`, `exportFilth`, `exportPlant`, `needRoofClearance`,
`spawnConduits`, `forceGenerateRoof`, `isStorage`, `randomizeWallStuffAtGen`,
`saveFuel`, `savePower`, `randomRotation`). **Copy structure** puts the whole
`StructureLayoutDef` on the clipboard. **Copy symbols** puts only the SymbolDefs
that do not already exist.

Round-trip check: Dev quickspawn, then "Temp structure...". An existing keep can
be spawned (`VFEM2_Keep_Alpha`), edited in place, and re-exported. **This
collapses the dominant cost of authoring castles.**

---

## SettlementLayoutDef schema

`settlementSize` (default 42,42), `samplingDistance` (8, Poisson spacing),
`avoidBridgeable`, `avoidMountains`, `centerBuildings` (REQUIRED: `centerSize`,
`spaceAround`, `forceClean`, `centralBuildingTags`, `allowedStructures`),
`peripheralBuildings`, `roadOptions`, `stuffableOptions`, `propsOptions`,
`defenseOptions`, `stockpileOptions`.

`StructOption` is `{ count: IntRange, tag: string }`. Placement Poisson-samples
points and weights by `GetWeight`: 0 once `count.max` is hit, 2 while below
`count.min`, 0.1 if it repeats the previous tag. **`count` is a soft target, not
a guarantee.**

### defenseOptions is dead below Industrial

`SymbolResolver_EdgeDefenseCustomizable` gates `addTurrets` and `addMortars` on
`faction.def.techLevel >= Industrial` (4). Medieval is 3. **Only `addSandbags`
and `pawnGroupMultiplier` take effect for a medieval faction.** Siege engines
have to live inside the layout grid instead. See `docs/TRAPS.md` T-30.

---

## StructureLayoutDef schema

`layouts` is a list of lists of strings: ordered **layers**, each a list of rows
of comma-separated symbol defNames, with `.` meaning empty. Layer order is spawn
order. Plus `terrainGrid` / `foundationGrid` / `underGrid` / `tempGrid`,
`terrainColorGrid`, `roofGrid` (`.` none, `1` RoofConstructed, `2` RoofRockThin,
else Thick), `tags`, `modRequirements` (packageIds; the layout is skipped
entirely if absent), `isStorage`, `spawnConduits`, `randomRotation`, `spawnAt`.

Size derives from `layouts[0]`. Rows and cells beyond that are **dropped
silently** (see `docs/TRAPS.md` T-29).

---

## A missing tag is a loud failure

**A tag no layout carries throws `KeyNotFoundException` mid-worldgen.**
`structuresTagsCache[tag]` is indexed unguarded, and `centralBuildingTags` has
no fallback. Worth adding to `check_refs.py`.

This one is loud. The quiet KCSG failures live in the trap register instead:

- `docs/TRAPS.md` T-32 — rotated `_North` / `_East` / `_South` / `_West` symbol
  variants are generated at runtime and cannot be patched, and
  `StartupActions.CreateSymbols` auto-generates only for Core, DLC, VFE Props
  and Decor, so every other modded ThingDef needs a hand-written SymbolDef.
- `docs/TRAPS.md` T-06 — `Def.GetModExtension` returns the FIRST match, so never
  add a second `KCSG.CustomGenOption` to a faction that already has one.
- `docs/TRAPS.md` T-05 — `XmlInheritance` appends list children; `Inherit="False"`
  clears first.
- `docs/TRAPS.md` T-29 and T-30, above.

---

## Who already uses KCSG

**VFE Medieval 2 does.** `Factions_Kingdom.xml` puts a `KCSG.CustomGenOption` in
the `modExtensions` of abstract `VFEM2_MedievalFactionBase`, pointing at an
85x85 settlement layout (one keep from tag `VFEM2_Keep`, 12 houses from
`VFEM2_MedievalHouses`, packed-dirt roads). All three kingdoms inherit it.

**Medieval Overhaul does too**, but via `chooseFromlayouts`: single hand-built
85x67 / 75x78 / 68x69 structures per noble house, rather than a tag pool.

**Vanilla Base Generation Expanded** is 100% def-only (634 StructureLayoutDef,
21 SettlementLayoutDef, 6 SymbolDef, no assembly, VEF only), but its faction
patch covers **only Empire, Tribals, Outlanders and Pirates**. It contains no
keeps, gatehouses, curtain walls, towers, chapels, stables or taverns.

### Reusable medieval vocabulary

| Source | Assets |
|---|---|
| VFEM2 | 10 keeps 38x38 (tag `VFEM2_Keep`), 48 houses 13x13, 31 tents, **143 SymbolDefs** covering castle walls in every stone, 2/3/4-wide gates, low walls, palisades, hearths, anvils, training dummies |
| MO | 31 layouts, **785 SymbolDefs**, no tags (referenced by defName). `DankPyon_StartingCastle` 26x27, `Dwarfenfortress` 144x153 |
| VFEC | 19 layouts, no tags. `Outpost_Struct_Defensive` 39x33, `_Artillery` 26x19 |

---

## Siege placement

A `StructureLayoutDef` can place anything with a ThingDef, including turrets,
traps and **pawns** (`SymbolDef.pawnKindDef` plus `numberToSpawn`;
`defendSpawnPoint: true` wraps them in a `LordJob_DefendPoint` radius 3, which
is a manned battlement).

- **`VFEM2_Turret_WallMountedArbalest` and `_Arquebus` exist and are never
  placed anywhere.** 1x1, `Building_TurretGun` plus `CompProperties_Mannable`,
  zero occurrences in `Keeps.xml`, no SymbolDef. Two hand-written symbols and
  they go straight into a tower.
- `DankPyon_Turret_Trebuchet` 3x3 can be placed (MO's own 1.5 layouts do it) but
  **spawns unmanned**. `SymbolUtils.SpawnMortar` auto-assigns a gunner via
  `LordJob_ManTurrets` only when `buildingTags` contains
  `Artillery_MannedMortar`. The trebuchet's tags are `Artillery_BaseDestroyer`,
  `ArtilleryMedieval`, `ArtilleryMedieval_BaseDestroyer`. Add a pawn symbol
  beside it, or patch the tag.
- The settlement garrison comes from `faction.pawnGroupMakers` via
  `SymbolResolver_Settlement.AddHostilePawnGroup` under `LordJob_DefendBase`,
  points equal to `DefaultPawnsPoints x defenseOptions.pawnGroupMultiplier`.
  Layout-placed pawns are additional.

### Enemy siege against the player

Medieval Overhaul's `MedievalOverhaul.RaidStrategyWorker_MedievalSiege` cannot
fire as shipped — `docs/TRAPS.md` T-31 has why. What is useful here is that both
the `MedievalOverhaul.FactionSiegeExtension` extension and the
`ArtilleryMedieval_BaseDestroyer` buildingTag are **plain def-level constructs**,
so they can be patched onto VFEM2 factions once MO is loaded.
Inside MO the extension is carried by two **abstract** faction bases —
`DankPyon_BrigandFactionBase` (`1.6/Defs/FactionDefs/Factions_Brigand.xml:113`) and
`DankPyon_NobleHouseFactionBase` (`Factions_NobleHouse.xml:155`) — so every brigand
and noble house inherits it. **No VFEM2 faction sets `canSiege`**, so vanilla sieges
cannot fire for them either.

*Re-verified against MO 1.6 on disk, 2026-09-08. An earlier record claimed
`DankPyon_BrigandFaction` was the only carrier; that was wrong on both the def name
and the count.*
