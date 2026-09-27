# Capabilities

What RimWorld 1.6, the DLC and the mods on disk can do for each system the campaign needs, one
card per system. **Read this before writing a beat.** It tells you what the game can and cannot
do without opening a spec.

This document **summarises** `docs/specs/`. It adds no verdict, route or limit of its own. Where
this document and a spec disagree, the spec wins, and this document is wrong. The requirements
each system answers are in `docs/requirements/`. Gaps between specs are tracked in
[`specs/INTEGRATION.md`](specs/INTEGRATION.md).

## Reading a card

- **Possible?** Yes · Partly · No, for the system as a whole. **Multiplayer?** Yes · With work ·
  No · Unknown. "Yes (spec), condition: …" is a Yes that the spec gives only if the stated
  condition holds.
- **Routes** are the genuinely different ways to deliver a capability:
  - The "what it gets us" of each route.
  - The carrier: vanilla, a named mod, or our code.
  - The kind: XML, patch or C#.
  - The weight: Easy · Medium · Hard, as defined in [`specs/README.md`](specs/README.md#routes).
  - *Not recommended* marks a route that is possible but has no good reason to be taken.
- **A (as specced)** marks a spec written before the routes rule. It designed one build and
  stated no alternatives. That build is shown as the only route.
- **(mapped)** marks a weight the spec never stated. It was mapped from the spec's line counts or
  shape, using the README's definitions.
- **[I]** marks a claim the spec itself marks as inferred rather than verified.
- **Verified is not selected.** "Spec recommends" repeats the spec's recommendation. Choosing a
  route is the build map's decision ([#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)).
- *What the story can do* lists the levers a beat can pull. *What it cannot do* lists the hard
  limits a beat must not assume. Trap IDs (T-NN) are in [`TRAPS.md`](TRAPS.md).
- Links to tickets are `#NN`. The investigation behind each answer lives on its ticket.

## At a glance

"Open" names the capability tickets still open against a system: requirement clauses that no
spec answers yet. They are listed in [Open capability questions](#open-capability-questions)
below. Until one closes, write no beat that depends on it.

| System | Possible? | Multiplayer? | Open |
|---|---|---|---|
| **Faith** | | | |
| [The altar](#the-altar) | Yes; a willing giver is a certainty threshold, gated by one small role class | Yes (spec), conditional; one two-client run owed | — |
| [Religion](#religion) | Yes | With work; varies by its four sub-cards | — |
| [The psychic track](#the-psychic-track) | Partly: "rank only from the altar" needs VPE's XP loop cut or gated | Yes (spec), conditional | — |
| [Transcendence](#transcendence) | Yes | Yes (spec), conditional | — |
| **Politics** | | | |
| [Faction politics](#faction-politics) | Yes; by design, no peace with a permanent enemy, and no demand to defend a world-map route (#174) | Yes; With work for some routes | — |
| [Territory](#territory) | Yes; one era-advance edge case | With work | — |
| [Pressure](#pressure) | Yes; the composition is [I] until played | Yes (spec), conditional | — |
| [Encounters](#encounters) | Yes | Yes | — |
| **Glittertech** | | | |
| [Trace and the Glitterite pursuit](#trace-and-the-glitterite-pursuit) | Yes | With work (T-177) | — |
| [Spendable currencies](#spendable-currencies-influence-and-intel) | Yes | With work | — |
| [Hacking](#hacking) | Yes, on Ushanka's Hacking Expansion | With work | — |
| [Androids](#androids) | Yes | Yes (spec), conditional on MP Compat's entry | — |
| [Research](#research) | Yes | Yes | — |
| **World and space** | | | |
| [Era](#era) | Yes; the arrival band holds only by a gate of ours, not by Ignorance Is Bliss alone | With work | #207 |
| [Charting](#charting) | Yes | With work | — |
| [World infrastructure](#world-infrastructure) | Yes; NPC vehicles only from Industrial | With work | — |
| [Orbit](#orbit) | Partly: closing orbit rests on our switches; [#22](https://github.com/cjd721/Rimworld-Archinity/issues/22) is open | Yes (spec), conditional | — |
| [Gravship](#gravship) | Partly: ordinary life arriving at an orbital home is gated | Mostly Yes; the home build is Unknown | — |
| **Colony** | | | |
| [Colony management](#colony-management) | Yes | Yes | — |
| [Shipped defaults and presets](#shipped-defaults-and-presets) | Partly for gear sets; Yes for bills | Yes / With work | — |
| [Items and gear](#items-and-gear) | Yes | Yes | — |
| [Specialisation](#specialisation) | Yes, through a system of ours (Hard) | With work | — |
| [Quests](#quests) (spans four specs) | Yes; taken beats stay legible only with a readout or tab patch of ours | With work | — |

## Open capability questions

Requirement clauses that no spec answers yet, each on its own ticket. When a ticket closes, its
answer lands in the named spec, and its line here and on its card is replaced by that answer.

- **Era** · [#207](https://github.com/cjd721/Rimworld-Archinity/issues/207) Every faction hand-authored,
  spawn pools included: can every faction, ours or a mod's, be closed against pawn kinds, gear and
  xenotypes we did not write? (`requirements/ERA.md`, 2026-09-26.)

Nine earlier questions (#92 reopened, #190–#197) were answered on 2026-09-23, and each card below carries
its answer. A demand's "protected route" was reworded to an escort or a threat
cleared ([#198](https://github.com/cjd721/Rimworld-Archinity/issues/198)), since routes are never threatened.

Clauses this pass found unanswered, but that turned out to be shape decisions rather than
capability questions, are owned by [the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119).
The reasons are on [the capabilities document's ticket](https://github.com/cjd721/Rimworld-Archinity/issues/121).

---

## Faith

### The altar

**Possible?** Yes. The final rite and the lottery are specced. Charge that never spoils, and "the donor dies, the recipient lives", are already built. Willing means believing enough: a giver is admitted only at a certainty threshold (e.g. 85 %). No ritual ships that, but one small role class gates a vanilla-style sacrifice rite on it (#49). The threshold is #119's.
**Multiplayer?** Yes (spec, on reading), condition: every path runs on the altar's synced tick or through Multiplayer's own `PersistentDialog`. One two-client run is owed for the lottery (Verification 4). A stale caravan-dialogue flag can still split one click (T-82 by another door).

The Archotech apparatus. It banks blood and life as charge and grants named genes to a living recipient. It runs an opt-in gene lottery. At the end it grants the shipped `VRE_Transcendent` gene to a founder who has claimed a title.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| Charge that never spoils; the donor dies, the recipient lives | Yes, built [V] | Yes (the altar's synced tick) | **A (already built)** The charge lives in the altar and has no decay path. A prisoner or slave is fuel and dies. Anyone else is a recipient and leaves alive · `ArchinityAltar.dll` · Easy (mapped: nothing to build) | [§ Available mechanisms](specs/ALTAR.md#the-three-asserted-and-nowhere-verified-altar-behaviours-are-built-and-they-work) |
| Willing devotion counts differently from coerced life: a giver is admitted only at a certainty threshold | Yes. Nothing ships it and XML alone cannot gate a role on certainty; one `RitualRoleColonist` subclass reading `Certainty` does | Yes: Multiplayer syncs the ritual dialog and roles by id | **A** a sacrifice rite where the priest kills the believer: vanilla's `Sacrifice` duty aimed at our certainty-gated role · XML + one class (~20 lines) · Easy. Vanilla records it as an executed colonist<br>**B** the believer gives their own life as the rite completes: VIE Memes' Ceremonial Suicide outcome by XML, or a copy, plus the same role class · Easy. The threshold, and whether a mid-rite drop cancels, are #119's | [§ Available mechanisms](specs/ALTAR.md#the-three-asserted-and-nowhere-verified-altar-behaviours-are-built-and-they-work) |
| Electricity improves the apparatus but never replaces the life | Yes, built [V] | Yes | **A (already built)** Linked, powered facilities scale the charge cost, with a floor of 25 %. Their category bias and extra options have no reader until the lottery is built · our code · Easy (mapped) | [§ 7](specs/ALTAR.md#7-what-a-repeat-costs-and-what-is-remembered) |
| A named core vector grants its gene, deterministically | Yes: the existing arm [V] | Yes | **A (already built)** The rite calls `GrantGene` and the recipient survives · our code · Easy (mapped). Which genes, and mark-locking, are #31's | [§ 9](specs/ALTAR.md#9-what-spends-the-charge--and-the-trap-it-closes) |
| An opt-in lottery with genuinely bad outcomes, and a drawn offer the player must take | Yes (mechanism). The bad band has no teeth until tier 1 holds more genes | Yes (spec, on reading), condition: one two-client run (Verification 4) | **A (as specced)** One roll picks a tier band. Four genes, plus facility extras, are drawn by weight; the capsule's category is a weight, never a filter. The offer is a vanilla `Dialog_NodeTree` with no Close option. The recipient is held until the player chooses, and a deadline picks at random · our C#, no Harmony · Medium (mapped)<br>**B** Multiplayer's `GrowthMomentSession` shape plus a `Multiplayer.API` reference · C# · weight not stated · *fallback only if the two-client check fails*. Ruled out: a custom `ChoiceLetter` (unsynced) and VQE Ancients' window (desyncs) | [§ The build — the repeatable lottery](specs/ALTAR.md#the-build--the-repeatable-lottery) |
| The player knows the domain of the gamble, not the outcome | Yes, both versions buildable | Yes | **A (as specced)** The category is printed on the capsule and on the altar, and the four options are shown in full. The odds stay unpublished · XML + ~4 lines · Easy (mapped)<br>**B** Publish the odds per option (VQE Ancients' `GetOutcomeChance` is the donor) · ~15 lines C# · Medium (mapped) | [§ Odds](specs/ALTAR.md#odds-legible-options-opaque-distribution--and-why) |
| The final rite grants `VRE_Transcendent` to a founder who has claimed a title, and a transcended founder is never fuel | Yes | Yes (synced tick) | **A (as specced)** The no-vector arm adds the shipped gene, sets the founder's transcended tick and opens the Administrator. A refusal inside the fuel branch is keyed on the founder record, never on the gene, because every `VRE_Archon` carries it · our C# · Medium (mapped) | [§ The final rite](specs/ALTAR.md#the-final-rite) |

**What the story can do with it**
- Bank a sacrifice now and spend it eras later: charge never rots.
- Burn a prisoner or slave as fuel, who dies, or put anyone else in as a recipient, who lives.
- Let power and facilities make each rite cheaper, never below a quarter of the blood. For the lottery they also lean the draw toward a category and widen the offer.
- Keep a named rite's promise: load a vector naming a gene, and the recipient walks out alive with it.
- Offer the lottery as a gamble the player opts into. The capsule prints its domain, four genes of comparable worth appear in full, and one must be taken. Walking the pawn away is not an exit, and a pawn never draws a gene it already carries.
- Lock the final rite with a stated reason: "X has not claimed a title". Once through, the founder goes straight to the Administrator.

**What it cannot do**
- Gate a ritual role on certainty in XML alone. It takes one role class (~20 lines), and nothing re-checks certainty once the rite has started.
- Give the worst lottery band teeth. Tier 1 holds one drawable gene, so the bottom band always widens into the next (#31). `Social` holds one gene, so a category is a lean, never a guarantee.
- Skip the fuel refusal. Our own drain calls `Pawn.Kill`, which Deathless does not stop.
- Use a null-gene vector before the lottery ships: it silently consumes the rite and reports success (**T-64**).
- Run two offers at once. No one can enter while an offer is pending. An offer opened behind an unanswered Administrator dialog is invisible and can time out into a gene nobody saw (open build task). Under Multiplayer the offer re-shows only while its map is being drawn.
- Keep `VRE_Transcendent` rite-only yet. Random genepacks, captured `VRE_Archon` pawns and More Archotech Garbage leak it (sealing is #119's). The pool also offers `VRE_InnatePsylink`, a psylink by gene (#31).
- Gate the lottery to Industrial or convert hoarded Archon capsules. That is era and progression work, not priced here. The optional anima-teaching encounter is [`ENCOUNTERS.md`](specs/ENCOUNTERS.md).

**Spec and tickets:** [`specs/ALTAR.md`](specs/ALTAR.md) · #59 the final rite, #110 the lottery, #49 willing givers, #31 the gene pools, #112 the dangling `Resurrect` entry, #158 the anima encounter (answered in `ENCOUNTERS.md`)

---

### Religion

**Possible?** Yes. Every behaviour has a verified route. The only thing no route gives is a revolt that splits off a new lasting faction, which the requirement forbids anyway.
**Multiplayer?** With work. The Schism's writes, and a revolt's pawn and leader generation, must fire from a quest signal or a synced command. Comms options must be disabled rather than omitted, and must host their action on an allowed type. Several compositions still owe a two-client run (#16).

The player faith and how far it reaches into other peoples. The Church (the Empire transformed), its titles, decrees and betrayal. The Schism that replaces it, revolts and changing faiths, and how the game knows a founder. One spec, [`specs/RELIGION.md`](specs/RELIGION.md), carried here as four cards.

#### Religion · Reverence and institutions

**Possible?** Yes.
**Multiplayer?** Yes [I] for the number. The hook fires inside simulation, and one two-client check is owed (#16). Gated comms actions need work: the enabled action must be on an allowed type, and gated options are disabled, never omitted.

How deeply the player faith has reached each NPC faction, and the churches that hold it there.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| A per-faction number raised by believers carrying the faith home and by credited deeds | Yes. Vanilla pilgrims cannot carry it | Yes [I] | **A (as specced)** One world store. A hook on a pawn leaving the map catches converted visitors and prisoners released as believers. A quest part and reward cover deeds · our C# + Harmony · Hard (mapped: new saved state, three postfixes)<br>**C** a table of which history events move Reverence, in XML · Medium (mapped) · *recommended only if it earns its keep*. Pilgrims need an authored quest from the real faction | [§ 3 What changes it](specs/RELIGION.md#3-what-changes-it) |
| Decays when neglected; crosses announced bands | Yes | Yes | **A (as specced)** A capped step on a neglect timer, the natural-goodwill shape, reduced by institutions. Bands are XML defs, with a letter on each crossing · our C# + XML · Medium (mapped) | [§ 4 Decay](specs/RELIGION.md#4-decay) |
| Shown beside Goodwill; gated diplomacy visible before it opens | Yes. The faction info card is not an option | With work: the enabled option's action must be on an allowed type | **D1** A strip on the Factions-tab row. Real, but contested by three mods and needing a re-check each update · Medium (mapped)<br>**Own political tab** · a vanilla `MainButtonDef` + `MainTabWindow`, no conflict · C# + XML · Medium (the shape of POLITICS RD-7) · the surface is #119's<br>**D2** A greyed comms option: "requires N Reverence — currently M" · Medium (mapped) | [§ 6](specs/RELIGION.md#6-where-the-player-sees-it) |
| Reverence scales Goodwill: a wary middle, a sharp top, losses too | Yes | Yes | **A** a reason-aware scaler at the one goodwill choke point · Medium (spec recommends)<br>**A2** A plus a named "why" line per change · Medium<br>**B** scale vanilla's adjuster; reason-blind · Medium · *not recommended* unless every change counts<br>**C** scale at each source · Medium→Hard<br>**D** Reverence as natural goodwill · *partial, not recommended alone*: cannot reduce a gain<br>**E** a ceiling instead of damping · *partial*: a different fiction | [§ Reverence scales the Goodwill](specs/RELIGION.md#reverence-scales-the-goodwill-a-faction-gains) |
| Institutions in friendly factions: Reverence unlocks, Goodwill pays, they hold off decay, hostility suppresses them | Yes | Yes (spec), condition: the founding click is synced by Multiplayer as long as a gated option is disabled, never omitted | **A (as specced)** A record on the faction's Reverence entry, founded from a comms option priced in Goodwill. It is suppressed (not destroyed) when the relation turns Hostile and restored when it turns back, each with a letter · C# + one postfix · Medium (mapped)<br>**B** A settlement comp holding the state: visible, selectable and caravan-reachable · *not recommended*: a second store for a number the ledger owns, keyed to settlements that come and go<br>**A + display adapter** the same comp holding only a lookup into the ledger, for a world-map presence · XML + ~25 lines C# · Medium (mapped), only if taken | [§ Institutions](specs/RELIGION.md#the-build--religious-institutions-inside-foreign-factions) |

**What the story can do with it**
- Make Reverence personal. It moves when a believer goes home, such as a converted visitor or a prisoner released as a believer, or when a deed is credited to the founders. Offer it as a quest reward the player chooses.
- Show the carrot. Every Reverence gate appears greyed, with its threshold and the current value. Band crossings arrive as letters.
- Make governments react to the faith. At low Goodwill and high Reverence a government is wary: gains shrink and losses deepen. Past the top band it is won over. This works per faction, optionally with a named reason line.
- Plant a church or monastery by spending Goodwill behind a Reverence gate. It holds Reverence up, is suppressed with a letter when the host turns hostile, and is restored on peace. A hostile government can be made worse than neglect (a negative suppression factor). Destroying institutions is also buildable, and the spec prices a donor for it.

**What it cannot do**
- Give Reverence or institutions to a faction the world was not created with (T-07).
- Credit vanilla pilgrims. They belong to a throwaway hidden faction, so the number would vanish.
- Stop a stored decay offset drifting. The spec's build recomputes it. Shipped without the clamp, institutions quietly make Reverence rise on its own.
- Fail loudly. If the leaving-map hook or the suppression hook is missed, nothing logs; only the number shows it.
- Own the storyteller's attention weight (`PRESSURE.md`) or the global view's surface (#119, #61).

**Spec and tickets:** [`specs/RELIGION.md`](specs/RELIGION.md) · #98 Reverence, #160 / #176 Goodwill scaling, #73 institutions, #61 political surface

#### Religion · The Church

**Possible?** Yes.
**Multiplayer?** With work. The betrayal write must force a goodwill recalculation, or a player joining in the window diverges [I]. The ending's refiring timer is "with work", and one click ends the run for both players only when the accepter is on a map (#191). Everything else is Yes [I], with two-client checks owed (#16).

The Empire transformed in place into a Roman-Catholic-like Church: Exaltation, titles by rite, perks, decrees, the credit for deeds, and a betrayal that is final.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| The Empire becomes the Church in place; Church quests pay Exaltation; titles come by a rite | Yes. Renaming any identifier breaks it | Yes [I] (the ceremony is simulation; two-client check owed) | **A (required)** relabel in XML, rename nothing · Easy (mapped)<br>Ceremony **A** vanilla's bestowing ceremony reskinned, with a bestower and honour guard arriving and psylink levels zeroed · XML · Easy (mapped) (spec recommends)<br>Ceremony **B** the founders run their own title ritual, and the bestower quest is refused · C# · Medium (mapped). Chosen on fiction alone | [§ The build — Exaltation](specs/RELIGION.md#the-build--exaltation-the-empire-becomes-the-church-in-place) · [§ 4](specs/RELIGION.md#4-exaltation-and-the-rite--vanilla-unchanged-and-no-longer-a-hazard) |
| Titles unlock privileges and Church trade | Yes, native | Yes [I] (royalty writes are synced; not re-read) | **A (as specced)** Vanilla permits are relabelled as Church privileges and new ones are data. Trade already needs a Knight (a Baron for orbital), and closes while the Church is hostile · XML · Easy (mapped) | [§ 5 Privileges](specs/RELIGION.md#5-privileges--native-now-and-trade-is-already-one-of-them) |
| Credit for a deed is chosen at acceptance: Church, founders, Schism or a mix | Yes. Options freeze at generation | Yes. Two near-simultaneous clicks: RUN owed (#16) | **A** our credit node: written options per deed, any reward mix, consequences per option, and a Schism option only when working with the Schism · Medium (spec recommends)<br>**B** patch the reward generator, so founder and Schism credit appears on every random-reward quest · Medium<br>**C** vanilla as shipped · Easy · *not a route to the requirement* | [§ Credit for a deed](specs/RELIGION.md#credit-for-a-deed--the-attribution-chosen-at-acceptance) |
| Decrees whose failure costs mood, Exaltation or Goodwill; none while the Church is hostile | Yes | Yes [I] | **A** author the failure branch per decree · XML (+ one tiny node without VFED) · Easy with VFED / Medium without<br>**B** decrees end with the Church · XML · Easy<br>**C** a generic C# cost hook · Medium · *not recommended*: nothing generic to reach<br>**D** Church-issued decrees on a schedule · Easy / Medium. Spec recommends A + B | [§ Decrees](specs/RELIGION.md#decrees--what-failing-one-costs-set-per-decree) |
| Who may hold a Church title | Yes, any rule. Founders-only needs C# | Yes [I] | **A** anyone, as shipped · Easy<br>**B** guard the write methods: refuse, or redirect to a founder · Medium<br>**C** steer each surface (accept menu, choose-pawn letter, inheritance, tribute collector) · Medium<br>**D** restricted by kind · Medium<br>**E** authored deeds name the founder · Easy / Medium | [§ Who may hold a Church title](specs/RELIGION.md#who-may-hold-a-church-title--every-exaltation-writer-and-the-seams-that-keep-titles-on-the-founders) |
| Betrayal is final: the Church is permanently hostile | Yes (the latch). The threshold firing the authored mission is not routed in RELIGION. The seam is ENCOUNTERS T4, our storyteller comp that offers a quest once its condition holds [I], and revolt route A's quest eligibility already reads Reverence. The beat itself is #119's | Yes (spec), condition: the bit's write calls `RecalculateAll` | **A** one saved bit read by a goodwill worker, capping the Church at −100 · C# · Medium (mapped)<br>**B** VFE Deserters' latch, if VFED ships · as shipped | [§ 6 Betrayal](specs/RELIGION.md#6-betrayal--the-permanent-hostility-latch) |
| The Church's ending: sanctioned apotheosis offered at the top title, and accepting ends the run for both players | Yes. Accept is a synced command, and a quest part listening to its `Initiate` signal runs inside it on both machines; the command's map context follows the accepter (T-193) | With work: one click ends the run for both only with a spawned accepter (the two-client run is shared with TRANSCENDENCE); otherwise each player leaves on their own click, or we sync the dialog through the MP API | Offer: **(as specced)** Royal Ascent's shape, a refiring offer gated on the top title, closed by the betrayal bit or the orbital reveal; vanilla's Royal Ascent is stripped · XML · Easy (mapped)<br>Ending: **A** accept on the map: a titled, spawned accepter, and our quest part opens the game-over dialog · XML + C# · Medium (spec recommends) · MP Unknown until TRANSCENDENCE § Verification 5–6<br>**B** accept anywhere, the dialog registered with `MP.RegisterSyncDialogNodeTree` · C# · Medium · MP Unknown, the same run · not saved, so a rejoining player never sees it<br>**C** accept anywhere, each player leaves on their own click · C# · Medium · MP Yes<br>**D** accepting summons the ending and a later act on the map finishes it · Medium · changes the requirement's wording<br>Vanilla `QuestNode_EndGame` is *not a route*: it rolls credits and play continues | [§ 7 Cost](specs/RELIGION.md#7-cost) · [§ 8 Accepting ends the run](specs/RELIGION.md#8-the-churchs-ending--accepting-ends-the-run-for-both-players) |

**What the story can do with it**
- Run the Church on vanilla Royalty. Quests pay Exaltation, and a rung brings a bestower and honour guard, or the founders' own rite.
- Let titles open permits and Church trade. Titled colonists get decrees whose failure costs mood, Exaltation or Goodwill.
- Put the temptation at "Accept". Each deed's reward rows are its credit, with consequences riding on the row.
- Restrict titles to founders, to a kind, or to anyone.
- Betray in one authored write. The Church turns hostile for good with vanilla's letter. Decrees and perks end; titles stay.
- Offer the Church's own ending while the top title is held, closing for good at betrayal or the orbital reveal. The run ends at the *Accept* click.

**What it cannot do**
- Rename the Church at identifier level, or swap its def to present it per era (T-36, T-98). Its name, clergy and creed exist only in a world generated after the patch. It must be exempt from World Tech Level's roster strip (T-54).
- Grant a title without psylinks unless every Church title's psylink level is zeroed. Even then, VPE gives an honoree with no psylink one level (`PSYCHIC.md` R9, C#).
- Change a quest's credit options once offered. Options freeze at generation, only one choice per quest is visible, and acceptance requirements apply to the whole quest.
- Keep Church trade and steerable Church techprints open while the Church is hostile. After betrayal they close for good without VFED.
- Keep titles founders-only for free. The first point of Exaltation is a title (T-184), and a dead founder's favour passes to an heir (T-183).
- Take both players out with one click when the offer is accepted from a caravan, unless we register the dialog with the MP API (T-193).

**Spec and tickets:** [`specs/RELIGION.md`](specs/RELIGION.md) · #53 Exaltation, #123 perks, decrees, betrayal and ending, #135 credit, #137 decrees, #184 title holders, #191 the ending under Multiplayer

#### Religion · The player faith and the founders

**Possible?** Yes.
**Multiplayer?** Yes (spec), condition: every role add runs inside simulation, and play uses one shared player faction. Multiplayer's multifaction mode and two mods' hand-over dialogs need work.

The colony's own faith and its seats, the campaign's floor under it, and how the game knows a founder, requires one, and never gives one away.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| Role seats (founders, preachers, specialists) that unlock during the campaign | Yes | Yes (spec), condition: every add runs in simulation (one two-client run owed) | **A** seats visible from day one, locked with a stated reason until a milestone · XML + C# · Medium (spec recommends)<br>**B** a seat appears when its milestone is reached · Medium<br>**C** the player adds the seat at a fluid reform · Easy (meme gate) / Medium (campaign gate) | [§ Role hierarchy](specs/RELIGION.md#the-player-faiths-role-hierarchy--what-the-role-system-holds-and-how-a-seat-arrives-mid-campaign) |
| A campaign base: forced precepts, and minimums the player may tighten but never loosen | Yes | Yes | **A** a campaign meme forcing a legal set per issue · XML · Easy<br>**B** a campaign player faction def disallowing precepts · XML · Easy (three silent holes)<br>**C** a campaign preset · Easy<br>**D** VFE Tribals' pattern: seed the base, then the player authors the rest · C# · Medium<br>**E** a scenario part that re-applies the base whenever the player leaves the ideology page · Medium<br>**F** a gate at the one precept choke point · Medium<br>**G** a hand-installed ideology file · *not recommended*: a mod cannot ship it. Spec recommends A + D, with B free | [§ A campaign base](specs/RELIGION.md#a-campaign-base-for-the-player-faith--forced-precepts-and-tighten-only-minimums) |
| Founders: told apart from anyone, required at a beat, never given away | Yes. None of it in XML alone | Yes for one shared faction. With work for multifaction; the Rim War and Worksites dialogs are unsynced | Identity: **A1** a founder record stamped at game start · Medium (spec recommends) · A2 pawn kind (an XML selector only) · A3 genes · *not recommended*<br>Required, declared before accepting: **B1** a named founder on the accept gate · **B2** a founder as the accepter · Medium · B3 quest shuttle · Easy · B4 present at the site · Medium<br>Never given away: **C1** our flows skip founders · **C2** quest shuttles refuse them · C3 no sale or gift · **D1/D2** refuse banishment, or never banish "to die" · R1 no release to a flipped faction · **K1–K5** raiders never pick them, never a demanded hand-over, a kidnapped founder stays the player's, a way home, no raid kidnaps · Medium. C4 and K6 are *not recommended* (silent no-ops) | [§ Founders](specs/RELIGION.md#founders--who-they-are-beats-that-require-them-flows-that-refuse-them) |

**What the story can do with it**
- Grow the institution with the colony. Seats can appear as promises (visible, locked, with their reason), as revelations, or at the player's reform.
- Hold a campaign floor under the faith. Tolerance of other faiths, for example, can be pinned to a strict set the player may tighten.
- Name a founder, or both, as required before the player accepts. The acceptance gate states it.
- Fence founders out of lending, revolt contributions, sale, banishment deaths and raiders' kidnap choice. A kidnapped founder can be kept recoverable.

**What it cannot do**
- Give a pawn more than one role. Plain multi-holder roles cap at two per ideology in the editor and at reform.
- Separate a tailor from an armourer by stat, since both share one work-speed stat, without C#.
- Tell a founder apart by genes or pawn kind. Converts share the xenotype, and pawn kind changes on joining.
- Stop vanilla banishment killing a downed founder for good (T-182). A kidnap vetoed at the wrong seam orphans the pawn (T-181). Map closure kidnaps whoever is left, and no selection seam reaches it.

**Spec and tickets:** [`specs/RELIGION.md`](specs/RELIGION.md) · #114 role architecture (#116 catalogue), #140 campaign base, #134 / #183 founders

#### Religion · The Schism, revolt and changing faiths

**Possible?** Yes, except a revolt splitting off a new lasting faction, which is forbidden.
**Multiplayer?** With work. None of the Schism's writes are synced by Multiplayer, and a revolt's generation must stay in synced context. Faith changes are Yes (spec), condition: they fire from the tick or a quest signal, not a player button.

How the Church's world is remade: faiths that spread and turn, peoples that rise, and the Schism that takes the Church's place.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| An NPC faction's faith changes: the Church's spread (~40 % at Medieval), the Schism turning, a revolt | Yes | Yes (spec), condition: from the tick or a quest signal. With work from a player button | **A** the label moves; existing people keep their faith · Medium (lightest)<br>**B** label and people · Medium<br>**C** a chosen share converts · Medium<br>**D** rewrite the faith in place · *not recommended*: a copy, not the Church's faith. Spec recommends A for the spread, B or C where people turned | [§ An NPC faction's faith changes](specs/RELIGION.md#an-npc-factions-faith-changes) |
| Revolt: a reverent people overthrows a hostile government, with the player | Yes, except a split into a new faction | With work | Shapes: **A** an offered quest · Medium · **B** a comms option · Easy on D2 · **C** started at the settlement by caravan · Medium<br>Decided by: **D** allied rebels fight · **E** draftable rebels join for the quest · Easy–Medium · **F** the garrison turns · **G** a contribution of goods, Influence or pawns · Medium<br>Outcomes: **O1** faith only · **O2** government replaced · **O3** ally · **O4** settlements to another faction · **O5** to the player · **O6** vassal (#120) · **O7** split · *not recommended*: forbidden. Spec recommends A + G, fought through E or F, ending in O3 or O2 + O1 | [§ Revolt](specs/RELIGION.md#revolt) |
| The Schism: revealed at commitment, takes Church ground blow by blow, leaves a hostile remnant, stays an ally | Yes | With work | **A** the Schism supersedes the Church · Medium (spec recommends, with H2)<br>**B** the Church becomes the Schism in place · Hard<br>**C** VFE Deserters as shipped · Easy · *not recommended*: it never reveals the Schism, never moves ground, and its finale ends the game<br>Holding the alliance: **H1** vanilla hysteresis · Easy · **H2** a goodwill-offset worker · Medium · **H3** a stored ally latch · Medium | [§ The Schism](specs/RELIGION.md#the-schism--revealed-taking-the-churchs-ground-allied-for-good) |

**What the story can do with it**
- Spread the Church's faith as a label on governments, as a conversion of whole peoples, or as a share.
- Stage a revolt as an offer or a field action. It can be fought with draftable rebels or a garrison that turns, or bought by contribution, and it can end in anything from a faith change to a sworn faction.
- Reveal the Schism at commitment and hand it Church settlements one plot beat at a time. Leave a hostile remnant the player may finish.
- Hold the successor as an ally that drift never breaks, while attacks still can.

**What it cannot do**
- Unlist a faith that still has believers without silently converting all of them (T-109).
- Give a hidden Schism goodwill before its reveal. A hide armed before a save becomes a reveal after load.
- Defeat the Church by transferring its ground. A fully converted Church stays a landless, undefeated, hostile faction unless the finale defeats or hides it.
- Decline a vanilla offer (dismiss only hides it), or make the Church a revolt target.

**Spec and tickets:** [`specs/RELIGION.md`](specs/RELIGION.md) · #133 NPC faith, #131 revolt, #130 the Schism, #120 vassals

---

### The psychic track

**Possible?** Partly. A founder-only psycaster path is buildable with any of six keys. "Rank comes only from the altar" does not survive Vanilla Psycasts Expanded as shipped until its XP loop is cut or gated, or VPE is dropped.
**Multiplayer?** Yes (spec), condition: locks act on saved per-pawn state inside synced simulation. The settings-only cut (route B) is per-install (T-18), and keys F1 and F5 inherit the founder record's gap under multifaction.

The founders' and disciples' psychic ladder. Psylink rank should come only from the altar's rite. Some VPE psycaster paths only the founders may enter.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| Rank is granted by the altar's rite (first psylink Medieval) | Yes | Unknown (spec silent on this writer) | **A (as specced)** vanilla's psylink comp on the altar, whose linking ritual adds one level. The recipient needs a focus it can use, and no vanilla focus is open to everyone, so a hediff-listed one such as F1's. The rite can gate on the giver's faith and certainty (#49) · XML on the altar def (+ a focus) · Easy (mapped). Focus, rites, counts and costs are #119's | [§ Purpose and scope](specs/PSYCHIC.md#purpose-and-scope) |
| Meditation or cultivation does not raise rank | Partly: not under VPE as shipped | Yes. B needs work (T-18) | **A** drop VPE · Easy<br>**B** VPE's XP setting at zero · Easy · *not recommended as a lock*: it misses three abilities and is per-install<br>**D1** XP to zero · **D2** XP levels a pawn only up to a ceiling the altar writes · **D3** XP buys points, never rank · C# · Medium. Spec recommends D2 + C + I1 | [§ What raises psylink rank](specs/PSYCHIC.md#what-raises-psylink-rank-besides-the-altar) |
| Every other rank writer is closed (neuroformer, anima trees, blinding, title ceremony, XP abilities) | Yes | Yes | **C** close each carrier at its own def · mostly XML; three need C# or the inert-neuroformer lever · Easy / Medium<br>**E** a rank chokepoint gate · Harmony · Medium · a backstop only, because it fails silently for the player | [§ C — close each carrier](specs/PSYCHIC.md#c--close-each-carrier-at-its-own-def) |
| A captured or recruited caster keeps or loses rank | Yes, either | Yes | **I1** strip generated casters from the world · XML · Easy<br>**I2** clamp rank on joining the player · C# · Medium. With neither, rank is kept | [§ I1 / I2](specs/PSYCHIC.md#i1--i2--imported-rank) |
| A psycaster path only the founders may enter | Yes, with every key; it leaks until the path is sealed | Yes (F1, F5: with work under multifaction) | **F1** a founder focus granted by the founder record · XML on A1's C# · Easy once A1 exists (spec: strongest key)<br>**F2** a gene the altar installs · Easy to open, Medium to seal · *not recommended as the key*<br>**F3** `VREA_Transcendent` as shipped · post-transcendence only<br>**F4a/F4b** leave VPE's Archotechist to the Church, or re-key it · XML · Easy<br>**F5** the gate reads the founder record · C# · Medium<br>**F6** a founder backstory category · XML · Easy, no C#. Every route also needs two sealing flags (T-167) | [§ Founder-only path](specs/PSYCHIC.md#a-psycaster-path-only-the-founders-can-take) |
| The Church's own psychics, never at the founders' level | Yes | Unknown (spec silent) | **A (as specced)** caster pawn kinds whose initial level is fixed and independent of titles (census I-b, I-d); which kinds is #119's · XML · Easy (mapped) | [§ census](specs/PSYCHIC.md#available-mechanisms--the-census) · [`RELIGION.md` decision 20](specs/RELIGION.md#outstanding-decisions) |
| Psychic ranks carry names or titles | Yes. XML alone reaches only the tooltip: the psylink row ignores stage labels (T-213) | Yes [I] (display only, or written in simulation) | **A** name-only psylink stages, the name in the health-tab tooltip · XML · Easy · *partial*: the row still reads "level N"<br>**B** relabel the psylink row: "Psylink (Adept)", read from the level so it never drifts · C# · Medium<br>**E** a title ladder on a faction **other than the Church** (a Church rung would overwrite the Church title): a real title in the Bio tab, but it leaves the inspect pane while a Church title is held, and the player can renounce it · C# + XML · Medium<br>**F** the rank as the pawn's epithet, "Aria, Adept", on Transcendence's surface; on a founder it shares the string with the claimed title · C# · Medium | [§ Open questions](specs/PSYCHIC.md#open-questions-1) |

**What the story can do with it**
- Make each rank a rite at the altar, and tell authored breakthroughs as altar rites.
- Keep meditation meaningful as cultivation. Under D2 pawns climb to a ceiling only the altar raises; under D3 meditation buys psycasts, never rank.
- Open a founders-only path from day one (F1), at an altar beat (F2), or as a postgame tier after transcendence (F3).
- Give VPE's "archotech" path to the Church's people (F4a) or take it for the founders (F4b). Under F4b the Church loses its only native path.
- Give the Church psychics at fixed levels that never climb, and decide whether a captured enemy caster keeps its powers.
- Turn the neuroformer into an inert trade good, or an altar reagent in the fiction.

**What it cannot do**
- Separate psycaster level from psylink rank under VPE. They are one number, and every psyfocus gain is XP: meditation, caravans, go-juice, the founders' own deathrest.
- Keep a path locked against psytrainers and psyrings unless the path is sealed (T-167). A lost key parks the path; it never revokes it or refunds points (T-168).
- Keep neuroformers out of quest rewards by tag. A pity timer injects them (T-170), and the vanilla-looking psylink chokepoint is not one (T-169).
- Stop VPE giving a bestowing honoree with no psylink one level, short of C# or holding no ceremonies (R9).
- Use VPE's max-level setting as a cap. It also caps the altar.
- Use genes as founder identity (T-111). Hemosage is open to every convert. Deleting the founder record also closes F1's path.

**Spec and tickets:** [`specs/PSYCHIC.md`](specs/PSYCHIC.md) · #162 the founders-only door, #163 rank writers, #49 willing givers, #31 the power grid, #134 founder identity

---

### Transcendence

**Possible?** Yes. The claimed title, its gate on the final rite, the once-only Administrator scene and three endings are all specced.
**Multiplayer?** Yes (spec, on reading), condition: *Enter*'s action is hosted on an allowed type and both options close the dialog. One dev check is owed for the claim, and Verification 3 for the Administrator. Ending the game for both players together is Unknown until one two-client run (#182); a deferred-exit fallback exists.

The end of a founder's arc: Claim Yourself (a self-authored title), the final rite, the Administrator, and the choice to enter the new reality or stay.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| One saved record per founder that the campaign reads | Yes | Yes | **A (as specced)** a component on a founder-only hediff holding the claimed title, the claim flag, the transcended tick and whether the Administrator was seen. Under `RELIGION.md`'s A1 it is stamped at game start. Alternatives surveyed and rejected · C# + XML · Medium (mapped) | [§ 1 The store](specs/TRANSCENDENCE.md#1-the-store--compfounderrecord) |
| Claim Yourself: the player types the founder's self-authored title, and the final rite waits on it | Yes | Yes (spec), condition: Multiplayer's automatic registration holds (one dev check) | **A (as specced)** a rename-style dialog opened from a gizmo on the founder or from the altar, with every effect inside the synced write. The altar refuses "X has not claimed a title" until then · C# · Medium (mapped). One-way or re-typeable: both trivial, #119 | [§ 2](specs/TRANSCENDENCE.md#2-the-epithet--one-synced-write-no-multiplayer-code-of-ours) · [§ 3](specs/TRANSCENDENCE.md#3-the-gate) |
| The claimed title is seen in play | Yes. A reaches the inspect-pane header, the Bio tab and grammar; the colonist bar and map label need N or C | Yes | **A (as specced)** vanilla's per-pawn title string, shown as "Name, Title" · none<br>**N** the claim becomes the founder's nickname: on the bar and map label with no patch, but it is then their name in every letter and log · C# inside A's setter · Easy<br>**C** a display-only postfix, founders only: on the bar and map label and nowhere else; C′ draws a second line or tooltip under the portrait · C# · Medium. The bar's name slot fits ~12–14 characters; a long claim shows whole only on C′. A is vanilla's own rename-window title, already synced by Multiplayer<br>**R** a royal title awarded by the player's own faction: vanilla accepts it and it sits beside the Church title, but typed text means one def per founder relabelled on load; a Bio-tab chip, not the bar · XML + C# · Medium | [§ 5](specs/TRANSCENDENCE.md#5-where-the-player-sees-it) |
| The Administrator, once per founder, offering Enter or Stay | Yes | Yes (spec, on reading), condition: *Enter*'s action is hosted on the altar's comp, *Stay* carries none, and both close the dialog (T-97). Run: Verification 3 | **A (as specced)** a vanilla dialogue replayed to both players. *Stay* closes it and changes nothing. A `ChoiceLetter` was ruled out (options unsynced) · C# · Medium (mapped) | [§ 4](specs/TRANSCENDENCE.md#4-the-administrator-and-the-choice) |
| Enter the new reality: credits, or the game ends | Yes | A, B: Yes · C: Unknown until run · C′: [I] | **A** credits, then play continues · Medium<br>**B** credits, then each player exits to the menu on their own · Medium<br>**C** vanilla's game-over dialog; one click ends it for both · Medium<br>**C′** C with the exit deferred · Medium · fallback. Spec recommends A + C; A alone if the second founder's arc should stay open | [§ Ending the game under Multiplayer](specs/TRANSCENDENCE.md#ending-the-game-under-multiplayer) |

**What the story can do with it**
- Let the player name the founder in their own words. The name rides with the founder in the inspect pane and in any letter or dialogue we write.
- Make the claim, an act of Self, the key to the final rite. A ritual or quest beat may open the same dialog (unverified).
- Keep a Church title beside the epithet, or strip it at the claim (VFED shows the shape).
- Meet the Administrator once per founder. *Stay* keeps the founder transcendent and playing.
- Let the two founders transcend separately: credits then play (A) leaves the second arc open.
- End the campaign with credits only, credits then the menu, or one shared game-over.

**What it cannot do**
- Show the epithet on the colonist bar or the in-world map label on route A alone. The nickname (N) or a display patch (C) puts it there; the bar's name slot holds about a dozen characters.
- Accept more than 27 characters through the vanilla dialog without overriding its cap.
- Re-offer the choice. The Administrator appears once, with no standing re-offer at the altar.
- Pause the other player's colony while a founder types or while credits roll under Multiplayer (T-53).
- End both players' games together with route B. The host skipping the credits closes the server on the other player mid-roll.
- Show the game-over dialog to a player looking at another map, or end anything through `GameEnder` (T-176).
- Survive dropping a comp from the record hediff (T-34), or building *Enter* without closing the dialog (T-97, which re-offers the ending forever). No field here tracks founder psylink progression; the capability is in `PSYCHIC.md` (#31).

**Spec and tickets:** [`specs/TRANSCENDENCE.md`](specs/TRANSCENDENCE.md) · #50 (absorbing #79) title and encounter state, #182 ending the game, #134 founder identity, #162 / #163 founder psylinks, #48 the final authored scene

---

## Politics

### Faction politics

**Possible?** Yes, with one named exception: no peace with a permanent enemy (Glitterites, Archons) while our own `permanentEnemy` flag stands. The spec marks that one part Partly. It is not a requirement clause failing, because requirements/TERRITORY puts the Glitterites *"outside diplomacy"*, and the spec records that both defs' comments state the flag keeps them out of diplomacy (§ Ending a losing war, route L).
**Multiplayer?** Yes for the ripple, the demand, the standing gate, caravan route B and the ways out of a war. With work for caravan route A (a saved cooldown), for any comms-console action of ours (a whitelisted host type, and a fixed option order, T-82) and for route L's mid-campaign def swap. No for caravan route C and for RimPacts. Two-client checks are owed on #16.

How factions come to care about each other and about the colony. One act can reach a faction's allies. A faction's demand carries a deadline and a price, and so does refusing it. Standing unlocks things the player can see locked in advance. Caravans meet the settlements they pass, and a losing war has ways out.

Not in this card: the planetary outcome snapshot, which [`specs/ORBIT.md`](specs/ORBIT.md) § 5 stores (predicates: #100); Reverence, which is [`specs/RELIGION.md`](specs/RELIGION.md)'s; and the ally-aid battle, which is on the Territory card.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| A single act moves more than one faction: wronging one (kidnap, harm, kill, strip, fouling ground near a settlement) reaches its allies | Yes. The alliance half fires only on edges we seed (T-100). The "fouling ground" trigger is part of A, verified but not priced | Yes (spec), condition: no `Rand` in the ripple path, no settings read (T-18), deterministic iteration, no cached ally set (T-20) | **A (as specced)**. Seed designed NPC↔NPC edges once at game start. Postfix the kidnap, harm, kill and strip act hooks, and author a trigger for fouling ground, reusing vanilla's settlement-distance maths. Write player↔X through VEF's delayed goodwill queue, whose letter names the faction and the amount · ours + VEF · XML + C# + 4 patches · Medium *(mapped)* | [§ The build](specs/POLITICS.md#the-build) |
| A demand: a specific ask, a deadline, a consequence stated before the player answers, and serving one faction costs its rival | Yes | Yes. Either founder accepts or dismisses for both | **A (as specced)**. An XML quest copied from `Script_TradeRequest`, with the countdown and alert built in. `QuestNode_ChangeFactionGoodwill` moves any second faction and shows the reason · vanilla · XML · Easy *(mapped)* | [§ The faction demand](specs/POLITICS.md#the-faction-demand) |
| Asks pointed at what the colony could build, including a specialist on loan in any era, an escort or a threat to the asker's travellers cleared, and a prisoner released, each with fulfilment and failure detected | Yes. A *threatened* world-map route is cut by #174, so the ask was reworded (#198). Vanilla's loan collects by shuttle (Empire only) and returns by drop pod | Yes; With work for the settlement hand-over comp that L1, E3 and P2 (b) share; P2 (a) is Yes (one `SyncMethod`, the shape MP already registers for `TradeRequestComp.Fulfill`) | **A**: silver, a delivery to a named tile, or a colonist lent for a duration · vanilla · XML · Easy *(mapped)*<br>**B**: a colonist with skill N (a new accept requirement) · C# · Medium *(mapped)*<br>**C**: an embargo on trading with a rival (a postfix plus a listener) · patch · Medium *(mapped)*<br>Loan: **L0** vanilla `Script_PawnLend`, Industrial+ askers only · XML · Easy · **L1** a caravan hands the specialist over at the asker's settlement, and they walk home · C# + XML · Medium · **L2** the same without the hand-over · C# · Medium. Both subclass the vanilla loan part rather than replace it<br>Route: **E1** clear a bandit camp raiding the asker's caravans (`Script_BanditCamp`) · XML · Easy · **E2** host the asker's refugees · XML · Easy · **E3** escort the asker's people by caravan · C# · Medium<br>Prisoner: **P1** vanilla `Released` / `Banished` signals · XML · Easy · **P2** handed back in person by caravan · patch or C# · Medium | [§ 3 Asks](specs/POLITICS.md#3-asks-pointed-at-capability) · [§ 3a](specs/POLITICS.md#3a-a-loan-without-pods-a-protected-route-a-prisoner-released) |
| Refusal is viable and not free: the telegraphed consequence fires, and refusing can earn standing with the refused faction's enemies | Yes. Refusing means letting the offer expire | Yes | **A (as specced)**. A refusal part fires on expiry, applying goodwill changes to any factions plus an optional retaliation quest · ours · C# · Medium *(mapped)*. The XML field `failedOrExpiredHistoryEvent` was rejected because it carries no faction<br>Consequence raid: an `IncidentDef` on VEF's special raid worker, sized by PRESSURE · XML · Easy *(mapped)*. The seam that fires it from a quest is [I]<br>**B**: VFE Medieval 2's raid-on-fail node · *not recommended as primary*: its raid size escapes PRESSURE. It is the fallback for a site-shaped demand whose failure raids home, not for the ally-aid battle | [§ 1 Refusal](specs/POLITICS.md#1-refusal--questpart_demandrefused--questnode_demandconsequence), [§ 4 Raid](specs/POLITICS.md#4-the-refusal-raid--what-fires-it-not-how-big-it-is) |
| Paired demands from rivals: serving one fails the other, and the player sees both prices before choosing | Yes | Yes (the choice is synced as shipped) | **A (as specced)**. One quest with two branches on `QuestPart_Choice`: serve A (+A, −B) or serve B (+B, −A). Our node is about 35 lines · C# · Medium *(mapped)*. Two quests plus `ExclusiveGroup` was rejected, because the engine forbids signals between quests. [I]: a branch with no reward may draw empty | [§ 2 Paired](specs/POLITICS.md#2-paired-rival-demands--questnode_rivaldemands-over-questpart_choice) |
| A manageable number of live diplomatic situations | Yes | Yes, but the cap does nothing for demands granted through VEF chains (T-71) | **A (as specced)**. A cap node counting pending demand offers, with the number held in a Def · C# · Medium *(mapped)*. XML alone gives only partial, per-script caps and no category cap | [§ 5 Budget](specs/POLITICS.md#5-the-notification-budget--questnode_demandbudget) |
| Standing buys relationships, and the threshold shows before it is reached: a locked row with its number | Yes | Yes. Disable a locked option, never omit it (T-82). Our enabled comms actions need a whitelisted host type | **A**: a quest offer that arrives locked, with "need N <axis>, currently M" in its requirement box. The same gate reads Goodwill, Reverence or Exaltation · C# · Medium *(mapped)*<br>**B**: a greyed comms option naming the threshold and the current value · C# · Medium *(mapped)*<br>**C**: a rite gizmo greyed with its reason · XML + small C# · Medium *(mapped)*<br>**D**: a building greyed in the Architect menu · patch · Medium *(mapped)*<br>A `RoyalTitlePermitDef` worker is not selected: it is title-gated and not on the MP whitelist. The spec routes research, trade and buildings through A–C | [§ Standing as a content gate](specs/POLITICS.md#standing-as-a-content-gate) |
| Standing buys candour: who a faction hates (and is allied to) is withheld until earned, and revealed per faction | Yes. Vanilla shows NPC↔NPC relations in one standing place, the Factions tab's "Enemy of" strip, and shows hostility only; it never displays an alliance | Yes. Every display route reads synced state; a stored record needs synced writes. Faction Customizer's editor writes relations unsynced | Knowledge: **RK-1** derived from a standing threshold, nothing stored, lost if standing falls · Easy once the gate's resolver exists · **RK-2** a per-faction record, kept for good · Medium · **RK-3** a per-pair record, so a quest or battle reveals one enmity · Medium<br>Display: **RD-1** the strip filtered to earned edges (one predicate postfix) · **RD-2** a locked row, "revealed at +40" · **RD-3** alliances shown · **RD-4** an info-card line · **RD-5** asked on the comms console, not in the Neolithic · **RD-7** our own ledger tab · **RD-8** no sheet, learned only from text · Medium · **RD-6** a letter at the reveal · Easy on RK-2<br>Spec recommends RK-2 (+ RK-3), RD-1 + RD-2, with event surfaces counted as reveals | [§ Withholding who a faction hates](specs/POLITICS.md#withholding-who-a-faction-hates) |
| A caravan passing near a settlement meets its faction: attacked if hostile, offered trade otherwise | Yes, with C#. No XML route (T-118) | A: With work. B: Yes [I]. C: No | **A**: a meeting on every pass, with a per-settlement cooldown · ours (FT&V donor) · C# · Medium<br>**B**: storyteller-fired proximity incidents, with frequency per biome; also reaches parked and vehicle caravans, and a small quiet caravan slips past more often · vanilla + ours · C# + XML · Medium<br>**C**: Faction Territories as shipped · XML · Easy · *not recommended*: declined on #8, settings are client-local, cooldowns are not saved, no MP Compat<br>The spec recommends B, or A if every pass must meet someone | [§ Settlements meet passing caravans](specs/POLITICS.md#settlements-meet-passing-caravans) |
| A lost war has a way back: peace, one payment, a tribute schedule, standing obligations | Yes against any faction that has goodwill (the spec's sub-verdict is Partly; see the next row) | Yes. With work for a comms "sue for peace" option | **P1** gifts and peace talks, as shipped · Easy<br>**P2** peace terms the colony asks for · XML + small C# · Easy–Medium<br>**O1** reparations as a demand · Easy, or ceding a holding · Medium<br>**S1** tribute on a clock, where a missed payment reopens the war at once · Medium<br>**B1** an overlord's levies, loans, embargoes and battle calls · Medium<br>**R** vanilla ransom · Easy<br>RimPacts as the carrier · *not recommended*: MP No, T-18<br>The spec recommends P1 as the floor, P2 + O1 as the authored beat and S1 as the one real build | [§ Ending a losing war](specs/POLITICS.md#ending-a-losing-war) |
| A war with the Glitterites or Archons can be eased or ended | Partly. Eased only, unless our flag is lifted | Yes. L's mid-campaign swap is With work (one synced command) | **E1** a bought truce: fewer raids or none, while still hostile (PRESSURE routes C and G) · Medium<br>**L** lift `permanentEnemy`, after which P1–B1 apply. Either a def edit (every save) or a mid-campaign swap as a story beat. The Archons must also be revealed (T-116) · Easy / Medium · it reverses a deliberate design | [§ Ending a losing war](specs/POLITICS.md#ending-a-losing-war) |

**What the story can do with it**
- Put two rivals' demands in one letter. The player sees *serve the Reach: +Reach, −Clans* beside the opposite branch and picks one.
- Have any demand name a third faction whose goodwill moves when it resolves, with a message naming who changed and why.
- Ask for something pointed: supplies delivered to a tile, a colonist lent for 30 days (walked there and back before pods exist), someone with Medicine 10, an embargo on a rival, a bandit camp cleared, refugees hosted, or a prisoner released.
- Make candour a reward. Who a faction hates is hidden until standing, a quest, a comms question or a battle earns it, and a locked row says what earns it.
- Fire a retaliation raid, or a follow-up quest, from the refused faction when an offer lapses. The refusal can also win standing with that faction's enemies.
- Spread gossip. Once the seed table says who loves whom, kidnapping one faction's pawn reaches its friends over the following day, as one letter per faction.
- Hang a visible carrot on a quest, a comms option or a rite: *need 60 Reverence with the Reach (now 42)*. The gate can check one axis and charge another, the way vanilla's comms asks charge Goodwill.
- Stage road encounters: a friendly settlement offers trade, a hostile one ambushes the caravan or demands a toll.
- Lose a war: sue for peace, pay reparations or cede a holding, or become a tributary whose missed payment is war the same day.

**What it cannot do**
- NPC factions are never allied in a fresh world. The alliance ripple does nothing until someone authors the seed table (T-100), and seeded edges never drift on their own.
- Goodwill does not land as written:
  - A change toward a faction's natural goodwill lands 25% larger, and Reverence scaling moves it too (#160 route A).
  - A write against a permanent enemy, a quest-locked pair or a faction at its cap fails silently.
  - A *positive* change fails silently during an assault on that faction's settlement (T-110).

  Church↔Glitterites and Church↔Free Companies can never change.
- Ally and Hostile are latches, not numbers. A faction turns hostile at −75 and becomes neutral again only at 0, so a gate on "Ally" is not a gate on "goodwill ≥ 75".
- An offer cannot be declined; refusal means letting it expire. The stated consequence is prose, and nothing keeps it in sync with what actually fires.
- A demand cannot ask the player to defend a world-map route; routes are never threatened (#174). A prisoner gifted back by caravan arrives factionless unless patched (T-196), and a release by caravan never sends `Released` (T-197). A demand copied from vanilla's loan (L0) pays at hand-over and scores all lent colonists dying as a success (T-198).
- Relations between NPC factions change silently, with no letter (T-199). NPC factions fighting on the colony's map reveal their enmity, and that cannot be withheld.
- Research and trader stock cannot be locked behind standing on their own screens. Reach them through a quest, a dialogue option or a rite.
- Caravan meetings have gaps:
  - Route A misses parked caravans, and reaches Vehicle Framework caravans only with a second patch (T-117).
  - Route B cannot guarantee a meeting, and skips biomes missing from its list (T-119).
  - Aircraft in flight meet nobody, and no encounter fires on the settlement's own tile.
  - Vanilla's random ambushes still fire beside friendly settlements unless they are suppressed.
- "Losing" means nothing to the engine; we write the predicate. There is no subordinate relation, only Hostile, Neutral and Ally. Vanilla has no trade price that follows goodwill; that takes a patch (TERRITORY OS-5).

**Spec and tickets:** [`specs/POLITICS.md`](specs/POLITICS.md) · #90 ripple, #91 demand, #93 standing gate, #136 caravan encounters, #189 losing war, #192 demand asks, #193 relation candour (Reverence scaling: #160, #176)

---

### Territory

**Possible?** Yes. Every clause has a verified route, though nothing on disk delivers any tier as it ships. The exception is a settlement due to change hands at the era advance while the players' gravship is parked on it. No route satisfies both ERA.md's single act and #118's "never while its map is loaded". GV-1 stops the case arising; GV-7 waits it out.
**Multiplayer?** With work. Every player act must be a synced commit: a float-menu option on a world object, or a quest accept or choice. Never a gizmo, a dialog or a modded letter (T-80, T-96). Every roll is seeded (§0 P4). VEF outposts need §2's harness unless OR-5 is taken. RimPacts and FT&V as shipped are No.

Everything the colony holds beyond its own map, in three tiers. **Outposts** cost the colony's own people. **Holdings** are settlements taken by force that then pay goods. **Sworn factions** give themselves and owe services. The same world-site machinery carries POLITICS' ally-aid battle.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| An ally under attack names a tile and a short window: attend and it is a real fight, decline and it resolves without the player and reports the outcome | Yes, in two shapes: over the ally's settlement (Build B), or on an ally-owned site at a tile near it (AS) | Build B: Yes (spec), condition: created from the world tick or a synced incident, the roll seeded (§0 P4), attendance a float-menu option (§0 P5) [I]. AS: Yes [I]: quest accept is synced, attendance is vanilla's visit-site option, the roll is P4 | **Build B (as specced)**. Our timed world object over the ally's settlement, with *Join fight* and a seeded winner when nobody attends. The winner can be predicted from the object's fields · ours, copying FT&V's invasions · C# · Hard *(mapped)*<br>**AS-1** an auto-accepted quest places an ally-owned site; attend and it is a three-way fight, stay home and a P4 roll part reports the outcome, with goodwill and letter in XML · XML + C# · Medium<br>**AS-2** AS-1 behind #91's offer window; expiry reaches the same roll · Medium<br>**AS-3** Worksites Expanded as the carrier (`Worksite_DefendAlly`) · Hard: it picks its own attacker, rolls unseeded, and its caravan gizmo is unsynced · its value is as the donor<br>**AS-4** a live NPC-only site map · Hard · *not recommended*<br>VFE Medieval 2's raid-on-fail is not a route: its raiders land on a player map. Build A (ship FT&V) was declined on #8 and is out of scope (#35) | [§ 1 Ally-aid battle](specs/TERRITORY.md#1-the-ally-aid-battle--build-it-against-a-read-reference) · [§ 1a The site shape](specs/TERRITORY.md#1a-the-site-shape--the-battle-on-an-ally-owned-site-at-a-tile-e-queste-site) |
| An outpost costs materials, silver and people, and its return justifies them | Yes | With work (§2 harness) | Cost:<br>**OC-C1** restat `CostToMake` · XML · Easy<br>**OC-C2** cost scaled by era or by outposts held · C# · Medium<br>**OC-C3** build debt: found now, pay from home, no yield until paid · Medium<br>**OC-N3** a hard cap, only if one is ever wanted · Medium<br>Yield:<br>**OC-Y1** XML restat (7 of 13 VOE defs) · Easy<br>**OC-Y2** C# for the rest (Scavenging and Town ignore XML) · Medium<br>**OC-Y3** yield by pawn kind · Medium<br>OC-N1 and OC-N2 were retired by #175 | [§ What an outpost costs](specs/TERRITORY.md#what-an-outpost-costs--materials-silver-and-committed-pawns), [§ 2](specs/TERRITORY.md#2-outposts-with-real-yields--the-engine-ships-inside-vef) |
| Committed pawns are consumed and the outpost runs on its own; the build can require or forbid a kind of pawn | Yes | With work (§2 harness); OR-5 Yes | **OR-1** ghost staff: they stay, but every control is removed · Medium<br>**OR-2** frozen staff, so the yield stays fixed at what was sent · Medium<br>**OR-3** a real sale with a flat yield · Medium<br>**OR-4** a real sale, with a snapshot of who was sold driving the yield · Medium–Hard<br>**OR-5** our own map-less world object · Hard<br>The kind rule is a filter in the synced founding commit. The spec recommends OR-2 + RU-1, or OR-5 + RU-2 | [§ Consumes its pawns](specs/TERRITORY.md#an-outpost-that-consumes-its-pawns-and-runs-on-its-own) |
| Upkeep arrives as an event. The required event is an attack, and an undefended outpost is destroyed into a ruin that can be looted and rebuilt | Yes. Nothing ships it; no corpus mod leaves a ruin | With work. OU-A2 is Yes [I]; RU-2 and RU-4 are Yes | Attack:<br>**OU-A2** a quest spawns a hostile site near the outpost · XML + C# · Medium (the spec's pick)<br>**OU-A1**/**OU-A3** a timed attack at the outpost itself · Hard<br>**OU-N1**/**OU-N2** a letter, or a declinable quest · Medium<br>**OU-D1–D4** delays and stalls (D3 and D4 only under OR-1)<br>**OU-T1–T3** variation per outpost type · Easy–Medium<br>**OU-A4** a staff ambush · *not recommended*: the player cannot decline it<br>Ruin:<br>**RU-1** the outpost is its own ruin · Medium<br>**RU-2** our ruin object, with *Loot* and *Rebuild* · Medium<br>**RU-3** a loot site the caravan walks · Medium<br>**RU-4** vanilla's dated marker, no loot · Easy<br>**RU-5** re-found on the same tile at full price · Easy | [§ Upkeep as events](specs/TERRITORY.md#an-outposts-upkeep-arrives-as-events-not-as-a-management-surface), [§ Consumes its pawns](specs/TERRITORY.md#an-outpost-that-consumes-its-pawns-and-runs-on-its-own) |
| Taking a settlement is hard: real defenses and real defenders, harder at a higher tier | Yes. Vanilla alone does not get there | With work (T-33, T-143, T-120) | **SM-1** vanilla with pawn kinds re-authored · XML · Easy · not hard enough alone<br>**SM-2** generated walled layouts per faction · XML · Easy<br>**SM-3** hand-built castles and forts with authored defenders · XML · Easy<br>**SM-4** garrison size on a tier curve, which can carry losses between visits · C# · Medium<br>**SM-5** a named citadel · Medium<br>**SM-6** vanilla's layout engine on the surface · Medium<br>**SM-7** defenders who call reinforcements · Medium<br>The spec recommends SM-3/SM-2 + SM-4, and SM-5 only for places the plot names | [§ Taking a settlement](specs/TERRITORY.md#taking-a-settlement-must-be-hard--a-defended-map-and-real-defenders) |
| A taken settlement becomes the colony's holding: owed, not operated | Yes. Nothing delivers it as shipped, and XML alone gets none of it | With work | **R1** a player-held world object that remembers its parent faction · Medium<br>**R2** a marked settlement that stays in its faction · Medium<br>**R4** a faction-level record, for sworn factions and the Schism's successor · Medium<br>**R5** vanilla ally machinery · Easy · partial<br>**R0 / R3** VFE Empire tithes: the Church's perk, not a holding; R3 *not recommended*<br>**R6 / R7** RimPacts or FT&V as shipped · MP No · *not recommended*<br>The spec recommends R1 (R2 if the settlement should stay in its faction), with R4 and R5 | [§ 3 Vassals](specs/TERRITORY.md#3-vassals--every-shape-by-route) |
| A rebuild debt is owed first. Then the holding pays what it is known for, on a schedule, delivered to wherever home is, including the gravship | Yes | Yes for shipped carriers; With work for ours | **P1** VFE Empire's tithe engine, repointed: payload, cadence, accrual, a readable due date · Medium · Yes, with one ordering hazard<br>**P2** VEF's five delivery methods · Medium · With work (T-18)<br>**P3** a drop the player asks for · Easy–Medium (T-137)<br>**P4** a standing debt on the tile, paid by a visiting caravan · Easy–Medium<br>**P6** unprompted sends · Easy<br>**P5** a credit menu · *ruled out by the requirement*: there is no holding currency<br>The spec recommends P1 + P2 + P4 | [§ What a holding pays](specs/TERRITORY.md#what-a-holding-pays-and-how-the-player-takes-it) |
| A settlement's specialty (the faction's and its own) is learned by going | Yes, for both layers | Yes for derived and XML routes; With work for stored rolls and reveals | Faction:<br>**SF-1** vanilla already names it · Easy<br>**SF-2** declared on the faction def · XML · Easy<br>**SF-3** hidden until first contact · Medium<br>Settlement:<br>**SS-1** several trade profiles per faction · XML · Easy<br>**SS-2** derived from the tile and faction · Medium<br>**SS-3** stored per tile, the only form unmoved by conquest, era or balance edits · Medium<br>**SS-5** no settlement layer · Easy<br>**SS-4** settlement def variants · *not recommended*<br>Reveal:<br>**SV-1** visit, **SV-3** a caravan nearby, **SV-4** a scouting outpost (T-18), **SV-5** first contact · Medium<br>**SV-2** trade · Easy–Medium<br>**SV-6** public at once · *fails the requirement*<br>The spec recommends SF-1 + SF-2, SS-3 keyed on the tile, and SV-1 + SV-2 + SV-3, with SV-4 as the scouting outpost's job | [§ Specialty](specs/TERRITORY.md#a-settlements-specialty-and-learning-it-before-you-commit) |
| What has been learned is shown, and what vanilla would leak early is withheld | Yes. The Factions tab can carry only the faction's layer | Yes, with no work beyond #165's | **SD-0** suppress *Show sellable items* until learned · Medium · *required whatever else is taken*<br>**SD-1–SD-11** inspect line, settlement tab, attack menu, info card, map badge, map mode (needs MMF), world search, a campaign tab of our own, Factions tab, reveal letter, Alt-hover line · mostly Medium<br>**SW-1** tier-neutral faction identity · XML · Easy<br>**SW-2**/**SW-4** per-settlement art, or removing WTL's tier line · Medium<br>**SW-3** gated faction rows · Medium–Hard<br>**SW-5** RimPacts' tier text · *not recommended*<br>**SP-1** strip "Trading here requires title" until learned · Medium<br>**SP-2** · *not recommended*<br>**SP-3** deletes the rule rather than withholding it | [§ Showing what is learned](specs/TERRITORY.md#showing-what-the-player-has-learned-about-a-settlement) |
| Paying advances a holding one era, never past the colony's, and the era advance never touches it | Yes. It holds by construction only under R1 + TR-1 | Yes, with the usual work (the commit is a float-menu option, T-80) | **TR-1** tier stored at conquest · Medium (Easy on top of R1/R2)<br>**TR-2** tier read from the former faction · *not recommended*: it climbs for free<br>**TR-3** tier in the def · Medium<br>**TR-4** advance by transfer, R2 only · Medium–Hard<br>Price: a P4 debt at the target tier. Gates: TG-1 colony era, TG-2 parent climbed, TG-3 research, TG-4 price only<br>The spec recommends R1 + TR-1 + P4 + TG-1 | [§ Advance a holding](specs/TERRITORY.md#paying-to-advance-a-holding-to-a-later-era) |
| A holding ends (released, retaken, destroyed or thrown off) as a moment the player acts on, forfeit and never a roll; whatever it still owes is cancelled | Yes | With work | Release: **H-L1–H-L4** · Medium. Only **H-L2** with a seeded random recipient conforms to #174; H-L1, H-L3 and H-L4 do not as written<br>Retaken:<br>**H-T2** "return it or we come" · Medium · Yes<br>**H-T1** a timed attack at the holding · Medium on top of §1, Hard alone<br>**H-T4** strike the staging camp · Medium<br>**H-T3** counter-attack waves · Hard<br>**H-T6** repudiation (R2) · Medium<br>The attacker-takes outcome of H-T1/H-T2 does not conform to #174 as written<br>**H-T5** · *not recommended*: its donor code never runs<br>Destroyed: **H-D1** (does not conform as written), **H-D2**<br>Thrown off: **H-O1** · Medium–Hard; **H-O2** RimPacts · *not recommended*<br>**H-V** VFE Empire's *Release all* (R0/R3 only)<br>The spec recommends H-L2 for release, H-T2 → H-T1 ending in forfeit for loss, H-T4 for destruction, and H-O1 for throwing off | [§ How a holding ends](specs/TERRITORY.md#how-a-holding-ends--released-retaken-destroyed) |
| A settlement never changes hands while its map is loaded, and caravans already on the way are handled | Yes, except a parked player gravship (see Possible above) | Yes, except MO-F2 (With work) and GV-6 (No) | Map loaded:<br>**MO-F1** eject everyone instantly, then transfer: the only eject branch that fits the era advance · Medium<br>**MO-W1** hold until the map closes (Schism, revolt, conquest) · Medium<br>**MO-W2**/**W3**/**F2**/**F3** · Medium<br>**MO-A** transfer anyway, **MO-S** skip · *not recommended*<br>Parked gravship:<br>**GV-1** refuse landings on NPC settlements · Medium<br>**GV-3 + GV-5** transfer with the map open, which breaks #118<br>**GV-7** hold the advance until the ship leaves<br>**GV-2** skip that settlement, which breaks ERA.md; **GV-4** defer, which is a forbidden delay; **GV-6** · *not recommended*<br>Caravans on the way:<br>**CF-B** re-check and abort, with a letter · Medium, plus **CF-C** rebind, **CF-E** a warning line, **CF-G** guard attack orders · Medium<br>**CF-F** a scene at the gate · Medium–Hard<br>**CF-A** vanilla · *not recommended alone*: attack orders land on allies<br>**CF-D** · *not for the advance* | [§ Map loaded](specs/TERRITORY.md#a-settlement-changing-hands-while-a-player-map-on-it-is-loaded), [§ Caravan en route](specs/TERRITORY.md#a-caravan-en-route-when-its-destination-changes-hands) |
| A sworn faction owes services, not goods, and the player can ask as well as receive | Yes | Yes for vanilla carriers; With work for ours (T-82, T-137); No for RimPacts | **OS-1** vanilla comms asks: trader, orbital trader, military aid · XML · Easy<br>**OS-2** titleless permits granted by Reverence band: troops, lent labourers, goods drops, a shuttle · Medium<br>**OS-3** our gated comms options · Medium<br>**OS-4** a service shelf priced in Goodwill · Medium<br>**OS-5** always-on boons; prices may follow Goodwill · Medium<br>**OS-6**/**OS-7** on the faction's own schedule, or a fixed one · Medium<br>**OS-8** people lent or offered, never dumped · Easy–Medium<br>**OS-9** asked in person by a caravan · Medium<br>**OS-10** a signal fire the colony builds · Easy–Medium<br>RimPacts · *not recommended*. The routes compose | [§ Sworn faction](specs/TERRITORY.md#a-sworn-faction-owes-services--every-form-that-can-take) |

**What the story can do with it**
- *Bob runs the outpost now.* The colony sells named pawns to a place and gets goods in kind. Deliveries come by pack animal before pods exist, and follow the gravship home without extra work. A scouting outpost also reveals the settlements around it.
- A raiders' camp appears near an outpost with a deadline. Break it, or the outpost falls into a ruin with loot, which the colony can rebuild for a price.
- Make one named fortress a hand-built citadel with authored defenders at any tier, while the rest of that faction's bases are generated. Defenders can call reinforcements, and killing the caller stops them.
- A holding pays in character: a slaver tribe sends newly generated slaves, an armourer sends arms. The debt and the next due date show on the tile.
- The colony learns a place by going there: visiting, trading, passing nearby or scouting. A letter marks the moment. The fact then shows on hover, in a tab, in world search and in the Attack menu.
- Endings are beats. *Return it or we come*, then a battle at the holding, forfeit if ignored. A province's grievances can be answered one event at a time.
- A sworn people answers a signal fire in the Neolithic and lends a specialist who leaves when the term ends. It offers help on its own schedule, and opens more at higher Reverence bands. Goodwill pays; Reverence opens.
- Call the player to an ally's battle at a tile: fight alongside, or hear who won. The site shape puts it on a tile near the ally, at Medium rather than Build B's Hard.

**What it cannot do**
- A settlement's map does not persist. The garrison returns at full strength, so an assault is won in one sitting (SM-4 can carry losses; #174 does not require it). Vanilla garrisons are 1150–1600 points at any tier, and no generator places turrets or mortars below Industrial (T-30).
- A holding is never a map the player runs. Under R1 it has no people.
- No faction can be created mid-game (T-07), and no settlement can be left factionless. A lost or released holding passes to a randomly drawn existing faction (#174). Handing it back to its parent, a buy-back, the victor or the attacker does not conform as written.
- A settlement's only identity that survives replacement is its tile; conquest or recreation mints a new ID (T-140).
- The era advance silently re-tiers holdings unless the tier is stored under R1 (T-145). Never write `FactionDef.techLevel` (T-11).
- Taking a faction's last settlement defeats it. It then takes no goodwill and is never drawn by the storyteller, though an authored raid that names it still fires.
- A transfer with a map open fake-defeats the settlement (T-179), or loses or kidnaps the party. A parked gravship's takeoff erases the NPC settlement (T-180). An attack order is not re-checked against a new owner, so it can land on an ally (T-138).
- A bare destroy drops an outpost's pawns and goods (T-151). An outpost adopts any map made on its tile (T-150).
- There is no vassal relation in the engine. A sworn faction is held at Ally, and Ally is a latch. There are no titles but the Church's, and a titleless permit is permanent until we remove it (T-146). Comms military aid refuses factions below Industrial. Orbit refuses any surface faction whose `arrivalLayerWhitelist` does not list it (T-48).
- Any caravan arrival action of ours (attend, release, loot) must override `StillValid`, which defaults to true (T-139).
- An aid site's battle is simulated only while the player is there; unattended, the outcome is always a roll. Only Build B puts the ally's settlement itself at stake. An ally-owned site reports its enemies defeated before any arrive (T-187), raids a caravan with a substituted faction on its default timer (T-188), and a vanilla raid will not carry a non-hostile attacker (T-189).

**Spec and tickets:** [`specs/TERRITORY.md`](specs/TERRITORY.md) · #81 outposts, #92 ally-aid battle, #120 vassals, #152 caravan en route, #164 taking a settlement, #165 specialty, #166 holding payment, #167 advancing a holding, #168 sworn-faction services, #170 outpost cost, #171 outpost upkeep, #172 holding endings, #178 showing what is learned, #179 consumed pawns and ruins, #187 withholding tier, #188 map loaded

---

### Pressure

**Possible?** Yes. Strength, frequency, composition, declared raid objectives and per-faction hostility all have verified seams. The exception is that hostility cannot keep growing *inside* goodwill. Whether the seams compose into "hard for two demigod founders" is [I] until played.
**Multiplayer?** Yes (spec), condition: nothing new is saved, the strength postfix never draws `Rand` (UI calls it), and objective targets are chosen inside incident execution, reading no UI state or settings. Hostility route E is With work. Two-client checks are owed (Verification 9, 14).

The campaign's own storyteller. It composes how big threats are, how often they come and what they are, from campaign state: era time, military strength, Reverence, enemies, and a limited share of wealth. It also covers what a raid wants and how much one particular faction hates the colony. The Glitterite pursuit is [`specs/TRACE.md`](specs/TRACE.md)'s, and Trace never enters this scale.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| Strength from bounded contributors: wealth as a minor share, era time with a ceiling, military capability, Reverence, enemy count | Yes | Yes (spec), condition: the postfix draws no `Rand` (a hard constraint) | **A (as specced)**. Our own storytellers keep the Cassandra, Randy and Phoebe temperaments. One postfix on `DefaultThreatPointsNow` recomposes vanilla's result from curve terms in a Def, between a floor and a ceiling · ours · XML + C# · Medium *(mapped)*. Mechanoids: Total Warfare transpiles the same method, which is a silent collision risk | [§ 2 Strength](specs/PRESSURE.md#2-strength--one-postfix-on-storytellerutilitydefaultthreatpointsnow) |
| Frequency responds to campaign state, separately from size | Yes. Independence costs re-authoring three vanilla curves | Yes: the schedule is seeded and draws nothing from the shared stream | **A (as specced)**. Our own `StorytellerDef`s (XML), plus one cadence comp whose accept fraction follows enemy count and era time · XML + C# · Medium *(mapped)* | [§ 1](specs/PRESSURE.md#1-the-storyteller--our-own-storytellerdefs), [§ 3 Frequency](specs/PRESSURE.md#3-frequency) |
| Opposition stays dangerous through quality, not only numbers | Yes | Yes (def data, no new state) | **A** cap the costliest pawn per faction (*"four juggernauts, not forty men"*) · XML · Easy *(mapped)*<br>**B** an era's signature raid legal only above a points band · XML · Easy *(mapped)*<br>A strategy with a high `minPawns` forces quantity, so author the two together | [§ 4 Composition](specs/PRESSURE.md#4-composition--quality-not-only-quantity) |
| More enemy factions raise pressure; alliances are an input | Yes | Yes | Size: § 2's enemy-count term. Frequency: § 3's hostile cadence<br>Selection weight:<br>**(a)** VEF's ally option · XML · Easy *(mapped)* · it cannot express "enemies increase threats", and it cannot read Reverence<br>**(b)** our weight by enemy count, Reverence band and era · C# · Medium *(mapped)*<br>The spec recommends (b). Alliances: (b), plus § 5 | [§ 4 Composition](specs/PRESSURE.md#4-composition--quality-not-only-quantity) |
| A beat, a refused demand or the pursuit can send a raid of fixed faction, size and strategy | Yes | Yes | **A**: an `IncidentDef` on VEF's `IncidentWorker_RaidEnemySpecial` · XML · Easy *(mapped)*. Always write `forcedPointsRange` (T-65) | [§ 4 Composition](specs/PRESSURE.md#4-composition--quality-not-only-quantity) |
| Reverence also brings welcome arrivals: pilgrims, offerings, volunteers | Yes | Yes | **A (as specced)**. A second instance of the cadence comp driven by global Reverence, plus our incident defs on vanilla visitor, trader, wanderer and quest workers · XML + C# · Medium *(mapped)* | [§ 5 Positive half](specs/PRESSURE.md#5-the-positive-half) |
| The ordered story spine is safe from storyteller chance | Yes | Yes | Four vanilla levers, all XML · Easy *(mapped)*:<br>fire beats from the spine quest, never a random comp<br>a quiet-window game condition<br>a `Special`-category incident that random comps cannot pick<br>floor or pin the beat's raid size | [§ 7 Spine](specs/PRESSURE.md#7-protecting-the-ordered-spine) |
| A raid can declare what it came for (people, livestock or stores) and leave once it has it | Yes. Burning fields is a want, and it is not free | Yes (spec), condition: targets are chosen inside incident execution, and read no current map, selection, prefs or settings. Two-client check owed | **A (as specced)**. One raid-strategy worker reading a per-objective extension; one `RaidStrategyDef` per objective, whose letter title names it; our own trigger for partial losses; a startup validator · C# + XML · Medium *(mapped)*<br>Kidnap and steal need code (there is no XML path). Livestock rides vanilla `LordJob_AssaultThings`. A stores raid targets shelves and coolers, never food or walls (T-88) | [§ 8 Raid objectives](specs/PRESSURE.md#8-raid-objectives--what-the-arriving-group-wants) |
| A faction that hates the colony acts against it more, and worse, than one that merely dislikes it | Yes, by composition, but not inside goodwill | Yes for A–D, F and G; With work for E | **A** raid size scaled per faction · C# · Medium<br>**B** a named enemy on its own cadence · C# · Medium<br>**C** a declared war as a quest state · XML · Easy<br>**D** hostility the world generates, through a goodwill cap · C# + XML · Easy<br>**E** a per-faction grudge past −100 · C# · Medium<br>**F** sieges, caravan demands, ambushes · XML · Easy<br>**G** which faction the storyteller draws · C# · Medium<br>The spec recommends D (cap) + A + C, with B and G "likely rather than optional" | [§ Hostility-scaled pressure](specs/PRESSURE.md#hostility-scaled-pressure--a-faction-acts-on-how-much-it-hates-you) |
| Players can broadly see what is raising pressure | Yes [I]. A costed piece only, with no section | Unknown. The spec is silent; a design and a two-client check would settle it | **A (as specced)**. A readout of about 40 lines of C#, supplied to the political surface · Medium *(mapped)*. Which surface is #119's, per #61 | [§ Cost](specs/PRESSURE.md#cost) |

**What the story can do with it**
- Grow raids with time spent in an era. They flatten at the era's ceiling and never reset at a boundary. Military capability, Reverence and enemy count add to that, and wealth is a minor share.
- Title the letter with the raid's aim: *"Slave raid: the Ashen Clans"*, *"Livestock raid"*, *"Stores raid"*. The player reads it before the group arrives, and the group leaves once it has what it came for.
- Declare war as a beat. The war is a quest with its own cadence and size, visible in the Quests tab, that ends when a signal says so. Peace or a bought truce can be that signal.
- A hated faction comes more often and in greater numbers, and can besiege or breach at strengths where others cannot. Taking its settlements turns it hostile at once, with the reason shown on the faction card.
- Send an authored raid of fixed faction, size and strategy in XML. It can be kept out of every random pool, and the storyteller quieted around it.
- Give chosen factions fewer, better pawns. An era's signature raid appears only above a strength band.
- Bring pilgrims, offerings and volunteers as Reverence rises, alongside the bigger threats.

**What it cannot do**
- Hatred cannot live in the goodwill number. It is clamped at −100, and nothing in vanilla reads how hostile a faction is past −75. Vanilla's natural drift takes about 400 in-game days to turn a faction hostile and stops at −80. A war needs a goodwill cap (route D) or a direct write.
- A declared war (route C) bypasses quiet windows and planet-layer limits, because its raids are `forced`. It sends only raids and mech clusters, and only against a map. Disable it around a beat.
- Raids aimed at stockpiled items, crops, walls or doors silently do nothing (T-88). A partial-herd objective ends only when the whole herd is dead unless we write our own trigger (T-89). A strategy without `arriveModes` is never picked (T-90). An authored raid without `forcedPointsRange` has zero points (T-65).
- Raid strategies have no `minTechLevel` (T-16). Era gates go through per-faction curves, pawn kinds or the worker.
- The Schism's deserters cannot raid through the storyteller without an Empire-titled pawn present, so their raids must be authored (T-14, T-91). An emptied raid pool stops raids with no message (T-17).
- Inserting a comp into a shared storyteller re-rolls every later comp's schedule (T-66). In orbit only 18 of 91 incidents are legal (T-48). Route A's heavier raids drop the same loot.
- Trace never scales ordinary raids. Pursuit raids and their timing belong to TRACE.md (#56).

**Spec and tickets:** [`specs/PRESSURE.md`](specs/PRESSURE.md) · #60 storyteller, #77 raid objectives, #169 hostility-scaled pressure (requirements: #9)

---

### Encounters

**Possible?** Yes, all four parts: the timer, the random friendly giver, delivery at a site, and delivery by visitors at the anima tree. Visitors who walk to the tree, and a *numeric* goodwill floor, need small C#.
**Multiplayer?** Yes. Timer T2, and T7 when it is added to a running save, have join-time edge cases.

An optional, authored quest that someone *tells* the colony about. It arrives on a timer from a randomly drawn faction at peace with the colony. It delivers its content at a site the player travels to, or through visitors who use something already on the colony's map. The campaign case is the anima-teaching encounter in [`requirements/ALTAR.md`](requirements/ALTAR.md). Any later told encounter of the same shape uses this card.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| It arrives on its own schedule | Yes | Yes. With work for T2, and for T7 added mid-save | **T1** one offer on day X · XML · Easy<br>**T2** re-offered N days after it lapses · XML · Easy<br>**T3** "may happen" any time after day X, by weight · XML · Easy<br>**T4** our comp: after day X, retrying until offered · C# · Medium<br>**T7** a VEF chain on a day drawn from a range, independent of storyteller · XML · Easy (T-71)<br>**T5**, **T6** · *not recommended*<br>The spec recommends T1 if the quest cannot fail on the day, else T4 | [§ 1 Timer](specs/ENCOUNTERS.md#1-the-timer--what-offers-the-quest-after-x-days) |
| From a faction the player is neutral or better with, drawn at random | Yes, as a relation kind. A goodwill *number* or a culture filter needs C# | Yes | **G1** any non-hostile faction · XML · Easy<br>**G2** a named leader as asker, with faction defs excluded · XML · Easy<br>**G3** our node, for a numeric goodwill floor or tribal-only · C# · Medium | [§ 2 Giver](specs/ENCOUNTERS.md#2-the-giver--drawn-at-random-neutral-or-better) |
| Delivered at a site the player travels to | Yes | Yes | **S1** a generated site under the giver's faction, with its people [I] and an anima tree, and a passage on arrival · XML · Easy<br>**S2** a map-less meeting on arrival, shaped like peace talks · C# · Medium | [§ 3 Site](specs/ENCOUNTERS.md#3-delivery-at-a-site-the-player-travels-to) |
| Delivered by a group that visits and uses the anima tree | Yes. Reaching the tree needs C# | Yes (V3 With work) | **V2** visitors walk to the tree, venerate it and leave, as Ideology's reliquary pilgrims do · C# · Medium (T-158)<br>**V1** visitors loiter; the tree appears only in the letter · XML · Easy<br>**V3** our own rite in which a colonist takes part · C# · Hard | [§ 4 Visiting group](specs/ENCOUNTERS.md#4-delivery-by-a-group-that-visits-and-uses-the-anima-tree) |
| It teaches without granting power | Yes | Yes (system verdict) | A passage (an archived letter), a fading memory, an inert mark on a pawn, a history event for precepts · XML · Easy<br>A techprint · XML · Easy, with a catch<br>A remembered fact that later content can check · C# · Medium<br>A readable lore object · C# · Medium | [§ 5 Payload](specs/ENCOUNTERS.md#5-what-teaching-can-deliver) |
| Offered, never imposed: ignoring it costs nothing, and it grants no psylink | Yes | Yes | **A**: an expiry with no failure part, plus a timeout that removes an unvisited site. The anima linking ritual is ruled out · XML · Easy *(mapped)* | [§ Constraints](specs/ENCOUNTERS.md#constraints) |

**What the story can do with it**
- Fix the day, draw it from a range, let it "maybe" happen, or bring the offer back after it lapses.
- Name the giver's leader in the letter, drawn from any faction that is not hostile. Restrict it to tribes through an exclusion list, or through our node.
- Send the colony on a caravan trip to the giver's village by an anima tree, with a passage on arrival and something to carry home.
- Bring the giver's people to the colony's own anima tree. They venerate it and leave, and harming the tree or the visitors ends the rite.
- Leave the colonists a memory, an inert mark or an archived passage. A later quest can ask whether the lesson was learned.
- Keep the quest out of every random pool with `rootSelectionWeight` 0 (`isRootSpecial` alone gates nothing, #197), and reuse the shape for any later told encounter.

**What it cannot do**
- A one-day timer (T1, and T2 within a session) is lost forever, with no log line, if there is no eligible giver, tree, site tile or unmet techprint on that day (T-157). T7 instead generates a broken quest (T-71).
- `allowNeutral` and `allowAlly` default to false. Omit them and no giver is ever found.
- An offer cannot be declined, only dismissed or left to expire. Leaving a quest site destroys it, so it cannot be revisited. A site nobody enters stays on the map unless a timeout node removes it.
- A save taken before the visitors arrive loses V2's completion signal, so a payload keyed to it never fires (T-158). Key the payload to the group leaving instead. V2 also needs Ideology.
- A techprint payload must unlock something the player can reach another way, or the encounter gates research.
- In V2 the rite belongs to the visitors, and no colonist takes part. The anima linking ritual grants a psylink and is off-limits (T-27).
- Every storyteller must carry the timer comp, appended last (T-66). If our storyteller drops vanilla's anima-tree respawn comp, a cut tree never returns.

**Spec and tickets:** [`specs/ENCOUNTERS.md`](specs/ENCOUNTERS.md) · #158 optional timed encounter (inherited: #136, #93, #131)

---

## Glittertech

### Trace and the Glitterite pursuit

**Possible?** Yes. Every mechanism is [V]; that they compose is [I] (no verdict line for the main build; from § Status). Planet↔orbit and two colonies both state Yes.
**Multiplayer?** With work. Every write to Trace is already on a synced path. The pursuit quest must be ended and regenerated on every relocation, or a gravship move strands it on a dead map clock (T-177).

Trace is how complete a picture the Glitterites have of the founders: 0–100, in three bands. It drives a hidden search. When the search completes, a detection raid comes, then raids repeat until the colony relocates far enough away.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| Trace as a level with low, rising and high bands, each switching effects on | Yes | Yes | **A (as specced)** VFE Deserters' Visibility ladder, rebuilt Def-for-Def without the mod · our `WorldComponent_Trace` · C# + XML · Hard (mapped) | [§ The build](specs/TRACE.md#the-build) |
| Hacks, missions and analysis raise Trace; Glitterite quests and time lower it | Yes | Yes | **A (as specced)** Per-hack increment by the target's authored depth (`Local` = 0), a quest part carrying ± Trace, analysis calling in from its tick, daily decay · ours on HACKING's and RESEARCH's seams · C# + XML · Medium (mapped) | [§ What changes it](specs/TRACE.md#what-changes-it) |
| Rising Trace makes Glitterite raids more frequent and gates incidents by band; ordinary raids stay the same size | Yes | Yes | **A (as specced)** `TraceEffect_Incident` and `TraceEffect_RaidChance` (the Glitterites' share of raid selection). Raid *size* scales only inside the pursuit · ours on two VFED seams · C# · Medium (mapped) | [§ Why Trace cannot multiply with Reverence](specs/TRACE.md#why-trace-cannot-multiply-with-reverence) |
| Search runs unseen, then a countdown appears that moves as Trace moves | Yes | With work (T-177) | **A (as specced)** Standing auto-accepted quest; our search part hides the estimate until the reveal, then recomputes it from current Trace on every draw · C# + XML · Medium (mapped) | [§ The search meter and the pursuit](specs/TRACE.md#the-search-meter-and-the-pursuit--one-quest-mostly-vanilla-parts) |
| Detection brings one huge raid, then repeated raids until escape | Yes | With work (T-177), condition: the repeats stay on vanilla `QuestPart_ThreatsGenerator` ("a custom incident-maker gets no such filter", T-178) | **A (as specced)** Vanilla `QuestPart_RandomRaid`, then `QuestPart_ThreatsGenerator` on an authored on/off cycle (Royal Ascent's shape) · vanilla · XML · Easy (mapped) | [§ The search meter and the pursuit](specs/TRACE.md#the-search-meter-and-the-pursuit--one-quest-mostly-vanilla-parts), [§ Which clock](specs/TRACE.md#which-clock-the-pursuit-runs-on) |
| A long enough move resets the search, never Trace; a short hop resets nothing | Yes | Yes | **A (as specced)** Compares the settled tile on the world tick, with no travel-path hook · ours · C# · Medium (mapped) | [§ The search meter and the pursuit](specs/TRACE.md#the-search-meter-and-the-pursuit--one-quest-mostly-vanilla-parts) |
| A planet↔orbit jump always counts as an escape; an orbit→orbit move needs its own distance | Yes | Yes (A–C) · With work (D) | **A** Free: the distance call already returns "infinite" across layers · vanilla · Easy<br>**B** Explicit layer branch, giving a named "we left the planet" event (B′: branch on `isSpace`) · C# · Easy<br>**C** Escape distance authored per layer · XML · Easy<br>**D** Detect the move in the landing frame · C#, Harmony · Medium · *not recommended*: T-78, contested seam<br>Spec recommends A + B + C | [§ Planet↔orbit](specs/TRACE.md#planetorbit-as-a-qualifying-relocation) |
| Two colonies: hunt each one, one of them, or the founders' people as a whole | Yes | With work (A, A′, C) · Yes (B) | **A** Per colony: separate search, reveal, raids and escape · C# + XML · Medium<br>**A′** As A, with the meter on the colony's map · C# · Medium<br>**B** One named colony; the other is never hunted · C# · Medium<br>**C** Faction-wide: one countdown, raids hit every colony · C# + XML · Medium<br>Spec recommends A | [§ Two colonies](specs/TRACE.md#two-colonies) |
| Players see the band, a mission's Trace cost before accepting, band changes and the countdown | Yes | Yes | **A (as specced)**<br>D1 band row in the network window<br>D2 Trace row on the quest offer<br>D3 per-target Trace cost before a hack (optional; no requirement names it)<br>D4 band-change letter<br>D5 countdown in the quest tab<br>D6 always-visible number<br>· ours · C# · Medium (mapped) | [§ Where the player sees it](specs/TRACE.md#where-the-player-sees-it) |

**What the story can do with it**
- Tag any hackable target `Local`, `Device`, `Network` or `Command` in XML. A basic door costs 0 Trace; a reactor or command core costs more, and more still if detected.
- A mission can raise or lower Trace. The change shows on the offer before acceptance, next to its other rewards.
- Crossing a band sends a letter listing what switched on and off. Band effects can block incidents or make Glitterite raids more common.
- The hunt is invisible until the reveal. After it, the countdown shortens or lengthens the moment Trace moves.
- After detection, raids repeat on an authored cycle. The player may stay and fight indefinitely; detection never forces departure or defeat (rule 6).
- A qualifying move resets the search: by gravship, or by caravanning out, founding a new settlement and abandoning the old one. Leaving the planet always qualifies (a named beat under B). A move within orbit uses its own authored distance.
- A higher Trace band can raise every Intel price, Instruction included ("aggression taxed twice"), unless an entry opts out.
- With two colonies the story can hunt both separately, only one (the other is a haven), or the founders' people wherever they are.

**What it cannot do**
- Trace never makes an ordinary raid bigger. It never enters the global threat scalar; only raids authored into the pursuit scale with it (PRESSURE check 5).
- The build ships three band effects: incident gating, raid share and search rate. Scaling raid size outside the pursuit is ruled out, because it multiplies with Reverence. Moving goodwill is ruled out, because it contradicts "outside diplomacy".
- Relocation never lowers Trace. Lowering Trace never undoes search progress or hides a colony that has already been found (rules 4 and 6). The pursuit quest cannot be dismissible.
- The launch screen shows fuel cost, not tiles. On a layer change the tooltip can state the rule but has no comparable number. The escape registers on the next world tick, not in the landing frame.
- Nothing in the game knows which settlement is "the colony". Every two-colony shape must name it, and a caravan move is three acts nothing pairs. Falling back to the first home map can fake an escape (T-49).
- Whether pursuit incidents fire on an orbital home is open (T-48). The pursuit's own defs need a layer whitelist.
- Every threshold, rate and distance is a def field, never a mod setting (T-18).

**Spec and tickets:** [`specs/TRACE.md`](specs/TRACE.md) · #56 Trace and pursuit, #150 planet↔orbit relocation, #186 two colonies

---

### Spendable currencies: Influence and Intel

**Possible?** Yes. The Schism catalogue is Yes; shop entries are Yes, with one part built; a failed bought quest's return is Yes, with one small piece built. The balance store and the exchange have no verdict line: per § Status their mechanisms are [V] and the build is [I]. Nothing in the corpus holds a Def-keyed spendable balance, so we build one.
**Multiplayer?** With work: one synced purchase method, plus one sync registration on VEF's quest-shop accept. Whether VEF's offer object crosses the wire unaided is untested; an index form is the fallback.

Influence and Intel are two rows in one saved store. Missions, destructive analysis and site lore pay into them. They are spent on Schism operations, favours and bought quests, and Intel is exchanged for Instruction items. Research never spends it. The card also answers parts of RELIGION (the Schism chain) and QUESTS (shops, the Purchase channel, failed bought quests).

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| Hold Influence and Intel as balances that persist and are always on screen | Yes | Yes | **A (as specced)** One world store keyed by currency def, a network tab (its button is XML only), and a row under the date. The stockpile readout is ruled out for a pure number · ours · C# + XML · Hard (mapped) | [§ The build](specs/CURRENCIES.md#the-build), [§ Where the player sees it](specs/CURRENCIES.md#where-the-player-sees-it) |
| Intel as a number or as an item | Yes | Yes (b) · Yes (spec), condition: fragile, breaks silently on a locale change (a) · Unknown (c) | **(a)** Adopt VFE Deserters' contraband economy whole: Intel becomes rotting cargo, and the Church war is the precondition of buying · VFED · patch · Medium (mapped)<br>**(b)** Stored balance plus our exchange (what the spec builds) · ours · C# · Hard (mapped)<br>**(c)** Our own Intel item and vendor. Free stockpile readout; cannot be earned by reading lore · ours · C# · Medium (mapped) | [§ Three Intel delivery options](specs/CURRENCIES.md#three-intel-delivery-options--priced-mechanisms-not-a-selection) |
| A mission pays a currency, shown before acceptance; approaches can pay differently | Yes | Yes | **A (as specced)** A currency reward row among a quest's reward choices, plus a grant part for authored quests · ours on vanilla `Reward` · C# · Medium (mapped) | [§ What changes it](specs/CURRENCIES.md#what-changes-it) |
| Intel from destructive analysis and optional site lore | Yes | Yes (analysis) · Yes (spec), condition: our lore object drops VEF's designate gizmo (T-61) (lore) | **Analysis** Credited from RESEARCH's destructive-analysis route A; a one-shot use item is *not recommended* (interruption loses all)<br>**Lore** A `Study` override calling `Credit` (CHARTING § 10), or a quest grant on a site signal | [§ What changes it](specs/CURRENCIES.md#what-changes-it), [CHARTING § Persistence and multiplayer](specs/CHARTING.md#persistence-and-multiplayer) |
| Exchange Intel for a techprint or other Instruction item | Yes | Yes (spec), condition: `CanPurchase` is re-checked inside the synced purchase | **A** Table venue: a decoder building, always reachable once built, paced by its own research · ours · C# + XML · Medium (mapped)<br>**B** Faction venue, e.g. the Traders Guild: a broker gated on goodwill and comms, and on the faction not being hidden · ours · C# · Medium (mapped)<br>Spec recommends building both and authoring every Spine item at the table | [§ The Intel exchange](specs/CURRENCIES.md#the-intel-exchange--a-balance-into-an-instruction-item) |
| Buy a quest with a currency (QUESTS' Purchase channel) | Yes | With work | **A** VEF's quest shop with our currency plugged in · VEF + ours · C# + XML · Medium (mapped)<br>**B** Our own catalogue, if VEF is declined · ours · C# · Hard (mapped)<br>Spec recommends A | [§ The purchasable quest catalogue](specs/CURRENCIES.md#the-purchasable-quest-catalogue) |
| Shop stock: an entry is a quest or an item, with its own eligibility and shelf life | Yes (one part built) | Yes (spec), condition: the fill and the accept stay on synced paths (A–D) · Unknown (E) | **A** One shelf; an item entry is an items-reward quest · XML · Easy<br>**B** Per-entry leave and restock on the shelf's tick · C# · Medium<br>**C** Our gate node (era, balance, political flag) · C# · Medium<br>**D** Two shelves: VEF for quests, our exchange for items · C# + XML · Medium<br>**E** Reskin a vanilla trader · Hard · *not recommended*: cannot sell a quest<br>Spec recommends A + B + C | [§ Shop entries](specs/CURRENCIES.md#shop-entries--a-quest-or-an-item-each-with-its-own-eligibility-and-shelf-life) |
| A failed bought quest comes back free, paid again or refunded | Yes | Yes (A, B, D) · with care (C) | **A** Restock the shelf with a fresh roll of the same script · C# + XML · Medium<br>**B** Refund on failure · C# + XML · Medium<br>**C** Free re-grant as an ordinary offer outside the shop · VEF · XML · Easy · *not recommended for plot entries*: also hands the quest out free at game start (T-153)<br>**D** The Schism re-offers its step · Medium<br>**E** Adopt VFED's shop · Hard · *not recommended*: service missions never return<br>Spec recommends A, with B's refund as a per-entry mode | [§ A failed bought quest returns](specs/CURRENCIES.md#a-failed-bought-quest-returns-to-the-shop) |
| Spending Influence advances the Schism plot in order; a marking act commits the founders | Yes | Yes (A, D) · With work (B, C) | **A** Paid ordered chain in the catalogue · ours on VFED's shape · C# + XML · Medium<br>**B** Price on an ordinary quest offer · C# + XML · Medium<br>**C** One VEF quest giver for plot and favours · Medium · *not recommended*: no order, and a reset discards favours<br>**D** Adopt VFE Deserters as the Schism · Hard · *not recommended as shipped*: wrong era, offers a sell-out<br>Spec recommends A, with first Influence gained as the marking act | [§ The Schism catalogue](specs/CURRENCIES.md#the-schism-catalogue--a-spend-that-advances-the-plot) |
| A currency decays or expires | Yes (capability) | Unknown | Item rot (delivery options (a) and (c)), or a tick debit on the store using TRACE's decay shape. Weight not stated. The choice is #119's | [§ Outstanding decisions](specs/CURRENCIES.md#outstanding-decisions) |

**What the story can do with it**
- One mission can offer Influence, Intel or Reverence as alternative rewards, all visible before the player accepts.
- Reward curiosity: reading lore at a site can pay Intel, because Intel is a number, not loot.
- The exchange can be a decoder that turns Intel into techprints, a broker who sells them for goodwill, or both at different prices. A greyed row says why.
- A hand-authored Instruction item needs no C#: its own name, art and lore on a techprint component [I].
- A shop can sell missions and items side by side. Each entry gates on research, or (with our node) on era, a balance or a political flag, and stands until bought or expires on its own clock.
- A failed bought mission can come back free, at its price, refunded, after a delay, or capped. The policy is set per entry.
- The Schism: an ordered chain of paid blows. Each blow can offer several approaches, each with its own price, combat level and exposure. A failed blow is re-offered.

**What it cannot do**
- Research and hacking never spend Intel. Only the exchange and the quest shop debit it. An Exemplar gate is never priced in Intel.
- Intel cannot be both: as a number it gets no free stockpile readout, and as an item it cannot be earned by reading lore.
- A purchase never advances the Schism; only a quest outcome does. Spending elsewhere stalls the plot and never strands it. Lost income, a step that fails to generate, or decay below a step's price can strand it.
- "First plot spend" as the marking act breaks RELIGION's banking clause.
- A faction venue can close: hostility, low goodwill, hidden, or missing from the roster (T-07). A Spine item sold only there is a softlock, and so is `maxIssued` set on a Spine item. Drop-pod delivery onto a gravship or orbit map is unverified.
- Glitterite techprints leak from orbital traders, quest rewards and loot unless excluded. If VFE Deserters ships, its shop sells every techprint (T-99).
- A returned quest is always a fresh roll, never the same quest, and free returns let a player re-roll rewards by failing on purpose.
- Three silent shop failures: buying an expired entry charges and starts nothing unless the shop checks the quest's state; an entry built without a choice part silently leaves the shelf (T-76); a quest script that throws during generation never appears (T-77).
- Balances are keyed by def name, never `DefMap` (T-37); every price is a def field, never a mod setting (T-18).

**Spec and tickets:** [`specs/CURRENCIES.md`](specs/CURRENCIES.md) · #54 Intel exchange (absorbed #55's currency half), #106 purchasable quest catalogue, #132 Schism catalogue, #144 shop entries, #145 failed bought quest returns

---

### Hacking

**Possible?** Yes, on Ushanka's Hacking Expansion, plus our Ultra rung, research gate, cross-map relay and intrusion report (no verdict line; from § Status: carrier verified, our pieces [I] as compositions). Without Ushanka the front is about 1,500 lines of new C#, and the requirement should be re-scoped.
**Multiplayer?** With work. Five of Ushanka's gizmo delegates and our relay gizmo need sync registration. Ushanka's settings and build must be identical on both clients (T-67).

Hacking is the second technology front. Intel teaches the Glitterites' protocol language. Research opens harder classes of target in order, and the verbs grow from bypassing a door to seizing mechs and turning defences.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| Hack targets are tiered, and harder ICE guards better targets | Yes | With work (T-67) | **A (as specced)** Ushanka's ICE bands plus two Ultra bands (Glitterite protocol, Archon ICE), and a fix so a target gets its highest band rather than a weighted roll · Ushanka + ours · XML + Harmony · Medium (mapped) | [§ Tiering](specs/HACKING.md#tiering-reuse-with-one-patch) |
| Research opens classes of target in order: defences, reactors, low mechs, strong mechs | Yes | Yes | **A (as specced)** A class tag on each target def; the hack is refused with a legible reason until the mapped project is done · ours · XML + Harmony · Medium (mapped) | [§ Gating target classes by research](specs/HACKING.md#gating-target-classes-by-research-new) |
| Named campaign artifacts unlock qualitative hacking research | Yes | Yes (RESEARCH; CURRENCIES) | **A (as specced)** Ultra hacking research gated on studied Glitterite exemplars and, where authored, an Intel-bought Instruction item · vanilla + the exchange · XML · Easy (mapped) | [§ Cost](specs/HACKING.md#cost), [RESEARCH § Persistence and multiplayer](specs/RESEARCH.md#persistence-and-multiplayer), [CURRENCIES § Multiplayer](specs/CURRENCIES.md#multiplayer) |
| New verbs keep arriving | Yes | With work | **A (as specced)** Ushanka's eight verbs, learned by hacking from data items and re-gated behind Glitterite items and Ultra research · XML · Easy (mapped). A genuinely new verb is one ability class · C# · Medium (mapped) | [§ New verbs](specs/HACKING.md#new-verbs-reuse) |
| Seize a turret or a mech; hack here and have the effect land elsewhere | Yes | With work | **A (as specced)** A turret flips in one hack; a mech is disabled, then hijacked. Odyssey's security terminal is the shipped "hack here, effect there" · Ushanka + vanilla · as shipped · Easy (mapped); the turret repair (T-68) is a small prefix | [§ Turning a hostile thing friendly](specs/HACKING.md#turning-a-hostile-thing-friendly-mid-map-reuse) |
| A skilled hacker at home operates through a field pawn at an away site | Yes | With work (the relay gizmo) | **A** Relay item on the field pawn; the home hacker's hacking stats replace the field pawn's · ours · C# + XML · Medium (mapped)<br>**B** Mechanitor-style cross-map control · C# · Hard (mapped) · *not selected*: moves a job across a map boundary, several hundred lines, adds a capacity cap nobody asked for | [§ The cross-map relay](specs/HACKING.md#the-cross-map-relay-new--the-one-genuine-absence) |
| Every intrusion reports its depth and whether it was detected, which feeds Trace | Yes | Yes | **A (as specced)** An intrusion log raised on hack completion and on lockout · ours · C# · Medium (mapped) | [§ What #56 needs from hacking](specs/HACKING.md#what-56-needs-from-hacking) |
| The player reads hacking state: progress, ICE, why a target refuses, remote reach, intrusion history | Yes | Yes | **A (as specced)** Mostly shipped UI. Intrusion history is a Cyberpod tab, with a letter per deep intrusion as the free fallback · C# · Medium (mapped) | [§ Display](specs/HACKING.md#display) |

**What the story can do with it**
- Author which class each target belongs to and which research opens it. A refused hack shows its reason in the menu, the inspect pane and under the cursor.
- Turrets and mechs that Ushanka makes hackable get their difficulty from their cost or combat power automatically. Every other target keeps its authored defence.
- Verbs are earned, not bought: data items from hacked sources teach an ability through use, with a letter.
- A mission that once needed every defender dead can later be won by disabling a mech and then hijacking it, or by flipping a turret onto its owners.
- A colonist sealed in a Cyberpod at home drives a hack at an away site through a field pawn carrying a relay. The field pawn's stat report names them.
- Deeper ICE notices intruders more often, for free. Black ICE can kill the hacker, and the game warns before the hack starts.
- Vanilla already emits "HackingStarted" and "Hacked" quest signals, so a quest-authored site can react to a hack starting or succeeding.

**What it cannot do**
- A Glitterite person is never hackable, and no android is: nothing gives a humanlike pawn a hackable component. The jailbreak is surgery, never a hack.
- The relay moves the numbers, not the job. The field pawn must stand on the target's map, and the home hacker must be in a Cyberpod on a home map. Cross-map hacking exists nowhere else in the corpus.
- As specced, a hack yields no Intel; Ushanka's data items give research points and verbs. That is HACKING's scope, not an engine limit: the "Hacked" quest signal and CURRENCIES' public `Credit` both exist.
- A seized turret may stay mis-targeted until the next load unless the repair ships (T-68). After a RimWorld update, the re-hack reset can fail silently (T-69).
- If an Ultra project needs an exemplar reachable only by the hack that project unlocks, the branch locks silently. The gate needs Biotech (T-40).
- Mismatched Ushanka settings or builds between clients desync with no error (T-67, T-18).

**Spec and tickets:** [`specs/HACKING.md`](specs/HACKING.md) · #58 hacking front

---

### Androids

**Possible?** Yes. VRE – Android ships player-side manufacture, gated on an Ultra project (no verdict line; from § Status). The psylink, by-kind, captured-Glitterite and jailbreak sections all state Yes.
**Multiplayer?** Yes (spec), condition: Multiplayer Compatibility's VRE – Android entry is loaded. Without it the first order desyncs. Every psylink, captive and jailbreak route is Yes except J5 (With work).

"Android" is a body; "Glitterite" is a civilisation. Player-built androids are full colonists who can hold a faith, and the ending's argument depends on building them carrying no penalty.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| Manufacture androids at Ultra as full colonists with a faith | Yes | Yes (spec), condition: MP Compat's VRE – Android entry | **A (as specced)** VRE – Android's production line. An android is a xenotype on race Human: it joins on spawn and holds a faith, and Devotion needs no new code ([I] until a rite runs with one). Rejected: a mech-gestator recipe, which makes a bonded mech, and NPC-only kinds · VRE – Android · as shipped · Easy (mapped) | [§ 1. The mechanism](specs/ANDROIDS.md#1-the-mechanism--a-building-with-a-job-not-a-recipedef), [§ 2. What an android is](specs/ANDROIDS.md#2-what-an-android-is-mechanically--a-xenotype-on-race-human) |
| Manufacture hangs off the exemplar loop | Yes | Yes (RESEARCH) | **A (as specced)** The android research requires studying a Glitterite exemplar, and optionally an Intel-bought techprint (#117); never a per-android Intel debit · vanilla · XML · Easy (mapped). Holds only if RESEARCH's bypass shutoffs ship (T-92) | [§ 5. The Exemplar gate](specs/ANDROIDS.md#5-the-exemplar-gate), [RESEARCH § Persistence and multiplayer](specs/RESEARCH.md#persistence-and-multiplayer) |
| An android can hold and use a psylink | Yes | Yes | **A** Every android · XML · Easy<br>**B** Chosen per android at the creation station, at the cost of synthetic immunity · XML · Easy<br>**C** Awakened androids may link at the anima tree (adds to A or B) · XML · Easy<br>**D** A gate that is not a gene (story flag, altar, era); also reopens neuroformer upgrades · C# · Medium<br>**E** Leave it; the asymmetry stands<br>Spec recommends B | [§ Psylinks](specs/ANDROIDS.md#psylinks--verdict-and-routes) |
| Psylinks by kind: built, arrived, awakened, jailbroken, Glitterite | Yes | Yes | **K1** Gate the grant: the rite already admits only awakened androids · XML · Easy<br>**K2** Awakening lifts deafness · XML · Easy<br>**K3** Route B with the xenotypes split · XML · Easy<br>**K4** Deafness on marker genes per kind · XML + one C# postfix · Medium<br>**K5** Our own sensitivity rule, the only absolute deafness · C# + XML · Medium<br>Spec recommends K1 + K2, with Glitterite deafness on its marker gene; K5 only if it must be absolute | [§ By kind of android](specs/ANDROIDS.md#by-kind-of-android) |
| A captured Glitterite is a prisoner only: no faith, never recruited, enslaved or converted | Yes | Yes | **A** Vanilla flags · Easy–Medium · *not recommended alone*: a faithless pawn converts on the first attempt (T-161); "unrecruitable" is difficulty-gated (T-162)<br>**B** Close every offer · C# + XML · Medium<br>**C** Refuse every effect at four chokepoints · C# · Medium<br>Spec recommends B + C on a gene marker | [§ A captured Glitterite](specs/ANDROIDS.md#a-captured-glitterite--no-faith-never-on-the-players-side) |
| Jailbreak a captured Glitterite into an android colonist | Yes | Yes (J1–J4) · With work (J5) | **J1** Surgery consuming a persona subcore: removes the marker, awakens, sets a faith and joins, in one act · C# + XML · Medium<br>**J2** VRE's behaviorist station, patched · C# · Medium (Hard with a consumed item)<br>**J3** Unlock only, then recruit the ordinary way (J3a at the station, J3b by surgery) · Easy (J3b) / Medium (J3a)<br>**J4** A rite of the player's faith · Medium–Hard · *not recommended*: drags in ritual quality and precepts<br>**J5** Our own rig · Hard · *not recommended*: J1 already does it<br>Spec recommends J1 | [§ Jailbreaking](specs/ANDROIDS.md#jailbreaking-a-captured-glitterite-into-an-android-colonist) |
| No awakened android arrives before Ultra (ERA's arrival band) | Yes | Unknown (not stated) | **A** Remove the 2% bleed from outlander, pirate and Church factions; this also removes them at Ultra · XML · Easy (mapped)<br>**B** An era-scoped removal · named by the spec; no carrier, weight or MP given | [§ 6. Scoping the bleed](specs/ANDROIDS.md#6-scoping-the-bleed) |

**What the story can do with it**
- A built android joins on the spot, with no recruitment. The player names its custom xenotype.
- Its real price is a persona subcore, which takes four colonists scanned in turn. The per-unit materials can change only by a small C# patch, for example a Glitterite material in place of uranium (T-93).
- Hearing the channel can be a decision about one android (B), or can follow awakening (K1 + K2): the line the altar's rite already draws.
- A captured Glitterite reads "Non-recruitable" in vanilla's own words. It can be held or sold, and nothing more.
- The jailbreak can be a surgery that gives the persona back. VRE's awakening letter lets the player pick passions and a trait, and the full name returns. Its faith can be the player's primary faith, the operator's ("it believes what the one who freed it believes"), or none until the next load.
- The jailbreak can be made able to fail, with our own roll. It can also only *open* the Glitterite (J3) and leave the colony to win it over.
- A basic Glitterite can awaken in its cell by mood, berserk or inspired, unless its xenotype carries anti-awakening protocols.

**What it cannot do**
- As shipped, no android holds a psylink. Two independent gates block it, and lifting one alone does nothing. A deaf, linked android, or a Glitterite, still casts or is targetable while psychic gear or lost eyes lift its sensitivity (T-185). Only K5 makes deafness absolute.
- Route B's price is fixed: the android that can hear can also catch disease, addiction and cancer.
- Built, arrived and jailbroken androids are indistinguishable without a marker gene of ours. Awakened is the only kind VRE marks (T-163 governs which marker genes land where).
- With VPE and Royalty loaded, bestowing a title on a psylink-blocked android throws. This matters wherever an android could be an Exaltation honoree.
- "No faith" and "no conversion" are separate properties. Route C alone leaves broken states: a refused recruit is a hostile Glitterite freed on the map. A kind is not a marker (T-112).
- Android surgery never fails as shipped, and it is Crafting work, not a doctor's (T-164).
- After a jailbreak the pawn is an ordinary android. Nothing recognises it later, for Trace or a later beat, without a second record. Letting the player pick its faith needs a synced choice.

**Spec and tickets:** [`specs/ANDROIDS.md`](specs/ANDROIDS.md) · #78 android manufacture, #141 android psylinks, #181 psylinks by kind, #142 captured Glitterite, #143 jailbreak

---

### Research

**Possible?** Yes. Practice, the Exemplar gate, Instruction and destructive analysis all have routes (the gate is vanilla XML; Practice's up-front routes are XML). Bypasses and granted verbs have no verdict line (from § Status, compositions [I]). No research-project field consumes a resource; Practice is carried by crafting the item a vanilla gate already asks for.
**Multiplayer?** Yes. The analysis order and the study toggle are already synced. The lockout and grant patches add no sync surface of ours, and destructive analysis states Yes. Practice's routes A, B, C and E are Yes; More Realistic Research (D) is Unknown.

How the colony earns knowledge: **Practice** (resources consumed by trial and error), **Instruction** (techprint, book, teacher), **Exemplar** (studying a surviving object). Also on this card: destructive Glitterite analysis, keeping the era arc free of shortcuts, and research that unlocks a verb.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| Exemplar: a project needs a named object studied at a bench, and the object survives | Yes | Yes | **A (as specced)** Vanilla `requiredAnalyzed` plus an analysable component on the object, with `destroyedOnAnalyzed false`; works at any tech level. More Realistic Research declined · vanilla · XML · Easy (mapped) | [§ The build](specs/RESEARCH.md#the-build) |
| Instruction: a techprint or authored item unlocks the project; the largest nodes need Instruction derived from Intel | Yes | Yes (CURRENCIES: applying one is a synced Job) | **A (as specced)** Vanilla techprints; a quest reward naming a fixed project; the Intel exchange · vanilla · XML · Easy (mapped) | [§ 6. The seam with Intel](specs/RESEARCH.md#6-the-seam-with-intel), [CURRENCIES § The Intel exchange](specs/CURRENCIES.md#the-intel-exchange--a-balance-into-an-instruction-item) |
| Practice: research consumes authored resources by trial and error | Yes. A and B take the cost before the project starts; only E consumes during research | Yes (A, B, C, E); D Unknown (no MP Compat coverage) | **A** a crafted `stackLimit 1` trial item, analysed and consumed N times (`requiredAnalyzed` + `destroyedOnAnalyzed`) · XML · Easy · needs Biotech; shares the Exemplar gate's ID space (T-41)<br>**B** a crafted techprint (`techprintCount` + a recipe) · XML · Easy, plus the T-99 postfix CURRENCIES already needs<br>**C** Ushanka Hacking's research-giver item · XML · Easy · a speed-up, not a cost<br>**D** More Realistic Research `experimental` · Medium · *not recommended*<br>**E** the bench burns the resource while researching: a refuelable bench plus two patches · XML + C# · Medium<br>**F** our own cost list · C# · *not recommended*: A and B already do it<br>A gate on `FinishProject` is no gate (T-190) | [§ Practice](specs/RESEARCH.md#practice--a-project-that-consumes-resources) |
| Destructive analysis: a long job consumes an artifact and pays Intel and Trace, never research | Yes | Yes (A) | **A** Vanilla study loop plus our payout component: many sessions, progress saved on the item · XML + C# · Medium<br>**B** Our analysable subclass · Medium · *not recommended*: loses an interrupted session; shares the Exemplar gate's manager<br>**C** A production bill with an unfinished item · XML + C# · Medium<br>**D** A use-item job · Medium · *not recommended*: interruption loses all<br>**E** VEF studiable building · Medium · *not recommended*: buildings only, no saved progress<br>**F** Fully custom · Medium–Hard · *not recommended*: rebuilds A<br>Spec recommends A | [§ Destructive artifact analysis](specs/RESEARCH.md#destructive-artifact-analysis) |
| No route reaches research past the era arc or the Exemplar gate for free | Yes | Yes | **A (as specced)** One lockout file: a shutoff per Class A carrier, a one-line fix for the vanilla Schematic book, and a whole-corpus audit script · XML + Python · Easy (mapped) | [§ Bypasses — the build](specs/RESEARCH.md#bypasses--the-build) |
| Research unlocks a verb (work type, work tag, designator): the Neolithic on-ramp | Yes | Yes | **A** Gate a whole architect category · vanilla · XML · Easy (mapped)<br>**B** A research extension plus six patches for work types and single designators, rebuilt from VFE Tribals · ours · C# · Medium (mapped). A vanilla deny-list and `ResearchMod` were surveyed and not taken | [§ Granted capability — the build](specs/RESEARCH.md#granted-capability--the-build) |

**What the story can do with it**
- Gate any branch, at any era, on having brought something home and studied it: a Glitterite heart, a shocktrooper suit, "the sword you took off a dead marauder". The trophy stays. One object can gate several projects across tiers.
- Studying needs a player order naming a colonist; it never happens by itself. The research tab shows the requirement for free, and the letter names the colonist and what was unlocked.
- Granting a project by quest or script clears its study requirement, so the player is never stranded.
- Destructive analysis is opt-in: nobody touches the artifact until the player turns study on. It pays Intel and Trace as it goes, where the artifact lies or at a bench, and fires a quest signal when done.
- Make "we learned to mine" a beat. The verb is greyed out and names its project, then goes live without a reload.
- Price a project in cloth, leather or any authored resource, spent in trials the player orders. Each trial can have its own letter.

**What it cannot do**
- Practice via A or B is paid before the project starts. Only E consumes during research, priced per bench. No route makes research labour worthless (T-191). Analysing a stackable resource burns the whole stack (T-192).
- Research never spends Intel. Destructive analysis adds no research progress and never satisfies an Exemplar gate.
- The Exemplar gate holds only with the lockout: vanilla's Schematic book and several mods can advance a gated project. The lockout must be in before world creation, and it cannot take back progress already granted (#18).
- A destroyed artifact cannot be resumed; only what was already paid stays. Artifacts must not stack, or merging keeps one stack's progress.
- Without Biotech owned, the gate silently disappears and the project becomes free (T-40). Duplicate analysis IDs silently merge two gates (T-41).
- A gated architect category shows greyed and clickable, not hidden. If a verb-granting project skips the cache refresh, no colonist can do the new work until a reload, silently.
- Passive research producers cannot skip an era, but they can collapse one.

**Spec and tickets:** [`specs/RESEARCH.md`](specs/RESEARCH.md) · #67 Exemplar gate, #115 destructive analysis, #83 research bypasses, #72 granted capability, #190 Practice

---

## World and space

### Era

**Possible?** Yes: the era clock, the single advance, its clock under Async Time, above-era content on the colony's own map, and the arrival band as a hard rule by a gate of ours. [#22](https://github.com/cjd721/Rimworld-Archinity/issues/22) still owes its three verifications.
**Multiplayer?** With work.
- WTL's in-game "Change tech level" button is "a client-local write to synchronised state" and must be shut off (§ 6a).
- The advance must stay on the synced research-completion path, or a rite's outcome. Any other caller needs a `[SyncMethod]`.
- AE-4 and AE-5(b) are settings-driven (T-18).
- The spec's two routed sections both say Yes.

The era is the campaign's single axis, Neolithic → Ultra. It is World Tech Level's number, raised one rung at a time by `AdvanceEra()` when a capstone completes, never lowered, and paired with a log of when each era began. The same spec answers how above-era wreckage and events are kept out of the colony's back yard.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| The era advances once per capstone, as one indivisible act, and it is always the players' choice. World and player-faction tech level move together | Yes | Yes (spec), condition: only on the synced research-completion path or a rite's success outcome; any other caller via `[SyncMethod]` | **A (as specced)** capstone completion calls `AdvanceEra()`. It writes WTL's saved level, its live mirror, the player faction def and the boundary log, with a one-rung guard and a T-11 repair on load · ours + WTL reflection shim · C# · Medium *(mapped)*<br>**B** the same call from a rite's success outcome; a cancelled or failed rite calls nothing · ritual outcome worker · C# · weight not stated in this spec (`requirements/ERA.md` cites ~40 lines from RELIGION.md)<br>**C** a build, resources or exemplars the capstone project requires · capstone prerequisites · weight not stated | [§ 3](specs/ERA.md#3-change--advanceera-four-writes-in-one-call), [§ Persistence and multiplayer](specs/ERA.md#persistence-and-multiplayer) |
| Nothing else moves the era | Yes | With work: the shutoff is the fix | **A (as specced)** a Harmony prefix removes WTL's button, which is also the only route to its runtime add-factions window. `Filter_Factions` stays frozen off. Lemmy Progression is recommended BLOCK (#14). A load-time assert makes any other writer loud · ours · C# · Medium *(mapped)* | [§ 6](specs/ERA.md#6-the-second-writers-and-shutting-them-off) |
| When each era began is kept for every era, prior eras included, on a clock that works when each colony runs its own time (Async Time) | Yes | Yes (spec) | The store **(as specced)**: `GameComponent_Era` boundary log · C# · Medium *(mapped)*. Which clock it runs on:<br>**A** world clock: one era time for everyone, running whenever either colony plays · vanilla `GameComponentTick` · C# · Medium<br>**B** one clock per colony: each colony's era time runs only while it plays, and the advance is still one instant · `MapComponentTick`, or MP Compat's `SetupAsyncTime` shape · C# · Medium–Hard<br>A and B compose | [§ 2](specs/ERA.md#2-state--the-boundary-log-and-prior-eras-are-retained), [§ An era's start under Async Time](specs/ERA.md#an-eras-start-under-async-time) |
| The player sees the era and when it began | Yes | Unknown: spec silent; Verification check 7 is the two-client test | **A (as specced)** WTL already prints the tech level on the planet tab (free). An "Era began: day N" line is one postfix; under route B it must name a colony. The boundary log is a row with its own layout, not a tooltip · WTL + ours · C# · Medium *(mapped)* | [§ 5](specs/ERA.md#5-display--mostly-free-and-one-line-of-ours) |
| Above-era structure is removed from the colony's map: ancient dangers, the mechanitor exostrider, road wrecks | Yes | Yes (spec); AE-4 With work (T-18) | **AE-1** scenario part per genstep: home-only for dangers and the exostrider, every map for wrecks · vanilla · XML · Easy<br>**AE-2** generator list edit (Medieval Overhaul ships the shape) · XML patch · Easy<br>**AE-3** home-only prevent on `Base_Player` · XML · Easy<br>**AE-4** WTL genstep filter · settings + XML · Easy · *not recommended*: not home-scoped, and it strips encounter maps (T-165)<br>Spec recommends AE-1 for dangers and the exostrider, AE-3 (ideally as AE-7) for wrecks | [§ Above-era content: Routes](specs/ERA.md#routes) |
| Above-era events arrive in their own era (the mechanitor crash at Industrial) | Yes | Yes (spec); AE-5(b) With work (T-18) | **AE-5(a)** `AdvanceEra()` gives the crash quest at Industrial · C# · Medium. Spec recommends this if the story wants the mechanitor<br>**AE-5(b)** an authored incident with a WTL Industrial row · XML · Easy<br>**AE-6** the transponder refuses to decrypt before Industrial; the remains still stand · C# + XML · Medium<br>**AE-9** a vault uncovered on the living map at an advance · C# · Medium–Hard · *not recommended for debris*: wrecks appearing overnight read as a bug; [I] throughout | [AE-5](specs/ERA.md#ae-5--timed-crash), [AE-6](specs/ERA.md#ae-6--gated-decrypt), [AE-9](specs/ERA.md#ae-9--late-insertion-not-recommended-for-debris) |
| Above-era content is replaced with something that fits | Yes | Yes (spec) | **AE-7** in place: era-fitting debris or an authored structure. Defenders need a genstep class of ours · vanilla / VEF KCSG + ours · XML; C# for defenders · Easy; Medium<br>**AE-8** replaced by a journey: an Archon site on a nearby tile, or the transponder repointed to one · vanilla quest machinery · XML (C# only for a custom site part) · Easy–Medium. Spec recommends it where the replacement should be a place | [AE-7](specs/ERA.md#ae-7--replace-in-place), [AE-8](specs/ERA.md#ae-8--replace-with-a-journey) |
| The arrival band: nothing arrives that breaks the era's flavour from above it, factions and faction-less events alike; no floor; no faction exempt (the Church is the Empire in place) | Yes, by a gate of ours. Ignorance Is Bliss alone is weighting plus a veto, never a hard rule: its pre-set-faction path leaks, and quests, caravan meetings, orbital traders and quest-placed pawns pass it | With work: the band is read from the era clock, never a cache | **AB-1** Ignorance Is Bliss configured: bands raids, visitors and caravans when the game picks the faction; the Church no longer exempt · settings · Easy · *partial*<br>**AB-2** WTL rows: a hard ceiling on every storyteller incident and quest script, per def; no faction choice, no floor · XML · Medium<br>**AB-3** our own gate on five engine seams plus a quest walk: a hard veto on every faction arrival and an authored-breach flag · C# · Medium, the quest half near Hard. AB-3 and AB-2 compose; AB-3 needs IIB off, since IIB rewrites an authored breach | [§ The arrival band](specs/ERA.md#the-arrival-band) |
| Nothing arrives by drop pod before Industrial, when the player gets pods | Yes. Drop raids, pod crashes and orbital trade are already gated at Industrial; quest rewards, quest pawns and siege supplies are not | With work | **DP-1** one patch on the pod funnel places goods at the map edge with no pod before Industrial · patch · Medium<br>**DP-2** the same seam, but a courier or pack animal carries the goods in (VEF Outposts is the donor) · C# · Medium, Hard if the courier must survive the trip · optional<br>**DP-3** pawn rewards and wanderer joiners walk in · patch · Easy–Medium<br>**DP-4** called aid walks in (`forQuickMilitaryAid` on the walk-in mode) · XML · Easy. Switching pods off is not a route: it loses the reward silently | [§ Delivery by drop pod](specs/ERA.md#delivery-by-drop-pod) |
| Every faction is hand-authored, spawn pools included, so no in-band faction fields a stray above-era pawn | Open (#207) | Open (#207) | None yet. WTL's pawn and gear filters clamp every generated pawn to the world level, a weak backstop, not an authored pool | [requirements § The arrival band](requirements/ERA.md#the-arrival-band) |

**What the story can do with it**
- The advance is a beat the players perform. They finish the capstone, and optionally a rite they celebrate, or a build the capstone demands, fires it. A failed or cancelled rite advances nothing.
- Beats can key on era time, e.g. *"180 days after the Medieval gate"*, even after the colony has left that era.
- Era time accumulates. Pressure climbs across the campaign, with no reset and no spike at a boundary. An era can be parked indefinitely; that case is designed for (`requirements/ERA.md` § *Open questions*, PRESSURE).
- The mechanitor's crash can land at Industrial instead of on day one (AE-5), or its transponder can refuse to decrypt until then (AE-6).
- A sealed ancient danger can become an Archon site a short journey away (AE-8), or an era-fitting fixture in the yard (AE-7).
- A vault that "was always there" can surface at an advance (AE-9, [I]).
- The planet tab can show the era, the day it began, and the log of every boundary crossed.

**What it cannot do**
- The advance is one rung, one way: no skip, no retreat. The boundary log is append-only.
- Hold the arrival band on Ignorance Is Bliss alone. Its quest and event tables are hardcoded, and a faction a quest pins leaks past it.
- The home map is generated once, in the Neolithic. There, "author it when it appears" means removal, unless code writes into the living map (AE-9, [I]).
- Under Async Time no clock is "the colony's time". Route A's world clock rises while the other player plays. Under route B, a day-keyed beat fires at different moments per colony. A tick stamped on one clock and read on another is T-175.
- Switching on WTL's `Filter_Factions` is the one setting that breaks the world irrecoverably (T-07). It is frozen off.
- AE-1 and AE-2 strip road wrecks from every map, encounter maps included. None of AE-1 to AE-3 reaches mutator-worker content such as the ancient uplink ([Orbit](#orbit)). AE-6 leaves an Ultra exostrider standing in the Neolithic yard.
- AE-5(b) has no once-only guard (T-157).
- The world's changes at the advance are owned elsewhere: which factions swap, shrink, vanish or appear is #34, with the mechanism in `engine/factions-and-worldgen.md`. The historian letter and changelog are authored flavour; the ERA spec does not mention them.
- None of it is built. Every mechanism is [V]; that they compose is [I] until built and loaded twice.

**Spec and tickets:** [`specs/ERA.md`](specs/ERA.md) · #109 era clock, #185 which clock under Async Time, #153 above-era home content, #113 capstone as trigger, #7 mechanism choice · open: #22 era-gate claims

---

### Charting

**Possible?** Yes. Every clause is expressible, and neither of the requirement's fallbacks is needed. One optional wish is unmet: the engine does not weight the draw within a band toward nearer tiles, and adding that costs code (§ 4).
**Multiplayer?** With work.
- The spec's verdicts: "Yes for the rolls; with work on one inherited seam", and VGE's scanner cluster as shipped is *With work*.
- The inherited seam is Outposts' mod settings, which rewrite each outpost type's range and cadence per install (T-18). TERRITORY § 2c's harness closes it.
- Any state-writing gizmo on the apparatus must be registered, because "a subclass's gizmos inherit nothing". The build is designed to have none.
- The whole find path is on the synced tick.

Discovery becomes labour. A pawn works the apparatus, which surveys for ordinary sites and reads the Waystone's returns. It feeds two pools. The survey pool is ordinary optional sites at vanilla's pace. The return pool is the ordered Archon spine plus a finite set of significant side discoveries. Caravans and scout outposts also turn up survey sites on their own.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| Discovery is labour at an apparatus. Two pools each carry their own guarantee, work does not bank, and skill buys more finds, never better ones | Yes | Yes (spec), condition: no unregistered state-writing gizmo | **A (as specced)** `CompChartingApparatus : CompScanner`, with two accumulators on one comp. Vanilla supplies operator labour, MTB finds, the pity timer and saved progress · vanilla + ours · C# · Medium *(mapped)* | [§ 1](specs/CHARTING.md#1-the-apparatus--compchartingapparatus--compscanner), [§ 7](specs/CHARTING.md#7-what-changes-it) |
| An ordered spine: beat *n+1* only after beat *n* succeeds. A lost site keeps its place, and a standing beat is not re-granted | Yes | A Yes (spec: the cursor is derived, nothing stored) · B Unknown | **A (as specced)** `QuestPart_ChartingSpine : QuestPart_SubquestGenerator` (vanilla's Archonexus pattern), under a parent quest whose root node is #119's · C# · Medium *(mapped)*<br>**B** VEF quest-chain gates, for gated *side* content only · VEF · XML · Easy *(mapped)*. Spec recommends B for side content and rejects it for the spine: it fires on its own clock, so discovery would not be labour | [§ 2](specs/CHARTING.md#2-the-return-pool--questpart_chartingspine--questpart_subquestgenerator), [Alternatives](specs/CHARTING.md#alternatives-and-what-separates-them) |
| A survey pool at roughly vanilla's pace, which any quest can join | Yes | Yes (spec) | **A (as specced)** a mod extension marks pool members, and vanilla's own selection weights pace them. Joining a quest is one XML patch · vanilla + ours · C# + XML · Medium *(mapped)* | [§ 3](specs/CHARTING.md#3-the-survey-pool) |
| A quest leaves the survey pool as eras advance and becomes an ordinary offer ("announced itself" widening) | Yes. Leaving the pool alone does not make it an offer: the storyteller's gate is `randomlySelectable`, which nothing links to the pool, so one era test must drive both | A Yes; B With work (WTL's quest filter is a mod setting, T-18) | **A** an "announced from" era on the survey extension; the selector drops the quest and a game component writes `randomlySelectable` from the same test, at load and at each advance · C#, no Harmony · Medium (spec recommends). Not for quests delivered by a named incident<br>**B** twin defs: a Charting copy, and a storyteller copy hidden below the era by a WTL row (Ludeon's own `OpportunitySite_ItemStash` / `_Giver` shape) · XML · Easy<br>**C** an era node in the quest's root · *not recommended*: givers skip it<br>**D** a patch on the storyteller's chooser · *not recommended*: adds nothing to A | [§ 3 Membership that changes with era](specs/CHARTING.md#membership-that-changes-with-era--a-quest-leaving-the-pool) |
| Reach: the era offers bands and the apparatus accepts them. Nothing is found that the colony cannot reach | Yes; in-band weighting unmet (optional) | Yes (spec) | **A (as specced)** a hard min/max band (`siteDistRange`) plus a rung registry, clamped by the apparatus's `maxAcceptedBand`. A new mobility rung is one XML block on an existing def · vanilla + ours · C# · Medium *(mapped)*<br>A nearer-weighted draw, if wanted: a distance-biased validator or a bespoke draw · C# · cost [I], weight not stated | [§ 4](specs/CHARTING.md#4-the-reach-band), [Rung registry](specs/CHARTING.md#the-rung-registry) |
| The apparatus ladder: Star Table → Observatory → Sensory Array, with more tiers if needed | Yes | Yes (spec) | **A (as specced)** one comp class. Each tier is a `ThingDef`, a `WorkGiverDef` and a `ResearchProjectDef`. A Waystone-less "mundane table" is the same shape with the return pool off · XML · Easy *(mapped)* | [§ 9](specs/CHARTING.md#9-cost) |
| Both jobs are visible with no estimate. The Waystone reports returns out of reach. A find says why it arrived | Yes | Yes (spec), condition: the Waystone readout never calls `CanRun` (T-39) | **A (as specced)** two progress bars with vanilla's estimate dropped, a Waystone inspect line, a reason in the arrival letter, and the chain count free in the quest tab. Optional band rings on the world map · ours · C# · Medium *(mapped)*. Whether any is shown is #119's (routes on #61) | [§ 8](specs/CHARTING.md#8-where-the-player-sees-it) |
| Caravans and scout outposts find ordinary sites as they go, placed next to the finder, with a per-tile re-roll timer | Yes, every clause | Yes (spec); D With work (TERRITORY § 2c) | **A** every tile a caravan enters rolls, on foot or in vehicles; anything that flies is excluded by the seam · vanilla + ours · C# (1 Harmony) · Medium<br>**B** the same with zero Harmony, via a comp on caravan defs · patch + C# · Medium<br>**C** Faction Territories as donor · C# · Medium · *not recommended*: misses vehicle caravans; its cooldown is unsaved and a mod setting<br>**D** outposts: which types search, chance, range, and a latch while a find is unresolved · VEF Outposts + VOE donors · C# + XML · Medium<br>**E** the find arrives as a quest, still anchored on the finder · C# · Easy–Medium<br>Spec recommends A + D, with E where a beat needs a quest | [§ Natural discovery](specs/CHARTING.md#natural-discovery--caravans-and-outposts-rolling-finds-as-they-go) |
| Lore inside a site: read if interested, pays Intel once, always re-readable | Yes | Yes (spec), condition: reached by right-click order (synced); VEF's designate gizmo dropped (T-61) | **A (as specced)** `LoreRecord : StudiableBuilding`. It sends both quest signals, credits Intel once per `loreKey`, raises an archived letter and leaves a "read" variant of the object · VEF + ours · C# + XML · Medium *(mapped)*<br>**B** a carried record: a book looted, hauled home and read, with its text written by reflection. Flagged, not designed · vanilla + ours · C# · Medium *(mapped)* | [§ 10](specs/CHARTING.md#10-inspectable-site-lore), [a record taken home](specs/CHARTING.md#the-other-half-a-record-taken-home) |
| Charting and the orbital scanner: one apparatus or two | Yes, every way | Yes (spec); VGE cluster as shipped With work | **A** Charting reaches orbit; the scanner leaves or is re-skinned (**A′**, XML). The reveal gate is one eligibility test in our code · C# + XML · Medium<br>**B** the scanner carries Charting's content · XML (survey) · Easy / C# (return) · Medium<br>**C** two apparatuses sharing pools; the scanner is a passive orbital survey instrument · XML · Easy<br>**D** fully separate, vanilla as shipped · Easy · *not recommended* unless orbit should feel like somebody else's game<br>Spec recommends A with E1 (tag Odyssey's six orbital quests into the survey pool by XML), or C for a mundane orbital instrument | [§ Orbital scanner](specs/CHARTING.md#the-orbital-scanner-and-charting--one-apparatus-or-two) |

**What the story can do with it**
- A beat becomes eligible on any saved state: spine position, era, a research node, a built thing, a political state, elapsed time, wealth. It never depends on a roll, and it never expires on a deadline.
- Each beat declares its own search band. Author the sequence outward, and "you already found everything near you" is true by construction.
- Each beat chooses whether its site persists until resolved or expires. Either way a lost site returns its beat to eligible.
- The Waystone's inspect line says *something is out there your instrument cannot resolve*. It never says what or where. The next apparatus's research entry says what it will find.
- A Star Table reads the stars: it works outdoors only, and the roof ban comes free.
- Caravans and scout posts turn up ordinary sites next to themselves. A mining camp does not look, and an outpost with an unresolved find stops looking.
- Lore left in a site: a mural becomes a "read" object, and its passage can be re-read from History by both players, with Intel paid once per record and "N of M records recovered".
- Under orbital route A the spine walks off the planet: the ending's "pointing out of the universe" on the instrument the colony built in the Neolithic.

**What it cannot do**
- Nothing names a beat or its location before it is found. The player cannot steer between the pools. The Waystone cannot tell "the site cannot be placed" from "you have done every beat" (T-39).
- As shipped, the draw inside a band is uniform. "Prefer the near end" costs code.
- Natural finds are survey content only and never reach the spine. Nothing that flies finds anything. A caravan standing still does not re-roll, and foraging cannot be told apart from marching. No shipped state records where the colony has been; whatever records it is ours.
- Lore on a site must be read by a right-click order. Designating it succeeds visibly and is never worked (T-62). VEF's study sends no quest signal (T-60), so a beat keyed on "studied" needs our override.
- Removing a beat def between saves silently renumbers every later beat. Renaming a lore key makes it pay twice.
- A survey quest must carry weight above 0 with `randomlySelectable false`: at weight 0 it is never drawn (T-212), and `isRootSpecial` keeps it out of nothing. A pool quest must carry no giver tag, or a trader can hand it over. A runtime def write outlives the save that made it (T-211). Anything nested under the Chronicle's parent advances its cursor (T-209).
- Odyssey's orbital quests ignore bands and always land 1–3 tiles out. A worked apparatus indoors or aboard a roofed ship hits the roof ban unless `CanUseNow` is overridden.
- Orbital routes B, C and D put a non-labour discovery source in orbit. Each needs the requirement's "only systemic source of unannounced sites" and "discovery is labour" clauses amended. A spine beat must never ride the scanner's quest tag.
- A graded road rung waits on T-42 being fixed; until then road tier carries no information.

**Spec and tickets:** [`specs/CHARTING.md`](specs/CHARTING.md) · #57 discovery engine, #89 travel and tenure, #80 site lore, #146 natural discovery, #149 scanner and Charting, #40 beat carrier and root node, #61 progress display routes, #197 era-relative pool membership, #196 subplot parents

---

### World infrastructure

**Possible?** Yes. Roads are a shipped engine system with no builder: NPC road growth over time is a build of ours, because nothing in the corpus does it. Contribution has five entry points, direct building ships, and vehicles ship as content. Funding to a higher tier works when the network's own tier sits below the era ceiling (#194). NPC factions can field vehicles from Industrial, through our code on Vehicle Framework's dormant raid layer (#195).
**Multiplayer?** With work.
- Vehicles desync silently without § 4a's three prefixes (T-74).
- Funding commits need `[SyncMethod]`s. The float-menu, quest and pod forms are synced for free. The comms-console form needs T-82/T-95/T-97 discipline.
- VF's per-def settings are a T-18 surface.

Roads make the world's era and alliances readable on the map. Every civilization paves toward its own and allied neighbours at a tier the era sets, visibly over about thirty days. The player can fund a named route or pave one. Vehicles are the Industrial rung of the same mobility ladder.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| The world does not start paved, and road tiers differ in travel speed | Yes | Unknown: spec silent on §§ 1–2 (def data) | **A (as specced)** remove the ancient-roads worldgen step and take stone roads out of the worldgen draw, leaving dirt paths and tracks. A freeze item (#18); the xpaths are unrun (#102) · XML · Easy *(mapped)*<br>A five-step speed ladder on the road defs, retunable any time · XML · Easy *(mapped)*<br>`neverConnectToRoads` on factions that stay isolated · VEF · XML · Easy *(mapped)* | [§ 1](specs/WORLD-INFRASTRUCTURE.md#1-differentiate-the-tiers--the-change-everything-else-rests-on), [§ 2](specs/WORLD-INFRASTRUCTURE.md#2-suppress-the-asphalt-at-worldgen--two-patchoperations-no-c) |
| Road dependence: ground vehicles fast on roads, near-useless off them (a strong want) | Yes; the rest is numbers | A Yes (spec: "def data, merged identically on both clients"); B–D Unknown | **A (selected)** a VF cost extension on the five road defs, so every vehicle, including future ones, sees the ladder · XML · Easy *(mapped)*<br>**B** a postfix keeping a per-vehicle road dial · C# · Medium *(mapped)*<br>**C** strip 14 VVE declarations · XML · Easy *(mapped)* · *not recommended*: dominated by A<br>**D** explicit per-tier dictionaries on 14 vehicles; keeps both dials but misses future vehicles · XML · Easy *(mapped)*<br>The off-road half is each vehicle's `offRoadMultiplier` | [§ 4c](specs/WORLD-INFRASTRUCTURE.md#4c-the-interaction-with-1--the-road-cost-override-and-the-fix-that-closes-it) |
| Every civilization builds and upgrades routes toward its nearby own and allied settlements, visibly over time, from each era advance. A broken alliance pauses a project; a captured endpoint completes it | Yes. Inter-faction routes wait on POLITICS' alliance seed (T-100) | Yes (spec), condition: every write on the synced tick or inside a `[SyncMethod]`; options with a `SyncMethod` owe the two-client test (Verification 8) | **Minimal** hand-authored routes; loses derived civilizations and "extend farther" · ours · C#, 1 Harmony · Medium *(mapped)*<br>**Middle** no clause lost · C#, 2 Harmony, 1 `SyncMethod` · Hard *(mapped)*<br>**As specified** `WorldComponent_RoadNetwork`: plans on each advance, lays edges on the world tick; the road on the map is the progress bar · C#, 2 Harmony, 2 `SyncMethod`s · Hard *(mapped)* | [§ 3](specs/WORLD-INFRASTRUCTURE.md#3-era-driven-route-construction--worldcomponent_roadnetwork), [Three road scopes](specs/WORLD-INFRASTRUCTURE.md#three-road-scopes--priced-options-not-a-selection) |
| The player funds a specific, named route, sooner, farther or at a higher tier, distinguishably from a gift, through an era-appropriate channel | Yes | Per route | **C1** a caravan at an endpoint settlement · C# · Medium · Yes as a float-menu option; the path-tile gizmo needs its own `SyncMethod` (T-80)<br>**C2** the builder asks: a delivery quest with a deadline that names the route · XML + small C# · Medium · Yes<br>**C3** the comms console, the radio beat · C# · Medium · With work (T-82, T-95, T-97)<br>**C4** pod or shuttle to an endpoint · C# · Medium · Yes<br>**C5** pledge by messenger or radio, deliver by caravan · C# · Medium · as C2 + C3<br>**Gift variant** vanilla gifts, ~25 lines, no `SyncMethod` of ours · Medium *(mapped)*; funds a *faction*, not a route, and drops "farther"<br>Spec recommends C1 (float menu) + C2, C3 at Industrial, and C5 if Medieval Overhaul's messenger table ships | [§ Contribute](specs/WORLD-INFRASTRUCTURE.md#the-players-verb-on-a-route--contribute), [§ 3d](specs/WORLD-INFRASTRUCTURE.md#3d-funding--the-players-first-verb) |
| Funding makes a route reach a higher tier than the network would have chosen, never above the era | Yes, if the network's default tier sits below the era ceiling; above-era is blocked by ERA | Yes: one more argument on the C1–C5 commits | **H1** the builder's own tech caps the network; funding lifts the route to the era's tier · C# + XML · Easy on top of § 3 (spec recommends)<br>**H2** the network runs one rung behind the era; funding buys the era's tier · XML (repoint) · Easy, or new in-between road defs · Medium<br>**H3** one rung above the era, bought (RimPacts' shape) · Easy for the engine · blocked by ERA's acquisition ceiling | [§ 3d Higher](specs/WORLD-INFRASTRUCTURE.md#higher--a-tier-the-network-would-not-have-chosen) |
| The colony builds roads directly | Yes | Yes (spec: MP Compat syncs VFE Classical) | **Build A** VFE Classical as shipped, with our road tiers in XML. Its one research gate opens every tier (T-202) · XML · Easy *(mapped)*, all tiers at once; a per-tier gate adds a postfix on `AddRoadGizmos` · C# · Medium. Spec recommends it while VFE Classical is in the set<br>**Build B** our own reimplementation · C#, 1 `SyncMethod` · Medium *(mapped)* | [§ 3e](specs/WORLD-INFRASTRUCTURE.md#3e-direct-construction--the-second-verb-shipped) |
| Vehicles: world speed, carrying capacity, combat platforms, aircraft as a separate rung | Yes | With work: § 4a is mandatory, or vehicles desync (T-74) | **A (as specced)** Vehicle Framework + VVE as shipped, plus three Harmony prefixes that keep vehicle pathing on the synced tick · C# · Medium *(mapped)*. There is no Build B; the alternative is no Industrial mobility rung<br>Aircraft re-gated to their own research · XML · Easy *(mapped)* | [§ 4](specs/WORLD-INFRASTRUCTURE.md#4-vehicles--the-second-half-of-the-mobility-ladder), [§ 4a](specs/WORLD-INFRASTRUCTURE.md#4a-put-vehicle-pathing-back-on-the-synced-tick--three-harmony-prefixes) |
| NPC factions field vehicles their era affords: in raids, caravans or defence | Partly: from Industrial only, since every vehicle on disk is Industrial. Vehicle Framework's NPC raid layer ships as data and is dead in code (T-205) | With work: § 4a's prefixes are a hard prerequisite, because NPC vehicles pathfind on the thread pool too (T-74) | **N1** vehicles in hostile raids and base defenders, our copy of VF's dormant injection gated on the campaign era (VF's own reads the faction's raw tech, T-206) · C# + XML · Medium<br>**N2** armored-assault behaviour, supplying VF's unused `LordJob_ArmoredAssault` · Medium<br>**N3** a vehicle in a trader caravan · C# · Medium<br>**N4** crewless parked vehicles at NPC sites · Worksites Expanded as shipped · Easy · MP Unknown (no MP Compat class), or our genstep · Medium<br>**N5** pre-Industrial vehicles · our own defs and art · Medium<br>**N6** a vehicle pawn kind in faction groups · *not recommended*: no crew, never moves<br>Spec recommends N1 + N2, with N4 if Worksites ships | [§ 4d](specs/WORLD-INFRASTRUCTURE.md#4d-npc-factions-fielding-vehicles--raids-caravans-defence) |
| Completed mobility widens Charting's reach (offered, not selected) | Yes | Unknown (spec silent) | **A** road rungs on each tier's research · XML · Easy *(mapped)*<br>**B** vehicle rungs on VVE's research · XML · Easy *(mapped)*<br>**C** a rung satisfied only by a road actually leaving a colony tile · C# · Medium *(mapped)*<br>The apparatus still clamps whatever the rungs offer | [Charting reach rungs](specs/WORLD-INFRASTRUCTURE.md#charting-reach-rungs--offered-not-selected) |

**What the story can do with it**
- At each era advance, a letter names how many routes the world starts building. Half-built roads visibly grow on the map. An endpoint's inspect line reads *"Stone road to Ashvale (Kingdom of Ruen): 12 / 30 segments, about 9 days."*
- An ally can pave a road to the colony's door: a player colony is an eligible endpoint for a builder allied to the player.
- Taking a corridor means taking the settlements at its ends. A captured endpoint completes the road for its new owner; a broken alliance pauses it. The completed-route record says whose road it was.
- The funding channel climbs the eras: a caravan at the endpoint, the builder asking with a deadline (*"for the road to Ruen"*), the radio at Industrial as its own beat (or a Medieval messenger table if Medieval Overhaul ships), then pods.
- Isolated factions, the anima tribe or a high-tech stronghold, can be left off the network entirely, at one field each.
- At Industrial, vehicles make the reachable world explode outward. Aircraft are a later, separate step from the first car.
- Paving matters much more to vehicles than to walkers: the proposed ladder makes seven VVE vehicles 3× slower on dirt paths. A balance call with teeth.
- A road the colony paid for can out-tier its neighbours for good.
- Hostile Industrial factions raid and defend with crewed combat vehicles; an NPC motor pool can be a prize.

**What it cannot do**
- Roads never degrade, and nothing anywhere removes or downgrades one (T-43). Roads have no ownership or contest, so a beat about wrecking or seizing a road itself has no carrier.
- There are no routes between factions until POLITICS seeds NPC alliances. Vanilla creates none, and only the route-count letter says so (T-100).
- A route through a no-roads biome is drawn and gives no speed (T-44).
- "No paved roads at start" must be decided before world creation (#18). It does not remove the 1–2 wrecks per map, and it scatters them map-wide instead ([Era](#era) AE-3/AE-7).
- Below Industrial, no vehicle exists anywhere in the corpus. A cart rung, for the colony or for NPC factions, needs our own defs and art (N5).
- Funding cannot buy a tier above the era. No allied vehicle reinforcements or NPC aircraft are routed.
- Road tier is a silent no-op until the ladder (T-42) and, for vehicles, § 4c (T-87) land.
- "Farther" reaches another settlement or the colony, never a bare tile. A float-menu contribution needs to stand at an endpoint settlement. An endpoint destroyed and recreated at transfer orphans its route unless it is re-bound (T-140).
- Speeds differ across installs if VF's per-def settings differ (T-18). VF's own multithreading switch cannot be set (T-75).

**Spec and tickets:** [`specs/WORLD-INFRASTRUCTURE.md`](specs/WORLD-INFRASTRUCTURE.md) · #68 roads, #69 vehicles, #154 contributing to a route, #174 route threats cut, #128 requirement clauses, #194 higher tier, #195 NPC vehicles

---

### Orbit

**Possible?** Partly.
- Closing orbit before the reveal rests on our content switches, not on a vanilla gate. Odyssey populates orbit at world creation, its own gate is open from the first tick, and emptying the layer alone leaves flight open.
- The reveal, the populated board, holding every giver shut and quest strongholds are all Yes.
- Whether the roster exemption's `Empire` row breaches "no exempt faction" is open (#22).

**Multiplayer?** Yes (spec), condition: the reveal is one `[SyncMethod]` on our `WorldComponent`, and map generation stays on vanilla's seeded path. With work in two places: re-opening a re-tagged giver at runtime (R4, T-173), and World Tech Level's filters (R5, T-18).

Before the reveal, orbit does not exist for the players. At the reveal, one synced moment for both founders, the offworld board appears in full: the spacer powers, the institutions the planetary resolution carried upward, and the Glitterite settlements. The spec also owns how an orbital stronghold map generates, and what a quest can make it hold.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| Before the reveal, orbit is completely closed: no view, no flight, no sites | Partly | Yes (spec) | **A** empty the layer. The view button greys, with Odyssey's own "No discovered orbital locations." It does **not** stop flight · Odyssey defs + our patches · XML · Easy<br>**B** a gated layer class: view, flight path and render all refuse until the flag flips. Must be decided before world creation · C# subclass, no Harmony · Medium<br>**C** a selection chokepoint; works on an existing world, but is a display gate only · Harmony · Medium<br>Spec recommends A + B; C if the decision comes after world creation | [§ The reveal gate](specs/ORBIT.md#the-reveal-gate--what-closes-orbit-and-what-opens-it) |
| No orbital quest is given before the reveal, from the scanner, the ancient uplink, VGE's cluster or GravTech's core | Yes | Yes (spec); R4 reopen and R5 With work | **R1** remove the givers, or research-lock them behind a project the reveal completes · XML · Easy<br>**R2** flag-gated giver comps; a hacked uplink can bank its coordinate · C# + XML · Medium<br>**R3** a Harmony gate at the givers; works on an existing save, but spends an uplink hack · C# · Medium<br>**R4** re-tag with a sink quest (surface finds or lore) · XML to close (Easy), C# to reopen (Medium, T-173)<br>**R5** World Tech Level: an *era* gate, not a reveal gate, and it moves #7's frozen set · XML · Easy · T-18<br>Spec recommends R1 (R2 on the uplink if the story keeps its hack) under Charting's orbital route A; R3 if the scanner stays; R5 only as defence in depth | [§ Holding every giver shut](specs/ORBIT.md#holding-every-orbitalscanner-giver-shut) |
| Nothing in orbit makes contact until the colony can reach or talk to orbit: traders, or hidden Salvagers raiding | Yes | Unknown (spec silent) | Traders: vanilla's comms-console and beacon stage. A later stage is a postfix on the arrival incident's chance (PRESSURE § *The build* › 4) · C# · Medium *(mapped)*. Or the incident is removed by a scenario part · XML · Easy *(mapped)*<br>Salvagers: a raid-faction selection prefix that reads the reveal flag · C# · Medium *(mapped)*. [I] on the predicate; T-17 applies | [§ Open questions](specs/ORBIT.md#open-questions-1), [hidden faction raids](specs/ORBIT.md#a-hidden-faction-raids-before-the-reveal) |
| The reveal is earned, fires once for the world, and survives losing whatever earned it | Yes | Yes (spec), condition: the flag is written only by the synced reveal | The carrier is whatever the fiction wants: a world flag (Easy), a research project (Easy–Medium), or a quest reward or event (Easy, permanent only if it writes the flag). Not the scanner or the signal jammer, both losable. The state is always one flag, written by `RevealOrbit` · ours · C# · Medium *(mapped)* | [§ What the player obtains](specs/ORBIT.md#what-the-player-obtains), [§ 5](specs/ORBIT.md#5-the-gate-state--ours-and-it-is-new-code) |
| At the reveal orbit is populated: spacer powers, surface institutions carried up, Glitterite settlements | Yes | Yes (spec) | **A (as specced)** orbital factions are generated hidden at worldgen, then unhidden and placed by one synced command. A surface faction gains orbital stations the same way, with an optional def swap to read as "ascended" (#8's leak list) · vanilla + ours · C# · Medium *(mapped)*<br>**B** create factions at runtime · *not recommended*: re-rolls name, colour, ideology and leader, has no shared history, and the layer overload has no precedent in the corpus | [§ 1](specs/ORBIT.md#1-worldgen--the-roster-complete-and-invisible), [§ 3](specs/ORBIT.md#3-the-reveal--one-synced-command), [§ 4](specs/ORBIT.md#4-who-came-with-you-is-not-a-new-faction-question), [escape hatch](specs/ORBIT.md#the-escape-hatch-and-why-we-are-not-using-it) |
| The orbital roster survives world creation | Yes; whether its `Empire` row breaches "no exempt faction" is open (#22) | Unknown (spec silent) | **A (as specced)** a `TechLevelConfigDef` exempting the four orbital factions and `Empire`. It is insurance behind `Filter_Factions` being frozen off. The settings-list route is rejected (T-18) · WTL · XML · Easy *(mapped)* | [§ WTL deletes the roster](specs/ORBIT.md#world-tech-level-deletes-the-orbital-roster-at-world-creation) |
| Stronghold maps: floored, heated, pressurised, and different every visit | Yes | Yes (spec: seeded, no `System.Random`) | **A** stronghold as a faction settlement · Odyssey + ours · XML · Easy *(mapped)*<br>**B** stronghold as a quest site (`Opportunity_AbandonedPlatform` verbatim) · Odyssey · XML · Easy *(mapped)*<br>KCSG on orbit · *not recommended*: it can never pressurise | [§ 6](specs/ORBIT.md#6-the-stronghold-interior--odyssey-generates-it-and-every-knob-is-xml) |
| A stronghold that a quest generates holds what the quest needs, is defended, and can be reached | Yes | Yes (spec); C6 With work | Shape: **S1** quest site (spec recommends) · **S2** standing settlement, which still needs S1 as fallback · both Medium<br>Contents: **C1** layout room · XML · Easy · **C2** a quest-held item placed and tracked · Medium · **C4** a world-side record · Medium · **C3**, **C5**, **C6** *not recommended*<br>Defenders: **E1–E4** room threats, garrison, station guns, response raids · XML · Easy · **E5** a boss · Easy with BTG, Medium ours<br>Reachability: **RA1** layout only ("usually") · Easy · **RA2** verify and repair · Medium · **RA3** reward on arrival · Easy | [§ A stronghold a quest generates](specs/ORBIT.md#a-stronghold-a-quest-generates) |
| Leaving, coming back, and failing | Yes | Yes (spec) | **M1** vanilla discard · Easy · **M2** the site stays while the item remains, and a return finds a fresh map around the same item · Medium · **M3** park the gravship (player-side)<br>**F1** a standing parent re-offers · Medium · **F2** the quest re-offers itself · Medium · **F3** VEF re-grant · Easy · *not recommended for plot* · **F4** storyteller refire · Easy · *not recommended*: no guarantee | [Map lifetime](specs/ORBIT.md#map-lifetime--leaving-and-coming-back), [Failure](specs/ORBIT.md#failure-and-regeneration) |

**What the story can do with it**
- The reveal is a curtain: one synced moment, both founders, the whole board at once. Its carrier can be whatever the fiction wants, and the flag keeps orbit open even if that object is later lost.
- A Neolithic colonist who hacks an ancient uplink can bank the coordinate and have it pay off at the reveal (R2, [I]). Alternatively the uplink stays scenery whose hack yields nothing (R1), or the givers point at something planet-side until then (R4).
- Terrestrial institutions go up with the players: an existing faction gets stations with its name, relations and history intact, and can read as ascended.
- Glitterite stations can be made **reachable only with a signal jammer aboard**. The per-destination gate is honoured by the pilot console and by `CompLaunchable`, and reads the *live* ship. GRAVSHIP's worked deck puts a `SignalJammer` on the bridge. It is a key the players can build, and a lost jammer re-closes the gate.
- Each stronghold flavour re-rolls its floor plan every visit. Per flavour: breach chance, derelict or intact, hackable blast doors or one pre-hacked.
- A heist from parts: a named item in the vault that tells the quest when it is found, destroyed or carried off; a raid countdown once inside (none if the gravship landed there); a boss in the objective room. Success can mean pickup, extraction (M2) or arrival (RA3).
- A failed stronghold can come back fresh after an interval (F1). The hidden Salvagers can be held back until the reveal [I].

**What it cannot do**
- Odyssey puts 3–20 asteroids in orbit at world creation. Without our switches the view-orbit button works from day one, and scrolling out bypasses the button unless the zoom connection is patched (T-05).
- Emptying the layer does not stop a ship flying straight up: the layer hop is free and costs 50 chemfuel. True unreachability is route B (pre-worldgen) or C.
- The orbital roster, route B's layer class and the orbit layer's size are all fixed at world creation (T-07, T-45). World Tech Level's faction filter, if on, silently deletes the roster (T-54). The design needs a world generated after the `<hidden>` patch lands.
- A world object cannot hide: anything that exists in orbit is drawn. Hiding a faction does not stop its hostile raids.
- The ancient uplink needs no research, only a pawn with Intellectual 6, and it arrives eight ways. Several (Scarlands and Glacial Plain maps, quest sites, gravcore sites) are not closed by World Tech Level.
- Never empty the scanner tag's quest list: the givers then throw every tick. A stronghold giver of ours must itself read the reveal flag, or it opens orbit early.
- After the reveal, the storyteller delivers only 2 of the 18 orbit-eligible quests. The rest need a giver.
- A vanilla quest site is destroyed when left, so there is no return without M2 or M3. Layout generation skips silently (T-154), so a plot-critical item needs C2 or RA2. A genstep missing `<temperature>` spawns the interior at −75 °C.

**Spec and tickets:** [`specs/ORBIT.md`](specs/ORBIT.md) · #70 deferred orbital instantiation, #148 reveal gate, #180 scanner givers, #151 quest strongholds, #66 stronghold interior · open: #22 era-gate claims

---

### Gravship

**Possible?** Partly.
- Living aboard permanently is a retier-and-patch job on shipped content: Yes.
- Ordinary life that *arrives* at an orbital home is shut by four gates and is recoverable mostly by XML. No route makes walking on or off an orbital map possible.
- A ship in flight when its landing tile changes hands: Yes.

**Multiplayer?** Yes (spec) for orbital life and the ship en route, with two exceptions: route F (Better Traders Guild) is No, and GF-F built as our own dialog is With work. The home build is Unknown: the spec gives no verdict and names two concerns, the client-local settlement-cap slider and a naming dialog opened from a shared tick path.

The gravship grows from late-Industrial transport into the colony's only home, and in orbit it is the only exit. The spec prices the deck budget, life support, food and defenses. It says which parts of ordinary colony life survive on the orbit layer, and what a ship already in flight does when its destination changes hands.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| The colony lives aboard permanently, with the planetside base retired: deck, air, heat, food, power, shields | Yes ([I] that it composes) | Unknown: no verdict; two concerns named | **A (as specced)** Odyssey + VGE as shipped. A research retier moves habitation to Spacer · XML · Easy *(mapped)*. An over-budget alert, because overflow is otherwise silent (T-46) · C# · Medium *(mapped)*<br>**G** remove the standing cabin-fever penalty · XML · Easy · *not recommended* | [§ The build](specs/GRAVSHIP.md#the-build), [§ The deck budget](specs/GRAVSHIP.md#the-deck-budget), [§ Life support](specs/GRAVSHIP.md#life-support) |
| The founders are vacuum-immune; everyone else wears suits | Yes | Unknown (spec silent) | **A** vanilla's archite gene `VacuumResistance_Total`. The gene needs no code; delivery weight is not stated. The spec's only delivery sketch is an archite-capsule supply line; the altar's named-gene grant ([ALTAR § 9](specs/ALTAR.md)) is a story delivery that needs no capsules. The route is #119's | [§ Life support](specs/GRAVSHIP.md#life-support) |
| Disasters, conditions and threats that make sense in space happen in orbit | Yes (spec: "All of it is reachable; most of it by XML") | Yes (spec) | **A** a whitelist pack across orbit's four gates: incidents, game conditions, faction arrivals, arrival modes · XML · Easy per def, Medium as a curated pack<br>**B** VGE's 9 orbital incidents and 8 matching conditions, as shipped · Easy<br>Spec recommends A + B + C | [§ Ordinary colony life](specs/GRAVSHIP.md#ordinary-colony-life-on-an-orbital-home), [four gates](specs/GRAVSHIP.md#the-four-gates-and-what-passes-them-today) |
| People arrive and join, and quests are offered, at an orbital home | Partly: no walking in, ever | Yes (spec); build (d) Unknown | **C** authored arrivals by pod and shuttle · XML · Medium<br>**D** vanilla's wanderer and refugee-pod family unblocked in orbit · C# · Medium<br>**Build (d)** a null-home patch for two quest nodes, needed only if our content uses them (T-49) · C# · Medium *(mapped)* | [Nobody joins](specs/GRAVSHIP.md#nobody-joins-and-the-flag-that-says-otherwise-is-a-dead-letter), [Quests](specs/GRAVSHIP.md#quests-are-gated-somewhere-else-entirely) |
| Visitors and traders at the ship; trade at stations | Partly | Yes (spec); F No | **E** visitors and walking trader caravans redirected off the impassable map edge · C# · Medium<br>**F** shuttle to a guild station and trade there · Better Traders Guild · as shipped · Easy · MP **No** | [§ Routes](specs/GRAVSHIP.md#routes) |
| A ship in flight keeps the player's commitment when its landing tile changes hands | Yes | Yes (spec); GF-F as our own dialog With work (T-82/T-95/T-96) | **GF-A** vanilla: lands on the new occupant, and an ally is attacked and turns hostile · Easy · *not recommended alone*<br>**GF-B** our transfers sweep the one ship in flight · C# · Medium<br>**GF-C** divert: home, nearest tile, or vanilla's crash-landing abort · C# · Medium<br>**GF-D** protect the endpoint: skip, defer until touchdown, or reserve the tile · C# · Medium<br>**GF-E** accept, and warn while the ship is still in the air · C# · Easy–Medium<br>**GF-F** the changed arrival becomes a decision · C# · Medium–Hard<br>**GF-G** guard at touchdown, whoever changed the tile · Harmony · Medium<br>Spec recommends GF-G feeding GF-F's vanilla landing marker, with GF-E's line | [§ En route](specs/GRAVSHIP.md#a-gravship-en-route-when-its-landing-tile-changes-hands) |
| The hull mounts an era defense ladder | Yes | Unknown (spec silent) | **A (as specced)** shields, turrets, point defense and Ultra guns, retiered in XML · Easy *(mapped)*. Mortars need orbit added to their manned-building gate (the fifth gate) · XML · Easy · [I] | [§ Defenses](specs/GRAVSHIP.md#defenses), [four gates](specs/GRAVSHIP.md#the-four-gates-and-what-passes-them-today) |

**What the story can do with it**
- The ship grows from short-range transport to home. Leaving the planet is the players' choice, and the planetside base can be kept. Cabin size is the deck's main lever: 22–40% of the budget.
- Gravcores are the real clock: at one per 15–30 days, fitting out the ship is a 300–500 day arc whatever the player does [I]. That gives the Spacer act a pacing spine.
- A breach kills the crop outright, it does not just stall it. The farm becomes a raid target, and split farms and sealant poppers are real answers.
- Shields come in bursts: 100 seconds up, a 4-hour charge, an EMP opens the window, and killing the grav engine stops them charging.
- The crew wants sky: a standing −5 cabin fever that only walks outside in suits (or indoor-lovers) avoid. The spec calls it a beat.
- In orbit, raiders fight to the last pawn, sappers decompress the hull, and prisoners can only be recruited, executed, sold or outlived.
- Orbital weather ships ready (VGE): solar flares, micrometeor storms, and escape pods that punch the hull and hold a stranger.
- A changed landing tile can become a scene: guns at the pad, a toll, a parley, or going round (GF-F). The transfer letter can warn while the ship is still in the air (GF-E).

**What it cannot do**
- There are no caravans in orbit and no walking on or off the map, ever. Nobody who arrives can leave. There is no siege and no breaching, and no wild animals.
- No vanilla joiner quest can generate on an orbit-only home (T-128). Whitelisting visitors or trader caravans is a silent no-op.
- Only four factions can reach an orbital home: Traders Guild, Salvagers, Mechanoids and Empire. Pirates, outlanders and tribals cannot. Insectoids never can while VFE Insectoids is loaded.
- Orbital settlements cannot be visited peacefully, except through Better Traders Guild, which Multiplayer does not cover. Mortars cannot be manned in orbit as shipped.
- The ship always lands: there is no hover, no cancel and no in-flight redirect. Landing on any non-player settlement counts as an attack (T-171). Under VGE the commitment starts at the launch ritual (T-172). Only one gravship flies at a time.
- If the ship loses its engine in orbit, there is no way off the tile. The spec names this campaign softlock.
- Deck overflow is dropped silently at launch (T-46). Stone, wood or obsidian walls never hold air (T-47). VGE alone lowers the deck ceiling below vanilla's; read it off the engine, never add up defs (T-50).
- Reading has not settled whether drop pods can land on a fully roofed hull (a RUN item). If they cannot, every drop-based arrival needs an open pad.

**Spec and tickets:** [`specs/GRAVSHIP.md`](specs/GRAVSHIP.md) · #71 gravship as home, #147 orbital colony life, #177 ship en route, #127 founders' vacuum immunity

---

## Colony

### Colony management

**Possible?** Yes. The era-sorted add-bill menu and passion-led recreation each sit on one vanilla seam. Nothing on disk does either today, so every route is ours.
**Multiplayer?** Yes. The menu works per player at draw time; a filter state *shared* by both players needs a synced field, and the Nice Bill Tab routes carry its unsynced bill writes. Recreation reads only synced pawn and def state.

This card covers the friction of running the colony: which recipes a bench puts in front of the player, and what a pawn does when it goes to relax.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| A bench's add-bill list foregrounds the recipes of the colony's current era. It is presentation, never a content gate | Yes | Yes (per player); a shared filter state is with work | **A** era checkboxes: unticked eras are not listed, and unkeyed recipes fail open · ours on `ITab_Bills` → `BillStack.DoListing`, FloatSubMenu donor · C# · Medium<br>**B** current era first; older eras tinted, sorted below, or folded into submenus; nothing hidden · same seam · C# · Medium<br>**C** era-limited benches · XML patches on `recipeUsers`, VEF `RecipeInheritanceExtension` · XML · Hard in aggregate · *not recommended*: cannot shorten the list and keep older recipes reachable; re-homes ~1,420 recipes<br>**D** search only · Nice Bill Tab as shipped, or our own search row · mod · C# · Easy (NBT; MP with work) / Medium (ours) · *does not meet the requirement alone*: no notion of era; it accompanies A or B<br>**E** Nice Bill Tab with an era axis · NBT patched or forked · C# · Hard · MP with work<br>**F** hide through `AvailableOnNow` · custom `workerClass` per recipe · XML + C# · Medium · *not recommended*: it changes list membership, and paste validation reads it<br>Spec recommends B, with A's checkboxes and D's search row on the same patch | [§ The add-bill menu shows what matters now](specs/COLONY.md#the-add-bill-menu-shows-what-matters-now) |
| A pawn at recreation prefers recreation that trains a skill it is passionate about, major passion first | Yes | Yes | **A** a passion factor on each giver's chance gives a drift, not a rule, and covers every `joySkill` job in the bin automatically · Harmony postfix on `JoyGiver.GetChance` · C# · Medium (low end)<br>**B** a passion-first think node: "always goes and shoots" while it can, with fallback when bored · our `JobGiver_GetJoy` subclass + think-tree XPath · C# + XML · Medium<br>**C** our JoyGiver subclasses · C# + XML · Medium · *not recommended*: A's result with more surface<br>**E** raise `baseChance` on all training recreation · XML · Easy · *not recommended*: ignores passion<br>**F** transpile `JobGiver_GetJoy.TryGiveJob` · C# · Medium · *not recommended*: reaches nothing on disk that A misses<br>Spec recommends A (+D); B only if the story wants the hard rule | [§ Recreation follows a pawn's passions](specs/COLONY.md#recreation-follows-a-pawns-passions) |
| Passion recreation reaches skills that no recreation job trains (7 of 12) | Partly | Yes | **D** reading prefers textbooks on the pawn's passion skills; vanilla textbooks cover all 12 · patch on `BookUtility.TryGetRandomBookToRead` · C# · Medium · composes with A<br>Otherwise, new `joySkill` recreation is plain XML content, and route A picks it up with no further code | [§ Recreation follows a pawn's passions](specs/COLONY.md#recreation-follows-a-pawns-passions) |

**What the story can do with it**
- Give each era its own menu. The Neolithic bench shows Neolithic work first, with older recipes tinted, folded away or one click off. The two players may see different menus (T-21).
- Choose whether passion is a drift (A) or a rule (B): a passionate shooter goes and shoots every time it can.
- Make reading the route to the "boring" skills: a passionate doctor picks the medicine textbook.
- Add recreation in XML, such as an archery butt or a forge game, and have it join the preference with no code. Give it its own `joyKind` so boredom does not land on the whole skill at once.

**What it cannot do**
- The menu never gates content. 334 of 1,420 bench recipes (24%) have no research prerequisite and escape the era ceiling. An XML `researchPrerequisite` closes each one, and which recipes get one is the progression grids' call (#30).
- `RecipeDef` has no `techLevel`. A recipe's era must be derived (K1 research → K2 product → K3 authored → K4 floor), and which key is the truth is unsettled (#30).
- Each player sees one menu surface at a time: while Nice Bill Tab is on, that player sees its tab and not our menu.
- A per-player filter state has no ratified carve-out in `CODING_STANDARDS.md`, and persisting it in a mod setting breaks the requirement's no-mod-settings rule (T-18).
- Boredom beats any preference. The three vanilla shooting games share one joy kind, so a passionate shooter shoots until it is bored of all three at once, then does something else.
- Preference changes *what* a pawn does for fun, never *how often*.
- Pawns at a Worksites Expanded outpost pick recreation blind to passion, on every route (T-159).
- The passion weight cannot come from a mod setting (T-18). It must sit in a def or a `DefModExtension`.

**Spec and tickets:** [`specs/COLONY.md`](specs/COLONY.md) · #161 add-bill menu, #87 menu mods, #96 what an era shows, #159 recreation, #76 playtest origin

---

### Shipped defaults and presets

**Possible?** Partly for gear sets; Yes for bill defaults and paste.
- *Gear sets:* every clause has a route, but no single shipped mechanism covers the whole gear set. Only route D does, and it is Hard.
- *Bill defaults:* every bill except those on recipes that cannot count products.

**Multiplayer?** Yes for the vanilla kit routes and for bill defaults. With work for our own kit layer (D) and for bill paste, which needs one synced command of ours. No for Better Workbench Management or Compositable Loadouts as they ship.

This card covers what the campaign puts in front of the player already set: role gear sets, the numbers on a new bill, and a bill's settings copied to its siblings.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| Gear sets are authored, shipped and present in a fresh colony | Yes (apparel); partly with the weapon | Yes | **B** apparel presets: a standing entry in the Assign tab of every new colony · our `Def` + `GameComponent`, donor `DrugPolicyDef` · C# · Medium<br>**A** one kit per `ThingDef`: the def ships, but the player must build and stock the stand · Odyssey outfit stand · XML · Easy<br>**E** a kit on *generated* pawns (arrivals, quest pawns, starting colonists) · vanilla `PawnKindDef` · XML · Easy | [§ The whole kit, weapon included](specs/DEFAULTS.md#the-whole-kit-weapon-included) |
| A set covers what the pawn carries, including its weapon | Yes | Yes (A, E); With work (D); No (C) | **A** apparel plus one weapon, swapped in one job · Odyssey `Building_OutfitStand` · XML · Easy<br>**C** weapon, inventory and quality filters · Compositable Loadouts · dependency + C# · Medium · *not recommended*: no MP compat, and it never swaps a weapon already held<br>**D** every clause, standing and authored · our code, donors `JobDriver_UseOutfitStand` + CL's think node · C# · Hard<br>**E** as above, generated pawns only · XML · Easy<br>B carries no weapon | [§ The whole kit, weapon included](specs/DEFAULTS.md#the-whole-kit-weapon-included) |
| Assigning a set is one act, after which the pawn equips itself | Partly: only D is both | Yes (A, B); With work (D) | **B** standing, but not one act, and apparel only · C# · Medium<br>**A** one act, but one-shot: a pawn that loses its weapon does not go back · XML · Easy<br>**D** standing and one act · C# · Hard<br>Spec would cost A + B together first | [§ The whole kit, weapon included](specs/DEFAULTS.md#the-whole-kit-weapon-included) |
| The player can force a pawn to re-equip to its set, and to drop what it carries | Partly | Yes (A); With work (D) | **A** re-targeting the stand's *Swap outfit* is the forced re-equip; the drop removes only apparel that conflicts · XML · Easy<br>**D** both verbs, whole pawn · C# · Hard<br>The weapon alone drops through one vanilla act that MP already syncs (`InterfaceDrop`); apparel drops item by item | [§ The whole kit, weapon included](specs/DEFAULTS.md#the-whole-kit-weapon-included) |
| A set naming gear from an unreached era is not a failure | Yes | Yes | A, B, C and D all tolerate it. The policy's filter allows unreached defs and the pawn wears the best it can reach; a stand simply stays partly empty | [§ The whole kit, weapon included](specs/DEFAULTS.md#the-whole-kit-weapon-included) |
| A new bill opens with its count and both floors set, per recipe, written once and never re-imposed | Partly: not on recipes that cannot count products (reclaim, smelting, butchery; T-58) | Yes | **A (as specced)** one Harmony postfix on `BillUtility.MakeNewBill` applies a per-recipe `Archinity_BillDefaultsDef` table behind three gates: bill type, `CanCountProducts`, and where the sliders render · C# + XML · Medium (mapped) | [§ Half one — bill defaults](specs/DEFAULTS.md#half-one--bill-defaults-95) |
| A bill's configuration can be pasted onto another bill: the settings, never the recipe or the material | Yes | With work (one synced command) | **A** Better Workbench Management as shipped · dependency · Easy · MP No; copies the material whenever the two recipes' fixed filters match<br>**B** BWM with its paste routed through our synced command · C# · Medium · MP with work; inherits the material rule<br>**C** our own paste: we choose the fields, leave the material out, refuse on T-58, message on a skipped field, and can paste onto every bill on a bench · C# · Medium · MP with work<br>**D** our paste riding MP's field watches · C# · Medium · MP No · *not recommended*: syncs less than C for the same code<br>**E** named bill configurations, a "house standard" library both players share · C# · Hard · MP with work<br>Spec recommends C (B if BWM ships anyway) | [§ A bill's configuration, pasted onto another bill](specs/DEFAULTS.md#a-bills-configuration-pasted-onto-another-bill) |

**What the story can do with it**
- Treat kits as places: an armoury of outfit stands, one per role, that hands a pawn its apparel and weapon in one click (A). The colony grows an armoury rather than a settings screen.
- Treat kits as standing wardrobes: a Smith or Miner preset in the Assign tab from day one keeps a pawn dressed as the eras supply better gear (B).
- Send arrivals already kitted, weapon included, in pure XML: "the Waystone's acolytes arrive carrying this" (E).
- Author sets that name tomorrow's gear. A preset naming plate armour in the Neolithic is intended, and the pawn wears the best it can reach.
- Open every crafting bill on "Do until you have N" with a quality floor already set ("five longswords, Good or better"). Set up the chest-armour bill once and paste it onto the gloves, helmet and boots (C).

**What it cannot do**
- The policy layer reaches no weapons. A weapon arrives only through the stand (A), our kit layer (D) or a pawnkind (E).
- There is no vanilla "drop everything" verb, and a healthy colonist cannot be stripped. Only route D makes one.
- A stand holds one weapon, equips one pawn at a time, and transfers once. What it puts on is force-worn, and stays so until the player clears forced apparel.
- Outfit stands need Odyssey and the `ComplexFurniture` research (Medieval), unless a kit def patches that prerequisite off in XML.
- One belt per pawn: a set naming both a tool belt and a shield belt yields one worn item and no message. Mechanitor packs are skipped on non-mechanitors.
- Presets cannot ship as plain XML, because an apparel policy is save state, not a def. Route B's `GameComponent` exists for this.
- Route A has two traps that fail with no error: a kit def without `<thingClass>`, and one whose inherited filter still disallows weapons. Both build, look right and do nothing.
- Bills on recipes that cannot count products stay on "Repeat N", so the target box and both floors never show (T-58).
- Never set a durability floor on the global row; it costs the fast count on counted resources.
- A paste across maps loses a specific stockpile. A pasted worker-skill range is read against the *target* recipe's skill.
- Compositable Loadouts, if it ships, fights the presets. With its setting on, pawns refuse preset gear; with it off, it still rescales their choices. Nothing here may read a mod setting (T-18).

**Spec and tickets:** [`specs/DEFAULTS.md`](specs/DEFAULTS.md) · #155 whole kit with weapon, #157 bill paste, #95 bill defaults, #28 kit presets

---

### Items and gear

**Possible?** Yes. Every clause is met in XML on a vanilla path: smelting, with the stuff flags switched on for cloth, leather, wool and wood.
**Multiplayer?** Yes. "Zero synchronization work": there is no new state, and the only `Rand` is on the bill-completion path, which is already synced.

This card covers reclamation, the counterweight to deprecation. Obsolete apparel, armour and weapons go back to half the material they were made of, at a bench, in whatever era the colony is in.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| Reclaiming returns the material itself, with no intermediate resource | Yes | Yes | **A (as specced)** `SpecialProductType.Smelted` returns the exact stuff the item was made of. One XML patch marks leathers, wools, cloth, synthread, devilstrand, hyperweave and wood smeltable, plus two reclaim `RecipeDef`s (apparel, weapons) · XML · Easy (mapped). No other engine return path is stuff-aware [I] | [§ Mechanism](specs/ITEMS.md#mechanism) · [§ New code and defs](specs/ITEMS.md#new-code-and-defs) |
| Half comes back | Yes | Yes | **A (as specced)** two `<li>Smelted</li>` entries give 50%. The mechanism works in 25% steps only · XML · Easy (mapped) | [§ The return fraction](specs/ITEMS.md#the-return-fraction) |
| The return ignores condition and quality; the player chooses which items to feed | Yes | Yes | **A (as specced)** the return path never reads hit points or quality [V]. The bill's ingredient HP and quality sliders already let the player feed only the tattered or only the awful · XML · Easy (mapped) | [§ Quality and damage](specs/ITEMS.md#quality-and-damage) |
| Reclaiming works in the era the colony is in, Neolithic included | Yes | Yes | **A (as specced)** the crafting spot is a real work table from turn one; a dedicated reclaim bench is a plain XML `ThingDef`; the era is an XML research gate (#30) · XML · Easy (mapped) | [§ New code and defs](specs/ITEMS.md#new-code-and-defs) |
| Relics are never reclaimed, and reclaiming never yields a manufactured resource | Yes | Yes | **A (as specced)** the engine refuses relics. Components, chemfuel, subcores and mech resources are `intricate` and never returned · as shipped · Easy (mapped) | [§ Mechanism](specs/ITEMS.md#mechanism) · [§ Available mechanisms](specs/ITEMS.md#available-mechanisms) |
| The player can find out the proportion before committing an item | Partly: as recipe description text only | Yes | **A (as specced)** the fraction is written into the recipe `<description>`. The info card's efficiency line would show a number the engine ignores (T-56) · XML · Easy (mapped) | [§ Where the player sees it](specs/ITEMS.md#where-the-player-sees-it) |
| A reclaim bill can run "do until you have X" | Partly: needs C# | Yes | **A (as specced)** our `workerCounterClass`, on the precedent of vanilla's stone-block counter · C# (~30 lines) · Medium (mapped). The fixed-`products` alternative is rejected under the no-chains rule | [§ Failure and recovery](specs/ITEMS.md#failure-and-recovery) |

**What the story can do with it**
- Turn a wardrobe of surpassed gear into stock: the tribe unpicks its old leather into leather, and the smiths melt last era's plate into steel.
- Reclaim from day one at the crafting spot, or give reclaiming its own bench that "earns its place by the labour it absorbs". Both are pure XML.
- Let the player be choosy (only the tattered, only the awful-quality) without the yield changing.
- Rely on sanctified relics being safe, with no filter of ours.

**What it cannot do**
- Only 25, 50, 75 and 100% are expressible. A fraction in between, or a yield scaled by condition, needs a Harmony postfix the requirement does not need.
- The number cannot appear on the info card (T-56). `smeltingWorkAmount` is ignored on our recipes (T-57).
- Once the flags flip, vanilla's electric smelter also takes cloth, leather and wooden gear, and so do Medieval Overhaul's furnace and, for weapons, VFE's fuelled smelter. They return vanilla's 25%, beside the reclaim recipe's 50%. Matching them is XML either way: a second `Smelted` entry, or removing the recipes from those benches. The choice is #119's.
- Until the counter ships, reclaim bills are Forever or Repeat N only (T-58).
- Any def we author must leave `smeltProducts` empty, or it smuggles a fixed product into the return.
- A missed stuff patch fails silently as zero output. Whether flipping the textile stuffs has any other consumer is still [I], owed an in-game check.

**Spec and tickets:** [`specs/ITEMS.md`](specs/ITEMS.md) · #82 reclamation (the era is #30's row; the bench is #119's)

---

### Specialisation

**Possible?** Yes, but only through a system of ours (routes A–D, Hard). Nothing on disk carries per-pawn specialisation inside a skill, and no XML-only route meets every clause.
**Multiplayer?** With work. The player's pick must be a synced command; MP Compat's precedents show the shape, and Archinity registers none today. Generation runs in the simulation. The role route rides paths Multiplayer already syncs, subject to #114's one RUN check.

A good smith becomes a weaponsmith or an armoursmith, and a captive's specialisations make it a prize or a disappointment. The fallback is a bounded set of named posts.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| A pawn good at a skill specialises inside it, on the same skill and experience, chosen by the player at intervals as the skill rises | Yes (A–D); not as progression under E, F or G | With work | **A** expertise list: at thresholds, pick one entry from the skill's list · ours, schema donor VSE `ExpertiseDef` (not on disk) · C# + XML · Hard (lightest of A–D)<br>**B** path tree: exclusive branches and tiers; a taken branch closes its sibling · ours, donor VPE · C# + XML · Hard<br>**C** perk catalogue with workers, for advances beyond a stat, such as a yield bonus on one recipe · ours, donor VFE Classical · C# + XML · Hard<br>**D** point board: every option and the unspent total on one screen · ours, donor VFE Tribals (sync shape proven) · C# + XML · Hard<br>Spec recommends A with B's exclusivity plus a VPE-pattern generation postfix; D's board if the pick should feel like a moment | [§ Routes](specs/SPECIALISATION.md#routes) |
| Specialisation is limited to skills the pawn is deeply passionate about | Yes | A–D With work; E Yes; F Yes [I] | **A–D** our gate on `Major` passion · C#<br>**E** posts: a `RoleRequirement` subclass of ours · C# · Medium<br>**F** trained hediff: a small gate subclass · C# · Medium<br>**G** trait: links to passion in XML, but backwards, because generation *creates* the passion to fit the trait | [§ Constraints](specs/SPECIALISATION.md#constraints) |
| Advances are small and numeric, and none unlocks content | Yes | With work (A–D) | Every route carries stat offsets; shipped entries are sized 0.01–0.05 on one stat. C's workers reach effects a stat cannot | [§ Routes](specs/SPECIALISATION.md#routes) |
| A smith can go toward weapons or toward armour | Partly: needs new stats or code | Unknown (spec silent). What would settle it: for the XML form, a statement that def-only stat changes are safe, since DEFAULTS § *The build* says a Def "is read from the same files on both clients… identical by construction"; for the C# form, it rides route C, which is With work | XML: new `StatDef`s, with `workSpeedStat` repointed on the weapon recipe bases · or C#: a reader that knows the recipe (C's worker) | [§ Constraints](specs/SPECIALISATION.md#constraints) |
| Pawns the player did not train arrive already specialised; starting colonists do not | Yes (A–D, F, G); No (E) | Yes [I for our postfix] | **A–D** a generation postfix on VPE's `PawnGen_Patch` pattern rolls entries from final skills and passions, and skips `PlayerStarter` pawns [V] · C#<br>**F** `PawnKindDef.startingHediffs` · XML · bound to the pawnkind, not keyed on skill<br>**G** backstory or pawnkind `forcedTraits` · XML · causality inverted<br>**E** cannot: generation assigns no role | [§ Generated pawns](specs/SPECIALISATION.md#generated-pawns--the-pre-specialised-half-per-route) |
| Scarcity fallback: a bounded set of named posts, each held by one pawn at a time | Partly | Yes (#114, one RUN check) | **E** Ideology specialist roles · vanilla `Precept_Role` · XML · Easy, but at most **two** post types, each unbounded in holders · XML + C# · Medium to bound seats (`Precept_RoleSingle` or a cap of ours), add types past the cap, and gate on passion. Not progression | [§ E. Specialist posts](specs/SPECIALISATION.md#e-specialist-posts-ideology-roles) |
| The commitment is visible, and changing an earned one costs something | Partly: stated for E and F only | E Yes; F Yes [I] | **E** one role per pawn; changing post runs the role-change ritual · XML<br>**F** a "trained as a weaponsmith" hediff, granted by surgery bill, usable item or rite; removed by surgery (`Recipe_RemoveHediff`); exclusive by tag; visible in the Health tab · XML · Easy (ungated) / Medium (skill- or passion-gated, or a rite)<br>**G** trait · XML + C# · Medium · *not recommended over F* unless it should read as who the pawn is<br>The spec does not address re-choosing under A–D | [§ F. Trained hediff](specs/SPECIALISATION.md#f-trained-hediff-at-a-bench-or-a-rite) |

**What the story can do with it**
- Make a captive worth inspecting: a level-10 cook who arrives with *gourmet cooking*, or with the wrong line, is a real prize or a real disappointment (A–D, F).
- Fork a skill: taking weaponsmithing closes armoursmithing, as an exclusion between two entries (A) or a whole tree (B).
- Make the pick a moment with one board, every option, and an alert for unspent advances (D). It is an alert, never a letter.
- Frame specialisation as training: "trained at the forge" at a bench or a rite, carried wherever the pawn goes and visible on strangers too (F).
- Offer named specialist posts with a ritual cost to change (E). These are ideological and tied to the player faith.

**What it cannot do**
- No new skills and no new experience currency. Any points must be derived from skill thresholds crossed.
- "Deeply passionate" can only mean Major; passion has exactly three values. Genes and growth moments can still move passion mid-game, so a gate can open or close under a pawn.
- A specialisation can outlive the level that earned it, because skills above 10 decay.
- Vanilla cannot tell weapon work from armour work: both use `GeneralLaborSpeed`, and quality knows the skill, not the product.
- Ideology posts come with limits:
  - One role per pawn (T-108), so a founder or preacher cannot also be the weaponsmith.
  - Under the Easy form, the preacher takes one of the two post slots.
  - Custom `RoleEffect`s are inert (T-107).
  - A generated pawn holds no role, and a pawn of another faith loses its post.
- The pick cannot be a modded `ChoiceLetter` (T-96), a `Dialog_NodeTree` subclass (T-95) or a write from a draw method (T-85).
- Hediff-held state copies onto Anomaly duplicates (T-113). Numbers read from a mod setting during generation are T-18.
- Passion is not grantable. If it ever ships, it is an altar function; no requirement owns it.

**Spec and tickets:** [`specs/SPECIALISATION.md`](specs/SPECIALISATION.md) · #156 specialisation, #114 role facts, #116 role catalogue (#119 content)

---

### Quests

**Possible?** Yes. Every clause of `requirements/QUESTS.md` has a route: nesting any quest under any parent, a challenge rating on every quest, and the era-relative announcement test. One is only Partly without a build of ours: a finished beat leaves its parent in the list (T-210), so "taken beats stay legible" needs a readout or a tab patch.
**Multiplayer?** With work: one sync registration on the shop's `ActivateQuest`. Charting's find path, decrees and timed encounters run on the synced tick, and Multiplayer syncs quest acceptance as shipped.

Almost everything the campaign delivers arrives as a quest or an event. No spec owns quests; the clauses of [`requirements/QUESTS.md`](requirements/QUESTS.md) are answered across Charting, Currencies, Religion and Encounters.

| Capability | Possible | MP | Routes | Spec |
|---|---|---|---|---|
| The main plot line is a standing, auto-accepted parent quest, with its necessary beats nested beneath it | Yes (main line) | Yes | **A (as specced)** `QuestPart_ChartingSpine : QuestPart_SubquestGenerator` sets `quest.parent` on each beat. The parent is a `QuestScriptDef` with `isRootSpecial`, `autoAccept` and no expiry, plus a ~25-line root node of ours · vanilla subclass, no Harmony · C# + XML · Medium (mapped). VEF quest chains were rejected for the spine (not labour, no player UI) and are recommended for gated side content | [CHARTING § 2](specs/CHARTING.md#2-the-return-pool--questpart_chartingspine--questpart_subquestgenerator) · [§ Alternatives](specs/CHARTING.md#alternatives-and-what-separates-them) |
| Each subplot is its own parent quest, including steps that arrive by purchase or as ordinary offers | Yes. The quests tab reads nothing but `Quest.parent`, so any code can nest any quest from any channel | Yes: the parent is a saved field written in simulation; only the already-flagged `ActivateQuest` needs work | **P** a standing, auto-accepted parent per subplot, fired by a named incident · XML · Easy<br>**N1** set the parent at the grant sites we own (Schism catalogue, the shop's buy) · C# · Medium<br>**N2** one `QuestManager.Add` postfix keyed on a def extension, reaching every channel (storyteller, giver, VFED plot, VEF chain and giver) · C# + XML · Medium<br>**N3** VEF's chain badge · Easy · an icon only, not a route. Spec recommends P + N2. Each subplot needs its own parent (T-209) | [CHARTING § Subplots as parent quests](specs/CHARTING.md#subplots-as-parent-quests--any-quest-nested-taken-beats-kept-a-rating-on-every-quest) · [CURRENCIES § The Schism catalogue](specs/CURRENCIES.md#the-schism-catalogue--a-spend-that-advances-the-plot) |
| Declining, failing or losing a beat never soft-locks its plot line | Yes | Yes | **A (as specced)** only `EndedSuccess` advances the derived cursor. An expired or destroyed site ends the quest non-success, and the same beat is next | [CHARTING § Failure and recovery](specs/CHARTING.md#failure-and-recovery) |
| The player sees where they are in a plot line; taken beats stay legible as taken | Yes with T2 or T3; Partly as shipped: a finished beat drops to the Historical tab, flat (T-210) | Yes | **A (as specced)** the quest tab shows `3 / 9` on the parent and indents live children beneath it, free from vanilla<br>**T1** as shipped: the parent's detail pane lists finished beats · Easy<br>**T2** a quest part writing a live beat list into the parent's description · C# · Medium<br>**T3** a tab patch drawing finished and not-yet-accepted beats under their parent · C# · Medium | [CHARTING § 8](specs/CHARTING.md#8-where-the-player-sees-it) · [CHARTING § Subplots as parent quests](specs/CHARTING.md#subplots-as-parent-quests--any-quest-nested-taken-beats-kept-a-rating-on-every-quest) |
| Every quest declares a challenge rating before commitment | Yes. About 60 visible quest scripts in the corpus declare none, and the tab draws an unrated quest as one star (T-208) | Yes; the shop's registration as before | **C1** `defaultChallengeRating` or `QuestNode_SetChallengeRating` per def, patchable onto any mod's quest · XML · Easy<br>**C2** a fallback rating from points at generation for any unrated quest · C# · Medium<br>**C3** a load-time audit listing unrated quests · Easy<br>VEF's contract window draws one pip per rating and none for an unrated quest (catalogue Build A, T-208); Build B draws it on the offer row. No offer letter shows one | [CHARTING § Subplots as parent quests](specs/CHARTING.md#subplots-as-parent-quests--any-quest-nested-taken-beats-kept-a-rating-on-every-quest) · [CURRENCIES § The purchasable quest catalogue](specs/CURRENCIES.md#the-purchasable-quest-catalogue) |
| A quest states plainly why it is happening | Yes | Yes | **A (as specced)** `QuestUtility.SendLetterQuestAvailable(quest, discoveryMethod)` takes free text for the letter body: one translation key. An encounter can name its asker in the letter (G2) | [CHARTING § 8](specs/CHARTING.md#8-where-the-player-sees-it) |
| What nobody announced is discovered through Charting, and "announced itself" widens with era | Yes | Yes (A); With work (B) | **(as specced)** any quest joins Charting's survey pool through a one-line XML `ChartingSurveyExtension` patch (T-06) · XML · Easy (mapped). A survey quest carries weight above 0 with `randomlySelectable false` (T-212); `isRootSpecial` keeps a quest out of nothing<br>Widening with era: **A** one era test drives both pool membership and `randomlySelectable` · C# · Medium · **B** twin defs plus a WTL row, for quests a named incident delivers · XML · Easy. See the Charting card. Per-quest dispositions belong to the ledger (#14) | [CHARTING § 3](specs/CHARTING.md#3-the-survey-pool) · [CHARTING § Membership that changes with era](specs/CHARTING.md#membership-that-changes-with-era--a-quest-leaving-the-pool) |
| Necessary content never depends on a roll | Yes | Yes | **A (as specced)** the spine is a fixed list in order, with no roll (the Archonexus donor). Each pool carries its own guaranteed-find timer, which labour matures, and `scanFindGuaranteedDays` must be set or there is none. For the Schism, spending elsewhere stalls the plot but never strands it | [CHARTING § 1](specs/CHARTING.md#1-the-apparatus--compchartingapparatus--compscanner) · [§ 2](specs/CHARTING.md#2-the-return-pool--questpart_chartingspine--questpart_subquestgenerator) · [CURRENCIES § The Schism catalogue](specs/CURRENCIES.md#the-schism-catalogue--a-spend-that-advances-the-plot) |
| Channels: storyteller pool, world object, named incident | Yes | Yes | **Storyteller pool:** ENCOUNTERS T3 (`rootSelectionWeight` + `rootEarliestDay`) · XML · Easy. **World object:** the Charting apparatus (CHARTING § 1), and caravans and outposts rolling finds (Natural discovery routes A–E). **Named incident:** T1 and T2 fire a named quest on a fixed day (XML · Easy). T4 is our comp, which offers it once a condition holds; the condition is ours to write, and the spec states only a day-based one ([I], C# · Medium) | [ENCOUNTERS § 1](specs/ENCOUNTERS.md#1-the-timer--what-offers-the-quest-after-x-days) · [CHARTING § Natural discovery](specs/CHARTING.md#natural-discovery--caravans-and-outposts-rolling-finds-as-they-go) |
| Giver channel: a trader, visitor, book or scan hands the content over | Partly: a faction giver only | Yes | **G1** a random non-hostile faction · `QuestNode_GetFaction` · XML · Easy<br>**G2** a named leader as asker, with a faction-def exclusion list · `QuestNode_GetPawn` · XML · Easy<br>**G3** a numeric goodwill floor or a tech/culture filter · our node · C# · Medium<br>Vanilla's giver tag is a closed enum (`Traders`, `OrbitalScanner`, `Reading`, `Beggars`), and a quest joins a tag's list with one XML `<li>`. Handover by trader, visitor or book is not otherwise answered | [ENCOUNTERS § 2](specs/ENCOUNTERS.md#2-the-giver--drawn-at-random-neutral-or-better) · [CHARTING § Two premises this corrects](specs/CHARTING.md#two-premises-this-corrects) |
| Decree channel: obligations an institution imposes once the founders hold standing in it | Yes | Yes [I] | **A** each Church decree authors its own failure cost (mood, lost Exaltation, lost Goodwill) · vanilla quest nodes + VFED's `QuestNode_GetEmpire` or our node · XML · Easy with VFED / Medium without<br>**B** decrees stop while the Church is hostile · one patch on `DecreeSetup` · XML · Easy<br>**C** a generic cost hook · C# + Harmony · Medium · *not recommended*: there is nothing for a generic hook to reach<br>**D** Church-issued decrees on a schedule, not from a breakdown · XML (conceited titleholders only) or C# · Easy / Medium<br>Spec recommends A with B | [RELIGION § Decrees](specs/RELIGION.md#decrees--what-failing-one-costs-set-per-decree) |
| Purchase channel: a shop, paid in Influence or Intel | Yes | With work: one `RegisterSyncMethod` on `ActivateQuest` (Build A); whether `QuestInfo` serialises unaided is not settled by reading | **Build A** VEF `QuestGiverDef` + our currency pair and window (~95 lines) · C# · Medium (mapped)<br>**Build B** our own catalogue (~260 lines, ~290 in the cost table) · C# · Hard (mapped) · the fallback if #14 declines VEF<br>Spec recommends Build A | [CURRENCIES § The purchasable quest catalogue](specs/CURRENCIES.md#the-purchasable-quest-catalogue) |
| Shop entries: each is a quest or an item from an authored set, with its own eligibility and shelf life, and may leave when ineligible | Yes, with one part built | Yes (spec), condition: the fill and the accept run on synced paths (#106's `ActivateQuest` registration) | **A** one shelf; an item entry is an items-reward quest; XML eligibility and per-entry expiry · VEF + vanilla nodes · XML · Easy<br>**B** entries leave one at a time (expired or ineligible) and restock individually · C# · Medium<br>**C** a gate node that reads era, a balance or a political flag · C# · Medium · the gate is advisory under MP unless re-checked inside the synced call<br>**D** two shelves, quests and items apart · C# + XML · Medium<br>**E** reskin a vanilla trader · Hard · MP Unknown · *not recommended*: cannot sell a quest<br>Spec recommends A + B + C | [CURRENCIES § Shop entries](specs/CURRENCIES.md#shop-entries--a-quest-or-an-item-each-with-its-own-eligibility-and-shelf-life) |
| A bought quest can fail without stalling its plot line, and may return free, paid again or refunded | Yes, with one small piece built | Yes (A, B, D); with care (C) | **A** a fresh roll of the same script restocks the same shelf, free or priced, set per entry · our `QuestPart` · C# + XML · Medium<br>**B** refund in full or part · same part · Medium<br>**C** a free copy arrives later as an ordinary offer · VEF `grantAgainOnFailure` · XML · Easy · *not recommended for plot entries*<br>**D** the Schism re-offers its current step · Medium, already specified<br>**E** adopt VFE Deserters' shop · Hard · *not recommended*: its service missions never return<br>Spec recommends A, with B's refund as a per-entry mode | [CURRENCIES § A failed bought quest returns to the shop](specs/CURRENCIES.md#a-failed-bought-quest-returns-to-the-shop) |
| Under Multiplayer the quest board is shared as vanilla ships it | Yes | Yes | No build. `Quest.Accept` and reward `Choose` are registered sync methods [V]; "acceptance is synced by Multiplayer as shipped" | [CURRENCIES § The Schism catalogue](specs/CURRENCIES.md#the-schism-catalogue--a-spend-that-advances-the-plot) · [ENCOUNTERS § Verdict](specs/ENCOUNTERS.md#verdict) |

**What the story can do with it**
- Run the Chronicle as one standing quest whose beats appear beneath it in order, with a visible `3 / 9`. A beat whose site is lost comes round again and is never skipped.
- Tell every arrival why it happened, in its letter ("the Sensory Array caught…").
- Make any vanilla or mod quest Charting-only with one XML line, so labour finds it rather than a letter delivering it; or keep a told quest out of every pool. From a named era it can stop being charted and start announcing itself.
- Present every subplot as its own standing parent quest, its beats nested beneath it whichever channel they arrived by, and rate every quest before commitment.
- Gate optional side content on progress with VEF quest chains.
- Send an optional encounter from a random friendly faction, named leader and all, on a fixed day, a drawn day or from the natural pool.
- Have the Church lay decrees whose failure costs mood, Exaltation or Goodwill, and which stop the moment the Church turns hostile.
- Sell missions and techprints side by side in the Schism and Glitterite shops, each entry appearing when its conditions are met and leaving on its own clock. A failed mission can come back free, paid again or refunded.

**What it cannot do**
- Show an unbought VEF shop offer under its parent, or stop the player dismissing a parent, which dismisses all its children.
- Keep a finished beat under its parent in the list without T2 or T3 (T-210). An unrated quest looks like a one-star quest (T-208).
- A shop entry whose clock ran out still charges if bought: it takes payment, sends the letter and starts nothing, unless our guard tests the quest state first. An entry whose script builds no choice part vanishes from the shelf (T-76).
- The *same* failed quest can never return; only a fresh roll of its script can.
- A timed encounter on a one-interval storyteller window is lost for the campaign if its giver or target is missing that day (T-157). VEF's chain timer generates it broken instead (T-71).
- An offer that reads campaign state (era, a balance, a political flag) needs our gate node; vanilla XML cannot see it.
- Vanilla decrees arrive only from a titled colonist's breakdown. Church-issued decrees need route D.
- Nothing arbitrates between the two players on the shared quest board.

**Spec and tickets:** no single spec: [`specs/CHARTING.md`](specs/CHARTING.md) · [`specs/CURRENCIES.md`](specs/CURRENCIES.md) · [`specs/RELIGION.md`](specs/RELIGION.md) · [`specs/ENCOUNTERS.md`](specs/ENCOUNTERS.md) · #57 Charting engine, #40 beat carrier, #61 readouts, #146 natural discovery, #106 catalogue, #144 shop entries, #145 failed bought quest, #132 Schism catalogue, #137 decrees, #158 encounter, #136 giver, #196 presentation, #197 announcement by era
