# Specialisation

## Purpose and scope

Answers [`docs/requirements/COLONY.md`](../requirements/COLONY.md) § *A pawn can advance within
a skill*:

- a pawn specialises inside a skill it already has, on the same skill and the same experience;
- the player chooses the advance, at intervals as the skill rises;
- only skills the pawn is deeply passionate about can be specialised;
- each advance is small and numeric, and none unlocks content;
- pawns the player did not train arrive already specialised.

The requirement allows the same commitment to be delivered **by scarcity instead of by
progression**, through bounded named posts. Both shapes are answered here as peers.

Established by [#156](https://github.com/cjd721/Rimworld-Archinity/issues/156). The Ideology
role facts are cited from [#114](https://github.com/cjd721/Rimworld-Archinity/issues/114), not
re-derived. Selecting a route is [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.

**Where adjacent systems take over.**

- Recreation that trains a passion skill: `COLONY.md` § *Recreation follows a pawn's passions*
  ([#159](https://github.com/cjd721/Rimworld-Archinity/issues/159)). It shares this document's
  passion facts; see *Constraints*.
- Granting or changing a passion: the altar (`ALTAR.md`). Passion-granting is reserved to it
  (`docs/playtest-notes.md`, restated on [#76](https://github.com/cjd721/Rimworld-Archinity/issues/76)).
- The player faith's role catalogue and unlock milestones:
  [#116](https://github.com/cjd721/Rimworld-Archinity/issues/116) and `RELIGION.md`.

## Verdict

- **Possible? Yes, but only through a system of ours.** Nothing on disk carries per-pawn
  specialisation inside a skill [V]. Every clause can be met by our own code, on seams that
  exist. No XML-only route meets every clause: vanilla roles and trained hediffs deliver the
  commitment but not "earned by use and gated by passion", and roles cannot arrive on a
  generated pawn.
- **Multiplayer? With work.** The trigger (skill experience) and the pre-specialisation of
  generated pawns both run in simulation. The player's pick must be a synced command. Every
  shipped precedent does this through a sync method that MP Compat registers [V]. Archinity
  registers none of its own today. The role route rides vanilla paths that Multiplayer already
  syncs, subject to #114's one RUN check.

## Routes

Routes A–D are the **player-chosen progression** family. They share one skeleton: per-pawn state,
a trigger on skill level, stat application, a synced pick, and a generation hook. They differ in
the **shape of the choice**: a flat list, a branching tree, a catalogue with coded effects, or a
point board. They compose, so one build could take A's catalogue and D's board. They are listed
separately because each has its own donor and gives the story different levers.

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **A. Expertise list** | At skill thresholds on a major-passion skill, the player picks one entry from that skill's list: *weaponsmithing*, *armoursmithing*, *gourmet cooking*. Each entry is a def naming a skill and its stat offsets | ours. Schema donor: Vanilla Skills Expanded's `ExpertiseDef`, not on disk | C# + XML catalogue | **Hard** | With work (a synced pick) |
| **B. Path tree** | Each skill forks into exclusive branches, each with ordered tiers and prerequisites. Taking *weapons* closes *armour*. Branch access is gated in XML | ours. Architecture donor: Vanilla Psycasts Expanded | C# + XML catalogue | **Hard** | With work |
| **C. Perk catalogue with workers** | As A, but an entry can also carry a worker class, so an advance can do what a stat offset cannot, such as a yield bonus on one recipe | ours. Shape donor: VFE Classical `PerkDef` / `PerkWorker` | C# + XML catalogue | **Hard** | With work |
| **D. Point board** | Points accrue per pawn as passion skills rise. The player spends them on a board that shows every option at once, with the unspent total as an alert | ours. UI donor: VFE Tribals' cornerstone window | C# + XML catalogue | **Hard** | With work. The donor's sync shape is proven |
| **E. Specialist posts (Ideology roles)** | Named posts carrying stat and quality offsets and an ability, gated on skill level. **Scarcity, not progression** | vanilla `Precept_Role`. Our injection or a reform adds the posts to the player faith (#114) | XML · XML + C# | **Easy** (reform-added: **at most two** multi-holder post types, see below) · **Medium** (injected past the cap, passion-gated, bounded) | Yes, per #114, with one RUN check |
| **F. Trained hediff at a bench or a rite** | "Trained as a weaponsmith" is a permanent hediff carrying stat offsets. It is acquired by a surgery bill, a usable bench or a rite, removed at a cost, and exclusive by tag | vanilla `HediffDef` + `Recipe_AddHediff` / `CompUseEffect_AddHediff`. A rite needs our outcome worker | XML · XML + C# | **Easy** (ungated) · **Medium** (skill- and passion-gated, rite, skill-keyed generation) | Yes for the XML form [I] |
| **G. Trait** | The same as F, held as a trait: stat offsets, skill gains, and a passion link that vanilla already understands | vanilla `TraitDef`. Mid-game granting needs our code | XML + C# | **Medium** | Yes [I] |

**Not a route: Vanilla Psycasts Expanded as the carrier.** Authoring skill specialisations as
psycaster paths would need every specialist to hold a psylink. `Hediff_PsycastAbilities` is
initialised from one (`InitializeFromPsylink`). Its currency is its own `experience`
(`GainExperience`), not skill XP [V]. It would also take over the psychic track the campaign
already uses. **Not recommended.**

### A. Expertise list

**What it gets us.**
- The exact shape the requirement describes. `ExpertiseDef` is `defName`, `label`,
  `description`, `<skill>` and `<statOffsets>` [V, the 1.6 payload XML]. A catalogue per skill is
  plain XML, and so is adding an entry.
- **The fork in the smith example is a catalogue choice**: two entries on Crafting, pointed at
  two different stats (see *Constraints* for why the stats must be new).
- The shipped content shows what one advance is sized at: `0.01` to `0.05` on one stat per entry
  (`VCE_GourmetChef`, `VCEF_Swiftcasting`, `VGE_GravshipResearch`) [V].
- Generated pawns can arrive holding entries (see *Generated pawns*).

**What it cannot do.**
- **It cannot reuse the content on disk.** All eight 1.6 `ExpertiseDef`s load only when Vanilla
  Skills Expanded is active [V]:
  - Vanilla Cooking Expanded and Vanilla Gravship Expanded gate the folder with
    `IfModActive="vanillaexpanded.skills"` in `loadFolders.xml`.
  - Vanilla Fishing Expanded wraps its entries in `PatchOperationFindMod` on
    "Vanilla Skills Expanded".

  They also target those mods' own stats. **The donor is the schema, not the content.**
- There is no tree and no exclusivity, unless the catalogue adds a tag.

**Consequences.**
- It is a new per-pawn system: state, a trigger, stat application, a pick UI and a synced
  command. That is why it is Hard, and it is the lightest Hard of A–D.
- **Name our def type in our own namespace.** A class called `VSE.Expertise.ExpertiseDef` would
  collide if Vanilla Skills Expanded were ever installed [I].
- MP Compat's `VanillaSkillsExpanded` class shows how the original was synced
  [V, `1629973374/1.6/Assemblies/Multiplayer_Compat.dll`]:
  - `ExpertiseTracker.AddExpertise` is registered as a sync method;
  - `ClearExpertise` is registered debug-only;
  - a sync worker finds the tracker through a static `VSE.ExpertiseTrackers.trackers`
    dictionary keyed by `Pawn_SkillTracker`.

  That is the sync surface this route would have: one synced "take this entry" call per pick.

### B. Path tree

**What it gets us.**
- **Commitment made visible as structure.** A branch taken closes its sibling. That is the
  requirement's "a pawn cannot specialise in everything" drawn as a tree.
- VPE's architecture is the precedent [V, `2842502659/1.6/Assemblies/VanillaPsycastsExpanded.dll`]:
  - state lives on a hediff, `Hediff_PsycastAbilities`, which scribes `points`, `experience`,
    `unlockedPaths` and `previousUnlockedPaths`;
  - points come from levels (`ChangeLevel` adds to `points`), and `UnlockPath`, `SpentPoints` and
    `ImproveStats` spend them.
- **Branch gating in XML.** `PsycasterPathDef` is gated by XML fields alone, and
  `ensureLockRequirement` re-evaluates access as conditions change [V, `docs/data/PARTS-BIN.md`
  § 9.2]. Four other mods ship paths, so the family is extensible in XML
  [inherited from the ticket, I].
- **Proven sync surface.** MP Compat registers `SpentPoints`, `ImproveStats`, `UnlockPath`,
  `UnlockMeditationFocus` and `GainExperience` as sync methods on `Hediff_PsycastAbilities`
  [V, `Multiplayer.Compat.VanillaPsycastsExpanded`].
- **It is also the generation donor**: see *Generated pawns*.

**What it cannot do.**
- `PsycasterPathDef`'s gates name genes, memes, meditation foci, mechanitor status and
  backstories. **None names a skill or a passion** [V, PARTS-BIN § 9.2]. A skill-gated branch is
  a field of ours.
- A tree needs a tree UI. VPE's is its psycast tab, which is not reusable for skills [I].

**Consequences.**
- It is the heaviest of A–D in UI.
- State held on a hediff inherits **T-113**: an Anomaly duplicate copies it unless the def sets
  `duplicationAllowed` false.

### C. Perk catalogue with workers

**What it gets us.**
- **Advances beyond a stat offset.** `VFEC.Perks.PerkDef` carries `statOffsets`, `statFactors`,
  a `workerClass` and a `tickerType`. `PerkWorker` supplies Harmony patches of its own
  (`GetPatches`), and the manager runs per-ticker lists [V, `2787850474/1.6/Assemblies/VFEC.dll`].
- So "+5% yield on armour recipes" can be a worker, not a stat nobody reads.
- **The stat application is the shipped pattern.** `PerkPatches` postfixes
  `StatWorker.GetValueUnfinalized` and `GetExplanationUnfinalized` [V]. VFE Tribals' cornerstones
  use the same pair (`RESEARCH.md`).

**What it cannot do.**
- As shipped it is **colony-wide**: `GameComponent_PerkManager.ActivePerks` is one
  `HashSet<PerkDef>` [V]. Per-pawn state is ours to add.
- Perks arrive from senators, not from the player's pick. The donor has no choice UI to copy.

**Consequences.**
- A worker per advance is code per advance. That is the opposite of "small and numeric". Keep it
  for the few advances a stat cannot express.
- MP Compat covers VFE Classical's senator buttons and one perk gizmo, but registers no
  `AddPerk` [V, `Multiplayer.Compat.VanillaFactionsClassical` in `1.6/Referenced/`]. That only
  matters if the mod is used as shipped; this route copies its shape.

### D. Point board

**What it gets us.**
- **One screen showing every option and the unspent points**, which is the most legible form of
  "chosen as they play". The donor [V, `3079786283/1.6/Assemblies/VFETribals.dll`]:
  - `GameComponent_Tribals` scribes `availableCornerstonePoints` and a `cornerstones` list;
  - `CornerstoneDef` carries `statOffsets` and `statFactors`;
  - `Window_CustomizeCornerstones` spends points through `AddCornerstone`, and
    `Alert_AvailableCornerstonePoints` flags unspent points.
- **The fix for the donor's sync defect is shipped too.** `AddCornerstone` writes saved state
  from the window. MP Compat registers it as a sync method, with a pre-check that points remain
  and a post-invoke that refreshes the open window [V, `Multiplayer.Compat.VanillaFactionsTribal`].
  That is the exact shape our pick needs.

**What it cannot do.**
- The donor is colony-wide and not tied to skills [V]. Per pawn, per skill, points are ours.
- **The requirement forbids a new experience currency.** Points pass only if they are a derived
  count: thresholds crossed on the existing skill level, minus picks spent. A pool earned
  separately from skill XP would breach the rule. VPE's points are the derived kind: they come
  from `ChangeLevel`, not from their own XP [V].
- A board is presentation. It still needs A's or B's catalogue and state behind it.

**Consequences.**
- The board is the natural home for the "a spec is waiting" nudge, as an alert, not a letter.
  A modded `ChoiceLetter` is synced by neither of Multiplayer's mechanisms (**T-96**).

### E. Specialist posts (Ideology roles)

**What it gets us.**
- **Vanilla already ships eight specialist roles** (shooting, melee, research, plants,
  production, mining, animals, medical), with stat offsets, a quality offset, an ability and work
  restrictions [V, `Ideology/Defs/PreceptDefs/Precepts_Role.xml`].
- **A skill gate in XML.** `RoleRequirement_MinSkillAny` (for example `Crafting 6 /
  Construction 6` on the production specialist) [V]. The role menu greys a post whose requirement
  is unmet and names the reason (#114).
- **Commitment for free.** One role per pawn (**T-108**), and changing post runs through the
  role-change ritual, which unseats first (#114). That is a real, visible cost.
- XML reaches `RoleEffect_PawnStatOffset` / `Factor` on any `StatDef` and
  `RoleEffect_ProductionQualityOffset` (#114).
- The posts reach the player faith by #114's routes A, B or C.

**What it cannot do.**
- **Correction to the ticket's premise: vanilla specialist posts are not bounded.** All eight
  inherit `PreceptRoleMultiBase`, so they are `Precept_RoleMulti` [V]. `Assign` has no cap, and
  nothing outside the class caps `chosenPawns` [V, #114, re-read here]. "One holder at a time"
  must be authored:
  - a `Precept_RoleSingle` def, which brings the believer-count gate (**T-106**) and the
    empty-seat mood thought;
  - or a cap of ours.
- **The Easy form reaches only two of the eight.** `IdeoFoundation.CanAdd` refuses a def whose
  `preceptClass` is exactly `Precept_RoleMulti` once the ideology holds two visible
  `Precept_RoleMulti`, returning `"MaxMultiRolesCount".Translate(2)` (`MaxMultiRoles = 2`)
  [V, re-read; `docs/engine/ideology.md` § *Two multi-holder roles per ideology*]. The editor,
  fluid reform and generation all pass through it. So the XML/reform route gives the colony at
  most **two specialist post types**, each still holding any number of pawns.
  - Scarcity then comes from which two skills get a post at all, not from seats. A smith and a
    cook cannot both be specialists alongside, say, a shooter.
  - "Enough posts" for the skills the colony cares about needs #114's injection route
    (`Ideo.AddPrecept` checks nothing), a `Precept_RoleMulti` subclass (escapes the exact-type
    test), `Precept_RoleSingle` posts, or `visible` false. Each of these is the **Medium** form.
- **No passion gate.** Vanilla ships four `RoleRequirement` classes: `NotChild`, `SameIdeo`,
  `SupremeGender` and `MinSkillAny` [V]. "Only a deeply passionate pawn" is a `RoleRequirement`
  subclass of ours: C#, contained, and the seam #114 already names for its locks.
- **It is not progression.** Nothing is earned by use or chosen at intervals.
- **Generated pawns cannot arrive holding one** (see *Generated pawns*).
- **Weapons vs armour** cannot be told apart by a vanilla stat (see *Constraints*). Neither can a
  quality offset per recipe: `RoleEffect_ProductionQualityOffset` applies to every roll (#114).

**Consequences.**
- Posts are ideological. They need the Ideology DLC and the player faith. A pawn of another faith
  fails `RoleRequirement_SameIdeo` and is dropped on the next recache (#114).
- Vanilla's specialists carry `requiredMemes` (`HumanPrimacy` on production) [V]. Using them
  as shipped ties the posts to memes. Our own defs need not.
- A custom `RoleEffect` subclass does nothing (**T-107**).
- It overlaps [#116](https://github.com/cjd721/Rimworld-Archinity/issues/116)'s role
  hierarchy. One role per pawn means **a founder or preacher cannot also be the colony's
  weaponsmith.**

### F. Trained hediff at a bench or a rite

**What it gets us.**
- **Literal commitment, in XML.**
  - `HediffStage` stat offsets are read by `StatWorker.GetValueUnfinalized` alongside traits,
    precepts, roles, genes and gear [V].
  - A surgery bill on the pawn grants the hediff: `Recipe_AddHediff` with `addsHediff` [V].
  - An item or a building with `CompUsable` grants it through `CompUseEffect_AddHediff`
    (`hediffDef`, `allowRepeatedUse`) [V]. That the comp works on a building is [I].
- **Exclusivity in XML.** `Recipe_AddHediff.IsValidNow` refuses when any existing hediff fails
  `RecipeDef.CompatibleWithHediff`, which matches `incompatibleWithHediffTags` against
  `HediffDef.tags` [V]. So *weaponsmith* and *armoursmith* can exclude each other.
- **Switching at a cost**: `Recipe_RemoveHediff` [V].
- **The rite form has a donor.** VFE Empire bestows per-pawn honors at a ritual
  (`RitualBehaviorWorker_BestowHonor`, `RitualOutcomeEffectWorker_BestowHonor`). Their effects
  are applied by `StatPart_Honor`, keyed on the pawn's honors, and MP Compat syncs `AddHonor`,
  `RemoveHonor` and the tracker [V, `2938820380/1.6/Assemblies/VFEEmpire.dll`,
  `Multiplayer.Compat.VanillaFactionsEmpire`]. It is the corpus's one shipped system that is
  per-pawn, catalogued, rite-granted and MP-covered.
- **The hediff travels with the pawn.** A captive who was trained elsewhere is still trained.

**What it cannot do.**
- **The XML form ignores skill and passion.** `CompUseEffect_AddHediff.CanBeUsedBy` checks only
  "already has it" [V]. On a surgery recipe, `skillRequirements` gates the doctor, not the
  patient [I].
  - A skill or passion gate is a small subclass (`CanBeUsedBy` or `IsValidNow`), and that makes
    the route Medium.
- Vanilla ships no generic "add a hediff" ritual outcome [V, the `RitualOutcomeEffectWorker_*`
  list]. A rite needs our worker.
- **It is not earned by use** unless the gate reads skill level. Even then the pick is "go to the
  bench", not "at intervals".

**Consequences.**
- It is visible in the Health tab, and on non-colonists too, which suits "looking at a pawn is
  interesting".
- **T-113**: set `duplicationAllowed` false.
- A surgery form can be performed on prisoners, which may or may not be wanted.

### G. Trait

**What it gets us.**
- `TraitDegreeData` carries `statOffsets`, `statFactors` and `skillGains` [V].
- **`TraitDef.forcedPassions` / `conflictingPassions` link a trait to passion in XML** [V].
- **Generation in XML** [V, `Verse.PawnGenerator.GenerateTraits`]: through
  `PawnKindDef.forcedTraits`, or through backstory `forcedTraits`. A backstory that makes a pawn
  a smith can also hand it the smith trait.

**What it cannot do.**
- **Its causality is inverted.** `TryGenerateNewPawnInternal` runs `GenerateTraits` before
  `GenerateSkills`, and `GenerateSkills` forces a passion for every trait that requires one [V].
  A randomly rolled specialist trait therefore **creates** the passion instead of following it.
- No vanilla use effect grants a trait: there is no `CompUseEffect_*Trait` in the 1.6 assembly
  [V]. Granting mid-game is our code. VPE's `AbilityExtension_GiveTrait` is the donor
  [V, class present].

**Consequences.**
- Traits compete with personality traits for the same list, and random generation rolls them by
  `commonality` [I on exact counts].
- **Not recommended over F** unless the story wants the specialisation to read as who the pawn is,
  rather than what it was trained to do.

### Generated pawns — the pre-specialised half, per route

**Confirmed: VPE's `PawnGen_Patch` does pre-specialise raiders** [V, decompiled from
`2842502659/1.6/Assemblies/VanillaPsycastsExpanded.dll`]:
- It is a `[HarmonyPostfix]` on `PawnGenerator.GenerateNewPawnInternal`, ordered after VEF.
- For a pawnkind carrying `PawnKindAbilityExtension_Psycasts`, it:
  - initialises the psycast hediff from the psylink;
  - unlocks each path in the extension's `unlockedPaths` that `CanPawnUnlock` allows;
  - grants a `Rand`-drawn number of that path's abilities within a level range;
  - spends a `statUpgradePoints` range on stat upgrades.
- Under the Basilicus storyteller, any humanlike can also roll a random unlockable path.
- The extension sits on VPE's `Empire_Caster_*` and tribal caster pawnkinds [V, `PawnKinds_Psycaster_*.xml`].
- `PawnGroupMaker_PsycasterRaid` is admitted only for the psycaster raid strategy, and only if one
  of its options carries a `PawnKindAbilityExtension` [V, `PawnGroupMaker_CanGenerateFrom_Patch`].
- **The ticket's [I] is now [V].**

**Why this donor fits.** `GenerateNewPawnInternal` wraps `TryGenerateNewPawnInternal`, which runs
`GenerateSkills` [V]. A postfix therefore sees the pawn's final skills and passions. Vanilla hands
passions to the highest skills first (`GenerateSkills` walks skills by descending level) [V]. A
level-10 cook is usually a passionate cook, and the roll has something to key on. Generation
runs in simulation, so `Rand` there is deterministic (`docs/engine/determinism.md`) [I for our
postfix].

**One thing not to copy:** VPE's Basilicus branch reads a mod setting,
`PsycastsMod.Settings.baseSpawnChance`, during generation [V]. Mod settings are part of the sync
surface (**T-18**). Our postfix must take its numbers from defs, never from settings.

| Route | How a generated pawn carries specialisations |
|---|---|
| A, B | A generation postfix on the VPE pattern rolls entries or branches from final skill levels and major passions, as if the pawn had progressed. Authored enemies can take a pawnkind extension, as in VPE's. |
| C, D | As A. The donors are colony-wide and have no generation of their own [V]. |
| E | **No.** `Verse.PawnGenerator` assigns no role, and a role is scoped to one ideology: a recruit must share the player faith before `RoleRequirement_SameIdeo` passes (#114). **The "prize captive" clause is unmet by this route.** |
| F | **XML, kind-bound:** `PawnKindDef.startingHediffs` (`def`, `chance`, `severity`, `durationTicksRange`) [V]. It keys on the pawnkind, not on skill. **Skill-keyed:** the same postfix as A. |
| G | **XML, backstory-bound or kind-bound:** backstory or `PawnKindDef.forcedTraits` [V]. It shares the inverted causality above. Skill-keyed: the postfix. |

### Recommendation, not a selection

**A with B's exclusivity, and a VPE-pattern generation postfix**, is the route I would point a
narrative session at:
- It is the only family that meets every clause, including the captive who arrives with the
  wrong specialisations.
- A is the lightest of the four shapes.
- The smith's weapons-or-armour fork needs only an exclusion between two entries, not a full tree.
- D's board is the right presentation if the pick should feel like a moment. It adds UI, not a
  different system.

**E is the guaranteed fallback, but weaker than the ticket assumed.** Its posts are not bounded
until we bound them, and its XML form offers only two post types. It has no passion gate until
we write one, and it cannot pre-specialise anyone. In practice it is Medium.

**F is the cheapest honest commitment.** It is XML, it travels with the pawn, and it is exclusive
by tag. It is right if "trained at a bench" is the fiction the story wants, and it fails
"earned by use" unless the gate reads skill.

## Constraints

Engine facts that bound every route.

- **Weapons and armour share one work-speed stat.** Every vanilla recipe base for weapons and
  armour uses `workSpeedStat` `GeneralLaborSpeed` [V, `Core/Defs/ThingDefs_Misc`]:
  - weapons: `BaseMakeableGun`, `BaseMeleeWeapon`, `BaseMakeableGrenade`, the neolithic ranged
    weapons;
  - apparel and armour: `ApparelMakeableBase`, `ArmorSmithableBase`, `ArmorMachineableBase`.

  Quality is rolled by `QualityUtility.GenerateQualityCreatedByPawn(Pawn, SkillDef, bool)`, which
  knows the skill and not the product [V]. **No route can express "better at weapons than at
  armour" through a vanilla stat.** Two ways through:
  - **XML.** New `StatDef`s, and `workSpeedStat` repointed on the weapon bases.
    `RecipeDefGenerator` copies `recipeMaker.workSpeedStat` onto the generated recipe [V]. Mods
    whose weapons do not inherit those bases keep `GeneralLaborSpeed` [I].
  - **C#.** A reader at the consumer that knows the recipe, which is C's worker, or a patch.
- **Skill levels have no level-up event.** `SkillRecord.Learn` increments `levelInt` inline. Its
  only side effects are a tale at level 14 and a mote [V]. A trigger is a postfix on `Learn` or a
  poll. Levels are also written without `Learn`: the `Level` setter, `EnsureMinLevelWithMargin`
  and generation [V]. Above level 10, `SkillRecord.Interval` decays skill, so **a specialisation
  can outlive the level that earned it** [V].
- **Passion is three values on the skill record.** `SkillRecord.passion` is a scribed
  `Passion : byte` (`None`, `Minor`, `Major`) [V]. `LearnRateFactor` switches on it (0.35 / 1 /
  1.5) and **throws** on any other value [V]. "Deeply passionate" can only mean `Major`. **No mod
  on disk adds passion tiers** [V]:
  - Vanilla Skills Expanded is absent (`About.xml` sweep);
  - Prepare Carefully carries `InitializeExtendedPassions` / `PassionManagerType` names for a
    passion mod it only reflects into [I].
- **Passion changes mid-game.** Biotech `GeneDef.passionMod` (`AddOneLevel`, `DropAll`) [V].
  Growth moments and child generation `IncrementPassion` [V]. So a specialisation gated on
  `Major` can lose its gate, for example to an altar xenogene. Passion-granting is the altar's
  (`docs/playtest-notes.md`). That makes the altar the only way to open a new specialisation
  line on an existing pawn.
- **The pick must be a synced command.**
  - A modded `ChoiceLetter` is synced by neither mechanism (**T-96**).
  - A `Dialog_NodeTree` subclass drops out of Multiplayer's bindings (**T-95**).
  - A write from a draw method diverges silently (**T-85** is the shipped example).

  The corpus's three per-pick precedents all go through MP Compat sync methods [V]: VSE
  `AddExpertise`, VPE `UnlockPath`/`SpentPoints`, VFE Tribals `AddCornerstone`.
- **Ideology.** One role per pawn (**T-108**). Custom `RoleEffect`s are inert (**T-107**). The
  single-holder believer gates are **T-105** and **T-106**.
- **Hediff-held state** duplicates onto Anomaly duplicates (**T-113**).
- **Per-pawn static caches.** VSE (per MP Compat's sync worker) and VFE Empire (`HonorUtility`)
  both keep per-pawn state in a static dictionary keyed by pawn [V]. That passes the
  divergence gate only because it is keyed (`CODING_STANDARDS.md` § *The two gates*). Where the
  state lives is a build question.

## Available mechanisms

| Mechanism | Provides | Evidence |
|---|---|---|
| `VSE.Expertise.ExpertiseDef` payloads | 29 tags across both roots and all version folders; **8 distinct 1.6 defs** (VCE 2, VGE 3, VCEF 3 in two variant folders). All load only with Vanilla Skills Expanded active | [V] `2134308519`, `3609835606` `loadFolders.xml`; `1914064942/1.6*/Patches/VanillaSkillsExpanded/Expertise_Patch.xml` |
| What would read them | **Nothing on disk.** The only assemblies naming `Expertise`, in either heap, are MP Compat's (its `VanillaSkillsExpanded` compat class) | [V] sweep below |
| VPE progression and generation | Hediff-held points and paths; XML-gated paths; `PawnGen_Patch` pre-specialisation; MP Compat sync of the spend methods | [V] `VanillaPsycastsExpanded.Hediff_PsycastAbilities`, `.PawnGen_Patch`, `.PawnKindAbilityExtension_Psycasts`; `Multiplayer.Compat.VanillaPsycastsExpanded` |
| VFE Classical perks | Def + worker + stat postfix pattern; colony-wide | [V] `VFEC.Perks.PerkDef`, `.GameComponent_PerkManager`, `.PerkPatches` |
| VFE Tribals cornerstones | Point-spend window, alert, stat postfix; colony-wide; MP Compat-synced pick | [V] `VFETribals.CornerstoneDef`, `.GameComponent_Tribals`; `Multiplayer.Compat.VanillaFactionsTribal` |
| VFE Empire honors | Per-pawn catalogue bestowed at a ritual, stat part keyed on the holder, MP Compat-synced add and remove | [V] `VFEEmpire.HonorUtility`, `.HonorsTracker`, `.StatPart_Honor`; `Multiplayer.Compat.VanillaFactionsEmpire` (`Referenced/`) |
| Ideology specialist roles | 8 multi-holder posts; `RoleRequirement_MinSkillAny`; vanilla stat, quality and ability effects | [V] `Precepts_Role.xml`; `RimWorld.Precept_RoleMulti`; #114 |
| Hediff grants | `Recipe_AddHediff`, `Recipe_RemoveHediff`, `CompUseEffect_AddHediff`, `RecipeDef.incompatibleWithHediffTags`, `PawnKindDef.startingHediffs` | [V] `Assembly-CSharp.dll` |
| Trait fields | `statOffsets`/`statFactors`/`skillGains`; `forcedPassions`/`conflictingPassions`; kind and backstory `forcedTraits` | [V] `RimWorld.TraitDef`, `.TraitDegreeData`, `Verse.PawnGenerator` |
| Biotech growth moment | Vanilla's own "choose at intervals" UI (a trait and passions at growth birthdays). Multiplayer needed a whole bespoke session for it | [V] `docs/traps/multiplayer.md` T-96; `ALTAR.md` § 10 |
| VFE Medieval 2 learning modifier | A hediff comp plus a `SkillRecord.LearnRateFactor` postfix that adds a learning bonus by passion. It changes learning rate, not specialisation | [V] `VFEMedieval.HediffComp_LearningPassionsModifier`, `.VFEMedieval_SkillRecord_LearnRateFactor_Patch` |

**Ruled out.**
- **Genes and aptitudes.** Biotech genes, and under Anomaly traits and hediffs, add *skill
  levels* through `SkillRecord.Aptitude` [V]. That raises the skill; it does not specialise
  inside it, and genes are the altar's.
- **Worksites Expanded** names skill roles for its outpost workers (`ApplyRoleSkills`,
  `GetSkillRoleName`) [I, names only]. It is not a per-pawn advance system.

**The wide pass.**
- **Roots.** `steamapps/workshop/content/294100/` and `steamapps/common/RimWorld/Mods/`, with
  vanilla under `Data/`. The only mods unique to the second root are Archinity's own five, and
  none of them names passion, `SkillRecord` or expertise.
- **DLL flags.** `-g '*.dll' -g '!**/obj/**'`, plus `-g '!**/Referenced/**'` when hunting
  implementers. Results attributed with `corpus.py --which`.
- **ASCII, case-insensitive:**
  - `Expertise` → MP Compat only;
  - `Specializ`, `Specialis`, `Mastery`, `Talent`, `Proficien` → VFE Props, Adaptive Storage,
    Mechanoids Total Warfare, Multiplayer, VEF, Prepare Carefully, Faction Customizer, Auto-Cast
    Specialist Commands, Worksites Expanded, VQE Ancients and VRE Hussar. None is a specialisation
    system [I, identifier names only; none decompiled];
  - `SkillTree`, `PerkTree` → zero;
  - `Passion` → eleven mods: MP Compat, Multiplayer (growth-moment sync), Prepare Carefully and
    Compositable Loadouts (UI), VPE and VPE Puppeteer, VRE Android (its own growth-passion
    choice), VFE Medieval 2 (learning rate, read), VQE Ancients (gene passion text), Worksites
    Expanded, and VEF in its 1.5-and-earlier assemblies only. None is a specialisation carrier,
    and none adds a passion value [I except where read].
  - **Validator:** `PsycasterPath` → VPE and VPE Hemosage.
- **UTF-16, case-insensitive,** with the null-interleaved literal `E\x00x\x00p\x00…` typed
  directly, no command substitution: `Expertise` → MP Compat only. **Validator:** the same file's
  `AccessTools.TypeByName("VSE.ExpertiseTracker")` literal is the `#US` hit.
- **XML.** Every namespaced `<Ns.TypeDef>` tag was enumerated, and every def tag whose name
  contains skill, perk, talent, expert, special, master, train, passion, learn, trait, honor, path,
  cornerstone or role was listed. The hits are the families above. **No mod adds a `SkillDef`.**
  **Validator:** the same sweep returned the known `VFEC.Perks.PerkDef` 152 and
  `VanillaPsycastsExpanded.PsycasterPathDef` 88.
- **Residual gap.** A per-pawn system implemented without any of these names, for example a
  generic `Harmony` patch on `StatWorker` keyed on a comp, would not surface. It would be a donor
  no better than VFE Empire's honors.

## Status

**Evidence class: READ.** Settled from decompiled RimWorld 1.6.4871 `Assembly-CSharp.dll` and the
1.6 assemblies of VPE (`2842502659`), VFE Classical (`2787850474`), VFE Tribals (`3079786283`), VFE
Empire (`2938820380`), VFE Medieval 2 (`3444347874`), Multiplayer Compatibility (`1629973374`, both
`Assemblies/` and `Referenced/`), plus the XML of both roots. `ilspycmd` 8.2.

- `corpus.py --check` reports Vanilla Gravship Expanded updated since the pin
  (2026-08-19 → 2026-09-15). Its expertise file was read as it stands on disk.
- Every mechanism a route composes is [V]. **Every route is [I] as a composition**, because none
  is built.

Capability: [#156](https://github.com/cjd721/Rimworld-Archinity/issues/156). Role facts:
[#114](https://github.com/cjd721/Rimworld-Archinity/issues/114).

## Open questions

**Requirement gaps.** These go to the COLONY requirement (authored by
[#129](https://github.com/cjd721/Rimworld-Archinity/issues/129), now closed), so owned by
[#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).

- **Does a specialisation survive losing its gate?** Skill decays above 10, and a xenogene can
  drop a passion. Kept, frozen or lost is a rule, not a mechanism.
- **Do starting colonists arrive specialised?** The generation postfix reaches them too, unless it
  excludes them.
- **Is "deeply passionate" `Major` only?** The engine offers nothing else.
- **Thresholds, slots per skill, and the size of each advance.** Balance. The only shipped figures
  are 0.01–0.05 per entry.
- **Does the smith fork require new work-speed stats?** If "weapons vs armour" is literal, the
  repointed `workSpeedStat` of *Constraints* is part of any route. It touches every weapon and
  armour recipe base in the bin, and bill and recipe owners should see it.

**Unverified route claims [I].**
- `CompUsable` / `CompUseEffect_AddHediff` on a building rather than an item.
- That a surgery recipe's `skillRequirements` binds the doctor, not the patient.
- That the vanilla surgery and use-item float menus are Multiplayer-synced without help.
- How `StatPart_Honor` is attached to stats in VFE Empire: the XML carries no reference, so it is
  presumably attached in code; not traced.

**Build questions for [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).** Not
answered here, by design.
- Where per-pawn state lives: a hediff, a pawn comp, or a keyed static dictionary with its own
  save hook.
- The trigger: a `Learn` postfix or a poll, and how it treats direct level writes.
- The pick's sync registration. Archinity registers no Multiplayer sync method today.
- How specialisations show on a non-colonist pawn, which is what makes a captive worth
  inspecting.
- Whether an advance's stat is ours (see *Constraints*) or an existing one.
