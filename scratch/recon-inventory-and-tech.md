# Recon: mod inventory + verified technical answers

Generated 2026-08-22. Two agent passes condensed.

---

# PART 1 — What we have built

| Mod | Contents | Assembly | Status |
|---|---|---|---|
| `archinity.origins` | 1 XenotypeDef (Archonian Sanguophage), 1 ScenarioDef ("Seed of Archinity"). 2 files, no patches. | no | Loaded, working |
| `archinity.pacing` | 1 ManualAnalysisDef; 7 patch files / 10 Operations (8 Remove, 6 Replace, 2 Add, 1 Sequence, 3 FindMod guards). Orbit layer size + subdivisions 5->6, VRE_Archon earliestRaidDays, VQEA injection blacklist, MRR SecurityDoor orphan fix, Alpha Mechs player lockout (26 recipes / 11 buildings / 8 apparel), Medieval retier of DrugProduction chain. | no | Loaded |
| `archinity.drifters` | Starjack Free Companies — neutral, hostile-capable, orbit-only. 1 FactionDef, 1 ThingSetMakerDef, 10 PawnKindDefs, 2 RulePackDefs, 1 placeholder icon. | no | Loads clean, **never through worldgen** |
| `archinity.glitterites` | Ultra-tech permanent enemy in orbit. 1 FactionDef, 2 ThingSetMakerDefs, 5 PawnKindDefs, 1 PrefabDef, 2 RulePackDefs, **18 ManualAnalysisDefs** gating glittertech behind `USH_Glitterheart`. 5 patch files / 21 ops. Rebinds Ushanka quests/pawnkinds off `AncientsHostile`, moves glitterheart drops to orbital loot. | no | Loads clean, **never through worldgen** |
| `archinity.altar` | 4 ThingDefs (1 building, 3 gene vectors), 2 HediffDefs, 1 JobDef, 2 WorkGiverDefs, 1 `GenePoolDef` w/ 50 gene entries, 16 keyed strings. | **YES** — `ArchinityAltar.dll`, 25 KB, 952 LOC / 5 .cs, HarmonyLib | **NOT IN LOAD ORDER. Has never loaded in game.** |

### Altar C# surface (the only assembly — keep it that way)
- `Patches.cs` — Harmony id `archinity.altar`, `PatchAll` from `[StaticConstructorOnStartup]`.
  - Startup: reflects VRE-Archon's `blockedWeapons` static HashSet, copies it out and **clears it**. try/catch, soft dependency.
  - Startup: warns on archite genes missing from `Archinity_ArchitePool`.
  - Postfix `EquipmentUtility.CanEquip` (Priority.Last) — re-gates stolen equipment on `pool.archonEquipmentGene` instead of `VRE_Transcendent`.
  - Postfix `GeneUtility.ReimplantXenogerm` — strips `founderOnlyGenes`, adds `conversionAddsGenes` as xenogenes.
- `GenePool.cs` — `GenePoolDef : Def`, `GenePoolEntry` (gene/tier/category/reserved), `Available()`, `MissingArchiteGenes()`, `GeneCategory`.
- `AltarData.cs` — `ArchinityDefOf`, `GeneVectorExtension`, `AltarFacilityExtension`, `AltarModifiers`.
- `Building_Altar.cs` — `Building_Enterable, IThingHolderWithDrawnPawn`; 7500-tick drain. **No custom gizmos — deliberate**, so Multiplayer syncs via vanilla `EnterBuilding`/`CarryToBuilding`.
- `WorkGivers.cs` — `WorkGiver_CarryToAltar`, `WorkGiver_LoadAltar`, `JobDriver_LoadAltar`.

### Active load order — 62 entries, `config/ModsConfig.xml` v1.6.4871
```
zetrith.prepatcher / brrainz.harmony / ludeon.rimworld (+royalty, ideology, biotech, odyssey)
smashphil.vehicleframework / edb.preparecarefully / mehni.pickupandhaul / rwmt.multiplayer
adaptive.storage.framework
oskarpotocki.vanillafactionsexpanded.core / vanillaexpanded.vfecore
vanillaexpanded.vfefarming / vfemedical / vfesecurity / vfeproduction
rabiosus.takecover / willworkforicecream.noalzheimers / kangel.moisture / bart.app
frozensnowfox.filthvanisheswithrainandtime
sbz.neatstoragefridge / sbz.gravshipstorage / sbz.neatstorage
vanillaexpanded.vfepower / vchemfuele
wiri.compositableloadouts / vanillaexpanded.vaeaccessories
oskarpotocki.vfe.pirates / vanillaexpanded.vnutriente
vanillaquestsexpanded.ancients
oskarpotocki.vanillavehiclesexpanded / vanillaexpanded.vwenl / ...upgrades
vanillaracesexpanded.sanguophage / waster / saurid
oskarpotocki.vanillafactionsexpanded.settlersmodule
ushanka.glittertechexpansion
fridgebaron.techblock
memegoddess.replacestuff
sae.researchmod            <- More Research Requirements
dame.ignorance             <- Ignorance Is Bliss
vanillaexpanded.gravship / als.gravtech
sarg.alphamechs / vanillaexpanded.vfespacer
shunter.bettertradersguild
als.biotechgravship
azravos.factioncustomizer
oskarpotocki.vfe.classical / oskarpotocki.vfe.medieval2
vanillaracesexpanded.archon / hussar / starjack
bs.xenotypespawncontrol
archinity.origins / pacing / drifters / glitterites
```

### ModSettings snapshot
- `TechBlockMod` — all eight `requiredPoints*` at 0.75, override on. Base costs Neo/Med 500, Ind 1000, Spacer 2000, Ultra 4000, Archotech 8000. Random-insight rate 1.
- `IgnoranceMod` — `changeQuests` on, `useActualTechLevel` on, `usePercentResearched` off.

### FLAGS
1. **`archinity.altar` is not in the load order.** Everything in QUESTLINE.md depends on it.
2. **Medieval Overhaul is NOT installed.** Route A ("enable MO and strip it") was decided in session 4, but no `DankPyon` mod is in `ModsConfig.xml`. Only VFE Medieval 2 is active. Route A is undelivered.
3. **VFE Tribals is NOT installed** and is not in the load order — despite the Progression Ideology treating it as the foundation of the whole Neolithic design.
4. `README.md` is stale — claims "XML defs only, no C#", omits `Archinity.Altar`, lists nonexistent `Archinity.Chronicle`.
5. `AltarFacilityExtension` applied to zero defs — the 12 intended facilities do nothing; crit-failure is a flat 25% forever.
6. Nothing has been through worldgen. Glitterheart drop unconfirmed.
7. Both faction icons are generated placeholders.
8. All four DLCs listed twice in ModsConfig; configs must match byte-for-byte between MP players.

---

# PART 2 — Verified technical facts
`[V]` verified against decompiled 1.6 source · `[?]` unknown / not covered

## Storyteller
- `[?]` Custom `StorytellerDef`, incident volume, threat scaling, population pressure — **not covered anywhere in our corpus.**
- `[V]` `StorytellerUtility.GetProgressScore = freeColonistCount*1 + PlayerWealthForStoryteller*0.0001`. Research contributes nothing.
- `[V]` VEF's whole storyteller surface: `QuestChainExtension`, `GameComponent_QuestChains`, `QuestNode_GetFaction`, `QuestNode_Site`, 3 Harmony patches.

## Quests / incidents
- `[V]` `rootSelectionWeight 0` = give-only; storyteller cannot pick it.
- `[V]` `QuestScriptDef.CanQuestOccurOnTile` reads `layerWhitelist`/`layerBlacklist`/`everAcceptableInSpace`/`neverPossibleInSpace` against the **player's** tile, not the site's.
- `[V]` VEF `QuestChainExtension.requiredResearch` blocks `TryScheduleQuest` — the only verified tech gate on quest appearance.
- `[V]` Ignorance Is Bliss `changeQuests` only swaps the threat faction; it never suppresses.
- `[?]` `minRefireDays`, root-selection weighting internals, generic third-party quest suppression.
- `[V]` Fixed rewards: `QuestNode_SetItemStashContents` (shipped, Royalty `Script_Intro_Deserter.xml:90`). `QuestNode_GenerateThing` + `QuestNode_AddItemsReward` verified in code, no shipped XML — **bypasses ThingSetMaker filters, budgets, techprint and PlayerAcquirable gates.** Must nest under a signal node or it drops on accept; needs `slate["map"]`; `stackCount` unclamped vs `stackLimit`; non-stuffable only.
- `[V]` No `ThingSetMaker_Fixed`. Only `_Count`/`_StackCount` are deterministic. `QuestNode_GiveRewards` can never be fixed.

## Factions
- `[V]` **`requiredCountAtGameStart` is dead code in 1.6** — `InitializeFactions` early-returns when factions != null. Real levers: `maxConfigurableAtWorldCreation` (0 = never), `startingCountAtWorldCreation`, `displayInFactionSelection`.
- `[?]` `configurationListOrderPriority`.
- `[V]` Orbit placement: `layerWhitelist` / `arrivalLayerWhitelist` / `neutralArrivalLayerBlacklist`. Settlement owner = `RandomElementByWeight(settlementGenerationWeight)`. `settlementWorldObjectDef` lives on `PlanetLayerDef`.
- `[V]` `hidden` + `permanentEnemy` pattern = Odyssey `Salvagers`.
- `[V]` Raid faction choice has **no tech weighting**. Empty pool fails open and silent.
- `[?]` What gear raiders carry; `pawnGroupMakers` internals; apparel/weapon tags.
- `[?]` `TraderKindDef` / `stockGenerator` structure.
- `[?]` Guaranteed base-raid drops. Orbit-only analogue that IS known: `LayoutRoomDef.thingSetMakerDef` and prefab -> `CompProperties_LootSpawn.contents`, both XML-patchable.
- `[V]` Settlement layouts: KCSG `CustomGenOption` in FactionDef `modExtensions` (VFEM2 precedent). `GetModExtension` returns the FIRST — never add a second. Missing `centralBuildingTags` tag throws `KeyNotFoundException` mid-worldgen. `count` is a soft target. `defenseOptions` turrets/mortars require `techLevel >= Industrial`. Garrison = `faction.pawnGroupMakers` x `pawnGroupMultiplier`. Layouts can place pawns. Every modded ThingDef needs a hand-written SymbolDef. `_North/_East/...` variants are runtime, unpatchable. In-game exporter: Architect -> Orders -> Export.

## Research
- `[V]` `requiredResearchBuilding` / `requiredResearchFacilities` gate the **research bench only**, never a forge. VEF `ResearchBuildingExtension.equivalentBenches`/`equivalentFacilities` loosens both.
- `[V]` `rootMinProgressScore` ignores research entirely (see progress-score formula).
- `[V]` Requiring/consuming a specific ITEM: **no vanilla XML field exists.** Two known routes — MO's `RequiredSchematic` modExtension + `CanBeResearchedAt` postfix (C#, and carries an unkeyed 250-tick cache = a real desync bug), and MRR `ManualAnalysisDef` study counts.
- `[?]` Techprints. `techLevel` / `tab` / `researchViewX/Y` / custom `ResearchTabDef`.
- `[V]` `baseCost` x `CostFactor` — confirmed only via TechBlock arithmetic.
- `[V]` Deleting a ResearchProjectDef **strips the prerequisite off its dependants**, leaving them buildable with no research. Neuter referencing defs first, delete research last.

## Tribal / Neolithic research mode
- `[?]` Tribal research bench mechanic, primitive-mode switch, whether research mode is locked at game start — **not covered.** (Separate agent pass running.)
- `[V]` TechBlock writes `ParentFaction.def.techLevel` only in `RecalculateBlockValues` — lags until save-load, no `FinishProject` patch. (Verified in source, unobserved in game; two agents disagreed.)
- `[V]` TechBlock def names are offset one tier from settings names.
- `[V]` MRR `BuildForProject` returns null for `techLevel <= Neolithic` and for Archotech. `Devilstrand` is a circular Neolithic deadlock.

## Tech level gating
- `[?]` Trader stock, quest-reward scaling, raider gear selection by `techLevel` — **not covered.**
- `[V]` Known consumers only: `SymbolResolver_EdgeDefenseCustomizable` (>= Industrial for turrets/mortars), MO `RaidStrategyWorker_MedievalSiege` (`== 3` + `FactionSiegeExtension`), IIB `FactionCanBeGroupSource` postfix reading `Faction.OfPlayer.def.techLevel`.
- `[V]` `QuestNode_GenerateThing` bypasses techprint / `PlayerAcquirable` gates entirely — a hard way to hand out out-of-tier items.

## Hard constraints / known-wrong assumptions
- `[V]` A RimWorld year is **60 days**, not 365.
- `[V]` **`RecipeDef` cannot be gated on a linked facility** — no field, no code path. The only soft XML gate is `workTableSpeedStat` / `workTableEfficiencyStat`.
- `[V]` **`CompProperties_Facility.statFactors` is a silent no-op.** Offsets only.
- `[V]` Blood-gating `VQEA_ArchogenInjector` is impossible in XML: unguarded `CompPowerTrader` deref -> per-tick NRE; `CompRefuelable` never read; `basePowerConsumption 0` fails; `ThingDefOf.ArchiteCapsule` hardcoded in 7 places.
- `[V]` Genepacks decay in 20 days. Roofs, shelves and `deteriorateFromEnvironmentalEffects` give zero protection; only a powered `GeneBank` (Industrial) stops it. Do not blanket-patch `Genepack` rate. Capsules and minified buildings never decay.
- `[V]` `--` inside an XML comment silently drops the whole file.
- `[V]` PatchOperations run **before** `ParentName` inheritance resolves, and apply to the whole merged database. Match on `@ParentName`.
- `[V]` MO `component_replace` hits 395 ThingDefs and is half-broken.
- `[V]` Glittertech sites cannot move to orbit — KCSG never paints a full floor.
- `[V]` Vanilla bug: `OpportunitySite_MechanoidPlatform` is gated on the **Insect** faction existing.
- `[V]` `Mech_Centipede` does not exist.
- `[V]` VFE Classical contributes **zero** Medieval research projects — all 18 are Neolithic. VISION.md is wrong.
