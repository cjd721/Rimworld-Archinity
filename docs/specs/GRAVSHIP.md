# Gravship

## Purpose and scope

How the gravship becomes the colony's permanent home — the deck budget, life support, food,
defenses, and what changes when the planetside base is retired. The fiction is
[`docs/plot/SPACER.md`](../plot/SPACER.md) § *Departure — The Gravship Becomes Home*: *"reliable
oxygen, gravity, food production, cooking, habitation, storage, defenses, shields and enough
capacity that the colony can permanently leave the electrified castle behind."*

This document owns **whether that is possible and at what cost**, and the deck budget every other
gravship decision is spent against. It also answers what a ship in flight does when its landing
tile changes hands (§ *A gravship en route when its landing tile changes hands*,
[#177](https://github.com/cjd721/Rimworld-Archinity/issues/177)).

It does not own: the Ultra pursuit that the defenses answer to
([`TRACE.md`](TRACE.md), [`PRESSURE.md`](PRESSURE.md)); which mods ship
([#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)); when each tier unlocks
(`docs/progression/`, which is empty today — see *Outstanding decisions*); or where the altar lives
([#10](https://github.com/cjd721/Rimworld-Archinity/issues/10), **closed**). Verified engine
mechanisms are in
[`docs/engine/gravship-and-substructure.md`](../engine/gravship-and-substructure.md). The silent
failures are `docs/TRAPS.md` **T-46** (overbuilt deck cells silently dropped on launch), **T-47**
(non-airtight walls never pressurise), **T-48** (the orbit incident pool collapses to 18 of 91),
**T-49** (`Find.RandomSurfacePlayerHomeMap` is null in orbit) and **T-50** (a budget computed from
un-patched def values).

## The build

**Permanent gravship habitation is a retiering and patching job, not an engineering one — plus one
thirty-line alert.**

Odyssey ships the whole thing. `Building_GravEngine` carries a cell budget, `Verse.VacuumComponent`
carries the vacuum simulation, `CompOxygenPusher` carries repressurisation, `HydroponicsBasin`
carries food on `fertility 0` decking, and `GravshipShieldGenerator` carries the shield. Vanilla
Gravship Expanded turns oxygen into a VEF `PipeSystem` network, GravTech raises the ceiling, and
`sbz.GravshipStorage` and Biotech for Gravship shrink the furniture. **Nothing needs to be
invented.** Four things need to be written. **[V]** on each carrier; **[I]** that the four compose
into a liveable ship.

### (a) Research retier — XML

The gravship tech sits at the wrong era for this campaign. `BasicGravtech` is Industrial/300,
`OrbitalTech` (which gates the vanilla `OxygenPump`) is Industrial/1,000, `AdvancedGravtech` is
Spacer/2,000. **[V]** The plot puts the ship at the Industrial capstone and *habitation* at Spacer,
with the weapon ladder spread across Ultra. `PatchOperationReplace` on `ResearchProjectDef.baseCost`
/ `techLevel` and on the `researchPrerequisites` of the habitation buildings. **~60 lines** **[I]**,
in a new `Patches/Gravship_Retier.xml`. `docs/progression/` is meant to set the actual era
boundaries; this spec only says the patch is the carrier.

### (b) Orbit incident and game-condition whitelist — XML

**This is the largest content consequence of the ship becoming home, and it is not about the ship.**
The Orbit layer sets `onlyAllowWhitelistedIncidents`, and across the merged vanilla + DLC database
that leaves **18 of 91 `IncidentDef`s** able to fire; its game-condition gate passes **4 of 32**
(§ *The four gates, and what passes them today*). **[V]** A campaign act played from an orbital home
loses wanderers, refugees, visitors, manhunter packs, infestations, solar flares, toxic fallout and
every walk-in social event — silently. See *Living on the orbit layer*, below, and T-48. Quests are
gated elsewhere, by `QuestGen_Get.GetMap(canBeSpace)`, not by this whitelist; they are Routes C and D
(§ *Quests are gated somewhere else entirely*).

`PatchOperationAdd` of `<layerWhitelist><li>Orbit</li></layerWhitelist>` onto each incident and game
condition the campaign wants alive. **~80 lines** **[I]**, one `<li>` per def, in a new `Patches/Orbit_Incidents.xml`. Which
defs pass is content for [the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119)
(§ *Ordinary colony life on an orbital home*, Routes A–G and the four gates).

### (c) `Alert_SubstructureOverBudget` — new C#

The only thing reading proves is missing. Build past `SubstructureSupport` and the cells build,
walk and hold buildings — and are dropped, with everything on them, on launch, with no message
(T-46). **[V]** The number is already visible in the engine's inspect string; being *told* is what
is absent.

```
Alert_SubstructureOverBudget : Alert_Critical
  GetReport()  -> for each Building_GravEngine of Faction.OfPlayer on each map,
                  cull = engine.AllConnectedSubstructureNoRegen.Count
                       - (int)engine.GetStatValue(StatDefOf.SubstructureSupport)
                  if cull > 0: culprit = engine
  GetExplanation() -> "<n> cells of substructure will be left behind on launch."
```

**~30 lines** **[I]**. No state, no scribing, no hook — `Building_GravEngine.ForceSubstructureDirty`
already fires on every substructure change and every facility link change, and the alert polls.
**[V]** Use the `NoRegen` accessors so the alert never triggers a section-layer regeneration.

Note that `GetStatValue(SubstructureSupport)` is the *composed* number, so the alert is correct
under any mod set — which is exactly the property a hand-computed budget does not have (T-50).

### (d) `Find_RandomSurfacePlayerHomeMap_Patch` — new C#, only if needed

`Find.RandomSurfacePlayerHomeMap` is wired to `Game.RandomRootSurfacePlayerHomeMap`, so
`QuestNode_GetSiteTile` and `QuestPart_SpawnMonolith` return null once the only home is in orbit
(T-49). **[V]** A Harmony postfix returning `Current.Game.RandomSurfacePlayerHomeMap` is **~8 lines**
**[I]**. Needed only if Archinity content uses those two nodes; otherwise avoid them and skip the
patch. Joiners fail elsewhere, at `CanBeSpace` (T-128; § *Nobody joins*).

### What we reuse, unchanged

All **[V]**.

| Need | Carrier | Shape |
|---|---|---|
| Cell budget | `Building_GravEngine` + `StatDefOf.SubstructureSupport` | flood fill capped at the stat |
| Vacuum | `Verse.VacuumComponent`, `VacuumUtility`, `HediffDefOf.VacuumExposure` | per-`Room`, 250-tick |
| Air | `CompOxygenPusher` (vanilla) or `VanillaGravshipExpanded.OxygenPipeNet` | room repressurisation |
| Pawn vacuum survival | `Apparel_Vacsuit` + `Apparel_VacsuitHelmet`, or `GeneDef VacuumResistance_Total` | stat `VacuumResistance` ≥ 1 |
| Food | `HydroponicsBasin` (fertility 2.8) or `VGE_Agrocell` (3.2, self-lit) | `sowTag Hydroponic` |
| Power | `GravcorePowerCell` — 1 cell, 1,200 W, no fuel, transmits | 1 `Gravcore` each |
| Shield | `GravshipShieldGenerator` ×2, or GravTech `AdvShip_ShieldGenerator` | `CompProjectileInterceptor` |
| Hull | `GravshipHull` (`isAirtight: true`) | never local stone — T-47 |

### Cost

| Piece | Kind | Estimate | Lands in |
|---|---|---|---|
| `Alert_SubstructureOverBudget` | new C# | ~30 lines | the shipped assembly |
| `Find_RandomSurfacePlayerHomeMap_Patch` | new C#, optional | ~8 lines | same |
| Research retier | XML patch | ~60 lines | `Patches/Gravship_Retier.xml` |
| Orbit incident and game-condition whitelist | XML patch | ~80 lines | `Patches/Orbit_Incidents.xml` |

Every estimate in that table is **[I]**. The mechanisms composed above are **[V]**. That they
compose into a liveable ship is **[I]** until one is built and flown.

## The deck budget

**Twenty pawns fit in 2,000 cells with ~10% to spare — and the ceiling moves in both directions
once mods merge.**

Every number in this section is **[I]** computed from **[V]** def values. Which def values applied
is the whole point: see T-50.

### The rules that make a cell cost

- **2,000 = `GravEngine` 500 + 6 × `GravFieldExtender` 250**, the extender capped at
  `maxSimultaneous 6` and required within **18.9** cells of the engine. **[V]** These are the
  *un-patched* Odyssey values, and three of the four are replaced the moment VGE loads.
- **Everything comes out of the same pool** — interior floor, walls, doors and hardpoints. A thing
  flies only if *every* cell of its `OccupiedRect` is valid substructure; a room holds air only if
  *every* one of its cells sits on substructure foundation. **[V]**
- **Wall attachments are free floor.** `OxygenPump`, `Cooler`, `Heater` in a wall,
  `VGE_WallToolCabinet` — `building.isAttachment` makes `OnValidSubstructure` test the host wall
  instead of the attachment's own cell. **[V]**
- **Geometry does not bind — if the extenders are spread.** `GravshipUtility.GetConnectedSubstructure`
  runs with `requireInsideFootprint: true`, so nothing outside the footprint union is even
  connected. **[V]** Six extenders placed *at* the 18.9 limit give a buildable union of ~3,551
  cells holding a ~2,400-cell axis-aligned rectangle **[I]**; six extenders bunched beside the
  engine collapse that union to ~1,291 cells and the largest rectangle to ~784 **[I]** — too small
  for the deck below. Extender placement is a hull-shape decision, not an engine-room decision.
- **Thrusters cost nothing but shape.** `LargeThruster`'s `exclusionAreaSize (2,0,7)` — **14 cells,
  two wide by seven deep**, at `exclusionAreaOffset (0,0,-7)` — must be clear *and must not be
  substructure*, so thrusters live on external pods pointing out of the hull. **[V]**

Full mechanism and citations: `docs/engine/gravship-and-substructure.md` § *The launch budget*.

### A worked twenty-pawn deck, Odyssey only

Costed as **(interior_w + 1) × (interior_h + 1)** per room — every wall shared once — plus one
`+W + H + 1` term for the two unattributed hull edges. Deck outer ≈ 46 × 38. Sizes **[V]**;
the plan and its arithmetic **[I]**.

| Block | Interior | Budget | Contents |
|---|---|---|---|
| 20 × crew cabin 3×4 | 12 ea | 400 | `Bed` 1×2, `Dresser` 2×1, `EndTable` 1×1 — **7 free cells** |
| Hydroponics bay 15×11 | 165 | 192 | 29 × `HydroponicsBasin`, 2 × `SunLamp` |
| Galley 7×6 | 42 | 56 | 2 × `ElectricStove`, `TableButcher`, 4 × `Shelf` |
| Cold store 7×7 | 49 | 64 | 12 × `Shelf` (24 cells → **72 stacks**) |
| General store 10×8 | 80 | 99 | 24 × `Shelf` (48 cells → **144 stacks**) |
| Mess & rec 13×10 | 130 | 154 | 3 × `Table2x4c`, 12 chairs, `BilliardsTable`, 2 × `ChessTable` |
| Workshop 12×8 | 96 | 117 | 5 benches, 2 × `ToolCabinet` |
| Laboratory 8×6 | 48 | 63 | `HiTechResearchBench`, `MultiAnalyzer` |
| Infirmary 8×6 | 48 | 63 | 4 × `HospitalBed`, 2 × `VitalsMonitor` |
| Engine room 10×8 | 80 | 99 | engine, 12 power cells, `FuelOptimizer`, `PilotSubpersonaCore`, 2 shields — **no extenders** |
| Bridge 8×5 | 40 | 54 | `PilotConsole`, `CommsConsole`, `SignalJammer` |
| Fuel bay 8×6 | 48 | 63 | 2 × `LargeChemfuelTank` |
| Spine corridor 2×44 | 88 | 135 | |
| 2 × cross corridor 2×18 | 36 ea | 114 | |
| 6 × `GravFieldExtender` | | *(6 cells, inside the room budgets above)* | **distributed to the 18.9 ring, one cell each — not in the engine room** |
| *Rooms* | | *1,673* | |
| Hull far edges | | 85 | |
| 6 × `LargeThruster` pods | | 24 | external, 14 clear non-substructure cells astern each |
| 8 × turret hardpoints | | 8 | |
| **Total** | | **1,790 / 2,000** | |

**The extenders do not live in the engine room.** Six of them bunched there collapse the footprint
union to ~1,291 cells and the largest rectangle to ~784 — a 46 × 38 deck is then impossible, because
`GetConnectedSubstructure` runs `requireInsideFootprint: true`. They must sit out toward the 18.9
ring, one cell each. On a 46 × 38 deck that ring falls inside rooms and corridors already counted,
so the 6 cells are still charged — inside those room budgets — and the total does not move. What
moves is the hull's *shape*: the deck must be drawn around six scattered 1×1 hardpoints near the
ring, not around a tidy engine block.

**Where it breaks.** 4×4 cabins cost +100 and still fit. Thirty pawns cost +296 and do not.
5×5 "impressive" cabins cost +320 and do not. **Cabin size is 22–40% of the whole budget and is the
lever that decides everything else.** **[I]**

**Storage headroom.** `Shelf` is 2×1 with `maxItemsInCell 3` — **6 stacks per shelf, 3 per cell**
(`ShelfBase`, `Core/Defs/ThingDefs_Buildings/Buildings_Furniture.xml`). **[V]** The two store rooms
above therefore hold **216 stacks in 72 cells of shelving** — twice the 108 the deck was drawn to
need. The deck total is conservative by that margin, and the store rooms are the first place to
reclaim cells if the budget tightens.

### What the mods change

Savings against the 1,790-cell deck above. Each mod's def values are **[V]**; each saving is
**[I]**.

| Lever | Saving | Note |
|---|---|---|
| `VGE_GravshipSubscaffold` | ~160 | airtight, flood-filled, **exempt from the budget** — but `affordances: [Walkable]` only, so corridor *floor* is free and the flanking walls are not |
| `VGE_Agrocell` (1×3, fertility 3.2, self-lit) | ~62 | also frees the farm from sun-lamp room geometry |
| VGE compact line (`VGE_CompactWorkspaces`) | ~40 | research bench 10 → 3, multi-analyzer 4 → 1, fab bench 10 → 3, tool cabinet 2 → 0 |
| `sbz_LongGravshipCrate` (5×2, `maxItemsInCell 8` → 80 stacks) | ~16 | 8 stacks/cell against `Shelf`'s 3. Matching the 108 stacks the deck was drawn to need costs 36 shelf cells or 20 crate cells — a **16**-cell saving, not the ~50 a halved shelf count implied |
| More Gravship Workbenches (`lts.mgw`) | 0–15, conditional | eight compact 2×1 / 3×1 benches, hard-dependent on VGE, each `MayRequire`-gated on a *different* donor (Anomaly, Jewelry, Vanilla Recycling Expanded, Integrated Implants, VRE Androids, VVE, Vanilla Nutrient Paste Expanded). Only the `LTS_CompactNutrientPasteGrinder` (3×1, **acts as its own hoppers**) bears on the Galley row as drawn; the rest are Workshop savings *if* their donors ship. See [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) |
| Biotech for Gravship compact line | ~20 | **not counted** — only if a mech bay flies, and a mech bay costs more than it saves |

**1,790 − (160 + 62 + 40 + 16) = 1,512, call it ≈ 1,510 cells.** **[I]**

And the ceiling itself moves — **in both directions**:

| Configuration | Ceiling | Composition |
|---|---|---|
| Odyssey alone | **2,000** | 500 + 6 × 250, no multiplier |
| + `als.gravtech`, VGE absent | **4,500** | + 3 × `GravFieldPylon` (1×1, 500 each) + `AdvShip_GravReactor` (5×5, 1,000, −150,000 W) |
| **VGE alone** | **≈ 1,625** | offsets 250 + 10 × 100 = 1,250, × 1.30 (six `LargeThruster` at +0.05 each). **Below Odyssey alone, and below the un-modded 1,790-cell deck** |
| + `als.gravtech` **and** VGE | **≈ 3,850 – 4,500** | offsets 250 + 10 × 100 + 3 × 130 + 500 = **2,140**, × 1.80 (no thrusters) to × 2.10 (six `LargeThruster`) |
| the deck as drawn, GravTech + VGE, six extenders only | **3,132** | offsets 250 + 6 × 100 + 3 × 130 + 500 = 1,740, × 1.80 |

**Every input to that table is a patched value, and that is the whole lesson of T-50.** With
`vanillaexpanded.gravship` loaded: **[V]** on each

- `1.6/Patches/VanillaGravEngineLinking.xml` replaces `GravEngine`'s `SubstructureSupport`
  **500 → 250** and its footprint radius **18.9 → 11.9**;
- `1.6/Patches/GravFieldExtender.xml` replaces the extender **250 → 100**, raises
  `maxSimultaneous` **6 → 10**, sets `maxDistance 500`, and lowers its footprint radius
  **16.9 → 12.9**;
- `1.6/Patches/VanillaThrusters.xml` adds `CompProperties_ConstantGravshipFacilityBonus` to both
  thrusters — **`LargeThruster` +0.05** each (max 6), `SmallThruster` +0.01 each (max 10);
- GravTech's own compat file
  `1.6/Mods/VanillaGravshipExpanded/Patches/VGE_Patch_GravTech.xml` restats **both** the pylon
  (**500 → 130**, +0.10 multiplier) **and `AdvShip_GravReactor` (1,000 → 500**, +0.50 multiplier,
  power −150,000 → −120,000, footprint radius → 49.9).

The multiplier path: VGE's `Patches/Stats.xml` adds `VGE_SubstructureSupportMultiplier` to the
`SubstructureSupport` StatDef's `statFactors`, `StatWorker.GetValueUnfinalized` applies comp offsets
and *then* multiplies, and VGE gives the engine
`CompAffectedByConstantGravshipFacilityBonus`, which sums `CompConstantGravshipFacilityBonus`
`statOffsets` from every linked facility. **[V]** **Plan against the composed number, never the
def** — and read it off the engine's stat page rather than computing it.

**Two levers the arithmetic above deliberately leaves out**, because both are counts a designer
picks rather than facts:

- **`VGE_GravFieldAmplifier`** — 3×3, `SubstructureSupport` **+200**, `maxSimultaneous 4`, footprint
  radius 22.9, `maxDistance 500`, `AdvancedGravtech`, **2 `Gravcore` each**. **[V]** Four of them add
  +800 offsets, worth **+1,440 to +1,680** composed ceiling **[I]** — the single largest lever
  available, and eight more gravcores.
- **More thrusters.** `SmallThruster` +0.01 (max 10) and `VGE_GiantThruster` (3×3) +0.10 (max 4)
  stack on top of the large thrusters' +0.30. **[V]** Each needs its own clear, non-substructure
  exclusion area, so the practical count is a hull-shape question, not an arithmetic one.

**The recommended set only fits because subscaffold is exempt.** A ≈1,510-cell deck against VGE's
≈1,625 ceiling leaves ~110 cells, 7% margin — but the reason the deck is ≈1,510 is that ~160 cells
of it are `VGE_GravshipSubscaffold` corridor floor the budget never charges. Count them and the
deck draws ≈1,670, which **does not fit**. **[I]** Anyone who ships VGE without GravTech is flying
on the subscaffold exemption: VGE alone lowers the ceiling.

**The binding constraint is not cells. It is `Gravcore`.** Six extenders, a signal jammer and twelve
power cells cost **19** **[V]**, and gravcores are not generically sellable — they arrive from
`QuestPart_SubquestGenerator_Gravcores` at a minimum of one per **15–30 days**
(`MinTimeBetweenSubquests` 900,000 ticks, `MaxTime` 1,800,000, one gravcore per site). **[V]**
Fitting out the ship is therefore a **300–500 day** arc **[I]** whether or not the player hurries,
and GravTech's pylons and reactor add ten more gravcores on top, amplifiers eight more again.
Whether that pacing is acceptable is balance, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.
This spec records that the constraint exists and that no amount of cell efficiency changes it.

## Life support

**Verified available, and cheap.** The engine states its own sizing rule in
`Building_GravEngine.GetOrbitalWarnings`: it warns below `ValidSubstructure.Count / 400` oxygen
pushers and below `ValidSubstructure.Count / 250` strong heat sources. **[V]** **For a 2,000-cell
ship: 5 oxygen pumps and 8 heaters. [I]** Warnings on the launch dialog, not gates.

- **Air costs no floor.** `OxygenPump` is a wall attachment: 150 W (×0.1 outside vacuum), `OrbitalTech`. **[V]**
- **Heat is the problem; cold is free.** `BiomeDef Space` sets `constantOutdoorTemperature −75`, so a
  cold store is an uninsulated room and no `Cooler` is needed, while the ship needs real heating. **[V]**
- **Pawn survival** needs `VacuumResistance ≥ 1`: `Apparel_Vacsuit` + `Apparel_VacsuitHelmet`
  (0.32 + 0.69) reaches it; power/recon/cataphract sets reach 0.95–0.98 and still take a trickle. **[V]**
- **`GeneDef VacuumResistance_Total` grants 1.0 outright plus `immuneToVacuumBurns`** — a shipped
  vanilla gene that does exactly what the founders should be able to do. **[V]** But it is
  `biostatArc 1` and `displayCategory Archite` **[V]**, so it is not free: an archite gene cannot be
  assembled into a xenogerm without **archite capsules**, which are themselves quest/trade-gated.
  The *code* cost is zero; the *delivery* cost is an archite-capsule supply line. The founders'
  vacuum immunity is required by [`docs/requirements/SPACE.md`](../requirements/SPACE.md)
  § *The gravship as home* ([#127](https://github.com/cjd721/Rimworld-Archinity/issues/127)); how it
  is delivered is [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.
- **Hull material is load-bearing and fails silently.** Only Steel, Plasteel, Silver, Gold and
  Uranium set `stuffProps.isAirtight`. Stone, wood, and **`Obsidian`** (Stony + Metallic, no
  `isAirtight`) do not. **[V]** Build from `GravshipHull`, which is airtight outright. See T-47.

**Vanilla Gravship Expanded's oxygen network, verified against the 1.6 assembly. [V]**
`VanillaGravshipExpanded.OxygenPipeNet` extends `PipeSystem.PipeNet` — the network engine is VEF's
separate **`PipeSystem.dll`**, so the capability is a hard VEF dependency.
`CompResourceTrader_OxygenPusher.CompTickRare` is vanilla's own repressurisation formula plus a
network budget gate; it writes `Room.Vacuum` and reads `Room.UnsanitizedVacuum`, so **vanilla's
`VacuumComponent` still owns the simulation** and `VacuumUtility` is untouched. The sustainable
source in vacuum is `VGE_LifeSupportSystem` (2×2, 160 W, +80 u³/day burning `VGE_Oxyalgae` at
80/day); `VGE_OxygenHarvester` is atmosphere-only and is a planetside filling station. Hull integrity
comes from the `VGE_VacBarrier*` line (down to 24 W/cell against vanilla's 50), `VGE_VacCheckpoint`,
and `VGE_SealantPopper`.

## Food

**Hydroponics, sized to the crew, and not `GardeningBox`.**

A colonist burns **1.6 nutrition/day**; twenty pawns need **32/day**. Simple meals multiply raw
nutrition by **1.8** (0.5 in → 0.9 out); the nutrient paste dispenser by **3.0** (0.3 → 0.9). Plants
grow only during `DayPercent` 0.25–0.80 — a **55% duty cycle** that `SunLamp`'s schedule matches
exactly — at `fertility × sensitivity + (1 − sensitivity)` times base rate. Inputs **[V]**;
the table below **[I]**.

| Grower | Fertility | Nutrition / plant-cell / day | Cells for 32/day, simple meals |
|---|---|---|---|
| `HydroponicsBasin` 1×4, 70 W, needs `SunLamp` (2,900 W) | 2.8 | 0.154 | **115** |
| `VGE_Agrocell` 1×3, 160/70 W, self-lit | 3.2 | 0.176 | **101** |
| `GardeningBox` (Medieval Overhaul) | **0.8** | 0.044 | 404 — **unusable at this scale** |

Size at **1.3×** for harvest gaps, prisoners and guests: ~150 hydroponics cells or ~130 agrocell
cells. **[I]** Nutrient paste cuts either by 40% at a permanent mood cost across twenty pawns.

Two constraints worth designing around:

- **A breach does not slow the crop, it kills it.** `Plant.GrowthPerTick` returns 0 when the cell's
  vacuum ≥ 0.5 and the plant is not `vacuumResistant` — but the same condition also makes
  `Plant.DyingBecauseExposedToVacuum` true, which drives `CurrentDyingDamagePerTick` until the plant
  dies and posts `MessagePlantDiedOfRot_ExposedToVacuum`. **[V]** So the recovery from a farm breach
  is **seal and resow**, not seal and resume: the standing crop is gone and a full grow cycle
  (~1.95 days for rice) restarts from zero. That makes the farm a genuinely valuable raid target,
  makes `VGE_SealantPopper` a real answer, and argues for splitting the farm across two
  independently sealed rooms so one breach cannot take the whole food supply.
- **`VGE_Oxyalgae` competes for the same hydroponics cells.** A ship breathing through algae
  oxygenators must size the farm for food *and* air. **[V]**

## Defenses

Not the pursuit — [`TRACE.md`](TRACE.md) and [`PRESSURE.md`](PRESSURE.md) own that. This is
the ladder the hull can mount, and it is entirely XML retiering. All rows **[V]**.

| Tier | Piece | Cells | Numbers |
|---|---|---|---|
| Spacer | `GravshipShieldGenerator` ×2 (max 2) | 9 ea | radius 24.9, 500 HP, up 100 s, 4 h charge, EMP-disarmed 1,500 ticks, intercepts ground **and** air |
| Spacer | vanilla turrets | 1–4 | fly fine on substructure |
| Spacer | `VGE_PointDefenseTurret` | 9 | the only thing in the corpus that shoots down hostile `DropPodIncoming` |
| Ultra | `VGE_AnticraftCaster` / `VGE_GaussGun` / `VGE_JavelinPod` | 9 ea | the caster draws 50,000 W — a power-plant decision |
| Ultra | GravTech `AdvShip_ShieldGenerator` | 9 | radius 44.9, 2,000 HP, 1,100 W |
| Ultra | GravTech `ShieldPylon_GT` | 1 | radius 5.3, **0 W**, 1 Gravcore + 1 `BroadshieldCore` |

**The shield is a burst, not a wall** — 100 seconds up against four hours of charge, and an EMP opens
the window for free. **Both shields depend on the engine**: `CompGravshipShieldGenerator.ShouldCharge`
requires `Facility.LinkedBuildings.Count > 0`, so killing the grav engine stops the ship charging.
Any pursuit design should know both.

## Living on the orbit layer

`Map.IsPlayerHome` returns true whenever `wasSpawnedViaGravShipLanding` or
`GravshipUtility.PlayerHasGravEngine(map)`. **[V]** It is read very widely, and the good news is
that almost all of those readers keep working: the storyteller targets the ship, `WealthUtility`
counts it, every `Alert_Need*` fires, `ForbidUtility` stops forbidding, pens and roaming work,
royal-title expectations apply. **[V]** **Retiring the planetside base does not break the home-map
machinery.**

Five things do change, and four of them are the *layer*, not the flag. All **[V]**.

1. **No walking off the map.** `ExitMapGrid.MapUsesExitGridNow` is false for home maps, pocket maps
   and `Biome.inVacuum`; `BiomeDef Space` also sets `canExitMap false`.
2. **No caravans in orbit at all** — `PlanetLayerDef Orbit` sets `canFormCaravans: false`. Caravan
   trade, caravan quests and caravan rescue arms all go.
3. **The incident pool collapses to 18 of 91** (T-48). This is the one that needs a patch pack,
   and it is build (b). Quests are gated by `QuestGen_Get.GetMap(canBeSpace)`, not the whitelist —
   Routes C and D (§ *Quests are gated somewhere else entirely*).
4. **`Find.RandomSurfacePlayerHomeMap` returns null** once the only home is off the root surface
   (T-49), taking `QuestNode_GetSiteTile` and `QuestPart_SpawnMonolith` with it. Joiners fail
   elsewhere: T-128, not T-49 (§ *Nobody joins*).
5. **An orbital home is not a `Settlement`.** `GravshipUtility.ArriveNewMap` only calls
   `SettleUtility.AddNewHome` where the layer's `DefaultWorldObject == SettlementWorldObjectDef`;
   `Orbit` has `Space` and `SpaceSettlement`. So the orbital home does not count against
   `Prefs.MaxNumberOfPlayerSettlements`. Landing on an empty *surface* tile does create a Settlement
   and does count.

The shrine `MapParent` pattern still stands, and the gravship still flips it into a player home if
it lands there — but only on a **surface** tile. A shrine on an orbit tile is already inside the
whitelist fence, which is a different and stronger reason nothing can raid it. (This finding was
written for #10, which is now closed; it is recorded here because nothing else carries it.)

## Ordinary colony life on an orbital home

Which of the colony's everyday life continues once the ship is the home and the home is in orbit,
and by which routes the rest is recovered. Answers
[`docs/requirements/SPACE.md`](../requirements/SPACE.md) § *Living in orbit*; established by
[#147](https://github.com/cjd721/Rimworld-Archinity/issues/147). The section above,
*Living on the orbit layer*, states the five layer facts; this one states what they cost and what
buys them back.

### Verdict

- **Possible? Partly, and the split is sharp.** Everything the colony *does to itself* works in
  orbit unchanged — food, production, research, recreation, beauty, temperature, life support,
  penned animals, prisoners held and recruited, pregnancy, birth, graves and Ideology rituals.
  Everything that *arrives* is shut, by **four separate gates**, of which build (b) prices
  two, and **every walk-in path in the game is structurally dead in orbit**, so the obvious XML
  fix for visitors and trader caravans is a silent no-op. **No vanilla joiner quest can generate at
  all.** All of it is reachable; most of it by XML.
- **Multiplayer? Yes** for every route but F. MP Compat carries `vanillaexpanded.gravship` and does
  not carry `shunter.bettertradersguild`.

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **A** | The four-gate whitelist pack: which disasters, conditions, threats and factions exist in the orbital act | our patches on Odyssey's `layerWhitelist` / `canOccurOnAllPlanetLayers` / `arrivalLayerWhitelist` | XML | Easy per def, **Medium** as a curated pack | Yes |
| **B** | Orbital weather and hazards, shipped and pre-whitelisted: 9 incidents, 8 game conditions | `vanillaexpanded.gravship` | ships as-is | Easy | Yes |
| **C** | People arriving and joining, authored as quests on the channel the engine leaves open — pods and shuttles | `QuestNode_GetMap`(`canBeSpace`) + `QuestNode_GeneratePawn` + `QuestNode_DropPods`; donors `OrbitalFugitive`, `Script_BTG_TradeRequest` | XML | Medium | Yes |
| **D** | Vanilla's own wanderer and refugee-pod family firing in orbit unmodified | our assembly, on `QuestNode_Root_WandererJoin.CanBeSpace` | C# | Medium | Yes |
| **E** | Visitors and walking trader caravans at the ship | our assembly, on `IncidentWorker_NeutralGroup.TryResolveParmsGeneral`; donor `PawnsArrivalModeWorker_EdgeDrop` | C# | Medium | Yes |
| **F** | The outbound half of orbital trade: shuttle to a station and trade there | `shunter.bettertradersguild` | ships as-is | Easy | **No** |
| **G** | *(not recommended)* Remove the standing cabin-fever penalty | `PatchOperationReplace` on `NeedOutdoors` stage 2 | XML | Easy | Yes |

Every mechanism cited below is **[V]**. Every claim that they compose into the described behaviour
is **[I]** by construction. **Nothing is selected.** `docs/requirements/SPACE.md` § *Living in orbit*
asks for ordinary colony life wherever the fiction allows; which defs pass each gate is content for
[the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119).

**The recommendation, not a selection: A + B + C.** B is free content that already opens both of
the gates it needs, A is the only thing that makes the storyteller's orbital pool non-trivial, and
C is the one arrival channel that does not need an assembly. D and E are worth their weight only if
the fiction wants *vanilla's* people rather than ours.

### The four gates, and what passes them today

`PlanetLayerDef Orbit` sets **four** whitelist flags, each with a different reader and a different
XML key — `docs/TRAPS.md` **T-48** carries all four; build (b) covers the first two. All **[V]**.

| Gate | Reader | Opened by | Passing today |
|---|---|---|---|
| Incidents | `IncidentWorker.CanFireNow` | `IncidentDef.canOccurOnAllPlanetLayers` / `layerWhitelist` | **18 of 91** |
| Game conditions | `GameCondition.MapExcludedByFilter` | `GameConditionDef.canAffectAllPlanetLayers` / `layerWhitelist` | **4 of 32** |
| Faction arrivals | `IncidentWorker_PawnsArrive.FactionCanBeGroupSource` | `FactionDef.arrivalLayerWhitelist` | **4 factions** |
| Arrival modes | `PawnsArrivalModeWorker.CanUseOnTile` | `PawnsArrivalModeDef.layerWhitelist` | **5 of 10** |

`onlyAllowWhitelistedQuests` and `onlyAllowWhitelistedBiomes` exist on `PlanetLayerDef` and Orbit
does **not** set them. **[V]**

**Corpus scope for every count in this section: vanilla + Royalty + Ideology + Biotech + Odyssey.
Anomaly is not installed on this disk** (`RimWorld/Data/` holds five folders). **[V]** So 91, 139
and 32 are five-set totals, and any Anomaly def is outside them. #71's 18/91 was measured against
the same five and reproduces exactly.

**There is a fifth layer gate, at the building rather than the layer.**
`CompProperties_Mannable.planetLayerWhitelist`, read twice in `CompMannable` —
`CompInspectStringExtra` and `CompFloatMenuOptions`, both emitting `CannotFunctionOnLayer`. **[V]**
Vanilla sets `<planetLayerWhitelist><li>Surface</li>` on the abstract `BaseArtilleryBuilding`, whose
only concrete child is **`Turret_Mortar`** — so **mortars cannot be manned in orbit**, loudly, with
the reason stated in the float menu. Vanilla Furniture Expanded – Security applies the same gate to
its manned turrets and to `CompProperties_WorldArtillery`'s host. **[V]** This qualifies
§ *Defenses* above, which says "vanilla turrets — fly fine on substructure": **automatic** turrets
do; **manned** ones do not, and the mortar is the one the pursuit ladder would otherwise reach for.
It is not one of the four layer gates and no whitelist pack touches it; the lever is
`PatchOperationAdd` of `<li>Orbit</li>` to that comp, XML, Easy. **[I]** that the patch is
sufficient.

- The 18 incidents are seven `GiveQuest*` children of the abstract `GiveQuestBase`, plus `Aurora`,
  `Eclipse`, `MeteoriteImpact`, `OrbitalDebris`, `PsychicDrone`, `PsychicSoothe`,
  `ResourcePodCrash`, `ShortCircuit`, `OrbitalTraderArrival`, `ShipChunkDrop` and `RaidEnemy`. This
  reproduces #71's count exactly from an independent parse of the merged def tree with
  `ParentName` resolved. **[V]**
- The 4 conditions are `Aurora`, `Eclipse`, `PsychicDrone`, `PsychicSoothe`. **No vanilla weather,
  fallout, solar flare or blight exists in orbit at all**; build (b) opens this gate alongside
  incidents.
- The 5 arrival modes are `EdgeDrop`, `EdgeDropGroups`, `RandomDrop`, `MechClusterDrop`,
  `SpecificDropDebug`. **`CenterDrop` is `Surface`-only** — nothing drops on top of you in orbit.
- The 4 factions are Odyssey's `TradersGuild` and `Salvagers`, Core's `Mechanoid` and Royalty's
  `Empire`. **Pirates, outlanders and tribals cannot send anyone to an orbital home**, friendly or
  hostile, whatever the incident whitelist says — the faction gate is checked separately.
  `TradersGuild` also sets `neutralArrivalLayerBlacklist: Surface`, so Ludeon's intent is that its
  *neutral* groups appear only in orbit; it ships `caravanTraderKinds` and `visitorTraderKinds`
  **empty**, which is why they never do.

### Quests are gated somewhere else entirely

The quest feed does **not** run through `onlyAllowWhitelistedQuests`. Three other gates do the work,
and only the second is silent. All **[V]**.

1. **`QuestScriptDef.everAcceptableInSpace`** — `QuestGen.Generate` attaches
   `QuestPart_RequirementsToAcceptPlanetLayer` to every root that is neither `everAcceptableInSpace`
   nor `autoAccept`, and its `CanAccept` refuses with `QuestNotSpace` / `QuestRequiredLayer`. **A
   loud, stated refusal on the Accept button**, not a disappearance. **66 of 139** concrete
   `QuestScriptDef`s already clear it.
2. **`QuestGen_Get.GetMap(canBeSpace: false)`**, the default — returns null when the only home is
   in space, so the root's `TestRun` fails and the quest is never offered. **This, not the
   whitelist, is what actually empties the quest feed in orbit**, and nothing is logged.
3. **`QuestScriptDef.CanQuestOccurOnTile`**, the layer whitelist proper — **18 of 139** pass, all of
   them Odyssey's orbital-site family. Note that `World.Tile` is `PlanetTile.Invalid`, so for the
   `World`-targeted `GiveQuest*` incidents `IncidentWorker_GiveQuest.CanQuestOccurOnTile`
   short-circuits to `true` and never applies.

**So build (b) covers incidents and game conditions, not quests.** `Orbit` never sets
`onlyAllowWhitelistedQuests`, and the feed is emptied by `QuestGen_Get.GetMap(canBeSpace: false)` — a
C# default that no `<li>Orbit</li>` reaches. **A whitelist-only patch pack restores the incidents and
leaves the quest feed as empty as it found it**; quests are Route C or D.

**The 18 is not the same measurement as `ORBIT.md`'s ten, and both are correct.** **[V]**
`docs/specs/ORBIT.md` counts quest scripts that **place a site on** the Orbit layer — a destination
a surface-based colony flies to. This section counts quest scripts that **pass the tile gate when
the colony's own home tile is Orbit** — whether a quest can be offered at all while the ship is the
home. Different predicates over the same 139. ORBIT.md's ten is a **strict subset** of this
eighteen: its six scanner-given `OpportunitySite_*`, its three orbital `Gravcore_*` and
`OrbitalFugitive` all appear here. The eight this adds —
`Gravcore_AncientReactor`, `Gravcore_AncientStockpile`, `Gravcore_CrashedMechanoidPlatform`,
`Gravcore_FrozenTerraformer`, `Gravcore_InsectLair`, `Gravcore_MechanoidRelay`, `GravshipWreckage`
and `SurveySite` — carry `canOccurOnAllPlanetLayers: true` so they may be *offered* to an orbital
home, while placing their sites on the **Surface**. (`SurveySite`'s `QuestNode_Root_Site` is
whitelisted `Surface` outright. **[V]**) Neither number supersedes the other and neither file needs
changing; the distinction is *offered here* versus *placed there*.

**Route C is the XML answer and Ludeon uses it themselves.** `Script_OrbitalFugitive.xml` composes
`canOccurOnAllPlanetLayers`, `everAcceptableInSpace`, `<QuestNode_GetMap><canBeSpace>true` and
`QuestNode_Root_Site` with an Orbit whitelist; Better Traders Guild ships two more of the same
shape. `QuestNode_GeneratePawn` and `QuestNode_DropPods` (with `joinPlayer` / `makePrisoners`) are
the arrival half, and `DropCellFinder.GetBestShuttleLandingSpot` has **no layer or vacuum gate**, so
shuttles are the second channel. **[V]**

### Nobody joins, and the flag that says otherwise is a dead letter

**No vanilla quest that adds a person to the colony can generate on an orbit-only home.** **[V]**
`QuestNode_Root_WandererJoin` declares `protected virtual bool CanBeSpace => false` and **no
subclass in vanilla or the four installed DLC overrides it** — swept the whole decompile for
`override bool CanBeSpace`, zero hits. The affected defs:

| Def | Source | Root node | Evidence |
|---|---|---|---|
| `WandererJoins` | `Core/Defs/QuestScriptDefs/Script_WandererJoins.xml` | `QuestNode_Root_WandererJoin_WalkIn` | **[V]** |
| `RefugeePodCrash` | `Core/Defs/QuestScriptDefs/Script_TransportPodCrash.xml` | `QuestNode_Root_RefugeePodCrash` | **[V]** |
| `RefugeePodCrash_Baby` | `Biotech/Defs/QuestScriptDefs/Script_TransportPodCrash_Baby.xml` | `QuestNode_Root_RefugeePodCrash_Baby` | **[V]** |
| `WandererJoinAbasia` | `Royalty/Defs/QuestScriptDefs/Script_WandererJoins.xml` | `QuestNode_Root_WandererJoinAbasia` | **[V]** |
| `RefugeePodCrash_Ghoul` | Anomaly — **not installed on this disk** | `QuestNode_Root_RefugeePodCrash_Ghoul` | **[I]** — the *class* is in the assembly and inherits the same unoverridden `CanBeSpace`; its def was not read |

Every one of them sets `<autoAccept>true</autoAccept>`. **[V]**

Four things make this load-bearing:

- `RefugeePodCrash` **arrives by drop pod** (`AddSpawnPawnQuestParts` → `quest.DropPods`), so
  nothing about the arrival is impossible in orbit. Only the map lookup is.
- **There is a second, independent blocker in the same node.** `QuestNode_Root_WandererJoin.RunInt`
  calls `quest.AcceptanceRequirementNotSpace(var.Parent)` whenever `!CanBeSpace` — **regardless of
  the def's own flags**. **[V]** So even a build that fixed only `TestRunInt` would produce a quest
  the colony cannot accept. Route D must clear both, and `CanBeSpace` is the one seam that does.
- **`everAcceptableInSpace: true` on these defs is a dead letter, but it is not an ignored field,
  and the difference matters to anyone who later tries to use it.** The field *is* consumed, in
  `RimWorld.QuestScriptDef.CanQuestOccurOnTile`:
  `if (!autoAccept && !everAcceptableInSpace && layerDef.isSpace) return false;` **[V]** — and in
  `QuestGen.Generate`'s `if (!root.everAcceptableInSpace && !root.autoAccept)`. Because every def in
  the table above already sets `autoAccept`, **`!autoAccept` short-circuits both tests before the
  flag is ever reached**, so setting or clearing `everAcceptableInSpace` on them changes nothing.
  Its net effect here is nil; its effect elsewhere, on the 60-odd non-`autoAccept` roots that carry
  it, is real.
- Even when a joiner letter is produced, `ChoiceLetter_AcceptJoiner` **disables the Accept option**
  when the target map's layer `isSpace`. **[V]** The path is barred three times: once silently at
  generation, once at acceptance by the quest part, once at the letter.

**T-49 does not reach joiners.** In 1.6 `Find.RandomSurfacePlayerHomeMap` appears in
`QuestNode_Root_WandererJoin` **only inside the `CanBeSpace == true` branch, which nothing
reaches**; the live path is `QuestGen_Get.GetMap`. T-49's other two consumers,
`QuestNode_GetSiteTile` and `QuestPart_SpawnMonolith`, do read it and stand — so build (d) is the
right patch for those two, and the wrong patch for joiners. **[V]** Registered as T-128; T-48
carries the four gates.

### What no route can do

All **[V]** unless marked.

- **No walking on or off the map, ever.** Three independent causes: `Map.CanEverExit` is false
  (`BiomeDef Space` sets `canExitMap false`) so `PawnsArrivalModeWorker.CanUseOnMap` rejects any
  `walkIn` mode; the three walk-in modes carry no layer whitelist either; and Odyssey's
  `TerrainDef Space` is **`Impassable`**, so `RCellFinder.TryFindRandomPawnEntryCell` has no edge
  cell to find. Whitelisting `VisitorGroup`, `TravelerGroup` or `TraderCaravanArrival` for Orbit is
  a **silent no-op** — the worker returns false and the storyteller moves on.
- **Nobody who arrives can leave.** `JobGiver_ExitMap.TryGiveJob` returns null on a map that cannot
  exit, and every departure toil in the game ends in that job giver. **[I]** on the composition.
- **Raiders never flee.** `Lord`'s constructor adds `LordToil_PanicFlee` only when
  `Map.CanEverExit`; `QuestNode_Raid` forces `canTimeoutOrFlee` false likewise. Every orbital raid
  is fought to the last pawn, and the fiction cannot opt out.
- **No siege and no breaching.** Five of nine `RaidStrategyDef`s survive — `ImmediateAttack`,
  `ImmediateAttackFriendly`, `ImmediateAttackSmart`, `StageThenAttack`, `ImmediateAttackSappers`.
  `Siege` is whitelisted `Surface`; both `ImmediateAttackBreaching*` list only `EdgeWalkIn`;
  `EmergeFromWater` is blacklisted. **Sappers survive**, and a sapper raid on a pressurised hull is
  a decompression event the engine does not know it is causing.
- **Prisoners cannot be released and slaves cannot be emancipated.**
  `WorkGiver_Warden_ReleasePrisoner` and `WorkGiver_Warden_EmancipateSlave` both bail on
  `!MapHeld.CanEverExit`. In orbit a prisoner's only exits are recruitment, execution, harvest, sale
  to a trade ship, or age.
- **No wild animals and no grazing.** `BiomeDef Space`: `animalDensity 0`, `plantDensity 0`,
  `wildAnimalsCanWanderInto false`, `maxFishPopulation 0`. Pens work — `IsPlayerHome` holds — but on
  `fertility 0` decking there is nothing to graze, so livestock are hay-and-kibble only. **[I]** on
  the pen conclusion.
- **The Space biome's own disease table is dead.** `BiomeDef Space` lists `Disease_OrganDecay` at
  commonality 20, and `StorytellerComp_Disease` picks through `IncidentWorker.CanFireNow` — which
  that def does not pass. A disease Ludeon wrote for space can never fire there.
- **A standing −5 across the crew.** `Need_Outdoors.NeedInterval` decays at −0.32/day under a
  non-thick roof with a **floor of 0.2**; `CurCategory` at 0.2 is `CabinFeverSevere`, which
  `ThoughtWorker_NeedOutdoors` maps to stage 2 of `NeedOutdoors`, `baseMoodEffect −5`. Every
  gravship roof is `RoofConstructed` (`isThickRoof false`) and VGE's `VGE_VacBarrierRoof` is thin
  too. The need refills only where `Position.UsesOutdoorTemperature` — unroofed, i.e. vacuum — so
  the crew pays it unless they take vacsuit walks outside the hull or are `PrefersIndoors`
  (Undergrounder, Ideology `Tunneler`). **[I]** on "permanent and colony-wide"; **[V]** on every
  value in the chain. **This is a beat, not only a cost**: the ship makes people want to see sky.
- **Abilities marked `useableInVacuum: false` are off for the whole map**, not just in breached
  rooms — `Ability.CanCast` and `CompApparelVerbOwner` test `MapHeld.Biome.inVacuum`, never the
  cell. Two defs in vanilla + DLC set it; any mod that does is off for the entire orbital act.
- **Orbital settlements cannot be peacefully visited at all.** `Settlement.Visitable` returns
  `!Tile.LayerDef.isSpace`. Route F is the corpus's only answer.

### Available mechanisms — what the corpus supplies

**Two passes, because the gates have an XML half and a C# half and an XML sweep cannot see the
second.** Construction is reported in full under *Verification — the wide pass behind the orbital
negatives*, below.

**Eleven mods on disk match the layer-field sweep; ten touch the four layer gates, and none of
them widens one for orbit beyond its own content.** All rows **[V]**.

| Mod | What it supplies for orbital life | Limitation |
|---|---|---|
| `vanillaexpanded.gravship` | **9 orbit-whitelisted incidents and 8 matching game conditions** — solar flare, gravitational anomaly, comet, micrometeor storm, space debris, asteroid shower, dust cloud, toxic dust cloud, escape-pod crash — plus `VGE_OpportunitySite_SolidCoreAsteroid` | hazard, not society; hard VEF dependency; opening both gates together is the pattern, and it is the only mod that does |
| `VGE_EscapePodCrash` | the **only shipped thing that delivers a body to an orbital home**: `IncidentWorker_EscapePodCrash` drops a `VGE_EscapePodSkyfaller` on a roofed non-natural cell carrying a `VGE_DamagedEscapePod` with `CompProperties_HackableEscapePod` (defence 4000, intellectual 5) | it punches the hull by design; contents are a hack roll, not a quest |
| `shunter.bettertradersguild` | `Settlement.Visitable` reopened for guild stations (Harmony postfix), `WorldObjectCompProperties_TradeRequest` patched onto `SpaceSettlement`, a `TransportersArrivalAction_Trade` shuttle option, and two space-safe quest scripts | **not covered by Multiplayer Compatibility** — swept both encodings, both validated |
| `ushanka.glittertechexpansion` | 3 `canOccurOnAllPlanetLayers` incidents and 2 space-safe quests | not in MP Compat |
| `godsfathermixtape.worksitesexpanded` | `OpportunitySite_OrbitalPlatform` quest | |
| `vanillaexpanded.vexploratione` | `VEE_Aurora`, orbit-eligible | |
| `ushanka.hackingexpansion` | one orbit-eligible incident | |
| `oskarpotocki.vfe.deserters` | one `QuestNode_GetMap canBeSpace` in `PlotMission` | |
| `icc.fov.elves` | the **only mod faction** declaring `Orbit` in `arrivalLayerWhitelist` | |
| `smashphil.vehicleframework`, `dankpyon.medieval.overhaul` | `ParatrooperDrop` and a medieval siege strategy, both whitelisted **`Surface` only** | they narrow orbit, they do not widen it |
| `vanillaexpanded.vfesecurity` | **not a layer gate — the fifth, building-level one**: `planetLayerWhitelist: Surface` on its manned turrets and on the `CompProperties_WorldArtillery` host | manned VFE Security guns and world artillery do not work in orbit; the eleventh mod, and the one the first sweep missed |

**One live collision, found by the C# half.** `VFEInsectoids.PawnsArrivalModeWorker_CanUseWith_Patch`
postfixes `PawnsArrivalModeWorker.CanUseWith` and returns **false for `Faction.OfInsects` on every
drop mode** — `EdgeDrop`, `CenterDrop`, `EdgeDropGroups`, `RandomDrop`. **[V]** Since all five
orbit-capable arrival modes are drop modes, **insectoids can never arrive at an orbital home while
VFE Insectoids is loaded**, whatever the whitelists say. Conflicts are cargo, not verdicts — the
mechanism is recorded here and the collision belongs in `docs/data/MOD-VERDICTS.md`.

**The negative, now carried on both halves.** Nothing in the corpus ships a general orbital-life
pack: no mod bulk-whitelists vanilla's social incidents for orbit, no mod opens the faction arrival
gate beyond one faction of elves, and **no mod re-points the neutral-group path off the impassable
map edge**. The two mods that patch that path at all — `wowgag.rimpacts`
(`Patch_NeutralGroup_FactionCanBeGroupSource`, which suppresses embargoed and civil-war factions)
and `vanillaracesexpanded.archon` — **narrow** it. **[V]** The nearest donor is VGE, and what it
donates is weather.

### Verification — the wide pass behind the orbital negatives

Reported because a null-interleaved negative is worth only the bytes that reached ripgrep.

**XML half.** Both roots, `rg -i -l -g '*.xml' -g '!**/obj/**'`, pattern
`canOccurOnAllPlanetLayers|everAcceptableInSpace|arrivalLayerWhitelist|neutralArrivalLayerWhitelist|neutralArrivalLayerBlacklist|arrivalLayerBlacklist|neverPossibleInSpace|canBeSpace|layerWhitelist|layerBlacklist|onlyAllowWhitelisted|canAffectAllPlanetLayers`,
attributed through `python tools/corpus.py --which -`. **Validator:** the identical form against
`RimWorld/Data/` returns 43 files, so it executes. **Result: 26 paths → 11 mods**, the table above.
`-i` is what surfaced `vanillaexpanded.vfesecurity`; the case-sensitive first run reported ten.

**C# half.** Both roots, `rg -a -i -l -g '*.dll' -g '!**/obj/**' -g '!**/Referenced/**'`, twelve
symbols — `FactionCanBeGroupSource`, `TryResolveParmsGeneral`, `TryFindRandomPawnEntryCell`,
`MapExcludedByFilter`, `CanQuestOccurOnTile`, `CanBeSpace`, `CanUseOnTile`, `arrivalLayerWhitelist`,
`onlyAllowWhitelistedIncidents`, `onlyAllowWhitelistedArrivals`, `everAcceptableInSpace`,
`canOccurOnAllPlanetLayers` — run **twice**: ASCII (reaches `#Strings` member names and `#Blob`
attribute arguments), then null-interleaved UTF-16LE with the `\x00` escapes **typed literally into
the pattern**, never built through `$(…)`.

**Validators, each drawn from the heap it tests.** ASCII: `IncidentWorker_EscapePodCrash`, a
`#Strings` type name independently confirmed by decompiling it — returns
`3609835606/…/VanillaGravshipExpanded.dll`. UTF-16LE: `VREAndroids`, an `AccessTools.TypeByName`
literal that lives in `#US` — returns 17 files across both roots. Both forms execute.

**Result.** Nine of the twelve symbols return **zero in both encodings**. The three that hit:
`FactionCanBeGroupSource` (24 ASCII paths → 6 mods, 1 UTF-16), `TryFindRandomPawnEntryCell` (65
ASCII), `TryResolveParmsGeneral` (zero — **nothing in the corpus overrides or patches the method
Route E names**). Intersecting the 77 arrival-path files with an orbit-awareness sweep
(`inVacuum|isSpace|PlanetLayerDef`) leaves **four** assemblies — VEF, VFE Insectoids, Faction
Territories, RimPacts — and all four were read: two patch the arrival path and both **narrow** it,
one for insectoid drop modes and one for embargoed factions. **[V]** No mod widens it for orbit.

### Status

**Evidence class: READ.** Verified against the whole-assembly decompile of RimWorld 1.6
`Assembly-CSharp.dll`, the Core/Royalty/Ideology/Biotech/Odyssey def tree parsed with inheritance
resolved, and decompiled `VanillaGravshipExpanded.dll`, `BetterTradersGuild.dll` and
`Multiplayer_Compat*.dll`.

- **Verified:** the four layer gates and their readers, plus the fifth at
  `CompProperties_Mannable.planetLayerWhitelist`; the 18/4/5/4 counts, measured over vanilla + the
  four installed DLC (**Anomaly is not on disk**); the three quest gates and the 66-of-139
  `everAcceptableInSpace`/`autoAccept` count; `CanBeSpace` unoverridden, and the second blocker in
  `RunInt`; `TerrainDef Space` impassable; the exit, flee, release and emancipate consequences; the
  raid strategy survivors; the `Need_Outdoors` chain; the eleven-mod corpus survey on **both** an
  XML and a dual-encoding DLL pass, each with a heap-matched validator; the MP Compat sweep.
- **Inferred:** that each route composes into the described behaviour; the pen and prisoner-milling
  conclusions; "permanent and colony-wide" for the cabin-fever penalty; `RefugeePodCrash_Ghoul`,
  whose class was read but whose Anomaly def is not installed.
- **One RUN item.** Reading cannot settle whether a drop-pod arrival onto a **fully roofed** orbital
  hull finds a landing cell. **What to observe:** only home map on an orbit tile, hull completely
  roofed, fire `RaidEnemy` from an orbit-whitelisted faction, and record whether pods land, whether
  they punch the roof, and whether the room depressurises. If they cannot land on a sealed hull,
  every drop-based route here needs an unroofed pad and the fiction needs a docking bay.

Established by [#147](https://github.com/cjd721/Rimworld-Archinity/issues/147), which also confirmed
#71's two counts from an independent parse and corrected T-49's attribution for the joiner family.
One small correction to [#66](https://github.com/cjd721/Rimworld-Archinity/issues/66): the field on
`GenStep_OrbitalPlatform` is `private LayoutDef layoutDef`, not a `StructureLayoutDef` — its
conclusion (def-driven, no new C#) is unaffected. **[V]**

## A gravship en route when its landing tile changes hands

### Purpose and scope

This section answers [#177](https://github.com/cjd721/Rimworld-Archinity/issues/177): **what a
gravship already committed to a tile does when that tile changes hands, or gains a hostile
settlement, before the ship lands, and by which routes the player's commitment is kept.**

It is the gravship clause of `TERRITORY.md` § *A caravan en route when its destination changes
hands* ([#152](https://github.com/cjd721/Rimworld-Archinity/issues/152)). The routes use the same
letters, **GF-A to GF-G for CF-A to CF-G**, and each says where the gravship differs. It serves the
same requirement: [`requirements/ERA.md`](../requirements/ERA.md) § *The era advance*, *"Nothing
else may change on a delay… while the player is caravanning toward it"*. It also covers the
Schism ([#130](https://github.com/cjd721/Rimworld-Archinity/issues/130)), revolts
([#131](https://github.com/cjd721/Rimworld-Archinity/issues/131)), and ordinary conquest by us,
Rim War, Faction Territories and RimPacts.

This section does not own:
- **which** settlements transfer ([#34](https://github.com/cjd721/Rimworld-Archinity/issues/34));
- **how** a transfer is written (`engine/factions-and-worldgen.md`; **T-140**);
- **selecting a route** ([#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)).

### Verdict

- **Possible? Yes.** Odyssey never re-checks the landing tile, and nothing in the 155-mod corpus
  does either. A gravship lands on whoever holds the tile when it arrives, and **any NPC
  settlement it lands on counts as attacked**, with the owner driven to hostile (**T-171**). Every
  route below closes that gap. The seams are all public or reachable, and the arrival runs on the
  synced world tick.
- **Multiplayer? Yes** for GF-B, GF-C, GF-D, GF-E and GF-G. **GF-F is Yes** when it reuses the
  existing-map landing UI, which Multiplayer already syncs, and **With work** as our own dialog
  (T-82/T-95/T-96).

### How gravship travel differs from a caravan

All **[V]** in `Assembly-CSharp.dll` 1.6. The mechanism is in
`engine/gravship-and-substructure.md` § *In flight*.

| | Caravan, pod or VF vehicle (#152) | Gravship |
|---|---|---|
| What it holds | an arrival action holding the target **object** | a **tile** (`Gravship.destinationTile`) and no arrival action |
| Re-check | caravans `StillValid` on every interval; pods and aircraft on arrival or never | **never**. The launch validator and confirmation run once, at the pick |
| Destroy-and-recreate | aborts the order (`Spawned == false`) | **lands on the replacement** |
| `SetFaction` | re-checks against the new owner | lands on the new owner |
| Landing on a non-hostile settlement | only an **attack** order hits allies (T-138) | **every** landing on a non-player settlement is an attack (`ArriveNewMap` → `AffectRelationsOnAttacked`) |
| Can stop mid-route | `StopDead` | **no**. The ship has no hover state; every outcome is a landing somewhere |
| Window | days of marching | **4,000 ticks per radian** of arc, at most about 12,600 ticks. Under VGE it starts earlier, at the launch ritual (T-172) |
| Player UI in flight | the caravan is selectable and re-orderable | `Gravship` declares no gizmos. There is no in-flight redirect |
| Player UI at arrival | the arrival letter | a landing marker (confirm or move) on both paths. **Abort** exists only on an existing map, and on a new map the relations hit is already applied |

**What each trigger can do inside that window:**
- **Era advance.** [#113](https://github.com/cjd721/Rimworld-Archinity/issues/113) fires it from
  research completion. While the ship flies, its crew is despawned into the world object, so the
  advance can land in the window **only** in these cases [I]:
  - through research on another map: a grav-anchored or VGE-kept origin, a second colony, or the
    other player's map;
  - during VGE's pre-launch ritual, when the colony is still on the ground.
- **Schism and revolt.** These are authored transfers on a quest or incident clock, so they can
  fire on any tick [I, both unbuilt].
- **Ordinary conquest.** NPC-on-NPC takeovers by Rim War, FT&V and RimPacts run on world ticks.
  The shapes are the same ones #152 read.
- **A tile that gains a settlement or site.** `Gravship.Tile` stays at the origin during flight, so
  the destination is never reserved. `TileFinder.TryFindNewSiteTile` (`!AnyWorldObjectAt`) can
  place a quest site on it [V], and Rim War's `Settler.ArrivalAction` →
  `WorldUtility.CreateSettlement` can found a settlement there [V].

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **GF-A** Vanilla as shipped | The ship lands on the new occupant. A formerly empty or hostile tile now held by an ally is **attacked, and the ally turns hostile**, with only an after-the-fact letter. **Not recommended alone** | vanilla | — | Easy | Yes |
| **GF-B** Sweep the ship inside our transfer | The transfer checks the one in-flight ship and VGE's pending launch targets, then warns and turns the ship back or diverts it (GF-C) | our transfer command | C# | Medium | Yes |
| **GF-C** Divert | The ship lands at its origin, at the nearest valid tile, or through vanilla's own crash-landing abort. A **response** fed by GF-B or GF-G, not a detector | our code on `Gravship.destinationTile` | C# | Medium | Yes; tile choice deterministic (T-135) |
| **GF-D** Protect the endpoint | Our transfer and placement code skips the ship's tile, or defers that tile's change until touchdown | our transfer selection (#34) | C# | Medium | Yes |
| **GF-E** Accept and warn | Vanilla stands. The transfer letter names the ship and what it will now land on, **while it is still in the air** | our transfer letter | C# | Easy–Medium | Yes |
| **GF-F** The arrival becomes a decision | On a changed tile, the player chooses to land, move or abort, and then an encounter or parley can follow | our arrival hook + vanilla landing marker, or our dialog | C# | Medium–Hard | Yes with the vanilla marker; With work with our dialog (T-82/T-95/T-96) |
| **GF-G** Guard the arrival | At touchdown, the tile is compared with what the player confirmed at launch, **whoever changed it**. On a mismatch the guard hands off to GF-C, GF-E or GF-F | Harmony prefix on `GravshipUtility.ArriveNewMap` / `ArriveExistingMap` (or `Gravship.TickInterval`) | C# | Medium | Yes [I] |

**GF-A — vanilla as shipped** (CF-A).
- **Gets:** nothing to build. A tile that stays hostile, or that passes from one hostile faction to
  another, lands as the player expected.
- **Cannot:**
  - warn at all before the landing;
  - tell a deliberate landing from a stale one;
  - spare a new owner who is an ally. Here it is **worse than CF-A**: a caravan with a trade
    order simply aborts, but a gravship has no order to abort.
- **Consequences:**
  - The hazard fires on the campaign's own transfers. The Schism takes Church ground, or an ally
    absorbs the hostile settlement the player was about to raid.
  - An empty tile can become a surprise landing inside an enemy base.

**GF-B — sweep the ship inside our transfer** (CF-B).
- **Gets:** the synced transfer reads three things, all public or scribed [V]:
  - `Find.CurrentGravship?.destinationTile` — there is one slot, so one ship at most;
  - `WorldComponent_GravshipController.landingTile` for the takeoff cutscene. It is private but
    scribed as `"targetTile"`, and Multiplayer freezes clients during the cutscene;
  - VGE's `LordJob_Ritual_ExposeData_Patch.targetTile`, a public static dictionary, for a launch
    that is scheduled but not yet flown (T-172).

  For each hit it sends one letter that names the ship and the new occupant, then applies a GF-C
  response or clears the pending ritual target so the player re-picks.
- **Cannot:**
  - see transfers made by Rim War, FT&V, RimPacts or quests;
  - see a site or settlement that appears on the tile;
  - stop the ship. Unlike CF-B's `StopDead`, every outcome is a landing somewhere.
- **Consequences:** no stored state, and no `Rand` unless the divert picks randomly. It is the
  smallest honest answer **for transfers we author**, as CF-B is for caravans.

**GF-C — divert** (CF-C, minus the rebind). The rebind lever disappears, because the ship already
follows the tile through a recreation.
- **Gets** three landing choices [I as composed; the seams are V]:
  - **home again** — `destinationTile` goes back to the origin. Unless a grav anchor or VGE kept
    that map, the origin is now empty, so the ship re-founds there (`ArriveNewMap` →
    `SettleUtility.AddNewHome`);
  - **nearest valid tile** — the donor is vanilla's
    `WorldComponent_GravshipController.AbortLanding`, which rewrites
    `Find.CurrentGravship.destinationTile` from a `FastTileFinder` query and rolls a doubled
    mishap chance;
  - **invoke `AbortLanding` itself** on an existing-map arrival, where it is already a synced
    method.

  `destinationTile` is a public field that vanilla itself rewrites.
- **Cannot:**
  - know what the player wanted;
  - let the player pick a new tile in flight without a picker of ours (see the build questions).
- **Consequences:**
  - `Gravship.DrawPos` slerps between `initialTile` (private) and the destination, so a
    mid-flight rewrite jumps the icon unless `initialTile` and `traveledPct` are reset. The step
    per tick is also recomputed from the new arc, so the remaining flight time changes. Both are
    harmless [I].
  - A divert to an empty **surface** tile founds a `Settlement`, which counts against the
    client-local `Prefs.MaxNumberOfPlayerSettlements` (see *Persistence and multiplayer*). The
    arrival path does not consult it [V].
  - Pick "nearest" deterministically, not through `GetClosestTile_NewTemp` (**T-135**).

**GF-D — protect the endpoint** (CF-D).
- **Gets:** the commitment is never broken, in one of two forms:
  - **skip for good**, exactly CF-D;
  - **defer until touchdown**. This is new for gravships. The window is short, bounded and
    observable: `Find.CurrentGravship` goes null in `LandingEnded`, and any pending VGE ritual
    target clears when the ritual ends.
  - **reserve the tile in flight** (added on review): a placeholder `WorldObject` on the
    destination tile for the flight's duration. Vanilla's `TileFinder.TryFindNewSiteTile` already
    rejects any tile with `AnyWorldObjectAt` [V], so quest sites skip it with no patch; the
    composition is [I], unbuilt. It covers **arrivals onto an empty tile only** — it does nothing
    against a transfer of a settlement already there, and a Rim War settler still needs its own
    check (unread).
- **Cannot:**
  - **skip for good** keeps the advance from being whole (the CF-D objection), and lets either
    player freeze a settlement by pointing a ship at it;
  - **defer until touchdown** is not admitted for the era advance by `ERA.md` § *The era
    advance*. *"Nothing else may change on a delay"* names no threshold, and *"a single,
    indivisible act"* names *"a world half re-authored — some settlements transferred, others
    not"* as the failure; a deferred tile is exactly that for the window, **however short**.
    Neither clause binds the Schism, a revolt or conquest, which are not the advance;
  - neither form can stop a Rim War settler or a quest site from taking the tile without also
    patching them.
- **Consequences:**
  - Defer needs a queued transfer, which is stored state.
  - It is the only route that fits the Schism played blow by blow, which can pick another target.

**GF-E — accept and warn** (CF-E).
- **Gets:**
  - one line in the transfer letter;
  - unlike CF-E, the warning can arrive **before** the consequence, because the ship is still in
    the air when the transfer fires. The player cannot act on it, though (see GF-C).
- **Cannot:**
  - avoid the attack on a new ally;
  - warn ahead of the era turn (#113 has no confirmation).
- **Consequences:** the attack hazard stays open unless GF-B's divert or GF-G is paired with it.

**GF-F — the arrival becomes a decision** (CF-F).
- **Gets:** the changed landing as a beat: the new owner's guns at the pad, a toll, a parley, or
  the choice to go round. There are two shapes:
  - **Vanilla's landing UI** [I as composed]. Vanilla already shows a landing marker on a
    new-map arrival (`GenStep_GravshipMarker` → `GravshipLandingMarker.SpawnSetup` →
    `Notify_LandingAreaConfirmationStarted`) [V]. That marker offers only confirm and move,
    though: the **Abort** button draws only when `landingMap` is set, which only
    `ArriveExistingMap` does. It also appears **after** `ArriveNewMap` has already applied the
    relations hit. So the route has three steps:
    1. generate the settlement's map without the attack consequence (`GetOrGenerateMap`, as
       `SettlementUtility.AttackNow` does);
    2. hand the ship to `ArriveExistingMap`, which gives confirm, move and abort (a crash landing
       nearby);
    3. apply the relations hit on confirm.

    Multiplayer already syncs `GravshipLandingMarker.BeginLanding` and `AbortLanding` [V].
  - **An E-letter or E-quest fired at arrival**, as in CF-F.
- **Cannot:**
  - reuse `IncidentWorker_CaravanMeeting` (same reason as CF-F);
  - be fired by the storyteller at the ship. `Storyteller.AllIncidentTargets` never includes the
    gravship, and its `Gravship` target tag is used by no `IncidentDef` in either corpus root [V].
- **Consequences:**
  - A generated enemy map is a real map, with defenders standing.
  - Our own dialog carries T-82/T-95, and a modded letter carries T-96.
  - It needs GF-G's comparison to know the tile changed.

**GF-G — guard the arrival** (CF-G).
- **Gets:** a prefix on `GravshipUtility.ArriveNewMap` and `ArriveExistingMap`, both reached from
  `Gravship.TickInterval` on the synced world tick [V]. `ArriveExistingMap` is called directly.
  `ArriveNewMap` is queued through `LongEventHandler.QueueLongEvent`, and vanilla's own
  `AbortLanding` queues it a second time, so the guard must let a divert it caused through [V].
  It compares the tile's current occupant,
  owner and relation with what the player confirmed at launch. It is the **only route that sees
  every source**:
  - our transfers;
  - Rim War settlers and conversions, RimPacts `CedeOne`, and FT&V;
  - quest sites, including one that sets `preventGravshipLanding`;
  - VGE's stale pre-ritual launch (T-172), for free.
- **Cannot:**
  - remember what was confirmed without new scribed state. `Gravship` has no spare field, and the
    controller stores only `takeoffTile`/`targetTile` (a build question);
  - a **stateless** variant can only re-ask whenever the tile holds any non-hostile settlement.
    That would also re-ask a player who deliberately confirmed a raid on a neutral.
- **Consequences:**
  - It covers what CF-G covers for caravans, and needs no knowledge of who made the change.
  - `ArriveNewMap` runs inside Multiplayer's `FactionContext` push for the ship's faction [V].
  - **Do not hang it on `TakeoffEnded` or `TravelTo`**, which run unfrozen and at client-local
    cutscene timing (**T-78**).

**Recommendation (not a selection):** **GF-G, feeding GF-F's vanilla landing-marker shape**, with
**GF-E's line** in the transfer letter.
- GF-G is the one detector that also catches the transfers we do not author and the tiles that
  gain a settlement. On a gravship both of those are live, because the destination is never
  reserved.
- GF-F's marker shape costs no dialog-sync work, since Multiplayer already syncs that UI.
- If a stored launch snapshot is unwanted, **GF-B + GF-C (home again)** is the smallest answer
  for our own transfers.

### Constraints

- **The ship always lands.** There is no hover, no cancel and no in-flight gizmo [V]. "Abort"
  means a landing somewhere else, and vanilla's own abort is a crash landing with a doubled
  mishap roll.
- **The launch dialog is the only warning today**, and it describes the tile as it was at launch
  [V] (`SettlementProximityGoodwillUtility.GetConfirmationDescriptions`). **T-171.**
- **Under VGE the commitment starts at the ritual**, and the launch itself re-checks nothing
  [V]. **T-172.**
- **One gravship at a time** (`Current.Game.Gravship`) [V]. A sweep has one object to find, and
  two Multiplayer players cannot both be in flight.
- **Transfer shape does not matter for a gravship** [V]. `SetFaction` and destroy-and-recreate
  both land on the new occupant. Contrast CF-A, where recreation aborts the order (**T-140**).
- **Nothing that runs at takeoff is safe for game-state writes** in Multiplayer (**T-78**).

### Available mechanisms

- **Vanilla, `Assembly-CSharp.dll` 1.6** [V]:
  - `CompPilotConsole.StartChoosingDestination_NewTemp` is the validator. `Settlement.GravShipCanLandOn`
    is `Faction != OfPlayer`, and `TileFinder.IsValidTileForNewSettlement(forGravship: true)`
    admits NPC settlements and rejects `Site.preventGravshipLanding`.
  - `SettlementProximityGoodwillUtility.CheckConfirmSettle` shows `ConfirmLandOnHostileFactionBase`
    or `ConfirmLandOnNeutralFactionBase`, plus the `GoodwillToMakeHostile` price, **at launch only**.
  - `WorldComponent_GravshipController.InitiateTakeoff` → `TakeoffEnded` → `GravshipUtility.TravelTo`
    adds the `Gravship` world object. `Tile` is the projected origin, and `destinationTile` is public.
  - `Gravship.TickInterval` advances `traveledPct` by `0.00025 / SphericalDistance` per tick. At
    1 it calls `ArriveExistingMap` if the tile's `MapParent` has a map, otherwise `ArriveNewMap`.
  - `ArriveNewMap` runs `GetOrGenerateMap` on the tile's current `MapParent`, or founds a home. For
    a non-player `Settlement` or attack `Site`, it sends *"gravship entered enemy base"* and calls
    `AffectRelationsOnAttacked`.
  - `ArriveExistingMap` opens the landing marker with confirm, move and `AbortLanding`.
    `AbortLanding` rewrites `destinationTile` to a `FastTileFinder` tile and calls `ArriveNewMap`.
    Neither landing path touches relations.
- **Vanilla Gravship Expanded** (`3609835606/1.6/Assemblies/VanillaGravshipExpanded.dll`) [V]:
  - it moves the pick before the launch ritual (T-172);
  - it patches `InitiateLanding` (moving pawns off the pad), `LandingEnded` (landing outcomes),
    `TakeoffEnded` (keep or settle the origin map) and `InitiateTakeoff` (a mood memory);
  - `WorldComponent_GravshipController_WorldComponentOnGUI_Patch` transpiles the landing marker's
    confirm button into `TryBeginLanding`, which checks **cells** (bounds, indestructible
    obstacles, a crash-landing confirm), never the tile or its owner. GF-F's marker shape must
    compose with it;
  - its gravlift launch targets the orbit tile directly above;
  - **nothing on arrival.**
- **RimPacts** (`3762723122/Assemblies/RimPacts.dll`) [V]:
  - `Patch_GravshipLandWarn` adds a second **launch-time** warning;
  - a postfix on `Settlement.GravShipCanLandOn` bars landing during its world war, **at the pick
    only**;
  - `Patch_GravshipAbandonKeepSettlement` changes what happens to the origin;
  - `Patch_Gravship_NegativeLanding` scales the landing-mishap odds for `Find.CurrentGravship`;
  - `Patch_SettlementAttacked_SiegeAid` postfixes `SettlementUtility.AffectRelationsOnAttacked`.
    It breaks a non-aggression pact with the owner, logs an unauthorized attack and can send
    allied aid. **A stale landing (T-171) therefore costs more under RimPacts.** It re-checks
    nothing.

  It is also a transfer source (`CedeOne`, #152).
- **Worksites Expanded** (`MiningOutpost.dll`) adds a launch-time warning for an orbital-platform
  site. **Defensive Positions** and **VEF** carry state across the flight (`Gravship..ctor`,
  `CopyCellContents`). **None touches the destination** [V].
- **Multiplayer** (`2606448745/1.6/AssembliesCustom/Multiplayer.dll`) [V]:
  - it syncs the tile-pick lambdas, `AbortLanding` (`SyncMethod`) and
    `GravshipLandingMarker.BeginLanding`;
  - it postfixes `ArriveExistingMap`/`ArriveNewMap` to open a session, and pushes the ship's
    `FactionContext` around `ArriveNewMap`.

  **MP Compat**'s `VanillaGravshipExpanded` class (in `Referenced/`) syncs VGE's pre-ritual pick
  and `ExecuteGravshipLaunch`.
- **Nearest donors for what does not exist:**
  - vanilla `Caravan_PathFollower`'s `StillValid` re-check, for the shape of GF-G;
  - vanilla `AbortLanding`, for GF-C;
  - the existing-map landing marker, for GF-F.
- **The wide pass** covered both corpus roots, `-g '*.dll' -g '!**/obj/**' -g '!**/Referenced/**'`,
  and `-i`, with ASCII **and** typed null-interleaved UTF-16 patterns for `ArriveNewMap`,
  `ArriveExistingMap`, `GravShipCanLandOn`, `InitiateTakeoff`, `TakeoffEnded`, `LandingEnded`,
  `AbortLanding` and `gravship`. It also ran ASCII-only for `InitiateLanding`,
  `GravshipController`, `GravshipLandingMarker`, `CheckConfirmSettle`,
  `StartChoosingDestination` and `TravelTo`, and UTF-16-only for `destinationTile` and
  `GravshipUtility`. Results:
  - `ArriveNewMap`, `ArriveExistingMap` and `AbortLanding` hit **only Multiplayer**. For
    `ArriveNewMap`, **both** encodings hit that one file, a same-heap validator for each sweep
    form.
  - `gravship` hit 11 mods in ASCII and 9 in UTF-16, the UTF-16 nine being a subset. All eleven
    were read by their `HarmonyPatch` targets.
  - `Referenced/` was searched separately for MP Compat's class.
  - The review re-ran the sweep. `ArriveExistingMap` is an **ASCII miss** even in Multiplayer,
    which names it only as an `AccessTools.Method` string literal. ASCII `destinationTile` hit 15
    mods, and `CurrentGravship` hit two. Intersected with a gravship reference, that leaves
    RimPacts, VGE, VEF, Worksites Expanded and Multiplayer, all read above.
    `AffectRelationsOnAttacked` (ASCII) adds Rim War, FT&V, VF and RimPacts. Two mods patch it:
    RimPacts (above), and Rim War's `Prevent_AffectRelationsOnAttacked_Patch`. That one skips the
    hit only on a one-shot `RimWarSettlementComp.preventRelationChange`, which only its caravan
    *reinforce* gizmo sets, so it never fires for a gravship. FT&V and VF only call it.
  - **No mod re-checks the landing tile** [V on the sweep as run].

### Status

**READ.** Every mechanism above is [V] and cited by `Type.Method`. Routes GF-B to GF-G are [I] as
compositions. The flight-time figure is [V] as a formula and [I] as a typical duration. Established
by [#177](https://github.com/cjd721/Rimworld-Archinity/issues/177).

It corrects the inherited framing from #152's open question: a gravship is **not** an aircraft that
skips a re-check. It carries no target at all. It also adds one case #152's caravans do not have:
the destination tile can **gain** a settlement or site, because nothing reserves it.

### Open questions

- **Era advance while a ship is in flight.** GF-D's *defer* form holds one tile's change until
  touchdown, which `ERA.md` § *The era advance* does not admit for the advance; it remains
  available for the Schism, a revolt or conquest. Capability: GF-A to GF-G. Choice:
  [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).
- **Transfer shape per beat** no longer matters for gravships, but still matters for caravans.
  *[#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).*
- **Build questions for the next map**, all owned by [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119):
  - where GF-G stores the launch-time snapshot;
  - GF-C's precedence between home, nearest tile and the vanilla abort;
  - whether GF-F generates the enemy map before touchdown or re-routes through
    `ArriveExistingMap` some other way;
  - whether an in-flight re-pick needs a tile picker of ours in Multiplayer;
  - GF-E's letter text.

## Persistence and multiplayer

**Nothing new is persisted.** `Building_GravEngine.validSubstructure` and `allConnectedSubstructure`
are `[Unsaved]` and rebuilt from `Map.terrainGrid` whenever `substructureDirty`; the durable state is
the terrain grid and the buildings on it, which vanilla already scribes. **[V]** The proposed alert
is stateless. Adding or removing any of the four build pieces from an existing save is safe. **[I]**

**Multiplayer.** The gravship path is already on Multiplayer's radar —
`rwmt.multiplayercompatibility` ships a shim naming `vanillaexpanded.gravship`, and `Multiplayer.dll`
references `CompGravshipFacility`. **[V]** Two concerns specific to this system:

- `Prefs.MaxNumberOfPlayerSettlements` is a **client-side, unsynced** slider (1–5). An orbital home
  does not consume a slot; a surface landing does. Two clients with different sliders disagree about
  whether a landing is allowed. **[V]**
- `Building_GravEngine.UpdateSubstructureIfNeeded` opens a `Dialog_NamePlayerGravship` the first
  time `validSubstructure.Count > 90` with `gravEngineInspected` set. **[V]** A window opened from a
  shared tick path is the usual MP hazard; see `CODING_STANDARDS.md`.

Nothing else in this system reads `Rand`, threads, or holds static collections keyed by map. **[V]**

## Failure and recovery

| Failure | Detection | Recovery |
|---|---|---|
| **Overbuilt deck** — cells past `SubstructureSupport` are silently dropped on launch, outermost first (T-46) | none today; the `N / M` inspect line is the only signal | build (c), the alert. Once dropped, the cells and everything on them are on the old map — recoverable only by flying back, and not at all if the old map was abandoned |
| **Budget computed from un-patched defs** (T-50) | none — the arithmetic looks right and the game disagrees | read `GetStatValue(SubstructureSupport)` off the engine's stat page in the actual load order; never trust a def value or a hand sum |
| **Room never pressurises** — stone, wood or obsidian walls (T-47) | the vacuum overlay, and pawns taking `VacuumExposure` indoors | replace the walls with `GravshipHull` or steel |
| **Crop dies** — breach puts the farm cell at vacuum ≥ 0.5; the plants take dying damage, not merely a growth stall | `MessagePlantDiedOfRot_ExposedToVacuum` per plant, but `Alert_LowOxygen` fires only once a *pawn* reaches `VacuumExposure` stage 2 — the plants die first | seal, **resow**, and absorb a full grow cycle. `VGE_SealantPopper` as prevention; two independently sealed farm rooms as insurance |
| **Orbital act runs dry** — 18 incidents (T-48) | none; the storyteller simply has nothing to pick | build (b) |
| **Quest never generates** — `Find.RandomSurfacePlayerHomeMap` null (T-49) | none | build (d), or avoid the two nodes |
| **Shield does not charge** — grav engine destroyed or unlinked | the generator's own inspect string | repair the engine |
| **Gravcore starvation** — the fit-out stalls | visible in the build menu as unaffordable | none; it is a pacing fact at one gravcore per 15–30 days, and nothing currently owns planning around it |

A campaign softlock is possible and worth naming: **abandon the planetside base, fly to orbit, and
the colony is inside the whitelist fence with no caravans and no map exit.** If the ship then loses
its engine, there is no way off the tile. The gravship is not merely the home; in orbit it is the
only exit.

## Status

**Evidence class: READ.** Verified against decompiled RimWorld 1.6.4871 (`Assembly-CSharp.dll`),
Odyssey/Core/DLC defs, decompiled `VanillaGravshipExpanded.dll`, and the raw patch XML of
`als.gravtech`, `als.biotechgravship`, `sbz.GravshipStorage` and `lts.mgw`.

- **Verified:** the cell budget and its enforcement; footprint geometry; airtightness rules; the
  vacuum and oxygen model; the food arithmetic's inputs; the shield and turret ladder; the orbit
  layer's incident filter; the `IsPlayerHome` consequences; every def value and patch operation
  feeding the ceiling table.
- **Inferred:** the worked deck plan and every number computed from it — 1,790, ≈1,510, the ≈3,850–
  4,500 composed ceiling, the ≈1,625 VGE-alone ceiling, the 300–500 day fit-out arc, and the claim
  that the four build pieces compose into a liveable ship.
- **Selected:** nothing. This is a verified available mechanism set and a priced build, not an
  implementation commitment.

Established by [#71](https://github.com/cjd721/Rimworld-Archinity/issues/71); its close-out audit
independently reproduced the geometry and food arithmetic to the cell, and the mod ceilings above
are the audited figures.

**One STUB attempt was inconclusive, and the root cause is now known.** `tools/xpath.py` reported
`GravEngine`'s `linkableFacilities` as the ten vanilla entries, showing neither VGE's seventeen
additions nor GravTech's seven. The cause is `tools/defdb.py`'s `_apply_leaf`, which evaluates a
patch xpath **relative to the `<Defs>` element** — so an ordinary `Defs/ThingDef[...]` matches
nothing while `report.patch_ops_applied` still increments, reporting success. That is
**[#102](https://github.com/cjd721/Rimworld-Archinity/issues/102)**. Consequences here:

- Every STUB-derived figure in this document is **provisional** until #102 is fixed and the merged
  tree is re-read. In practice the STUB tier settled nothing in this spec — the raw patch XML is the
  primary source throughout and is what is cited.
- The composed ceiling is the number most exposed to this: only a merged-tree read catches an
  un-patched engine, extender or reactor value (T-50).

## Available mechanisms

Everything cited above, in one place, with what it does not do. All rows **[V]**.

| Mechanism | Provides | Limitation |
|---|---|---|
| `Building_GravEngine` + `SubstructureSupport` | the cell budget and the flood fill that enforces it | not a placement check — overflow is silent (T-46); the number is only correct as composed (T-50) |
| `CompProperties_SubstructureFootprint` | where substructure may be laid | union of circles, and `GetConnectedSubstructure` uses `requireInsideFootprint: true`; vanilla radii 18.9 / 16.9, VGE radii 11.9 / 12.9 |
| `Verse.VacuumComponent` | per-room vacuum, 250-tick equalisation | inert outside `Biome.inVacuum` |
| `CompOxygenPusher` | repressurisation | `OxygenPump` needs `OrbitalTech`; wall attachment, zero floor |
| `VanillaGravshipExpanded.OxygenPipeNet` | oxygen as a real network with production, storage, canisters and packs | hard dependency on VEF's `PipeSystem.dll` |
| `GravcorePowerCell` | 1,200 W in one cell, no fuel, transmits power | one `Gravcore` each — the scarce resource |
| GravTech `GravFieldPylon` / `AdvShip_GravReactor` | the ceiling above 2,000 | **both** restatted under VGE — pylon 500 → 130, reactor 1,000 → 500 (T-50); 2 and 10 gravcores |
| `VGE_GravFieldAmplifier` | 3×3, +200 `SubstructureSupport`, up to 4 | 2 `Gravcore` each, `AdvancedGravtech` |
| `VGE_GravshipSubscaffold` | budget-exempt airtight floor | `affordances: [Walkable]` — nothing can be built on it |
| `HydroponicsBasin` / `VGE_Agrocell` | food on `fertility 0` decking | 55% duty cycle; plants *die* at vacuum ≥ 0.5 |
| `sbz_LongGravshipCrate` | 5×2, `maxItemsInCell 8` → 80 stacks | 2.7× a `Shelf`'s 3 stacks/cell, not the 5.3× a halved shelf count implies |
| `lts.mgw` compact benches | eight 2×1 / 3×1 gravship bench variants | hard VGE dependency; each `MayRequire`-gated on a different donor mod |
| `GravshipShieldGenerator` | 500 HP, radius 24.9, ground and air | 100 s up, 4 h charge, EMP-disarmed, dies with the engine |
| `VGE_PointDefenseTurret` | intercepts hostile drop pods | `VGE_GravshipWeaponry` |
| `GeneDef VacuumResistance_Total` | a pawn immune to vacuum | `biostatArc 1`, `displayCategory Archite` — needs archite capsules; required for the founders by `SPACE.md` (#127), delivery is #119's |

**What does not exist anywhere in the 155-mod corpus:** a warning before the substructure budget is
exceeded; a shield that holds continuously rather than in bursts; and any life-support mechanism
outside VGE. Vanilla Furniture Expanded's `VFEPD_ShipPart_LifeSupport` is `isInert: true` decoration.
The sweep behind that negative is recorded under *Verification*.

## Verification

### The wide pass behind the negative

Run over **both corpus roots** (`Data` and the workshop tree), `-a` with
`-g '*.dll' -g '!**/obj/**'`, ASCII **and** UTF-16LE-interleaved patterns, attributed through
`python tools/corpus.py --which -`:

| Pattern | Where | Mods carrying it |
|---|---|---|
| `SubstructureSupport` | XML | **3** — `vanillaexpanded.gravship` (8 files), `als.gravtech` (3), Odyssey (2) |
| `SubstructureSupport` | DLL | **2** |
| `GravshipFacility` | DLL | **4** — `als.gravtech`, `vanillaexpanded.gravship`, VEF, `rwmt.multiplayer` |

**The negative survives**: nothing outside VGE and GravTech touches the substructure budget or the
facility system, and build (c) has no donor. **[V]** on the sweep as run.

The UTF-16LE half of that pass is subject to
**[#103](https://github.com/cjd721/Rimworld-Archinity/issues/103)** — `rg --encoding utf-16le`
misses strings provably present in the `#US` heap, non-uniformly. This sweep used the
null-interleaved form, but any *narrower* re-run that reverts to `--encoding utf-16le` will not
reproduce it.

### Observable checks, for whoever builds this

1. **Budget.** Build 2,001 cells of substructure connected to the engine, Odyssey only. The engine's
   inspect string should read `ConnectedSubstructure: 2001 / 2000`; the substructure overlay should
   draw the excess in `GravshipUtility.DisconnectedSubstructureColor` (red). Launch, and confirm the
   outermost room is on the old map.
2. **Airtightness.** Build one sealed room of granite blocks and one of steel, both on substructure,
   both roofed, on an orbit tile. The granite room should never fall below vacuum 0.5.
3. **Farm.** One `HydroponicsBasin` of rice under a `SunLamp` at fertility 2.8 should harvest on a
   ~1.95-day cycle. If it is materially slower, the temperature factor is biting and the heating
   budget is wrong. Then breach the room: the plants should **die** and post
   `MessagePlantDiedOfRot_ExposedToVacuum`, not merely stall.
4. **Incidents.** With the only home map on an orbit tile, run the storyteller for a quadrum and
   record which `IncidentDef`s fire. The expectation is a set inside the 18 named on #71.
5. **Ceiling — the check this spec most needs.** Read `SubstructureSupport` off the engine's stat
   page in three load orders: Odyssey alone (**2,000**), VGE alone with six large thrusters
   (**≈1,625 — lower than vanilla**), and GravTech + VGE with all ten extenders, three pylons and a
   reactor (**≈3,850 with no thrusters, ≈4,500 with six**). Any published ceiling that has not been
   read this way is a def-value sum and is wrong (T-50). This is also the check
   [#102](https://github.com/cjd721/Rimworld-Archinity/issues/102) blocks doing offline.
6. **Extender geometry.** Place six extenders bunched in one room and confirm the buildable overlay
   cannot reach a 46 × 38 rectangle; spread them to the 18.9 ring and confirm it can.

## Outstanding decisions

| Question | Consequence | Owner |
|---|---|---|
| Which defs pass orbit's **four** gates — incidents, game conditions, factions-that-may-arrive, arrival modes — and whether the orbital act keeps the standing −5 cabin fever | decides whether the orbital act has a world, who can reach the ship, and the crew's baseline mood | Capability: § *Ordinary colony life on an orbital home*, Routes A–G and the four gates ([#147](https://github.com/cjd721/Rimworld-Archinity/issues/147)); requirement `docs/requirements/SPACE.md` § *Living in orbit*. Which defs pass: [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) |
| Cabin size — 3×4, 4×4 or shared | 22–40% of the whole deck budget, and a standing mood cost either way | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (playtest / balance; `SPACE.md` states no target) |
| How the founders' `VacuumResistance_Total` is delivered | commits to an archite-capsule supply line | Required by `docs/requirements/SPACE.md` § *The gravship as home* ([#127](https://github.com/cjd721/Rimworld-Archinity/issues/127)); how it is delivered is [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s |
| Whether one gravcore per 15–30 days is acceptable pacing | decides how long the fit-out arc runs, and whether GravTech's pylons, reactor and amplifiers are reachable at all | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (playtest / balance; `SPACE.md` states no target) |
| Which of GravTech / VGE / BfG / Gravship Storage / MGW ship | decides whether the ceiling is 2,000, ≈1,625, 4,500 or ≈3,850–4,500 — and VGE alone is *lower* than vanilla | [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) (open) |
| How the defense ladder maps onto pursuit intensity | this spec lists the rungs; nothing says when they are climbed | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (build map); `TRACE.md` owns the bands it would key on |
| Whether `tools/defdb.py` can be trusted to confirm any of the above offline | every STUB-tier figure in this spec is provisional until it can | [#102](https://github.com/cjd721/Rimworld-Archinity/issues/102) (open) |
