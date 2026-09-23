# Territory

## Purpose

Everything the colony holds beyond its own map: the places it builds, the places it takes,
and the peoples who swear themselves to it.

This document exists because RimWorld does not make the world matter. Settlements stand on
the map and mean nothing — their maps are generated, they hold nothing worth crossing the
world for, and breaking one changes little. Destroying a faction pays almost nothing and
allying with one pays little more, so diplomacy is a role-playing choice rather than a
strategic one. The one system that does reach outward, the outpost, is stood up once for a
small cost and then pays forever while the player forgets it exists.

The campaign wants the opposite of all three. **Territory should be worth crossing the
world for, hard to take, and never free to keep.** A settlement twelve tiles away should be
somewhere the player has scouted, judged and chosen; a faction's friendship or hatred should
change what the campaign does to the colony.

Authored by [#35](https://github.com/cjd721/Rimworld-Archinity/issues/35).

**How to read this document.** What follows is stated as **macro requirements** — *an
outpost gives the colony something for what it costs; a settlement can be taken and made to
pay; a faction can swear itself and be worth having* — with the shapes underneath recorded
as **routes to explore, not decisions**. Where a mechanism is named it is a candidate. The
capability tickets in *Open questions* answer what is possible, and the choice between
routes belongs to [the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119).
Where a route turns out not to exist, the requirement is what survives, and the campaign
pivots to another shape rather than to nothing.

## Meaning

### Three tiers, distinguished by what the colony supplies

| | What the colony supplies | What it gets back |
|---|---|---|
| **Outpost** | Materials, silver and **its own people** | Goods, in kind, for as long as it stands |
| **Holding** | A war it fights alone, then a rebuild cost | Goods set by what that place and its faction are known for |
| **Sworn faction** | Nothing material — devotion earned over the campaign | **Services**, not goods |

The tiers escalate in what they cost and differ in kind in what they return: **you pay with
labour, then with war, then with faith.**

### A vassal is subjugated, autonomous and obligated

**A vassal is a place or a people the colony has subjugated.** It is *autonomous* — the
player never operates it — and *obligated* — it owes the colony on a standing basis, in a
currency set by what kind of thing it is. Both halves are required. A place the player
operates is not a vassal, and a place that owes nothing is not one either.

There are two kinds, and the distinction is how they were acquired:

- **A holding** is a single settlement **taken** by force.
- **A sworn faction** is a whole faction that has **given** itself — by submission at high
  Reverence, or by a revolt the colony backed.

**An outpost is not a vassal.** Nothing has been subjugated: it is the colony's own site,
staffed by the colony's own people, doing what the colony built it to do. That is why the
outpost rules and the vassal rules cannot be shared.

### Ours means owed, not operated

A holding belongs to the colony in the sense that it answers to the colony and pays it.
**It is never a map the player runs.** There are no pawns there to assign, no priorities to
set, no screen to visit. The player's entire relationship with a holding is three verbs:
**take it, pay for it, and ask it for something.**

This is not a limitation being accepted — it is the requirement. A campaign that adds a
dozen small colonies to manage has spent the player's attention on administration, which is
the thing this document is most concerned to avoid.

### The Schism's successor is not a vassal

[Religion](RELIGION.md) establishes the successor faction as a **permanent ally**. It pays
the colony and follows it, but it was never subjugated and owes nothing on demand. What an
ally can pay is answered alongside sworn factions
([#120](https://github.com/cjd721/Rimworld-Archinity/issues/120)); the status is not the same.

## Required behavior

### An outpost is built, paid for in people, and worth it

- **An outpost costs materials and silver to build**, era-appropriate, and the cost is real
  rather than the near-free placement the corpus ships today.
- **An outpost consumes the pawns committed to it.** They leave the colony for good: the
  player cannot recall them, the campaign does not track them, and they stop being the
  colony's pawns. Mechanically the colony has sold them to the outpost; *Bob runs the outpost
  now* is all that remains of them. **The pawns consumed are the intended limiter on how many
  outposts exist** — a hundred committed pawns is a colony that does not exist, so no
  arbitrary cap should be needed ([#175](https://github.com/cjd721/Rimworld-Archinity/issues/175)).
- **Which kinds of pawn may be committed is the build map's**, but the build must be able to
  choose: colonists, slaves, prisoners, any of them, and to require or forbid a kind.
  [#170](https://github.com/cjd721/Rimworld-Archinity/issues/170) found vanilla can tell them
  apart.
- **Once built, an outpost runs on its own and is tracked as simply as possible.** It accrues
  toward what it was built to produce and sends that to the colony on a schedule. No staff
  are tracked, there is no staffing floor, and nothing is there to tend.
- **An outpost's return justifies the pawns it consumes.** Two colonists surrendered for a
  trickle of meat is not a system worth having; this is the clause the yields will be tuned
  against.
- **Outpost kinds differ, and each does one thing.** Scouting, logging, mining and road work
  are illustrative rather than a roster; which kinds ship is content, not requirement. A
  scouting outpost is also how the colony finds things, which [Charting](CHARTING.md)
  § *Natural discovery* already owns.
- **An outpost's upkeep reaches the player as an event, never as a management surface.**
  Something happens to the outpost, the player decides once, and it is over; a panel to
  visit and tend is ruled out. **The one required event is an attack.** The player can go and
  fight it off, or not, and an outpost left undefended is **destroyed**. No staff are
  captured and there is no rescue beat.
- **A destroyed outpost is not gone for good.** It stays on the map as a ruin a caravan can
  go and loot for what survives, and paying the build cost again rebuilds it. Routes for the
  attack are [#171](https://github.com/cjd721/Rimworld-Archinity/issues/171)'s; the
  consumed-pawn premise and the ruin are
  [#179](https://github.com/cjd721/Rimworld-Archinity/issues/179)'s.

### A holding is a settlement taken by force

- **Only a settlement can become a holding.** Not a quest site, a camp, a worksite or a
  scattered structure. A logging site the colony raids can never be made to pay it.
- **Taking one must be hard.** A holding is earned against real defenses and real defenders.
  Whether settlement maps can be authored or generated to carry that, and whether the
  difficulty can follow the owning faction's tech tier, is
  [#164](https://github.com/cjd721/Rimworld-Archinity/issues/164). A settlement the colony
  can walk into does not satisfy this requirement.
- **The assault keeps vanilla's posture.** Allies may help: calling in military aid for an
  assault is allowed. A failed assault leaves the garrison to recover as vanilla's does.
- **A rebuild cost is owed at conquest, and the holding yields nothing until it is paid.**
  The place was broken to take it, and it produces nothing until it is put back. The caravan
  standing on the tile may pay on the spot, or the colony may go home and come back; the
  debt stands either way.
- **The rebuild cost scales with the settlement's tech tier.** Taking a Neolithic settlement
  is expensive; taking an Industrial one is a campaign objective. This is the campaign's
  natural gate on how fast territory accumulates, and it replaces the arbitrary cap of three
  concurrent vassals approved on
  [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8), which had no fiction behind it.
  **A cooldown between claims survives**; the hard cap does not.
- **What a holding pays is characteristic of what was taken**, never a generic basket. A
  slaver tribe's settlement can be made to send people; an armourer's can be made to send
  arms. **The preferred shape is two layers** — what the *faction* is known for, and what
  that *particular settlement* is known for — with the tile's biome and hilliness making a
  yield *plausible* rather than computing one. Whether a settlement can carry anything of
  its own, or whether its faction's trade is the whole of it, is
  [#165](https://github.com/cjd721/Rimworld-Archinity/issues/165); the requirement is the
  characteristic payment, not the second layer. **A settlement's specialty is fixed**: it
  does not climb when its faction climbs an era.
- **The form the payment takes is open and every shape is on the table**
  ([#166](https://github.com/cjd721/Rimworld-Archinity/issues/166)): a fixed basket arriving
  on a clock; a credit the holding accrues that the player spends against that holding's own
  list; things sent unprompted on the faction's own schedule; or combinations. **Delivery to
  the colony's home map is the working preference**, and home itself moves once the gravship
  becomes it.
- **A holding does not improve on its own.** What was taken is what the colony has. A
  Medieval holding is still a Medieval holding in the Spacer era, and Industrial yields mean
  going and taking an Industrial settlement.
- **Paying to advance a holding is a route worth having.** The colony owns the place and its
  former faction will not invest in it, so paying to bring it forward is coherent and
  desirable. **It advances one era per payment, and never past the colony's current era.**
  Routes are [#167](https://github.com/cjd721/Rimworld-Archinity/issues/167)'s; if none is
  built, *go take a newer one* is an acceptable outcome rather than a failure.
- **Once taken, a holding is the colony's, and its former faction no longer matters.** What
  the holding needs from that faction — its era, its specialty — is fixed at conquest.
  Nothing that faction later does reaches the holding, including swearing itself to the
  colony: the holding stays a holding.
- **Whether a holding can be lost is the build map's call, on cost.** If
  [#172](https://github.com/cjd721/Rimworld-Archinity/issues/172)'s routes make it simple,
  it ships in one shape; if it needs background machinery, it is cut and holdings are never
  lost. The shape: an event names a faction hostile to the colony coming for the holding with
  an army, on a deadline of days. The player goes and fights on the holding's own map, with
  any allies they can call, **or the holding is lost — forfeit, never a roll**.
  [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8)'s exclusion of a
  vassal-gets-raided simulation stands.
- **When a holding ends, lost or released, everything outstanding on it is gone.** Unpaid
  rebuild debt and accrued credit are extinguished, not paid out or carried over. The
  settlement passes to a faction drawn at random from those available; what *available*
  means is the build map's.
- **The era advance does not touch a holding.** A holding stores its own era, set at
  conquest and moved only by paying to advance it. [Era](ERA.md) re-authors the world at a
  boundary but never modifies what the player owns, and a holding is owned. How the holding
  is represented (§ 3's R1 or R2 in [the spec](../specs/TERRITORY.md)) is the build map's,
  provided this holds.

### A sworn faction owes services, not goods

- **A whole faction can come to serve the colony**, by submitting when its population
  overwhelmingly follows the founders, or by revolting against its government with the
  colony's backing. [Religion](RELIGION.md) owns both doors and their eligibility.
- **It owes services, and it does not turn its settlements into paydays.** A faction of a
  dozen settlements each paying tribute would dwarf every other system in the campaign and
  make conquest pointless. What a sworn faction gives is of a different kind: troops,
  people, access, safe passage, standing — things only a people can give.
- **What it can owe, and how that reaches the player, is wide open**
  ([#168](https://github.com/cjd721/Rimworld-Archinity/issues/168)). Sends on its own
  schedule, specific things on a fixed one, categories it is known for, favours the player
  **requests** on a cooldown, a menu like a holding's but greater — all of them are routes.
- **The player must be able to ask, not only to receive.** Things that arrive unbidden on
  someone else's schedule are forgotten, and a random colonist given to a colony of twenty
  specialists is a body to sell. Whether asking is expressible, and on what gate, is part of
  [#168](https://github.com/cjd721/Rimworld-Archinity/issues/168); **that the player should
  have some purchase on what arrives is the requirement.**
- **A delivery is a service.** Asking a sworn faction to send fifty components — once, or
  every sixty days — is the service of a delivery, and is allowed. What is ruled out is its
  settlements paying tribute on their own account.
- **A sworn faction is held at Ally.** Sworn means allied; vanilla's asks and ally raids
  need it anyway.
- **The colony holds the relationship, not a founder.** Services are the colony's to call.
  #168's comms asks, gated options, service shelf and scheduled routes (OS-1, OS-3, OS-4,
  OS-6, OS-7) are faction-level already; its permit route (OS-2) hangs services on one
  pawn, and serves only as a carrier.
- **No faction but the Church grants titles.** A sworn faction's services never come as a
  title ladder on a founder; #168's OS-2a is ruled out. Titleless permits (OS-2b) remain a
  route.
- **How a sworn faction stops being one, and which of its services follow the colony into
  orbit, are the build map's.** The working intuition is that ground allies matter little
  once the colony is in orbit.
- **A faction cannot be conquered into a sworn faction.** The kind is entered only by being
  *given* — submission, or a revolt the colony backed. Taking a faction's settlements one by
  one is conquest and produces holdings; taking its last one ends the faction. This is why
  the campaign never has to reinterpret what it means for a faction to be *defeated*.
- **Subjugating a faction and carving it up are alternatives, not a combination.** A faction
  whose settlements the colony is taking by force will not come to swear itself, and a
  faction that has sworn itself is not one the colony can go on conquering. This falls out
  of the faith and goodwill rules rather than needing a rule of its own, and it is what
  makes the choice per faction a real one.
- [Religion](RELIGION.md) settles orbit for the Schism's successor, which follows the colony
  up; every other sworn faction is the build map's, above.

### Hostility must cost the colony something

- **A faction that hates the colony should act against it more, and worse, than one that
  merely dislikes it.** This is stated as intent, because without it the rebuild cost and
  the cooldown only slow territorial expansion rather than bounding it — the colony can take
  settlements indefinitely and absorb the consequences.
- **The mechanism is entirely open** ([#169](https://github.com/cjd721/Rimworld-Archinity/issues/169)).
  Goodwill as the input, a named hostility value the campaign keeps, a declared-war state,
  per-faction values that accumulate and are spent in events aimed at the colony, or actions
  other than raids — blockades, demands, sieges, refusal of trade.
- **Vanilla does not supply this.** A hostile faction is merely eligible to be drawn when a
  raid was going to happen anyway, and goodwill bottoms out at −100, so hatred past that
  point currently costs nothing. Raid *frequency* and raid *size* are different levers and
  the routes may reach only one.
- **Taking a faction's settlements damages relations with it**, and that damage is the
  beginning of this, not the whole of it.

### The economy never closes

**No combination of outposts, holdings and sworn factions makes the colony
self-sufficient.** Some resources stay genuinely scarce and must be traded for, across the
whole campaign. This is the clause that keeps trade, diplomacy and the world itself
load-bearing, and it is the one to check a generous yield table against.

## Campaign progression

Outposts are available as soon as the colony can afford the people, and the kinds available
follow the era.

Holdings follow the eras through their rebuild costs and through how hard the fight is: an
Industrial settlement is meant to be a campaign objective for a colony that has not reached
that era, not a shopping trip. Whether that is a hard gate or simply a price the colony
cannot yet meet is balance, not a requirement. The player's early holdings are meant to feel
dated later, which is what makes advancing one, or replacing it, a real decision.

Sworn factions arrive late by construction: they are gated on Reverence, which is
accumulated across the campaign, and on the revolt rules in [Religion](RELIGION.md).

Where payment arrives follows wherever home currently is. [Space](SPACE.md) is explicit that
once orbit opens the gravship **is** the colony's home rather than a second one, so delivery
has to follow that move rather than assume a fixed tile
([#127](https://github.com/cjd721/Rimworld-Archinity/issues/127)).

## Player information and agency

- **The player must be able to learn what a settlement will give before committing to take
  it.** Choosing a settlement because it has what the colony wants is the loop. Taking one
  blind, finding it worthless and abandoning it is not a game, it is a refund request.
- **Knowing is earned by going.** A settlement's presence and owner are visible as vanilla
  makes them; **what it is known for is not, until the colony finds out** — by visiting it,
  trading with it, passing a caravan nearby, or watching it from a scouting outpost. Whether
  that knowledge is its faction's alone or the settlement's own is
  [#165](https://github.com/cjd721/Rimworld-Archinity/issues/165); **that it must be earned
  is the requirement.** Nothing shows a settlement's specialty to a player who has not
  learned it, and vanilla's *Show sellable items*, which today shows any settlement's trade
  profile from anywhere on the map, is included.
- **Once learned, known for good.** A discovered settlement's information stays available
  forever and is always current; nothing lapses and no stale snapshot is kept. The point is
  immersion — a Medieval colony has no magic map — not a handicap.
- **A faction's own specialty is public**, learnable at first contact — the first envoy, the
  first comms-console call, the first trade.
- **Planning a campaign against what has been learned is a feature, not a leak.** Deciding
  which settlements to take, in what order, from what the colony has scouted, is the
  intended play.
- **The player never operates a holding, a sworn faction or an outpost.** No priorities, no
  allocation, no screen to tend.
- **What is owed, and when it is due, must be legible** — including the outstanding rebuild
  cost on a holding that has not yet started paying.

## Constraints

- **No background war simulation.** Factions do not fight each other offscreen, and no
  diplomatic world runs without the player in it
  ([#13](https://github.com/cjd721/Rimworld-Archinity/issues/13);
  [Politics](POLITICS.md): *wars exist once the player has been told about them*).
  **Per-faction values are not excluded by this** where they are spent in events aimed at
  the colony — what is excluded is a simulation the player is not part of.
- **No third currency.** Goodwill and Reverence are the levers; a new stat invented to sit
  beside them is not, and neither is royal favour with a sworn faction. Whether Reverence is
  *spent* as well as held is the build map's: both routes exist
  ([#168](https://github.com/cjd721/Rimworld-Archinity/issues/168),
  [#176](https://github.com/cjd721/Rimworld-Archinity/issues/176)).
- **Glitterites are not subjugatable.** They are orbital, hostile, outside diplomacy and
  believe nothing. [Glittertech](GLITTERTECH.md) previously said a Glitterite settlement
  could be "made a vassal"; that was a stray phrase and has been struck. Glitterite ground
  is a strongholds question, not a territorial one.
- **The player operates nothing it did not build.** Stated above as a requirement, repeated
  here as a boundary on solutions: any route whose cost is a management surface fails.
- **Nothing here may be carried in mod settings** ([T-18](../TRAPS.md)), and every player act
  on a holding, a sworn faction or an outpost is a **synced command** — never a bare gizmo
  or an unsynced dialog (T-80, T-82, T-95, T-96). Both players always agree on what is held,
  what it owes and when it is due.
- **Numbers are not this document's.** Yields, costs, cooldowns, thresholds and how many
  holdings is too many are balance, and belong to
  [the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119).
- **This is not a strategy layer.** The whole document is written against turning the world
  map into a board the player optimises. Knowing things is encouraged; operating them is not.

## Open questions

- **Taking a settlement must be hard** —
  [#164](https://github.com/cjd721/Rimworld-Archinity/issues/164): defended maps, real
  garrisons, difficulty following tech tier.
- **A settlement's specialty, and learning it before committing** —
  [#165](https://github.com/cjd721/Rimworld-Archinity/issues/165): whether a durable
  per-settlement specialty exists at all, what derives it, and what reveals it.
- **What a holding pays, and how the player takes it** —
  [#166](https://github.com/cjd721/Rimworld-Archinity/issues/166): basket, accrued credit
  and menu, unprompted sends; delivery; the rebuild gate and its tech-tier scaling.
- **Paying to advance a holding to a later era** —
  [#167](https://github.com/cjd721/Rimworld-Archinity/issues/167), which also confirms the
  era advance cannot retier or remove one.
- **How a holding ends** —
  [#172](https://github.com/cjd721/Rimworld-Archinity/issues/172): released, retaken,
  destroyed, or throwing the colony off — and whether loss can reach the player as an event
  rather than a background roll.
- **A sworn faction owes services** —
  [#168](https://github.com/cjd721/Rimworld-Archinity/issues/168): what can be owed, every
  route by which it arrives, whether the player can ask, and whether Reverence gates or is
  spent.
- **A hostile faction acts against the colony** —
  [#169](https://github.com/cjd721/Rimworld-Archinity/issues/169): every route from hatred to
  consequence.
- **What an outpost costs** —
  [#170](https://github.com/cjd721/Rimworld-Archinity/issues/170): materials, silver, and
  which pawns can be committed.
- **An outpost's upkeep as events** —
  [#171](https://github.com/cjd721/Rimworld-Archinity/issues/171).
- **An outpost that consumes its pawns and runs on its own**, and its ruin —
  [#179](https://github.com/cjd721/Rimworld-Archinity/issues/179).
- **What the colony owes when *it* is the weaker party** — [Politics](POLITICS.md) wants a
  route back from defeat through peace, tribute or subordination. That is the colony paying
  a stronger faction, which is the mirror of this document and not part of it. It has no
  owner yet.
- **Vassalage as an altar-fuel route.** A holding that sends people is one of the
  acquisition routes the sacrifice economy is counting on; how many bodies the altar demands
  and where they come from is [#10](https://github.com/cjd721/Rimworld-Archinity/issues/10)'s.
