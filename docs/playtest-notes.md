# Playtest notes

Evidence from actually playing the thing. One entry per session, newest last.

**Why this file exists.** The design map ([#2](https://github.com/cjd721/Rimworld-Archinity/issues/2))
rules *playing the campaign* out of scope on purpose — the map produces a spec, and
a spec that chases every session's impressions never locks. But play is the only
source of evidence that outranks argument, and it had nowhere to land. So it lands
here, and graduates by hand: a finding is written down when it happens, and moved
into the Waystone, the philosophy doc, or a ticket only once someone decides what
it means.

**Read a session as evidence, not as instruction.** Findings are about *classes* of
content and *shapes* of interaction. The mod set is an output of the map, never an
input to it, so nothing here endorses a specific mod staying in the bin.

---

## Session 1 — 2026-08-29

First real co-op session on the Multiplayer mod. Roughly a 66-mod bin, MP-vetted and
patched by hand. Neolithic start, played up to having the full set of crafting
benches. Not a balance pass — this is about whether the campaign's core loops feel
like anything.

### The finding: role kits are the mid-game engine

The content that landed hardest was the stuff the philosophy doc dismisses. Job
apparel — a set of clothes for every kind of worker — plus the utility layer of tool
belts, backpacks and boots, plus armour padding that stacks under plate and can be
made from a chosen material.

Conrad, unprompted: *"gives you a real sense of purpose and something to do while
playing the game besides just watching your pawns run around."*

That is the mid-game sag being answered by category-4 content, which
`rimworld-design-philosophy.md` §4 says cannot happen. It happened. The mechanism is
§5 of the same document: the gear **forces specialisation** — a pawn wearing the
cook's kit is a cook and cannot also be your smith — and a specialist you can finish
outfitting is a player-invented project with a defined end state, visible in the
world, at real cost, and chosen. *Deck out eight knights* and *dress the kitchen*
are the same shape.

The variable is not how many apparel defs exist. It is whether they **form a kit for
a role**. That distinction is now carried in `WAYSTONE.md` §6 and §4.4 of the
philosophy doc has been qualified.

### What the mods get wrong, and what we take from it

The content is good and the delivery is bad, in three specific ways:

1. **Nodes dump.** One project at ~2500 research hands over twelve to twenty
   unlocks at once.
2. **Nodes hand out two answers to one need.** Leather and chain arrive together,
   so leather is dead on arrival — it was never unlocked, only skipped.
3. **The grouping axis is the mod author's category**, which is not an axis the
   player ever thinks in.

The correction is not the opposite extreme. One node giving a chef's hat and an
apron for 100 research, then another, then another, was named as *annoying* before
anyone suggested it.

**Nor is the correction "one node hands you the cook."** Conrad struck an early draft
of this that implied it, and the correction is the actual design: a kit's pieces
should come from wherever they honestly come from — the hat and apron out of
tailoring, the cleaver out of smithing, the boots out of leatherwork — and be
**spread across the tree** rather than balled together.

> "I'm not literally suggesting that a single research node should just give you
> everything... My point is we should spread it out across the entire tree. We also
> shouldn't just ball it together."

The kit is what the *player* assembles. It is not a payload a node delivers. What
survives as the rule is the pair of failures, both observed live: a node must not
**dump**, and it must not hand out **two answers to one need**.

Explicitly not wanted yet: method. "We don't need a ton of notes on the method yet,
just the idea."

The player's own mental model, stated plainly: pawns split into **workers**
(specialised by skill, then by gear) and **soldiers** (melee and ranged,
positioning). Research should be legible in those terms.

### Fetch-gating: protected at the bottom, wanted at the leaps

Getting to a full set of crafting benches took a long time. The verdict was that
having to cross the map for items to unlock those benches *would have felt bad* —
a colony that cannot cook until it has fetched something is being punished for
starting.

**But the protection expires, and Conrad drew the line himself.** An early draft of
this said the critical path — benches and basic capability — is bought with work
alone, full stop. That over-committed:

> "That's true for literally basic capability. As soon as you get the Neolithic
> version of everything, then we can start gating progress again... but I do think
> big [moments], like developing electricity, should require an item for sure.
> That's just cool, you know? Learning electricity itself requires an item. I like
> that. But not every bench."

So the rule is a floor with an expiry, not a permanent exemption: nothing stands
between the colony and its **first** answer to a need, and once a Neolithic answer
to every need is owned, gating resumes. Spend it on the leaps worth remembering.
Every bench demanding a fetch item is a tollbooth; electricity demanding one is a
story.

The utility and augment gear remains a good home for hunt gating on its own merits,
and a higher resource cost is accepted as a gate there in place of a quest.

`WAYSTONE.md` §6 now carries this as **"The first answer to a need is never gated
behind a fetch"**, replacing the over-committed version.

### Menus are the binding constraint

The clearest operational complaint, and it answers open fog on the map.

- **Bill menus.** ~80 addable recipes on a tailoring bench. Unsortable, unsearchable,
  genuinely painful. The map's bench-and-augment fog asks *whether the real
  constraint is bill tabs or building count* — this session says **bill tabs**, and
  it is not close.
- **The research tab.** Same problem, same cause: too many nodes, no way to see only
  what is live for you.
- **The ask, in Conrad's words:** *"I want to see all the recipes that matter to me
  right now in the medieval era and nothing else."* A per-era filter — a checkbox set
  more than a sort — across bill menus and the research tab.

This is a hard ceiling on how much content the tree can hand out, which makes it a
design constraint and not only a QoL wish.

### Ask: ship our own kit presets

The kits are a design idea in the tree and a **usability object** in play. Conrad
wants them to exist as authored presets rather than something every player rebuilds
by hand — a Cook, a Farmer, a Smith, a melee soldier, a ranged soldier, defined by
us and selectable.

> "The sets themselves are cool, but I would want kits... we should create our own
> preset for this. It's just way easier."

Undecided, and deliberately so: whether that rides on the loadout mod or on vanilla
apparel policies. Both were named as acceptable homes.

**Open question blocking the choice:** will a vanilla apparel policy actually make a
pawn equip *utility* items — tool belts, backpacks — or does that need the loadout
mod? Conrad has not tested it and suspects the latter is why the loadout mod would
be required at all.

> "The loadout mod is neat but I don't know if I'm going to keep it yet. Apparel
> does the same thing so I don't really understand... like if I just give them an
> apparel command, will they equip utility items and things like that from the mods?"

He intends to playtest this. Nothing should assume the loadout mod stays in the bin.

### Ask: a sane default for new bills

The single most-repeated click complaint, and Conrad says he changes this on nearly
every build he plays.

Every new bill wants the same configuration and none of it is the default: **do until
you have at least one**, counting only items above ~51% durability and at decent
quality. Setting that by hand for twelve or fifteen recipes is the tax.

> "That's so annoying, the amount of times you have to click when you're trying to
> create 12 or 15 items and always want to make sure that you have one in storage
> and your colonists will go get it."

What he wants is that configuration as the thing a new bill *starts* as — a preset,
a default, or one button. He plans to try a mod route first and will fall back to
wanting it built.

Distinct from the menu-legibility problem above: that one is about **finding** a
recipe, this one is about **configuring** the bill once found. Same hostile surface,
different fix.

### Defect: modded bills with no Details tab

Some modded recipes (stews and soups were named) expose no Details tab on the bill,
so *do until you have X* and repeat-count configuration are unavailable. Unclear
whether this is vanilla behaviour for recipes without a single countable product or
an actual defect. Needs a repro. Filed separately.

### Standing priority, stated by Conrad

> "our biggest job here is going to be pacing the research tree and determining the
> exact resource cost for all of those items."

Half of that is live — the ladders are the map's frontier. The costing half is
`Balance`, which the map defers deliberately and last. Noted so it is not
re-litigated as a new priority.

---

## Session 2 — 2026-08-31

Continued Neolithic play, and then a long design conversation off the back of it.
So this entry is not pure evidence: the first half is what the game did, the second
half is where the argument landed. Where a conclusion was reached rather than
observed, it says so. Nothing here has graduated to the Waystone yet.

### The Neolithic is over-long, and the fix is a calendar

The observed complaint: pawns dry meat, sit at campfires and idle. Little to build,
little to craft, and the biggest raid in the whole era was **two people**, one-shot
by a founder's fist.

The diagnosis is not a content shortage. Vanilla's desperate early phase has roughly
fifteen to twenty days of material in it, and this era stretches that over far more.
Stretch an era past its content and the surplus is idle time.

**The resolution is that the Neolithic's length is a seasonal cycle, not a day
count.** Start in spring; the era ends when the colony comes out the far side of
winter on food it preserved itself. Call it 45–60 days. The number falls out of the
calendar rather than being chosen, and the player can read the ending off the world:
*we survived a winter.*

Conrad's fear against shortening it — that hardened leather and animal husbandry
would never pay off — **dissolves, and this is the load-bearing bit**: neither is
Neolithic-terminal. Husbandry begun in the Neolithic pays out for the next five
hundred days. The era only has to be long enough to *begin* a cycle, not to complete
one three times. So the era length and the leather question are decoupled, and the
length can be set on its own merits.

### The two Neolithic stages are subsistence → surplus

An earlier proposed split — stage one unlocks *who can work*, stage two unlocks
*where they work* — was struck by Conrad as artificial. You do not learn to hunt and
then farm the next day; the Neolithic is a progression of capability, not two
buckets.

What replaced it:

- **Stage one (~15–20 days).** You eat what you caught today. Hunting, hauling, a
  crafting spot, a campfire, a few drying racks, a wooden settlement. Too many
  mouths, no buffer, and no ability to store.
- **Stage two.** You produce more than you consume, and the problem inverts: storage,
  spoilage, preservation, pemmican, curing leather, husbandry, stone benches, stone
  walls.

That inversion is a genuine regime change rather than a content unlock — the colony
rethinks rather than redoes — and every specific thing Conrad listed sorts into one
side or the other without argument.

### Raid escalation is the era's engine, and it must have an agenda

**The single strongest finding of the session.** Neolithic raids should be an order
of magnitude larger — five, ten, twenty attackers with sticks and stones. Large raids
of *bad* pawns generate the decision the era is missing: how much do I spend
capturing, holding, converting and above all **feeding** people whose stats are poor
but whose skills I can grow? That is demand rather than capability, and it costs
nothing but numbers and spawn tables.

The kit system from session 1 is what makes it work: a pawn at skill four in a full
chef's kit is a serviceable cook, so weak captures are worth taking.

**The correction, accepted:** volume alone is a longer animation. Twenty tribals
against two demigods is a queue to be punched. The raids have to want things a
founder's fists cannot defend — **the stockpile, the animals, the fields and the
colonists**. Kidnappers, animal-killers, food raids, sappers going around the two
immortals standing in the doorway. Point the raid at the base and the founders become
a liability, because they can only be in one place.

Conrad's addition: the bin already carries the wall-breaking half — trolls,
firebombs — and fortification is a period-correct, genuinely enjoyable player
activity in an era fought with bows and swords. It is also a large stone-labour sink,
which is stage two's answer to *what are my pawns doing*.

This is also where "you should lose people, not runs" gets its first real test.

### Gate the recipe, never the resource

Nearly every early bench — the research bench was named — costs steel, in an era that
should be stone, wood and leather. Mining cannot be restricted, and **should not be**:
if you can mine, you can mine steel.

The answer Conrad arrived at himself is that there are simply no *recipes* that take
it. That is the map's **exposure is free; supply is gated** operating one layer over —
and it is true of the real world, which is where the framing came from: you could
always pick up iron, you just did not know what to do with it.

**And the unusable hoard is a feature, not a tolerated cost.** A stockpile of steel
you can look at and cannot use is a visible countdown to the next era, and the moment
Medieval smithing lands the era transition pays out on material already sitting on
the floor.

The same move gates farming. You do not remove plants from the world, you remove the
**sowing recipes** — two or three crops for the whole early era, chosen to force a
playstyle rather than to solve food. Corn-shaped: high yield, long growth, does not
store, so it creates the surplus problem instead of answering hunger. Hay feeds
animals and not you. Neither feeds you tonight, so tonight is still hunting, and the
whole of stage two's tension comes out of two recipes. *(Crops named as examples, not
as spec.)*

### Bronze: declined

Considered seriously as a late-Neolithic metal rung — a smelter, bronze, and a small
set of crafting-table and building recipes — on the grounds that bronze has a low
melting point and is period-honest.

**Refused**, and Conrad had most of the way there himself (*"it might just be
convoluting it"*). It is the Waystone's own **need with an expiry date** almost
verbatim: the furnace that smelts ingots for medieval recipes. A smelter, an
intermediate ingot and a bin of recipes that all die the moment steel arrives, leaving
permanent trade-screen clutter and permanent management cost for temporary value.

The only version that survives is bronze as a **rename** of the Medieval metal rung
rather than an extra rung before it. That buys a word, not a system, and can be
decided in five minutes whenever the Medieval ladder is worked.

### Deprecation is a design axis, not a feel-good rule

A proposed rule — *leather survives because it occupies a layer the medieval tier
does not contest* — was **struck as over-committed**. The concept survives; the
mechanism was stated as if final and is only one lever. Not all leather clothing
should survive, and it should not.

**The goal is explicitly not longevity.** "300 days" was named as crazy. The goal is
that things phase out **at the right time, with a replacement and a strategy**, rather
than becoming useless the instant their successor unlocks.

The levers, per Conrad:

1. **Layer occupancy** — the original point, demoted to one option among several.
2. **Non-combat stat bonuses.** Farming yield, crafting speed, carry capacity, walk
   speed, shooting. Any one of these can make an item worth keeping over a technical
   upgrade in the same slot, which is the case the layer argument misses.
3. **The item upgraded as itself, later.** A cloth chef's hat at +5% cooking when
   tailoring unlocks; a silk chef's hat at +10% once silk is growable in the late
   Medieval. Replacement by its own better version, deliberately delayed.
4. **Recycling.** See below — it changes the calculus for everything else.

**The target feel, and it is a good articulation of the whole progression problem:**
in vanilla, Conrad grows cotton, builds only parkas and cowboy hats and a t-shirt-and-
pants floor, and does not bother with anything else — *because he already knows* he
will blanket the map in devilstrand on the first planting day of year two. He knows
devilstrand exists, knows it grows slowly, knows it is the ceiling.

That anticipation exists **only because the future is legible in advance**. Which
promotes the menu and research-tab legibility problem ([#26](https://github.com/cjd721/Rimworld-Archinity/issues/26))
from a comfort complaint to a **precondition for the strategic layer this campaign
most wants**. An opaque tree does not merely annoy — it deletes the mode of play where
you build cheap now because you can see what is coming.

### Recycling is in, and a bench may be justified by the labour it soaks

Recycling apparel and gear back into material makes deprecation feel materially
better and never stops being useful. **Guard:** material in, material out, at a
bench — no new intermediate noun (scrap, rags, salvage), which would be the bronze
problem wearing a different hat.

**New principle, from Conrad, and it qualifies the anti-clutter rule:** *some* new
basic-crafting benches are fine, because by the end of year one or two the colony has
twenty pawns and they all need something to do. **A bench can earn its place by the
labour it absorbs, not only by the output it produces.** Recycling is the named
candidate — useful, and it never goes away.

### The job system

The session's largest new idea. A **job** is a work-priority profile + an apparel
policy + a recreation preference. Two of those three already exist in vanilla, so
this is mostly a bundle over existing systems plus one new axis. It must not fight
RimWorld's work categories — a tailor is a tailor because there is a Tailoring work
type, and that is correct.

**Recreation that trains skills, option two.** Each recreation item trains a small set
of two to four *plausible* skills, and the pawn's job decides which one they get.
Option one — one recreation item per skill — was rejected: it rebuilds the session-1
menu-clog problem as a rec room full of single-purpose furniture. Bound on option two:
a player must be able to **guess** what an item trains. Kickball trains melee or
crafting, fine. Kickball trains cooking, and nobody will ever find out.

**Passion is the gate, and it is Conrad's answer, not the one proposed to him.** A
counterweight of *training recreation must be worse recreation* was offered and
**rejected**: recreation already costs you working hours, vanilla already trains
skills this way (horseshoe pins, chess), and the philosophy doc's own line is that
vanilla here is *narrow, not absent*.

What replaced it is stronger. **A pawn can only train what they are passionate about,
and naturally prefers the recreation associated with it.** Passion is pawn-intrinsic
and unmanufacturable, so it caps specialisation without touching mood at all — and it
closes the loop with the raid escalation above: you sift twenty captured tribals for
**passions**, not just stats, which is what makes a 3-skill pawn worth feeding through
a winter.

**Passion must not be made grantable — and not only for scarcity reasons.** Conrad
floated a ritual, or passion growing through repetition. Held off, because the
Waystone states there is exactly one way to become more than you are and no second
path. If passion-granting ever ships it is an **altar function**, which is a better
version of the idea anyway: you want a specialist you were not given, someone else
pays for it. Left open for playtest.

**The guard is rate, not mood.** Conrad's numbers, offered explicitly as unvalidated:
roughly **20% of the rate the pawn would gain doing the job**, doubling to **~40% in
an immaculate room**. Room quality as the multiplier is the right knob — it turns
training speed into a *building project* with real wealth cost, it matches vanilla's
existing impressive-room logic so nobody learns a new rule, and it gives the stage-two
Neolithic something to do with all that stone.

**A second job it quietly does:** it is a natural counterweight to skill decay, which
Conrad calls a bad mechanic and wants negated rather than removed. You learned to
farm, you have been cutting stone for months, but a few books and games kept the skill
up. You did not gain a level; you did not lose one either.

**Open, and worth playtesting early:** whether recreation time is actually scarce
enough to be a price. Colonists have plenty of idle hours by mid-game. If it does not
bite, the fix is making the good training furniture **expensive and few** so pawns
queue for it — not making recreation worse.

Also restated from session 1: authored apparel policies per job, pre-made by us.

### The method finding: progression is specified as grids

Conrad's, and the shape the ladder work should take from here. Filed to the map as
[The progression grids](https://github.com/cjd721/Rimworld-Archinity/issues/30).

Three artifacts, and the first two are the real ones:

- **Wearables: slot/layer × era.** Rows are every apparel slot and layer plus
  utility; columns are the eras. A cell holds what is best-available there and what it
  costs. You then read the **deprecation curve straight off a row**: a row whose cell
  changes every era is a treadmill, a row that never changes is dead content, and what
  you want is most rows turning over two or three times across the run, **staggered so
  they do not all change at the same moment**. That staggering is the actual design
  object, and it is invisible in a list.
- **Benches: bench × era.** Cell holds live recipes. A bench whose cell empties is a
  bench that should have merged into its successor. A cell going from three recipes to
  eighteen in one step is a node dump, visible at a glance — the exact session-1
  failure, made legible.
- **Research is the transition function**, derived from the two state grids rather
  than drawn first. Design the states you want at each era, and the tree is close to
  mechanical. Draw the tree first and you design nodes and hope the state falls out
  right, which is how the current bin got the way it is.

The grids overlap heavily by construction, and that overlap is the point: it is where
*two answers to one need* and *fifteen unlocks at once* become obvious.

### To explore: books, and a real library

Raised mid-play, not tested. Wants writing as a **job** in the sense above — a pawn
with a writing passion produces books, and books are what other pawns read, which
feeds straight into recreation-that-trains-skills and skill-decay negation.

The hard constraint is **the chain stays short**. Conrad will play a three-step chain
and will not play a production line:

1. **Grow a paper crop** (papyrus-shaped). Harvest *is* paper — no retting, pulping or
   pressing step.
2. **Ink at an existing crafting table.** Something on the order of mashing berries.
3. **Writing desk**: paper + ink → pages → books.

Whether writing is work, recreation, or both is undecided. Note that several mods
already ship a version of this; nothing here assumes we build it.

### To explore: food preservation belongs in the early eras

Two observations, same theme, and the theme matters because the campaign parks the
player in the Neolithic and Medieval for a very long time — preservation is a
long-lived problem here in a way it never is in vanilla.

- **Canning is gated too late.** The canning mod in the bin requires electricity, so
  it arrives after freezers, which makes it pointless. But the flavour is loved, and
  the history is on our side: people sealed food in clay jars under a layer of fat
  thousands of years ago. **Pull canning down to a Neolithic/Medieval rung** and it
  becomes a real answer to stage two's surplus-and-spoilage problem.
- **Cellars are good, and mispriced.** Storage capacity is far too high for how cheap
  and easy they are to build. Cost or capacity wants tightening.
  - Their preservation bonus may be too weak — food still rots decently fast — but
    Conrad explicitly withheld that verdict: *"that's worth playtesting some more
    before I give that input."* Leave alone for now.

### Defect: floors

No ability to build floors, and no way to tell what unlocks them. Two problems
tangled:

1. **Possibly a real misgate.** Packed dirt and stone tile are among the most
   Neolithic-shaped things in the game and should sit at or near day one. Needs a
   check against the live bin.
2. **Second sighting of the legibility problem.** Even correctly gated, there is no
   way to find out *where*. Same disease as
   [#26](https://github.com/cjd721/Rimworld-Archinity/issues/26), and it will keep
   surfacing as "why can't I do X" until a per-era view exists.
