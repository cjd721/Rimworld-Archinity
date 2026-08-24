# Recon — the tick loop and the storyteller

**Date:** 2026-08-24. **Method:** `ilspycmd` against
`RimWorldWin64_Data/Managed/Assembly-CSharp.dll` (1.6). Types decompiled:
`RimWorld.Storyteller`, `RimWorld.StorytellerUtility`, `Verse.TickManager`.

Everything marked **VERIFIED** was read directly out of the decompile and is quoted.
**INFERRED** means reasoned from verified code but not itself observed.

> This document exists because a subagent tasked with it died on an auth error. The
> work was redone in the main thread and is narrower than the original brief — it
> answers the architecture questions and does not enumerate every incident worker.

---

## 1. The tick order — VERIFIED

`Verse.TickManager.DoSingleTick()` executes in this order:

```
maps[i].MapPreTick();          // ~line 362
Find.World.WorldTick();        // ~line 394
Find.Storyteller.StorytellerTick();  // ~line 418
maps[j].MapPostTick();         // ~line 450
```

**The storyteller runs inside the game tick**, between the world pass and the map
post-pass. This single fact is the basis of the multiplayer conclusion in §7.

Tick rate is driven by `TickRateMultiplier` switching on `TimeSpeed`
(`Paused / Normal / Fast / Superfast / Ultrafast`), with
`return 1f / (60f * TickRateMultiplier)` for seconds-per-tick — i.e. **60 ticks per
second at 1x**, and speed multipliers run more ticks per real second rather than
changing what a tick means.

## 2. The storyteller's cadence — VERIFIED

```csharp
public void StorytellerTick()
{
    incidentQueue.IncidentQueueTick();
    if (Find.TickManager.TicksGame % 1000 != 0 || !DebugSettings.enableStoryteller)
    {
        return;
    }
    foreach (FiringIncident item in MakeIncidentsForInterval())
    {
        TryFire(item);
    }
}
```

Called every tick; does work every **1000 ticks**. At 60,000 ticks per game day that
is **60 storyteller evaluations per day**, roughly one per 16 real seconds at 1x.

Note `incidentQueue.IncidentQueueTick()` runs *outside* the interval gate — queued
incidents are checked every tick.

## 3. It is N independent generators, not one roll — VERIFIED

```csharp
public IEnumerable<FiringIncident> MakeIncidentsForInterval()
{
    List<IIncidentTarget> targets = AllIncidentTargets;
    for (int j = 0; j < storytellerComps.Count; j++)
    {
        foreach (FiringIncident item in MakeIncidentsForInterval(storytellerComps[j], targets))
        {
            yield return item;
        }
    }
    // ... then quests, see §4
}
```

Each `StorytellerComp` is asked independently every interval and yields zero or more
candidates. **There is no central roll to compete for.** A `StorytellerDef`
(Cassandra / Randy / Phoebe) is essentially a tuned list of comps.

**Design consequence:** adding a comp is additive. It does not displace vanilla
generators. Contrast Rim War, which built a rival system and then had to blanket-block
vanilla `RaidEnemy`, `RaidFriendly` and `TraderCaravanArrival` to make room for it
(`RimWarMod.cs:984`, `restrictEvents` default on — see `recon-rimwar.md`).

### The vanilla comp roster — VERIFIED (via `ilspycmd -l c`)

`_CategoryIndividualMTBByBiome` · `_CategoryMTB` · `_ClassicIntro` ·
`_DeepDrillInfestation` · `_Disease` · `_DissolutionTriggered` · **`_FactionInteraction`** ·
`_GauranlenPodSpawn` · `_ImportantQuest` · `_MechanitorComplexQuest` ·
`_MonolithMigration` · `_NoxiousHaze` · `_OnOffCycle` · `_RandomEpicQuest` ·
`_RandomMain` · `_RandomQuest` · `_RefiringUniqueQuest` · `_ShipChunkDrop` ·
`_SingleMTB` · `_SingleOnceFixed` · `_ThreatsGenerator` · `_Triggered` · `_WorkSite`

Each has a paired `StorytellerCompProperties_*`.

Two are worth naming for our purposes: **`StorytellerComp_Triggered`** and
**`StorytellerComp_SingleOnceFixed`** fire on a *condition* or at a *fixed moment*
rather than on a timer. Vanilla already ships the "when X holds, do Y" firing model —
our deterministic-consequence design is a native pattern, not a workaround.

## 4. Ongoing quests are also incident generators — VERIFIED

The same `MakeIncidentsForInterval()` continues:

```csharp
List<Quest> quests = Find.QuestManager.QuestsListForReading;
for (int j = 0; j < quests.Count; j++)
{
    if (quests[j].State != QuestState.Ongoing) continue;
    List<QuestPart> parts = quests[j].PartsListForReading;
    for (int k = 0; k < parts.Count; k++)
    {
        if (!(parts[k] is IIncidentMakerQuestPart incidentMakerQuestPart)
            || ((QuestPartActivable)parts[k]).State != QuestPartState.Enabled) continue;
        foreach (FiringIncident item2 in incidentMakerQuestPart.MakeIntervalIncidents())
        { ... yield return item2; }
    }
}
```

**An active quest can generate incidents on the same 1000-tick interval for as long as
it runs.** This is a second extension point and it was not previously known to the
project. Directly relevant to the Chronicle and to faction demands: a demand quest can
apply continuing pressure while live, rather than being an inert entry in a list.

## 5. The world is a first-class incident target — VERIFIED

```csharp
tmpAllIncidentTargets.Clear();
... tmpAllIncidentTargets.Add(maps[i]);
... tmpAllIncidentTargets.Add(caravans[j]);
tmpAllIncidentTargets.Add(Find.World);
return tmpAllIncidentTargets;
```

Targets are **every map, every caravan, and the world itself.** An event that happens
"out there" with no map involved is native behaviour.

### Per-comp target filtering is pure props — VERIFIED

`MakeIncidentsForInterval(StorytellerComp comp, List<IIncidentTarget> targets)` gates on:

- `comp.props.minDaysPassed` vs `GenDate.DaysPassedSinceSettleFloat` — early return
- `comp.props.allowedTargetTags` / `comp.props.disallowedTargetTags` vs the target's
  `IncidentTargetTags()`

So a custom comp can declare *world only, not before day N* in XML, with no code.

### Self-veto — VERIFIED

```csharp
public bool TryFire(FiringIncident fi, bool queued = false)
{
    if (fi.def.Worker.CanFireNow(fi.parms) && fi.def.Worker.TryExecute(fi.parms))
    {
        fi.parms.target.StoryState.Notify_IncidentFired(fi);
        lastIncidentTick = GenTicks.TicksGame;
        return true;
    }
    return false;
}
```

The incident's own worker decides whether its preconditions hold. `StoryState` tracks
last-fire per target.

## 6. Threat points are computed on demand, not cached — VERIFIED

```csharp
public static IncidentParms DefaultParmsNow(IncidentCategoryDef incCat, IIncidentTarget target)
{
    IncidentParms incidentParms = new IncidentParms();
    incidentParms.target = target;
    if (incCat.needsParmsPoints)
        incidentParms.points = DefaultThreatPointsNow(target);
    return incidentParms;
}
```

A **fresh** `IncidentParms` per call; `DefaultThreatPointsNow` reads
`target.PlayerWealthForStoryteller` through `PointsPerWealthCurve` and iterates
`PlayerPawnsForStoryteller` at that moment. **There is no maintained snapshot object
that the storyteller reads.** It is pull, not push.

Corollary, and it explains a note already in `CLAUDE.md`:

```csharp
public static float GetProgressScore(IIncidentTarget target)
{
    int num = 0;
    foreach (Pawn item in target.PlayerPawnsForStoryteller)
        if (!item.IsQuestLodger() && item.IsFreeColonist) num++;
    return (float)num * 1f + target.PlayerWealthForStoryteller * 0.0001f;
}
```

Progress score is **free colonists + wealth × 0.0001**, nothing else. That is the
whole formula, and it is why `rootMinProgressScore` ignores research entirely.

## 7. Multiplayer — the decisive conclusion

**VERIFIED:** `Find.Storyteller.StorytellerTick()` is called from inside
`TickManager.DoSingleTick()`.

**INFERRED (sound, not confirmed):** the Multiplayer mod's mechanism is synchronising
the tick loop, so both clients execute the same `DoSingleTick` against the same RNG
state. Therefore **randomness consumed inside a `StorytellerComp` is deterministic
across clients by construction** — in exactly the way randomness in a settings window,
a UI tab, or a worker thread is not.

This is the difference between our proposed design and every mod assessed on
2026-08-24. Rim War desyncs because it rolls `Rand` on the GUI thread and on background
threads; FTV desyncs because a settings window marks a static cache dirty which gates a
`Rand`-indexed decision. A storyteller comp sidesteps the entire class of problem by
sitting in the one place where randomness is already safe.

**Not confirmed and worth confirming before committing:** whether the Multiplayer mod
does anything storyteller-specific. The mod folder did not resolve by package ID
(`rwmt.multiplayer`) during this pass and its assembly was not located. This is a
low-risk gap — MP would not function at all if it did not sync the tick loop — but it
is an inference, not an observation.

## 8. Verdict

Extending the storyteller with a custom comp, backed by a small deterministic ledger in
a `WorldComponent`, is **with RimWorld's grain rather than against it**. Specifically:

- The comp list is a designed extension point; adding to it is additive.
- The world is already a legal incident target.
- Target filtering and ramp-in are pure XML props.
- Randomness is safe because of where it sits.
- No Harmony patches are required for any of the above.

Known limitations, stated honestly:

- The 1000-tick interval is the floor for reactivity. Anything needing finer granularity
  than ~16 real seconds does not belong in a comp.
- `StorytellerComp` and `StorytellerCompProperties` subclasses are C#. This is not a
  pure-XML route — but per `CLAUDE.md` the constraint is desync, not C#.
- Incidents that need genuinely new behaviour need an `IncidentWorker` subclass. Reuse
  vanilla workers wherever one already does the job.
- Nothing here creates NPC↔NPC relations *machinery* — that is verified to already work
  and to be uncontested by vanilla; see `recon-vanilla-faction-baseline.md`.
