# Recon: Rim War (Steam `2222935097`, `Torann.RimWar`, v0.9.9.8)

**Target:** `/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/2222935097/v1.6/Assemblies/RimWar.dll`
**Decompiled to:** `C:/Users/cjd72/AppData/Local/Temp/claude/C--Users-cjd72-Desktop-Personal-Mods-Rimworld-Archinity/6631190b-4577-4393-b6f3-561f901befe1/scratchpad/rimwar`
(80 `.cs` files, 19,677 lines. All file paths below are relative to that root.)

**Assessment date:** 2026-08-24. Only the `v1.6` assembly was read.

---

## 0. Verdict up front

| Question | Answer |
|---|---|
| Does it simulate factions acting on their own? | Yes, genuinely. Settlements accumulate power, spend it to spawn world-map armies/traders/settlers/diplomats that path and resolve. |
| Territory model? | **None.** Zero per-tile ownership. No borders, no overlay, no painted map. |
| MP-safe? | **No. Hard fail.** Two independent, confirmed desync sources. Not fixable by settings alone. |
| Worth harvesting the design? | Yes — the core loop is ~600-800 lines to rebuild and the abstract combat math is ~60. |
| Worth shipping the mod? | **No, not in a Multiplayer co-op save.** |

Three separate reasons it cannot ship, any one of which is disqualifying:

1. **Threaded faction AI consuming global `Rand`**, on by default (§7.1).
2. **`Rand` consumed on the GUI thread** — opening the mod's own tab desyncs the game, and no setting turns this off (§7.2).
3. **~30 Harmony patches** including full-replacement prefixes on `Faction.RelationWith`, `IncidentWorker.TryExecute` (priority 10000) and `WorldPathPool.GetEmptyWorldPath` (§7.3).

There is a fourth, non-MP reason that matters specifically for Archinity: with `restrictEvents` on (**the default**), Rim War **blanket-blocks vanilla `RaidEnemy`, `RaidFriendly` and `TraderCaravanArrival`** (`RimWarMod.cs:984-995`) and becomes the sole source of those events. That is a direct takeover of the storyteller. Archinity's progression design — neolithic start, era-gated tech — would be fighting a system that sizes raids from AI settlement wealth on its own schedule.

---

## 1. What it actually simulates

### Entity types

Two persistent state carriers plus a family of transient world objects.

**A. `RimWarData`** — one per faction, `IExposable`, saved in the WorldComponent.
`RimWar/RimWarData.cs:9`. State it carries:

- `behavior` — enum `RimWarBehavior`: `Undefined, Player, Vassal, Excluded, Random, Aggressive, Cautious, Expansionist, Merchant, Warmonger`
- Six action weights, stored as **cumulative thresholds**: `settlerChance, warbandChance, scoutChance, warbandLaunchChance, diplomatChance, caravanChance`
- Three multipliers: `movementAttribute, combatAttribute, growthAttribute` (each rolled `Rand.Range(0.75f, 1.25f)` at faction init if `randomizeAttributes`)
- `createsSettlements`, `hatesPlayer`, `movesAtNight`, `capitolTile`
- `warFactions`, `allianceFactions` — explicit war/alliance lists, saved
- Derived-and-cached: `PointsFromSettlements`, `PointsFromWarObjects`, `PointsFromWorldObjects`, `TotalFactionPoints`

**B. `RimWarSettlementComp`** — a `WorldObjectComp` patched onto *every* `Settlement` def (and `Cities.City`, `FactionColonies.WorldSettlementFC` if present) via `v1.6/Patches/RimWarCompsx.xml`. This is the resource model. State:

- `RimWarPoints` — the single currency. Settlements grow it, spend it to spawn units, lose it when attacked.
- `PointDamage` — combat damage, regenerates over time
- `PlayerHeat` / `vassalHeat` — accumulating aggression counter that gates whether the faction may act against the player
- `isCapitol`, `bonusGrowthCount`, `nextEventTick`, `nextSettlementScan`, `lastReinforcementTick`
- `SettlementPointGains` — a delayed-reward queue
- `settlementsInRange` cache + a **`System.Threading.Mutex`** (`RimWarSettlementComp.cs:54`)

**C. World objects** (`v1.6/Defs/WorldObjectDefs/RW_WorldObjects.xml`), all subclasses of `WarObject : WorldObject`:

`RW_Warband`, `RW_LaunchedWarband`, `RW_Scout`, `RW_Settler`, `RW_Trader`, `RW_Diplomat`, `RW_WarObject`, `RW_LaunchedWarObject`, `RW_Warband_Caravan`, `RW_BattleSite`, `RW_Site`, `RW_CapitolBuilding`.

Each `WarObject` carries `RimWarPoints`, `PointDamage`, `parentSettlement`, `targetWorldObject`, a `WarObject_PathFollower` (custom world pather, saved deep), a tweener, and a `List<Pawn>` for when it materializes.

### So: settlements, armies, trade caravans, resources — yes. Territory — no.

Resources are a single scalar (`RimWarPoints`) per settlement. There is no goods model, no stockpile, no production chain. Trade is `Trader` objects moving points between settlements (`IncidentUtility.ResolveSettlementTrade`, `IncidentUtility.cs:183`).

---

## 2. The tick loop

One driver: **`WorldComponent_PowerTracker.WorldComponentTick()`**, `RimWar.Planet/WorldComponent_PowerTracker.cs:196`. It runs every world tick. Cadences:

| Interval | Work |
|---|---|
| every tick | `WorldUtility.CopyData()` — reassigns the static world-object list |
| `% 60` | `AdjustCaravanTargets()` — re-path player caravans that are being chased |
| `% heatFrequency` (3000) | `UpdatePlayerAggression()` — decay the global player-action gate |
| `% rwdUpdateFrequency` (2500) | `CheckForNewFactions()` then `UpdateFactions()` (**threaded by default**) + victory check |
| `% 60000` (one in-game day) | `DoGlobalRWDAction()` — a free global action for one random faction |
| `>= nextEvaluationTick` (avg 150 ticks, jittered) | **the main faction-action loop** |

### The main loop (lines 255–370)

```csharp
if (ticksGame >= nextEvaluationTick)
{
    nextEvaluationTick = ticksGame + Rand.Range((int)(settingsRef.averageEventFrequency * 0.5f),
                                                (int)(settingsRef.averageEventFrequency * 1.5f));
    RimWarData rimWarData = GenCollection.RandomElement<RimWarData>(Active_RWD);
    Settlement val = GenCollection.RandomElement<Settlement>(rimWarData.WorldSettlements);
    ...
```
— `WorldComponent_PowerTracker.cs:255-263`

**This is the crux of the whole mod, and it is not a scan.** Every ~150 ticks it picks **one random faction**, then **one random settlement of that faction**, and asks *that settlement* whether it wants to do something. It never iterates all settlements. The per-settlement cooldown is `settlementEventDelay = 50000` ticks (~0.83 in-game days), halved-ish for capitols:

```csharp
if (component.isCapitol)
    component.nextEventTick = ticksGame + Mathf.RoundToInt((float)settingsRef.settlementEventDelay / 1.5f);
else
    component.nextEventTick = ticksGame + settingsRef.settlementEventDelay;
```
— `WorldComponent_PowerTracker.cs:352-359`

Also gated on night: a `movesAtNight` faction only acts while `CaravanNightRestUtility.RestingNowAt` is true at the settlement's tile, and vice versa (`:273`).

`UpdateFactions()` (`:726`) is the growth pass — it does iterate everything:

```csharp
public void UpdateFactions()
{
    IncrementSettlementGrowth();
    ReconstituteSettlements();
    UpdateFactionSettlements(GenCollection.RandomElement<RimWarData>(RimWarData));
}
```

`IncrementSettlementGrowth()` (`:733`) walks **every faction × every settlement** and adds points scaled by biome, tech level, `growthAttribute` and a `Rand.Range(2f, 3f)` roll, plus `PlayerHeat += Rand.Range(1, 3)`.

### Per-object ticks

`WarObject.TickInterval(int delta)` — `RimWar.Planet/WarObject.cs:444`:

- every `1001` ticks: regenerate `PointDamage` with `Rand.Range(0.004f, 0.006f)`
- every `Rand.Range(180, 300)` ticks (`WarObject.cs:138`): `ScanAction(ScanRange)` — look for things to fight/trade with
- every `(TicksGame + ID) % 251`: `ValidateTargets()` (ID-staggered, so this part is well behaved)
- every `woEventFrequency` (200) ticks: `pather.PatherTick(delta)` — actual movement

`RimWarSettlementComp.CompTick()` — `RimWarSettlementComp.cs:523` — every `2500` ticks, resolve combat against any `AttackingUnits`.

---

## 3. How a faction decides

**Weighted random over six actions. No utility scoring, no state machine, no planning.**

```csharp
public RimWarAction GetWeightedSettlementAction()
{
    float value = Rand.Value;
    if (value <= settlerChance)        return RimWarAction.Settler;
    if (value <= warbandChance)        return RimWarAction.Warband;
    if (value <= scoutChance)          return RimWarAction.ScoutingParty;
    if (value <= warbandLaunchChance)  return RimWarAction.LaunchedWarband;
    if (value <= diplomatChance)       return RimWarAction.Diplomat;
    if (value <= caravanChance)        return RimWarAction.Caravan;
    return RimWarAction.None;
}
```
— `RimWar/RimWarData.cs:562`

The `*Chance` fields are cumulative CDF thresholds, built once per faction at init from an integer weight table keyed on `behavior`:

```csharp
num7 = num + num2 + num3 + num4 + num5 + num6;
rimwarObject.settlerChance       = num / num7;
rimwarObject.warbandChance       = (num + num2) / num7;
rimwarObject.scoutChance         = (num + num2 + num3) / num7;
rimwarObject.warbandLaunchChance = (num + num2 + num3 + num4) / num7;
rimwarObject.diplomatChance      = (num + num2 + num3 + num4 + num5) / num7;
rimwarObject.caravanChance       = (num + num2 + num3 + num4 + num5 + num6) / num7;
```
— `RimWar.Planet/WorldUtility.cs:995-1001`

Weight table (`WorldUtility.CalculateFactionBehaviorWeights`, `:880-1002`), as `settler / warband / scout / launched / diplomat / caravan`:

| behavior | settler | warband | scout | launched | diplomat | caravan |
|---|---|---|---|---|---|---|
| Random | 1 | 3 | 4 | 2 | 1 | 3 |
| Aggressive | 2 | 4 | 4 | 4 | 1 | 5 |
| Cautious | 2 | 2 | 4 | 3 | 2 | 5 |
| Expansionist | 3 | 3 | 3 | 1 | 2 | 4 |
| Merchant | 2 | 3 | 3 | 1 | 2 | 6 |
| Warmonger | 3 | 7 | 4 | 5 | 0 | 5 |

(`settler` weight is zeroed if `!createsSettlements`; `launched` is zeroed if `techLevel < Industrial`; `diplomat` is zeroed unless the `createDiplomats` setting is on — off by default.)

**The one bit of "intent"**, and it is a bug-shaped hack: if the faction is at war, reroll once, biased toward military actions.

```csharp
RimWarAction weightedSettlementAction = rimWarData.GetWeightedSettlementAction();
if (rimWarData.IsAtWar && weightedSettlementAction != RimWarAction.LaunchedWarband
    && weightedSettlementAction != RimWarAction.ScoutingParty && weightedSettlementAction != RimWarAction.Warband)
{
    weightedSettlementAction = rimWarData.GetWeightedSettlementAction();   // reroll, keep whatever comes up
}
```
— `WorldComponent_PowerTracker.cs:280-284`

The reroll doesn't filter — it just rolls again and accepts anything, military or not. Single reroll, no loop.

### The actual gating is downstream, in the `Attempt*` methods

The interesting logic isn't in the choice, it's in whether the chosen action can be *afforded and justified*. `AttemptWarbandActionAgainstTown_UnThreaded` (`WorldComponent_PowerTracker.cs:1150`) is representative:

1. Build a candidate list — `rwsComp.NearbyHostileSettlements` (distance-filtered, capped at 20)
2. If at war, append the nearest same-faction settlement and inflate scan range ×1.5
3. `GenCollection.RandomElement` one target from the list
4. Reject if outside `SettlementScanRange`
5. Reject if target is player and `preventActionsAgainstPlayerUntilTick > TicksGame` (grace period, `90000 / threatScale` ticks)
6. Reject if target is player and `rwsComp.PlayerHeat < minimumHeatForPlayerAction` — **the escalation gate**
7. Size the force: `WorldUtility.CalculateWarbandPointsForRaid(targetComp)`, ×1.1 if Cautious, ×1.25 if Warmonger, ×1.2 more if formally at war
8. **Affordability check** — spawn only if `rwsComp.RimWarPoints * 0.75f >= num2` (0.85 if at war). This is the one real feedback loop: weak settlements physically cannot raid strong ones.
9. On spawn: `rwsComp.RimWarPoints -= num2`, reset `PlayerHeat = 0`, and raise the global `minimumHeatForPlayerAction`

So the "AI" is: **random action → random target → affordability + heat gate**. It is a slot machine with a budget, not a planner. But the budget is what makes it feel alive: settlements that keep losing armies stop being able to send them.

### Reinforcement (`:293-309`)

Only genuinely cooperative behavior in the mod: a damaged settlement asks a nearby friendly settlement with `RimWarPoints > 1000` for help, first-match wins.

### Global daily action (`DoGlobalRWDAction`, `:476`)

Once per in-game day, one random faction gets a free action. Note `Settler` and `Warband` here mean **diplomacy**, not units: `Settler` → `TryAffectGoodwillWith(randomOtherFaction, Rand.Range(0, 20))`, `Warband` → `TryAffectGoodwillWith(randomOtherFaction, Rand.Range(-20, 0))`. That is how inter-faction relations drift over a campaign.

---

## 4. Territory — there is none

Confirmed by exhaustive grep: `territor|border|claim|ownedtile|tileowner|influence` → **zero hits across all 80 files**. No `WorldLayer` subclass, no `SetTileColor`, no tile-mesh code, no `WorldComponentUpdate` override anywhere in the mod.

`WorldComponent_PowerTracker` overrides exactly two methods: `ExposeData` (`:168`) and `WorldComponentTick` (`:196`). No rendering.

The closest analogue is a **scalar radius recomputed on demand**:

```csharp
public int SettlementScanRange => Mathf.RoundToInt(Mathf.Clamp(
    (0.4f * (float)RimWarPoints + 1400f) / Settings.Instance.settlementScanRangeDivider,
    10f, Settings.Instance.maxSettlementScanRange));
```
— `RimWar.Planet/RimWarSettlementComp.cs:152`

Defaults: `settlementScanRangeDivider = 70`, `maxSettlementScanRange = 75`. So a 0-point settlement reaches 20 tiles; anything above ~9,000 points is clamped at 75.

Everything downstream (`NearbyHostileSettlements` `:331`, `NearbyFriendlySettlements` `:403`, `GetWorldObjectsInRange` `WorldUtility.cs:1292`) is a live `Find.WorldGrid.ApproxDistanceInTiles` filter. No tile set is ever materialized or persisted. `RimWarData.ExposeData` (`RimWarData.cs:411`) saves no tiles beyond a single `capitolTile` int.

### The entire visual footprint

1. War objects as faction-colored icons (`WarObject.Material`, `WarObject.cs:263`)
2. Two badge icons drawn on settlements — capitol star, under-attack marker — via a Harmony postfix on `WorldSelectionDrawer.DrawSelectionOverlays` (`RimWar.Harmony/RimWarMod.cs:264`, impl `:614 WorldCapitolOverlay`)
3. A vanilla `GenDraw.DrawWorldRadiusRing` when a settlement is selected (`RimWarSettlementComp.cs:899`)
4. A UI main-tab (`RimWar/MainTabWindow_RimWar.cs`) with three tabs: Relations (a data table), Events (a log archive), Performance (a history graph). Note `DoRelationsContent()` at `:135` has an **empty body**.

The `Textures/World/` folder holds 28 files, all world-object sprites and badges. No border texture, no hex fill, no overlay atlas.

**Implication for Archinity: a territory layer is fully greenfield.** Rim War provides no prior art, and its distance queries are not a usable spatial index — see §6.

---

## 5. Does the player's map get involved?

**Both, and the split is clean.** AI-vs-AI is pure abstract math. The moment the player is a participant, it converts to a real generated map with real pawns. And the conversion runs *both directions* — abstract damage becomes real injuries, real pawn deaths become abstract point loss.

### The routing decision — one function, three branches

`IncidentUtility.ResolveRimWarBattle` (`RimWar.Planet/IncidentUtility.cs:56`) is the exact line where "abstract or real" is decided:

```csharp
if (flag)   // a Settlement exists at this tile
{
    if (((WorldObjectComp)rimWarSettlementComp).parent.Faction == Faction.OfPlayer)
    {
        foreach (WarObject item2 in list)
            DoRaidWithPoints(item2, (Settlement)parent, item2.rimwarData,
                             PawnsArrivalModeDefOf.EdgeWalkIn);      // :96  REAL RAID, one per unit
    }
    else
    {
        rimWarSettlementComp.AttackingUnits.AddRange(list);          // :101 abstract siege
        rimWarSettlementComp.nextCombatTick = Find.TickManager.TicksGame + 2500;
    }
}
else
{
    CreateNewBattleSite(((WorldObject)defender).Tile, list);         // :107 abstract battle site
}
```

Note the player branch spawns a **separate simultaneous raid per war object present** — these can stack.

### Abstract (AI vs. AI) — pure math

```csharp
public static void ResolveCombat_Units(WarObject attacker, WarObject defender)
{
    float num = 200f;
    if (attacker.RimWarPoints > 20000)     num = 4000f;
    else if (attacker.RimWarPoints > 5000) num = 2000f;
    else if (attacker.RimWarPoints > 1000) num = 500f;
    float num2 = Mathf.Clamp((float)defender.EffectivePoints, 0f, num);
    float num3 = Mathf.Clamp((float)attacker.EffectivePoints, 0f, num);
    float num4 = Rand.Value * num3 * attacker.rimwarData.combatAttribute;
    float num5 = Rand.Value * num2 * defender.rimwarData.combatAttribute;
    float num6 = Rand.Range(0.5f, 0.7f);
    float num7 = Rand.Range(0.5f, 0.7f);
    ... // shift num6/num7 by the ratio of num4:num5
    attacker.PointDamage += Mathf.RoundToInt(num * num6);
    defender.PointDamage += Mathf.RoundToInt(num * num7);
}
```
— `IncidentUtility.cs:1035`

Four `Rand` draws, no map, no pawns, zero dependencies. **The single most portable piece of the mod.** Driven from `BattleSite.Tick()` (`RimWar.Planet/BattleSite.cs:52`) on a 2500-tick combat round, and explicitly gated:

```csharp
if (!((MapParent)this).HasMap)                       // BattleSite.cs:60 — abstract only while no map
{ ... IncidentUtility.ResolveCombat_Units(...); if (!flag) IncidentUtility.ResolveBattle_Units(this); }
else
{ IncidentUtility.UpdateUnitCombatStatus(base.Units); }   // real pawns now drive the numbers
```

Siblings: `ResolveCombat_Settlement` (`:782`, adds `if (defender.isCapitol) num5 *= 1.15f`), `ResolveBattle_Settlement` (`:850`, handles capture via `WorldUtility.ConvertSettlement` `:932`, sack, or raze), `ResolveBattle_Units` (`:1095`, re-spawns survivors as world objects and destroys the battle site). Settlement sieges tick from `RimWarSettlementComp.CompTick()` (`:523`), same `ParentHasMap` gate.

### Against the player — a genuine vanilla raid

`Warband.ArrivalAction()` (`RimWar.Planet/Warband.cs:172`) → `IncidentUtility.DoRaidWithPoints` (`:253`):

```csharp
val.faction = rwd.RimWarFaction;
val.generateFightersOnly = true;
val.raidArrivalMode = arrivalMode;
val.target = (IIncidentTarget)((MapParent)playerSettlement).Map;     // :281
val.points = (float)wo.RimWarPoints * rwd.combatAttribute;
val = ResolveRaidStrategy(val, val2);
val.points = AdjustedRaidPoints(wo.RimWarPoints, val.raidArrivalMode, val.raidStrategy, ...);
if (WorldUtility.FactionCanFight((int)val.points, val.faction))
{
    IncidentWorker_WarObjectRaid incidentWorker_WarObjectRaid = new IncidentWorker_WarObjectRaid();
    incidentWorker_WarObjectRaid.TryExecuteCustomWorker(val, val2);   // :290
```

`IncidentWorker_WarObjectRaid : IncidentWorker_Raid` (`RimWar.Utility/IncidentWorker_WarObjectRaid.cs:10`) reimplements vanilla raid execution at `:61-135` — `TryGenerateThreats`, `TryResolveRaidSpawnCenter`, `PawnGroupMakerUtility.GeneratePawns`, `MakeLords`. **A warband's raid strength is its home settlement's accumulated `RimWarPoints`.** That is the mod's actual selling point.

Non-hostile factions get `DoReinforcementWithPoints` (`:326`) → vanilla `IncidentWorker_RaidFriendly` with `RaidStrategyDefOf.ImmediateAttackFriendly` — real allied pawns spawn on your map.

Failure fallback (`:307-316`): if the raid throws, points are refunded abstractly into a random faction settlement via `ConsolidatePoints`.

### The abstract ↔ concrete bridge (both directions)

- **Abstract → real:** `InflictPointDamageToPawnGroup` (`:1368`) converts accumulated `PointDamage` from prior world-map skirmishes into real `RimWarDefOf.RW_CombatInjury` damage on the spawned pawns *before they act* (`IncidentWorker_WarObjectRaid.cs:120-130`). A warband you bled on the world map arrives wounded.
- **Real → abstract:** `UpdateUnitCombatStatus` (`:1391`) converts real pawn deaths and health back into `RimWarPoints`/`PointDamage`. `ExitMapPostBattle_Prefix` (`RimWarMod.cs:298`) counts survivors per attacking `WarObject`, prunes wiped or ≤25%-strength ones, and grants +25..35 goodwill if a siege is broken.

**This bidirectional bridge is the design idea worth stealing.** It is what makes world-map events feel consequential rather than cosmetic.

### The player can force any abstract battle onto a real map

`BattleSite` is a `MapParent` (`RimWarSite : MapParent`, `RimWarSite.cs:15`) with an attack gizmo (`BattleSite.cs:148`). `AttackBattleSiteNow` (`IncidentUtility.cs:1180`):

```csharp
Map orGenerateMap = GetOrGenerateMapUtility.GetOrGenerateMap(((WorldObject)bs).Tile, null, null);
Find.TickManager.Notify_GeneratedPotentiallyHostileMap();
CaravanEnterMapUtility.Enter(car, orGenerateMap, (CaravanEnterMode)1, (CaravanDropInventoryMode)0, true, null);
GenerateSiteUnits(bs, orGenerateMap);   // :1235 — materializes BOTH AI armies as pawns
```

So you can walk into a three-way fight between two AI factions. Also reachable by drop pod (`TransportPodsArrivalAction_JoinBattle.cs:98`), shuttle (`TransportPodsArrivalAction_Shuttle_JoinBattle.cs:86`), and caravan (`CaravanArrivalAction_JoinBattle.cs:82`). Attacking a lone war party: `CaravanArrivalAction_AttackWarObject` → `WarObject.EngageCaravan` (`WarObject.cs:661`) → `DoCaravanAttackWithPoints` (`:389`) → `CaravanIncidentUtility.SetupCaravanAttackMap` (`:453`) + `LordJob_AssaultColony` (`:463`).

You can also **reinforce a besieged ally**: `RimWarSettlementComp.GetCaravanGizmos` (`:681`) sets `preventRelationChange = true` and calls vanilla `SettlementUtility.Attack`, with the relations penalty suppressed by the `AffectRelationsOnAttacked` prefix.

### Pawn generation — 6 sites, all via `PawnGroupMakerUtility.GeneratePawns`

No direct `PawnGenerator.GeneratePawn` calls anywhere. Core site is `GeneratePawnGroup` (`IncidentUtility.cs:1285-1366`): generates, `GenSpawn.Spawn` into `GenRadial.RadialCellsAround(near, 20f, true)`, assigns `LordJob_DefendPoint` or `LordJob_AssaultColony`, and **rewrites the morale trigger** so Rim War armies fight past vanilla break points:

```csharp
val.Graph.transitions[i].triggers[j] = new Trigger_FractionPawnsLost(Rand.Range(0.8f, 1f));   // :1360
```

Other sites: `DoCaravanAttackWithPoints` (`:447`), `IncidentWorker_WarObjectRaid.cs:82`, `IncidentWorker_WarObjectDemand.cs:150`, `IncidentWorker_WarObjectMeeting.cs:249`, and `WorldUtility.CreateWarband_Caravan` (`:332`) — the last means **some AI armies exist as real pawn-holding `Caravan` subclasses, not abstractions.**

---

## 6. Performance

### Entity scale

- Settlements: `maxFactionSettlements = 40` **per faction**. At default 0.12 planet coverage with ~8 factions, expect 60–200 settlements. Every one carries a `RimWarSettlementComp` **and a `Mutex`**.
- War objects: no global cap. Governed by `settlementEventDelay = 50000` ticks per settlement, so steady state is roughly `settlements × (60000/50000)` spawns per day, minus affordability rejections. INFERRED: tens of live war objects mid-game, low hundreds late.

### The main loop is cheap

Only one settlement is evaluated per ~150 ticks. That is genuinely light — a deliberate design choice and a good one.

### The expensive parts

**(a) `GetWorldObjectsInRange` shuffles the entire world-object list to return 5 items.**

```csharp
List<WorldObject> list3 = GenCollection.InRandomOrder<WorldObject>(list, null).ToList();
for (int i = 0; i < list3.Count; i++)
{
    PlanetTile tile = list3[i].Tile;
    if (list2.Count >= 5) break;
    ...
}
```
— `RimWar.Planet/WorldUtility.cs:1312-1320`

A full Fisher-Yates + `ToList()` allocation over *every world object on the planet*, then take at most 5. Every `WarObject` calls this every `Rand.Range(180,300)` ticks via `ScanAction` (`WarObject.cs:466-468`). With `W` war objects and `N` world objects that is **O(W·N) shuffles and allocations** on a ~240-tick cadence. This is the O(n²) you asked about, and it is also a `Rand` consumption proportional to `N`.

Same function backs `GetRimWorldSettlementsInRange` (`:1057`), `GetHostileSettlementsInRange` (`:1194`), `GetHostileWarbandsInRange` (`:1385`), `GetHostileWarObjectsInRange` (`:1404`).

**(b) `WarSettlementComps` has no cache and rebuilds on every access.**

```csharp
public List<RimWarSettlementComp> WarSettlementComps
{
    get
    {
        if (warSettlementComps == null) warSettlementComps = new List<RimWarSettlementComp>();
        warSettlementComps.Clear();
        for (int i = 0; i < WorldSettlements.Count; i++) { ... GetComponent<RimWarSettlementComp>() ... }
        return warSettlementComps;
    }
}
```
— `RimWar/RimWarData.cs:168`

And `WorldSettlements` (`:139`) itself, when its ~175-tick cache expires, scans `Find.WorldObjects.AllWorldObjects` in full. `AllRimWarSettlements` (`WorldComponent_PowerTracker.cs:109`) calls `WarSettlementComps` for every faction — a full rebuild each time.

`AssignRWDCapitol` (`RimWarData.cs:442`) calls the `WarSettlementComps` property **inside a loop condition and 6 more times in the body** — each access re-does the whole rebuild. `ClosestSettlementTo` (`:478`) does the same, ~8 property accesses per iteration inside a `for` loop over that very property. Those are quadratic in settlements-per-faction.

**(c) Mutex-per-settlement.** `RimWarSettlementComp.cs:54, :520`. 100+ kernel sync objects for a design that doesn't need them.

**(d) `WorldCapitolOverlay` iterates every settlement every frame.** A Harmony postfix on `WorldSelectionDrawer.DrawSelectionOverlays` (`RimWarMod.cs:264`, impl `:614`) walks `Find.WorldObjects.Settlements` in full, calls `GetComponent<RimWarSettlementComp>()` on each, and checks `isCapitol` / `UnderAttack` — every rendered frame the world map is open. With 200 settlements that is 200 `GetComponent` lookups at 60fps.

**(e) `WorldUtility.CopyData()` runs every single world tick** (`WorldComponent_PowerTracker.cs:202`) — trivial (one reference assignment) but pointless at 60Hz.

Overall: playable, but the scanning is sloppy and gets worse with planet size. Reported community experience of late-game slowdown is consistent with (a) and (b). *(INFERRED — not measured.)*

---

## 7. MP determinism verdict — **HARD FAIL**

`grep -rn "Multiplayer|Zetrith|MP\.API|SyncMethod"` → **zero hits.** No Multiplayer integration of any kind.

There are **two independent, confirmed desync sources.** Either alone is fatal. They are not the same problem and disabling one does not fix the other.

### Desync source #1 — the faction AI runs on background threads, by default

The mod ships its own thread pool, `RimWar.RocketTools/RocketTasker.cs`:

```csharp
public RocketTask(Func<T> threaded, Action<T> nonThreaded)
{
    this.threaded = threaded;
    this.nonThreaded = nonThreaded;
    threadStart = RunOffMainThread;
    thread = new Thread(threadStart);          // RocketTasker.cs:64
}
```

and the world component registers the faction update into it:

```csharp
if (ticksGame % settingsRef.rwdUpdateFrequency == 0)
{
    CheckForNewFactions();
    if (Settings.Instance.threadingEnabled)
    {
        tasker.Register(delegate
        {
            UpdateFactions();                                  // <-- ENTIRE FACTION AI, OFF-THREAD
            if (settingsRef.useRimWarVictory && !victoryDeclared && rwdInitVictory)
                CheckVictoryConditions();
            return (ContextStorage)null;
        }, delegate { });
    }
    else { UpdateFactions(); ... }
}
```
— `WorldComponent_PowerTracker.cs:225-249`

`UpdateFactions()` → `IncrementSettlementGrowth()` → `Rand.Range(2f, 3f)`, `Rand.Range(1, 3)`, `Rand.Range(0.005f, 0.01f)`, `Rand.RangeInclusive(1, 3)` — **all consuming the shared global `Verse.Rand` state from a non-main thread** (`:784`, `:790`, `:801`, `:804`, `:809`).

**`threadingEnabled` defaults to `true`** — `RimWar.Options/Settings.cs:40`.

Same pattern in three more places:
- `AttemptSettlerMission` (`WorldComponent_PowerTracker.cs:1936`) and `AttemptTradeMission` (`:2227`) register threaded tasks
- `RimWarSettlementComp.OtherSettlementsInRange` (`:288-302`) — a **property getter** that spawns a background task calling `GetRimWorldSettlementsInRange`, which shuffles the world-object list under `Rand`
- `WarObject.TickInterval` (`:469-475`) registers a `Notify_Player()` task per war object per scan

The author knew: `Mutex settlementsMutex` (`RimWarSettlementComp.cs:54`), six `lock (locker)` blocks in `WorldUtility.cs` (`:1274, 1305, 1349, 1432, 1458, 1537`), `MainthreadID = Thread.CurrentThread.ManagedThreadId` captured in three places. **None of that helps.** Thread-safety is not determinism. Two clients running the same tick will interleave `Rand` consumption between main and worker threads in different orders, producing different values from the same seed. Guaranteed divergence, usually within minutes.

Concurrency is capped at 4 (`RocketTasker.cs:69, actionCounter <= 4`) and there is a 15ms `Thread.Sleep` bail-out with `thread.Interrupt()` (`:197-217`) — wall-clock-dependent, so *whether a task even completes this tick* depends on each machine's speed.

### Desync source #2 — `Rand` on the GUI thread, ungated by any setting

Opening the Rim War main tab consumes global `Rand` draws. `MainTabWindow_RimWar.DoWindowContents` (`:110`) → `RimWarFactionUtility.DoWindowContents` (`:142`) → per faction, per frame:

```csharp
int num = rimWarDataForFaction.TotalFactionPoints / 10;
```
— `RimWar/RimWarFactionUtility.cs:211`

and again in the label string at `RimWarFactionUtility.cs:256`. `TotalFactionPoints` (`RimWarData.cs:384`) is `PointsFromSettlements + PointsFromWarObjects + PointsFromWorldObjects`, and each of those three is a lazily-refreshing property whose **cache-expiry stamp is itself a `Rand` roll**:

```csharp
public int PointsFromSettlements
{
    get
    {
        if (pointsFromSettlementsTickHash < Find.TickManager.TicksGame)
        {
            pointsFromSettlementsTickHash = Find.TickManager.TicksGame + Rand.Range(300, 310);   // <-- GUI THREAD
            ...
```
— `RimWar/RimWarData.cs:207-223` (siblings at `:225` and `:242`, using `Rand.Range(300,310)` and `Rand.Range(600,610)`)

Plus `WorldSettlements` (`RimWarData.cs:143-145`) → `GetNextUpdateTick` → `Rand.Range(150, 200)` (`:87`), also reachable from the same GUI path.

**Consequence:** if player A has the Rim War tab open and player B does not, A's client draws extra values from the shared `Rand` stream that B's does not. The simulations diverge from that moment. Merely *looking at the UI* desyncs the game. This is not settings-gated and cannot be turned off.

### Lesser issues (real, but secondary)

- **Wall-clock in the tick path.** `Stopwatch` at `WorldComponent_PowerTracker.cs:1937, 1949, 2228, 2240` and `RocketTasker.cs:199` — only logging in the first four, but `RocketTasker.Await` uses elapsed ms to decide whether to kill a task.
- **Per-client cached state.** `WorldUtility.wcpt` (`:20`), `factionCount` (`:30`), `_worldObjectsHolder`, `RimWarFactionUtility.hashSilver` (`:32`) which reads `Find.AnyPlayerHomeMap` — ambiguous with two colonies.
- **Direct `Settings.Instance` reads inside the tick loop** (`:221, 225, 228, 371`, and `new SettingsRef()` on every tick at `:201`). Both players must have byte-identical `config/ModSettings/`, which the project already knows to watch (`CLAUDE.md` §Multiplayer). Here the exposure is unusually wide: `averageEventFrequency`, `settlementEventDelay`, `rwdUpdateFrequency`, `settlementGrowthRate`, `maxFactionSettlements`, `heatFrequency`, `objectMovementMultiplier`, `woEventFrequency`, `settlementScanDelay`, `maxSettlementScanRange`, `settlementScanRangeDivider` all feed the simulation directly.
- **`Faction.randomKey` as the identity key** everywhere (`RimWarData.RandomKey`, `:332`; `CheckForRimWarFaction`, `:877`). Fine if world gen is synced, but it is another shared-state assumption.
- **A non-reentrant static used across map generation.** `GenStep_Settlement.ScatterAt` prefix stashes `settlementGenPoints` into a **static field** (`RimWarMod.cs:192`, patch at `:325`) which the `SymbolStack.Push` prefix (`:319`) then reads to override `pawnGroupMakerParams.points`. Two map generations overlapping — or a background task interleaving — corrupts it silently.

### Desync source #3 (adjacent) — the Harmony surface is far larger than it looks

`RimWar.Harmony/RimWarMod.cs` applies **~30 patches**: 7 attribute-based via `PatchAll()` (`:337`) plus 23 manual `val.Patch(...)` calls (`:245-336`), under Harmony ID `rimworld.torann.rimwar`. Several are not decorations — they are **replacements of vanilla methods**, which is where Multiplayer's own patches live:

| Target | Type | Risk |
|---|---|---|
| `Faction.RelationWith` (`:64-88`) | Prefix, **always returns false — full replacement** | Reimplements a very hot vanilla method. Any other mod's patch on it is bypassed. |
| `IncidentWorker.TryExecute` (`:290`) | Prefix, `[HarmonyPriority(10000)]` | Patches **the base of every incident in the game at maximum priority.** Largest single compat surface in the mod. |
| `WorldPathPool.GetEmptyWorldPath` (`:332`) | Prefix, **returns false — full replacement** | Reimplements path pooling, with a self-described leak workaround ("WorldPathPool leak … Force-recovering"). |
| `FactionDialogMaker.CallForAid` (`:314`) | Prefix, **returns false — replaces vanilla** | Substitutes Rim War warband spawning for vanilla military aid. |
| `IncidentQueue.Add` (`:307`) | Prefix, **can skip** | Matches a queued `TraderCaravanArrival` by the **magic number `+120000` ticks** and replaces it. Brittle. |
| `SettlementDefeatUtility.IsDefeated` (`:21`) | Prefix, can skip | Forces `false` under Rim War conditions. |
| `IncidentWorker_Ambush_EnemyFaction` / `_CaravanDemand` / `_CaravanMeeting` / `_PawnsArrive` `.CanFireNowSub` (`:333-336`) | Prefix, can force false | With `restrictEvents` (**default on**) blanket-blocks `RaidEnemy`, `RaidFriendly`, `TraderCaravanArrival` (`:984-995`). **This is Rim War taking over the storyteller.** |
| `FactionDialogMaker.FactionDialogFor` (`:154`) | Postfix | **String-matches English UI text** ("Request a trade caravan", "Request immediate military aid") via `Traverse` reflection and deletes those options. Breaks on non-English locale; conflicts with any comms mod. |
| `WorldSelectionDrawer.DrawSelectionOverlays` (`:264`) | Postfix | Iterates **every settlement every frame** to draw badges. See §6. |

Also present: `SettlementUtility.AffectRelationsOnAttacked` (`:49`), `FactionManager.Remove` (`:90`), `SettlementProximityGoodwillUtility.AppendProximityGoodwillOffsets` (`:103`), `Page_CreateWorldParams.DoWindowContents` (`:127`), `TransportersArrivalAction_AttackSettlement.Arrived` (`:246`), `Caravan_PathFollower.StartPath` (`:257`), `CaravanEnterMapUtility.Enter` (`:265`), `Settlement.GetShuttleFloatMenuOptions` (`:273`), `ThingSetMaker.Generate` (`:278`, an explicit hack that nulls `traderDef` when `mlie.morefactioninteraction` is loaded), both `FactionGiftUtility.GiveGift` overloads (`:279, :284`), `IncidentWorker_CaravanDemand.ActionGive` (`:291`), `CaravanExitMapUtility.ExitMapAndCreateCaravan` (`:298`).

Dead code worth noting as a quality signal: `AttackNow_SettlementReinforcement_Postfix` has a body of `_ = component.ReinforcementPoints; _ = 0;` (`:712-720`); `TryResolveParms_Points_Prefix` is `return true` (`:796`); `ShuttleArrived_SettlementHasAttackers_Postfix` (`:394-433`) is defined but never registered. Several `CanFireNowSub` gates are hardcoded defName allowlists for specific other mods (`"VisitorGroup"`, `Contains("Cult")`, `Contains("Salvagers")`, `workerClass.ToString().StartsWith("Rumor_Code")`).

Whether any of this collides with Multiplayer's own patch set was **not cross-checked against the MP assembly (INFERRED risk)** — but `Faction.RelationWith`, `IncidentWorker.TryExecute` and `IncidentQueue.Add` are exactly the kind of methods MP wraps for syncing, and full-replacement prefixes on them are the worst case.

### Bottom line

**Do not ship Rim War in an Archinity co-op save.** Not "with settings adjusted", not "with threading off". Turning `threadingEnabled` off removes source #1 but leaves source #2 entirely intact, and source #2 fires from the UI. Fixing it properly means patching `RimWarData`'s three cache properties, `WorldSettlements`, the `RocketTasker` registrations, and auditing every `Rand` site — i.e. maintaining a fork of a closed-source 20k-line assembly. That is not a reasonable commitment for this project.

There is also a save-compat trap: the mod patches a comp onto **every** `Settlement` def and saves `RimWarData` into the world. Adding it to an existing save and later removing it leaves orphaned comp data and `RW_*` world objects. Decide before starting, not during.

---

## 8. The simplest 20% that delivers "factions act on their own"

Rim War's insight, stripped of everything else, is three lines:

> **A settlement is a bank account. It earns points passively. Actions cost points. It cannot act beyond its means.**

Everything that makes the world feel alive falls out of that. Everything else in the mod — the threading, the pathing war objects, the tweener, the UI tab, the victory condition, diplomats, battle sites — is decoration on that loop.

### The separable core (rebuild, do not extract)

**Piece 1 — the settlement economy.** A `WorldObjectComp` on each settlement holding `points`, `pointDamage`, `playerHeat`, `nextActionTick`. Growth as in `IncrementSettlementGrowth` (`WorldComponent_PowerTracker.cs:733`): biome multiplier × tech-level multiplier × faction growth attribute. Persisted via `ExposeData`.

**Piece 2 — the sampled action loop.** The single best design decision in the mod, and the cheapest thing to copy: **do not scan; sample.** One random faction, one random settlement, every N ticks, with a long per-settlement cooldown (`WorldComponent_PowerTracker.cs:255-263`). This is what keeps the tick cost flat.

**Piece 3 — the weighted action table.** `GetWeightedSettlementAction` (`RimWarData.cs:562`) plus the behavior weight table (`WorldUtility.cs:880`). ~120 lines total, no dependencies. Replace the cumulative-threshold trick with a normal weighted pick — the original is fragile and the at-war "reroll" is half-broken.

**Piece 4 — the affordability + heat gates.** From `AttemptWarbandActionAgainstTown_UnThreaded` (`:1150`): `points * 0.75 >= cost` before spawning, plus `playerHeat` escalation and the `preventActionsAgainstPlayerUntilTick` grace period. These two gates are why the world feels like it has consequences rather than randomness.

**Piece 5 — abstract combat.** `ResolveCombat_Units` (`IncidentUtility.cs:1035`) transcribed nearly verbatim. ~60 lines, four `Rand` draws, no dependencies at all.

**Piece 6 — the abstract↔concrete bridge.** The highest value-per-line in the whole mod. Two directions:
- Outbound: when a war party reaches a player colony, set `IncidentParms.points` from its accumulated `RimWarPoints` and run a normal raid (`DoRaidWithPoints`, `IncidentUtility.cs:253-290`). ~40 lines.
- Inbound: on map exit, count survivors and write the losses back to the world object (`ExitMapPostBattle_Prefix`, `RimWarMod.cs:298`; `UpdateUnitCombatStatus`, `IncidentUtility.cs:1391`). ~50 lines.

Carrying `PointDamage` forward as real injuries (`InflictPointDamageToPawnGroup`, `:1368`) is a nice third touch but optional.

That is roughly **600–800 lines of new C#** and it delivers: settlements that grow, factions that spend their growth on visible armies, armies that fight each other and arrive at your door sized by their home settlement's actual accumulated strength, and a world where beating a faction's warband measurably weakens it.

### What to leave out

| Drop | Why |
|---|---|
| `RocketTasker` / all threading | The desync. Non-negotiable. |
| Cached `Rand`-stamped properties | Desync source #2. Use plain tick arithmetic: `nextTick = TicksGame + CONSTANT`. |
| `WarObject_PathFollower` / `Tweener` | ~700 lines of custom world pathing. A war party can be a tile + ETA int. |
| Territory | Doesn't exist here anyway. |
| Diplomats, victory faction, battle sites, peace talks, rocket-pod launches | All optional flavor. |
| The UI main tab | If you build one, keep it read-only over already-computed values. **Never let it call anything that touches `Rand`.** |

### MP rules for the rebuild (per `CLAUDE.md`)

The project already ships one Harmony assembly (`Archinity.Altar`). Adding this would mean a second, which `CLAUDE.md` says requires an explicit decision — **flag that**. If it goes ahead:

1. **Every `Rand` call must sit inside `WorldComponentTick`.** No exceptions — not in a property getter, not in `GetInspectString`, not in a `Gizmo`, not in a `DoWindowContents`.
2. **No threads, no `Task`, no `async`, no `Stopwatch`-driven control flow.**
3. **No property with a side effect.** Rim War's `OtherSettlementsInRange` getter mutates `nextSettlementScan` *and* spawns a thread. That pattern is the trap; make caches explicit methods called from the tick.
4. **Stagger by `thing.ID`, never by real time** — Rim War gets this right at `WarObject.cs:483`: `(Find.TickManager.TicksGame + base.ID) % 251 == 0`.
5. **Keep tuning constants in defs, not mod settings.** Settings are per-client and the project has already been bitten by settings mismatch; defs are load-order-identical and validated by the existing `tools/check_refs.py`.

Point 5 is the one that makes this whole thing Archinity-shaped: most of what Rim War exposes as mod settings should be `Def` fields here, which removes an entire class of co-op failure before it starts.

---

## Appendix — file map

| File | Lines | Role |
|---|---|---|
| `RimWar.Planet/WorldComponent_PowerTracker.cs` | 2308 | The tick loop and every `Attempt*` action. **Read this first.** |
| `RimWar.Planet/WorldUtility.cs` | 1711 | Spatial queries, faction weight table, `Create*` factories |
| `RimWar.Planet/IncidentUtility.cs` | 1421 | Combat resolution (abstract + real-map raids), pawn generation |
| `RimWar.Utility/RimWar_DebugToolsPlanet.cs` | 1133 | Dev tools; also `ValidateAndResetSettlements` called on load |
| `RimWar.Harmony/RimWarMod.cs` | 998 | ~30 Harmony patches + mod init |
| `RimWar.Planet/WarObject.cs` | 953 | Base world-object entity + `TickInterval` |
| `RimWar.Planet/RimWarSettlementComp.cs` | 922 | The settlement economy + the `Mutex` |
| `RimWar/RimWarData.cs` | 620 | Per-faction state + `GetWeightedSettlementAction` |
| `RimWar.RocketTools/RocketTasker.cs` | 230 | The thread pool. The problem. |
| `RimWar.Options/Settings.cs` | 117 | 30+ settings, all sim-affecting |
