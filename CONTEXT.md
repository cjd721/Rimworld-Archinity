# Archinity

The project's glossary. What the words mean, and nothing else.

Campaign: [overview](docs/PLOT.md), [era chapters](docs/plot/),
[systems](docs/specs/) and [cosmology](docs/COSMOLOGY.md).
Engineering: [coding standards](CODING_STANDARDS.md) and
[verified findings](docs/technical-findings.md).

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

Campaign sequence: [PLOT.md](docs/PLOT.md). Shared mechanics: [specs](docs/specs/).

**The founders**:
The two player pawns the Archons marked. Protagonists and progress bar both.
_Avoid_: the chosen ones, the mains, the player characters

**The mark**:
The founders' direct Archon inheritance and the key to core vectors. A head start,
not a cosmological requirement for transcendence. [Altar](docs/specs/ALTAR.md)

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
rite combines Life, aligned Devotion and Self. [Altar](docs/specs/ALTAR.md)

**Core vector** · **Augment vector**:
The two named-gene classes. **Core** is the path-to-divinity set and is mark-locked;
**augment** is specialisation and works on anyone.
_Avoid_: main genes, side genes

**Lottery capsule**:
An Archon capsule converted by Industrial research into something usable.
_Avoid_: archite capsule (the **inert** pre-conversion item)

**The Chronicle**:
The ordered campaign discoveries from the first Archon gift to transcendence.
[Charting](docs/specs/CHARTING.md)
_Avoid_: the questline, the main quest

**Plot line**:
A sequence of motives, pressures and developments in the world, with a beginning,
a movement and a landing. The **main plot line** is the
spine the player is expected to engage with; a **subplot** is any other. Some close inside an era, some run the whole campaign.
[#11](https://github.com/cjd721/Rimworld-Archinity/issues/11)
_Avoid_: arc (which is the whole story's shape), thread, storyline

**Beat**:
One step of the Chronicle, **derived from a plot line** — the point at which a plot
line touches the player and becomes an event they interact with. **Main beats
and sub beats**, mirroring the main plot line and its subplots.
_Avoid_: quest, mission, stage

**Era**:
One of the five technological eras: Neolithic, Medieval, Industrial, Spacer or
Ultra. The coda is the concluding campaign phase, not another research tier.
_Avoid_: tier (which means a RimWorld `techLevel`), age

**Leap**:
A named capability jump within an era. Exact Industrial and later partitions
remain subject to the campaign and progression specifications.

**The coda**:
The concluding phase around transcendence and the threshold. Returning permits
continued Ultra research and play. [Ending](docs/plot/ENDING.md)
_Avoid_: the Archotech era, the endgame

**Chapter close**:
The resolution of a political phase. The major planetary resolution occurs in
early Spacer before orbit is revealed. [Spacer](docs/plot/SPACER.md)

**Waystone**:
The Archotech detector interpreted through Charting from the Star Table to the
Sensory Array. At transcendence, it points out of the universe.

**Reverence**:
Adoption of the player's ideology among a faction's people. Persistent, slowly
decaying and sustained by institutions; not spendable. [Religion](docs/specs/RELIGION.md)

**Exaltation**:
Church service currency whose thresholds unlock title rites and institutional
privileges, independently of psychic rank.

**Influence**:
Spendable leverage earned through Schism operations and used in its anti-Church
network. Ordered mission progress is separate.

**Intel**:
Spendable Glitterite technical intelligence used by advanced research and hacking;
completed knowledge persists. [Glittertech](docs/specs/GLITTERTECH.md)

**Trace**:
How well the Glitterites can correlate, locate and hunt the colony. Visibility is
an alternative UI name still under consideration.

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
_Avoid_: the tech range, the faction filter

**The advance**:
The one synced command that raises the ceiling, writes the player faction's tier, and
stamps the era-start tick. The only writer of an era anywhere in the project.

**The trigger**:
What the player does to earn the advance — a capstone that unlocks a rite at the altar.

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

**Practice** · **Instruction** · **Analysis**:
How a node is earned, chosen by asking _how would you actually figure this out?_
**Practice** — resource cost alone, the default. **Instruction** — a techprint, a book, a
teacher. **Analysis** — a physical example you took apart.
_Avoid_: gating, hunt requirements

### Process

**The map**:
The wayfinder issue tracking the road to a locked design spec —
[#2](https://github.com/cjd721/Rimworld-Archinity/issues/2). Its children are
**tickets**, each one question.

**The freeze**:
World creation — the campaign's only true one-way door. Before it nearly every
decision is free to change; after it, some are a new world rather than a patch.
[#18](https://github.com/cjd721/Rimworld-Archinity/issues/18)
_Avoid_: launch, go-live
