# Traps: worldgen layouts

KCSG structure and settlement authoring, the shipped siege that never fires, the
road model whose tier dial is wired to nothing, and what a planet layer quietly
removes from the game. KCSG mechanisms in `docs/engine/mods/kcsg.md`.

Part of the trap register. **The index at `docs/TRAPS.md` is the file you read
before a diff**; this one carries the full entries for this group. Every entry here
fails with no error message. Cite by ID.

## Worldgen layouts

### T-29 — Layout rows and cells beyond `layouts[0]` are dropped silently

A `StructureLayoutDef`'s size derives from `layouts[0]`; rows and cells beyond that
are dropped with no message, so part of a hand-authored structure does not spawn.
Size every layer to the first layer, and re-export rather than hand-editing a grid's
width.

*`docs/engine/mods/kcsg.md`. 1.6.4871.*

### T-30 — `defenseOptions` is dead below Industrial

`SymbolResolver_EdgeDefenseCustomizable` gates `addTurrets` and `addMortars` on
`faction.def.techLevel >= Industrial` (4); Medieval is 3. Only `addSandbags` and
`pawnGroupMultiplier` take effect below Industrial — siege engines have to live
inside the layout grid instead.

*1.6.4871.*

### T-31 — `DankPyon_MedievalSiege` cannot fire as shipped

Its worker requires `RaidStrategyWorker_Siege.CanUseWith` (i.e.
`FactionDef.canSiege`) **and** a `MedievalOverhaul.FactionSiegeExtension` with
`medievalSiege: true` **and** `techLevel == Medieval`. The extension is on
`DankPyon_BrigandFactionBase` and `DankPyon_NobleHouseFactionBase`; **neither sets
`canSiege`**, which has **zero hits across all of Medieval Overhaul** (1.4/1.5/1.6,
defs, patches and assembly). Core `FactionBase` does not set it and the field
defaults `false`. Empty intersection — a shipped raid strategy that never occurs and
never explains itself. No VFEM2 faction sets `canSiege` either.

Fixing it is not a one-liner: `canSiege` must go onto **both** abstract defs, and
`RaidStrategyWorker.CanUseWith` adds further gates — the def's curve is
`(500,0) → (1000,1.6)`, so it needs **>500 threat points**, plus the Surface layer
and no blocking tile mutator. That makes it *possible*, not frequent.

What it would buy: the def already ships `LordJob_MedievalSiege` with its own supply
generation and **trebuchets** — `DankPyon_Turret_Trebuchet` is the only holder of
`ArtilleryMedieval_BaseDestroyer`. *(MO's own arrival text says "catapults"; that is
flavour copy, not the def.)*

*`docs/engine/mods/medieval-overhaul.md`. MO 1.6.*

### T-32 — Rotated KCSG symbol variants are not defs and cannot be patched

`_North` / `_East` / `_South` / `_West` variants are generated at runtime by
`HotGenerateRotationSymbols` and never enter the def database, so a patch targeting
one matches nothing. Patch the base symbol. Related:
`StartupActions.CreateSymbols` auto-generates symbols **only** for Core, DLC, VFE
Props and Decor — every other modded ThingDef needs a hand-written SymbolDef.

*Same shape as the `USH_GlittershipChunk_North` finding. 1.6.4871.*

### T-42 — Road tier changes travel time by nothing

All five vanilla `RoadDef`s ship `movementCostMultiplier 0.5` — `DirtPath` (priority
10), `DirtRoad` (20), `StoneRoad` (30), `AncientAsphaltRoad` (40, `ancientOnly`) and
`AncientAsphaltHighway` (50, `ancientOnly`), every one of them at 0.5
(`Core/Defs/RoadDefs/RoadDefs.xml`). A dirt path is exactly as fast as an ancient
asphalt highway. **Upgrading a road is a silent no-op**: nothing says so, and the tile
tooltip prints the same 50% before and after.

Tier is not inert — it changes the world-map texture, the terrain laid on a generated
map, `tilesPerSegment`, `pathingMode` and `worldTransitionGroup`. It changes travel
time by nothing. Any design that treats road quality as a capability is reading a
constant until it patches the ladder itself. **No mod in the corpus ships or patches a
`RoadDef`**, so the ladder is ours to set and nothing will fight us for it.

Differentiating it is safe because the field's readers are enumerable and few. In
`Assembly-CSharp` there are **exactly two**, both on `WorldGrid`:
`GetRoadMovementDifficultyMultiplier` and
`FindMostReasonableAdjacentTileForDisplayedPathCost`. There are **two more** out of
assembly, and they are the two `RoadDef` overloads of
`Vehicles.RoadCostHelper.GetRoadMovementDifficultyMultiplier` — `(List<VehicleDef>, …)`
and `(List<VehiclePawn>, …)`, identical bodies, the second being what a live caravan
reaches, so a patch aimed at one of them misses the other. Each takes the def's value as
a base and lets `VehicleDef.properties.customRoadCosts` **replace** it outright: the
first declaring vehicle wins whatever its direction, so the vehicle table is **not a
floor** and the two ladders do **not** multiply. Under Vehicle Framework a patched road
tier is read there and then discarded for any caravan carrying a declaring vehicle —
**T-87**, whose remedy is `docs/specs/WORLD-INFRASTRUCTURE.md` § 4c.

*[#68](https://github.com/cjd721/Rimworld-Archinity/issues/68),
`docs/specs/WORLD-INFRASTRUCTURE.md`. 1.6.4871. The Vehicle Framework paragraph was
corrected against `294100/3014915404/1.6/Assemblies/Vehicles.dll` when T-87 was
registered: it had described `customRoadCosts` as undercutting the base and named one
overload where there are two.*

### T-43 — `OverlayRoad` refuses to downgrade a road, and the refusal is silent

`WorldGrid.OverlayRoad(from, to, roadDef)` is the only road-writing API in the
assembly, and it is upgrade-only. It logs in exactly one case: handed a **null**
`RoadDef` it calls `Log.ErrorOnce("Attempted to remove road with overlayRoad; not
supported")` — loud, and easy to mistake for the whole story. Handed a real def whose
`priority` is **less than or equal to** the existing road's, it takes a bare `return`
— no log, no message, and no return value to check. So "the war destroyed the highway"
written through `OverlayRoad` does nothing at all, quietly.

There is no vanilla road-removal path to fall back on either: `RemoveRoad`,
`DowngradeRoad` and `DestroyRoad` return **zero hits corpus-wide**, `Assembly-CSharp`
included. Degradation or removal has to mutate `SurfaceTile.potentialRoads` directly on
**both** endpoint tiles — the link is stored symmetrically — and `OverlayRoad` cannot
express it.

The guard is the right behaviour for an era-advance pass, which can then be re-run or
run out of order without clobbering anything; it is a defect for every other purpose.

*[#68](https://github.com/cjd721/Rimworld-Archinity/issues/68). 1.6.4871.*

### T-44 — A road in a no-roads biome is drawn but inert

`SurfaceTile.Roads` returns `null` when `!PrimaryBiome.allowRoads`, and that getter is
what every gameplay reader goes through — `WorldGrid.GetRoadDef(visibleOnly: true)`,
`GetRoadMovementDifficultyMultiplier`, `FindMostReasonableAdjacentTileForDisplayedPathCost`,
`CaravanExitMapUtility.RandomBestExitTileFrom` and the terrain inspect surfaces. But
`WorldDrawLayer_Roads.Regenerate` reads `surfaceTile.potentialRoads` **directly**,
bypassing the gate.

So a road written into such a tile is **painted on the world map and does nothing**: no
movement bonus, no inspect line, no message. The player sees a road and is simply
wrong about it. RimPacts ships a postfix on exactly that getter
(`RimPacts.Patch_SurfaceTile_Roads`) to work around it — independent corroboration that
the behaviour bites in practice.

*[#68](https://github.com/cjd721/Rimworld-Archinity/issues/68). 1.6.4871.*

### T-48 — On an orbit layer the content pool collapses without a word

`PlanetLayerDef` `Orbit` inherits `onlyAllowWhitelistedIncidents`,
`onlyAllowWhitelistedGameConditions`, `onlyAllowWhitelistedArrivals` and
`onlyAllowWhitelistedArrivalModes` from the abstract `OrbitLayer`, along with
`canFormCaravans false` and `isSpace true`. `IncidentWorker.CanFireNow` then returns
false for any def that is neither `canOccurOnAllPlanetLayers` nor carries the layer in
its `layerWhitelist`.

**Those are four gates, not one, and each has a different reader and a different XML
key** [V]. Whitelisting an `IncidentDef` alone leaves the game condition, the arriving
faction and the arrival mode shut, and the incident then fails **with no message**.
Nothing about the def you patched reports that three other doors are still closed.
(*[#147](https://github.com/cjd721/Rimworld-Archinity/issues/147), 2026-09-23.*)

**Correction, same source: the quest half has a different cause.** `Orbit` never sets
`onlyAllowWhitelistedQuests` — there is no such field on the layer — and the quest feed
is emptied by `QuestGen_Get.GetMap(canBeSpace: false)`, a C# default no `<li>Orbit</li>`
reaches [V]. **A whitelist-only patch pack restores the incidents and leaves the quest
feed as empty as it found it.** See **T-128** for the joiner family, where the same
default bars the path three times over.

Across the merged **Core plus four DLC** database — Royalty, Ideology, Biotech and
Odyssey; **Anomaly is not on this disk**, so the denominators are over the DLC actually
present — the layer-whitelisting clause stated above leaves **18 of 91 `IncidentDef`s**
(94 tags − 3 abstract = 91) and **18 of 139 `QuestScriptDef`s** orbit-legal. Both figures
are the **single clause**, reproduced independently by `grep -c`: eighteen defs set
`canOccurOnAllPlanetLayers true` and none whitelists Orbit.

**⚠ But 18 is a ceiling, and the storyteller never sees it.** The quest figure depends
entirely on which reader you ask, and the gap is a factor of nine [V]:

| Path | Orbit-legal quests | What it is |
|---|---|---|
| The layer-whitelist clause alone | **18 of 139** | the ceiling, reachable via `CanRun` paths — subquest generators, decrees |
| `QuestScriptDef.CanQuestOccurOnTile` end to end | **66 of 139** | whitelist + blacklist + the `autoAccept` exemption + `neverPossibleInSpace` |
| `IncidentWorker_GiveQuest.CanQuestOccurOnTile` | **2 of 139** | **the storyteller's actual path** — `OrbitalFugitive` and `SurveySite`, nothing else |

The storyteller's own reader is the bottom row: it **drops the `autoAccept` exemption**
and additionally demands `everAcceptableInSpace`, so **the effective orbital quest budget
is two**. A reader who takes 18 as the storyteller's budget is wrong by a factor of nine,
and nothing in the game reports either number. A campaign act played from an orbital home
therefore loses wanderers, refugees, visitors, manhunter packs, infestations, solar
flares, toxic fallout and every walk-in social event — not by a design decision but by
a def field nobody set. **The storyteller keeps running; it simply has almost nothing
to pick, and nothing anywhere reports the narrowing.** Patch `layerWhitelist` onto every
def the campaign needs in orbit, and re-count after every mod addition.

**The placing set nests inside the receiving gate, and that is authorship rather than
structure** [V]. `docs/specs/ORBIT.md` counts **ten** quest scripts that *place* a world
object on the Orbit layer; this entry counts which quests may be *given to* a colony whose
home tile is Orbit. They answer different questions, and a direct containment check settles
how they sit: **all ten are members of the 18, and inside the 66 as well.** The eight the
18 adds — `Gravcore_AncientReactor`, `_AncientStockpile`, `_CrashedMechanoidPlatform`,
`_FrozenTerraformer`, `_InsectLair`, `_MechanoidRelay`, `GravshipWreckage` and
`SurveySite` — are all **surface**-placing. So a placing set and a receiving gate are
distinct questions that happen to nest here because of how Odyssey authored its orbital
family; nothing makes the nesting necessary, and a quest we author can sit in either set
alone. (*Settled 2026-09-23 between
[#147](https://github.com/cjd721/Rimworld-Archinity/issues/147) and
[#148](https://github.com/cjd721/Rimworld-Archinity/issues/148); #147's containment claim
was the correct one.*)

Three supporting facts belong with it, because they close the exits an author would
reach for. The `Space` biome is `constantOutdoorTemperature -75` and `inVacuum true`,
and sets `canExitMap false`. `Verse.ExitMapGrid.MapUsesExitGridNow` is false for
`IsPlayerHome`, for `IsPocketMap` **and** for `map.Biome.inVacuum` — in orbit all three
apply. Nobody walks on and nobody walks off; every arrival and departure is a shuttle
or the gravship.

**The arrival gate is per faction, and vanilla opens it for four** [V].
`IncidentWorker_PawnsArrive.FactionCanBeGroupSource` (which raids, traders and visitors all reach)
refuses a faction whose
`FactionDef.arrivalLayerWhitelist` lacks the layer, and vanilla lists Orbit only for **Empire,
TradersGuild, Salvagers and Mechanoid**. Every other surface faction, and every modded one, never
sends help, visitors or traders to a gravship home unless its def is patched. A pinned-faction
`TryExecute` skips that check; vanilla's troop, labourer, strike and shuttle permits blacklist
Orbit through `RoyalTitlePermitDef.layerBlacklist`. **Fix:** XML — add Orbit to the faction's
`arrivalLayerWhitelist`, and to the incident's `layerWhitelist` where the storyteller should fire
it. (*[#168](https://github.com/cjd721/Rimworld-Archinity/issues/168), 2026-09-23.*)

*[#71](https://github.com/cjd721/Rimworld-Archinity/issues/71),
[#147](https://github.com/cjd721/Rimworld-Archinity/issues/147),
[#148](https://github.com/cjd721/Rimworld-Archinity/issues/148),
[#168](https://github.com/cjd721/Rimworld-Archinity/issues/168), `docs/specs/ORBIT.md`.
`RimWorld.IncidentWorker.CanFireNow`, `RimWorld.QuestScriptDef.CanQuestOccurOnTile`,
`RimWorld.IncidentWorker_GiveQuest.CanQuestOccurOnTile`,
`RimWorld.QuestGen.QuestGen_Get.GetMap`. Corpus scope: Core plus Royalty, Ideology,
Biotech and Odyssey — **Anomaly absent**. 1.6.4871.*

### T-87 — A vehicle's `customRoadCosts` discards the road ladder, and it is not a floor

`Vehicles.RoadCostHelper.GetRoadMovementDifficultyMultiplier` takes
`roadDef.movementCostMultiplier` as a base and lets
`VehicleDef.properties.customRoadCosts[roadDef]` **replace** it. The loop is
`if (customRoadCosts.TryGetValue(roadDef, out value) && (!flag || value < num))`:
`!flag` short-circuits the comparison on the first declaring vehicle, so **the first
declarer overwrites the def value whatever its direction**, and "lower wins" applies
only *among* declaring vehicles. A vehicle can therefore be **slower** on a road than
the `RoadDef` says. There are **two** `RoadDef` overloads, `(List<VehicleDef>, …)` and
`(List<VehiclePawn>, …)`, with identical bodies; the `VehiclePawn` one is what a live
caravan reaches, and a patch aimed at one of them misses the other. **T-42** carries the
same reading for the road half of the pair.

The silent part is what fills that dictionary. `<customRoadCosts AssignDefaults="0.25"/>`
is not a per-road table — `Vehicles.VehicleProperties.PostDefDatabase` hands it to
`Vehicles.XmlHelper.FillDefaults_Def<RoadDef, float>`, which `TryAdd`s **one flat number
for every `RoadDef` in the database**. Fourteen of Vanilla Vehicles Expanded's
twenty-three vehicles declare it that way (0.25 to 0.85), so for most of the roster a
dirt path and an ancient asphalt highway cost the same. **Patch the five-tier ladder in
`Core/Defs/RoadDefs/RoadDefs.xml` and vehicle travel time does not change, anywhere, with
no message.** It is indistinguishable in play from T-42 surviving the fix, which is what
makes it expensive: the tooltip prints a road line either way, and it prints the same
percentage on every tier.

The remedy is `docs/specs/WORLD-INFRASTRUCTURE.md` **§ 4c** — hang
`Vehicles.CustomCostDefModExtension` on each `RoadDef` with an empty `vehicles` list.
It works because of an ordering that is easy to get backwards:
`Vehicles.VehicleHarmony`'s `[StaticConstructorOnStartup]` constructor runs
`PostDefDatabaseCalls` (the `TryAdd` fill) **before** `ApplyAllDefModExtensions`, and
`Vehicles.PathingHelper.LoadDefModExtensionCosts` writes by **indexer**, not `TryAdd` —
so the extension overwrites the `AssignDefaults` values rather than losing to them. An
empty `vehicles` list means every `VehicleDef` in the database. **Do not instead delete
the `customRoadCosts` nodes**: only one `CustomCostDefModExtension` per cost def is ever
read (**T-06**), and a `VehicleDef` whose `defaultImpassable` contains `Roads` treats a
missing key as impassable rather than as a lost multiplier.

Read at `294100/3014915404/1.6/Assemblies/Vehicles.dll` and
`294100/3014906877/1.6/Defs/VehicleDefs/`. Both mods ship 1.4 source only; none of it
was read.

*[#68](https://github.com/cjd721/Rimworld-Archinity/issues/68),
`docs/specs/WORLD-INFRASTRUCTURE.md` § 4c. 1.6.4871.*

### T-117 — A `Caravan_PathFollower` patch never runs for a Vehicle Framework caravan

**`VehicleCaravan` is a `Caravan`, but it does not move through `Caravan_PathFollower`.**
`Vehicles.Patch_WorldPathing.StartVehicleCaravanPath` prefixes `Caravan_PathFollower.StartPath`.
For a `VehicleCaravan` it calls `vehicleCaravan.vehiclePather.StartPath(…)` and returns `false`.
From then on, movement runs through `Vehicles.World.VehicleCaravan_PathFollower`, a **sealed** class
unrelated to vanilla's, with its own private `TryEnterNextPathTile` and `PatherTick` [V]. The
vanilla follower on the same caravan never starts a path, so `PatherTickInterval` never reaches
`TryEnterNextPathTile` for it [V].

**So any postfix on `Caravan_PathFollower.TryEnterNextPathTile`, or on the rest of vanilla's
per-tile movement, does nothing for vehicle caravans, and nothing says so.** The caravan still
counts as a `Caravan` for type tests, `Find.WorldObjects.Caravans` and
`Storyteller.AllIncidentTargets` [V]. A hook that works on a walking caravan therefore looks
correct until a vehicle is formed.
Faction Territories' encounter trigger (`CaravanTerritoryIncidents`, a `TryEnterNextPathTile`
postfix) is exactly this, and never fires for a vehicle caravan [V].

**Fix:** patch `VehicleCaravan_PathFollower.TryEnterNextPathTile` as well, by name through
`AccessTools`, because it is private. Better, use a hook that reads `Caravan.Tile` on a tick or a
storyteller comp and does not care which follower moved the caravan. Aircraft in flight are
`AerialVehicleInFlight`, not a `Caravan`, and neither hook reaches them [V].

**This does not put VF caravans outside vanilla's arrival handling.** VF's follower carries the
vanilla `CaravanArrivalAction` objects and calls their `StillValid` every tick
(`VehicleCaravan_PathFollower.PatherTick`), so a patch on an arrival action reaches VF caravans
and a patch on the pather does not [V] (#152; see **T-138** and **T-139**).

*[#136](https://github.com/cjd721/Rimworld-Archinity/issues/136), `docs/specs/POLITICS.md` §
*Settlements meet passing caravans*;
[#152](https://github.com/cjd721/Rimworld-Archinity/issues/152) for the arrival-action
paragraph. `Vehicles.Patch_WorldPathing.StartVehicleCaravanPath`,
`Vehicles.World.VehicleCaravan_PathFollower.TryEnterNextPathTile` / `.PatherTick`,
`Vehicles.World.VehicleCaravan`, `Vehicles.World.AerialVehicleInFlight` from
`294100/3014915404/1.6/Assemblies/Vehicles.dll`; `RimWorld.Planet.Caravan_PathFollower.StartPath` /
`.PatherTickInterval` / `.TryEnterNextPathTile` (`Assembly-CSharp.dll`). 1.6.4871.*

### T-138 — An attack order carries on after its target passes to an ally, and turns the ally hostile with no confirmation

`CaravanArrivalAction_AttackSettlement.CanAttack` checks only `Spawned`, `Attackable`
(`Faction != OfPlayer`) and the enter cooldown. **It never checks the faction.** The *"attack a
friendly faction?"* confirmation (`ConfirmAttackFriendlyFaction`) is a `confirmActionProxy` that
runs **only when the order is given**. So when a settlement changes hands to an ally or neutral
faction while a caravan is marching on it with an attack order, the re-check on every interval
passes, the caravan arrives, and `SettlementUtility.AffectRelationsOnAttacked` drives the new
owner to hostile. The player sees no prompt and no warning, only the attack letter after the fact.

The same hole exists in two other places:

- `TransportersArrivalAction_AttackSettlement.CanAttack` (pods and shuttles, checked on arrival
  only);
- Vehicle Framework's aircraft `ArrivalAction_AttackSettlement`. It is never re-checked, and
  `ArrivalAction_LoadMap` resolves the target by `MapParentAt(tile)`.

A deliberate attack on a non-hostile faction still prompts as usual. The hole is an order issued
**before** the transfer.

**Fix:** stop such orders inside the transfer command, or guard the attack actions'
`StillValid`. See `docs/specs/TERRITORY.md` § *A caravan en route when its destination changes
hands*.

*[#152](https://github.com/cjd721/Rimworld-Archinity/issues/152), `docs/specs/TERRITORY.md` §
*A caravan en route when its destination changes hands*. `Assembly-CSharp.dll` 1.6
`CaravanArrivalAction_AttackSettlement`, `SettlementUtility.AttackNow`,
`TransportersArrivalAction_AttackSettlement`; `3014915404/1.6/Assemblies/Vehicles.dll`
`FlightPath.ConsumeNode`, `ArrivalAction_LoadMap.Arrived`, `ArrivalAction_AttackSettlement.MapLoaded`.*

### T-139 — A custom `CaravanArrivalAction` that does not override `StillValid` never cancels itself

`CaravanArrivalAction.StillValid` returns `true` in the base class. Vanilla's pather re-checks
every interval (`Caravan_PathFollower.PatherTickInterval`) and on arrival, but only through that
method. **An arrival action of ours will march a caravan to a target that has since been destroyed
or has changed owner, and then call `Arrived` on stale state**, with no message. Transport pods
re-validate only on arrival.

Every one of our arrival actions must override `StillValid` with the target's `Spawned`, faction
and tile checks:

- the #92 / `TERRITORY.md` §1 attend option;
- #154 RC-1, RC-4 and RT-1 (C1, C4 and T1 in `WORLD-INFRASTRUCTURE.md` § *The player's two verbs on
  a route*);
- #171 OU-A1 and OU-A3 (attend);
- #172 H-T1 (attend) and every H-L release option that is an arrival action;
- #167's advance option, if it is built as an arrival action rather than a direct float-menu
  option on the holding.

*[#152](https://github.com/cjd721/Rimworld-Archinity/issues/152); the list from
[#154](https://github.com/cjd721/Rimworld-Archinity/issues/154),
[#167](https://github.com/cjd721/Rimworld-Archinity/issues/167),
[#171](https://github.com/cjd721/Rimworld-Archinity/issues/171) and
[#172](https://github.com/cjd721/Rimworld-Archinity/issues/172). `Assembly-CSharp.dll` 1.6
`CaravanArrivalAction.StillValid`, `Caravan_PathFollower.PatherTickInterval`.*

### T-144 — An XML `<mapGenerator>` on the Settlement `WorldObjectDef` also rebuilds every new player colony

Player and NPC settlements are made from the same def, `layer.Def.SettlementWorldObjectDef`:

- `FactionGenerator` for NPCs;
- `SettleUtility.AddNewHome` for a new colony;
- `ScenPart_PlayerFaction` for the start.

`Settlement.MapGeneratorDef` returns `def.mapGenerator` **before** its
`Faction == OfPlayer → Base_Player` branch. A patch that gives the Settlement def a harder
`mapGenerator` for enemy bases therefore generates the player's next colony as one too. It raises
no error. Per-faction or per-settlement generators need a getter postfix (KCSG's
`Postfix_Settlement_MapGeneratorDef` is the pattern) or a distinct `WorldObjectDef`.

*[#164](https://github.com/cjd721/Rimworld-Archinity/issues/164), `docs/specs/TERRITORY.md` §
*Taking a settlement must be hard*. `Assembly-CSharp.dll` 1.6 —
`RimWorld.Planet.Settlement.MapGeneratorDef`, `SettleUtility.AddNewHome`, `FactionGenerator`,
`ScenPart_PlayerFaction`. [V]. `ORBIT.md` § *The build → 6* already records the three-branch
getter; this is the surface consequence.*

## Living on an orbit layer

Four of these belong with **T-48** and are filed here for the same reason it is: the orbit
layer is the subject, and no group in the register names it. See the register's own note on
the split this shape is asking for.

### T-128 — `QuestNode_Root_WandererJoin.CanBeSpace` is `false` on all five shipped subclasses

`WandererJoins`, `RefugeePodCrash`, `RefugeePodCrash_Baby` and `RefugeePodCrash_Ghoul`
(**[I]** — the class inherits the same unoverridden `CanBeSpace`, but Anomaly is not installed
on this disk and its def was not read) and `WandererJoinAbasia` never generate on an orbit-only
home [V]. The gate is a C# property, **upstream of acceptance**, so each def's
`everAcceptableInSpace: true` XML is a dead letter on these defs.

**The path is barred three times, not once** [V]: silently at generation via
`QuestGen_Get.GetMap(canBeSpace: false)`; at acceptance, because
`QuestNode_Root_WandererJoin.RunInt` calls `quest.AcceptanceRequirementNotSpace(var.Parent)`
whenever `!CanBeSpace` **regardless of the def's own flags**; and at the letter, by
`ChoiceLetter_AcceptJoiner`. A build that fixed only `TestRunInt` would produce a quest the
colony cannot accept.

**`everAcceptableInSpace` is not an ignored field** — it *is* consumed, in
`QuestScriptDef.CanQuestOccurOnTile` (`if (!autoAccept && !everAcceptableInSpace &&
layerDef.isSpace) return false;`) and in `QuestGen.Generate` [V]. Every def in the joiner family
sets `autoAccept`, so `!autoAccept` short-circuits both tests before the flag is reached. Dead
letter *here*; real on the ~60 non-`autoAccept` roots that carry it.

**Fix:** the one seam that clears all three is `CanBeSpace`. **T-49** is not the cause here and
was corrected accordingly.

*[#147](https://github.com/cjd721/Rimworld-Archinity/issues/147), `docs/specs/GRAVSHIP.md` §
*Ordinary colony life on an orbital home*. `RimWorld.QuestGen.QuestNode_Root_WandererJoin`
(`.CanBeSpace`, `.TestRunInt`, `.RunInt`), `RimWorld.QuestGen.QuestGen_Get.GetMap`,
`RimWorld.QuestScriptDef.CanQuestOccurOnTile`, `RimWorld.ChoiceLetter_AcceptJoiner`;
`Core/Defs/QuestScriptDefs/Script_WandererJoins.xml`. Corpus scope: vanilla + Core, Royalty,
Ideology, Biotech, Odyssey — **Anomaly absent**. 1.6.4871.*

### T-129 — `TerrainDef Space` is `Impassable`, so no edge-entry cell exists on an orbital map

`RCellFinder.TryFindRandomPawnEntryCell` cannot succeed on a map whose edge is `Space` [V], and
the arrival worker simply returns false.

**So whitelisting `VisitorGroup`, `TravelerGroup` or `TraderCaravanArrival` for the Orbit layer
is a silent no-op.** The def passes every layer gate you patched, the incident is selected, and
nothing arrives. The whitelist looks like the fix and is not one; only a drop-style arrival mode
reaches an orbital map at all.

This is the companion of **T-48**'s exit half (`ExitMapGrid.MapUsesExitGridNow` false for
`inVacuum`): nobody walks on and nobody walks off.

*[#147](https://github.com/cjd721/Rimworld-Archinity/issues/147), `docs/specs/GRAVSHIP.md` §
*Ordinary colony life on an orbital home*. `Verse.RCellFinder.TryFindRandomPawnEntryCell`,
`RimWorld.PawnsArrivalModeWorker_EdgeWalkIn`; `Data/Odyssey/Defs/TerrainDefs/`. 1.6.4871.*

### T-130 — Prisoners cannot be released and slaves cannot be emancipated on a vacuum map

`WorkGiver_Warden_ReleasePrisoner`, `WorkGiver_Warden_EmancipateSlave` and
`JobGiver_ExitMap.TryGiveJob` all bail on `!MapHeld.CanEverExit` [V], which is false on an
orbital map.

**There is no alert, no message and no disabled button — the work giver simply never offers the
job.** A prison-break escapee has no exit job either, so it mills about the map until something
else picks it up. From the player's side this reads as pawns ignoring an order.

**Fix:** anything the campaign wants done with a prisoner in orbit — release, emancipation,
exile — needs a shuttle or a transport pod path of its own. The vanilla verbs are not available
and do not say so.

*[#147](https://github.com/cjd721/Rimworld-Archinity/issues/147), `docs/specs/GRAVSHIP.md` §
*Ordinary colony life on an orbital home*. `RimWorld.WorkGiver_Warden_ReleasePrisoner`,
`RimWorld.WorkGiver_Warden_EmancipateSlave`, `RimWorld.JobGiver_ExitMap.TryGiveJob`,
`Verse.Map.CanEverExit`. 1.6.4871.*

### T-131 — Every sealed orbital home runs a standing −5 `NeedOutdoors` mood penalty

`Need_Outdoors` floors at **0.2** under a thin roof [V], and 0.2 is `CabinFeverSevere` — stage 2
of the need's thought chain. **Every gravship roof is thin** [V].

So a colony living in orbit carries a permanent cabin-fever mood debuff that no amount of room
size, beauty or lighting removes, because the cause is the roof and there is no alternative
roof. Nothing reports it as a design consequence; it presents as a mood problem with no
identifiable source.

**Fix:** budget for it, or offset it deliberately. There is no thin-roof exemption for a
vacuum-sealed hull.

*[#147](https://github.com/cjd721/Rimworld-Archinity/issues/147), `docs/specs/GRAVSHIP.md` §
*Ordinary colony life on an orbital home*. `RimWorld.Need_Outdoors`,
`RimWorld.ThoughtDefOf.CabinFeverSevere`. 1.6.4871.*

### T-132 — Odyssey populates every planet layer at world creation, so the Orbit layer is never empty

`WorldComponent_LocationGenerator` runs from **`FinalizeInit`**, not from a gen step [V] — which
is why an audit of `Orbit`'s `worldGenSteps` (`Tiles`, `Factions`) truthfully reports no object
generation and is still wrong about the outcome. It then ticks in `WorldComponentTick`, budgeting
per layer as `planetLayer.Def.generatedLocationFactor * worldLocationsTarget`, and Odyssey's
`GeneratedLocationDef Asteroids` targets `Orbit`.

`worldLocationsTarget` is fixed in the component's constructor from `world.PlanetCoverage` [V]:

| Planet coverage | Asteroids in orbit at creation |
|---|---|
| < 5.1% | **3** |
| 5.1% – 30.0% | **8** |
| 30.1% – 50.0% | **12** |
| ≥ 50.1% | **20** |

**The floor is the point: no coverage setting produces an empty orbit layer**, and
`AnyWorldObjectOnLayer` applies no filter [V], so one asteroid opens the view-orbit gizmo
exactly as well as twenty. **The gizmo is live from the first tick of a fresh world.**

Nothing logs and nothing warns. A design that assumes an empty layer — a reveal gated on orbit
being visibly untouched — looks correct in review and is already false the moment the world is
created.

*[#148](https://github.com/cjd721/Rimworld-Archinity/issues/148), `docs/specs/ORBIT.md` §
*The reveal gate*. `RimWorld.Planet.WorldComponent_LocationGenerator` (`.FinalizeInit`,
`.WorldComponentTick`, `..ctor`), `RimWorld.Planet.GeneratedLocationDef`,
`RimWorld.Planet.WorldObjectsHolder.AnyWorldObjectOnLayer`;
`Data/Odyssey/Defs/GeneratedLocationDefs/GeneratedLocations.xml`. 1.6.4871.*

### T-133 — Scrolling out on the world map switches planet layer without consulting `CanSelectLayer`

`WorldCameraDriver` switches the selected layer on zoom when `PrefsData.zoomSwitchWorldLayer` is
true — **it is true by default** — and `ScenarioBase` carries the matching `zoomMode` [V]. The
switch does not go through whatever gate a design put on the layer button.

**A disabled view gizmo is not a closed layer.** The player reaches orbit by scrolling out, the
bypass leaves no trace, and nothing distinguishes a layer that was revealed from one that was
scrolled into.

**Fix:** `WorldSelector.set_SelectedLayer` is the sole writer of the selected layer
(`docs/engine/world-time-and-layers.md`), so it — not the gizmo — is the chokepoint anything
policing layer access has to take.

*[#148](https://github.com/cjd721/Rimworld-Archinity/issues/148), `docs/specs/ORBIT.md` §
*The reveal gate*. `RimWorld.Planet.WorldCameraDriver`, `Verse.PrefsData.zoomSwitchWorldLayer`,
`RimWorld.Planet.WorldSelector.SelectedLayer`, `RimWorld.ScenarioBase`. 1.6.4871.*

### T-134 — `canTraverseLayers: true` turns a cross-layer distance from `int.MaxValue` into a near-zero hop, and poisons a cache on the way

`WorldGrid.TraversalDistanceBetween(start, end, passImpassable = true, maxDist = int.MaxValue,
canTraverseLayers = false)` returns `int.MaxValue` across layers **by default** [V]. Pass `true`
and it **projects** `start` onto `end`'s layer first, so the same call returns a small number —
with no error, no warning and no change in the call site's shape.

**A relocation or pursuit test written against this reads better with `true` and stops firing on
exactly the move it was written for**: the planet↔orbit jump, the largest move in the campaign,
measures as almost nothing.

**The second half is worse, because it reaches callers that never passed `true`.** In order,
`TraversalDistanceBetween` does `start == end` → `0`; either tile invalid → `int.MaxValue`;
**then the static cache**; then the layer guard; then `!passImpassable && !CanReach`; then the
flood fill [V]. On a `canTraverseLayers: true` cross-layer call it sets `cachedLayer = end.Layer`,
projects `start`, and then writes the cache under the **original, unprojected** start — the local
`planetTile`, saved before the reassignment [V]. So one such call on an ordered pair leaves a
**finite** cross-layer distance that every subsequent *default* call on that same pair returns,
ahead of the guard, until a different pair evicts it.

**No vanilla caller passes `true`** — `GravshipUtility.TryGetPathFuelCost` pre-projects instead
[V] — so the path is unarmed in shipped code today and one mod away from armed. **A corpus sweep
cannot bound this**: a positional `true` leaves no string in any metadata heap, so a zero-hit
sweep for `canTraverseLayers` is evidence about the identifier, not about callers.

**Fix:** branch on the layer *before* the call rather than trying to make one call answer both
cases. See `docs/engine/gravship-and-substructure.md` § *Landing hooks* for the four sources of
`int.MaxValue` and why a finite value rules a layer change out while `int.MaxValue` does not rule
one in.

*[#150](https://github.com/cjd721/Rimworld-Archinity/issues/150), `docs/specs/TRACE.md` §
*Planet↔orbit as a qualifying relocation*. `RimWorld.Planet.WorldGrid.TraversalDistanceBetween`,
`RimWorld.GravshipUtility.TryGetPathFuelCost` (`Assembly-CSharp.dll`). 1.6.4871.*

---
