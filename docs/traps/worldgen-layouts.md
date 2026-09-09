# Traps: worldgen layouts

KCSG structure and settlement authoring, and the shipped siege that never fires.
Mechanisms in `docs/engine/mods/kcsg.md`.

Part of the trap register. **The index at `docs/TRAPS.md` is the file you read
before a diff**; this one carries the full entries for this group. Every entry here
fails with no error message. Cite by ID.

## Worldgen layouts

### T-29 — Layout rows and cells beyond `layouts[0]` are dropped silently

A `StructureLayoutDef`'s size derives from `layouts[0]`; rows and cells beyond that
are dropped with no message, so part of a hand-authored structure does not spawn.
Size every layer to the first layer, and re-export rather than hand-editing a grid's
width.

*`docs/engine/mods/kcsg.md`. 1.6.4871.*

### T-30 — `defenseOptions` is dead below Industrial

`SymbolResolver_EdgeDefenseCustomizable` gates `addTurrets` and `addMortars` on
`faction.def.techLevel >= Industrial` (4); Medieval is 3. Only `addSandbags` and
`pawnGroupMultiplier` take effect below Industrial — siege engines have to live
inside the layout grid instead.

*1.6.4871.*

### T-31 — `DankPyon_MedievalSiege` cannot fire as shipped

Its worker requires `RaidStrategyWorker_Siege.CanUseWith` (i.e.
`FactionDef.canSiege`) **and** a `MedievalOverhaul.FactionSiegeExtension` with
`medievalSiege: true` **and** `techLevel == Medieval`. The extension is on
`DankPyon_BrigandFactionBase` and `DankPyon_NobleHouseFactionBase`; **neither sets
`canSiege`**, which has **zero hits across all of Medieval Overhaul** (1.4/1.5/1.6,
defs, patches and assembly). Core `FactionBase` does not set it and the field
defaults `false`. Empty intersection — a shipped raid strategy that never occurs and
never explains itself. No VFEM2 faction sets `canSiege` either.

Fixing it is not a one-liner: `canSiege` must go onto **both** abstract defs, and
`RaidStrategyWorker.CanUseWith` adds further gates — the def's curve is
`(500,0) → (1000,1.6)`, so it needs **>500 threat points**, plus the Surface layer
and no blocking tile mutator. That makes it *possible*, not frequent.

What it would buy: the def already ships `LordJob_MedievalSiege` with its own supply
generation and **trebuchets** — `DankPyon_Turret_Trebuchet` is the only holder of
`ArtilleryMedieval_BaseDestroyer`. *(MO's own arrival text says "catapults"; that is
flavour copy, not the def.)*

*`docs/engine/mods/medieval-overhaul.md`. MO 1.6.*

### T-32 — Rotated KCSG symbol variants are not defs and cannot be patched

`_North` / `_East` / `_South` / `_West` variants are generated at runtime by
`HotGenerateRotationSymbols` and never enter the def database, so a patch targeting
one matches nothing. Patch the base symbol. Related:
`StartupActions.CreateSymbols` auto-generates symbols **only** for Core, DLC, VFE
Props and Decor — every other modded ThingDef needs a hand-written SymbolDef.

*Same shape as the `USH_GlittershipChunk_North` finding. 1.6.4871.*
