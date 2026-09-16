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

**The same memo is blind to everything in the slate except `points` — including who asks.**
This one is single-player and needs no second client. `Pawn_RoyaltyTracker.PossibleDecreeQuests`
builds a slate with `asker` set to the titled pawn and calls `CanRun` on every decree script
sharing a tag. The memo key has no `asker`. So on one tick, every titled colonist on a map
at the same threat points gets the **first** colonist's answer for each script. A decree
gate that reads the asker in a `TestRunInt` — their title, their traits, their faction
standing — silently answers for the wrong noble. **Route decrees per ladder with
`RoyalTitleDef.decreeTags` / `QuestScriptDef.decreeTags`, which are read before `CanRun`, and keep
`TestRun` gates to state every asker shares.**

*[#57](https://github.com/cjd721/Rimworld-Archinity/issues/57); the per-asker case
[#137](https://github.com/cjd721/Rimworld-Archinity/issues/137).
`RimWorld.QuestScriptDef.CanRun`, `RimWorld.Planet.TileFinder.TryFindNewSiteTile` and
`RimWorld.QuestPart_SubquestGenerator_ArchonexusVictory.GetNextSubquestDef`, all read from
`Assembly-CSharp.dll` 1.6.4871 rev590 with `ilspycmd` 8.2.0, 2026-09-12;
`RimWorld.Pawn_RoyaltyTracker.PossibleDecreeQuests` / `IssueDecree` and
`Verse.AI.MentalBreakWorker_WildDecree.BreakCanOccur`, same build and tool, 2026-09-16.
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

### T-61 — VEF's study-designation gizmo writes scribed state and no compat patch covers it

`VEF.Buildings.StudiableBuilding.GetGizmos` builds a `Command_Action` whose `action` calls
`MapComponent_InteractableBuildingsInMap.AddStudiablesToMap(this)`, and that `HashSet<Thing>`
is scribed — `Scribe_Collections.Look(ref studiables_InMap, "studiables_InMap",
LookMode.Reference)`. **Nothing syncs it.** One client designates a mural; the other client's
colonists never see it, and the divergence is written into the save rather than living in a
cache.

**The negative is byte-exact, not a metadata guess.** Every ASCII and null-interleaved UTF-16
literal was extracted from both 1.6 compat assemblies (`Multiplayer_Compat.dll` and
`Multiplayer_Compat_Referenced.dll`, the two on-disk copies md5-identical, so T-22 does not
bite): **71 other `VEF.` strings are present**, and `StudiableBuilding`, `LootableBuilding`,
`AddStudiablesToMap` and `MapComponent_InteractableBuildingsInMap` are **absent in both
encodings**.

**The right-click path is already safe, which is what makes this easy to miss.**
`GetFloatMenuOptions` ends in `selPawn.jobs.TryTakeOrderedJob(…)`, and
`Multiplayer.Client.SyncMethods` registers `Pawn_JobTracker.TryTakeOrderedJob` generically.
*Ordering* a pawn to read a mural is synced; *designating* one is not. Play-testing the
feature the obvious way exercises only the safe half.

**Registration is per concrete type, by lambda ordinal, so a subclass inherits nothing** —
the same fact `docs/specs/CHARTING.md` already records for `CompLongRangeMineralScanner`.
Anything of ours deriving from `StudiableBuilding` must override `GetGizmos` and route the
designation through one method we register ourselves against `Multiplayer.API`. MP Compat
does exactly that for a third-party studiable —
`MpCompat.RegisterLambdaMethod("VanillaQuestsExpandedTheGenerator.Building_Genetron_Studiable",
"GetGizmos", 0)` — and notably **without** `.SetDebugOnly()`, so MP treats a study
designation as a real sync surface.

*[#80](https://github.com/cjd721/Rimworld-Archinity/issues/80), `docs/specs/CHARTING.md`.
`VEF.dll` (`2023507013/1.6/Assemblies/`); `Multiplayer.Client.SyncMethods` from
`Multiplayer.dll` 1.6; literal extraction over `Multiplayer_Compat.dll` and
`Multiplayer_Compat_Referenced.dll` 1.6 (`1629973374/`). 1.6.4871.*

### T-66 — A storyteller comp's list index is a `Rand` seed salt

`RimWorld.IncidentCycleUtility.IncidentCountThisInterval(target, randSeedSalt, …)` seeds from
`Gen.HashCombineInt(Find.World.info.persistentRandomValue, target.ConstantRandSeed,
randSeedSalt, i)`, and **every scheduled comp passes
`Find.Storyteller.storytellerComps.IndexOf(this)` as `randSeedSalt`**. The salt is therefore
a position in a list, not an identity.

Two ways that position moves without anybody intending it. Adding a comp to a
`StorytellerDef` by `PatchOperationAdd` re-indexes every comp after it. And the runtime list
is filtered by `StorytellerCompProperties.Enabled`, so **merely changing the active mod set
moves the same indices** — a comp gated on a DLC or a mod that is switched off shifts
everything below it.

The effect is that every later comp's **pre-computed hit schedule is silently re-rolled**:
cadence changes nobody authored, arriving mid-campaign, with nothing reported and nothing to
compare against. This is a determinism trap before it is a Multiplayer one — the same save,
reopened with a different mod set, generates a different schedule — but it is also T-18's
shape at one remove, since two clients with different mod lists hold different index
assignments.

Consequence for `docs/specs/PRESSURE.md`: **ship our own `StorytellerDef`s rather than
patching comps into the vanilla three**. A def of ours owns its own comp order and nothing
inserts ahead of it. Worth keeping alongside this: `IncidentCycleUtility`'s schedule draws
nothing from the shared `Rand` stream, which makes it the safest scheduler available under
Multiplayer — the hazard is the salt, not the stream.

*[#60](https://github.com/cjd721/Rimworld-Archinity/issues/60), `docs/specs/PRESSURE.md`.
`RimWorld.IncidentCycleUtility.IncidentCountThisInterval`,
`RimWorld.StorytellerCompProperties.Enabled`, `RimWorld.Storyteller.storytellerComps`.
1.6.4871.*

### T-67 — Hacking Expansion's settings change the def database, not just behaviour

**Distinct from T-18, and worse than it.** T-18 is a setting read at runtime. This is a
setting that **rewrites `ThingDef.comps` and `PawnKindDef.race.comps`** at
`Verse.DefOfHelper.RebindAllDefOfs`: `USH_HE.Patch_DefOfHelper_RebindAllDefOfs` is a postfix
that appends `CompProperties_TurretHackable` to every qualifying turret `ThingDef` only when
`HE_Mod.Settings.EnableTurretsHacking`, and `CompProperties_MechanoidHackable` to every
qualifying mechanoid/drone race only when `HE_Mod.Settings.EnableMechHacking`.

Two clients with different values therefore hold **different comp lists on the same defs** —
different derived `defence` values, different `ExposeData` shapes — and desync with no error
message anywhere. Both settings must be pinned identical before a session, and a settings
re-snapshot is mandatory after either is touched.

**Pinning the two settings is not a complete mitigation.** The same postfix's
`ShouldBeDataSource` branch appends `CompProperties_DataSourceProtected` to **every**
`CompHackable` ThingDef, **ungated by any setting**. The def database this mod produces is
never the one on disk, whatever the settings say — which is also why a `PatchOperation`
written against `CompProperties_TurretHackable` or `CompProperties_MechanoidHackable` matches
**zero** nodes (T-03), and why `tools/defdb.py`, `patch_check.py` and `xpath.py` cannot see
the injected comps at all. Def-side work targets `CompHackable`, or runs after the injector.

*[#58](https://github.com/cjd721/Rimworld-Archinity/issues/58), `docs/specs/HACKING.md`.
`USH_HE.Patch_DefOfHelper_RebindAllDefOfs` from `HackingExpansion.dll`
(`3573344880/1.6/Assemblies/`); `Verse.DefOfHelper.RebindAllDefOfs`. T-18, T-03.
1.6.4871.*

### T-74 — Vehicle Framework pathfinds on the thread pool, and nothing anyone has patched reaches it

`SmashTools.TaskManager.Run(Action, CancellationToken)` is a bare `Task.Run` wrapped in a
fire-and-forget awaiter. Two of its three call sites are simulation, both reached from the
synced tick:

```
VehiclePawn.BaseTickOptimized → VehiclePathFollower.PatherTick → TryEnterNextPathCell
  → RequestNewPath → TaskManager.Run(AsyncPathFindAction.Invoke)
WorldVehiclePathGrid.WorldComponentTick → RecalculateAllPathCostsAsync → TaskManager.Run(…)
```

**Neither consults `VehiclePathingSystem.ThreadAvailable`**, which is the only thing VF's own
`Vehicles.SectionDebug.debugUseMultithreading` (T-75) and Multiplayer Compat's `NoThreadInMp`
can reach — and MP Compat's `ReplaceThreadAvailable` transpiler is applied to **3 of the 8
`ThreadAvailable` readers** in the assembly, all three of them in `PathingHelper`. Reading
only those eight call sites makes the mod look fixed. **The compat layer patched what it said
it would patch**, and logged nothing, because nothing failed.

What the escaped task does. `VehiclePathFinder.FindPath` walks
`VehicleRegionCostCalculator.RegionMedianPathCost`, which runs `Rand.PushState()`,
`Rand.Seed = …`, eleven `region.RandomCell` draws and `Rand.PopState()` **on `Verse.Rand`'s
unlocked process-global state, from a pool thread**. The seed itself is derived from region
geometry, so this is not an RNG-value bug: it is a **race on the shared stream**, and the
damage lands on whatever the simulation thread drew next. MP checksums `Rand` state as
simulation state, so this trips the desync detector while naming something else entirely.

A second divergence needs no RNG at all. `TryEnterNextPathCell` opens with
`if (RequestStatus == PathRequestStatus.Calculating) return;`, so **the tick a vehicle starts
moving is a function of thread scheduling** — two clients' vehicles sit in different cells.
And the world-map half is the mobility ladder's own cost function:
`PerceivedMovementDifficultyAt` is an unlocked `pathGrids[vehicleDef.DefIndex][tile]` array
read against a grid a pool thread rewrites once per in-game day.

**A third, independent race sits one level down.**
`Vehicles.VehicleRegionCostCalculator.pathCostSamples` is a `private static int[11]` shared
across every instance and written from inside the async task. Two concurrent path requests
overwrite each other's samples with no lock and no error.

The fix is ours to write and nobody else's: three `MP.IsInMultiplayer`-gated Harmony prefixes
(`VehiclePathingSystem.InitThread`, `VehiclePathFollower.RequestNewPath`,
`WorldVehiclePathGrid.RecalculateAllPathCostsAsync`), ~60 lines. The first is the one that
closes all five uncovered `ThreadAvailable` readers at once, by leaving `dedicatedThread`
null. VF announces that configuration in the log — *"Loading map without DedicatedThread"* —
which is the only positive confirmation available anywhere on this path.

*[#69](https://github.com/cjd721/Rimworld-Archinity/issues/69),
`docs/specs/WORLD-INFRASTRUCTURE.md`. `Vehicles.dll` and `SmashTools.dll`
(`3014915404/1.6/Assemblies/`, workshop only — no `Mods/` copy, so T-22 does not bite);
`Multiplayer.Compat.VehicleFramework` from `Multiplayer_Compat_Referenced.dll`
(`1629973374/1.6/Referenced/`). Reader counts enumerated over a whole-assembly decompile, not
sampled. `ilspycmd` 8.2.0, 2026-09-12.*

### T-75 — `debugUseMultithreading` cannot be set; there is no flag to turn the threading off

The field that every plan for T-74 reaches for **does not exist at runtime.**
`Vehicles.SectionDebug.debugUseMultithreading` looks like a scribed bool and is not: its
`Scribe_Values.Look` sits inside `if (DebugProperties.Debug)`, and
`Vehicles.DebugProperties.Debug` is an `internal static readonly bool = false` in the shipped
1.6 build. So it is **never written to `config/ModSettings/`, never read back, and resets to
its field initialiser — `true` — on every launch**. A settings file edited by hand is
discarded on load with no message.

Three supporting facts, each enumerated over the whole assembly rather than sampled. **No
settings UI draws it**: the identifier occurs four times in `SectionDebug` — the declaration,
`ResetSettings`, the guarded `ExposeData` line and `RevalidateAllMapThreads` — and there is no
`CheckboxLabeled` for it anywhere. **`SectionDebug.RevalidateAllMapThreads`, the only method
that would act on the flag being false, is referenced from nowhere**; the string occurs
exactly once in the assembly, at its own definition. And a null-interleaved UTF-16 sweep of
both corpus roots plus `Data/` returns `Vehicles.dll` 1.4 and 1.6 and nothing else — **no mod
sets it either**.

The live gate is `VehiclePathingSystem.InitThread`'s own read of
`VehicleMod.settings.debug.debugUseMultithreading`, and in the shipped build that read always
returns `true`. The consequence for sourcing: **any plan priced as "one settings flag" against
this field is priced against a field that does not exist**, and T-74's threading is not
switchable from outside our own assembly.

*[#69](https://github.com/cjd721/Rimworld-Archinity/issues/69). `Vehicles.dll`
(`3014915404/1.6/Assemblies/`) decompiled whole; `Vehicles.SectionDebug`,
`Vehicles.DebugProperties.Debug`, `Vehicles.VehiclePathingSystem.InitThread`. Corrects the
Vehicle Framework row in `docs/data/MOD-VERDICTS.md` § *Real*. `ilspycmd` 8.2.0, 2026-09-12.*

### T-78 — The gravship takeoff and landing are not equally protected

`Verse.WorldComponent_GravshipController.WorldComponentUpdate` advances the cutscene on
`Time.deltaTime`, gated on `Prefs.GravshipCutscenes`, and calls **both** `TakeoffEnded()`
and `LandingEnded()` from there. Multiplayer patches both — differently:

| | `TakeoffEnded` | `LandingEnded` |
|---|---|---|
| patch | `Multiplayer.Client.Patches.PatchGravshipTakeoffEnded`, prefix | `…PatchGravshipLandingEnded`, prefix |
| body | `GravshipTravelUtils.StopFreeze();`<br>`CloseSessionAt(__instance.takeoffTile);` | `Rand.PushState();`<br>`Rand.StateCompressed = __instance.map.AsyncTime().randState;`<br>plus a `Finalizer` calling `Rand.PopState()` |
| `Rand` wrapper | **none** | yes |
| client freeze | **lifted here, before the body runs** | held until here |

`Multiplayer.Client.Patches.PatchGravshipCutsceneToFreeze` postfixes `InitiateTakeoff`
and `InitiateLanding` with `GravshipTravelUtils.StartFreeze()`, which sends a
`ClientFreezePacket` to every client. It **opens** the window that the takeoff prefix
closes — it does not protect the takeoff body.

**Consequence.** `GravshipUtility.TravelTo` is called from inside `TakeoffEnded`'s body,
so a Harmony patch on either one runs with the simulation unfrozen, with no `Rand`
state pushed, on a path whose timing depends on a per-client `Prefs` value. Two clients
reach it at different ticks. A game-state write there desyncs, and **nothing reports it**
— the symptom is a divergence some time after a gravship launch.

Reading only `PatchGravshipLandingEnded` invites the opposite conclusion, because that
one is fully protected. **Check the takeoff half separately.**

**Fix:** do not hang game-state writes on `TakeoffEnded` or `TravelTo`. Detect a
relocation on a synced tick by comparing the settled tile against a scribed previous
value — see `docs/specs/TRACE.md` § *The escape rule*.

**Related, and not a multiplayer issue but adjacent:** `GravshipUtility.TravelTo`
reassigns its own `oldTile` parameter — `if (oldTile.Layer != newTile.Layer) oldTile =
newTile.Layer.GetClosestTile_NewTemp(oldTile);`. A **postfix** reads the mutated
value, so a cross-layer move measures from a projected tile rather than the origin. Use a
prefix or `__state` if you must patch it.

*[#56](https://github.com/cjd721/Rimworld-Archinity/issues/56), `docs/specs/TRACE.md`.
`RimWorldWin64_Data/Managed/Assembly-CSharp.dll`
(`WorldComponent_GravshipController.WorldComponentUpdate` / `.TakeoffEnded` /
`.LandingEnded` / `.ResetCutscene`, `GravshipUtility.TravelTo`) and `Multiplayer.dll`
(`2606448745/1.6/AssembliesCustom/`). 1.6.4871.*

### T-80 — Multiplayer's caravan sync net covers float-menu options and nothing else

**What the net covers.** `Multiplayer.Client.SyncActions.Init` registers one `SyncAction` over
`WorldObject.GetFloatMenuOptions(Caravan)` and calls `PatchAll("GetFloatMenuOptions")`. In
`SyncAction.DoSync`, every yielded option gets
`actionGetter(current) = actionWrapper(...) ?? delegate { ActualSync(...); }`, and the default
wrapper is `(…) => (Action)null`, so a `null` wrapper falls through to the sync path. **Every
`FloatMenuOption` the method yields is synced, hand-rolled or not.**
`WorldObjectCaravanMenuWrapper`'s non-null branch is not the sync case — it defers the command
behind `CaravanArrivalActionUtility`'s confirmation dialog.

**What the net does not cover, which is the trap.** `SyncAction`'s registration only ever sees
`FloatMenuOption`s returned from `WorldObject.GetFloatMenuOptions(Caravan)`. Two things on a caravan
are not that, and are therefore **never synced, with no error and no log line**:

- a `Command_Action` (or any `Gizmo`) yielded from `Caravan.GetGizmos`, including one added by a
  postfix;
- any button inside a `Window` / `Dialog_*`, however it was opened.

Either one can mutate world state on one client only. VEF's
`Outposts.Dialog_CreateCamp.DoOutpostDisplay` founds an outpost exactly this way —
`WorldObjectMaker.MakeWorldObject` + `NameGenerator.GenerateName` + `Find.WorldObjects.Add` +
`AddPawn`, inline in a `Widgets.ButtonText` branch, reached from a `Caravan.GetGizmos` postfix.

**The tell, when a world object is involved:** `WorldObjectMaker.MakeWorldObject` calls
`Find.UniqueIDsManager.GetNextWorldObjectID()`, and MP's `UniqueIdsPatch` hands out **negative,
decreasing, client-local IDs** while `Multiplayer.InInterface` is true — so the object exists with a
negative ID on the clicking client and not at all on the other.

**Fix:** commit through an explicit `[SyncMethod]`, or move the commit into a `FloatMenuOption` on
the world object. Do not assume a gizmo or a dialog inherits the caravan net.

*[#81](https://github.com/cjd721/Rimworld-Archinity/issues/81) and
[#92](https://github.com/cjd721/Rimworld-Archinity/issues/92), `docs/specs/TERRITORY.md`.
`Multiplayer.Client.SyncActions.Init` / `SyncAction.DoSync` /
`SyncActions.WorldObjectCaravanMenuWrapper` / `Multiplayer.Client.UniqueIdsPatch` from
`Multiplayer.dll` (`2606448745/1.6/AssembliesCustom/`);
`Outposts.Dialog_CreateCamp.DoOutpostDisplay` from `Outposts.dll`
(`2023507013/1.6/Assemblies/`). 1.6.4871.*

### T-81 — Overriding `WorldObject.UpdateRateTicks` escapes Multiplayer's VTR sync

`WorldObject.DoTick` accumulates `tickDelta` and calls `TickInterval(tickDelta)` when
`tickDelta > UpdateRateTicks` or on a hash-offset interval, where
`UpdateRateTicks => !WorldRendererUtility.WorldSelected ? 15 : 1` — client-local viewport state.
Multiplayer repairs it: `Multiplayer.Client.Patches.VtrSyncWorldObjectPatch` prefixes
`WorldObject.UpdateRateTicks` to return `Multiplayer.AsyncWorldTime.VTR`, whose `CurrentPlayerCount`
is mutated only from the synced `CommandType.PlayerCount` world command.

Harmony patches the declaration it is pointed at. MP patches `RimWorld.Planet.WorldObject` and
`Verse.Projectile` **separately** — and elsewhere in the same assembly `SyncAction.PatchAll`
enumerates `AllSubtypesAndSelf()` rather than trusting a base-declaration patch. A `WorldObject`
subclass of ours that overrides the property is covered by neither.

**The symptom is not drift.** `DoTick` passes the accumulated `tickDelta` and consumers decrement by
`delta`, so elapsed ticks are conserved. What diverges is the **phase and granularity** at which a
timer crosses zero: the same production or expiry fires on a different tick on each client, taking
any `Rand` inside it to a different stream position. Silent until the trace names something else.

**Fix:** do not override it. Put new clocks on `Tick()` / `CompTick()`, which run unconditionally
every tick, and stagger with `Gen.IsHashIntervalTick(WorldObject, int)`. Note that VEF's
`Outposts.Outpost` puts production on the gated `TickInterval(delta)` and is safe **only** because it
does not override the property.

*[#81](https://github.com/cjd721/Rimworld-Archinity/issues/81) and
[#92](https://github.com/cjd721/Rimworld-Archinity/issues/92), `docs/specs/TERRITORY.md`.
`RimWorld.Planet.WorldObject.DoTick` / `.UpdateRateTicks`;
`Multiplayer.Client.Patches.VtrSyncWorldObjectPatch` and `Multiplayer.Client.SyncAction.PatchAll`
from `Multiplayer.dll` (`2606448745/1.6/AssembliesCustom/`); `Outposts.Outpost` from
`Outposts.dll` (`2023507013/1.6/Assemblies/`). 1.6.4871.*

### T-82 — Multiplayer syncs a `DiaOption` by its index in the option list

**Two Harmony prefixes sit on `DiaOption.Activate`, and both identify the option by its position
in `curNode.options`.** Which one carries a given click depends on how the dialog was opened.

- `Multiplayer.Client.NodeTreeDialogSync.Prefix` fires only when `Multiplayer.session != null`
  **and** `SyncUtil.isDialogNodeTreeOpen` **and** `__instance.dialog is Dialog_NodeTree`. It
  routes the click through `[SyncMethod] internal static void SyncDialogOptionByIndex(int position)`
  — declared **on `NodeTreeDialogSync` itself**, not on `SyncMethods` — which re-activates
  `curNode.options[position]` on every client. **It re-resolves its target client-locally**:
  the synced method finds the dialog with `Find.WindowStack.WindowOfType<Dialog_NodeTree>()` and
  activates `options[position]` on whatever that returns. So when this path takes a click on a
  stale `isDialogNodeTreeOpen`, the index lands on **a different dialog**, not merely a different
  list — and building identical option lists, the fix below, does not save you.
- `Multiplayer.Client.DiaOptionActivate.Prefix` fires when `Multiplayer.InInterface` **and**
  `PersistentDialog.FindDialog(__instance.dialog) != null`, and calls
  `persistentDialog.Click(persistentDialog.ver, persistentDialog.Dialog.curNode.options.IndexOf(__instance))`.
  `Multiplayer.Client.PersistentDialog.Click(int ver, int opt)` is itself `[SyncMethod]`, running
  `Dialog.curNode.options[opt].Activate()` behind a `ver` guard that drops a click made against a
  stale node.

**Neither prefix declares a Harmony priority**, so on any surface where both gates hold at once
the winner is patch order, and it is **not determinable from the decompile** [V on the absence of
priority, [I] on which wins]. The stale-flag window is narrow but real, and it arrives from an
unrelated incident: `isDialogNodeTreeOpen` is armed by the two caravan incident workers below and
is not cleared by anything the *other* path runs.

**For the faction comms console it is the second one.** `SyncUtil.isDialogNodeTreeOpen` is armed
only by `SyncUtil.DialogNodeTreePostfix`, applied only by `SyncUtil.PatchMethodForDialogNodeTreeSync`
← `Sync.RegisterSyncDialogNodeTree`, whose in-assembly call sites are the `[SyncDialogNodeTree]`
attribute scan in `Sync.RegisterAllAttributes` plus **exactly two explicit registrations** in
`SyncMethods` — `IncidentWorker_CaravanMeeting.TryExecuteWorker` and
`IncidentWorker_CaravanDemand.TryExecuteWorker`. Neither is the comms console, so on that surface
`NodeTreeDialogSync.Prefix` falls straight through: it sets `isDialogNodeTreeOpen = false` and
returns `true`. The comms dialog reaches `DiaOptionActivate` instead because
`Multiplayer.Client.CancelDialogNodeTree` prefixes `WindowStack.Add` and, when
`Multiplayer.MapContext != null` and the window has a registered binding, builds a
`PersistentDialog` and adds it to `mapContext.MpComp().mapDialogs` — and
`PersistentDialog_NodeTreeWithFactionInfo : PersistentDialog<Dialog_NodeTreeWithFactionInfo>` is
exactly that binding. All [V].

**The failure.** A postfix that *appends* options to the faction dialogue must build the same
list, in the same order, on both clients. If a gate omits an option on one client and not the
other, index *n* activates one action on one machine and a different action on the other —
**silently, with no error on either.** A world-state gate (goodwill, standing, a per-faction cap)
is exactly the kind that can differ between two clients mid-evaluation.

**Three ways a bad index goes wrong, and only one of them is loud [V]:**

- `DiaOptionActivate` applies **no `>= 0` check** to `IndexOf`. An option missing from the
  *receiving* dialog's list sends `opt = -1`, and `Click` indexes `options[-1]` — that one throws,
  on the receiving side, far from the click.
- `NodeTreeDialogSync` does check, but its `return false` sits **outside** the `if (num >= 0)`
  guard. A `FindIndex` miss therefore swallows the click entirely: nothing is synced, nothing is
  activated locally, and `isDialogNodeTreeOpen` is left set. The player clicks and nothing happens.
- Two lists that merely *differ in order* produce no error at all on either side — the wrong
  action simply runs on one client.

**Fix, and it covers the divergent-list cause only: disable an unavailable option; never omit it.**
`DiaOption.Disable(string newDisabledReason)` keeps the option in the list and greys it with the
reason concatenated into the label, which is what makes a gate on world state safe here. **It is
necessary and not sufficient** — against the client-local re-resolution above, an identical list on
both machines still activates against whichever `Dialog_NodeTree` each client's `WindowStack`
happens to return. A reader who has already done this and is still diverging is looking at cause 2,
not at a failure of the register.

⚠ **And do not reach for `AddAndDecorateOption` to do it.** Vanilla's helper is **not** a method on
`FactionDialogMaker` — it is a **local function inside `FactionDialogFor(Pawn, Faction)`**, IL name
`<FactionDialogFor>g__AddAndDecorateOption|0_0`, so
`AccessTools.Method(typeof(FactionDialogMaker), "AddAndDecorateOption")` returns **null** — the same
silent-null-target class as `Pawn.GetDisabledWorkTypes`'s `FillList` local (**T-79**,
`docs/data/PARTS-BIN.md` § 5.3), and the `|0_0` ordinal can shift on any vanilla rebuild. It is also
**not a blanket disable**: the body is
`if (needsSocial && negotiator.skills.GetSkill(SkillDefOf.Social).TotallyDisabled) opt.Disable(…)`,
so with a socially-capable negotiator those options are added untouched [V]. Both facts point the
same way — **an option appended by a postfix carries its own `Disable` reason and nothing vanilla
overwrites it.**

The mechanisms are [V]; the divergence consequence is [I] until two clients are run — it is one of
the observations [#16](https://github.com/cjd721/Rimworld-Archinity/issues/16) owns.

*[#93](https://github.com/cjd721/Rimworld-Archinity/issues/93), `docs/specs/POLITICS.md` §
*Standing as a content gate*; consumed by
[#73](https://github.com/cjd721/Rimworld-Archinity/issues/73).
`Multiplayer.Client.NodeTreeDialogSync.Prefix` / `.SyncDialogOptionByIndex`,
`Multiplayer.Client.DiaOptionActivate.Prefix`, `Multiplayer.Client.PersistentDialog.Click` /
`.FindDialog`, `Multiplayer.Client.CancelDialogNodeTree.Prefix`,
`Multiplayer.Client.PersistentDialog_NodeTreeWithFactionInfo`,
`Multiplayer.Client.SyncUtil.DialogNodeTreePostfix` / `.PatchMethodForDialogNodeTreeSync`,
`Multiplayer.Client.Sync.RegisterSyncDialogNodeTree` — all from `Multiplayer.dll`
(`2606448745/1.6/AssembliesCustom/`), decompiled 2026-09-12 with `ilspycmd` 8.2.0;
`RimWorld.FactionDialogMaker.FactionDialogFor`'s local `AddAndDecorateOption`,
`Verse.DiaOption.Disable` / `.OptOnGUI`. 1.6.4871.
**Amended 2026-09-12 from [#110](https://github.com/cjd721/Rimworld-Archinity/issues/110)**: the
second cause — `SyncDialogOptionByIndex` re-resolving its target through
`Verse.Find.WindowStack.WindowOfType<Dialog_NodeTree>()`, which makes the index land on a different
dialog rather than a different list — plus the absence of a Harmony priority on either prefix, and
the consequent scoping of the fix to cause 1. Same assembly and build.*

### T-95 — Subclassing `Dialog_NodeTree` drops it out of Multiplayer's bindings

**Multiplayer wraps a `Dialog_NodeTree` only if its *exact* runtime type is in a lookup table,
and a subclass of yours is not.** `Multiplayer.Client.CancelDialogNodeTree.Prefix` hands the
window to `PersistentDialog.CreateInstance(Map, Dialog_NodeTree)`, which does
`bindings.TryGetValue(dialog.GetType(), null)` — an exact-type dictionary lookup, no base-chain
walk. `bindings` is filled by `PersistentDialog.BindAll(Assembly)` → `FindDialogForType` →
`GenGeneric.GetTypeWithGenericDefinition(type, typeof(PersistentDialog<>))`, so it holds only the
types Multiplayer ships a proxy for: `Dialog_NodeTree`, `Dialog_NodeTreeWithFactionInfo` and
`Dialog_Negotiation` [V].

**On a miss, `CreateInstance` returns `null`** and `CancelDialogNodeTree.Prefix` therefore
returns `true` — the local `WindowStack.Add` proceeds, and the dialog exists on the adding
client and nowhere else.

**Every downstream door is then shut too, and none of them says so [V]:**

- `Multiplayer.Client.DiaOptionActivate.Prefix` is gated on
  `PersistentDialog.FindDialog(__instance.dialog) != null`; there is no such dialog, so it falls
  through and `DiaOption.Activate` runs **client-locally**.
- `Multiplayer.Client.NodeTreeDialogSync.Prefix` is gated on `SyncUtil.isDialogNodeTreeOpen`,
  which is normally false (**T-82**), so it falls through as well.
- `Multiplayer.Client.ForceShowDialogs` reads `mapDialogs`, which has no entry, so the other
  client is never shown the window.

**The one diagnostic is empty.** The miss branch is
`Log.Warning($"Unknown Window Type {type}")` — and `type` is the **result variable of the failed
`TryGetValue`**, so it is `null` at that point. The line prints `Unknown Window Type ` with no
type name, which is unsearchable and reads as noise [V].

**This is a constraint on the mod, not a limit of the engine, and the distinction matters.**
`PersistentDialog.Bind(Type target, Type proxy)` and `PersistentDialog.BindAll(Assembly)` are both
**public** [V], so a mod that takes a `Multiplayer.API` reference can register its own
`Dialog_NodeTree` subclass together with its own `PersistentDialog<T>` proxy and get the whole
path back. **Archinity takes no such reference** — `Archinity.Altar/Source/Archinity.Altar.csproj`
references `Assembly-CSharp`, the Unity modules and Harmony, and nothing else [V] — so for us the
vanilla types are the only bound ones.

**Fix: use `Dialog_NodeTree` itself and carry per-dialog state somewhere else** — on the building,
the comp or the def, not in fields on a window subclass. `docs/specs/ALTAR.md` § 10 does exactly
this for the altar's lottery offer: the four drawn genes live on `Building_Altar` as scribed
state, and the dialog is a plain `Dialog_NodeTree` built from them each time.

*[#110](https://github.com/cjd721/Rimworld-Archinity/issues/110), `docs/specs/ALTAR.md` § 10.
`Multiplayer.Client.PersistentDialog.CreateInstance` / `.Bind` / `.BindAll` / `.FindDialog`,
`Multiplayer.Client.PersistentDialog_NodeTree`,
`Multiplayer.Client.PersistentDialog_NodeTreeWithFactionInfo`,
`Multiplayer.Client.CancelDialogNodeTree.Prefix`, `Multiplayer.Client.DiaOptionActivate.Prefix`,
`Multiplayer.Client.NodeTreeDialogSync.Prefix`, `Multiplayer.Client.ForceShowDialogs.Prefix` —
all from `Multiplayer.dll` (`2606448745/1.6/AssembliesCustom/`), decompiled 2026-09-12 with
`ilspycmd` 8.2.0. 1.6.4871.*

### T-96 — A modded `ChoiceLetter`'s options are synced by neither mechanism

**Vanilla's choose-one-of-N letter is not a synced primitive; each vanilla letter was synced by
hand, one lambda at a time.** `Multiplayer.Client.SyncDelegates.InitChoiceLetters` carries
**13 registration calls covering eight `ChoiceLetter` subclasses** — `_ChoosePawn`,
`_AcceptJoiner`, `_AcceptVisitors`, `_RansomDemand`, `_BabyToChild`, `_BabyBirth`,
`_GrowthMoment`, `_AcceptCreepJoiner` — through `SyncDelegate.Lambda`,
`SyncMethod.LambdaInGetter(type, "Choices", n)` and `SyncMethod.Register` [V]. **A modded
subclass appears on none of them**, so each of its `DiaOption.action`s runs on the clicking
client alone.

**The second door is shut for a different reason.** `Verse.ChoiceLetter.OpenLetter()` builds a
`DiaNode`, fills it from `Choices`, and adds a `Dialog_NodeTreeWithFactionInfo` — a **bound**
type, so **T-95** is not the problem here [V]. But a letter is opened by a click in the letter
stack, and `Multiplayer.Client.Multiplayer.MapContext` is
`AsyncTimeComp.tickingMap ?? AsyncTimeComp.executingCmdMap`, both null in interface [V].
`CancelDialogNodeTree.Prefix` returns immediately on a null map context, so **no
`PersistentDialog` is created**, and `DiaOptionActivate.Prefix` then finds nothing to sync
through.

**So the letter looks right and acts wrong.** It is delivered to both clients by the letter
stack, opens identically on both, shows the same options in the same order — and the button does
something on one machine only. Nothing is logged on either side.

**How much bespoke work a single letter actually takes, as the measure of what you are not
getting [V]:** `ChoiceLetter_GrowthMoment` needed a whole
`Multiplayer.Client.Persistent.GrowthMomentSession` (an `ExposableSession` in
`map.MpComp().sessionManager`), a `GrowthMomentWindow`, a `[SyncMethod] UpdateChoices(int, List<int>)`
carrying the selection as **indexes**, a `[SyncMethod] OpenSessionWindow` so the `Rand`-drawing
`TrySetChoices` runs inside a command on every client, and a `Rand.PushState(Gen.HashCombineInt(
pawn.thingIDNumber, letter.arrivalTick))` prefix to make the draw itself identical. None of that
generalises to a letter Multiplayer has never heard of.

**Fix: do not resolve a shared decision through a `ChoiceLetter` unless you take the MP API and
register it.** Open a plain `Dialog_NodeTree` from **synced code with a map context** — a tick or
a synced command — so `CancelDialogNodeTree` converts it into a `PersistentDialog` and
`PersistentDialog.Click(int ver, int opt)` carries the click by index. `docs/specs/ALTAR.md` § 10
takes that route for the altar's lottery and records why the `ChoiceLetter` shape was rejected
despite fitting the problem better on paper.

*[#110](https://github.com/cjd721/Rimworld-Archinity/issues/110), `docs/specs/ALTAR.md` § 10.
`Multiplayer.Client.SyncDelegates.InitChoiceLetters` / `.PreLetterChoices`,
`Multiplayer.Client.Persistent.GrowthMomentSession` / `.GrowthMomentWindow`,
`Multiplayer.Client.Multiplayer.MapContext`, `Multiplayer.Client.CancelDialogNodeTree.Prefix`,
`Multiplayer.Client.DiaOptionActivate.Prefix` — from `Multiplayer.dll`
(`2606448745/1.6/AssembliesCustom/`), decompiled 2026-09-12 with `ilspycmd` 8.2.0;
`Verse.ChoiceLetter.OpenLetter`, `RimWorld.ChoiceLetter_GrowthMoment.TrySetChoices`. 1.6.4871.*

### T-97 — A `DiaOption` without `resolveTree` strands its `PersistentDialog` forever

**Multiplayer has exactly one path that removes a dialog from `mapDialogs`, and it only runs when
the close happens outside the interface.** `Multiplayer.Client.WindowStackTryRemove` postfixes
`WindowStack.TryRemove(Window, bool)` and, when
`Multiplayer.Client != null && !Multiplayer.InInterface`, does
`PersistentDialog.FindDialog(window)?.map.MpComp().mapDialogs.Remove(...)` [V]. There is no other
removal anywhere in the assembly.

`Multiplayer.Client.Multiplayer.InInterface` is
`Client != null && !Ticking && !ExecutingCmds && !reloading && Current.ProgramState == Playing &&
LongEventHandler.currentEvent == null` [V]. So the removal fires **only** when the window is
closed from inside a tick or inside a synced command — never when a player closes it by hand.
That asymmetry is deliberate: it is what makes a `PersistentDialog` undismissable, because
`Multiplayer.Client.ForceShowDialogs` prefixes `MapDrawer.DrawMapMesh` and re-adds
`mapDialogs.First().Dialog` whenever no `Dialog_NodeTree` is open [V].

**The trap is that answering the dialog is not by itself a close.** `PersistentDialog.Click(int
ver, int opt)` is `[SyncMethod]`, so it executes as a command with `ExecutingCmds` true and
`InInterface` false — the removal path is available. What actually closes the window is
`Verse.DiaOption.Activate`, whose body is `if (resolveTree) OwningDialog.Close();` **before** it
invokes `action` [V]. **An option built without `resolveTree = true` runs its action, resolves
whatever it resolves, and never closes** — so `TryRemove` never fires, the entry stays in
`mapDialogs`, and `ForceShowDialogs` re-opens an already-answered dialog on the next frame that
map is drawn. Clicking again re-runs the action.

**Nothing reports it.** There is no error, no warning, and the symptom appears only on a client
that is looking at that map — so it can survive a whole session in which one player never
switched colonies. The same applies to any code path that *resolves* the offer without closing
the window: clearing the underlying state is not enough, the dialog has to be closed from the
tick as well.

**Two rules, and both are needed:**

- **Every option on a `PersistentDialog` sets `resolveTree = true`**, including options that
  exist only to run an action. Because `Activate` closes before it calls `action`, the removal is
  not contingent on the action succeeding.
- **Any tick-side resolution closes the window itself.** `docs/specs/ALTAR.md` § 10 states this
  for the altar's lottery timeout, which must close the offer dialog from the tick and not merely
  clear the pending draw.

**Neighbouring hazard: T-82**, which is the other half of getting a `PersistentDialog` option
right — it governs what the transmitted *index* means, where this entry governs whether the
dialog ever goes away. An option list can be correct by T-82 and still strand its dialog here.

*[#110](https://github.com/cjd721/Rimworld-Archinity/issues/110), `docs/specs/ALTAR.md` § 10.
`Multiplayer.Client.WindowStackTryRemove.Postfix`, `Multiplayer.Client.Multiplayer.InInterface`,
`Multiplayer.Client.PersistentDialog.Click` / `.FindDialog`,
`Multiplayer.Client.ForceShowDialogs.Prefix`, `Multiplayer.Client.CancelDialogNodeTree.Prefix` —
from `Multiplayer.dll` (`2606448745/1.6/AssembliesCustom/`), decompiled 2026-09-12 with
`ilspycmd` 8.2.0; `Verse.DiaOption.Activate`. 1.6.4871.*

---

### T-114 — Multifaction faction creation skips the game-start hooks

`Multiplayer.Client.Factions.FactionCreator.CreateFaction` (a `[SyncMethod]`) generates a joining
player's faction, map and starting pawns without `Game.InitNewGame`. Its own `InitNewGame(Scenario)`
calls:
- `GiveAllStartingPlayerPawnsThought`;
- `ApplyPlayerStartingResearch`;
- `PostGameStart` restricted to `ScenPart_StartingResearch`;
- `ScenPart_GameStartDialog`, issuer only, via `InitLocalVisuals`.

It **never** calls `GameComponentUtility.StartedNewGame`. Every other `ScenPart.PostGameStart` is
skipped, and `Find.GameInfo.startingAndOptionalPawns` is not updated. Anything a mod does "at game
start" through those hooks happens for the host's faction and silently not for the joiner's.
Backfilling from `GameInfo.startingAndOptionalPawns` misses them too.

A single shared faction is unaffected: it starts through vanilla `Game.InitNewGame`, or is converted
from a single-player save.

*[#134](https://github.com/cjd721/Rimworld-Archinity/issues/134). `2606448745/1.6/AssembliesCustom/Multiplayer.dll`,
`Multiplayer.Client.Factions.FactionCreator.CreateFaction` / `.InitNewGame` / `.PostGameStart` /
`.InitLocalVisuals`; vanilla `Verse.Game.InitNewGame`. 1.6.4871.*

---
