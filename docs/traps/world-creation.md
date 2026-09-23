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

When the eligible pool empties, raids simply stop firing and nothing says so. Ignorance
Is Bliss gates via a postfix on `FactionCanBeGroupSource` that is a **pure veto** —
`__result = __result && FactionInEligibleTechRange(f)`, with no substitution and no
fallback — so `IncidentWorker_RaidEnemy.TryResolveRaidFaction` simply finds no candidate
and returns false. Its `desperate: true` second pass is vetoed identically. **The
warning never fires at raid time**: `WarnIfNoFactions()` is called only from
`Settings.WriteAll`, i.e. on closing the settings window. Never let the eligible pool
empty; check it whenever the roster or a tech gate changes.

> **Mechanism corrected — 2026-09-17, [#128](https://github.com/cjd721/Rimworld-Archinity/issues/128).**
> This entry previously read *"with `changeQuests=true` that postfix has **no `else`** — so
> an out-of-tech faction is not replaced, it is allowed."* **`changeQuests` does not reach
> `FactionCanBeGroupSource` at all.** It governs a different postfix, on
> `IncidentWorker_PawnsArrive.CanFireNowSub`, which catches the case
> `TryResolveRaidFaction` returns early on — a faction already set in `parms.faction`, as a
> quest threat does — and **substitutes** a random in-band hostile faction. Two separate
> paths: an unresolved faction is **vetoed**, a pre-set one is **substituted**.
> The fail-open, fail-quiet symptom above is unchanged and still the reason this trap
> exists. Note also that **`changeQuests = false` force-*allows* the incident**
> (`__result = true`) rather than blocking it — confirmed against IL, not the decompiler.
> [#22](https://github.com/cjd721/Rimworld-Archinity/issues/22) owns the fix.

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
  **⚠ Corrected 2026-09-23 ([#147](https://github.com/cjd721/Rimworld-Archinity/issues/147)):
  this property is *not* what takes the joiner quests down in 1.6.** It appears only in
  the `CanBeSpace == true` branch, and `CanBeSpace` is `false` on **all five** shipped
  subclasses [V], so that branch is unreachable. The live path is
  `QuestGen_Get.GetMap(canBeSpace: false)` — see **T-128**. T-49's mechanism is unchanged
  and its other two consumers stand; only this consumer was mis-blamed.
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

### T-109 — Unlisting a faith from its last faction is a deferred, silent mass conversion

`RimWorld.IdeoManager.CanRemoveIdeo` treats an `Ideo` as garbage when no faction lists it (primary
or minor) **and no pawn on a map** holds it. It checks `PawnsFinder.AllMaps` only, so **world pawns
and caravan members do not keep a faith alive**. `Pawn.ExitMap` → `IdeoManager.Notify_PawnLeftMap` and
`Pawn.Kill` → `Notify_PawnKilled` queue the removal. On the next `World.WorldTick` → `IdeoManagerTick`,
`IdeoManager.Remove` calls `Pawn_IdeoTracker.Notify_IdeoRemoved` on
`PawnsFinder.AllMapsWorldAndTemporary_AliveOrDead`. That `SetIdeo`s every holder to `FallbackIdeo`
(the pawn's faction's primary, or a random `Ideo` for a factionless pawn) and strips the faith from
every `previousIdeos`. No letter is sent. The only log line (`"Faction … contains ideo … which was
removed!"`) fires when a faction *still* lists it, which is exactly the case that is not happening.

**How it bites.** `FactionIdeosTracker.SetPrimary` on an NPC faction whose old faith no other faction
holds, with the old faith not kept in `ideosMinor`, looks like a label-only change. The faction's
people still hold the old faith, and nothing complains. The next time one of its trader, visitor or raid
groups walks off a map, or its last on-map member dies, the old faith is deleted and **every one of that
faction's world pawns converts to the new primary at once**. A design that meant "the government changed
and the people did not" has silently become "everyone converted", at a moment nobody chose. RimPacts'
`ResolveMissionary` and `EnsurePuppetIdeo` and VFE Classical's `GainFavorOf` all set up exactly this
state.

**It survives play-testing** because the delay depends on traffic: in a quiet stretch the old faith
lingers for days, and when it goes it leaves no trace except its absence from the Ideoligions tab.

**Fix:** never unlist a faith that still has believers. Keep it as a minor
(`IdeosMinorListForReading.Add`), or convert its holders first. If anything of ours stores an `Ideo`
reference, treat null-on-load as "removed", not "never set".

*[#133](https://github.com/cjd721/Rimworld-Archinity/issues/133), `docs/specs/RELIGION.md`
§ *An NPC faction's faith changes*. `RimWorld.IdeoManager.CanRemoveIdeo` / `.TryQueueIdeoRemoval` /
`.Remove` / `.IdeoManagerTick`, `RimWorld.Pawn_IdeoTracker.Notify_IdeoRemoved` / `.FallbackIdeo`,
`Verse.Pawn.ExitMap` / `.Kill`, `RimWorld.PawnsFinder.AllMaps` from `Assembly-CSharp.dll`. 1.6.4871.
Confirmable in one client: unlist a faction's unique faith, let one of its groups leave the map.*

---

### T-110 — Positive goodwill is refused while the player is on that faction's settlement

`Faction.CanChangeGoodwillFor(other, goodwillChange)` returns `false` for any **positive** change when
`IsPlayer && SettlementUtility.IsPlayerAttackingAnySettlementOf(other)` or the mirror. The check is
*"`other` is hostile to the player and any loaded map's parent is a `Settlement` of `other`"*.
`TryAffectGoodwillWith` then returns `false`, **with no message, log line or letter**, and the
goodwill is unchanged.

A reward, a liberation, a revolt's *"the new government is friendly"* or an alliance written while
the players are still standing on that faction's settlement map is silently discarded. Nothing in
the UI says a write was attempted. It reads as a balance bug.

**Pay it on map exit.** FT&V's reference scribes a pending reward and applies it in
`ApplyPendingExitReward` (`docs/specs/TERRITORY.md` § *Persistence and multiplayer*). Or write it
after the faction has stopped being hostile by another path.

The same method also refuses **every** goodwill change when either def is `permanentEnemy` (and the
permanent-enemy-except gates), which is equally silent.

*[#92](https://github.com/cjd721/Rimworld-Archinity/issues/92),
[#131](https://github.com/cjd721/Rimworld-Archinity/issues/131).
`RimWorld.Faction.CanChangeGoodwillFor`, `RimWorld.Planet.SettlementUtility.IsPlayerAttackingAnySettlementOf`.
1.6.4871.*

---

### T-112 — A `PawnKindDef` used as a marker silently resets

Scenarios can give starting pawns a custom kind
(`ScenPart_ConfigPage_ConfigureStartingPawns_Xenotypes.overrideKinds`; Biotech's *The Sanguophage*
uses `Sanguophage_Player`), and `QuestNode_GetPawn.mustBeOfKind` filters on it from XML. That makes
the kind look like a free marker. It does not last:

- **`Pawn.SetFaction(newFaction)`** calls `ChangeKind(newFaction.def.basicMemberKind)` whenever
  `newFaction == Faction.OfPlayer`, the pawn is humanlike and it is not a quest lodger. A marked
  colonist who leaves the faction and rejoins becomes a `Tribesperson` (PlayerTribe) or `Colonist`.
  That covers a captured colonist who is re-recruited, and a kidnapped one:
  `KidnappedPawnsTracker.KidnappedPawnsTrackerTick` moves kidnapped pawns to the kidnapper's
  faction on a 30-day MTB.
- **`MentalBreakWorker_RunWild`** calls `ChangeKind(WildMan)`. Re-taming then goes through
  `SetFaction` and resets the kind again.
- `GameComponent_PawnDuplicator.Duplicate` copies `kindDef`, so a duplicate carries the marker.

No log line in any case.

*[#134](https://github.com/cjd721/Rimworld-Archinity/issues/134). `Verse.Pawn.SetFaction`, `Verse.Pawn.ChangeKind`,
`Verse.AI.MentalBreakWorker_RunWild`, `RimWorld.GameComponent_PawnDuplicator.Duplicate`. 1.6.4871.*

---

## Holdings, outposts and world objects changing hands

### T-140 — Per-settlement state across an ownership change: `SetFaction` carries all of it, and destroy-and-recreate loses all of it

A settlement changes hands in one of two shapes, and each fails silently in its own direction.
Which shape a transfer takes decides what survives it.

**Half 1 — `SetFaction` carries everything keyed on the settlement.** `WorldObject.SetFaction` is a
bare `factionInt` write. `Settlement` and `MapParent` do not override it, and nothing is notified
(`docs/engine/factions-and-worldgen.md` § *`WorldObject.SetFaction` is a bare field write*).
Everything attached survives a transfer and now belongs to the new owner, with no error:

- **Every `WorldObjectComp`** comes with it. A holding record or a rebuild debt
  (`TradeRequestComp`) on an R2 settlement now marks the winner's settlement.
  - Bare-`SetFaction` transfers include RimPacts' `CedeOne` (#152) — its `TryRevertConquered` has
    the same shape but is unreachable in 1.6, because its hold meter only rises (#172) — and FT&V's `Invasions.Utility.ApplyWinnerToSettlement` **only when a map is open**.
  - **Resolved in absentia** (`!mapStillOpen && !HasMap`), that same method destroys and recreates
    (`Remove` + `MakeWorldObject(def)` + `SetFaction` + `Add`), so it falls under half 2: the comps
    die and the ID is new.
  - **So the #92 overlay's outcome takes both shapes depending on attendance.** A Build B copy
    inherits whichever it copies.
- **VFE Empire's `TitheInfo`** is keyed by reference on the `Settlement` in
  `WorldComponent_Vassals.titheInfo` (`Dictionary<Settlement, TitheInfo>`). `DoDay` and
  `TitheWorker.Deliver` never check `Settlement.Faction` or `Destroyed`, so a vassal whose settlement
  changed hands keeps delivering to the same lord (#167). A destroyed or recreated one is half 2.
- **Inbound caravans re-check against the new owner.** Trade and Visit abort on a hostile owner,
  OfferGifts aborts on a non-hostile one, and Attack carries on (**T-138**).

**Half 2 — destroy-and-recreate mints a new ID.** `WorldObjectMaker.MakeWorldObject` assigns
`Find.UniqueIDsManager.GetNextWorldObjectID()` [V]. The paths that replace a settlement rather than
rewrite it:

- `SettlementDefeatUtility.CheckDefeated` → `DestroyedSettlement`;
- a `TERRITORY.md` §3 R1 holding object, and R2's recreation;
- a replacement for a def change (`TERRITORY.md` TR-3);
- FT&V's `ApplyWinnerToSettlement` in absentia (above) and `ApplyWinnerToVassalOffMap`;
- Rim War's `ConvertSettlement` (`Destroy()` + `AddNewHome`).

On any of them, with no error:

- **ID-derived values silently re-roll:** vanilla's `TraderKind` (`|ID.HashOffset()| % n`),
  RimPacts' `SpecialtyOf` (`HashCombineInt(ID, 977)`), MP Compat's `GetTitheInfo` seed.
- **Records keyed on the old object are orphaned:** by ID — BTG `cachedTraderKinds`, FT&V
  `lastTickProcessedByWorldId`; by reference — a TR-1 tier comp, `WORLD-INFRASTRUCTURE.md`'s
  `RouteProject.from/to` (`Scribe_References` to the old `Settlement`), and VFE Empire's `TitheInfo`,
  whose old entry keeps paying in-session and is dropped with a logged null-key error at the next
  load [I, `Scribe_References`]; the new object is not a vassal.
- **Comps die with the object:** `WorldObjectsHolder.Remove` runs `PostPostRemove`, and `Destroy`
  adds `PostDestroy` and the quest `Destroyed` signal.
- **Every inbound player order aborts** at the next re-check, because the old object is no longer
  `Spawned`, with vanilla's vague *"couldn't reach its destination"*. VF aircraft instead land on
  whatever now owns the tile.

**Fix:** whatever keys on a settlement must validate owner and existence on read, or be ended or
re-bound by the transfer code. There is no hook to subscribe to. Derive from, or key on, `Tile` —
the only identity that survives replacement — or copy the value at conversion. For inbound orders,
rebind by tile inside the transfer command (`TERRITORY.md` CF-C); for a route project, re-bind its
endpoints by tile or transfer by `SetFaction`.

*[#152](https://github.com/cjd721/Rimworld-Archinity/issues/152),
[#154](https://github.com/cjd721/Rimworld-Archinity/issues/154),
[#165](https://github.com/cjd721/Rimworld-Archinity/issues/165),
[#167](https://github.com/cjd721/Rimworld-Archinity/issues/167),
[#172](https://github.com/cjd721/Rimworld-Archinity/issues/172); `docs/specs/TERRITORY.md` § *How
a holding ends* and § *A caravan en route when its destination changes hands*.
`RimWorld.Planet.WorldObject.SetFaction` / `.Destroy`, `RimWorld.Planet.WorldObjectsHolder.Remove`,
`RimWorld.Planet.WorldObjectMaker.MakeWorldObject`; `294100/3626725895/Assemblies/FactionTerritories.dll`
`FactionTerritories.Invasions.Utility.ApplyWinnerToSettlement`;
`294100/2938820380/1.6/Assemblies/VFEEmpire.dll` `VFEEmpire.WorldComponent_Vassals.DoDay`. The
dual shape read from `ApplyWinnerToSettlement`'s `!mapStillOpen && !HasMap` branch. 1.6.4871.*

### T-145 — Under R1, anything a holding reads from its own owner reads the player's def, and the era advance rewrites it

Under `docs/specs/TERRITORY.md` §3 R1, a taken settlement becomes a world object owned by
`Faction.OfPlayer` (#120). `AdvanceEra()` write 3 sets `Faction.OfPlayer.def.techLevel` at every
boundary (`docs/specs/ERA.md` § 3). A holding whose tier is computed the vanilla way,
`holding.Faction.def.techLevel`, therefore climbs to the colony's era at every advance. Its yield
and its advancement price move with it, and no error or letter says so. The idiom is correct for
an NPC `Settlement` and is the one `TERRITORY.md` § *What a holding pays* P4 states, which is why it
will get copied.

**The same applies to anything else keyed on the owner's def** (#165): a specialty from a
`FactionDef` extension, or a tech filter such as RimPacts' `SpecialtyOf` pool filter on
`Faction.def.techLevel`, reads the player's def under R1. (`TraderKind` is not the hazard: an R1
holding has no trader tracker, so the kind is copied at conquest.)

The same shape applies one step removed. A tier **derived from the former faction**, as Faction
Territories does (`VassalagePointsComponent.ResolveFactionTechLevelSafe` → `faction.def.techLevel`,
live by loadID), climbs whenever the faction grid climbs that faction by `Faction.def` swap.

**Fix:** store the tier (and the specialty) on the holding at conquest, read from the *former*
faction (`TERRITORY.md` § *Paying to advance a holding* TR-1). Never read either from
`holding.Faction`.

*[#167](https://github.com/cjd721/Rimworld-Archinity/issues/167),
[#165](https://github.com/cjd721/Rimworld-Archinity/issues/165). [V]
`294100/3626725895/Assemblies/FactionTerritories.dll`
`FactionTerritories.Vassalise.VassalagePointsComponent`, `FactionTerritories_VassalOutpost`;
[V, spec] `docs/specs/ERA.md` § 3. The composition is [I] until built.*

### T-148 — Outpost occupants are invisible to the storyteller's population

`StorytellerUtilityPopulation.AdjustedPopulation` sums
`PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive` plus
`QuestUtility.TotalBorrowedColonistCount()`. `Outposts.Outpost.AddPawn` removes the pawn from its
caravan, its `holdingOwner` and `Find.WorldPawns` and keeps it only in the outpost's private
`occupants` list — on no map, in no caravan, in no transporter, in no quest. **The pawn stops
counting.** Population intent rises, and the storyteller behaves as though the colony shrank:
more joiners, never an error.

Anything that parks pawns off-map in its own container has the same shape. Vanilla's own fix is
the precedent: `QuestPart_LendColonistsToFaction` is summed back in by
`TotalBorrowedColonistCount`.

**Fix:** a postfix on `AdjustedPopulation` adding the occupants of every live `Outposts.Outpost`
(`docs/specs/TERRITORY.md` OC-N2).

*[#170](https://github.com/cjd721/Rimworld-Archinity/issues/170), `docs/specs/TERRITORY.md` §
*What an outpost costs*. Verified against 1.6 `Assembly-CSharp.dll` and
`2023507013/1.6/Assemblies/Outposts.dll`.*

### T-149 — VEF charges an outpost's cost only when the caravan's last humanlike joins

`CostToMake` is deducted, and `costPaid` set, inside the branch of `Outposts.Outpost.AddPawn` that
runs when the joining pawn's caravan has **no humanlike left** — at which point the caravan's goods
move into the outpost and the caravan is destroyed. The founding dialog calls `AddPawn` on every
caravan pawn, so in the shipped flow the last humanlike's call charges (animals later in the list join
after it). **Any rule that makes `AddPawn` /
`Utils.CanAddPawn` return false for a humanlike** (a prisoner, a slave, a child) leaves that pawn in
the caravan: the caravan survives, its goods stay in it, and the outpost is founded free. No error;
`costPaid` simply stays false.

**Fix:** a roster rule and the charge are one change. Either move rejected humanlikes out before
the last `AddPawn`, or charge explicitly at founding.

*[#170](https://github.com/cjd721/Rimworld-Archinity/issues/170), `docs/specs/TERRITORY.md` §
*What an outpost costs*. Verified against `2023507013/1.6/Assemblies/Outposts.dll`
`Outposts.Outpost.AddPawn`.*

### T-150 — Any map generated on a `MapParent`'s tile belongs to that `MapParent`, and a VEF outpost never lets it go

`GetOrGenerateMapUtility.GetOrGenerateMap(tile, …)` generates under
`Find.WorldObjects.MapParentAt(tile)` if one exists. It uses the suggested def only when none does.
`WorldObjectsHolder.MapParentAt` returns the **first** `MapParent` in list order on that tile.
**M-proxy works only while the target is not a `MapParent`.** A temporary `Settlement` placed on
the tile to borrow its map generation (FT&V's `GetOrCreateVassalBattleSettlement`) loses to an older
`MapParent` already there. FT&V's own holding is a plain `WorldObject`, so the trick works for it.

`Outposts.Outpost : MapParent` declares no `mapGenerator` (VEF `1.6/Defs/WorldObjectDefs/Base.xml`
`OutpostBase`), so `MapParent.MapGeneratorDef` falls back to `MapGeneratorDefOf.Encounter`.
`Outpost` does not override `ShouldRemoveMapNow`, whose base returns `false`, so
`CheckRemoveMapNow` never removes the map. While the map exists, `Outpost.Tick` skips
`SatisfyNeeds` for occupants.

Vanilla caravan incidents are protected by default. `WorldObjectDef.allowCaravanIncidentsWhichGenerateMap`
defaults `false`, and `OutpostBase` does not set it
(`CaravanIncidentUtility.CanFireIncidentWhichWantsToGenerateMapAt`). Our own code has no such
guard.

**Fix:** never call `GetOrGenerateMap` on an outpost's tile unless an `Outpost` subclass or patch
overrides `ShouldRemoveMapNow`. Otherwise fight on an adjacent tile (M-site).

*[#171](https://github.com/cjd721/Rimworld-Archinity/issues/171), `docs/specs/TERRITORY.md` §
*An outpost's upkeep arrives as events*. Verified against 1.6 `Assembly-CSharp.dll` and VEF
`2023507013/1.6/Assemblies/Outposts.dll`.*

### T-151 — `Outpost.Destroy()` on a staffed outpost silently discards its pawns

`Outpost.AddPawn` removes each occupant from its caravan, its `holdingOwner` and `Find.WorldPawns`,
and holds it only in `occupants` (scribed `LookMode.Deep`). `Outpost.PostRemove` calls
`OutpostsMod.Notify_Removed`, whose body is **empty**. A `Destroy()` on a staffed outpost therefore
leaves living colonists referenced by nothing: no death, no `Notify_PawnLost`, no letter, and they
are gone at the next save. VEF's own exits are safe for living pawns: `ConvertToCaravan` makes a
caravan first, and `Tick` destroys only at `PawnCount == 0`. For dead ones see **T-152**.

**Fix:** any code of ours that ends an outpost must first evacuate the occupants
(`ConvertToCaravan`), kill them, or transfer them to a holder, and only then destroy it.

*[#171](https://github.com/cjd721/Rimworld-Archinity/issues/171), `docs/specs/TERRITORY.md` §
*An outpost's upkeep arrives as events* → *Loss*. Verified against VEF
`2023507013/1.6/Assemblies/Outposts.dll`.*

### T-152 — An outpost occupant who dies of disease or bleeding stays an occupant, counts and produces

VEF cleans up a death only on the per-tick path. `Outposts.Outpost.SatisfyNeeds(Pawn)` runs
`if (!Spawned && !pawn.Dead) { OutpostHealthTick(pawn); if (pawn.Dead) { occupants.Remove(pawn);
containedItems.Add(pawn.Corpse); } }`. In 1.6 the per-tick `Hediff.Tick` / `PostTick` are empty in
the base; disease progression (`HediffComp_SeverityModifierBase.CompPostTickInterval`), injuries
(`Hediff_Injury.TickInterval`) and bleeding run on the **interval** path, `TickInterval` →
`SatisfyNeedsInterval` → `OutpostHealthTickInterval`, which simply returns on `pawn.Dead`. On the
next tick `SatisfyNeeds` skips the pawn because it is dead.

So a pawn killed by disease or bleeding stays in `occupants`. `PawnCount` never reaches 0, so the
outpost is never abandoned, and `IsCapable` (humanlike, has skills) still counts the dead pawn as a
producer. No letter, no error.

**Fix:** handle occupant death ourselves, as a check in the synced tick, before anything reads
`occupants`, `PawnCount` or the yield.

*Found in review of [#171](https://github.com/cjd721/Rimworld-Archinity/issues/171),
`docs/specs/TERRITORY.md` § *An outpost's upkeep arrives as events* → OU-D4. `Outposts.Outpost.SatisfyNeeds`
/ `.OutpostHealthTickInterval` / `.IsCapable`, `2023507013/1.6/Assemblies/Outposts.dll`; `Verse.Hediff`
(`Assembly-CSharp.dll` 1.6). [V code; the in-play outcome is I — RUN listed in the spec.]*

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

**The prune is broader than the flag, and this is the clause that bites an item shop.**
`QuestInfo`'s constructor populates `quest_Part_choice` / `choice` only if `onlyOneChoice` is
true **and** the generated quest actually contains a `QuestPart_Choice` [V]. So **even with
`onlyOneReward: true`, any entry whose script builds no choice part is silently discarded on
the next read of `AvailableQuests`.** An item entry must therefore go through
`QuestNode_AddItemsReward` — whose `RunInt` constructs a `QuestPart_Choice` holding a single
`Reward_Items` and adds the `QuestPart_DropPods` that `Reward_Items.GenerateQuestParts` yields
[V] — or another node that builds a choice part. A bare delivery node produces an entry that
generates, looks correct, and is gone before it is ever drawn.
(*Added 2026-09-23 from [#144](https://github.com/cjd721/Rimworld-Archinity/issues/144).*)

**Fix:** author `onlyOneReward: true` and set `fixedQuestGiverFaction` explicitly. A
startup validator over `DefDatabase<QuestGiverDef>` asserting both is ~10 lines and turns
a silent empty shop into a config error.

*[#106](https://github.com/cjd721/Rimworld-Archinity/issues/106),
[#144](https://github.com/cjd721/Rimworld-Archinity/issues/144), `docs/specs/CURRENCIES.md` §
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

### T-101 — A reward option with nothing to draw cannot be chosen

`RimWorld.MainTabWindow_Quests.DoRewards` builds each option's row from its rewards'
`StackElements` and **`continue`s past an option whose list is empty**. No row is drawn,
so that option's "Accept for:" button never exists. Meanwhile `DoAcceptButton` returns
early (outside dev mode) for **any** quest carrying a `QuestPart_Choice`. There is no
plain Accept button to fall back on.

Nothing is logged. The option is still in `QuestPart_Choice.choices`, still counts toward
`PreventsAutoAccept`, and still has its parts in the quest. It just cannot be picked from
the window. If *every* option draws nothing, the quest cannot be accepted from the quest
window at all.

It is the shape two specs reach for: a custom `Reward_*` that forgets to override
`StackElements` (the base returns `Enumerable.Empty`), and a choice branch carrying
consequence parts but no reward (`POLITICS.md` § *Paired rival demands*). Give every option
at least one reward whose `StackElements` yields
`QuestPartUtility.GetStandardRewardStackElement(…)`, as `VFED.Reward_Visibility` does.

Related and also silent: `DoRewards` and `DoAcceptButton` both stop at the **first**
`QuestPart_Choice` in the parts list. A second choice part's options are never drawn,
and at acceptance its `PreQuestAccept` auto-picks option 0. That last step logs a red error.

*[#135](https://github.com/cjd721/Rimworld-Archinity/issues/135), `docs/specs/RELIGION.md`
§ *Credit for a deed*. `RimWorld.MainTabWindow_Quests.DoRewards`, `.DoAcceptButton`,
`RimWorld.Reward.StackElements`, `RimWorld.QuestPart_Choice.PreQuestAccept`. 1.6.4871.*

---

### T-102 — `GiveRewards` drops Exaltation unless the asker is titled

`RimWorld.QuestGen.QuestGen_Rewards.GiveRewards` — the method behind `QuestNode_GiveRewards`
and six vanilla C# roots — sets `allowRoyalFavor = false` **before** generating when any of
these holds: `giverFaction == null`, `asker.royalty == null`,
`!asker.royalty.HasAnyTitleIn(asker.Faction)`, or the giver is hostile to the player.
`RewardsGenerator.DoGenerate`'s own gate (`giverFaction.allowRoyalFavorRewards &&
def.HasRoyalTitles`) never gets a vote.

So a Church (Empire) quest whose asker is untitled offers **no Exaltation option**. It gets
goodwill and items instead, with no message. `docs/specs/RELIGION.md` §4 stated only the
generator's gate. Royalty's scripts ask for a titled asker with
`QuestNode_GetPawn.mustHaveRoyalTitleInCurrentFaction`, for example in `Scripts_Utility.xml`,
`Scripts_RewardRaid.xml` and `Script_PawnLend.xml`. A hand-built Church deed must do
the same, or construct `Reward_RoyalFavor` directly, as `QuestNode_GiveRoyalFavor` does.

*[#135](https://github.com/cjd721/Rimworld-Archinity/issues/135).
`RimWorld.QuestGen.QuestGen_Rewards.GiveRewards`, `RimWorld.RewardsGenerator.DoGenerate`.
1.6.4871.*

---

### T-103 — A VEF `QuestGiverDef` never refills after a purchase, and its reset throws away what it did not sell

`VEF.Storyteller.QuestGiverManager` fills its pool in three places only:
- `Init()`, called by `CompQuestGiver.Use` when the manager is first created
- `StorytellerWatcher.AddQuestGiverManager`, when `generateOnce` is set
- `Reset()`, called from `Tick()` only when `def.resetEveryTick != -1`

`ActivateQuest` adds, accepts and charges the bought offer, then `availableQuests.Remove(questInfo)`. **It generates nothing.**

So a giver authored with the default `resetEveryTick = -1` gets **one** pool for the life of the save. Each purchase shrinks it, and when it is empty the window shows no rows. Nothing logs.

Setting `resetEveryTick` is not a clean fix. `Reset()` begins with `availableQuests.Clear()`, so every refresh **discards every unbought offer** — including one the player was saving for — before `QuestWorker.GenerateQuests` redraws by `RandomElement`.

This bites hardest on anything sequential. A step whose `CanRun` gate opens only after the previous step succeeded cannot appear until the next reset, and that reset wipes everything else on offer.

**Fix:** decide per giver whether offers are perishable. If a new offer must appear promptly after a purchase or a quest outcome, call `GenerateQuests()` (which appends, not `Reset()`) from a hook of ours on the synced path — a `Quest.End` postfix or our purchase command — never from the window.

*[#132](https://github.com/cjd721/Rimworld-Archinity/issues/132), `docs/specs/CURRENCIES.md` § *The Schism catalogue — a spend that advances the plot*. `VEF.Storyteller.QuestGiverManager.Init` / `.Tick` / `.Reset` / `.GenerateQuests` / `.ActivateQuest`, `VEF.Storyteller.StorytellerWatcher.AddQuestGiverManager`, `VEF.Storyteller.CompQuestGiver.Use` from `VEF.dll` (`2023507013/1.6/Assemblies/`). 1.6.4871.*

---

### T-115 — VEF's `storytellerThreat` replaces every faction's natural goodwill, silently

`VEF.Storyteller.VanillaExpandedFramework_Faction_NaturalGoodwill_Patch` is a postfix on the
`RimWorld.Faction.NaturalGoodwill` **getter** — the `#Blob` attribute names `RimWorld.Faction`,
`NaturalGoodwill`, `MethodType.Getter`. For any non-player faction it reads the **active**
storyteller's `StorytellerDefExtension`. If `storytellerThreat` is non-null, it sets `__result` to
`storytellerThreat.naturallGoodwillForAllFactions.Average`. That field is a non-nullable
`IntRange` defaulting to `0~0`: the null check compiles away, and the override applies the moment
the object exists.

So a storyteller that adds `storytellerThreat` for any of its **other** fields
(`disableThreatsAtPopulationCount`, `allDamagesMultiplier`, `goodIncidents`,
`raidWarningRange`) also pins every faction's natural goodwill to 0. That discards every
`GoodwillSituationWorker.GetNaturalGoodwillOffset` term the vanilla sum would have produced:
`NaturalEnemy`'s −130, `SameIdeo`, every Ideology meme situation, and any worker of ours,
including the Church suspicion offset (`docs/specs/RELIGION.md` § *The build — Exaltation* §6).

Every reader goes through the patched getter:

- `Faction.CheckReachNaturalGoodwill` (drift)
- `Faction.CalculateAdjustedGoodwillChange`
- `FactionUIUtility`'s natural-goodwill column

So drift, change scaling and the Factions tab all agree on the wrong number, and nothing looks
inconsistent. `GoodwillSituationManager.GetNaturalGoodwill` itself is not patched, and
`GetMaxGoodwill` caps are unaffected.

No corpus XML sets `storytellerThreat` today, so the trap is armed only by a storyteller we
author. `docs/specs/PRESSURE.md` plans ours on the same extension.
**Leave `storytellerThreat` unset**, or set `naturallGoodwillForAllFactions` knowing that it
replaces the vanilla sum for every faction.

*[#130](https://github.com/cjd721/Rimworld-Archinity/issues/130), `docs/specs/RELIGION.md` § *The
Schism* § *Constraints*. `VEF.Storyteller.VanillaExpandedFramework_Faction_NaturalGoodwill_Patch.Postfix`,
`VEF.Storyteller.StorytellerThreat`, `VEF.Storyteller.StorytellerDefExtension`
(`2023507013/1.6/Assemblies/VEF.dll`); `RimWorld.Faction.NaturalGoodwill` /
`.CheckReachNaturalGoodwill` / `.CalculateAdjustedGoodwillChange`,
`RimWorld.GoodwillSituationManager.GetNaturalGoodwill`. 1.6.4871.*

---

### T-116 — `QuestPart_SetFactionHidden` forgets which way it points across a save

`RimWorld.QuestPart_SetFactionHidden` holds `inSignal`, `faction` and `bool hidden`, and on its
signal writes `faction.hidden = hidden`. Its `ExposeData` scribes **`inSignal` and `faction`
only**. After a load, `hidden` is the C# default, `false`.

Vanilla never notices. Its only constructor, `QuestGen_Factions.SetFactionHidden(quest,
faction, hidden = false, …)`, is called only to **reveal**: from `QuestNode_Root_Beggars`,
`_Hospitality_Refugee`, `_ReliquaryPilgrims` and `_Hack_WorshippedTerminal`. A reveal survives a
reload by accident. **A part built with `hidden: true` that is still waiting on its signal
when the game is saved reveals the faction instead.** There is no error, and the
`faction.Hidden != hidden` guard makes the flip look deliberate.

Hide a faction with our own write, or our own part that scribes the flag. Use the vanilla part
only to reveal.

*[#130](https://github.com/cjd721/Rimworld-Archinity/issues/130). `RimWorld.QuestPart_SetFactionHidden.ExposeData`
/ `.Notify_QuestSignalReceived`, `RimWorld.QuestGen.QuestGen_Factions.SetFactionHidden`
(`Assembly-CSharp.dll`). 1.6.4871.*

### T-118 — A faction set in `IncidentParms` is ignored or overwritten by all three caravan encounters

**Setting `parms.faction` and calling `TryExecute` on a vanilla caravan encounter does not choose
who you meet.** The faction is drawn at random in all three, and nothing is logged [V]:

- `IncidentWorker_CaravanMeeting.CanFireNowSub` and `.TryExecuteWorker` both call the private
  `TryFindFaction(out Faction)`. It draws `RandomElement` from every non-player, non-hostile,
  non-hidden, non-temporary humanlike faction with `caravanTraderKinds` and `pawnGroupMakers`.
  **`parms.faction` is never read.**
- `IncidentWorker_Ambush_EnemyFaction.GeneratePawns` (and `.CanFireNowSub`) **assigns**
  `parms.faction` from `PawnGroupMakerUtility.TryGetRandomFactionForCombatPawnGroup(parms.points,
  out parms.faction)`, overwriting the value passed in. The lord, the letter and the attackers all
  use the random one.
- `IncidentWorker_CaravanDemand.TryExecuteWorker` does the same overwrite before it builds the
  demand dialog.

The encounter still fires, and the letter or dialog names a faction, so the result looks
deliberate. Only the faction is wrong.

**Fix:** pin the faction in the vanilla method rather than in the parms. The shipped technique is
Faction Territories': prefixes on `CaravanMeeting.CanFireNowSub` / `.TryExecuteWorker` and
`Ambush_EnemyFaction.GeneratePawns` / `.TryExecuteWorker`, reading a faction held in a per-caravan
scope around `TryExecute` [V]. For the ambush, which opens no dialog, a subclass overriding the
protected `GeneratePawns` also works. **For the meeting and the demand, keep the vanilla method
running** (a replacing prefix, or a patch on `TryFindFaction`), not a subclass overriding
`TryExecuteWorker`: Multiplayer syncs those two dialogs only through a postfix registered on the
vanilla `MethodInfo` (`docs/engine/storyteller-and-incidents.md` § *Caravan encounters*).

*[#136](https://github.com/cjd721/Rimworld-Archinity/issues/136), `docs/specs/POLITICS.md` §
*Settlements meet passing caravans*. `RimWorld.IncidentWorker_CaravanMeeting.TryFindFaction` /
`.CanFireNowSub` / `.TryExecuteWorker`, `RimWorld.IncidentWorker_Ambush_EnemyFaction.GeneratePawns`
/ `.CanFireNowSub`, `RimWorld.IncidentWorker_CaravanDemand.TryExecuteWorker` (`Assembly-CSharp.dll`);
`FactionTerritories.CaravanTerritoryIncidents`,
`FactionTerritories.Patch_AmbushEnemyFaction_GeneratePawns_ForceFaction` from
`294100/3626725895/Assemblies/FactionTerritories.dll`. 1.6.4871.*

### T-119 — A caravan incident never fires in a biome its `mtbDaysByBiome` omits

**Caravan-targeted incidents are rolled per biome, and a biome with no entry is skipped, not
defaulted.** `StorytellerComp_CategoryIndividualMTBByBiome.MakeIntervalIncidents` takes the target
tile's `PrimaryBiome` and runs `incidentDef.mtbDaysByBiome.Find(x => x.biome == biome)`. On `null`
it `continue`s: no roll, no fallback MTB, no log [V]. A def with no `mtbDaysByBiome` at all is
skipped the same way [V]. This comp is the one vanilla storytellers use for the `Caravan` /
`Map_TempIncident` target tags in the Misc, ThreatSmall and ThreatBig categories (`Storytellers.xml`) [V].

**So an authored caravan incident, or a vanilla one such as `CaravanMeeting`, `Ambush` or
`CaravanDemand`, is simply absent from every biome it does not name.** That includes **every biome
a mod adds, and Odyssey's own surface biomes.** `Incidents_Caravan_All.xml` lists only Core
biomes, from `TemperateForest` to `SeaIce`. `Grasslands`, `Glowforest`, `Scarlands`, `GlacialPlain`
and `LavaField` (`Data/Odyssey/Defs/BiomeDefs/`) appear in none of its three caravan encounters.
No DLC or corpus file adds them: the only XML under `Data/` or either mod root that contains
`mtbDaysByBiome` is that Core file and VFE Deserters' own `Incidents_Visibility.xml` [V].
**A caravan crossing an Odyssey grassland meets nobody and is never ambushed**, which reads as a
quiet road, not a fault.

**Fix:** list every biome that should carry the incident, modded ones included, with an XML patch
per biome mod or a generated patch. Otherwise, fire the incident from a comp or trigger of our own
that does not key on biome. A per-biome value of our own is also where frequency balance lives.

*[#136](https://github.com/cjd721/Rimworld-Archinity/issues/136), `docs/specs/POLITICS.md` §
*Settlements meet passing caravans*. `RimWorld.StorytellerComp_CategoryIndividualMTBByBiome.MakeIntervalIncidents`
(`Assembly-CSharp.dll`); `Data/Core/Defs/Storyteller/Incidents_Caravan_All.xml`,
`Data/Core/Defs/Storyteller/Storytellers.xml`. 1.6.4871.*

### T-124 — A shelved offer whose expiry clock has run can be bought for nothing

`Quest.Accept(Pawn)` is `if (State == QuestState.NotYetAccepted) { … }` and **silently does
nothing otherwise** [V]. `Quest.State` is *computed*: it returns `EndedOfferExpired` as soon as
`TicksUntilExpiry == 0 && acceptanceTick < 0`, and `TicksUntilExpiry` derives from
`acceptanceExpireTick`, which `QuestGen.InitializeQuestGen` sets from
`QuestScriptDef.expireDaysRange` **at generation** [V]. So the clock is live on an offer VEF
holds outside `Find.QuestManager` and never ticks (`docs/engine/quests.md` § *Offers*).

`VEF.Storyteller.QuestGiverManager.ActivateQuest` then runs `Add` → `Accept` (**no-op**) →
`SendLetterQuestAvailable` → `currencyInfo?.Buy` → `Remove` [V], and its only guard —
`QuestUtility.CanAcceptQuest`, called from `Window_Contracts.AcceptQuestByInterface` — **does
not test `State`** [V].

**Result: the currency is debited, a "quest available" letter arrives, and no quest is
accepted. Nothing logs.** The player has paid for an entry that was already dead on the shelf,
and the shop's own accounting shows a successful sale.

**Fix:** test `Quest.State == QuestState.NotYetAccepted` in the shop's own affordability and
eligibility guard, or prune expired entries on the tick. Either is cheap; neither is there.

*[#144](https://github.com/cjd721/Rimworld-Archinity/issues/144), `docs/specs/CURRENCIES.md` §
*Shop entries*. `RimWorld.Quest.Accept`, `RimWorld.Quest.State`,
`RimWorld.QuestGen.QuestGen.InitializeQuestGen`, `RimWorld.QuestUtility.CanAcceptQuest`
(`Assembly-CSharp.dll`); `VEF.Storyteller.QuestGiverManager.ActivateQuest`,
`VEF.Storyteller.Window_Contracts.AcceptQuestByInterface` (`2023507013/1.6/Assemblies/VEF.dll`).
1.6.4871.*

### T-125 — Two quest-giver comps sharing a `questManagerID` silently share one shelf

`VEF.CompProperties_QuestGiver.questManagerID` is a **bare `int`** keying
`StorytellerWatcher.questGiverManagers` [V]. There is no uniqueness check and no warning.

Two comps that happen to declare the same id resolve to **one** `QuestGiverManager`, built from
whichever `QuestGiverDef` was used first. The second building opens the first building's shop:
the same catalogue, the same currency, the same stock. Nothing distinguishes it from a shop that
was simply authored that way.

**Fix:** allocate `questManagerID` from one place and assert uniqueness across
`DefDatabase<ThingDef>` at startup. Treat a colliding id as a config error, because the game
will not.

*[#144](https://github.com/cjd721/Rimworld-Archinity/issues/144), `docs/specs/CURRENCIES.md` §
*Shop entries*. `VEF.CompProperties_QuestGiver.questManagerID`,
`VEF.Storyteller.StorytellerWatcher.questGiverManagers`
(`2023507013/1.6/Assemblies/VEF.dll`). 1.6.4871.*

### T-126 — `generateOnce: true` fills the shelf twice

`VEF.Storyteller.StorytellerWatcher.AddQuestGiverManager` fills the shelf, and
`VEF.CompQuestGiver.Use` then calls `Init()`, **filling it a second time** [V]. Nothing dedupes
and nothing logs.

It is harmless only when `maximumAvailableQuestCount` is set, because `QuestWorker.GenerateQuests`
otherwise takes a budget of **100** [V] — so an unbounded giver generates a hundred offers,
throws a hundred generator runs at the storyteller, and then does it again on first use.

**Fix:** set `maximumAvailableQuestCount` on every authored `QuestGiverDef`, and treat
`generateOnce` as meaning "generated at least once", not "generated exactly once".

*[#144](https://github.com/cjd721/Rimworld-Archinity/issues/144), `docs/specs/CURRENCIES.md` §
*Shop entries*. `VEF.Storyteller.StorytellerWatcher.AddQuestGiverManager`,
`VEF.CompQuestGiver.Use`, `VEF.Storyteller.QuestWorker.GenerateQuests`
(`2023507013/1.6/Assemblies/VEF.dll`). 1.6.4871.*

### T-127 — `QuestNode_GetSiteTile`'s early-out guard is typed against the wrong type, so it can never fire

`QuestNode_GetSiteTile.RunInt` guards with `slate.TryGet<int>(storeAs, …)` for a value it stores
as a **`PlanetTile`** [V]. `Verse.ConvertHelper` does not consult implicit operators [V], so the
`int` lookup never matches the `PlanetTile` that is actually there and **the guard can never
fire**.

Two consequences, and only one of them is loud. A caller that pre-sets the key gets a red
*"Could not convert slate variable"* — and its tile is **silently overwritten anyway**. And
because the node always re-derives the tile rather than honouring one it was given,
**`siteDistRange` is measured from a map and never from a caravan**, whatever the XML says. No
def field reaches that decision.

**Fix:** anything that needs a site placed relative to a caravan has to supply the anchor in
C#; there is no XML route. See also **T-49**, which is the other half of how this node loses its
"near the colony" reference.

*[#146](https://github.com/cjd721/Rimworld-Archinity/issues/146), `docs/specs/CHARTING.md`.
`RimWorld.QuestGen.QuestNode_GetSiteTile.RunInt` / `.TryFindTile`, `Verse.ConvertHelper`,
`RimWorld.QuestGen.Slate.TryGet` (`Assembly-CSharp.dll`). 1.6.4871.*

### T-142 — A goodwill refund through `TryAffectGoodwillWith` leaves a net change

A "spend, then refund on failure" pattern calls `TryAffectGoodwillWith(-cost)` and, if the
action fails, `TryAffectGoodwillWith(+cost)`. Both legs pass `CalculateAdjustedGoodwillChange`,
which for a player pair adds 25% of `min(|gap to NaturalGoodwill|, |change|)` to a change moving
**toward** natural goodwill and nothing to one moving away. Either leg, or both, is amplified
depending on where goodwill sits against natural: at natural the spend is not amplified and the
refund is; straddling it, both are. The refund therefore does not cancel the spend, and the
player keeps a net loss or gain with no message saying so. The refund can also be refused
outright by `CanChangeGoodwillFor`. The refund leg usually passes
`canSendMessage: false`.

FT&V ships this shape: `VassaliseUtility` spends `-settlementVassaliseGoodwillCost` and refunds
`+cost` on failure, with `reason: null`. Any positive-gain scaler at the choke point (#160
routes A, A2 and B) skews the refund leg a second time, because a null-reason refund is
indistinguishable from a gain.

**The fix:** restore by a write that bypasses the adjuster, or pre-compensate the refund the way
RimPacts' `Patch_RptGoodwill` does (÷1.25 within the gap), or exempt it from any positive-gain
scaler by authoring it with a dedicated `HistoryEventDef`. Writing "the difference back" through
`TryAffectGoodwillWith` runs the adjuster and the gates again, so it does not restore exactly.

*[#160](https://github.com/cjd721/Rimworld-Archinity/issues/160), `docs/specs/RELIGION.md` §
*Reverence scales the Goodwill a faction gains*. `RimWorld.Faction.TryAffectGoodwillWith`,
`.CalculateAdjustedGoodwillChange`; `3626725895/Assemblies/FactionTerritories.dll`
`FactionTerritories.Vassalise.VassaliseUtility`. 1.6.4871.*

### T-147 — VEF's `GoodwillCurrency` silently offers nothing for a quest with no `asker` on the slate

`VEF.Storyteller.GoodwillCurrency.Allows` reads `slate.Get<Pawn>("asker")`, and returns false with
`questInfo = null` when the asker or its faction is null, or when goodwill is below
`minimunGoodwillRequirement` [V]. The shelf row never appears, and nothing says why. A sibling of
**T-76**.

**Fix:** every quest a goodwill-priced shelf offers must put an `asker` of the shelf's faction on
the slate.

*[#168](https://github.com/cjd721/Rimworld-Archinity/issues/168), `docs/specs/TERRITORY.md` §
*A sworn faction owes services* (OS-4). `VEF.Storyteller.GoodwillCurrency.Allows`
(`2023507013/1.6/Assemblies/VEF.dll`).*

---
