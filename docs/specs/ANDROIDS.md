# Androids

## Purpose and scope

> **Authority correction — 2026-09-13.** “Android” is a body/person category;
> “Glitterite” is a civilization and origin. Other androids can be sincere believers and
> can be essentially ordinary people. Glitterites deliberately removed emotion, fervor
> and the faculties needed to connect to the channel; they run on anima-rich
> neutroamine, cannot receive psylinks and are not hackable. The VRE donor's psylink block is a
> carrier constraint, not permission to generalize the Glitterite condition to every android in
> the fiction. *(#141: nor is that block unconditional — it is two XML-reachable gates. See
> **Psylinks — verdict and routes**.)*

> **Premise reopened 2026-09-16, answered 2026-09-23.** The psylink block is **not** unconditional,
> and #78's statement of it was wrong in both halves. [#141](https://github.com/cjd721/Rimworld-Archinity/issues/141)
> settled it; the answer is *Psylinks — verdict and routes* below, and §2, *Status*, *Verification*
> and decision 3 are corrected in place.

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
class **READ**. The psylink question below is
[#141](https://github.com/cjd721/Rimworld-Archinity/issues/141)'s, also **READ**. Since
[#142](https://github.com/cjd721/Rimworld-Archinity/issues/142) this document also owns **the captured
Glitterite as an android pawn** — no faith, never recruited, enslaved or converted — because no other
spec owns the Glitterite faction's pawns; see *A captured Glitterite*.
[#143](https://github.com/cjd721/Rimworld-Archinity/issues/143) adds the one exception, the jailbreak;
see *Jailbreaking a captured Glitterite into an android colonist*.

---

## Psylinks — verdict and routes

*Answers `docs/requirements/GLITTERTECH.md`: "**Whether an android can hold a psylink is open.**
If a route lets it, the campaign may take it; if none does, the asymmetry stands."
Established by [#141](https://github.com/cjd721/Rimworld-Archinity/issues/141).*

### Verdict

- **Possible? Yes.** An android colonist can hold a psylink and level it. The refusal is **two
  independent gates carried by two different genes** — `VREA_SyntheticImmunity` refuses the hediff,
  `VREA_PsychicallyDeaf` zeroes psychic sensitivity — and the second one's refusal is vanilla's
  code, not VRE's. Both are reachable from XML, and **lifting either alone gets you nothing.**
  Two of vanilla's four grant routes open with a pure-XML lift; the anima tree needs one more
  patch for a reason that has nothing to do with androids; the psylink neuroformer's *upgrade*
  step is the only thing that genuinely needs C#.
- **Multiplayer? Yes.** Every XML route changes defs and introduces no code path, so it has no
  sync surface of its own, and the machinery it hands the android to is already carried —
  `Multiplayer.Compat.VanillaRacesAndroid` and `Multiplayer.Compat.VanillaPsycastsExpanded` both
  sit in the loaded `1629973374/1.6/Assemblies/Multiplayer_Compat.dll`. **[V]**

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **A — global lift** | *Every* android can hold, level and cast from a psylink. Two operations: the `PsychicAmplifier` entry (gate 1) and `VREA_PsychicallyDeaf`'s stat factor (gate 2) | VRE – Android (`vanillaracesexpanded.android`, `2975771801`) — its own `AndroidSettings` def and `AndroidSettingsExtension`, plus the gene def | XML patch | Easy | Yes |
| **B — per-android lift** | The player chooses, at the creation station, which androids can hear the channel; those that can also lose synthetic immunity. Two operations: `isCoreComponent` on `VREA_SyntheticImmunity` (gate 1) and on `VREA_PsychicallyDeaf` (gate 2) | same, via `VREAndroids.AndroidGeneDef.isCoreComponent` | XML patch | Easy | Yes |
| **C — anima access** *(additive)* | An awakened android may take the linking ritual at the anima tree | vanilla `MeditationFocusTypeAvailabilityCache.PawnCanUseInt`'s hediff bypass | XML patch | Easy | Yes |
| **D — our own prefix** | A gate that is **not** a gene — a story flag, the altar, an era — and the only way to reopen the neuroformer upgrade | our assembly; donor `VREAndroids.Pawn_HealthTracker_AddHediff_Patch` | C# | Medium | Yes |
| **E — leave it** | The asymmetry stands as a stated cost of an artificial body | — | — | — | — |

**Recommended, not selected: B.** It is the only route that makes the psylink a decision about
*one android* rather than a fact about the species, it costs two XML operations, and the price it
charges — the android that can hear the channel is the android that can fall ill — is a trade the
campaign's argument about personhood can use. A and B are not exclusive; C stacks on either.
Selection is a story decision.

### The two gates

> **They are two independent mechanisms with two different genes, and nothing connects them.**
> Gate 1 is `VREA_SyntheticImmunity`: it is the gene `Pawn_HealthTracker_AddHediff_Patch` tests
> before it will consult `AndroidCanCatch`, and `AndroidCanCatch` is what reads the
> `androidsShouldNotReceiveHediffs` list that `PsychicAmplifier` sits in. Gate 2 is
> `VREA_PsychicallyDeaf`: a `PsychicSensitivity` stat factor of 0 feeding vanilla's own
> `< float.Epsilon` tests. **[V]** Neither gene appears anywhere in the other's path —
> `AndroidCanCatch` never reads `VREA_PsychicallyDeaf`, and vanilla's sensitivity tests never read
> `VREA_SyntheticImmunity`. A route that lifts one has not touched the other, which is why route A
> is *two* operations and why the phrase "the android psylink block" is always wrong in the
> singular.

**Gate 1 — `VREA_SyntheticImmunity` refuses the first psylink hediff.**
`RimWorld.PawnUtility.ChangePsylinkLevel` makes
`PsychicAmplifier` and calls `pawn.health.AddHediff(...)` when the pawn has no psylink, and calls
`Hediff_Psylink.ChangeLevel(int, bool)` when it already has one. **[V]**
`VREAndroids.Pawn_HealthTracker_AddHediff_Patch.Prefix` — and `VREAndroids.HediffSet_AddDirect_Patch.Prefix`,
which delegates to the same helper — routes every android hediff through
`Pawn_HealthTracker_AddHediff_Patch.HandleHediffForAndroid`, which returns `false` when
`pawn.HasActiveGene(VREA_SyntheticImmunity) && !Utils.AndroidCanCatch(hediff.def)`. **[V]**
`Utils.AndroidCanCatch` consults, in order: an `AndroidSettingsExtension` mod extension on the
hediff def (`androidCanCatchIt`); the `"Sterilized"` tag; `VREA_AndroidSettings.androidsShouldNotReceiveHediffs`;
then a class / `chronic` / `Immunizable` / `makesSickThought` battery. **[V]** `PsychicAmplifier` is
the fifth entry of that list in `2975771801/1.6/Defs/AndroidSettings.xml` **[V]**, and vanilla's
`HediffDef PsychicAmplifier` carries no tags, no comps, no `chronic` and no `makesSickThought` — so
taking it off the list makes `AndroidCanCatch` return `true`. **[V]**

**Gate 2 — `VREA_PsychicallyDeaf` zeroes psychic sensitivity, and the refusal that follows is
vanilla's, not VRE's.** `VREA_PsychicallyDeaf` declares
`<statFactors><PsychicSensitivity>0</PsychicSensitivity></statFactors>` **[V]**, and
`RimWorld.Psycast.GizmoDisabled` and `RimWorld.Verb_CastPsycast.ValidateTarget` both refuse at
`PsychicSensitivity < float.Epsilon`. **[V]** This gate is not in VRE's Harmony patches at all — it
is a stat factor in a def meeting a vanilla comparison. Lift gate 1 alone and the android holds a
psylink level and a psycast gizmo it can never press.

**`Hediff_Psylink_ChangeLevel_Patch` is not gate 1, and never was.** It is declared
`[HarmonyPatch(typeof(Hediff_Psylink), "ChangeLevel", new Type[] { typeof(int) })]` — the
**one-argument override only**. **[V]** Vanilla `Verse.Hediff_Psylink` declares both
`ChangeLevel(int, bool)` and `override ChangeLevel(int)`, and the one-arg delegates to the
two-arg **[V]**, so the prefix catches only `CompUseEffect_InstallImplant.DoEffect`,
`JobDriver_InstallImplant`, `Recipe_ChangeImplantLevel.ApplyOnPawn`, `HediffComp_ChangeImplantLevel`
and the dev tool. **[V]** Every ritual grant path reaches `ChangeLevel(int, bool)`, which VRE does
not patch.

### What each grant route does once gate 1 is lifted

| Grant route | Vanilla call site | State after an XML lift |
|---|---|---|
| **Bestowing ceremony** | `RitualOutcomeEffectWorker_Bestowing` → `ChangePsylinkLevel(1, false)` **[V]** | Works, first level and every later level |
| **Blinding ritual** (Ideology) | `RitualOutcomeEffectWorker_Blinding.ApplyExtraOutcome` → `ChangePsylinkLevel(1)` **[V]** | Works |
| **Psylink neuroformer** | `CompUseEffect_InstallImplant.DoEffect`: `AddHediff` when absent, else `ChangeLevel(1)` **[V]** | First use works; **every upgrade stays blocked** by the one-arg prefix. No XML reaches it — that is route D's unique job |
| **Anima tree linking** | `CompPsylinkable.FinishLinkingRitual` → `ChangePsylinkLevel(1)` **[V]** | Still closed — see route C |

### Route A — global lift

Two operations against VRE – Android's own declared compatibility seam; the `AndroidSettings` def's
label reads *"Can be used for mod compatibility from outside via xml patches."* **[V]**

- **Gate 1** (the `VREA_SyntheticImmunity` path): take `PsychicAmplifier` off
  `androidsShouldNotReceiveHediffs`, **or** add an
  `AndroidSettingsExtension` with `androidCanCatchIt true` to the hediff def — the extension is
  checked first and short-circuits **[V]**, and VRE ships that exact operation shape on
  `HediffDef[@Name="DiseaseBase"]` in `1.6/Patches/Core.xml`. **[V]** Note that neither operation
  touches the gene: they change what `AndroidCanCatch` answers, so the gate opens for every
  android whether or not it carries `VREA_SyntheticImmunity`.
- **Gate 2** (the `VREA_PsychicallyDeaf` path): restore its `PsychicSensitivity` factor to a
  non-zero value. **Removing the
  gene from the xenotype bases does not work:** `Window_CreateAndroidBase` seeds `selectedGenes`
  from `Utils.AndroidGenesGenesInOrder.Where(x => !x.CanBeRemovedFromAndroid())`, not from the
  xenotype, and `Building_AndroidCreationStation.FinishAndroidProject` installs the project's gene
  list **[V]** — so the gene lands on every player-built android whatever the xenotype says.

**What it gets us.** Psylinks as an ordinary colonist capability that happens to include androids.
No new UI, no new decision, nothing for the player to discover.

**What it cannot do.** It is a statement about the species. Every android built, bought, captured or
awakened becomes psychically sensitive, and the gene's own label and description then lie.

**Consequences.** `VREA_PsychicallyDeaf` also shields androids from hostile psychic effects.
`Psycast.CanApplyPsycastTo` refuses a target at `PsychicSensitivity < float.Epsilon` **[V]**, so
lifting the factor removes that shield; that psychic *incidents* begin to bite too is **[I]**.

### Route B — per-android lift

Set `<isCoreComponent>false</isCoreComponent>` on the concrete `VREA_SyntheticImmunity` and
`VREA_PsychicallyDeaf` defs, overriding the `true` they inherit from `VREA_HardwareBase`. **[V]**
**One def per gate, and both are needed:** de-coring `VREA_SyntheticImmunity` alone opens gate 1
and leaves the android deaf; de-coring `VREA_PsychicallyDeaf` alone restores sensitivity to a pawn
that can still never be given the hediff.

That flips exactly the predicate the creation window uses. `Utils.CanBeRemovedFromAndroid` returns
false for `AndroidGeneDef { isCoreComponent: not false }` **[V]**; `Window_CreateAndroidBase`
pre-selects every gene that fails it and refuses to un-toggle it. **[V]** With the field false both
genes become ordinary selectable hardware, and an android built without `VREA_SyntheticImmunity`
never enters `HandleHediffForAndroid`'s `AndroidCanCatch` branch at all — gate 1 does not apply to
it. **[V]**

**What it gets us.** The story can point at *this* android. A sensitive unit is a deliberate build
with a visible biostat cost in the creation window, and the fiction gets a mechanical reason why
most androids are deaf.

**What it cannot do.** The lever is gene presence and nothing else — it cannot make the capability
depend on an era, an altar, a quest or a pawn's history (that is route D). Nor can it separate
*can hold a psylink* from *can catch tuberculosis*: dropping `VREA_SyntheticImmunity` opens every
hediff `AndroidCanCatch` was filtering — diseases, addictions, toxic buildup, `Carcinoma`. **[V]**

**Consequences.** Androids that arrive rather than get built (recruits, awakened NPCs, gifts) carry
both genes from the xenotype. Stripping them afterwards is the behaviorist station's
`Window_AndroidModification`, which extends the same base and shares its removal predicate — so it
should follow, **[I]**, not read end to end.

**A lever worth knowing.** VRE – Android adopts as an android gene **any `GeneDef` in the database**
whose `displayCategory` is `VREA_Hardware` or `VREA_Subroutine`:
`GeneDefGenerator_ImpliedGeneDefs_Patch.Postfix` iterates `DefDatabase<GeneDef>.AllDefsListForReading`
and calls `AddAndroidGene` on every match. **[V]** Archinity can therefore author its own android
hardware components in pure XML and have them appear in the creation window — which is what makes a
*named, in-fiction component* (rather than "the absence of a gene") an Easy option rather than a C#
one. That such a gene composes into a working psychic android is **[I]**.

### Route C — anima access (additive)

The anima tree is closed to androids for two reasons, **neither of which is the psylink block.**

1. `CompPsylinkable.CanPsylink` requires `Props.requiredFocus.CanPawnUse(pawn)` **[V]**. Vanilla's
   `MeditationFocusDef Natural` declares `requiredBackstoriesAny` of `Tribal` / `AdultTribal` /
   `ChildTribal` in the Childhood slot **[V]**, and `MeditationFocusTypeAvailabilityCache.PawnCanUseInt`
   returns `false` when a focus with a non-empty `requiredBackstoriesAny` matches nothing **[V]**.
   VRE – Android's backstories declare only `AwakenedAndroid` and `ColonyAndroid`. **[V]**
   **This gate would close the anima tree to androids even if VRE – Android did not exist.**
2. `VREAndroids.MeditationFocusTypeAvailabilityCache_PawnCanUseInt_Patch` forces the result `false`
   for any pawn with `VREA_JoyDisabled` **[V]** — every non-awakened android. That gene carries
   `removeWhenAwakened true` **[V]**, so awakening clears it, and `Gene_SyntheticBody` calls
   `MeditationFocusTypeAvailabilityCache.ClearFor(pawn)` so the cache does not keep a stale
   `false`. **[V]**

The bypass is vanilla's own and it is XML: `PawnCanUseInt` returns `true` if **any hediff on the
pawn** lists the focus in `HediffDef.allowedMeditationFocusTypes`. **[V]** Give an android-carried
hediff — `VREA_Reactor`, or a new one — `Natural`, and an awakened android can take the ritual.

**What it cannot do.** Nothing for a non-awakened android, because of reason 2; awakening is
`Gene_SyntheticBody.Awaken`'s authored transition and is not on the player's schedule.

**Consequences.** A hediff that grants `Natural` grants it wherever that hediff goes. Scope it to a
def only androids carry.

### Route D — our own prefix

Two jobs no XML reaches. **A gate that is not a gene:** a prefix of ours ahead of VRE's
`HarmonyPriority(int.MaxValue)` `Pawn_HealthTracker_AddHediff_Patch` can let `PsychicAmplifier`
through for a pawn selected by anything the campaign likes; the donor is VRE's own patch and the
seam is verified. **The neuroformer upgrade:** `Hediff_Psylink_ChangeLevel_Patch` is unconditional
on `IsAndroid()` and reads no gene **[V]**, so levels 2–6 by neuroformer need a prefix ahead of it
or an `Unpatch`.

**Consequences.** Patching against another mod's `int.MaxValue`-priority prefix is ordering-sensitive
and the kind of thing that breaks quietly on a VRE update. Take it only if the campaign needs a
non-gene gate. **[I]** by construction.

### Constraints every psylink route inherits

**A psylink on an android is a level counter until `PsychicSensitivity` is non-zero.** Gate 2 is
vanilla's and applies to any pawn. **[V]**

> **⚠ With Vanilla Psycasts Expanded and Royalty both running, bestowing a title on a
> psylink-blocked android throws.** `VanillaPsycastsExpanded.RitualOutcomeEffectWorker_Bestowing_Apply_Patch`
> transpiles vanilla's psylink loop out of `RitualOutcomeEffectWorker_Bestowing.Apply` and replaces
> it with `ApplyTitlePsylink`, whose null branch calls `PawnUtility.ChangePsylinkLevel(pawn, 1, false)`
> and then **immediately dereferences `pawn.Psycasts()`**. **[V]** For an android, `ChangePsylinkLevel`
> is swallowed by gate 1, `Psycasts()` returns `null` — it is
> `hediffSet.GetFirstHediffOfDef(VPE_PsycastAbilityImplant)` **[V]** — and the next line NREs inside
> a ritual outcome. **Zeroing `maxPsylinkLevel` on the title does not avoid it**: the null branch runs
> before any level arithmetic. **[V]** This bears on [`RELIGION.md`](RELIGION.md) §4's Church-title
> design wherever an android could be the honoree.

**VPE replaces psylink levelling wholesale.** `VanillaPsycastsExpanded.Hediff_Psylink_ChangeLevel`
prefixes `ChangeLevel(int, bool)` and returns `false`, routing the level into
`pawn.Psycasts().ChangeLevel(...)`; `Hediff_Psylink_PostAdd` attaches `VPE_PsycastAbilityImplant`;
`Hediff_Psylink_TryGiveAbilityOfLevel` suppresses vanilla's random-ability grant. **[V]** So with VPE
loaded the campaign's "psylink level" is really a psycast point, and a lifted gate 1 hands androids
psycast points. `VPE_PsycastAbilityImplant`'s def carries no tags, comps, `chronic` or
`makesSickThought`, so `AndroidCanCatch` permits it and VPE's `PostAdd` postfix does not NRE on an
android. **[V]**

**Multiplayer, re-read rather than inherited.** `Multiplayer.Compat.VanillaRacesAndroid`
(`[MpCompatFor("vanillaracesexpanded.android")]`) and `Multiplayer.Compat.VanillaPsycastsExpanded`
(`[MpCompatFor("VanillaExpanded.VPsycastsE")]`) are both in the loaded 1.6 `Multiplayer_Compat.dll`,
not the `Referenced/` copy. **[V]** The latter registers sync methods on
`VanillaPsycastsExpanded.Hediff_PsycastAbilities` for `SpentPoints`, `ImproveStats`, `UnlockPath`,
`UnlockMeditationFocus` and `GainExperience`, plus sync workers for the psyset dialogs **[V]** —
everything a psycasting android would then do.

### Corrections this section makes to #78

1. *"The prefix is the whole block, and it is unconditional"* — **wrong.** The prefix is not the
   block; it catches only the one-argument `ChangeLevel` overload, which no ritual grant path uses.
2. *"`VREA_PsychicallyDeaf` … a player can deselect it when designing an android"* — **wrong.** It
   inherits `isCoreComponent true` from `VREA_HardwareBase`, and neither
   `CanBeRemovedFromAndroid()` nor `CanBeRemovedFromAndroidAwakened()` is true for a hardware gene
   without `removeWhenAwakened`, so the creation window will not un-toggle it. **[V]** #78's
   *conclusion* (deselecting buys nothing) was right; both halves of its reason were wrong, and the
   corrected mechanism is exactly what makes routes A and B possible.

### Open questions

1. **Requirement gap, handed to `docs/requirements/GLITTERTECH.md`'s owner.** It says the question
   is open and the campaign may take a route if one exists. Routes exist. What no document states:
   **which** androids — all of them (A) or a chosen build (B) — and whether route B's price (the
   android that hears the channel is the android that can fall ill) is one the campaign wants
   visible. Fiction, not capability.
2. **`docs/COSMOLOGY.md`'s *"no Glitterite can form a psylink or open a channel"* is untouched** —
   it is about Glitterites, and the 2026-09-13 authority correction above already separates
   Glitterite from android. But under route A the distinction stops being mechanical and becomes
   purely authorial. Unowned.
3. **Build questions, deferred to the next map:** the exact operations and their `expect:` counts;
   list-removal versus mod extension for the `PsychicAmplifier` lift; whether route B's sensitive
   android gets an authored Archinity hardware gene of its own; whether route C's `Natural` grant
   hangs off `VREA_Reactor` or a new hediff.
4. **The behaviorist-station path is [I]** — that an existing android can have a de-cored
   `VREA_PsychicallyDeaf` stripped at `VREA_AndroidBehavioristStation` follows from
   `Window_AndroidModification` extending `Window_CreateAndroidBase`, but its accept path was not
   read end to end. *#143 has since read the station's accept path for prisoners and the gene
   rules it enforces — see § Jailbreaking a captured Glitterite (J2/J3a) and T-163 — and this
   item should be re-graded against that reading, not re-run.*

---

## A captured Glitterite — no faith, never on the player's side

*Answers `docs/requirements/GLITTERTECH.md` § *A captured Glitterite*: "A Glitterite holds no
faith and believes nothing. Captured, it can be held as a prisoner and nothing more: it is never
recruited, enslaved or converted." Established by
[#142](https://github.com/cjd721/Rimworld-Archinity/issues/142), evidence class **READ**. The one
exception, the jailbreak, is [#143](https://github.com/cjd721/Rimworld-Archinity/issues/143)'s.*

**Why this document.** No spec owns the Glitterite faction. `TRACE.md` owns their pursuit,
`ORBIT.md` their settlements, and neither owns the pawn. The answer here depends on the Glitterite
having an **android body** — VRE – Android genes, the creation and behaviorist machinery, and the
`IsAndroid` predicate — and that body is this document's subject. It is also where #141's
Glitterite/android distinction already lives. The answer is for the android
Glitterite the fiction describes, not today's `Archinity.Glitterites` defs. Those make them race
`Human` with Genie, Hussar and Highmate xenotypes, and they are due for a rewrite.

### Verdict

- **Possible? Yes.** Nothing in the corpus ships it. Vanilla's two flags each cover part of one
  clause:
  - `PawnKindDef.preventIdeo` makes a faithless pawn, but a faithless pawn is the **easiest** pawn
    to convert (T-161).
  - `recruitable = false` holds only under a difficulty option. It hides two of the five prisoner
    modes, and seven writers set it back (T-162).

  Two Harmony routes on verified seams cover every clause, keyed on a durable Glitterite marker.
  **Route B** closes every offer. **Route C** refuses every effect at the chokepoints all paths
  share.
- **Multiplayer? Yes.** Every route reads pawn state that is already synced and runs inside commands
  or ticks that are already synced. None adds a command, a UI write or a mod setting.

### Every route keys on a marker

Something must say "this pawn is a Glitterite", and must still say it after everything the game
does to a pawn. The candidates [V]:

| Marker | Survives | Loses it |
|---|---|---|
| **A gene in the Glitterite android xenotype** *(recommended)* | `ChangeKind` (joining, redress), `SetFaction`, sale. Every pawn the Glitterite faction generates carries it, including a vanilla `Slave`-kind pawn, because `Slave` has `useFactionXenotypes` true | Gene removal. VRE – Android adopts any `GeneDef` with `displayCategory` `VREA_Hardware`/`VREA_Subroutine` (`GeneDefGenerator_ImpliedGeneDefs_Patch.Postfix`), and `isCoreComponent` decides whether the creation and behaviorist windows can remove it (`Utils.CanBeRemovedFromAndroid`). The xenogerm erasures of T-111 do not reach androids through the UI: VRE's `Xenogerm_GetFloatMenuOptions_Patch` and `CompAbilityEffect_ReimplantXenogerm_Valid_Patch` both test `IsAndroid()` [V]. A `Xenogerm_GetGizmos_Patch` exists and was not read [I] |
| A `PawnKindDef` | Nothing past `ChangeKind` (T-112) | Joining, redress, run-wild |
| A hediff | `ChangeKind`, `SetFaction` | Surgery, if any recipe removes it. Needs `duplicationAllowed false` (T-113) |
| Faction membership | — | Sale (`Pawn.PreTraded(PlayerSells)` → `SetFaction(null)`). Misses a Glitterite who is no longer a member |

**#143 passes through the gene.** The jailbreak is the act that removes the marker. VRE's
`Building_AndroidBehavioristStation.CanAcceptPawn` accepts an android `IsPrisonerOfColony` [V]. The
"opened up" seam already exists and already takes prisoners. #143 then joins the pawn through
`RecruitUtility.Recruit`, which every route below lets pass once the marker is gone. *#143 refines
this:* stripping the marker at the station as shipped only **unlocks** the prisoner (#143's J3a) —
it neither consumes, awakens nor joins, and it lifts every clause below at once. #143's recommended
jailbreak is a surgery that removes the marker and joins in one call; see *Jailbreaking a captured
Glitterite into an android colonist*.

**The marker also reaches pawns the Glitterite faction never made** [V]. `XenotypeDef.factionlessGenerationWeight`
defaults to **1**, and `PawnGenerator.AdjustXenotypeForFactionlessPawn` rolls every factionless
baseliner against it. A Glitterite xenotype that leaves it at the default spawns factionless marked
pawns — refugees, quest joiners, world pawns — whose joins route C then refuses. VRE – Android sets
it `0` on `VREA_AndroidBasic` for the same reason; the Glitterite xenotype must too.

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **A — vanilla flags** *(not recommended alone)* | No faith at generation (`preventIdeo`). Recruit and reduce-resistance are hidden (`recruitable = false`). Enslave, reduce-will and convert are hidden too, if `hideIfNotRecruitable` is patched onto those three modes | vanilla | XML, plus one C# write of `guest.Recruitable` at generation | Easy–Medium | Yes |
| **B — close every offer** | No player-facing option ever appears: no warden mode, no Convert ability target, no convertee slot, no Glitterite in a slaver's stock. The prisoner tab reads *"Non-recruitable"* | our assembly. Donor for the tab: VRE – Android's `ITab_Pawn_Visitor_CanUsePrisonerInteractionMode_Patch` | C# patches + XML | Medium | Yes |
| **C — refuse every effect** | No faith can be written, and no path can make the pawn the player's — including third-party ones nobody listed | our assembly | C# prefixes | Medium | Yes |
| **B + C** *(recommended)* | B's legible "no" in front of C's absolute one | our assembly | C# + XML | Medium | Yes |

**Which clause each route closes** [mechanisms V, coverage I]:

| Clause | A | B | C |
|---|---|---|---|
| No ideology | At generation only. Conversion writes one (T-161); redress into another faction writes one | Yes against every vanilla offer | **Yes, absolutely** |
| Recruit never offered or run | While `unwaveringPrisoners` is on and no writer flips it (T-162) | **Yes** | Run: yes. Offered: no |
| Convert never offered or run | Warden mode only | Warden, ability, ritual | **All effects** |
| Enslave never offered or run | Warden modes only | Warden, plus slaver stock | **All effects** |
| No other path to the player | No | Vanilla offers only | **Yes** |
| Imprisonment still works | Yes | Yes | Yes |

One route does not cover every clause **and** read well to the player. C alone is absolute, but it
refuses after the game has committed (see its consequences). B alone is legible but leaves
third-party writers open. That is why the recommendation is both.

#### Route A — vanilla flags

**What it gets us.**
- `<preventIdeo>true</preventIdeo>` on every Glitterite kind. `PawnGenerator` then assigns no faith,
  and `Pawn.ShouldHaveIdeo` is false, so the load-time fallback does not fire [V].
- The Glitterite faction's `hiddenIdeo` faith then never un-hides, because only a spawning *holder*
  flips it (`Pawn.SpawnSetup`) [V].
- `recruitable = false` shows *"Non-recruitable"* on the prisoner tab and hides the two Core modes
  [V].
- `hideIfNotRecruitable` is a plain def field, so patching it onto `Enslave`, `ReduceWill` and
  `Convert` is XML [V].

**What it cannot do.**
- It cannot keep the faith null: the Convert ability and the conversion ritual both accept a
  faithless prisoner and write one (T-161).
- It cannot hold "never recruited" (T-162):
  - The getter ignores the field unless the host's difficulty keeps `unwaveringPrisoners` on.
  - `PawnGroupKindWorker_Normal` sets the field true on its `forceOneDowned` raider.
  - Three corpus mods flip it: VPE Puppeteer subjugation, Ushanka's gamma serum, and VQE Ancients'
    `VQEA_MasterfulSocial`.
- There is no XML field for `recruitable`. `PawnGenerator` rolls it through `SetupRecruitable`, so
  even this route writes it from C#.
- It leaves slaver stock, the ability, the ritual and every direct `SetFaction` writer open.

**Consequences.** Patching `hideIfNotRecruitable` onto the Ideology modes changes a vanilla rule for
**every** unrecruitable prisoner: vanilla's first-capture letter tells the player an unrecruitable
pawn can still be enslaved. `preventIdeo` rides on the kind, so it ends at the first `ChangeKind`
(T-112).

#### Route B — close every offer

**What it gets us** — each seam verified to exist [V]:
- **Recruit.** A postfix on the `Pawn_GuestTracker.Recruitable` getter returns false for a marked
  pawn. It does not depend on difficulty, and every writer in T-162 becomes inert. It also buys
  vanilla's own *"Non-recruitable"* line and its hidden recruit modes.
- **Warden modes.** A postfix on `ITab_Pawn_Visitor`'s local `CanUsePrisonerInteractionMode` hides
  `Enslave`, `ReduceWill` and `Convert`. VRE – Android ships exactly this patch shape, and finds
  the local function by name, to hide `HemogenFarm` from androids. The warden work-givers act only
  on the mode that is set: `WorkGiver_Warden_Chat`, `_Enslave` and `_Convert` all read
  `ExclusiveInteractionMode` / `IsInteractionEnabled`. A mode that cannot be chosen is never run.
  Captured prisoners start on `MaintainOnly`.
- **Convert ability.** A postfix on `CompAbilityEffect_Convert.Valid`.
- **Conversion ritual.** A postfix on `RitualRoleConvertee.AppliesToPawn`, with a reason string.
- **Slaver stock.** `StockGenerator_Slaves.GenerateThings` picks a random faction from
  `AllFactionsVisible` that is humanlike, not temporary and not the player. **`permanentEnemy`
  is not excluded**, so as shipped a slaver can stock a Glitterite-faction `Slave` wearing the
  faction's xenotype. The filter is ours; whether it filters the faction pick or the output is a
  build question.
- **No faith.** `preventIdeo` from route A, or a postfix on `Pawn.ShouldHaveIdeo`. That property is
  the only reader of the load-time fallback.

**What it cannot do.** It closes the vanilla offers. It does not close:
- **Third-party writers.** Each of these calls `Pawn.SetFaction(Faction.OfPlayer)` or
  `RecruitUtility.Recruit` directly, behind no prisoner mode [V]:
  - RimPacts: `MarryIn`, `AcceptAsylum`, `ArriveStateVisit`, `RestoreIfRedressed`;
  - Worksites Expanded: `Dialog_Parley`, `OrbitalVolunteerHall`, `WorksiteRecruitUtility`;
  - FT&V `ChoiceLetter_VassalPurchasedPawn`;
  - VQE Ancients' caskets.

  Most can never pick a Glitterite. Proving that for each is the enumeration route C makes
  unnecessary.
- **The redress leak.** `PrisonerWillingToJoinQuestUtility.GeneratePrisoner` reuses any living
  `Human` world pawn with `WorldPawnFactionDoesntMatter` [V]. Under the gene marker, a Glitterite
  who escaped into the world could be offered back as a rescuable joiner.

**Consequences.**
- The player is told "no" in vanilla's own words where vanilla has them.
- Ushanka's gamma serum becomes a dud on a Glitterite: its flag write is ignored, but it still sends
  its success letter [V for the write; I for the letter reading wrong].
- MP: every patch reads synced pawn state. The ITab choice itself is already a synced command
  (`SyncMethod.Register(Pawn_GuestTracker, "SetExclusiveInteraction")` in `Multiplayer.dll`) [V].

#### Route C — refuse every effect

**What it gets us.** Every path found converges on four methods [V]:
- **`Pawn.SetFaction(Faction.OfPlayer)`**. Paths that reach it:
  - recruit (`RecruitUtility.Recruit`);
  - enslave (`GenGuest.TryEnslavePrisoner` → `Pawn_GuestTracker.SetGuestStatus(Slave)` →
    `SetFaction(newHost)`);
  - VRE – Android's own `int.MaxValue` enslave prefix, which also goes through `SetGuestStatus`;
  - purchase (`Pawn.PreTraded(PlayerBuys)`);
  - every third-party writer above.

  The only pawn-level `SetFactionDirect` to the player is inside `PawnGenerator` and
  `GameInitData` (starting pawns), both of which make new pawns — hence the marker note on
  `factionlessGenerationWeight` above.
- **`Pawn_GuestTracker.SetGuestStatus(host, Slave)`**.
- **`Pawn_IdeoTracker.SetIdeo`**. Paths that reach it:
  - the ritual (`RitualOutcomeEffectWorker_Conversion`);
  - the ability, via `IdeoConversionAttempt`;
  - the speech;
  - Reliquary pilgrims;
  - redress;
  - the load-time fallback.
- **`Pawn_IdeoTracker.IdeoConversionAttempt`**. VFE Deserters also calls it directly.

A prefix on each, refusing a marked pawn, holds every clause however the call arrived.

**What it cannot do.** It refuses after the game has committed, and the callers do not expect a
refusal:
- **Recruit releases the prisoner.** `RecruitUtility.Recruit` calls `SetGuestStatus(null)` **before**
  `SetFaction`, so a refused recruit is a Glitterite freed on the map, hostile.
- **Enslave half-applies.** `SetGuestStatus(Slave)` writes `slaveFactionInt` after its
  `SetFaction` call, so refusing only `SetFaction` leaves a half-slave. Refusing `SetGuestStatus`
  as well is why it is on the list.
- **The ability misreports.** It reports its failure branch, and a warden conversion would still
  NRE first (T-161).

C is the backstop that makes "never" true. It is not a player-facing answer.

**Consequences.** MP: each refusal runs inside an already-synced command or tick, so both clients
refuse identically. There is no desync, but the partial states above would also be identical on both
clients. Harmony ordering: VRE's enslave prefix is `HarmonyPriority(int.MaxValue)`, so route C
should not try to beat it on `GenGuest.EnslavePrisoner`. It meets it downstream at
`SetGuestStatus` [V].

#### Recommendation — not a selection

Build **B + C on a gene marker**, with `preventIdeo` or the `ShouldHaveIdeo` postfix for a clean
null. B makes the "no" legible and keeps the game out of C's partial states. C makes "never" true
against paths nobody enumerated: seven `Recruitable` writers and more than a dozen direct
`SetFaction(Faction.OfPlayer)` sites across five mods turned up in one pass. The gene marker is the one that survives joining, redress and sale, and it
hands #143 its exception for free. Take A only as the XML half of B (`preventIdeo`), never as the
answer.

### Constraints

- **No faith and no conversion are two properties.** A null `Ideo` converts on the first attempt —
  T-161. A route that delivers the first clause without gating conversion delivers neither.
- **Vanilla "unrecruitable" is not a pawn fact** — T-162.
- **A kind is not a marker** — T-112, now including world-pawn redress.
- **Anomaly-only precedents are unavailable** at our DLC floor. Anomaly is not installed: `Data/`
  holds Core, Royalty, Ideology, Biotech and Odyssey. That rules out `Pawn.IsSubhuman` (mutants,
  `MutantDef.consideredSubhuman`, which the getter reads), `MutantDef.disablesIdeo`, the
  creepjoiner `Recruitable = false`, holding-platform containment and `studiableAsPrisoner` (whose
  ITab branch is `ModsConfig.AnomalyActive`). The code is in `Assembly-CSharp`; the content that
  would reach it is not.
- **Imprisonment is untouched by every route.**
  - Capture is `Pawn_GuestTracker.CapturedBy` → `SetGuestStatus(player, Prisoner)`. It sets a host
    and never calls `SetFaction` on the prisoner [V].
  - Release, execution and feeding are their own work-givers, and none is patched.
  - The one open part is android upkeep in a cell. VRE – Android ships no warden work-giver (its
    only warden-adjacent patch is the enslave prefix), so whether a prisoner's reactor or neutroamine
    needs a warden is **[I]**.

### Available mechanisms

- **Vanilla, 1.6.4871 `Assembly-CSharp`, decompiled** [V]:
  - `PawnKindDef.preventIdeo`, `Pawn.ShouldHaveIdeo`, `Pawn_IdeoTracker.ExposeData`'s fallback,
    `FactionDef.hiddenIdeo` — `docs/engine/ideology.md` § *A pawn with no ideology*.
  - The conversion funnel — T-161.
  - `Pawn_GuestTracker.Recruitable` / `.SetGuestStatus` / `.CapturedBy`; `ITab_Pawn_Visitor`'s
    `CanUsePrisonerInteractionMode`; the three warden work-givers; `GenGuest.TryEnslavePrisoner`;
    `RecruitUtility.Recruit`; `Pawn.SetFaction`; `Pawn.PreTraded`; `StockGenerator_Slaves`;
    `PawnGenerator.IsValidCandidateToRedress`; `PrisonerWillingToJoinQuestUtility`.
  - `QuestNode_GetPawn` and `QuestGen_Pawns` exclude `permanentEnemy` factions when they
    **generate** a pawn (`allowPermanentEnemyFaction` defaults false). An existing pawn is excluded
    only when the slate sets the flag false explicitly [V].
  - `permanentEnemy` is a strong filter on quest joiners, not a complete one.
- **VRE – Android** (`2975771801/1.6/Assemblies/VREAndroids.dll`, decompiled) [V]:
  - It touches no ideology, recruitment or conversion code. Its only prisoner patches are
    `GenGuest_EnslavePrisoner_Patch` (the *Androids as tools* precept enslaves without the vanilla
    path) and the `HemogenFarm` hide.
  - Its behaviorist and polyanalyzer stations accept prisoners of the colony.
  - Its own android kinds set resistance 0 and will 0 (`1.6/Defs/PawnKindDefs/PawnKinds_Special.xml`).
    **A Glitterite built on those kinds is recruited on the first chat**, so the Glitterite kinds
    must stay our own.
- **Multiplayer** (`2606448745/1.6/AssembliesCustom/Multiplayer.dll`) [V]:
  - It syncs `SetExclusiveInteraction`, `ToggleNonExclusiveInteraction` and the `ideoForConversion`
    field.
  - Storyteller difficulty is a **host-only** synced field, so route A's difficulty dependence is at
    least identical on both clients.
- **Wide pass** — both roots, `-g '!**/obj/**' -g '!**/Referenced/**'`, `-i`:
  - ASCII sweeps: `RecruitUtility`, `SetGuestStatus`, `EnslavePrisoner`, `IdeoConversionAttempt`,
    `set_Recruitable`, `SetExclusiveInteraction`, `ShouldHaveIdeo`, `preventIdeo`, and the
    no-ideo / unrecruitable / unconvertible / unenslavable name family.
  - Null-interleaved UTF-16 sweeps, typed literally: `preventIdeo`, `unrecruit`, `noideo`, `enslav`.
  - XML: `<preventIdeo>`, `disablesIdeo`.
  - Results:
    - The `SetFaction(OfPlayer)` / `Recruitable` writers above, all decompiled.
    - VFE Deserters' `FilthExtension_OnClean` conversion.
    - **No mod ships a never-recruit, never-convert or no-faith mechanism**; `preventIdeo` has zero
      uses in either root.
  - Validators: `<initialResistanceRange>` returns 156 XML files; `VREAndroids` returns UTF-16 in
    MP Compat; `prisoner` returns UTF-16 in VREAndroids.dll.

### Status

- **Verified [V]:**
  - every seam named above;
  - T-161, T-162;
  - today's Glitterites hold a real, hidden faith that un-hides at first spawn;
  - today's Glitterites are recruitable, enslavable and convertible;
  - slavers can stock Glitterite-faction pawns;
  - every player-side path found ends in `Pawn.SetFaction(Faction.OfPlayer)`.
- **Inferred [I]:**
  - that routes B and C compose into the requirement;
  - that no path outside the ones read reaches the player side without `SetFaction` (C covers any
    that does reach it);
  - residual null-`Ideo` dereferences outside the paths read. The pawn-facing UI and needs are
    guarded; 184 unguarded `.Ideo.` sites were not all read.
- **Corrects the ticket:**
  - "Only slows recruitment" understates today's defs. `hiddenIdeo` gives the Glitterites a real
    faith.
  - Ushanka's `USH_AncientGlittertechSoldier` is also on the Glitterite roster
    (`Patches/Glittertech_FactionRebind.xml`), so any kind-level route must cover a kind we do not
    own.
  - The vanilla flag the ticket points at, `unrecruitable`, is `Pawn_GuestTracker.recruitable`, and
    it is difficulty-gated.

### Open questions

1. **Build — owner #119.**
   - Which marker: gene (recommended) or hediff.
   - Whether the marker gene is `isCoreComponent` (fixed) or removable at the behaviorist station.
     If removable at the station, that is #143's J3a unlock, not a join; the accept path is now read
     (#143, *Jailbreaking a captured Glitterite*).
   - `factionlessGenerationWeight 0` on the Glitterite xenotype (see *Every route keys on a marker*).
   - Where the slaver filter sits.
   - Whether C's refusals log.
   - Whether `hideIfNotRecruitable` is patched globally or B's tab postfix does it per pawn.
2. **Story — Conrad.**
   - Should the prisoner tab explain *why*? B can reuse vanilla's *"Non-recruitable"* or add its
     own line.
   - May a Glitterite be **sold**? A sale takes it off the player's side and is not forbidden by
     the requirement, but it sets its faction to null (`PreTraded(PlayerSells)`).
3. **#143.**
   - `SetFaction(OfPlayer)` resets the kind (T-112), so the jailbroken android gets a fallback faith
     on the next load unless #143 gives it one deliberately.
   - The behaviorist station already takes prisoners.
4. **Unowned.**
   - Android upkeep in a cell (reactor and neutroamine) — **[I]**.
   - Ushanka's gamma serum sends a success letter on a Glitterite it cannot affect under B —
     **[I]**.

---

## Jailbreaking a captured Glitterite into an android colonist

*Answers `docs/requirements/GLITTERTECH.md` § *A captured Glitterite*, "Exploring, not chosen: the
jailbreak": a Glitterite taken home, opened up and given back the persona and free will it removed
may become an ordinary android colonist. A **jailbreak** (`CONTEXT.md`) is an operation on a
prisoner, never a hack from the console. Established by
[#143](https://github.com/cjd721/Rimworld-Archinity/issues/143), evidence class **READ**. It is the
one exception to the section above, and every route here passes through that section's marker.*

### Verdict

- **Possible? Yes.** Nothing in the corpus ships it, but every piece does, and the cleanest shape is
  an ordinary surgery. A surgery bill already reaches a held prisoner, hauls and consumes an item,
  and runs as a job. VRE – Android already ships the item-consuming, android-only surgery class to
  copy. Vanilla already ships a surgery that makes a prisoner the player's: Anomaly's
  `Recipe_GhoulInfusion`, whose code is in `Assembly-CSharp` even though its content is not
  installed. It is a precedent for the shape only: J1 calls none of it, so the DLC floor
  ([#6](https://github.com/cjd721/Rimworld-Archinity/issues/6), no Anomaly) is not touched. VRE's awakening is the "free will" half, and it reaches any android, whatever made it.
- **Multiplayer? Yes.** Surgery bills are a synced command, completion runs in a synced job tick,
  and MP Compat already syncs the behaviorist station and the awakening letter's choices. No route
  needs a custom dialog, and none should add one (see *Faith*).

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **J1 — jailbreak surgery** *(recommended)* | A bill on the prisoner's Operations tab that consumes a persona subcore. When it completes, one call removes the marker, awakens the android, gives it a faith and makes it a colonist. There is never a moment when it is an unmarked prisoner | our `Recipe_Surgery` subclass + a `RecipeDef`; VRE – Android (`Recipe_InstallAndroidPart`, `VREA_PersonaSubcore`) | C# + XML | Medium | Yes |
| **J2 — behaviorist station, patched** | The prisoner is carried into VRE's station. A postfix on `FinishAndroidProject` joins it when the marker has been removed in the window. The window can be allowed to strip the awakening genes. It consumes nothing | VRE – Android's `Building_AndroidBehavioristStation` + our postfixes | C# | Medium (Hard with a consumed item) | Yes |
| **J3 — unlock, then recruit the vanilla way** | The operation only removes the marker. The warden then recruits (or enslaves, or converts) an ordinary prisoner. Two carriers: **J3a**, the station as shipped, with a non-core subroutine marker; **J3b**, vanilla `Recipe_RemoveHediff` with a hediff marker and a subcore ingredient | VRE station as shipped / vanilla `Recipe_RemoveHediff` | XML (J3b); XML + one Harmony hide postfix (J3a) | Easy (J3b) · Medium (J3a) | Yes |
| **J4 — a ritual** *(not recommended)* | A rite of the player's faith with the prisoner in a `RitualRolePrisoner` slot; the outcome worker performs J1's call | vanilla Ideology rituals + our `RitualOutcomeEffectWorker` | C# + XML | Medium–Hard | Yes |
| **J5 — our own building and job** *(not recommended)* | A dedicated jailbreak rig | ours; donors are the behaviorist station and Biotech's subcore scanner | C# | Hard | With work |

**Recommended, not selected: J1.** It is the only route that does all three of what the requirement
asks: a deliberate operation on a held prisoner, a consumed persona, and a colonist at the end. It
does them atomically, and every moving part is already synced. J3 is the cheap alternative if
the campaign wants the jailbreak to **open** the Glitterite rather than **turn** it. J2 is only
worth it if the jailbreak should happen at a VRE machine rather than on a bed.

#### J1 — jailbreak surgery

**The seams, each verified to exist [V]:**
- **It reaches the prisoner.** `ITab_Pawn_Health.ShouldAllowOperations` returns true for
  `IsPrisonerOfColony`. A pending surgery makes the patient seek bed
  (`HealthAIUtility.ShouldSeekMedicalRestUrgent` → `ShouldHaveSurgeryDoneNow`), which is how vanilla
  operates on prisoners; that it runs unchanged for an android prisoner is **[I]**.
- **It can be android-only and consume an item.** VRE's `Recipe_InstallAndroidPart` is a
  `Recipe_Surgery` whose `AvailableOnNow` requires `IsAndroid()`. Its `VREA_InstallReactor` def
  names an item in `<ingredients>`, and `Recipe_InstallReactor.ApplyOnPawn` reads that consumed item
  from `ingredients`. `VREA_PersonaSubcore` is an ordinary `ThingDef` (§3), so it can be an
  ingredient the same way.
- **The operation can make the prisoner the player's.** `Recipe_GhoulInfusion.ApplyOnPawn` calls
  `pawn.SetFaction(Faction.OfPlayer)` on the patient. After `ApplyOnPawn`,
  `Bill_Medical.Notify_IterationCompleted` calls `billStack.Delete(this)`. That is safe even though
  `SetFaction` has already cleared the bill list, because `BillStack.Delete` is a plain
  `List.Remove`.
- **Free will: `Gene_SyntheticBody.Awaken(title, text)` is public.** It removes every
  `removeWhenAwakened` gene and restores `storedTripleName`, the full name that
  `PawnGenerator_TryGenerateNewPawnInternal_Patch` hid behind a single name at generation. It then
  sends `ChoiceLetter_AndroidAwakened`, where the player picks passions and a trait. A non-awakened
  android is generated with an empty `TraitSet` when it carries `VREA_PsychologyDisabled`, so this
  choice really is its personality coming back. The method checks nothing about where the pawn came
  from.
- **The join** is `RecruitUtility.Recruit(pawn, Faction.OfPlayer, billDoer)`, or `SetFaction` as
  ghoul infusion does it. See *What happens to the guest state* below.

**What it gets us.**
- An operation the player orders on the Operations tab like any other, with the bill visible and
  cancellable.
- A price in fiction: the persona it is given back is a persona subcore, and a subcore costs four
  colonists' scans at the polyanalyzer (§3).
- Its free will, shown as VRE's awakening letter, with its full name back.
- A faith chosen by the code, not by chance (see *Faith*).
- One synced call, so no in-between state that #142's routes would have to reason about.

**What it cannot do.**
- **Fail, as shipped.** VRE prefixes `Recipe_Surgery.CheckSurgeryFail` to return "no failure" for
  every android patient, and re-skills every android surgery to Crafting (T-164). A jailbreak that
  can go wrong needs its own roll inside `ApplyOnPawn`.
- **Be done by a doctor.** VRE routes android patients to `VREA_DoBillsAndroidOperation`
  (`workType Crafting`) and removes them from the medical work-giver (T-164).
- **Turn anything but an android.** That is by design: `AvailableOnNow` keys on the marker.

**Consequences.**
- The Operations tab offers the jailbreak on every marked prisoner as soon as the recipe is
  researched. Gate it with `researchPrerequisite` as the Glittertech tree does.
- Awakening sends a letter. A patient who is still a prisoner when `Awaken` runs passes
  `PawnUtility.ShouldSendNotificationAbout` like any colony pawn [I]. Whether awakening runs before
  or after the join is a build question.
- MP: `HealthCardUtility.CreateSurgeryBill` is a registered `SyncMethod` in `Multiplayer.dll`
  (and MP Compat's `CancelOperationModificationIfResultNull` guards VRE's postfix on it). Bill work
  and `ApplyOnPawn` run in a synced job tick, so the `Rand` inside `SetIdeo`'s certainty roll and
  `Awaken` is deterministic. MP Compat registers `ChoiceLetter_AndroidAwakened.MakeChoices` as a
  sync method, with a default letter choice [V].

#### J2 — behaviorist station, patched

**What ships [V].**
- `Building_AndroidBehavioristStation.CanAcceptPawn` takes any `IsAndroid()` pawn that is a
  colonist, a slave or `IsPrisonerOfColony`. It refuses only awakened non-prisoner colonists, and
  nothing checks provenance.
- `WorkGiver_CarryToAndroidBehavioristStation` extends vanilla `WorkGiver_CarryToBuilding`, which
  carries prisoners. It is Hauling work.
- `JobDriver_ModifyAndroid` (Research work, `ResearchSpeed`) calls `FinishAndroidProject` from its
  tick. That method removes every android gene and reinstalls the window's list, then ejects the
  pawn.
- MP Compat syncs the modification window (`AcceptInner` + a sync worker), the gizmo and float-menu
  lambdas, and suppresses the in-tick `WindowStack.Add` in `TryAcceptPawn`.

**What it cannot do as shipped.**
- **Awaken.** Every `removeWhenAwakened` gene is `VREA_Hardware` (`isCoreComponent true`).
  `Window_AndroidModification` never sets `disableAndroidHardwareLimitation`, so the toggle will not
  remove them.
- **Consume anything.** The station has no `requiredItems` or ingredient path at all:
  `ReadyForModifying` checks only power, project and occupant.
- **Join the pawn.** It stays a Glitterite-faction prisoner.

**The patched route.** Two seams:
- a postfix on `FinishAndroidProject` that joins the occupant when the marker is gone (and awakens
  it, or lets the window have done so);
- a postfix on the `Window_AndroidModification` constructor setting the public
  `disableAndroidHardwareLimitation` for a marked occupant, which opens the awakening genes
  (`CanBeRemovedFromAndroidAwakened`).

**What it gets us.** The jailbreak happens *in* the Glitterite machine the player already owns. The
player picks which subroutines to keep, which is J1's awakening with a gene-by-gene editor.

**Consequences.** A persona-subcore price means adding an ingredient path to a building that has
none. That is new hauling work, and it makes the route Hard. Research work, not Crafting.

#### J3 — unlock, then recruit the vanilla way

**J3a, the station as shipped.** VRE subroutines (`VREA_SubroutineBase`) inherit
`isCoreComponent false`, so a marker authored as a subroutine is an ordinary removable toggle in
`Window_AndroidModification` [V]. **J3b, pure XML.** Vanilla `Recipe_RemoveHediff` removes a
whole-body hediff named by `removesHediff` when `targetsBodyPart` is false. It requires the hediff
to be `Visible` [V]. A `RecipeDef` with that worker, the marker hediff and a subcore ingredient is a
jailbreak surgery with no C#.

**What it gets us.** The cheapest shape. The jailbreak *unlocks*; the colony still has to win the
Glitterite over the ordinary way, against its kind's resistance.

**What it cannot do.**
- It gives no personality: no awakening, no traits and a single name, unless the pawn later
  awakens by mood. See *Constraints*.
- It cannot choose the Glitterite's future. Removing the marker lifts **every** clause of the
  section above at once, so the unmarked prisoner can be enslaved or converted as readily as
  recruited. A warden conversion NREs on its null faith (T-161).
- J3b decides #142's open marker question as a **hediff**, which T-113 governs.
- J3a needs the marker hidden from the creation window, or the player can build androids that carry
  it (T-163). That is one `GeneValidator` postfix.

**Consequences.** Recruitment goes through `RecruitUtility.Recruit` like any prisoner's.
`preventIdeo` ends at the kind reset, so the colonist gets the load-time fallback faith, with a
logged warning (see *Faith*).

#### J4 — a ritual *(not recommended)*

`RitualRolePrisoner.AppliesToPawn` accepts `IsPrisonerOfColony` [V], and MP carries a
`Dialog_BeginRitual` sync worker (`SyncDictDlc`) [V]. The donor for a building-started rite is
vanilla's anima linking: `PreceptDef AnimaTreeLinking` is `visible false`, `classic true` and
`countsTowardsPreceptLimit false`, and `CompPsylinkable` finds it in the linker's own ideo [V].
Whether a hidden precept reaches every player faith, including a custom one, is **[I]**.

**Not recommended.** It makes the jailbreak a rite *of the player's faith*. That is a story choice,
not a mechanism, and it drags in ritual quality rolls and the faith's precept list (T-121). Nothing
it does needs a ritual, and the outcome worker would make J1's call anyway.

#### J5 — our own building and job *(not recommended)*

It is technically possible: a `Building_Enterable` on the behaviorist station's shape, plus the
subcore scanner's `def.building.*` ingredient pattern (§3). **Strictly dominated by J1.** A surgery
bill already provides the target selection, the ingredient hauling, the job, the progress and the
MP sync that J5 would have to write. It would also be a custom building whose UI is not covered by
MP Compat.

### What happens to the guest state on joining

All [V], `Assembly-CSharp` 1.6. Every route ends in `RecruitUtility.Recruit` or `Pawn.SetFaction`,
and both clear the prisoner state the same way:

1. `Recruit`: `apparel.UnlockAll()`, royal titles swapped by `replaceOnRecruited`, then
   **`guest.SetGuestStatus(null)`**. `Pawn.SetFaction` opens with the same call, so a bare
   `SetFaction` (ghoul-infusion style) gets it too.
2. `SetGuestStatus(null)` sets the status to `Guest` with **no host**, so the pawn is no longer a
   prisoner, and clears `slaveFaction`. Then:
   - `health.surgeryBills.Clear()`;
   - `ownership.Notify_ChangedGuestStatus()` **unclaims the prison bed**;
   - `Ideo?.Notify_MemberGuestStatusChanged`;
   - the map's pawn registry and attack-target cache are updated.
3. `SetFaction(OfPlayer)`:
   - **`ChangeKind(basicMemberKind)`** (T-112), which ends any kind flag, `preventIdeo` included;
   - the lord is told `ChangedFaction`;
   - `workSettings.EnableAndInitialize()`;
   - surgery bills cleared again, medical care reset;
   - `ClearMind_NewTemp(ifLayingKeepLaying: true)`: jobs stop, a patient in bed stays in bed;
   - needs recomputed, relations notified, colonist bar dirtied, population records updated.
4. `Recruit` ends with `guest.Notify_PawnRecruited()`, which nulls `slaveFaction` again.

**Left behind, inert:** `resistance`, `will`, `interactionMode`, `recruitable`,
`ideoForConversion` and `everEnslaved` keep their values on the tracker. `SetGuestStatus` resets
none of them for a non-prisoner. A later re-capture re-rolls resistance and will from the new kind
[V]. That nothing reads the rest for a free colonist is **[I]**.

**Through #142's routes.** Route C refuses `SetFaction(OfPlayer)`, `SetGuestStatus(Slave)`,
`SetIdeo` and `IdeoConversionAttempt` for a *marked* pawn. So J1 and J2 must remove the marker
**first**, inside the same call, and then write the faith and join. Route B closes only warden modes,
the Convert ability, the convertee slot and slaver stock. It never touches the Operations tab or
the behaviorist station, so neither J1's bill nor J2's station needs an exception in B.

### Faith

`SetFaction` does not write a faith. A Glitterite joining with a null `Ideo` keeps it until the next
load. Then `Pawn_IdeoTracker.ExposeData` logs *"did not have an ideo set; assigning fallback ideo"*
and calls `SetIdeo(FallbackIdeo())`, now the **player faction's primary** faith (`FallbackIdeo`
takes `pawn.Faction.ideos.PrimaryIdeo`) [V]. The routes that write it deliberately, all through
`Pawn_IdeoTracker.SetIdeo`, which rolls a fresh certainty [V]:
- **the player's primary faith**, which is what the fallback would have done, minus the warning;
- **the operator's faith** (`billDoer.Ideo`, which J1's `ApplyOnPawn` receives). That lever is
  specific to this fiction: *it believes what the one who freed it believes*;
- **none**. The pawn stays faithless until load, and then gets the fallback.

**A player-chosen faith needs a dialog, and a dialog is not synced.** If the story wants the player
to pick, the choice must travel as a synced command; the awakening letter's `MakeChoices` is the
shipped pattern for that.

### Constraints

- **T-163 — the marker gene's category decides who carries it.** A `VREA_Hardware` gene with
  `isCoreComponent true` is locked onto every player-built android. A `VREA_Subroutine` gene is
  offered in the creation window. A plain gene is invisible to both windows, and then J2 and J3a
  cannot remove it.
- **T-164 — android surgery never fails, and it is Crafting work.**
- **A basic Glitterite can awaken in its cell.** `Gene_SyntheticBody.TickInterval` rolls every
  2500 ticks (50%) on any non-awakened android lacking `VREA_AntiAwakeningProtocols`: mood ≤ 0.05
  awakens it and sends it berserk, mood ≥ 0.8 awakens it with an inspiration [V]. Awakening changes
  no faction, but it hands back the name and personality the jailbreak is meant to give. The
  Glitterite xenotype should carry `VREA_AntiAwakeningProtocols`. That gene is a non-core subroutine,
  so the station can remove it, which J3a's players would find.
- **A kind is not a marker** (T-112). The Glitterite kind ends at the join, so everything
  kind-scoped ends with it.
- **The jailbroken android is an ordinary android.** Psylinks follow *Psylinks — verdict and routes*
  above, not the Glitterite rule.

### Available mechanisms

- **VRE – Android** (`2975771801/1.6/Assemblies/VREAndroids.dll`, `ilspycmd -t`) [V]:
  - `Building_AndroidBehavioristStation` (`CanAcceptPawn`, `TryAcceptPawn`, `ReadyForModifying`,
    `FinishAndroidProject`), `Window_AndroidModification`, `Window_CreateAndroidBase` (constructor
    seeding, toggle predicate, `GeneValidator`, `disableAndroidHardwareLimitation`),
    `WorkGiver_CarryToAndroidBehavioristStation`, `WorkGiver_ModifyAndroid`,
    `JobDriver_ModifyAndroid`;
  - `Gene_SyntheticBody.TickInterval` / `.Awaken`, `ChoiceLetter_AndroidAwakened`,
    `PawnGenerator_TryGenerateNewPawnInternal_Patch`;
  - `Utils.IsAndroid` / `IsAwakened` / `CanBeRemovedFromAndroid(Awakened)` / `RecipeForAndroid`;
  - `Recipe_InstallAndroidPart`, `Recipe_InstallReactor`, `Recipe_Surgery_CheckSurgeryFail_Patch`,
    `WorkGiver_DoBill_ThingIsUsableBillGiver_Patch`, `HealthCardUtility_CreateSurgeryBill_Patch`,
    `RecipeWorker_AvailableOnNow_Patch`;
  - defs: `WorkGivers.xml`, `GeneDefs.xml`, `Hediffs_BodyParts_Android(_Bases).xml`.
- **Vanilla 1.6** [V]: `ITab_Pawn_Health.ShouldAllowOperations`, `Recipe_GhoulInfusion`,
  `Recipe_RemoveHediff`, `Bill_Medical.Notify_IterationCompleted`, `BillStack.Delete`,
  `WorkGiver_CarryToBuilding`, `Building_Enterable.SelectPawn`, `RecruitUtility.Recruit`,
  `Pawn.SetFaction`, `Pawn_GuestTracker.SetGuestStatus` / `.Notify_PawnRecruited`,
  `Pawn_Ownership.Notify_ChangedGuestStatus`, `Pawn_IdeoTracker.SetIdeo` / `.FallbackIdeo`,
  `RitualRolePrisoner`, `CompPsylinkable`, `PreceptDef AnimaTreeLinking`.
- **Multiplayer** (`Multiplayer.dll`) [V]: `SyncMethod.Register(HealthCardUtility,
  "CreateSurgeryBill")`, `BillStack.AddBill`, the `Dialog_BeginRitual` sync worker.
  **MP Compat** `Multiplayer.Compat.VanillaRacesAndroid` (loaded `1629973374/1.6`) [V]: the
  modification window, `TryAcceptPawn`, the station lambdas, `MakeChoices`, the default letter
  choice.
- **Precedents.**
  - VRE Archon (`3067715093`): `VREArchon_KidnappedPawnsTracker_Kidnap_Patch` calls
    `SetXenotype(VRE_Archon)` on a kidnapped pawn, and the join is then vanilla's (`rescueesCanJoin`)
    [V]. That is J3's two-step shape: transform, then let an ordinary path join.
  - Ghoul infusion is J1's one-step shape.
- **Wide pass.** Both roots, `-g '!**/obj/**' -g '!**/Referenced/**'`, `-i`.
  - ASCII: `jailbreak`, `reprogram` → 0; `awaken` → VRE – Android and MP Compat only.
  - Null-interleaved UTF-16, typed literally: `awaken` → the same two; `reprogram` → VRE – Android;
    `jailbreak` → Worksites Expanded's `OpportunityCatalog`, a text-adventure ending, not a
    mechanism [V].
  - XML: `jailbreak|reprogram` → labels only.
  - Every 1.6 assembly overriding `ApplyOnPawn` was decompiled and checked for `SetFaction` /
    `RecruitUtility`. Ushanka's Hacking Expansion, VME, VFE Pirates, VFE Insectoids 2 and Ushanka's
    Glittertech Expansion: none joins a pawn from a recipe. The Hacking Expansion's
    `Ability_HijackSubcore` takes mechs and drones only.
  - Validators: `VREAndroids.dll` returns for `ApplyOnPawn` (ASCII) and for `VREA` (UTF-16).
  - **No mod ships a jailbreak, a recruiting surgery or a prisoner awakening.**

### Status

- **Verified [V]:** every seam above; the guest-state sequence; that the station and awakening reach
  a pawn not made at the creation station; that the station as shipped cannot awaken, consume or
  join; T-163, T-164.
- **Inferred [I]:** that the seams compose into each route; the awakening letter's reach at a
  prisoner; that the stale guest fields are never read; the hidden-precept reach for J4.
- **Refines #142 (not a reversal):** #142's *"stripping it [at the station] IS the jailbreak"* holds
  only for J3a. That removes the marker and leaves an unmarked prisoner of the Glitterite faction.
  It does not consume, awaken or join.

### Open questions

1. **Story — Conrad.**
   - *Turn* or *open*? J1/J2 hand the player a colonist; J3 hands the player a prisoner who can now
     be recruited, enslaved or converted.
   - Can a jailbreak fail? As shipped it cannot (T-164).
   - Which faith does it wake into: the colony's, its operator's, or none until load?
   - Does a jailbroken Glitterite stay recognisable to the story — to TRACE's pursuit, or to later
     beats? The marker is gone by construction, so that needs a second, non-gating record.
2. **Requirement — `docs/requirements/GLITTERTECH.md`'s owner.** The requirement says "may become an
   ordinary android colonist" but not whether it arrives **awakened** (traits, joy, mental breaks,
   skill gain) or **basic** (VRE's player-built default). "Given back the persona and free will"
   reads as awakened.
3. **Build — #119.**
   - Which of #142's marker shapes, now constrained by T-163.
   - Awaken before or after the join.
   - `Recruit` versus a bare `SetFaction`.
   - A research gate on the recipe.
   - Hiding the marker from the creation window.
   - `VREA_AntiAwakeningProtocols` on the Glitterite xenotype (part of the unticketed Glitterite
     defs rewrite #142 named).

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
| **Xenotype on `Human`** *(what ships)* | Counts as a colonist everywhere vanilla counts colonists. Holds an `Ideo`, so **Devotion works with no new code**. Cannot take psycasts *as shipped* — two XML-reachable gates, see *Psylinks — verdict and routes*. Awakening is a shipped, authored transition. |
| PawnKind / faction-member only | Would make androids NPC-only and delete the capability the requirement asks for. Rejected. |
| Mechanoid-adjacent (`Building_MechGestator` path) | Produces a **mechanitor-bonded mech**, not a colonist — no `Ideo`, no Devotion, no backstory, no social tab. Wrong shape for a campaign about personhood. |

**Recommend the shipped shape — xenotype on `Human`.** It is the only one of the three
that lets the campaign make its argument, because the argument is precisely that an
android is a person; a mechanoid-adjacent android would concede the Glitterite position in
the mechanics while the text denied it.

**Psycasts: androids cannot hold a psylink *as shipped*, and the block is two XML-reachable gates,
not one unconditional prefix.** Corrected by
[#141](https://github.com/cjd721/Rimworld-Archinity/issues/141); the mechanism, the routes and the
weights are in *Psylinks — verdict and routes* above.

> **Superseded — the two sentences #78 left here were wrong in both halves.** It said
> `VREAndroids.Hediff_Psylink_ChangeLevel_Patch` was "the whole block, and it is unconditional",
> and that `VREA_PsychicallyDeaf` was deselectable. The prefix is declared on
> `Hediff_Psylink.ChangeLevel(**int**)` only — the one-argument override, which no ritual grant
> path calls — and `VREA_PsychicallyDeaf` inherits `isCoreComponent true` from `VREA_HardwareBase`,
> so the creation window refuses to un-toggle it. **[V]** The real gates are
> `Pawn_HealthTracker_AddHediff_Patch` reading an XML list behind `VREA_SyntheticImmunity`, and
> vanilla's own
> `PsychicSensitivity` test — the first keyed on `VREA_SyntheticImmunity`, the second on
> `VREA_PsychicallyDeaf`, and neither gene appears in the other's path. **There is an XML edit that
> buys an android a psylink; there are two, and you need both.**

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
- **Verified** — androids are a Biotech xenotype on race `Human`; they are colonists and they
  hold an `Ideo`. **[V]**
- **Verified, and it replaces #78's claim** — androids cannot hold a psylink *as shipped*, and the
  refusal is two **independent** gates keyed on two different genes: `VREA_SyntheticImmunity` gates
  `Pawn_HealthTracker_AddHediff_Patch`'s deferral to `AndroidCanCatch`, which reads the
  `androidsShouldNotReceiveHediffs` list; `VREA_PsychicallyDeaf`'s `PsychicSensitivity` factor of 0
  meets vanilla's own `< float.Epsilon` tests. Both are reachable from XML; neither gene appears in
  the other's path. #78's "unconditional prefix" was wrong. **[V]** —
  [#141](https://github.com/cjd721/Rimworld-Archinity/issues/141).
- **Proposed** — routes A–D for lifting that refusal. The mechanisms each composes are **[V]**;
  that they compose into a psycasting android is **[I]** until built.
- **Proposed** — the Analysis gate on `VREA_AndroidTech`. The mechanism is #67's and is
  **[V]**; its application here is **[I]**.
- **Proposed, and a fiction call** — scoping the outlander/pirate xenotype bleed.
- **Struck** — the per-unit Intel debit (§5; [`CURRENCIES.md`](CURRENCIES.md) § *What changes it*).

Evidence class **READ**: settled by the 1.6 defs of `2975771801`, its decompiled
`1.6/Assemblies/VREAndroids.dll`, the decompiled
`1629973374/1.6/Assemblies/Multiplayer_Compat.dll`, vanilla `Assembly-CSharp` and vanilla
Biotech defs, plus a two-root two-encoding wide pass validated against known positives.
The psylink section adds a full decompile of vanilla `Assembly-CSharp`, `2842502659`'s
`1.6/Assemblies/VanillaPsycastsExpanded.dll`, and vanilla Royalty/Core hediff and meditation-focus
defs. Nothing here needed the game launched.

Established by [#78](https://github.com/cjd721/Rimworld-Archinity/issues/78) and
[#141](https://github.com/cjd721/Rimworld-Archinity/issues/141).

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

**Settled by reading** — the manufacture chain, the xenotype shape, the persistence, the MP Compat
coverage, the hardcoded ingredient list, the faction-patch bleed and our own factions' immunity to
it. The **psylink block is settled by reading too, and differently from what #78 recorded**: two
independent gates keyed on two different genes — `VREA_SyntheticImmunity` on the hediff,
`VREA_PsychicallyDeaf` on the stat — both XML-reachable, anchored in
*Psylinks — verdict and routes*. Paths and anchors are cited above.

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

3. **Whether androids take psycasts is now a choice, not an engine fact.** *(Rewritten by
   [#141](https://github.com/cjd721/Rimworld-Archinity/issues/141); #78's "permanently, and cannot
   be patched away" is struck.)* The refusal is two independent gates — `VREA_SyntheticImmunity`
   on the hediff, `VREA_PsychicallyDeaf` on the stat — both XML-reachable, and four routes lift
   them — see *Psylinks — verdict and routes*. What the campaign must decide is no longer *can we*
   but **which androids, and at what price**: route A makes every android sensitive and makes the
   gene's own description a lie; route B makes it a per-unit build that costs synthetic immunity.
   Leaving it alone (route E) keeps the asymmetry as a *stated* cost of an artificial body, which
   remains a defensible reading — but it is now an authorial choice against
   *"the campaign does not treat artificial bodies as inherently inferior,"* not a constraint the
   engine imposes. Handed to `docs/requirements/GLITTERTECH.md`'s owner. It still has implications
   for `docs/specs/TRANSCENDENCE.md` if the endgame assumes any colonist can be a psycaster —
   those implications are now satisfiable.

4. **Resolved: an android costs no Intel per unit.** Intel is exchanged for Instruction items,
   and [`CURRENCIES.md`](CURRENCIES.md) admits no other debit (§5). Whether `VREA_AndroidTech`
   also requires an Instruction item bought with Intel is exchange-catalogue authoring, owned by
   [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117).

5. **Does the campaign want the per-android material cost changed?** It cannot be done in XML
   (the list is a C# literal). If Ultra manufacture should cost a Glitterite material rather
   than Uranium, that is a ~15-line Harmony postfix on
   `Window_AndroidCreation.OnGenesChanged` and should be decided before the Ultra chapter is
   priced.
