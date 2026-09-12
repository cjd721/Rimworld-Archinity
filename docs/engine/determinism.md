# Determinism, ticks and `Rand`

What Multiplayer actually synchronizes, why `Rand` on a synced tick is safe, and
what the real hazard class is. This is the evidence under the **Divergence** gate —
`CODING_STANDARDS.md` § *The two gates* — the gate is the rule, this file is why it
is the rule.

Verified against `Assembly-CSharp.dll` (1.6.4871) and Multiplayer 0.11.5's
`Multiplayer.dll`, not from memory and not from a mod's behaviour. Underpins the
third-party bar in [#3](https://github.com/cjd721/Rimworld-Archinity/issues/3).

---

## What is on the synced tick and what is not

`TickManager.DoSingleTick()` contains, in order: every map's `MapPreTick`, the three
tick lists, `DateNotifierTick`, `TickScenario`, **`Find.World.WorldTick()`**,
`StoryWatcherTick`, `GameEndTick`, **`Find.Storyteller.StorytellerTick()`**,
`TaleManagerTick`. All of it is simulation.

`GameComponentUtility.GameComponentUpdate()` is called from **`Game.UpdateEntry()`
and `Game.UpdatePlay()`** — the Unity frame loop, not the tick.

| Hook | Runs | Safe to write sim state? |
|---|---|---|
| `WorldComponentTick` | inside `DoSingleTick` | **Yes** |
| `GameComponentTick` | inside `DoSingleTick` | **Yes** |
| `Thing.Tick` / `TickRare` / `TickLong` / `TickInterval` | tick lists | **Yes** |
| `WorldComponentUpdate` | frame loop | **No** |
| `GameComponentUpdate` | frame loop | **No** |

## Why `Rand` inside a synced tick is safe

There is **no per-tick reseeding**. Multiplayer runs deterministic lockstep: both
clients execute the same ticks in the same order against the same `Rand` state, so
the same *sequence* of draws yields the same results.

`Multiplayer.Client.ThingMethodPatches` — which wraps `Tick`/`TickRare`/`TickLong`/
`TickInterval`/`TakeDamage`/`Kill`/`SpawnSetup` on every `Thing` subtype — pushes
**faction and Thing context**, not a `Rand` seed. Thing ticks draw from the shared
global stream in tick order.

`Multiplayer.Client.MapRandomStateData` holds `List<uint> randomStates`: MP
checksums `Rand` state as simulation state, which is how desyncs are detected.

**The consequence: the hazard is never "a mod uses `Rand`". It is a mod consuming the
shared stream a different number of times, or at a different position, per client.**

## MP's own list of paths that must not touch the shared stream

`MultiplayerStatic` wraps `RandPatches.Prefix`/`Finalizer` — a bare
`Rand.PushState()` / `Rand.PopState()` pair — around a set it labels
**`SetCategory("Non-deterministic patches 1")`**:

`SubSustainer` lambda · `Sample` ctor · `SubSoundDef.TryPlay` ·
`Effecter.EffectTick` / `Trigger` / `Cleanup` · `LightningBoltMeshPool.RandomBoltMesh` ·
`Pawn_DrawTracker` ctor · `PawnStyleItemChooser.RandomHairFor` ·
**every public static `MoteMaker` method** · `Cable.Tick` ·
**every void `FleckMaker` and `FleckManager` method** · `LavaFXComponent.ThrowLavaSmoke` ·
`FishShadowComponent.SpawnFishFleck` · `CompFleckEmitterLongTerm.EmissionTick` ·
`RitualRoleAssignments.CanEverSpectate`

Every one is rendering- or audio-dependent — code that may run a different number of
times per client depending on camera, sound, and frame timing. **This is the
authoritative statement of the hazard class**, and it is why viewport-gated RNG
(`if (GenView.ShouldSpawnMotesAt(...)) { Rand.Value; }`) is the canonical bug.

## Why leaving the tick is the one thing that bars a mod

Work that runs outside `DoSingleTick` cannot be ordered relative to the tick, so any
`Rand` it consumes or sim state it writes is non-deterministic by construction — and
there is no XML or settings fix, because the scheduling is not data. That is the whole
content of the bar. A `WorldComponent` grinding through heavy world state inside
`WorldComponentTick` is deterministic; disliking it is a design objection about shadow
worlds, not a safety one.

**State the bar as *does any simulation path leave the tick*, never as *does it create
threads*.** The narrow form fails on real code. `Task.Run` constructs no named thread,
has no lifecycle and has no switch, so it is invisible to a sweep for thread-creation
vocabulary — and `SmashTools.TaskManager.Run(Action, CancellationToken)` is a bare
`Task.Run` behind a fire-and-forget awaiter [V]. Vehicle Framework carries both shapes,
and it is the `Task.Run` half that neither its own kill switch nor Multiplayer
Compatibility reaches; the worked case is **T-74**, and its sibling, VF's second
uncovered exit, is **T-75**.

So the census sweeps for `Task.Run`, `ThreadPool.QueueUserWorkItem`, `async void` and
`Parallel.ForEach` alongside `new Thread`. **Fan-out is not the hazard; fire-and-forget
is** — VF's `Parallel.ForEach` in `GenerateRegionsParallel` blocks until every partition
completes, so the tick sees a finished result and it is safe [V].

## Worked example — TechBlock, the shape to recognise

Verified against `1.6/Assemblies/TechBlock 1.2.1.dll`, which is what loads. (The
folder also ships a `1.0/Assemblies/TechBlock.dll`; reading that one gives different
code and a wrong conclusion — see `docs/TRAPS.md` T-22.)

`TechBlock_Component.GameComponentUpdate()` accumulates `savedProgress` and, per 25
points, calls `AddRandomProgress()` → `GenCollection.RandomElement(techLevelProjects)`
→ `Find.ResearchManager.AddProgress(val, 25f * settings.randomInsightRate)`.

Three defects, and the third is the instructive one:

1. Gated on client-local `settings.randomInsights`.
2. Magnitude scaled by client-local `settings.randomInsightRate`.
3. **The draw is taken from a per-frame method**, so it enters the shared stream at a
   frame-dependent position. Note the draw *count* is fine — the accumulator ties it
   to research progress, not frame count. It is the **interleaving position** that
   diverges, which means identical settings files do **not** fix it.

> The general lesson: when auditing a mod, do not stop at "does the number of draws
> match". Ask where in the stream the draw lands.

TechBlock's own mechanics are in `docs/engine/research-and-tech-tiers.md`.

## Settings are part of the sync surface

Mod settings drive both def-load and runtime, so a settings mismatch is a def
mismatch and often a live `Rand` mismatch as well. See `docs/TRAPS.md` T-18, with
T-19 and T-20 as the worked Medieval Overhaul cases.

## Map generation is seeded by vanilla, not by Multiplayer

Verified in [#88](https://github.com/cjd721/Rimworld-Archinity/issues/88) against the
1.6 assemblies. Recorded because the natural assumption — that MP must be seeding map
generation, and that a gap there would be reported — is wrong twice over.

**Vanilla seeds itself, at two levels** [V]:

- `MapGenerator.GenerateMap` — `Rand.PushState()`, then
  `Rand.Seed = Gen.HashCombineInt(Find.World.info.Seed, parent?.Tile.GetHashCode() ?? 0)`
  (pocket maps substitute `parent?.ID`), with `Rand.PopState()` in the `finally`.
  `parent?.PostMapGenerate()` is called **inside** that `try`, so it is covered.
- `MapGenerator.GenerateContentsIntoMap` — a second `Rand.PushState()` /
  `Rand.Seed = HashCombineInt(seed, GetSeedPart(...))` around **each** GenStep.

Both seed inputs are cross-client identical: `World.info.Seed` is world state and
`PlanetTile.GetHashCode()` is value-based. **`Site.PostMapGenerate` running unseeded
cannot happen** — the older inferred hazard in `scratch/recon-factional-war.md` is
refuted for `Verse.Rand` and upheld only for `System.Random` (**T-33**).

**Multiplayer therefore patches nothing here**, and none is missing: it carries exactly
two Harmony patches on `MapGenerator.GenerateMap` (`MapSetup`, `CleanupTileFactionContext`)
and neither touches `Rand`; `PostMapGenerate` appears zero times in the assembly [V]. MP
seeds the paths vanilla leaves loose and only those — `Game.LoadGame`, `Map.ExposeData`,
`Map.FinalizeLoading`, `CaravanEnterMapUtility.Enter`, `LongEventHandler.QueueLongEvent`.

**The consequence that matters: map generation is invisible to MP's desync detector.**
`ClientSyncOpinion.CheckForDesync` compares FP round mode, map IDs, per-map
`randomStates`, `worldRandomStates` and `commandRandomStates` — and because
`GenerateMap` pushes and pops its *own* `Rand` state, the number of draws made during
generation does not perturb the enclosing command's state at all [V]. A fresh map even
starts with matched state on both clients. **Two clients can begin ticking a
structurally different map from an identical RNG state, and MP reports nothing.** The
divergence surfaces later, as a desync whose stack trace names a pawn rather than the
map generator — and permanently through `thingIDNumber`, since different structure
counts offset every subsequent ID, which MP's own seeding then consumes.

## `UnityEngine.Random` is a third stream, and nothing on a map-gen path touches it

Swept in [#94](https://github.com/cjd721/Rimworld-Archinity/issues/94), the follow-up to
#88's `System.Random` pass. The **corpus result** is a clean zero and lives here, because
there is no live instance to trap. The **silent half** of the same finding does not need
one: MP Compat's `FixUnityRNG` half-fixes a method and says nothing, which is a standing
condition on our own code and on anything the sourcing ledger adds later. That half is
registered as **T-51** — read it alongside **T-33**, whose reassurance it does *not*
inherit.

**Three independent RNG streams exist in a running RimWorld, and there is no fourth** [V]:

| Stream | State | Seeded by map gen? |
| --- | --- | --- |
| `Verse.Rand` | `private static uint seed` + `iterations`, `Stack<ulong> stateStack` | **Yes** — `MapGenerator` pushes and seeds it |
| `System.Random` | per-instance, in the instance | No — **T-33** |
| `UnityEngine.Random` | process-global, inside the Unity engine | No |

The enumeration was **tested, not assumed** [V]: `Unity.Mathematics.Random` is **zero**
corpus-wide, and `RandomNumberGenerator` / `RNGCryptoServiceProvider` appear in 24 and 2
assemblies respectively — every one of them `0Harmony.dll` or Multiplayer's
`RestSharp.dll`, no mod game code.

**`Rand.PushState` cannot reach `UnityEngine.Random`, and this is read from the code, not
inferred from `System.Random`'s case** [V]. `Verse.Rand` (decompiled from
`Assembly-CSharp.dll`) is closed over its own two fields: `PushState()` pushes
`StateCompressed` — `seed | ((ulong)iterations << 32)` — and `PopState()` assigns it back;
`Rand.Seed`'s setter writes `seed` and zeroes `iterations`; every draw is
`MurmurHash.GetInt(seed, iterations++)`. The type contains **no** reference to
`UnityEngine.Random` and **no** call to `Random.InitState`. An IL scan of the whole of
`Assembly-CSharp.dll` finds `UnityEngine.Random` called from exactly two methods —
`RimWorld.Planet.WorldDrawLayer_Clouds.Regenerate` (a shader seed) and
`RimWorld.GravshipRenderer.EmitSmoke` — and neither is `Verse.Rand`.

**It is structurally worse than `System.Random`, not equivalent.** A `System.Random`
hazard needs a *fresh unseeded instance*; a mod that writes `new Random(syncedValue)` is
safe. `UnityEngine.Random` has one process-global state, and **RimWorld never calls
`Random.InitState`** — nor does any of the 155 mods, nor is `Random.state` ever read or
written [V]. (MemberRef enumeration across all 55 TypeRef-carrying assemblies plus vanilla:
the only members referenced anywhere in the corpus are `Range`, `value`, `insideUnitSphere`
and `ColorHSV`.) Unity seeds that global from system entropy at process start, so it is
different on each client in every session — **[I]**, inferred; Unity's native engine was not
read. **The conclusion survives either way**: whatever seeds it, nothing re-seeds it to a
synced value, so it cannot be assumed equal across two clients. Every draw is
client-divergent by default and there is no seeded-constructor escape. One on a map-gen path
would be strictly worse than KCSG's.

**Vanilla draws the line deliberately, and it is the line to copy** [V]:
`WorldDrawLayer_Satellites.Regenerate` wraps its generation in
`Rand.PushState(); Rand.Seed = Find.World.info.Seed; … Rand.PopState();`, while its sibling
`WorldDrawLayer_Clouds.Regenerate` reaches for `UnityEngine.Random.value` — because clouds
are allowed to differ between clients and satellites are not.

**The corpus result** [V]: across all 155 mods on both roots plus vanilla, **seven live 1.6
call sites in six mods** touch `UnityEngine.Random`, and **none is on a map-generation
path** — no `GenStep`, no `SymbolResolver`, no `GenStepDef` worker, no `PostMapGenerate`, no
`MapComponent.MapGenerated`. They are a settings window, a `JobDriver` tick action, an
animation-editor colour, a texture generator, a `Verb` tick, a pre-game xenotype pick and a
`Fleck` emitter. (The five DLC add nothing to search: they ship **no assemblies of their
own** — all DLC code is in `Assembly-CSharp.dll`. Five further assemblies carry the TypeRef
and call no member of it, including `UnityEngine.UnityWebRequestModule.dll`, where it is
inert.)

**Two of the seven are simulation, not one** [V]:

- `VFE_Settlers.JobGivers.JobDriver_PlayFiveFingerFillet.WatchTickAction` (VFE — Settlers)
  runs on the synced tick, and on the `Random.Range(0, 100) > 80` branch calls
  `pawn.TakeDamage(new DamageInfo(DamageDefOf.Cut, …))` and
  `pawn.skills.Learn(SkillDefOf.Melee, 50f)` — damage and skill XP, both sim state. It is
  also the corpus's **only `PatchUnityRand`-covered site**: MP Compat patches precisely this
  method, 1:1 with the mod's single call site. That is what makes it safe, and it is safe
  only because someone else wrote the patch.
- `NCLWorm.Verb_WormDeathRay.BurstingTick` (Mechanoids: Total Warfare) is **uncovered** —
  that mod appears nowhere in `Multiplayer_Compat.dll`. A `Verb` tick runs inside
  `DoSingleTick`, so the draw is a live desync source. It is a *combat* divergence and
  whether the mod ships is [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s
  call; carried as cargo, not resolved here.

**Neither is map generation**, which is the question the sweep was run to answer.

**The count is version-conditional** [I]. Range Finder (`brrainz.rangefinder`, workshop
`1332119637`) ships **two different** `RangeFinder.dll`s, and its `LoadFolders.xml` puts
both `/` and `1.6` in the v1.6 path. The two builds disagree on this exact symbol:
`1.6/Assemblies/RangeFinder.dll` (21,504 B) carries the `UnityEngine.Random` TypeRef, and
root `Assemblies/RangeFinder.dll` (36,352 B) carries none [V]. So the corpus figure is
**seven-in-six or six-in-five**, and `RangeFinder.RangeFinderSettings.DoWindowContents` is a
**conditional** site until the launch-log check already listed as open in
`docs/data/MOD-VERDICTS.md` § *Range Finder* settles which build loads. It is a mod-settings
window under either build, so no conclusion above moves — but the number does, and a sweep
that reports a bare count without pinning the build is reporting a number it did not verify.

**Multiplayer core carries no handling for it** [V]: `Multiplayer.dll` 1.6 holds a
`UnityEngine.Random` TypeRef but calls no member of it. As with `System.Random`, the compat
layer is the only carrier.

**MP Compat's coverage of this corpus is one mod** [V]. `PatchUnityRand` is invoked at
**11 call sites across 10 compat classes**, which between them declare **12** package IDs
(`RimNauts2` also claims `rimfridge.kv.rw`; `VanillaRacesFungoid` also
`vanillaracesexpanded.lycanthrope`). Exactly one of the twelve is on disk —
`OskarPotocki.VanillaFactionsExpanded.SettlersModule` — covering that mod's only call site.
Two of the corpus's seven sites use members the facility could not rewrite even with an
allowlist entry (VGE's `insideUnitSphere`, Vehicle Framework's `ColorHSV`). **What it does
and does not rewrite, and why its warning does not mean what T-33's means, is T-51.**

**The build this negative owes has not landed** [I]. #94 priced it as one line of prose in
`CODING_STANDARDS.md` § *The two gates*, under **Divergence**: *`UnityEngine.Random` is
banned in Archinity assemblies; use `Verse.Rand`.* **That line is not there.** The gate
today names `ModSettings`, camera and viewport state, `Find.CurrentMap`, selection, `Prefs`,
wall-clock time and unkeyed static caches, and carves `Rand` out; it says nothing about the
Unity stream. It is a review-time rule rather than code, because the section above
establishes there is no correct way to use that stream in synced code — so it needs no
carve-out, no reviewer judgement and no exception path. Until it is written, this file is
the only place the prohibition exists. The priced fallback — our own member-complete
transpiler, ~60–80 lines, *if* #14 ever ships an offender — is in #94 §7 and is not owed yet.

**The requirement underneath it now has an owner.** Nothing in `docs/requirements/` states
that map generation must be cross-client identical; #88 raised the gap and #94 depended on
it. It is
[#104](https://github.com/cjd721/Rimworld-Archinity/issues/104). The prohibition above is
justified *by* that requirement, so it is conditional on #104 answering yes.

**The seam this enumeration does not cover.** Three RNG streams are accounted for;
**non-RNG map-generation divergence is not.** A modded `GenStep` that branches on a
reference `GetHashCode()`, iterates an unordered collection in hash order, or reads
`DateTime.Now` / `Environment.TickCount` diverges between clients with no RNG involved at
all — and per the section above, MP's checksum would not see it either. **That sits on no
ticket.** #88 examined `PlanetTile.GetHashCode()` alone, and only far enough to confirm it
is value-based.

## What is not synced for free

Nothing is covered by default. For the faction-mutation case specifically —
`WorldObject.SetFaction`, `FactionDef` mutation, and which operations pull `Rand`
and must therefore sit inside the same synced command — see
`docs/engine/factions-and-worldgen.md` § *Multiplayer*.

---

## MP serialises the comms-console dialogue, options included

Established on [Reverence, end to end](https://github.com/cjd721/Rimworld-Archinity/issues/98),
and it constrains anyone adding an option to a faction dialogue.

`Multiplayer.Client.PersistentDialog_NodeTreeWithFactionInfo` scribes every `DiaNode` and
`DiaOption` — text, `resolveTree`, `disabled`, `disabledReason`, `clickSound` — and
reconstructs each option's `action` delegate through a `FieldSave` that walks the closure's
captured fields and picks a scribe mode **per field type**: `ParseHelper`-handled values,
`Def`, `ILoadReferenceable`, `IExposable`, or a plain-object fallback [V].

**The binding constraint is not the field types — it is a hardcoded whitelist of declaring
types, and it will reject our code.** Delegate reconstruction runs
`DelegateSerialization.CheckMethodAllowed`, which walks to the delegate method's outermost
declaring type, walks up its base chain, and requires a member of this fixed array [V]:

> `Ability`, `AbilityComp`, `Command`, `ThingComp`, `Dialog_BeginRitual`, `LordToil`,
> `Precept`, `SocialCardUtility`, `Letter`, `FactionDialogMaker`, `GenGameEnd`,
> `IncidentWorker`, `QuestPart`, `ResearchManager`, `ShipUtility`

Anything else throws `"Delegate deserialization: method not allowed"` **on load**. A closure
compiled into a display class nested in one of our own patch classes resolves to *our* type,
base `object`, and is refused. Vanilla's own dialogue options work because
`FactionDialogMaker` is on the list.

**So an option added by a postfix on `FactionDialogMaker.FactionDialogFor` reaches both clients
and survives save/load only if its action's method is hosted on a type deriving from one of
those 15** — `QuestPart`, `Command`, `Letter` and `ThingComp` are the realistic hosts — or MP
Compatibility is persuaded to extend the array.

The field-type rule still applies on top of that: capture the `Faction` (which is
`ILoadReferenceable`) and primitives. Capturing something outside the five modes is not a quiet
no-op either — plain-object mode throws
`"Persistent dialog field deserialization: Unsupported plain object type"` unless the type is
compiler-generated [V]. **Both failures are loud and both happen at load, not at click.**

`DiaOption.Disable(reason)` is safe by all of this — `disabled` and `disabledReason` are
scribed as plain values with no delegate involved — which makes the disabled-with-reason idiom
the cheap way to show a gate before it opens, and the only half of a gated option that carries
no delegate risk at all.

**The live-click path is separate from the scribing above, and it makes a comms-console option a
synced command for free.** There are **two** Harmony prefixes on `DiaOption.Activate`, and which
one carries a click depends on how the dialog was opened. All [V]:

- `Multiplayer.Client.NodeTreeDialogSync.Prefix` — gated on `Multiplayer.session != null`,
  `SyncUtil.isDialogNodeTreeOpen`, and the option's own `dialog` being a `Dialog_NodeTree`. It
  routes through `[SyncMethod] internal static void SyncDialogOptionByIndex(int position)`,
  declared **on `NodeTreeDialogSync` itself**.
- `Multiplayer.Client.DiaOptionActivate.Prefix` — gated on `Multiplayer.InInterface` and
  `PersistentDialog.FindDialog(__instance.dialog) != null`, calling
  `PersistentDialog.Click(int ver, int opt)`, itself `[SyncMethod]`, which runs
  `Dialog.curNode.options[opt].Activate()` behind a `ver` guard that drops a click made against a
  stale node.

**For the faction comms console the second is the live one, and the first falls through.**
`isDialogNodeTreeOpen` is armed only by `SyncUtil.DialogNodeTreePostfix`, applied only via
`Sync.RegisterSyncDialogNodeTree` — whose in-assembly call sites are the `[SyncDialogNodeTree]`
attribute scan plus **two explicit registrations**, `IncidentWorker_CaravanMeeting.TryExecuteWorker`
and `IncidentWorker_CaravanDemand.TryExecuteWorker`. Neither is the comms console, so
`NodeTreeDialogSync.Prefix` sets the flag false and returns `true`. The comms dialog is instead a
registered `PersistentDialog`: `CancelDialogNodeTree` prefixes `WindowStack.Add` and, when
`Multiplayer.MapContext != null` and the window has a binding, builds one and adds it to
`mapContext.MpComp().mapDialogs` — and `PersistentDialog_NodeTreeWithFactionInfo` is that binding.
So "a `DiaOption` is synced for free" is true of a dialog opened inside a synced command with map
context, and **not** of a `DiaOption` reached any other way. [V]

**Consequence: an option appended to the faction dialogue needs no `[SyncMethod]` of ours.** The
delegate whitelist above still governs whether its action survives *reconstruction*; this governs
whether the *click* reaches both clients, and they are different gates.

⚠ **Both mechanisms identify the option by its index in `curNode.options`.** A postfix appending
options must therefore build the same list, in the same order, on both clients — otherwise index
*n* activates one action on one machine and a different action on the other, silently, with no
error on either. **Disable an unavailable option; never omit it.** `Disable(string newDisabledReason)`
keeps it in the list, which is what makes a gate on world state safe here. Note that vanilla's
`AddAndDecorateOption` is a **local function inside `FactionDialogFor`** — unreachable by
`AccessTools.Method` — and disables only `needsSocial` options whose negotiator has Social
`TotallyDisabled`, so it never touches an appended option's own reason. See `docs/TRAPS.md`
**T-82** for the index-mismatch outcomes, including the one that swallows the click in silence.

Established on [#93](https://github.com/cjd721/Rimworld-Archinity/issues/93) and consumed by
[#73](https://github.com/cjd721/Rimworld-Archinity/issues/73); the Multiplayer members were
re-derived from `2606448745/1.6/AssembliesCustom/Multiplayer.dll` on 2026-09-12.

---

## Multiplayer does not intercept sync methods inside a long event

`Multiplayer.Client.Multiplayer.ShouldSync` is `InInterface && !dontSync`, and `InInterface` is
`Client != null && !Ticking && !ExecutingCmds && !reloading && Current.ProgramState == Playing &&
LongEventHandler.currentEvent == null` **[V]** (`2606448745/1.6/AssembliesCustom/Multiplayer.dll`,
`Multiplayer.Client.Multiplayer.InInterface`). Note `SyncField.DoSync` bypasses `ShouldSync` when
`inGameLoop` **[V]**.

Game load, worldgen and map generation all run inside a long event, so code on those paths —
`GameComponent.FinalizeInit`, `StartedNewGame`, `LoadedGame`, GenSteps — **never generates a
command**, even when it calls a registered `SyncMethod`. Our own seeding code may therefore call
e.g. `OutfitDatabase.MakeNewOutfit` there without dispatching a command. Prefer not to rely on it:
the predicate lives in someone else's assembly, and constructing the object directly is usually two
lines. Established by [#28](https://github.com/cjd721/Rimworld-Archinity/issues/28).

---

## Adding a bill is synced two different ways, and a mod can remove one of them

`SyncDelegate.Lambda(typeof(ITab_Bills), "FillTab", 2).SetContext(SyncContext.MapSelected).CancelIfNoSelectedMapObjects()`
makes the add-bill float-menu delegate a synced *delegate* — its body, including
`BillUtility.MakeNewBill`, is **replayed on every client** **[V]**. Every other caller — clipboard
paste, mod bill tabs — goes through
`SyncMethod.Register(typeof(BillStack), "AddBill").ExposeParameter(0)` **[V]**, which serialises
the finished `Bill` instead.

**A postfix on `MakeNewBill` must therefore be deterministic.** `SyncContext.MapSelected` restores
the initiator's selection on the replaying client, so `Find.Selector` reads correctly there;
**nothing restores a mod setting.**

`Multiplayer.Client.SyncMethods.AddBill_Prefix` assigns `bill.loadID` from the shared
`UniqueIDsManager` when `ExecutingCmds && bill.loadID < 0`, but it is a **backstop** — the `Bill`
constructor already assigns the id from the same manager **[V]**.

Nice Bill Tab (`Andromeda.NiceBillTab`) prefixes `ITab_Bills.FillTab` and returns `false` while its
own `Settings.EnabledMod` is true **[V]**, so with it loaded vanilla `FillTab` never runs, the
registered lambda never fires, and creation rests entirely on the `AddBill` SyncMethod. Established
by [#95](https://github.com/cjd721/Rimworld-Archinity/issues/95).

---

## Presentational separation between the two players

Verified during [#23](https://github.com/cjd721/Rimworld-Archinity/issues/23) and
[#8](https://github.com/cjd721/Rimworld-Archinity/issues/8). Recorded here because it
is the one place a deliberate per-client difference has been assessed as viable.

Under one shared player faction, every MP `Disable*ForOtherFactions` guard is
faction-compared and therefore **inert by construction**; no patch restores them
without recreating the divergence class #24 catalogued. What remains buildable is a
*presentational* layer — a filtered colonist bar, filtered letters, a filtered quest
tab.

**The load-bearing rule, verified from two directions: filter at draw time, never at
list-membership time** (`docs/TRAPS.md` T-21).

- `Letter.CanCullArchivedNow` culls the Archive by **stack membership**, so filtering
  at receive makes two clients cull different sets, and synced `ChoiceLetter` commands
  then deserialize to null. MP ships this bug with a TODO admitting it.
- If such a layer ever patches `MapPawns.FreeColonists`, `PawnsFinder` or
  `Pawn.IsColonist`, **~15 ticked readers diverge** — recreating the multifaction bug
  inside shared mode, and equally silent.

What makes it tractable:

- `ColonistBar.cachedEntries` is **never serialised**, and nothing in the tick path
  reads it.
- MP already ships the same three filters keyed on `Faction.OfPlayer` — inert under
  one faction, but a working reference implementation.
- `MP.GetPlayers()` supplies a sanctioned per-player identity.

> ⚠️ **Open standards gap.** `CODING_STANDARDS.md` has **no** rule on `[SyncMethod]`,
> UI Harmony patches, or deliberate client-local state, and a layer like this
> **violates the Divergence gate as written**. It needs a ratified carve-out, or every
> review re-litigates it. Not yet decided — do not treat the assessment above as
> permission.
