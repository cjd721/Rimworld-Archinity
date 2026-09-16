# Archinity

The project's glossary. What the words mean, and nothing else.

Campaign: [overview](docs/PLOT.md), [era chapters](docs/plot/),
[systems](docs/requirements/) and [cosmology](docs/COSMOLOGY.md).
Engineering: [coding standards](CODING_STANDARDS.md), the
[trap register](docs/TRAPS.md) and the [engine reference](docs/engine/).

## Language

### The mod set

**The parts bin**:
Every third-party mod on disk, treated as raw material rather than a committed load
order. Catalogued in `docs/data/PARTS-BIN.md`; current verdicts and counts in
`docs/data/MOD-VERDICTS.md`.
_Avoid_: the load order, the mod list, ModsConfig

**The build**:
The mods that actually ship in the campaign. A strict subset of the parts bin.
_Avoid_: the final set, production

**Barred**:
We _cannot_ use it. Reserved for the case where fixing the mod would mean owning
their assembly — a parallel world simulation, or background threads.
[#3](https://github.com/cjd721/Rimworld-Archinity/issues/3)
_Avoid_: blocked, banned, rejected

**Declined**:
We _can_ use it and choose not to. Owes no justification. Orthogonal to barred.
_Avoid_: rejected, cut, dropped

**Reference**:
The disposition of every mod that is out of the build, barred or declined alike.
It stays on disk to be read and learned from; none of it reaches the build.
_Avoid_: archived, disabled, deprecated

**Pinned**:
The whole set copied out of Steam's `workshop/` into local `Mods/` and never
auto-updated, so an update lands when we choose and both machines get it at once.
_Avoid_: frozen, locked

**Vendored**:
A specific mod copied into our control. A pinned mod we have also _edited_ is a
**fork**, and forks are the only third-party content committed to this repo.
_Avoid_: bundled, embedded

### Cost of admitting a mod

Every third-party mod in the build sits at one of four tiers. Barred is not a tier —
it is the absence of one, and the tiers do not apply to our own mods at all.

**Free**:
Enable it, reference its defNames, change nothing.

**Cheap**:
Enable it plus a `PatchOperation`. `patch_check.py` holds the patch to a match
count, so it stays honest under upstream drift.

**Cheap + settings**:
Cheap, plus a managed condition: the mod's `ModSettings` are part of the sync
surface, so its settings file must be copied rather than re-entered.

**Real**:
A fork we re-merge on update, or a Harmony patch in our assembly.

### Postures toward third-party code

The five things we can do with someone else's work, in default order.
[#3](https://github.com/cjd721/Rimworld-Archinity/issues/3)

**Depend** · **Patch** · **Harmony-patch** · **Fork and recompile** · **Reimplement**

**Fork and recompile**:
Take their `Source/`, fix the line, and ship our build of their DLL.
Rules: `CODING_STANDARDS.md`.

**Reimplement**:
Write our own minimal version of a technique. Neither routine nor last resort:
it is what you do when the thing you want is a small fraction of what the mod
does.
_Avoid_: rewrite, lift

### Our own code

**The assembly**:
The single assembly holding everything we own, namespaced `Archinity.Core`. One
of ours; a recompiled third-party DLL is not counted.
Rules: `CODING_STANDARDS.md`.
_Avoid_: Archinity.Altar (the historical name, being retired)

**Divergence**:
The first of the two gates a solution must pass — whether it reads anything that
can differ between the two machines.
_Avoid_: desync (the _symptom_; divergence is the cause)

**Loudness**:
The second gate — whether a failure announces itself or happens silently.

### The campaign

Campaign sequence: [PLOT.md](docs/PLOT.md). Shared system requirements: [requirements](docs/requirements/).

**The founders**:
The two player pawns the Archons marked. Protagonists and progress bar both.
_Avoid_: the chosen ones, the mains, the player characters

**The player faith**:
The player-chosen ideology followed by the colony, with Archinity's required campaign
roles and precepts baked into it. Its theology and presentation remain the player's.
It is the faith measured by Reverence.
_Avoid_: the Church, Church ideology

**The Church**:
The Roman-Catholic-like external faction the vanilla Empire becomes wholesale. It is
an institution the founders may serve, oppose or replace; it is never shorthand for
the colony's player-chosen faith.

**The Schism**:
The faction of Church insiders who believe the founders are truly divine and break from
the Church over it. Part of the Church in the fiction until it breaks away; present, hidden
and landless from world creation until then. [Religion](docs/requirements/RELIGION.md)
_Avoid_: the Deserters, the Witnesses, the other faction

**The Church remnant**:
Whatever of the Church does not convert when the Schism's plot ends: permanently hostile, left
for the player to finish or ignore. Which faction instance carries it is open (#130's routes).
[Religion](docs/requirements/RELIGION.md)
_Avoid_: the old Church, the loyalists

**Credit**:
Who a public deed is attributed to, chosen by the player as the quest's reward when accepting
it: the Church (Exaltation), the founders (Reverence) or the Schism (Influence). One option may
mix rewards. [Religion](docs/requirements/RELIGION.md)
_Avoid_: attribution reward, faction reward, reward type

**The mark**:
The founders' direct Archon inheritance and the key to core vectors. A head start,
not a cosmological requirement for transcendence. [Altar](docs/requirements/ALTAR.md)

**The altar**:
The one machine that turns lives into power. One machine, one philosophy.

**Disciple**:
A colonist raised onto the psychic track. Psychic only — it changes nothing about a
pawn's genetics. [#10](https://github.com/cjd721/Rimworld-Archinity/issues/10)
_Avoid_: acolyte, initiate, priest (a **role**, not this)

**Cultivation**:
What meditation is reskinned into: attendance at the altar and its dead.
_Avoid_: meditation, training

**The rite**:
An altar ceremony. Willing-devotion rites advance psychic capacity; the final
rite combines Life, aligned Devotion and Self. [Altar](docs/requirements/ALTAR.md)

**Core vector** · **Augment vector**:
The two named-gene classes. **Core** is the path-to-divinity set and is mark-locked;
**augment** is specialisation and works on anyone.
_Avoid_: main genes, side genes

**Lottery capsule**:
An Archon capsule converted by Industrial research into something usable.
_Avoid_: archite capsule (the **inert** pre-conversion item)

**The Chronicle**:
The ordered campaign discoveries from the first Archon gift to transcendence — the main
plot line's chain of beats. It is the content; the **main quest** is how that content is
presented. [Charting](docs/requirements/CHARTING.md) ·
[Quests](docs/requirements/QUESTS.md)
_Avoid_: the questline

**Plot line**:
A sequence of motives, pressures and developments in the world, with a beginning,
a movement and a landing. The **main plot line** is the
spine the player is expected to engage with; a **subplot** is any other. Some close inside an era, some run the whole campaign.
[#11](https://github.com/cjd721/Rimworld-Archinity/issues/11)
_Avoid_: arc (which is the whole story's shape), thread, storyline

**Beat**:
One step of a plot line — the point at which it touches the player and becomes something
they interact with. **Main beats and sub beats**, mirroring the main plot line and its
subplots. Every beat appears in its plot line's chain, whatever type it is.
[Quests](docs/requirements/QUESTS.md)
_Types_: quest beats, event beats, mission beats, etc.

**Quest** · **Event**:
RimWorld ships **events** — everything the world does. An event that can be accepted or
declined is a **quest**. [Quests](docs/requirements/QUESTS.md)

**Parent quest**:
The standing heading that presents one plot line, with its beats beneath it. Auto-accepted
and never expiring. Membership is decided by **necessity**, never by flavour.
_Avoid_: quest chain, questline

**Channel** · **Payload** · **Theatre**:
The three independent axes any quest is described by: how it arrived, what it is, and
where it happens. [Quests](docs/requirements/QUESTS.md)

**Era**:
One of the five technological eras: Neolithic, Medieval, Industrial, Spacer or
Ultra. The coda is the concluding campaign phase, not another research tier.
_Avoid_: tier (which means a RimWorld `techLevel`), age

**Leap**:
A named capability jump within an era. Exact Industrial and later partitions
remain subject to the campaign and progression specifications.

**The coda**:
The concluding phase around transcendence and the threshold. Entering the new reality
ends the game; staying leaves the transcendent pawn and colony unchanged and permits
continued play. [Ending](docs/plot/ENDING.md)
_Avoid_: the Archotech era, the endgame

**Chapter close**:
The resolution of a political phase. The major planetary resolution occurs in
early Spacer before orbit is revealed. [Spacer](docs/plot/SPACER.md)

**Waystone**:
The Archotech detector interpreted through Charting from the Star Table to the
Sensory Array. At transcendence, it points out of the universe. Colony-level
state, never a hauled item. [Charting](docs/requirements/CHARTING.md)

**Charting**:
Discovery as labor. One activity at one apparatus doing two jobs at once —
surveying the region by ordinary means, and interpreting the Waystone's returns.
[Charting](docs/requirements/CHARTING.md)
_Avoid_: scanning, exploration

**The survey pool** · **The return pool**:
The two pools Charting's two jobs feed, and they accrue separately. **Survey** is
the repeatable optional content — ruins, resource sites, faction places — ours and
vanilla's alike. **Return** is the Archon spine and the finite set of named
campaign rewards. The split is by **role**, never by who authored it.
_Avoid_: tier 3 / tiers 1–2 (the priority ordering, not the pools)

**Search band**:
A minimum and maximum tile distance bounding where a discovery may be placed. The
era ceiling decides which bands the world offers; the apparatus decides which it
accepts. Not **the band**, which is the era gate's faction-contact range.
_Avoid_: the band, range, radius

**Reverence**:
Adoption of the player's ideology among a faction's people. Persistent, slowly
decaying and sustained by institutions; not spendable. [Religion](docs/requirements/RELIGION.md)

**Exaltation**:
Church service currency whose thresholds unlock title rites and institutional
privileges, independently of psychic rank.

**Influence**:
Spendable leverage with the Schism, taken as a reward from its operations. It buys the
missions that advance the Schism's plot, and its favors. [Religion](docs/requirements/RELIGION.md)

**Revolt**:
A reverent population rising against its hostile government. What success makes of the
faction is open. Never against the Church, whose revolt is the Schism.

**Vassal**:
A holding or a faction that owes the colony tribute. What a vassal is — a settlement taken by
conquest, a friendly faction that submits, a whole faction — is open, and the shapes may coexist.
[Religion](docs/requirements/RELIGION.md)
_Avoid_: outpost (a site the colony staffs with its own people), ally (the Schism's successor pays
the colony and is not a vassal), tithe (VFE Empire's Church-only mechanism)

**Intel**:
Accumulated Glitterite technical intelligence. The player converts or trades it for
techprints or other authored instruction items; research never spends Intel directly.
[Glittertech](docs/requirements/GLITTERTECH.md)

**Trace**:
How well the Glitterites can correlate and hunt the colony, distinct from their
progress toward finding its current location. [Pressure](docs/requirements/PRESSURE.md)

**Search progress**:
How close the Glitterites are to locating the colony at its current position.
Distinct from Trace, which determines how quickly that search advances.

### Era gating

The four jobs the era gate does, kept separate on purpose.
[#7](https://github.com/cjd721/Rimworld-Archinity/issues/7)

**The ceiling**:
The single stored scalar gating what content may _exist_ — research, trader stock, quest
rewards, gear on generated pawns, incidents. A ceiling, never a level: everything at or
below it stays available forever.
_Avoid_: the world tech level, the tech cap

**The band**:
Which factions may _contact_ you — your tier and one below, and nobody else.
**This is a configuration we must write, not a default.** Ignorance Is Bliss ships
`numTechsAhead 1` / `numTechsBehind 1` and `empireIsAlwaysEligible true`, and the repo's
settings file sets none of the three. [#22](https://github.com/cjd721/Rimworld-Archinity/issues/22)
Not a **search band**, which is Charting's placement distance.
_Avoid_: the tech range, the faction filter

**The advance**:
The one synced command that raises the ceiling, writes the player faction's tier, and
stamps the era-start tick. The only writer of an era anywhere in the project.

**The trigger**:
Completing the era's capstone research project. The project's prerequisites can encode
whatever story conditions that boundary requires; no altar rite sits between completion
and the advance.

**Capstone**:
The research project whose prerequisites are an era's named Spine nodes. Always declared
at the techLevel of the era it climbs _from_, never the one it climbs to.
_Avoid_: theory project, tech lock

**Fade**:
What happens to a faction the band has left behind. It stays alive, visible and raidable;
it stops being eligible for ordinary contact. Authored political changes can still
affect its holdings. [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8)

**Exposure** · **Supply**:
The line the gate is drawn on. **Exposure** — seeing, mining, holding and using what you
took at real risk — is free. **Supply** — a trader who restocks it, a recipe that makes
it, a research node that unlocks it — is gated.

### Research

The two axes every research node sits on.
[#5](https://github.com/cjd721/Rimworld-Archinity/issues/5)

**Spine** · **Muscle** · **Comfort**:
What a node is worth. **Spine** — you cannot go forward without it. **Muscle** — you can,
and you will be measurably weaker for it. **Comfort** — you would never miss it if you
did not know it existed.

**Practice** · **Exemplar** · **Instruction**:
How a node is earned, chosen by asking _how would you actually figure this out?_
**Practice** — a resource cost paid through research, such as cloth consumed by trial and
error. **Exemplar** — study a physical likeness to unlock the project; the exemplar
survives. **Instruction** — outside knowledge such as a techprint or a specific authored
event.
_Avoid_: gating, hunt requirements

**Glitterite analysis**:
Long, destructive investigation of a recovered one-use artifact. It produces Intel and
raises Trace; it never counts as research progress and is not the Exemplar route above.

**Android**:
An artificial person or body. Androidhood does not by itself remove belief, emotion,
personhood or access to the channel.

**Glitterite**:
A member of the Glitterite civilization, which deliberately removed the emotional and
individual faculties needed for sincere fervor and connection to the channel. Glitterites
run on anima-rich neutroamine, cannot receive psylinks and are not hackable. Other androids
need not share those limitations.

### Process

**The map**:
A wayfinder issue whose children are **tickets**, each one question. There are two,
split on 2026-09-16:
[#2](https://github.com/cjd721/Rimworld-Archinity/issues/2), the **capability map** —
requirements stated and answered at route depth, ending in the capabilities document —
and [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119), the **build map** —
beats, grids, sourcing and route selection, ending in a buildable specification.

**System**:
A coherent area of campaign behavior — religion, Charting, the altar, Glittertech.
A system contains many capabilities and gets one document in each of
`docs/requirements/`, `docs/specs/` and `docs/progression/` as it needs them.

**Feature**:
One named thing inside a system. Reverence is a feature of religion, and it
needs persistence, propagation, decay, a readout and downstream reactions —
which is why one feature can demand several capabilities.

**Capability**:
Something the game must be able to do, stated as observable behavior and
independent of what carries it. _Maintain a persistent measure of religious
adoption for each faction._ A mod is a possible provider of a capability, never
the definition of one.

**Requirement**:
The condition a capability must satisfy — its meaning, its behavior, its
constraints and what the player can see, choose or refuse. Requirements are
derived from the campaign arc and live in `docs/requirements/`. Gameplay rules
are requirements: _Reverence decays; Intel is spent; Charting prioritizes the
ordered discoveries._

**Technical specification**:
Whether a system's requirements can be satisfied, and by which **routes** — each with
what it gets us, its carrier, XML or C#, its weight and whether it survives
Multiplayer. Lives in `docs/specs/`, organized by system. A spec lists routes and never
selects one; many written before 2026-09-16 also carry a designed build, kept for the
build map.

**Route**:
One distinct way RimWorld 1.6 could satisfy a requirement — _an XML repoint of VFE
Empire's tithe defs_, _a custom `WorldComponent`_ — weighed **Easy**, **Medium** or
**Hard**. Verified to exist, not designed. Selecting one is a build-map decision.
_Avoid_: option, build (for an unselected route). Not an acquisition route in a
progression grid, and not a road.

**Capabilities document**:
`docs/CAPABILITIES.md` — one card per system summarising its spec: possible,
Multiplayer, routes, what the story can do with it, what it cannot. The capability
map's deliverable, and what a narrative session reads first.

**Progression grid**:
A domain charted as rows against era columns, each cell naming what is available
at that point, its prerequisites and its acquisition route. Lives in
`docs/progression/`.
_Avoid_: ladder, tier list

**The freeze**:
World creation — the campaign's only true one-way door. Before it nearly every
decision is free to change; after it, some are a new world rather than a patch.
[#18](https://github.com/cjd721/Rimworld-Archinity/issues/18)
_Avoid_: launch, go-live
