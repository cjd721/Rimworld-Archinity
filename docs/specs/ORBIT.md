# Orbit

## Purpose and scope

> **Authority correction — 2026-09-13.** The planetary outcome is selected from live
> campaign state when the political resolution occurs; it is not a binary route chosen at
> world creation. It may name multiple factions. That result is frozen as an immutable
> snapshot before orbit is revealed, so later goodwill, settlement losses or faction
> changes cannot rewrite the orbital roster already created.

How the Odyssey orbit layer is populated, gated and revealed — and what that costs at
world creation.

This document owns the **orbital reveal**: what exists in orbit at worldgen, what the
player can see and select before the gate opens, the command that opens it, **and the
gate state itself** — the saved "has the reveal fired, and for whom". It owns the
consequences of `docs/plot/SPACER.md`'s *Departure* and *Orbit — Small Again* sections for
the save file.

It also owns **how an orbital location generates a playable map** — the platform genstep,
the layout defs behind it, and the pressurisation and life-support rules the interior then
obeys — stated in § *The build → 6*, and established on
[#66](https://github.com/cjd721/Rimworld-Archinity/issues/66). It does
**not** own what a Glitterite stronghold must *contain* — that is
`docs/requirements/GLITTERTECH.md`, which states it in prose and never as a map
requirement, and the flavour count comes from
[#46](https://github.com/cjd721/Rimworld-Archinity/issues/46) and
[#47](https://github.com/cjd721/Rimworld-Archinity/issues/47).

It does not own the political resolution that *decides* the reveal — that is
[`POLITICS.md`](POLITICS.md) and `docs/requirements/POLITICS.md`. It **does** own the
component that records the outcome's orbital consequence and fires the command; POLITICS.md
declines the state explicitly ("zero new saved state", correct for the goodwill ripple it is
about) and `docs/requirements/POLITICS.md` states no orbit requirement at all. The missing
requirement — that the planetary resolution yields a machine-readable outcome naming the
surviving institution — is
[#100](https://github.com/cjd721/Rimworld-Archinity/issues/100).

It does not own which orbital powers exist or what they are for — that is
[the faction grid](https://github.com/cjd721/Rimworld-Archinity/issues/34). It does not own
the orbital-access device, the Glitterite heists, or any beat — those are
`docs/plot/SPACER.md` and [#46](https://github.com/cjd721/Rimworld-Archinity/issues/46). It does
not own the pre-worldgen checklist it feeds — that is
[#18](https://github.com/cjd721/Rimworld-Archinity/issues/18).

Established on [Deferred orbital instantiation](https://github.com/cjd721/Rimworld-Archinity/issues/70).

## The build

**Generate the orbital factions at worldgen, hidden. Defer the settlements.**

The campaign wants orbit to arrive late and to arrive populated by whoever survived the
planet. Exactly one half of that is a worldgen decision.

> **A `Faction` can be hidden. A `WorldObject` cannot.**

There is no hidden, undiscovered or deferred-visibility flag on `WorldObject`,
`WorldObjectDef` or `Settlement` anywhere in 1.6 [V]. An orbital settlement that exists is
drawn the moment the player selects the Orbit layer. So "generate the settlements up front
and hide them" is not available. What *is* available is the faction-level switch, and it
turns out to drive the whole reveal.

### 1. Worldgen — the roster, complete and invisible

Every orbital `FactionDef` that will ever exist must be in the world-creation faction list.
`FactionManager.ExposeData` has no reconcile path, and `WorldGenStep_Factions` runs **once
per layer** — so the orbital roster freezes exactly as the planetside one does, on the same
trap (`docs/TRAPS.md` **T-07**) [V].

⚠️ **"In the world-creation faction list" is a stronger condition than "shipped as a def".**
`Current.CreatingWorld.info.factions` is built from `FactionGenerator.ConfigurableFactions`,
and that enumerable is patchable — World Tech Level postfixes it and can empty the orbital
roster outright. See *Failure and recovery*; it is the single largest risk this spec carries.

Every one of them ships `<hidden>true</hidden>`. `Faction.Hidden` is `hidden ?? def.hidden`
[V], and a hidden faction is excluded from both of the two ways a settlement reaches the
layer:

| Placement path | Gate |
|---|---|
| The one free settlement per faction, in `FactionGenerator.NewGeneratedFaction` | `if (!faction.Hidden && !factionDef.isPlayer)` |
| The bulk lottery, in `GenerateFactionsIntoWorldLayer` | local `Validator`: `!x.def.isPlayer && !x.Hidden && !x.temporary && CanExistOnLayer(...)` |

Both [V]. With no non-hidden orbit faction, `source.Any()` is false, the lottery loop never
runs, and **the Orbit layer generates with tiles and zero world objects** [V].

The factions themselves are fully built: `loadID`, name, colour, ideo, leader and initial
relations against every other faction, all rolled at worldgen inside worldgen's seeded
`Rand` [V]. They simply hold nothing and appear nowhere.

⚠️ **`Hidden` does not suppress hostile raids.** `IncidentWorker_RaidFriendly` checks
`!f.Hidden`; `IncidentWorker_RaidEnemy` does not [V]. This is deliberate — it is how
Odyssey's hidden `Salvagers` raid you. Raid gating stays where it already is:
`earliestRaidDays` on the def plus Ignorance Is Bliss's tech band, with `docs/TRAPS.md`
**T-17** on the fail-open pool.

### 2. Before the reveal — vanilla already draws the locked door

`OrbitLayer.CanSelectLayer()` returns `"CannotSelectOrbitReason".Translate()` whenever
`!Find.WorldObjects.AnyWorldObjectOnLayer(this)`, and `WorldGrid.GetGizmos` renders the
view-orbit command **disabled with that reason** [V]. The string is Odyssey's own —
**"No discovered orbital locations."** — shipped in eighteen languages.

So the pre-reveal state is a visible, greyed, explained button. That is the display half of
this spec and it costs nothing.

⚠️ It costs nothing **and it is not exclusively ours**. `AnyWorldObjectOnLayer` counts any
world object, including Odyssey's own orbital quest sites. Six shipped `QuestScriptDef`s can
open the gate before the politics do; the bound on them is a research gate, not a design
guarantee. See *Failure and recovery*.

**`viewGizmoOnlyVisibleWithDirectConnection` is a different and much weaker gate**, and we
have been reading it as this one. It tests
`Find.WorldSelector.SelectedLayer.HasConnectionFromTo(layer)` — a **scenario-declared layer
connection**, not player presence [V]. `ScenarioBase` declares `Surface → Orbit` and
`Orbit → Surface` at worldgen, `Archinity_SeedOfArchinity` inherits both (list children are
appended by inheritance, **T-05**), and `ScenarioMaker` and `Scenario.ExposeData` each
re-inject them when Odyssey is active [V]. **The gizmo is therefore visible from the first
tick of any Odyssey game, patched or not.**

### 3. The reveal — one synced command

A `[SyncMethod]` taking the factions to reveal and how many settlements each gets:

```csharp
PlanetLayer orbit = Find.WorldGrid.Orbit;
if (orbit == null) return;                  // see the condition below — not Odyssey alone

faction.hidden = false;                     // scribed bool?, overrides def.hidden
// optional: faction.def = <ascended tier>; // the #8 swap, with its leak list
for (int i = 0; i < count; i++)
{
    var wo = WorldObjectMaker.MakeWorldObject(orbit.Def.SettlementWorldObjectDef);
    wo.SetFaction(faction);
    wo.Tile = TileFinder.RandomSettlementTileFor(orbit, faction);
    ((INameableWorldObject)wo).Name = SettlementNameGenerator.GenerateSettlementName(wo);
    Find.WorldObjects.Add(wo);
}
```

That is `GenerateFactionsIntoWorldLayer`'s own placement block, lifted verbatim [V].
`Def.SettlementWorldObjectDef` resolves to `SpaceSettlement` from the `PlanetLayerDef` — so
the placed object inherits `requiresSignalJammerToReach`, the `SettlementPlatform` map
generator and the `(200,1,200)` override size for free [V].

⚠️ **`Find.WorldGrid.Orbit` is not non-null on "Odyssey active" alone.**
`WorldGrid.CreateRequiredLayers` assigns `orbit` only when the scenario contains a
`ScenPart_PlanetLayer` whose `layer == PlanetLayerDefOf.Orbit` **and** Odyssey is active [V].
That holds for us — `ScenarioBase` declares the part, and `ScenarioMaker` and
`Scenario.ExposeData` each re-inject it — but it is a scenario condition wearing a DLC
condition's clothes, and a scenario edit can revoke it silently. **Null-guard the property in
`RevealOrbit`** rather than relying on the DLC check.

Placing the first settlement is the entire unlock: `CanSelectLayer` re-evaluates from
`AnyWorldObjectOnLayer` every frame, with no cache and no invalidation call [V].

### 4. "Who came with you" is not a new-faction question

Each terrestrial institution selected by the planetary resolution **is already a
`Faction`**, on the surface, with its relations, its name and its history intact. None
needs creating in orbit, and the outcome may select more than one.

`FactionDef.layerWhitelist` / `layerBlacklist` are read at **exactly one site in the whole
1.6 assembly** — `FactionGenerator.CanExistOnLayer`, reached only from
`WorldGenStep_Factions.GenerateFresh` [V]. Nothing at runtime ever re-checks which layer a
faction may hold territory on. So step 3 run against a surface faction, with no `hidden`
write, gives it an orbital presence and the engine has no opinion.

If it should read as *ascended* rather than merely present, swap `Faction.def` — the
machinery [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) verified end to end, with
its leak list: null `Settlement.cachedMat` by reflection (**T-12**), null
`allegianceColor`, handle `Faction.Color`, and set `replacesFaction` down the chain
(**T-13**). Never write `FactionDef.techLevel` (**T-11**).

### 5. The gate state — ours, and it is new code

**This document owns the reveal-gate `WorldComponent`.** Earlier drafts hung it on
"the political `WorldComponent`, if it exists by then". No such component is planned:
`docs/specs/POLITICS.md` § *The build* declines it outright — *"Zero maintenance, zero new
saved state… A `WorldComponent` is tick-safe but the ripple is event-driven; nothing needs
polling."* That statement is correct about the goodwill ripple, and it means the reveal gate
has no host. It gets one here.

A `WorldComponent` holding the immutable outcome, reveal state and the synced command:

```csharp
PlanetaryOutcome outcome;            // written once at political resolution
bool revealed;                       // Scribe_Values.Look(ref revealed, "orbitRevealed")
List<Faction> revealedFactions;      // Scribe_Collections.Look(..., LookMode.Reference)

PlanetaryOutcome
    PoliticalRoute route;            // Church | Schism | Independent
    List<Faction> ascendingFactions;  // zero, one or many; snapshot at resolution
    List<Faction> defeatedFactions;   // historical result, not a live query
    List<Faction> absorbedFactions;   // historical result, not a live query
    int resolvedTick;
```

This is **new code in a new component**, not a free field on someone else's. It needs no
ticking. `ResolveOutcome` refuses a second write; `RevealOrbit` reads only the snapshot.

**What sets it is partially settled.** The political resolution evaluates authored rules
against live state and writes the snapshot once. [#100](https://github.com/cjd721/Rimworld-Archinity/issues/100)
still owns the exact conditions and priority/tie rules; it no longer needs to choose one
hard-coded faction or decide whether the result stays live. The reveal beat itself is
[#46](https://github.com/cjd721/Rimworld-Archinity/issues/46).

### 6. The stronghold interior — Odyssey generates it, and every knob is XML

**Use `GenStep_OrbitalPlatform` with our own `StructureLayoutDef`. Do not put KCSG on the
orbit layer.**

`RimWorld.GenStep_OrbitalPlatform` paints a real floor, generates a procedural room graph,
roofs it, sets room temperature, installs the life-support unit, adds landing docks or a
ring, mounts cannons and scatters exterior debris — and **every one of its fields is set
from XML** [V]: `factionDef`, `layoutDef`, `useSiteFaction`, `temperature`,
`spawnSentryDrones`, `cannonDef`, `platformTerrain`, `orbitalDebrisDef`, `fogOfWarColor`,
`exteriorPrefabs`.

> **A `StructureLayoutDef` is a generator, not a floor plan.**

`LayoutWorker_OrbitalPlatform.GetStructureLayout` calls
`RoomLayoutGenerator.GenerateRandomLayout(rect, 10, 10, 0.1f, canRemoveRooms: true,
generateDoors: false, maxMergeRoomsRange: 2~4, …, corridorExpansion: 2)`, and
`GenStep_OrbitalPlatform.GeneratePlatform` picks `SizeRange 70~80` on both axes with
`Rot4.Random` before it; `Generate` then rolls a ring (33 %), large docks or small docks
[V]. `LayoutDef.roomDefs` is a weighted list with per-def `countRange`, drawn per map.
**One layout def therefore yields a different stronghold every time**, so the campaign's
cost is one layout per *flavour*, not per encounter.

Two routes, same genstep, chosen by what the stronghold is on the world map.

**A — the stronghold as a faction settlement.** `Settlement.MapGeneratorDef` has **three**
branches, not two: `def.mapGenerator` when the `WorldObjectDef` sets one, else
**`Base_Player` if the settlement's faction is the player's**, else `Base_Faction` [V]. The
player branch does not arise for a Glitterite station, but it is the reason the property
cannot be read as "the def or the faction default". `SpaceSettlement` sets
`<mapGenerator>SettlementPlatform</mapGenerator>` and `<overrideMapSize>(200,1,200)</…>`
[V]. So a per-faction platform is an Archinity `WorldObjectDef` whose `mapGenerator` names
an Archinity `MapGeneratorDef` parented to `SpaceMapGenerator`, whose `genSteps` are our
`GenStepDef` (order 200, `genStep Class="GenStep_OrbitalPlatform"`,
`useSiteFaction: true`) and vanilla `SettlementPawnsLoot` (order 700). That is
Odyssey's own `SettlementPlatform` block with two defNames changed [V].

> **This saves a Harmony patch, and it is the seam with § *The build → 3*.** Vanilla
> places settlements from `PlanetLayerDef.SettlementWorldObjectDef` — one type per layer —
> so Better Traders Guild has to swap the generator with a Harmony patch on
> `MapParent.MapGeneratorDef` for its faction's settlements. **`RevealOrbit` constructs the
> world objects itself**, so it selects a per-faction `WorldObjectDef` instead of
> `orbit.Def.SettlementWorldObjectDef`. One argument on a command we already cost.

**B — the stronghold as a quest site.** `SitePartDef` plus a `GenStepDef` with
`<linkWithSite>`, reached by a quest using `QuestNode_Root_Site` with
`<layerWhitelist><li>Orbit</li></layerWhitelist>` and `<worldObjectDef>SpaceSite</…>`.
`SpaceSite` sets `<mapGenerator>Space</mapGenerator>` and `Site.ExtraGenStepDefs` appends
the site part's gensteps to it [V], so `GenStep_Space` voids the map at order 100 and our
platform genstep builds on it at 200. This is `Opportunity_AbandonedPlatform` verbatim [V].

**The layout def itself is ~40 lines**, parented to Odyssey's `OrbitalAncientPlatformBase`,
which already supplies `workerClass LayoutWorker_OrbitalPlatform`, `terrainDef` and
`surroundingTerrainDef OrbitalPlatform`, `wallDef OrbitalAncientFortifiedWall`,
`exteriorDoorDef AncientBlastDoor`, `corridorDef`, `corridorShapes` and `wallLampDef` [V].
It needs `roomDefs` (Odyssey's own shipped `LayoutRoomDef`s are usable unchanged), an
`importantRoomDef` for the objective, a `LifeSupportUnit` wall attachment, and a `parts`
entry if we want breaches.

⚠️ **The roofs come from the room defs, not from a `roofs:` argument — and the argument is
dead code.** An earlier draft credited `LayoutWorker.Spawn(…, roofs: true, …)` with roofing
and therefore de-fogging the interior. It does not:
**`LayoutWorker_Structure.Spawn` ignores its own `roofs` argument and calls
`base.Spawn(…, roofs: false, …)` unconditionally**, and `LayoutWorker_OrbitalPlatform`
inherits that override [V]. What roofs the interior is the sketch —
`LayoutRoomDef.roofDef`, with `noRoof` to suppress it — applied per room as the layout
spawns [V]. **A `roomDefs` entry that leaves `roofDef` unset, or sets `noRoof`, is an
unroofed room; an unroofed room is `ExposedToSpace` and can never pressurise.** Check
`roofDef` on every Odyssey room def before borrowing it into a layout, and read the fog
behaviour below as *unproven* rather than settled: it follows from roofs existing, and the
roofs are now known to arrive by a different route than the one the claim was built on.

⚠️ **`<temperature>20</temperature>` on the genstep is mandatory.**
`PostMapInitialized` calls `MapGenUtility.SetMapRoomTemperature(map, layoutDef, SpawnTemp)`
and `SpawnTemp` is `temperature ?? -75f` [V]. Omit it and the interior generates at the
biome's −75 °C with no error.

⚠️ **Write `<StructureLayoutDef>`, never `<KCSG.StructureLayoutDef>`.** Two unrelated
classes share the short name. `GenTypes.GetTypeInAnyAssembly` consults
`TryGetTypeInIgnoredNamespace` first and `RimWorld` is an ignored namespace [V], so the
bare node always binds to the vanilla class. The same dictionary is **last-writer-wins**
over every type whose namespace is null or ignored, and vanilla's `LayoutWorker_*` classes
have **no namespace at all** [V] — so any `LayoutWorker` subclass we author goes in an
`Archinity.*` namespace and is referenced fully qualified. Registered as
[`docs/TRAPS.md` T-55](../TRAPS.md).

#### Pressurisation, stated exactly

Two different rules exist in 1.6 and only one governs a station.

| Rule | Tests | Governs |
|---|---|---|
| `Room.ExposedToSpace` → `District.ExposedVacuumCount` | a cell is exposed if **unroofed** *or* its terrain sets `exposesToVacuum` [V] | `Room.Vacuum`, and therefore `VacuumExposure` on pawns |
| `VacuumUtility.IsRoomAirtight` → `IsRoomDirectlyOpenToOutside` | the above **plus** `terrainGrid.FoundationAt(cell).IsSubstructure` on every cell [V] | the gravship budget — **not** breathability |

`TerrainDefOf.Space` sets `exposesToVacuum true`; `OrbitalPlatform` (`ParentName
PlatformBase`) does not [V]. **That is why a KCSG structure on a space map can never
pressurise**: its `.` cells stay `Space` inside the sealed room, `ExposedCountStopAt(1)`
returns 1 on the first one, `Room.Vacuum` pins to 1 forever, and
`Building_LifeSupportUnit.ComputeVacuum`'s `!Room.ExposedToSpace` guard makes the pump a
no-op [V]. An orbital-platform room is pressurised and is **not** `IsRoomAirtight`;
`OrbitalPlatform` carries no `Substructure` tag, and `TerrainDef.IsSubstructure` is
`HasTag("Substructure")` [V].

- **The hull is airtight by def, not by stuff.** `OrbitalAncientFortifiedWall` inherits
  `AncientFortifiedWall`, which sets `<isAirtight>true</isAirtight>` outright [V], so
  `docs/TRAPS.md` **T-47** does not bite the generated hull. It bites everything the player
  builds afterwards: that wall is `neverBuildable: true`, `deconstructible: false` [V], so
  repairs and extensions are steel or plasteel `Wall` or they leak.
- **Life support ships in the layout.** `<wallAttachments><LifeSupportUnit>` appears on
  `OrbitalSettlementPlatform`, `Opportunity_AbandonedPlatform` and BTG's platform alike
  [V]. `Building_LifeSupportUnit.TickRare` drives its room toward 20 °C on a 30 J/s budget
  and, when the room is sealed, subtracts `100/CellCount * 0.05 * 4.1667` vacuum per rare
  tick [V]. Its `CompProperties_Power` is `compClass CompPowerPlant`,
  `basePowerConsumption -3200`, `transmitsPower true` — it is the platform's **generator**,
  not a drain, and `TickRare` checks no power flag [V].
- **What the founders need outside.** `VacuumUtility.PawnVacuumTickInterval` applies
  `VacuumExposure` at `0.02 * vacuum * max(1 - VacuumResistance, 0)` per 60 ticks, and only
  above `vacuum >= 0.5` [V]. `Apparel_Vacsuit` is `0.32` and `Apparel_VacsuitHelmet` is
  `0.69` [V] — the pair reads as designed to zero the term [I]. Vacuum **burns** are a
  separate track gated on `IsProtectiveApparel` coverage per body part [V]. The exterior
  deck between shuttle and airlock is always vacuum: **suit and helmet for everyone
  boarding.**

#### Whether a breach is wanted — per layout, one line, already shipped

`RoomPartDef Breached` (`RoomPart_Breached`) blows a 2–4 cell hole in a room's outer wall,
damages the flanking edifices to 40–80 % HP and scatters rubble [V]. It is applied per room
through `LayoutDef.parts` as `LayoutPartParms{ def, chance = 1f }`, and Odyssey ships
`<parts><Breached>0.25</Breached><Gore>0.25</Gore></parts>` on
`Opportunity_AbandonedPlatform` [V]. `RoomPart_Breached.CanRemoveWalls` refuses the
`importantRoomDef` and any room whose def sets `canRemoveBorderDoors` /
`canRemoveBorderWalls` [V], so the objective room is never the one holed. `LayoutRoomDef.noRoof`
is the second lever, for a deliberately open bay. **No blanket decision is needed.**

#### The hacking seam

`OrbitalAncientPlatformBase`'s `exteriorDoorDef` is `AncientBlastDoor`, whose `thingClass`
is `Building_HackableDoor` [V]. **Every orbital stronghold's outer doors are hackable by
vanilla default**, and `StructureLayoutDef.ensureOneDoorUnlocked` is the switch deciding
whether a hack is required to get in at all. The lever is recorded here; the mechanism is
[#58](https://github.com/cjd721/Rimworld-Archinity/issues/58)'s and lives in
`docs/specs/HACKING.md`.

#### State, change and display — the remaining three legs, all of them vanilla's

**State: none.** The map half stores nothing of ours. The generated stronghold is an
ordinary `Map`; no component, no scribed field, no def-keyed table. The reveal gate in
§ *The build → 5* is this spec's only new state, and it belongs to the world half, not the
map half. (How the map itself persists is the next section: `Map.layoutStructureSketches`
is scribed by vanilla.)

**Change: generation only, once, at first entry.** `GenStep_OrbitalPlatform.Generate` runs
inside `MapGenerator.GenerateContentsIntoMap`, then `PostMapInitialized` sets room
temperature [V]. Nothing re-runs it — `MapGenerator.GenerateMap` runs once per map. After
generation the only quantity that moves is `Room.Vacuum`, driven by
`Building_LifeSupportUnit.TickRare` and by whatever the players blow open [V]. There is no
mid-game mutation path and no tick of ours.

**Display: the map, and one building.** The stronghold is seen by being entered; the
world-side presentation is the `WorldObjectDef`'s ordinary `expandingIconTexture` /
`expandingIconColor`, shared with every other settlement. The piece worth naming is that
**`Building_LifeSupportUnit` is the player-legible pressurisation control** — a physical
object standing in a room, read against vanilla's vacuum overlay, which is why the
pressurisation rules above need no UI of ours. **Nothing here adds a window, a gizmo or an
alert.**

### The escape hatch, and why we are not using it

`FactionGenerator.CreateFactionAndAddToManager` is public static and is a **legitimate
runtime route, not a repair**. It runs the full generation path; `FactionManager.Add`
recaches and notifies every loaded map; Multiplayer patches `Add` specifically to register
the new faction in `sharedCrossRefs`; and RimPacts ships it in production for civil-war
splinters and exile restoration [V].

⚠️ **The shipped precedent is for the wrong overload.** Both call sites in
`RimPacts.WorldComponent_RimPacts` use the **single-argument
`CreateFactionAndAddToManager(FactionDef)`**, which hardcodes `Find.WorldGrid.Surface` [V].
The **layer-taking overload** — the one this spec would need, and the one earlier drafts
named — has **no shipped precedent anywhere in the corpus** [V]. So the route is verified by
reading and by a surface-layer production precedent, and by nothing at all on a non-surface
layer.

It is still the wrong tool here, precedent or not. It re-rolls a name, a colour, an ideo and
a leader and places a freebie settlement the caller must hunt down and `Destroy()` —
RimPacts does exactly that — all of it `Rand`. The hidden-at-worldgen route makes the reveal
a `bool?` write plus placement, and only the placement touches `Rand`. Keep the hatch
documented as available; do not build on it.

### Cost

| Piece | Kind | Estimate | Target |
|---|---|---|---|
| Hide `TradersGuild` at worldgen | XML patch | ~10 lines | `Archinity.Pacing/Patches/Orbit_HiddenAtWorldgen.xml` (new) |
| `<hidden>true</hidden>` on our two orbit factions | XML edit | 2 lines | `Factions_FreeCompanies.xml`, `Factions_Glitterites.xml` |
| **Delete `Orbit_AlwaysViewable.xml`** | deletion | — | `Archinity.Pacing/Patches/` |
| Correct `Orbit_LayerSize.xml`'s arithmetic, re-decide 6 vs 5 | XML comment | ~8 lines | `Archinity.Pacing/Patches/Orbit_LayerSize.xml` |
| Lock the six orbital opportunity quests out of the pool, if #20 puts `OrbitalTech` before the resolution | XML patch | ~15 lines | `Archinity.Pacing/Patches/` (new) |
| `RevealOrbit(List<Faction>, int)` synced command | **new C#** | **~60–80 lines** | the assembly we already ship |
| Reveal-gate `WorldComponent` — two scribed fields, no tick | **new C#** | ~15 lines | the assembly we already ship, **owned by this spec** |
| `StructureLayoutDef` per stronghold flavour, reusing Odyssey's `LayoutRoomDef`s | XML | ~40–60 lines each | `Defs/StructureLayoutDefs/` (new) |
| `GenStepDef` wrapping `GenStep_OrbitalPlatform` | XML | ~15 lines each | `Defs/GenStepDefs/` (new) |
| `MapGeneratorDef` + `WorldObjectDef` (route A), or `SitePartDef` + quest patch (route B) | XML | ~30 lines each | `Defs/` (new) |
| Bespoke `LayoutRoomDef` — the vault, the archive | XML **content** | ~60–120 lines each | `Defs/LayoutRoomDefs/` (new) |
| `TechLevelConfigDef` rows for every Archinity orbital `GenStepDef` | XML patch | ~10 lines | the same file as the faction exemption (**T-54**) |
| Per-faction `WorldObjectDef` selection inside `RevealOrbit` | **new C#** | **~1 line** | inside the command already costed above |

**~76–96 lines of new C#** (60–80 + 15 + 1), no new assembly. The component is new; nothing
else provides it. **Map generation adds no C# at all** — the genstep, the layout worker, the
room generator and the life-support building are all vanilla. The ceiling, if we want Better
Traders Guild's level of polish, is its actual shipped size: a 128-line
`StructureLayoutDef`, ~1,500 lines of `LayoutRoomDef` across **19** rooms, and a
`LayoutWorker` subclass for post-spawn decoration. That is content, and it is the maximum
rather than the entry price.

**Zeroing `TradersGuild`'s worldgen count is not taken.** Conrad, 2026-09-15: *"We want the
Traders Guild 100% in the game."* The faction is generated and hidden; its count is never
zeroed. Zeroing would have removed, permanently and at worldgen (**T-07**),
[`CURRENCIES.md`](CURRENCIES.md)'s Traders Guild exchange venue and the Odyssey orbital
traders `Orbital_Exotic` / `Orbital_CombatSupplier`, which name `TradersGuild` and spawn only
while it exists (`IncidentWorker_OrbitalTraderArrival.CanSpawn` [V]) — the Empire-tagged
techprint route [`RELIGION.md`](RELIGION.md) decision 21 relies on once the Church turns
hostile. Recorded on [the faction grid](https://github.com/cjd721/Rimworld-Archinity/issues/34),
which owns the worldgen column. Had it been taken, it would first have required checking
`replacesFaction` — the prune runs over defs you excluded (**T-10**).

## Persistence and multiplayer

**The reveal introduces almost no new saved state, and what it does introduce is ours.**
`Faction.hidden` is already scribed (`Scribe_Values.Look(ref hidden, "hidden")`) [V] and the
settlements are ordinary `WorldObject`s in `WorldObjectsHolder` [V]. The only new state is
the gate itself — one `bool` and a `List<Faction>` reference list — and it lives on **this
spec's `WorldComponent`** (§ *The build → 5*), not on a political component that does not
exist.

**Added to a save that predates it**, `revealed` loads `false` and the list loads null,
which correctly means the reveal has not happened. No back-compat shim.

⚠️ **The design is only available on a world generated after the `<hidden>` patch lands.**
A world generated today has three non-hidden orbit factions and their settlements already
placed; `Faction.hidden` is read from the instance and the settlements exist, so no patch
retracts them. This is a
[#18](https://github.com/cjd721/Rimworld-Archinity/issues/18) item and the strongest reason to
settle it before world creation.

**Multiplayer.** `PlanetLayer` and `PlanetTile` both have implicit sync workers in
`SyncDictRimWorld` — the layer writes its `LayerID` and reads back
`Find.WorldGrid.PlanetLayers[id]` [V] — so a command taking the orbit layer or an orbital
tile serialises for free. `Faction` has an explicit worker keyed on `loadID`, and `Def`
subclasses serialise generically [V].

**Nothing is covered for free.** `WorldObject.SetFaction` has no `SyncMethod`, and
`CreateFactionAndAddToManager` appears nowhere in `Multiplayer.dll` — ASCII and UTF-16LE,
both on-disk copies, SHA-1 identical so **T-22** is not in play [V]. The command must be
ours.

**The `Rand` surface is exactly two calls per settlement**: `RandomSettlementTileFor` and
`GenerateSettlementName` [V]. The `hidden` write and `SetFaction` consume none. Both sit
inside the one synced command, so both clients walk the same sequence.
`docs/engine/determinism.md` owns the general model.

**Map generation stores nothing of ours and is MP-safe by construction.** The generated
map is an ordinary `Map`; `Map.ExposeData` already scribes the room graph
(`Scribe_Collections.Look(ref layoutStructureSketches, "layoutStructureSketches",
LookMode.Deep)`) [V], which is what lets `SetMapRoomTemperature` and the debug room views
survive a reload. Added to an existing save these are defs only: nothing is retroactive,
and an orbital map already generated keeps what it was generated with, because
`MapGenerator.GenerateMap` runs once per map.

`GenStep_OrbitalPlatform`, `RoomLayoutGenerator`, `LayoutWorker`, `LayoutWorker_Structure`
and `PrefabUtility` contain **zero** `System.Random` constructions [V] — everything is
`Verse.Rand`, inside `MapGenerator.GenerateContentsIntoMap`'s per-genstep
`Rand.PushState(); Rand.Seed = Gen.HashCombineInt(seed, GetSeedPart(…))`, itself seeded
from `Gen.HashCombineInt(Find.World.info.Seed, parent.Tile.GetHashCode())`, both
cross-client identical ([#88](https://github.com/cjd721/Rimworld-Archinity/issues/88), [V]).
**This route is immune to `docs/TRAPS.md` T-33 outright** rather than relying on
Multiplayer Compatibility's `PatchKCSG` allowlist entry, and it removes VEF from this
spec's dependency set entirely. #88 recommended authoring the strongholds as
`structureLayoutDefs`/`tiledStructures` rather than `settlementLayoutDefs`; not touching
KCSG at all is the stronger form of the same move.

## Failure and recovery

### World Tech Level deletes the orbital roster at world creation

**Registered as [`docs/TRAPS.md` T-54](../TRAPS.md).** It earns its own ID rather than a line
on T-07 because a reader who has obeyed T-07 in full — authored the roster, frozen it before
worldgen — is still completely exposed: the defs are correct and a third-party postfix removes
them anyway. T-54 also carries the second leg, `GenStepDef` filtering — which has **no
`ApplyExclusions` (settings) escape hatch**, but *is* covered by `ApplyOverrides` and so by a
`TechLevelConfigDef`, and which **T-54 records as recoverable**: unlike the faction roster it
is re-evaluated per map rather than baked into the world, so the fix works on an existing
save once the cause is found. Only the faction leg is permanent.

**This is T-07 firing on the campaign's opening move, and #70's wide pass missed it.** The
resolution read World Tech Level's **transpiler** on `FactionGenerator.InitializeFactions`,
correctly proved that call site to be inside the `factions == null` dev-quickstart branch
(**T-09**), and wrote *"WTL filters the world-creation UI list, not the generation. Not a
hazard for us."* **The sibling postfix rode in on that finding, and the postfix is the live
one.**

`WorldTechLevel.Patches.Patch_FactionGenerator.GetConfigurableFactions` is a Harmony
**postfix on `FactionGenerator.ConfigurableFactions`**, filtering the enumerable to defs
whose `MinRequiredTechLevel <= WorldTechLevel.Current` [V].

`ConfigurableFactions` is not a UI convenience. **`Page_CreateWorldParams.ResetFactionCounts()`
builds `Current.CreatingWorld.info.factions` from precisely that enumerable, and
`WorldGenStep_Factions.GenerateFresh` consumes `Current.CreatingWorld.info.factions`** [V].
The world-creation list **is** the generation input; there is no second, unfiltered path.

So on a **Neolithic** world-tech-level start with World Tech Level active, every Spacer
orbital faction — `TradersGuild`, `Salvagers`, `Archinity_Glitterites`,
`Archinity_FreeCompanies` — drops out of `info.factions` before `WorldGenStep_Factions` ever
runs. Silently, permanently, with no error, no warning and no log line, and no repair short
of a new world (**T-07**).

**Note the failure is not the one this spec is built around.** The design wants the orbital
factions *generated and hidden*. WTL's filter removes them from the roster entirely, so
there is nothing to unhide: the reveal command has an empty argument, orbit stays greyed
forever, and the only surviving path is § *The build → 4* — giving orbital ground to a
surface faction that was never filtered.

**World Tech Level is currently inactive in `config/ModsConfig.xml`.** That is not a
defence. The enabled set is an accident of the last playtest, and this decision is taken
once, irrevocably, at world creation.

**The mitigation is one XML file, and it is the mod's own shipped pattern.** Read end to end
against `3414187030/1.6/Lunar/Components/WorldTechLevel.dll` (the real assembly; `1.6/Assemblies/`
holds only `LunarLoader.dll`).

The postfix does **not** call `CurrentFilterLevel`. It reads a precomputed array —
`TechLevelUtility.MinRequiredTechLevel<T>()` is a bare `TechLevelDatabase<T>.Levels[def.index]`
lookup [V]. The exemption is baked into that array at startup instead:
`DefTechLevels.Initialize()` runs `TechLevelDatabase<FactionDef>.ApplyOverrides()` and then
`ApplyExclusions(WorldTechLevel.Settings.FactionsExcluded)`, and `ApplyExclusions` writes
`Levels[index] = TechLevel.Undefined` [V]. `Undefined` is `0`, the array's *unrestricted*
sentinel — `0 <= Current` for every selectable level — so an exempt faction survives the
postfix on a Neolithic world [V]. **`FactionDef` is the only def type in that method that gets
an `ApplyExclusions` call.**

That corrects the lead in `docs/engine/research-and-tech-tiers.md`: the exemption is real, but
it arrives by a different route than `CurrentFilterLevel`, which the postfix never touches.

Two routes follow, and the XML one is better:

- **`Settings.FactionsExcluded`** works but is a **mod setting** — **T-18** sync surface, per
  install, and it cannot ship in a def. Two clients whose lists differ build different faction
  databases.
- **`WorldTechLevel.TechLevelConfigDef`** is a public `Def` loadable from any mod's `Defs/`, and
  `ApplyOverrides` runs from it immediately before `ApplyExclusions` [V]. WTL ships exactly this
  for VFE Empire in `1.6/Defs/TechLevels_FactionDefs.xml` — `<defName>Empire</defName>`,
  `<techLevel>Undefined</techLevel>`, `<ifModPresent>`. Ours is the same shape with the four
  orbital defNames and a `MayRequire` on WTL's packageId so it is skipped when WTL is absent.
  **~20 lines of XML, no C#, no Harmony, no setting.**

  **The same def must also carry `Empire → Undefined`, with no VFE Empire guard.** WTL's own
  `Empire` entry applies only under `<ifModPresent>oskarpotocki.vfe.empire</ifModPresent>` [V].
  The Church *is* Royalty's `Empire`, transformed in place
  ([`RELIGION.md`](RELIGION.md) § *The build — Exaltation* §3), so without VFE Empire an Ultra
  Church is stripped from a Neolithic world's roster (**T-54**), permanently (**T-07**). The
  `MayRequire` on WTL itself still applies.

One precision on the failure path, which does not change the outcome: at the create-world page
the operative filter is `Patch_Page_CreateWorldParams.ApplyChanges`, not the postfix —
`ResetFactionCounts_Prefix` forces `Current = Archotech` first, then the postfix re-trims via
`ApplyChanges` [V]. The postfix is what bites `ConfigurableFactions`' other callers. Both honour
the exemption.

**A second instance of the same mechanism — louder in consequence, but recoverable.**
`Patch_MapGenerator.GenerateContentsIntoMap_Prefix` filters `GenStepDef` through the *same*
`MinRequiredTechLevel` array and **rewrites the ref parameter** [V]. Any Archinity map genstep
resolving above the world level silently never runs, with no log line. Two qualifications
that ORBIT previously stated too harshly, both from **T-54**:

- **It is gated, like every `Filter_*` patch in that assembly, on a mod setting** — this one
  on `WorldTechLevel.Settings.Filter_GenSteps`, through the `[PatchGroup("Filters")]` /
  `[HarmonyPrepare]` pair [V]. That makes it a **T-18** surface as well: two clients with
  different settings generate different maps.
- **It is not terminal.** `GenStepDef` gets no `ApplyExclusions` pass, so the settings
  exclusion list cannot reach it and a `TechLevelConfigDef` override is the only lever — but
  `ApplyOverrides` *does* cover `GenStepDef`, and the filter is re-evaluated **per map**
  rather than baked into the world. A stronghold that generated as a void is repaired by
  shipping the override; only maps already generated keep what they were generated with.
  **The faction leg is the permanent one; this one is a bug you can fix after the fact.**

**[#18](https://github.com/cjd721/Rimworld-Archinity/issues/18) needs a checklist line that
does not exist yet:** *is World Tech Level active at world creation, at what level, and does a
`TechLevelConfigDef` exempt every orbital `FactionDef` and every Archinity `GenStepDef`?* This
spec does not edit #18.

**A shipped post-worldgen faction-addition path exists, and it qualifies the escape hatch below.**
`Window_AddFactions.OpenIfAnyAvailable(previousLevel)` offers the player any faction whose
minimum level falls in `(previous, new]` and that is not already in `FactionManager`, and WTL
drives it from a `WITab_Planet` button that sets `WorldTechLevel.Current` [V]. `Current` is a
public static with a scribed home in `GameComponent_TechLevel`, so *"the Spacers become
available when the world reaches the Spacer era"* is roughly five lines of our own code. It does
not rescue this spec's design — a faction added that way still arrives with a fresh `loadID` and
no shared history, which is why the reveal-at-worldgen architecture stands — but it is a **live
T-07 exception** and the only shipped precedent for adding a faction after world creation.
Recorded against [#107](https://github.com/cjd721/Rimworld-Archinity/issues/107), which owns
T-07's body.

### Vanilla content can open the reveal gate before the politics do

`OrbitLayer.CanSelectLayer` triggers on **any** world object on the layer, and Odyssey ships
six that a player can cause. `Odyssey/Defs/QuestScriptDefs/Script_SpaceSites.xml` defines
`OpportunitySite_Asteroid`, `OpportunitySite_OrbitalItemStash`,
`OpportunitySite_AbandonedPlatform`, `OpportunitySite_OrbitalWreck`,
`OpportunitySite_MechanoidPlatform` and `OpportunitySite_Satellite`; each roots on
`QuestNode_Root_Asteroid` with `<layerDef>Orbit</layerDef>` and places a `SpaceMapParent`
there [V]. **The first one to fire enables the view-orbit gizmo whatever the political state**
— and the entire *Display* leg of this spec rests on that layer being empty.

The gate is bounded, not open. All six are `randomlySelectable false` with
`<givenBy><li>OrbitalScanner</li></givenBy>` [V], so the storyteller never picks them; they
arrive only from a built, powered, un-roofed `OrbitalScanner` (`CompOrbitalScanner`,
`PlaceWorker_NotUnderRoof`), which costs 180 steel, 6 industrial and **2 spacer components**
and requires the `OrbitalTech` research project [V].

Two things follow.

1. **The real gate is when `OrbitalTech` and `ComponentSpacer` become reachable**, which is
   progression, not this spec: [#20](https://github.com/cjd721/Rimworld-Archinity/issues/20)
   fills the Spacer ladder rows in `docs/progression/`. If that ladder puts `OrbitalTech`
   before the planetary resolution, a player who builds a scanner unlocks orbit early. **No
   ticket currently states that the orbital scanner is a reveal-gate item** — that is the
   gap, and #20 is where it should land.
2. **The mitigation is not frozen at worldgen**, unlike everything else in this spec. Clearing
   `givenBy` on the six, or locking `OrbitalScanner` out of the build menu in the lockout
   pattern the project already uses, is an ordinary def patch that can land after the world
   exists. The severity is a design one, not a T-07 one.

Note what the early reveal produces: unowned quest sites on the layer, not stations. Orbit
becomes *selectable* early; it does not become *populated* early. That is a weaker failure
than the roster one, and it is loud rather than silent.

### A stronghold that generates as a void, or as a structure in vacuum

Three silent failures, all on the map-generation half.

1. **T-54's second leg deletes our gensteps.** `WorldTechLevel`'s
   `Patch_MapGenerator.GenerateContentsIntoMap_Prefix` filters `GenStepDef` through the
   `MinRequiredTechLevel` array and rewrites the ref parameter, and unlike `FactionDef`,
   `GenStepDef` gets **no `ApplyExclusions` pass** [V]. An Archinity orbital `GenStepDef`
   resolving above the world tech level therefore **never runs, with no log line**, and the
   player enters a bare `GenStep_Space` void — 200×200 of impassable, vacuum-exposing
   nothing. `TechLevelConfigDef` is the only lever; the patch is gated on
   `WorldTechLevel.Settings.Filter_GenSteps`, so it is a **T-18** surface too. **Unlike the
   roster failure this one is recoverable** — the filter runs per map, not at worldgen, so
   shipping the override repairs every stronghold not yet generated (**T-54**). Every
   `GenStepDef` in the cost table must appear in the same file as the faction exemption, and
   the [#18](https://github.com/cjd721/Rimworld-Archinity/issues/18) line covering it still
   does not exist.
2. **A missing `<temperature>` generates the interior at −75 °C.** `SpawnTemp` is
   `temperature ?? -75f` [V]. Nothing warns.
3. **A KCSG layout placed on an orbit map produces a structure that can never
   pressurise.** This is the failure the route above exists to avoid, and it is worth
   keeping written down because the cause is not the one it looks like: a `.` in a
   `KCSG.StructureLayoutDef` `terrainGrid` means *leave the terrain alone*, so those cells
   stay `TerrainDefOf.Space`, which sets `exposesToVacuum` — and one such cell inside a
   sealed, roofed room pins `Room.Vacuum` to 1 permanently and neuters the life-support
   unit [V]. Walls and roofs do not help. `KCSG.GenStep_CustomStructureGen` has **no
   default-terrain or terrain-fill field of any kind** [V], so there is no XML escape
   inside KCSG.

### The campaign softlock this spec exists to prevent

A roster mistake in orbit. An orbital faction omitted at world creation cannot be added
afterwards, does not error, and does not log (**T-07**). Discovery would be at the reveal,
tens of hours in, with no repair short of `CreateFactionAndAddToManager` — which would
produce a faction with a fresh `loadID` and no shared history, in a save that is otherwise
finished, and on the layer-taking overload nobody has shipped. Treat the orbital roster as a
worldgen deliverable, not a Spacer one.

### The second irreversible

`PlanetLayer.ExposeData` scribes `subdivisions`, `radius`, `viewAngle` and `viewCenter`, and
`InitializeLayer()` rebuilds the icosphere from the *scribed* values, not the def [V].
`Orbit_LayerSize.xml` is worldgen-only; editing it later is a silent no-op —
`docs/TRAPS.md` **T-45**.

### Partial reveal

The command is idempotent per faction if it checks `hidden` before writing and counts
existing settlements before placing. It should — an interrupted or double-fired reveal
otherwise doubles the board.

### Orbit revealed empty

If the reveal fires with an empty faction list, `CanSelectLayer` stays false and the gizmo
stays greyed. That is a visible failure rather than a silent one, and it is the correct
behaviour. It is also what a WTL-filtered roster looks like from the player's seat, which is
why the WTL check belongs before world creation rather than at the reveal.

### A hidden faction raids before the reveal

Not a failure of this design — `IncidentWorker_RaidEnemy` ignores `Hidden` by intent — but
it is the one way an orbital power can reach the player before orbit does. Raid gating is
the def's and Ignorance Is Bliss's job, not this spec's.

## Status

**Verified available mechanism. Not yet selected, not yet built.**

Evidence class **READ**, against decompiled RimWorld 1.6.4871, `Multiplayer.dll`,
`RimPacts.dll`, `WorldTechLevel.dll` and `KCSG.dll`, Odyssey's shipped defs, plus two-root
corpus sweeps of all 155 mods.
Re-verified adversarially on 2026-09-12; every load-bearing engine claim below reproduced,
and five claims were corrected in place (the WTL postfix, the `CreateFactionAndAddToManager`
overload, the `Find.WorldGrid.Orbit` condition, the `State` leg's owner, and two STUB-grade
numbers reported as [V]).

A second adversarial pass the same day corrected the map half: the `roofs:` argument is dead
code and roofing comes from `LayoutRoomDef.roofDef` (which demotes the fog claim to a RUN
item), `Settlement.MapGeneratorDef` has three branches rather than two, the WTL `GenStepDef`
leg is settings-gated and recoverable rather than terminal, the BTG counts were 17/3 and are
19/2, and the § 6 cost arithmetic read ~80–95 for 76–96.

- **Verified:** T-07 applies per layer and therefore to orbit; `Faction.hidden` is a
  scribed instance override; hidden factions get neither the freebie nor a lottery slot;
  `OrbitLayer.CanSelectLayer` is vanilla's reveal gate; `layerWhitelist` is read at one
  worldgen-only site; `WorldObject` has no hide flag, and no mod supplies one; layer geometry
  is scribed (**T-45**); `CreateFactionAndAddToManager` is a real runtime route, with a
  shipped precedent **only for the surface-layer overload**; MP syncs `PlanetLayer` and
  patches `FactionManager.Add`; World Tech Level's `ConfigurableFactions` postfix reaches
  worldgen; `GenStep_OrbitalPlatform` builds a floored, heated, pressurised,
  life-supported interior from an XML-only `StructureLayoutDef`, **roofed per room from
  `LayoutRoomDef.roofDef` rather than from the dead `roofs:` argument**, and its whole
  pipeline is
  `Verse.Rand`; `Room.ExposedToSpace` and `VacuumUtility.IsRoomAirtight` are different
  rules with different callers; `Breached` is a shipped per-layout `RoomPartDef`; three
  corpus mods already use Odyssey's layout system, one of them for custom-faction orbital
  settlements.
- **Proposed [I]:** that these compose into the reveal described above. Nothing is built.
- **Open, and owned elsewhere:** the machine-readable political outcome that fires the reveal
  ([#100](https://github.com/cjd721/Rimworld-Archinity/issues/100), with the beat at
  [#46](https://github.com/cjd721/Rimworld-Archinity/issues/46)); which orbital powers exist and
  how many settlements each gets
  ([#34](https://github.com/cjd721/Rimworld-Archinity/issues/34)); when `OrbitalTech` becomes
  reachable ([#20](https://github.com/cjd721/Rimworld-Archinity/issues/20)); **which room
  kinds a Glitterite stronghold must present**, which `docs/requirements/GLITTERTECH.md`
  states only in prose and no ticket currently owns
  ([#46](https://github.com/cjd721/Rimworld-Archinity/issues/46),
  [#47](https://github.com/cjd721/Rimworld-Archinity/issues/47)).

The map-generation half is established on
[#66](https://github.com/cjd721/Rimworld-Archinity/issues/66), which **corrected the framing
that ticket was written around**: the choice is not *"author `terrainGrid`, or write a
flooring `GenStep`"* but *"do not put KCSG on the orbit layer"*. `GenStep_OrbitalPlatform`
is a **verified available mechanism**, not yet selected and not yet built.

**T-07's provenance is stale.** It is marked against 1.6.4566 while every read here is
1.6.4871, and its body still calls `CreateFactionAndAddToManager` "a repair, not a plan".
Both are being corrected under
[#107](https://github.com/cjd721/Rimworld-Archinity/issues/107); the trap's substance holds.

**Two shipped patches were found to have decided this by accident**, and both need action
before world creation — see *Verification*.

## Available mechanisms

**Vanilla/Odyssey supplies the entire reveal gate and we are currently defeating it.**

| Mechanism | What it gives | Limitation |
|---|---|---|
| `Faction.hidden` (`bool?`, scribed) | per-instance hide that overrides the def and survives save/load [V] | does not gate hostile raids [V] |
| `FactionGenerator` hidden gates | a hidden faction costs no map presence on any layer [V] | decided at worldgen for placement purposes |
| `OrbitLayer.CanSelectLayer` | the greyed "No discovered orbital locations." button [V] | triggers on *any* world object on the layer, including Odyssey's six scanner-given orbital quest sites — see *Failure and recovery* |
| `PlanetLayerDef.SettlementWorldObjectDef` | `SpaceSettlement`, with jammer gate and platform map generator [V] | one base type per layer; Better Traders Guild's `PatchOperationSequence` is the worked example of specialising it |
| `WorldObject.SetFaction` | bare field write, `Settlement` does not override [V] | notifies nothing; not MP-synced |
| `FactionGenerator.CreateFactionAndAddToManager(FactionDef)` | full runtime faction creation; the overload RimPacts actually ships [V] | hardcodes `Find.WorldGrid.Surface` — no use to orbit |
| `FactionGenerator.CreateFactionAndAddToManager(layer, def)` | full runtime faction creation on a named layer [V] | `Rand`-heavy; places a freebie settlement the caller must destroy; **zero shipped precedent in the corpus** [V] |
| `GenStep_OrbitalPlatform` | floor, procedural rooms, roofs (per room, from `LayoutRoomDef.roofDef`), 20 °C, life support, docks, cannons, exterior prefabs, debris — every field XML [V] | `temperature` defaults to −75 °C; needs a `StructureLayoutDef`; its `roofs:` argument is dead code, so an unroofed `roomDefs` entry silently fails to pressurise [V] |
| `StructureLayoutDef` + `LayoutRoomDef` | a *generator*, not a floor plan — size, rotation, room set, corridor shape and dock arrangement all re-roll per map [V] | vanilla rooms are Ancient-flavoured; bespoke rooms are content |
| `RoomPartDef Breached` / `Gore` | per-room, weighted hull breach and gore, applied through `LayoutDef.parts` [V] | refuses the `importantRoomDef` and wall-protected rooms [V] |
| `Building_LifeSupportUnit` | pumps a sealed room to zero vacuum and 20 °C, and **generates** 3200 W [V] | no-ops on any room that is `ExposedToSpace` [V] |
| `AncientFortifiedWall` / `OrbitalAncientFortifiedWall` | `isAirtight` on the def, so **T-47** does not bite the generated hull [V] | `neverBuildable`, `deconstructible: false` — the player cannot extend or repair with it [V] |
| `AncientBlastDoor` | `Building_HackableDoor` exterior door, shipped on the orbital base layout [V] | the design lever is `ensureOneDoorUnlocked`; the mechanism is [#58](https://github.com/cjd721/Rimworld-Archinity/issues/58)'s |

**The corpus precedent.** A two-root sweep of all 155 mods found **three** mods using
Odyssey's layout system: **Better Traders Guild** (`shunter.bettertradersguild`) ships
`BTG_SettlementPlatform`, `BTG_SmugglersDenPlatform` and `BTG_OrbitalCargoVault` — custom
`StructureLayoutDef`s, **19** custom `LayoutRoomDef`s, three `MapGeneratorDef`s and three
platform `GenStepDef`s, **two** of which use the bare vanilla `GenStep_OrbitalPlatform` as
their `genStep Class` (the cargo-vault one declares a class of its own) [V];
**Vanilla Gravship Expanded – Chapter 1** and **Worksites Expanded** ship layout content
too [V]. BTG is the worked example for route A, including the one thing we avoid: it needs
a Harmony patch on `MapParent.MapGeneratorDef` because it cannot choose the settlement's
`WorldObjectDef`, and `RevealOrbit` can.

**What does not exist.**

- **No terrain fill in KCSG.** `KCSG.GenStep_CustomStructureGen`'s fields are `fullClear`,
  `clearFogInRect`, `preventBridgeable`, `spawnInRandomFreeLocation`, `structureLayoutDefs`,
  `settlementLayoutDefs`, `tiledStructures`, `symbolResolvers`, `scatterThings`,
  `filthTypes`, `scatterChance`, `scaleWithQuest` — and nothing that sets a default terrain
  [V]. The two fixes [#66](https://github.com/cjd721/Rimworld-Archinity/issues/66) was framed
  around — author `terrainGrid` on every layout, or write a flooring `GenStep` — both buy a
  floor and neither buys roofing, temperature, life support, docking or fogging. **Replacing
  the generator is cheaper than repairing its input.**

- **No `WorldObject` hide.** Checked `WorldObject`, `WorldObjectDef` and `Settlement`; the
  only visibility concept is `VisibleInBackground`, a render flag for space layers [V].
  **And no mod supplies one** — see the completing sweep under *Verification* [V].
- **No runtime layer generation that works.** `WorldGrid.RegisterPlanetLayer` and
  `PlanetLayer.RunWorldGeneration()` are both public, and — unlike factions —
  `WorldGrid.ExposeData` calls `CreateRequiredLayers()` at `PostLoadInit` unconditionally,
  so a layer added to the scenario after the fact *is* reconciled on load [V]. It still
  fails: `WorldGenStep_Factions.GenerateFresh` reads `Current.CreatingWorld.info.factions`,
  and `Current.CreatingWorld` is null outside worldgen, so running the orbit layer's gen
  steps mid-game NREs inside `GeneratePlanetLayer`'s `try/catch` and surfaces as a red
  `Log.Error("Error in WorldGenStep: …")` with a content-free layer [V]. Loud, so not a
  trap — but fatal to the route.
- **No donor.** A two-root sweep of all 155 mods (`-a -g '*.dll' -g '!**/obj/**'`) returned
  **zero** hits for `RegisterPlanetLayer`, `RunWorldGeneration`, `GeneratePlanetLayer`,
  `CreateRequiredLayers`, `GenerateFactionsIntoWorldLayer` and `RemovePlanetLayer`. Nobody
  has tried it. (On the sweep's own validation, see the #103 caveat under *Verification*.)
- **`CreateFactionAndAddToManager` has three hits**, depth-read: RimPacts uses it in
  production, on the single-argument surface-layer overload [V]; World Tech Level's
  `Patch_FactionGenerator` transpiles `InitializeFactions` but only at the
  `DefDatabase<FactionDef>.AllDefs` call site, which lives in the `factions == null`
  dev-quickstart branch (**T-09**) and never runs during real worldgen [V]. Neither is a
  donor for deferred instantiation. **The same WTL class's other patch — the
  `ConfigurableFactions` postfix — is not a donor either but is a live hazard**; it is under
  *Failure and recovery*, not here.

**The nearest shipped mechanism, with one piece replaced.** Odyssey's own `Salvagers` is a
`hidden: true`, `layerWhitelist: [Orbit]`, `displayInFactionSelection: false` faction that
generates at worldgen, holds no settlements and still raids [V]. That is this design
already running in vanilla — the piece we replace is that ours get unhidden and populated
on a trigger instead of staying hidden forever.

## Verification

**Two shipped patches were found to have decided this by accident.**

**`Archinity.Pacing/Patches/Orbit_AlwaysViewable.xml` — inert, and a latent blocker.** Its
comment asserts the view-orbit gizmo *"only appears once you have a presence up there."*
It does not; the scenario connection makes it visible from the first tick regardless [V].
Setting `viewGizmoOnlyVisibleWithDirectConnection` to `false` shows the gizmo
*unconditionally*, which is the one thing that would defeat the alternative hide (dropping
the scenario's Surface↔Orbit connection). **Delete it.**

**`Archinity.Pacing/Patches/Orbit_LayerSize.xml` — real, applied, and the one that matters.**
`tools/xpath.py` reports: baseline `subdivisions = 5`, one node matched; with our patches,
`6`. **That is a STUB-grade result and must be read as one** — `tools/xpath.py` merges the
**active** mod set, so it is a match **in one configuration**, not a corpus-wide fact [I].

⚠️ **Provisional in a second way.** `tools/defdb.py` `_apply_leaf` evaluates patch xpaths
relative to `<Defs>`, so an ordinary `Defs/ThingDef[...]` patch matches nothing while
`report.patch_ops_applied` still increments and the tool reports success —
[#102](https://github.com/cjd721/Rimworld-Archinity/issues/102). Every STUB number produced
through `xpath.py` on this ticket measured a partly unpatched tree. **Re-run this check when
#102 lands.**

Its arithmetic is wrong. `PlanetLayer.Subdivide` adds one vertex per triangle and emits one
triangle per (vertex, adjacent-triangle) pair; since `Σ deg(v) = 3·|tris|`, triangles
**triple** per pass and tiles ≈ `12 + 10·(3^s − 1)` — 2,432 at s=5, 7,292 at s=6, a ratio of
3.00, not 4 [V]. `docs/engine/world-time-and-layers.md` repeats the same "~4^subdivisions"
error.

The consequence:

```
num2 = RoundRandom(TilesCount/100000 * settlementsPer100kTiles.RandomInRange
                   * populationScaleFactor
                   * viewAngleSettlementsFactorCurve.Evaluate(ViewAngle/180))
```

Orbit sets `useSurfaceViewAngle: true` and `surfaceViewAngle = PlanetCoverage * 180f` [V].
At 50% coverage the visible cap is half the sphere and the curve evaluates to 0.75, with
`settlementsPer100kTiles = 1000~1000`:

| | orbit tiles | orbital settlements |
|---|---|---|
| vanilla, s=5 | ~1,216 | **~9** |
| ours, s=6 | ~3,646 | **~27** |

[V] on the formula and tile counts; [I] on the settlement figures, which move with the
coverage and population the world is created at. **The patch roughly triples the number of
permanently frozen orbital settlements** — and with **three non-hidden orbit factions in the
bin today (a count over the active set, so true in one configuration only, and provisional
pending #102)** [I], all of them are generated, owned and visible on day one of the
neolithic game, Glitterite stations included.

Re-decide 6 against the reveal design rather than against scenery, and correct the comment.

**The completing sweep.** #70's negative had two halves and swept only one. It proved that
*the engine* has no world-object hide flag; it never asked whether *a mod* supplies its own
world-object visibility or discovery mechanism over the orbit gate. That sweep has since been
run: **`AnyWorldObjectOnLayer` → 0 files across both roots** [V]. Nothing in the corpus reads
or patches the gate. The gate is vanilla's, and after this spec, ours.

⚠️ **On the method behind every negative above.** The UTF-16LE half of these sweeps used
`rg -a --encoding utf-16le`, which is now known to miss strings provably present in the `#US`
heap, and to do so non-uniformly —
[#103](https://github.com/cjd721/Rimworld-Archinity/issues/103). The conclusions survived
re-derivation with a null-interleaved ASCII pattern; **the stated validation did not**, so the
"validated against `TryAffectGoodwillWith` → 65, `PlanetLayer` → 36" line is evidence of a
sweep having run, not of its completeness.

### Observable checks

1. **The one RUN item — empty orbit at worldgen, under the real load order.** Generate a
   world with every orbit-whitelisted faction hidden and confirm three things in the same
   run:
   - `Find.WorldObjects.AllWorldObjectsOnLayer(Find.WorldGrid.Orbit)` is empty, and the
     view-orbit gizmo is present, greyed, and reads *"No discovered orbital locations."*
     The mechanism is read end to end; what a run confirms is that no other gen step or mod
     places a world object on Orbit, which no grep can prove. Orbit's `worldGenSteps` are
     only `Tiles` and `Factions` [V], so the expected answer is yes.
   - **With World Tech Level active and the world tech level set to Neolithic**, whether
     `Current.CreatingWorld.info.factions` still contains all four orbital factions, and
     whether adding them to `Settings.FactionsExcluded` restores them if it does not. This is
     the WTL hazard above, and it is the check that decides a #18 line. Compare against the
     same world generated with WTL absent.
   - **Whether an orbital scanner opens the gate.** Dev-mode a built `OrbitalScanner`, force
     one of the six `OpportunitySite_*` quests, and confirm the site lands on Orbit and the
     gizmo enables with no reveal having fired. Expected: yes, it does.
2. **The gizmo lights on the first placement**, with no reload.
3. **Unhiding persists.** Set `hidden = false`, save, load, confirm the faction is still in
   the Factions tab and its settlement inspect string shows a goodwill number.
4. **Two clients agree.** Run the reveal under Multiplayer and confirm identical settlement
   tiles and names — the two `Rand` calls are the whole determinism surface.
5. **The second RUN item — generate one stronghold and walk it.** Everything in § *The
   build → 6* is read end to end; what a run confirms is composition, which no grep proves.
   In one generated map:
   - **Interior pressure.** Stand a colonist in a generated room and read the vacuum
     overlay: expect **0**, not 1, and no `VacuumExposure` accruing. Catches a `roomDefs`
     entry with `noRoof`, or a `LayoutRoomDef` whose `floorTypes` leaves `Space` showing.
   - **Interior temperature is 20 °C**, not −75 °C. This is the one that fails silently if
     `<temperature>` is omitted from the `GenStepDef`.
   - **Whether the interior is fogged on arrival**, with the exterior deck unfogged. **This
     is the check, not a settled claim — read it as unproven [I].** The reading half is
     solid: `GenStep_FogSpace` flood-unfogs from the four map corners through a validator
     that rejects any cell with an edifice **or a roof** [V], so a roofed hull stops the
     fill. What is *not* solid is the premise — an earlier draft rested it on
     `LayoutWorker.Spawn(…, roofs: true, …)`, which is dead code (see § *The build → 6*);
     roofing actually arrives per room from `LayoutRoomDef.roofDef`, so the fog outcome is
     only as good as the room defs in the layout. A layout carrying an unroofed room will
     leak the fill into the interior, silently. *(The recon's separate claim that `FogSpace`
     "reveals essentially everything" is true of an all-vacuum map with no roofs — the
     failure case — and not of a correctly roofed platform.)*
   - **With World Tech Level active at a Neolithic world level**, confirm the map is a
     platform and not a void. If it is a void, the `TechLevelConfigDef` exemption is
     missing (**T-54**). There is no log line either way; the map is the readout.

   **Multiplayer needs no separate run for the map half.** Determinism rests on vanilla's
   per-genstep `Rand` seeding, which this route inherits with no `System.Random` anywhere
   on it. If a two-client check is run anyway, compare the room graph — room count,
   corridor shape, dock arrangement — because those are the only `Rand` consumers.

## Outstanding decisions

| Question | Consequence | Owner |
|---|---|---|
| Which orbital powers exist, and their weights | **Frozen at worldgen.** SPACER.md's "at least two additional Spacer powers" are unauthored and cannot be added later | [#34](https://github.com/cjd721/Rimworld-Archinity/issues/34) |
| How many settlements each revealed faction gets | The reveal's only real parameter; a balance number, not a mechanism | [#34](https://github.com/cjd721/Rimworld-Archinity/issues/34) |
| **Is World Tech Level active at world creation, at what level, and is every orbital faction exempt?** | **The orbital roster exists or does not.** Silent, permanent, and taken before the first tick | [#18](https://github.com/cjd721/Rimworld-Archinity/issues/18) — the line does not exist yet |
| Which live-state predicates select each route and ascending faction, and how ties compose | The immutable snapshot can hold multiple factions; this decides its contents | [#100](https://github.com/cjd721/Rimworld-Archinity/issues/100) |
| What fires the reveal, as a beat | The narrative moment the command hangs off | [#46](https://github.com/cjd721/Rimworld-Archinity/issues/46) |
| When `OrbitalTech` / `ComponentSpacer` become reachable, and whether the six orbital opportunity quests stay in the pool | Whether a player can select the Orbit layer before the politics resolve | [#20](https://github.com/cjd721/Rimworld-Archinity/issues/20); **no ticket names the scanner as a reveal-gate item today** |
| Whether the surviving institution also swaps `Faction.def` | If yes, pay #8's leak list | [#34](https://github.com/cjd721/Rimworld-Archinity/issues/34) |
| Orbit `subdivisions` — 6, or back to 5 | ~27 frozen orbital settlements versus ~9 | [#18](https://github.com/cjd721/Rimworld-Archinity/issues/18) |
| **How many stronghold *flavours* the campaign distinguishes** | ~40–60 lines of XML each; the mechanism does not wait on the number, and each flavour re-rolls per encounter | [#46](https://github.com/cjd721/Rimworld-Archinity/issues/46), [#47](https://github.com/cjd721/Rimworld-Archinity/issues/47) |
| **Which room kinds a Glitterite stronghold must present** — the exemplar vault, the archive, the command core | The bespoke `LayoutRoomDef`s cannot be authored without it. `docs/requirements/GLITTERTECH.md` states the contents in prose and **never as a map requirement**; no ticket owns that gap today | [#46](https://github.com/cjd721/Rimworld-Archinity/issues/46), [#47](https://github.com/cjd721/Rimworld-Archinity/issues/47) — **gap** |
| Whether the outer blast doors must be hacked to enter, per flavour | `ensureOneDoorUnlocked` on the layout def; free either way | [#58](https://github.com/cjd721/Rimworld-Archinity/issues/58) |
| Breach chance per flavour, and whether any stronghold is deliberately derelict | One weight in `LayoutDef.parts`; costs nothing | [#46](https://github.com/cjd721/Rimworld-Archinity/issues/46), [#47](https://github.com/cjd721/Rimworld-Archinity/issues/47) |
| Whether Glittertech Expansion's art is reused inside our `LayoutRoomDef`s | Content reuse without KCSG — GTE `ThingDef`s referenced from vanilla room defs. Its surface quests are unaffected either way | [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) |
