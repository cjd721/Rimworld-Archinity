# Shared mode: MP's client-local / synced boundary, and what a UI ownership layer must respect

**Question.** If we run **shared mode** (one player faction, two players) and rebuild the *feel* of
two factions as a client-local presentation layer we write ourselves — filtered colonist bar,
filtered letters, filtered quest tab, per-player "my pawns" — where exactly is MP's client-local /
synced boundary, and what would break?

**Method and date.** 2026-08-28. Read against `rwmt/Multiplayer` at commit
**`4a3be276bbf90cc597abfa5b299935ca8eeeb285`** (v0.11.5, 2026-04-29), confirmed to be the commit
shipped in the installed `1.6/AssembliesCustom/Multiplayer.dll` (see
`MULTIFACTION-REVERSIBILITY.md` for the version-matching method). RimWorld 1.6 vanilla behaviour
verified by decompiling `Assembly-CSharp.dll` with `ilspycmd`. Labels: **[code]** verified in
source; **[docs]** official MP wiki; **[community]**; **[inferred]**. Nothing observed in-game.

**Headline.** The boundary is real, coherent, and enforced by a mechanism that is *stricter* than a
naive read suggests — but it is **not documented for mod authors anywhere**. And MP already ships a
working, shipped-to-users precedent for exactly the layer being proposed.

---

## 1. The boundary rule

### 1.1 The gates, in code

`Source/Client/Multiplayer.cs:60-72` [code]:

```csharp
public static bool ExecutingCmds => TickPatch.currentExecutingCmdType != null;
public static bool Ticking => AsyncWorldTimeComp.tickingWorld
                           || AsyncTimeComp.tickingMap != null
                           || ConstantTicker.ticking;

public static bool dontSync;
public static bool ShouldSync => InInterface && !dontSync;
public static bool InInterface =>
    Client != null
    && !Ticking
    && !ExecutingCmds
    && !reloading
    && Current.ProgramState == ProgramState.Playing
    && LongEventHandler.currentEvent == null;
```

Read them as a two-state machine over one process:

| State | `InInterface` | Meaning |
|---|---|---|
| **Interface** | `true` | Drawing, input handling, tooltips, gizmo construction. Runs at frame rate, differs freely between clients. **Nothing here is simulation.** |
| **Simulation** | `false` | Inside a tick (`Ticking`), inside a replayed command (`ExecutingCmds`), inside a save/reload (`reloading`), or inside a long event. **Every client executes this identically or desyncs.** |

`ShouldSync` is `InInterface` minus an explicit opt-out flag (`dontSync`), which MP sets when it
wants to run interface code without capturing it as a command.

### 1.2 The rule a third-party patch author must follow

Stated as one sentence:

> **Interface code may read anything and must write nothing that the simulation will later read.
> Simulation code may read and write simulation state but must never read anything client-local.**

The precise operational form, from how MP itself enforces it:

1. **Never mutate game state while `Multiplayer.InInterface` is true.** Route the mutation through
   `[SyncMethod]` (or `MP.Watch*` for a field) so it becomes a command that every client replays
   inside `ExecutingCmds`.
2. **Never read a client-local value while `Multiplayer.Ticking || Multiplayer.ExecutingCmds`.**
   This is the rule the ownership layer must obey. `Find.CurrentMap`, `Find.Selector.selected`,
   camera position, `Prefs`, `MpSettings`, and any new "who owns this pawn" map are all in this
   category.
3. **Anything cached during the interface that the simulation later reads must be treated as
   poison.** MP spends most of `Source/Client/Patches/Determinism.cs` on exactly this — the file is
   ~700 lines of "don't let the UI dirty a cache the tick will read." Worked examples in there
   include `SituationalThoughtHandler` (three separate patches), `PawnCapacitiesHandler.GetLevel`
   and `StatWorker.GetValue` (both given a **synthetic third cache status**,
   `CachedInInterface = (CacheStatus)3`, so an interface-warmed cache is not trusted by the tick),
   `Pawn_AbilityTracker.AllAbilitiesForReading`, `WealthWatcher.ForceRecount`,
   `StoryWatcher_PopAdaptation.Notify_PawnEvent`, `PriorityWork.Clear`,
   `AutoSlaughterManager.Notify_ConfigChanged`, and `Zone.Cells` / `Plan.Cells` (shuffle
   determinism).
4. **Never consume RNG in the interface.** MP's whole desync detector is a fingerprint of the `Rand`
   stream (§4). Interface code that calls `Rand.Value` outside a `Rand.PushState()` block is the
   classic way to desync a mod.
5. **Never allocate a real unique ID in the interface** — MP already handles this for you, and the
   mechanism is worth knowing (§2.3).

### 1.3 Is it documented?

**No.** [docs, verified by fetching] The official Dev Wiki's *General Documentation*
(`hackmd.io/@rimworldmultiplayer/dev-general`) covers entry points, chat commands, the arbiter and
the server loop — it contains none of this. The *Multiplayer API* page (`dev-mapi`) documents the
public surface (`MP.enabled`, `MP.RegisterAll()`, `MP.IsInMultiplayer`, `MP.Watch*`,
`MP.WatchBegin/WatchEnd`, `[SyncMethod]`, `[SyncField]`, `[SyncWorker]`, `SyncWorker.Bind`,
`SyncWorker.isWriting`) and carries a note that it is incomplete pending migration from an older
wiki. It states no rule about interface side effects.

The public API *does* expose the gates, via `IAPI` (`Source/Client/MultiplayerAPIBridge.cs:15-33`)
[code]:

```csharp
public bool IsInMultiplayer                     => Client.Multiplayer.session != null;
public bool IsExecutingSyncCommand              => Client.Multiplayer.ExecutingCmds;
public bool IsExecutingSyncCommandIssuedBySelf  => TickPatch.currentExecutingCmdIssuedBySelf;
public bool InInterface                         => Client.Multiplayer.InInterface;
public bool CanUseDevMode                       => ...;
public Faction RealPlayerFaction                => Client.Multiplayer.RealPlayerFaction;
```

So `MP.InInterface` and `MP.IsExecutingSyncCommand` are available to a third-party mod through
`0MultiplayerAPI.dll` without reflecting into MP internals. **`Multiplayer.Ticking` is not
exposed** — but `!MP.InInterface` covers ticking, command execution, reloading and long events in
one test, which is the conservative direction. **That is the guard to write.**

**Assessment: the rule is inferable and stable, but unwritten. Archinity should write it down in
`CODING_STANDARDS.md` as a hard constraint, because it fails silently.**

---

## 2. Does MP already ship per-player client-local state?

**Yes — and more than expected. This is the strongest finding in this document.**

### 2.1 `MpSettings` is the sanctioned per-player channel

`Source/Client/Settings/MpSettings.cs` is a vanilla `ModSettings` — written to the player's own
config file, never synced, never scribed into the save. It already carries per-player *presentation*
state [code]:

```csharp
public bool showCursors = true;                        // draw other players' cursors
public bool transparentPlayerCursors = true;
public bool transparentChat = true;
public bool enablePings = true;
public KeyCode? sendPingButton = KeyCode.Mouse4;
public KeyCode? jumpToPingButton = KeyCode.Mouse3;
public List<ColorRGBClient> playerColors = new(DefaultPlayerColors);
public Rect chatRect;
public bool hideOtherPlayersInColonistBar = false;
public bool hideOtherPlayersQuests = false;
```

**`MpSettings` is the hook the ownership layer should hang on.** It is per-player, persistent,
outside the save, and MP already treats it as read-only-from-simulation.

### 2.2 MP has already built this exact layer

The last two fields are not aspirational — they drive shipped patches in
`Source/Client/Factions/MultifactionPatches.cs` [code]:

- **Filtered quest tab.** `MainTabWindow_Quests.ShouldListNow` **prefix** returns `false` for quests
  belonging to another player faction when `hideOtherPlayersQuests` is set (lines 42-58).
- **Quest ownership marker.** `MainTabWindow_Quests.DoRow` **prefix** draws a 4px colour stripe in
  the owning faction's colour and a tooltip naming the owner, with `". (you)"` appended for your own
  (lines 19-40).
- **In-tab toggle.** `MainTabWindow_Quests.DoRewardsPrefsButton` prefix adds a second button that
  flips `hideOtherPlayersQuests` live (lines 90-127).
- **Filtered colonist bar.** `ColonistBar.CheckRecacheEntries` **transpiler** replaces every
  `Find.Maps` call with `GetFilteredMaps()` (lines 129-158).

**This is precedent, template, and proof-of-safety in one.** MP filters the two exact surfaces the
Archinity layer wants, from a client-local settings bool, using ordinary Harmony prefixes and one
transpiler, and it ships to users.

**The gap, stated exactly.** Both toggles gate only on `Multiplayer.Client != null`, so they are
*active* in shared mode — but they have nothing to bite on. The quest filter keys off
`quest.TryGetPlayerFaction(out f) && f != Faction.OfPlayer`, and in shared mode there is exactly one
player faction, so the predicate is never true. The colonist-bar filter is **map-level**
(`Find.Maps.Where(map => map.mapPawns.FreeColonistsSpawned.Any() || map.Parent?.Faction == Faction.OfPlayer)`),
because multifaction gives each faction its own map — on one shared map it is a no-op.

**So: the mechanism exists and works; what shared mode lacks is a per-pawn ownership predicate.
That is precisely, and only, what Archinity would supply.** [inferred, from the verified code above]

For a per-pawn bar filter the patch site is different but adjacent: `ColonistBar.CheckRecacheEntries`
builds its entries from `map.mapPawns.FreeColonistsSpawned`, so the same transpiler technique
applies one level down, or a postfix can filter `ColonistBar.cachedEntries`.

### 2.3 The other client-local channels MP maintains

[code]

| Channel | Where | Notes |
|---|---|---|
| **Interface-only unique IDs** | `Patches/UniqueIds.cs` | `UniqueIdsPatch` returns **negative** IDs (`localIds--` from `-2`) whenever `Multiplayer.InInterface`. This is MP's built-in "this object is interface-only" marker. |
| **Interface-only letters/messages** | `ArchiveAddPatch` | `Archive.Add` refuses any `Message`/`Letter` with `ID < 0` — negative-ID letters never enter shared history. |
| **Unhistorical message IDs** | `NextMessageIdPatch` | Messages with `historical: false` get their own negative counter. |
| **Camera / selection** | Not synced | Restored across MP's own save-reload via `Find.Selector.selected` round-trip in `SaveLoad.SaveAndReload`, but never sent to peers. |
| **Player cursors and pings** | `MpSettings` + session | Explicit per-player presentation traffic. |
| **Dev mode / god mode** | `PlayerData` (`Comp/PlayerData.cs`) | Per-player, but **synced** (`ISynchronizable`) — because it changes what commands you may issue. |
| **Time votes** | `PlayerData.timeVotes` | Per-player, synced. |

**`PlaySettings` is NOT a client-local channel — it is synced.** `Source/Client/Syncing/Game/SyncFields.cs:120-137`
registers `useWorkPriorities`, `autoHomeArea`, `autoRebuild` and the eleven `defaultCareFor*` fields
as `Sync.Field(null, "Verse.Current/Game/playSettings", ...)`. Do not hang per-player state on
`PlaySettings`; use `MpSettings`.

**Negative IDs are the pattern to imitate.** If the ownership layer ever needs to create an object
that only one client sees, giving it a negative ID is the idiom MP already uses and already guards.

---

## 3. Letters and alerts in shared mode

**Settled: letters are synced simulation objects; alerts are pure client-side derivations. Filtering
alerts is free. Filtering letters is safe to *display*, but must never remove them.** [code]

### 3.1 Letters are synced state

`LetterStack` is scribed with the game and letters are created inside the tick, so both clients hold
the **same letter stack, produced identically by the shared simulation** — not generated
independently per client. Evidence:

- `ArchiveAddPatch` exists specifically to keep *interface-created* (negative-ID) letters **out** of
  the archive — which only makes sense because normal, positive-ID letters *are* shared state.
- `SortArchivablesById` (`Determinism.cs:191`) forces deterministic archive ordering — needed only
  for synced content.
- `DontRemoveGrowthMomentLetter` cancels `LetterStack.RemoveLetter` while a growth-moment dialog is
  drawing, with the comment: *"When reading sync data we check for the letter in the letter stack,
  and not archive - which fails to read the letter."* **Letters are sync-serialised by reference
  into the letter stack.**
- `DontDismissBabyLetters` forces `CanDismissWithRightClick` false for `ChoiceLetter_BabyBirth` and
  `ChoiceLetter_BabyToChild` with the comment: *"can be dismissed with right-click, which causes
  issues in MP if some of the players do it."*
- `DontAutoOpenLettersOnTimeout` disables `LetterStack.OpenAutomaticLetters` entirely in MP.
- `GrowthMomentSession` is a full persistent **Session** — a growth moment is a synced, blocking,
  shared decision.

**Consequence for the layer.** A filtered letter *view* is fine — draw a subset, tint by owner, add
an "only mine" toggle. **Do not call `LetterStack.RemoveLetter`, do not dismiss, do not archive**
from the filtering layer, because those are synced operations and MP has already had to patch
around players doing them asymmetrically. Filter at the draw site (`LetterStack.LetterStackUpdate`
/ the letter drawing loop), not at the data site. **[inferred from the verified patches above]**

Choice letters carrying decisions (growth moments, baby letters, ritual outcomes) must stay visible
to both players, or one player will silently never see a decision the other is blocked on.

### 3.2 Alerts are client-side

`Alert` instances live in `AlertsReadout`, are re-evaluated every frame from current game state, and
are never scribed or synced. MP's own alert work is pure display filtering
(`Source/Client/Patches/Alerts.cs`) [code]: three postfixes that narrow
`Alert_SlavesUnsuppressed.Targets`, `SlaveRebellionUtility.IsUnattendedByColonists` and
`Alert_AbandonedBaby.AbandonedBabies` by faction — each a `.Where(...)` on the result list, gated on
`MP.IsInMultiplayer`.

**These three patches are the exact idiom to copy for a per-pawn ownership filter.** Postfix the
alert's target getter, filter the list, done. No sync risk: an alert readout is downstream of
simulation and feeds nothing back.

One caveat: `SlaveRebellionUtility.IsUnattendedByColonists` is *also* called from simulation
(rebellion checks), and MP's postfix does **not** gate on `InInterface` — it changes the value for
everyone identically, which is safe only because it is deterministic and faction-based. **A postfix
that filtered by a client-local ownership map on that same method would desync immediately.** That
is the concrete shape of the trap in §4.

---

## 4. The desync hazard for a filtering layer, and what MP gives you

### 4.1 What the detector actually compares

`ClientSyncOpinion.CheckForDesync` (`Source/Client/Desyncs/ClientSyncOpinion.cs:33-60`) [code]
compares, in order:

1. floating-point round mode
2. the set of map IDs
3. **per-map `Rand` state sequences**
4. **world `Rand` state sequence**
5. **per-command `Rand` state sequence**
6. **stack-trace hashes** (only when both sides have them and neither is simulating)

So the fingerprint is **the RNG stream plus the shape of the code that consumed it**.

**This is the good news for the proposed layer.** A client-local value that only affects *drawing*
consumes no RNG and changes no simulation call path, so it is invisible to the detector *because it
is genuinely harmless*. The moment it leaks into simulation it almost certainly perturbs the RNG
stream or the trace hashes, and the detector fires.

### 4.2 Stack-trace hashing is the real guard

`DeferredStackTracing` (`Source/Client/Desyncs/DeferredStackTracing.cs`) postfixes
**`Rand.Value` and `Rand.Int`** and captures a native stack trace on each call, hashing it into the
opinion. `ShouldAddStackTraceForDesyncLog` gates on [code]:

```csharp
if (Multiplayer.Client == null) return false;
if (Multiplayer.settings.desyncTracingMode == DesyncTracingMode.None) return false;
if (!Multiplayer.game.gameComp.logDesyncTraces) return false;
if (Rand.stateStack.Count > 1) return false;      // inside a PushState block - ignored
if (Multiplayer.IsReplay) return false;
if (!Multiplayer.Ticking && !Multiplayer.ExecutingCmds) return false;   // interface RNG not traced
return ignoreTraces == 0;
```

Two things follow, both load-bearing:

- **Divergence is caught even when the random numbers coincide.** If your layer causes one client to
  take a different code path into an RNG call, the trace hash differs and `"Trace hashes don't
  match"` fires — a much finer net than comparing RNG state alone.
- **Traces are only collected during `Ticking || ExecutingCmds`.** Interface RNG use is deliberately
  untraced. This is a direct statement of the boundary: *MP does not care what the interface does,
  because the interface is not simulation.*

**Turn `logDesyncTraces` on for the whole development period.** Without it,
`desyncStackTraceHashes` is empty and check (6) is skipped entirely — you lose the fine net and keep
only the coarse RNG-state comparison.

### 4.3 The other guards you get for free

[code]

- **`Rand.PushState()` / `PopState()` bracketing.** Every tick context brackets RNG:
  `AsyncWorldTimeComp.PreContext`/`PostContext` and `AsyncTimeComp.PreContext`/`PostContext` push,
  set `Rand.StateCompressed = randState`, and pop. `Rand.stateStack.Count > 1` suppresses tracing
  inside nested pushes, which is how MP lets deliberate non-determinism (e.g. cosmetic effects) run
  without polluting the fingerprint. **If your layer ever must use RNG, wrap it in
  `Rand.PushState()`/`Rand.PopState()`.**
- **Negative unique IDs** (§2.3) — a structural guard that stops interface-created objects entering
  shared state at all.
- **`Determinism.cs` as a worked catalogue.** ~700 lines of every place vanilla lets UI dirty
  simulation. Read it before writing the layer; several of its patches (`StatWorker.GetValue`,
  `PawnCapacitiesHandler.GetLevel`, `SituationalThoughtHandler`) are exactly the caches a
  "my pawns" overlay will be tempted to warm.
- **`Multiplayer.dontSync`** — the explicit escape hatch for running interface code that must not be
  captured as a command.
- **`MP.IsExecutingSyncCommandIssuedBySelf`** — the sanctioned way to do "only the player who
  clicked sees this" inside an otherwise-synced method. `FactionCreator.CreateFaction` uses exactly
  this pattern for camera jumps and local visuals.
- **Dev-mode debug action "Trigger desync"** (`Debug/DebugActions.cs:217`) — verify the detector is
  live before trusting a clean run.
- **"Pause on desync"** server setting (`pauseOnDesync`, default `true`) — halts at the divergence
  rather than running past it.

**There is no dev-mode warning for "client-local value read during synced execution."** MP has no
taint tracking. The detector is behavioural, not static: it tells you *that* you diverged and
*where the RNG call was*, not *which variable was to blame*. **[verified by reading the full
`Desyncs/` directory; this is a specific negative about a specific mechanism, not a general "I found
nothing"]**

### 4.4 The discipline this implies for the layer

Make the ownership map **write-once from a synced source, read-only in the interface**:

1. Store ownership as a **synced** value (a `Dictionary<int,int>` pawn→playerId on a
   `GameComponent`, mutated only via `[SyncMethod]`). Then it is identical on both clients and
   cannot desync at all — only its *use* is client-local.
2. Gate every consumer with `if (!MP.InInterface) return;` — or, for filters, only ever apply the
   filter inside a draw/UI method.
3. **Never** postfix a method that is also called from simulation (the
   `IsUnattendedByColonists` trap, §3.2). Before patching anything, check its call sites for tick
   paths.
4. Assert loudly in dev builds: `if (MP.IsInMultiplayer && !MP.InInterface) Log.Error(...)` at the
   top of every ownership read. This is the taint check MP does not give you — build it yourself,
   because it is cheap and the failure is otherwise silent.

That design makes the layer's failures **visible**, which was the whole premise of the pivot.

---

## 5. Shared mode's own bug surface

### 5.1 What the code itself admits

The single best evidence of shared mode's failure classes is `Source/Client/Persistent/` — an entire
subsystem MP built to arbitrate **two players contending for one colony** [code]. Twenty-eight files
implementing a `Session` framework, with `SessionManager`, `ISessionWithCreationRestrictions`,
`ISessionWithTransferables`, `ITickingSession`, and `GetBlockingWindowOptions`.

The contended operations MP has had to wrap in synced, mutually-exclusive sessions:

| Session | File | Exclusion rule |
|---|---|---|
| Trading | `Trading.cs` (`MpTradeSession`) | `CanExistWith` returns false if `otherTrade.trader == trader` — **two players cannot trade with the same trader** |
| Caravan forming | `CaravanFormingSession.cs` | `CanExistWith(other) => other is not CaravanFormingSession` — **strictly one at a time, globally** |
| Caravan splitting | `CaravanSplittingSession.cs` | same pattern |
| Transporter loading | `TransporterLoadingSession.cs` | `ISessionWithCreationRestrictions` |
| Map portals | `MapPortalSession.cs` | `ISessionWithCreationRestrictions` |
| Rituals | `RitualSession.cs` | `SemiPersistentSession` |
| Psychic rituals | `PsychicRitualSession.cs` | `ISessionWithCreationRestrictions` |
| Growth moments | `GrowthMomentSession.cs` | ticking session tied to a letter |
| Gravship travel | `GravshipTravelSession.cs` | — |
| Pause locks | `PauseLockSession.cs` | — |

`SessionManager.GetOrAddSession` (lines 51-71) returns the *existing* conflicting session if it is
of the same type, and `default` (null) if the conflict is cross-type — i.e. **the second player's
attempt to open the dialog silently no-ops or joins the first player's**. `GetBlockingWindowOptions`
exists so the colonist bar can surface "this pawn is inside someone else's dialog."

**This is MP telling you, in code, what the shared-mode failure classes are:** modal, stateful,
multi-step UI over shared resources — trade, caravans, transporters, rituals — is where two players
collide. Everything MP could make idempotent it made a `[SyncMethod]`; everything it could not, it
made a Session.

Two further admissions in the same corpus [code]:

- `ServerPlayingState.HandleSetFaction` carries `// todo restrict handling` and performs **no
  permission check** — any player can reassign any player's faction.
- `MpTradeSession.CanExistWith` carries `// todo show error messages?` — the conflict is detected
  but the losing player is given **no feedback**. Expect "my click did nothing" as a routine
  experience.
- `SyncFieldUtil.FieldWatchPostfix` carries `// todo what happens on exceptions?` — an exception
  thrown mid-watch leaves the watched stack unbalanced.

### 5.2 The issue corpus

A sweep of `rwmt/Multiplayer` was run by a parallel agent; **every issue number below was then
re-verified by me directly against the tracker via `gh issue view` on 2026-08-28**, and the titles,
states and dates given here are that verification, not the sweep's prose. [verified]

| # | State | Title | Created / closed |
|---|---|---|---|
| 142 | closed | Allowed areas forced upon clients. | 2021-02-17 / 2021-07-26 |
| 168 | closed | `#142 Synced Designators Don't Interrupt Current Action` (the fix) | 2021-06-10 / 2021-07-29 |
| 301 | closed | "Research complete" popup blocks resync popup buttons | 2022-05-30 / 2023-11-20 |
| 365 | **open** | Potential soft-lock when launching transport pods | 2023-02-05 |
| 456 | closed | Desync when other player pushes the button "Create Caravan" | 2024-05-05 / 2024-07-18 |
| 506 | **open** | Opening a ritual dialog causes the wrong one to open (multiple ideologies) | 2024-09-18 |
| 512 | **open** | Caravan events don't pause the game | 2024-12-25 |
| 518 | **open** | Entering a new map causes desync | 2025-02-28 |
| 849 | closed | `FloatMenuOptionProvider_DraftedMove:PawnGotoAction` can cause desyncs | 2026-03-24 / 2026-07-27 |
| 854 | **open** | Resyncs run with wrong ProgramState | 2026-03-30 |
| 965 | closed | Desync when cancelling a gravship launch (**`CloseSessionAt` uses `Find.CurrentMap`**) | 2026-07-23 / 2026-08-03 |
| 967 | closed | Desync when spamming the gravship launch button (**RNG in `CanReachGravship` not isolated**) | 2026-07-24 / 2026-08-01 |
| 975 | **open** | Desync in `JobDriver_ConstructFinishFrame` (**`Rand.Value` divergence** with Mech_Constructoid) | 2026-07-29 |

**Two corrections to the brief's framing.** The brief described #965 *and* #975 as
`Find.CurrentMap`-leak issues. Only **#965** is — its title names `CloseSessionAt` using
`Find.CurrentMap`. **#975** is an `Rand.Value` RNG-divergence bug in `JobDriver_ConstructFinishFrame`,
a different class (§4.1 rather than §1.2), and it is still open. **#967** is the closer analogue to
#965 in spirit but is again an RNG bug: *RNG in `CanReachGravship` not isolated*, triggered by
**spamming a UI button** — i.e. interface interaction consuming un-bracketed RNG, which is exactly
failure mode 4 in §1.2.

**The designator/area class is verified, not inferred — and it is the most relevant one to this
proposal.** #142: *"Allowed areas forced upon clients. When the host is editing Area 1, clients are
unable to edit any other 'Allowed area' other than Area 1."* Its fix, #168, names two distinct
UI-state leaks verbatim: *"Last person to edit an 'allowed area' would force that area on all other
players"*, and *"Designating a thing to be reinstalled would cause all other players to lose their
currently active 'designators'. For example if you were in the process of marking out an area to be
mined at the same time a different player reinstalled a thing **on any map**, your mining tool would
disappear and revert to a simple cursor."*

That is a **client-local UI selection (the active designator, the selected area) leaking into synced
state, with cross-map blast radius**. It is precisely the failure shape a per-player ownership layer
risks reintroducing. Fixed in 2021 — but it establishes that this surface has historically been got
wrong by MP itself, and that the symptom is *visible and immediate* (your tool vanishes), not
silent. [verified: issue + PR text]

**Order stomping is confirmed as a desync vector, not merely an annoyance.** This corrects §5.3
class 2 below. #849's title names `FloatMenuOptionProvider_DraftedMove:PawnGotoAction`, and a
confirming comment (2026-07-11, while open) gives a clean repro: *"draft a group of pawns, give a
long move order, then while they're still walking, re-issue a move onto the cells they're currently
standing on… it stops only on the client that issued the order while the others keep walking it to
the old target. Desynced 3/3 for me."* Same commenter: *"I don't think it's specific to async time or
multifaction."* Closed 2026-07-27, so fixed in current 0.11.5 — but the class is real.

**Two-player gizmo races.** #456: *"Desync when other player pushes the button 'Create Caravan'…
it happened every time with no exceptions"*, three +1s, fixed in 0.10.4. Older analogue #60 (2020):
comms console *"window opens infinitely (the sound loops), which effectively locks the game."*

**Still-open items that bear on a 600-day campaign**: #518 (entering a new map causes desync, open
since 2025-02-28), #512 (caravan events don't pause), #506 (ritual dialog opens the wrong ritual
with multiple ideologies), #365 (transport-pod soft-lock), #854 (resyncs run with wrong
`ProgramState`, open since 2026-03-30 — this one degrades the *recovery* path, not just the
failure). #301 (a modal popup physically covering the resync button) is closed but illustrates the
same recovery-fragility.

**Steam is a dead source, definitively — not an empty search.** The mod description states: *"We
don't provide support from the workshop page, and is why we've removed the comments section."* The
discussions URL errors. Real reporting is GitHub plus a non-scrapeable Discord, so **absence of
Steam reports carries zero information** and community frequency data is inherently thin.

**Community frequency data** [community, low confidence — self-reported, 2-4 players, mostly
vanilla]: desync rates range from *"a couple of desyncs in 3 hours"* to *"every minute."* Several
reports claim **1.5 is more stable than 1.6**: *"Vanilla 1.5 is reliable, 1.6 not. Even with two or
three players."* Highest-risk actions by report: entering a new map, large raids, caravan forming,
ritual start, gravship launch. Treat the numbers as impressionistic; treat the *ranking* as useful.

**The community recovery ladder**: Resync / "Fix & Restart" → sync config files (delete the joiner's
`Config` folder, copy the host's) → keep maps ≤200×200 → periodically re-host → convert to SP and
re-host → reload save.

### 5.2a The official position on per-pawn ownership

**There is none, and MP says so.** [docs] The FAQ, answering how to stop players controlling each
other's pawns: *"RimWorld by design isn't made to micromanage one single pawns actions and the mod
doesn't provide such a functionality."* Its recommended workaround is social — bills bound to
specific colonists, zones restricting movement per player. Reddit co-op groups independently
converge on the same convention (*"section off the map into quarters that are our individual
'territories' using zoning"*). [community]

**This is the single strongest argument for the pivot.** The gap the proposed layer fills is one
the mod's own maintainers have explicitly declined to fill, and which players are currently papering
over with manual zoning conventions. Archinity would be building the missing ownership model, not
fighting an existing one. It also means **no upstream code will contest the layer** — but equally,
no upstream code will maintain it.

### 5.2b What the official Known Issues page says

[docs] With multifaction-specific entries excluded (those are covered in
`MULTIFACTION-REVERSIBILITY.md`), this residue applies to *all* MP modes:

- **Async time + quest sites**: smoke spewers and sun blockers behave incoherently under decoupled
  time; negative-condition camps only clear the condition for the quest recipient.
- **Mod mismatches**: local copies of Workshop mods cause def mismatches; HugsLib in particular can
  desync configs (hosts are advised to share their HugsLib folder); a corrupted `data` folder
  requires a Steam integrity verify.
- **Desyncs generally**: *"This is usually caused a bad connection between the host and player, but
  it can also be caused by using or having incompatible mods, unsynced config files, different mod
  files or game files."* Recovery is *"the host needs to save and the client needs to re-join."*
- **Pawn names may differ across clients** — explicitly flagged as visual-only and safe to ignore.

That last one is worth dwelling on: **MP already ships a known, accepted, purely-cosmetic
client-divergence.** It is precedent that a presentation layer diverging between clients is not
inherently a defect in MP's model.

### 5.3 The honest comparison

Shared mode is not bug-free — it is bug-*bounded*. Its failure classes are:

1. **Contention on modal shared dialogs** (trade, caravan, transporter, ritual) — manifests as
   silent no-ops and stolen dialogs, not corruption. Bounded by the Session framework, and MP knows
   about it.
2. **Order stomping on the same pawn** — two players issuing jobs to one pawn. I initially assessed
   this as deterministic and desync-free; **the corpus refutes that** (#849, §5.2): re-issuing a
   move order onto a walking pawn's current cells stopped the pawn only on the issuing client and
   desynced 3/3 in the reporter's testing. Fixed by 0.11.5, but the class is a genuine desync
   vector, not merely annoyance. This is exactly the class a "my pawns" ownership layer addresses —
   and it addresses it by **reducing the frequency of the input pattern**, not by removing the
   underlying fragility.
3. **Client-local UI state leaking into synced state** — the active designator, the selected allowed
   area (#142/#168); `Find.CurrentMap` inside a session teardown (#965). **This is the class the
   proposed layer must be most careful not to rejoin.** Symptoms are immediate and visible (your
   tool vanishes; a desync fires), which is the property the pivot is betting on.
4. **UI interaction consuming un-bracketed RNG** — #967 (spamming the gravship launch button;
   *"RNG in `CanReachGravship` not isolated"*). Directly failure mode 4 of §1.2.
5. **Mod/config mismatch desyncs** — orthogonal to mode; applies equally to multifaction.
6. **Async-time incoherence** — avoidable by leaving async time **off**.
7. **Fragile recovery** — #854 (resyncs run with wrong `ProgramState`, open) and #301 (modal popup
   covering the resync button, closed) both degrade the *escape hatch* rather than the simulation.
   Over 600 days this compounds: the cost of a desync is the recovery ritual, not the desync.

Against multifaction's failure classes (from the prior document): every third-party
`GameComponentTick`/`WorldComponentTick` running as the Spectator with empty research and no home
maps, silently, on both clients, invisible to the desync detector.

**The asymmetry the pivot is betting on is real and is confirmed by the code and the corpus.**
Shared mode's bugs are *arbitration* and *UI-leak* bugs — visible, bounded, recoverable, and
largely already fixed upstream. Multifaction's bugs are *context* bugs — silent, unbounded across
125 mods, and undetectable by MP's own machinery. A presentation layer's bugs are *drawing* bugs:
the most visible class of all.

**The synthesis worth keeping.** Every shared-mode failure in the corpus reduces to one of two
shapes:

- **a session that should have locked and didn't** — #512, #506, #365, #456; or
- **local UI state that should have stayed local and didn't** — #142/#168, #965, #849, #967.

The proposed ownership layer is squarely a member of the second family by construction. That is not
a reason not to build it — it is the reason to build it under the discipline in §4.4, where the
ownership map is *synced* state (so it cannot itself diverge) and only its *consumption* is
client-local.

One honest caveat on scope. **Nothing in the corpus reports two players editing the same bill stack,
work tab, or policy simultaneously.** That is a statement about the searches run, not about the
software — and bills and policies are shared object state with **no `Session` lock** (§5.1), while
#142 shows MP got exactly this wrong for the sibling panel (allowed areas). Treat that surface as
**under-reported, not safe**, and put it on the test checklist.

---

## 6. The "Join faction" tab — verdict

**It is multifaction with a shared faction. The Spectator machinery still runs. That path inherits
every multifaction bug.** [code] — settled decisively:

Every piece of the Spectator machinery gates on the **session-level flag**
`Multiplayer.GameComp.multifaction`, never on the local player's faction:

```csharp
// AsyncWorldTimeComp.PreContext — the world tick
if (Multiplayer.GameComp.multifaction)
{
    FactionExtensions.PushFaction(null, Multiplayer.WorldComp.spectatorFaction, force: true);
    foreach (var map in Find.Maps)
        map.MpComp().SetFaction(Multiplayer.WorldComp.spectatorFaction);
}
```

```csharp
// AsyncTimeComp.PreContext — every map tick
map.PushFaction(
    !Multiplayer.GameComp.multifaction || map.ParentFaction is { IsPlayer: true }
        ? map.ParentFaction
        : Multiplayer.WorldComp.spectatorFaction,
    force: true);
```

Joining a faction sends `ClientSetFactionPacket`, which only changes `player.FactionId` and the
local `Multiplayer.RealPlayerFaction` (`ClientPlayingState.HandleSetFaction`). It does not and
cannot clear `GameComp.multifaction`. Likewise `MapSetup.CreateAsyncTimeCompForMap`,
`SaveLoad.SaveAndReload`'s fixed-faction save, `MainTabWindow_QuestsDoRewardsPrefsButtonPatch`,
`ChatWindow`'s Factions button and `Replay`'s recorded flag all read the same session-level bool.

**Therefore:** "host with Multifaction ticked, then have the second player Join the host's faction"
is **not** an equivalent of shared mode. It runs the full Spectator context on every world tick and
every non-player-parented map tick, so every mod-compatibility risk in
`MULTIFACTION-REVERSIBILITY.md` §D1 applies unchanged.

**If the goal is one colony and two players, host with Multifaction OFF.** There is no benefit to
leaving it on and joining one faction, and there is the entire Spectator risk surface as a cost.

---

## 7. Two concurrent research projects

**A synced second research slot would be a normal `[SyncMethod]` job. MP does not special-case
`currentProj` in any way that obstructs it — but it does route research through the *window*, not
the manager, and that is the detail to get right.** [code]

MP's complete research-related sync surface (`Source/Client/Syncing/Game/SyncMethods.cs:59-70`):

```csharp
SyncMethod.Register(typeof(MainTabWindow_Research), nameof(MainTabWindow_Research.DoBeginResearch))
    .TransformTarget(Serializer.SimpleReader(() => new MainTabWindow_Research()));
SyncMethod.Register(typeof(ResearchManager), nameof(ResearchManager.StopProject));
// ResearchManager.SetCurrentProject changes the current project and is synced by
// MainTabWindow_Research.DoBeginResearch. It will still be called when selecting
// "Debug: Finish now". The issue with this is that when triggered by a player who
// can't execute debug-only methods it may change the current project to a research
// project which cannot be research due to prerequisites, allowing to research them.
SyncMethod.Register(typeof(ResearchManager), nameof(ResearchManager.SetCurrentProject)).SetDebugOnly();
SyncMethod.Register(typeof(ResearchManager), nameof(ResearchManager.FinishProject)).SetDebugOnly();
SyncMethod.Register(typeof(ResearchManager), nameof(ResearchManager.ApplyTechprint)).SetDebugOnly();
```

Plus one `FactionRepeater` entry on `ResearchManager.Notify_MonolithLevelChanged` (multifaction-only,
to give every faction Anomaly knowledge) and, in **multifaction only**, `MultiplayerWorldComp.SetFaction`
swapping `game.researchManager` wholesale.

Reading that carefully:

- **In shared mode MP does not patch `ResearchManager` at all** beyond registering sync methods on
  it. There is no transpiler, no prefix, no field interception on progress or `currentProj`.
  Research progress accrues inside the tick from `JobDriver_Research`, which is ordinary synced
  simulation.
- **The synced unit is `MainTabWindow_Research.DoBeginResearch`, not `SetCurrentProject`.** The
  quoted comment explains why: syncing the manager method directly would let a non-dev player
  bypass prerequisite checks. `SetCurrentProject` is registered `SetDebugOnly()` purely to catch the
  "Debug: Finish now" path.
- The `.TransformTarget(Serializer.SimpleReader(() => new MainTabWindow_Research()))` shim exists
  because the window is UI state that must not be serialised — it reconstructs a throwaway instance
  on the receiving side.

**Implication for a second research slot.** Two rules follow from the above:

1. **Sync at the UI entry point that carries the validation, not at the manager setter.** Whatever
   method your mod exposes as "begin second project" should be the `[SyncMethod]`, and it should
   perform its own prerequisite/availability check *inside* the synced method — mirroring MP's
   reason for choosing `DoBeginResearch`.
2. **Progress accrual needs no sync work at all**, provided the second slot's state lives in scribed
   simulation state (a `GameComponent` field or a `ResearchManager` extension) and is advanced from
   the tick. It is already inside the deterministic path.

**One caveat, and it is the one to watch:** if the second slot is stored in a `GameComponent`, note
§D1 of the prior document — under *multifaction* that component ticks as the Spectator. **In shared
mode this does not apply**, which is another point in shared mode's favour for this specific
feature. If the second slot is instead stored on `ResearchManager` itself, it travels with
`FactionWorldData` automatically and would work in either mode.

*(The vanilla-side mechanics of a second `currentProj` are another agent's question; the above is
strictly the MP-side answer.)*

---

## Bottom line

1. **The boundary rule** — interface reads anything and writes nothing the simulation reads;
   simulation reads nothing client-local. Testable via `MP.InInterface` /
   `MP.IsExecutingSyncCommand` from the public API. **Undocumented**; write it into
   `CODING_STANDARDS.md`.
2. **MP already ships the hook and the precedent.** `MpSettings` is the sanctioned per-player
   channel, and `hideOtherPlayersInColonistBar` / `hideOtherPlayersQuests` already implement a
   filtered colonist bar and quest tab via Harmony prefixes and one transpiler. Shared mode lacks
   only the per-pawn ownership predicate.
3. **Letters are synced; alerts are client-side.** Filter alerts freely (MP does, in
   `Patches/Alerts.cs`). Filter letters at the *draw* site only — never remove, dismiss or archive.
4. **The detector is an RNG-stream plus stack-trace-hash fingerprint.** Harmless UI divergence is
   invisible to it *because it is harmless*; leakage into simulation is caught fast. Enable
   `logDesyncTraces` or you lose the fine net. Build your own read-time assertion — MP has no taint
   tracking.
5. **Shared mode's bugs are arbitration bugs and UI-leak bugs** — contention on modal dialogs
   (#512, #506, #365, #456) and client-local UI state escaping into sync (#142/#168, #965, #849,
   #967). Visible, immediate, mostly fixed upstream — unlike multifaction's silent context bugs.
   **MP has explicitly declined to implement per-pawn ownership** ("the mod doesn't provide such a
   functionality"), so the proposed layer fills a real, uncontested gap that players currently
   paper over with manual zoning. Corrections to the brief: only #965 is a `Find.CurrentMap` leak
   (#975 is an open `Rand.Value` divergence), and order stomping **is** a desync vector (#849), not
   just an annoyance.
6. **"Join faction" is multifaction, not shared mode.** The Spectator still runs on every world
   tick. **Host with Multifaction OFF.**
7. **A second research slot is ordinary synced work.** MP does not special-case `currentProj`; sync
   at the validating UI entry point, and prefer storing the slot where it travels with the faction.

## Sources

- MP source at the installed commit: `rwmt/Multiplayer` @ `4a3be276bbf90cc597abfa5b299935ca8eeeb285`
- RimWorld 1.6 `Assembly-CSharp.dll`, decompiled with `ilspycmd`
- [RWMP Dev Wiki — General Documentation](https://hackmd.io/@rimworldmultiplayer/dev-general)
- [RWMP Dev Wiki — Multiplayer API](https://hackmd.io/@rimworldmultiplayer/dev-mapi)
- [RimWorld Multiplayer Known Issues](https://hackmd.io/@rimworldmultiplayer/BJBQwcPPlx)
- [RimWorld Multiplayer FAQ](https://hackmd.io/@rimworldmultiplayer/faq)
- `rwmt/Multiplayer` issue tracker, issues #60, #142, #168, #301, #365, #456, #506, #512, #518,
  #849, #854, #965, #967, #975 — each verified via `gh issue view --repo rwmt/Multiplayer` on
  2026-08-28 for number, title, state and dates
- Companion document: `docs/data/MULTIFACTION-REVERSIBILITY.md`
