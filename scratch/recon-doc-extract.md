# Recon: extraction from HANDOFF / VISION / WORKLIST / DECISION-medieval-route

Source docs are considered largely stale. This file preserves only what is load-bearing.
Generated 2026-08-22.

## A) OPEN DECISIONS

- **Quest cadence -> then gene split**: how many archite genes leave the starting xenotype. Options: Conrad's "a few more upfront" vs. the proposed split. Cadence must be fixed first.
- **VFE Tribals**: VISION.md rejects it; `Player Progression Ideology.txt` calls it "the perfect start." Cannot both stand. Knock-on: `Progression: Core` SKIP verdict reopens if Tribals returns.
- **MO `woodChain` setting**: explicitly never ruled on. Same class of core change as `metalChain` (which is off).
- **`requiredPointsMedieval`**: 0.75 (~88 bench days) vs 1.0 (~117). Setting names are offset one tier from the gate.
- **RimFantasy**: enable minus the 4 temperature pylons + `RF_ArcaneTemperatureRegulation`? (`RF_FrostPylon` = -22 heat/s, no power cost, kills Electricity's value.)
- **`Faction - Elves`**: subscribed, unassessed. Rule against the no-race-bleeding principle.
- **Dark Ages: Medieval Tools**: recommended skip, not ruled.
- **Buy Anomaly?** Paid DLC; only "simulation/void" content available in the load order.
- **Neolithic storage**: author one (`sbzCrateBase` template, workshop `3416243474`) vs subscribe "Adaptive Primitive Storage."
- **Nice Research Tab**: does Conrad dislike node graphs generally, or just this mod's output? Determines graph-tuning vs list-based tab.
- **Two grape plants / two wine chains** (`DankPyon_Plant_Grape` vs `VFEM2_Plant_Grape`) - no compat patch anywhere.
- **Faction diplomacy + ideology pass** across the world map - flagged, untouched.
- **`HeavyBridges` (800) / `Piano` (2000) retier to Medieval** - clean, noted, not taken.
- **Orbit subdivisions 5->6->7** - pending worldgen-time data at 6.
- **Neolithic-tier siege**: can `RaidStrategyWorker_MedievalSiege`'s `techLevel == 3` check be satisfied without C#? Unverified.
- **KCSG perimeter risk**: Poisson-placed wall segments may not tile into a continuous wall. Untested.

## B) HARD DECISIONS ALREADY MADE

- **Route A: enable Medieval Overhaul and strip it** with `PatchOperationRemove`. Resolved session 4. *(HANDOFF.md still lists this as open - stale.)*
- **Electricity stays as the thing that ends the Medieval era**; Conrad declined removing it from `Machining` prereqs.
- **Only one C# assembly (`Archinity.Altar`)** - everything else XML-defs-only for MP safety. No second assembly without explicit decision.
- **Multiplayer mod, not RimWorld Together.**
- **One machine, one philosophy** - VQE injector as a rival path is dead.
- **Vanilla `ArchiteCapsule` only**; no new capsule types.
- **The recipient never dies at the altar** - non-negotiable.
- **`Deathrest` + `XenogermReimplanter` removed from starting xenotype**; both load-bearing. `Deathless` stays.
- **Beats gate on research completion, not day timers** (VEF postfixes `FinishProject`).
- **Vat + Galvanic Coil ship in the same beat**; vat yields altar charge, never electricity.
- **Vectors are quest-only** - no recipe, no trade tags, `thingSetMakerTags` cleared.
- **Endgame is orbit/gravship-as-main-base; `VRE_Transcendent` arrives as the final named vector.**
- **Glitterites are `permanentEnemy`** (not `naturalEnemy` - goodwill would soften).
- **Reskin VQE Ancients' 12 facilities rather than build new ones.**
- **No Vanilla Psycasts Expanded** -> VRE-Archon's psycaster path stays dormant, accepted.
- **Power gains carry no hunger cost** (`Archinity_ArchiteSustenance`).
- **Glittertech sites are NOT relocated to orbit** - KCSG cannot floor a space map.
- **Three-leap Medieval structure approved** (Forge ~5,100 / Mail+Siege ~12,400 / Plate+Powder ~13,400).
- **MRR availability rule locked**: 2-4 materials per requirement, >=1 craft/harvest, flavour item raider-sourced via `reverseEngineeringMaterials`, nothing ships under 2 routes.
- **Content/presentation pass happens after the Medieval route lands**, not before.
- **`USH_Glitterheart` is the canonical heart** - never duplicate it again.

## C) CONCRETE WORK ITEMS

### From HANDOFF.md
- Register `archinity.altar` in `ModsConfig.xml` - the def has never loaded.
- Remove the duplicate `ludeon.rimworld.odyssey` entry from `ModsConfig.xml`.
- Apply the agreed archoplate buff: Sharp->2.00, Blunt->~1.20, Heat->~1.50, shield energy 5.6->~20 + ~2x recharge; keep `disarmedByEmpForTicks`.
- Build `Archinity.Chronicle` (not started).
- Build the archite-capsule lottery selection window (the one genuinely desync-prone piece).
- Author remaining gene vectors alongside their beats.
- Verify: glitterheart actually drops; altar texture resolves from VQE Ancients; 12 facilities link; prisoner haul-and-drain works; vector grants its gene.
- Verify `VQEA_Electromagnetized` holds the archoplate shield through EMP - the whole Ultra-era reward rests on it.
- Re-snapshot `config/ModSettings/` after Conrad sets IIB `NumTechsAhead=0`, `NumTechsBehind=1`.
- Replace generated placeholder faction icons.
- Author `Book`-parented lore readables (near-zero exist in load order).
- Diagnose the orphan architect-menu entries (pipe-disassembly designators; check PipeSystem/VEF) before patching.

### From WORKLIST.md
- Fix the VISION.md sentence claiming VFE Classical carries the Medieval era - it contributes **zero** Medieval projects; all 18 are Neolithic.
- Apply `AltarFacilityExtension` to actual defs - it exists only in a comment, so crit-failure is a flat 25% forever.
- Fix both shipped vectors: `VQEA_PerfectVision`/`VQEA_PlasteelSkin` are already on the founders -> `AlreadyHasGene`; neither sets `requiresRecipientGene`, so only baseliners can use them.
- Allow non-`Humanlike` altar fuel (`CanAcceptPawn` currently blocks animals; VISION promises "several hundred animals").
- `DrainTicks = 7500` is 3h, not the documented ~2h - pick one and align.
- Make something actually spawn the altar (no quest, prefab, scatterer or ThingSetMaker references it).
- Add `neverBuildable` to the altar rather than relying on absent `designationCategory`/`costList`.
- Scenario hands `MeleeWeapon_Ikwa` with a Steel stuff tag at a Neolithic start.
- Place `VFEM2_Turret_WallMountedArbalest`/`_Arquebus` via two SymbolDefs - cheapest win available.
- Fix `DankPyon_Turret_Trebuchet` auto-manning (needs `Artillery_MannedMortar` buildingTag, or add a pawn symbol).
- Author `Archinity_CurtainWall` / `_CastleTower` / `_Gatehouse` as tagged `StructureLayoutDef`s; `PatchOperationAdd` into `VFEM2_MedievalFactionBase`. Use the KCSG dev-mode exporter. Est. 6-9 layouts, 4-6 sessions.
- Patch `FactionSiegeExtension.medievalSiege` + `ArtilleryMedieval_BaseDestroyer` onto VFEM2 factions; add `canSiege` (no VFEM2 faction sets it).
- Add research gates: `VFEM2_Apparel_PaddedArmor` (none at all), MO heraldic greathelm/hauberk variants, MO's 4 heater shields (no recipe, no research).
- Repoint `VFES_SiegeEquipment` behind `DankPyon_Engineering`; gate `VFEC_Scorpion` out of the Neolithic; split `PlateArmor`'s two armour rungs.
- Add 3 `ManualAnalysisDef` entries to `Analysis_Unblock.xml` for `VCE_Canning`/`DeepFrying`/`SoupCooking`; resolve the `Devilstrand` Neolithic deadlock.
- `PatchOperationAdd` the three stew processes onto `VCE_ElectricPot`.
- `PatchOperationReplace` `VFEM2_LeatherBoilpot`'s `StuffPower_Armor_*` so hardleather is worth boiling.
- Apply the settings table (IIB `useHighestResearched` on, `EmpireIsAlwaysEligible` false, `ChangeQuests` true; TechBlock insight rates ~0.5; MO `vanillaMine` on, `component_replace`/`chemfuel_replace`/`biotechSchematic`/`slopDispenser` off, `industrialJunk` on). Copy files, never re-click - the `metalChain` force lives in a *draw* method. Faction Customizer settings file is missing.
- At world creation, hand-add `VFEM2_KingdomRough`/`KingdomSavage`/`ClanSavage`/`CivilClan` (all ship at `startingCountAtWorldCreation = 0`).
- Teach `audit_research.py` Replace/Add/Remove on `ResearchProjectDef`; make `check_refs.py` read `ModsConfig.xml`; add the KCSG tag-has-a-layout check; either implement or delete `check_availability.py --plan`.
- Run the 6-item MP desync checklist (Dark Forest tile first - reported hard failure, possibly one `PatchOperationRemove` away).
- Investigate the 36 MRR deadlocks, prioritising the vanilla ship chain + GravTech + `VGE_GravshipPower`/`HeatDissipation`/`AstrofuelRefining`.

### From DECISION-medieval-route.md
- Implement the approved `VFE_Res_Sprinkler` retier (`Machining` -> a Medieval project).
- Deliver the **obsolescence audit**: classify all 46 MO+VCE production buildings into (a) naturally obsolete / (b) superseded - name successor + research / (c) persists forever. Bucket (c) is Conrad's actual question. Check specifically whether anything supersedes `Millstone`/`WindMill`/`WaterMill` post-Electricity.
- Produce the turn-to-turn Route A gameplay walkthrough mapped onto the three leaps.
- Re-run all four tools with MO enabled (~2,930 new defs).

### MO removals (from Player Progression Ideology, recorded in WORKLIST section 4)
- Cut: woodworking chain (wood->planks->boards), paper/paper press/cartography, textile spinning + linen, Mithril, most plant additions, ingredient additions (salt, saffron).
- Keep/simplify: carrier birds (no paper), beekeeping, brewing, winemaking, mine shaft, medieval crane, scarecrow, sprinkler.
- Cooking: one base station + augments, not six benches; each tier adds one *generic* ingredient class.

## D) MEDIEVAL MOD EXTRACTION PLAN

Route A = **enable and strip**, not hand-port. Nothing is copied into an `Archinity.Medieval` module.

| Mod | Status | What we take | What we strip / notes |
|---|---|---|---|
| **Medieval Overhaul** (`DankPyon_*`) | Enable (Route A) | ~39,900 research pts; full cooking/flour economy; `RequiredSchematic` gating on 14 projects; 60 buildings; 4 visible Noble House factions; `MedievalSiege` raid strategy; mine shaft, crane, carrier birds, beekeeping, brewing | Strip woodworking, paper/cartography, spinning/linen, Mithril, extra plants + ingredients. `metalChain` OFF (Conrad's sole objection - a setting, not a patch). `woodChain` UNRULED. Crossbow/heavy crossbow/handgonne dead under no-new-metals (need `DankPyon_IronIngot`). MO moves `Bow_Recurve`/`Bow_Great` off `CraftingSpot`, removing the early bow - needs a fix. |
| **Processor Framework** | Already subscribed | Hard dep for MO's mill/press/cheese chain | Doc's claim it needs a new Steam sub is stale - already there. |
| **Vanilla Cooking Expanded** | Enable | Grilling 400, CheeseMaking 750, Condiments 500 (Neo), 1,600 Industrial; 66 meals, 7 benches, 3 plants | Assembly exists but only 3 XML class refs. Three of its projects are MRR deadlocks. |
| **VCE - Stews** | Enable | StewCooking 300 | Fully def-only. `VCE_StewPot` does not supersede `VCE_ElectricPot` - needs the process patch. |
| **VFE Medieval 2** (`VFEM2_*`) | Already on | Keeps via KCSG (85x85, `VFEM2_Keep` tag, 12 houses); Arbalest + HandCannon/Arquebus (cover the dead MO gun slots); wall-mounted turrets; Matchlocks, Heraldry, ComplexWorkshops, Alchemy, plate armour; leather boilpot | Has **no perimeter, no garrison, no `defenseOptions`** - that's our authoring job. MO ships reconciliation patches for the overlaps via `LoadFolders.xml`. |
| **VFE Classical** (`VFEC_*`) | Already on | Scorpion siege engine, heavy shields (`VFEC_HeavyShieldMaking` gates the best shield in the load order, S .75/B .70) | **Contributes zero Medieval research** - all 18 projects Neolithic; VISION.md is wrong. Five 1,200-pt projects stranded behind a Medieval `FueledSmithy` = 6,000 pts buying nothing. Scorpion is Neolithic-era and needs regating. |
| **VFE Settler** | Already on | `VFES_Turret_Ballista` | `VFES_SiegeEquipment` reachable off bare `Smithing`. |
| **RimFantasy** | Undecided | - | Would need the 4 temperature pylons + `RF_ArcaneTemperatureRegulation` removed. |
| **Dark Ages: Medieval Tools** | Skip (recommended) | - | Zero research points; MO ships better versions of its 3 best tools; 4 of 5 buildings are stacking tool-cabinet clones. |
| **Faction - Elves** | Unassessed | - | Def-only, ships a faction + xenotypes. Test against no-race-bleeding. |

## Stale / contradicted items

- **HANDOFF.md still frames the Medieval route as open** - resolved to Route A in session 4.
- **HANDOFF.md's verification backlog #1 (fresh worldgen)** is done - Glitterites and Drifters both rendered correctly.
- **VISION.md lists Medieval Overhaul under "Explicitly rejected"** - reversed by Route A.
- **VISION.md claims "VFE Classical and Medieval 2 carry" the Medieval era** - VFE Classical contributes zero Medieval projects.
- **DECISION doc's Route A cost #1 (Processor Framework not subscribed)** and **#2 (patch `requiredCountAtGameStart` to 0)** are both dead - PF is subscribed, and `requiredCountAtGameStart` is dead code in 1.6.
- **DECISION doc's "7 MO factions force-spawn," "39 JobDrivers," "7 baseCost changes," "39+7 buildings," "Route B ~37,700 pts"** - all superseded (9 factions/6 hidden, 10 JobDrivers, 4 baseCost, 60 buildings, both routes yield 37,900).
- **HANDOFF's altar drain "~2 in-game hours"** contradicts `DrainTicks = 7500` (3h).
