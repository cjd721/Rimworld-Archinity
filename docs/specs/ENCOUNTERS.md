# Encounters

## Purpose and scope

How an **optional, authored quest** reaches the player on a timer, from a giver the game draws
at random from the factions the player is at peace with, and delivers what it carries either at
a site the player travels to or through a group that visits the colony and uses something
already standing there.

It answers [`docs/requirements/ALTAR.md`](../requirements/ALTAR.md) § *Altar, Anima and
Biological Progression* — *"One optional encounter may teach what anima is … offered and never
imposed: it arrives on its own schedule, from a faction the player is neutral or better with,
it grants no psylink, it gates nothing"* — and was established on
[#158](https://github.com/cjd721/Rimworld-Archinity/issues/158). The anima-tree encounter is
the campaign case; nothing below is specific to it except where it says *anima tree*.

**Why a document of its own, not a section of [`CHARTING.md`](CHARTING.md).** By
[`QUESTS.md`](../requirements/QUESTS.md)'s announcement test this quest is **not** Charting
content: somebody tells the colony about it, so it arrives as an ordinary letter on the
storyteller or giver channel. Charting owns discovery; this document owns the *told* optional
encounter, and any later encounter of the same shape (timer, random friendly giver, away or
home delivery) joins it. Charting's quest machinery is cited, not restated.

Whether the campaign keeps the encounter is
[#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s call. Pacing of optional
content belongs to [`PRESSURE.md`](PRESSURE.md) (numbers:
[#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)); quest presentation to
[`QUESTS.md`](../requirements/QUESTS.md).

## Verdict

- **Possible?** **Yes, all four parts.** The timer, the random giver with a neutral-or-better
  floor, and the site delivery are **XML on shipped vanilla machinery**. The visiting group that
  walks to the **anima tree** and venerates it is a **vanilla quest part with no XML node** —
  one small C# node, copying Ideology's reliquary pilgrims. A **numeric** goodwill floor (as
  opposed to "not hostile") is not XML either.
- **Multiplayer?** **Yes.** Everything runs in the storyteller tick and in quest generation,
  which are simulation; acceptance is synced by Multiplayer as shipped. Two timer routes (T2, and
  T7 when it is added to a running save) have a join-time edge case, below.

**If only one of the two deliveries is cheap, it is the site.** Site delivery is Easy (XML).
Visitors who arrive and hang about are Easy too, but they cannot be aimed at the tree from XML;
visitors who **go to the tree** are Medium.

## Routes

The ticket asked four things; each has its own routes. A build takes one row from each of
tables 1, 2 and 3-or-4, plus a payload from table 5.

### 1. The timer — what offers the quest after X days

The offer is an `IncidentDef` on `IncidentWorker_GiveQuest` with `questScriptDef` set, which
`IncidentWorker_GiveQuest.TryExecuteWorker` turns into an offered quest and a letter **[V]**
(already recorded in `docs/engine/quests.md`, *Offers*). The route question is what fires that
incident.

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **T1 — `StorytellerComp_SingleOnceFixed`** | One offer on day X. Royalty's intro quests use exactly this | vanilla | XML | Easy | Yes |
| **T2 — `StorytellerComp_RefiringUniqueQuest`** | One offer after day X, **re-offered** N days after it expires unaccepted | vanilla | XML | Easy | With work |
| **T3 — natural random pool** (`rootEarliestDay`) | May be offered any time after day X, by weight | vanilla | XML | Easy | Yes |
| **T4 — our comp: fire after day X, retry until offered** | T1 without its silent miss | our code | C# | Medium | Yes |
| **T7 — VEF quest chain, `conditionMinDaysSinceStart`** | One offer on a day **drawn from a range**, scheduled at game start and saved | VEF | XML | Easy | Yes, if scheduled at game start; **with work** otherwise (below). Every `TestRun` gate is dead (**T-71**) |
| T5 — a `GameComponent` timer | Same as T4 | our code | C# | Medium | Yes — **not recommended**: T4 does it inside the storyteller, where cadence already lives |
| T6 — a Charting pool entry | — | Charting | — | — | **Not recommended**: wrong channel, and it cannot be selected (below) |

**T1 — `SingleOnceFixed`.** The shipped precedent: `Core/Defs/Storyteller/Storytellers.xml`'s
`BaseStoryteller` fires `GiveQuest_Intro_Wimp` on day 8 and `GiveQuest_Intro_Deserter` on day 26
this way **[V]**.
- *Levers (XML):* `fireAfterDaysPassed`; `minColonistCount` (the count, then the clock restarts
  from when it was reached); `skipIfColonistHasMinTitle`; `skipIfOnExtremeBiome`; the base
  `minDaysPassed`, `allowedTargetTags`, `enableIfAnyModActive` **[V,
  `StorytellerCompProperties_SingleOnceFixed`, `StorytellerCompProperties`]**. The
  `IncidentDef`'s own `earliestDay` also applies, because a storyteller fire is not `forced`.
- *Cannot:* retry. `MakeIntervalIncidents` yields on exactly one 1000-tick interval —
  `TicksGame / 1000 == fireAfterDaysPassed * 60` — without testing anything, and
  `Storyteller.TryFire` then calls `CanFireNow`; a `false` is dropped and nothing ever asks
  again **[V, `StorytellerComp_SingleOnceFixed.MakeIntervalIncidents`,
  `Storyteller.StorytellerTick`, `Storyteller.TryFire`]**. `IncidentWorker_GiveQuest.CanFireNowSub`
  runs the quest's `CanRun` **[V]**, so if on that interval there is **no eligible giver** (§2)
  or **no anima tree** (§4), the encounter is lost for the whole campaign, with no log line
  (**T-157**). See *Constraints*.
- *Consequences:* the comp must be in **every** storyteller the players can pick — for us, the
  abstract `Archinity_BaseStoryteller` in [`PRESSURE.md`](PRESSURE.md) §1. Append it at the
  **end** of the comp list: inserting re-salts every later comp's schedule (**T-66**).

**T2 — `RefiringUniqueQuest`.** Vanilla uses it for the Royal Ascent and Archonexus endgame
offers **[V]**.
- *Levers:* `minDaysPassed`; `refireEveryDays` (re-offer that many days after the last one
  **ended without success** — an ignored, expired offer comes back); `minColonyWealth`
  **[V, `StorytellerComp_RefiringUniqueQuest.MakeIntervalIncidents`]**. It looks the quest up by
  `root`, so it never stacks two offers.
- *Cannot:* retry within a session either. The first offer is attempted on exactly one interval
  (`minDaysPassed * 60 + 1`), and `CanFireNow` is checked there **[V]**. **On load** the comp's
  `Initialize` sets a private `generateSkipped` flag whenever the day has already passed, and
  from then it tries every interval until a quest exists **[V; `Storyteller.ExposeData` calls
  `InitializeStorytellerComps` on `ResolvingCrossRefs`]**.
- *Multiplayer — with work.* `generateSkipped` is **not scribed**. If the one window was missed,
  a client that joins by loading the host's save has `generateSkipped = true` while the running
  host still has `false`, and the two storytellers disagree about firing **[I — the fields are
  V; that a joining host does not re-run `Initialize` is inferred]**. Harmless while the window
  is not missed; fatal when it is. T4 is the clean version.

**T3 — the natural random pool.** A `QuestScriptDef` with `rootSelectionWeight > 0` and
`rootEarliestDay = X` joins vanilla's own random quest draw
(`NaturalRandomQuestChooser.GetNaturalRandomSelectionWeight`, which also applies `rootMinPoints`,
`rootMinProgressScore`, `minRefireDays` and recent-quest anti-repetition) **[V]**.
- *Gets:* optional content paced as vanilla paces all of it — `QUESTS.md`'s *Storyteller pool*
  channel, and *"optional content is free to be as lucky as it likes."*
- *Cannot:* promise it arrives, or arrives once. It is a weighted roll among every other
  eligible quest, and it recurs unless `minRefireDays` or a `QuestNode_QuestUnique` stops it.

**T4 — our comp.** A ~T2 with the one-interval window replaced by *"day ≥ X and no quest with this
root exists"*, checking `CanFireNow` before it yields. The donor is
`StorytellerComp_RefiringUniqueQuest` **[V]**; reading "has it been offered" from
`Find.QuestManager` by `root` stores nothing, so there is nothing to desync (quests are never
pruned — `docs/engine/quests.md`, *Offers*). **[I]** until built.

**T7 — VEF's quest chains.** A `QuestChainExtension` on the `QuestScriptDef` with
`conditionMinDaysSinceStart` makes `GameComponent_QuestChains.TryScheduleQuest` — run at
`StartedNewGame` and `LoadedGame` — roll a day from the range and store a `FutureQuestInfo`
(scribed); `GameComponentTick` fires it when `TicksGame` reaches that tick, through
`QuestUtility.GenerateQuestAndMakeAvailable`, so it arrives as an ordinary offer **[V,
`VEF.Storyteller.GameComponent_QuestChains`, `FutureQuestInfo.TryFire`,
`2023507013/1.6/Assemblies/VEF.dll`]**. It is deduplicated against pending, live and (unless
`isRepeatable`) past copies **[V]**.
- *Gets:* a timer that lives outside the storyteller, so it works under **any** storyteller the
  players pick; a randomised day rather than a fixed one; no missed window, because the fire
  does not ask `CanFireNow`.
- *Cannot:* test anything. The chain path never runs `TestRun` (**T-71**), so a giver or tree
  that is missing on the day is not a refusal but a **broken quest** — `QuestNode_GetFaction`'s
  `RunInt` still draws, and on finding nothing leaves `giver` unset **[V, `RunInt`]**. The
  quest's own nodes must branch on absence. The re-grant fields carry **T-72** and **T-73**.
- *Consequences:* the quest belongs to a `QuestChainDef`, and so to VEF's chain bookkeeping.
- *Multiplayer.* `GameComponent_QuestChains.LoadedGame` runs `TryScheduleQuests` **[V]**. A
  client that joins by loading runs it, and the running host does not **[I]**.
  - **Harmless** for a day range scheduled at `StartedNewGame` and saved: the load finds the
    scribed `FutureQuestInfo` and returns early.
  - **Not harmless** for a quest added to a running save, or one gated on `requiredResearch`
    finished mid-game. There the joining client schedules, with its own `Rand` roll, a quest
    the host never schedules.

**T6 — why Charting is the wrong carrier, not merely a heavier one.** Charting's survey pool
ranks candidates by the same `GetNaturalRandomSelectionWeight`, which returns 0 for
`rootSelectionWeight <= 0` **[V]**; a special-root quest therefore cannot win there, and a
weighted one is T3 behind a labour gate. More to the point, the announcement test puts a
faction's approach outside Charting (*Purpose*).

**Keeping the quest out of every pool it was not written for.** Set `isRootSpecial` and leave
`rootSelectionWeight` at 0: `IsRootRandomSelected` is then false, so neither vanilla's random
draw nor Charting's survey pool can pick it, and `IsRootAny` stays true so it is still a legal
root **[V, `QuestScriptDef.IsRootRandomSelected` / `IsRootAny`]**. Intro_Deserter is written
exactly so **[V]**.

**Recommendation, not a selection.** T1 if the quest's own `TestRun` cannot fail on the day
(see *Constraints* for how to make it so); T4 if it can. T3 if the narrative prefers "it may
happen" to "it happens". T7 if a randomised day or storyteller independence matters more than
a live eligibility test — T1 and T7 fail in opposite directions: T1 **skips** when the quest
cannot run, T7 **generates it anyway**.

### 2. The giver — drawn at random, neutral or better

[#136](https://github.com/cjd721/Rimworld-Archinity/issues/136) established that vanilla picks
the faction at random for the caravan meeting (`docs/engine/storyteller-and-incidents.md`,
*Caravan encounters*). The same holds for quests, and the floor is expressible.

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **G1 — `QuestNode_GetFaction`** | A uniformly random faction, not hostile | vanilla | XML | Easy | Yes |
| **G2 — `QuestNode_GetPawn` as asker** | A named leader from a random non-hostile faction, with a faction-def exclusion list | vanilla | XML | Easy | Yes |
| **G3 — our node: numeric goodwill floor or tech ceiling** | "Goodwill ≥ 20", "tribal only" | our code | C# | Medium | Yes |

**G1.** `QuestNode_GetFaction.TryFindFaction` is `TryRandomElement` over
`FactionManager.GetFactions(allowHidden: true)` — which already drops the player, defeated and
temporary factions — filtered by `IsGoodFaction` **[V]**. Neutral-or-better is:

```xml
<li Class="QuestNode_GetFaction">
  <storeAs>giver</storeAs>
  <allowEnemy>false</allowEnemy>
  <allowNeutral>true</allowNeutral>
  <allowAlly>true</allowAlly>
  <allowPermanentEnemy>false</allowPermanentEnemy>
</li>
```

- *Levers:* also `leaderMustBeSafe`, `playerCantBeAttackingCurrently`,
  `mustHaveGoodwillRewardsEnabled`, `exclude` (a slate list of faction **instances**),
  `allowedHiddenFactions` **[V, `QuestNode_GetFaction`]**.
- *Cannot:* filter by goodwill **number**, tech level or faction def. **`allowNeutral` and
  `allowAlly` default to `false`** — omit them and the node finds nothing, which under T1 is the
  silent miss.
- *Note:* "neutral" here is the **relation kind**, which is latched, not a function of the
  number: a faction coming down from +10 stays Neutral until −75 (`docs/engine/quests.md` §
  *The accept-time gate is one abstract base, with a quest-wide half and a per-pawn half*). Neutral-or-better in the requirement's words is exactly
  "not Hostile" in the engine's.

**G2.** Vanilla's asker idiom, `Royalty/.../Scripts_Utility.xml` `Util_DecideRandomAsker`
**[V]**: `QuestNode_GetPawn` with `mustBeFactionLeader`, `mustBeNonHostileToPlayer`,
`excludeFactionDefs`, `minTechLevel`, `hostileWeight` / `nonHostileWeight` **[V,
`QuestNode_GetPawn.IsGoodPawn`]**.
- *Gets:* a person to name in the letter (`[asker_nameFull]`, the faction through
  `[asker_factionName]`); a **def** filter, which G1 lacks.
- *Cannot:* express "tribal only" positively — `minTechLevel` is a floor and the tribes are the
  lowest tier, so the only tribal filter is `excludeFactionDefs` listing everything else **[V]**.
  With `mustBeFactionLeader`, one candidate per faction, so the draw is near-uniform by faction
  **[I]**.

**G3.** Vanilla's `IsGoodFaction` is `private`, so the route is a new node of ~G1's size with a
`minGoodwill` / tech or def filter, not a subclass. **Not** a postfix on `IsGoodFaction`: VEF does
exactly that (`VanillaExpandedFramework_QuestNode_GetFaction_IsGoodFaction_Patch`, reading
`FactionDefExtension.excludeFromQuests`) **[V]**, and it is global — it removes a faction from
**every** quest. Needed only if the narrative wants a number or a culture, not "not hostile".

**VEF levers, not routes.** VEF's own `VEF.Storyteller.QuestNode_GetFaction` adds `factionDef`,
which **pins** the first faction of a def and is therefore not random; `excludeFromQuests` is the
global exclusion above **[V, `2023507013/1.6/Assemblies/VEF.dll`]**.

### 3. Delivery at a site the player travels to

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **S1 — an ordinary generated site under the giver's faction** | A map the player caravans to, with an anima tree and the giver's people, and a passage on arrival | vanilla | XML | Easy | Yes |
| S2 — a map-less world object, PeaceTalks-shaped | A meeting on arrival, no map | vanilla donor | C# | Medium | Yes |

**S1.** Every shipped site quest: `QuestNode_GetSiteTile` (`siteDistRange`) →
`QuestNode_GenerateSite` (`sitePartsParams`, **`faction`**, `tile`) →
`QuestNode_SpawnWorldObjects`, with passages fired on `site.MapGenerated` **[V — node fields
read; `site.MapGenerated` is the signal vanilla XML uses]**.
- *Levers:* the site's faction is the giver from §2. To put the giver's people on the map, the
  named carrier is the worshipful village's: a `SitePartDef` with `ParentName="Outpost"` plus a
  `GenStepDef` running `GenStep_Outpost` with a `pawnGroupKindDef` (`Settlement_RangedOnly`),
  which spawns the **site faction's** pawns **[V, `Ideology/Defs/Sites/WorshippedTerminal.xml`]**.
  That def uses a temporary faction it generates itself. That the same pair, handed an existing
  non-hostile faction, gives peaceable villagers is **[I]**. A `GenStepDef` with `linkWithSite`
  places an anima tree — Royalty's `GenStep_AnimaTrees` or
  Vanilla Landmarks Expanded's single ancient tree (`VEE_AncientAnimaTree`,
  `3656316229/1.6/Defs/MapGeneration/MutatorGenSteps.xml`) are both XML **[V defs; I that they
  compose]**; a `QuestNode_Letter` on arrival; an inspectable lore object through
  [`CHARTING.md`](CHARTING.md) §10.
- *Closest precedent:* Ideology's **worshipful village** — a non-hostile tribal village around
  a venerated object, with a stay timer and hostility on rule-breaking
  (`Ideology/Defs/Sites/WorshippedTerminal.xml`) **[V]**. Its root is C#
  (`QuestNode_Root_Hack_WorshippedTerminal`) and it generates a *temporary* faction rather than
  using an existing one **[V]**, so it is the shape to imitate, not a node to reuse.
- *Cannot:* make the player go. That is the point of optional; it also means the whole payload
  sits behind a caravan trip, which in the Neolithic is a real cost.
- *Cannot:* be revisited. **Leaving a vanilla quest site destroys it**
  (`Site.ShouldRemoveMapNow` → `alsoRemoveWorldObject`). A lore object must therefore be read
  there or **carried home**, and the passage should fire on arrival (`docs/engine/quests.md`
  § *A quest site's map*, from [#151](https://github.com/cjd721/Rimworld-Archinity/issues/151)).
- *Consequence:* **a site the player never enters outlives its quest.** When the offer expires
  or the quest ends, the site stays on the world map unless the script adds
  `QuestNode_WorldObjectTimeout` with `destroyOnCleanup` (or `QuestNode_DestroyWorldObject`)
  (same section, #151). "Ignoring it costs nothing" therefore needs that node.

**S2.** Vanilla's peace talks are the donor: a world object spawned by an XML quest
(`Core/Defs/QuestScriptDefs/Script_PeaceTalks.xml`, `QuestNode_GetFaction` then
`QuestNode_GenerateWorldObject`) whose arrival resolves in C# **[V]**. Cheaper for the player
than a map, less vivid, and needs a world-object class of ours. Listed for completeness.

### 4. Delivery by a group that visits and uses the anima tree

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| V1 — `QuestNode_PawnsArrive` + `QuestNode_VisitColony` | Visitors arrive, loiter, leave; a passage is sent | vanilla | XML | Easy | Yes — but **does not reach the tree** |
| **V2 — vanilla `QuestPart_Venerate` aimed at the tree** | The group walks to the tree, venerates it for a set time, signals, leaves | vanilla part + our node | C# | Medium | Yes |
| V3 — our own `LordJob` | Anything, including a colonist drawn into the rite | our code | C# | Hard | With work |

**Is there a shipped way to make a visitor group walk to a specific existing thing and do
something there? Yes — Ideology's reliquary pilgrims.** `QuestNode_Root_ReliquaryPilgrims`
finds a reliquary holding a relic on a player home map, brings 1–4 pilgrims in through
`quest.PawnsArrive`, and adds a `QuestPart_Venerate` whose `target` is that building **[V]**.
`LordJob_Venerate`'s graph is **travel to `target.InteractionCell` → `LordToil_Venerate` for
`venerateDurationTicks` → exit**, sending `outSignalVenerationCompleted` on the way out, and
leaving early if the target takes damage, a pilgrim is killed or the group turns hostile **[V,
`LordJob_Venerate.CreateGraph`]**. `LordToil_Venerate` rotates one pawn close in while the rest
spectate around the target **[V]**.

**V2** is that part, aimed at `Plant_TreeAnima`.
- *What it needs:* `QuestPart_Venerate` has **no XML node** — every vanilla `QuestNode_*` was
  listed and none constructs it, and nothing in the corpus does either (both roots, `.dll` and
  `.xml`, `-g '!**/obj/**' -g '!**/Referenced/**'`, zero hits; the same form found VFED's and
  Glittertech's `QuestNode_MakeLord`) **[V]**. So: one node that finds a spawned anima tree on
  the map (failing `TestRun` if there is none) and adds the part — or a whole root node copying
  the pilgrims'.
- *It works on a tree [I on composition, V on the pieces].* A 1×1 thing without an interaction
  cell resolves `InteractionCell` to a standable adjacent cell
  (`ThingUtility.InteractionCellWhenAt`) **[V]**; the anima tree is a 1×1 plant with no
  interaction cell **[V, `Royalty/Defs/ThingDefs_Plants/Plants_Wild.xml`]**.
- *Levers:* the giver's pawns (from §2's faction) instead of the pilgrims' temporary faction;
  the duration; a passage, thought or hediff on the completion signal (§5); the exits already
  wired — a player who harms the tree or the visitors ends it.
- *Cannot:* involve a colonist. The rite is the visitors'; the colony watches.
- ⚠ *The completion signal does not survive a save before the lord exists.*
  `QuestPart_Venerate.ExposeData` saves `target`, `venerateDurationTicks` and
  `inSignalForceExit` but **not `outSignalVenerationCompleted`**, and `QuestPart_MakeLord` saves
  none of the three **[V]**. Once the lord is made, `LordJob_Venerate` saves the field itself
  **[V]**. A save taken between generation and the part's `inSignal` (an offer left waiting is
  exactly that) reloads the field as `null`. `CreateGraph` then adds no completion action, so a
  payload keyed to that signal **never fires, with no error** **[V]**. Three ways round it:
  - key the payload to the group **leaving**. This is vanilla's own success path:
    `QuestPart_PassAll` over each pawn's `LeftMap`, the pilgrims' `AllLeftMap`. Note that it
    also fires if the group leaves early.
  - a subclass of `QuestPart_Venerate` that saves the field (one line of `ExposeData`).
  - `autoAccept` with the lord made on the quest's initiate signal, which leaves no window.

  See **T-158**.
- *Dependency:* the spectate duty `Pilgrims_Spectate` is **Ideology** content
  (`[MayRequireIdeology]` on `DutyDefOf.Pilgrims_Spectate`) **[V]**. Ideology is on disk and
  active; the DLC floor ([#6](https://github.com/cjd721/Rimworld-Archinity/issues/6)) rules out
  only Anomaly.

**V1** is the XML-only visit. `QuestPart_VisitColony.MakeLord` places the group at
`RCellFinder.TryFindRandomSpotJustOutsideColony` **[V]**; there is no field for a target. The
tree is only in the letter.

**V3** is a lord of our own — donors `LordJob_BestowingCeremony` (Royalty: a visitor comes to a
spot and performs a rite **with** a colonist) and VFE Empire's `LordJob_ArtExhibit` (visiting
nobles tour specific art pieces on the colony's map, a `LordJob_Ritual` subclass)
**[V, `2938820380/1.6/Assemblies/VFEEmpire.dll`]**. Only if a colonist must take part.

**Ruled out: the anima linking ritual.** Its outcome worker is `RitualOutcomeEffectWorker_AnimaTreeLinking`
(`Royalty/Defs/Rituals/Ritual_Outcomes.xml`) **[V]** — it links a psycaster, which the requirement
forbids — and it is gated on the `Natural` focus, i.e. on tribal childhood backstories (**T-27**).
The encounter may *talk* about linking; it must not run it.

### 5. What "teaching" can deliver

The requirement allows pure narrative. Every row is reachable from either delivery.

| Payload | What the player gets | Carrier | Kind | Weight |
|---|---|---|---|---|
| **A passage** | An archived letter, re-readable forever | `QuestNode_Letter` | XML | Easy |
| A memory | A mood thought on the colonists present, which fades | `QuestNode_AddMemoryThought` (`def`, `pawns`) | XML | Easy |
| A mark on a pawn | A permanent, inspectable hediff on the participants | `QuestNode_AddHediff` (`hediffDef`, `pawns`) | XML | Easy |
| A techprint | Research unlocked directly, no item | `QuestNode_GiveTechprints` (`fixedProject`) → `ResearchManager.ApplyTechprint` | XML | Easy — **with a catch** |
| A history event | Ideology precepts react once | `QuestNode_RecordHistoryEvent` | XML | Easy |
| A remembered fact | Later content can ask "did they learn?" | the ended quest itself, read by `root` and `EndedSuccess` | C# read | Medium |
| A readable | A lore object at the site, or a book carried home | [`CHARTING.md`](CHARTING.md) §10 | C# | Medium |

All node fields **[V]**, `Assembly-CSharp.dll`. Notes:

- **The techprint catch.** A project that *needs* this techprint is now gated on the encounter,
  which the requirement forbids. It works only for a project the player can also reach another
  way. Two more **[V, `QuestNode_GiveTechprints`]**:
  - `TestRunInt` fails once the project's `TechprintRequirementMet`. That is a further silent
    miss under T1.
  - Without `fixedProject` the node picks a **random** unfinished project from the whole
    database, of any era.
- **The hediff must be inert** — a label and a description, or a cosmetic effect. Nothing that
  touches psylink or the psychic ladder ([`ALTAR.md`](../requirements/ALTAR.md)).
- **"A remembered fact" costs no storage.** Ended quests are never pruned, so the quest *is*
  the flag; but no XML node reads quest history (`docs/engine/quests.md` §
  *`QuestScriptDef.CanRun` has 16 non-debug vanilla callers*), so whatever consults it is C#.

## Constraints

- **The one-shot miss.** Under T1 (and T2 within a session) the offer is attempted on one
  interval. The quest's `TestRun` must be unable to fail then, or the encounter silently never
  happens. Things that can fail it: no non-hostile faction (G1/G2); `allowNeutral` /
  `allowAlly` left at their `false` default; no anima tree on the home map (V2); no site tile in
  range (S1); a techprint payload whose requirement is already met (§5). The cheap fixes are a fallback branch inside the quest (V2 falling back to S1, or
  an askerless letter), or T4. Under T7 the same absences do not skip the offer — they reach
  generation (**T-71**). The one-shot miss itself is **T-157**.
- **Every storyteller must carry the comp** (T1, T2, T4). A player who picks a storyteller
  without it never gets the offer. For us that is `Archinity_BaseStoryteller`
  ([`PRESSURE.md`](PRESSURE.md) §1), appended last (**T-66**).
- **The anima tree must exist on the day (V2).** `GenStep_AnimaTrees.DesiredTreeCountForMap`
  asks for at least one per player home map at generation, and `BaseStoryteller` carries an
  `AnimaTreeSpawn` `OnOffCycle` comp **[V]**. If `Archinity_BaseStoryteller` does not carry
  that comp over, a cut tree is never replaced **[I]**. The player can cut it
  (`warnIfMarkedForCut` only warns).
- **An offer cannot be declined, only dismissed or left to expire**
  (`docs/engine/quests.md`, *Offers*). "Ignoring it costs nothing" is `expireDaysRange` and no
  failure part — nothing more.
- **No psylink, by construction.** No route above grants one unless a payload is written to;
  the linking ritual is ruled out (§4). **T-27** stands for anything the narrative says the
  founders can do at the tree afterwards.

## Available mechanisms

**Positives.** `StorytellerComp_SingleOnceFixed`, `StorytellerComp_RefiringUniqueQuest`,
`IncidentWorker_GiveQuest`, `NaturalRandomQuestChooser.GetNaturalRandomSelectionWeight`,
`QuestScriptDef.isRootSpecial` / `rootEarliestDay`; `QuestNode_GetFaction`, `QuestNode_GetPawn`;
`QuestNode_GetSiteTile`, `QuestNode_GenerateSite`, `QuestNode_SpawnWorldObjects`;
`QuestNode_PawnsArrive`, `QuestNode_VisitColony`; `QuestPart_Venerate` / `LordJob_Venerate` /
`LordToil_Venerate`; `QuestNode_Letter`, `QuestNode_AddMemoryThought`, `QuestNode_AddHediff`,
`QuestNode_GiveTechprints`, `QuestNode_RecordHistoryEvent`; `GenStep_AnimaTrees`. All
`Assembly-CSharp.dll` 1.6, decompiled with `ilspycmd` 8.2 **[V]**. VEF's
`QuestChainExtension` / `GameComponent_QuestChains` / `FutureQuestInfo` and its
`QuestNode_GetFaction` and `IsGoodFaction` postfix, `2023507013/1.6/Assemblies/VEF.dll` **[V]**.

**Existence proofs.** Royalty's intro quests (T1); Royal Ascent (T2); Ideology's reliquary
pilgrims (V2); Ideology's worshipful village (S1's shape); VFE Empire's art exhibit and Royalty's
bestowing ceremony (V3); Vanilla Landmarks Expanded's ancient anima tree gen step and Vanilla Base
Generation Expanded's `VGBE_TribalCenter` layout, which places an anima tree inside a tribal
settlement (`3209927822/1.6/Defs/LayoutDefs/VGBE_TribalCenter.xml`) **[V defs]**.

**Negatives, each validated.** No XML node constructs `QuestPart_Venerate`, and no corpus mod
references it or `LordJob_Venerate` (sweep above). No XML node aims `QuestPart_VisitColony`. No
XML node reads a goodwill number (`docs/engine/quests.md`). Corpus `minGoodwill` hits are Rim War
and RimPacts only, neither a quest node **[I — names only]**.

## Status

Evidence class **READ**. Established on
[#158](https://github.com/cjd721/Rimworld-Archinity/issues/158). Inherited and cited, not
re-run: [#136](https://github.com/cjd721/Rimworld-Archinity/issues/136) (random faction on the
caravan meeting), [#93](https://github.com/cjd721/Rimworld-Archinity/issues/93) (no XML goodwill
number), [#131](https://github.com/cjd721/Rimworld-Archinity/issues/131) (offers cannot be
declined; `IncidentWorker_GiveQuest`), **T-27**, **T-66**.

Every mechanism above is **[V]** unless marked. **Every route is [I] by construction** — nothing
has been compiled.

## Open questions

- **Narrative, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).** Keep or cut;
  which delivery; which payload; the day.
- **Requirement, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).** Is
  "neutral or better" the relation kind (XML, G1) or a goodwill number (C#, G3)? And should the
  giver be tribal? The requirement names neither.
- **Requirement, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).** Does an
  ignored offer come back (T2 / T4 with a refire) or is it once only (T1)?
- **Build, next map.** Whether the timer's miss is handled by T4 or by a fallback branch inside
  the quest.
- **Build, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).** Whether
  `Archinity_BaseStoryteller` keeps vanilla's `AnimaTreeSpawn` comp; V2 depends on it.
  ([#60](https://github.com/cjd721/Rimworld-Archinity/issues/60), which specified the
  storyteller, is closed.)
- **RUN, narrow.** T2's Multiplayer edge case: after a missed first window, host a game and
  join a client; watch whether one side offers the quest and the other does not. Only matters if
  T2 is selected.
