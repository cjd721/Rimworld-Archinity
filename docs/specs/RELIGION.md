# Religion

## Purpose and scope

> **Authority correction — 2026-09-13.** In this project, **the Church** means the
> Roman-Catholic-like external faction produced by transforming the vanilla Empire
> wholesale. **The player faith** is the colony's player-chosen ideology with campaign
> roles and precepts baked in. They are not the same ideology or institution. The prior
> selections that create a second Church faction, make the player faith become the
> Church's doctrine, give one founder a Church leader seat, or store separate Church
> tolerance/threat state are superseded. Global Reverence drives the Church's political
> reaction. The capability evidence below remains useful, but those builds must be
> reselected against the corrected requirements.

How the religious systems in [`docs/requirements/RELIGION.md`](../requirements/RELIGION.md)
will be built. This document owns four behaviours end to end:

- **Reverence** — the number, the events that move it, the decay that pulls it back, the bands,
  and the surfaces the player reads it on.
- **Exaltation and the sacred titles** — the Church (Royalty's Empire, transformed in place), its
  rising scale, the thresholds that confer permanent titles by rite, the privileges those titles
  unlock, and the Church's suspicion derived from Global Reverence
  ([#53](https://github.com/cjd721/Rimworld-Archinity/issues/53)).
- **The player faith's role hierarchy** — founder-special seats, several core-disciple
  preacher/converter seats, crafting and other specialist seats, and how those roles unlock
  during play. Capability is [#114](https://github.com/cjd721/Rimworld-Archinity/issues/114);
  the authored hierarchy and milestones are [#116](https://github.com/cjd721/Rimworld-Archinity/issues/116).
- **Religious institutions inside foreign factions** — the church or monastery the player plants
  inside another faction, its Reverence gate, its Goodwill price, the decay it offsets and its
  suppression by a hostile government
  ([#73](https://github.com/cjd721/Rimworld-Archinity/issues/73)).

**Two boundaries inside this document matter more than the rest, because both were drawn to stop
one number acquiring two owners.** The institution build **writes** `sustain` on the per-faction
record *The build — Reverence* §1 defines and **adds no store of its own**; and the mechanism that
refuses the founding action until Reverence is high enough, and draws the threshold before it is
reached, is [`POLITICS.md`](POLITICS.md) § *Standing as a content gate* — **this document consumes
that gate and does not restate it**, for every Reverence- and Exaltation-gated action alike.

It does not own **Reverence as a storyteller attention
weight** ([#60](https://github.com/cjd721/Rimworld-Archinity/issues/60)), **vassalage and
revolt** ([#35](https://github.com/cjd721/Rimworld-Archinity/issues/35)), or the **shape of
the political surface** ([#61](https://github.com/cjd721/Rimworld-Archinity/issues/61)) —
this document says what must be drawn and where the draw call goes, #61 decides what window
it lives in. It does not own **Influence and Intel**
([#54](https://github.com/cjd721/Rimworld-Archinity/issues/54), whose spec is
[`CURRENCIES.md`](CURRENCIES.md)) or **Glitterite Trace**
([#56](https://github.com/cjd721/Rimworld-Archinity/issues/56)).

Goodwill and the political ripple are [`POLITICS.md`](POLITICS.md)'s. The two systems are
separate axes by requirement; whether they couple is an open decision, below.

It does not own the **Devotion alignment rule** — what makes a willing sacrifice count as
aligned with the founder's claimed Self — nor **which pawns are founders**. Both are
requirements, and [#49](https://github.com/cjd721/Rimworld-Archinity/issues/49) owns the
first by its own body. This document states what the commitment build needs from each and
nothing more.

## The build — Reverence

Nothing in the corpus carries a per-faction ideology-penetration measure, so Reverence is new
saved state. **What is not new is anything else**: vanilla already ships the departure hook
that observes an apostle going home, the quest-part pattern that makes a custom meter a quest
reward, the deadband-and-timer decay shape, the disabled-with-reason dialogue option that
shows a gate before it opens, and a mod donor for the band ladder. The build is one component,
three postfixes and two Def types.

### 1. The store — `WorldComponent_Reverence`

**Mechanism.** One `WorldComponent` subclass in the existing `ArchinityAltar.dll`, holding a
list of per-faction records. `RimWorld.Planet.WorldComponent` is `IExposable`, requires a
`(World world)` constructor, and declares `WorldComponentTick()` and
`FinalizeInit(bool fromLoad)` [V]. `World.FillComponents` instantiates every non-abstract
subclass reflectively via `Activator.CreateInstance(type, this)` and logs an error rather than
failing silently when the constructor is wrong [V].

The alternatives stay ruled out [V]: `RimWorld.Faction` has no comps list, so there is no
extension point on a faction instance; a `DefModExtension` on `FactionDef` is shared across
instances and defs are not scribed, which is **T-11** exactly and fails silently; a
`GameComponent` would work but the state is world-scoped and `GameComponent`s scribe by class
name.

**State.** A `List<FactionReverence>` of nested `IExposable` records, one per faction that has
ever had a non-zero value:

| Field | Purpose |
|---|---|
| `Faction faction` | the key, scribed `Scribe_References.Look` — `Faction` is `ILoadReferenceable` [V] |
| `float value` | the number the requirement calls "57 out of 100" |
| `float sustain` | institutional resistance to decay — **written by *[The build — religious institutions inside foreign factions](#the-build--religious-institutions-inside-foreign-factions)* below, read here**. That section also nests a `List<Institution>` beside it and recomputes this field from it; nothing else about this record or the decay changes |
| `int decayTimer` | the neglect counter, on `Faction.naturalGoodwillTimer`'s pattern [V] |
| `ReverenceBandDef lastBand` | the band as of the last crossing, so a change can be announced once |

**A list, not a `Dictionary<Faction, float>`, and the reason is determinism.** Vanilla does
ship the dictionary form — `HistoryEventsManager` holds
`Dictionary<Faction, DefMap<HistoryEventDef, HistoryEventRecords>>` and scribes it with
`Scribe_Collections.Look(…, LookMode.Reference, LookMode.Deep, …)` [V], which is a better
precedent than the VFED `Dictionary<Site, …>` the earlier draft cited. But vanilla only ever
iterates it to prune. Our decay pass iterates to *simulate* and can send letters, and
[`POLITICS.md`](POLITICS.md) § *Persistence and multiplayer* already forbids iterating a
`Dictionary` or `HashSet` of factions to drive simulation. A list is insertion-ordered and
costs nothing at this scale.

**Global Reverence is derived, never stored.** It is a function of the records — planetary
adoption weighted however the requirement eventually says — computed when it is drawn or when
the global band is checked. No second number to keep in sync, no second thing to scribe.

### 2. Persistence

`ExposeData` does one `Scribe_Collections.Look(ref records, "reverence", LookMode.Deep)`; each
record scribes its own `Faction` reference and values.

**Adding this to a save that predates it is safe, and this is verified rather than assumed.**
`World.ExposeComponents` runs
`Scribe_Collections.Look(ref components, "components", LookMode.Deep, this)` and then calls
`FillComponents()` **again**, which backfills every `WorldComponent` subclass the save did not
contain [V]. The component initialises with an empty record list, which is the correct
starting state.

`FinalizeInit(fromLoad: true)` prunes records whose `faction` resolved to null — a faction
removed through `FactionManager.toRemove`. **What *should* happen to a removed faction's
Reverence is a requirements question**, handed to
[#97](https://github.com/cjd721/Rimworld-Archinity/issues/97); pruning is the safe default
until it answers.

### 3. What changes it

Three routes, and the first is the one the requirement cares about most.

**A. The apostle hook — one Harmony postfix on
`RimWorld.Faction.Notify_MemberExitedMap(Pawn member, bool freed)`.**

This single public method covers three of requirement 3's four clauses [V]:

- Its main call site in `Pawn.ExitMap` is `base.Faction?.Notify_MemberExitedMap(this, flag4)`,
  so `__instance` is normally **the departing pawn's own home faction** — exactly the faction
  whose Reverence should move. **There is a second call site two lines down** [V]: for a
  player-faction slave with a non-player `SlaveFaction`, `ExitMap` also calls
  `SlaveFaction.Notify_MemberExitedMap(this, flag4)`, where `__instance != member.Faction`.
  **Read `__instance`, never `member.Faction`** — on that path `member.Faction` is the player.
- `freed` is vanilla's already-computed
  `(IsPrisoner || IsSlave) && guest != null && guest.Released`, so **a released prisoner and a
  departing guest arrive at the same hook already distinguished**.
- It fires *before* `Pawn.ExitMap` clears the guest state (`guest.SetGuestStatus(null)`,
  `guest.Released = false`), so guest status is still readable.
- `member.Ideo` and `member.ideo.Certainty` are intact, so "sincerely converted" is a readable
  condition rather than an inferred one.
- It is vanilla's own convergence point for *"a member of your faction left our colony, adjust
  how you feel about us"* — the goodwill gain for releasing a healthy prisoner is computed
  here. Reverence is the second axis on the same event, which is what the requirement asks for.

**Vanilla pilgrims do *not* reach it usefully, and this is the one requirement clause the hook
does not cover.** `QuestScriptDef ReliquaryPilgrims` / `QuestNode_Root_ReliquaryPilgrims` exist,
but the node calls
`FactionGenerator.NewGeneratedFactionWithRelations(factionDef, list, hidden: true)` and sets
`faction.temporary = true` [V]. So a departing pilgrim's `__instance` is a **throwaway hidden
faction created for that quest**: Reverence credited to it is orphaned when the quest ends,
hits the null-prune path in §2, and can never be displayed, because hidden factions are
filtered out of `FactionUIUtility.DoWindowContents`. Vanilla itself special-cases this — it
passes `!temporary` as the `canSendMessage` argument to `TryAffectGoodwillWith`.

**Pilgrims therefore need an authored arrival**, not vanilla's: a Reverence-gated pilgrim quest
whose visitors belong to the *real* reverent faction. That is the requirement's own framing —
*"pilgrims **from reverent factions**"* — and it is quest work on route B below, not a second
hook. Recorded because the hook otherwise looks like it covers all four clauses; it covers
three.

Two guards the postfix needs [V]: skip `__instance == Faction.OfPlayer` (a colonist leaving
the map raises the same hook), and respect
`member.mindState.AvailableForGoodwillReward` — `Find.TickManager.TicksGame >= noAidRelationsGainUntilTick`
— which is vanilla's existing anti-farming gate applied inside this very method.

**There is no caravan escape path.** An earlier draft claimed a converted pawn leaving inside a
player caravan bypasses the hook. It does not [V]: both caravan branches re-enter with the flag
off — `ExitMapAndJoinOrCreateCaravan` does `caravan.AddPawn(pawn, true); pawn.ExitMap(false, exitDir)`,
and `ExitMapAndCreateCaravan` passes `addToWorldPawnsIfNotAlready: false` — so `IsWorldPawn()`
is false on re-entry and the full body runs through to `Notify_MemberExitedMap`. The only branch
that skips it is the `Log.Error("didn't find any caravan to join…")` fallthrough, which
`CanExitMapAndJoinOrCreateCaravanNow` has already excluded. **Note the `freed` value differs on
that path**, because the re-entry recomputes it.

**B. The deed and quest route — `QuestPart_ReverenceChange` + `QuestNode_ChangeReverence`.**

Requirement 3's remaining clause — public deeds and selected quest outcomes, "publicly
attributed to the founders and their faith" — is quest-scoped, and quest-scoped consequences
belong in a `QuestPart`. Two donors, both read [V]:

- Vanilla's `QuestNode_ChangeFactionGoodwill` → `QuestPart_FactionGoodwillChange` is the exact
  shape: a `SlateRef<Faction>`, a `SlateRef<int> change`, an `inSignal`, and the part scribing
  both. Copy it with Reverence in place of goodwill.
- VFED's `QuestPart_ChangeVisibility` and `Reward_Visibility : Reward` prove the same pattern
  works for an invented meter, including appearing in the quest's reward stack [V]. A
  `Reward_Reverence` is what makes *"Reverence as an alternative outcome to loot or Goodwill"*
  a thing the player chooses rather than a thing that happens to them.

**`QuestPart_RecordHistoryEvent` cannot substitute for this.** It records
`new HistoryEvent(historyEvent)` with **no args at all** — no `Doer`, no `AffectedFaction` [V]
— so a quest-driven history event carries no faction attribution and cannot move a per-faction
number. This is worth stating because `QuestNode_RecordHistoryEvent` is pure XML and looks like
the free answer.

**C. Optional generalisation — a postfix on `HistoryEventsManager.RecordEvent`.**

If we want *"which events move Reverence, and by how much"* to be entirely XML, one postfix on
`RecordEvent` plus a `HistoryEventDef → amount` table gets it: the faction resolves from
`HistoryEventArgsNames.AffectedFaction` where present, falling back to `Doer.HomeFaction`
otherwise. The arg names are [V]; **the fallback is our design, not vanilla's** — vanilla files
a `Doer` event into `colonistEvents` only when the doer `IsColonist`, and resolves no faction at
all, so that half is [I].
Vanilla's own `PreceptComp_DevelopmentPoints` is the same idea one layer up — an XML comp
carrying `eventDef` and `points`, dispatched from `IdeoUtility.Notify_HistoryEvent` [V].
`RecordEvent` has no listener registry [V], so this is a Harmony patch and not an extension
point. **Recommended only if C actually earns its keep** — A and B cover every clause the
requirement states, and C adds a hook that fires on every history event in the game.

### 4. Decay

In `WorldComponentTick`, on a modulus, copying `Faction.CheckReachNaturalGoodwill`'s shape [V]:
a deadband, a `decayTimer` that resets whenever the value moves, a threshold, and a step capped
at a small constant. The step is reduced by the record's `sustain`, which is the institution
build's only required interface: **it writes `sustain`, this reads it.** A faction whose
institutions fully offset decay holds its value; the requirement's *"institutions deliberately
counteract natural Reverence decay and can eventually make the faith self-sustaining"* is that
subtraction and nothing more. **Self-sustaining is an inequality, not a state** — see
*[The build — religious institutions inside foreign factions](#the-build--religious-institutions-inside-foreign-factions)* §3,
which also flags the one open question this subtraction raises: whether it is clamped at the step
or may go negative and turn decay into growth.

`WorldComponentTick` is reached from `TickManager.DoSingleTick` → `World.WorldTick` →
`WorldComponentUtility.WorldComponentTick` [V] — inside the synced tick. `WorldComponentUpdate`
and `WorldComponentOnGUI` are the Unity frame loop and must not write simulation state.

**Every rate and threshold is a Def field.** Not a `ModSettings` field — **T-18**, and VFED is
the live worked example of getting this wrong: `WorldComponent_Deserters.WorldComponentTick`
reads `DesertersMod.VisibilityChangePerDay` — a `public static` forwarding to
`Instance.Settings.VisibilityChangePerDay`, a client-local slider — inside its tick [V].

### 5. Bands

**Pure XML, on VFED's `VisibilityLevelDef` pattern**, verified [V]:
`VFED.VisibilityLevelDef : Def` carries an `IntRange visibilityRange`, an icon, and a
polymorphic `List<VisibilityEffect> specialEffects` resolved in `PostLoad`. `ReverenceBandDef`
is the same object with a `FloatRange`, a label, a description of what the band enables and
risks, and a `List<ReverenceEffect>`. The ladder is data; only the effect workers are C#.

A band crossing announces itself with a `ChoiceLetter` subclass — VFED's
`Letter_VisibilityChange` is the shipped precedent [V], and its
`Utilities.ChangeVisibility` → `Notify_VisibilityChanged` → recompute band → send letter
sequence is the whole pipeline in one method.

### 6. Where the player sees it

**D1 — beside Goodwill: a postfix on `RimWorld.FactionUIUtility.DrawFactionRow`, and it is
tighter than it first looked.**

This is the in-game Factions tab row — icon, name, leader, info-card button, ideo icons, the
goodwill number with its relation-kind label, the natural-goodwill column, the enemy-faction
strip [V]. Full geometry is in
[`docs/engine/factions-and-worldgen.md`](../engine/factions-and-worldgen.md) § *Two faction UIs*.
Three facts govern the design, and an earlier draft of this section had two of them backwards:

- **There is no vertical slack in the goodwill columns.** The two labels are drawn into 80px
  rects at `rowY - 10` and `rowY + 10` with `TextAnchor.MiddleCenter`, so their glyphs land at
  `rowY + 30` and `rowY + 50`, and the natural-goodwill column draws a black rect at exactly
  `rowY + 30` [V]. Reverence needs **its own horizontal strip**, not a third line in an
  existing column.
- **The row is contested.** Three mods patch this method under 1.6 — VFE Classical (a prefix
  registered from a static constructor), RimPacts (prefix + finalizer, *and* a postfix
  rewriting the relation-kind label in that column), and Faction Territories (a prefix that
  shrinks `fillRect` by 80 to claim the right edge) — and Rim War and Faction Customizer fork
  the method outright [V]. **The obvious free strip is already Faction Territories'.**
- **It is `private static`** and its body uses inlined literals rather than the declared
  consts, so the postfix hardcodes layout that vanilla can move in an update, and must
  replicate the `ModsConfig.IdeologyActive && !Find.IdeoManager.classicMode` branch that zeroes
  the ideo column.

**So D1 is a real but crowded option, not the free win it was written as.** It ships Reverence
on vanilla's own surface with no new window, at the price of negotiating a strip with up to
three other patches and re-checking geometry each RimWorld update. The tooltip, built in the
same method, is uncontested and can carry the band and recent contributions cheaply.

**This strengthens rather than weakens the case for
[#61](https://github.com/cjd721/Rimworld-Archinity/issues/61).** A political tab of our own owns
its layout, has no conflict surface and no update tax. D1 is the interim display; #61's surface
is the destination, and the choice is now a real trade rather than a formality.

**The faction info card is not an option** [V]. `StatsReportUtility.StatsToDraw(Faction)` yields
exactly one description entry, and the rest comes from
`faction.def.SpecialDisplayStats(StatRequest.ForEmpty())` — **def-level, with no faction
instance in scope**. Showing per-faction Reverence there would mean patching
`DrawStatsReport(Rect, Faction)` to inject into a static cache.

**D2 — the visible gate: a postfix on `RimWorld.FactionDialogMaker.FactionDialogFor(Pawn, Faction)`.**

The requirement is *"diplomatic actions are visibly gated by Reverence so the player can see the
carrot before reaching it."* `DiaOption` carries `disabled` and `disabledReason` and
`Disable(string)` is vanilla's own idiom for it — `FactionDialogMaker` uses it for the social
skill gate [V]. The postfix appends options to `root.options` with the reason reading
*"requires N Reverence — currently M."* Establishing an institution and calling a revolt are
options on this list, gated this way.

⚠ **Where the option's `action` lives is not free, and this constrains the implementation.**
Multiplayer reconstructs each `DiaOption`'s delegate through
`DelegateSerialization.CheckMethodAllowed`, which requires the method's outermost declaring type
to derive from one of **fifteen** whitelisted types — `QuestPart`, `Command`, `Letter`,
`ThingComp`, `FactionDialogMaker` and eleven others [V]. **A closure compiled into one of our
own patch classes is refused and throws on load**, not on click. See
[`docs/engine/determinism.md`](../engine/determinism.md) § *MP serialises the comms-console
dialogue* for the list and the two failure messages.

**The disabled half is safe regardless** — `disabled` and `disabledReason` are scribed as plain
values with no delegate — so *showing* the gate costs nothing. It is the **enabled** action
behind it that must be hosted on a whitelisted type. That is a naming constraint on where we put
one method, not a redesign, but it is invisible until a save is reloaded and is therefore worth
building against from the start.

**D3 — the Global Reverence view.** The number is derived (above) and the band letter (§5) is
the change announcement. The *view* — one political tab or several surfaces, and where it hangs
— is [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61)'s to decide; it is a live
ticket with this exact question in its body. The donor for a global meter reached from the comms
console is VFED's `WorldComponent_Deserters`, which implements `ICommunicable` and pairs with a
`Dialog_NodeTreeWithFactionInfoAndVisibility` [V].

### Cost

| Piece | Cost |
|---|---|
| Store, decay, band lookup, query API | **New C#** — one `WorldComponent`, ~120 lines |
| Band ladder, per-event amounts, decay rate | **XML** — two new Def types |
| Apostle hook | **Patch** — 1 Harmony postfix, ~25 lines |
| Quest / deed route | **New C#** — `QuestPart` + `QuestNode` (+ `Reward`), ~70 lines |
| Reverence beside Goodwill | **Patch** — 1 Harmony postfix, ~50 lines, and a contested row (D1) |
| Visible diplomatic gate | **Patch** — 1 Harmony postfix, ~40 lines |
| Band-change letter | **New C#** — one `ChoiceLetter` subclass, ~20 lines |
| Global Reverence view | **#61** — the surface, not the number |
| Storyteller attention weight | **#60** — one `StorytellerComp` subclass per behaviour |

**Aggregate: two new Def types, three Harmony postfixes, one `WorldComponent`, one
`QuestPart`/`QuestNode` pair, ~300–350 lines of C# in the existing `ArchinityAltar.dll`.** No
new assembly — `Archinity.Altar` already ships a Harmony instance and references
`Assembly-CSharp` and `0Harmony` ([`POLITICS.md`](POLITICS.md)).

**The storyteller half remains the expensive one and is not in that total.** VFED's five
`…_ByVisibility` comps are each a bespoke `StorytellerComp` subclass reading the raw scalar and
applying its own hardcoded lerp, with every endpoint constant compiled in [V]. There is no
generic "Def field = weight curve keyed on a custom stat" mechanism to borrow. Budget one
subclass per storyteller behaviour Reverence is meant to move; that is
[#60](https://github.com/cjd721/Rimworld-Archinity/issues/60)'s to price.

## The build — Exaltation: the Empire becomes the Church in place

**Transform Royalty's `Empire` in place. Keep every identifier it has; change only what the player
reads, what the faction believes, and how it feels about the founders.** The Church keeps defName
`Empire`, `categoryTag Empire` and `royalTitleTags EmpireTitle`, and every `RoyalTitleDef`,
`RoyalTitlePermitDef`, `PawnKindDef` and `TraderKindDef` keeps its defName. What changes is labels,
names, doctrine and appearance, plus one ~30-line `GoodwillSituationWorker` that makes the Church's
temper a function of Global Reverence.

**Cost: XML, ~30 lines of C#, zero Harmony patches, no new saved state, no new Def type**
([#53](https://github.com/cjd721/Rimworld-Archinity/issues/53), reopened and re-resolved
2026-09-15). The earlier build instanced a second Church faction beside an untouched Empire. The
campaign has withdrawn it (§ *Authority correction*), and its §-numbered pieces are gone from this
document. The two patches it needed, the permits-card seed and the bestowing-quest suppressor, are
**deleted**, not ported (§4, §7).

### 1. Why every identifier stays — the transformation is a presentation layer

Everything that makes the Empire *work* finds it by an identifier. Nothing finds it by its label
[V]:

| Key | Resolved by | If renamed or dropped |
|---|---|---|
| defName `Empire` | `FactionManager.RecacheFactions` sets `empire = FirstFactionOfDef(FactionDefOf.Empire)`, which backs `Faction.OfEmpire` [V]. Vanilla reads that singleton in **22 files**, among them the bestowing ceremony, tribute collector, shuttle-crash rescue, mission roots, throne-room and landing-pad settlement gen, `RewardsGenerator` and the **T-35** permits seed [V]. VFE Empire reads it at **138 sites in 58 of 227** decompiled files (counting `OfEmpire` + `FactionDefOf.Empire`; #53's 136/57 counted `OfEmpire` alone — same data, different basis), and VFE Deserters at **49 in 24 of 168** [V]. **12 more mods** carry `OfEmpire` in their metadata [I]. **Fifteen mods** patch `FactionDef[defName="Empire"]` in their 1.6 folders [V]; WTL's override names it [V]; Royalty's own XML carries 25 `<faction>Empire</faction>` refs, and VFE Empire adds 29 more [V] | `OfEmpire` is null or points at nothing, everywhere at once. Most consumers null-check and stand down, silently |
| `categoryTag Empire` | `TechprintUtility.GetResearchProjectsNeedingTechprintsNow`, the single techprint chokepoint [V]. Five assemblies hold the exact `#US` literal `"Empire"` — RimPacts, Better Traders Guild, Sensible Factions, Worksites Expanded (`MiningOutpost.dll`), Lemmy Progression [I] | 14 Empire-only techprint projects lose trader and quest-reward supply (§ *Verification*) |
| `royalTitleTags EmpireTitle` | `FactionDef.RoyalTitlesAwardableInSeniorityOrderForReading` [V]; `TraderKindDef.TitleRequiredToTrade` [V]; VFE Empire's `WorldComponent_Hierarchy` static constructor [V] | **T-36** ladder freeze; the title-gated trade check silently opens (§5); the NPC hierarchy empties |
| title / permit / pawn-kind defNames | `PawnKindDefOf.Empire_Royal_Bestower` / `Empire_Fighter_Janissary` in `QuestNode_Root_BestowingCeremony`; `PawnKindDefOf.Empire_*` in `QuestNode_Root_ShuttleCrash_Rescue` and `QuestNode_Root_Mission_BanditCamp` [V]; VFE Empire's `RoyalTitleDefExtension.kindForHierarchy` [V] | loud where a `DefOf` binds, silent where a string or an XML cross-reference does (**T-04**) |

**So "rename nothing" is the rule, and it is the whole reason the build is cheap.** Every
Empire-bound route — techprints, titles, permits, quests, VFE Empire's hierarchy and ceremonies,
VFE Deserters' pursuit, WTL's roster exemption, RimPacts' guards, the Permits tab — resolves to the
Church **unchanged**, because the Church *is* the faction they already look for. The content
inventory in § *Outstanding decisions* 18 is therefore a list of **fiction** choices, not of
breakage.

### 2. What changes — the faction def, in XML

`PatchOperation`s on `FactionDef[defName="Empire"]`:

- **Presentation — `PatchOperationReplace`.** `label`, `description`, `pawnSingular`, `pawnsPlural`,
  `leaderTitle`, **`royalFavorLabel` → "exaltation"**, `royalFavorIconPath`, `factionIconPath`,
  `colorSpectrum`, `allowedCultures`, `backstoryFilters`, and `factionNameMaker` /
  `settlementNameMaker`, which point at two new `RulePackDef`s. The current values are the Sophian
  "shattered empire" set [V].
- **Doctrine — the Church's Roman-Catholic-like creed.** `requiredMemes`, `allowedMemes`,
  `disallowedPrecepts` and `structureMemeWeights` are replaced; `fixedIdeo` / `ideoName` /
  `deityPresets` are added if the creed is to be authored rather than generated. These are NPC-only
  fields funnelled through `FactionGenerator.CreateFactionAndAddToManager` (§ *Superseded build —
  replacing the player faith* §1 [V]). ⚠ Vanilla Ideology Expanded — Memes and Structures
  **appends** to `allowedMemes` and `structureMemeWeights` [V]. A Replace discards those additions,
  which is intended here, but only if our patch runs after theirs (**T-02**, **T-05**). The other
  non-list patchers: Vanilla Psycasts Expanded **replaces `pawnGroupMakers`** to add `Empire_Caster_*`
  kinds, Vehicle Framework adds `Vehicles.VehicleRaiderDefModExtension`, Vanilla Base Generation
  Expanded edits the def, and VRE Android adds a xenotype chance [V]. Any `pawnGroupMakers` rewrite of
  ours must be ordered against VPE's.
- ⚠ **Keep the backstory *category names*; rewrite backstory *text* in place.** VFE Deserters'
  `VFED.HarmonyPatches.MiscPatches.CheckBiosecurity` (postfix on `WorkGiver_Open.HasJobOnThing`) and
  its `FloatMenuOptionProvider_OpenThing.GetSingleOptionFor` postfix refuse to open a
  `Building_CrateBiosecured` unless the pawn has a backstory whose `spawnCategories` contains the
  literal `"ImperialRoyal"` [V] — a category Royalty's royal pawn kinds use (`PawnKinds_Empire.xml`
  [V]). Renaming `ImperialRoyal` / `ImperialCommon` / `ImperialFighter`, or swapping
  `backstoryFilters` to new categories, silently locks those crates. Change the backstories' `title`
  and `description`, not their categories.
- ⚠ **`permanentEnemyToEveryoneExcept` — `PatchOperationAdd` only, never Replace.** **Eleven** mods
  append their factions to it (1.6): TechBlock, VFE Settlers, VFE Classical, VRE Android, VFE Tribals,
  Medieval Overhaul, Better Traders Guild, VFE Empire (`VFEE_NewFamily`), VFE Insectoids 2
  (`VFEI2_PlayerOutpost`), VFE Medieval 2 (`VFEM2_MerchantGuild`, `_KingdomCivil`, `_CivilClan`,
  `_PlayerKingdom`) and VQE Ancients (`VQE_NewVaultPlayerFaction`) [V]. A Replace silently
  makes the Church a permanent enemy of every one of them, and `Faction.CanChangeGoodwillFor` then
  refuses goodwill writes in both directions, forever [V]. Which factions the Church *should* be
  allowed to befriend is § *Outstanding decisions* 19.
- **`techLevel` stays `Ultra` until someone decides otherwise.** Lowering it does **not** cost
  techprints — `GetResearchProjectsNeedingTechprintsNow` has no tech-level test [V]. What it moves
  is roster filtering (§3), the contact band, and
  `FactionManager.TryGetRandomNonColonyHumanlikeFaction`'s tech filters [V]. It is an open
  parameter, § *Outstanding decisions* 17.
- **Appearance** is pawn-kind apparel and weapon tags on the `Empire_*` kinds. That is authoring,
  not mechanism.

**The text surface, sized** [V counts]: `RoyalTitles_Empire.xml` holds **7 awardable titles**
(`favorCost` 1–20, Freeholder → Count) and **4 non-awardable** (Duke, Consul, Stellarch, Emperor).
16 vanilla `RoyalTitlePermitDef`s in `RoyalPermits_Empire.xml`, plus VFE Empire's 29 `VFEI_` permits if it ships. `PawnKinds_Empire.xml` has
20 text hits, and Royalty's `Imperial*` backstory files have 87. Six Royalty `Keyed` strings
hardcode the word **"honor"** instead of reading `royalFavorLabel` — `CommandCallRoyalAidDesc`,
`CommandCallRoyalAidNotEnoughFavor`, `LetterRewardsForNewTitle`, `LetterPartBestowingExtraHonor`,
`LetterPartNoExtraHonor` and `CooldownUseFavorCost` [V]. VFE Empire and VFE Deserters add 27 and
29 English lines naming empire, imperial or honor [V count]. Keyed text is overridden by shipping the same
keys under our `Languages/English/Keyed` [I — STUB-check, § *Verification*].

### 3. What must be added so the Church exists at all

- **The WTL roster exemption — unconditional.** WTL's own `TechLevelConfigDef` exempts `Empire` only
  under `<ifModPresent>oskarpotocki.vfe.empire</ifModPresent>` [V]. Without VFE Empire, an Ultra
  Church on a Neolithic world is **stripped from the generated roster** (**T-54**), and every row of
  §1's table goes dark at once. **T-07** makes that permanent. The fix is ~8 lines: one
  `TechLevelConfigDef` entry, `Empire → Undefined`, with no mod guard. It can share the def
  [`ORBIT.md`](ORBIT.md) already plans for the orbital factions.
- **Roster protection.** `requiredCountAtGameStart` is dead (**T-09**). Royalty only *warns* at world
  creation when the Empire is removed (`WorldFactionsUIUtility`), and `BackCompatibility` re-adds it
  only to legacy saves that have no `world.info.factions` [V]. VFE Empire ships the real guard —
  `VEF.Factions.FactionDefExtension.forcedFactionData`, with `preventRemovalAtWorldGeneration` and
  `forcePlayerToAddFactionIfMissing` [V as XML; VEF's enforcement [I]]. Without VFE Empire, the
  guard is the world-creation checklist at the freeze
  ([#18](https://github.com/cjd721/Rimworld-Archinity/issues/18)).

### 4. Exaltation, and the rite — vanilla, unchanged, and no longer a hazard

**The scale.** `Pawn_RoyaltyTracker.favor[Faction.OfEmpire]` is the Exaltation number: per pawn,
scribed, faction-keyed [V]. Church quests offer it automatically through `Reward_RoyalFavor` →
`QuestPart_GiveRoyalFavor` whenever `giverFaction.allowRoyalFavorRewards && def.HasRoyalTitles`
[V]. `RewardsGenerator`'s `flag5` — `giverFaction == Faction.OfEmpire` — now applies to the Church
and suppresses its items-only reward stacks [V]. Authored awards use `QuestNode_GiveRoyalFavor`, and
gates use `QuestNode_RequireRoyalFavorFromFaction` / `QuestNode_HasRoyalTitleInCurrentFaction`
[V]. The *Exaltation or Reverence* fork is two `Reward`s on one quest, vanilla's
`Reward_RoyalFavor` and *The build — Reverence* §3B's `Reward_Reverence`.

**The rite is vanilla's bestowing ceremony.** When favour crosses a rung,
`Pawn_RoyaltyTracker.OnFavorChanged` calls `RoyalTitleUtility.GenerateBestowingCeremonyQuest`
directly, and the 37,500-tick scan re-arms it [V]. `QuestNode_Root_BestowingCeremony` generates:

- a shuttle for the bestowing faction;
- one `Empire_Royal_Bestower` and six `Empire_Fighter_Janissary`;
- `AddShipJob_Arrive(…, Faction.OfEmpire)`;
- a throne-room acceptance requirement when the title carries `throneRoomRequirements` [V].

`QuestPart_BestowingCeremony` runs `LordJob_BestowingCeremony`, which is a **`LordJob_Ritual`**.
Its `RitualOutcomeEffectWorker_Bestowing.Apply` calls `TryUpdateTitle` and adds `honorFromQuality`
favour for spectators [V].

Under the second-faction build this was imperial content firing on a Church ladder, and it needed a
suppressor. **Under this build it is literally the requirement** — *"at Exaltation thresholds, the
founders perform a rite and receive the next sacred title"* — with a Church bestower and a Church
honour guard. **Zero code.**

⚠ **But the same `Apply` grants psylinks, and the requirement forbids it.** It loops
`target.ChangePsylinkLevel(1)` from the current level up to `GetMaxPsylinkLevelByTitle()` [V].
`maxPsylinkLevel` is 1–6 on Yeoman → Count, and 6 on the abstract `BaseEmpireTitleNPC`, which the
four non-awardable titles inherit [V]. `docs/requirements/ALTAR.md`
says the psychic ladder is measured *"independently of Church titles"*, and RELIGION's requirement
says titles are *"institutional standing, not psychic power"*. **Set `maxPsylinkLevel` to 0 on every
Church title** — seven XML replaces: six concrete titles and the NPC base. Left alone, the ceremony silently hands out psylinks as title
perks. The same field makes `PawnGenerator` give NPC title-holders psylinks [V], so zeroing it also
makes generated Church nobles non-casters; see § *Outstanding decisions* 20. Vanilla Psycasts
Expanded transpiles `RitualOutcomeEffectWorker_Bestowing.Apply` to call its own
`ApplyTitlePsylink`, which also reads `newTitle.maxPsylinkLevel` [V] — so zeroing the field covers the
VPE path too; only its `pawn.Psycasts() == null` branch still grants one base level via
`ChangePsylinkLevel(pawn, 1)` before adding `max − old` (0) [V], which the STUB below must check.

**The alternative, if the fiction rejects an arriving bestower.** The founders run their own rite:
a `RitualOutcomeEffectWorker` calling `TryUpdateTitle` (~20 lines), plus a prefix on
`RoyalTitleUtility.GenerateBestowingCeremonyQuest` that refuses (~15 lines — the one chokepoint both
callers reach [V]). What separates the two is fiction alone: a Medieval-presented Church arriving
by shuttle, and vanilla's throne-room demands. **Recommended: the vanilla ceremony**, reskinned. It
is free, it is already a ritual, and it is already Multiplayer-shaped (§ *Persistence and
multiplayer*).

### 5. Privileges — native now, and trade is already one of them

- **Permits.** Every delivery worker takes the faction as a parameter [V], so vanilla's permits
  become Church privileges by relabelling. New privileges are `RoyalTitlePermitDef`s with
  `<faction>Empire</faction>` and a `minTitle` in the existing ladder — a native fit, where the old
  build needed a copy. **VFE Empire's 29 `VFEI_` permits are usable as-is** if VFE Empire ships.
  The earlier draft said they could only be imitated, which was true of a second faction only.
  `RoyalAid` carries pawn, item, targeting, explosion and temperature fields and nothing else; that
  claim is inherited [I].
- **Title-gated trade already exists, and an earlier draft called it inert.** All three Empire trader
  kinds carry `permitRequiredForTrading` — `Base_Empire_Standard → TradeSettlement`,
  `Empire_Caravan_TraderGeneral → TradeCaravan`, `Orbital_Empire → TradeOrbital` [V].
  `TraderKindDef.TitleRequiredToTrade` resolves that to the lowest title granting the permit —
  **Knight** for `TradeSettlement` / `TradeCaravan`, **Baron** for `TradeOrbital` in vanilla's ladder
  (`RoyalTitles_Empire.xml` [V]). Refusals [V]: `IncidentWorker_TraderCaravanArrival` commonality 0
  without a permitted colonist; `CaravanVisitUtility` and `IncidentWorker_CaravanMeeting` disable the
  trade command; `FactionDialogMaker` denies caravan and orbital requests; `FactionUtility.CanTradeWith`
  refuses the call-with-ship and gates `IncidentWorker_OrbitalTraderArrival.CanSpawn`. `Settlement`
  only *shows* the requirement (inspect string, tutor dialog). **`FactionUtility.CanTradeWith` also
  rejects any faction `HostileTo` the pawn's** [V]. **So Church trade — including the trader half of
  every Empire techprint route — is title-gated for free, and closed outright when the Church is
  hostile.** That is the
  requirement's *"titles unlock acquisition routes"*. The earlier claim that those three permits are
  inert (no `<faction>`, no worker) was true only of a Church *copy*.
- **Safe passage and political privileges** still have no vanilla worker and no `RoyalAid` field
  (inherited [I]). They remain unpriced; see § *Outstanding decisions* 10.

### 6. Suspicion and hostility — derived from Global Reverence, never stored

**Mechanism.** One `GoodwillSituationDef` in XML, whose `workerClass` is a new
`GoodwillSituationWorker_ChurchSuspicion : GoodwillSituationWorker`. It overrides
`GetMaxGoodwill(Faction other)` and `GetNaturalGoodwillOffset(Faction other)` [V — both `virtual`,
defaults 100 and 0], and returns non-defaults only when `other == Faction.OfEmpire`. Both values
come from **derived** Global Reverence (*The build — Reverence* §1) through two `SimpleCurve`s on
the def's mod extension (**T-18**: never a setting).

**Why that produces hostility** [V]:

- `GoodwillSituationManager.GoodwillManagerTick` runs `RecalculateAll` every 1,000 ticks.
- Each recalculation calls `Faction.OfPlayer.Notify_GoodwillSituationsChanged(other, canSendHostilityLetter: true)`,
  which runs `FactionRelation.CheckKindThresholds`.
- `Faction.GoodwillWith` returns `Mathf.Min(baseGoodwill, GetMaxGoodwill(…))` for the player pair.
- So a cap at or below −75 **makes the Church hostile** (`CheckKindThresholds`: `goodwill <= -75`), with vanilla's hostility letter. It returns to neutral only when effective goodwill reaches **≥ 0** [V].
- `NaturalGoodwill` meanwhile moves the ±50 drift band `CheckReachNaturalGoodwill` pulls toward.

Broad penetration therefore makes the Church progressively colder, then hostile — the requirement's
*"progressively more hostile until betrayal or open attack"*. Betrayal and open attack as *authored
scenes* are plot content, not this build.

**State: none.** `GoodwillSituationManager.cachedData` is an unscribed cache [V], and Global
Reverence is derived.

⚠ **Every Reverence write must call `Find.GoodwillSituationManager.RecalculateAll(canSendHostilityChangedLetter: true)`.**
The cache is refreshed by `RecalculateAll` only from the 1,000-tick `GoodwillManagerTick`,
`GravshipUtility` and `SettlementUtility` [V]; otherwise `GetSituations` fills a missing entry lazily —
including from `FactionUIUtility`'s draw — and then runs `CheckHostilityChanged` [V]. So the host's
cached cap can lag live Reverence by up to 1,000 ticks, while a client that joins inside that window
builds its cache from live Reverence and computes a different `GoodwillWith` (mechanism [V]; desync
[I]). Recalculating on write keeps the cache a pure function of synced state. ~2 lines in the
Reverence component's setter; still no saved state. **Display: free.** `FactionUIUtility` lists every situation from `GetSituations`
in the faction row [V], and overriding `GetPostProcessedLabel` names the reason.

⚠ **Do not use `GoodwillSituationDef.baseMaxGoodwill`** — nothing reads it (**T-83**). The worker
override is the only route.

⚠ **The cap is not memory.** `baseGoodwill` keeps accumulating under the clamp [V]. If Global
Reverence falls, the cap lifts and the Church is instantly as warm as its base allows. Whether
suspicion ratchets is a requirement, and a ratchet needs one stored high-water mark;
§ *Outstanding decisions* 11.

### 7. Cost

| Piece | Cost |
|---|---|
| Church presentation and doctrine on `FactionDef[defName="Empire"]` | **XML** — ~15 field operations + 2 `RulePackDef`s |
| `permanentEnemyToEveryoneExcept` | **XML** — `PatchOperationAdd` only; entries are a fiction call (decision 19) |
| Title, permit and pawn-kind relabels | **XML** — 11 titles, 16 vanilla permits (+29 `VFEI_` if shipped), the `Empire_*` kinds |
| Keyed strings hardcoding "honor" | **XML** — 6 keys; backstories optional |
| `maxPsylinkLevel` → 0 on Church titles | **XML** — 7 replaces (§4) |
| WTL roster exemption | **XML** — ~8 lines, unconditional (§3) |
| Exaltation, quest rewards, the rite, gizmo, character card | **Nothing** — vanilla |
| Title-gated trade | **Nothing** — vanilla (§5) |
| Church suspicion and hostility | **New C#** — one `GoodwillSituationWorker`, ~30 lines, + 1 `GoodwillSituationDef`, + a `RecalculateAll` call on every Reverence write (~2 lines) |
| Permits-card seed (**T-35**) | **Deleted** — `Faction.OfEmpire` always exists |
| Bestowing-quest suppressor | **Deleted** — the ceremony is the Church's rite (alternative in §4: ~35 lines) |
| Royal Ascent ending | **XML** — keep or strip the storyteller comp (decision 18) |
| Safe passage, political privileges | **Unpriced** — no carrier (decision 10) |

**Aggregate: zero Harmony patches, ~30 lines of C# in the existing assembly, no new saved state, no
new Def type.** The XML is mostly *authoring* — names, creed, catalogue — and none of it waits on
mechanism.

## Superseded build — replacing the player faith with Church doctrine

**Mid-game ideology conversion of the player faction is not merely possible — it is what
vanilla does on its own.** `RimWorld.FactionIdeosTracker.RecalculateIdeosBasedOnPlayerPawns`
recomputes the player faction's `primaryIdeo` from live free-colonist ideo counts, on every
member gain or loss and on every colonist ideo change [V]. So the campaign does not need a
mechanism that *moves* the ideology. It needs a rite that moves it **deliberately**, and a
record saying it did.

The build is one ritual outcome worker, one `RoleRequirement` subclass, two `PreceptDef`s
and three scribed fields. No Harmony patch, no new Def type, no new saved collection.

### 1. The rite — one `RitualOutcomeEffectWorker` subclass

On a good outcome the worker does three things, in order:

1. `pawn.ideo.SetIdeo(churchFaction.ideos.PrimaryIdeo)` for each founder in the rite's roles.
   `RimWorld.Pawn_IdeoTracker.SetIdeo(Ideo)` is public and accepts **any** `Ideo` — it performs
   no `IdeoManager` membership check of its own, so passing an unregistered `Ideo` is our
   responsibility, not the engine's. Its one refusal is a **baby early-return** [V], which is
   irrelevant to a founder but would matter if the rite were ever opened to the colony at large.
2. Writes the commitment record (§2).
3. `Precept_Role.Assign(founder, addThoughts: true)` for the leader and preacher rungs.
   `RimWorld.Precept_Role.Assign(Pawn, bool)` is public abstract, concrete on
   `Precept_RoleSingle` [V].

**Everything downstream of step 1 is vanilla's, unpatched** [V]:

- `SetIdeo` calls `pawn.Faction.ideos.Notify_ColonistChangedIdeo()` for a player-faction
  member, which calls `RecalculateIdeosBasedOnPlayerPawns()`.
- That method promotes the new plurality, sends `LetterLabelNewPrimaryIdeo` /
  `LetterNewPrimaryIdeo`, calls `Ideo.Notify_NotPrimaryAnymore` on the old primary, and
  rebuilds `ideosMinor` from scratch.
- `SetIdeo` itself already unclaims an ideologically forbidden bed, strips forbidden
  bonds with a letter, dirties situational thoughts, re-evaluates needs, apparel and
  temporary abilities, and files a `HistoryEventDefOf.ChangedIdeo` event.

**A colonist holding an NPC faction's `Ideo` is an ordinary state, not an exotic one.**
`RimWorld.InteractionWorker_ConvertIdeoAttempt.ConversionSelectionFactor` weights an
`NPC_Free → Colonist` conversion at 0.5 [V] — vanilla preachers do this to colonies every
playthrough.

**The nearest shipped donor performs this exact sequence mid-game, inside a synced command.**
`Multiplayer.Client.Factions.FactionCreator.CreateFaction` is a `[SyncMethod]` that runs
while a game is in progress and calls `IdeoGenerator.GenerateIdeo(…)`,
`Find.IdeoManager.Add(ideo)`, `faction.ideos.SetPrimary(ideo)` and then
`startingPawn.ideo.SetIdeo(faction.ideos.PrimaryIdeo)` for every pawn [V]. The mechanism is
not theoretical; a mod we already ship drives it.

⚠ **State the precedent's limit with it.** `CreateFaction` runs that sequence on a **brand-new
faction with freshly generated pawns**, not on an established colony changing its mind [V]. What
it proves is that the four calls compose and survive `[SyncMethod]` serialisation mid-game. What
it does not prove is the part our rite actually does: `SetIdeo` onto founders who already hold an
ideology, already have beds, bonds, apparel and thoughts bound to it, inside a colony whose
believer counts then drive `RecalculateIdeosBasedOnPlayerPawns`. That composition is the [I] this
capability carries, and § *Verification* names the observation that closes it.

**The Church's doctrine is authored in XML and costs nothing.** `FactionDef` carries
`fixedIdeo`, `ideoName`, `ideoDescription`, `forcedMemes`, `requiredMemes`,
`disallowedMemes`, `deityPresets`, `styles`, `hiddenIdeo` and `requiredPreceptsOnly`, and
`RimWorld.FactionGenerator.CreateFactionAndAddToManager` funnels all of them into
`IdeoGenerationParms(fixedIdeo: true)` → `FactionIdeosTracker.ChooseOrGenerateIdeo` →
`IdeoGenerator.MakeFixedIdeo` [V]. Those fields are **NPC-only** — `Page_ChooseIdeoPreset.PostOpen`
applies them inside `if (allFaction != Faction.OfPlayer && …)` [V] — which is exactly why the
*player's* starting ideology needs the `.rid` route and the Church's does not.

### 2. State and persistence — three fields, and why none of it is derivable

⚠ **`founder.Ideo == churchFaction.ideos.PrimaryIdeo` is not proof of a commitment.**
`InteractionWorker_ConvertIdeoAttempt.Interacted` → `Pawn_IdeoTracker.IdeoConversionAttempt`
converts any colonist whose `Certainty` reaches zero, and certainty decays on
`ConversionTuning.CertaintyPerDayByMoodCurve` [V]. A visiting Church preacher can walk a
founder through the one-way door by accident. Vanilla *does* announce it —
`LetterLabelConvertIdeoAttempt_Success` [V] — so it is loud, but the **resulting state is
identical to the deliberate act**, and no campaign gate may read it as consent.

Three fields on the religion `WorldComponent` (§ *The build — Reverence* §1's component;
if that component is ever split, these follow religion state):

| Field | Purpose |
|---|---|
| `Ideo committedIdeo` | `Scribe_References.Look` — `Ideo` is `ILoadReferenceable`, `GetUniqueLoadID() => "Ideo_" + id` [V] |
| `int commitmentTick` | when the rite completed; `-1` means never |
| `List<Pawn> committedFounders` | `Scribe_References.Look`, `LookMode.Reference` |

**The ideology itself needs no new persistence at all.** `Pawn_IdeoTracker.ideo` and
`FactionIdeosTracker.primaryIdeo` are both already `Scribe_References.Look` [V]. Adding the
three fields to a save that predates them is a no-op: they read as null, `-1` and empty,
which is the correct "not committed" state, on the backfill path already verified in
§ *The build — Reverence* §2.

### 3. What changes it — the rite, and one thing vanilla will undo behind you

The rite is the only writer.

⚠ **Do not also call `FactionIdeosTracker.SetPrimary` to force the promotion.** It is a bare
field write with no guard [V], and on the *player* faction the value is recomputed by
`RecalculateIdeosBasedOnPlayerPawns` on the next colonist gain, loss, death or conversion —
so a forced primary with fewer believers than the standing plurality is silently overwritten.
On **NPC** factions the same call is durable, because `Notify_MemberGainedOrLost` early-returns
unless `faction.IsPlayer` [V]. Vanilla's own use in `Page_ChooseIdeoPreset.AssignIdeoToPlayer`
is safe only because it runs at worldgen, where the recalculation early-returns on
`Current.ProgramState != ProgramState.Playing` [V].

**This is a design constraint, not a trap, and the distinction was audited.** An earlier draft
proposed it for `docs/TRAPS.md`. It does not qualify: the revert is **not silent**.
`RecalculateIdeosBasedOnPlayerPawns` sends `LetterLabelNewPrimaryIdeo` /
`LetterNewPrimaryIdeo` whenever it promotes an ideo that differs from the standing
`primaryIdeo` [V] — and a forced primary being overwritten by the standing plurality is exactly
that case, so the overwrite announces itself in a letter. It fails the register's silent-failure
bar and no ID is allocated. The behaviour stays documented **here**, because it still forbids a
call the build would otherwise be tempted to make.

⚠ **The plurality gate is real, and it is the design's price rather than a defect.**
The promotion test is `num > tmpPlayerIdeos.TryGetValue(primaryIdeo, 0)` — **strictly
greater** free-colonist believer count [V]. Two founders in a two-pawn colony flip the
primary; two founders in a ten-colonist colony do not.
[`ENDING.md`](../plot/ENDING.md) § *The Alignment Rule* already states that the Church route
costs the player their own religion, and the plurality gate is that sentence expressed as
arithmetic. **Do not engineer around it.**

### 4. The roles — and the requirement is wrong twice

> **Superseded selection.** These roles belong to the **player faith**, not the Church.
> The required shape is one or two founder-specific seats, several multi-holder
> preacher/converter seats for core disciples, at least one production specialist, and
> campaign-time role unlocks. The role mechanics collected below are inputs to the new
> capability ticket [#114](https://github.com/cjd721/Rimworld-Archinity/issues/114); the
> single-leader/single-preacher build is not selected.

[`docs/requirements/RELIGION.md`](../requirements/RELIGION.md) asserts *"the two founding
pawns are mechanically forced into the ideology's defining leader/preacher roles."*
Neither half holds as written.

**A. The preacher role cannot activate in a two-founder colony.** Vanilla's moral guide,
`IdeoRole_Moralist`, inherits `activationBelieverCount: 3` / `deactivationBelieverCount: 1`
from the abstract `PreceptRoleSingleBase` in
`common/RimWorld/Data/Ideology/Defs/PreceptDefs/Precepts_Role.xml` [V].
`Precept_RoleSingle.RecacheActivity` gates on
`colonistBelieverCountCached >= def.activationBelieverCount || def.leaderRole`, and
`Ideo.RecacheColonistBelieverCount` counts **free colonists only**, excluding slaves, quest
lodgers **and pawns in cryptosleep** [V] — the last of which matters for a campaign that will
put founders under for a transit. There is **no primary-ideo escape hatch**: three lines away in the same
class, `Ideo.ObligationsActive` *does* have one (`return Faction.OfPlayer.ideos.IsPrimary(this);`)
[V], and the role path deliberately does not. With two believers the preacher role is
inactive, and if assigned it is unassigned on the next recache.

The leader role is fine. `IdeoRole_Leader` carries `leaderRole: true`, which short-circuits
the count on **both** the activation and the deactivation branch [V]. `Precept_RoleSingle.Assign`
additionally sets `Faction.OfPlayer.leader = p` and unassigns every other leader role across
`Faction.OfPlayer.ideos.AllIdeos` [V] — so seating a founder as the Church ideology's leader
also makes them the colony's diplomatic face, for free.

**Fix: ship our own two `PreceptDef`s** with `activationBelieverCount: 1`. **Do not
`PatchOperation` vanilla's `IdeoRole_Moralist`** — it is the moral guide for every ideology in
the game, NPC ones included.

⚠ **And the two roles do not take the same class.** The leader precept is
`ParentName="PreceptRoleSingleBase"`: one shared player faction has exactly one
`Faction.OfPlayer.leader`, `leaderRole: true` is what sets it, and one holder is the right
answer. **The preacher precept is `Precept_RoleMulti`**, and this reverses an earlier draft.
Under **T-21** there is one player faction and two colonies; a `Precept_RoleSingle` preacher
seats exactly one founder and leaves the other colony without one, permanently.
`Precept_RoleMulti.Assign` is uncapped [V], which is the whole reason closed #10 recommended
authoring our own role precepts as `RoleMulti` in the first place — a recommendation this
document previously recorded as *falsified*, and then built against its opposite.

**What a `RoleMulti` preacher owes a read: its activation fields.** §4A's
`activationBelieverCount` / `deactivationBelieverCount` finding is verified on
`PreceptRoleSingleBase` and `Precept_RoleSingle.RecacheActivity` [V]. Whether
`Precept_RoleMulti` gates the same way, on the same field names, has **not** been read —
**[I]**, and the one piece of §4 that still owes one. It does not change the class choice; it
changes which XML fields the def has to set, and the STUB check in § *Verification* covers it.

**B. "Forced" has no vanilla mechanism, but it has a cheap XML-shaped one.**
`Precept_Role.Assign` is a free player action from the ideo UI and nothing pins a pawn.
`RimWorld.RoleRequirement` is a **four**-member abstract — an earlier draft said three — whose
only override is `bool Met(Pawn p, Precept_Role role)`, selected per role in XML as
`<li Class="…">` [V].
`VanillaMemesExpanded` ships five subclasses of it in its 1.6 assembly —
`RoleRequirement_BestCrafter`, `_BestPsycaster`, `_HighestTitle`, `_NoTitles`,
`_BestFighter` [V] — so it is a live 1.6 extension point; `RoleRequirement_BestCrafter.Met`
is eight lines.

One `RoleRequirement_Founder` makes the founders the **only eligible pawns**, and the rite
seats them. That is the honest reading of "forced": the player may leave the seat empty but
cannot give it to anyone else.

> **Rejected: a Harmony prefix on `Precept_RoleSingle.Assign` refusing `null`.** It makes a
> visible UI button silently do nothing, which is precisely what `CODING_STANDARDS.md`
> § *Silent failures* exists to prevent.

**Founder identity is an open parameter, not a blank — and it now has a carrier.**
[`TRANSCENDENCE.md`](TRANSCENDENCE.md) § *The store* rule 1 makes `CompFounderRecord`, on the
`Archinity_FounderRecord` hediff, **the** store for founder state, and forbids a second one;
[`ALTAR.md`](ALTAR.md) already extends that comp with a field of its own. So
`RoleRequirement_Founder.Met` should read `CompFounderRecord` — one `TryGetComp` on a comp that
already travels with the pawn, is already scribed and is already MP-serialisable — rather than
introducing a private `GeneDef` / `XenotypeDef` predicate here. **This document does not edit
either of those specs and claims nothing in them**; it states where the answer lives.

Archinity expresses founder-ness genetically today —
`Archinity.Altar/Defs/GenePoolDefs/GenePool_Archite.xml`'s `<founderOnlyGenes>` is `Deathless`
and `Ageless`, and the founders are the `Archinity_ArchonianSanguophage` xenotype in
`Archinity.Origins/Defs/XenotypeDefs/Xenotypes_Archinity.xml`. That is an implementation
accident standing in for a requirement. **Which predicate defines a founder is still a
requirement and no open ticket owns it** — *Outstanding decisions* 13; what has changed is that
the mechanism no longer has to wait on it, because the comp is the carrier whatever the
predicate turns out to be.

⚠ **A ritual role may gate on any `PreceptDef`, and an earlier draft of this section turned
vanilla's habit into an engine constraint.**

What vanilla *does* is narrow, and that part holds: the only role precepts any shipped ritual
behaviour references are `IdeoRole_Moralist` and `IdeoRole_Leader`, and both derive from
`PreceptRoleSingleBase` [V]. The count was wrong — **`<precept>` appears 11 times** in
`Ideology/Defs/Rituals/Ritual_Behaviors.xml`, five naming `IdeoRole_Moralist` and six naming
`IdeoRole_Leader` [V], not the "exactly twice" an earlier draft asserted and marked [V]. The
roster of two is right; the count of two was a miscount.

**What vanilla does is not what the engine allows.** `RitualRole.precept` is a bare
`PreceptDef` field, and `AppliesToRole` tests `p.Ideo.GetRole(p).def == precept` [V]. Nothing
on that path restricts the precept to `Precept_RoleSingle`, so a ritual role gating on a
`Precept_RoleMulti` we author is ordinary, not exotic. Vanilla's choice of two single-holder
roles is content, not a rule we inherit.

**So the final altar rite inherits neither the single-holder constraint nor §4A's three-believer
threshold.** (The Exaltation rite is now vanilla's bestowing ceremony — § *The build — Exaltation*
§4. Its participants are the quest's bestower and title-holder, not role precepts, so neither
constraint reaches it either [I].) The altar rite inherits whatever our own role precepts say — which, for the preacher rung, is `Precept_RoleMulti` with
`activationBelieverCount: 1` (§4A). Wherever this document previously propagated the
single-holder constraint to those rites, it was importing a claim that had already been
withdrawn; see § *Status* → *The commitment*.

### 5. Where the player sees it — almost entirely vanilla's

| Surface | Source | Evidence |
|---|---|---|
| "Your colony's primary ideoligion is now X" | `RecalculateIdeosBasedOnPlayerPawns` → `LetterLabelNewPrimaryIdeo` | [V] — free |
| "X is now the Y", with a sound, per role seated | `Precept_Role.Notify_PawnAssigned` → `Messages.Message("MessageRoleAssigned"…)` + `SoundDefOf.Quest_Succeded` | [V] — free |
| The colony's ideoligions, precepts and role slots with their holders | `MainTabWindow_Ideos` / `IdeoUIUtility` | [V] — free |
| The founder's ideo plate on the character card | `CharacterCardUtility.DoTopStack` | [V] — free. MP's `CharacterCardUtilityDontDrawIdeoPlate` suppresses it **only** when `Multiplayer.Client != null && generating`, i.e. on the pawn-config page, never in play [V] |
| The rite's outcome letter | our worker, on `RitualOutcomeEffectWorker_RoleChange`'s shape — it composes the outcome letter, then calls `Unassign`/`Assign` on a good result [V] | [V] on the donor |
| The door *before* it is walked through | the Church quest chain, or the `FactionDialogMaker` gate already specified for Reverence (D2) | — |

**This capability needs nothing from [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61).**
Every readout above is a vanilla surface we do not patch, which is the opposite of Reverence's
position and worth saying plainly.

### 6. The alternative build, and the one line of vanilla that separates them

`RimWorld.IdeoDevelopmentUtility.ApplyChangesToIdeo(Ideo ideo, Ideo newIdeo)` is **public
static** and overwrites `ideo` **in place** from `newIdeo` — foundation, culture, memes, the
whole precept list rebuilt through `PreceptMaker.MakePrecept` + `Precept.CopyTo`, plus `name`,
`memberName`, `leaderTitleMale`/`Female`, icon, colour and styles [V]. It preserves the `Ideo`
**instance**, so every scribed reference on every pawn and faction stays valid, and it has no
`Fluid` check of its own — `Fluid` gates `Dialog_ReformIdeo`, not the utility.
`Multiplayer.Client.SyncMethods` already registers it with `.ExposeParameter(1)`, serialising
the entire replacement ideology across the wire [V].

That is a second, near-zero-code route: the colony's own ideology *becomes* the Church's
doctrine with no pawn changing `Ideo` reference.

**What separates the two is one line.** `RoleRequirement_SameIdeo.Met` is `p.Ideo == role.ideo`
— **reference equality** [V]. Under `SetIdeo` the founders and the Church's NPC believers
share one `Ideo` object and any "aligned" test is free. Under `ApplyChangesToIdeo` they hold
two doctrinally identical but distinct objects, and the Devotion alignment rule then needs a
doctrinal comparison nobody has specified.

**Selected: nothing.** § *Status* says nothing in this document is an implementation
commitment, and this section must say the same thing (`README.md` § *Verified is not
selected*). An earlier draft wrote "Selected: `SetIdeo`" three screens below a Status section
that contradicted it.

**The build above is written against `SetIdeo`, and these are the reasons it is:** it is what
[`ENDING.md`](../plot/ENDING.md) literally asks (*"become what the Church says they are"*), it
makes Devotion alignment reference equality, it is what Multiplayer's own `FactionCreator`
does mid-game, and it is what vanilla preachers already do to colonists.
`ApplyChangesToIdeo` is the recorded alternative, taken **if**
[#49](https://github.com/cjd721/Rimworld-Archinity/issues/49) rules alignment doctrinal —
*Outstanding decisions* 12. The commitment between the two is #49's to make, not this
document's.

⚠ **The selected route moves Reverence's referent.**
`docs/requirements/RELIGION.md` says *"Reverence is tied to the player's actual ideology."*
After the rite the player's primary ideology **is** the Church's, which the Church faction
already follows completely — so a naive reading pins Church Reverence to its ceiling the
instant the rite completes. Owner: [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97),
whose existing question ("per (faction × ideo), or per faction against the player's current
primary") is the same question. *Outstanding decisions* 14.

**And the pin does not stay inside this document.** [`PRESSURE.md`](PRESSURE.md) § *The build*
feeds **global Reverence** into the global threat scalar as one bounded contributor, and again
into the `StorytellerComp.IncidentChanceFinal` selection weight — it names the Reverence term
but not this event. So if the rite pins Church Reverence to its ceiling, it also moves raid
magnitude and incident selection on the tick the rite completes, campaign-wide. That seam is
named here so it is visible from this side; the direction and size of the response are
[#60](https://github.com/cjd721/Rimworld-Archinity/issues/60)'s, and what the pin itself should
be is #97's.

### Cost

| Piece | Cost |
|---|---|
| The consecration rite | **New C#** — one `RitualOutcomeEffectWorker`, ~40 lines, plus the `RitualPatternDef` / `RitualBehaviorDef` / `RitualOutcomeEffectDef` trio in XML |
| Founder-only role eligibility | **New C#** — one `RoleRequirement` subclass, ~10 lines, reading `CompFounderRecord` ([`TRANSCENDENCE.md`](TRANSCENDENCE.md)) rather than a predicate of its own |
| The founders' leader role | **XML** — one `PreceptDef`, `ParentName="PreceptRoleSingleBase"`, `leaderRole: true`, `activationBelieverCount: 1` |
| The founders' preacher role | **XML** — one `PreceptDef` on `Precept_RoleMulti`, so both colonies get a holder under **T-21** (§4A). Its activation fields are **[I]** until `Precept_RoleMulti` is read |
| Commitment record | **New C#** — 3 fields and 3 `Scribe_*` lines on the religion `WorldComponent` |
| The Church's doctrine | **XML** — `FactionDef.fixedIdeo` and companions, no code |
| Announcement, role messages, ideo tab, character card | **Nothing** |
| Multiplayer | **Nothing** — the rite is inside simulation and `Precept_Ritual.ShowRitualBeginWindow` is already registered [V] |
| The alignment predicate | **[#49](https://github.com/cjd721/Rimworld-Archinity/issues/49)** — a requirement, not a mechanism |

**Aggregate: ~55 lines of C# in the existing `ArchinityAltar.dll`, two `PreceptDef`s and one
ritual def trio. No new saved collection, no new Def type, no Harmony patch.** This is
cheaper than Exaltation, and for the same reason: we are not building a system, we are
invoking one the DLC already ships.

## The build — religious institutions inside foreign factions

`docs/requirements/RELIGION.md`: *"With sufficient Reverence, the player can spend Goodwill to
establish churches, monasteries or equivalent religious institutions inside friendly factions.
These institutions deliberately counteract natural Reverence decay and can eventually make the
faith self-sustaining. Hostile governments can suppress institutions, persecute apostles and keep
Reverence falling unless the player changes the political situation."*

**This section owns the institution. It does not own the store and it does not own the gate.**
The per-faction Reverence ledger is *The build — Reverence* §1 above
([#98](https://github.com/cjd721/Rimworld-Archinity/issues/98)); §3 below states the interface this
capability needs from it and adds nothing else. The mechanism that refuses the founding action
until Reverence is high enough, and draws the threshold before it is reached, is
[`POLITICS.md`](POLITICS.md) § *Standing as a content gate*; §2 below consumes it rather than
restating it.

**Nothing in the corpus carries this.** A wide pass over both roots returned **zero in both
assembly metadata heaps** for `Embassy`, `Monastery`, `ChapterHouse`, `Diocese`, `Congregation`,
`Chapel` and `Persecut` — and zero corpus-wide for four of the seven; the other three appear only
in backstory, meme and quest **XML** with no institution behind any of them [V]. *Available
mechanisms* § *Institutions* carries the exact scoping. What does exist is two near misses and one
genuine structural donor. So this is new code — but it is **~125–130 lines and no new saved
collection**, because the store, the gate, the decay subtraction, the world hook and the letter
shape are all already there.

### 1. What it is, structurally — a record on the ledger, not a world object

**An institution is a nested record on the per-faction Reverence entry that
`WorldComponent_Reverence` already holds.** No new component, no new world object, no map.

The ticket's own guess was *"probably not a `WorldObject` — closed
[#10](https://github.com/cjd721/Rimworld-Archinity/issues/10) established that a bare `MapParent`
shrine carries real costs and cannot own a quest clock under Async Time"*, and that is **confirmed
and it is the right conclusion for a stronger reason than the one given.** #10's finding is about
`MapParent` specifically — a full simulated map, a tick cost, an authoring requirement that its
`WorldObjectDef` declare no `incidentTargetTags` or it becomes the sole incident target whenever it
ticks, and a quest clock that `MultiplayerAsyncQuest.TryGetQuestMap` binds to the wrong speed. A
plain `WorldObject` avoids all of that. **The reason not to use one is different: it would be a
second store for a number #98 already owns**, and two stores for one number is the specific failure
this capability was re-scoped to prevent.

So: `FactionReverence` gains one field.

| Field | Purpose |
|---|---|
| `List<Institution> institutions` | one record per institution planted in that faction |

and `Institution : IExposable` is four values:

| Field | Purpose |
|---|---|
| `ReligiousInstitutionDef def` | the tier — shrine, church, monastery — carrying its Reverence gate, its Goodwill price and its sustain contribution |
| `int foundedTick` | when, for the letter, the inspect string and any maturation ramp |
| `int suppressedTick` | `-1` when operating; the tick suppression began otherwise (§4) |
| `PlanetTile tile` | optional, and only for display — which of that faction's settlements it sits beside |

**`ReligiousInstitutionDef : Def` is the whole tunable surface**, and it is XML: a label, a
description, the Reverence threshold to found one, the Goodwill price, the sustain it contributes,
the maximum number of that tier per faction, a `float suppressedSustainFactor` (§4), and a
work/time cost if one is wanted. One further field is global rather than per-tier and belongs on
the same settings-style Def instance the decay rate already lives on: `bool allowNegativeDecay`
(§3). **Not `ModSettings` — T-18.**

### 2. The gate and the price — consumed, not rebuilt

The founding action is a `DiaOption` on the faction's comms dialogue, appended by the
`FactionDialogMaker.FactionDialogFor` postfix *The build — Reverence* D2 already costs. Its gate is
[`POLITICS.md`](POLITICS.md) § *Standing as a content gate* §3, on the Reverence axis:

```
Found a monastery among the Reach (cost: 40 goodwill)  (need 60 Reverence — currently 41)
```

**This is the split the requirement asks for, exactly**: *"Reverence unlocks the diplomatic option;
normal Goodwill remains the spend lever."* One axis is **checked**, a different axis is **charged**,
and vanilla already does both at once on this same surface — `RequestTraderOption` gates on ally
status and charges 15 goodwill, with the price in the label and the gate in the disabled reason
[V]. The label's *"(cost: N goodwill)"* half is vanilla's own formatting, built from
`-Faction.OfPlayer.CalculateAdjustedGoodwillChange(faction, -N)` [V].

**The charge itself, and the two ways it lies if written naively** [V, both from
[`POLITICS.md`](POLITICS.md) § *Available mechanisms*]:

- `Faction.OfPlayer.TryAffectGoodwillWith(faction, -cost, …)` returns a `bool`, and gates C and E
  make it return `false` silently. **Check it before creating the record and before sending the
  letter** — an institution founded for free because the charge no-opped is worse than one that
  could not be founded.
- `CalculateAdjustedGoodwillChange` amplifies any change moving *toward* natural goodwill by 25% of
  the remaining gap, so a −40 price can land as more than −40. The label prints the adjusted figure
  because it calls the same method; the record must store the price actually paid if a refund is
  ever wanted.

**A second, deliberate gate:** `ReligiousInstitutionDef.maxPerFaction`, and a relation-kind floor.
The requirement says *"inside **friendly** factions"*, so the option is disabled — never omitted,
see *Persistence and multiplayer* — with `"MustBeAlly"`-shaped reasoning when the faction is
hostile. Vanilla's own key is reusable verbatim.

### 3. The interface to the Reverence ledger — exactly three things, and two already exist

This is the whole of what #73 asks of #98:

1. **`float sustain` on `FactionReverence`.** Already specified by
   [#98](https://github.com/cjd721/Rimworld-Archinity/issues/98) — *The build — Reverence* §1 lists
   it as *"institutional resistance to decay — written by #73, read here"*, and §4 already
   subtracts it from the decay step. **Nothing about #98's decay code changes.**
2. **The nested `institutions` list (§1)**, which is one extra
   `Scribe_Collections.Look(ref institutions, "institutions", LookMode.Deep)` inside
   `FactionReverence.ExposeData`. The record is already scribed `LookMode.Deep` from the
   component's single collection, so this nests for free and a save predating it loads the field as
   null → empty.
3. **`sustain` is recomputed from the list whenever the list changes**, and never independently
   accumulated. Founding recomputes it; suppression recomputes it; a faction losing its last
   institution recomputes it to zero. This is the one design rule that keeps the two numbers from
   drifting apart across a months-long save, and it costs a three-line method.

**The requirement's *"can eventually make the faith self-sustaining"* is the case where the
recomputed `sustain` meets or exceeds the decay step** — #98's §4 subtraction, unchanged, with no
special-casing. Self-sustaining is not a state, it is an inequality.

⚠ **`sustain` needs a ceiling, and the build sets one rather than handing the question back.**
Nothing in #98's decay step stops `sustain` exceeding the step and turning decay into *growth*,
which the requirement does not ask for and which would make institutions a second acquisition loop
rather than a preservation one. **The mechanism is one clamp and a `bool allowNegativeDecay`
defaulting to `false`** — the step becomes `Max(0, step − sustain)` unless the flag says otherwise.
Whether the flag is ever flipped is then an ordinary balance call on an XML field, and the *"can
eventually make the faith self-sustaining"* clause is satisfied at the default. Stating the default
is the point: *institutions preserve, they do not evangelise*, unless someone deliberately says
otherwise.

### 4. Suppression — one Harmony postfix, on a method vanilla already uses for exactly this

**`RimWorld.Faction.Notify_RelationKindChanged(Faction other, FactionRelationKind previousKind, bool canSendLetter, string reason, GlobalTargetInfo lookTarget, out bool sentLetter)`
is the hook, and it is `public`** [V]. It is vanilla's single convergence point for *"the political
situation with this faction just changed"*, and **it already contains two suppression routines of
exactly the shape this capability needs** [V]:

- **The suppression branch.** When `other == OfPlayer && this.HostileTo(OfPlayer)`, it walks
  `Find.WorldObjects.AllWorldObjects`, finds every object whose `Faction` is the newly hostile
  faction, fetches its `TradeRequestComp`, and calls `component.Disable()` on any active request —
  then, per map, `map.passingShipManager.RemoveAllShipsOfFaction(this)`. **A player-facing
  arrangement with that faction is disabled, not destroyed, the moment the faction turns hostile;
  a transient one is removed outright.** That is suppression, shipped, and the split between the
  two halves is the model for ours.
- **The restoration branch, and its letter.** When `other == OfPlayer && !this.HostileTo(OfPlayer)`,
  it collects every site of that faction where
  `factionMustRemainHostile && sites[i].Faction == this && !sites[i].HasMap` — **the `!HasMap` term
  matters: a site the player is currently standing on is left alone** — and if any remain sends
  `LetterLabelSiteNoLongerHostile` / `…Multi`, the multi form building a bulleted
  `"  - " + LabelCap` list with a parenthesised pawn name per entry, and a `LookTargets` over the
  affected tiles, before destroying them.

**So the postfix is small and its letter is a transcription.** On the hostile edge: mark every
institution in that faction `suppressedTick = TicksGame`, recompute `sustain`, and send a
`ChoiceLetter` built on the `…Multi` shape naming each institution and the faction. On the friendly
edge: clear `suppressedTick`, recompute, and send the mirror letter.

**Suppressed, not destroyed — and the requirement decides that, not the design.**
*"keep Reverence falling **unless the player changes the political situation**"* says the state is
reversible by changing the situation, which is precisely the friendly edge of this same hook. The
vanilla routine it is modelled on destroys its sites; ours must not, and the difference is
deliberate and worth stating because the donor code is right there doing the other thing.

**What suppression costs the player, mechanically — and the build settles the branch rather than
handing it back.** A suppressed institution contributes
`def.sustain * def.suppressedSustainFactor` to the recomputation instead of `def.sustain`, with
**`suppressedSustainFactor` defaulting to `0f`**. At the default, suppression simply removes the
help and #98's decay step resumes at full rate. The requirement's *"persecute apostles"* clause —
a hostile government making things actively worse than neglect — is then **a negative value in that
same field**, needing no second mechanism and no `if`. Whether it is ever set negative is an
ordinary balance call; the branch exists either way.

⚠ **The postfix must read the right operand.** `Notify_RelationKindChanged` is an instance method on
the faction whose relation changed, and `other` is the counterparty. **The two branches quoted
above** are each guarded on `other == OfPlayer` [V] — though the method as a whole is not: its
prisoner-status sweep and its attack-target-cache block run for any pair. Read `__instance` for the
faction whose institutions move. This is the same discipline the apostle hook needs (*The build —
Reverence* §3A) and for the same reason.

⚠ **Guard on `Current.ProgramState == ProgramState.Playing`** — but not for the reason an earlier
draft of this section gave. **It does *not* fire during world generation**, and saying so sent an
implementer hunting a bug that cannot happen [V]:

- `FactionGenerator.NewGeneratedFactionWithRelations` reaches `Faction.SetRelation(FactionRelation)`,
  which mutates `relations` directly.
- `Faction.TryMakeInitialRelationsWith` hand-constructs **both** `FactionRelation` objects and
  appends them to the two `relations` lists itself.

Neither calls `Notify_RelationKindChanged` at all. The only route that could fire early —
`GoodwillSituationManager.CheckHostilityChanged` → `Notify_GoodwillSituationsChanged` →
`CheckKindThresholds` — is itself guarded on `Current.ProgramState != ProgramState.Playing`, and
worldgen runs at `ProgramState.Entry`.

**The guard is still required**, because the hook *does* reach us at
`ProgramState.MapInitializing` — during map generation and during load — through
`SettlementUtility.AffectRelationsOnAttacked` and `GoodwillSituationManager.RecalculateAll`. That
is the window in which the component may not yet hold its records.

⚠ **And the vanilla body consults `ProgramState` three times, not once.** The first occurrence
suppresses letters; a second brackets the prisoner-status sweep; a third `return`s before the
attack-target-cache and lord block [V]. An earlier draft said the method used it *"only to suppress
letters"*, which is true of the first line and false of the method.

### 5. Where the player sees it

Four surfaces, three of them free:

- **The gate, before it is reachable** — the disabled `DiaOption` with its threshold and the
  player's current Reverence, §2. This is the *"see the carrot"* clause of
  [`requirements/RELIGION.md`](../requirements/RELIGION.md) § *Reverence — Religious Penetration,
  Not Goodwill++*, satisfied on vanilla's own surface.
- **The founding and the suppression** — `ChoiceLetter`s, on the shapes above and on *The build —
  Reverence* §5's band-change letter (VFED's `Letter_VisibilityChange` is the shipped precedent
  [V]).
- **The standing state** — the faction row tooltip that *The build — Reverence* D1 already builds.
  Institutions belong in the tooltip rather than in the row: *"3 institutions, 2 suppressed;
  sustain 0.4/day"* is a line of tooltip text and needs none of D1's contested layout arithmetic.
  **This is the piece that makes `sustain` legible**, and without it the number the whole capability
  exists to move is invisible.
- **On the world map, optionally** — `Settlement.GetInspectString` is the template and it is
  vanilla's: it already prints `"RequiresTradePermission"` with the required title **beside the
  live relation kind and goodwill number** [V], which is precisely the register an institution line
  belongs in. Reaching it is the alternative build, §6.

### 6. The alternative build — a `WorldObjectComp` on `Settlement`, and what separates them

**It is cheaper than it looks, and it is still not selected.** `WorldObjectDef Settlement` already
declares a `<comps>` list with five entries, so a `PatchOperationAdd` puts a comp of ours on every
settlement in the game [V]. And the backfill is free: `WorldObject.ExposeData` calls
`InitializeComps()` on `LoadingVars` **from `def.comps`**, then `comps[i].PostExposeData()` — comps
are *rebuilt from the def at load*, never scribed as a collection, so adding one mid-campaign
initialises it on every existing settlement rather than erroring [V]. `WorldObjectComp` gives
`CompInspectStringExtra`, `GetDescriptionPart`, `GetFloatMenuOptions(Caravan)`, `GetGizmos`,
`GetCaravanGizmos` and `PostDrawExtraSelectionOverlays` [V] — the institution would be visible,
selectable and caravan-reachable on the world map with no new world object and no map.

**What separates the two builds is not cost, it is ownership.** A comp holding institution state is
a second store for a number #98 owns, keyed by `Settlement` rather than by `Faction`, and
settlements are destroyed, abandoned and re-founded over a campaign while the faction persists.
The requirement is per faction — *"institutions inside friendly factions"*, *"counteract natural
Reverence decay"* — and the decay it counteracts is per faction.

**So the recommendation is the ledger, with the comp available as a pure display adapter**: if the
map presence is wanted, add the comp holding *nothing but a lookup* — read the ledger for
`comp.parent.Faction`, print a line — and the ledger stays the single authority. That is the
version to build if [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61) or playtest says
the institution needs to be somewhere the player can point at.

### Cost

| Piece | Cost |
|---|---|
| `ReligiousInstitutionDef` — tiers, thresholds, prices, sustain, caps | **XML** — one new Def type |
| `Institution` record + the nested list on `FactionReverence` | **New C#**, ~20 lines, inside #98's component. **No new saved collection** |
| `sustain` recomputation | **New C#**, ~5 lines |
| The decay subtraction that consumes it | **Free** — [#98](https://github.com/cjd721/Rimworld-Archinity/issues/98) already built it |
| The Reverence gate and the Goodwill price, shown before reached | **Free** — [`POLITICS.md`](POLITICS.md) § *Standing as a content gate* §3, on the postfix D2 already costs |
| The founding action | **New C#**, ~35 lines, hosted on an MP-whitelisted type |
| Suppression and restoration | **Patch** — 1 Harmony postfix on `Faction.Notify_RelationKindChanged`, **~55–60 lines** including both letters. The `…Multi` letter builder this transcribes is ~25 lines on its own and there are two edges; an earlier estimate of ~40 did not account for that |
| Institutions in the faction tooltip | **New C#**, ~10 lines, inside D1's existing tooltip |
| World-map presence (§6) | **XML** — one `PatchOperationAdd` — plus ~25 lines, **only if taken** |
| Multiplayer | **Free** — the comms click is already a synced command |
| Every number | **Requirements / balance** — see *Outstanding decisions* |

**Aggregate: one new Def type, one Harmony postfix, ~125–130 lines of C# in the existing
`ArchinityAltar.dll`, and no new component, no new world object and no new saved collection.** No
new assembly. The optional world-map adapter adds ~25.

The mechanisms are [V]; **the claim that they compose into the behaviour the requirement describes
is [I]**, as every proposed build is until something is built.


## Persistence and multiplayer

### Exaltation

- **The transformation reaches a save in two halves, and only one of them is free.** Def fields —
  labels, titles, permits, `royalFavorLabel`, `maxPsylinkLevel`, trader kinds — are read at use time
  and change on the next load of any save. **Scribed state keeps the Empire.** That covers
  `Faction.name` (generated by `factionNameMaker`), the faction leader and world pawns with their
  `Imperial*` backstories, settlement names, and the faction's `Ideo`, which is created only from
  the worldgen def (`docs/engine/factions-and-worldgen.md` § *What breaks, and the fix* →
  `Faction.ideos` [V]). **The Church's name, clergy and creed therefore exist only in a world
  generated after the patch.** Before the freeze ([#18](https://github.com/cjd721/Rimworld-Archinity/issues/18))
  that costs nothing; after it, it is a new world.
- **No new saved state anywhere in this build.** Exaltation, titles and permits live on
  `Pawn_RoyaltyTracker` inside `Pawn.ExposeData`. The suspicion worker's output lives in
  `GoodwillSituationManager.cachedData`, an unscribed cache rebuilt every 1,000 ticks [V].
- **Player-initiated royalty writes are already synced.** `Multiplayer.Client.SyncMethods` registers
  `Pawn_RoyaltyTracker.AddPermit`, `RefundPermits`, `SetTitle` and `ResetPermitsAndPoints`, plus the
  two caravan permit calls. `GainFavor` / `SetFavor` / `TryUpdateTitle` are deliberately not synced,
  because every caller is already in simulation. **[I] this pass** — verified by #53's first
  resolution and not re-read after the reopen.
- **The rite is simulation.** The bestowing ceremony is a `LordJob_Ritual`, and its
  `RitualOutcomeEffectWorker_Bestowing.Apply` runs in the synced tick [V].
  `AssembliesCustom/Multiplayer.dll` names `LordJob_BestowingCeremony` and
  `LordToil_BestowingCeremony_Wait` [I — metadata hit]. The two-client check is under
  § *Verification*.
- **The suspicion worker is simulation — but its cache is not only filled from simulation.**
  `GoodwillManagerTick` runs inside the world tick on both clients [V], and the worker may read only
  factions, defs and the Reverence records. But `GoodwillSituationManager.cachedData` is unscribed,
  `RecalculateAll` runs only from that 1,000-tick tick, `GravshipUtility` and `SettlementUtility`, and
  `GetSituations` fills a missing entry lazily, including from `FactionUIUtility`, then runs
  `CheckHostilityChanged` [V]. A client joining after a Reverence change but before the next
  boundary computes the cap from live Reverence while the host's cache is stale, so `GoodwillWith`
  can differ (mechanism [V]; desync [I]). **Fix: every Reverence write calls
  `Find.GoodwillSituationManager.RecalculateAll`** (§6). No saved state.
- **Titles are per pawn**, so **T-21** does not bite: both players see the same founders holding the
  same titles.
- **T-18 surfaces now belong to the Church.**
  - VFE Empire's `WorldComponent_Hierarchy` reads `PER_RANK => VFEEmpireMod.Settings.noblesPerTitle`
    inside the daily `WorldComponentTick` → `RefreshPawns` → `MakePawnFor` → `PawnGenerator.GeneratePawn`
    chain [V, re-read on the 1.6 decompile]. MP Compat reads `WorldComponent_Hierarchy.Instance.TitleHolders`
    but patches none of those three [I this pass].
  - WTL's `Filter_Factions` setting gates the roster strip (**T-54**).
  - Ignorance Is Bliss's `empireIsAlwaysEligible` is a setting ([`CONTEXT.md`](../../CONTEXT.md)
    § *The band* [I]).
  - All three must be copied settings files or, better, defs.

### Reverence

- **The apostle hook is already downstream of a synced action.** A guest walking off the map is
  simulated identically on both clients, so `Pawn.ExitMap` and therefore
  `Faction.Notify_MemberExitedMap` fire on both at the same tick in the same order [V on the
  mechanism, I that this hook qualifies]. No explicit synced command is needed for it, on the
  same reasoning [`POLITICS.md`](POLITICS.md) sets out for the ripple.
- **The decay tick draws no `Rand`** and is trivially clean. The hazard was never "uses `Rand`"
  but "consumes the shared stream a different number of times per client"
  (`docs/engine/determinism.md` § *Why `Rand` inside a synced tick is safe*).
- **Iterate the record list, never a dictionary of factions.** Insertion order is the only
  order both clients agree on.
- **Every tunable ships as a Def** — **T-18**.
- **Multiplayer serialises the comms-console dialogue, options included, and this constrains
  D2 harder than the field types suggest** [V].
  `Multiplayer.Client.PersistentDialog_NodeTreeWithFactionInfo` scribes every `DiaNode` and
  `DiaOption` — text, `resolveTree`, `disabled`, `disabledReason`, `clickSound` — and
  reconstructs each option's `action` delegate. **The binding gate is
  `DelegateSerialization.CheckMethodAllowed`'s fifteen-type whitelist**, not the field scribe
  modes: a delegate whose outermost declaring type does not derive from `QuestPart`, `Command`,
  `Letter`, `ThingComp`, `FactionDialogMaker` or one of the other ten **throws on load**. Host
  the action's method on a whitelisted type. On top of that, capture only `Faction` (which is
  `ILoadReferenceable`) and primitives — capturing a `WorldComponent` or a UI local hits the
  plain-object path, which also throws. Both failures are loud and both happen at load. Full
  list and messages: [`docs/engine/determinism.md`](../engine/determinism.md).
- **The player-initiated writes are the ones that need synced commands** — establishing an
  institution, calling a revolt. A UI click is not a simulated event, and that is the case the
  "wrap every write" rule is actually about. ⚠ **The rule stands; both named instances turn out to
  be covered already.** A `DiaOption` click on the comms console is synced by Multiplayer itself
  [V] — see *Institutions*, below, and
  [`POLITICS.md`](POLITICS.md) § *Persistence and multiplayer (the gate)*. The *unsynced* case is a
  gizmo or a window of our own, which nothing in this document builds.
- **One shared player faction means one Reverence number per NPC faction.** Letters are shared;
  any per-player filtering is draw-time only (**T-21**).
- If Reverence ever hooks faction-ideo recalculation, Multiplayer already brackets
  `FactionIdeosTracker.RecalculateIdeosBasedOnPlayerPawns` with a `FactionContext` push/pop [V].

### The commitment

- **The whole capability costs nothing in multiplayer, and the reason is structural.** The
  rite is a `LordJob_Ritual`; its outcome worker runs inside the synced tick on both clients,
  on the same reasoning the Exaltation rite inherits above. The one player-initiated act —
  opening the ritual window — is already covered:
  `Multiplayer.Client.SyncMethods` registers
  `SyncMethod.Register(typeof(Precept_Ritual), "ShowRitualBeginWindow")` [V]. **No
  `[SyncMethod]` of ours and no `Multiplayer.API` reference is needed for this capability**,
  unlike [`CURRENCIES.md`](CURRENCIES.md)'s `TryPurchase`.
- ⚠ **`Pawn_IdeoTracker.SetIdeo` draws `Rand`** —
  `Certainty = Mathf.Clamp01(ConversionTuning.InitialCertaintyRange.RandomInRange)` [V].
  Inside the ritual outcome that is safe by the standing rule
  ([`determinism.md`](../engine/determinism.md) § *Why `Rand` inside a synced tick is safe*),
  because both clients call it the same number of times in the same order. It would **not**
  be safe from a gizmo or a `DiaOption` action, and that is the reason the rite is a rite
  rather than a button.
- **Multiplayer already brackets the recalculation this build depends on.**
  `Multiplayer.Client.Factions.RecalculateFactionIdeosContext` is a Harmony prefix/finalizer on
  `FactionIdeosTracker.RecalculateIdeosBasedOnPlayerPawns` that pushes and pops
  `FactionContext` around it [V] — noted for Reverence above as a contingency, and load-bearing
  here.
- ⚠ **If the alternative route (§6) is ever taken, both ideos must be `Fluid`.**
  `Multiplayer.Client.SyncMethods.FixIdeoAfterCopy` is `[MpPostfix(typeof(Ideo), "CopyTo")]`
  and ends with `ideo.development.ideo = ideo; ideo.style.ideo = ideo;` with **no null check**
  [V]. `Ideo.development` is non-null only for a fluid ideo — `Ideo.Fluid`'s setter,
  `ExposeData`'s `if (fluid && development == null)`, and `CopyTo`'s own `if (ideo.fluid)`
  branch are its only writers, and the field has no initialiser [V]. Vanilla never reaches it
  because `Dialog_ReformIdeo` is only open for a fluid ideo. Calling `ApplyChangesToIdeo` on a
  non-fluid ideo therefore throws **inside an executing MP command**, half-applying the copy on
  one client. Loud in the log, silent in its symptom. This is a **proposed trap**, pending a
  central ID.
- **`Page_ChooseIdeoPreset` is not the one-way door, and the ticket's "assume host-only" was
  the wrong premise** [V]. Under Multiplayer the page is not host-only: MP wraps it in
  `Multiplayer.Client.Factions.Page_ChooseIdeo_Multifaction`, shown to a player *creating* a
  faction, whose result is a `Multiplayer.Client.Factions.IdeologyData : ISyncSimple` record
  carried into `[SyncMethod] FactionCreator.CreateFaction`. But Archinity runs one shared
  player faction (**T-21**), and joining an existing faction runs through
  `Multiplayer.Client.Factions.FactionsWindow` → `ClientSetFactionPacket` with no ideo page
  anywhere on the path [V]. The page runs once, on the host, at worldgen — before anyone
  joins, and the campaign ships a `.rid` for that anyway. The real door is the rite, which is
  inside simulation and therefore symmetric by construction.
- **One shared player faction means one commitment.** The record is world-scoped and both
  players see the same founders in the same roles (**T-21**). **That is also why the preacher
  precept is `Precept_RoleMulti` and the leader precept is not** (§4A): under one faction a
  `RoleSingle` seat is one seat for two colonies, so the preacher rung would be permanently
  held by one founder and permanently empty for the other, while one leader is the correct
  answer because there is one `Faction.OfPlayer.leader` to set.
### Institutions

- **Nothing new is persisted.** The institution list nests inside the `FactionReverence` record
  Reverence already scribes `LookMode.Deep` (*The build — religious institutions* §3), so there is
  no second collection, no second component and no migration. A save predating the feature loads
  the field null and the recomputation yields `sustain = 0`, which is the correct starting state.
- **The founding click is already a synced command, and this corrects the assumption above.** The
  *Reverence* subsection says *"the player-initiated writes are the ones that need synced commands
  — establishing an institution, calling a revolt."* The rule is right; **this instance is already
  covered.** `Multiplayer.Client.NodeTreeDialogSync` is a Harmony prefix on `DiaOption.Activate`
  that, while a `Dialog_NodeTree` is open in a multiplayer session, suppresses the local activation
  and routes it through `[SyncMethod] SyncDialogOptionByIndex(int position)`; and
  `Multiplayer.Client.PersistentDialog.Click(int ver, int opt)` is itself `[SyncMethod]` behind a
  version guard that drops a click made against a stale node [V]. **No `[SyncMethod]` of ours and
  no `Multiplayer.API` reference is needed to found an institution.** Full mechanism and its
  hazard: [`POLITICS.md`](POLITICS.md) § *Persistence and multiplayer (the gate)*.
- ⚠ **Disable the option, never omit it.** Both sync mechanisms identify the clicked option by its
  **index in `curNode.options`** [V], so an option list that differs between clients makes index
  *n* mean two different actions. Every gate in §2 — the Reverence threshold, the per-faction cap,
  the friendly-faction floor — must produce a `Disable(reason)`, not a skipped `Add`. It fails
  silently on both clients and it is the single easiest mistake to make here.
- **The enabled action's host type is constrained.** `DelegateSerialization.CheckMethodAllowed`
  requires the delegate's outermost declaring type to derive from one of fifteen whitelisted types
  [V]; `QuestPart`, `Command`, `Letter` and `ThingComp` are the realistic hosts. This is the same
  constraint D2 carries and the founding action inherits it.
- **The suppression postfix is inside simulation.** `Faction.Notify_RelationKindChanged` is reached
  from `TryAffectGoodwillWith` → `CheckKindThresholds`, which both clients execute on the same tick
  in the same order [V on the mechanism, I that this hook qualifies] — the same reasoning
  [`POLITICS.md`](POLITICS.md) sets out for the ripple. It consumes no `Rand`.
- **Every tunable is a `ReligiousInstitutionDef` field** — **T-18**. Faction Territories is the
  live worked example of getting this wrong for exactly this capability: its vassalage goodwill
  cost comes from a `ModSettings` slider [V].
- **One shared player faction means one set of institutions per faction** (**T-21**). Either
  founder can found one, both see the letters, and any per-player filtering is draw-time only.
- **Iterate the institution list, never a dictionary**, for the same determinism reason the record
  list is a list.


## Failure and recovery

### Exaltation

- ⚠ **Renaming any identifier in § *The build — Exaltation* §1 is the campaign's largest silent
  failure.** Change the defName and `Faction.OfEmpire` is null for the 22 vanilla files, VFE Empire's
  138 sites and VFE Deserters' 49. Change the `categoryTag` and 14 techprint projects lose supply.
  Change `royalTitleTags` and you get **T-36**. Every one of those consumers null-checks or
  filters, and none logs. **Relabel; never rename.**
- ⚠ **The Church must never climb eras by swapping its `Faction.def`.** **T-36** already covers the
  ladder: the tags, `royalFavorLabel` and `categoryTag` come off the new def. There is a second,
  delayed failure [V]. `FactionManager.RecacheFactions` resolves
  `empire = FirstFactionOfDef(FactionDefOf.Empire)`, and it is called only from `ExposeData` (on
  load), `Add` and `Remove`. After a swap, `Faction.OfEmpire` keeps the old instance until the next
  save load or faction add/remove. **Then it goes null**, taking every consumer in §1 with it — a
  session or a week after the change that caused it. Per-era presentation of the Church must go
  through pawn kinds and the era ceiling, not a def swap. See § *Outstanding decisions* 17, and
  **T-98**.
- ⚠ **WTL strips the Church at worldgen unless the exemption is unconditional** (**T-54**; §3). WTL's
  own entry is guarded on VFE Empire being present [V]. Because of **T-07**, the loss cannot be
  repaired after worldgen.
- ⚠ **A `PatchOperationReplace` on `permanentEnemyToEveryoneExcept` silently erases eleven mods'
  entries** (§2), and `CanChangeGoodwillFor` then freezes goodwill with each of those factions in
  both directions [V].
- ⚠ **If `maxPsylinkLevel` is not zeroed, every bestowing ceremony grants psylinks**, one level per
  loop up to the highest title held (§4) [V]. That breaches `docs/requirements/ALTAR.md`'s
  independence rule with no error, and the letter reads as a normal promotion.
- ⚠ **Never give a Church title `favorCost: 0`** — **T-28**. It leaves the ladder, freezes any pawn
  standing on it, refuses its own `rewards`, and cannot be reduced. The four non-awardable titles
  are NPC-only for exactly this reason.
- **Never set `awardWorkerClass` to `RoyalTitleAwardWorker_Instant` on a Church title.** The default
  no-op is what leaves the ceremony as the conferral event. `_Instant` calls `TryUpdateTitle` from
  inside `OnFavorChanged` [V, #53 close-out], so the title is conferred without the rite.
- **A new rung needs `kindForHierarchy` wherever VFE Empire ships.** The earlier warning *"never
  give a Church title the `EmpireTitle` tag"* is **inverted**: Church titles *are* `EmpireTitle`
  titles. `WorldComponent_Hierarchy`'s static constructor collects every `RoyalTitleDef` with
  `seniority > 0` sharing that tag, and `MakePawnFor` dereferences
  `GetModExtension<RoyalTitleDefExtension>().kindForHierarchy` with **no null check** [V]. That is an
  NRE on the daily refresh — loud, so not a trap, but a one-element omission.
- **The suspicion cap is not memory** (§6). A drop in Global Reverence lifts the cap at the next
  recalculation, and `CheckKindThresholds` turns the Church from hostile back to neutral with a
  vanilla letter once effective goodwill is **≥ 0** [V] — which the accumulated `baseGoodwill` may
  already be.
- ⚠ **Church hostility closes the Empire-only techprint trader route** (§ *Verification*):
  `FactionUtility.CanTradeWith` rejects a hostile faction and `IncidentWorker_TraderCaravanArrival`
  refuses to execute for one [V]. So §6 working as designed silently removes supply the
  reopen comment says must not be lost silently. That is correct if suspicion is meant to track the present, and
  a silent design miss if it was meant to ratchet (§ *Outstanding decisions* 11).
- **The Permits tab is no longer at risk.** **T-35** fires only when `Faction.OfEmpire` is null; under
  this build the Empire *is* the Church, so the tab seeds itself. Its failure mode collapses into the
  two above: a renamed defName, or a WTL strip.
- **RimPacts' guards stand down.** `RptFactionUtility.IsEmpire` requires `categoryTag == "Empire"`
  and non-empty `royalTitleTags`, and the Church keeps both [I this pass — #53 first resolution].
  Recorded as conflict cargo only.

### Reverence

- **Reverence is keyed by `Faction`, so it inherits T-07** — the faction roster must be final
  before world creation. A faction added later cannot acquire a Reverence history.
- **The component must tolerate a `Faction` key resolving to null on load.** `FinalizeInit`
  prunes; whether pruning is the *right* answer is [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97)'s.
- **The apostle hook fails open, not loud.** Every ordinary departure reaches it, caravans
  included (§3A), but if it is ever missed — a pawn teleported out, a mod short-circuiting
  `Pawn.ExitMap` — Reverence simply does not move and nothing is logged. Any acceptance check
  for this capability has to observe the *number*, not the absence of an error.
- **Vanilla pilgrims credit a temporary hidden faction**, so the pilgrim clause needs an
  authored quest rather than the hook (§3A). Left unaddressed, pilgrims appear to work and move
  a number nobody can ever see.
- **A `DiaOption` action hosted on the wrong type throws on load, not on click** — the MP
  delegate whitelist, under *Persistence and multiplayer*. The failure surfaces one save/load
  cycle after the code looks correct.
- **A settings-driven decay rate would desync silently** and is forbidden by construction
  (T-18).
- **The `DrawFactionRow` postfix fails visibly, not silently** — wrong column geometry draws
  text in the wrong place rather than doing nothing, which is the good failure mode. It is
  still the piece most exposed to a RimWorld update.
- **Name collision, carried forward:** `ReverenceUtility`, `Gene_Reverence` and
  `GeneGizmo_ResourceReverence` exist in the wider ecosystem — Biotech Expansion: Mythic,
  late-bound by string through MP-Compat's `AccessTools.TypeByName`. That mod is not on disk and
  its Reverence is a per-pawn gene resource, not a donor [V]. The names are taken.

### The commitment

- ⚠ **A founder can be converted to the Church's ideology by accident, and the resulting state
  is indistinguishable from the rite's.** `InteractionWorker_ConvertIdeoAttempt` on a visiting
  Church preacher converts any colonist whose `Certainty` reaches zero [V]. Vanilla announces
  it with `LetterLabelConvertIdeoAttempt_Success`, so it is loud — but the campaign must gate
  on `commitmentTick`, never on `founder.Ideo`. **This is the entire reason §2 stores anything.**
  An acceptance check that reads the ideo reference will pass on an accident.
- ⚠ **A forced primary reverts — loudly, which is why it is not a trap.**
  `FactionIdeosTracker.SetPrimary` on the player faction is undone by the next
  `RecalculateIdeosBasedOnPlayerPawns` (§3). An earlier draft claimed the revert is silent and
  proposed it for the register; that is wrong. The recalculation sends
  `LetterLabelNewPrimaryIdeo` / `LetterNewPrimaryIdeo` whenever the promoted ideo differs from
  the standing `primaryIdeo` [V], and the revert case is precisely a promotion **over** a
  different primary — so the player gets a letter announcing the ideology they did not choose.
  No trap ID is allocated. The recovery-relevant point survives: **do not call `SetPrimary` on
  the player faction at all**; let the believer counts do the promotion.
- **The preacher role fails quiet in the direction that matters.** This is verified on
  `Precept_RoleSingle`; whether `Precept_RoleMulti` — the class §4A now selects for the
  preacher — deactivates on the same field is **[I]** and owed a read, so treat the shape
  below as the hazard to check for rather than a confirmed behaviour of the shipped def. Below
  `activationBelieverCount`, `Precept_RoleSingle.RecacheActivity` deactivates the role and
  nulls its holder. It *does* send `LetterLabelRoleLost` / `LetterLabelRoleInactive` when the
  player faction holds the ideo — but a role that has **never** activated sends nothing at all,
  because the deactivation branch requires `active` to have been true. So a founders' preacher
  role shipped with vanilla's `activationBelieverCount: 3` simply never appears, with no
  message (§4A).
- **Losing a founder unseats them, and vanilla handles it.**
  `Precept_RoleSingle.Notify_MemberChangedFaction` calls `Assign(null, addThoughts: false)`
  when the holder leaves the player faction, and `RecacheActivity` nulls the holder whenever
  `ValidatePawn` fails — dead, destroyed, no longer a free non-slave colonist, or no longer
  meeting a `RoleRequirement` [V]. `committedFounders` keeps the historical record; the seat
  does not.
- **The commitment record tolerates dangling references.** `committedIdeo` can resolve to null
  if the ideology is ever removed — `IdeoManager.Remove` is reachable through
  `TryQueueIdeoRemoval` when no faction and no living pawn holds it [V] — and a dead founder's
  `Pawn` reference can resolve to null. Both read as "no commitment on record", which is the
  wrong answer for a campaign gate; the component must treat a non-null `commitmentTick` as
  authoritative and the references as decoration.
- ⚠ **Setting `awardWorkerClass`-style shortcuts has an analogue here: never give the founders'
  role precepts vanilla's `IdeoRole_Moralist` or `IdeoRole_Leader` `defName`s, and never patch
  vanilla's.** Both are conferred on *every* ideology in the game, NPC factions included, and a
  `PatchOperation` on them changes the moral guide for the whole planet with no error (§4A).
### Institutions

- ⚠ **A `sustain` that is stored rather than recomputed drifts, and nothing detects it.** Two
  numbers describing one fact — the institution list and the decay offset — diverge the first time
  a code path changes one without the other, and the symptom is a decay rate that is quietly wrong
  for the rest of the campaign. *The build* §3 makes `sustain` a recomputation for this reason and
  no other.
- ⚠ **A goodwill charge that silently no-ops founds a free institution.** `TryAffectGoodwillWith`
  returns `false` under gates C and E and clamps at `GetMaxGoodwill` [V,
  [`POLITICS.md`](POLITICS.md)]. **Check the `bool` before creating the record**, not after —
  otherwise the requirement's *"spend Goodwill"* clause is unenforced against exactly the factions
  whose relations are locked.
- ⚠ **Omitting a gated founding option instead of disabling it desyncs the comms option index**,
  silently, on both clients (*Persistence and multiplayer*).
- **Suppression fails open.** If the `Notify_RelationKindChanged` postfix is ever missed — a mod
  short-circuiting the method, a relation changed through `SetRelationDirect` — institutions keep
  sustaining a faction that is now shooting at the colony, and nothing is logged. Any acceptance
  check has to observe `sustain`, not the absence of an error. This is the same failure shape the
  apostle hook has (*Failure and recovery* § *Reverence*) and it is inherent to a Harmony
  observation of a vanilla event.
- **The postfix can fire before the component holds records — at `MapInitializing`, not at
  worldgen.** Both worldgen relation-seeding paths bypass the hook entirely
  (`FactionGenerator.NewGeneratedFactionWithRelations` → `Faction.SetRelation`, and
  `TryMakeInitialRelationsWith`, which appends both `FactionRelation` objects itself) [V]. The real
  early window is map generation and load, through `SettlementUtility.AffectRelationsOnAttacked`
  and `GoodwillSituationManager.RecalculateAll`. Guard on
  `Current.ProgramState == ProgramState.Playing` (*The build* §4) — an earlier draft gave the right
  guard with the wrong justification, which would send an implementer hunting a worldgen bug that
  cannot happen.
- **Institutions are keyed by `Faction`, so they inherit T-07** — the faction roster must be final
  before world creation. A faction added later can never host one.
- **A faction removed mid-campaign takes its institutions with it.** They nest inside the
  `FactionReverence` record, which *The build — Reverence* §2 prunes on a null `Faction` reference.
  Whether pruning is right is [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97)'s
  question for Reverence, and the institutions inherit whatever it decides — they do not need a
  second ruling.
- **A `sustain` exceeding the decay step would turn decay into growth**, and nothing in #98's step
  prevents it on its own. The build clamps at `Max(0, step − sustain)` behind
  `allowNegativeDecay: false` (*The build* §3); **shipping without the clamp is the silent failure**
  — institutions quietly become a second acquisition loop the requirement never asked for, and the
  symptom is a Reverence number that rises while nobody is doing anything.
- **Suppression that destroys rather than disables has no route back**, and the requirement
  explicitly wants one (*The build* §4). The donor routine in the same vanilla method destroys its
  sites, so the wrong behaviour is the one that is easiest to copy.


## Status

**Verified available mechanism. Nothing here is an implementation commitment.**

### Exaltation

Established by
[Church Exaltation and the sacred titles](https://github.com/cjd721/Rimworld-Archinity/issues/53).
First resolved 2026-09-12 as a second Church faction beside an untouched Empire; **reopened
2026-09-14** when the campaign ruled that the Empire becomes the Church wholesale; **re-resolved
2026-09-15** as the in-place transformation above.

**Evidence class: READ.** `corpus.py --check` was clean at the start of the pass (155 mods). Read
this pass:

- `Assembly-CSharp.dll` 1.6, decompiled whole;
- `VFEEmpire.dll` from `2938820380/1.6/Assemblies/`, decompiled whole (227 files);
- VFE Deserters' 1.6 assembly from `3025493377/1.6/Assemblies/`, decompiled whole (168 files);
- Royalty's `Faction_Empire.xml`, `RoyalTitles_Empire.xml`, `RoyalPermits_Empire.xml` and the three
  Empire trader kinds;
- WTL's `TechLevels_FactionDefs.xml`;
- the fifteen mods' `FactionDef[defName="Empire"]` patches (1.6).

Inherited claims not re-read are marked **[I]** where they are used.

**The mechanisms are [V]; the claim that they compose into the Church is [I]** until something is
built. The specific untried composition is the ceremony with `maxPsylinkLevel` 0, and the suspicion
worker's cap driving `CheckKindThresholds` from Reverence.

**Selected, pending Conrad's fiction calls:** the in-place transformation (§1–§3), the vanilla
bestowing ceremony as the rite (§4, alternative priced), and the Reverence-derived suspicion worker
(§6). **Deleted from the build:** the second Church faction, the permits-card seed and the
bestowing-quest suppressor.

**Verdict for the sourcing ledger ([#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)):**

| Piece | Verdict |
|---|---|
| Royalty's title / favour / permit / ceremony system | **reuse as-is** — carrier is the base DLC |
| Royalty's `Empire` FactionDef and its content | **transform in place, in XML; rename nothing** — every identifier is load-bearing (§1) |
| VFE Empire honour / hierarchy / ceremonies / `VFEI_` permits | **follows the Church automatically if shipped** — all of it resolves `Faction.OfEmpire`. It brings the `WorldComponent_Hierarchy` **T-18** defect with it |
| VFE Deserters | **follows the Church automatically if shipped** — its 49 `OfEmpire` sites now point at the Church, which is what the Schism donor reading in [`CURRENCIES.md`](CURRENCIES.md) needs |
| Church suspicion | **author** — one `GoodwillSituationWorker`, ~30 lines |

### Reverence

Established by
[Reverence, end to end](https://github.com/cjd721/Rimworld-Archinity/issues/98), evidence class
**READ** — every mechanism claim rests on 1.6 assemblies decompiled with `ilspycmd`, at the
versions pinned in `docs/data/MOD-SNAPSHOT.md` (`corpus.py --check` clean at the start and end
of that session). #98 supersedes [#52](https://github.com/cjd721/Rimworld-Archinity/issues/52)
and [#74](https://github.com/cjd721/Rimworld-Archinity/issues/74), which split one behaviour
across three implementation seams.

**The composition is [I] by construction.** Each mechanism above was read; the claim that they
compose into "57 out of 100, earned by play, decaying when neglected, visible on the faction
row" is a design, not a verified fact, until something is built.

**Three inherited claims were re-derived and two were wrong** — see *Available mechanisms*.

**This document was itself audited against the assemblies after it was written, and three of its
own claims were wrong**: the faction-row geometry and conflict surface (D1), the MP delegate
constraint on a gated dialogue option (D2), and a caravan escape path that does not exist. All
three are corrected above. The lesson worth keeping is that the D1 error came from a sweep that
skipped the UTF-16LE pass — three mods patch `DrawFactionRow` and two more fork it, and the
ASCII-only pass found two. `docs/agents/capability-research.md` warns about exactly this and it
still happened — **and the wide form it prescribes is itself broken**
([#103](https://github.com/cjd721/Rimworld-Archinity/issues/103)), so running the pass as written
would not reliably have caught it either.

### The commitment

Established by
[Mid-game ideology commitment for the founders](https://github.com/cjd721/Rimworld-Archinity/issues/75),
evidence class **READ** — vanilla `Assembly-CSharp.dll`, the Ideology DLC's shipped defs under
`common/RimWorld/Data/Ideology/Defs/`, `Multiplayer.dll`
(`2606448745/1.6/AssembliesCustom/`) and `VanillaMemesExpanded.dll`
(`2636329500/1.6/Assemblies/`), all decompiled with `ilspycmd` at the versions pinned in
`docs/data/MOD-SNAPSHOT.md`. `corpus.py --check` clean at the start and the end of that session.

**This is the one section of this document whose headline is a positive.** The mechanisms are
[V]; the claim that a rite composing three public calls delivers the campaign's commitment is
[I], as every build is until something is built. The untried part is small: `SetIdeo` onto an
NPC faction's `Ideo` from inside a ritual outcome worker, which is a combination of two things
each of which vanilla does separately.

**Three claims this ticket inherited were re-derived. One is half wrong, one holds — and the
third was never the claim this document said it was:**

| Inherited claim | Verdict |
|---|---|
| Closed #8 — *"`Faction.ideos` is generated once from the worldgen def and never regenerated"* | ⚠ **Half false, and the halves must be kept apart.** The player faction's **`primaryIdeo` pointer** is recomputed from live free-colonist believer counts on every member gain, loss and conversion [V] — so "never regenerated" is wrong about *which* `Ideo` the faction points at, and that is the half this capability runs on. But #8's actual claim was about **doctrine**: that a later def's `fixedIdeo` / `forcedMemes` never re-apply to a faction that already exists. **That half stands** — the doctrine is built once on the `CreateFactionAndAddToManager` → `ChooseOrGenerateIdeo` → `MakeFixedIdeo` path and nothing re-runs it on a live faction [V]. A recomputed pointer is not a regenerated ideology, and this document previously reported #8 as flatly false without that qualifier. |
| *"Forcing a specific ideology is not possible in XML; `FactionDef.fixedIdeo` / `ideoName` / `forcedMemes` are NPC-only"* | ✅ **Confirmed [V]** — `Page_ChooseIdeoPreset.PostOpen` applies them inside `if (allFaction != Faction.OfPlayer && …)`. |

⚠ **Withdrawn: the "#10 claimed role-gated rites use `Precept_RoleMulti`" falsification.** #10
made no such claim, so there was nothing to falsify and the row asserting it has been removed.
What #10 actually said was that **we should author our own role precepts as `Precept_RoleMulti`**,
so that under one shared player faction each of the two colonies gets a holder, and that
`Precept_RoleMulti.Assign` is uncapped. **Both are true** [V]. The damage was downstream: having
recorded #10 as falsified, this document then reimported the **single-holder constraint** as
fact and propagated it to the Exaltation and altar rites. That constraint is deleted (§4), the
preacher precept is `RoleMulti` (§4A), and `RitualRole.precept` accepts any `PreceptDef`
regardless (§4).

**And one framing premise was wrong:** the ticket's *"Assume host-only"* for
`Page_ChooseIdeoPreset`. See *Persistence and multiplayer* § *The commitment*.
### Institutions

**Verified available mechanism. Not an implementation commitment.**

Established by
[Religious institutions inside foreign factions](https://github.com/cjd721/Rimworld-Archinity/issues/73),
evidence class **READ** — a fresh decompile of `Assembly-CSharp.dll` at the version
`docs/data/MOD-SNAPSHOT.md` pins, plus `Multiplayer.dll`, `VFEEmpire.dll` and `VFED.dll` (the
**1.6** files, never their 1.4 `Source/` trees), `FactionTerritories.dll`, `RimPacts.dll`,
`Outposts.dll`/`VOE.dll`, shipped Core XML, and a wide pass over both corpus roots in ASCII and in
a hand-typed null-interleaved UTF-16LE form, validated against known hits before any negative was
trusted.

Three findings shape the build:

1. **The corpus negative is clean and the near misses are instructive.** Nothing anywhere spells a
   church, monastery, embassy, mission house, chapter house or diocese. The two things that come
   closest — Vanilla Outposts Expanded and VFE Empire's vassals — each miss on a different axis,
   and Faction Territories carries the whole shape but converts a settlement rather than planting
   beside one.
2. **Suppression is not new code, it is a transcription.** `Faction.Notify_RelationKindChanged`
   already contains a disable-on-hostile routine and a restore-with-bulleted-letter routine, both
   over faction-owned world objects, both public and both read end to end [V].
3. **The institution needs one field from #98's store and changes none of its code.** `sustain` was
   already specified as *"written by #73, read here"*; this resolution takes that at its word and
   adds exactly one nested list beside it.

**One premise in the ticket's own body is wrong, and it is recorded rather than inherited.** #73
cites *"VFE Empire's Great Hierarchy (`WorldComponent_Hierarchy`, 147 lines)"* as the nearest
shipped analogue. **That figure is a count of the 1.4 `Source/` file — which is exactly 147 lines —
and not of the 1.6 assembly the game loads**, which is the failure
`docs/agents/capability-research.md` § *Stale source* names #73 for by name. No replacement number
is given here on purpose: a line count against a decompiler's output is an artifact of the
invocation, not a fact about the type, and two `ilspycmd` runs disagreed by twenty lines. The
load-bearing point needs no number. And having read it: **it is
not the analogue.** Its state is `List<Pawn> TitleHolders` plus a `bool`, scribed
`LookMode.Reference` — a roster of generated nobles, not a per-faction record of anything the
player placed; its `WorldComponentTick` calls `Rand.Chance` and `Rand.RangeSeeded` and generates
world pawns whose *count* comes from a `ModSettings` slider, which is the T-18 defect this document
already records under *Persistence and multiplayer* § *Exaltation*; and neither it nor anything
else in VFE Empire or VFE Deserters has any Multiplayer sync surface at all [V]. It was read
because the ticket asked for it. It is a counter-example, not a donor.

**Verdict for the sourcing ledger ([#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)):**

| Piece | Verdict |
|---|---|
| `Faction.Notify_RelationKindChanged` as the suppression hook, and its two routines as the pattern | **reuse as-is** — carrier is base RimWorld |
| The comms `DiaOption` + `Disable` gate, and MP's sync of the click | **reuse as-is** — base RimWorld and `Multiplayer.dll` |
| `WorldObjectDef Settlement`'s `<comps>` list, if §6 is taken | **reuse as-is** — base RimWorld |
| VFE Empire `WorldComponent_Hierarchy` / `WorldComponent_Vassals` | **not the donor** — read at the ticket's request and rejected on state shape, T-18 and the absent suppression path |
| Vanilla Outposts Expanded / VEF `Outposts.dll` | **not the donor** — player tiles, no host faction, no gate, no price, no suppression |
| Faction Territories' vassal outpost | **not the donor, but the closest structural precedent** — read and reported below |
| The institution record, its Def, the founding action and the postfix | **author from nothing** — ~125–130 lines |


## Available mechanisms

### Exaltation — the donor is vanilla Royalty's own Empire

Read from `Assembly-CSharp.dll` at `common/RimWorld/RimWorldWin64_Data/Managed/`, decompiled with
`ilspycmd` at 1.6.4871.

| Mechanism | What it gives the Church | Evidence |
|---|---|---|
| `FactionManager.RecacheFactions` → `Faction.OfEmpire` | the singleton every Empire consumer reads; resolved by def identity, recached only on load / `Add` / `Remove` | [V] |
| `Pawn_RoyaltyTracker` — `favor`, `titles`, `factionPermits`, `highestTitles` | Exaltation, the title, the privileges, the high-water mark; per pawn, per faction, scribed | [V, #53] |
| `FactionDef.royalTitleTags` × `RoyalTitleDef.tags`; `RoyalTitlesAwardableInSeniorityOrderForReading` | the ladder, filtered on `Awardable` (`favorCost > 0`, **T-28**) | [V, #53] |
| `FactionDef.royalFavorLabel` / `royalFavorIconPath` | the word "exaltation" wherever the engine prints the scale — except six hardcoded Keyed strings (§2) | [V] |
| `Pawn_RoyaltyTracker.OnFavorChanged` → `RoyalTitleUtility.GenerateBestowingCeremonyQuest` → `QuestNode_Root_BestowingCeremony` → `QuestPart_BestowingCeremony` → `LordJob_BestowingCeremony : LordJob_Ritual` → `RitualOutcomeEffectWorker_Bestowing.Apply` | **the rite**: bestower and honour guard arrive, `TryUpdateTitle`, spectator favour, and a psylink loop to `GetMaxPsylinkLevelByTitle` | [V] |
| `RoyalTitleDef.maxPsylinkLevel` | read by the ceremony's psylink loop, `PawnUtility.GetMaxPsylinkLevelByTitle` and `PawnGenerator`'s NPC title psylinks | [V] |
| `Reward_RoyalFavor` / `QuestPart_GiveRoyalFavor`; `RewardsGenerator` | Exaltation as an automatic quest reward; `flag5` suppresses items-only stacks for the Church | [V] |
| `RoyalTitlePermitDef` + the five delivery workers | privileges as data; workers take the faction as a parameter | [V, #53] |
| `TraderKindDef.permitRequiredForTrading` → `TitleRequiredToTrade`; refused in `IncidentWorker_TraderCaravanArrival`, `CaravanVisitUtility`, `IncidentWorker_CaravanMeeting`, `FactionDialogMaker`, `FactionUtility.CanTradeWith` (which also rejects hostility); shown by `Settlement` | **title-gated trade**, on all three Empire trader kinds | [V] |
| `GoodwillSituationWorker.GetMaxGoodwill` / `GetNaturalGoodwillOffset`; `GoodwillSituationManager` (1,000-tick recalc → `Notify_GoodwillSituationsChanged`); `Faction.GoodwillWith` clamp | Reverence-derived suspicion that turns into hostility, with no stored value | [V] |
| `CharacterCardUtility.GetTitleTipString` + `RoyalTitleUtility.GetTitleProgressionInfo` | the "see the carrot" readout — current Exaltation, next title and price, whole ladder | [V, #53] |
| `TechprintUtility.GetResearchProjectsNeedingTechprintsNow` | the one techprint tag test: `heldByFactionCategoryTags.Contains(faction.def.categoryTag)`, **no tech-level test** | [V] |

**Where vanilla reads `Faction.OfEmpire` / `FactionDefOf.Empire`** — 22 files [V], every one of
which follows the Church:

- **Worldgen:** `GenStep_Settlement` and `GenStep_Outpost` (throne rooms, landing pads), with the two
  `SymbolResolver_BasePart_*` leaves they drive.
- **Quest roots:** `QuestNode_Root_BestowingCeremony`, `_DistressCall`, `_Mission`,
  `_Mission_AncientComplex`, `_ShuttleCrash_Rescue`; `QuestGen_Lord`; `QuestPart_LendColonistsToFaction`.
- **Incident:** `IncidentWorker_CaravanArrivalTributeCollector`.
- **Rewards:** `RewardsGenerator`, `Reward_Items`.
- **Royalty:** `Pawn_RoyaltyTracker` (heir exclusion).
- **UI:** `StatsReportUtility` (**T-35**), `WorldFactionsUIUtility` (the world-creation warning).
- **Load:** `BackCompatibility` (re-adds the Empire to legacy saves).
- **Plumbing:** `Faction`, `FactionManager`, two debug-action classes.

### Exaltation — the wide pass, and what it justifies

Both corpus roots, all 155 mods, active and inactive, plus vanilla and the DLC. Every `.dll` sweep
excludes `obj/` and `Referenced/`.

- **`#Strings`, ASCII, `-i`, `OfEmpire`** — 14 mods [I]. VFE Empire and VFE Deserters are the
  validating hits, confirmed on full decompile; the other 12 are metadata hits only.
- **`#US`, exact literal `"Empire"`** — a length-prefixed, null-interleaved pattern
  (`\x0DE\x00m\x00p\x00i\x00r\x00e\x00[\x00\x01]`) with the escapes typed literally. It found 5
  assemblies: RimPacts, Better Traders Guild (both copies), Sensible Factions, Worksites Expanded's
  `MiningOutpost.dll`, Lemmy Progression. A Python reader confirmed the `0x0D` prefix byte on each
  [I — a hit, not a reading].
- **A caution on validators.** The first validator, `VFEEmpire.BestowTitle`, was **not** an exact
  `#US` entry — Python showed it continuing into `.Fi…` — so it could not validate an exact-literal
  form. The form was validated by its own byte-confirmed hits instead. **A substring you remember is
  not an exact literal until you have looked at the bytes.**
- **`#US` substring `E\x00m\x00p\x00i\x00r\x00e\x00` with `-i`** — 12 mods including VFE Empire,
  the same-heap known hit.
- **XML: `>Empire<`, `defName="Empire"`, `EmpireTitle`, `Empire_*`** — 24 mods. **Fifteen** patch the
  FactionDef in 1.6 (a first pass counted ten, missing the `defName = "Empire"` spacing and three
  `PatchOperationFindMod`-wrapped appenders), and **eleven** of those append to
  `permanentEnemyToEveryoneExcept` (§2).
- **No mod `replacesFaction` the Empire, and none removes it** [V].

**The negative that matters is the absence of a breaking consumer, and it is narrow.** What was
searched: `Faction.OfEmpire` / `FactionDefOf.Empire` uses, and `"Empire"` string literals, in the full
decompiles of vanilla, VFE Empire and VFE Deserters [V]; the other assemblies by metadata only [I].
Within that, nothing resolves the Empire by `label`, `description`, `techLevel` or `pawnSingular`.
**It is not a negative for keys this build might also touch** — the one found by audit is VFED's
`"ImperialRoyal"` backstory-category literal (§2), which no `"Empire"` search could see. Treat any
other field the reskin changes (backstory categories, pawn-kind defNames, apparel tags) as unsearched.

### VFE Empire and VFE Deserters — no longer rejected; they follow the Church

Read from the **1.6** assemblies. The source trees ship only under `1.4/` and are not what 1.6
runs.

- **VFE Empire resolves the Empire at 138 sites in 58 of 227 decompiled files [V]**, counting
  `OfEmpire` + `FactionDefOf.Empire`. #53's *"136 places across 57"* counted `OfEmpire` alone and
  reproduces exactly on the same decompile — same data, different basis. Honors, hierarchy, vassals, the royalty
  tab, ceremonies and `LordToil` gates all follow the Church unchanged. Its main button requires an
  Empire-titled colonist, which a Church-titled founder now is [I — #53's reading].
- **VFE Deserters resolves it at 49 sites in 24 of 168 files [V]** — imperial patrols, forces-size
  patches, intel extraction, `WorldComponent_Deserters`. **It is the Schism donor keyed to the
  Church by construction.** It holds no `"Empire"` string literal [V].
- **`HonorsTracker` is still not the Exaltation scale** — a `List<Honor>` with no running total
  (#53, [I] this pass).
- **`WorldComponent_Hierarchy`** builds its title list from `FactionDefOf.Empire.royalTitleTags` and
  NREs on a rung without `kindForHierarchy` [V]. Its settings-in-tick defect is **T-18** (§ *Persistence
  and multiplayer*).
- **VFE Empire's `Patches/Empire.xml`** adds `VFEE_NewFamily` to the enemy allow-list,
  `FactionExtension_Deserters { canSendDeserters: false }`, and VEF `forcedFactionData`, which makes
  the faction required at worldgen and during play [V as XML].
- **The 29 `VFEI_` permits are Church privileges as shipped** — `<faction>Empire</faction>`,
  `minTitle` in the Church ladder [V as XML].

### Exaltation — corrections, cumulative

1. **The second-faction verdict is withdrawn by requirement, not by evidence.** Its mechanism claims
   — faction-parameterised titles, techprint tags, VFE Empire hardwiring — were sound and are
   reused above.
2. **Vanilla's three trade permits are not inert.** They were inert only as a *copy*.
   `TraderKindDef.permitRequiredForTrading` names them on all three Empire trader kinds, and the
   permit gates trade in five places (§5) [V]. The earlier survey searched
   `Assembly-CSharp`'s string heap for the defNames, and XML-bound references never appear there.
3. **The bestowing ceremony grants psylinks** — `RitualOutcomeEffectWorker_Bestowing.Apply` loops
   `ChangePsylinkLevel` to `GetMaxPsylinkLevelByTitle` [V]. No earlier draft recorded this, and it
   was harmless only while the ceremony was suppressed.
4. **"Never give a Church title the `EmpireTitle` tag" is inverted** — they are the same titles now.
5. **VFE Empire's count, restated on a named basis:** 138 sites in 58 files for `OfEmpire` + `FactionDefOf.Empire`; #53's 136 in 57 is `OfEmpire` alone. Both reproduce [V]; neither is an error.
6. **The imperial-ceremony hazard is gone, not fixed.** The chokepoint analysis stands:
   `OnFavorChanged` calls the generator directly [V]. It now describes the Church's own rite.
7. **Carried from #53 and still true:** **T-28** is `favorCost > 0` with four silent no-ops. The
   honour scale is vanilla `favor`, not VFE Empire `Honor`. The readout is vanilla's character card.
   `MostSeniorTitle` does not drive the displayed name.

### Exaltation — hostility and the techprint supply, measured against vanilla

**A [V] finding that narrows decision 21; it does not answer it.** What it establishes is that the
in-place Church reproduces **vanilla's own behaviour exactly**, so decision 21 is only a *loss*
under one specific condition, stated at the end.

**13 Empire-locked projects in vanilla + Royalty — 12 Empire-only.** `BrainWiring`,
`SpecializedLimbs`, `CompactWeaponry`, `VenomSynthesis`, `ArtificialMetabolism`,
`NeuralComputation`, `SkinHardening`, `HealingFactors`, `FleshShaping`, `MolecularAnalysis`,
`CircadianInfluence`, `CataphractArmor`, `JumpPack`; `JumpPack` also carries the Outlander tag.
The tag is declared **once**, on abstract `BaseBodyPartEmpire_TierA`, and inherited. **Counted two
independent ways** [V]: an inheritance-resolved lxml parse filtering on `isinstance(e.tag, str)`,
and a `grep` block count over `ResearchProjects_Implants.xml` — 13 defs, 2 abstract, 11 concrete,
plus `CataphractArmor` and `JumpPack`. (A parse without the `isinstance` filter counts XML comments
as defaults-bearing records; see `docs/agents/capability-research.md` § *Known tooling hazards*.)

**What hostility closes** [V]:

- **All Empire trade** — settlement, caravan and orbital. `FactionUtility.CanTradeWith` rejects on
  `faction.HostileTo` **before** it reaches the permit check;
  `IncidentWorker_TraderCaravanArrival.TryExecuteWorker` returns false while hostile;
  `TraderKindCommonality` is 0 with no permit holder. The permits themselves are **Knight** for
  `TradeSettlement` and `TradeCaravan`, **Baron** for `TradeOrbital`.
- **Empire quest rewards.** `Reward_Items.InitFromValue` sets `makingFaction = parms.giverFaction`,
  and `QuestNode_GetFaction` rejects a hostile faction unless `allowEnemy` is set — which Royalty's
  Empire scripts do not set (per-script coverage **[I]**).

**What hostility does *not* close** [V]:

- **Orbital trade ships** — a null `makingFaction` skips the tag test entirely (**T-99**). Gated on
  `TradersGuild` with Odyssey, so era-gated and unsteerable, but open.
- **Map-generation loot** — `MapGen_AncientTempleContents`,
  `MapGen_AncientComplexRoomLoot_Default`.
- **Asker-less quest rewards** — same null-faction bypass.
- **Books are never a route**, hostile or not: `ReadingOutcomeDoerGainResearch.IsValid` returns
  false when `project.TechprintCount == 0`, and `CanStartNow` requires `TechprintRequirementMet`.

**And the loss is recoverable in vanilla, which is the part decision 21 turns on** [V]:

- The Empire is **not** `permanentEnemy`, and its `permanentEnemyToEveryoneExcept` lists
  `PlayerColony` and `PlayerTribe`, so `CanChangeGoodwillFor` passes. Hostile at **≤ −75**, neutral
  again at **≥ 0**.
- **Natural drift alone stalls** at natural − 50 (`CheckReachNaturalGoodwill`), so drift never
  reopens trade by itself.
- **Gifts do.** `CanOfferGiftsTo` *requires* hostility; `Settlement_TraderTracker.CanTradeNow` has
  **no** hostility gate and **no** permit gate; the rate is ~40 silver per goodwill point, +25 %
  amplified.
- **Peace talks admit the Empire** — `allowEnemy true`; success **+60~70**, triumph **+100~110**.
- **Titles and permits are not stripped.** There is no royalty reference in
  `Notify_RelationKindChanged` or in `Pawn_RoyaltyTracker`'s relation handling, so the moment
  goodwill reaches neutral the Knight/Baron trade route reopens with the same pawns.
- **Already-applied techprints persist.** `ResearchManager`'s applied count is not faction state.
  **This is supply closure, not confiscation.**

**Therefore:** the in-place Church reproduces vanilla's behaviour exactly, and **decision 21 is
live — i.e. strictly worse than vanilla — only if Reverence-driven hostility is made one-way**:
goodwill pinned so gifts and peace talks cannot move it, or the Church marked `permanentEnemy`.
Restated in those terms under *Outstanding decisions* 21.

### Reverence — there is no donor for the measure itself

Re-verified against `Assembly-CSharp.dll` at
`common/RimWorld/RimWorldWin64_Data/Managed/`. Vanilla stores faction↔ideo as **set
membership, never a weight** [V]:

- `RimWorld.FactionIdeosTracker` holds exactly `Ideo primaryIdeo` and `List<Ideo> ideosMinor`,
  scribed as a reference and a reference-collection. No count, weight or percentage attaches to
  membership.
- `FactionIdeosTracker.RecalculateIdeosBasedOnPlayerPawns` builds a `Dictionary<Ideo,int>` of
  believers, but it is a `private static` scratch field, cleared at the end of the method, never
  scribed, and it runs only for the player faction.
- `Ideo.colonistBelieverCountCached` counts the player's own colonists only and is absent from
  `Ideo.ExposeData` — a session cache.
- `Pawn_IdeoTracker.Certainty` is per-pawn and nothing sums or averages it across a faction.
- `IdeoDevelopmentTracker` persists `points` / `reformCount`, scoped to the ideoligion and
  measuring reform progress.
- `Faction.ExposeData`'s only per-other-faction persisted structure is `relations`
  (`List<FactionRelation>`). **There is no ideo analogue of `relations`.**

Across the corpus, likewise nothing. The wide pass ran over both roots — all 155 mods, active
and inactive — searching `.cs`, `.xml` and every `.dll` in ASCII and again in UTF-16LE, and was
extended for #98 with a fresh vocabulary (`Fealty`, `Worship`, `Congregation`, `Missionary`,
`Evangel`, `Creed`, `Sanctity`, `Faithful`) that returned room roles and meme names only.

### What vanilla does ship, and what each piece is for

| Mechanism | What it gives Reverence | Evidence |
|---|---|---|
| `Faction.Notify_MemberExitedMap(Pawn, bool freed)` | the apostle hook — home faction, pawn, and released-vs-departed, before guest state is cleared | [V] |
| `Pawn.ExitMap` | the single funnel every departure passes through | [V] |
| `Pawn_IdeoTracker.SetIdeo` / `IdeoConversionAttempt` | the conversion funnel, if a conversion-time credit is ever wanted; records `ChangedIdeo` / `ConvertedNewMember` with a `Doer` and no faction | [V] |
| `QuestNode_ChangeFactionGoodwill` → `QuestPart_FactionGoodwillChange` | the template for a quest-authored per-faction write | [V] |
| `HistoryEventsManager` | a persisted `Dictionary<Faction, …>` with `LookMode.Reference` keys — vanilla's own precedent for the storage shape | [V] |
| `PreceptComp_DevelopmentPoints` | the XML `eventDef` + `points` pattern, dispatched from `IdeoUtility.Notify_HistoryEvent` | [V] |
| `Faction.CheckReachNaturalGoodwill` | the deadband / timer / capped-step decay shape, with `naturalGoodwillTimer` scribed on the faction | [V] |
| `DiaOption.Disable(reason)` | the visible gate | [V] |
| `FactionUIUtility.DrawFactionRow` | the in-game faction row, with free space in the goodwill column | [V] |
| `World.ExposeComponents` → `FillComponents()` | mid-campaign component backfill | [V] |

**`HistoryEventsManager` is not a Reverence store, and the reason matters.** It keeps
timestamps, not a scalar, and `CheckRemoveOldEvents` prunes each faction's record set to at most
20 entries every 10,000 ticks on a recency×magnitude score [V]. It is a *ledger of recent
events*, deliberately lossy. It is an excellent precedent for the persistence shape and a bad
place to keep a number that must survive a months-long save.

### Mod donors

- **VFED `VisibilityLevelDef`** — `Def` with `IntRange visibilityRange` and a polymorphic
  `List<VisibilityEffect> specialEffects` resolved in `PostLoad`. The band ladder, XML-driven
  [V].
- **VFED `QuestPart_ChangeVisibility` and `Reward_Visibility : Reward`** — an invented meter as a
  first-class quest reward [V].
- **VFED `Letter_VisibilityChange : ChoiceLetter`**, sent from
  `Utilities.ChangeVisibility` → `Notify_VisibilityChanged` — the band-crossing announcement [V].
- **VFED `WorldComponent_Deserters : WorldComponent, ICommunicable`** with
  `Dialog_NodeTreeWithFactionInfoAndVisibility` — a global meter reached from the comms console
  [V]. Its `WorldComponentTick` reading a `ModSettings` slider is the T-18 defect to reject [V].
- **VEF `WorldComponent_FactionGoodwillImpactManager`** — a persisted, tick-driven delayed-effect
  queue with letters [V]. Not needed for Reverence, which applies immediately, but it is the
  shape if a delay is ever wanted.

### Three corrections to inherited claims

1. **`WorldFactionsUIUtility` is the wrong utility, and `docs/specs/RELIGION.md` previously
   pointed the display work at it.** `RimWorld.Planet.WorldFactionsUIUtility` is the
   **world-creation faction-selection screen** — it takes a `List<FactionDef>`, offers Add and
   Delete buttons, caps at 12 factions and warns about disabled content [V]. The in-game faction
   row is `RimWorld.FactionUIUtility.DrawFactionRow`. VEF's three patches
   (`…_CanAddFaction_Patch`, `…_DoRow_Patch`, `…_DoWindowContents_Patch`) are all on the
   world-creation screen [V], so the earlier claim that "VEF demonstrates the faction row is
   patchable" was true of a screen that exists only before a game does.
2. **A `GoodwillSituationDef` is a coupling mechanism, not a display one.** The earlier draft
   proposed it as the way to show Reverence "without touching goodwill maths." It is the
   opposite: `FactionUIUtility.GetNaturalGoodwillExplanation` lists only situations whose
   `naturalGoodwillOffset != 0`, and `GetOngoingEvents` only those whose `maxGoodwill < 100`
   [V]. A `GoodwillSituationWorker_Reverence` is visible **exactly when, and only when, it moves
   goodwill** — which is the coupling
   [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97) has not ruled on. It stays on
   the table as the implementation of that coupling if #97 says yes, and it is not the answer to
   requirement 5.
3. **"The UI is a separate ticket" now names one.** It is
   [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61), *The political and campaign UI
   surfaces*, and it exists.

Re-derived and confirmed correct: the vanilla ideology negatives above; `WorldComponent`
construction and the `FillComponents` backfill; the `VisibilityLevelDef` band pattern; VFED's
`ModSettings`-in-tick defect; Empire Honor being a per-pawn collection of discrete achievement
objects with no running total and no decay, and Deserters Visibility being a single global
`int`.

### The commitment — the donor is the Ideology DLC, and Multiplayer proves it works mid-game

| Mechanism | What it gives the commitment | Evidence |
|---|---|---|
| `Pawn_IdeoTracker.SetIdeo(Ideo)` | public; accepts **any** `Ideo` with no `IdeoManager` membership check of its own (registration is the caller's job) and one early-return, on babies; handles beds, bonds, thoughts, needs, apparel, abilities and the `ChangedIdeo` history event | [V] |
| `FactionIdeosTracker.RecalculateIdeosBasedOnPlayerPawns` | promotes the player faction's primary from live free-colonist counts, on every member gain/loss and every colonist ideo change, with a vanilla letter | [V] |
| `FactionIdeosTracker.Notify_ColonistChangedIdeo` / `Notify_MemberGainedOrLost` | the two entry points; the latter early-returns unless `faction.IsPlayer` | [V] |
| `FactionDef.fixedIdeo` + `ideoName` + `forcedMemes` + `requiredMemes` + `deityPresets` + `styles` → `FactionGenerator.CreateFactionAndAddToManager` → `IdeoGenerator.MakeFixedIdeo` | the Church's authored doctrine, pure XML, NPC-only and therefore ours to use | [V] |
| `InteractionWorker_ConvertIdeoAttempt` | proves a colonist holding an NPC faction's `Ideo` is an ordinary vanilla state (`NPC_Free → Colonist` weight 0.5) | [V] |
| `Precept_Role.Assign(Pawn, bool)` / `Unassign` / `RequirementsMet` / `ValidatePawn` | seating a pawn in a role, with vanilla's own message, sound and side effects; `leaderRole` also sets `Faction.OfPlayer.leader` | [V] |
| `RimWorld.RoleRequirement` — abstract, one `Met(Pawn, Precept_Role)` override, XML-selected per role | founder-only eligibility as data plus ten lines | [V] |
| `RitualOutcomeEffectWorker_RoleChange` | the shipped shape for "a rite seats a pawn in a role": compose the outcome letter, then `Unassign`/`Assign` on a good result | [V] |
| `Precept_Ritual.ShowRitualBeginWindow`, registered in `Multiplayer.Client.SyncMethods` | the only player-initiated act, already synced | [V] |
| `IdeoDevelopmentUtility.ApplyChangesToIdeo(Ideo, Ideo)` — public static, in-place, no `Fluid` check, already MP-synced with `.ExposeParameter(1)` | the alternative build (§6): wholesale doctrine replacement preserving the `Ideo` instance and every reference to it | [V] |
| `Multiplayer.Client.Factions.FactionCreator.CreateFaction` | the shipped proof that `GenerateIdeo` → `IdeoManager.Add` → `SetPrimary` → `SetIdeo` runs correctly **mid-game inside a synced command** | [V] |
| `VanillaMemesExpanded.RoleRequirement_BestCrafter` and four siblings | the shipped 1.6 precedent that a custom `RoleRequirement` works | [V] |

**What does not exist, and where it shaped the build:**

- **No lock on a role.** Nothing in vanilla pins a pawn to a `Precept_Role`; `Assign` is a free
  UI action. Hence the eligibility-narrowing approach in §4B rather than a refusal patch.
- **No primary-ideo exemption for role activation.** `Ideo.ObligationsActive` has one and
  `Precept_RoleSingle.RecacheActivity` does not [V]. Hence our own `PreceptDef`s rather than
  vanilla's.
- **No public installer.** `Page_ChooseIdeoPreset.AssignIdeoToPlayer` — the three lines that set
  the primary, clear every other `Ideo.initialPlayerIdeo` and add to the manager — is `private`
  [V]. Trivially reimplemented; recorded because it looks callable.
- **Nothing in the corpus carries a mid-game commitment mechanism**, and nothing needs to. A wide
  pass over both roots plus `common/RimWorld/Data/`, ASCII and null-interleaved UTF-16,
  `-g '*.dll' -g '!**/obj/**'`, returned: `SetIdeo` → VFE Medieval 2 only; `RoleRequirement_` →
  VIE Memes and Structures only; `Precept_RoleSingle` → VIE M&S and RimPacts; `ApplyChangesToIdeo`
  → Multiplayer only; `Precept_RoleMulti`, `ChosenPawnValue` and `Dialog_ReformIdeo` → nothing.
  The sweep was validated first: `ApplyChangesToIdeo` returns zero ASCII hits and hits
  `Multiplayer.dll` in UTF-16, the correct signature for a name existing only as a
  `SyncMethod.Register` string literal. **The `--encoding utf-16le` form
  ([#103](https://github.com/cjd721/Rimworld-Archinity/issues/103)) was not used.**
### Institutions — nothing carries it, and the near misses each miss differently

**The corpus negative, stated with its construction.** Both roots plus vanilla and the DLC, `.cs`,
`.xml` and every `.dll` with `-a` and `-g '!**/obj/**'` (the five vendored publicised
`Assembly-CSharp.dll` copies under `Source/obj/**` were excluded from every pass and **no `obj/`
path appears in any result set** — verified, not assumed). Each vocabulary swept twice: ASCII, then
a **hand-typed null-interleaved literal** for the `#US` heap — never `--encoding utf-16le`
([#103](https://github.com/cjd721/Rimworld-Archinity/issues/103)), and never through `$(…)` or a
generated pattern file, which strips the NULs and degrades the sweep to ASCII in silence. Validated
against `GoodwillSituationWorker` and `TryAffectGoodwillWith` before any negative was trusted.

| Vocabulary | Result |
|---|---|
| `Embassy`, `ChapterHouse`, `Diocese`, `Chapel` | **zero** — corpus-wide, across `.cs`, `.xml` and both assembly heaps |
| `Monaster`, `Congregation`, `Persecut` | **zero in the assembly heaps**, which is the claim that matters. ⚠ **Not zero corpus-wide** — an earlier draft said "both heaps" under a heading claiming a `.cs`/`.xml`/`.dll` pass, which overstated its own evidence. They hit vanilla backstory and meme **XML**, Sepulchral Reliquary, VFED's `PlotMission.xml` and a cultists mod. **None is an institution**, so the negative survives; the sentence did not |
| `Missionar` | RimPacts only, in both heaps |
| `Church`, `Shrine`, `Institution`, `Suppression` | vanilla Ideology's `Need_Suppression`, `VPE_Shrineshield_*`, `NatureShrine_*` — decoration and abilities, no institution |
| `Temple`, `Estate`, `Holding`, `Gated` | `AncientTemple` genstep, Anomaly's `Building_HoldingPlatform`, Rim War's transient `AttemptDiplomatMission`, vanilla's `Mission_BanditCamp` quest |
| `Outpost` | VEF `Outposts.dll`, VOE, VFE Classical, Mining Outpost, Faction Territories |

#### Vanilla Outposts Expanded — the framework is real and it is on the wrong tiles

The state machinery is **not** in VOE: it is `Outposts.Outpost : MapParent, IRenameable` in VEF's
`Outposts.dll`, holding `List<Pawn> occupants`, `List<Thing> containedItems`,
`ticksTillProduction`, `ticksTillPacked`, `costPaid`, `raidFaction`, `raidPoints`, `deliveryMap`
and a name, all scribed, with behaviour driven by an `OutpostExtension` on the `WorldObjectDef`
[V]. VOE ships only the subclasses and defs.

**It cannot be planted inside an NPC faction, by construction.**
`Outposts.Utils.CanSpawnOnWithExt` rejects the placement outright when
`Find.WorldObjects.AnySettlementBaseAtOrAdjacent(tile)`, and `Dialog_CreateCamp` calls
`outpost.SetFaction(creator.Faction)` — the creating caravan's, i.e. the player's [V]. No goodwill
cost, no standing gate, no host faction, no suppression path. It is a player colony annex on an
empty tile, and it is also a `MapParent`, which [#10](https://github.com/cjd721/Rimworld-Archinity/issues/10)
already priced. **Not a donor.**

#### VFE Empire's vassal — the right *decoration* pattern, no adversary

`VFEEmpire.TitheInfo : IExposable` carries `TitheTypeDef Type`, `Pawn Lord`,
`Settlement Settlement`, a setting, a speed and `DaysSinceDelivery`; `WorldComponent_Vassals`
holds `Dictionary<Settlement, TitheInfo>` scribed Reference→Deep, and
`AllPossibleVassals` lazily mints a record per existing Empire settlement [V]. **The object is an
existing NPC settlement, decorated — never a new world object the player builds**, which is a
genuinely useful precedent for §6's comp-as-adapter.

Three reasons it is not the donor [V]: the currency is a derived vassalage-point budget summed
over the pawn's title chain, not a spend; **nothing can suppress, raid, contest or reduce a
vassal** — the only removal paths are the lord losing standing and a debug action, so the
requirement's entire third clause has no precedent here; and `WorldComponent_Vassals.DoDay()`
writes directly from a tick and a UI callback with no Multiplayer sync anywhere in the assembly.

#### Faction Territories — the closest structural precedent in the corpus

`jaeger972.factionterritories`, `Assemblies/FactionTerritories.dll`, no source, decompiled [V]. It
is the only thing in 155 mods with the whole shape, and it is worth reading before building:

- **Gate and price on one axis.** `VassaliseUtility.GetSettlementVassaliseGoodwillCost()` clamps a
  configured cost to 10–100; the check is `if (faction.PlayerGoodwill < cost)` producing a
  *"Requires N goodwill with …"* reason, guarded by `Faction.CanChangeGoodwillFor`; execution then
  spends it through `TryAffectGoodwillWith(Faction.OfPlayer, -cost, …)` **with a `+cost` rollback
  on failure**. The rollback is the detail worth copying.
- **The planted object.** `FactionTerritories_VassalOutpost : WorldObject` — a plain `WorldObject`,
  not a `MapParent` — placed by `VassaliseUtility.ExecuteVassalisationAtTile` **at the NPC
  settlement's own tile** and given `SetFaction(Faction.OfPlayer)`, retaining `originalFactionId`,
  `originalFactionLoadID`, `originalSettlementName` and `originalWorldObjectDefName` so the host
  identity survives on the object.
- **The ongoing effect.** `VassalagePointsComponent : GameComponent` accrues per-faction points on
  `GameComponentTick` and spends them on silver tribute, purchased pawns and trade sellables.
- **A real suppression loop.** `FactionTerritories.Invasions.Component` scans `GetAllOutposts()`,
  calls `Utility.FindEligibleAttackers(outpost)` and `TryCreateForVassalOutpost(...)` to spawn an
  `Invasion` against it, and the outpost can be destroyed.

**Two reasons it is a precedent and not a donor.** It **converts** an existing NPC settlement, or a
destroyed one, rather than planting an institution beside a living base — so the placement half
would have to be built anyway; and ⚠ its cost is a `ModSettings` slider, **T-18**, which is the one
thing not to copy. It is also already recorded as a `DrawFactionRow` patcher claiming the row's
right-edge 80px (*The build — Reverence* D1), so it is a known collision surface either way.

#### RimPacts' missionary — the pricing half without the persistence half

`RimPacts.RptTuning` carries `MissionaryCost`, `MissionaryCooldownDays`, `MissionaryBaseChance`,
`MissionarySuccessGoodwill`, `MissionaryFailGoodwill`, `MissionaryFavorBonus` and
`MissionaryTechPenalty` [V on the symbols, [I] on the numbers, which come from the mod's own docs].
Mechanically it sends the moral guide away for seven days at a silver cost for a roll to convert
the faction's ideoligion, moving goodwill either way. **It is a timed operation with a price and an
outcome — there is no persistent object and no decay offset**, so it is the *transaction* half of
this capability and none of the *institution* half. The mod itself is already rejected on
[`POLITICS.md`](POLITICS.md)'s grounds.

#### What vanilla ships that this build stands on

| Mechanism | What it gives institutions | Evidence |
|---|---|---|
| `Faction.Notify_RelationKindChanged` | the suppression trigger, **plus two shipped routines of exactly the right shape** — `TradeRequestComp.Disable()` on the hostile edge, and the `LetterLabelSiteNoLongerHostile{,Multi}` bulleted letter with `LookTargets` on the friendly edge | [V] |
| `FactionDialogMaker` | the founding surface, its gate idiom and its *"(cost: N goodwill)"* label formatting | [V] |
| `Multiplayer.Client.NodeTreeDialogSync` / `PersistentDialog.Click` | the founding click as a synced command, free | [V] |
| `Faction.TryAffectGoodwillWith` | the price, with a `bool` that must be checked | [V] |
| `WorldObjectDef Settlement`'s `<comps>` + `WorldObject.ExposeData` → `InitializeComps()` | the optional world-map presence, **with mid-save backfill for free** | [V] |
| `Settlement.GetInspectString`'s `RequiresTradePermission` line | the register a world-map institution line belongs in | [V] |
| `WorldComponent_Reverence`'s per-faction record | the store, already built | [V], [#98](https://github.com/cjd721/Rimworld-Archinity/issues/98) |


## Verification

### Exaltation

READ-class throughout. Anchors are `Type.Member` for decompiled code and file paths for defs; no
line numbers.

**The techprint inventory — preserved while the Church is non-hostile and a colonist holds Knight;
not unconditionally.**
`Verse.ResearchProjectDef.heldByFactionCategoryTags` is matched against `faction.def.categoryTag` in
`TechprintUtility.GetResearchProjectsNeedingTechprintsNow` alone, and that method tests **no tech
level** [V]. Re-counted this pass over vanilla and the 1.6 mod folders [V]:

| Source | Projects | Also held by |
|---|---|---|
| Royalty implants — tag declared once on `BaseBodyPartEmpire_TierA`, inherited by `_TierB`; 11 concrete children | `BrainWiring`, `SpecializedLimbs`, `CompactWeaponry`, `VenomSynthesis`, `ArtificialMetabolism`, `NeuralComputation`, `SkinHardening`, `HealingFactors`, `FleshShaping`, `MolecularAnalysis`, `CircadianInfluence` (names [I], from #53) | — |
| Royalty apparel | `CataphractArmor`, `JumpPack` | `JumpPack` also Outlander [I] |
| VFE Deserters `3025493377` | `VFED_ImperialDefenses`, `VFED_ImperialWarSolutions` | — |
| GravTech `3545374124` | `GravEngineBuild`, `GravForge`, `BlackHole_GT` | TradersGuild [I] |

**18 projects, 14 Empire-only.** The tag-gated routes keep working, **conditionally**:

- **Church trader stock** (`StockGenerator_Techprints.GenerateThings` [V]) — needs a colonist holding
  the permit: **Knight** for settlement and caravan trade, **Baron** for the orbital trader (§5). No
  Knight, no caravan (`IncidentWorker_TraderCaravanArrival` commonality 0) and no trade command
  (`CaravanVisitUtility`) [V].
- **Church quest rewards** (`ThingSetMaker_Techprints` via `parms.makingFaction` [V]) — Church quests
  presumably stop while it is hostile [I].
- **Once §6 makes the Church hostile**, `FactionUtility.CanTradeWith` rejects it and
  `IncidentWorker_TraderCaravanArrival` refuses to execute [V], so **the trader route closes for all
  14** — by this build's own worker.

**What survives hostility** [V unless marked]:

- the **null-faction map-gen lottery** (four `MapGen_*` setmakers) — unsteerable;
- **orbital traders, whose stock is generated without a faction** (**T-99**): `Orbital_Exotic` and
  `Orbital_CombatSupplier` carry `StockGenerator_Techprints`; `TradeShip.GenerateThings` builds
  `ThingSetMakerParams` with no `makingFaction`, `ThingSetMaker_TraderStock` forwards that null, and the
  tag test is skipped for a null faction — so any Empire-only techprint can appear in their stock.
  **Their arrival is the Traders Guild's, not the Church's.** Both declare
  `<faction MayRequire="Ludeon.RimWorld.Odyssey">TradersGuild</faction>`
  (`Core/Defs/TraderKindDefs/TraderKinds_Orbital_Misc.xml`), and
  `IncidentWorker_OrbitalTraderArrival.CanSpawn` passes a trader with no faction unconditionally but,
  for one naming a faction, requires that faction to exist and a free colonist to pass `CanTradeWith`
  against it [V]. Needs a comms console and orbital beacon, i.e. it is era-gated; its draw is weighted,
  not steerable; and it is gone for the campaign if [`ORBIT.md`](ORBIT.md) zeroes the guild's worldgen
  count;
- **if VFE Deserters ships**: `VFED.QuestNode_BetrayalRewards` draws
  `TechprintUtility.TryGetTechprintDefToGenerate_NewTemp` with the slate's `"empire"` faction —
  tag-based, not hostility-gated [V; quest reachability [I]] — and `VFED.GenStep_FlagshipRuins`
  places every project whose tags contain `FactionDefOf.Empire.categoryTag` [V]. **VFED is the
  hostile-branch carrier.**

**No techprint requirement is removed, but without VFED the steerable supply ends when the Church
turns hostile** — § *Outstanding decisions* 21, owed to Conrad by the reopen's "no silent loss" clause. Whether
Spacer and Ultra implant techprints should come *from the Church at all* is a progression question
([`docs/progression/`](../progression/)), not a loss.

**What still needs a stub or the game.** Nothing to settle the mechanism.

- **STUB** — `tools/patch_check.py` over the Church patch set, active-set merge, so the result is
  "matches in one configuration":
  - `permanentEnemyToEveryoneExcept` still carries every mod's appended entries after our patches;
  - the Replace on `allowedMemes` lands after Vanilla Ideology Expanded — Memes and Structures;
  - every Church `RoyalTitleDef` has `favorCost > 0` or is NPC-only;
  - `maxPsylinkLevel` reads 0 on all seven;
  - `pawnGroupMakers` ordering against Vanilla Psycasts Expanded's replace;
  - no Church patch renames a `spawnCategories` value.
- **STUB** — on a dev quickstart with WTL enabled at Neolithic and **VFE Empire absent**:
  - the Church is in the roster;
  - `TechprintUtility.TechprintsFromFactions` names it for all 18 projects;
  - a Keyed override of `CommandCallRoyalAidNotEnoughFavor` is what the gizmo prints.
- **RUN** — one colonist crosses a rung through a quest reward. Observe:
  - the Church bestowing quest appears;
  - the ceremony confers the title;
  - **no psylink level is gained** — with Vanilla Psycasts Expanded loaded as well, since its
    `ApplyTitlePsylink` grants one base level when the pawn has no psycast hediff;
  - the Permits tab opens on the Church.
- **RUN** — force Global Reverence past the cap threshold and advance to the next 1,000-tick
  boundary. The Church turns hostile with vanilla's letter, and the faction row lists the suspicion
  situation.
- **RUN** on [#16](https://github.com/cjd721/Rimworld-Archinity/issues/16)'s two-client regime: the
  ceremony's title and the hostility flip land on the same tick on both clients.
- **RUN** — a client **joins mid-window**, after a Reverence change and before the next 1,000-tick
  boundary; `Faction.OfEmpire.GoodwillWith(Faction.OfPlayer)` matches on host and joiner. Run it
  once without and once with the `RecalculateAll`-on-write fix.
- **RUN** — Church hostile, no VFED: confirm no Church caravan arrives and that `Orbital_Exotic` can
  still stock an Empire-only techprint.

**Residual gaps, stated.**

- The `OfEmpire` metadata hits in the 12 mods beyond VFE Empire and VFE Deserters were not
  decompiled. Among them are Medieval Overhaul, Vanilla Psycasts Expanded and RimPacts. The claim that they resolve the Church unchanged rests on
  them using the singleton rather than a label, and is [I].
- Generic-instantiation and runtime-concatenated lookups are invisible to both sweep forms.

### Reverence

READ-class throughout, from decompiled 1.6 assemblies at the pinned versions. The negative was
justified by a wide pass over both corpus roots — the workshop root **and**
`common/RimWorld/Mods` — in ASCII and UTF-16LE, and the sweep was validated against a known hit
(`GoodwillSituationWorker`, 13 files) before its negatives were trusted.
⚠ **That pass used the same unsound `rg -a --encoding utf-16le` form**
([#103](https://github.com/cjd721/Rimworld-Archinity/issues/103)), and unlike Exaltation's it has
**not** been re-checked: `GoodwillSituationWorker` is ASCII-visible, so the control does not
demonstrate that the wide leg was working. The Reverence negatives are therefore weaker than they
read, and a re-sweep with the null-interleaved form is owed before this one is relied on again.

**Two residual gaps, stated:**

- A `Dictionary<Faction, float>` inside a generically named component is invisible to text
  search: generic instantiations live in the `#Blob` heap as signatures, not readable strings.
  Bounded by enumerating every assembly referencing `FactionIdeosTracker` and checking each.
  Closing it fully needs a Mono.Cecil metadata scan listing fields whose type signature mentions
  `Faction` — worth building as a `tools/` mode, since the same question recurs across
  [#53](https://github.com/cjd721/Rimworld-Archinity/issues/53)–[#56](https://github.com/cjd721/Rimworld-Archinity/issues/56).
- The claim that the apostle hook fires for every departure shape the requirement names is [V]
  on the code path and untested in play. The cheapest confirmation is a **STUB**-class one: a
  logging postfix on `Notify_MemberExitedMap`, one visitor group and one released prisoner, and
  a check that both arrive with the expected `freed` value.

**What still needs the game:** nothing to settle the mechanism. The multiplayer claims about the
apostle hook belong to the two-client regime on
[#16](https://github.com/cjd721/Rimworld-Archinity/issues/16), as one observation: that a guest
departing produces the same Reverence delta on both clients on the same tick.

### The commitment

READ-class throughout, from decompiled 1.6 assemblies and the Ideology DLC's shipped XML at
the pinned versions. The headline is a **positive**, so by
`docs/agents/capability-research.md`'s asymmetry the wide pass was owed only for the two
negative sub-claims — that nothing locks a pawn into a role, and that no mod carries a
commitment mechanism — and it was run in both encodings and validated against a control
before either negative was trusted (*Available mechanisms*).

**What still needs the game: one observation, and it is narrow.** It belongs to the two-client
regime on [#16](https://github.com/cjd721/Rimworld-Archinity/issues/16):

> The commitment rite completing produces the **same** `Faction.OfPlayer.ideos.PrimaryIdeo`,
> the same seated role-holders and the same `LetterLabelNewPrimaryIdeo` on both clients on the
> same tick.

That is the one place `SetIdeo`'s `Rand` draw could diverge — if the rite's participant set
were ever resolved client-side rather than from the `LordJob_Ritual`'s assignments.

A cheaper **STUB**-class confirmation of §4A is available first and does not need two clients:
ship the two founder `PreceptDef`s — the leader on `PreceptRoleSingleBase`, the preacher on
`Precept_RoleMulti` — with `activationBelieverCount: 1`, start a two-colonist game, and check
that the preacher role is assignable. With vanilla's value it will not be, and nothing will say
why. **The same check closes §4A's one open [I]**: whether `Precept_RoleMulti` gates activation
on the same field names as `Precept_RoleSingle`. If the `RoleMulti` def ignores
`activationBelieverCount`, the role activates regardless and the check passes for the wrong
reason — so read the class, or assert the field is present on the loaded def, rather than
inferring it from the role appearing.

**Residual gap, stated:** a mod expressing a commitment as a chain of existing def types — a
`QuestScriptDef` chain reaching `SetIdeo` through a generically named quest part — would be
invisible to a name sweep. Bounded but not excluded; it would not be a better donor than
`Pawn_IdeoTracker.SetIdeo` itself.
### Institutions

READ-class throughout, from decompiled 1.6 assemblies at the pinned versions. Every mechanism claim
is cited by `Type.Method`. The ticket's named donor was read from the **1.6** `VFEEmpire.dll` and
not from its 1.4 `Source/` tree, which is where the ticket's own line count came from (*Status*).

**Two things that would raise confidence, and neither is a RUN:**

- A **STUB**-class check that a `PatchOperationAdd` onto `WorldObjectDef Settlement`'s `<comps>`
  reaches every settlement — `python tools/xpath.py '/Defs/WorldObjectDef[defName="Settlement"]/comps'`
  gives the red-green number before the patch is written (`CODING_STANDARDS.md` § *The red–green
  loop for def work*). Only needed if §6 is taken. Both tools merge the **active** set, so the
  verdict is "matches in one configuration."
- A logging postfix on `Faction.Notify_RelationKindChanged`, one faction driven across the −75
  threshold, confirming the hostile edge fires once with `__instance` as the faction whose relation
  changed and `other == Faction.OfPlayer`. Single-client, one session.

**What still needs the game: nothing to settle the mechanism.** One observation belongs to the
two-client regime on [#16](https://github.com/cjd721/Rimworld-Archinity/issues/16), and it is the
one multiplayer claim here that reading cannot close: **with the founding option present on both
clients, one founder clicking it produces the same institution, the same goodwill charge and the
same letter on both, on the same tick** — and, separately, that with the option *disabled* on both,
clicking the option below it activates the same action on both (the positional-index hazard,
[`POLITICS.md`](POLITICS.md) § *Persistence and multiplayer (the gate)*).

Observable checks that the requirement is satisfied: a faction below the Reverence threshold shows
the founding option greyed, naming the threshold and the current value; founding one deducts the
stated goodwill and the faction's Reverence stops sliding; that faction turning hostile produces a
letter naming the institutions and the slide resumes; the relation returning to neutral produces
the mirror letter and the slide stops again.

**Residual gap, stated:** a mod could express an institution as a `WorldObjectComp` or a `GameComponent`
field with an entirely generic name and a `Dictionary<Faction, …>` type signature, which lives in
the `#Blob` heap and is invisible to text search — the same bounded gap
[#98](https://github.com/cjd721/Rimworld-Archinity/issues/98) records for the Reverence store, and
closable by the same Mono.Cecil `tools/` mode it proposes. Given that the vocabulary sweep returned
a clean zero across seven institution words in both **assembly** heaps — and corpus-wide for four
of them, with the other three surviving only as unrelated XML prose — a hidden better donor is
unlikely.


## Outstanding decisions

### Reverence

1. **Is Reverence per (faction × ideo), or per faction against the player's current primary
   ideo?** If the player reforms a fluid ideo mid-campaign, the stored value either follows or
   resets. The one-key form is much cheaper. Owner:
   [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97).
2. **What happens to a faction's Reverence when the faction is removed or goes permanently
   hostile** — persist, zero, or drop. T-07 and the `FactionManager.toRemove` path make this a
   real load-time case. Owner: [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97).
   The build prunes, as the safe default.
3. **Whether Reverence modulates the Goodwill ripple.** Owner:
   [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97). If it does, correction 2 above
   names the mechanism.
4. **The numbers.** Decay rate and its deadband, band thresholds and their count, per-event
   amounts, and what "sincerely converted" means as a `Certainty` threshold. All are XML Def
   fields by construction, so the build does not wait on them — **but no open ticket owns them.**
   `docs/requirements/RELIGION.md` says only that they "still need design or tuning", and #97's
   scope is the coupling. **This is a gap, not a hand-off**, and it belongs on the map.
5. **The shape of the political surface** — one tab or several, and where it hangs. Owner:
   [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61). Until it rules, D1 and D2 above
   are the shipping display and they patch vanilla's own surfaces.

### Exaltation

**Most of these are fiction and requirements calls, not mechanisms.** Where an item names a ticket
that is *closed* ([#7](https://github.com/cjd721/Rimworld-Archinity/issues/7),
[#10](https://github.com/cjd721/Rimworld-Archinity/issues/10),
[#21](https://github.com/cjd721/Rimworld-Archinity/issues/21)), it is context, never the owner.

6. **Resolved: the Empire becomes the Church wholesale, in place, renaming nothing** (§1). Every
   Empire-tagged techprint route is kept by identifier; the trader route is conditional on
   non-hostility and a Knight (§ *Verification*, decision 21).
7. **The `seniority` bands, and how the godhood ladder interleaves. Gap, no owner.**
   `Pawn_RoyaltyTracker`'s aggregate accessors — `MostSeniorTitle`, `MainTitle()`, `HasTitle`, the
   throne and bedroom checks, `UpdateAvailableAbilities()`, `IssueDecree()` — span every ladder a pawn
   holds [V, #53]. `titles` holds one `RoyalTitle` per (pawn, faction), so if the tiers of godhood
   are `RoyalTitleDef`s they must sit on a faction **other than the Church**, or they overwrite the
   Church title silently [V, #53]. #21 is closed.
8. **The numbers and the catalogue. Gap, no owner.** Relabel vanilla's 7-rung ladder or re-cut it;
   `favorCost` per rung; the permit-point curve; which privileges each rung unlocks; which title
   unlocks trade — **default is vanilla's: Knight for settlement and caravan trade, Baron for orbital**
   [V]; the Exaltation-vs-Reverence split per mission. All XML.
9. **Whether ordinary colonists can hold Church titles, or only the founders.** Vanilla imposes no
   limit, and `Reward_RoyalFavor` lets a quest ask which colonist is exalted [V, #53]. It is a
   requirement that `docs/requirements/RELIGION.md` does not state.
10. **Safe passage and political privileges — what they do to the simulation.** There is no vanilla
    carrier (§5). Unpriced until the requirement says what they are. Gap, no owner.
11. **Suspicion — the curve, and whether it ratchets.** The build is §6; the thresholds are open
    parameters. If suspicion must not forgive a falling Global Reverence, the worker needs one
    scribed high-water mark. That is not a tolerance currency, but it *is* saved state, and the
    requirement's "no separate … threat currencies" should say whether it is allowed.
    [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97) (open) owns how Reverence touches
    Goodwill *per faction*, which is adjacent context. It does not own this *global* coupling. Gap.
17. **The Church's per-era presentation and first contact.** An Ultra-tech Church is contactable
    from the Neolithic, because Ignorance Is Bliss's `empireIsAlwaysEligible` defaults true [I]. The
    plot introduces it in Medieval. The band configuration is
    [#22](https://github.com/cjd721/Rimworld-Archinity/issues/22)'s (open). **Presenting it
    era-appropriately cannot use a `Faction.def` swap** (§ *Failure and recovery*); `techLevel`, pawn
    kinds and gear are the levers. #7 is closed, so the presentation half is a gap.
18. **Which Empire-fiction content the Church keeps.** None of it breaks, and all of it will appear
    unless cut:
    - the **Royal Ascent ending** — a `StorytellerCompProperties_RefiringUniqueQuest` on every vanilla
      storyteller, day 35, refiring every 22 days [V], which competes with the campaign's own ending;
    - shuttle arrivals — the bestower, the tribute collector, shuttle-crash rescues, lend-colonists;
    - landing pads and throne rooms in Church settlements (`GenStep_Settlement`);
    - Royalty's Empire intro quests;
    - VFE Empire's vassals and ceremonies, and VFE Deserters as the Schism
      ([#54](https://github.com/cjd721/Rimworld-Archinity/issues/54) context).

    A fiction call per item; gap, no owner.
19. **The Church's enemy roster.** It is currently a permanent enemy of everyone except 9 vanilla
    factions plus eleven mods' additions [V]. Glitterites and Free Companies are unwritable forever
    ([`POLITICS.md`](POLITICS.md) gate C). Whether a Medieval Church is born at war with every
    Medieval kingdom is fiction. The mechanism is `PatchOperationAdd`. Gap.
20. **Psylinks and Church clergy.** Zeroing `maxPsylinkLevel` is required by
    `docs/requirements/ALTAR.md` for the *founders*. It also strips `PawnGenerator`'s psylinks from
    generated Church nobles [V]. Whether the Church's own clergy cast is fiction, and whether *"early
    Church titles and early psychic states may share language"* wants any title-linked psychic
    effect is a requirement. Gap.

21. **Techprint supply after the Church turns hostile — owed to Conrad under "no silent loss", and
    now narrowed to one question.** §6 makes the Church hostile from Global Reverence, which closes
    the Church trader route for the 14 Empire-only projects (§ *Verification*); the route also needs
    a Knight while it is open. What survives is the map-gen lottery, the Traders Guild's orbital
    traders (era-gated, unsteerable, and dependent on the guild existing —
    [`ORBIT.md`](ORBIT.md)'s hide-versus-zero row) and — only if VFE Deserters ships — VFED's
    betrayal rewards and flagship ruins.

    **What narrows it:** all of that is *exactly what vanilla does* when the Empire turns hostile,
    and vanilla's closure is **recoverable** — gifts and peace talks both reopen it, titles and
    permits are never stripped, and applied techprints persist
    (§ *Available mechanisms* § *Exaltation — hostility and the techprint supply*, [V]).
    **So the decision is not "does hostility cost us techprints" but:**

    > **Is Reverence-driven hostility one-way?** If the suspicion worker merely pins goodwill low
    > while leaving gifts and peace talks live, the campaign is at vanilla parity and there is no
    > loss to accept. If it pins goodwill so nothing can move it, or the Church is marked
    > `permanentEnemy`, the supply closes **permanently** and that is strictly worse than vanilla.

    Only in the second case is the rest of this item live: accept the loss, require VFED, add a
    Schism or other supplier (for example `heldByFactionCategoryTags` matching a Schism faction's
    `categoryTag` — XML), or remove those techprint requirements deliberately. Gap, no owner.

### The commitment

12. **Is Devotion alignment reference equality on `Ideo`, or doctrinal equivalence?** This is
    the single question that chooses between §1's build and §6's alternative, and it changes
    nothing else. Owner: [#49](https://github.com/cjd721/Rimworld-Archinity/issues/49) — its
    body already claims *"what the founders' commitment to the Church must mean, what it must
    gate, and what it must never measure."* The build assumes reference equality, which is the
    cheaper and more literal reading of [`ENDING.md`](../plot/ENDING.md).
13. **Which predicate defines a founder. Still a gap — but the *carrier* is no longer one, and
    that was this document's own error.** The rule is unstated:
    `docs/requirements/RELIGION.md` says only *"the two founding pawns"*, and
    [#49](https://github.com/cjd721/Rimworld-Archinity/issues/49)'s scope is eligibility for the
    altar's rites, not identity. **No open ticket owns the predicate.** What *is* settled is
    where the answer is stored: [`TRANSCENDENCE.md`](TRANSCENDENCE.md) rule 1 makes
    `CompFounderRecord` on the `Archinity_FounderRecord` hediff the single store for founder
    state and forbids a second, and [`ALTAR.md`](ALTAR.md) already extends it. So
    `RoleRequirement_Founder` reads that comp (§4B); it does not need a `GeneDef` /
    `XenotypeDef` field of its own, and the build does not wait on the predicate either way.
    The altar assembly currently encodes founder-ness as genetics
    (`GenePool_Archite.xml`'s `<founderOnlyGenes>`), which is an implementation accident
    standing in for a requirement. **This is a pointer, not a claim on those specs** — neither
    is edited here.
14. **What Reverence measures after the commitment.** The player's primary ideology becomes the
    Church's, which the Church faction already follows completely. Owner:
    [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97) — it is the same question as
    that ticket's existing "per (faction × ideo), or per faction against the player's current
    primary", now with a concrete campaign event that forces it.
15. **Rerouted: player-faith role architecture.** The player faith needs one or two
    founder-specific seats, several preacher/converter seats for core disciples, at least one
    crafting specialist and campaign-time role unlocks. [#114](https://github.com/cjd721/Rimworld-Archinity/issues/114)
    owns multiple holders, custom specialist effects and progressive unlocking;
    [#116](https://github.com/cjd721/Rimworld-Archinity/issues/116) owns the later catalogue
    decision. §4's old two-seat build is superseded.
16. **Is the commitment reversible, and at what price?** Mechanically it is trivially
    reversible — a second rite calling `SetIdeo` back, or enough colonists converting away —
    and `Pawn_IdeoTracker.previousIdeos` already records the founder's prior ideologies [V].
    Whether the campaign *permits* it is a requirement, and neither
    `docs/requirements/RELIGION.md` nor [`ENDING.md`](../plot/ENDING.md) says. **Gap, no owner.**
    This is the same unowned-numbers gap as decisions 4 and 8 and probably belongs in the same
    ticket.

### Institutions

**Every open item here is a number, and that is deliberate.** Two entries in an earlier draft were
*mechanisms* wearing a number's clothes — whether the decay subtraction is clamped, and whether
suppression can reverse rather than merely remove sustain. Handing those back was wrong under
`docs/agents/capability-research.md` § *Requirements stay where they live*: **a missing mechanism
is the build's**. Both are now branches the build ships, with their defaults stated, and only their
values are open. Items 4 and 6 remain open questions rather than parameters, but each is priced
against a named donor, so neither blocks.

The build does not wait on any of these — all are Def fields by construction — but naming them is
the point.

1. **The prices and the thresholds.** What Reverence a tier requires, what Goodwill it costs, how
   many of each tier a faction may host. Same owner problem as *Reverence* item 4 above: no open
   ticket holds Reverence's values, and none holds these either.
   [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97)'s scope is the coupling.
   **Gap, no owner**, recorded rather than handed to a ticket that disclaims it.
2. **What `sustain` is worth per tier.** Purely a number. **The clamp question that used to sit
   here is no longer open**: the build sets `Max(0, step − sustain)` behind a global
   `bool allowNegativeDecay` defaulting to `false` (*The build* §3), so *"institutions preserve,
   they do not evangelise"* is the shipped default and flipping it is an ordinary XML call. Whether
   a branch exists at all was a mechanism and belonged in the build, not in this list.
3. **What `suppressedSustainFactor` should be, per tier.** Also purely a number. **The
   remove-versus-reverse question that used to sit here is no longer open either**: a suppressed
   institution contributes `sustain * suppressedSustainFactor`, defaulting to `0f` (*The build*
   §4), so the requirement's *"persecute apostles"* clause is **a negative value in that field**
   rather than a second mechanism. Setting it is balance.
4. **Whether an institution can be destroyed at all, and by what.** This build makes suppression
   reversible because the requirement's *"unless the player changes the political situation"*
   demands a route back (*The build* §4). Faction Territories' invasion loop shows the destructive
   alternative exists and is affordable. Nothing in `docs/requirements/RELIGION.md` says whether a
   long-hostile faction should eventually raze what the player built there.
5. **Whether the institution has a world-map presence.** §6 prices it at one XML patch and ~25
   lines and recommends the ledger-only form until something asks for it. The natural asker is
   [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61), which owns the shape of the
   political surface and is open.
6. **Whether founding is instant or takes time.** Every shipped analogue in the corpus is instant —
   a click, a charge, an object. The requirement is silent and the fiction may want a delay; VEF's
   `WorldComponent_FactionGoodwillImpactManager` is the shape if one is wanted (*The build —
   Reverence*, *Mod donors*), and it costs nothing extra because it already ships.
