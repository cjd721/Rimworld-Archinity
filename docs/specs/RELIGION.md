# Religion

## Purpose and scope

How the religious systems in [`docs/requirements/RELIGION.md`](../requirements/RELIGION.md)
will be built. This document currently owns **Reverence end to end** — the number, the events
that move it, the decay that pulls it back, the bands, and the surfaces the player reads it
on.

It does not own **religious institutions inside foreign factions**
([#73](https://github.com/cjd721/Rimworld-Archinity/issues/73)); the interface those need is
named in *The build* and nothing more. It does not own **Reverence as a storyteller attention
weight** ([#60](https://github.com/cjd721/Rimworld-Archinity/issues/60)), **vassalage and
revolt** ([#35](https://github.com/cjd721/Rimworld-Archinity/issues/35)), or the **shape of
the political surface** ([#61](https://github.com/cjd721/Rimworld-Archinity/issues/61)) —
this document says what must be drawn and where the draw call goes, #61 decides what window
it lives in. Exaltation and Influence land here as
[#53](https://github.com/cjd721/Rimworld-Archinity/issues/53)–[#54](https://github.com/cjd721/Rimworld-Archinity/issues/54)
resolve.

Goodwill and the political ripple are [`POLITICS.md`](POLITICS.md)'s. The two systems are
separate axes by requirement; whether they couple is an open decision, below.

## The build

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

## Persistence and multiplayer

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

## Failure and recovery

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

## Status

**Verified available mechanism. Nothing here is an implementation commitment.**

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
still happened.

## Available mechanisms

### There is no donor for the measure itself

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

## Verification

READ-class throughout, from decompiled 1.6 assemblies at the pinned versions. The negative was
justified by a wide pass over both corpus roots — the workshop root **and**
`common/RimWorld/Mods` — in ASCII and UTF-16LE, and the sweep was validated against a known hit
(`GoodwillSituationWorker`, 13 files) before its negatives were trusted.

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

## Outstanding decisions

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
