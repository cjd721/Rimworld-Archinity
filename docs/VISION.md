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
| Medieval | 3–4 years | The long middle. VFE Classical and Medieval 2 carry it. |
| Industrial | 2–4 years | Research lightens. The gravship arrives. |
| Spacer → Ultra → Archotech | — | Roaming the planet, then the stars. |

Late game the **gravship becomes the main base**. You land where you want,
strip-mine it, leave. You are allied with a faction or two and at war with
others. Space is where you live.

A RimWorld year is 60 days, so this whole arc fits under roughly 600 days.

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

---

## Explicitly rejected

- **Medieval Overhaul** — suits a strictly medieval run, fights multi-era
  progression. Subscribed, deliberately off.
- **VFE Tribals** — changes research too heavily. *"I'm not trying to spend 4
  years in the tribal era, but I don't want to totally skip it either."*
  Subscribed, deliberately off. VFE Classical covers this ground instead.
- **RimWorld Together** — the run uses the **Multiplayer** mod for co-op with
  one friend.

---

## Undecided

Carry these forward; do not resolve them unilaterally.

1. **Whether to strip the starting xenotype.** All 33 genes are currently on it,
   13 of them archite. Splitting ~11 out and delivering them through the
   Chronicle chain was proposed and not decided. Conrad's position: *"being
   completely busted out of the gate is also fine"* — he leans toward keeping
   the power, but liked the idea of earning it. Every archite gene is annotated
   `<!-- [ARCHITE] -->` in the def, so the split is mechanical whenever he says.
2. **Blood-fuelled Archogen Injector.** Would be the only C# in the project.
   Optional, purely flavour, his call.
3. **Faction diplomacy and ideology across the world map.** He flagged it at
   world creation and it has not been touched.

---

## Working relationship

Conrad is technical and checks the work. Several times this session he caught
real errors by asking why something seemed too convenient — the duplicated
glitterheart came out that way. **Verify against decompiled source rather than
memory, and say plainly when something turns out wrong.** He would rather have
a correction than a confident answer.

He also pushes back on invented mechanism. If a mod already does the thing,
use its door rather than building a parallel one.
