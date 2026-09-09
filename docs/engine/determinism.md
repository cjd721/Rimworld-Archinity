# Determinism, ticks and `Rand`

What Multiplayer actually synchronizes, why `Rand` on a synced tick is safe, and
what the real hazard class is. This is the evidence under the **Divergence gate**
in `CODING_STANDARDS.md` — the gate is the rule, this file is why it is the rule.

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

## Why threads are the one thing that bars a mod

A background thread runs outside `DoSingleTick` entirely. It cannot be ordered
relative to the tick, so any `Rand` it consumes or sim state it writes is
non-deterministic by construction — and there is no XML or settings fix, because the
scheduling is not data. That is the whole content of the bar: **a world simulation
only bars if it runs off the synced tick, so in practice the bar reduces to *does it
create threads*.** A `WorldComponent` grinding through heavy world state inside
`WorldComponentTick` is deterministic; disliking it is a design objection about
shadow worlds, not a safety one.

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

## What is not synced for free

Nothing is covered by default. For the faction-mutation case specifically —
`WorldObject.SetFaction`, `FactionDef` mutation, and which operations pull `Rand`
and must therefore sit inside the same synced command — see
`docs/engine/factions-and-worldgen.md` § *Multiplayer*.

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
