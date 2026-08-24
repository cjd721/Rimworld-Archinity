# Recon: five faction/world-tech support mods

Assessed for Archinity (RimWorld 1.6, two-player co-op on `rwmt.multiplayer`, neolithic
start, ~600 in-game days, endgame in orbit).

Hard filter applied throughout: **multiplayer determinism**. The disqualifying
patterns are unsynced `System.Random`, per-client cached state that feeds
simulation, and world mutation from unsynced UI code.

Workshop root: `/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/`
Decompiles were written to the session scratchpad (not checked in).

Verification basis per mod:

| Mod | ID | Evidence |
| = | = | = |
| Sensible Factions | 3531306011 | shipped C# source, 23 files / 1604 lines |
| Faction Customizer | 3336572602 | `ilspycmd` decompile of `1.6/Assemblies/FactionCustomizer.dll`, 2359 lines |
| Lemmy Progression | 3548896697 | shipped C# source, 13 files / 3059 lines, plus embedded `.git` history |
| World Tech Level | 3414187030 | `ilspycmd` decompile of `1.6/Lunar/Components/WorldTechLevel.dll`, 5313 lines |
| Vanilla Outposts Expanded | 2688941031 | `ilspycmd` decompile of `1.6/Assemblies/VOE.dll` (shipped source is stale 1.3), plus decompile of VEF's `Outposts.dll` |

Current Archinity modlist context (`config/ModsConfig.xml`, 66 entries) matters for
several verdicts below. Already active: `rwmt.multiplayer`,
`oskarpotocki.vanillafactionsexpanded.core` (VEF), `azravos.factioncustomizer`,
`oskarpotocki.vfe.classical`, `oskarpotocki.vfe.medieval2`, `fridgebaron.techblock`.
**Not** active: VFE Tribals, Medieval Overhaul, World Tech Level, Lemmy Progression,
Vanilla Outposts Expanded, Sensible Factions, and `rwmt.compatibility`
(Multiplayer Compatibility).

= = =

## 1. Sensible Factions (3531306011)

### What it does

Reassigns which faction owns which already-generated settlement at world-gen time, so
that each faction's bases end up clustered together and in biomes that suit it, instead
of being scattered uniformly across the planet. It does **not** move settlements, create
them, or change faction counts — it only re-labels ownership.

### Mechanism

Single Harmony postfix, registered from a static constructor:

```csharp
// RunWorldDistributionOnWorldStart.cs
harmony.Patch(
    original: AccessTools.Method(typeof(WorldGenerator), nameof(WorldGenerator.GenerateWorld)),
    postfix: new HarmonyMethod(typeof(RunWorldDistributionOnWorldStart), nameof(AfterWorldGenerated))
);

public static void AfterWorldGenerated(World __result)
{
    if (__result == null) return;
    LongEventHandler.ExecuteWhenFinished(() => { ColonyRedistributor.RunRedistribution(); });
}
```

`ColonyRedistributor.RunRedistribution` is the whole mod. It:

1. Snapshots every non-player `Settlement` and computes a per-faction quota equal to that
   faction's *existing* settlement count — so totals are preserved exactly.
2. Orders factions by their single strongest biome affinity
   (`FactionPlacementOrder.GetFactionPlacementPriority`).
3. Greedily assigns settlements by a score that weights biome fit ~100x over distance:

```csharp
// ColonyRedistributor.ScoreSettlementForFaction
float biomeScore = biomeWeight * 10000f;
float distancePenalty = distance * 100f;
return biomeScore - distancePenalty;
```

4. Re-seeds each faction's centroid after every assignment (`RecalculateFactionSeed`), which
   produces the clustering.
5. Applies with `kv.Key.SetFaction(kv.Value)` and calls
   `Find.World.renderer.RegenerateAllLayersNow()`.

Biome affinities are a 350-line hardcoded table (`FactionBiomeDefaults.cs`) keyed by
FactionDef defName — `OutlanderCivil`, `OutlanderRough`, tribals, etc. — with entries for
Odyssey biomes (`Odyssey_Glowforest`, `Odyssey_Scarlands`, `Odyssey_Undercave`). Unknown
modded factions fall through to weight 0 unless the player sets weights in mod settings.
Which factions participate is opt-in via `SensibleFactions_Settings.allowedFactionDefNames`;
**an empty allow-list means the mod does nothing**:

```csharp
// ColonyRedistributor.RunRedistribution
if (allowedFactionDefs == null || allowedFactionDefs.Count == 0)
    return;
```

`BiomeClusterPlacer.cs` and `TileClusterFinder.cs` exist but are unreachable from the
redistribution path — they are scaffolding for a settlement-*placement* feature that was
not wired up. There is also a `Version_2_Legacy/Legacy_Redistributor.txt` and a
`Version_3/` folder, i.e. the author is on his third rewrite.

### MP determinism verdict: PASS (low risk)

Randomness present, but all of it is Verse `Rand`, and all of it executes only inside
`WorldGenerator.GenerateWorld`:

```csharp
// ColonyRedistributor.GetInitialSeedForFaction — only when a faction owns nothing yet
if (unassigned.Any())
    return Find.WorldGrid.GetTileCenter(unassigned.RandomElement().Tile);

// TileClusterFinder.FindBestCluster — dead code, not reached
candidateTiles.InRandomOrder().Take(100)
```

In RimWorld Multiplayer the host generates the world and ships the resulting save to the
joining client, so world-gen-time divergence cannot desync a session. Nothing here ticks,
nothing runs per-frame, no `System.Random`, no static cache that survives into play.

One caveat that is real but bounded: `allowedFactionDefNames` and `factionBiomeWeights`
live in `config/ModSettings/` and are read at world-gen only. Per CLAUDE.md's settings-parity
rule, snapshot them, but a post-worldgen mismatch is harmless for this mod specifically.

`Dictionary<Settlement, Faction>` iteration order is used for the final `SetFaction` loop,
which is nondeterministic ordering — but each entry is independent so the outcome is
order-invariant. Not a hazard.

### Maintained?

`supportedVersions` is `1.6` only. Ships full source. Third internal rewrite with legacy
folders retained. No changelog, no repo link (About points at a Steam profile). Small
enough (1604 lines, one entry point) that Archinity could vendor or fork the logic if it
breaks. INFERRED: low-volume solo hobby mod, but the surface area is so small that abandonment
is not a serious risk.

= = =

## 2. Faction Customizer (3336572602)

### What it does

A **manual GUI editor** for faction and settlement metadata. It is not a simulation mod at
all — it adds no defs, no incidents, no AI. It lets a human sitting at the keyboard rename
factions and leaders, recolor them, change relationships, rename/move/create/delete
settlements, and add new faction instances.

The "62 XML files" in this mod are almost entirely translation keys. Actual def content:

```
Defs/KeyBindings/KeyBindingCategories.xml
1.6/Defs/KeyBindings/KeyBindings.xml
```

Two keybinding defs. Everything else under `1.6/Languages/{English,ChineseSimplified,ChineseTraditional}/Keyed/`.

### Mechanism

Standard `Mod` + `Harmony.PatchAll`:

```csharp
// FactionCustomizer.cs
public FactionCustomizer(ModContentPack contentPack) : base(contentPack)
{
    ModSettings = GetSettings<ModSettings>();
    new Harmony(contentPack.PackageId).PatchAll(Assembly.GetExecutingAssembly());
}
```

Entry point in play is an icon injected into the world-view toolbar:

```csharp
// PlaySettingPatch.cs
[HarmonyPatch(typeof(PlaySettings), "DoPlaySettingsGlobalControls")]
public static void DoPlaySettingsGlobalControls(WidgetRow row, bool worldView)
{
    row.Gap(row.CellGap);
    if (row.ButtonIcon(ModTextures.fcText, ...))
        Show();   // opens FCDialog_FactionDuringLanding
}
```

The work happens in dialogs that write world state directly, with no sync wrapper:

```csharp
// Dialog_ModifyFactionRelation.cs — direct relation mutation
relation.baseGoodwill  = ChangingProperties.BaseGoodWill;
relation.kind          = ChangingProperties.RelationKind;
otherRelation.baseGoodwill = ChangingProperties.BaseGoodWill;
otherRelation.kind         = ChangingProperties.RelationKind;
```

```csharp
// WorldInterfaceUpdate.CreateSettlement — creates a settlement mid-game
WorldObject obj = WorldObjectMaker.MakeWorldObject(PlanetLayer.Selected.Def.SettlementWorldObjectDef);
Settlement val = obj as Settlement;
val.SetFaction(faction);
val.Tile = planetTile;
val.Name = SettlementNameGenerator.GenerateSettlementName(val, null);
Find.WorldObjects.Add(val);
```

```csharp
// WorldInterfaceUpdate.HandleRemoveSettlement — deletes one
Find.WorldObjects.Remove(settlement);
```

```csharp
// MoveSettlement.cs:79 — relocates one
selectedSettlement.Tile = selectedTile;
```

```csharp
// FCDialog_FactionDuringLanding.cs — spawns whole new factions
FactionGeneratorParms val7 = new FactionGeneratorParms(factionDef, default(IdeoGenerationParms), null);
Faction val8 = FactionGenerator.NewGeneratedFaction(val7);
Find.FactionManager.Add(val8);
```

Also bundles `0ColourPicker1.6.dll` (a third-party colour picker) alongside its own assembly.

### MP determinism verdict: CONDITIONAL — safe if untouched, desyncs the moment it is used in-session

There is no `System.Random`, no `Rand.*`, and no ticking code anywhere in the assembly —
grep for `Rand.`, `new Random`, `RandomElement`, `InRandomOrder` returns **zero hits**. The
mod is inert while nobody has the dialog open. That is why it can sit in the modlist safely.

The hazard is different: every mutation above runs in unsynced UI code on whichever client
clicked. `Find.WorldObjects.Add(...)`, `Find.FactionManager.Add(...)`,
`relation.baseGoodwill = ...`, `settlement.Tile = ...` — none of these are wrapped in a
Multiplayer `SyncMethod`, and Multiplayer does not auto-sync arbitrary modded window
callbacks. Player A creating a settlement or flipping a relation to hostile produces a world
object / relation that Player B's simulation does not have. That is an immediate,
unrecoverable state divergence, not a soft one.

`FCDialog_FactionDuringLanding` also calls `NameGenerator.GenerateName(...)` in its
randomize-all-names path, which consumes Verse `Rand` in an unsynced context — a second,
independent divergence on the same click.

**Operational rule for Archinity: Faction Customizer is a pre-game / world-setup tool only.**
Use it before the co-op session starts (or on the host with both clients then loading the
same save), and never open the FC toolbar icon during a live MP session. It is already in
`ModsConfig.xml`, which is fine — the risk is behavioural, not structural.

### Maintained?

`supportedVersions` lists 1.3 / 1.4 / 1.5 / 1.6, with a separate assembly per version —
that is a maintainer who has tracked four game releases. The About description carries
explicit "[For 1.6 and forward]" feature notes (create/delete settlements, add factions,
randomize names), so 1.6 got real new work, not a version-bump. Actively maintained.

= = =

## 3. Lemmy Progression Mod For World Tech Levels (3548896697)

### What it does

Intended: sit on top of World Tech Level and VFE Tribals so that (a) the player is exempt
from WTL's research ceiling, and (b) when the player advances an era via the VFE Tribals
ritual, the world tech level is pushed up and each other faction gets a percentage chance to
tech up with it.

### Mechanism

`ModCore` static constructor → `PatchManager.Initialize` → `harmony.PatchAll()` plus two
runtime reflection-driven patches:

```csharp
// PatchManager.cs
private static readonly List<IPatchDefinition> patches = new List<IPatchDefinition>
{
    new WorldTechLevelPatch(),
    new VFETribalsPatch()
};
```

**Trigger** — a prefix on VFE Tribals' `GameComponent_Tribals.AdvanceToEra`, located by
scanning the mod's assemblies for the type by name:

```csharp
// VFETribalsPatch.AdvanceToEraPrefix
var newTechLevel = (RimWorld.TechLevel)techLevelField.GetValue(def);
WorldEraManager.AdvanceToEra(def);
return true; // let original run too
```

**Research unlock** — a prefix on WTL's `TechLevelUtility.PlayerResearchFilterLevel` that
short-circuits the ceiling entirely:

```csharp
// WorldTechLevelPatch.ResearchFilterPrefix
private static bool ResearchFilterPrefix(ref TechLevel __result)
{
    if (!settings.modEnabled) return true;
    __result = TechLevel.Archotech;
    return false;
}
```

**World tech level write** — by reflection onto WTL's auto-property backing field:

```csharp
// WorldEraManager.InitializeWorldTechLevelAccess
cachedCurrentField = AccessTools.Field(cachedWorldTechLevelType, "Current");
if (cachedCurrentField == null) {
    var prop = AccessTools.Property(cachedWorldTechLevelType, "Current");
    if (prop != null)
        cachedCurrentField = AccessTools.Field(cachedWorldTechLevelType, "<Current>k__BackingField");
    ...
}
// WorldEraManager.SetWorldTechLevel
cachedCurrentField.SetValue(null, level);
```

**Faction upgrade** — `FactionUpgradeManager.UpgradeFactionsToTechLevel` rolls per faction,
then `FactionUpgrader.UpgradeToTechLevel` swaps the faction onto a *different* FactionDef:

```csharp
// FactionUpgrader.UpgradeToTechLevel
var selectedDef = SelectBestCandidate(candidateDefs);
...
faction.def = selectedDef;   // "Simple def swap - RimWorld handles all the persistence"
```

### MP determinism verdict: FAIL — hard, immediate, unfixable-without-a-fork

Three separate disqualifying findings.

**(a) `System.Random`, twice, in the decision path.** Both upgrade classes hold their own
unsynced RNG:

```csharp
// FactionUpgradeManager.cs:12
private static readonly Random random = new Random();
// FactionUpgradeManager.cs:208
private static bool ShouldUpgradeFaction(Faction faction, TechLevel targetLevel)
{
    var settings = ModCore.Settings;
    return random.NextDouble() < settings.factionUpgradeChance;
}
```

```csharp
// FactionUpgrader.cs:16
private static readonly Random random = new Random();
```

`System.Random` is seeded per-process from the system clock and is invisible to Multiplayer's
RNG synchronisation — it is never synced, in any context, including inside an already-synced
tick or command. With the default `factionUpgradeChance = 0.5f`, every faction in the world
is an independent coin flip that lands **differently on each client**. Host and client end up
with different `faction.def` values for the same factions, which immediately diverges raid
composition, pawn kinds, trader stock, and `MinPointsToGeneratePawnGroup`. This is the single
worst pattern in the whole set.

**(b) The def swap mutates shared global state that the save only partially covers.**
`faction.def = selectedDef` reassigns a `Faction` onto a different `FactionDef` instance. The
`.def` reference is scribed with the faction, so it survives save/load — meaning a desynced
world tech state is *persisted*, not transient. The class also reaches into private caches by
reflection:

```csharp
// FactionUpgrader.ClearPawnGenerationCaches
string[] cacheFields = new string[] { "_options", "cachedOptions", "options" };
...
string[] factionCacheFields = new string[]
{ "cachedPawnGenerator", "cachedRandomPawnGenerator", "cachedPawnKinds", "cachedFighters" };
```

and re-invokes `FactionDef.ResolveReferences` / `PawnGroupMaker.PostLoadInit` at runtime.
Those are startup-only lifecycle methods; calling them mid-game rebuilds caches per client
at a per-client moment. This is textbook per-client cached state feeding simulation.

**(c) The world tech level write does not actually persist.** WTL's real setter writes
*both* the static mirror and the GameComponent:

```csharp
// WTL Patch_WITab_Planet — the correct write path
WorldTechLevel.Current = value;
Current.Game.TechLevel().WorldTechLevel = value;   // <- Lemmy never does this
```

Lemmy only writes the static backing field. On reload, WTL restores from the component:

```csharp
// WTL Patch_WorldGenerator.GenerateFromScribe_Prefix
WorldTechLevel.Current = Current.Game.TechLevel().WorldTechLevel;
```

So every Lemmy era advance is **silently reverted on the next load**. In MP this is worse than
in singleplayer: the joining client builds its world from the transferred save, so it starts
at the original tech level while the host is running at the advanced one. Divergence on join,
before anyone does anything.

**Additional: shipped debug scaffolding runs unconditionally.** `harmony.PatchAll()` installs
a class literally named `RootCauseInvestigationPatch` that prefixes
`PawnGroupKindWorker_Normal.MinPointsToGenerateAnything` and emits five-plus `Log.Message`
lines **on every pawn-group generation in the game**, not gated behind `debugLogging`:

```csharp
[HarmonyPatch]
public static class RootCauseInvestigationPatch
{
    [HarmonyTargetMethod] static MethodBase TargetMethod()
        => AccessTools.Method(typeof(PawnGroupKindWorker_Normal), "MinPointsToGenerateAnything");
    [HarmonyPrefix] static bool Prefix(...)
    {
        Log.Message("[LemProgress][ROOT_CAUSE] MinPointsToGenerateAnything called:");
        ...
    }
}
```

Over a 600-day campaign this is a log-spam and framerate hazard on its own.

**Additional: the trigger does not exist in Archinity's modlist.** Lemmy's `About.xml`
declares hard `modDependencies` on `m00nl1ght.WorldTechLevel`, `oskarpotocki.vfe.tribals`
and `dankpyon.medieval.overhaul`. None of the three are in `config/ModsConfig.xml`. Both
runtime patches are gated on `ModsConfig.IsActive(RequiredModId)`, so with the current list
Lemmy installs *nothing but* the debug spam patch and the null-pawn-group fix. Archinity also
already owns its own era-advance mechanism (`Archinity.Altar`, `Archinity.Pacing`), which
Lemmy has no hook into.

### The `Worldbuilder/` folder

`1.6/Worldbuilder/Tribal World/` contains `Preset.xml`, `Thumbnail.png`, `Flavor.png`. This is
a preset for the **Worldbuilder** mod (a separate world-creation-preset mod), not part of
Lemmy's own code path — nothing in the 13 `.cs` files references it. It defines a planet type
that pins the world to neolithic and stacks the faction roster with tribals:

```xml
<worldPreset>
  <name>Tribal World</name>
  <planetType>Tribal World</planetType>
  <description>This planet type limits all technology to the Neolithic era and below.</description>
  <saveWorldTechLevel>True</saveWorldTechLevel>
  <worldTechLevel>Neolithic</worldTechLevel>
  <savedFactionDefs>
    <li>Ancients</li><li>AncientsHostile</li><li>Mechanoid</li><li>Insect</li><li>Pirate</li>
    <li>TribeCivil</li><li>TribeSavage</li><li>TribeRough</li>
    ... (TribeCivil/TribeSavage/TribeRough repeated ~9x)
  </savedFactionDefs>
</worldPreset>
```

Worth noting as a *reference* for how a neolithic-start faction roster is configured — the
repeated-triple pattern is how you get many tribal factions — but it is inert data unless the
Worldbuilder mod is installed, and it is pure XML, so it is MP-safe on its own.

Also note the duplicated tree: `3548896697/Source/` and `3548896697/Assemblies/` at the mod
root are **empty directory skeletons**; the real content is under `1.6/`.

### Maintained?

`About/Version.txt` reads `0.0.1`. The mod ships its own `.git` directory; last commit is
`76dc102 Removed stuff`, dated **2025-08-14**. Earlier commit messages read like an
in-progress debugging session: `Major refactor - still not working entirely`, `Fixed
pawnGroup exception so raids work properly`, `...`, `First upload` twice. Combined with the
unconditional `RootCauseInvestigationPatch`, this is pre-alpha code published mid-debug.

**Verdict: reject.** Not salvageable for this project without a rewrite of the RNG, the
persistence path, and the trigger — at which point it is an Archinity feature, not a
dependency.

= = =

## 4. World Tech Level (3414187030)

### What it does

Establishes a single world-wide `TechLevel` ceiling chosen at world creation, then filters
essentially every content pipeline in the game against it: research, items, stuff, pawn gear,
backstories, traits, xenotypes, ideology memes/precepts, quests, raid strategies, arrival
modes, world gen steps, map gen, book contents, techprints, trader stock, complex threats,
site parts, tile mutators. This is the mod that makes "no guns in the medieval era, no
mechanoid raids in the neolithic era" actually hold across the whole game.

It is **the framework** of the pair with Lemmy.

### Mechanism

Loaded through **LunarFramework**, m00nl1ght's self-contained component loader. Crucially,
LunarFramework is **not a separate Workshop dependency** — it is bundled:

```
1.6/Assemblies/LunarLoader.dll          <- the only thing RimWorld loads directly
1.6/Lunar/Components/HarmonyLib.dll
1.6/Lunar/Components/LunarFramework.dll
1.6/Lunar/Components/WorldTechLevel.dll <- the real assembly
1.6/Lunar/Components/*.lfc              <- per-file checksums
1.6/Lunar/Manifest.xml
```

Per the bundled README, if several m00nl1ght mods are installed only the newest copy of each
shared component loads, and the `.lfc` checksums exist to detect partial Steam updates. For
Archinity this means: **no extra Workshop subscription, but a hard load-order and file-integrity
requirement**, and `LunarLoader.dll` sitting in front of Harmony in the load chain. There is
also `About/Version.txt` = `1.1.6` and a real `Changelog.md`.

Patches are grouped and subscribed rather than blanket-applied:

```csharp
// WorldTechLevel.cs
[LunarComponentEntrypoint]
public class WorldTechLevel : Mod
{
    internal static readonly LunarAPI LunarAPI = LunarAPI.Create("WorldTechLevel", Init, Cleanup);
    public static TechLevel Current { get; set; } = (TechLevel)7;   // 7 == Archotech/unrestricted

    private static void Init()
    {
        MainPatchGroup.AddPatches(typeof(WorldTechLevel).Assembly);   MainPatchGroup.Subscribe();
        FiltersPatchGroup.AddPatches(typeof(WorldTechLevel).Assembly); FiltersPatchGroup.Subscribe();
        ModCompat.ApplyAll(LunarAPI, CompatPatchGroup);
        MainPatchGroup.CheckForConflicts(Logger);
        FiltersPatchGroup.CheckForConflicts(Logger);
        DefTechLevels.Initialize();
    }
}
```

Individual filters can be turned off in settings via `[HarmonyPrepare]` gates, e.g.:

```csharp
// Patch_FactionGenerator
[HarmonyPrepare] private static bool IsFilterEnabled() => WorldTechLevel.Settings.Filter_Factions;
```

The filtering primitive is a precomputed per-def index lookup, not a per-call scan:

```csharp
// TechLevelUtility
public static IEnumerable<T> FilterByMinRequiredTechLevel<T>(this IEnumerable<T> defs, TechLevel techLevel) where T : Def
{
    if ((int)techLevel == 7) return defs;                     // unrestricted short-circuit
    TechLevelDatabase<T>.EnsureInitialized();
    TechLevel[] data = TechLevelDatabase<T>.Levels;
    return defs.Where(def => def.index >= data.Length || (int)data[def.index] <= (int)techLevel);
}
```

Per-def tech levels come from 22 XML `TechLevelConfigDef` files (1462 lines total) with
`ifModPresent` conditions:

```xml
<WorldTechLevel.TechLevelConfigDef>
    <defName>WTL_FactionDefs</defName>
    <defType>FactionDef</defType>
    <entries>
        <li><defName>Empire</defName><techLevel>Undefined</techLevel><ifModPresent>oskarpotocki.vfe.empire</ifModPresent></li>
    </entries>
</WorldTechLevel.TechLevelConfigDef>
```

**Faction-level exemptions are first-class** — this is the hook Archinity wants for
"Glitterites exist from day one but stay out of reach":

```csharp
// TechLevelUtility
public static TechLevel CurrentFilterLevel(this FactionDef faction)
{
    if (faction != null && WorldTechLevel.Settings.FactionsExcluded.Value.Contains(faction.defName))
        return (TechLevel)7;      // this faction ignores the world ceiling entirely
    return WorldTechLevel.Current;
}
```

**The world tech level can be raised mid-game, and factions are retroactively added.** From
`Changelog.md` v1.1.0: *"Factions can now be retroactively added when changing the world tech
level in an ongoing game."* The implementation:

```csharp
// Patch_WITab_Planet — in-game change, via the planet inspect tab
TechLevel current = WorldTechLevel.Current;
WorldTechLevel.Current = value;
Current.Game.TechLevel().WorldTechLevel = value;
WorldTechLevel.Logger.Log("World tech level changed from " + current.SelectionLabel() + " to " + ...);
WorldTechLevelSettings.RefreshResearchViewWidth();
Window_AddFactions.OpenIfAnyAvailable(current);
```

Persistence is a proper `GameComponent`, with the static as a load-time mirror:

```csharp
// GameComponent_TechLevel
public override void ExposeData() => Scribe_Values.Look<TechLevel>(ref _worldTechLevel, "WorldTechLevel", (TechLevel)7, false);

// Patch_WorldGenerator
GenerateWorld_Prefix:          Current.Game.TechLevel().WorldTechLevel = WorldTechLevel.Current;
GenerateFromScribe_Prefix:     WorldTechLevel.Current = Current.Game.TechLevel().WorldTechLevel;
GenerateWithoutWorldData_Prefix: WorldTechLevel.Current = Current.Game.TechLevel().WorldTechLevel;

// Patch_MemoryUtility.ClearAllMapsAndWorld_Postfix — resets on quit-to-menu
WorldTechLevel.Current = (TechLevel)7;
```

A `ScenPart_WorldTechLevel` lets a scenario pre-set the level, which is how Archinity would
pin a neolithic start declaratively.

### MP determinism verdict: PASS, with two named caveats

No `System.Random`, no `DateTime.Now`, no `Environment.TickCount` anywhere in the assembly.
All randomness is Verse `Rand` sitting inside the vanilla generation paths WTL is filtering —
i.e. inside contexts Multiplayer already synchronises:

```csharp
// BuildingMaterialUtility (called from BaseGen during map generation)
if (Rand.Chance(num2) && (validator == null || validator(ThingDefOf.WoodLog)))
if (Rand.Chance(0.5f) && !map.IsPocketMap)

// ReplacementUtility (called from the same generation paths)
GenCollection.RandomElementByWeight<TechLevelDatabase<T>.Alternative>(array.Where(Filter), a => a.weight)
```

One patch is explicitly RNG-hygienic, pushing a deterministic seed derived from the def index
rather than consuming the ambient stream:

```csharp
// Patch_Sketch
Rand.PushState((int)def.index);
...
Rand.PopState();
```

That is exactly the discipline that keeps this MP-safe.

`WorldTechLevel.Current` is a static, but it is a **mirror of a scribed `GameComponent`**, set
from `GenerateFromScribe` / `GenerateWithoutWorldData` — so both clients derive it from the
same save data. This is the correct pattern, and the direct contrast with Lemmy's
backing-field poke.

Caveat 1 — **`Patch_WITab_Planet`'s "change tech level" float menu is unsynced UI**. That
`SetLevel()` closure writes `WorldTechLevel.Current` and the GameComponent directly from a
click. Same class of hazard as Faction Customizer: whichever player clicks it changes only
their own world. `Window_AddFactions` then compounds it with unsynced `Rand`:

```csharp
// Window_AddFactions.cs:147
for (int k = 0; k < Rand.RangeInclusive(3, 7); k++)
```

Caveat 2 — **the filter toggles are mod settings**, `Filter_Factions`, `Filter_WorldGenSteps`,
`FactionsExcluded`, and per-def `Overrides`. These gate whether Harmony patches are applied
at all (`[HarmonyPrepare]`), so a mismatch means the two clients are running structurally
different patch sets. This is precisely the CLAUDE.md settings-parity trap; snapshot
`config/ModSettings/` after any WTL settings change and treat it as load-bearing.

### Maintained?

Best-maintained mod in this set. `Version.txt` = `1.1.6`, a real `Changelog.md` with eight
released versions, a GitHub URL (`github.com/m00nl1ght-dev/WorldTechLevel`), 1.5 and 1.6
folders, declared `incompatibleWith` for the mods it overlaps (`ogam.rimedieval`,
`sickboywi.medieval.vanilla`, the `mlie.remove*stuff` family), and shipped compat patches for
seven named mods including VFECore, ResearchPal, Research Powl, Better Research Tabs, Dubs
Mint Menus, Real Ruins, Realistic Planets. v1.1.6 adds Odyssey landmark filtering — current
with the newest DLC.

= = =

## 5. Vanilla Outposts Expanded (2688941031)

### Is it faction behaviour? **No. It is a player colony feature.** Categorise accordingly.

Every outpost is created by the player forming a caravan and settling it, is owned by the
player faction, is staffed by the player's own colonists, and ships resources back to the
player's colony. From the About text: *"form a caravan, travel in the world map and create a
camp... Each of these camps ships resources to the player... build a new Outpost Drop off spot
to designate where the resources should appear."*

It does nothing whatsoever to NPC factions. If it was on a "faction mods" list, that is a
miscategorisation — the word "outpost" is doing the misleading.

### Mechanism

VOE is **content on top of a framework it does not own**. The `Outpost` base class,
`OutpostExtension`, the gizmos, the delivery lords and the WITabs all live in VEF's
`Outposts.dll` (`/294100/2023507013/1.6/Assemblies/Outposts.dll`, namespace `Outposts`). VOE
ships only 15 thin subclasses:

```csharp
// VOE/Outpost_Mining.cs
using Outposts;
public class Outpost_Mining : Outpost_ChooseResult
```

```csharp
// VOE/Outpost_Artillery.cs, Outpost_Defensive.cs, Outpost_Drilling.cs,
//     Outpost_Encampment.cs, Outpost_Farming.cs, Outpost_Hunting.cs,
//     Outpost_Scavenging.cs, Outpost_Science.cs, Outpost_Town.cs
public class Outpost_X : Outpost
```

Wired up in 13 `WorldObjectDef`s under `1.6/Defs/WorldObjectDefs/Outposts.xml`:

```xml
<WorldObjectDef ParentName="OutpostBase">
  <defName>Outpost_Farming</defName>
  <worldObjectClass>VOE.Outpost_Farming</worldObjectClass>
  <modExtensions>
    <li Class="Outposts.OutpostExtension_Choose">
      <DisallowedBiomes><li>Desert</li><li>ExtremeDesert</li></DisallowedBiomes>
      <TicksPerProduction>3600000</TicksPerProduction>
      <RequiredSkills><Plants>10</Plants></RequiredSkills>
      ...
```

Plus a separate optional `1.6/Factory/` module with its own `FactoryOutpost.dll`.

`VEF Outposts` is **already active** in Archinity's modlist
(`oskarpotocki.vanillafactionsexpanded.core`), so VOE adds no new framework dependency.

### MP determinism verdict: PASS on simulation, CONDITIONAL on interaction

The VEF `Outposts.dll` framework — which is where the actual work happens — is clean. Grep for
`new Random`, `DateTime.Now`, `Environment.TickCount`, `UnityEngine.Random`, and even
`Rand.` across all 29 decompiled files returns **zero hits**. All work is driven from the
world-object tick:

```csharp
// Outposts/Outpost.cs
public override void Tick()
public override void TickInterval(int delta)
{
    ((MapParent)this).TickInterval(delta);
    ...
}
```

`TickInterval(int delta)` is the 1.6 batched-tick signature, driven by the world object tick
loop, which Multiplayer executes identically on both clients. Pawn ageing, health and immunity
are all forwarded through it (`ageTracker.AgeTickInterval(delta)`,
`health.immunity.ImmunityHandlerTickInterval(delta)`).

VOE's own three `Rand` calls are all Verse `Rand` inside that same ticked path:

```csharp
// VOE/Outpost_Town.Produce() — called from the outpost production tick
if (Rand.Chance((float)capablePawn.skills.GetSkill(SkillDefOf.Social).Level * Chance / 100f))
{
    Pawn val = PawnGenerator.GeneratePawn(capablePawn.kindDef, capablePawn.Faction, null);
    ...
}
```

```csharp
// VOE/TravellingArtilleryStrike — Arrived(), on a ticked travelling world object
int num4 = Rand.Range(0, num3);
if (Rand.Chance(0.5f)) val4 = (ProjectileHitFlags)(-1);
```

Both sit inside synced tick contexts, so Verse `Rand` is deterministic there. That satisfies
the CLAUDE.md rule as written.

Two caveats, both real.

**Caveat A — mod settings feed directly into RNG thresholds.** VOE uses a `[PostToSetings]`
attribute to expose per-outpost tuning as mod settings:

```csharp
// VOE/Outpost_Town.cs
[PostToSetings(...)] public float Chance = 1f;
// VOE/Outpost_Mining.cs
[PostToSetings(...)] public float ProductionMultiplier = 1f;
```

and VEF stores them per-client:

```csharp
// Outposts/OutpostsSettings.cs
public DeliveryMethod DeliveryMethod;
public float ProductionMultiplier = 1f;
public float TimeMultiplier = 1f;
public Dictionary<string, OutpostSettings> SettingsPerOutpost = new Dictionary<string, OutpostSettings>();
```

`Chance` is multiplied straight into `Rand.Chance(... * Chance / 100f)`. A settings mismatch
between the two players changes the roll threshold and therefore the outcome of a synced
`Rand` draw — same seed, different comparison, different result. This is exactly the third
CLAUDE.md multiplayer trap ("identical mod settings — the one people miss"), with a concrete
mechanism attached. `ProductionMultiplier` and `TimeMultiplier` are the same class of problem
for yields and cadence.

**Caveat B — custom gizmos and dialogs are unlikely to be sync-wrapped.** The framework ships
`Dialog_CreateCamp`, `Dialog_GiveItems`, `Dialog_TakeItems`, `Dialog_RenameOutpost`, and
gizmos for abandon/add-to/remove-items. Multiplayer does not auto-sync arbitrary modded window
callbacks. The mod that normally provides those sync patches is **Multiplayer Compatibility
(`rwmt.compatibility`), which is not installed and not in `ModsConfig.xml`** — I verified the
core `Multiplayer.dll` contains no reference to `Outposts`, `VanillaExpanded`, `VFECore` or
`OskarPotocki` (zero string hits), so the core mod is definitely not carrying that compat
itself.

INFERRED (not verified — the mod is not on disk): Multiplayer Compatibility ships a
VanillaExpandedFramework patch that covers the Outposts module. If Archinity adopts VOE, adding
`rwmt.compatibility` is a prerequisite to test, not an optional nicety.

### Maintained?

Authors are legodude17 and Oskar Potocki (Vanilla Expanded team). `supportedVersions` 1.4 /
1.5 / 1.6 with a full assembly and def set per version. The 1.6 `VOE.dll` is compiled against
the 1.6 API (`PlanetTile`, `TickInterval(int delta)`, `PlanetLayer.Selected`), so it is a real
port, not a compatibility bump. Note the shipped `Source/` folder is **stale at 1.3 only** —
1.4/1.5/1.6 ship DLL-only, which is why the decompile was necessary. Actively maintained.

= = =

## 6. Lemmy Progression vs. World Tech Level — overlap, conflict, and which is which

**They do not overlap. They are framework and consumer, and the dependency is declared.**

Lemmy's `About.xml` lists `m00nl1ght.WorldTechLevel` as a hard `modDependency`, and every one
of its runtime patches is gated on that mod being active:

```csharp
public string RequiredModId { get { return "m00nl1ght.worldtechlevel"; } }
public bool ShouldApply() { return ModsConfig.IsActive(RequiredModId); }
```

- **World Tech Level is the framework.** It owns the tech ceiling, the persistence
  (`GameComponent_TechLevel`), the per-def tech database, and ~60 filter patches across
  research, items, pawns, quests, raids, ideology and world gen. Lemmy owns none of that
  machinery and could not function without it.
- **Lemmy Progression is a very thin content/policy layer**: roughly "let the player research
  past the ceiling" plus "when VFE Tribals fires an era advance, raise the ceiling and roll
  each faction for an upgrade". Three files do the real work; the rest is reflection plumbing
  and debug logging.

**Can they coexist?** Mechanically yes — Lemmy is designed to. But Lemmy relates to WTL
entirely through reflection and Harmony against WTL's *internals*, not a public API:

```csharp
cachedWorldTechLevelType = AccessTools.TypeByName("WorldTechLevel.WorldTechLevel");
...
cachedCurrentField = AccessTools.Field(cachedWorldTechLevelType, "<Current>k__BackingField");
```

and it patches `TechLevelUtility.PlayerResearchFilterLevel` by name-scanning WTL's assembly.
Any WTL refactor — of an auto-property, a private backing field, or a static utility method —
silently breaks Lemmy with a `Log.Warning`, not an error. WTL is on v1.1.6 and shipping
changes; Lemmy is on v0.0.1 and last touched 2025-08-14. That asymmetry is not stable.

There is also a genuine functional conflict that is *not* about MP: as established in §3,
Lemmy writes only the static mirror and never `Current.Game.TechLevel().WorldTechLevel`, so
WTL's own `GenerateFromScribe_Prefix` overwrites Lemmy's change on the next load. The two
mods disagree about what the world tech level is, and WTL wins.

**Which does the project want? World Tech Level, and only World Tech Level.**

WTL alone already delivers the stated principle — "don't get raided by mechanoids in the
Medieval era; don't get raided by medievals once you're glitterworld-tier" — because:

- it filters raid strategies, arrival modes, pawn gear, pawn kinds, quests and site parts
  against the ceiling, which is the actual mechanism behind that principle;
- **v1.1.0 already added mid-game tech level advancement with retroactive faction addition**
  (`Patch_WITab_Planet` + `Window_AddFactions.OpenIfAnyAvailable(current)`), which is the
  "world ages forward" half that Lemmy claims to add;
- `FactionsExcluded` gives per-faction exemptions from the ceiling, which is how Archinity
  keeps a glitterworld faction visible-but-unreachable from day one;
- `ScenPart_WorldTechLevel` pins the starting level declaratively from a scenario.

What WTL does *not* give you for free is the automatic, ritual-driven trigger — its
advancement is a manual float menu on the planet inspect tab, which is unsynced UI and
therefore unsafe to click mid-session. That gap is exactly the thing Archinity should close
itself, because Archinity already owns the progression trigger (`Archinity.Altar`,
`Archinity.Pacing`) and because closing it in-house means writing one MP-safe synced call
instead of importing 3000 lines of pre-alpha reflection.

The correct shape is: **WTL as the substrate, an Archinity-owned synced call that writes both
`WorldTechLevel.Current` and `Current.Game.TechLevel().WorldTechLevel`, and no Lemmy.**
Note that per CLAUDE.md this would need to go in `Archinity.Altar` (the one Harmony assembly)
rather than starting a second one — and it is an explicit decision, not a drive-by.

= = =

## 7. Does Faction Customizer overlap with Sensible Factions?

**No. Near-zero overlap.** They touch the same nouns and nothing else.

| | Sensible Factions | Faction Customizer |
| = | = | = |
| Nature | Automatic algorithm | Manual GUI editor |
| Runs | Once, `WorldGenerator.GenerateWorld` postfix | Only when a human opens the FC dialog |
| Changes | Which faction *owns* each existing settlement | Names, colours, leaders, ideologies, relations; settlement rename/move/create/delete; adds faction instances |
| Settlement count | Strictly preserved (quota == existing count) | Freely changed |
| Settlement positions | Never moved | `settlement.Tile = selectedTile` |
| Faction roster | Never changed | `Find.FactionManager.Add(newFaction)` |
| Input | 350-line hardcoded biome-affinity table + mod settings | Human clicks |
| Defs shipped | none | 2 keybinding defs |

The one point of contact: both end up deciding which faction is associated with which
settlement. Sensible Factions does it wholesale at world-gen by biome fit; Faction Customizer
does it one settlement at a time by hand. They are complementary — run Sensible Factions to
get a sane clustered starting distribution, then use Faction Customizer for the handful of
narrative fixups Archinity wants (naming the Glitterites' capital, forcing a specific faction
into a specific region, seeding a relation).

Ordering matters: Sensible Factions runs in a `GenerateWorld` postfix, so it fires *before*
any manual FC editing. Edit after generation, not before, or the redistribution will move
ownership out from under your edits.

Neither is a substitute for the other, and neither makes factions *act* — see §9.

= = =

## 8. Composition verdict

### What actually stacks

```
                    WTL (framework)          VEF Outposts (framework, already installed)
                        |                              |
                   [Lemmy: REJECT]                    VOE (content)
                                                       |
  Sensible Factions ..... world-gen only, no runtime overlap with anything
  Faction Customizer .... manual editor, no runtime overlap with anything
```

| Pair | Interaction |
| = | = |
| Sensible Factions + Faction Customizer | **Clean.** Different phases (auto world-gen vs. manual post-gen). Complementary. Do the FC edits *after* generation. |
| Sensible Factions + WTL | **Clean, with a sequencing note.** WTL's `Patch_FactionGenerator` filters which FactionDefs are configurable/instantiated at all; Sensible Factions then redistributes whatever survived. WTL culls, SF arranges. Both are `GenerateWorld`-adjacent — verify SF's `LongEventHandler.ExecuteWhenFinished` postfix lands after WTL's transpiled `InitializeFactions`. INFERRED: should be fine given SF defers to end-of-load-event, but worth one world-gen smoke test. |
| WTL + Lemmy | Declared dependency, but see §6 — Lemmy is MP-fatal and its writes get reverted by WTL on load. |
| VOE + anything here | **No interaction.** Player colony feature, orthogonal. |
| VOE + WTL | INFERRED minor: WTL filters items and stuff globally, so outpost production yields of above-ceiling items would be filtered by the same mechanism as everything else. Not a conflict — arguably desirable. Untested. |
| Faction Customizer + WTL | **Watch this one.** FC's `FCDialog_FactionDuringLanding` enumerates `FactionGenerator.ConfigurableFactions`, which WTL postfixes to filter by tech level. So FC's "add faction" list will already be tech-level-culled. That is correct behaviour, but it means a faction you expect to see in FC may be absent because WTL hid it — diagnose there before assuming FC is broken. |

### MP red flags, ranked

1. **Lemmy Progression — two `System.Random` instances in the faction-upgrade decision path.**
   Disqualifying. `random.NextDouble() < settings.factionUpgradeChance` at a default 0.5
   means every faction is an unsynced coin flip. Compounded by runtime `faction.def` mutation
   and reflection cache-clearing. Not usable, not patchable from outside.
2. **Faction Customizer — every mutation is unsynced UI.** `Find.WorldObjects.Add/Remove`,
   `Find.FactionManager.Add`, `relation.baseGoodwill = ...`, `settlement.Tile = ...`, plus
   `NameGenerator.GenerateName` consuming `Rand` on the randomize path. Safe while dormant;
   instant divergence on use. **Pre-game tool only.**
3. **World Tech Level — `Patch_WITab_Planet` in-game tech level change is unsynced UI**, and
   `Window_AddFactions` calls `Rand.RangeInclusive(3, 7)` from that click. Do not use the
   in-game changer during a live session; drive advancement from Archinity's own synced code.
4. **Mod-settings parity is load-bearing for both WTL and VOE**, not just cosmetic. WTL's
   `Filter_*` booleans gate `[HarmonyPrepare]` — a mismatch means different patch sets are
   installed on the two clients. VOE's `[PostToSetings]` `Chance` / `ProductionMultiplier`
   feed straight into `Rand.Chance(... * Chance / 100f)` thresholds. Re-snapshot
   `config/ModSettings/` after any change to either, per CLAUDE.md.
5. **Multiplayer Compatibility (`rwmt.compatibility`) is not installed.** Verified: core
   `Multiplayer.dll` has zero string references to `Outposts`, `VanillaExpanded`, `VFECore`,
   `OskarPotocki`, `WorldTechLevel`, `FactionCustomizer`, `SensibleFactions` or
   `LunarFramework`. Any modded gizmo/dialog sync must come from that mod or be written
   in-house. Prerequisite for VOE.

### Hard conflicts

- **Lemmy vs. WTL, functional (not just MP):** Lemmy writes `<Current>k__BackingField` only;
  WTL's `GenerateFromScribe_Prefix` restores from `GameComponent_TechLevel` on load. Lemmy's
  era advances are silently reverted. In MP the joining client loads the save and therefore
  starts at the pre-advance level — divergence on join.
- **Lemmy's trigger is absent from Archinity.** Hard deps `oskarpotocki.vfe.tribals` and
  `dankpyon.medieval.overhaul` are not in `ModsConfig.xml`. Its only trigger is a prefix on
  `GameComponent_Tribals.AdvanceToEra`, which does not exist here. With the current list,
  Lemmy installs nothing but its always-on `RootCauseInvestigationPatch` debug spam.
- **WTL declares `incompatibleWith`**: `ogam.rimedieval`, `sickboywi.medieval.vanilla`,
  `mlie.removeindustrialstuff`, `mlie.removemedievalstuff`, `mlie.removespacerstuff`. None
  are in Archinity's list — clear, but check before adding any tech-restriction mod later.
- **`fridgebaron.techblock` is already active** and also restricts progression. INFERRED and
  **untested**: WTL filters by a world-wide ceiling while TechBlock gates research
  differently, and both are settings-driven. This is the one overlap in the whole set I could
  not rule out from source, and it deserves its own investigation before WTL goes in. Note
  CLAUDE.md already flags TechBlock as settings-driven and desync-prone.

### Minimum useful set for "the world ages forward and factions feel distinct"

**Adopt two:**

1. **World Tech Level (3414187030)** — the only mod here that delivers "the world ages forward
   with the player". Nothing else in this set filters raids, gear, quests and research against
   a world tech ceiling, and nothing else has per-faction exemptions (`FactionsExcluded`) or a
   scenario part to pin the neolithic start. Best-maintained, cleanest RNG discipline, bundles
   its own framework. **Caveat: resolve the TechBlock overlap first.**
2. **Sensible Factions (3531306011)** — cheapest possible win for "factions feel distinct".
   One world-gen postfix, no runtime footprint, no MP risk, and it converts a uniformly
   scattered faction soup into "the tribals live in the jungle, the outlanders hold the
   temperate belt". Geography is what makes factions legible as separate powers on the world
   map. 1604 lines of readable source you can fork if it breaks.

**Keep, with a usage rule:**

3. **Faction Customizer (3336572602)** — already installed. Zero runtime cost while dormant,
   and it is how you give Archinity's factions their actual names and starting relations.
   **Rule: pre-game / world-setup only; never open the FC toolbar icon in a live MP session.**

**Reject:**

4. **Lemmy Progression (3548896697)** — MP-fatal (`System.Random` in the decision path),
   functionally broken against WTL (writes don't persist), trigger absent from the modlist,
   ships always-on debug spam, v0.0.1. Its *idea* — factions tech up alongside the player —
   is exactly right for Archinity and worth stealing; its implementation is not.

**Defer:**

5. **Vanilla Outposts Expanded (2688941031)** — good mod, clean framework, but it answers a
   different question. It is a player-colony logistics feature, not faction behaviour, and it
   contributes nothing to "the world ages forward" or "factions feel distinct". It also needs
   `rwmt.compatibility` added and tested first. Revisit if Archinity later wants player
   resource chains at mid-game; it is not part of the faction-and-progression minimum.

### The gap none of these fill

All five are **passive**. Sensible Factions arranges factions at birth; WTL constrains what
they may own; Faction Customizer lets a human relabel them; VOE is the player's own economy.
**None of them makes an NPC faction take an action of its own** — no faction expands, wars a
neighbour, loses ground, or pursues a goal. Archinity's stated aim of "factions as true forces
in the world, not vending machines plus raid spawners" is *not* met by any combination of
these five.

WTL + Sensible Factions gets you a world that is **tech-coherent and geographically
legible** — which is a real and necessary foundation, and is the honest ceiling of this set.
Faction *agency* is a separate problem needing either a different mod class (faction-war /
world-simulation mods) or first-party Archinity work in `Archinity.Altar`. Worth scoping
separately.
