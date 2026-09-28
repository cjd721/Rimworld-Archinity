# Era

## Purpose and scope

**What the campaign's era is, where it is stored, and how long the colony has been in it.**

Everything in the campaign hangs off the era, and until this document existed nothing owned
it. [#7](https://github.com/cjd721/Rimworld-Archinity/issues/7) resolved the *mechanism choice*
— World Tech Level for the ceiling, Ignorance Is Bliss for the band, one operation of ours for
the advance — and then closed. [#60](https://github.com/cjd721/Rimworld-Archinity/issues/60)
built [`PRESSURE.md`](PRESSURE.md)'s threat-point composition on **capped time within the
current era**, could find no document holding that number, and recorded it as an ownerless gap.
[`PRESSURE.md`](PRESSURE.md) and the progression grids
([#30](https://github.com/cjd721/Rimworld-Archinity/issues/30),
[#34](https://github.com/cjd721/Rimworld-Archinity/issues/34)) read it. This document is
that owner ([#109](https://github.com/cjd721/Rimworld-Archinity/issues/109)).

This document owns:

- the **era clock** — the current era, the tick each era began, and the retained history of
  every boundary crossed;
- **`AdvanceEra()`** — the single operation that raises the era, what it writes, from where,
  and why it is the only writer;
- the **persistence contract** every other spec reads through, and what a save that predates
  the clock sees;
- the **second writers** that must be shut off, and the multiplayer consequences of each;
- **which clock the era runs on** under Multiplayer Async Time with two colonies — § *An era's
  start under Async Time* ([#185](https://github.com/cjd721/Rimworld-Archinity/issues/185));
- whether **above-era structures and events seeded on the player's own map** can be removed,
  timed to their era or replaced, and by which routes — § *Above-era content seeded on the
  player's own map* at the end of this document
  ([#153](https://github.com/cjd721/Rimworld-Archinity/issues/153)).

It does **not** own: how long an era *should* last, or what era time is *worth* — those are
balance, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119), and the era-length
table in [`docs/engine/world-time-and-layers.md`](../engine/world-time-and-layers.md) § *Time*
is campaign design input rather than an engine fact. It does not own **what the capstone is**
or what research it requires ([`RESEARCH.md`](RESEARCH.md) and
[#41](https://github.com/cjd721/Rimworld-Archinity/issues/41)). The capstone's completion
is the trigger ([#113](https://github.com/cjd721/Rimworld-Archinity/issues/113) settled it);
the advance is always the players' choice, and a rite or build performed with the capstone is
a route ([`docs/requirements/ERA.md`](../requirements/ERA.md) § *Player information and
agency*; choice [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)). This document
owns the hook that turns that completion into the single `AdvanceEra()` call.
It does not own **what becomes available at each era**
([`docs/progression/`](../progression/README.md)), nor the **filter set** WTL runs (#7 froze
those twenty-four toggles and this document does not reopen them).
It does not own **the world re-authoring pass the advance triggers** — settlement swaps,
removals, shrinks and reveals. The mechanism is verified in
[`docs/engine/factions-and-worldgen.md`](../engine/factions-and-worldgen.md)
([#8](https://github.com/cjd721/Rimworld-Archinity/issues/8),
[#70](https://github.com/cjd721/Rimworld-Archinity/issues/70),
[#130](https://github.com/cjd721/Rimworld-Archinity/issues/130)); which factions is
[#34](https://github.com/cjd721/Rimworld-Archinity/issues/34)'s; the transfer shape and its
in-flight hazards are [`TERRITORY.md`](TERRITORY.md) § *A caravan en route when its destination
changes hands* and [`GRAVSHIP.md`](GRAVSHIP.md) § *A gravship en route when its landing tile
changes hands* (T-140). It is bound by [`docs/requirements/ERA.md`](../requirements/ERA.md)
§ *The era advance*: a single, indivisible act. The determinism rule is § 3's note on Lemmy's
`System.Random`.

**Consumers of the advance:** [`PRESSURE.md`](PRESSURE.md), [`docs/progression/`](../progression/README.md),
[`WORLD-INFRASTRUCTURE.md`](WORLD-INFRASTRUCTURE.md) § 3a, [`TERRITORY.md`](TERRITORY.md)
(T-145). AE-5(a) (unselected) would add a write.

---

## The build

**One `GameComponent` of ours holds the boundary log, WTL keeps holding the era itself, and
`AdvanceEra()` is a single method in the assembly we already ship that writes both in one
call.** No new XML, no new def type, no second store for a number vanilla or WTL already keeps.

### 0. A correction to what this ticket inherited

**`AdvanceEra()` does not exist.** It is #7's *design*, not shipped code. **The repository tracks
five `.cs` files** — `AltarData.cs`, `Building_Altar.cs`, `GenePool.cs`, `Patches.cs` and
`WorkGivers.cs`, all under `Archinity.Altar/Source/` [V, `git ls-files '*.cs'`] — **and none of
them declares it.** Every occurrence of the identifier in the tracked tree is prose in a
`docs/specs/` document: [`PRESSURE.md`](PRESSURE.md) § *The build* and § *Outstanding
decisions*, and now this file and [`RESEARCH.md`](RESEARCH.md). So #60's *"#7 resolved that
`AdvanceEra()` … stamps an era-start tick"* describes an intended write, not an observed one.
**This document specifies it; nothing has built it.**

Two of #7's load-bearing premises *do* survive re-reading, and are restated here as [V]:

- **WTL's scribed field is real and is a `GameComponent`.** `WorldTechLevel.GameComponent_TechLevel`
  holds one field, `private TechLevel _worldTechLevel`, exposed through a public
  `WorldTechLevel` property and scribed as
  `Scribe_Values.Look<TechLevel>(ref _worldTechLevel, "WorldTechLevel", TechLevel.Archotech)` [V,
  `…/294100/3414187030/1.6/Lunar/Components/WorldTechLevel.dll`, `WorldTechLevel.GameComponent_TechLevel.ExposeData`].
  It is the whole of WTL's saved state.
- **It is not the field the ~60 filter sites read.** They read the static property
  `WorldTechLevel.WorldTechLevel.Current`, which has **no persistence of its own** and is
  restored from the `GameComponent` by
  `Patch_WorldGenerator.GenerateFromScribe_Prefix` / `GenerateWithoutWorldData_Prefix` on every
  load [V]. **A writer that sets one and not the other is wrong**, and §3 shows the shipped mod
  that gets it wrong.

### 1. Mechanism — `GameComponent_Era`, and why a `GameComponent`

**`GameComponent`, not `WorldComponent`, and not a new def.** The decisive reason is that the
thing this clock must stay consistent with — the era itself — is already stored in a
`GameComponent` [V, above]. Splitting one fact across `Game.ExposeData`'s `components` node and
`World.ExposeData`'s `components` node buys nothing and creates a pair that can disagree across
a partial load. `GameComponent` also gives the two hooks this needs for free and on the synced
tick: `FinalizeInit` (post-load repair, §4) and `GameComponentTick` if a poll is ever wanted
[V, [`docs/engine/determinism.md`](../engine/determinism.md) § *What is on the synced tick*].

**The same question, asked of [`RESEARCH.md`](RESEARCH.md)'s granted-capability half
([#72](https://github.com/cjd721/Rimworld-Archinity/issues/72)), gets the opposite answer, and
the rule that produces both is one rule:**

> **Scribe only what nothing else scribes. Derive everything else.**

#109 owes a store because **nothing in the game or the corpus records when an era began** (§
*Available mechanisms*). #72 owes none, because whether a research project is finished is
already `ResearchManager.progress`, already scribed, already synced. Two stores for one fact is
the failure this rule exists to prevent; so is a store for a fact somebody else already keeps.

### 2. State — the boundary log, and prior eras are retained

```
GameComponent_Era : GameComponent
    List<EraBoundary> boundaries          // scribed
    // EraBoundary : IExposable { TechLevel era; int startTick; }

    TechLevel CurrentEra        => boundaries.Last().era
    int  CurrentEraStartTick    => boundaries.Last().startTick
    int  TicksInCurrentEra      => era-clock now - CurrentEraStartTick
    int  StartTickOf(TechLevel) => first boundary with that era, or -1
```

**`startTick` and "now" are read on the era clock, and the era clock is not
`Find.TickManager.TicksGame`.** Under Multiplayer Async Time that call returns whichever clock the
calling context installed — the researching colony's own map clock at a bench, the world clock in
`GameComponentTick` — so a stamp taken in one context and read in another is off by the drift
between colonies. Which clock the era runs on is § *An era's start under Async Time*; in
single-player every route reduces to `TicksGame`.

**Prior eras' boundaries are retained — all of them — and this is a design decision with a
consumer, not tidiness.** Two reasons, in order of force:

1. **[`PRESSURE.md`](PRESSURE.md)'s era term needs the whole history.** Its § *Verification*
   check 2 requires that points *"must not reset at the next `AdvanceEra()`"*, which a single
   `int EraStartTick` — resetting at every boundary — cannot satisfy. The sum

   > `eraTime = Σ over every boundary e of  cappedCurve( ticks spent in e )`

   climbs within an era, flattens at that era's ceiling, and **adds** rather than
   restarting at the seam — which is also #7 § 6's *"no reset and no spike at a boundary … the
   budget is continuous across the seam."* The retained log is what makes that sum computable,
   and PRESSURE.md § *The build* (era-time row) reads it this way
   ([#109](https://github.com/cjd721/Rimworld-Archinity/issues/109)).

   > **The balance consequence of the sum, named because the spec must not hide it.** Under
   > `Σ cappedCurve`, the era term's own ceiling is **five times a single era's cap** rather than
   > one era's — a five-era campaign that reaches every ceiling contributes five times what a
   > single-stamp reading would at the same moment. That is the intended shape (pressure
   > accumulates across the campaign rather than resetting), but it means the per-era cap must be
   > authored at roughly a fifth of whatever a single-stamp reading would have suggested.
   > **The number is balance**, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119);
   > this document owes only the warning that the unit changed.
2. **The progression grids ask "when did we enter era X", not "how long in this one".**
   [#30](https://github.com/cjd721/Rimworld-Archinity/issues/30) and
   [#34](https://github.com/cjd721/Rimworld-Archinity/issues/34) fill a column per era; a beat
   that wants *"180 days after the Medieval gate"* needs `StartTickOf(Medieval)` after the
   colony has left Medieval behind.

The cost of retaining is five rows of `(byte, int)` for a five-era campaign. `CurrentEraStartTick`
is supplied verbatim so that #60's stated requirement — *"a read-only `int EraStartTick` and the
current `TechLevel`"* — is satisfied without any consumer having to understand the log.

**The era itself stays in WTL's component.** `GameComponent_Era` does not duplicate it;
`CurrentEra` reads the last boundary and `FinalizeInit` asserts it equals
`WorldTechLevel.Current`, logging loudly on disagreement (§4). One number, one writer survives
#7 intact — what is added is a second *fact*, the tick, which had no writer at all.

### 3. Change — `AdvanceEra()`, four writes in one call

```
[SyncMethod-equivalent: see Persistence and multiplayer]
public void AdvanceEra(TechLevel next)
    guard: next == CurrentEra + 1, else Log.Error and return      // one-way, one rung
    1. Current.Game.GetComponent<GameComponent_TechLevel>().WorldTechLevel = next   // scribed
    2. WorldTechLevel.WorldTechLevel.Current = next                                 // volatile mirror
    3. Faction.OfPlayer.def.techLevel = next                                        // see T-11
    4. boundaries.Add(new EraBoundary(next, <start on the era clock>))              // § An era's start under Async Time
```

**Write 4 does not stamp the caller's `TicksGame`.** The capstone completes at a research bench,
inside the researching colony's map tick, where `TicksGame` is that colony's clock and no one
else's [V, `RimWorld.JobDriver_Research` toil `tickIntervalAction` → `ResearchManager.ResearchPerformed`;
`Multiplayer.Client.AsyncTimeComp.Tick`]. Stamping it would be **T-175** — a stored absolute tick read against whatever clock the reader is on. It opens the boundary on the era clock — a world count or
one per colony, § *An era's start under Async Time*.

Writes 1 and 2 are **both mandatory and the pair is the whole trap.** WTL's own
"Change tech level" button does exactly this pair [V,
`WorldTechLevel.Patches.Patch_WITab_Planet.FillTab_Postfix`, local function `SetLevel`], which is
the shipped proof that one is not enough.

**The shipped mod that gets it wrong, read rather than inherited.** Lemmy Progression
(`LemmyMods.LemProgression`, workshop `3548896697`,
`1.6/Assemblies/LemProgress.dll`) resolves the WTL type by `AccessTools.TypeByName` and writes
**only the static `Current`**, through `LemProgress.Systems.WorldEraManager.SetWorldTechLevel`
[V]. It scribes nothing of its own, so the raised level is discarded by
`Patch_WorldGenerator.GenerateFromScribe_Prefix` on the next load. Its faction-upgrade half
also draws from **two `System.Random` instances** (`LemProgress.Systems.FactionUpgradeManager`
and `LemProgress.Systems.FactionUpgrader` each hold a `private static readonly Random`) [V],
which is a guaranteed multiplayer divergence. Both defects are exactly as #7 described them;
both are confirmed against the 1.6 assembly.

**What Lemmy gets *right*.**
`WorldEraManager.InitializeWorldTechLevelAccess` handles the auto-property correctly and
explicitly: `AccessTools.Field(type, "Current")` → null → `AccessTools.Property(type, "Current")`
non-null → `AccessTools.Field(type, "<Current>k__BackingField")` → and, failing that, a
`GetFields(Static | Public | NonPublic)` scan for the first static `TechLevel` [V]. The engine
fact in *Cost* below is real and our shim must handle it; this mod does not trip over it. Its
defect is the missing second write, not the reflection.

**What calls it.** Completion of an authored era-capstone `ResearchProjectDef` calls
`AdvanceEra(next)` once. The project may be gated by any combination of prerequisites,
resources, exemplars or instruction. The advance is always the players' choice; a rite or a
build the players perform between completion and the call is a route
([`docs/requirements/ERA.md`](../requirements/ERA.md) § *Player information and agency*;
choice [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)), and a rite's
multiplayer chain is in § *Persistence and multiplayer*. The implementation must identify capstones explicitly, run on the synced
research-completion path (or a rite's outcome, where that route is taken), guard duplicate completion and
preserve the rule that `AdvanceEra()` has no other gameplay caller. A debug route still needs its own treatment.

**Reversible? No.** The guard rejects a downgrade and rejects a skip. There is no `RetreatEra()`
and the boundary log is append-only. Per `CODING_STANDARDS.md` § *The bar for a change*,
permanence is deliberately not a gate here.

### 4. Persistence, and the two post-load repairs

- **Scribing.** `Scribe_Collections.Look(ref boundaries, "boundaries", LookMode.Deep)`, with a
  `Scribe.mode == LoadSaveMode.PostLoadInit` null-guard reconstructing an empty list —
  the guard stage `AnalysisManager` uses, and the one
  [`RESEARCH.md`](RESEARCH.md) § *Persistence and multiplayer* already distinguishes from
  `LoadingVars`.
- **A save that predates the clock loads cleanly and silently.** `Game.ExposeData`'s
  `LoadingVars` branch calls `FillComponents()`, which walks
  `typeof(GameComponent).AllSubclassesNonAbstract()` and `Activator.CreateInstance(type, this)`
  for every subclass absent from the save [V, `Verse.Game.FillComponents`]. So the component
  appears with `boundaries` empty and **no error** — provided it declares a `(Game game)`
  constructor. Omitting that constructor is a `Log.Error`, i.e. loud, not silent.
- **The seed.** `FinalizeInit` seeds an empty log with a single boundary
  `{ WorldTechLevel.Current, 0 }`. Era time on a legacy save therefore reads *"since the
  beginning of the game"* rather than zero — the direction that saturates a capped curve
  instead of collapsing it, which is the safe failure for every consumer in *Status*.
- **Repair 1 — T-11.** Write 3 mutates `FactionDef.techLevel`, which **silently reverts on
  load** (**T-11**). The mitigation is not invented here; it is read out of the nearest donor.
  `VFETribals.GameComponent_Tribals` scribes its own `TechLevel? playerTechLevel` and, in
  `FinalizeInit`, re-writes `Faction.OfPlayer.def.techLevel` from it when the def has come back
  lower [V, `…/294100/3079786283/1.6/Assemblies/VFETribals.dll`]. `GameComponent_Era.FinalizeInit`
  does the same from `CurrentEra`. **This is the entire content of T-11's workaround and it costs
  four lines.**
- **Repair 2 — the consistency assert.** `FinalizeInit` compares `CurrentEra` against
  `WorldTechLevel.Current`. They can only disagree if something other than `AdvanceEra()` moved
  the era; `Log.Error` naming both values converts a silent second writer into a loud one at the
  next load. Cheap, and the only detector we get.

**One known limit, stated rather than fixed.** WTL snapshots `FactionDef.techLevel` and
`PawnKindDef.techLevel` into `TechLevelDatabase` at startup and re-initialises only when the def
*count* changes [V, [`docs/engine/research-and-tech-tiers.md`](../engine/research-and-tech-tiers.md)
§ *World Tech Level*]. Write 3 therefore does not refresh WTL's snapshot of the player faction.
It does not need to: WTL's player-side gate is `TechLevelUtility.PlayerResearchFilterLevel()` =
`Max(WorldTechLevel.Current, ResearchUtility.InitialResearchLevel)` [V], which never consults the
snapshot. Write 3 exists for Ignorance Is Bliss's `useActualTechLevel` (#7 § 4), which reads the
live `Faction` with no snapshot at all [V, `docs/engine/research-and-tech-tiers.md` § *Ignorance
Is Bliss*].

### 5. Display — mostly free, and one line of ours

| Surface | What it shows | Cost |
|---|---|---|
| world `WITab_Planet` description | **WTL already prints `Tech level: <era>` there**, through `Patch_WITab_Planet.GetDesc_Postfix` [V] | free |
| the same description | *"Era began: day N — n days here"*, from `CurrentEraStartTick`. Under Multiplayer the world view reads the **world** clock (§ *An era's start under Async Time*), so under Route B this line must name a colony | one postfix on `WITab_Planet.get_Desc`, ~10 lines |
| the boundary log | *"Neolithic day 0 · Medieval day 96 · Industrial day 310"* | **not a tooltip on the line above** — see below. A `FillTab` postfix with its own layout, ~40 lines |
| the crossing itself | the capstone project's completion **is** the event | the era-capstone project and `AdvanceEra()` hook |
| pressure readout | era time as a named contributor | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (routes verified on [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61)), supplied by [`PRESSURE.md`](PRESSURE.md) |

**The boundary log cannot be a tooltip on the description line.** `WITab_Planet.get_Desc` is a `string` property; a postfix on it has
`ref string __result` and **no `Rect`**, so there is nothing for `TooltipHandler.TipRegion` to be
given. Showing the log means a postfix on `WITab_Planet.FillTab` that lays out its own row and
calls `TipRegion` against that rect — a different patch, with layout of its own, priced
accordingly in *Cost*.
Note that `FillTab` is also where shutoff § 6a operates, so the two live next to each other.

Days are `ticks / GenDate.TicksPerDay`; a RimWorld year is **60 days**
([`docs/engine/world-time-and-layers.md`](../engine/world-time-and-layers.md) § *Time*) and any
label expressed in years must use that.

### 6. The second writers, and shutting them off

**One number, one writer** is a claim about our code and is false about the load order as it
stands. Two live routes move the era without going through `AdvanceEra()`, and both are
multiplayer-unsafe on their own terms.

**(a) WTL's in-game "Change tech level" button.**
`WorldTechLevel.Patches.Patch_WITab_Planet.FillTab_Postfix` draws a `Widgets.ButtonText` on the
planet inspect tab whenever `Current.ProgramState == Playing` — **not dev-mode gated** — opening
a float menu whose `SetLevel` writes both the static and the `GameComponent` [V]. It is a
one-click era skip, it bypasses the boundary log, and because it writes saved state from
`FillTab` it is a client-local write to synchronised state.

> **Shutoff:** a Harmony prefix returning false on
> `WorldTechLevel.Patches.Patch_WITab_Planet:FillTab_Postfix` — a private static in a
> third-party assembly, named by string through `AccessTools.Method`. ~6 lines. **Loud if WTL
> renames it**: Harmony throws at startup on a null target, which is the Loudness gate's
> preferred failure. The `GetDesc_Postfix` half stays — § 5 wants it.

**(b) `Window_AddFactions`, which the same button opens, registers factions at runtime.**
`SetLevel` calls `WorldTechLevel.Window_AddFactions.OpenIfAnyAvailable(previousLevel)`; the
window's Confirm button calls `FactionGenerator.CreateFactionAndAddToManager(def)` per selected
faction and then spawns settlements for each, **from `DoWindowContents`** [V]. That is a runtime
faction registration against a frozen roster (**T-07**, the same class of defect as **T-15**)
*and* unsynced `Rand` off the frame loop, in one control.

> **The `Rand` half is worse than a single draw.** The loop
> is written `for (int k = 0; k < Rand.RangeInclusive(3, 7); k++)` — **the bound is in the loop
> condition, so it is re-drawn on every iteration** [V]. The number of settlements is therefore
> not a draw of 3–7; it is however many iterations it takes for `k` to exceed a freshly drawn
> bound, and the count of values consumed from the shared `Rand` stream is itself random. Two
> clients running this would diverge in both the world state and the stream position.

It is **inert in this campaign's settled configuration**: `OpenIfAnyAvailable` returns
immediately when `Settings.Filter_Factions` is false [V], and #7 § 3 froze `Filter_Factions`
**off** because WTL's factions filter runs at worldgen and would otherwise generate a
Neolithic-only planet. So the mitigation is already chosen, for an unrelated reason. Shutoff (a)
removes the only route to the window regardless, which is the belt to that braces.

**(c) Lemmy Progression adds a third route, and it is one more reason the mod is BLOCK.**
`LemProgress` draws *"Force Tech Level Advance"* in its **mod-settings window**, opening a float
menu whose options call `LemProgress.Systems.WorldEraManager.AdvanceToTechLevel(level)` from
`DoSettingsWindowContents` [V]. A mod setting driving saved world state is **T-18**'s shape on
top of everything in § 3. It also prefixes VFE Tribals' `GameComponent_Tribals.AdvanceToEra` —
**returning `true`**, so it observes that mod's era advance and pushes WTL's level alongside it
rather than suppressing it [V]. Nothing in the corpus suppresses VFE Tribals' polling detector;
the one mod that hooks it amplifies it. Not a shutoff we have to write — the disposition is
[#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s and the recommendation is BLOCK —
but it belongs on the list of things that move the era without asking.

### Cost

| Piece | Kind | Estimate | Lands in |
|---|---|---|---|
| `GameComponent_Era` + `EraBoundary` — state, `ExposeData`, `FinalizeInit` repairs and assert | C# | ~70 | the assembly we already ship (`ArchinityAltar.dll` today; `CODING_STANDARDS.md` § *Hard constraints*) |
| `AdvanceEra(TechLevel)` + guards | C# | ~25 | same |
| `WITab_Planet.get_Desc` postfix — era-started readout | C# | ~10 | same |
| `WITab_Planet.FillTab` postfix — the boundary-log row and its `TipRegion` (layout, not a tooltip on a string) | C# | ~40 | same |
| Prefix killing WTL's `FillTab_Postfix` (§ 6a) | C# | ~6 | same |
| WTL reflection shim — `GameComponent_TechLevel` and the static `Current`, resolved once, cached, with the auto-property fallback chain and a `Log.ErrorOnce` on failure | C# | ~80 | same |
| **XML** | **none** | **0** | — |

**~230 lines of C# in the assembly we already ship. No new assembly, no def type, no XML, no
recompiled third-party DLL.**

**Two pieces carry most of the weight.** The boundary readout is a layout patch rather than a
tooltip (§ 5), and the shim is not twenty-five lines: the nearest shipped equivalent,
`LemProgress.Systems.WorldEraManager`'s WTL access, is **~80 lines with its assembly scan and
its four-step auto-property fallback** [V] — and ours needs the same fallback plus a second
member (`GameComponent_TechLevel`) that Lemmy never resolves.

The reflection shim exists because `Archinity.Core` must not hard-reference
`WorldTechLevel.dll` — WTL loads through the Lunar loader from
`1.6/Lunar/Components/`, not `1.6/Assemblies/`, and a hard reference to a Lunar component is a
load-order dependency we do not want. Resolve `WorldTechLevel.GameComponent_TechLevel` and the
`Current` property **once**, cache the `MemberInfo`, and `Log.ErrorOnce` if either is absent —
the same shape Lemmy uses, minus its *write* defect. **The engine fact the shim must handle:**
`WorldTechLevel.Current` is an **auto-property**, so `AccessTools.Field(type, "Current")` returns
null and only `AccessTools.Property` — or the `<Current>k__BackingField` name — finds it [V].
Lemmy handles this correctly and is worth copying here (§ 3); it is stated as a trap because it
is a real one for anyone writing the shim from scratch, **not** because the donor falls into it.

---

## Persistence and multiplayer

**Saved state added by this document: one list of `(TechLevel, int)` pairs** — per colony under
§ *An era's start under Async Time* Route B. Nothing else. The era itself stays WTL's; research
stays `ResearchManager`'s; era *time* runs on the era clock, which under Async Time is a choice
between the world clock and one clock per colony (§ *An era's start under Async Time*).

**What must be a synced command, and what already is.**

- **A rite as the caller: `AdvanceEra()` called from a ritual outcome worker needs no sync plumbing.**
  A rite is one route for the advance (§ 3, *What calls it*; choice
  [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)). The
  citation is the lord tick, not the component tick. `LordJob_Ritual.ApplyOutcome` fires
  from a `StateGraph` transition's pre-action, which runs under
  `LordManager.LordManagerTick()` → `Map.MapPostTick()` → `TickManager.DoSingleTick()` [V,
  `Verse.Map.MapPostTick` calls `lordManager.LordManagerTick()`]. That is simulation, executed
  identically on both clients. (`docs/engine/determinism.md` § *What is on the synced tick and
  what is not* covers `WorldComponentTick`, `GameComponentTick` and `Thing.Tick` and says
  nothing about Lords; it is the authority for the two bullets below, not for this one.)
  >
  > One clause the ritual path does owe: `Dialog_BeginRitual`'s cancel route and a ritual's
  > `CancelSignal` are client-local UI, and Multiplayer serialises the dialogue separately
  > (`docs/engine/determinism.md` § *MP serialises the comms-console dialogue*). **Neither
  > touches this design**, because `AdvanceEra()` hangs off the *outcome*, and only the success
  > outcome — a cancelled or failed rite calls nothing.
- **Any other caller does.** A dev gizmo, a debug action, or a button of ours sits on the frame
  loop, and `GameComponentUpdate` is explicitly **not** synced [V, same table]. Such a caller
  must be routed through `Multiplayer.API`'s `[SyncMethod]` / `MP.RegisterSyncMethod`, which
  ships in `0MultiplayerAPI.dll` alongside the Multiplayer mod and no-ops when MP is absent
  [V, `…/294100/2606448745/1.6/Assemblies/0MultiplayerAPI.dll`, `Multiplayer.API.MP`]. **The
  cheaper discipline is to have no such caller**: one entry point, reached only from the
  synchronized research-completion path.
- **The four writes draw no random number**, which is a rule rather than an observation. Every
  write is a plain assignment. Any boundary roll (AE-5(a)'s quest generation) runs on the same
  synced research-completion path, after the writes.
- **Nothing here is a `ModSettings` field.** WTL's twenty-four filter toggles *are* settings and
  are therefore part of the sync surface (**T-18**); #7 froze them, and a mismatch between the
  two clients is a divergence this document cannot detect. That is an argument for recording
  the frozen set in the repo, not for reading settings at runtime.
- **Session shape.** [#23](https://github.com/cjd721/Rimworld-Archinity/issues/23) settled
  one shared player faction, two colonies on separate tiles, Async Time on. The era is world-scoped and
  faction-independent, so Multiplayer's `FactionRepeater` machinery does not apply to it.
  The era *value* is one instant for both colonies; the era *clock* is not — next section.

---

## An era's start under Async Time

**Can an era's start be stamped consistently for both colonies, and by which clock?**
([#185](https://github.com/cjd721/Rimworld-Archinity/issues/185))

- **Possible? Yes**, by either route below. Stamping `Find.TickManager.TicksGame` wherever
  `AdvanceEra()` runs is not one: it records the caller's clock, and every reader on another clock
  is off by the drift between them, which is unbounded.
- **Multiplayer? Yes.** Every clock is lockstep state — scribed, advanced only on the synced tick —
  so no route can desync. The problem is between colonies, not between clients.

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| A — the world clock is the era clock | One era time for everyone, at every instant; it runs whenever either colony is unpaused | vanilla `GameComponentTick`, which under MP runs only on the world tick | C# | Medium | Yes |
| B — one era clock per colony | Each colony's era time runs only while that colony plays; the advance is still one instant for both | vanilla `MapComponentTick` (map tick only), or a per-colony stamp table written through MP Compat's `PatchingUtilities.SetupAsyncTime` shape | C# | Medium–Hard — one component per colony, plus carry-over on relocation and a rule for world-side readers | Yes |

Which one is a route choice for the build map, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).

### The clocks

There is one `TickManager.ticksGameInt`, and Multiplayer swaps its **value** by context
(`AsyncTimeComp.PreContext` → `TimeSnapshot.GetAndSetFromMap`, restored by `PostContext`) [V,
`2606448745/1.6/AssembliesCustom/Multiplayer.dll`]:

| Clock | What `TicksGame` returns it in | Advances at |
|---|---|---|
| **Map clock**, `AsyncTimeComp.mapTicks` (scribed) — one per **map**, encounter maps and sites included | map ticks: every Thing, pawn and job tick, lord toils and ritual outcomes, bench research, `MapComponentTick`; map commands; threat points for a `Map` target (`MapContextIncidentParms`); map-drawn UI (`SetMapTimeForUI`) | that map's voted speed — 0/1/3/6/15× for Paused/Normal/Fast/Superfast/Ultrafast, **12× instead of 6× at Superfast while its colonists all sleep**, 1× under `forceNormalSpeed`, 0 under a pausing session |
| **World clock**, the global value outside map context (`AsyncWorldTimeComp.worldTicks`) | `AsyncWorldTimeComp.Tick` → `DoSingleTick`: `GameComponentTick`, `WorldComponentTick`, world quests, world-target storyteller; world commands, including any `[SyncMethod]` whose arguments carry no map (`SyncMethod.DoSync` sends `MpContext.map?.uniqueID ?? -1`); world-view UI such as `WITab_Planet` | the fastest unpaused map's *desired* speed, and 6× at Superfast even when a map is at 12×; 0 when every map is paused |
| `TickPatch.Timer` | never | once per lockstep step, paused or not. Not a game clock and not a candidate |

`TicksAbs` and `GenDate` inherit the split, because `TimeSnapshot` swaps `gameStartAbsTick` too.
**No clock is the max or the min of the others by construction** — a sleeping colony outruns the
world, a paused one falls behind it. A new map — a second colony, a gravship landing — starts at
`max(other maps' mapTicks)`, usually the *other* colony's clock
(`MapSetup.CreateAsyncTimeCompForMap`). Multiplayer converts exactly four pawn timestamp fields
between clocks (`Patches.TimestampFixer.FixPawn`; MP Compat adds VEF ability cooldowns through
`PatchingUtilities.RegisterTimestampFixer`); nothing of ours would be converted.
`Multiplayer.API` exposes no clock.

**What a stamp on the caller's clock gets each reader.** The researching colony reads
`A_now − A_stamp`, correct. The other colony reads `B_now − A_stamp`: negative if it has been
paused more — its era term sits at the curve's floor until it catches up — or a head start if it
ran faster. World readers read `W_now − A_stamp`, wrong either way. If a later capstone completes on
the other colony, the log's spans subtract one clock from another and PRESSURE's `Σ cappedCurve`
breaks with them.

### Route A — the world clock

**Levers.** Count rather than stamp: `GameComponent_Era` adds to the open boundary's span in
`GameComponentTick`. Vanilla calls that only from `TickManager.DoSingleTick`, and under Multiplayer
`DoSingleTick` runs only from `AsyncWorldTimeComp.Tick` (MP's `TickPatch` replaces
`TickManagerUpdate`) [V] — so the count *is* world ticks, identical on both clients, with no
reference to `Multiplayer.dll`, and it reads the same from any context. Stamping `worldTicks`
instead forces every map-context reader to reflect into Multiplayer for "now"; counting is strictly
lighter.

**Limits.** The world clock is no colony's time. It runs at the faster colony's speed and keeps
running while one colony is paused, so a paused colony's era time rises on the other player's play —
the *"another colony's clock"* [`requirements/PRESSURE.md`](../requirements/PRESSURE.md)
§ *Constraints* rules out for local quantities. It lags a colony sleeping at 12×.

**Consequences.** The contract becomes spans — `TicksInCurrentEra` and per-boundary durations —
rather than absolute ticks, because a world tick cannot be compared against `TicksGame` in map
context. The log never mixes clocks; relocation and new colonies do not touch it. Single-player is
identical to the design above.

### Route B — one clock per colony

**Levers.** Count per home map in `MapComponentTick`, which runs only inside that map's
`AsyncTimeComp.Tick` (`CancelMapManagersTick` suppresses `Map.MapPostTick` elsewhere) [V]. Or stamp
every home map's `mapTicks` at the advance: inside map context `TicksGame − stamp[map]` then needs no
reflection, because `TicksGame` there *is* that map's clock [V]; only the write reflects, and MP
Compat's `PatchingUtilities.SetupAsyncTime` is the shipped shim for it (it resolves
`Multiplayer.Client.Extensions:AsyncTime` and `AsyncTimeComp.mapTicks` by string) [V,
`1629973374/1.6/Assemblies/Multiplayer_Compat.dll`].

**Limits — open for the build map.** A colony founded mid-era; a colony that relocates, which lands
on a new map and a new clock, so its era time must be carried or rebased (`TimestampFixer`'s offset
is the donor shape); what world-side readers — world quests' points, the planet-tab line — use;
excluding temporary maps (`IsPlayerHome`).

**Consequences.** Satisfies PRESSURE's per-colony clock constraint by construction: threat points
are always computed on the target map's clock [V, `MapContextIncidentParms`], and so would this term
be. Era time differs between colonies, so a beat keyed to *"180 days after the Medieval gate"* fires
at different moments per colony. The log becomes one per colony. Single-player has one colony.

**The two compose** — a world count for world beats beside per-colony counts for threat — as a
combination of these mechanisms, not a third.

**Survey.** Across both corpus roots only Multiplayer and Multiplayer Compatibility reference
`mapTicks`, `AsyncTimeComp` or `AsyncWorldTime` — ASCII and null-interleaved UTF-16 passes,
`Referenced/` included deliberately, the UTF-16 form validated on MP's own `"Map Ticks: "` literal.
MP Compat reads map clocks and extends the rebase list; nothing reads the world clock, and nothing
stamps an era (§ *Available mechanisms*).

---

## Failure and recovery

- **The era and the boundary log disagree.** Detected loudly at the next load by § 4's assert.
  Recovery: append a boundary for the current era at the current tick; era time restarts, which
  is a balance wobble rather than a broken save.
- **Someone moves the era outside `AdvanceEra()`.** § 6 removes the two known routes. A new mod
  that writes `WorldTechLevel.Current` is invisible until the next load, when the assert fires.
  Re-run the § 6 survey whenever the mod set moves.
- **The WTL reflection shim resolves nothing.** Log once, and let `AdvanceEra()` still write the
  boundary and the player faction def. The campaign then advances its own era while the world's
  content filter does not follow — visible within minutes as tech above the era appearing in
  trade stock. Loud enough, and strictly better than throwing on the research-completion path.
- **A legacy save's era time reads as the whole game.** § 4's seed, by design. It over-states
  rather than under-states, so a capped curve sits at its ceiling instead of at zero. Say so to
  whoever balances it.
- **The capstone completes twice.** The one-rung guard rejects the second call with `Log.Error` and
  changes nothing. The log stays append-only and no boundary is duplicated.
- **`Filter_Factions` is switched back on.** § 6b re-arms a runtime faction generator against
  **T-07**. This is the single settings change that can break the world irrecoverably, and it
  is worth writing on the frozen-settings list in bold.

---

## Status

**Evidence class: READ.** Settled against the 1.6 `Assembly-CSharp.dll`, `WorldTechLevel.dll`
1.6 (`…/294100/3414187030/1.6/Lunar/Components/WorldTechLevel.dll` — **not** `1.6/Assemblies/`,
which holds only the Lunar loader), `VFETribals.dll` 1.6, `LemProgress.dll` 1.6,
`0MultiplayerAPI.dll` 1.6, and — for § *An era's start under Async Time* — `Multiplayer.dll` 1.6
(`2606448745/1.6/AssembliesCustom/`) and `Multiplayer_Compat.dll` 1.6. No stub, no launch.

**Verified available mechanisms.** Every mechanism the build composes is read out of a
decompiled assembly and marked [V] where claimed: WTL's scribed component and its volatile
mirror, `Game.FillComponents`, `GameComponent.FinalizeInit`, the VFE Tribals T-11 workaround,
the synced-tick table, and both second writers.

**Selected: nothing.** This is a proposed design. **The claim that these verified mechanisms
compose into a working era clock is [I] by construction** and stays [I] until something is
built and loaded twice.

**Not ours:** how long an era lasts, what era time is worth, and the shape of the capped curve
— all balance, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).

**The contract other specs may rely on**, stated so nobody re-derives it:

| Read | Returns |
|---|---|
| `GameComponent_Era.CurrentEra` | the era, `TechLevel` |
| `GameComponent_Era.CurrentEraStartTick` | start of the current boundary **on the era clock** — not comparable to `TicksGame` under Async Time (§ *An era's start under Async Time*) |
| `GameComponent_Era.TicksInCurrentEra` | derived; what #60 asked for; the safe read in every context |
| `GameComponent_Era.StartTickOf(TechLevel)` | start on the era clock, or `-1` if never entered |
| `GameComponent_Era.Boundaries` | the whole log, read-only, oldest first |

- [#109](https://github.com/cjd721/Rimworld-Archinity/issues/109) — this document.
- [#7](https://github.com/cjd721/Rimworld-Archinity/issues/7) — the mechanism choice this
  implements. Closed; its `AdvanceEra()` is a design, not shipped code (§ 0).
- [#60](https://github.com/cjd721/Rimworld-Archinity/issues/60) /
  [`PRESSURE.md`](PRESSURE.md) — the first consumer, and the source of the reset contradiction
  § 2 resolves.
- [#30](https://github.com/cjd721/Rimworld-Archinity/issues/30),
  [#34](https://github.com/cjd721/Rimworld-Archinity/issues/34) — the grids, next consumers.
- [#18](https://github.com/cjd721/Rimworld-Archinity/issues/18) — the world-creation freeze § 6b
  bears on.
- [#23](https://github.com/cjd721/Rimworld-Archinity/issues/23) — the session shape.

---

## Available mechanisms

**The survey behind the build, including what does not exist.**

### Nothing in the game or the corpus records when an era began

That negative is the reason § 2 owes a store, and it survives a tier-4 read:

- **Vanilla has no era.** It has `Faction.def.techLevel`, a def field, and
  `GenDate.DaysPassedSinceSettle`, which counts from world creation and never segments. There is
  no boundary, no stamp and nothing to retain.
- **WTL stores the era and no time at all.** `GameComponent_TechLevel` has exactly one field
  [V]. `WorldTechLevel.Current` is a static auto-property with no backing persistence [V].
- **VFE Tribals runs a five-rung ritual ladder and stamps nothing.**
  `VFETribals.GameComponent_Tribals` scribes `availableCornerstonePoints`, `playerTechLevel`,
  `ethos`, `ethosLocked`, `lastLargeFireUpdate`, `largeFireActiveTicks`,
  `lastTickResearchFinished`, `cornerstones` and `finishedResearchProjects` [V,
  `GameComponent_Tribals.ExposeData`]. `lastTickResearchFinished` is the only tick in it, and it
  is a storyteller cooldown, not an era boundary. `AdvanceToEra(EraAdvancementDef)` writes the
  player faction def and hands out a cornerstone point; **it records no time** [V].
- **Lemmy Progression scribes nothing whatsoever about the era** (§ 3) [V].
- **The name sweep is empty.** `EraStartTick`, `eraStartTick`, `EraStartedTick` and
  `techLevelChangedTick` return **zero** `.dll` hits across both corpus roots
  (`rg -a -l "<name>" <workshop> <common/Mods> -g '*.dll' -g '!**/obj/**'`). `EraAdvancementDef`
  returns 3 — the three version folders of VFE Tribals, which is the sweep's own validation
  against a hit known to exist.

### VFE Tribals is the nearest donor, and it is the donor for the workaround rather than the clock

Read in full for #72 (see [`RESEARCH.md`](RESEARCH.md) § *Granted capability*), and two of its
pieces bear on this document:

- **The T-11 workaround, shipped and working** — § 4, Repair 1. This is the piece worth taking.
- **A polling era detector, which is not.** `GameComponent_Tribals.GameComponentTick` compares
  `Faction.OfPlayer.def.techLevel` against its own scribed `playerTechLevel` **every tick** and
  calls `AdvanceTechLevel()` when the def has moved [V]. It works, it is on the synced tick, and
  it is the wrong shape for us: it makes a def mutation the *trigger* rather than the
  *consequence*, so **any** mod that writes the player faction def silently advances the era —
  including our own write 3, which is why `AdvanceEra()` is a method with a one-rung guard rather
  than a poll.

  > **Node Research (`3729878405`) is said to prefix `AdvanceTechLevel` to `false`; that is
  > [I].** It is **not in either corpus root** and is absent from `MOD-SNAPSHOT.md`, so its
  > assembly cannot be read ([`docs/agents/capability-research.md`](../agents/capability-research.md)
  > § *Inherited claims*), and it is not in this load order. A corpus-wide sweep
  > for `AdvanceTechLevel`, both heap halves, returns **only** VFE Tribals' three copies and
  > `LemProgress.dll` [V]. **Nothing in the corpus suppresses the detector**, and the one mod
  > that hooks the ladder at all — Lemmy, via a prefix on `AdvanceToEra` that returns **`true`**
  > [V] — *amplifies* it. The design argument against a poll stands on its own and never needed
  > the third party.

`docs/data/PARTS-BIN.md` § 5.3 already files VFE Tribals as **RESTAT leaning REBUILD** and says
the ladder is *"five XML defs and one `GameComponent`"*. Reading the assembly agrees, and adds
the reason to rebuild rather than restat: the era advance has to sit behind capstone completion and write
a boundary, and neither is a patch on somebody else's `GameComponent`.

### What vanilla does provide, and where it is used instead

- `Game.FillComponents` — free migration for any `GameComponent` added to an old save [V]. §4.
- `GameComponent.FinalizeInit` — the post-load repair hook both repairs use [V].
- `Scribe_Collections.Look(…, LookMode.Deep)` over an `IExposable` row type — the ordinary way
  to scribe a small log [V].
- `RimWorld.GameRules` — scribed `Game`-level state with a public mutator and a live read.
  Surveyed here because it is the one vanilla precedent for "saved state that changes what the
  player may do", and **it is the right answer for a different ticket**: it gates designators,
  not eras. See [`RESEARCH.md`](RESEARCH.md) § *Granted capability — available mechanisms*.

### Wide pass

Run against both corpus roots plus `common/RimWorld/Data`, `-g '*.dll' -g '!**/obj/**'`, in
**both halves** — ASCII for the `#Strings` heap and a null-interleaved literal for the `#US`
heap, with the `\x00` escapes typed directly into the ripgrep pattern, never built through
`$(…)` and never with `--encoding utf-16le` (**#103**).

| Symbol | ASCII (`#Strings`) | `#US` null-interleaved | Note |
|---|---|---|---|
| `EraStartTick` / `eraStartTick` / `EraStartedTick` / `techLevelChangedTick` | **0** | **0** | the negative § *Available mechanisms* opens on |
| `EraAdvancementDef` / `EraAdvancement` | 3 paths → VFE Tribals only | **1 → `LemProgress.dll`** | sweep validation, both halves |
| `AdvanceTechLevel` | VFE Tribals ×3, `LemProgress.dll` | 0 | confirms nothing else hooks the ladder |

**Why the `#US` half is not optional here, even for a field or type *name*.** This sweep is
its own proof: the `#US` half of `EraAdvancement` returns a hit in
`LemProgress.dll` that the ASCII half does not, because Lemmy reaches VFE Tribals and WTL
entirely through `AccessTools.TypeByName` / `AccessTools.Field` **string arguments** — which is
exactly where a type or member *name* lives in the `#US` heap. Any mod that touches another mod
reflectively is invisible to the ASCII half alone. Skipping it would have hidden the one mod in
the corpus that manipulates the era ladder from outside.

Hit counts are **[I]** — a sweep is a filename-and-string result, never a read. The three
assemblies that matter were then read end to end.

---

## Verification

**What is verified:** every mechanism cited, from the assemblies named in *Status*. Anchors are
`Type.Method`, def field names and trap IDs — never line numbers.

**What needs a prototype:** none of the mechanism. What needs *playing* is the era-time curve,
which is Balance's and not this document's.

**Observable checks that demonstrate the design is satisfied:**

1. **The pair.** Advance an era, save, quit to menu, reload. `WorldTechLevel.Current` must still
   be the new era. (This is the check Lemmy Progression fails.)
2. **The def re-stamp.** After the same reload, `Faction.OfPlayer.def.techLevel` must equal the
   new era — **T-11**'s revert repaired by § 4.
3. **Retention.** After two advances, the boundary-log row must list three rows and the first
   two start ticks must be unchanged.
4. **Continuity.** With [`PRESSURE.md`](PRESSURE.md)'s dev storyteller panel open, note base
   points immediately before and after an advance. They must not fall. (Fails today if the era
   term is written against `CurrentEraStartTick` instead of the sum — § 2.)
5. **Legacy save.** Load a save made before the component existed. No error, no red text, and
   the planet tab must read *"era began: day 0"*.
6. **No second writer.** With shutoff § 6a in, the planet tab must show the tech level and
   **no** "Change tech level" button.
7. **Two clients.** Advance the era on one client while the other is looking at the world map.
   Both must show the same era and the same era-start day, and no desync.

---

## Outstanding decisions

- **The era-time curve is Balance's**, including its ceiling, its time-to-ceiling, and whether
  each era's cap is the same: balance, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).
  **The unit changed** — under `Σ cappedCurve` the term's ceiling is five era-caps, not one (§ 2)
  — so a per-era cap authored against a single-stamp reading will be roughly 5× too large.
- **`PRESSURE.md`'s era term** reads the sum of § 2; it was applied to PRESSURE.md § *The
  build* (era-time row) from [#109](https://github.com/cjd721/Rimworld-Archinity/issues/109).
- **Era lengths are balance**, owned by [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)
  per [`docs/requirements/ERA.md`](../requirements/ERA.md) § *Open questions*.
  `docs/engine/world-time-and-layers.md` § *Time* carries Conrad's target lengths as campaign
  design input rather than an engine fact.
- **Showing the boundary log to the player.** Capability: § 5's `FillTab` row; the log also
  feeds the pressure readout whether or not it is shown.
- **Whether a beat may read `StartTickOf` for an era the colony has left.**
  [`docs/progression/`](../progression/README.md) grid cells are the consumer; a beat that wants
  it reads the same contract. The contract in *Status* supports it either way.

---

## Above-era content seeded on the player's own map

([#153](https://github.com/cjd721/Rimworld-Archinity/issues/153).) Written in the routes form of
[`README.md`](README.md); the sections above predate it and are not re-run.

### Purpose and scope

Answers [`docs/requirements/ERA.md`](../requirements/ERA.md) § *Constraints*: **nothing above the
era is seeded on the player's own map, as structure or as event.** It names three carriers —
vanilla ancient dangers, Biotech's crashed mechanitor ship, and the ancient vehicle wrecks of
`GenStep_ScatterRoadDebris` — and three outcomes in order of preference: **remove**, **author
when it appears**, **replace**.

"The player's own map" is read here as **a map generated for a player settlement**. In vanilla
that is one `MapGeneratorDef`, `Base_Player`: `Settlement.MapGeneratorDef` returns it for any
player-owned settlement without its own generator [V, `RimWorld.Planet.Settlement`], so it covers
the starting map, a second colony and a gravship landing that settles. **One widening, not
home-only:** Odyssey's `ClaimableSite` world object also names `Base_Player` as its
`mapGenerator` (`MapParent.MapGeneratorDef` reads `def.mapGenerator`), and it is the site
object for `QuestNode_Root_AncientStructure`, `QuestNode_Root_AncientMercenaries` and
`QuestNode_Root_Site` quests such as `Opportunity_SurveySite` [V]. So every route below that is
"home-scoped" through `Base_Player` also reaches those claimable quest sites — encounters the
player travels to. The exostrider is `onlyOnStartingMap` and unaffected; `ScatterShrines` already
skips 75 % of non-starting maps; the wrecks under AE-3 are the visible case.

This section does **not** reopen the exposure rule. Maps the player travels to keep their
content. Several routes below *would* also change those maps, and each says so. It does not
answer [#22](https://github.com/cjd721/Rimworld-Archinity/issues/22) § 2, and it does not answer
closing an ancient uplink as an orbital-quest giver, which is
[#180](https://github.com/cjd721/Rimworld-Archinity/issues/180)'s
([`ORBIT.md`](ORBIT.md) § *The reveal gate*).

**A reversal, stated once.** [#7](https://github.com/cjd721/Rimworld-Archinity/issues/7) § 5 froze
WTL's *Ancient debris* (`Filter_GenSteps`) and *Ancient facilities and roads*
(`Filter_WorldGenSteps`) **off**. Only route **AE-4** moves either toggle. Every other route leaves
the frozen set as it is.

### Verdict

- **Possible? Yes, for all three carriers.** Removal is vanilla XML for all three. The mechanitor
  crash can be timed to Industrial. Replacement is XML for structure and C# for defenders. One
  limit: a map exists once, so "author when it appears" for **map-seeded** content either means
  *on maps generated later* or needs code that writes into the living home map.
- **Multiplayer? Yes.** The recommended routes are defs and a scenario part that are scribed into
  the save. Neither side can diverge. The one settings-driven route (AE-4) needs the frozen-set
  record and Multiplayer's join-time config sync.

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **AE-1** Scenario part | A `ScenPart_DisableMapGen` part per genstep in `Archinity_SeedOfArchinity`: the genstep never runs in this game. Biotech's *The Mechanitor* scenario ships exactly this for the exostrider | vanilla | XML | Easy | Yes |
| **AE-2** Generator list edit | `PatchOperationRemove` of the `<li>` from `Base_Player` (dangers, exostrider) or from abstract `MapCommonBase` (debris; Medieval Overhaul ships this patch) | vanilla (MO as donor) | XML patch | Easy | Yes |
| **AE-3** Home-only prevent | A `GenStepDef` of ours whose `preventsGenSteps` names the vanilla genstep, added to `Base_Player` only. It reaches inherited and biome-added gensteps on player maps and nowhere else | vanilla | XML (+ a no-op genstep class if nothing replaces it) | Easy | Yes |
| **AE-4** WTL genstep filter | `Filter_GenSteps` on, plus our `TechLevelConfigDef` rows (e.g. `ScatterShrines`). Gensteps run only on maps generated at or above their level | World Tech Level | settings + XML | Easy | With work (T-18) |
| **AE-5** Timed crash | Exostrider removed (AE-1/2/3); the `MechanitorShip` quest is given when the era reaches Industrial, either by (a) `AdvanceEra()` or (b) an authored `IncidentDef` with a WTL Industrial row | vanilla quest + ours | (a) C# · (b) XML | (a) Medium · (b) Easy | (a) Yes · (b) With work (T-18) |
| **AE-6** Gated decrypt | The exostrider stays. Its transponder cannot be decrypted before Industrial. A `CompUseEffect` subclass of ours is added to `MechanoidTransponder` by XML | ours | C# + XML | Medium | Yes |
| **AE-7** Replace in place | AE-3's genstep does real work: in-era debris or an authored structure (`GenStep_ScatterThings` / `_ScatterLayout` / `_ScatterGroupPrefabs`, VEF KCSG layouts). Defenders need a genstep class of ours | vanilla / VEF + ours | XML · C# for defenders | Easy · Medium | Yes |
| **AE-8** Replace with a journey | Removed from the yard. An authored quest offers an Archon site on a nearby world tile instead, or the transponder's `quest` is repointed to one. The content becomes an encounter | vanilla quest machinery | XML (C# only for a custom site part) | Easy–Medium | Yes |
| **AE-9** Late insertion | At the advance, a genstep (e.g. `GenStep_ScatterShrines`) runs on the living home map. The age "uncovers" a vault | ours | C# | Medium–Hard | Yes (synced path) |

**AE-4 is not recommended.** It is not scoped to the home map, and the same toggle rebuilds
above-era settlements as in-era ones (**T-165**). **AE-9 is not recommended for debris.** Wrecks
appearing overnight read as a bug, not an age.

**Carrier × outcome** — which routes reach which cell:

| | Remove | Author when it appears | Replace |
|---|---|---|---|
| **Ancient dangers** (`ScatterShrines`, `Base_Player` only) | AE-1, AE-2 (`Base_Player`), AE-3 — all home-scoped | AE-4 (later maps only), AE-9 (living home map) | AE-7, AE-8 |
| **Mechanitor crash** (exostrider → transponder → quest) | AE-1, AE-2, AE-3 on `AncientExostriderRemains` — home-scoped | AE-5 (a/b), AE-6; **not** AE-4 (see below) | AE-7 (other remains), AE-8 (repoint the transponder) |
| **Road wrecks** (`ScatterRoadDebris`, in `MapCommonBase`) | AE-3 home-scoped; AE-1, AE-2 (`MapCommonBase`) remove it from **every** map | AE-4 (later maps only) | AE-7 (in-era debris in its place) |

#### AE-1 — Scenario part

- **Gets us:** one `ScenPartDef` per genstep (`scenPartClass ScenPart_DisableMapGen`, `genStep X`,
  `selectionWeight 0`), listed in our `ScenarioDef`. `MapGenerator.GenerateMap` filters
  `mapGenerator.genSteps` **and** `BiomeDef.extraGenSteps` through a local `IsValidBiome`, which
  drops any genstep a scenario part names [V]. `Scenario.ExposeData` scribes `parts` deep, so the
  choice travels with the save [V]. Vanilla precedent: `DisableExostriderRemains` in Biotech's
  *The Mechanitor* [V, `Biotech/Defs/Scenarios/`]. It also reaches Odyssey's
  `AncientRuins_Scarlands` and Glacial Plain's `FrozenRuins`, the two biome `extraGenSteps` whose
  ruin layouts can carry the uplink room (#180).
- **Cannot:** reach tile-mutator `extraGenSteps`, mutator workers (the ancient uplink), or site
  parts' `extraGenStepDefs` [V]. It scopes by genstep, not by map. `ScatterShrines` and the
  exostrider appear only in `Base_Player`, so for them it is home-scoped. `ScatterRoadDebris` is in
  `MapCommonBase`, so for the wrecks it reaches every map, encounters included. **Permanent for
  the game** unless code removes the part at an advance. That is AE-5's shape, and it affects only
  maps generated afterwards.
- **Consequences:** none on the frozen set. The parts show in the scenario summary unless marked
  invisible.

#### AE-2 — Generator list edit

- **Gets us:** XML deletion at the source. The `Base_Player` list holds `ScatterShrines` and
  `AncientExostriderRemains` directly [V, `Core`/`Biotech` `BasePlayerMapGenerator.xml`]. The
  Ideology debris lives in abstract `MapCommonBase` [V, `Core/Defs/MapGeneration/CommonMapGenerator.xml`].
  **Medieval Overhaul ships this exact patch shape**: `Defs/MapGeneratorDef[@Name='MapCommonBase']/genSteps/li[text()="ScatterRoadDebris"]`
  and ten siblings, plus `AncientExostriderRemains` on `Base_Player`, each behind its own settings
  toggle [V, `3219596926/1.6/Patches/ToggleOptions/MOSetting_RemoveJunk.xml`, `…_RemoveExostrider.xml`].
- **Cannot:** remove an inherited entry from `Base_Player` alone. **T-05** appends child lists to
  the parent's, so the `<li>` is not in `Base_Player`'s XML to remove. `Inherit="False"` would drop
  every mod's additions to `MapCommonBase` along with it. The xpaths are **unrun [I]**:
  `tools/defdb.py` cannot check a leading-`Defs/` xpath until
  [#102](https://github.com/cjd721/Rimworld-Archinity/issues/102). MO's shipping copy is the
  evidence that the shape works.
- **Consequences:** the `MapCommonBase` form changes every map, as AE-1 does for the wrecks. Do not
  copy MO's settings-toggle wrapper — that is **T-18** at patch time.

#### AE-3 — Home-only prevent

- **Gets us:** the one vanilla lever that is **both** XML and home-scoped for inherited content.
  `GenStepDef.preventsGenSteps` is applied in `MapGenerator.GenerateContentsIntoMap` (and
  `MapGeneratorPostInit`) to the **merged** list — generator, biome, mutator and site steps
  together [V]. So a step added only to `Base_Player` removes `ScatterRoadDebris`, `ScatterShrines`,
  Scarlands junk or `AncientRuins_Scarlands` from player maps and leaves every other map untouched.
  Vanilla precedent: Odyssey's `ScarlandsJunkClusters` prevents `AncientJunkClusters` [V].
- **Cannot:** stop mutator-worker content (the uplink prefab). A `GenStepDef` must carry a
  `genStep` (`GenStepDef.PostLoad` dereferences it [V]). For pure removal that means a no-op step:
  a zero-count vanilla scatterer [I] or a trivial class of ours.
- **Consequences:** none on the frozen set. It combines naturally with AE-7: the preventing step
  *is* the replacement.

#### AE-4 — WTL genstep filter (not recommended)

- **Gets us:** "author when" for free on maps generated later. The filter compares each genstep's
  level with `WorldTechLevel.Current` at generation [V]. WTL already rows the Ideology debris at
  Industrial/Spacer/Ultra and `AncientExostriderRemains` at Ultra. A row of ours for
  `ScatterShrines` is pure XML (T-54's mechanism, used as a weapon; see
  [`docs/engine/research-and-tech-tiers.md`](../engine/research-and-tech-tiers.md) § *Which toggle
  gates which filter*).
- **Cannot:** give the **home** map anything later. The home map is generated once, in the
  Neolithic, so on it every row behaves as removal. The exostrider genstep is `onlyOnStartingMap`
  [V], and `GenStep_ScatterShrines.ShouldSkipMap` skips 75 % of non-starting maps [V], so for both
  carriers AE-4 is effectively removal. It cannot reach the mechanitor **quest** at all: the quest is
  item-given and never passes the storyteller. It cannot scope to the home map.
- **Consequences:** moves #7's frozen set, and is **T-18**. Multiplayer's config sync covers the
  file at join, but not a mid-session flip, because WTL re-applies toggles live. `Settings.Overrides`
  still beats our rows per install. **T-165**: the same toggle strips site turrets and ancient
  remains from encounter maps, and clamps every NPC base's build to the world era. That is the
  quiet widening the requirement forbids. Our own gensteps are **not** at risk from it: a
  `GenStepDef` has no derived level and stays `Undefined` unless a row or `Settings.Overrides` names
  it, and no mod in either corpus root ships a `GenStepDef` row besides WTL's own named list [V,
  sweep of `<defType>GenStepDef</defType>`]. T-54's "derived level above the world level" does not
  arise for gensteps (see the correction note on **T-54**).

#### AE-5 — Timed crash

- **Gets us:** the crash in the Industrial era and not before. The requirement names this
  outcome. The quest is vanilla: `QuestScriptDef MechanitorShip`, `QuestNode_Root_MechanitorShip`,
  which lands `ShuttleCrashed_Exitable_Mechanitor` near the colony with a mech group scaled from
  threat points and a dead mechanitor's mechlink [V]. (a) `AdvanceEra()` calls
  `QuestUtility.GenerateQuestAndMakeAvailable` on the synced research-completion path. (b) An
  `IncidentDef` of ours (`IncidentWorker_GiveQuest`, `questScriptDef MechanitorShip`) with a WTL row
  at Industrial. `Filter_Incidents` is already **on** in the frozen set, so no toggle moves — but
  the row must **not** carry `<offworld>` (**T-166**).
- **Cannot:** (b) is fired by a storyteller comp and has no once-ever guard of its own. It needs
  `blockedByQueuedOrActiveQuests` or a refire window. A fixed-day comp is **T-157**. (a) and (b)
  both need AE-1/2/3 on the exostrider first, or the vanilla chain still fires early.
- **Consequences:** (b) inherits T-18 through `Filter_Incidents` and `Settings.Overrides`. (a) is
  one more write in `AdvanceEra()`. How it is built belongs to
  [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).

#### AE-6 — Gated decrypt

- **Gets us:** the crash still comes only when the player acts, and only from Industrial on.
  `CompUseableDatacore.CanBeUsedBy` already refuses with a reason when there is no research bench
  [V]. An extra `CompUseEffect` can refuse by era the same way. There is no XML field for it:
  `CompProperties_Usable` has no research or tech gate [V].
- **Cannot:** remove the **structure**. An Ultra exostrider still stands in the Neolithic yard.
  That is exposure, but it is also map-seeded, so this answers the crash and not the remains. The
  simple research bench has no prerequisite [V], so without this gate a Neolithic colony can
  decrypt on day one.
- **Consequences:** C# in the assembly we ship. The refusal is read from game state on both
  clients.

#### AE-7 — Replace in place

- **Gets us:** something era-fitting where the vanilla content was. Pure XML covers props and
  structures: `GenStep_ScatterThings`, `GenStep_ScatterLayout` (the exostrider's own class),
  `GenStep_ScatterGroupPrefabs` over `PrefabDef`s [V]. VEF's KCSG `GenStep_CustomStructureGen` places
  authored `StructureLayoutDef`s [V].
- **Cannot:** field defenders from XML. KCSG resolves layouts under `map.ParentFaction`, which on a
  home map is the player [V]. Hostile Archon defenders with a defend-point lord need a genstep class
  of ours. The donor is `GenStep_ScatterShrines.ScatterAt`, which pushes a BaseGen symbol into a
  used-rect-checked rect [V].
- **Consequences:** the "Archon site with a few defenders" sits in the yard. It is still
  map-seeded, so it can be opened from day one.

#### AE-8 — Replace with a journey

- **Gets us:** the requirement's example, *"an Archon site with a few defenders that becomes part of
  the campaign's own quest line"*, as an **encounter**. That keeps the design principle: going there
  is a decision. Either an authored quest offers a site on a nearby tile, or
  `CompProperties_UseEffectGiveQuest.quest` on `MechanoidTransponder` is repointed by XML [V field].
- **Cannot:** fire itself at game start without a giver. A storyteller comp is subject to T-157. A
  quest chain is subject to T-71/T-153.
- **Consequences:** the site's own gensteps and BaseGen face AE-4's T-165 if that toggle is ever
  on.

#### AE-9 — Late insertion (not recommended for debris)

- **Gets us:** a vault that "was always there" surfaces at an advance. That fits the requirement's
  wave of the wand.
- **Cannot:** this is [I] throughout. Gensteps assume `MapGenerator`'s working data (`UsedRects`,
  fog roots). Vanilla runs a genstep on a finished map only from debug tools
  (`MapGenerator.DebugDoNextGenStep`, `DebugActionsMapManagement`) [V].
- **Consequences:** must avoid the player's buildings (*"the advance never modifies anything the
  player built"*). Hard to test.

**Recommendation (not a selection).**
- **AE-1 for ancient dangers and the exostrider.** It is vanilla's own mechanism, XML, home-scoped
  for those two, scribed in the save, and leaves #7's set alone.
- **AE-3 for the wrecks**, ideally as AE-7: an in-era debris step that prevents
  `ScatterRoadDebris` on player maps only. AE-1 and AE-2 would take the wrecks off encounter maps
  too.
- **AE-5(a)** if the story wants the mechanitor at Industrial.
- **AE-8** where a replacement should be a place rather than a fixture.

### Constraints

- **A map is generated once.** Any gensteps-level gate on the Neolithic home map is removal.
  "Later" means other maps (AE-4) or code on the living map (AE-9).
- **Genstep-keyed levers cannot see the map's parent.** Of the removal levers, only a step added
  to `Base_Player` (AE-3) is home-scoped for content the home map inherits.
- **T-165** — WTL's "Ancient debris" misses `ScatterShrines`, strips encounter maps, and clamps
  settlement builds. **T-166** — `AlwaysAllowOffworld` voids offworld rows. **T-54** — WTL filters
  our own gensteps (correction note: the map leg is `Filter_GenSteps`). **T-05** — generator lists
  append. **T-18** — any settings-driven route. **T-157**, **T-71** — one-shot and chain-granted
  quests.

### Available mechanisms

- **The mechanitor crash is not an `IncidentDef`** — correcting this ticket's premise [V].
  `AncientExostriderRemains` (a `Base_Player` genstep, `onlyOnStartingMap`) leaves a
  `MechanoidTransponder` in `killedLeavings`. Decrypting it at any research bench
  (`CompUseableDatacore`) runs `CompUseEffect_GiveQuest` → `MechanitorShip`
  (`isRootSpecial`, `rootSelectionWeight 0`). No storyteller comp, `IncidentDef` or quest node in
  vanilla gives it, and the transponder has no other vanilla source [V: sweep of `Data` XML and the
  decompiled `Assembly-CSharp`]. No mod in either root supplies it either. `MechanoidTransponder|MechanitorShip`,
  XML plus both `.dll` heaps: the only mod hits are WTL's `ThingDef` row and VPE's
  `Ability_TransmuteItem`, which *excludes* the transponder from transmutation. The validators
  were the vanilla assembly: 3 ASCII hits and 2 `#US` hits. The storyteller only lists `MechanitorShip` as a **blocker** of the
  ancient-complex giver. WTL rows the transponder `ThingDef` and the exostrider genstep at Ultra, but
  not the quest.
- **Road debris**, re-verified [V]: `GenStep_ScatterRoadDebris.Generate` spawns
  `VehicleRangeNonRoadMap = IntRange(1, 2)` wrecks on a roadless map, and `CanScatterAt` rejects
  off-road cells only when `mapHasRoads`. The wreck set is a hardcoded `ThingDefOf` list, so XML
  cannot swap the things — only the step. `TileMutatorDef.junkDensityFactor` scales it per tile.
- **Ancient dangers**: `GenStep_ScatterShrines` pushes BaseGen `ancientTemple`, which honours the
  `peacefulTemples` difficulty flag. It is listed only in `Base_Player` [V].
- **Others found on the same behaviour** (listed, not answered):
  - **Ushanka's Hacking Expansion** adds `USH_AncientCyberdeck` to `Base_Player` and `USH_DataCenter`
    to `MapCommonBase` [V, `3573344880/1.6/Patches/MapGeneratorDef.xml`]. Both are reachable by AE-1/2/3.
  - **Vanilla Exploration Expanded** — tile mutator `VEE_MechanoidShipChunks` (mutator
    `extraGenSteps`; no WTL row) [V]. Reachable by AE-3 only.
  - **Odyssey** — `Junkyard` mutator (Scarlands junk ×15 density, no WTL row); Scarlands'
    `AncientRuins_Scarlands` and Glacial Plain's `FrozenRuins` biome steps; the `AncientUplink`
    mutator and ruin room. The uplink's home-map half is ours and its giver half is
    [`ORBIT.md`](ORBIT.md) § *Holding every `OrbitalScanner` giver shut*
    ([#180](https://github.com/cjd721/Rimworld-Archinity/issues/180)), whose single `PrefabDef
    AncientUplink` funnel reaches every arrival route.
  - **Anomaly** — `VoidMonolith` on `Base_Player`, so within AE-1–AE-3's home scope [I].
  - **Mechanoids: Total Warfare** redefines `AncientExostriderRemains` and defines an unattached
    `AncientWarBeaconRemains` (its `Base_Player` patch adds nothing) [V].
  - **Vanilla ship-part crash incidents** — un-gated in the frozen configuration by **T-166**.
    They are *arrivals*, so they are the arrival band's
    ([#22](https://github.com/cjd721/Rimworld-Archinity/issues/22)).
- **Wide pass** (both roots, `-g '!**/obj/**' -g '!**/Referenced/**'`):
  - `GenerateContentsIntoMap|Base_Player`, ASCII `-i`, returned only World Tech Level in 1.6.
    That is the validator: its prefix is known.
  - The null-interleaved literal (typed escapes) returned Vanilla Gravship Expanded and Vehicle
    Framework, both map-generator selection, not content.
  - No other assembly injects gensteps. XML additions to `Base_Player`/`MapCommonBase` came from
    VEF (KCSG biome structures — `BiomeStructGenExtension` has **zero** users), Medieval Overhaul
    (in-era), Ushanka and MTW.
- **What #22 § 2 becomes under each route** — handed back to
  [#22](https://github.com/cjd721/Rimworld-Archinity/issues/22), not answered:
  - Under AE-1/2/3 on `ScatterShrines`, ancient-danger soldiers never generate on a player map.
    The check **loses its home-map subject**. Whether an encounter still generates them is #22's.
  - Under AE-4/AE-9, dangers appear at world level L. The check **matters only if L is below the
    soldiers' gear level**.
  - Under AE-7/AE-8, the defenders are ours. The check becomes one about the Archon faction's
    exemption: **T-54**'s `Undefined` row versus the `FactionsExcluded` setting.

### Status

**Evidence class: READ.**
- Settled against the 1.6 `Assembly-CSharp.dll`, `WorldTechLevel.dll`
  (`3414187030/1.6/Lunar/Components/`), `LunarFramework.dll`, VEF's `KCSG.dll`, `Multiplayer.dll`
  (`2606448745/1.6/AssembliesCustom/`) and MP Compat (both assemblies).
- Also read: vanilla and DLC defs, and the mods named above.
- Every mechanism cited is [V]. **Every route is [I] by construction.** AE-2's xpaths are unrun
  (#102), and AE-9 is [I] throughout.
- **Selected: nothing.**

### Open questions

- **Capability, answered above:** a replacement can be a fixture in the yard (AE-7) or a place to
  go (AE-8); the mechanitor crash has routes of its own in the carrier table (AE-1–AE-3, AE-5,
  AE-6, AE-7, AE-8); Anomaly's `VoidMonolith` sits on `Base_Player`, which AE-1–AE-3 reach [I].
- **Build — [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119):**
  - the no-op step for AE-3;
  - AE-5's once-only guard;
  - the defender genstep for AE-7;
  - where AE-8's quest is given from.
- **[#22](https://github.com/cjd721/Rimworld-Archinity/issues/22):**
  - § 2 per the list above;
  - the T-166 ship-part incidents as arrivals.
- **The uplink as a giver:** answered in [`ORBIT.md`](ORBIT.md) § *Holding every
  `OrbitalScanner` giver shut* ([#180](https://github.com/cjd721/Rimworld-Archinity/issues/180)).
- **Capability, unread [I]:** whether a `Base_Player` child or a modded player-settlement generator bypasses
  AE-3. Vanilla's two children (`BasePlayer_SecondArchonexusCycle`, `…Third…`) inherit it [V].

---

## The arrival band

Written in the routes form of [`README.md`](README.md). Answers [`docs/requirements/ERA.md`](../requirements/ERA.md)
§ *The arrival band*: everything that arrives at the player — raids hostile and friendly, quests and the threats
inside them, visitors, travelers and trade caravans, storyteller incidents with or without a faction — never
breaks the era's flavour by coming from above it. There is no floor. No faction is exempt by default, and only an
authored beat may breach it. "Merely unlikely" does not satisfy it.
Per the owner, Multiplayer players share one config folder, so a settings-driven route is not a divergence risk.

### Verdict

- **Possible? Yes, by a gate of our own. Ignorance Is Bliss (IIB) cannot become a hard rule by configuration.**
  Settings close two of its four known gaps; its quest and event tables are hardcoded C# dictionaries no XML
  extends, and its pre-set-faction path leaks in four ways no setting reaches (below). Closing those takes
  patches on the same seams our own gate uses, at which point IIB adds nothing.
- **Multiplayer? With work.** Every seam runs on the synced tick; the band must be read from the era clock
  (saved state), never from a static cache.

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **AB-1** IIB configured | Raids, friendly raids, visitors, travelers and trade caravans banded when the **game chooses** the faction; the Church no longer exempt (`numTechsAhead 0`, `empireIsAlwaysEligible false`; a negative `numTechsBehind` means no floor). A veto plus weighting, *not a hard rule* | IIB | settings | Easy | Yes, with the cache call below |
| **AB-2** WTL rows | A hard **ceiling** at the world era on every storyteller-fired incident and every quest script from any source, per `IncidentDef` / `QuestScriptDef` / `SitePartDef` row. Never chooses or refuses a faction; no floor. Unrowed defs pass silently, so the rows enumerate the whole corpus; `AlwaysAllowOffworld` off (T-166) | World Tech Level | XML | Medium | Yes |
| **AB-3** Our own gate | A hard veto or substitution on **every** faction arrival, and an explicit authored-breach flag — a Glitterite beat is exempt by construction and nothing else is | ours, in `AdvanceEra()`'s assembly | C# (Harmony) | Medium; the quest-pawn half edges toward Hard | With work |

AB-3 composes with AB-2 (factions from ours, events and quest scripts from WTL's rows). AB-1 alongside AB-3 is
harmless on the veto path but **fights a breach** on the pre-set path, so AB-3 means IIB off or its
`CanFireNowSub` postfix unpatched. **Selected: nothing.**

### Why IIB is not a hard rule [V, `IgnoranceIsBliss.dll` 1.6]

- **The static cache.** `IgnoranceBase.cachedTechLevel` is recomputed only when 0, on
  `ResearchManager.FinishProject` and on settings write. It goes stale on a second load in one session and on an
  advance not fired by research completion (the rite route). The `PlayerTechLevel` setter is public: one call
  from `AdvanceEra()` and one on load closes it.
- **Pre-set factions leak.** `CanFireNowSub`'s substitution assigns only when an in-band hostile faction exists
  (fails open); `IncidentWorker.CanFireNow` returns `lastCanRunResult` within a tick, skipping the substitution;
  16 non-debug caller files (`QuestPart_SurpriseReinforcement`, call-for-aid, `ScenPart_CreateIncident`, ritual
  outcomes…) call `TryExecute` without `CanFireNow`; and the substitute is always hostile, so an out-of-band
  visitor group can arrive as hostile "visitors" (`IncidentWorker_VisitorGroup` has no hostility check).
- **Untouched arrivals.** `IncidentWorker_CaravanMeeting.TryFindFaction`,
  `IncidentWorker_OrbitalTraderArrival.GetFaction`, and pawns placed by `QuestPart_PawnsArrive` /
  `QuestPart_DropPods` with no incident. Its storyteller filter reaches five comps; its quest gate names one quest.
- **It rewrites an authored breach.** No whitelist, and `parms.forced` does not bypass `CanFireNowSub`.
- **Not a hole: WTL's `Empire → Undefined` row.** It writes WTL's own `TechLevelDatabase<FactionDef>`, not
  `FactionDef.techLevel`, which IIB reads and which stays `Ultra`. `Undefined` passes IIB only for a `FactionDef`
  with no `techLevel`; a sweep of 106 concrete faction defs across the corpus found none, so it is an authoring
  rule: every faction we write declares `techLevel`. WTL's faction database is read by the roster, the
  world-creation page, `Window_AddFactions` and `Patch_QuestNode_Root_WorkSite` — the last is the one reader
  outside worldgen ([INTEGRATION](INTEGRATION.md)'s #22 row).

### AB-3's seams [V, `Assembly-CSharp.dll` 1.6]

| Where the faction is decided | Seam |
|---|---|
| Chosen by the game: hostile and friendly raids, visitors, travelers, trade caravans, the tribute collector | `IncidentWorker_PawnsArrive.FactionCanBeGroupSource` (virtual; every subclass calls `base`) |
| Pinned by a caller (quest threats, call-for-aid, scenario, rituals, `SignalAction_Incident`), and faction-less events by def | `IncidentWorker.TryExecute` — public, non-virtual, the sole entry to `TryExecuteWorker` for all 25 caller files |
| Paths that choose their own faction | `PawnGroupMakerUtility.TryGetRandomFactionForCombatPawnGroup` (caravan ambush, demand), `IncidentWorker_CaravanMeeting.TryFindFaction`, `IncidentWorker_OrbitalTraderArrival.GetFaction` |
| Quest-placed pawns and askers | `QuestManager.Add` (WTL's seam), walking the quest's parts [I]. `Quest.InvolvedFactions` is not a detector: `QuestPart_Incident` does not override it. A refused quest inherits T-174 |

No other mod on disk carries a tech-level arrival gate: `FactionInEligibleTechRange` occurs only in IIB, and Rim War,
Factional War, RimPacts, VRE Archon, the VFE mods, Medieval Overhaul and VEF's storyteller half touch these seams
without reading tech level [V, decompiled; [I] for 1.6-only additions]. WTL's pawn and gear filters clamp every
generated pawn to the world level — a weak pawn-level backstop, and a downgrade of an authored Ultra breach unless
its faction is in `FactionsExcluded` ([#22](https://github.com/cjd721/Rimworld-Archinity/issues/22) § 2).
*Corrected on [#207](https://github.com/cjd721/Rimworld-Archinity/issues/207):* the exemption holds for kinds and
gear but not xenotypes, whose filter never sees the faction (**T-215**; re-verified in both assemblies, see
*Hand-authored factions and spawn pools*).

### Delivery by drop pod

Pods belong to the Industrial era, when the player gets them, so a pod before Industrial breaks the era's flavour
whatever it carries (Conrad, 2026-09-26). **Possible? Yes: the ungated paths close with XML and one funnel patch**
[V, `Assembly-CSharp.dll` 1.6 and both mod roots; Anomaly not on disk]. **Multiplayer? With work.**

- **The funnel.** Every non-player pod lands through `DropPodUtility.MakeDropPodAt`, directly or via
  `DropThingsNear` / `DropThingGroupsNear`, which already has a pod-less `instaDrop` branch. The pod def is chosen
  per call (`info.sentTransporterDef`, then `faction.def.dropPodActive`, then `ActiveDropPod`). Only the player's own
  launches (`CompLaunchable`, `CaravanShuttleUtility`) set `sentTransporterDef`, so a patch can exempt them.
  Royalty shuttles are a separate path, Empire only.
- **Already gated at Industrial.** The drop arrival modes carry `minTechLevel Industrial`, tested against the
  arriving faction's tech (`PawnsArrivalModeWorker.CanUseWith`), so under the arrival band drop raids and drop
  visitors come only from factions the player's era admits; WTL gates the resource and refugee pod crashes at
  Industrial; orbital-trader purchases need a comms console, which is Industrial research.
- **Ungated — pods before Industrial.** Every quest item reward (`Reward_Items.GenerateQuestParts` →
  `QuestPart_DropPods`, no faction); pawn rewards on the pod side of `Reward_Pawn`'s `DropPod` / `WalkIn` flip; quest
  pawns placed by `QuestPart_PawnsArrive` with a stored drop mode or by `QuestPart_DropPods` (about a dozen quest
  roots: wanderer joins, hospitality refugees, shuttle-crash rescue…); siege supplies (no faction); and quick
  military aid — no def on disk sets `forQuickMilitaryAid`, so `IncidentWorker_Raid.TryResolveRaidArriveMode`
  hard-assigns a drop mode with no check. Calling aid needs comms, so that last one is Industrial in practice;
  a royal permit or ability is Empire-only. Vanilla's ransom payout is the precedent for a per-tech switch:
  `ChoiceLetter_RansomDemand` walks the hostage in below Industrial and pods it above.

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **DP-1** No pod before Industrial | One prefix on `MakeDropPodAt`: every non-player delivery — rewards, quest pawns, siege supplies — is placed at the map edge or trade spot with no skyfaller, the ransom payout's shape. Acceptable to the requirement | ours, Harmony | patch | Medium | With work |
| **DP-2** A courier carries it in | Same seam, but a pawn or pack animal walks in from the edge, drops the goods and leaves. Donor: VEF Outposts' `Outposts.LordJob_Deliver`, whose `PackOrPods` mode already picks pack or pod by `TransportPod.IsFinished`. Optional flavour over DP-1 | ours, copying VEF | C# | Medium; Hard if the carrier must be the giver's pawn and survive what it meets | With work |
| **DP-3** Pawn joiners walk in | `Reward_Pawn` forced to `WalkIn`; `QuestNode_Root_WandererJoin.AddSpawnPawnQuestParts` is virtual and already has a walk-in variant. DP-1 also catches these | vanilla + ours | patch | Easy–Medium | Yes |
| **DP-4** Called aid walks in | `forQuickMilitaryAid` on `EdgeWalkIn` (and on the drop modes, so industrial allies still drop); the hard-coded pod fallback never fires [I] | vanilla | XML | Easy | Yes |

**Not a route: switching pods off.** `giveToCaravan` on a home-map quest loses the reward silently
(`QuestPart_GiveToCaravan.Notify_QuestSignalReceived` returns with no caravan), and removing reward quests removes
the quests, not the pods. No mod on disk replaces pod delivery. **Multiplayer:** patch inside the funnel and never
swap `Reward_Items`' part for a new type, because Multiplayer binds a quest's clock to the exact type
`QuestPart_DropPods` (T-177); copy VEF's lord job, not its per-client delivery setting (T-18); and
`Multiplayer.Client.ThingSpawnSetForbidden` exempts only contents of the exact `ActiveDropPod` def, so goods placed
with no pod enter per-faction forbidden bookkeeping [I on the effect; a one-line build check].

### Hand-authored factions and spawn pools

Answers [#207](https://github.com/cjd721/Rimworld-Archinity/issues/207): every faction in the game is written by
us, spawn pools included, so no faction, ours or a mod's, can field a pawn kind, gear or xenotype we did not write.
**READ.** [V, `Assembly-CSharp.dll` 1.6.4871 and the 1.6 assemblies named below; both mod roots.]

**Possible? Yes, for every faction the game can create, but not by writing `FactionDef`s alone.** A faction def
owns its group makers, its member and leader kinds and its `xenotypeSet`. It does not own what those kinds carry.
Gear is drawn by tag against every `ThingDef` in the database, some kinds are chosen outside any faction, and a few
mods add to a finished pawn in C#. XML closes the first two if we own the tag vocabulary and every kind a faction
can reach. Only a check at `PawnGenerator.GeneratePawn` closes the third.
**Multiplayer? Yes.** The XML is identical on both clients, and the check runs inside generation, which already
runs in synced context [I].

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **HF-1** Every faction def is ours | The worldgen roster is our defs alone (`maxConfigurableAtWorldCreation 0` on every other configurable def; mind **T-10**). Every def the engine or a mod creates mid-game is **overwritten in place**, not removed: the `DefOf` factions vanilla instantiates by name, and every def the work-site fallback can reach (**T-216**). Fixes *which kinds* a faction lists | ours | XML | Medium: 106 concrete defs, most needing a flag, the `DefOf` set a full rewrite | Yes |
| **HF-2** Closed kinds | Every `PawnKindDef` a faction can reach is ours, with a private tag vocabulary (`weaponTags`, `apparelTags`, `techHediffsTags`), non-empty `apparelTags`, `apparelIgnoreSeasons` and `apparelIgnorePollution`, an explicit `xenotypeSet`, and no title fields unless meant. Our faiths set `disallowedPrecepts`, or are fixed, so no apparel precept dresses members. A mod item joins a pool only if it carries our tag. Fixes *what they carry* and *which xenotypes*, on the def path | ours | XML | Medium–Hard, by volume | Yes |
| **HF-3** Kinds chosen outside the faction | The vanilla kinds C# names directly (`PawnKindDefOf.SpaceRefugee`, `Refugee`, `Slave`, `Drifter`, `Salvager_Elite`, `Sanguophage`, `Mechanitor_Basic`, `AncientSoldier`…) and the quest and incident XML `kindDef`s rewritten as HF-2 kinds; no kind outside a faction carries that faction's title (**T-214**) | ours | XML | Medium; the list of C# sites is [I] for completeness | Yes |
| **HF-4** A gate at the funnel | One postfix on `PawnGenerator.GeneratePawn(PawnGenerationRequest)`, the one public entry for new and redressed pawns. It checks kind, xenotype, genes, apparel, equipment, inventory and implants against the faction's written list, then strips, swaps or regenerates. **The only route closed against C# injectors and world-pawn redress** | ours, Harmony | C# | Medium | Yes [I] |
| **HF-5** World Tech Level's clamp | A tech-level ceiling at the world era on kinds, gear, implants, traits, backstories, xenotypes and ideo apparel. Not authored: it meets *"no stray above-era pawn"*, not *"written by us"*. Its xenotype filter ignores `FactionsExcluded` (**T-215**) | World Tech Level | settings | Easy | Yes, one shared config |

HF-1 to HF-3 are the requirement as written. HF-4 is what makes the pool closed rather than closed by inventory.
HF-5 is a backstop, not a substitute. **Selected: nothing** ([#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)).

#### Which factions reach a world

- **At worldgen, only the world-creation list,** which XML authors whole (`docs/engine/factions-and-worldgen.md` §
  *The roster is authorable as defs*). World Tech Level strips from it (**T-54**).
- **Mid-game, vanilla creates factions from fixed defs in eight quest roots** [V]. `Beggars` → `Beggars`;
  `Bossgroup` → `Mechanoid`; `Hospitality_Refugee` → `OutlanderRefugee`; `Hack_WorshippedTerminal` → `TribeCivil`;
  `SanguophageMeetingHost` and `SanguophageShip` → `Sanguophages`; `ReliquaryPilgrims` → `Pilgrims` or
  `OutlanderCivil`; `WorkSite` → an existing faction, else **any def with the right group makers** (**T-216**).
  These defs are `DefOf` targets and cannot be deleted, so HF-1 overwrites them.
- **Mods create factions too:** VFE Tribals' wild men (**T-15**), WTL's add window (**T-86**), VEF's
  `forcedFactionData` (VFE Deserters, § *The roster is authorable*), and RimPacts' puppets, mercenaries and civil-war
  splits (`MOD-VERDICTS.md`) [V]. Faction Customizer, Worksites Expanded, VQE Ancients and Mechanoids: Total Warfare
  reference the same creators [I, metadata]. Each instantiates a def, so a pool stays ours when the def is ours.
  **HF-1 therefore covers every `FactionDef` in the database, not only the roster.**

#### What a faction def does not own

- **Gear is open by tag.** `PawnWeaponGenerator.TryGenerateWeaponFor` takes every weapon sharing one of the
  kind's `weaponTags`, with no tech test. `PawnApparelGenerator.CanUsePair` does the same for `apparelTags`, and
  **admits all apparel when the kind's list is empty**. `PawnTechHediffsGenerator.GenerateTechHediffsFor` does it
  for `techHediffsTags`. On disk, at least 16 mods ship weapons carrying a vanilla kind's weapon tag, 10 ship
  apparel carrying a vanilla apparel tag, and 1 ships implants [V, XML sweep of directly declared tags; inherited
  tags uncounted, so a floor].
- **Three free layers bypass the kind's tags** and draw from all apparel. **Warmth** has only a coarse
  Neolithic-versus-Industrial test (`CorrectFactionForApparel`). **Toxic resistance** has none. `apparelIgnoreSeasons`
  and `apparelIgnorePollution` switch those two off. **Vacuum** has no kind flag, only
  `ThingDef.apparel.canBeGeneratedToSatisfyVacuumResistance`. It fires for any pawn generated with no tile while
  the player's home is in vacuum (`NeedVacuumResistance`), which means once the colony is in orbit.
- **The faith dresses its members.** `Ideo.Notify_MemberGenerated` → `PreceptComp_Apparel_Desired` adds the
  ideo's desired apparel after gear. That item was drawn when the faith was made, from every stuffable apparel with
  `canBeDesiredForIdeo` (`PreceptWorker_Apparel`). `request.ForceNoIdeoGear` skips it.
- **Xenotypes have five inputs** (`XenotypesAvailableFor`, `GetXenotypeForGeneratedPawn`): the caller's
  `ForcedXenotype` or `AllowedXenotypes`; the faction's `xenotypeSet` while the kind's `useFactionXenotypes`
  (default true); the primary faith's memes' `xenotypeSet` (no `MemeDef` on disk sets one); the kind's `xenotypeSet`;
  and a Baseliner remainder. `XenotypeDef.doubleXenotypeChances` then adds hybrids; only Sanguophage has any.
- **Titles bring psylinks.** A kind with `titleRequired` or `titleSelectOne`, in a faction with no titles, takes the
  title from `RandomRoyalFaction()`, the Church, plus a psylink at the title's level.
- **Redress keeps the body.** `GenerateOrRedressPawnInternal` may reuse a world pawn. `RedressPawn` keeps its genes
  and implants, bar the `removeOnRedress*` ones, and re-rolls gear. `IsValidCandidateToRedress` checks the xenotype
  against the kind's and faction's sets but checks no implant. A `WorldPawnFactionDoesntMatter` request takes any
  faction's pawn (`docs/engine/health-and-death.md`).
- **Some kinds come from outside the faction.** `Faction.RandomPawnKind` reads the def's group makers, so HF-1
  covers it. But vanilla also names a `PawnKindDefOf` kind directly at about two dozen non-debug sites. Some pass a
  faction, such as `QuestNode_Root_OrbitalFugitive` (`Salvager_Elite`, Salvagers) and `SanguophageMeetingHost`. A
  titled quest asker's kind is drawn from the whole database (**T-214**).
- **Not every fielded thing is a generated pawn.** Vehicle Framework's NPC vehicles never pass `PawnGenerator`
  (**T-206**). Mechs summoned from gear follow the gear (VFE Pirates' spidermine and wardrone).
- **Scenario parts** add to generated pawns (`Scenario.Notify_NewPawnGenerating`, `Notify_PawnGenerated`). The
  scenario is ours.

#### Who adds to another faction's pool

**By XML patch** [V; 1.6-loading patch files, both roots]:
- **14 mods patch `FactionDef` group makers, member kinds or `xenotypeSet`:** VFE Settlers, Pirates and Empire;
  VPE; VRE Saurid, Hussar and Android; Uncompromising Tribal Faction; Alpha Mechs; Ushanka's Glittertech; Mechanoids:
  Total Warfare; Better Traders Guild; Biotech for Gravship; RimPacts.
- **9 patch `PawnKindDef` gear or xenotype fields:** VAE Armour; VWE Frontier; VAE Accessories; Uncompromising
  Tribal Faction; VFE Empire; Dwarves of the Rim; VRE Sanguophage; ETRT Tribal Apparel; Better Traders Guild.
- **Our patches win if they load last and replace whole nodes.** A mod patch on a vanilla abstract base
  (`OutlanderFactionBase`, `PirateBandBase`, `TribeBase`) reaches our defs only if ours inherit that base
  (ANDROIDS § 6, **T-02**). HF-1 and HF-2 defs inherit only our own bases.

**By C#** [V, decompiled 1.6 assemblies]:
- **Keyed to a kind's mod extension, so inert once every kind is ours:**
  - VEF's `PawnKindAbilityExtension` (`GenerateNewPawnInternal` postfix);
  - VPE's `PawnKindAbilityExtension_Psycasts`;
  - VQE Ancients' `PawnKindExtension_Experiment`, which draws random archite and metabolism genes from the whole
    `GeneDef` database;
  - VFE Pirates' warcasket completion, on a pawn already wearing one.
- **Not keyed to a kind:**
  - **VPE** gives a random psycaster path to any humanlike at `baseSpawnChance`, under its Basilicus storyteller
    only.
  - **Xenotype Spawn Control** (`GenerateGenes` prefix) forces a custom xenotype per faction or kind from its
    settings whenever the roll came out Baseliner. That is after WTL's xenotype filter, which never sees it.
  - **Ushanka's Glittertech** overclocks 2% of NPC weapons carrying its `CompOverclock`, which only its own weapons
    have.
- **Removing, not adding:** VRE Android strips android xenotypes from any set that does not name one. World Tech
  Level is HF-5.
- **Residual [I]:** the sweep found candidates by patch-class and target-member names in both heaps. A patch named
  neither way, on a member the funnel reaches, is not ruled out. HF-4 does not care.

#### Limits and consequences

- **HF-2's closure lasts only while nobody tags an item with our vocabulary.** We decide which items carry our tags,
  by patching them onto chosen `ThingDef`s, so a new mod item never joins silently.
- **Stuff stays open.** Any stuff with `allowedInStuffGeneration` can be rolled. The levers are
  `weaponStuffOverride` on a kind and `apparelStuffFilter` on a faction.
- **Factionless pawns are outside "every faction" but inside the band.** A quest that asks for no faction draws a
  random humanlike kind from the whole database (**T-214**). A factionless xenotype is drawn by
  `factionlessGenerationWeight` across every `XenotypeDef`. Only HF-4 and HF-5 reach these pawns.
- **The authored breach survives HF-4 by construction:** the Glitterites' list is Ultra. It does not survive HF-5's
  xenotype filter (**T-215**).
- **Build questions for #119:** where the per-faction allowlist lives; strip versus regenerate; how HF-4 orders
  against other postfixes on `GeneratePawn` (VFE Pirates, VQE Ancients, WTL's prefix).

### Open questions

- **Requirement, settled** ([`requirements/ERA.md`](../requirements/ERA.md), 2026-09-26): the test is era
  flavour and binds faction-less events, so AB-2's rows carry equal weight with AB-3; there is no floor, so a
  faction an advance leaves below the era is allowed; every faction and its spawn pools is hand-authored, which
  closes pawn-level contamination such as ANDROIDS § 6's android chance. Delivery by drop pod is routed above
  (*Delivery by drop pod*): pods are Industrial, and goods appearing at the map edge before then is acceptable.
  Hand-authored factions and pools are routed in *Hand-authored factions and spawn pools*
  ([#207](https://github.com/cjd721/Rimworld-Archinity/issues/207)).
- **Build — [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119):** where the breach flag lives,
  substitution or refusal per category, the part walk's type list.
