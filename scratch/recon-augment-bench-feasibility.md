# Recon: core-bench + augment pattern feasibility

All [CONFIRMED IN SOURCE] against 1.6 `Assembly-CSharp.dll` + shipped mod assemblies.
Generated 2026-08-22.

## Q1 — Recipe gated on a linked FACILITY
**[NOT POSSIBLE natively] -> [POSSIBLE WITH ~15 LINES OF C#, no Harmony patch]**

`Verse.RecipeDef` (note: `Verse`, not `RimWorld`) has no `requiredFacility` field. Its
complete gate list: `researchPrerequisite`, `researchPrerequisites`, `memePrerequisitesAny`,
`factionPrerequisiteTags`, `fromIdeoBuildingPreceptOnly`. `RecipeDef.AvailableNow` checks
only those. `RimWorld.CompProperties_Facility` exposes only `statOffsets`, `maxSimultaneous`,
`maxDistance`, `mustBePlacedAdjacent`, `requiresLOS` — zero recipe surface.

**But** the bill menu is built in `RimWorld/ITab_Bills.cs:86`:
```csharp
if (SelTable.def.AllRecipes[i].AvailableNow && SelTable.def.AllRecipes[i].AvailableOnNow(SelTable))
```
`AvailableOnNow(Thing thing)` delegates to `Worker.AvailableOnNow(thing, part)`, and
**`RecipeDef.workerClass` is XML-settable**. `thing` is the worktable itself. So:

```csharp
public class RecipeWorker_RequiresFacility : RecipeWorker {
    public override bool AvailableOnNow(Thing thing, BodyPartRecord part = null) {
        var ext = recipe.GetModExtension<RequiredFacilityExtension>();
        var comp = thing.TryGetComp<CompAffectedByFacilities>();
        return comp != null && comp.LinkedFacilitiesListForReading
            .Any(f => f.def == ext.facility && comp.IsFacilityActive(f));
    }
}
```
XML: `<workerClass>Archinity.RecipeWorker_RequiresFacility</workerClass>` on the RecipeDef.

**No Harmony patch required** — this is a vanilla extension point. Pure deterministic read,
no `Rand`, called from a UI path. Multiplayer-safe.

**Gotcha [CONFIRMED]:** `Bill_Production.ShouldDoNow()` and `WorkGiver_DoBill` never call
`AvailableOnNow`. Removing the augment hides the recipe from the add-bill menu but
**existing bills keep running.** Either sweep on `Notify_LinkRemoved` or accept it.

Zero-C# alternative: research unlocks the recipe, and the research uses
`requiredResearchFacilities` (Q6) — but that gates on the *research bench*, not the craft
bench, and once researched it is permanent.
The `ThingDefCountClass` ingredient idea does not work (ingredients are consumed, not
proximity-checked).

## Q2 — Existing implementations
**[CONFIRMED — one real precedent, and it modifies rather than adds]**

`VFEMedieval.RecipePatches` (`3444347874/1.6/Assemblies/VFEMedieval.dll`): when
`VFEM2_MannequinStand` is linked, it prefixes `ITab_Bills.FillTab`, swaps
`thingDef.allRecipesCached` (private, publicized) for a cloned list with
`ingredient.count * 0.9f`, restores it in a min-priority postfix — plus patches
`BillStack.AddBill`, `Bill_Production.ExposeData/Clone`, and
`CompAffectedByFacilities.Notify_NewLink`/`LinkToNearbyFacilities`.
**That `allRecipesCached` swap is the exact hook for *adding* recipes too.**

Medieval Overhaul (`Building_ScribeTable`, `MedievalOverhaul.RequireLinkables`) gates a
**comms console**, not recipes; all its `CompProperties_AffectedByFacilities` worktables use
facilities for stat offsets only. VFE Production / Cooking: facilities are stat-only.

## Q3 — In-place bench upgrade
**[CONFIRMED — native in 1.6; bills LOST by vanilla, PRESERVED by a mod we already run]**

`Verse.ThingDef.replaceTags` (`List<string>`) is **vanilla 1.6**, consumed by
`GenConstruct.CanReplace` / `HasMatchingReplacementTag`, `GenSpawn.SpawningWipes`,
`Designator_Build`, and copied onto blueprint/frame defs by `ThingDefGenerator_Buildings`.
Core uses it on Wall/Fence, Door, Chair, Bed, Conduit, Barricade/Sandbags — **never on a
workbench**. Give bench tiers a shared `<replaceTags><li>ArchinityTailorBench</li></replaceTags>`
and you get native build-over-in-place with no mod dependency.

`CompProperties_Replaceable` and `buildingReplacementAllowedThings` **do not exist** in 1.6.
`building.smoothedThing` is rock-smoothing only. `building.relatedBuildCommands` is pure UI
(`BuildRelatedCommandUtility`) and pairs well with `BuildFacilityCommandUtility` to surface
augment build buttons on the core bench.

**Bills are not preserved by vanilla:** `RimWorld/Frame.cs:262 CompleteConstruction`
transfers quality, art, `CompHasSources`, storage group + `ThingStoreSettings`, ideo color,
style — **never `billStack`**.

**Replace Stuff - Continued (`3526354009`) is already in our load order** and fixes exactly
this: `Replace_Stuff.DestroyedRestore.BuildingReviver` stashes the old `Building_WorkTable`
in a MapComponent and re-adds every `Bill` to the new one. Its
`Replace_Stuff.InterchangeableItems` def also *writes* `replaceTags` onto ThingDefs at load,
and already defines a `TailoringBenches` category (HandTailoringBench / ElectricTailoringBench
/ VFE_TableTailorLarge).

## Q4 — `recipeUsers` vs `ThingDef.recipes`
**[CONFIRMED — declare `recipeUsers` on our own RecipeDef]**

`ThingDef.AllRecipes` merges `this.recipes` with every `RecipeDef` whose `recipeUsers`
contains this def, then caches into private `allRecipesCached`. Declaring `<recipeUsers>` on
*our* RecipeDef needs **no PatchOperation at all** against a foreign def.

Gotchas:
- The cache is built once on first access — anything mutating it at runtime must swap and
  restore, as VFEM does.
- `PatchOperationAdd` on `Defs/RecipeDef[defName="X"]/recipeUsers` **fails hard if the node
  is absent** (many recipes omit it). Guard with `PatchOperationFindMod`. Real example:
  `294100/1880253632/1.6/Patches/Rimefeller.xml`.
- `MayRequire="packageId"` is honored on `<li>` elements
  (`Verse/DirectXmlToObject.cs:212,297`) — the cheap alternative to a Patch file.

## Q5 — "MRR" does not exist; the installed mod is **More Realistic Research**
**[`sae.ResearchMod`, workshop `3771646847`]**

No "More Research Requirements" in any of the 71 workshop folders.
Schema (`Defs/Research Project.xml`, `Assemblies/ModResearchRimworld.dll`):

```xml
<ResearchMakesSense.ManualAnalysisDef>
  <defName>Lights</defName>
  <researchProject>ColoredLights</researchProject>
  <experimentalMaterials><li>Steel</li><li>WoodLog</li></experimentalMaterials>
  <experimentalPointsRequired>5</experimentalPointsRequired>
  <reverseEngineeringMaterials><li>Gloomlight</li></reverseEngineeringMaterials>
  <reverseEngineeringPointsRequired>6</reverseEngineeringPointsRequired>
  <theoreticalMaterials><li>ComponentIndustrial</li></theoreticalMaterials>
  <theoreticalPointsRequired>10</theoreticalPointsRequired>
</ResearchMakesSense.ManualAnalysisDef>
```

Semantics from `AnalysisEngine.ProcessCompletion` — the mod attaches
`CompProperties_Studiable{studyAmountToComplete=10}` + `CompProperties_Analyzable{canStudyInPlace=true}`
to every listed ThingDef at startup. A pawn studies the item **where it lies — no stockpile
requirement, just reachable on-map.** Each completed study = **1 point**.

| Type | Effect on the item |
|---|---|
| `Experimental` | `SplitOff(1).Destroy()` — **1 item consumed per point** |
| `ReverseEngineering` | `TakeDamage(Deterioration, 5-50% of MaxHitPoints)` — **degraded, not consumed** |
| `Theoretical` | **Not consumed, not damaged** |

`Patch_WorkGiver_Researcher` hard-blocks the research job (`HasJobOnThing` -> false, plus a
`JobDriver_Research` fail condition) until all three types are satisfied.

**No field for a required building-on-map, research bench, or facility.** Buildings can be
listed (`ResolveStudySubject` passes any non-race ThingDef) but a pawn must still study it.

### CRITICAL GOTCHA
**Any research project not explicitly listed gets auto-generated requirements based on its
TechLevel.** Every Archinity project will silently acquire material gates unless we declare
an empty `ManualAnalysisDef` for it. This is almost certainly the source of the 36 recorded
"MRR deadlocks."

## Q6 — Research requiring a building
**[CONFIRMED IN SOURCE]**

`Verse.ResearchProjectDef` has `public ThingDef requiredResearchBuilding;` and
`public List<ThingDef> requiredResearchFacilities;`.

From `CanBeResearchedAt(Building_ResearchBench bench, bool ignoreResearchBenchPowerStatus)`:
- `requiredResearchBuilding` is an **exact `bench.def` equality check** — no subclass or tag
  matching.
- Each `requiredResearchFacilities` entry must be in
  `bench.TryGetComp<CompAffectedByFacilities>().LinkedFacilitiesListForReading` **and** pass
  `IsFacilityActive(x)` — so facilities must be genuinely linked and powered/fueled.
- `CanStartNow` gates on `requiredResearchBuilding == null || PlayerHasAnyAppropriateResearchBench`,
  scanning all maps' `listerBuildings.allBuildingsColonist` with `ignoreResearchBenchPowerStatus: true`.

**The bench must be a `Building_ResearchBench`** — this cannot gate on a tailor bench.

## Source files
- `RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll` — `Verse.RecipeDef`,
  `Verse.ResearchProjectDef`, `Verse.ThingDef`, `RimWorld.ITab_Bills`, `RimWorld.Frame`,
  `RimWorld.GenConstruct`, `RimWorld.CompAffectedByFacilities`,
  `RimWorld.BuildRelatedCommandUtility`
- `RimWorld\Data\Core\Defs\ThingDefs_Buildings\Buildings_Structure.xml`
- `workshop\294100\3444347874\1.6\Assemblies\VFEMedieval.dll`
- `workshop\294100\3526354009\1.6\Defs\Vanilla.xml` (Replace Stuff)
- `workshop\294100\3771646847\Defs\Research Project.xml` + `Defs\readme.txt`
- `workshop\294100\1880253632\1.6\Patches\Rimefeller.xml`
