# Items and materials

What survives being acquired centuries before its era, and how stuff-based armour
actually adds up when the colony is still Neolithic.

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
