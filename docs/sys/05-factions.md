# 05 — Factions & world

**Blocked by 01.** Which factions exist depends on which mods are enabled.

## What this system must do

Guarantee the factions we want are in every world, with the right gear, the right trade
stock, and reliable ways for the player to get named items from them.

The player-facing contract, from `Player Progression Ideology.txt`:

> I need item X for research Y. Faction Z has it. I can quest for it, trade for it, or
> raid them for it — and I can find out which.

**All three routes are buildable.** Verified below.

---

## The single most important correction

**Faction `techLevel` does not control what raiders carry or what traders sell.**

- `PawnWeaponGenerator` reads **only** `weaponTags` ∩ `ThingDef.weaponTags`, with
  `weaponMoney` as a price ceiling. Faction techLevel is **never consulted**.
- `PawnApparelGenerator` reads faction techLevel exactly once — in the free-warm-parka
  fallback.
- Trade ignores faction techLevel entirely. Only per-generator `maxTechLevelGenerate` /
  `maxTechLevelBuy` matter, and `StockGenerator_SingleDef` / `_MultiDef` ignore even those.

So **era-appropriate factions are an authoring job on `PawnKindDef`s and `TraderKindDef`s,
not a techLevel setting.** Patching `FactionDef.techLevel` and expecting medieval raiders
to show up with medieval weapons does not work. This is the natural assumption and it is
wrong.

What faction techLevel *does* affect: settlement loot filtering, drop-pod raid availability
(`PawnsArrivalModeWorker.minTechLevel`), many `QuestNode_Root_*` requiring `> Medieval`, and
— for the *player* faction — the research cost multiplier TechBlock writes. Do not fight
TechBlock with a static patch there.

`FactionDef.techLevel` is def-level state saved by defName, so an XML patch **applies
retroactively to existing saves**. It **cannot** differ per faction instance of the same def.

---

## Route 1 — Guaranteed trade stock

`StockGenerator_SingleDef` with `countRange` minimum ≥ 1.

- **`countRange` is a uniform draw, not a chance.** `StockGenerator.RandomCountOf` returns
  `intRange.RandomInRange` when `totalPriceRange` is unset. The vanilla "sometimes zero"
  idiom is a *negative minimum* (`Gold: -40~120`) — so a min of 1 is genuinely guaranteed.
- It applies **no** techLevel, tag, or `PlayerAcquirable` filter. Only
  `tradeability.TraderCanSell()`.
- `baseTraderKinds` is **deterministic per settlement** (`[abs(HashOffset()) % count]`), so
  a single entry means that trader everywhere for that faction.
- Random orbital arrivals **ignore `orbitalTraderKinds`** and scan all `orbital=true`
  TraderKindDefs by commonality.

**1.6 has no `StockGenerator_Armor` / `_Weapons` / `_BuyCategory`** — folded into
`StockGenerator_MarketValue`. Older docs and wiki pages referencing them are stale.

## Route 2 — Guaranteed drops from raiding a base

Two corrections to the obvious approaches, both confirmed:

1. **`FactionDef.settlementLootMaker` is not read by ground faction bases.** Its only
   consumer is `GenStep_SettlementPawnsLoot`, referenced solely by Odyssey's
   `SettlementPlatform` (orbital) generator. Ground bases run
   `Base_Faction` → `GenStep_Settlement` → `SymbolResolver_Settlement`, which **hardcodes**
   `ThingSetMakerDefOf.MapGen_DefaultStockpile` at 1800 value, filtered to
   `faction.def.techLevel` via `SymbolResolver_LootScatter`.
2. **Trader stock is never loot.** `SettlementDefeatUtility.CheckDefeated` →
   `Settlement.Destroy` → `Settlement_TraderTracker.TryDestroyStock()` literally `Destroy()`s
   every non-pawn item. You cannot raid a settlement for the things its trader was selling.

### The mechanism that works: `PawnKindDef.fixedInventory`

`PawnInventoryGenerator.GenerateInventoryFor` runs **unconditionally** — no techLevel check,
no money check, no `PlayerAcquirable` check. It also auto-equips weapons and auto-wears
apparel.

Put the carrying kind in the faction's **`Settlement`** pawnGroupMaker (for base assaults)
**and** its **`Combat`** pawnGroupMaker (so it can also arrive as a raider).

Supporting options:
- `FactionDef.raidLootMaker` + `raidLootValueFromPointsCurve` → `RaidLootDistributor` stuffs
  raider inventories and **skips the techLevel filter entirely**. Good for raids *on the
  player*.
- KCSG `SymbolDef` with `<thing>` inside a `StructureLayoutDef` — the per-faction in-base
  alternative, useful for placing a thing in a specific room.

Dead ends, recorded so nobody retries them: `CompProperties_LootSpawn` hard-casts its parent
to `Building_Crate`. `LayoutRoomDef.thingSetMakerDef` only feeds `RoomContents_Stockpile`
(layout maps, not BaseGen). `GenStep_ScatterThings` is per-`MapGeneratorDef`, i.e. global.

### Gear guarantee ranking

`fixedInventory` > `apparelRequired` / unique `weaponTags` > `techHediffsRequired`.

`apparelRequired` bypasses `CanUsePair` entirely — no tags, no money, may go negative.
Set `biocodeWeaponChance=0` and avoid `specificApparelRequirements` `Locked`/`Biocode` on
anything meant to be lootable.

## Route 3 — Quests

See `sys/06`. `QuestNode_SetItemStashContents` is the verified, shipped mechanism.

---

## Getting factions into the world

- **`requiredCountAtGameStart` is dead code in 1.6.** Use `startingCountAtWorldCreation`.
- `maxConfigurableAtWorldCreation` 0 = never offered in the UI.
- `configurationListOrderPriority` is **purely the sort order of world-creation UI rows** —
  one reader, `FactionGenerator.ConfigurableFactions`. It guarantees nothing.
- `settlementGenerationWeight` is the world-map settlement **count** share. Weight 0 means
  the faction exists with **zero settlements**.
- `pawnGroupMultiplier` is **not vanilla** — it is `KCSG.DefenseOptions`, scaling
  settlement-map defender points only.
- `FactionDef.defaultSettlementGroupKindDef` is a dead private field.

### Adding a faction to an existing save does nothing

Silent, no error. `FactionManager.ExposeData` has no reconcile path — only a hardcoded DLC
backfill in `BackCompatibility.FactionManagerPostLoadInit`.

**[NOT POSSIBLE via XML]. [NEEDS C#]** but trivial:
`FactionGenerator.CreateFactionAndAddToManager(layer, def)` is public static.

Practical consequence: **the faction set must be final before world creation.** Since this
is one long co-op playthrough, that is a one-time gate — but it is a hard one.

### Possible live bug — but confirm the symptom exists first

**Do not start here until the worldgen contradiction in `MAP.md` is resolved.** Our own
recon files disagree about whether Drifters and Glitterites have ever generated: one says
never, another says worldgen was run and both rendered correctly.

*If* they genuinely never generate: `CanExistOnLayer` (`layerWhitelist` / `layerBlacklist`)
is the probable cause. Both are orbit-only factions, and it is the cheapest explanation.

*If* they already generate correctly, this whole item is void.

---

## The two mods that look like they'd help, and don't

- **Faction Customizer (`azravos.factioncustomizer`)** — zero custom Defs, zero data-driven
  config. It mutates live `Faction` / `Settlement` instances (name, colour, def pointer,
  leader, ideo, `baseGoodwill`, `kind`) stored in the savegame. **No** techLevel,
  pawnGroupMakers, traderKinds or gear tags. Its six ModSettings booleans are UI gates.
  It cannot carry our config.
- **Xenotype Spawn Control (`bs.xenotypespawncontrol`)** — ModSettings-only, and it **writes
  `FactionDef.xenotypeSet` at `StaticConstructorOnStartup`**. That is a multiplayer hazard
  unless settings match byte-for-byte, and it is unnecessary: we can patch
  `<xenotypeSet><xenotypeChances>` directly.

Plain vanilla PatchOperations plus KCSG defs carry everything we need. Consider dropping
both mods.

---

## Settlement maps

- KCSG `CustomGenOption` in FactionDef `modExtensions` drives layouts (VFEM2 precedent).
- **`GetModExtension` returns the FIRST only — never add a second.**
- A missing `centralBuildingTags` tag throws `KeyNotFoundException` **mid-worldgen**.
- `count` is a soft target.
- `defenseOptions` turrets and mortars require `techLevel >= Industrial` — so medieval
  faction bases cannot use them. This is why the VFEM2 bases have no defences.
- Garrison = `faction.pawnGroupMakers` × `pawnGroupMultiplier`.
- Layouts can place pawns.
- Every modded ThingDef needs a hand-written SymbolDef.
- `_North` / `_East` / … variants are runtime and unpatchable.
- In-game exporter: **Architect → Orders → Export.**

`PawnGenOption` = kind + selectionWeight, `Cost = kind.combatPower`.
`ChoosePawnGenOptionsByPoints` weights by
`selectionWeight × PawnWeightFactorByMostExpensivePawnCostFractionCurve(cost/highestCost)`;
the curve `(0.2,0.01)(0.3,0.3)(0.5,1.0)` **suppresses cheap kinds at high points**. Relevant
if a low-combatPower kind is carrying a `fixedInventory` item — at high raid points it may
stop appearing.

---

## Work items

- [ ] Decide the **final faction roster**. This must be settled before world creation and
      cannot be changed after without C#.
- [ ] **First:** resolve the worldgen contradiction in `MAP.md`. Only if the two factions
      genuinely never generate, check their `layerWhitelist` / `layerBlacklist`.
- [ ] Set `startingCountAtWorldCreation` on everything we require. Four VFEM2 factions ship
      at 0 (`KingdomRough`, `KingdomSavage`, `ClanSavage`, `CivilClan`) and currently need
      hand-adding at world creation — fix at the def level instead.
- [ ] **Author era-appropriate `PawnKindDef`s** — weaponTags, apparelTags, weaponMoney,
      apparelMoney per faction per era. This is the real work of "medieval factions feel
      medieval," and techLevel will not do it for you.
- [ ] Build the **acquisition ledger**: for every gated item, which faction supplies it and
      by which route (trade / raid / quest). This is the artifact that makes `sys/04`'s
      research gating legible. Cross-check against `check_availability.py`'s 2-route rule.
- [ ] Author `TraderKindDef`s with `StockGenerator_SingleDef` entries for guaranteed items.
- [ ] Author `fixedInventory` kinds for raid-obtainable items; place in both `Settlement`
      and `Combat` pawnGroupMakers. Watch the cheap-kind suppression curve.
- [ ] Author `Archinity_CurtainWall` / `_CastleTower` / `_Gatehouse` as tagged
      `StructureLayoutDef`s; `PatchOperationAdd` into `VFEM2_MedievalFactionBase`.
      Est. 6–9 layouts, 4–6 sessions. **KCSG perimeter risk: Poisson-placed wall segments
      may not tile into a continuous wall — test early.**
- [ ] Patch `FactionSiegeExtension.medievalSiege` + `ArtilleryMedieval_BaseDestroyer` onto
      VFEM2 factions; add `canSiege` (no VFEM2 faction sets it).
- [ ] Open question: can `RaidStrategyWorker_MedievalSiege`'s `techLevel == 3` check be
      satisfied for a Neolithic-tier siege without C#?
- [ ] Replace the two generated placeholder faction icons.
- [ ] Faction diplomacy + ideology pass across the world map — flagged, never touched.
- [ ] Evaluate dropping Faction Customizer and Xenotype Spawn Control.
- [ ] Note: Glitterites are `permanentEnemy` (not `naturalEnemy` — goodwill would soften).
- [ ] Note: vanilla bug — `OpportunitySite_MechanoidPlatform` is gated on the **Insect**
      faction existing. Do not prune Insects without checking.
