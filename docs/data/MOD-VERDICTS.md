# Mod verdicts

The bar from [#3](https://github.com/cjd721/Rimworld-Archinity/issues/3), applied to
**every mod on disk — all 130**. Issue [#17](https://github.com/cjd721/Rimworld-Archinity/issues/17).

**The instrument, restated so this file stands alone:**

- **Barred** — we *cannot* use it. Only when fixing it would mean owning their
  assembly: a parallel world simulation, or background threads. Nothing else bars.
- **Declined** — we *can* use it and choose not to. Conrad's call. No justification owed.
- Everything else is **Free** (enable it), **Cheap** (enable plus a
  `PatchOperation`) or **Real** (a fork we re-merge, or a Harmony patch in our
  assembly).
- Barred and declined mods **stay on disk as reference.**

**130 mods on disk** — the workshop folder, local `Mods/`, and this repo. **Every one
has a verdict.**

**Five of them are ours** (Origins, Pacing, Drifters, Glitterites, Altar) and the
admission bar does not apply to them: the bar decides whether to admit *someone
else's* work. Our own code is governed by the two gates in `CODING_STANDARDS.md`.
So the bar runs over the **125 third-party** mods.

> **`config/ModsConfig.xml` carries no signal and is not referenced below.** Mods are
> unenabled because the game has not been launched, not because anything was decided.
> An earlier revision of this file treated enabled/disabled as evidence of intent and
> drew a conclusion from it; that was wrong and is struck.

---

## Corrections to the first pass

1. **Factional War is not barred, and not declined.** It has no threading of any kind
   — a single `WorldCompFormCaravanAfterAllyExit` and nothing else **[V]**. Both the
   barred label and a later declined label were mine and neither was supported. It is
   **in and undecided**; see **Explicitly NOT declined** below.
2. **The Medieval Overhaul flag is void.** It rested on MO being disabled, which
   means nothing. MO is a normal candidate.
3. **Faction Territories and Worksites Expanded are un-declined.** I declined both
   on my own judgment; that was not mine to do. Both are tiered below and returned
   to Conrad undecided. Neither is barred — one `WorldComponent` each, no thread
   creation **[V]**.
4. **Six mods added since the first scan**, taking the disk total to 120:
   RimPacts, ATH's Styleable Framework, and the style packs Gothic, Norse and Draconic,
   plus Fix Styled Blueprints. RimPacts closes a standing `PARTS-BIN.md` §14 open item
   — see below. The five ATH/style entries are one family: a framework, three style
   packs and a blueprint compat fix; none carries a bar risk of any kind.
4b. **Two more mods added since, taking the disk total to 122:** **Tavern**
   (`ODs.Tavern`, `3775694305`) and **Slave Rebellions Improved (Continued)**
   (`Mlie.SlaveRebellionsImproved`, `3259932217`). Neither is barred. Tavern is
   **Free** — no assembly at all. SRI is **Cheap + settings**, and its settings are
   read from inside rebellion logic, so they are save-critical in the strong sense.
   Both are tiered below and recorded in `PARTS-BIN.md` §15.
4c. **Eight more mods added since, taking the disk total to 130** — seven QoL and one
   race, recorded in `PARTS-BIN.md` §16. **None is barred.** The batch is cheap in
   content and expensive in *settings*: five of the eight carry a `ModSettings` surface
   and **three of those steer synced simulation state**, which is §3.1's dominant hazard
   rather than anything new. The sharpest is **Auto-Cast Specialist Commands**, which
   gates *toil-list construction* on a client-local bool — see the Named prices table.
   One item outside the tiers: **Range Finder** ships a second, stale assembly in a
   folder its own `LoadFolders.xml` puts in the 1.6 load path; see below.
5. **`Archinity.Altar` was absent from every earlier revision**, despite the claim
   that every mod had a verdict. It lives only in this repo, not in Steam's `Mods/`
   folder like the other four Archinity mods, so the disk scan never saw it — and it
   is the one Archinity mod that ships an assembly. Now covered under **Ours** below.
6. **Vehicle Framework and TechBlock were counted twice**, appearing in both the
   Cheap+settings table and the Real tier. Real is now carved *out of* Cheap+settings.
7. **The TechBlock evidence was read from the wrong build** — the `1.0` assembly
   rather than the `1.6` one that actually loads. Re-verified; the verdict stands but
   the reasoning changed. See the Real tier.

---

## Method, and what it can and cannot prove

Byte-marker scan of every 1.6 assembly, then `ilspycmd` decompiles wherever a marker
was load-bearing. `[V]` = decompiled and read. `[M]` = marker-level only.

**90 of 130 are mechanically unbarrable** — no assembly at all, or an assembly with
no threading and no `WorldComponent`. For those the bar cannot bite and no
decompile is needed. The remaining 40 were examined individually.

**What the scan proves.** Absence of `ThreadStart` / `ThreadPool` / `IsBackground`
is strong evidence a mod starts no background threads. Assembly presence and
`ModSettings` surface are exact.

**What it does not.** `System.Threading` alone means nothing — `Interlocked`,
`Monitor` and `ConcurrentDictionary` pull it in without any thread being created,
and 18 mods trip it for exactly that reason. `WorldComponent` does not imply a
parallel world model either.

**The sharpened rule, learned from running it:** a world simulation only *bars* if it
runs **off the synced tick**. A `WorldComponent` doing heavy world-state work inside
`WorldComponentTick` is deterministic and syncs fine — objecting to it is a *design*
objection about shadow worlds, which is a reason to **decline**, never to bar. In
practice the bar reduces to one testable thing: **does it create threads.**

**A second methodological trap, found while verdicting Slave Rebellions Improved:**
**do not byte-scan for a fully-qualified type name.** Searching that assembly for
`Verse.Rand` returns **zero** hits, yet the decompile shows a live `Rand.Value` call —
.NET metadata stores namespace and type name as *separate* strings, so the qualified
form never appears as a contiguous byte run. Scan for the bare type (`Rand`) and treat
any hit as "decompile to find out". A zero on `Verse.Rand` proves nothing whatsoever,
and any earlier claim in this file resting on that string is only as good as its `[V]`.

**A third trap, found while verdicting Range Finder: "the 1.6 assembly" is not always
one file.** The TechBlock correction above says to read the build that actually loads.
Range Finder shows the harder case — **two builds load**. Its `LoadFolders.xml` maps
`v1.6` to `/` *and* `1.6`, and **both** directories contain an `Assemblies/RangeFinder.dll`:
a clean 21 KB 1.6 build, and a stale 36 KB legacy build at the root that ILMerges
`CrossPromotion` and `MultiVersionModFix`. They are different files
(`813a891bc7fb…` vs `d660775e8b43…`) **[V]**, and only the stale one contains
`new Thread(…)`. **So resolve `LoadFolders.xml` first and scan every `Assemblies/`
directory it puts in the version's path** — scanning the version-numbered folder alone
would have returned a clean result here and missed the threading entirely.

**One methodological trap, recorded because it cost a pass:** reading `<packageId>`
by regex over `About.xml` returns the first match in the file, which for many mods is
a *dependency's* id inside `<modDependencies>`. The first run reported eight separate
mods as `brrainz.harmony`. Parse the XML; take the direct child of `ModMetaData`.

---

## Barred — 1

| Mod | packageId | Evidence |
|---|---|---|
| **Rim War** | `Torann.RimWar` | `ThreadStart` present in the 1.6 assembly **[V]**, plus `WorldComponent_PowerTracker` and `WorldComponent_IncidentTracker` running a genuine parallel world power simulation, plus a 30-field settings ref constructed inside `WorldComponentTick`. Threads are on by default. |

**One mod, out of 125 third-party.** That is the instrument working as designed, not a shortfall.
With licence struck and the set pinned, almost every defect that used to read as
disqualifying is now something we can simply fix. Already mined for the
faction-tension shape; stays on disk as reference.

## Declined — 5

Conrad's calls, made directly. No justification owed and none recorded.

| Mod | packageId |
|---|---|
| Faction – Elves | `ICC.FOV.ELVES` |
| Dwarves of the Rim | `bean.customxenotypes.dwarvesoftherim` |
| Rim War | `Torann.RimWar` |
| VFE – Insectoids 2 | `OskarPotocki.VFE.Insectoid2` |
| Faction Territories and Vassalage | `jaeger972.factionterritories` |

Rim War is **both** barred and declined; the barred verdict is the operative one.

**The last two were declined in [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) session 2:**

- **VFE – Insectoids 2** — Conrad: *"I don't like that mod and we're going for a mech-themed bad
  guy."* Side effect worth knowing: it removes **5.6 of `ThreatBig` incident weight** that would
  otherwise have crowded the incident pool.
- **Faction Territories and Vassalage** — declined as a *dependency*, with its ideas kept. The
  design it was carrying (territory, caravan-tile ambush forcing, off-map AI-vs-AI invasion,
  vassalage) is **reimplemented in `Archinity.Core`**, and the territory model is deliberately *not*
  its Dijkstra flood-fill: a claimed tile is one within a small radius of a visible settlement or
  outpost. See [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) session 2 and `scratch/recon-vassalage-territory.md`.

### Explicitly NOT declined

These three were listed as declined in an earlier revision **on my judgment, not
Conrad's**. That was not mine to do. Two remain in, tiered below, and undecided —
**Faction Territories has since been declined by Conrad** and has moved to the table above:

| Mod | packageId | Where the want-question lives |
|---|---|---|
| [SR] Factional War (fork) | `SR.ModRimworld.FactionalWarContinued` | [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) — a *duplication* question against whatever shape #8 lands on for faction tension, not a safety one. Not barred: one caravan `WorldComponent`, no threading **[V]**. |
| Worksites Expanded | `godsfathermixtape.worksitesexpanded` | Undecided. One `WorldComponent`, no thread creation **[V]**. |

**The rule this file follows:** it decides what we *can* use. What we *want* is
Conrad's, and gets recorded here only once he has said so.

---

## Ours — 5, and the bar does not apply

The admission bar exists to decide whether to take *someone else's* work. Our own
mods answer to the two gates in `CODING_STANDARDS.md` instead — **divergence** and
**loudness** — and to nothing here.

| Mod | packageId | Assembly | Scan |
|---|---|---|---|
| Archinity – Origins | `archinity.origins` | none | — |
| Archinity – Pacing | `archinity.pacing` | none | — |
| Archinity – Drifters | `archinity.drifters` | none | — |
| Archinity – Glitterites | `archinity.glitterites` | none | — |
| **Archinity – Altar** | `archinity.altar` | `ArchinityAltar.dll`, 24 KB | No `ThreadStart`, no `ThreadPool`, no `IsBackground`, no `System.Threading.Thread`, no `WorldComponent`, no `GameComponentUpdate`, no `ModSettings`, no `Verse.Rand` **[V]** |

**Altar is the only Archinity mod carrying code, and it passes both gates cleanly** —
nothing client-local, no threads, and no `Rand` at all. Worth stating plainly because
it is the assembly the whole project routes through, and because an earlier revision
of this file **omitted it entirely**: it lives only in this repo, not in Steam's
`Mods/` folder like the other four, so the disk scan never saw it. Corrected here.

---

## In — 120 third-party, by tier

> **Amended by [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) session 2.** Was 122. **VFE – Insectoids 2** and **Faction
> Territories and Vassalage** have since been declined by Conrad and are listed in **Declined**
> above. Both still appear in the tier tables below, where the tier verdict (what we *can* use)
> remains accurate — the decline supersedes it on whether we *will*.

Everything third-party that is not barred and not declined. **Our five are not listed
here** — see the note at the top; they are in by definition and answer to the two
gates, not to a tier.

**Free (24)** — no assembly. Nothing can go wrong that is not XML.

| Mod | packageId |
|---|---|
| Vanilla Weapons Expanded | `VanillaExpanded.VWE` |
| Vanilla Weapons Expanded – Tribal | `VanillaExpanded.VWETB` |
| Vanilla Weapons Expanded – Frontier | `VanillaExpanded.VWEFT` |
| Vanilla Furniture Expanded – Production | `VanillaExpanded.VFEProduction` |
| Vanilla Base Generation Expanded | `VanillaExpanded.BaseGeneration` |
| Vanilla Cooking Expanded – Stews | `VanillaExpanded.VCookEStews` |
| Vanilla Ideology Expanded – Icons and Symbols | `VanillaExpanded.Ideo.IconsandSymbols` |
| Vanilla Vehicles Expanded – Upgrades | `OskarPotocki.VanillaVehiclesExpandedUpgrades` |
| Adaptive Primitive Storage | `Adaptive.PrimitiveStorage` |
| [sbz] Neat Storage · Gravship Storage | `sbz.NeatStorage`, `sbz.GravshipStorage` |
| Animal Feed Trough (Continued) | `Mlie.AnimalFeedTrough` |
| ETRT: Tribal Apparel (continued) | `ETRT.TribalApparel` |
| Rustic Workbenches | `SereQ.RusticWorkbenches` |
| Advanced Pollution Pump · Faster Moisture Pump | `Bart.APP`, `Kangel.Moisture` |
| Filth Vanishes With Rain And Time · No Alzheimer's | `FrozenSnowFox.…`, `willworkforicecream.NoAlzheimers` |
| ATH's style Gothic and Bloody Gothic | `anthitei.athsstylegothic.style` |
| ATH's styles Norse | `anthitei.athsstylenorse.style` |
| ATH's style Draconic | `Anthitei.ATHsStyleDraconic.Style` |
| **Tavern** | `ODs.Tavern` — hard `modDependencies` on VEF; ~27 of its 30 concrete buildings are `techLevel` Undefined (`PARTS-BIN.md` §15) |
| **AI Upscaled Textures – Core** | `AIRetexture.Core` — 6,760 textures, 196 MB, and **not one def, patch or assembly** **[V]**. Pure path-shadowing over the base game and DLCs, DLC-gated by `loadfolders.xml`, so the Anomaly folder never loads. Declares Harmony under `modDependencies` and then ships no code. |
| **Vanilla Pawns Retextured** | `neronix17.hd.pawns` — 246 textures plus 7 patch files, all cosmetic: `graphicData` / `renderNodeProperties` on the Biotech eye and horn genes and graphic attributes on the furskin `HeadTypeDef`s. **[V]** |

**Cheap (34)** — an assembly, no settings surface. Enable plus a `PatchOperation`
where wanted.

| Mod | packageId |
|---|---|
| Vanilla Factions Expanded – Classical | `OskarPotocki.VFE.Classical` |
| Vanilla Factions Expanded – Tribals | `OskarPotocki.VFE.Tribals` |
| Vanilla Quests Expanded – Ancients | `vanillaquestsexpanded.ancients` |
| RimFantasy – Medieval Overhaul Edition | `Sierra.RF.MedievalOverhaul` |
| Dark Ages: Beasts and Monsters · Crypts and Tombs · Medieval Tools | `Van.Beasts`, `Van.DACrypts`, `Van.DATools` |
| Uncompromising Tribal Faction | `Fuu.UncompromisingTribalFaction` |
| Vanilla Furniture Expanded (+ Farming, Medical, Security, Spacer) | `VanillaExpanded.VFECore`, `…VFEFarming`, `…VFEMedical`, `…VFESecurity`, `…VFESpacer` |
| Vanilla Armour Expanded · Apparel Accessories · Chemfuel Expanded | `VanillaExpanded.VARME`, `…VAEAccessories`, `…VChemfuelE` |
| Vanilla Landmarks Expanded · Outposts Expanded | `VanillaExpanded.VExplorationE`, `vanillaexpanded.outposts` |
| VPE – Hemosage · VPE – Puppeteer | `VanillaExpanded.VPE.Hemosage`, `…VPE.Puppeteer` |
| Vanilla Races Expanded – Android | `vanillaracesexpanded.android` |
| Vanilla Races Expanded – Waster | `vanillaracesexpanded.waster` |
| World Tech Level | `m00nl1ght.WorldTechLevel` |
| More Realistic Research | `sae.ResearchMod` |
| Multiplayer | `rwmt.Multiplayer` |
| EdB Prepare Carefully | `EdB.PrepareCarefully` |
| Pharmacist: Represcribed · Milky Way · Architect Icons | `Fluffy.Pharmacist`, `Andromeda.MilkyWay`, `com.bymarcin.ArchitectIcons` |
| More Gravship Workbenches · [sbz] Fridge | `LTS.MGW`, `sbz.NeatStorageFridge` |
| ATH's Styleable Framework | `Anthitei.ATHsStyleableFramework.Style` |
| Fix Styled Blueprints | `kathanon.FixStyledBlueprints` |
| **Vanilla Races Expanded – Genie** | `vanillaracesexpanded.genie` — the cleanest assembly in the bin at 9.7 KB: no threading, no `WorldComponent`, no `GameComponent`, **no `ModSettings` and no RNG of its own** **[V]**. Two `IngestionOutcomeDoer`s and one `InternalDefOf`; the only draw is vanilla `IngestionOutcomeDoer.chance`, taken on the ingestion tick and therefore synced. Its price is a def-surface one, not a code one — see Named prices. |

**Cheap + settings (62)** — Cheap plus a **managed condition**: per
`CODING_STANDARDS.md`, `config/ModSettings/` is part of the sync surface. Copy the
file; never re-click it. This is a rule to follow, not a defect to fix.

| Mod | packageId |
|---|---|
| Vanilla Expanded Framework | `OskarPotocki.VanillaFactionsExpanded.Core` |
| Multiplayer Compatibility · Harmony · Prepatcher · HugsLib | `rwmt.MultiplayerCompatibility`, `brrainz.harmony`, `zetrith.prepatcher`, `UnlimitedHugs.HugsLib` |
| Medieval Overhaul · MO: Adaptive Storage | `DankPyon.Medieval.Overhaul`, `EEG.MOxASF` |
| VFE – Medieval 2 · Empire · Deserters · Pirates · Settlers · Insectoids 2 | `OskarPotocki.VFE.*`, `…SettlersModule` |
| VRE – Archon · Starjack · Sanguophage · Hussar · Saurid | `vanillaracesexpanded.*` |
| Vanilla Psycasts Expanded | `VanillaExpanded.VPsycastsE` |
| Vanilla Ideology Expanded – Memes and Structures | `VanillaExpanded.VMemesE` |
| Vanilla Gravship Expanded Ch.1 · Biotech for Gravship · GravTech | `vanillaexpanded.gravship`, `als.biotechgravship`, `als.gravtech` |
| Vanilla Vehicles Expanded | `OskarPotocki.VanillaVehiclesExpanded` |
| Ignorance Is Bliss · Lemmy Progression | `dame.ignorance`, `LemmyMods.LemProgression` |
| Faction Customizer · Sensible Factions · Xenotype Spawn Control | `azravos.factioncustomizer`, `Boots.SensibleFactions`, `bs.xenotypespawncontrol` |
| Faction Territories and Vassalage · Worksites Expanded | `jaeger972.factionterritories`, `godsfathermixtape.worksitesexpanded` |
| Better Traders Guild · Ushankas Glittertech · Alpha Mechs | `shunter.bettertradersguild`, `Ushanka.GlittertechExpansion`, `sarg.alphamechs` |
| VFE Power · Props and Decor · Nutrient Paste · Non-Lethal | `VanillaExpanded.VFEPower`, `…VFEPropsandDecor`, `…VNutrientE`, `…VWENL` |
| Vanilla Apparel Expanded · Cooking Expanded · Fishing Expanded | `VanillaExpanded.VAPPE`, `…VCookE`, `…VCEF` |
| Vanilla Animals Expanded – Waste Animals | `VanillaExpanded.VAEWaste` |
| Adaptive Storage Framework · [SYR] Processor Framework · Map Mode Framework | `adaptive.storage.framework`, `syrchalis.processor.framework`, `NozoMe.MapModeFramework` |
| Replace Stuff · Pick Up And Haul · Compositable Loadouts | `Memegoddess.ReplaceStuff`, `Mehni.PickUpAndHaul`, `Wiri.compositableloadouts` |
| Tribal Furniture · Tribal Siege Raids · TakeCover · Vanilla Combat Reloaded | `Xercaine.Tribal.Furniture`, `PJerri.TribalSiegeRaids`, `rabiosus.TakeCover`, `Donald.VCR` |
| Better Architect Menu · Architect Menu Optimizer | `ferny.BetterArchitect`, `MRK.architectmenuoptimizer` |
| [SR] Factional War (fork) | `SR.ModRimworld.FactionalWarContinued` |
| **RimPacts – Diplomacy Overhaul** | `wowgag.RimPacts` |
| **Slave Rebellions Improved (Continued)** | `Mlie.SlaveRebellionsImproved` — no threads, no `WorldComponent` **[V]**, but both settings floats are read *inside* rebellion logic, so mismatched files produce different rebel rosters from the same tick. Transpiles `SlaveRebellionUtility.IsRebelling`. |
| **Auto-Cast Specialist Commands** | `Linnun.AutoCastSpecialistCommands` — no threads, no `WorldComponent` **[V]**. **The heaviest settings dependency in the bin, by kind rather than by size:** six bools that decide whether a *toil is inserted into a vanilla `JobDriver`*. See Named prices. |
| **Better Workbench Management** | `falconne.BWM` — no threads **[V]**; two `WorldComponent`s (`ExtendedBillDataStorage`, `WorktableRestrictionDataStorage`) that only persist bill metadata. Three of its seven settings are read inside a `RecipeWorkerCounter.CountProducts` detour. See Named prices. **A second settings defect, on a different method from the count-setting one:** `ImprovedWorkbenches.Detours.BillUtility_MakeNewBill_Detour.Postfix` calls `Main.Instance.ShouldDropOnFloorByDefault()` → `ModSettings_ImprovedWorkbenches._dropOnFloorByDefault` **[V]**, and the add-bill delegate is replayed on every client, so two players with different settings write different `storeMode` onto the same scribed bill — **T-18**, live. MP transmits the map selection as command context for that delegate, which rescues the postfix's other divergent read (`Find.Selector.SingleSelectedThing`); nothing restores a mod setting. The assembly declares no `[HarmonyPriority]`/`HarmonyBefore`/`HarmonyAfter` anywhere **[V]**. See [#95](https://github.com/cjd721/Rimworld-Archinity/issues/95). |
| **QualityBuilder Unofficial 1.6** | `hatti.qualitybuilder` — no threads, no `WorldComponent` **[V]**. **The only mod in this batch the compat layer covers**, and it covers the commands, not the defaults path. See Named prices. |
| **Defensive Positions – Forked** | `GonDragon.DefensivePositions` — no threads **[V]**: every `Thread` hit in the assembly is the compiler-generated `<>l__initialThreadId` of an iterator, and the one `Task` hit is `MessageTypeDefOf.TaskCompletion`. Its four settings are hotkey and camera behaviour only. **Its orders are MP-safe with no patch of any kind** — see the dedicated section below, which corrects an earlier claim in this file. |
| **Range Finder** | `brrainz.rangefinder` — settings are display-only (modifier keys, colours, max draw range) and steer nothing synced **[V]**. Tiered here for the rule, not for a hazard. Its assembly question is separate and is recorded below. |

> **Arithmetic.** 130 mods on disk. **Five are ours** (Origins, Pacing, Drifters,
> Glitterites, Altar) and are not subject to the admission bar, leaving **125
> third-party**. Three distinct mods are out — Rim War (barred *and* declined),
> Elves and Dwarves (declined) — so the **in** set is **122**, tiered Free 24 / Cheap 34 /
> Cheap+settings 62 / Real 2 = 122. Real is carved *out of* Cheap+settings, not
> added to it — an earlier revision counted Vehicle Framework and TechBlock twice.
> The two mods Conrad declined in [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8)
> session 2 are still inside those tier counts, which is why the section heading says
> **120** and this block says 122.

### Real (2) — counted separately from Cheap+settings, not in addition to it

| Mod | The price |
|---|---|
| **Vehicle Framework** `SmashPhil.VehicleFramework` **[V]** | The only mod besides Rim War with real thread-creation machinery: `SmashTools.Performance.DedicatedThread` runs `new Thread(Execute){IsBackground=true}` + `Start()`, and `Vehicles.DeferredGridGeneration` enqueues **vehicle pathing-grid and region generation** onto it — simulation off the synced tick. **Corrected in full by [#69](https://github.com/cjd721/Rimworld-Archinity/issues/69): there is no flag to set, and the previous version of this row was wrong in three independent ways.** ① **"a scribed bool defaulting `true`" — false.** `Vehicles.SectionDebug.debugUseMultithreading` has its `Scribe_Values.Look` **behind `DebugProperties.Debug`, a `readonly bool = false`**, and the field has **no settings UI**. It never scribes and a player cannot reach it. **There is no lever.** **[V]** ② **The `ReleaseThread()` path, as this row described it — false.** **[V]** ③ **"every enqueue site takes its synchronous fallback" — false**, and this is the load-bearing one. `Vehicles.VehiclePathFollower.RequestNewPath` and `Vehicles.WorldVehiclePathGrid.RecalculateAllPathCostsAsync` reach **`SmashTools.TaskManager.Run` — a bare `Task.Run`** — **from the synced tick**. That path is not the `DedicatedThread` and is not gated by `ThreadAvailable` at all, so no setting of that flag would have covered it. MP Compat's `NoThreadInMp` transpiler covers only **3 of 8 `ThreadAvailable` readers**. **[V]** **A second, independent race:** `Vehicles.VehicleRegionCostCalculator.pathCostSamples` is a `private static int[11]` **written from the async task** — shared mutable static state reached off the synced tick, with no lock and no per-map instance. **[V]** Traps: `docs/TRAPS.md` **T-74** / **T-75**. **Price: a fork or real Harmony work in our own assembly, not a settings flag.** [#17](https://github.com/cjd721/Rimworld-Archinity/issues/17) priced this mod on the struck row and that pricing is void; whether vehicles are available to the campaign at all is re-opened, not settled. |
| **TechBlock** `fridgeBaron.TechBlock` **[V]** | Verified against `1.6/Assemblies/TechBlock 1.2.1.dll`, which is what actually loads — an earlier revision of this file read the `1.0` build by mistake. `TechBlock_Component.GameComponentUpdate()` runs **per frame** (`Game.UpdatePlay` → `GameComponentUtility.GameComponentUpdate`, confirmed in `Assembly-CSharp`), and inside it: `AddRandomProgress()` calls `GenCollection.RandomElement(techLevelProjects)` — **a draw from the shared `Rand` stream taken outside the synced tick** — then `Find.ResearchManager.AddProgress(val, 25f * settings.randomInsightRate)`, writing synced sim state scaled by a client-local setting, with the whole branch gated on client-local `settings.randomInsights`. **Correction to an earlier claim in this file:** it is *not* simply "progress diverges with frame rate" — the component accumulates `savedProgress` and only draws per 25 points, so the draw *count* tracks research, not frames. The decisive defect is the **interleaving position**: a `Rand` draw taken from a per-frame method enters the shared stream at a frame-dependent point, so two clients diverge even with identical settings and identical draw counts. Matching settings files therefore does **not** fix it. Fork-and-recompile, or a Harmony prefix. Owned by [#7](https://github.com/cjd721/Rimworld-Archinity/issues/7). |

### RimPacts — the §14 open item, closed **[V]**

`wowgag.RimPacts` (`3762723122`), *RimPacts – Diplomacy Overhaul*. `PARTS-BIN.md` §14
has asked for this decompile since the last pass, because it bears on the faction-demands
question (§10.3). Done.

**Not barred.** No `ThreadStart`, no `ThreadPool`, no `IsBackground`, no
`System.Threading.Thread`. Everything runs in `WorldComponentTick`, which is synced.
**Tier: Cheap + settings.**

**But it is the largest shadow world in the bin, by a distance.** One class,
`WorldComponent_RimPacts`, decompiles to **33,715 lines**; the assembly carries 623
types including `ActiveTreaty`, `PendingConquest`, `RptCoalitionStats`, `RptBorderMap`,
`PlayerCourt`/`CourtMember`/`CourtRecord`, `RptForcedBattleManager`, a counter-spy
subsystem, and its own chronicle (`RptChronicle` — unrelated to ours, but a name
collision worth knowing about).

**The managed condition here is unusually heavy.** `RimPactsSettings` has **57 fields**,
and they gate `Rand` paths *inside the ticking component* — `if (RimPactsMod.Settings.enableDynamics)`
wrapping code that then calls `Rand.Chance`, plus `startAsEmpireTributary`,
`enemySpyDetectNoBureau` and others in the same shape. That is §3.1's dominant hazard
at full scale: two clients with different settings draw a **different number of values
from the shared stream**, and the whole diplomatic sim diverges from there. Identical
settings files are not a nicety for this mod, they are the entire safety story.

**So the decision is a design decision, not a safety one**, and it belongs to
[The faction pressure prototype](https://github.com/cjd721/Rimworld-Archinity/issues/13),
which owns the RimPacts whole / fork / ours question — with the vassalage half at
[Vassalage and the tithe catalogue](https://github.com/cjd721/Rimworld-Archinity/issues/35).
Weigh it
against the campaign's refusal of a parallel world simulation — the stated reason faction-sim
mods are perpetually beta is that they maintain a parallel world model, and this is
one, ticking synced or not. Against that: it is the only thing in the bin that
already implements treaties, vassalage, tribute and a humiliating peace, which is
close to what [religion and politics](../requirements/RELIGION.md#political-pressure) asks the political board to do.

**Added on [#131](https://github.com/cjd721/Rimworld-Archinity/issues/131) [V]:**

- **Multiplayer Compat carries no class for it.** `RimPacts` and `wowgag` return zero hits in both
  encodings across `1629973374/1.6/**`, `Referenced/` included. The sweep was validated in the same
  dll by `vanillaracesexpanded.android` (ASCII) and `VREAndroids` (UTF-16).
- **It creates factions at runtime** in two places: the civil-war split
  (`ResolveCivilWarSplit` → `FactionGenerator.CreateFactionAndAddToManager(mother.def)`) and the
  player's puppet (`Rpt_Puppet_*` defs). Both conflict with the campaign's no-new-faction rule (T-07's
  requirement), which is conflict cargo.
- **Its civil war is the corpus's only faction-revolt system**:
  - eligibility in `CivilWarEligible`, which excludes `categoryTag` Empire, orbital and puppet factions;
  - a `Rand.Chance(0.08 × a stability factor)` in `TryStartCivilWarQuarter`;
  - resolution after 1,200,000 ticks into quelled, coup (`TryGenerateNewLeader`) or split;
  - a 7,200,000-tick cooldown after any outcome;
  - a player-initiated *Incite rebellion* spy op.

  It has no player-joined fight.

### Range Finder — the one place this batch touches the bar **[V]**

`brrainz.rangefinder` (`1332119637`). **Not barred, and the reasoning matters more than
the verdict**, because a literal reading of the bar would bar it.

**Threads exist.** Its `LoadFolders.xml` maps `v1.6` to `/` and `1.6`, and the root
`Assemblies/RangeFinder.dll` — a stale 36 KB legacy build, distinct from the 21 KB one
in `1.6/` — carries six `new Thread((ThreadStart)delegate …).Start()` sites. Separately,
`1.6/Assemblies/CrossPromotion.dll` embeds two more assemblies as manifest resources
(`Brrainz.CrossPromotionSteam.dll`, `…SteamDeck.dll`) which it loads by
`Assembly.Load(byte[])`, and those carry `FetchPromotionMods` and `ThreadStart` too.

**But every one of those threads belongs to Pardeike's Steam Workshop cross-promotion
widget**, not to Range Finder. They are started from `MainMenuDrawer.Init` and from the
`Page_ModsConfig` screen; they fetch UGC details, preview images and vote status, and
they write to `promoMods` and `allVoteStati`. **They cannot run during a session and
they touch no game state** — there is no game when they fire. The bar exists to stop us
inheriting simulation that runs off the synced tick; this is a mod-list decoration.

**Range Finder itself is inert.** The 1.6 build is three Harmony patches —
`SelectionDrawer.DrawSelectionOverlays`, `MainTabsRoot.HandleLowPriorityShortcuts`,
`Map.FinalizeLoading` — drawing range rings under a held modifier key. No `WorldComponent`,
no `GameComponent`, no writes to anything.

**The one thing to actually do:** confirm which `RangeFinder.dll` the game loads. Both
directories are in the v1.6 path and only the stale build contains the threading and the
`MultiVersionModFix` Harmony patch on `ModMetaData.VersionCompatible` — a patch that
**rewrites which mods the game considers version-compatible**, which is not something to
inherit unknowingly on a pinned set. This is a launch-log check, not a decompile, and it
is in Open below.

### Defensive Positions – Forked — the author's two claims, verified **[V]**

`GonDragon.DefensivePositions` (`3550360467`). The fork advertises two changes: the
**HugsLib dependency removed**, and **the section that required a Multiplayer patch
deleted**. Both are literally true, and the second is architecturally justified rather
than a removal of safety.

**The dependencies are genuinely gone.** The assembly references only `0Harmony`,
`Assembly-CSharp`, `mscorlib`, `UnityEngine.*` and `System.Core`. There is **no
`Multiplayer.API` surface and no HugsLib surface** — not one `MP.`, `SyncMethod`,
`RegisterSync`, `SyncField`, `SyncWorker` or `IsInMultiplayer` string anywhere in it —
and `About.xml` declares no `modDependencies` at all.

**It does not need them, because it routes orders through methods Multiplayer already
syncs.** The fork issues every move through `JobDriver_DraftToPosition`, a real
`JobDriver`, started by `Pawn_JobTracker.TryTakeOrderedJob`. Multiplayer registers that
method itself — `SyncMethod.Register(typeof(Pawn_JobTracker), "TryTakeOrderedJob")
.SetContext(…).ExposeParameter(0)` **[V]** — and also registers
`Pawn_DraftController.Drafted` **[V]**, which covers the undraft-all hotkey. The drafting
and the `Goto` / `ManTurret` order both happen *inside the job's toil*, on the synced
tick. Both entry points qualify: MP's `InInterface` is
`Client != null && !Ticking && !ExecutingCmds && !reloading && ProgramState == Playing`,
which is satisfied during gizmo processing *and* during `MapComponentOnGUI`, so
`ShouldSync` is true for the button and for the keypad hotkeys alike. The in-toil calls
run with `Ticking` true, so they execute normally instead of re-syncing.

> **Correction.** An earlier revision of this file said DP "issues draft and position
> orders straight from gizmos and a `KeyBindingDef` … an unsynced order moves pawns on
> one client only," and made that the reason for a smoke test. **That was wrong.** The
> orders are synced, by vanilla registrations, with no DP-specific patch and no compat-layer
> entry. Struck. This is the better architecture, not a missing one — a mod that needs no
> MP-specific code cannot have its MP-specific code rot.

**What the deleted section does not cover is the *stored* state, and that is the real
price.** `DefensivePositionsMapComponent.ExposeData` scribes the saved positions and the
squads into the save, and `DefensivePositionsWorldComponent` scribes the advanced-mode
flag and ferries both across gravship moves. Four writers touch that data and **none goes
through a vanilla synced method**:

| Writer | How it is reached |
|---|---|
| `SetDefensivePosition` → `SetPosition` | straight from `HandleControlInteraction`, during gizmo processing |
| `DiscardSavedPosition` | same path, ctrl-click |
| `ScheduleAdvancedModeToggle` | sets client-local `modeSwitchScheduled`; applied in `MapComponentTick` |
| `ReassignSquadMembers` / `ClearSquad` | `mapComponent.pawnSquads.Add` / `.Remove`, from the hotkey `OnGUI` path |

The third deserves naming because **it looks like a fix and is not.** Deferring the write
to `MapComponentTick` puts it on the tick but synchronises nothing: `modeSwitchScheduled`
is set on the clicking client only, `MapComponentTick` runs on both, so exactly one client
applies the toggle.

**None of this can desync the game, and that is precisely what makes it worth writing
down.** Multiplayer's detector compares **`Rand` state only** — `mapRandomStates`,
`worldRandomStates`, `commandRandomStates` **[V]** — and not one of those four writes
touches `Rand`. Meanwhile the data's *consequences* are all funnelled back through synced
jobs: the clicking client reads its own handler, computes a cell, and issues a job
carrying that cell **explicitly**, which both clients then execute identically. So the
simulation stays consistent and the detector stays silent while **each player quietly
accumulates their own set of defensive positions and squads** — and on the next save-and-reload
only the host's survive.

That is a **loudness** failure, not a divergence one. Under `CODING_STANDARDS.md`'s second
gate it is the shape to distrust most: nothing in the game, and nothing in Multiplayer,
will ever report it.

**Price, and it is optional.** Three `MP.RegisterSyncMethod` calls from `Archinity.Core` —
on `SetPosition`, on the squad add/remove pair, and on the advanced-mode toggle — make the
stored state shared. All are reachable by `AccessTools` on public types; no fork, no
transpiler. **Tier is unchanged at Cheap + settings**: the mod is fully playable without
them, with per-player positions as the quirk. Do it only if shared positions are wanted.

### Named prices already known

Carried from `PARTS-BIN.md` rather than re-derived. None of these changes a tier;
each is a specific thing to do when the mod ships.

| Mod | What to do |
|---|---|
| `vanillaracesexpanded.starjack` | `starjackGenesAmount` drives the **number of `Rand` draws** per pawn — settings must match. |
| `vanillaracesexpanded.hussar` | Settings determine the **GeneDef count at load** — settings must match. |
| `vanillaracesexpanded.saurid` | `replacesFaction` **deletes a vanilla faction**. Patch it out before worldgen. |
| `vanillaracesexpanded.waster` | Rewrites the vanilla Waster xenotype; `Rand` in a render path. |
| `vanillaracesexpanded.android` | Patches the **abstract** outlander and pirate bases, so it bleeds unless scoped. Its `AndroidSettings.xml` is the model for Def-based tunables. |
| `azravos.factioncustomizer` | **Pre-worldgen use only.** `Rand`-heavy, zero MP sync, and it *cannot* remove factions. |
| `DankPyon.Medieval.Overhaul` | Unkeyed schematic cache is a genuine desync bug — strip the `RequiredSchematic` extension from the 14 projects and the postfix returns immediately. Also the Map-Gen settings trap: copy the file, never re-click. |
| `VanillaExpanded.VPsycastsE` | Viewport-gated RNG in three places — **fixed by the compat layer**, which is the strongest single argument for enabling it. |
| `VanillaExpanded.VMemesE` | Unseeded `new Random()`. |
| `vanillaexpanded.outposts` | Reflection writes settings **onto live instances** at load. |
| `m00nl1ght.WorldTechLevel` | ~45 `[HarmonyPrepare]` toggles ⇒ clients get **different patched methods**. Settings file is save-critical. |
| `Xercaine.Tribal.Furniture` | Four settings read inside `PatchOperation.ApplyWorker` ⇒ one client has a ThingDef the other does not. |
| `OskarPotocki.VFE.Empire` | `Rand.Chance(… * Settings.deserterChanceMult)` in pawn-group generation. |
| `Ushanka.GlittertechExpansion` | `FormingSpeedMultiplier` in `BillTick()`; pylon mood multipliers. |
| `vanillaexpanded.gravship` | `maintenanceLossMultiplier` in `TickInterval()`. Audit Biotech for the unseeded gene `Rand` before use. |
| `vanillaracesexpanded.sanguophage` | `drainCasketAmount` consumed in a tick. |
| `syrchalis.processor.framework` | `initialProcessState` in `CompProcessor.Initialize()` ⇒ every processor spawns with a different enabled set. |
| `adaptive.storage.framework` | The **only natively MP-aware mod** in the bin. Nothing to do. |
| `rwmt.MultiplayerCompatibility` | **Not hygiene — it is the carrier for a live silent desync fix.** Its `VanillaExpandedFramework.PatchKCSG` transpiles the unseeded `System.Random` in `KCSG.SettlementGenUtils.Sampling.Sample` into a `Verse.Rand` redirector: **`docs/TRAPS.md` T-33**, the hazard on every `SettlementLayoutDef` path. Beyond that one patch it carries 33 `PatchSystemRand` sites, 41 `PatchPushPopRand` sites and 224 `[MpCompatFor]` package ids, **21 of which are mods on disk**. It is the single highest-leverage entry in the shipping set for multiplayer, and it costs nothing to author. **Its protection is a hardcoded per-mod allowlist, not a general mechanism** — anything else in the set, and anything we write, gets no coverage. **[V]** ([#88](https://github.com/cjd721/Rimworld-Archinity/issues/88)) |
| `Andromeda.NiceBillTab` | **New candidate, absent from every earlier survey — silence, not rejection.** It carries the *finding* half of the bill-menu problem (search box, sigil category filters, collapsible `ThingCategoryDef` tree) by replacing `ITab_Bills` wholesale: its `FillTab` prefix returns `false` while `Settings.EnabledMod` and the vanilla add-bill `FloatMenu` ceases to exist. **Two prices.** (1) **MP-hostile as it stands** — zero `Multiplayer`/`SyncMethod` references in 8,949 decompiled lines, and its reorder/insert paths write `billStack.Bills.Insert/Remove` **directly**, bypassing the `BillStackAddPatch`/`DeletePatch` that MP core syncs **[V]**; the desync consequence is **[I]**, unverified against two clients. (2) `Settings.EnableAutoNaming` is read inside `TryAddBillToQueue` and writes `Bill_Production.RenamableLabel`, which is **scribed game state** — settings must match. Zero tech-level awareness. **[V]** ([#87](https://github.com/cjd721/Rimworld-Archinity/issues/87)) **Amended by [#95](https://github.com/cjd721/Rimworld-Archinity/issues/95), and it does not soften the verdict above:** on the *creation* path specifically, `NiceBillTab.TabBillsDrawer.TryAddBillToQueue` calls `BillUtility.MakeNewBill(recipe, selection.style)` itself and adds the result, so with the tab loaded MP's `SyncDelegate.Lambda(typeof(ITab_Bills), "FillTab", 2)` never fires and bill *creation* rests entirely on the `BillStack.AddBill` SyncMethod **[V]**. That one path is covered; the reorder/insert paths in (1) are a different seam and remain uncovered. It also mutates the bill **after** `billStack.AddBill` — `SetMaterialToBill` rewrites `ingredientFilter`, `AutoRenameBill` under its own setting — **a seam no Harmony priority on `MakeNewBill` reaches** **[V]**. Workshop `3520130671`, `1.6/Assemblies/NiceBillTab.dll`. |
| `ferny.betterarchitect` | **PULL with a caveat, and its era resolver is worth harvesting regardless.** `MysteryUnlockTracker : GameComponent` scribes `baMysteryUnlocks` and is mutated from two asymmetric sources — a synced game event (`ResearchManager.FinishProject`) **and a purely local UI click** (`ClearPendingFor`, when a player reveals a wrapped gizmo). RimWorld instantiates every `GameComponent`, so this is live whether or not the feature is on; mitigation is `mysteryUnlocks = false`. **[V]** on the mechanism, **[I]** on save divergence. Separately it **conflicts silently with Architect Menu Optimizer** (`MRK.architectmenuoptimizer`): BAM's `DesignationTabOnGUI` prefix returns `false` unconditionally, so AMO's transpiler never runs and its pagination is a no-op — and AMO's BAM-compat shim never installs, because it looks up a property `Settings` where BAM exposes a static field `settings`. Cargo, not a verdict. **T-22 is live for both.** **[V]** ([#87](https://github.com/cjd721/Rimworld-Archinity/issues/87)) |
| `Linnun.AutoCastSpecialistCommands` | **The worst settings dependency in the bin, and it is not close.** Five postfixes on `MakeNewToils` — `JobDriver_Mine`, `JobDriver_DoBill`, `JobDriver_PlantWork`, `JobDriver_Research`, `JobDriver_StudyInteract` — each call `AutoCastToilInjector.Inject(…, settings.enableAutoCastX)`, which returns immediately if the bool is false and otherwise **inserts a toil into the job's toil list** that calls `ability.verb.TryStartCastOn`. Every other settings hazard in this file changes a *value*; this one changes the *length and indexing of a pawn's toil list*. **The mechanism, stated precisely** (confirmed while verdicting Defensive Positions): Multiplayer syncs the `Job` — `TryTakeOrderedJob` is a registered SyncMethod with the job exposed — but each client then reconstructs the **toil list locally** by calling `MakeNewToils`. So a settings-gated toil injection makes two clients execute *different toils from the same synced job*, and the sync layer has no way to notice: it delivered the job correctly. Not covered by the compat layer. Settings must match, and this is the mod to check first if a desync appears. **[V]** |
| `falconne.BWM` | `_countOutsideStockpiles`, `_countInventory` and `_countCarriedByNonHumans` are read inside a detour on `RecipeWorkerCounter.CountProducts` (plus a `GetCarriedCount` transpiler). That count is what decides whether a "do until X" bill is satisfied — so mismatched settings mean one client's bill completes and the other's keeps issuing jobs. Not covered by the compat layer. Settings must match. **[V]** |
| `hatti.qualitybuilder` | **Partly fixed for us, and know which part.** MP Compatibility ships `[MpCompatFor("hatti.qualitybuilder")]` and sync-registers `CompQualityBuilder.ToggleSkilled` and the two quality float-menu lambdas — the *player commands*. It does **not** touch the two paths that read settings inside game logic: `CompQualityBuilder.PostSpawnSetup` seeds `skilled` and `desiredMinQualityRef` on every non-reloaded blueprint from `getDefaultUseQualityBuilder(map)` / `getDefaultMinQualitySetting(map)`, and `getBestConstructionSkillCached` recomputes the best builder's skill on a **`Stopwatch` with a 10-second wall-clock window** — wall-clock time is on the divergence list by name. Settings must match; the map-level override in `QualityBuilder_MapComponent` is saved and so is safe, but it falls back to the client-local global whenever `useMapSettings` is false. **[V]** |
| `GonDragon.DefensivePositions` | Settings are inert (hotkey mode, shift behaviour, group radius, camera jump). Orders are synced by vanilla registrations and need no patch. **The price is the stored positions and squads, which are not** — three optional `MP.RegisterSyncMethod` calls if we want them shared. See the dedicated section below. **[V]** |
| `vanillaracesexpanded.genie` | **Rewrites the vanilla `Genie` xenotype in place** — the Waster shape. `GenieXenotypePatch.xml` adds nine genes (`VRE_Hemophiliac`, `VRE_Immunity_VeryWeak`, `VRE_WoundHealing_VerySlow`, `VRE_AptitudePhenomenal_Crafting` and others) and removes `AptitudeRemarkable_Crafting`. Also patches Saurid and Alpha Genes. Free of code hazards; the cost is that a vanilla xenotype no longer means what the base game says it means. **[V]** |

---

## What this pass changes

1. **One mod is barred out of 125 third-party, and three are declined.** The bar is not a filter
   that removes work — it removes almost nothing, and that *is* the finding. What
   actually shapes the set is cost and taste, and taste is recorded here only when
   Conrad has stated it.
2. **The bar reduces to one testable question: does it create threads.** A world sim
   on the synced tick is deterministic; disliking it is a decline, not a bar.
3. ~~**Vehicles are available**, at one settings flag.~~ **STRUCK by
   [#69](https://github.com/cjd721/Rimworld-Archinity/issues/69).** The flag is not
   settable and would not have covered the two `Task.Run` paths anyway — see the Real
   tier row. **Vehicles are neither blocked nor cheap: they cost a fork or a real
   Harmony patch**, and nothing here decides whether they ship.
4. **The real cost of the set is its settings surface.** 65 of the 130 mods on disk carry
   one, so `config/ModSettings/` is save-critical across **exactly half** the build and
   [#18](https://github.com/cjd721/Rimworld-Archinity/issues/18) must snapshot it as a
   single artifact. The QoL batch sharpened this rather than adding to it: a settings
   surface is not a cost, it is a cost *multiplier*, and the thing to grade is what the
   settings reach. Range Finder has four and reaches nothing; Auto-Cast Specialist
   Commands has six and reaches the toil list.
5. **Saurid and Waster are cheap to drop if #8 wants to.** `PARTS-BIN.md` blocked both
   under the pre-#3 reasoning, but under the current bar neither is barred — both are
   patchable. So they are **in and undecided**, routed to
   [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) like every other want
   question. Recorded only because the cost of dropping them is unusually low: two
   `MayRequire` gene lines in `Archinity.Origins` (`VRESaurids_Pheromones`,
   `VRE_Instability_Extreme`) plus an over-declared `<modDependencies>` block, and
   Origins' own description already says missing sources degrade gracefully.

## Wanted, decided

Recorded here only because Conrad has said so — the rule above still holds.

| Mod | packageId | Decision |
|---|---|---|
| Tribal Siege Raids | `PJerri.TribalSiegeRaids` | **In, and it needs work.** [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) session 2: its `TribalCatapultSiege` is the only siege strategy in the bin that bypasses `FactionDef.canSiege` and gates on Neolithic \|\| Medieval — but its `selectionWeightPerPointsCurve` is `(0,0)(2000,0)(3000,0.4)(5000,0.75)(10000,1)`, **zero weight below 3000 threat points**, so it must be re-curved into band. A `canSiege` `PatchOperation` onto the Medieval load-bearing factions and an authored medieval siege blueprint set go with it. |

---

## What the 2026-09-11 capability batch found

Nine capability tickets resolved in parallel, then each re-verified against the 1.6
assemblies by an independent adversarial pass. Recorded here only where a finding bears on
a **verdict** — the mechanisms themselves live in `docs/specs/` and `docs/engine/`, and the
silent failures in `docs/TRAPS.md`. Nothing below changes a bar or a decline.

**One mod on disk has no entry in this file at all.**

| Mod | packageId | Why it now needs one |
|---|---|---|
| **Mechanoids: Total Warfare** | `nyar.nclvstw` (`3555799437`, snapshot row 121) | `NCLWorm.Verb_WormDeathRay.BurstingTick` draws `UnityEngine.Random.Range` **on the synced tick, in combat simulation** [V], and it is **not** on MP Compat's `PatchUnityRand` allowlist — so the divergence is real and, per **T-51**, the transpiler will not report it. No threads, so it does not touch the bar; the price is one `PatchUnityRand` entry or a ~10-line transpiler if the mod ships. It also holds the corpus's lowest `analysisID` (`007`), which is **T-41** territory. ([#94](https://github.com/cjd721/Rimworld-Archinity/issues/94), [#67](https://github.com/cjd721/Rimworld-Archinity/issues/67)) |

**Three notes against mods already tiered.**

- **VFE Settlers** — `VFE_Settlers.JobGivers.JobDriver_PlayFiveFingerFillet.WatchTickAction`
  draws `UnityEngine.Random` on the synced tick and, on the random branch, calls
  `TakeDamage` and `skills.Learn` [V]. It **is** covered by MP Compat
  (`Multiplayer.Compat.VanillaFactionsSettlers` binds that exact method). Recorded because
  it is the corpus's only covered Unity-RNG site, and therefore the evidence that
  `rwmt.MultiplayerCompatibility` is load-bearing for more than T-33.
  ([#94](https://github.com/cjd721/Rimworld-Archinity/issues/94))
- **VFE Empire** — `VFEEmpire.WorldComponent_Hierarchy` reads `Settings.noblesPerTitle`
  inside `WorldComponentTick` → `RefreshPawns` → `FillTitles` → `MakePawnFor` →
  `PawnGenerator.GeneratePawn` [V]. A mod setting steering **pawn generation on the synced
  tick** is a heavier instance of the settings-surface cost than anything in the QoL batch —
  this is the shape point 4 above is about, at its worst. **T-18.**
  ([#53](https://github.com/cjd721/Rimworld-Archinity/issues/53))
- **Vehicle Framework** — `Vehicles.RoadCostHelper.GetRoadMovementDifficultyMultiplier`
  (**two `RoadDef` overloads**, one taking `List<VehicleDef>` and one `List<VehiclePawn>`; the
  latter is the live-caravan path) takes `RoadDef.movementCostMultiplier` as a base and lets
  `VehicleDef.properties.customRoadCosts` **replace** it per road def — the **first declaring
  vehicle wins, in either direction**. It is **not** a floor and not "lower winning" [V].
  Not a bar question; it means any road-tier ladder we ship is silently bypassable per
  vehicle — **T-87**, and 14 of VVE's 23 vehicles flatten all five tiers through
  `AssignDefaults`. VF also **publishes the fix**: `Vehicles.CustomCostDefModExtension` is a
  supported pure-XML override hook, which is what
  `docs/specs/WORLD-INFRASTRUCTURE.md` § 4c selects. Handed to
  [#69](https://github.com/cjd721/Rimworld-Archinity/issues/69).
  ([#68](https://github.com/cjd721/Rimworld-Archinity/issues/68); *"undercut … lower winning"*
  corrected 2026-09-12 against `3014915404/1.6/Assemblies/Vehicles.dll`, 1.6.4871)

**Three collisions this batch tripped over.** Per `docs/agents/capability-research.md`,
**conflicts are cargo, not verdicts** — they are filed against the mod here and change no
tier and no bar. All three are the same shape: two pieces of code claiming the same seam,
with nothing in the game reporting the overlap.

| Collision | What it is | Why it is cargo |
|---|---|---|
| **Mechanoids: Total Warfare** — `NCL_Storyteller.Patch_StorytellerUtility` | **Transpiles `RimWorld.StorytellerUtility.DefaultThreatPointsNow`** [V], injecting an additive term into the returned points and **replacing the hardcoded `10000f` ceiling**. Both edits are inside the method body. | `DefaultThreatPointsNow` is the pacing seam the campaign is most likely to patch, and `PARTS-BIN.md` §8.1's `fixedWealthMode` finding feeds it. **A postfix of ours on that method would read a number this transpiler has already rewritten** — no error either way. If both ship, the two edits must be reconciled deliberately. ([#60](https://github.com/cjd721/Rimworld-Archinity/issues/60)) |
| **Ushanka's Hacking Expansion** — `USH_HE.Patch_CompHackable_CanHackNow` | A **postfix on `RimWorld.CompHackable.CanHackNow(Pawn)`** [V], which is how it lets a remote hacker past vanilla's `"NoPath"` refusal. | The research-gate build proposed for [#58](https://github.com/cjd721/Rimworld-Archinity/issues/58) postfixes **the same method**, so our refusal and its permission would sit side by side **with Harmony ordering unspecified**. Proven shape, shared seam — decide the order explicitly rather than discovering it. ([#58](https://github.com/cjd721/Rimworld-Archinity/issues/58)) |
| **Mechanoids: Total Warfare** — `NCL.CompProperties_UnlockResearch` on vanilla `CerebrexCore` | Added to the **vanilla Odyssey `CerebrexCore` ThingDef by `PatchOperationAdd`** [V]. `NCL.CompUnlockResearch.UnlockResearch` calls `ResearchManager.FinishProject`, which **recursively completes every unfinished prerequisite**, and grants Spacer `NCL_CerebrexCore_Rebuild` — **`baseCost` 5000, no prerequisites**. | **A cascading research bypass attached to a def the campaign does not own.** It is not a defect in the mod and not a bar question; it is a collision between MTW's content and any era gate, and the disposition (a `PatchOperationRemove` of that `li`) is [#83](https://github.com/cjd721/Rimworld-Archinity/issues/83)'s, recorded in `docs/specs/RESEARCH.md`. |

**A method caveat that touches every negative in this file.** The wide-pass technique this
repo prescribes for the UTF-16LE half — `rg -a --encoding utf-16le` — **silently misses
strings that are provably present**, non-uniformly. Two auditors reproduced it
independently on different files. Every negative in the 2026-09-11 batch survived
re-derivation by a null-interleaved byte scan, but the *stated* validation was false in at
least three tickets, and negatives recorded here before that date were swept the same way.
**And the replacement has its own failure mode:** a null-interleaved pattern built through a
shell `$(…)` substitution degrades to a plain ASCII search, and its validator degrades with
it, so a re-derivation is only as good as the bytes that reached ripgrep — which is why
`docs/agents/capability-research.md` now requires a sweep's *construction* to be reported
with its result. [#103](https://github.com/cjd721/Rimworld-Archinity/issues/103),
[#83](https://github.com/cjd721/Rimworld-Archinity/issues/83).

## What the 2026-09-12 capability batch found

Ten capability tickets resolved in parallel, each re-verified against the 1.6 assemblies by an
independent adversarial pass. Same rule as the batch above: recorded here only where a finding
bears on a **verdict** or on a mod's price. Nothing below changes a bar or a decline, and
**conflicts are cargo, not verdicts**.

**Every mod this batch touched already has an entry.** Nice Bill Tab's findings are folded into
its existing row in § *Named prices already known*, which #87 filed as **MP-hostile** — this batch
covers a different seam and does not soften that.

**Rows amended, by mod.**

**Compositable Loadouts** — `Wiri.compositableloadouts` (`2679126859`,
`1.6/Assemblies/Inventory.dll`) — the only loadout mod in the corpus. Its `Loadout`/`Tag` are
`IExposable` on a `GameComponent`, **not Defs**, so it ships no authorable preset content **[V]**.
It is the only thing in the corpus that reaches weapons from a preset
(`Inventory.ThinkNode_LoadoutRealisation` issues `JobDefOf.Equip`) **[V]**.
**Live T-18 on the simulation path.** `Inventory.OptimizeApparel_ApparelScoreGain_Patch` postfixes
`JobGiver_OptimizeApparel.ApparelScoreRaw` and returns `-1000f` when
`ModBase.settings.onlyItemsFromLoadout` is set and the pawn's `LoadoutComponent` does not desire the
item; `Inventory.OptimizeApparel_TryGiveJob_Patch` transpiles `TryGiveJob` to drop apparel outside
the loadout on the same setting **[V]**. Both read mod settings inside AI that ticks on every client
— unlike Better Workbench Management's, there is no synced-command context to rescue it. **With that
setting on, any apparel-policy-driven equipment scheme stops working**, Archinity's presets
included. Also transpiles `BillRepeatModeUtility.MakeConfigFloatMenu` to inject a mod-defined
`BillRepeatModeDef` **[V]** (adds an option; does not remove vanilla's `CanCountProducts` gate).
([#28](https://github.com/cjd721/Rimworld-Archinity/issues/28),
[#95](https://github.com/cjd721/Rimworld-Archinity/issues/95))

**Vanilla Expanded Framework** — `OskarPotocki.VanillaFactionsExpanded.Core` (`2023507013`).
**Ships a purchasable quest catalogue with a pluggable currency**, not merely a board: `QuestGiverDef` / `QuestCurrency` / `QuestCurrencyInfo` /
`QuestInfo` / `QuestGiverManager` / `QuestWorker` / `Window_Contracts`, held by
`GameComponent_QuestChains`, with `GoodwillCurrency` as a shipped subclass debiting through
`TryAffectGoodwillWith` **[V]**. Extending it to a new currency is two small subclasses.
`QuestGiverManager.ActivateQuest` is reached from `OnGUI` and needs one sync registration **[V]**.
Carries **T-76** and **T-77**. **The outpost engine is also VEF's**, not Vanilla Outposts
Expanded's: `Outposts.dll` ships inside VEF and carries `Outposts.Outpost : MapParent`, the
`OutpostExtension`, production, delivery and packing, plus the abstract `WorldObjectDef`
`OutpostBase`; `VEF.dll` itself contains **zero** `Outpost` types, so a sweep of `VEF.dll` for
outposts returns a false negative **[V]**.
([#106](https://github.com/cjd721/Rimworld-Archinity/issues/106),
[#81](https://github.com/cjd721/Rimworld-Archinity/issues/81))

**Vanilla Outposts Expanded** — `vanillaexpanded.outposts` (`2688941031`,
`1.6/Assemblies/VOE.dll`) — **not a donor for a player-planted institution inside an NPC faction**,
and it contains no *outpost* engine of its own (see VEF above). Placement is structurally barred
from NPC territory: `Outposts.Utils.CanSpawnOnWithExt` rejects the tile when
`Find.WorldObjects.AnySettlementBaseAtOrAdjacent(tile)`, and `Dialog_CreateCamp` calls
`outpost.SetFaction(creator.Faction)` — the player's. No goodwill cost, no standing gate, no host
faction, no suppression. And it is a `MapParent`, which
[#10](https://github.com/cjd721/Rimworld-Archinity/issues/10) already priced. **Multiplayer
Compatibility does not cover it** — the whole of `Multiplayer.Compat.VanillaOutpostsExpanded` is two
lines, and a whole-assembly byte scan of `1.6/Assemblies/Multiplayer_Compat.dll` finds **zero**
`Outposts.` references **[V]**; counts and the full correction are in `docs/data/PARTS-BIN.md`
§ 7.6. **[V]**
([#73](https://github.com/cjd721/Rimworld-Archinity/issues/73),
[#81](https://github.com/cjd721/Rimworld-Archinity/issues/81))

**Lemmy Progression** — `LemmyMods.LemProgression` (`3548896697`,
`1.6/Assemblies/LemProgress.dll`). **BLOCK, on three independent defects [V]:**

① **It writes the volatile mirror and never the scribed field.**
`LemProgress.Systems.WorldEraManager.SetWorldTechLevel` calls `InitializeWorldTechLevelAccess()` —
which is where the reflection lives, a four-tier fallback starting at `AccessTools.TypeByName` —
and then does one `cachedCurrentField.SetValue(null, level)` inside a try/catch. That is the
assembly's **only** `FieldInfo.SetValue` call site, and the string `GameComponent_TechLevel` does
not appear anywhere in the assembly in **either** metadata heap. So WTL's scribed state is never
touched and the raise is discarded on the next load — see
`docs/engine/research-and-tech-tiers.md` § *The scribed field and the volatile mirror are two
different things*.

② **`System.Random` in the faction-upgrade half — two instances, one of them live.** Both
`LemProgress.Systems.FactionUpgradeManager` and `LemProgress.Systems.FactionUpgrader` declare a
`private static readonly System.Random random`. **`FactionUpgrader.random` is dead** — it is read
nowhere in the assembly, and `FactionUpgrader` draws through `GenCollection.RandomElement` instead.
The live site is `FactionUpgradeManager`'s: `random.NextDouble() < settings.factionUpgradeChance`.
One unseeded stream off the shared `Rand` stream is enough; the count is two, the defect is one.

③ **A settings-window write to saved state.** `LemProgress.Settings.LemProgressMod.DrawAdvancedSettings(Rect)`
draws *"Force Tech Level Advance"* through `Listing_Standard.ButtonText`, reached from
`DoSettingsWindowContents` only via `case SettingsTab.Advanced:` and only when `Current.Game != null`;
the handler is `ForceAdvanceTechLevel()`, which opens the `FloatMenu` whose options call
`WorldEraManager.AdvanceToTechLevel(level)` — **T-18**'s shape on top of ①.

Also prefixes VFE Tribals' `AdvanceToEra` and returns **`true`**, observing that mod's polling era
detector and pushing WTL's level alongside it — *amplifying* the detector rather than suppressing
it. Worth copying, though: `InitializeWorldTechLevelAccess` handles the auto-property correctly in
four steps (`AccessTools.Field` → `AccessTools.Property` → `<Current>k__BackingField` → a
static-field scan).
([#109](https://github.com/cjd721/Rimworld-Archinity/issues/109))

**Faction Territories and Vassalage** — `jaeger972.factionterritories` (`3626725895`,
`Assemblies/FactionTerritories.dll`, no source) — **the closest structural precedent in the corpus
for a player-planted object inside an NPC faction**, and not the donor. `VassaliseUtility` gates on
`faction.PlayerGoodwill < GetSettlementVassaliseGoodwillCost()` (clamped 10–100) with a
*"Requires N goodwill with …"* reason guarded by `Faction.CanChangeGoodwillFor`, then **spends** the
standing via `TryAffectGoodwillWith(Faction.OfPlayer, -cost, …)` **with a `+cost` rollback on
failure** — the rollback is the detail to copy. `FactionTerritories_VassalOutpost : WorldObject` — a
plain `WorldObject`, not a `MapParent` — is placed by `ExecuteVassalisationAtTile` **at the NPC
settlement's own tile** with `SetFaction(Faction.OfPlayer)`, retaining `originalFactionId`,
`originalFactionLoadID`, `originalSettlementName` and `originalWorldObjectDefName`.
`VassalagePointsComponent : GameComponent` accrues the yield; `Invasions.Component` scans
`GetAllOutposts()` and spawns an `Invasion` against them — a real suppression loop. **Rejected as
donor on two grounds:** it *converts* an existing (or destroyed) settlement rather than planting
beside a living one, so the placement half is new work regardless; and ⚠ its cost comes from a
`ModSettings` slider — **T-18**. Already recorded as a `DrawFactionRow` patcher claiming the row's
right-edge 80px. **[V]** ⚠ Its invasion half carries a second T-18:
`Invasions.Component.GameComponentTick` reads `FactionTerritoriesSettings.enableInvasions` — a
**public field**, so it cannot be Harmony-prefixed — and `RollNextInvasionTick` draws
`Rand.Range(...)` off the **shared stream** with both bounds derived from per-client settings, so a
client with the setting false never takes the draw at all **[V]**. Its `Utility.RollWinner` is by
contrast better than merely safe: the winner is a pure function of tile, both faction load IDs and
the tick, under `Rand.PushState(seed)` with a `finally { Rand.PopState(); }` **[V]**. MP Compat
covers the packageId **nowhere** — a validated sweep across all 18 `Multiplayer_Compat*.dll` builds
returns zero **[V]**.
([#73](https://github.com/cjd721/Rimworld-Archinity/issues/73),
[#92](https://github.com/cjd721/Rimworld-Archinity/issues/92),
[#93](https://github.com/cjd721/Rimworld-Archinity/issues/93))

**The vassalise prompt is unsyncable as shipped [V].** `ShowVassalisePromptOnMapRemovedPatch`
postfixes `MapDeiniter.Deinit`, opens a modded `ChoiceLetter_VassaliseDestroyedSettlement`
(**T-96**) and calls `Find.TickManager.Pause()`. `InterceptBaseDestroyedLetterPatch` prefixes
`SettlementDefeatUtility.CheckDefeated`. `ExecuteCedeToFactionAtTile` recreates a
`WorldObjectDefOf.Settlement` for a recipient faction — the donor for handing a ruin back to an NPC
faction. ([#120](https://github.com/cjd721/Rimworld-Archinity/issues/120))

**VFE Empire** — `OskarPotocki.VanillaFactionsExpanded.Empire`. `WorldComponent_Hierarchy`, named on
[#73](https://github.com/cjd721/Rimworld-Archinity/issues/73) as the nearest analogue for a
per-faction ledger, **is not one**. Its state is `List<Pawn> TitleHolders` plus a `bool initialized`,
scribed `LookMode.Reference` — a roster of generated nobles, not a per-faction record of anything
the player placed. Its `WorldComponentTick` (daily, at `TicksGame % 60000 == 2500`) calls
`Rand.Chance` and `Rand.RangeSeeded` and generates world pawns whose *count* comes from
`VFEEmpireMod.Settings.noblesPerTitle`, a client-local slider — **T-18**, and
`Multiplayer.Compat.VanillaFactionsEmpire` patches neither `WorldComponentTick` nor `RefreshPawns`
nor `MakePawnFor`. ⚠ **The ticket's "147 lines" is the 1.4 `Source/` file, not the 1.6 assembly**
— the exact failure `docs/agents/capability-research.md` § *Stale source* names.
`WorldComponent_Vassals` + `TitheInfo` (a `Dictionary<Settlement, TitheInfo>` scribed
Reference→Deep, lazily decorating an existing Empire settlement) is the nearer analogue and has
**no suppression path at all** — nothing can raid, contest or reduce a vassal. The only
non-debug caller of `ReleaseAllVassalsOf(Pawn)` is the Royalty tab's *Release all* confirmation
button; nothing releases a vassal on title loss or when its settlement falls **[V]**. **Neither VFE Empire nor VFE Deserters references
`Multiplayer`, `SyncMethod` or `SyncWorker` anywhere**: both assemblies reference only mscorlib,
Assembly-CSharp, UnityEngine and 0Harmony (plus KCSG for VFED). **[V]** — **but the vassals are synced from outside.** `Multiplayer.Compat.VanillaFactionsEmpire`
(`1629973374/1.6/Referenced/Multiplayer_Compat_Referenced.dll`, `[MpCompatFor("OskarPotocki.VFE.Empire")]`)
reroutes vassalising through `[SyncMethod] SyncedVassalizeSettlement`, registers
`RoyaltyTabWorker_Vassals.DoVassal` lambdas 2–4, syncs `WorldComponent_Vassals.ReleaseAllVassalsOf`,
and wraps `GetTitheInfo` in `Rand.PushState(Gen.HashCombineInt(settlement.ID, tile))` **[V]**.
Residual [I]: `DoDay` iterates a `Dictionary<Settlement, TitheInfo>` minted lazily from the tab's
draw path, so insertion order can differ per client while each delivery draws `Rand` — RUN item on
[#120](https://github.com/cjd721/Rimworld-Archinity/issues/120).
([#73](https://github.com/cjd721/Rimworld-Archinity/issues/73))

**What the vassal system is, in 1.6 [V]:**
- **Empire only.** `AllPossibleVassals` filters `Settlement.Faction == Faction.OfEmpire`.
- **Held by a titled pawn.** `VassalUtility.VassalagePointsAvailable` sums `vassalagePointsAwarded`
  down the title chain (seven Empire rungs award 1, one awards 0) minus vassals held. Reach is 100
  tiles from a player home or a held vassal.
- **Catalogue drawn at random.** `GetTitheInfo` picks a random `TitheTypeDef` and a
  weighted-random speed (0.5×–2.5×).
- **Delivered only where the lord is.** `TitheWorker.DeliverInt` delivers into the lord's caravan
  (refused over mass capacity) or by drop pod near the lord on a player home map; otherwise nothing.
- **Seven `TitheTypeDef`s, not six**, the seventh being `VFEE_Slavery` (Ideology): `TitheWorker_Slaves`
  generates a new `PawnKindDefOf.Slave` pawn as the player's slave every 10 days.

XML reaches the catalogue and the title points, never which factions can be vassals.
([#120](https://github.com/cjd721/Rimworld-Archinity/issues/120))

**Rim War** — `2222935097`, `v1.6/Assemblies/RimWar.dll`. Player heat is stored **per settlement**:
`RimWar.Planet.RimWarSettlementComp.playerHeat`, a private `int` scribed `"playerHeat"`, clamped
0–10000 in its setter [V]. `RimWarData.PlayerHeat` is a derived aggregation over those comps, not
the store. **It does have a readout** — `RW_AggressionPoints` and `RW_AggressionDefense` (with a
`vassalHeat` variant) are appended to a settlement's inspect string; both literals live in the `#US`
heap only, so an ASCII-only sweep misses them [V]. No band ladder and no world-scoped meter. Its one
reusable idea is pacing: on firing an action, `PlayerHeat = 0; minimumHeatForPlayerAction +=
GetHeatForAction(...)` — spend heat and raise the bar, so the next strike costs more. Verdict
unchanged: **barred and declined**.
([#56](https://github.com/cjd721/Rimworld-Archinity/issues/56))

Its "vassal" is not a mechanism: `RimWar.Planet.WorldUtility.IsVassalFaction` is
`f.def.defName == "PColony"` **[V]**. ([#120](https://github.com/cjd721/Rimworld-Archinity/issues/120))

**Ushanka's Glittertech Expansion** — `3522676478`. `_instability` is on
**`USH_GE.Hediff_CryogenicNexus : Hediff_AddedPart`** — a pawn hediff — as a private `float` scribed
`"_instability"`, clamped 0–1, with `ResetInstability()` and `LabelInBrackets` showing
`CurStage.label` and `(1 - Instability) × 100%` [V]. `USH_GE.CompOverclock` does not carry it.
Banded by hediff stage, not by a Def threshold; **not** a world meter. Ruled out for
[#56](https://github.com/cjd721/Rimworld-Archinity/issues/56). Separately, it **prefixes
`RimWorld.BillUtility.MakeNewBill`** and returns `false` for its own recipes, substituting
`USH_GE.Bill_ModifyCell : Bill_Production`, `Bill_Glittertech : Bill_Autonomous` and
`Bill_Overclock : Bill_Glittertech` [V] — so any bill-defaults postfix must allowlist types rather
than test `is Bill_Production`. Cite the **1.6** assembly specifically,
`3522676478/1.6/Assemblies/GlittertechExpansion.dll`; the 1.5 build is a differently named
`GlitterworldUprising.dll` carrying one of the three branches [I].
([#56](https://github.com/cjd721/Rimworld-Archinity/issues/56),
[#95](https://github.com/cjd721/Rimworld-Archinity/issues/95))

**RimPacts – Diplomacy Overhaul** — `wowgag.RimPacts` (`3762723122`, `Assemblies/RimPacts.dll`, no
version folder; About declares 1.6 only). **Verdict unchanged: not barred; Cheap + settings; the
whole/fork/ours question is [#13](https://github.com/cjd721/Rimworld-Archinity/issues/13)'s.** Three
findings against the dedicated section above, all **[V]**:

- **The only shipped faction-level vassalage in the corpus [V].** `Rpt_Treaty_Tribute` makes a whole
  NPC faction the player's tributary (`WorldComponent_RimPacts.IsMyTributary`).
  - `TreatyWorker_Tribute.WouldAccept` gates on a power ratio and `Submission` (military collapse,
    economic pressure, diplomatic vulnerability, shocks) — not on anything religious.
  - `OnSigned` enforces non-aggression.
  - `OnQuarter` either pays via `DeliverTributeQuarter` (silver, or the faction's settlement
    specialties, at `Find.AnyPlayerHomeMap`'s trade drop spot) or rolls `Rand.Chance` for a revolt
    that breaks the treaty and may schedule a revenge raid.
  - `OnBroken` by the player gives +10 goodwill and a 1,800,000-tick cooldown.

  ⚠ **`CreatePuppet` calls `FactionGenerator.CreateFactionAndAddToManager` mid-game** — the
  **T-07** / **T-15** shape. `RimPacts.dll` contains no "multiplayer" string in either encoding, and
  MP Compat covers no RimPacts packageId or type literal. Donor for `docs/specs/TERRITORY.md` §3 R4,
  not a carrier. ([#120](https://github.com/cjd721/Rimworld-Archinity/issues/120))

- **The corpus's only other world-scoped player heat meter.**
  `WorldComponent_RimPacts.playerNotoriety`, an `int` scribed `"playerNotoriety"`, 0–100. Decay is
  `((PlayerIdeoLeader() != null) ? -3 : -2) × DoctrineNotorietyDecayMult` per day in
  `ProcessNotorietyDaily`, **not a flat rate**. `AddPlayerNotoriety(int, string)` is the main but
  **not the only** write site — at least three places clamp `playerNotoriety` directly, including an
  inline settlement-raze path. The band threshold is read through `DoctrineHegemonThreshold`,
  doctrine-dependent and able to return 90, not a bare constant; `RptTuning` holds the defaults
  (`NotorietyMax 100`, `NotorietyHegemonThreshold 80`, `NotorietyHegemonEndBelow 60`, with
  hysteresis). Displayed as one colour-flipping label row in `MainTabWindow_RimPacts`; escalates
  through `EnterPlayerHegemon` → `FormAntiPlayerCoalition` → `DeclareCoalitionWar`. Gated on
  `RimPactsMod.Settings.enableNotoriety` — **T-18**. **Design reference, not code reference**, and it
  confirms that VFED's Def-driven bands are the better shape.
  ([#56](https://github.com/cjd721/Rimworld-Archinity/issues/56))
- **The corpus's only def-level standing gate.** `RimPacts.TreatyDef : Def` with `minTrust`,
  `minGoodwill`, `silverCost`, `durationDays`, `breakTrustPenalty`, `breakGoodwillPenalty`,
  `TreatyDef requiresTreaty`, `empireAllowed`, enforced by `RimPacts.TreatyWorker.CanSign(...)`
  returning a vanilla `AcceptanceReport` with the threshold substituted into its reason string,
  softened by 10 at leader favour ≥ 60. Shipped ladder: NonAggression −20 / trust 20 / 300 silver →
  Passage 0/15 → Trade +10/30 → Defense +40/50 (requires NonAggression) → Alliance +75/60. Recorded
  because the *shape* is the one `docs/specs/POLITICS.md` § *Standing as a content gate* proposes,
  independently arrived at. ([#93](https://github.com/cjd721/Rimworld-Archinity/issues/93))
- **A `Missionary` operation**: send the moral guide away for seven days at a silver cost for a roll
  to convert the faction's ideoligion, moving goodwill either way; tunables `MissionaryCost`,
  `MissionaryCooldownDays`, `MissionaryBaseChance`, `MissionarySuccessGoodwill`,
  `MissionaryFailGoodwill`, `MissionaryFavorBonus`, `MissionaryTechPenalty` in `RimPacts.RptTuning`.
  **It is the transaction half of a mission with none of the institution half** — no persistent
  object, no decay offset. **[V]** on the symbols, **[I]** on the numbers.
  ([#73](https://github.com/cjd721/Rimworld-Archinity/issues/73))
- **It postfixes `CompShuttle.IsAllowed`** (`RimPacts.Patch_ShuttleAllowMech`), flipping
  `false→true` only for player mechanoids on its own combat-dispatch ships, and returning early when
  the result is already true. **No collision** with a founder-refusing postfix (#134's route C2):
  it never re-admits a humanlike. The consequence runs the other way. Such a refusal also keeps
  founders off RimPacts' own dispatch shuttles. [V]
  ([#134](https://github.com/cjd721/Rimworld-Archinity/issues/134))

**A sweep hazard that touches every negative in this file, added to the method doc.** Ripgrep is
case-sensitive and C# identifiers are not written the way you type them: `notoriety` returns
**zero** over both roots while `Notoriety` returns RimPacts. It splits **both** metadata heaps
identically, because the cause is the pattern rather than the encoding. See
`docs/agents/capability-research.md` § *Searching what the mods actually ship*.
([#56](https://github.com/cjd721/Rimworld-Archinity/issues/56))

## What the 2026-09-15 reopened batch found

Three reopened capability tickets — [#53](https://github.com/cjd721/Rimworld-Archinity/issues/53),
[#54](https://github.com/cjd721/Rimworld-Archinity/issues/54) and
[#68](https://github.com/cjd721/Rimworld-Archinity/issues/68) — re-resolved against changed
requirements, each adversarially audited. Same rule as above: recorded only where a finding bears on
a verdict or a mod's price, and **conflicts are cargo, not verdicts**. No bar or decline moves.

**VFE Empire** — `OskarPotocki.VanillaFactionsExpanded.Empire` (`2938820380`). **T-18 reconfirmed on
the 1.6 decompile**: `WorldComponent_Hierarchy` reads `VFEEmpireMod.Settings.noblesPerTitle` inside
the daily `WorldComponentTick` → `RefreshPawns` → `MakePawnFor` → `PawnGenerator.GeneratePawn` chain
**[V]**. Under the in-place Church build it follows the Church unchanged and brings that defect with
it. `docs/specs/RELIGION.md` § *Persistence and multiplayer* § *Exaltation*. ([#53](https://github.com/cjd721/Rimworld-Archinity/issues/53)) Its 1.6 `QuestNode_Root_GrandBall`, `QuestNode_Root_RoyalParade` and `Questnode_Root_ArtExhibit` gate acceptance on a specific player colonist, the most senior titled host, through vanilla `QuestPart_RequirementsToAcceptPawnOnColonyMap`. It is the corpus's only mod use of that part, and it is C#. [V] ([#134](https://github.com/cjd721/Rimworld-Archinity/issues/134))

**VFE Deserters** — `oskarpotocki.vfe.deserters` (`3025493377`, `1.6/Assemblies/VFED.dll`). Seven
findings **[V]**, none changing its standing:

- `VFED.HarmonyPatches.MiscPatches` — `CheckBiosecurity`, a postfix on `WorkGiver_Open.HasJobOnThing`,
  and a `FloatMenuOptionProvider_OpenThing.GetSingleOptionFor` postfix — refuses to open a
  `Building_CrateBiosecured` unless the pawn has a backstory whose `spawnCategories` contains
  `"ImperialRoyal"`. Renaming Royalty's backstory categories silently locks the crates.
  ([#53](https://github.com/cjd721/Rimworld-Archinity/issues/53))
- `ContrabandManager.TryGiveExtension`, run from its static constructor over every `ThingDef`,
  auto-registers each def carrying `CompProperties_Techprint` as Intel-priced stock — so if VFED
  ships, every techprint we author is on its shelf, outside `docs/specs/CURRENCIES.md`'s exchange
  and its exclusion postfix (**T-99**). ([#54](https://github.com/cjd721/Rimworld-Archinity/issues/54))
- **It is the hostile-branch techprint carrier, if it ships.** `VFED.GenStep_FlagshipRuins` places
  every Empire-tagged techprint **×3** from map generation, and `VFED.QuestNode_BetrayalRewards`
  calls `TechprintUtility.TryGetTechprintDefToGenerate_NewTemp` with the slate's `empire` faction —
  **tag-based, not hostility-gated** **[V]**. So a Church that has turned hostile still has a
  steerable Empire-tagged supply *only* while VFED is in the set.
  ([#53](https://github.com/cjd721/Rimworld-Archinity/issues/53))
- **Its Intel economy is keyed to the Empire, which is now the Church** **[V]**, and the ledger
  should price that: Intel is extracted from Empire-titled pawns (`VFED.CompIntelExtractor`'s
  validator is `pawn.royalty.GetCurrentTitle(Faction.OfEmpire) != null`) and dropped by
  `VFED.EmpireRaidLootMaker`, and the shop opens only after
  `VFED.WorldComponent_Deserters.JoinDeserters`, which force-hostiles `Faction.OfEmpire` via
  `GoodwillToMakeHostile` and strips titles. Adopting its economy therefore buys an anti-Church war
  as the precondition of buying anything. `docs/specs/CURRENCIES.md` § *Available mechanisms* §
  *Three Intel delivery options*. ([#54](https://github.com/cjd721/Rimworld-Archinity/issues/54))
- **Its contraband shop is multiplayer-synced, by Multiplayer Compatibility rather than by itself.**
  The note above — *neither VFE Empire nor VFE Deserters references `Multiplayer`, `SyncMethod` or
  `SyncWorker` anywhere* — is about their own assemblies and must not be read as "unsynced":
  `Multiplayer.Compat.VanillaFactionsDeserters` carries `SyncedPurchaseContraband`,
  `SyncedPurchaseContrabandRushedDelivery`, `SyncedPurchaseQuest`, `SyncedPurchaseService` and
  `SyncedAcceptPlot`. It lives **only** in `1629973374/1.6/Referenced/Multiplayer_Compat_Referenced.dll`,
  which is conditionally loaded (see `docs/agents/capability-research.md`), so a sweep that excludes
  `Referenced/` reports it absent. The sync is real but fragile: `PreDoPurchaseButton` dispatches on
  **translated button-text equality**, so a locale change breaks it silently. A balance debit we own
  and sync ourselves is strictly safer. ([#54](https://github.com/cjd721/Rimworld-Archinity/issues/54))
- **Its plot tab is a paid ordered chain — the only shipped one — and it is Medieval-unreachable as shipped.** `WorldComponent_Deserters.InitializePlots` builds the chain from `VFEEmpire.WorldComponent_Hierarchy.Titles` ≥ Knight, so it targets the Church hierarchy under the reskin. `DeserterTabWorker_Plots.DoMainPart` runs `TrySpendIntel(approach.intelCost, useCriticalIntel)` → `Choose` → `Accept`, and `MiscPatches.CheckForPlotEnd` (a `Quest.End` postfix) advances on `EndedSuccess` and regenerates the same step on `EndedFailed`/`EndedInvalid` **[V]**. Four things stand against it:
  - Commitment is fixed at accepting `VFED_ChasedDeserter`. While `Active`, `GoodwillPatches.CanChangeGoodwillFor_Postfix` freezes Empire↔player goodwill.
  - `VFED_EmpireBargain`, rolled after plot successes, carries `QuestPart_BetrayDeserters`, which sets `Locked` and ends every Deserter quest.
  - The network is reachable only as a comms-console target while `Active`.
  - Intel is counted only on powered orbital trade beacons. Both buildings require `MicroelectronicsBasics` **[V]**.

  MP Compat's `SyncedAcceptPlot` carries the plot accept through a call-site transpiler and an approach-index counter — not the button-text dispatch the contraband sync uses **[V]**. `docs/specs/CURRENCIES.md` § *The Schism catalogue — a spend that advances the plot*. ([#132](https://github.com/cjd721/Rimworld-Archinity/issues/132))
- **Its Intel extraction is not a destructive-analysis carrier** **[V]**.
  - `VFED.CompIntelExtract` is one fixed 3600-tick `WaitWith` (`JobDriver_ExtractIntel`), gated by
    a saved `intelExtracted` bool. It spawns `VFED_Intel` items whose count is the
    `DesertersMod.IntelFromExtraction` settings slider (**T-18**), and it does not consume the thing.
  - `VFED.CompIntelScraper` is the nearer shape: 10 pulses, each 3600 ticks, each a weighted
    random draw among Intel, Critical Intel, +Visibility or a quarter-strength Empire raid, then
    wick or destroy. But no colonist does any work.
  - Multiplayer Compatibility syncs both comps' gizmos (`Multiplayer.Compat.VanillaFactionsDeserters`,
    `Referenced/`).
  - `docs/specs/RESEARCH.md` § *Destructive artifact analysis*.
    ([#115](https://github.com/cjd721/Rimworld-Archinity/issues/115))

**RimPacts** — `wowgag.RimPacts` (`3762723122`). **Not an NPC road builder**, correcting #68's first
resolution. `WITab_RptTrade` sells a **player-financed** road from a player colony to any non-hostile
settlement — its only faction gate is `HostileTo(Faction.OfPlayer)` — bought in a confirmation
delegate after `RptSilverUtility.TryConsumeSilver`, with no sync; `ProcessRoadWorks` lays the **whole
path at `finishTick`** and then calls `SetAllLayersDirty()` **[V]**. Verdict unchanged; donor value
only. `docs/specs/WORLD-INFRASTRUCTURE.md` § *Available mechanisms*. ([#68](https://github.com/cjd721/Rimworld-Archinity/issues/68))

**Faction Territories and Vassalage** — `jaeger972.factionterritories` (`3626725895`).
`FactionTerritories.Vassalise.VassalRoadProgressComponent` mirrors Roads of the Rim construction
sites by reflection, is funded by `TryInvestRoadPoints`, and **writes no road** — no `OverlayRoad` or
`potentialRoads` in the assembly **[V]**; Roads of the Rim is on neither corpus root. **The mod stays
declined.** ([#68](https://github.com/cjd721/Rimworld-Archinity/issues/68))

**GravTech** — `als.gravtech` (`3545374124`). Adds **three** Empire + TradersGuild techprint
projects — `GravEngineBuild`, `GravForge`, `BlackHole_GT` **[V]**. They follow the Church under the
in-place transformation like every other Empire-tagged project, and because they are *also* held by
TradersGuild they survive Church hostility by a route the Royalty implants do not have.
`docs/specs/RELIGION.md` § *Verification* § *Exaltation*.
([#53](https://github.com/cjd721/Rimworld-Archinity/issues/53))

**Dwarves of the Rim** — `bean.customxenotypes.dwarvesoftherim` (declined). **A checked negative,
recorded so it is not re-derived:** it is one of only three mods on disk declaring `techprintCount`,
but its `heldByFactionCategoryTags` are **Mountainfolk** and **Hillfolk**, not Empire **[V]**, so it
neither adds to nor rescues the Empire-tagged supply. Verdict unchanged.
([#53](https://github.com/cjd721/Rimworld-Archinity/issues/53))

## What the 2026-09-16 capability batch found

**World Tech Level** — `m00nl1ght.WorldTechLevel` (`3414187030`, `1.6/Lunar/Components/WorldTechLevel.dll`).
`WorldTechLevel.Patches.Patch_IdeoFoundation.CanAdd_Postfix` (patch group `Filters`, gated on
`Settings.Filter_Ideoligions`) refuses any `PreceptDef` whose `MinRequiredTechLevel` exceeds
`WorldTechLevel.Current` **[V]**. It is the shipped donor for a progress gate on precept
availability. It is also cargo: while the filter is on, it hides any Archinity role def whose
derived tech level is above the world's from the editor, the reform dialog and generation. How
`TechLevelDatabase<PreceptDef>` derives that level is **[I]**. Direct `Ideo.AddPrecept` does
not pass through it **[V]**. ([#114](https://github.com/cjd721/Rimworld-Archinity/issues/114))

**Vanilla Ideology Expanded – Memes and Structures** — `VanillaExpanded.VMemesE` (`2636329500`).
Ships the corpus's meme-gated role defs (`requiredMemes`) and five `RoleRequirement` subclasses
**[V]**. `StatPart_Pattisier.Applies` keys on `Precept_Role.ChosenPawnSingle()`, which
`Precept_RoleMulti` returns as null, so that holder-keyed bonus pattern does not port to a
multi-holder role unchanged **[V]**. Its `IdeoUIUtility.AddPrecept` transpiler raises the
*ritual* cap only; nothing in the corpus lifts the two-multi-role cap **[V]**. Covered by
`Multiplayer.Compat.VanillaIdeologyMemes` (`[MpCompatFor("VanillaExpanded.VMemesE")]`) **[V]**.
([#114](https://github.com/cjd721/Rimworld-Archinity/issues/114))

**Vanilla Expanded Framework** — `2023507013`, `1.6/Assemblies/VEF.dll`.
`VEF.Memes.VanillaExpandedFramework_Ideo_ExposeData_Patch` is a transpiler on `Ideo.ExposeData`.
It locates the backfill's `Ideo.AddPrecept` call **[V]** and, by its shape, reroutes it to
`CheckIfCanAdd` **[I]**; the transpiler body did not decompile. `CheckIfCanAdd` adds a precept
only when `foundation.CanAdd` accepts and the def has `canGenerateAsSpecialPrecept` **[V]**.
Cargo: with VEF loaded, a missing hidden ritual that `CanAdd` refuses is probably no longer
backfilled **[I]**. ([#114](https://github.com/cjd721/Rimworld-Archinity/issues/114))

**RimPacts** — `wowgag.rimpacts` (`3762723122`, `Assemblies/RimPacts.dll`). The `Missionary`
operation's conversion is **label only**: `WorldComponent_RimPacts.ResolveMissionary` calls
`faction.ideos?.SetPrimary(player primary)` on `Rand.Chance(num)`. `num` is 0.1, +0.1 at leader favour
≥ 60, and −0.1 at `techLevel ≥ 4`. `EnsurePuppetIdeo` pins a puppet state's primary the same way. No
pawn converts and no minor is kept, so both arm **T-109** **[V]**. The chance is now [V]; the other
`RptTuning` numbers stay [I]. ([#133](https://github.com/cjd721/Rimworld-Archinity/issues/133))

**VFE Classical — the senators' "won-over government" [V]** (`2787850474/1.6/Assemblies/VFEC.dll`;
the shipped source is stale ⚠). When the last senator is won, `WorldComponent_Senators.GainFavorOf`:

- adds +1000 goodwill;
- sets `Permanent[faction]`;
- calls `faction.ideos.SetPrimary(Faction.OfPlayer.ideos.PrimaryIdeo)` — label only, keeping no minor, so it arms **T-109** ([#133](https://github.com/cjd721/Rimworld-Archinity/issues/133));
- nulls every one of the faction's `Settlement.cachedMat`.

Its constructor postfixes `Faction.GoodwillWith` (→ 100), `Faction.CanChangeGoodwillFor` (→ false)
and `Faction.RelationKindWith` (→ Ally) for permanent factions. **Conflict cargo:** any other patch
on those three methods, ours included, composes with a forced result.
Multiplayer Compat's `VanillaFactionsClassical` lives in `Referenced/` and patches its senator dialog buttons.

**Faction Customizer** — `azravos.factioncustomizer` (`3336572602`). `Dialog_ModifyFaction`, opened
from `FCDialog_FactionDuringLanding`, changes a faction's primary **and** `SetIdeo`s every world pawn of
that faction. It misses map pawns and keeps no minor **[V]**. Pre-landing and unsynced, consistent with
its existing entry. ([#133](https://github.com/cjd721/Rimworld-Archinity/issues/133))

**VFE Deserters** — `oskarpotocki.vfe.deserters` (`3025493377`). Three findings **[V]**, none
changing its standing:

- **Its finale ends the game and takes both factions with it.**
  `VFED.MapComponent_FlagshipFight.DamageFlagship`:
  - sets `Faction.OfEmpire` `defeated` and `hidden`, and the Deserters `defeated`
  - hands every Empire settlement to `TryGetRandomNonColonyHumanlikeFaction`
  - kills or re-factions every Empire pawn, and removes Empire titles and permits
  - calls `ShipCountdown.InitiateCountdown`
  
  Under the in-place Church that is the Church's destruction and the campaign's end.
- **It never reveals its faction.** The Deserters stay hidden. `JoinDeserters` sets them Ally
  through `SetRelationDirect`, which is legal only because a hidden faction has no goodwill.
  VFED's only faction `hidden` write is the finale's hide of the Empire.
- **Its commitment is a latch on the Church.** `HarmonyPatches.GoodwillPatches.CanChangeGoodwillFor_Postfix`
  refuses every player↔Empire goodwill change while `WorldComponent_Deserters.Active` is set.
  That freezes the Church at the −75 `JoinDeserters` wrote, below any suspicion cap.
  `VisibilityEffect_Goodwill` meanwhile drops a random faction's goodwill daily while `Active` is
  set. `BetrayDeserters` reverses the whole thing (+200 Church goodwill).

`docs/specs/RELIGION.md` § *The Schism*. ([#130](https://github.com/cjd721/Rimworld-Archinity/issues/130))

**VFE Empire** — `OskarPotocki.VanillaFactionsExpanded.Empire` (`2938820380`). Two findings **[V]**:

- **`VFEEmpire.GameComponent_Empire.GameComponentTick` rewrites the player↔`VFEE_Deserters`
  relation kind with `SetRelationDirect` every 6,000 ticks**, from Church hostility, Deserter
  hostility and whether any colonist holds a title. Inert while the faction is hidden. Once it is
  revealed, each call whose conditions hold is a `Log.Error` ("Tried to use SetRelationDirect for
  factions which use goodwill").
- **`VFEE_Deserters` sets VEF's gameplay-backfill fields under `MayRequire` VFE Deserters**
  (`docs/engine/factions-and-worldgen.md` § *The roster is authorable as defs*). The def is also
  `Ultra`, `hidden`, `fixedName Deserters`, `Sophian`, with `Collectivist` and `Loyalist` required.

([#130](https://github.com/cjd721/Rimworld-Archinity/issues/130))

**RimPacts** — `wowgag.RimPacts` (`3762723122`). **It gates the Ally relation on its own
declared alliances [V].** `Patch_RptAllianceDeclaredOnly` (prefix and postfix on
`FactionRelation.CheckKindThresholds`) demotes an Ally that `WorldComponent_RimPacts.IsDeclaredAlly`
does not list, for any diplomacy-listed faction. `LapseAllianceIfGoodwillFell` clears a declared
alliance at goodwill ≤ 0. A permanent ally we hold would be demoted to Neutral if RimPacts ships
undeclared. Verdict unchanged. ([#130](https://github.com/cjd721/Rimworld-Archinity/issues/130))

**VEF** — `oskarpotocki.vanillafactionsexpanded.core` (`2023507013`).
`VanillaExpandedFramework_Faction_NaturalGoodwill_Patch` replaces every faction's natural goodwill
whenever the active storyteller carries `storytellerThreat` (**T-115**) **[V]**. No corpus
storyteller sets it. ([#130](https://github.com/cjd721/Rimworld-Archinity/issues/130))

## What the 2026-09-23 capability batch found

Merged from the resolution and correction comments on #140, #141, #144, #146, #147, #148, #150,
#155, #166 and #169. Every mod below already has a tier row; these are amendments to it, not new
admissions. Evidence marks are the resolving agent's.

**Rows amended, by mod.**

**VFE Tribals** — `OskarPotocki.VFE.Tribals` (`3079786283`). The **end-to-end donor for a
campaign-forced player ideology**: a Harmony pair on `Page_ChooseIdeoPreset` (`PostOpen` /
`DoNext`), gated on the scenario's player faction def, handing the player `Page_ConfigureIdeo`
afterwards to author the rest **[V]**. Also the donor for a **custom player `FactionDef` carrying
`disallowedPrecepts`** (`3079786283/1.6/Defs/FactionDefs/Factions_Player.xml`) **[V]**, and for
the concealment pattern `visible false` + `classic true` + `countsTowardsPreceptLimit false` on
`VFET_PreceptBase` **[V]**. Note **T-15** and the stale-source warning still apply to this mod.
([#140](https://github.com/cjd721/Rimworld-Archinity/issues/140))

**VFE Pirates** — `OskarPotocki.VFE.Pirates` (`2723801948`). The donor for a **meme-enforced
precept floor**: its pirate meme authors multi-element `requireOne` sublists — `Raiding_Respected`
/ `Raiding_Required`, `VFEP_Camaraderie_Respected` / `VFEP_Camaraderie_Exalted` — the strict end
of each issue and nothing below it, which is the shape a campaign floor wants
(`1.6/Mods/Ideology/Defs/MemeDefs/Memes_Misc.xml`, second copy in the `Mods/` root — **T-22**)
**[V]**. ([#140](https://github.com/cjd721/Rimworld-Archinity/issues/140))

**Vanilla Ideology Expanded – Memes and Structures** — `VanillaExpanded.VMemesE` (`2636329500`).
Two additions to its existing row: it is the corpus's donor for mod **`IdeoPresetDef`s**, and it
is **the one mod that widens vanilla precepts' `requiredMemes`** — 12 XML patches, two of them on
`IdeoDiversity_Exalted` and `IdeoDiversity_Respected` **[V]**. That is cargo for any campaign
tolerance floor, because `Ideo.PreceptIsRequired` scans *every* meme's `requireOne`, so a widened
precept widens our legal set. It also authors single-element `requireOne` sublists — a hard forced
precept with no choice at all **[V]**.
([#140](https://github.com/cjd721/Rimworld-Archinity/issues/140))

**Vanilla Races Expanded – Android** — `vanillaracesexpanded.android` (`2975771801`). Its
`AndroidSettings` def is an **explicitly documented external-patch surface**: the def's own label
reads *"this def will have various settings used for androids. Can be used for mod compatibility
from outside via xml patches."* **[V]** `VREAndroids.AndroidSettingsExtension` on a `HediffDef`
gives a **per-hediff override with precedence over the list** — `Utils.AndroidCanCatch` checks the
extension first and short-circuits **[V]**, and VRE ships that exact operation shape itself on
`HediffDef[@Name="DiseaseBase"]` in `1.6/Patches/Core.xml` **[V]**. See
`docs/engine/psycasts-and-meditation.md` for the two independent psychic gates and for the
`displayCategory` hook that makes third-party android hardware pure XML.
([#141](https://github.com/cjd721/Rimworld-Archinity/issues/141))

**Better Traders Guild** — `shunter.bettertradersguild`. Carries **orbital settlement visiting,
orbital trade-request quests and shuttle trade** — and is **not covered by Multiplayer
Compatibility** **[V]**, swept ASCII and UTF-16LE with both forms validated. Anything the campaign
hangs on orbital trade through this mod is unsynced until we cover it.
([#147](https://github.com/cjd721/Rimworld-Archinity/issues/147))

**Vanilla Furniture Expanded – Security** — `vanillaexpanded.vfesecurity`. Sets
`planetLayerWhitelist: Surface` on its **manned turrets** and on the `CompProperties_WorldArtillery`
host **[V]**, so neither functions in orbit. Same gate vanilla puts on `Turret_Mortar`; see
`docs/engine/world-time-and-layers.md` § *Cross-layer budgets, gates and the selected layer*. The
lever is a `PatchOperationAdd` of `<li>Orbit</li>` — XML, Easy, **[I]** that the patch alone
suffices. ([#147](https://github.com/cjd721/Rimworld-Archinity/issues/147))

**VFE – Insectoids 2** — `OskarPotocki.VFE.Insectoid2`. **A live collision, recorded as cargo.**
`VFEInsectoids.PawnsArrivalModeWorker_CanUseWith_Patch` postfixes the arrival-mode check to return
**false for `Faction.OfInsects` on `EdgeDrop`, `CenterDrop`, `EdgeDropGroups` and `RandomDrop`**
**[V]**. All five orbit-capable arrival modes are drop modes, so **insectoids can never arrive at
an orbital home while this mod is loaded**, whatever the layer whitelists say. (The mod is already
declined on Conrad's call; this is why the negative would survive even if it were not.)
([#147](https://github.com/cjd721/Rimworld-Archinity/issues/147))

**Vanilla Gravship Expanded – Chapter 1** — `vanillaexpanded.gravship` (`3609835606`). Three
additions:

- **It is the corpus's dominant source of orbital `GeneratedLocationDef`s.**
  `3609835606/1.6/Defs/GeneratedLocationDefs/GeneratedLocations.xml` ships **10** (`VGE_IceAsteroids`
  … `VGE_DerelictStation`), against Odyssey's **1** (`Asteroids`) **[V]**. The figure is **ten**:
  #146 measured it two independent ways — open tags and `<defName>` elements, 10/10 — across both
  corpus roots plus `Data/`. *(An earlier incidental pass on #148 said four; that count was not
  taken over the whole file and is superseded.)* Every one targets `Orbit`, and
  `WorldComponent_LocationGenerator` budgets **per layer**, so the contention is an orbital-layer
  question. A second source of pre-reveal orbital objects — see **T-132**.
- **It patches the gravship travel path**: `InitiateTakeoff`, `TakeoffEnded` and `LandingEnded`
  **[V]**. Anything we hang on that path shares the seam — and **T-78** says Multiplayer wraps
  only the landing half.
- **MP Compat carries a `VanillaGravshipExpanded` compat class in `Referenced/`** **[V]** — real
  code that runs only while this mod is running, not a stub.
- It also carries `IncidentWorker_EscapePodCrash`, and `corpus.py --check` reported it **updated
  since the pin** (2026-08-19 → 2026-09-15) during this batch; the readings above are from the
  copy on disk today.
  ([#146](https://github.com/cjd721/Rimworld-Archinity/issues/146),
  [#148](https://github.com/cjd721/Rimworld-Archinity/issues/148),
  [#150](https://github.com/cjd721/Rimworld-Archinity/issues/150))

**Compositable Loadouts** — `Wiri.compositableloadouts` (`2679126859`). Appended to its existing
row in § *What the 2026-09-12 capability batch found*:

> **Unsynced in 1.6 Multiplayer.** `Wiri.compositableloadouts`, `CompositableLoadouts`,
> `LoadoutManager`, `LoadoutComponent` and `Dialog_TagEditor` appear in exactly one file under
> `1629973374`: `1.4/Referenced/Multiplayer_Compat_Referenced.dll`. Nothing in 1.5 or 1.6,
> `Assemblies/` or `Referenced/` **[V]** (both sweep forms validated on the same files; `VREAndroids`
> UTF-16LE hits 1.4, 1.5 and 1.6). Its *Satisfy loadout now* gizmo
> (`Inventory.LoadoutComponent.CompGetGizmosExtra`) calls `Loadout.RequiresUpdate()`, setting a
> field `Loadout.ExposeData` scribes, with **no synced command behind it** **[V]**. Its *Clear
> inventory now* gizmo survives only because it terminates in `Pawn_JobTracker.TryTakeOrderedJob`,
> which MP registers **[V]**. Also: `Inventory.ThinkNode_LoadoutRealisation` equips a weapon **only
> when `pawn.equipment.Primary == null`** — it never swaps one **[V]** — and `SetPawnLastUpdated`
> calls `Rand.Range(10000, 15000)` inside the think node **[V]**.

This **corrects** the existing row's *"the only thing in the corpus that reaches weapons from a
preset"*: it is the only **mod** that does. Odyssey's outfit stand is vanilla's own authored
equipment set and it includes the weapon — `docs/engine/equipment-and-kits.md`, and **T-136** for
how a derived stand def fails silently.
([#155](https://github.com/cjd721/Rimworld-Archinity/issues/155))

**Nothing new for the bar.** No mod in this batch moved tier, and #166 tripped over no conflict at
all. Two rows above (VFE – Insectoids 2, Better Traders Guild) are cargo per
`docs/agents/capability-research.md` § *Conflicts are cargo, not verdicts*.

## Open

- **`rwmt.MultiplayerCompatibility` is a required member of the shipping set, not a
  pre-test chore.** It carries the fix for **T-33** — an unseeded `System.Random` that
  gives two clients different KCSG settlements with no error and no desync report — and
  covers 20 other mods on disk by name. It loads after `rwmt.multiplayer`. Confirm it
  bound by checking the startup log for the **absence** of
  `"No System RNG was patched for method: KCSG.SettlementGenUtils+Sampling.Sample"`.
  ([#88](https://github.com/cjd721/Rimworld-Archinity/issues/88))
- ~~Confirm Vehicle Framework's synchronous fallback is deterministic, if vehicles ship.~~
  **CLOSED, premise wrong.** There is no reachable switch to put it on the fallback path,
  and `VehiclePathFollower.RequestNewPath` / `WorldVehiclePathGrid.RecalculateAllPathCostsAsync`
  bypass the `ThreadAvailable` gate entirely via `SmashTools.TaskManager.Run` **[V]**. The
  question that replaces it: **decide whether to own the patch** — the 5 `ThreadAvailable`
  readers MP Compat's `NoThreadInMp` does not cover, plus the
  `VehicleRegionCostCalculator.pathCostSamples` static. **T-74** / **T-75**.
  ([#69](https://github.com/cjd721/Rimworld-Archinity/issues/69))
- **Confirm which `RangeFinder.dll` the game loads**, and whether `MultiVersionModFix`'s
  patch on `ModMetaData.VersionCompatible` is live. Launch-log check, not a decompile.
- ~~**Smoke-test Defensive Positions in a live MP session** — it is not covered by the
  compat layer and it issues pawn orders from gizmos.~~ **CLOSED, and the premise was
  wrong.** Its orders go through `TryTakeOrderedJob` and `Pawn_DraftController.Drafted`,
  both of which Multiplayer registers itself **[V]**. See the section above. The open
  question that replaces it is a *want*, not a safety one: **decide whether defensive
  positions and squads should be shared between the two players.** They are per-player
  today, silently. Three `MP.RegisterSyncMethod` calls if we want them shared.
- Everything else is a *want* question, owned by the design tickets, not by this file.
