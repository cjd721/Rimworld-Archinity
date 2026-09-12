# Traps: multiplayer and determinism

Divergence that survives identical mod lists. The model these rest on is
`docs/engine/determinism.md`.

Part of the trap register. **The index at `docs/TRAPS.md` is the file you read
before a diff**; this one carries the full entries for this group. Every entry here
fails with no error message. Cite by ID.

## Multiplayer and determinism

### T-18 — Mod settings are part of the sync surface

Both players need identical mods, identical load order (`config/ModsConfig.xml`)
**and** identical mod settings (`config/ModSettings/`). The third is the one people
miss — TechBlock, Ignorance Is Bliss and Medieval Overhaul are all settings-driven,
and settings reach runtime as well as def-load. A diff that changes settings must
re-snapshot them.

Compare **parsed values, not bytes**: `Scribe_Values.Look` omits values equal to
their default, so a fresh config and an explicitly-defaulted one are byte-different
with identical meaning.

*`docs/engine/determinism.md`; T-19 and T-20 are the worked cases. MP 0.11.5.*

### T-19 — Medieval Overhaul forces a setting from a draw method

The force lives inside the **Map-Gen tab's draw method** — not `ExposeData`, not a
constructor:

```csharp
if (!metalChain) { vanillaMine = true; }
```

Uncheck `metalChain` on the Production tab, close without visiting Map Gen, and the
force never runs. **Two players clicking identical settings produce different
files.** Copy the settings file between machines; never re-click it.

*`docs/engine/mods/medieval-overhaul.md`. MO 1.6.*

### T-20 — Medieval Overhaul's schematic cache is a live desync bug

Both schematic patches carry `private static bool? cachedSchematicCheck` and
`cacheStaleAfterTicks` with a 250-tick window and **no key** — not the project, not
the bench, not the schematic —
so whichever call lands first decides the answer for every gated project on every
bench. `CanBeResearchedAt` is called from `WorkGiver_Researcher` (simulation)
**and** the research tab UI (client-local), so the player with the tab open poisons
the shared cache on a schedule the other client does not share, and one client's
`WorkGiver_Researcher` refuses jobs the other accepts.

Separately, both patches' `Prepare()` returns `!settings.biotechSchematic`, and
`Prepare()` decides whether the patch is applied at all — so a settings mismatch
changes which code exists. Mitigation needs no assembly: strip the
`RequiredSchematic` extension from the 14 gated projects and the postfix returns
immediately.

*`docs/engine/mods/medieval-overhaul.md`. MO 1.6.*

### T-21 — Filter at draw time, never at list-membership time

`Letter.CanCullArchivedNow` culls the Archive by **stack membership**, so filtering
at receive makes two clients cull different sets and synced `ChoiceLetter` commands
then deserialize to null — Multiplayer ships this bug with a TODO admitting it. The
same shape is worse upstream: patching `MapPawns.FreeColonists`, `PawnsFinder` or
`Pawn.IsColonist` diverges **~15 ticked readers**, equally silently.

Any per-player presentational layer filters at **draw** time only.
`ColonistBar.cachedEntries` is never serialised and nothing in the tick path reads
it, which is why the colonist bar is tractable and the pawn lists are not.

*`docs/engine/determinism.md` § *Presentational separation*. MP 0.11.5.*

### T-22 — 77 workshop mods have a second copy on disk

**77 workshop mods carry a full second copy** under
`steamapps/common/RimWorld/Mods/`, declaring the same `packageId` — measured today
as the id-overlap between the two roots: 145 folders under
`workshop/content/294100`, 83 under `Mods/`, of which 77 collide and 6 are ours
(the five `Archinity.*` mods plus Steam's placeholder file).

These are real copies, not junctions — VEF (`2023507013`) is 13 MB in both. Which
one loads is not something the mod list tells you, and byte-identity between
machines is not established by matching workshop IDs.

**All 77 have now been diffed, and six of them differ.** The earlier reading —
five sampled, all byte-identical — did not generalise. Comparing every `.dll` and
`.xml` under both roots:

| Diverged `packageId` | |
|---|---|
| `oskarpotocki.vanillafactionsexpanded.core` | `VEF.dll` md5 `04a732e9…` local vs `c8b454bc…` workshop |
| `andromeda.milkyway` · `ferny.betterarchitect` · `mrk.architectmenuoptimizer` · `sbz.neatstoragefridge` · `vanillaexpanded.vexploratione` | |

**VEF is the worst possible member of that list** — 57 of the 150 mods in the bin
declare it under `modDependencies`, and quest chaining, KCSG site generation and the
goodwill queue all live in the assembly that differs.

**The two copies are not a pin and must not be read as one.** Nothing has been
pinned; `Mods/` holds an incidental second copy of 77 workshop mods, and the
instruction below still stands unmet. Workshop auto-updates and `Mods/` does not,
so the divergence set grows on its own every time Steam updates something — which
is why a duplicate that was byte-identical when sampled is no evidence about it
today.

**`corpus.py --check` cannot see any of this and reports the corpus clean.** It
keys by `packageId`, first base wins, and its base order is `(DATA, WORKSHOP,
LOCAL)` — so it records one row per mod, attributes VEF's origin as **workshop**,
and never compares the two copies. Its `scan()` docstring asserts *"First base
wins, as RimWorld does"*, and **that claim is unverified**. If it is wrong, every
finding this project has cited "against the version on disk" was read from the copy
the game does not load. Only a launch-log check separates the two readings —
[which copy of 77 duplicated mods the game actually
loads](https://github.com/cjd721/Rimworld-Archinity/issues/99) owns it.

**Resolve this before the mod set is pinned**; the vendoring decision in
[#3](https://github.com/cjd721/Rimworld-Archinity/issues/3) has to say which root
wins, and a pin taken over an unresolved duplicate pins the wrong copy half the
time. The same hazard applies inside a mod: TechBlock ships both a `1.6/` and a
`1.0/` assembly, and decompiling the wrong one yields different code and a wrong
conclusion. §14's open `RangeFinder.dll` item is the same shape again.

*Disk survey 2026-09; overlap re-counted against both roots 2026-09-08; all 77
diffed and the six divergences found 2026-09-09, against the build on disk that
day.*

### T-33 — KCSG generates settlements from an unseeded `System.Random`

`KCSG.SettlementGenUtils.Sampling.Sample` opens with `random = new Random();` — a
parameterless `System.Random`, read by `random.Next(int)` and `random.NextDouble()`.
**`Verse.Rand` never touches it**, so vanilla's map-generation seeding
(`docs/engine/determinism.md` § *Map generation is seeded by vanilla*) does not reach
it and `Rand.PushState` cannot. Every `SettlementLayoutDef` takes this path — every
faction stronghold, every KCSG-authored site.

Two clients walking into the same site generate **different maps**, and nothing
reports it: map generation is outside MP's desync checksum by construction. The
failure surfaces minutes later as a desync whose stack trace names a pawn.

**The fix is not ours to write.** Multiplayer Compatibility
(`rwmt.multiplayercompatibility`) carries it: `VanillaExpandedFramework.PatchKCSG`
transpiles `newobj System.Random::.ctor()` into a `RandRedirector` routing into
`Verse.Rand`. A transpiler is the only shape that works — `Sampling.random` is a
`public static` field that `Sample` reassigns as its **first statement**, so a prefix
that seeds the field is overwritten before the first draw. Do not author a second
transpiler on the same method.

The transpiler logs `"No System RNG was patched for method: …"` if it fails to bind,
so wherever it is in the load order this trap fails **loudly** — which is the one
thing it otherwise does not do. **That reassurance is specific to `System.Random` and
does not generalise**: `FixRNG` rewrites `newobj` on *both* of that type's constructors
(`SystemRandConstructor`, `SystemRandSeededConstructor`), so a method either has every
construction redirected or trips the warning, whereas the Unity-side sibling
`FixUnityRNG` enumerates a hand-written subset of members under the same
`!anythingPatched` guard and half-fixes a method in silence — **T-51**.

Two carve-outs worth keeping [V]: the `structureLayoutDefs` and `tiledStructures`
branches of `GenStep_CustomStructureGen.Generate` **never reach `Sampling`**, so sites
we author that way are safe even with the compat layer off. That is a design lever for
[#57](https://github.com/cjd721/Rimworld-Archinity/issues/57) and
[#66](https://github.com/cjd721/Rimworld-Archinity/issues/66) — belt-and-braces, not a
substitute, since faction strongholds take the `SettlementLayoutDef` path regardless.

**MP Compat's protection is a hardcoded per-mod allowlist, not a general mechanism.**
It covers 21 of the mods on disk by name; anything else in the shipping set, and
anything we write ourselves, gets no coverage. That is a standing condition on
sourcing, not a one-off.

*[#88](https://github.com/cjd721/Rimworld-Archinity/issues/88). `KCSG.dll`,
`Multiplayer.dll`, `Multiplayer_Compat.dll` 1.6, decompiled at the MOD-SNAPSHOT pin.
Corpus-wide sweep of 1,057 assemblies: this is the only unseeded `System.Random` on a
map-generation path. The `FixRNG` / `FixUnityRNG` contrast re-read from
`Multiplayer.Compat.PatchingUtilities` (`Multiplayer_Compat.dll` 1.6) 2026-09-12.*

### T-39 — `QuestScriptDef.CanRun` draws on the shared `Rand` stream and memoises per tick

The name reads as a pure predicate. It is not one. `CanRun(Slate, IIncidentTarget)`
answers by **running the quest**: its body is

```csharp
lastCanRunResult = target != null && CanQuestOccurOnTile(target.Tile)
                   && root.TestRun(slate.DeepCopy());
```

The copied slate keeps the walk from writing anything back, but it does not keep it off
`Verse.Rand`. Any script whose tree reaches `QuestNode_GetSiteTile` reaches
`TileFinder.TryFindNewSiteTile`, whose success path ends in

```csharp
tile = list.RandomElement();
```

— a draw on the **shared** stream, plus a second `RandomElement()` on the layer fallback
and whatever `TryFindRandomPlayerTile` spends before it. The number of draws depends on
how the query lands, so it is not even a fixed cost.

**The memoisation makes this worse, not safer.** Three fields carry the cache —

```csharp
[Unsaved(false)] private int  lastCheckCanRunTick;
[Unsaved(false)] private int  lastCheckCanRunPoints;
[Unsaved(false)] private bool lastCanRunResult;
```

— keyed on `Find.TickManager.TicksGame` **and** the slate's `points`. The first caller in
a tick at a given points value pays the draws; every later caller in that tick pays none.
So the stream position after a tick is a function of *who called first*, not of what the
simulation did.

**Render code renders on one client only, and on selection.** An inspect string, a gizmo
label or tooltip, a custom `ITab`, a left-open dev window — all of these run on the
machine whose player is looking, at the moment they look. Call `CanRun` from one and that
client pulls the shared stream while the other does not. **The canonical shape of this bug
is an inspect string previewing eligibility** — a readout answering *"is any beat eligible
right now?"* on the apparatus's inspect pane is exactly the tempting, wrong thing to
build. The desync surfaces later, in a trace naming whatever drew next.

**The safe pattern: compute such a readout from declared def data and condition workers,
never from `CanRun`.** Read the fields the def already states — the band, the research
gates, the beat's own declared conditions — and evaluate them with workers you wrote,
which draw nothing. A preview owes the player an answer, not the engine's answer.

Vanilla's own `QuestPart_SubquestGenerator_ArchonexusVictory.GetNextSubquestDef` calls
`CanRun` and is fine, which is the distinction that matters: it runs from **synced
quest-part code** on the ticked path, where both clients execute it in the same order and
spend the same draws. Calling `CanRun` is not the error. Calling it from a path only one
client walks is.

*[#57](https://github.com/cjd721/Rimworld-Archinity/issues/57).
`RimWorld.QuestScriptDef.CanRun`, `RimWorld.Planet.TileFinder.TryFindNewSiteTile` and
`RimWorld.QuestPart_SubquestGenerator_ArchonexusVictory.GetNextSubquestDef`, all read from
`Assembly-CSharp.dll` 1.6.4871 rev590 with `ilspycmd` 8.2.0, 2026-09-12.
`docs/engine/determinism.md` § *Presentational separation between the two players* is the
general rule this is a case of.*

### T-51 — MP Compat's `FixUnityRNG` half-fixes in silence, unlike its `System.Random` sibling

`Multiplayer.Compat.PatchingUtilities.FixUnityRNG` — the transpiler behind
`PatchUnityRand(...)` — walks the instruction stream and, on an `OpCodes.Call` whose
operand is a `MethodInfo`, rewrites **exactly six targets**:
`UnityEngine.Random.Range(int,int)` and `Range(float,float)`, the obsolete `RandomRange`
spelling of each, `Random.value`, and `Random.insideUnitCircle`. That is the whole list;
the fields backing it are the whole list too. Every other member of the type —
`insideUnitSphere`, `onUnitSphere`, `rotation`, `ColorHSV`, `state`, `InitState` — is
passed through untouched.

Then the warning:

```csharp
if (!anythingPatched)
    Log.Warning("No Unity RNG was patched for method: " + …);
```

It fires only when the transpiler matched **nothing at all**. A method holding one
`Random.Range` and one `Random.insideUnitSphere` matches something, so `anythingPatched`
is true, so the log stays quiet — and the second draw still reads a process-global stream
that was never equal between two clients to begin with. The mod is on the allowlist, the
patch applied, and the method is **half-fixed with no signal**.

**Its `System.Random` sibling is a different shape.** `FixRNG` carries the identical
`!anythingPatched` guard, but what it rewrites is `newobj` on *both* of that type's
constructors — `SystemRandConstructor` and `SystemRandSeededConstructor` — which is every
way to construct one. Per method it is therefore all-or-nothing: either the draws are
redirected or the warning means what it says. **That is why T-33 closes by saying its trap
fails "loudly", and that claim does not carry over to the Unity side.** A static class has
no constructor to hijack, so the Unity facility has to enumerate members by hand, and it
silently passes over the ones it was not told about.

**This entry needs no live instance to justify it.** It is a standing condition on any
assembly we ship and on anything the sourcing ledger
([#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)) adds later — neither gets
allowlist coverage by default, because as T-33 records the coverage is a hardcoded per-mod
list. The corpus sweep behind that judgement, and the reason `UnityEngine.Random` is worse
than `System.Random` to start with, are in `docs/engine/determinism.md`
§ *`UnityEngine.Random` is a third stream*; not restated here.

Two consequences for us. Do not read "MP Compat patches that mod" as "that mod's Unity
draws are handled" — check the member. And do not reach for `UnityEngine.Random` in
Archinity code at all: there is no seeded escape hatch on that stream, so `Verse.Rand` is
the only correct choice.

*[#94](https://github.com/cjd721/Rimworld-Archinity/issues/94).
`Multiplayer.Compat.PatchingUtilities` read from `Multiplayer_Compat.dll` 1.6 with
`ilspycmd` 8.2.0, 2026-09-12; both on-disk copies of `1629973374` are byte-identical
(md5 `471a7221…`), so T-22 does not bite here. `Verse.Rand` and the corpus result:
`docs/engine/determinism.md`.*

### T-52 — `Dialog_Rename<T>.OnRenamed` runs client-locally, ahead of the synced setter

`Verse.Dialog_Rename<T>` accepts inside `DoWindowContents`, and the two lines that matter
are adjacent:

```csharp
if (renaming != null) { renaming.RenamableLabel = curName; }
OnRenamed(curName);
```

**Only one of them is synced.** `Multiplayer.Client.SyncMethods` registers the declared
`RenamableLabel` property setter of every `IRenameable` implementor its serializer can
handle — enumerated from `typeof(IRenameable).AllImplementing()` after mods load — so the
first line does not write anything on the clicking machine. The sync prefix intercepts it,
dispatches a command and returns; the write lands on both clients later, when the command
replays.

`OnRenamed(curName)` on the very next line is intercepted by nothing. It runs
**immediately, on the clicking client, and nowhere else** — and it runs *before* the setter's
write has landed even locally, so it can also read the old value. There is no error, no
warning, and on a single-player playtest no symptom at all.

The default body is empty:

```csharp
protected virtual void OnRenamed(string name) { }
```

which is exactly why this is easy to walk into. It reads as the hook the base class provides
for your side-effects, and vanilla gives you no hint that it is the wrong side of the sync
boundary.

**Multiplayer had to work around this in vanilla's own code**, which is the corroborating
evidence that it bites in practice — right after the `IRenameable` loop, in the same
initialiser:

```csharp
SyncMethod.Register(typeof(Dialog_RenameBuildingStorage_CreateNew), "OnRenamed")
    .TransformTarget<Dialog_RenameBuildingStorage_CreateNew, IStorageGroupMember>(…);
```

A `Window` is not serialisable, so they needed a target transformer that sends the dialog's
`building` and reconstructs the dialog on the far side. Nobody writes that unless the
straightforward thing was observably broken.

**The rule for us: leave `OnRenamed` empty.** The synced setter is the entire write, so
every effect of a rename — recording the string, setting a flag, mirroring to a display
field — goes inside `RenamableLabel`'s setter, where it is one command applied identically
on both clients. If an effect genuinely cannot live there, it needs its own registered sync
method, and then it needs the transformer too.

*[#50](https://github.com/cjd721/Rimworld-Archinity/issues/50).
`Verse.Dialog_Rename<T>.DoWindowContents` and `.OnRenamed` from `Assembly-CSharp.dll`
1.6.4871 rev590; `Multiplayer.Client.SyncMethods` from `Multiplayer.dll` 1.6
(`2606448745/1.6/AssembliesCustom`, both on-disk copies byte-identical, md5 `2032ec31…`).
`ilspycmd` 8.2.0, 2026-09-12.*

### T-53 — `Window.forcePause` does not pause a Multiplayer session

Vanilla honours `forcePause` through a chain that Multiplayer removes.
`Verse.TickManager.ForcePaused` reads `Find.WindowStack.WindowsForcePause`,
`TickManager.Paused` consults
`ForcePaused`, and `TickManager.TickManagerUpdate` returns early when paused. In a session
**none of that executes**: `Multiplayer.Client.TickPatch` is
`[HarmonyPatch(typeof(TickManager), "TickManagerUpdate")]` and its `Prefix()` returns `true`
— *run the original* — only when `Multiplayer.Client == null`. With a session live it
returns `false` and MP drives ticking from its own tickables and the server's time vote. The
whole `Paused` → `ForcePaused` → `WindowsForcePause` path is skipped.

Swept the whole of `Multiplayer.dll`: `WindowsForcePause` is read in **exactly one place**,
`Multiplayer.Client.AsyncTime.TimeControlPatch.DoTimeControlsHotkeys` — and even there it
only suppresses the four *speed-change* hotkeys, with the pause hotkey handled above the
guard and still firing. `TickPatch` does not mention it at all.

So a modal window stops nothing. One player typing into a dialog does not stop the other
player's colony, and does not stop their own. `WindowStack` is per-client UI state and was
never going to be shared; `forcePause` is a single-player affordance that keeps compiling.

`Dialog_Rename` sets `forcePause = true` in its constructor, and there it is **harmless** —
a rename is instantaneous and nothing hinges on the clock. The trap is anywhere a design
leans on a modal window stopping the world: a timed choice, a "the colony waits while you
decide" beat, any dialog whose correctness assumes nothing ticks while it is open. Build
those to hold their own state and be driven from the synced tick, and treat `forcePause` as
a courtesy to the local player rather than a guarantee.

*[#50](https://github.com/cjd721/Rimworld-Archinity/issues/50).
`Verse.TickManager.ForcePaused` and `Verse.Dialog_Rename<T>`'s constructor from
`Assembly-CSharp.dll` 1.6.4871 rev590; `Multiplayer.Client.TickPatch` and the
single-hit full-assembly sweep for `WindowsForcePause` against `Multiplayer.dll` 1.6
(`2606448745/1.6/AssembliesCustom`, md5 `2032ec31…`). `ilspycmd` 8.2.0, 2026-09-12.*

---
