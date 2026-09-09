# Traps: buildings, items, rituals and titles

Content-side no-ops: comps that look like mechanisms, stats that are never read,
and gates that are invisible from the def.

Part of the trap register. **The index at `docs/TRAPS.md` is the file you read
before a diff**; this one carries the full entries for this group. Every entry here
fails with no error message. Cite by ID.

## Buildings, recipes and items

### T-23 — `statFactors` on a facility is a silent no-op

`CompProperties_Facility` has **`statOffsets` only**. There is no `statFactors`
field, and `CompAffectedByFacilities` overrides `GetStatOffset` but not
`GetStatFactor`, so a facility declaring `statFactors` does nothing at all.
Facilities are additive-only: express bench augments as offsets, or use
`RecipeDef.workTableSpeedStat` / `workTableEfficiencyStat`.

*`docs/engine/facilities-and-recipes.md`. 1.6.4871.*

### T-24 — `CompRefuelable` does not gate a `Building_PawnProcessor`

Adding `CompProperties_Refuelable` with a `HemogenPack` filter gives a real,
working fuel bar that gates nothing — VQE Ancients' code never reads
`CompRefuelable`. It looks like a mechanism and is decoration. Removing
`CompProperties_Power` instead is worse: `Building_PawnProcessor.PowerOn`
dereferences the power comp unguarded and NREs every tick.

Real gating requires a Harmony postfix on `Building_PawnProcessor.get_PowerOn`. The
capsule requirement is likewise not def-driven — `ThingDefOf.ArchiteCapsule` is
hardcoded in seven places.

*`docs/engine/mods/vqe-ancients.md`. 1.6.4871.*

### T-25 — Genepacks decay in 20 days and roofs do not help

`DeteriorationRate 5`/day against 100 max HP, no grace period, and
`deteriorateFromEnvironmentalEffects: false` — so roofs, rooms and shelves give
**zero** protection. Only a **powered** `GeneBank` stops it (research
`Xenogermination`, Industrial, cost 1000, itself gated behind Electricity, 40 W
constant); unpowered banks do not protect. Genepack rewards are viable from
Industrial onward, never before.

Do **not** patch `Genepack`'s `DeteriorationRate` to 0: genepacks are a single
ThingDef with dynamic contents, so it is all-or-nothing and would strip gene banks
of their entire purpose.

*`docs/engine/items-and-materials.md`. 1.6.4871.*

### T-26 — An unscoped `PatchOperationSetName` reaches the whole database

Medieval Overhaul's `component_replace` targets
`Defs/ThingDef/costList/ComponentIndustrial` with no scoping and hits **395
ThingDefs** across Core, all four DLC and 47 active mods — including `Ship_Beam`,
`Ship_SensorCluster`, `Ship_CryptosleepCasket`, Odyssey's `GravFieldExtender` and
`Apparel_Vacsuit`, every GravTech pylon and 24 `BfG_*` buildings. This is T-03 in
production, at scale.

It is also **half-broken**: the ingredient-side op targets
`Defs/RecipeDef/li/filter/thingDefs/li`, which matches **0** nodes (the correct path
matches 17), and its inner `PatchOperationReplace` has no xpath and would throw if
it fired. Read it as a whole-database rename when reasoning about anything
downstream of components. `chemfuel_replace` is structurally identical: 51 defs,
zero Spacer.

*`docs/engine/mods/medieval-overhaul.md`. MO 1.6.*

---

## Rituals and titles

### T-27 — `MeditationFocusDef` gates are backstory gates, and a failed gate looks like nothing

`Natural` — the anima tree's only focus type — requires a **Childhood** backstory in
category `Tribal`, `AdultTribal` or `ChildTribal`. A pawn without one is simply
never offered the linking ritual: no error, no message, no disabled button. The
founders' backstories are therefore load-bearing on the Neolithic psychic on-ramp.

Of the six vanilla focus types only three are ungated — `Morbid`, `Minimal` and
`Flame` — and `Morbid` is the altar's.

*[#21](https://github.com/cjd721/Rimworld-Archinity/issues/21). 1.6.4871.*

### T-28 — `RoyalTitleDef.Awardable` is believed to derive from `favorCost > 0`

**Corroborated, not verified at source.** No `awardable` field exists in any XML, so
it is a computed C# property and the repo carries no decompile of it — but exactly
seven `RoyalTitleDef`s carry a `favorCost`, and those are exactly the seven
player-attainable titles. A title with no favour cost would be invisible to every
vanilla award path, with nothing reporting why.

Our tiers of godhood are conferred by calling `SetTitle` directly from a ritual
outcome worker, which never consults `Awardable`. If the rule holds, a later attempt
to award one through a normal route silently does nothing — so do not add one.
Decompile `RoyalTitleDef` before relying on the negative.

*Corroboration only. 1.6.4871, indirect.*

---
