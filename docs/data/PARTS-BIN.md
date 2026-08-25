# The Workshop parts bin

What each installed mod can actually **supply** to Archinity, and what it costs to
take it. Resolves wayfinder ticket **#4**.

**This is a parts bin, not a load order.** Conrad subscribed to ~100 mods because
they looked useful, not because he plans to run them. Nothing here commits the
project to shipping anything. The active/inactive split in `config/ModsConfig.xml`
carries **zero weight** and was deliberately ignored throughout.

> ## ⚠ Standing correction — licence reasoning is void
>
> **Archinity is a private mod for two people. It will never be public and never be
> published.** Licence, copyright and attribution are therefore **not constraints on
> this project** and must not enter any assessment.
>
> This document was originally written with a licence axis. Wherever a verdict below
> reads **BLOCK**, **REBUILD** or **RESTAT** *because of a licence* — "unlicensed",
> "all rights reserved", "depend, never vendor", "reference-only", "do not copy",
> "worth asking", "if licence permits" — **that reasoning is struck and the verdict
> reverts to PULL.** Everything in the bin is available to lift, fork, vendor,
> restat or repair, source included.
>
> Verdicts resting on *engineering* grounds — multiplayer safety, save-state
> permanence, maintenance status, performance, design fit — are unaffected and still
> stand. Where an entry gave both, only the engineering half survives.
>
> Section 4 has been rewritten and the per-mod verdicts corrected. A few inline
> provenance notes remain — read them as facts about a mod, never as an argument
> against using it.

**Scope.** 108 Workshop mods (`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\`)
plus the 4 local Archinity mods (symlinked into
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\`). Roughly 45 got a
depth pass — folder opened, defs and patches read, assemblies decompiled with
`ilspycmd`. The rest are bookmarked at index level in §11.

**How to read a claim.** **[V]** = someone read the def, the patch or the decompiled
code and cites the path. **[I]** = inferred from a name, a blurb or structure. Every
verdict is one of **PULL** (ship it) / **RESTAT** (ship it but rebalance and
repoint) / **REBUILD** (lift the technique, write our own) / **BLOCK** (must
actively suppress its content). Split verdicts are common and expected.

**Read alongside** `docs/technical-findings.md`, which already carries the verified
internals of TechBlock, Ignorance Is Bliss, More Realistic Research, VQE Ancients,
KCSG, Medieval Overhaul's settings traps, facility linking and the research-rate
maths. This document does not repeat those; it extends them and cites them.

Game version 1.6.4871. Verify again after any major RimWorld update.

---

## 1. The nine findings that change something

1. **Vanilla already ships non-wealth threat scaling, and nothing on disk does it
   better.** `Difficulty.fixedWealthMode` replaces real colony wealth with a
   time curve. A Custom-difficulty toggle, saved in the game, no mod, no assembly,
   no desync surface. §8.1. **[V]**

2. **The Chronicle can be authored in pure XML with exactly one new dependency.**
   VEF's `QuestChainExtension` + vanilla's 306 `QuestNode_*` types + VEF's
   `LootableBuilding` compose into a branching, save-persistent, research-gated
   questline with no second assembly. VQE Ancients is the working reference and its
   whole 6-beat topology is ~40 lines of XML. §7. **[V]**

3. **The altar is one ThingDef, and the whole religion→industry arc is vanilla
   XML.** `CompProperties_Refuelable` (fuel filter = a blood item) +
   `CompProperties_SpawnSubplant` (accumulating evidence) +
   `CompProperties_Psylinkable` (`requiredSubplantCountPerPsylinkLevel`) +
   `CompProperties_MeditationFocus`, all on one def, with vanilla's anima-tree
   linking ritual retargeted at it. Zero C#. §9. **[V]** This is the single largest
   result in the ticket.

4. **The two power tracks join in XML.** `PsycasterPathDef.requiredGene` plus
   `ensureLockRequirement: true` makes a named Archon gene the literal key to a
   psychic path, activating and deactivating automatically. §9.2. **[V]**

5. **Two of the five "unclaimed" asks are already delivered, one by a mod already
   installed.** Ingredient-tier food buffs → Vanilla Cooking Expanded. Bench
   upgrade-in-place → Replace Stuff. And the **coat of arms is delivered too** — by
   VFE Medieval 2, which was on nobody's list for it. §10. **[V]**

6. **`Story Framework` is closed as a lead — negative.** It exists (`1413932960`,
   MIT), its XML surface was genuinely expressive, and it is **1.0-only, last
   touched February 2019**, shipping a vendored 2019-era `0Harmony.dll`. §12.1.
   **[V]**

7. **The era-gating contest is settled on facts.** TechBlock's ladder is
   *unclimbable* under World Tech Level and fails silently. Node Research is
   silently kills WTL's research filter. And the two candidates the
   project already leans on are the two the Multiplayer compat layer does not cover.
   §5. **[V]** No winner picked — that is a separate ticket.

8. **Five always-present hostile Industrial factions have no
   `raidCommonalityFromPointsCurve`, so they are exactly as likely to raid at 80
   points as at 20,000** — which makes Ignorance Is Bliss the *sole* era gate, not a
   backstop. Fixable with five `PatchOperationAdd`s. §8.3. **[V]**

9. ~~**Licence is the binding constraint on art, not quality.**~~ **STRUCK — see the
   standing correction above.** Licence is not a constraint on this project at all.
   The finding that survives is the raw volume: **north of 14,000 sprites across the
   assessed set, all of them usable**, led by Medieval Overhaul's 4,119 and VFE
   Medieval 2's 1,122. *Reskin before you rebuild* applies at full strength. §4. **[V]**

---

## 2. The four design areas, in one table

| | (a) Era progression | (b) The world | (c) Questline | (d) What the world demands |
|---|---|---|---|---|
| **Best thing available** | World Tech Level's 23-def-type filter | Vanilla Landmarks Expanded's 115 named places | VEF `QuestChainExtension` | vanilla `fixedWealthMode` |
| **Best technique to steal** | VFE Classical: era unlocks held by named NPCs, earned by quest | Faction Territories: territory flood-fill + tech-weighted siege resolution | VFE Deserters: one `SubScript` base quest, 30 lines per beat | VFE Deserters: `VisibilityLevelDef` escalation ladder as data |
| **Second-best** | Tribal Furniture's `min/maxTechLevelToBuild` content *retirement* | [SR] Factional War: factions fight each other on your map | VEF `LootableBuilding` signal | vanilla ritual obligations — the altar that *demands* |
| **Biggest gap** | nothing gates on *capability* rather than research or wealth | nothing makes a faction want something from *another* faction and tell you | no XML persistent screen alert for a deadline | non-wealth *quality* scaling — points buy quantity by default |

---

## 3. Multiplayer: the cross-cutting risk

This is the risk column for every entry below, so it is stated once here.

**Native integration is almost nonexistent.** Of 107 installed non-Multiplayer mods,
exactly **one** references the Multiplayer API in its 1.6 build: **Adaptive Storage
Framework** (`3033901359`), which ships `0MultiplayerAPI.dll` and uses
`SyncMethodAttribute`. **[V]** Two mods actively *regressed*: **VEF** shipped
`0MultiplayerAPI.dll` in its 1.3/1.4/1.5 folders and dropped it in 1.6 **[V]**, and
**[SYR] Processor Framework** shipped it in 1.3/1.4 and the 1.5/1.6 "continued" build
dropped it **[V]**.

**The Multiplayer mod itself carries no per-mod compat.** `2606448745` is at 0.11.5;
its `1.6/AssembliesCustom/Multiplayer.dll` contains no VE, MO, TechBlock or RimWar
references. Checked from both directions — VPE's assembly has zero "Multiplayer"
strings, and Multiplayer's assemblies have zero `VanillaPsycastsExpanded`,
`PsycasterPath`, `VanillaMemesExpanded` or `OskarPotocki` strings. **[V]** Its
`About.xml` does declare
`<loadBefore>OskarPotocki.VanillaFactionsExpanded.Core</loadBefore>`.

**The community compat layer is NOT installed.** *Multiplayer Compatibility*,
Workshop **`1629973374`** (`rwmt.MultiplayerCompatibility`, MIT © 2019 Meru, author
notfood, tags 1.2–1.6, updated 2026-08-20, 221k current / 419k lifetime
subscribers). **[V]** Three other IDs appear in the project's notes and in agent
reports — `2098714807`, `2596027042`, `2038000254` — and none resolve; `2098714807`
returns `result: 9` from the Steam API. **Use 1629973374.**

**Coverage: 36 of 108 installed packageIds**, diffed case-insensitively against 240
distinct packageIds across 214 `MpCompatFor` patch files at master (pushed
2026-08-20). **[V]** Only three mods carry the author's `x` broken-marker
(Gastronomy, RunAndGun, ZombieLand); none is installed.

**Covered (36):** `adaptive.storage.framework`, `Fluffy.Pharmacist`,
`Mehni.PickUpAndHaul`, `OskarPotocki.VanillaFactionsExpanded.Core`, `…SettlersModule`,
`OskarPotocki.VanillaVehiclesExpanded`, `OskarPotocki.VFE.Classical`, `…Deserters`,
`…Empire`, `…Insectoid2`, `…Medieval2`, `…Pirates`, `…Tribals`, `sarg.alphamechs`,
`SmashPhil.VehicleFramework`, `syrchalis.processor.framework`, `UnlimitedHugs.HugsLib`,
`vanillaexpanded.gravship`, `vanillaexpanded.outposts`, `VanillaExpanded.VAEWaste`,
`VanillaExpanded.VCEF`, `VanillaExpanded.VExplorationE`, `VanillaExpanded.VFECore`,
`…VFEFarming`, `…VFEPower`, `…VFESecurity`, `…VMemesE`, `…VNutrientE`, `…VPE.Hemosage`,
`…VPE.Puppeteer`, `…VPsycastsE`, `vanillaracesexpanded.android`, `…hussar`,
`…sanguophage`, `…saurid`, `Wiri.compositableloadouts`.

**The four uncovered mods that actually matter** — uncovered *and* simulation-affecting
rather than cosmetic:

| Mod | Why it matters |
|---|---|
| `Torann.RimWar` | background world simulation, on real threads |
| `SR.ModRimworld.FactionalWarContinued` | faction-vs-faction combat resolution |
| `m00nl1ght.WorldTechLevel` | ~60 generation/filter patches; author's own line is *"mixed reports… I can't provide any support for multiplayer-related issues"* |
| `fridgeBaron.TechBlock` | tech-level advancement; its own roadmap lists MP support as unimplemented |

The last two are two of the three era-gating candidates. Material to that lead (§5) —
recorded, no winner picked.

**What the VEF patch actually covers**, since ~40 of the 108 sit on VEF: 26–28
independently-registered subsystems (Advanced Resource Processor, Abilities, Hireable
Factions, VFE Furniture, Animal Behaviour, MVCF, Pipe System, KCSG, Faction Discovery,
Genes, Cooking, Teleporter Doors, Special Terrain, Weather Overlays, Graphic
Customization, Drafted AI, map-gen thing spawning, quest-chain dev window, Moving
Bases…), plus a separately-compiled `Source_Referenced` file covering Outposts.
**[V]** Two properties matter operationally: each subsystem is **individually
try/caught**, logging `"Encountered an error patching {componentName}"` and
degrading *silently and partially* rather than failing closed **[V]**; and many
gizmo lambdas are addressed **by ordinal**, so an upstream gizmo insertion renumbers
them. Grep that log string during MP smoke-testing.

**VPE's patch** covers psyset create/remove/rename, `SpentPoints`/`ImproveStats`/
`UnlockPath`/`UnlockMeditationFocus`/`GainExperience`, `Dialog_CreatePsyring.Create`,
ability toggles, and explicit RNG fixes whose own comments name the bug class:
*"Uses RNG after `GenView.ShouldSpawnMotesAt`, gonna cause desyncs."* **[V]** Active
psyset switching is left unsynced deliberately.

**Naming traps that will each cost a debugging cycle:**

1. `VanillaExpanded.VFECore` is Vanilla **Furniture** Expanded. The framework is
   `OskarPotocki.VanillaFactionsExpanded.Core`. Both installed, both covered.
2. `VanillaExpanded.VCookE` reads as uncovered but is **functionally synced** — the
   VEF patch's Cooking component patches `VEF.Cooking.Thought_Hediff` via
   `PatchingUtilities.PatchTryGainMemory`, the exact class VCE's condiment thoughts
   use, self-gating on whether any `ThoughtDef` uses that `thoughtClass`. Read "not
   in the list" as "no dedicated patch". Stews presumably rides the same path — **[I]**.
3. `DankPyon.Medieval.Overhaul` (uncovered) is not `OskarPotocki.VFE.Medieval2`
   (covered). `Sierra.RF.MedievalOverhaul` is also uncovered. The repo's
   `VanillaFactionsMedieval*.cs` files are VFE, not MO.
4. `Torann.RimWar` is not `Torann.ARimworldOfMagic`. Same author, only the latter is
   patched.
5. **VRE splits 4/4.** Android, Hussar, Sanguophage, Saurid covered. **Archon,
   Starjack and Waster are absent from the repo entirely** — and Archon and Starjack
   are the two the project's own factions lean on hardest.
6. `adaptive.storage.framework` is covered *and* natively MP-aware;
   `Adaptive.PrimitiveStorage` is a different, uncovered mod.
7. Vehicles split — VVE covered, VVE-Upgrades not, though `SmashPhil.VehicleFramework`
   underneath both is covered.
8. `rwmt.Multiplayer`, `brrainz.harmony` and `zetrith.prepatcher` appear uncovered by
   construction; the real uncovered count is ~69.

> **Absence of a compat patch is not proof a mod desyncs, and presence is not proof
> it is safe under our usage.** Treat this as coverage, not verdict.

### 3.1 The systemic hazard, and it is not RNG

**51 of 107 installed mods ship a settings-bearing 1.6 assembly. [V]** Client-local
`ModSettings` read inside simulation is the dominant desync source in this bin, and
it appears in nearly every mod assessed — often as the *only* real defect in
otherwise clean code. A representative census of what was actually verified:

| Mod | The read | Consequence |
|---|---|---|
| TechBlock | `GameComponentUpdate()` per-frame, `randomInsightRate` → `AddProgress` | continuous divergence |
| World Tech Level | ~45 `[HarmonyPrepare]` toggles | clients get **different patched methods** |
| Rim War | 30-field `SettingsRef` constructed inside `WorldComponentTick` | whole world sim diverges |
| Medieval Overhaul | `Rand.Chance(settings.soilWearChance)` gating `RemoveTopLayer()` per harvest; 10+ `Prepare()` returning settings | terrain mutation + different patch sets |
| VPE | `GainExperience(gain * 100f * Settings.XPPerPercent)` | divergent saved `experience` per psycaster per tick |
| VRE Starjack | `starjackGenesAmount` in `OrderBy(Rand.Value).Take(n)` | **different number of `Rand` draws** per pawn |
| VRE Hussar | `WeaponFilter` inside a `GeneDefGenerator.ImpliedGeneDefs` postfix | **different GeneDef count at load time** |
| VFE Empire | `Rand.Chance(… * Settings.deserterChanceMult)` in pawn-group generation | different pawns spawn |
| Ushanka Glittertech | `FormingSpeedMultiplier` in `BillTick()`; pylon mood multipliers | production speed and mood diverge |
| VGE Chapter 1 | `maintenanceLossMultiplier` in `TickInterval()` | ship deterioration diverges |
| Processor Framework | `initialProcessState` in `CompProcessor.Initialize()` | **every processor spawns with a different enabled set** |
| VRE Sanguophage | `drainCasketAmount` consumed in a tick | nutrition diverges |
| Tribal Furniture | four settings read inside `PatchOperation.ApplyWorker` | one client has a ThingDef the other does not |
| Outposts | production timers and yields; reflection writes settings **onto live instances** at load | item counts diverge |

**The pattern worth adopting project-wide: put tunables in a Def, never in
`ModSettings`.** Defs ship with the mod and are identical on both machines by
construction. Three mods here already do it and are the cleanest in their clusters —
Dark Ages: Beasts (`…\3472275628\1.6\Defs\Settings\TrollSettings.xml`), VRE Android
(`…\2975771801\1.6\Defs\AndroidSettings.xml`), and **VPE Puppeteer's
`PuppetSettings : Def`**. **[V]** RimFantasy is the existence proof from the other
direction: one of the largest assemblies in the bin and one of the safest, because it
has **no settings surface at all**.

**The second systemic hazard is viewport-gated RNG**, and it recurs in exactly the
same shape three times in the VPE family alone:

```csharp
if (GenView.ShouldSpawnMotesAt(...))   // ← CAMERA-DEPENDENT, client-local
{
    Rand.Value; Rand.Value; Rand.Range(...); Rand.Range(...);   // ← SHARED STREAM
}
```
Two clients looking at different parts of the map consume **different numbers of
draws from the shared `Rand` stream in the same tick**. Verified in VPE
`FixedTemperatureZone` and `Tornado`, VPE Hemosage `Hediff_Bloodmist`, and VPE
Puppeteer `Hediff_BrainLeech`. **[V]** VPE knows the correct idiom — it uses
`Rand.PushState(); Rand.Seed = thingIDNumber; … PopState()` elsewhere in the same
file. The bug is inconsistency, not ignorance. The Multiplayer Compatibility patch
fixes exactly this class for VPE, which is a strong argument for installing it.

15 mods reference `System.Threading` in a 1.6 assembly: TechBlock, VEF, VRE Waster,
VVE, Vehicle Framework, Adaptive Storage, Processor Framework, Map Mode Framework,
VGE, Faction Territories, Better Traders Guild, EdB, HugsLib, plus Multiplayer and
Prepatcher. **[V]** The scan misses Rim War, whose assemblies live in a non-standard
`v1.6/` folder and which was confirmed by decompile to run **real background threads,
on by default**. **[V]**

---

## 4. Art volume — what each mod actually ships

> This section originally ranked mods by what their licences permitted. That reasoning
> is void — see the standing correction at the top of this file. What follows is the
> half that was actually useful.

What survives is the useful half — **how much art each mod actually ships**, which is
what makes it worth raiding as a parts bin.

| Mod | Sprites | Notes |
|---|---:|---|
| Medieval Overhaul | 4,119 | by far the largest single art source in the bin |
| VFE Medieval 2 | 1,122 | includes the 566 heraldry masks (§10.4) |
| VIE Memes and Structures | 704 | plus 16 ritual `.ogg` audio loops |
| Alpha Mechs | 664 | the late-game mechanoid bestiary |
| Vanilla Gravship Expanded | 523 | |
| Vanilla Psycasts Expanded | 468 | |
| VQE Ancients | 407 | already the altar's art source |
| VFE Insectoids 2 | 380 | |
| Dark Ages: Beasts and Monsters | 347 | the wall-breaking-monster candidates |
| VRE Archon | 268 | |
| VFE Security | 231 | |
| Dark Ages (Tools + Crypts) | 137 | 85 of them at up to 2048² |
| Ushankas Glittertech | 91 | full C# source ships alongside |

Those thirteen sum to **~9,460**. They are the largest sources, not the whole bin —
another twenty-plus assessed mods carry art too (VFE Props and Decor alone ships 1,073),
putting the real assessed-set total north of **14,000 sprites**. All of it usable.

**Practical consequences.** *Reskin before you rebuild* applies at full strength — there
is no reason to author art for anything the bin already draws. **Ushankas
Glittertech ships full C# source**, so it can be forked and repaired outright rather
than worked around. **Vanilla Expanded Framework can be vendored**, which is insurance
against upstream abandonment — not an exit from the save-state commitment in
[The VEF dependency](https://github.com/cjd721/Rimworld-Archinity/issues/15), since its
GameComponents scribe by class name and vendoring under new namespaces orphans those
refs rather than rescuing them. And
`Source/` folders anywhere in the bin are fair game to read and copy.

---

## 5. Design area (a) — era progression and the tech tree

### 5.1 The three-way contest — facts, no winner

| | **World Tech Level** `3414187030` | **TechBlock** `1970774610` | **Node Research** `3729878405` |
|---|---|---|---|
| Installed | yes | yes | **no** |
| Subs | 204k / 330k lifetime | 9.9k / 60k | 27.9k / 44.5k |
| Mutates defs? | **no — explicitly** | yes, at startup | yes, incl. the research main tab |
| Save-safe on removal | **yes, cleanest in the bin** | mostly; orphans player FactionDef | author says *"try not to remove it"* |
| MP compat patch | none | none | none |
| XML extension point | `TechLevelConfigDef` (21 files shipped) | none | 4 `DefModExtension`s + `GroupNodeDef` |

**World Tech Level** builds a parallel tech-level database over **23 def types** and
filters at ~60 sites: research startability, tab visibility, techprints, trader
stock, 11 `ThingSetMaker` targets, storyteller incidents, seven quest paths,
**post-hoc raid gear replacement** via `ReplacementUtility.TryMakeReplacementFor`,
factions, prosthetics, addictions, traits, backstories, diseases, ideo memes,
arrival modes, building materials, mineables. **[V]** State lives in
`GameComponent_TechLevel` (scribed) plus a volatile static `WorldTechLevel.Current`
re-seeded on load. Its README states, and the code bears out, *"World Tech Level does
not modify or remove any defs."*

**TechBlock** ships **zero Harmony patches** and works entirely by runtime def
mutation from `[StaticConstructorOnStartup]`. **[V]** It bundles a dead **Harmony
2.0.0.6** that can win assembly-name resolution over brrainz.harmony 2.3.x. **[V]**
Its `GameComponentUpdate()` is a **per-frame, client-local** callback that calls
`RandomElement` on unfinished research and then `AddProgress` — a continuous
desync. **[V]** Its settings window rewrites live `baseCost` values on open. **[V]**

> **The interop fact that decides the pair.** `TB_MedievalTheory` is declared
> `<techLevel>Medieval</techLevel>`, and WTL's `CanStartNow` postfix blocks any
> project above `Max(WorldTechLevel.Current, InitialResearchLevel)`. **In a Neolithic
> world, `TB_MedievalTheory` is unstartable, so every Medieval project stays
> permanently locked behind a prerequisite you can never buy.** The first two rungs
> work; the wall is at Medieval. No error, no warning. **[V]**
>
> Only two things unblock it: raising the world tech level by hand from WTL's Planet
> tab, or Lemmy's `PlayerResearchFilterLevel` prefix — which is exactly why all four
> ended up installed together, and why the combination is load-bearing on the one mod
> that is broken.

**Node Research** takes over the research tab by def mutation, rewrites every
project's `tab`, force-assigns `TechLevel.Industrial` to any project with
`techLevel Undefined`, synthesises six `BRM_Emergence_*` capstones that write
`Faction.OfPlayer.def.techLevel`, and **prefixes `VFETribals.GameComponent_Tribals.AdvanceTechLevel`
to return false, disabling VFE Tribals' era system by default.** **[V]** Its genuinely
strong property is the XML surface — `ResearchFoundationExtension`,
`EmergenceExtension` (`<targetLevel>`), `ResearchIconExtension`, `GroupParentExtension`
+ `GroupNodeDef`, all patchable from pure XML. **[V]**

**Coexistence, from code on both sides. [V] on the reads, [I] on the consequence:**
- The two `CanStartNow` postfixes stack harmlessly — both only narrow to false.
- **WTL's UI filter silently dies under Node Research.** WTL hangs its visual
  filtering off `MainTabWindow_Research.GetVisibleResearchProjects`, which Node
  Research's replacement window never calls. Over-level projects **render as
  available and refuse to start, with no message.** WTL ships compat shims for
  ResearchPal, ResearchPowl, Better Research Tabs, Dubs Mint Menus, Realistic
  Planets, RealRuins and VFECore — and none for Node Research. **[V]**
- **Node Research and TechBlock are the same mod.** Both are era capstones writing
  the player faction tech level. Adopting one replaces the other; they do not layer.

**Verdicts.** WTL **PULL** — architecturally sound, save-safe both directions, real
public API, pure-XML `TechLevelConfigDef` extension point. TechBlock **REBUILD** —
the *shape* is right and is ~150 lines of honest code. Node Research **BLOCK**.

### 5.2 Lemmy Progression `3548896697` — the claim, confirmed and corrected

**Confirmed in substance, corrected in detail: there are two defects, and the
faction-upgrade half actually works.** Full C# source ships. **[V]**

**The half that works.** `FactionUpgrader.cs:70` — `faction.def = selectedDef;` with
the comment *"Simple def swap - RimWorld handles all the persistence."* That is
correct: `Faction.ExposeData` does `Scribe_Defs.Look(ref def, "def")`. **[V]**

**Defect 1 — the wrong backing field, confirmed.** `WorldEraManager.cs:155`:
```csharp
cachedCurrentField = AccessTools.Field(cachedWorldTechLevelType, "<Current>k__BackingField");
```
It writes only the volatile static auto-property, never
`GameComponent_TechLevel.WorldTechLevel` — the field WTL scribes and re-seeds
`Current` from on **every load**. **So every save/load silently reverts the world
tech level.** Factions stay upgraded; the ceiling snaps back. Spacer factions inside a
Neolithic content filter, no error. **[V]** Grepping the source for `GameComponent` /
`GetComponent` / `Scribe_` returns nothing outside its own settings. **[V]**

**Defect 2 — a latent reflection landmine.** The fallback path matches
`type.FullName.Contains("WorldTechLevel")`; *every* type in that assembly is in
namespace `WorldTechLevel`, so it grabs the first type enumerated and then the first
static `TechLevel` field on it. `searchAttempted` is never reset, so one mistimed
attempt poisons the session. **[V]**

**Multiplayer: disqualifying.** Two static `System.Random` instances;
`ShouldUpgradeFaction` is `random.NextDouble() < settings.factionUpgradeChance`.
**Each client upgrades a different set of factions.** **[V]** It also ships
unconditional debug tracers prefixed onto `FactionDef.MinPointsToGeneratePawnGroup`
and `PawnGroupKindWorker_Normal.MinPointsToGenerateAnything`, emitting 5–8 log lines
per raid/caravan/quest evaluation. **[V]**

**Two techniques carry across, neither requiring a line of its code:**
- **Prefix `TechLevelUtility.PlayerResearchFilterLevel()`** to decouple the player
  from the world ceiling. One seam, enormous leverage. **[V]**
- **Advance the world by swapping `faction.def` to a same-archetype, higher-tier
  FactionDef**, rolled deterministically inside a synced command, persisted via WTL's
  GameComponent.

16 commits, all on 2025-08-14. Four hard dependencies. **REBUILD.**

### 5.3 The era ladder that already exists — VFE Tribals `3079786283`

`…\1.6\Defs\EraAdvancementDefs\EraAdvancements.xml` defines a five-rung
**ritual-gated** ladder: Neolithic → Medieval → Industrial → Spacer → Ultra, each
firing only once all research of the prior era is complete and granting a cornerstone
point. **[V]** It ships 26 pre-neolithic `TribalResearchProjectDef`s, **88
`CornerstoneDef`s** of named ethos flavour, 5 buildings, 3 apparel, 2 weapons, 2
quests, a scenario, a storyteller, ~24 compat patch files, and 88 PNGs including
three complete 16-frame tribalwear sets.

**This is Archinity's premise rendered as XML, and framed as a ceremony rather than a
research checkbox** — the right register for a campaign centred on an altar.

Two blockers. **A hard co-op desync:** `AddCornerstone` is called *directly from
inside `DoWindowContents`*, immediately after `Widgets.ButtonText` returns true,
mutating saved state on one client with no `[SyncMethod]`. **[V]** (It *is* covered by
the compat layer, so verify rather than assume.) **And it retiers a dozen vanilla
buildings** in `…\1.6\Patches\Core.xml` — `SimpleResearchBench`, `Campfire`,
`TorchLamp`, `Wall`, `Door`, `Barricade`, `FueledStove`, `TableButcher`, the pen
buildings — which **collides head-on with `Archinity.Pacing/Patches/Retier_Medieval.xml`**.
Whichever loads later wins, silently. Reconcile deliberately.

Removal is a one-way door: because `Core.xml` retiered vanilla buildings, removal can
leave a colony holding buildings it can no longer rebuild.

**Verdict: RESTAT, leaning REBUILD.** The ladder is five XML defs and one
GameComponent; the ritual-outcome workers are ~40 lines each. Rebuilding it in
`Archinity.Pacing` + `Archinity.Altar` gets the mechanic, lets the era advance sit
behind an altar interaction the project already owns and can sync correctly, and lets
the cornerstones carry the Waystone's narrative.

### 5.4 More Realistic Research `3771646847` — the pacing idea

Not a cost multiplier — a gate. It requires **physical study of materials** before a
project can be worked, using Anomaly's study system.
`AnalysisEngine.AttachStudyCompsToAllManagedMaterials()` runs at
`[StaticConstructorOnStartup]` and **mutates vanilla ThingDefs at runtime**,
appending `CompProperties_Analyzable` + `CompProperties_Studiable` to WoodLog, Steel,
Chocolate, Devilstrand, ComponentIndustrial, Gloomlight and more. **[V]**
`Patch_WorkGiver_Researcher` returns false from `HasJobOnThing` when requirements are
unmet. **[V]**

**Neolithic, Animal and Undefined projects are exempt entirely**, and so is
Archotech. **[V]** That is perfect for this campaign — the tribal opening stays
frictionless and the bite starts at Medieval, exactly where the first real era wall
belongs. `Defs\readme.txt` documents the `ManualAnalysisDef` XML format. **[V]**

Cleanest of the era cluster on RNG: no `Rand.`, no `System.Random`, no threading,
**no mod settings at all**. **[V]** But: anonymous author, 1.6-only, no
upstream, an **undeclared and unguarded Anomaly coupling**, runtime ThingDef comp
injection, and a transposed `Mathf.Clamp(num, 20, 0)` that silently discards the
Intellectual-skill term. **[V]** Its `Devilstrand` entry is circular — already
recorded in `technical-findings.md`, already patched around by
`Archinity.Pacing/Patches/Fix_MoreRealisticResearch.xml`.

**Verdict: REBUILD.** The gate is ~40 lines of the mod's ~1,500.

### 5.5 The best era-gating idea in the bin — VFE Classical `2787850474`

**Its 18 research projects are not on the research bench at all.** All 18 are
`techLevel Neolithic`, all `baseCost 1200`, **none has `prerequisites`**. They are
granted by completing quests for named NPCs — 15 senators across 3 republics, each
with a name, a portrait, a quest, a perk and a research unlock. **[V]** Favour is
earned by quest **or bribe**, and `WorldComponent_Senators` **revokes the perk if the
senator dies** before the republic is made permanent. **[V]** Uniting all three
republics grants a capstone perk and the letter *"You have now become Emperor."*

> **A shipped answer to the project's hardest gating question: how do you gate an era
> on something other than a research bar? You gate it on the world.** Each era's
> unlock bundle is held by a named party; you earn it by doing what they want. The
> research bar stops being the clock and becomes flavour. **You need none of its
> code** — `FinishProject(def)` on a quest signal plus a `FactionDefExtension` mapping
> is maybe 80 lines.

**Two hard warnings.** **`Profectus`** (Eastern Republic capstone) completes a
**random research project** every `(5 + n) × 60000` ticks, forever, excluding only
techprint/analysis/mechanitor/anomaly projects. **It will hand you industrial and
spacer research for free**, unilaterally destroying the era arc. **[V]** And **MP:
BLOCK, not "use with care."** `Dialog_SenatorInfo` generates a quest and adds it to
`Find.QuestManager`, consumes **global `Rand` from a UI window**
(`if (Rand.Chance(0.15f))`), destroys caravan silver, and calls `GainFavorOf` — which
completes research and grants permanent perks — all from a button handler. **The
senator dialog *is* the mod, and it desyncs on the first bribe.** **[V]** It also has
an undeclared dependency on VE Outposts (`using Outposts;`).

Its economy is the project's named refusal case three times over: **`VFEC_Bronze`**
(StoneChunks + Steel → a slightly-worse steel; its own research description says so),
**`VFEC_BlocksConcrete`** (a second stone-block noun plus a dedicated 83-hour press),
and **`VFEC_Tyrian`** (Cloth ×150 → Tyrian ×150 over ~20 in-game days, whose only
property is market value — literally converting a resource so you can convert it
again). **[V]** `technical-findings.md` already records that it contributes **zero**
Medieval research projects.

**Verdict: BLOCK the code, BLOCK the economy, PULL the art (193 PNGs incl. 24
hand-drawn perk icons), REBUILD the architecture.**

### 5.6 Medieval Overhaul `3219596926` — the chains, enumerated

`technical-findings.md` already carries MO's settings-menu trap, the schematic-cache
desync, `metalChain` vs `vanillaMine`, the 395-ThingDef `component_replace`, the four
electric successors, the iron-locked items and the measured tier totals. What this
pass adds is the full production-chain enumeration and the accept/refuse call.

**Supplies. [V]** 1,279 ThingDefs (~1,197 concrete), 226 RecipeDefs, **54
ResearchProjectDefs** (6 Neolithic + ~47 Medieval, 200–4000), **81
`ProcessorFramework.ProcessDef`** (72 live), 113 PawnKinds, **18 FactionDefs**, 82
TerrainDefs, 65 Hediffs, 6 new architect tabs, 2 new StuffCategoryDefs (`Textile`,
`Hide`) **stamped onto vanilla and third-party defs**, 79 weapons/shields, 116
apparel, **49 production buildings**. **4,119 PNGs / 86.9 MB** — Building 1,650, Pawn
1,350, Item 675. The best medieval art library that exists for RimWorld.

**Research slots in, does not replace.** `1.6\Patches\Core\Change_ResearchProjectDef.xml`
(108 ops) only *re-tabs* 16 vanilla projects; `Remove_Old_Recipes.xml` deletes only 4
of MO's own. Own bench tier: `DankPyon_AdvancedResearchBench` hard-gates the upper
medieval projects. **[V]**

**~45 intermediate ThingDefs in six families. Every one fails the "need with an
expiry date" test. [V]**

| Family | The chain | Call |
|---|---|---|
| **Metal** | `MineableIron → IronOre → [Furnace \| Smelter] → IronIngot → + Coal → Steel`. Also PlasteelOre, SilverOre, GoldOre | 🔴 **REFUSE** — three steps to reach vanilla `Steel`, and `DankPyon_IronIngot` is the costList currency for nearly every MO weapon, armour and bench |
| **Wood** | `DankPyon_RawWood → WoodLog` at Trestle/SawTable/WindMill/WaterMill; `RawWood → Coal` (CharcoalPile, 3d); `WoodLog → Tar`; **paper is three steps** (`RawWood → Mixture_Paper → Press → Paper`) | 🔴 **REFUSE** — MO **demotes vanilla `WoodLog` to a second-stage product**, and `MOSetting_WoodChain.xml` rewrites `harvestedThingDef[text()="WoodLog"]` **globally**, retargeting every other mod's trees |
| **Leather** | `butcher → Hides → [RawhideRack] → Leather_Rawhide`; `Hides → [TanningRack \| TanningDrum] → DummyLeather`; `wood/food → TanningLiquor` | 🔴 **REFUSE** — and `DankPyon_DummyLeather` exists **only so the processor UI has an icon**; the real output is swapped by a `ProcessorExtension`. 26 of the 72 live ProcessDefs are hide→rug conversions duplicated medieval/industrial |
| **Cloth** | vanilla `Plant_Cotton` no longer yields `Cloth`: `Plant_Cotton → RawCotton → Cloth` at SpinningWheel; plus Flax→RawFlax→Linen, Silkworm→Silk (6d) | 🔴 **REFUSE** |
| **Food** | `Cereal → Flour → MealBread`; `Fat + Salt → Tallow`; `RawHerb → Spices → + MeatRaw → Sausages → grilled`; `Milk → MealCheese`; `RawApples → MincedApple → JuiceApple → JuiceAppleUnfermented`; `RawGrapes → MustWine → Wine`; `Clay → BlocksClay` | 🔴 **REFUSE** — four-step meal chains are routine |
| **Alchemy** | every potion is `Mixture_X → X` in the Cauldron, 3–15 days | 🔴 **REFUSE** |

> **The escape hatch does not deliver the Waystone position. [V]** MO ships load-time
> toggles (`leatherChain` / `woodChain` / `clothChain` / `metalChain`, all default
> `true`) that genuinely delete recipes and unhook benches. **But `metalChain=false`
> does not remove the ingot — it removes the *ore*:** it sets
> `DankPyon_MineableIron.mineableThing` to `DankPyon_IronIngot` and rewrites the
> rusted-armour butcher products to ingots. **You now mine ingots**, and
> `DankPyon_IronIngot` stays in every trade screen and costList for the rest of the
> run.

**MP: fails.** No `Multiplayer.API`. Hard desync in `Plant_PlantCollected.Postfix` —
`Rand.Chance(settings.soilWearChance)` gates `terrainGrid.RemoveTopLayer()` and, via
`settings.autoPlow`, `GenConstruct.PlaceBlueprintForBuild()`: per-client sliders
driving RNG **and terrain mutation** on every harvest. Ten-plus Harmony `Prepare()`
methods return mod settings, so **clients with different settings load different
patch sets**. 33 `Rand.` sites, one correctly seeded. **[V]**

**Save permanence: catastrophic, decide before day 1.** ~1,197 ThingDefs, 18
FactionDefs (with settlements, relations and quests), 113 PawnKinds, 82 TerrainDefs,
6 architect tabs, 2 StuffCategories stamped onto foreign defs, and — because
`MOSetting_WoodChain` rewrote `harvestedThingDef` globally — **every tree on every
map**. **[V]**

**The reusable idea:** the three-rung ladders `DankPyon_{Basic,Military,Noble}{Blades,Maces,Polearms}`
at 300/600/1000 — three rearmament moments in the long middle with no new resource.

**Verdict: SPLIT.** Art **PULL** — 4,119 sprites, the largest single source in the bin.
Production chain **BLOCK**, emphatically. Research shape and tier ladders **PULL as
reference**. Assembly **BLOCK** for MP.

### 5.7 VFE Medieval 2 `3444347874` — two mechanisms worth taking outright

**1,122 PNGs / 825 defs** — including ~440 heraldry files (§10.4), 128 apparel frames
at 16 per garment, 89 KCSG structure layouts, 143 symbols, 10 keeps, 170 backstories,
10 factions, 31 pawnkinds. **[V]**

> **There is no ammunition.** Every matchlock — `VFEM2_Gun_Arquebus`, `HandCannon`,
> `Musket`, `Flintlock` — pays its `Chemfuel` cost **at craft time only**
> (`…\1.6\Defs\ThingDefs_Misc\Weapons\RangedMedieval.xml:125-129, 220-224, 494-498,
> 594-598`) and fires forever. **[V]** VFE M2 already applied "keep the surface, cut
> the procedure" to gunpowder. Four weapons, one research, escalating without a new
> noun — the right shape for the long medieval middle. Copy verbatim.

> **Fourteen linkable facilities** — SmithingAnvil, ForgeBellows, TailoringLoom,
> ChiselRack, StoneClamp, CleaverRack, CarvingBoard, StonePolisher, ArtToolStand,
> NotesStack, ResearchBoard, SurgicalTools, AilmentsShelf, MannequinStand. Build a
> thing next to a bench, the bench gets better. **Pure surface, zero procedure, no new
> resource.** **[V]** This is how to fill medieval build-out time without inventing a
> noun. (`technical-findings.md` records that its `GenRecipe` patch is the working
> precedent for facility-driven quality, and that facilities are additive-only.)

**Cut on sight:** `VFEM2_Must` (grapes → must → wine; "must" was never a need),
`VFEM2_LeatherBoilpot` (keep `HardLeather` as a stuff, delete the pot), ~11 of the 16
alchemical draughts, and **`VFEM2_MannequinStand`** — the last because its 10%
ingredient discount is paid for by an **unbounded `RecipeDef` allocation leak**:
`ContractedRecipe()` `MemberwiseClone`s on every call against a live original into a
never-cleared static `HashSet`, hit from four call sites, two of which loop every bill
on a bench. **[V]**

**Accept, as genuinely good:** `SmokeleafLeaves → VFEM2_Hardweave` and
`Hay → VFEM2_Hayweave` (hayweave answers "grow fibre" at neolithic cost with a
deliberately inferior material), and `WoodLog → Chemfuel` at the alchemy bench
(output is a vanilla permanent; it just moves the unlock earlier). **[V]**

**Never use the `VFEM_MaynardMedieval` storyteller in MP** — its research-cost patch
caches on `lastCalculatedTick`, and the same helper is called from the research-tab
UI, so having the window open diverges the simulation. **[V]** Two lesser MP notes: three
unscribed `Dictionary<Pawn, float>` statics read in `SkillRecord.LearnRateFactor` and
`Thought_Memory.DurationTicks` give a joining client up to 200 ticks of divergent
learn rate; and `Dialog_Barter` is a bespoke trade window MP does not sync (pricing
*is* seeded — it is the transaction that is not). **[V]**

Its thesis — *"medieval technologies remain relevant even as you advance"* — is a
**different thesis from Archinity's**, which wants each era to hand off cleanly. Its
`LordJob_BurnAndStealColony` is a genuinely different demand, though: **raiders who
come to take and burn, not to kill**, reframing "defend the colony" from a combat
problem into a protect-the-stores problem. **[V]**

### 5.8 The Dark Ages art quarry

**Dark Ages: Medieval Tools `3028566550` — CC BY 4.0, and the best small idea in the
cluster.** 7 tool ThingDefs, 4 facility buildings, **0 research, 0 explicit
recipes**, 52 PNGs (plus **4 orphan sprites with no def attached** — free). **[V]**
The mechanic is 100% XML: each tool is a plain `BaseMeleeWeapon_*_Quality` with
`equippedStatOffsets`, occupying the **primary weapon slot**. Hammer →
ConstructionSpeed +0.10 / ConstructSuccessChance +0.08; Pickaxe → MiningSpeed +0.15 /
MiningYield +0.10; Cleaver → ButcheryFleshSpeed +0.20; Scythe → PlantHarvestYield
+0.15 / PlantWorkSpeed +0.2; **Hacksaw → MedicalOperationSpeed +0.20 /
MedicalSurgerySuccessChance −0.10**; Broom → CleaningSpeed +0.35; GuardBaton →
ArrestSuccessChance +0.20.

> **Nothing auto-equips, so a colonist gets the scythe bonus only while unarmed for
> combat. Specialisation costs combat readiness — free tension, no resource.** And it
> is era-portable by construction: a steel scythe still gives `PlantWorkSpeed` at
> Ultra. The DLL is cosmetic only.

⚠ **Hidden global side effect: [V]** `Textures\Things\Mote\Clean.png` sits at vanilla
`Mote_Clean`'s exact texPath — it **silently retextures every cleaning mote in the
game, forever.** No error, no def diff. Exactly the silent-failure class
`CODING_STANDARDS.md` warns about. Never take its MO sub-path
(`1.6\Mods\MOAdditions\Patches\PatchMOCosts.xml` rewrites all four facility costs to
`DankPyon_IronIngot`). **Verdict: PULL the art, RESTAT the mechanic, drop both DLLs.**

**Dark Ages: Crypts and Tombs `2963826335` — CC BY 4.0.** 22 concrete buildings, 2
research (300 + 450, both prereq'd off vanilla, both in the **vanilla Main tab**), 5
thoughts, **0 recipes, 0 terrain, 0 pawnkinds**. **85 PNGs up to 2048×2048, 42 of
them multi-rotation container sets** — the best art in the era cluster, coherent in
one register. Plus 8 orphan sprites. **Passes the expiry test without exception** —
all 22 are `stuff → terminal building`. **[V]** The safest code in the whole bin:
`WallTombs.dll` is **133 lines, one PlaceWorker, zero static fields, zero Harmony,
zero map generation.** **[V]**

**But removal is a one-way door for a reason worth naming:** the coffins, sarcophagi
and wall tombs are `Building_Sarcophagus` accepting `Corpses` — **removal destroys
every buried colonist** — and `DA_OssuaryWall` is `holdsRoof true`, so removal **drops
roofs**. **[V]** Two shipped bugs: defName typo `DA_DarkligtSepulchralStatue`, and
`DA_BloodflameSepulchralBrazier` points at the plain brazier texture. One greedy
unanchored xpath in `Patches\PatchMisc.xml` injects `DA_WallTomb` into every ThingDef
matching a meditation-comp shape, including other mods'. **Verdict: PULL the art,
RESTAT into your own defs, BLOCK as a live dependency** — not because it is unsafe,
but because you should not accept a never-uninstallable dependency for art you can
simply copy.

**Dark Ages: Beasts and Monsters `3472275628` — CC BY 4.0.** 20 animal races, 12 spawn
incidents, 7 abilities, 5 buildings, 22 materials including 12 leathers and two drug
chains, a hidden settlement-less `DA_Troll` faction, **347 sprites**. Touches only
`BiomeDef` — **zero race bleed**. Tuning lives in a **Def**. **[V]** One hazard: a
static, never-invalidated `Dictionary<Map, List<LocationCandidate>>` burrow cache a
mid-session joiner would populate from a different map state. **It adds world texture
without adding a people** — exactly what *"a trace of the exotic is flavour"* wants.
**Verdict: PULL, and treat as the art quarry.**

### 5.9 Neolithic art — and a content-retirement primitive

**208 PNGs across three mods. [V]**

**Tribal Furniture `3671245310`** — 138 PNGs, 16 ThingDefs, 0 research, 0 recipes. Its
seven 12-file bench folders are **three stuff-appearance variants × 4 rotations**,
resolved by a custom `Graphic_Appearances_Multi` — **unusable without the DLL** unless
rewritten to plain `Graphic_Multi`. **[V]**

> **The idea worth stealing: content retirement.** Its `lockToTechLevel` setting
> stamps `<minTechLevelToBuild>Medieval</minTechLevelToBuild>` onto ~18 **vanilla**
> furniture defs and `<maxTechLevelToBuild>Neolithic</maxTechLevelToBuild>` onto its
> own 16. Decompiling vanilla `Designator_Build:117/121` confirms the gate reads
> `Faction.OfPlayer.def.techLevel` — **a FactionDef field vanilla never advances**, so
> the author's own tooltip says *"Recommended to be used with a mod that advances tech
> level."* **[V]** Four lines of XML plus a tech-level advancer, and it **retires** old
> answers instead of accumulating them — the day-600 build menu is not fourteen eras
> deep. It lights up every respecting mod in the load order.

Delete `XER_TribalRefinery` (`WoodLog → Chemfuel`, gated `DrugProduction`, tooltip
*"gives access to biofuel for tribals earlier than normal"*) — converting a resource
so you can convert it again, verbatim. Its off-switch is a **mod setting** read inside
`PatchOperation.ApplyWorker`, which **conjures the entire ThingDef into existence**:
mismatched settings mean one client has a ThingDef the other does not. **[V]**
**Verdict: REBUILD — take the pattern, leave the package.**

**ETRT Tribal Apparel `3545351721`** — 60 PNGs all at 512×512, including
`FSFurCoat` and `FSDesertRobe` with **complete five-body-type worn graphics** (the
expensive part most mods skip). 9 ThingDefs, all Neolithic, craftable at a
`CraftingSpot` from turn one. **No assemblies.** Passes the expiry test. **[V]**
**PULL.**

**VWE Tribal `2454918552`** — 10 PNGs, 30 Neolithic weapon/tool defs, no assemblies.
Passes on 6 of 7 — `VWE_Weapon_FireBomb` costs 80 `Chemfuel`, a neolithic item priced
in an industrial intermediate. **[V]** **PULL**, and restat the firebomb's `Chemfuel` cost.

**Adaptive Primitive Storage `3400037215`** — 83 PNGs of genuine early-era storage:
Granary, CoveredClayPot, LargeLogPile, stone and wood cellars. 28 defs, no assembly.
**[V]**

**Rustic Workbenches `3761824516`** deserves special mention: **zero defs, zero
assembly, 93 PNGs, two patch files of nothing but `PatchOperationReplace` on
`graphicData/texPath`** for FueledStove, CraftingSpot, Brewery, HandTailoringBench and
the rest. **[V]** It is "reskin before you rebuild" taken literally — a vanilla bench
that *looks* medieval without adding a bench. Note it also silently changes
`DrugLab`'s `size` and `costList`: a balance change riding along with a retexture.

### 5.10 Ushankas Glittertech `3522676478` — correcting the premise

> ⚠ **The working assumption was that this is the Glitterite villain's gear. It is
> not.** **[V]** `\3522676478\1.6\Defs\` contains **0 FactionDefs, 0 weapon ThingDefs,
> 0 apparel ThingDefs.** Exactly **one** PawnKindDef — `USH_AncientGlittertechSoldier`,
> `defaultFactionDef AncientsHostile`, wearing *vanilla* apparel tags
> (`SpacerMilitary`, `IndustrialMilitaryAdvanced`) and carrying *vanilla* `SpacerGun`
> weapons, `apparelMoney 5000~10000`, `biocodeWeaponChance 0.85`.
>
> So `Archinity.Glitterites` is rebinding **a single PawnKindDef onto a faction the
> project supplies** — there is no FactionDef here and no bespoke gear to dress it in.
> For an actual Ultra-tier arsenal the source in this bin is **GravTech** (§5.11),
> which can be lifted directly.

**Supplies. [V]** 103 ThingDefs, 62 RecipeDefs, **20 ResearchProjectDefs**, 24
Hediffs, 4 StatDefs, **3 QuestScriptDefs**, 3 IncidentDefs, 91 PNGs. Buildings:
Fabricator, MolecularDisassembler, NeutroamineExtractor, ResearchProbe, MemoryPylon,
NeuroclearConsole, Telepad, Biocoder, MountainRaiser, SolarFlareBank, Repairer,
Targeter, ADP turret + IED, MobileComforter, Glittercrate, GlittershipChunk, 5
Glitterpanel walls. Implants: CryogenicNexus, Glitterlink, Golden/Plasteel Skin and
Teeth, MemoryProjector, TelepadIntegrator.

> **The mechanism worth taking.** `USH_GlittertechFabricator` uses **`formingTicks` +
> `gestationCycles`** (the vanilla gene-assembler shape), not an item chain — base
> abstract `workAmount 600`, `gestationCycles 5`, `formingTicks 18000`,
> `skillRequirements Intellectual 6`. And **most recipes make things that already
> exist**: MedicineUltratech, Synthread ×64, Hyperweave ×64, Plasteel ×24/96, Gold,
> Jade, MechSerumHealer, MechSerumResurrector, all 12 Neurotrainers, plus
> ComponentIndustrial and Neutroamine via a generator that **reverse-derives**
> extraction recipes from every drug recipe in the game. **[V]** One bench, one
> looted key, previously-uncraftable goods become craftable. Zero intermediate items.

**Expiry test: passes, unusually well.** Two new resources. `USH_Glittercore` is one
step from ComponentIndustrial + Plasteel + Uranium — a key, not a chain.
**`USH_Glitterheart` is not craftable at all**: *"extracted from fallen glittership
chunks, found in prestige quest awards and occasionally in ancient structures."* Loot.
`USH_DisassembleMechSlag → Steel ×10 + Plasteel ×2` is a **sink**. **[V]**

**Quests re-gate cleanly.** 3 QuestScriptDefs + 3 IncidentDefs + SiteParts +
StructureLayouts, and `QuestNodes.cs:135` seeds properly with
`Rand.PushState(Gen.HashCombineInt(Find.World.info.Seed, mapParent.Tile))`. **[V]**
`Archinity.Glitterites` already moves `USH_GlittertechOutpost` /
`USH_GlittertechFacility` from day 45 / 1000 points out to day 240–300 / 2500.

**MP: fails on settings only, and all four are fixable.**
Full C# source (75 files), **zero threading, zero `System.Random`**. The four:
`FormingSpeedMultiplier` in `BillTick()` (production speed per client),
`PylonMoodMultiplier` and the positive/negative mood multipliers in `MoodOffset()`
(**mood drives breaks**), `DoubleNeutroamineCost` at def-gen, and a cosmetic skin one.
Minor: an unseeded `RandomInRange` in a WorldComponent constructor. **[V]**

**Verdict: PULL the mechanism, the 91 textures, the 20-project tree and the implant
set; FIX the four settings reads; do not expect villain gear.** It ships full C#
source, so it is the cheapest mod in the bin to fork and repair outright.

### 5.11 The Spacer tier — gravship group


**GravTech `3545374124`** — 90 ThingDefs, 24 recipes, **7 research** (`GravEngineBuild`
3000 Spacer → six at Ultra, 3000–6000), 130 PNGs. **The Ultra arsenal the project
actually needs:** GravBlaster, GravBeamCannon, GravRifle, GravHammer + Bladelink,
GravBarrier ability, GravBelt/GravPack apparel, GravSpine/Armor/Stomach/Hands
bionics. **[V]** Expiry: mostly passes — most recipes make *vanilla* things
(`Steel+Chemfuel+Silver → Plasteel ×35`, `Steel → ComponentIndustrial ×5`,
`ChunkSlagPlasteel → Plasteel ×15` as a sink), and Gravitonium/Graweave are
single-step stuff materials. 🔴 **Delete `RoughGravlitePanel`:**
`ChunkVacstone → RoughGravlitePanel → [ElectricCrematorium, "scorch"] → GravlitePanel`
— three steps, and its own description admits it (*"A blank for a gravlite panel…
Final processing requires the crematorium"*), **while the one-step alternative already
exists in the same mod** (`BlocksVacstone + Plasteel → GravlitePanel`). **[V]** MP:
594 lines, **zero `Rand.`, zero threading, zero static collections** — one hazard,
`ApplySettings()` writing into live `CompProperties` (radius, power, `statOffsets`,
`maxDistance`) from an Apply button. **RESTAT** — and fix or bypass that Apply path,
which is the only real objection.

**Vanilla Gravship Expanded Ch1 `3609835606`** — 165 ThingDefs, 8 research, only 4
RecipeDefs, 523 PNGs. Ship weapons, 10 compact benches, heatsinks, Agrocell,
bunk/medbay beds, four console types, two engine tiers, 7 compressed stuffs, **6
mechanoid ship parts (a ready antagonist fleet)**, escape pods. **[V]**

> **Expiry: passes near-perfectly, and it is the model.** Only **3 new items** in 165
> ThingDefs — OxygenCanister, Astrofuel, Oxyalgae. The sole conversion is
> `Chemfuel → Astrofuel`, one step. **Oxygen is a *network*, not an item chain** — a
> permanent need with a permanent answer. Philosophically the best-designed mod in
> the bin. **[V]**

MP: four settings reads, the worst being `maintenanceLossMultiplier` scaling
deterioration **every tick**. Covered by the compat layer. Save permanence high — most
of the 165 are structural ship parts. **PULL as a dependency, do not lift art, fix the
four reads.**

**More Gravship Workbenches `3714981583`** — 8 ThingDefs, 39 PNGs. **MP: clean** — 263
lines, zero `Rand.`, zero threading, zero statics. **[V]** One latent NRE:
`LTS_Building_NutrientGrinderAndHopper.Notify_ReceivedThing` does `Contents.Add(...)`
but `Contents` is initialised only inside `ExposeData`'s load branch, so a freshly
built grinder throws on first item received. **[V]** It uses VEF's `copyLinksFrom` /
`inheritRecipesFrom` idiom seven times each — **the most transferable small idea in
the group.** **PULL as a dependency.**

**Biotech for Gravship `3722358861`** — 80 ThingDefs, 140 PNGs. Compact ship variants
of Biotech buildings; **passes the expiry test** by re-housing existing needs into
ship-sized boxes — "the need is permanent; the answer changes shape." MP: one correct
`Rand.PushState(thingIDNumber ^ startTick)` block, but an **unseeded `Rand.Value`
assigning genes**, which are permanent pawn state. **[V] / [I] on the consequence —
audit before use.**

### 5.12 [SYR] Processor Framework `3210544395` — better mechanism, worse influence

**Yes, it is exactly a generic XML-driven `input → time → output` comp, and it is
genuinely excellent engineering.** `ProcessDef` exposes `ingredientFilter` (a full
`ThingFilter`), `processDays`, `capacityFactor`, `efficiency`, `usesTemperature` with
safe/ideal ranges and `ruinedPerDegreePerHour`, **weather-driven speed**
(`sunFactor`/`rainFactor`/`snowFactor`/`windFactor`), unpowered/unfueled factors,
`filledGraphicSuffix` (auto-swaps the texture), **`usesQuality` + a 7-tuple
`qualityDays`** (quality accrues over time), `destroyChance`, `bonusOutputs` with
chances (**it can even spawn pawns**), and `useStatForEfficiency`. Free UI: progress
bar, product icon, two auto-injected inspector tabs. **[V]**

**Cannot express:** multiple *simultaneously required* inputs (the filter is a set of
alternatives, so `A + B → C` is impossible), no skill requirement or XP, no pawn work
amount (wall-clock, not labour), no bill counts, no research prereq on the process.

**A complete shipping processor is 11 lines** — `VFEM2_Wine` gets quality-over-time
fermentation, a progress bar, an icon, temperature spoilage and a player-facing tab.
Versus a bespoke bench at ~50 + ~30 lines plus an optional WorkGiver.

> **And that is precisely the problem. Medieval Overhaul, its largest consumer, has 72
> live ProcessDefs — 26 of them just hide→rug conversions duplicated
> medieval/industrial.** Because each costs 11 lines, there was never a moment where
> adding "rawhide → tanning → leather" felt expensive enough to question. **The
> framework made the anti-pattern free, and MO built its whole economy out of it.**
> Waystone's "suspect on sight" rule needs implementation friction to enforce it, and
> PF removes exactly that friction.

**MP: fails, and it regressed.** It shipped `0MultiplayerAPI.dll` in 1.3 and 1.4; the
1.5/1.6 continued build ships only Harmony. **[V]** Worst defect:
`PF_Settings.initialProcessState` in `CompProcessor.Initialize()` decides whether a
new processor spawns with process[0] enabled, all, or none — **every processor spawns
with a different enabled set per client, on every build.** Plus `defaultTargetQualityInt`,
and `Rand.Chance(destroyChance)` followed by a per-client setting gating a
`PlaceBlueprintForBuild`. **[V]** It *is* covered by the compat layer.

**Verdict: do not adopt it as a house mechanism** — on the design grounds above: it
makes the intermediate-item anti-pattern free, which is exactly the friction the
Waystone wants preserved. The settings-read hazard is a secondary strike. If used at all, cap
the count deliberately — three processors for the whole run — and only for things that
are genuinely *time* rather than *labour*; vanilla's fermenting barrel already covers
most of it. **And note: if MO is used at all, PF comes with it as a hard dependency.**

### 5.13 Gear ladders by tier

Counted from `techLevel` tags. **[V]**

| Mod | Neolithic | Medieval | Industrial | Spacer |
|---|---:|---:|---:|---:|
| Vanilla Weapons Expanded `1814383360` | 8 | 26 | 49 | 30 |
| Vanilla Apparel Expanded `1814987817` | 17 | 26 | 177 | – |
| Vanilla Armour Expanded `1814988282` | 12 | 60 | 60 | 46 |
| VWE Tribal `2454918552` | 30 | – | – | – |

`technical-findings.md` already records the binding constraint: the Neolithic armour
rung count is **1** for leather and **0** for steel, because the only Neolithic apparel
venue is `CraftingSpot`.

---

## 6. Design area (b) — the world

### 6.1 Races and containment

`technical-findings.md` already records that neither VRE Starjack nor VRE Archon
injects xenotypes into vanilla factions. This pass adds the inventory and the
bleed audit.

**VRE Archon `3067715093` — the closest thing to Archinity's Archons that exists.**
**[V]** `VRE_Archons` in `…\1.6\Defs\FactionDefs\Factions_Hidden.xml` is remarkably
on-spec: `hidden: true`, `displayInFactionSelection: false`, `permanentEnemy: true`,
`techLevel Archotech`, `ParentName="FactionBase"` (which sets no
`settlementGenerationWeight`, so **zero settlements on the world map**),
`xenotypeSet Inherit="False"` with `VRE_Archon: 999`, and `rescueesCanJoin: true`.
One pawnkind (`ArchonWarrior`, combatPower 450, apparelMoney 10000,
`initialResistanceRange 1` — trivially recruitable if captured). 23 genes including
`VRE_Transcendent`. **[V]**

Three design hooks worth taking, all unprotectable structure:
- **The gear you cannot use.** Both gear pieces are hard-gated to the
  `VRE_Transcendent` gene by a Harmony patch on `EquipmentUtility.CanEquip`, plus
  `ApparelScoreGain` returning `−1000f` so colonists will not even try. **The
  archoblade sits in your stockpile as a permanent question.** A quest hook made
  entirely of a restriction. **[V]**
- **The storm as herald.** `VREA_PsychicStorm` fires (`baseChance 1`,
  `minRefireDays 45`), doubles map-wide psychic sensitivity, and **only then** queues
  `VREA_ArchonRaid` (`baseChance 0` — it can never self-fire). A Harmony postfix on
  `FactionCanBeGroupSource` **actively blocks the Archons from ever being picked as a
  normal raid faction.** **[V]**
- **The kidnap conversion.** Any pawn the Archons kidnap is **converted to the
  `VRE_Archon` xenotype**. Combined with `rescueesCanJoin` and
  `initialResistanceRange 1`, that is a complete three-beat quest with no extra
  machinery: *they take one of yours → you find them later → they come back changed,
  and they can be recruited.* **[V]**

**Art:** 268 PNGs — 18 body sprites (a complete set), 30 head attachments, 33
hairstyles, 120 archoblade frames, 16 archoplate, 23 gene icons, a faction icon.
**[V]** All of it usable — a complete Archon visual identity with no authoring cost at
all. *(The original entry priced the rebuild at ~110 pawn-render sprites plus ~25 UI
icons on the assumption permission was needed. Struck.)*

One MP hazard: `Rand.Chance(VREArchonSettings.archonRaidSpawnChanceInPsychicStorm)`
inside `IncidentWorker_PsychicStorm.TryExecuteWorker` — a client-local slider deciding
a branch on a shared draw. **[V]** `Archinity.Pacing/Patches/Faction_Archons.xml`
already pushes `earliestRaidDays` to 999999.

**Verdict: RESTAT the design, REBUILD the code, PULL the art.** Do not ship it, or you get a
second competing Archon faction.

**VRE Starjack `3531912428` — not what the name promises.** **[V]** **It defines no
faction, no pawnkind, no apparel, no weapons, no buildings, no incidents, no
settlements.** 18 non-texture files and **15 PNGs** (a tail, 10 gene icons, an ability
icon, a background). The Starjack xenotype itself is **vanilla Odyssey**; this mod
patches genes onto it. So **the Starjack Free Companies faction is 100% REBUILD** —
FactionDef, icon, pawnkinds, gear, settlements and the ally/betray arc all have to be
authored, which is what `Archinity.Drifters` is already doing.

Two reasons not to ship it anyway. Its `Gene_Randomizer.PostAdd` does
`allAstrogenes.OrderBy(x => Rand.Value).Take(starjackGenesAmount)` where the count is a
**client-local setting** — different gene counts *and* different numbers of `Rand`
draws per Starjack spawn. **[V]** And its "astrogenes" are **runtime-generated defs
cloned from every qualifying `GeneDef` in the whole modlist**, so adding or removing
any unrelated gene mod later changes the astrogene set and orphans genes already saved
on living pawns. **[V]** **Verdict: BLOCK.**

**The vanilla bleed you must patch regardless of modlist. [V]** Odyssey gives
`TradersGuild` a Starjack chance of **0.25** and `Salvagers` **0.1**
(`…\Data\Odyssey\Defs\FactionDefs\Factions_Misc.xml:75, 232`). A quarter of every
traders-guild pawn is a Starjack out of the box.

**Xenotype Spawn Control `2891975564` — MIT, full source, and the answer is "bake,
don't ship."** Its entire effect on vanilla xenotypes is **`FactionDef.xenotypeSet`
mutation** via an `AccessTools.FieldRef`, executed at `[StaticConstructorOnStartup]`
from a **client-local `ModSettings` file that never travels with the save**. **[V]**
It also calls `Rand.Range` on **every** pawn-gene generation, even with nothing
configured. Two players with different settings boot with structurally different
FactionDefs and consume different numbers of draws.

> **Anything XSC can do, a static `PatchOperationReplace` on
> `xenotypeSet/xenotypeChances` can do deterministically and identically on both
> machines.** Run XSC solo, find the numbers, read them out of
> `Config\Mod_bs.xenotypespawncontrol_ModSettings.xml`, bake them into an Archinity
> patch file, and remove XSC from the co-op modlist. One XML file makes "no race
> bleeding" a property of the modpack rather than a per-player configuration both
> players must remember to keep synchronised.

**Bleed-if-simply-enabled — the four to block. [V]** VRE **Saurid** declares
`<replacesFaction>OutlanderRough</replacesFaction>`, which **deletes a vanilla faction
from world gen**. VRE **Android** patches the abstract `OutlanderFactionBase` and
`PirateBandBase` — the broadest bleed in the bin. VRE **Waster** rewrites the *vanilla*
`Waster` xenotype in place, so a `Patches/` grep for faction xpaths would miss it
entirely. VRE **Hussar** rewrites the vanilla `Hussar` xenotype **and** lets
client-local settings determine the GeneDef count at load time. Each is
counter-patchable, and none returns enough content to be worth it.

**Faction – Elves `3726293423`** and **Dwarves of the Rim `2939964151`** are blocked on
era grounds: four **medieval** factions and one **Industrial `naturalEnemy`** faction
respectively, all `requiredCountAtGameStart: 1`, present before the player has a stone
axe. **[V]** Elves also uses unprefixed defNames (`MeleeWeapon_Glaive`, `Rapier`) that
will silently last-one-wins against MO and VFEM2.

**Uncompromising Tribal Faction `2571594852` — MIT, 89 lines of C#, no Harmony, no
settings, no static state, one `Rand` call inside a synced `Impact()`. The only mod in
the bin with essentially zero multiplayer risk.** **[V]** Three fire pawnkinds injected
into `FactionDef[@Name="TribeBase"]` plus the Biotech impid and neanderthal tribes, a
great flamebow, an AI-usable smoke bomb. **Zero xenotypes, zero race bleed.** For a
campaign that spends years in the neolithic, the highest value-per-risk item here.
**PULL.**

### 6.2 Faction politics

**Faction Territories and Vassalage `3626725895`** — the most design-aligned mod in
the bin. **[V]**
- **Territory** is a multi-source Dijkstra flood fill from every settlement across the
  world grid, weighted by terrain difficulty, road difficulty and hilliness, rendered
  through Map Mode Framework. Derived and cached, **never saved**.
- **Vassalage:** destroying an enemy settlement offers raze / cede to an ally /
  vassalise. A vassal outpost keeps the original faction's icon and counts as your
  territory. **Tribute flows inward**, accruing per outpost per day multiplied by **the
  vassal's tech level**. **Your vassals can then be invaded** — a real cost of empire.
- **Invasions:** every ~720,000 ticks a faction besieges a rival. You can caravan in
  and fight for either side on a real map. If you never show,
  `RollWinner(attackerWeight, defenderWeight × 1.15)` resolves off-map on
  `GetTechWeight(faction.def.techLevel)`, **deterministically seeded**. Winner takes the
  settlement.
- **Expansion:** factions start settlements at a tile that completes at `completeTick`;
  you can attack the site to stop it permanently.
- **`CaravanIncidentEntryDef`** is a ready-made, def-driven, **era-gated encounter
  table keyed to whose land you are standing on** — flags over
  `{Hostile, Neutral, Allied, Royalty, Animal, Neolithic … Archotech}` evaluated against
  the territory-owning faction's tech level. The closest anything gets to *"you deal
  with factions at your own era."*

MP: **HIGH but specific.** `VassaliseComponent` calls **`Find.TickManager.Pause()` and
re-opens a letter every 30 ticks from inside `GameComponentTick`** — that alone breaks
a lockstep session; disable `enableDefeatedSettlementVassalisePrompt`. **[V]** Every
interval and multiplier is client-local. No threads, and the RNG that matters is
deterministically seeded — the author was thinking about determinism even if not about
MP. Removal is a one-way door and settlements that changed hands stay changed.
**PULL with surgery.**

**Rim War `2222935097` — MIT, and MP-catastrophic by construction.** The reference
implementation of a living political board: per-faction behaviour archetypes, a points
economy per settlement, real `WarObject` world objects that walk the globe, settlements
that change hands, vanilla goodwill fully wired, a comms-console dialog transpiled to
add Request Scout / Warband, and a rival-faction victory condition. **[V]** And:
`RocketTasker<T>` constructs real `System.Threading.Thread`s applying results on
whatever later tick they finish, `threadingEnabled` **defaults true**, a fresh 30-field
`SettingsRef` is constructed *inside* `WorldComponentTick`, and War/Peace/Alliance
buttons mutate shared state from `Widgets.ButtonText` while `TributeSilver` walks
`Find.AnyPlayerHomeMap.listerThings` and `Destroy()`s silver from a click handler.
**[V]** **BLOCK — and harvest the design into deterministic, synced code.**

**[SR] Factional War (fork) `3423264477` — Apache 2.0**, the best cheap answer to
*"factions want things from each other and not only from you."* Four incident families:
two hostile factions fight **on your map** and you choose whether to join; a contention
site; a shelling site; a temporary camp. Detailed AI — plunder, kidnap, retreat,
execute the downed — and it **never writes vanilla goodwill**, exactly what you want
from a co-tenant. **[V]** Two MP fixes, both settings: `threatPointFactor` multiplies
points inside `PawnGroupMakerUtility.GeneratePawns`, and `DiscardPawns()` GCs world
pawns on a client-local bool — a divergent *deletion*, worse than a desync. **Gap:** it
filters by points and `earliestRaidDays`, not tech level. **PULL, both settings pinned,
with an era gate added.**

**Sensible Factions `3531306011`** — one Harmony postfix on
`WorldGenerator.GenerateWorld` that redistributes already-generated settlements by
biome affinity, preserving each faction's count exactly. **Zero runtime cost, zero
saved state, removing it does literally nothing.** **[V]** Quietly essential:
*"relationships form slowly and through encounter"* requires that factions **have
places**, and vanilla scatters them uniformly. **Gotcha: it is inert until
configured** — `allowedFactionDefNames` starts as an empty `HashSet`. **[V]** **PULL.**

**Map Mode Framework `3296654393` — MIT**, actively maintained, upstream at
`github.com/nozomemu/MapModeFramework`. Its async work is confined to mesh and
region-cache generation and feeds no gameplay state. **[V]** Hard dependency of Faction
Territories. Its real value: *"standing should move on its own, and the movement should
be visible before it becomes a crisis"* — Archinity could ship its own `MapMode`
subclasses (era reach, faction standing, threat pressure) on this framework.
**PULL.**

**Faction Customizer `3336572602`** — `technical-findings.md` already records that it
cannot remove factions and is pre-landing use only. Adding: its
`Dialog_ModifyFactionRelation.SaveChanges` sets `relation.kind` **without calling
`Faction.Notify_RelationKindChanged`**, skipping hostility letters, lord re-evaluation
and every downstream listener. **[V]** Its edits persist without it. **PULL as a
world-setup tool, disabled before the run.**

**Better Traders Guild `3684587591`** — orbital trade settlements with hand-built
interiors, ~30 room workers, rotating traders, entrenched defenders, two quests, two
scenarios. Requires Odyssey. **Actively hostile to the premise:** orbital bases and
shuttles from day one is a vending machine parked in the sky. Client-local settings
feed **map generation**. `technical-findings.md` already records its `SpaceSettlement`
patch-sequence trick as a reusable template. **DEFER to Spacer tier, or drop.**

**Milky Way `3773448562`** — miscategorised. It is a **GUI widget toolkit**;
`grep -c "Faction"` = 0, no `Defs/` folder at all. **[V]** Keep only if something
depends on it.

---

## 7. Design area (c) — the questline

**The Chronicle is authorable in pure XML today, with VEF as the only new dependency
and no second assembly.**

### 7.1 What vanilla already gives you

Vanilla 1.6 ships **306 distinct `QuestNode_*` types** **[V]**, and authors complete
"go there and take it" quests in nothing but XML —
`…\Data\Core\Defs\QuestScriptDefs\Script_BanditCamp.xml` is the canonical reference and
contains zero C#. **[V]**

| Node | Why it matters |
|---|---|
| `QuestNode_GenerateThing` | `<def>`, `<stackCount>`, `<storeAs>` — makes **one exact named Thing**, no ThingSetMaker roulette |
| `QuestNode_AddItemsReward` | turns `$items` into a real `Reward_Items` part with the standard "you will receive" UI |
| `QuestNode_GetSiteTile` | has **`allowedLandmarks`** (`List<LandmarkDef>`) and `selectLandmarkChance` — force a beat onto a specific *kind of place* |

`QuestNode_GenerateThing` + `QuestNode_AddItemsReward` is the **named, deterministic
reward that does not fail**, in pure XML, with no mod dependency. **[V]** This extends
the `QuestNode_SetItemStashContents` precedent already in `technical-findings.md`.

### 7.2 The chain primitive — VEF `QuestChainExtension`

A `DefModExtension` on any `QuestScriptDef`. **[V]** Full XML surface:

```
conditionSucceedQuests / ticksSinceSucceed
conditionFailQuests / ticksSinceFail
conditionSucceedQuestsCount        "N successes of X"
conditionEither                    blocks if that quest was ever accepted
conditionMinDaysSinceStart
requiredResearch                   <-- the era gate
isRepeatable / mtbDaysRepeat
grantAgainOnSuccess / OnFailure / OnExpiry + daysUntil*
questChainDef                      groups the chain, gives it a UI icon
```

`GameComponent_QuestChains` re-evaluates on new game, load, **every quest completion,
every quest expiry, and every research project finishing** (a Harmony postfix on
`ResearchManager.FinishProject`). State is scribed. **[V]**
`technical-findings.md` already records `requiredResearch` and its TechBlock tier-lock
mapping; this is the rest of the surface.

**The reference implementation is on disk and is ~40 lines.**
`…\3618306875\1.6\Defs\Quests\` — a `QuestChainDef` plus six `QuestScriptDef`s whose
entire topology lives in `modExtensions`: AncientLabComplex (day 90–120) →
ArchiteControlVault → SpliceframeBlacksite → {InhibitorResearchLab |
AncientResearchVault} → ArchiteArraySite. **A 6-beat, branching, save-persistent main
questline whose topology is XML.** **[V]**

**Two bugs to design around. [V]**
- **`grantAgainOnExpiry` is broken** — it passes *ticks* into a parameter named
  `mtbDays`, so `60` becomes an MTB of 3.6 million days. `grantAgainOnFailure` and
  `grantAgainOnSuccess` work.
- **Duplicate-suppression lives only in `TryScheduleQuest`.** `FutureQuestInfo.TryFire()`
  calls `CreateQuest()` with no guards.

### 7.3 The "take the thing from the place" primitive

`VEF.Buildings.LootableBuilding`. When a pawn opens it:
```csharp
Find.SignalManager.SendSignal(new Signal("LootableBuildingOpened", SUBJECT=<site MapParent>));
QuestUtility.SendQuestTargetSignals(mapParent.questTags, "LootableBuildingOpened", …);
```
Contents are a fixed `<contents>` list — deterministic, named, cannot fail. It resolves
through `PocketMapParent.sourceMap.Parent`, so it works from inside an underground
pocket map. Working template at
`…\3618306875\1.6\Defs\ThingDefs_Buildings\Buildings_Lootables.xml:220-252`. **[V]**

> **Critical distinction:** `LootableBuilding` sends the quest signal.
> `LootableBuilding_Custom` (the gizmo/hack-timer variant) **does not** — it only
> dispenses loot. **[V]**

Sibling: `VEF.Buildings.StudiableBuilding` — the "spend time at the site" verb, also
XML.

### 7.4 The authoring pattern — VFE Deserters `3025493377`

**1,519 lines of quest XML** across 15 files; ~160 vanilla node instances across 37
types versus ~52 `VFED.*` nodes across 25 types. **~75% of the quest graph by node
instance is stock vanilla.** **[V]**

**The technique:** `…\1.6\Defs\QuestScriptDefs\Base.xml` is one abstract
`VFED_DeserterQuestBase` — ~160 lines defining the whole shape of "travel to an
installation, do a thing, get out before the response timer." Every concrete mission is
then ~30 lines of `QuestNode_SubScript` with `<parms>`. **[V]** The base branches on
parms with `QuestNode_IsTrue` / `IsSet` / `Set` — conditional composition, in XML.
**Write `Archinity_ChronicleBeatBase` once; each beat becomes 30 lines plus prose.**

Its campaign *spine* is a C# state machine — VEF's `QuestChainExtension` is the newer
XML-native replacement for exactly that; VFED predates it.

Its reward design is worth stealing conceptually: **`Reward_Visibility`** — the third
choice in every mission is "take nothing, lower your heat." A cost dressed as a reward.
**[V]**

MP: **BLOCK as a dependency.** Currency spend and quest generation from UI buttons with
no sync, four settings read inside simulation. **[V]**

### 7.5 Reward types worth knowing

**`HonorDef`** (VFE Empire, `…\1.6\Defs\Misc\HonorDefs.xml`) — **named, permanent,
deterministic titles attached to a specific pawn**: *"First of {PAWN_possessive}
Name"*, *"{RANK} of {SETTLEMENT_label}"*, *"Destroyer of {FACTION_name}"*, *"Chosen of
{FACTION_name}"*. **[V]** The closest thing in the bin to a named reward that cannot
fail and is *not* an item — a permanent mark on a pawn, earned at a place. Exactly the
register the Waystone's "mark" language already speaks.

**`Permit_CallTechfriar.xml`** — 191 lines of **100% vanilla nodes**:
`QuestNode_GeneratePawn` → `SetAllApparelLocked` → `WorkDisabled` → `AddMemoryThought`
→ `ExtraFaction` → `JoinPlayer` → `LeaveOnCleanup`. A complete "a specialist NPC joins
you temporarily, with locked gear and restricted work, and leaves" quest, in XML.
**[V]** VFE Empire's other seven quests are ~85% C# and not copyable.

### 7.6 Making beats *places*

**Vanilla Landmarks Expanded `3656316229`** — **115 `LandmarkDef`s** each with a world
icon, a `nameMaker` RulePack and a weighted mutator table, plus ~263
`TileMutatorDef`s. **[V]** Combined with `allowedLandmarks`:

```xml
<li Class="QuestNode_GetSiteTile">
  <storeAs>siteTile</storeAs>
  <allowedLandmarks><li>VEE_ResurgentCaldera</li></allowedLandmarks>
  <selectLandmarkChance>1</selectLandmarkChance>
</li>
```

**Every Chronicle beat gets a distinct, named, visually identifiable place on the world
map, in pure XML.** Requires Odyssey. Covered by the compat layer. One confirmed bug:
`DenseSnow.Destroy` uses **`Find.CurrentMap`** instead of `this.Map`, inside a silent
`try/catch(Exception){}`. **[V]** Removal is not clean (thousands of scribed per-tile
def refs). **PULL.**

**Vanilla Base Generation Expanded `3209927822`** — 100% XML, zero assemblies, zero
textures. **[V]** `technical-findings.md` already records its 634 layouts and that its
faction patch covers only Empire, Tribals, Outlanders and Pirates. Adding: **it is the
cleanest removal in the bin** — its layouts are built from vanilla ThingDefs at map-gen
time and nothing is scribed, so removing it changes only *future* map generation.
**[V]** And one MP hazard that lives in KCSG, not here:
`SettlementGenUtils.Sampling.Sample` constructs an **unseeded `System.Random`** to pick
building placement points, on the path taken by every `SettlementLayoutDef`. **Two
clients generate structurally different bases from the same seed.** **[V]** The
`tiledStructures` / `structureLayoutDefs` paths of `GenStep_CustomStructureGen` do
*not* go through it — **so authoring your own quest sites with KCSG is MP-safe; letting
VBGE regenerate faction settlements is not.**

**Worksites Expanded `3687071198`** — not previously on any list, and it belongs here.
**11 XML `QuestScriptDef`s of "opportunity site" shape** (mining, farming, component,
gunsmithing, clothes-making, black market, homestead, mercenary, orbital platform,
vehicles ×2), **48 KCSG `StructureLayoutDef`s**, 8 `SitePartDef`s, 57 GenSteps, a
parley hediff, and a `Duties_WorksiteSack` duty set. **[V]** A worked, shipping example
of "go somewhere and take something" built from vanilla nodes plus a handful of custom
finders. Depends on VEF. **RESTAT.**

**Vanilla Outposts Expanded `2688941031`** — the inverse verb: send colonists to a tile
and they produce on a timer. Zero quest integration. **[V]** The engine
(`Outposts.dll`) ships *inside VEF*; this mod is 13 thin subclasses and 18 textures,
and its 1.6 `loadFolders.xml` drops Fishing and comments out Factory. **BLOCK for
co-op:** a `Window` calling `WorldObjectMaker.MakeWorldObject` + `Find.WorldObjects.Add`
unsynced; production timers and yields multiplied by client-local settings; and
reflection writing settings values **directly onto live `Outpost` instances at load**.
**[V]** Removing it deletes the outposts *and the colonists inside them*. (It *is*
covered by the compat layer, which patches the dialogs and gizmos — verify rather than
assume.)

### 7.7 What still is not XML

| Want | Status |
|---|---|
| Quest A success unlocks quest B | **solved** — `QuestChainExtension` |
| Research unlocks a quest | **solved** — `requiredResearch` |
| One exact named item as reward | **solved** — `QuestNode_GenerateThing` + `AddItemsReward` |
| Take a specific object off a site map to complete | **solved** — `LootableBuilding` signal |
| Hand-designed site map | **solved** — KCSG `StructureLayoutDef` + `<linkWithSite>` |
| Site on a specific landmark type | **solved** — `allowedLandmarks` (needs Odyssey) |
| Multi-objective tracker with UI | **not XML** — VFED's `QuestNode_MarkObjectives` is C# |
| Persistent reddening screen alert on a deadline | **not XML** — §10.3 |
| A world-escalation meter | **not XML** — the tiers are data, the effects are workers |

**Do not use `QuestChainDef.uniqueCharacters` under Multiplayer.**
`EnsureAllUniquePawnsCreated()` runs `PawnGenerator.GeneratePawn` in `LoadedGame()` /
`StartedNewGame()` — **outside the ticking simulation**, so joining clients can generate
different pawns. **[V]** Generate recurring NPCs inside a quest with vanilla
`QuestNode_GeneratePawn` instead.

### 7.8 The architecture, assembled

1. **`Archinity_ChronicleBeatBase`** — one `QuestScriptDef` in the VFED `Base.xml`
   style, parameterised by `$sitePartDef`, `$landmark`, `$rewardThing`,
   `$distanceRange`, `$objectiveSignal`.
2. **Each beat** = ~30 lines of `QuestNode_SubScript` + name/description rules + one
   `QuestChainExtension`.
3. **The place** = a `SitePartDef` + a `GenStepDef` with `<linkWithSite>` running
   `KCSG.GenStep_CustomStructureGen` over Archinity's own ASCII layout grids,
   landmark-pinned via `allowedLandmarks`.
4. **The thing you take** = a ThingDef with
   `<thingClass>VEF.Buildings.LootableBuilding</thingClass>` and a fixed `contents`
   list, firing `site.LootableBuildingOpened`.
5. **Completion** = `QuestNode_End` with `<inSignal>site.LootableBuildingOpened</inSignal>`.
6. **The chain** = `conditionSucceedQuests` + `ticksSinceSucceed` + `requiredResearch`.
7. **Extra guaranteed reward** = `QuestNode_GenerateThing` → `QuestNode_AddItemsReward`.
8. **Atmosphere** = `VEF.Sounds.QuestNode_ForceMusic` between `site.MapGenerated` and
   `site.MapRemoved`.

Nothing there is a parcel on the roof. Every step is *travel to a named place, find a
specific object, take it*.

**The cost:** VEF becomes a hard dependency, and close to a one-way door.

---

## 8. Design area (d) — what the world demands

### 8.1 Non-wealth threat scaling — vanilla already ships it

`RimWorld.StorytellerUtility.DefaultThreatPointsNow` is wealth-driven through four
`private static readonly SimpleCurve`s — **not defs, not patchable from XML**: **[V]**

```
PointsPerWealthCurve:            0 @ 0,  0 @ 14,000,  2400 @ 400k,  3600 @ 700k,  4200 @ 1M
PointsPerColonistByWealthCurve: 15 @ 0, 15 @ 10,000,   140 @ 400k,   200 @ 1M
PointsFactorForColonyMechsCurve, PointsFactorForColonySubhumanCurve
```

Note the second: **colonist contribution itself scales with wealth.** Final points are
`(wealth pts + pawn pts) × IncidentPointsRandomFactorRange × Lerp(1, adaptation, difficulty.adaptationEffectFactor) × difficulty.threatScale × StorytellerDef.pointsFactorFromDaysPassed.Evaluate(DaysPassedSinceSettle)`,
clamped to `[GlobalPointsMin(), 10000]`. **[V]**

`StorytellerDef` exposes only `pointsFactorFromDaysPassed` and
`pointsFactorFromAdaptDays` in XML — **there is no wealth curve field on
`StorytellerDef`, and none appears in any vanilla storyteller def.** **[V]**

**But `Difficulty` has the lever, and it is saved with the game. [V]**

```csharp
// RimWorld.Difficulty
public bool  fixedWealthMode;             // line 97
public float fixedWealthTimeFactor = 1f;  // line 99
// both Scribe_Values.Look'd at lines 362-363
```

and `RimWorld.Planet.MapParent.PlayerWealthForStoryteller`:

```csharp
if (Find.Storyteller.difficulty.fixedWealthMode)
    return StorytellerUtility.FixedWealthModeMapWealthFromTimeCurve
             .Evaluate(AgeInDays * Find.Storyteller.difficulty.fixedWealthTimeFactor);
return wealthWatcher.WealthItems + wealthWatcher.WealthBuildings * 0.5f + wealthWatcher.WealthPawns;
```

with `FixedWealthModeMapWealthFromTimeCurve` = **10,000 @ day 0 → 180,000 @ day 180 →
1,000,000 @ day 720 → 2,500,000 @ day 1,800.** **[V]**

> **This is the project's stated requirement, shipped in vanilla, selectable at game
> start under Custom difficulty, persisted in the save, with zero mods, zero assemblies
> and zero desync surface** (it is part of the `Difficulty` object, which is game
> state, not client-local settings).
>
> It maps onto the campaign almost exactly: day 720 sits just past the projected end of
> a ~600-day run and evaluates to the 4,200-point ceiling.

**Two caveats.** It is **map age**, not colony age — a newly settled map (a gravship
relocation, a second colony) restarts at 10,000. **[V]** And `Difficulty.Copy()` resets
`fixedWealthTimeFactor = 1f` while copying `fixedWealthMode` — a quirk when cloning a
difficulty. **[V]**

**What it does not give you** is the *quality* axis — "a small number of much
better-equipped enemies is a legitimate escalation." Points buy quantity by default.
That is where **World Tech Level's post-hoc gear replacement** earns its place:
`Patch_PawnGenerator.GenerateGearFor` swaps over-level apparel and weapons via weighted
alternatives tables, so raiders arrive era-appropriate **without re-authoring a single
pawn kind**. **[V]** Points curve from vanilla, gear tier from WTL, era-appropriate
faction selection from Ignorance Is Bliss — three levers, none of them wealth.

### 8.2 The escalation ladder worth copying

**VFE Deserters' `VisibilityLevelDef`** is the best "what the world demands" artefact
in the bin, and its *structure is pure data*: six named tiers — hidden → whispers →
rumors → news → public enemy → divine inferno — each carrying a 0–100 band, cost
multipliers, a response timer, a response type, and a list of `specialEffects`
(`VisibilityEffect_Incident` to switch incidents on and off, `_ArmySize` at
×1.2/×1.5/×2.0, `_RaidChance`, `_Goodwill`, `_AerodroneBombardment`, `_GameCondition`
with a 30-day doom countdown). **[V]** Paired with `ImperialResponseDef` — a plain
`{label, reinforcements: {PawnKind: IntRange}, gameCondition}`.

**It answers "the world notices you and escalates" with a readable table rather than a
storyteller curve.** The tiers are XML; only the effect workers are C#, and several
tiers are reachable with plain `PatchOperation`s on `IncidentDef.baseChance` keyed to
research, requiring no code at all.

VFE Classical's **`CurseDef`** system is the same idea from the other direction:
player-chosen, save-persisted global difficulty modifiers, with the active count
feeding back into storyteller pacing. **[V]** The closest thing in the ecosystem to
*"the world is hard because the story says so, and it is not wealth."*

### 8.3 The absent curve — five factions that raid at any points level

**None of the five hostile Industrial factions across VFE Pirates and VFE Settlers
declares `raidCommonalityFromPointsCurve`. [V]** From vanilla `FactionDef`:

```csharp
public float RaidCommonalityFromPoints(float points) {
    if (points < 0f || raidCommonalityFromPointsCurve == null) return 1f;
    return raidCommonalityFromPointsCurve.Evaluate(points);
}
```

**A missing curve means flat weight 1.0 at every points level.** `VFEP_Junkers` —
permanently hostile, Industrial, present in every world — is exactly as likely to be
the raid source at 80 points as at 20,000, and its floor unit `VFEP_Scrapper`
(combatPower 65) arrives **in plate armour with a gun at ~78–260 points**. **[V]**

VFE Settlers adds three more, all `requiredCountAtGameStart: 1`, all Industrial, all
`canSiege`/`canStageAttacks`, sharing Combat `pawnGroupMakers`: `SettlerCivil`
(neutral), `SettlerRough` (**`naturalEnemy: true`**), `SettlerSavage`
(**`permanentEnemy: true`**). Its raids ride vanilla `RaidEnemy`, which is why no raid
def appears in its `Defs/Storyteller/`. **[V]**

> **This makes Ignorance Is Bliss the *only* thing standing between a neolithic
> Archinity colony and industrial gunmen — not a backstop, the sole gate.** Which
> raises the stakes on TechBlock's desync considerably, since
> `technical-findings.md` already records that IIB's `useActualTechLevel` depends on
> TechBlock writing the player faction's tech level, and that its empty-pool behaviour
> is **fail-open and fail-quiet**.

**And it is fixable in pure XML.** Neither mod uses `VEF.Factions.FactionDefExtension`
or `VEF.Storyteller.IncidentDefExtension`, and neither patches the wealth calculation —
no Harmony patch on `StorytellerUtility`, `WealthWatcher` or `IncidentWorker_Raid*` in
either assembly. **[V]** **Five `PatchOperationAdd`s using vanilla's own mechanoid curve
as the template close the whole hole.** Corollary: **VFE Pirates ships zero
`IncidentDef`s**, so there is no `earliestDay` or `minThreatPoints` to set —
`raidCommonalityFromPointsCurve` is the *only* lever.

**MP for both is high risk.** VFE Pirates: `Dialog_WarcasketCustomization` **equips real
apparel onto the real Pawn on every slider move** in a client-local window;
`Apparel_Warcasket.DrawColor` pulls `Rand` in a getter and **writes the result into a
Scribed field**; `IncomingSmoker` gates four `Rand.Range` calls behind
`GenView.ShouldSpawnMotesAt`; and `Building_CrashedShip` has no `respawningAfterLoad`
guard and no `ExposeData` at all, so a mid-countdown save/load NREs every tick from tick
700. **[V]** VFE Settlers has four of its own, the worst an **unsynced closure gizmo**
mutating a caravan on bounty turn-in. Both are covered by the compat layer.

**Two content items worth taking. [V]** `VFEP_Turret_Cannon` — a **Smithing-gated
medieval cannon** that refuels on steel as cannonballs, with art, sound and projectile,
ready-made Medieval artillery. And `VFES_Tomahawk` — `techLevel Neolithic`, **a ranged
neolithic option that is not a bow**, which is rare and directly useful. Both can be
copied outright.

**Verdicts: VFE Pirates BLOCK as-shipped / RESTAT viable. VFE Settlers RESTAT** (a
correction — its three always-present Industrial factions make "essentially not a threat
mod" wrong). ⚠ Settlers also ships **~30 unprefixed defNames** (`Windmill`, `Post`,
`Settler`, `Bandit`, `Outlaw`, `Wanted`, `Apparel_Vest`…). None collide with vanilla,
but a collision with another mod is a **silent last-one-wins overwrite**. **[V]**

### 8.4 Fortification and siege — VFE Security `1845154007`

Content by era, counted
against actual ThingDefs rather than the blurb: **Medieval (4)** —
`VFES_Turret_Ballista` and `VFES_Turret_Catapult` (both off `VFES_SiegeEquipment`, 900
points, prereq vanilla **`Smithing`**), `VFES_CavalrySpikes`, `VFES_BearTrap`;
**Industrial (10)**; **Trench Warfare (5)**; **Spacer (5)**; **Ultra (2)**. **No
Neolithic tier** — 1.6 deleted that file. 231 textures. **[V]**

**The Medieval slice is pure vanilla classes:** the **ballista** is `Building_TurretGun`
+ `CompProperties_Mannable` + `CompProperties_Refuelable` **fuelled by `WoodLog`**, and
the **catapult** is `Building_TurretGun` + `ITab_Shells` firing **stone chunks** via a
`fixedStorageSettings` filter. **[V]**

> `CompProperties_Refuelable` with `consumeFuelOnlyWhenUsed` — the ballista's
> wood-as-ammunition — is the cleanest vanilla expression of *"this thing eats a
> resource when you use it"*, and it reads Medieval rather than industrial.

**The assembly is the problem, not the defs.** `CompWorldArtillery.StartWorldTargeting`
mutates **`Current.Game.CurrentMap`** from a UI targeter callback; `Rand.InsideUnitCircle`
miss-scatter at cross-map impact; world objects spawned from map ticks. And the perf
cost is real: a **transpiler into `PathGrid.CalculatedCostAt`** — the hottest function
in the pathfinder — plus a postfix on `Pawn_FilthTracker.Notify_EnteredNewCell` doing
`GetEdifice()` + `GetModExtension<>()` **every time any pawn steps on any cell**. **[V]**

**Save permanence is the gentlest in the bin:** no genes, no xenotypes, three transient
hediffs. **[V]**

**Verdict: PULL the Medieval siege slice** — `VFES_Turret_Ballista`,
`VFES_Turret_Catapult`, `VFES_Artillery_Catapult`, `VFES_Gun_BallistaTurret`,
`VFES_CavalrySpikes`, `VFES_BarbedWire` and the `VFES_SiegeEquipment` research —
**all vanilla classes, copyable straight into Archinity,
loading none of `VFESecurity.dll`.** Drop the one `VEF.Weapons.AutoRefuelMannedTurrets`
modExtension. **BLOCK the assembly.** `technical-findings.md` already records the
complementary finding that `VFEM2_Turret_WallMountedArbalest` and `_Arquebus` exist and
are never placed anywhere.

### 8.5 Threat content

`technical-findings.md` already records that raid faction choice has no tech weighting
and that Ignorance Is Bliss gates it via a `FactionCanBeGroupSource` postfix.

**Alpha Mechs `2973169158`** — 664 PNGs, 212 def files, covered by the compat layer.
Already in the load order specifically so the Glitterites can field `AM_*` kinds, with
`Archinity.Pacing/Patches/Lockout_AlphaMechs.xml` surgically removing the 26 gestation
recipes, 11 mechanitor buildings, 8 apparel items and 9 research projects that face the
player. **That patch is the model for the whole BLOCK verdict class: keep the content,
delete the player's access.** **[V]**

⚠ **VPE injects `PawnGroupMaker_PsycasterRaid` into `Empire` *and* `TribeBase`**
(`…\2842502659\1.6\Patches\PawnGroupMakers.xml`) — **tribal enemies field psycasters
from day one of a neolithic start.** **[V]** A real difficulty consideration, and a real
narrative one: the power is already loose in the world before the founders touch it.

---

## 9. The altar — the largest single result

The Waystone asks for one machine that runs on blood, starts as religion and ends as
industry, and for psychic ability reflavoured away from meditation and brain heat.
**Both are deliverable in pure vanilla XML.** The VE mods in this cluster are
proof-of-concept, not dependencies.

### 9.1 The altar is one ThingDef

Four vanilla comps compose freely on one def: **[V]**

| Comp | What it gives the altar |
|---|---|
| `CompProperties_Refuelable` | **it eats blood.** Vanilla's abstract `DeathrestBuildingHemogenFueled` (`…\Data\Biotech\Defs\ThingDefs_Buildings\Buildings_Deathrest.xml:125`) is exactly `CompProperties_Power` + `_Flickable` + `_Refuelable` with `fuelFilter → HemogenPack`, `fuelLabel → Hemogen`, `autoRefuelPercent`, `canEjectFuel`. Hauling, gizmos and auto-refuel, free. Pair with vanilla `RecipeDef ExtractHemogenPack` and the whole prisoner→blood→building loop needs **zero new assemblies** |
| `CompProperties_SpawnSubplant` | **the accumulating evidence.** 100% data — `subplant`, `maxRadius`, `subplantSpawnDays`, `chanceOverDistance`, `maxPlants`. Bloodstained soil, offerings, bone |
| `CompProperties_Psylinkable` | **the rite that grants power.** `requiredSubplantCountPerPsylinkLevel` (a `List<int>`), `requiredFocus`, `linkSound`, two `[MustTranslate]` letter strings. Requires a sibling `CompSpawnSubplant` — which is a feature here, not a bug |
| `CompProperties_MeditationFocus` | the altar as a psyfocus source |

**And `RitualOutcomeEffectWorker_AnimaTreeLinking` is not hardcoded to the anima
tree. [V]** Decompiled from `Assembly-CSharp.dll`:

```csharp
CompPsylinkable obj = jobRitual.selectedTarget.Thing?.TryGetComp<CompPsylinkable>();
obj?.FinishLinkingRitual(pawn, num);
```

`FinishLinkingRitual` ends in `pawn.ChangePsylinkLevel(1)` — which VPE's prefix
intercepts and converts into a **VPE psycast point**. Full chain verified.

> **So: put `CompProperties_Psylinkable` on Archinity's altar ThingDef, reuse vanilla's
> anima-tree linking ritual defs, and you get "a rite at the altar grants a level of
> power, priced in the altar's accumulated evidence" with zero lines of C#.**

One constraint: `RitualRoleAnimaLinker` hardcodes `MeditationFocusDefOf.Natural.CanPawnUse(p)`,
and `Natural` is XML-gated on tribal backstories — **which for a neolithic start is a
fit, not a problem.** **[V]**

**A third route, also pure XML:** `CompProperties_UseEffectInstallImplant` with
`<hediffDef>PsychicAmplifier</hediffDef>` + `<canUpgrade>true</canUpgrade>`
(`…\Data\Core\Defs\HediffDefs\Hediffs_Psycasts.xml:44-48`). Any ThingDef carrying that
comp is a psylink grantor. Pair it with a RecipeDef that costs blood and you have the
Neolithic *"object that demands blood"* with no code at all. **[V]**

**And the Medieval stage is already built.** Vanilla `Altar_Small/Medium/Large/Grand`
have **no research prerequisite and no techLevel** — buildable turn one of a neolithic
start from 50–300 stone. **[V]** Mood payload: Terrible 5% / −3, Boring 15% / −1,
Satisfying 60% / +5, Spectacular 20% / +8.

> **The vanilla `RitualOutcomeComp_*` family itemises the quality contract on screen —
> lectern within 5 tiles +0.15, ritual seat +0.15, moral guide present +0.25, a
> participant-count curve, a room `Impressiveness` curve, priest `SocialImpact`
> scaling. The player sees a percentage breakdown they can chase without ever being
> told *why* it works. That is priesthood, not science, and it is pure XML per
> ritual.** **[V]**

**Ritual XML-authorability, precisely. [V]** Six def types; **exactly one field forces
C#**:

| Def type | `workerClass` required? |
|---|---|
| `RitualPatternDef` | **no** — 100% data |
| `RitualBehaviorDef` | **no — optional.** 6 of VIE's 13 ship none; vanilla `SacrificeAnimal`, `DateRitual`, `TreeConnection`, `RoleChange` ship none |
| `RitualOutcomeEffectDef` | **YES — the only mandatory one** |
| `PreceptDef` (issue Ritual) | **no** — no worker field exists |
| `RitualObligationTargetFilterDef` | yes, **but** vanilla `RitualObligationTargetWorker_ThingDef` is parameterised by a `<thingDefs>` list |
| `RitualVisualEffectDef` | **no** — 100% data |

**Can Archinity point a new ritual at an existing worker? YES for vanilla, NO for VIE.
[V]** Vanilla proof: one `Sacrifice` `RitualOutcomeEffectDef` (worker
`RitualOutcomeEffectWorker_Consumable`) is reused by two different patterns with two
different behaviors; VIE's own `CeremonialSuicide` and `LeadershipChallenge` behaviours
point at vanilla `RitualBehaviorWorker_Funeral` and `_Duel`. **The class to target is
`RitualOutcomeEffectWorker_FromQuality`** (or `_Consumable`) — a generic
quality→tier→memory-thought→letter pipeline. **All 13 VIE outcome workers are BLOCK**:
every one hardcodes role-id string literals, `InternalDefOf` constants or a static
`WorldComponent_*.Instance`, and `RitualOutcomeEffectWorker_LeadershipChallenge`
**throws** on a foreign def.

**`VME_BloodCourt` is a red herring. [V]** It is gladiatorial *succession* — a duel to
the death between the leader and the best melee colonist, winner takes the Leader role.
No altar, no victim, no offering. The nearest real neighbours are
`VME_Structure_ChthonianCult` (uses `AltarOrRitualSpot` + `PreceptRequirement_Altar`),
`VME_FireWorship` and `VME_ViolentConversion`.

**And VIE's altar contribution is the reskin ladder, not a building:** 29 textures in
four skin sets (Serketist / Eldritch / Shintaoist / Corporate) wired by 16 nine-line
`ThingStyleDef`s via `StyleCategoryDef.thingDefStyles`. **[V]** That progression maps
almost exactly onto religion→industry. ("Structures" in its title means Ideology
*structure memes*, not buildings — and 53 of its ancient-ruin prop textures are
**absent from this install** and would render as placeholders.)

⚠ **VIE Memes MP: one guaranteed desync. [V]**
`RitualOutcomeEffectWorker_ViolentConversion.Apply` does
`Random random = new Random();` — **unseeded, time-seeded per process** — and branches
on `random.NextDouble() > 0.5` between converting the prisoner and executing them by
cut. Two clients land on opposite branches the first time it runs. Its save permanence
is catastrophic: memes and precepts serialise into the saved `Ideo` by defName with no
in-game UI to drop one, and 50 `VME_Fleshcrafted*` hediffs mean a pawn with a
fleshcrafted **heart** loses the hediff and is left with a missing body part.

**VRE Sanguophage `2963116383`: BLOCK, and pull nothing — you do not need to. [V]** Its
hemogen pipe network is declared in **pure XML against `PipeSystem.*` classes that live
in VEF**, not in it. Four of its six deathrest machines are **100% pure XML** — proof
that "blood-fuelled building grants a permanent boon to an occupant" needs no C#. Its
`VRE_Draincasket` is an `IThingHolder` **with a pawn inside**, so removing the mod
**deletes a contained colonist from the save** rather than ejecting them. **[I], high
confidence.** Its one genuinely transferable idea is a *design* one: the escalation
ladder **consent → exploitation → atrocity** (feeding on a willing sanguophage, then a
draincasket on a prisoner, then the occupant starves in the box). That ladder, not the
pipes, is what *"it runs on blood"* should feel like.

### 9.2 The psychic track — and the framing

**Three corrections to earlier working figures. [V]** VPE 1.6 ships **150
AbilityDefs, not 399** (the higher number counts the independent 1.4/1.5/1.6 copies),
and **15 live paths, not 17** — `VPE_Animat` and `VPE_Puppeteer` are inside an XML
comment in `Paths.xml`.

**`PsycasterPathDef`'s complete gating surface is pure XML fields:** **[V]**

```
requiredGene       (GeneDef)
requiredMeme       (MemeDef)
requiredFocus      (MeditationFocusDef)
requiredMechanitor (bool)
requiredBackstoriesAny
lockedReason       ([MustTranslate])
ensureLockRequirement (bool)
```

`CanPawnUnlock` is the AND of exactly those. And `ensureLockRequirement: true` makes
access **dynamically re-evaluated** — `PsycastUtility.RecheckPaths` moves a path
between `unlockedPaths` and `previousUnlockedPaths` as the condition flips. **[V]**

> ```xml
> <requiredGene>Archinity_ArchonGene_Whatever</requiredGene>
> <ensureLockRequirement>True</ensureLockRequirement>
> <lockedReason>...</lockedReason>
> ```
> **A path declared like this activates the instant the named Archon gene is installed
> and deactivates if it is removed. That wires the Waystone's two power tracks —
> "named, chosen and deterministic" genes and psychic ability — together in pure XML.**
> Hemosage already ships exactly this shape with `<requiredGene>Hemogenic</requiredGene>`.

**Adding a whole path is 17 lines.** VPE Hemosage's entire `Paths.xml` is 17 lines;
`ResolveReferences` discovers a path's abilities by scanning `DefDatabase<AbilityDef>`
for `AbilityExtension_Psycast.path == this`, and derives `MaxLevel` and `TotalPoints`.
**[V]** Retiering is equally XML: all 150 abilities carry an `AbilityExtension_Psycast`
with `level`, `order`, `path`, `psyfocusCost`, `entropyGain`, `prerequisites`, and
patches run before `ResolveReferences`, so the tree rebuilds around your numbers.
**[V]** A new tab is one free-form string field (caveat: used raw as the TabRecord
label, not through `Translate()`).

**Progression.** VPE does not replace the Empire honour route — it hijacks the vanilla
psylink hediff. A postfix on `Hediff_Psylink.PostAdd` attaches
`VPE_PsycastAbilityImplant` to any pawn that gains a psylink **from any source**;
`ChangeLevel` is prefix-returned-false and rerouted; `TryGiveAbilityOfLevel` is
prefixed to `return false`, killing vanilla's random-power grant. **[V]**

**XP is a linear function of psyfocus gained**, and the only rate knob is
`PsycastSettings.XPPerPercent` — **a C# mod setting, not XML, and unsynced.** **[V]**

> **There is no XML knob for the earn rate. The XML-side lever Archinity actually has
> is `MeditationFocusStrength` / `MeditationFocusGain` on the focus objects and the
> pawn — patch those and you move XP rate, because XP is downstream of psyfocus gain.
> That is the correct place to intervene.**

**Framing: 100% reskinnable, and this is a clean decisive answer. [V]** Every
player-visible string was classified across the 19,583-line decompile. VPE makes 142
`Translate()` calls against 106 distinct `VPE.*` keys in four Keyed files. Every
literal containing psyfocus / neural-heat / meditat / entropy / psycast / psylink is one
of: a Harmony patch target name, a **translation key**, a Scribe save key, a defName, or
a dev log line. **Zero player-visible hardcoded English.** Vanilla's side is entirely
Keyed too — `Psyfocus`, `PsyfocusDesc`, `PsyfocusPerDayOfMeditation`, `DesiredPsyfocus`,
`TotalMeditationToday`, `AbilityNoEntropyToDump` in
`Data\Royalty\Languages\English\Keyed\Misc_Gameplay.xml` — and the def-side labels
("meditation psyfocus gain", "psyfocus cost", the `Meditate` JobDef's
`<reportString>meditating.</reportString>`, all six `MeditationFocusDef` labels) are
plain XML. Four icon textures (`IconNeuralHeatLimit`, `IconNeuralHeatRegenRate`,
`IconPsyfocusCost`, `IconPsyfocusGain`) are replaceable by shadowing the path.

**The only caveat: defNames are permanent** — the `MeditationFocusDef` type name, the
`Meditate` JobDef defName, the `MeditationFocusGain` / `PsychicEntropyMax` StatDef
defNames. None is player-visible. **The mechanics can be borrowed; the framing genuinely
can be replaced.**

**Blood-as-cost is ~40 lines.** Hemosage's whole economy is three modExtensions:
`AbilityExtension_HemogenRequirement` (blocks the cast below a threshold),
`AbilityExtension_HemogenCost` (`resource.Value -= hemogenCost` on cast — **twelve
lines of C#**), and a target validator. **[V]** Reimplementing them inside
`Archinity.Altar` gives a psycast path whose costs are paid in blood rather than
psyfocus. Also notable: `Ability_Hemodrain` does
`HealthUtility.AdjustSeverity(target, HediffDefOf.BloodLoss, 0.55f)` and converts to
hemogen — literal blood extraction at range; and a patch **zeroes neural heat entirely**
while the bloodstorm weather is active, i.e. *blood substitutes for the heat mechanic
wholesale*. Hemosage is gated only on the vanilla `Hemogenic` **gene** — no xenotype
lock, no faction lock. **[V]**

**VPE's MP profile: four independent desync classes, and the worst one is the mod's
primary interaction loop. [V]** (a) The entire progression UI mutates Scribed pawn state
from raw `Widgets.ButtonInvisible` clicks with no sync wrapper — `SpentPoints`,
`GiveAbility`, `ImproveStats`, path unlock, focus unlock. (b) The viewport-gated `Rand`
chain in `MapComponent_PsycastsManager.MapComponentTick` → `FixedTemperatureZone.DoEffects`
→ four gated draws. (c) `Settings.XPPerPercent` and `Settings.maxLevel` consumed in
simulation. (d) `PsycastsMod.ApplySettings()` writes
`HediffDefOf.PsychicAmplifier.maxSeverity = Settings.maxLevel` — **a per-client setting
mutating a shared Def at runtime, after load, where a def-checksum handshake will not
catch it.** The Multiplayer Compatibility patch addresses (a) and (b) explicitly.

**VPE Puppeteer `3033779606`: BLOCK, with one exception.** Thematically it is a *second*
philosophy of power, which fights *"one machine, one philosophy."* Mechanically it is
imperial-backstory-locked, wrong for a neolithic arc. Its `Hediff_Puppeteer` /
`Hediff_Puppet` encode a cross-pawn master/servant relationship, so removal leaves
pawns that were puppets with no needs suppression, no work restrictions and no owner.
**[V]** **But PULL its `PuppetSettings : Def` technique** — config-as-Def is exactly how
Archinity should express every tunable, and it costs nothing.

### 9.3 What the altar demands

The richest part of design area (d), and the answer is a stack of vanilla XML: **[V]**

1. **Ritual obligations** — `RitualObligationTriggerProperties` on a `RitualPatternDef`
   turn the altar from *permitted* into *demanding*. Vanilla ships
   `RitualObligationTrigger_DateProperties` and `_MemberDiedProperties`, XML-usable with
   no code. **The cheapest way to make the altar hunger.**
2. **Ritual quality comps** — the itemised, on-screen, chaseable contract. *"You learn
   by repetition what pleases it"*, in pure XML per ritual.
3. **`requiredSubplantCountPerPsylinkLevel`** — the altar's accumulated evidence becomes
   the escalating price of the next level of power.
4. **`CompProperties_Refuelable` with `consumeFuelOnlyWhenUsed`** — this thing eats a
   resource *when you use it*.

Author Archinity's own `PreceptDef` with `<issue>Ritual</issue>` +
`<preceptClass>Precept_Ritual</preceptClass>` + `<ritualPatternBase>` +
`<requiredMemes>` — **not** vanilla's `MemeDef.replacementPatterns` slot-swap, which
makes the ritual a roll. **[V]**

---

## 10. The five "unclaimed" asks — resolved

| Ask | Verdict | By what |
|---|---|---|
| (i) Penned animals eat less | **CONFIRMED UNCLAIMED** | nothing, anywhere, on any version |
| (ii) Ingredient-tier food buffs | **REFUTED** | Vanilla Cooking Expanded, installed |
| (iii) Faction demands with deadlines | **PARTIALLY REFUTED** | More Faction Interaction (not installed) |
| (iv) Colony coat of arms | **REFUTED** | **VFE Medieval 2, installed** |
| (v) Bench upgrade-in-place | **REFUTED** | Replace Stuff (MIT) + vanilla `replaceTags` |

### 10.1 Penned animals eat less — genuinely unclaimed

**Animal Feed Trough (Continued) `2071757940` has no mechanic at all.** One def file,
79 lines, three ThingDefs. The entire mod is `thingClass Building_Storage` with a
`fixedStorageSettings` filter of Hay + Kibble at `priority Important` and a trough
texture. **[V]** Its five patch files just append more defNames to that filter. It makes
hay legal to store inside a pen so `FoodUtility.FoodOptimality` picks it over walking to
grass — it changes *which* food is eaten and, by pulling animals off free map grass,
makes you consume **more** stored feed.

**VFE Farming `1957158779` has nothing animal-related** — its complete 1.6 content is
Scarecrow, Sprinkler, PlanterBox, Hydroponics, Ecosystem. The advertised animal feeder
does not exist in 1.6. **[V]**

**Vanilla is unambiguous about what "eat less" requires.**
`Verse.Need_Food.FoodFallPerTickAssumingCategory` is
`BaseHungerRate × HungerMultiplier × GetHungerRateFactor(hediffs) × traits ×
bed.GetStatValue(BedHungerRateFactor)`. **[V]** Animals have no traits, so for a penned
animal there are exactly **three** levers: the race def, a hediff, or a bed.
`Verse.PenFoodCalculator` is **UI only** — real consumption never routes through it.
**[V]** No installed mod patches `baseHungerRate` or `BedHungerRateFactor` for animals.

**And there is a pure-XML path nobody has taken.** The vanilla precedent is Ideology's
Sleep Accelerator (`…\Data\Ideology\Defs\ThingDefs_Buildings\Buildings_Ideo.xml:397`),
which uses `CompProperties_Facility` `statOffsets` to apply `BedHungerRateFactor +0.20`.
**[V]** Vanilla `AnimalSleepingSpot` / `AnimalSleepingBox` / `AnimalBed` are all
`Building_Bed`. **[V]** So: `PatchOperationAdd` a
`CompProperties_AffectedByFacilities` onto the animal beds, give the trough a
`CompProperties_Facility` with `<BedHungerRateFactor>-0.25</BedHungerRateFactor>`, and
**penned animals with a trough beside their bedding genuinely consume 25% less** — a
real change to `Need_Food`, ~15 lines of XML, no assembly. Limitation: it applies only
while the animal is in the bed. A full-strength version is ~60 lines of C#.

Trough art and a def shape to extend. **RESTAT.**

### 10.2 Ingredient-tier food buffs — refuted, by an installed mod

The hook is vanilla: `IngestibleProperties.specialThoughtAsIngredient` fires a distinct
`ThoughtDef` on the eater based on what was cooked in, independent of meal tier and cook
skill. **Vanilla uses it zero times in XML** — a fully wired, entirely unused extension
point. **[V]**

**Vanilla Cooking Expanded `2134308519` uses it, and the def file's own section header
is literally `<!-- ======= Ingredient based thoughts ========= -->`.** **[V]** Each
condiment carries `specialThoughtAsIngredient` with `mergeCompatibilityTags
<li>Condiments</li>` to survive `CompIngredients`' 3-item truncation; the thought uses
`VEF.Cooking.Thought_Hediff`, which attaches a 12-hour hediff:

| Condiment | Mood | Mechanical effect |
|---|---:|---|
| Insect jelly preserves | +6 | — |
| Chocolate syrup | +4 | — |
| Salt | +3 | — |
| Sugar | +2 | `VCE_SugarRush` |
| Mayo | +1 | `hungerRateFactorOffset −0.15` |
| Agave nectar | +1 | `ImmunityGainSpeed +0.15` |
| Spices | +1 | `Manipulation +0.05` |

Same meal tier, +6 versus +2, purely on ingredient. `VCE_AteGourmetMeal` (+14) uses
`<replaceThoughts>` to supersede `AteLavishMeal`/`AteFineMeal`. **[V]**

**But it is binary presence/absence per ingredient def — no tier, no scaling.** The
prior art for actual tiering is `VEF.Cooking.CompIngestedThoughtFromQuality`, used on
VCE cheese: it maps a quality index onto a 7-stage ThoughtDef (−7 → +15) with blending.
It reads the *meal's own* `CompQuality`, not ingredients. **Swap that one expression and
you have the ask.** **[V]**

**Two hard ceilings**, both vanilla: `CompIngredients` stores at most **3 distinct
ThingDefs** with no quantity and no quality, and ingredient quality is destroyed at
craft time (`Verse.GenRecipe.cs:28` registers `ingredients[l].def` and discards the
Thing). **[V]** Tier must be a lookup on ThingDef identity.

Building it costs **zero Harmony patches**: a `DefModExtension` tier table applied by
`PatchOperationAdd`, one `ThingComp` overriding `PostIngested` (which fires *after*
vanilla gains its thoughts, so you modify rather than fight), and one
`IngestionOutcomeDoer` for the hediff half. **Do not postfix
`FoodUtility.ThoughtsFromIngesting`** — it returns a magnitude-less struct and is called
from `FoodOptimality`, so mutating it changes food-selection AI as a side effect. **[V]**

⚠ **VCE Stews `2134312965` is actively hostile to this.** Its three `ProcessDef`s never
set `useIngredients`, and `PipeSystem.Process.HandleIngredientsAndQuality` gates
ingredient copying on that flag — **cooked stews emerge with an empty `CompIngredients`
list.** That is how it advertises "removes debuffs from insect and human meat": it
launders provenance by deleting it. If you pull Stews you must `PatchOperationAdd`
`<useIngredients>true</useIngredients>` or stews are a permanent hole. **[V]**

### 10.3 Faction demands with deadlines — partially refuted

| Clause | Delivered in the local set? |
|---|---|
| explicit deadline | ✅ `IncidentWorker_RansomDemand` (`StartTimeout(60000)`), Royalty `Decree_*` (`decreeDays`) |
| stated, specific, real consequence | ✅ `Script_BuildMonument_Root_TimeProtect.xml:23`, `VFED_DivineInferno` |
| **both, in one def, from a faction, about goods** | ❌ **nothing** |

**The missing half is the telegraphed consequence on the goods-demand path.** Vanilla's
one faction goods-demand with a countdown, `IncidentWorker_RansomDemand`, does
**nothing** on refusal. Vanilla's one goods-delivery quest, `Script_TradeRequest.xml`,
does not print its deadline and ends on a bare `<outcome>Fail</outcome>`. **[V]**

**Refuted by a mod that is not installed: More Faction Interaction (Continued)
`2379076640`** (MIT, 212k subs, updated 2026-07-13). `IncidentWorker_Extortion.cs`:
`private const int TimeoutTicks = GenDate.TicksPerDay;` — exactly one in-game day —
with letter text *"failure to pay will be met with aggression, but [PAWN_pronoun] is
gracefully willing to give you a day to pay"*, and a reject branch that forces
`IncidentDefOf.RaidEnemy` with `ImmediateAttack` / `EdgeWalkIn` and
`parms.faction = <the demanding faction>`. The letter is re-pushed and **force-opened**
on timeout. **[V]** Its gaps: silver only, permanent-enemy factions only, one 1-day
window, no escalation.

**Across ~75,000 lines of decompiled faction-simulation code in the local set, every mod
models the world as something that *happens*.** Two point a tribute pipeline **at** the
player. **Not one points an obligation away from the player.** Faction Territories has
every primitive — a timed `ChoiceLetter` with a stated deadline and a destructive expiry
(*"You have 24 hours to decide"*, `ExpireTicks = 60000`, pawn destroyed on expiry), a
goodwill delta on a choice, a tech-weighted world resolution, a per-faction resource
ledger — assembled into four systems, none of which is that one. **[V]**

**Templates to copy, all pure XML: [V]**
- `Scripts_Decree_Utility.xml:9` — *"If you fail to fulfill this decree within
  [decreeDays] days…"* — the sentence shape.
- `Script_BuildMonument_Root_Basic.xml:24` — *"your relations with [asker_factionName]
  will fall by [goodwillChangeIfMonumentDestroyed]"* — the best numeric telegraph in
  vanilla.
- `…\3025493377\1.6\Defs\QuestScriptDefs\EmpireBargain.xml:19` —
  `<expireDaysRange>3</expireDaysRange>` plus `[raid/raidPawnKinds]` printing the actual
  enemy roster into the description **before the player commits**.

**And the strongest telegraphed consequence on the machine is VFED's
`VFED_DivineInferno`:** *"You have 30 days before The Empire moves all required orbital
slicer beam satellites into position… your colony will be glassed."*
`GameCondition_DivineInferno` renders the **exact calendar glassing date** plus a live
countdown in a permanent tooltip, checks the escape hatch every tick, and on expiry
fires 30 orbital strikes at 5s intervals. **[V]** It demands *behaviour*, not goods.

**One load-bearing gap.** `RimWorld.QuestPart_Delay` carries `alertLabel`,
`alertExplanation`, `alertCulprits` and `ticksLeftAlertCritical` — but the XML-facing
`QuestNode_Delay` **does not expose any of them**, and zero vanilla quest defs use them.
So a pure-XML demand quest gets the quest-tab countdown but **cannot raise the
persistent reddening screen alert** — the thing that makes a deadline *felt*. That needs
a ~30-line `QuestNode` subclass. **This is the sole justification for touching an
assembly on this feature.** **[V]**

Two type names in the project's notes do not exist in 1.6: `QuestNode_GetDeadline` and
`QuestPart_RequirementsToAcceptThing`. The real primitives are `QuestPart_Delay` /
`QuestNode_Delay` (`isQuestTimeout`), quest-level `expireDaysRange`, and
`QuestNode_ChangeFactionGoodwill`. **[V]**

⚠ **Residual risk:** `[WG] RimPacts – Diplomacy Overhaul` `3762723122` (1.6-only, closed
source, updated daily) names *tribute treaties*, *ultimatums*, *"trust falls on unpaid
tribute"* and *"expiry warning"* in its blurb. **Decompile it before building (iii).**
**[I]**

### 10.4 Colony coat of arms — refuted, and the premise was wrong

**VFE Medieval 2 `3444347874` ships a complete, working heraldry system.** It is
installed. It was on nobody's list for this. **[V]**

- **Two new Def types** — `VFEMedieval.HeraldicPattern` (11: barry, barry dancetty,
  bordure, cross, per bend/chevron/cross/fess/pale/saltier, plain) and
  `VFEMedieval.HeraldicSymbol` (61).
- **Art:** 121 symbol PNGs plus **566 mask PNGs** across 13 pattern folders,
  per-garment and per-bodytype (`Tabard_Fat_Barry_eastm.png`, `Tabard_Female_…`,
  `StandingBanner`, `Standard`, three rug sizes).
- **A real rendering mechanism** in VEF: `VEF.Graphics.DynamicGraphicBuilding` overrides
  `DrawAt` and composites runtime-built `Graphic`s layered by `Altitudes.AltIncVect * i`
  from tagged texPath / maskPath / colorA / colorB, cached per Thing. **World-space
  rendering, not UI textures.**

| Thing | defName | Class |
|---|---|---|
| Standing banner | `VFEM2_StandingBanner` | `VEF.Graphics.DynamicGraphicBuilding` |
| **Tabard (apparel)** | `VFEM2_Apparel_Tabard` | `VEF.Graphics.PawnRenderNode_Omni` |
| Heraldic standard (carried) | `VFEM2_MeleeWeapon_Standard` | `VEF.Graphics.DynamicGraphicThing` |
| Heraldic rugs ×3 | `VFEM2_HeraldicRug{Narrow,Broad,Grand}` | `DynamicGraphicBuilding` |

**Faction-wide is a supported mode.** `CompEditHeraldic` yields a "style heraldics"
gizmo when `Thing.Faction == Faction.OfPlayerSilentFail`, opening `Dialog_Heraldic` with
`VFEM2_EditThingHeraldry` and **`VFEM2_EditFactionHeraldry`**; in faction mode the target
resolves to `thing.Faction`, so the choice becomes **the colony's arms** and every
un-overridden item inherits it. **[V]** NPC factions get presets; factions without one
get a **deterministic** roll seeded on faction + ideo load IDs.

**Two gaps.** **Shields are not covered** — `VFEM2_Shield_Heater` and
`VFEM2_Shield_Round` are plain `Graphic_Single`/`Graphic_Multi` with no heraldry tags.
**[V]** (Web search found **zero shield-heraldry candidates anywhere, on any version.**)
And **the player edit is not synced** — `Dialog_Heraldic` writes tags on the clicking
client only. Choices are stored in a scribed `GameComponent`, so they are
save-permanent; it is the edit, not the storage, that diverges. **[V]**

Upstream bug if you build on it: `HeraldicSettings.Items` lists `"HeraldryColorB"`
twice, and the faction constructor does
`maskPath = new TaggedText("HeraldryColorA", pattern.path)` where it clearly meant
`"HeraldryPattern"`. **[V]**

**The mods everyone assumed would do this, do not. [V]** `2552609458` VIE Icons and
Symbols is **220 `IdeoIconDef`s and nothing else** — 220 PNGs all at 128×128, no
assembly, no mechanism. (Sticky on removal: `Ideo.iconDef` is scribed, so removing it
leaves a pink placeholder forever.) VFE Empire has **one** banner PNG. VFE Classical has
**zero** banner or standard textures. Vanilla Furniture Expanded has no banner at all.
VFE Props and Decor's `VFEPD_Banner` inherits a base whose entire body is
`<building><paintable>true</paintable></building>` — the vanilla paint bucket.

**And vanilla 1.6 has no banner, flag or standard building at all.** The Ideology
Ideogram is a fake-out: it hardcodes one texture path and varies only through 12
hand-drawn `ThingStyleDef`s. It never draws `Ideo.Icon`. **[V]**

**If you build it natively (~80–150 lines):** `Ideo.Icon` is a `Texture2D` and
`Verse.GraphicDatabase` has a **public `Texture2D` overload** —
`Graphic_Single.Init` does
`new MaterialRequest(req.texture ?? ContentFinder<Texture2D>.Get(req.path), …)`. Vanilla
already does exactly this for the mechanitor control-group marker. **"UI textures can't
be world materials" is a myth** — `ContentFinder` applies identical import settings to
`Textures/UI/…` and `Textures/Things/…`. **[V]** For apparel,
`PawnRenderNodeProperties.nodeClass` and `.workerClass` are both XML-settable `Type`
fields and `PawnRenderNode.GraphicsFor` is `protected virtual`, so **a tabard needs zero
Harmony patches** — the route VFE M2 took. Crest art is free (94 vanilla + 220 VE
`IdeoIconDef`s). Two gotchas: runtime-built Graphics miss `BakeStaticAtlases` (render
fine, unbatched — use `RealtimeOnly`), and `Ideo.SetIcon` nulls only its own field, so
key your cache on `iconDef` and call `SetAllGraphicsDirty()` on ideo change.

Web search adds two more: **Coat of Arms – Faction Icon Editor `3677207603`**
(editor-grade, extensible via `EmblemDef`/`FrameDef`/`BackgroundPatternDef`, but renders
**only** as the world-map faction icon), and **Amnabi's Flags (Continued) `2592638428`**
(MIT, 47k subs — in-game designer, 27 patterns, custom PNG import, one design updating
every display object, four flag buildings and a banner **belt**; no tabard, **no
shields**). **[V]**

### 10.5 Bench upgrade-in-place — refuted

**Facility-link preservation is a non-problem.** `CompAffectedByFacilities` calls
`LinkToNearbyFacilities()` in `PostSpawnSetup` and `UnlinkAll()` in `PostDeSpawn`. Links
are geometric derived state, rebuilt on every spawn. **[V]** The one real constraint:
links rebuild from the **new** def's `linkableFacilities`, so if tier B omits one tier A
had, the bonus is **silently lost with no log line**.

**Bills are preserved by Replace Stuff `3526354009` (MIT), generically.**
```csharp
private static void TransferBills(Thing n, Thing o)
{
    if (n is not Building_WorkTable newTable || o is not Building_WorkTable oldTable) return;
    foreach (Bill bill in oldTable.BillStack) newTable.BillStack.AddBill(bill);
}
```
Bills move **by reference**, so repeat counts, ingredient filters, suspended state, pawn
restrictions and skill ranges all survive. Wired via a Harmony prefix/postfix pair on
`GenSpawn.Spawn`. It contains **zero** facility-handling code, correctly. **[V]**

**Vanilla 1.6 shipped `replaceTags` but not the tags.** `ThingDef.replaceTags` is a
public `List<string>` and `GenConstruct.HasMatchingReplacementTag` is a set intersection.
**[V]** But only **12 defs in 4 files** across all of `Data/` use it —
`Buildings_Production.xml` has **zero**. And vanilla `Frame.CompleteConstruction`
transfers quality, style, storage group, storage settings and scaled hitpoints — **but
nothing about bills**. So a bare-vanilla `replaceTags` upgrade works and **silently
wipes the bill list**. Replace Stuff's `GenSpawn.Spawn` patch is precisely the fix.
**[V]**

**The remaining gap is eligibility, and it is closable in XML.** Replace Stuff's upgrade
pairs come from a **Def**, not hard-coded: `Replace_Stuff.InterchangeableItems` with
`<replaceLists><li><category>…</category><items>…</items></li></replaceLists>`, read at
startup. Its shipped `Vanilla.xml` defines Smithys, Stoves, TailoringBenches,
MachiningTables, ArtTables, ResearchBenches — **but not `CraftingSpot` or
`ButcherSpot`**, even though both are `Building_WorkTable` and would fire
`TransferBills`. Adding one `InterchangeableItems` def is **pure XML**. **[V]**

So the whole ask is ~4 lines of XML per bench pair:
```xml
<ThingDef ParentName="BenchBase">
  <defName>Archinity_SmithyCrude</defName>
  <replaceTags><li>Archinity_Smithy</li></replaceTags>
</ThingDef>
```

**Two silent-failure traps** (the CODING_STANDARDS "no error message" class): tier B
omitting one of tier A's `linkableFacilities` drops that bonus with no log line; and
tier B lacking a recipe an active bill referenced leaves the bill copied but unworkable.

**Correcting the record on VEF: there is no generic upgrade comp in it.**
`grep -ci "upgrad"` over the complete 92,806-line `VEF.dll` decompile returns **0**.
`CompUpgrade`, `CompProperties_Upgrad`, `Building_Upgradeable` — all absent, and absent
from `KCSG.dll`, `MVCF.dll`, `Outposts.dll`, `PipeSystem.dll` too. **[V]** What VEF
*does* have, and it matters for tier compatibility, is
`VEF.Buildings.AffectedByFacilitiesExtension` (`copyLinksFrom`) and
`RecipeInheritanceExtension` (`inheritRecipesFrom`, `allowedRecipes`,
`disallowedRecipes`) — both already in `technical-findings.md`, both ~30 lines to
reimplement, which avoids deepening the dependency.

**The closest architectural template is VVE-Upgrades `3302208420`** — pure XML on
**Vehicle Framework**, with `Vehicles.UpgradeTreeDef` whose `nodes` carry
`StatUpgrade`/`VehicleUpgrade`, `work`, `gridCoordinate`, `ingredients` and
`graphicOverlays`. **Additive, not a def swap** — the Thing keeps identity and nodes
layer stat offsets. **[V]** Vehicle-only, no bills or facilities concept, no licence.
Worth stealing as a *design template*.

MP:
low-moderate — no `Rand`, no threading; the replace flow rides vanilla construction paths
that MP syncs generically. **[I] — smoke-test one workbench replace in a real MP session
before building progression on it.**

**Verdict: PULL Replace Stuff.** The expensive alternative — a framework-clean
`CompUpgradeInPlace` — is 400–700 lines, and you would be reimplementing Replace Stuff's
80 patch points of placement/blueprint/frame/designator interception to avoid an XML tag.

---

## 11. Bookmark index — the rest

Not depth-assessed. Recorded so the next pass does not re-hunt. Counts are
`Defs/*.xml` files / `Patches/*.xml` files / PNGs. **[V]** for counts; verdicts **[I]**.

### Infrastructure
`2009463077` Harmony (MIT) · `2934420800` Prepatcher · `2606448745` Multiplayer 0.11.5 ·
`818773962` HugsLib (covered) · `735106432` EdB Prepare Carefully (MIT, pre-game only,
**not** covered).

**Missing and worth acquiring:** *Multiplayer Compatibility* `1629973374` (MIT). See §3.

### Art and content libraries — bookmark for reskinning
| ID | Mod | defs / patches / png | Note |
|---|---|---|---|
| `2102143149` | VFE Props and Decor | 377 / 3 / **1073** | largest prop library; the only modded source KCSG auto-generates symbols for |
| `2636329500` | VIE Memes and Structures | 838 / 308 / 704 | §9.1; unseeded `new Random()` desync |
| `2842502659` | Vanilla Psycasts Expanded | 340 / 29 / 468 | §9.2 |
| `1718190143` | Vanilla Furniture Expanded | 146 / 24 / 400 | no banner exists in it |
| `1845154007` | VFE Security (**MIT**) | 97 / 26 / 231 | §8.4 |
| `2062943477` | VFE Power | 93 / 5 / 153 | covered by compat layer |
| `1814383360` | Vanilla Weapons Expanded | 83 / 16 / 346 | **no assembly** |
| `1814988282` | Vanilla Armour Expanded | 82 / 19 / 414 | |
| `1914064942` | Vanilla Fishing Expanded | 50 / 35 / 113 | answers "food" permanently |
| `2028381079` | VFE Spacer | 50 / 20 / 138 | |
| `1814987817` | Vanilla Apparel Expanded | 45 / 6 / 428 | |
| `2962126499` | VAE Waste Animals | 117 / 12 / 66 | covered |
| `2454918354` | VWE Non-Lethal | 55 / 2 / 24 | capture-alive verb, on-theme for the altar |
| `2792917473` | Vanilla Chemfuel Expanded | 24 / 13 / 33 | |
| `1957158779` | VFE Farming | 24 / 1 / 27 | §10.1 — nothing animal-related |
| `2521176396` | VAE Accessories | 16 / 18 / 54 | |
| `1880253632` | VFE Production | 15 / 9 / 58 | no assembly |
| `2454918139` | VWE Frontier | 18 / 30 / 16 | |
| `1718191613` | VFE Medical | 27 / 3 / 25 | |
| `2836791007` | RimFantasy – MO Edition | 406 / – / 163 | 30 arcane weapons, 114 trait defs; hard MO dependency drags in the ingot chain; **no settings surface at all — one of the safest assemblies in the bin** |

### Storage
`3033901359` Adaptive Storage Framework (**MIT**, the only natively MP-aware mod, and
covered) · `3400037215` Adaptive Primitive Storage (neolithic storage art) ·
`3416243474` [sbz] Neat Storage (198 png) · `3486264784` [sbz] Fridge · `3537905298`
[sbz] Gravship Storage · `3425601715` MO: Adaptive Storage.

### Quality of life — no design bearing
`1195427067` Architect Icons (MIT) · `3563882422` Better Architect Menu (990 patch
files) · `3697920753` Architect Menu Optimizer · `1279012058` Pick Up And Haul (MIT,
covered) · `2679126859` Compositable Loadouts (LGPL, covered) · `3527418098` Pharmacist:
Represcribed (covered) · `1508341791` Filth Vanishes With Rain And Time · `2734454892`
Faster Moisture Pump · `2903717987` Advanced Pollution Pump · `3760520682` No
Alzheimer's · `3749200746` TakeCover · `2860414285` Vanilla Combat Reloaded ·
`3773448562` Milky Way (a GUI toolkit, miscategorised — §6.2).

### Assessed and blocked
VRE **Saurid** `2880990495` (`replacesFaction` deletes a vanilla faction) · VRE
**Hussar** `2893586390` (client-local settings determine the GeneDef count at load) ·
VRE **Android** `2975771801` (patches the abstract outlander and pirate bases; but
**study its `AndroidSettings.xml`**) · VRE **Waster** `2983471725` (rewrites the vanilla
Waster xenotype; `Rand` in a render path) · **Faction – Elves** `3726293423` (four
medieval factions at world gen; unprefixed defNames) · **Dwarves of the Rim**
`2939964151` (Industrial `naturalEnemy` at world gen; 17 textures, no pawn art). All
**[V]**.

---

## 12. The named leads — resolved

### 12.1 `Story Framework` — closed, negative

**Story Framework – Missions & Objectives for your mod!**, Workshop `1413932960`, author
Telefonmast, **MIT**, repo `RealTelefonmast/Missions-Objectives`. **[V]** Still publicly
listed (`banned: 0`, `visibility: 0` — a claim that it was removed for guideline
violations is **false**). 4,945 current / 36,868 lifetime subscribers.

**`supportedVersions` is `<li>1.0</li>`. Last Workshop update 2019-02-26; last git push
2019-10-23. One fork, last pushed 2018.** **[V]** It ships `StoryFramework.dll` (135 KB)
**and a vendored 2019-era `0Harmony.dll`** — a hard blocker for 1.6.

The archive's claim was right in spirit — *users* author in XML — but the framework
itself is a C# mod. It does not remove an assembly from the load order; it adds someone
else's. Its XML surface was genuinely expressive: `MissionDef` and `ObjectiveDef` with
types `{Custom, Wait, Destroy, Kill, Recruit, ConstructOrCraft, Own, MapCheck, Research,
Travel}`, a `Requisites` vocabulary covering objectives / missions / **researchProjects**
/ things / incidents / jobs with `any*` variants and **`failedObjectives` /
`failedMissions` for multi-pathing**, and `IncidentProperties` covering
`{CustomWorker, Reward, Research, Appear, Skyfaller, Raid}` with `researchUnlocks`.
**[V]** No successor — `TeleCore` (`3188258848`, 1.5-only) carries no mission system.

**The live alternative, if branching *dialogue* is ever wanted:** **Custom Quest
Framework `2978572782`** (HaiLuan, 1.4–1.6, updated daily, 156k current / 273k lifetime,
repo `ying636/Custom-Quest-Framework`). Consumer mods built on it are provably 100% XML —
`Custom Quests: Outcasts` `3115358432` has **no `Assemblies/` folder at all** — and it
adds a `DialogTreeDef`: a branching dialogue graph in XML with indexed nodes, per-option
conditions (`DialogCondition_Skill`, `DialogCondition_Hediff`), `hideWhenDisabled` and
`results → nextIndex`. **[V]** It even ships Claude agent skills in-repo (in Chinese).
**Catches:** the author's own compatibility statement is literally
*"I don't know"*, English is machine-translated, it self-describes as `(WIP)`, and its
runtime surface is exactly the shape that desyncs.

> **The ticket's own alternative is the right one.** Vanilla `QuestScriptDef` plus VEF's
> `QuestChainExtension` (§7) delivers the Chronicle with no second assembly. Mark `Evaluate Story Framework` resolved-negative.

### 12.2 `Worldbuilder` — identified, and larger than assumed

**Worldbuilder `3522102833`**, author **ferny** (the same author as Node Research),
1.6-only, updated daily, **152,964 current / 245,285 lifetime** subscribers, repo
`fernyrepos/Worldbuilder`, **no licence**, hard dependencies on Harmony **and VEF**, and
*"Do not add this mid-game!"* in its own description. **[V]**

It is a planet authoring suite — tile brush, map editor from any world tile, map markers,
world-feature text, and shareable **world presets** others publish as separate mods.

**It bears heavily on faction authoring.** `WorldPreset.cs` persists `saveFactions`,
`saveIdeologies`, `saveBases`, `saveFactionCustomizations`, **`saveWorldTechLevel`**,
plus dictionaries for `factionNameOverrides`, `factionDescriptionOverrides`,
**`factionIconOverrides`**, `factionIdeoIconOverrides`, `factionColorOverrides`,
`factionPopulationOverrides`, `savedFactionDefs` and `savedSettlementsData`. UI covers
`Window_ManageFactions`, `Window_AddFaction`, `Window_FactionCustomization`,
`Window_PopulationEditor`, `Window_SettlementCustomization`, `Window_IdeoIconPicker`.
Harmony patches cover `FactionDef.FactionIcon`, `Faction.Name`, `Faction.LeaderTitle`,
`Faction.CanChangeGoodwillFor` and `FactionGenerator.GenerateFactionsIntoWorld`. **[V]**

**Notably, it explicitly integrates with World Tech Level** and ships a
`WorldTechLevel_WITab_Planet_FillTab` transpiler. No equivalent exists between Node
Research and WTL. **[V]**

MP hazards **[I], concrete**: presets are files under
`GenFilePaths.FolderUnderSaveData("Worldbuilder")` with a `Dialog_FileSelector` and a
`syncToExternalFile` flag — per-machine filesystem paths inside game state — plus static
graphic caches and a `Rand_EnsureStateStackEmpty_Patch`.

**Verdict: RESTAT as a pre-game authoring tool** (same posture as Faction Customizer),
never live in a co-op session. Node Research and Worldbuilder are two limbs of the same
1,400-mod Progression Modpack ecosystem; adopting one pulls you toward its assumptions.

---

## 13. What this changes

Nothing here commits the project to anything. But seven things are now settled enough to
stop re-litigating:

1. **The Chronicle does not need a second assembly.** §7.8 is a complete architecture
   out of vanilla nodes plus VEF, and VQE Ancients proves the chain works.
2. **The altar does not need one either.** §9.1 assembles the whole religion→industry
   arc from four vanilla comps and a retargeted vanilla ritual.
3. **Threat can track time instead of wealth today, for free.** §8.1. The remaining work
   is the *quality* axis, and World Tech Level's gear replacement is the lever.
4. **The era gate is currently single-point-of-failure.** §8.3 — five hostile Industrial
   factions with no points curve, gated only by Ignorance Is Bliss, which depends on
   TechBlock, which desyncs. Five `PatchOperationAdd`s close it.
5. **Two of the five asks are done and two more are nearly free.** §10. The animal trough
   is the only genuinely unclaimed one, and it has a ~15-line XML path nobody has taken.
6. **Story Framework is closed.** §12.1.
7. ~~**Licence, not quality, is what gates the art.**~~ **STRUCK.** Licence is not a
   constraint on this project. The whole bin — 14,000-plus sprites, plus every
   `Source/` folder in it — is available. §4.

And two things to decide deliberately rather than drift into:

**VEF is close to a one-way door.** It is the only source of XML quest chaining,
`LootableBuilding`, KCSG and the facility-topology extensions; it dropped its
Multiplayer API integration in 1.6; and its GameComponents scribe by class name, so if
the Chronicle is built on `QuestChainExtension` that decision is effectively made at
scenario setup. *(The original entry also called it never-vendorable on licence
grounds. Struck — vendoring VEF is available to us if depending on it proves fragile,
which is the real escape hatch.)*

**Client-local `ModSettings` is the project's real desync surface, not `Rand`.** Fifty-one
of the installed mods have one. Every tunable Archinity ships should be a **Def**.

---

## 14. Open items

- **Install *Multiplayer Compatibility* (`1629973374`) before any co-op smoke test.**
  Without it the entire VE stack — ~40 of the 108 mods — runs unsynced, and it fixes
  VPE's viewport-gated RNG class explicitly.
- **Decompile `[WG] RimPacts` (`3762723122`)** before building faction demands (§10.3).
- **Verify whether More Realistic Research's study loop functions without the Anomaly
  DLC** on the target install (§5.4). It is unguarded and undeclared.
- **Smoke-test one workbench replace in a real MP session** before building progression
  on Replace Stuff (§10.5).
- **Reconcile `Archinity.Pacing/Patches/Retier_Medieval.xml` against VFE Tribals'
  `Core.xml`** — they retier overlapping vanilla buildings and the loser is silent (§5.3).
- ~~Ask three authors for art permission.~~ **STRUCK** — licence is not a constraint
  on this project.
- **Audit Biotech for Gravship's unseeded gene `Rand`** (§5.11) before use.
- Not assessed at depth, and cheap to finish if wanted: `3697533935` Tribal Siege Raids,
  `3309003431` VFE Insectoids 2, `2860414285` Vanilla Combat Reloaded and `3749200746`
  TakeCover (combat-AI changes are a classic desync source and neither of the last two is
  covered by the compat layer), and the full enumeration of VEF's XML-driven
  raid/arrival-mode knobs.
