# Open decision: how do we build the Medieval era?

**Status: UNRESOLVED. This is the first thing to work in the next session.**

Read [`VISION.md`](VISION.md) first if you have not. The Medieval era is the
longest single stretch of the campaign (intended 3–4 years, 180–240 days) and
it is currently the thinnest content in the whole load order. Everything below
exists to fix that.

Nothing in this document has been implemented. No mod has been enabled. The
question is genuinely open and Conrad has not made the call.

---

## The question in one line

**Route A** — enable Medieval Overhaul as a normal mod and strip the unwanted
parts with `PatchOperationRemove`.

**Route B** — leave it disabled and hand-copy selected content into a new
def-only `Archinity.Medieval` module.

A previous session recommended B. That recommendation was **partly based on a
mischaracterisation** (see "Corrections already made" below) and the current
lean is **A**. Do not treat either as settled.

---

## Why the Medieval era needs help at all

Measured, not estimated. `python tools/audit_research.py --tiers` regenerates
all of this.

| Tier | Projects | Total baseCost |
|---|---|---|
| Neolithic | 28 | 27,500 |
| Medieval | **22** | **15,500** |
| Industrial | 93 | 147,300 |
| Spacer | 42 | 105,900 |
| Ultra | 39 | 138,000 |

Research rate, from the decompiled formula
(`points/tick = (0.08 + 0.115 × IntellectualSkill) × benchFactor × 0.00825`;
bench factors simple 0.75, hi-tech 1.0, hi-tech+multianalyzer 1.1):

| Situation | points/day |
|---|---|
| 2 pawns, skill 12, simple bench (Medieval-realistic) | **505** |
| 2 pawns, skill 15, hi-tech | 833 |
| 2 pawns, skill 20, hi-tech + multianalyzer | 1,209 |

At 505/day, TechBlock's 0.75 gate on 15,500 points is **~22 days of content
against an intended 180–240 day era.**

Retiering cannot fix this. Nearly every Industrial project descends from
`Electricity`, `Machining` or `MicroelectronicsBasics`, and retiering a project
whose prerequisite stays Industrial changes nothing. Only the alchemy line was
free-standing, and it has already been moved (`Archinity.Pacing/Patches/Retier_Medieval.xml`,
+2,500). Conrad explicitly declined to remove `Electricity` from `Machining`'s
prerequisites, which is what would have unlocked another 5,500. **Electricity
stays as the thing that ends the Medieval era.**

---

## What each route yields

| | Route B (hand-port) | Route A (enable) |
|---|---|---|
| Medieval research points | ~37,700 | **~59,350** |
| Bench days @505/day, 0.75 gate | ~56 | **~88** |
| Same at `requiredPointsMedieval` 1.0 | — | **~117** |
| Cooking economy | **impossible** (see below) | full |
| `RequiredSchematic` gating | forfeited | 14 projects |
| Work for us | port ~200 defs + textures | none |
| New Steam subscription | none | Processor Framework |

Route A's ~59,350 is 15,500 existing + 39,900 from MO + 1,450 from the two
Vanilla Cooking Expanded mods + 2,500 from the drug retier already shipped.

---

## Verified facts — do not re-derive these

### The iron chain is a SETTING, not a patch

This was Conrad's sole original objection to Medieval Overhaul and it is
switchable. MO wraps all four resource-chain replacements in
`MedievalOverhaul.PatchOperation_ToggleSettings`, driven by the in-game mod
settings menu, in `1.6/Patches/ToggleOptions/`:

| File | Setting key |
|---|---|
| `MOSetting_MetalChain.xml` | `metalChain` — ore → ingot smelting |
| `MOSetting_WoodChain.xml` | `woodChain` — trees drop raw wood |
| `MOSetting_ClothChain.xml` | `clothChain` |
| `MOSetting_LeatherChain.xml` | `leatherChain` |
| `MOSetting_VanillaMineables.xml` | `vanillaMine` |

The mod's own tooltip: *"Vanilla mineables will be forced on if this is
inactive."* Across all 1.6 patches the string `Steel` appears in exactly two
files, both toggle-gated. There is no unconditional patch touching vanilla Steel.

**`woodChain` has NOT been ruled on by Conrad.** It is the same class of core
change as the metal chain. Ask.

### MO is built to coexist with what we already run

`LoadFolders.xml` ships conditional compat folders that would activate:

```
IfModActive="OskarPotocki.VFE.Medieval2"  -> 1.6/Mods/VanillaExpandedMedieval
IfModActive="vanillaexpanded.vcooke"      -> 1.6/Mods/VanillaCookingExpanded
IfModActive="Ludeon.RimWorld.Odyssey"     -> 1.6/Mods/Odyssey
```

Both directories exist. The VFE Medieval 2 folder contains reconciliation
patches for the exact overlaps that would worry you —
`Change_Alchemy_Research.xml`, `Change_Beekeeping_Research.xml`,
`Change_Plant_Research.xml`, `Changed_Leather_Boilpot_Research.xml`.
The author has already done the MO + VFE Medieval 2 + VCE integration.

### The cooking mods Conrad downloaded

Both are subscribed and currently **disabled**.

| Mod | packageId | Assembly | Medieval research |
|---|---|---|---|
| Vanilla Cooking Expanded | `VanillaExpanded.VCookE` | yes, but only 3 XML class refs | Grilling 400, CheeseMaking 750 |
| VCE - Stews | `VanillaExpanded.VCookEStews` | **none, def-only** | StewCooking 300 |

Plus Condiments 500 (Neolithic) and 1,600 Industrial. 66 meals, 7 benches,
3 plants. Dependencies are Harmony and VEF, both already loaded. These are
additive VE mods with no core-function changes — **enabling them is a separate,
much easier decision than the MO one, and probably a yes regardless of route.**

### MO cooking is Route A only

Do not waste time trying to port it. `DankPyon_CookMealApplePie` needs
`DankPyon_Flour`, and flour is produced by `ProcessDef_Watermill.xml` /
`ProcessDef_Windmill.xml` — **Processor Framework**. Sugar and juice come from
the presser, cheese from processors, apples from MO's fruit trees, and the
recipes run on `DankPyon_StoneOven` / `StewPot` / `Grill`, all
`MedievalOverhaul` classes. The recipe XML is portable; its entire ingredient
economy is not.

### Route A's real costs

1. **Processor Framework** (`syrchalis.processor.framework`) is a hard
   dependency and is NOT currently subscribed.
2. **7 MO factions force-spawn** at `requiredCountAtGameStart=1`
   (`DankPyon_Forest_Faction`, `DankPyon_Witch_Faction`,
   `DankPyon_SnakeCave_Faction`, and 4 more). Conrad runs
   `azravos.factioncustomizer` with a curated set, so this collides — but he
   has also said he *wants* medieval factions active in the world. Either
   accept, or patch `requiredCountAtGameStart` to 0.
3. **Both players need identical MO settings.** The toggles apply at def-load,
   so a mismatch means divergent defs and immediate desync. MO's settings file
   must be snapshotted into `config/ModSettings/` alongside TechBlock and
   Ignorance Is Bliss. This is the same trap the main handoff already warns
   about and it is easy to miss.
4. **MP desync risk from the assembly.** `MedievalOverhaul.dll` is 334 KB with
   39 JobDrivers, tick-driven comps and unsynced RNG, and contains zero
   references to `Multiplayer`/`Sync`. **Settle this by testing, not by
   argument** — a 30-minute two-player session surfaces desyncs fast.

---

## Corrections already made — do not repeat them

**The research patch is not what an earlier session reported.** It was
described as making "the whole vanilla medieval tree a subtree of MO's tree."
Counting the 83 operations in `1.6/Patches/Core/Change_ResearchProjectDef.xml`:

| Ops | What |
|---|---|
| 32 | `tab` reassignment onto MO's research tab |
| 32 | `researchViewX` / `researchViewY` layout position |
| 7 | `prerequisites` changes |
| 7 | `baseCost` changes |
| 5 | `label` renames |
| 1 | description |

Nearly 80% is cosmetic. The structural change is **seven prerequisite rewires
across sixteen vanilla projects.** That is normal overhaul integration. The
`researchViewX/Y` edits would probably *help* the research-tab layout problem.

**The multiplayer objection was overweighted.** The def-only rule exists for
*Archinity's own* mods; it was never a ban on third-party assemblies. The load
order already includes Prepatcher, Vehicle Framework, Vanilla Vehicles
Expanded, VEF, Alpha Mechs and Adaptive Storage. Vehicle Framework alone is far
more invasive than MO. MO's DLL is not the outlier it was made out to be.

---

## THE TASK FOR NEXT SESSION

Conrad wants two things before deciding.

### 1. A full Route A vs Route B assessment

Most of the raw material is above. What is missing is a concrete
**gameplay walkthrough**: with MO + VCE + VCE Stews enabled and `metalChain`
off, what does the Medieval era actually look like turn to turn? Which
research, in which order, unlocking what, gated behind finding what?

Map it onto the three-leap structure already designed (below), and say plainly
which leaps MO fills well and which it does not.

### 2. The obsolescence audit — Conrad's main worry

His words: he does not want to end up *"sailing through the stars on a
gravship with a bunch of alien bitches and I've got my cheese press in the
back."* He is explicitly asking that everything we enable either **scales with
him** or **becomes obsolete at the right time, replaced by something genuinely
better.**

This is a real risk and the numbers are concrete. **MO adds 39 production
buildings. VCE adds 7.** Measured:

```
MO (39):  AdvancedResearchBench  AlchemyBench  Anvil  Book_ScribeTable
          BurnPit  ButchersBlock  Cauldron[PF]  DiggingSpot  Furnace[MO-dll]
          GardeningBox  Grill[MO-dll]  MendingBench  Millstone
          MineShaft[MO-dll]  MiningSpot  Post  Press_Paper[PF]  Presser[PF]
          Pyre[MO-dll]  ResearchingSpot  RusticCookingTable[MO-dll]
          RusticHearth[MO-dll]  SilkBed[PF]  SlopPot[MO-dll]
          SlopPot_Fondue[MO-dll]  SlopPot_Stew[MO-dll]  SpinningWheel
          StewPot[MO-dll]  StonecuttingSpot  TailorsBench  WaterMill[PF]
          WaterSpot  Well  WindMill[PF]

VCE (7):  VCE_CanningMachine  VCE_CheesePress[PF]  VCE_CondimentPrepTable
          VCE_DeepFrier  VCE_ElectricPot[PF]  VCE_Grill  VCE_StewPot[PF]
```

Classify **every one** of those 46 into exactly one bucket:

- **(a) Naturally obsolete** — an early-game stopgap the game itself retires.
  The `*Spot` family (DiggingSpot, MiningSpot, ResearchingSpot,
  StonecuttingSpot, WaterSpot) looks like this; confirm it.
- **(b) Superseded by a strictly better building** — name the successor and the
  research that unlocks it. `VCE_StewPot` → `VCE_ElectricPot` is a promising
  sign that VCE thought about this; verify and find the others.
- **(c) Persists forever** — still needed on a late-game gravship. **These are
  the problem.** For each, decide: accept it, patch a successor, or don't take
  the feature at all.

Deliverable: a table of all 46 with bucket, successor, and a recommendation.
Bucket (c) is the answer to Conrad's actual question.

Worth checking specifically: does anything supersede `Millstone` / `WindMill` /
`WaterMill` (the flour chain) once you have electricity? If flour has no
industrial-tier producer, the whole cooking economy becomes permanent medieval
infrastructure — which is precisely the cheese-press-on-a-gravship outcome.

### 3. Re-run the tooling with MO enabled

MO adds ~2,930 defs. Before committing to Route A:

```bash
python tools/audit_research.py          # new deadlock candidates?
python tools/audit_research.py --tiers  # new tier totals and gate costs
python tools/check_availability.py      # do the planned MRR materials still score safe?
python tools/check_refs.py
```

`audit_research.py` reads raw defs and does **not** apply our own
PatchOperations, so its tier totals lag any retier we have shipped. Known
limitation, worth fixing if it starts to mislead.

---

## The three-leap design this feeds (already agreed)

Conrad approved this structure. Route A vs B only changes what fills it.

**Leap 1 — The Forge** (~5,100 pts). Smithing, Stonecutting, ComplexFurniture,
ComplexClothing, basic blades/maces/polearms, hunting bow, protective
clothing, `VFE_Res_FarmingTechniques`, DrugProduction. Padded and leather
armour, real melee, scarecrows and planter boxes.

**Leap 2 — Mail and Siege** (~12,400 pts). Military blades/maces/polearms,
chain armour, crossbow, war bow, engineering, ballista, trebuchet,
intermediate agriculture + plowed soil, `VFEM2_ComplexWorkshops`,
`VFEM2_Alchemy`. **This is where you stop defending and start taking
settlements.**

**Leap 3 — Plate and Powder** (~13,400 pts). Noble weapons, adorned armour,
heavy crossbow, repeater ballista, gunpowder, `PlateArmor`,
`VFEM2_Matchlocks`, `VFEM2_Heraldry`, advanced agriculture,
`VFE_Res_Sprinkler` (approved for retier, not yet done). Then `Electricity`,
and the world changes.

### The MRR availability rule — settled, keep it

Research is gated on finding items, which converts research time into
expedition time. That is the mechanic that makes the era long. It is also the
mechanic that can silently brick a save.

**Raider equipment is the only source guaranteed by the storyteller rather
than by luck.** Quests are RNG and settlements are placed at worldgen, but
raids arrive on schedule, and Ignorance Is Bliss guarantees era-appropriate
gear. "Study the longsword you took off a dead marauder" is both the safest
source and the right fiction.

Five rules, enforced by `tools/check_availability.py`:

1. Every requirement lists 2–4 acceptable materials. MRR pools points per
   *type*, so any one satisfies it. Never a single item.
2. At least one is always CRAFT or HARVEST — something he can make or hunt.
3. The flavour item is always RAIDER-sourced.
4. Flavour items use `reverseEngineeringMaterials`, not experimental — you need
   to possess **one**, ever, and it is never consumed.
5. Nothing ships scoring under 2 routes.

---

## Other unresolved items

- **`VFE_Res_Sprinkler` retier.** Approved by Conrad, not yet implemented.
  Change its prerequisite from `Machining` to a Medieval project so irrigation
  lands in Leap 3. Targeted edit; does not touch `Machining` or `Electricity`.
- **`HeavyBridges` (800) and `Piano` (2,000) retier.** Both clean,
  zero-collateral moves to Medieval. Noted in
  `Archinity.Pacing/Patches/Retier_Medieval.xml`, not taken — only the drug
  line was approved.
- **`requiredPointsMedieval`.** Currently 0.75. Under Route A, 1.0 takes the
  Medieval gate from ~88 to ~117 bench days. Cheap dial, Conrad's call. **Note
  the setting names are offset one tier from the gate they control** —
  `requiredPointsMedieval` drives `TB_IndustrialTechLock`. Editing the one that
  sounds right moves the wrong gate. Re-snapshot into `config/ModSettings/`
  after any change, and both players need the identical file.
- **36 MRR deadlocks remain.** `python tools/audit_research.py` lists them.
  `MultiAnalyzer` is fixed. The clusters that matter next are the vanilla ship
  chain (`ShipBasics`, `ShipEngine`, `ShipReactor`, `ShipCryptosleep`,
  `ShipSensorCluster`), all GravTech projects, and
  `VGE_GravshipPower`/`HeatDissipation`/`AstrofuelRefining`. Given the gravship
  is the late-game home, these matter. The audit is a **screening tool with
  heuristics**, not an oracle — hand-verify before acting, as was done for
  MultiAnalyzer.
- **Nice Research Tab layout.** `andromeda.niceresearchtab` has zero TechBlock
  awareness (no `TB_` reference anywhere in its defs). TechBlock injects
  `TB_<Era>Theory` as a prerequisite onto every tier-root project, turning the
  graph into a star, which is almost certainly why the tree renders badly. It
  is improvable via its own `FineTune` defs (`AlwaysZeroX`, `AlwaysSeparated`,
  `BranchOrder`, `CoreBranchOrder`, `ProximityRules`, `CategoryRules`) but not
  cleanly fixable. **Open question for Conrad: does he dislike node-graph
  presentation in general, or just this mod's output?** If the former, no graph
  viewer will satisfy him and a list-based tab is the answer instead.
- **Fresh-world verification is DONE.** Conrad generated a world; Glitterites
  and Drifters both rendered correctly. The main handoff may still list this as
  outstanding.

---

## Traps found in this area — do not rediscover

- **XML comments cannot contain `--`.** Hit twice now, including by an agent
  that had just documented it. A run of hyphens as a divider is a parse error
  and RimWorld drops the whole file silently. Use `=`.
- **PatchOperations run on raw XML before `ParentName` inheritance resolves.**
  A predicate on a field declared only on an Abstract parent matches the parent,
  not the children. This broke the first Alpha Mechs lockout: all 26 gestation
  recipes inherit `researchPrerequisite` from four abstract parents. Match on
  `@ParentName` instead.
- **RimWorld omits unresolvable cross-references rather than storing null.**
  So deleting a ResearchProjectDef *removes the prerequisite* from anything
  requiring it, leaving the thing buildable with **no** research. Neuter
  referencing defs first, delete the research last.
- **`local-name()` does not split on a dot.** The tag is
  `ResearchMakesSense.ManualAnalysisDef`; matching `local-name()='ManualAnalysisDef'`
  silently matches nothing. This made the audit tool report MRR's own 46
  hand-authored entries as auto-generated and inflated the deadlock count from
  37 to 55.
- **`CellRect.FromString` parses min/max corners, not width/height.** `(0,0,0,0)`
  is a 1×1 cell, not empty.
- **Always sanity-check research rates against era.** A flat "1,000 points/day"
  assumption produced a wrong recommendation to lower every TechBlock gate. The
  real rate is ~213/day in the Neolithic and ~1,209/day at Spacer, and at
  era-appropriate rates the existing 0.75 values are close to correct.
