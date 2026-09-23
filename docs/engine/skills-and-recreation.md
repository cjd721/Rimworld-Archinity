# Skills and recreation

How a skill record and its passion are stored and changed, and how a pawn picks its recreation —
the two halves a passion-keyed system of ours sits between.

Verified against decompiled RimWorld 1.6.4871 unless an entry says otherwise.
These are *verified available mechanisms*, not commitments to use them —
selection happens in `docs/specs/`.

---

## Skills and passions

`SkillRecord` scribes `def`, `level`, `xpSinceLastLevel`, `passion` and `xpSinceMidnight`.
`Passion : byte` is `None` / `Minor` / `Major`, and `LearnRateFactor` switches 0.35 / 1 / 1.5 and
**throws on anything else** [V].

- **There is no level-up event.** `Learn` increments `levelInt` inline, records a tale at 14 and
  throws a mote. Levels are also written by the `Level` setter, `EnsureMinLevelWithMargin` and
  generation. `Interval` decays skill above level 10 [V].
- **Generation order.** `PawnGenerator.TryGenerateNewPawnInternal` runs `GenerateTraits` →
  `GenerateSkills`. `GenerateSkills` forces passions for traits with `forcedPassions`, then hands
  passions out by descending skill level [V].
- **Passion is not static mid-game.** Biotech `GeneDef.passionMod` (`AddOneLevel`, `DropAll`) and
  growth moments change it [V]. A rule keyed on `passion` should read it live.
- **No mod on disk adds passion values** — no `*PassionDef` XML tag, and Vanilla Skills Expanded is
  absent by `About.xml` sweep [V]. VFE Medieval 2's `HediffComp_LearningPassionsModifier` changes
  the learning *rate* only, through a `SkillRecord` patch [V].
- Recreation XP is ordinary `SkillRecord.Learn` XP (below) [V].

From [#156](https://github.com/cjd721/Rimworld-Archinity/issues/156)
(`docs/specs/SPECIALISATION.md`) and [#159](https://github.com/cjd721/Rimworld-Archinity/issues/159)
(`docs/specs/COLONY.md` § *Recreation follows a pawn's passions*).

## How a pawn picks recreation

`ThinkNode_Priority_GetJoy` decides *when*: the timetable plus the joy level.
`JobGiver_GetJoy.TryGiveJob` decides *what* [V]:

- For each `JoyGiverDef` it computes `Worker.GetChance(pawn) × max(0.001, (1 − tol)⁵)`, after the
  gates: `JoyGiverAllowed`, bored, `CanBeGivenTo`, and per-pawn `pctPawnsEverDo` seeded on
  `thingIDNumber`. It then does `TryRandomElementByWeight`, zeroing the weight and redrawing on
  failure.
- **`JoyGiver.GetChance` is the only per-pawn weight hook.** The base returns `def.baseChance`.
  Vanilla overrides it in Skygaze (calls base) and TakeDrug (trait-weighted, no base call). Knick
  Knacks (`3595196942`) ships a postfix on it, so the shape composes.
- Inside a giver, the thing is the closest reachable building (`JoyGiver_InteractBuilding`) or a
  random outcome-providing book (`BookUtility.TryGetRandomBookToRead`).
- Skill experience comes from `JobDef.joySkill` in `JoyUtility.JoyTickCheckEnd`. VFE Furniture's
  `ExtendedSitFacingJoyDataExtension.extraJoySkill` is a building-keyed second skill.
- `JobGiver_GetJoy` is placed in Humanlike, four `SubTrees_Misc` sites and five gathering duties.
  `IdleJoy`, `GetJoyInBed` and `GetJoyInGatheringArea` change only the gates and dispatch.
- **Passion is read nowhere in the chain.** The passion-weighted vanilla donor is
  `InspirationWorker.CommonalityFor` (×1 / ×2.5 / ×5 over `associatedSkills`).
- Worksites Expanded picks its worksite pawns' recreation outside this chain entirely (**T-159**).

**Boredom sits ahead of every weight (working as designed).** The gate skips any `JoyGiverDef`
whose `joyKind` is `BoredOf`: tolerance above 0.5, cleared only below 0.3
(`JoyToleranceSet.Notify_JoyGained`). This happens before `GetChance` is consulted, and the chance
is then scaled by `max(0.001, (1 − tol)⁵)`. So a preference factor of any size lapses once the
pawn is bored of that joy kind. Tolerance is per joy kind, not per game, and vanilla's three
Shooting games share `Gaming_Dexterity`, so they bore together [V].

From [#159](https://github.com/cjd721/Rimworld-Archinity/issues/159), `docs/specs/COLONY.md` §
*Recreation follows a pawn's passions*.
