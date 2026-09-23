# The psychic track

## Purpose and scope

What RimWorld 1.6 and Vanilla Psycasts Expanded (VPE) can do for the campaign's psychic
ladder: who can enter which psycaster path, and what writes a pawn's psylink rank. Each
capability ticket that touches the track adds a section below. Whether VPE ships, which
paths survive, reskins and the `VPE_Archon` rename belong to
[the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119).

Requirements answered here:

- [`docs/requirements/ALTAR.md`](../requirements/ALTAR.md) § *One apparatus and separate rewards*: core
  vectors are mark-locked; psychic discipleship is distinct from genetic augmentation; the
  psychic ladder measures channel capability, and the first psylink is Medieval.
- [Who the altar serves](https://github.com/cjd721/Rimworld-Archinity/issues/10) §5 (closed)
  settled founder-only paths in principle: disciples have no rank ceiling, and the founders
  stay above them by holding paths nobody else may enter. Whether that door is built at all
  is [the power grid](https://github.com/cjd721/Rimworld-Archinity/issues/31)'s Q2.

**Why a document of its own and not a section of `ALTAR.md`.** `ALTAR.md` owns the altar's
builds: the gene author, the lottery and the charge. The psychic track reaches past the
altar. VPE's path gates, the XP loop that writes psylink rank
([#163](https://github.com/cjd721/Rimworld-Archinity/issues/163)), disciples and NPC casters
all live outside it. `TRANSCENDENCE.md` already lists founder psylink progression as a gap
with no owner. This document is where those answers land.

Adjacent systems take over at these points:

- the founder identity record (`CompFounderRecord` on `Archinity_FounderRecord`) —
  `TRANSCENDENCE.md` and [#134](https://github.com/cjd721/Rimworld-Archinity/issues/134)
  route A1;
- the altar's gene installation — `ALTAR.md`;
- android psylinks — `ANDROIDS.md`;
- engine facts on focus gates and VPE's Multiplayer hooks — `docs/engine/psycasts-and-meditation.md`.

---

## Vanilla Psycasts Expanded — the facts every section rests on

Read from `2842502659/1.6/Assemblies/VanillaPsycastsExpanded.dll`, decompiled whole, and
from VPE's 1.6 defs, on [#162](https://github.com/cjd721/Rimworld-Archinity/issues/162).
The inherited claims below came from [#33](https://github.com/cjd721/Rimworld-Archinity/issues/33),
`docs/data/PARTS-BIN.md` §9.2 and #10 §5–6, and #162 re-derived each one. Corrections are marked.

- **15 live paths in VPE**, five levels each, and 150 `AbilityDef`s. The corpus carries 20
  at 1.6, because add-ons contribute five more: `VPEH_Hemosage`, `VPEP_Puppeteer`,
  `VREA_Transcendent`, `AM_Circuitbinder` and `AM_Technowraith`. [V, #33]
- **The path gate.** `PsycasterPathDef.CanPawnUnlock(Pawn)` is **`virtual`** and is the AND
  of **five** conditions: `requiredBackstoriesAny` (any listed category in the named
  slot), `requiredMeme` (on `pawn.Ideo`), `requiredGene` (present **and `Active`**),
  `requiredMechanitor` and `requiredFocus` (`MeditationFocusDef.CanPawnUse`). [V]
  - **Correction.** The inherited claim was "seven fields AND-ed". `lockedReason` is only
    display text, and `ensureLockRequirement` is a recheck flag. An **eighth** field
    matters more than either: **`ignoreLockRestrictionsForNeurotrainers`, which defaults
    to `true`**. See *Where the gate is read*, below.
- **Where the gate is read.** [V] Only five places consult `CanPawnUnlock`:
  - `ITab_Pawn_Psycasts`, for the *Unlock* button (spend a point, then `UnlockPath`);
  - `PawnGen_Patch`, for NPC paths;
  - `PsycastUtility.RecheckPaths`, only for paths with `ensureLockRequirement`;
  - `CompPsytrainer.CanBeUsedBy` and `AbilityExtension_Psycast.IsEnabledForPawn`, but
    **only when `ignoreLockRestrictionsForNeurotrainers` is false**.

  With the default `true`, a psytrainer unlocks a locked path and a psyring grants a
  locked ability, and either one casts (T-167). `ensureLockRequirement` alone parks a
  psytrainer-opened path at the next recheck, but never touches a psyring's ability, whose
  path was never unlocked. [V]
- **`ensureLockRequirement`.** `RecheckPaths` moves a path between `unlockedPaths` and
  `previousUnlockedPaths` as `CanPawnUnlock` flips. `AbilityExtension_Psycast.ShowGizmoOnPawn`
  hides the gizmos of a parked path. Learned abilities stay learned. The path comes back
  free when the key returns. [V]
  - **Correction.** #33 said this "refunds the point". Nothing touches `points`: the unlock is
    parked, not refunded.
  - **Correction.** The recheck is not continuous. It runs only from postfixes on
    `HediffSet.DirtyCache`, `Pawn_GeneTracker.Notify_GenesChanged` and
    `Pawn_AbilityTracker.Notify_TemporaryAbilitiesChanged` (T-168).
- **A hediff can grant a focus per pawn.**
  - `MeditationFocusTypeAvailabilityCache.PawnCanUseInt` returns true when any hediff lists
    the focus in `HediffDef.allowedMeditationFocusTypes`. [V]
  - It returns false for a focus that some trait or hediff *could* grant but this pawn
    lacks. A focus referenced only by our hediff is therefore closed to everyone else. [V]
  - `HediffSet.DirtyCache` clears that cache before VPE's recheck runs. [V]
  - VPE's postfix on `PawnCanUseInt` also admits any focus the pawn bought with a point
    (`unlockedMeditationFoci`). `MeditationUtilities.CanUnlock` refuses to sell a focus
    whose `MeditationFocusExtension.canBeUnlocked` is false. [V]
- **Hijack of the vanilla psylink** [V, #33 and PARTS-BIN §9.2]:
  - A postfix on `Hediff_Psylink.PostAdd` attaches `VPE_PsycastAbilityImplant` to any pawn
    that gains a psylink.
  - `Hediff_Psylink.TryGiveAbilityOfLevel` is disabled.
  - `Hediff_Psylink.ChangeLevel` is rerouted into `Hediff_PsycastAbilities.ChangeLevel`,
    which writes the psylink's level. **Psycaster level and psylink rank are one number.**
    #163 owns what writes it.
- **Multiplayer.** PARTS-BIN §9.2 lists four desync classes:
  - MP Compat syncs `UnlockPath`, `UnlockMeditationFocus`, `SpentPoints`, `ImproveStats`
    and `GainExperience`, which covers the UI class (`docs/engine/psycasts-and-meditation.md`
    § *Multiplayer*) [V]. It also covers the viewport-gated RNG class.
  - `XPPerPercent` and `maxLevel` are per-install settings (T-18). MP's join-time config sync
    hands a joiner the host's file; only a mid-session change diverges (#163, route B).
    `maxLevel` mutates `PsychicAmplifier.maxSeverity` at runtime. That is #163's and #119's to
    close.

---

## A psycaster path only the founders can take

### Purpose and scope

Can a VPE path be opened to the two founders and closed to everyone else, and what key
tells VPE who a founder is? Asked on [#162](https://github.com/cjd721/Rimworld-Archinity/issues/162),
superseding #33 clause 3's gene key. The ticket is scoped to the door: whether it can be
built, not whether it exists or which path goes behind it.

### Verdict

- **Possible? Yes.** Every candidate key works. They differ in what leaks and in how much
  of it XML can close. **Whatever the key, the door leaks until the path sets
  `ignoreLockRestrictionsForNeurotrainers false`**: psytrainers and psyrings bypass every
  key by default (T-167).
- **Multiplayer? Yes.** Every key is saved per-pawn state read in simulation, and the
  unlock clicks are already synced by MP Compat. One inherited exception: route F1 and
  route F5 read #134's A1 record, which a player joining under MP multifaction never
  receives.

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **F1. Founder focus fed by the founder record** | Path `requiredFocus` = our own focus. Only `Archinity_FounderRecord` grants it (`allowedMeditationFocusTypes`). Opens at tick 0 and closes if the record goes | vanilla focus cache + VPE path fields + #134 A1 | XML on top of A1's C# | Easy, once A1 exists | Yes (multifaction: A1's caveat) |
| **F2. Gene key on an altar-installed gene** | Path `requiredGene` = a gene the altar installs on the founders; opens when it is installed | VPE path fields + our `GeneDef` + the altar | XML; C# to close two leaks | Easy to open; Medium to seal | Yes |
| **F3. `VREA_Transcendent` as it ships** | A finished five-level path keyed on `VRE_Transcendent`, the gene the final rite grants. **Post-transcendence only** | VRE–Archon `1.6/VPsycastsE/` | none (XML to seal) | Easy | Yes |
| **F4a. Leave `VPE_Archotechist` as the Church's** | Nothing for the founders. It stays a path for imperial-backstory pawns, which after #53 means Church-born pawns | VPE as it ships | none | Easy | Yes |
| **F4b. Re-key `VPE_Archotechist`** | VPE's "archotech" path becomes the founders': replace its `requiredBackstoriesAny` with F1's, F2's, F5's or F6's key | VPE + an XML patch | XML | Easy | Yes |
| **F5. The gate reads the founder record directly** | No proxy focus or gene. A `DefModExtension` marks founder paths and a postfix on `PsycasterPathDef.CanPawnUnlock` checks `CompFounderRecord`. The alternative is a `PsycasterPathDef` subclass overriding the virtual | our code + A1 | C# | Medium | Yes (multifaction: A1's caveat) |
| **F6. A founder backstory category** | The founders start with authored backstories carrying the spawn category `Archinity_Founder`, and the path lists it in `requiredBackstoriesAny`. The only key that needs no C# at all | scenario `overrideKinds` (#134 A2) + our `BackstoryDef`s + VPE path fields | XML | Easy | Yes |

**Keys examined and rejected.**
- `requiredMeme` is per-ideoligion, so every convert shares it. An ideoligion change also
  fires none of `RecheckPaths`'s three signals (T-168).
- `requiredMechanitor` is not identity.
- A trait feeding F1's focus (`TraitDegreeData.allowedMeditationFocusTypes` is read before
  hediffs) is strictly dominated by the hediff. An Anomaly duplicate copies traits and no
  trait flag opts out. [V] (Anomaly is outside [the DLC floor](https://github.com/cjd721/Rimworld-Archinity/issues/6),
  so that leak is moot today; the trait still offers nothing the hediff lacks.)
- An ability cannot key a path: `PsycasterPathDef` has no such field. [V]

**Every route also needs the sealing flags.** Set `<ignoreLockRestrictionsForNeurotrainers>false</ignoreLockRestrictionsForNeurotrainers>`
and `<ensureLockRequirement>true</ensureLockRequirement>` on the path. The corpus already
ships that shape: `VPEH_Hemosage` sets both. [V] #10 §5's decision to cut neurotrainers
closes the trainer half. **It does not close the psyring half.** Only the flag does, or
listing the path's abilities on `VPE_CraftPsyRing`'s `PsyringExclusionExtension` (XML).

#### Where each key leaks

Read [V] unless marked. "Closed" names the lever.

| Leak path | F1 focus + record | F2 altar gene | F3 `VRE_Transcendent` | F6 backstory |
|---|---|---|---|---|
| **Psytrainer / psyring** (T-167) | sealing flag (XML) | sealing flag | sealing flag | sealing flag |
| **Buying the focus with a VPE point** | closed by `canBeUnlocked false` (XML) | — | — | — |
| **Anomaly duplicate** (Anomaly only: outside the DLC floor, [#6](https://github.com/cjd721/Rimworld-Archinity/issues/6); moot unless Anomaly is added) | closed by `duplicationAllowed false` on the record (T-113, XML) | **leaks**: `CopyGenes` copies every gene; no gene flag (C#) | **leaks** (C#) | **leaks**: the duplicator copies `Childhood`/`Adulthood` (C#) |
| **Xenogerm reimplant** (converts) | — | closed if the gene is a per-pawn **endogene** not in the founders' `XenotypeDef`. `ReimplantXenogerm` copies only the caster's xenotype list and xenogenes. As a xenogene it leaks, but our existing `ReimplantXenogermPatch` already strips `founderOnlyGenes` | depends on how the rite installs it (build) | — |
| **Xenogerm implanted *on* a founder** (false negative) | — | endogene survives (`ImplantXenogermItem` → `SetXenotype` clears xenogenes only) | same | — |
| **Gene extraction** | — | closed if `biostatArc > 0`: vanilla `Building_GeneExtractor` and Biotech for Gravship's extractor weight archite genes 0. **More Archotech Garbage's `ArchotechGeneExtractor` extracts archite genes**, and its `ArchotechGeneRipper` lets the player pick any gene, archite included (`Dialog_SelectGenes` has no archite filter), killing the donor (C#, or keep MAG out) | same as F2 | — |
| **Random genepacks** | — | `canGenerateInGeneSet false` (XML; `GeneSet.CanAddGeneDuringGeneration` reads it). **MAG's `CompArchiteGenepackSpawner` ignores it** (C#) | **leaks today**: `VRE_Transcendent` leaves the field at its default `true` (XML patch) | — |
| **VQE Ancients archogen injector** | — | `InjectionBlacklistDef` (XML) | already blacklisted by `ArchiteInjection_Blacklist.xml` | — |
| **Inheritance** | — | closed for `biostatArc > 0` (`PregnancyUtility.GetInheritedGenes`) | the `VRE_Archon` xenotype is `inheritable` [I: archon parents] | — |
| **NPCs born with the key** | none | none unless we author a carrier | **every `VRE_Archon` pawn** (xenotype carries it plus `VRE_InnatePsylink`), so a captured archon qualifies [I: capture and recruit] | none unless a kind lists the category [I] |
| **Start-screen editors** | `scenarioCanAdd` defaults false | [I] | [I] | **Prepare Carefully and character editors can hand any pawn the backstory** [I] |
| **VEF `HediffComp_AsexualReproduction`** | — | copies all endogenes to offspring (humanlike carriers [I]) | same | — |

#### F1 — founder focus fed by the founder record

**What it gets us**
- Identity from tick 0, inherited from #134 A1: the path opens the moment the record is
  stamped. [I, composition]
- **Every leak we found closes in XML**:
  - the sealing flags on the path;
  - `canBeUnlocked false` on the focus's `MeditationFocusExtension`;
  - `duplicationAllowed false` on the record, which A1 already requires (only matters if
    Anomaly is ever added, #6).
- Dynamic in both directions. A record added or removed runs `HediffSet.DirtyCache`, which
  clears the focus cache and runs `RecheckPaths`, so the path parks and returns with no
  code. [V mechanism; I composition]
- One focus can key any number of founder paths.
- A second focus, granted by a second hediff, can AND a further condition onto one path.
  #10 §5 sketched this with certainty for disciples.

**What it cannot do**
- **Stand without A1.** A1 is Medium C# (#134). F1 is only the XML on top of it.
- **Be invisible.** The founder focus is a real `MeditationFocusDef`. It shows in the
  pawn's focus list, and in VPE's focus grid as a locked tile. The fiction owns what it is
  called.
- **Be pure XML end to end.** `ScenPart_ForcedHediff` has no xenotype filter, so the record
  cannot be stamped in XML (#134 A1).

**Consequences.** The record becomes load-bearing for the psychic track as well as quests.
Anything that deletes the record (dev mode, hediff-removal mods [I]) now also closes the
founders' path.

#### F2 — gene key on an altar-installed gene

**What it gets us**
- The #10 §5 design, nearly as written: one `requiredGene` field on the path.
- The path opens at the altar rite that installs the gene, which is a story beat.
- `Notify_GenesChanged` triggers the recheck, so the path follows the gene. [V]

**What it cannot do**
- **Identify a founder by itself** (T-111). It is safe only for a gene with all of these:
  - installed per pawn as an **endogene**;
  - absent from `Archinity_ArchonianSanguophage`'s gene list;
  - `biostatArc > 0`;
  - `canGenerateInGeneSet false`;
  - on VQE Ancients' blacklist.
- **Survive duplication.** The Anomaly duplicator copies genes with no opt-out, which needs
  C#. Anomaly is outside the DLC floor (#6), so this is moot unless it is added.
- **Survive More Archotech Garbage.** Its archite extractor, gene ripper and archite
  genepack spawner need C#, or MAG kept out.
- **Tolerate override.** `PawnHasGene` demands `Active`. A conflicting xenogene that
  overrides the key closes the path until it is removed. [V]
- **Name *which* founder** unless the altar already knows. Installing the gene only on a
  founder needs A1 anyway. [I]

**Consequences.** It re-imports the gene-as-identity weakness #134 rejected, then patches its
leaks one carrier at a time. Every gene-copying mod added later reopens the question.

#### F3 — `VREA_Transcendent` as it ships

**What it gets us**
- A complete path, gated `requiredGene VRE_Transcendent`, `lockedReason "Transcendent only"`.
  It loads from `1.6/VPsycastsE` only when VPE is active. [V]
- It keys on the gene the final rite already grants (`TRANSCENDENCE.md`, authority
  correction). No new key is authored.

**What it cannot do**
- **Serve as the founders' psychic ladder.** It opens after the final rite: *Enter the new
  reality* ends the game, and only *Stay* plays on. It is a postgame tier at most.
- **Stay founder-only as shipped.** It lacks both sealing flags [V]. `VRE_Transcendent`
  can drop in random genepacks. Every `VRE_Archon` pawn carries it. Archinity pushes
  archon raids to day 999999 but keeps the faction for quest-summoned archons
  (`Faction_Archons.xml`), so a downed and captured archon is a transcendent psycaster.
  [I: capture and recruit]

**Consequences.** It needs an XML patch (the two flags, `canGenerateInGeneSet false`) and a
ruling on captured archons. VRE–Archon has **no MP Compat class**: an ASCII and
null-interleaved sweep of `1629973374/1.6` for `archon` returned zero, validated by its
`VREAndroids` hit. [V] Its own abilities' Multiplayer safety is unread. Its register ("pain",
"raining death") is the build map's call.

#### F4 — `VPE_Archotechist`

**F4a, leave it the Church's.** As shipped, `requiredBackstoriesAny` names `ImperialFighter`
and `ImperialRoyal`, childhood or adulthood. It has no `ensureLockRequirement`. [V] After
[#53](https://github.com/cjd721/Rimworld-Archinity/issues/53) that means Church-born pawns,
recruits included. Nothing to build.

**F4b, re-key it.** It is a list field, so one `PatchOperationReplace` on
`requiredBackstoriesAny`, plus the sealing flags and a new `lockedReason`, moves it to any
other key. Adding a founder key *beside* the imperial list ANDs them, and founders hold no
imperial backstory, so that opens it to nobody. **Re-keying is replacement.** The Church
then loses its only VPE-native path. [V fields; I composition]

**Consequences.** It is orthogonal to the key choice: F4b is "which path", F1/F2/F5/F6 are
"which key".

#### F5 — the gate reads the founder record directly

**What it gets us**
- No proxy. The path asks `CompFounderRecord` itself.
- A marker `DefModExtension` makes "founder-only" a one-line tag on any path, VPE's or ours.
- Seams [V]:
  - `CanPawnUnlock` is `public virtual`.
  - `DefDatabase<T>.AddAllInMods` takes `mod.AllDefs.OfType<T>()`, so a subclass tag such
    as `<Archinity.FounderPathDef>` still lands in `DefDatabase<PsycasterPathDef>`.
  - No corpus path uses a subclass today.

**What it cannot do**
- Stand without A1.
- Recheck on its own. `RecheckPaths` still runs only on the three signals, so a record added
  by code must go through `AddHediff`, as A1 does. That fires `DirtyCache`. [I]

**Consequences.** It is Harmony on a hot, UI-called method. The subclass shape avoids Harmony,
but whether `ResolveReferences` then runs once per database (`PsycasterPathDef.TotalPoints`
is a static counter) is an open build question. [I]

#### F6 — a founder backstory category

**What it gets us**
- **The only route with no C#.**
  - `ScenPart_ConfigPage_ConfigureStartingPawns_Xenotypes.overrideKinds` gives the two
    archonians a founder `PawnKindDef` (#134 A2 [V]).
  - `PawnKindDef` carries `fixedAdultBackstories` and `backstoryFiltersOverride`. [V fields]
  - The path lists `Archinity_Founder` in `requiredBackstoriesAny`.
- **It persists where A2's kind does not.** `Pawn.ChangeKind` touches only `kindDef`
  (and wild-man reachability), never the backstory. [V]
- It is the field `VPE_Archotechist` already uses, so F4b becomes a one-category swap.

**What it cannot do**
- Survive duplication. The duplicator assigns `Childhood`/`Adulthood` from the source, and
  there is no flag. [V] Anomaly-only, so moot at the DLC floor (#6).
- Resist start-screen editors. Prepare Carefully can assign any backstory. [I]
- Recheck. Nothing fires on a backstory change, so `ensureLockRequirement` never fires for
  it (T-168). A founder never loses it anyway.
- Leave the founders' backstory to the player. The founders' adult backstory becomes
  authored, or chosen from an authored set.

**Consequences.** Adult backstories carry skills and disabled work types, so the founders'
kit becomes a design output. That is a story cost as much as a technical one.

### Recommendation (not a selection)

- **F1 is the strongest key.** It sits on the identity route #134 already recommends. It
  opens at tick 0, and it is the only key whose every verified leak closes in XML.
- **F5** if the proxy focus is unwanted in the UI. It costs Medium C# for the same result.
- **F6** only if the build map wants no C# on this door, accepting the start-screen leak
  [I]. Its duplicate leak is Anomaly-only and moot at the DLC floor (#6).
- **F2 is not recommended as the founders' key.** It is technically possible, but it is
  the gene-as-identity route #134 rejected, and its leaks at the DLC floor (More Archotech
  Garbage's three gene paths, VEF asexual reproduction) need C#. Keep genes for what the
  altar gives, not for who may enter.
- **F3 is a postgame tier, not the door.** It needs sealing if it ships.
- **F4 is independent.** Pair any key with F4b, or leave Archotechist to the Church (F4a)
  and author a founders' path (~17 lines, #33).
- **Whatever is chosen, set the sealing flags on every gated path.** Consider #10 §5's
  startup-validator guard extended from "no psytrainer reachable" to "every gated path
  seals".

### Constraints

- **T-167.** A path lock gates only VPE's *Unlock* button unless
  `ignoreLockRestrictionsForNeurotrainers` is false.
- **T-168.** `ensureLockRequirement` rechecks on three signals, parks rather than revokes,
  and never refunds.
- **T-111 / T-113.** Genes and xenotype are not identity. Record hediffs copy into Anomaly
  duplicates unless they opt out.
- **`requiredGene` is one `GeneDef`, `requiredFocus` one `MeditationFocusDef`.** To AND two
  keys, use two different fields, or F5. [V]
- **NPC generation honours the gate.** `PawnGen_Patch` offers only paths passing
  `CanPawnUnlock`, so Basilicus and `PawnKindAbilityExtension_Psycasts` pawns never draw a
  founder path under F1, F5 or F6. Under F2 or F3 an NPC with the gene can. [V]

### Available mechanisms

- **Existing gates across the corpus at 1.6** [V, every `PsycasterPathDef` outside XML
  comments]:
  - Archotechist and Puppeteer: `requiredBackstoriesAny`.
  - Wildspeaker: `requiredFocus Natural`.
  - Circuitbinder and Technowraith: `requiredMechanitor`.
  - Hemosage: `requiredGene Hemogenic` plus both sealing flags.
  - Transcendent: `requiredGene VRE_Transcendent`.
  - The other twelve VPE paths are open.
  - No path uses `requiredMeme` or a subclass.
- **Hemosage is open to the founders and to every convert.** The founders' xenotype carries
  `Hemogenic`, and reimplant copies it. [V]
- **Psytrainers are implied, not authored.** `ThingDefGenerator_Neurotrainer_ImpliedThingDefs_Patch`
  makes one `Psytrainer_<ability>` per psycast `AbilityDef`, including any we add. Each is
  tagged `RewardStandardLowFreq` in `NeurotrainersPsycast`. [V]
- **Psyrings.** A caster with Technomancer's `VPE_CraftPsyRing` makes a ring from any psycast
  they know. `Psyring.Notify_Equipped` gives the ability to any psycaster who wears it and
  never consults the path. [V]
- **Donor for sealing genes against reimplant already exists:**
  `Archinity.Altar/Source/Patches.cs` `ReimplantXenogermPatch` strips `founderOnlyGenes`
  after reimplant. [V]
- **Wide pass for gene writers.**
  - Method: `AddGene\x00` over both roots' `.dll`s, excluding `obj/` and `Referenced/`. The
    trailing null only, because metadata strings share suffixes. Validated against
    `Assembly-CSharp.dll`.
  - Hits, 7 mods: VEF, VRE Android, Hussar, Waster, Starjack, VQE Ancients, Biotech for
    Gravship.
  - A second pass on `ReimplantXenogerm\x00|GetInheritedGenes\x00|Genepack\x00` added VRE
    Saurids, More Archotech Garbage and Multiplayer.
  - Decompiled and read for pawn-to-pawn copying: VEF, Hussar, Waster, VQE Ancients, BfG,
    Saurids, MAG. The table above records the leaks. The rest add fixed or random
    non-archite genes. [V]
  - Not read, with a name-level reason: VRE Android (android hardware) and Starjack. [I]

### Status

- **Evidence class: READ.** Settled by the decompiled VPE 1.6 assembly, `Assembly-CSharp.dll`
  1.6.4871, the seven gene-writer assemblies above, and the path, gene, xenotype and focus
  defs.
- The mechanisms are [V]. Every route is [I] by construction.
- Established by [#162](https://github.com/cjd721/Rimworld-Archinity/issues/162).
- Supersedes #33 clause 3's `requiredGene: <the mark>` key.
- Corrects:
  - #33's and PARTS-BIN §9.2's "seven fields AND-ed" and "refunds the point";
  - #10 §5's `Pawn_HealthTracker.DirtyCache`, which is `HediffSet.DirtyCache`;
  - #10 §5's assumption that cutting neurotrainers closes the bypass. Psyrings use the same
    flag.

### Open questions

- **Requirement, [#31](https://github.com/cjd721/Rimworld-Archinity/issues/31) Q2.** Does
  the founders-only door exist, and behind which path?
- **Requirement, #134's owner (unowned since #122 closed).** Is an Anomaly duplicate of a
  founder a founder? F1 says no by flag. F2, F3 and F6 say yes unless patched. Moot at the
  DLC floor ([#6](https://github.com/cjd721/Rimworld-Archinity/issues/6) rules Anomaly out);
  live only if Anomaly is added.
- **Build, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119):**
  - whether VPE and Technomancer ship;
  - whether More Archotech Garbage ships (it decides F2's seal);
  - F3's sealing and the captured-archon ruling;
  - F5's subclass or postfix;
  - the founder focus's name and icon;
  - how the final rite installs `VRE_Transcendent` (endogene or xenogene).
- **Unverified:** whether a captured `VRE_Archon` can be recruited. Whether Prepare
  Carefully can assign a founder-only backstory or hediff at start.

---

## What raises psylink rank besides the altar

### Purpose and scope

What in the bin raises a pawn's psylink rank other than the altar, and how can each writer be
closed? Asked on [#163](https://github.com/cjd721/Rimworld-Archinity/issues/163), using the
method of the research-bypass survey ([#83](https://github.com/cjd721/Rimworld-Archinity/issues/83),
`RESEARCH.md` § *Bypasses — the build*).

The rule under test comes from #10 §4 ("Rank comes from the altar") and #21. The requirement
text is a little wider. [`ALTAR.md`](../requirements/ALTAR.md) § *One apparatus and separate
rewards* says "willing-devotion rites **and later campaign breakthroughs**" advance the ladder,
and it frames meditation as *cultivation*. So this section treats **anything Archinity authors**
as a sanctioned writer: altar rites, and breakthroughs we script.

**A bypass is any other code path that does one of these:**
- gives a pawn its first psylink (adds `Hediff_Psylink`);
- raises `Hediff_Psylink.level`;
- raises VPE's `Hediff_PsycastAbilities.level`. Under VPE that is the same number as the
  psylink level (§ *Vanilla Psycasts Expanded — the facts every section rests on*).

**Three classes, because they close differently:**
- **R, raises:** changes the rank of a pawn the player already holds.
- **I, imports:** the pawn enters the player's hands already ranked (generation, then
  recruit or capture).
- **S, supplies:** puts a rank-raising item into the world. The item's comp is the writer
  (R1). S rows say where the items come from.

Out of scope:
- Psytrainers and psyrings open paths and abilities, not rank (T-167, above).
- Dev-mode tools.

### Verdict

- **Possible? Partly.** Every writer outside VPE's core loop closes, most of them in XML. **The
  rule does not survive VPE as shipped.** VPE's progression *is* a second writer: meditation
  earns XP, and XP raises the one rank number. The rule survives VPE only if that loop is cut or
  gated. The cleanest cut is **one Harmony prefix on `Hediff_PsycastAbilities.GainExperience`**,
  which every XP source funnels through (route D), or dropping VPE (route A). Under VPE, *any*
  psyfocus gain is XP: meditation, caravans, go-juice, deathrest buildings and about ten
  other feeders (R6). A settings-only cut exists (route B). It is a per-install value and misses the
  three abilities that grant raw XP.
- **Multiplayer? Yes, with one caveat.** Every XML and Harmony route acts on saved per-pawn
  state inside synced simulation (rituals, jobs, ability casts, item use). Route B is T-18:
  MP's join-time config sync covers VPE's settings file, but a mid-session change does not.

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **A. Drop VPE** | No XP loop at all. Vanilla rank moves only by discrete events, and C closes every one. The talent tree goes | a sourcing decision ([#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) / [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)) | none | Easy | Yes |
| **B. VPE settings: `XPPerPercent 0`** | Meditation stops writing rank. The three XP abilities still need C's XML | VPE as shipped | setting + XML | Easy | With work: T-18 (a mid-session change diverges) |
| **C. Close each carrier at its own def** | Every writer in the census below closed where it lives. Mostly XML; three carriers need C# or the inert-item lever | vanilla + the census mods | XML; small C# for three | Easy; Medium for the C# three | Yes |
| **D. One gate on `GainExperience`** | Covers every XP source at one seam. Three variants: **D1** XP to zero; **D2** XP raises the level only up to a per-pawn ceiling the altar writes; **D3** XP buys points instead of rank | our code on VPE's seam | C# (Harmony) | Medium | Yes |
| **E. Rank chokepoint gate** | Refuses any rank change not made under the altar's token, at `Hediff_PsycastAbilities.ChangeLevel(int)` plus the first-rank add. Catches writers nobody has catalogued yet | our code | C# (Harmony) | Medium | Yes |
| **I1. Strip imports in XML** | No generated ranked pawns reach the player: VPE's psycaster group makers and kinds, VFE Empire's deserter casters, `maxPsylinkLevel 0` on titles, no Basilicus | XML patches | XML | Easy | Yes |
| **I2. Clamp rank on joining** | A captured or recruited caster arrives at rank 0, or at a set rank, whatever generated it | our code on `Pawn.SetFaction` (#142's funnel) | C# | Medium | Yes |

#### A — drop VPE

**What it gets us**
- The rule holds by construction. Vanilla has no XP; rank moves only by the discrete events
  in R1–R5.
- Each of those events closes by C's XML, except the pity timer (R1/S1), which needs the
  inert-item lever or a small C# fix.

**What it cannot do**
- Keep the talent tree, the paths, or #162's founder door. PSYCHIC.md's first two sections
  assume VPE.

**Consequences.** This is a sourcing call, not a patch. It is listed because the ticket asked
whether VPE ships.

#### B — `XPPerPercent 0`

**What it gets us**
- One slider, every psyfocus-derived XP source: meditation, caravans and every psyfocus
  feeder in R6. All three of VPE's psyfocus patches call `GainXpFromPsyfocus`, which
  multiplies by `Settings.XPPerPercent`. [V]

**What it cannot do**
- **Close the three abilities.** `VPE_TimeskipMeditation` (+300 XP), `VPE_DrainPsyessence`
  (the victim's whole-level XP) and VPE-Puppeteer's `VPEP_Ascension` (puppet skill XP ÷ 100)
  pass raw XP, not scaled. They need C's XML. [V]
- **Be a campaign guarantee.** It is a per-install value that the player can change. MP's
  join-time sync (`Multiplayer.Client.Util.OverrideConfigsPatch`, and VPE uses
  `Mod.GetSettings`) hands a joiner the host's file. A change made mid-session does not
  propagate. [V]

**`maxLevel` is not the same lever, and it is not recommended.** It gates the XP loop
(`level < Settings.maxLevel`), so `maxLevel 1` stops XP above rank 1. But
`PsycastsMod.ApplySettings` also writes it into `HediffDefOf.PsychicAmplifier.maxSeverity`
[V]. That caps every vanilla consumer:
- `CompPsylinkable.CanPsylink`, via `GetMaxPsylinkLevel`, which is #10 §4's altar rite;
- the neuroformer's `CanBeUsedBy`;
- the psylink hediff's severity clamp.

So it caps the altar too.

#### C — close each carrier at its own def

**What it gets us.** A lever per carrier, listed in the census under *Available mechanisms*.
The load-bearing ones:
- **Make the neuroformer inert.** `PatchOperationRemove` its `CompProperties_UseEffectInstallImplant`
  (and `VFED_PsychicAmplifier`'s). This one lever closes every supply row (S1–S7) at once,
  including the two that are C# (the pity timer and Worksites' black-market list).
  **Do not delete the def**: `ThingDefOf`/`HediffDefOf.PsychicAmplifier`.
- **Remove `CompProperties_Psylinkable` from `Plant_TreeAnima` and VLE's
  `VEE_Plant_TreeAnima_Ancient`.** The altar's own rite reuses the comp on the altar (#10 §4)
  and is unaffected.
- **Repoint `BlindingCeremony`'s `workerClass` to `RitualOutcomeEffectWorker_FromQuality`.**
  The base class's `ApplyExtraOutcome` is empty [V], so the mood outcomes stay and the
  psylink goes. [I, composition] Drop the `extraPredictedOutcomeDescriptions` line as well.
- **`maxPsylinkLevel 0` on every title.** Vanilla Empire, VFE Empire's nine and the Church's
  (`RELIGION.md` §4 already plans the Church's).
- **Remove the XP abilities** `VPE_TimeskipMeditation`, `VPE_DrainPsyessence`,
  `VPEP_Ascension` and `VPEP_MindJump`. Use the pattern `RESEARCH.md` uses for
  `VPE_ReverseEngineer` (remove the ability and its path slot), coordinated with
  [#33](https://github.com/cjd721/Rimworld-Archinity/issues/33)'s path set.
- **`duplicationAllowed false`** on `PsychicAmplifier` and `VPE_PsycastAbilityImplant`.
  `GameComponent_PawnDuplicator` skips such hediffs [V], so an Anomaly duplicate is born
  unlinked. Only needed if Anomaly is added; it is outside the DLC floor (#6).

**What it cannot do**
- **The VPE bestowing floor.** `RitualOutcomeEffectWorker_Bestowing_Apply_Patch.ApplyTitlePsylink`
  gives rank 1 to a pawn with no VPE hediff **before** it reads the title. `maxPsylinkLevel 0`
  does not stop it. [V] Close it in C#, or hold no bestowing ceremonies.
- **Close the loop itself.** C closes the meditation writer and R6's psyfocus feeders only
  if paired with B or D.
- **Anything added later.** C is a census, and a mod added after this survey is a new row.
  #83 answered the same problem with a standing audit script; the same shape applies here
  (open question).

**Consequences.**
- An inert neuroformer still arrives: as a quest reward, as loot, in the black market. It
  becomes a 2,600-silver trade good, or the fiction repurposes it as an altar reagent.
- Removing the anima trees' linking removes the vanilla Neolithic psylink route the
  requirements already exclude (the first psylink is Medieval).

#### D — one gate on `GainExperience`

**What it gets us**
- One seam for the whole loop. Every XP source calls
  `Hediff_PsycastAbilities.GainExperience` [V]:
  - the meditation postfix (`JobDriver_Meditate`, and the caravan psyfocus tick, which
    earns XP without meditation);
  - the `OffsetPsyfocusDirectly` postfix and the `RechargePsyfocus` prefix, which turn every
    other psyfocus gain into XP (R6's feeders);
  - the Timeskip Meditation, Drain Psyessence and Ascension abilities;
  - the dev button.
- MP Compat registers it as a sync method, so the gate runs identically on every client.
- **D1, XP to zero.** The rule holds. VPE points then come only from altar-granted levels
  (`ChangeLevel` does `points += levelOffset`), so the talent tree advances at the altar's
  pace.
- **D2, a ceiling.** XP keeps levelling, but only up to a per-pawn ceiling the altar writes.
  VPE's own loop already stops at `Settings.maxLevel`, so D2 swaps a global cap for a
  per-pawn one.
  - This recovers #10 §4's intent ("levels within a rank come from cultivation") on a
    two-number model: the altar raises the ceiling, and meditation climbs to it.
  - It fits `ALTAR.md`'s "cultivation" framing.
  - A scribed per-pawn int already exists on the hediff, `maxLevelFromTitles`. Its only
    reader is `ApplyTitlePsylink`. [V] Reusing it is [I].
- **D3, XP buys points.** Meditation earns psycasts and stat upgrades, but never rank. It
  changes VPE's economy most.

**What it cannot do**
- Touch any non-XP writer. D needs C beside it.

**Consequences.** D2 and D3 put a design choice on #31: what cultivation earns.

#### E — rank chokepoint gate

**What it gets us**
- A single invariant: rank changes only inside an altar-scoped token, set and cleared within
  the altar's synced ritual outcome.
- Under VPE, every rank change after the first reaches `Hediff_PsycastAbilities.ChangeLevel(int)`
  [V]. That covers:
  - the rerouted vanilla `Hediff_Psylink.ChangeLevel`;
  - `ChangePsylinkLevel` on an existing psylink;
  - the XP loop;
  - `ApplyTitlePsylink`;
  - `PawnGen_Patch`;
  - VEF's `SetLevelTo`.
- The first rank is a separate seam: the psylink hediff's add (`Pawn_HealthTracker.AddHediff`
  for `PsychicAmplifier`, where VPE's `Hediff_Psylink.PostAdd` postfix already sits). [V
  seams; I composition]
- Without VPE, the equivalents are `Hediff_Psylink.ChangeLevel(int, bool)` and the same add.

**What it cannot do**
- **See direct field writes.** `Hediff_Psylink.CopyFrom` (duplication), Prepare Carefully's
  `AddPsylinkOrSetLevel`, VPE's `InitializeFromPsylink`, and `VPEPuppeteer.MindJump.TransferMind`
  (which moves both hediffs by `hediffs.Add`) all write the level without a call. [V]
- **Explain itself.** A refused write leaves the neuroformer consumed and the ritual's promised
  psylink missing, with no message. E is a backstop behind C, not a substitute for it.
- **Tell NPCs from colonists** unless it is scoped to the player's pawns. Otherwise it strips
  NPC casters at generation.

**Consequences.** The vanilla-looking seam is the wrong one (T-169).

#### I1 / I2 — imported rank

**I1** strips the generators in XML. Remove the `PawnGroupMaker_PsycasterRaid` entries VPE
patches into `TribeBase` and Empire factions, and the four tribal and five
Empire caster kinds. Remove VFE Empire's five `VFEE_Deserter_*` casters. Set `maxPsylinkLevel
0` on titles: the vanilla `PawnGenerator` gives noble NPCs `SetLevelTo(maxPsylinkLevel)` [V].
Do not run the Basilicus storyteller.

**I1 cannot reach `VRE_Archon` pawns.** Their xenotype carries `VRE_InnatePsylink`. Handle it
as in #162's F3 ruling, or remove the gene from the xenotype.

**I2** clamps on `Pawn.SetFaction(OfPlayer)`. Every player-side join funnels there (#142,
inherited [I]). I2 keeps enemy casters as enemies, but a captured caster loses its powers.
That is a story choice.

**Whether a recruited caster keeps rank is a requirement nobody owns.** See *Open questions*.

### Recommendation (not a selection)

- **D2 + C + I1, with E only if the build map wants one invariant.**
  - D2 is one prefix on the one funnel VPE ships. It keeps meditation meaningful as
    cultivation, and it gives #10 §4's altar-rank / cultivation-level split back on a model
    that can hold it.
  - C is nearly all XML, and its inert-neuroformer lever alone closes all seven supply rows.
  - E catches the uncatalogued, but it fails silently for the player, so it cannot be the
    only lock.
- **A** only if VPE's value does not survive D.
- **B** is not recommended as a lock. It misses three sources and is per-install. It is a
  fine playtest switch.

### Constraints

- **One number** (§ *Vanilla Psycasts Expanded*). There is no "psycaster level within a
  psylink rank" in VPE. A two-tier design must add the second number itself (D2).
- **T-169.** The vanilla psylink chokepoint is not one.
- **T-170.** Quest rewards inject neuroformers on a pity timer that no tag controls.
- **T-18.** VPE's `XPPerPercent` and `maxLevel` are settings. `maxLevel` also rewrites
  `PsychicAmplifier.maxSeverity` live.
- **T-113.** `duplicationAllowed` defaults true, so a duplicate keeps its psylink unless
  the hediff opts out.
- **XP ignores the psyfocus cap.** The postfix recomputes the gain rather than reading the
  clamped result, so a pawn at 100% psyfocus still earns XP while meditating. [V]

### Available mechanisms — the census

Every row is read from the 1.6 assembly the game loads, or from the def.
`Assembly-CSharp.dll` is 1.6.4871. All rows are [V] unless marked.

**Class R — raises the rank of a held pawn. Fifteen carriers: five vanilla, ten across six mods.**
One vanilla row, R5, is Anomaly's and outside the DLC floor ([#6](https://github.com/cjd721/Rimworld-Archinity/issues/6)).
R6 also stands for every psyfocus feeder, listed below the table; under VPE each is an XP
writer, closed only by B or D.

| # | Carrier | Anchor | Writes | Lever (route C) |
|---|---|---|---|---|
| R1 | Psylink neuroformer (Core, Royalty/Biotech-gated) | `CompUseEffect_InstallImplant.DoEffect`: `AddHediff`, or `ChangeLevel(1)` | both | inert item (XML) |
| R2 | Anima-tree linking | `CompPsylinkable.FinishLinkingRitual` → `ChangePsylinkLevel(1)` | both | remove the comp from `Plant_TreeAnima` (XML) |
| R3 | Blinding ritual (Ideology, needs Royalty) | `RitualOutcomeEffectWorker_Blinding.ApplyExtraOutcome` → `ChangePsylinkLevel(1)`, on the best outcome or at 50% | both | repoint `workerClass` (XML) |
| R4 | Bestowing ceremony | `RitualOutcomeEffectWorker_Bestowing.Apply`, a loop to `GetMaxPsylinkLevelByTitle` | both | `maxPsylinkLevel 0` (XML) |
| R5 | Anomaly duplication (Anomaly only; outside the DLC floor) | `Hediff_Psylink.CopyFrom` copies `level`; `GameComponent_PawnDuplicator` reads `duplicationAllowed` | both [I: VPE hediff side] | `duplicationAllowed false` (XML) |
| R6 | **VPE meditation XP — the core loop** | `Pawn_EntropyTracker_GainPsyfocus_Postfix` → `GainExperience(gain × 100 × XPPerPercent)`. One XP per 1% psyfocus; rank 2 costs 115 XP, and each later rank costs ×1.15 up to 20. Its callers are `JobDriver_Meditate` and `Caravan_NeedsTracker.TryGainPsyfocus`. The caravan call covers **every psylinked pawn in a caravan that is stopped and not night-resting, whether or not it meditates** | both | B or D |
| R7 | VPE `VPE_TimeskipMeditation` (Chronopath) | `Chronopath.Ability_Meditate.Cast` → `GainExperience(300)` | both | remove ability (XML) or D |
| R8 | VPE `VPE_DrainPsyessence` (**VPE's `VPE_Archon` path, not VRE–Archon**) | `Ability_DrainPsyessence.Cast`. It zeroes the victim's `experience` before reading it, so only the victim's whole levels transfer | both | remove ability (XML) or D |
| R9 | VPE bestowing floor | `RitualOutcomeEffectWorker_Bestowing_Apply_Patch.ApplyTitlePsylink`: with no VPE hediff, `ChangePsylinkLevel(pawn, 1)` whatever the title | both | C#, or no bestowing |
| R10 | VPE-Puppeteer `VPEP_Ascension` | `VPEPuppeteer.Ability_Ascension.Cast` → `GainExperience(Σ puppet skill XP / 100)` | both | remove ability (XML) or D |
| R11 | VPE-Puppeteer `VPEP_MindJump` | `MindJump.TransferMind` moves the psylink and VPE hediffs into the puppet's body. A new body holds the rank; the net rank is unchanged | both (moved) | remove ability (XML) |
| R12 | Vanilla Landmarks Expanded `VEE_Plant_TreeAnima_Ancient` | a second `CompProperties_Psylinkable` (focus `Natural`) | both | remove the comp (XML) |
| R13 | VFE Deserters `VFED_PsychicAmplifier` | `CompProperties_UseEffectInstallImplant`, `requiresExistingHediff`, so upgrade only | both | inert item or remove the def (XML) |
| R14 | VRE–Archon `VRE_InnatePsylink` | VEF `GeneExtension.hediffsToBodyParts` → `GeneUtils` `AddHediff(PsychicAmplifier)` + `VPE_PsycastAbilityImplant` (VRE–Archon's VPE patch). First rank only: a second add merges, and `Hediff_Level.TickInterval` resets severity to `level` | both | see *Genes*, below |
| R15 | EdB Prepare Carefully | `ManagerPawns.AddPsylinkOrSetLevel` writes `level` directly; `InjuryOption` admits any `Hediff_Level`. Start screen only | psylink; VPE copies it at `PostAdd` [I] | sourcing, or accept |

**Psyfocus feeders (R6).** VPE also patches `Pawn_PsychicEntropyTracker.OffsetPsyfocusDirectly`
(postfix, positive offsets) and `RechargePsyfocus` (prefix, XP for the missing fraction). Both
call `GainXpFromPsyfocus`, so under VPE **every psyfocus gain raises rank**. [V] Carriers at 1.6:
- vanilla: go-juice (`IngestionOutcomeDoer_OffsetPsyfocus`), the persona-weapon trait
  `WeaponTraitWorker_PsyfocusOnKill`, and the ritual attachable outcome
  `RitualAttachableOutcomeEffectWorker_PsyfocusRecharge`;
- VPE's own Harmonist `Ability_HeatFocus` and Chronopath `Ability_Meditate` (which then adds
  R7's 300 raw XP on top);
- VRE Sanguophage: deathrest buildings with `DeathrestExtension.psyfocusPercentPerHour`. This
  one touches the founders directly, since they deathrest;
- VPE Hemosage `Hediff_Bloodfocus`;
- VEF `HediffComp_PsyfocusRegeneration`, used by a VQE Ancients gene hediff;
- VFE Medieval 2 `CompUseEffect_IncreasePsypower` (draughts);
- Medieval Overhaul: four drugs with `IngestionOutcomeDoer_OffsetPsyfocus`;
- More Archotech Garbage `CompTargetEffect_CureHeatFillFocus`.

These are not counted among the fifteen. B and D close them all; C cannot close them one at a
time.

**Genes (R14).** The gene reaches pawns through several routes:
- **Archinity's own altar lottery offers it**: `GenePool_Archite.xml`, tier 5, category
  `Mind`. That is the altar, so it is sanctioned, but it gives a psylink through *genetic
  augmentation*, which `ALTAR.md` keeps distinct from psychic discipleship. See *Open
  questions*.
- The `VRE_Archon` xenotype (`inheritable true`).
- Random genepacks: the def leaves `canGenerateInGeneSet` at its default. The XML lever is
  `canGenerateInGeneSet false` (#162).
- More Archotech Garbage's archite spawner, which only C# closes (#162).

**Class I — imports rank.**

| # | Carrier | Anchor |
|---|---|---|
| I-a | Vanilla noble generation | `PawnGenerator`: `AddHediff(PsychicAmplifier)` then `SetLevelTo(royalTitleDef.maxPsylinkLevel)`. Includes VFE Empire's nine titles that carry `maxPsylinkLevel` |
| I-b | VPE psycaster kinds and raids | `PawnGen_Patch` on `PawnKindAbilityExtension_Psycasts`: four `Tribal_Caster_*` and five `Empire_Caster_*` kinds, injected by `PawnGroupMaker_PsycasterRaid` into `TribeBase` and Empire factions only (`1.6/Patches/PawnGroupMakers.xml`). So a Neolithic tribal raid can bring a capturable caster |
| I-c | VPE Basilicus storyteller | `PawnGen_Patch`: `baseSpawnChance` 10% of any humanlike, under `VPE_Basilicus` only |
| I-d | VEF kind extension | `VanillaExpandedFramework_PawnGenerator_GenerateNewPawnInternal_Patch`: `SetLevelTo(initialLevel)` on the implant. This is the base of I-b |
| I-e | VFE Empire deserter casters | `1.6/Patches/VPE.xml`: five `VFEE_Deserter_*` kinds carrying VPE's extension |
| I-f | `VRE_Archon` xenotype | R14's gene, native |

**Class S — supplies the neuroformer (writer R1).**

| # | Source | Anchor |
|---|---|---|
| S1 | **Quest pity timer** (T-170) | `Reward_Items.InitFromValue`: chance 0→1 over 45→60 days since `History.lastPsylinkAvailable`, for a non-Empire giver and a reward of at least 600 |
| S2 | Deserter intro quest | `Script_Intro_Deserter`, two in the stash |
| S3 | More Archotech Garbage | `MakeArchotechRoyalPsychicAmp` at `ArchBench` (`ArchoTechTierThree`), from `1.6/Compat/Royalty` |
| S4 | Worksites Expanded | `MiningOutpost.Orbital.Services.OrbitalBlackMarketStock`: a C# string list, 20% chance |
| S5 | VFE Deserters | a `ContrabandExtension` patched onto `PsychicAmplifier` (intel 3); `VFED_PsychicAmplifier` (intel 20) |
| S6 | Vanilla Base Generation Expanded | Empire settlement loot and `VGBE_CentralEmpire` layouts |
| S7 | Bestower betrayal | from #21 [I] |

Every vanilla trader reference is `StockGenerator_BuyTradeTag` (traders buy, never sell), and
so is VFE Medieval 2's. Mechanoids: Total Warfare only *consumes* one, in a recipe.

**Ruled out on a read.** Each of these references psylink but writes nothing:
- VRE–Archon's assembly: `ModCompatibility` checks `Psycasts() != null`.
- VPE Hemosage: entropy patches. (Its `Hediff_Bloodfocus` is an R6 psyfocus feeder.)
- VIE Memes: reads `GetPsylinkLevel`.
- VRE Sanguophage: reads `HasPsylink`. (Its deathrest psyfocus is an R6 feeder.)
- VEF: stage, graphics and contracts readers; its `GeneUtils` is R14's mechanism.
- VRE Android: a *blocking* prefix on `Hediff_Psylink.ChangeLevel(int)` for androids, which
  is T-169's example.
- Multiplayer: sync.
- Medieval Overhaul: its `ChangeLevel` hit is a need.

Vehicle Framework's `GainPsyfocus` and `Hediff_Psylink` hits are in its 1.4 and 1.5 assemblies
only.

**The wide pass.**
- **Roots and exclusions.** Both roots, with `-g '!**/obj/**'`. Mechanism hunts also used
  `-g '!**/Referenced/**'`. `python tools/corpus.py --check` matched the snapshot, 155 mods.
- **`.dll`, ASCII, `-i`:**
  - `ChangePsylinkLevel` → VPE only.
  - `Hediff_Psylink` → VPE, Puppeteer, VRE Android, Prepare Carefully, Vehicle Framework.
  - `GetMainPsylinkSource` → Puppeteer, Prepare Carefully.
  - `Hediff_PsycastAbilities` → VPE, Hemosage, Puppeteer, VRE–Archon.
  - `PsycastUtility` → the same, minus Hemosage.
  - `maxLevelFromTitles` → VPE.
  - `GainPsyfocus` → VPE, Vehicle Framework.
  - `PsychicAmplifier` → VPE, Prepare Carefully.
  - `psylink` → ten mods, all read.
  - `ChangeLevel|SetLevelTo|Hediff_Level` at 1.6 → Prepare Carefully, VRE Android, VEF, VPE,
    Medieval Overhaul.
- **`.dll`, null-interleaved UTF-16LE, typed literally, `-i`:**
  - `PsychicAmplifier` → VPE, Prepare Carefully, Worksites Expanded (S4's string list).
  - `Psylink` → VPE, Worksites, VEF.
  - `GainExperience` and `PsycastAbilit` → MP Compat only (its VPE sync class).
- **XML, both roots plus `Data/`:** `PsychicAmplifier`, `PawnKindAbilityExtension_Psycasts`,
  `VPE_PsycastAbilityImplant`, `CompProperties_Psylinkable`, the three ritual workers,
  `hediffLevelOffset`, `ChangeImplantLevel`, the three XP ability classes, `PsylinkNeuroformer`,
  `maxPsylinkLevel` and `VRE_InnatePsylink`. The rows above are the result. Every Local-root
  hit is a second copy of a workshop mod (T-22). Archinity's own mods write nothing; their one
  reference is `GenePool_Archite.xml`.
- **Added on review:** ASCII `.dll` `OffsetPsyfocusDirectly|RechargePsyfocus`, `-i`, both
  roots → at 1.6 VPE, Hemosage, VRE Sanguophage, VFE Medieval 2, VEF, More Archotech Garbage,
  each decompiled to its call site. XML sweep for the feeder classes → vanilla, Medieval
  Overhaul, VQE Ancients and the same mods. That is R6's feeder list.
- **Validated.** ASCII `ChangePsylinkLevel` returned VPE, where it is known to be. UTF-16
  `PsychicAmplifier` returned the Worksites literal that the ASCII pass cannot see.
- **Residual gap, stated.** A write of `level` or `experience` by reflection, from an assembly
  that references neither type by name, would pass every sweep. The UTF-16 pass for
  `PsycastAbilit` bounds it for VPE's type.

### Status

- **Evidence class: READ.** Settled by:
  - `Assembly-CSharp.dll` 1.6.4871, spot-checked against the loaded file with `ilspycmd -t`;
  - `2842502659/1.6/Assemblies/VanillaPsycastsExpanded.dll`;
  - the 1.6 assemblies of VPE-Puppeteer, VPE Hemosage, VRE–Archon, VRE Android, VEF, Prepare
    Carefully, VIE Memes, VRE Sanguophage, Worksites Expanded and Medieval Overhaul;
  - the defs named above.
- The mechanisms and census rows are [V]. Every route is [I] by construction.
- Established by [#163](https://github.com/cjd721/Rimworld-Archinity/issues/163). It builds
  on #162's VPE facts, which were re-read.
- **Corrects:**
  - **#21** "`PsychicAmplifier` … cannot roll as a generic quest reward". The tag is absent,
    and `Reward_Items` injects it anyway (S1, T-170).
  - **#10 §4 / §6** "levels within a rank come from cultivation" and "points come from psylink
    levels and from XP". XP raises the level, and the level is the rank: there is no
    within-rank level. Points come only from levels.
  - **#10 §6** "patching `MeditationFocusGain` moves XP". True, but it moves psyfocus by the
    same factor, because it is one input.
  - **The ticket's "VRE–Archon" suspect.** The drain is VPE's own `VPE_Archon` path. VRE–Archon
    writes rank only through XML (R14).

### Open questions

- **Requirement, [#31](https://github.com/cjd721/Rimworld-Archinity/issues/31):**
  - Does cultivation advance rank at all? This decides D1, D2 or D3. `ALTAR.md` says
    "willing-devotion rites and later campaign breakthroughs" and frames meditation as
    cultivation; #10 §4 says rank is the altar's.
  - Should `VRE_InnatePsylink` stay in the altar's genetic lottery? `ALTAR.md` keeps psychic
    progression distinct from genetic augmentation, and this gene is a psylink by gene.
- **Requirement, unowned:** does a captured or recruited caster keep its rank (I1/I2)? #31 is
  the nearest owner.
- **Build, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119):**
  - whether VPE, VPE-Puppeteer, Prepare Carefully, Worksites Expanded and More Archotech
    Garbage ship;
  - D's variant and where D2's ceiling lives (`maxLevelFromTitles` reuse is [I]);
  - E's token and its scope to player pawns;
  - the C# for R9;
  - the inert neuroformer's fiction;
  - a standing audit for new rank writers, the shape of #83's `tools/audit_bypasses.py`.
- **Unverified [I]:**
  - `VPE_PsycastAbilityImplant`'s duplication behaviour (R5, VPE side);
  - Prepare Carefully's edit of an existing psylink versus VPE's level (R15);
  - #21's bestower betrayal (S7).
