# Gravship and substructure

What substructure affords, what will and will not fly on it, and how the launch
budget is actually counted.

Verified against decompiled RimWorld 1.6.4871 unless an entry says otherwise.
These are *verified available mechanisms*, not commitments to use them —
selection happens in `docs/specs/`.

---

## Substructure affordances

`Substructure` is `ParentName="FloorBase"` and `XmlInheritance` appends (see
`docs/TRAPS.md` T-05), so its resolved affordances are
`[Light, Medium, Heavy, Walkable, Substructure]`. `GridsUtility.GetAffordances`
returns the **foundation** list, overriding any floor laid on top.

## What flies and what does not

- `Heavy` buildings fly fine. **`Diggable` and `SmoothableStone` do not**, so
  `DiggingSpot` and `MiningSpot` are unbuildable on substructure. Same reason
  graves cannot fly.
- `MedievalOverhaul.PlaceWorker_WaterWheel.AllowsPlacing` has an explicit
  `WaterCellsPresent` check, so the water mill is impossible on a gravship.
- `GardeningBox` works (`Light` affordance, own `fertility 0.8` via the edifice
  branch). `Post` does not; its `DankPyon_GrowSoilVine` affordance is never
  patched onto `Substructure`.

## The launch budget

- **Budget is cells, not mass.** `MaxLaunchWeight` does not exist. `GravEngine`
  gives `SubstructureSupport 500`; up to 6 `GravFieldExtender` add 250 each, so
  **2000 cells**.

See also `docs/engine/mods/medieval-overhaul.md` for the Medieval Overhaul
buildings named above.
