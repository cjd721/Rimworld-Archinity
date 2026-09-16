# Androids

## Purpose and scope

> **Authority correction — 2026-09-13.** “Android” is a body/person category;
> “Glitterite” is a civilization and origin. Other androids can be sincere believers and
> can be essentially ordinary people. Glitterites deliberately removed emotion, fervor
> and the faculties needed to connect to the channel; they run on anima-rich
> neutroamine, cannot receive psylinks and are not hackable. The VRE donor's
> unconditional psylink block is a carrier constraint, not permission to generalize the
> Glitterite condition to every android in the fiction.

> **Premise reopened — 2026-09-16.** The psylink block is **not** shown to be unconditional. A
> read on [#124](https://github.com/cjd721/Rimworld-Archinity/issues/124) found the `ChangeLevel(int)`
> prefix misses vanilla's main `ChangeLevel(int, bool)` path, and the first psylink is refused by a
> gene-gated settings list instead. §2, *Status*, *Verification* and decision 3 stand unrevised until
> [#141](https://github.com/cjd721/Rimworld-Archinity/issues/141) answers; do not cite them as settled.

This document owns **player-manufactured android bodies as a production capability** —
what an android is mechanically, what builds one, what gates it, and how the campaign's
final argument rests on it.

It implements `docs/requirements/GLITTERTECH.md`: *"Ultra also opens advanced android
manufacture. The campaign does not treat artificial bodies as inherently inferior; that
distinction is essential to the final cosmology."* The ending's argument in
`docs/COSMOLOGY.md` — the Glitterites fail *"not because android bodies are invalid"* —
is only legible if the player can build androids and suffer no penalty for it. That makes
this document load-bearing on the ending, not on a side system.

**Where adjacent systems take over.** The Analysis research gate itself is
`docs/specs/RESEARCH.md`'s; the spendable Intel balance is `docs/specs/CURRENCIES.md`'s;
whether an android can hold Devotion is a consequence stated here and owned by
`docs/specs/RELIGION.md`. Player-made androids may hold an ideology and be sincere
believers. Glitterites are explicitly excluded from hacking; there is no missing
android-hacking capability to build.

Established by [#78](https://github.com/cjd721/Rimworld-Archinity/issues/78). Evidence
class **READ**.

---

## The build

**We ship VRE – Android and gate its research project behind an Analysis exemplar. The
manufacture capability already exists, end to end, and is already multiplayer-safe.**

The ticket's framing asked whether VRE – Android offers player-side manufacture at all,
"as opposed to an NPC xenotype", and recorded that this was unknown anywhere in the repo.
It does, and it is not close: the mod ships a four-building production line, a dedicated
`WorkGiver`/`JobDriver` pair, an unfinished-work item, and a customisation window, all
gated on one research project whose `techLevel` is **`Ultra`** — the era the requirement
names. **[V]**

### 1. The mechanism — a `Building` with a job, not a `RecipeDef`

`VREAndroids.Building_AndroidCreationStation` (`ThingDef` `VREA_AndroidCreationStation`)
is a plain `Building` subclass. It is **not** a `Building_WorkTable` and carries no
`RecipeDef`; the bill-and-recipe machinery is bypassed entirely.

The chain, as read from the 1.6 assembly **[V]**:

| Step | Carrier |
|---|---|
| Player picks a gene loadout | `VREAndroids.Window_AndroidCreation` (extends `Window_CreateAndroidBase`), opened from the station's `GetFloatMenuOptions` / `GetGizmos` |
| Order is committed | `Window_AndroidCreation.AcceptInner()` writes `curAndroidProject`, `totalWorkAmount`, `currentWorkAmountDone`, `requiredItems` onto the station |
| Colonist is dispatched | `WorkGiverDef VREA_CreateAndroid` (`1.6/Defs/WorkGiverDefs/WorkGivers.xml`) — `giverClass VREAndroids.WorkGiver_CreateAndroid`, **`workType Crafting`**, `priorityInType 100`, requires `Manipulation` — → `VREAndroids.JobDriver_CreateAndroid` (`JobDef VREA_CreateAndroid`). **This def is what makes the chain ordinary player work rather than a debug path** |
| Ingredients hauled, work item spawned | `Building_AndroidCreationStation.CreateUnfinishedAndroid(List<Thing>)` → spawns `VREA_UnfinishedAndroid` (`VREAndroids.UnfinishedAndroid`) |
| Work ticks | `Building_AndroidCreationStation.DoWork(Pawn, int, out bool)`, scaled by the crafter's `WorkSpeedGlobal`, from the job's `Toil.tickIntervalAction` |
| Pawn is created | `Building_AndroidCreationStation.FinishAndroidProject()` |

`FinishAndroidProject` calls
`PawnGenerator.GeneratePawn(new PawnGenerationRequest(VREA_DefOf.VREA_AndroidBasic, Faction.OfPlayer, …))`,
then clears worn apparel, equipment and inventory, zeroes `AgeBiologicalTicks` and
`AgeChronologicalTicks`, adds `VREA_NeutroLoss` at severity 1, sets `genes.xenotypeName`
and `genes.iconDef` from the project, strips every gene in `Utils.allAndroidGenes`, adds
the project's chosen genes, and `GenSpawn.Spawn`s the pawn at the station. **[V]**

**The product is a colonist.** `Faction.OfPlayer` is passed to the generation request, so
the android joins on spawn — no recruitment, no join quest.

### 2. What an android *is*, mechanically — a xenotype on race `Human`

This is the question that decides Devotion, psycasts and colonist status, and the answer
is unambiguous in the defs. **[V]**

`PawnKindDef VREA_AndroidBasic` declares `<race>Human</race>` and a `xenotypeSet` forcing
`XenotypeDef VREA_AndroidBasic` at weight 999 with `useFactionXenotypes false`. There is
no custom `ThingDef` race, no `Building`-as-pawn, nothing mechanoid-adjacent. An android is
an ordinary humanlike pawn wearing a xenotype whose genes disable most needs.

`XenotypeDef VREA_AndroidBasic` (via abstract `VREA_AndroidXenotypeBase`) carries 21 genes,
including `VREA_SyntheticBody`, `VREA_NeutroCirculation`, `VREA_JoyDisabled`,
`VREA_MentalBreaksDisabled`, `VREA_NoSkillGain`, `VREA_PsychologyDisabled` and
`VREA_PsychicallyDeaf`. `VREA_AndroidAwakened` (via `VREA_AndroidXenotypeAwakenedBase`)
carries only 10 — the awakening restores joy, comfort, mental breaks and skill gain.

**The three consequences the ticket asked for, each with its cost:**

| Option | Consequence |
|---|---|
| **Xenotype on `Human`** *(what ships)* | Counts as a colonist everywhere vanilla counts colonists. Holds an `Ideo`, so **Devotion works with no new code**. Cannot take psycasts. Awakening is a shipped, authored transition. |
| PawnKind / faction-member only | Would make androids NPC-only and delete the capability the requirement asks for. Rejected. |
| Mechanoid-adjacent (`Building_MechGestator` path) | Produces a **mechanitor-bonded mech**, not a colonist — no `Ideo`, no Devotion, no backstory, no social tab. Wrong shape for a campaign about personhood. |

**Recommend the shipped shape — xenotype on `Human`.** It is the only one of the three
that lets the campaign make its argument, because the argument is precisely that an
android is a person; a mechanoid-adjacent android would concede the Glitterite position in
the mechanics while the text denied it.

**Psycasts: androids cannot hold a psylink.** `VREAndroids.Hediff_Psylink_ChangeLevel_Patch`
prefixes `RimWorld.Hediff_Psylink.ChangeLevel(int)` at `HarmonyPriority(int.MaxValue)` and
returns `false` when `pawn.IsAndroid()`.

**The prefix is the whole block, and it is unconditional.** `VREA_PsychicallyDeaf` appears on
both the basic and awakened xenotype bases, but it is a *selectable* `VREAndroids.AndroidGeneDef`
with `biostatCpx 1` — a player can deselect it when designing an android, and doing so changes
nothing, because the prefix does not consult genes. **[V]** That strengthens the hand-back rather
than weakening it: there is no loadout, no awakening and no XML edit that buys an android a
psylink. It is a **campaign consequence, not a bug** — see *Outstanding decisions*.

**Devotion: no blocker found.** The 1.6 assembly contains **no `Ritual*` metadata string at
all**, so VRE – Android patches no ritual participation path; androids are humanlike pawns
with an `Ideo` and participate as any colonist does. The mod ships one Ideology precept
(`Precepts_Androids.xml`) governing how *other* colonists regard androids, plus
`FleshPurity` / `Transhumanist` patches — none of which gate the android's own `Ideo`.
The negative sweep is **[V]**; the conclusion that Devotion therefore works is **[I]** until
a rite is run with an android in a role.

### 3. The persona subcore — and the real price of an android

The fictional component the ticket names, `VREA_PersonaSubcore`, exists as a `ThingDef`
(`ParentName SubcoreBase`, `MarketValue 2000`) and is **required for every android**. It is
produced by `VREA_SubcorePolyanalyzer` (`VREAndroids.Building_SubcorePolyanalyzer`, extends
`Building_Enterable`). **[V]**

That building drives itself entirely from **vanilla Biotech's subcore-scanner def surface**
— `subcoreScannerOutputDef`, `subcoreScannerTicks`, `subcoreScannerFixedIngredients`,
`subcoreScannerHediff`, `subcoreScannerStartEffect/Working/Complete`, all fields under
`<building>` that vanilla itself uses in
`Data/Biotech/Defs/ThingDefs_Buildings/Buildings_Production.xml`. **These are XML, and they
are ours to patch.** **[V]**

As shipped: output `VREA_PersonaSubcore`, `subcoreScannerTicks` 3750, fixed ingredients
10 Plasteel + 1 ComponentSpacer, hediff `VREA_ScanningSickness`.

**Four different colonists must be scanned in sequence to yield one subcore.**
`Building_SubcorePolyanalyzer.scanProgress` computes
`(1 - fabricationTicksLeft / subcoreScannerTicks) / 4f + 0.25f * scannedPawns.Count`, and
`scannedPawns` is scribed by reference. **[V]** The true price of a manufactured android is
therefore *four colonists' time*, not a materials cost — which is exactly the right shape
for a campaign that is about what a person is worth.

### 4. What changes it, and where the player sees it

**Change.** Three player-driven writes, all already synchronised (see below):
`Window_AndroidCreation.AcceptInner` (commits the order), `JobDriver_CreateAndroid`'s work
toil (advances and completes it), `UnfinishedAndroid.CancelProject` (abandons it).

**Display.** Entirely shipped and entirely vanilla-shaped: the station's float-menu entry
`VREA.CreateAndroid`; the gene-selection window with its biostat table
(`AndroidStatsTable.Draw`, which renders `requiredItems` as the cost row); a progress bar
on the work toil via `ToilEffects.WithProgressBar`; `UnfinishedAndroid.GetInspectString`
reporting work left; the subcore polyanalyzer's own four-segment progress bars. **There is
no display half to build.** **[V]**

### 5. The Intel gate

Manufacture must hang off the exemplar loop rather than be a research project the player
simply reaches. Two layers were surveyed; **the first ships and the second is struck.**

**Layer 1 — the research gate. Pure XML, and it is [#67](https://github.com/cjd721/Rimworld-Archinity/issues/67)'s shipped mechanism.**
`VREA_AndroidTech` is a `ResearchProjectDef` like any other, so
`PatchOperationAdd` of a `<requiredAnalyzed>` list naming a Glitterite exemplar gates it
exactly as the Glittertech branch roots are already gated. #67 established that
`requiredAnalyzed` + `CompProperties_CompAnalyzableUnlockResearch` is base `Assembly-CSharp`,
costs zero C#, and that `destroyedOnAnalyzed: false` lets the player keep the trophy. No new
mechanism is needed **for the gate itself**.

> **The gate is not airtight on its own, and for this project the leak is live — see T-92.**
> `VREA_AndroidTech` declares `<tab>VanillaExpanded</tab>`, sets `generalRules` nowhere, and
> VRE – Android **hard-depends on VEF**. `VEF.Research.ResearchProjectUtility.AutoAssignRules`
> then satisfies both remaining def-side conditions itself: it assigns `generalRules` to **every**
> non-Anomaly project in the database that lacks one, and adds the `VanillaExpanded` tab to
> vanilla `Schematic`'s doer. **[V]** So the `Schematic` book can pick this project, and that path
> never tests `CanStartNow`.
>
> **The one condition that still binds is `PrerequisitesCompleted`:** the bypass opens once
> `HighMechtech` is done, not from the start of a save. That is still a gate bypass, because the
> Analysis exemplar and the research prerequisite are independent locks.
>
> **This gate holds only if RESEARCH.md's `usesHiddenProjects` one-liner and the relevant Class-A
> shutoffs ship with it** — [#83](https://github.com/cjd721/Rimworld-Archinity/issues/83) owns that
> remedy, so it costs us nothing extra. A dependency, not a defect in the patch above.
>
> **Of RESEARCH.md's three Class-A bypasses, only two can reach this project, and on different
> terms — not "the same terms".**
>
> | Bypass | Reaches `VREA_AndroidTech`? |
> |---|---|
> | MTW `NCL.CompUnlockResearch.UnlockResearch` | **No.** It `FinishProject`s one *named* project, `NCL_CerebrexCore_Rebuild`, and its own prerequisite chain. `VREA_AndroidTech` is neither, and sits in no chain MTW names. |
> | VPE `Ability_ReverseEngineer.Cast` | **Yes, conditionally.** It writes `progress[proj] = proj.baseCost` for every project that is a `researchPrerequisite` of the *targeted* thing. It reaches this project only if the player targets one of the four android buildings — which requires already owning one. |
> | RimPacts `WorldComponent_RimPacts.ResolveSpyOpSuccess` | **Yes, conditionally.** It draws a **random unfinished project at the target faction's tech level**. `VREA_AndroidTech` is `Ultra`, so only a spy op against an Ultra-tech faction can select it. |

**A second route past the gate, worth knowing about.** VRE – Android ships
`1.6/Defs/Scenarios/Scenarios_Androids.xml`, whose Android Utopia scenario carries a
`ScenPart_StartingResearch` granting `VREA_AndroidTech` outright. **[V]** Harmless to us — we do
not use that scenario — but a reader comparing the gate against the mod's own content should know
it exists.

> **Caveat carried from #67, re-read rather than inherited:** `requiredAnalyzed` is switched
> off without **Biotech**. VRE – Android hard-depends on Biotech in its `About.xml`
> `modDependencies`, so the gate cannot silently evaporate while the capability exists —
> the two stand or fall together. **T-40** applies to the general case, not to this one.

**Layer 2 — a per-unit Intel debit. Struck.** An earlier draft priced each android through
`WorldComponent_Currencies.TrySpend` — a Harmony prefix on `Window_AndroidCreation.AcceptInner`
refusing the order when the balance is short, plus the debit. **That is withdrawn.**
[`CURRENCIES.md`](CURRENCIES.md) § *What changes it* names exactly two Intel debit sites — the
Intel exchange and #106's quest catalogue — and a per-android debit would be a third. If
manufacture should cost Intel at all, the shape is a one-time **exchange for an Instruction
item**: a `CurrencyPurchaseDef` at [`CURRENCIES.md`](CURRENCIES.md) § *The Intel exchange*
delivering a techprint for `VREA_AndroidTech` (which must then declare `techprintCount`), priced by
[#117](https://github.com/cjd721/Rimworld-Archinity/issues/117). `subcoreScannerFixedIngredients`
cannot carry Intel either way: it takes a `ThingFilter` and consumes only a physical `Thing`.
**If any per-android price is ever expressed as an ingredient, it must be appended in a postfix on
`OnGenesChanged` — T-93.**

**Recommendation: ship Layer 1 only.** It costs nothing, it is the mechanism the rest of the
Glittertech tree already uses, and it puts manufacture behind the exemplar loop as the ticket
requires.

### 6. Scoping the bleed

VRE – Android's `1.6/Patches/FactionPatches.xml` adds
`<VREA_AndroidAwakened>0.02</VREA_AndroidAwakened>` to the `xenotypeChances` of
`FactionDef[@Name="OutlanderFactionBase"]` and `FactionDef[@Name="PirateBandBase"]`, and —
under `PatchOperationFindMod` Royalty — to `FactionDef[defName="Empire"]`. **[V]**

**Two corrections to the ticket's framing, both verified.**

1. The ticket says the mod *"patches the **abstract** outlander and pirate bases."*
   `OutlanderFactionBase` is indeed `Abstract="True"`. **`PirateBandBase` is not abstract** —
   it is declared `<FactionDef Name="PirateBandBase" ParentName="FactionBase">` with
   `<defName>Pirate</defName>` in `Core/Defs/FactionDefs/Factions_Misc.xml`. It is the
   concrete vanilla `Pirate` faction that *additionally* serves as a `ParentName`. The bleed
   conclusion is unchanged — both propagate to children, and by **T-02** patches run before
   inheritance resolves, so every child inherits the added chance — but one of the two targets
   is a live faction, not a template.

2. **The bleed does not reach factions we authored.** Archinity's own `FactionDef`s —
   `Archinity_Glitterites` (`Archinity.Glitterites/Defs/FactionDefs/Factions_Glitterites.xml`)
   and `Archinity_FreeCompanies` (`Archinity.Drifters/Defs/FactionDefs/Factions_FreeCompanies.xml`)
   — both declare `ParentName="FactionBase"`, not `OutlanderFactionBase` or `PirateBandBase`.
   **[V]** The ticket's requirement that *"the abstract-base patches must not reach factions we
   authored"* is **already satisfied by our own inheritance choices**, and needs no patch.

What the bleed *does* reach is vanilla's outlander and pirate children (Core, Ideology and
Biotech all declare some) and other mods' factions — 20 `ParentName` declarations across 12
files in both corpus roots plus vanilla. The remaining question is therefore **fictional, not
structural**: should awakened androids appear at 2% in ordinary outlander and pirate
populations from game start, in a campaign that introduces androids at Ultra?

**If the answer is no, the scoping patch is two operations and no C#:**

```xml
<!-- expect: 1 -->
<Operation Class="PatchOperationRemove">
  <xpath>/Defs/FactionDef[@Name="OutlanderFactionBase"]/xenotypeSet/xenotypeChances/VREA_AndroidAwakened</xpath>
</Operation>
<!-- expect: 1 -->
<Operation Class="PatchOperationRemove">
  <xpath>/Defs/FactionDef[@Name="PirateBandBase"]/xenotypeSet/xenotypeChances/VREA_AndroidAwakened</xpath>
</Operation>
```

It must load **after** VRE – Android, which Archinity's mods already do. The annotations
above are written as expectations to be checked by `tools/patch_check.py`, not copied from it.

**Cost of the bleed if left alone: zero to us, and a fiction leak.** It cannot break T-07 —
it adds a xenotype chance to an existing faction, not a faction to the roster.

### Cost

| Piece | XML / patch / C# | Estimate | Lands in |
|---|---|---|---|
| The whole manufacture capability | **none — shipped** | 0 | VRE – Android (`2975771801`) |
| Multiplayer safety | **none — shipped** | 0 | Multiplayer Compatibility (`1629973374`) |
| Analysis gate on `VREA_AndroidTech` | XML patch | ~6 lines | `Archinity.Glitterites/Patches/Analysis_GlittertechGate.xml` (exists per #67) |
| Bleed scoping *(optional, fiction call)* | XML patch | ~10 lines | `Archinity.Glitterites/Patches/VREAndroid_Scope.xml` (new) |
| ~~Per-unit Intel debit~~ *(struck — Intel is exchanged for Instruction items, see §5)* | — | 0 | — |

**Total for the recommended build: ~6 lines of XML.** The capability itself is a sourcing
decision, not an implementation one — it belongs to
[#14](https://github.com/cjd721/Rimworld-Archinity/issues/14).

The mechanisms above are **[V]**. The claim that they compose into the campaign's Ultra
android capability is **[I]** until built.

---

## Persistence and multiplayer

**Persistence is complete and needs nothing from us. [V]**

`Building_AndroidCreationStation.ExposeData` scribes `unfinishedAndroid`
(`Scribe_References`), `curAndroidProject` (`Scribe_Deep`, a `CustomXenotype`),
`currentWorkAmountDone` and `totalWorkAmount` (`Scribe_Values`), and `requiredItems`
(`Scribe_Collections`, `LookMode.Deep`). `UnfinishedAndroid.ExposeData` scribes `workLeft`,
its `resources` list and a `station` back-reference.
`Building_SubcorePolyanalyzer.ExposeData` scribes `scannedPawns` by reference.

A save predating the mod gains the buildings as ordinary new `ThingDef`s; there is no world
component and no global state, so nothing has to migrate.

> **`requiredItems` is scribed `LookMode.Deep` on the station while
> `UnfinishedAndroid.resources` is scribed under the key `"requiredItems"` as well** — two
> different collections of two different types sharing a scribe key across two different
> classes. They do not collide (different `IExposable`s), but it is a readability trap for
> anyone debugging a save.

**Multiplayer is covered, and my first reading of this was wrong.**

The shape looked like a textbook desync: `Window_AndroidCreation.AcceptInner()` writes four
**scribed** fields on the station directly from a `Window`, with no `SyncMethod` of its own —
the same shape as **T-61** and **T-85**. It is not one, because
**Multiplayer Compatibility carries a dedicated compat class for this mod.** **[V]**

`Multiplayer.Compat.VanillaRacesAndroid`, attributed
`[MpCompatFor("vanillaracesexpanded.android")]`, in the assembly the game actually loads
(`1629973374/1.6/Assemblies/Multiplayer_Compat.dll` — **not** the `Referenced/` stub):

- `MP.RegisterSyncMethod(Window_AndroidCreation, "AcceptInner").SetPreInvoke(PreAcceptInnerCreation)`
  — the order commit is synced; the pre-invoke nulls a `creator` that died or despawned.
- `MP.RegisterSyncWorker<GeneCreationDialogBase>(SyncAndroidCreationWindow, Window_AndroidCreation)`
  — the window is reconstructed on the remote client from `station` + `creator` via
  `Activator.CreateInstance`, with the gene selection and `requiredItems` written across the wire.
- `MP.RegisterSyncMethod(Building_AndroidCreationStation, "FinishAndroidProject").SetDebugOnly()`
  — **debug-only**, which is the confirmation that the production path is not a UI call.
- `MP.RegisterSyncMethod(UnfinishedAndroid:CancelProject)`.
- Lambda registrations for the station's, the polyanalyzer's and the behaviorist station's
  gizmos and float menus; `RegisterSyncField` on `Gene_SyntheticBody:autoRepair`;
  `RegisterDefaultLetterChoice` for `ChoiceLetter_AndroidAwakened`.
- A `ClearCache` postfix on `GameComponentUtility.FinalizeInit` that empties two **static,
  unkeyed client-local caches** — `VREAndroids.SocialInteractionUtility_CanInitiateRandomInteraction_Patch:cachedResults`
  (namespaced) and `MentalBreaker_CanDoRandomMentalBreaks_Patch:cachedResults` (bare, as the
  `AccessTools` string is actually written). That is the **T-20** shape, already neutralised by a
  third party.

**The `Rand` question passes the Divergence gate on its own merits.** `FinishAndroidProject`
calls `PawnGenerator.GeneratePawn`, which draws heavily on the shared `Rand` stream — but it is
reached from `Toil.tickIntervalAction` inside `JobDriver_CreateAndroid`, an already-synced job
tick that both clients execute identically. Per `CODING_STANDARDS.md` § *The two gates*, `Rand`
reached from a synced tick is deterministic by construction. **[V]**

**The carrier verdict therefore names two mods:** `vanillaracesexpanded.android` for the
capability and `rwmt.multiplayercompatibility` for its multiplayer safety. The second is not
optional — without it, `AcceptInner` is an unsynced write to scribed state and the capability
desyncs a co-op session on first use.

**`AndroidSettings` is not a settings-sync hazard.** `VREAndroids.AndroidSettings` is a
`Verse.Def` — seven `List<string>` fields read from XML — not a `ModSettings`. **T-18 does not
apply.** **[V]**

---

## Failure and recovery

| Failure | Detection | Recovery |
|---|---|---|
| Station destroyed mid-project | MP Compat patches `Window_CreateAndroidBase:DoWindowContents` with `CloseDialogIfStationDestroyed` | Window closes; `UnfinishedAndroid` holds the hauled resources and is recoverable |
| Project abandoned | Player gizmo | `UnfinishedAndroid.CancelProject`, synced |
| `VREA_UnfinishedAndroid` left outdoors | `DeteriorationRate 2` — it rots | Materials lost; no campaign state touched |
| Analysis gate never satisfied | Vanilla research UI shows the study requirement and the locked reason | The gate is the design; there is no softlock, because the exemplar is a Glitterite drop the campaign already supplies |
| **Analysis gate bypassed — player reaches Ultra androids early** | **Nothing reports it — T-92** | **Not recoverable after the fact, and not fixable here.** Ship RESEARCH.md's `usesHiddenProjects` one-liner alongside this capability, plus the VPE and RimPacts shutoffs (**not** MTW's — it cannot reach this project) — [#83](https://github.com/cjd721/Rimworld-Archinity/issues/83) |
| Android awakens | `ChoiceLetter_AndroidAwakened`, synced by MP Compat | Authored transition, not a fault |

**No campaign softlock exists here.** Manufacture is a capability, not a plot beat: the
campaign's ending argues *that the player could* build androids without penalty, and a player
who never builds one has still been shown the option. The one thing that would break the
argument is a **penalty** applied to android colonists — see *Outstanding decisions*.

---

## Status

- **Verified available mechanism** — player-side android manufacture, complete, in
  VRE – Android's 1.6 assembly and defs. Read end to end. **[V]**
- **Verified available mechanism** — multiplayer safety for that capability, in Multiplayer
  Compatibility's loaded 1.6 assembly. **[V]**
- **Verified** — androids are a Biotech xenotype on race `Human`; they are colonists, they
  hold an `Ideo`, and they cannot hold a psylink. **[V]**
- **Proposed** — the Analysis gate on `VREA_AndroidTech`. The mechanism is #67's and is
  **[V]**; its application here is **[I]**.
- **Proposed, and a fiction call** — scoping the outlander/pirate xenotype bleed.
- **Struck** — the per-unit Intel debit (§5; [`CURRENCIES.md`](CURRENCIES.md) § *What changes it*).

Evidence class **READ**: settled by the 1.6 defs of `2975771801`, its decompiled
`1.6/Assemblies/VREAndroids.dll`, the decompiled
`1629973374/1.6/Assemblies/Multiplayer_Compat.dll`, vanilla `Assembly-CSharp` and vanilla
Biotech defs, plus a two-root two-encoding wide pass validated against known positives.
Nothing here needed the game launched.

Established by [#78](https://github.com/cjd721/Rimworld-Archinity/issues/78).

---

## Available mechanisms

### VRE – Android (`vanillaracesexpanded.android`, `2975771801`) — the carrier

Ships `1.4`, `1.5`, `1.6`. **Loaded assembly: `1.6/Assemblies/VREAndroids.dll`.**
**Source is 1.4-only** — 293 `.cs` files under `1.4/Source/`, and no `Source` directory under
`1.5/` or `1.6/`. Everything above was decompiled from the 1.6 assembly; the shipped source
describes a different game version. Hard-depends on Harmony, Vanilla Expanded Framework and
**Biotech**.

The production line, all four buildings gated on the single `ResearchProjectDef`
`VREA_AndroidTech` (`techLevel Ultra`, `baseCost 2000`, prerequisite `HighMechtech`,
`requiredResearchBuilding HiTechResearchBench`, `requiredResearchFacilities MultiAnalyzer`):

| Building | Class | Cost | Role |
|---|---|---|---|
| `VREA_SubcorePolyanalyzer` | `Building_SubcorePolyanalyzer` | 200 Steel, 150 Plasteel, 3 ComponentSpacer | Scans four colonists → one `VREA_PersonaSubcore` |
| `VREA_AndroidCreationStation` | `Building_AndroidCreationStation` | 360 Steel, 6 ComponentIndustrial, 6 ComponentSpacer | Builds the android |
| `VREA_AndroidBehavioristStation` | `Building_AndroidBehavioristStation` | 160 Steel, 4 ComponentIndustrial, 4 ComponentSpacer, 20 Gold | Reprograms subroutines and skills afterwards |
| `VREA_AndroidPartWorkbench` | `Building_WorkTable` | 220 Steel, 8 ComponentIndustrial | Replacement parts (this one *is* recipe-driven) |

**The ingredient list is hardcoded in C#, and this is the one real constraint on us.**
`Window_AndroidCreation.OnGenesChanged()` assigns
`requiredItems = { VREA_PersonaSubcore ×1, Plasteel ×125, Uranium ×30, ComponentSpacer ×7 }`
as a literal `List<ThingDefCount>`. **[V]** There is no def, no `RecipeDef` and no mod
extension behind it — **the per-android material cost cannot be changed by XML.** Changing it
means a Harmony postfix on `OnGenesChanged` **and nowhere else: the list is rebuilt on every
gene toggle, so a write at any other seam is silently discarded — T-93.** Work scales instead, and separately:
`totalWorkAmount = selectedGenes.Sum(x => x.biostatCpx * 2000)`. **[V]**

`VREA_AndroidBehavioristStation`'s `WorkGiver_ModifyAndroid` is workType **Research**, not
Crafting — easy to miss when staffing.

### Vanilla — the `RecipeDef` route exists, and the ticket's premise is half wrong

**The ticket states that *"a `RecipeDef` producing a pawn is not something vanilla supports
without C#"*. That is refuted, with heavy caveats — and the caveats are why we still do not
use it.** **[V]**

A `RecipeDef`'s `products` are `List<ThingDefCountClass>`, which has no `PawnKindDef` field —
but a **pawn race `ThingDef` is a perfectly ordinary `ThingDef`**, and vanilla's mech recipes
name one directly (`<products><Mech_Militor>1</Mech_Militor></products>`). The routing is pure
XML: `RimWorld.BillUtility.MakeNewBill` returns a `Bill_ProductionMech` whenever
`recipe.gestationCycles > 0`, and `Verse.AI.Toils_Recipe.FinishRecipeAndStartStoringProduct`
branches on `curJob.bill is Bill_Mech` to call `GenRecipe.FinalizeGestatedPawns` instead of
`GenRecipe.MakeRecipeProducts`. So **XML alone can make a bill yield a pawn.**

**What it costs is the entire Biotech mech-gestator contract, and every clause of it is wrong
for an android:**

- The building's `thingClass` must be `Building_MechGestator` — `Bill_Mech.Gestator` is an
  **unguarded cast** to it.
- `mechanitorOnlyRecipe` must be `true`, or `Bill_Mech.PawnAllowedToStartAnew` NREs on
  `p.mechanitor`. **Only a mechanitor can ever run the bill**, and it consumes mech bandwidth.
- `RimWorld.Bill_ProductionMech.CreateProducts` resolves the pawnkind by **reverse lookup** —
  `DefDatabase<PawnKindDef>.AllDefs.Where(pk => pk.race == recipe.ProducedThingDef).First()`.
  There is **no field naming the resulting pawnkind.**
- It hard-wires `PawnRelationDefOf.Overseer` from the worker to the product, and
  `DevelopmentalStage.Newborn`.
- `Notify_FormingCompleted` calls `WasteProducer.ProduceWaste(...)` and `Tick` dereferences
  `Power`, both without null guards — so `CompWasteProducer` and `CompPowerTrader` are mandatory.

An android built this way would be a **mechanitor-bonded mech with an Overseer**, which is
precisely the personhood claim the campaign exists to deny. **VRE – Android's choice to bypass
the recipe system is the right one, and we inherit it.** The correct statement of the ticket's
premise is: *a `RecipeDef` producing a pawn that is a **colonist** is not something vanilla
supports without C#.*

Vanilla ships exactly one bill-to-pawn path, and it is that one. No `RecipeWorker` subclass in
the vanilla assembly creates a pawn; `Recipe_ExtractOvum` and `Recipe_ImplantEmbryo` produce an
item and a pregnancy respectively, and `Recipe_GhoulInfusion` transforms a pawn that already
exists. **[V]**

**The near donor is Biotech's subcore scanner, and VRE – Android already uses it.** The
`subcoreScanner*` fields on `BuildingProperties` are vanilla, shipped, and used by vanilla's
own `SubcoreSoftscanner` / `SubcoreRipscanner`. **[V]** `VREA_SubcorePolyanalyzer` is that
mechanism with exactly one piece replaced — the output def — which is the shape
`docs/agents/capability-research.md` predicts. `RimWorld.Building_SubcoreScanner` carries
**no `RecipeDef` and no `Bill`**, drives itself entirely from `def.building.*`, and makes its
product on `Tick` via `ThingMaker.MakeThing(def.building.subcoreScannerOutputDef)`. **[V]**

Biotech's **growth vats** are not a donor. `RimWorld.Building_GrowthVat` has no `<recipes>`,
no `ITab_Bills` and no `RecipeDef`; it either accelerates a pawn already inside it
(`AgeTicksPerTickInGrowthVat = 20`, ejecting at 18 years) or gestates an existing
`HumanEmbryo` into a **baby** via `PregnancyUtility.ApplyBirthOutcome`. It never creates a
pawn from materials and never yields an adult. **[V]**

**This section is moot for the build**, because question 1 resolved yes. It is recorded
because the ticket asked, and because the subcore-scanner def surface is the one XML lever we
have over this capability.

### Multiplayer Compatibility (`rwmt.multiplayercompatibility`, `1629973374`)

`Multiplayer.Compat.VanillaRacesAndroid` in `1.6/Assemblies/Multiplayer_Compat.dll`. Covered
above. Required alongside the capability.

### What does not exist in the corpus

A validated wide pass over both roots found **no second carrier** for player-side pawn
manufacture. `AndroidCrafter`, `Building_AndroidCreator` and `Recipe_MakePawn` return zero in
every assembly in either root **in both encodings** — plain ASCII and literal-escape UTF-16.

**`CompAndroid` is not a zero, and saying it was would have been the exact error this
document's own method finding describes.** It returns **ASCII 0, UTF-16 8** — all eight in
`Multiplayer_Compat.dll`, versions 1.3 through 1.6, mirrored across both roots. The string is
`MOARANDROIDS.CompAndroidState`, a type-name literal belonging to **Android Tiers**, which is
**not on disk**. So it is an artifact of a compat layer for an absent mod, and it is filed with
the Android Tiers references below rather than counted as a carrier. **The conclusion is
unchanged; the evidence for it was wrong and is corrected here.** **[V]**

**Android Tiers / ATReforged, Chj Android, Misc. Robots and Robotic Surrogates are not on
disk** — Android Tiers appears only as *type-name and packageId literals inside* Multiplayer
Compat's and MedPod's compat layers, which are references to a mod we do not have.

The mech-gestator mods on disk — **Alpha Mechs** (`sarg.alphamechs`, `2973169158`) and
**Mechanoids: Total Warfare** (`nyar.nclvstw`, `3555799437`) — both extend vanilla's
`MechGestator` with `RecipeDef`s. They produce **mechanitor-bonded mechs, not colonists**, and
are the wrong shape for this requirement. They are recorded as a real but rejected alternative.

---

## Verification

**Settled by reading** — the manufacture chain, the xenotype shape, the psylink block, the
persistence, the MP Compat coverage, the hardcoded ingredient list, the faction-patch bleed and
our own factions' immunity to it. Paths and anchors are cited above.

**Observable checks that would demonstrate the requirement is satisfied**, if someone wants
them in-game rather than on paper:

1. With the Analysis patch in, `VREA_AndroidTech` shows a **"Study requirements"** block and
   cannot be started until the Glitterite exemplar is analysed. (Vanilla UI, per #67.)
2. After research, a `VREA_AndroidCreationStation` offers **"Create android"**; building one
   yields a pawn in the colonist bar with no join quest and no recruitment.
3. The android's Health tab shows `VREA_NeutroLoss`; its Character tab shows the custom
   xenotype name chosen in the window.
4. **No penalty is applied to the player for owning android colonists** — no mood debuff on
   other colonists absent the Ideology precept, no faction goodwill change. *This is the check
   the ending's argument actually depends on.*
5. **Multiplayer, two clients:** one player commits an order in the creation window; the other
   client's station shows the same project, the same required items and the same progress bar.
   This is the one check reading cannot fully settle, because it exercises MP Compat's sync
   worker rather than any def — but the registration is read and cited, so a failure here would
   be a bug in a third-party mod, not a gap in this design.

`tools/patch_check.py` holds the two annotated scoping operations to their expected counts if
that patch is written.

---

## Outstanding decisions

1. **Should awakened androids appear at 2% in outlander and pirate populations from game
   start?** A fiction call, not a structural one — our own factions are unaffected. If no, the
   scoping patch above is ~10 lines of XML. **Owner: the era/progression fiction, not a
   capability ticket.** No ticket currently owns it.

2. **Does an android colonist hold Devotion, and does the campaign want it to?** Nothing in
   VRE – Android blocks it **[V]**, and `docs/specs/RELIGION.md` does not currently say whether
   Devotion alignment has a personhood predicate at all. **This is a requirements gap, not a
   mechanism gap** — it is handed back rather than settled here. It interacts with
   `RELIGION.md`'s open question 12 (whether Devotion alignment is reference equality on `Ideo`
   or doctrinal equivalence), because an android colonist shares the colony's `Ideo` by
   construction.

3. **Androids cannot take psycasts, permanently.** This is shipped behaviour and cannot be
   patched away without fighting a `HarmonyPriority(int.MaxValue)` prefix — deselecting
   `VREA_PsychicallyDeaf` does not help, because the prefix never reads genes. The campaign must
   decide whether that is
   a *stated* cost of an artificial body — which is a defensible and interesting reading — or
   whether it contradicts *"the campaign does not treat artificial bodies as inherently
   inferior."* **It is the one place where the mechanics do impose an asymmetry, and the
   requirement's wording does not currently anticipate it.** Handed to
   `docs/requirements/GLITTERTECH.md`'s owner. This has implications for
   `docs/specs/TRANSCENDENCE.md` if the endgame assumes any colonist can be a psycaster.

4. **Resolved: an android costs no Intel per unit.** Intel is exchanged for Instruction items,
   and [`CURRENCIES.md`](CURRENCIES.md) admits no other debit (§5). Whether `VREA_AndroidTech`
   also requires an Instruction item bought with Intel is exchange-catalogue authoring, owned by
   [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117).

5. **Does the campaign want the per-android material cost changed?** It cannot be done in XML
   (the list is a C# literal). If Ultra manufacture should cost a Glitterite material rather
   than Uranium, that is a ~15-line Harmony postfix on
   `Window_AndroidCreation.OnGenesChanged` and should be decided before the Ultra chapter is
   priced.
