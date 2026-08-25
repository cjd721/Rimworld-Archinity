# Technical findings

Verified facts underpinning the Archinity design. Everything here was confirmed
against game defs or decompiled source — not documentation, not the wiki, not
assumption. Recorded so we never re-litigate it.

Game version 1.6.4871. Verify again after any major RimWorld update.

---

## Pacing and gating

### Quests can be gated on tech tier

`VEF.Storyteller.QuestChainExtension` has a `requiredResearch` field, unused by
any mod in our load order. `GameComponent_QuestChains.TryScheduleQuest`:

```csharp
QuestChainExtension ext = quest.GetModExtension<QuestChainExtension>();
if (ext.requiredResearch != null && !ext.requiredResearch.IsFinished)
    return false;
```

TechBlock's tier locks are `ResearchProjectDef`s, so they plug straight in:

| Def | Meaning |
|---|---|
| `TB_NeolithicTheory` | entered Neolithic |
| `TB_MedievalTheory` | entered Medieval |
| `TB_IndustrialTheory` | entered Industrial |
| `TB_SpacerTheory` | entered Spacer |
| `TB_UltraTheory` | entered Ultra |
| `TB_ArchoTheory` | entered Archotech |

### `rootMinProgressScore` is NOT a tech gate

`StorytellerUtility.GetProgressScore` is:

```csharp
return freeColonistCount * 1f + target.PlayerWealthForStoryteller * 0.0001f;
```

Colonists plus wealth/10000. Ignores research entirely. Vanilla gates sit at
3–10, which a wealthy neolithic colony clears in year one. Do not use.

### TechBlock's two projects per tier

- `TB_<Era>TechLock` — cost = `(tier's total research points × requiredPoints<Era>) − points already researched in that tier`. Shrinks as you research normally.
- `TB_<Era>Theory` — cost = the flat `<era>BaseCost` setting.

So advancing a tier costs a *fraction of the tier's value* plus a flat toll. It
is **not** "complete X% of the tree." Currently set to 0.75 across all tiers.

### Ignorance Is Bliss scope

`changeQuests` does **not** stop quests firing. It substitutes the faction in a
quest's threat for a tech-appropriate one ("Will not change the quest
description, but an appropriate faction will arrive").

Division of labour: **IIB controls who shows up, `requiredResearch` controls
when the quest appears.** Both needed; neither replaces the other.

`useActualTechLevel: true` is correct for us — its own tooltip says it is only
appropriate with a mod that drives colony tech level, which TechBlock does.

---

## Archite injection (VQE Ancients)

### Gene pool

`GetFilteredGenes(pawn, g => g.biostatArc > 0)` — every archite gene in the
loaded def database, minus `InjectionBlacklistDef`, minus genes the pawn has,
minus genes whose prerequisite is unmet. ~50 genes with our load order,
including `VRE_Transcendent` (now blacklisted in `Archinity.Pacing`).

`blacklistedGenes` is `List<string>` — plain defName strings, not
cross-referenced. Naming an absent gene is silently ignored, so the patch is
safe to over-specify.

### Outcome table

| Outcome | `baseWeight` |
|---|---|
| Success | 50 |
| Rejection | 35 |
| Spliceling | 8 |
| Splicehulk | 5 |
| Splicefiend | 2 |

All patchable. Optional looted facilities modify results — `VQEA_TraitSelectionPrism`
gives a choice of two archite genes instead of one random.

### Three independent gates

1. **The machine.** `VQEA_ArchogenInjector` inherits `neverBuildable: true`, but
   its base sets `minifiedDef: MinifiedThing` and `claimable: true`. You cannot
   build one — you find it in a vault, claim it, uninstall it, haul it home.
   Same for every support facility.
2. **Power.** 400 W running, 50 W idle. Hard requirement — see below.
3. **Ammo.** One `ArchiteCapsule` per injection. Not craftable by anyone at any
   tech level; the item description says so. Trade-only (outlander bases and
   caravans, orbital traders, Empire bases) plus ancient crate loot.

### Blood cannot gate it without C#

`Building_PawnProcessor.PowerOn` dereferences the power comp unguarded:

```csharp
public bool PowerOn => TryGetComp<CompPowerTrader>(this).PowerOn;
```

Read every tick via `ShouldProcessTick()`. Removing `CompProperties_Power`
causes a continuous NullReferenceException.

Adding `CompProperties_Refuelable` with a `HemogenPack` filter is crash-free and
gives a real fuel bar, but **does not gate** — VQEA's code never reads
`CompRefuelable`. Cosmetic only.

The capsule requirement is also not def-driven: `ThingDefOf.ArchiteCapsule` is
hardcoded in seven places, so hemogen cannot be added as a second ingredient.

Real gating requires ~10 lines of Harmony postfixing
`Building_PawnProcessor.get_PowerOn`. Deterministic, no RNG, reads only synced
state — assessed multiplayer-safe, but it means shipping an assembly.

---

## Quest rewards

### Fixed rewards ARE possible in pure XML

**Preferred — shipped precedent.** `Data/Royalty/.../Script_Intro_Deserter.xml:90-96`:

```xml
<li Class="QuestNode_SetItemStashContents">
  <items>
    <li>PsychicAmplifier</li>
    <li>PsychicAmplifier</li>
  </items>
</li>
```

Stocks an item stash at a site the player must travel to and clear. Threats are
attached to the same site via `Util_Raid` (see the node directly above it in
that file). Reward and danger authored together.

**Alternative — code-verified, no shipped XML usage.** `QuestNode_GenerateThing`
(calls `ThingMaker.MakeThing` directly, bypassing ThingSetMaker filters and
budgets) feeding `QuestNode_AddItemsReward`. Delivers by drop pod.

> **Gotcha:** the reward node must be nested inside a signal node.
> `Reward_Items.GenerateQuestParts` reads `slate.Get<string>("inSignal")`; at top
> level the pods drop on quest *accept* rather than on completion.

There is no `ThingSetMaker_Fixed`. VEF adds no reward nodes.

---

## Decay — what survives being acquired centuries early

| Thing | Decays? | Notes |
|---|---|---|
| `ArchiteCapsule` | **No** | No `DeteriorationRate`, no ticker, no `CompRottable`, `Flammability 0`. Safe anywhere, forever. No shelter needed. |
| Minified buildings | **No** | `MinifiedThing` has no `statBases` ⇒ rate 0; inner building is `category=Building` ⇒ `CanEverDeteriorate` false. A crated `VQEA_ArchogenInjector` keeps indefinitely, indoors or out. |
| `Genepack` | **Yes — 20 days** | `DeteriorationRate 5`/day vs 100 max HP. No grace period. `deteriorateFromEnvironmentalEffects: false`, so roofs, rooms and shelves give **zero** protection. |

**Consequence:** capsules and the crated god machine can be looted in the
Neolithic and stored for a decade with no special handling. **Genepacks cannot
be an early-game reward** — they are dust in 20 days.

The only thing that stops genepack decay is a powered `GeneBank` — research
`Xenogermination` (Industrial, cost 1000, itself gated behind Electricity),
40 W constant. Unpowered banks do not protect.

Genepack rewards are therefore viable **only from Industrial onward**, which is
fine: that is exactly when guaranteed-specific-gene rewards are wanted anyway.

> Do **not** patch `Genepack`'s `DeteriorationRate` to 0 to work around this.
> Genepacks are a single ThingDef with dynamic contents, so it is all-or-nothing
> and would strip gene banks of their entire purpose.

---

## Time

`GenDate.DaysPerYear = 60`. A RimWorld year is **60 days**, four 15-day
quadrums. Any gate expressed in years must be multiplied by 60, not 365.

Conrad's target era lengths, converted:

| Era | Years | Days | Era ends ~day |
|---|---|---|---|
| Neolithic | 1–2 | 60–120 | 60–120 |
| Medieval | 3–4 | 180–240 | 240–360 |
| Industrial | 2–4 | 120–240 | 360–600 |
| Spacer | 1–2 | 60–120 | 420–720 |

Day-based gates much above ~700 are effectively "never" for this campaign.

**Gating principle:** set day gates to the EARLIEST plausible entry into the
target era, and let `rootMinPoints` (which tracks colony strength) hold the
line. An available quest can be ignored; an absent one cannot be summoned.

---

## Odyssey space layer

| Layer | radius | subdivisions |
|---|---|---|
| Surface (Core) | 100 | 10 |
| Orbit (Odyssey) | 130 | **5** |

Tile count scales ~4^subdivisions, so orbit has orders of magnitude fewer tiles
than the surface. `PlanetLayerDef.Orbit` sets `settlementsPer100kTiles` to
`1000~1000` (one per ~100 tiles), so few tiles also means few settlements,
asteroids and sites. Raised to 6 in `Archinity.Pacing`.

Faction placement on the orbit layer is controlled by `FactionDef.layerWhitelist`
/ `arrivalLayerWhitelist` / `neutralArrivalLayerBlacklist`. Odyssey's own
`TradersGuild` and `Salvagers` are the working templates.

`settlementWorldObjectDef` lives on `PlanetLayerDef`, not `FactionDef`, so all
orbit factions share one base type by default. Better Traders Guild works around
this with a `PatchOperationSequence` on `SpaceSettlement` — same approach
available to us.

---

## Race containment

Neither VRE Starjack nor VRE Archon injects xenotypes into vanilla factions.
Starjack has zero `xenotypeChances` anywhere; Archon ships its own hidden
faction. The only Starjacks on the planet come from Odyssey's own Traders Guild
(25%) and Salvagers (10%) defs, which is vanilla intent.

`Archinity_ArchonianSanguophage` sets `canGenerateAsCombatant: false` and
`factionlessGenerationWeight: 0` so it can never spawn on anyone but the player.

---

# Session 4 findings

Verified against decompiled 1.6.4871 source and workshop files on disk. Nine
research agents. Where two disagreed, both positions are recorded rather than
smoothed over.

## Bench augments and linkable facilities

The mechanism behind "one base station, augmented over time" in
`Player Progression Ideology.txt`. **Read this section before designing against
that doctrine — it does not work the way it reads.**

### A RecipeDef CANNOT be gated on a linked facility

`RecipeDef` has no facility field. Its complete gate set is
`researchPrerequisite`, `researchPrerequisites`, `memePrerequisitesAny`,
`factionPrerequisiteTags`, `fromIdeoBuildingPreceptOnly`, `skillRequirements`,
`recipeUsers`. `AvailableNow` reads exactly those.

The job path never touches facilities either: `WorkGiver_DoBill.JobOnThing` to
`ThingIsUsableBillGiver` to `BillStack.AnyShouldDoNow` to `StartOrResumeBillJob`
checks only `bill.ShouldDoNow()` and `PawnAllowedToStartAnew`.
`Building_WorkTable.CurrentlyUsableForBills()` checks power, fuel, breakdown.

Every vanilla reader of `LinkedFacilitiesListForReading` was enumerated:
research-bench requirement, school-desk blackboards, psychic-ritual quality,
gravship engine, beds, stat-report string, LOS relink. **None is a recipe or a
bill.**

`RecipeDef.AvailableOnNow(Thing)` delegates to `Worker.AvailableOnNow`, and
`ITab_Bills` passes the worktable, so a custom `workerClass` can see the bench.
But it is called from UI paths only. It hides a recipe from the add-bill menu
and does **not** stop a standing bill. Needs C#.

### Facilities are additive-only

`CompProperties_Facility` has **`statOffsets` only**. There is no `statFactors`
field, and `CompAffectedByFacilities` overrides `GetStatOffset` but not
`GetStatFactor`. **Writing `statFactors` on a facility is a silent no-op.**

Offsets feed `StatWorker` generically, so any StatDef read off the bench Thing
works: `WorkTableWorkSpeedFactor`, `WorkTableEfficiencyFactor` (multiplies
product *count*), `ResearchSpeedFactor`, the medical-bed stats, `Comfort`,
`ContainmentStrength`, `GravshipRange`, `SubstructureSupport`.

**The def-only lever worth knowing:** `RecipeDef.workTableSpeedStat` and
`workTableEfficiencyStat` are pure-XML StatDef pointers. Define a custom stat,
set the bench base to 0, and only an augment can make the recipe progress. Soft
gate (the bill runs forever, or yields nothing) but entirely XML.

### Crafted quality is pawn-only in vanilla, but VFEM2 already patches it

`QualityUtility.GenerateQualityCreatedByPawn` takes only skill level,
`Inspired_Creativity` and an Ideology `RoleEffect_ProductionQualityOffset`. Its
sole crafting caller `GenRecipe.PostProcessProduct` has the `billGiver` in scope
and does not pass it. No building can influence quality in vanilla, and VEF adds
nothing here.

**VFE Medieval 2 ships the Harmony pattern, and it is already in the load
order.** `VFEMedieval_GenRecipe_MakeRecipeProducts_Patch` reads linked
facilities:

| Facility | Effect |
|---|---|
| `VFEM2_SmithingAnvil` | `Rand.Chance(0.2f)` to bump quality one level if below Normal |
| `VFEM2_StonePolisher` | same at `Rand.Chance(0.25f)` |
| `VFEM2_StoneClamp` / `VFEM2_CarvingBoard` | `stackCount * 1.1f` |
| `VFEM2_ForgeBellows` | transpiles `CompRefuelable.ConsumptionRatePerTick` to `* 0.8f` |

So the augment doctrine is proven, is roughly 20 lines of Harmony, and partly
already runs. Those `Rand.Chance` calls sit inside the synced bill-completion
path.

### Facility limits

- `maxSimultaneous` (default 1) is a **per-bench cap on that facility def**.
  Multiple copies stack **additively**.
- **One facility serves unlimited benches.** No cap on the facility side.
- A facility links to benches of different defs freely. `linkableBuildings` is
  computed at load by scanning ThingDefs whose
  `CompProperties_AffectedByFacilities.linkableFacilities` names it.
  **Declaration is bench-side only. You never edit the facility.**
- `maxDistance` 8 default, true-center Euclidean, `requiresLOS` true by default.
- Ties broken deterministically: `orderby distance, Position.x, Position.z`.

### Multiplayer cost: zero

Linking is purely positional and automatic (`PostSpawnSetup`, `PostMapInit`,
`Notify_LOSBlockerSpawnedOrDespawned`). **No gizmo, no `Command_`, no
designator, no player toggle** anywhere in `CompFacility` or
`CompAffectedByFacilities`. Zero `Rand` in linking. `Multiplayer.dll` contains
no occurrence of `Facility` or `CompFacility`, because it needs none.

### requiredResearchFacilities checks the RESEARCH bench

`ResearchProjectDef.requiredResearchFacilities` is checked by
`CanBeResearchedAt(Building_ResearchBench bench, ...)`, and
`requiredResearchBuilding` is compared against `bench.def` where `bench` is
already cast to `Building_ResearchBench`. So it gates *"you need a bellows next
to your research bench"*, not *"next to your forge"*.

**VEF's pure-XML link-topology tools**, all useful for one-bench-many-eras:
`VEF.Buildings.ResearchBuildingExtension` (`equivalentBenches`,
`equivalentFacilities`, which loosen both fields via transpiler),
`FacilityExtension` (`equivalentToFacility`, `copyLinksFrom`,
`linkOnInteractionSpots`), `AffectedByFacilitiesExtension` (`copyLinksFrom`),
`RecipeInheritanceExtension` (`inheritRecipesFrom`, `allowedRecipes`,
`disallowedProductFilter`).

### What MO and VFEM2 actually ship

`DankPyon_Bellows` is a plain facility, `WorkTableWorkSpeedFactor +0.04`,
maxDist 6, maxSim 1. `DankPyon_Anvil` is a plain `Building_WorkTable`. All 13
`VFEM2_ComplexWorkshops` unlocks are **facilities, not benches** (+0.02/0.03
work speed, maxDist 3.9). MO's
`Mods/VanillaExpandedMedieval/Patches/Add_Linkables.xml` already cross-links
them. **Neither gates a recipe.**

---

## KCSG settlement and structure authoring

### The exporter exists in 1.6

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

### SettlementLayoutDef schema

`settlementSize` (default 42,42), `samplingDistance` (8, Poisson spacing),
`avoidBridgeable`, `avoidMountains`, `centerBuildings` (REQUIRED: `centerSize`,
`spaceAround`, `forceClean`, `centralBuildingTags`, `allowedStructures`),
`peripheralBuildings`, `roadOptions`, `stuffableOptions`, `propsOptions`,
`defenseOptions`, `stockpileOptions`.

`StructOption` is `{ count: IntRange, tag: string }`. Placement Poisson-samples
points and weights by `GetWeight`: 0 once `count.max` is hit, 2 while below
`count.min`, 0.1 if it repeats the previous tag. **`count` is a soft target, not
a guarantee.**

### StructureLayoutDef schema

`layouts` is a list of lists of strings: ordered **layers**, each a list of rows
of comma-separated symbol defNames, with `.` meaning empty. Layer order is spawn
order. Plus `terrainGrid` / `foundationGrid` / `underGrid` / `tempGrid`,
`terrainColorGrid`, `roofGrid` (`.` none, `1` RoofConstructed, `2` RoofRockThin,
else Thick), `tags`, `modRequirements` (packageIds; the layout is skipped
entirely if absent), `isStorage`, `spawnConduits`, `randomRotation`, `spawnAt`.

Size derives from `layouts[0]`. Rows and cells beyond that are **dropped
silently**.

### KCSG traps

- **A tag no layout carries throws `KeyNotFoundException` mid-worldgen.**
  `structuresTagsCache[tag]` is indexed unguarded, and `centralBuildingTags` has
  no fallback. Worth adding to `check_refs.py`.
- **`_North` / `_East` / `_South` / `_West` symbol variants are generated at
  runtime** by `HotGenerateRotationSymbols`. They are not defs and **cannot be
  patched**. Same shape as the `USH_GlittershipChunk_North` finding in session 2.
- `StartupActions.CreateSymbols` auto-generates symbols **only for Core and DLC
  content**, plus VFE Props and Decor. **Every modded ThingDef needs a
  hand-written SymbolDef.**
- **`Def.GetModExtension` returns the FIRST match.** Never
  `PatchOperationAddModExtension` a second `KCSG.CustomGenOption` onto a faction
  that already has one. Patch its settlement def instead.
- `XmlInheritance.RecursiveNodeCopyOverwriteElements` **appends** list children,
  so a `ParentName` child's `allowedStructures` merges with the parent's.
  `Inherit="False"` clears first.

### defenseOptions is dead below Industrial

`SymbolResolver_EdgeDefenseCustomizable` gates `addTurrets` and `addMortars` on
`faction.def.techLevel >= Industrial` (4). Medieval is 3. **Only `addSandbags`
and `pawnGroupMultiplier` take effect for a medieval faction.** Siege engines
have to live inside the layout grid instead.

### Who already uses KCSG

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

### Siege placement

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

`MedievalOverhaul.RaidStrategyWorker_MedievalSiege` is gated on the
`FactionSiegeExtension.medievalSiege` extension **and** `techLevel == 3`. Both
that extension and the `ArtilleryMedieval_BaseDestroyer` buildingTag are **plain
def-level constructs**, so they can be patched onto VFEM2 factions once MO is
loaded. `DankPyon_BrigandFaction` is currently the only faction carrying it.
**No VFEM2 faction sets `canSiege`**, so vanilla sieges cannot fire for them
either.

---

## TechBlock

### The def names are offset one tier from the settings names

Confirmed in `BlockTechs()`: `switch (techLevel - 1)` puts **Medieval** costs
into `indCount`.

| Def | Actually gates | Label |
|---|---|---|
| `TB_NeolithicTechLock` | Animal | costs **1**, since we have no Animal research |
| `TB_MedievalTechLock` | **Neolithic** | "Neolithic Understanding" |
| `TB_IndustrialTechLock` | **Medieval** | "Medieval Understanding" |

`baseCost = SnapToMult(tierTotal x requiredPoints<Era> - alreadyResearched, 100)`.
`TB_MedievalTheory` is 500 baseCost x `CostFactor` 1.5 = **750 effective**.

### It writes the player faction's techLevel, but only on load

`RecalculateBlockValues` sets `Find.CurrentMap.ParentFaction.def.techLevel`. So
Ignorance Is Bliss's `useActualTechLevel` **does** track your tier. It just lags
until the next save-load. There is no `FinishProject` patch, so hand-finished
research does not shrink the lock until reload either.

> **Session note, unresolved.** Two agents disagreed. One read
> `IgnoranceBase.GetPlayerTech()` returning `Faction.OfPlayer.def.techLevel` and
> concluded the window was frozen at Neolithic for the whole run. The write
> above is the more specific finding and is probably correct, but it has **not
> been observed in game**. `useHighestResearched` sidesteps the question.

### The random-insight mechanic cancels visible progress

While researching a block tech, every 25 points grants 25 (`randomInsightRate 1`)
to a random unfinished same-tier project **and adds 25 back to the block's cost**
(`randomInsightProgressBlock 1`).

> **Net spend = tierTotal x requiredPoints - alreadyFinished.**

Two consequences: roughly 75% of a tier arrives free without being chosen, and
**the lock bar appears frozen**, because cost and progress rise together 1:1.
Setting both values to about 0.5 gives identical total spend with visible
movement. Must be edited in XML; the settings window forcibly re-couples the
sliders.

## Research rate, reconstructed

The documented 213/day reproduces exactly with one unstated assumption:
**46.64% researcher uptime, about 11.2 h/day**.

```
pts/day = N x (0.08 + 0.115*Skill) x benchFactor x 0.00825 x 60000 x 0.4664
```

**213/day is ONE Intellectual-10 researcher, not a colony rate.** Two
multipliers the earlier tables omit: `difficulty.researchSpeedFactor` (Rough
1.0, Hard 0.95, Extreme 0.90) and the bench's own StatParts, which are **x0.75
outdoors** plus a room-cleanliness curve from 0.75 to 1.15.

Both founders have `Neversleep`, about 75% uptime, so **x1.6 per pawn**.

| Int | pts/day | with Neversleep |
|---|---|---|
| 5 | 113 | 182 |
| 10 | 213 | 343 |
| 12 | 253 | 407 |

## More Realistic Research

`BuildForProject` returns null for `techLevel <= Neolithic` **and for
Archotech**, which was not previously recorded.

`BuildRegistry` applies hand-authored `ManualAnalysisDef`s *before* the tier
filter, so MRR's three Neolithic entries still apply. **`Devilstrand` demands 9
studies of `DevilstrandCloth`** — circular, since sowing needs the research, and
no Neolithic trader stocks `Fabric`.

## Factions

### The faction roster must be final BEFORE world creation

**Adding a `FactionDef` to an already-generated world does nothing, and says
nothing.** `FactionManager.ExposeData` has no reconcile path: it scribes the
faction list it was saved with and never re-reads `DefDatabase` for defs that
appeared since. No error, no warning, no log line — the faction simply is not in
the world and never will be.

For a single long co-op run this is a **one-time hard gate**, and it is the most
consequential silent failure in the project: a roster mistake is not a patch, it
is a new world.

There is a C# escape hatch — `FactionGenerator.CreateFactionAndAddToManager(layer, def)`
is public static — but it is a repair, not a plan.

Recorded here because it is load-bearing for the world-roster decision and
previously lived only in `docs/archive/sys/05-factions.md`, which is archived
prose rather than the fact store.

### requiredCountAtGameStart is DEAD CODE in 1.6

`FactionGenerator.InitializeFactions(layer, factions)` early-returns when
`factions != null`, and `WorldGenStep_Factions.GenerateFresh` always passes
`Current.CreatingWorld.info.factions`, which
`Page_CreateWorldParams.ResetFactionCounts()` always builds non-null. The only
null-passing caller is the dev quickstart.

**The real levers are `maxConfigurableAtWorldCreation` (0 means it can never
spawn), `startingCountAtWorldCreation`, and `displayInFactionSelection`.**

### Faction Customizer cannot remove factions

`azravos.factioncustomizer`'s entire Harmony surface is eight UI patches.
`FactionManager.Remove` / `defeated` / `deactivated` appear zero times. It can
add, rename, recolour and move settlements, and nothing else. Zero MP sync and
`Rand`-heavy mutations, so it is **pre-landing use only**. Its settings file is
missing from `config/ModSettings/`.

### Raid faction choice has no tech weighting

`UsableFactions(...).TryRandomElementByWeight(f => RaidCommonalityFromPoints(points) * (lastRaidFaction ? 0.4 : 1))`.
Ignorance Is Bliss gates via a postfix on `FactionCanBeGroupSource`.

Empty-pool behaviour is **fail-open and fail-quiet**:
`GetRandomEligibleFaction()` returns null with no fallback; with
`changeQuests=true` the postfix has no `else`, so the out-of-tech faction
attacks anyway. Storyteller raids simply stop firing.

**VFEM2 ships `VFEM2_KingdomRough`, `KingdomSavage`, `ClanSavage` and
`CivilClan` at `startingCountAtWorldCreation = 0`**, so a default world gets
only two visible Medieval factions. All have `maxConfigurableAtWorldCreation
9999`, so add them by hand at world creation.

## Armour maths

**Effective armour on stuffable apparel is `StuffEffectMultiplierArmor` (SEMA)
times the stuff's `StuffPower_Armor_X`**, not `ArmorRating_X`, which is 0 on
nearly every stuffable armour (`Core/Defs/Stats/Stats_Apparel.xml`,
`StatPart_Stuff`). **SEMA is the ladder metric.**

Reference stuffs: `Leather_Plain` S .81 / B .24; `Steel` S .90 / B .45.
Leather tier: `Leather_Patch` .45, `Leather_Plain` .81, `VFEM2_HardLeather` .88,
`Leather_Heavy` 1.24, `Leather_Rhinoceros` 1.29, `Leather_Thrumbo` 2.08.

**Rung counts available today:**

| | Neolithic | Medieval (active) | Medieval + MO |
|---|---|---|---|
| Leather | **1** | 3 | 4 |
| Steel | **0** | 4 | 6 |

The Neolithic result is the constraint. `HandTailoringBench` is gated on
`ComplexClothing` (Medieval) and `FueledSmithy` on `Smithing` (Medieval), so the
only Neolithic apparel venue is `CraftingSpot`, which exactly four armour defs
reach: `Apparel_TribalA`, `TribalHeaddress`, `KidTribal`, `VFEC_Toga`.

`VFEM2_LeatherBoilpot` already exists and is active (30 wood + 30 steel,
`ComplexClothing`), but hardleather is **+.07 sharp and -.02 blunt** over plain.
A junk-leather upcycler, not a rung, until its `StuffPower_Armor_*` is patched.

## Gravship

`Substructure` is `ParentName="FloorBase"` and `XmlInheritance` appends, so its
resolved affordances are `[Light, Medium, Heavy, Walkable, Substructure]`.
`GridsUtility.GetAffordances` returns the **foundation** list, overriding any
floor laid on top.

- `Heavy` buildings fly fine. **`Diggable` and `SmoothableStone` do not**, so
  `DiggingSpot` and `MiningSpot` are unbuildable on substructure. Same reason
  graves cannot fly.
- **Budget is cells, not mass.** `MaxLaunchWeight` does not exist. `GravEngine`
  gives `SubstructureSupport 500`; up to 6 `GravFieldExtender` add 250 each, so
  **2000 cells**.
- `MedievalOverhaul.PlaceWorker_WaterWheel.AllowsPlacing` has an explicit
  `WaterCellsPresent` check, so the water mill is impossible on a gravship.
- `GardeningBox` works (`Light` affordance, own `fertility 0.8` via the edifice
  branch). `Post` does not; its `DankPyon_GrowSoilVine` affordance is never
  patched onto `Substructure`.

## Medieval Overhaul specifics

### The settings-menu trap that breaks MP byte-identity

Inside the **Map-Gen tab's draw method**, not `ExposeData` and not a
constructor:

```csharp
if (!metalChain) { vanillaMine = true; }
```

Uncheck `metalChain` on the Production tab, close without visiting Map Gen, and
the force never runs. **Two players clicking identical settings can produce
different files.** Copy the file; never re-click it.

Also, `Scribe_Values.Look` omits values equal to their default, so a fresh
config and an explicitly-defaulted one are byte-different with identical
meaning. **Compare parsed values, not bytes.**

### Settings reach runtime, not just def-load

21 files read `MedievalOverhaulSettings.settings` across **27 fields**.
`Plant_PlantCollected` calls `Rand.Chance(settings.soilWearChance)` on every
plowed-soil harvest, so a mismatch means clients draw a **different number of
values** from the shared stream and everything downstream diverges.

Worse: both schematic patches' `Prepare()` returns `!settings.biotechSchematic`,
and **`Prepare()` decides whether the Harmony patch is applied at all**. A
mismatch means one client's `WorkGiver_Researcher` refuses jobs the other
accepts.

### The schematic cache is a genuine desync bug

Both patches carry `private static bool? cachedSchematicCheck` and
`cacheStaleAfterTicks` with a 250-tick window and **no key**: not the project,
not the bench, not the schematic. Whichever call lands first decides the answer
for every gated project on every bench. `CanBeResearchedAt` is called from
`WorkGiver_Researcher` (simulation) **and** the research tab UI (client-local),
so the player with the tab open poisons the shared cache on a schedule the other
client does not share.

Mitigation needs no assembly: strip the `RequiredSchematic` extension from the
14 projects and the postfix returns immediately.

### metalChain does not remove vanilla steel

It **prefixes** it. `DankPyon_MakeIngots_Steel` (IronIngot + Coal to vanilla
`Steel`, gated `DankPyon_Steel`, Medieval 2000) keeps steel fully craftable.

**`vanillaMine`, which defaults OFF, is what zeroes `MineableSteel` and
`MineableComponentsIndustrial` scatter** and relabels `Steel` to "steel ingot".
Its active branch is purely additive (adds 9 MO mineables to `PreciousLump`), so
turning it ON restores steel and component veins.

**Read the inactive branch, not the active one.** `metalChain` has no active
block at all: MO's base defs ship the chain unconditionally and the 23 inactive
ops dismantle it. The teardown also deletes `DankPyon_BlastFurnace`.

### component_replace hits 395 ThingDefs

An **unscoped** `PatchOperationSetName` on
`Defs/ThingDef/costList/ComponentIndustrial`. Parsing Core, all 4 DLC and the 47
active mods on disk gives 395 matches (320 inherited, 44 Industrial, 31 Spacer),
including `Ship_Beam`, `Ship_SensorCluster`, `Ship_CryptosleepCasket`, Odyssey's
`GravFieldExtender` and `Apparel_Vacsuit`, every GravTech pylon, and 24 `BfG_*`
biotech-gravship buildings.

It is also **half-broken**: the ingredient-side op targets
`Defs/RecipeDef/li/filter/thingDefs/li`, which matches **0** nodes (the correct
path matches 17), and its inner `PatchOperationReplace` has no xpath and would
throw if it fired. `chemfuel_replace` is structurally identical: 51 defs, zero
Spacer.

### MO ships four electric successors

`Defs/ThingDefs_Buildings/Production/Buildings_Processors_Industrial.xml` holds
`BlastFurnace` (500 W), `TanningDrum` (250 W), `ClothSpinner` (250 W) and
`SawTable` (250 W), all gated on `Electricity`. So every one of the four
resource chains has a verified Electricity-tier successor.

### Nothing in MO is ever hidden

`grep menuHidden` across all of MO 1.6 returns **zero hits**. The `*Spot` family
is retired purely by a flat `WorkTableWorkSpeedFactor 0.5` plus
`PlaceWorker_ReportWorkSpeedPenalties`. Economic, not mechanical: **the build
menu never gets shorter.**

### Iron-locked items

`DankPyon_Crossbow`, `DankPyon_CrossbowHeavy` and `DankPyon_Handgonne` require
`DankPyon_IronIngot`, producible only from `DankPyon_IronOre`. **There is no
Steel to ingot path.** `VFEM2_Arbalest` and `VFEM2_Gun_HandCannon` / `Arquebus`
cover the same slots in Steel.

MO also moves `Bow_Recurve` and `Bow_Great` off `CraftingSpot` onto
`DankPyon_Workbench`, removing the early bow path.

`VFEC_Bronze` is **not** a new mineable. It is crafted from 10 Steel plus stone
chunks and consumed only by `VFEC_BronzeTile` — a steel extender, not a
resource.

## Tier totals, measured

`audit_research.py` does not apply PatchOperations, so these are hand-corrected
for `Retier_Medieval.xml` (+2,500 Medieval) and MO's four research baseCost
changes (`LongBlades` 400 to 1,000; `PlateArmor` 600 to 2,000; `Cocoa` 500 to
600; `TreeSowing` a no-op), which are +2,000 Medieval and -1,000 Neolithic.

| Tier | Baseline | plus MO/PF | plus VCE/Stews |
|---|---:|---:|---:|
| Neolithic | 27,500 | 28,600 | 29,100 |
| **Medieval** | **18,000** | **57,900** | **59,350** |
| Industrial | 144,800 | 144,800 | 146,400 |

Medieval by source under full Route A: MO 45 projects / 37,900, Core 12 / 8,800,
VFEM2 7 / 7,400, Royalty 4 / 1,800, VCE 2 / 1,150, others 4 / 2,300.

**VFE Classical contributes ZERO Medieval projects.** All 18 are `techLevel
Neolithic` at 1,200 each, which is 74% of that tier. `VISION.md` says "VFE
Classical and Medieval 2 carry it" about the Medieval era; that is wrong.

**MO adds zero MRR deadlocks**, structurally, since all 45 of its projects are
Medieval and MRR gives Medieval "Experimental only" with no study subject.
**VCE adds three real ones**: `VCE_Canning`, `VCE_DeepFrying` and
`VCE_SoupCooking` each unlock exactly one bench that is `tradeability: None`
with no loot, mapgen or trade route — research needs the bench, the bench needs
the research.

## Medieval Overhaul licensing

MO ships **no license**. No LICENSE, COPYING or TERMS file in the mod;
`About.xml` says only "Pretty dank mod"; `gh api
repos/ViralReaction/MedievalOverhaul` returns `"license": null` with no LICENSE
in the repo root. No license means all rights reserved.

This only matters if MO content is **copied** into this repo (Route B). Enabling
MO as a normal mod and referencing its defNames distributes nothing, which is
what every compat patch on the Workshop does.

---

# Session 5 findings

## The determinism model: ticks, `Rand`, and threads

Verified against `Assembly-CSharp.dll` (1.6.4871) and Multiplayer 0.11.5's
`Multiplayer.dll`, not from memory and not from a mod's behaviour. This underpins
the third-party bar in issue #3 and the two gates in `CODING_STANDARDS.md`, so it is
recorded here rather than left in a ticket.

### What is on the synced tick and what is not

`TickManager.DoSingleTick()` contains, in order: every map's `MapPreTick`, the three
tick lists, `DateNotifierTick`, `TickScenario`, **`Find.World.WorldTick()`**,
`StoryWatcherTick`, `GameEndTick`, **`Find.Storyteller.StorytellerTick()`**,
`TaleManagerTick`. All of it is simulation.

`GameComponentUtility.GameComponentUpdate()` is called from **`Game.UpdateEntry()`
and `Game.UpdatePlay()`** — the Unity frame loop, not the tick.

| Hook | Runs | Safe to write sim state? |
|---|---|---|
| `WorldComponentTick` | inside `DoSingleTick` | **Yes** |
| `GameComponentTick` | inside `DoSingleTick` | **Yes** |
| `Thing.Tick` / `TickRare` / `TickLong` / `TickInterval` | tick lists | **Yes** |
| `WorldComponentUpdate` | frame loop | **No** |
| `GameComponentUpdate` | frame loop | **No** |

### Why `Rand` inside a synced tick is safe

There is **no per-tick reseeding**. Multiplayer runs deterministic lockstep: both
clients execute the same ticks in the same order against the same `Rand` state, so
the same *sequence* of draws yields the same results.

`Multiplayer.Client.ThingMethodPatches` — which wraps `Tick`/`TickRare`/`TickLong`/
`TickInterval`/`TakeDamage`/`Kill`/`SpawnSetup` on every `Thing` subtype — pushes
**faction and Thing context**, not a `Rand` seed. Thing ticks draw from the shared
global stream in tick order.

`Multiplayer.Client.MapRandomStateData` holds `List<uint> randomStates`: MP
checksums `Rand` state as simulation state, which is how desyncs are detected.

**The consequence: the hazard is never "a mod uses `Rand`". It is a mod consuming the
shared stream a different number of times, or at a different position, per client.**

### MP's own list of paths that must not touch the shared stream

`MultiplayerStatic` wraps `RandPatches.Prefix`/`Finalizer` — a bare
`Rand.PushState()` / `Rand.PopState()` pair — around a set it labels
**`SetCategory("Non-deterministic patches 1")`**:

`SubSustainer` lambda · `Sample` ctor · `SubSoundDef.TryPlay` ·
`Effecter.EffectTick` / `Trigger` / `Cleanup` · `LightningBoltMeshPool.RandomBoltMesh` ·
`Pawn_DrawTracker` ctor · `PawnStyleItemChooser.RandomHairFor` ·
**every public static `MoteMaker` method** · `Cable.Tick` ·
**every void `FleckMaker` and `FleckManager` method** · `LavaFXComponent.ThrowLavaSmoke` ·
`FishShadowComponent.SpawnFishFleck` · `CompFleckEmitterLongTerm.EmissionTick` ·
`RitualRoleAssignments.CanEverSpectate`

Every one is rendering- or audio-dependent — code that may run a different number of
times per client depending on camera, sound, and frame timing. **This is the
authoritative statement of the hazard class**, and it is why viewport-gated RNG
(`if (GenView.ShouldSpawnMotesAt(...)) { Rand.Value; }`) is the canonical bug.

### Why threads are the one thing that bars a mod

A background thread runs outside `DoSingleTick` entirely. It cannot be ordered
relative to the tick, so any `Rand` it consumes or sim state it writes is
non-deterministic by construction — and there is no XML or settings fix, because the
scheduling is not data. That is the whole content of the bar: **a world simulation
only bars if it runs off the synced tick, so in practice the bar reduces to *does it
create threads*.** A `WorldComponent` grinding through heavy world state inside
`WorldComponentTick` is deterministic; disliking it is a design objection about
shadow worlds, not a safety one.

### Worked example — TechBlock, the shape to recognise

Verified against `1.6/Assemblies/TechBlock 1.2.1.dll`, which is what loads. (The
folder also ships a `1.0/Assemblies/TechBlock.dll`; reading that one gives different
code and a wrong conclusion.)

`TechBlock_Component.GameComponentUpdate()` accumulates `savedProgress` and, per 25
points, calls `AddRandomProgress()` → `GenCollection.RandomElement(techLevelProjects)`
→ `Find.ResearchManager.AddProgress(val, 25f * settings.randomInsightRate)`.

Three defects, and the third is the instructive one:

1. Gated on client-local `settings.randomInsights`.
2. Magnitude scaled by client-local `settings.randomInsightRate`.
3. **The draw is taken from a per-frame method**, so it enters the shared stream at a
   frame-dependent position. Note the draw *count* is fine — the accumulator ties it
   to research progress, not frame count. It is the **interleaving position** that
   diverges, which means identical settings files do **not** fix it.

> The general lesson: when auditing a mod, do not stop at "does the number of draws
> match". Ask where in the stream the draw lands.
