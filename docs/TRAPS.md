# The trap register

**Read this index before writing a def or a `.cs` file. Flag every occurrence in
review, and cite the ID.**

Every trap listed here fails **without an error message**. None is caught by running
the game; several are not caught by reading the log either. `CODING_STANDARDS.md`
owns the rule ("check the register"); this file is the whole register at a glance,
and each group's file carries the mechanism, the evidence and the fix.

Read the index whole — it is short on purpose, and the traps cross domains: an
unscoped xpath (T-03) is what bites in a mod patch (T-26), and settings sync (T-18)
is what bites in faction work. When a row looks like it might be you, open its file.

Cite `T-14`, never a line number. IDs are stable and never reused.

## Defs and patching — [`docs/traps/defs-and-patching.md`](traps/defs-and-patching.md)

| ID | Trap |
|---|---|
| T-01 | `--` inside an XML comment drops the entire file, unnamed |
| T-02 | PatchOperations run *before* `ParentName` inheritance resolves |
| T-03 | Patch xpaths apply to the whole merged database; `PatchOperationFindMod` does not scope |
| T-04 | Unresolvable cross-references are omitted, not nulled — a stripped prerequisite reads as "none" |
| T-05 | `XmlInheritance` appends list children rather than replacing them |
| T-06 | `Def.GetModExtension` returns the FIRST match; a second is inert |
| T-37 | `Verse.DefMap<D,V>` scribes positionally — adding or removing a def mid-save rebinds every value to the wrong key |
| T-40 | `requiredAnalyzed` is nulled without Biotech; the gate ceases to exist and the project becomes free |
| **T-50** | **A budget computed from un-patched def values is wrong once mods merge — the compat patch one mod ships *for another* is the copy that wins** |
| **T-55** | **`GenTypes` resolves short names last-writer-wins; a mod type in no namespace replaces the vanilla one for every `Class=` lookup** |
| T-69 | `AccessTools.Field(...)?.SetValue(...)` is a silent no-op after a rename — `ResetHackProgress` does it ten times |
| T-79 | Granting a work type from research and not calling `Pawn.Notify_DisabledWorkTypesChanged()` leaves every colonist unable to do the work until the next load, with no message |
| T-83 | A `GoodwillSituationDef` with no `workerClass` is inert end to end — `baseMaxGoodwill` is read nowhere, the default worker returns a hardcoded 100/0, and the faction card shows no row at all |
| T-84 | `PreceptComp_GoodwillSituation` is inert in 1.6 — the list its only reader writes to is never read |
| T-92 | Declaring a modded research tab silently enrols a `requiredAnalyzed`-gated project into the vanilla `Schematic` book's grant pool, bypassing the gate |
| T-99 | Declaring `techprintCount` puts the techprint into every faction-less generator — orbital trade ships, map-gen loot and asker-less rewards skip `heldByFactionCategoryTags` |
| T-136 | `OutfitStandBase` declares no `thingClass`, so a def derived from it is a plain `Building` — no gizmo, no contents, no error |

## World creation and factions — [`docs/traps/world-creation.md`](traps/world-creation.md)

| ID | Trap |
|---|---|
| **T-07** | **The faction roster must be final BEFORE world creation — not repairable by patch** |
| T-08 | `maxCountAtGameStart` / `canMakeRandomly` are `[Obsolete]` no-ops in 1.6 |
| T-09 | `requiredCountAtGameStart` is dead code |
| T-10 | The `replacesFaction` prune runs over defs you excluded, deleting ones you kept |
| T-11 | Writing `FactionDef.techLevel` at runtime silently reverts on load |
| T-12 | `Settlement.cachedMat` is never invalidated |
| T-13 | `FactionUtility.DefaultFactionFrom` returns null once a faction climbs |
| T-14 | VFE Empire blacklists every other raid strategy on its deserter faction |
| T-15 | `VFET_OpportunitySite_WildMen` generates a faction at runtime, unguarded — breaks T-07 |
| T-16 | `RaidStrategyDef` / `QuestScriptDef` have no `minTechLevel` field at all |
| T-17 | Raid faction selection is fail-open and fail-quiet |
| T-36 | Swapping `Faction.def` freezes the title ladder — `royalTitleTags`, `royalFavorLabel` and `categoryTag` do not follow |
| T-45 | `PlanetLayer` geometry rebuilds from *scribed* values, so a layer-size patch after worldgen is a silent no-op |
| T-49 | `Find.RandomSurfacePlayerHomeMap` returns null once the only home is in orbit, taking three quest nodes with it |
| **T-54** | **World Tech Level silently strips factions from the worldgen roster and gensteps from the map** |
| T-68 | `SetFactionDirect` leaves a seized turret in the wrong attack-target bucket until a reload |
| T-65 | VEF's `forcedPointsRange` sentinel is `IntRange.One`; omit it and the authored raid fires at zero points |
| T-70 | `QuestNode_End` sets `signalListenMode` on the end part but not on the goodwill change beside it |
| T-71 | A chain-granted quest skips `TestRun`, so `CanRun`, `QuestNode_QuestUnique` and `minRefireDays` are inert |
| T-72 | VEF's `conditionFailQuests` never matches an expired offer — `outcome` is written only on completion |
| T-73 | VEF's `grantAgainOnExpiry` passes a tick count into an `mtbDays` parameter and never fires |
| T-76 | A VEF `QuestGiverDef` with `onlyOneReward: false` has a permanently empty catalogue |
| T-77 | `QuestWorker.GenerateQuests` swallows every generation exception, so a broken quest script silently never appears |
| T-85 | World Tech Level's planet-tab button writes the scribed `GameComponent_TechLevel` from `FillTab` — a client-local write to synchronised state, off a draw path |
| T-86 | WTL's `Window_AddFactions` registers factions at runtime and spawns settlements on a `Rand` bound re-drawn inside the loop condition, from `DoWindowContents` — armed whenever `Filter_Factions` is on |
| T-88 | A factionless or inert `attackTargets` focus issues no job at all — the objective no-ops and the group lingers until auto-flee |
| T-89 | `Trigger_ThingsDamageTaken` cannot express a partial loss of pawns — "destroy a fraction" silently means "destroy all of them" |
| T-90 | A `RaidStrategyDef` authored without `arriveModes` is silently unselectable forever, and a vanilla strategy is picked in its place |
| T-91 | `VFEE_Deserters` silently stops raiding whenever no Empire-titled pawn is on the map |
| T-98 | Swapping a faction's `Faction.def` nulls `Faction.OfEmpire` (and every `FactionManager` singleton) at the next load or faction add/remove, not at the swap |
| T-100 | An "allied factions" filter over NPC pairs is empty in vanilla — no NPC↔NPC `Ally` relation ever exists, and nothing says so |
| T-101 | A quest reward option whose rewards draw no stack element is never shown and can never be accepted — and any `QuestPart_Choice` hides the plain Accept button |
| T-102 | `QuestGen_Rewards.GiveRewards` silently drops royal favour (Exaltation) unless the asker holds a title in its own faction |
| T-103 | A VEF `QuestGiverDef` never refills after a purchase unless `resetEveryTick` is set — and a reset discards every unbought offer |
| T-109 | Unlisting a faith from its last faction deletes it at the next holder's death or map exit, silently moving every world pawn that held it to its faction's primary |
| T-110 | A positive goodwill write returns `false` with no message while any player map sits on that faction's settlement — a revolt, liberation or battle reward paid on the map never lands |
| T-112 | A humanlike joining the player faction has its `kindDef` reset to `basicMemberKind`, and a run-wild break sets `WildMan` — a `PawnKindDef` used as a marker silently vanishes |
| T-115 | A `StorytellerDef` carrying VEF's `storytellerThreat` replaces every faction's natural goodwill with one number (0 by default) — every `GoodwillSituationWorker` natural offset is discarded |
| T-116 | `QuestPart_SetFactionHidden` does not scribe `hidden` — a part that hides a faction becomes one that reveals it after a save and load |
| T-118 | A faction set in `IncidentParms` is ignored by `CaravanMeeting` and overwritten by `Ambush_EnemyFaction` and `CaravanDemand` — the encounter fires with a random faction |
| T-119 | A caravan incident never fires in a biome its `mtbDaysByBiome` omits — vanilla's three caravan encounters are absent from every Odyssey and modded biome |
| T-124 | A shelved offer whose expiry clock has run is bought for nothing — `Quest.Accept` no-ops, the currency is debited and a letter still arrives |
| T-125 | Two VEF quest-giver comps sharing a `questManagerID` silently share one shelf, built from whichever `QuestGiverDef` was used first |
| T-126 | `generateOnce: true` fills the shelf twice, at a budget of 100 unless `maximumAvailableQuestCount` is set |
| T-127 | `QuestNode_GetSiteTile`'s early-out guard is typed `int` against a `PlanetTile`, so it never fires and `siteDistRange` never measures from a caravan |
| T-140 | Per-settlement state across an ownership change — `SetFaction` silently carries every comp, record and tithe to the new owner; destroy-and-recreate mints a new ID that re-rolls ID-derived values, orphans ID-keyed records and aborts inbound orders. FT&V's `ApplyWinnerToSettlement` takes both shapes, by attendance |
| T-142 | A goodwill refund written as a second `TryAffectGoodwillWith` does not restore the balance — vanilla amplifies whichever leg moves toward natural goodwill, and a Reverence scaler on positive gains would skew the refund leg again |
| T-145 | Under R1, a holding's tier or specialty read from `holding.Faction` reads the player's def, which `AdvanceEra()` rewrites at every boundary |
| T-147 | VEF's `GoodwillCurrency` silently offers nothing for a quest with no `asker` on the slate |
| T-148 | A pawn committed to a VEF outpost drops out of the storyteller's population — committing pawns silently raises population intent |
| T-149 | Rejecting a humanlike from VEF `Outpost.AddPawn` silently skips the outpost's build charge |
| T-150 | A map generated on a tile that already holds a `MapParent` is parented by it — M-proxy works only while the target is not a `MapParent`; a VEF outpost adopts the map with the `Encounter` generator and never removes it |
| T-151 | Destroying a staffed VEF outpost drops its living pawns with no death, no letter and no world-pawn record |
| T-152 | An outpost occupant who dies of disease or bleeding stays in `occupants` — it still counts, still produces, and the outpost is never abandoned |

## Multiplayer and determinism — [`docs/traps/multiplayer.md`](traps/multiplayer.md)

| ID | Trap |
|---|---|
| T-18 | Mod settings are part of the sync surface — the third thing people miss |
| T-19 | Medieval Overhaul forces a setting from a *draw method* |
| T-20 | MO's schematic cache is unkeyed and UI-poisoned — a live desync bug |
| T-21 | Filter at draw time, never at list-membership time |
| **T-22** | **77 mods have a second copy on disk under one `packageId`; six have drifted apart — VEF among them — and `corpus.py --check` reports the corpus clean** |
| **T-33** | **KCSG generates settlements from an unseeded `System.Random` — two clients get different maps, and MP's checksum cannot see it** |
| T-39 | `QuestScriptDef.CanRun` draws on the shared `Rand` stream and memoises per tick and threat points — calling it from render code desyncs, and a per-noble decree gate answers every titled colonist with the first one's result |
| **T-51** | **MP Compat's Unity-RNG transpiler rewrites 4 members and half-fixes the rest in silence — unlike its `System.Random` sibling, it is not all-or-nothing** |
| T-52 | `Dialog_Rename<T>.OnRenamed` runs client-locally, ahead of the synced setter |
| T-53 | `Window.forcePause` does not pause a Multiplayer session |
| T-61 | VEF's study-designation gizmo writes scribed state and no Multiplayer Compat patch covers it |
| T-66 | A storyteller comp's list index salts a `Rand` seed — inserting one re-rolls every later comp's schedule |
| **T-67** | **Hacking Expansion's settings rewrite `ThingDef.comps` at `RebindAllDefOfs`, and a third injection is ungated entirely** |
| **T-74** | **Vehicle Framework pathfinds on the .NET thread pool, and neither its own switch nor MP Compat reaches it** |
| T-75 | `Vehicles.SectionDebug.debugUseMultithreading` cannot be set — there is no flag to turn that threading off |
| T-78 | Multiplayer wraps the gravship *landing* for determinism and does not wrap the *takeoff*; code hung on `TakeoffEnded` or `TravelTo` runs unfrozen and unseeded |
| T-80 | A caravan gizmo or dialog is outside Multiplayer's float-menu SyncAction — the net covers `WorldObject.GetFloatMenuOptions`, and nothing else on a caravan |
| T-81 | Overriding `WorldObject.UpdateRateTicks` escapes MP's VTR prefix, and the world-object tick phase silently goes back to depending on which player has the world map open |
| T-82 | Multiplayer syncs a `DiaOption` click by its **index**, through either of two contending prefixes — and one of them re-resolves the dialog client-locally, so identical option lists are necessary but not sufficient |
| T-95 | Subclassing `Dialog_NodeTree` drops it out of Multiplayer's `PersistentDialog` bindings — options never sync, and the one log line names no type |
| T-96 | A modded `ChoiceLetter`'s options are synced by neither mechanism — identical on both clients, acting on one |
| T-97 | A `DiaOption` without `resolveTree = true` strands its `mapDialogs` entry, and `ForceShowDialogs` re-opens an already-answered dialog forever |
| T-114 | Multiplayer's multifaction faction creation runs no `GameComponent.StartedNewGame`, only two `ScenPart.PostGameStart`s, and never writes `GameInfo.startingAndOptionalPawns` — a game-start stamp silently misses a joining player's pawns |
| T-120 | Map generation runs on both clients and outside MP's checksum — a `GenStep` that diverges without `Rand` (hash order, `GetHashCode`, `DateTime`) desyncs later, silently. Not yet swept |
| T-135 | `GetClosestTile_NewTemp` resolves through a Burst job whose closest-tile tie-break depends on thread partitioning — two clients can pick different tiles |
| T-137 | Multiplayer registers `OrderForceTarget` only for `ITargetingSource` implementors in the vanilla assembly — one declared in ours must register itself |
| **T-143** | **KCSG's static `GenOption.settlementLayout` is never reset — a `chooseFromlayouts` faction's garrison is multiplied by whatever layout was generated last in the process, and diverges between clients after a rejoin** |

## Buildings, items, rituals and titles — [`docs/traps/content-and-buildings.md`](traps/content-and-buildings.md)

| ID | Trap |
|---|---|
| T-23 | `statFactors` on a facility is a silent no-op; facilities are additive-only |
| T-24 | `CompRefuelable` does not gate a `Building_PawnProcessor` — the fuel bar is decoration |
| T-25 | Genepacks decay in 20 days and roofs give zero protection |
| T-26 | An unscoped `PatchOperationSetName` reaches 395 ThingDefs |
| T-27 | `MeditationFocusDef` gates are *backstory* gates; a failed gate looks like nothing |
| T-28 | `RoyalTitleDef.Awardable` is `favorCost > 0` — a title with no favour cost is invisible to every award path |
| T-34 | Editing a `HediffDef`'s `comps` list drops the comp; its fields read as defaults on the next load |
| T-35 | The Permits tab is gated on `Faction.OfEmpire`, and the switcher that would fix it is drawn inside the gated card |
| T-38 | A `CompScanner` find that generates no quest still zeroes the guaranteed-find timer |
| T-41 | `analysisID` is a hand-picked int with no uniqueness check — a duplicate silently merges two Analysis gates |
| T-46 | Substructure cells past `SubstructureSupport` are silently dropped on launch, outermost first |
| T-47 | Only five stuffs are `isAirtight`; a stone, wood or obsidian room never pressurises |
| T-56 | `Thing.SmeltProducts` discards `efficiency` for a literal `0.25f` — and the info card prints the stat anyway |
| T-57 | `RecipeDef.smeltingWorkAmount` is honoured by reference identity against `SmeltOrDestroyThing` alone |
| T-58 | Any recipe with `specialProducts` silently loses "Do until you have X" |
| T-59 | `StudiableBuilding.Study` calls `DeSpawn`, so a studied building leaks forever into a scribed set |
| T-60 | `StudiableBuilding.Study` sends no quest signal; the sibling `LootableBuilding.Open` sends both |
| T-62 | A study designation on a null- or hostile-faction building is shown, scribed — and never worked |
| T-63 | Overriding `Gene.Label` reaches the tooltip header only; the tile and info card are typed on the def |
| T-64 | A `GeneVectorExtension` with `gene: null` spends the charge, grants nothing and reports success |
| T-93 | `Window_AndroidCreation.OnGenesChanged()` reassigns `requiredItems` wholesale on every gene toggle, discarding any write that is not a postfix on it |
| T-104 | `CompStudiable` progress does not survive stacking — a merge keeps one stack's study, a split starts at zero |
| T-105 | A believer count on a `Precept_RoleMulti` def is inert — and the role's tooltip still advertises it |
| T-106 | A `Precept_RoleSingle` with `activationBelieverCount` −1 never activates, sends no letter and shows no reason |
| T-107 | A custom `RoleEffect` subclass does nothing — every reader type-tests a vanilla class — while the tooltip lists its label |
| T-108 | `Ideo.GetRole` returns one role; a second role assigned to the same pawn is held and contributes nothing |
| T-94 | `Bill_ProductionMech.CreateProducts` resolves the gestated pawnkind by reverse-lookup `.First()` — two `PawnKindDef`s sharing a race yield whichever `DefDatabase` ordering returns |
| T-111 | A pawn's xenotype is not identity — reimplanting gives the recipient the caster's `XenotypeDef`, and implanting a xenogerm resets the target to Baseliner and deletes every xenogene |
| T-113 | `HediffDef.duplicationAllowed` defaults to `true` — an Anomaly duplicate silently inherits every per-pawn record hediff, comps and fields included |
| T-121 | No `FactionDef` restriction applies inside `Dialog_ReformIdeo` — every precept and meme gate silently lifts the moment the player clicks Reform |
| T-122 | A precept refused by `disallowedPrecepts` vanishes from the issue menu instead of greying out; its rejection reason is the empty string |
| T-123 | `FactionDef` **meme** fields on a player faction def are inert whenever a world exists — vanilla's own `PlayerTribe` `disallowedMemes` does nothing |
| T-141 | A faction-dialogue option appended for the Industrial comms console also appears at Medieval Overhaul's messenger table, an era early |
| T-146 | A permit granted without a title is permanent — vanilla never revokes it, and the "Call aid" gizmo keeps offering it after whatever granted it is gone |

## Worldgen layouts — [`docs/traps/worldgen-layouts.md`](traps/worldgen-layouts.md)

| ID | Trap |
|---|---|
| T-29 | Layout rows and cells beyond `layouts[0]` are dropped silently |
| T-30 | `defenseOptions` is dead below Industrial |
| T-31 | `DankPyon_MedievalSiege` cannot fire as shipped — empty intersection |
| T-32 | Rotated KCSG symbol variants are runtime-generated and cannot be patched |
| T-42 | All five vanilla `RoadDef`s share `movementCostMultiplier 0.5` — upgrading a road is a silent no-op |
| T-43 | A downgrade through `WorldGrid.OverlayRoad` returns silently; only a null `RoadDef` logs |
| T-44 | A road in an `allowRoads = false` biome is drawn but inert |
| T-48 | On an orbit layer the content pool collapses unannounced behind **four** separate whitelist gates — 18 of 91 incidents, and the storyteller's own reader leaves **2** of 139 quests, not the 18 the clause suggests |
| T-87 | A `RoadDef.movementCostMultiplier` patch is discarded for any caravan carrying a vehicle that declares `customRoadCosts` — the first declarer replaces the value in either direction |
| T-117 | A `Caravan_PathFollower` patch never runs for a Vehicle Framework caravan — VF diverts `StartPath` to its own sealed `VehicleCaravan_PathFollower` |
| T-128 | `QuestNode_Root_WandererJoin.CanBeSpace` is `false` on all five shipped subclasses, and the joiner path is barred three times over |
| T-129 | `TerrainDef Space` is `Impassable`, so whitelisting a walk-in arrival for an orbit layer is a silent no-op |
| T-130 | Prisoners cannot be released and slaves cannot be emancipated on a vacuum map — the work giver simply never offers the job |
| T-131 | Every sealed orbital home runs a standing −5 `NeedOutdoors` penalty; every gravship roof is thin |
| T-132 | Odyssey populates every planet layer at world creation, so the Orbit layer is never empty and the view gizmo is live from the first tick |
| T-133 | Scrolling out on the world map switches planet layer without consulting `CanSelectLayer` — a disabled gizmo is not a closed layer |
| T-134 | `canTraverseLayers: true` turns a cross-layer distance into a near-zero projected hop, and poisons a static cache that later default calls read |
| T-138 | An attack order issued before a settlement passes to an ally or neutral lands anyway — `AttackSettlement` never re-checks the faction, and the new owner turns hostile with no prompt |
| T-139 | `CaravanArrivalAction.StillValid` returns `true` in the base class — an arrival action of ours that does not override it marches on to a destroyed or transferred target |
| T-144 | An XML `<mapGenerator>` on the Settlement `WorldObjectDef` also rebuilds every new player colony — player and NPC settlements share one def |

---

## Adding an entry

A finding earns a slot **only if it fails silently**. A crash, a red error or a
startup exception is loud and belongs in the relevant `docs/engine/` file instead —
loudness is the whole selection criterion.

- Take the next free ID; **never renumber**, and never reuse a retired one.
- Add the entry to its group file, and a one-line row here. Both, or it is invisible.
- **Correct an entry in place** and update its provenance line. Do not append "an
  earlier draft said…" under superseded text.
- Every entry carries the build it was verified against.

**Allocate the ID against the working tree, not just this index.** T-34 was claimed
independently by six specs in one parallel batch because each agent read this file,
saw it end at T-33, and took the next number. If several tickets are in flight, the
orchestrator allocates; an agent proposes the trap and leaves it unnumbered.

A group file that passes roughly a dozen entries is a candidate for splitting
further; this index stays one file regardless, because it is the thing that gets
read whole. **All five are now over that line**, counted 2026-09-23 after the map #2
territory merge (#152–#172): `world-creation.md` (54), `content-and-buildings.md` (34),
`multiplayer.md` (27), `defs-and-patching.md` (17) and `worldgen-layouts.md` (20).

**The split the shape now asks for is an incidents-and-quests group, and this batch
sharpened the case rather than changing it.** None of the five names the subject, so
T-65, T-70 through T-73, T-76/T-77 and now **T-88 through T-91** sit in
`world-creation.md` on the strength of factions and goodwill alone — filed under an
*Incidents, quests and goodwill* heading inside it — and T-39 and T-48 are the same
subject filed under determinism and worldgen respectively. **That is 24 entries under
*Incidents, quests and goodwill* in `world-creation.md` and 26 across the register**, against
a host file whose remaining 30 are 23 about factions and worldgen and 7 under *Holdings,
outposts and world objects changing hands*. Adding a group
changes this index's shape and is Conrad's call; it is recorded here rather than taken.
