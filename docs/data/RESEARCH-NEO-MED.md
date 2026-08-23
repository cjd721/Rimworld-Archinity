# Neolithic & Medieval research — recommendation for review

Every research project in the two eras we are actually building, with a verdict
each. **For Conrad's review.** Nothing here is executed.

Source data: `tools/inventory.py` against the live `ModsConfig.xml`, dumps in
`scratch/inventory-research.csv` / `scratch/inventory-things.csv`. Costs and
prerequisites are read with `ParentName` inheritance resolved. Unlock counts are
ThingDefs only — a project marked *no things* may still unlock recipes, terrain
or plants, and that is called out where it matters.

Assumes **VFE Tribals is enabled** (decided this session). Its 13 projects are
included; they are not in the CSVs because the mod is still switched off.

---

## The headline

The two eras carry **30,100** and **54,850** points today. `sys/07` approves a
Medieval three-leap structure totalling **~30,900**, so Medieval is running at
**1.8× the approved budget**, and the Neolithic's weight is in the wrong place —
72% of it is one mod that is not really Neolithic.

The recommendation, in one line: **move VFE Classical wholesale into the
Medieval era where it belongs, cut 15 Medieval projects that are duplicates or
dead ends, and pull six genuinely primitive Medieval Overhaul projects down into
the Neolithic.** That lands Medieval at ~31,800 against an approved ~30,900 —
within 3% — without authoring a single new project.

| | Now | Proposed |
|---|---:|---:|
| Neolithic | 30,100 | ~7,500 + 760 (Tribals) + 2,200 (retiered down) = **~10,460** |
| Medieval | 54,850 | **~31,800** (excludes Classical — see below) |

---

## Answering the Classical question directly

*"Is there anything that could replace this in the Neolithic period?"*

**Nothing on the shelf.** Subscribed-but-inactive mods are RimFantasy-MO Edition,
VFE Empire, VFE Deserters, VFE Insectoids 2, Dwarves of the Rim, Faction-Elves,
Nice Research Tab and HugsLib. Every one is Medieval or later, a race mod, or
UI. The only Neolithic mod on the shelf is VFE Tribals, which is going in anyway.

So there are four real options, and the interesting thing is that the best one
is not a replacement at all.

**1. VFE Tribals fills the *shape*, not the volume.** Its 13 projects grant the
grow job, the mining designator, bows, medicine, culture — research that hands
you *capability*, which is the exact pattern `Player Progression Ideology.txt`
praises and the exact thing Classical does not do. Classical buys 22 things for
21,600 points. Tribals buys the entire early job set for 760. On
capability-per-point it is roughly thirty times denser. But it is over in 20–30
days by design, so it does not fill a 60–120 day era on its own.

**2. Retier Medieval Overhaul content downward.** MO has 45 Medieval projects and
several are primitive in character, not medieval: the grill, the stew pot, basic
blades, the hunting bow, rustic furniture, the oven. Moving those down does
double duty — it fills the Neolithic *and* relieves a Medieval tier that is
already 1.8× over budget. This is the strongest move available because one
change fixes both problems.

**3. Recost what survives.** Points are a free variable; if the worry is era
*length* rather than era *content*, raise `baseCost` on the survivors. This is
the option that produces a player staring at a progress bar with nothing to do,
which is the Ideology's named failure mode. Use it to fine-tune, not to fill.

**4. Author our own in `Archinity.Pacing`.** Full control, on-theme, and the
Neolithic is where the altar's first Chronicle beats land anyway. Real authoring
cost, but it is the only option that makes the Neolithic *ours*.

### What I actually recommend

**Retier all 18 Classical projects to Medieval, not just the seven obvious ones.**

Classical is Roman. Bronze working, cement, roads, thermae, togas, legionary and
centurion armour, the scorpion — none of that is neolithic in any reading. It
was never Neolithic content; it was Neolithic-*tagged* content, and TechBlock
reads that tag literally. Moving it up is a correction, not a compromise, and it
buys a better story: **Roman → dark-ages medieval** is a real historical descent
that reads well against Medieval Overhaul's dark fantasy, where *tribal → Roman*
never did.

Then the Neolithic reads: Tribals gathering → Core neolithic → MO basics. That
is a coherent primitive era with capability-granting research at the front of it.

**The catch, stated plainly:** this adds 21,600 to a Medieval era already 1.8×
over budget. Classical cannot move up *and* survive intact. Either it moves up
and gets cut hard within itself — I would keep roughly eight and drop ten — or
it moves up and `requiredPointsMedieval` absorbs the difference at 0.75. That
second decision is `sys/07`'s and I have not pre-empted it. **The Medieval table
below excludes Classical entirely** so the two decisions stay separable.

Three Classical projects are worth knowing about either way: `VFEC_RoadBuilding`
unlocks nothing found anywhere in the mod except a faction reference — 1,200
points for nothing. `VFEC_BronzeWorking` unlocks one recipe. `VFEC_Mosaics`
unlocks floor terrain. If Classical is cut hard, those are the first three out.

---

## Neolithic

### Keep as is — 13 projects, 760 points

All VFE Tribals, all at `Animal` techLevel so TechBlock's Neolithic lock sits
correctly above them. These are the model the Ideology asks for: research that
grants jobs, gizmos and designators rather than recipes.

`VFET_Fire` 50 · `VFET_Agriculture` 50 · `VFET_Cultivation` 50 ·
`VFET_Medicine` 70 · `VFET_AnimalHandling` 50 · `VFET_Mining` 50 ·
`VFET_Construction` 50 · `VFET_Furniture` 70 · `VFET_Tribalwear` 50 ·
`VFET_Hunting` 50 · `VFET_Weapons` 50 · `VFET_Bow` 70 · `VFET_Culture` 100

### Keep as is — 13 projects, 6,700 points

| Project | Cost | Source | Note |
|---|---:|---|---|
| `Brewing` | 400 | Core | |
| `PassiveCooler` | 400 | Core | |
| `RecurveBow` | 400 | Core | Prereq for `Greatbow` and `DankPyon_HuntingBow`. |
| `PsychoidBrewing` | 500 | Core | Prereq for `VFEM2_Alchemy` — see Medieval cuts. |
| `Pemmican` | 500 | Core | Prereq for `VFEM2_Beekeeping`. |
| `TreeSowing` | 1000 | Core | |
| `Cocoa` | 1000 | Core | |
| `Fishing` | 600 | Odyssey | |
| `MF_BasicFurniture` | 300 | VFurE | |
| `DankPyon_LeatherTanning` | 600 | MO | Head of the leather ladder `sys/07` audits. |
| `DankPyon_CandleMaking` | 300 | MO | Gates 6 buildings. Pre-electric lighting; earns its slot. |
| `DankPyon_BasicAgriculture` | 300 | MO | Tier 1 of the agriculture ladder. |
| `DankPyon_BasicCooking` | 400 | MO | Root of the whole cooking domain. |

### Keep with changes — 1 project

| Project | Cost | Change |
|---|---:|---|
| `Devilstrand` | 800 | Keep the project, but `sys/02` records it as a **circular Neolithic deadlock** under More Realistic Research — `BuildForProject` returns null at `techLevel <= Neolithic`, so its auto-generated gate cannot be satisfied. Needs an explicit empty `ManualAnalysisDef`. |

### Retier down from Medieval — 6 projects, 2,200 points

These are the Neolithic backfill. All Medieval Overhaul, all primitive in
character, all currently tagged Medieval.

| Project | Cost | Unlocks | Why it belongs here |
|---|---:|---|---|
| `DankPyon_Grill` | 200 | grill | A grill is not a medieval invention. |
| `DankPyon_StewPot` | 300 | 4 pots | Same. Cooking over a fire. |
| `DankPyon_BasicBlades` | 300 | cleaver, hatchet, woodcutter's axe, falchion | Three of the four are tools, not weapons. |
| `DankPyon_HuntingBow` | 500 | hunting bow | Sits behind `RecurveBow`, which is already Neolithic. |
| `DankPyon_RusticFurniture` | 300 | 107 things | **Must be re-parented off `DankPyon_Lumber` first** — see order of operations. |
| `DankPyon_Oven` | 600 | rustic oven, large oven | Bread predates the medieval era comfortably. |

### Not keeping — 3 projects, 1,000 points

| Project | Cost | Dependants | Verdict |
|---|---:|---|---|
| `DankPyon_PlowedSoil` | 300 | none, 0 things | Clean cut. Buggy in play; scarecrow and sprinkler cover the ground. |
| `VCE_CondimentsResearch` | 500 | none | Condiments are the canonical dilution failure `sys/04` names by name — salt and saffron. Clean cut. Also cut MO's 3 `DankPyon_Condiments` items with it. |
| `DankPyon_Lumber` | 200 | `DankPyon_RusticFurniture`, 14 things | Head of the kill-listed wood chain. **Not a clean cut** — see order of operations. |

### Moved out — VFE Classical, 18 projects, 21,600 points

Retiered to Medieval per the argument above. Listed there.

---

## Medieval

Excludes VFE Classical. Totals below are before Classical lands.

### Keep as is — 21 projects, ~14,150 points

The spine. Core's smithing and clothing lines, MO's production and agriculture
ladders, VFEM2's architecture and workshops.

| Project | Cost | Source | Note |
|---|---:|---|---|
| `Smithing` | 700 | Core | 52 things. The single most load-bearing Medieval project. |
| `ComplexClothing` | 600 | Core | 83 things incl. both tailor benches. |
| `ComplexFurniture` | 300 | Core | 100 things. Also gates the simple research bench, which is what ends the tribal phase. |
| `Stonecutting` | 300 | Core | |
| `CarpetMaking` | 800 | Core | No ThingDefs; unlocks terrain. |
| `Greatbow` | 600 | Core | |
| `DankPyon_IntermediateAgriculture` | 400 | MO | Tier 2 of the ladder. |
| `DankPyon_AdvancedAgriculture` | 600 | MO | Tier 3. Unlocks plants, not things. |
| `DankPyon_IntermediateCooking` | 400 | MO | Tier 2. Recipes only. |
| `DankPyon_AdvancedCooking` | 800 | MO | Tier 3. Recipes only. |
| `DankPyon_Smoker` | 600 | MO | Load-and-leave process building — `sys/03` says this class earns a standalone slot. |
| `DankPyon_Presser` | 600 | MO | Cheese press + apple juice. **Strip the paper press** from its unlocks; the paper chain is cut. |
| `DankPyon_Windmill` | 400 | MO | |
| `DankPyon_Watermill` | 400 | MO | |
| `DankPyon_Mining` | 1000 | MO | Mine shaft + medieval crane. Both on the `sys/04` QoL keep list. |
| `DankPyon_Engineering` | 1000 | MO | Well + advanced research bench. |
| `DankPyon_Jewelry` | 600 | MO | 20 things. Pure trade goods, no dilution risk. |
| `DankPyon_CarrierBirds` | 600 | MO | Keep — **without** the paper chain, per `sys/04`. |
| `DankPyon_Silk` | 600 | MO | **Must be re-parented off `DankPyon_TextileSpinning` first.** |
| `VFEM2_MedievalArchitecture` | 1200 | VFEM2 | Castle doors and gates. |
| `VFEM2_ComplexWorkshops` | 1800 | VFEM2 | Anvil, bellows, loom, chisel rack — this **is** the augment set `sys/03` is built around. Highest-value project in the era. |
| `VFE_Res_FarmingTechniques` | 300 | VFurE-Farming | Scarecrow. QoL keep list. |
| `MF_RoyalFurniture` | 800 | VFurE | |

### Keep with changes — 16 projects

**The cooking domain — 3 duplicate projects to drop (see cuts) and one bench
consolidation.** MO's grill / stew pot / smoker / oven / presser plus its
three-tier cooking ladder is ~6 benches for one domain. `sys/03` wants one core
stove plus three or four augments. The research stays; the *benches* consolidate.
That work belongs to `sys/03` and is noted here only so the two do not diverge.

**MO's weapon triplicates — six projects into two.**

| Now | Cost | Proposed |
|---|---:|---|
| `DankPyon_BasicPolearms` / `BasicMaces` / `BasicBlades` | 300 each | One **basic arms** project, ~600. (`BasicBlades` retiers to Neolithic instead — it is tools.) |
| `DankPyon_MilitaryPolearms` / `MilitaryMaces` / `MilitaryBlades` | 600 each | One **military arms** project, ~1,200. |

Nine weapon projects saying the same thing three times becomes two rungs. Saves
~900 points and, more importantly, four clicks of nothing.

**Individual changes:**

| Project | Cost | Change |
|---|---:|---|
| `PlateArmor` | 600 | Split into two rungs — already a `sys/07` work item. 28 things behind one node. |
| `LongBlades` | 400 | Overlaps `DankPyon_MilitaryBlades` — both unlock a longsword. Pick one owner for the shared weapons. |
| `DankPyon_ProtectiveClothing` | 1000 | Prereq for `ChainArmor`; keep, but it is the armour rung `VFEM2_Apparel_PaddedArmor` has **no gate at all** according to `sys/02`. Fill that hole here. |
| `DankPyon_ChainArmor` | 1500 | Keep. Second armour rung. |
| `DankPyon_Alchemy` | 1000 | **Keep — this is the surviving alchemy.** 28 things, and it is the prerequisite for Tar and Gunpowder. |
| `DankPyon_Gunpowder` | 1000 | Keep as the single gunpowder route. Cut `VFEM2_Matchlocks`, or keep Matchlocks and cut this — but not both. **[?]** |
| `DankPyon_Ballista` | 1000 | Keep as the single siege line. Absorb `DankPyon_HeavyCrossbow`'s arbalest into it. |
| `DankPyon_Crossbow` | 400 | Keep, but `sys/04` records crossbow and heavy crossbow as needing `DankPyon_IronIngot` and therefore **dead under no-new-metals**. Verify in game before trusting either. |
| `DankPyon_RusticStorage` | 400 | Keep the project, cut the 113 variants hard. We already run three storage mods. |
| `DankPyon_RoyalRusticFurniture` | 900 | Keep. Overlaps `MF_RoyalFurniture` on four labels — pick one. |
| `DankPyon_Tar` | 400 | Keep. Recipes only, feeds alchemy. |
| `NobleApparel` / `RoyalApparel` | 400 each | Keep, Royalty. |
| `Harp` / `Harpsichord` | 500 each | Keep. Cheap flavour, and `sys/02` wants `Piano` moved down here too. |
| `VFEM2_Heraldry` | 1200 | Keep. `sys/02` notes MO's heraldic greathelm and hauberk variants have **no research gate** — attach them here. |
| `VFEM2_Beekeeping` / `VFEM2_Wine` | 500 / 600 | Keep as opt-in roleplay per `sys/04`. **Resolve the two-grape collision first** (`DankPyon_Plant_Grape` vs `VFEM2_Plant_Grape`). |

### On the fence — 3 projects, 3,400 points

| Project | Cost | The question |
|---|---:|---|
| `VFEM2_Matchlocks` | 600 | Arquebus, musket, flintlock, hand cannon — better gun coverage than MO's four thrown fire-pots. If gunpowder is a Medieval capstone, this may be the one to keep and `DankPyon_Gunpowder` the one to cut. Inverts the row above. **[?]** |
| `DankPyon_TreeGriffonBerry` | 900 | A single plant behind a 900-point gate, requiring `Cocoa` + advanced agriculture. Flavour, but it is exactly the "one more plant" dilution the Ideology warns about. |
| `DankPyon_Trebuchet` | 1000 | Listed as a cut below because we only need one siege line. If the trebuchet is the one you want visually, keep it and cut `DankPyon_Ballista` instead. **[?]** |

### Not keeping — 15 projects, 19,950 points

Grouped by why. Dependency damage is stated for each; **order of operations
below is not optional.**

**Dead ends — clean cuts, nothing depends on them**

| Project | Cost | Verdict |
|---|---:|---|
| `DankPyon_Plasteel` (labelled "Mithril") | 4000 | Zero dependants, zero ThingDefs. Kill list. Safe today. |
| `DankPyon_Exploration` | 1800 | Paper, cartography, maps. Zero dependants. Safe today. |
| `DankPyon_AdornedArmor` | 1500 | No ThingDefs, no dependants. Decorative armour recipes behind a 1,500-point wall. |

**Duplicates — a second copy of something we already have**

| Project | Cost | Duplicate of |
|---|---:|---|
| `VCE_Grilling` | 400 | `DankPyon_Grill`. Both unlock a grill. |
| `VCE_CheeseMaking` | 750 | `DankPyon_Presser`. Both unlock a cheese press. |
| `VCE_StewCooking` | 300 | `DankPyon_StewPot`. Both unlock a stew pot. |
| `VFEM2_Alchemy` | 1500 | `DankPyon_Alchemy`. MO's gates 28 things and feeds Steel/Tar/Gunpowder; VFEM2's gates 18 and nothing depends on it. Cut the one with no dependants. |
| `VFES_SiegeEquipment` | 900 | The third siege system, after MO's ballista line and Classical's scorpion. |
| `DankPyon_HeavyCrossbow` | 700 | Its arbalest folds into `DankPyon_Ballista`. |
| `DankPyon_Trebuchet` | 1000 | Second siege engine. See *on the fence*. |

**Chain heads — cut, but only after re-parenting**

| Project | Cost | Damage if cut first |
|---|---:|---|
| `DankPyon_TextileSpinning` | 600 | `DankPyon_Silk` loses its prerequisite and becomes free. Silk is a keeper. |
| `DankPyon_Steel` | 2000 | `DankPyon_Plasteel` loses its prerequisite — irrelevant if Plasteel is cut in the same pass, and it is. `metalChain` is off as a setting, so **verify this is not already inert** before spending a patch on it. |

**Redundant tiers**

| Project | Cost | Why |
|---|---:|---|
| `DankPyon_NoblePolearms` | 1000 | Two weapons for 1,000 points, and Core's `LongBlades` already gives a halberd. |
| `DankPyon_NobleMaces` | 1000 | Two weapons, and Core's `LongBlades` plus Royalty already give a warhammer. |
| `DankPyon_RepeaterBallista` | 2500 | A third ballista rung at 2,500 points. |

---

## The arithmetic

| Step | Medieval |
|---|---:|
| Today | 54,850 |
| − 15 cuts above | −19,950 |
| − 6 weapon projects merged into 2 | −900 |
| − 6 projects retiered down to Neolithic | −2,200 |
| **Proposed** | **31,800** |
| `sys/07` approved three-leap structure | ~30,900 |

Within 3% of the approved structure, with no new projects authored. VFE Classical
is **not** in that figure — if all 18 move up untouched it becomes 53,400, which
is back where we started. That is why Classical has to be cut down as it moves,
or absorbed by `requiredPointsMedieval` at 0.75.

| Step | Neolithic |
|---|---:|
| Today | 30,100 |
| − VFE Classical retiered up | −21,600 |
| − `PlowedSoil`, `VCE_CondimentsResearch`, `Lumber` | −1,000 |
| + VFE Tribals | +760 |
| + 6 projects retiered down | +2,200 |
| **Proposed** | **~10,460** |

Whether ~11,000 is the right Neolithic weight depends on the early-game research
rate, which is far below the ~469 points/day implied by `sys/07`'s "117 bench
days" figure — you have two colonists and a gathering ritual, not a research
team. Setting that number is `sys/07`'s job. What matters here is the *shape*:
capability-granting research at the front, and no 21,600-point Roman block
sitting in the middle of it.

---

## Order of operations

Deleting a `ResearchProjectDef` **strips the prerequisite off everything that
required it**, leaving those things buildable with no research at all — the
opposite of the intent, with no error message. So:

1. **Re-parent `DankPyon_RusticFurniture` off `DankPyon_Lumber`.** It gates 107
   things directly and is the prerequisite for `DankPyon_RusticStorage` (113
   more), `DankPyon_Presser`, `DankPyon_CarrierBirds` and
   `DankPyon_TextileSpinning`. Cut Lumber before this and roughly **220
   buildings go free**. Re-parent to `DankPyon_BasicCooking` or nothing, since
   it is moving to the Neolithic anyway.
2. **Re-parent `DankPyon_Silk` off `DankPyon_TextileSpinning`.** Onto
   `ComplexClothing`.
3. **Re-parent `DankPyon_Ballista` off `DankPyon_Crossbow`** if the crossbow
   line turns out to be dead under no-new-metals.
4. **Strip the paper press** from `DankPyon_Presser`'s unlocks.
5. **Then** apply the 15 cuts, research last.
6. **Then** retier: Classical up, the six MO projects down.
7. Re-run all four `CLAUDE.md` checks. Note `audit_research.py` does not apply
   our own PatchOperations, so its tier totals will lag every retier here —
   `sys/02` already has a work item to fix that.

Everything in step 1–4 is safe to do today and changes nothing the player sees.
That is the natural first commit.

---

## Still needs Conrad

1. **VFE Classical** — retier all 18 up and cut ~10 of them, or retier and
   absorb the cost at `requiredPointsMedieval` 0.75? The recommendation above
   argues for moving them; how hard to cut is a taste call about how much Rome
   you want in the medieval era.
2. **Gunpowder** — `DankPyon_Gunpowder` (fire pots, flash pots) or
   `VFEM2_Matchlocks` (arquebus, musket, flintlock)? One of them, not both.
3. **Siege** — ballista or trebuchet as the surviving engine?
4. **`DankPyon_Steel`** — needs an in-game check that `metalChain` off has not
   already made it inert. Not a decision, a verification, but it needs the game
   open.
