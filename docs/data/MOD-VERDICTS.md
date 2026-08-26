# Mod verdicts

The bar from [#3](https://github.com/cjd721/Rimworld-Archinity/issues/3), applied to
**every mod on disk — all 122**. Issue [#17](https://github.com/cjd721/Rimworld-Archinity/issues/17).

**The instrument, restated so this file stands alone:**

- **Barred** — we *cannot* use it. Only when fixing it would mean owning their
  assembly: a parallel world simulation, or background threads. Nothing else bars.
- **Declined** — we *can* use it and choose not to. Conrad's call. No justification owed.
- Everything else is **Free** (enable it), **Cheap** (enable plus a
  `PatchOperation`) or **Real** (a fork we re-merge, or a Harmony patch in our
  assembly).
- Barred and declined mods **stay on disk as reference.**

**122 mods on disk** — the workshop folder, local `Mods/`, and this repo. **Every one
has a verdict.**

**Five of them are ours** (Origins, Pacing, Drifters, Glitterites, Altar) and the
admission bar does not apply to them: the bar decides whether to admit *someone
else's* work. Our own code is governed by the two gates in `CODING_STANDARDS.md`.
So the bar runs over the **117 third-party** mods.

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

**85 of 122 are mechanically unbarrable** — no assembly at all, or an assembly with
no threading and no `WorldComponent`. For those the bar cannot bite and no
decompile is needed. The remaining 37 were examined individually.

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

**One methodological trap, recorded because it cost a pass:** reading `<packageId>`
by regex over `About.xml` returns the first match in the file, which for many mods is
a *dependency's* id inside `<modDependencies>`. The first run reported eight separate
mods as `brrainz.harmony`. Parse the XML; take the direct child of `ModMetaData`.

---

## Barred — 1

| Mod | packageId | Evidence |
|---|---|---|
| **Rim War** | `Torann.RimWar` | `ThreadStart` present in the 1.6 assembly **[V]**, plus `WorldComponent_PowerTracker` and `WorldComponent_IncidentTracker` running a genuine parallel world power simulation, plus a 30-field settings ref constructed inside `WorldComponentTick`. Threads are on by default. |

**One mod, out of 117 third-party.** That is the instrument working as designed, not a shortfall.
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

## In — 112 third-party, by tier

> **Amended by [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) session 2.** Was 114. **VFE – Insectoids 2** and **Faction
> Territories and Vassalage** have since been declined by Conrad and are listed in **Declined**
> above. Both still appear in the tier tables below, where the tier verdict (what we *can* use)
> remains accurate — the decline supersedes it on whether we *will*.

Everything third-party that is not barred and not declined. **Our five are not listed
here** — see the note at the top; they are in by definition and answer to the two
gates, not to a tier.

**Free (22)** — no assembly. Nothing can go wrong that is not XML.

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

**Cheap (33)** — an assembly, no settings surface. Enable plus a `PatchOperation`
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

**Cheap + settings (57)** — Cheap plus a **managed condition**: per
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

> **Arithmetic.** 122 mods on disk. **Five are ours** (Origins, Pacing, Drifters,
> Glitterites, Altar) and are not subject to the admission bar, leaving **117
> third-party**. Three distinct mods are out — Rim War (barred *and* declined),
> Elves and Dwarves (declined) — so the **in** set is **114**, tiered Free 22 / Cheap 33 /
> Cheap+settings 57 / Real 2 = 114. Real is carved *out of* Cheap+settings, not
> added to it — an earlier revision counted Vehicle Framework and TechBlock twice.

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

---

## What this pass changes

1. **One mod is barred out of 117 third-party, and three are declined.** The bar is not a filter
   that removes work — it removes almost nothing, and that *is* the finding. What
   actually shapes the set is cost and taste, and taste is recorded here only when
   Conrad has stated it.
2. **The bar reduces to one testable question: does it create threads.** A world sim
   on the synced tick is deterministic; disliking it is a decline, not a bar.
3. **Vehicles are available**, at one settings flag. Previously this read as a hard block.
4. **The real cost of the set is its settings surface.** 60 of the 122 mods on disk carry
   one, so `config/ModSettings/` is save-critical across half the build and
   [#18](https://github.com/cjd721/Rimworld-Archinity/issues/18) must snapshot it as a
   single artifact.
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
- Everything else is a *want* question, owned by the design tickets, not by this file.
