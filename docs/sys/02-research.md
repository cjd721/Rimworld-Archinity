# 02 — Research tree

**Blocked by 01.** TechBlock reads `techLevel` off every project at startup, and More
Realistic Research auto-generates gates off `techLevel`. Both need the final def database.

## What this system must do

Hand-place every research project through Neolithic and Medieval so progression is
authored rather than inherited. Gate advancement so eras arrive in order. Attach item
requirements so specific research demands specific things the player must go get.

## The design, from `Player Progression Ideology.txt`

Three ideas carry everything:

1. **Research grants capability, not just recipes.** The Neolithic projects that unlock
   *jobs and gizmos* — agriculture granting the grow job, the grow designators and the base
   plants — are the model. This is `TribalResearchProjectDef.unlocksWorkTypes` /
   `unlocksWorkTags` / `unlocksDesignators`.
2. **Tier the same capability rather than adding parallel ones.** Basic → intermediate →
   advanced agriculture, each widening the plant set. Not forty plants at once.
3. **Two classes of research, gated differently.**
   - **Spine** — the things you must have to play. Resource costs and ordinary item
     requirements. Hunt items **by exception**, not by default.
   - **Quality-of-life** — the scarecrow, the mine shaft, the crane. Rare, high-value, does
     *not* gate progression. **The default home for hunt-item requirements.**

   The Ideology is explicit that gating core weaponry behind a questline is wrong, and that
   the bellows-class augment is the right target. But some *major* unlocks should sit behind
   a hunt — just not most of them. Treat this as a ratio to tune, not a rule to enforce.

### Vocabulary — keep these separate

These get conflated and they are different asks:

- **Ordinary item requirement** — a specific ThingDef you can farm, craft, trade for or
  loot in normal play. Cheap to satisfy, mostly a pacing device. Fine anywhere, spine
  research included.
- **Hunt item** — hand-placed, not obtainable through ordinary play, you have to go get it.
  Expensive in player time. Default home is QoL research; allowed on spine research when a
  specific unlock deserves the weight.

Both are authored with the same Research Mod fields. The difference is entirely in whether
the item is reachable without going looking for it.

## The mechanics — all verified

### Tribal → bench research handoff: automatic, no work

There is no research-mode flag. Gathering is the only early path because:
- the `Intellectual` work tag is disabled until `VFET_Culture` completes (`unlocksWorkTags`), and
- `SimpleResearchBench` is patched behind `ComplexFurniture`.

After `VFET_Culture`, `Utils.IsUnlocked()` returns true forever. Separately
`Precept_Ritual_ShouldShowGizmo_Patch` **hard-hides the gathering ritual** once faction
techLevel passes Neolithic.

**Author Medieval+ projects as ordinary `ResearchProjectDef` and they are bench-only.**
Conrad's stated wish is the mod's default behaviour.

Gathering eligibility is hardcoded in C# to `techLevel == Animal || Neolithic`.

### Cornerstones for the whole game: free

`GameComponent_Tribals.GameComponentTick()` polls `Faction.OfPlayer.def.techLevel` and calls
`OffsetAvailableCornerstonePoints()` on **any increase from any source**. TechBlock writes
faction techLevel on tier-up. **They already connect.**

Add `EraAdvancementDef` entries (`newTechLevel`, `cornerstonePoint`) in XML. Archotech is
currently missing one.

### TechBlock

`TB_<Era>TechLock` / `TB_<Era>Theory` pairs. `TechBlocker.BlockTechs()` runs at
`[StaticConstructorOnStartup]`, iterates **every** `ResearchProjectDef`, injects the matching
Theory as a prerequisite if none at the same techLevel exists. It reads
`ResearchProjectDef.techLevel`, not a curated list. No Harmony patches — def mutation plus
polling.

Lock cost = `sum(baseCost of tier) × requiredPoints`. Settings names are **offset one tier**
from the def names — a persistent source of confusion.

### More Realistic Research — the item-gating backbone

`sae.ResearchMod`, workshop `3771646847`. **This is not "MRR"; that mod is not installed and
every doc reference to it is wrong.**

```xml
<ResearchMakesSense.ManualAnalysisDef>
  <defName>Lights</defName>
  <researchProject>ColoredLights</researchProject>
  <experimentalMaterials><li>Steel</li></experimentalMaterials>
  <experimentalPointsRequired>5</experimentalPointsRequired>
  <reverseEngineeringMaterials><li>Gloomlight</li></reverseEngineeringMaterials>
  <reverseEngineeringPointsRequired>6</reverseEngineeringPointsRequired>
  <theoreticalMaterials><li>ComponentIndustrial</li></theoreticalMaterials>
  <theoreticalPointsRequired>10</theoreticalPointsRequired>
</ResearchMakesSense.ManualAnalysisDef>
```

A pawn studies the item **where it lies** — no stockpile needed, just reachable on-map.
One completed study = one point.

| Type | Effect on item | Use it for |
|---|---|---|
| `Experimental` | destroyed, 1 per point | ordinary materials you farm |
| `ReverseEngineering` | damaged 5–50% max HP, not consumed | **the quest/raid trophy** — survives, so one item can gate one research |
| `Theoretical` | untouched | flavour requirements that shouldn't cost anything |

`reverseEngineering` is the right slot for quest-obtained items: the player keeps the trophy.

**No field can require a building on the map, a research bench, or a facility.**
For that use vanilla `requiredResearchBuilding` (exact `bench.def` equality) and
`requiredResearchFacilities` (must be linked **and** active). Both gate on a
`Building_ResearchBench` only — they cannot gate on a forge or a tailor bench.

## Traps

1. **Unlisted projects get auto-generated requirements by techLevel.** Every Archinity
   project silently acquires gates we did not author. **Declare an empty `ManualAnalysisDef`
   for anything that should be ungated.** Near-certainly the cause of the 36 recorded
   deadlocks.
2. ~~VFET × TechBlock premature advancement.~~ **Resolved — disable VFET's advancement
   ritual outright.** TechBlock is the sole advancement lever. The conflict was that VFET's
   `RitualObligationTargetWorker_AnyGatherSpotForAdvancement` fires when *no* project at the
   current techLevel is `CanStartNow`, and TechBlock's injected prerequisites make projects
   not-startable, so the ritual could unlock early. Removing the ritual removes the conflict.
   **Cornerstones are unaffected** — they key off any faction techLevel increase, which
   TechBlock writes on tier-up.
3. **Deleting a `ResearchProjectDef` strips the prerequisite off its dependants**, leaving
   them buildable with no research at all. Neuter referencing defs first, delete last.
4. `rootMinProgressScore` ignores research entirely —
   `progressScore = freeColonists + wealth×0.0001`. Do not use it to pace anything.
5. `BuildForProject` in More Realistic Research returns null for `techLevel <= Neolithic`
   and for Archotech. `Devilstrand` is a circular Neolithic deadlock.
6. TechBlock `randomInsights` — **disable the feature entirely.** Frame-based `Rand` is an
   MP desync, and separately Conrad does not want RNG research progress in the game at all.

## Work items

- [ ] Disable `randomInsights` and VFET's advancement ritual (both in `sys/01` — do once).
- [ ] Audit every project More Realistic Research auto-gated; declare empty
      `ManualAnalysisDef`s where we want no gate. Resolve the 36 deadlocks — prioritise the
      vanilla ship chain, GravTech, `VGE_GravshipPower`, `HeatDissipation`, `AstrofuelRefining`.
- [ ] Author the Neolithic tree: which projects exist, what each unlocks, cost, order.
      Tier agriculture basic→intermediate→advanced. Pare the plant set hard (`sys/04`).
- [ ] Author the Medieval tree against the approved three-leap structure
      (Forge ~5,100 / Mail+Siege ~12,400 / Plate+Powder ~13,400).
- [ ] Add `EraAdvancementDef` entries incl. the missing Archotech one.
- [ ] Decide the VFET × TechBlock premature-ritual behaviour.
- [ ] Rule on `requiredPointsMedieval` 0.75 (~88 bench days) vs 1.0 (~117).
- [ ] Fill the research holes: `VFEM2_Apparel_PaddedArmor` (no gate at all), MO heraldic
      greathelm/hauberk variants, MO's 4 heater shields (no recipe, no research).
- [ ] Retier the known-wrong placements: `VFES_SiegeEquipment` behind `DankPyon_Engineering`;
      `VFEC_Scorpion` out of the Neolithic; split `PlateArmor`'s two armour rungs;
      `VFE_Res_Sprinkler` off `Machining` into Medieval. Consider `HeavyBridges` (800) and
      `Piano` (2000) to Medieval.
- [ ] Decide whether VFE Classical's five stranded 1,200-pt projects (6,000 points buying
      nothing behind a Medieval `FueledSmithy`) are retiered or cut.
- [ ] Teach `audit_research.py` to apply Replace/Add/Remove on `ResearchProjectDef` — its
      tier totals currently lag every retier we ship.
- [ ] Rule on Nice Research Tab: is the objection node-graphs generally, or this mod's output?
