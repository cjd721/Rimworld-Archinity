# Gravship

## Purpose and scope

How the gravship becomes the colony's permanent home — the deck budget, life support, food,
defenses, and what changes when the planetside base is retired. The fiction is
[`docs/plot/SPACER.md`](../plot/SPACER.md) § *Departure — The Gravship Becomes Home*: *"reliable
oxygen, gravity, food production, cooking, habitation, storage, defenses, shields and enough
capacity that the colony can permanently leave the electrified castle behind."*

This document owns **whether that is possible and at what cost**, and the deck budget every other
gravship decision is spent against.

It does not own: the Ultra pursuit that the defenses answer to
([#56](https://github.com/cjd721/Rimworld-Archinity/issues/56)); which mods ship
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

### (b) Orbit incident whitelist — XML

**This is the largest content consequence of the ship becoming home, and it is not about the ship.**
The Orbit layer sets `onlyAllowWhitelistedIncidents`, and across the merged vanilla + DLC database
that leaves **18 of 91 `IncidentDef`s and 18 of 139 `QuestScriptDef`s** able to fire. **[V]** A
campaign act played from an orbital home loses wanderers, refugees, visitors, manhunter packs,
infestations, solar flares, toxic fallout and every walk-in social event — silently. See *Living on
the orbit layer*, below, and T-48.

`PatchOperationAdd` of `<layerWhitelist><li>Orbit</li></layerWhitelist>` onto each def the campaign
wants alive. **~80 lines** **[I]**, one `<li>` per def, in a new `Patches/Orbit_Incidents.xml`. The
list of *which* incidents belong in Ultra is a requirements question with no owner — see
*Outstanding decisions*.

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
`QuestNode_GetSiteTile`, `QuestNode_Root_WandererJoin` and `QuestPart_SpawnMonolith` return null
once the only home is in orbit (T-49). **[V]** A Harmony postfix returning
`Current.Game.RandomSurfacePlayerHomeMap` is **~8 lines** **[I]**. Needed only if Archinity content
uses those three nodes; otherwise avoid them and skip the patch.

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
| Orbit incident whitelist | XML patch | ~80 lines | `Patches/Orbit_Incidents.xml` |

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

**Re-derived: 1,790 − (160 + 62 + 40 + 16) = 1,512, call it ≈ 1,510 cells.** **[I]** The earlier
≈1,480 figure rested on a halved `Shelf` capacity and a crate saving inflated with it; it is
withdrawn.

And the ceiling itself moves — **in both directions**:

| Configuration | Ceiling | Composition |
|---|---|---|
| Odyssey alone | **2,000** | 500 + 6 × 250, no multiplier |
| + `als.gravtech`, VGE absent | **4,500** | + 3 × `GravFieldPylon` (1×1, 500 each) + `AdvShip_GravReactor` (5×5, 1,000, −150,000 W) |
| **VGE alone** | **≈ 1,625** | offsets 250 + 10 × 100 = 1,250, × 1.30 (six `LargeThruster` at +0.05 each). **Below Odyssey alone, and below the un-modded 1,790-cell deck** |
| + `als.gravtech` **and** VGE | **≈ 3,850 – 4,500** | offsets 250 + 10 × 100 + 3 × 130 + 500 = **2,140**, × 1.80 (no thrusters) to × 2.10 (six `LargeThruster`) |
| the deck as drawn, GravTech + VGE, six extenders only | **3,132** | offsets 250 + 6 × 100 + 3 × 130 + 500 = 1,740, × 1.80 |

The published **~6,100** figure is withdrawn. It summed offsets of 3,390 from four inputs of which
**three were un-patched def values** — a 500 engine that is 250, a 250 extender that is 100, and a
1,000 reactor that is 500 — and then applied a multiplier that omitted the thruster term entirely.
That is precisely the error T-50 exists to name, made in the document that cites it.

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
on the subscaffold exemption, and the spec's earlier framing — that VGE only ever raises the
ceiling — was backwards.

**The binding constraint is not cells. It is `Gravcore`.** Six extenders, a signal jammer and twelve
power cells cost **19** **[V]**, and gravcores are not generically sellable — they arrive from
`QuestPart_SubquestGenerator_Gravcores` at a minimum of one per **15–30 days**
(`MinTimeBetweenSubquests` 900,000 ticks, `MaxTime` 1,800,000, one gravcore per site). **[V]**
Fitting out the ship is therefore a **300–500 day** arc **[I]** whether or not the player hurries,
and GravTech's pylons and reactor add ten more gravcores on top, amplifiers eight more again.
`docs/progression/` was to own whether that pacing is acceptable; it is empty. This spec records
that the constraint exists and that no amount of cell efficiency changes it.

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
  The *code* cost is zero; the *delivery* cost is an archite-capsule supply line, and that is a
  campaign decision. **[#10](https://github.com/cjd721/Rimworld-Archinity/issues/10) is closed**, so
  no live ticket owns whether the founders get this gene. It is a gap — see *Outstanding decisions*.
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

Not the pursuit — [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56) owns that. This is
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
machinery.** (An earlier draft quoted a count of vanilla *source files* reading the flag. That is
not reproducible against a shipped single assembly and is withdrawn; the named consumers above are
the reproducible claim.)

Five things do change, and four of them are the *layer*, not the flag. All **[V]**.

1. **No walking off the map.** `ExitMapGrid.MapUsesExitGridNow` is false for home maps, pocket maps
   and `Biome.inVacuum`; `BiomeDef Space` also sets `canExitMap false`.
2. **No caravans in orbit at all** — `PlanetLayerDef Orbit` sets `canFormCaravans: false`. Caravan
   trade, caravan quests and caravan rescue arms all go.
3. **The incident pool collapses to 18 of 91**, and quests to 18 of 139 (T-48). This is the one that
   needs a patch pack, and it is build (b).
4. **`Find.RandomSurfacePlayerHomeMap` returns null** once the only home is off the root surface
   (T-49), taking `QuestNode_GetSiteTile`, `QuestNode_Root_WandererJoin` and
   `QuestPart_SpawnMonolith` with it.
5. **An orbital home is not a `Settlement`.** `GravshipUtility.ArriveNewMap` only calls
   `SettleUtility.AddNewHome` where the layer's `DefaultWorldObject == SettlementWorldObjectDef`;
   `Orbit` has `Space` and `SpaceSettlement`. So the orbital home does not count against
   `Prefs.MaxNumberOfPlayerSettlements`. Landing on an empty *surface* tile does create a Settlement
   and does count.

The shrine `MapParent` pattern still stands, and the gravship still flips it into a player home if
it lands there — but only on a **surface** tile. A shrine on an orbit tile is already inside the
whitelist fence, which is a different and stronger reason nothing can raid it. (This finding was
written for #10, which is now closed; it is recorded here because nothing else carries it.)

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
| **Quest never generates** — `Find.RandomSurfacePlayerHomeMap` null (T-49) | none | build (d), or avoid the three nodes |
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

Established by [#71](https://github.com/cjd721/Rimworld-Archinity/issues/71) and corrected by its
close-out audit, which independently reproduced the geometry and food arithmetic to the cell and
found the two published mod-ceiling numbers wrong.

**One STUB attempt was inconclusive, and the root cause is now known.** `tools/xpath.py` reported
`GravEngine`'s `linkableFacilities` as the ten vanilla entries, showing neither VGE's seventeen
additions nor GravTech's seven. The cause is `tools/defdb.py`'s `_apply_leaf`, which evaluates a
patch xpath **relative to the `<Defs>` element** — so an ordinary `Defs/ThingDef[...]` matches
nothing while `report.patch_ops_applied` still increments, reporting success. That is
**[#102](https://github.com/cjd721/Rimworld-Archinity/issues/102)**. Consequences here:

- Every STUB-derived figure in this document is **provisional** until #102 is fixed and the merged
  tree is re-read. In practice the STUB tier settled nothing in this spec — the raw patch XML is the
  primary source throughout and is what is cited.
- Filing the gap as a tooling item rather than a verdict was procedurally right, but it buried it:
  **the one thing the STUB could not settle is exactly the number that was published wrong** — the
  composed ceiling. A merged-tree read would have caught the un-patched engine, extender and
  reactor values immediately.

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
| `GeneDef VacuumResistance_Total` | a pawn immune to vacuum | `biostatArc 1`, `displayCategory Archite` — needs archite capsules, and no live ticket owns the decision |

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
| Which incidents and quests are whitelisted for orbit | decides whether the orbital act has a world | **No owner.** A requirements question with no ticket; the patch is build (b). This is a gap, not a hand-off |
| Cabin size — 3×4, 4×4 or shared | 22–40% of the whole deck budget, and a standing mood cost either way | **No owner.** A requirements question with no ticket |
| Whether the founders get `VacuumResistance_Total` | decides whether hull work needs suits, and commits to an archite-capsule supply line | **No live owner** — [#10](https://github.com/cjd721/Rimworld-Archinity/issues/10) is closed |
| Whether one gravcore per 15–30 days is acceptable pacing | decides how long the fit-out arc runs, and whether GravTech's pylons, reactor and amplifiers are reachable at all | nominally `docs/progression/`, **which is empty**. No document and no ticket owns it today |
| Which of GravTech / VGE / BfG / Gravship Storage / MGW ship | decides whether the ceiling is 2,000, ≈1,625, 4,500 or ≈3,850–4,500 — and VGE alone is *lower* than vanilla | [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) (open) |
| How the defense ladder maps onto pursuit intensity | this spec lists the rungs; nothing says when they are climbed | [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56) (open) |
| Whether `tools/defdb.py` can be trusted to confirm any of the above offline | every STUB-tier figure in this spec is provisional until it can | [#102](https://github.com/cjd721/Rimworld-Archinity/issues/102) (open) |
