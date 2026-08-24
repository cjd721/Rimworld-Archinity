# Recon: [SR]Factional War (fork) — Workshop 3423264477

**Path:** `/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3423264477`
**packageId:** `SR.ModRimworld.FactionalWarContinued`
**Authors:** llunak (fork maintainer), Shadowrabbit (original)
**Assembly:** `Assemblies/ModRimworldFactionalWar.dll`, `AssemblyVersion 2025.0830.1`
**Source:** ships complete, 62 `.cs` files under `Source/` — read directly, no decompile needed.
**Assessed:** 2026-08-24

---

## TL;DR

This is **not** a faction-war simulation. It is a **battle-scene generator**: four vanilla-style
incidents that spawn two mutually-hostile factions' pawns onto a map and let their Lord AI fight
each other while the player watches. Faction hostility is read as a *precondition* from vanilla
relations; the mod **never writes a single point of goodwill, never defeats a faction, never
changes faction strength, and holds no persistent war state at all**. There is no
`WorldComponent`, no `GameComponent`, no tick loop, no ledger.

Against the Archinity design requirement ("factions in wars that progress with or without the
player"), this delivers the *visual* of the requirement and none of the *mechanics*.

---

## 1. Architecture — what actually exists

Grep for the things a war simulation would need, over `Source/`:

```
=== goodwill/relations ===
./AI/AIGroup/TriggerBecameNonHostileToFaction.cs:48:  var previousRelationKind = signal.previousRelationKind;   (READ)
./AI/AIGroup/TriggerBecameNonHostileToFaction.cs:49:  ... == FactionRelationKind.Hostile ...                     (READ)
./Faction/FactionExtension.cs:36:                     if (faction.defeated)                                     (READ)

=== WorldComponent/GameComponent/MapComponent/override void Tick ===
(no matches)
```

Zero writes. Zero background simulation. Every mention of faction relations is a *read* used to
pick two factions or to abort a fight that has stopped being valid.

Harmony surface is likewise near-nil:

```csharp
// Source/HarmonyPatches.cs
_harmonyInstance = new Harmony("com.shadowrabbit.factionalwar.saveourships2.filterspacemap");
_harmonyInstance.PatchAll();
```

`PatchAll()` is called but **there is not a single `[HarmonyPatch]` attribute anywhere in the
source tree** (`grep -rn "HarmonyPatch" --include=*.cs .` → only `HarmonyPatches.cs` itself, the
class name). Harmony is used purely as a *reflection helper* — `AccessTools.MethodDelegate` for
soft-linking to the HideRaidStrategy mod (`Source/Util/HideRaidStrategy.cs`) and
`Traverse.Create(map).Method("IsSpace")` for SOS2 detection (`Source/Util/HarmonyUtil.cs`). The
mod patches nothing in vanilla. Everything else is defs + subclasses of vanilla
`IncidentWorker` / `Site` / `LordJob` / `LordToil` / `ThinkNode_JobGiver` / `GenStep`.

---

## 2. The four incidents — enumerated

All four live in `Defs/IncidentDef/IncidentsMapSpecial.xml`, all identical in gating:

```xml
<category>Misc</category>
<baseChance>1</baseChance>
<pointsScaleable>true</pointsScaleable>
<requireColonistsPresent>false</requireColonistsPresent>
<targetTags>Map_PlayerHome, Map_TempIncident, Map_Misc, Map_RaidBeacon</targetTags>
```

`baseChance` 1 with `category Misc` — these are ordinary storyteller-roll incidents. The trigger
is the **vanilla storyteller**, not player action, not a war state, not a tick loop.

| defName | Worker | Where it happens | Preconditions |
|---|---|---|---|
| `SrFactionWar` | `IncidentWorkerFactionWar : IncidentWorker_Raid` | **On the target map — i.e. the player's colony map** | Two visible, non-hidden, non-defeated, non-temporary humanlike factions hostile to each other, both with a `Combat` pawnGroupMaker, both affordable at current points, both `earliestRaidDays` elapsed. **No tech-level gate.** Not an SOS2 space map. |
| `SrFactionWarShellingSiteGenerate` | `IncidentWorkerFactionWarShellingSiteGenerate : IncidentWorker` | New **world-map site**, 2–7 tiles away | None at fire time. Faction pair is picked later, at `PostMapGenerate`, and **both factions must be `techLevel >= Industrial`**. |
| `SrFactionWarContentionSiteGenerate` | `IncidentWorkerFactionWarContentionSiteGenerate : IncidentWorker` | New **world-map site**, 2–7 tiles away | Same; additionally at `PostMapGenerate` **faction1 must be `HostileTo(Faction.OfPlayer)`**. |
| `SrFactionWarTempCampSiteGenerate` | `IncidentWorkerFactionWarTempCampSiteGenerate : IncidentWorker` | New **world-map site**, 2–7 tiles away | Site faction = `Find.FactionManager.RandomRaidableEnemyFaction(false,false,false)` — an enemy of the *player*. Attacker chosen at map gen. |

Note the site incidents have **`CanFireNowSub` unoverridden** — they always pass. They create the
world object unconditionally. The "is there actually a war?" check happens only when the player
*enters* the map, and if it fails the map is simply empty (`if (faction1 == null || faction2 ==
null) { return; }` — `SiteFactionWarShelling.cs:70`, `SiteFactionWarContention.cs:64`). **A
generated site can be a completely empty map.**

### Duplicate-faction bug (worth flagging)

`FactionUtil.GetHostileFactionPair` (`Source/Faction/FactionUtil.cs:31`) iterates
`candidateFactionList` for `faction`, then iterates the *same list* for `anotherFaction` with
`.Where(anotherFaction => faction.HostileTo(anotherFaction))`. There is no
`anotherFaction != faction` guard. A faction that is `HostileTo` itself (rare but possible with
some modded faction defs) would fight itself. INFERRED — not observed, but the guard is absent.

---

## 3. `SrFactionWar` end to end — the on-colony-map fight

`Source/Incident/IncidentWorkerFactionWar.cs`, `TryExecuteWorker`:

1. `ResolveRaidPoints(parms)` — clamped to `MaxRaidPoints = 5000`.
2. `FindFactionsInWar` → `FactionUtil.GetHostileFactionPair(...)` after
   `candidateFactionList.Shuffle()`.
3. Builds a **second** `IncidentParms` for faction 2 sharing the same `target` map.
4. Both forced to `parms.raidStrategy = RaidStrategyDefOf.SrFactionFirst` and arrival mode
   `SrTwoFactionsEdgeWalkIn` (`PawnsArrivalModeWorker_EdgeWalkIn`, `walkIn = true`).
5. `ResolvePawnList` → `PawnGroupMakerUtility.GeneratePawns` → `parms.raidArrivalMode.Worker.Arrive(...)`.
   **Both groups walk in from map edges onto the player's home map.**
6. Loot: `var raidLootPoints = parms.points / 10;` then `GenerateRaidLoot` on both groups — the
   pawns carry sellable/lootable goods, i.e. the corpses are worth picking over.
7. Letter: `LetterDefOf.ThreatSmall` (llunak's fork downgraded this from ThreatBig — see §9).
8. Lord assignment via the shared def-worker singleton:

```csharp
raidStrategyWorkerFactionFirst.TempTargetFaction = _faction2;
raidStrategyWorkerFactionFirst.MakeLords(parms, pawnListFaction1);
raidStrategyWorkerFactionFirst.TempTargetFaction = _faction1;
raidStrategyWorkerFactionFirst.MakeLords(parms2, pawnListFaction2);
```

`TempTargetFaction` is an instance property on `RaidStrategyWorkerFactionFirst`, and
`RaidStrategyDef.Worker` is a **process-wide singleton**. It is set-then-immediately-consumed on
the same call stack, so it is not itself a desync source, but it *is* mutable shared state hanging
off a Def — noted for the record (`Source/Incident/RaidStrategyWorkerFactionFirst.cs:33`).

### The Lord state machine

`LordJobStageThenAssaultFactionFirst` → `LordToil_Stage` (5000 ticks / 30% losses / harmed by
target faction) → subgraph `LordJobAssaultFactionFirst`:

- `LordToilAssaultFactionFirst` (duty `SrAssaultFactionFirst`: fight hostile faction, walk to
  nearest hostile faction member, sap)
- on `TriggerFactionAssaultVictory` (all target-faction pawns downed/dead/prisoner, polled every
  600 ticks) → `LordToilKillHostileFactionMember` (**executes the downed wounded**)
- on `TriggerAllHostileFactionMembersDead` → `LordToilClearBattlefield` (duty
  `SrClearBattlefield`: `JobGiver_TakeWoundedGuest` + `JobGiverTakeSpoils` + `JobGiver_ExitMapBest`)
- on `TriggetGetDamageFromPlayer` → **`LordToil_AssaultColony`** — vanilla. They turn on you.
- on `TriggerBecameNonHostileToFaction` → `LordToil_ExitMap`.

`JobGiverTakeSpoils` (`Source/AI/AISingle/JobGiverTakeSpoils.cs`) only steals items **adjacent to
a corpse of the target faction or their own faction** (`IsThingNearByCorpse`). So they loot the
battlefield, not your stockpiles — unless the fight moves through them.

**Net board change: some corpses, some dropped gear, some kidnapped wounded, on your map. Nothing
on the world map. Nothing in the faction ledger.**

---

## 4. The three site incidents — where and what

All three: `TileFinder.TryFindNewSiteTile(out var tileId, MinDist=2, MaxDist=7)`, then
`WorldObjectMaker.MakeWorldObject(...)`, `Find.WorldObjects.Add(site)`, neutral letter.

**Faction Contention** (`SiteFactionWarContention.cs`) — `GenStepAirdropResource` drop-pods three
rolls of `MapGen_AncientTempleContents` loot into the map centre and spawns **1000 points of
mechanoids** on `LordJob_DefendPoint` to guard it. Then `PostMapGenerate` airdrops two hostile
industrial+ factions (3000–5000 pts, and `2 *` that for faction 2 — faction 2 is deliberately
overwhelming) on `LordJobFactionContention` → `LordToilDefendPoint` → after
`Trigger_TicksPassedWithoutHarmOrMemos(1500)` → `LordToilRetreat` (grab the best thing and leave).
This is a loot map with three-way opposition, not a war.

**Faction Bombardment** (`SiteFactionWarShelling.cs`) — two industrial+ hostile factions,
3000–9999 pts each, on `LordJobShellFactionFirst`: travel → `LordToilShell : LordToil_Siege`
(drop-pods in mortars, shells, building materials, they build a siege camp and shell each other)
→ assault → kill wounded. Mortar shells landing on a map the player can wander into.

**Faction Defense** (`SiteTempCamp.cs` + `GenStepTempCamp` + `SymbolResolverTempCamp`) — generates
a full 70×70 fortified outpost (`edgeDefenseTurretsCount = Rand.RangeInclusive(3, 6)`,
`edgeDefenseMortarsCount = Rand.RangeInclusive(1, 2)`, barracks, power) for a raidable-enemy
faction, then spawns 2000–5000 pts of a *different* faction hostile to it on
`LordJobRaidFactionFirst` → assault → on victory `LordToilPlunderFaction` (duty
`SrPlunderFaction`: `JobGiverDestroyDoor`, `JobGiverKidnapFaction`, `JobGiverTakeBestThing`,
exit). This is the closest thing to "one faction attacks another faction's holding" in the mod —
but the holding is created for the occasion and evaporates afterwards.

All three sites: `TimeoutComp.StartTimeout(90000)` = **1.5 in-game days** from spawn
(`TimeOutTick = 90000` in all three site classes). That is a very short window to caravan 2–7
tiles and back.

---

## 5. Persistence — the crux

**No.** Nothing persists.

- No goodwill written (grep above).
- No `faction.defeated = true` ever set — only read in `FactionExtension.IsFactionEffective`.
- No settlement destroyed, no tile changed hands, no faction strength value exists to change.
- The site world objects `Destroy()` on timeout; the maps are `Site` subclasses so vanilla
  `ShouldRemoveMapNow` reclaims them when no player pawn is present (INFERRED — vanilla `Site`
  behaviour, not overridden here).
- The only durable trace: corpses, dropped weapons, and kidnapped pawns from the fights the player
  actually attended.

If the same two factions are hostile tomorrow, the same incident can fire again identically. It
**resets**. There is no attrition, no escalation, no resolution.

---

## 6. Player intervention

Two mechanisms, both purely local:

**Attack them and they turn on you.** `TriggetGetDamageFromPlayer`
(`Source/AI/AIGroup/TriggetGetDamageFromPlayer.cs`) fires on `TriggerSignalType.PawnDamaged` where
`signal.dinfo.Instigator.Faction == Faction.OfPlayer` (turrets count; animals don't):

```csharp
//友好派系
if (!lord.faction.HostileTo(Faction.OfPlayer)) { return false; }
```

Note the guard: **only factions already hostile to the player can be provoked into
`LordToil_AssaultColony`.** A neutral faction fighting on your map can be shot at all day and will
not switch to attacking you via this mod. It *will* lose goodwill through vanilla
`Faction.Notify_MemberDied`, and can go hostile that way — but that is vanilla, unmodified, and
the Lord will not retarget. INFERRED for the vanilla-goodwill half.

**Make peace and they leave.** `TriggerBecameNonHostileToFaction` — if the two AI factions stop
being hostile to *each other* mid-fight, the Lord transitions to `LordToil_ExitMap`. The mod
supplies no way to cause that; it is a defensive check against relations changing under it.

**There is no "help faction A against faction B" action, no reward for doing so, no relations
consequence for doing so, and no way for the two factions to notice you did.** Helping one is not
refusing another. It is shooting at pixels.

---

## 7. Multiplayer determinism verdict

### Verdict: **CONDITIONAL FAIL — do not ship without a settings lockdown, and treat site maps as unverified.**

No `Multiplayer` reference anywhere (`grep -rni "multiplayer|Zetrith|SyncMethod"` → 0 hits). The
mod is unaware of MP. That is normal; the question is whether its behaviour is deterministic.

#### Hazard 1 — mod settings feed directly into pawn generation. **This is the killer.**

`Source/Pawn/PawnGroupMakerUtility.cs:29`:

```csharp
public static List<Pawn> GeneratePawns(PawnGroupMakerParms pawnGroupMakerParms)
{
    DiscardPawns();
    pawnGroupMakerParms.points *= SettingWindow.Instance.settingModel.threatPointFactor;
    var pawnList = RimWorld.PawnGroupMakerUtility.GeneratePawns(pawnGroupMakerParms).ToList();
    return pawnList;
}
```

`threatPointFactor` is a `ModSettings` float, slider range **0.1 to 2.0**
(`Source/UI/Window/SettingWindow.cs:44`), stored per-client in `config/ModSettings/`. A one-notch
difference between the two clients means **a different number of pawns, of different kinds, with
different Rand draws consumed** — instant, unrecoverable desync the first time any of these four
incidents fires. This is precisely the failure mode `CLAUDE.md` warns about ("identical mod
settings — the third is the one people miss").

#### Hazard 2 — the "optimization" setting *destroys world pawns* mid-generation.

Same file, `DiscardPawns()`:

```csharp
private static void DiscardPawns()
{
    if (SettingWindow.Instance.settingModel.needOptimization) { return; }   // note: inverted naming
    var worldPawns = Find.World.worldPawns;
    DiscardPawns(worldPawns.GetPawnsBySituation(WorldPawnSituation.Free).ToList());
    DiscardPawns(worldPawns.GetPawnsBySituation(WorldPawnSituation.Dead).ToList());
    DiscardPawns(worldPawns.GetPawnsBySituation(WorldPawnSituation.Kidnapped).ToList());
}
...
    worldPawns.RemoveAndDiscardPawnViaGC(pawnList[i]);
```

When `needOptimization == false` (the checkbox is labelled "Enable optimization", so the *unticked*
state runs this — the naming is inverted relative to the field), every faction-war spawn
**permanently deletes free/dead/kidnapped world pawns**, including relatives of colonists and
kidnapped colonists not on a player-home map. It also iterates `for (var i = pawnList.Count - 1;
i > 0; i--)` — index 0 is never processed, a latent off-by-one. Two clients with different values
for this checkbox will have divergent world-pawn registries *and* divergent Rand consumption.
Save-integrity hazard independent of MP.

#### Hazard 3 — unseeded `Rand` in `Site.PostMapGenerate`. **INFERRED risk, needs testing.**

`GenStep` subclasses correctly declare `SeedPart` (`GenStepAirdropResource.SeedPart =
546950704`, `GenStepTempCamp.SeedPart = 546950703`), so map-generation randomness is seeded the
vanilla way. But the faction selection and pawn spawning for the shelling and contention sites
happen in `PostMapGenerate()`, *after* the gen-step chain, using raw `Rand`:

```csharp
// Source/WorldObject/Site/SiteFactionWarShelling.cs:52,113
var points = ThreatPoints.RandomInRange;                 // IntRange(3000, 9999)
...
var blueprintPoints = points * Rand.Range(0.2f, 0.3f);

// Source/Faction/FactionUtil.cs:38
candidateFactionList.Shuffle();

// Source/Util/PawnSpawnUtil.cs:20-22
if (!RCellFinder.TryFindRandomPawnEntryCell(out incidentParms.spawnCenter, map, CellFinder.EdgeRoadChance_Hostile))
    incidentParms.spawnCenter = CellFinder.RandomEdgeCell(map);
```

Whether this is safe depends on whether RimWorld-Multiplayer's map-generation sync wraps
`PostMapGenerate` inside its seeded `Rand.PushState` scope. If it does not, **the two clients will
pick different faction pairs and different spawn cells on the same site map.** I could not verify
this from the mod source; it requires reading the MP mod's map-gen patches. **Mark this as the
single highest-value thing to test if you proceed.**

Note the fork's own commit "consistent faction selection for faction defense" (2025-06-19)
suggests inconsistency in this exact area was already a known bug — `SiteTempCamp` calls
`FactionUtil.RandomTempCampFaction()` **twice** in
`IncidentWorkerFactionWarTempCampSiteGenerate.cs` (once into `GenerateDefaultParams`, once into
`SetFaction`), which returns a *different* random faction each call.

#### Hazard 4 — `WorldCompFormCaravanAfterAllyExit` overrides caravan gizmos. **INFERRED.**

`Source/WorldObject/WorldObject/WorldCompFormCaravanAfterAllyExit.cs` subclasses vanilla
`FormCaravanComp` and fully replaces `GetGizmos()`, constructing its own `Command_Action` with
`action = () => Find.WindowStack.Add(new Dialog_FormCaravan(mapParent.Map))`. The MP mod syncs
caravan formation by patching vanilla gizmo/dialog paths. A mod-authored gizmo that bypasses the
patched call site is a classic MP break (one client opens a dialog the other never sees). Whether
MP's patch on `Dialog_FormCaravan` itself is sufficient to cover this is unverified.

#### Not hazards

`Rand` inside `LordToilShell.Init()`, `TriggerFactionAssaultVictory` (Tick-gated,
`TicksGame % 600`), the JobGivers, and `SymbolResolverTempCamp` all execute inside already-synced
tick/mapgen contexts and consume Rand identically on both clients **provided** hazards 1–3 have
not already caused divergence. No static mutable caches of consequence: the only statics are
`Harmony _harmonyInstance`, `SettingWindow.Instance`, the `[DefOf]` fields in `Util/Defs.cs` and
`Incident/IncidentDefOf.cs`, and `readonly` config ranges.

#### Minimum viable mitigation if you use it

1. Both clients ship an identical `config/ModSettings/SR.ModRimworld.FactionalWarContinued.xml`
   and re-snapshot after any settings touch. Non-negotiable.
2. Force `needOptimization = true` (the non-destroying branch) on both.
3. Test a site map entry in a live two-client session before trusting hazard 3.

---

## 8. Performance and save bloat

- **Pawn counts are large.** `SrFactionWar` caps at 5000 points **per faction** = up to 10,000
  points of humanlike pawns on your colony map at once, from a mod whose incident has
  `baseChance 1` and no cooldown of its own. Shelling sites go to 9999 **each**. Contention spawns
  `3000–5000` for faction 1 and `2 * (3000–5000)` for faction 2, plus 1000 points of mechanoids.
  On the MP mod, which already ticks worse than vanilla, these are the exact scenarios that turn a
  co-op session into a slideshow.
- **World-pawn accumulation.** Every survivor that exits the map is passed to `WorldPawns`. Over a
  long playthrough this is the main save-bloat vector, and the author's own answer to it is the
  destructive `DiscardPawns` in hazard 2 — a cure worse than the disease.
- **Maps.** Site maps are vanilla `Site`s with `TimeoutComp(90000)`, so they self-clean on timeout
  and on player exit. No leak there (INFERRED from vanilla `Site.ShouldRemoveMapNow`).
- **Empty-site garbage.** Because the site incidents never check whether a valid faction pair
  exists before creating the world object, they can leave 1.5-day-lived world objects on the map
  that generate nothing. Cosmetic clutter and a wasted caravan trip.
- `LordToilShell.Init()` drop-pods a full siege camp's worth of materials and shells per faction —
  two siege camps per shelling map.

---

## 9. What is the fork

Upstream chain: Shadowrabbit's original (`2534328163`, 2021) → a "Continued" fork
(`3220197628`) → **llunak's fork** (this one). About.xml:

> This is a fork of ...id=2534328163 , with changes from ...id=3220197628 incorporated.

**Repo:** `https://github.com/llunak/rimworld-FactionalWar` — not archived, 0 open issues, last
push **2025-08-30**, which matches `AssemblyVersion 2025.0830.1` exactly. So the shipped 1.6 DLL
is the head of that repo. **Genuinely maintained**, by a maintainer with a track record of
maintaining abandoned RimWorld mods, but with a bus factor of one and 1 star.

Commit log (via GitHub API), what the fork actually changed:

| Date | Change |
|---|---|
| 2024-08-31 | classify faction war event only as a **small threat** (`LetterDefOf.ThreatSmall`) |
| 2024-08-31 | **force starting a fight if a faction in faction war gets attacked** |
| 2024-12-14 | optipng, remove .rej files |
| 2025-06-12 | switch to 1.6, make build with 1.6, rebuild dll |
| 2025-06-16 | copy textures and languages to version folders |
| 2025-06-19 | harmony dependency for 1.6; **explicitly filter out hidden factions** (`if (faction.Hidden) return false;` in `FactionExtension.cs:44`) |
| 2025-06-19 | **prevent non-humanlikes from taking items** (`if (!pawn.RaceProps.Humanlike) return null;` in `JobGiverTakeSpoils.cs:26`) |
| 2025-06-19 | **consistent faction selection for faction defense** |
| 2025-07-18 | comply with RimWorld EULA (the `LICENSE` file — EULA-derivative, redistribution allowed) |
| 2025-08-13 | **do not start the incident if pawns couldn't be spawned**; **abort incident if raid arrival mode cannot be used** |
| 2025-08-30 | **try harder to avoid using factions that cannot be spawned on the map** (`FactionUtil.IsUsable`) |

The fork's contribution is entirely **robustness and 1.6 compat** — SOS2 space-map filtering,
hidden-faction filtering, arrival-mode validation, pawn-cleanup-on-partial-failure:

```csharp
// IncidentWorkerFactionWar.cs — llunak's cleanup for the half-spawned case
var pawnListFaction2 = ResolvePawnList(parms2);
if( !pawnListFaction2.Any())
{
    foreach( Pawn pawn in pawnListFaction1 )
    {
        pawn.DeSpawn();
        Find.WorldPawns.PassToWorld(pawn);
    }
    return false;
}
```

**No design changes.** The fork did not add persistence, relations effects, or world simulation.

### 1.6 support is thin

`loadFolders.xml` maps `v1.6` to `/` (root). `diff -rq Defs 1.5/Defs` → **identical**, and
`diff -rq 1.4/Defs 1.5/Defs` → **identical**. 1.6 support is a DLL recompile, nothing more. 812
XML files is misleading — it is 5 near-identical copies of ~10 defs plus 8 language folders each.

### Latent def/namespace mismatch

`Defs/IncidentDef/IncidentsMapSpecial.xml` and `Defs/RaidStrategyDef/RaidStrategies.xml` reference
`SR.ModRim**w**orld.FactionalWar.*` (lowercase w) while the assembly's namespace is
`SR.ModRim**W**orld.FactionalWar` (`grep -ac "ModRimworld.FactionalWar" <dll>` → 0;
`grep -ac "ModRimWorld.FactionalWar" <dll>` → 2). All *other* class references in the same def
folder use the correct capitalisation. This resolves only because `GenTypes` falls back to
short-name lookup when the fully-qualified name misses (INFERRED). It works today; it would break
if another loaded mod ever shipped a class named `IncidentWorkerFactionWar`.

---

## 10. The 20% question — what is separable

If the goal is "factions visibly fight each other and it changes the board," here is the split.

### Delivers "visibly fight" — cleanly separable, genuinely reusable

The **AI layer** is the real asset and it is almost entirely def-driven:

- `Defs/DutyDef/DutiesMisc.xml` — `SrAssaultFactionFirst`, `SrKillHostileFactionMember`,
  `SrClearBattlefield`, `SrDefend`, `SrRetreat`, `SrPlunderFaction`
- `Source/AI/AISingle/*` — 8 `ThinkNode_JobGiver` subclasses (fight-hostile-faction,
  goto-nearest-hostile-faction-member, sapper, destroy-door, kidnap, take-spoils, take-best-thing,
  kill-hostile-faction-member) and `JobDriverKillMelee`
- `Source/AI/AIGroup/*` — the LordJob/LordToil/Trigger set

Vanilla pawn AI cannot target a non-player faction; this layer is the machinery that makes it
possible. It has **no dependency** on the incidents, the sites, the settings, or
`PawnGroupMakerUtility`. Lifting `LordJobAssaultFactionFirst` + its toils/triggers + the DutyDefs
+ the JobGivers into an Archinity assembly is a clean cut. **This is the 20%.**

Caveat: it would be Archinity's *second* Harmony-free-but-still-C# assembly, which `CLAUDE.md`
says needs an explicit decision. Note the AI layer contains no `Rand` at all outside
`JobGiverAISapper`'s `TryRandomElement` and `LordToilShell` — both inside synced job/tick contexts.

### Delivers "changes the board" — **nothing here delivers this.** Must be built.

The mod has no concept of a war that exists between fights. To satisfy the design requirement you
would need, and would be writing from scratch:

- a `WorldComponent` holding war state (belligerents, attrition, objectives)
- a tick loop advancing it whether or not the player attends
- relations/strength writes on resolution
- something the factions *want* — a demand, an ask, a reward for siding
- consequences to the player for siding (the other belligerent's goodwill)

### Not worth taking

- The three **site incidents** — short 1.5-day timeout, 2–7 tile range, can generate empty maps,
  spawn 5000–20000 threat points, and in MP demand both players caravan to and load a second map.
  For two-player co-op this is expensive and fragile for a self-contained vignette.
- **`PawnGroupMakerUtility`** — hazards 1 and 2. Delete outright; call
  `RimWorld.PawnGroupMakerUtility.GeneratePawns` directly.
- **`WorldCompFormCaravanAfterAllyExit`** — solves a problem (can't reform caravan while allies
  loot) you only have if you take the sites.
- **`SettingModel`/`SettingWindow`** — the MP hazard surface. If you lift the AI layer, ship no
  settings at all.

---

## Bottom line for Archinity

**As a drop-in mod: no.** The MP settings coupling is a hard fail without a locked settings
snapshot, and even with one, hazard 3 is untested and hazards 2 and 4 are real. More importantly
it does not do the thing the design document asks for — it *stages* faction conflict, it does not
*simulate* it. Factions here never want anything from each other; the mod reads a hostility flag
vanilla already set and puts on a show. Helping one costs you nothing and gains you nothing, so
the vending-machine problem is untouched.

**As a parts donor: yes, one part.** The Lord AI + DutyDef + JobGiver layer that lets pawns
meaningfully fight a non-player faction is well-built, MP-clean, def-heavy, and exactly the piece
that is genuinely hard to write. The war *simulation* has to be Archinity's own.
