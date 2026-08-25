# Mod verdicts

The bar from [#3](https://github.com/cjd721/Rimworld-Archinity/issues/3), applied to
**every mod on disk — all 113**. Issue [#17](https://github.com/cjd721/Rimworld-Archinity/issues/17).

**The instrument, restated so this file stands alone:**

- **Barred** — we *cannot* use it. Only when fixing it would mean owning their
  assembly: a parallel world simulation, or background threads. Nothing else bars.
- **Declined** — we *can* use it and choose not to. Conrad's call. No justification owed.
- Everything else is **Free** (enable it), **Cheap** (enable plus a
  `PatchOperation`) or **Real** (a fork we re-merge, or a Harmony patch in our
  assembly).
- Barred and declined mods **stay on disk as reference.**

**113 mods scanned** — 108 in `workshop/`, the rest local. **Every one has a verdict.**

> **`config/ModsConfig.xml` carries no signal and is not referenced below.** Mods are
> unenabled because the game has not been launched, not because anything was decided.
> An earlier revision of this file treated enabled/disabled as evidence of intent and
> drew a conclusion from it; that was wrong and is struck.

---

## Corrections to the first pass

1. **Factional War is not barred.** It has no threading of any kind — a single
   `WorldCompFormCaravanAfterAllyExit` and nothing else **[V]**. The barred label was
   mine and unsupported by evidence. Whether we *want* it is a separate, still-open
   question — see **Nothing declined yet** below.
2. **The Medieval Overhaul flag is void.** It rested on MO being disabled, which
   means nothing. MO is a normal candidate.
3. **Faction Territories and Worksites Expanded are un-declined.** I declined both
   on my own judgment; that was not mine to do. Both are tiered below and returned
   to Conrad undecided. Neither is barred — one `WorldComponent` each, no thread
   creation **[V]**.

---

## Method, and what it can and cannot prove

Byte-marker scan of every 1.6 assembly, then `ilspycmd` decompiles wherever a marker
was load-bearing. `[V]` = decompiled and read. `[M]` = marker-level only.

**77 of 113 are mechanically unbarrable** — no assembly at all, or an assembly with
no threading and no `WorldComponent`. For those the bar cannot bite and no
decompile is needed. The remaining 36 were examined individually.

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

**One methodological trap, recorded because it cost a pass:** reading `<packageId>`
by regex over `About.xml` returns the first match in the file, which for many mods is
a *dependency's* id inside `<modDependencies>`. The first run reported eight separate
mods as `brrainz.harmony`. Parse the XML; take the direct child of `ModMetaData`.

---

## Barred — 1

| Mod | packageId | Evidence |
|---|---|---|
| **Rim War** | `Torann.RimWar` | `ThreadStart` present in the 1.6 assembly **[V]**, plus `WorldComponent_PowerTracker` and `WorldComponent_IncidentTracker` running a genuine parallel world power simulation, plus a 30-field settings ref constructed inside `WorldComponentTick`. Threads are on by default. |

**One mod, out of 113.** That is the instrument working as designed, not a shortfall.
With licence struck and the set pinned, almost every defect that used to read as
disqualifying is now something we can simply fix. Already mined for the
faction-tension shape; stays on disk as reference.

## Declined — none yet

**Nothing on this list is closed.** Three mods have been *spoken of* as unwanted —
Faction – Elves, Dwarves of the Rim, and Factional War — but that was conversational,
not reasoned, and Conrad has since said explicitly that it needs thinking through
before it is recorded as a verdict.

| Mod | packageId | Status |
|---|---|---|
| Faction – Elves | `ICC.FOV.ELVES` | **Open want-question** → [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) |
| Dwarves of the Rim | `bean.customxenotypes.dwarvesoftherim` | **Open want-question** → [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) |
| [SR] Factional War (fork) | `SR.ModRimworld.FactionalWarContinued` | **Open want-question** → [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) |

All three are faction and world content, so the want-question belongs to
[The world roster](https://github.com/cjd721/Rimworld-Archinity/issues/8) alongside
Empire, Deserters and Android — not to this file. **This pass declines nothing.**
It establishes what we *can* use; what we *want* is decided elsewhere, deliberately.

Recorded so the reasoning is not lost: Elves and Dwarves both add **medieval-era
factions at world creation**, which puts them behind the freeze and makes them a
roster decision rather than a content one. Factional War resolves faction-vs-faction
combat, which overlaps whatever shape [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8)
lands on for faction tension — so it is a question of *duplication*, not of safety.

---

## In — 112, by tier

Everything not barred. Three of these carry an open want-question, flagged **†** and
listed above; they are counted here because the bar admits them.

**Free (24)** — no assembly. Nothing can go wrong that is not XML.

| Mod | packageId |
|---|---|
| Archinity – Origins / Pacing / Drifters / Glitterites | `archinity.*` |
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
| **†** Faction – Elves | `ICC.FOV.ELVES` |
| **†** Dwarves of the Rim | `bean.customxenotypes.dwarvesoftherim` |

**Cheap (31)** — an assembly, no settings surface. Enable plus a `PatchOperation`
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
| Vehicle Framework · Vanilla Vehicles Expanded | `SmashPhil.VehicleFramework`, `OskarPotocki.VanillaVehiclesExpanded` |
| TechBlock · Ignorance Is Bliss · Lemmy Progression | `fridgeBaron.TechBlock`, `dame.ignorance`, `LemmyMods.LemProgression` |
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
| **†** [SR] Factional War (fork) | `SR.ModRimworld.FactionalWarContinued` |

> **Arithmetic**, since an earlier revision of this file got it wrong: 113 total,
> tiered as Free 24 / Cheap 31 / Cheap+settings 58. Rim War is barred and sits in
> Cheap+settings, so the **in** set is 24 + 31 + 57 = **112**.

### Real tier — 2

| Mod | The price |
|---|---|
| **Vehicle Framework** `SmashPhil.VehicleFramework` **[V]** | The only mod besides Rim War with real thread-creation machinery: `SmashTools.Performance.DedicatedThread` runs `new Thread(Execute){IsBackground=true}` + `Start()`, and `Vehicles.DeferredGridGeneration` enqueues **vehicle pathing-grid and region generation** onto it — simulation off the synced tick. **Saved by a switch:** `Vehicles.SectionDebug.debugUseMultithreading` is a scribed bool defaulting `true`; false ⇒ `ReleaseThread()` instead of `InitThread()` ⇒ `ThreadAvailable` false ⇒ every enqueue site takes its synchronous fallback. Price: one settings flag, treated as save-critical. Unverified residuals: the sync fallback is not confirmed deterministic, and single-threaded grid generation costs frame time. **This is what decides whether vehicles are available to the campaign at all — and the answer is yes.** |
| **TechBlock** `fridgeBaron.TechBlock` | `GameComponentUpdate()` writes research progress **per frame**, so clients at different frame rates diverge continuously and no settings file fixes it, because frame rate is not a setting. Fork-and-recompile, or a Harmony prefix. Owned by [#7](https://github.com/cjd721/Rimworld-Archinity/issues/7). |

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

1. **One mod is barred out of 113, and nothing is declined.** The bar is not a filter
   that removes work — it removes almost nothing, and that *is* the finding. What
   actually shapes the set is cost and taste, and taste is not this file's to record.
2. **The bar reduces to one testable question: does it create threads.** A world sim
   on the synced tick is deterministic; disliking it is a decline, not a bar.
3. **Vehicles are available**, at one settings flag. Previously this read as a hard block.
4. **The real cost of the set is its settings surface.** 52 of 113 mods carry one, so
   `config/ModSettings/` is save-critical across most of the build and
   [#18](https://github.com/cjd721/Rimworld-Archinity/issues/18) must snapshot it as a
   single artifact.
5. **Three ejections are already decided and all are cheap.** Saurid and Waster cost
   two `MayRequire` gene lines in `Archinity.Origins` (`VRESaurids_Pheromones`,
   `VRE_Instability_Extreme`) plus an over-declared `<modDependencies>` block.

## Open

- Enable `rwmt.MultiplayerCompatibility` before any co-op smoke test.
- Confirm Vehicle Framework's synchronous fallback is deterministic, if vehicles ship.
- Decompile `[WG] RimPacts` (`3762723122`) — **not installed**; carried from `PARTS-BIN.md` §14.
- Everything else is a *want* question, owned by the design tickets, not by this file.
