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
before any level arithmetic **[V]**. Bears on `docs/specs/RELIGION.md` §4's Church-title
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

## Multiplayer

`Multiplayer.Compat.VanillaRacesAndroid` (`[MpCompatFor("vanillaracesexpanded.android")]`)
and `Multiplayer.Compat.VanillaPsycastsExpanded` (`[MpCompatFor("VanillaExpanded.VPsycastsE")]`)
are both in `1629973374/1.6/Assemblies/Multiplayer_Compat.dll` — the loaded assembly, not
`Referenced/` **[V]**. The VPE class registers `MP.RegisterSyncMethod` on
`VanillaPsycastsExpanded.Hediff_PsycastAbilities` for `SpentPoints`, `ImproveStats`,
`UnlockPath`, `UnlockMeditationFocus` and `GainExperience`, plus sync workers for the
psyset dialogs **[V]** — everything a psycasting pawn then does.
