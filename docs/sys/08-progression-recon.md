# 08 — The Progression Modpack: recon

**Not a workstream.** This is a competitor teardown, recorded so the conclusions are not
re-litigated. Five parallel research agents, 2026-08-23. Everything here is sourced; the
unverified items are marked as such and should not be repeated as fact.

**The question it answers:** should Archinity be built on top of an existing mega-pack
instead of authored from scratch, and what has that pack already solved that we have not?

---

## What it is

**The Progression Modpack**, by `ferny` / `misterferny`. Steam Workshop `3521297585`, 1.6.
Seven years old, ~20,000 claimed active users, daily playtesting, same-day patching.

Its stated goal is ours, almost word for word:

> *"Your journey starts as a caveman, and takes you into godhood all within one authored
> and tailored brand-new experience."*
> *"Don't you find it odd that in vanilla Rimworld, you are given the ability to fly a
> spaceship and command an army of robots in the first five minutes of the game?"*

| Collection | Items | Contents |
| --- | ---: | --- |
| The Progression Modpack (1/3) — `3521297585` | **843** | Frameworks, UI/menu overhauls, the research and era system, ferny's ~119 custom mods, the soundtrack, QoL |
| The Progression Content (2/3) — `3521319712` | **396** | Factions, creatures, biomes, genetics, weapons, buildings, ideology |
| The Progression Cosmetics (3/3) — `3637541646` | **175** | Retextures, hair, apparel, VFX |

≈1,414 total, matching their own "1400 mods" claim. The 843 figure from the Steam
Collection API is the main collection only — not a discrepancy.

**The single most useful number in this document: the content is 396 mods, and the
apparatus needed to make 396 mods cohere is 843.** Most of the pile is the cost of the
pile. That is the strongest available argument for staying small.

---

## The verdict, in one line

> **They prune research projects. They never prune content. And they never authored a story.**

Everything below is elaboration on that.

---

## What they actually built

### Era gating — `Node Research` (`3729878405`), read from source

Vanilla `TechLevel` ladder, unmodified: `Animal → Neolithic → Medieval → Industrial →
Spacer → Ultra → Archotech`. Same spine we use.

- `Startup.GenerateEmergenceDefs()` auto-generates one **"Emergence"** `ResearchProjectDef`
  per era.
- `UpdateEmergenceNodes()` sets that node's `prerequisites` to every project tagged with
  `ResearchFoundationExtension` at that tech level. Foundations are a **hardcoded defName
  list** applied by `PatchOperationAddModExtension`, not auto-detected: `Electricity`,
  `AirConditioning`, `MicroelectronicsBasics`, `Machining`, `MultiAnalyzer`, `Fabrication`,
  `Smithing`, `Stonecutting`, `ShipBasics`, `ShipEngine`, `ShipReactor`,
  `AdvancedFabrication`, `MedicineProduction`. Per-mod additions include VFE-Tribals'
  `Fire` and `Culture`, and Medieval Overhaul's Steel, Engineering, Basic Woodworking and
  Textile Spinning.
- Completing the emergence node writes `Faction.OfPlayer.def.techLevel` directly.
- Tunable: `AdvancementType { Foundations, EraCompletion }` (default `Foundations`),
  `enableTechAdvancement`, `restrictResearchToTechLevel` (default on — blocks researching
  above tier). Per-era costs are flat and hand-tuned, 500 Neolithic → 100,000 Archotech.

**vs TechBlock (`1970774610`).** `EraCompletion` at 100% is functionally TechBlock.
TechBlock scales its capstone cost *proportionally to the number of projects in the era*;
Node Research's costs are flat constants. TechBlock's model is better for us because our
node count is still moving.

**It cannot coexist with any other research-tree mod** — "mods will compete for the right
to be the vanilla menu." Adopting it replaces TechBlock, it does not join it.

**Two decisions it already implements that `VISION.md` reached independently:**
`VFETribals_Rituals_Patch.cs` + the `disableVFETribalsAdvancement` setting turn off
VFE-Tribals' ritual advancement and grant a **Cornerstone point** on era advance instead.
That is exactly our stated position.

### The era-boundary beat is real, and empty

`Window_TechAdvance.cs` + `ResearchManager_FinishProject_Patch.cs`: force-pauses the game,
plays a full-screen animated pan across tech-level icons, fires a dedicated sound cue
(`BRM_Advancement`), and prints three generic lines — *"Advanced to {Era}!"*,
*"{N} projects unlocked"*, *"Colony is now {Era}"*. Same strings for all six eras.
`Keys.xml` contains no lore, no letters, no quests.

**The presentation is worth copying. The content is the thing they didn't do.**

### The `Progression: X` family — 26 repos

Core, Production, Education, Aesthetics *(discontinued)*, Agriculture, Worlds, Defenses,
Drugs, Equipment *(dead)*, Factories, Fantasy, Furniture, Genetics, Gravship, Hives,
Hospitality, Kitchen, Robotics/Robotics-2, Scenarios, Storage, Storytellers, Temperature,
Therapy, Verticality, Warrants.

None of them gate eras — that is entirely Node Research's job. They **feed content into
Node Research's tech-level buckets** by re-tiering, consolidating or pruning other mods'
research defs.

- **`Progression: Production`** (`3453408412`) retiers vanilla **Stonecutting and Smithing
  down into Neolithic** (both Medieval in vanilla), plus MO's Basic Woodworking and
  Textile Spinning. Explicitly *"does not add new buildings, consolidate workbenches into
  fewer structures, or hide obsolete buildings."*
- **`Progression: Agriculture`** (`3418017359`) **does prune**: removes Core's Devilstrand,
  MO's Intermediate and Advanced Agriculture, Regrowth 2's Berry and Mushroom Cultivation,
  VFE-Tribals' Cultivation and Medicine; folds VFE-Farming's planter boxes into MO's
  leftover project.
- **`Progression: Kitchen`** (`3424640315`) gates meal tiers to Agriculture's crop tiers —
  structurally our food ladder, arrived at independently, without the buff scaling.
- **`Progression: Robotics`** (`3736402055`) delays the mechanoid crash-ship and mechanitor
  path until mechanoids are researched. Targeted threat-class gating.
- **`Progression: Storage`** (`3292746186`) rebalances storage buildings onto a consistent
  curve. Retiers, does not merge or hide.

Note the direction: **they compress the early tree downward. We stretch it.**

---

## What they did NOT build

The most valuable finding. All five of our hardest asks are unclaimed after seven years,
119 repos and a team.

| Our problem | What exists |
| --- | --- |
| **The trough** — penned animals eat less | Nothing. Third-party *Animal Feed Trough (Continued)* (`2071757940`) is a decorative hay/kibble object with **no consumption-reduction mechanic**. |
| **Ingredient-tier scaling food buffs** | Nothing anywhere. `Progression: Kitchen` gates *which* tiers unlock, never scales an effect. |
| **Faction demands, deadlines, non-material renown** | Nothing. Closest is *Back For Vengeance* — raiders remember and retaliate. A consequence system, not a demand system. |
| **Colony coat of arms on banners / tabards / shields** | Nothing. *Coat of Arms - Faction Icon Editor* (`3677207603`) is a **world-map faction icon designer only**; it does not apply the emblem to gear. |
| **Bench upgrade-in-place with persistent facility links** | Nothing. `Progression: Factories` / `Production` retier research, not the bench object. |
| **Era-appropriate raid gear** | Partial — `Progression: Robotics` for mechs specifically. General raid tech-levelling is *Ignorance Is Bliss* (`2554423472`), **already in our load order**. |

**No authored questline, no branching arc, no ascension mechanic.** "Godhood" is flavour
language for reaching archotech-tier research plus gravship content. "Narrative tools" in
their marketing resolves to Storytellers + Perspective Shift + Character Development +
Consistent Text — **no quest, dialogue or event-scripting editor exists in the catalogue.**

---

## Techniques worth taking

1. **Ship mod settings as a mod.** `Fernys-Mod-Configs` (`3256902751`) bakes recommended
   settings into a versioned artifact. Directly answers the `CLAUDE.md` multiplayer
   footgun — *"identical mod settings… the third is the one people miss."*
2. **Rename the stub, don't delete it.** `Progression: Agriculture` gutted MO's "Basic
   Agriculture" down to one unlock and **renamed the project to "Planter Boxes"** rather
   than deleting it. The def survives, every prerequisite still resolves, the player sees a
   coherent node. This sidesteps the entire `CLAUDE.md` re-parent → neuter → delete trap.
3. **Load-order tooling.** `Load-Them-Last` forces named mods' defs to load last. Same wall
   as our two `ParentName` / merged-database silent failures.
4. **Systematic text consistency.** `Consistent-Text` (`3578462306`) — pure XML
   `PatchOperation`s, 400+ lines: capitalization, terminology, and stripping references to
   *"modding"* and *"mod configuration"* out of flavour text so nothing breaks fiction.
5. **Architect-category splitters.** Eleven small XML mods splitting the build menu
   (Transport / Lighting / Bedroom / Animals / Culture / Environment / Automation…). No
   save state, effectively zero MP risk.
6. **The ceremonial era beat**, decoupled from its empty text. Cheap, and their data says
   it lands.

### Outside leads, worth evaluating on their own merits

- **`[SR]Factional War (fork)`** — confirmed in-pack. Factions fight *each other* on and
  near the player's map: assaults, artillery, cargo disputes. Direct hit on the
  design-philosophy §7.1 requirement that *factions must want things from each other*.
- **`Story Framework`** — pure-XML mission/objective authoring, **no C# assembly**. The
  only real candidate found for authoring the Chronicle under our one-assembly rule.
  Ecosystem-adjacent; not confirmed in-pack.
- **`Lemmy's Progression Mod For World Tech Levels`** (`3548896697`) — built for ferny's
  pack; map factions probabilistically tech up over time by faction-def substitution.
  Makes the *world* age forward instead of freezing at spawn tier.
- **`Worldbuilder`** (`3522102833`) — in-game biome/terrain/landmark painter, standalone,
  co-developed with Taranchuk and the VE team. Relevant if Glitterite installations ever
  need a hand-authored world-map presence.
- **Threat variety for M→Industrial**: `Dark Ages: Beasts and Monsters`, `Dark Ages: Crypts
  and Tombs`, `Epochs - Golems`.

### MP-verified QoL (entries exist in `rwmt/Multiplayer-Compatibility`)

`LWM's Deep Storage` (`1617282896`) · `Dubs Mint Menus` (`1446523594`) · `Work Tab` ·
`Pick Up And Haul` · `Common Sense`. `Performance Fish` self-declares MP-compatible
(needs Prepatcher + Fishery).

Note Progression chose **Adaptive Storage Framework**, not LWM. At 70 mods LWM is the
safer pick and it is the one with a documented MP patch.

---

## Warnings

**Granularity — the one to actually act on.** Their players complain the tree is *too
granular*: separate research projects per storage container type called "clutter," and a
note that some exercise-equipment variants demand more research mastery than *"electricity
and several applications thereof."* Ferny confirms it is deliberate. An experienced player
counters that the extra steps create *"disaster dominoes"* rendering early scenarios
unwinnable.

They draw that complaint with **843 mods spread across six eras.** We have 101 nodes across
two. Counterpoint from the same thread: a player reached **day 100 on a tribe start without
finishing Neolithic research**, and another was stuck at 5 of 6 foundations — so their early
game is deep, not thin, and our 27-node N1 is not obviously out of line.

**Performance.** Reported **140–170 TPS** on a Ryzen 5700X / 32GB / RTX-class rig.
*"Expect it to take around half an hour to start. Not just on the first start, but on every
start."* For two-player co-op that is disqualifying on its own — every desync-and-rehost
costs 40 minutes.

**Licensing.** `github.com/fernyrepos` is a **personal account, ~119 repos, and no LICENSE
file was found in any repo checked** — including `Progression-Core` and `Worldbuilder`.
"Open-source" here means publicly readable, **not licensed for reuse.** Funded via
Patreon. Read the technique; do not copy the code without asking.

**Multiplayer.** No page, discussion or repo mentions the Multiplayer mod. Roughly half of
ferny's 119 repos ship C#. Node Research contains zero references to Multiplayer; it mutates
`Faction.def.techLevel` and `DefDatabase` inside a `ResearchManager.FinishProject` postfix —
*plausibly* deterministic, but that is inference, not confirmation.

**Steam availability.** Four pages found pulled for Community Guidelines violations across
the research: `CE Removals`, `Progression: Core`, `Progression: Scenarios`, and the
Cosmetics collection. Reasons unstated in all four. Ferny posts mirror links because
*"steam keeps taking down the page."* Real availability risk if anything here becomes a
dependency.

---

## Corrections logged

- **The Epochs mods are not ferny's.** Author is **DetVisor**. Small flavour additions,
  mostly research-free — side content, not era-defining systems.
- **"They never remove anything" was too broad.** They prune *research projects*
  (`Progression: Agriculture`). They never prune *content* — the ThingDefs those nodes
  gated stay in the game forever.
- **Regression** — a community ~750-mod trim of Progression "with additional QoL,
  automation and less tedium." Their own ecosystem treats the volume as a cost.

## Unverified — do not repeat as fact

- Node Research MP compatibility, either direction.
- Whether `Progression: Core` patches `tradeTags` (page never loaded through rate limiting).
- Whether Rim War / Faction Territories / Vassalage are in the Content collection.
- Claim that quest loot tables were "revamped to increase rewards."
- The 20,000-users and 100+-custom-mods figures are the pack's own marketing.
- Only ~30 of ~119 `fernyrepos` repos enumerated in detail.
- No Reddit or YouTube sourcing obtained; all player quotes are Steam comments.

---

## The conclusion

Build our own; mine theirs. Seven years and 119 repos went into making 1400 mods coexist.
Almost none of it went into deciding what should exist. The two things Progression
structurally cannot give us — **two-player multiplayer** and **an authored campaign** — are
the entire justification for this project, and they are sufficient.

**If multiplayer stops mattering, or the Chronicle stops mattering, the honest answer flips
and we should go play Progression instead.**

## Work items

Tracked in `docs/HANDOFF.md`. This document is the evidence, not the task list.
