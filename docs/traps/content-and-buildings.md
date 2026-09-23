# Traps: buildings, items, rituals and titles

Content-side no-ops: comps that look like mechanisms, stats that are never read,
and gates that are invisible from the def.

Part of the trap register. **The index at `docs/TRAPS.md` is the file you read
before a diff**; this one carries the full entries for this group. Every entry here
fails with no error message. Cite by ID.

## Buildings, recipes and items

### T-23 — `statFactors` on a facility is a silent no-op

`CompProperties_Facility` has **`statOffsets` only**. There is no `statFactors`
field, and `CompAffectedByFacilities` overrides `GetStatOffset` but not
`GetStatFactor`, so a facility declaring `statFactors` does nothing at all.
Facilities are additive-only: express bench augments as offsets, or use
`RecipeDef.workTableSpeedStat` / `workTableEfficiencyStat`.

*`docs/engine/facilities-and-recipes.md`. 1.6.4871.*

### T-24 — `CompRefuelable` does not gate a `Building_PawnProcessor`

Adding `CompProperties_Refuelable` with a `HemogenPack` filter gives a real,
working fuel bar that gates nothing — VQE Ancients' code never reads
`CompRefuelable`. It looks like a mechanism and is decoration. Removing
`CompProperties_Power` instead is worse: `Building_PawnProcessor.PowerOn`
dereferences the power comp unguarded and NREs every tick.

Real gating requires a Harmony postfix on `Building_PawnProcessor.get_PowerOn`. The
capsule requirement is likewise not def-driven — `ThingDefOf.ArchiteCapsule` is
hardcoded in seven places.

*`docs/engine/mods/vqe-ancients.md`. 1.6.4871.*

### T-25 — Genepacks decay in 20 days and roofs do not help

`DeteriorationRate 5`/day against 100 max HP, no grace period, and
`deteriorateFromEnvironmentalEffects: false` — so roofs, rooms and shelves give
**zero** protection. Only a **powered** `GeneBank` stops it (research
`Xenogermination`, Industrial, cost 1000, itself gated behind Electricity, 40 W
constant); unpowered banks do not protect. Genepack rewards are viable from
Industrial onward, never before.

Do **not** patch `Genepack`'s `DeteriorationRate` to 0: genepacks are a single
ThingDef with dynamic contents, so it is all-or-nothing and would strip gene banks
of their entire purpose.

*`docs/engine/items-and-materials.md`. 1.6.4871.*

### T-26 — An unscoped `PatchOperationSetName` reaches the whole database

Medieval Overhaul's `component_replace` targets
`Defs/ThingDef/costList/ComponentIndustrial` with no scoping and hits **395
ThingDefs** across Core, all four DLC and 47 active mods — including `Ship_Beam`,
`Ship_SensorCluster`, `Ship_CryptosleepCasket`, Odyssey's `GravFieldExtender` and
`Apparel_Vacsuit`, every GravTech pylon and 24 `BfG_*` buildings. This is T-03 in
production, at scale.

It is also **half-broken**: the ingredient-side op targets
`Defs/RecipeDef/li/filter/thingDefs/li`, which matches **0** nodes (the correct path
matches 17), and its inner `PatchOperationReplace` has no xpath and would throw if
it fired. Read it as a whole-database rename when reasoning about anything
downstream of components. `chemfuel_replace` is structurally identical: 51 defs,
zero Spacer.

*`docs/engine/mods/medieval-overhaul.md`. MO 1.6.*

### T-38 — A `CompScanner` find that generates nothing still resets the guaranteed-find timer

`RimWorld.CompScanner.Used` consumes the accumulator on the strength of the
eligibility roll alone:

```
daysWorkingSinceLastFinding += lastUserSpeed / 60000f;
if (TickDoesFind(lastUserSpeed))
{
    DoFind(worker);
    daysWorkingSinceLastFinding = 0f;
}
```

`TickDoesFind` tests an MTB roll or `daysWorkingSinceLastFinding >=
Props.scanFindGuaranteedDays`, and knows nothing about whether a find can produce
anything. `DoFind` is `void` and cannot report failure.
`CompLongRangeMineralScanner.DoFind` opens on
`QuestScriptDefOf.LongRangeMineralScannerLump.CanRun(slate, parent.Map)` and simply
returns when that declines — but the caller has already zeroed the counter. The
player sees `ScanningProgressToGuaranteedFind` snap back to 0%, gets no quest and no
letter, and is told nothing. Every day of scanner work since the last find is spent
on a find that never happened.

Vanilla's own counter-pattern is the shape to copy:
`QuestPart_SubquestGenerator_ArchonexusVictory.GetNextSubquestDef` runs `CanRun`
first and returns null, and `QuestPart_SubquestGenerator.TryGenerateSubquest` then
returns false having consumed nothing. **Test eligibility before consuming the
accumulator, never after** — any Archinity scanner-shaped clock included.

*[#57](https://github.com/cjd721/Rimworld-Archinity/issues/57). 1.6.4871.*

### T-41 — A duplicate `analysisID` silently merges two Exemplar gates

`CompProperties_CompAnalyzableUnlockResearch.analysisID` is a bare `public int`,
hand-picked at the def, with **no uniqueness check anywhere**: the properties class
overrides no `ConfigErrors`, and nothing in the load path inspects the value.
`AnalysisManager` keys progress on that int alone —
`Dictionary<int, AnalysisDetails> analysisDetails` — so two ThingDefs sharing an ID
share one entry, and completing either satisfies both
`ResearchProjectDef.requiredAnalyzed` gates. It is worse than a shared counter:
`CompAnalyzable.PostSpawnSetup` calls `AddAnalysisTask` only when
`!HasAnalysisWithID(AnalysisID)`, so the second def's `analysisRequiredRange` is
never rolled at all — it inherits whatever the first item happened to draw.

**Medieval Overhaul ships two live collisions today**, in
`3219596926/1.6/Mods/Biotech/Patches/Schematics.xml`: `355904050` on both
`DankPyon_Schematic_NoblePolearms` and `DankPyon_Schematic_Crossbow`, and
`355904058` on both `DankPyon_Schematic_AdvancedCooking` and
`DankPyon_Schematic_BallistaRepeater`. Studying the polearm schematic unlocks
crossbows, and nothing says so.

The whole bin carries **26 distinct IDs** — three of them vanilla Biotech, all
nine digits — and the lowest in the corpus is **`7`** (Mechanoids: Total Warfare,
`TW_ArmorBlitzWarfare`), with `520`, `521` and `996` behind it. Low hand-picked
numbers are a live hazard, not a theoretical one. **Archinity IDs must come from a
reserved block** — high, contiguous, allocated in one place and recorded there —
never invented at the def.

*[#67](https://github.com/cjd721/Rimworld-Archinity/issues/67). 1.6.4871; Medieval Overhaul 1.6.*

### T-46 — Substructure past `SubstructureSupport` builds fine and is dropped on launch

`Building_GravEngine.UpdateSubstructureIfNeeded` computes the flying set as
`GravshipUtility.GetConnectedSubstructure(this, validSubstructure,
(int)GetStatValue(StatDefOf.SubstructureSupport))`, and that method is a
`Map.floodFiller.FloodFill(engine.Position, …, maxCells)`. **The cap is a flood-fill
limit, not a placement check.** Cell 2,001 places, builds, walks and holds buildings
exactly like cell 2,000; it is simply never added to `validSubstructure`.
`GravshipUtility.GenerateGravship` then reads `engine.ValidSubstructure`, and
`Gravship.AddThing` requires *every* cell of a thing's `OccupiedRect` to be in it.
The overflow cells and everything standing on them stay behind, with no message, no
alert and no confirmation prompt.

`Verse.FloodFiller` is a BFS queue, so which cells overflow is distance order from
the engine — **the outermost rooms are the ones that vanish**. The only signal is
the `ConnectedSubstructure: N / M` line in `Building_GravEngine.GetInspectString`,
and it is a number to look at, not a warning to receive: `AllConnectedSubstructure`
is computed with `int.MaxValue`, so `N` keeps climbing past `M` in silence.

Watch `AllConnectedSubstructure.Count` against
`GetStatValue(StatDefOf.SubstructureSupport)` yourself. Recovery after the fact is
flying back to the old map — and nothing at all if that map was abandoned.

*[#71](https://github.com/cjd721/Rimworld-Archinity/issues/71). 1.6.4871.*

### T-47 — Only five stuffs are airtight; a stone, wood or obsidian room never pressurises

`Verse.Building.IsAirtight` is `def.building.isAirtight || (def.building
.isStuffableAirtight && Stuff.stuffProps.isAirtight)`. `Wall` and its kin set
`isStuffableAirtight`, so the stuff decides — and across Core and all four DLC only
**Steel, Plasteel, Silver, Gold and Uranium** set `stuffProps.isAirtight`. Stone
blocks, `WoodLog`, `Jade` and every fabric do not. A room whose boundary is not
airtight does not hold against space: it equalises, and pawns inside take
`VacuumExposure` with no error and no red text.

**`VacuumUtility.IsRoomAirtight` is not the test that decides that.** Breathability runs
`Room.Vacuum` ← `Room.ExposedToSpace` ← `District.ExposedVacuumCount`, and that count
asks exactly two
things of a cell: is it unroofed, or does its terrain set `exposesToVacuum`.
`IsRoomAirtight` is the **other** question — its inner `IsRoomDirectlyOpenToOutside`
additionally demands `terrainGrid.FoundationAt(cell).IsSubstructure` on every cell, so
it is false for **every orbital-platform room**, and those rooms are pressurised and
breathable regardless. Read `IsRoomAirtight` as the gravship-hull question and never as
*"will they breathe"*. What the two share is the wall half, which is what this entry is
about.

**`Obsidian` is the nastiest case.** Odyssey's
`Odyssey/Defs/ThingDefs_Items/Items_Resource_Stuff.xml` gives it
`stuffProps/categories` of `Stony` **and** `Metallic` — and no `isAirtight`. It
reads as a metal wall in the build menu, is available on exactly the volcanic maps
where a player is short of steel, and leaks.

Build pressurised hulls from `GravshipHull`, which sets `building.isAirtight`
outright in `Odyssey/Defs/ThingDefs_Buildings/Buildings_Gravship.xml` and so does not
care about stuff, or from steel/plasteel `Wall`. Never from local stone. The one
place the game will tell you is the `Stat_Airtight` row in the info card, which
nobody opens before laying a wall.

*[#71](https://github.com/cjd721/Rimworld-Archinity/issues/71);
[#66](https://github.com/cjd721/Rimworld-Archinity/issues/66) for the separation of the
two pressurisation rules, which `docs/engine/gravship-and-substructure.md`
§ *Pressurisation* had filed under one heading.
`Verse.Building.IsAirtight`, `RimWorld.Room.ExposedToSpace`,
`RimWorld.District.ExposedVacuumCount`, `RimWorld.VacuumUtility.IsRoomAirtight` /
`.IsRoomDirectlyOpenToOutside`. 1.6.4871.*

### T-56 — `Thing.SmeltProducts` throws away its `efficiency` argument, and the info card advertises it anyway

`Verse.Thing.SmeltProducts(float efficiency)` takes the argument and **never reads it**.
The multiplier in the body is a literal `0.25f`. Its two siblings on the same class,
`ButcherProducts` and `StoneBlockProducts`, both honour the identical argument — which is
exactly what makes the field read as live.

`GenRecipe.MakeRecipeProducts` computes `efficiency` from `RecipeDef.efficiencyStat` and
`workTableEfficiencyStat` and passes it in, where it is discarded. So a bench augment
expressed as `workTableEfficiencyStat`, or a recipe's own `efficiencyStat`, does **nothing
at all** on any recipe whose `specialProducts` contains `Smelted`. No log line, no config
error.

**The display is worse than the silence.** `RecipeDef.SpecialDisplayStats` emits the
`EfficiencyStat` line whenever `efficiencyStat != null`, so the info card prints a
multiplier that has no effect — the one surface a player would check asserts the opposite
of the truth. There is therefore no honest way to *show* the return fraction at all; it
goes in the recipe `<description>` as prose.

**The only XML lever on the fraction is repetition.** `MakeRecipeProducts` loops
`for each specialProducts entry { for each ingredient { … } }`, and `specialProducts` is a
`List<SpecialProductType>`, not a set — so `<li>Smelted</li>` twice is 50%, three times
75%, and nothing between. Ushanka's Glittertech Expansion ships the same idiom on the
`Butchery` case (`USH_DisassembleCorpseMechanoid`, commented *"doubled products"*). Any
other fraction, or any dependence on hit points or quality, needs a Harmony postfix over
the returned `IEnumerable<Thing>`.

*[#82](https://github.com/cjd721/Rimworld-Archinity/issues/82), `docs/specs/ITEMS.md`.
`Verse.Thing.SmeltProducts` / `.ButcherProducts` / `.StoneBlockProducts`,
`RimWorld.GenRecipe.MakeRecipeProducts`, `RimWorld.RecipeDef.SpecialDisplayStats`.
1.6.4871.*

### T-57 — `RecipeDef.smeltingWorkAmount` is honoured by reference identity, on one def

`RecipeDef.WorkAmountTotal` reads it behind
`if (this == RecipeDefOf.SmeltOrDestroyThing && thing.Smeltable)` — a **reference-identity
test against a single def**, not a null check on the field. Set `smeltingWorkAmount` on any
recipe of ours and it is ignored: no error, no config warning, and a work amount that
quietly falls back to `workAmount`. Same family as T-56, and the same shape — a field that
exists on the type for one caller's benefit.

*[#82](https://github.com/cjd721/Rimworld-Archinity/issues/82).
`RimWorld.RecipeDef.WorkAmountTotal`, `RimWorld.RecipeDefOf.SmeltOrDestroyThing`.
1.6.4871.*

### T-58 — Any recipe with `specialProducts` silently loses "Do until you have X"

`RimWorld.RecipeWorkerCounter.CanCountProducts` returns `false` whenever
`recipe.specialProducts != null`. The consequence is not a disabled control or a refusal
message — the **TargetCount repeat mode is simply omitted from the bill's repeat-mode
button**, so a bill that ought to offer *"Do until you have 500 cloth"* offers Forever and
Repeat-N and nothing else. Nothing says why.

Vanilla hit this itself and left the evidence in its own XML: `ExtractMetalFromSlag`
carries a commented-out `<specialProducts><li>Smelted</li></specialProducts>` above the
note *"Switched to standard products so we can do 'do until you have X'"*. **That escape is
closed to us** — a fixed `products` list is the intermediate noun `docs/PLOT.md` forbids for
a reclaim recipe.

**The supported fix is one XML field.** `RecipeDef.workerCounterClass` is a plain `Type`
field, and vanilla ships `RimWorld.RecipeWorkerCounter_MakeStoneBlocks`, which overrides
`CanCountProducts` to `true` and counts a whole `ThingCategoryDef` — the exact shape a
reclaim recipe wants. ~30 lines of C# in the assembly we already ship, and optional: without
it the bill is Forever / Repeat-N.

*[#82](https://github.com/cjd721/Rimworld-Archinity/issues/82), `docs/specs/ITEMS.md`.
`RimWorld.RecipeWorkerCounter.CanCountProducts`,
`RimWorld.RecipeWorkerCounter_MakeStoneBlocks`, `RecipeDef.workerCounterClass`. 1.6.4871.*

### T-59 — A studied `StudiableBuilding` leaks forever into a scribed `HashSet<Thing>`

`VEF.Buildings.StudiableBuilding.Study(Pawn)` ends in `DeSpawn(DestroyMode.Vanish)`, and
only the `Destroy` and `Kill` overrides call `RemoveStudiablesFromMap`. `Thing.Destroy`
calls `DeSpawn`, never the reverse — so a building that is **studied**, the one path the
feature exists for, is never removed from
`MapComponent_InteractableBuildingsInMap.studiables_InMap`.

That set is scribed, and scribed as
`Scribe_Collections.Look(ref studiables_InMap, "studiables_InMap", LookMode.Reference)`. It
therefore accumulates, in the save, references to things no `ThingOwner` holds:
`WorkGiver_StudyBuilding.ShouldSkip` stops short-circuiting on that map, and the set grows
for the life of the run. No error, no log line, and nothing a player can see.

**VQE Ancients ships the bug**: `Building_BroadcastingStation` inherits it by calling
`base.Study(pawn)`. Any subclass of ours inherits it the same way. *Fix:* call
`InteractablesMapComp?.RemoveStudiablesFromMap(this)` explicitly in the override, before
`base.Study`.

*[#80](https://github.com/cjd721/Rimworld-Archinity/issues/80), `docs/specs/CHARTING.md`.
`VEF.Buildings.StudiableBuilding.Study` and
`VEF.Buildings.MapComponent_InteractableBuildingsInMap` from `VEF.dll`
(`2023507013/1.6/Assemblies/`); `VanillaQuestsExpandedAncients.Building_BroadcastingStation`
(`3618306875/1.6/Assemblies/`). 1.6.4871.*

### T-60 — `StudiableBuilding.Study` sends no quest signal, where its sibling sends both

`VEF.Buildings.LootableBuilding.Open()` sends **both** `Find.SignalManager.SendSignal` and
`QuestUtility.SendQuestTargetSignals`. `StudiableBuilding.Study(Pawn)` sends **neither** —
its whole body is spawn `buildingLeft`, play the sound, optionally start
`Inspired_Creativity`, `DeSpawn`. A quest beat authored with `<inSignal>` against a
studiable therefore never fires, and a quest gated on one never completes: no error, no
warning, no log line.

This is the `LootableBuilding` / `LootableBuilding_Custom` split extended to a third class,
and `docs/data/PARTS-BIN.md` §7.3 records it for only two of the three.

**Copy the signal *pair*, not the precedent.** VQE Ancients' `Building_BroadcastingStation`
overrides `Study` to send `QuestUtility.SendQuestTargetSignals(site.questTags, …)` and
stops there — so a plain `Find.SignalManager` listener still misses it. Send both, as
`LootableBuilding.Open` does.

*[#80](https://github.com/cjd721/Rimworld-Archinity/issues/80), `docs/specs/CHARTING.md`.
`VEF.Buildings.StudiableBuilding.Study`, `VEF.Buildings.LootableBuilding.Open` from
`VEF.dll` (`2023507013/1.6/Assemblies/`). 1.6.4871.*

### T-62 — A study designation on a null- or hostile-faction building is accepted and never worked

`VEF.Buildings.WorkGiver_StudyBuilding.HasJobOnThing` returns **false** when
`t.Faction != pawn.Faction`. Nothing upstream of it agrees: `StudiableBuilding.GetGizmos`
offers the designation button regardless of faction, `AddStudiablesToMap` accepts the
thing, the pulsing `MetaOverlay` appears over it, and the entry is written into the scribed
`studiables_InMap` set.

So the player designates the object, sees every affordance confirm it, and **no colonist
ever walks to it**. There is no refusal message, no disabled button and no log line — the
work simply never appears in the queue, which reads as ordinary job-priority behaviour.

**This is the common case for us, not the edge case.** Charting-site objects — a mural on
an abandoned platform, a terminal in an ancient complex — carry a null faction or a hostile
one almost by definition, which is the entire population of things a lore record would be
attached to. Anything of ours deriving from `StudiableBuilding` needs its own `WorkGiver`,
or a postfix on `HasJobOnThing`. The right-click path (`GetFloatMenuOptions` →
`TryTakeOrderedJob`) is unaffected and works, which makes the gizmo path's silence harder
to spot rather than easier.

*[#80](https://github.com/cjd721/Rimworld-Archinity/issues/80), found in the resolution
audit. `VEF.Buildings.WorkGiver_StudyBuilding.HasJobOnThing`,
`VEF.Buildings.StudiableBuilding.GetGizmos` from `VEF.dll`
(`2023507013/1.6/Assemblies/`). 1.6.4871.*

### T-93 — `Window_AndroidCreation` rebuilds its ingredient list on every gene toggle

`VREAndroids.Window_AndroidCreation.OnGenesChanged()` assigns `requiredItems` as a **fresh
hardcoded `List<ThingDefCount>`** — `VREA_PersonaSubcore` ×1, `Plasteel` ×125, `Uranium` ×30,
`ComponentSpacer` ×7. There is no `RecipeDef`, no def field and no mod extension behind an android's
material cost; the numbers exist only as a C# literal.

`VREAndroids.Window_CreateAndroidBase` calls `OnGenesChanged()` **from its constructor and from the
gene click handler**, so the list is discarded and rebuilt in full every time the player adds or
removes a single gene. `Window_AndroidCreation.AcceptInner()` then copies whatever the last toggle
produced onto `VREAndroids.Building_AndroidCreationStation.requiredItems`, which is scribed.

**The failure:** a Harmony patch that writes `requiredItems` at any other seam — on window open, on
`AcceptInner`, on the station — is silently overwritten by the player's next gene click, and the
overwrite is invisible because the cost row redraws from the same field
(`AndroidStatsTable.Draw(…, requiredItems)`). The patch appears to work right up until the player
touches a gene, and the wrong list is the one that gets saved.

**The fix:** postfix `OnGenesChanged` itself and append there. Every other seam is downstream of a
reassignment. This binds any per-android ingredient price we put on android manufacture — see
`docs/specs/ANDROIDS.md` § *5. The Exemplar gate*, Layer 2.

*[#78](https://github.com/cjd721/Rimworld-Archinity/issues/78), `docs/specs/ANDROIDS.md`.
`VREAndroids.Window_AndroidCreation.OnGenesChanged` / `.AcceptInner`,
`VREAndroids.Window_CreateAndroidBase`, `VREAndroids.Building_AndroidCreationStation.requiredItems`,
`VREAndroids.AndroidStatsTable.Draw` from `VREAndroids.dll`
(`2975771801/1.6/Assemblies/` — the mod ships **1.4-only source**, so this is decompiled from the
loaded assembly). 1.6.4871.*

### T-94 — Mech gestation resolves its output pawnkind by reverse lookup, and a duplicate is silent

`RimWorld.Bill_ProductionMech.CreateProducts` finds the pawn to build with
`DefDatabase<PawnKindDef>.AllDefs.Where(pk => pk.race == recipe.ProducedThingDef).First()`.
**No def field names the resulting pawnkind** — `RecipeDef` has none, and
`Verse.RecipeDef.ProducedThingDef` is just `products[0].thingDef` (null when `specialProducts != null`
or `products.Count != 1`). The recipe names a *race* `ThingDef`; the *kind* is inferred.

**The failure:** if two `PawnKindDef`s declare the same `<race>`, `.First()` returns whichever
`DefDatabase` ordering happens to yield first. That is load-order dependent, not modder-controllable,
and produces no warning — the gestator completes normally and hands back a pawn of the wrong kind,
with the wrong combat power, apparel and generation rules. `Verse.RecipeDef.ConfigErrors()` checks
only `workerClass == null` and never validates the product at all. Vanilla never trips this because
Biotech ships exactly one kind per mech race (`PawnKindDef Mech_Militor` ↔ `ThingDef Mech_Militor`).

**The fix:** one `PawnKindDef` per gestated race. If a variant is needed for raids or quests, give it
its own race `ThingDef` rather than a second kind on the shared one.

Not traps, and recorded here so they are not filed as such — both are **loud**: zero matching kinds
throws `InvalidOperationException` from `.First()`, and a `gestationCycles` recipe placed on a bench
that is not a `Building_MechGestator` throws `InvalidCastException` from the unguarded cast in
`RimWorld.Bill_Mech.Gestator`.

*[#78](https://github.com/cjd721/Rimworld-Archinity/issues/78), found while pricing the
non-VRE alternative; `docs/specs/ANDROIDS.md` § *Available mechanisms*.
`RimWorld.Bill_ProductionMech.CreateProducts`, `RimWorld.Bill_Mech.Gestator`,
`Verse.RecipeDef.ProducedThingDef` / `.ConfigErrors`, `RimWorld.BillUtility.MakeNewBill`. 1.6.4871.*

### T-141 — A faction-dialogue option appended for the Industrial comms console also appears at Medieval Overhaul's messenger table

`FactionDialogMaker.FactionDialogFor(negotiator, faction)` carries **no console**, and Medieval
Overhaul's messenger table (`DankPyon_ScribeTable`, research `DankPyon_CarrierBirds`, techLevel
Medieval) is `MedievalOverhaul.Building_ScribeTable : Building_CommsConsole`. Its float menu lists
every visible non-temporary faction through vanilla `Faction.CommFloatMenuOption`, which ends at
`Faction.TryOpenComms(Pawn)` → `FactionDialogFor`. So an option postfixed onto the faction
dialogue for the radio beat — and vanilla's own trader and military-aid requests — also appears
at a Medieval building, an era early. Nothing errors; the option simply appears.

**Fix:** gate era-sensitive options on research or the era clock with `DiaOption.Disable`, never
on the building type. Live only if Medieval Overhaul ships
([#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)).

*[#154](https://github.com/cjd721/Rimworld-Archinity/issues/154),
`docs/specs/WORLD-INFRASTRUCTURE.md` § *The player's verb on a route — contribute*.
`3219596926/1.6/Assemblies/MedievalOverhaul.dll` `MedievalOverhaul.Building_ScribeTable`;
`RimWorld.Faction.TryOpenComms`, `RimWorld.FactionDialogMaker.FactionDialogFor`
(`Assembly-CSharp.dll`). See `docs/engine/determinism.md` § *MP serialises the comms-console
dialogue*.*

### T-156 — BWM's "paste settings" keeps the target's material filter whenever the two recipes' fixed filters differ

Better Workbench Management's *Paste all settings (except output product)* runs
`BillCopyPaste.DoPasteInto(Bill_Production)` → `ExtendedBillDataStorage.MirrorBills(source,
target, preserveTargetProduct: true)`. It copies `ingredientFilter` only if `DoFiltersMatch` finds
the two recipes' `fixedIngredientFilter`s def-identical. Every other field pastes. Plate armour
(`Metallic`+`Woody`) → simple helmet (`Metallic`) therefore loses a *"steel only"* restriction,
**with no message** — the player sees every other setting arrive and has no reason to check the
materials.

The same strict rule is what stops BWM producing an empty filter on a disjoint pair (plate →
parka), and it means the material **does** paste whenever the two fixed filters match.
`docs/requirements/COLONY.md` has a pasted configuration never carry the material, so BWM's paste
carries it on matching recipes, which the requirement forbids; a paste that meets the
requirement leaves `ingredientFilter` out entirely (`DEFAULTS.md` § *A bill's configuration*,
Route C).

*[#157](https://github.com/cjd721/Rimworld-Archinity/issues/157), `docs/specs/DEFAULTS.md` § *A
bill's configuration, pasted onto another bill*. `935982361/1.6/Assemblies/ImprovedWorkbenches.dll`
(`ImprovedWorkbenches.ExtendedBillDataStorage.MirrorBills`, `DoFiltersMatch`);
`Data/Core/Defs/ThingDefs_Misc/Apparel_Various.xml`, `Apparel_Headgear.xml`. [V] by reading.*

### T-163 — An android-category gene we author is installed on every player-built android, or offered to the player, depending on one field

VRE – Android adopts **any** `GeneDef` whose `displayCategory` is `VREA_Hardware` or
`VREA_Subroutine` into `Utils.allAndroidGenes` (`GeneDefGenerator_ImpliedGeneDefs_Patch.Postfix`).
That makes it look like the natural home for a gene only one faction's androids carry. What happens
next depends on `isCoreComponent`, and neither outcome is announced:

- **`isCoreComponent true`** (the default for anything inheriting `VREA_HardwareBase`): the
  `Window_CreateAndroidBase` constructor seeds `selectedGenes` with every android gene that
  `CanBeRemovedFromAndroid()` refuses, and the toggle will not un-select it.
  `Building_AndroidCreationStation.FinishAndroidProject` installs that list. So **every android the
  player builds carries the gene**. A "this is a Glitterite" marker authored this way turns every
  player-built android into a Glitterite for any code keyed on it.
- **`isCoreComponent false`** (the `VREA_SubroutineBase` default): the gene is an optional
  subroutine in the creation window, which the player can add to their own androids. It is also
  removable at the behaviorist station from any android the station accepts, prisoners included.
- A gene in any other category is invisible to both windows. `Window_AndroidModification` seeds
  only from `IsAndroidGene`, and `FinishAndroidProject` strips and reinstalls only
  `allAndroidGenes`. The station then can neither show nor remove it.

**Remedy.** Choose the category for who should be able to see and remove the gene. If it must be
android-category but not player-selectable, postfix `Window_CreateAndroidBase.GeneValidator` (a
public virtual that filters the drawn list) to hide it. That works for a **non-core** gene only: a
core gene reaches `selectedGenes` through the constructor, not through `GeneValidator`, so hiding it
does not stop the install. `docs/specs/ANDROIDS.md` § *Jailbreaking a
captured Glitterite*.

*[#143](https://github.com/cjd721/Rimworld-Archinity/issues/143). `VREAndroids.Window_CreateAndroidBase`
(constructor, `GeneValidator`), `.Window_AndroidModification`, `.Utils.CanBeRemovedFromAndroid`,
`.Building_AndroidCreationStation.FinishAndroidProject`,
`.Building_AndroidBehavioristStation.FinishAndroidProject`, `.GeneDefGenerator_ImpliedGeneDefs_Patch`;
`2975771801/1.6/Defs/GeneDefs/GeneDefs.xml`. [V]*

### T-164 — Every surgery on an android is Crafting work and cannot fail

VRE – Android rewrites surgery for any `IsAndroid()` patient, with no message:

- `HealthCardUtility_CreateSurgeryBill_Patch` swaps the bill's recipe for
  `RecipeDef.RecipeForAndroid()`, a **clone** with `workSkill Crafting`. Any `Medicine` skill
  requirement becomes `Crafting`, and the work speed stat becomes `ButcheryMechanoidSpeed`
  (unless the recipe already used Crafting).
- `WorkGiver_DoBill_ThingIsUsableBillGiver_Patch` removes android patients from vanilla's medical
  work-giver and gives them to `VREA_DoBillsAndroidOperation` (`workType Crafting`). **Doctors never
  operate on androids; crafters do.**
- `Recipe_Surgery_CheckSurgeryFail_Patch` is an `int.MaxValue` prefix that skips
  `Recipe_Surgery.CheckSurgeryFail` for an android patient, and the default result means "did not
  fail". `surgerySuccessChanceFactor`, skill, medicine and the operating bed do nothing, and no
  android surgery can fail, botch or kill.

A beat written as "a doctor opens it up, and it might go wrong" is impossible as shipped on both
counts.

**Remedy.** Author android surgeries with `workSkill Crafting` so no clone is made. If an operation
must be able to fail, roll inside its own `ApplyOnPawn`.

*[#143](https://github.com/cjd721/Rimworld-Archinity/issues/143), `docs/specs/ANDROIDS.md` §
*Jailbreaking a captured Glitterite*. `VREAndroids.Utils.RecipeForAndroid`,
`.HealthCardUtility_CreateSurgeryBill_Patch`, `.WorkGiver_DoBill_ThingIsUsableBillGiver_Patch`,
`.Recipe_Surgery_CheckSurgeryFail_Patch`; `2975771801/1.6/Defs/WorkGiverDefs/WorkGivers.xml`. [V]*

---

## Rituals and titles

### T-27 — `MeditationFocusDef` gates are backstory gates, and a failed gate looks like nothing

`Natural` — the anima tree's only focus type — requires a **Childhood** backstory in
category `Tribal`, `AdultTribal` or `ChildTribal`. A pawn without one is simply
never offered the linking ritual: no error, no message, no disabled button. The
founders' backstories are therefore load-bearing on the Neolithic psychic on-ramp.

No vanilla focus type is ungated. `Morbid` is listed by seven Core traits (Bloodlust,
Psychopath, Cannibal, Masochist, Jealous, Undergrounder, TorturedArtist), `Minimal` by
Ascetic, `Flame` by Pyromaniac. A type is open to all only if no `TraitDef` and no
`HediffDef` lists it (`MeditationFocusTypeAvailabilityCache.PawnCanUseInt`). The altar
defines no focus. **[V]**

*[#21](https://github.com/cjd721/Rimworld-Archinity/issues/21); [#49](https://github.com/cjd721/Rimworld-Archinity/issues/49). 1.6.4871; `Data/Core/Defs/TraitDefs/Traits_Singular.xml`.*

### T-28 — `RoyalTitleDef.Awardable` is `favorCost > 0`, and a title without one is invisible

`RimWorld.RoyalTitleDef.Awardable => favorCost > 0;` — a computed property, with no
`awardable` field in any XML to set. Exactly seven of the thirteen vanilla
`RoyalTitleDef`s carry a `favorCost` (`Freeholder` 1 through `Count` 20), and those
are exactly the seven player-attainable titles.

A title without a `favorCost` is therefore a silent no-op on **every** vanilla award
path, each failing by a different quiet route:

- `FactionDef.RoyalTitlesAwardableInSeniorityOrderForReading` filters on
  `item.Awardable`, so the title is not in the ladder at all — and
  `FactionDef.HasRoyalTitles` counts that same list.
- `RoyalTitleDefExt.GetNextTitle` returns null when `IndexOf(currentTitle) == -1`,
  so a pawn holding a non-awardable title can never be promoted from it.
- `Pawn_RoyaltyTracker.UpdateRoyalTitle` returns early on
  `currentTitle != null && !currentTitle.Awardable` — favour accrues and never
  converts.
- `ApplyRewardsForTitle` is guarded by `newTitle.Awardable`, and `ReduceTitle`
  returns early on `!currentTitle.Awardable`.

Nothing logs, nothing warns, and the title is simply absent from every list a player
can see.

Our tiers of godhood are conferred by calling `Pawn_RoyaltyTracker.SetTitle`
directly from a ritual outcome worker. **`SetTitle` does not consult `Awardable`**,
which is why they work. A later attempt to award one of them through a normal route
— a quest reward, a favour purchase, an inheritance — silently does nothing, so do
not add one.

*[#53](https://github.com/cjd721/Rimworld-Archinity/issues/53). 1.6.4871.*

### T-34 — Editing the `comps` list on a `HediffDef` silently drops the comp's saved fields

`Verse.HediffWithComps.ExposeData` calls `InitializeComps()` on `LoadingVars` and
then loops `comps[i].CompExposeData()` **into one flat node, with no per-comp
wrapper**. `InitializeComps` rebuilds the list from `def.comps` alone, so what the
save holds is matched to the def's *current* comps by Scribe key and nothing else.
Remove a comp from the def and its keys are never read again: the data is gone, and
re-adding the comp later reads defaults. Two comps sharing a key clobber each other
by the same mechanism.

Nothing reports it. `HediffUtility.TryGetComp<T>` returns null for a comp that is not
in the list, so an accessor shaped like
`…GetFirstHediffOfDef(Archinity_FounderRecord)?.TryGetComp<CompFounderRecord>()?.titleClaimed
== true` reads **false**, and the founder appears never to have claimed anything —
no exception, no missing-node warning, no clue in the log.

Prevention only; a save already written cannot be recovered from. Once
`Archinity_FounderRecord` ships, **never edit its `comps` list**. Add new state as
new fields on the existing comp, each with its own new Scribe key, and never reuse a
retired one.

*[#50](https://github.com/cjd721/Rimworld-Archinity/issues/50). 1.6.4871.*

### T-35 — The Permits tab is gated on the Empire existing, and the switch that would fix it is inside the gate

`Verse.Dialog_InfoCard` adds the Permits tab only when
`PermitsCardUtility.selectedFaction != null`. That static is assigned in exactly two
places in the whole assembly. One is `RimWorld.StatsReportUtility.Reset`:

```
PermitsCardUtility.selectedFaction = ((ModLister.RoyaltyInstalled && Current.ProgramState == ProgramState.Playing) ? Faction.OfEmpire : null);
```

The other is the faction switcher's float menu — drawn by
`PermitsCardUtility.DrawRecordsCard`, which is to say **inside the card the tab
gates**. Remove the Empire from the world and `Faction.OfEmpire` is null, the seed is
null, the tab is never added for *any* faction, and the one control that could set
the field lives behind a tab that cannot be opened. A circular gate, with no error,
no empty tab and no disabled button to hover.

A custom faction can therefore ship a complete, correct `RoyalTitlePermitDef` ladder
that no player will ever see. Reaching it needs code — a Harmony patch seeding
`selectedFaction`, or our own window — and T-07 rules out the obvious alternative:
the roster is not repairable after worldgen, so "add the Empire later" is not a fix.

**Under the campaign's Church build it cannot fire.** `docs/specs/RELIGION.md` § *The build —
Exaltation* transforms Royalty's `Empire` in place and renames nothing, so `Faction.OfEmpire`
always resolves and the seed is never null. It returns only through the doors that null the
singleton: a renamed defName, World Tech Level stripping the Empire at worldgen (**T-54**), or —
delayed — a `Faction.def` swap (**T-98**). It still binds any *other* faction's permit ladder.

*[#53](https://github.com/cjd721/Rimworld-Archinity/issues/53); Church note from its
re-resolution, 2026-09-15. 1.6.4871.*

### T-63 — Overriding `Gene.Label` reaches the tooltip header and nowhere else

`Gene.Label` and `Gene.LabelCap` are `virtual`, which reads as the supported way to give a
per-instance gene a per-instance name. It is not.
`RimWorld.GeneUIUtility.DrawGene(Gene, …)` uses the instance's `LabelCap` for the tooltip
**title** only. Everything a player actually looks at is typed on the **def**: the tooltip
body is `gene.def.DescriptionFull`, the tile itself is drawn by
`DrawGeneBasics(GeneDef, …)`, and clicking it opens `new Dialog_InfoCard(gene.def)`. An
overridden label therefore appears in exactly one place, on hover, and nowhere in the gene
tab, the info card or any list — with no error.

**VRE Starjack ships a prefix on the private `GeneUIUtility.DrawSection` for exactly this
reason**: it pulls its own genes out of the list and redraws them itself. That patch exists
because the virtual property does not carry.

It binds any gene whose per-instance contents differ from its def's: the only free surface for
that difference is the hover title, and every other readout is a patch we write or the def's
generic text. The altar's final rite now grants the shipped `VRE_Transcendent` gene, with no
per-founder instance (`docs/specs/ALTAR.md` § *The final rite*); the per-founder Transcendent
Archogene this trap was found on is archived in `docs/archive/altar-transcendent-gene-build.md`.

*[#59](https://github.com/cjd721/Rimworld-Archinity/issues/59), `docs/archive/altar-transcendent-gene-build.md`.
`RimWorld.GeneUIUtility.DrawGene` / `.DrawGeneBasics` / `.DrawSection`, `Verse.Gene.Label`;
`VanillaRacesExpandedStarjack.dll`. 1.6.4871.*

### T-64 — A `GeneVectorExtension` with `gene: null` spends the charge and grants nothing

**Ours, and shipping.** `Archinity.Building_Altar.PerformRite` guards the grant with
`if (ext.gene != null)` and then — outside that guard — **unconditionally destroys the
vector, debits the charge and posts `Archinity_AltarRiteSucceeded`**, rendering the gene
name as `ext.gene?.LabelCap ?? "?"`. A vector whose extension names no gene therefore
consumes a rite, consumes the item, grants nothing, and tells the player it worked. The
message reads `"?"` where the gene name would be, which is the only evidence anything went
wrong.

`gene: null` is not a malformed def. It is documented in our own source as *"Null means the
lottery"* — and the lottery has no draw code: `GenePoolDef.Available()` and `EntryFor()`
have zero call sites, and `categoryBias` and `extraOptions` are computed in
`AltarModifiers.For` and never read. The data model exists, the draw does not, and the gap
between them is a success message.

**Remedy.** `gene: null` is the lottery's own marker, and the draw that consumes it is now
specified: `docs/specs/ALTAR.md` § *The build — the repeatable lottery* routes `PerformRite`'s
`ext.gene == null` arm into the offer instead of letting it fall through to the success
message, which closes the silent no-op by giving the branch the behaviour its comment always
claimed. **Until that lands**, an extension with a null `gene` must be refused loudly at the
rite rather than honoured quietly.

*[#59](https://github.com/cjd721/Rimworld-Archinity/issues/59), remedy replaced 2026-09-12
from [#110](https://github.com/cjd721/Rimworld-Archinity/issues/110), which owns the lottery
draw — the "unowned" note this entry previously carried is superseded; the trap statement
itself is unchanged and still true of shipping code.
`Archinity.Building_Altar.PerformRite`, `Archinity.GeneVectorExtension`,
`Archinity.GenePoolDef` in `ArchinityAltar.dll`. 1.6.4871.*

---

### T-104 — `CompStudiable` progress does not survive stacking

`RimWorld.CompStudiable` keeps its study progress on the comp: `studyPoints` (saved as
`studiedAmount`), `studyInteractions` and `lastStudiedTick`. It overrides **none** of
`ThingComp.AllowStackWith`, `PreAbsorbStack` or `PostSplitOff`, and `AllowStackWith`
defaults to `true`. So on any stackable def carrying the comp:

- **Merging two stacks.** `ThingWithComps.TryAbsorbStack` gives each comp only a
  `PreAbsorbStack` call, which `CompStudiable` ignores. The absorbing stack keeps its own
  progress, and the absorbed stack's progress disappears with it.
- **Splitting a stack.** `ThingWithComps.SplitOff` makes the new piece through
  `ThingMaker.MakeThing`, then calls `PostSplitOff`, which `CompStudiable` ignores. The
  split piece starts at 0.

Nothing is logged, and the inspect pane simply shows the surviving number. A payout
keyed to study thresholds (`IThingStudied.OnStudied`) can therefore lose progress the
player already paid for in pawn-hours. It can also re-pay a threshold, if the record of
what was paid does not travel with the progress.

**Fix:** give every studiable item `stackLimit 1`, or override all three members on a
subclass.

*[#115](https://github.com/cjd721/Rimworld-Archinity/issues/115). 1.6.4871.*

---

### T-105 — A believer count on a `Precept_RoleMulti` def is inert, and the tooltip still advertises it

`Precept_RoleMulti.Init` sets `active = true`, and `Precept_RoleMulti.RecacheActivity` only
drops holders failing `ValidatePawn`. Neither reads `activationBelieverCount` or
`deactivationBelieverCount`. `Precept_Role.GetTip` prints `RoleBelieverCountDesc` whenever
`activationBelieverCount != -1` on a non-leader role. So a multi-holder role authored with
`activationBelieverCount: 3` is assignable with one believer, while its tooltip tells the player
it needs three.

**Remedy.** Leave both counts unset on multi-holder defs, as `PreceptRoleMultiBase` does. Gate a
multi-holder role through a `RoleRequirement`.

*[#114](https://github.com/cjd721/Rimworld-Archinity/issues/114). `RimWorld.Precept_RoleMulti.Init`,
`.RecacheActivity`, `RimWorld.Precept_Role.GetTip` in `Assembly-CSharp.dll`. 1.6.4871.*

---

### T-106 — A `Precept_RoleSingle` with `activationBelieverCount` −1 never activates, and nothing says so

`PreceptDef.activationBelieverCount` defaults to −1, and only `PreceptRoleSingleBase` sets 3.
`Precept_RoleSingle.RecacheActivity` activates only when `def.activationBelieverCount >= 0`, and
`Precept_RoleSingle.Init` does not set `active`. So a single-holder role def that does not
inherit the base is never active:
- The inactive letter needs `active` to have been true, so no letter is sent.
- `SocialCardUtility.DrawPawnRoleSelection` greys the role but prints a believer reason only when
  `activationBelieverCount` exceeds the believer count, so the menu shows no reason.
- The tooltip's believer line is suppressed at −1.

**Remedy.** Inherit `PreceptRoleSingleBase`, or set `activationBelieverCount` ≥ 0 explicitly.
Keep `deactivationBelieverCount` *below* it: at activation ≤ deactivation the role flips off and
on every world tick (loud, see `docs/engine/ideology.md`).

*[#114](https://github.com/cjd721/Rimworld-Archinity/issues/114). `RimWorld.Precept_RoleSingle.RecacheActivity`,
`RimWorld.SocialCardUtility.DrawPawnRoleSelection`, `RimWorld.PreceptDef` in `Assembly-CSharp.dll`. 1.6.4871.*

---

### T-107 — A custom `RoleEffect` subclass does nothing, and the tooltip lists it anyway

`RimWorld.RoleEffect`'s only hooks are `Label`, `CanEquip` (read by
`EquipmentUtility.RolePreventsFromUsing`) and `Notify_Tended`. Every other role effect is
applied by a reader that type-tests a concrete vanilla class:
- `StatWorker` looks for `RoleEffect_PawnStatOffset` / `RoleEffect_PawnStatFactor`;
- `QualityUtility.GenerateQualityCreatedByPawn` looks for `RoleEffect_ProductionQualityOffset`;
- `PawnUtility` looks for `RoleEffect_HuntingRevengeChanceFactor`.

A new subclass is loaded, and its label appears under *Role effects* in `Precept_Role.GetTip`,
but it changes nothing. The corpus ships no `RoleEffect` subclass to copy.

**Remedy.** Express the effect through the vanilla subclasses against an existing `StatDef`, or
ship the reader: a `StatPart` keyed on the holder, as in VIE Memes' `StatPart_Pattisier`, or a
Harmony patch at the consuming site.

*[#114](https://github.com/cjd721/Rimworld-Archinity/issues/114). `RimWorld.RoleEffect`, `RimWorld.StatWorker`,
`RimWorld.QualityUtility`, `RimWorld.Precept_Role.GetTip` in `Assembly-CSharp.dll`. 1.6.4871.*

---

### T-108 — `Ideo.GetRole` returns one role; a second role on the same pawn is held and inert

`Ideo.GetRole(p)` returns the first `Precept_Role` in `RolesListForReading` whose `IsAssigned(p)`
is true. Stat effects, production quality, conversion power, weapon bans, the role menu and
ritual role matching all read it. `Precept_RoleMulti.Assign` and `Precept_RoleSingle.Assign`
do not check whether the pawn already holds another role. Only the role-change ritual unseats
first (`RitualOutcomeEffectWorker_RoleChange.Apply`). So code that seats a pawn in two roles
leaves them listed as a holder of both, while only the first in precept sort order has any
effect.

**Remedy.** Treat one role per pawn as an engine rule. When seating from code, `Unassign` the
pawn's current `GetRole` first, as the ritual does.

*[#114](https://github.com/cjd721/Rimworld-Archinity/issues/114). `RimWorld.Ideo.GetRole`, `RimWorld.Precept_RoleMulti.Assign`,
`RimWorld.RitualOutcomeEffectWorker_RoleChange.Apply` in `Assembly-CSharp.dll`. 1.6.4871.*

---

### T-111 — A pawn's xenotype is not identity

A custom `XenotypeDef` reads like a durable marker for "this pawn is one of ours". Two vanilla
calls rewrite it with no message.

- **`GeneUtility.ReimplantXenogerm(caster, recipient)`** calls
  `recipient.genes.SetXenotype(caster.genes.Xenotype)`. **Every pawn a sanguophage-style reimplanter
  converts carries the caster's xenotype.**
- **`GeneUtility.ImplantXenogermItem(pawn, xenogerm)`** calls `pawn.genes.SetXenotype(Baseliner)`.
  `Pawn_GeneTracker.SetXenotype` runs `ClearXenogenes()` before adding the new xenotype's genes. A
  xenotype with `inheritable false` places its genes as **xenogenes**
  (`AddGene(gene, !xenotype.inheritable)`), so implanting any xenogerm into such a pawn **erases the
  xenotype and every gene that came with it**.
- Anomaly's `GameComponent_PawnDuplicator.Duplicate` copies xenotype, xenogenes and endogenes onto
  the duplicate.

Gene-based markers fail the same way. Vanilla `Sanguophage` already carries `Ageless` and
`Deathless`, so "has these genes" also matches every vanilla sanguophage.

**This bites Archinity directly.** The founders are `Archinity_ArchonianSanguophage`
(`inheritable false`), and `GenePool_Archite.xml`'s `founderOnlyGenes` are `Deathless` and
`Ageless`. Neither is a founder predicate once reimplanting returns.

**Remedy.** Record identity in state that none of these calls touches. `docs/specs/RELIGION.md`
§ *Founders*, route A1, stamps a founder hediff at game start with `duplicationAllowed: false`.

*[#134](https://github.com/cjd721/Rimworld-Archinity/issues/134). `RimWorld.GeneUtility.ReimplantXenogerm`
/ `.ImplantXenogermItem`, `Verse.Pawn_GeneTracker.SetXenotype`,
`RimWorld.GameComponent_PawnDuplicator.Duplicate`; `Biotech/Defs/GeneDefs/XenotypeDefs.xml`. 1.6.4871.*

---

### T-113 — An Anomaly duplicate inherits every record hediff unless the def opts out

`GameComponent_PawnDuplicator.CopyHediffs` clears the duplicate's hediffs and re-adds every source
hediff whose `def.duplicationAllowed` is true and whose body part exists on the duplicate. Added
parts and implants are copied only if `organicAddedBodypart`. `HediffDef.duplicationAllowed`
**defaults to `true`**. A hediff used as a per-pawn store therefore appears on the duplicate as a
second copy, and nothing reports it. The one we specify is `Archinity_FounderRecord` /
`CompFounderRecord` (`docs/specs/TRANSCENDENCE.md`). The duplicate then reads as a second founder to
every gate.

**Remedy.** Set `<duplicationAllowed>false</duplicationAllowed>` on any identity- or record-bearing
`HediffDef`.

*[#134](https://github.com/cjd721/Rimworld-Archinity/issues/134). `RimWorld.GameComponent_PawnDuplicator.CopyHediffs`,
`Verse.HediffDef.duplicationAllowed`. 1.6.4871.*

### T-146 — A permit granted without a title is permanent, and the "Call aid" gizmo keeps offering it

`Pawn_RoyaltyTracker.AddPermit(permit, faction)` stores
`new FactionPermit(faction, GetCurrentTitle(faction), permit)`, and the title may be null. Every
automatic vanilla removal keys on the `Title`:

- `ReduceTitle` and `ResetPermitsAndPoints`, which returns at once when `currentTitle == null`;
- `Notify_Resurrected`.

The only faction-keyed removal is the player's *Return all permits*
(`Pawn_RoyaltyTracker.RefundPermits`, from `PermitsCardUtility`), which requires
`faction.def.HasRoyalTitles` and 8+ favour — out of reach for a titleless grant. `AddPermit` also
replaces a permit's prerequisite.

The load-time `RemoveAll` only de-duplicates prerequisites. `Pawn.GetGizmos` yields
`RoyalAidGizmo` on `HasAidPermit` alone.

A band drop, a broken oath or a hostile turn therefore removes nothing, and nothing says so.
Hostility does grey the option (`AidDisabled_NewTemp`); neutrality does not.

**Fix:** remove from the live `AllFactionPermits` list in the same synced command that ends the
grant.

*[#168](https://github.com/cjd721/Rimworld-Archinity/issues/168), `docs/specs/TERRITORY.md` §
*A sworn faction owes services*. `RimWorld.Pawn_RoyaltyTracker.AddPermit` / `.ReduceTitle` /
`.ResetPermitsAndPoints` / `.Notify_Resurrected`, `Verse.Pawn.GetGizmos`,
`RimWorld.RoyalTitlePermitWorker.AidDisabled_NewTemp` (`Assembly-CSharp.dll`). [V]*

### T-167 — A VPE path lock gates only the *Unlock* button; psytrainers and psyrings walk past it by default

`PsycasterPathDef.ignoreLockRestrictionsForNeurotrainers` **defaults to `true`**. While it is true,
nothing outside VPE's psycast tab consults the path's `requiredGene` / `requiredFocus` /
`requiredBackstoriesAny` / `requiredMeme` / `requiredMechanitor`:

- **Psytrainers.** VPE generates a `Psytrainer_<ability>` for **every** psycast `AbilityDef`
  (`ThingDefGenerator_Neurotrainer_ImpliedThingDefs_Patch`), including any path we author, tagged
  `RewardStandardLowFreq`. `CompPsytrainer.CanBeUsedBy` skips the lock check. `DoEffect` then calls
  `UnlockPath` unconditionally, so the whole locked path opens to any psycaster.
- **Psyrings.** Technomancer's `VPE_CraftPsyRing` makes a ring from any psycast the crafter knows.
  `Psyring.Notify_Equipped` gives the ability to any psycaster wearing it and never reads the path.
- **Casting.** `AbilityExtension_Psycast.IsEnabledForPawn` refuses a locked path's ability only when
  the flag is false.

No message and no greyed option appear. A founder-only or gene-locked path simply has a
non-founder casting from it.

**Fix.** Set `<ignoreLockRestrictionsForNeurotrainers>false</ignoreLockRestrictionsForNeurotrainers>`
on every gated path, as VPE Hemosage's `VPEH_Hemosage` does. Removing psytrainers (#10 §5's decision)
closes only the trainer half. `ensureLockRequirement` alone parks a psytrainer-opened path at the
next recheck (T-168), but a psyring's ability belongs to a path the wearer never unlocked, so it
stays castable.

*[#162](https://github.com/cjd721/Rimworld-Archinity/issues/162), `docs/specs/PSYCHIC.md` § *A
psycaster path only the founders can take*. `VanillaPsycastsExpanded.CompPsytrainer.CanBeUsedBy` /
`.DoEffect`, `.AbilityExtension_Psycast.IsEnabledForPawn`, `.Technomancer.Psyring.Notify_Equipped`,
`.ThingDefGenerator_Neurotrainer_ImpliedThingDefs_Patch` (`2842502659/1.6/Assemblies/VanillaPsycastsExpanded.dll`). [V]*

### T-168 — `ensureLockRequirement` rechecks on three signals only, parks the path, and never revokes or refunds

`PsycastUtility.RecheckPaths` is VPE's only relock. It runs only from postfixes on
`HediffSet.DirtyCache`, `Pawn_GeneTracker.Notify_GenesChanged` and
`Pawn_AbilityTracker.Notify_TemporaryAbilitiesChanged`. Keys that change by any other signal leave
the path open until some unrelated hediff change happens to fire a recheck:

- `requiredMeme`, on an ideoligion change or conversion;
- `requiredBackstoriesAny`, on a backstory edit;
- anything a custom `CanPawnUnlock` reads.

When it does fire, the path is **parked**, not removed. It moves to `previousUnlockedPaths`,
`AbilityExtension_Psycast.ShowGizmoOnPawn` hides that path's gizmos, the learned abilities stay in
`CompAbilities`, and `points` is untouched. When the key returns, the path comes back free. A path
**without** `ensureLockRequirement` never relocks once unlocked, whatever happens to the key.

**Fix.** Key relockable paths on a hediff or a gene, whose changes fire the recheck. If a key must
change by another signal, call `pawn.RecheckPaths()` (public extension) in the same synced command.

*[#162](https://github.com/cjd721/Rimworld-Archinity/issues/162). `VanillaPsycastsExpanded.PsycastUtility.RecheckPaths`,
`.HediffSet_DirtyCache_Patch`, `.Pawn_GeneTracker_Notify_GenesChanged_Patch`,
`.Pawn_AbilityTracker_Notify_TemporaryAbilitiesChanged_Patch`, `.AbilityExtension_Psycast.ShowGizmoOnPawn`
(`2842502659/1.6/Assemblies/VanillaPsycastsExpanded.dll`). [V]*

### T-169 — The vanilla psylink method is not a chokepoint: a gate there misses most rank writes

A Harmony gate on `Hediff_Psylink.ChangeLevel` looks as if it guards psylink rank. It misses
most writes, silently:

- **The one-argument overload is skipped.** `PawnUtility.ChangePsylinkLevel` calls
  `ChangeLevel(int, bool)` directly. So a prefix on `ChangeLevel(int)` never sees the anima tree
  (`CompPsylinkable.FinishLinkingRitual`), the blinding ritual or the bestowing ceremony. It sees
  only neuroformer upgrades, which reach it through the virtual `Hediff_Level.ChangeLevel`.
  VRE – Android's android block has exactly this shape.
- **The first rank never calls `ChangeLevel`.** A neuroformer, the `ChangePsylinkLevel` null
  branch, a gene's hediff and `PawnGenerator` all *add* the hediff at level 1.
- **Some writers set the field directly.** `Hediff_Psylink.CopyFrom` (Anomaly duplicates),
  Prepare Carefully's `AddPsylinkOrSetLevel` and VPE-Puppeteer's `MindJump.TransferMind` write
  the level without calling any method.
- **Under VPE the method is dead code.** VPE's prefix on `ChangeLevel(int, bool)` returns false
  and hands off to `Hediff_PsycastAbilities.ChangeLevel`. That method writes
  `psylink.level = this.level` directly, as do VPE's XP loop, NPC generation and title grants.
  None of them calls the vanilla method.

**Fix.** Under VPE, gate `Hediff_PsycastAbilities.ChangeLevel(int)`, the virtual override that
every VPE rank change after the first passes through. Gate the first rank where
`PsychicAmplifier` is added. Close the direct field writers at their own defs.

*[#163](https://github.com/cjd721/Rimworld-Archinity/issues/163), `docs/specs/PSYCHIC.md` §
*What raises psylink rank besides the altar*. `Verse.Hediff_Psylink.ChangeLevel` / `.CopyFrom`,
`RimWorld.PawnUtility.ChangePsylinkLevel` (`Assembly-CSharp.dll` 1.6.4871);
`VanillaPsycastsExpanded.Hediff_Psylink_ChangeLevel`, `.Hediff_PsycastAbilities.ChangeLevel`;
`VREAndroids.Hediff_Psylink_ChangeLevel_Patch`. [V]*

### T-170 — Quest rewards add a psylink neuroformer on a pity timer that no def tag controls

The psylink neuroformer (`ThingDef PsychicAmplifier`) has no `thingSetMakerTags`, so it looks as
if it can never be a quest reward. It can. `Reward_Items.InitFromValue` adds one by `ThingDefOf`
before any tag-driven generation runs. The conditions:

- Royalty is active;
- the chance ramps from 0 at 45 days to 1 at 60 days since `History.lastPsylinkAvailable`
  (`QuestTuning.DaysSincePsylinkAvailableToGuaranteedNeuroformerChance`);
- the reward is worth at least 600;
- the giver is not the Empire;
- the quest's `disallowedThingDefs` does not list it.

The timer starts at game start (`History.FinalizeInit`). It resets only when a psylink becomes
*available* (`History.Notify_PsylinkAvailable`):
- an anima-tree link;
- a chosen neuroformer reward (`QuestPart_Choice`);
- a quest that carries one being added (`QuestPart_DropPods`, `QuestPart_GiveToCaravan`,
  `QuestPart_SpawnWorldObject`);
- a title reward containing one;
- vanilla's bestowing loop. VPE's transpiler removes that loop, so under VPE bestowing does not
  reset it.

It does **not** reset on psylinks from the blinding ritual, VPE XP or our own code. A campaign
whose first psylink comes late therefore sees neuroformers guaranteed in item rewards from about
day 60, and again roughly every 45 to 60 days after each one is offered. Nothing logs it.
[#21](https://github.com/cjd721/Rimworld-Archinity/issues/21) read the missing tag as proof
that no quest could reward one.

**Fix.** Make the item inert in XML: remove `CompProperties_UseEffectInstallImplant` from the
ThingDef, and keep the def, which `ThingDefOf` needs. Or keep `History.lastPsylinkAvailable`
current from C#. Stripping tags does nothing.

*[#163](https://github.com/cjd721/Rimworld-Archinity/issues/163). `RimWorld.Reward_Items.InitFromValue`,
`RimWorld.QuestTuning`, `RimWorld.History.Notify_PsylinkAvailable` / `.FinalizeInit`,
`RimWorld.QuestPart_Choice`, `.QuestPart_DropPods.PostQuestAdded`, `.QuestPart_GiveToCaravan`,
`.QuestPart_SpawnWorldObject`, `.RitualOutcomeEffectWorker_Bestowing.Apply`, `RimWorld.Pawn_RoyaltyTracker`
(`Assembly-CSharp.dll` 1.6.4871); `VanillaPsycastsExpanded.RitualOutcomeEffectWorker_Bestowing_Apply_Patch.Transpiler`. [V]*

## Ideology authoring

### T-121 — No `FactionDef` restriction applies inside the ideology reform dialog

`Dialog_ReformIdeo` edits `newIdeo = IdeoGenerator.MakeIdeo(...)` — a scratch ideology that is
**in no `IdeoManager` and listed by no faction** [V]. Every faction-def gate on precept choice
runs through `Ideo.CanAddPreceptAllFactions`, whose faction loop tests
`ideos.IsPrimary(this) || ideos.IsMinor(this)`; against the scratch copy that loop matches
nothing, falls through, and **accepts everything** [V].

So `disallowedPrecepts`, `requiredMemes` and every sibling field **silently stop applying the
moment the player clicks Reform**. The meme picker in that dialog is bypassed the same way.
There is no error, no message and no visible difference in the UI — the restricted options are
simply back.

What *does* survive a reform is `MemeDef.requireOne`, because `ideo.CopyTo(newIdeo)` carries the
memes and both `CanAdd`'s swap rule and `GetMemeThatRequiresPrecept`'s remove block read the copy
[V]. A campaign floor that must hold through a reform belongs on a meme, not on a faction def.

*[#140](https://github.com/cjd721/Rimworld-Archinity/issues/140), `docs/specs/RELIGION.md` §
*A campaign base for the player faith*; `docs/engine/ideology.md` § *Forcing and floor-setting a
player ideology*. `RimWorld.Dialog_ReformIdeo`, `RimWorld.IdeoGenerator.MakeIdeo`,
`RimWorld.Ideo.CanAddPreceptAllFactions`, `RimWorld.IdeoFoundation.CanAddForFaction`.
1.6.4871.*

### T-122 — A precept refused by `disallowedPrecepts` vanishes from the menu instead of greying out

`IdeoFoundation.CanAddForFaction` returns a **bare `false`**, which becomes an
`AcceptanceReport.WasRejected` whose `Reason` is `""` [V]. `Precept.DrawPreceptBox` lists a
rejected option only when the reason is non-blank [V].

**The player sees a shorter list and no explanation — and so do we.** A restriction that is
working and a restriction that was never loaded look identical in the editor, so the only way to
tell a typo in `disallowedPrecepts` from a correct gate is to read the def.

**Remedy:** verify the gate by reading the faction def in play, not by looking at the issue menu;
if a reason must be shown, the report has to be constructed with one.

*[#140](https://github.com/cjd721/Rimworld-Archinity/issues/140), `docs/specs/RELIGION.md` §
*A campaign base for the player faith*. `RimWorld.IdeoFoundation.CanAddForFaction`,
`RimWorld.Precept.DrawPreceptBox`, `Verse.AcceptanceReport`. 1.6.4871.*

### T-123 — `FactionDef` meme fields on a *player* faction def are inert whenever a world exists

`Dialog_ChooseMemes.CanUseMeme` and `CanRemoveMeme` consult the player `FactionDef` **only in the
`Current.Game.World == null` branch** [V]. Once a world exists — which it does throughout normal
setup, since `Page_ChooseIdeoPreset.PostOpen` reads `Find.FactionManager.AllFactions` — both fall
to a faction loop that **explicitly skips `allFaction.def.isPlayer`** [V].

So `FactionDef.requiredMemes`, `forcedMemes`, `allowedMemes` and `disallowedMemes` have **no
effect on a player-authored custom ideology's meme selection**. Vanilla ships
`<disallowedMemes><li>Transhumanist</li></disallowedMemes>` on `PlayerTribe` and it does not bind
the editor [V] — which is exactly what makes the field look as though it works. World Tech
Level's `IsMemeAllowedFor` postfix leaks through the same hole [V].

**This is the opposite of `disallowedPrecepts`**, which *does* reach the player by a different
path (`docs/engine/ideology.md` § *Forcing and floor-setting a player ideology*). "FactionDef
ideology fields are NPC-only" is wrong as a generalisation and right about these four.

**Remedy:** put the meme on the ideology by a route that does not go through the picker — a
`IdeoPresetDef`, a `Page_ChooseIdeoPreset` patch (VFE Tribals is the shipped donor), or a
`ScenPart.PostIdeoChosen`.

*[#140](https://github.com/cjd721/Rimworld-Archinity/issues/140), `docs/specs/RELIGION.md` §
*A campaign base for the player faith*. `RimWorld.Dialog_ChooseMemes.CanUseMeme` / `.CanRemoveMeme`,
`RimWorld.Page_ChooseIdeoPreset.PostOpen`; `Data/Core/Defs/FactionDefs/Factions_Player.xml`.
1.6.4871.*

### T-161 — A pawn with no ideology is the easiest pawn to convert

A null `Ideo` reads like "nothing for conversion to act on". It is the opposite. Nothing on the
conversion path treats a null faith as a refusal:

- **`Pawn_IdeoTracker.IdeoConversionAttempt`** does not test `ideo != null`. It lowers `Certainty`,
  and at `<= 0` calls `SetIdeo(initiatorIdeo)` [V]. A pawn that never had a faith has never had
  `SetIdeo` run, so its certainty field is still **0**, and the **first** attempt converts it. After a
  save and load, `ExposeData` gives it a random starting certainty whether or not it holds a faith,
  and it converts on an ordinary schedule instead.
- **The Convert ability.** `CompAbilityEffect_Convert.Valid` asks only human, not a baby, no mental
  state, **not the same ideology** and conscious. `null != caster.Ideo`, so the target is valid. The
  ability plays its normal *success* message [V].
- **The conversion ritual.** `RitualRoleConvertee.AppliesToPawn` refuses only `p.Ideo ==
  ritual.ideo` [V], and `Dialog_BeginRitual` draws its candidates from
  `FreeColonistsAndPrisonersSpawned` [V]. A prisoner with no faith is a legal convertee, and the
  best outcome calls `SetIdeo` [V].

Only the warden route is loud: `InteractionWorker_ConvertIdeoAttempt.Interacted` dereferences
`recipient.Ideo.GetRole(recipient)` and throws [V]. The two routes a player is most likely to use
say nothing.

**Remedy.** "Believes nothing" and "can never be converted" are two properties. Gate the second
where the faith is written — `Pawn_IdeoTracker.SetIdeo` and `IdeoConversionAttempt` — and close the
ability and ritual offers for legibility. `docs/specs/ANDROIDS.md` § *A captured Glitterite*.

*[#142](https://github.com/cjd721/Rimworld-Archinity/issues/142). `RimWorld.Pawn_IdeoTracker.IdeoConversionAttempt`
/ `.ExposeData`, `RimWorld.CompAbilityEffect_Convert.Valid`, `RimWorld.RitualRoleConvertee.AppliesToPawn`,
`RimWorld.Dialog_BeginRitual`, `RimWorld.RitualOutcomeEffectWorker_Conversion.Apply`,
`RimWorld.InteractionWorker_ConvertIdeoAttempt.Interacted`. 1.6.4871.*

---
