# Recon: Faction Territories and Vassalage + Map Mode Framework

Assessed for Archinity (RimWorld 1.6, two-player co-op on the **Multiplayer** mod).

| | Faction Territories and Vassalage | Map Mode Framework |
|---|---|---|
| Workshop | `3626725895` | `3296654393` |
| packageId | `jaeger972.factionterritories` | `NozoMe.MapModeFramework` |
| Author | jaeger972 | NozoMe |
| Ships source? | **No** — DLL only, decompiled with `ilspycmd` | **Yes** — `Source/MapModeFramework/*.cs` |
| Size | ~18,800 lines decompiled, 5 namespaces | ~3,200 lines |
| Assembly | `Assemblies/FactionTerritories.dll` | `1.6/Assemblies/MapModeFramework.dll` |

Everything below is verified against the decompile / source unless marked **INFERRED**.

Decompile lives at
`%LOCALAPPDATA%\Temp\claude\C--Users-cjd72-Desktop-Personal-Mods-Rimworld-Archinity\6631190b-4577-4393-b6f3-561f901befe1\scratchpad\ft\`
(regenerate with `ilspycmd -p -o <dir> FactionTerritories.dll`).

---

## 0. TL;DR verdicts

- **Territory representation is genuinely good.** Deterministic, hash-seeded, cost-weighted
  multi-source Dijkstra over world tiles, resolved by influence plurality. No `Rand` anywhere in it.
  Derived, never saved. This is the single most reusable idea in the mod.
- **Territory does substantial mechanical work** — it gates AI-vs-AI invasions (settlements really
  change hands), drives map incursions from claimants, forces caravan-ambush factions to be the tile's
  owner, and bounds where factions expand. This is not a visualization with a token effect.
- **Vassalage is not what the name promises.** It is one-directional — the player takes vassals and
  can never become one — and its payoff is a **three-tab shop** converting idle time into silver,
  items, colonists and road progress. Closer to a vending machine than to a political loss path.
  Its one real story beat is the ally-cede dialog; its one real risk is losing a vassal to an
  invasion, and only if you enable a different subsystem.
- **MP verdict: both mods are unsafe as shipped, for different reasons.** MMF is MP-inert (zero live
  `Rand`, threads touch only render data) but structurally hostile — worker threads read
  `Find.WorldGrid` off the main thread. FT will desync six different ways, the first of which fires
  when a player merely **opens the settings or colour window**: that invalidates a static cache whose
  per-client revision counter gates a `Rand`-indexed AI decision.
- **The good part is cleanly separable.** `TerritoryOwnershipCache.cs` (553 lines) has *zero*
  MapModeFramework imports. Lift it, and you have territory-that-matters without the renderer.

---

## 1. How territory is actually represented

### Data structure

Not per-tile save data. Not a claimed radius. It is a **multi-source, cost-weighted Dijkstra flood
from every settlement, resolved by influence-count plurality**, held entirely in a static in-memory
cache and recomputed on demand.

`FactionTerritories/TerritoryOwnershipCache.cs`:

```csharp
private static Dictionary<int, HashSet<int>> factionsByTile;          // tile -> set of faction loadIDs
private static Dictionary<int, Dictionary<int, int>> influenceByTile; // tile -> factionId -> influence count
private static bool dirty = true;
private static int lastSettingsHash;
private static int revision;
```

`factionsByTile` maps **world tile id → set of owning faction loadIDs**. A set with >1 member means
*contested*. That is the whole ownership model.

### How it is computed

**Step 1 — collect sources.** Every `Settlement` plus anything `IsTerritoryAnchorWorldObject` accepts
(vassal outposts, outposts, outpost sites, Empire-FC settlements, "looks like an outpost" heuristics):

```csharp
int sourceSeed = FactionTerritoriesUtility.HashCombine3(
    globalSeed,
    PlanetTile.op_Implicit(((WorldObject)val).Tile),
    GenText.StableStringHash(((WorldObject)val).GetUniqueLoadID() ?? string.Empty));
int innerAlways = ((variation > 0) ? Mathf.Max(0, baseRadius - variation) : baseRadius);
int outer = baseRadius + variation;
```

`globalSeed` is the **world seed string**, not `Rand`:

```csharp
public static int GetDeterministicSeed(FactionTerritoriesSettings settings)
{
    if (settings != null && settings.seedOverride != 0) return settings.seedOverride;
    ...
    return GenText.StableStringHash(world.info.seedString);
    ...
    return 123456789;
}
```

**Step 2 — sort sources into a canonical order** so iteration order can never vary:

```csharp
list.Sort(delegate(Source a, Source b)
{
    int num4 = a.factionId.CompareTo(b.factionId);
    if (num4 != 0) return num4;
    num4 = a.startTile.CompareTo(b.startTile);
    return (num4 != 0) ? num4 : a.sourceSeed.CompareTo(b.sourceSeed);
});
```

**Step 3 — Dijkstra with a hand-rolled min-heap and a fully-specified tiebreak chain.** Note the
comparator: it never falls back to insertion order.

```csharp
private static bool Less(HeapItem a, HeapItem b)
{
    if (a.dist != b.dist)               return a.dist < b.dist;
    if (a.tie != b.tie)                 return a.tie < b.tie;
    if (a.sourceIndex != b.sourceIndex) return a.sourceIndex < b.sourceIndex;
    return a.tile < b.tile;
}
```

Edge cost is terrain movement difficulty, scaled ×100 to stay in integer arithmetic (avoiding float
non-determinism):

```csharp
private static int ComputeStepCostScaled(WorldGrid grid, int fromTile, int toTile, FactionTerritoriesSettings settings)
{
    float num = FactionTerritoriesUtility.EdgeMovementDifficultyNoWinter(grid, fromTile, toTile, settings);
    int num2 = Mathf.RoundToInt(Mathf.Max(0.01f, num) * 100f);
    return Mathf.Max(1, num2);
}
```

The ragged border is hash noise, not RNG:

```csharp
private static bool CanClaimTile(int seed, int tile, int dist, int radius, int variation, int innerAlways, int outer)
{
    if (variation <= 0)   return dist <= radius;
    if (dist <= innerAlways) return true;
    if (dist > outer)     return false;
    float num  = FactionTerritoriesUtility.Noise01(seed, tile, 9173);
    float num2 = (num - 0.5f) * 2f * (float)variation;
    return (float)dist - num2 <= (float)radius;
}
```

`Noise01` is a pure xorshift hash, no state:

```csharp
public static int HashInt(int x) { x ^= x << 13; x ^= x >> 17; x ^= x << 5; return x; }
public static float Noise01(int seed, int tile, int salt)
{
    int num = HashCombine3(seed, tile, salt);
    return (float)((num & 0x7FFFFFFF) % 10000) / 10000f;
}
```

**Step 4 — uncontested core rings.** `ApplySettlementUncontestedRings` BFS-stamps a hard-override
influence of `536870911` (0x1FFFFFFF) within `settlementUncontestedRange` steps of each settlement, so
a capital's immediate hinterland can never be contested:

```csharp
Dictionary<int, int> dictionary2 = new Dictionary<int, int>(1);
dictionary2[faction.loadID] = 536870911;
influenceMap[num4] = dictionary2;
```

**Step 5 — collapse influence into ownership.** Strict plurality: one faction owns the tile only if
its influence exceeds the *sum* of all others; otherwise all positive contributors are listed and
the tile renders as Contested.

```csharp
HashSet<int> hashSet = new HashSet<int>();
if (num >= 0 && num2 > num3) { hashSet.Add(num); }        // num2 = best, num3 = sum of rest
else { foreach (...) if (item3.Value > 0) hashSet.Add(item3.Key); }
```

### How it is stored in the save

**It is not.** There is no `ExposeData` for territory anywhere. It is a pure derived function of
`(world seed, set of anchor world objects, mod settings)`, rebuilt lazily:

```csharp
private static void EnsureCache(FactionTerritoriesSettings settings)
{
    int num = ComputeSettingsHash(settings);
    if (!dirty && factionsByTile != null && influenceByTile != null && num == lastSettingsHash) return;
    lastSettingsHash = num; dirty = false;
    factionsByTile = BuildFactionMap(settings, out influenceByTile);
    revision++;
}
```

`ComputeSettingsHash` mixes in nine settings fields (`radiusSteps`, `variationSteps`,
`terrainDifficultyImpactPercent`, `roadMovementDifficultyPercent`, `includeWaterTiles`,
`seedOverride`, `addRimWarSettlementScanRangePercent`, `settlementUncontestedRange`,
`impassableHillinessOffset`). **This is the MP landmine: territory is a function of mod settings,
so a settings mismatch between the two players produces different maps of the world.**

Invalidation hooks: `WorldObjectsHolder_Add_Patch` / `WorldObjectsHolder_Remove_Patch` /
`Caravan_PostRemove_FactionTerritories` all call `MarkDirty()`.

### Sizing

`radiusSteps` defaults to 5 → `baseRadius = 500` cost-units, and each step costs
`max(1, round(movementDifficulty × 100))` — so roughly 5 tiles on easy terrain, fewer through
mountains. `variationSteps` defaults to 0 (perfectly circular borders unless you turn it up).

---

## 2. How it is rendered

### What Map Mode Framework provides

MMF is a **pure presentation layer**. Grep confirms it contains no `Rand`, no simulation writes,
no game-state mutation. It provides:

- `MapModeDef` (a `Def`) declaring a `mapModeClass`, a `worldLayerClass`, and draw toggles
  (`drawHills`, `drawRivers`, `drawRoads`, `drawPollution`, `includeWater`, `displayLabels`,
  `doTooltip`) plus a nested `RegionProperties { overrideSelector, doBorders, borderWidth }`.
- `MapModeComponent : GameComponent` holding `currentMapMode` and a `DrawSettings` bag. Its
  `ExposeData` saves only the *list of MapModeDefs*, nothing else.
- `Region`, the drawing primitive — this is what a "territory" becomes:

```csharp
public class Region
{
    public string name;
    public List<int> tiles;
    public bool skipBody;
    public Material material;
    public bool doBorders;
    public Material borderMaterial;
    public float borderWidth;
    public string tooltip;
    public List<int> cachedBorders;
}
```

- `WorldLayer_MapMode_Region : WorldDrawLayer` — the actual draw path.
- `WorldRegenHandler` / `TaskHandler` — async regeneration with cancellation tokens.
- `EdgesCache` / `RegionCache<T>` — static memo dictionaries.
- A toolbar window (`MapModeUI`) auto-added whenever `WorldRendererUtility.WorldRendered`.
- Harmony patches, all render/UI only: suppressing vanilla `WorldDrawLayer_Hills/Rivers/Roads/Pollution`,
  suppressing `ExpandableWorldObjectsOnGUI`, overriding `WorldSelector.SelectUnderMouse` to select a
  whole region instead of a tile, and killing async tasks on `MemoryUtility.ClearAllMapsAndWorld`.
- An XML patch injecting four draw layers into the Surface planet layer:

```xml
<xpath>Defs/PlanetLayerDef[defName="Surface"]/worldDrawLayers</xpath>
<value>
  <li>MapModeFramework.WorldLayer_MapMode_Terrain</li>
  <li>MapModeFramework.WorldLayer_MapMode_Region</li>
  <li>MapModeFramework.WorldLayer_MouseRegion</li>
  <li>MapModeFramework.WorldLayer_SelectedRegion</li>
</value>
```

### The actual draw path

**It is an overlay mesh, not a shader on the world sphere.** Per-tile hex geometry is appended to
`LayerSubMesh` buffers grouped by `Material`, lifted 1.2% off the sphere to avoid z-fighting:

```csharp
public static void DrawTile(LayerSubMesh subMesh, int tile)
{
    List<Vector3> vertices = GetTileVertices(tile);
    ...
    subMesh.verts.Add(vertices[j] + vertices[j].normalized * 0.012f);
    subMesh.uvs.Add((GenGeo.RegularPolygonVertexPosition(vertCount, j) + Vector2.one) / 2f);
```

Borders are ribbon quads built from tile edges, with interior edges culled by testing whether the
neighbour is also in the region:

```csharp
TileUtilities.DerivePerpendicularVectors(edge.Item1, edge.Item2, borderWidth, out var v1, out var v2);
subMesh.verts.Add(v1); subMesh.verts.Add(v2);
subMesh.verts.Add(edge.Item1); subMesh.verts.Add(edge.Item2);
```

Materials are `ShaderDatabase.MetaOverlay` at `renderQueue = 3510` (`Materials.cs`).

### The shader — what it is actually for

`Shaders/FT_WorldVoronoiPalette.shader` is **not** how territory is drawn. It is used only for the
**contested-tile fill pattern**. `worldcomponent.cs` bakes a 1024×512 Voronoi cell texture from 256
hash-placed sites (R = cell id, G = distance-to-second-nearest, used as an edge darken), and the
shader indexes a per-contest palette texture by cell id:

```hlsl
float cellId = cell.r * 255.0;
float edge   = cell.g;
float idx = fmod(cellId, max(1.0, _PaletteCount));
float u = (idx + 0.5) / max(1.0, _PaletteCount);
fixed4 col = tex2D(_PaletteTex, float2(u, 0.5));
col.a *= _Alpha;
col.rgb *= lerp(1.0, 1.0 - _EdgeStrength, saturate(edge));
```

So contested regions get a mottled multi-colour patchwork of the claimants' colours instead of a flat
average. Purely cosmetic. `settings.useSolidContestedColour` disables it entirely, and
`GetContestedMaterialSafe` has an extensive fallback path if the shader bundle fails to load.

### Cost

Real, and the mod authors know it — MMF ships a progress bar (`"MMF.UI.LoadProgress".Translate(tilesPrepared, tilesToPrepare)`),
an async worker-thread pipeline, an opt-in persistent cache, and a "you should turn on caching"
nag after 10 seconds.

The hot spot is quadratic. `WorldLayer_Region.PrepareBorders` closes over `List.Contains`:

```csharp
bool excludeNeighbor(int x)      => regionTiles.Contains(x) && !borderTiles.Contains(x);
bool neighborIsContiguous(int x) => regionTiles.Contains(x) && borderTiles.Contains(x);
```

`regionTiles` is a `List<int>` that for a large faction is thousands of entries, and these predicates
run per border tile per neighbour (6×). `MapMode_Region.GetRegion` is worse:

```csharp
public Region GetRegion(int tile) => regions.FirstOrDefault(x => x.tiles.Contains(tile));
```

O(regions × tiles) per lookup, and it is the backing of both `GetMaterial` and `GetTooltip`.
Mitigations that exist: mesh build runs on `Task.Run` off the main thread; `EdgesCache` memoises the
per-tile `bool[] drawEdges`; results are only recomputed when `MapModeComponent.regenerateNow` is set.

**Cost verdict:** fine for a world-map overlay you toggle on. Not fine as an always-on layer on a
100%-coverage planet, and it produces a visible multi-second hitch on first entry to the map mode and
on every settlement destroyed/created (`FactionTerritoriesUtility.RequestRegenerate(clearCache: true)`
is called on every vassalisation, cede, and outpost add/remove).

---

## 3. Does territory DO anything mechanically?

**Yes — two real systems, both driven off `TerritoryOwnershipCache.TryGetClaimingFactions(tile, ...)`.**

### 3a. Map incursions (the good one)

`GameComponent_FactionTerritories.GameComponentTick` scans every open `Map` on a 2500-tick interval
plus a 60-tick new-map scan, and periodically sends squads from whatever factions claim that map's
tile. This is the "territory has teeth" mechanic.

```csharp
IEnumerable<Pawn> enumerable = PawnGroupMakerUtility.GeneratePawns(new PawnGroupMakerParms
{
    groupKind = PawnGroupKindDefOf.Combat,
    faction = faction,
    points = incursionPoints,
    raidStrategy = RaidStrategyDefOf.ImmediateAttack,
    dontUseSingleUseRocketLaunchers = true
}, true);
...
if (hostileToPlayer)
{
    LordMaker.MakeNewLord(faction, new LordJob_AssaultColony(faction, false, false, false, false, false, false, false), map, list);
    Messages.Message(faction.Name + " forces have launched a territory incursion on " + GetMapLabel(map) + ".", MessageTypeDefOf.ThreatBig, false);
}
else
{
    IntVec3 val4 = FindMapDefenceCentre(map, faction);
    LordMaker.MakeNewLord(faction, new LordJob_DefendBase(faction, val4, 25000, false), map, list);
    Messages.Message(faction.Name + " forces have arrived to support " + GetMapLabel(map) + ".", MessageTypeDefOf.PositiveEvent, false);
}
```

Note it distinguishes **temporary** maps (sites, camps, quests, ambushes — classified by fuzzy type-name
matching in `LooksLikeTemporaryEncounterParent`) from **persistent** ones, with four independent
settings toggles (`enable{Temporary,Persistent}{Hostile,Friendly}TerritoryMapIncursions`). Friendly
claimants show up to *help you*. That is exactly the "factions are forces in the world" flavour.

Scheduling is explicitly hash-seeded, which is unusually careful:

```csharp
int num6 = Gen.HashCombineInt(PlanetTile.op_Implicit(map.Tile), faction?.loadID ?? 0);
num6 = Gen.HashCombineInt(num6, (Find.TickManager != null) ? Find.TickManager.TicksGame : 0);
Rand.PushState(num6);
try { return Mathf.RoundToInt(Rand.Range(num4, num5) / 2500f) * 2500; }
finally { Rand.PopState(); }
```

And its scheduling state IS saved (`nextMapIncursionTickByKey`, `processedMapEntryKeys` are `ExposeData`'d).

### 3b. Caravan interception

`CaravanTerritoryIncidents` postfixes `Caravan_PathFollower.TryEnterNextPathTile` — i.e. **every time a
player caravan steps onto a new world tile**, it checks who claims that tile and rolls for an incident
weighted by the `CaravanIncidentEntryDef`s:

```csharp
if (!TerritoryOwnershipCache.TryGetClaimingFactions(PlanetTile.op_Implicit(((WorldObject)val).Tile), tmpFactionIds)
    || !CaravanIncidentUtility.CanFireIncidentWhichWantsToGenerateMapAt(((WorldObject)val).Tile))
    return;
...
if (!(num4 <= 0f) && Rand.Chance(num4))
{
    Candidate candidate = WeightedRandomCandidate(list);
    if (candidate != null && TryFireIncident(val, candidate.incident, candidate.faction)) ...
}
```

The mod then **forces the incident's faction to be the territory owner** rather than a random enemy,
via a scoped override plus four Harmony patches on `FactionManager.RandomEnemyFaction`,
`RandomRaidableEnemyFaction`, `TryGetRandomNonColonyHumanlikeFaction`, and three on
`IncidentWorker_Ambush_EnemyFaction`:

```csharp
forcedAmbushFactionIdByCaravanId[((WorldObject)caravan).ID] = faction.loadID;
```

Ships two `CaravanIncidentEntryDef`s out of the box (`Defs/CaravanIncidents.xml`) — `Ambush` (weight
15, hostile factions only) and `CaravanMeeting` (weight 10, any tech level) — with a flag filter enum
(`Hostile / Neutral / NeutralAndAllied / Allied / Royalty / Animal / Neolithic … Archotech`). This is
an **extension point**: you can add your own entries in XML.

### 3c. Invasions — AI factions actually fight each other over territory

This is the strongest "factions are forces in the world" system in the mod and it is **entirely
territory-driven**. `FactionTerritories.Invasions` (~3,200 lines) adds an `FT_BaseInvasion` world
object. An invasion can only be created where a **rival faction's territory overlaps the defender's
tile** — i.e. on contested ground:

```csharp
// Invasions/Utility.cs:185-211 — FindEligibleAttackers
if (!TerritoryOwnershipCache.TryGetClaimingFactions(PlanetTile.op_Implicit(((WorldObject)settlement).Tile), tmpFactionIds))
    return list;
for (int i = 0; i < tmpFactionIds.Count; i++)
{
    int num = tmpFactionIds[i];
    if (num != ((WorldObject)settlement).Faction.loadID)
    {
        Faction val = ResolveFaction(num);
        if (val != null && !val.IsPlayer && !val.Hidden && !val.temporary
            && FactionUtility.HostileTo(val, ((WorldObject)settlement).Faction) && IsValidCombatFaction(val))
            list.Add(val);
    }
}
```

**Settlements genuinely change hands.** `ApplyWinnerToSettlement` either destroys and re-creates the
world object under the winner's faction (off-map, name preserved) or just `SetFaction`s it (on-map),
then invalidates the territory map:

```csharp
// Invasions/Utility.cs:808-848
worldObjects.Remove((WorldObject)(object)settlement);
WorldObject obj = WorldObjectMaker.MakeWorldObject(def);
((WorldObject)val).Tile = PlanetTile.op_Implicit(num);
((WorldObject)val).SetFaction(winner);
val.Name = name;
worldObjects.Add((WorldObject)(object)val);
...
FactionTerritoriesUtility.RequestRegenerate(clearCache: true);
```

Resolution has three paths — on-map extinction, on-map-closure by summed `combatPower`, and off-map
timeout — with a tech-level weight table and a **1.15× defender bias**:

```csharp
float attackerWeight = Mathf.Max(0.01f, currentFactionStrength)  * GetTechWeight(val);
float defenderWeight = Mathf.Max(0.01f, currentFactionStrength2) * GetTechWeight(val2) * 1.15f;
```

The roll is properly seeded (this is the mod's best-written RNG):

```csharp
// Invasions/Utility.cs:685-696
int num2 = Gen.HashCombineInt(tile, attacker.loadID);
num2 = Gen.HashCombineInt(num2, defender.loadID);
num2 = Gen.HashCombineInt(num2, (Find.TickManager != null) ? Find.TickManager.TicksGame : 0);
Rand.PushState(num2);
try { if (Rand.Value < attackerWeight / num) return attacker; return defender; }
finally { Rand.PopState(); }
```

**The player can join as a genuine third party.** `Patches_GetFloatMenuOptions` strips the vanilla
"Attack" option while an invasion is live and substitutes "Join fight"; neither side's `LordJob`
targets the player specifically. Helping the defender win earns a deferred `+30` goodwill paid on map
exit (`invasion.rewardGoodwillOnExit`). `Patches_CheckDefeated` blocks vanilla
`SettlementDefeatUtility.CheckDefeated` so an NPC-vs-NPC fight is not miscounted as a player conquest.

### 3d. Expansion — factions grow into their own borders

`FactionTerritories.Expansion` (~1,100 lines) adds `FT_SettlementConstruction`, a site that matures
into a real `Settlement` after `settlementConstructionDurationTicks`, which then projects new
territory. **Site selection respects borders and stays well inside them.** The algorithm
(`Expansion/Utility.BuildApproximateConstructionCandidates`) is: collect all tiles the faction claims →
find frontier tiles (owned, with ≥1 non-owned neighbour) → subsample ≤24 frontier origins with a
faction-id-derived phase offset → BFS **inward, never leaving own territory**, accepting tiles whose
hop distance falls in the band `[radiusSteps/2, radiusSteps]`:

```csharp
int num2 = ... Settings.radiusSteps : 5;
int num3 = Mathf.Max(1, Mathf.RoundToInt((float)num2 * 0.5f));
int num4 = Mathf.Max(num3, num2);
...
if (num9 >= num3 && num9 <= num4 && hashSet2.Add(num8) && IsValidConstructionCandidate(num8)) { ... }
...
if (hashSet.Contains(num10) && !dictionary.ContainsKey(num10))   // never leaves own territory
```

Validity checks are thin: no blocking world object, and ≥3 traversal steps from any vanilla
settlement. **No biome, hilliness or water check** — water is excluded only as a side effect of
`BuildFactionMap` skipping water tiles, so turning on `includeWaterTiles` lets factions build on ocean.

Defenders of a construction site are a **trader caravan**, not a raid
(`groupKind = PawnGroupKindDefOf.Trader`, `LordJob_DefendAttackedTraderCaravan`) — attacking one is a
banditry beat, not a siege. Both systems are toggleable (`enableInvasions`,
`enableSettlementConstruction`).

### What is NOT real

No tolls. No safe-passage / permission mechanic. No caravan pathing preference or avoidance. No
territory-based trade or diplomacy modifiers. No ownership *dispute* resolution — "contested" is a
render state and an incident-source multiplier, nothing arbitrates it. Territory does not gate
settlement placement for the player.

---

## 4. Vassalage — the whole mechanic

**This is the section that matters most, and it is where the mod under-delivers relative to its name.**

### 4a. Direction: one-way only

There is no path by which the player becomes anyone's vassal. Grep the entire assembly: the player is
always the master.

```csharp
((WorldObject)factionTerritories_VassalOutpost).SetFaction(Faction.OfPlayer);
factionTerritories_VassalOutpost.SetOriginalFaction(faction);
```

`FactionTerritories_VassalOutpost.MasterFactionLoadIDString` is a misleading name — it returns
`originalFactionLoadID`, i.e. the *conquered* faction, used as the ledger key for points. The owner is
hard-coded to `Faction.OfPlayer`.

**There is no losing-at-politics path here.** If that is the design goal, this mod does not supply it.

### 4b. The state machine

```
                       ┌─────────────────────────────────────────┐
                       │  AI Settlement (any non-player faction) │
                       └───────────────┬─────────────────────────┘
              ┌────────────────────────┴────────────────────────┐
       PATH A: CONQUEST                                  PATH B: PURCHASE
              │                                                 │
   player raids & clears the map                    select settlement on world map
              │                                                 │
   MapDeiniter.Deinit postfix fires                 Settlement.GetGizmos postfix adds
   (ShowVassalisePromptOnMapRemovedPatch)           "Vassalise" Command_Action
              │                                                 │
   PendingVassaliseDecision registered              Dialog_VassaliseSettlement
   in VassaliseComponent (SAVED)                              │
              │                                    CanPurchaseVassaliseSettlement:
   ChoiceLetter_VassaliseDestroyedSettlement          PlayerGoodwill >= cost (default 50)
   + Find.TickManager.Pause()                                 │
   + OpenLetter()                                   TryAffectGoodwillWith(-cost)
              │                                                 │
      ┌───────┼────────┬──────────────┐                        │
   Accept  Decline   (ally variant)   │                        │
      │       │      cede to ally     │                        │
      ▼       ▼          ▼            │                        ▼
  ExecuteVassalisationAtTile   ExecuteCedeDestroyedSettlementToFaction    ExecuteVassalisation
      │                            │                                          │
      └────────────┬───────────────┘                                          │
                   ▼                                                          ▼
      ┌───────────────────────────────────────────────────────────────────────────┐
      │  FT_VassalOutpost world object on the tile, Faction = OfPlayer,            │
      │  originalFactionLoadID = conquered faction (the points ledger key)         │
      │  → registered with VassaliseComponent.AddOutpost                           │
      │  → RequestRegenerate(clearCache: true)                                     │
      │  → counts as a territory anchor, so it now projects PLAYER territory       │
      └───────────────────────────────┬───────────────────────────────────────────┘
                                      ▼
              VassalagePointsComponent.GameComponentTick, once per in-game day
              points[originalFactionId] += vassalagePointsPerDay × techLevelMultiplier
                                      ▼
              Gizmo "Vassalage" on the outpost → Dialog_Vassalage
                          ┌───────────┼───────────┐
                        Pawns       Items       Roads (if Roads of the Rim present)
```

### 4c. How you become a master — path A, conquest

`ShowVassalisePromptOnMapRemovedPatch` postfixes `MapDeiniter.Deinit`. When you leave a map whose
parent is a `DestroyedSettlement` and a pending decision was registered:

```csharp
comp.MarkPromptShown(((WorldObject)val).ID);
ChoiceLetter_VassaliseDestroyedSettlement choiceLetter = new ChoiceLetter_VassaliseDestroyedSettlement(pendingDecisionForDestroyedSettlement) { def = LetterDefOf.NeutralEvent };
Find.LetterStack.ReceiveLetter((Letter)choiceLetter, null, 0, true);
Find.TickManager.Pause();
((Letter)choiceLetter).OpenLetter();
```

The mod is aggressive about making you answer. `VassaliseComponent.GameComponentTick` **force-pauses
the game every tick and re-opens the letter every 30 ticks** until the decision is resolved:

```csharp
if (!forcedPauseActive) { forcedPauseActive = true; speedBeforeForcedPause = Find.TickManager.CurTimeSpeed; }
Find.TickManager.Pause();
int ticksGame = Find.TickManager.TicksGame;
if (ticksGame >= lastForceOpenTick + 30)
{
    lastForceOpenTick = ticksGame;
    ChoiceLetter_VassaliseDestroyedSettlement letter = FindExistingLetterForTile(decision.tileId);
    if (letter != null) ((Letter)letter).OpenLetter();
}
```

That behaviour would be actively hostile in a two-player co-op session — one player's unanswered
prompt hard-pauses the shared game and re-raises a modal window twice a second.

The decision itself is properly persisted (`PendingVassaliseDecision : IExposable`, saved via
`Scribe_Collections.Look(ref pendingDecisionsByDestroyedSettlementId, ...)`), so it survives a save/load.

**Three-way choice when an ally helped:** if `alliedFactionLoadId >= 0`, the letter offers
"leave the base to them" (cede — spawns a `Settlement` for the ally) vs "vassalise it for yourself",
each with its own configurable goodwill delta:

```csharp
Text = "You helped " + (alliedFactionName ?? "an allied faction") + "capture this settlement.\n\n"
     + "You can leave the base to them" + GoodwillSentence(alliedFactionGoodwillOnCede)
     + ", or vassalise it for yourself" + GoodwillSentence(alliedFactionGoodwillOnVassalise) + ".";
```

This is the single most interesting design beat in the mod: taking the prize costs you standing with
the ally who bled for it. (Note the missing space in `+ "capture this settlement"` — the mod's polish
level is uneven.)

### 4d. How you become a master — path B, purchase

`Settlement_GetGizmos_Vassalise` postfixes `Settlement.GetGizmos` and adds a buy button. The cost is
**goodwill, not silver or military effort**:

```csharp
public static int GetSettlementVassaliseGoodwillCost()
{
    var s = FactionTerritoriesMod.Instance?.Settings;
    return (s != null) ? Mathf.Clamp(s.settlementVassaliseGoodwillCost, 10, 100) : 50;
}

public static bool CanPurchaseVassaliseSettlement(Settlement settlement, out string failReason)
{
    ...
    int cost = GetSettlementVassaliseGoodwillCost();
    int playerGoodwill = faction.PlayerGoodwill;
    if (playerGoodwill < cost)
    {
        failReason = "Requires " + cost + " goodwill with " + faction.Name + ". Current goodwill: " + playerGoodwill + ".";
        return false;
    }
    ...
}
```

At 50 goodwill default and a 100 goodwill ceiling in vanilla, **an ally at max goodwill can have a
settlement peeled off them for half their affection, repeatedly, with no war, no siege, no consent
check.** No `Settlement` count guard, no distance requirement, no cooldown. This is the weakest
mechanic in the mod by a wide margin and I would disable it outright.

### 4e. What vassalage grants — the obligations flow only one way

The vassal owes you a per-day tribute stream:

```csharp
public override void GameComponentTick()
{
    int ticksGame = Find.TickManager.TicksGame;
    if (ticksGame >= lastTickUpdated + 60000)   // 60000 ticks = 1 in-game day
    {
        lastTickUpdated = ticksGame - ticksGame % 60000;
        if (VassaliseComponent.TryGet(out var comp)) UpdatePointsFromVassals(comp, ticksGame);
    }
}
```

```csharp
int num = factionTerritoriesSettings?.vassalagePointsPerDay ?? 100;
...
TechLevel tl = ResolveFactionTechLevelSafe(masterFactionLoadIDString);
int techLevelMultiplierPercent = factionTerritoriesSettings.GetTechLevelMultiplierPercent(tl);
num4 = (float)techLevelMultiplierPercent / 100f;
int num5 = (int)Math.Floor((float)(num3 * num) * num4);
if (num5 > 0) AddPoints(masterFactionLoadIDString, num5);
```

100 points/day per outpost, scaled by the conquered faction's tech level. Points are banked
**per original faction**, so vassals of the same faction pool into one purse. Saved via
`Scribe_Collections.Look(ref pointsByFactionId, ...)`.

Points buy exactly four things.

**(1) Raw silver tribute.** 1 point → 1 silver, dropped at the home map:

```csharp
int num = Math.Min(points, maxSilverToDrop);
...
pointsByFactionId[factionLoadID] = points - num;
...
GenPlace.TryPlaceThing(val2, val, anyPlayerHomeMap, (ThingPlaceMode)1, ...);
Messages.Message("Received " + num + " silver tribute.", MessageTypeDefOf.PositiveEvent, false);
```

**(2) Colonists** — generated from the vassal faction's own pawnkinds, priced on combat power:

```csharp
float num = (FactionTerritoriesMod.Instance?.Settings)?.colonistCostMultiplierThreatPoints ?? 50f;
num = Mathf.Clamp(num, 0.5f, 100f);
Widgets.Label(..., "Cost = combat power × " + num.ToString("0.0") + " + average equipment cost x " + 1f.ToString("0.0"));
...
int num3 = Mathf.Max(1, Mathf.RoundToInt(num2 * num));         // combatPower × multiplier
num4 = ((FloatRange)(ref val.apparelMoney)).Average;
num5 = ((FloatRange)(ref val.weaponMoney)).Average;
int cost = num3 + Mathf.Max(0, Mathf.CeilToInt((num4 + num5) * 1f));
```

```csharp
Pawn pawn = PawnGenerator.GeneratePawn(val2);
Find.LetterStack.ReceiveLetter((Letter)(object)new ChoiceLetter_VassalPurchasedPawn(pawn), null, 0, true);
```

The offer letter then lets you take them as **colonist or slave**. This is the closest thing to the
"pawn loans" idea — but it is a permanent purchase, not a loan, and the pawn is generated by
`PawnGenerator.GeneratePawn` in the button handler (see §6, this is a hard desync).

**(3) Items**, restricted to what that faction's traders would actually stock — a nice touch:

> "Items are restricted to what this faction would sell at its settlements. Purchased items arrive by drop pods."

`TraderSellablesUtility` walks the faction's `TraderKindDef` `StockGenerator`s to build the catalog;
`BuildSettlementSimCatalog` caches it per faction for 60000 ticks. Price is `1 point per silver of
market value` (`private const float ItemPointsPerSilver = 1f;`). Delivery is a real drop pod
(`DropThingsSinglePod`) or into an adjacent caravan.

**(4) Road construction progress**, iff Roads of the Rim is installed
(`VassalRoadProgressComponent.RoadsOfTheRimAvailable`). Points are invested into the vassal faction's
road build queue, tile by tile. This is a genuinely nice "standing buys infrastructure" idea and the
only reward that is not fungible with silver. The whole 1,521-line component is reflection-driven
interop against Roads of the Rim internals (`TryDiscoverRoadPlanSnapshotForFaction`,
`TryExtractRoadPlanFromObject`, `TryReadTilesFromDictionary`) — i.e. brittle.

### 4f. Obligations imposed on the player, and how vassalage ends

**No obligations. One exit, and only if you enable a different subsystem.**

There is no upkeep, no unrest, no rebellion timer, no loyalty stat, no decay. Nothing about holding a
vassal costs you anything, and nothing makes it stop paying.

> **Correction to an earlier read of mine:** the vassal *can* be taken from you, but only via the
> Invasions subsystem, not via anything in the Vassalise namespace. `Invasion` has a
> `vassalOutpostId` field and a `TargetsVassal` mode; `FindEligibleAttackersForVassalOutpost`
> (`Invasions/Utility.cs:230`) selects territory claimants **hostile to the player**. Because the
> outpost is not a `MapParent`, the mod fabricates a temporary `Settlement` under a neutral "proxy"
> faction just to have something to generate a battle map from
> (`GetOrCreateVassalBattleSettlement`, `:1181-1219`). If the attacker wins:
>
> ```csharp
> // ApplyWinnerToVassalOffMap, Invasions/Utility.cs:865-902
> // deletes the outpost and spawns a fresh Settlement owned by the attacker,
> // carrying outpost.originalSettlementName
> ```
>
> So: **turn `enableInvasions` off and a vassal is permanent and free. Turn it on and holding
> vassals in hostile territory is a standing liability.** That is a real, if accidental, tension —
> and it is the only thing resembling an obligation in the whole mechanic.

The outpost is still not a `MapParent`. You cannot land on it, garrison it, or build on it. Absent an
invasion it is a pin on the world map that emits 100 points a day forever.

### 4g. Honest summary of the mechanic

| Design goal | Delivered? |
|---|---|
| Losing-at-politics path / becoming someone's vassal | **No.** Player-as-master only. |
| Standing buys non-material things | **Partly.** Roads yes; pawns are a purchase not a loan; items and silver are straightforwardly material. |
| Granted sites | **No.** You take sites; nobody grants you one. |
| Tech transfer | **No.** No research interaction anywhere. |
| A story rather than a soft loss screen | **No.** It is an income multiplier with a shop UI. |
| Obligations / a relationship that can go wrong | **Barely.** No decay, no upkeep. The only way to lose a vassal is an AI invasion, and only if `enableInvasions` is on. |

The one narrative beat worth stealing outright is **4c's ally-cede dialog** — "you and your ally both
bled for this; taking it costs you their trust." That is a story. The rest is a spreadsheet.

---

## 5. How the two mods couple

**Hard dependency, declared, and structurally deep — but the interesting half of FT does not touch MMF.**

`About/About.xml`:

```xml
<modDependencies>
  <li>
    <packageId>NozoMe.MapModeFramework</packageId>
    <displayName>Map Mode Framework</displayName>
    ...
  </li>
</modDependencies>
<loadAfter>
  <li>NozoMe.MapModeFramework</li>
  <li>Torann.RimWar</li>
</loadAfter>
```

Coupling surfaces:

1. **Compile-time inheritance.** `MapMode_FactionTerritories : MapMode_Region` (which is
   `MapMode_Cached : MapMode`). FT's assembly will not load without MMF's.
2. **A `MapModeDef` in `Defs/Regions.xml`** referencing `MapModeFramework.MapModeDef`,
   `worldLayerClass = MapModeFramework.WorldLayer_MapMode_Region`.
3. **Two Harmony patches into MMF** to let FT hide MMF's own toolbar
   (`[HarmonyPatch(typeof(MapModeComponent), "GameComponentUpdate")]` and
   `[HarmonyPatch(typeof(MapModeUI), "DoWindowContents")]`, both gated on
   `settings.hideMapModeFrameworkToolbar`) — FT wants to be the only map mode you see.
4. **Reflection over MMF's internals**, which is the tell that the author expected MMF's API to
   change under him:

```csharp
cachedRegionType = AccessTools.TypeByName("MapModeFramework.MMFRegion")
                ?? AccessTools.TypeByName("MMFRegion")
                ?? AccessTools.TypeByName("MapModeFramework.Region")
                ?? AccessTools.TypeByName("MapModeFramework.MapRegion");
```

```csharp
cachedRegionsField = AccessTools.Field(typeof(MapMode_Region), "regions");
if (cachedRegionsField == null)
{
    cachedRegionsField = typeFromHandle.GetFields(...).FirstOrDefault((FieldInfo f) =>
        typeof(IList).IsAssignableFrom(f.FieldType) && f.FieldType.IsGenericType
        && f.FieldType.GetGenericArguments()[0].Name.IndexOf("Region", StringComparison.OrdinalIgnoreCase) >= 0);
}
```

And `TryBuildRegionCtorArgs` is a 150-line **heuristic constructor matcher** that guesses which
`Material` / `Color` / `float` parameter is which by inspecting parameter *names* for substrings
`"border"`, `"fill"`, `"width"`, `"alpha"`:

```csharp
bool flag  = !GenText.NullOrEmpty(text2) && (text2.Contains("border") || text2.Contains("edge") || text2.Contains("outline"));
bool flag2 = !GenText.NullOrEmpty(text2) && (text2.Contains("fill") || text2.Contains("body") || text2.Contains("region") || text2.Contains("area"));
```

That is genuinely fragile — it silently produces a wrong-looking region rather than an error if MMF
renames a ctor parameter, exactly the failure class CLAUDE.md warns about.

**But:** `TerritoryOwnershipCache.cs`, `FactionTerritoriesUtility`'s hash/seed/neighbour helpers,
`GameComponent_FactionTerritories` (incursions), and `CaravanTerritoryIncidents` (interception)
contain **no MMF references whatsoever**. The dependency is confined to the rendering half.

---

## 6. MP determinism verdict

**Neither mod has any Multiplayer awareness.** Verified by grep across both trees and the raw DLL:
zero hits for `Multiplayer`, `[SyncMethod]`, `MP.IsInMultiplayer`, or any compat shim.

### Map Mode Framework — CAUTION (cosmetically safe, structurally hostile)

| Finding | Class |
|---|---|
| No `Rand.*` anywhere in the source tree | SAFE |
| No writes to game state; all patches are render/UI suppression or `WorldSelector` override | SAFE |
| `MapModeComponent.ExposeData` saves only `List<MapModeDef>` — no sim state | SAFE |
| `EdgesCache.cachedEdges`, `RegionCache<T>.cachedRegions` static dictionaries | SAFE — geometry only, never read by sim |
| `MapMode_Cached.MapModeOnGUI` reads `DateTime.Now - WorldRegenHandler.startTime` | SAFE — drives a nag label only |
| `Task.Run(() => PrepareMeshes(...))` reads `Find.WorldGrid` and iterates `Regions` off the main thread | **SUSPECT** — not a determinism bug, but a data race against the sim thread. If Archinity ever mutates `Region.tiles` from a tick while a regen task is running, you get a torn read / `InvalidOperationException` under load, and MP's tick pacing makes that more likely, not less. |
| `Core.KillAllAsyncProcesses()` is `async void` in a Harmony `Prefix` on `ClearAllMapsAndWorld` | **SUSPECT** — fire-and-forget across a world teardown |

**Verdict: MMF alone will not desync you.** It is a viewer. Its risk is stability, not divergence.

### Faction Territories and Vassalage — WILL DESYNC

**The territory algorithm itself is the mod's strongest MP asset.** Genuinely deterministic:
hash-seeded from the world seed, integer edge costs, total ordering on the heap comparator, sources
canonically sorted, no `Rand`. Two clients with identical settings produce byte-identical territory.

Everything built on top of it is unsafe. Ranked:

#### DESYNC RISK #1 — a UI window invalidates the cache that gates the simulation

This is the subtlest and probably the *first* desync you would actually hit, because it needs no
combat and no vassalage — just one player opening a settings or colour window.

```csharp
// FactionTerritoriesUtility.cs:260
public static void RequestRegenerate(bool clearCache)
{
    if (clearCache)
    {
        TerritoryOwnershipCache.MarkDirty();      // <-- the sim-gating cache
        try { VassalisationCaches.ClearAll(); } catch { }
        InvalidateContestedVisualCaches();
    }
    GameComponent_FactionTerritories.NotifyWorldChanged(clearCache);
}
```

Callers include **pure client-local UI**: `Dialog_FactionTerritoryColor.cs:146` (the territory colour
picker) and `FactionTerritoriesMod.cs:401` / `:641` (the mod settings window). `MarkDirty()` forces
the next `EnsureCache` to rebuild, which **increments the static `revision` counter** — and `revision`
is never saved and is what downstream simulation caches key against:

```csharp
// Expansion/Utility.cs:29
private static readonly Dictionary<int, ConstructionTileCache> constructionTileCacheByFactionId = ...;

// Expansion/Utility.TryFindConstructionTile
int num = TerritoryOwnershipCache.TryGetRevisionUnsafeForMainThreadOnly();
if (constructionTileCacheByFactionId.TryGetValue(faction.loadID, out var value))
{
    if (value != null && value.ownershipRevision == num && TryPickValidCachedCandidate(value.candidateTiles, out result))
        return true;
}
```

and the pick is a bare global `Rand` indexed into that per-client list:

```csharp
// Expansion/Utility.cs:43
int num = Rand.Range(0, cachedCandidates.Count);
for (int i = 0; i < cachedCandidates.Count; i++)
{
    int index = (num + i) % cachedCandidates.Count;
```

**Chain:** player A opens the colour dialog → A's `revision` advances, B's does not → A rebuilds
candidates, B reuses stale ones → `Rand.Range(0, count)` draws over lists of *different length and
content* → the AI builds its next settlement on a different tile on each client, **and** the global
`Rand` stream advances a different number of steps. Both a state divergence and a stream divergence
from one UI click.

#### DESYNC RISK #2 — unsynced world mutation from UI callbacks

Every vassalage action mutates shared game state directly from a `Command_Action.action`, a
`DiaOption` callback, or a `Widgets.ButtonText` handler. Only the clicking client executes it.

```csharp
// Dialog_Vassalage.TryBuyColonist — from a button click
Pawn pawn = PawnGenerator.GeneratePawn(val2);
Find.LetterStack.ReceiveLetter((Letter)(object)new ChoiceLetter_VassalPurchasedPawn(pawn), null, 0, true);
```

`PawnGenerator.GeneratePawn` makes hundreds of `Rand` calls. Firing it on one client only both
diverges the shared RNG stream **and** creates a pawn that does not exist on the other client. This
is the single worst offender in the mod.

```csharp
// VassaliseUtility.ExecuteVassalisation — from a gizmo / letter choice
worldObjects.Remove((WorldObject)(object)settlement);
...
((WorldObject)factionTerritories_VassalOutpost).SetFaction(Faction.OfPlayer);
worldObjects.Add((WorldObject)(object)factionTerritories_VassalOutpost);
```

```csharp
// VassaliseUtility.TryPurchaseVassalisation — from a gizmo
faction.TryAffectGoodwillWith(Faction.OfPlayer, -settlementVassaliseGoodwillCost, true, true, null, null);
```

```csharp
// VassalagePointsComponent.TrySpendAllForSilverTribute — from a button click
pointsByFactionId[factionLoadID] = points - num;
GenPlace.TryPlaceThing(val2, val, anyPlayerHomeMap, (ThingPlaceMode)1, ...);
```

```csharp
// Dialog_Vassalage.TryBuyItem → DropThingsSinglePod — from a button click
```

Also `DropCellFinder.TryFindDropSpotNear` and `TryFindShopDropSpot` are `Rand`-driven cell finders
invoked from the same UI path.

#### DESYNC RISK #3 — unordered collections feed `Rand`-indexed picks

`TryGetClaimingFactions` hands out a `HashSet<int>` verbatim:

```csharp
// TerritoryOwnershipCache.cs:193-198
if (!factionsByTile.TryGetValue(tile, out var value) || value == null || value.Count == 0) return false;
outFactionIds.AddRange(value);   // value is HashSet<int> — enumeration order is not contractual
```

That order is preserved through `Invasions/Utility.FindEligibleAttackers` into an index-based pick:

```csharp
// Invasions/Component.cs:184-189
Candidate candidate = GenCollection.RandomElement<Candidate>((IEnumerable<Candidate>)list);
...
Faction val2 = GenCollection.RandomElement<Faction>((IEnumerable<Faction>)candidate.attackers);
```

Same index, different order → **different faction attacks**. Same pattern feeds
`CaravanTerritoryIncidents.BuildCandidates` → `WeightedRandomCandidate` (`Rand.Value`, line 447), and
`Expansion/Utility.cs:74-124` builds its candidate list by iterating `factionMap` (a `Dictionary`)
directly, so dictionary order determines the strided frontier sample that #1 then indexes into.

**Fix in any reimplementation: sort every claimant list before anything random touches it.**

#### DESYNC RISK #4 — unsaved static caches gating a `Rand` roll inside a tick path

```csharp
// CaravanTerritoryIncidents.cs:195-201  — static, NOT ExposeData'd anywhere
private static readonly Dictionary<int, int> lastIncidentTickByCaravanId        = new Dictionary<int, int>();
private static readonly Dictionary<int, int> lastIncidentAttemptTickByCaravanId = new Dictionary<int, int>();
private static readonly Dictionary<int, int> forcedMeetingFactionIdByCaravanId  = new Dictionary<int, int>();
private static readonly Dictionary<int, int> forcedAmbushFactionIdByCaravanId   = new Dictionary<int, int>();
```

These gate the roll in the `Caravan_PathFollower.TryEnterNextPathTile` postfix:

```csharp
if (IsOnCooldown(lastIncidentAttemptTickByCaravanId, ((WorldObject)val).ID, num, cooldownTicks)) return;
lastIncidentAttemptTickByCaravanId[((WorldObject)val).ID] = num;
...
if (!(num4 <= 0f) && Rand.Chance(num4)) { ... }
```

Because they are static and never serialised, they are empty on a client that has just joined (MP
joins by loading a save) while the host's are populated. The client is off cooldown, the host is on
→ the client fires a `Rand.Chance` the host does not → RNG streams diverge on the very next caravan
step. **This one will bite within minutes of a mid-session join.**

#### DESYNC RISK #5 — a Harmony prefix that *skips* a `Rand`-consuming vanilla method

This is the amplifier that converts any of the above from a contained difference into total stream
divergence:

```csharp
// Patch_FactionManager_RandomEnemyFaction_ForceAmbushFaction.cs:18-31
if (ForcedAmbushFactionScope.TryGet(out var f) && f != null)
{
    __result = f;
    return false;      // vanilla RandomEnemyFaction never runs -> its Rand calls never happen
}
```

Same shape in `Patch_FactionManager_RandomRaidableEnemyFaction_*` and
`Patch_FactionManager_TryGetRandomNonColonyHumanlikeFaction_*`. The scope is pushed from
territory-derived state, so whenever it is active on one client and not the other, **the global `Rand`
stream advances a different number of steps** and every subsequent roll in the entire game diverges.

#### DESYNC RISK #6 — mod settings feed the simulation

`ComputeSettingsHash` shows territory depends on nine settings values; incursion cadence depends on
`territoryMapIncursionIntervalTicks` / `...RandomisationPercent`; incident weights depend on
`caravanIncidentWeightOverrides`; the vassalage economy depends on `vassalagePointsPerDay` and the
tech-level multiplier table. This is exactly the failure mode CLAUDE.md flags:

> Both players need identical mods, identical load order **and identical mod settings**.

Here it is not a subtle divergence — a `radiusSteps` mismatch means the two clients disagree about
who owns which tile, and therefore about who raids you.

#### SUSPECT — but probably fine

- `GameComponent_FactionTerritories.GameComponentTick` → `RollMapEntryIncursions` → `Rand.Chance` /
  `PawnGroupMakerUtility.GeneratePawns`: this is on the synced tick path, its scheduling state IS
  saved, and `RollRandomisedIntervalTicks` uses explicit `Rand.PushState(hash)` / `PopState()`.
  This one is written correctly. It only diverges if the territory map underneath it diverges.
- `TerritoryOwnershipCache` static caches: they are a *pure function* of world state + settings, so
  a rebuild at a different wall-clock moment yields the same answer. The `revision` counter differs
  per client but is only read by the renderer.
- `MapMode_FactionTerritories` uses `Find.TickManager.TicksGame` as a dedupe key
  (`lastQueuedTick`, `lastCtorChoiceLogTick`) from worker-thread code — render-only.
- `FactionTerritories_VassalOutpost` icon caches use `lock (iconCacheLock)` — `Texture2D` only.
- `Invasions/Utility.RollWinner` and the three `Roll*ExpansionTick` methods are the *correctly done*
  examples: `Rand.PushState(Gen.HashCombineInt(...synced world state...))` with a `finally { PopState(); }`.
  Steal this pattern.
- `Expansion/Component.cs:214` — `RollNextInvasionTick` is the one sibling that **omits** the
  push/pop and consumes the global stream unseeded. Inconsistent with the surrounding style; looks
  like an oversight rather than a decision.
- `CollapseInfluenceMap` breaks an exact influence tie on `Dictionary` enumeration order
  (`TerritoryOwnershipCache.cs:410-427`, strict `>`). Insertion order derives from the deterministic
  sorted heap above it so it is *probably* identical across clients — but it is the one place in an
  otherwise carefully deterministic algorithm where the guarantee comes from a .NET implementation
  detail rather than from the code. **Sort before collapsing in any reimplementation.**
- `FactionTerritoriesUtility.ProcessPendingMainThreadActions` drains a `ConcurrentQueue<Action>` from
  `GameComponentTick`, so *which tick* a queued action lands on depends on worker-thread completion
  time — wall-clock, not tick count. Currently only region meshes go through it, so it is cosmetic;
  but it is a live wall-clock→tick channel and anything added to that closure later is an instant desync.
- `Expansion/Component.ExposeData` rolls new expansion schedules during `PostLoadInit`, seeded on
  `factionId` alone with the un-seeded `now` added afterwards. A mid-session MP joiner loads at a
  different `TicksGame` than the host did → different absolute schedules per client.
- `Prefs.DevMode` gates `DevVassalagePointsUtility` (which grants points — real sim state) and the
  `DevTools` / `DevTools_Vassal` gizmos (which create invasions via `RandomElement` from a
  `Command_Action`). `Prefs` is per-client. Dev-only, but worth knowing before someone opens dev mode
  mid-session to debug something.

#### The forced pause

```csharp
Find.TickManager.Pause();
```

called unconditionally from `VassaliseComponent.GameComponentTick` whenever a prompt is unresolved.
In MP, time speed is a synced concept; a per-client tick calling `Pause()` directly will at minimum
fight the MP time-control layer, and the accompanying `OpenLetter()` every 30 ticks throws a modal
window in *both* players' faces. Whichever player clicks first mutates the world unsynced.

### Bottom line

One more structural offender worth calling out — map generation and pawn generation dispatched
through a client-local long event rather than the tick loop:

```csharp
// Invasions/Patches_Attack.cs:24-27
LongEventHandler.QueueLongEvent((Action)delegate { Utility.Enter(caravan, settlement, invasion); },
    "GeneratingMapForNewEncounter", false, null, true, false, null);
```

`Utility.Enter` generates the map, runs `PawnGroupMakerUtility.GeneratePawns`, calls
`RCellFinder`/`CellFinder`, and mutates `invasion.enteredMap` / `attackerRaidSpawned`.

| Mod | Verdict |
|---|---|
| Map Mode Framework | **Usable with caution.** Pure viewer, zero live `Rand` (the only matches are commented out), no sim writes. Its threads compute mesh/material/border data consumed only by `Render`. Watch the async workers if you ever mutate `Region.tiles` from a tick. |
| Faction Territories and Vassalage | **Do not ship as-is.** Six independent desync vectors, at least one of which (#1) fires from opening a settings window. Fixing it means: rebuild `EnsureCache` on a fixed tick cadence instead of on `MarkDirty`; sort every claimant/candidate list before any `Rand` touches it; `ExposeData` four static dictionaries; route ~12 UI entry points through synced methods; remove settings from `ComputeSettingsHash`; move `Patches_Attack` off `LongEventHandler`. That is a fork, not a patch. |

Also note the CLAUDE.md rule this violates for Archinity specifically: `Archinity.Altar` is meant to
be the *only* Harmony assembly. FT adds a second one with 20+ patches, several of them on
`FactionManager` and `IncidentWorker` internals.

---

## 7. Minimum viable "territory that matters"

**Yes, the sim and the rendering are cleanly separable — the seam is already there.**

### The sim without the renderer

`FactionTerritories/TerritoryOwnershipCache.cs` is 553 lines and imports only
`System`, `System.Collections.Generic`, `System.Linq`, `RimWorld`, `RimWorld.Planet`, `UnityEngine`,
`Verse`. **No `using MapModeFramework`.** Its only external dependencies are five helpers in
`FactionTerritoriesUtility`:

- `GetDeterministicSeed(settings)` — world-seed hash
- `HashInt` / `HashCombine` / `HashCombine3` / `Noise01` — pure xorshift, ~15 lines total
- `GetNeighborsInt(tile, outList)` — thin wrapper over `WorldGrid.GetTileNeighbors`
- `EdgeMovementDifficultyNoWinter(grid, from, to, settings)` — terrain cost
- `IsValidTerritorySource` / `IsTerritoryAnchorWorldObject` — what counts as an anchor

A minimum viable Archinity implementation is roughly **250–350 lines**:

```
TerritoryMap (static or WorldComponent)
  ├─ Sources: every Settlement (+ your own anchor types), sorted by (factionId, tile, seed)
  ├─ Seed: GenText.StableStringHash(Find.World.info.seedString)   // NOT Rand
  ├─ Dijkstra: min-heap, integer costs (movementDifficulty × 100),
  │            comparator MUST tiebreak to (dist, hash, sourceIndex, tile)
  ├─ Collapse: plurality wins outright, else the tile is contested
  ├─ Query:   TryGetClaimingFactions(tile, List<int> out)
  └─ Invalidate: on WorldObjectsHolder Add/Remove
```

Deliberately drop: `ApplySettlementUncontestedRings` (only needed if you want capital hinterlands
immune to contest), `variationSteps` noise (cosmetic raggedness), and the RimWar scan-range integration.

**Make it MP-safe from the start** by fixing the four things FT got wrong. These are cheap at design
time and expensive to retrofit:

1. **No mod settings in the computation.** Hard-code `radius`, `terrainImpact`, `includeWater` as
   consts, or put them in a Def so they travel with the mod rather than with a per-client settings
   file. Removes the largest divergence surface and the `ComputeSettingsHash` machinery with it.
2. **Rebuild on a fixed tick cadence in `WorldComponentTick`, never lazily on first query.** FT's
   lazy `EnsureCache` + `revision` counter is the root of desync #1 — a client-local UI action bumps a
   counter that downstream simulation caches key against. Eager, tick-scheduled rebuild makes both
   clients provably identical and kills the whole class.
3. **Return a sorted `List<int>`, never a `HashSet<int>`.** Any consumer that indexes with `Rand`
   into an unordered collection is a desync waiting for a rehash. Sort at the boundary.
4. **Break the plurality tie deterministically.** FT's `CollapseInfluenceMap` resolves an exact tie by
   whichever faction enumerates first out of a `Dictionary`. Sort by `(influence desc, factionId asc)`
   and the ambiguity is gone.

Then keep the parts FT got *right*: integer edge costs (`× 100`, no float accumulation), a total
ordering in the heap comparator, canonically sorted sources, and world-seed hashing instead of `Rand`.

Then the mechanical payload — which is where the design value is — is small:

- **Territory-gated incident faction.** Copy the `forcedAmbushFactionIdByCaravanId` idea: when a
  caravan/raid incident fires and the target tile is claimed, force `parms.faction` to a claimant.
  This is the single highest-value, lowest-risk mechanic in the whole mod: raids stop being random
  and start being *someone specific reacting to where you are*. It is also cheap — no new world
  objects, no new UI, and it runs inside vanilla's already-synced incident pipeline.
- **Territory-gated map incursions.** FT's version is already written correctly for MP
  (`Rand.PushState(hash)`, `ExposeData`'d scheduling). Worth porting near-verbatim, including the
  friendly-claimant-sends-help case, which is the mechanic that makes factions feel like *forces*
  rather than threats.
- **AI-vs-AI invasion over contested tiles.** The single best idea in the mod: an invasion can only
  exist where two factions' claims overlap, settlements genuinely change hands, and the player can
  walk in as a third party and tip it. That is "factions act on their own" delivered literally. It is
  also the most expensive to port — the resolution paths, the temp-settlement proxy hack for
  map-less targets, and the `LongEventHandler` entry all need rework. **INFERRED:** a stripped
  version that only resolves off-map (tech-weight + strength roll, no player-joinable battle) would
  capture most of the world-feel for perhaps 200 lines and would be trivially MP-safe, since it is
  pure tick-path arithmetic with a seeded `PushState`.

### The renderer without the sim

Also yes. MMF's `MapMode_GenericRegion<T>` exists exactly for this: give it a `RegionList` and a
`GenerateRegion(T)` and it draws them. Archinity could ship a `MapModeDef` with a
`MapMode_ArchinityTerritory : MapMode_GenericRegion<Faction>` in ~60 lines, and skip **all** of FT's
reflection layer (`ResolveRegionType`, `TryBuildRegionCtorArgs`, `GetRegionsList`) — that machinery
exists only because FT compiles against an MMF version it doesn't trust. If you compile against the
MMF you actually ship, you just call `new Region(name, tiles, false, mat, true, borderMat, 0.7f, tooltip)`.

But note MMF costs you a second Harmony assembly in the load order and an async worker-thread
pipeline. **For a two-player co-op game the rendering is the part you can most afford to skip** — a
tooltip on the world tile saying "Claimed by X" costs nothing and conveys 80% of the information.

### Recommendation

| Component | Take? |
|---|---|
| `TerritoryOwnershipCache` algorithm (reimplemented, settings removed, sorted output) | **Yes — highest value.** |
| Territory-forced incident faction | **Yes.** Cheap, big narrative payoff, MP-safe if done in the tick path. |
| Territory map incursions (incl. friendly support) | **Yes**, port the `Rand.PushState` pattern verbatim. |
| AI-vs-AI invasion over contested tiles (off-map resolution only) | **Yes, in stripped form.** Best world-feel per line in the mod. Skip the player-joinable battle map and the proxy-settlement hack. |
| Faction expansion / construction sites | **Probably not.** Nice idea, but its candidate cache is desync vector #1 and the site validity checks are too thin (no biome/hilliness gate). |
| MMF rendering | **Optional.** Defer; a tooltip gets you most of the way. |
| Voronoi contested shader | **No.** Pure decoration, a `Texture2D` bake, and a 134M-op main-thread loop in `worldcomponent.BuildTexture`. |
| Vassalage as designed | **No.** One-directional, no obligations, no end state, and the purchase path is exploitable. |
| The ally-cede dialog beat | **Yes, as an idea.** "Take the prize or keep your ally's trust" is the one real story in the mod. |
| Vassalage points → shop | **No.** This is the vending machine you are trying to get away from. |
| Running FT as a dependency in the co-op save | **No.** Guaranteed desync; would require a fork. |

---

## Appendix: file map of the decompile

| Namespace | Lines | What |
|---|---|---|
| `FactionTerritories` | ~6,400 | Territory algorithm, map mode, caravan incidents, incursions, settings, ambush-faction forcing patches |
| `FactionTerritories.Vassalise` | ~5,600 | Outposts, points, the shop dialog, Roads-of-the-Rim interop, choice letters |
| `FactionTerritories.Invasions` | ~3,200 | AI-vs-AI settlement invasions, player join-fight |
| `FactionTerritories.Expansion` | ~1,100 | Faction settlement construction sites |

Key files, largest first:

- `FactionTerritories/FactionTerritoriesUtility.cs` (1528) — hashes, materials, RimWar interop, main-thread action queue
- `FactionTerritories.Vassalise/VassalRoadProgressComponent.cs` (1521) — Roads of the Rim reflection interop
- `FactionTerritories.Vassalise/Dialog_Vassalage.cs` (1412) — **the shop**
- `FactionTerritories.Invasions/Utility.cs` (1335)
- `FactionTerritories/MapMode_FactionTerritories.cs` (1003) — MMF reflection bridge
- `FactionTerritories/GameComponent_FactionTerritories.cs` (748) — **map incursions**
- `FactionTerritories/TerritoryOwnershipCache.cs` (553) — **the algorithm worth stealing**
- `FactionTerritories/CaravanTerritoryIncidents.cs` (516) — **caravan interception**
- `FactionTerritories.Vassalise/VassaliseUtility.cs` (468) — vassalise / cede execution
- `FactionTerritories.Vassalise/VassalagePointsComponent.cs` (270) — the tribute ledger
