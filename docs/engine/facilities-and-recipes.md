# Facilities and recipes

How linkable facilities attach to benches, what they can and cannot change, and
what the recipe/bill pipeline will and will not read from them.

Verified against decompiled RimWorld 1.6.4871 unless an entry says otherwise.
These are *verified available mechanisms*, not commitments to use them —
selection happens in `docs/specs/`.

---

This is the mechanism behind "one base station, augmented over time" in
`Player Progression Ideology.txt`. **Read this section before designing against
that doctrine — it does not work the way it reads.**

## A RecipeDef CANNOT be gated on a linked facility

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

## Facilities are additive-only

`CompProperties_Facility` has **`statOffsets` only**. There is no `statFactors`
field, and `CompAffectedByFacilities` overrides `GetStatOffset` but not
`GetStatFactor` — writing `statFactors` on a facility fails silently (see
`docs/TRAPS.md` T-23).

Offsets feed `StatWorker` generically, so any StatDef read off the bench Thing
works: `WorkTableWorkSpeedFactor`, `WorkTableEfficiencyFactor` (multiplies
product *count*), `ResearchSpeedFactor`, the medical-bed stats, `Comfort`,
`ContainmentStrength`, `GravshipRange`, `SubstructureSupport`.

**The def-only lever worth knowing:** `RecipeDef.workTableSpeedStat` and
`workTableEfficiencyStat` are pure-XML StatDef pointers. Define a custom stat,
set the bench base to 0, and only an augment can make the recipe progress. Soft
gate (the bill runs forever, or yields nothing) but entirely XML.

## Crafted quality is pawn-only in vanilla, but VFEM2 already patches it

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

## Weapons, apparel and armour share one work-speed stat

`BaseMakeableGun`, `BaseMeleeWeapon`, `BaseMakeableGrenade`, the neolithic ranged weapons,
`ApparelMakeableBase`, `ArmorSmithableBase` and `ArmorMachineableBase` all set
`recipeMaker.workSpeedStat` `GeneralLaborSpeed`. `RecipeDefGenerator` copies
`recipeMaker.workSpeedStat` and `efficiencyStat` onto the generated `RecipeDef`, so **repointing
the stat on a base is how a recipe family gets its own speed stat** — pure XML plus a new
`StatDef`. `QualityUtility.GenerateQualityCreatedByPawn(Pawn, SkillDef, bool)` takes no product,
so no stat distinguishes quality by recipe; that needs C#. From
[#156](https://github.com/cjd721/Rimworld-Archinity/issues/156) (`docs/specs/SPECIALISATION.md`);
`Core/Defs/ThingDefs_Misc`, `RimWorld.RecipeDefGenerator`, `RimWorld.QualityUtility`. 1.6.4871 [V].

## Facility limits

- `maxSimultaneous` (default 1) is a **per-bench cap on that facility def**.
  Multiple copies stack **additively**.
- **One facility serves unlimited benches.** No cap on the facility side.
- A facility links to benches of different defs freely. `linkableBuildings` is
  computed at load by scanning ThingDefs whose
  `CompProperties_AffectedByFacilities.linkableFacilities` names it.
  **Declaration is bench-side only. You never edit the facility.**
- `maxDistance` 8 default, true-center Euclidean, `requiresLOS` true by default.
- Ties broken deterministically: `orderby distance, Position.x, Position.z`.

## Multiplayer cost: zero

Linking is purely positional and automatic (`PostSpawnSetup`, `PostMapInit`,
`Notify_LOSBlockerSpawnedOrDespawned`). **No gizmo, no `Command_`, no
designator, no player toggle** anywhere in `CompFacility` or
`CompAffectedByFacilities`. Zero `Rand` in linking. `Multiplayer.dll` contains
no occurrence of `Facility` or `CompFacility`, because it needs none.

Facility linking therefore needs no sync work of any kind. For what does need
sync, see `docs/engine/determinism.md`.

## requiredResearchFacilities checks the RESEARCH bench

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

## What MO and VFEM2 actually ship

`DankPyon_Bellows` is a plain facility, `WorkTableWorkSpeedFactor +0.04`,
maxDist 6, maxSim 1. `DankPyon_Anvil` is a plain `Building_WorkTable`. All 13
`VFEM2_ComplexWorkshops` unlocks are **facilities, not benches** (+0.02/0.03
work speed, maxDist 3.9). MO's
`Mods/VanillaExpandedMedieval/Patches/Add_Linkables.xml` already cross-links
them. **Neither gates a recipe.**

## The add-bill menu has no search and no era concept

Verified in [#87](https://github.com/cjd721/Rimworld-Archinity/issues/87) against
vanilla 1.6.9642.18666.

`ITab_Bills.OptionsMaker()` walks `SelTable.def.AllRecipes`, gates each on
`AvailableNow && AvailableOnNow(SelTable)`, and returns a `List<FloatMenuOption>`
ordered only by `-recipe.displayPriority`. `BillStack.DoListing` hands that straight to
a `FloatMenu`, and `Verse.FloatMenu` contains **zero** occurrences of "search" [V].
No search, no grouping, no filter — by construction, which is why a bench with eighty
recipes is unreadable.

**`RecipeDef.AvailableNow` keys on `researchPrerequisite(s)`, memes and faction tags —
never on `techLevel`** [V]. There is no vanilla era concept on this surface at all.
This is the same shape as § *A RecipeDef CANNOT be gated on a linked facility*:
`AvailableOnNow` is the one hook, it is UI-only, and it does not stop a standing bill.

Near miss worth knowing: `Dialog_BillConfig` **does** own a
`thingFilterState.quickSearch` [V] — a quick-search over the *ingredient* filter. The
engine ships the widget; it is simply not wired to the recipe list.

**The configuring complaint is a defaults complaint, not a missing mechanism** [V].
Every field wanted already exists on `Bill_Production`; the vanilla initialisers are
`repeatMode = RepeatCount`, `targetCount = 10`, `hpRange = ZeroToOne`,
`qualityRange = All`. And `Dialog_BillConfig.DoWindowContents` draws the `hpRange` and
`qualityRange` sliders **inside the `repeatMode == TargetCount` branch**, so the mode
must be switched before they render at all. The injection point for a hard default is
proven and already in use by a mod: a postfix on `BillUtility.MakeNewBill`.

**An era filter over this menu is the MP-safe kind (T-21).** `OptionsMaker` builds a
fresh list on each click, never serialises it, and nothing in the tick path reads it —
so a filter applied there is draw-time by construction. The unsafe variant mutates
`def.AllRecipes` or patches `AvailableOnNow` to a per-player value; `AvailableOnNow` is
also consulted on the paste-validation path, so that would diverge what a client can
*do* rather than what it sees [V].

**What the menu can be reshaped with, and what a recipe's era can key on** (from
[#161](https://github.com/cjd721/Rimworld-Archinity/issues/161), vanilla 1.6.4871) [V]:

- `FloatMenu` sorts by `Priority` descending, then by `orderInPriority`. A `Disabled` option
  reports `MenuOptionPriority.DisabledOption`, the enum's lowest value. **A disabled row
  therefore sinks to the bottom** and cannot serve as a group header.
- `RecipeDef` has **no `techLevel` field**. `RecipeDefGenerator` copies
  `recipeMaker.researchPrerequisite(s)` onto the recipes it generates. World Tech Level keeps
  a tech-level database for `ThingDef` and `ResearchProjectDef` but none for `RecipeDef`.
- **FloatSubMenu** is kathanon's library. The corpus ships it only as `FloatSubMenu.dll` inside
  Nice Bill Tab (`3520130671`). It adds nested menus, a `QuickSearchWidget` search row, checkbox
  rows and dividers to any vanilla `FloatMenu`. It filters by swapping `FloatMenu.options` for a
  copy at draw time. **Every patch it applies is a UI patch.** Its `PatchAll` covers
  FloatSubMenu's own targets (`FloatMenu.UpdateBaseColor`, `GenUI.DistFromRect`) and those of
  its bundled MoreWidgets:
  - `GameConditionManager.TotalHeightAt` and `DoConditionsUI`;
  - `GameComponentUtility.GameComponentOnGUI`;
  - `DebugTabMenu_Settings.InitActions`;
  - a tooltip transpiler on `LongEventHandler.LongEventsOnGUI` and `UIRoot.UIRootOnGUI`.
- **Nice Bill Tab can be switched off per player.** Its `ITab_Bills.FillTab` prefix returns
  `true`, so vanilla's tab and add-bill menu run, while its on-tab checkbox
  (`Settings.EnabledMod`) is off. The flag defaults to `true`, is client-local and is never
  scribed.
- **Correction:** Glittertech's `Source/ITab_BillsMemoryCell.cs`, cited in #87 as a 1.6
  template, is **not in the 1.6 `GlittertechExpansion.dll`**. That assembly ships
  `ITab_MemoryCellMods` instead, so the file is stale source. The shape survives under the
  new name: `BuildRecipeOptions` walks `AllRecipes` and hands the result to
  `BillStack.DoListing`. **A patch at `DoListing` reaches every such menu; one on vanilla's
  local `OptionsMaker` reaches only vanilla's.**

See also `docs/engine/mods/medieval-overhaul.md` and
`docs/engine/research-and-tech-tiers.md`.
