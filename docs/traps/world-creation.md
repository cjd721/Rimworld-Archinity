# Traps: world creation and factions

The roster, the world-creation page, and faction mutation. T-07 is the one that
cannot be repaired without a new world. Mechanisms in
`docs/engine/factions-and-worldgen.md`.

Part of the trap register. **The index at `docs/TRAPS.md` is the file you read
before a diff**; this one carries the full entries for this group. Every entry here
fails with no error message. Cite by ID.

## World creation and factions

### T-07 — The faction roster must be final BEFORE world creation

**The most consequential silent failure in the project.** Adding a `FactionDef` to
an already-generated world does nothing: no error, no warning, no log line — the
faction simply is not in the world and never will be.
`FactionManager.ExposeData` has no reconcile path, scribing the faction list it was
saved with and never re-reading `DefDatabase` for defs that appeared since.

For one long co-op run this is a **one-time hard gate**. A roster mistake is not a
patch, it is a new world. `FactionGenerator.CreateFactionAndAddToManager(layer, def)`
is public static and is a repair, not a plan.

*[#18](https://github.com/cjd721/Rimworld-Archinity/issues/18),
[#8](https://github.com/cjd721/Rimworld-Archinity/issues/8). 1.6.4566.*

### T-08 — `maxCountAtGameStart` and `canMakeRandomly` are `[Obsolete]` no-ops

Both are read nowhere in 1.6 (`FactionDef.cs:239-243`). No Core or DLC def sets
either; **six mods in the bin still do**, writing to no-ops with no warning. A
faction you believe you have excluded stays out — or comes in — by accident. The
live replacements are `maxConfigurableAtWorldCreation` and
`startingCountAtWorldCreation`; treat any def relying on the obsolete pair as
unauthored.

*`FactionDef.cs:239-243`. `VFET_WildMen` is the worked case —
`docs/engine/factions-and-worldgen.md`. 1.6.4566.*

### T-09 — `requiredCountAtGameStart` is dead code in 1.6

`FactionGenerator.InitializeFactions(layer, factions)` early-returns when
`factions != null`, and `WorldGenStep_Factions.GenerateFresh` always passes
`Current.CreatingWorld.info.factions`, which
`Page_CreateWorldParams.ResetFactionCounts()` always builds non-null. The only
null-passing caller is the dev quickstart. The real levers are
`maxConfigurableAtWorldCreation` (0 means it can never spawn),
`startingCountAtWorldCreation` and `displayInFactionSelection`.

*`FactionGenerator.InitializeFactions`, `WorldGenStep_Factions`. 1.6.4566.*

### T-10 — The `replacesFaction` prune runs over defs you excluded

`Page_CreateWorldParams.cs:81-87` runs the prune over **every** configurable def,
including ones at `startingCountAtWorldCreation: 0` that never entered the list — so
a def you excluded can still delete a def you kept. When authoring the roster by
patch, check the `replacesFaction` of the defs you zeroed out, not only the ones you
kept.

*`Page_CreateWorldParams.cs:81-87`. 1.6.4566.*

### T-11 — Writing `FactionDef.techLevel` at runtime silently reverts

Defs are not scribed, so the value is gone next session with no error and no log
line. Three further consequences: it changes only the tech level (pawn kinds,
traders and KCSG layouts are unaffected); a `FactionDef` is a **shared object**, so
it changes every faction instance using that def; and World Tech Level does exactly
this in production (`Patch_BaseGen.cs`, prefix + `[HarmonyFinalizer]`), clobbering
any write made during a BaseGen pass. Do not persist state on a def — climb a
faction by swapping `Faction.def` instead.

*`docs/engine/factions-and-worldgen.md` for what leaks when you swap. 1.6.4566.*

### T-12 — `Settlement.cachedMat` is never invalidated

`Settlement.cs:20,68-78` caches material and colour from the def on first draw. The
field is **never nulled anywhere in the assembly** and is not scribed, so a
settlement whose faction changed keeps drawing the old faction's texture and colour
indefinitely. Null it by reflection inside the same synced command that swaps the
def.

*`Settlement.cs:20,68-78`. 1.6.4566.*

### T-13 — `FactionUtility.DefaultFactionFrom` returns null once a faction climbs

It resolves `AllFactions.Where(x => x.def == ft)`, falls back to `replacesFaction`,
and otherwise returns **null** with no fallback — quietly orphaning any
`PawnKindDef.defaultFactionDef` that pointed at the old tier. Set `replacesFaction`
on each higher tier pointing down the chain.

*1.6.4566.*

### T-14 — VFE Empire's deserter strategy blacklists every other raid strategy

A `[StaticConstructorOnStartup]` in `VFEEmpire.RaidStrategyWorker_Deserters` sets
`disallowedRaidStrategies = AllDefs.Except(VFEE_DefOf.DesertersStrat)` — no filter,
one exclusion — so **any `RaidStrategyDef` we author is silently excluded from the
`VFEE_Deserters` faction**. The field is a **vanilla `FactionDef` field** (`FactionDef.cs:178`),
consumed at `RaidStrategyWorker.cs:54`, not a VFE extension.

Two escapes: a custom `workerClass` whose `CanUseWith` does not chain to base
ignores the list entirely; and `IncidentWorker_RaidEnemy.ResolveRaidStrategy`
(`:94`) only filters when `parms.raidStrategy == null`, so a pre-set strategy
bypasses it.

*VFE **Empire** (`2938820380`) — not VFE Deserters, where this was first
mis-recorded. 1.6.4566.*

### T-15 — `VFET_OpportunitySite_WildMen` generates a faction at runtime

`VFETribals.QuestNode_Root_WildMen` (`:60-64`) builds
`FactionGeneratorParms(VFET_WildMenGroup, default, hidden: true)`, calls
`NewGeneratedFactionWithRelations`, sets `temporary = true` and calls
`Find.FactionManager.Add`, with relations computed from `AllFactionsListForReading`
at that moment (`:39-58`). **There is no reuse guard** — `FirstFactionOfDef` appears
nowhere in the assembly, so it can fire more than once. The generated faction is
**Hostile** to the player (`kind = 0`).

It fires only for a Neolithic player (`:149`), which is precisely our Neolithic. A
frozen roster (T-07) cannot survive it: block the quest, or accept the roster is not
frozen.

*`VFETribals.QuestNode_Root_WildMen:39-64, 149`. 1.6.4566.*

### T-16 — `RaidStrategyDef` and `QuestScriptDef` have no `minTechLevel` field

Verified against the full field lists — every tech gate in either is worker code, so
a tech gate written in XML never fires and there is nothing to validate against.
`QuestScriptDef`'s available gates are `rootMinPoints`, `rootMinProgressScore`,
`rootEarliestDay`, `rootSelectionWeight`, `isRootSpecial` and `randomlySelectable`.
Note `rootMinProgressScore` is **not** a tech gate either.

*`docs/engine/research-and-tech-tiers.md` for what it actually computes. 1.6.4566.*

### T-17 — Raid faction selection is fail-open and fail-quiet

`GetRandomEligibleFaction()` returns null with no fallback when the pool empties, so
raids simply stop firing. Ignorance Is Bliss gates via a postfix on
`FactionCanBeGroupSource`, and with `changeQuests=true` that postfix has **no
`else`** — so an out-of-tech faction is not replaced, it is allowed. Never let the
eligible pool empty; check it whenever the roster or a tech gate changes.

*`IncidentWorker_Raid`; IIB `IgnoranceBase`. 1.6.4871.*

---
