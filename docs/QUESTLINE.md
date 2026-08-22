# The Chronicle — beat outline

Sixteen beats over roughly 700 days. What each one gives, and what the gift
actually does.

**Status: design, not built.** Nothing here exists as a def yet.

Two caveats before anyone builds against this:

- **Research gate defNames are proposed, not verified.** `TB_<Era>Theory` and
  `Xenogermination` are confirmed; the rest are from memory and must be checked
  against the def database first. See `CLAUDE.md` — an unresolvable cross-ref is
  omitted rather than erroring, so a wrong gate silently means *no gate*.
- **Every number is a first pass.** Blood costs and facility magnitudes have
  never been played. They are meant to be argued with.

---

## How gating works

Each beat carries `requiredResearch` (a single `ResearchProjectDef`) and, from
beat 2 onward, `conditionSucceedQuests` naming the previous beat.

That means a beat fires when **both** are true: you finished the prior beat, and
you finished a specific piece of research. VEF postfixes
`ResearchManager.FinishProject`, so it triggers the instant the research
completes — pacing tracks how fast Conrad actually plays rather than a clock.

`ticksSinceSucceed` should be small (1–3 days) purely for breathing room.

---

## The reward vocabulary

Everything the chain hands out is one of four things.

**Vectors** — a sealed capsule meaning one specific gene. Deterministic. Spend
blood at the altar, get exactly that gene.

**Stackable facilities** — awarded in multiples, effects add up. These are the
filler that makes a mid-era beat feel worth doing. VQE's own `maxSimultaneous`
caps carry over.

**Milestone facilities** — one only, each changes what the altar can do.

**Lore** — no mechanical payload. Roughly a third of the beats should be these,
or the chain becomes a vending machine.

---

## The facilities

All thirteen are reskins of things VQE Ancients already ships. Effects are
expressed through `AltarFacilityExtension`.

Three of VQE's original effects are **meaningless in our design** and were
repurposed rather than dropped — noted below.

### Stackable

| Ours | Was | Max | Effect |
|---|---|---:|---|
| **Chorus Stones** | Neurostabilizer array | 10 | `outcomeBonus +0.02` each. Ten of them shift the roll +0.20. |
| **Recovery Shroud** | Cognitive recovery array | 6 | Cuts the critical-failure coma. −12h each, from a ~4 day base. |
| **Exsanguination Channel** | Rapid infusion pump | 9 | `durationFactor ×0.94` each. Nine ≈ 42% faster. |
| **Warding Coil** | Rejection buffer coil | 5 | `outcomeBonus +0.04` each — stronger than Chorus Stones, arrives later. |
| **The Attenuator** | Genomic attenuator | 4 | `chargeCostFactor ×0.92` each. **Repurposed** — its original job was reducing side-gene metabolism, and we cancel metabolism anyway. |

### Milestones

| Ours | Was | Effect |
|---|---|---|
| **The Rendering Vat** | Ancient biobattery | Doubles charge per body. **Repurposed** — the original made *electricity*, which a windmill obsoletes. This makes altar charge, which nothing else can. |
| **Galvanic Substitution Coil** | Mutagen inhibitor core | `chargeCostFactor ×0.7` while powered. Blood offset by electricity — never replaced. |
| **Reliquary Sump** | Archite recycler | Refunds the *blood* on a critical failure. **Repurposed** — the vector already always survives. |
| **The Descent Engine** | Spliceframe uplink | **Non-founders may use the altar.** The hinge of the campaign. |
| **The Prism** | Trait selection prism | Lottery draws 4 options instead of 2. |
| **The Redirector** | Aberration redirector | A critical failure still yields one tier-1 option. **Repurposed** — the original chose between negative genes, and we grant none. |
| **The Harmonizer** | Complexity harmonizer | Removes the escalating blood cost of stacking genes on one pawn. |
| **The Pathing Array** | Archite pathing array | Required for the Transcendent vector. Also a 25% chance of a second gene. |

> **Stacking cost.** The Harmonizer implies a rule that does not exist yet:
> blood cost should scale with how many archite genes the recipient already
> carries (proposed +15% per gene). Without it the Harmonizer has nothing to
> remove. Decide this before building either.

---

## Act I — Neolithic

*You are gods. People bring you their blood. You understand nothing.*

### Beat 1 — The Stone That Fell
**Gate:** `TB_NeolithicTheory`
**Reward:** the **Altar**, minified, hauled home.

No vector. No explanation. It obviously matters and it obviously wants
something. Conrad owns a machine he cannot use for as long as we dare.

### Beat 2 — The First Gift
**Gate:** any early neolithic project — the point is a short gap, not a hurdle.
**Reward:** `Archinity_Vector_PerfectVision` — **1 life.**

The dots connect. Cheap on purpose: the lesson is what the altar costs, not what
it gives.

**From here, vanilla `ArchiteCapsule` works too** — the lottery, founders only.
That is what stops capsules being dead weight for 400 days.

---

## Act II — Medieval

*A rite. Not science — priesthood. You learn by repetition what pleases it.*

### Beat 3 — The Choir
**Gate:** `TB_MedievalTheory`
**Reward:** **Chorus Stones ×3** + one tier-2 vector (**2 lives**)

### Beat 4 — The Sky-Fire *(must be one quest)*
**Gate:** mid-medieval project
**Reward:** **The Rendering Vat** + **Galvanic Substitution Coil**

Neither does anything alone. The vat makes charge, the coil makes charge go
further. Split them and the vat is inert for 200 days.

Bodies now yield double, and lightning-out-of-a-corpse makes the rite cheaper.
Nobody knows why.

### Beat 5 — The Reliquary
**Gate:** late-medieval project
**Reward:** **Recovery Shroud ×2** + **Reliquary Sump**

The first real safety net: failure stops costing you the blood.

### Beat 6 — First Contact
**Gate:** `TB_MedievalTheory` complete + beat 5
**Reward:** **lore only**, and one tier-3 vector (**3 lives**)

An Archon walks into the colony, says something, and leaves. No fight.

---

## Act III — Industrial

*You work out what you have been doing for four hundred years, and do not stop.*

### Beat 7 — Method
**Gate:** `TB_IndustrialTheory`
**Reward:** **Exsanguination Channel ×3** + tier-3 vector (**4 lives**)

### Beat 8 — The Warding
**Gate:** `Electricity` *(verify defName)*
**Reward:** **Warding Coil ×2** + tier-3 vector (**4 lives**)

### Beat 9 — **The Descent Engine**
**Gate:** `Xenogermination` — verified, and the only gate in the chain that is
non-negotiable
**Reward:** **The Descent Engine** + the `XenogermReimplanter` vector

The hardest quest in the chain. It should cost the most and hurt the most.

Two things change at once: ordinary colonists can use the altar, and the
founders can convert people again — a gene deliberately stripped at game start
so that this moment has something to give back. Your religion becomes a
programme.

### Beat 10 — What You Have Made
**Gate:** late-industrial project
**Reward:** **lore only**

Sit in it for a beat before the stars.

---

## Act IV — Spacer

*Engineering your own divinity.*

### Beat 11 — The Prism
**Gate:** `TB_SpacerTheory`
**Reward:** **The Prism** + tier-4 vector (**6 lives**)

Lottery goes from two options to four — the first time the machine offers a real
choice.

### Beat 12 — The Gate
**Gate:** `OrbitalTech` *(verify defName)*
**Reward:** `VacuumResistance_Total` vector (**6 lives**) + **lore**

The Archons explain the Glitterites: theirs, left as a gate, and the instruction
was to let nothing out that could not take the system by force.

Breathlessness arriving exactly as you reach orbit is deliberate.

### Beat 13 — Deep Water
**Gate:** mid-spacer project
**Reward:** two tier-4 vectors (**8 lives** each)

---

## Act V — Ultra

### Beat 14 — Attunement
**Gate:** `TB_UltraTheory`
**Reward:** **The Attenuator ×2** + **The Redirector** + the
`VQEA_Electromagnetized` vector (**12 lives**)

`VQEA_Electromagnetized` is the key that switches on the archoblade and
archoplate — VRE-Archon's own gate, rebound off `VRE_Transcendent` so the gear
arrives while there is still something to fight. It also grants full EMP
immunity, which is what keeps the archoplate's shield up against mechanoids.

> **Unverified.** That the gene actually prevents the shield being disarmed is
> an assumption. Test before this beat is written.

### Beat 15 — The Testing
**Gate:** late-ultra project
**Reward:** **The Harmonizer**, the **archoblade** and **archoplate**, and a
tier-5 vector (**20 lives**)

A real trial — the hardest fight in the campaign. The Harmonizer removes the
stacking penalty, so the last stretch stops punishing you for what you already
are.

---

## Act VI — Archotech

### Beat 16 — Become One Of Us
**Gate:** `TB_ArchoTheory`
**Reward:** **The Pathing Array** + the `VRE_Transcendent` vector — **50 lives**

Fifty people. You will be raiding, abducting and buying specifically to feed it,
which is the intended ending: the cost of becoming a god is paid entirely by
other people, and you pay it knowingly.

The Pathing Array is required for this vector to work at all.

Conrad performs the last step himself. **The game announces nothing.**

---

## Cost curve

| Era | Per vector | Cumulative |
|---|---:|---:|
| Neolithic | 1 | ~1 |
| Medieval | 2–3 | ~10 |
| Industrial | 4 | ~25 |
| Spacer | 6–8 | ~55 |
| Ultra | 12–20 | ~105 |
| Archotech | 50 | ~155 |

Around 155 lives across a campaign, before anything spent on the lottery. The
Vat halves the bodies needed; the Coil and Attenuator cut it further. A fully
built altar runs at roughly 45% of listed cost — call it **~70 bodies** played
well, and well over 150 played badly.

## Beat rhythm

Sixteen beats over ~700 days is one every ~44 days. Of those: seven give
facilities, eleven give vectors, three give lore only, and one — beat 9 — changes
what the machine fundamentally is.
