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
- **raid objectives** — what an arriving group is *trying to do*, as distinct from how big it is
  ([#77](https://github.com/cjd721/Rimworld-Archinity/issues/77), §8);
- **protecting the ordered spine** from storyteller RNG;
- the multiplayer constraints on all of the above.

It does not own: **Trace and the Glitterite pursuit**
([#56](https://github.com/cjd721/Rimworld-Archinity/issues/56)) — this document says how big a
pursuit raid is and how it is authored, #56 says what starts one and when; **the
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
| Era time | `Σ` over every boundary `e` in `GameComponent_Era.Boundaries` of `cappedCurve(ticks spent in e)` | each era's contribution is capped by the curve's last point; the sum is monotonic and never resets | [V] the boundary log is [`ERA.md`](ERA.md) § *The build* § 2 |
| Military capability | summed `CostApparent` of finished `ResearchProjectDef`s; free-colonist count; `map.wealthWatcher.WealthItems` | curve per indicator | [V] all three are public and already computed |
| Reverence | global Reverence derived from `WorldComponent_Reverence` | band curve | [V] [`RELIGION.md`](RELIGION.md) § *The build — Reverence* |
| Diplomacy | count of `Faction`s with `PlayerRelationKind == Hostile`, excluding `Hidden` and `temporary` — the mirror of `StorytellerUtility.AllyIncidentFraction` | curve, capped | [V] |

**The sum, not the current stamp, is what satisfies this document's own Verification check 2.**
A single `EraStartTick` resets at every boundary; `cappedCurve` over the retained log climbs
within an era, flattens at that era's ceiling, and **adds** at the seam — which is also #7 § 6's
*"no reset and no spike at a boundary."* [`ERA.md`](ERA.md) exists so this term has a
read-only source: `CurrentEra`, `CurrentEraStartTick`, `TicksInCurrentEra`,
`StartTickOf(TechLevel)` and `Boundaries`. **Note the unit change:** the term's ceiling is now
six era-caps rather than one, so each era's cap must be authored at roughly a sixth of what the
single-stamp reading implied. That factor is Balance's.

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

### 8. Raid objectives — what the arriving group wants

**Mechanism: one generic `RaidStrategyWorker` subclass driven by a `DefModExtension`, plus one
`RaidStrategyDef` per objective in XML.** No new `LordJob`. The objective is expressed by which
vanilla `LordJob` the worker builds and what it hands that job, and both of the jobs we need
already ship.

This is the answer to [#77](https://github.com/cjd721/Rimworld-Archinity/issues/77). It is scoped
to **objective only** — magnitude and composition stay in
[#9](https://github.com/cjd721/Rimworld-Archinity/issues/9) and §2/§4, incident selection stays in
§3/§4.

**Vanilla's whole objective vocabulary, read out of `Assembly-CSharp.dll`** [V]:

| Job | Reached by | What it does |
|---|---|---|
| `LordJob_AssaultColony` | `RaidStrategyWorker_ImmediateAttack.MakeLordJob` and every sapper/breach sibling | assault the colony; **opportunistically** branch to kidnap or steal |
| `LordJob_AssaultThings` | the same method, **when `parms.attackTargets` is non-empty** | assign `DutyDefOf.AssaultThing` at a randomly-chosen spawned target, re-picked every 300 ticks; leave when `Trigger_ThingsDamageTaken` fires — read its scoring carefully, below |

`LordJob_AssaultColony`'s constructor is
`(Faction, bool canKidnap = true, bool canTimeoutOrFlee = true, bool sappers = false, bool
useAvoidGridSmart = false, bool canSteal = true, bool breachers = false, bool
canPickUpOpportunisticWeapons = false)` [V]. Its `CreateGraph` attaches `LordJob_Kidnap` and
`LordJob_Steal` as **subgraphs off the assault toil**, entered on `Trigger_KidnapVictimPresent`
and `Trigger_HighValueThingsAround`, and only when `assaulterFaction.def.humanlikeFaction` [V].

**That is the finding the ticket is actually about: vanilla has no kidnap raid.** It has an
assault raid that kidnaps *if a colonist happens to go down*. Nine `RaidStrategyDef`s ship — three
`ImmediateAttack` variants, `StageThenAttack`, `EmergeFromWater`, `Siege`, `ImmediateAttackSappers`
and two breaching — and every one of them is "assault the colony", differing only in approach [V].
None of the five DLC adds one [V].

#### The three vehicles, and which objective goes on which

**(a) `attackTargets` — the "point the raid at the base" lever, and it is already in the engine.**
`IncidentParms.attackTargets` is a `List<Thing>`, `Scribe_Collections.Look(…, LookMode.Reference)`
with a `PostLoadInit` null-prune [V]. `RaidStrategyWorker_ImmediateAttack.MakeLordJob` checks it
*first*, before the hostility branch, and routes to `LordJob_AssaultThings` [V]. The duty it ends
in, `AssaultThing`, is `JobGiver_AIFightEnemies` → **`JobGiver_AITrashDutyFocus`** →
**`JobGiver_AISapper`** [V] — so the raiders fight what is in reach, wreck the focus, **and mine
through walls to get to it.** The founders standing in the doorway are not on the path.

> **Two silent no-ops sit on this path, and between them they kill the obvious build. This is the
> section's load-bearing warning.**
>
> **A factionless target is never attacked.** `JobGiver_AITrashDutyFocus.TryGiveJob` returns null
> unless `pawn.HostileTo(focus.Thing)`, and `GenHostility.HostileTo(Thing, Thing)` ends
> `if (a.Faction == null || b.Faction == null) return false;` [V]. **A stockpiled item and a sown
> crop have no `Faction`.**
>
> **An inert building is never attacked either.** `JobGiver_AITrashDutyFocus` calls
> `TrashUtility.TrashJob(pawn, focus.Thing, allowPunchingInert: false, killIncappedTarget: true)`,
> and `TrashJob` **returns null** for a `Building` whose `def.building.isInert` is true when
> `allowPunchingInert` is false [V]. `Wall` sets `isInert: true`, and so do `DoorBase`, `Fence` and
> `Column` (`Core/Defs/ThingDefs_Buildings/Buildings_Structure.xml`) [V]. `Shelf`, `ShelfSmall` and
> `Cooler` declare no `isInert` and are therefore valid [V].
>
> In either case the objective **silently no-ops**: the raiders path to the focus and issue no
> job, `Trigger_ThingsDamageTaken` never fires, and the group lingers. It is **not** a guaranteed
> hang — `LordJob.AddFleeToil` is `virtual => true` and `LordJob_AssaultThings` does not override
> it, so `Lord`'s graph builder attaches a `LordToil_PanicFlee` transition off **every** toil when
> `faction.def.autoFlee && !faction.neverFlee && Map.CanEverExit`, fired by
> `Trigger_FractionPawnsLost` [V]. So they leave once enough of them are downed. The group only
> lingers indefinitely for a **never-flee or non-auto-flee faction, or against a player who does
> not engage**. No error either way. That is **T-88**.

So:

- **Animal-killers** — `attackTargets` = colony animals. They are player-faction `Pawn`s, therefore
  hostile, therefore valid [V]. **But `damageFraction` does nothing for pawn targets.**
  `Trigger_ThingsDamageTaken.ActivateOn` counts only entries where `things[i].Spawned`; a dead
  animal is despawned and so leaves the numerator *and* the denominator, while every surviving
  spawned pawn scores `1f` [V]. The average is therefore always exactly `1`, and
  `num < 1f - damageFraction` is never true — the transition fires **solely** through the
  `num2 == 0` branch, i.e. the whole herd. The same bias applies to buildings: a destroyed shelf is
  excluded too, so the fraction only ever moves on *partial* damage to survivors. **A livestock
  objective on `LordJob_AssaultThings` terminates on total loss only.** A partial-herd objective —
  "kill four and go" — needs a `Trigger` of our own that counts the original list rather than the
  spawned one: about 25 lines, priced in the cost table.
- **Stores raids** — target the **storage buildings**, never the food and never the walls. Shelves
  and coolers are player-faction, non-inert `Building`s and yield a real `TrashJob` [V]; the
  freezer's walls are inert and are a no-op focus. The food is then taken by the ordinary
  `canSteal` branch or lost to deterioration. Free, given the right target set.
- **Fields** — vanilla already does some of this, opportunistically, and it is weaker than a field
  raid. `JobGiver_AITrashColonyClose` samples 35 random cells in a **5-cell** radius around the
  pawn and will `Ignite` a plant passing `TrashUtility.ShouldTrashPlant` — sown, non-tree,
  flammable, not raining, no static fire within two cells — but **only when
  `pawn.natives.IgniteVerb` is non-null and usable**, which excludes mechanoids [V]. That is
  passing damage to whatever a raider walks past, not an objective. A real field raid is **not**
  duplicated by it; it is also not reachable through `attackTargets`, because crops are
  factionless. If the campaign wants one, it is the custom-trigger build above with an `Ignite`
  duty — out of scope here, and named so it is not assumed free.

**(b) `canKidnap` / `canSteal` / `canTimeoutOrFlee` — and the negative that owes the code.**
These are `IncidentParms` fields, all three scribed with vanilla defaults `true` [V]. **There is no
XML path to `canKidnap` or `canSteal` anywhere in vanilla** [V]: `QuestNode_Raid` exposes
`canTimeoutOrFlee`, `arrivalMode`, `raidPawnKind` and the custom letter, and nothing else [V]; the
only vanilla XML occurrence of any of the three is `$canTimeoutOrFlee` in
`Scripts_Utility_ThreatsCore.xml` [V]. Forcing a **declared** kidnap raid — arrive intending to
take people, leave once they have — therefore needs a worker that hard-sets the flags. That is the
code this section owes, and it is small.

**(c) `RaidStrategyDef` — the era gate and the whole of Display.** Its full 1.6 field list is
`workerClass`, `selectionWeightPerPointsCurve`, `minPawns`, `selectionWeightCurvesPerFaction`,
`layerWhitelist`, `layerBlacklist`, `arrivalTextFriendly`, `arrivalTextEnemy`, `letterLabelEnemy`,
`letterLabelFriendly`, `pointsFactorCurve`, `pawnsCanBringFood`, `arriveModes`,
`raidLootValueFactor` [V] — **T-16 re-verified against the class, not inherited.**

#### The build

One `RaidStrategyWorker` subclass in `Archinity.Altar`, reading a `RaidObjectiveExtension :
DefModExtension` off its own `def`. `MakeLordJob` is `RaidStrategyWorker_ImmediateAttack`'s, with
two changes: the `attackTargets` list is **selected by us** from the extension's target class when
`parms.attackTargets` is empty, and the `LordJob_AssaultColony` flags come from the extension
rather than from `parms`. `CanUseWith` chains to `base` and adds the era gate.

**Prior art for exactly this shape, both read** [V]: `VREArchon.RaidStrategyWorker_ArchonRaid`
(`.../294100/3067715093/1.6/Assemblies/VREArchon.dll`) is `RaidStrategyWorker_ImmediateAttack`'s
`MakeLordJob` copied verbatim with the hostile branch swapped and `canKidnap` hard-set — about
fifteen lines. **Tribal Siege Raids** (`3697533935`, `TribalSiege_StrategyDef.xml`) is the XML
half: a third-party `RaidStrategyDef` with its own `workerClass`, its own `letterLabelEnemy`, a
points curve flat at zero below 2,000, and `arriveModes` cut to `EdgeWalkIn` alone.

**Correcting the ticket's stated guess.** #77 proposes *"animal-, field- and stockpile-targeting
variants likely need a custom `LordJob`, which is C#; the rest is `RaidStrategyDef` plus
`PawnsArrivalModeDef` in XML."* **It is inverted at both ends.** Animal-targeting needs no custom
`LordJob` — `LordJob_AssaultThings` is vanilla; field-targeting needs no raid machinery at all;
stockpile-targeting is not a `LordJob` problem but a *target-selection* problem, and the naive
target set fails silently as above. Meanwhile the half assumed to be free XML — kidnap and steal as
**declared** objectives — is the half with no XML path in the engine. The code we owe is a target
selector and a flag-setter, not a state graph.

#### Era gating without `minTechLevel`

**T-16 confirmed: `RaidStrategyDef` has no `minTechLevel`** [V]. Four substitutes, all verified,
in the order they should be reached for:

1. **`selectionWeightCurvesPerFaction`** — a `SimpleCurve` *per `FactionDef`*, consulted by
   `RaidStrategyWorker.SelectionWeightForFaction` ahead of the global curve; a weight of `0` makes
   `CanUseWith` return false [V]. Vanilla's `EmergeFromWater` is the idiom in pure form: base curve
   flat `(0, 0)`, Mechanoid curve non-zero, so the strategy exists **only** for one faction [V].
   Because the campaign's era progression is expressed as faction identity, this *is* the era gate.
2. **`selectionWeightPerPointsCurve`** — the points band, which is how vanilla actually gates its
   own escalation (§below). XML, free.
3. **`PawnKindDef.canBeSapper` / `isGoodBreacher` plus the faction's `pawnGroupMakers`** —
   `RaidStrategyWorker_WithRequiredPawnKinds.CanUseWith` refuses the strategy outright unless the
   faction's group makers expose a matching kind [V]. A Neolithic faction with no sapper kind can
   never draw a sapper raid at any points value. This is a **content** gate and the most robust of
   the four.
4. **`CanUseWith` in the worker we are writing anyway** — three lines reading the era clock
   ([`ERA.md`](ERA.md)'s `GameComponent_Era.CurrentEra`). Free, because the worker exists for other
   reasons.

**`PawnsArrivalModeDef` *does* carry `minTechLevel`, and it is used** — `Industrial` on `EdgeDrop`,
`EdgeDropGroups`, `CenterDrop`, `RandomDrop` and `SpecificDropDebug`, compared against
`parms.faction.def.techLevel` in `PawnsArrivalModeWorker.CanUseWith` [V]. So the half of the pair
the ticket pairs with `RaidStrategyDef` is already era-gated for free, and `FactionDef` adds
`arrivalModeWhitelist` / `arrivalModeBlacklist` on top [V]. **The tech gate vanilla ships governs
how a raid arrives, never what it wants.**

#### The VFE Empire blacklist — which escape, and a second finding

**T-14 re-verified against the assembly the game loads**,
`.../294100/2938820380/1.6/Assemblies/VFEEmpire.dll`. `VFEEmpire.RaidStrategyWorker_Deserters` is
`[StaticConstructorOnStartup]`; its static constructor null-initialises
`VFEE_DefOf.VFEE_Deserters.disallowedRaidStrategies` and then
`AddRange(DefDatabase<RaidStrategyDef>.AllDefs.Except(VFEE_DefOf.DesertersStrat))` [V]. The field is
vanilla's own `FactionDef.disallowedRaidStrategies`, consumed on the first line of
`RaidStrategyWorker.CanUseWith` [V]. Defs load before `[StaticConstructorOnStartup]`, so a strategy
we author is in the list. T-14 is correct; its wording *"sets `disallowedRaidStrategies =`"* is
`AddRange` onto a freshly-nulled list, which is the same outcome.

**Take escape 2 — pre-set `parms.raidStrategy`.** `IncidentWorker_RaidEnemy.ResolveRaidStrategy`
enters its selection block only `if (parms.raidStrategy == null)`, and the whole `CanUseStrategy`
filter — `disallowedRaidStrategies` included — lives inside that block [V]. §4 already selects the
carrier that does this in XML: VEF's `IncidentWorker_RaidEnemySpecial` reading
`IncidentDefExtension.forcedStrategy`. **Escape 1 — a `workerClass` whose `CanUseWith` does not
chain to `base` — is available and is not recommended**, because base `CanUseWith` is also where
`layerBlacklist`, `layerWhitelist`, `MinimumPoints` and the tile-mutator blacklist are enforced
[V]; dropping it to dodge one list silently drops the orbital-layer gate as well, straight into
**T-48**.

> **A second constraint on the Schism that T-14 does not record.**
> `RaidStrategyWorker_Deserters.CanUseWith` returns false unless a pawn holding an Empire royal
> title is spawned on the map [V]. `IncidentWorker_RaidEnemy.FactionCanBeGroupSource` rejects a
> faction outright when no `RaidStrategyDef` passes `CanUseWith` [V]. Together: with every other
> strategy blacklisted and `DesertersStrat` gated on a titled pawn, **the `VFEE_Deserters` faction
> cannot produce a storyteller raid at all unless a titled pawn is present.** For the Schism,
> authored raids are therefore not a compromise — they are the only route, which is a second and
> independent reason to take escape 2. That is **T-91**, a companion to T-14 rather than a
> replacement for it — T-14 stands as written.

#### Display — and it is free

The player must be able to read the objective off the arrival letter. Vanilla already carries it
[V]:

- `IncidentWorker_RaidEnemy.GetLetterLabel` returns `parms.raidStrategy.letterLabelEnemy + ": " +
  parms.faction.Name`.
- `GetLetterText` returns `parms.raidArrivalMode.textEnemy` formatted, then `\n\n`, then
  `parms.raidStrategy.arrivalTextEnemy`, then the leader and age-restriction lines.

Both fields are `[MustTranslate]` strings on `RaidStrategyDef` [V]. **A `RaidStrategyDef` we author
gets its own letter title and its own body paragraph with zero code.** Every vanilla strategy spends
`letterLabelEnemy` on the word `"Raid"` and differentiates only in the body — `Siege` is the one
exception, and Tribal Siege Raids takes the same liberty [V]. We should use the title: *"Slave
raid"*, *"Livestock raid"*, *"Stores raid"*. The arrival letter is `LetterDefOf.ThreatBig`, which
pauses via `SignalForceNormalSpeedShort` [V] — the player reads it before the group closes.

**The one thing Display does not cover, stated rather than hidden:** the *opportunistic* kidnap and
steal branches announce themselves only when they trigger, through
`TransitionAction_Message("MessageRaidersKidnapping" / "MessageRaidersStealing")` [V] — mid-raid,
after a colonist is already down. That is late by construction and we are not fixing it; it is the
reason the objectives above are declared up front on a strategy instead of left to vanilla's
triggers.

#### State, persistence and change

**State: none of ours.** Every field the objective rides on is vanilla's and already scribed —
`raidStrategy` and `raidArrivalMode` by `Scribe_Defs`, `canKidnap` / `canSteal` /
`canTimeoutOrFlee` by `Scribe_Values` at their `true` defaults, `attackTargets` by
`Scribe_Collections` with `LookMode.Reference` and a `PostLoadInit` prune of nulls [V].
`LordJob_AssaultThings.ExposeData` scribes `assaulterFaction`, `things`, `damageFraction` and
`useAvoidGridSmart` [V]. **Added to a save that predates it, this scribes nothing and migrates
nothing**; a raid already in flight keeps the lord it was created with, and the next raid can draw
the new strategies. The only new saved thing is the `DefModExtension`, which is def data, not save
data.

**Change:** `MakeLordJob`, called once per pawn group from `RaidStrategyWorker.MakeLords`, itself
called from `IncidentWorker_Raid.TryGenerateRaidInfo` inside `IncidentWorker.TryExecute` [V]. That
is the only write, it happens once, and there is no per-tick term.

**Multiplayer.** Target selection draws from the shared `Rand` stream and must therefore stay on
the synced path — it does. `Multiplayer.Client.AsyncTime.MapContextIncidentExecute` prefixes
`IncidentWorker.TryExecute` and pushes the target map's async-time RNG context around the whole
call [V, §*Persistence and multiplayer*], so `MakeLordJob` runs in the right context on both
clients. Two constraints follow and they are hard: **the selector must not read
`Find.CurrentMap`, selection, `Prefs` or any `ModSettings`** — it takes `parms.target` as the map
and its parameters from the `DefModExtension` — and **it must not be reachable from a draw path**,
which `MakeLordJob` is not. Vanilla's own `LordToil_AssaultThings.UpdateAllDuties` re-picks its
focus with `TryRandomElement` every 300 ticks [V]; that is a lord-toil tick, already synced, and
already shipped.

#### Which objectives, and what is not ours

The behaviours the playtest correction named — *"the stockpile, the animals, the fields and the
colonists"* — are all expressible, and the survey above says at what price. **Which of them the
campaign actually authors, at which era, and with what weights is not a capability answer.**
`docs/requirements/PRESSURE.md` § *Difficulty contributors* requires only that *"enemy quality,
equipment, composition and numbers produce an appropriate challenge"* and never names an
objective; it lists #77 under *Open questions*. That is the gap, and it is handed back there.

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
| **§8** `RaidObjectiveExtension : DefModExtension` (target class, lord flags, era band) | C# Def class | ~35 |
| **§8** `RaidStrategyWorker_Objective` — `MakeLordJob` + target selector + `CanUseWith` era gate | C# | ~110 |
| **§8** one `RaidStrategyDef` per objective, with `letterLabelEnemy` and `arrivalTextEnemy` | XML | ~35 each |
| **§8** startup validator: every `RaidStrategyDef` of ours has a non-empty `arriveModes`, and every `attackTargets` selector returns only **faction-owned, non-inert** Things | C# | ~30 |
| **§8** `Trigger_ThingsLost` — our own trigger, scoring against the *original* list, for any partial-loss objective | C# | ~25 |

**~545 lines of C# in the assembly we already ship, ~590 lines of XML, no new assembly, no
recompiled third-party DLL.** §8 adds no new `LordJob` and no new saved state.

## Hostility-scaled pressure — a faction acts on how much it hates you

**Scope.** This section answers
[`docs/requirements/TERRITORY.md`](../requirements/TERRITORY.md) § *Hostility must cost the colony
something* and [#169](https://github.com/cjd721/Rimworld-Archinity/issues/169): by what routes a
faction that hates the colony attacks it **more often and more heavily** than one that merely
dislikes it, and what else hostility can be made to do. Everything above this heading is the
**global** storyteller — faction-free by construction. This section is the **per-faction** half, and
the two are deliberately disjoint code paths.

It does not own **what raises hostility** ([`TERRITORY.md`](TERRITORY.md),
[#35](https://github.com/cjd721/Rimworld-Archinity/issues/35),
[#172](https://github.com/cjd721/Rimworld-Archinity/issues/172)), **what the arriving group is
trying to do** (§8, [#77](https://github.com/cjd721/Rimworld-Archinity/issues/77)), **what a refused
demand fires** ([`POLITICS.md`](POLITICS.md), [#91](https://github.com/cjd721/Rimworld-Archinity/issues/91)),
or **the Glitterite pursuit** ([`TRACE.md`](TRACE.md),
[#56](https://github.com/cjd721/Rimworld-Archinity/issues/56)).

### Verdict

- **Possible? Yes, by composition — but not inside goodwill.** Raid **size**, raid **frequency**,
  **which faction is drawn**, the **strategy** it arrives with, and **non-raid actions** are all
  reachable per faction. What is not reachable is a hatred that keeps growing inside the goodwill
  number: every vanilla writer clamps it to `[-100, 100]` [V], and nothing in vanilla reads goodwill
  as a *magnitude* on the hostile side at all [V].
- **Multiplayer? Yes** for routes A–D and F–G. **With work** for E, and the work is ordinary
  `WorldComponent` scribing plus keeping the read path `Rand`-free — not new sync surface.
- **And none of it is theoretical.** Two mods in the corpus already do most of this: **RimPacts**
  scales raid points from a per-faction `trust` record and filters the raid draw by treaty, and
  **VFE Deserters** drives raid frequency from a stored campaign number through vanilla's own
  scheduler [V, both decompiled]. See *Corpus donors*. The routes below are things to copy.

**The crux.** Vanilla decides raid points **before** it decides who is raiding.
`StorytellerUtility.DefaultThreatPointsNow(IIncidentTarget)` takes no faction [V] and
`IncidentWorker_RaidEnemy.ResolveRaidPoints` `Log.Error`s if points were not already set [V]; the
faction is resolved afterwards, in `IncidentWorker_Raid.TryGenerateRaidInfo`, in the order
`ResolveRaidPoints → TryResolveRaidFaction → ResolveRaidStrategy → … → AdjustedRaidPoints` [V].
**`IncidentWorker_Raid.AdjustedRaidPoints` is `public static`, receives the resolved `Faction`, and
is the last thing that touches points before pawn generation** [V]. That one fact is what makes
per-faction strength expressible at all.

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **A** | Raid **size** scales with how much *this* faction hates you | our postfix on `IncidentWorker_RaidEnemy.TryResolveRaidFaction` or on `IncidentWorker_Raid.AdjustedRaidPoints`; **RimPacts ships a working one** | C# | Medium | Yes |
| **B** | Raid **frequency** per faction — a named enemy on its own cadence | our `StorytellerComp` emitting `RaidEnemy` with `parms.faction` pre-set; **VFE Deserters ships the shape** | C# | Medium | Yes |
| **C** | A **declared-war state**, started and ended by signal, saved by vanilla | `QuestNode_GenerateThreats` → `QuestPart_ThreatsGenerator` | XML | Easy | Yes |
| **D** | Hostility **generated by the world**, with vanilla's letter and faction-card reason, no new state — via `GetMaxGoodwill`, which is immediate; **not** via the natural-goodwill drift, which is 10 points per 50 in-game days | our `GoodwillSituationWorker` + one `GoodwillSituationDef` | C# (tiny) + XML | Easy | Yes |
| **E** | A **named per-faction magnitude** past −100 — escalates, decays, or accumulates and is *spent* | TERRITORY's own store, or our `WorldComponent` | C# | Medium | With work |
| **F** | **Actions other than raids** — sieges, caravan demands, ambushes, refusal of trade | vanilla `IncidentDef`s + `RaidStrategyDef.selectionWeightCurvesPerFaction` | XML | Easy | Yes |
| **G** | **Which faction is drawn** for an ordinary storyteller raid | our postfix on `FactionDef.RaidCommonalityFromPoints` | C# | Medium | Yes |

**Recommended, not selected: D (cap half) + A + C.** D makes the world produce the hostility without
inventing a number — **but only through `GetMaxGoodwill`**; its natural-goodwill drift is a
50-in-game-day tide and cannot carry a war (see the rate table under D). A spends the hostility on
the thing the player feels; C is pure XML, already shipped, and is how a *beat* — "they have
declared war on you" — is expressed rather than a simulation. **B and G are likely rather than
optional**, because the requirement names *frequency* first and A only changes size. E is for when
the −100 floor proves too coarse, and its cheapest form stores nothing.

**A warning against the obvious build.** The intuitive reading of D — *give the faction a negative
`naturalGoodwillOffset` per holding taken and let vanilla do the rest* — produces a system that
looks correct in code review and takes **roughly 400 in-game days** to make one faction hostile,
then stops at −80. Nothing reports it; the symptom is a campaign in which taking settlements
appears to cost nothing for a year. Build D on the cap.

#### A — size, after the faction is known

**Two seams, and the choice between them is not cosmetic.**

- **`IncidentWorker_RaidEnemy.TryResolveRaidFaction(IncidentParms)`** — a postfix gets the whole
  `IncidentParms`: faction, points, target and `forced`, all in one object. It runs **before**
  `ResolveRaidStrategy`, so the strategy's own point gates (`CanUseWith`,
  `selectionWeightPerPointsCurve`) see the *hostility-scaled* number — a hated faction becomes
  eligible for siege and breach that a merely-hostile one is not. The method is `protected override`,
  so the patch names it by string with an explicit `Type[]` argument list [V].
- **`IncidentWorker_Raid.AdjustedRaidPoints(...)`** — `public static`, receives the `Faction`
  directly, runs **after** strategy and arrival mode, and is the last touch before pawn generation
  [V]. It sees no `parms`, so it cannot check `forced`, and it floors at
  `raidStrategy.Worker.MinimumPoints(faction, groupKind) * 1.05f` [V] — a reduction below that floor
  is silently discarded.

**A shipped carrier proves the first seam works.** **RimPacts — Diplomacy Overhaul**
(`wowgag.rimpacts`, workshop `3762723122`, `Assemblies/RimPacts.dll`) ships
`RimPacts.Patch_RaidEnemy_TurmoilPoints`, a Harmony postfix on exactly that method, which multiplies
`parms.points` from a **per-faction** record: `×0.7` under turmoil, `×0.8` when the faction is weak,
`×1.3` during an independence war, then by world-war stage multipliers [V]. It early-outs on
`!__result`, `parms.forced` and a null faction [V] — **deliberately exempting authored and quest
raids**, which is the discipline §7 wants and is worth copying verbatim.

**What it gets us.** Two hostile factions at the same storyteller points send groups of different
sizes. Per-raid, no state of its own, and the only place in the pipeline where the faction and the
points coexist [V].

**What it cannot do.** Not frequency, not who is drawn, and **not loot**: `TryGenerateRaidInfo`
saves `float points = parms.points` *before* the call and hands that pre-adjustment value to
`GenerateRaidLoot` [V]. A heavier raid drops the same loot unless loot is scaled separately.

**Consequences.** `AdjustedRaidPoints` is on `IncidentWorker_RaidFriendly`'s path too — both extend
`IncidentWorker_Raid` [V] — so a postfix *there* must gate on `faction.HostileTo(Faction.OfPlayer)`
or it silently inflates allied relief parties. (The `TryResolveRaidFaction` seam does not have this
problem: `IncidentWorker_RaidFriendly` overrides it separately.) Either seam composes
**multiplicatively** with §2's global postfix,
which is where the requirement's *"bounded and combined without accidental runaway multiplication"*
clause bites; the two stay separable because one is global and faction-free and the other is
per-raid and faction-keyed. `QuestNode_GenerateThreats` also calls it to build a quest's **example
threat text** [V], so it runs outside a raid. And it floors at
`raidStrategy.Worker.MinimumPoints(faction, groupKind) * 1.05f` [V] — a reduction below that floor
is discarded.

#### B — frequency, in a comp of our own

`IncidentWorker_RaidEnemy.TryResolveRaidFaction` returns `true` immediately when `parms.faction` is
already set, hostile and not deactivated [V]. A comp that fills `parms.faction` therefore bypasses
the weighted draw entirely — no patch on the selection path is needed to make one faction raid.

The scheduler exists and is the safest in the game:
`IncidentCycleUtility.IncidentCountThisInterval(IIncidentTarget, int randSeedSalt, float minDaysPassed,
float onDays, float offDays, float minSpacingDays, float minIncidents, float maxIncidents, float acceptFraction = 1f)`
is `public static` and seeds `Rand` from `Gen.HashCombineInt(Find.World.info.persistentRandomValue,
target.ConstantRandSeed, randSeedSalt, i)` [V] — a pure function that draws nothing from the shared
stream. §3's `StorytellerComp_Pressure` is already this shape for the *global* hostile cadence; the
per-faction version is the same class with the faction written into the parms.

**Consequences.** **T-66** in full: a comp's list index is the `randSeedSalt` [V]. One comp that
**iterates** the hostile factions, not one comp per faction — otherwise the salt moves whenever the
roster does.

#### C — a declared war, as a quest part, in XML

**This route already ships.** `RimWorld.QuestGen.QuestNode_GenerateThreats` is an ordinary XML quest
node carrying `<parms>` (a `ThreatsGeneratorParams`), an optional `SlateRef<Faction> faction`,
`inSignalEnable`, `inSignalDisable` and `threatStartTicks` [V]. It builds
`QuestPart_ThreatsGenerator : QuestPartActivable, IIncidentMakerQuestPart`, whose
`MakeIntervalIncidents` is walked by `Storyteller.MakeIncidentsForInterval` on the same 1000-tick
interval as every comp — for every quest whose `State` is `Ongoing` and whose part is `Enabled` [V].

`ThreatsGeneratorParams` is the whole vocabulary of a war, `IExposable` and `Scribe_Deep`'d by the
quest part [V]:

| Field | What it controls |
|---|---|
| `faction` | **who** — a `Scribe_References` live `Faction`, written into every raid's parms |
| `onDays` · `offDays` · `minSpacingDays` · `numIncidentsRange` | **how often**, with quiet stretches |
| `currentThreatPointsFactor` | **how big**, as a multiplier on `DefaultThreatPointsNow` |
| `threatPoints` · `minThreatPoints` | a fixed size, or a floor |
| `allowedThreats` | `Raids` and `MechClusters`, and nothing else [V] |

Vanilla's own donor is Royalty's `Script_EndGame_RoyalAscent.xml`: `onDays 1.0`, `offDays 0.5`,
`minSpacingDays 0.04`, `numIncidentsRange 1~2`, `currentThreatPointsFactor 1.4`,
`minThreatPoints 500`, for the duration of the ascent [V].

**What it gets us.** A war becomes *a state a quest is in* — it starts on a signal, ends on a
signal, appears in the quests tab, survives save/load with none of our code, and carries its own
cadence and magnitude. Per-faction saved state, scribed by vanilla.

**What it cannot do.** Two threat kinds only [V]. The target must be a `MapParent` with a map [V],
so it never presses on caravans or the world. `TestRunInt` returns false when
`difficulty.allowViolentQuests` is off or the slate has no `map` [V]. And the quest must stay
`Ongoing` for the part to be walked at all [V].

> **Consequence that is easy to miss.** `ThreatsGenerator.GetIncidentParms` sets
> `incidentParms.forced = true` [V], and `IncidentWorker.CanFireNow` skips its **entire** def-level
> gate block when `parms.forced` — `min`/`maxThreatPoints`, `earliestDay`, `disabledWhen`,
> `allowBigThreats`, biomes, `layerWhitelist`/`layerBlacklist`, `ScenPart_DisableIncident`,
> `minPopulation`, `FiredTooRecently`, **the `GameCondition.preventIncidents` quiet window**, and the
> game-ender guards, leaving only `CanFireNowSub` [V]. A declared war therefore **fires straight
> through §7.2's beat protection and through T-48's planet-layer narrowing.** Disable the quest part
> around an authored beat, or accept the collision.

#### D — hostility the world generates, through vanilla's own machinery

`GoodwillSituationDef` is a plain `Def` whose `workerClass` is instantiated reflectively [V].
`GoodwillSituationManager.RecalculateAll` runs every 1000 ticks over every non-player faction with
`HasGoodwill`, asking each def's worker for **two** numbers — `GetMaxGoodwill(other)` and
`GetNaturalGoodwillOffset(other)` — and caching the pair [V]. **The two behave completely
differently, and the difference decides what this route is worth.**

| Half | How it reaches goodwill | Rate |
|---|---|---|
| `GetMaxGoodwill` — a **cap** | `Faction.GoodwillWith` applies `Mathf.Min(baseGoodwill, GetMaxGoodwill(…))` **on every read** [V] | **immediate** — live within the 1000-tick recache, which itself calls `CheckHostilityChanged` → `Notify_GoodwillSituationsChanged` [V] |
| `GetNaturalGoodwillOffset` — a **drift target** | summed into `Faction.NaturalGoodwill`, chased by `Faction.CheckReachNaturalGoodwill` | **10 goodwill per 3,000,000 ticks ≈ 50 in-game days**, and it stops at `natural + 50` [V] |

**The drift rate, read exactly** [V]. `CheckReachNaturalGoodwill` is called from `FactionTick`, but
it returns immediately — resetting `naturalGoodwillTimer` to 0 — whenever base goodwill is *inside*
`[NaturalGoodwill − 50, NaturalGoodwill + 50]`. Outside the band it increments the timer and fires
one step only at `naturalGoodwillTimer >= 3000000`, of magnitude
`Mathf.Min(10, distance to the band edge)`, then resets the timer. So: **one step of at most 10 per
50 in-game days, and the drift halts at the band edge, not at the natural value and not at the −100
clamp.** This matches `docs/engine/factions-and-worldgen.md` § *Alliance hysteresis*, which already
states the gate.

**The consequence for the donor this section cites.** `GoodwillSituationWorker_NaturalEnemy`'s flat
`-130` offset puts the band at `[-180, -80]`. A faction starting at neutral drifts down **10 per 50
days and stops at −80** — eight steps, roughly **400 in-game days**, ending five points past the
−75 hostile threshold and nowhere near −100 [V]. Drift is a background tide, not a war declaration.

**What it gets us, re-weighed.** A worker of ours that reads world state — how many of that
faction's settlements the colony holds — and returns a `GetMaxGoodwill` **cap** makes **vanilla
itself** make the faction hostile, within one recache, with vanilla's hostility letter, and with the
reason shown in the faction card through `GoodwillSituationManager.GetExplanation` [V].
`FactionRelation.CheckKindThresholds` compares `faction.GoodwillWith(other)` — the **capped** value
— so the cap really does flip the relation kind [V]. **No new saved state and no new sync surface**:
the cache is rebuilt from world state every 1000 ticks, and `Faction.naturalGoodwillTimer` is
already scribed [V]. The shipped donor is exact and is the *cap* one:
`GoodwillSituationWorker_AttackingSettlement` returns `GetMaxGoodwill` = `-80` while
`SettlementUtility.IsPlayerAttackingAnySettlementOf(other)` [V] — that is how vanilla makes
attacking a settlement hostile *now* rather than in a year.

**Use the offset for the slow half only**, where its rate is a feature: a grudge that cools over
seasons after the colony releases a holding, or a low tide of resentment that never quite reaches
war. The periodic donor for that shape is
`SettlementProximityGoodwillUtility.CheckSettlementProximityGoodwillChange`, which sums a
per-faction offset over the player's settlements every 900,000 ticks (**15 in-game days**), applies
it through `TryAffectGoodwillWith`, and sends **one** letter listing the causes [V] — and it already
skips a faction at `PlayerGoodwill == -100`, which is this ticket's own complaint demonstrated in
vanilla code. Note it is a *direct* `TryAffectGoodwillWith` call on a fixed schedule, not the
natural-goodwill drift, which is why it moves three times faster.

**What it cannot do.** It produces the *input*, never the *output*: goodwill below −75 changes
nothing in vanilla beyond eligibility, and it cannot pass −100 or distinguish "hates you" from
"hates you three times over". The cap and the drift also do not compose cleanly —
`CheckReachNaturalGoodwill` reads `BaseGoodwillWith` (**uncapped**) and the band from
`NaturalGoodwill`, so a cap changes what the player sees and what the relation kind is while the
base number underneath continues to drift on its own terms [V].

**Consequences.** Silently inert for a whole class of factions: `CheckReachNaturalGoodwill` returns
early for `def.permanentEnemy`; `CanChangeGoodwillFor` refuses every change for `permanentEnemy`,
`permanentEnemyToEveryoneExceptPlayer`, a `permanentEnemyToEveryoneExcept` list omitting the other
side, `defeated`, `temporary` and `Hidden`; `RecalculateAll` skips anything without `HasGoodwill`
[V]. Mechanoids and insects are out by construction, and so is anything the campaign marks a
permanent enemy.

> **Silent failure — a `GoodwillSituationDef` written in pure XML does nothing.** `workerClass`
> defaults to `typeof(GoodwillSituationWorker)`, whose `GetMaxGoodwill` returns a hardcoded `100`
> and whose `GetNaturalGoodwillOffset` returns a hardcoded `0` [V]. **No shipped worker reads
> `baseMaxGoodwill` at all** — `_PermanentEnemy`, `_NaturalEnemy` and `_AttackingSettlement` return
> constants, `_MemeCompatibility` and `_SameIdeo` read only `naturalGoodwillOffset` and are both
> gated on ideo membership [V]. A def authored without a `workerClass` loads cleanly, is walked
> every 1000 ticks, contributes nothing, and is not even listed in `GetExplanation`, because
> `Recalculate` records a situation only when `maxGoodwill < 100 || naturalGoodwillOffset != 0` [V].
> No error, no warning. Proposed for `docs/TRAPS.md` on
> [#169](https://github.com/cjd721/Rimworld-Archinity/issues/169); not yet assigned a T-ID.

#### E — a named per-faction magnitude past the floor

Needed the moment the campaign wants *"the fourth settlement you take costs more than the third"*.

**The cheap form stores nothing.** The magnitude the story wants is how many of the faction's
holdings the colony has taken, and that is world state [`TERRITORY.md`](TERRITORY.md) already owns.
Read it in A's or B's curve and there is no new scribing and no new sync surface. Whether that store
exposes a per-faction count is **[I]** here — it is a sibling document's answer, and this route's
weight depends on it.

**The expensive form** is a `WorldComponent` holding a per-faction value, ticked on the world tick,
spent and reset when the faction "arrives at the door". **RimPacts has already built it** — see
*Corpus donors* below for `TrustRecord` and its multiplayer caveat. Every part of it also has a
vanilla donor:
`Faction.naturalGoodwillTimer` is a scribed per-faction accumulator advanced in `FactionTick`,
reset on arrival and spent at a hardcoded 3,000,000-tick threshold [V] — the accumulate-and-spend
shape, in vanilla, at a rate chosen for background drift rather than for events;
`QuestPart_ThreatsGenerator.parms` is a scribed per-faction payload re-read every interval [V];
`StoryState.lastFireTicks` shows the dictionary-scribe shape [V]. Multiplayer cost is the ordinary
`WorldComponent` one ([`../engine/determinism.md`](../engine/determinism.md)) plus §2's standing
rule that the read path stays `Rand`-free.

**What only this route gets us:** escalation with no ceiling, decay so a war can cool, and the
accumulate-then-spend shape — the faction builds toward something and then it arrives, which is a
beat rather than a slider.

#### F — the actions that are not raids

All XML, all on shipped mechanisms:

- **Siege is already a vanilla `RaidStrategyDef`** (`Core/Defs/Storyteller/RaidStrategies_Siege.xml`)
  [V], and `RaidStrategyDef.selectionWeightCurvesPerFaction` is a `List<FactionCurve>` matched on
  `faction.def` inside `RaidStrategyWorker.SelectionWeightForFaction` [V] — a per-`FactionDef`
  strategy weight in XML, on a vanilla field; vanilla uses the sibling field on
  `PawnsArrivalModeDef` for mechanoid drop pods [V]. *"This faction besieges rather than charges"* is
  authorable without code. *"…because it hates you"* is not, because the curve's input is points.
- **Demands and ambushes against caravans ship.** `IncidentWorker_CaravanDemand` stops a caravan and
  demands 5–20% of it on pain of attack; `IncidentWorker_Ambush_EnemyFaction` attacks it outright
  [V]. Both draw their faction through `PawnGroupMakerUtility.TryGetRandomFactionForCombatPawnGroup`
  — the **unweighted** variant, with no last-raider penalty [V] — so route G reaches them too.
- **Refusal of trade is already automatic, and already total.**
  `IncidentWorker_NeutralGroup.FactionCanBeGroupSource` rejects any `Hidden` or
  `HostileTo(Faction.OfPlayer)` faction [V], which removes that faction's traders, visitors and
  travellers the moment goodwill crosses −75; `StorytellerUtility.AllyIncidentFraction` then scales
  the whole friendly stream by the **count** of non-hostile factions [V]. Hatred cannot make this
  worse.
- **Blockade and bounty have no vanilla carrier.** No type in `Assembly-CSharp.dll` 1.6 names either
  [V — zero hits for `blockade`, `bounty` and `embargo` over the full type list, validated against
  21 hits for `Siege` in the same list]. The nearest shipped shapes are the caravan ambush above and
  `IncidentWorker_RansomDemand`, which ransoms a kidnapped colonist *back* — the aftermath of a
  raid, not a bounty [V].

#### G — which faction the storyteller draws

`IncidentWorker_RaidEnemy.TryResolveRaidFaction` calls
`PawnGroupMakerUtility.TryGetRandomFactionForCombatPawnGroupWeighted`, whose weight is
`f.def.RaidCommonalityFromPoints(maxPoints) × (f == target.StoryState.lastRaidFaction ? 0.4f : 1f)`
[V]. That confirms [#120](https://github.com/cjd721/Rimworld-Archinity/issues/120)'s *"a raid-weight
increase has no XML lever"* **with one correction worth carrying**: there *is* an XML lever —
`FactionDef.raidCommonalityFromPointsCurve` — it is simply keyed on **points** and lives on the
**def**, so it cannot read goodwill and cannot separate two factions sharing a def [V].

**The patch target.** The weight is a lambda in a compiler-generated closure and has no name to
patch. The clean target is `RimWorld.FactionDef.RaidCommonalityFromPoints(float)`, a `public`
instance method [V]: a postfix gets the `FactionDef` as `__instance`. Two caveats, both [V]: it is
per **def**, not per faction instance; and it is called from *both* selection helpers, including the
unweighted one behind route F's caravan incidents — a feature if hostility should also steer who
ambushes your caravans, a surprise otherwise.

**The alternative is not to patch it.** Pre-setting `parms.faction` (routes B and C) makes the draw
moot [V], and is how vanilla itself directs a raid.

**A shipped carrier for this route too.** `RimPacts.Patch_TryGetRandomFactionForCombatPawnGroup` is
a Harmony **prefix** that takes `ref Predicate<Faction> validator` and wraps it — composing the
original predicate with its own treaty exclusions, so a faction under a non-aggression, passage or
tribute treaty is never drawn for a raid [V]. Wrapping the validator rather than the weight is the
cheaper half of this route: it is binary (drawn / not drawn) and cannot express *more likely*, but
it needs no reweighting and cannot go negative. **T-17 applies with full force** — excluding
factions this way is exactly how the pool empties silently.

### Corpus donors — this behaviour already ships, twice

**The headline negative does not survive the wide pass, and that is the most useful thing this
section found.** Two mods in the corpus already do most of what the ticket asks, by different
routes, and both are readable donors rather than dependencies.

**RimPacts — Diplomacy Overhaul** (`wowgag.rimpacts`, workshop `3762723122`,
`Assemblies/RimPacts.dll`) is the closest existing model for the whole behaviour [V, decompiled]:

- `RimPacts.TrustRecord : IExposable` is a **per-faction record** held in a `WorldComponent`,
  carrying a `trust` int (default 30) alongside `embargoed` (trade refusal), `casusBelliUntilTick`
  (a declared-war window), `turmoilUntilTick`, `lastPlayerAggressionTick` and a stack of cooldown
  ticks. **One small scribed struct per faction gates trade, diplomacy, war and raid strength at
  once** — which is route E's expensive form, built.
- `Patch_RaidEnemy_TurmoilPoints` spends it on raid **points** (route A, above).
- `Patch_TryGetRandomFactionForCombatPawnGroup` spends it on faction **selection** (route G, above).
- `WorldComponent_RimPacts.playerNotoriety` is a **single global** scalar, not per-faction: it rises
  on razing and aggression, decays daily, and at a threshold forms an anti-player coalition [V].
  **The field this ticket was pointed at is therefore the aggregate half, and the per-faction half
  is `TrustRecord.trust`** — worth stating, because the name suggests otherwise.
- **Multiplayer: unsynced and uncovered.** MP Compat carries no `[MpCompatFor]` class for
  `wowgag.rimpacts`, and `RimPacts.dll` references no Multiplayer API [I, inherited from
  [#120](https://github.com/cjd721/Rimworld-Archinity/issues/120)'s sweeps]. A
  `Dictionary<Faction, …>` walked in a world tick is the shape #120 flagged for iteration-order
  desync. Copy the pattern, not the assembly.

**Vanilla Factions Expanded — Deserters** (`oskarpotocki.vfe.deserters`, workshop `3025493377`,
`1.6/Assemblies/VFED.dll`) ships **route B's exact shape** [V, decompiled]:
`VFED.StorytellerComp_ByVisibility` exposes `VisibilityFactor = Mathf.InverseLerp(0, 100,
WorldComponent_Deserters.Instance.Visibility)`, and
`VFED.StorytellerComp_FactionInteraction_ByVisibility.MakeIntervalIncidents` feeds it into vanilla's
scheduler **twice** — once multiplying `baseIncidentsPerYear` by `Mathf.Lerp(0f, 20f, factor)` and
once multiplying the accept fraction by `factor + 0.5f`, then calling
`IncidentCycleUtility.IncidentCountThisInterval` [V]. Four such comps ship
(`_OnOffCycle_`, `_CategoryMTB_`, `_CategoryIndividualMTBByBiome_`, `_FactionInteraction_`), each a
vanilla comp with one stored campaign number spliced into its rate [V]. **This is the proof that
route B is a copy rather than an invention**; the only change is reading a per-faction value instead
of one global one.

**Ruled out, with the reason.** **Rim War** (`torann.rimwar`) gates its warband attacks on vanilla
`FactionUtility.HostileTo` and feeds results back through `TryAffectGoodwillWith` — it rides
goodwill rather than storing a magnitude [V]. **VEF**'s
`StorytellerDefExtension.incidentSpawnOptions` scales threat chance by the **count** of hostile or
allied factions, capped 0.1–9 — an aggregate, not per-faction, and it does not carry the direction
the requirement names (§4). **VFE Empire**'s `HonorWorker_Faction` is a quest-reward flavour value,
not a threat input. **Sensible Factions** (`boots.sensiblefactions`) matched the raid-weight sweep
but decompiles to biome-based worldgen placement only. **Tribal Siege Raids** checks `HostileTo` as
a binary eligibility gate. **Faction Control**, **More Faction Interaction**, **Call of Cthulhu
Factions** and **Save Our Ship 2** are not present in the corpus at all.

**How the sweeps were run.** Both corpus roots plus `RimWorld/Data`, ripgrep with
`-a -i -g '*.dll' -g '!**/obj/**' -g '!**/Referenced/**'` for the `#Strings` half, and a second
null-interleaved pass with the `\x00` escapes typed literally into the pattern for the `#US` half
(`n\x00o\x00t\x00o\x00r\x00i\x00e\x00t\x00y\x00` and siblings), never built through `$(…)`. Terms:
notoriety, grudge, vendetta, animosity, hatred, hostility, war/declare-war/at-war, aggression,
vengeance, retaliation, reprisal, siege, blockade, bounty, raid/faction weight, raid frequency,
goodwill threshold, and the vanilla member names this section patches. The UTF-16 form was
validated against `Notoriety` → `RimPacts.dll` before any negative was trusted; attribution through
`python tools/corpus.py --which -`. **Every hit named above was decompiled; hits not decompiled are
not cited.** `corpus.py --check` at the start flagged four mods updated since the pin, none of them
cited here.

### Constraints on every route above

1. **Goodwill is clamped to `[-100, 100]` by every vanilla writer.** `Faction.TryAffectGoodwillWith`
   and `Faction.ChangeGoodwill_Debug` both `Mathf.Clamp` before assigning, and
   `FactionRelation.baseGoodwill` is written nowhere else in the assembly [V]. Thresholds are
   `const`s on `DiplomacyTuning`: hostile at −75, neutral back at 0, ally at 75 [V]. **A campaign
   magnitude cannot live in the goodwill number.**
2. **Nothing in vanilla reads goodwill as a hostile-side magnitude.** The only goodwill-keyed curve
   in the game is `DiplomacyTuning.VisitorGiftChanceFactorFromGoodwillCurve`, `(-30, 0) → (0, 1)`,
   on gifts from friendly visitors [V]. Everything else compares `FactionRelationKind` or calls
   `HostileTo` — both binary [V].
3. **Every goodwill magnitude in the game is a `const` or `static readonly` on `DiplomacyTuning`**
   [V]: attacked settlement −50, member killed −100, settlement proximity −30/−20/−10 per quadrum,
   and the rest. None is XML-reachable, so rebalancing what *raises* hostility is a patch, never a
   def edit.
4. **Natural-goodwill drift is far slower than it looks, and it does not reach the floor.** The
   step is gated on `naturalGoodwillTimer >= 3000000` — **10 goodwill per ~50 in-game days** — and
   it halts at `NaturalGoodwill + 50` rather than at `NaturalGoodwill` or at −100 [V]. Any route
   that expects the world to *become* hostile on a story-relevant timescale must use a
   `GetMaxGoodwill` cap or a direct `TryAffectGoodwillWith` call, not the drift. This is also
   `docs/engine/factions-and-worldgen.md` § *Alliance hysteresis*.
5. **`parms.forced` disables the whole def-level gate block** in `IncidentWorker.CanFireNow`,
   including the `preventIncidents` quiet window and the layer whitelist [V]. Route C sets it.
6. **T-17 stands.** Raid faction selection is fail-open and fail-quiet: any gate added to
   `FactionCanBeGroupSource`, or any weight driven to zero, can empty the pool and raids simply stop
   with no message.
7. **T-91 bounds the whole section.** Hostility that scales a faction which cannot be drawn scales
   nothing — `VFEE_Deserters` passes `FactionCanBeGroupSource` only while an Empire-titled pawn is
   on the map ([I] as inherited from #77).
8. **Multiplayer gives the *player* faction goodwill.**
   `Multiplayer.Client.Patches.PlayerFactionsHaveGoodwill` postfixes `Faction.HasGoodwill` to `true`
   for `IsPlayer`, and `GetMaxGoodwillPatch` / `GetNaturalGoodwillPatch` prefix
   `GoodwillSituationManager.GetMaxGoodwill` / `GetNaturalGoodwill` to **skip the original** for a
   player faction [V]. With [#23](https://github.com/cjd721/Rimworld-Archinity/issues/23)'s settled
   one-player-faction shape that is inert, but a `GoodwillSituationWorker` of ours must not assume
   the player faction is excluded from the walk, nor that a meaningful value comes back for it.

### What this section verified, corrected and inherited

**Re-verified inherited claims.**

- **#60 — `MapParent.PlayerWealthForStoryteller` does not exist. Confirmed [V].**
  `RimWorld.Planet.MapParent` is `MapParent : WorldObject, IThingHolder`, and the member name does
  not occur in its decompilation.
- **#60 — one postfix on `DefaultThreatPointsNow` composes bounded campaign terms. Confirmed [V],
  and insufficient for this section:** the method takes an `IIncidentTarget` and no faction, so it
  cannot express per-faction pressure. This section adds a second, disjoint seam rather than loading
  more onto §2's.
- **#93 — the numeric standing gate is in `FactionDialogMaker`, not in quests. Confirmed [V]:**
  the AI-persona-core request is disabled by `faction.PlayerGoodwill < 40` against
  `DiplomacyTuning.MinGoodwillToRequestAICoreQuest`, and the other numeric effects there
  (−15 trader, −30 orbital trader, −25 military aid) are `DiplomacyTuning` consts [V].
- **#120 — per-faction raid weight has no XML lever. Confirmed, with route G's correction [V].**
- **#9 — wealth scaling is replaced by bounded development and political inputs.** Unchanged: the
  per-faction term is bounded by its own curve and applies *after* the global composition, not
  inside it. That it composes correctly is **[I]**.

**Evidence class: READ.** 1.6 `Assembly-CSharp.dll` (`RimWorldWin64_Data/Managed/`), the shipped
Core and Royalty defs, `Multiplayer.dll` 1.6 (`.../294100/2606448745/1.6/AssembliesCustom/`),
`RimPacts.dll` (`.../294100/3762723122/Assemblies/`) and `VFED.dll`
(`.../294100/3025493377/1.6/Assemblies/`). Types read: `IncidentWorker_RaidEnemy`,
`IncidentWorker_RaidFriendly`,
`IncidentWorker_Raid`, `IncidentWorker`, `IncidentWorker_NeutralGroup`,
`IncidentWorker_CaravanDemand`, `IncidentWorker_Ambush_EnemyFaction`, `PawnGroupMakerUtility`,
`RaidStrategyWorker`, `StorytellerUtility`, `Storyteller`, `IncidentCycleUtility`,
`StorytellerComp_FactionInteraction`, `StorytellerComp_ThreatsGenerator`, `ThreatsGenerator`,
`ThreatsGeneratorParams`, `QuestPart_ThreatsGenerator`, `QuestGen.QuestNode_GenerateThreats`,
`StoryState`, `Faction`, `FactionRelation`, `FactionDef`, `DiplomacyTuning`,
`GoodwillSituationManager`, `GoodwillSituationDef`, `GoodwillSituationWorker` and its five
subclasses, `SettlementProximityGoodwillUtility`, `FactionDialogMaker`, `MapParent`;
`RimPacts.Patch_RaidEnemy_TurmoilPoints`, `RimPacts.Patch_TryGetRandomFactionForCombatPawnGroup`,
`RimPacts.TrustRecord`; `VFED.StorytellerComp_ByVisibility`,
`VFED.StorytellerComp_FactionInteraction_ByVisibility` and its properties class. Defs read:
`Core/Defs/Goodwill/GoodwillSituations_Misc.xml`, `Core/Defs/Storyteller/Storytellers.xml`,
`Core/Defs/Storyteller/RaidStrategies_Siege.xml`,
`Core/Defs/Misc/PawnsArrivalModeDefs/PawnsArrivalModes.xml`,
`Royalty/Defs/QuestScriptDefs/Hospitality/Script_EndGame_RoyalAscent.xml`.
**Routes A–G are [I] by construction** — each composes mechanisms that are individually [V], and
nothing has been built.

### Open questions for this section

- **Requirement gap — nobody owns whether hostility is legible.**
  `docs/requirements/TERRITORY.md` states the behaviour and deliberately leaves the mechanism open,
  which is right. What no requirements document states is whether the player can **see** how much a
  faction hates them, or whether hatred can be **bought back down**. Handed to the owning
  requirements ticket for `TERRITORY.md`.
- **Requirement coordination.** `docs/requirements/PRESSURE.md` § *Difficulty contributors* frames
  diplomacy as the **count** of enemy factions; the per-faction **degree** requirement lives only in
  `TERRITORY.md`. They are compatible — count and degree are separate terms — but a reader of
  PRESSURE.md alone would conclude the count is all there is.
- **Does TERRITORY's holdings store expose "settlements taken from faction F"?** Route E's cheap
  form depends on it; **[I]** here, and [`TERRITORY.md`](TERRITORY.md) owns the answer.
- **Build questions, unowned until a route is selected:** where the per-faction curve lives; whether
  the hostility factor is one curve or a band table; whether raid **loot** is scaled with the raid;
  whether a declared war suspends itself around a Chronicle beat, given `forced`'s gate bypass.

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
- **An objective raid does nothing and lingers.** **T-88**, §8. `attackTargets` populated with a **factionless**
  Thing (a stockpiled item, a crop) fails `JobGiver_AITrashDutyFocus`'s `pawn.HostileTo(focus.Thing)`
  gate, and an **inert** `Building` (`Wall`, `Fence`, `Column`, any door) makes
  `TrashUtility.TrashJob` return null because `JobGiver_AITrashDutyFocus` passes
  `allowPunchingInert: false` [V]. Either way no job is issued,
  `Trigger_ThingsDamageTaken` never fires, and the objective silently no-ops. `LordJob_AssaultThings`
  has no timeout of its own, so the group then **lingers until auto-flee** — `LordJob.AddFleeToil`
  defaults `true` and `Lord` attaches a `LordToil_PanicFlee` transition off every toil on
  `Trigger_FractionPawnsLost` when `faction.def.autoFlee && !faction.neverFlee && Map.CanEverExit`
  [V] — **and indefinitely if the faction never flees or the player does not engage.** The selector
  must return faction-owned, non-inert Things; the startup validator in the cost table is what makes
  this loud.
- **A partial-loss objective never completes.** **T-89**, §8. `Trigger_ThingsDamageTaken` skips unspawned
  entries, so a dead pawn leaves both sides of the average and the score is pinned at `1` [V]. Any
  objective phrased as "destroy a fraction" resolves only at total loss unless it uses our own
  trigger. Symptom: a livestock raid that will not leave until the last animal is dead.
- **An authored `RaidStrategyDef` is never selected.** **T-90**, §8.
  `IncidentWorker_RaidEnemy.ResolveRaidStrategy`'s
  local `CanUseStrategy` returns **false** when `parms.raidArrivalMode` is null and the def's
  `arriveModes` is null [V] — a strategy authored without `arriveModes` is silently unselectable by
  the storyteller forever. The sibling path is loud rather than silent for the same omission:
  `PawnsArrivalModeWorker.CanUseWith` dereferences `parms.raidStrategy.arriveModes` with no null
  guard [V], so a *pre-set* strategy missing the list throws instead — which is the path an
  authored raid takes. Both halves are
  [`docs/engine/storyteller-and-incidents.md`](../engine/storyteller-and-incidents.md)
  § *`arriveModes` is not optional, and the two paths fail differently*.
- **The Schism cannot raid.** **T-91**, §8. With VFE Empire's blacklist (**T-14**) and
  `RaidStrategyWorker_Deserters.CanUseWith`'s titled-pawn requirement both live, `VFEE_Deserters`
  passes `FactionCanBeGroupSource` only while an Empire-titled pawn is on the map [V]. If the
  Schism goes quiet, this is why, and it is **T-17**'s fail-open-and-fail-quiet shape again.

## Status

**Evidence class: READ.** Settled against the 1.6 `Assembly-CSharp.dll`, `VEF.dll` 1.6,
`Multiplayer.dll` 1.6, `NCL_Storyteller.dll` 1.6 and — for §8 — `VFEEmpire.dll` 1.6 and
`VREArchon.dll` 1.6. Corpus-wide hit counts are **[I]** — a sweep is a filename-and-string result,
never a read. Established by
[#60](https://github.com/cjd721/Rimworld-Archinity/issues/60), against requirements settled on
[#9](https://github.com/cjd721/Rimworld-Archinity/issues/9); §8 by
[#77](https://github.com/cjd721/Rimworld-Archinity/issues/77).

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

### Raid objectives — what vanilla already does, and what it does not

**The archived claim is settled, and it is half true.** `docs/archive/HANDOFF.md` flags
*"Raiders start bringing tools instead of torches"* as *"prose, not a mechanism — vanilla raid
composition does not respond to your walls"*, and asks whether wealth- and time-scaled sappers and
breachers already supply it.

- **"Does not respond to your walls" — correct** [V]. Nothing in the raid pipeline reads wall
  material, thickness or count. `RaidStrategyWorker.CanUseWith` and `SelectionWeightForFaction` see
  points, faction, tile mutators and planet layer, and nothing else.
- **"Wealth- and time-scaled sappers and breachers" — correct, and here are the numbers** [V].
  `ImmediateAttackSappers.selectionWeightPerPointsCurve` is `(700, 0) → (1000, 0.4)`;
  `BreachingBase`'s is `(700, 0) → (2000, 0.6)`, inherited by **both** breach strategies — vanilla's
  own comment notes that doubles it. Below 700 points neither can be drawn. On top of that,
  `RaidStrategyWorker_ImmediateAttackBreaching.MinRequiredPawnsForPoints` evaluates
  `MinGoodBreachersFromPointCurve` `(0,1) → (200,1) → (1000,3) → (4000,4)`.
- **But availability is a hard content gate, not a scaling one** [V]. Points only ever open a door
  that `RaidStrategyWorker_WithRequiredPawnKinds.CanUseWith` has already unlocked: it refuses the
  strategy unless the faction's `pawnGroupMakers` expose a `PawnKindDef` with `canBeSapper` or
  `isGoodBreacher`. A faction without one never breaches at 10,000 points.

So the escalation the claim describes is real, it is driven by **points and faction roster** rather
than by the player's construction, and it is the reason §8's era gate is built out of
`selectionWeightCurvesPerFaction` and pawn-kind flags rather than a tech field.

**What does not exist:**

- **No objective-bearing `RaidStrategyDef` in vanilla or any DLC.** Nine ship, all "assault the
  colony", differing in approach and pathing only [V]. `RaidStrategyDefOf` registers four.
- **No XML path to `canKidnap` or `canSteal`** [V]. Both are `IncidentParms` fields;
  `QuestNode_Raid` exposes `canTimeoutOrFlee` and not the other two; the only vanilla XML mention
  of any of the three is `$canTimeoutOrFlee` in `Scripts_Utility_ThreatsCore.xml`. This is the
  negative that makes §8 owe code.
- **No declared kidnap or steal objective anywhere.** Both are `LordJob_AssaultColony` subgraphs
  entered on a runtime trigger, and only for a `humanlikeFaction` [V].

**Corpus donors, read rather than grepped.** `VREArchon.RaidStrategyWorker_ArchonRaid`
(`3067715093/1.6/Assemblies/VREArchon.dll`) shows the C# shape — `MakeLordJob` copied from
`RaidStrategyWorker_ImmediateAttack`, `attackTargets` branch kept intact, hostile branch swapped for
its own job with `canKidnap` hard-set [V]. **Tribal Siege Raids** (`3697533935`,
`Defs/RaidStrategyDefs/TribalSiege_StrategyDef.xml`) shows the XML shape — a third-party
`RaidStrategyDef` with its own `workerClass` and its own `letterLabelEnemy` [V].
`VFEEmpire.RaidStrategyWorker_Deserters` shows a third: an objective expressed purely by returning
a different `LordJob` (`LordJob_KillRoyalty`) from `MakeLordJob` [V].

**Stated residual gap.** `RimPacts.LordJob_RptAssaultThings` — a `LordJob_AssaultThings` subclass
that overrides `AddFleeToil` to `false`, which is itself the evidence that the base class has one —
was **not** tier-4 read for its target set. Its callers are `Patch_RaidEnemy_*` pact machinery, so
it is almost certainly still colony-assault rather than a stockpile or herd objective, but that is
**[I]**, not read. If a donor for our target selector is wanted, it is the first thing to open.

### Wide pass

`DefaultThreatPointsNow` appears in 26 mods across both corpus roots; `PlayerWealthForStoryteller`
in 4; `StorytellerComp` in 12 plus VEF; `ChanceFactorNow` in 2; `IncidentCountThisInterval` in VEF
and VFE Deserters only. `StorytellerDef` appears in the XML of 13 mods.

**§8's sweeps**, over both corpus roots with `-a -i -g '*.dll' -g '!**/obj/**' -g '!**/Referenced/**'`,
validated against a known hit (`RaidStrategyWorker_Deserters` → the three `VFEEmpire.dll` copies)
before any negative was trusted. Nine mods ship a `RaidStrategyDef` in XML; sixteen carry a
`RaidStrategyWorker` in an assembly; `LordJob_AssaultThings` is carried by RimPacts, VFE Tribals,
VRE Archon and Mechanoids: Total Warfare; `canKidnap` by VRE Archon, Vehicle Framework, VFE Medieval
2 and Worksites Expanded. All of those are **[I]** metadata-heap hits except VRE Archon, VFE Empire
and Tribal Siege Raids, which were decompiled or read. **No mod in the corpus expresses a raid
objective against the stockpile, the herd or the fields** — the three that define an objective at
all define it against pawns (`LordJob_KillRoyalty`, `LordJob_ArchonRaid`).

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
10. **The objective is legible before contact.** §8. Fire each authored objective raid and read the
    letter: the title must name the objective, not the word "Raid", and the body's second paragraph
    must be that strategy's `arrivalTextEnemy`. This is a def check, not a code check.
11. **The herd raid ends, and on the right condition.** §8. Fire a livestock raid on stock
    `Trigger_ThingsDamageTaken` and confirm it ends **only** when the last targeted animal is dead —
    that is the predicted behaviour, not a defect, and confirming it is what justifies
    `Trigger_ThingsLost`. Then fire the same raid on our trigger with a partial fraction and confirm
    it leaves early.
12. **Both silent no-ops are reproduced once, deliberately.** §8. In a dev game, point
    `attackTargets` at (a) a factionless stockpiled item and (b) a `Wall`, and confirm in each case
    that no trash job is issued, nothing is logged, and the group leaves only via auto-flee or not
    at all. Then confirm the startup validator rejects both selectors. This is the check that proves
    the traps are real rather than reasoned.
13. **The Schism can still raid.** §8. With VFE Empire loaded, confirm an authored Deserters raid
    using a pre-set strategy fires with **no** Empire-titled pawn on the map — the case where
    `FactionCanBeGroupSource` rejects the faction for the storyteller's own raids.
14. **Two clients, objective raids.** Confirm the same targets are chosen on both clients — the
    selector draws from the shared `Rand` stream inside `MakeLordJob`.

## Outstanding decisions

- **The era clock is owned.** [`ERA.md`](ERA.md)
  ([#109](https://github.com/cjd721/Rimworld-Archinity/issues/109)) holds `GameComponent_Era` and
  the boundary log, and states the read contract this document's era term uses. Note the
  correction it carries: **`AdvanceEra()` did not exist** when this document was written — #7
  designed it and nothing built it.
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
- **Which objectives the campaign authors.** §8 settles what is *expressible* and at what price.
  Which objectives exist, at which era, against which faction, and with what `damageFraction` and
  selection weights is a **requirement**, and `docs/requirements/PRESSURE.md` does not state one —
  it lists #77 under *Open questions* and its *Difficulty contributors* section names quality,
  equipment, composition and numbers but never an objective. Handed back to that document; the
  numbers are Balance's, fog on [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2).
- **Whether the opportunistic kidnap and steal branches stay on for ordinary raids.** §8 declares
  objectives up front on authored strategies; vanilla's `Trigger_KidnapVictimPresent` and
  `Trigger_HighValueThingsAround` branches remain live on every other raid unless a worker turns
  them off [V]. Leaving both on is the default and costs nothing; turning them off is a design
  call, not a capability one.
