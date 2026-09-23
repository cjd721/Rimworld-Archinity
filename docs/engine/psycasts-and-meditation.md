# Psycasts and meditation

What gates a psylink, what gates a meditation focus, and the two mod stacks that sit
on top of both.

Verified against decompiled RimWorld 1.6.4871 unless an entry says otherwise. These
are *verified available mechanisms*, not commitments to use them — selection happens
in `docs/specs/`.

Established on [#141](https://github.com/cjd721/Rimworld-Archinity/issues/141); the
system built on them is `docs/specs/ANDROIDS.md` § *Psylinks — verdict and routes*.

---

## A meditation focus's backstory gate has exactly one XML bypass

`CompPsylinkable.CanPsylink` requires `Props.requiredFocus.CanPawnUse(pawn)` **[V]**.
Vanilla's `MeditationFocusDef Natural` — the anima tree's focus — declares
`requiredBackstoriesAny` of `Tribal` / `AdultTribal` / `ChildTribal` in the **Childhood**
slot **[V]**, and `MeditationFocusTypeAvailabilityCache.PawnCanUseInt` returns `false`
when a focus with a non-empty `requiredBackstoriesAny` matches nothing **[V]**.

**So the anima tree is closed to any modded pawn kind with its own backstory
categories** — VRE – Android's backstories declare only `AwakenedAndroid` and
`ColonyAndroid` **[V]** — and it would be closed even if no mod patched anything. The
failure is silent; that half is **T-27**.

**The bypass is XML and vanilla's own.** `PawnCanUseInt` returns `true` if **any hediff
on the pawn** lists the focus in `HediffDef.allowedMeditationFocusTypes` **[V]**. Give
a carried hediff `Natural` and the pawn can take the linking ritual.

VRE – Android adds a second, mod-side gate on the same method:
`MeditationFocusTypeAvailabilityCache_PawnCanUseInt_Patch` forces `false` for any pawn
with `VREA_JoyDisabled` — every non-awakened android **[V]**. That gene carries
`removeWhenAwakened true` **[V]**, and `Gene_SyntheticBody` calls
`MeditationFocusTypeAvailabilityCache.ClearFor(pawn)` so the cache does not keep the
stale `false` **[V]**.

## Bestowing a title on a psylink-blocked pawn throws, and `maxPsylinkLevel` does not prevent it

**Loud, not silent — it NREs and logs, which is why it is here and not in the
register.**

With Vanilla Psycasts Expanded and Royalty both running:
`VanillaPsycastsExpanded.RitualOutcomeEffectWorker_Bestowing_Apply_Patch` transpiles
vanilla's psylink loop out of `RitualOutcomeEffectWorker_Bestowing.Apply` and replaces
it with `ApplyTitlePsylink`, whose null branch calls
`PawnUtility.ChangePsylinkLevel(pawn, 1, false)` and then **immediately dereferences
`pawn.Psycasts()`** **[V]**.

Any mod that refuses the `PsychicAmplifier` hediff leaves that dereference null —
`Psycasts()` is `hediffSet.GetFirstHediffOfDef(VPE_PsycastAbilityImplant)` **[V]** — and
the next line throws **inside a ritual outcome**. VRE – Android does exactly that for
androids (below).

**Zeroing `maxPsylinkLevel` on the title does not avoid it**: the null branch runs
before any level arithmetic **[V]**. Bears on `docs/specs/RELIGION.md` § *The build — Exaltation* › *4. Exaltation, and the rite*'s Church-title
design wherever an android could be the honoree.

## VRE – Android's two psychic gates are independent, and each does nothing alone

Both **[V]**, from `2975771801/1.6/Assemblies/VREAndroids.dll` and the mod's own defs.

- **Gate 1 — the hediff.** `VREAndroids.Pawn_HealthTracker_AddHediff_Patch.HandleHediffForAndroid`
  tests `pawn.HasActiveGene(VREA_SyntheticImmunity)` before it will defer to
  `Utils.AndroidCanCatch`, and `AndroidCanCatch` is what reads
  `VREA_AndroidSettings.androidsShouldNotReceiveHediffs`, where `PsychicAmplifier` sits.
  `AndroidCanCatch` consults, in order: a `VREAndroids.AndroidSettingsExtension` on the
  hediff def (`androidCanCatchIt`), the `"Sterilized"` tag, the settings list, then a
  class / `chronic` / `Immunizable` / `makesSickThought` battery.
- **Gate 2 — the sensitivity.** `VREA_PsychicallyDeaf` carries
  `<statFactors><PsychicSensitivity>0</PsychicSensitivity></statFactors>`, which meets
  vanilla's own `PsychicSensitivity < float.Epsilon` tests in `RimWorld.Psycast.GizmoDisabled`
  and `RimWorld.Verb_CastPsycast.ValidateTarget`. No Harmony patch is involved on this side.

**`AndroidCanCatch` never reads `VREA_PsychicallyDeaf`; vanilla's sensitivity tests never
read `VREA_SyntheticImmunity`** **[V]**. Lifting either alone gets nothing: gate 1 alone
yields an android holding a psylink level and a psycast gizmo it can never press; gate 2
alone yields a psychically sensitive android that can never be given the hediff.

Both `VREA_SyntheticImmunity` and `VREA_PsychicallyDeaf` are `ParentName="VREA_HardwareBase"`
and inherit `isCoreComponent true` with no `removeWhenAwakened`, so **neither is
deselectable in either creation window** — the `disableAndroidHardwareLimitation` escape
needs `CanBeRemovedFromAndroidAwakened()` **[V]**. This corrects
[#78](https://github.com/cjd721/Rimworld-Archinity/issues/78), whose conclusion was right
and whose stated reason was wrong in both halves.

## Third-party android hardware is pure XML

VRE – Android registers as an android gene **any `GeneDef` in the database** whose
`displayCategory` is `VREA_Hardware` or `VREA_Subroutine`:
`GeneDefGenerator_ImpliedGeneDefs_Patch.Postfix` iterates
`DefDatabase<GeneDef>.AllDefsListForReading` and calls `AddAndroidGene` on every match
**[V]**. So a named, in-fiction hardware component authored by us appears in the creation
window with no code. That such a gene composes into a working psychic android is **[I]**.

## What a VPE path lock actually gates

From `2842502659/1.6/Assemblies/VanillaPsycastsExpanded.dll`, on
[#162](https://github.com/cjd721/Rimworld-Archinity/issues/162). All **[V]**.

- **`PsycasterPathDef.CanPawnUnlock` is `virtual`.** It is the AND of five conditions:
  - `requiredBackstoriesAny`;
  - `requiredMeme`;
  - `requiredGene`, which must be present and `Active`;
  - `requiredMechanitor`;
  - `requiredFocus`, tested through `MeditationFocusDef.CanPawnUse`.

  `lockedReason` is text only.
- **A subclass lands in the base database.** `DefDatabase<T>.AddAllInMods` takes
  `mod.AllDefs.OfType<T>()`, so a subclass def tag lands in `DefDatabase<PsycasterPathDef>` too.
- **Five readers.**
  - The psycast tab's *Unlock* button.
  - `PawnGen_Patch`, for NPC paths.
  - `RecheckPaths`, only under `ensureLockRequirement`.
  - `CompPsytrainer.CanBeUsedBy` and `AbilityExtension_Psycast.IsEnabledForPawn`, only when
    `ignoreLockRestrictionsForNeurotrainers` is false. It **defaults to true**, which is **T-167**.
- **Relocking.** `ensureLockRequirement` rechecks only on `HediffSet.DirtyCache`,
  `Notify_GenesChanged` and `Notify_TemporaryAbilitiesChanged`. A relock parks the path and
  hides its gizmos. It never refunds or removes (**T-168**). With the neurotrainer flag still
  `true`, it parks a psytrainer-opened path at the next recheck, but never reaches a psyring's
  ability.
- **VPE also sells foci for points** (`unlockedMeditationFoci`, admitted by a postfix on
  `PawnCanUseInt`). A `MeditationFocusExtension` with `canBeUnlocked false` stops that.
  So a focus granted only by a hediff stays exclusive to that hediff's carriers.

The founder-only door built on these is `docs/specs/PSYCHIC.md`.

## Where psylink rank is written

From `Assembly-CSharp.dll` 1.6.4871 and `2842502659/1.6/Assemblies/VanillaPsycastsExpanded.dll`,
on [#163](https://github.com/cjd721/Rimworld-Archinity/issues/163). All **[V]**.

**Vanilla** has three shapes of write:
- **Add the hediff at level 1.** This is how every first rank arrives:
  - `CompUseEffect_InstallImplant.DoEffect`;
  - the null branch of `PawnUtility.ChangePsylinkLevel`;
  - `PawnGenerator` for nobles;
  - a gene's hediff, through VEF `GeneExtension.hediffsToBodyParts`.

  A second add of `PsychicAmplifier` merges (`Hediff.TryMergeWith`), and
  `Hediff_Level.TickInterval` resets severity to `level`, so it grants nothing.
- **`Hediff_Psylink.ChangeLevel(int, bool)`**, which `ChangePsylinkLevel` calls directly, and
  `ChangeLevel(int)`, which calls it.
- **A direct `level` write**: `Hediff_Psylink.CopyFrom`, used for Anomaly duplicates, and any
  mod that sets the field.

**VPE** replaces the second shape. Its prefix hands `Hediff_Psylink.ChangeLevel(int, bool)` to
`Hediff_PsycastAbilities.ChangeLevel`, and the virtual `ChangeLevel(int)` override then does
three things:
- sets `points += offset`;
- creates a psylink if there is none;
- writes `psylink.level = level`.

Every VPE rank change after the first passes that override, including:
- XP (`GainExperience` loops `ChangeLevel(1)` while `level < Settings.maxLevel`);
- NPC generation;
- title grants.

The first rank still arrives as an add. VPE's `Hediff_Psylink.PostAdd` postfix then copies it
(`InitializeFromPsylink`, 2 points at level ≤ 1).

**XP has one funnel, `Hediff_PsycastAbilities.GainExperience`.** It is fed by:
- the `GainPsyfocus_NewTemp` postfix (gain × 100 × `XPPerPercent`, recomputed, so the
  psyfocus cap is ignored), whose callers are `JobDriver_Meditate` and
  `Caravan_NeedsTracker.TryGainPsyfocus`. The caravan call covers any psylinked pawn in a
  stopped, non-resting caravan, meditating or not;
- the `OffsetPsyfocusDirectly` postfix (positive offsets) and the `RechargePsyfocus` prefix,
  also through `GainXpFromPsyfocus`. So **every psyfocus gain is XP under VPE**: go-juice,
  persona psychic-kill weapons, the psyfocus-recharge ritual outcome, VRE Sanguophage deathrest
  buildings, and the other feeders listed under R6 in the spec;
- Timeskip Meditation;
- Drain Psyessence;
- VPE-Puppeteer's Ascension;
- the dev button.

`PsycastsMod.ApplySettings` writes `Settings.maxLevel` into `PsychicAmplifier.maxSeverity` at
startup and on every settings save.

The census of every writer, and the routes that close them, are in `docs/specs/PSYCHIC.md`
§ *What raises psylink rank besides the altar*. The obvious vanilla seam is the wrong one
(**T-169**), and the quest pity timer is **T-170**.

## Multiplayer

`Multiplayer.Compat.VanillaRacesAndroid` (`[MpCompatFor("vanillaracesexpanded.android")]`)
and `Multiplayer.Compat.VanillaPsycastsExpanded` (`[MpCompatFor("VanillaExpanded.VPsycastsE")]`)
are both in `1629973374/1.6/Assemblies/Multiplayer_Compat.dll` — the loaded assembly, not
`Referenced/` **[V]**. The VPE class registers `MP.RegisterSyncMethod` on
`VanillaPsycastsExpanded.Hediff_PsycastAbilities` for `SpentPoints`, `ImproveStats`,
`UnlockPath`, `UnlockMeditationFocus` and `GainExperience`, plus sync workers for the
psyset dialogs **[V]** — everything a psycasting pawn then does.
