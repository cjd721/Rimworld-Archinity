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
| **Better Workbench Management** | `falconne.BWM` — no threads **[V]**; two `WorldComponent`s (`ExtendedBillDataStorage`, `WorktableRestrictionDataStorage`) that only persist bill metadata. Three of its seven settings are read inside a `RecipeWorkerCounter.CountProducts` detour. See Named prices. |
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
| **Vehicle Framework** `SmashPhil.VehicleFramework` **[V]** | The only mod besides Rim War with real thread-creation machinery: `SmashTools.Performance.DedicatedThread` runs `new Thread(Execute){IsBackground=true}` + `Start()`, and `Vehicles.DeferredGridGeneration` enqueues **vehicle pathing-grid and region generation** onto it — simulation off the synced tick. **Saved by a switch:** `Vehicles.SectionDebug.debugUseMultithreading` is a scribed bool defaulting `true`; false ⇒ `ReleaseThread()` instead of `InitThread()` ⇒ `ThreadAvailable` false ⇒ every enqueue site takes its synchronous fallback. Price: one settings flag, treated as save-critical. Unverified residuals: the sync fallback is not confirmed deterministic, and single-threaded grid generation costs frame time. **This is what decides whether vehicles are available to the campaign at all. The lever exists and is confirmed in source; whether it is *sufficient* is not confirmed until the fallback is shown deterministic** — which is why that sits in Open below rather than being claimed here. |
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
[The world roster](https://github.com/cjd721/Rimworld-Archinity/issues/8). Weigh it
against the Waystone's *do not build a shadow world* — the stated reason faction-sim
mods are perpetually beta is that they maintain a parallel world model, and this is
one, ticking synced or not. Against that: it is the only thing in the bin that
already implements treaties, vassalage, tribute and a humiliating peace, which is
close to a literal restatement of what WAYSTONE §5 asks the political board to do.

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
| `rwmt.MultiplayerCompatibility` | **Floor assumption.** Downloaded; enable before any co-op test. |
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
3. **Vehicles are available**, at one settings flag. Previously this read as a hard block.
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

## Open

- Enable `rwmt.MultiplayerCompatibility` before any co-op smoke test.
- Confirm Vehicle Framework's synchronous fallback is deterministic, if vehicles ship.
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
