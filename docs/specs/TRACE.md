# Trace and the Glitterite pursuit

## Purpose and scope

> **Authority correction — 2026-09-13.** Destructive Glitterite artifact analysis and
> repeated raids are first-class Trace inputs alongside serious network intrusion.
> Glitterites themselves are never hack targets, so android-target hacking contributes
> nothing. Other androids are not Glitterites by definition.

Implements [`docs/requirements/GLITTERTECH.md`](../requirements/GLITTERTECH.md)
§ *Trace — The Glitterites Learn You Back* and
[`docs/requirements/PRESSURE.md`](../requirements/PRESSURE.md) § *Glitterite pursuit*
(rules 1–7). Established by
[#56](https://github.com/cjd721/Rimworld-Archinity/issues/56).

**This document owns** the Trace number, its bands, what raises and decays it, the
search-progress meter that runs beside it, the relocation rule that resets search,
the pursuit quest, and every surface on which the player reads any of the above.

**Adjacent systems take over at five boundaries.**

| | |
|---|---|
| **What a hack reports** | [`HACKING.md`](HACKING.md) § *The intrusion report*. It emits every intrusion, including `Local` ones, flagged; the function from report to Trace increment is here. |
| **How big a raid is, and how it is authored** | [`PRESSURE.md`](PRESSURE.md). It says how threat strength is composed; this document says what starts a pursuit raid and when. **Trace never enters `DefaultThreatPointsNow`** — see § *Why Trace cannot multiply with Reverence*. |
| **The balance that pays for a Trace-reducing quest** | [`CURRENCIES.md`](CURRENCIES.md). Trace is a band ladder, not a balance, and lives in its own component. |
| **The shop window the readout sits in** | [`CURRENCIES.md`](CURRENCIES.md) § *Where the player sees it*, D1. This document adds one header row to a window that document already builds. |
| **Cross-cutting political-UI layout** | [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61). This number's readout is here. |

**Why this is its own document.** Trace spans three specs — its input is hacking, its
output is the storyteller, its readout is the currency window — and none of the three
can own it without reaching into the other two. `HACKING.md` says so explicitly:
*"[#56] owns the number, its bands, its decay and how a hack moves it. This document
owns only the emission."* It is a subsystem, not a hook, and
[`docs/specs/README.md`](README.md) § *Organize by system* is the rule it is filed under.

---

## The build

**Nothing carries this and we build it — but almost every piece is a shipped
mechanism with one part replaced.** The band ladder is `VFED.VisibilityLevelDef`'s
architecture rebuilt Def-for-Def without the VFE dependency; the pursuit is a vanilla
quest assembled from `QuestPartActivable`, `QuestPart_RandomRaid` and
`QuestPart_ThreatsGenerator`; the relocation test is one postfix on a `public static`
vanilla method that receives both tiles. **The only genuinely new logic is the search
accumulator and the function from an intrusion to a Trace increment.**

Everything lands in the single assembly we already ship, `ArchinityAltar.dll`,
namespace `Archinity.Core` (`CODING_STANDARDS.md` § *Hard constraints*).

### Mechanism

Four `Def` types, one `WorldComponent`, one `QuestPart`, three Harmony seams.

```
TraceDef : Def                       // exactly one instance ships
    float                 decayPerDay
    List<TraceIntrusionRow> intrusionRows
    SimpleCurve           searchRatePerDayByTrace     // Trace -> search units/day
    float                 revealAtSearchProgress      // when the countdown appears
    int                   escapeDistanceTiles
    FactionDef            pursuerFaction

TraceIntrusionRow                    // a plain class in a Def's list, not a Def
    IntrusionDepth depth             // Local | Device | Network | Command
    int            onSuccess
    int            onDetected
    SimpleCurve    defenceFactorCurve

TraceBandDef : Def                   // three instances ship
    IntRange            traceRange
    string              label, description, iconPath
    float               intelCostModifier
    List<TraceEffect>   effects

TraceEffect (abstract)               // polymorphic, authored with Class= in XML
    string label                     // the player-visible line — see Display
    virtual void OnActivate() / OnDeactivate() / OnLoadActive() / TickDay()
    virtual bool Replaces(TraceEffect other)
```

`TraceBandDef` and `TraceEffect` are **`VFED.VisibilityLevelDef` and
`VFED.VisibilityEffect` re-authored** — the same `IntRange` threshold, the same
polymorphic effect list, the same per-effect `label`, the same
`OnActivate`/`OnDeactivate`/`OnLoadActive`/`TickDay`/`Replaces` lifecycle **[V]**.
That design is verified working and is worth copying exactly; what it is not worth is
a dependency on VFE Deserters, which the copy costs nothing to avoid. See
*Available mechanisms*.

Three `TraceEffect` subclasses ship, and the list is **deliberately shorter than the
donor's** — see § *Why Trace cannot multiply with Reverence* for the two the donor
carries that we must not.

| Subclass | Seam | Evidence |
|---|---|---|
| `TraceEffect_Incident` | Harmony **prefix** on `RimWorld.IncidentWorker.CanFireNow` setting `__result = false` for an `IncidentDef` registered as band-gated. Two static `HashSet<IncidentDef>` built in `PostLoad`. | `VFED.HarmonyPatches.MiscPatches.CheckForVisibility` does exactly this **[V]** |
| `TraceEffect_RaidChance` | Harmony **postfix** on `RimWorld.FactionDef.RaidCommonalityFromPoints`, gated on `__instance == TraceDef.pursuerFaction`, multiplying `__result`. Changes the Glitterites' **share of faction selection**, not the size or the number of raids. | `VFED.HarmonyPatches.MiscPatches.EmpireRaidChance` does exactly this **[V]** |
| `TraceEffect_SearchRate` | no patch — read by the search accumulator below | new |

### Where state lives

**`Archinity.Core.WorldComponent_Trace`**, a new `WorldComponent`. Not
`WorldComponent_Currencies` — that component holds spendable balances and
[`CURRENCIES.md`](CURRENCIES.md) states *"Nothing else lives here, and that is the
design."* Trace is a ladder with thresholds and no spend, and it gets its own store.

```csharp
private int                trace;              // 0..100, clamped
private TraceBandDef       band;               // DERIVED, not scribed
private List<TraceEffect>  activeEffects;      // DERIVED, not scribed
private PlanetTile         lastSettledTile;    // for the relocation test
```

Public surface — the whole of it:

```csharp
int          Trace       { get; }
TraceBandDef Band        { get; }              // recomputed, never stored
IEnumerable<TraceEffect> ActiveEffects { get; }
void Notify_Trace(int delta, Quest from = null);        // tick / quest-part callers only
void Notify_Intrusion(in IntrusionReport report);       // subscribed to HACKING.md's event
void Notify_Relocated(PlanetTile from, PlanetTile to);
```

**`band` and `activeEffects` are derived and recomputed, never scribed.** That is the
donor's choice and it is the right one: `VFED.WorldComponent_Deserters.ExposeData`
scribes `visibility` and nothing else about the ladder, then calls
`Notify_VisibilityChanged(fromLoad: true)` as its last statement to rebuild the band
and the active-effect list from the def database **[V]**. A rebalanced
`TraceBandDef` therefore takes effect on the next load with no migration, and a band
def that leaves the load order cannot leave a dangling scribed reference.

The band walk is the donor's, verified **[V]**
(`VFED.WorldComponent_Deserters.Notify_VisibilityChanged`): iterate
`DefDatabase<TraceBandDef>.AllDefs.OrderBy(d => d.traceRange.max)`, accumulate the
effects of **every** band whose `traceRange.min <= trace` (deduplicating through
`TraceEffect.Replaces`), and set `band` to the first whose `traceRange.max >= trace`,
then break. **Effects accumulate upward from the bottom band**, which is why a
higher band need only author what it adds.

### What changes it

**Raise A — an intrusion completes.** `WorldComponent_Trace` subscribes to
`Archinity.Core.HackIntrusionLog.IntrusionCompleted`, the event
[`HACKING.md`](HACKING.md) § *The intrusion report* commits to. The increment is
looked up in `TraceDef.intrusionRows` by the report's `depth` and scaled by
`defenceFactorCurve.Evaluate(report.defence)`.

**This is where the two specs must agree, and the agreement is data rather than a
convention.** `GLITTERTECH.md` says *"Simple local hacks — such as a basic isolated
door — need not matter. Network-level hacks of mechanoids, reactors, command systems,
defenses or androids do."* `HACKING.md` makes `depth` **a property of the target,
declared in XML** on `Arch_IntrusionDepthExtension`, defaulting to `Local`, and emits
every intrusion including `Local` ones so that *"#56 decides to ignore them, rather
than me deciding they never happened"* **[V]**. So:

> **The `Local` row in `TraceDef.intrusionRows` is authored `onSuccess: 0,
> onDetected: 0`.** The requirement is satisfied as an authored number, not as a
> special case in code, and re-deciding it later is an XML edit. `Device`, `Network`
> and `Command` carry the real values.

**"Detectable access patterns" costs nothing.** `report.detected` is already rolled
by vanilla — `Rand.MTBEventOccurs(hacker.GetStatValue(StatDefOf.HackingStealth),
amount * 60f, 1f)` inside `CompHackable.Hack`, scaled per hackset by Ushanka's
`HacksetDef.stealthMultiplier` **[V]**. Deeper ICE already notices you more often; the
`onDetected` column is the only thing we author.

**Raise B — a mission against the Glitterites.** `QuestPart_ChangeTrace` (an
`inSignal` and an `int traceChange`) and its `QuestNode_ChangeTrace`, modelled on
`VFED.QuestPart_ChangeVisibility` — twenty-eight lines in the donor, two scribed
fields, `Notify_QuestSignalReceived` **[V]**. This is *"repeated raids… teach the
Glitterites who is attacking them"*: a raid that raises Trace does it by firing a
quest signal, which is inside the synced quest machinery.

**Raise C — an artifact is analysed.** Destructive Glitterite analysis calls `Notify_Trace` from the synced tick, at start, per increment or at completion, as [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117) decides. The carrier is [`RESEARCH.md`](RESEARCH.md) § *Destructive artifact analysis* ([#115](https://github.com/cjd721/Rimworld-Archinity/issues/115)). Add it to § *Multiplayer*'s writer table as "`IThingStudied.OnStudied` → job tick".

**Lower — a Trace-reducing quest.** The same part with a negative `traceChange`.
Requirements rule 7 (*"Glitterite quests provide opportunities to reduce Trace"*) is
the same mechanism with the sign flipped, which is why it is one part and not two.

**Decay.** `TraceDef.decayPerDay`, applied in
`WorldComponent_Trace.WorldComponentTick()` at `TicksGame % 60000 == 0`, the donor's
cadence **[V]**.

> **The donor reads its decay rate from a `ModSettings` slider and we must not.**
> `VFED.WorldComponent_Deserters.WorldComponentTick` does
> `Visibility -= DesertersMod.VisibilityChangePerDay`, and
> `DesertersMod.VisibilityChangePerDay => Instance.Settings.VisibilityChangePerDay`
> on a `ModSettings` subclass with a −5..5 slider **[V]**. Three more of its
> numbers are settings the same way — `IntelFromExtraction`, `VisibilityFromPillar`,
> `ResponseTimeMultiplier` **[V]**. Two clients with different sliders diverge on the
> same tick, from a `WorldComponentTick`, with no error message. **T-18.** Every
> number in this document is a `TraceDef` field.

### The search meter and the pursuit — one quest, mostly vanilla parts

Requirements rules 1–6 describe a **second** number: search progress, *"distinct from
Trace"*, which Trace controls the speed of and relocation resets. It does not live on
the component. It lives on a quest part, because the quest is also what displays it
and what fires the raids.

**`Archinity_GlitteritePursuit`**, a `QuestScriptDef` — a standing, auto-accepted,
`hiddenInUI: false` quest started by a `TraceEffect_Incident`-gated `IncidentDef` at
the middle band. Its parts:

| Part | Kind | Job |
|---|---|---|
| `QuestPart_TraceSearch : QuestPartActivable` | **new, ~90 lines** | holds `float searchProgress` and `bool revealed`; `QuestPartTick()` adds `TraceDef.searchRatePerDayByTrace.Evaluate(Trace) / 60000f` each tick; calls `Complete()` at 1.0 |
| `QuestPart_RandomRaid` | **vanilla, XML** | the detection raid, on `OutSignalCompleted`. `useCurrentThreatPoints: true` plus an authored `currentThreatPointsFactor` is requirements rule 5's *"huge raid scaled by both overall difficulty and Trace"* **[V]** |
| `QuestPart_ThreatsGenerator` | **vanilla, XML** | the repeats. `QuestPartActivable, IIncidentMakerQuestPart`; `ThreatsGeneratorParams` carries `onDays`, `offDays`, `minSpacingDays`, `numIncidentsRange`, `currentThreatPointsFactor` and `faction`, all scribed **[V]**. Enabled by `OutSignalCompleted`, disabled by our escape signal |

`QuestPart_ThreatsGenerator` is authored through the vanilla
`QuestNode_GenerateThreats` node and **vanilla already ships a worked example of
exactly this shape**: Royalty's `Script_EndGame_RoyalAscent.xml` uses it for *survive
escalating raids until the condition fires*, with `onDays 1.0 / offDays 0.5 /
minSpacingDays 0.04 / numIncidentsRange 1~2 / currentThreatPointsFactor 1.4 /
minThreatPoints 500` **[V]**. That is requirements rule 5's second sentence, in XML,
already written down once.

**Why the repeats are a quest part and not a storyteller comp.**
`RimWorld.Storyteller.MakeIncidentsForInterval` walks every ongoing quest and calls
`IIncidentMakerQuestPart.MakeIntervalIncidents` on enabled `QuestPartActivable`s
**[V]** — [`PRESSURE.md`](PRESSURE.md) § 7.1 already relies on this. A live pursuit
quest is its own incident generator; the storyteller roster never gets a vote, the
comp list is not re-indexed (**T-66**), and nothing else in the campaign's pacing
moves.

**The escape rule — rules 1, 4 and 6. No Harmony patch, and no hook on the travel path
at all.** `WorldComponent_Trace` scribes `lastSettledTile` and compares it on its own
`WorldComponentTick`:

```csharp
PlanetTile now = CurrentSettledTile();       // invalid while in transit — skip
if (now.Valid && now != lastSettledTile) {
    int d = Find.WorldGrid.TraversalDistanceBetween(lastSettledTile, now);
    if (d >= Def.escapeDistanceTiles) SendEscapeSignal();    // searchProgress -> 0
    lastSettledTile = now;
}
```

- distance **≥** `TraceDef.escapeDistanceTiles` → the threats generator disables and
  `searchProgress` resets to `0`. **`trace` is not touched.**
- distance **<** the threshold → nothing resets. Search continues from where it was —
  rule 1's *"a short move does not grant a fresh safe window and permits rapid
  reacquisition."*

`Find.WorldGrid.TraversalDistanceBetween(PlanetTile, PlanetTile)` is layer-aware and is
the same function `GravshipUtility.TryGetPathFuelCost` uses **[V]**, so the number the
player sees when launching and the number we test are the same number.

Rule 4 (*"Reducing Trace cannot undo progress already made"*) is structural rather
than enforced: `searchProgress` is only ever written by `QuestPartTick` and by the
escape signal. No Trace path can reach it.

> **Three seams were considered and two rejected. The rejections are the useful part.**
>
> **`ScenPart.PostGravshipLanded(Map)`** is `virtual`, engine-called, needs no Harmony
> patch, and Odyssey's own pursuit uses it — **but it takes only a `Map`** **[V]**.
> Nothing in its signature, and nothing reachable from it, says where the gravship came
> from. That alone disqualifies it.
>
> *An earlier draft gave two further reasons and **both were false**, so they are struck
> rather than quietly dropped. It said `LandingEnded` nulls the gravship "two statements
> before" the call — it is seven (`terrainCapture`, `gravship`, `Current.Game.Gravship`,
> `CurTimeSpeed`, two curtain masks, `map`, `moveDesignator`, then `ResetCutscene()`, then
> the call) **[V]**. And it said `takeoffTile` / `landingTile` are "reset by
> `ResetCutscene`" — **they are not**. `ResetCutscene()` is exactly
> `Find.ScreenshotModeHandler.Active = false; cutsceneInProgress = false; landingMap =
> null;` **[V]**. Both tiles survive the landing and are `Scribe_Values`-persisted as
> `"takeoffTile"` and `"targetTile"` **[V]**, so they are reachable by `AccessTools.Field`
> from anywhere. The conclusion was right on the wrong evidence.*
>
> **A postfix on `GravshipUtility.TravelTo(Gravship, PlanetTile oldTile, PlanetTile
> newTile)`** has both tiles and was the previous proposal. **Rejected on two independent
> counts, each verified:**
>
> 1. **`TravelTo` reassigns its own `oldTile` parameter.** The body is
>    `if (oldTile.Layer != newTile.Layer) oldTile = newTile.Layer.GetClosestTile_NewTemp(oldTile);`
>    **[V]**. A Harmony **postfix** reads the post-mutation slot, so a surface→orbit
>    relocation measures from the *projected same-layer* tile — a distance near zero,
>    never an escape. The late-Ultra act is in orbit, which is precisely where this would
>    have failed, and silently. A prefix or `__state` avoids it; the tick comparison never
>    has to.
> 2. **It runs outside Multiplayer's determinism window** — see § *Persistence and
>    multiplayer* and **T-78**. `TakeoffEnded` is where Multiplayer *lifts* the freeze,
>    not where it holds it.
>
> **What the tick comparison costs:** the escape is detected on the next world tick rather
> than in the landing frame. Nothing in the requirements asks for instantaneity — rule 1
> is about distance — and detection lands within one tick of the map existing.

### Where the player sees it

Six surfaces. Four are free or nearly so, and **the one the requirements name
explicitly — the risk of an intrusion, before committing to it — is ten lines on a
patch [`HACKING.md`](HACKING.md) already writes.**

**D1 — the band, in the network window.** One header row in the
`MainTabWindow_Network` that [`CURRENCIES.md`](CURRENCIES.md) builds: band icon,
band label, the number coloured
`Color.Lerp(BrightGreen, RedReadable, InverseLerp(0, 100, trace))`, and a hover
tooltip carrying the band description, the modifiers, and a bullet list of every
active effect's `label`. **This is the donor's exact readout** —
`VFED.Dialog_DeserterNetwork.DoWindowContents` **[V]** — and reproducing it costs
~40 lines inside a window that already exists. It is also the *only* place the donor
draws the number, which is why D6 exists.

**D2 — the price of a mission, before accepting it.** `Reward_Trace : RimWorld.Reward`,
modelled on `VFED.Reward_Visibility` **[V]** — a plain `Reward` subclass whose
`StackElements` returns `QuestPartUtility.GetStandardRewardStackElement(label, icon,
tipGetter, onClick)`, vanilla's own reward-row helper, and whose `TotalMarketValue`
prices the change so the quest generator treats Trace as part of the payload. A
mission that raises Trace and one that lowers it both show a row in the quest-choice
list *before* acceptance. ~60 lines, and [`CURRENCIES.md`](CURRENCIES.md) already
establishes the pattern for `Reward_Currency`.

**D3 — the risk of *this* intrusion, before committing to it.**
`GLITTERTECH.md` asks the player to *"see the risk before committing to an
intrusion"*, and that is a per-target readout, not a letter afterwards.
[`HACKING.md`](HACKING.md) already writes a postfix on
`RimWorld.CompHackable.CanHackNow(Pawn)` for the research gate, and vanilla already
renders that `AcceptanceReport.Reason` in three places — the float-menu refusal,
`CompHackable`'s inspect string, and the targeter mouse label **[V]**. We add the
target's authored `IntrusionDepth` and its Trace cost to `CompHackable`'s inspect
string through the same postfix: **~10 lines on a patch that is already in the
budget.**

**D4 — the band changed.** `Letter_Trace : ChoiceLetter`, modelled on
`VFED.Letter_VisibilityChange` **[V]**. The body lists newly-active and
newly-inactive effect `label`s as two bullet lists, and the `LetterDef` is chosen by
direction — positive when the band falls, `ThreatBig` at the top band, negative
otherwise, which is the donor's own rule **[V]**. ~50 lines.

**D5 — the pursuit countdown.** `QuestPartActivable` declares
`public virtual string ExpiryInfoPart` and `ExpiryInfoPartTip`, rendered by
`RimWorld.MainTabWindow_Quests`, plus `AlertReport` / `AlertLabel` /
`AlertExplanation` / `AlertCritical` which feed a vanilla alert **[V]**.
`QuestPart_TraceSearch` overrides them:

- `revealed == false` → `ExpiryInfoPart` returns `null`. **Rule 2's *"search
  initially proceeds invisibly"* is the default, not a special case.**
- `revealed == true` → it returns
  `((1f - searchProgress) / currentRatePerTick).ToStringTicksToPeriod()`, recomputed
  **on every draw from the current Trace**. Rule 3's *"changes take effect without
  waiting for a periodic reassessment window; the visible estimate updates
  accordingly"* is satisfied because there is no stored deadline to reassess — the
  estimate is a division, and lowering Trace lengthens it on the next frame.
- `ExpiryInfoPartTip` states that it is an estimate at the current Trace, and carries
  `TraceDef.escapeDistanceTiles` — which is where *"relocation distance requirements
  must be legible so a short hop is an informed risk"* lands.

`QuestPart_Delay` is the shape to copy: `TicksLeft`, `ExpiryInfoPart`,
`ExpiryInfoPartTip`, `AlertCritical => TicksLeft < ticksLeftAlertCritical`,
`QuestPartTick()` **[V]**.

**D6 — the always-visible number.** One more row on the
`RimWorld.GlobalControlsUtility.DoDate(float, float, ref float curBaseY)` postfix
[`CURRENCIES.md`](CURRENCIES.md) § D3 already specifies. The `ref float curBaseY`
makes rows additive by construction **[V]**, so Trace stacks under Influence and
Intel rather than fighting them. **One postfix, three rows — not two postfixes.**

### Cost

| Piece | Kind | Lines | Lands in |
|---|---|---|---|
| `TraceDef` + `TraceIntrusionRow` + `TraceBandDef` + `TraceEffect` base | new C# | ~70 | `Archinity.Altar/Source/Trace.cs` |
| `WorldComponent_Trace` (band walk, decay, intrusion subscription, relocation) | new C# | ~140 | same |
| Three `TraceEffect` subclasses + their two Harmony seams | new C# | ~70 | same, patches in `Source/Patches.cs` |
| `QuestPart_TraceSearch` + `QuestNode_TraceSearch` | new C# | ~110 | `Archinity.Altar/Source/TraceQuests.cs` |
| `QuestPart_ChangeTrace` + `QuestNode_ChangeTrace` | new C# | ~50 | same |
| `Reward_Trace` | new C# | ~60 | same |
| `Letter_Trace` | new C# | ~50 | same |
| Relocation check on `WorldComponentTick` (no patch) | new C# | ~25 | `Archinity.Altar/Source/Trace.cs` |
| Startup validator — band ranges tile 0..100 with no gap or overlap | new C# | ~15 | same |
| D1 band row in `MainTabWindow_Network` | new C# | ~40 | `Source/CurrencyUI.cs` |
| D3 inspect-string addition to the existing `CanHackNow` postfix | patch | ~10 | `Source/Patches.cs` |
| D6 — one more row on an existing postfix | patch | ~5 | `Source/Patches.cs` |
| **Total new C#** | | **~645** | one assembly |
| One `TraceDef` + three `TraceBandDef`s + every effect | **XML** | ~180 | `Archinity.Glitterites/Defs/Trace/` |
| The pursuit `QuestScriptDef` — the search part, the detection raid, the threats generator, the reveal letter, signals and text | **XML** | **~400** | same |
| The detection `IncidentDef`, `Arch_IntrusionDepthExtension` on every target def, `layerWhitelist` patches for orbit (**T-48**) | **XML** | ~120 | `Archinity.Glitterites/Patches/` |
| **Total XML** | | **~700** | |

> The XML figure was **~350** in the first draft and that was 1.5–2× low. Royalty's
> `Script_EndGame_RoyalAscent.xml` — the shipped quest that does roughly what the pursuit
> quest must do — is ~400 lines on its own **[V]**, and it does not also carry a band
> ladder or an intrusion-depth patch set.

Marked **[I]**: every mechanism composed above is **[V]**; the claim that they
compose into the required behaviour is inferred until something compiles, and the
line estimates with it.

---

## Why Trace cannot multiply with Reverence

[`docs/requirements/PRESSURE.md`](../requirements/PRESSURE.md) forbids *"accidental
runaway multiplication"*, [`GLITTERTECH.md`](../requirements/GLITTERTECH.md) says the
Glitterites *"do not care about Reverence"*, and
[`PRESSURE.md`](PRESSURE.md) § 2 already states the structural answer: Reverence
enters the **global scalar** (`DefaultThreatPointsNow`) and the **selection weight**
(`IncidentChanceFinal`); *"Trace is deliberately absent from this list… it never
touches the global scalar."* Its Verification check 5 is *"raise Trace to maximum and
confirm ordinary raids are unchanged in size."*

**That ruling costs one of the donor's effects, and this document pays it.**
`VFED.VisibilityEffect_ArmySize` is a Harmony **prefix** on
`PawnGroupMakerUtility.GeneratePawns` and `GeneratePawnKindsExample` that multiplies
`PawnGroupMakerParms.points` whenever `parms.faction == Faction.OfEmpire` **[V]**.
Ported naively it would make a Glitterite raid's size
`(vanilla + Reverence term) × Trace` — a product, arrived at by a different code path
but the same arithmetic the requirement forbids. **We do not port it.**

Trace scales raid size **only inside the pursuit quest**, through two per-part fields
that requirements rule 5 asks for by name: `QuestPart_RandomRaid.currentThreatPointsFactor`
and `ThreatsGeneratorParams.currentThreatPointsFactor` **[V]**. The multiplication is
therefore confined to raids authored for the pursuit, is bounded by the authored
factor, and never reaches an ordinary raid — which is exactly what PRESSURE.md's check
5 tests.

`TraceEffect_RaidChance` survives because it is a different quantity:
`FactionDef.RaidCommonalityFromPoints` decides the Glitterites' **share of faction
selection**, not how big the raid is or how many arrive. It expresses *"raids and
pursuit become more frequent"* without touching any product that Reverence is in.

**Nothing proposed here needs an edit to [`PRESSURE.md`](PRESSURE.md).** Its § 4
already names itself the carrier for *"the Glitterite detection raid (#56 says when,
this says how big)"*, and the parts above are the *when*.

---

## Decoupling from Church politics

[#56](https://github.com/cjd721/Rimworld-Archinity/issues/56) item 4 is the single
decision point for whether machinery shared with Exaltation or Influence couples
Church standing to Glitterite pursuit.
[`CURRENCIES.md`](CURRENCIES.md) § *What is shared* reported the shape and asked for a
ruling. **Ruled here, three ways.**

**1. The shared balance store stays shared.** `WorldComponent_Currencies` holds
Influence and Intel as two rows in one `Dictionary<CurrencyDef,int>` under one
`Scribe` key. That is a shared save key and a shared null-key prune and nothing else:
the API takes one `CurrencyDef`, no path is keyed on a faction, and Church standing is
not an input to any code in that document **[V]**. The escape hatch
(`CURRENCIES.md`'s two-component split, ~15 lines) is **not taken**.

**2. Trace does not live there.** `WorldComponent_Trace` is its own component with
its own `Scribe` key. This is not a concession to the coupling question — it falls out
of the shapes being different, as `CURRENCIES.md` already observed.

**3. The band's price modifier is currency-scoped, and this is the one real risk.**
The donor applies `VisibilityLevelDef.intelCostModifier` to **everything in its
shop** — `DeserterServiceDef.intelCost`, `ContrabandExtension`, and the derived quest
price in `Utilities.GetIntelCost` **[V]**. Ported naively into a window that also
sells Schism operations, Glitterite pursuit would silently set the price of Church
politics. **`TraceBandDef.intelCostModifier` is applied only where
`CurrencyPurchaseDef.currency == Archinity_Intel`**, and that is checkable by grep
rather than by review: no code path may read `TraceBandDef` without a `CurrencyDef`
in scope.

**That scope includes every Intel exchange entry, by construction.**
[`CURRENCIES.md`](CURRENCIES.md) § *The Intel exchange* sells Instruction items as
`Archinity_Intel` purchases, so a high Trace band raises the price of Instruction as well
as the pursuit — aggression taxed twice. Whether that is intended is an **open
requirement**, not ruled here; owner
[#117](https://github.com/cjd721/Rimworld-Archinity/issues/117) (`CURRENCIES.md`
§ *Outstanding decisions*). A per-entry opt-out is ~2 lines.

---

## Persistence and multiplayer

### Persistence

```csharp
Scribe_Values.Look(ref trace, "trace", 0);
Scribe_Values.Look(ref lastSettledTile, "lastSettledTile");
// band and activeEffects are NOT scribed
```

The last statement of `ExposeData` rebuilds the ladder, the donor's own ordering
**[V]**:

```csharp
RecomputeBand(fromLoad: true);   // runs OnLoadActive, not OnActivate
```

The `fromLoad` flag matters and the donor gets it right: on load the effects get
`OnLoadActive()` and **no letter is sent**, so reloading a save does not re-announce a
band the player already knows about **[V]**.

`searchProgress` and `revealed` are scribed on the quest part, inside
`QuestPart_TraceSearch.ExposeData`, which is the vanilla quest machinery's own
persistence — `QuestPart_ThreatsGenerator` scribes its `ThreatsGeneratorParams` with
`Scribe_Deep.Look` the same way **[V]**.

**Adding the component to an existing save is safe.**
`RimWorld.Planet.World.ExposeComponents` scribes `components` and then calls
`FillComponents()`, which constructs any `WorldComponent` type not present **[V]** —
the component arrives at Trace 0, band 1, no pursuit.

**A `TraceBandDef` removed from the load order costs nothing**, because the band is
derived. This is the direct benefit of not scribing it.

### Multiplayer

**Every write to Trace is already on a synced path, and that is by construction
rather than by luck.**

| Writer | Path | Synced by |
|---|---|---|
| decay | `WorldComponentTick` | the world tick |
| `Notify_Intrusion` | `ThingComp.Notify_Hacked` inside `CompHackable.OnHacked`, reached from `JobDriver_Hack` **[V]** | the job |
| `QuestPart_ChangeTrace` | `Notify_QuestSignalReceived` | the quest machinery |
| `QuestPart_TraceSearch.QuestPartTick` | `Quest.QuestTick` | the world tick |
| the relocation check | `WorldComponentTick` — no patch, no hook |

**There is no new synced-command surface.** Nothing in this document originates at a
button. That is the whole reason the donor's defects do not reproduce here: VFED's
problem is a *purchase* running in `OnGUI`, and Trace has no purchase.

### Why the relocation check is not on the travel path — T-78

`WorldComponent_GravshipController.WorldComponentUpdate` advances the cutscene on
`Time.deltaTime`, gated on `Prefs.GravshipCutscenes`, and calls **both** `TakeoffEnded()`
and `LandingEnded()` from there **[V]**. Multiplayer patches both — **but not the same
way, and the asymmetry is the hazard:**

| | Takeoff | Landing |
|---|---|---|
| patch | `PatchGravshipTakeoffEnded`, a **prefix** | `PatchGravshipLandingEnded`, a **prefix** |
| what it does | `GravshipTravelUtils.StopFreeze(); CloseSessionAt(__instance.takeoffTile);` **[V]** | `Rand.PushState(); Rand.StateCompressed = __instance.map.AsyncTime().randState;` plus a `Finalizer` popping it **[V]** |
| `Rand` wrapper | **none** | yes |
| freeze | **lifted, in the prefix, before the body runs** | held until this point |

`GravshipUtility.TravelTo` is called from inside `TakeoffEnded`'s **body** **[V]** — i.e.
**after** `StopFreeze()` has already run. So anything hung on `TravelTo` or on
`TakeoffEnded` executes with the simulation unfrozen, with no `Rand` state pushed, on a
frame-driven path whose timing depends on a per-client `Prefs` value. Two clients reach it
at different ticks, and a game-state write there is a desync with no error message.

**`PatchGravshipCutsceneToFreeze` does not rescue it**: it postfixes `InitiateTakeoff` and
`InitiateLanding` with `StartFreeze()` **[V]** — it opens the window that
`PatchGravshipTakeoffEnded` closes.

> *An earlier draft of this section asserted that our postfix would sit "inside the same
> frozen window", and § *Verification* item 3 said "the freeze lifts in `LandingEnded`'s
> prefix". **Both are false**, and they were reached by reading two of the three gravship
> patches and generalising. `PatchGravshipTakeoffEnded` is the third. The same draft
> withdrew a proposed trap on the strength of that generalisation; **the trap is
> reinstated as T-78**, scoped to the asymmetry rather than to vanilla.*

**The build avoids the whole question.** The relocation check runs on
`WorldComponentTick`, reads two scribed `PlanetTile`s, calls one grid method, draws no
random number and reads no `Prefs`. It never touches the cutscene path.

**Defs, not settings** (**T-18**). Every threshold, rate, distance and multiplier is a
`TraceDef` or `TraceBandDef` field. The donor puts four of its equivalents on a
`ModSettings` slider **[V]** and that is the single largest reason this is a rebuild
rather than a reuse.

**No static mutable effect state.** `VFED.VisibilityEffect_AerodroneBombardment`
keeps `private static bool active` and schedules itself with
`Rand.Range(120000, 180000)` into a delegate queue whose `ExposeData` serializes
*method names as strings* and reflects them back on load **[V]**. None of that is
copied. Our effects hold no static state and schedule nothing; `TickDay` is called
from `WorldComponentTick` and does its work inline (**T-21**).

---

## Failure and recovery

| Failure | Detection | Recovery |
|---|---|---|
| A `TraceBandDef` leaves the load order, or its range is edited | **Loud on the next load** — the band walk finds no band whose `traceRange.max >= trace` | The walk must not leave `band` null. A startup validator asserting that the shipped `traceRange`s tile 0..100 with no gap and no overlap is ~15 lines and converts a null-band crash into a config error. **This is the one place the donor's design is genuinely fragile: its walk has no fallback** **[V]**. |
| Trace and search disagree — search completes while Trace is 0 | Visible: a pursuit raid with no readout to explain it | Not a bug. Rule 4 is explicit that reducing Trace *"cannot undo progress already made"*, and rule 6 that *"reducing Trace after detection does not conceal the location."* The `ExpiryInfoPartTip` must say so. |
| The pursuit quest ends (declined, failed, cleaned up) and search is orphaned | `searchProgress` lives on the quest part, so it dies with it | Correct by construction, but it means **the pursuit quest must not be dismissible**. Author it auto-accepted with no `QuestPart_Choice`; `Quest.dismissed` only hides a row, it does not end a quest **[V]**. |
| A short relocation is mistaken for an escape | **Silent** — the player believes they got away | Prevented rather than recovered: the threshold is a `TraceDef` field, stated in `ExpiryInfoPartTip`, and `TraversalDistanceBetween` is the same function the gravship's own fuel cost uses **[V]**, so the number the player sees when launching and the number we test are the same number. |
| `GravshipUtility.TravelTo`'s signature changes on a RimWorld update | **Loud** — Harmony throws at startup on a missing target | Nothing else in this document is exposed to an update; every other seam is a virtual override or a `Def` field. |
| Two clients hold different Trace | MP desync | Unreachable by design — see the writer table. No path originates at a button and no number comes from `ModSettings`. |

**No campaign softlock is reachable from this document.** Rule 6 is explicit that
*"detection neither forces departure nor causes automatic defeat"*; the player may
stay and fight indefinitely, and the threats generator is bounded by its authored
`onDays`/`offDays` cycle rather than being continuous.

---

## Status

**Evidence class: READ.** Settled against the 1.6 `Assembly-CSharp.dll`, `VFED.dll`
1.6 and `Multiplayer.dll` 1.6, plus shipped def XML. No stub run, no launch.

| | |
|---|---|
| **Verified available mechanisms** | `VFED.VisibilityLevelDef` / `VisibilityEffect` as a band-ladder architecture; the `IncidentWorker.CanFireNow` prefix and the `FactionDef.RaidCommonalityFromPoints` postfix as band-effect seams; `QuestPartActivable`'s `QuestPartTick` / `ExpiryInfoPart` / `AlertReport`; `QuestPart_RandomRaid` and `QuestPart_ThreatsGenerator` with `currentThreatPointsFactor`; `WorldGrid.TraversalDistanceBetween`; `World.FillComponents`. All **[V]**. |
| **Corrected since the first resolution** | The relocation seam moved from a `GravshipUtility.TravelTo` postfix to a `WorldComponentTick` tile comparison, for two verified reasons: `TravelTo` reassigns its own `oldTile` parameter on a cross-layer move, and `TakeoffEnded` runs **after** Multiplayer lifts its freeze and with no `Rand` wrapper (**T-78**). Two supporting claims about `LandingEnded`'s statement ordering and `ResetCutscene` were **false** and are struck in place. |
| **Confirmed negative** | **Odyssey's gravship pursuit does not carry the required behaviour.** See *Available mechanisms*; this corrects a stated preference in `docs/requirements/PRESSURE.md`. |
| **Proposed, not selected** | The whole build above. **[I]** as a composition, and the line estimates with it. |
| **Open parameters** | Every number: band thresholds, decay rate, the four `intrusionRows` columns, `searchRatePerDayByTrace`, `revealAtSearchProgress`, `escapeDistanceTiles`, both `currentThreatPointsFactor`s. Balance, fog on [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2). |

---

## Available mechanisms

### Odyssey's gravship pursuit — the named preferred provider, read and declined as a carrier

`docs/requirements/PRESSURE.md` § *Glitterite pursuit* opens: *"The preferred provider
to investigate is Odyssey's existing gravship pursuit mechanic. Reuse is a design
preference, not yet a verified implementation."* It has now been verified, and the
verdict is **repoint, not reuse**.

**What it actually is [V]:** `RimWorld.ScenPart_PursuingMechanoids`, a single
`ScenPart` on the Odyssey `TheGravship` scenario (`ScenPartDef PursuingMechanoids`,
`Data/Odyssey/Defs/Scenarios/ScenParts_Various.xml`). It holds two
`Dictionary<Map,int>` fields — `mapWarningTimers` and `mapRaidTimers` — of **absolute
tick deadlines**, scribed `LookMode.Reference, LookMode.Value`. `Tick()` runs from
`Scenario.TickScenario` every tick and does work every 2500.

**Each of the five behaviours the requirements ask for is absent:**

| Required | Odyssey ships |
|---|---|
| Search progress accumulating at a rate Trace controls | **A fixed one-shot draw.** `StartTimers(Map)` sets `warning = Now + WarningDelayRange.RandomInRange` (14–16 days) and `raid = Now + RaidDelayRange.RandomInRange` (18–35 days) **[V]**. There is no accumulator and no rate term of any kind. |
| *"Escape requires sufficient distance"* | **No distance check exists anywhere.** `ScenPart_PursuingMechanoids.PostGravshipLanded(Map)` does `onStartMap = false; StartTimers(map);` unconditionally **[V]**. One tile or forty, surface or orbit — every landing resets. |
| Hidden, then revealed by a quest | Hidden, then revealed by an **alert**. `Alert_MechThreat : Alert_Scenario`, surfaced by `ScenPart.GetAlerts()` and collected by `AlertsReadout` walking `Find.Scenario.AllParts`, with `GetLabel()` printing `(raidTick - TicksGame).ToStringTicksToPeriod()` **[V]**. No quest is involved. |
| Repeated raids until escape | **Exactly two raids, then silence on that map.** `FireRaid_NewTemp(map, 1.5f, 2000f)` at the deadline and `(map, 2f, 8000f)` half a day later, both `IncidentDefOf.RaidEnemy.Worker.TryExecute` with `faction = Faction.OfMechanoids` **[V]**. There is no repeating loop. |
| Trace-driven termination | `Notify_QuestCompleted()` sets a `questCompleted` kill switch, and its **only caller** is `RimWorld.CompCerebrexCore.DeactivateCore(bool)` **[V]** — the pursuit ends by destroying one specific Odyssey building. |

**What is worth taking, and it is not nothing:**

- **`ScenPart` is a legitimate save-backed global tick host** with `GetAlerts()`
  straight into the alert strip and no Harmony patch **[V]**. We do not use it,
  because the pursuit is a quest and a quest gets `ExpiryInfoPart` and
  `QuestPartTick` for free — but it is the cheaper option if the quest framing is
  ever dropped.
- **`TimerIntervalTick(int t) => (t + 2499) / 2500 * 2500`** **[V]** — rounding a
  deadline up to the next tick-interval boundary so an equality test cannot be
  skipped. Worth knowing; not needed here, because our meter accumulates rather than
  comparing against a deadline.
- `PostGravshipLanded`'s existence proved where the landing hook is, and its
  signature proved why we cannot use it.

**Premise corrected, and the correction belongs to exactly one file.**
**`docs/requirements/PRESSURE.md` § *Glitterite pursuit*** is the only requirements
document that names Odyssey or gravship pursuit; its opening sentence is *"The preferred
provider to investigate is Odyssey's existing gravship pursuit mechanic."* The mechanic
exists, and it is a scenario timer — rules 1, 3, 4, 5 and 7 each need machinery it does
not have.

> **`docs/requirements/GLITTERTECH.md` does not name Odyssey, gravships or pursuit reuse
> anywhere.** Its § *Saved state and remaining work* delegates: *"The pursuit rules are
> settled in [difficulty and pursuit](PRESSURE.md#glitterite-pursuit)."* An earlier draft
> of this paragraph said both files carried the preference. They do not, and a requirements
> correction that names the wrong file cannot be acted on.

### VFE Deserters Visibility — the architecture, repointed

`…/294100/3025493377/1.6/Assemblies/VFED.dll`. `MOD-SNAPSHOT.md` marks
`oskarpotocki.vfe.deserters` **Src 1.4 ⚠**, so everything below is the 1.6 assembly,
not the source tree.

**Verdict per piece:**

| Piece | Verdict |
|---|---|
| `VisibilityLevelDef` — `IntRange` band, icon, description, `List<VisibilityEffect>` | **KEEP THE SHAPE, REBUILD.** Six bands ship, 0–100, tiling without gaps **[V]**. Our three bands are the same shape with the VFE-specific fields (`contraband*`, `imperialResponse*`) dropped. |
| `VisibilityEffect` + the `OnActivate`/`OnDeactivate`/`OnLoadActive`/`TickDay`/`Replaces` lifecycle | **KEEP, REBUILD.** The single best idea in the donor: band effects are polymorphic objects with their own player-visible `label`, so the readout and the behaviour are authored in one place and cannot drift apart **[V]**. |
| `Notify_VisibilityChanged`'s band walk and effect diff | **KEEP THE ALGORITHM** — cumulative-from-below with `Replaces` dedup, `OnActivate`/`OnDeactivate` on the set difference, `OnLoadActive` on load **[V]**. |
| `VisibilityEffect_Incident` → `IncidentWorker.CanFireNow` prefix | **KEEP THE SEAM** **[V]**. |
| `VisibilityEffect_RaidChance` → `FactionDef.RaidCommonalityFromPoints` postfix | **KEEP THE SEAM** **[V]**. |
| `VisibilityEffect_ArmySize` → `PawnGroupMakerUtility.GeneratePawns` prefix | **REJECT.** See § *Why Trace cannot multiply with Reverence*. The seam is real; using it is the multiplication the requirements forbid. |
| `VisibilityEffect_GameCondition` → a world `GameCondition` with a duration | **REJECT for the pursuit**, though it is a working countdown. A `GameCondition` duration is a fixed deadline; rule 3 requires an estimate that moves when Trace moves. |
| `VisibilityEffect_Goodwill` → a random faction −10 per `TickDay` | **REJECT.** `GLITTERTECH.md` says the Glitterites are *"outside human belief, persuasion or diplomacy"*; a pursuit that moves human goodwill contradicts it. |
| `VisibilityEffect_AerodroneBombardment` | **REJECT the implementation outright.** `private static bool active`, an `OnActivate` `Rand.Range`, and a scheduled delegate whose persistence serializes `action.Method.Name + "." + DeclaringType.AssemblyQualifiedName` and reflects it back on load **[V]**. |
| `QuestPart_ChangeVisibility` + `Utilities.ChangeVisibility` | **KEEP THE PATTERN** — a two-field `QuestPart` on `Notify_QuestSignalReceived` **[V]**. |
| `Reward_Visibility` | **KEEP THE PATTERN, not the type** — a plain `RimWorld.Reward` subclass using only vanilla API, with `TotalMarketValue` pricing the meter change **[V]**. |
| `Letter_VisibilityChange` | **KEEP THE PATTERN** — a `ChoiceLetter` carrying the band def and listing effect labels **[V]**. |
| `StorytellerComp_*_ByVisibility` (five classes) | **REJECT.** They multiply `acceptFraction` by `VisibilityFactor + 0.5f` and `numIncidentsRange` by `Mathf.Lerp(0, 20, VisibilityFactor)` before calling `IncidentCycleUtility.IncidentCountThisInterval` **[V]** — i.e. the meter drives the *global* incident cadence. That is what [`PRESSURE.md`](PRESSURE.md) reserves for `StorytellerComp_Pressure`, and a second meter reaching the same lever is the multiplication problem again. They are nonetheless a **live precedent for PRESSURE.md's own `StorytellerComp_Pressure` design**, which supplies `acceptFraction` through the same public method — worth citing there. |
| The `ModSettings`-driven rates | **REJECT — T-18.** Four numbers on sliders **[V]**. |
| `WorldComponent_Deserters.EventQueue` | **REJECT.** A `PriorityQueue<Action,int>` persisted by serializing method names **[V]**. |

### Vanilla and the DLC

| Mechanism | What it gives | Why it is or is not the answer |
|---|---|---|
| `QuestPartActivable` **[V]** | `QuestPartTick()`, `ExpiryInfoPart` / `ExpiryInfoPartTip` in the quest tab, `AlertReport` / `AlertLabel` / `AlertExplanation` / `AlertCritical` in the alert strip, `inSignalEnable` / `inSignalDisable` / `reactivatable`, `Complete()` firing `OutSignalCompleted` | **Adopted.** It is a save-backed, tick-driven, self-displaying, signal-gated state machine — every seam the search meter needs, in one base class. |
| `QuestPart_Delay` **[V]** | the worked example of an activable with a countdown | **Adopted as the model** for `ExpiryInfoPart` and `AlertCritical`. |
| `QuestPart_ThreatsGenerator` + `ThreatsGeneratorParams` + `QuestNode_GenerateThreats` **[V]** | repeated raids on a cycle, faction-pinned, points-factored, scribed, XML-authorable; pumped by `Storyteller.MakeIncidentsForInterval` walking `IIncidentMakerQuestPart` | **Adopted.** Royalty's `Script_EndGame_RoyalAscent` is the shipped worked example. |
| `QuestPart_RandomRaid` **[V]** | a one-shot raid on a signal with `pointsRange`, `faction`, `useCurrentThreatPoints`, `currentThreatPointsFactor`, `arrivalMode`, `raidStrategy` | **Adopted** for the detection raid. |
| `IncidentCycleUtility.IncidentCountThisInterval` **[V]** | a schedule seeded from `World.info.persistentRandomValue`, the target's `ConstantRandSeed`, the comp index and the interval number — it draws nothing from the shared `Rand` stream | The reason the threats generator is the MP-safest of the repeating options. [`PRESSURE.md`](PRESSURE.md) § 3 says the same about its own comp. |
| `GravshipUtility.TravelTo(Gravship, PlanetTile, PlanetTile)` **[V]** | `public static`, receives both tiles, called from `TakeoffEnded()`'s body | **Considered and rejected.** It reassigns `oldTile` on a cross-layer move, so a postfix measures the projected tile **[V]**; and its caller runs after Multiplayer's freeze lifts, with no `Rand` wrapper (**T-78**). |
| `WorldComponent_GravshipController.takeoffTile` / `landingTile` **[V]** | both `Scribe_Values`-persisted (`"takeoffTile"`, `"targetTile"`), untouched by `ResetCutscene`, reachable by `AccessTools.Field` | **Not needed** — the tick comparison reads the settled tile directly. Recorded because an earlier draft claimed they were destroyed, and they are not. |
| `WorldGrid.TraversalDistanceBetween` / `ApproxDistanceInTiles` **[V]** | tile distance, layer-aware; `TraversalDistanceBetween` is what `GravshipUtility.TryGetPathFuelCost` uses | **Adopted** — the player's fuel cost and our escape test read the same function. |
| `MapParent.Abandon(bool wasGravshipLaunch)` leaving a `GravshipLaunch` world object **[V]** | a marker at the abandoned tile, carrying `creationGameTicks` | **Not adopted**, but it is the fallback if `TravelTo` ever stops being patchable. |
| `ScenPart` + `Scenario.TickScenario` + `GetAlerts()` **[V]** | a save-backed global tick host with a free alert surface and no Harmony patch | **Not adopted** — the quest gives us more. Recorded because it is genuinely the cheaper spine for a meter with no quest. |
| `GameCondition` with a duration **[V]** | a visible world-scoped countdown | **Not adopted** — a fixed deadline cannot express a rate that Trace changes continuously. |

### The wide pass

Run over both corpus roots plus vanilla and the DLC.
`python tools/corpus.py --check` reported the corpus clean at **155 mods** at both ends
of this ticket. Sweep construction, per-carrier findings and the validation run are on
[#56](https://github.com/cjd721/Rimworld-Archinity/issues/56).

**Result: `VFED.VisibilityLevelDef` is the only Def-driven world-scoped band ladder
with an escalating consequence in the corpus**, and nothing anywhere carries a
search-progress meter whose rate is an external variable.

---

## Verification

**Read, with a path and a `Type.Method` anchor, on
[#56](https://github.com/cjd721/Rimworld-Archinity/issues/56):**
`VFED.WorldComponent_Deserters` (`WorldComponentTick`, `Notify_VisibilityChanged`,
`ExposeData`), `VFED.VisibilityLevelDef`, `VFED.VisibilityEffect` and all six
subclasses, `VFED.QuestPart_ChangeVisibility`, `VFED.Utilities.ChangeVisibility`,
`VFED.Reward_Visibility`, `VFED.Letter_VisibilityChange`,
`VFED.Dialog_DeserterNetwork.DoWindowContents`,
`VFED.StorytellerComp_ByVisibility` and `_OnOffCycle_ByVisibility`,
`VFED.HarmonyPatches.MiscPatches.CheckForVisibility` / `.EmpireRaidChance`,
`VFED.HarmonyPatches.ImperialForcesSizePatches`, `VFED.DesertersMod` /
`DesertersSettings`; vanilla `ScenPart_PursuingMechanoids`, `Alert_MechThreat`,
`QuestPartActivable`, `QuestPart_Delay`, `QuestPart_RandomRaid`,
`QuestPart_ThreatsGenerator`, `ThreatsGeneratorParams`, `QuestNode_GenerateThreats`,
`Quest` (`TicksUntilExpiry`, `State`, `QuestTick`),
`Verse.WorldComponent_GravshipController` (`WorldComponentUpdate`, `LandingEnded`),
`GravshipUtility.TravelTo`, `WorldGrid.TraversalDistanceBetween`;
Multiplayer's `PatchGravshipLandingEnded`, `PatchGravshipCutsceneToFreeze`,
`GravshipTravelUtils`.

**Needs a prototype or an in-game check before this is built:**

1. **That the band walk never leaves `band` null.** A startup validator over
   `DefDatabase<TraceBandDef>` asserting the ranges tile 0..100 is the fix; confirming
   the donor's walk actually falls through on a gap is a one-line test. **[I]**
2. **That `QuestPart_TraceSearch.ExpiryInfoPart` re-renders when Trace changes.**
   `MainTabWindow_Quests` reads the property each draw **[V]**, so it should — but
   whether the quest tab caches the row is not read. Observable: lower Trace with the
   quest tab open and watch the estimate lengthen without a reload.
3. **That `CurrentSettledTile()` returns invalid for the whole of a gravship transit,
   and returns the new tile once — not twice, and not the origin tile again — on
   arrival.** The failure mode if it flickers is a spurious escape or a missed one.
   Observable with one client; the two-client check is only that both reach the same
   verdict on the same tick, which they must, because the input is scribed game state.
   *(This item previously asked whether a `TravelTo` postfix fired inside Multiplayer's
   freeze. It does not — `PatchGravshipTakeoffEnded`'s prefix lifts the freeze before
   `TakeoffEnded`'s body runs **[V]** — and the seam was changed rather than tested. See
   **T-78**.)*
4. **That a `TraceEffect_Incident`-gated `IncidentDef` is actually suppressed.** The
   donor's prefix on `CanFireNow` is **[V]**; that our registration runs before the
   first storyteller interval is **[I]**.

**Observable checks that demonstrate the requirements are satisfied:**

- Hacking an isolated door authored `Local` moves Trace by zero; hacking a Glitterite
  reactor authored `Network` moves it, and the amount was legible on the reactor's
  inspect string *before* the hack started.
- A quest offering a Trace reduction shows a Trace row in the quest-choice list before
  acceptance, next to an Intel row on the alternative approach.
- Crossing a band sends one letter listing exactly the effects that changed, and
  reloading the save sends none.
- The pursuit countdown is absent until the reveal, then lengthens when Trace falls
  and shortens when it rises, without a reload.
- A short gravship hop does not reset the countdown. A long one resets the countdown
  and **leaves Trace where it was** — visible in the same window, in the same frame.
- Raising Trace to maximum leaves an ordinary raid's size unchanged
  ([`PRESSURE.md`](PRESSURE.md) Verification check 5).

---

## Outstanding decisions

| Question | Consequence | Owner |
|---|---|---|
| **Every number** — band thresholds, decay, the `intrusionRows` columns, search rate curve, reveal point, escape distance, both raid factors | Balance. Nothing structural depends on any of them. | Balance, fog on [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2) |
| **Which target defs are authored `Network` / `Command`** | Decides what actually raises Trace. The mechanism does not depend on the answer. | Authoring, alongside [`HACKING.md`](HACKING.md)'s `HackTargetClass` catalogue ([#47](https://github.com/cjd721/Rimworld-Archinity/issues/47)) |
| **Does deep analysis raise Trace?** `GLITTERTECH.md` names *"deep analysis"* among the things that teach the Glitterites, but no mechanism reports an analysis. `CompUseEffect_GainCurrency` ([`CURRENCIES.md`](CURRENCIES.md) Credit B) is the obvious place to add a Trace field. | One extra field on a comp that is already in the budget, or the clause goes unimplemented. | **Requirements gap, no ticket** → [`docs/requirements/GLITTERTECH.md`](../requirements/GLITTERTECH.md) |
| **Does the pursuit reach an orbital home?** `QuestPart_ThreatsGenerator` needs a `mapParent` with a map, and **T-48** narrows the legal `IncidentDef` set drastically on an orbit layer. The pursuit's own defs need `layerWhitelist`. | The late-Ultra act is where pursuit matters most, and it is exactly where incidents silently stop. | This document flags it; [`PRESSURE.md`](PRESSURE.md) § *Failure and recovery* owns the T-48 sweep, and [`ORBIT.md`](ORBIT.md) owns the layer |
| **Which tile counts as "the colony's" when two player home maps exist.** `CurrentSettledTile()` reads the home map holding a grav engine, falling back to `Find.AnyPlayerHomeMap`. [#23](https://github.com/cjd721/Rimworld-Archinity/issues/23) settled one player faction and one colony, so this is inert until the gravship creates a second map — and the orbital act is exactly when it stops being inert. | A wrong answer makes a relocation read as an escape, or the reverse. | [`ORBIT.md`](ORBIT.md) owns the layer; flagged here. |
| **The pressure-stat name.** [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56) leaves *Trace* as the working name with *Visibility* acceptable. | Naming only. **Recommend Trace**, because *Visibility* is the donor's word for a different fiction and reusing it invites the reader to assume the donor's behaviour. | Conrad |
