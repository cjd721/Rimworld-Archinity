# Waystone

The design document for Archinity. What the campaign is protecting, and how it
should play.

## Standing

**This document owns design.** How the campaign plays, the altar as a machine,
the sanctioned progression, the balance targets, the doctrine for the political
board, and the standing constraints every implementation works inside. It answers
exactly one question: _how should it play._

**It does not own the rest.** Events — what happens, in what order — are
`PLOT.md`'s. The premise, what is true about this universe, and the rules
governing player-facing copy are `STORY.md`'s. How anima, the channel and the
price actually work is `COSMOLOGY.md`'s. Generic RimWorld theory — the
homeostasis inversion, the mid-game sag, demand versus capability, the evaluation
tests — is `rimworld-design-philosophy.md`'s. Read that one once and apply it
everywhere; this document never restates it.

**`PLOT.md` governs above this document.** Where the two disagree, `PLOT.md` is
right and the line here is wrong. A current decision overrides an older settled
label.

**A diff does not get to change it** (`CODING_STANDARDS.md`). It changes by
addition and by deliberate decision. If a line here turns out to be wrong, that
is a real event — say so and change it on purpose. Do not let it drift.

**Read the examples as shape, not spec.** Where something here is illustrated,
the illustration is one instance of a pattern, not the required implementation.
The rule is the sentence; the example is a gesture at it.

**It carries no live numbers.** No gene names, beat placements, research costs,
mod settings, or the current state of anything — those go stale and issues carry
them. The one number in this document is the arc-length target in §5, and it is
here because everything else is priced against it.

**Disambiguation.** _The Waystone_ in prose means the Archotech object the
Charting spine hangs on (`PLOT.md` §2.2). This file is the design document that
happens to share its name. The collision is unresolved; see `## Open`.

---

## 1. The founders on the board

They are the protagonists and they are the progress bar. How far into the story
you are can be read off their gene list.

**They begin deathless, impossibly strong, and skilled at nothing.** That is the
opening settlement of _how much power to hand over at the start_, and it works
because the two halves pull opposite ways. Everything they are good at, they
earn: the opening progression is the discovery of civilisation, not the discovery
of competence. And the strength is a problem as often as it is a solution — two
people who cannot die are noticed, and the world answers what it notices.

They lose limbs and eyes and months of usefulness, so overpowered pieces have to
be spent carefully in a world that can genuinely maim them. **How much further
than maiming the world is allowed to go is open** and this document does not
settle it; see `## Open`.

**They stay singular, permanently.** Deathlessness is not what makes them special
— every vanilla sanguophage has it. What they carry is a **mark**. It has no
power of its own. It exists so the campaign can tell them apart from everyone who
comes after. How many were ever marked is not asserted anywhere, and must not be.

They can pass on strength. They cannot pass on being chosen.

> _I can make you like me. I cannot make you one of Theirs._

Ordinary colonists rise, and they rise as far as their commitment carries them —
a disciple who has genuinely mastered a discipline is a character, not a
footnote. What separates the founders is not a **ceiling** on everyone else but a
difference in **kind**: there are gifts only the marked may receive, and no
amount of climbing reaches them. Two chosen ones who can mint copies of
themselves are not chosen — but two chosen ones surrounded by useless people are
not interesting either.

So the design does not police how far a colonist gets. It fences off what is
categorically not theirs, and lets consequence handle the rest: a colonist who
takes a god's gift is still a colonist, and the next firefight teaches that
lesson better than any rule.

**Their power arrives on two tracks**: Archon genes, which come from the chain
and are named, chosen and deterministic; and psychic ability, reflavoured away
from meditation and brain heat into something worth wanting — you are not
meditating, you are cultivating toward the energy the universe runs on; your
brain is not overheating, you are processing more than human neurons can carry.
The mechanics can be borrowed. The framing cannot.

## 2. The altar

The centre of the campaign, and the thing everything else hangs off.

**One machine, one philosophy.** There is exactly one _path_ to becoming an
Archon, and it runs on blood: the machine, the sacrifices, and the discipline
that grows out of them. Read that as one philosophy, not one mechanism — the
genes and the psychic track are both on it, because both are paid for the same
way and neither can be had anywhere else. What is refused is a **rival** device:
a second machine, a second way of buying power that does not cost a life. When a
mechanic needs extending, extend the altar.

**It runs on lives, not power.** A person goes in and is drawn out entirely.
What is left is a corpse and a charge that never spoils. That is why it works
from the first hour of the Neolithic and is never obsoleted by electricity — a
windmill cannot make what it needs.

Power arrives late, and it never replaces blood. It makes blood go further, and
that is worse rather than better: cheaper lives mean more of them. The machine
ends the campaign holding two charges at once, and only one of them is the price.

**The price is always paid by somebody else.** The person in the vat dies. The
person receiving the gene never does. That asymmetry is the horror of it, and it
is also what makes the machine safe to gamble with.

For most of what the machine does, any life will do. But the rite that grants
psychic power is particular, and always has been: it will not take a stranger.
It wants one of your own, going in willingly, because you asked.

**Efficiency never means mercy. It means scale.** Risk falls across the campaign
while cost rises far faster. By the end it can barely fail and the body count is
at its highest, and you are acquiring people specifically to feed it.

**It starts as religion and ends as industry.**

| Era            | What the altar is to your people                                                              |
| -------------- | --------------------------------------------------------------------------------------------- |
| Neolithic      | An object that demands blood. You understand nothing. It refuses you and you never learn why. |
| Medieval       | A rite. Not science — priesthood. You learn by repetition what pleases it.                    |
| Industrial     | A machine. You work out what you have been doing for four hundred years, and do not stop.     |
| Spacer / Ultra | An instrument. You are engineering your own divinity.                                         |
| Coda           | A door. Nothing goes in, and what comes out was authored from the person who walked in.       |

**It opens in stages.** Fuel and named gifts from the start. Much later, the
ability to lift ordinary colonists at all — the mid-campaign hinge, which only
lands because the ability was withheld across two whole eras first. Later still,
the truth about its own odds. Nothing that pays out before the player can use it:
a warehouse of expensive mystery objects is the failure state, not the teaser.

**Determinism where it counts.** Uncertainty about _how well_ is welcome.
Uncertainty about _what you are getting_ is not, and no dice roll may cost a good
pawn. Named rewards from the chain do not fail. Everything random is opt-in, on
its own path, priced as a gamble the player chose — including outcomes that are
genuinely bad, because a lottery with no bad band is not a lottery.

## 3. Conversion and conviction — the sanctioned progression

The price the altar charges has a giving half and a receiving half, and they get
opposite treatment. The giving half is a real system and gets the mechanical
investment. The receiving half is never a score — no meter, no rating, nothing
tracked, ever. `STORY.md` states that as a rule and `COSMOLOGY.md` explains why it
has to be one: the condition is unmistakable from the inside and impossible to
check from the outside, so anything that measured it would be measuring something
else. Build one half; refuse the other outright.

**Conversion and conviction are the sanctioned progression, not a loophole.**
Ideology, faith and a congregation that genuinely believes are the engine the
player is supposed to engineer, and optimising that engine is precisely what the
campaign wants them doing. _Design against the min-maxer_ (§7) is satisfied here
rather than violated: **the min-maxed outcome is a colony that built a real
religion, which is the intended one.**

**Build it out.** This is the deep system on the fiction side and it deserves the
mechanical investment — belief, conversion, worship throughput, and the zero-sum
arithmetic of a congregation that both sides can do from the first meeting.

**Reverence must pay.** It cannot exist only as the stat that makes the Church
angry (`PLOT.md` §4.2, §12). Goodwill asks whether a government likes you;
Reverence asks what its people will do because of what they believe you are — and
that has to cash out in things goodwill cannot buy: offerings, volunteers,
pilgrims, political favours that would be implausible on goodwill alone, levies
paid in lives, and eventually subordination. A player who chooses worship over
the institutional reward must be visibly better off for it in ways they can spend.

**It is earned by publicly interpretable acts, not by religion XP.** Saving a
settlement, beating something impossible, a public rite, a visible miracle, a war
won, a costly promise kept, and above all choosing to take the credit. Anything
that accrues quietly in the background has become a stat again.

## 4. The arc

**Six eras: Neolithic, Medieval, Industrial, Spacer, Ultra, and a Coda.** Every
one in order, no skipping. Archotech is not an era — it is a class of object that
is never researched or manufactured, only found or captured (`PLOT.md` §12).

**`PLOT.md` §1 and §9 own the arc.** What each era is, what the world does back,
which beats land where, and what the founders get — all of it lives there, in far
more detail than this document should carry. Do not maintain a second copy.

What belongs here is what the arc has to leave behind.

**The run leaves residue.** The throne room you built as a medieval king is still
yours in orbit — because you chose to keep it, not because the game denied you
something better.

**A domain running out of room to grow is not a gap that needs filling.** Some
things simply reach their ceiling early: food is largely finished by the end of
the Medieval era, and that is correct, since a good meal has not changed much
since. Do not invent a Spacer-tier answer to a need that was already answered.

**There are two endings and the game grades neither.** At the top of the Church
route the institution can offer a terminal terrestrial apotheosis — safety,
wealth, legitimacy, a completed victory. Accepting ends the run (`PLOT.md` §6).
Cosmologically it is a failure, and the game must never say so: no bad-ending
framing, no scolding letter, no penalty screen. The player chose to stop. That
ending only works if the Church route was materially tempting the whole way up,
which is why that is an invariant and not a preference.

The final threshold is the other ending. **The questline ends and says so** —
reaching it should be announced and celebrated, because you know you made it. How
that scene is presented is unauthored and is not a diff's decision to make; see
`## Open`.

## 5. Campaign length — two clocks, and only one of them is real

**Narratively, nothing pushes.** No clock, no countdown, no rival racing you, and
no consequence for taking your time. Parking an era indefinitely is a legitimate
campaign: a player who stops in the Medieval for a thousand hours, builds the
largest colony anyone has ever seen and moves on when they are finally bored has
played this correctly. `PLOT.md` §12 states it as an invariant — no forced
calendar race.

**Mechanically, there is a target.** Price research, quests and beats against a
**10–12 year average arc**, knowing the player can stall whenever they want. It
is what stops the Medieval being costed as though it were the whole game, and it
is the only reason to have a number at all.

> _That was a target for internal game balancing. Narratively, nothing pushes.
> Different goals._

**The distinction is load-bearing and easy to lose.** A balance target that leaks
into the fiction becomes a deadline, and a deadline the player can feel is the one
thing this campaign refuses. The target lives in spreadsheets and in this section.
Any beat, letter, quest or system that lets the player see it has converted it
into a countdown and must be rewritten.

## 6. The world

**The Glitterites — the standing late-campaign enemy.** Permanently hostile on
purpose, and the reason is appetite rather than orders: they consume living
biological material at industrial scale, which makes every other civilisation
livestock and diplomacy beside the point. Mostly in orbit; planetside only as
scars, uncommon but absolute where they appear. They are also the only source of post-vanilla technology, which
makes them a research dependency as well as a threat — see the conquest-linked
invariant in §9. What they actually are, and why they hoard what they hoard, is
`PLOT.md` §8 and `COSMOLOGY.md`.

**The Starjack Free Companies — the ally.** Independent crews who hold that a
ship belongs to the people aboard it and nobody planetside gets a say. A
spacefaring faction with real teeth, which you can ally with _and_ go to war with.

**The Archons — man behind the curtain.** Hidden, no diplomacy, they never raid,
and the only thing they ever ask is _become one of us_. **The encounter budget is
three, and only two are witnessed**: the marking, which is never seen in play; the
opening contact; and the door. Spending a fourth is spending the scarcest thing in
the campaign.

**No race bleeding.** Archons and Starjacks must not seep into ordinary
planetside factions. A trace of the exotic is flavour; a world where everyone is
exotic is noise.

**The rest of the world is a political board, not a vending machine.** The general
case — factions wanting things from each other, demands with deadlines, territory,
distinct doctrine, notification budget, a floor beneath total hostility — is
`rimworld-design-philosophy.md` §7 and is not restated here. What is specific to
this campaign:

- **Relationships form through encounter.** You learn what a faction is by meeting
  it, not by reading a menu.
- **Standing moves on its own**, in response to what you do and what you decline
  to do, and the movement is visible before it becomes a crisis.
- **Taking things by force is a first-class verb.** Strongholds are real places
  with real maps — and by Ultra, conquest is the only route advanced technology
  has.
- **Reverence is a second axis on the same board** (§3), and a faction's people
  and its government are allowed to disagree.

**You deal with factions at your own era**, plus stragglers below it. The
advanced ones do not care about you yet. This means allies age out and become
fond irrelevances, which is honest and guarantees a new cast every tier.

**The world is hard because the story says so.** Two gods in a garden bring the
snake. Word gets around; raiders come, get destroyed, go home and tell everyone.
The intended feel is ordinary colonists dying to things the founders walk
through, and a constant churn of recruitment around two immortals. Aimed at the
top end of manageable — you should lose people, not runs.

**Threat tracks era and capability, never wealth.** Wealth scaling punishes
exactly the building this campaign is about, and it is trivially gamed. Quality
scales as readily as quantity; a small number of much better-equipped enemies is
a legitimate escalation.

---

## 7. What we are actually protecting

Everything above is the _what_. This is the _why_ — the small set of things that
make this campaign feel like itself, distinct from general RimWorld design.

**Narrative first; systems fall out of it.** The deepest rule in the project. If
a system cannot be justified by what is happening in the story, it does not go
in — and if the story needs something, the mechanism is negotiable.

**The need is permanent; the answer is not.** A colony acquires a fixed set of
needs — butcher, cook, craft, clothe, arm, grow fibre, treat a wound — and never
loses one of them. What changes across the campaign is _what answers the need_:
cloth until devilstrand answers it better, a butcher spot until a butcher table
does. Replacing an answer with a better one is not loss, it is the whole pleasure
of teching up, and the design should be enthusiastic about it.

What we refuse is a **need with an expiry date** — a resource, bench or
processing step invented to serve one era and then gone. Cotton is fine: fibre is
forever and cotton is the first rung of a ladder that keeps going. A furnace that
smelts ingots for medieval recipes is not, because "ingots" was never a need, only
a chore attached to one — permanent management cost for temporary value, and
clutter in every trade screen for the rest of the run. The test is not _will I
still use this later_, which almost nothing survives. It is _does this serve a
need that outlives the era_.

Where an upgrade happens to collapse four benches into one, that is a pleasure
worth chasing. It is not a bar every addition has to clear.

**Kits are assembled, not granted.** The colony's work is done by specialists,
and what makes a specialist is a _set_ — the cook's hat, apron and cleaver. The
set is what the player is working toward. That does not mean any one node hands
one over: the pieces come from wherever they would honestly come from, the hat
and apron out of tailoring, the cleaver out of smithing, the boots out of
leatherwork. A kit finished across three branches is a project. A kit dropped by
a single node is a delivery.

What a node must not do is **dump** — fifteen unlocks at once — or hand out two
answers to the same need, which is the same as handing out one. Leather and
chainmail together means leather was never unlocked, only skipped.

So: spread the pieces across the tree and let the player pull them together. That
is what turns a pile of apparel into something worth wanting, and gear that
forces specialisation is what makes the colony a cast of people rather than a
pool of interchangeable labour.

**Earned beats granted.** Anything that meaningfully changes how you play should
have a story of how you got it — you went somewhere, you took it, someone taught
you, you studied a captured example. Research alone is not a story. The same rule
governs how the player learns a place exists: locations are found because somebody
did the work of finding them, never because the storyteller decided the colony
somehow knows. This is not a tax on the critical path; it is what makes the
memorable acquisitions memorable, and it doubles as something to do in the hours
the player would otherwise idle.

**The first answer to a need is never gated behind a fetch.** A colony that
cannot cook until it has crossed the map for something is being punished for
starting, and that protection holds until it owns a Neolithic answer to every
need it has. Then it expires. Once you can already cook, gating a _better_ stove
is fair game, and the same goes for every rung above it.

Spend that gating on the leaps worth remembering rather than spreading it thin.
Electricity should cost an expedition — learning what electricity _is_ from
something you had to go and take is exactly the kind of story this section is
asking for. Every bench in the game demanding one is a tollbooth with extra
steps.

**Keep the surface, cut the procedure.** Take the research, the building, the
roleplay, the unlock. Throw away the chain of intermediate steps wrapped around
it. Complexity may grow in the _kinds_ of system the player runs; it must not
grow in the number of exact items they track. Anything that has you converting a
resource so you can convert it again is suspect on sight, and doubly so if you
will still be doing it in orbit.

**The world makes you feel the gap.** The player should not have to be _told_
that the next tier is better — they should discover they are insufficient, in a
fight, and go and fix it. Progress that only shows up on a stat block gets
researched and never built.

**Never idle, never busywork.** Two ditches. Too little to do leaves the player
staring at a screen; minutiae invented to fill the time is worse than nothing.
The demand the world places on the player and the capability it grants them
should stay proportionate, era by era.

**Design against the min-maxer.** Conrad will optimise whatever is left
optimisable, including straight into a worse experience — he has said so. Do not
build systems that depend on his restraint to stay fun. Where optimisation is
_wanted_, say so explicitly and make the optimised outcome the intended one, as
§3 does.

**The next mission is the hook.** The founders' power arc is what holds the whole
campaign together. If the player ever stops thinking about the next beat, the
campaign has failed at that moment. Beats are places you travel to and take
something from — never a parcel dropped on your roof.

---

## 8. Standing constraints

**The co-op frame has two halves and they are not in conflict.**

_Narratively, this is a single-player campaign._ It is designed, built and
playtested as single-player and migrated to Multiplayer afterward by patch. There
are no narrative changes for co-op; nothing in the fiction is written for two
players, and nothing downstream of the fiction should be either.

_Engineering knows better._ Two players, co-op, months of real time. The recurring
failure mode is not a crash, it is a desync, and the one after that is a broken
save — which is worse than any missing feature. Prefer what cannot desync; when
code is genuinely the simplest answer, write small code that fails loudly. The
fiction is allowed to forget there are two players. The code never is.

**One assembly, `Archinity.Core`, deliberately.**

**Reskin before you rebuild.** Most of what this campaign needs already exists
somewhere in the load order and needs renaming and repointing, not inventing. And
what the mods intended is not binding — their content is raw material, and what
research exists, what it bundles and what it costs are entirely ours.

**Availability beats scarcity.** When choosing where to gate something, err
early. An available quest can be declined; an absent one cannot be summoned.

**Timing is the whole game.** Do not get raided by mechanoids in the Medieval
era. Do not get raided by medievals once you are glitterworld-tier. Almost every
gate in this project exists to serve that one sentence — and none of it should
railroad the run.

---

## 9. Invariants carried from `PLOT.md` §12

These are `PLOT.md`'s, not this document's. They are repeated here because they
are design rules, and an agent working from this document alone still has to obey
them. Where the wording differs, `PLOT.md` wins.

- **No forced calendar race.** Pressure may key off era, research, rank,
  capability and player action. Parking an era stays valid. See §5.
- **Every major discovery has a believable information source.** Places do not
  appear because the storyteller decided the player knows about them. See §7,
  _earned beats granted_.
- **The player never hoards high-value objects they cannot yet use.** Mystery is a
  singular teaser, never repeatable inventory clutter. See §2, _it opens in
  stages_.
- **Reverence must pay.** It cannot exist only as the stat that makes the Church
  angry. See §3.
- **The Church route must be materially tempting.** Accepting subordination has to
  be a reasonable strategic choice — the comfortable option, never the stupid one.
  The terminal Church ending in §4 depends entirely on this.
- **The schism is not the morally correct questline.** It is one path, created by
  people who genuinely believe in the founders and reject the institution that
  turned on them. Do not reward it as virtue.
- **Archotech is never researched or manufactured.** It is found, captured,
  inherited or used. Any tech tree that produces it is wrong.
- **Ultra research beyond vanilla is conquest-linked.** A captured exemplar comes
  before the research that explains it: a better rifle requires a captured rifle.

The rest of §12 — where the first psylink belongs, the Waystone's role, Life plus
Devotion plus Self, the self-authored title, the altar authoring the final gene,
religion outliving technology, Archon intent staying behind the curtain, and the
campaign never authoring what the founders believe — is plot and register, and
lives in `PLOT.md`, `STORY.md` and `COSMOLOGY.md`.

---

## Open

Not a to-do list. Places where two good principles pull against each other and the
design has deliberately not collapsed them, plus the questions genuinely awaiting
a decision. Anyone proposing a resolution should know they are resolving
something, not discovering it.

**How lethal the founders are. Awaiting a ruling; assert neither reading.** One
reading: they are hard to kill, not hard to hurt — losing your main pawns to one
bad afternoon is not fun and the design refuses it outright. The other: a founder
can be killed permanently in the first week by a raid that happened to land right,
and that danger is what keeps two demigods honest. `PLOT.md` §3.1 says only
_extraordinarily resilient and deathless_, which settles neither. This is the most
consequential open question in the project: if a founder can die permanently in
week one, the campaign can end in week one.

**The name collision on _Waystone_.** `PLOT.md` names the Archotech detector the
Waystone; this document is also called Waystone. A rename is expected and has not
been decided. Until it is, disambiguate in prose and change no filenames.

**How the final threshold is presented.** What the player must have become before
that scene is fixed. The scene itself is unauthored, and authoring it is a
deliberate decision, not something a diff arrives at.

**How far to lean on our own code.** Every custom system is a desync surface;
every avoided system is a piece of the vision not delivered.

**Whether allies can climb with you.** Falling away is honest and refreshes the
cast. Climbing honours the relationship you built.

**How early real fortification arrives.** Period-correct and satisfying, and also
the thing that ends the game's difficulty — acceptable only alongside enemies who
can answer it.
