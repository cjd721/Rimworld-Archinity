# Vision

The part that cannot be read out of the defs. Everything mechanical is
recoverable from the code and `technical-findings.md`; this is not.

Written from Conrad's own framing across session 1. Where something was never
decided, it says so rather than guessing.

---

## The premise

**The Archons built this universe as a simulation.**

The goal of the playthrough is to become advanced enough to *transcend* it —
and by transcending, earn the right to join them in the real universe. Becoming
the most advanced possible being is the win condition. Conrad does not need the
game to announce a victory; he'll know, and he'll stop there. Reaching it is
what matters, not a victory screen.

The mechanical expression is the `VRE_Transcendent` gene. That is why it is
blacklisted out of the random archite injection pool — earning it by accident
from a routine injection would resolve the entire arc by coincidence.

It arrives as the final **vector**: a named, deterministic item spent at the
altar. Conrad executes the last step himself. The game never announces
anything, because he'll know.

## The opening

The Archons reached backwards through time and put some fraction of their DNA
into a handful of random neolithic humans.

You start with **two of them**: ageless, deathless, blood-drinking, and
permanently unstable. Their tribe worships them — for drinking blood, and for
being visibly obsessed with technology nobody around them possesses. That
obsession is the engine of the whole run. It is *why* the colony needs
followers, why it takes blood slaves, why it climbs.

Conrad's own words: they "have the potential to evolve into greater and greater
things as they get more Archon genes."

This was originally intended as pure roleplay. It became the
`Seed of Archinity` scenario because it was cheap to make real.

## The arc

Every era, slowly, in order. No skipping.

| Era | Intended length | Feel |
|---|---|---|
| Neolithic | 1–2 years | Learning the world. Research is genuinely slow. |
| Medieval | 3–4 years | The long middle. Medieval Overhaul and VFE Medieval 2 carry it. |
| Industrial | 2–4 years | Research lightens. The gravship arrives. |
| Spacer → Ultra → Archotech | — | Roaming the planet, then the stars. |

Late game the **gravship becomes the main base**. You land where you want,
strip-mine it, leave. You are allied with a faction or two and at war with
others. Space is where you live.

A RimWorld year is 60 days, so this whole arc fits under roughly 600 days.

## The altar

The centre of the campaign, and the thing everything else hangs off.

**One machine, one philosophy.** There is exactly one way to become more than
you are, and it runs on blood. No second path, no competing device. Conrad was
explicit about this after an earlier design offered two: *"I don't have two
machines and two philosophies. I don't really like that."*

**It runs on lives, not power.** A prisoner or slave is carried inside and
drawn out entirely; what is left is a corpse and a charge that never spoils.
That is why the altar works from the first hour of the Neolithic and never
becomes obsolete when electricity arrives. A windmill cannot make what it
needs.

**The price is always paid by somebody else.** The person in the vat dies. The
person receiving the gene never does. That asymmetry is the horror of the
thing and it is deliberate — it is also what makes the machine safe to gamble
with, because a bad outcome costs a lost week rather than your best colonist.

**The cost scales into atrocity.** One person early. Ten to twenty each for the
late genes. Fifty, or several hundred animals, for transcendence. By the end
you are raiding, abducting and buying people specifically to feed it.

### What the altar means in each era

The arc is that **it starts as religion and ends as industry, and the body
count goes up, not down.** Efficiency never means mercy. It means scale.

| Era | What it is to your people |
|---|---|
| Neolithic | An object that demands blood. You understand nothing. It refuses you and you never learn why. |
| Medieval | A rite. Not science — priesthood. You learn by repetition what pleases it. |
| Industrial | A machine. You discover electricity and evolution, work out what you have been doing for four hundred years, and do not stop. |
| Spacer / Ultra | An instrument. You are engineering your own divinity. |
| Archotech | A door. |

The reskinned VQE Ancients facilities carry that progression — chorus stones
and an exsanguination channel in the Medieval era, a galvanic substitution coil
and the Descent Engine in the Industrial.

### The hinge

The **Descent Engine**, gated on `Xenogermination`, is the most important beat
in the campaign. Before it, only the two founders can use the altar at all.
After it, ordinary colonists can — and `XenogermReimplanter` comes back.

That beat only exists because the gene was **taken away at the start**. For
roughly four hundred days there is no way whatsoever to share what the founders
are. Conrad's reasoning: two chosen ones who can mint copies of themselves at
will are not chosen.

### What keeps the founders singular

Not `Deathless` and not `Ageless` — every vanilla sanguophage gets both, so
they cannot be the distinction.

**It is a custom marker gene**, working names *Chosen of Archinity* / *Child of
Archinity* / *Seed of the Archons*: a plain endogene on the starting xenotype,
`biostatArc 0` so it can never appear in the lottery, with no mechanical effect
of its own. It exists to be keyed off.

> **Superseded.** This section previously named *the absence of `Deathrest`* as
> the distinction. That was rejected — an absence means nothing on a pawn that
> would never have had the gene, so it cannot serve as a key. `Deathrest` is
> still stripped from the starting xenotype and that removal is still
> load-bearing; it simply is not the marker. See `QUESTLINE.md` §3.

The intent it was reaching for is unchanged, and still governs:

> *I can make you like me. I cannot make you deathless. Only They can do that.*

Two chosen ones who can mint copies of themselves at will are not chosen.
Ordinary colonists may become special slowly; they must never reach what the
founders are.

### On randomness

Conrad will accept uncertainty about *how well* something goes. He will not
accept uncertainty about *what he is getting*, and he will not accept losing a
good pawn to a dice roll.

So: named vectors are fully deterministic. The roll never decides whether you
receive something — it decides which **tier band** four options are drawn from.
A poor roll offers four weak genes, never an empty window. Reason, in his
words: out of thirty or forty pawns you might find one worth keeping, and
sacrificing two slaves to gamble that pawn away *"just feels bad."*

## The villain — the Glitterites

**The Archons seeded a gatekeeper civilisation.** Not Archons themselves —
something they left behind, running on glitterworld technology, with one
standing instruction: let nothing out of this system that could not have taken
the system by force.

Glitterworld tech first. Archon tech after. *You have to be strong enough to
beat them to reach us.*

They exist mainly **in orbit**. Lightly on the planet — a few installations
that shouldn't be there, scars rather than territory. They deploy mechanoids
and glitterworld-geared soldiers together.

They are `permanentEnemy` on purpose. A gate you can negotiate with is not a
gate.

## The ally — Starjack Free Companies

Freedom, exploration, no rules, no unified government. A few hundred
independent crews who agree a ship belongs to the people aboard it and nobody
planetside gets a say.

Neutral but hostile-capable. Conrad wanted a spacefaring faction with actual
teeth — one you can ally with *and* go to war with — rather than a stock list.

## The Archons themselves

**Man behind the curtain.** You barely see them.

One or two encounters in an entire playthrough is plenty. Their only quest
should be, in Conrad's words, a *"become one of us"* type. They are hidden,
they never raid on their own initiative, and they have no diplomacy.

He was explicit that he doesn't strictly need them present at all — he needs
the *race*, so transcendence is reachable. They exist because the Chronicle
chain needs something to summon.

---

## Design principles

These drove more decisions than any mechanic did.

**Losing the main pawns is not fun.** Direct quote: *"Nobody wants to lose a
RimWorld playthrough because your main pawns die. At least I don't, that's not
fun for me."* This is why `Deathless` stays on the Archonians. It is
load-bearing, not flavour.

**But the world must still be dangerous.** The intended feel: *"letting the
trash pawns die to the really hard enemies while my really overpowered guys
continuously have to recruit new people."* Overpowered protagonists, genuinely
threatening world, constant churn of ordinary colonists. Played on harder
difficulties.

**Timing is the whole game.** Stated three ways:
- Don't get raided by mechanoids in the Medieval era
- Don't get raided by medievals once you're glitterworld-tier
- Don't get a quest telling you to fly a ship while you're learning the wheel

Almost every gate in this project exists to serve that one principle.

**Availability beats scarcity.** *"Better to ignore them than not have them when
we want them."* When choosing a gate, err early — an available quest can be
declined; an absent one cannot be summoned.

**Quests should feel alive.** Not *"go here for free loot."* Reward and danger
belong on the same site. He specifically liked the 15% chance that archite
injection turns a colonist into a monster — real risk is a feature.

**Power should escalate through the quest line.** He wants to be *"led along by
the archotech gods"* — specific, chosen upgrades over time, not a random loot
table. He does **not** want heavy downsides bolted onto those gains; the point
is becoming godlike.

**No race bleeding.** Archons and Starjacks must not seep into ordinary
planetside factions. A trace of diversity is fine; a world where everyone is
exotic is not.

**Don't railroad it.** The timing should line up, but the playthrough is not a
script.

**One machine, one philosophy.** When a mechanic needs extending, extend the
thing that already exists rather than adding a rival to it. This killed an
early design where VQE's injector and our altar coexisted as two routes to the
same goal.

**Reskin before you rebuild.** VQE Ancients ships twelve lab facilities, a
biobattery that dissolves people, hand-authored complex layouts and 33 of the
50 archite genes. Almost nothing needs to be invented — it needs renaming and
repointing. *"What exists is pretty cool, but it would need to change to fit
our story, not the other way around."*

**Power gains carry no hunger cost.** Stacking archite genes drives metabolism
down, which would quietly punish the exact progression the campaign is built
on. Cancelled deliberately. The cost is measured in other people and nowhere
else.

---

## Explicitly rejected

- **RimWorld Together** — the run uses the **Multiplayer** mod for co-op with
  one friend.

### Reversed — both of these were rejected here and are now in

- **Medieval Overhaul.** Previously rejected as suiting a strictly medieval run.
  Now **enabled and gutted**: we take the assets, the research volume and the
  faction content, and strip the systems that fight multi-era progression — the
  wood→plank→board chain, paper and cartography, textile spinning and linen,
  Mithril, the plant and ingredient bloat. Without it the Medieval era is nearly
  empty. The old note that *"VFE Classical covers this ground"* was simply
  wrong: **all 18 of VFE Classical's research projects are Neolithic.** It
  contributes zero Medieval research.
- **VFE Tribals.** Previously rejected for *"changing research too heavily."*
  Verified against source, that concern does not hold: gathering-research is not
  a mode, it is the `Intellectual` work tag being disabled until `VFET_Culture`
  completes. It **ends itself** — the ritual hard-hides above Neolithic and
  bench research takes over with no work from us. It delivers the exact pattern
  `Player Progression Ideology.txt` asks for, where research grants *jobs and
  gizmos* rather than only recipes. It has zero mod settings, so no multiplayer
  risk.

  **Its own tech-advancement ritual is disabled.** TechBlock is the single
  advancement lever. This also removes a real conflict: VFET's advancement
  ritual fires when no project at the current techLevel is startable, and
  TechBlock's injected prerequisites make projects not-startable, so the two
  together could advance the era prematurely.

  *"I'm not trying to spend 4 years in the tribal era, but I don't want to
  totally skip it either"* still governs. The target is roughly 20–30 days.

---

## Undecided

Carry these forward; do not resolve them unilaterally.

1. **How much of the starting xenotype to strip.** DECIDED IN PART:
   `Deathrest` and `XenogermReimplanter` are removed, and both removals are
   load-bearing (see *The altar* above). The wider question — how many of the
   remaining archite genes move into the quest chain — is still open. Conrad's
   last word: *"I'm gonna give a few more upfront"* than the split proposed to
   him, and he wants to settle it **after** the quest cadence is fixed, not
   before. Every archite gene is annotated `<!-- [ARCHITE] -->` in the def, so
   the split stays mechanical.
2. ~~**Blood-fuelled Archogen Injector.**~~ RESOLVED — it became the altar, and
   the project now ships one assembly deliberately.
3. **Faction diplomacy and ideology across the world map.** He flagged it at
   world creation and it has not been touched.
4. **Whether to buy Anomaly.** The asset inventory found no eldritch or
   reality-warping content anywhere in the load order, and Anomaly's void
   material fits "the universe is a simulation" better than anything else
   available. It is a paid DLC, so it is his call. He has declined Vanilla
   Psycasts Expanded — *"Psycasts always seemed lame to me"* — which leaves
   VRE-Archon's `VREA_Transcendent` psycaster path permanently dormant. That is
   accepted, not an oversight.

---

## Working relationship

Conrad is technical and checks the work. Several times this session he caught
real errors by asking why something seemed too convenient — the duplicated
glitterheart came out that way. **Verify against decompiled source rather than
memory, and say plainly when something turns out wrong.** He would rather have
a correction than a confident answer.

He also pushes back on invented mechanism. If a mod already does the thing,
use its door rather than building a parallel one.
