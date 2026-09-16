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
[`CHARTING.md`](CHARTING.md) and the progression grids
([#30](https://github.com/cjd721/Rimworld-Archinity/issues/30),
[#34](https://github.com/cjd721/Rimworld-Archinity/issues/34)) read it next. This document is
that owner ([#109](https://github.com/cjd721/Rimworld-Archinity/issues/109)).

This document owns:

- the **era clock** — the current era, the tick each era began, and the retained history of
  every boundary crossed;
- **`AdvanceEra()`** — the single operation that raises the era, what it writes, from where,
  and why it is the only writer;
- the **persistence contract** every other spec reads through, and what a save that predates
  the clock sees;
- the **second writers** that must be shut off, and the multiplayer consequences of each.

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
