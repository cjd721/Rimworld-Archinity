# Storyteller and incidents

How the storyteller decides *which* incident, *how many*, and *how big* — three
separate mechanisms that are routinely confused for one — and where threat points are
actually composed.

Verified against decompiled RimWorld 1.6.4871 unless an entry says otherwise.
These are *verified available mechanisms*, not commitments to use them —
selection happens in `docs/specs/`.

---

## Selection weight, cadence and points are three different things

Only one of them is what people mean by "more raids", and it is not the one everybody
reaches for [V].

| Question | Mechanism |
|---|---|
| **Which** incident, once a comp has decided to pick one | `StorytellerComp.IncidentChanceFinal` |
| **How many** picks this interval | `IncidentCycleUtility.IncidentCountThisInterval` for the cycle comps; `Rand.MTBEventOccurs` for `StorytellerComp_RandomMain` |
| **How big** the threat is | `StorytellerUtility.DefaultThreatPointsNow` |

`IncidentChanceFinal` is **`protected`**, and it multiplies
`IncidentWorker.BaseChanceThisGame`, the two population factors, the `virtual`
`IncidentWorker.ChanceFactorNow(target)` and the recent-fire decay. **Doubling a
threat def's weight there shifts the mix within a category and changes the raid count
by nothing.** For `StorytellerComp_RandomMain` the category is chosen *first*, by
`categoryWeights`, before any per-def weight applies [V].

## `DefaultThreatPointsNow` is the composition point, and `MapParent` is not

**`RimWorld.Planet.MapParent.PlayerWealthForStoryteller` does not exist in 1.6** [V].
`MapParent : WorldObject, IThingHolder` is not an `IIncidentTarget` at all. The
property is declared on **`RimWorld.IIncidentTarget`** and implemented by `Verse.Map`,
`RimWorld.Planet.Caravan` and `RimWorld.Planet.World`.

Recorded explicitly because a repo draft cited the non-existent member and
[#22](https://github.com/cjd721/Rimworld-Archinity/issues/22) § 1's premise rests on
it. A postfix written against `MapParent` binds nothing.

`PlayerWealthForStoryteller` has at least eight consumers — `PointsPerWealthCurve`,
`PointsPerColonistByWealthCurve`, `PointsFactorForColonyMechsCurve`,
`PointsFactorForColonySubhumanCurve`, `StorytellerUtility.GetProgressScore` (which
gates quests through `QuestScriptDef.rootMinProgressScore`),
`StorytellerComp_OnOffCycle.acceptPercentFactorPerProgressScoreCurve`,
`StorytellerComp_RefiringUniqueQuest.minColonyWealth` and
`StorytellerComp_FactionInteraction.minWealth` [V]. A synthetic number written there
moves all of them invisibly, which is the argument for composing *above* the
aggregation rather than inside it.

## There are two XML-reachable multipliers on threat points, not one

Both are `SimpleCurve`s and both are free [V]:

- **`StorytellerDef.pointsFactorFromDaysPassed`**, evaluated on
  `GenDate.DaysPassedSinceSettle` inside `DefaultThreatPointsNow`. Vanilla's is
  `(10, 0.70) → (40, 1.00)` — a ramp-in and **a no-op after day 40**, so it is unused
  for the whole of a long campaign.
- **`StorytellerDef.pointsFactorFromAdaptDays`**, reaching the same product through
  `StoryWatcher_Adaptation.TotalThreatPointsFactor`.

Any claim that the first is "the only XML-reachable multiplier" is wrong.

## `IncidentCycleUtility.IncidentCountThisInterval` is public

`IncidentCycleUtility` is **not** a static class, but
`IncidentCountThisInterval` is `public static` and takes `acceptFraction` as its last
argument [V] — so campaign-state cadence is reachable from a comp of our own without
touching vanilla's. It is also the safest scheduler under Multiplayer, because its
schedule draws nothing from the shared `Rand` stream [V].

Two things about that method fail silently and are the register's, not this file's:
its per-comp seed salt, and VEF's `forcedPointsRange` sentinel on the authored-raid
path. They are `docs/TRAPS.md` **T-65** and **T-66** — read both before adding a comp
to a `StorytellerDef` or authoring a fixed-size raid.

## `arriveModes` is not optional, and the two paths fail differently

`RaidStrategyDef.arriveModes` has no default and no null guard on the path that consumes it
second, so omitting it produces **two different failures depending on how the strategy was
chosen** [V].

- **Chosen by the storyteller — silent.** `IncidentWorker_RaidEnemy.ResolveRaidStrategy`'s local
  `CanUseStrategy` returns `false` when `parms.raidArrivalMode` is null and `def.arriveModes` is
  null. The strategy is never selected, one of vanilla's nine is picked instead, and nothing is
  logged. That is the register's, not this file's — **`docs/TRAPS.md` T-90**.
- **Pre-set on `parms` — loud.** `PawnsArrivalModeWorker.CanUseWith` evaluates
  `parms.raidStrategy != null && !parms.raidStrategy.arriveModes.Contains(def)` with **no null
  check on the list**, and throws a `NullReferenceException`. This is the path taken by VEF's
  `IncidentWorker_RaidEnemySpecial` reading `IncidentDefExtension.forcedStrategy`, and by
  **T-14**'s second escape — so an authored raid pinning a strategy is precisely the case that
  hits it.

The asymmetry is worth knowing because the loud half is the *good* one: an authored raid tells you
immediately, while a storyteller-selected strategy that quietly never fires can survive a whole
campaign. Both are fixed by the same one line of XML. Every vanilla `RaidStrategyDef` declares
`arriveModes`, which is why the field reads as optional and is not.

*`RimWorld.IncidentWorker_RaidEnemy.ResolveRaidStrategy`,
`RimWorld.PawnsArrivalModeWorker.CanUseWith`, `RimWorld.RaidStrategyDef.arriveModes`.
[#77](https://github.com/cjd721/Rimworld-Archinity/issues/77); the design that uses both paths is
`docs/specs/PRESSURE.md` § *The build* § 8.*

## A live third-party collision on `DefaultThreatPointsNow`

`NCL_Storyteller.Patch_StorytellerUtility` — **Mechanoids: Total Warfare**,
`nyar.nclvstw`, workshop `3555799437` — **transpiles `DefaultThreatPointsNow`**,
injecting an additive term and replacing the hardcoded `10000f` ceiling [V]. Anything
of ours that postfixes the same method composes with a body that is no longer
vanilla's, and the ceiling it assumes may not be there.

## Caravan encounters: the faction is random, and the position is never read

Vanilla stages three encounters on a world-map caravan, defined in
`Core/Defs/Storyteller/Incidents_Caravan_All.xml`: `Ambush` (ThreatBig), `CaravanMeeting` (Misc)
and `CaravanDemand` (ThreatSmall). Each targets `Caravan` and fires by `mtbDaysByBiome` [V].

- **None of them honours `IncidentParms.faction`** [V]:
  - `IncidentWorker_CaravanMeeting.TryFindFaction` draws a random non-player, non-hostile, non-hidden, humanlike faction with `caravanTraderKinds` and `pawnGroupMakers`. Allied and neutral are both eligible, and `parms.faction` is never read.
  - `IncidentWorker_Ambush_EnemyFaction.GeneratePawns` and `IncidentWorker_CaravanDemand.TryExecuteWorker` both **overwrite** `parms.faction` with `PawnGroupMakerUtility.TryGetRandomFactionForCombatPawnGroup`.
  - A faction passed in is therefore discarded silently.
- **None of them reads where the caravan is**, beyond the biome MTB and `CaravanIncidentUtility.CanFireIncidentWhichWantsToGenerateMapAt`. That check refuses a tile holding a map or a world object whose def lacks `allowCaravanIncidentsWhichGenerateMap`. `Settlement` lacks it, so nothing fires on a settlement's own tile [V].
- **`StorytellerComp_CategoryIndividualMTBByBiome` skips any def with no `mtbDaysByBiome` entry for the target's biome** [V]. A biome a def does not list never fires it, and nothing is logged. Vanilla's three caravan encounters list Core biomes only, so they never fire in Odyssey's `Grasslands`, `Glowforest`, `Scarlands`, `GlacialPlain` or `LavaField` (**T-119**). With `applyCaravanVisibility`, the MTB is divided by `Caravan.Visibility`. The roll is `Rand.MTBEventOccurs(mtb, 60000, 1000)`.
- **`Storyteller.AllIncidentTargets` adds every `Find.WorldObjects.Caravans` entry with `IsPlayerControlled`** [V]. Vehicle Framework's `VehicleCaravan : Caravan` is included. Its `AerialVehicleInFlight` is not a `Caravan` and is not included [V].
- **The per-tile movement hook is `Caravan_PathFollower.TryEnterNextPathTile` (private)** [V], called from `PatherTickInterval`. **A Vehicle Framework caravan never runs it.** VF's `Patch_WorldPathing.StartVehicleCaravanPath` prefixes `Caravan_PathFollower.StartPath` and diverts to `VehicleCaravan.vehiclePather`, a sealed `VehicleCaravan_PathFollower` with its own private `TryEnterNextPathTile` [V].
- **Multiplayer syncs the meeting and demand dialogs by method.** `SyncMethods` calls `Sync.RegisterSyncDialogNodeTree` on exactly `IncidentWorker_CaravanMeeting.TryExecuteWorker` and `IncidentWorker_CaravanDemand.TryExecuteWorker`. Registration is a postfix (`SyncUtil.PatchMethodForDialogNodeTreeSync`) on those `MethodInfo`s [V]. A subclass that overrides `TryExecuteWorker` without calling base is outside it [I] (**T-82**, **T-95**). A `Dialog_Trade` constructed inside the synced click becomes an `MpTradeSession` (`DialogTradeCtorPatch`) [V].

*[#136](https://github.com/cjd721/Rimworld-Archinity/issues/136), `docs/specs/POLITICS.md` §
*Settlements meet passing caravans*. `RimWorld.IncidentWorker_CaravanMeeting`,
`RimWorld.IncidentWorker_Ambush` / `_EnemyFaction`, `RimWorld.IncidentWorker_CaravanDemand`,
`RimWorld.Planet.CaravanIncidentUtility`, `RimWorld.StorytellerComp_CategoryIndividualMTBByBiome`,
`RimWorld.Storyteller.AllIncidentTargets`, `RimWorld.Planet.Caravan_PathFollower` —
`Assembly-CSharp.dll` 1.6.4871; `Vehicles.World.VehicleCaravan` / `VehicleCaravan_PathFollower`,
`Vehicles.Patch_WorldPathing.StartVehicleCaravanPath` from `3014915404/1.6/Assemblies/Vehicles.dll`;
`Multiplayer.Client.SyncMethods`, `SyncUtil`, `DialogTradeCtorPatch` from
`2606448745/1.6/AssembliesCustom/Multiplayer.dll`; decompiled 2026-09-16 with `ilspycmd` 8.2.0.*

## `parms.forced` skips the whole def-level gate block in `IncidentWorker.CanFireNow`

`IncidentWorker.CanFireNow(IncidentParms parms)` gates on `parms.forced` before it reaches
any def-level test. Everything in that block is skipped when `forced` is set [V]:
`minThreatPoints` / `maxThreatPoints`, `earliestDay`, `disabledWhen`, `allowBigThreats`,
biomes, `layerWhitelist` / `layerBlacklist`, `onlyAllowWhitelistedIncidents`,
`ScenPart_DisableIncident`, `minPopulation`, `minGreatestPopulation`, `FiredTooRecently`,
the `GameCondition.preventIncidents` quiet window, and the game-ender guards. Only
`CanFireNowSub` is still consulted.

**Everything that fires through `ThreatsGenerator` sets `forced`** [V]. Two consequences
worth carrying: the layer narrowing in **T-48** does not apply to a forced fire, and a
quiet window authored around a beat does not hold against one.

*[#169](https://github.com/cjd721/Rimworld-Archinity/issues/169),
`docs/specs/PRESSURE.md` §7.2. `RimWorld.IncidentWorker.CanFireNow`,
`RimWorld.ThreatsGenerator` — `Assembly-CSharp.dll` 1.6.4871.*

## `IncidentWorker_Raid.AdjustedRaidPoints` is the one seam where the faction and the points coexist

`public static`, called once per raid from `IncidentWorker_RaidEnemy.TryGenerateRaidInfo`
**after** faction and strategy resolution, and once more from
`QuestNode_GenerateThreats` for preview text [V]. Everywhere else the two are apart: the
points are chosen before a faction exists, and the faction is chosen without them.

**Raid loot is generated from the pre-adjustment points** [V] — a scale applied here
changes how hard the raid comes and not what it drops.

*[#169](https://github.com/cjd721/Rimworld-Archinity/issues/169),
`docs/specs/PRESSURE.md`. `RimWorld.IncidentWorker_Raid.AdjustedRaidPoints`,
`RimWorld.IncidentWorker_RaidEnemy.TryGenerateRaidInfo`,
`RimWorld.QuestGen.QuestNode_GenerateThreats` — `Assembly-CSharp.dll` 1.6.4871.*
