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

### T-36 — Swapping `Faction.def` freezes the title ladder

T-11 says climb a faction by swapping `Faction.def`, and
`docs/engine/factions-and-worldgen.md` § *Climbing a faction by swapping
`Faction.def`* → *What breaks, and the fix* is the canonical list of what leaks when
you do. This is that list's royalty row, and it is the quietest one.

`Pawn_RoyaltyTracker` keys `titles`, `favor` and `factionPermits` by **`Faction`
instance**, so held titles survive the swap intact. Every question *about* the ladder
is then answered from the new `Faction.def`:

- `FactionDef.RoyalTitlesAwardableInSeniorityOrderForReading` filters
  `item.Awardable && item.tags.SharesElementWith(royalTitleTags)`. If the new tier's
  def does not declare the same `royalTitleTags`, the held title is not in the list,
  `RoyalTitleDefExt.GetNextTitle` gets `IndexOf(currentTitle) == -1` and returns
  null, and `Pawn_RoyaltyTracker.CanUpdateTitle` is false **forever**. Favour keeps
  accruing and buys nothing; the character card prints the pawn's title as final.
- `GetPermitPoints` walks the ladder down through
  `GetPreviousTitle_IncludeNonRewardable`, which also resolves by `IndexOf` and so
  returns null on the first step. The award total collapses to the current rung's own
  `permitPointsAwarded` while `permitPointCost` for permits **already bought** is
  still subtracted, so the balance can go negative.
- `royalFavorLabel` and `royalFavorIconPath` (through `FactionDef.RoyalFavorIcon`)
  are read off `Faction.def` at every use site — the character card, the permits tab,
  the trade window, the quest reward stack. Losing `royalFavorLabel` degrades
  harmlessly but invisibly: `GenText.CapitalizeFirst` is null-tolerant, so the
  tooltip prints a blank word rather than throwing.
- `categoryTag` is what techprint acquisition matches on
  (`ResearchProjectDef.heldByFactionCategoryTags` against `faction.def.categoryTag`),
  so losing it removes a research path with nothing logged.

Nothing anywhere reports the mismatch. **Every tier def of a faction that confers
titles must carry identical `royalTitleTags`, `royalFavorLabel`, `royalFavorIconPath`
and `categoryTag`** — the ladder is a property of the def, not of the faction.

*`FactionDef.RoyalTitlesAwardableInSeniorityOrderForReading`,
`RoyalTitleDefExt.GetNextTitle`, `Pawn_RoyaltyTracker.CanUpdateTitle`,
`Pawn_RoyaltyTracker.GetPermitPoints`. Leak table in
`docs/engine/factions-and-worldgen.md`.
[#53](https://github.com/cjd721/Rimworld-Archinity/issues/53). 1.6.4871.*

### T-45 — Planet-layer geometry is scribed, so a layer-size patch is worldgen-only

`PlanetLayer.ExposeData` scribes `subdivisions`, `radius`, `viewAngle` and
`viewCenter` per layer, and at `LoadingVars` it calls `InitializeLayer()`, which
rebuilds the icosphere **from those scribed values — never from the def**. Editing a
layer's `PlanetLayerSettingsDef` after a world exists therefore changes nothing in
that save: no error, no warning, no log line, and the def and the world disagree for
the rest of the run.

`Archinity.Pacing/Patches/Orbit_LayerSize.xml` (orbit `subdivisions` 5 → 6, via
`PlanetLayerSettingsDef[defName="Orbit"]/settings/subdivisions`) is exactly this
patch. **It must be final before world creation**, alongside the faction roster
(T-07).

Do not generalise the freeze from the layer to the layer *list*. `WorldGrid.ExposeData`
calls `CreateRequiredLayers()` unconditionally at `PostLoadInit`, so a layer the
scenario gains later **is** created on load — the opposite of T-07. Geometry gets no
such treatment: `CreateRequiredLayers` matches existing layers by `ScenarioTag` and
passes `ScenPart_PlanetLayer.Settings` only to layers it is creating fresh.

Second-order, and worth having right because the patch's own comment has it wrong:
tile count scales **~3^subdivisions, not ~4^subdivisions**. `PlanetLayer.Subdivide`
adds one vertex per triangle and emits one triangle per (vertex, adjacent-triangle)
pair, and `Σ deg(v) = 3·|tris|`, so triangles triple per pass. `InitializeLayer` runs
`subdivisions + 1` passes and the last one emits one tile per pre-existing vertex, so
tiles = `12 + 10·(3^s − 1)`: **2,432 at s=5, 7,292 at s=6** on the full sphere. Orbit
takes `useSurfaceViewAngle`, so multiply by the visible cap.

*`PlanetLayer.ExposeData`, `PlanetLayer.InitializeLayer`, `PlanetLayer.Subdivide`,
`PlanetLayer.FinalizeGeneratedTile`; `WorldGrid.ExposeData`,
`WorldGrid.CreateRequiredLayers`.
[#70](https://github.com/cjd721/Rimworld-Archinity/issues/70). 1.6.4871.*

### T-49 — `Find.RandomSurfacePlayerHomeMap` is null once the only home is in orbit

`Verse.Find` declares
`public static Map RandomSurfacePlayerHomeMap => Current.Game?.RandomRootSurfacePlayerHomeMap;`
— the **same backing property** as `Find.RandomRootSurfacePlayerHomeMap`.
`Game.RandomSurfacePlayerHomeMap`, which accepts a home on any layer whose
`LayerDef.SurfaceTiles` is true, exists and has **no caller anywhere in the
assembly**. So the accessor named "surface" means "root surface", and it returns null
the moment the colony's only home map is in orbit — or on any non-root surface layer.

Three shipped consumers, all in namespace `RimWorld.QuestGen` (not `RimWorld`):

- `QuestNode_Root_WandererJoin.TestRunInt` — when `CanBeSpace`, it is exactly
  `Find.RandomSurfacePlayerHomeMap != null`. False means the quest is never
  generated. Nothing is logged, and a quest that is never offered looks like
  ordinary storyteller variance.
- `QuestNode_GetSiteTile.TryFindTile` — with `canSelectSpace` false, the anchor tile
  degrades to `PlanetTile.Invalid`, so site placement loses its "near the colony"
  reference entirely and either fails or lands anywhere.
- `QuestPart_SpawnMonolith.Notify_QuestSignalReceived` — ends the quest
  `QuestEndOutcome.Fail`. This one does write `Log.Message("Tried to spawn monolith
  but no map found")` — a plain dev-log line, not a warning or an error, and it names
  no cause.

Two supporting facts about why an orbital home does not satisfy the check.
`Verse.Map.IsPlayerHome` is `wasSpawnedViaGravShipLanding || (parent is a
player-faction `canBePlayerHome`) || GravshipUtility.PlayerHasGravEngine(this)`, so
the orbital map genuinely *is* a home — it is the **layer** test that fails. And
`GravshipUtility.ArriveNewMap` calls `SettleUtility.AddNewHome` only when the
destination layer's `DefaultWorldObject == SettlementWorldObjectDef`; `Orbit` sets
`defaultMapWorldObject Space`, so an orbital home is a `Space` `MapParent` and never
a `Settlement`.

The fix, if orbital content needs any of the three: a Harmony postfix on the `Find`
property returning `Current.Game.RandomSurfacePlayerHomeMap` — the dead one.

*`Verse.Find.RandomSurfacePlayerHomeMap`, `Verse.Game.RandomSurfacePlayerHomeMap`,
`Verse.Map.IsPlayerHome`, `GravshipUtility.ArriveNewMap`;
`RimWorld.QuestGen.QuestNode_Root_WandererJoin`,
`RimWorld.QuestGen.QuestNode_GetSiteTile`,
`RimWorld.QuestGen.QuestPart_SpawnMonolith`.
[#71](https://github.com/cjd721/Rimworld-Archinity/issues/71). 1.6.4871.*

### T-54 — World Tech Level strips factions from the roster, and gensteps from the map

T-07 says the roster must be final before worldgen. It does not protect you here: a
reader who has authored the roster correctly and frozen it in time can still watch a
third-party postfix quietly delete rows from it.

`WorldTechLevel.Patches.Patch_FactionGenerator.GetConfigurableFactions` is a
`[HarmonyPostfix]` (priority 200) on `FactionGenerator.ConfigurableFactions` that
rewrites the result as
`__result.Where(f => f.MinRequiredTechLevel<FactionDef>() <= WorldTechLevel.Current)`.
`Page_CreateWorldParams.ResetFactionCounts()` builds `factions` — the list handed to
worldgen — by enumerating **exactly that property**, twice. So on a low-tech-level
start every Spacer faction is dropped from the generated roster: no row in the
faction list, no warning, no log line, and nothing that distinguishes "filtered out"
from "not installed". A sibling transpiler on `FactionGenerator.InitializeFactions`
swaps `DefDatabase<FactionDef>.AllDefs` for the same filtered enumerable, so the dev
quickstart path is filtered too.

**The def is not where the value lives.** `TechLevelUtility.MinRequiredTechLevel<T>()`
is a bare `TechLevelDatabase<T>.Levels[def.index]` array lookup — no field on the def,
no per-call evaluation. That is why the def reads as correct when you inspect it, and
why the fix is not on the def either.

**The fix is one XML file.** `DefTechLevels.Initialize()` runs
`TechLevelDatabase<FactionDef>.ApplyOverrides()`, which reads
`WorldTechLevel.TechLevelConfigDef` — a public `Def` type loadable from **any** mod's
`Defs/` — and writes `Levels[index] = entry.techLevel`. Setting `Undefined` (which is
`0`, and so `<= Current` at every selectable level) is the array's unrestricted
sentinel. WTL ships exactly this pattern for VFE Empire in
`1.6/Defs/TechLevels_FactionDefs.xml`, `<techLevel>Undefined</techLevel>` under an
`<ifModPresent>` guard. Copy it and name our factions. Prefer it to
`Settings.FactionsExcluded`, which reaches the same array through `ApplyExclusions`
but is a **mod setting** — per-install, and therefore T-18.

**The same mechanism is worse one type over.** `FactionDef` is the *only* def type
that gets an `ApplyExclusions` pass at all;
`Patch_MapGenerator.GenerateContentsIntoMap_Prefix` filters `GenStepDef` through the
same `Levels` array and **rewrites the `ref` parameter**, with no exclusion escape
hatch. An Archinity map genstep whose derived level sits above the world level
therefore never runs, on any map, in silence. `ApplyOverrides` does cover
`GenStepDef`, so the `TechLevelConfigDef` fix works there too — and unlike the
faction leg, this one is recoverable once you find it, because it is re-evaluated per
map rather than baked into the world.

Both patches sit in `[PatchGroup("Filters")]` behind
`[HarmonyPrepare] IsFilterEnabled() => WorldTechLevel.Settings.Filter_Factions`, so
this is a T-18 surface as well: two clients with different settings build different
rosters.

Treat the faction leg as effectively permanent. `Window_AddFactions.OpenIfAnyAvailable`
is a real post-worldgen addition path that WTL itself drives from the world faction
tab when the tech level rises, so the categorical "it can never be added" is wrong —
but it offers only defs in the band just crossed, and a faction that arrives that way
is a fresh `loadID` with no shared history. The faction is absent from the generated
world, and the only way back is a post-hoc addition that carries no history.

*`WorldTechLevel.Patches.Patch_FactionGenerator`,
`WorldTechLevel.Patches.Patch_MapGenerator.GenerateContentsIntoMap_Prefix`,
`WorldTechLevel.TechLevelUtility.MinRequiredTechLevel`,
`WorldTechLevel.TechLevelDatabase<T>.ApplyOverrides` / `.ApplyExclusions`,
`WorldTechLevel.TechLevelConfigDef`, `WorldTechLevel.Window_AddFactions`
(`3414187030`, `1.6/Lunar/Components/WorldTechLevel.dll`);
`RimWorld.FactionGenerator.ConfigurableFactions`,
`Page_CreateWorldParams.ResetFactionCounts`. T-07, T-18.
[#70](https://github.com/cjd721/Rimworld-Archinity/issues/70). 1.6.4871.*

---
