# Items and gear

## Purpose and scope

**What this document owns:** how obsolete apparel, armour and weapons are turned back
into the material they were made of, at a bench, without inventing an intermediate
resource.

The campaign deprecates constantly, across five eras, and recycling is the counterweight
the deprecation design leans on — one of four named levers in
`docs/playtest-notes.md` § *Recycling is in, and a bench may be justified by the labour
it soaks*. The hard constraint is the no-chains rule in `docs/PLOT.md` § *Campaign in play*
— *"Avoid warehouses of unusable mystery items, chains of intermediate processing and
compulsory busywork"* — which this document reads as: **material in, material out. No
scrap, no rags, no salvage.**

Established by [#82](https://github.com/cjd721/Rimworld-Archinity/issues/82).

**Where adjacent systems take over.**

- Which era a recipe unlocks in, and the research key that gates it — the research gate
  (`docs/requirements/ERA.md` § *The acquisition gate*), placed by
  [#30](https://github.com/cjd721/Rimworld-Archinity/issues/30); the bench is
  [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.
- What a new bill defaults to, and the `hpRange` / `qualityRange` sliders —
  [#95](https://github.com/cjd721/Rimworld-Archinity/issues/95), `DEFAULTS.md` § *Half one*.
- Whether the add-bill menu is legible with this many recipes on it — `COLONY.md` § *The
  add-bill menu shows what matters now*
  ([#161](https://github.com/cjd721/Rimworld-Archinity/issues/161)).
- Requirement: `docs/requirements/COLONY.md` § *Obsolete gear goes back to the material it
  was made of*.

---

## The build

### Mechanism

**`SpecialProductType.Smelted`, with the stuff flags switched on.**

The engine already ships the behaviour this ticket asks for, and it is stuff-aware by
construction:

```
GenRecipe.MakeRecipeProducts
  → Verse.Thing.SmeltProducts(float)
    → ThingDef.CostListAdjusted(Stuff)          [RimWorld.CostListCalculator]
```

`CostListAdjusted` returns the def's fixed `costList` **plus one entry for the stuff
itself**, at `Mathf.RoundToInt(CostStuffCount / stuff.VolumePerUnit)` [V]. A thrumbofur
parka's adjusted cost list *is* `Leather_Thrumbo × 80` — the same list its make-recipe
consumed. The engine hands back the stuff def, never a token, so **an intermediate noun is
not expressible on this path at all**.

**`SmeltProducts` also appends `def.smeltProducts`** — a fixed per-def
`ThingDefCountClass` list, emitted in full alongside the adjusted-cost yield and **not**
scaled by the 0.25 multiplier [V]. Vanilla leaves it unset on apparel and weapons, so it
contributes nothing here; it is worth knowing because it is the one place a def *can*
smuggle a fixed product into an otherwise stuff-only return, and any def we author must
leave it empty for the no-chains rule to hold.

**No other return path in the engine is stuff-aware [I].** `products` is a fixed
`ThingDefCountClass` list; `SpecialProductType.Butchery` reads `ThingDef.butcherProducts`,
also fixed and per-def; neither can say *"whatever it was made of."* The three paths were
read directly [V]; that they exhaust the engine's return paths is an **exhaustiveness
negative over the assembly and is [I]** — marked once here, and not restated as [V]
anywhere below.

**The one thing standing in the way is a boolean on five metals.**

```csharp
// Verse.Thing.Smeltable
if (this.IsRelic()) return false;
if (def.smeltable) { if (def.MadeFromStuff) return Stuff.smeltable; return true; }
return false;
```

```csharp
// Verse.Thing.SmeltProducts
if (!costListAdj[j].thingDef.intricate && costListAdj[j].thingDef.smeltable) { ... }
```

Both [V]. **Nearly every vanilla apparel def is already `smeltable = true`, and every def
this build touches is** — the abstract `ApparelNoQualityBase` sets it, and `ApparelBase`,
`ApparelMakeableBase`, `HatBase` and `ArmorSmithableBase` all descend from it; weapons the
same, via `BaseWeapons.xml` [V]. **It is not a universal.** Six defs override the inherited
`true` back to `false` — `Apparel_PsychicFoilHelmet`, both psychic lances,
`OrbitalUtilityBase`, `Apparel_CerebrexNode` and the abstract `PsychicApparelBase` [V].
**None of the six is `MadeFromStuff`**, so `Thing.Smeltable`'s stuff branch never reaches
them and they are already outside a stuff-returning recipe's reach — **the build survives
the exception intact**, and the six are correctly excluded rather than accidentally so. The
claim to carry forward is the narrow one: *stuff-made apparel and weapons inherit
`smeltable = true`*, not *every apparel def is smeltable*.
**The block is therefore entirely on the stuff side.** Vanilla marks exactly `Silver`, `Gold`,
`Steel`, `Plasteel` and `Uranium` smeltable (`Jade` is explicitly false). `Cloth`,
`Synthread`, `DevilstrandCloth`, `Hyperweave`, `WoodLog`, every `Wool*` and every leather
leave the field at its `false` default [V] — which is why a cloth parka is filtered out of
`SmeltApparel`'s bill before a pawn walks to the bench, and would yield nothing if it got
there.

**Flip the flag and the whole mechanism comes on**, for the Neolithic and Medieval
material economy this campaign spends two eras in.

### New code and defs

**1 — the stuff patch.** One `Patches/` file:

| Target | Reaches |
|---|---|
| `ThingDef[@Name="LeatherBase"]` | the 20 Core leathers and every mod leather parented to it |
| `ThingDef[@Name="WoolBase"]` | every wool — **5 in Core, 7 with the DLC installed**; state the expected count against the load-out being patched |
| `Cloth`, `Synthread`, `DevilstrandCloth`, `Hyperweave`, `WoodLog` | named; no shared abstract |

Patching the abstract parents is correct **because of T-02** — PatchOperations run before
`ParentName` inheritance resolves, so one operation on `LeatherBase` reaches every
descendant, including mod-added ones (`docs/engine/def-loading.md` § *Patching happens
before inheritance*). Annotate each operation with its expected match count derived from
the def files, never from `tools/xpath.py`'s own output (`CODING_STANDARDS.md` §
*The red–green loop for def work*).

Checked for blowback [V]: `ThingDef.ConfigErrors` emits *"is smeltable but does not give
anything for smelting"* only for defs that are neither `IsStuff` nor `MadeFromStuff`, and
every target here is stuff. The readers of `smeltable` located are
`SpecialThingFilterWorker_Smeltable` / `_NonSmeltable` / `_NonSmeltableWeapons`,
`ThingDef.PotentiallySmeltable`, `Thing.Smeltable`, `Thing.SmeltProducts` and
`RecipeDef.WorkAmountTotal`'s `SmeltOrDestroyThing` branch. The intended side effect is
that vanilla's own `SmeltApparel` and `SmeltWeapon` at the `ElectricSmelter` begin
accepting textile and wooden gear too — at vanilla's 25%, beside the reclaim recipe's 50%:
each carries one `<li>Smelted</li>` (Core `Recipes_Production.xml`) [V], and the same two
defs sit on `DankPyon_Furnace` and (`SmeltWeapon`) on `VFE_FueledSmelter` (3, below). Every
reclaim path's fraction can be set by mechanisms verified here: a second `Smelted` entry
added to `SmeltApparel`/`SmeltWeapon` by `PatchOperation` (*The return fraction*), or
removing them from a bench's `recipeUsers` (3, below). Field readers were not exhaustively
enumerated across the whole assembly; residual risk **[I]**.

**2 — two RecipeDefs**, `Archinity_ReclaimApparel` over the `Apparel` category and
`Archinity_ReclaimGear` over `Weapons`. Split rather than merged so the bill's ingredient
filter stays legible. Each carries `specialProducts` repeated once per 25% of return
wanted (below), `workSkill Crafting`, a `workSpeedStat`, and **no `efficiencyStat`** — see
the trap note.

`Thing.Smeltable` hard-returns `false` for relics [V], so anything Ideology has sanctified
is protected without a filter of ours.

**3 — the venue.** `RecipeDef` gating is `researchPrerequisite(s)` plus `recipeUsers`, both
XML. It **cannot** be gated on a linked facility, and `AvailableNow` never reads
`techLevel` (`docs/engine/facilities-and-recipes.md`). The venues that exist:

| Venue | Ships in | Gate | Carries today |
|---|---|---|---|
| `CraftingSpot` | Core | none — buildable turn one | real `Building_WorkTable` + `ITab_Bills` |
| `ElectricSmelter` | Core | `Smithing`, 700 W | `SmeltWeapon`, `SmeltApparel`, `SmeltOrDestroyThing`, `Destroy*` |
| `VFE_FueledSmelter` | VFE Production `1880253632` | wood-fuelled | `SmeltWeapon`, `DestroyWeapon`, `ExtractMetalFromSlag` — **no `SmeltApparel`** |
| `DankPyon_Furnace` | Medieval Overhaul `3219596926` | — | `SmeltWeapon` **and** `SmeltApparel` |

`CraftingSpot` being a genuine `Building_WorkTable` [V] is what makes a Neolithic reclaim
possible at all. Per Conrad's *"a bench earns its place by the labour it absorbs"*, a
dedicated reclaim bench is available as a plain `Building_WorkTable` ThingDef with no
`thingClass` of ours — pure XML.

### The return fraction

**`Thing.SmeltProducts` takes a `float efficiency` and never reads it.** The multiplier is
a literal `0.25f` [V]. See *Failure and recovery* — this is `docs/TRAPS.md` **T-56**,
because both sibling methods on the same class honour the identical argument.

**The fraction is still XML-tunable, in 25% quanta.** `GenRecipe.MakeRecipeProducts` loops
`for each specialProducts entry { for each ingredient { ... } }`, and `specialProducts` is
a `List<SpecialProductType>`, not a set [V]. A repeated entry runs the pass again:

```xml
<specialProducts>
  <li>Smelted</li>
  <li>Smelted</li>   <!-- 50% return -->
</specialProducts>
```

Shipped precedent: Ushanka's Glittertech Expansion does exactly this for the Butchery case
on `USH_DisassembleCorpseMechanoid`, commented `<!-- doubled products -->`
(`294100/3522676478/1.6/Defs/Recipes/Recipe_Disassembler.xml`) [V]. The loop is [V]; that
two independent `GenMath.RoundRandom` draws aggregate to the intended fraction modulo
rounding variance is **[I]**.

The mechanism can express 25 / 50 / 75 / 100 and nothing between. **The requirement is
50%: two `Smelted` entries** (`docs/requirements/COLONY.md` § *Obsolete gear goes back to
the material it was made of*).

### Quality and damage

`SmeltProducts` reads `def.CostListAdjusted(Stuff)` and nothing else. It never touches
`HitPoints`, `MaxHitPoints` or `CompQuality` [V]. **Yield cannot depend on the item's
condition in XML at any price.**

What *is* available today: `bill.ingredientFilter.AllowedHitPointsPercents` and
`.AllowedQualityLevels`, so *"recycle only tattered gear"* and *"recycle only awful-quality
gear"* are already expressible on the bill **[V]**. These are `ThingFilter` fields, not
`Bill_Production.hpRange`/`.qualityRange` — that pair filters which existing products count
toward a target, not which items are consumed. They are drawn by
`Dialog_BillConfig.DoIngredientConfigPane`, a separate method with **no repeat-mode gate**
(`forceHideHitPointsConfig: false, forceHideQualityConfig: false`) **[V]**, subject to two
conditions: the pane draws only when the recipe has at least one **non-fixed** ingredient
**[V]**, and inside `ThingFilterUI.DoThingFilterConfigWindow` the two sliders are additionally
gated on `ThingFilter.allowedHitPointsConfigurable` / `allowedQualitiesConfigurable` — both
default `true` and recomputed from the allowed defs at `ResolveReferences` **[V]**. So a reclaim
bill can express both with no repeat-mode click and does not wait on
[#95](https://github.com/cjd721/Rimworld-Archinity/issues/95). What a new bill *defaults* to is
#95's.

### Where the player sees it

The recipe appears in the bench's add-bill float menu through `ITab_Bills.OptionsMaker`,
and the yield is visible as items dropping at the bench.

**The return fraction cannot be shown on the info card.** The only slot is
`RecipeDef.SpecialDisplayStats`' `EfficiencyStat` line, which requires setting
`efficiencyStat` — which does nothing, but would print the number as though it did [V]. The
fraction therefore goes in the recipe `<description>` as prose. Menu legibility with this
many recipes on one bench is `COLONY.md` § *The add-bill menu shows what matters now*
([#161](https://github.com/cjd721/Rimworld-Archinity/issues/161)).

### Cost

| Piece | Kind | Estimate |
|---|---|---|
| `smeltable` flip, 7 targets | XML `PatchOperationAdd` | ~40 lines, one `Patches/` file |
| `Archinity_ReclaimApparel` / `_ReclaimGear` | XML RecipeDefs | ~70 lines |
| dedicated reclaim bench (optional) | XML ThingDef | ~50 lines |
| era attachment (`researchPrerequisite`, `recipeUsers`) | XML | ~10 lines; keys from #30 |
| *"Do until you have X"* | C#: `workerCounterClass` subclass of `RecipeWorkerCounter` | ~30 lines, `Archinity.Core` |
| yield scaled by HP or quality, or a non-25% fraction | C#: Harmony postfix wrapping `Verse.Thing.SmeltProducts`' `IEnumerable<Thing>` result | not needed (COLONY requirement) |

**Nothing is selected; route choice is #119's.** Rows 1–4 are the **verified available
mechanism** and the shape the build takes. Row 5 is a named escalation above that (T-58,
*Failure and recovery*). Row 6 is not needed: the requirement's 50% return and
condition-blind yield are both expressible in XML, and the postfix was the only way to
express a fraction off the 25% quanta or a yield that depends on condition.

**No mod needs to be sourced.** Nothing in the corpus carries this, and nothing needs to:
the verdict for the sourcing ledger
([#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)) is *author from nothing, in
XML*.

---

## Persistence and multiplayer

**No new state.** RecipeDefs and ThingDefs are defs; bills are already scribed by
`BillStack`. Adding these to a running save needs no migration — the recipe simply appears
in the bench's add-bill menu on next load.

**Removing one later is safe and loud** [V]: `BillStack.ExposeData` drops any bill whose
`recipe` resolved null at `ResolvingCrossRefs` and logs *"Some bills had null recipe after
loading."*

**Zero synchronization work.** The only `Rand` on the path is `GenMath.RoundRandom` inside
`SmeltProducts`, reached from the already-synced bill-completion path — the same path VFE
Medieval 2 runs `Rand.Chance` in today (`docs/engine/facilities-and-recipes.md` § *Crafted
quality is pawn-only in vanilla*; `CODING_STANDARDS.md` § *The two gates*). Nothing here is
cached per client, and nothing reads `ModSettings`, `Prefs` or `Find.CurrentMap`.

---

## Failure and recovery

**A `Smelted` recipe silently ignores `efficiencyStat` and `workTableEfficiencyStat`**, and
displays them anyway. `GenRecipe.MakeRecipeProducts` computes `efficiency` from both fields
and passes it to `SmeltProducts`, which discards it for a hardcoded `0.25f` [V]. The two
sibling methods immediately above it — `ButcherProducts` and `StoneBlockProducts` — both use
the argument, so the field reads as live. `RecipeDef.SpecialDisplayStats` compounds it by
emitting the `EfficiencyStat` info-card line whenever `efficiencyStat != null`. No log
line, no config error, and the info card asserts the opposite of the truth. Registered as
[`docs/TRAPS.md` **T-56**](../TRAPS.md), from
[#82](https://github.com/cjd721/Rimworld-Archinity/issues/82).

**`RecipeDef.smeltingWorkAmount` is honoured by identity only.** `WorkAmountTotal` reads
`if (this == RecipeDefOf.SmeltOrDestroyThing && thing.Smeltable)` [V] — a
**reference-identity** test against that one def, so the field is silently ignored on any
recipe of ours. [`docs/TRAPS.md` **T-57**](../TRAPS.md).

**A recipe with any `specialProducts` can never offer *"Do until you have X"*.**
`RecipeWorkerCounter.CanCountProducts` returns `false` whenever `specialProducts != null`
[V], so the repeat-mode button omits `TargetCount` with no explanation.
[`docs/TRAPS.md` **T-58**](../TRAPS.md). Vanilla hit this
itself and left the evidence in XML: `ExtractMetalFromSlag` carries a commented-out
`<specialProducts><li>Smelted</li></specialProducts>` above the note *"Switched to standard
products so we can do 'do until you have X'"*. **We cannot take that escape**, because a
fixed `products` list is exactly the intermediate noun the no-chains rule in
`docs/PLOT.md` § *Campaign in play* forbids. The supported fix
is `RecipeDef.workerCounterClass`, a plain XML `Type` field, with vanilla's
`RecipeWorkerCounter_MakeStoneBlocks` as the working precedent — it overrides
`CanCountProducts` to `true` and counts a whole `ThingCategoryDef` [V], which is precisely
the shape *"do until you have 500 cloth"* wants. Until that is written, reclaim bills are
Forever / Repeat-N only, which is a liveable floor rather than a failure.

**Campaign softlock risk: none.** Recycling adds material and removes nothing. The failure
mode if the stuff patch silently misses is that reclaim bills produce zero output — visible
within one bill, and caught before shipping by the match-count annotations
(`tools/patch_check.py`).

---

## Status

**Evidence class: READ.** Settled against decompiled RimWorld 1.6
(`RimWorldWin64_Data/Managed/Assembly-CSharp.dll`), vanilla and DLC defs, and a
control-validated wide pass over both corpus roots plus `common/RimWorld/Data/`.

- **Verified available mechanism:** `SpecialProductType.Smelted` returns the exact stuff a
  thing was made of, with no intermediate resource, gated on `smeltable` [V].
- **Verified:** the 25% hardcode, the ignored `efficiency` argument, the repeated-entry
  multiplier, the `TargetCount` block, the venue inventory, relic protection, `intricate`
  exclusion [V].
- **Proposed, not selected:** the era, the bench, and whether a dedicated bench ships at
  all. The return fraction is the requirement's 50%. **Nothing in this document is
  selected** — rows 1–4 of the cost table are the shape the build takes, not a commitment
  to build it.
- **[I]:** that the composed build behaves as designed — nothing has been built; that no
  other engine return path is stuff-aware; and **every corpus-sweep negative below**, which
  is a metadata-heap or label hit and inferential by the method's own rule.

Established by [#82](https://github.com/cjd721/Rimworld-Archinity/issues/82).

---

## Available mechanisms

### Vanilla and DLC

Core ships `SmeltWeapon`, `SmeltApparel`, `SmeltOrDestroyThing`, `DestroyWeapon` and
`DestroyApparel`, all on `ElectricSmelter` alone [V]. `SmeltApparel`'s fixed ingredient
filter disallows `AllowNonSmeltableApparel`, so in practice it reaches only metal armour —
which is the whole shape of the problem, and the flag flip is the whole shape of the fix.

`intricate` resources are never returned: `ComponentIndustrial`, `ComponentSpacer`,
`Chemfuel`, every Biotech subcore via the abstract `SubcoreBase`, **and Biotech's
`MechResourceBase`** — which is the one that keeps
mech-derived resources out of a reclaim yield [V]. That is desirable — reclaiming power
armour must not print free components.

### The corpus — what does not exist, and where it shaped the build

The wide pass ran over `steamapps/workshop/content/294100/` and
`steamapps/common/RimWorld/Mods/` with `-g '!**/obj/**'`, ASCII control `SmeltProducts` and
UTF-16 control `Cannot get AdjustedCostList` both returning the vanilla assembly. The
method doc's `--encoding utf-16le` form was not used —
[#103](https://github.com/cjd721/Rimworld-Archinity/issues/103).

- **`SmeltProducts` across every `.dll` in both roots: zero mods** [I]. Nothing in the
  corpus appears to call, override or patch the return path. **A metadata-heap sweep is
  inferential by the method's own rule** — it reads names out of the `#US` / metadata
  tables, not call graphs, and a mod reaching the path by reflection or by a computed name
  would not appear.
- **`Smelt` as a metadata name: one mod** [I] — VEF's `PipeSystem.dll`, carrying
  `onlySmeltable` on `CompProperties_ConvertThingToResource`. The hit itself was depth-read
  [V]; the *only one* is the inferential half. A thing → pipe-net-resource converter;
  definitionally the intermediate noun, ruled out.
- **`specialProducts` in mod XML: three mods** [V]. Medieval Overhaul
  (`DankPyon_ExtractMetalFromScrap`, consuming `DankPyon_BrokenWeapons` — the forbidden
  shape, and `docs/data/PARTS-BIN.md` already REFUSEs MO's ingot chain for the same
  reason), More Archotech Garbage, and Ushanka's Glittertech Expansion (mechanoid
  disassembly — the source of the doubled-`specialProducts` precedent above). None recycles
  gear into its own material.
- **`recycl` across mod XML: 12 mods, none of them this** [V]. Replimat (corpse →
  feedstock), VQE Ancients and VFE Props & Decor (`ArchiteRecycler`, `PulpRecycler` — set
  dressing, see `docs/data/archon-asset-inventory.md`), pollution pumps, android shredding.
- **Vanilla Recycling Expanded is not on disk** [V]. `VRecyclingE_*` appears only inside
  conditional patch files shipped by Better Architect Menu's patch pack (`3563882422`),
  More Gravship Workbenches (`3714981583`) and VQE Ancients (`3618306875`) — none of which
  is the mod. Its own design (`VRecyclingE_AlloypackSplitter`, `VRecyclingE_WasteCrate`) is
  the intermediate-noun shape regardless.
- **Labels matching unravel / shred / dismantle / disassemble / salvage / reclaim across
  both roots: nothing that takes apparel** [I] — a label sweep can only find the words we
  thought to search for, and a mod naming the same behaviour something else is invisible
  to it.

**Nothing in the 155-mod corpus recycles gear back into the material it was made of [I]** —
the conclusion rests on the sweeps above, and each of those is a metadata or label hit
rather than a read of every mod. That is fine, because vanilla does — it is simply gated on five metals, and the gate is XML.

---

## Verification

Supported by decompiled 1.6: `Verse.Thing.Smeltable`, `Verse.Thing.SmeltProducts`,
`Verse.GenRecipe.MakeRecipeProducts`, `RimWorld.CostListCalculator.CostListAdjusted`,
`Verse.RecipeDef.WorkAmountTotal`, `Verse.RecipeDef.SpecialDisplayStats`,
`Verse.RecipeWorkerCounter.CanCountProducts`, `Verse.RecipeWorkerCounter_MakeStoneBlocks`,
`RimWorld.BillStack.ExposeData`, `RimWorld.SpecialThingFilterWorker_Smeltable`,
`Verse.ThingDef.PotentiallySmeltable`, `Verse.ThingDef.ConfigErrors`.

**Before the def work is called done**, all five of `CODING_STANDARDS.md` § *Verification*
must run clean, and every PatchOperation in the stuff patch must carry an
independently-derived `<!-- expect: N -->`.

**Observable checks.**

1. Build a `CraftingSpot`, add the reclaim bill, feed it a cloth t-shirt of known
   `costStuffCount`. Expect `round(costStuffCount × 0.25 × <Smelted entries>)` cloth,
   ± rounding.
2. Feed it a component-bearing item. Expect the stuff back and **no** components.
3. Feed it a legendary and an awful item of the same def and stuff. Expect identical yield
   — confirming condition-independence rather than assuming it.
4. Feed it a relic. Expect it to be excluded from the bill entirely.
5. Open the bill's repeat-mode button. Expect **no** *"Do until you have X"* until a
   `workerCounterClass` ships.

**Needs an in-game check, not reading:** that flipping `smeltable` on textile and leather
stuffs has no unlocated consumer elsewhere in the assembly — one colony-load with the patch
active, watching for new config errors and for unexpected changes to storage filters
showing *allow smeltable* / *allow non-smeltable*.

---

## Outstanding decisions

`docs/requirements/COLONY.md` § *Obsolete gear goes back to the material it was made of*
owns reclaiming: **the return fraction is 50%** (two `Smelted` entries), and **yield does
not depend on condition or quality** — what the player filters is which items are fed to
the bench, not what each is worth once fed. Two parameters sit elsewhere:

- **Which era the reclaim recipe unlocks in.** The research gate
  (`docs/requirements/ERA.md` § *The acquisition gate*), placed by
  [#30](https://github.com/cjd721/Rimworld-Archinity/issues/30)'s progression row.
- **Which bench carries it.** The mechanism supports a dedicated reclaim bench or existing
  benches at the same cost (*New code and defs* › 3); which ships is
  [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.
