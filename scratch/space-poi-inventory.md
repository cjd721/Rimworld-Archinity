# Space / Orbit Point-of-Interest Inventory — RimWorld 1.6 + Odyssey

Scope: **active mods only** per `config/ModsConfig.xml` (64 active mods, Odyssey enabled).
Inactive-but-subscribed noted at the bottom.

Legend for **Faction rebindable?**
- **XML-full** — owning faction *and* map-gen faction are both plain XML elements.
- **XML-partial** — one of the two is XML, the other is hardcoded in C#.
- **C#-hard** — hardcoded, needs Harmony.

Legend for **Loot patchable?**
- **ThingSetMaker** — resolves through a `ThingSetMakerDef` (cleanest hook).
- **Prefab/LootSpawn** — resolves through `PrefabDef` → `ThingDef` with `CompProperties_LootSpawn <contents>`, which *is* a ThingSetMakerDef ref. Still XML.
- **Mineables** — `<mineableCounts>` / `<mineables>` XML lists.
- **C#-hard** — hardcoded thing spawns.

---

## 1. Odyssey (ludeon.rimworld.odyssey) — 13 distinct space POIs

| # | defName | Def type(s) | Map generator / layout | Owning faction (world object) | Map-gen faction | Faction rebindable? | Loot / reward | Loot patchable? | Lifecycle |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `SpaceSettlement` | WorldObjectDef (`ParentName="SpaceBase"`, `worldObjectClass Settlement`) | `SettlementPlatform` → GenStepDef `SettlementPlatform` (`GenStep_OrbitalPlatform`, `useSiteFaction=true`, layout `OrbitalSettlementPlatform`, `cannonDef GaussCannon`) + GenStepDef `SettlementPawnsLoot` | Assigned at worldgen by `FactionGenerator` — any FactionDef with `<layerWhitelist><li>Orbit</li></layerWhitelist>` + `settlementGenerationWeight`. Vanilla: `TradersGuild`, `Salvagers` | inherits site faction | **XML-full** — no defName-keyed faction anywhere; purely `FactionDef.layerWhitelist` driven | `GenStep_SettlementPawnsLoot.lootThingSetMaker` (public field, currently unset) → falls back to `faction.def.settlementLootMaker` → `MapGen_AbandonedColonyStockpile` | **ThingSetMaker** (two independent XML hooks) | Permanent worldgen |
| 2 | `DestroyedSpaceSettlement` | WorldObjectDef (`worldObjectClass DestroyedSettlement`) | inherits `Space` | former settlement owner | n/a | XML-full (inherits #1) | none | n/a | Permanent worldgen residue |
| 3 | `AsteroidMiningSite` | WorldObjectDef (`ParentName="ClaimableSpace"`, `ResourceAsteroidMapParent`) | `Asteroid` → GenStepDef `Asteroid` (`GenStep_Asteroid`, `mineableCounts` Gold/Plasteel/Uranium) | **none** — `QuestNode_Root_Asteroid` never assigns a faction | none | **C#-hard** (no faction plumbing at all; would need a different quest node) | `<mineables>` list on the QuestScriptDef + `<mineableCounts>` on GenStepDef `Asteroid` | **Mineables** | Quest-spawned, repeatable (`OpportunitySite_Asteroid`, `givenBy: OrbitalScanner`) |
| 4 | `AsteroidBasic` | WorldObjectDef (`ParentName="GeneratedAsteroid"`, `BasicAsteroidMapParent`) + GeneratedLocationDef `Asteroids` (`layerDefs: Orbit`) | `AsteroidBasic` → GenStepDef `AsteroidBasic` (`GenStep_BasicAsteroid`) + `AncientMiningCharge_Asteroid`, `AncientExplosivesCrate_Asteroid`, `AncientDrillPlatform_Asteroid`, `AncientTuneller_Asteroid`, `MechShipChunk_Asteroid` | **none** | none | **C#-hard** | `<mineableCounts>` + scatter GenSteps (`AncientExplosivesCrate`, `GravlitePanel` 5~10) | **Mineables** | Permanent worldgen |
| 5 | `OrbitalItemStash` | WorldObjectDef (`ParentName="GeneratedAsteroid"`) | `OrbitalItemStash` → `Asteroid_NoRuins` + GenStepDef `AsteroidItemStash` (`GenStep_AsteroidItemStash`). Layout hardcoded to `LayoutDefOf.OrbitalItemStash`; `worker.Spawn(..., faction: null)` | **none — hardcoded `null`** | **hardcoded `null`** | **C#-hard** ⚠️ | LayoutRoomDef `OrbitalItemStash_ItemRoom` → `<thingSetMakerDef>MapGen_OrbitalItemStash</thingSetMakerDef>` (= `ThingSetMaker_UniqueWeapon` + `MapGen_DefaultStockpile`) | **ThingSetMaker** ✅ | Quest-spawned, repeatable (`OpportunitySite_OrbitalItemStash`) |
| 6 | `Mechhive` / SitePartDef `OrbitalMechhive` | WorldObjectDef + SitePartDef (`ParentName="SpaceGravcoreLocationBase"`) | `Mechhive` → GenStepDef `OrbitalMechhive` (`GenStep_OrbitalMechhive`) | **none** — `QuestNode_Root_Gravcore_Mechhive` passes `null` | **`Faction.OfMechanoids` hardcoded**; `LayoutDef => LayoutDefOf.Mechhive` hardcoded | **C#-hard** ⚠️⚠️ | Cerebrex core via `SketchResolverDefOf.CerebrexCore`; `Reward_Unknown()` in C# | **C#-hard** ⚠️ | One-shot (endgame; `requiredSubquestsGiven: 7`) |
| 7 | `Opportunity_AbandonedPlatform` | SitePartDef (`ParentName="SpaceSiteBase"`) + GenStepDef | GenStepDef `Opportunity_AbandonedPlatform` → `GenStep_OrbitalPlatform`, `<factionDef>AncientsHostile</factionDef>`, `<layoutDef>Opportunity_AbandonedPlatform</layoutDef>`, `spawnSentryDrones=true`, exterior `CrashedShuttle`/`BaricadeTurret` | `ClaimableSpaceSite`; `QuestNode_Root_Site` has an **XML `<factionDef>` SlateRef** (unset → defaults `Faction.OfAncientsHostile`) | `<factionDef>` XML | **XML-full** ✅ (add `<factionDef>` to the quest node + edit GenStepDef) | Rooms `OrbitalStoreroom_Loot` (prefab `AncientSealedCrate` → `CompProperties_LootSpawn contents: MapGen_HighValueCrate`), `OrbitalStoreroom` ×2, `OrbitalComputerRoom`, `OrbitalStoreroom_GravshipUpgrade` @0.1 (→ `Reward_GravshipUpgrade`) | **Prefab/LootSpawn → ThingSetMaker** ✅ | Quest-spawned, repeatable (`OpportunitySite_AbandonedPlatform`, OrbitalScanner, 45–60d timeout) |
| 8 | `Opportunity_MechanoidPlatform` | SitePartDef + GenStepDef | `GenStep_OrbitalPlatform`, `<factionDef>Mechanoid</factionDef>`, layout `Opportunity_OrbitalMechanoidPlatform`, terrain `MechanoidPlatform` | `ClaimableSpaceSite`, quest-node `<factionDef>` unset → `AncientsHostile` | `<factionDef>` XML | **XML-full** ✅ | `MechLootRoom` prefabs: `GestatorTanksWithLoot`, `MechStorageCylinder_Cluster`, `AncientSpacerCrate_Cluster` | **Prefab/LootSpawn** ✅ | Quest-spawned, repeatable (`OpportunitySite_MechanoidPlatform`) ⚠️ *quest is gated behind `QuestNode_FactionExists faction=Insect` — looks like a vanilla copy-paste bug; disabling insects kills this POI* |
| 9 | `OpportunitySite_Satellite` | SitePartDef + GenStepDef | `GenStep_OrbitalSatellite`, `<factionDef>AncientsHostile</factionDef>`, `<layoutDef>OpportunitySite_Satellite</layoutDef>`, prefabs `SolarArray`/`AutoturretBarricade`, `spawnSentryDrones=true` | `ClaimableSpaceSite`, quest-node `<factionDef>` unset | `<factionDef>` XML | **XML-full** ✅ | `AncientSatelliteLootRoom` (prefab `AncientSealedContainer` → `Reward_AncientSealedContainer`), `AncientSatelliteSecondaryLootRoom` (`AncientSpacerCrateWithComponentSpacer`, `WoodenCratesWithSomeLoot`) | **Prefab/LootSpawn → ThingSetMaker** ✅ | Quest-spawned, repeatable (`OpportunitySite_Satellite`) |
| 10 | `Opportunity_OrbitalWreck` | SitePartDef + **two** GenStepDefs | `Opportunity_OrbitalWreck` → `GenStep_OrbitalWreck` `<factionDef>AncientsHostile</factionDef>`, layout `Opportunity_OrbitalWreck` (worker `LayoutWorker_AncientRuins`); **`Opportunity_OrbitalWreck_Salvagers` → `GenStep_SitePawns` `<factionDef>Salvagers</factionDef>`, `pawnGroupKindDef Combat`** (public C# field) | `ClaimableSpaceSite`, quest-node `<factionDef>` unset | **two** XML `<factionDef>` knobs | **XML-full** ✅✅ — the only Odyssey POI with a dedicated *live hostile pawn group* GenStep already split into its own patchable def | `OrbitalRuinsLootroom` (`AncientSealedCrate`→`MapGen_HighValueCrate`), `OrbitalRuinsHermeticCrate` (`MapGen_ScarlandsHermeticCrate`), `OrbitalRuinsSteelRoom`, `OrbitalRuinsAdvancedComponentRoom`, `OrbitalRuinsShelves` | **Prefab/LootSpawn → ThingSetMaker** ✅ | Quest-spawned, repeatable (`OpportunitySite_OrbitalWreck`) |
| 11 | `OrbitalFugitivePlatform` | SitePartDef + GenStepDef (both in `Script_OrbitalFugitive.xml`) | `GenStep_OrbitalPlatform`, `<factionDef>Salvagers</factionDef>`, layout `Opportunity_AbandonedPlatform_Enterable`, `spawnSentryDrones=false` | `ClaimableSpaceSite`, quest-node `<factionDef>` unset | `<factionDef>` XML | **XML-full** ✅ | Quest node `QuestNode_GenerateThingSet <thingSetMaker>Reward_GravshipUpgrade</thingSetMaker>` → `QuestNode_AddItemsReward` on `fugitive.Destroyed` | **ThingSetMaker, direct in the quest** ✅✅ | Quest-spawned, repeatable (storyteller; `minRefireDays 30`, `expireDaysRange 4~8`, gated on `BasicGravtech` research) |
| 12 | `OrbitalAncientPlatform` | SitePartDef (`ParentName="SpaceGravcoreLocationBase"`) + GenStepDef | `GenStep_OrbitalPlatform`, `<factionDef>AncientsHostile</factionDef>`, layout `OrbitalAncientPlatform` (contains `OrbitalStoreroom_GravshipUpgrade` guaranteed 1) | **hardcoded `Faction.OfAncientsHostile`** in `QuestNode_Root_Gravcore_OrbitalAncientPlatform` | `<factionDef>` XML | **XML-partial** ⚠️ (map pawns rebindable, world-object owner is not) | `AncientSealedContainer_GravshipUpgrade` → `Reward_GravshipUpgrade`; `AncientSealedCrate_Gravlite` → `Reward_AncientSealedCrateBase_Gravlite`. Quest reward `Reward_DefinedThingDef(Gravcore)` + `(GravlitePanel)` **hardcoded C#** | **Map loot: Prefab/LootSpawn ✅ / Quest reward: C#-hard ⚠️** | One-shot (gravcore chain, `requiredSubquestsGiven: 3`) |
| 13 | `OrbitalMechanoidPlatform` | SitePartDef (`ParentName="SpaceGravcoreLocationBase"`) + GenStepDef | `GenStep_OrbitalPlatform`, `<factionDef>Mechanoid</factionDef>`, layout `OrbitalMechanoidPlatform` (contains `MechGravlitePanelRoom`) | **hardcoded `null`** in `QuestNode_Root_Gravcore_OrbitalMechanoidPlatform` | `<factionDef>` XML | **XML-partial** ⚠️ | quest reward `Gravcore` + `GravlitePanel` **hardcoded C#**; map loot via `MechGravlitePanelRoom` prefabs | **Map loot: Prefab ✅ / Quest reward: C#-hard ⚠️** | One-shot (gravcore chain) |

### Odyssey — orbit-layer maps that are NOT POIs
| defName | Type | Note |
|---|---|---|
| `Space` | WorldObjectDef | Generic in-transit / pocket space map. `canResizeToGravship`. |
| `SpacePocket` | MapGeneratorDef | Pocket-map variant of `Space`. |
| `OrbitalRelay` | MapGeneratorDef + GenStepDef | `validScenarioMap=true`; used by `ScenPart_ForcedMap` (Odyssey `Scenarios.xml`, and BTG's Exiled Traders scenario). Not a world object. |
| `Opportunity_SurveySite` | SitePartDef + GenStepDef | Surface-only (`QuestNode_Root_Site` `<layerWhitelist><li>Surface</li>`), reward `Reward_GravshipUpgrade`. **Convertible in one line to `Orbit`** but its `worldObjectDef` is `ClaimableSite` (mapGenerator `Base_Player`), so viability in vacuum is **UNCONFIRMED**. |

### Odyssey orbit factions (the rebind substrate)
| FactionDef | `layerWhitelist` | `permanentEnemy` | Notes |
|---|---|---|---|
| `TradersGuild` | `Orbit` | no | `settlementGenerationWeight 1`, `requiredCountAtGameStart 1`, `canGenerateQuestSites false` |
| `Salvagers` | `Orbit` | **yes** | `hidden true`, `settlementGenerationWeight 1`, spacer tech, used by `GenStep_SitePawns` on #10 and `factionDef` on #11 |
| `Archinity_Glitterites` *(local mod)* | `Orbit` | **yes** | `settlementGenerationWeight 1.2`, `hiddenIdeo true` — **already the intended custom hostile orbit faction** |

Confirmed mechanism (`FactionGenerator`, decompiled):
```csharp
if (!f.layerWhitelist.NullOrEmpty() || !layer.IsRootSurface)
    return f.layerWhitelist.Contains(layer.Def);
...
Faction faction = source.RandomElementByWeight(x => x.def.settlementGenerationWeight);
```
So orbital settlement ownership is 100% FactionDef-XML driven — no patch needed to *add* a faction to orbit.

---

## 2. Vanilla Gravship Expanded – Chapter 1 (`vanillaexpanded.gravship`, 3609835606) — 11 space POIs

All under `...\294100\3609835606\1.6\Defs\`.

| # | defName | Def type | Map generator / GenStep class | Faction | Faction rebindable? | Loot | Loot patchable? | Lifecycle |
|---|---|---|---|---|---|---|---|---|
| 14 | `VGE_IceAsteroid` | WorldObjectDef (`ParentName="GeneratedAsteroid"`) + GeneratedLocationDef (`layerDefs: Orbit`) | `VGE_IceAsteroid` → `VanillaGravshipExpanded.GenStep_IceAsteroid`; `worldObjectClass VanillaGravshipExpanded.IceAsteroidMapParent` | **none** | **C#-hard** (no faction plumbing) | `<mineableCounts>` + vanilla `Ancient*_Asteroid` scatterers | **Mineables** | Permanent worldgen |
| 15 | `VGE_AsteroidCluster` | same | `GenStep_AsteroidCluster` | none | C#-hard | mineableCounts | Mineables | Permanent worldgen |
| 16 | `VGE_AsteroidField` | same | `GenStep_AsteroidField` | none | C#-hard | mineableCounts | Mineables | Permanent worldgen |
| 17 | `VGE_PorousAsteroid` | same | `GenStep_PorousAsteroid` | none | C#-hard | mineableCounts | Mineables | Permanent worldgen |
| 18 | `VGE_GiantAsteroid` | same | `GenStep_GiantAsteroid` | none | C#-hard | mineableCounts | Mineables | Permanent worldgen |
| 19 | `VGE_ShatteredAsteroid` | same | `GenStep_ShatteredAsteroid` | none | C#-hard | mineableCounts | Mineables | Permanent worldgen |
| 20 | `VGE_DenseAsteroid` | same | `GenStep_DenseAsteroid` | none | C#-hard | mineableCounts | Mineables | Permanent worldgen |
| 21 | `VGE_SmallAsteroid` | same | `GenStep_SmallAsteroid` | none | C#-hard | mineableCounts | Mineables | Permanent worldgen |
| 22 | `VGE_AsteroidWithRuins` | same | `GenStep_AsteroidWithRuins` **plus** the `VGE_DerelictStation` GenStep in the same mapGenerator | inherits #23's `<factionDef>` for the station portion | **XML-full** for the station portion | mineables + station rooms | Mineables + Prefab | Permanent worldgen |
| 23 | `VGE_DerelictStation` | WorldObjectDef (`ParentName="GeneratedAsteroid"`) + GeneratedLocationDef | `VGE_DerelictStation` → `VanillaGravshipExpanded.GenStep_AncientOrbitalPlatform : GenStep_OrbitalPlatform`, **`<factionDef>AncientsHostile</factionDef>`**, `<layoutDef>VGE_DerelictStation</layoutDef>`, terrain `VGE_AncientOrbitalPlatform`, debris `VGE_MixedDebris`, exterior `CrashedShuttle 0~1` / `BaricadeTurret 2~5` | XML `<factionDef>` | **XML-full** ✅ (only faction-bearing VGE POI) | Layout `VGE_DerelictStation` (`ParentName="OrbitalAncientPlatformBase"`) → rooms `AncientCryptosleepRoom_Hostile_Deserted`, `RecRoom_Deserted`, `OrbitalNursery_Deserted`, **`OrbitalStoreroom_Loot`** (vanilla → `AncientSealedCrate` → `MapGen_HighValueCrate`), `VGE_OrbitalHydroponics` | **Prefab/LootSpawn → ThingSetMaker** ✅ | **Permanent worldgen** (no quest, no timeout) |
| 24 | `VGE_CoreAsteroidMiningSite` | WorldObjectDef (`ParentName="ClaimableSpace"`, `ResourceAsteroidMapParent`) | `VGE_CoreAsteroidMiningSite` → `VanillaGravshipExpanded.GenStep_CoreAsteroid : GenStep_Asteroid`, `numChunks 60~100` | **none** ("You detect no signs of life") | C#-hard | `<mineables>` in the quest: `VGE_Compressed_Steel/_Silver/_Gold/_Uranium/_Plasteel/_Jade` | **Mineables** | Quest-spawned, repeatable (`VGE_OpportunitySite_SolidCoreAsteroid`, `givenBy: OrbitalScanner`) |

**No `ThingSetMakerDef` exists anywhere in VGE's space content.** Its only ThingSetMaker touches are `Patches/Uncraftables.xml` editing vanilla `Reward_GravshipUpgrade` / `Reward_AncientSealedContainer`.

**VGE density lever (important for "more reasons to explore"):** VGE transpiles `WorldComponent_LocationGenerator.GenerateUntilTarget` and `.WorldComponentTick` with
`generatedLocationFactor * worldLocationsTarget * GravshipsMod_Settings.orbitalObjectsMultiplier` — a mod-settings slider that scales *all* `GeneratedLocationDef` orbit spawns, vanilla `AsteroidBasic` included.

**VGE patches on Odyssey space defs:** `Patches/SpaceBaseAbandon.xml` adds `WorldObjectCompProperties_Abandon` to the vanilla abstract `WorldObjectDef[@Name="SpaceBase"]`. Nothing else in VGE touches `ClaimableSpaceSite`, `Mechhive`, `SpaceSettlement`, or any `Opportunity_*` in XML.

Non-POI VGE world objects: `VGE_ArtilleryProjectile` (travelling shot), `VGE_GravshipGenerationSite` (texture-render scratch map), `VGE_MechOrbitalDestroyer_Alpha/Beta/Gamma` (KCSG layouts placed into the `TheGravship` starting map by `ScenPart_SpawnMechDestroyers`).

---

## 3. Better Traders Guild (`shunter.bettertradersguild`, 3684587591) — 0 own POIs, 3 orbit constructs

| defName | Def type | Detail | Faction | Rebindable? | Loot |
|---|---|---|---|---|---|
| `BTG_SettlementMapGenerator` + `BTG_SettlementPlatform` (GenStepDef) + `BTG_SettlementPlatform` (StructureLayoutDef) | MapGeneratorDef / GenStepDef / StructureLayoutDef | Replaces vanilla `SettlementPlatform` mapgen **via Harmony patch on `MapParent.MapGeneratorDef`, keyed on the TradersGuild faction** (namespaces `BetterTradersGuild.Patches.MapParentPatches` / `SettlementPatches`). GenStep is vanilla `GenStep_OrbitalPlatform` with `useSiteFaction=true`. Layout worker `BetterTradersGuild.LayoutWorkers.Settlement.LayoutWorker_Settlement` | C# (faction-keyed, not defName-keyed) | **C#-hard** ⚠️ — a rival orbit faction will *not* get BTG's platform layout | `BTG_SettlementPawnsLoot` sets **`<lootMarketValue>0~0</lootMarketValue>` — loot deliberately disabled**. Rooms are prefab + `roomContentsWorkerType` driven. **Zero ThingSetMakerDefs in the whole mod.** |
| `BTG_CargoVaultMapGenerator` / `BTG_OrbitalCargoVault` / `BTG_CargoVaultRoom` | MapGeneratorDef (pocket, `biome: Orbit`) + StructureLayoutDef + LayoutRoomDef | Sub-map reached via `BTG_CargoVaultHatch` inside a settlement shuttle bay. Not a standalone world POI | inherits | — | prefabs + `RoomContents_CargoVault` C#; threat `WaspDrone 0~1` |
| `BTG_ExiledTraders` | ScenarioDef | `ScenPart_PlanetLayer <layer>Orbit</layer>` + `ScenPart_ForcedMap <mapGenerator>OrbitalRelay</mapGenerator>`; player faction `BTG_IndependentTraders` | XML | XML | hardcoded `ScenPart_StartingThing_Defined` |
| — | Patch | `Patches/WorldObjects_SpaceSettlement.xml` adds `WorldObjectCompProperties_TradeRequest` to `WorldObjectDef[defName="SpaceSettlement"]` — **the one worked example of vanilla `SpaceSettlement` being patched by defName** | — | — | — |
| `BTG_TradeRequest` | QuestScriptDef | `everAcceptableInSpace=true`; spawns **no** world object, targets an existing settlement via `QuestNode_GetNearestTGSettlement` | — | — | — |

---

## 4. Active mods with NO space POIs (verified)

| Mod | packageId | Finding |
|---|---|---|
| GravTech | `als.gravtech` (3545374124) | One WorldObjectDef, `World_GravCapsule` (travelling shuttle). No SitePartDef / QuestScriptDef / GenStepDef / MapGeneratorDef / GeneratedLocationDef at all. `AsteroidCollector` is a building. |
| Biotech for Gravship | `als.biotechgravship` (3722358861) | Zero defs of any POI type. `BiotechForGravship.dll` has no GenStep/WorldObject/SitePart/Asteroid/Orbital symbols. |
| Vanilla Expanded Framework | `OskarPotocki.VanillaFactionsExpanded.Core` (2023507013) | No `PlanetLayerDef`, no `layerDef`, no `planetLayer` in any XML. World defs are `KCSG_UndergroundRoom`, `OutpostBase`, `KCSG_EnnemiesPresence` — all surface/pocket. |
| Vanilla Quests Expanded – Ancients | `vanillaquestsexpanded.ancients` (3618306875) | 6 SitePartDefs (`VQEA_AncientLabComplexSite`, `VQEA_ArchiteControlVaultSite`, `VQEA_SpliceframeBlacksiteSite`, `VQEA_InhibitorResearchLabSite`, `VQEA_ArchiteArraySite`, `VQEA_AncientResearchVaultSite`), all underground/surface. **Not one `everAcceptableInSpace` or `canOccurOnAllPlanetLayers` in the entire mod** — would need those flags before relocation is even possible. Loot: `VQEA_AncientOrganBox` ThingSetMakerDef. |
| Ushankas Glittertech Expansion | `Ushanka.GlittertechExpansion` (3522676478) | 2 SitePartDefs (`USH_GlittertechOutpost`, `USH_GlittertechFacility`), surface, `KCSG.GenStep_CustomStructureGen`. **Both quests carry `canOccurOnAllPlanetLayers` + `everAcceptableInSpace`** — layer-permissive already. Faction set by quest slate `siteFaction` (XML), loot via `USH_RewardGlittercrate` ThingSetMakerDef on the `USH_Glittercrate` building's `<contents>`. Already rebound to `Archinity_Glitterites` by `Archinity.Glitterites/Patches/Glittertech_FactionRebind.xml`. |
| Vehicle Framework | `SmashPhil.VehicleFramework` (3014915404) | `Compatibility/Odyssey/Patches/SpaceObjects.xml` — pure `PatchOperationAddModExtension` adding `Vehicles.SpaceObjectDefModExtension` to `Gravship` and to `@Name = "SpaceBase" or "SpaceSite" or "GeneratedAsteroid"`. Defines no POIs. |
| Alpha Mechs, VFE Spacer, VFE Pirates, all other active mods | — | Global grep across all 64 workshop mods for `GenStep_OrbitalPlatform`, `GenStep_OrbitalWreck`, `GenStep_OrbitalSatellite`, `ParentName="ClaimableSpace"`, `<mapGenerator>Space/Asteroid/Mechhive/OrbitalItemStash`, `requiresSignalJammerToReach`, `PlanetLayerDef`, `<layer>Orbit` returned only the mods listed above. |

**Grep note for future work:** the Odyssey abstracts are declared `Name="SpaceBase"` / `Name="SpaceSite"` / `Name="GeneratedAsteroid"` / `Name="ClaimableSpace"` / `Name="SpaceSiteBase"` (SitePartDef). Searching `ParentName="SpaceSite"` will always miss the declarations.

---

## 5. Cross-cutting: how loot actually resolves on orbital platforms

The chain is fully XML at every hop:

```
StructureLayoutDef  ─ roomDefs ─▶  LayoutRoomDef
                                     ├─ <thingSetMakerDef>   (direct)   e.g. OrbitalItemStash_ItemRoom → MapGen_OrbitalItemStash
                                     └─ <prefabs>            (indirect) e.g. OrbitalStoreroom_Loot → AncientSealedCrate
                                                                          │
                                        PrefabDef ─▶ ThingDef ─ comps ─▶ CompProperties_LootSpawn
                                                                            └─ <contents>ThingSetMakerDef</contents>
```

Confirmed `CompProperties_LootSpawn` bindings (all patchable by defName):

| Container ThingDef | `<contents>` ThingSetMakerDef |
|---|---|
| `AncientSealedCrate` | `MapGen_HighValueCrate` |
| `AncientSealedCrate_Gravlite` | `Reward_AncientSealedCrateBase_Gravlite` |
| `AncientSealedCrate_Shells` | `Reward_AncientSealedCrate_Shells` |
| `AncientSealedContainer` | `Reward_AncientSealedContainer` |
| `AncientSealedContainer_GravshipUpgrade` | `Reward_GravshipUpgrade` |
| `AncientPallet_SteelSlag` | `Reward_AncientPallet_SteelSlag` |
| *(room-level)* `OrbitalItemStash_ItemRoom` | `MapGen_OrbitalItemStash` |
| *(room-part)* `OrbitalRuinsHermeticCrate` | `MapGen_ScarlandsHermeticCrate` |

`Reward_GravshipUpgrade` currently rolls: `FuelOptimizer` (w1), `GravshipShieldGenerator` (w1), `PilotSubpersonaCore` (w1), `Gravcore` (w0.75).

**Two tech-gating strategies, both pure XML:**
1. **Narrow** — define a new `ThingSetMakerDef` (e.g. `Archinity_OrbitTechCache`) and `PatchOperationReplace` a specific container's `<contents>`, or add a new sealed-container ThingDef + PrefabDef and inject it into one LayoutRoomDef's `<prefabs>`. Keeps vanilla crates vanilla.
2. **Broad** — `PatchOperationAdd` your tech items into `MapGen_HighValueCrate` / `Reward_GravshipUpgrade`. One patch, hits every orbital platform at once, but also leaks into surface ancient ruins that share `MapGen_HighValueCrate`.

---

## 6. Ranked rebinding candidates

| Rank | defName | Why | Patch surface |
|---|---|---|---|
| 1 | `Opportunity_OrbitalWreck` | Two independent XML faction knobs: `GenStep_OrbitalWreck.<factionDef>` (structure owner) **and** a dedicated `GenStep_SitePawns` GenStepDef `Opportunity_OrbitalWreck_Salvagers` with `<factionDef>Salvagers</factionDef>` + `<letterLabel>`/`<letterDesc>`. Live hostile squad already separated into its own patchable def. Repeatable, OrbitalScanner-driven. | `GenStepDef[Opportunity_OrbitalWreck]/genStep/factionDef`, `GenStepDef[Opportunity_OrbitalWreck_Salvagers]/genStep/factionDef`, `QuestScriptDef[OpportunitySite_OrbitalWreck]//li[@Class="QuestNode_Root_Site"]` ← add `<factionDef>` |
| 2 | `Opportunity_AbandonedPlatform` | Highest-frequency repeatable orbital platform (`rootSelectionWeight 1`). Full `GenStep_OrbitalPlatform` with XML faction + XML layoutDef. Loot rooms include a 0.1-weight `OrbitalStoreroom_GravshipUpgrade` — a ready-made rare-tech slot. | same three hooks as above + `StructureLayoutDef[Opportunity_AbandonedPlatform]/roomDefs` |
| 3 | `OrbitalFugitivePlatform` | Already bound to a **hostile spacer faction** (`Salvagers`) rather than `AncientsHostile`, and its reward is a literal `<thingSetMaker>Reward_GravshipUpgrade</thingSetMaker>` inside the quest — swap that one element for a custom ThingSetMakerDef and you have a clean tech-gated bounty. Research-gated on `BasicGravtech`, `minRefireDays 30`. | `GenStepDef[OrbitalFugitivePlatform]/genStep/factionDef`, `QuestScriptDef[OrbitalFugitive]//li[@Class="QuestNode_GenerateThingSet"]/thingSetMaker` |
| 4 | `OpportunitySite_Satellite` | XML faction + XML layout, and its two loot rooms are the *only* orbital rooms driven by `AncientSealedContainer` → `Reward_AncientSealedContainer`, so retargeting that container affects satellites without touching platform crates. `spawnSentryDrones=true` gives free defenders. | `GenStepDef[OpportunitySite_Satellite]/genStep/factionDef`, `ThingDef[AncientSealedContainer]/comps/li[@Class="CompProperties_LootSpawn"]/contents` |
| 5 | `SpaceSettlement` | Not a patch at all — **any FactionDef with `<layerWhitelist><li>Orbit</li></layerWhitelist>` and a `settlementGenerationWeight` gets permanent orbital settlements for free.** `Archinity_Glitterites` already has both. Loot is patchable two ways (`GenStepDef[SettlementPawnsLoot]/genStep/lootThingSetMaker`, or add `<settlementLootMaker>` to the FactionDef — no vanilla faction sets it). Downside: BTG's Harmony layout swap is TradersGuild-keyed, so a rival faction gets vanilla `OrbitalSettlementPlatform`. | FactionDef only, + one optional GenStepDef edit |
| 6 | `VGE_DerelictStation` | Permanent worldgen (no quest, no expiry), density scaled by VGE's `orbitalObjectsMultiplier` slider, XML `<factionDef>AncientsHostile</factionDef>`, and its layout already pulls vanilla `OrbitalStoreroom_Loot`. The only *always-there* faction-owned structure in orbit. | `GenStepDef[VGE_DerelictStation]/genStep/factionDef`, `StructureLayoutDef[VGE_DerelictStation]/roomDefs` |

---

## 7. Hardcoded / unpatchable — flagged

| defName | What's hardcoded | Where |
|---|---|---|
| `Mechhive` / `OrbitalMechhive` | `GenStep_OrbitalMechhive`: `protected override Faction Faction => Faction.OfMechanoids;` and `protected override LayoutDef LayoutDef => LayoutDefOf.Mechhive;`. Quest node passes site faction `null`. Reward is `Reward_Unknown()` + `SketchResolverDefOf.CerebrexCore`. | `RimWorld.GenStep_OrbitalMechhive`, `RimWorld.QuestGen.QuestNode_Root_Gravcore_Mechhive` |
| `OrbitalItemStash` | `GenStep_AsteroidItemStash`: layout pinned to `LayoutDefOf.OrbitalItemStash`, `worker.Spawn(..., null, allSpawnedThings)` — faction argument is a literal `null`. **Loot is still XML-patchable** via `MapGen_OrbitalItemStash`. | `RimWorld.GenStep_AsteroidItemStash` |
| `OrbitalAncientPlatform` | World-object owner pinned: `QuestGen_Sites.GenerateSite(..., Faction.OfAncientsHostile, ...)`. Quest reward pinned: `Reward_DefinedThingDef(ThingDefOf.Gravcore)` + `(ThingDefOf.GravlitePanel)`. Map-gen faction *is* XML. | `RimWorld.QuestGen.QuestNode_Root_Gravcore_OrbitalAncientPlatform` |
| `OrbitalMechanoidPlatform` | World-object owner pinned to `null`; quest reward pinned to Gravcore + GravlitePanel. Map-gen faction *is* XML. | `RimWorld.QuestGen.QuestNode_Root_Gravcore_OrbitalMechanoidPlatform` |
| `AsteroidMiningSite`, `AsteroidBasic`, `OrbitalItemStash`, all 11 VGE asteroids | `QuestNode_Root_Asteroid` / `GeneratedLocationDef` construct a bare `SpaceMapParent` and never touch faction. There is no faction field to patch. | `RimWorld.QuestGen.QuestNode_Root_Asteroid` |
| BTG orbital settlements | Layout/mapgen swap is a Harmony patch on `MapParent.MapGeneratorDef` keyed on the TradersGuild faction; the literal string `SpaceSettlement` does not appear in the DLL. Cannot be redirected to another faction via XML. | `BetterTradersGuild.Patches.MapParentPatches` |
| BTG settlement loot | `BTG_SettlementPawnsLoot` sets `<lootMarketValue>0~0</lootMarketValue>`. No ThingSetMakerDef exists in the mod. Loot is prefab + `roomContentsWorkerType` only. | `...\3684587591\1.6\Defs\GenStepDefs\SettlementPawnsLoot.xml` |
| VGE space loot | No ThingSetMakerDef anywhere in VGE's space content — everything is `<mineableCounts>` or prefab. | `...\3609835606\1.6\Defs\MapGeneration\SpaceMapGenerator.xml` |

---

## 8. Known vanilla oddity worth flagging

`QuestScriptDef[OpportunitySite_MechanoidPlatform]` opens with:
```xml
<li Class="QuestNode_FactionExists">
  <faction>Insect</faction>
</li>
```
An orbital **mechanoid** platform gated on the **insect** faction existing. Almost certainly a copy-paste from a gravcore/megahive script. If insects are disabled in worldgen, this POI never fires. One-line `PatchOperationReplace` to `Mechanoid` (or removal) restores it.

---

## 9. Inactive-but-subscribed — notable

Nothing found. The global workshop grep (all 64 subscribed mods, XML only, for every orbit/space token) returned hits **only** in mods that are already active: 3609835606 (VGE Ch.1), 3684587591 (BTG), 3014915404 (Vehicle Framework), 3309003431 (VFE Insectoids 2 — a `PlanetLayerDef defName="Surface"` xpath reference in `Patches/InsectWorldLayer.xml`, inactive, and surface-only anyway).

---

## 10. Totals

| Source | Distinct space POIs |
|---|---|
| Odyssey | **13** |
| Vanilla Gravship Expanded – Ch.1 | **11** |
| Better Traders Guild | **0** (reskins Odyssey `SpaceSettlement`; adds 1 pocket sub-map + 1 scenario) |
| GravTech / Biotech for Gravship / VEF / VQE-Ancients / Ushanka / all other active mods | **0** |
| **Total** | **24** |

Of the 24: **9 are XML-full faction-rebindable** (#7–11 Odyssey, #23 VGE, plus `SpaceSettlement` via FactionDef and `OrbitalAncientPlatform`/`OrbitalMechanoidPlatform` partially). **13 have a patchable ThingSetMaker or prefab-LootSpawn loot path.** **11 are unfactionable asteroids** whose only lever is `<mineableCounts>`.
