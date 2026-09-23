# Colony management

## Purpose and scope

Answers the colony-life clauses of [`docs/requirements/COLONY.md`](../requirements/COLONY.md)
that no other spec owns, at route depth.

**Where adjacent systems take over.**

- Bills arriving configured, and a configuration reused across bills — `DEFAULTS.md`.
- Kit presets and the whole kit — `DEFAULTS.md`.
- A pawn advancing within a skill — `SPECIALISATION.md`.
- Reclaiming obsolete gear — `ITEMS.md`.
- What research gates — `RESEARCH.md` and `ERA.md`.

## The add-bill menu shows what matters now

### Purpose

Answers [`docs/requirements/COLONY.md`](../requirements/COLONY.md) § *The add-bill menu
shows what matters now*: a bench's add-bill list foregrounds the recipes of the colony's
current era. **Presentation, never a content gate** — research alone decides what can be made;
an above-era recipe drops out when its research is locked, and one with no prerequisite does
not until the grids give it one (see *Open questions*). Established by
[#161](https://github.com/cjd721/Rimworld-Archinity/issues/161), building on
[#87](https://github.com/cjd721/Rimworld-Archinity/issues/87) (the menu mods) and
[#96](https://github.com/cjd721/Rimworld-Archinity/issues/96) (what an era shows). The
research tab is settled and is not this section's. Bill defaults and copy-paste are
`DEFAULTS.md`'s.

### Verdict

- **Possible?** Yes. Filter, demotion by era and search all fit one vanilla seam, the
  add-bill `FloatMenu`, as draw-time C#. Era-limited benches are XML but cannot meet the
  requirement on their own.
- **Multiplayer?** Yes, per player by construction, if the filter applies at draw time and
  keeps vanilla's option actions. A filter state *shared* between the two players needs a
  synced field. Adopting Nice Bill Tab means taking on its Multiplayer debt.

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **A. Era filter** | Era checkboxes on the add-bill menu; unticked eras are not listed | our code on vanilla `ITab_Bills` → `BillStack.DoListing`; donor: FloatSubMenu (vendored in Nice Bill Tab) | C# | Medium | Yes, per player. Shared state: with work |
| **B. Group and demote by era** | Current era first; older eras sorted below, tinted, or folded into one submenu per era | our code on the same seam; vanilla `FloatMenu` sort; donor: FloatSubMenu `FloatSubMenu`/`FloatMenuDivider` | C# | Medium | Yes |
| **C. Era-limited benches** | Each era's bench carries its era's recipes | XML patches on `recipeUsers`/`recipes`; VEF `RecipeInheritanceExtension` for cumulative benches | XML · patch | Hard in aggregate | Yes |
| **D. Search only** | Type to find; no era axis | Nice Bill Tab as it ships, **or** our own `QuickSearchWidget` row in the vanilla menu (FloatSubMenu's `FloatMenuSearch` is the working donor) | mod as-is · C# | Easy (Nice Bill Tab) · Medium (ours) | Nice Bill Tab: with work. Ours: Yes |
| **E. Nice Bill Tab with an era axis** | Nice Bill Tab's two-pane, categorised, searchable tab, plus era grouping | Nice Bill Tab, patched or forked | C# | Hard | With work: its bill-list writes bypass MP |
| **F. Hide through `RecipeWorker.AvailableOnNow`** | Out-of-era recipes vanish from the add-bill list | custom `workerClass` on every recipe | XML + C# | Medium | **Not recommended**: this is list membership, not draw time |

**A. Era filter.**
- *What it gets us.* A set of era checkboxes; the menu lists only ticked eras. By default
  it shows the current era, or the current era plus the one below. This matches Conrad's
  #87 wording: *"a checkbox set, not a sort order"*.
- *What it cannot do.* It does nothing for a recipe with no era key. Such recipes must
  **fail open** and always be listed, or the menu would hide something below the ceiling
  (see *How a recipe gets an era*, below).
- *Consequences.*
  - Per player by default. The two players see different menus, which the requirement
    allows and T-21 makes safe.
  - It coexists with Nice Bill Tab, one player at a time.
    - Nice Bill Tab draws an on-tab checkbox (`Settings.EnabledMod`, flipped by
      `Settings.ToggleMod`). While it is off, the `FillTab` prefix returns `true` and
      vanilla's tab and menu run [V].
    - The flag defaults to `true` and is not scribed, so Nice Bill Tab is back on at every
      launch [V].
    - While Nice Bill Tab is on for a player, that player sees its tab and not our menu. The
      other player can be on vanilla's menu with this filter. Both creation paths are synced.

**B. Group and demote by era.**
- *What it gets us.*
  - Nothing is ever hidden, so it is presentation in the strictest sense.
  - The shapes the story can use: current era on top; older eras below in a muted tint; or
    each older era folded into a submenu. Better Architect Menu's era grouping is the
    shipped precedent: it groups and tints, and never removes.
- *What it cannot do.*
  - It does not shorten the list unless older eras are folded into submenus.
  - A disabled row cannot serve as a group header. Vanilla sorts disabled rows to the
    bottom.
- *Consequences.* It composes with A and D on the same patch. B+A is "demote by default,
  filter on demand".

**C. Era-limited benches.**
- *What it gets us.* A bench's list is short by construction, and it needs no C# at all.
- *What it cannot do.* It cannot meet "older recipes stay available, only less
  prominent" and still shorten the list:
  - If the newest bench keeps every older recipe, its list is exactly as long as before.
  - If it does not, an older recipe needs an older bench to be kept or built.
  - The bin already has era pairs that share one list: the hand and electric tailoring
    benches carry 184 and 181 recipes, and the fueled and electric smithies 241 each.
- *Consequences.*
  - Every mod's recipes must be re-homed by patch: about 1,420 bench recipes across the bin,
    334 of them with no era to sort by (counting rules under *How a recipe gets an era*).
  - It re-homes content, which drags it towards a content gate.
  - **Not recommended as the answer to this requirement.** It stays a legitimate content
    decision for the progression grids.

**D. Search only.**
- *What it gets us.* The eighty become findable by name.
- *What it cannot do.*
  - It has no notion of era, so it does not answer the requirement alone.
  - It is best as a companion to A or B.
- *Consequences.* Nice Bill Tab replaces the whole tab, and its Multiplayer debt is recorded
  in #87 § 7. Our own search row avoids that debt and costs a small patch.

**E. Nice Bill Tab with an era axis.**
- *What it gets us.* The richest surface: a permanent recipe pane with categories, search
  and stat columns.
- *What it cannot do.* Stay small. Nice Bill Tab has no era concept (zero `TechLevel` in
  its assembly).
- *Consequences.* We would own its unsynced bill-list writes and its `EnableAutoNaming`
  hazard.

**F. Hide through `AvailableOnNow`.**
- *Why it is not recommended.*
  - `AvailableOnNow` also governs whether a pasted bill is accepted, so hiding through it
    changes what a client can *do*.
  - A per-recipe `workerClass` collides with every recipe that already has one.

**Recommendation, not a selection:** B as the default presentation, with A's checkboxes
and D's search row on the same draw-time patch. Everything stays reachable, the list gets
short on demand, and there is one seam to maintain. Selecting a route is
[#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s act.

#### How a recipe gets an era

**`RecipeDef` has no `techLevel` field** [V]. Its era has to come from somewhere else.
The counts below are whole-bin, under these inclusion rules:
- **Mods:** all 155 mods and the game data, one copy per packageId, every mod treated as
  loaded.
- **LoadFolders:** a `v1.6` entry counts only if its `IfModActive` mods are on disk, and not
  if its `IfModNotActive` mods are.
- **Inheritance:** `ParentName` is resolved, and list fields merge the way RimWorld merges
  them.
- **Patches** are **not** applied.
- **What counts:** a recipe that lands on a non-pawn bench. Surgeries are excluded, and so
  are namespaced `RecipeDef` subclasses.

**Counting every conditional folder regardless of its condition** moves the totals:
- `RecipeDef`s go from 748 to 800, which matches an independent recount exactly;
- bench recipes go from 1,420 to 1,458, of which 336 have no prerequisite.

An independent recount with its own bench-membership rules got 1,514, with 76.7% having a
prerequisite. **The proportions hold within a point under every rule tried.**

| Key | What it covers | Limit |
|---|---|---|
| **K1. Derived from the gating research** (max `techLevel` over `researchPrerequisite(s)`; `RecipeDefGenerator` copies `recipeMaker`'s prerequisites onto generated recipes [V]) | **1,086 of 1,420** bench recipes (76%) | Follows research re-tiering for free. Could instead key on the project's era tab once ERA's one-tab-per-era exists [I] |
| **K2. Derived from the product's `ThingDef.techLevel`**, or World Tech Level's `MinRequiredTechLevel` over the product | 102 of the 334 no-prerequisite recipes | 232 of the 334 have no product tech level (200) or no single product (32). **141 recipes** whose product and research tech levels are both set disagree on era |
| **K3. Authored per recipe** (our `DefModExtension` on `RecipeDef`) | anything | World Tech Level's `TechLevelConfigDef` cannot key a recipe. It keys the product `ThingDef` (no `RecipeDef` database [V]) |
| **K4. Floor default** (Better Architect Menu: `Undefined → Neolithic` [V]) | the remainder | Wrong for no-prerequisite content from later eras. Medieval Overhaul alone carries 149 no-prerequisite recipes, counting all of them rather than only bench-reachable ones |

**No-prerequisite recipes are 334 of 1,420 (24%)**. Counting every no-prerequisite recipe,
not only bench-reachable ones, the largest sources are Medieval Overhaul (149), vanilla Core
(58) and VE Cooking (31). The natural composite
is K1 → K2 → K3 exceptions → K4, and under route A an unkeyed recipe fails open. **Which
key is the truth is a progression-grid question**, not this one: `docs/progression/` is
still empty.

### Constraints

- **Filter at draw time, never at list-membership time** ([T-21](../TRAPS.md)).
  `ITab_Bills.OptionsMaker` builds a fresh `List<FloatMenuOption>` on each click, and
  nothing serialises it [V]. Mutating `def.AllRecipes` or `AvailableOnNow` per player is the
  unsafe form, because paste validation reads both [V].
- **Keep vanilla's option actions.** The add-bill click is synced as a delegate:
  `SyncDelegate.Lambda(typeof(ITab_Bills), "FillTab", 2)`. Every other path goes through
  `SyncMethod BillStack.AddBill` [V]. Filtering, reordering or nesting vanilla's own
  options leaves that path untouched [I]. **Transpiling `FillTab`** risks the lambda
  ordinal Multiplayer addresses [I]; prefer a wrap of `DoListing`'s options delegate.
- **A client-local filter state is a deliberate per-player difference.** Draw-only reads of
  a mod setting do not trip [T-18](../TRAPS.md), which concerns the sim path. But
  `CODING_STANDARDS.md` has **no ratified carve-out** for client-local UI state
  (`docs/engine/determinism.md` § *Presentational separation*).
- **One surface per player at a time.** While Nice Bill Tab is enabled, its `FillTab`
  prefix returns `false` and vanilla's menu does not open. Its on-tab checkbox
  (`Settings.EnabledMod`, client-local, not scribed, default `true`) makes the prefix return
  `true`, and vanilla runs [V, `NiceBillTab.ITab_Bills_FillTab_Patch.Prefix`]. So A, B and D
  coexist with Nice Bill Tab, per player. E and A/B/D are alternatives for one player, not
  exclusive for the pair.
- VFE Medieval 2 swaps `def.allRecipesCached` inside a `FillTab` prefix and postfix for
  mannequin-linked benches [V]. A filter on the options sees the swapped recipes, which is
  correct.

### Available mechanisms

- **Vanilla** [V, `Assembly-CSharp` 1.6.4871]:
  - `ITab_Bills.FillTab` → local `OptionsMaker` over `AllRecipes`, gated on
    `AvailableNow && AvailableOnNow`.
  - `BillStack.DoListing(rect, Func<List<FloatMenuOption>>, …)` opens `new FloatMenu(...)`.
  - `FloatMenu` orders by `Priority` then `orderInPriority`, descending, and a `Disabled`
    option takes `MenuOptionPriority.DisabledOption`. `FloatMenuOption` carries a
    `tooltip`, an icon colour and an extra-part GUI hook.
  - `QuickSearchWidget` exists; it is not wired to this menu.
- **FloatSubMenu** (kathanon's library, vendored only inside Nice Bill Tab
  `3520130671/1.6/Assemblies/FloatSubMenu.dll`; the standalone `kathanon.floatsubmenu` is
  not on disk) [V]:
  - `FloatSubMenu` (nested menus), `FloatMenuSearch` (a `QuickSearchWidget` row that
    swaps `FloatMenu.options` for a filtered copy at draw), `FloatMenuToggleOption`
    (checkbox rows) and `FloatMenuDivider`.
  - All its Harmony patches are UI patches. `new Harmony("kathanon.FloatSubMenu").PatchAll()`
    applies FloatSubMenu's own patches (`FloatMenu.UpdateBaseColor`, `GenUI.DistFromRect`) and
    those of its bundled MoreWidgets:
    - `GameConditionManager.TotalHeightAt` and `DoConditionsUI`;
    - `GameComponentUtility.GameComponentOnGUI`;
    - `DebugTabMenu_Settings.InitActions`;
    - a tooltip transpiler on `LongEventHandler.LongEventsOnGUI` and `UIRoot.UIRootOnGUI`.

    [V, `FloatSubMenus.Patches`, `MoreWidgets.Patch_ShowCoords`,
    `MoreWidgets.Patch_DoTooltipGUI`]
  - The working donor for A, B and D inside the vanilla menu. Whether it can be reused or
    re-vendored is a licence question [I].
- **Menu mods on disk**, both roots, 1.6 assemblies. Validated wide pass: ASCII and
  UTF-16 `ITab_Bills`, with `AddBill` as the UTF-16 validator.

| Mod | packageId | Workshop id | What it does to the add-bill list | Multiplayer |
|---|---|---|---|---|
| Nice Bill Tab | `Andromeda.NiceBillTab` | 3520130671 | Replaces the tab. Searchable, categorised, **no era** [V] | No shim, and its bill-list writes are unsynced (#87) |
| Better Workbench Management | `falconne.BWM` | 935982361 | Leaves it alone. Its `BillStack.DoListing` prefix always returns `true` and never touches the options delegate; it draws its paste button and drag-to-reorder [V, `BillStack_DoListing_Detour.Prefix`]. Copy, paste and link happen after the pick | No shim; count-setting hazard; its paste-settings button writes unwatched fields (`DEFAULTS.md`, #157) |
| Better Architect Menu | `ferny.BetterArchitect` | 3563882422 | Architect menu only. Donor for the era resolver [V, 1.6 source] | `MysteryUnlockTracker` hazard (#87) |
| VFE Medieval 2 | `OskarPotocki.VFE.Medieval2` | 3444347874 | Swaps `allRecipesCached` on mannequin-linked benches through a `FillTab` prefix and postfix. Swaps `bill.recipe` on `AddBill`/`Clone`/`ExposeData` [V] | Keyed on facility links, which are synced state |
| Compositable Loadouts | `Wiri.compositableloadouts` | 2679126859 | The list is untouched. A `DoListing` postfix adds a button that *creates* bills from loadouts. It adds a `W_PerTag` repeat mode whose tag lives outside the bill, carried through `Bill_Production.Clone` and a postfix on BWM's `MirrorBills` [V] | No compat |
| Ushankas Glittertech Expansion | `Ushanka.GlittertechExpansion` | 3522676478 | Its own add-bill menu for memory cells: `ITab_MemoryCellMods.BuildRecipeOptions` over `AllRecipes`, handed to `BillStack.DoListing` [V] | — |
| Multiplayer | `rwmt.multiplayer` | 2606448745 | Syncs the add-bill delegate and `AddBill` [V] | — |

- **Absent** [V]: Nicer Bills, Dubs Mint Menus, `kathanon.searchablemenus`.
- **Glittertech's 1.6 menu** [V]: Glittertech's `Source/ITab_BillsMemoryCell.cs` is not in the
  1.6 `GlittertechExpansion.dll`. The same shape ships renamed as
  `ITab_MemoryCellMods.BuildRecipeOptions` → `DoListing`. **A wrap at `DoListing` reaches
  this menu too; a patch on vanilla's local `OptionsMaker` would miss it.** Its option
  actions are Glittertech's own, not the delegate Multiplayer registers.
- **None of the menu mods writes a bill field from the add-bill menu.** Multiplayer's
  field-watch scopes (`docs/engine/determinism.md` § *Editing a bill is synced by where the
  edit happens*) cover the bill row and the bill dialog, and neither is involved. A filter
  whose toggles write only its own client-local state needs none of them.
- **Era-limited-bench tools:** VEF `RecipeInheritanceExtension` copies another bench's
  recipes at startup through `inheritRecipesFrom` and an `Allows` filter. It is additive
  only [V, `VEF.Buildings.RecipeInheritance` static constructor]. Removing a recipe from a
  bench is a plain XML patch.
- **Current-era source:** World Tech Level's `WorldTechLevel.Current`, or the planned
  `GameComponent_Era` ([`ERA.md`](ERA.md)). Both are synced; a draw-time read of either is
  safe.

### Status

**READ.** Established by #161 from vanilla 1.6.4871 and the 1.6 mod assemblies, decompiled.
The route compositions are [I]. What is [V] is each seam, the Multiplayer registrations,
the FloatSubMenu API and the whole-bin counts.

- The counts come from a scratch scanner. Its `RecipeDef` total (748) matches a regex
  count over the same folders. Its all-conditional-folders variant (800) matches an
  independent recount.
- The counts are pre-patch, so any retiering patch would move them.

### Open questions

- **Which key is the truth** (K1–K4), and whether a recipe's era follows its research tab:
  owned by the progression grids ([#30](https://github.com/cjd721/Rimworld-Archinity/issues/30)).
- **Default filter state and whose it is**: current era alone or plus one below; per player
  or shared. Capability: per-player draw-time state is MP-safe (*Constraints*); shared state
  needs a synced field (*Verdict*); per-player state can live for the session only, with no
  mod setting, or be saved in a mod setting.
- **"Superseded" as well as "older"**, from #96 row 3: whether a Neolithic recipe still in
  use ranks as current. [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s,
  per #96's hand-back.
- **A ratified carve-out for client-local UI state** in `CODING_STANDARDS.md`, which every
  per-player route needs. Owned by [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119),
  before any per-player route is built.
- **FloatSubMenu's licence**, and whether to depend on Nice Bill Tab's copy of it or
  re-vendor it: a build question for #119.
- **Recipes with no prerequisite escape the research ceiling** (334 of 1,420). Capability:
  an XML `researchPrerequisite` closes each one — `RecipeDef.AvailableNow` keys on
  `researchPrerequisite(s)`, and `RecipeDefGenerator` copies `recipeMaker` prerequisites [V]
  (`docs/engine/facilities-and-recipes.md`; `ITEMS.md` § *New code and defs* › 3, the
  venue). Which recipes get which project is the progression grids'
  ([#30](https://github.com/cjd721/Rimworld-Archinity/issues/30)). A menu filter must not be
  mistaken for it.

## Recreation follows a pawn's passions

Resolved on [#159](https://github.com/cjd721/Rimworld-Archinity/issues/159). Evidence class
**READ**.

### Purpose

Answers [`docs/requirements/COLONY.md`](../requirements/COLONY.md) § *Recreation follows a
pawn's passions*: a pawn at recreation prefers recreation that trains a skill it is passionate
about, major passion first. That recreation *can* train a skill is vanilla XML
(`JobDef.joySkill` / `joyXpPerTick`, settled on
[#76](https://github.com/cjd721/Rimworld-Archinity/issues/76#issuecomment-5729323742)) and is
not re-answered here. How much experience, room multipliers and which item trains what are the
[build map](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.

### Verdict

- **Possible?** Yes. Vanilla has one per-pawn weight seam, `JoyGiver.GetChance(pawn)`, and passion
  appears nowhere in the chain today. A weight keyed on the job's `joySkill` and the pawn's
  passion in that skill slots in there. Nothing on disk does it already, so every route is
  ours to build.
- **Multiplayer?** Yes. Recreation is picked inside the pawn's think tree on the synced tick,
  and every route reads only synced pawn and def state. The one hazard is taking the weight
  from a mod setting (T-18).

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **A. Passion factor on the chance** | Weighted preference: the chance of each skill-training recreation is multiplied by the pawn's passion in that skill (major > minor > none), and it covers every `joySkill` job in the bin automatically | our assembly: a Harmony postfix on `JoyGiver.GetChance` | C# (patch) | Medium (low end) | Yes |
| **B. Passion-first think node** | Strict preference: the pawn tries passion-training recreation first and falls back to ordinary recreation only if none is available or it is bored | our `JobGiver_GetJoy` subclass (overrides `JoyGiverAllowed`) + an XPath insert into the think trees | C# + XML patch | Medium | Yes |
| **C. Our JoyGiver subclasses** | The same as A, without Harmony: each skill-training `JoyGiverDef` is repointed to a subclass of ours whose `GetChance` reads passion | our assembly + `giverClass` patches | C# + XML patch | Medium | Yes |
| **D. Passion-weighted book choice** | Reading prefers textbooks on the pawn's passion skills. Vanilla textbooks cover **all 12 skills** | our assembly: a patch on `BookUtility.TryGetRandomBookToRead` (+ route A's factor on the `Reading` giver) | C# (patch) | Medium | Yes |
| **E. Raise `baseChance` of training recreation** | Every pawn favours skill-training recreation, whatever its passions | XML patch on `JoyGiverDef.baseChance` | XML | Easy | Yes |
| **F. Transpile `JobGiver_GetJoy.TryGiveJob`** | The same as A, applied at the one line that multiplies chance by tolerance. This also reaches givers whose `GetChance` override skips the base method | our assembly | C# (transpiler) | Medium | Yes |

**Not recommended:** **E** does not satisfy the requirement, because it ignores passion.
**C** gets route A's result with more surface: one subclass per vanilla worker class, plus
another for each mod worker class (such as VFE Medieval 2's `JoyGiver_PlayTrainingDummy`), so
it breaks whenever a donor mod changes. **F** is a transpiler over a line route A already
reaches. Its only gain, reaching `GetChance` overrides that skip the base, touches no
skill-training giver on disk.

**A — passion factor on the chance.**
- *Gets us:* a pawn with a major passion in Shooting drifts to horseshoes, billiards and darts
  rather than always taking them. The strength of the drift is one number per passion level.
  It needs no per-item authoring: any recreation job anyone authors with `joySkill` joins
  automatically, including the build map's future content. It works everywhere recreation is
  chosen: idle time, the recreation timetable, in bed and at gatherings, because all four go
  through `JobGiver_GetJoy.TryGiveJob` → `GetChance` [V].
- *Cannot:* override boredom (see *Constraints*). It cannot favour a skill the pawn has no
  recreation for on the map. It cannot see VFE Furniture's `extraJoySkill`, which lives on the
  building rather than the job, without a second lookup. It also cannot reach pawns at a
  Worksites Expanded worksite. `MiningOutpost.SharedJobUtility.TryRecreation` picks their
  recreation from a uniform shuffle of `JoyGiverDef`s, bypassing both `GetChance` and
  tolerance [V] (**T-159**). The same gap applies to B–F.
- *Consequences:* the factor has a vanilla donor. `InspirationWorker.CommonalityFor` already
  weights a chance by passion in a def's skills (×1 / ×2.5 / ×5) [V]. A corpus precedent for
  the patch exists too: Knick Knacks (`3595196942`) ships a postfix on
  exactly `JoyGiver.GetChance` [V], so the patch shape is proven and two postfixes compose. It
  is patched on the base virtual method, so a subclass override that never calls `base`
  bypasses it. On disk that is only vanilla's `JoyGiver_TakeDrug` [V], which trains nothing.

**B — passion-first think node.**
- *Gets us:* the playtest wording taken literally: "when a deeply passionate shooter goes to
  relax, it goes and shoots", every time it can. Major-first comes from giving major and minor
  separate nodes in order. Optionally, one of our own chance nodes can soften it. Vanilla's
  chance nodes are per-hour MTB nodes [V], not a per-call chance.
- *Cannot:* reach recreation chosen outside the nodes we patch. `JobGiver_GetJoy` sits in
  Humanlike, four `SubTrees_Misc` sites and five gathering duties (Core, Royalty, Ideology)
  [V]. Each site is a separate XPath insert, or it is simply left vanilla. Like A, it cannot
  override boredom.
- *Consequences:* the pawn loses variety faster than under A. It hits the boredom gate on its
  passion joy kind sooner, then falls through to ordinary recreation.

**D — passion-weighted book choice.**
- *Gets us:* the only existing reach into the seven skills no recreation job trains (below).
  Vanilla textbooks roll one or two skills from all twelve [V]. Reading already prefers books
  that still teach the pawn something, and chooses among those at random [V]. D weights that
  random pick by passion. Vanilla already rewards the outcome with mood (the `SkillBookPassion`
  thought, +6 minor, +10 major [V]) but never uses it in the choice.
- *Cannot:* make books appear. Supply is loot and trade, which is content and progression.
- *Consequences:* `Reading` is one `JoyGiverDef` whose job carries no `joySkill` [V], so A and B
  both miss it. D is a separate seam and composes with A.

**Recommendation, not selection.** **A**, with **D** added if reach beyond the five covered
skills matters. A is the smallest piece of code that satisfies the requirement as written
(weighted, major first). It covers the whole bin with no per-item work, and a proven patch
already sits on the same method. Choose **B** instead only if the story wants a hard "always
goes and shoots" rather than a drift. The pick is
[#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.

### Constraints

- **Boredom beats any weight.** Tolerance is tracked **per joy kind**. Past 0.5 the kind is
  `BoredOf` and its givers are skipped outright until tolerance falls below 0.3. Until then the
  chance is also multiplied by `max(0.001, (1 − tolerance)⁵)` (`JoyToleranceSet`,
  `JobGiver_GetJoy.TryGiveJob` [V]). A passionate shooter shoots until bored and then does
  something else. No route above changes this; changing it would be a separate patch against
  vanilla's variety design.
- **Joy kinds lump the skill games together.** All three vanilla Shooting games (horseshoes,
  hoopstone, billiards) share `Gaming_Dexterity`, and chess, poker and Ur share
  `Gaming_Cerebral` [V]. Boredom therefore arrives on the whole skill at once, not on one game.
  A distinct `joyKind` for new training content is an XML lever for the build map.
- **Preference changes *what*, never *when*.** When recreation happens is set by
  `ThinkNode_Priority_GetJoy`: the timetable plus the joy level [V]. No route here makes a pawn
  take recreation more often.
- **Hard per-pawn exclusions stand.** `pctPawnsEverDo` is a per-pawn roll seeded on
  `thingIDNumber` [V]. Required capacities, the outdoors preference and conceited royal titles'
  `disabledJoyKinds` [V] all remove a giver before any weight applies.
- **Passion has exactly three values.** `Passion` is None / Minor / Major, and
  `SkillRecord.LearnRateFactor` throws on anything else [V]. No mod on disk adds a passion level
  (the sweep below). A mod that did would need handling in the factor.
- **No weight from a mod setting.** Settings are client-local, so a settings slider for the
  factor desyncs unless it is synced. **T-18**. Put the numbers in a def or a
  `DefModExtension`.

### Available mechanisms

**The 1.6 selection chain, decompiled** (`RimWorldWin64_Data/Managed/Assembly-CSharp.dll`):

1. `ThinkNode_Priority_GetJoy.GetPriority`: *whether* to seek recreation (timetable, joy
   level, lord) [V].
2. `JobGiver_GetJoy.TryGiveJob`: for every `JoyGiverDef` it computes
   `chance = Worker.GetChance(pawn) × max(0.001, (1 − tolerance[joyKind])⁵)`, after skipping
   givers that are disallowed, bored, unable (`CanBeGivenTo`) or excluded by `pctPawnsEverDo`.
   It then takes `TryRandomElementByWeight` and tries the winner, zeroing the weight and
   redrawing on failure [V]. Subclasses `JobGiver_IdleJoy`, `JobGiver_GetJoyInBed` and
   `JobGiver_GetJoyInGatheringArea` override only the gates and the dispatch [V].
3. `JoyGiver.GetChance(pawn)` returns `def.baseChance` [V]. **This is the only per-pawn weight
   hook.** In vanilla it is overridden twice: `JoyGiver_Skygaze` (weather factor, calls
   `base`) and `JoyGiver_TakeDrug`, which reads the `DrugDesire` trait (×2 / ×5, does not call
   `base`) [V]. **TakeDrug is the in-seam donor for a trait-aware weight**, and route C copies
   its shape. The passion-weighted donor is `InspirationWorker.CommonalityFor` (below).
4. Inside the winning giver, the thing is chosen: the closest reachable building for
   `JoyGiver_InteractBuilding` [V], or a random outcome-providing book for `JoyGiver_Read`
   (`BookUtility.TryGetRandomBookToRead`) [V].
5. `JoyUtility.JoyTickCheckEnd` grants `curJob.def.joySkill` experience each tick [V]. It is
   keyed on the job, so the skill is known at giver level from `def.jobDef.joySkill`.

**Passion appears nowhere in steps 1–5** [V, full read of the decompiled types]. That confirms
the ticket's [I]. Elsewhere, vanilla reads passion in several places:
- `SkillRecord.LearnRateFactor` (0.35 / 1 / 1.5) [V].
- **`InspirationWorker.CommonalityFor`** [V] weights each inspiration's chance by the pawn's
  passion in the def's `associatedSkills`: ×1 none, ×2.5 minor, ×5 major, taking the highest.
  **This is the closest vanilla donor for route A.** It is a skill-keyed, passion-weighted
  chance, the same shape with `joySkill` in place of `associatedSkills`.
- The mood thoughts `SkillBookPassion`, `ThoughtWorker_PassionateWork` and
  `ThoughtWorker_LoveReading` [V].
- By the orchestrator's review [I here]: the `SkillRecord.Learn` mastery tale at level 14,
  work-tab widgets (`WidgetsWork`) and growth moments.

None of these readers feeds recreation choice.

**Corpus sweep: nothing weights recreation by skill or passion** [V]. Both roots, 1.6-loading
paths, `obj/` and `Referenced/` excluded.
- Every assembly naming `JoyGiver` / `JobGiver_GetJoy` / `JoyGiverDef` (ASCII) was checked, and
  so was every one with a `JoyGiver` / `GetJoy` UTF-16 literal: VFE Furniture, VEF, VFE
  Classical, VFE Medieval 2, VRE Android, Knick Knacks and Worksites Expanded. Their recreation
  classes were decompiled. The only chance patch is Knick Knacks' decorate on/off gate. VFE
  Medieval 2's passion code (`HediffComp_LearningPassionsModifier`) scales learning rate, not
  choice. VRE Android's `JoyGiver_Meditate_Patch` blocks meditation for the no-joy gene.
  Worksites Expanded runs its own passion-blind picker (route A, *Cannot*). No `GetChance`
  override exists outside vanilla [V].
- No assembly names `JobGiver_GetJoy` [V]. The same sweep finds it three times in
  `Assembly-CSharp.dll`, which validates it.

**Reach: what recreation trains, across the whole bin** [V]. There are 20 distinct `JobDef`s
with `joySkill` on 1.6 paths, from six carriers, covering **5 of 12 skills**:

| Skill | Jobs | Carriers |
|---|---|---|
| Intellectual | 9 | Core (chess, Ur, poker, telescope), VFE Settlers (faro, five-finger fillet), Medieval Overhaul (three games) |
| Shooting | 6 | Core (horseshoes, hoopstone, billiards), VFE Furniture (darts), VFE Medieval 2 (archery), VQE Ancients (foosball) |
| Melee | 2 | VFE Furniture (punching bag), VFE Medieval 2 (training dummy) |
| Artistic | 2 | Core (instrument), VFE Furniture (piano) |
| Social | 1 | VFE Furniture (roulette) |

**No recreation job trains** Construction, Mining, Cooking, Plants, Animals, Crafting or
Medicine. VFE Furniture's Crafting computers survive only in its ≤1.4 folders. Two sources
agree: an lxml parse (29 elements) and a ripgrep line count (29). VFE Furniture also ships
`ExtendedSitFacingJoyDataExtension.extraJoySkill`, a second skill per *building* in XML, used
only for Intellectual [V]. Its child-learning computer trains Intellectual through
`LearningUtility`, not recreation [V].

**What the reach finding means.** No preference route creates reach. A and B only redistribute
among recreation that exists. For the seven uncovered skills there are two answers.
Textbooks (route D) already cover every skill in vanilla. Otherwise new recreation `JobDef`s
with `joySkill` are plain XML content that route A picks up with no further code. That is
the build map's content.

**Not a route: precepts, memes and mood.** No vanilla precept or meme field touches recreation
choice. The XML field census of `Data/` finds joy fields only on joy defs, royal titles
(`disabledJoyKinds`, a gate) and expectations [V]. Vanilla Memes Expanded records a
`VME_HavingFun` history event from `JoyTickCheckEnd` [V]. That lets an ideology *react* to
recreation but not steer it. A mood reward for passion recreation (donor: `SkillBookPassion`)
is a possible complement. Mood is never read by the selection chain [V], so it does not
satisfy the requirement.

**Passion, for the sibling ticket** [#156](https://github.com/cjd721/Rimworld-Archinity/issues/156).
`SkillRecord.passion` is a scribed `Passion` enum with three values [V]. No `PassionDef`-style
def type and no Vanilla Skills Expanded exist on disk (a tag sweep plus an `About.xml` sweep)
[V]. VFE Medieval 2 changes passion *learning rate* through a hediff comp and static
dictionaries [V].

### Status

- **Verified [V]:** the chain above, decompiled from 1.6 `Assembly-CSharp.dll`; the joy-skill
  census (two sources); the corpus sweep (both heaps, validated); Knick Knacks' `GetChance`
  postfix; the think-tree and duty sites of `JobGiver_GetJoy`.
- **Inferred [I]:** that routes A–F compose as described. None is built. That the think tree
  runs on the synced pawn tick is inferred from `Pawn.Tick` being on the tick list
  (`docs/engine/determinism.md` § *What is on the synced tick*). The path from
  `Pawn_JobTracker` to the think tree was not re-read. That nothing calls `GetChance` from UI
  code outside `DebugOutputsJoy` is also inferred.

### Open questions

- **The passion factor.** The requirement settles the gate: any passion, major first. How
  strong major is against minor is balance for
  [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119), and it must be judged
  against the tolerance curve.
- **Drift or hard preference** (A versus B). This is a story call, owned by
  [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).
- **Textbooks as "recreation that trains a skill".** Capability: route D (*Routes*); with it,
  reach is complete.
- **Softening boredom for a passion.** Not asked for by the requirement. Capability: the
  bored-skip and the tolerance multiplier both sit in `JobGiver_GetJoy.TryGiveJob` (route B's
  gate override, route F's line); separate `joyKind`s for training content spread boredom in
  XML.
- **Build questions for #119:** whether A also reads VFE Furniture's `extraJoySkill`; the
  def or extension that carries the numbers; whether a pawn whose passion skill is at its cap
  still prefers it, since books already skip maxed skills and joy jobs do not.
