# Can Ushanka's Glittertech Expansion sites be moved to the Orbit planet layer with XML patches only?

Researched against RimWorld 1.6 + Odyssey, GTE workshop build `3522676478/1.6`, VEF/KCSG `2023507013/1.6`.

**VERDICT: PARTIALLY VIABLE.**
The *world-map placement* (site appears on the Orbit layer, reachable only by shuttle/pod/gravship) is
achievable in pure XML. The *map generation* is not: the KCSG structures GTE ships cannot produce a
functional map on a space map generator, and the closest non-space alternative trips a hard
`Log.Error` in vanilla terrain generation. Fixing the map requires either new content (authoring
`terrainGrid` for every GTE layout) or C#.

---

## 1. How a quest chooses the planet layer

### 1a. GTE's current node: `QuestNode_GetSiteTile` — no layer control

`.../3522676478/1.6/Defs/QuestScriptDefs/Base.xml` (`USH_GlittertechQuestBase`):

```xml
<li Class="QuestNode_Set">
    <name>siteDistRange</name>
    <value>2~6</value>
</li>
<li Class="QuestNode_GetMap" />
<li Class="QuestNode_SubScript"><def>Util_AdjustPointsForDistantFight</def></li>
<li Class="QuestNode_GetSiteTile">
    <storeAs>siteTile</storeAs>
    <preferCloserTiles>true</preferCloserTiles>
</li>
...
<li Class="QuestNode_SubScript"><def>Util_GenerateSite</def></li>
<li Class="QuestNode_SpawnWorldObjects"><worldObjects>$site</worldObjects></li>
```

Decompiled (`ilspycmd -t RimWorld.QuestGen.QuestNode_GetSiteTile Assembly-CSharp.dll`):

```csharp
public class QuestNode_GetSiteTile : QuestNode
{
    [NoTranslate] public SlateRef<string> storeAs;
    public SlateRef<bool> preferCloserTiles;
    public SlateRef<bool> allowCaravans;
    public SlateRef<bool> canSelectSpace;
    public SlateRef<bool?> clampRangeBySiteParts;
    public SlateRef<IEnumerable<SitePartDef>> sitePartDefs;
    public SlateRef<List<LandmarkDef>> allowedLandmarks;
    public SlateRef<float?> selectLandmarkChance;
    public SlateRef<bool> canSelectComboLandmarks;

    private bool TryFindTile(Slate slate, out PlanetTile tile)
    {
        bool value = canSelectSpace.GetValue(slate);
        PlanetTile nearTile = (slate.Get<Map>("map")
            ?? (value ? Find.RandomPlayerHomeMap : Find.RandomSurfacePlayerHomeMap))?.Tile
            ?? PlanetTile.Invalid;
        if (nearTile.Valid && nearTile.LayerDef.isSpace && !value)
            nearTile = PlanetTile.Invalid;
        ...
        return TileFinder.TryFindNewSiteTile(out tile, nearTile, var.min, var.max,
            allowCaravans.GetValue(slate), allowedLandmarks.GetValue(slate), num2,
            canSelectComboLandmarks.GetValue(slate), tileFinderMode,
            exitOnFirstTileFound: false, value);
    }
}
```

**There is no `layer` / `planetLayer` / `layerWhitelist` field.** `canSelectSpace` is *permissive*, not
*directive*: it only allows the near-tile to itself be a space tile. The layer of the result is
inherited from the near tile, per `TileFinder.TryFindNewSiteTile`:

```csharp
public static bool TryFindNewSiteTile(out PlanetTile tile, PlanetTile nearTile, int minDist = 7,
    int maxDist = 27, ..., bool canBeSpace = false, PlanetLayer layer = null, ...)
{
    ...
    if (layer == null)
        layer = nearTile.Layer;                    // <-- layer follows the colony's layer
    if (!canBeSpace && layer.Def.isSpace && !Find.WorldGrid.TryGetFirstAdjacentLayerOfDef(
            nearTile, PlanetLayerDefOf.Surface, out layer))
        (_, layer) = Find.WorldGrid.PlanetLayers.Where(t => !t.Value.Def.isSpace).RandomElement();
    ...
    List<PlanetTile> list = layer.FastTileFinder.Query(query, null, allowedLandmarks);
```

The `PlanetLayer layer` parameter exists but is **only reachable from C#** — `QuestNode_GetSiteTile`
never passes it. So no XML edit to the existing node can send the site to Orbit.

`QuestNode_GetSiteTile` is the only generic "find a tile and store it in the slate" node in the game
(301 `QuestNode_*` classes scanned; none of the others store a tile with layer control).

### 1b. Odyssey's own pattern: `QuestNode_Root_Site` — layer control IS XML-settable

`Data/Odyssey/Defs/QuestScriptDefs/Script_SpaceSites.xml`, e.g. `OpportunitySite_AbandonedPlatform`:

```xml
<li Class="QuestNode_Root_Site">
  <layerWhitelist>
    <li>Orbit</li>
  </layerWhitelist>
  <canBeSpace>true</canBeSpace>
  <sitePartDef>Opportunity_AbandonedPlatform</sitePartDef>
  <worldObjectDef>ClaimableSpaceSite</worldObjectDef>
  <distanceFromColonyRange>1~3</distanceFromColonyRange> <!-- distance in orbital layer tiles -->
</li>
```

Decompiled `RimWorld.QuestGen.QuestNode_Root_Site` — the relevant fields and layer logic:

```csharp
public class QuestNode_Root_Site : QuestNode
{
    private SlateRef<SitePartDef> sitePartDef;
    private SlateRef<WorldObjectDef> worldObjectDef;
    private SlateRef<FactionDef> factionDef;
    private SlateRef<IntRange> distanceFromColonyRange;
    public SlateRef<bool> canBeSpace;
    public SlateRef<bool> requireSameOrAdjacentLayer = true;
    public SlateRef<List<PlanetLayerDef>> layerWhitelist;
    public SlateRef<List<PlanetLayerDef>> layerBlacklist;

    protected override void RunInt()
    {
        Slate slate = QuestGen.slate;
        Quest quest = QuestGen.quest;
        if (!TryFindSiteTile(slate, out var tile)) { Log.Error("Could not find valid site tile."); return; }
        Faction faction = ((factionDef != null)
            ? Find.FactionManager.FirstFactionOfDef(factionDef.GetValue(slate))
            : Faction.OfAncientsHostile);
        Site site = QuestGen_Sites.GenerateSite(new SitePartDefWithParams[1] {
            new SitePartDefWithParams(sitePartDef.GetValue(slate), new SitePartParams {
                points = slate.Get("points", 0f), threatPoints = slate.Get("points", 0f) })
        }, tile, faction, hiddenSitePartsPossible: false, null, worldObjectDef.GetValue(slate));
        slate.Set("site", site);
        quest.SpawnWorldObject(site);
    }

    protected virtual bool TryGetLayer(Slate slate, out PlanetTile source, out PlanetLayer layer)
    {
        ...
        bool Validator(PlanetTile origin, PlanetLayer layer)
        {
            if (!canBeSpace.GetValue(slate) && layer.Def.isSpace) return false;
            List<PlanetLayerDef> value  = layerWhitelist.GetValue(slate);
            List<PlanetLayerDef> value2 = layerBlacklist.GetValue(slate);
            if (!value.NullOrEmpty()  && !value.Contains(layer.Def))  return false;
            if (!value2.NullOrEmpty() &&  value2.Contains(layer.Def)) return false;
            if (requireSameOrAdjacentLayer.GetValue(slate) && origin.Valid && origin.Layer != layer
                && !layer.DirectConnectionTo(origin.Layer)) return false;
            return true;
        }
    }
}
```

So the crux comparison holds: **Odyssey ships exactly this pattern, and it is 100% XML.** The catch is
that `QuestNode_Root_Site` *also* generates and spawns the site itself — it is a root replacement, not
a tile-picker. Swapping it into GTE's base script means dropping GTE's
`QuestNode_GetSiteTile` → `QuestNode_GetDefaultSitePartsParams` → `QuestNode_GetSiteThreatPoints` →
`Util_GenerateSite` → `QuestNode_SpawnWorldObjects` chain.

### 1c. Red herring: `QuestScriptDef.layerWhitelist` / `everAcceptableInSpace`

GTE already sets `<canOccurOnAllPlanetLayers>true</canOccurOnAllPlanetLayers>` and
`<everAcceptableInSpace>true</everAcceptableInSpace>` on both quests. These gate where the *player*
may be when the quest fires, not where the site lands:

```csharp
private bool CanQuestOccurOnTile(PlanetTile tile)   // QuestScriptDef
{
    if (!tile.Valid) return true;
    PlanetLayerDef layerDef = tile.LayerDef;
    if (!layerWhitelist.NullOrEmpty() && !layerWhitelist.Contains(layerDef)) return false;
    if (!layerBlacklist.NullOrEmpty() &&  layerBlacklist.Contains(layerDef)) return false;
    if (!autoAccept && !everAcceptableInSpace && layerDef.isSpace) return false;
    if (neverPossibleInSpace && layerDef.isSpace) return false;
    return true;
}
```

`tile` here is the player home map / incident target tile. Setting `<layerWhitelist><li>Orbit</li></layerWhitelist>`
on the QuestScriptDef would *prevent the quest from firing for a surface colony*, which is the
opposite of what is wanted.

---

## 2. Does the site's `WorldObjectDef` matter? Yes — it is the map generator selector.

GTE never passes a `worldObjectDef`. `Util_GenerateSite`
(`Data/Core/Defs/QuestScriptDefs/Scripts_Utility_ThreatsCore.xml:346`):

```xml
<QuestScriptDef>
  <defName>Util_GenerateSite</defName>
  <root Class="QuestNode_GenerateSite">
    <sitePartsParams>$sitePartsParams</sitePartsParams>
    <hiddenSitePartsPossible>$hiddenSitePartsPossible</hiddenSitePartsPossible>
    <storeAs>site</storeAs>
    <faction>$siteFaction</faction>
    <tile>$siteTile</tile>
    ...
```

`QuestNode_GenerateSite` **does** expose a `worldObjectDef` SlateRef, it is simply left unset here:

```csharp
public class QuestNode_GenerateSite : QuestNode
{
    public SlateRef<IEnumerable<SitePartDefWithParams>> sitePartsParams;
    public SlateRef<Faction> faction;
    public SlateRef<PlanetTile> tile;
    [NoTranslate] public SlateRef<string> storeAs;
    public SlateRef<RulePack> singleSitePartRules;
    public SlateRef<bool> hiddenSitePartsPossible;
    public SlateRef<WorldObjectDef> worldObjectDef;   // <-- XML-settable, unused by Util_GenerateSite
    ...
}
```

The resulting `WorldObjectDef` decides the map generator (`RimWorld.Planet.MapParent`):

```csharp
public virtual MapGeneratorDef MapGeneratorDef => def.mapGenerator ?? MapGeneratorDefOf.Encounter;
```

`RimWorld.Planet.Site` does **not** override `MapGeneratorDef`. Core's `Site` WorldObjectDef
(`Data/Core/Defs/WorldObjectDefs/WorldObjects.xml:152`) declares no `<mapGenerator>`, so GTE sites
currently generate with `Encounter`.

Odyssey's `SpaceSite` (`Data/Odyssey/Defs/WorldObjectDefs/WorldObjects.xml`):

```xml
<WorldObjectDef Name="SpaceSite" ParentName="Site">
  <defName>SpaceSite</defName>
  <label>space site</label>
  <useDynamicDrawer>true</useDynamicDrawer>
  <expandingIcon>true</expandingIcon>
  <expandingIconPriority>60</expandingIconPriority>
  <expandingIconColor>(255,255,255,255)</expandingIconColor>
  <fullyExpandedInSpace>true</fullyExpandedInSpace>
  <expandingIconDrawSize>1.35</expandingIconDrawSize>
  <mapGenerator>Space</mapGenerator>
</WorldObjectDef>
```

**Answer: yes, a quest can be patched to use `SpaceSite` — via `QuestNode_Root_Site/worldObjectDef` or
by inlining `QuestNode_GenerateSite` with `<worldObjectDef>SpaceSite</worldObjectDef>`.** Both are XML.

Also note `Site.GetTransportersFloatMenuOptions` branches on the map generator, not the layer:

```csharp
if (def.mapGenerator == MapGeneratorDefOf.Space)
{
    foreach (var o in TransportersArrivalAction_VisitSpace.GetFloatMenuOptions(launchAction, pods, this))
        yield return o;
    yield break;
}
foreach (var o in TransportersArrivalAction_VisitSite.GetFloatMenuOptions(launchAction, pods, this))
    yield return o;
```

So an orbit-layer site that is *not* `mapGenerator == Space` would be offered the surface-visit
arrival action. Unconfirmed whether that actually functions from orbit.

---

## 3. THE HARD BLOCKER — GTE's KCSG structures cannot produce a working space map

### 3a. What the Space map generator leaves behind

`Data/Odyssey/Defs/MapGeneration/SpaceMapGenerator.xml`:

```xml
<MapGeneratorDef Name="SpaceMapGenerator">
  <defName>Space</defName>
  <defaultUnderGridTerrain>Space</defaultUnderGridTerrain>
  <genSteps>
    <li>Space</li>       <!-- order 100 -->
    <li>ScenParts</li>
    <li>FogSpace</li>    <!-- order 1500 -->
  </genSteps>
</MapGeneratorDef>
```

```csharp
public class GenStep_Space : GenStep
{
    public override int SeedPart => 196743;
    public override void Generate(Map map, GenStepParams parms)
    {
        if (!ModsConfig.OdysseyActive) return;
        map.regionAndRoomUpdater.Enabled = false;
        TerrainGrid terrainGrid = map.terrainGrid;
        foreach (IntVec3 allCell in map.AllCells)
            terrainGrid.SetTerrain(allCell, TerrainDefOf.Space);
    }
}
```

`TerrainDefOf.Space` (`Data/Odyssey/Defs/TerrainDefs/Terrain_Natural.xml:5`):

```xml
<TerrainDef>
  <defName>Space</defName>
  <label>space</label>
  <dontRender>true</dontRender>
  <exposesToVacuum>true</exposesToVacuum>
  <passability>Impassable</passability>
  <pathCost>300</pathCost>
  ...
```

So after `GenStep_Space`, **every cell is impassable and vacuum-exposing.** A space map generator that
does nothing else is a 100% empty void — a floor must be *painted in* by a later genstep. That is
precisely what `GenStep_OrbitalPlatform` does (`platformTerrain`/`OrbitalPlatform`), and what
`GenStep_Asteroid` / `GenStep_BasicAsteroid` do (vacstone).

### 3b. GTE's gensteps are KCSG and would run, but KCSG never paints a full floor

`.../3522676478/1.6/Defs/SiteParts.xml`:

```xml
<GenStepDef>
  <defName>USH_GlittertechOutpost</defName>
  <linkWithSite>USH_GlittertechOutpost</linkWithSite>
  <order>460</order>
  <genStep Class="KCSG.GenStep_CustomStructureGen">
    <scaleWithQuest>true</scaleWithQuest>
    <tiledStructures><li>USH_GlittertechOutpost</li></tiledStructures>
    <fullClear>true</fullClear>
    <clearFogInRect>false</clearFogInRect>
    <preventBridgeable>true</preventBridgeable>
  </genStep>
</GenStepDef>
```

Ordering is fine (460 sits between `Space`@100 and `FogSpace`@1500) and site-part gensteps are appended
for any map generator (`RimWorld.Planet.Site.ExtraGenStepDefs` yields `parts[i].def.ExtraGenSteps`,
independent of the generator). So the genstep *runs*. The problem is what it does.

`KCSG.LayoutUtils.GenerateTerrainGrid` (decompiled from `2023507013/1.6/Assemblies/KCSG.dll`):

```csharp
if (layout._terrainGrid == null || layout._terrainGrid.Length == 0) return;
bool flag = layout._terrainColorGrid != null && layout._terrainColorGrid.Length > 0;
for (int num = 0; num < rotatedSizes.z; num++)
    for (int num2 = 0; num2 < rotatedSizes.x; num2++)
    {
        IntVec3 val7 = new IntVec3(num2, 0, num) + offset;
        IntVec3 sourceCoords4 = GetSourceCoords(num2, num, rot, layout.sizes);
        TerrainDef val8 = layout._terrainGrid[sourceCoords4.z, sourceCoords4.x];
        if (val8 != null && GenGrid.InBounds(val7, map))     // <-- ONLY named cells
        {
            GenOption.DespawnMineableAt(val7);
            map.terrainGrid.SetTerrain(val7, val8);
            ...
        }
    }
```

and the parser that turns `.` into `null` (`KCSG.StructureLayoutDef.ResolveReferences`):

```csharp
_terrainGrid = new TerrainDef[sizes.z, sizes.x];
...
_terrainGrid[i, j] = DefDatabase<TerrainDef>.GetNamedSilentFail(array[j]);   // named terrain
...
_terrainGrid[i, j] = null;                                                   // "." or unknown
...
_terrainGrid[i, k] = null;                                                   // short rows
```

**A `.` in a KCSG `terrainGrid` means "leave whatever terrain is already there".** On a surface map that
is grass/soil; on a Space map that is `TerrainDefOf.Space` — impassable, vacuum.

Measured coverage across every GTE layout in
`.../3522676478/1.6/Defs/StructureLayoutDefs.xml` (each tile is 11x11 = 121 cells):

| Layout | terrain cells | `.` (untouched) | % untouched | roofGrid |
|---|---|---|---|---|
| USH_GlittershipSpot | 121 | 95 | 79% | N |
| USH_ResearchSpot | — | **no terrainGrid at all** | 100% | Y |
| USH_FoamSpot | 121 | 121 | 100% | Y |
| USH_DiningSpot | 121 | 97 | 80% | N |
| USH_CenterSpot | 121 | 41 | 34% | Y |
| USH_LearningSpot | 121 | 71 | 59% | Y |
| USH_StockpileSpot | 121 | 71 | 59% | Y |
| USH_PylonSpot | 121 | 96 | 79% | N |
| USH_SleepingSpot | 121 | 71 | 59% | Y |
| USH_TraderSpot | 121 | 86 | 71% | Y |
| USH_TurretsSpotA/B/C | 121 | 84 / 80 / 72 | 69% / 66% / 60% | Y/N/N |
| USH_JunkA | 121 | 72 | 60% | N |
| USH_JunkB/C/D/E | 121 | 121 each | 100% | N |

The best case (`USH_CenterSpot`) still leaves **34% of its own footprint as raw vacuum**; several tiles
(`USH_FoamSpot`, `USH_ResearchSpot`, all four Junk variants) would place buildings on a 100% void floor.
And the outpost is a 3x3 grid of these tiles (`TiledStructureDef` `tilesNumber 9`,
`maxDistanceFromCenter 1`), so the assembled site would be an archipelago of disconnected concrete
patches with walls and turrets floating over impassable nothing.

Sample proving the pattern — `USH_GlittershipSpot`'s terrainGrid:

```xml
<terrainGrid>
  <li>.,.,.,.,.,.,.,.,.,.,.</li>
  <li>.,.,.,.,.,.,.,.,.,.,.</li>
  <li>.,.,.,.,.,.,.,.,.,.,.</li>
  <li>.,.,.,.,.,AncientConcrete,AncientConcrete,.,.,.,.</li>
  <li>.,.,.,AncientConcrete,AncientConcrete,AncientConcrete,AncientConcrete,AncientConcrete,.,.,.</li>
  ...
```

while the *layout* grid at the same coordinates is full of `Turret_Sniper`, `AncientRazorWire`,
`Column_Steel`, `HiddenConduit`, `USH_GlittershipChunk_North` etc. — i.e. the objects are placed
regardless of terrain.

Secondary consequences, all following from the same fact:
- Even the walled/roofed rooms would be permanently unpressurizable: their floor cells are
  `Space` with `exposesToVacuum=true`.
- Ambient temperature on a space map is `-75`
  (`BiomeDef Space: <constantOutdoorTemperature>-75</constantOutdoorTemperature>`, and
  `GenStep_OrbitalPlatform.SpawnTemp => temperature ?? -75f`). Odyssey's own platform gensteps
  explicitly override this with `<temperature>20</temperature>`; `KCSG.GenStep_CustomStructureGen` has
  no equivalent field.
- `GenStep_FogSpace` unfogs by flood-filling from the map corners through cells with no edifice and no
  roof — on an all-vacuum map that reveals essentially everything, defeating the "raid a hidden
  facility" framing. Unconfirmed how badly this reads in play.
- `preventBridgeable: true` on GTE's genstep is a surface-map concern and does nothing to help here.
- `KCSG.LayoutUtils.CleanRect` (called with `fullClear: true`) only despawns things; it never sets
  terrain, so it does not rescue the floor either.

### 3c. The non-space fallback also fails, differently

If you place the site on an Orbit tile but leave `worldObjectDef` as vanilla `Site`
(→ `MapGeneratorDefOf.Encounter`), map generation reads the tile's biome, which is `Orbit`
(`PlanetLayerDef Orbit: <defaultBiome>Orbit</defaultBiome>`). That biome
(`Data/Odyssey/Defs/BiomeDefs/Space.xml`) inherits `SpaceBiome`:

```xml
<BiomeDef Name="SpaceBiome">
  <defName>Space</defName>
  <workerClass>BiomeWorker_Space</workerClass>
  <generatesNaturally>false</generatesNaturally>
  <plantDensity>0</plantDensity>
  <constantOutdoorTemperature>-75</constantOutdoorTemperature>
  <inVacuum>true</inVacuum>
  <hasBedrock>false</hasBedrock>
  <forceRockTypes><li>Vacstone</li></forceRockTypes>
  <canExitMap>false</canExitMap>
</BiomeDef>
<BiomeDef ParentName="SpaceBiome"><defName>Orbit</defName>...</BiomeDef>
```

It declares **no `terrainsByFertility`**, so vanilla terrain generation hits its own error path:

```csharp
if (terrainDef == null)
    terrainDef = TerrainThreshold.TerrainAtValue(biomeDef.terrainsByFertility, fertility);
if (terrainDef == null)
{
    if (!debug_WarnedMissingTerrain)
    {
        Log.Error("No terrain found in biome " + biomeDef.defName + " for elevation=" + elevation
                  + ", fertility=" + fertility);
        debug_WarnedMissingTerrain = true;
    }
    terrainDef = TerrainDefOf.Sand;
}
```

Result: a red error and a map of sand "in orbit", `inVacuum` biome, `canExitMap=false`,
`hasBedrock=false` with `forceRockTypes: Vacstone`. This is the closest thing to a working structure
map, and it is explicitly an unsupported code path. Whether the KCSG rooms would seal against the
biome-level vacuum on sand terrain, and whether the surface-style arrival action works from an Orbit
tile, is **unconfirmed** — it would need an in-game test.

---

## 4. Is anything hardcoded in GTE's own assembly?

No. `GlittertechExpansion.dll` (decompiled in full) contains no tile-selection, layer, world-object, or
map-generator logic. Every `PlanetTile` reference is a *read* of an already-chosen tile:

```
5962-5981   pocket-map distance helper (TraversalDistanceBetween)
11087-11088 QuestNode_AncientForces: PlanetTile tile = ((WorldObject)value).Tile;  // reads $site's tile
11104,11130 passes that tile into PawnGroupMakerParms_Saveable
11180       Rand seed from mapParent.Tile
11216       Scribe_Values.Look<PlanetTile>(ref base.tile, ...)
```

`USH_GE.QuestNode_AncientForces` (the only custom quest node) just spawns defenders on `$site`:

```csharp
protected override void RunInt()
{
    Slate slate = QuestGen.slate;
    MapParent value = mapParent.GetValue(slate);
    PlanetTile tile = ((WorldObject)value).Tile;
    IEnumerable<PawnKindDef> enumerable = HandleAncientForces(slate, tile, value)
        .Concat(HandleMechForces(slate, tile, value));
    QuestGen.AddQuestDescriptionRules(...);
}
```

It is layer-agnostic and would work unchanged on an orbit site. **All placement behaviour lives in the
XML and in vanilla code — nothing in GTE's DLL blocks this.**

---

## 5. What IS achievable in pure XML, and the patch

Achievable:
- Site spawns on the **Orbit** planet layer, 1–3 orbital tiles from the colony.
- Site is a `SpaceSite` (space arrival actions, expanding orbital icon, gravship-landable via
  `<gravShipsCanLandOn>true</gravShipsCanLandOn>` already on both GTE SitePartDefs).
- Quest still fires from a surface colony (`requireSameOrAdjacentLayer` is satisfied — Orbit directly
  connects to Surface, which is what Odyssey's own space quests rely on).
- GTE's ancient-forces defenders, timeout, and completion signals all still work.

NOT achievable in XML: a map that is actually walkable/pressurizable.

### Patch approach

Replace GTE's tile/site block with Odyssey's `QuestNode_Root_Site`. `PatchOperationReplace` against
`USH_GlittertechQuestBase`, dropping the five nodes `QuestNode_GetMap` … `QuestNode_SpawnWorldObjects`
(note `QuestNode_Root_Site` sets `$site` and spawns it itself, and reads `points` from the slate,
which `Util_AdjustPointsForDistantFight` has already set):

```xml
<Patch>
  <!-- 1. Orbit placement + SpaceSite world object -->
  <Operation Class="PatchOperationReplace">
    <xpath>/Defs/QuestScriptDef[defName="USH_GlittertechQuestBase"]/root/nodes/li[@Class="QuestNode_GetSiteTile"]</xpath>
    <value>
      <li Class="QuestNode_Root_Site">
        <layerWhitelist>
          <li>Orbit</li>
        </layerWhitelist>
        <canBeSpace>true</canBeSpace>
        <requireSameOrAdjacentLayer>true</requireSameOrAdjacentLayer>
        <sitePartDef>$sitePartDef</sitePartDef>
        <worldObjectDef>SpaceSite</worldObjectDef>
        <factionDef>AncientsHostile</factionDef>
        <distanceFromColonyRange>1~3</distanceFromColonyRange>
      </li>
    </value>
  </Operation>

  <!-- 2. Remove the now-redundant surface-site pipeline -->
  <Operation Class="PatchOperationRemove">
    <xpath>/Defs/QuestScriptDef[defName="USH_GlittertechQuestBase"]/root/nodes/li[@Class="QuestNode_GetMap"]
         | /Defs/QuestScriptDef[defName="USH_GlittertechQuestBase"]/root/nodes/li[@Class="QuestNode_GetDefaultSitePartsParams"]
         | /Defs/QuestScriptDef[defName="USH_GlittertechQuestBase"]/root/nodes/li[@Class="QuestNode_GetSiteThreatPoints"]
         | /Defs/QuestScriptDef[defName="USH_GlittertechQuestBase"]/root/nodes/li[@Class="QuestNode_SubScript"][def="Util_GenerateSite"]
         | /Defs/QuestScriptDef[defName="USH_GlittertechQuestBase"]/root/nodes/li[@Class="QuestNode_SpawnWorldObjects"]</xpath>
  </Operation>

  <!-- 3. Site parts want minMapSize like Odyssey's space sites -->
  <Operation Class="PatchOperationAdd">
    <xpath>/Defs/SitePartDef[defName="USH_GlittertechOutpost" or defName="USH_GlittertechFacility"]</xpath>
    <value>
      <minMapSize>(200, 0, 200)</minMapSize>
    </value>
  </Operation>
</Patch>
```

Untested caveat: removing `QuestNode_GetSiteThreatPoints` also removes `$sitePoints`, which
`Util_GetDefaultRewardValueFromPoints` consumes two nodes later. `$rewardValue` is computed but never
consumed by any reward node in `USH_GlittertechQuestBase`, so this is believed harmless — **unconfirmed**.

### What still has to be authored (this is the non-XML-only part)

To make the map work, one of:

1. **(XML-only but is authoring, not patching)** Add a full `terrainGrid` to every one of the ~14 GTE
   `StructureLayoutDef`s so that 100% of each 11x11 tile is a real floor (e.g. `OrbitalPlatform` or
   `AncientConcrete`), plus a full `roofGrid`. ~1700 terrain cells to write. This *is* achievable in
   XML via `PatchOperationReplace` on each `terrainGrid`/`roofGrid`, and it would fix passability and
   pressurization. Temperature (-75 ambient) and the `FogSpace` reveal remain.
2. **C#** — a `GenStep` subclass that paints a platform (like `GenStep_OrbitalPlatform`) over the
   structure's bounding rect before/after the KCSG step, and sets map temperature.

Given the tiled-structure system randomizes which 9 tiles are used and rotates them, option 1 is a
large but tractable content job; option 2 is a small code job.

---

## Evidence file paths

- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3522676478\1.6\Defs\QuestScriptDefs\Base.xml`
- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3522676478\1.6\Defs\QuestScriptDefs\OutpostQuest.xml`
- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3522676478\1.6\Defs\QuestScriptDefs\FacilityQuest.xml`
- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3522676478\1.6\Defs\SiteParts.xml`
- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3522676478\1.6\Defs\StructureLayoutDefs.xml`
- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3522676478\1.6\Defs\TiledStructureDefs.xml`
- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3522676478\1.6\Assemblies\GlittertechExpansion.dll`
- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2023507013\1.6\Assemblies\KCSG.dll`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Odyssey\Defs\QuestScriptDefs\Script_SpaceSites.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Odyssey\Defs\WorldObjectDefs\WorldObjects.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Odyssey\Defs\PlanetLayerDefs\PlanetLayers.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Odyssey\Defs\MapGeneration\SpaceMapGenerator.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Odyssey\Defs\Sites\Opportunities.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Odyssey\Defs\Sites\GravcoreLocations.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Odyssey\Defs\TerrainDefs\Terrain_Natural.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Odyssey\Defs\BiomeDefs\Space.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\QuestScriptDefs\Scripts_Utility_ThreatsCore.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\WorldObjectDefs\WorldObjects.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`

## Explicitly unconfirmed

- Whether removing `QuestNode_GetSiteThreatPoints` breaks `Util_GetDefaultRewardValueFromPoints` at
  runtime (`$rewardValue` appears unused downstream in GTE's script, but this was not run in-game).
- Whether a non-`Space` map generator (`Encounter`) on an Orbit tile is playable at all beyond the
  `Log.Error` + sand fallback — arrival actions, vacuum sealing on sand, `hasBedrock=false` with
  `forceRockTypes: Vacstone`, and `canExitMap=false` were not tested.
- Exact in-play severity of `GenStep_FogSpace` unfogging an all-vacuum map.
- Whether KCSG's `preventBridgeable` interacts badly with `Space` terrain's `Bridgeable` affordance.
- No in-game test was performed for any of this; all conclusions are from defs and decompiled IL.
