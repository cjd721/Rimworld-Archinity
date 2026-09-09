# Medieval Overhaul

How MO's settings reach both def-load and runtime, what its metal chain actually
does and does not remove, which of its buildings have electric successors, what
it locks behind iron, and the licence it does not ship.

Verified against Medieval Overhaul 1.6 on disk and decompiled RimWorld 1.6.4871.
These are *verified available mechanisms*, not commitments to use them —
selection happens in `docs/specs/`.

---

## Settings

### The settings menu can force a value you never clicked

MO forces `vanillaMine = true` from inside the Map-Gen tab's **draw method** when
`metalChain` is off, so two players clicking identical settings can produce
different files. Copy the settings file; never re-click it. Full entry:
`docs/TRAPS.md` T-19. For why settings files must be compared as parsed values
rather than bytes, see `docs/TRAPS.md` T-18.

### Settings reach runtime, not just def-load

21 files read `MedievalOverhaulSettings.settings` across **27 fields**.
`Plant_PlantCollected` calls `Rand.Chance(settings.soilWearChance)` on every
plowed-soil harvest, so a mismatch means clients draw a **different number of
values** from the shared stream and everything downstream diverges.

Worse, both schematic patches' `Prepare()` returns `!settings.biotechSchematic`,
and **`Prepare()` decides whether the Harmony patch is applied at all** — a
settings mismatch changes which code exists. That, and the unkeyed 250-tick
schematic cache it guards, are a live desync bug: `docs/TRAPS.md` T-20, which
also carries the no-assembly mitigation (strip the `RequiredSchematic` extension
from the 14 projects).

---

## The metal chain

### metalChain does not remove vanilla steel

It **prefixes** it. `DankPyon_MakeIngots_Steel` (IronIngot + Coal to vanilla
`Steel`, gated `DankPyon_Steel`, Medieval 2000) keeps steel fully craftable.

**`vanillaMine`, which defaults OFF, is what zeroes `MineableSteel` and
`MineableComponentsIndustrial` scatter** and relabels `Steel` to "steel ingot".
Its active branch is purely additive (adds 9 MO mineables to `PreciousLump`), so
turning it ON restores steel and component veins.

**Read the inactive branch, not the active one.** `metalChain` has no active
block at all: MO's base defs ship the chain unconditionally and the 23 inactive
ops dismantle it. The teardown also deletes `DankPyon_BlastFurnace`.

### component_replace hits 395 ThingDefs

MO's `component_replace` is an **unscoped** `PatchOperationSetName` on
`Defs/ThingDef/costList/ComponentIndustrial`, and it reaches the whole merged
database: 395 matches (320 inherited, 44 Industrial, 31 Spacer), including
`Ship_Beam`, `Ship_SensorCluster`, `Ship_CryptosleepCasket`, Odyssey's
`GravFieldExtender` and `Apparel_Vacsuit`, every GravTech pylon, and 24 `BfG_*`
biotech-gravship buildings. It is also half-broken, and `chemfuel_replace` is
structurally identical — `docs/TRAPS.md` T-26 has the detail.

---

## Buildings

### MO ships four electric successors

`Defs/ThingDefs_Buildings/Production/Buildings_Processors_Industrial.xml` holds
`BlastFurnace` (500 W), `TanningDrum` (250 W), `ClothSpinner` (250 W) and
`SawTable` (250 W), all gated on `Electricity`. So every one of the four
resource chains has a verified Electricity-tier successor.

### Nothing in MO is ever hidden

`grep menuHidden` across all of MO 1.6 returns **zero hits**. The `*Spot` family
is retired purely by a flat `WorkTableWorkSpeedFactor 0.5` plus
`PlaceWorker_ReportWorkSpeedPenalties`. Economic, not mechanical: **the build
menu never gets shorter.**

---

## Items

### Iron-locked items

`DankPyon_Crossbow`, `DankPyon_CrossbowHeavy` and `DankPyon_Handgonne` require
`DankPyon_IronIngot`, producible only from `DankPyon_IronOre`. **There is no
Steel to ingot path.** `VFEM2_Arbalest` and `VFEM2_Gun_HandCannon` / `Arquebus`
cover the same slots in Steel.

MO also moves `Bow_Recurve` and `Bow_Great` off `CraftingSpot` onto
`DankPyon_Workbench`, removing the early bow path.

`VFEC_Bronze` is **not** a new mineable. It is crafted from 10 Steel plus stone
chunks and consumed only by `VFEC_BronzeTile` — a steel extender, not a
resource.

---

## Sieges

MO ships a medieval siege that cannot fire: `DankPyon_MedievalSiege` requires a
combination of gates no shipped faction satisfies. See `docs/TRAPS.md` T-31. The
def-level constructs it uses are still patchable onto other factions —
`docs/engine/mods/kcsg.md` covers that under enemy siege against the player.

---

## Licensing

MO ships **no license**. No LICENSE, COPYING or TERMS file in the mod;
`About.xml` says only "Pretty dank mod"; `gh api
repos/ViralReaction/MedievalOverhaul` returns `"license": null` with no LICENSE
in the repo root. No license means all rights reserved.

This only matters if MO content is **copied** into this repo (Route B). Enabling
MO as a normal mod and referencing its defNames distributes nothing, which is
what every compat patch on the Workshop does.
