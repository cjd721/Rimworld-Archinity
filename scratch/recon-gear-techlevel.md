# Recon: how RimWorld 1.6 enforces era-appropriate raider gear

All findings verified against the 1.6 decompile of
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`
(ilspycmd) and shipped Core XML under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\`.

## Verdict up front

The prior conclusion — "`PawnWeaponGenerator` reads only `weaponTags` and `weaponMoney`; techLevel is
never consulted" — is **correct for weapons** and **wrong as a general statement about gear**.

- **Weapons: no techLevel filter of any kind.** Era-appropriateness is 100% emergent from
  hand-authored `weaponTags` sets, which vanilla keeps in disjoint per-era namespaces.
- **Apparel: there IS a hard `FactionDef.techLevel` vs `ThingDef.techLevel` filter**
  (`CorrectFactionForApparel`) — but it only guards the *free warmth layer*, not the main
  apparel roll, which is also tag-driven.
- **Inventory (drugs): there IS a hard `ThingDef.techLevel > Faction.def.techLevel` reject.**

So the user's intuition ("something enforces it") is right about the *observed outcome*, but the
mechanism is authored tag hygiene, not a systemic gate. A modded weapon that reuses the tag
`NeolithicRangedBasic` will be carried by `Tribal_Archer` even if its `techLevel` is `Spacer`.

---

## Q1 — Weapon selection call path for a spawned raider

`PawnGenerator.GeneratePawn` → `GenerateNewPawnInternal` → `GenerateGearFor` (line 1166,
`Verse.PawnGenerator`):

```csharp
private static void GenerateGearFor(Pawn pawn, PawnGenerationRequest request)
{
    PawnApparelGenerator.GenerateStartingApparelFor(pawn, request);
    PawnInventoryGenerator.GenerateInventoryFor(pawn, request);
    if (!request.DontGiveWeapon)
    {
        PawnWeaponGenerator.TryGenerateWeaponFor(pawn, request);
    }
}
```

### Candidate pool construction — `PawnWeaponGenerator.Reset()`

```csharp
allWeaponPairs = ThingStuffPair.AllWith(IsWeapon);
...
static bool IsWeapon(ThingDef td)
{
    if (td.equipmentType == EquipmentType.Primary)
        return !td.weaponTags.NullOrEmpty();
    return false;
}
```

Pool = every `ThingDef` with `equipmentType == Primary` **and** a non-empty `weaponTags`, crossed
with every legal stuff. No techLevel, no faction. Per-def commonality is then normalised against
`ThingDef.generateCommonality`.

### `PawnWeaponGenerator.TryGenerateWeaponFor(Pawn, PawnGenerationRequest)`

Early-out guard (all must pass, else pawn is unarmed):

1. `pawn.kindDef.weaponTags != null && Count != 0`
2. `pawn.RaceProps.ToolUser`
3. `pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation)`
4. `!pawn.WorkTagIsDisabled(WorkTags.Violent)`

Then `float randomInRange = pawn.kindDef.weaponMoney.RandomInRange;` and the single filter loop —
this is the entire filter set, in source order:

```csharp
if (!(w2.Price > randomInRange)
 && (pawn.kindDef.weaponTags == null || pawn.kindDef.weaponTags.Any((string tag) => w2.thing.weaponTags.Contains(tag)))
 && (pawn.kindDef.weaponStuffOverride == null || w2.stuff == pawn.kindDef.weaponStuffOverride)
 && (!w2.thing.IsRangedWeapon || !pawn.WorkTagIsDisabled(WorkTags.Shooting))
 && (w2.stuff == null || w2.stuff.stuffProps.allowedInStuffGeneration)
 && (!(w2.thing.generateAllowChance < 1f) || Rand.ChanceSeeded(w2.thing.generateAllowChance, pawn.thingIDNumber ^ w2.thing.shortHash ^ 0x1B3B648)))
{
    workingWeapons.Add(w2);
}
```

Ordered filter list:

| # | Condition | Field |
|---|---|---|
| 1 | `pair.Price <= weaponMoney.RandomInRange` | `PawnKindDef.weaponMoney` (price *ceiling*, not a floor) |
| 2 | tag intersection non-empty | `PawnKindDef.weaponTags` ∩ `ThingDef.weaponTags` |
| 3 | stuff override match | `PawnKindDef.weaponStuffOverride` |
| 4 | ranged weapons rejected if Shooting disabled | `WorkTags.Shooting` |
| 5 | stuff generatable | `stuffProps.allowedInStuffGeneration` |
| 6 | seeded rarity roll | `ThingDef.generateAllowChance` |

Weighted pick: `pair.Commonality * pair.Price * ideoFactor * xenotypeFactor`
(`IdeoWeaponDisposition.Noble` = 100×, `Despised` = 0.001×; `Xenotype.forbiddenWeaponClasses` = 0×).
Then style, `biocodeWeaponChance`, equip.

**`techLevel` appears nowhere** in `PawnWeaponGenerator` — not `ThingDef.techLevel`, not
`Faction.def.techLevel`, not `PawnKindDef`. `techHediffsRequired` is unrelated (it lives in
`PawnTechHediffsGenerator.GenerateTechHediffsFor`, which filters on `techHediffsTags` +
`BaseMarketValue <= techHediffsMoney` and also never touches techLevel).

**The one indirect techLevel touch in the gear path** is in the sibling call
`PawnInventoryGenerator.GenerateInventoryFor` → `GiveDrugsIfAddicted` / `GiveCombatEnhancingDrugs`:

```csharp
if (p.Faction != null && (int)x.techLevel > (int)p.Faction.def.techLevel)
{
    return false;
}
```

So tribal raiders can't spawn carrying go-juice, but *can* spawn carrying a charge rifle if you
tag one `NeolithicRangedBasic`.

---

## Q2 — Apparel: `PawnApparelGenerator.GenerateStartingApparelFor`

Guard: `pawn.RaceProps.ToolUser && pawn.RaceProps.IsFlesh && !pawn.RaceProps.IsAnomalyEntity`.

Setup:
- `money = pawn.kindDef.apparelMoney.RandomInRange`
- `neededWarmth = ApparelWarmthNeededNow(...)`, `needVacuum = NeedVacuumResistance(...)`,
  `allowHeadgear = Rand.Value < pawn.kindDef.apparelAllowHeadgearChance`,
  `toxic = ApparelToxicEnvironmentToAddress(...)`
- one `Rand.Int` fixed seed for the whole set

### Stage 1 — candidate filter, `CanUsePair(pair, pawn, money, allowHeadgear, fixedSeed)`

In order:
1. `pair.Price > moneyLeft` → reject (`PawnKindDef.apparelMoney`)
2. `!allowHeadgear && IsHeadgear(pair.thing)` → reject
3. `!pair.thing.apparel.PawnCanWear(pawn)` → reject (body/gender/age/dev-stage)
4. `PawnKindDef.apparelTags` non-empty → require intersection with `thing.apparel.tags`
5. `PawnKindDef.apparelDisallowTags` → reject on any intersection
6. `!kindDef.ignoreApparelAllowChance && thing.generateAllowChance < 1f` → seeded roll

**No techLevel here.**

### Stage 2 — set assembly, `GenerateWorkingPossibleApparelSetFor`

- `GenerateSpecificRequiredApparel` — `PawnKindDef.specificApparelRequirements`
  (`ApparelRequirementTagsMatch`, `ApparelRequirementHandlesThing`, `CanUseStuff`, `PawnCanWear`,
  no overlap)
- `PawnKindDef.apparelRequired` — forced defs (e.g. tribals' `Apparel_WarVeil`), age-checked
- greedy weighted fill by `Commonality`, subject to `CanUseStuff` and `!PairOverlapsAnything`,
  stopping on money or a 10% early-out

`CanUseStuff` is where faction enters, but **on stuff, not tech**:

```csharp
if (pair.stuff != null && pawn.Faction != null && !pawn.kindDef.ignoreFactionApparelStuffRequirements
    && !pawn.Faction.def.CanUseStuffForApparel(pair.stuff))
{
    return false;
}
```
`FactionDef.CanUseStuffForApparel` → `apparelStuffFilter.Allows(stuffDef)` (null filter = allow all).
Core sets `apparelStuffFilter` only on `Factions_Player.xml`, `Factions_Hidden.xml`,
Royalty's `Faction_Empire.xml` and Odyssey's player faction. **`TribeBase` does not set it.**

### Stage 3 — retry loop (up to ~80 attempts)

Rejects on: spent < 45–80% of money (first 10 tries, 85% of the time), doesn't cover Torso,
coat-but-no-shirt, `SatisfiesNeededWarmth`, `SatisfiesNeededToxicEnvironmentResistance`, naked.

### Stage 4 — free layers — **THE ONLY techLevel GATE**

`AddFreeWarmthAsNeeded` (fires when `!kindDef.apparelIgnoreSeasons` and warmth is unmet) picks a
free parka and/or hat via `ParkaPairValidator` / `HatPairValidator`, both of which end with
`CorrectFactionForApparel(homeFaction, pa.thing)`:

```csharp
private bool CorrectFactionForApparel(FactionDef faction, ThingDef apparel)
{
    if (faction != null)
    {
        if (apparel.apparel.anyTechLevelCanUseForWarmth)
            return true;
        if ((int)faction.techLevel >= 4 && apparel.techLevel == TechLevel.Neolithic)
            return false;
        if (faction.techLevel == TechLevel.Neolithic && (int)apparel.techLevel >= 4)
            return false;
    }
    return true;
}
```

(`4` == `TechLevel.Industrial`.) What it actually gates: **only** the free warmth parka/hat handed
out when the generated set is too cold. It stops a tribal from being gifted a free industrial
parka and an industrial faction from being gifted a free neolithic one. It does **not** touch the
main apparel roll, `apparelRequired`, `specificApparelRequirements`, the free toxic-resistance
layer, or the free vacuum layer. Note `Apparel_Parka` itself sets
`<anyTechLevelCanUseForWarmth>true</anyTechLevelCanUseForWarmth>` and `techLevel Neolithic`, so it
short-circuits the check anyway.

---

## Q3 — THE CRUX: how vanilla actually achieves era-appropriateness

**It is purely emergent from hand-authored, era-namespaced tag sets. There is no systemic filter.**

### Core tribal PawnKindDefs
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\PawnKindDefs_Humanlikes\PawnKinds_Tribal.xml`

`TribalBase` (abstract) carries exactly one gear tag:
```xml
<apparelTags>
  <li>Neolithic</li>
</apparelTags>
```

| PawnKindDef | `weaponTags` | `weaponMoney` | `apparelMoney` | `apparelRequired` |
|---|---|---|---|---|
| `Tribal_Penitent` | `NeolithicMeleeBasic` | 90~150 | 50~100 | — |
| `Tribal_Archer` | `NeolithicRangedBasic` | 80~80 | 180~350 | — |
| `Tribal_Warrior` | `NeolithicMeleeDecent` | 150~150 | 200~300 | `Apparel_WarVeil` |
| `Tribal_Hunter` | `NeolithicRangedDecent` | 100~100 | 200~300 | `Apparel_WarVeil` |
| `Tribal_Trader` | (inherits Hunter) | 100~100 | 200~300 | `Apparel_TribalHeaddress` |
| `Tribal_Berserker` | `NeolithicMeleeAdvanced` | 300~300 | 200~550 | `Apparel_WarMask` |
| `Tribal_HeavyArcher` | `NeolithicRangedHeavy` | 250~250 | 200~550 | `Apparel_WarMask` |
| `Tribal_ChiefMelee` | `NeolithicMeleeAdvanced`, **`MedievalMeleeAdvanced`** | 500~1000 | 450~750 | `Apparel_TribalHeaddress`, `Apparel_PlateArmor` |
| `Tribal_ChiefRanged` | `NeolithicRangedChief` | 500~1000 | 450~750 | as above |

`Tribal_ChiefMelee` is the proof: it deliberately opts into `MedievalMeleeAdvanced`, so a
`techLevel Medieval` longsword spawns on a Neolithic-faction pawn. If any systemic techLevel gate
existed, that would be impossible.

### Weapon tag namespaces are disjoint by hand
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\ThingDefs_Misc\Weapons\`

| Weapon | file | `techLevel` | `weaponTags` |
|---|---|---|---|
| `Bow_Short` | `RangedNeolithic.xml` | Neolithic | `NeolithicRangedBasic` |
| `Bow_Recurve` | `RangedNeolithic.xml` | Neolithic | `NeolithicRangedDecent` |
| `Bow_Great` | `RangedNeolithic.xml` | Neolithic | `NeolithicRangedHeavy`, `NeolithicRangedChief` |
| `Pila` | `RangedNeolithic.xml` | Neolithic | `NeolithicRangedHeavy`, `NoRelic` |
| `MeleeWeapon_Club` | `MeleeNeolithic.xml` | Neolithic | `NeolithicMeleeBasic` |
| `MeleeWeapon_Knife` | `MeleeNeolithic.xml` | Neolithic | `MedievalMeleeBasic`, `NeolithicMeleeBasic` |
| `MeleeWeapon_Ikwa` | `MeleeNeolithic.xml` | Neolithic | `NeolithicMeleeDecent` |
| `MeleeWeapon_Spear` | `MeleeNeolithic.xml` | Neolithic | `NeolithicMeleeAdvanced`, `MedievalMeleeAdvanced`, `Spear` |
| `MeleeWeapon_Mace` | `MeleeMedieval.xml` | Medieval | `MedievalMeleeDecent` |
| `MeleeWeapon_Gladius` | `MeleeMedieval.xml` | Medieval | `MedievalMeleeDecent` |
| `MeleeWeapon_LongSword` | `MeleeMedieval.xml` | Medieval | `MedievalMeleeAdvanced`, `LongSword` |
| `Gun_Revolver` | `RangedIndustrial.xml` | Industrial | `SimpleGun`, `Revolver` |
| `Gun_AssaultRifle` | `RangedIndustrial.xml` | Industrial | `IndustrialGunAdvanced`, `AssaultRifle` |
| `Gun_ChargeRifle` | `RangedSpacer.xml` | Spacer | `SpacerGun` |
| `Gun_ChargeLance` | `RangedSpacer.xml` | Spacer | `MechanoidGunMedium`, `SpacerGun` |

The abstract `BaseWeaponNeolithic` declares `<weaponTags><li>Neolithic</li></weaponTags>`, but every
concrete child re-declares `weaponTags` (which replaces the inherited list), so the umbrella
`Neolithic` tag never survives onto a concrete weapon — and no Core PawnKindDef asks for it.

**Conclusion:** the only thing preventing `Tribal_Archer` from spawning with a charge rifle is that
nobody wrote `SpacerGun` into `Tribal_Archer.weaponTags`, and nobody wrote `NeolithicRangedBasic`
onto `Gun_ChargeRifle`. `weaponMoney` (80 silver for `Tribal_Archer`) is a soft second line of
defence, but it is a price ceiling, not an era check — a cheap-but-spacer weapon would pass it.

---

## Q4 — Is there ANY systemic techLevel gate on gear? — Enumerated

Full-assembly grep for `techLevel` across the 28 MB decompile. Every comparison of a **faction**
techLevel against a **ThingDef** techLevel:

| Location | Comparison | What it gates |
|---|---|---|
| `PawnApparelGenerator.PossibleApparelSet.CorrectFactionForApparel` | `faction.techLevel` ↔ `apparel.techLevel` | **free warmth parka/hat only** |
| `PawnInventoryGenerator.GiveDrugsIfAddicted` | `x.techLevel > p.Faction.def.techLevel` | addiction drugs in inventory |
| `PawnInventoryGenerator.GiveCombatEnhancingDrugs` | `x.techLevel > pawn.Faction.def.techLevel` | combat drugs in inventory |
| `DrugPolicyUtility`-adjacent (`allDrugs.Any(... x.techLevel <= faction.def.techLevel)`) | drug availability | not gear |
| `TurretGunUtility.TryFindRandomShellDef(..., lord.faction.def.techLevel, ...)` | `x.techLevel <= techLevel` | mortar shell choice for raid mortars |
| `GenStuff.AllowedStuffsFor / RandomStuffInexpensiveFor(thingDef, faction?.def.techLevel)` | `stuff.techLevel <= faction techLevel` | **stuff** for map-gen buildings, not pawn gear |
| `BaseGenUtility.*`, `SymbolResolver_*` (`faction.def.techLevel < 4/3`) | building/furniture picks in settlement gen | not pawn gear |
| `ThingSetMakerUtility.GetAllowedThingDefs(parms)` | `x.techLevel <= parms.techLevel` | loot/reward/trade sets |
| `ThingSetMaker_StockGenerators` / `StockGenerator.maxTechLevelGenerate/Buy` | `t.techLevel <= max` | trader stock |
| `PawnsArrivalModeWorker.CanUseWith` | `parms.faction.def.techLevel < def.minTechLevel` | drop-pod/arrival mode, not gear |
| `SitePartDef.FactionCanOwn` | `faction.def.techLevel < minFactionTechLevel` | world site ownership |
| `ThingSetMakerUtility` weighting (`techLevel2 < techLevel && techLevel2 <= 2 && (IsApparel \|\| IsWeapon)`) | de-prioritises neolithic gear in reward sets | rewards only |

`ThingSetMakerUtility.GetAllowedThingDefs` **does** apply a real ceiling:
```csharp
TechLevel techLevel = parms.techLevel.GetValueOrDefault();
IEnumerable<ThingDef> source = parms.filter.AllowedThingDefs;
if (techLevel != 0)
    source = source.Where((ThingDef x) => (int)x.techLevel <= (int)techLevel);
```
…and `parms.techLevel` is set from `faction?.def.techLevel` at the raid-loot / site-loot call sites.
But that governs **dropped loot and stockpile contents**, never what a pawn is holding.

**Explicit statement: there is NO systemic `Faction.def.techLevel` vs `ThingDef.techLevel` check on
equipped weapons anywhere in RimWorld 1.6, and the only such check on apparel is the free-warmth
layer.** Raider weapon era is a pure content-authoring convention.

---

## Q5 — What `Ignorance Is Bliss` (`dame.ignorance`, workshop id `2554423472`) actually does

Assembly: `...\workshop\content\294100\2554423472\1.6\Assemblies\IgnoranceIsBliss.dll`
Namespaces: `DIgnoranceIsBliss`, `DIgnoranceIsBliss.Core_Patches`,
`DIgnoranceIsBliss.RimWar_Patches`, `DIgnoranceIsBliss.WinstonWaves_Patches`.

### Mechanism: it gates WHICH FACTIONS may appear. It never touches gear.

Grep of the whole assembly: zero references to `PawnWeaponGenerator`, `PawnApparelGenerator`,
`PawnGenerator`, `weaponTags`, `apparelTags`, `ThingDef.techLevel`. Every single decision funnels
through `IgnoranceBase.FactionInEligibleTechRange(Faction f)` → `TechIsEligibleForIncident(f.def.techLevel)`.

Harmony patches, complete list:

| Patch | Target | Effect |
|---|---|---|
| `Patch_FactionCanBeGroupSource_Postfix` | `IncidentWorker_PawnsArrive.FactionCanBeGroupSource` | `__result = __result && FactionInEligibleTechRange(f)` — **this is the main raid gate.** `IncidentWorker_RaidEnemy : IncidentWorker_Raid : IncidentWorker_PawnsArrive`, so it covers raids, and also visitors/traders/caravans that route through `PawnsArrive`. |
| `Patch_PawnsArriveCanFireNowSub_Postfix` | `IncidentWorker_PawnsArrive.CanFireNowSub` | If `parms.faction` is out of range: with `ChangeQuests` on, **substitutes** a random eligible hostile faction; with it off, sets `__result = true` (i.e. lets it fire — a deliberate no-op fallback). |
| `Patch_TryGetRandomFactionForCombatPawnGroup_Prefix` | `PawnGroupMakerUtility.TryGetRandomFactionForCombatPawnGroup` | Injects the eligibility predicate **only if `validator == null`**. Callers that already pass a validator are unaffected. |
| `Patch_CanRun_Prefix` / `Patch_CanRun2_Prefix` | `QuestScriptDef.CanRun` (both overloads) | Only when `ChangeQuests` is on, and only for the hardcoded `questScriptDefs` dictionary (currently one entry: `ThreatReward_MechPods_MiscReward` → Ultra). |
| `Patch_UsableIncidentsInCategory_Postfix` | `StorytellerComp.UsableIncidentsInCategory` | Filters incidents by two hardcoded lookup tables — `incidentWorkers` (`IncidentWorker_MechCluster`/`CrashedShipPart` → Ultra; `Infestation`/`DeepDrillInfestation` → Animal) and `incidentDefNames` (a small list of modded incident defNames: Crystalloid, Ratkin, VFEM_BlackKnight, SW psychic/weapons cache, AA_Incident_BlackHive). |
| `Patch_FinishProject_Postfix` | `ResearchManager.FinishProject` | Recomputes the cached player tech level. |
| RimWar / Winston Waves patches | third-party warband + wave spawners | Same faction-eligibility test. |

### Core logic

```csharp
public static bool TechIsEligibleForIncident(TechLevel tech)
{
    if ((int)tech == 0) return true;                       // Undefined always passes
    if (UseFixedTechRange)
        return (int)tech >= FixedRange.min && (int)tech <= FixedRange.max;
    int num  = (int)PlayerTechLevel;
    int num2 = (int)tech;
    if (num < num2) {                                      // faction ahead of player
        if (NumTechsAhead >= 0) return num + NumTechsAhead >= num2;
    } else if (num > num2 && NumTechsBehind >= 0) {        // faction behind player
        return num - NumTechsBehind <= num2;
    }
    return true;
}

public static bool FactionInEligibleTechRange(Faction f)
{
    if (EmpireIsEligible(f) || MechanoidsAreEligible(f)) return true;
    return TechIsEligibleForIncident(f.def.techLevel);
}
```

### Settings and what each really controls

Mutually exclusive "how is my tech level computed" radio group (`Settings.WriteAll` enforces
exclusivity):

| Setting | Default | What it does in code |
|---|---|---|
| `useHighestResearched` | `false` | `GetPlayerTech()`: walk tech levels 7→1, return the first level where **any** `ResearchProjectDef.IsFinished`. |
| `usePercentResearched` | **`true`** | `GetPlayerTech()`: walk 7→1, return the first level where finished-count / total-count for that level ≥ `percentResearchNeeded`. Note the counter `num2` is **not reset per level**, so it accumulates from higher levels downward. |
| `percentResearchNeeded` | `0.75` | Threshold for the above; clamped 0.05–1.0. |
| `useActualTechLevel` | `false` | `GetPlayerTech()` returns `Faction.OfPlayer.def.techLevel` verbatim. Static unless another mod mutates it. |
| `useFixedTechRange` + `fixedRange` | `false`, `1~7` | Ignores the player entirely; allows factions whose `def.techLevel` sits inside `[min,max]`. |
| `NumTechsAhead` | `1` | Max levels a faction may be **above** you. `-1` = unlimited. |
| `NumTechsBehind` | `1` | Max levels a faction may be **below** you. `-1` = unlimited. |
| `EmpireIsAlwaysEligible` | **`true`** | Hard bypass: `f.def == FactionDefOf.Empire` → always eligible, regardless of tech gap. |
| `MechanoidsAreAlwaysEligible` | `false` | Same bypass for `FactionDefOf.Mechanoid`. |
| `changeQuests` | `false` | Enables the two `QuestScriptDef.CanRun` prefixes, and switches `CanFireNowSub` from "let it fire anyway" to "substitute an eligible faction". |
| `debugOutput` | `false` | Log spam. |

### The guarantee it actually provides

**Guarantee: a hostile faction whose `FactionDef.techLevel` is more than `NumTechsAhead` above (or
`NumTechsBehind` below) your computed tech level will not be selected as a raid source** (subject to
the Empire/Mechanoid bypasses, and subject to callers actually routing through
`IncidentWorker_PawnsArrive.FactionCanBeGroupSource`).

**Not guaranteed:**
- It does **not** change what gear the raiders of an eligible faction carry. A faction whose
  `techLevel` is `Neolithic` but whose PawnKindDefs carry `IndustrialGunAdvanced` weaponTags will
  still field assault rifles. Gear era is entirely on the faction/pawnkind author.
- It does not gate raids that bypass `FactionCanBeGroupSource` (custom incident workers,
  `IncidentParms.faction` forced by a quest/script, mechanoid clusters unless covered by the
  hardcoded `incidentWorkers` table).
- The `TryGetRandomFactionForCombatPawnGroup` prefix is a no-op whenever the caller supplies its own
  validator.
- With `changeQuests = false` (the default) and an out-of-range `parms.faction`, `CanFireNowSub`'s
  postfix sets `__result = true` — it does not block.
- It shows an in-game warning `DNoValidFactions` if `NumFactionsInRange() <= 0`; note the mod's own
  settings text warns "there are NO medieval factions in the vanilla game".

Bottom line for the user: **IIB is a faction-eligibility gate keyed on `FactionDef.techLevel`. It is
not, and cannot be, a gear-era guarantee.** It is complementary to — not a substitute for —
authoring correct `weaponTags` on your PawnKindDefs.

---

## Q6 — Minimal correct authoring for a Neolithic/Medieval-only faction

The whole job is tags + a couple of numbers. There is nothing systemic to lean on.

**Required:**

1. **`FactionDef.techLevel`** — set `<techLevel>Neolithic</techLevel>` (or `Medieval`).
   This buys you: IIB eligibility bucketing, the free-warmth `CorrectFactionForApparel` gate,
   drug-inventory exclusion, `raidLootMaker`/`ThingSetMaker` loot ceilings, settlement map-gen
   furniture, `IsNeolithicOrWorse()` behaviours. It buys you **nothing** on equipped weapons.

2. **`PawnKindDef.weaponTags`** — this is the actual enforcement. Use only era tags that exist
   solely on era-appropriate weapons:
   `NeolithicMeleeBasic / NeolithicMeleeDecent / NeolithicMeleeAdvanced`,
   `NeolithicRangedBasic / NeolithicRangedDecent / NeolithicRangedHeavy / NeolithicRangedChief`,
   `MedievalMeleeBasic / MedievalMeleeDecent / MedievalMeleeAdvanced`.
   Never use `Gun`, `SimpleGun`, `IndustrialGunAdvanced`, `SpacerGun`, `GunHeavy`, `GrenadeDestructive`,
   `AdvancedWeapon`, or the bare umbrella tag `Neolithic` (which no concrete Core weapon carries).
   Safest: copy the tag sets straight off `PawnKinds_Tribal.xml`.

3. **`PawnKindDef.weaponMoney`** — set a ceiling near the era's price band (tribal Core uses
   80–1000). A backstop only; it will not stop a cheap mis-tagged weapon.

4. **`PawnKindDef.apparelTags`** — `<li>Neolithic</li>` (Core `TribalBase`'s only apparel tag);
   for medieval, whatever tag your medieval apparel source uses. Optionally add
   `apparelDisallowTags` for belt-and-braces.

5. **`PawnKindDef.apparelRequired`** — force the era-signalling pieces (Core tribals force
   `Apparel_WarVeil` / `Apparel_WarMask` / `Apparel_TribalHeaddress` / `Apparel_PlateArmor`).
   These bypass `apparelTags` filtering entirely, so only list era-correct defs.

6. **`PawnKindDef.techHediffsTags` / `techHediffsMoney`** — if you don't want bionic tribals, leave
   `techHediffsTags` unset or restrict to `Poor`, and keep `techHediffsChance` low (Core tribal:
   `0.03`–`0.15`, `techHediffsMoney 50~50`). There is **no** techLevel filter in
   `PawnTechHediffsGenerator` — only tags and market value.

7. **`FactionDef.pawnGroupMakers`** — reference only your own era-correct PawnKindDefs. A single
   stray `Pirate`/`Mercenary_*` option in a group maker undoes everything above.

**Strongly recommended, easy to forget:**

8. **`FactionDef.apparelStuffFilter`** — Core `TribeBase` omits it, so tribal raiders can wear
   plasteel/hyperweave dusters if the stuff is generatable. Add a filter allowing only
   `Leathery` / `Fabric` (minus hyperweave) / `Woody` / `Stony` if you want that closed.

9. **`FactionDef.raidLootMaker`** and `caravanTraderKinds` / `baseTraderKinds` — point at
   Neolithic-tier makers (`TribeRaidLootMaker`, `Caravan_Neolithic_*`, `Base_Neolithic_Standard`).
   These *do* honour `parms.techLevel` via `ThingSetMakerUtility.GetAllowedThingDefs`, so setting
   `FactionDef.techLevel` correctly already does most of the work here.

10. **`FactionDef.allowedArrivalTemperatureRange` / `arrivalModeBlacklist`** — block drop pods, which
    otherwise read as spacer even with neolithic gear. `PawnsArrivalModeWorker.CanUseWith` honours
    `PawnsArrivalModeDef.minTechLevel` against your `FactionDef.techLevel` automatically, so a
    correct `techLevel` covers most of this; the blacklist is for anything with `minTechLevel` unset.

**Audit step:** after authoring, dump the debug table `PawnWeaponGenerator.WeaponPairs` (dev mode →
Debug output → weapon pairs) and confirm no non-era weapon shares a tag with your PawnKindDefs.
Cross-mod risk is real: any mod that tags a modern weapon `NeolithicMeleeBasic` (or whatever tag you
use) will inject it into your faction, because the pool is built from the *merged* def database with
no techLevel screen. Using a private tag namespace (e.g. `Archinity_NeoRangedBasic`) plus
PatchOperations to stamp it onto the specific weapons you approve is the only fully mod-proof option.
