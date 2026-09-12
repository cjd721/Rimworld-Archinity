# Items and materials

What survives being acquired centuries before its era, how stuff-based armour
actually adds up when the colony is still Neolithic, what the engine will give back
when an item is unmade, and the vanilla carrier for an authored readable record.

Verified against decompiled RimWorld 1.6.4871 unless an entry says otherwise.
These are *verified available mechanisms*, not commitments to use them —
selection happens in `docs/specs/`.

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

Genepack decay, the powered `GeneBank` that is the only thing that stops it, and
why the `DeteriorationRate` must not be patched to 0, are the trap register's:
see `docs/TRAPS.md` T-25. The practical scheduling consequence is that genepack
rewards are viable **only from Industrial onward**, which is fine: that is
exactly when guaranteed-specific-gene rewards are wanted anyway.

---

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

The `CraftingSpot`-as-only-Neolithic-venue claim above was re-read against 1.6 and
is **confirmed [V]**: `CraftingSpot` is a real `Building_WorkTable` carrying
`ITab_Bills`.

---

## Recycling and smelting

**`SpecialProductType.Smelted` is the engine's only stuff-aware return path**, and
it returns the stuff def itself, so an intermediate resource is not expressible on
it at all [V]. The chain is `GenRecipe.MakeRecipeProducts` → `Thing.SmeltProducts`
→ `ThingDef.CostListAdjusted(Stuff)`, and `CostListAdjusted` returns the def's fixed
`costList` **plus the stuff at crafting cost**. A thrumbofur parka's cost list *is*
`Leather_Thrumbo × 80`. `SmeltProducts` also appends `def.smeltProducts` on top.
The two sibling return paths cannot do this: `products` is a fixed
`ThingDefCountClass` list and `Butchery` reads the equally fixed
`ThingDef.butcherProducts`.

**The gate is two flags, and the stuff-side one is why recycling feels absent in the
early eras.** `Thing.Smeltable` requires **both** `def.smeltable` and, when the def
`MadeFromStuff`, `Stuff.smeltable` — and it hard-returns false for a relic [V].
Every vanilla apparel and weapon def is already `smeltable` through its abstract
parent, but **vanilla marks only Silver, Gold, Steel, Plasteel and Uranium as
stuff-smeltable** (`Jade` is explicitly false; cloth, synthread, devilstrand,
hyperweave, wood, every wool and every leather leave it at its `false` default) [V].
So a cloth parka is filtered out of the bill before a pawn walks to the bench.

**Six vanilla apparel defs override `smeltable` to false**, and none of them is
`MadeFromStuff`: `Apparel_PsychicFoilHelmet`, both psychic lances,
`OrbitalUtilityBase`, `Apparel_CerebrexNode` and `PsychicApparelBase` [V].

**The return fraction is tunable in 25% steps and no finer.** `specialProducts` is a
`List<SpecialProductType>` rather than a set, and `MakeRecipeProducts` loops it, so
repeating `<li>Smelted</li>` runs the products pass again — ×2 is 50%, ×3 is 75%.
The shipped precedent is Ushanka's Glittertech Expansion doubling `<li>Butchery</li>`
on `USH_DisassembleCorpseMechanoid` [V]. That the two independent
`GenMath.RoundRandom` draws aggregate to the intended fraction, modulo rounding
variance, is **[I]**.

Three things about this path fail silently and belong to the register rather than
here — the discarded `efficiency` argument and the info-card line that advertises
it, `smeltingWorkAmount` honoured only by def identity, and *"do until you have X"*
being unavailable to any recipe carrying `specialProducts`. They are
`docs/TRAPS.md` **T-56**, **T-57** and **T-58**; read them before authoring a
reclaim recipe.

---

## `Verse.Book` is a core, non-Anomaly authored-record carrier

Worth recording so the next ticket reaching for "studiable" or "readable" does not
re-run the Anomaly rejection against the wrong type: **`RimWorld.CompStudiable` is
the unrelated Anomaly class** — its `AnomalyKnowledge` and `KnowledgeCategory` both
return early on `!ModsConfig.AnomalyActive` and its whole payload is
`anomalyKnowledgeGained` against a `KnowledgeCategoryDef` [V]. `Verse.Book` shares
nothing with it.

`Book` is core, per-instance and readable: `DescriptionDetailed` renders it in the
info card, `GenerateBook(Pawn, long?)` is `public virtual`, and `OnBookReadTick`
runs every `BookOutcomeDoer` scaled by `StatDefOf.ReadingSpeed`. Vanilla ships
`BookOutcomeProperties_GainResearch` and `_GiveQuest`; only the mental-break branch
consults `ModsConfig.AnomalyActive`. `VanillaBooksExpanded.Newspaper : Book` is the
1.6 subclassing precedent [V].

**Two catches, both load-bearing if you want to author the text** [V]:

- `Book.title` and `description` are **`private` fields** (the public accessor is the
  `Title` getter), both scribed. A subclass cannot write them, so authoring a Book's
  prose needs reflection or a Harmony patch.
- `Book.PostPostMake` and `Book.PostQualitySet` both call `GenerateBook()`, which
  **overwrites** title and description from the grammar packs. An authored string
  assigned to an instance is replaced unless `GenerateBook` itself is overridden.
