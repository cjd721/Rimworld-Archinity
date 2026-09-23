# Trace and the Glitterite pursuit

## Purpose and scope

Implements [`docs/requirements/GLITTERTECH.md`](../requirements/GLITTERTECH.md)
§ *Trace — The Glitterites Learn You Back* and
[`docs/requirements/PRESSURE.md`](../requirements/PRESSURE.md) § *Glitterite pursuit*
(rules 1–7). Established by
[#56](https://github.com/cjd721/Rimworld-Archinity/issues/56).

**This document owns** the Trace number, its bands, what raises and decays it, the
search-progress meter that runs beside it, the relocation rule that resets search,
the pursuit quest, and every surface on which the player reads any of the above.
Glitterites are never hack targets (`GLITTERTECH.md` § *A captured Glitterite*), so no
android-target hack feeds Trace.

**Adjacent systems take over at five boundaries.**

| | |
|---|---|
| **What a hack reports** | [`HACKING.md`](HACKING.md) § *The intrusion report*. It emits every intrusion, including `Local` ones, flagged; the function from report to Trace increment is here. |
| **How big a raid is, and how it is authored** | [`PRESSURE.md`](PRESSURE.md). It says how threat strength is composed; this document says what starts a pursuit raid and when. **Trace never enters `DefaultThreatPointsNow`** — see § *Why Trace cannot multiply with Reverence*. |
| **The balance that pays for a Trace-reducing quest** | [`CURRENCIES.md`](CURRENCIES.md). Trace is a band ladder, not a balance, and lives in its own component. |
| **The shop window the readout sits in** | [`CURRENCIES.md`](CURRENCIES.md) § *Where the player sees it*, D1. This document adds one header row to a window that document already builds. |
| **Cross-cutting political-UI layout** | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (build map). Every surface has a route ([#61](https://github.com/cjd721/Rimworld-Archinity/issues/61)); tab shape and placement are the build map's. This number's readout is here. |

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
convention.** `GLITTERTECH.md` § *Trace* says *"Simple local hacks—such as a basic isolated
door—need not matter. Network-level hacks of mechanoids, reactors, command systems and
defenses do."* `HACKING.md` makes `depth` **a property of the target,
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

**Raise C — an artifact is analysed.** Destructive Glitterite analysis calls `Notify_Trace` from the synced tick, at start, per increment or at completion, as [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117) decides. The carrier is [`RESEARCH.md`](RESEARCH.md) § *Destructive artifact analysis* ([#115](https://github.com/cjd721/Rimworld-Archinity/issues/115)). Its writer is in § *Multiplayer*'s table.

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

`Find.WorldGrid.TraversalDistanceBetween(PlanetTile, PlanetTile)` is layer-aware **[V]**.
It is not the number the player sees at launch: `GravshipUtility.TryGetPathFuelCost`
**projects** a cross-layer origin with `GetClosestTile_NewTemp` *before* measuring, and
the launch UI shows a chemfuel cost rather than a tile count **[V]** (§ *Planet↔orbit as a
qualifying relocation* › *Legibility*,
[#150](https://github.com/cjd721/Rimworld-Archinity/issues/150)). Across a layer change
the unprojected call here returns `int.MaxValue`, which is what makes rule 1's last
sentence hold for free.

**A qualifying relocation is a move of the colony's base**
([`docs/requirements/PRESSURE.md`](../requirements/PRESSURE.md) § *Glitterite pursuit*,
rule 1): by gravship, or by caravanning out, founding a new settlement and abandoning the
old. A short move still grants no fresh safe window, and a move between two places in
orbit counts the same way, past its threshold (§ *Planet↔orbit as a qualifying
relocation*, Route C). The tick comparison above registers any change of settled tile,
however it was made, so the caravan case needs nothing further **[I]**.

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
> **A postfix on `GravshipUtility.TravelTo(Gravship, PlanetTile oldTile, PlanetTile
> newTile)`** has both tiles. **Rejected on two independent
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

Six surfaces. Four are free or nearly so, and **the per-intrusion risk readout (D3) is
ten lines on a patch [`HACKING.md`](HACKING.md) already writes.** PRESSURE's player-information
rules ask that pressure be broadly understood and relocation distance legible; D3 is
optional, and no requirement names it.

**D1 — the band, in the network window.** One header row in the currency window(s)
[`CURRENCIES.md`](CURRENCIES.md) builds: band icon,
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

**D3 — the risk of *this* intrusion, before committing to it — optional; no requirement
names it.** A per-target readout, not a letter afterwards.
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
| D1 band row in the currency window ([`CURRENCIES.md`](CURRENCIES.md) § *The purchasable quest catalogue*) | new C# | ~40 | `Source/CurrencyUI.cs` |
| D3 inspect-string addition to the existing `CanHackNow` postfix | patch | ~10 | `Source/Patches.cs` |
| D6 — one more row on an existing postfix | patch | ~5 | `Source/Patches.cs` |
| **Total new C#** | | **~645** | one assembly |
| One `TraceDef` + three `TraceBandDef`s + every effect | **XML** | ~180 | `Archinity.Glitterites/Defs/Trace/` |
| The pursuit `QuestScriptDef` — the search part, the detection raid, the threats generator, the reveal letter, signals and text | **XML** | **~400** | same |
| The detection `IncidentDef`, `Arch_IntrusionDepthExtension` on every target def, `layerWhitelist` on our own pursuit/threat defs (**T-48**) — the general orbital pack is [`GRAVSHIP.md`](GRAVSHIP.md) § *Ordinary colony life on an orbital home*, Route A | **XML** | ~120 | `Archinity.Glitterites/Patches/` |
| **Total XML** | | **~700** | |

> Royalty's `Script_EndGame_RoyalAscent.xml` — the shipped quest that does roughly what
> the pursuit quest must do — is ~400 lines on its own **[V]**, and it does not also carry
> a band ladder or an intrusion-depth patch set.

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
as the pursuit — aggression taxed twice. Either can be built: a per-entry opt-out is ~2
lines. Exchange prices and Trace exposure are
[#117](https://github.com/cjd721/Rimworld-Archinity/issues/117)'s (`CURRENCIES.md`
§ *Outstanding decisions*).

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
| destructive analysis (Raise C) | `IThingStudied.OnStudied` → job tick | the job |
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
`PatchGravshipTakeoffEnded` closes. **T-78** is the register entry, scoped to the
asymmetry rather than to vanilla.

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

## Planet↔orbit as a qualifying relocation

Answers [`docs/requirements/PRESSURE.md`](../requirements/PRESSURE.md) § *Glitterite
pursuit* rule 1's last sentence and
[`docs/requirements/SPACE.md`](../requirements/SPACE.md) § *Living in orbit* —
*"a jump between the planet and orbit, in either direction, always qualifies"*.
Established by [#150](https://github.com/cjd721/Rimworld-Archinity/issues/150), which
re-read [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56)'s scribed-tile
claim. Evidence class **READ**.

**This section owns only whether the move counts.** Whether the pursuit's raid can
reach an orbital home once it does is the **T-48** row in § *Outstanding decisions*;
ordinary life on an orbital home, and the general orbital whitelist, is
[`GRAVSHIP.md`](GRAVSHIP.md) § *Ordinary colony life on an orbital home*
([#147](https://github.com/cjd721/Rimworld-Archinity/issues/147)).

### Verdict

- **Possible? Yes — and it already holds, by an argument default rather than by design.**
  `RimWorld.Planet.WorldGrid.TraversalDistanceBetween(PlanetTile start, PlanetTile end,
  bool passImpassable = true, int maxDist = int.MaxValue, bool canTraverseLayers = false)`
  returns **`int.MaxValue`** when `start.Layer != end.Layer` and `canTraverseLayers` is
  false **[V]**. **The escape rule** (inside § *The search meter and the pursuit*) calls
  it with default arguments, so a planet↔orbit move already returns a distance no
  `escapeDistanceTiles` can fail to clear.
- **Multiplayer? Yes**, for every route but D. The comparison is on `WorldComponentTick`,
  inside `DoSingleTick` and synced (`docs/engine/determinism.md`); the grid call draws no
  `Rand`, its static cache is keyed on both `PlanetTile`s **including the layer**, and
  routes A–C never call `PlanetLayer.GetClosestTile_NewTemp`.

**#56's scribed-tile claim holds, and holds better than it was stated.**
`RimWorld.Planet.PlanetTile` is a `readonly struct` carrying `public readonly int tileId`
and `private readonly int layerId`, `ToString()` emits `"{tileId},{layerId}"`, and
`Verse.ParseHelper.ParsePlanetTile` registers `PlanetTile.TryParse` as the reader
**[V]**. `lastSettledTile` therefore
round-trips its layer through a save, by the same mechanism
`RimWorld.Planet.WorldObject.ExposeData` uses for `Scribe_Values.Look(ref tile, "tile")`
**[V]**. And the orbital map really does carry an orbit-layer tile:
`RimWorld.GravshipUtility.ArriveNewMap` sets `mapParent.Tile = destinationTile` and makes
`destinationTile.LayerDef.DefaultWorldObject`, while `Verse.MapInfo.Tile => parent?.Tile`
and `Verse.Map.IsPlayerHome` returns true outright for `wasSpawnedViaGravShipLanding`
**[V]**.

> **`PlanetTile.Equals` is not a plain both-fields compare, and the qualifier matters.**
> It returns false immediately on differing `tileId`, true immediately on equal
> `layerId` — and where the `layerId`s differ it returns true anyway **if both sides are
> negative-or-root-surface** (`layerId < 0 || Layer.IsRootSurface`, on each side)
> **[V]**. So two surface tiles with different `layerId` encodings still compare equal,
> which is what makes the implicit `int` → `PlanetTile` conversion safe on the surface.
> Surface-versus-orbit is unaffected, because `Orbit` is neither negative nor the root
> surface **[V]** — but "`Equals` compares both fields" would be the wrong summary to
> build anything else on.

**The four cases are distinguishable from the return value — with one asymmetry.**
A finite value rules a layer change out; `int.MaxValue` does **not** rule one in.

| Move | `TraversalDistanceBetween` returns |
|---|---|
| No move | `0` — `start == end` short-circuits |
| Ordinary tile move, same layer | a finite flood-fill distance |
| Gravship hop, same layer | the same finite distance |
| **Planet↔orbit, either direction** | **`int.MaxValue`** — the branch tests layer *inequality*, so it is symmetric |

> **`int.MaxValue` has four sources and only one of them is a layer mismatch** **[V]**:
> either tile invalid; `start.Layer != end.Layer && !canTraverseLayers`;
> `!passImpassable && !Find.WorldReachability.CanReach(start, end)`; and a flood fill
> that never reaches `end` (which also covers a `maxDist`-bounded call, since `finalDist`
> is initialised to `int.MaxValue`). Three of the four are layer-independent. **The
> escape rule** calls with `passImpassable` and `maxDist` at their defaults, which
> retires the third — but not the first or the fourth. **Route A's guarantee is that a
> layer change always produces `int.MaxValue`, never the converse.**

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **A** | The guarantee, for nothing — the call the escape rule (§ *The search meter and the pursuit*) already makes returns `int.MaxValue` across layers | vanilla — `WorldGrid.TraversalDistanceBetween` | already in the design | Easy (zero) | Yes |
| **B** | The same guarantee **stated** — an explicit `from.Layer != to.Layer` branch ahead of the distance test | our code, reading `PlanetTile.Layer` / `.LayerDef` | C# | Easy | Yes |
| **C** | A threshold that means the same thing on each layer, so orbit→orbit reads sensibly | `TraceDef` XML keyed by `PlanetLayerDef` | XML | Easy | Yes |
| **D** | The move seen in the landing frame, both endpoints unprojected | `WorldComponent_GravshipController.takeoffTile` + `Gravship.destinationTile` | C#, Harmony | Medium | **With work** — **not recommended** |

A, B and C are independent decisions rather than alternatives; B and C compose on A.
**Recommended: A plus B plus C** — A is free, B makes the rule findable and removes
Route A's two failure modes below, C is the only one that answers orbit→orbit.
**Nothing is selected here.** Every route composes individually-**[V]** mechanisms; that
they compose into the required behaviour is **[I]**.

**Route A — what it gets us.** Rule 1's last sentence is satisfied today with no branch
and no new field. In order, `TraversalDistanceBetween` short-circuits on `start == end`
(→ `0`), then on either tile invalid (→ `int.MaxValue`), **then reads its static cache**,
then on `start.Layer != end.Layer && !canTraverseLayers` (→ `int.MaxValue`), then on
`!passImpassable && !CanReach`, and only then flood-fills inside the end layer **[V]**.

**What it cannot do, and this is the part worth writing a beat around.**

- **`int.MaxValue` does not mean "layer change".** Three of its four sources are
  layer-independent — see the box above. No letter, tooltip or message can be worded
  from the number.
- **The cache is read *before* the layer guard, and a cross-layer entry can be finite.**
  The hit condition is
  `cachedTraversalDistanceForStart == start && cachedTraversalDistanceForEnd == end &&
  cachedLayer == end.Layer && passImpassable && maxDist == int.MaxValue`, and on a
  `canTraverseLayers: true` cross-layer call the function sets `cachedLayer = end.Layer`,
  projects, and then writes the cache under the **original, unprojected** start
  (`planetTile`, saved before the reassignment) **[V]**. So one such call on an ordered
  pair leaves a **finite** cross-layer distance that every subsequent *default* call on
  the same pair will return, ahead of the guard, until a different pair overwrites it.
  **The sweep does not bound this:** `canTraverseLayers` returned zero mod hits, but a
  positional `true` leaves no string in any metadata heap, so the negative is evidence
  about the *identifier*, not about callers. No vanilla caller passing `true` was found —
  `TryGetPathFuelCost` pre-projects instead **[V]** — which makes the path unarmed in
  shipped code today and one mod away from armed. **Route B is immune, because its
  branch runs before the call.**
- **The guarantee is held by an optional argument nobody wrote.** Adding
  `canTraverseLayers: true` — the obvious move if someone later wants a *readable*
  number — silently inverts it: the function then projects `start` onto the end layer
  with `GetClosestTile_NewTemp` and flood-fills from the projection **[V]**, so
  surface→orbit measures a near-zero distance and **stops qualifying, with no error** —
  and, per the bullet above, poisons the cache for the default callers too.
  It is the same footgun that disqualified the `TravelTo` postfix, relocated into the
  function this document kept. Proposed as a new trap on
  [#150](https://github.com/cjd721/Rimworld-Archinity/issues/150).
- **`int.MaxValue` is arithmetic poison.** Safe under `>=`; any later `d - x`, `d * f`
  or `SimpleCurve.Evaluate(d)` overflows or reads off the end of the curve.

**Route B — an explicit layer branch.** Puts the rule where a reader finds it and makes
it immune to any later change to the distance call. It also gives the story a *named
event* — "we left the planet", distinct from "we moved far" — which is what a letter or a
quest signal has to be worded from. `PlanetTile.Layer` and `.LayerDef` are public reads
with no side effects **[V]**.

> **Variant B′, because vanilla ships the case.** Branch on `LayerDef.isSpace` changing
> rather than on layer identity. `PlanetLayerDef.isSpace` is a real field; Odyssey's
> `Orbit` sets it `true` and `Surface` does not **[V]**. Odyssey also ships a
> **commented-out `Moon` layer** in `Data/Odyssey/Defs/PlanetLayerDefs/PlanetLayers.xml`
> and its settings file, `layerType SurfaceLayer` **[V]** — the shipped, XML-only
> template for adding a layer. Under plain `Layer !=` a hop to a moon surface escapes
> for the same reason orbit does; under `isSpace`, only entering or leaving space does.
> The engine supports either reading at identical cost (§ *Outstanding decisions*).

**Route C — the per-layer threshold, and the answer to orbit→orbit.** Two orbital tiles
are on the same layer, so the distance test behaves normally there — but **a "tile" is
not the same size on the two layers**, so one `escapeDistanceTiles` cannot mean the same
thing on both. Vanilla faces the same problem and solves it by division:
`RimWorld.CompPilotConsole.GetMaxLaunchDistance(PlanetLayer layer)` is exactly
`engine.MaxLaunchDistance / layer.Def.rangeDistanceFactor`, and Odyssey's `Orbit` sets
`rangeDistanceFactor 20` **[V]**.

> **Do not derive the threshold from that factor.** `rangeDistanceFactor 20` is Odyssey's
> **fuel** calibration against Odyssey's orbit grid — `radius 130 / subdivisions 5`
> **[V]** — and **we have already replaced that grid.**
> `Archinity.Pacing/Patches/Orbit_LayerSize.xml` is a live `PatchOperationReplace` of
> `PlanetLayerSettingsDef[defName="Orbit"]/settings/subdivisions` from `5` to `6`
> **[V]**, which its own comment puts at 2,432 → 7,292 tiles. Orbit tiles therefore run
> roughly √3 finer than the ones `20` was chosen for, and any threshold derived from
> `rangeDistanceFactor` inherits that error silently. Worse, **T-45** makes our patch
> worldgen-only — `PlanetLayer.InitializeLayer` rebuilds from scribed values — so *which*
> grid a given save has depends on when its world was made. **A threshold derived from
> grid geometry is not stable across our own saves.**
>
> So Route C is the **explicit** form: a `List` on `TraceDef` keyed by `PlanetLayerDef`,
> authored per layer. Same weight, no derived constant, and it does not assume the fuel
> ratio is the right ratio for a *pursuit*. The `÷ rangeDistanceFactor` shorthand is
> recorded here as vanilla's precedent for the *shape* of the answer, not as the number.

**The corpus is both Steam roots plus this repo.** No mod in either Steam root adds a
`PlanetLayerDef` or `PlanetLayerSettingsDef` **[V]**, but `Archinity.Pacing` replaces the
orbit grid (above), so not every planet layer in play is vanilla's.

**Route D — observing the travel event, and why not.** Both endpoints are there and
unprojected: `Verse.WorldComponent_GravshipController.takeoffTile` and
`RimWorld.Planet.Gravship.destinationTile` are `PlanetTile`s carrying their layers, both
survive the landing, both are `Scribe_Values`-persisted **[V]**. It is the only route
that fires in the landing frame rather than on the next world tick. Three verified counts
against it: **T-78** (`Multiplayer.Client.Patches.PatchGravshipTakeoffEnded` is a prefix
calling `GravshipTravelUtils.StopFreeze()`, so code hung there runs unfrozen and unseeded
**[V]**); the seam is contested — Vanilla Gravship Expanded patches `InitiateTakeoff`,
`TakeoffEnded` and `LandingEnded`, RimPacts patches the landing, Multiplayer patches both
ends, and MP Compat's `Multiplayer.Compat.VanillaGravshipExpanded` postfixes VGE's own
prefix **[V]**; and `ScenPart.PostGravshipLanded(Map)` still takes only a `Map` **[V]**.

> **A determinism hazard this route inherits, recorded because it bounds every future
> route too.** `PlanetLayer.GetClosestTile_NewTemp` — the projection `TravelTo`,
> `TryGetPathFuelCost` and `CompPilotConsole` all call on a cross-layer move — resolves
> through `RimWorld.Planet.FastTileFinder.Closest`, a Burst-compiled parallel job.
> `FastTileFinder.ComputeQueryJob.CheckClosest` keeps a per-thread minimum with a strict
> `<`, and `FastTileFinder.TryGetClosest` reduces the thread slots with a strict `<`
> **[V]**. Which index wins an exact squared-distance tie therefore depends on how the
> job partitioned tiles across threads — a machine property. Exact ties on a symmetric
> icosahedral grid are plausible **[I]**. **Routes A–C never call it.** Proposed as a
> trap on [#150](https://github.com/cjd721/Rimworld-Archinity/issues/150).

### Legibility

Requirements rule 1 asks that *"relocation distance requirements must be legible so a
short hop is an informed risk."* The number the player sees at launch is not the number
the relocation test reads, and the gap is widest on a layer change.

`RimWorld.GravshipUtility.TryGetPathFuelCost` **projects first and measures second**: on
`from.Layer != to.Layer` it does `from = to.Layer.GetClosestTile_NewTemp(from);` and only
then calls `Find.WorldGrid.TraversalDistanceBetween(from, to)` **[V]**. Same function,
different call. For a surface→orbit launch the UI's `distance` is the projected
same-layer hop — small — while the relocation test's unprojected call returns
`int.MaxValue`.

**And the player is shown no tile count at launch at all.**
`RimWorld.CompPilotConsole.StartChoosingDestination_NewTemp`'s mouse-attached label
prints `"Cost": "FuelAmount"(cost, Chemfuel)` plus at most a *beyond maximum range*
clause, and `GenDraw.DrawWorldRadiusRing` draws the range rings around the **projected**
tile when the selected layer differs **[V]**. The only tile number on screen is the pilot
console's inspect line `"GravshipRange": GetMaxLaunchDistance(parent.Map.Tile.Layer)`
**[V]**.

**Consequence for D5.** `QuestPart_TraceSearch.ExpiryInfoPartTip` carrying a raw
`escapeDistanceTiles` figure is comparable to nothing the player sees while choosing a
destination. For a **same-layer** move the legibility argument survives in weaker form —
the fuel cost is monotonic in the distance the test reads. For a **layer change** the
tooltip must state the *rule* — leaving the planet always breaks contact — rather than a
number, because there is no number on either side to compare.

### Carriers, and what the corpus does not have

- **No mod in either Steam root adds a `PlanetLayerDef` or `PlanetLayerSettingsDef`.**
  An XML sweep for both tags across both roots returned zero; the validator `<ThingDef`
  in the identical form matched 4,351 mod files **[V]**. **But the layers in play are not
  all vanilla's:** `Archinity.Pacing/Patches/Orbit_LayerSize.xml` replaces the orbit
  layer's `subdivisions` with `6` **[V]**, and this repo is outside the roots the sweep
  covered. See Route C.
- **`canTraverseLayers`, `IsRootSurface`, `ScenPart_PlanetLayer` and
  `PostGravshipLanded` have zero mod hits** across both roots — `-a -g '*.dll'
  -g '!**/obj/**' -g '!**/Referenced/**'`, ASCII plus a null-interleaved `#US` pass with
  the `\x00` escapes typed literally, each negative validated against the same pattern
  form run on `Assembly-CSharp.dll` **[V]**.
- **VFE Deserters, the band ladder's donor, does not touch this half at all.**
  `VisibilityLevelDef` lives in exactly one assembly, `3025493377/1.6/Assemblies/VFED.dll`,
  and that assembly carries **zero** `PlanetLayer` and **zero** `Gravship` references
  **[V]**. The ladder is worth copying; the relocation test has no donor to copy.
- **No vanilla quest part fires on a layer change.**
  `RimWorld.QuestPart_RequirementsToAcceptPlanetLayer` gates *acceptance* only, and
  `WorldGrid.OnPlanetLayerAdded` / `OnPlanetLayerRemoved` are layer-lifecycle events, not
  move events **[V]**.
- **Multiplayer already treats gravship travel as a synced, tile-keyed session.**
  `Multiplayer.Client.Persistent.GravshipTravelSession` holds a `PlanetTile InitialTile`;
  the takeoff patch closes the session at `takeoffTile`, the landing patch at
  `gravship.destinationTile` and restores `Rand` from `map.AsyncTime().randState` **[V]**.
  Multiplayer's own `PlanetLayer` references are the cross-layer ping feature and world
  draw layers — display, not travel **[V]**.
- **Layer 0 is the Surface in every vanilla-derived scenario.**
  `WorldGrid.CreateRequiredLayers` iterates `RimWorld.Scenario.AllParts`, which yields
  `playerFaction`, then `surfaceLayer`, then `parts`, and `ScenarioBase` puts `Orbit` in
  `parts` **[V]**. This matters because `PlanetTile`'s implicit `int` conversion produces
  `layerId = 0`: **any tile that round-trips through a bare `int` silently lands on layer
  0**, which is benign only because layer 0 happens to be the surface.

---

## Failure and recovery

| Failure | Detection | Recovery |
|---|---|---|
| A `TraceBandDef` leaves the load order, or its range is edited | **Loud on the next load** — the band walk finds no band whose `traceRange.max >= trace` | The walk must not leave `band` null. A startup validator asserting that the shipped `traceRange`s tile 0..100 with no gap and no overlap is ~15 lines and converts a null-band crash into a config error. **This is the one place the donor's design is genuinely fragile: its walk has no fallback** **[V]**. |
| Trace and search disagree — search completes while Trace is 0 | Visible: a pursuit raid with no readout to explain it | Not a bug. Rule 4 is explicit that reducing Trace *"cannot undo progress already made"*, and rule 6 that *"reducing Trace after detection does not conceal the location."* The `ExpiryInfoPartTip` must say so. |
| The pursuit quest ends (declined, failed, cleaned up) and search is orphaned | `searchProgress` lives on the quest part, so it dies with it | Correct by construction, but it means **the pursuit quest must not be dismissible**. Author it auto-accepted with no `QuestPart_Choice`; `Quest.dismissed` only hides a row, it does not end a quest **[V]**. |
| A short relocation is mistaken for an escape | **Silent** — the player believes they got away | Prevented rather than recovered: the threshold is a `TraceDef` field, stated in `ExpiryInfoPartTip`. The launch UI shows a chemfuel cost, not a tile count, and it **projects** a cross-layer origin before measuring **[V]** ([#150](https://github.com/cjd721/Rimworld-Archinity/issues/150)). For a same-layer move the fuel cost is still monotonic in the distance we test; for a layer change there is no comparable number and the tooltip must state the rule. See § *Planet↔orbit as a qualifying relocation* → *Legibility*. |
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
| **Corrected since the first resolution** | The relocation seam moved from a `GravshipUtility.TravelTo` postfix to a `WorldComponentTick` tile comparison, for two verified reasons: `TravelTo` reassigns its own `oldTile` parameter on a cross-layer move, and `TakeoffEnded` runs **after** Multiplayer lifts its freeze and with no `Rand` wrapper (**T-78**). |
| **Confirmed negative** | **Odyssey's gravship pursuit does not carry the required behaviour.** See *Available mechanisms*. |
| **Proposed, not selected** | The whole build above. **[I]** as a composition, and the line estimates with it. |
| **Open parameters** | Every number: band thresholds, decay rate, the four `intrusionRows` columns, `searchRatePerDayByTrace`, `revealAtSearchProgress`, `escapeDistanceTiles`, both `currentThreatPointsFactor`s. Balance, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119). |

---

## Available mechanisms

### Odyssey's gravship pursuit — read and declined as a carrier

`docs/requirements/PRESSURE.md` § *Glitterite pursuit* once named this as the preferred
provider; it now names none and cites this section. The verdict is **repoint, not
reuse**.

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
| `VisibilityEffect_Goodwill` → a random faction −10 per `TickDay` | **REJECT.** `GLITTERTECH.md` § *Strongholds* says the Glitterites are *"hostile to everyone and outside normal diplomacy"*; a pursuit that moves human goodwill contradicts it. |
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
| `WorldComponent_GravshipController.takeoffTile` / `landingTile` **[V]** | both `Scribe_Values`-persisted (`"takeoffTile"`, `"targetTile"`), untouched by `ResetCutscene`, reachable by `AccessTools.Field` | **Not needed** — the tick comparison reads the settled tile directly. |
| `WorldGrid.TraversalDistanceBetween` / `ApproxDistanceInTiles` **[V]** | tile distance, layer-aware; `TraversalDistanceBetween` is what `GravshipUtility.TryGetPathFuelCost` uses | **Adopted** — layer-aware; the unprojected call returns `int.MaxValue` across layers. It is not the number the launch UI shows (§ *Planet↔orbit as a qualifying relocation* › *Legibility*). |
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
4. **That a `TraceEffect_Incident`-gated `IncidentDef` is actually suppressed.** The
   donor's prefix on `CanFireNow` is **[V]**; that our registration runs before the
   first storyteller interval is **[I]**.

**Observable checks that demonstrate the requirements are satisfied:**

- Hacking an isolated door authored `Local` moves Trace by zero; hacking a Glitterite
  reactor authored `Network` moves it (and, if D3 is built, the amount shows on the
  reactor's inspect string *before* the hack starts).
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
| **Every number** — band thresholds, decay, the `intrusionRows` columns, search rate curve, reveal point, escape distance, both raid factors | Balance. Nothing structural depends on any of them. | Balance, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) |
| **Which target defs are authored `Network` / `Command`** | Decides what actually raises Trace. The mechanism does not depend on the answer. | Authoring, alongside [`HACKING.md`](HACKING.md)'s `HackTargetClass` catalogue ([#47](https://github.com/cjd721/Rimworld-Archinity/issues/47)) |
| **Does the pursuit reach an orbital home?** `QuestPart_ThreatsGenerator` needs a `mapParent` with a map, and **T-48** narrows the legal `IncidentDef` set drastically on an orbit layer. The pursuit's own defs need `layerWhitelist` (§ *Cost*). | The late-Ultra act is where pursuit matters most, and it is exactly where incidents silently stop. | This document whitelists its own pursuit defs; the general orbital pack and life on an orbital home are [`GRAVSHIP.md`](GRAVSHIP.md) § *Ordinary colony life on an orbital home* ([#147](https://github.com/cjd721/Rimworld-Archinity/issues/147)) |
| **Which tile counts as "the colony's" when two player home maps exist.** `CurrentSettledTile()` reads the home map holding a grav engine, falling back to `Find.AnyPlayerHomeMap`, and scribes one tile. [#23](https://github.com/cjd721/Rimworld-Archinity/issues/23) settled two colonies on two separate tiles, so two home maps exist from the second colony's founding, and the pursuit can run while both stand. | A wrong answer makes a relocation read as an escape, or the reverse. | Capability: [#186](https://github.com/cjd721/Rimworld-Archinity/issues/186) — whether the pursuit can track each colony separately, only one, or both as one target, and by which routes |
| **How far an orbit→orbit move must go.** A move between two places in orbit shakes the pursuit the same way a move on the planet does (`PRESSURE.md` § *Glitterite pursuit*, rule 1). An orbit "tile" is not a surface tile, so the threshold must be **authored per layer rather than derived** — `Archinity.Pacing` already replaces the orbit grid Odyssey's own `rangeDistanceFactor 20` was calibrated against, and **T-45** makes that replacement worldgen-only. | The late-Ultra act is entirely in orbit, so this is the threshold that will actually be tested. | Capability: § *Planet↔orbit as a qualifying relocation*, Route C (a threshold per layer). The number: balance, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) |
| **Layer identity, or `isSpace`?** If a second *surface* layer is ever added — Odyssey ships a `Moon` template commented out, XML-only **[V]** — hopping to it qualifies under layer identity and not under `isSpace`. | Decides whether "escape" means *left the planet* or *left this world*. Nothing structural depends on the answer. | Capability: Route B (layer identity) or B′ (`isSpace`), both **[V]**, same cost (§ *Planet↔orbit as a qualifying relocation* › *Routes*). Which ships is the build map's |
