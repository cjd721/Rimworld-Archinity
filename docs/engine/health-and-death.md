# Health and death

Which code path actually decides that a pawn is dead, what vanilla already ships for
coming back, and which of the engine's three "cannot die" switches is real.

Verified against decompiled RimWorld 1.6.4871 unless an entry says otherwise.
These are *verified available mechanisms*, not commitments to use them —
selection happens in `docs/specs/`.

---

## Death is intercepted on the damage path, not in `ShouldBeDead`

`Pawn_HealthTracker.ShouldBeDead()` contains **no Deathless check at all** [V], and
its first line is `if (Dead) return true;`, which precedes the `preventsDeath` test.
So nothing that reads `ShouldBeDead` is where immortality lives.

`GeneDefOf.Deathless` is instead special-cased at **exactly ten discrete call sites**
[V] — executions, bloodfeeding, surgery, childbirth, the MTB death roll, the
death-on-downed roll, and two UI strings among them. The load-bearing one is the coma
interception below. `Verse.Gene_Deathless` itself holds only
`lastSkillReductionTick` [V]; there is no behaviour on the gene class to copy.

**`Pawn.Kill` is unguarded.** A whole-assembly read finds zero occurrences of
Deathless, `preventsDeath` or the coma anywhere on that path [V]. **Every protection
in the engine is a property of the *damage* path**, so any of our own code calling
`Kill` directly kills an otherwise-unkillable pawn, permanently and with no warning.
Guard at the caller.

## `ShouldBeDeathrestingOrInComaInsteadOfDead` is the interception, and it is reached twice

`RimWorld.SanguophageUtility.ShouldBeDeathrestingOrInComaInsteadOfDead(Pawn)` is a
`public static bool` returning true when Biotech is active, `health.ShouldBeDead()` is
already true, the pawn has an active `GeneDefOf.Deathless`, **and the brain is present,
not missing, with `GetPartHealth(brain) > 0f`** [V].

It is reached from **both** `Pawn_HealthTracker.CheckForStateChange` and
`Pawn_HealthTracker.PostApplyDamage` [V], which is the fact worth knowing outside any
one design: **one postfix covers both entry points.** When it returns true,
`ForceDeathrestOrComa` runs in place of `pawn.Kill` — deathrest if `CanDeathrest()`,
otherwise `TryStartRegenComa`, which adds `HediffDefOf.RegenerationComa`.

## `RegenerationComa` pauses its own countdown while the pawn would be dead

`RegenerationComa` is 420000 ticks, caps Consciousness at `setMax 0.1`, and carries
`HediffComp_DisappearsPausable_LethalInjuries`, whose `Paused` property is literally
`ShouldBeDeathrestingOrInComaInsteadOfDead(Pawn)` [V]. So the timer only runs once the
pawn is no longer in a state that would otherwise be death — vanilla already ships
"death as temporary absence while they recover", built for sanguophages.

**The corollary is the trap in it: a brain-destroyed pawn is paused forever.** The
brain clause makes the interception false, so the pawn dies — and if something else
keeps the interception true while the brain is gone, the countdown never advances and
the pawn is permanently comatose rather than temporarily absent. Any design that
removes the brain clause owes a part-regrowth path.

## `HediffDef.preventsDeath` is a real switch that nothing sets

`preventsDeath` short-circuits `ShouldBeDead()` to false through
`HediffSet.HasPreventsDeath`, ahead of every other check — and it occurs **exactly
twice in the entire 1.6 assembly**: the `HediffDef` field declaration and that one
`HediffSet` read [V]. A sweep for the XML field name across both corpus roots plus
`common/RimWorld/Data/` returns **zero**: it is set by nothing in vanilla, nothing in
the DLC and nothing in the 155-mod corpus [V].

It is therefore a one-field, XML-only "cannot die" that is strictly stronger than
Deathless and has no incumbent. What it does *not* give is a return: no corpse, no
letter, no absence — the pawn simply never dies. That is a different behaviour from
the coma route, not a cheaper version of it.
