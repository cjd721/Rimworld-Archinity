# Religion

## Purpose and scope

How the religious systems in [`docs/requirements/RELIGION.md`](../requirements/RELIGION.md)
will be built. This document owns two behaviours end to end:

- **Reverence** — the number, the events that move it, the decay that pulls it back, the bands,
  and the surfaces the player reads it on.
- **Exaltation and the sacred titles** — the Church's rising scale, the thresholds that confer
  permanent titles by rite, and the privileges those titles unlock
  ([#53](https://github.com/cjd721/Rimworld-Archinity/issues/53)).
- **The founders' commitment to the Church** — whether the founders can genuinely adopt the
  Church's ideology mid-run, what seats them in that ideology's defining roles, and what the
  campaign stores so the act can be told apart from an accident
  ([#75](https://github.com/cjd721/Rimworld-Archinity/issues/75)).

It does not own **religious institutions inside foreign factions**
([#73](https://github.com/cjd721/Rimworld-Archinity/issues/73)); the interface those need is
named in *The build* and nothing more. It does not own **Reverence as a storyteller attention
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
| `float sustain` | institutional resistance to decay — **written by [#73](https://github.com/cjd721/Rimworld-Archinity/issues/73), read here** |
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
at a small constant. The step is reduced by the record's `sustain`, which is
[#73](https://github.com/cjd721/Rimworld-Archinity/issues/73)'s only required interface: **it
writes `sustain`, this reads it.** A faction whose institutions fully offset decay holds its
value; the requirement's *"institutions deliberately counteract natural Reverence decay and can
eventually make the faith self-sustaining"* is that subtraction and nothing more.

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

## The build — Exaltation and the sacred titles

**Vanilla Royalty already ships the whole Exaltation engine, and it is faction-generic.** Every
piece the requirement asks for — a rising earned scale, thresholds that confer permanent titles,
privileges those titles unlock, and a readout that names the next title and its price before you
reach it — exists in `Pawn_RoyaltyTracker`, `RoyalTitleDef`, `RoyalTitlePermitDef` and
`CharacterCardUtility`, and **every *per-faction* accessor takes a `Faction` as a parameter** [V].
The tracker also exposes an aggregate half that takes no faction and spans every ladder the pawn
holds — `MainTitle()`, `MostSeniorTitle`, `HasTitle(RoyalTitleDef)`, `HasAidPermit`,
`CanRequireThroneroom()`, `HighestTitleWithThroneRoomRequirements()`,
`AnyUnmetBedroomRequirements()`, `UpdateAvailableAbilities()`, `IssueDecree()` [V]. That half is
why §2's interleaving constraint exists; it is not a coupling to the Empire. Nothing is hardwired
to the Empire except a handful of quest generators and one UI seed.

So the verdict is neither *repoint* nor *replace*: it is **keep, and instance a second copy.** The
Church gets its own `royalTitleTags` ladder next to the Empire's, entirely in XML. Royalty's Empire
FactionDef is not edited, not repointed and not removed — which is also what makes the techprint
hazard a non-event (below).

**VFE Empire is not the donor.** Its honour/hierarchy/vassal layer resolves `Faction.OfEmpire` in
**136 places across 57 of its 227 decompiled source files** [V] and cannot be pointed at another faction without
rewriting the assembly; its `HonorsTracker` is a `List<Honor>` of discrete achievement objects with
no running total, no thresholds and no decay [V]; and its `WorldComponent_Hierarchy` reads a
`ModSettings` float inside `WorldComponentTick` to decide how many world pawns to generate, which is
**T-18** with `Rand` attached. It stays what it is — the Empire's ceremony layer — and Exaltation
does not touch it.

### 1. The ladder — pure XML

| Piece | Field | What it becomes |
|---|---|---|
| Church `FactionDef` | `royalTitleTags: [<ChurchTitle>]` | which ladder this faction confers [V] |
| " | `royalFavorLabel` (`[MustTranslate]`) | the word "exaltation" everywhere the engine prints the scale [V] |
| " | `royalFavorIconPath` (`[NoTranslate]`) | its icon in the quest reward stack [V] |
| Each title | `RoyalTitleDef` with `seniority`, `favorCost`, `tags`, `permits`, `rewards`, `permitPointsAwarded`, `grantedAbilities`, `awardThought` / `lostThought` | one rung [V] |
| Each privilege | `RoyalTitlePermitDef` with `<faction>`, `minTitle`, `permitPointCost`, `royalAid`, `workerClass` | one title privilege [V] |

`FactionDef.RoyalTitlesAwardableInSeniorityOrderForReading` builds the ladder by
`item.Awardable && item.tags.SharesElementWith(royalTitleTags)`, sorted by `seniority`, gated only
on `ModLister.RoyaltyInstalled` [V]. There is no Empire check anywhere in it.

**`RoyalTitlePermitDef.faction` is a `FactionDef`** [V], and every vanilla permit worker takes the
faction as a parameter and never reads `Faction.OfEmpire` [V]. Vanilla ships **five** delivery
workers — `RoyalTitlePermitWorker_DropResources`, `_CallLaborers`, `_CallAid`, `_OrbitalStrike` and
`_CallShuttle`, with `_Targeted` as their abstract base — plus VFE Empire's own
`RoyalTitlePermitWorker_Call` [V].

So *elite equipment, rare resources, military aid, specialists and requisitions* are authorable as
data: the content lives in `royalAid`, and the existing workers deliver it. **`RoyalAid` carries
`pawnKindDef`, `pawnCount`, `itemsToDrop`, targeting, explosion and temperature fields and nothing
else** [V]; `cooldownDays` is a field on `RoyalTitlePermitDef`, not on `RoyalAid` — the table two
rows above has the ownership right and an earlier draft of this paragraph did not.

⚠ **Two of the requirement's privilege classes have no data route at all, and an earlier draft of
this section claimed they did.** *Safe passage* and *political privileges* have **no vanilla
delivery worker and no `RoyalAid` field** [V]. They cannot be borrowed from vanilla's three trade
permits either: `TradeSettlement`, `TradeOrbital` and `TradeCaravan` carry no `<faction>` and no
`workerClass`, and their defNames appear nowhere in `Assembly-CSharp.dll`'s string heap [V] —
nothing instances them per faction, so a Church copy would be inert. **Both classes need new C# (a
`RoyalTitlePermitWorker` subclass) or authored quest content, and neither is inside the "~45 lines
of C#" aggregate in §5.** They are priced separately in §5 and recorded as *Outstanding decisions*
10 — a gap with no owner, and a clause `docs/requirements/RELIGION.md` should carry.

**Which of VFE Empire's 29 `VFEI_` permits become Church privileges is
a copy of the shape, not of the def** — they all carry `<faction>Empire</faction>` and `minTitle`
pointing at Empire titles, so they are a catalogue to imitate rather than a list to repoint.
`Permit_CallTechfriar.xml`'s 191 lines of 100% vanilla quest nodes
([`PARTS-BIN.md`](../data/PARTS-BIN.md) §7.5) is the worked template for a "a specialist arrives,
works under restriction, and leaves" privilege.

**Two permit economies, not one.** `RoyalTitleDef.permits` is granted outright with the title;
`permitPointsAwarded` accumulates a budget the player spends across `RoyalTitlePermitDef`s at
`permitPointCost` each, through `Pawn_RoyaltyTracker.GetPermitPoints(faction)` [V]. Both are
per-faction. The Church ladder sets its own numbers and does not share the Empire's.

### 2. State and persistence — already built, already scribed

`RimWorld.Pawn_RoyaltyTracker` holds [V]:

| Field | Shape |
|---|---|
| `List<RoyalTitle> titles` | one `RoyalTitle` per faction, each with `faction`, `def`, `receivedTick`, `conceited` |
| `Dictionary<Faction, int> favor` | **the Exaltation number** |
| `Dictionary<Faction, RoyalTitleDef> highestTitles` | the high-water mark, so rewards are not re-granted |
| `List<FactionPermit> factionPermits` | `(Permit, Faction, Title, LastUsedTick)` |
| `Dictionary<Faction, Pawn> heirs` | inheritance |

It is `IExposable`, scribed inside `Pawn.ExposeData`, and **every *per-faction* accessor is
`Something(Faction faction)`** [V] — `GainFavor`, `SetFavor`, `GetFavor`, `SetTitle`,
`TryUpdateTitle`, `CanUpdateTitle`, `MainTitleOf`, `GetPermitPoints` and the rest. **The aggregate
accessors take no faction and span every ladder the pawn holds at once**: `MainTitle()`,
`MostSeniorTitle`, `HasTitle(RoyalTitleDef)`, `HasAidPermit`, `CanRequireThroneroom()`,
`HighestTitleWithThroneRoomRequirements()`, `AnyUnmetBedroomRequirements()`,
`UpdateAvailableAbilities()` and `IssueDecree()` [V]. That is not a coupling to the Empire — it is
why the constraint below exists, and why two ladders on one pawn have to be designed together.
**Adding the Church ladder to a save that predates it costs
nothing**: an absent dictionary key reads as 0 favour and a null title, which is the correct
starting state, and `FindFactionTitleIndex(faction, createIfNotExisting: true)` creates the row on
first write [V].

⚠ **One `RoyalTitle` per (pawn, faction), and this constrains the ascent track.**
`FindFactionTitleIndex` matches on `titles[i].faction == faction` and `SetTitle` does
`titles[index].def = title` [V] — so conferring a second title *on the same faction* **overwrites
the first, silently**. If the tiers of godhood are also `RoyalTitleDef`s conferred by `SetTitle`
(**T-28**), they must be conferred *on a different faction* from the Church's, or the Church title
and the godhood title erase each other. `MostSeniorTitle` then picks the higher `seniority` across
both ladders, and the aggregate accessors listed above resolve against **both** — so the two
ladders' `seniority` bands must be chosen together. **No open ticket owns the godhood half** — #21
and #10 are both closed — so this is *Outstanding decisions* 7, below, and a gap on the map.

**`MostSeniorTitle` does *not* drive the pawn's displayed name, and an earlier draft of this
paragraph said it did.** `Verse.Pawn`'s only read of `MostSeniorTitle` is in `GetInspectString` —
an inspect-pane **body** line, not the label [V]. The displayed name comes from
`Pawn.LabelNoCount` / `LabelShortCap`, which do not read `pawn.royalty` at all.
[`TRANSCENDENCE.md`](TRANSCENDENCE.md)'s "the claimed epithet and any Church title coexist without
contention" is correct and stands; this document was the overstatement. What the seniority
comparison *does* govern is the aggregate half — throne and bedroom requirements, granted
abilities, decrees and the bio tab's Titles section via `MainTitle()` — which is the part that
makes the interleaving constraint real.

### 3. What changes it

**A. Quest rewards — free, and automatic.** `RewardsGenerator` offers royal favour whenever
`parms.allowRoyalFavor && giverFaction.allowRoyalFavorRewards && giverFaction.def.HasRoyalTitles`
[V]. `Faction.OfEmpire` appears in that method only in `flag5`, which suppresses items-only rewards
— it is **not** a gate on the reward itself [V]. So the moment the Church FactionDef has awardable
titles, Church quests start offering Exaltation in their reward stack, through
`Reward_RoyalFavor` → `QuestPart_GiveRoyalFavor`, with `faction = parms.giverFaction` [V]. No code.

**B. Authored quests — `QuestNode_GiveRoyalFavor`**, pure XML, for the scripted Church missions
[V]. `QuestNode_RequireRoyalFavorFromFaction` and `QuestNode_HasRoyalTitleInCurrentFaction` gate on
it.

**C. The Exaltation-or-Reverence fork.** Requirement 4 — *"Church missions must be able to award
Exaltation **or** Reverence depending on who gets credit"* — is two `Reward` subclasses on the same
quest, chosen by outcome: vanilla's `Reward_RoyalFavor` and the `Reward_Reverence` in *The build —
Reverence* §3B. Both appear in the quest's reward stack; both are `QuestPart`s hosted on their own
types. Nothing new is needed for the fork itself.

**D. The rite — a `RitualOutcomeEffectWorker` calling `TryUpdateTitle`.** `TryUpdateTitle(faction)`
→ `UpdateRoyalTitle` consumes exactly `nextTitle.favorCost`, sets the title, fires the award thought,
grants abilities, applies `rewards`, sends the vanilla gained-title letter, and loops if enough
favour remains for two rungs [V]. Roughly twenty lines of worker on top of an Ideology ritual gets
*"at Exaltation thresholds the founders perform a rite and receive the next title"* with the entire
consequence chain already written. VFE Empire's `RitualOutcomeEffectWorker_BestowTitle` /
`LordToil_BestowTitle` is the shipped precedent for the shape — but it calls
`SetTitle(Faction.OfEmpire, …)` directly and reads `GetNextTitle(defToBestow, ofEmpire).favorCost`
with no null guard, which NREs on the ladder's top rung [V]. Copy the pattern, not the code.

**`RoyalTitleDef.awardWorkerClass` — the hook the survey missed, and why the rite stays a ritual
outcome anyway.** Vanilla ships an
XML-selectable award hook that this spec did not previously survey: every `RoyalTitleDef` carries
`awardWorkerClass`, defaulting to `RoyalTitleAwardWorker` — a **no-op** — with
`RoyalTitleAwardWorker_Instant` shipped as the alternative, which calls `TryUpdateTitle` [V].
`Pawn_RoyaltyTracker.OnFavorChanged` invokes `item.AwardWorker.OnPreAward` / `DoAward` once per rung
crossed [V]. It is a real extension point, it needs no Harmony patch, and it is a cheaper home for a
hook than a ritual worker. The design uses it, but **by leaving it at its default**:

- **The default no-op is load-bearing, not an omission.** It is precisely what stops crossing a
  favour threshold from conferring the title by itself, which is what leaves room for the rite to
  *be* the conferral event. Setting `RoyalTitleAwardWorker_Instant` on a Church rung would make
  Exaltation auto-promote and delete the requirement's rite. **Never set it on a Church title** —
  the omission has to be deliberate and documented, because the field is one word in XML.
- **A custom `RoyalTitleAwardWorker` subclass is the right place for the *announcement*** — "the
  founders are eligible for the next rung" — since it fires exactly on the crossing, per rung, with
  the pawn and the title in hand, inside simulation. That is cheaper than watching favour ourselves
  [I].
- **It cannot host the rite itself.** `DoAward` runs synchronously inside `OnFavorChanged`, which
  is reached from a quest part's `GainFavor`; an Ideology ritual is a lord job that has to be
  gathered, scheduled and performed. The conferral therefore stays on the
  `RitualOutcomeEffectWorker` calling `TryUpdateTitle` [I].

⚠ **E. Vanilla will try to fly an imperial shuttle to the Church's ceremony, and the obvious
suppressor does not suppress.** Two callers generate that quest, not one [V]:

- `Pawn_RoyaltyTracker.RoyaltyTrackerTickInterval` calls
  `RoyalTitleUtility.ShouldGetBestowingCeremonyQuest(pawn, out faction)` every 37,500 ticks, which
  is `CanUpdateTitleOfAnyFaction` — **it iterates every faction in the game** — and on a hit calls
  `RoyalTitleUtility.GenerateBestowingCeremonyQuest`.
- **`Pawn_RoyaltyTracker.OnFavorChanged` calls
  `RoyalTitleUtility.EndExistingBestowingCeremonyQuest` and then
  `GenerateBestowingCeremonyQuest(pawn, faction)` *directly*, never consulting
  `ShouldGetBestowingCeremonyQuest`**, whenever the awarded-title seniority rises. `OnFavorChanged`
  is reached from `GainFavor` — which is exactly what `QuestPart_GiveRoyalFavor` calls, i.e. the
  "free, and automatic" reward route §3A recommends.

**So the imperial ceremony fires on the first Church quest reward that crosses a rung**, long before
any 37,500-tick scan, and an earlier draft of this section proposed a fix that is inert on that
path: a postfix on the two `ShouldGetBestowingCeremonyQuest` overloads never runs when
`OnFavorChanged` is the caller.

`QuestNode_Root_BestowingCeremony` hardcodes `PawnKindDefOf.Empire_Royal_Bestower`, six
`PawnKindDefOf.Empire_Fighter_Janissary`, a shuttle, and `Faction.OfEmpire` on the ship job [V] —
generated **for the bestowing faction**, i.e. wearing Church colours.

**The fix is a prefix on the single chokepoint `RoyalTitleUtility.GenerateBestowingCeremonyQuest`
that refuses the Church faction** — the one site both callers funnel through, ~20 lines. Patching
the two `ShouldGetBestowingCeremonyQuest` overloads as well is optional belt-and-braces (it keeps
the tick scan from re-selecting the Church and lets it re-scan for another faction); patching
*only* them is a silent no-op on the reward path. Without the chokepoint prefix the ceremony is not
a one-off cosmetic error: it re-arms on every rung crossing and again every 37,500 ticks for the
life of the campaign.

### 4. Where the player sees it — free, and already correct

**D1 — the character card, per faction, and it already satisfies the "see the carrot" clause.**
`CharacterCardUtility` draws one stack element per held title reading
`"<Title> (<favour>)"`, and its tooltip is `GetTitleTipString(pawn, faction, title, favor)` [V],
which prints:

- `faction.def.royalFavorLabel` and the current number — *"Exaltation: 14"*;
- `def.GetNextTitle(faction)` and `nextTitle.favorCost` — the next rung and its price, or
  *"final title"* at the top;
- and `RoyalTitleUtility.GetTitleProgressionInfo(faction, pawn)` — **the entire ladder**, each rung
  with its cost and a running total, plus the non-earnable titles listed separately [V].

That is the requirement's *"see the next title and what it unlocks before reaching it"*, drawn by
vanilla, faction-generic, with no patch. **This is why the display seam does not fall through here
the way [#52](https://github.com/cjd721/Rimworld-Archinity/issues/52) left Reverence's**: the
readout is not VFE Empire's tab, which we are not keeping — it is vanilla's character card, which is
already ours.

**D2 — the Permits card, and the one place it is *not* free.**
`Dialog_InfoCard` shows the Permits tab only when `PermitsCardUtility.selectedFaction != null`, and
`selectedFaction` is seeded in exactly one place — `StatsReportUtility.Reset`, to
`Faction.OfEmpire` [V]. The in-card faction switcher can reach the Church, but it is drawn *inside*
`PermitsCardUtility.DrawRecordsCard`, which the tab gates. **So if no `Empire`-def faction exists in
the world, the permits UI is unreachable for every faction, including ours, with no error** — a
circular gate. Under this build the Empire is present, so this is latent rather than live; the
insurance is a ~5-line postfix on `StatsReportUtility.Reset` that falls back to the Church faction
when `Faction.OfEmpire` is null. This is **T-35**.

> **Trap IDs, reallocated.** #53 proposed these two as T-33 and T-34, reading a register that then
> ended at T-32. T-33 was already taken by the KCSG unseeded-`System.Random` entry in
> `docs/traps/multiplayer.md`, and eight other tickets resolved the same night each claimed a T-34
> of their own. The orchestrator's allocation is authoritative: the permits-tab gate is **T-35** and
> the faction-def swap is **T-36**. Both are cited as live references throughout this document.

**D3 — the gizmo.** `Pawn_RoyaltyTracker.RoyalAidGizmo()` and `GetGizmos()` build the call-aid
command from `factionPermits` and are faction-generic [V]. Church permits appear on the founder's
gizmo bar with no work.

**Not used: VFE Empire's royalty main tab.** It *is* extensible —
`MainTabWindow_Royalty.DoWindowContents` iterates `DefDatabase<RoyaltyTabDef>.AllDefs` and each
`RoyaltyTabDef` carries a `workerClass` [V], so a Church tab would be one XML def plus one
`RoyaltyTabWorker` subclass. But the window is gated by
`MainButtonWorker_Royalty.Visible → Faction.OfEmpire != null && EmpireUtility.AllColonistsWithTitle().Any()`,
which is Empire-only [V], so a Church-titled colonist with no Empire title never sees the button.
Recorded because it looks like the obvious home and is not.

### 5. Cost

| Piece | Cost |
|---|---|
| Church FactionDef fields (`royalTitleTags`, `royalFavorLabel`, `royalFavorIconPath`) | **XML** — 3 fields |
| The title ladder | **XML** — one `RoyalTitleDef` per rung; vanilla's Empire ladder is 7 awardable + 4 non-awardable for reference |
| Title privileges — equipment, resources, military aid, specialists, requisitions | **XML** — one `RoyalTitlePermitDef` per privilege, reusing the five vanilla delivery `workerClass`es |
| Title privileges — **safe passage** and **political privileges** | **New C# or quest content — unpriced.** No vanilla worker, no `RoyalAid` field, and vanilla's three trade permits cannot be instanced per faction (§1). **Not in the aggregate below.** |
| Exaltation as a quest reward | **Nothing** — `Reward_RoyalFavor` is automatic once the ladder exists |
| Authored Exaltation awards | **XML** — `QuestNode_GiveRoyalFavor` |
| The consecration rite | **New C#** — one `RitualOutcomeEffectWorker` calling `TryUpdateTitle`, ~20 lines, plus the `RitualPatternDef`/`RitualBehaviorDef`/`RitualOutcomeEffectDef` trio in XML |
| Rung-crossing announcement (optional) | **New C#** — one `RoyalTitleAwardWorker` subclass named in `awardWorkerClass`, ~10 lines, no Harmony patch (§3D) |
| Suppressing vanilla's imperial bestowing quest | **Patch** — 1 Harmony **prefix on `RoyalTitleUtility.GenerateBestowingCeremonyQuest`**, ~20 lines. A postfix on the two `ShouldGetBestowingCeremonyQuest` overloads does **not** cover the `OnFavorChanged` path (§3E) |
| Permits-card faction seed (insurance, **T-35**) | **Patch** — 1 Harmony postfix, ~5 lines |
| The Exaltation / Reverence fork on a mission | **XML** — two `Reward`s on one quest; both halves already exist |
| Title rows, next-title tooltip, full ladder readout | **Nothing** — `CharacterCardUtility` |
| Church↔godhood ladder interleaving (`seniority` bands) | **Gap, no owner** — a design number, not a mechanism. #21 and #10 are closed; *Outstanding decisions* 7 |

**Aggregate: no new saved state, no new Def *types*, ~45 lines of C# in the existing
`ArchinityAltar.dll`, and the rest XML.** This is the cheapest capability on the board, and the
reason is that we are not building an Exaltation system — we are declaring a second instance of one
the DLC already ships.

⚠ **What that aggregate excludes, stated so it is not read as a total.** Safe passage and political
privileges are not in it and cannot be priced from the survey — they have no vanilla carrier at all.
The optional announcement worker is not in it. And it is 45 lines only because the rite's
`RitualPatternDef` / `RitualBehaviorDef` / `RitualOutcomeEffectDef` trio, the ladder and the permit
catalogue are all XML whose *content* still has to be authored and tuned (*Outstanding decisions* 8).

## The build — the founders' commitment to the Church

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

**So the Exaltation consecration rite (§ *The build — Exaltation* §3D) and the final altar rite
inherit neither the single-holder constraint nor §4A's three-believer threshold.** They inherit
whatever our own role precepts say — which, for the preacher rung, is `Precept_RoleMulti` with
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

## Persistence and multiplayer

### Exaltation

- **Multiplayer already syncs the royalty system.** `Multiplayer.Client.SyncMethods` registers
  `Pawn_RoyaltyTracker.AddPermit`, `RefundPermits`, `SetTitle` and `ResetPermitsAndPoints`, plus
  `RoyalTitlePermitWorker_DropResources.CallResourcesToCaravan` and a `SyncDelegate.LocalFunc` on
  `RoyalTitlePermitWorker_CallShuttle.CallShuttleToCaravan` [V]. Those are exactly the
  player-initiated writes, and they are handled for us.
- **`GainFavor`, `SetFavor` and `TryUpdateTitle` are deliberately *not* synced** [V], because every
  vanilla caller is already inside simulation — a `QuestPart`, a ritual outcome, a tick. Our rite is
  a ritual outcome and inherits that. **A UI button that awards Exaltation would need its own synced
  command**; nothing in this build has one.
- **Every tunable is a Def field by construction** — `favorCost`, `permitPointCost`,
  `permitPointsAwarded`, `cooldownDays`, `royalAid` are all XML (**T-18**).
- **Titles are per pawn, not per player faction**, so the one-shared-player-faction constraint
  (**T-21**) does not bite: both players see the same founders with the same titles.
- ⚠ **VFE Empire's `WorldComponent_Hierarchy` is a live T-18 defect and MP-Compat does not cover
  it.** `PER_RANK => VFEEmpireMod.Settings.noblesPerTitle` is read inside `WorldComponentTick` →
  `RefreshPawns` → `FillTitles`, which calls `MakePawnFor` → `PawnGenerator.GeneratePawn` [V]. Two
  clients with different slider values generate different numbers of world pawns inside the synced
  tick, consuming the shared `Rand` stream a different number of times.
  `Multiplayer.Compat.VanillaFactionsEmpire` covers the tab, honors, vassals, permits and the three
  ceremonies. **It is not true that it does not touch the component at all** — an earlier draft said
  so. `ReadRoyalPawn` **reads** `WorldComponent_Hierarchy.Instance.TitleHolders` [V]. What it does
  not do is the load-bearing part: it **patches neither `WorldComponentTick` nor `RefreshPawns` nor
  `MakePawnFor`** [V], so the settings-driven pawn generation inside the synced tick is unguarded.
  This is the Empire's problem, not Exaltation's, but it is the reason Exaltation does not build on
  that component.
- **The bestowing-quest suppressor sits inside simulation and must be deterministic.**
  `GainFavor` → `OnFavorChanged` → `GenerateBestowingCeremonyQuest` runs on both clients on the same
  tick (§3E). A prefix that consults client-local state — a setting, a UI selection — would generate
  the quest on one client and not the other. It may read `Faction`s and defs, and nothing else [I].

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
  "wrap every write" rule is actually about.
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

## Failure and recovery

### Exaltation

- ⚠ **A faction def swap silently kills the title ladder, and this is the campaign's most likely
  way to lose Exaltation.** [`factions-and-worldgen.md`](../engine/factions-and-worldgen.md)
  § *Climbing a faction by swapping `Faction.def`* is the era-gating mechanism
  ([#7](https://github.com/cjd721/Rimworld-Archinity/issues/7)), and the seven `[Unsaved]` caches in
  this area live on `FactionDef`, so they follow the **new** def correctly [V]. But
  `Pawn_RoyaltyTracker.titles` is keyed by `Faction` **instance**, and the held `RoyalTitle.def` is
  a title from the **old** def's ladder. If the new tier's def does not carry the same
  `royalTitleTags`, `RoyalTitlesAwardableInSeniorityOrderForReading.IndexOf(currentTitle)` is -1,
  `RoyalTitleDefExt.GetNextTitle` returns null, and `CanUpdateTitle` returns false **forever** [V].
  Exaltation keeps accruing and buys nothing; the character-card tooltip prints *"final title"*; no
  error is logged. **Every tier def of the Church faction must carry identical `royalTitleTags`,
  `royalFavorLabel`, `royalFavorIconPath` and `categoryTag`.** This is **T-36**.
- **A missing `royalFavorLabel` on a tier def degrades silently but harmlessly.**
  `GenText.CapitalizeFirst` is null-tolerant [V], so the tooltip prints a blank word rather than
  throwing. Cosmetic, and invisible unless someone reads the tooltip.
- ⚠ **Never give a Church title `favorCost: 0`** — **T-28**, now verified at source. It is excluded
  from the ladder, freezes any pawn standing on it, refuses its own `rewards`, and cannot be taken
  away by `ReduceTitle`. Four separate silent no-ops, none logged.
- ⚠ **Never give a Church title the `EmpireTitle` tag.** `VFEEmpire.WorldComponent_Hierarchy`'s
  static constructor collects every `RoyalTitleDef` with `seniority > 0` sharing a tag with
  `FactionDefOf.Empire.royalTitleTags`, and `MakePawnFor` dereferences
  `GetModExtension<RoyalTitleDefExtension>().kindForHierarchy` with **no null check** [V] — an NRE at
  world init. Loud, so not a trap, but a one-character mistake.
- ⚠ **The imperial bestowing quest is the loud-looking failure that is actually quiet, and it fires
  earlier than the tick interval suggests.** Without the §3E guard it generates a perfectly valid
  quest with the wrong content. Nothing errors; the campaign just acquires a shuttle it never
  wanted. The recovery-relevant detail is *when*: `Pawn_RoyaltyTracker.OnFavorChanged` calls
  `GenerateBestowingCeremonyQuest` **directly**, so it fires on the **first Church quest reward that
  crosses a rung** — through `QuestPart_GiveRoyalFavor` → `GainFavor` — and then again on the
  37,500-tick scan for the life of the campaign [V]. **A postfix on the two
  `ShouldGetBestowingCeremonyQuest` overloads is inert on the reward path**, which is the path §3A
  recommends; the guard has to be the prefix on `RoyalTitleUtility.GenerateBestowingCeremonyQuest`.
  An acceptance check that only advances the clock will not see the miss.
- **Never set `awardWorkerClass` on a Church `RoyalTitleDef`.** Its default,
  `RoyalTitleAwardWorker`, is a no-op, and that no-op is what leaves the rite as the conferral
  event. `RoyalTitleAwardWorker_Instant` calls `TryUpdateTitle` from inside `OnFavorChanged` [V], so
  one word of XML converts the ladder from rite-gated to auto-promoting, with no error and a
  perfectly ordinary-looking gained-title letter (§3D).
- **The Permits card can become unreachable.** Under D2, if `Faction.OfEmpire` is ever null the
  whole tab is gated off for every faction. This is **T-35**.
- **Conflict cargo, not a verdict:** RimPacts (`wowgag.rimpacts`, `3762723122`) ships
  `RptFactionUtility.IsEmpire` — `def.categoryTag == "Empire"` **and** non-empty `royalTitleTags` —
  plus five Harmony prefixes (`Patch_RoyalSetTitleNull`, `…SetFavorNull`, `…CurrentTitleNull`,
  `…GetNextTitleNull`, `…PurchasePermitsNull`) that skip the royalty path when no such faction
  exists [V]. Because this build keeps Royalty's Empire, those guards find it and stand down. They
  would fire if the Empire were ever removed, and they recognise a faction only by the *Empire*
  `categoryTag` — so a Church faction is invisible to them by construction.

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

## Status

**Verified available mechanism. Nothing here is an implementation commitment.**

### Exaltation

Established by
[Church Exaltation and the sacred titles](https://github.com/cjd721/Rimworld-Archinity/issues/53),
evidence class **READ** — vanilla `Assembly-CSharp.dll` and `VFEEmpire.dll` (the **1.6** file,
SHA-1-distinguished from the 1.5 and 1.4 copies), `Multiplayer.dll` and
`Multiplayer_Compat_Referenced.dll`, all decompiled with `ilspycmd` at the versions pinned in
`docs/data/MOD-SNAPSHOT.md`. `corpus.py --check` clean at the start and end of that session.

**The mechanisms are [V]; the claim that they compose into a Church ladder is [I]**, as every build
is until something is built. The specific untried part is the one the corpus says nobody has tried:
declaring `royalTitleTags` on a FactionDef that is not Royalty's Empire.

**Verdict for the sourcing ledger ([#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)):**

| Piece | Verdict |
|---|---|
| Royalty's title / favour / permit system | **reuse as-is** — carrier is the base DLC, not a mod |
| Royalty's `Empire` FactionDef and its content | **reuse as-is, untouched** — it is what keeps 18 techprint routes resolving |
| VFE Empire honour / hierarchy / royalty tab | **not the donor for Exaltation.** Its own verdict belongs to the Empire's slot, not to this capability — but [#21](https://github.com/cjd721/Rimworld-Archinity/issues/21) is **closed**, so that slot has no owner either |
| The Church ladder, its titles and its permits | **author from nothing** — but as data, not code |

**T-28 was verified at source and is correct**; **three of #53's own framing premises were wrong,
and its resolution mis-sited one patch**. See *Exaltation — five corrections*, below.

**This document was itself audited against the 1.6 assemblies after #53 closed, and the audit found
one design bug and six errors of fact.** The design bug — a bestowing-quest suppressor that does not
suppress on the path the build actually uses — is corrected in §3E, in the §5 cost table and under
*Failure and recovery*. The rest are corrected in place and each is marked where it stands: the
"every accessor takes a `Faction`" overstatement (§2), `MostSeniorTitle` and the displayed name
(§2), the safe-passage and political-privilege clauses that have no vanilla carrier (§1, §5),
`cooldownDays`'s owner (§1), the MP-Compat hierarchy claim (*Persistence and multiplayer*,
*Available mechanisms*), the ladder-shaped-def-type sweep marked [V] when it is [I], and the
`VFEI_` pawn-call count. The verdict on the whole was **solid with fixes**; the donor was confirmed
as the correct 1.6 `VFEEmpire.dll` by SHA-1 and every structural claim reproduced.

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

## Available mechanisms

### Exaltation — the donor is vanilla Royalty, and it is the whole system

Read from `Assembly-CSharp.dll` at `common/RimWorld/RimWorldWin64_Data/Managed/`, decompiled with
`ilspycmd` at 1.6.4871.

| Mechanism | What it gives Exaltation | Evidence |
|---|---|---|
| `Pawn_RoyaltyTracker` — `Dictionary<Faction,int> favor`, `List<RoyalTitle> titles`, `List<FactionPermit> factionPermits`, `Dictionary<Faction,RoyalTitleDef> highestTitles` | the number, the title, the privileges and the high-water mark, all per faction, all scribed | [V] |
| `FactionDef.royalTitleTags` × `RoyalTitleDef.tags` | which faction confers which ladder — the only coupling to the Empire, and it is **data** | [V] |
| `FactionDef.royalFavorLabel` / `royalFavorIconPath` | the scale's name and icon, `[MustTranslate]` / `[NoTranslate]` | [V] |
| `FactionDef.RoyalTitlesAwardableInSeniorityOrderForReading` | the ordered ladder, filtered by `Awardable` and tag, gated only on `ModLister.RoyaltyInstalled` | [V] |
| `RoyalTitleDefExt.GetNextTitle` / `GetPreviousTitle` | rung arithmetic, `Faction`-parameterised | [V] |
| `Pawn_RoyaltyTracker.GainFavor` / `CanUpdateTitle` / `TryUpdateTitle` / `UpdateRoyalTitle` | the threshold engine: consumes `favorCost`, sets the title, fires thoughts, grants abilities, drops `rewards`, sends the letter, loops for multiple rungs | [V] |
| `Pawn_RoyaltyTracker.OnFavorChanged` | the crossing event, reached from `GainFavor`: runs each crossed rung's award worker, then calls `RoyalTitleUtility.EndExistingBestowingCeremonyQuest` and `GenerateBestowingCeremonyQuest` **directly**, without consulting `ShouldGetBestowingCeremonyQuest`. This is why the suppressor is a prefix on the generator (§3E) | [V] |
| `RoyalTitleDef.awardWorkerClass` — default `RoyalTitleAwardWorker` (a **no-op**), with `RoyalTitleAwardWorker_Instant` shipped as the alternative (calls `TryUpdateTitle`); invoked as `AwardWorker.OnPreAward` / `DoAward` once per rung crossed | an XML-selectable hook on the crossing, needing no Harmony patch. The default no-op is what keeps conferral on the rite rather than on the threshold; a custom subclass is the cheapest home for a rung-crossing announcement (§3D) | [V] |
| `RoyalTitlePermitDef` with `faction`, `minTitle`, `permitPointCost`, `prerequisite`, `royalAid` | title privileges as data; `permitPointsAwarded` / `GetPermitPoints` is a second, budgeted economy | [V] |
| `RoyalTitlePermitWorker_CallAid` / `_CallLaborers` / `_CallShuttle` / `_DropResources` / `_OrbitalStrike` / `_Targeted` | the delivery workers — **none reads `Faction.OfEmpire`** | [V] |
| `Reward_RoyalFavor` → `QuestPart_GiveRoyalFavor` | Exaltation as a first-class quest reward with a stack element; `faction = parms.giverFaction` | [V] |
| `RewardsGenerator` `flag2` | auto-offers it for any faction with `allowRoyalFavorRewards && def.HasRoyalTitles`; `Faction.OfEmpire` appears only in `flag5`, which suppresses items-only rewards | [V] |
| `QuestNode_GiveRoyalFavor`, `QuestNode_RequireRoyalFavorFromFaction`, `QuestNode_HasRoyalTitleInCurrentFaction` | XML award and gate nodes | [V] |
| `CharacterCardUtility.GetTitleTipString` + `RoyalTitleUtility.GetTitleProgressionInfo` | the "see the carrot" readout: current favour, next title and its cost, and the whole ladder with running totals | [V] |
| `Pawn_RoyaltyTracker.RoyalAidGizmo` / `GetGizmos` / `OpenPermitWindow` | the in-game call-aid surface, faction-generic | [V] |
| `Multiplayer.Client.SyncMethods` | `AddPermit`, `RefundPermits`, `SetTitle`, `ResetPermitsAndPoints` already registered | [V] |

**What is Empire-bound in vanilla, precisely** [V]: `Faction.OfEmpire` is
`FactionManager.FirstFactionOfDef(FactionDefOf.Empire)` — a lookup by **defName**, not by tag. It is
read by worldgen (`GenStep_Outpost`, `GenStep_Settlement`, two `SymbolResolver`s), the tribute-collector
incident, six quest roots, `RewardsGenerator`'s items-only suppression,
`QuestNode_Root_BestowingCeremony`, and `StatsReportUtility.Reset`'s permits seed. **None of those
is part of the title mechanism**; they are Royalty's *content*.

### Exaltation — the wide pass, and what it justifies

Both corpus roots, all 155 mods, active and inactive, plus vanilla and the DLC. `.dll` swept with
`rg -a -g '*.dll' -g '!**/obj/**'` and again with `--encoding utf-16le`; `.xml` swept separately.
Validated against known hits (`HonorsTracker` in `VFEEmpire.dll` for ASCII;
`VFEEmpire.BestowTitle` / `RoyalAddress` for UTF-16LE) before any negative was trusted.
**`--encoding utf-16le` is an unsound sweep form — [#103](https://github.com/cjd721/Rimworld-Archinity/issues/103)** — and
the negatives below were re-checked after the fact; see § *Verification* → *Exaltation* for what
that re-check found.

- **`royalTitleTags` appears in exactly one XML file in the entire corpus, vanilla and DLC
  included** — `Data/Royalty/Defs/FactionDefs/Faction_Empire.xml`, value `EmpireTitle` [V]. No mod
  declares it, and no `PatchOperation` inserts it. **Nothing on disk has ever instanced the title
  system to a non-Empire faction.** All three code hits are reads:
  `VFEEmpire.WorldComponent_Hierarchy`'s static constructor, `RimPacts.RptFactionUtility.IsEmpire`,
  and EdB Prepare Carefully's setup UI.
- **Only three ladder-shaped def types were found corpus-wide:** `RoyalTitleDef`,
  `RoyalTitlePermitDef` and `VFEEmpire.HonorDef` **[I]**. The evidence is a vocabulary sweep, and a
  vocabulary sweep proves the absence of those *strings*, not the absence of the category — the
  residual gap at the end of *Verification* concedes exactly this, and the two claims must agree.
  Zero hits, both encodings, for `RankDef`, `ReputationDef`,
  `PrestigeDef`, `RenownDef`, `StandingDef`, `MeritDef`, `EsteemDef`, `AccoladeDef`,
  `CommendationDef`, `ExaltationDef`, `PromotionDef`, `OrdinationDef`, `ClearanceDef`,
  `PrivilegeDef`, `CharterDef`.
- **The nearest non-Empire standing ladder is VFE Classical's Senate** (`2787850474`) [V] —
  `WorldComponent_Senators` holding `SenatorInfo{Pawn, Favored}` per faction, declared in XML on
  **non-Empire** FactionDefs (`numSenators`, `senatorPerks`, `senatorResearch`, `finalPerk`), with
  `GameComponent_PerkManager.ActivePerks` delivering `PerkDef` stat effects. It proves the *shape*
  on a non-Empire faction and lacks both halves we need: `Favored` is a bool per senator, so there
  is no scale, and the reward is a perk, not a conferred name.
- **The nearest scale is RimPacts' `TrustRecord.trust`** (`3762723122`) [V] — a per-faction 0–100
  with decay floors, a scribed 10-entry audit log, threshold-gated privileges and named grade bands.
  It runs the wrong direction (the faction's trust *in* the player) and its grades are computed
  display bands, never conferred.
- **The strongest form of the negative is adversarial**: RimPacts is a 200-type diplomacy overhaul
  with vassalage, tribute, courts and puppet states, and it **refuses** to run the royalty path on a
  faction lacking the Empire's tags rather than extending it [V].

### VFE Empire — surveyed, and rejected as the donor

Read from `2938820380/1.6/Assemblies/VFEEmpire.dll`, confirmed as the 1.6 file by SHA-1 against the
1.4 and 1.5 copies and by the absence of `LoadFolders.xml`. **The mod's 176 `.cs` files live under
`1.4/Source/` and are not what 1.6 runs** (`MOD-SNAPSHOT.md` marks it ⚠).

- **`Faction.OfEmpire` / `FactionManager.OfEmpire` is resolved in 136 places across 57 of the mod's
227 decompiled source files** [V].
  Honors, hierarchy, vassals, the royalty tab, every ceremony gizmo and every `LordToil` gate on it.
  It cannot be instanced to another faction without rewriting the assembly.
- **`HonorsTracker` is not an Exaltation scale.** It is `List<Honor>` + `List<Honor> pendingHonors`,
  scribed `LookMode.Deep`, and `UpdateTitles()` writes the honours into the pawn's
  `NameTripleTitle` [V]. No running total, no thresholds, no decay — #98's claim re-derived and
  confirmed. Its only contact with the scale is `GameComponent_Honors.GameComponentTick` granting
  `GainFavor(Faction.OfEmpire, 1)` every 300,000 ticks for a `VFEE_LordOf` honour on a held
  settlement [V]. `HonorDef` remains valuable as the *named permanent mark* pattern
  ([`PARTS-BIN.md`](../data/PARTS-BIN.md) §7.5), which is a different capability.
- **`WorldComponent_Hierarchy` generates and mothballs the NPC nobility** for every Empire title,
  refreshed daily [V]. Its `Titles` list is built in a static constructor from
  `FactionDefOf.Empire.royalTitleTags`; `PER_RANK` reads `VFEEmpireMod.Settings.noblesPerTitle`
  **inside the tick that calls `PawnGenerator.GeneratePawn`** — **T-18**, with `Rand` attached, and
  **MP-Compat patches none of `WorldComponentTick`, `RefreshPawns` or `MakePawnFor`** [V].
- **`RoyaltyTabDef` is a genuine extension point** — `MainTabWindow_Royalty.DoWindowContents`
  iterates `DefDatabase<RoyaltyTabDef>.AllDefs`, each with a `workerClass : RoyaltyTabWorker` [V].
  Unusable here only because `MainButtonWorker_Royalty.Visible` requires an Empire-titled colonist.
- **`rwmt.multiplayercompatibility` ships a current `[MpCompatFor("OskarPotocki.VFE.Empire")]`
  handler** covering the tab, honors, vassals, permits and the three ceremonies [V]. It does
  **read** the hierarchy component — `ReadRoyalPawn` resolves a pawn through
  `WorldComponent_Hierarchy.Instance.TitleHolders` [V] — so "MP-Compat does not touch it", as an
  earlier draft put it, is wrong. The precise and load-bearing statement is that it patches neither
  `WorldComponentTick` nor `RefreshPawns` nor `MakePawnFor` [V]. VFE Empire is MP-safe as shipped,
  the hierarchy component's generation path excepted.
- **The 29 `VFEI_` permits are a catalogue to imitate, not a list to repoint** — every one carries
  `<faction>Empire</faction>` and a `minTitle` in the Empire ladder [V]. Sixteen are resource drops
  (that count is correct); **seven** are pawn calls — `CallCataphractPlatoon`,
  `CallJanissaryPlatoon`, `CallTrooperPlatoon`, `CallTechfriar`, `CallLaborerUnion`,
  `CallImperialRegiment` and `CallStellicGuards` [V], not the five an earlier draft listed — and the
  rest are shuttle, turret, shield, absolver and orbital-beam calls.

### Exaltation — five corrections

1. **T-28 is correct, and is now verified rather than corroborated.**
   `RimWorld.RoyalTitleDef.Awardable` is literally `public bool Awardable => favorCost > 0;` [V].
   The consequence is **stronger** than T-28 recorded: a `favorCost: 0` title is not merely
   invisible to award paths, it is a **trap you cannot get out of**. Four silent no-ops, none
   logged — `FactionDef.RoyalTitlesAwardableInSeniorityOrderForReading` omits it;
   `RoyalTitleDefExt.GetNextTitle` returns null because `IndexOf` is -1, so progression stalls
   permanently; `Pawn_RoyaltyTracker.UpdateRoyalTitle` early-returns on
   `!currentTitle.Awardable`; and `ApplyRewardsForTitle` refuses to deliver its `rewards`.
   `ReduceTitle` also early-returns, so it cannot be taken back. `SetTitle` itself never consults
   `Awardable` [V], so the direct-call approach the ascent track uses does work.
2. **"Empire's honor machinery is the obvious donor" is wrong about which machinery.** The honour
   *scale* is vanilla Royalty's `favor`, not VFE Empire's `Honor`. VFE Empire's contribution is
   ceremony and NPC nobility on top of a system it does not own.
3. **"Whether the honor scale can be instanced to a non-Empire faction" has a data answer, not a
   code answer.** Every method is `Faction`-parameterised; the coupling is one XML field pair
   (`FactionDef.royalTitleTags` × `RoyalTitleDef.tags`). Nothing on disk has done it, which makes it
   untried — not blocked.
4. **The display seam does not fall through, and the reason is not the one the ticket expected.**
   #53 anticipated that rejecting Empire's machinery would leave the ladder with no display owner,
   as [#52](https://github.com/cjd721/Rimworld-Archinity/issues/52) did to Reverence. It does not,
   because the readout was never VFE Empire's — `CharacterCardUtility.GetTitleTipString` and
   `RoyalTitleUtility.GetTitleProgressionInfo` are vanilla and faction-generic [V]. The only display
   work is the ~5-line permits-card seed (**T-35**).
5. **#53's resolution mis-sited the bestowing-quest suppressor, and this document inherited it.**
   The resolution's Cost row prices "the bestowing-quest suppressor (~20)" as a postfix on the two
   `ShouldGetBestowingCeremonyQuest` overloads. `Pawn_RoyaltyTracker.OnFavorChanged` never consults
   that method — it calls `RoyalTitleUtility.EndExistingBestowingCeremonyQuest` and then
   `GenerateBestowingCeremonyQuest` **directly** [V] — and `OnFavorChanged` sits on the
   `QuestPart_GiveRoyalFavor` → `GainFavor` path the same resolution calls "free, and automatic".
   The suppressor belongs on the generator, which is the chokepoint both callers funnel through
   (§3E). Related and from the same reading: #53 never surveyed `RoyalTitleDef.awardWorkerClass`,
   the shipped XML-selectable hook on that same crossing, whose default no-op is what keeps
   conferral on the rite rather than on the threshold (§3D).

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

## Verification

### Exaltation

READ-class throughout. Anchors are `Type.Member` for decompiled code and file paths for defs; no
line numbers.

⚠ **The sweep method behind every negative in this section is now known to be unsound, and the
negatives survived it anyway.** The wide pass used `rg -a --encoding utf-16le`, the form
`docs/agents/capability-research.md` prescribed at the time. That form **silently and
non-uniformly misses strings that are provably present in the `#US` heap** —
[#103](https://github.com/cjd721/Rimworld-Archinity/issues/103); the sound form is `-a` with a
null-interleaved pattern (`G\x00a\x00m\x00e\x00`). The audit re-ran this session's controls: the
UTF-16LE control (`VFEEmpire.BestowTitle` / `RoyalAddress`) was **genuinely encoding-sensitive**, so
the pass was actually exercising the wide path rather than passing on an ASCII-visible token, and
**the negatives here hold on re-check** — `royalTitleTags` in one XML file corpus-wide, no
non-Empire instancing, no fourth ladder-shaped def type. That is a better outcome than most of the
batch and it is not a reason to trust the method: the ladder-shaped-def-type bullet in *Available
mechanisms* is marked **[I]**, and any future re-sweep of this corpus should use the
null-interleaved form.

**The techprint hazard, verified and enumerated — and this build does not trigger it.**
`Verse.ResearchProjectDef.heldByFactionCategoryTags` (the field is on `Verse`, not `RimWorld`) is
matched against `FactionDef.categoryTag` at a single chokepoint,
`RimWorld.TechprintUtility.GetResearchProjectsNeedingTechprintsNow` [V]. **`categoryTag Empire` is
declared by exactly one FactionDef in the entire corpus** — `Data/Royalty/Defs/FactionDefs/Faction_Empire.xml`
— and no mod inherits from it or patches it [V]. **18 projects carry an Empire tag, not twelve**;
the ticket's twelve is the Royalty Empire-*only* subset:

| Source | Projects | Tags |
|---|---|---|
| Royalty implants (`BaseBodyPartEmpire_TierA/B`, tag declared once on the abstract parents) | `BrainWiring`, `SpecializedLimbs`, `CompactWeaponry`, `VenomSynthesis`, `ArtificialMetabolism`, `NeuralComputation`, `SkinHardening`, `HealingFactors`, `FleshShaping`, `MolecularAnalysis`, `CircadianInfluence` | Empire |
| Royalty apparel | `CataphractArmor` (×2 prints) | Empire |
| " | `JumpPack` | Empire, **Outlander** |
| VFE Deserters `3025493377` | `VFED_ImperialDefenses`, `VFED_ImperialWarSolutions` | Empire |
| GravTech `3545374124` | `GravEngineBuild`, `GravForge`, `BlackHole_GT` (×3 prints) | Empire, **TradersGuild** |

**14 are Empire-only.** `JumpPack` survives on `Outlander`; the three GravTech projects survive on
Odyssey's `TradersGuild`. The four map-gen setmakers
(`MapGen_AncientTempleContents`, `MapGen_AncientComplexRoomLoot_Default` / `_Better`,
`MapGen_AncientComplex_SecurityCrate`) pass `makingFaction == null`, and the tag test is **skipped
entirely when the faction is null** [V] — a real but unsteerable lottery (weights 0.05, chance 0.5,
`weightAccordingToPlayerNeeds=false`), not a supply line. `QuestNode_GiveTechprints` ignores tags
but has **zero users** corpus-wide [V].

**It fails completely silently.** `ResearchProjectDef.ConfigErrors` checks only three techprint
conditions and **never checks that any FactionDef supplies the tag**, let alone that such a faction
generated [V]; it runs at def-load, before a world exists, so it structurally cannot.
`TryGetTechprintDefToGenerate_NewTemp` returns false with no log;
`StockGenerator_Techprints.GenerateThings` breaks with no log;
`ThingSetMaker_Techprints.CanGenerateSub` returns false, so the setmaker is simply not chosen [V].
The `Techprint_*` ThingDef still exists — `ThingDefGenerator_Techprints.ImpliedTechprintDefs` reads
only `techprintCount` — so the research tab still says *"Required techprint"* and dev mode can still
spawn it. The only observation surface is the dev-mode debug output
`TechprintUtility.TechprintsFromFactions` / `TechprintsFromFactionsChances`, which prints
`"    none possible"` per faction [V].

**Under this build the Empire FactionDef is not edited, so all 18 routes resolve unchanged.** The
enumeration above is the cost of the *alternative* — repointing or removing the Empire — and it is
the single strongest argument against it.

**What still needs the game.** Nothing to settle the mechanism. Two **STUB**-class checks and one
**RUN** observation, all narrow:

- **STUB:** author a two-rung Church ladder plus one permit and run `tools/patch_check.py`, then in
  dev mode confirm `TechprintUtility.TechprintsFromFactions` still names the Empire for all 14
  Empire-only projects, and that the Church's titles appear in the character-card tooltip's
  progression list.
- **STUB:** confirm a Church-titled colonist with no Empire title does **not** raise VFE Empire's
  royalty main button, and that the Permits tab is reachable and switchable to the Church.
- **RUN:** one observation on [#16](https://github.com/cjd721/Rimworld-Archinity/issues/16)'s
  two-client regime — a consecration rite completing produces the same title on both clients on the
  same tick, and a permit invocation from one client's gizmo appears on the other.

**Residual gap, stated:** a mod could express a de-facto rank ladder as a chain of existing def
types (`PreceptDef` stages, a `QuestScriptDef` chain) with no distinctive type name, and no
vocabulary sweep would find it. Likewise a type resolved by runtime string concatenation. Neither is
excluded; both are unlikely to be a better donor than the DLC's own.

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

**All six are gaps, not hand-offs. None of them has an owner.** The two tickets that would naturally
own the first several — [#21](https://github.com/cjd721/Rimworld-Archinity/issues/21) (the ascent
track) and [#10](https://github.com/cjd721/Rimworld-Archinity/issues/10) (who the altar serves) —
are **closed**. Deferring to a closed ticket is the same failure as deferring to one that was never
created, so these are recorded here and belong on the map. Where an item below names a ticket, that
ticket is named as *context*, never as the owner.

6. **Is the Church a faction of its own, or the Empire relabelled?** This build assumes the former,
   because it is the only reading that leaves the 14 Empire-only techprint routes alone, and the only
   one consistent with the Church being a Medieval institution while the Empire is a proposed
   *Spacer* slot (#21's resolution, where the Empire slot is explicitly *"a live proposal,
   unapproved"*). If the campaign later decides the Church **is** the Empire, the mechanism is
   unchanged — one FactionDef instead of two — but the techprint enumeration above stops being moot
   and becomes the cost.
7. **The `seniority` bands, and how the two ladders interleave. Gap, no owner.** Church titles and
   the tiers of godhood both resolve through `Pawn_RoyaltyTracker`'s aggregate accessors —
   `MostSeniorTitle`, `MainTitle()`, `HasTitle`, `CanRequireThroneroom()`,
   `HighestTitleWithThroneRoomRequirements()`, `AnyUnmetBedroomRequirements()`,
   `UpdateAvailableAbilities()`, `IssueDecree()` — none of which takes a faction, so all of them
   resolve across **both** ladders at once [V]. (It is *not* the pawn's displayed name: that comes
   from `LabelNoCount` / `LabelShortCap`, which do not read `pawn.royalty` — see §2.) Choosing one
   ladder's numbers without the other's is how a Church rank silently outranks an apotheosis in
   throne requirements, granted abilities and the bio tab's Titles line. It also depends on §2's
   constraint — the two ladders must sit on different factions or they overwrite each other.
   **#21 and #10 are closed; nothing open owns this.**
8. **The numbers and the catalogue. Gap, no owner.** How many rungs, the `favorCost` per rung, the
   `permitPointsAwarded` curve, which privileges each rung unlocks, and the Exaltation-vs-Reverence
   split per mission outcome. All are XML Def fields by construction, so the build does not wait on
   them. **`docs/requirements/RELIGION.md` says only that "title and favor catalogs … still need
   design or tuning", and no open ticket owns them.** This is the same gap decision 4 records for
   Reverence's numbers; they should probably be one ticket, and that ticket does not exist.
9. **Whether ordinary colonists can hold Church titles, or only the founders.** The requirement calls
   titles *"permanent institutional standing"* and speaks only of the founders; `Pawn_RoyaltyTracker`
   is per-pawn and imposes no such limit, and `Reward_RoyalFavor.MakesUseOfChosenPawnSignal` lets a
   quest ask the player which colonist is exalted [V]. A gameplay rule, not a mechanism — it belongs
   in `docs/requirements/RELIGION.md` and is not currently there.
10. **Safe passage and political privileges — what they actually are, and who builds them. Gap, no
    owner.** The requirement lists them alongside equipment, resources, aid and specialists as
    though they were the same kind of thing. They are not: the other four are `royalAid` data
    delivered by a shipped worker, while these two have **no vanilla delivery worker, no `RoyalAid`
    field, and no borrowable trade-permit def** (§1) [V]. Until someone says what "safe passage"
    does to the simulation — caravan immunity, a goodwill floor, a raid-exclusion flag, or simply
    fiction — it cannot be priced, and the §5 aggregate deliberately excludes it. This belongs in
    `docs/requirements/RELIGION.md` as a behaviour statement before it can come back here as a
    build; no open ticket carries it.
11. **Tolerance / threat — named in the requirement's saved state, built by nothing. Gap, no owner.**
    `docs/requirements/RELIGION.md` § *Saved state and remaining work* says Church state includes
    "Exaltation, title, privileges **and tolerance/threat**", and the same section lists "tolerance"
    among the things that still need tuning. **Exaltation covers the first three and nothing in this
    document covers the fourth.** It is not `Pawn_RoyaltyTracker` state — that tracker holds favour,
    titles, permits, points and heirs and nothing resembling a tolerance or threat scalar [V] — and
    it is not Reverence, which is the *player's* religious penetration of a faction rather than a
    faction's patience with it. So it is either new saved state on the Church record, a projection
    of Goodwill owned by [`POLITICS.md`](POLITICS.md), or a requirement that should be withdrawn.
    **This document does not decide it and no ticket owns it**; recorded here because the
    requirement asserts state that has no builder.

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
15. **The roles clause in `docs/requirements/RELIGION.md` is wrong and no live ticket owns it.
    Gap.** *"The two founding pawns are mechanically forced into the ideology's defining
    leader/preacher roles"* is false twice over (§4). It should read something like *"the
    founders are the only pawns eligible for the ideology's leader and preacher roles, and the
    consecration rite seats them."* Recorded here because a requirement that asserts a mechanism
    the engine does not have is how a build gets designed against fiction.
16. **Is the commitment reversible, and at what price?** Mechanically it is trivially
    reversible — a second rite calling `SetIdeo` back, or enough colonists converting away —
    and `Pawn_IdeoTracker.previousIdeos` already records the founder's prior ideologies [V].
    Whether the campaign *permits* it is a requirement, and neither
    `docs/requirements/RELIGION.md` nor [`ENDING.md`](../plot/ENDING.md) says. **Gap, no owner.**
    This is the same unowned-numbers gap as decisions 4 and 8 and probably belongs in the same
    ticket.
