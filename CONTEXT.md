# Archinity

The project's glossary. What the words mean, and nothing else.

**What belongs here:** a term this project uses as a label, where a reader would
otherwise guess. One or two lines, defining what it *is*.

**What does not:** the rules for applying a term, its rationale, or the argument
that produced it. Those live where they always did —

| Doc | Owns |
|---|---|
| `CODING_STANDARDS.md` | how code and defs get written; the rules an author follows |
| `docs/technical-findings.md` | verified facts, so they are never re-litigated |
| `docs/WAYSTONE.md` | design intent and the campaign's North Star |
| GitHub issues | the decisions themselves, and the reasoning behind them |

A term here links to the doc that carries its detail. If an entry grows past two
lines it is misfiled.

---

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
We *cannot* use it. Reserved for the case where fixing the mod would mean owning
their assembly — a parallel world simulation, or background threads.
[#3](https://github.com/cjd721/Rimworld-Archinity/issues/3)
_Avoid_: blocked, banned, rejected

**Declined**:
We *can* use it and choose not to. Owes no justification. Orthogonal to barred.
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
A specific mod copied into our control. A pinned mod we have also *edited* is a
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
_Avoid_: desync (the *symptom*; divergence is the cause)

**Loudness**:
The second gate — whether a failure announces itself or happens silently.

### The campaign

Detail for all of these lives in `docs/WAYSTONE.md`; these are the labels only.

**The founders**:
The two player pawns the Archons marked. Protagonists and progress bar both.
_Avoid_: the chosen ones, the mains, the player characters

**The mark**:
What makes the founders singular. It has no power of its own; it exists so the
campaign can tell them from everyone who rises after.

**The altar**:
The one machine that turns lives into power. One machine, one philosophy.

**The Chronicle**:
The quest chain from the first Archon gift to transcendence. Currently greenfield
— no def exists.
_Avoid_: the questline, the main quest

**Beat**:
One step of the Chronicle. Always a place you travel to and take something from,
never a parcel dropped on the roof.
_Avoid_: quest, mission, stage

**Era**:
One of the six tech tiers the campaign passes through in order.
_Avoid_: tier (which means a RimWorld `techLevel`), age

**Leap**:
A named capability jump *within* an era. An era has several.

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
