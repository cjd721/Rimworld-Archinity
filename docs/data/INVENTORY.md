# Inventory & bucketing ledger

What is actually in the game right now, and what we are doing with each of it.
Four buckets: **keep as is / keep with changes / on the fence / not keeping.**

Generated from the **live** `ModsConfig.xml`, not the repo snapshot, by
`tools/inventory.py`. Raw dumps in `scratch/inventory-research.csv` and
`scratch/inventory-things.csv`. Re-run the tool after any load-order change.

First pass, 2026-08-22. Verdicts marked **[?]** need Conrad.

---

## The numbers

70 active mods. **293 research projects** (281 content + 12 TechBlock
lock/theory infrastructure) and **3,961 ThingDefs**, of which **3,114** are
decision-relevant — building, apparel, weapon, item, food/drug, plant, bodypart.
The other 847 are motes, projectiles, filth, corpses and pawn defs, which are
not things we choose to keep.

| Era | Projects | Points | Carried by |
|---|---:|---:|---|
| Neolithic | 35 | 30,100 | VFE Classical 18, Core 8, MO 6 |
| Medieval | 70 | 54,850 | **MO 45**, Core 8, VFEM2 7, Royalty 4 |
| Industrial | 96 | 148,900 | Core 49, Biotech 11, VFE Pirates 6 |
| Spacer | 42 | 105,900 | Core 12, VGE 7, Royalty 5 |
| Ultra | 38 | 137,000 | Glittertech 18, Royalty 7, GravTech 6 |

Items, top contributors of the 3,114:

| Mod | Things | Shape of it |
|---|---:|---|
| Medieval Overhaul | 1,124 | 538 buildings, 179 items, 125 apparel, 101 food/drug |
| Core | 557 | the baseline |
| Odyssey | 254 | 133 buildings |
| VFE Medieval 2 | 114 | overlaps MO heavily — see collisions |
| VQE Ancients | 110 | **108 buildings** — the altar reskin source |
| VGE Chapter 1 | 104 | 78 buildings, the gravship |

---

## Three things the docs have wrong

Found while building this. All three are checkable in one look at the live
config; none are judgement calls.

1. **VFE Tribals is not enabled.** `sys/01`, `MAP.md` and `sys/02` all record
   D1 as *resolved: in*, on the basis that Conrad enabled it and booted a game.
   The live `ModsConfig.xml` (2026-08-22 13:03) has no `oskarpotocki.vfe.tribals`.
   The mod is subscribed and fully downloaded at workshop `3079786283`, 5.4 MB —
   it is simply switched off. Everything `sys/02` says about the Neolithic era
   depends on it.

   **Resolved 2026-08-22: the docs are right — enable it.** It needs turning on
   in the mod list and the config re-snapshotting. All bucketing from here
   assumes it is in.

2. **`archinity.altar` is still not in the load order.** Confirmed still true.
   Unchanged since `sys/01` flagged it.

3. **The duplicate-DLC defect is fixed.** The live config lists each DLC once.
   `sys/01` work item can be closed.

Lower-stakes, worth a look: `sys/01` requires TechBlock to load *after* all
content mods. It currently sits at position 41 of 70, ahead of VFE Classical,
VFE Medieval 2, Medieval Overhaul, VCE, VGE and GravTech. But `MAP.md` also
records that `BlockTechs()` runs at `[StaticConstructorOnStartup]`, which by
definition fires after the whole def database is loaded and resolved. Those two
statements cannot both matter. Verify which before spending a reorder on it.

---

## How to bucket this — the method

Three different units, because the three populations are not alike.

**Research: one verdict per project.** 281 is a finishable list. Neolithic and
Medieval are 105 of them and are the eras we are actually building, so they get
verdicts now. Industrial and up (176) are ~300 days of play away and land in the
`sys/07` balance pass; they get a mod-level verdict here and a project-level one
later.

**Items: one verdict per set or chain, never per def.** 3,114 individual
verdicts is weeks of work that produces the same answers as ~50. The evidence is
Medieval Overhaul: its 538 buildings are 113 storage variants on one research,
107 more on another, and 234 with no research gate at all that are scenery props
and ruins debris. That is six decisions wearing 538 costumes. The sets are the
real objects; the defs are stuff-variants of them.

**Duplicates: one verdict per collision.** 62 labels exist in two or more mods
at once — two arbalests, two hearths, two castle walls, two winemaking chains.
This is a mechanical workstream: pick one, hide the other. It is separate from
the keep/cut question because both members of a pair are usually fine, and the
problem is only that there are two.

---

## Bucket 1 — Keeping as is

| What | Size | Note |
|---|---:|---|
| Core + Royalty + Ideology + Biotech + Odyssey research | 122 projects | The baseline. Individual retiers below, but the set stays. |
| Core + DLC items | 1,116 things | Same. |
| VFE Tribals' gathering research | 13 projects / 760 pts | Exactly the "research grants jobs and gizmos" pattern the Ideology asks for, at `Animal` techLevel so TechBlock's Neolithic lock sits above it correctly. Cheap and clean — **if it gets switched on.** |
| VQE Ancients | 108 buildings | The reskin source for the whole altar chain. Kept mechanically; renamed narratively. That is a `QUESTLINE.md` job, not a cut. |
| Glittertech Expansion | 18 projects / Ultra | Endgame, on-theme, correctly tiered. |
| MO QoL set | ~8 buildings | Mine shaft, crane, carrier birds (minus the paper chain), flour mill, cheese press, scarecrow, sprinkler, trough. Already the `sys/04` keep list. |
| MO beekeeping / brewing / winemaking | 3 chains | Opt-in roleplay, close to right out of the box. |

## Bucket 2 — Keeping with changes

**VFE Classical's 18 Neolithic projects.** Every one costs exactly 1,200, so
they are **21,600 of the Neolithic era's 30,100 points — 72%** — on a flat line
with no curve at all. Separately, at least seven are Classical-era content
sitting in the Neolithic tier: `VFEC_BronzeWorking`, `VFEC_CementMaking`,
`VFEC_LegionnaireArmor`, `VFEC_CenturionArmor`, `VFEC_HeavyShieldMaking`,
`VFEC_RoadBuilding`, `VFEC_Scorpion`. Retier those to Medieval and recost the
remainder onto a curve. See also *On the fence*, because there is a case for
cutting the mod outright.

**MO's cooking stack.** `DankPyon_BasicCooking` → Intermediate → Advanced, plus
Grill, StewPot, Smoker, Oven, Presser — 8 projects — plus VCE's `VCE_Grilling`,
`VCE_CheeseMaking` and `VCE_StewCooking`. Eleven research projects and roughly
six benches for one domain. `sys/03` wants one core stove plus three or four
augments. This is the single largest consolidation target in the project.

**MO's weapon triplicates.** Basic / Military / Noble × Polearms / Maces /
Blades is nine projects that all say the same thing three times. Collapse to two
rungs, or keep three and merge the families so one project advances all of them.

**MO's storage set.** 113 buildings behind `DankPyon_RusticStorage` — barrels of
every ore, crates in every size, filled shelves. We already run three storage
mods (Neat Storage 27, Fridge 7, Gravship Storage 8). Keep the medieval look,
cut the variant count hard.

**MO's decorative furniture and props.** 107 things behind
`DankPyon_RusticFurniture` and 234 with no gate at all. Scenery costs nothing
and never becomes required input, so most of this stays — but audit the ~40
`empty bottle` / `empty plate` / `empty cooking pot` defs, because those *do*
enter the item pool and are exactly the dilution the Ideology warns about.

**Two re-parentings that must happen before the cuts.** Both are the
`CLAUDE.md` silent-failure trap, and both are large:

- `DankPyon_RusticFurniture` is a child of `DankPyon_Lumber`, which is the head
  of the kill-listed wood chain. RusticFurniture gates **107 things** directly
  and is the prerequisite for RusticStorage (**113 more**), Presser, CarrierBirds
  and TextileSpinning. Cut Lumber without re-parenting first and roughly 220
  buildings become free, with no research at all.
- `DankPyon_Silk` is a child of `DankPyon_TextileSpinning`, which is cut. Silk is
  on the keep list.

**Individual retiers already known.** `VFES_SiegeEquipment` (raw def says
prerequisite `Smithing`, not `DankPyon_Engineering` as `MAP.md` records — verify
whether something patches it), `VFE_Res_Sprinkler` off `Machining`,
`PlateArmor`'s two armour rungs split, `HeavyBridges` and `Piano` to Medieval.

## Bucket 3 — On the fence

| Question | Why it is genuinely open |
|---|---|
| **VFE Classical, whole mod** **[?]** | 18 projects, 27 items, and 72% of the Neolithic research budget. Cutting it leaves the Neolithic at 17 projects / 8,500 points, which is thin for a 60–120 day era. Keeping it means the Neolithic era is substantially Roman, against Medieval Overhaul's dark-fantasy medieval. This is a taste call, not a mechanics one. |
| **Two alchemy systems** | `DankPyon_Alchemy` (1,000 pts, gates 28 things, and is the prerequisite for Steel, Tar and Gunpowder) vs `VFEM2_Alchemy` (1,500 pts, gates 18 things, nothing depends on it). MO's is load-bearing; VFEM2's is not. Cutting VFEM2's is the cheap direction. |
| **Two gunpowder routes** | `DankPyon_Gunpowder` vs `VFEM2_Matchlocks`. Both are Medieval firearms and one is enough. |
| **Three siege systems** | MO's Trebuchet / Ballista / RepeaterBallista, `VFES_SiegeEquipment`, and `VFEC_Scorpion`. |
| **`DankPyon_Steel`** (2,000 pts) | Alchemy → steel. `metalChain` is off as a setting, which may already make this inert. Needs verifying in game, not guessing. |
| **Dark Ages: Medieval Tools** | 11 things, zero research. `sys/01` already recommends skipping it. Confirm and drop it from the load order. |
| **The 62 label collisions** | Mechanical, but each needs a pick. Heaviest overlap is MO × VFE Medieval 2: arbalest, mead, wine, fur bed, double fur bed, hearth, castle wall, grape must. |
| **Two grape plants / two wine chains** | `DankPyon_Plant_Grape` vs `VFEM2_Plant_Grape`. No compat patch exists anywhere. Already flagged in `sys/01`. |

## Bucket 4 — Not keeping

The `sys/04` kill list, now with the actual def targets and the dependency
damage each one does. **Order matters** — re-parent, then neuter, then delete.

| Target | Cost | Depends on it | Safe to cut? |
|---|---:|---|---|
| `DankPyon_Lumber` — wood chain | 200 | `DankPyon_RusticFurniture`, 14 things | **No, not yet.** Re-parent RusticFurniture first or ~220 buildings go free. |
| `DankPyon_TextileSpinning` — spinning + linen | 600 | `DankPyon_Silk`, 1 thing | **No, not yet.** Re-parent Silk first. |
| `DankPyon_Exploration` — paper, cartography, maps | 1,800 | nothing, 2 things | **Yes.** Clean cut. |
| `DankPyon_Plasteel` — labelled "Mithril" | 4,000 | nothing, 0 things | **Yes.** Clean cut. |
| `DankPyon_PlowedSoil` | 300 | nothing, 0 things | **Yes.** Buggy in play; scarecrow and sprinkler cover it. |
| Ingredient bloat | — | — | MO's 19 alchemy ingredients + 3 condiments, plus VCE's 44 food/drug defs. Curate to a target number, then cut to it. |
| Added plants | ~35 | — | MO 29, VCE 3, others. Keep vanilla plus a curated few, tiered across basic/intermediate/advanced agriculture. |
| Crossbow line, *if* no-new-metals holds | 1,100 | `DankPyon_Ballista` depends on Crossbow | **Verify first.** `sys/04` records crossbow / heavy crossbow / handgonne as needing `DankPyon_IronIngot` and therefore dead. If so they are already inert and cutting is tidying, not balance — but Ballista's prerequisite has to move. |

---

## What this pass did not cover

- **Neolithic and Medieval research** is now worked to a per-project verdict in
  `RESEARCH-NEO-MED.md`. That doc supersedes this one for those two eras; this
  file stays the whole-database view.
- **Industrial / Spacer / Ultra research** — 176 projects, mod-level verdicts
  only. Project-level in the `sys/07` balance pass.
- **Apparel and weapons as a set** — 279 apparel and 251 weapons across all
  mods, not yet bucketed. `sys/05`'s era-appropriate-gear work needs this and
  should drive it.
- **The 62 collisions individually** — listed as a workstream, not resolved.
- **Anything VFE Tribals adds** — it is not in the active set, so it is not in
  the CSVs. Its 13 projects and 13 things were counted separately by hand.
