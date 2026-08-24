# Recon: Faction / World-Simulation Mod Status

Sweep of nine workshop mods under
`/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/`.
Everything below comes from the shipped mod folders on this machine — About.xml,
README/Changelog/LICENSE, folder layout, shipped C# source, and `ilspycmd`
decompiles of the closed-source assemblies. No internet, no wiki, no memory.

Decompiles live in the session scratchpad at
`.../scratchpad/dec/{rimwar,ftv,fc}` (temporary — regenerate with `ilspycmd` if needed).

Anything not directly observed is tagged **INFERRED**.

---

## 1. Per-mod table

| Mod | ID | Author | supportedVersions | 1.6 real? | Declared deps | Licence | Source shipped |
|---|---|---|---|---|---|---|---|
| Rim War | 2222935097 | Torann | 1.2–1.6 | Yes — `v1.6/` with own recompiled `RimWar.dll` (297,984 B, differs from 1.5's 299,520 B) | Harmony (1.6 drops the HugsLib dep that 1.2–1.5 declared) | MIT (2019 TorannD) | No |
| Faction Territories and Vassalage | 3626725895 | jaeger972 | 1.6 only | Yes — no version folders at all, root-level `Assemblies/Defs` | Map Mode Framework (hard); `loadAfter` MMF + `Torann.RimWar` | **None** | No |
| [SR]Factional War (fork) | 3423264477 | llunak, Shadowrabbit | 1.2–1.6 | Yes — 1.6 maps to root `/` via `loadFolders.xml`; root DLL 66,048 B is the newest build | Harmony | Yes (11.8 KB, GPL-family) | Yes, full `Source/` |
| Sensible Factions | 3531306011 | Roundhead | 1.6 only | Yes — single unversioned `Assemblies/` | Harmony | **None** | Yes, full `Source/` |
| Map Mode Framework | 3296654393 | カタストロフ/NozoMe | 1.5, 1.6 | Yes — `1.6/` with own DLL + `PlanetLayerPatches.xml` | Harmony | MIT (2024 nozomemu) | Yes, plus a live `.git` |
| World Tech Level | 3414187030 | m00nl1ght | 1.5, 1.6 | Yes — `1.6/` with its own LunarFramework component set | none declared; ships its own Harmony + LunarFramework under `Lunar/` | CC BY-NC-SA 4.0 | No (but full README + Changelog) |
| Lemmy Progression for WTL | 3548896697 | lemmy101 | 1.6 only | Yes — but see §5, this is v0.0.1 | Harmony, World Tech Level, **VFE Tribals**, **Medieval Overhaul** (all hard deps) | **None** | Yes, plus a live `.git` |
| Vanilla Outposts Expanded | 2688941031 | legodude17, Oskar Potocki | 1.4, 1.5, 1.6 | Yes, **with feature loss** — see below | Harmony, Vanilla Expanded Framework | **None** | Yes (1.3 tree) |
| Faction Customizer | 3336572602 | Azravos | 1.3–1.6 | Yes — `1.6/` has the largest DLL of the set (49,664 B vs 37,888 B for 1.5), so real new 1.6 work | Harmony (bundles its own `0ColourPicker1.6.dll`) | **None** | No |

### Author statements, verbatim

**Rim War** — the version string is in the description itself, and it has never reached 1.0:

> "Version 0.9.9.8"

Rim War's own English keys contain a defensive-disable admission:

> "There are no traders defined for this faction - trading is administratively disabled to prevent errors."
> — `Languages/English/Keyed/RW_English.xml`, `RW_CaravanMeeting_FactionIncapableOfTrade`

and a threading toggle that concedes it conflicts with other mods:

> "Toggles threading performed by RimWar. Disable this option if other threading functions are used."
> — same file, `RW_threadingEnabledInfo`

**Faction Customizer** — the 1.6 features are explicitly flagged in the settings UI:

> "Active game features (experimental, use with caution)"
> — decompiled `FactionCustomizer/ModSettings.cs:70`

and are all defaulted **off** (`settlementManipulationEnabledWhileGameIsRunning`,
`createNewFactionEnabledWhileGameIsRunning`, `relocateEnabledWhileGameIsRunning`
all `= false`). The About.xml also concedes a workaround-by-parallel-UI:

> "I had to create my own faction dialog to avoid some conflicts with other mods. This means that to access the faction customize menu from now on, you need to click the "FC" icon letters that should be down to the right of your screen"

**Lemmy Progression** — `About/Version.txt` contains exactly:

> `0.0.1`

and the shipped git history is candid:

> `62d4f7d Major refactor - still not working entirely`
> `87be310 First version looking fairly solid`
> `7f8f9a0 Fixed pawnGroup exception so raids work properly`
> `96bb576 Makes factiondefs unique when upgrading to avoid contamination of other factions sharing the same def`

Plus an unimplemented feature left as a log line:

> `// This would require a custom GameComponent to track and execute delayed upgrades`
> `// For now, log the intent`
> — `1.6/Source/Systems/FactionUpgradeManager.cs:251-252`

The whole repo is dated **2025-08-14** — a single day of commits ("First upload" twice).

**Faction Territories and Vassalage** — the reverse of an admission: the About
description drastically *undersells* what ships.

> "Adds a  mode that draws territory regions around settlements for each faction."

The actual 267 KB assembly ships autonomous **invasions**, **AI settlement
construction**, **vassalage**, **vassal outposts**, **vassal road progress**,
and a **caravan incident weighting system** — six `GameComponent`s and a
`WorldComponent`, four Def files (`Regions.xml`, `Invasions.xml`,
`VassalOutposts.xml`, `CaravanIncidents.xml`), 40+ settings, all defaulted on
(`enableInvasions = true`, `enableSettlementConstruction = true`,
`enablePersistentHostileTerritoryMapIncursions = true`, …). No licence, no
README, no changelog, no source. A settings field named
`caravanIncidentLegacyMigrated` shows the config format has already broken once.

**World Tech Level** — the only mod in the set that makes explicit
save-safety guarantees, and it backs them with an architectural choice:

> "Can I safely add this mod to an existing save? - Yes."
> "Can I safely remove this mod from an existing save? - Yes."
> "World Tech Level does not modify or remove any defs. This means it is fully save-compatible, less likely to conflict with other mods…"
> "No incompatibilities have been reported so far."
> — `README.md`

**Map Mode Framework** — no beta language; a rendering/UI framework with a
stated performance goal:

> "Only the `WorldLayer_MapMode` corresponding to the current `MapMode` is rendered and can regenerate, optimizing performance especially on high coverage worlds with lots of tiles."

**Vanilla Outposts Expanded** — no beta language in About, but the
`loadFolders.xml` records the 1.6 regression in a comment:

```xml
<v1.6>
  <li>/</li>
  <li>1.6</li>

  <!--<li IfModActive="oskarpotocki.vfe.mechanoid">1.6/Factory</li>-->
</v1.6>
```

The VFE-Mechanoid Factory outpost is commented out on 1.6, and the `Fishing`
submodule that exists in `1.3/`, `1.4/` and `1.5/` **has no `1.6/` counterpart
at all** — the folder was not shipped. Two content submodules silently lost in
the 1.6 port.

**Sensible Factions** and **[SR]Factional War** ship no beta/WIP statements.
Sensible Factions does carry a `Version_2_Legacy/Legacy_Redistributor.txt` — an
entire prior implementation kept as a `.txt` next to the live `Version_3/`
folder, i.e. the mod has been rewritten once already.

---

## 2. Dependency graph

Frameworks are boxed; content mods hang off them.

```
                        ┌───────────────────────┐
                        │ brrainz.harmony       │  (external, universal)
                        └───────────┬───────────┘
                                    │ declared by 7 of 9
   ┌────────────────────────────────┼──────────────────────────────┐
   │                                │                              │
┌──┴──────────────────────┐   ┌─────┴────────────────────┐   ┌─────┴──────────────┐
│ NozoMe.MapModeFramework │   │ OskarPotocki.VFE.Core    │   │ (LunarFramework)   │
│  FRAMEWORK (1.5,1.6)    │   │  (VEF — external)        │   │ bundled INSIDE WTL │
└──┬──────────────────────┘   └─────┬────────────────────┘   └─────┬──────────────┘
   │ hard dep                       │ hard dep                     │ internal
┌──┴──────────────────────────┐  ┌──┴────────────────────┐   ┌─────┴──────────────┐
│ jaeger972.factionterritories│  │ vanillaexpanded.      │   │ m00nl1ght.         │
│ (FTV)                       │  │ outposts (VOE)        │   │ WorldTechLevel     │
│ loadAfter: MMF, Torann.RimWar  └───────────────────────┘   └─────┬──────────────┘
└──┬──────────────────────────┘                                    │ hard dep
   │ SOFT (reflection-probed, not declared)                        │
┌──┴──────────────────────┐                              ┌─────────┴──────────────┐
│ Torann.RimWar           │                              │ LemmyMods.LemProgression│
│ loadAfter: Harmony,     │                              │ hard deps also on:      │
│ Core, Royalty           │                              │  oskarpotocki.vfe.tribals│
└─────────────────────────┘                              │  dankpyon.medieval.overhaul│
                                                          │ loadAfter also ferny.worldbuilder│
Standalone (Harmony only, no cross-links):                └─────────────────────────┘
  Boots.SensibleFactions
  SR.ModRimworld.FactionalWarContinued
  azravos.factioncustomizer  (bundles its own 0ColourPicker1.6.dll)
```

**Framework vs content**

- Frameworks: `NozoMe.MapModeFramework`, VEF (external), LunarFramework
  (vendored inside World Tech Level, not a separate mod), Harmony.
- World Tech Level is a *hybrid*: a content-filter mod that is also depended on
  as a platform by Lemmy Progression.
- Content: Rim War, FTV, Factional War, Sensible Factions, VOE, Faction
  Customizer, Lemmy Progression.

**Load order implied by declarations**

```
Harmony
  → Ludeon.RimWorld + DLCs
  → OskarPotocki.VanillaFactionsExpanded.Core  (VOE loadAfter)
  → NozoMe.MapModeFramework                    (FTV loadAfter)
  → m00nl1ght.WorldTechLevel                   (Lemmy loadAfter)
  → oskarpotocki.vfe.tribals                   (Lemmy loadAfter)
  → ferny.worldbuilder                         (Lemmy loadAfter)
  → dankpyon.medieval.overhaul                 (Lemmy loadAfter)
  → Torann.RimWar                              (FTV loadAfter)
  → jaeger972.factionterritories
  → LemmyMods.LemProgression
  (Sensible Factions, Factional War, Faction Customizer: unconstrained)
```

**Undeclared coupling worth flagging:** FTV does *not* declare Rim War as a
dependency but reflection-probes for it at runtime —
`AccessTools.TypeByName("RimWar.Planet.RimWarSettlementComp")` in
`FactionTerritoriesUtility.EnsureRimWarCache()`, gated behind a
`RimWarInstalled` property, with a 15,000-tick TTL cache and a
`addRimWarSettlementScanRangePercent` setting. FTV also reflection-probes
`VehicleMapFramework.VehicleMapUtility` in `Compatibility.cs`. Both probes are
wrapped in bare `catch { return false; }`.

**Incompatibilities declared:** World Tech Level lists five —
`ogam.rimedieval`, `sickboywi.medieval.vanilla`, `mlie.removeindustrialstuff`,
`mlie.removemedievalstuff`, `mlie.removespacerstuff`. It is the only mod in the
set that declares any.

---

## 3. Multiplayer compatibility — factual scan

Grep across all nine folders (source, XML, and binaries) for `multiplayer`,
`zetrith`, `rwmt`, `SyncMethod`, `SyncWorker`, `SyncField`:

| Mod | Hits |
|---|---|
| Rim War | **none** |
| FTV | **none** |
| Factional War | **none** |
| Sensible Factions | **none** |
| Map Mode Framework | only inside the vendored `0Harmony.dll` / `.pdb` (binary noise, not a Multiplayer reference) |
| World Tech Level | only inside the vendored `HarmonyLib.dll` (same, binary noise) |
| Lemmy Progression | **none** |
| Vanilla Outposts Expanded | **none** |
| Faction Customizer | **none** |

**Zero of the nine reference the Multiplayer mod, Zetrith, `rwmt`, or any sync
attribute.** That is *not* evidence of incompatibility — a pure-def or
deterministic-code mod needs no MP awareness whatsoever and works fine. It only
means none of them were written with MP in mind and none ship explicit support.

What *is* evidence, from the decompiles:

**Rim War — concrete desync mechanisms observed (not inferred):**

1. `RimWar.RocketTools/RocketTasker.cs:64` — `thread = new Thread(threadStart);`
   Rim War runs its own raw OS threads.
2. `RimWar.Planet/WorldComponent_PowerTracker.WorldComponentTick()` dispatches
   the faction simulation onto that thread pool when a **mod setting** is on:
   ```csharp
   if (Settings.Instance.threadingEnabled) {
       tasker.Register(delegate { UpdateFactions(); ... });
   } else {
       UpdateFactions();
   }
   ```
   The setting is client-local. Two players with different values run the world
   sim on different schedules.
3. `UpdateFactions()` consumes randomness: it ends in
   `UpdateFactionSettlements(GenCollection.RandomElement<RimWarData>(RimWarData))`
   — i.e. **`Rand` is pulled off the main thread**. RimWorld's `Rand` state is
   not thread-safe and Multiplayer's determinism depends entirely on both
   clients pulling the same numbers in the same order.
4. `WorldComponentTick` itself calls `Rand.Range(...)` directly to schedule
   `nextEvaluationTick`, and 101 `Rand.*` call sites exist across the assembly
   (71 `Rand.Range`, 13 `Rand.Value`, 8 `Rand.Chance`) with only **one**
   `Rand.PushState`/`PopState` pair.

**INFERRED** but with high confidence from the above: Rim War will desync a
Multiplayer session. Points 1–3 are exactly the pattern `CLAUDE.md` warns about
for `Archinity.Altar`.

**FTV — concrete MP hazard observed:** `VassaliseComponent.GameComponentTick()`
calls `Find.TickManager.Pause()` and reads/writes `CurTimeSpeed` from inside a
tick, to force a decision letter open. In Multiplayer, time control is a synced
global; a client-side pause driven by a local tick is at minimum a
desynchronised game speed. The same method swallows every exception in a bare
`catch { }`, so failures are silent. FTV has 20 `Rand.*` sites but does bracket
5 of them in `Rand.PushState`/`PopState` — better hygiene than Rim War, still
not sync-aware. Six `GameComponent`s and a `WorldComponent` all tick
autonomously.

**Sensible Factions — the safest profile by construction:** every class is
`internal static` utility code, there is no `GameComponent` or `WorldComponent`
anywhere, and the single Harmony patch is a **postfix on
`WorldGenerator.GenerateWorld`**. It runs once, at world creation, before any
save exists. `IExposable` appears only on the settings object.

**World Tech Level** is filter-only and states it modifies no defs; its work is
in generation-time filters. **INFERRED**: low MP risk, but it does hook
generation paths, so both clients must have identical mod settings (which
`CLAUDE.md` already mandates).

**Map Mode Framework** is rendering/UI only — WorldLayers, materials, caching,
an async `TaskHandler` for regeneration. **INFERRED**: presentation-layer work
does not enter the simulation, so MP-neutral, though its async regeneration is
a rendering thread, not a sim thread.

**Faction Customizer** mutates faction relations, ideoligions, colours,
settlement positions, and (on 1.6) creates/deletes settlements and factions —
all from dialog buttons. **INFERRED**: any such click is an unsynced local
mutation of world state under MP unless the Multiplayer mod happens to catch it.

---

## 4. Why is this genre perpetually beta?

Grounded answer, each claim tied to something observed in these folders.

### 4.1 RimWorld's world map has no ownership model, so every mod builds its own — and then has to repair it on every load

Vanilla has settlements on tiles and bilateral `FactionRelation` records. It has
no concept of territory, borders, fronts, supply, or a faction's total power.
Every mod here invents one:

- Rim War invents `RimWarData` (`IExposable`), `RimWarSettlementComp`,
  `RimWarCaravanComp`, `CapitolBuilding`, `WarObject`,
  `WarObject_PathFollower`, `CaravanTargetData`, `LaunchedWarObject` — a
  parallel world-state graph across 25 files with `Scribe_` calls.
- FTV invents a Voronoi cell texture (1024×512, 256 sites, seeded from the
  world seed string) plus a `TerritoryOwnershipCache` with its own hash-based
  invalidation.

Because that state is invented, nothing in vanilla maintains it, and it drifts.
Rim War's response is the tell — on every save load
(`Scribe.mode == LoadingVars`) it runs:

```csharp
RimWar_DebugToolsPlanet.ValidateAndResetSettlements();
WorldUtility.ValidateFactions(forced: true);
```

and `ValidateFactions` reaches into vanilla's **private** relations list by
reflection and rebuilds missing entries:

```csharp
List<FactionRelation> value = Traverse.Create(list[i]).Field("relations")
                                      .GetValue<List<FactionRelation>>();
if (value == null || value.Count <= 0) { ... CreateFactionRelation(...); }
```

A mod that must run a repair pass over private engine state on every single load
is a mod whose author knows the state does not survive contact with the game.
That is the structural reason these things sit at 0.9.9.8 forever: not a missing
feature, an invariant that cannot be closed.

### 4.2 Faction relations are bilateral-only, so alliances and wars have to be simulated on top of a data model that cannot express them

`FactionRelation` is a pair. There is no coalition, no war side, no third-party
obligation. Rim War's UI text shows the author hand-rolling the semantics in
prose because the data model cannot carry them:

> "War may be ended with a declaration of peace, however, this option will only become available if the NPC faction is willing to engage in diplomacy."
> "A formal alliance will be ended by any hostile action that reduces relations with this faction below Ally"

Those are rules enforced by bespoke code paths, each of which is a place where
two mods disagree. FTV independently invents *vassalage* — a third relation kind
— with its own points component, road-progress component, outposts and letters.
Two mods, two incompatible ownership models, no shared vocabulary. **INFERRED**:
this is why the genre never converges on a framework; Map Mode Framework
succeeded precisely because it only standardises *rendering*, which is the one
layer with no semantics to disagree about.

### 4.3 The storyteller owns incident pacing, so any autonomous world sim is fighting the game for control of the same channel

Rim War's own setting text states the conflict outright:

> "Restricts Rim War actions from occurring randomly. When disabled, the storyteller will continue to generate random raids, caravans, and any other events associated with Rim War global objects."

So the mod ships a toggle whose job is to decide *who* gets to fire raids. FTV
does the same battle from the other side, with six Harmony patches whose names
are the whole story:

```
Patch_FactionManager_RandomEnemyFaction_ForceAmbushFaction
Patch_FactionManager_RandomRaidableEnemyFaction_ForceAmbushFaction
Patch_FactionManager_TryGetRandomNonColonyHumanlikeFaction_ForceAmbushFaction
Patch_AmbushEnemyFaction_CanFireNowSub_ForceFaction
Patch_AmbushEnemyFaction_GeneratePawns_ForceFaction
Patch_AmbushEnemyFaction_TryExecuteWorker_ForceFaction
```

plus a `ForcedAmbushFactionScope` — a scoped global override, meaning FTV
temporarily lies to `FactionManager` about which factions exist while an incident
resolves. Two mods both doing this to the same static manager is not
composable, and no amount of testing by either author finds it.

### 4.4 Per-tick world simulation is a performance problem serious enough that authors reach for threads — which then makes the mod untestable and undeterministic

Rim War does not merely tick; it bundles a whole miniature scheduler
(`RimWar.RocketTools/RocketTasker`) and a `RimWar.RocketMan` namespace
(`CachedDict`, `CachedUnit`, `RocketShip`) — caching infrastructure named after
the RocketMan performance mod. It caps itself at 4 concurrent tasks, has a 15 ms
`Await` budget, and will `Thread.Interrupt()` its own work with
`Log.Warning("RIMWAR: interrupted excution.")` when it overruns.

Interrupting your own simulation mid-flight to protect frame rate means the
world state after tick N is not a function of the world state at tick N−1 — it
depends on wall-clock timing. That is unreproducible by construction. A bug
report that cannot be reproduced cannot be closed, and a mod whose bugs cannot
be closed does not ship a 1.0. This is, mechanically, why Rim War is on
0.9.9.8 seven years in.

Note also `WorldComponentTick` runs `WorldUtility.CopyData()` **every single
tick** before doing anything else — a full data copy at 60 Hz, which is where
the threading pressure came from in the first place.

### 4.5 The combinatorial testing surface is unbounded, and the code shows authors have given up on covering it

- FTV ships **40+ persisted settings**, most of them behavioural
  (`enableInvasions`, `enableSettlementConstruction`, four independent
  incursion toggles, interval + randomisation-percent pairs). The cross-product
  is not testable by one person.
- Rim War's behaviour table is per-faction-def and the def file itself lists ten
  behaviour enums (`Expansionist, Cautious, Merchant, Aggressive, Warmonger,
  Random, Player, Vassal, Excluded, Undefined`) against every modded faction in
  the load order.
- Lemmy Progression declares **four** hard dependencies (WTL, VFE Tribals,
  Medieval Overhaul, Harmony) and integrates by reflection against a fifth
  (Worldbuilder). Its WTL integration is a string-name search through another
  mod's assembly:
  ```csharp
  string[] possibleTypeNames = { "WorldTechLevel.TechLevelUtility",
                                 "TechLevelUtility",
                                 "WorldTechLevel.Utilities.TechLevelUtility" };
  ```
  followed by a fallback that scans *every type in the assembly* for a name
  containing `TechLevelUtility`. Three guesses plus a brute-force scan is what
  integration looks like when the surface you depend on has no contract. Every
  WTL refactor breaks it silently — the failure path is `Log.Warning`, not an
  error, so the mod loads and simply does nothing.
- The graceful-degradation pattern is everywhere and it *hides* breakage rather
  than surfacing it: FTV's `Compatibility.cs` and `EnsureRimWarCache()` both
  end in bare `catch { return false; }`; `VassaliseComponent.GameComponentTick`
  ends in `catch { }`. A mod that silently no-ops when its assumptions break
  produces bug reports of the form "it just doesn't do anything", which are the
  hardest kind to act on.

### 4.6 Arbitrary world state has to survive save/load *and* mod-list churn over a months-long game

Every autonomous world sim here persists custom `WorldObject`s into the save:
Rim War writes `RW_Warband_Caravan`, `RW_CapitolBuilding`, `RW_Site`; FTV writes
`FT_BaseInvasion`, `FT_SettlementConstruction`, `FT_VassalOutpost`, with 19
`Scribe_` calls in `Invasion.cs` alone. Per `CLAUDE.md`, unresolvable
cross-references are omitted rather than nulled — so a save that contains these
objects and then loses the mod does not error, it quietly loses structure. The
Lemmy commit `96bb576 Makes factiondefs unique when upgrading to avoid
contamination of other factions sharing the same def` is the same class of
problem discovered the hard way: mutating a shared def at runtime leaks into
every faction pointing at it, and the fix is to fork defs at runtime — which is
itself a def-database mutation mid-save.

### 4.7 The version treadmill resets the work before it finishes

Observable in the folder layout, not inferred:

- VOE's 1.6 port **dropped** the Fishing submodule (no `1.6/Fishing` folder
  exists although 1.3/1.4/1.5 all have one) and **commented out** the Factory
  submodule in `loadFolders.xml`. Two features lost to a version bump, from the
  most professional team in the set.
- Map Mode Framework's git history: substantive feature work in Aug 2024, then
  a single commit `7fcbf7b Update for version 1.6` on 2025-07-21 and nothing
  since. Eleven months of gap, and the 1.6 work is the port, not features.
- Rim War carries five parallel version trees (v1.2 through v1.6), and
  `v1.5/Defs` and `v1.6/Defs` are **byte-identical** — the 1.6 release is a
  recompile. The maintenance budget goes entirely to staying loadable.
- Factional War carries 1.2/1.3/1.4/1.5 folders plus a root tree for 1.6; its
  root `Defs/` is identical to `1.5/Defs`. Also a recompile, and it is already
  a fork of a fork (Shadowrabbit's original → a 1.5 continuation → llunak's
  fork; the About names both lineages).

**Synthesis.** The genre is perpetually beta because the *correct* version of
these mods does not exist inside RimWorld's architecture. Vanilla gives you
tile-and-bilateral-relation, single-threaded, storyteller-paced, save-everything
semantics. An autonomous world-map faction war needs territory, multilateral
alliances, its own pacing authority, and enough CPU headroom to run a strategy
layer at 60 Hz — four things the engine does not offer. Each mod therefore
builds a shadow world model, and then spends the rest of its life on the two
costs that shadow model imposes: repairing its own invariants on every load
(§4.1), and fighting whatever other mod built a *different* shadow model over
the same static managers (§4.2, §4.3). Threading is added to make it fast
enough (§4.4), which destroys reproducibility and therefore the ability to close
bugs at all. Meanwhile the test surface grows combinatorially with settings and
dependencies (§4.5) and the whole thing gets reset every twelve months by a
RimWorld version bump (§4.7). "1.0" would mean "the invariants hold" — and
nobody in this folder can assert that, so the version number stops at 0.9.9.8
and the mod ships anyway.

---

## 5. Risk ranking for a months-long two-player Multiplayer save

Weighting save-corruption and desync far above feature loss, per the brief.

### Safest → most dangerous

**1. Sensible Factions** (3531306011) — *Safest.*
Runs exactly once, as a postfix on `WorldGenerator.GenerateWorld`, before a save
exists. No `GameComponent`, no `WorldComponent`, no tick, no persisted world
state, no runtime def mutation. Whatever it does is baked into the world at
creation. Both clients must have identical mod settings (its settings drive
faction/biome weights), which `CLAUDE.md` already requires. Risk if it
misbehaves: an oddly-distributed world, discovered at day 1.

**2. Map Mode Framework** (3296654393) — *Very safe.*
Rendering and UI only: WorldLayers, materials, caches, map-mode switching. Its
only Def work is a `PatchOperationAdd` appending four draw layers to
`PlanetLayerDef[defName="Surface"]`. No simulation state, nothing scribed into
the save beyond MMF's own mode selection. MIT, source shipped, live git, real
1.6 commit. Its async `TaskHandler` is a *render* thread, not a sim thread.
Note: it hard-depends on nothing but Harmony, so it can be removed later
without stripping references off other defs — *except* that removing it breaks
FTV, which hard-depends on it.

**3. World Tech Level** (3414187030) — *Safe, and the best-engineered mod here.*
Explicit author guarantee of both add-to-save and remove-from-save safety,
backed by the design choice of not modifying defs. Detailed README, real
changelog through v1.1.6, CC BY-NC-SA licence, vendored LunarFramework so it
does not fight over a shared framework version. Declares five incompatibilities
— the only mod that bothers. Risk is confined to filters producing surprising
content gaps, which is exactly the Archinity progression use case, and its
"Overrides" settings tab exists to fix them.

**4. Vanilla Outposts Expanded** (2688941031) — *Low risk, known feature loss.*
Mature, VE-team, four version trees, source shipped for the 1.3 tree. It does
persist custom `WorldObject`s (outposts) into the save, so it is not removable
mid-save without losing structure. The 1.6 port dropped Fishing outposts
entirely and commented out Factory outposts — plan around that, don't plan on
them returning. Outposts are player-initiated (form a caravan, create a camp),
so the state it writes is state the player caused, not autonomous drift. No
licence file.

**5. [SR]Factional War (fork)** (3423264477) — *Moderate.*
Full source shipped, real licence, eleven translations, and its scope is
honestly bounded: four incidents in which "you are not the protagonist." It is
incident-scoped rather than a continuous world sim — it spawns two hostile
factions onto a map and lets them fight, using Lords, Duties and JobGivers,
which are already-synced RimWorld primitives. Downsides: it is a fork of a fork
with no changelog, its 1.6 tree is a recompile of the 1.5 defs, and its Harmony
instance id is a leftover from a Save Our Ships 2 compatibility fix
(`com.shadowrabbit.factionalwar.saveourships2.filterspacemap`) that no longer
describes what it does. **INFERRED**: map-local combat AI is the least
MP-hostile thing in this list after the read-only mods, because it runs inside
the existing synced job/lord system.

**6. Faction Customizer** (3336572602) — *Moderate, entirely under player control.*
Everything it does is a button press in a custom dialog. Nothing ticks. The
danger is that the buttons on 1.6 mutate world topology — create/delete
settlements, add factions, relocate colonies — and the author labels that panel
`"Active game features (experimental, use with caution)"` and ships all three
toggles **off** by default. Leave them off and this is a cosmetic renamer with
near-zero risk. Turn them on in a two-player MP session and you are doing
unsynced world-object surgery on a live save. **INFERRED**: MP-unsafe when the
experimental toggles are on; benign when off. No licence, no source.

---

### The bottom three — do not run these in a months-long co-op save without a decision

**7. Lemmy Progression for World Tech Levels** (3548896697) — *Dangerous, and pre-alpha by its own version file.*
`About/Version.txt` says `0.0.1`. The entire git history is one day, 2025-08-14,
including a commit literally titled `Major refactor - still not working
entirely`. It has **four hard dependencies** (WTL, VFE Tribals, Medieval
Overhaul, Harmony) plus reflection coupling to Worldbuilder — so five upstream
projects can break it, and its failure mode when they do is `Log.Warning` and
silent no-op, not an error. Its integration with World Tech Level is a
string-name guess-and-scan through another mod's assembly (§4.5). The core
mechanic is **runtime mutation of `FactionDef`s** to upgrade factions between
tech eras, with a git commit confirming this leaked across factions sharing a
def until it was patched by forking defs at runtime. Per `CLAUDE.md`, def
mutation of shared defs is precisely the class of change that fails silently.
Ships with several empty folders (`1.6/Patches`, `1.6/Sounds`, `1.6/Textures`,
root `Assemblies`, root `Source/*`) and a misspelled `1.6/Langauges`. No
licence. `ScheduleSettlementUpgrades` is a stub that logs its intent and does
nothing. **This is the mod whose function most directly overlaps Archinity's
own progression design** — evaluate whether Archinity should just own this
behaviour in XML rather than depend on a v0.0.1 assembly.

**8. Rim War** (2222935097) — *Dangerous for MP specifically.*
Version 0.9.9.8 after seven years. Three independently sufficient desync
mechanisms, all directly observed: raw `new Thread()` for the faction sim; the
threading toggle is a **client-local mod setting** so two players can run
different execution models; and the threaded path consumes `Rand` off the main
thread via `RandomElement`. 101 `Rand.*` sites with one `PushState`/`PopState`
pair. `WorldComponentTick` also draws `Rand.Range` directly. It writes a large
parallel world model into the save (`RimWarData`, per-settlement and
per-caravan comps, capitols, warbands, path followers) across 25 scribing
files, and it runs a reflection-based repair pass over vanilla's private
faction relations on every load — meaning removing it later from a save that
contains its world objects is not a clean operation. It self-interrupts threads
under time pressure, making its own behaviour non-reproducible. MIT licence and
a real 1.6 recompile, but the 1.6 defs are byte-identical to 1.5, so the port
is maintenance, not hardening. Feature-wise it is exactly what Archinity's
vision wants; engineering-wise it is the single most likely cause of a dead
save. **If it is used at all, the threading setting must be identically off on
both clients — and that still leaves the main-thread `Rand` draws unsynced.**

**9. Faction Territories and Vassalage** (3626725895) — *Most dangerous.*
Ranked below Rim War because it combines Rim War's hazard class with none of
Rim War's track record, and because it actively misrepresents its own scope.

- The About description claims it draws territory regions. The 267 KB assembly
  ships autonomous invasions, AI settlement construction, vassalage, vassal
  outposts, vassal road progression and caravan incident weighting — **six
  `GameComponent`s and a `WorldComponent`, all ticking, all enabled by default**.
- `VassaliseComponent.GameComponentTick()` calls `Find.TickManager.Pause()` and
  mutates `CurTimeSpeed` from inside a tick. Under Multiplayer, game speed is
  synced global state; this is a direct conflict, and the whole method is
  wrapped in `catch { }` so it fails invisibly.
- It persists three custom `WorldObject` types into the save (`Invasion` alone
  has 19 `Scribe_` calls). Removing it mid-save silently strips structure.
- It reflection-probes two other mods (Rim War, VehicleMapFramework) with bare
  `catch { return false; }` fallbacks and an undeclared soft dependency on Rim
  War — so the two most dangerous mods in this list are designed to run
  *together*, compounding both shadow-ownership models over the same map.
- **No licence, no README, no changelog, no source, no version folders, single
  1.6 target, a settings field named `caravanIncidentLegacyMigrated` proving the
  config has already broken once, and 40+ behavioural settings** whose
  cross-product nobody has tested.
- It is also the newest mod in the set (highest workshop ID, 3626725895).

**Not genuinely 1.6-ready** (as distinct from "declares 1.6"):
Lemmy Progression (self-declared `0.0.1`, one day of history, silent-no-op
failure mode) and FTV (1.6-only, but no versioning discipline, no source, no
licence, scope wildly beyond its own description, and an MP-hostile tick).
Vanilla Outposts Expanded declares 1.6 honestly but **ships less on 1.6 than on
1.5** — Fishing outposts are gone and Factory outposts are commented out.
Rim War, Factional War and Faction Customizer all have genuine 1.6 builds;
Rim War's and Factional War's are recompiles of unchanged 1.5 defs.

---

## Appendix: how to reproduce

```bash
W="/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
ilspycmd -o out/rimwar -p "$W/2222935097/v1.6/Assemblies/RimWar.dll"
ilspycmd -o out/ftv    -p "$W/3626725895/Assemblies/FactionTerritories.dll"
ilspycmd -o out/fc     -p "$W/3336572602/1.6/Assemblies/FactionCustomizer.dll"

# MP-relevant scan
grep -ril -e multiplayer -e zetrith -e rwmt -e SyncMethod -e SyncWorker -e SyncField "$W/<id>"
grep -rn  -e "new Thread" -e "Task.Run" -e "ThreadPool" out/<mod>
grep -ro  "Rand\.[A-Za-z]*" out/<mod> | cut -d: -f2 | sort | uniq -c | sort -rn
grep -rn  "ComponentTick" out/<mod>
```

Sensible Factions, Factional War, Lemmy Progression, Map Mode Framework and
Vanilla Outposts Expanded ship readable `Source/` trees — no decompile needed.
Map Mode Framework and Lemmy Progression ship live `.git` directories; run
`git log --format="%ad %h %s" --date=short` in them for maintenance history.
