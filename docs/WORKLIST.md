# Work list

Everything session 4 found that needs doing, with the verified fact behind it.
Mechanics only — **`Player Progression Ideology.txt` is the design authority**
for what the progression should feel like, and nothing here overrides it.

`technical-findings.md` has the evidence for every claim below.

---

## 0. Conflicts to resolve before building

**`VISION.md` rejects VFE Tribals. `Player Progression Ideology.txt` wants it.**
VISION says it "changes research too heavily… subscribed, deliberately off."
The ideology doc opens by calling it "the perfect start to a game like this" and
asks to keep its skill-unlock research, its job/gizmo unlocks and its cornerstone
system tied to TechBlock tier-ups. **These cannot both stand.** Resolve before
any Neolithic work, because it decides the whole shape of the first 30 days.

Knock-on: `Progression: Core` was assessed SKIP *because* it depends on VFE
Tribals. If Tribals comes back, that assessment reopens.

**`VISION.md` says "VFE Classical and Medieval 2 carry" the Medieval era.**
Measured: VFE Classical contributes **zero** Medieval projects. All 18 are
Neolithic. Fix the sentence.

---

## 1. Castles and siege

The user's own framing: MO factions should get maps as good as VFEM2's, both
should be enhanced, earlier-era siege weapons should appear in them, and enemies
should deploy siege when raiding the player.

### Authoring
- **Use the KCSG exporter.** Dev mode, Architect, Orders, **Export**, drag a
  rectangle, then "Copy structure" and "Copy symbols". Build castles in a
  sandbox rather than hand-writing grids. An existing keep can be spawned,
  edited and re-exported.
- **VFEM2 already routes its kingdoms through KCSG** (85x85, one keep from tag
  `VFEM2_Keep`, 12 houses). What it lacks is a **perimeter and a garrison** —
  no curtain wall, no gatehouse, no towers, no `defenseOptions` block at all.
  The keep sits in an open village.
- **MO uses `chooseFromlayouts`** — single hand-built structures per noble
  house, not a tag pool. Different mechanism; give it equivalent treatment.
- Author `Archinity_CurtainWall`, `_CastleTower`, `_Gatehouse` as tagged
  `StructureLayoutDef`s and `PatchOperationAdd` them into
  `VFEM2_MedievalFactionBase`'s `peripheralBuildings/allowedStructures`.
- **Never add a second `KCSG.CustomGenOption`** to a faction that has one —
  `GetModExtension` returns the first match. Patch the settlement def instead.
- **Every tag must have at least one layout** or `structuresTagsCache[tag]`
  throws mid-worldgen. Add this check to `check_refs.py`.
- Estimated 6–9 distinct layouts, roughly 4–6 sessions. **Open risk:** KCSG has
  no concept of a settlement boundary, so independently Poisson-placed wall
  segments may not tile into a continuous perimeter. Untested.

### Siege weapons in the maps
- **`VFEM2_Turret_WallMountedArbalest` and `_Arquebus` ship and are never placed
  anywhere.** 1x1, mannable. Two hand-written SymbolDefs and they go into a
  tower. Cheapest win available.
- `DankPyon_Turret_Trebuchet` can be placed but **spawns unmanned** — auto-manning
  needs `buildingTags` to contain `Artillery_MannedMortar`, and its tags are
  `Artillery_BaseDestroyer` / `ArtilleryMedieval` /
  `ArtilleryMedieval_BaseDestroyer`. Add a pawn symbol beside it or patch the tag.
- Neolithic-tier options: `VFEC_Turret_Scorpion`, `VFES_Turret_Ballista`.
- `defenseOptions.addTurrets` and `addMortars` are **dead below Industrial** —
  KCSG gates both on `techLevel >= 4`. Only `addSandbags` and
  `pawnGroupMultiplier` work for medieval factions, so siege engines must live
  inside the layout grid.
- SymbolDefs place pawns too: `pawnKindDef` + `numberToSpawn` +
  `defendSpawnPoint: true` gives a manned battlement.

### Enemies using siege against the player
- `MedievalOverhaul.RaidStrategyWorker_MedievalSiege` is gated on the
  `FactionSiegeExtension.medievalSiege` extension **and** `techLevel == 3`.
- **Both that extension and the `ArtilleryMedieval_BaseDestroyer` buildingTag
  are plain def-level constructs** — patchable onto VFEM2 factions once MO
  loads. Currently only `DankPyon_BrigandFaction` carries it.
- **No VFEM2 faction sets `canSiege`**, so vanilla sieges cannot fire for them
  either. Both need adding.
- For earlier-era siege, the same pattern needs a Neolithic-appropriate
  equivalent — unverified whether the strategy worker's `techLevel == 3` check
  can be satisfied any other way without C#.

---

## 2. Bugs in our own code

- **`AltarFacilityExtension` is applied to ZERO defs.** It appears only inside a
  comment. So all twelve linked VQE facilities do nothing, `outcomeBonus` is
  permanently 0, `chargeCostFactor` and `durationFactor` are permanently 1, and
  the critical-failure rate is a flat **25% for the entire campaign**. This is
  why the altar's Medieval facilities are currently decorative.
- **Both shipped gene vectors are unusable by the founders.**
  `VQEA_PerfectVision` and `VQEA_PlasteelSkin` are already in
  `Archinity_ArchonianSanguophage`, so `CanAcceptPawn` returns `AlreadyHasGene`.
  Neither sets `requiresRecipientGene`, so **only baseliners can use them** —
  the inverse of the intent.
- **`CanAcceptPawn` rejects non-`Humanlike`**, so animals can never be altar
  fuel. `VISION.md` says "fifty people, or several hundred animals."
- **`DrainTicks = 7500` is 3 hours**, not the "~2 hours" HANDOFF states.
- **`archinity.altar` is not in `ModsConfig.xml`** — the def has never loaded.
- **Nothing spawns the altar.** `grep -rn Archinity_Altar` hits only its own
  def, its C# and its language keys. No quest, prefab, scatterer or ThingSetMaker.
- The altar is **not `neverBuildable`** as documented — it is unbuildable only
  because it has no `designationCategory` and no `costList`. A stray
  `designationCategory` later would silently make it buildable.
- **`ModsConfig.xml` lists `ludeon.rimworld.odyssey` twice.**
- The scenario hands out `MeleeWeapon_Ikwa` with `<stuff>Steel</stuff>` at a
  Neolithic start.

---

## 3. Balance holes found

- **`VFEM2_Apparel_PaddedArmor` has no `researchPrerequisite` at all** — 0.65
  SEMA free at tailor-bench tier.
- Several of MO's nine `DankPyon_Headgear_HeraldicGreatHelm*` / `Hauberk*`
  colour variants also have no research gate. MO's four heraldic heater shields
  have **no recipe and no research**.
- **`VFEC_Scorpion` gives a siege engine in the Neolithic era.**
- `VFES_SiegeEquipment` is reachable off bare `Smithing`. Repoint behind
  `DankPyon_Engineering`.
- **`PlateArmor` issues two rungs** (0.90 and 1.02) on one gate.
- **MRR `Devilstrand` is a genuine Neolithic deadlock** — 9 studies of
  `DevilstrandCloth`, but sowing needs the research and no Neolithic trader
  stocks `Fabric`.
- **VCE adds three real MRR deadlocks**: `VCE_Canning`, `VCE_DeepFrying`,
  `VCE_SoupCooking`. Each unlocks exactly one bench that is `tradeability: None`
  with no loot/mapgen/trade route. Fix is three `ManualAnalysisDef` entries in
  the existing `Archinity.Pacing/Defs/ManualAnalysisDefs/Analysis_Unblock.xml`.
- **`VCE_StewPot` does not supersede `VCE_ElectricPot`** — stews and soups are
  different items. `PatchOperationAdd` the three stew processes onto
  `VCE_ElectricPot`'s `processes` node.
- **`VFEM2_LeatherBoilpot` exists but is pointless** — hardleather is +.07 sharp
  and **-.02 blunt** over plain leather. One `PatchOperationReplace` on its
  `StuffPower_Armor_*` makes boiling mean something.
- **MO's crossbow, heavy crossbow and handgonne are dead under the no-new-metals
  rule** — all three need `DankPyon_IronIngot` and there is no Steel path.
  `VFEM2_Arbalest` and `VFEM2_Gun_HandCannon`/`Arquebus` cover the same slots.
- MO moves `Bow_Recurve`/`Bow_Great` off `CraftingSpot`, removing the early bow.

---

## 4. Content the ideology doc rules out

Straight from `Player Progression Ideology.txt`, recorded here as work items.

- **Remove MO's woodworking chain** (wood to planks to boards). "I take wood, I
  use wood."
- **Remove MO's paper / paper press / cartography** entirely.
- **Remove textile spinning and linen.** Tailoring absorbs it; the spinning
  wheel becomes an augment. Silk stays only as a cloth upgrade, not a spun chain.
- **Remove Mithril** — strictly medieval-terminal, and power armour supersedes it.
- **Keep and simplify:** carrier birds (research, build a bird post, own birds,
  done — no paper), beekeeping, brewing, winemaking as opt-in.
- **Keep:** mine shaft, medieval crane, scarecrow, sprinkler. Place-and-forget
  QoL that scales.
- **Cut the plant count hard.** Vanilla set plus a small expansion, tiered
  across basic/intermediate/advanced agriculture.
- **Cut the ingredient additions** (salt, saffron etc.) on the pool-dilution
  rule.
- **Cooking:** one base station plus augments, not six benches. Recipe
  complexity stays linear — each tier adds *one* ingredient class, and
  ingredients are generic ("any two vegetables"), never specific crops.

---

## 5. Settings

Both players need byte-identical files. Re-snapshot into `config/ModSettings/`
after any change.

| Mod | Setting | To |
|---|---|---|
| Ignorance Is Bliss | `useHighestResearched` | **on** (sidesteps the techLevel-lag question entirely) |
| Ignorance Is Bliss | `EmpireIsAlwaysEligible` | **false** — defaults true, so Ultra raids can hit a Neolithic colony |
| Ignorance Is Bliss | `ChangeQuests` | **true** — defaults false, letting quest raids bypass the tech filter |
| TechBlock | `randomInsightRate`, `randomInsightProgressBlock` | **both ~0.5**, in XML. Identical total spend, but the lock bar visibly moves |
| MO | `vanillaMine` | **on** — defaults off, and it is what removes steel and component veins |
| MO | `component_replace`, `chemfuel_replace` | **off** — 395 and 51 ThingDefs, including ship parts |
| MO | `biotechSchematic` | **off** — destroys the item on analysis and strips its `tradeTags` |
| MO | `industrialJunk` | **on** — free answer to the architect-menu clutter complaint |
| MO | `slopDispenser` | **off** — the author's own advice |
| Faction Customizer | — | settings file **missing** from `config/ModSettings/` |

**The MO settings trap:** `if (!metalChain) { vanillaMine = true; }` lives inside
the Map-Gen tab's *draw* method. Uncheck `metalChain` elsewhere and close without
visiting that tab and the force never runs. **Copy the file between machines;
never re-click.** And compare *parsed values*, not bytes — `Scribe_Values.Look`
omits defaults.

**Worldgen, not a setting:** `VFEM2_KingdomRough`, `KingdomSavage`, `ClanSavage`
and `CivilClan` ship at `startingCountAtWorldCreation = 0`. A default world gets
only two visible Medieval factions. **Add them by hand at world creation** —
this is the single cheapest fix to "80% of medieval raids are neolithic tribals."

---

## 6. Tooling

- **`audit_research.py` applies no PatchOperations**, so every tier total needs
  hand-correction. Under Route A that is misleading rather than merely lagging.
  Teach it Replace/Add/Remove on `ResearchProjectDef` before the next retier.
- **`check_refs.py` never reads `ModsConfig.xml`** — it harvests the whole
  workshop directory, so identical output across configurations is guaranteed by
  construction and proves nothing about a route change.
- **`check_availability.py --plan` is not a mode.** It strips all `--` args; the
  docstring promises a third mode that does not exist.
- **New check needed:** every KCSG tag referenced by a `SettlementLayoutDef` must
  have at least one `StructureLayoutDef` carrying it, or worldgen throws.
- One broken XML file found in MO:
  `Languages/ChineseSimplified/DefInjected/ThingDef/Races_Hyena.xml`. Translation
  only, no English def affected.

---

## 7. Multiplayer test checklist

MO's failure mode is reported as **specific, not diffuse**. Settle by testing.

1. Load a **Dark Forest** tile — reported as a hard failure, joining player
   desyncs immediately. If this is the only one, it is a `PatchOperationRemove`
   away.
2. Craft and use MO custom items.
3. Force a quest — desync reported on arrival, recovering after resync.
4. Enter an encounter map.
5. **Both players harvest plowed soil simultaneously** — exercises
   `Rand.Chance(settings.soilWearChance)`.
6. **Both players open the research tab and research simultaneously** —
   exercises the unkeyed schematic cache.

Facility linking needs no test: it is positional, automatic, has no `Rand`, and
`Multiplayer.dll` contains no facility references at all.

---

## 8. Still open

- **Route A vs B was resolved on licensing**, which the user has since made moot
  by planning to take the repo private. On the merits Route A still wins: same
  37,900 research points either way, 4–8 h versus ~45 h, six free compat layers,
  and no fork to re-port at RimWorld 1.7. **Not re-litigated after the
  frame changed — worth one explicit confirmation.**
- **RimFantasy** — enable minus the four temperature pylons and
  `RF_ArcaneTemperatureRegulation`? `RF_FrostPylon` is a -22 heat/s cooler with
  **no power cost**, which permanently devalues Electricity. Buildings first,
  then the research, per the CLAUDE.md ordering rule.
- **Dark Ages: Medieval Tools** — recommended skip. Zero research points, MO
  ships strictly better versions of its three best tools, and four of its five
  buildings are permanent tool-cabinet clones that stack with the vanilla one.
- **`Faction - Elves`** is subscribed, unassessed, def-only, and ships a faction
  plus xenotypes. Rule on it against the no-race-bleeding principle.
- **Two grape plants and two wine chains** (`DankPyon_Plant_Grape` vs
  `VFEM2_Plant_Grape`) with no compat patch anywhere.
- **Neolithic storage.** Nothing in the load order provides it — Adaptive
  Storage Framework is a pure library with zero buildable defs, and every sbz
  crate is gated on `ComplexFurniture`. Either author one (template at workshop
  `3416243474`, `sbzCrateBase`) or subscribe "Adaptive Primitive Storage", which
  ships exactly `ASF_WovenBasket`, `ASF_ClayPot`, `ASF_StoragePit`.
- **Stranded VFE Classical research** — five 1,200-point Neolithic projects
  (`LegionnaireArmor`, `CenturionArmor`, `HeavyShieldMaking`, `BronzeWorking`,
  and Togas' wreath) all need a Medieval `FueledSmithy`. That is 6,000 points
  buying nothing. `VFEC_HeavyShieldMaking` gates the **best shield in the entire
  load order** (S .75 / B .70).
- **Nice Research Tab.** TechBlock injects `TB_<Era>Theory` onto every tier-root
  project, turning the graph into a star. This stops being cosmetic under a
  design where the player is meant to *see* the next unlock and its
  requirements.
