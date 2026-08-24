# Recon: VANILLA FACTION BASELINE (RimWorld 1.6.4871 rev590)

Generated 2026-08-24. Every claim below is read from decompiled `Assembly-CSharp.dll`
(`ilspycmd -p`) or from shipped XML under
`C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/`.

Decompile cache used (regenerate with
`ilspycmd -p -o <dir> ".../RimWorldWin64_Data/Managed/Assembly-CSharp.dll"`):
`C:\Users\cjd72\AppData\Local\Temp\claude\C--Users-cjd72-Claude\4539541a-e10d-46a7-b6fa-874f67b08142\scratchpad\decomp`

Paths are `<namespace-dir>/<File>.cs` relative to that cache root.

**Tags:** `[VERIFIED]` = read in decompiled source or shipped XML, quoted here.
`[INFERRED]` = reasoned from verified facts, not directly observed.
`[NOT VERIFIED]` = could not confirm; treat as open.

**Relationship to the prior pass.** `scratch/recon-factions.md` (2026-08-22) already covers
trade/`TraderKindDef`, raider gear (`weaponTags`/`apparelRequired`/`fixedInventory`),
guaranteed settlement loot, `pawnGroupMakers`, worldgen guarantees
(`settlementGenerationWeight`, `requiredCountAtGameStart` is dead on normal starts),
the full reader list for `faction.def.techLevel`, and a teardown of Faction Customizer /
Xenotype Spawn Control / KCSG. **This document does not repeat any of that.** It covers
the parts that pass did not touch: relations, goodwill, the world tick, settlement
lifecycle, quests, techprints, and runtime def substitution.

---

# EXECUTIVE ANSWER (read this first)

1. **Vanilla has essentially zero autonomous faction behaviour.** The world tick does
   four faction-related things, all of which are about the *player*: recache
   player-goodwill situation caps (every 1000 ticks), apply settlement-proximity goodwill
   penalties to the *player* (every 900k ticks = 15 days), drift each faction's goodwill
   *with the player* toward its natural value (a ±10 nudge after 50 days out of band),
   and tick kidnapped-pawn trackers. Nothing else.
2. **`Faction.RelationWith` fully supports non-player pairs, and the entire goodwill
   pipeline works between two NPC factions — but nothing in vanilla ever calls it that
   way.** Every single mutation site in the assembly has `Faction.OfPlayer` on one side.
   This is the single most important finding: *the machinery is complete and unused.*
3. **Techprints are real, in 1.6, with the exact field names the design assumed.**
   Royalty-gated. They work as quest rewards, trader stock, and ThingSetMaker output.
4. **The quest layer confirms the same asymmetry.** A quest *can*, in pure XML, name a
   specific faction, impose a telegraphed deadline, and change that faction's goodwill
   **with the player** on failure. It **cannot** touch an NPC↔NPC pair — every goodwill
   QuestPart hardcodes `Faction.OfPlayer` and takes only one faction field. The two
   QuestParts that do accept an arbitrary `(faction1, faction2)` pair are a *lock* and a
   *watcher*, never a writer.
5. The cheap levers that already exist and that vanilla honours everywhere:
   `Faction.defeated` (one bool), NPC↔NPC `FactionRelation.kind`, world-object
   add/remove for settlements, and `FactionGenerator.CreateFactionAndAddToManager`.

---

# Q1 — THE `FactionDef` SURFACE

`RimWorld/FactionDef.cs` — complete field list, 1.6.4871. **[VERIFIED]**

## 1.1 Corrections to assumptions in the brief

| Assumed field | Reality |
|---|---|
| `naturalColonyGoodwill` | **DOES NOT EXIST IN 1.6.** Zero occurrences anywhere in the assembly. Natural goodwill is computed at runtime by `GoodwillSituationManager.GetNaturalGoodwill(faction)` summing `GoodwillSituationDef.naturalGoodwillOffset` over all situation defs. **[VERIFIED — grep returns nothing]** |
| `permanentEnemy` | Exists, real, read in 5+ places. |
| `techLevel` | Exists. Reader list already enumerated in `recon-factions.md` §7.2. |
| `raidCommonalityFromPointsCurve` | Exists and is live — `PawnGroupMakerUtility.cs:362,379` weights faction selection for raids by `f.def.RaidCommonalityFromPoints(points)`. |
| `pawnGroupMakers` | Exists. Covered in `recon-factions.md` Q4. |
| `settlementGenerationWeight` | Exists. Covered in `recon-factions.md` §4.5. |
| `allowedArrivalTemperatureRange` | Exists and is live (4 readers). |
| `mustStartOneEnemy` | **DEAD FIELD in 1.6.** Three occurrences, all inside `FactionDef.cs`: the declaration and a `ConfigErrors` warning about redundancy with `permanentEnemy`. **Nothing reads it for behaviour.** Setting it does nothing. **[VERIFIED]** |
| `defaultSettlementGroupKindDef` | Dead field (already noted in the prior pass). |

## 1.2 Behaviour-governing fields, by system

### Relations at world generation (the ONLY time relations are set from def)
```csharp
public bool mustStartOneEnemy;                            // DEAD — no readers
public bool naturalEnemy;                                 // initial goodwill -80; natural goodwill -130
public bool permanentEnemy;                               // -100, hard-locked
public bool permanentEnemyToEveryoneExceptPlayer;
public List<FactionDef> permanentEnemyToEveryoneExcept;
public bool hostileToFactionlessHumanlikes;               // GenHostility.cs:81,170
```
`Faction.TryMakeInitialRelationsWith(Faction other)` (`RimWorld/Faction.cs:390-429`) is
the whole of def-driven relation setup:
```csharp
int a2 = GetInitialGoodwill(this, other);
int b2 = GetInitialGoodwill(other, this);
int num = Mathf.Min(a2, b2);
FactionRelationKind kind = ((num > -10) ? ((num < 75) ? FactionRelationKind.Neutral
                                                     : FactionRelationKind.Ally)
                                        : FactionRelationKind.Hostile);
// GetInitialGoodwill: permanentEnemy → -100; permanentEnemyToEveryoneExceptPlayer && !b.IsPlayer → -100;
//                     permanentEnemyToEveryoneExcept lacking b.def → -100; naturalEnemy → -80; else 0.
```
**Consequence: two ordinary NPC factions always start at goodwill 0 / Neutral.**
Nothing in pure XML can make faction A start hostile to faction B specifically unless
one of them is permanently hostile to (nearly) everyone. `permanentEnemyToEveryoneExcept`
is the only XML lever that expresses a *targeted* hostility, and it is an allow-list
(hostile to all except the listed defs), not a deny-list. **[VERIFIED]**

### Raids / combat
```csharp
public SimpleCurve raidCommonalityFromPointsCurve;   // PawnGroupMakerUtility:362,379 — faction pick weight
public bool raidsForbidden;                          // PawnGroupMakerUtility:357; TimedDetectionRaids:51
public float earliestRaidDays;                       // IncidentWorker_RaidEnemy:20 (vs DaysPassedSinceSettle)
public bool canSiege;                                // RaidStrategyWorker_Siege:26
public bool canStageAttacks;                         // RaidStrategyWorker_StageThenAttack:25
public bool canPsychicRitualSiege;                   // RaidStrategyWorker_PsychicRitualSiege:80
public bool canUseAvoidGrid = true;                  // PawnUtility:454; RaidStrategyWorker_ImmediateAttackSmart:20
public bool autoFlee = true;                         // Lord.cs:308
public FloatRange attackersDownPercentageRangeForAutoFlee = (0.4, 0.7);  // Lord.cs:316 (Trigger_FractionPawnsLost)
public List<RaidStrategyDef> disallowedRaidStrategies;
public List<RaidAgeRestrictionDef> disallowedRaidAgeRestrictions;
public SimpleCurve maxPawnCostPerTotalPointsCurve;   // required if pawnGroupMakers != null
public List<PawnGroupMaker> pawnGroupMakers;
public PawnKindDef basicMemberKind;
public ThingSetMakerDef raidLootMaker;
public SimpleCurve raidLootValueFromPointsCurve;     // ConfigErrors HARD-REQUIRES this on every FactionDef
public ThingDef dropPodActive; public ThingDef dropPodIncoming;  // must both be set or both null
```

### Arrival / geography
```csharp
public FloatRange allowedArrivalTemperatureRange = (-1000, 1000);
    // IncidentWorker_PawnsArrive:32 (hard gate), FactionDialogMaker:270,334, RoyalTitlePermitWorker:115
public SimpleCurve minSettlementTemperatureChanceCurve;   // TileFinder:47-49, worldgen tile weighting
public List<PawnsArrivalModeDef> arrivalModeWhitelist / arrivalModeBlacklist;   // PawnsArrivalModeWorker:20-26
public List<PlanetLayerDef> layerWhitelist / layerBlacklist;                    // FactionGenerator.CanExistOnLayer
public List<PlanetLayerDef> arrivalLayerWhitelist / arrivalLayerBlacklist;
public List<PlanetLayerDef> neutralArrivalLayerWhitelist / neutralArrivalLayerBlacklist;
public List<PlanetLayerDef> raidArrivalLayerWhitelist / raidArrivalLayerBlacklist;
public float forageabilityFactor = 1f;               // ForagedFoodPerDayCalculator:91-98 (caravans)
```

### Worldgen / existence
```csharp
public int requiredCountAtGameStart;                 // DEAD on normal starts (see recon-factions.md §5.2)
public int startingCountAtWorldCreation = 1;
public int maxConfigurableAtWorldCreation = -1;      // >0 to appear in the world-creation UI at all
public int configurationListOrderPriority;           // UI sort order ONLY
public FactionDef replacesFaction;
public bool displayInFactionSelection = true;
public float settlementGenerationWeight;             // share of the world settlement budget; 0 ⇒ zero settlements
public bool hidden;
public bool humanlikeFaction = true;
public bool isPlayer;
public float listOrderPriority;                      // faction-list sort (FactionManager.GetInViewOrder)
public TechLevel techLevel;                          // ConfigError if Undefined
```

### Player-facing interaction
```csharp
public bool canRequestTraders = true;
public bool canRequestMilitaryAid = true;
public bool canRequestOrbitalTrader;
public bool canGenerateQuestSites = true;            // QuestNode_Root_DistressCall:148, QuestNode_Root_WorkSite:186
public bool rescueesCanJoin;                         // Pawn_GuestTracker:614
public bool hideGiftingInHostilityText;
public bool animalsFleeDanger = true;                // FleeUtility:80
public bool generateNewLeaderFromMapMembersOnly;
public List<PawnKindDef> fixedLeaderKinds;
public bool leaderForceGenerateNewPawn;
```

### Research / techprints / recipes
```csharp
public List<ResearchProjectTagDef> startingResearchTags;           // ResearchUtility.cs:8-10  — PLAYER faction only
public List<ResearchProjectTagDef> startingTechprintsResearchTags; // ResearchUtility.cs:32-36 — PLAYER faction only
public List<string> recipePrerequisiteTags;                        // RecipeDef.cs:270          — PLAYER faction only
[NoTranslate] public string categoryTag;   // joins to ResearchProjectDef.heldByFactionCategoryTags — see Q7
```
Note the first three are read exclusively via `Faction.OfPlayer.def.*`. They configure
the *player's* starting state, not NPC behaviour. **[VERIFIED]**

### Trade
```csharp
public List<TraderKindDef> caravanTraderKinds / orbitalTraderKinds
                         / visitorTraderKinds / baseTraderKinds;
public ThingSetMakerDef settlementLootMaker;   // orbital platforms ONLY — see recon-factions.md §3.1
```

### Ideology / Biotech / Royalty (behaviour-affecting subset)
```csharp
public XenotypeSet xenotypeSet;  public FloatRange melaninRange;
public List<CultureDef> allowedCultures;
public List<MemeDef> requiredMemes / allowedMemes / disallowedMemes / forcedMemes;
public List<PreceptDef> disallowedPrecepts;
public List<MemeWeight> structureMemeWeights;
public bool classicIdeo, fixedIdeo, hiddenIdeo, requiredPreceptsOnly;
public string ideoName, ideoDescription;
public List<StyleCategoryDef> styles;  public List<DeityPreset> deityPresets;
public List<string> royalTitleTags;
public List<RoyalImplantRule> royalImplantRules;
public List<PawnRelationDef> royalTitleInheritanceRelations;
public Type royalTitleInheritanceWorkerClass;
public ThingFilter apparelStuffFilter;   // FactionDef.CanUseStuffForApparel
```

### Cosmetic (listed for completeness, excluded from "behaviour")
`factionNameMaker`, `settlementNameMaker`, `playerInitialSettlementNameMaker`,
`fixedName`, `pawnSingular`, `pawnsPlural`, `leaderTitle`, `leaderTitleFemale`,
`royalFavorLabel`, `royalFavorIconPath`, `settlementTexturePath`, `factionIconPath`,
`colorSpectrum`, `backstoryFilters`, `backstoryCategories`, all `dialogFactionGreeting*`,
`dialogMilitaryAidSent`, `messageDefendersAttacking`, `renounceTitleMessage`.

### Obsolete
`maxCountAtGameStart`, `canMakeRandomly` — both `[Obsolete]`, no readers.

## 1.3 `ConfigErrors` — the hard constraints on any new FactionDef
`RimWorld/FactionDef.cs:536-578`. A new FactionDef **must** have:
- `techLevel` set (not `Undefined`)
- `raidLootValueFromPointsCurve` — **required unconditionally on every FactionDef**
- `maxPawnCostPerTotalPointsCurve` if `pawnGroupMakers != null`
- non-empty `backstoryFilters` if `humanlikeFaction`
- `dropPodActive` and `dropPodIncoming` both set or both null
**[VERIFIED]**

---

# Q2 — INTER-FACTION RELATIONS *(the crux)*

## 2.1 Does `RelationWith` support non-player pairs? **YES. [VERIFIED]**

`RimWorld/Faction.cs:487-507` — a plain list scan, no player special-casing:
```csharp
public FactionRelation RelationWith(Faction other, bool allowNull = false)
{
    if (other == this) { Log.Error(...); return new FactionRelation(); }
    for (int i = 0; i < relations.Count; i++)
        if (relations[i].other == other) return relations[i];
    if (!allowNull) { Log.Error("Faction " + name + " has null relation with " + other + ". Returning dummy relation."); return new FactionRelation(); }
    return null;
}
```
`FactionGenerator.NewGeneratedFaction` (`RimWorld/FactionGenerator.cs:170-172`) creates a
symmetric `FactionRelation` for **every** existing faction pair at worldgen:
```csharp
foreach (Faction item in Find.FactionManager.AllFactionsListForReading)
    faction.TryMakeInitialRelationsWith(item);
```
So an N-faction world carries a full N×N relation matrix, all of it persisted
(`Scribe_Collections.Look(ref relations, "relations", LookMode.Deep)`, `Faction.cs:277`).

## 2.2 Does the goodwill pipeline work for NPC↔NPC? **YES, end to end. [VERIFIED]**

Traced `Faction.TryAffectGoodwillWith(other, delta, ...)` (`RimWorld/Faction.cs:579-626`)
for the case where neither side is the player:

- **`CanChangeGoodwillFor`** (`:533-548`) — the gate. Full condition:
  ```csharp
  if (!HasGoodwill || !other.HasGoodwill || def.permanentEnemy || other.def.permanentEnemy
      || defeated || other.defeated || other == this
      || (def.permanentEnemyToEveryoneExceptPlayer && !other.IsPlayer)
      || (other.def.permanentEnemyToEveryoneExceptPlayer && !IsPlayer)
      || (def.permanentEnemyToEveryoneExcept != null && !def.permanentEnemyToEveryoneExcept.Contains(other.def))
      || (other.def.permanentEnemyToEveryoneExcept != null && !other.def.permanentEnemyToEveryoneExcept.Contains(def)))
      return false;
  ```
  **There is no "one side must be the player" requirement.** `HasGoodwill` is
  `!Hidden && !temporary` (`:202-212`). So any two visible, non-temporary, non-defeated,
  non-permanent-enemy factions can have their goodwill changed.
- **`GoodwillWith`** (`:514-526`) — the `GoodwillSituationManager` max-goodwill clamp is
  applied only `if (IsPlayer)` or `else if (other.IsPlayer)`. For an NPC pair,
  `GoodwillWith == BaseGoodwillWith`. **The situation-cap system does not apply to NPC pairs.**
- **`CalculateAdjustedGoodwillChange`** (`:559-577`) — the whole body is inside
  `if (IsPlayer || other.IsPlayer)`. For NPC pairs the delta is applied unmodified;
  there is **no pull toward natural goodwill.**
- **HistoryEvent recording** (`:597`) — `if (reason != null && (IsPlayer || other.IsPlayer))`.
  Skipped for NPC pairs. Harmless.
- **The write itself** (`:602-608`) is unconditional and symmetric:
  ```csharp
  FactionRelation factionRelation = RelationWith(other);
  factionRelation.baseGoodwill = num3;                       // Mathf.Clamp(base + delta, -100, 100)
  factionRelation.CheckKindThresholds(this, canSendHostilityLetter, reason?.LabelCap, lookTarget, out var sentLetter);
  FactionRelation factionRelation2 = other.RelationWith(this);
  factionRelation2.baseGoodwill = factionRelation.baseGoodwill;
  factionRelation2.kind         = factionRelation.kind;
  ```
- **`FactionRelation.CheckKindThresholds`** (`RimWorld/FactionRelation.cs:24-49`) flips
  `kind` at the vanilla thresholds regardless of who the parties are:
  `≤ -75 → Hostile`, `≥ 75 → Ally`, Hostile and `≥ 0 → Neutral`, Ally and `≤ 0 → Neutral`.
- **`Notify_RelationKindChanged`** (`:943-1084`) — the letter is suppressed
  (`if (Current.ProgramState != Playing || other != OfPlayer) canSendLetter = false;`),
  and the site-cleanup / trade-request-disable blocks are gated on `other == OfPlayer`.
  **But the last block is not gated:**
  ```csharp
  List<Map> maps = Find.Maps;
  for (int m = 0; m < maps.Count; m++) {
      maps[m].attackTargetsCache.Notify_FactionHostilityChanged(this, other);
      LordManager lordManager = maps[m].lordManager;
      for (int n = 0; n < lordManager.lords.Count; n++) {
          Lord lord = lordManager.lords[n];
          if (lord.faction == other)     lord.Notify_FactionRelationsChanged(this, previousKind);
          else if (lord.faction == this) lord.Notify_FactionRelationsChanged(other, previousKind);
      }
  }
  ```
  **This is the payoff.** Making two NPC factions hostile via `TryAffectGoodwillWith`
  correctly invalidates the attack-target caches and re-evaluates the `Lord` AI on every
  loaded map, so their pawns will actually fight each other. `FactionUtility.HostileTo`
  (`RimWorld/FactionUtility.cs:8-15`) is a plain `RelationWith(other).kind == Hostile`
  check with no player special-casing, and it is what all of `GenHostility` consults.

## 2.3 Does anything vanilla EVER change a non-player pair's goodwill on its own?

## **NO. VERIFIED — exhaustive.**

Every call site in `Assembly-CSharp` of every relation-mutating method, with the
player-side marked:

**`TryAffectGoodwillWith` — 48 call sites, `Faction.OfPlayer` on one side in all 48.**
```
CompAbilityEffect:47                         Faction.OfPlayer → homeFaction
CompAbilityEffect_Flashstorm:40              Faction.OfPlayer → item.Faction
CompAbilityEffect_Neuroquake:98              Faction.OfPlayer → key
CompAbilityEffect_PsychicSlaughter:24        pawn.Faction    → Faction.OfPlayer
CompCerebexCore_Destroyed:32                 item            → Faction.OfPlayer
CompDissolutionEffect_Goodwill:90            Faction.OfPlayer → result.Faction
CompTargetEffect_GoodwillImpact:15           Faction.OfPlayer → faction
Faction:375,384  (CheckReachNaturalGoodwill) this            → OfPlayer
Faction:768,793,806,814,838,845,850,1089,1104,1309            OfPlayer ↔ this
FactionDialogMaker:132,139,248,312,503       both directions, always OfPlayer
GameComponent_Anomaly:348                    item2           → Faction.OfPlayer
IncidentWorker_CaravanMeeting:76             Faction.OfPlayer → faction
JobDriver_AbsorbXenogerm:31                  Faction.OfPlayer → Target.HomeFaction
LordJob_BestowingCeremony:235,266            bestower.Faction → Faction.OfPlayer
QuestPart_FactionGoodwillChange:92           Faction.OfPlayer → faction
QuestPart_FactionGoodwillChange_ShuttleSentThings:92          Faction.OfPlayer → faction
QuestPart_RefugeeInteractions:273            Faction.OfPlayer → faction
RitualAttachableOutcomeEffectWorker_NearbyFactionGoodwill:33  settlement.Faction → Faction.OfPlayer
DefeatAllEnemiesQuestComp:79                 Faction.OfPlayer → requestingFaction
FactionGiftUtility:43,65                     Faction.OfPlayer → giveTo
Gravship:763                                 key             → Faction.OfPlayer
PeaceTalks:104,128,141,149                   Faction.OfPlayer → base.Faction
SettlementDefeatUtility:56                   Faction.OfPlayer → allFaction
SettlementProximityGoodwillUtility:57        Faction.OfPlayer → faction
SettlementUtility:66                         Faction.OfPlayer → mapParent.Faction
TimedMakeFactionHostile:65                   parent.Faction  → Faction.OfPlayer
TradeRequestComp:107                         Faction.OfPlayer → parent.Faction
TransportersArrivalAction_VisitSite:63       Faction.OfPlayer → site.Faction
QuestPart_ChangeGoodwillForAlivePawnsMissingFromShuttle:46    Faction.OfPlayer → faction
DebugActionsMisc:628,632                     Faction.OfPlayer → localFac   (debug)
Pawn:2612                                    Faction.OfPlayer → faction
RecipeWorker:71                              Faction.OfPlayer → factionToInform
PsychicRitualToil_TargetCleanup:48           target.HomeFaction → Faction.OfPlayer
```

**`SetRelationDirect` — 9 non-declaration call sites, all `→ Faction.OfPlayer`:**
`Faction:762,777,787`, `IncidentWorker_Raid:261,299,325,365`,
`QuestPart_FactionRelationChange:20`, `QuestPart_InnerFactionFight:162`,
`QuestPart_RefugeeInteractions:277`, `TimedMakeFactionHostile:61`.
(Also note `SetRelationDirect` **hard-refuses** when both sides `HasGoodwill`:
`Log.Error("Tried to use SetRelationDirect for factions which use goodwill…")`, `Faction.cs:645`.
It is only for hidden/temporary factions.)

**`ChangeGoodwill_Debug` — 4 call sites, all `IncidentWorker_Raid` → `Faction.OfPlayer`.**

**Direct `baseGoodwill =` writes — 7 sites, all inside `Faction.cs`** (in
`TryMakeInitialRelationsWith`, `TryAffectGoodwillWith`, `ChangeGoodwill_Debug`) plus the
field declaration in `FactionRelation.cs:10`.

**`Faction.SetRelation(FactionRelation)` — exactly one call site:**
`FactionGenerator.cs:213`, inside `NewGeneratedFactionWithRelations`, i.e. faction
*creation*, not ongoing simulation.

### Corollary that matters for design
Because `CalculateAdjustedGoodwillChange` and `CheckReachNaturalGoodwill` both short-circuit
on non-player pairs, **NPC↔NPC goodwill never drifts and is never touched by anything.**
Whatever we write there stays exactly as written, forever, and is serialised for free.
This is durable, zero-maintenance state that vanilla already saves, loads, and renders in
the faction UI. **[VERIFIED]**

### The one near-miss
`QuestPart_InnerFactionFight` (`RimWorld/QuestPart_InnerFactionFight.cs`) is the closest
vanilla gets to a faction war. On `Enable()` it *generates a brand-new temporary faction*
that is hostile to the first faction and neutral to everyone else:
```csharp
List<FactionRelation> list = new List<FactionRelation>();
foreach (Faction item in Find.FactionManager.AllFactionsListForReading) {
    if (item == firstFaction) list.Add(new FactionRelation(item, FactionRelationKind.Hostile));
    else if (!item.def.PermanentlyHostileTo(firstFaction.def))
        list.Add(new FactionRelation(item, FactionRelationKind.Neutral));
}
secondFaction = FactionGenerator.NewGeneratedFactionWithRelations(secondFactionDef, list, hidden: true);
secondFaction.temporary = true;
```
It creates a *hidden, temporary splinter*; it does not alter any persistent NPC pair. But
it proves the pattern works and gives us the vanilla-blessed API:
`FactionGenerator.NewGeneratedFactionWithRelations(FactionDef, List<FactionRelation>, bool hidden)`
is `public static`. **[VERIFIED]**

---

# Q3 — THE WORLD TICK

`RimWorld.Planet/World.cs:213-222` — the entire world tick. **[VERIFIED]**
```csharp
public void WorldTick()
{
    worldPawns.WorldPawnsTick();
    factionManager.FactionManagerTick();
    worldObjects.WorldObjectsHolderTick();
    debugDrawer.WorldDebugDrawerTick();
    pathGrid.WorldPathGridTick();
    WorldComponentUtility.WorldComponentTick(this);
    ideoManager.IdeoManagerTick();
}
```

`RimWorld/FactionManager.cs:147-161`:
```csharp
public void FactionManagerTick()
{
    goodwillSituationManager.GoodwillManagerTick();
    SettlementProximityGoodwillUtility.CheckSettlementProximityGoodwillChange();
    for (int i = 0; i < allFactions.Count; i++) allFactions[i].FactionTick();
    for (int num = toRemove.Count - 1; num >= 0; num--) { ...Remove(faction); }
}
```

That is **all four** faction-related things vanilla does per tick:

1. **`GoodwillSituationManager.GoodwillManagerTick()`** — `if (TicksGame % 1000 == 0) RecalculateAll(...)`.
   Recomputes, for **every non-player faction**, its max-goodwill cap and natural-goodwill
   offset *with respect to the player*. `GetSituations` explicitly errors on
   `other.IsPlayer` and every worker hardcodes `Faction.OfPlayer` (see Q5).
2. **`SettlementProximityGoodwillUtility.CheckSettlementProximityGoodwillChange()`** —
   `if (TicksGame == 0 || TicksGame % 900000 != 0) return;` → every **900,000 ticks = 15 days**.
   Iterates *player* settlements only, penalises factions whose bases are within
   `Goodwill_PerQuadrumFromSettlementProximity` (curve: 2 tiles → -30, 3 → -20, 4 → -10,
   5 → 0), and applies it to the **player** relation.
3. **`Faction.FactionTick()`** (`Faction.cs:304-354`) — per faction, per tick:
   `CheckReachNaturalGoodwill()`; `kidnapped.KidnappedPawnsTrackerTick()`; expiry sweep of
   `predatorThreats`; a player-only "name your faction/settlement" dialog check at
   `TicksGame % 1000 == 200`; a `Log.ErrorOnce` if a faction that should have a leader has none.
   **No AI, no decisions, no world-map action.**
4. **`toRemove` drain** — only `temporary` factions can be removed
   (`Remove()` `Log.Error`s otherwise, `FactionManager.cs:109-112`).

`WorldObjectsHolderTick` (`RimWorld.Planet/WorldObjectsHolder.cs:207-215`) just calls
`DoTick()` on every world object. Settlements tick their `Settlement_TraderTracker`
(stock regenerates every 30 days) and comps like `TimedDetectionRaids` and
`TradeRequestComp`. None of that is faction-vs-faction.

**Vanilla `WorldComponent` subclasses** (`grep ": WorldComponent"`): `TilePollutionComp`,
`TileTemperaturesComp`, `WorldComponent_LocationGenerator`, `WorldGenData`,
`OrbitalScannerWorldComponent`, `WorldComponent_GravshipController`. **None does anything
faction-related.** **[VERIFIED]**

**Verdict: there is no autonomous faction behaviour in vanilla RimWorld 1.6. None.**
Factions are inert data that the storyteller reads when it wants to point an incident
at someone.

---

# Q4 — SETTLEMENTS

## 4.1 Creation
Every `Settlement` in a vanilla game is created in one of these places
(`grep "SettlementWorldObjectDef"`): **[VERIFIED]**

| Site | When |
|---|---|
| `FactionGenerator.GenerateFactionsIntoWorldLayer:41` | Worldgen — the settlement-count budget loop |
| `FactionGenerator.NewGeneratedFaction:177` | Whenever a faction is created, **one settlement is auto-placed** if `!hidden && !isPlayer` |
| `ScenPart_PlayerFaction:60` | Player's starting colony |
| `SettleUtility:36` | Player settles a tile |
| `MoveColonyUtility:162`, `Tile.cs:307`, `GravshipUtility:495` | Player colony relocation / gravship landing |
| `AbandonedArchotechStructures:22`, `QuestNode_Root_ArchonexusVictory_*` | Archonexus victory chain (player) |
| `DebugActionsMapManagement`, `DebugToolsSpawning` | Debug only |

**No vanilla incident, quest, or tick ever creates an NPC settlement after worldgen.**

The runtime API is trivially available and `public`:
```csharp
Settlement s = (Settlement)WorldObjectMaker.MakeWorldObject(tile.LayerDef.SettlementWorldObjectDef);
s.SetFaction(faction);                                  // WorldObject.SetFaction — virtual, public
s.Tile = TileFinder.RandomSettlementTileFor(layer, faction);   // public static, honours minSettlementTemperatureChanceCurve
s.Name = SettlementNameGenerator.GenerateSettlementName(s);
Find.WorldObjects.Add(s);                               // public
```
(Exactly the five lines `FactionGenerator.cs:41-48` runs.) **[VERIFIED]**

## 4.2 Destruction
`WorldObject.Destroy()` → `Find.WorldObjects.Remove(o)` → `PostRemove()`.
`WorldObjectsHolder.Add` / `.Remove` are both `public void` and merely `Log.Error` on
double-add/double-remove.

`Settlement.PostRemove()` calls `trader.TryDestroyStock()`, which destroys every non-pawn
item held on the world object (already documented in `recon-factions.md` §3.2).

## 4.3 `SettlementDefeatUtility` — the only vanilla settlement destroyer
`RimWorld.Planet/SettlementDefeatUtility.CheckDefeated(Settlement)`. Player-triggered only
(returns immediately if the settlement is the player's; requires a generated `Map` and
`IsDefeated(map, faction)`). What it does: **[VERIFIED]**
```csharp
DestroyedSettlement destroyedSettlement = (DestroyedSettlement)WorldObjectMaker.MakeWorldObject(
    factionBase.Tile.LayerDef.DestroyedSettlementWorldObjectDef);
destroyedSettlement.Tile = factionBase.Tile;
destroyedSettlement.SetFaction(factionBase.Faction);
Find.WorldObjects.Add(destroyedSettlement);
...
if (!HasAnyOtherBase(factionBase)) {
    factionBase.Faction.defeated = true;                       // ← THE "FACTION FELL" FLAG
    stringBuilder.Append("LetterFactionBaseDefeated_FactionDestroyed".Translate(factionBase.Faction.Name));
}
foreach (Faction allFaction in Find.FactionManager.AllFactions)
    if (!allFaction.Hidden && !allFaction.IsPlayer && allFaction != factionBase.Faction
        && allFaction.HostileTo(factionBase.Faction))
        Faction.OfPlayer.TryAffectGoodwillWith(allFaction, 20, ..., HistoryEventDefOf.DestroyedEnemyBase);
...
map.info.parent = destroyedSettlement;
factionBase.Destroy();
```
Note the loop: **destroying a faction's base already earns you +20 with everyone who was
hostile to that faction.** Vanilla already has an "enemy of my enemy" reward — it just
needs NPC↔NPC hostility to exist for the loop to find anyone.

## 4.4 `Faction.defeated` — a high-value one-bit lever
`public bool defeated;` (`Faction.cs:32`), `Scribe_Values.Look(ref defeated, "defeated", false)`.
**Written in exactly one place** (`SettlementDefeatUtility:46`) and **never reset**.
Read in 12 places, all of which behave sensibly: **[VERIFIED]**
- `Faction.CanChangeGoodwillFor:535` — a defeated faction's goodwill is frozen
- `FactionManager.GetFactions:185`, `TryGetRandomNonColonyHumanlikeFaction:177` — excluded from all faction pools by default (`allowDefeated: false`)
- `PawnGroupMakerUtility.UsableFactions:357` — **excluded from raids**
- `IncidentWorker_PawnsArrive:24` — **no visitors/traders/caravans arrive**
- `GenStep_Turrets:42`, `SitePartDef:171`, `QuestGen_Pawns:249`, `QuestNode_GetPawn:211`,
  `QuestNode_Root_Hack_Spacedrone:154`, `QuestPart_RequirementsToAcceptFactionRelation:24` — excluded
- `FactionManager.GetInViewOrder:299` — `orderby x.defeated` sorts them to the bottom of the faction tab
- `FactionUIUtility:182` — displayed as defeated in the UI

**Setting `faction.defeated = true` is a one-line, fully-supported way to make a faction
"fall".** Nothing needs patching; every consumer already handles it.

---

# Q5 — GOODWILL MECHANICS

## 5.1 The two-layer model **[VERIFIED]**
- **`FactionRelation.baseGoodwill`** (`int`, clamped -100..100) — persisted state.
- **`Faction.GoodwillWith(other)`** — `baseGoodwill`, then **for player pairs only**
  clamped down by `GoodwillSituationManager.GetMaxGoodwill(other)`.
- **`Faction.NaturalGoodwill`** ⇒ `Find.GoodwillSituationManager.GetNaturalGoodwill(this)`
  — the sum of every `GoodwillSituationDef.naturalGoodwillOffset` that applies. This is a
  *target*, not a value; it is the centre of the drift band.
- **`FactionRelation.kind`** — derived from `GoodwillWith` by `CheckKindThresholds`.

## 5.2 Thresholds — `RimWorld/DiplomacyTuning.cs` **[VERIFIED]**
```csharp
MaxGoodwill = 100;   MinGoodwill = -100;
BecomeHostileThreshold = -75;   BecomeNeutralThreshold = 0;   BecomeAllyThreshold = 75;
InitialHostileThreshold = -10;  InitialAllyThreshold = 75;
NaturalEnemyNaturalGoodwill = -130;   NaturalEnemyInitialGoodwill = -80;
NaturalGoodwillRange = 50;   NaturalGoodwillDailyChange = 0.2f;
GoodwillChangeTowardsNaturalGoodwillFactor = 1.25f;   Goodwill_NaturalChangeStep = 10;
```
Note the **hysteresis**: you become Hostile at ≤ -75 but only return to Neutral at ≥ 0;
you become Ally at ≥ 75 but only drop to Neutral at ≤ 0. A faction pushed to hostile stays
hostile until goodwill climbs 75 points.

## 5.3 The natural drift — `Faction.CheckReachNaturalGoodwill` **[VERIFIED]**
`RimWorld/Faction.cs:356-388`. Runs every tick per faction. **Player pairs only.**
```csharp
if (IsPlayer || !HasGoodwill || def.permanentEnemy) return;
int num = BaseGoodwillWith(OfPlayer);
IntRange intRange = new IntRange(NaturalGoodwill - 50, NaturalGoodwill + 50);
if (intRange.Includes(num)) { naturalGoodwillTimer = 0; return; }
naturalGoodwillTimer++;
if (num < intRange.min) {
    int num2 = 3000000;
    if (naturalGoodwillTimer >= num2) {
        TryAffectGoodwillWith(OfPlayer, Mathf.Min(10, intRange.min - num), ..., HistoryEventDefOf.ReachNaturalGoodwill, ...);
        naturalGoodwillTimer = 0;
    }
}   // symmetric for num > intRange.max
```
**3,000,000 ticks = 50 in-game days** (60,000 ticks/day) for a ±10 step ⇒ the documented
0.2 goodwill/day. And it only fires when goodwill is **more than 50 points outside**
natural goodwill. In practice the drift is nearly irrelevant on any human timescale.
Confirms: **there is no meaningful "drift back to neutral" in vanilla.**

The `1.25×` `GoodwillChangeTowardsNaturalGoodwillFactor` lives in
`CalculateAdjustedGoodwillChange` (`Faction.cs:559-577`): a change that moves goodwill
*toward* natural goodwill is amplified by 25% of the remaining gap (capped at the change
magnitude). **Player pairs only.**

## 5.4 `GoodwillSituationDef` / `GoodwillSituationWorker` — the complete list **[VERIFIED]**

`RimWorld/GoodwillSituationDef.cs`:
```csharp
public Type workerClass = typeof(GoodwillSituationWorker);
public int baseMaxGoodwill = 100;     // NOTE: no worker reads this — dead in 1.6
public MemeDef meme;  public MemeDef otherMeme;
public int naturalGoodwillOffset;
public bool versusAll;
```
`GoodwillSituationWorker` exposes exactly two overridables:
`GetMaxGoodwill(Faction other)` and `GetNaturalGoodwillOffset(Faction other)`.

**Only five worker classes exist in the whole assembly:**

| Worker | Effect | Player-only? |
|---|---|---|
| `GoodwillSituationWorker_PermanentEnemy` | `maxGoodwill = -100` if `ArePermanentEnemies(Faction.OfPlayer, other)` | **Yes** — hardcoded `Faction.OfPlayer` |
| `GoodwillSituationWorker_NaturalEnemy` | `naturalGoodwillOffset = -130` if `other.def.naturalEnemy` | n/a (unary) |
| `GoodwillSituationWorker_AttackingSettlement` | `maxGoodwill = -80` while `SettlementUtility.IsPlayerAttackingAnySettlementOf(other)` | **Yes** |
| `GoodwillSituationWorker_SameIdeo` | `+naturalGoodwillOffset` if `Faction.OfPlayer.ideos.PrimaryIdeo == other.ideos.PrimaryIdeo` | **Yes** |
| `GoodwillSituationWorker_MemeCompatibility` | `naturalGoodwillOffset` if the meme pair matches; `versusAll` matches any partner | **Yes** — both `Applies` overloads test against `Faction.OfPlayer` |

Vanilla defs: `Data/Core/Defs/Goodwill/GoodwillSituations_Misc.xml` (3 defs) and
`Data/Ideology/Defs/Goodwill/GoodwillSituations_MemeCompatibility.xml` (~30 defs, offsets
+10 / -10 / -20 / -30 / -50).

> **CRITICAL LIMITATION.** `GoodwillSituationManager.GetSituations(other)` `Log.Error`s if
> `other.IsPlayer`, `RecalculateAll` skips `Faction.OfPlayer`, and `GoodwillWith` only
> consults the manager when one side is the player. **The entire `GoodwillSituation`
> system is a player-relations system.** New `GoodwillSituationDef`s can be authored in
> pure XML (via `GoodwillSituationWorker_MemeCompatibility`) but they can only ever
> influence player↔NPC goodwill, never NPC↔NPC. **[VERIFIED]**

## 5.5 What changes player goodwill — the full vanilla catalogue
Magnitudes from `DiplomacyTuning`, call sites from Q2.3. **[VERIFIED]**

| Event | Δ | Source |
|---|---|---|
| Damage a member | `-1.3 × min(100, dmg)` | `Faction.Notify_MemberTookDamage:768` |
| Damage a building | `-1.0 × min(100, dmg)` | `Faction.Notify_BuildingTookDamage:793` |
| Member crushed (collapse) | -25 humanlike / -15 animal | `Notify_MemberDied:838` |
| Member died neutrally | -5 humanlike / -3 animal | `Notify_MemberDied:845` |
| Member captured | → hostile (`GoodwillToMakeHostile`) | `Notify_MemberCaptured:806` |
| Member stripped | -40 | `Notify_MemberStripped:814` |
| Member killed (`factionHostileOnDeath/Kill`) | → hostile | `Notify_MemberDied:850` |
| Member sold | → hostile | `Pawn.cs:2612` |
| Attacked settlement / caravan / site | → hostile | `SettlementUtility:66`, `IncidentWorker_CaravanMeeting:76`, `TransportersArrivalAction_VisitSite:63` |
| Harmful surgery | `recipe.goodwillImpact` | `RecipeWorker:71` |
| Xenogerm absorbed | -50 | `JobDriver_AbsorbXenogerm:31` |
| Psychic ritual target | -25 | `PsychicRitualToil_TargetCleanup:48` |
| Psychic slaughter | -100 | `CompAbilityEffect_PsychicSlaughter:24` |
| Royal thing-use violation | -4 | `Faction.Notify_RoyalThingUseViolation:1309` |
| Kidnapped on gravship | `-10 × count` | `Gravship:763` |
| Request trader / orbital trader / military aid | -15 / -30 / -25 | `FactionDialogMaker:312,248,503` |
| Traded | `+marketValue/600` | `Notify_PlayerTraded:1089` |
| Gave gift | `silver/40` × `GiftGoodwillFactorRelationsCurve` | `FactionGiftUtility:43,65` |
| Guest exited healthy | +12 (+40 if faction leader), +1/tend up to 10 | `Notify_MemberExitedMap:1104` |
| Destroyed a mutual enemy's last base | +20 | `SettlementDefeatUtility:56` |
| Settlement proximity | -30…0 per quadrum by distance | `SettlementProximityGoodwillUtility:57` |
| Peace talks | -50…-40 / -20…-10 / +60…+70 / +100…+110 | `PeaceTalks:104,128,141,149` |
| Quest reward / penalty | arbitrary | `QuestPart_FactionGoodwillChange:92` |
| Destroyed void monolith / cerebex core | +50 | `GameComponent_Anomaly:348`, `CompCerebexCore_Destroyed:32` |
| Natural drift | ±10 per 50 days | `CheckReachNaturalGoodwill:375,384` |

`HistoryEventDef`s for all of these are pure XML in `Data/Core/Defs/Goodwill/GoodwillEvents_*.xml`
(diplomatic / misc / pawns / quests / world). They are labels for the message text and for
Ideology precept hooks — **they do not themselves cause any goodwill change.**

---

# Q6 — QUEST / INCIDENT HOOKS

## 6.1 Incidents cannot target a specific faction from XML **[VERIFIED]**
`RimWorld/IncidentDef.cs` has **no faction field** of any kind. Faction selection happens
at runtime through `IncidentParms.faction` (`RimWorld/IncidentParms.cs:14`), which is set
by the `IncidentWorker` — normally via
`PawnGroupMakerUtility.TryGetRandomFactionForCombatPawnGroup` (weighted by
`raidCommonalityFromPointsCurve`) or `FactionManager.RandomEnemyFaction()`.
**To point an incident at a named faction you need either C# or a quest.**
Quests, by contrast, *can* name a faction in XML — see §6.4.

## 6.2 Deadlines — **YES, and fully telegraphed. [VERIFIED]**

Two independent deadline systems:

### (a) Acceptance expiry (before the player accepts)
`RimWorld/QuestScriptDef.cs`: `public FloatRange expireDaysRange = new FloatRange(-1f, -1f);`
Consumed in `RimWorld.QuestGen/QuestGen.cs:194-196`:
```csharp
if (root.expireDaysRange.max > 0f)
    quest.acceptanceExpireTick = GenTicks.TicksGame + (int)(root.expireDaysRange.RandomInRange * 60000f);
```
`Quest.TicksUntilExpiry` (`Quest.cs:97`); `Quest.State` (`:158`) becomes
`QuestState.EndedOfferExpired`. **No signal is emitted** — expiry is a state transition.
UI telegraphing is automatic and free: `Alert_QuestExpiresSoon` (fires under 60,000 ticks),
`MainTabWindow_Quests.cs:409-413,680-697` (`"QuestExpiresIn"` / `"QuestExpiresOn"`),
and `QuestUtility.cs:228-230` appends `"LetterQuestRequiresAcceptance"` to the offer letter.
Runtime override: `QuestNode_SetTicksUntilAcceptanceExpiry` (`SlateRef<int> ticks`).
`QuestScriptDef.ConfigErrors()` requires `expireDaysRange` when
`rootSelectionWeight > 0 && !autoAccept`, and forbids it when `autoAccept`.

### (b) Post-acceptance deadline — `QuestNode_Delay` / `QuestPart_Delay`
`RimWorld.QuestGen/QuestNode_Delay.cs` — full XML field list:

| Field | Type |
|---|---|
| `inSignalEnable` / `inSignalDisable` / `outSignalComplete` | `SlateRef<string>` |
| `delayTicks` | `SlateRef<int>` |
| `delayTicksRange` | `SlateRef<IntRange?>` → builds `QuestPart_DelayRandom` instead |
| `isQuestTimeout` | `SlateRef<bool>` → sets `isBad = true`, `expiryInfoPart = "QuestExpiresIn"`, `expiryInfoPartTip = "QuestExpiresOn"` |
| `expiryInfoPart` / `expiryInfoPartTip` | `SlateRef<string>` — the countdown shown in the Quests tab |
| `inspectString` / `inspectStringTargets` | `SlateRef<string>` / `SlateRef<IEnumerable<ISelectable>>` |
| `reactivatable`, `waitUntilPlayerHasHomeMap`, `useAcceptanceExpiry` | `SlateRef<bool>` |
| `node` | `QuestNode` — **the failure branch, run on completion** |

`RimWorld/QuestPart_Delay.cs` (a `QuestPartActivable`) additionally carries
`alertLabel`, `alertExplanation`, `alertCulprits` (`List<GlobalTargetInfo>`) and
`ticksLeftAlertCritical` — i.e. a real right-side Alert that **turns red** as the
deadline nears. `TicksLeft => enableTick + delayTicks - TicksGame`.
There is **no `outSignalExpired`**; the "expired" path *is* the completion path, and
XML nests the failure logic inside `<node>`.

**`QuestNode_QuestUnfinished` does not exist in 1.6.** (The nearest thing is
`QuestNode_QuestUnique`, which deduplicates by tag.)

Related: `QuestNode_WorldObjectTimeout` / `QuestPart_WorldObjectTimeout`
(deadline attached to a world object, `destroyOnCleanup = true`),
`QuestNode_ShuttleDelay`, `QuestNode_ShuttleLeaveDelay`, `QuestNode_GuardianShipDelay`,
`QuestPart_MTB`, `QuestPart_PassOutInterval`.

### (c) Ending on failure
`QuestNode_End` (`RimWorld.QuestGen/QuestNode_End.cs`): `inSignal`,
`outcome` (`SlateRef<QuestEndOutcome>`), `signalListenMode`, `sendStandardLetter`, **plus a
built-in goodwill hook**: `goodwillChangeAmount` (int), `goodwillChangeFactionOf`
(`SlateRef<Thing>`), `goodwillChangeReason` (`SlateRef<HistoryEventDef>`). When
`amount != 0` it emits a `QuestPart_FactionGoodwillChange` and sets the slate var
`goodwillPenalty` for use in the letter text.

Canonical vanilla XML shape (`Core/Defs/QuestScriptDefs/Script_ItemStash.xml:147-164`):
```xml
<li Class="QuestNode_WorldObjectTimeout">
  <worldObject>$site</worldObject>
  <isQuestTimeout>true</isQuestTimeout>
  <delayTicks>$(randInt(12,28)*60000)</delayTicks>
  <inSignalDisable>site.MapGenerated</inSignalDisable>
  <node Class="QuestNode_Sequence"><nodes>
    <li Class="QuestNode_Letter"> ... </li>
    <li Class="QuestNode_End"><outcome>Fail</outcome></li>
  </nodes></node>
</li>
```
`isQuestTimeout` XML users: `Core/Script_{BanditCamp,DownedRefugee,ItemStash,LongRangeMineralScannerLump,PrisonerWillingToJoin,TradeRequest}.xml`,
`Odyssey/Script_{AlphaThrumboSighting,BanditCamp,ItemStash,OrbitalFugitive,Site,SpaceSites}.xml`,
`Royalty/BuildMonument/Script_BuildMonument_Worker.xml:317`,
`Royalty/Decree/Scripts_Decree.xml:{67,139,215,315}`,
`Royalty/Intro/Script_Intro_Deserter.xml:139`, `Royalty/Script_ChangeRoyalHeir.xml:89`.

**ANSWER: yes — a vanilla quest can impose a deadline with a telegraphed consequence
(quest-tab countdown + red alert + letter) and change faction goodwill on failure, in
pure XML: `QuestNode_Delay { isQuestTimeout } → QuestNode_ChangeFactionGoodwill →
QuestNode_End { Fail }`.**

## 6.3 Goodwill / relation QuestParts — the full list

| Class | XML-reachable? | Fields | Other side |
|---|---|---|---|
| `QuestPart_FactionGoodwillChange` | **Yes** — `QuestNode_ChangeFactionGoodwill` | `historyEvent`, `inSignal`, `change`, `faction`, `canSendMessage`, `canSendHostilityLetter`, `getLookTargetFromSignal`, `lookTarget`, `ensureMakesHostile` | **`Faction.OfPlayer`, hardcoded** |
| `QuestPart_FactionRelationChange` | **NO — no `QuestNode` wrapper exists.** C# only, via `QuestGen_Factions.FactionRelationToPlayerChange` | `inSignal`, `faction`, `relationKind`, `canSendHostilityLetter` | **`Faction.OfPlayer`, hardcoded** |
| `QuestPart_FactionGoodwillChange_ShuttleSentThings` | via C# | `inSignalsShuttleSent`, `inSignalShuttleDestroyed`, `changeNotOnShuttle`, `faction`, `things`, `historyEvent`, … | **`Faction.OfPlayer`** |
| `QuestPart_ChangeGoodwillForAlivePawnsMissingFromShuttle` | **Yes** — `QuestNode_ChangeGoodwillForAlivePawnsMissingFromShuttle` | `inSignal`, `pawns`, `faction`, `goodwillChange`, `historyEvent` | **`Faction.OfPlayer`** |
| `QuestPart_FactionGoodwillForMoodChange` | **Yes** — `QuestNode_FactionGoodwillForMoodChange` | `inSignal`, `outSignalSuccess`, `outSignalFailed`, `pawns` | n/a — emits a `GOODWILL` signal arg, does not change goodwill itself |
| `QuestPart_FactionGoodwillLocked` | via C# | **`faction1`, `faction2`** — genuinely arbitrary pair | *freezes* a relation (read by `Faction.CanChangeGoodwillFor` via `QuestUtility.IsGoodwillLockedByQuest`); never changes one |
| `QuestPart_FactionRelationKind` | via C# | **`faction1`, `faction2`, `relationKind`** — arbitrary pair | pure **watcher**; `Complete()`s when the condition holds |

`QuestNode_ChangeFactionGoodwill` XML fields: `inSignal`, `faction` (`SlateRef<Faction>`),
`factionOf` (`SlateRef<Thing>` fallback), `change` (int), `canSendLetter` (bool?),
`canSendMessage` (bool?), `ensureHostile` (bool), `reason` (`HistoryEventDef`).

> ### **The critical Q6 finding, and it matches Q2 exactly:**
> **No vanilla QuestPart can move goodwill between two arbitrary non-player factions.**
> `QuestPart_FactionGoodwillChange` and `QuestPart_FactionRelationChange` both contain an
> explicit `faction != Faction.OfPlayer` guard and take only *one* faction field; the other
> side is literally `Faction.OfPlayer` in the source. There is no "other faction" parameter
> to supply. **[VERIFIED]**
>
> The two QuestParts that *do* take an arbitrary `(faction1, faction2)` pair —
> `QuestPart_FactionGoodwillLocked` and `QuestPart_FactionRelationKind` — are a *lock* and a
> *watcher*. Vanilla knew the pair concept was needed and only ever used it read-only.
>
> Writing our own `QuestPart_ChangeInterFactionGoodwill` + matching `QuestNode` is ~40 lines
> and calls the existing symmetric `Faction.TryAffectGoodwillWith`. Remember the change will
> be **silent** for NPC pairs (no `HistoryEvent`, no message, no letter — `Faction.cs:597,619`),
> so it must be paired with our own `Find.LetterStack.ReceiveLetter`.

`QuestGen_Factions.cs` is the C#-only helper surface: `AssaultColony`, `ExtraFaction`,
`ReserveFaction`, `FactionRelationToPlayerChange`, `FactionGoodwillChange`, `SetFactionHidden`.

Adjacent parts worth knowing: `QuestPart_InvolvedFactions`, `QuestPart_ReserveFaction`
(blocks other quests from using a faction), `QuestPart_ExtraFaction`, `QuestPart_SetFaction`,
`QuestPart_SetFactionHidden`, `QuestPart_Filter_FactionHostileToOtherFaction`,
`QuestPart_InnerFactionFight`, `QuestPart_LendColonistsToFaction`,
`QuestPart_Notify_PlayerRaidedSomeone`.

## 6.4 Faction selection — `QuestNode_GetFaction`

`RimWorld.QuestGen/QuestNode_GetFaction.cs` — complete field list. **[VERIFIED]**

| Field | Type | Effect (from `IsGoodFaction`) |
|---|---|---|
| `storeAs` | `SlateRef<string>` | slate var name |
| `allowEnemy` / `allowNeutral` / `allowAlly` | `SlateRef<bool>` | filter on `PlayerRelationKind` |
| `allowAskerFaction` | `SlateRef<bool>` | **DEAD — declared, never referenced** |
| `allowPermanentEnemy` | `SlateRef<bool?>` | if explicitly false, reject `def.permanentEnemy` |
| `mustBePermanentEnemy` | `SlateRef<bool>` | require `def.permanentEnemy` |
| `playerCantBeAttackingCurrently` | `SlateRef<bool>` | reject if `SettlementUtility.IsPlayerAttackingAnySettlementOf` |
| `peaceTalksCantExist` | `SlateRef<bool>` | reject if a `PeaceTalks` object / quest exists for it |
| `leaderMustBeSafe` | `SlateRef<bool>` | reject if `leader == null \|\| leader.Spawned \|\| leader.IsPrisoner` |
| `mustHaveGoodwillRewardsEnabled` | `SlateRef<bool>` | require `faction.allowGoodwillRewards` |
| `ofPawn` | `SlateRef<Pawn>` | require `faction == ofPawn.Faction` |
| `mustBeHostileToFactionOf` | `SlateRef<Thing>` | require `faction.HostileTo(thing.Faction)` |
| `exclude` | `SlateRef<IEnumerable<Faction>>` | blacklist |
| `allowedHiddenFactions` | `SlateRef<IEnumerable<Faction>>` | hidden factions rejected unless listed |

Selection is `Find.FactionManager.GetFactions(allowHidden: true).Where(IsGoodFaction).TryRandomElement(...)`
— **uniform random, no weighting.**

**There is NO `techLevel`, `factionDefs`, `categoryTags`, or `minSettlements` filter.**
Workaround: `QuestNode_GetPawn` *does* expose `minTechLevel` (`SlateRef<TechLevel>`),
`excludeFactionDefs` (`SlateRef<List<FactionDef>>`), `mustBeFactionLeader`,
`mustBeNonHostileToPlayer`, `allowPermanentEnemyFaction`, `hostileWeight`/`nonHostileWeight`,
`factionMustBePermanent`, `mustHaveSettlementOnLayer` — so
`QuestNode_GetPawn → QuestNode_GetFactionOf` is the vanilla way to get a tech-filtered faction.

> **XML shortcut worth remembering:** `SlateRef<Faction>` accepts a bare **FactionDef defName
> string**. `Verse/ConvertHelper.cs` has an explicit `if (obj is string && to == typeof(Faction)) return true;`
> branch. That is why `Royalty/.../Script_Intro_Deserter.xml:49` can write
> `<faction>Empire</faction>` literally. **This is how we name an Archinity faction in a
> quest from pure XML.** **[VERIFIED]**

Other selection nodes: `QuestNode_GetFactionOf`, `QuestNode_GetPlayerFaction`,
`QuestNode_GetRandomFactionForSite` (has `mustBeHostileToFactionOf`),
and predicates `QuestNode_FactionExists`, `QuestNode_IsFactionHostileToPlayer`,
`QuestNode_IsFactionLeader`, `QuestNode_IsOfFaction`, `QuestNode_IsPermanentEnemy`,
`QuestNode_Filter_FactionNonPlayer`, `QuestNode_GetRelationsInfo`.

## 6.5 Demands with consequences — what vanilla ships

**Not quests (so don't look for XML):** `IncidentWorker_RansomDemand` +
`ChoiceLetter_RansomDemand` (pay `fee` silver to recover a kidnapped pawn; refusal costs
nothing, **no goodwill change**), `IncidentWorker_CaravanDemand`,
`IncidentWorker_CaravanMeeting`, and the **tribute collector**, which is
`IncidentWorker_CaravanArrivalTributeCollector` — an
`IncidentWorker_TraderCaravanArrival` subclass forcing `parms.faction = Faction.OfEmpire`
and `TraderKindDef.category == "TributeCollector"`. **It is a trader, not a quest, and has
no refusal penalty.** **[VERIFIED]**

**Actual demand-shaped QuestScriptDefs:**

| Quest | XML | Demand | Consequence |
|---|---|---|---|
| `TradeRequest` | `Core/Defs/QuestScriptDefs/Script_TradeRequest.xml` | deliver N of an item by caravan | `expireDaysRange 4~8`; `isQuestTimeout` + `QuestNode_End`. **No goodwill penalty.** |
| `Beggars` | `Ideology/Defs/QuestScriptDefs/Script_Beggars.xml` | give silver/medicine/beer | `autoAccept`, `defaultCharity`. Refusal = Charity-precept mood only. Beggars are factionless — explicitly "without diplomatic consequences". |
| `Decree_*` | `Royalty/.../Decree/Scripts_Decree.xml` | Empire orders production/harvest/hunt by a deadline | `isQuestTimeout` at 67/139/215/315; royal-title consequences |
| Hospitality lodgers | `Royalty/.../Hospitality/Script_Hospitality_Worker.xml` | house/feed/return nobles | ~15 × `<goodwillChangeAmount>-5</goodwillChangeAmount>` (lines 1029–1366); `QuestNode_ChangeFactionGoodwill` at 1315; mood bonus via `QuestNode_FactionGoodwillForMoodChange` |
| Empire permits | `Royalty/Defs/QuestScriptDefs/Scripts_Permits.xml` | return borrowed laborers | `QuestNode_ChangeFactionGoodwill` at 88/141/182/197 with reasons `QuestPawnLost` / `ShuttleDestroyed` / `LaborersMissedShuttle` |
| `BuildMonument_*` | `Royalty/.../BuildMonument/Script_BuildMonument_Worker.xml` | build + protect a monument | goodwill at 228; `-5` at 268/327; `isQuestTimeout` at 317 |
| `Intro_Deserter` | `Royalty/.../Intro/Script_Intro_Deserter.xml:48-55` | shelter an Empire deserter | **the strongest vanilla consequence**: `<change>-100</change> <ensureHostile>true</ensureHostile> <reason>AcceptedDeserter</reason>` |
| `PollutionDump` | `Biotech/.../Script_PollutionDump.xml` | accept pollution | refusal ⇒ `PollutionRetaliation` / `PollutionRaid` quests |
| Bestowing ceremony | `Royalty/.../Script_Bestower.xml` | provide throne room | mistreatment ⇒ `bestower.Faction.TryAffectGoodwillWith(Faction.OfPlayer, -50)` |

## 6.6 Rewards — can a quest pay a techprint? **YES. [VERIFIED]**

`QuestNode_GiveRewards` fields: `inSignal`, `parms` (`SlateRef<RewardsGeneratorParams>`),
`customLetterLabel` / `customLetterText` (+`…Rules` RulePacks), `useDifficultyFactor`,
`nodeIfChosenPawnSignalUsed`, `variants` (`int?`, default 3 → presented as a
`QuestPart_Choice`), `addCampLootReward`.

`RewardsGeneratorParams` XML knobs: `rewardValue`, `giverFaction`, `chosenPawnSignal`,
`giveToCaravan`, `minGeneratedRewardValue`, `thingRewardDisallowed`, `thingRewardRequired`,
`thingRewardItemsOnly`, `disallowedThingDefs`, `allowRoyalFavor`, `allowGoodwill`,
`allowDevelopmentPoints`, `allowXenogermReimplantation`, `populationIntent`.

`RewardsGenerator.DoGenerate` splits into a **thing reward** and a **social reward**:
- Goodwill allowed iff `allowGoodwill && giverFaction != null && giverFaction != Faction.OfPlayer
  && giverFaction.CanEverGiveGoodwillRewards && giverFaction.allowGoodwillRewards
  && giverFaction.PlayerGoodwill <= 92`
- Royal favor iff `allowRoyalFavor && giverFaction.allowRoyalFavorRewards && giverFaction.def.HasRoyalTitles`
- Thing reward: `Rand.ElementByWeight(Reward_Items @ 3f, Reward_Pawn @ max(0, populationIntent))`
- Social reward: `Rand.ElementByWeight(Reward_Goodwill @ 1f, Reward_RoyalFavor @ 9f)`,
  **forced to `Reward_Goodwill` if the giver is hostile** — goodwill is the only thing a
  hostile faction can pay you.
- `RewardValueToGoodwillCurve` = (100,10) (500,15) (1000,20) (2000,35) (5000,50)
- `RewardValueToRoyalFavorCurve` = (100,2) (500,4) (2000,10) (5000,18)
- `AddMarketValueFillers` tops up the remainder with Silver/Gold/Uranium/Jade/Plasteel.

Reward classes: `Reward_Items`, `Reward_Pawn`, `Reward_Goodwill`, `Reward_RoyalFavor`,
`Reward_DevelopmentPoints`, `Reward_ReimplantXenogerm`, `Reward_CampLoot`,
`Reward_ShuttleLoot`, `Reward_DefinedThingDef`, `Reward_ArchonexusMap`,
`Reward_BestowingCeremony`, `Reward_PassageOffworld`, `Reward_PossibleFutureReward`,
`Reward_RelicInfo`, `Reward_Unknown`, `Reward_VisitorsHelp`.

**Techprints are NOT a `Reward_*` class** — they are a separate node,
`QuestNode_GiveTechprints` (see §7.7), added alongside `QuestNode_GiveRewards`.
Nothing in the shipped XML currently references `QuestNode_GiveTechprints`
(**[INFERRED]** it is reachable only through C# paths today), but the node exists, is
`public`, takes `fixedProject`, and is fully XML-authorable. **This is the mechanism the
Archinity design should use to make a specific research project a specific quest's reward.**

## 6.7 Signals — can XML wire arbitrary quest logic? Mostly yes.

`RimWorld/QuestUtility.cs:16-140` defines ~70 `QuestTargetSignalPart_*` constants emitted by
`SendQuestTargetSignals(questTags, signalPart, …)` (`:301-331`). Any tagged
`Thing`/`WorldObject`/`Pawn`/`Lord` emits `"<tag>.<signalPart>"`. Faction-relevant parts:
**`BecameHostileToPlayer`**, `ChangedFaction`, `ChangedFactionToPlayer`,
`ChangedFactionToNonPlayer`, `FactionMemberArrested`, `NoLongerFactionLeader`,
`Resolved` (peace talks), plus `MapGenerated`, `Killed`, `Destroyed`, `Researched`,
`SentSatisfied`/`SentUnsatisfied`, `AllEnemiesDefeated`, `TradeRequestFulfilled`, …

`SignalArgs` payloads actually used by vanilla: `"SENT"` (`List<Thing>` from shuttles),
`"GOODWILL"` (int — **overrides `QuestPart_FactionGoodwillChange.change`**), `"SUBJECT"`,
`"OUTCOME"` (`QuestEndOutcome` for `QuestPart_QuestEnd`), `"AVERAGEMOOD"`, `"INDEX"`.

Routing: `QuestPart_Pass{,All,Any,AllActivable,AnyActivable,AllSequence,AllOutMany,AnyOutMany,OutMany,OutRandom,WhileActive,Activable,WithFactionArg}`,
`QuestPart_MergeOutcomes`, `QuestPart_MTB`, and **`QuestPart_PassOutInterval`**
(`IntRange ticksInterval`, `List<string> outSignals`, `List<string> inSignalsDisable`) —
the vanilla "poll repeatedly" primitive.

Filters: ~35 `QuestPart_Filter_*` subclasses (`inSignal`, `outSignal`, `outSignalElse`,
args passed through), including `QuestPart_Filter_FactionHostileToOtherFaction` and
`QuestPart_Filter_FactionNonPlayer`. **But only three `QuestNode_Filter_*` XML wrappers
ship** (`_AnyColonistAlive`, `_DecreeNotPossible`, `_FactionNonPlayer`), so most filters
are C#-only.

## 6.8 Is a new QuestScriptDef XML-authorable? **YES — this is the dominant vanilla pattern.**

**87 shipped `QuestScriptDef`s use `<root Class="QuestNode_Sequence">` with zero custom C#**,
versus ~55 distinct `QuestNode_Root_*` classes each used once. There are ~215 non-root
`QuestNode_*` classes usable as XML building blocks, including full control flow:
`QuestNode_Sequence`, `_RandomNode`, `_Chance`, `_SubScript` (call another QuestScriptDef
with `<parms>`), `_LoopCount`, `_Set`/`_Unset`/`_IsSet`/`_IsNull`/`_IsTrue`/`_IsInList`,
comparisons `_Equal`/`_Greater`/`_Less` (+`*OrFail`), arithmetic
`_Multiply`/`_Divide`/`_Add`/`_Clamp`/`_EvaluateSimpleCurve`/`_SplitRandomly`,
`_ModIsActive`, `_ExpansionActive`, `_ViolentQuestsAllowed`, `_QuestUnique`.

`SlateRef<T>` gives XML a small expression language (`RimWorld.QuestGen/SlateRef.cs`):
`$varName` substitution, `(($varName))` high-priority pass, and `$(expr)` inline math via
`MathEvaluator.Evaluate` — e.g. `<delayTicks>$(randInt(12,28)*60000)</delayTicks>`.

**Reference file to copy for an Archinity faction quest:**
`Data/Core/Defs/QuestScriptDefs/Script_TradeRequest.xml` — 100% XML, and it is a
faction-flavoured, deadline-bearing, deliver-goods quest. Header carries
`rootSelectionWeight`, `rootMinProgressScore`, `defaultChallengeRating`, `expireDaysRange`,
`questNameRules`/`questDescriptionRules`.

Canonical goodwill snippets:
```xml
<!-- Royalty/Defs/QuestScriptDefs/Intro/Script_Intro_Deserter.xml:48-55 -->
<li Class="QuestNode_ChangeFactionGoodwill">
  <faction>Empire</faction>          <!-- bare FactionDef defName works -->
  <change>-100</change>
  <canSendLetter>false</canSendLetter>
  <canSendMessage>false</canSendMessage>
  <ensureHostile>true</ensureHostile>
  <reason>AcceptedDeserter</reason>
</li>

<!-- Royalty/Defs/QuestScriptDefs/Scripts_Permits.xml:141-145 -->
<li Class="QuestNode_ChangeFactionGoodwill">
  <faction>$permitFaction</faction>
  <change>$goodwillPenalty</change>
  <reason>QuestPawnLost</reason>
</li>
```

## 6.9 Where XML runs out and C# is required
1. **Goodwill or relation between two arbitrary non-player factions** (§6.3) — the big one.
2. `QuestPart_FactionRelationChange` has **no `QuestNode`**; XML can nudge goodwill but
   cannot hard-set a `FactionRelationKind`.
3. Faction selection by `techLevel` / `FactionDef` / category tag
   (workaround: `QuestNode_GetPawn` + `QuestNode_GetFactionOf`).
4. New state predicates — only 3 of ~35 filters have XML wrappers.
5. Emitting a new world signal from an untagged source.

---

# Q7 — TECHPRINTS — **VERIFIED, WITH CAVEATS**

## 7.1 The fields exist, exactly as assumed
`Verse/ResearchProjectDef.cs:44-50` — quoted verbatim: **[VERIFIED]**
```csharp
public int techprintCount;

public float techprintCommonality = 1f;

public float techprintMarketValue = 1000f;

[NoTranslate]
public List<string> heldByFactionCategoryTags;
```
All four names in the design are correct, including `heldByFactionCategoryTags`.

## 7.2 Derived members
```csharp
public int TechprintCount            // :204 — returns 0 if !ModLister.RoyaltyInstalled, else techprintCount
public int TechprintsApplied         // :216 — Find.ResearchManager.GetTechprints(this)
public bool TechprintRequirementMet  // :218 — TechprintCount > 0 && applied < required ⇒ false
public ThingDef Techprint            // :230 — first ThingDef whose CompProperties_Techprint.project == this
```
`CanStartNow` (`:168`) includes `&& TechprintRequirementMet`, so techprints are a hard gate
on starting a project — not a cost multiplier.

## 7.3 The techprint ThingDef is **auto-generated**, not hand-authored
`RimWorld/ThingDefGenerator_Techprints.ImpliedTechprintDefs()` — for every
`ResearchProjectDef` with `TechprintCount > 0` it emits a ThingDef named
`"Techprint_" + defName` with: **[VERIFIED]**
- `thingCategories = [Techprints]`, `tradeTags = ["Techprint"]`, `thingSetMakerTags = ["Techprint"]`
- `MarketValue = item.techprintMarketValue`, `Mass = 0.03`, `SellPriceFactor = 0.1`, `MaxHitPoints = 100`
- `comps = [CompProperties_Forbiddable, CompProperties_Techprint { project = item }]`
- texture hardcoded to `Things/Item/Special/TechprintUltratech`
- `modContentPack = item.modContentPack` (so ours will be attributed to our mod)

**You do not author the techprint item.** Adding `techprintCount` + `heldByFactionCategoryTags`
to a `ResearchProjectDef` is sufficient; the item appears by itself.

## 7.4 Hard `ConfigErrors` you must satisfy (`:406-425`) **[VERIFIED]**
```csharp
if (techprintCount == 0 && !heldByFactionCategoryTags.NullOrEmpty())
    yield return "requires no techprints but has heldByFactionCategoryTags.";
if (techprintCount > 0 && heldByFactionCategoryTags.NullOrEmpty())
    yield return "requires techprints but has no heldByFactionCategoryTags.";
if (!ModLister.RoyaltyInstalled && techprintCount > 0)
    yield return "defines techprintCount, but techprints are a Royalty-specific game system
                  and only work with Royalty installed.";
```
`techprintCount` and `heldByFactionCategoryTags` are a matched pair — set one, set both.

## 7.5 ⚠ **ROYALTY IS REQUIRED — AND FAILURE IS SILENT**
`PostLoad()` (`:446-457`):
```csharp
public override void PostLoad()
{
    base.PostLoad();
    if (!ModLister.RoyaltyInstalled) techprintCount = 0;
    if (!ModLister.BiotechInstalled) requiredAnalyzed = null;
}
```
Without Royalty, `techprintCount` is **zeroed at load**, `ImpliedTechprintDefs` `yield break`s
before generating anything, and the research simply becomes available with no gate.
There *is* a red `ConfigError`, so it is not fully silent — but the runtime behaviour is
"the gate quietly vanishes", which is exactly the failure mode this project keeps hitting.
**ACTION: confirm Royalty is in the Archinity load order before relying on techprints.**

## 7.6 The faction join — `categoryTag` ↔ `heldByFactionCategoryTags`
`RimWorld/TechprintUtility.GetResearchProjectsNeedingTechprintsNow(Faction, ...)`: **[VERIFIED]**
```csharp
if (p.TechprintCount == 0) return false;
if (p.IsFinished || p.TechprintRequirementMet) return false;
if (faction != null && (p.heldByFactionCategoryTags == null
                        || !p.heldByFactionCategoryTags.Contains(faction.def.categoryTag)))
    return false;
if (maxMarketValue != float.MaxValue && p.Techprint.BaseMarketValue > maxMarketValue) return false;
// ...also excludes anything already in `alreadyGeneratedTechprints` beyond the outstanding need
```
Selection weight (`GetSelectionWeight_NewTemp`):
```csharp
return project.techprintCommonality * (project.PrerequisitesCompleted ? 1f : 0.02f);
```
**A project whose prerequisites the player has not completed is 50× less likely to appear.**
This is a genuinely useful progression property: techprints self-sequence.

## 7.7 Can a techprint be a quest reward? **YES — two independent routes. [VERIFIED]**

**Route A — direct grant, no item.** `RimWorld.QuestGen/QuestNode_GiveTechprints.cs`:
```csharp
[NoTranslate] public SlateRef<string> inSignal;
public SlateRef<ResearchProjectDef> fixedProject;
[NoTranslate] public SlateRef<string> storeProjectAs;
```
→ emits `QuestPart_GiveTechprints { amount = 1; project = ...; outSignalWasGiven = "AddedTechprints" }`,
whose `Notify_QuestSignalReceived` calls `Find.ResearchManager.ApplyTechprint(project, null)`.
Note it grants the techprint *effect* directly (no physical item to haul).
`TestRunInt` fails the node if the project is null or `TechprintRequirementMet` — so the
quest simply will not generate once the player already has enough. `fixedProject` means
**we can pin a specific research project as a specific quest's reward from pure XML.**

**Route B — physical item in a reward package.** `RimWorld/ThingSetMaker_Techprints.cs`,
which routes through `TechprintUtility.TryGetTechprintDefToGenerate_NewTemp(parms.makingFaction, ...)`
and therefore respects `heldByFactionCategoryTags` vs the *making faction's* `categoryTag`.
Fields: `weightAccordingToPlayerNeeds` (bool, default true), `marketValueFactor` (private float, XML-settable).
Its `ExtraSelectionWeightFactor` boosts itself when the player has researchable projects
blocked on missing techprints (curve `(4,1) → (0,5)`).

**Route C (not a quest, listed for completeness) — trader stock.**
`StockGenerator_Techprints` with `countChances`, already documented in `recon-factions.md` §1.3.

**Route D — `SymbolResolver_AncientShrine`** also references techprints (ancient shrine loot).

---

# Q8 — RUNTIME `FactionDef` SUBSTITUTION

## 8.1 Is `faction.def` writable? **Yes, technically.** **[VERIFIED]**
`public FactionDef def;` (`Faction.cs:14`), serialised as
`Scribe_Defs.Look(ref def, "def")` — i.e. **by defName**, re-resolved from `DefDatabase` on
every load. Vanilla writes it in exactly one place, `FactionGenerator.cs:135`, during
faction construction. The Faction Customizer mod writes it at runtime from a GUI
(see `recon-factions.md` §6.1), which is evidence it does not immediately explode.

## 8.2 What actually breaks — enumerated

**Safe (read live, every time):**
- `def.techLevel` — every reader listed in `recon-factions.md` §7.2 reads it live.
- `def.pawnGroupMakers`, `maxPawnCostPerTotalPointsCurve`, `raidCommonalityFromPointsCurve`
- `def.permanentEnemy*`, `naturalEnemy`, `hostileToFactionlessHumanlikes`
- `def.categoryTag` → techprint eligibility changes immediately
- `def.*TraderKinds` — but note `Settlement_TraderTracker.TraderKind` is
  `baseTraderKinds[abs(settlement.HashOffset()) % count]`, so the *index* is stable while
  the *list* changes ⇒ every settlement's trader changes at once.
- `def.canSiege / canStageAttacks / autoFlee / arrivalMode*` — all read from `parms.faction.def`.

**Stale after a swap (cached, will not refresh):**
- **`Settlement.cachedMat`** (`RimWorld.Planet/Settlement.cs`) —
  `MaterialPool.MatFrom(base.Faction.def.settlementTexturePath, ..., base.Faction.Color, 3550)`.
  Cached per world object with no invalidation. **World-map settlement icons keep the old
  texture and colour until the object is recreated or the game reloaded.** **[VERIFIED]**
- `FactionDef.factionIcon` / `settlementTexture` / `royalFavorIcon` / `cachedDescription`
  are `[Unsaved]` caches **on the def**, not on the faction — they follow the def, so they
  are correct after a swap.
- `Faction.colorFromSpectrum` was chosen against the *old* `colorSpectrum`; the new def's
  spectrum is indexed with a stale `t`. Cosmetic.
- `Faction.leader` was generated from the old def's `pawnGroupMakers` / `fixedLeaderKinds`.
  Harmless but narratively wrong; `TryGenerateNewLeader()` fixes it.
- `Faction.ideos` was generated under the old def's `requiredMemes` / `disallowedMemes` /
  `allowedCultures`. It will not be re-validated. **[INFERRED — no re-validation code found]**
- `GoodwillSituationManager.cachedData` is keyed by `Faction` and recomputed every 1000
  ticks, so permanent-enemy / meme situations self-correct within ~17 seconds. **[VERIFIED]**

**Hard limits:**
- `FactionDef.techLevel` is **def-level, not instance-level**. Two `Faction`s sharing a def
  cannot have different tech levels. (Already established in `recon-factions.md` §7.1.)
- Runtime mutation of `def.techLevel` (rather than swapping `faction.def`) is
  process-global and **not saved** — it must be re-applied each session. TechBlock does this.
- `Faction.RelationWith` is unaffected by a def swap — the relation list is instance state.

## 8.3 Multiplayer
A `PatchOperation*` on FactionDef XML is byte-identical across clients and therefore MP-safe.
A **runtime** `faction.def = X` must run at an identical tick on both clients or the def
hash diverges. Doing it inside a synced tick/`GameComponent.FinalizeInit` is the only safe
shape. **[INFERRED — consistent with the project's existing MP rules, not separately verified]**

---

# Q9 — THE CREATIVE WORKAROUNDS

The design question is: *what is the cheapest way to make factions appear to act
autonomously?* Everything below is grounded in the verified findings above.

## 9.1 The core insight

> **Vanilla ships a complete, symmetric, serialised, UI-rendered NPC↔NPC relations
> system that nothing ever touches.** We do not need to build a diplomacy model. We need
> to write into one that already exists, and let vanilla's existing consumers
> (`GenHostility`, `attackTargetsCache`, `LordManager`, `SettlementDefeatUtility`'s
> mutual-enemy loop, the faction UI) do the rest.

Second insight: because `CheckReachNaturalGoodwill` and `CalculateAdjustedGoodwillChange`
both short-circuit on non-player pairs, **NPC↔NPC goodwill is inert, free-standing,
persisted state that nothing will fight us over.** Write it once, it stays.

## 9.2 What MUST be simulated (i.e. needs real state)

Only four things, and vanilla already stores all four:

| Concept | Vanilla storage | API | Cost |
|---|---|---|---|
| "A and B are at war" | `FactionRelation.kind == Hostile` on the A↔B pair | `a.TryAffectGoodwillWith(b, -N)` | 1 line |
| "Faction X has fallen" | `Faction.defeated` | `x.defeated = true` | 1 line |
| "Territory changed hands" | `Settlement.SetFaction(newOwner)` (and `Name`) | `WorldObject.SetFaction` is `public virtual` | 1 line |
| "A new power rose" | a new `Faction` + auto-placed settlement | `FactionGenerator.CreateFactionAndAddToManager(layer, def)` or `NewGeneratedFactionWithRelations(def, relations, hidden)` | 1–2 lines |

Every one is a `public` member. None requires a Harmony patch. **[VERIFIED]**

## 9.3 What can be NARRATED (no state at all)

- **Letters.** `Find.LetterStack.ReceiveLetter(label, text, LetterDef, LookTargets, Faction)`.
  A war can be reported as it "progresses" with zero simulation behind it.
- **Faction name and colour.** `Faction.Name` has a public setter (`Faction.cs:92-95`);
  `Faction.color` and `Faction.AllegianceColor` are public `Color?`. A faction can be
  *renamed* ("the Ashen Concord" → "the Ashen Remnant") to signal decline. Caveat: world-map
  settlement icons cache the colour in `Settlement.cachedMat` and will not update (§8.2).
- **Settlement names.** `Settlement.Name` is a public setter. Renaming a settlement on
  capture reads as conquest for free.
- **Quests.** A quest that says "the Concord asks you to raid a Confederacy caravan" is
  narration with a real mechanical payload attached (goodwill, items, techprints) but
  requires no world simulation. **This is fully XML-authorable** (§6.8): name the faction
  as a bare defName, telegraph a deadline with `QuestNode_Delay { isQuestTimeout }`, pay
  with `QuestNode_GiveTechprints { fixedProject }`, penalise with
  `QuestNode_ChangeFactionGoodwill`. Copy `Script_TradeRequest.xml`.
  **Quests are the highest-leverage narration channel we have** — they carry a real
  deadline UI, a red alert, letters, and a mechanical payout, for zero code.

## 9.4 The cheapest concrete architecture

**One `WorldComponent`, one timer, one table.** This is the minimum viable "living world".

```
WorldComponent_ArchinityGeopolitics : WorldComponent
    WorldComponentTick():
        if (Find.TickManager.TicksGame % 900000 != 0) return;   // every 15 days, same cadence
                                                                // vanilla already uses for
                                                                // SettlementProximityGoodwillUtility
        ResolveEra();     // deterministic, table-driven
```

Inside that 15-day beat, in a **fixed, deterministic order** (iterate
`Find.FactionManager.AllFactionsListForReading` by index, never a `HashSet`):

1. **Advance the scripted war ledger.** Keep a small serialised list of
   `(factionDefA, factionDefB, goodwillPerBeat)` rows, authored by us. Apply
   `a.TryAffectGoodwillWith(b, delta, canSendMessage:false, canSendHostilityLetter:false)`.
   When `kind` crosses to `Hostile`, vanilla fires
   `Notify_RelationKindChanged` → `attackTargetsCache.Notify_FactionHostilityChanged` +
   `Lord.Notify_FactionRelationsChanged` on every loaded map, so their pawns start shooting
   each other *if they ever co-occur*. Send our own letter (vanilla suppresses letters for
   NPC pairs). **Everything here is already-verified vanilla behaviour.**
2. **Resolve one settlement flip.** Pick the losing side's settlement furthest from the
   player, `SetFaction(winner)`, rename it, letter. Optionally
   `WorldObjectMaker.MakeWorldObject(DestroyedSettlement)` instead, for a razing.
3. **Check for collapse.** If a faction has zero settlements left, `faction.defeated = true`.
   Vanilla then removes it from raids, visitors, quests, trader arrivals, and greys it out
   in the faction tab — an entire "faction fell" feature for one assignment.
4. **Check for a rise.** When an era gate opens, `CreateFactionAndAddToManager(layer, def)`.
   `NewGeneratedFaction` auto-places one settlement (`FactionGenerator.cs:177`), so a
   faction appearing on the map is free. Use `NewGeneratedFactionWithRelations` if it should
   arrive already hostile to someone.

**This is one file, well under 200 lines, no Harmony, no new Def types.**

## 9.5 Simulated vs narrated — the honest split

| Player-visible claim | Real, or theatre? |
|---|---|
| Two NPC factions are at war | **Real.** `kind == Hostile` is genuine state; their pawns fight on shared maps; `SettlementDefeatUtility` gives you +20 with a faction's enemies when you raze its last base. |
| The war is *progressing* | **Theatre.** No battles are resolved. A ledger ticks; we narrate. |
| Territory changed hands | **Real** (the settlement's faction/name/trader/loot/defenders all change) but the *reason* is scripted. |
| A faction is collapsing | **Real** — `defeated` is honoured by 12 vanilla systems. |
| A new faction has risen | **Real** — a genuine `Faction` with a settlement, traders, and raids. |
| Factions have opinions about each other | **Real** and visible in the faction UI's relation list. |

The only thing that is pure theatre is the *causal chain*, and the player cannot inspect it.

## 9.6 Pure-XML levers worth using alongside

These need no code at all: **[VERIFIED]**
- `permanentEnemyToEveryoneExcept` — the one XML way to express targeted, permanent
  hostility (allow-list semantics: hostile to everyone *not* listed). Good for a faction
  that should read as universally reviled with one ally.
- `naturalEnemy` — starts at -80 and pins natural goodwill at -130. Player-facing only for
  the natural-goodwill part, but the -80 *initial* value applies to NPC pairs too via
  `TryMakeInitialRelationsWith`.
- `settlementGenerationWeight` — set an "emerging" faction to 0 so it starts with a `Faction`
  object and no settlements; place settlements later from the WorldComponent as it rises.
  (Careful: `NewGeneratedFaction` auto-places one settlement for any non-hidden faction.)
- `earliestRaidDays` — gates a faction out of raids for the first N days since settling.
  A clean era gate.
- `raidsForbidden` — a faction that exists, trades, and holds territory but never raids.
- `techprintCount` + `heldByFactionCategoryTags` + `categoryTag` — makes a faction's
  *existence* and *relationship* a research gate. This is the strongest pure-XML link
  between the diplomacy layer and the progression layer. See Q7.
- `ThingDef.requiresFactionToAcquire` — `ThingDef.PlayerAcquirable` returns false when the
  named faction is not in the world (`recon-factions.md` §1.6). Combined with a faction
  that rises mid-game, this makes items literally appear in the world's item pool when a
  faction arrives.

## 9.7 Multiplayer discipline for the WorldComponent

Per `CLAUDE.md`, a second Harmony assembly requires an explicit decision — but this needs
**no Harmony at all**, only a `WorldComponent` subclass, which is a different (and lower)
risk class. Constraints, in order of importance: **[INFERRED where marked]**
1. **Prefer zero `Rand` calls.** A fully table-driven, deterministic ledger has no
   desync surface whatsoever. If randomness is unavoidable, seed it from
   `Find.TickManager.TicksGame` + `faction.loadID` via `Rand.PushState(seed)` /
   `Rand.PopState()` so both clients compute the same value from the same inputs. **[INFERRED]**
2. **Iterate deterministically.** `AllFactionsListForReading` by index; never
   `Dictionary`/`HashSet` enumeration order. Vanilla itself does this — note
   `SettlementProximityGoodwillUtility.SortProximityGoodwillOffsets` sorts by
   `faction.loadID` specifically to get a stable order. **[VERIFIED — good precedent to copy]**
3. **Never mutate world state from GUI code.** This is exactly the flaw that makes Faction
   Customizer desync (`recon-factions.md` §6.1).
4. `WorldComponentTick` runs inside `World.WorldTick`, which runs inside the synced tick
   loop, so it executes on both clients at the same tick. **[INFERRED — not verified against
   the Multiplayer mod's source]**

## 9.8 What NOT to attempt

- **Do not build on `GoodwillSituationDef`.** Every worker hardcodes `Faction.OfPlayer`,
  and `GoodwillSituationManager` errors out on player input. It cannot express NPC↔NPC
  relations, no matter how the XML is written. **[VERIFIED]**
- **Do not use `SetRelationDirect` between two visible factions.** It `Log.Error`s and
  returns when both sides `HasGoodwill` (`Faction.cs:643-647`). Use `TryAffectGoodwillWith`.
- **Do not expect `QuestNode_ChangeFactionGoodwill` to move an NPC↔NPC relation.** It
  cannot — there is no field for the other side, and `QuestPart_FactionGoodwillChange`
  early-outs on `faction == Faction.OfPlayer` while hardcoding `Faction.OfPlayer` as the
  actor. Same for `QuestPart_FactionRelationChange`, which has no XML node at all. **[VERIFIED]**
- **Do not rely on `mustStartOneEnemy`.** Dead field. **[VERIFIED]**
- **Do not rely on `naturalColonyGoodwill`.** Does not exist in 1.6. **[VERIFIED]**
- **Do not expect natural drift to undo our writes.** It only touches player pairs, only
  after 50 days out of a ±50 band, and only by ±10. NPC pairs never drift at all.
- **Do not `Remove()` a non-temporary faction.** `FactionManager.Remove` `Log.Error`s
  unless `faction.temporary`. Use `defeated = true` instead. **[VERIFIED]**
- **Do not assume Royalty is optional** if techprints are load-bearing (§7.5).

---

# APPENDIX — THE SHORTEST PATH FROM HERE

If exactly one thing gets built from this document, build this:

**A.** A `WorldComponent` on a 900,000-tick beat that walks a hand-authored war ledger and
calls `a.TryAffectGoodwillWith(b, delta, canSendMessage:false, canSendHostilityLetter:false)`
for NPC pairs, sends its own letters, flips `Settlement.SetFaction` on capture, and sets
`faction.defeated = true` on collapse. **No Harmony. No new Def types. Deterministic.**

**B.** Pure-XML `QuestScriptDef`s modelled on `Script_TradeRequest.xml` that name Archinity
factions directly (`<faction>Archinity_Foo</faction>` — the string→`Faction` converter
handles it), impose deadlines with `QuestNode_Delay { isQuestTimeout }`, pay
`QuestNode_GiveTechprints { fixedProject }` on success, and
`QuestNode_ChangeFactionGoodwill` on failure.

**C.** Optionally, ~40 lines of C# for a `QuestPart_ChangeInterFactionGoodwill` +
`QuestNode` pair, so a quest outcome can also move an NPC↔NPC relation. This is the only
capability vanilla's quest layer genuinely lacks. Per `CLAUDE.md` this would have to live
in `Archinity.Altar` or be an explicit new-assembly decision — but note it needs **no
Harmony patch**, only new `QuestPart`/`QuestNode`/`WorldComponent` subclasses, which is a
materially lower risk class than a Harmony assembly.

## Open items / things NOT verified
- Whether the Multiplayer mod's tick sync covers `WorldComponentTick` identically on both
  clients. Assumed yes (it is inside `World.WorldTick` inside the synced tick loop) but
  **not verified against the Multiplayer mod's source.**
- Whether Royalty is actually in the Archinity load order. **Techprints are dead without it**
  (§7.5) — confirm before the design leans on them.
- Whether `Faction.ideos` needs re-validation after a `faction.def` swap (§8.2). No
  re-validation code was found; the consequences of a mismatched ideo were not traced.
- The behaviour of `TryAffectGoodwillWith` on an NPC pair was traced through the source but
  **not observed running in game.** Every branch is accounted for and none requires the
  player, but an in-game confirmation is cheap and worth doing before building on it.
