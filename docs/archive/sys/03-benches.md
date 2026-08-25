# 03 — Benches & production

**Blocked by 01, 02.** Recipes are research-unlocked; the tree must exist first.

**Decided:** research-based gating is the primary mechanism and is sufficient. You research
an augment, which unlocks a band of recipes, and keep researching more advanced ones until
the next augment. The `RecipeWorker` mechanism below is a genuine second door — it exists,
it is cheap, and it is worth using where a hard requirement improves the feel — but nothing
in the design depends on it.

## What this system must do

Replace "one workbench per capability" with **one core bench per craft domain, kept for the
whole game, expanded by augments and upgraded in place.**

This is the single most load-bearing pattern in `Player Progression Ideology.txt`. It
governs cooking, smithing, tailoring and agriculture. Conrad's phrasing, and the test to
apply to every decision here:

> Keep the narrative surface. Reduce the complexity.

The complaint it answers is specific and worth restating: RimWorld makes you manage
production through per-building bill cards, and MO + VCE together ship ~13 cooking and
smithing benches. Switching between them is the tax. Researching the bellows and watching
your existing smithy get better is the fantasy.

## The mechanic — proven, three parts

### 1. Augment expands the core bench's recipe list

`RecipeDef` has **no** facility gate — its only gates are `researchPrerequisite(s)`,
`memePrerequisitesAny`, `factionPrerequisiteTags`, `fromIdeoBuildingPreceptOnly`.
`CompProperties_Facility` has no recipe surface at all.

**But `RecipeDef.workerClass` is XML-settable**, and the bill menu calls
`AvailableOnNow(SelTable)` — passing the worktable itself (`ITab_Bills.cs:86`).

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

~15 lines, **no Harmony patch** — this is a vanilla extension point. Deterministic read,
no `Rand`, UI path. Multiplayer-safe. Goes in the existing `Archinity.Altar` assembly,
so it does not violate the one-assembly rule.

**Known limit:** `Bill_Production.ShouldDoNow()` and `WorkGiver_DoBill` never call
`AvailableOnNow`. Remove the augment and the recipe vanishes from the add-bill menu, but
**existing bills keep running.** Either sweep on `Notify_LinkRemoved` or accept it —
accepting it is defensible, since players rarely deconstruct augments.

### 2. Core bench upgrades in place, keeping its bills

`ThingDef.replaceTags` is **vanilla 1.6** (`GenConstruct.CanReplace`,
`GenSpawn.SpawningWipes`, `Designator_Build`). Core uses it on walls, doors, beds,
conduits — never on a workbench. Give bench tiers a shared tag and you get native
build-over-in-place:

```xml
<replaceTags><li>ArchinityTailorBench</li></replaceTags>
```

`CompProperties_Replaceable` and `buildingReplacementAllowedThings` do not exist in 1.6.
`building.smoothedThing` is rock-smoothing only.

**Vanilla does not preserve bills** — `Frame.CompleteConstruction` transfers quality, art,
storage settings, style, never `billStack`. **Replace Stuff - Continued (`3526354009`) is
already in our load order** and fixes exactly this: `BuildingReviver` stashes the old
`Building_WorkTable` and re-adds every `Bill`. It already defines a `TailoringBenches`
category and *writes* `replaceTags` onto ThingDefs at load — check for collisions before
authoring our own.

### 3. Adding recipes to a foreign bench

Declare `<recipeUsers>` on **our** RecipeDef — `ThingDef.AllRecipes` merges it in, and this
needs **no PatchOperation** against a foreign def. `MayRequire="packageId"` is honored on
`<li>` elements, which is cheaper than a Patch file.

Do **not** `PatchOperationAdd` onto `Defs/RecipeDef[defName="X"]/recipeUsers` — it fails
hard when the node is absent, which is common.

## Design rules for this system

- **Augments are real, not decorative.** Each carries `statOffsets` on
  `WorkTableWorkSpeedFactor` or similar. Note `CompProperties_Facility.statFactors` is a
  **silent no-op** — offsets only.
- **The core bench never becomes obsolete.** It upgrades. A tailoring bench is a tailoring
  bench whether you are in a hut or a gravship; some benches simply stop improving after
  the electric tier and that is fine.
- **Augments survive the core upgrade.** They link to the new bench.
- **A separate building is justified only when the *process* is the point** — something you
  load and leave, that takes real time. A cheese press or a fermenting barrel qualifies. A
  second oven that exists to hold four more recipes does not.
- **Never add a processing step whose output is an input to normal construction.**
  wood→plank→board, ore→ingot, cloth→linen are all rejected. The construction cost of using
  the material *is* the roleplay of shaping it. Test: would I still be doing this in the
  Spacer era? If not, cut it.

## Domains to author

> **D2 resolved yes — Medieval Overhaul is enabled**, so the MO content named below exists.
> Note that MO is enabled *to be gutted*: cross-check every bench here against `sys/04`'s
> kill list before building on it.

| Domain | Core bench | Augment candidates | Notes |
|---|---|---|---|
| **Cooking** | one stove, Neolithic → electric | brick oven, flour mill, cheese press, smoker | MO + VCE ship ~13 benches; target 1 core + 3-4 augments. Cheese press may deserve to stay standalone (load-and-leave). |
| **Smithing** | smithy, upgradeable | anvil, bellows, furnace, grind wheel | MO's `Smithing` currently unlocks anvil + bellows + fueled smelter + field smithy + furnace + grind wheel **all at once**. Split across research. Bellows gates military-grade. |
| **Tailoring** | hand → pedal → electric | spinning wheel, others TBD | Absorb textile spinning entirely. **Linen is cut.** Silk survives as a cloth upgrade, not a spun chain; silk beds are acceptable (load-and-leave). Armour needs **both** tailoring and smithing. |
| **Agriculture** | n/a (field-based) | scarecrow, sprinkler, trough | Not a bench, but the same pattern: placeable, no management, real bonus. Prefer these over MO's plowed soil, which was buggy in play. |

## Work items

- [ ] Write `RecipeWorker_RequiresFacility` + `RequiredFacilityExtension` into
      `Archinity.Altar`. Decide the stale-bill behaviour.
- [ ] Check Replace Stuff's `InterchangeableItems` for `replaceTags` collisions before
      authoring bench tiers.
- [ ] **Obsolescence audit** — classify all 46 MO+VCE production buildings into
      (a) naturally obsolete, (b) superseded — name successor + research, (c) persists forever.
      Bucket (c) is the real question. Check specifically whether anything supersedes
      `Millstone` / `WindMill` / `WaterMill` after Electricity.
- [ ] Author the four domains: core bench tiers, augment set, which recipes attach to which
      augment, which research unlocks each.
- [ ] `PatchOperationAdd` the three stew processes onto `VCE_ElectricPot` — `VCE_StewPot`
      does not supersede it today.
- [ ] Surface augment build buttons on the core bench via `BuildFacilityCommandUtility` +
      `building.relatedBuildCommands` (pure UI, cheap, big legibility win).
- [ ] Confirm the bill-menu behaviour in game with one augment before authoring all four
      domains.
