# Era

## Purpose and scope

> **Authority correction — 2026-09-13.** Completing the era capstone research project
> is the trigger for `AdvanceEra()`, exactly as in the progression mod. The node's
> prerequisites may encode whatever story conditions the boundary needs. There is no
> altar rite and no separate player confirmation between project completion and the
> advance. [#113](https://github.com/cjd721/Rimworld-Archinity/issues/113) is resolved by
> this requirement; only the implementation hook remains for the spec.

**What the campaign's era is, where it is stored, and how long the colony has been in it.**

Everything in the campaign hangs off the era, and until this document existed nothing owned
it. [#7](https://github.com/cjd721/Rimworld-Archinity/issues/7) resolved the *mechanism choice*
— World Tech Level for the ceiling, Ignorance Is Bliss for the band, one operation of ours for
the advance — and then closed. [#60](https://github.com/cjd721/Rimworld-Archinity/issues/60)
built [`PRESSURE.md`](PRESSURE.md)'s threat-point composition on **capped time within the
current era**, could find no document holding that number, and recorded it as an ownerless gap.
The progression grids
([#30](https://github.com/cjd721/Rimworld-Archinity/issues/30),
[#34](https://github.com/cjd721/Rimworld-Archinity/issues/34)) read it next. This document is
that owner ([#109](https://github.com/cjd721/Rimworld-Archinity/issues/109)).

> **Correction — 2026-09-17, [#128](https://github.com/cjd721/Rimworld-Archinity/issues/128).**
> This paragraph previously named `CHARTING.md` as a reader of the era clock. It is not one:
> [`CHARTING.md`](CHARTING.md) gates on research, not on the clock — *"the era knob is a rung
> on a `ResearchProjectDef`"* — and no `CurrentEra` or `TicksInCurrentEra` read appears in it.
> [`PRESSURE.md`](PRESSURE.md) and the progression grids are the real consumers.

This document owns:

- the **era clock** — the current era, the tick each era began, and the retained history of
  every boundary crossed;
- **`AdvanceEra()`** — the single operation that raises the era, what it writes, from where,
  and why it is the only writer;
- the **persistence contract** every other spec reads through, and what a save that predates
  the clock sees;
- the **second writers** that must be shut off, and the multiplayer consequences of each;
- whether **above-era structures and events seeded on the player's own map** can be removed,
  timed to their era or replaced, and by which routes — § *Above-era content seeded on the
  player's own map* at the end of this document
  ([#153](https://github.com/cjd721/Rimworld-Archinity/issues/153)).

It does **not** own: how long an era *should* last, or what era time is *worth* — those are
Balance, fog on [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2), and the era-length
table in [`docs/engine/world-time-and-layers.md`](../engine/world-time-and-layers.md) § *Time*
is campaign design input rather than an engine fact. It does not own **what the capstone is**
or what research it requires ([`RESEARCH.md`](RESEARCH.md) and
[#41](https://github.com/cjd721/Rimworld-Archinity/issues/41)). The capstone's completion
itself is the trigger; this document owns the hook that turns that completion into the
single `AdvanceEra()` call.
It does not own **what becomes available at each era**
([`docs/progression/`](../progression/README.md)), nor the **filter set** WTL runs (#7 froze
those twenty-four toggles and this document does not reopen them).

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
    int  TicksInCurrentEra      => Find.TickManager.TicksGame - CurrentEraStartTick
    int  StartTickOf(TechLevel) => first boundary with that era, or -1
```

**Prior eras' boundaries are retained — all of them — and this is a design decision with a
consumer, not tidiness.** Two reasons, in order of force:

1. **[`PRESSURE.md`](PRESSURE.md) contains a contradiction that only a retained history
   resolves.** Its § *The build* table takes the era term as *"ticks since the era-start stamp,
   through a curve that reaches a ceiling"* — which resets at every boundary. Its § *Verification*
   check 2 requires that points *"must not reset at the next `AdvanceEra()`"*. Both cannot hold
   of a single `int EraStartTick`. They both hold of

   > `eraTime = Σ over every boundary e of  cappedCurve( ticks spent in e )`

   which climbs within an era, flattens at that era's ceiling, and **adds** rather than
   restarting at the seam — which is also #7 § 6's *"no reset and no spike at a boundary … the
   budget is continuous across the seam."* The retained log is what makes that sum computable.
   The contradiction is **recorded here rather than repaired in `PRESSURE.md`**, which this
   document does not own. The full replacement text for that document's era-term row, the
   sentence under it and its *Outstanding decisions* bullet is written out verbatim on
   [#109](https://github.com/cjd721/Rimworld-Archinity/issues/109) **and is being applied by the
   orchestrator** — it is not a hand-off awaiting an owner, which matters because
   [#60](https://github.com/cjd721/Rimworld-Archinity/issues/60), the ticket that raised the gap,
   is **closed**.

   > **The balance consequence of the sum, named because the spec must not hide it.** Under
   > `Σ cappedCurve`, the era term's own ceiling is **six times a single era's cap** rather than
   > one era's — a six-era campaign that reaches every ceiling contributes six times what the
   > single-stamp reading would at the same moment. That is the intended shape (pressure
   > accumulates across the campaign rather than resetting), but it means the per-era cap must be
   > authored at roughly a sixth of whatever a reader of the old row would have guessed.
   > **The number is Balance's**, fog on [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2);
   > this document owes only the warning that the unit changed.
2. **The progression grids ask "when did we enter era X", not "how long in this one".**
   [#30](https://github.com/cjd721/Rimworld-Archinity/issues/30) and
   [#34](https://github.com/cjd721/Rimworld-Archinity/issues/34) fill a column per era; a beat
   that wants *"180 days after the Medieval gate"* needs `StartTickOf(Medieval)` after the
   colony has left Medieval behind.

The cost of retaining is six rows of `(byte, int)` for a six-era campaign. `CurrentEraStartTick`
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
    4. boundaries.Add(new EraBoundary(next, Find.TickManager.TicksGame))
```

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

**What Lemmy gets *right*, recorded because an earlier draft of this section got it backwards.**
`WorldEraManager.InitializeWorldTechLevelAccess` handles the auto-property correctly and
explicitly: `AccessTools.Field(type, "Current")` → null → `AccessTools.Property(type, "Current")`
non-null → `AccessTools.Field(type, "<Current>k__BackingField")` → and, failing that, a
`GetFields(Static | Public | NonPublic)` scan for the first static `TechLevel` [V]. The engine
fact in *Cost* below is real and our shim must handle it; **the claim that this mod trips over it
is false and is withdrawn.** Its defect is the missing second write, not the reflection.

**What calls it.** Completion of an authored era-capstone `ResearchProjectDef` calls
`AdvanceEra(next)` once. The project may be gated by any combination of prerequisites,
resources, exemplars or instruction, so story purpose belongs in the node rather than in a
second rite. The implementation must identify capstones explicitly, run on the synced
research-completion path, guard duplicate completion and preserve the rule that
`AdvanceEra()` has no other gameplay caller. A debug route still needs its own treatment.

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
| the same description | *"Era began: day N — n days here"*, from `CurrentEraStartTick` | one postfix on `WITab_Planet.get_Desc`, ~10 lines |
| the boundary log | *"Neolithic day 0 · Medieval day 96 · Industrial day 310"* | **not a tooltip on the line above** — see below. A `FillTab` postfix with its own layout, ~40 lines |
| the crossing itself | the capstone project's completion **is** the event | the era-capstone project and `AdvanceEra()` hook |
| pressure readout | era time as a named contributor | [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61)'s surface, supplied by [`PRESSURE.md`](PRESSURE.md) |

**The boundary log cannot be a tooltip on the description line, and an earlier draft of this
section said it could.** `WITab_Planet.get_Desc` is a `string` property; a postfix on it has
`ref string __result` and **no `Rect`**, so there is nothing for `TooltipHandler.TipRegion` to be
given. Showing the log means a postfix on `WITab_Planet.FillTab` that lays out its own row and
calls `TipRegion` against that rect — which is a different patch, with layout of its own, and it
is priced accordingly in *Cost* rather than as the fifteen lines the tooltip would have been.
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

> **The `Rand` half is worse than a single draw, and an earlier draft understated it.** The loop
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

**An earlier draft priced this at ~150 and both of the differences are real, not padding.** The
boundary readout is a layout patch rather than a tooltip (§ 5), and the shim is not twenty-five
lines: the nearest shipped equivalent, `LemProgress.Systems.WorldEraManager`'s WTL access, is
**~80 lines with its assembly scan and its four-step auto-property fallback** [V] — and ours
needs the same fallback plus a second member (`GameComponent_TechLevel`) that Lemmy never
resolves. Pricing the shim at Lemmy's size is the honest read; pricing it at a quarter of that
was wishful.

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

**Saved state added by this document: one list of `(TechLevel, int)` pairs.** Nothing else.
The era itself stays WTL's; research stays `ResearchManager`'s; era *time* is computed from
`Find.TickManager.TicksGame`, which is synchronised simulation state by construction.

**What must be a synced command, and what already is.**

- **Superseded caller analysis: `AdvanceEra()` called from a ritual outcome worker needs no sync plumbing** — a conditional,
  and the condition is not yet met: **no document builds that ritual** (§ 3, *What calls it*). The
  bullet establishes that the ritual route *would* be safe, not that it is the route. The
  citation is the lord tick, not the component tick. `LordJob_Ritual.ApplyOutcome` fires
  from a `StateGraph` transition's pre-action, which runs under
  `LordManager.LordManagerTick()` → `Map.MapPostTick()` → `TickManager.DoSingleTick()` [V,
  `Verse.Map.MapPostTick` calls `lordManager.LordManagerTick()`]. That is simulation, executed
  identically on both clients.
  > **An earlier draft cited `docs/engine/determinism.md` § *What is on the synced tick and what
  > is not* for this. That table covers `WorldComponentTick`, `GameComponentTick` and
  > `Thing.Tick` and says nothing about Lords** — it is the right authority for the two bullets
  > below and the wrong one for this. The conclusion is unchanged; the anchor is corrected.
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
- **`AdvanceEra()` draws no random number**, which is a rule rather than an observation. Every
  write is a plain assignment. If a future beat wants a roll at a boundary, it belongs in the
  rite's outcome worker — already on the tick — and not here.
- **Nothing here is a `ModSettings` field.** WTL's twenty-four filter toggles *are* settings and
  are therefore part of the sync surface (**T-18**); #7 froze them, and a mismatch between the
  two clients is a divergence this document cannot detect. That is an argument for recording
  the frozen set in the repo, not for reading settings at runtime.
- **Session shape.** [#23](https://github.com/cjd721/Rimworld-Archinity/issues/23) settled
  shared: one player faction, one colony, Async Time on. The era is world-scoped and
  faction-independent, so Multiplayer's `FactionRepeater` machinery does not apply to it.

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
  trade stock. Loud enough, and strictly better than throwing inside a rite.
- **A legacy save's era time reads as the whole game.** § 4's seed, by design. It over-states
  rather than under-states, so a capped curve sits at its ceiling instead of at zero. Say so to
  whoever balances it.
- **The rite fires twice.** The one-rung guard rejects the second call with `Log.Error` and
  changes nothing. The log stays append-only and no boundary is duplicated.
- **`Filter_Factions` is switched back on.** § 6b re-arms a runtime faction generator against
  **T-07**. This is the single settings change that can break the world irrecoverably, and it
  is worth writing on the frozen-settings list in bold.

---

## Status

**Evidence class: READ.** Settled against the 1.6 `Assembly-CSharp.dll`, `WorldTechLevel.dll`
1.6 (`…/294100/3414187030/1.6/Lunar/Components/WorldTechLevel.dll` — **not** `1.6/Assemblies/`,
which holds only the Lunar loader), `VFETribals.dll` 1.6, `LemProgress.dll` 1.6, and
`0MultiplayerAPI.dll` 1.6. No stub, no launch.

**Verified available mechanisms.** Every mechanism the build composes is read out of a
decompiled assembly and marked [V] where claimed: WTL's scribed component and its volatile
mirror, `Game.FillComponents`, `GameComponent.FinalizeInit`, the VFE Tribals T-11 workaround,
the synced-tick table, and both second writers.

**Selected: nothing.** This is a proposed design. **The claim that these verified mechanisms
compose into a working era clock is [I] by construction** and stays [I] until something is
built and loaded twice.

**Not ours:** how long an era lasts, what era time is worth, and the shape of the capped curve
— all Balance, fog on [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2).

**The contract other specs may rely on**, stated so nobody re-derives it:

| Read | Returns |
|---|---|
| `GameComponent_Era.CurrentEra` | the era, `TechLevel` |
| `GameComponent_Era.CurrentEraStartTick` | absolute `TicksGame` of the current boundary |
| `GameComponent_Era.TicksInCurrentEra` | derived; what #60 asked for |
| `GameComponent_Era.StartTickOf(TechLevel)` | absolute tick, or `-1` if never entered |
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

  > **An earlier draft claimed Node Research prefixes `AdvanceTechLevel` to `false` to stop
  > exactly this, cited to `docs/data/PARTS-BIN.md`. That is withdrawn.** Node Research
  > (`3729878405`) **is not in either corpus root** and is absent from `MOD-SNAPSHOT.md`, so its
  > assembly cannot be read and the claim is **[I]** by
  > [`docs/agents/capability-research.md`](../agents/capability-research.md) § *Inherited
  > claims* — and false read as a present-tense fact about this load order. A corpus-wide sweep
  > for `AdvanceTechLevel`, both heap halves, returns **only** VFE Tribals' three copies and
  > `LemProgress.dll` [V]. **Nothing in the corpus suppresses the detector**, and the one mod
  > that hooks the ladder at all — Lemmy, via a prefix on `AdvanceToEra` that returns **`true`**
  > [V] — *amplifies* it. The design argument against a poll stands on its own and never needed
  > the third party.

`docs/data/PARTS-BIN.md` § 5.3 already files VFE Tribals as **RESTAT leaning REBUILD** and says
the ladder is *"five XML defs and one `GameComponent`"*. Reading the assembly agrees, and adds
the reason to rebuild rather than restat: the era advance has to sit behind the altar and write
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

**Why the `#US` half is not optional here, contra an earlier draft of this note.** That draft
said a null-interleaved pass "is not applicable to a field or type *name*". **That is wrong, and
this sweep is its own counter-example:** the `#US` half of `EraAdvancement` returns a hit in
`LemProgress.dll` that the ASCII half does not, because Lemmy reaches VFE Tribals and WTL
entirely through `AccessTools.TypeByName` / `AccessTools.Field` **string arguments** — which is
exactly where a type or member *name* lives in the `#US` heap. Any mod that touches another mod
reflectively is invisible to the ASCII half alone. The negative above survives; the reasoning
that would have justified skipping the second pass does not, and skipping it would have hidden
the one mod in the corpus that manipulates the era ladder from outside.

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
3. **Retention.** After two advances, the boundary tooltip must list three rows and the first
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
  each era's cap is the same. Fog on [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2).
  **The unit changed** — under `Σ cappedCurve` the term's ceiling is six era-caps, not one (§ 2)
  — so a per-era cap authored against the old single-stamp reading will be roughly 6× too large.
- **`PRESSURE.md`'s era term needed one edit and this document did not make it.** § 2 shows the
  single-stamp reading contradicts that document's own Verification check 2. **This is not an
  open hand-off:** the full replacement text — the term-table row, the sentence under it, and the
  *Outstanding decisions* bullet — is written out verbatim in the resolution on
  [#109](https://github.com/cjd721/Rimworld-Archinity/issues/109) and **is being applied by the
  orchestrator**. Recorded as a row here only so a reader of this document knows the change
  happened and why, not as work awaiting an owner — which matters, because
  [#60](https://github.com/cjd721/Rimworld-Archinity/issues/60), the ticket that raised the gap,
  is closed and #109 closes with this resolution.
- **Era *lengths* have no requirements owner.** `docs/engine/world-time-and-layers.md` § *Time*
  carries Conrad's target lengths and says explicitly that they are campaign design input rather
  than an engine fact; `docs/requirements/` holds no document that owns them and
  `docs/progression/` holds only a README. **Stated as a gap, not handed off** — the owning
  document would be a progression requirement, and
  [#30](https://github.com/cjd721/Rimworld-Archinity/issues/30) is the nearest live ticket.
- **Whether the boundary log is shown to the player at all**, or only fed to the pressure
  readout. § 5 proposes a tooltip; it is a design call, not a capability one.
- **Whether a beat may read `StartTickOf` for an era the colony has left.**
  [`CHARTING.md`](CHARTING.md) is the consumer; the contract in *Status* supports it either way.

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
  map-seeded, so whether it may be expected to be opened on day one is a story call.

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
    [#180](https://github.com/cjd721/Rimworld-Archinity/issues/180)'s, whose single `PrefabDef
    AncientUplink` funnel reaches every arrival route.
  - **Anomaly** — `VoidMonolith` on `Base_Player`. Whether it counts as above-era is a story call.
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

- **Story — Conrad:**
  - Is a replacement a fixture in the yard (AE-7) or a place to go (AE-8)?
  - Does the mechanitor arrive at Industrial at all?
  - Does Anomaly's monolith count?
- **Build — [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119):**
  - the no-op step for AE-3;
  - AE-5's once-only guard;
  - the defender genstep for AE-7;
  - where AE-8's quest is given from.
- **[#22](https://github.com/cjd721/Rimworld-Archinity/issues/22):**
  - § 2 per the list above;
  - the T-166 ship-part incidents as arrivals.
- **[#180](https://github.com/cjd721/Rimworld-Archinity/issues/180):** the uplink as a giver.
- **Unowned:** whether a `Base_Player` child or a modded player-settlement generator bypasses
  AE-3. Vanilla's two children (`BasePlayer_SecondArchonexusCycle`, `…Third…`) inherit it [V].
