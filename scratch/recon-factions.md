# Recon: faction control — trade, raider gear, guaranteed drops, worldgen

Generated 2026-08-22. All findings from decompiled `Assembly-CSharp.dll` (RimWorld 1.6.4871, ilspycmd)
and shipped `Data/Core|Royalty|Ideology|Biotech|Anomaly|Odyssey/Defs/**.xml`.

Decompile cache used for this pass (temporary, regenerate with
`ilspycmd -p -o <dir> ".../Managed/Assembly-CSharp.dll"`):
`C:\Users\cjd72\AppData\Local\Temp\claude\C--Users-cjd72-Claude\4539541a-e10d-46a7-b6fa-874f67b08142\scratchpad\decomp`

Paths below are given as `<namespace-dir>/<File>.cs` relative to that cache root.

Verdict tags: **[CONFIRMED — file/type]**, **[NOT POSSIBLE]**, **[NEEDS C#]**.

---

# Q3 — GUARANTEED DROPS FROM RAIDING A SETTLEMENT

## 3.1 What actually generates a faction-base map

`Settlement.MapGeneratorDef` → `MapGeneratorDefOf.Base_Faction`
(`RimWorld.Planet/Settlement.cs:80-92`). **[CONFIRMED — RimWorld.Planet/Settlement.cs]**

`Data/Core/Defs/MapGeneration/BaseFactionMapGenerator.xml`:

```xml
<MapGeneratorDef ParentName="MapCommonBase">
  <defName>Base_Faction</defName>
  <genSteps>
    <li>RocksFromGrid</li>
    <li>Settlement</li>       <!-- GenStep_Settlement, order 400 -->
    <li>SettlementPower</li>
  </genSteps>
</MapGeneratorDef>
```

`GenStep_Settlement` (`RimWorld/GenStep_Settlement.cs`) picks a 34–38 square rect, then pushes the
BaseGen symbol `"settlement"`:

```csharp
resolveParams.thingSetMakerDef = lootThingSetMaker;   // field on the GenStep, null by default
resolveParams.lootMarketValue  = lootMarketValue;     // float?, null by default
BaseGen.symbolStack.Push("settlement", resolveParams2);
```

`SymbolResolver_Settlement.Resolve` (`RimWorld.BaseGen/SymbolResolver_Settlement.cs:29-40`):

```csharp
ResolveParams resolveParams = rp;
ref ThingSetMakerDef thingSetMakerDef = ref resolveParams.thingSetMakerDef;
if (thingSetMakerDef == null) thingSetMakerDef = ThingSetMakerDefOf.MapGen_DefaultStockpile;
ref float? lootMarketValue = ref resolveParams.lootMarketValue;
if (!lootMarketValue.HasValue) lootMarketValue = 1800f;   // DefaultLootMarketValue
BaseGen.symbolStack.Push("lootScatter", resolveParams);
```

### CRITICAL FINDING
`FactionDef.settlementLootMaker` is **not read** by the ground faction-base path.
Its only consumer in the whole assembly is `GenStep_SettlementPawnsLoot`
(`RimWorld/GenStep_SettlementPawnsLoot.cs:39`), which is referenced by exactly one def:
Odyssey's `SettlementPlatform` map generator
(`Data/Odyssey/Defs/MapGeneration/SpaceMapGenerator.xml:73-100`, GenStepDef `SettlementPawnsLoot`).

**[CONFIRMED — RimWorld/GenStep_SettlementPawnsLoot.cs + Odyssey/SpaceMapGenerator.xml]**
`settlementLootMaker` only affects **orbital settlement platforms**, not ground bases. Any plan that
assumed "set settlementLootMaker to control what's in a ground faction base" is wrong.

### Loot sources actually present on a ground faction base map

1. **`lootScatter`** — `SymbolResolver_LootScatter` (`RimWorld.BaseGen/SymbolResolver_LootScatter.cs`):
   ```csharp
   ThingSetMakerParams parms = rp.thingSetMakerParams ?? new ThingSetMakerParams {
       countRange = new IntRange(3,10),                       // DefaultLootCountRange
       techLevel  = rp.faction != null ? rp.faction.def.techLevel : TechLevel.Undefined
   };
   parms.makingFaction = rp.faction;
   parms.totalMarketValueRange = new FloatRange(rp.lootMarketValue.Value, rp.lootMarketValue.Value);
   list = rp.thingSetMakerDef.root.Generate(parms);
   MapGenUtility.GenerateLoot(map, rp.rect, list);
   ```
   → ~1800 silver-equivalent of `MapGen_DefaultStockpile` output, **filtered to the faction's techLevel**.

2. **Storage rooms** — `SymbolResolver_Stockpile` (`RimWorld.BaseGen/SymbolResolver_Stockpile.cs:40-56`),
   also `MapGen_DefaultStockpile`, `techLevel = faction.def.techLevel`, value
   `min(cells*130, 1800)`, plus a validator that strips cheap (<100 value) weapons below faction techLevel.

3. **Pawn gear/inventory** — everything the `Settlement`-kind pawn group is wearing/carrying (see Q2).

4. **Buildings** — walls/beds/lamps/power chosen by `BaseGenUtility` + the various
   `SymbolResolver_BasePart_*`, all keyed off `faction.def.techLevel`.

### 3.2 Trader stock is NOT loot
`Settlement_TraderTracker` (`RimWorld.Planet/Settlement_TraderTracker.cs`) holds stock in a
`ThingOwner<Thing> stock` on the **world object**, regenerated every 30 days
(`RegenerateStockEveryDays => 30`) from `ThingSetMakerDefOf.TraderStock`.
On defeat, `SettlementDefeatUtility.CheckDefeated` calls `factionBase.Destroy()`
(`RimWorld.Planet/SettlementDefeatUtility.cs:66`), and `Settlement.Destroy` →
`trader.TryDestroyStock()` which **destroys every non-pawn item**:

```csharp
public void TryDestroyStock() {
    for (int num = stock.Count - 1; num >= 0; num--) {
        Thing thing = stock[num]; stock.Remove(thing);
        if (!(thing is Pawn) && !thing.Destroyed) thing.Destroy();
    }
    stock = null;
}
```
**[CONFIRMED — RimWorld.Planet/Settlement_TraderTracker.cs]** You cannot raid a settlement to take its
trade stock. Trade and raid are entirely disjoint item channels.

Also note `Settlement_TraderTracker.TraderKind` is **deterministic per settlement**:
```csharp
int index = Mathf.Abs(settlement.HashOffset()) % baseTraderKinds.Count;
return baseTraderKinds[index];
```
→ a faction with exactly ONE `baseTraderKinds` entry has that trader at every one of its settlements.

### 3.3 XML-level mechanisms to guarantee a named ThingDef, ranked

| # | Mechanism | Per-faction? | Guaranteed? | Cost |
|---|---|---|---|---|
| 1 | `PawnKindDef.fixedInventory` on a kind in the faction's `Settlement`/`Combat` group makers | YES | YES | 3 lines XML |
| 2 | `PawnKindDef.apparelRequired` (worn) / a unique `weaponTags` tag (carried) | YES | YES | 3 lines XML |
| 3 | `FactionDef.raidLootMaker` (only for raids **on the player**) | YES | YES | ~12 lines XML |
| 4 | Patch the `Settlement` GenStepDef's `lootThingSetMaker` | NO (global) | YES | ~8 lines XML |
| 5 | `CompProperties_LootSpawn` on a crate ThingDef | only via placement | YES | needs placement hook |
| 6 | `LayoutRoomDef.thingSetMakerDef` | only layout maps | YES | N/A for ground bases |

#### (1) CHEAPEST RELIABLE MECHANISM — `PawnKindDef.fixedInventory`
`PawnInventoryGenerator.GenerateInventoryFor` (`RimWorld/PawnInventoryGenerator.cs:12-40`) runs
unconditionally for every generated pawn, **before** any money/tag/techLevel filtering:

```csharp
p.inventory.DestroyAll();
for (int i = 0; i < p.kindDef.fixedInventory.Count; i++) {
    ThingDefCountClass c = p.kindDef.fixedInventory[i];
    Thing thing = ThingMaker.MakeThing(c.thingDef, c.stuff);
    thing.stackCount = c.count;
    if (thing.TryGetComp(out CompQuality comp)) comp.SetQuality(c.quality, ArtGenerationContext.Outsider);
    if (thing.HasComp<CompEquippable>())      p.equipment.AddEquipment((ThingWithComps)thing);
    else if (thing is Apparel newApparel)     p.apparel.Wear(newApparel);
    else                                      p.inventory.innerContainer.TryAdd(thing);
}
```
No techLevel check. No market-value check. No `PlayerAcquirable` check. It even auto-equips weapons
and auto-wears apparel. XML:

```xml
<PawnKindDef ParentName="...">
  <defName>Archinity_GlitteriteQuartermaster</defName>
  <fixedInventory>
    <li><thingDef>USH_Glitterheart</thingDef><count>1</count></li>
  </fixedInventory>
</PawnKindDef>
```
Then put that kind in the faction's `Settlement` **and** `Combat` `pawnGroupMakers`. Every settlement
map and every raid that rolls that kind carries the item; it drops on death/downing/stripping.
Caveat: `PawnKindDef.destroyGearOnDrop` must stay false (default) and `canStrip` true (default).
To make it *certain* rather than points-dependent, give the kind a low `combatPower` and a high
`selectionWeight`, or (better) rely on `apparelRequired` on a kind that is already common.

#### (2) `apparelRequired` — see Q2.4. Guaranteed worn apparel, bypasses money and tags.

#### (3) `FactionDef.raidLootMaker` — guaranteed items on raiders attacking YOU
`IncidentWorker_RaidEnemy.GenerateRaidLoot` (`RimWorld/IncidentWorker_RaidEnemy.cs:155-172`):
```csharp
if (parms.faction.def.raidLootMaker != null && pawns.Any()) {
    raidLootPoints *= Find.Storyteller.difficulty.EffectiveRaidLootPointsFactor;
    float num = parms.faction.def.raidLootValueFromPointsCurve.Evaluate(raidLootPoints);
    if (parms.raidStrategy != null) num *= parms.raidStrategy.raidLootValueFactor;
    ThingSetMakerParams parms2 = default;
    parms2.totalMarketValueRange = new FloatRange(num, num);
    parms2.makingFaction = parms.faction;
    List<Thing> loot = parms.faction.def.raidLootMaker.root.Generate(parms2);
    new RaidLootDistributor(parms, pawns, loot).DistributeLoot();
}
```
`RaidLootDistributor` stuffs the loot into raider inventories, starting with the highest-`combatPower`
pawn (`RimWorld/RaidLootDistributor.cs`). Note `parms2.techLevel` is **not** set here, so the
techLevel filter in `ThingSetMakerUtility.GetAllowedThingDefs` is skipped (`techLevel == Undefined`).
Vanilla example (`Data/Core/Defs/FactionDefs/Factions_Misc.xml:426-440`):
```xml
<ThingSetMakerDef>
  <defName>TribeRaidLootMaker</defName>
  <root Class="ThingSetMaker_MarketValue">
    <fixedParams><filter><thingDefs>
      <li>Silver</li><li>Jade</li><li>MedicineHerbal</li><li>Pemmican</li>
    </thingDefs></filter></fixedParams>
  </root>
</ThingSetMakerDef>
```
For a **guaranteed exactly-one-of-X**, use `ThingSetMaker_Sum` with `resolveInOrder` and a
`ThingSetMaker_Count` option whose `fixedParams` pin both filter and count:
```xml
<ThingSetMakerDef>
  <defName>Archinity_GlitteriteRaidLoot</defName>
  <root Class="ThingSetMaker_Sum">
    <resolveInOrder>true</resolveInOrder>
    <options>
      <li>
        <thingSetMaker Class="ThingSetMaker_Count">
          <fixedParams>
            <countRange>1~1</countRange>
            <filter><thingDefs><li>USH_Glitterheart</li></thingDefs></filter>
          </fixedParams>
        </thingSetMaker>
      </li>
      <li><!-- filler ThingSetMaker_MarketValue for the rest of the budget --></li>
    </options>
  </root>
</ThingSetMakerDef>
```
`ThingSetMaker.Generate` → `ApplyFixedParams(parms)` merges `fixedParams` over the caller's parms,
so `countRange` and `filter` win (`RimWorld/ThingSetMaker.cs:22-46`).
**Gotcha:** `ThingSetMaker_Count.Generate` clamps to `Mathf.Max(intRange.RandomInRange, 1)` — so
countRange `1~1` yields exactly 1 — but `ThingSetMakerUtility.GetAllowedThingDefs` still applies
`x.PlayerAcquirable` and (if `parms.techLevel != Undefined`) `x.techLevel <= parms.techLevel`.

#### (4) Global GenStepDef patch (only if you want it for ALL factions)
```xml
<Operation Class="PatchOperationAdd">
  <xpath>/Defs/GenStepDef[defName="Settlement"]/genStep</xpath>
  <value>
    <lootThingSetMaker>Archinity_SettlementLoot</lootThingSetMaker>
    <lootMarketValue>2500</lootMarketValue>
  </value>
</Operation>
```
This flows into `SymbolResolver_Settlement` → `lootScatter` for every faction base.
Remember `SymbolResolver_LootScatter` sets `techLevel = faction.def.techLevel`, so a neolithic
faction still cannot receive an industrial-techLevel item this way. **[CONFIRMED]**

#### (5) `CompProperties_LootSpawn`
```csharp
public class CompProperties_LootSpawn : CompProperties { public ThingSetMakerDef contents; }
// CompLootSpawn.PostSpawnSetup: Building_Crate crate = (Building_Crate)parent; ...
```
`RimWorld/CompLootSpawn.cs` — **requires `parent` to be a `Building_Crate`** (hard cast, will throw
otherwise). Only useful if you also arrange for that crate to be placed, which on a ground faction
base means a `SymbolResolver`/GenStep, i.e. C#. **[NEEDS C#]** for faction-base placement.

#### (6) `LayoutRoomDef.thingSetMakerDef`
Read only by `RoomContents_Stockpile` (`RimWorld/RoomContents_Stockpile.cs:47-52`), which is part of
the Odyssey/Ideology *layout* pipeline (`LayoutWorker*`, ancient complexes, orbital platforms), not the
BaseGen faction-base pipeline. Irrelevant for ground settlements. **[CONFIRMED]**

#### `GenStep_ScatterThings`
`Verse/GenStep_ScatterThings.cs` — has `thingDef`, `stuff`, `clusterSize`, `quality`, `minify`,
`countPer10kCellsRange` (from `GenStep_Scatterer`). It scatters ONE named ThingDef map-wide. It is a
GenStep, so it can only be added to a MapGeneratorDef — i.e. `Base_Faction`, which is **shared by all
factions**. No per-faction hook exists at the GenStepDef level. **[NOT POSSIBLE per-faction via XML]**

### 3.4 RECOMMENDATION
Use **`PawnKindDef.fixedInventory` / `apparelRequired` / a private `weaponTags` tag** as the primary
"raid faction Z for item X" mechanism. It is per-faction, pure XML, techLevel-blind, works on both
settlement assault and defensive raids, and is the only mechanism that survives every code path.
Layer `raidLootMaker` on top for raid-on-player drops.

---

# Q1 — TRADE

## 1.1 `TraderKindDef` full schema
`RimWorld/TraderKindDef.cs` **[CONFIRMED]**

| Field | Type | Default | Notes |
|---|---|---|---|
| `stockGenerators` | `List<StockGenerator>` | empty | ordered; each is a separate `<li Class="...">` |
| `orbital` | `bool` | false | required for `IncidentWorker_OrbitalTraderArrival.CanSpawn` |
| `requestable` | `bool` | **true** | shows in comms-console "request trader" list |
| `hideThingsNotWillingToTrade` | `bool` | false | UI filter in `Dialog_Trade` |
| `commonality` | `float` | 1 | weight when picking among candidate traders |
| `category` | `string` | null | vanilla uses `"Slaver"`, `"TributeCollector"` |
| `tradeCurrency` | `TradeCurrency` | Silver | e.g. `Favor` for Empire |
| `commonalityMultFromPopulationIntent` | `SimpleCurve` | null | multiplies commonality |
| `faction` | `FactionDef` | null | **orbital traders only** — gates spawn on that faction existing + non-hostile |
| `permitRequiredForTrading` | `RoyalTitlePermitDef` | null | Royalty |

Derived: `CalculatedCommonality`, `WillTrade(ThingDef)` (any generator `HandlesThingDef`),
`PriceTypeFor(...)`.

## 1.2 `StockGenerator` base fields (shared by every subclass)
`RimWorld/StockGenerator.cs` **[CONFIRMED]**
```csharp
public IntRange countRange = IntRange.Zero;
public List<ThingDefCountRangeClass> customCountRanges;   // per-ThingDef countRange override
public FloatRange totalPriceRange = FloatRange.Zero;
public TechLevel maxTechLevelGenerate = TechLevel.Archotech;  // gates GENERATION
public TechLevel maxTechLevelBuy     = TechLevel.Archotech;   // gates HandlesThingDef / what trader will buy
public PriceType price = PriceType.Normal;
```

`RandomCountOf(def)` — this is the answer to "is countRange guaranteed":
```csharp
IntRange intRange = countRange;
if (customCountRanges != null) { /* per-def override */ }
if (intRange.max <= 0 && totalPriceRange.max <= 0f)  return 0;
if (intRange.max >  0 && totalPriceRange.max <= 0f)  return intRange.RandomInRange;      // <- deterministic range
if (intRange.max <= 0 && totalPriceRange.max >  0f)  return RoundToInt(totalPriceRange.RandomInRange / def.BaseMarketValue);
// both set: reroll intRange up to 100x until count*value falls inside totalPriceRange
```
**`countRange` is a uniform draw, not a chance.** `<countRange>3~10</countRange>` always yields 3–10.
The vanilla "sometimes zero" idiom is a **negative min**, e.g. `Base_Neolithic_Standard`'s
`<thingDef>Gold</thingDef><countRange>-40~120</countRange>` — a roll ≤0 produces nothing
(`StockGeneratorUtility.TryMakeForStockSingle` returns null when `stackCount <= 0`).

## 1.3 Subclass list (1.6 — complete)
All in `RimWorld/`. **[CONFIRMED — DefDatabase-visible classes in Assembly-CSharp]**

**Sell-side (generate stock):**
- `StockGenerator_SingleDef` — `private ThingDef thingDef;` (private fields are XML-settable).
  The only generator with **no** techLevel, tag, or `PlayerAcquirable` filtering on generate.
- `StockGenerator_MultiDef` — `List<ThingDef> thingDefs;` picks **one** at random per resolve.
- `StockGenerator_Category` — `categoryDef`, `thingDefCountRange` (IntRange.One),
  `excludedThingDefs`, `excludedCategories`. Filters `t.techLevel <= maxTechLevelGenerate`.
- `StockGenerator_Tag` — `tradeTag`, `thingDefCountRange`, `excludedThingDefs`.
  Filters `d.PlayerAcquirable` **and** `d.techLevel <= maxTechLevelBuy` (via `HandlesThingDef`).
- `StockGenerator_MiscItems` (abstract) → `StockGenerator_MarketValue`
  (`tradeTag`, `weaponTag`, `apparelTag`; selection weighted by an inverse market-value curve).
  **In 1.6 there is no `StockGenerator_Armor` / `StockGenerator_Weapons`** — they were folded into
  `StockGenerator_MarketValue`. Vanilla uses `<li Class="StockGenerator_MarketValue"><tradeTag>WeaponMelee</tradeTag>…`.
- `StockGenerator_Animals` — `tradeTagsSell`, `tradeTagsBuy`, `createMatingPair`, `kindCountRange`,
  `minWildness`, `maxWildness`, `checkTemperature`.
- `StockGenerator_Slaves` — `respectPopulationIntent`, `slaveKindDef`. Blocked if any faction ideo
  disapproves of slavery.
- `StockGenerator_Techprints` — `countChances` (`List<CountChance>`); routed through
  `TechprintUtility.TryGetTechprintDefToGenerate_NewTemp`, which respects
  `project.heldByFactionCategoryTags` vs the making faction's `categoryTag`.
- `StockGenerator_Tomes` — Anomaly-gated `Tome`; extends `_SingleDef`.
- `StockGenerator_ReinforcedBarrels` — suppressed under `difficulty.classicMortars`.

**Buy-only (`GenerateThings` returns empty; only widen what the trader will BUY):**
- `StockGenerator_BuySingleDef` (`public ThingDef thingDef;`)
- `StockGenerator_BuyTradeTag` (`public string tag;`)
- `StockGenerator_BuyCategory` — **does not exist in 1.6 core**; use `StockGenerator_Category` with
  `countRange 0~0` if you need buy-only-by-category, or `_BuyTradeTag`.
- `StockGenerator_BuySlaves`
- `StockGenerator_BuyExpensiveSimple` (`minValuePerUnit = 15f`; excludes apparel/weapons/medicine/drugs
  and anything with `genericMarketSellable = false`)

## 1.4 How to GUARANTEE a specific ThingDef in a trader's stock
**[CONFIRMED — RimWorld/StockGenerator_SingleDef.cs + StockGeneratorUtility.cs]**
```xml
<li Class="StockGenerator_SingleDef">
  <thingDef>USH_Glitterheart</thingDef>
  <countRange>1~2</countRange>
</li>
```
This is fully deterministic given `countRange.min >= 1`. `_SingleDef.GenerateThings` calls
`StockGeneratorUtility.TryMakeForStock(thingDef, RandomCountOf(thingDef), faction)` with **no**
techLevel / tag / `PlayerAcquirable` filter — the only gate is `thingDef.tradeability.TraderCanSell()`
(i.e. `Tradeability.Buyable` or `.All`), which is also validated at load in `ConfigErrors`.

Notably `_SingleDef` **bypasses `ThingDef.requiresFactionToAcquire`** (that's checked in
`ThingDef.PlayerAcquirable`, which only `_Tag` / `_MiscItems` / ThingSetMakers consult).

Traps:
- `ThingDef.tradeability` must be `Buyable`/`All`. `Tradeability.None` → red error at startup.
- `MadeFromStuff` / `tradeNeverStack` / `tradeNeverGenerateStacked` defs are emitted as N separate
  stacks of 1 (`StockGeneratorUtility.TryMakeForStock`).
- `ThingSetMaker_TraderStock.Generate` re-checks `TraderCanSell` and logs+drops anything that fails.

## 1.5 Faction ↔ trader wiring
`RimWorld/FactionDef.cs:166-172`:
```csharp
public List<TraderKindDef> caravanTraderKinds = new();
public List<TraderKindDef> orbitalTraderKinds = new();
public List<TraderKindDef> visitorTraderKinds = new();
public List<TraderKindDef> baseTraderKinds    = new();
```

| List | Consumer | Selection |
|---|---|---|
| `caravanTraderKinds` | `IncidentWorker_TraderCaravanArrival` (`:47`), `PawnGroupKindWorker_Trader` (`:60`), `FactionDialogMaker:287` (request trader, filtered by `requestable`) | `RandomElementByWeight(CalculatedCommonality)` |
| `visitorTraderKinds` | `IncidentWorker_VisitorGroup:83,96` — 75% chance one visitor becomes a small trader | `RandomElementByWeight(CalculatedCommonality)` |
| `baseTraderKinds` | `Settlement_TraderTracker.TraderKind` | **deterministic**: `baseTraderKinds[abs(settlement.HashOffset()) % count]` |
| `orbitalTraderKinds` | `FactionDialogMaker:217` (comms request only, needs `FactionDef.canRequestOrbitalTrader`) | player choice |

Random orbital trader arrivals do **not** use `orbitalTraderKinds` — `IncidentWorker_OrbitalTraderArrival`
scans **all** `TraderKindDef`s with `orbital == true`, weights by `CalculatedCommonality`, and resolves
the faction from `TraderKindDef.faction` (`RimWorld/IncidentWorker_OrbitalTraderArrival.cs:26,42-55`).
So to control orbital trade you must control `TraderKindDef.orbital` + `.faction` + `.commonality`
globally, not per-FactionDef. **[CONFIRMED]**

`FactionDef.canRequestTraders`, `canRequestOrbitalTrader`, `canRequestMilitaryAid` gate the comms dialog.

## 1.6 Does techLevel filter stock?
**Faction techLevel: NO.** Nothing in the trade path reads `faction.def.techLevel`.
**StockGenerator techLevel: YES, but it's per-generator XML**, not inherited from the faction:
- `maxTechLevelGenerate` → filters what `_Category` / `_MiscItems` will *create*.
- `maxTechLevelBuy` → filters `HandlesThingDef` for `_Category`, `_Tag`, `_MiscItems`, `_Techprints`
  (i.e. what the trader will *buy* from you, and what `Dialog_SellableItems` shows).
- `_SingleDef` / `_MultiDef` / `_BuySingleDef` ignore techLevel entirely.

`tradeTags` (`ThingDef.tradeTags`) is the join key for `_Tag`, `_MarketValue`, `_BuyTradeTag`,
`_Animals` (via `race.tradeTags`), and `_Techprints` (hardcoded `"Techprint"`).
`ThingDef.weaponTags` / `ThingDef.apparel.tags` are additionally consulted by `_MarketValue`.

`ThingDef.PlayerAcquirable` (`Verse/ThingDef.cs:506+`) returns false when `destroyOnDrop`, or when
`requiresFactionToAcquire` names a faction that does not exist in the world, or for
`ReinforcedBarrel` under `classicMortars`. It gates `_Tag` generation and all ThingSetMakers —
**this is the lever for "item X only exists once faction Z is in the world"**.

## 1.7 Practical recipe for the progression design
- One `TraderKindDef` per faction per era, referenced from that faction's `baseTraderKinds`
  (single entry ⇒ deterministic) and `caravanTraderKinds`.
- Anchor items via `StockGenerator_SingleDef` with `countRange` min ≥ 1.
- Use `maxTechLevelGenerate` on the `_Category`/`_MarketValue` generators to keep filler in-era.
- Set `requestable=false` on traders you don't want purchasable on demand via comms.

---

# Q2 — RAIDER GEAR

## 2.1 Order of operations
`PawnGenerator.GeneratePawn` → `GenerateGearFor` calls, in order:
`PawnApparelGenerator.GenerateStartingApparelFor` → `PawnWeaponGenerator.TryGenerateWeaponFor` →
`PawnInventoryGenerator.GenerateInventoryFor` → `PawnTechHediffsGenerator.GenerateTechHediffsFor`.

## 2.2 Weapons — `RimWorld/PawnWeaponGenerator.cs` **[CONFIRMED]**
```csharp
if (pawn.kindDef.weaponTags == null || pawn.kindDef.weaponTags.Count == 0 || !pawn.RaceProps.ToolUser
    || !pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation)
    || pawn.WorkTagIsDisabled(WorkTags.Violent)) return;
float randomInRange = pawn.kindDef.weaponMoney.RandomInRange;
for (...) if (!(w2.Price > randomInRange)
        && pawn.kindDef.weaponTags.Any(tag => w2.thing.weaponTags.Contains(tag))
        && (pawn.kindDef.weaponStuffOverride == null || w2.stuff == pawn.kindDef.weaponStuffOverride)
        && (!w2.thing.IsRangedWeapon || !pawn.WorkTagIsDisabled(WorkTags.Shooting))
        && (w2.stuff == null || w2.stuff.stuffProps.allowedInStuffGeneration)
        && (!(w2.thing.generateAllowChance < 1f) || Rand.ChanceSeeded(...)))
    workingWeapons.Add(w2);
workingWeapons.TryRandomElementByWeight(w => GetCommonality(pawn, w), out result);
// GetCommonality = pair.Commonality * pair.Price * ideoFactor * xenotypeFactor
```
Candidate pool `allWeaponPairs` = every ThingDef with `equipmentType == Primary` **and non-empty
`weaponTags`**, crossed with allowed stuffs, weighted by `ThingDef.generateCommonality`.

- **`ThingDef.weaponTags` ↔ `PawnKindDef.weaponTags` is the ONLY join.** Any overlap qualifies.
- `weaponMoney` is a hard price ceiling per candidate (`w2.Price > money` ⇒ rejected).
  `PawnKindDef.ConfigErrors` warns if the cheapest tagged weapon exceeds `weaponMoney.min`.
- `biocodeWeaponChance` — chance to biocode to the pawn (biocoded gear is useless to you if looted).
  **Set this to 0 on any kind you want the player to loot from.**
- `forceWeaponQuality`, `weaponStyleDef`, `weaponStuffOverride` also live on PawnKindDef.
- **`faction.def.techLevel` is not read here at all.** Faction techLevel does NOT restrict weapons.

**Guarantee a specific weapon:** give the ThingDef a private tag and put only that tag on the kind:
```xml
<ThingDef ParentName="BaseGun"> <defName>Archinity_Foo</defName>
  <weaponTags><li>ArchinityFooOnly</li></weaponTags> </ThingDef>
<PawnKindDef> <defName>Archinity_FooBearer</defName>
  <weaponTags><li>ArchinityFooOnly</li></weaponTags>
  <weaponMoney>9999~9999</weaponMoney>
  <biocodeWeaponChance>0</biocodeWeaponChance> </PawnKindDef>
```
If exactly one ThingDef carries the tag and its price ≤ `weaponMoney.min`, the pawn always spawns
with it. **[CONFIRMED]**

## 2.3 Apparel — `RimWorld/PawnApparelGenerator.cs` **[CONFIRMED]**
Money: `float money = pawn.kindDef.apparelMoney.RandomInRange;`
Headgear: `bool allowHeadgear = Rand.Value < pawn.kindDef.apparelAllowHeadgearChance;` (default 1.0)

`CanUsePair(pair, pawn, moneyLeft, allowHeadgear, seed)` (`:1040`) rejects when:
`pair.Price > moneyLeft`; headgear when disallowed; `!pair.thing.apparel.PawnCanWear(pawn)`;
`apparelTags` non-empty and no tag matches `pair.thing.apparel.tags`; any `apparelDisallowTags`
match; `generateAllowChance` roll fails (unless `ignoreApparelAllowChance`).

`CanUseStuff` additionally enforces `FactionDef.apparelStuffFilter` via
`pawn.Faction.def.CanUseStuffForApparel(stuff)` unless `kindDef.ignoreFactionApparelStuffRequirements`.

**Faction techLevel appears exactly once**, in `CorrectFactionForApparel` (`:605`):
```csharp
if (apparel.apparel.anyTechLevelCanUseForWarmth) return true;
if ((int)faction.techLevel >= 4 && apparel.techLevel == TechLevel.Neolithic) return false;
if (faction.techLevel == TechLevel.Neolithic && (int)apparel.techLevel >= 4) return false;
```
…and it is only called from the **free warm parka/hat fallback** validators (`:300`, `:332`), i.e.
`forceAddFreeWarmLayerIfNeeded`. It does **not** gate normal apparel selection.
So faction techLevel effectively does not restrict raider apparel either. **[CONFIRMED]**

## 2.4 `apparelRequired` — the guarantee lever
`GenerateWorkingPossibleApparelSetFor` (`:884`):
```csharp
moneyLeft = GenerateSpecificRequiredApparel(pawn, moneyLeft, false);
List<ThingDef> reqApparel = pawn.kindDef.apparelRequired;
if (reqApparel != null) for (i...) {
  if (reqApparel[i].apparel.CorrectAgeForWearing(pawn)
      && allApparelPairs.Where(pa => pa.thing == reqApparel[i] && CanUseStuff(pawn, pa)
                                     && !workingSet.PairOverlapsAnything(pa))
                        .TryRandomElementByWeight(pa => pa.Commonality, out var result)) {
      workingSet.Add(result); moneyLeft -= result.Price;   // moneyLeft may go negative — fine
  }
}
```
No `CanUsePair`, no tag check, no money check, no headgear check.
Only constraints: age-appropriate, faction `apparelStuffFilter` (via `CanUseStuff`), and no layer
overlap with `specificApparelRequirements` already placed. **This is the guaranteed apparel path.**
`specificApparelRequirements` (`List<SpecificApparelRequirement>`: `RequiredTag`,
`AlternateTagChoices`, `Color`, `StyleDef`, `Locked`, `Biocode`, `IgnoreNaked`) resolves *before*
`apparelRequired` and can `Locked`/`Biocode` the item — again, **avoid `Biocode`/`Locked` on anything
you want the player to loot.**

## 2.5 Tech hediffs — `RimWorld/PawnTechHediffsGenerator.cs`
```csharp
float partsMoney = pawn.kindDef.techHediffsMoney.RandomInRange;
int num = pawn.kindDef.techHediffsMaxAmount;
foreach (ThingDef item in pawn.kindDef.techHediffsRequired) { partsMoney -= item.BaseMarketValue; num--; InstallPart(pawn, item); }
if (pawn.kindDef.techHediffsTags == null || pawn.kindDef.techHediffsChance <= 0f) return;
// then up to `num` rolls at techHediffsChance each, picking from ThingDefs where
//   x.isTechHediff && x.BaseMarketValue <= partsMoney
//   && x.techHediffsTags intersects kindDef.techHediffsTags
//   && !kindDef.techHediffsDisallowTags intersects x.techHediffsTags
// weighted by BaseMarketValue (expensive parts favoured)
```
`techHediffsRequired` is unconditional (ignores chance and money). Note installed parts are **inside
the pawn** — recovering them means butchering/harvesting, not stripping. `ThingDef.techHediffsTags` is
the join key. No faction techLevel involvement. **[CONFIRMED]**

## 2.6 Summary: can we guarantee a faction's pawns carry a specific item?
**YES, per-PawnKindDef, all pure XML:**
`fixedInventory` (unconditional, auto-equips/auto-wears) > `apparelRequired` (worn) ≈ unique
`weaponTags` + sufficient `weaponMoney` (carried) > `techHediffsRequired` (implanted).
Then reference those kinds from the faction's `pawnGroupMakers`. Faction `techLevel` is irrelevant
to all four. **[CONFIRMED]**

---

# Q4 — `pawnGroupMakers`

## 4.1 Structure — `RimWorld/PawnGroupMaker.cs` **[CONFIRMED]**
```csharp
public PawnGroupKindDef kindDef;
public float commonality = 100f;
public List<RaidStrategyDef> disallowedStrategies;
public float maxTotalPoints = 9999999f;
public List<PawnGenOption> options  = new();   // combat/settlement bodies
public List<PawnGenOption> traders  = new();   // Trader kind only; kinds must have trader=true
public List<PawnGenOption> carriers = new();   // Trader kind only; kinds must be packAnimal
public List<PawnGenOption> guards   = new();   // Trader kind only
```
`PawnGenOption` (`RimWorld/PawnGenOption.cs`) has `kind` + `selectionWeight`, and a custom XML loader —
hence the shorthand `<Tribal_Archer>10</Tribal_Archer>` syntax. `Cost => kind.combatPower`.

## 4.2 `PawnGroupKindDef`
`RimWorld/PawnGroupKindDef.cs` — just `workerClass` (default `PawnGroupKindWorker`).
Core defs: `Data/Core/Defs/Misc/PawnGroupKindDefs/PawnGroupKinds.xml`.
`PawnGroupKindDefOf`: `Combat`, `Trader`, `Peaceful`, `Settlement`, `Settlement_RangedOnly`,
plus Ideology (`Miners`/`Farmers`/`Loggers`/`Hunters`) and Anomaly entity kinds.
Workers: `PawnGroupKindWorker_Normal` (Combat/Peaceful/Settlement) and `PawnGroupKindWorker_Trader`.

## 4.3 Points → composition — `RimWorld/PawnGroupMakerUtility.cs`
1. **Pick the group maker**: `TryGetRandomPawnGroupMaker` filters
   `gm.kindDef == parms.groupKind && gm.CanGenerateFrom(parms)` then
   `TryRandomElementByWeight(gm => gm.commonality)`.
   `CanGenerateFrom` rejects if `parms.points > maxTotalPoints`, the raid strategy is in
   `disallowedStrategies`, or `points < MinPointsToGenerateAnything`.
2. **Fill the budget**: `ChoosePawnGenOptionsByPoints(pointsTotal, options, parms)` loops:
   - eligible options = cost ≤ points remaining **and** cost ≤ `MaxPawnCost(...)`
   - `MaxPawnCost = faction.def.maxPawnCostPerTotalPointsCurve.Evaluate(totalPoints)`, then
     `min(…, totalPoints / raidStrategy.minPawns)`, then floored at
     `MinPointsToGeneratePawnGroup(groupKind) * 1.2f`
   - weight = `selectionWeight * PawnWeightFactorByMostExpensivePawnCostFractionCurve.Evaluate(cost / highestCost)`
     where that curve is `(0.2, 0.01), (0.3, 0.3), (0.5, 1.0)` — **cheap pawns relative to the most
     expensive eligible pawn are heavily suppressed**, which is what makes high-point raids drop trash kinds.
   - subtract `option.Cost` (= `kind.combatPower`, × `xenotype.combatPowerFactor` under Biotech)
   - stops when nothing fits; warns if only one pawn was made with >half the points unspent.
3. `PawnKindDef.maxPerGroup` caps repeats; `kind.factionLeader` may only be chosen once.
4. Biotech: each option is expanded per xenotype via `PawnGenerator.XenotypesAvailableFor`, and the
   xenotype's weight multiplies `selectionWeight` — **this is the hook `bs.xenotypespawncontrol` uses.**

## 4.4 Trader groups — `RimWorld/PawnGroupKindWorker_Trader.cs`
`MinPointsToGenerateAnything => 0f`. Requires `groupMaker.traders.Any()` and at least one carrier
whose race is `IsPackAnimalAllowed` for the tile's biome. Hard-errors (and generates nothing) if any
`traders` kind has `trader == false`, or any `carriers` kind is not `RaceProps.packAnimal`, or the
faction has no `caravanTraderKinds`. Carrier count = `ceil(wares.Count / 8f)`.
Note: `parms.seed` is explicitly **not honoured** here (logs a warning) — trader caravans are
non-deterministic. **Relevant for multiplayer determinism.**

## 4.5 `settlementGenerationWeight` vs `pawnGroupMultiplier`
`FactionDef.settlementGenerationWeight` (`float`, default **0**) is read in exactly one place —
`FactionGenerator.GenerateFactionsIntoWorldLayer` (`RimWorld/FactionGenerator.cs:40`):
```csharp
Faction faction = source.RandomElementByWeight(x => x.def.settlementGenerationWeight);
```
The loop count is `roundRandom(layer.TilesCount / 100000f * layer.Def.settlementsPer100kTiles.RandomInRange
* world.info.overallPopulation.GetScaleFactor() * viewAngleFactor)` minus existing settlements. So it
is a **relative share of the world's total settlement budget**, per planet layer. A faction with
weight 0 gets a `Faction` object but **zero settlements**. It has nothing to do with pawn groups.
**[CONFIRMED — RimWorld/FactionGenerator.cs]**

`pawnGroupMultiplier` **does not exist in Assembly-CSharp**. Grep across all of
`Data/` and the decompiled core returns nothing. It lives in `KCSG.dll` (Vanilla Expanded Framework,
workshop `2023507013`, all of `1.2/`–`1.6/Assemblies/KCSG.dll`) — see Q6.
**[CONFIRMED — not vanilla]**

Also worth knowing: `FactionDef.defaultSettlementGroupKindDef` is `private` and has **no readers** in
1.6 — dead field. Settlement groups always use `PawnGroupKindDefOf.Settlement`
(`SymbolResolver_Settlement:52`, `GenStep_SettlementPawnsLoot:33`), with `GenStep_SitePawns` falling
back to `Settlement` when the requested kind is absent from the faction.

---

# Q5 — FACTION GENERATION GUARANTEES

## 5.1 `configurationListOrderPriority`
Read in exactly one place, `FactionGenerator.ConfigurableFactions`
(`RimWorld/FactionGenerator.cs:13-24`):
```csharp
foreach (FactionDef item in from f in DefDatabase<FactionDef>.AllDefs
                            where f.maxConfigurableAtWorldCreation > 0
                            orderby f.configurationListOrderPriority
                            select f)
```
It is **purely the sort order of the faction rows in the world-creation UI** (ascending). It has no
effect on which factions are generated or how many. `maxConfigurableAtWorldCreation > 0` is what makes
a faction appear in that list at all. **[CONFIRMED]**

## 5.2 The actual generation path
`Page_CreateWorldParams.ResetFactionCounts` (`RimWorld/Page_CreateWorldParams.cs:69-88`):
```csharp
foreach (FactionDef f in FactionGenerator.ConfigurableFactions)
    if (f.startingCountAtWorldCreation > 0)
        for (int i = 0; i < f.startingCountAtWorldCreation; i++) factions.Add(f);
foreach (FactionDef f in FactionGenerator.ConfigurableFactions)
    if (f.replacesFaction != null) factions.RemoveAll(x => x == f.replacesFaction);
```
That list becomes `Current.CreatingWorld.info.factions`, consumed by
`WorldGenStep_Factions.GenerateFresh` → `FactionGenerator.GenerateFactionsIntoWorldLayer(layer, info.factions)`
→ `InitializeFactions(layer, factions)`:
```csharp
if (factions != null) {                       // normal path: player's UI list
    foreach (FactionDef faction in factions)
        if (CanExistOnLayer(layer, faction)) AddFactionToManager(layer, faction);
    return;                                   // <-- requiredCountAtGameStart never reached
}
// fallback (factions == null): the requiredCountAtGameStart loop
```
Confirms the known result: **`requiredCountAtGameStart` is dead on any normal game start.**
`CanExistOnLayer` applies `layerWhitelist` / `layerBlacklist` — a faction whitelisted to
`Orbit` will silently be skipped on the Surface pass and only created during the Orbit layer pass.
**This is the most likely reason `archinity.drifters` / `archinity.glitterites` "never go through
worldgen".** Check their `layerWhitelist` and confirm `PlanetLayerDef` Orbit generation actually runs
`WorldGenStep_Factions` for that layer.

## 5.3 Forcing a faction into an EXISTING save
**[NOT POSSIBLE via XML.]** Nothing in the load path reconciles FactionDefs against saved factions
except a hardcoded DLC backfill, `BackCompatibility.FactionManagerPostLoadInit`
(`Verse/BackCompatibility.cs:403-431`) — Empire / HoraxCult / Entities / TradersGuild / Salvagers only.
`FactionManager.ExposeData` merely loads `allFactions` and drops nulls.

**[NEEDS C#]** but trivially: `FactionGenerator.CreateFactionAndAddToManager(FactionDef)` and
`CreateFactionAndAddToManager(PlanetLayer, FactionDef)` are both `public static`
(`RimWorld/FactionGenerator.cs:106-124`). A `GameComponent.FinalizeInit` doing:
```csharp
if (Find.FactionManager.FirstFactionOfDef(MyDefOf.MyFaction) == null)
    FactionGenerator.CreateFactionAndAddToManager(Find.WorldGrid.Surface, MyDefOf.MyFaction);
```
mirrors exactly what vanilla does for DLC factions. Settlements still need separate placement
(`WorldObjectMaker.MakeWorldObject(...)` + `TileFinder.RandomSettlementTileFor(layer, faction)` —
see `FactionGenerator.GenerateFactionsIntoWorldLayer:41-48` for the exact five lines).
**Multiplayer note:** this must run identically on all clients and is a world-state mutation; do it in
`FinalizeInit` (deterministic point) or accept a desync risk.

## 5.4 What happens if you add a FactionDef with `startingCountAtWorldCreation > 0` to an existing world?
**Nothing.** The def loads, `ConfigurableFactions` includes it for *future* world creation, and the
existing save simply has no `Faction` instance of that def. Downstream effects:
- `Find.FactionManager.FirstFactionOfDef(x)` → null; any quest/incident/`GenStep` that requires it
  silently no-ops (matching the known "empty pool fails open + silent" raid behaviour).
- Any `ThingDef` with `requiresFactionToAcquire = <that def>` stays `PlayerAcquirable == false`
  (`Verse/ThingDef.cs:506+`) — so it will not appear in `StockGenerator_Tag` stock or any
  ThingSetMaker output, though `StockGenerator_SingleDef` will still emit it.
- No error, no letter, no log message. **[CONFIRMED]**

## 5.5 Other worldgen levers worth noting
- `FactionDef.replacesFaction` — removes another def from the default UI list (Page_CreateWorldParams only).
- `FactionDef.mustStartOneEnemy`, `permanentEnemy`, `permanentEnemyToEveryoneExcept[Player]`,
  `naturalEnemy`, `hostileToFactionlessHumanlikes` — relations at generation.
- `FactionDef.hidden` — excluded from `AllFactionsVisible` and from settlement generation
  (`Validator` in `GenerateFactionsIntoWorldLayer` requires `!x.Hidden && !x.temporary`).
- `FactionDef.ConfigErrors` **hard-requires** `raidLootValueFromPointsCurve` on every FactionDef
  (`RimWorld/FactionDef.cs:570`) and `maxPawnCostPerTotalPointsCurve` whenever `pawnGroupMakers != null`.

---

# Q6 — Does the loaded mod set already give fine-grained faction control?

## 6.1 Faction Customizer — `azravos.factioncustomizer` (workshop `3336572602`)
**[CONFIRMED — decompiled `3336572602\1.6\Assemblies\FactionCustomizer.dll`]**

**Verdict: useless as a config carrier for this project.** It is a cosmetic + diplomacy + world-map
editor operating on **live `Faction` / `Settlement` instances**, never on Defs.

Entire mod content: `About\About.xml` (deps: `brrainz.harmony` only), three `KeyBindingDef`s
(`3336572602\1.6\Defs\KeyBindings\KeyBindings.xml`), Languages, Textures, and
`FactionCustomizer.dll` + `0ColourPicker1.6.dll`. **No Patches folder. No FactionDef XML.
No custom `Def` or `DefModExtension` types at all** (grep for `: Def` / `: DefModExtension` → 0 hits).

The complete set of things it can change (`FactionCustomizer.Dialogs/FactionProperties.cs`,
`FactionRelationProperties.cs`, `Dialog_ModifyFaction.MakeChanges():409-465`):
```csharp
faction.Name  = ChangingProperties.FactionName;
faction.def   = ChangingProperties.factionDef;      // swaps the instance's def pointer
faction.leader.Name = new NameTriple(...);
faction.color = ChangingProperties.FactionColor;
faction.ideos.SetPrimary(ChangingProperties.Ideo);
// Dialog_ModifyFactionRelation.cs:100-103
relation.baseGoodwill = ChangingProperties.BaseGoodWill;   // -100..100
relation.kind         = ChangingProperties.RelationKind;
```
Plus create/delete/relocate/rename `Settlement` world objects (`WorldInterfaceUpdate.cs`,
`MoveSettlement.cs`) and spawn a brand-new faction during landing
(`FCDialog_FactionDuringLanding.cs:121-144` → `FactionGenerator.NewGeneratedFaction(...)` +
`Find.FactionManager.Add(...)`, filtered to `ConfigurableFactions.Where(t => t.displayInFactionSelection
&& !t.hidden && t.orbitalTraderKinds.Count == 0)`).

| Knob we care about | Supported? |
|---|---|
| `techLevel` | **NO** — the string never appears in the assembly |
| `pawnGroupMakers` | **NO** |
| `caravan/base/visitor/orbitalTraderKinds` | **NO** (only read as a filter) |
| `settlementGenerationWeight` / settlement counts | **NO** (hand-places one world object at a time) |
| `permanentEnemy` | **NO write** — `FactionRelationProperties.PermanentEnemy` is a dead field |
| hostility / goodwill | **YES**, live `FactionRelation.baseGoodwill` + `.kind` only |
| `apparelTags` / `weaponTags` / raid gear | **NO** |

**Settings:** `ModSettings` holds only **6 UI booleans**
(`confirmDialogWhenDeletingSettlements`, `showRenameDialogAfterSettlementCreation`,
`showFactionDialogAfterAddingNew`, `relocateEnabledWhileGameIsRunning`,
`settlementManipulationEnabledWhileGameIsRunning`, `createNewFactionEnabledWhileGameIsRunning`),
all `Scribe_Values.Look<bool>`, written to
`...\Config\Mod_3336572602_FactionCustomizer.xml` (not yet present on this machine).
The *actual* customizations are **not in settings and not in XML** — they are mutated
`Faction`/`Settlement` objects serialised into the **savegame**. No export/import path exists.
**You cannot ship a mod that reproduces Faction Customizer's output; each player would redo it by hand
per world.**

**Load sequence:** `Mod` ctor does `GetSettings<ModSettings>()` + `Harmony.PatchAll()`. No Def
mutation, no startup Def edits. All Harmony patches are UI plumbing
(`WorldGlobalControls.WorldGlobalControlsOnGUI`, `GlobalControls.GlobalControlsOnGUI`,
`Page_SelectStartingSite.DoCustomBottomButtons`, `Page.DrawPageTitle`,
`PlaySettings.DoPlaySettingsGlobalControls`, `InspectPaneUtility.InspectPaneOnGUI`).

**Multiplayer:** zero references to `Multiplayer`/`rwmt`. Good: it never mutates a Def from settings,
so no Def-hash divergence. Bad: every mutation happens in **unsynced GUI code**, so in MP it applies
client-side only and will desync world state. The 6 booleans are harmless if they differ.

## 6.2 Xenotype Spawn Control — `bs.xenotypespawncontrol` (workshop `2891975564`)
**[CONFIRMED — full C# source is shipped at `2891975564\Source\`]**

Controls per-xenotype spawn chance/weight for `FactionDef`, `PawnKindDef`, `MemeDef` (+ a synthetic
"No Faction" entry), plus `AllowArchite`, Random/Hybrid pseudo-xenotypes, and named Templates.

**Settings-only, and it mutates Defs at startup.** `Source/StaticConstructor.cs`:
```csharp
[StaticConstructorOnStartup]
public static class StaticConstructor {
    static StaticConstructor() => XenotypeChanceDatabases.AssignXenotypeChancesFromSettings();
}
```
→ `XenotypeChances<T>.SetChanceInXenotypeSet(ref XenotypeSet? set, XenotypeDef, int chance)` writes
`FactionDef.xenotypeSet` / `PawnKindDef.xenotypeSet` / `MemeDef.xenotypeSet` **in place** via
`AccessTools.FieldRefAccess`, and `XenotypeDef.factionlessGenerationWeight = rawChanceValue / 10f`
for the No-Faction case. Scribe node names: `XenotypesByFactionDef`, `XenotypesByPawnKindDef`,
`XenotypesByMemeDef`, `Templates`. Settings file:
`...\Config\Mod_2891975564_XenotypeDiversityMod.xml`.
Harmony: `PawnGenerator.GenerateGenes` (Prefix, the live hook),
`PawnGenerator.AdjustXenotypeForFactionlessPawn`, `StartingPawnUtility.Get/SetGenerationRequest`,
`GameDataSaveLoader.SaveXenotype`, `NameUseChecker.XenotypeNameIsUsed`.

Only third-party XML hook — one `DefModExtension` (`Source/Extension.cs`):
```xml
<li Class="XenotypeSpawnControl.Extension">
  <randomGenesChance>0.25</randomGenesChance>
  <hybridChance>0.1</hybridChance>
</li>
```
(the mod's own single patch, `2891975564\Patches\XenotypeSpawnControlModExtension.xml`, applies this
to `StrangerInBlack`). No custom `Def` types.

**Multiplayer:** no MP API registration. It **does mutate Def state from ModSettings at
`StaticConstructorOnStartup`**, so every client needs a byte-identical
`Mod_2891975564_XenotypeDiversityMod.xml` or pawn generation diverges immediately. **MP hazard.**

**We do not need it.** XSC only writes `FactionDef.xenotypeSet.xenotypeChances`, which we can set
directly with a plain `PatchOperationReplace`/`Add` on `<xenotypeSet>` in our own mod — identical
result, deterministic, MP-hash-stable.

## 6.3 VEF / KCSG — the actual settlement-map lever
**[CONFIRMED — decompiled `2023507013\1.6\Assemblies\KCSG.dll`]**

- **`pawnGroupMultiplier`** lives on `KCSG.DefenseOptions` (`KCSG/DefenseOptions.cs:27`), a plain
  class (not a Def, not a DefModExtension), nested as `<defenseOptions>` inside a
  `KCSG.SettlementLayoutDef`. `float`, default `1f`. **Exactly one reader**,
  `KCSG/SymbolResolver_Settlement.cs:129-133`:
  ```csharp
  if (GenOption.settlementLayout != null) {
      PawnGroupMakerParms p = val.pawnGroupMakerParams;
      p.points *= GenOption.settlementLayout.defenseOptions.pawnGroupMultiplier;
  }
  ```
  It scales **settlement-map defender points only** (the `PawnGroupKindDefOf.Settlement` group you
  meet when you attack a base). It does **not** affect raids. Contrast with vanilla
  `settlementGenerationWeight`, which is the world-map settlement *count* share (Q4.5).
  Also on `DefenseOptions`: `addEdgeDefense`, `addSandbags`, `addTurrets`, `cellsPerTurret` (30),
  `allowedTurretsDefs`, `addMortars`, `cellsPerMortar` (75), `allowedMortarsDefs`, `groupKindDef`.

- **`KCSG.SymbolDef : Def`** (XML node `<KCSG.SymbolDef>`) — *the* third-party-extensible way to place
  a named ThingDef into a faction settlement map. Fields include `thing` (string → `thingDef`),
  `replacementDef`, `maxStackSize`, `stuff`, `randomizeStuff`, `color`, `styleCategory`, `rotation`,
  `fuelPercent`, `powerPercent`, `plantGrowth`, `chanceToContainPawn`, `containPawnKindAnyOf`,
  `thingSetMakerDef` / `thingSetMakerDefForPlayer`, `crateStackMultiplier`, `pawnKindDef`, `isSlave`,
  `faction`, `numberToSpawn`, `spawnDead`, `spawnRotten`, `spawnFilthAround`, `defendSpawnPoint`,
  `spawnPartOfFaction` (default true). Spawned by `KCSG.SymbolUtils`.
  Reference the SymbolDef's defName inside `KCSG.StructureLayoutDef.layouts`
  (`List<List<string>>`, comma-separated grid rows).

- **`KCSG.CustomGenOption : DefModExtension`** on a FactionDef —
  `canSpawnSettlements`, `chooseFromlayouts`, `chooseFromSettlements`, `tiledStructures`,
  `symbolResolver(s)`, `tryFindFreeArea`, `preGenClear`, `fullClear`, `preventBridgeable`,
  `clearFogInRect`, **`scatterThings (List<ThingDef>)`**, `filthTypes`, `scatterChance` (0.4),
  `scaleWithQuest`.

- **`KCSG.SettlementLayoutDef : Def`** — `settlementSize` (42×42), `centerBuildings`
  (`centralBuildingTags` matching `StructureLayoutDef.tags`), `peripheralBuildings`, `roadOptions`,
  `stuffableOptions`, `propsOptions` (**`mainRoadPropsDefs` / `linkRoadPropsDefs` / `scatterPropsDefs`**),
  `defenseOptions`, `stockpileOptions` (**`fillWithDefs (List<ThingDef>)`**, `fillStorageBuildings`,
  `fillChance` 0.6, `stockpileValueMultiplier`, `maxValueStackIncrease` 40, `replaceOtherThings`).

- There is **no `itemsMenu` field** on `StructureLayoutDef` — grep over `VEF.dll` and `KCSG.dll`
  returns 0 hits.

**KCSG route for a guaranteed named ThingDef in a specific faction's base:** define a
`KCSG.SymbolDef` with `<thing>YourThingDef</thing>` + `numberToSpawn`, place its defName in a
`KCSG.StructureLayoutDef.layouts` grid, tag that layout, and reference the tag from
`SettlementLayoutDef.centerBuildings.centralBuildingTags` (or list the layout in
`chooseFromlayouts` on the FactionDef's `CustomGenOption`). Lower-effort but non-deterministic
alternatives: `CustomGenOption.scatterThings`, `stockpileOptions.fillWithDefs`.
This is heavier than `PawnKindDef.fixedInventory` (Q3.3) but it puts the item **in the base**
rather than **on a pawn**, which reads better narratively.

## 6.4 Bottom line
Neither settings-driven mod can carry our configuration. **Everything we need is plain vanilla
`PatchOperation*` XML on `FactionDef` / `PawnKindDef` / `TraderKindDef` / `ThingSetMakerDef`, plus
KCSG's all-XML Defs for the settlement-map side.** That is data-driven, byte-identical across
machines, and MP-hash-stable — which the two settings-driven mods are not.

---

# Q7 — Faction `techLevel` at runtime

## 7.1 Is it patchable / mutable?
`FactionDef.techLevel` is a plain public field on a `Def`. `Faction` serialises its def by
`Scribe_Defs.Look(ref def, "def")` (`RimWorld/Faction.cs:272`), i.e. **by defName** — the def object is
re-resolved from `DefDatabase` on every load. Consequences:
- A `PatchOperationReplace` on `FactionDef/techLevel` **applies retroactively to existing saves**
  the moment the mod is added; there is nothing per-save to migrate. **[CONFIRMED]**
- Runtime mutation (`faction.def.techLevel = X`) is process-global and **not saved** — it must be
  re-applied every session (which is what TechBlock does by writing `ParentFaction.def.techLevel`).
- **[NOT POSSIBLE]** to have two `Faction` instances of the same `FactionDef` with different tech
  levels — it is def-level state, not faction-instance state.

## 7.2 Complete list of readers of `<faction>.def.techLevel` in Assembly-CSharp
**[CONFIRMED — exhaustive grep of the decompiled assembly]**

**Player-faction reads (this is what TechBlock is aimed at):**
- `Verse/ResearchProjectDef.cs:103,107` — `CostApparent` / `ProgressApparent` use
  `CostFactor(Faction.OfPlayer.def.techLevel)`.
- `RimWorld/ResearchManager.cs:320` — actual research speed divisor.
- `RimWorld/MainTabWindow_Research.cs:477-481` — "tech level too low" warning + cost multiplier text.
- `RimWorld/Designator_Build.cs:117,121` — `minTechLevelToBuild` / `maxTechLevelToBuild` gating.

**Map/base generation (biggest visual + loot impact):**
- `RimWorld.BaseGen/SymbolResolver_Settlement.cs:23` — edge defenses only auto-generate at
  techLevel ≥ Industrial (else 50% chance); `:70` — firefoam poppers require ≥ Industrial.
- `RimWorld.BaseGen/SymbolResolver_EdgeDefense.cs:69`, `SymbolResolver_BasePart_Indoors_Leaf_BatteryRoom.cs:35`,
  `..._Leaf_Brewery.cs:35`, `..._Outdoors_Leaf_PowerPlant.cs:35`,
  `..._Outdoors_Division_Grid.cs:146`, `SymbolResolver_IndoorLighting.cs:12`,
  `SymbolResolver_OutdoorLighting.cs:15`, `SymbolResolver_Interior_Brewery.cs:22`,
  `SymbolResolver_FillWithBeds.cs:10`, `SymbolResolver_RandomlyPlaceMealsOnTables.cs:12`,
  `InteriorSymbolResolverUtility.cs:28`, `SymbolResolver_WorkSite_Mining.cs:64`.
- `RimWorld.BaseGen/BaseGenUtility.cs:21,37,109` — wall/floor stuff selection, carpet only above Neolithic.
- `RimWorld.BaseGen/SymbolResolver_LootScatter.cs:22`, `SymbolResolver_Stockpile.cs:51,53`,
  `SymbolResolver_ThingSet.cs:24`, `SymbolResolver_Interior_PrisonCell.cs:10`,
  `RimWorld/MapGenUtility.cs:896` — **loot ThingSetMaker `techLevel` param**.
- `RimWorld/GenStep_Turrets.cs:42` — turret-owning faction must be ≥ Industrial.
- `RimWorld/GenStuff.cs:218` — `RandomStuffInexpensiveFor(thingDef, faction.def.techLevel)`.

**Pawn generation:**
- `RimWorld/PawnApparelGenerator.cs:613,617` (via `CorrectFactionForApparel`) — **free warm layer only**.
- `RimWorld/PawnInventoryGenerator.cs:90,131` — addiction drugs and combat-enhancing drugs must be
  `x.techLevel <= faction.def.techLevel`.
- `RimWorld/PawnAddictionHediffsGenerator.cs:76` — which chemicals a pawn can be addicted to.
- `RimWorld/PawnRelationWorker.cs:61-62`, `PawnRelationWorker_Sibling.cs:125`, `Verse/Pawn.cs:1855`,
  `PawnBanishUtility.cs:59` — relation/faction-pick heuristics (`tryMedievalOrBetter`).

**Incidents / quests / world:**
- `RimWorld/FactionManager.cs:177,185` — `TryGetRandomNonColonyHumanlikeFaction` /
  `RandomEnemyFaction(minTechLevel:)`; weight ×0.1 for below-Medieval when `tryMedievalOrBetter`.
- `RimWorld/PawnsArrivalModeWorker.cs:16` — `PawnsArrivalModeDef.minTechLevel`
  (**this is what blocks drop-pod raids for low-tech factions**).
- `RimWorld/SitePartDef.cs:167` — `minFactionTechLevel`.
- `RimWorld/LordToil_Siege.cs:95,322`, `RimWorld.BaseGen/SymbolResolver_MannedMortar.cs:55` —
  mortar shell selection.
- `RimWorld/ChoiceLetter_RansomDemand.cs:31`, `FactionDialogMaker.cs:354` — < Industrial branches.
- `RimWorld.Planet/PeaceTalks.cs:152` — reward ThingSetMaker techLevel.
- `RimWorld.QuestGen/QuestGen_Pawns.cs:192,262`, `QuestNode_GetPawn.cs:124,220`,
  `QuestNode_Root_Gravship_Wreckage.cs:91`, `QuestNode_Root_MysteriousCargo.cs:91`,
  `QuestNode_Root_PollutionDump.cs:71`, `QuestNode_Root_PollutionRetaliation.cs:82`,
  `QuestNode_Root_Mission_AncientComplex.cs:309`, `QuestNode_Root_Hack_Spacedrone.cs:97` —
  quest faction eligibility (several require `techLevel > Medieval`).

## 7.3 Risks of patching faction techLevel via XML
1. **Raider gear does NOT follow techLevel.** Lowering a faction to Neolithic will *not* take guns off
   its pawns — that is entirely `PawnKindDef.weaponTags` + `weaponMoney`. You must edit the
   `pawnGroupMakers` / kinds too. (Known KCSG note: `defenseOptions` turrets/mortars need ≥ Industrial,
   which is the same `SymbolResolver_EdgeDefense`/`GenStep_Turrets` gate.)
2. **Base loot silently shifts.** `SymbolResolver_LootScatter` / `_Stockpile` pass
   `faction.def.techLevel` into `ThingSetMakerUtility.GetAllowedThingDefs`, which hard-filters
   `x.techLevel <= parms.techLevel`. Dropping a faction to Neolithic removes all
   industrial+ items from its settlement loot pool.
3. **Arrival modes.** `PawnsArrivalModeWorker:16` — dropping below a mode's `minTechLevel` removes
   drop pods / gravship arrivals for that faction; the pool can empty and fail silently.
4. **Quest eligibility.** Many `QuestNode_Root_*` require `techLevel > 2` (Medieval). Lowering a
   faction can quietly starve those quest lines if it was the only eligible faction.
5. **Empty-pool footguns.** `FactionManager.RandomEnemyFaction(minTechLevel:)` and
   `GenStep_Turrets` fall back to `RandomEnemyFaction()` or `RandomElementWithFallback` — silent.
6. **`Faction.OfPlayer.def.techLevel` is the research cost multiplier.** Do not patch the player
   FactionDef's techLevel casually; TechBlock already writes it at runtime and a static XML patch
   will fight it.
7. **Multiplayer:** XML patches are deterministic and identical across clients (mod files match), so
   patching is MP-safe. **Runtime** mutation from mod settings is not, unless settings match exactly.

---
