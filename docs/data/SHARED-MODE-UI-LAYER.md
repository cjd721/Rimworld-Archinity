# Shared mode + a client-local "two factions" presentation layer

**Question:** if we take Multiplayer's **shared mode** (one player faction, two humans)
and rebuild the *feel* of two factions as a client-local presentation layer we write
ourselves — how filterable is the vanilla 1.6 UI, and where would such a layer leak
into simulation?

**Date:** 2026-08-28. Companion to `MULTIFACTION-VANILLA-DLC.md`.

---

## 0. Method

Same two primary sources as the companion document, both real code:

- **RimWorld 1.6.4871** decompiled with `ilspycmd 8.2.0.7535 -p` → 9217 `.cs`.
  Namespaces map to directories (`rw/RimWorld/`, `rw/Verse/`, `rw/RimWorld.Planet/`).
- **Multiplayer 0.11.5** — *embedded upstream source* extracted from
  `1.6/AssembliesCustom/Multiplayer.dll` (393 `.cs`, git log `4a3be27 Version 0.11.5`).
  Not decompiler output.

Labels: **[CODE]** read in one of those trees · **[INFER]** deduced from code read ·
**[UNVERIFIED]** flagged, not confirmed. Nothing here was observed running.

### The governing invariant

MP is deterministic lockstep. Two regimes exist and the boundary is explicit in code
(`Multiplayer.cs:62-71`) **[CODE]**:

```csharp
public static bool Ticking => AsyncWorldTimeComp.tickingWorld || AsyncTimeComp.tickingMap != null || ConstantTicker.ticking;
public static Map MapContext => AsyncTimeComp.tickingMap ?? AsyncTimeComp.executingCmdMap;
public static bool InInterface => Client != null && !Ticking && !ExecutingCmds && !reloading;
```

- **Simulation** = tick + synced-command execution. Must be byte-identical on all
  clients. Anything read here must come from saved game state.
- **Interface** = `MapUpdate` / `OnGUI` / `Window.DoWindowContents`. Free.

A presentation layer is safe exactly insofar as it lives on the `InInterface` side and
never writes state that simulation reads.

---

## 1. The colonist bar — the user's literal question

**Verdict: filterable, and this is the easy one — but there is a live trap inside the
very method you would patch.**

### 1.1 Where entries are built

`rw/RimWorld/ColonistBar.cs` (567 lines) **[CODE]**:

- `cachedEntries` (`:44`), `cachedDrawLocs` (`:46`), `cachedReorderableGroups` (`:48`),
  `entriesDirty` (`:52`) — all **private instance fields on `ColonistBar`**.
- `Find.ColonistBar` is rooted on `UIRoot_Play`, **not on `Game`**, and `ColonistBar` is
  **not `IExposable`** — it is never saved **[CODE]**.
- `Entries` getter (`:92-100`) → `CheckRecacheEntries()` (`:218`) → rebuilds from
  `Find.Maps` → `mapPawns.FreeColonists` + `ColonySubhumansControllable` + colonist
  corpses, then caravans.
- Called from `ColonistBarOnGUI()` (`:144`), which runs only when
  `Event.current.type != EventType.Layout` — a pure render path.

**So the entry cache is genuinely client-local.** A Harmony postfix filtering
`cachedEntries` (plus the parallel `cachedDrawLocs` / `cachedReorderableGroups`, which
are index-aligned) is architecturally sound.

**Prior art: MP already does exactly this.** `ColonistBarCheckRecacheEntriesPatch`
(`Factions/MultifactionPatches.cs:129-157`) **[CODE]** transpiles the `Find.Maps` call
inside `CheckRecacheEntries` into `GetFilteredMaps()`, gated on
`Multiplayer.settings.hideOtherPlayersInColonistBar` — a **client-local** setting
(`Settings/MpSettings.cs:37`, scribed to the *mod config*, not the save). MP ships a
per-client colonist-bar filter and treats it as safe. So does our answer to the user's
question: **no, you will not see 30 pawns that aren't yours — this is filterable.**

### 1.2 The trap inside `CheckRecacheEntries`

`ColonistBar.cs:257-263` **[CODE]**, inside the render-path rebuild:

```csharp
foreach (Pawn tmpPawn in tmpPawns)
{
    if (tmpPawn.playerSettings.displayOrder == -9999999)
    {
        tmpPawn.playerSettings.displayOrder =
            Mathf.Max(tmpPawns.MaxBy(p => p.playerSettings.displayOrder).playerSettings.displayOrder, 0) + 1;
    }
}
```

`Pawn_PlayerSettings.displayOrder` is **saved state** — declared at
`rw/RimWorld/Pawn_PlayerSettings.cs:33` with the sentinel `-9999999`, and scribed at
`:210` **[CODE]**.

So a **pure UI method writes saved pawn state**, and the value written is derived from
`tmpPawns` — *the list we intend to filter*. Filter the bar, and a newly-arrived pawn
gets a different `displayOrder` on each client, or none at all on the client that
filtered it out.

`ColonistBar.Reorder` (`:327-379`) is worse: dragging a portrait rewrites
`displayOrder` across **`cachedEntries`** — the filtered cache — incrementing and
decrementing every other pawn's value. It is **not synced**: MP's `SyncMethods.cs:50`
registers `BillStack.Reorder` and nothing else named `Reorder` **[CODE]**, and a grep of
the whole MP tree finds no `displayOrder` sync field.

**How bad is it?** Bounded, because of who reads it back. Every consumer of
`displayOrder` in the entire game **[CODE]**:

| Site | Kind |
| --- | --- |
| `ColonistBar.cs:259,261` | the write above |
| `ColonistBar.cs:264,286` | `PlayerPawnsDisplayOrderUtility.Sort(tmpPawns)` — bar ordering |
| `ColonistBar.cs:353-377` | `Reorder` |
| `PawnTable_PlayerPawns.cs:11` | `LabelSortFunction` — Work/Assign/Restrict tab row order |

**Nothing in simulation reads it.** It is a display-ordering field and nothing else.

**[INFER]** So the divergence is *latent, not live*: it corrupts saved pawn state
differently on each client but no tick decision consumes it, so it will not desync. It
will silently reset to the host's values at every join point, because MP redistributes
the host's save (`SaveLoad.CreateGameDataSnapshot`). Cosmetically annoying; not
dangerous.

**Fix, cheaply:** prefix `CheckRecacheEntries` and pre-assign `displayOrder` for *all*
colonists deterministically (unfiltered) before the filter applies, or replace the
sentinel branch outright with our own deterministic assignment keyed on
`Pawn.thingIDNumber`. Then filter. ~20 LOC.

**This is the pattern to internalise: `CheckRecacheEntries` is a UI method that writes
saved state.** It is not the only one (§5).

### 1.3 What reads the cache back

The full readback surface, and every external caller **[CODE]**:

| `ColonistBar` member | Callers |
| --- | --- |
| `GetColonistsInOrder()` `:437` | `SelectorUtility.cs:15`; `ThingSelectionUtility.cs:187,216` (select-next/prev colonist hotkeys) |
| `MapColonistsOrCorpsesInScreenRect()` `:486` | `Selector.cs:425` (drag-box); `WorldSelector.cs:268` |
| `ColonistOrCorpseAt()` `:550` | `Selector.cs:519` (click); `WorldSelector.cs:359` |
| `TryGetEntryAt()` `:420` | `Targeter.cs:423` (targeting a pawn via its portrait) |
| `AnyColonistOrCorpseAt()` `:411` | `ColonistBarColonistDrawer.cs:224` |
| `Reorder()` `:327` | the reorder drag callback (writes `displayOrder`) |

**Every one is selection or targeting.** No caller feeds a synced decision *by way of
the set*.

That holds because of a deliberate MP invariant. `Find.Selector` is
`MapUI.selector` (`rw/Verse/Find.cs:62`), rooted on `UIRoot_Play`, **not `IExposable`**
— purely client-local **[CODE]**. And MP **blanks it for the entire duration of synced
command execution** (`AsyncTime/AsyncTimeComp.cs:254-255`, restored at `:304`)
**[CODE]**:

```csharp
prevSelected = Find.Selector.selected;
Find.Selector.selected = new List<object>();
```

— alongside forcing `Current.Game.currentMapIndex` to the command's map (`:242-243`).
MP is stating in code that **nothing may read local selection or current map during
synced execution**. Selection-derived values are instead captured at *issue* time on the
issuing client and serialized into the command payload — e.g.
`Find.Selector.SelectedZone` written into the packet at `Patches/Designators.cs:123`,
and `ITab_Genes.PawnForGenes(Find.Selector.SingleSelectedThing)` resolved in
`Syncing/Game/SyncDelegates.cs:486` **[CODE]**.

**Consequence for us:** drafting, camera-jump, group-select and hotkeys are all safe to
filter, because each resulting command names its specific pawn. Filtering the bar means
"I cannot select your pawns from my bar" — which is the feature.

---

## 2. Concurrent research — the one item that is *not* presentation

**Verdict: (b) a moderate fork — roughly 450–700 LOC.** Not a small patch, nowhere near
a redesign. The blast radius is far smaller than it looks.

### 2.1 The 1.6 shape

`rw/RimWorld/ResearchManager.cs:24-36` **[CODE]** — `currentProj` is confirmed a
**single field**:

```csharp
private ResearchProjectDef currentProj;                                    // :24
private List<KnowledgeCategoryProject> currentAnomalyKnowledgeProjects;    // :26
private Dictionary<ResearchProjectDef, float> progress;                    // :28
private Dictionary<ResearchProjectDef, int> techprints;                    // :30
private Dictionary<ResearchProjectDef, float> anomalyKnowledge;            // :32
public bool gravEngineInspected;                                           // :36
```

Two facts make this tractable:

1. **Progress is not on the Def.** `ResearchProjectDef` has no progress field;
   `ProgressReal => Find.ResearchManager.GetProgress(this)` (`:105`), `IsFinished`
   (`:120`), `CanStartNow` (`:164`) all derive from the manager's dictionary **[CODE]**.
   Two concurrent projects need **zero storage redesign** — they share `progress`, keyed
   by def.
2. **Anomaly already ships a multi-slot precedent.** `currentAnomalyKnowledgeProjects`
   is a per-category list of concurrent projects with a keyed
   `GetProject(KnowledgeCategoryDef)` accessor (`:46-53, :155-169, :518-540`) **[CODE]**.
   The template for an owner-keyed slot list already exists in the class.

### 2.2 Blast radius

Every external `currentProj`-dependent read, exhaustively **[CODE]**: **~26 touches, of
which only 6 are simulation.**

- **Simulation (6):** `JobDriver_Research.cs:11,38`; `WorkGiver_Researcher.cs:12,24,33`;
  `Building_ResearchBench.cs:14`; `CompUseEffect_FinishRandomResearchProject.cs:10,19`.
- **UI (~21):** `MainTabWindow_Research.cs` (a 1604-line file);
  `MainButtonWorker_ToggleResearchTab.cs:7`.
- **Alerts (5):** `Alert_NeedResearchProject.cs`, `Alert_NeedResearchBench.cs`,
  `Alert_NeedAnomalyProject.cs`.

### 2.3 The seam

`JobDriver_Research.cs:38` already calls
`Find.ResearchManager.ResearchPerformed(statValue * delta, actor)` — **the researcher
pawn is already an argument** **[CODE]**. `WorkGiver_Researcher.ShouldSkip(Pawn)` and
`HasJobOnThing(Pawn, …)` likewise. Only `PotentialWorkThingRequest` lacks a pawn, and it
merely gates "is any project running" → rewrite as "does any owner have a project".

**Per-pawn context is available at every simulation site that matters.** That is the
single biggest cost saver.

Recommended shape:

1. **Keep `currentProj` as owner-slot A; store slot B in our own `GameComponent`,** not
   in `ResearchManager.ExposeData`. Vanilla saves stay readable, MP's
   `Scribe_Deep(researchManager)` is untouched, and every unpatched vanilla read still
   finds a valid project. This is the save-compat firewall.
2. **Prefix `ResearchManager.ResearchPerformed`** (`:309`) — resolve the researcher's
   owner tag → that owner's project; replicate the ~12 lines of difficulty / `CostFactor`
   / records math (`:316-326`) against the resolved def. ~40 LOC. **This alone gives
   simultaneous progression.**
3. **Postfix `JobDriver_Research.get_Project`** using `__instance.pawn`. ~15 LOC.
4. **`WorkGiver_Researcher`** — pawn-routed. ~40 LOC.
5. **New synced start/stop taking `(ownerId, def)`**, registered via MP's `SyncMethod`.
6. **UI** — 200–350 LOC across four seams in `MainTabWindow_Research`
   (`UpdateSelectedProject` `:284`, `DrawStartButton` `:506`, progress panel `:388-415`,
   node colouring `:934,:962`). The Anomaly branch at `:389-390` **already draws two
   concurrent progress bars** — clone that layout.

### 2.4 Hazards

1. **Determinism (highest).** `ResearchPerformed` is **not synced** — it runs inside the
   deterministic tick on every client (MP syncs only
   `MainTabWindow_Research.DoBeginResearch` and `ResearchManager.StopProject`,
   `SyncMethods.cs:59-61`) **[CODE]**. Owner routing must therefore derive **only from
   saved pawn state**, never `Multiplayer.session.playerId` or the local player. Also:
   `SyncDictRimWorld.cs:1114` serializes a `ResearchManager` as "whatever
   `Find.ResearchManager` is" — a context-dependent zero-byte handle — so any new synced
   method must take an **owner id**, never a manager reference **[CODE]**.
2. **`FinishProject` recursion cross-talk.** `:405-413` auto-finishes unfinished
   prerequisites but `:484-487` clears only `currentProj`. If B's project completes A's
   as a prerequisite, slot A points at a finished def and re-enters `FinishProject` every
   tick — duplicate letters on both clients **[INFER]**. Needs a "clear any slot whose
   project `IsFinished`" postfix.
3. **Do not** postfix `GetProject()` / `IsCurrentProject()` to consult the *local*
   player. They are shared by simulation and UI; a local-player-dependent return value
   desyncs instantly. Add separate accessors.

**Out of scope:** leave Anomaly's `currentAnomalyKnowledgeProjects` single-slot —
already multi-slot by category, and doubling it multiplies UI cost for no benefit here
(Anomaly is not installed anyway).

---

## 3. The traps — where a filtering layer leaks into simulation

**This is the most valuable section. MP has already catalogued this exact bug class, and
the catalogue is readable.**

`mp/src/Source/Client/Patches/Determinism.cs` is **754 lines and 35 Harmony patches**
**[CODE]**, every one of them a place where vanilla either reads client-local state
inside simulation or mutates simulation state from a UI path. Its guard idioms are
uniformly one of `!Multiplayer.InInterface`, `Multiplayer.ExecutingCmds`, or
`AsyncWorldTimeComp.tickingWorld`.

The failure shape the coordinator named — A's client computes a filtered set, that set
feeds a decision, B computes a different set — has **four distinct sub-shapes** in this
codebase.

### Trap 1 — lazy caches whose *recompute moment* is UI-driven

The largest class. Vanilla caches are recomputed on first read; if the UI reads them,
the cache is populated at a client-local moment, and the cached value can differ.

MP guards, all `[CODE]`: `Pawn_AbilityTracker.AllAbilitiesForReading` (`:239`),
`SituationalThoughtHandler.CheckRecalculateSocialThoughts` / `AppendSocialThoughts` /
`UpdateAllMoodThoughts` / `Notify_SituationalThoughtsDirty` (`:316-395`),
`PawnCapacitiesHandler.GetLevel` (`:396`), `StatWorker.GetValue` (`:442`),
`DangerWatcher.DangerRating` (`:209`), `Zone.Cells` (`:174`), `Plan.Cells` (`:182`),
`Caravan.ImmobilizedByMass` (`:221`), `WealthWatcher.ForceRecount` (`:114`).

**Why this bites us specifically:** a filtering layer changes *which pawns each client's
UI touches*. Player A's client never renders player B's pawns → never triggers their
stat/thought/capacity cache recompute; player B's client does. Any of these caches whose
recompute has an observable side effect now differs.

**Mitigation:** our filter must never *widen* what the UI touches, and we must not add
new UI reads of un-guarded lazy caches. Filtering to a subset is the safe direction —
it reads strictly less. Verify against this list before touching a new getter.

### Trap 2 — UI paths with real side effects

The `ColonistBar.CheckRecacheEntries` → `displayOrder` write (§1.2) is one, and **MP
does not patch it**. Others MP *did* patch **[CODE]**:

- `PriorityWork.Clear` (`Determinism.cs:252`) — comment: *"This can get called in the UI
  but has side effects"*; guarded to `Multiplayer.ExecutingCmds`.
- `AutoSlaughterManager.Notify_ConfigChanged` (`:233`).
- `StoryWatcher_PopAdaptation.Notify_PawnEvent` (`:227`).
- `Pawn_RecordsTracker.ExposeData` (`:294`) — *"Remove mutation of `battleActive` during
  saving which was a source of non-determinism"*.
- `MainTabWindow.SetInitialSizeAndPosition` (`:668`) — guarded to
  `Multiplayer.InInterface`, because a window resize was reaching simulation.

**This is the trap class to audit hardest**, because the leak is invisible: a getter you
called for display purposes wrote a field.

### Trap 3 — `Find.CurrentMap` and camera state read inside simulation

The prior art the coordinator cited. MP's own instance, with its comment verbatim
(`Determinism.cs:687-705`) **[CODE]**:

> *"Due to an oversight, the vanilla method is using `Find.CurrentMap` rather than using
> `(Map)parms.target`. This causes bugs in the game, like mechanoids emerging from
> void/sand/random locations rather than water. For us, it currently causes desyncs with
> multiple maps active, so we need to fix it."*

Also `WorldObjectSelectionUtility.VisibleToCameraNow` (`:104`),
`MoteMaker.MakeStaticMote` (`:601` — skips `GenView.ShouldSpawnMotesAt` and
`MoteCounter.Saturated` precisely because both are current-map- and client-dependent),
and `GameConditionManager.MapBrightnessTracker.Tick` (`:508` — replaces `Time.deltaTime`
with a constant `1/60` because it was FPS-tied).

**For us:** if our layer introduces a notion of "my colony" and any code path resolves it
via `Find.CurrentMap` or the camera, and that path is reachable from a tick or a synced
command, it desyncs. Resolve ownership **only** from the owner tag in saved state.

### Trap 4 — non-determinism from infrastructure

`FastTileFinder.Query` (`:732`) **[CODE]**, comment: the vanilla implementation
race-fills a 50-slot array across parallel Unity Job batches, so *"thread scheduling
differs between machines"*; MP forces single-batch execution. Also
`PawnBioAndNameGenerator.TryGetRandomUnusedSolidName` (`:66`).

Not our doing, but it sets the bar: even *ordering* must be deterministic. Any collection
we build for the layer that later feeds a synced decision must have a stable sort — use
`Pawn.thingIDNumber`, never enumeration order of a `Dictionary` or `HashSet`.

### The rule that falls out

> **A client-local view may read anything and write nothing. Any value the layer computes
> that reaches a synced command must be captured at command-issue time on the issuing
> client and serialized into the payload — never recomputed during execution.**

That is precisely MP's own architecture: blank the `Selector`, pin the map, pass the
selection-derived value in the packet (§1.3).

### Where our owner tag should live

**[INFER]**, from the constraints above. A `GameComponent` holding
`Dictionary<int, ownerId>` keyed by `Pawn.thingIDNumber` is the soundest of the three
options proposed:

- It is **saved state**, so simulation may read it — which the research feature (§2)
  *requires*.
- It is a single object, so MP's existing `Scribe`/sync machinery covers it without a
  `ThingComp` def-injection into every pawn def.
- `thingIDNumber` is stable across save/load and is already MP's canonical pawn handle in
  `SyncDictRimWorld`.
- Mutating it must be a **synced method**, never a local write.

A `ThingComp` would also work and is more idiomatic, but requires patching pawn defs and
gives no advantage here. Do **not** use a client-local dictionary — the research feature
would then read local state inside the tick, which is Trap 3.

---

## 4. Letters, choice letters, alerts

### 4.1 Trap 5 — letter-stack membership is an input to synchronized state

**This is the best trap in the document, and MP has shipped it unfixed.**

The chain, every link **[CODE]**:

1. `LetterStack.ReceiveLetter` (`rw/Verse/LetterStack.cs:56`) does `letters.Add(let)`
   (`:80`) **and** `Find.Archive.Add(let)` (`:81`). It is called from the **tick** —
   `TickManager.cs:463` → `LetterStackTick` (`:154`) → `:161` — and from arbitrary
   ticking incident/quest code. So `letters` is mutated **inside simulation**.
2. `LetterStack` is **saved**: `ExposeData` at `:199-212` (`letters` by Reference,
   `letterQueue` Deep).
3. `Letter.cs:51`:
   ```csharp
   bool IArchivable.CanCullArchivedNow => !Find.LetterStack.LettersListForReading.Contains(this);
   ```
   **Cullability is a function of letter-stack membership.**
4. `Archive.CheckCullArchivables` (`rw/RimWorld/Archive.cs:81-103`) permanently removes
   non-pinned cullable archivables once their count exceeds
   `MaxNonPinnedArchivables = 200` (`:12`). It runs on **every** `Archive.Add` (`:40`).
   The `Archive` is saved (`:16-25`).
5. MP's `Letter` sync serializer writes `letter.ID` and reads it back by **scanning
   `Find.Archive.ArchivablesListForReading`** (`Syncing/Dict/SyncDictRimWorld.cs:1315-1322`).

**So:** a client that removes a letter from `letters` makes it *immediately cullable* on
that client alone. Past ~200 archivables the two clients cull **different sets**. Then
(a) a synced ChoiceLetter command from the other player deserializes to `null` on the
culling client, and (b) the saved Archive differs, so a rejoin hands over a game missing
entries the other client still references.

MP does exactly this in multifaction — `LetterStackReceiveOnlyMyFaction`
(`Factions/MultifactionPatches.cs:630-639`) postfixes `ReceiveLetter` with
`__instance.letters.Remove(let)` — and carries the comment **verbatim**:

> *"todo the letter might get culled from the archive if it isn't in the stack and Sync
> depends on the archive"*

Two further MP patches prove the Archive is treated as synchronized simulation state:
`Patches/UniqueIds.cs:105-121` blocks archiving of negative-ID interface-only letters,
and `Patches/Determinism.cs:190-207` (`SortArchivablesById`) forces `Archive.Add`'s sort
key to `Letter.ID` because `CreatedTicksGame` ties sorted nondeterministically **[CODE]**.

**Mitigation, and it is the single load-bearing rule of this whole document:**

> **Filter at draw time, never at list-membership time.**

Suppress rows inside `LetterStack.LettersOnGUI` (`:92`). `letters` then stays identical
on both clients, `CanCullArchivedNow` stays identical, culling stays deterministic, and
the sync serializer's archive scan stays resolvable.

### 4.2 Choice letters — hide the draw, never the letter

Every accept/reject option is a **registered synced command**
(`Syncing/Game/SyncDelegates.cs:340-373`) **[CODE]**: AcceptJoiner accept/reject,
AcceptVisitors, RansomDemand, the generic `ChoiceLetter.Option_Reject`, BabyToChild,
`GrowthMoment.MakeChoices`, CreepJoiner.

**[INFER]** Therefore one player's click applies to the shared faction and the other
player is affected whether or not they ever saw the letter. That is a **UX** problem
(you must agree who answers what), not a desync.

Removing a choice letter from `letters` is **unsafe** for two reasons beyond §4.1: it
breaks MP's `ArchivedOnly` close logic (`Patches/Letters.cs:77-88`) and
`DontRemoveGrowthMomentLetter` (`:109-115`), whose comment documents that sync data
reads the letter **from the stack, not the archive** — the mirror image of the cull
hazard **[CODE]**.

Timeouts: MP **disables vanilla auto-open entirely**
(`Patches/Letters.cs:127-131`, `DontAutoOpenLettersOnTimeout.Prefix() => Multiplayer.Client == null`)
and substitutes `CloseDialogsForExpiredLetters` (`:32-75`), which invokes a registered
default choice inside the tick on every client **[CODE]**. MP flags the area itself:
`Letters.cs:12`, `// todo letter timeouts and async time`. Expect a hidden letter to
still auto-resolve on both clients.

### 4.3 Alerts — safe, with one edge

`AlertsReadoutUpdate` (`rw/RimWorld/AlertsReadout.cs:92`) is called only from
`UIRoot_Play.cs:67`; `AlertsReadoutOnGUI` (`:278`) only from `UIRoot_Play.cs:33`.
Recompute is round-robin, 1/24th of alerts per frame (`:106-111`). `Alert.Recalculate`
(`rw/RimWorld/Alert.cs:130-138`) writes only `cachedActive`/`cachedLabel`, and
`AlertsReadout` has **no `ExposeData`** — not saved **[CODE]**. **Pure UI, recomputed
per-client per-frame. Safe to filter.**

One edge, **[CODE]**: `AlertsReadout.cs:231` calls `Alert.AlertActiveUpdate`, and
`Alert_Critical.cs:24-31` overrides it to fire `Messages.Message(...)` with `historical`
defaulting true (`rw/Verse/Messages.cs:39`), which reaches `Find.Archive.Add(msg)`
(`:59-61`). So *which client shows a critical alert already perturbs the saved archive*,
and MP does not patch this. **Filter at `AlertsReadoutOnGUI` / `DrawAt`, not at
`CheckAddOrRemoveAlert`.**

---

## 5. The quest tab

**Verdict: SAFE — and again MP has already built exactly this.**

`SortQuestsByTab` (`rw/RimWorld/MainTabWindow_Quests.cs:288-311`) reads
`Find.QuestManager.questsInDisplayOrder`, filters through `ShouldListNow` (`:1273-1300`,
which reads only `hidden`, `State`, `dismissed`, `hiddenInUI`) plus the search box, into
a scratch list. `selected` (`:23`) is a plain window field, never exposed —
**client-local** **[CODE]**.

MP's prior art: `MainTabWindow_QuestsShouldListNowPatch`
(`Factions/MultifactionPatches.cs:42-58`) prefixes `ShouldListNow` and forces
`__result = false` for another player's quests, gated on
`Multiplayer.settings.hideOtherPlayersQuests` — declared at `Settings/MpSettings.cs:38`,
scribed into **mod config**, toggled live in the UI at `MultifactionPatches.cs:115-122`
with no sync call. The paired `MainTabWindow_QuestsDoRowPatch` (`:19-40`) only tints and
tooltips. Neither touches game state **[CODE]**.

**Acceptance is synced.** The Accept button (`MainTabWindow_Quests.cs:603-605`) →
`Quest.Accept`, registered at `Syncing/Game/SyncMethods.cs:156`. Reward choice
(`:1022-1025`, `choice.Choose(...)`) is intercepted by `Patches/Patches.cs:394-424` and
routed through `PatchQuestChoices.Choose`, registered at `SyncMethods.cs:157` **[CODE]**.

**Two rules:** filter only at `ShouldListNow` / row draw — never filter
`QuestManager.QuestsListForReading` itself. And never use `dismissed` or `hiddenInUI` as
your filtering mechanism: `dismissed` is a **synced field** (`SyncFields.cs:140`, watched
at `:288-292`) **[CODE]**.

Caveat, **[INFER]**: a hidden quest still expires, and either player can accept a quest
the other never saw. UX, not desync.

---

## 6. What is genuinely shared-only

Rooting verified in `rw/Verse/Game.cs` and `rw/Verse/Find.cs` **[CODE]**. Verdicts:
**(a)** impossible · **(b)** possible as pure UI · **(c)** possible only by forking
simulation state.

### 6.1 The good news: the policy databases are (b)

| Piece | Root | Assignment lives on | Verdict |
| --- | --- | --- | --- |
| `outfitDatabase` | `Game.cs:53` | `Pawn_OutfitTracker.curApparelPolicy` (`:9`, saved `:50`) | **(b)** |
| `drugPolicyDatabase` | `Game.cs:55` | `Pawn_DrugPolicyTracker.curPolicy:12` | **(b)** |
| `foodRestrictionDatabase` | `Game.cs:59` | `Pawn_FoodRestrictionTracker.curPolicy:11` | **(b)** |
| `readingPolicyDatabase` | `Game.cs:57` | `Pawn_ReadingTracker` | **(b)** |

**The assignment is per-pawn**, so sharing the database is a clutter problem, not a
simulation problem. Filtering `Dialog_ManageApparelPolicies` by owner is pure UI. MP
forks these in multifaction only for **ID-space** reasons
(`FactionWorldData.ReassignIds`, `:50-61`) — not simulation ones. Caveat: create/delete
mutates `UniqueIDsManager` and delete nulls other pawns' assignments
(`OutfitDatabase.cs:44-53` and siblings) — those must be synced commands.

### 6.2 Work priorities need no split at all

`Pawn_WorkSettings.priorities` is a per-pawn `DefMap<WorkTypeDef,int>`
(`rw/RimWorld/Pawn_WorkSettings.cs:12`, saved `:69`). **No global ordering state
exists** — WorkGiver order is recomputed per pawn from
`DefDatabase<WorkTypeDef>.AllDefsListForReading` (`:207-256`), i.e. Def order, identical
on both clients. Work-tab columns come from `PawnTableDef.columns`, a Def; **vanilla 1.6
has no drag-to-reorder of work columns** **[CODE]**.

The one shared bit is `useWorkPriorities`, read *inside* `GetPriority` (`:164`), where it
silently rewrites every priority to 3 — **(c)**. **Set it ON at game start and lock the
checkbox** (`MainTabWindow_Work.cs:42`).

### 6.3 `PlaySettings` splits 14 / 17

**[CODE]** — the crux distinction the coordinator asked for.

**Simulation-affecting (14) — (c), lock globally:** `autoHomeArea`
(`AutoHomeAreaMaker.cs:11` writes the Home area on build), `autoRebuild`
(`ThingUtility.cs:159,168` spawns blueprints on destroy), `useWorkPriorities`, and the
eleven `defaultCareFor*` fields (`Pawn_PlayerSettings.cs:360,364,373` set `medCare` at
pawn init — a one-shot mismatch, but still must be synced).

**Pure display (17) — (b), safe as a client-local shadow struct:** `showZones`,
`showBeauty`, `showRoomStats`, `showColonistBar`, `showLearningHelper`,
`showRoofOverlay`, `showTemperatureOverlay`, `showFertilityOverlay`,
`showTerrainAffordanceOverlay`, `showPollutionOverlay`, `showVacuumOverlay`,
`lockNorthUp`, `usePlanetDayNightSystem`, `showWorldFeatures`,
`showImportantExpandingIcons`, `showBasesExpandingIcons`, `showExpandingLandmarks`.

### 6.4 Areas and zones

- **Zones / stockpiles: (c).** MP forks `zoneManager` *plus* `haulDestinationManager`,
  `listerHaulables`, `resourceCounter`, `listerFilthInHomeArea`, `listerMergeables`
  (`FactionMapData.cs:14-24`) **[CODE]** — the haul-target listers are derived caches of
  zone state, which is why a zone split cannot be pure UI. In shared mode both players
  necessarily edit one set. Only *visibility* is (b).
- **Area restrictions: (b), effectively free.** Which area a pawn obeys is per-pawn:
  `Pawn_PlayerSettings.allowedAreas` is a `Dictionary<Map,Area>` (`:15`, saved `:228`)
  **[CODE]**. Each player can own distinct `Area` objects inside the one shared
  `AreaManager`.
- **Hard budget:** `AreaManager.MaxAllowedAreas = 10` (`AreaManager.cs:14`), minus the
  4–5 special areas created at `:32-41` **[CODE]** — realistically **~5 custom areas
  total for two players**. Plan for it.

### 6.5 Genuinely (a) or (c), no escape

| Piece | Root | Verdict |
| --- | --- | --- |
| **Storyteller** | `Game.cs:43`, saved `:423` | **(a)** — one player faction, one incident stream. No UI split exists. |
| **Faction goodwill** | `Faction.relations` (`Faction.cs:24`, saved `:277`), stored bidirectionally (`:402-407,:443-449`) | **(a)** — raid/trade decisions read `RelationKindWith(OfPlayer)`. |
| **Research** | `Game.researchManager` (`:37`, saved `:417`) | **(c)** — MP forks it per faction; in shared mode see §2. |
| **`history` / `storyWatcher`** | `Game.cs:45 / :33` | **(c)** — feed threat scaling. |
| **`uniqueIDsManager`** | `Game.cs:71` | **(a)** — every ID allocation is a sync point. |
| **`questManager`** | `Game.cs:73` | filter **(b)**, decisions **(c)** — see §5. |
| **`letterStack`** | `Game.cs:35` | filter at draw **(b)**; see §4.1 for why membership is (c). |
| **`ideoManager`** | on **`World`**, not `Game` (`World.cs:17`) | one primary ideo — but Ideology supports per-pawn ideos, so "two cultures" is **(b)** at pawn level. |

Also necessarily shared, not forked by MP **[CODE]**: `tickManager` (`:61`),
`gameEnder` (`:41`), `taleManager`/`playLog`/`battleLog` (`:47/49/51` — per-player filter
is (b)), `studyManager` (`:77`), `analysisManager` (`:39`, Odyssey scanning),
`entityCodex`, `hiddenItemsManager`, `relationshipRecords`, `transportShipManager`
(`:87/85/83/75`). `customXenogermDatabase` / `customXenotypeDatabase` (`:79/81`) behave
like the policy databases — catalogues with per-pawn use, so **(b)**.

---

## 7. Bottom line

**Shared mode + a presentation layer is the sounder bet, and the vanilla UI is more
filterable than expected.** The colonist bar, quest tab, alerts and letter *rendering*
are all client-local and MP has already shipped per-client filters for two of them.

Three things to get right:

1. **Filter at draw time, never at list-membership time.** Every hazard in §4 traces to
   `Letter.cs:51` and `Letters.cs:108` making letter-stack membership an input to
   synchronized logic.
2. **Neutralise the two known UI-writes-simulation sites** before filtering:
   `ColonistBar.CheckRecacheEntries`'s `displayOrder` assignment (§1.2, ~20 LOC) and
   anything on MP's `Determinism.cs` list you newly touch (§3, Trap 2).
3. **Put the owner tag in a saved `GameComponent` keyed by `Pawn.thingIDNumber`**, mutate
   it only through a synced method, and never resolve ownership from
   `Multiplayer.session.playerId`, `Find.CurrentMap`, or `Find.Selector` inside a tick.

Concurrent research is the only wishlist item that changes simulation, and at ~450–700
LOC with a clean seam at `ResearchPerformed(amount, Pawn)` it is affordable.
