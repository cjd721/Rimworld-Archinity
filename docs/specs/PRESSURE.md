# Pressure

## Purpose and scope

How the difficulty half of [`docs/requirements/PRESSURE.md`](../requirements/PRESSURE.md) will
be built: **the storyteller mechanism** — how threat strength, incident composition and incident
frequency are measured, controlled and made independent of one another, and where the campaign's
bounded contributors (wealth, era time, military capability, Reverence, diplomacy) enter.

This document owns:

- the storyteller we ship and why it is ours rather than a patch on Cassandra;
- the single seam where threat **strength** is composed, and what may and may not feed it;
- the **frequency** levers and the cadence comp that reads campaign state;
- the **composition** levers — points-band gating, faction selection, and the pawn-cost curve
  that turns points into quality instead of quantity;
- the **positive half** — arrivals, aid and volunteers that scale with Reverence;
- **protecting the ordered spine** from storyteller RNG;
- the multiplayer constraints on all of the above.

It does not own: **Trace and the Glitterite pursuit**
([#56](https://github.com/cjd721/Rimworld-Archinity/issues/56)) — this document says how big a
pursuit raid is and how it is authored, #56 says what starts one and when; **raid objectives as
distinct from raid size** ([#77](https://github.com/cjd721/Rimworld-Archinity/issues/77)); **the
faction demand** ([#91](https://github.com/cjd721/Rimworld-Archinity/issues/91), whose spec is
[`POLITICS.md`](POLITICS.md)) — #91 says what a refusal fires, this document says how big it is;
**Reverence itself** ([`RELIGION.md`](RELIGION.md)); **the window the readout is drawn in**
([#61](https://github.com/cjd721/Rimworld-Archinity/issues/61)); **the ordered Archon beats
themselves** ([`CHARTING.md`](CHARTING.md)).

**Every number in this document is an open parameter.** Weights, curve points, band thresholds,
cadences and magnitudes are **Balance**, held as fog on
[#2](https://github.com/cjd721/Rimworld-Archinity/issues/2) — *"costs, durations, threat
magnitudes and progression rates. Last, after the structure is concrete."* The structure below is
what Balance will be given numbers for.

## The build

**We ship our own `StorytellerDef`s, compose strength in one Harmony postfix, and take frequency
and composition entirely from existing XML fields.** No new assembly, no rival scheduler, no
blanket block of vanilla incidents.

Vanilla's storyteller is a roster of independent generators over a shared target list, re-asked
every 1000 ticks; adding to the roster is additive rather than competitive [V]
(`RimWorld.Storyteller.MakeIncidentsForInterval`). Three distinct mechanisms already produce the
three outputs the requirement names, and the whole build is putting campaign state into each of
them without letting any one leak into another.

| Output | Vanilla mechanism | Our entry point |
|---|---|---|
| **Strength** | `StorytellerUtility.DefaultThreatPointsNow` | one Harmony postfix |
| **Frequency** | comp scheduling — `IncidentCycleUtility`, `Rand.MTBEventOccurs` | XML on our comps, plus one cadence comp |
| **Composition** | `StorytellerComp.IncidentChanceFinal`, `IncidentDef.min/maxThreatPoints`, `FactionDef.maxPawnCostPerTotalPointsCurve` | XML, plus one postfix |

### 1. The storyteller — our own `StorytellerDef`s

`StorytellerDef` is a plain `Def` whose `comps` list is instantiated reflectively by
`Storyteller.InitializeStorytellerComps` from `def.comps[i].compClass` [V]. A new storyteller is
therefore pure XML: an abstract `Archinity_BaseStoryteller` carrying the shared comps and curves,
and three concrete defs reproducing the Cassandra / Randy / Phoebe temperaments so **the players
keep the choice**. `StorytellerDef.listVisible` is a vanilla field [V], so hiding the stock three
is one `PatchOperationReplace` each if we decide the campaign requires our tuning.

**Owning the def is not cosmetic — the comp list is a hash salt.**
`IncidentCycleUtility.IncidentCountThisInterval(target, randSeedSalt, …)` is called by every
scheduled comp with `Find.Storyteller.storytellerComps.IndexOf(this)` as `randSeedSalt`, and
seeds `Rand` from `Gen.HashCombineInt(Find.World.info.persistentRandomValue, target.ConstantRandSeed,
randSeedSalt, i)` [V]. Inserting a comp into a *shared* parent def re-indexes every later comp and
silently re-rolls its entire pre-computed hit schedule. The runtime list is also filtered by
`StorytellerCompProperties.Enabled` [V], so a change to the active mod set moves the same indices.
That is **T-66**. A storyteller we own has a list we control and append to.

Four `StorytellerDef` curve fields are ours for free and need no code:

- `pointsFactorFromDaysPassed` — a global multiplier on threat points, evaluated on
  `GenDate.DaysPassedSinceSettle` inside `DefaultThreatPointsNow` [V]. **Vanilla's is
  `(10, 0.70) → (40, 1.00)`, i.e. a ramp-in that is a no-op after day 40** [V]. It is the cheapest
  campaign-time term in the game and currently unused past the first forty days.
- `pointsFactorFromAdaptDays` — the adaptation response (Cassandra reaches `2.00` at 180
  adapt-days) [V].
- `adaptDaysMin` / `adaptDaysMax` / `adaptDaysGrowthRateCurve` — the cap and rate of adaptation,
  which is the only outcome-measuring input vanilla has [V].
- `populationIntentFactorFromPopCurve` / `populationIntentFactorFromPopAdaptDaysCurve` — how a
  two-founder headcount biases the incident pool (§6).

### 2. Strength — one postfix on `StorytellerUtility.DefaultThreatPointsNow`

**Mechanism.** A `[HarmonyPostfix]` on `RimWorld.StorytellerUtility.DefaultThreatPointsNow(IIncidentTarget)`
in the assembly we already ship. It recomposes the result:

```
final = Clamp( (vanillaResult + Σ additive_i(target)) × Π factor_j(target),
               floorCurve(target), ceilingCurve(target) )
```

Every term, factor, floor and ceiling is a `SimpleCurve` read from one new `PressureDef` instance.
The postfix itself contains no numbers.

**Why this seam, and a correction to what this ticket inherited.**
[#7](https://github.com/cjd721/Rimworld-Archinity/issues/7) §6 and the superseded comments on
[#9](https://github.com/cjd721/Rimworld-Archinity/issues/9) put the postfix on
`RimWorld.Planet.MapParent.PlayerWealthForStoryteller`. **That member does not exist.**
`RimWorld.Planet.MapParent` is `WorldObject, IThingHolder` and is **not** an `IIncidentTarget` [V].
`PlayerWealthForStoryteller` is declared on **`RimWorld.IIncidentTarget`** and implemented by
`Verse.Map`, `RimWorld.Planet.Caravan` and `RimWorld.Planet.World` [V] — three implementors, none
of them `MapParent`. So the inherited seam was not merely wrong for the settled requirement that
**wealth remains a real, bounded contributor**; it was unpatchable as written.

Restated against the type that actually declares the property: patching `IIncidentTarget`'s
implementors is still the wrong seam, because the number they return is consumed by **two distinct
reading methods** [V]:

- **`StorytellerUtility.DefaultThreatPointsNow`**, which evaluates four `private static readonly`
  curves against it — `PointsPerWealthCurve`, `PointsPerColonistByWealthCurve`,
  `PointsFactorForColonyMechsCurve`, `PointsFactorForColonySubhumanCurve`. These are four curve
  evaluations *inside one method*, not four consumers.
- **`StorytellerUtility.GetProgressScore`**, which gates quests via
  `QuestScriptDef.rootMinProgressScore` and is itself read downstream by
  `StorytellerComp_OnOffCycle.acceptPercentFactorPerProgressScoreCurve`.

**The earlier "eight consumers" count was wrong twice.** Two of the eight never touch the property
at all: `StorytellerComp_RefiringUniqueQuest.minColonyWealth` is compared against
`WealthUtility.PlayerWealth`, and `StorytellerComp_FactionInteraction.minWealth` against
`map.wealthWatcher.WealthTotal` [V]. Of the six that remain, four are the curve evaluations above.
The load-bearing half survives: writing a synthetic number into the property still moves quest
gating as well as threat points, invisibly. Composing *above* the aggregation leaves wealth
genuinely wealth and makes its share a function of how large the other terms are — which is exactly
the 10–20% the requirement describes as illustrative.

**Consequence to hand back:** [#22](https://github.com/cjd721/Rimworld-Archinity/issues/22) §1 asks
whether `MapParent` is the only implementation of `PlayerWealthForStoryteller`, because a postfix
there would miss caravans. **§1's premise is false, not merely no longer load-bearing** — `MapParent`
implements nothing of the kind, and the real implementor set is `Map` / `Caravan` / `World`. The
question as posed cannot be answered as posed and should be struck rather than carried. §1's
*second* half — that the property also feeds `GetProgressScore` and therefore quest gating — is
confirmed here and is the reason the seam moved.

**The terms.** Each input is verified to exist and be readable; the claim that they *compose* into
the right feel is [I] until played.

| Term | Reads | Bound | Evidence |
|---|---|---|---|
| Wealth, colonists, mechs, animals | `vanillaResult` unchanged | vanilla's own curves saturate (`PointsPerWealthCurve` flat 0 below 14,000, 4,200 at 1M) | [V] |
| Era time | ticks since the era-start stamp, through a curve that **reaches a ceiling** | ceiling is the curve's last point | [V] the stamp is `AdvanceEra()`'s, per #7; see *Outstanding decisions* |
| Military capability | summed `CostApparent` of finished `ResearchProjectDef`s; free-colonist count; `map.wealthWatcher.WealthItems` | curve per indicator | [V] all three are public and already computed |
| Reverence | global Reverence derived from `WorldComponent_Reverence` | band curve | [V] [`RELIGION.md`](RELIGION.md) § *The build — Reverence* |
| Diplomacy | count of `Faction`s with `PlayerRelationKind == Hostile`, excluding `Hidden` and `temporary` — the mirror of `StorytellerUtility.AllyIncidentFraction` | curve, capped | [V] |

**Trace is deliberately absent from this list.** See §4; it never touches the global scalar, which
is the structural reason Reverence and Trace cannot silently multiply.

**The postfix must be `Rand`-free, and this is a hard constraint rather than a preference.**
`DefaultThreatPointsNow` is called outside any incident-firing path: by
`StorytellerComp_OnOffCycle.MakeIntervalIncidents` to evaluate `acceptPercentFactorPerThreatPointsCurve`,
by VEF's `QuestWorker` and `QuestUtils` against `Find.World`, and by `Storyteller.DebugString()`
**from UI rendering** [V]. Vanilla survives this because `Map.IncidentPointsRandomFactorRange` is
`FloatRange.One` and `Rand.Range(min, max)` returns `min` without drawing when `max <= min` [V],
and because `GlobalPointsMin()` uses `Rand.RangeSeeded`, which pushes and pops its own state [V].
Any `Rand` call we add breaks that property and desyncs from a hover.

**The ceiling.** Vanilla clamps to `[GlobalPointsMin(), 10000]` *inside* the method [V]; our
postfix runs after, so a late-campaign ceiling above 10,000 is reachable. It is not taken by
default — `ceilingCurve` starts flat at 10,000 until Balance raises it, because consumers that
assume the vanilla ceiling have not been enumerated.

**One mod in the corpus already rewrites this method, and it is a live collision risk.**
**Mechanoids: Total Warfare** (`nyar.nclvstw`, workshop `3555799437`,
`1.6/Assemblies/NCL_Storyteller.dll`) ships `NCL_Storyteller.Patch_StorytellerUtility`, which
**transpiles `DefaultThreatPointsNow`** — injecting an additive term into the body and replacing
the hardcoded `10000f` ceiling with its own [V]. Two consequences for this build: our postfix sees a
`vanillaResult` that is already neither vanilla's value nor vanilla's clamp when that mod is
active, and our `ceilingCurve` is no longer the only thing deciding what 10,000 means. A transpiler
and a postfix do not conflict at the Harmony level, so **nothing will report this** — the symptom
is a scaling curve that behaves differently between two mod sets. Re-check the shipped IL whenever
that mod updates, and treat the observable checks in *Verification* as mod-set-specific.

### 3. Frequency

**All of it is XML on comps we own** [V]:

| Lever | Field | Comp |
|---|---|---|
| cadence window | `onDays`, `offDays`, `minSpacingDays`, `numIncidentsRange` | `StorytellerCompProperties_OnOffCycle` |
| ramp-in | `acceptFractionByDaysPassedCurve` | `_OnOffCycle` |
| strength coupling | `acceptPercentFactorPerThreatPointsCurve`, `acceptPercentFactorPerProgressScoreCurve` | `_OnOffCycle` |
| mean time between | `mtbDays`, `maxThreatBigIntervalDays`, `randomPointsFactorRange`, `categoryWeights` | `StorytellerCompProperties_RandomMain` |
| per-year rate, danger and wealth gates | `baseIncidentsPerYear`, `minSpacingDays`, `minDanger`, `minWealth`, `fullAlliesOnly` | `StorytellerCompProperties_FactionInteraction` |
| beacon / siege cadence | `ThreatsGeneratorParams`: `onDays`, `offDays`, `numIncidentsRange`, `threatPoints`, `minThreatPoints`, `currentThreatPointsFactor`, `faction` | `StorytellerCompProperties_ThreatsGenerator` |

**Independence is achievable, not free, and that is the honest answer to the ticket's question 3.**
Vanilla already couples frequency to strength in two places: Cassandra's `ThreatSmall` comp carries
`acceptPercentFactorPerThreatPointsCurve` `(800, 1) → (2800, 0)`, so small threats **stop firing
entirely** once points pass 2,800 [V]; and `IncidentWorker.CanFireNow` rejects any def whose
`minThreatPoints`/`maxThreatPoints` band excludes the current points [V]. Raising strength
therefore changes the mix and the cadence unless those curves are re-authored. Because the
storyteller is ours, they are ours to author — the price of independence is three curves, paid
once.

**The cadence comp — `StorytellerComp_Pressure`.** Diplomacy, era and Reverence must be able to
change *how often*, not only *which*. Nothing in XML reaches the accept fraction from campaign
state, but `IncidentCycleUtility.IncidentCountThisInterval` is `public static` and takes
`acceptFraction` as its last argument [V]. (`IncidentCycleUtility` itself is **not** a static class
[V] — the method is what is static, and we call it rather than extending the type.) One comp class,
~70 lines, reproduces
`StorytellerComp_FactionInteraction`'s shape and supplies `acceptFraction` from a `PressureDef`
curve over campaign state. It is used twice:

- **hostile cadence** — accept fraction rises with hostile-faction count and era time;
- **welcome cadence** — the positive half, §5.

Because the count comes from `IncidentCycleUtility`, the schedule is a pure function of
`Find.World.info.persistentRandomValue`, the target's `ConstantRandSeed`, the comp index and the
interval number [V]. It draws nothing from the shared `Rand` stream, which makes it the safest
scheduler in the game for our purposes.

### 4. Composition — quality, not only quantity

Points buy quantity by default. Three verified levers change that, and two of the three are XML:

1. **`FactionDef.maxPawnCostPerTotalPointsCurve`.** `PawnGroupMakerUtility.MaxPawnCost` evaluates
   it to cap the cost of the most expensive single pawn in a group, then
   `ChoosePawnGenOptionsByPoints` draws options under that cap weighted by
   `PawnWeightFactorByMostExpensivePawnCostFractionCurve` [V]. **This is the "four juggernauts, not
   forty men" dial**, per faction, in XML, on a vanilla `FactionDef` field. Note `MaxPawnCost` also
   takes `Mathf.Min(a, totalPoints / raidStrategy.minPawns)` [V] — a strategy with a high
   `minPawns` *forces* quantity, so the two must be authored together.
2. **`IncidentDef.minThreatPoints` / `maxThreatPoints`** gate which incident is legal at which
   strength [V]. This is how a qualitative regime shift is expressed as data: an era's signature
   raid simply becomes legal at a points band.
3. **`StorytellerComp.IncidentChanceFinal`** is the selection weight, and it is the attention
   weight the requirement asks for. It already multiplies `IncidentWorker.BaseChanceThisGame`,
   population factors, `IncidentWorker.ChanceFactorNow(target)` (a `virtual` returning `1f` in the
   base class, i.e. a free per-worker hook) and the recent-fire decay [V]. **It is `protected`, not
   public** [V]: a patch must name it by string — `[HarmonyPatch(typeof(StorytellerComp),
   "IncidentChanceFinal")]`, or `AccessTools.Method` with non-public binding — and our own code
   cannot call it directly from outside the type. Harmony patches it regardless; a public-method
   lookup finds nothing and fails at patch time rather than silently, which is the one mercy here.

**The authored raid — reuse, not new code.** VEF ships
`VEF.Storyteller.IncidentWorker_RaidEnemySpecial`, a `workerClass` that overrides
`TryResolveRaidFaction`, `ResolveRaidPoints` and `ResolveRaidStrategy` to read a
`VEF.Storyteller.IncidentDefExtension` mod extension carrying `forcedFaction`, `forcedPointsRange`
and `forcedStrategy` [V]. **An `IncidentDef` with a fixed faction, a fixed points band and a fixed
strategy is therefore pure XML.** That is the carrier for the Glitterite detection raid
([#56](https://github.com/cjd721/Rimworld-Archinity/issues/56) says when, this says how big), for a
faction demand's refusal raid ([#91](https://github.com/cjd721/Rimworld-Archinity/issues/91) says
what fires it), and for any Chronicle beat's fixed opposition.

> **Silent failure in that donor — T-65.** `IncidentDefExtension.forcedPointsRange` defaults to
> `IntRange.Zero`, but the fall-through sentinel in `ResolveRaidPoints` is `IntRange.One` [V]
> (verified in both VEF 1.6 copies). An `IncidentDef` using `IncidentWorker_RaidEnemySpecial`
> **without** an explicit `forcedPointsRange` gets `parms.points = 0 × threatScale = 0` — a raid
> with no budget — rather than default scaling. To get vanilla point scaling you must write
> `<forcedPointsRange>1~1</forcedPointsRange>`. Nothing reports it.

**Why Trace and Reverence cannot multiply.** Reverence enters the **global scalar** (§2) and the
**selection weight** (§4.3). Trace enters **neither**: a pursuit raid is an authored `IncidentDef`
whose points come from `forcedPointsRange` or from #56's own comp setting `parms.points` directly,
bypassing `DefaultThreatPointsNow`. The two axes are disjoint code paths rather than two factors in
one product, which is what makes the independence structural instead of arithmetic.

**Diplomacy and the attention weight.** VEF already carries half of this: a postfix on
`StorytellerComp.IncidentChanceFinal` scales the weight by ally count or enemy count — capped at 9,
floored at 0.1 — configured purely in XML through `StorytellerDefExtension.incidentSpawnOptions` on
the storyteller def [V]. **But it offers exactly four directions —** `alliesReduceThreats`,
`alliesIncreaseGoodIncidents`, `enemiesReduceThreats`, `enemiesIncreaseGoodIncidents` **— and
"enemies increase threats", which is what the requirement names, is not among them** [V]. Two
builds:

- **(a)** set `alliesReduceThreats: true` and take the inverse expression. XML only, zero code,
  but the ladder is the coarse 0.1–9 one VEF chose and the direction is inverted.
- **(b)** our own postfix on the same method, ~25 lines, weighting by hostile count, Reverence band
  and era through `PressureDef` curves. Because the method is `protected`, the patch target is
  declared by string, as above.

**Recommend (b)**, and note it composes with VEF's rather than replacing it — both are postfixes on
the same method, both multiply `__result`, and the order does not matter. What separates them is
that (a) cannot express the requirement's direction and cannot read Reverence at all.

### 5. The positive half

Reverence raises attention in **both** directions, and the friendly direction is the one that gets
forgotten. It has a native carrier: `StorytellerComp_FactionInteraction` generates arrivals at
`baseIncidentsPerYear`, multiplied by `StorytellerUtility.AllyIncidentFraction(fullAlliesOnly)`
[V] — which counts non-hostile factions over `CanEverBeNonHostile` ones through
`AllyIncidentFractionFromAllyFraction` `(1, 1) → (0.25, 0.6)`, and returns `-1` (yielding nothing)
when the player has no allies [V]. Cassandra uses it four times: `RaidFriendly`,
`TraderCaravanArrival`, `VisitorGroup`, `TravelerGroup` [V].

The build is the **welcome cadence** instance of `StorytellerComp_Pressure` (§3) plus our own
`IncidentDef`s for pilgrims, offerings and volunteers, whose accept fraction is a curve on global
Reverence. Reusing vanilla workers wherever one already does the job: `IncidentWorker_VisitorGroup`,
`IncidentWorker_TraderCaravanArrival`, `IncidentWorker_WandererJoin` and the `GiveQuest` category
all cover the shapes the requirement names. Whether a pilgrim *joins* or *visits* is an
`IncidentDef.populationEffect` choice, which also puts it under population intent (§6) rather than
letting it run free.

### 6. Population inputs, and whether they survive

They survive because we do not substitute wealth. All [V]:

- `StorytellerUtilityPopulation.PopulationIntent` feeds `StorytellerComp.IncidentChanceFactor_PopulationIntent`,
  bounded below by `StorytellerCompProperties.minIncChancePopulationIntentFactor` (default `0.05`).
- `IncidentDef.chanceFactorByPopulationCurve`, `minPopulation`, `minGreatestPopulation` and
  `populationEffect` are per-incident XML.
- **`TrySelectRandomIncident` splits the pool before weighting**: it rolls
  `Rand.Chance(IncreasesPopChanceByPopIntentCurve.Evaluate(PopulationIntent))` and then draws
  *only* from incidents with a non-`None` `populationEffect`, or *only* from those without [V].
  A permanently small founder colony therefore sits at high population intent and biases selection
  toward pawn-gaining incidents at the level above the weights. The corrective is
  `populationIntentFactorFromPopCurve` on our storyteller def — which is why §1 lists it.
- `IncidentWorker.CanFireNow`'s `minPopulation` gate counts
  `PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive_FreeColonists` — **global across
  maps** [V]. With one player faction and one colony that is inert; it becomes live during the
  gravship and orbital acts, when a second map exists.

Adaptation stays in the formula rather than being replaced: `TotalThreatPointsFactor` is applied as
`Mathf.Lerp(1, factor, difficulty.adaptationEffectFactor)` inside the vanilla computation and is
capped by `StorytellerDef.adaptDaysMax` [V]. It is the only thing in the game that measures
*outcomes* — it climbs when raids are crushed and falls when colonists are lost — and the
requirement's "practical broad indicators" clause is best served by leaving it on and tuning
`pointsFactorFromAdaptDays`.

### 7. Protecting the ordered spine

Four levers, all [V], in the order they should be reached for:

1. **Do not route a beat through a random comp.** `Storyteller.MakeIncidentsForInterval` also walks
   every **ongoing quest**, calling `IIncidentMakerQuestPart.MakeIntervalIncidents` on enabled
   `QuestPartActivable`s [V]. A live quest is itself an incident generator on the same 1000-tick
   interval. [`CHARTING.md`](CHARTING.md) already builds the spine on
   `QuestPart_ChartingSpine : QuestPart_SubquestGenerator`; beats fire from there, and the roster
   never gets a vote.
2. **Quiet the window.** `IncidentWorker.CanFireNow` returns false when any active `GameCondition`
   on the target map has `def.preventIncidents` [V]. A beat-scoped `GameConditionDef` is the
   vanilla-shaped way to suppress competing threats, in XML.
3. **Make the beat unreachable by RNG.** The random comps draw only from the `IncidentCategoryDef`
   they declare [V], so an `IncidentDef` in the `Special` category cannot be selected by them;
   `Special` also sets `ShouldIgnoreRecentWeighting` [V]. `ScenPart_DisableIncident` is the
   permanent blacklist if one is ever needed [V].
4. **Floor the beat's opposition.** `IncidentDef.minThreatPoints` on a beat's raid stops it firing
   under-strength, and `forcedPointsRange` (§4) pins it outright.

Three registered traps bear directly on authored beats and must be read before one is written:
**T-17** (raid faction selection is fail-open and fail-quiet — an ineligible faction is *allowed*,
not replaced), **T-14** (VFE Empire's static constructor blacklists every `RaidStrategyDef` but its
own on the deserter faction, so a strategy we author is silently excluded), and **T-16**
(`RaidStrategyDef` and `QuestScriptDef` have no `minTechLevel` — a tech gate written in XML never
fires).

### Cost

| Piece | Kind | Estimate |
|---|---|---|
| `Archinity_BaseStoryteller` + three concrete `StorytellerDef`s | XML | ~250 lines |
| `PressureDef`, `PressureTermDef`, `PressureBandDef` + one instance | XML + C# Def classes | ~120 XML, ~90 C# |
| `DefaultThreatPointsNow` postfix + term workers | C# | ~120 |
| `StorytellerComp_Pressure` + its `StorytellerCompProperties` | C# | ~70 |
| `IncidentChanceFinal` postfix (diplomacy / Reverence weight) | C# | ~25 |
| Authored raids — `IncidentWorker_RaidEnemySpecial` + `IncidentDefExtension` | XML | per raid, ~15 lines |
| `maxPawnCostPerTotalPointsCurve` patches on band factions | XML patch, annotated | ~10 per faction |
| Pressure readout supplied to [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61)'s surface | C# | ~40 |
| `layerWhitelist` patches for the orbital act (**T-48**) | XML patch, annotated | ~40 lines |

**~345 lines of C# in the assembly we already ship, ~450 lines of XML, no new assembly, no
recompiled third-party DLL.**

## Persistence and multiplayer

**Nothing in this build is new saved state.** Threat points are computed on demand from a fresh
`IncidentParms` per call with no maintained snapshot [V]; every tunable is a `Def`; the terms read
state other systems already scribe — WTL's `GameComponent_TechLevel` and the era-start stamp,
`WorldComponent_Reverence`, `Find.ResearchManager`, `Find.FactionManager`, `map.wealthWatcher`.
Adding this to a save that predates it changes behaviour on the next storyteller interval and
scribes nothing, so there is no migration and no version gate. `StorytellerComp_Pressure` holds no
fields; its schedule is derived, not stored.

**Session shape.** [#23](https://github.com/cjd721/Rimworld-Archinity/issues/23) resolved to
**shared: one player faction, one colony, Async Time on**. The per-colony instancing concerns that
the earlier two-colony comments handed this ticket are therefore moot for the base case and become
live only when the gravship creates a second map.

**What Multiplayer does to the storyteller**, verified against `Multiplayer.dll` 1.6 under
`AssembliesCustom/` (**T-22** — confirm the copy you read):

- `Multiplayer.Client.AsyncTime.StorytellerTickPatch.TargetMethods` yields **both**
  `Storyteller.StorytellerTick` and `StoryWatcher.StoryWatcherTick`; its prefix returns
  `Multiplayer.Ticking` [V].
- `Multiplayer.Client.StoryWatcherTickPatch` is a `FactionRepeater` prefix that returns false and
  redirects into each `FactionWorldData.storyWatcher`, with a re-entrancy flag [V]. With one player
  faction it resolves to `Find.StoryWatcher` and there is one adaptation clock.
- `Multiplayer.Client.AsyncTime.StorytellerTargetsPatch` postfixes `Storyteller.AllIncidentTargets`
  with two branches: under a map context the list collapses to that map; during the world tick it
  becomes the player caravans plus `Find.World` [V]. **World-tagged incidents are a third pressure
  stream, scaled off `World.PlayerWealthForStoryteller`.**
- `Multiplayer.Client.AsyncTime.MapContextIncidentParms` prefixes `StorytellerUtility.DefaultParmsNow`
  and `MapContextIncidentExecute` prefixes `IncidentWorker.TryExecute`, pushing the target map's
  async-time RNG context around both [V]. **Points generated through `DefaultParmsNow` and incident
  execution therefore run in the right context; direct calls to `DefaultThreatPointsNow` do not**,
  which is the second reason §2's postfix must be `Rand`-free.
- **`IncidentQueue` carries no Multiplayer patch** [V] — absent from the assembly's type list.
  `IncidentQueue.IncidentQueueTick` runs outside the 1000-tick gate, every tick [V], so anything we
  put on the queue is evaluated against whichever clock is ticking. Prefer a comp or a quest part
  over the queue.
- **Every tunable ships as a `Def`, never a `ModSettings` field** — `docs/engine/determinism.md`
  § *Settings are part of the sync surface*.

**Do not enable VEF's `raidWarningRange`.** `StorytellerDefExtension.storytellerThreat.raidWarningRange`
makes `VanillaExpandedFramework_IncidentWorker_Raid_TryExecuteWorker_Patch` return false and queue
the raid on `StorytellerWatcher`, a `GameComponent`, which later calls
`incidentDef.Worker.TryExecute` from `GameComponentTick` [V]. That moves raid execution — and all
of its pawn generation — out of the storyteller tick and out of `MapContextIncidentExecute`'s
reach. Its async-time behaviour is unverified; treat the feature as off until someone verifies it.

## Failure and recovery

- **Points collapse to the floor.** If a term worker throws or a curve is misauthored, the postfix
  should return `vanillaResult` unchanged rather than zero. Wrap the composition, log once via
  `Log.ErrorOnce`, and keep playing on vanilla scaling — a quiet campaign is recoverable, a
  campaign that has silently become trivial is not noticed for weeks.
- **The eligible raid faction pool empties.** **T-17**: `GetRandomEligibleFaction()` returns null
  with no fallback and raids simply stop. Whenever the roster or a tech gate changes, check the
  pool. A startup validator that asserts at least one hostile faction is eligible at each era band
  is cheap and loud.
- **A beat's raid arrives at zero points.** **T-65** — the `forcedPointsRange` sentinel above. A startup
  validator over every `IncidentDef` whose `workerClass` is `IncidentWorker_RaidEnemySpecial`,
  asserting an explicit `forcedPointsRange`, converts a silent failure into a loud one.
- **The orbital act goes quiet.** **T-48**: on an orbit layer only 18 of 91 `IncidentDef`s and 18
  of 139 `QuestScriptDef`s are legal, and nothing reports the narrowing. Every def the campaign
  needs in orbit — **including ours** — needs `layerWhitelist` or `canOccurOnAllPlanetLayers`, and
  the count must be re-taken after every mod addition.
- **A comp insertion re-rolls the schedule.** **T-66**, §1. If cadence changes for no reason anyone
  authored, check whether the comp list or the active mod set moved.

## Status

**Evidence class: READ.** Settled against the 1.6 `Assembly-CSharp.dll`, `VEF.dll` 1.6,
`Multiplayer.dll` 1.6 and `NCL_Storyteller.dll` 1.6. Corpus-wide hit counts are **[I]** — a sweep
is a filename-and-string result, never a read. Established by
[#60](https://github.com/cjd721/Rimworld-Archinity/issues/60), against requirements settled on
[#9](https://github.com/cjd721/Rimworld-Archinity/issues/9).

**Verified available mechanisms** — every lever in *The build* is read out of a decompiled
assembly or a shipped def and is marked [V] where it is claimed.

**Selected:** nothing. This is a proposed design. The composition of verified mechanisms into the
intended campaign feel is **[I]** and stays [I] until something is built and played.

**Not ours:** the numbers. Every weight, curve point, threshold and cadence is **Balance**, fog on
[#2](https://github.com/cjd721/Rimworld-Archinity/issues/2).

## Available mechanisms

**The survey behind the build, including what does not exist.**

### Vanilla carries the three outputs, separately

`Storyteller` is a list of independent `StorytellerComp`s asked every 1000 ticks against every map,
every player caravan and `Find.World`; per-comp filtering is pure props (`minDaysPassed`,
`allowedTargetTags`, `disallowedTargetTags`); the incident's own worker holds the final veto through
`CanFireNow` [V]. Threat points are pulled on demand with no cached snapshot [V]. Twenty-three comp
classes ship, including `_Triggered` and `_SingleOnceFixed`, which fire on a condition or at a fixed
moment rather than on a timer [V].

### What does not exist in vanilla

- **No campaign-state input to threat points.** The four point curves are `private static readonly`
  and unreachable from XML [V]. **There are exactly two XML-reachable multipliers, and both are
  keyed on time**: `StorytellerDef.pointsFactorFromDaysPassed`, evaluated on
  `GenDate.DaysPassedSinceSettle` inside `DefaultThreatPointsNow`, and
  `StorytellerDef.pointsFactorFromAdaptDays`, which multiplies through
  `StoryWatcher_Adaptation.TotalThreatPointsFactor` [V]. Neither is keyed on era, capability,
  religion or diplomacy. This is why §2 is a postfix.
- **No hostile-side diplomacy term.** `StorytellerUtility.AllyIncidentFraction` exists and scales
  the *friendly* stream; there is no mirror that raises pressure with enemy count [V].
- **No frequency lever reachable from campaign state.** Accept fractions come from
  `StorytellerCompProperties` curves over days passed, threat points and progress score — never
  from arbitrary state [V]. This is why §3 adds a comp.
- **`fixedWealthMode` is disqualified.** It replaces wealth with a curve over **map** age [V], so a
  gravship relocation or a second colony restarts it at 10,000 — it zeroes itself precisely where
  the campaign needs it most. `Difficulty.Copy()` also resets `fixedWealthTimeFactor` while copying
  the flag. It stays off, and leaving it off avoids running two mechanisms for one job.

### VEF is the donor, twice

`VEF.dll` 1.6 absorbed Vanilla Storytellers Expanded (older version folders still ship
`VanillaStorytellersExpanded.dll`; 1.6 ships only `VEF.dll`) [V]. Two pieces are directly reusable:

- **`IncidentWorker_RaidEnemySpecial` + `IncidentDefExtension`** — an XML-authored raid with a
  forced faction, points range and strategy [V]. §4. Carries the sentinel defect noted there.
- **`StorytellerDefExtension.incidentSpawnOptions` + the `IncidentChanceFinal` postfix** — ally and
  enemy counts as selection weights, XML-configured [V]. §4. Carries only four directions, and not
  the one the requirement names.

Also present and **not** taken: `StorytellerCompProperties_IncidentSpawner` (a thinner
`FactionInteraction` with no accept fraction — our comp supersedes it) [V]; `raidWarningRange` (see
*Persistence and multiplayer*) [V]; `StorytellerThreat.disableThreatsAtPopulationCount` and
`allDamagesMultiplier` [V].

**Residual gap — `StorytellerDefExtension.storytellerThreat` was not surveyed as a whole.** The
three fields named above are the ones actually read; the rest of the extension, and
`raidRestlessness` in particular, was **not** examined. This survey is therefore incomplete over
VEF's storyteller extension, and a field there could duplicate or fight a lever §2–§4 builds. It is
a reading gap, not a negative: nothing below should be taken as "VEF offers nothing else".

### Wide pass

`DefaultThreatPointsNow` appears in 26 mods across both corpus roots; `PlayerWealthForStoryteller`
in 4; `StorytellerComp` in 12 plus VEF; `ChanceFactorNow` in 2; `IncidentCountThisInterval` in VEF
and VFE Deserters only. `StorytellerDef` appears in the XML of 13 mods.

**Nothing in the corpus composes threat strength from *campaign state*.** That negative survives a
tier-4 read and is the reason §2 owes a build. It is narrower than it first looked:

- **Mechanoids: Total Warfare** (`nyar.nclvstw`, workshop `3555799437`,
  `1.6/Assemblies/NCL_Storyteller.dll`) **does** compose — `NCL_Storyteller.Patch_StorytellerUtility`
  transpiles `DefaultThreatPointsNow`, injecting an additive term and replacing the hardcoded
  `10000f` ceiling [V]. So "the mods that touch the seam consume the number rather than compose it"
  is **false** and has been struck. What it injects is not campaign state in the sense this document
  means — it is that mod's own escalation counter, not era, capability, religion or diplomacy — so
  the headline negative holds while the generalisation about *how* the seam is touched does not.
  It is also the collision risk recorded in §2.

The nearest prior art for a rival scheduler is Rim War, which built a rival
generator and then had to blanket-block vanilla `RaidEnemy`, `RaidFriendly` and
`TraderCaravanArrival` to make room for it [I, from `scratch/recon-rimwar.md`] — the failure mode
this build exists to avoid, since adding a comp is additive.

## Verification

**What is verified:** every mechanism cited above, from the 1.6 `Assembly-CSharp.dll`, `VEF.dll`
1.6 (`.../294100/2023507013/1.6/Assemblies/VEF.dll`), `Multiplayer.dll` 1.6
(`.../294100/2606448745/1.6/AssembliesCustom/Multiplayer.dll`) and `NCL_Storyteller.dll`
(`.../294100/3555799437/1.6/Assemblies/NCL_Storyteller.dll`). Anchors are `Type.Method` and def
field names, never line numbers.

**What needs a prototype:** the composition. Whether the five terms produce a campaign that is hard
for two demigod founders is not a reading question.

**Observable checks that demonstrate the requirements are satisfied:**

1. **Bounded contribution.** With the dev storyteller panel open, note "Base points". Multiply
   colony wealth by ten with no other change; points must rise by well under an order of magnitude.
   The requirement's 10–20% is illustrative, but a near-linear response means the composition is
   wrong.
2. **Era ceiling.** Park an era. Points must climb and then flatten; they must not climb
   indefinitely, and they must not reset at the next `AdvanceEra()`.
3. **Low Reverence is not an exemption.** Zero the Reverence term and confirm a late-era,
   well-equipped colony still faces era-appropriate points.
4. **Independence.** Change only the Reverence term and confirm raid *cadence* is unchanged;
   change only the hostile-count term and confirm raid *size* is unchanged.
5. **No silent multiplication.** Raise Trace to maximum and confirm ordinary raids are unchanged in
   size — Trace must only move raids authored for the pursuit.
6. **Quality over quantity.** Raise `maxPawnCostPerTotalPointsCurve` on one band faction and
   confirm the same points produce fewer, more expensive pawns.
7. **Composition band.** Confirm `Storyteller.DebugLogTestFutureIncidents` over 100 days shows
   the intended mix — it prints incidents per def, per target and per comp [V].
8. **Spine immunity.** Fire an authored beat with a fixed hostile faction and confirm Ignorance Is
   Bliss did not substitute the faction ([#22](https://github.com/cjd721/Rimworld-Archinity/issues/22)
   §3 owns this check).
9. **Two clients.** Confirm no desync while the dev storyteller panel is open on one client and not
   the other — the direct-call path in §2.

## Outstanding decisions

- **The era clock has no spec owner.** [#7](https://github.com/cjd721/Rimworld-Archinity/issues/7)
  resolved that `AdvanceEra()` writes WTL's scribed `GameComponent_TechLevel` and stamps an
  era-start tick, but no document in `docs/specs/` owns that state and `docs/progression/` holds
  only a README. This build needs a read-only `int EraStartTick` and the current `TechLevel`. Until
  something owns it, the era term reads WTL's `WorldTechLevel.Current` for the era and derives
  era time from a stamp this spec does not define. **Raised on
  [#60](https://github.com/cjd721/Rimworld-Archinity/issues/60); the map
  ([#2](https://github.com/cjd721/Rimworld-Archinity/issues/2)) decides whether it earns a ticket.**
- **What "military capability" measures.** The requirement says *"practical broad indicators,
  potentially including research and wealth"* and *"research must establish useful measurements"*.
  Three are available and cheap (§2); which of them, and in what proportion, is Balance's.
- **Whether the point ceiling is raised above 10,000.** Reachable, not taken. Consumers assuming
  the vanilla clamp have not been enumerated.
- **Whether the stock storytellers stay in the list.** `listVisible` makes it a one-line decision
  either way; it is a design call, not a capability one.
- **Alliance effects have no owner.** `docs/requirements/PRESSURE.md` leaves the precise effect of
  alliances to be designed. The mechanism is in hand — `AllyIncidentFraction` for the friendly
  stream, the §4 postfix for the weight — but the direction and magnitude are not this document's,
  and **the ticket this was previously handed to,
  [#13](https://github.com/cjd721/Rimworld-Archinity/issues/13), is closed.** This is a stated gap,
  not a hand-back: nothing currently owns the political behaviour that would settle it.
- **[#77](https://github.com/cjd721/Rimworld-Archinity/issues/77)'s objectives.** `IncidentParms`
  carries `raidStrategy`, `raidArrivalMode`, `canSteal`, `canKidnap`, `canTimeoutOrFlee` and
  `attackTargets` [V] — the levers for *what a raid wants* rather than how big it is. Named here so
  #77 does not re-derive them; the choice is #77's.
