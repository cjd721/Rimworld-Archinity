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

**The Church must never climb eras this way.** It is Royalty's `Empire` transformed in place
(`docs/specs/RELIGION.md` § *Failure and recovery* § *Exaltation*), so on top of this freeze a def
swap nulls `Faction.OfEmpire` — not at the swap, but at the next load or faction add/remove
(**T-98**). Present the Church per era through pawn kinds and gear.

*`FactionDef.RoyalTitlesAwardableInSeniorityOrderForReading`,
`RoyalTitleDefExt.GetNextTitle`, `Pawn_RoyaltyTracker.CanUpdateTitle`,
`Pawn_RoyaltyTracker.GetPermitPoints`. Leak table in
`docs/engine/factions-and-worldgen.md`.
[#53](https://github.com/cjd721/Rimworld-Archinity/issues/53); Church note and T-98 cross-reference
from its re-resolution, 2026-09-15. 1.6.4871.*

### T-98 — Swapping a faction's `Faction.def` nulls `Faction.OfEmpire` later, not at the swap

**Companion to T-36.** `RimWorld.FactionManager` caches its singletons — `OfEmpire`, and beside it
`OfPirates`, `OfTradersGuild`, `OfSalvagers`, `OfMechanoids` and the rest — in the private
`RecacheFactions`, which resolves each by def identity
(`empire = FirstFactionOfDef(FactionDefOf.Empire)`). `RecacheFactions` has exactly three callers:
`ExposeData` (on load), `Add` and `Remove`.

So swap the Empire's `Faction.def` and nothing changes yet: the cached field still holds the
instance and every consumer keeps working. **At the next save load, or the next time any faction is
added or removed, the recache finds no faction with that def and the singleton goes null.** Most
consumers null-check and stand down in silence — vanilla's bestowing ceremony, tribute collector and
settlement generation, **T-35**'s permits seed, VFE Empire's 138 sites and VFE Deserters' 49. The
failure lands a session or a week after the change that caused it, which is what makes it so hard to
attribute.

The same holds for every `FactionManager` singleton whose faction climbs by def swap. **A faction any
code reaches through a `FactionManager` singleton must keep its def for the life of the save**;
present its tiers through pawn kinds and gear instead.

*[#53](https://github.com/cjd721/Rimworld-Archinity/issues/53), `docs/specs/RELIGION.md` § *Failure
and recovery* § *Exaltation*; companion to **T-36**. `RimWorld.FactionManager.RecacheFactions` /
`.ExposeData` / `.Add` / `.Remove`, re-read for this entry. 1.6.4871.*

### T-100 — An "allied factions" filter over NPC pairs is empty in vanilla

Any mechanism that selects `B` where `A.RelationKindWith(B) == FactionRelationKind.Ally` for two
non-player factions returns nothing in a vanilla world — as an empty set, never an error.

`Faction.TryMakeInitialRelationsWith` is the only def-driven relation setup, and its local
`GetInitialGoodwill` returns exactly `-100`, `-80` or `0`; `FactionRelation` becomes `Ally` only at
goodwill ≥ 75. **Nothing in vanilla writes NPC↔NPC goodwill afterwards** — every one of the 48
`TryAffectGoodwillWith` call sites has `Faction.OfPlayer` on a side — and NPC↔NPC goodwill never
drifts, because `CalculateAdjustedGoodwillChange` and `CheckReachNaturalGoodwill` short-circuit on
non-player pairs. No NPC alliance exists at game start, and none ever forms.

An alliance ripple, a road network between allies, an "allies send help" rule: each reads green in
review, ships, and never fires. **Seed the edges** — a one-time `TryAffectGoodwillWith` pass between
the factions you author, which then persists unchanged in `Faction.relations` — mind **gate C**
(`permanentEnemyToEveryoneExcept`) when choosing pairs, and make the consumer say when it found none.

*[#68](https://github.com/cjd721/Rimworld-Archinity/issues/68), [#90](https://github.com/cjd721/Rimworld-Archinity/issues/90);
`docs/specs/POLITICS.md` § *The graph is empty* and § *The build* §1,
`docs/specs/WORLD-INFRASTRUCTURE.md` § 3b. `RimWorld.Faction.TryMakeInitialRelationsWith` /
`.RelationKindWith` / `.TryAffectGoodwillWith`, `RimWorld.FactionRelation.CheckKindThresholds`.
1.6.4871.*

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

### T-68 — `SetFactionDirect` leaves a seized turret mis-indexed in the attack-target cache

A mid-map faction flip written with `Thing.SetFactionDirect` skips three things
`Thing.SetFaction` does: `Map.attackTargetsCache.UpdateTarget(t)` for an `IAttackTarget`, the
`ChangedFactionToPlayer` quest signal, and `Map.events.Notify_ThingFactionChanged`. The first
is the one that bites.

`Verse.AI.AttackTargetsCache.RegisterTarget` builds `targetsHostileToFaction` by snapshotting
`thing.HostileTo(faction)` **once per faction, at registration time**, and `UpdateTarget` — a
deregister/re-register pair — is the **only** thing that refreshes it for a live target. So a
turret seized through the direct setter **stays in the player's hostile bucket and stays out
of the raiders'**: the map's AI keeps treating it as an enemy and the attackers keep ignoring
it, with no log line.

**Ushanka's `USH_HE.CompTurretHackable.OnHacked` uses `SetFactionDirect`** where its own
sibling `Ability_HijackSubcore` and vanilla's `RimWorld.CompAncientSecurityTerminal.OnHacked`
both use the full `SetFaction`. Repair is a prefix substituting the call, ~5 lines.

**The reason this survives play-testing is that a reload cures it.** Loading a save
re-registers every attack target from scratch, so the symptom vanishes and comes back only on
the next seizure. Anything of ours that changes a `Thing`'s faction mid-map goes through
`SetFaction`, or calls `UpdateTarget` itself.

*[#58](https://github.com/cjd721/Rimworld-Archinity/issues/58), `docs/specs/HACKING.md`.
`Verse.Thing.SetFaction` / `.SetFactionDirect`,
`Verse.AI.AttackTargetsCache.RegisterTarget` / `.UpdateTarget`;
`USH_HE.CompTurretHackable.OnHacked` from `HackingExpansion.dll`
(`3573344880/1.6/Assemblies/`). T-12 is the same shape one cache over. 1.6.4871.*

### T-85 — World Tech Level writes scribed state from a draw method

`WorldTechLevel.Patches.Patch_WITab_Planet.FillTab_Postfix` draws a `Widgets.ButtonText` on the
planet inspect tab, and its float menu's `SetLevel` writes **both** the volatile
`WorldTechLevel.Current` **and the scribed `GameComponent_TechLevel.WorldTechLevel`** — from
`FillTab`, a draw method. That is a **client-local write to synchronised, saved state off the
frame loop**: the clicking client's save now carries a world tech level the other client's does
not, and nothing reports it. There is no synced command, no letter and no log line; the
divergence surfaces later as mods filtering content differently on the two machines.

Two things make it easy to reach by accident. The button is drawn whenever
`Current.ProgramState == Playing` — **there is no `Prefs.DevMode` guard** — so it is live in an
ordinary campaign, not a debug affordance. And because it skips an era in one click while writing
nothing else, it is also a route around any era clock layered on top: a boundary log that records
era-start ticks never sees the transition, and its history is silently wrong rather than absent.

Shutoff and rationale: `docs/specs/ERA.md` § *The build* § 6a — a Harmony prefix returning false
on that private static, named by string, ~6 lines, loud at startup if WTL renames it. Keep
`GetDesc_Postfix`; the display half wants it.

*[#109](https://github.com/cjd721/Rimworld-Archinity/issues/109), `docs/specs/ERA.md`.
`WorldTechLevel.Patches.Patch_WITab_Planet.FillTab_Postfix` and
`WorldTechLevel.GameComponent_TechLevel` from `WorldTechLevel.dll`
(`3414187030/1.6/Lunar/Components/` — **not** `1.6/Assemblies/`, which holds only the Lunar
loader). See `docs/engine/research-and-tech-tiers.md` § *The scribed field and the volatile
mirror are two different things*. 1.6.4871.*

### T-86 — WTL's add-factions window registers factions at runtime

`Patch_WITab_Planet`'s `SetLevel` calls `WorldTechLevel.Window_AddFactions.OpenIfAnyAvailable(prev)`;
the window's Confirm button calls `FactionGenerator.CreateFactionAndAddToManager(def)` per selected
faction and then spawns settlements for each, **from `DoWindowContents`**. Runtime faction
registration against a frozen roster (**T-07**, the **T-15** class) plus unsynced `Rand` off the
frame loop, in one control.

The `Rand` half is worse than a single draw: the loop is written
`for (int k = 0; k < Rand.RangeInclusive(3, 7); k++)`, so **the bound is re-drawn on every
iteration** and the number of values consumed from the shared stream is itself random. Two clients
diverge in both world state and stream position, with nothing reported on either.

Inert only while `Settings.Filter_Factions` is false, which is this campaign's settled
configuration for an unrelated reason (#7 § 3) — `OpenIfAnyAvailable` returns immediately in that
state. **Turning `Filter_Factions` back on re-arms it.**

*[#109](https://github.com/cjd721/Rimworld-Archinity/issues/109), `docs/specs/ERA.md` § *The
build* § 6b. `WorldTechLevel.Window_AddFactions.OpenIfAnyAvailable` / `.DoWindowContents` and
`Patch_WITab_Planet`'s local `SetLevel`, from `WorldTechLevel.dll`
(`3414187030/1.6/Lunar/Components/`); `RimWorld.FactionGenerator.CreateFactionAndAddToManager`.
1.6.4871.*

---

## Incidents, quests and goodwill

### T-65 — VEF's `forcedPointsRange` sentinel is `IntRange.One`, not its own default

`VEF.Storyteller.IncidentDefExtension.forcedPointsRange` defaults to `IntRange.Zero`, but
`IncidentWorker_RaidEnemySpecial.ResolveRaidPoints` falls through to vanilla point scaling
only when the value **`== IntRange.One`**. The default and the sentinel are different values.

So an `IncidentDef` using that `workerClass` **without** an explicit
`<forcedPointsRange>1~1</forcedPointsRange>` — or with no `IncidentDefExtension` at all —
gets `parms.points = 0 × threatScale = 0`. Not default scaling: a **zero-point raid**. No
error, no warning, no log line, and a raid that arrives empty or does not arrive reads as
ordinary storyteller variance.

Every authored raid the campaign wants goes through this worker — the Glitterite detection
raid, a demand's refusal raid, any Chronicle beat's fixed opposition — because it is the one
XML-reachable way to pin faction, points band and strategy. **Write the `1~1` even when you
want vanilla scaling.**

*[#60](https://github.com/cjd721/Rimworld-Archinity/issues/60), `docs/specs/PRESSURE.md`.
`VEF.Storyteller.IncidentWorker_RaidEnemySpecial.ResolveRaidPoints` and
`VEF.Storyteller.IncidentDefExtension` from `VEF.dll`; verified in **both** on-disk copies of
`2023507013`, which is the one place T-22's VEF divergence had to be checked. 1.6.4871.*

### T-70 — `QuestNode_End` builds two parts and sets `signalListenMode` on one of them

`RimWorld.QuestGen.QuestNode_End.RunInt` sets `signalListenMode` on the
`QuestPart_QuestEnd` it builds, and **not** on the `QuestPart_FactionGoodwillChange` it
builds alongside — which therefore keeps the `OngoingOnly` default. An author writing
`<signalListenMode>NotYetAcceptedOnly</signalListenMode>` together with
`<goodwillChangeAmount>` gets the quest ended and **no goodwill change at all**, with no
error and nothing in the log.

The combination looks sanctioned: shipped XML uses that `signalListenMode` value in three
files — `Script_PawnLend.xml`, `Script_Hospitality_Worker.xml` and
`Script_EndGame_RoyalAscent.xml`. It is exactly the shape a demand that must cost standing
when it is refused before acceptance would reach for, and it is the shape that does nothing.
Author the goodwill change as its own `QuestNode_ChangeFactionGoodwill`, or carry it on a
`QuestPart` of ours whose listen mode we set.

*[#91](https://github.com/cjd721/Rimworld-Archinity/issues/91), `docs/specs/POLITICS.md`.
`RimWorld.QuestGen.QuestNode_End.RunInt`, `RimWorld.QuestPart_FactionGoodwillChange`,
`RimWorld.QuestPart.signalListenMode`. 1.6.4871.*

### T-71 — A chain-granted quest never runs `TestRun`, so every XML gate on it is inert

VEF's `QuestUtils.CreateQuest` → `QuestUtility.GenerateQuestAndMakeAvailable` →
`QuestGen.Generate` calls `root.Run()` and **never** `TestRun`, and `QuestScriptDef.CanRun` is
never consulted on that path. Everything that lives in a `TestRunInt` is therefore dead for a
quest granted through a chain: `QuestScriptDef.CanRun`, `QuestNode_QuestUnique` and
`minRefireDays` all evaluate to nothing, and the quest generates anyway.

Nothing reports it. The gates are still on the def, still correct, still read by the *other*
callers — which is what makes this so easy to trust: a cap that works when the storyteller
grants the quest quietly stops working when a chain does. A category cap of ours built as a
`QuestNode` whose `TestRunInt` counts pending offers has the same problem, and must live
somewhere the chain path actually executes.

*(One claim the audit struck: it is **not** true that only two vanilla callers run `CanRun` —
there are 16. The gates are inert on the chain path regardless; the narrow-caller framing was
wrong and is not what this entry rests on.)*

*[#91](https://github.com/cjd721/Rimworld-Archinity/issues/91), `docs/specs/POLITICS.md`.
`VEF.QuestUtils.CreateQuest` and `VEF.GameComponent_QuestChains` from `VEF.dll`;
`RimWorld.QuestGen.QuestGen.Generate`, `RimWorld.QuestScriptDef.CanRun`,
`RimWorld.QuestGen.QuestNode_QuestUnique`. T-39 is the same method, read for a different
hazard. 1.6.4871.*

### T-72 — VEF's `conditionFailQuests` never matches an expired offer

`VEF.GameComponent_QuestChains.QuestExpired` writes only `QuestInfo.tickExpired`. The
matching predicate, `QuestIsCompletedAndFailed`, tests `outcome == QuestEndOutcome.Fail` —
and `outcome` is written **only** by `QuestCompleted`. An offer that simply expires
therefore never satisfies it.

So a retaliation quest keyed on `conditionFailQuests` is dead on the refusal path, which is
the exact path a faction demand needs: declining a demand in this engine *means* letting the
offer expire, because refusal is not an act (`ChoiceLetter.Option_Reject` only removes the
letter, and expiry emits no signal). The chain field reads as the supported way to say
"and if they refuse, this happens", and it is the one case it cannot see. No error, no log
line — the successor quest is simply never scheduled.

Build the refusal consequence on `QuestPart.Cleanup()` instead, discriminating on
`Quest.State == EndedOfferExpired`; `Quest.CleanupQuestParts()` is the single convergence
point for every terminal transition and needs no signal.

*[#91](https://github.com/cjd721/Rimworld-Archinity/issues/91), `docs/specs/POLITICS.md`.
`VEF.GameComponent_QuestChains.QuestExpired` / `.QuestCompleted` /
`.QuestIsCompletedAndFailed` from `VEF.dll`; `RimWorld.Quest.State`,
`RimWorld.Quest.CleanupQuestParts`. 1.6.4871.*

### T-73 — VEF's `grantAgainOnExpiry` is a unit mismatch, and never fires

`VEF.GameComponent_QuestChains.TryGrantAgainOnExpiry` passes a **tick count**
(`60000f × days`) into `ScheduleQuestMTB`'s **`mtbDays`** parameter, which
`FutureQuestInfo.TryFire` hands to `Rand.MTBEventOccurs(mtbDays, 60000f, 60f)`. So
`daysUntilGrantAgainOnExpiry = 5` becomes a mean time between events of **300,000 days**: the
quest is not re-granted, ever, and nothing says so.

Its two siblings give the field its air of correctness — `TryGrantAgainOnFailure` and
`TryGrantAgainOnSuccess` both use `ScheduleQuestInTicks`, and both work. Only the expiry leg
is wrong, and expiry is the leg a refusable demand runs on. Pairs with T-72: **both of VEF's
expiry-path chain features are broken, in different ways, and both fail silently.** Treat
`conditionFailQuests` and `grantAgainOnExpiry` as unavailable and re-schedule from our own
`QuestPart.Cleanup()`.

*[#91](https://github.com/cjd721/Rimworld-Archinity/issues/91), `docs/specs/POLITICS.md`.
`VEF.GameComponent_QuestChains.TryGrantAgainOnExpiry` / `.TryGrantAgainOnFailure` /
`.TryGrantAgainOnSuccess` / `.ScheduleQuestMTB` / `.ScheduleQuestInTicks` and
`VEF.FutureQuestInfo.TryFire` from `VEF.dll`; `Verse.Rand.MTBEventOccurs`. 1.6.4871.*

### T-76 — A VEF `QuestGiverDef` with `onlyOneReward: false` has a permanently empty catalogue

`VEF.Storyteller.QuestGiverManager.AvailableQuests` prunes on every read:

    availableQuests.RemoveAll(x => x == null || x.askerFaction == null
                                || x.quest_Part_choice == null || x.choice == null);

and `QuestInfo`'s constructor populates `quest_Part_choice` and `choice` **only inside
`if (onlyOneChoice)`** — the flag fed by `QuestGiverDef.onlyOneReward`.

So a giver authored `onlyOneReward: false` generates offers normally and then discards
every one of them on the next read. The window draws no rows. **Nothing logs.**

The same prune fires on a null `askerFaction`, which happens when
`fixedQuestGiverFaction` is unset and `FixedQuestGiverFaction` falls through to
`Find.FactionManager.RandomAlliedFaction(...)` with no allies.

**Fix:** author `onlyOneReward: true` and set `fixedQuestGiverFaction` explicitly. A
startup validator over `DefDatabase<QuestGiverDef>` asserting both is ~10 lines and turns
a silent empty shop into a config error.

*[#106](https://github.com/cjd721/Rimworld-Archinity/issues/106), `docs/specs/CURRENCIES.md` §
*The purchasable quest catalogue*. `VEF.Storyteller.QuestGiverManager.AvailableQuests`,
`VEF.Storyteller.QuestInfo..ctor`, `VEF.Storyteller.QuestGiverDef.onlyOneReward` from `VEF.dll`
(`2023507013/1.6/Assemblies/`). 1.6.4871.*

### T-77 — `QuestWorker.GenerateQuests` swallows every generation exception

`VEF.Storyteller.QuestWorker.GenerateQuests` wraps the whole per-quest body — slate
setup, `CanRun`, `QuestGen.Generate`, `QuestCurrency.Allows` — in `catch (Exception) { }`
with an empty handler.

A quest script that throws during generation therefore never appears in the catalogue and
never reports why. Because the loop removes each candidate from its working list and
continues, a systematically broken script family produces a quietly smaller shop rather
than an error.

**Fix:** prefer `QuestGiverDef.onlySpecifiedQuests` so the pool is a list we authored and
can test, rather than every `!isRootSpecial && IsRootAny` script in the load order. If a
shop is short, this trap is the first thing to check — the log will not mention it.

*[#106](https://github.com/cjd721/Rimworld-Archinity/issues/106), `docs/specs/CURRENCIES.md` §
*The purchasable quest catalogue*. `VEF.Storyteller.QuestWorker.GenerateQuests` from `VEF.dll`
(`2023507013/1.6/Assemblies/`). 1.6.4871.*

### T-88 — A factionless or inert `attackTargets` focus issues no job at all

`IncidentParms.attackTargets` is the one lever that points a raid at something other than the
colonists — `RaidStrategyWorker_ImmediateAttack.MakeLordJob` checks it first and routes to
`LordJob_AssaultThings`, whose pawns take `DutyDefOf.AssaultThing`. **Two classes of target
silently produce no job whatsoever**, and the obvious food-raid target set is both of them:

- **Factionless.** `JobGiver_AITrashDutyFocus.TryGiveJob` returns null unless
  `pawn.HostileTo(focus.Thing)`, and `GenHostility.HostileTo(Thing, Thing)` ends
  `if (a.Faction == null || b.Faction == null) return false;`. A stockpiled item and a sown crop
  have no `Faction`.
- **Inert.** The same job giver calls `TrashUtility.TrashJob(pawn, focus.Thing,
  allowPunchingInert: false, killIncappedTarget: true)`, and `TrashJob` returns **null** for a
  `Building` whose `def.building.isInert` is true when `allowPunchingInert` is false. `Wall`,
  `DoorBase`, `Fence` and `Column` all set it. `Shelf`, `ShelfSmall` and `Cooler` do not, and are
  valid targets.

`Trigger_ThingsDamageTaken` then never fires, and `LordJob_AssaultThings` has **no timeout
transition of its own**. The group is not guaranteed to hang: `LordJob.AddFleeToil` is
`virtual => true` and `LordJob_AssaultThings` does not override it, so `Lord`'s graph builder
attaches a `LordToil_PanicFlee` off every toil when
`faction.def.autoFlee && !faction.neverFlee && Map.CanEverExit`, fired by
`Trigger_FractionPawnsLost`. **So they leave once enough of them are downed — and linger
indefinitely for a never-flee or non-auto-flee faction, or against a player who does not
engage.** The objective failing is unconditional either way, and nothing is logged in any case.

Target faction-owned, non-inert Things: player buildings that are not structure, and
player-faction pawns. `docs/specs/PRESSURE.md` § *The build* § 8 prices a startup validator over
the selector, which is what converts this into a loud failure.

*[#77](https://github.com/cjd721/Rimworld-Archinity/issues/77), `docs/specs/PRESSURE.md` § 8.
`RimWorld.JobGiver_AITrashDutyFocus.TryGiveJob`, `RimWorld.TrashUtility.TrashJob`,
`RimWorld.GenHostility.HostileTo`, `RimWorld.LordJob_AssaultThings`,
`Verse.AI.Group.LordJob.AddFleeToil`; `Wall` in
`Core/Defs/ThingDefs_Buildings/Buildings_Structure.xml`. 1.6.4871.*

### T-89 — `Trigger_ThingsDamageTaken` cannot express a partial loss of pawns

`Verse.AI.Group.Trigger_ThingsDamageTaken.ActivateOn` accumulates only over entries where
`things[i].Spawned`. A dead pawn is despawned, so it leaves the **numerator and the
denominator**, while every surviving spawned pawn contributes `1f`. The average is therefore
pinned at exactly `1`, `num < 1f - damageFraction` is never true, and the transition fires
**solely** through its `num2 == 0` branch — every target gone.

**So `damageFraction` does nothing for a pawn target set.** An objective authored as "kill a third
of the herd and leave" silently means "kill the entire herd", and reads in play as raiders who
will not disengage. The same bias applies to buildings for a different reason: a destroyed
building is excluded too, so the fraction only ever moves on *partial* damage to survivors.

A partial-loss objective needs a trigger of our own that scores against the **original** list
rather than the spawned one; `docs/specs/PRESSURE.md` § *The build* § 8 prices it.

*[#77](https://github.com/cjd721/Rimworld-Archinity/issues/77), `docs/specs/PRESSURE.md` § 8.
`Verse.AI.Group.Trigger_ThingsDamageTaken.ActivateOn`, `RimWorld.LordJob_AssaultThings`.
1.6.4871.*

### T-90 — A `RaidStrategyDef` authored without `arriveModes` is silently unselectable

`IncidentWorker_RaidEnemy.ResolveRaidStrategy`'s local `CanUseStrategy` predicate returns
**false** when `parms.raidArrivalMode` is null and the def's `arriveModes` is null — the fallback
in that branch is a bare `return false`, not a default mode. A strategy we author without the
list is therefore never selected by the storyteller, for any faction, forever.

Nothing reports it. `ResolveRaidStrategy` does log an error and fall back to `ImmediateAttack`,
but **only when no strategy at all passes**; while vanilla's nine remain selectable one of them is
simply chosen instead, and the omission reads as a strategy that is merely unlucky. Every vanilla
`RaidStrategyDef` declares `arriveModes`, so the field looks optional and is not.

**The sibling failure on the other path is loud, and deliberately not a register entry.** A
strategy *pre-set* on `parms` — the T-14 escape — reaches
`PawnsArrivalModeWorker.CanUseWith`, which dereferences `parms.raidStrategy.arriveModes` with no
null guard and throws. See `docs/engine/storyteller-and-incidents.md` § *`arriveModes` is not
optional, and the two paths fail differently*.

*[#77](https://github.com/cjd721/Rimworld-Archinity/issues/77), `docs/specs/PRESSURE.md` § 8.
`RimWorld.IncidentWorker_RaidEnemy.ResolveRaidStrategy`, `RimWorld.RaidStrategyDef.arriveModes`.
1.6.4871.*

### T-91 — `VFEE_Deserters` stops raiding entirely without an Empire-titled pawn on the map

**Companion to T-14, which stands as written.** T-14 records that VFE Empire blacklists every raid
strategy but its own on the deserter faction. This is what that blacklist does when combined with
the one surviving strategy's own gate.

`VFEEmpire.RaidStrategyWorker_Deserters.CanUseWith` returns false unless a pawn holding a title in
`Faction.OfEmpire` is spawned on the map. With every other strategy in
`FactionDef.disallowedRaidStrategies`, `DesertersStrat` is the faction's only candidate — and
`IncidentWorker_RaidEnemy.FactionCanBeGroupSource` rejects a faction outright when no
`RaidStrategyDef` passes `CanUseWith`. **No titled pawn on the map, no passing strategy, no
raid.** The faction is dropped from the eligible pool with no message, which is **T-17**'s
fail-open-and-fail-quiet shape reached by a different route.

This bites the campaign specifically: the deserter faction is the Schism, so its raids are
political beats rather than ambient pressure, and a Schism that has gone quiet looks like the
storyteller's variance. The remedy is not to satisfy the gate but to bypass the selection path
entirely — author the raid and pre-set `parms.raidStrategy`, which is T-14's second escape and the
one `docs/specs/PRESSURE.md` § *The build* § 8 selects. That makes authored raids the **only**
route for this faction rather than a stylistic preference.

*[#77](https://github.com/cjd721/Rimworld-Archinity/issues/77), `docs/specs/PRESSURE.md` § 8;
companion to **T-14**, sibling of **T-17**. `VFEEmpire.RaidStrategyWorker_Deserters.CanUseWith`
from `VFEEmpire.dll` (`2938820380/1.6/Assemblies/`);
`RimWorld.IncidentWorker_RaidEnemy.FactionCanBeGroupSource`,
`RimWorld.RaidStrategyWorker.CanUseWith`. 1.6.4871.*

---
