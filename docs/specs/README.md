# Technical specifications

**What a technical specification owns:** how a system will satisfy its requirements —
state ownership, conversion hooks, persistence, synchronization, UI integration, the
existing machinery we reuse and the new code we must write.

This directory holds the technical designs, organized by coherent system — including ones
still in progress. A spec may record a **verified available mechanism** long before that
mechanism is selected; the Status section is where that distinction is kept.

It is not a place for fiction (`docs/plot/`), for gameplay rules (`docs/requirements/`),
or for what becomes available and when (`docs/progression/`).

## Organize by system, not by mod or by ticket

Several capability tickets contribute to one spec. `RELIGION.md` can absorb the findings
of the Reverence, propagation, institution and Exaltation investigations. A sufficiently
substantial subsystem earns its own document when the content warrants it — do not
manufacture a document for every hook someone investigates.

## Where a research result goes

- **The issue** retains the investigation, the evidence and the resolution.
- **The system's spec** retains the supported mechanism, its constraints, the unresolved
  questions and the resulting design.
- **`docs/engine/`** retains broadly reusable engine and mod facts worth knowing
  outside the system, filed by subject, with a link rather than a copied
  investigation. If the finding is a behaviour that fails **silently**, it goes to
  the register at **`docs/TRAPS.md`** instead and is cited by ID.

## Verified is not selected

An investigation can establish that a mechanism exists without settling the design. Say
**"verified available mechanism"**. It becomes an implementation commitment only once that
choice is made.

## Lead with the build

**The first thing a reader meets is what we are going to do.** The survey — what exists,
what does not, which donor was ruled out and why — is the *support* for that answer and sits
below it.

This is not a style preference. `RELIGION.md`'s first draft opened on a Status section whose
headline was a confirmed negative, followed by a catalogue of absences, with the actual
answer — a `WorldComponent` holding the number — buried four screens down. The document was
accurate about what it had read and could not answer the question it was written for. **A spec
that opens on what does not exist reads as a dead end.**

Worse, the buried answer was *also* partly wrong, and burying it is why nobody caught that: its
display half pointed at `WorldFactionsUIUtility`, which is the world-**creation** faction screen,
and at a `GoodwillSituationDef`, which is visible only when it moves goodwill. Both survived
review because the section a reader gives up before reaching is the section nobody checks.

A negative survey is still worth writing down; it belongs under *Available mechanisms*, where
it explains why the build looks the way it does.

**The build section owes six things** — mechanism, where state lives, how it persists, what
changes it, where the player sees it, and the cost in XML / patch / new C#. That is the same
list `docs/agents/capability-research.md` puts on the resolution, because the spec section is
where it lands. A blank among the six is either another ticket (name it by number, and check
that it exists) or a gap.

## Template

```markdown
# <System>

## Purpose and scope
Which requirements this implements, linked to their source.
What this document owns and where adjacent systems take over.

## The build
What we are going to do, stated first and in full. Four of the six:
the mechanism, where state lives, what changes it, where the player sees it.
(The fifth — how it persists — goes in the next section; the sixth is the cost table below.)
State ownership, transitions, defs, hooks and integration boundaries.
Distinguish existing behavior we reuse from new code we must write.
Close with the cost table — per piece, XML / patch / new C#, with an estimate.

## Persistence and multiplayer
Save/load behavior, shared versus colony-specific state,
synchronization, randomness and async-time interactions.
Include only the concerns that apply to this system.

## Failure and recovery
What can fail, how failure is detected, and how play recovers.
Include campaign softlocks and silent integration failures where relevant.

## Status
What is verified, what is selected, and what remains proposed.
The evidence class, and links to the capability issues that established it.

## Available mechanisms
Relevant vanilla, DLC and mod support — the survey behind the build.
What each provides, its limitations, and the evidence.
What does not exist, where that shaped the build.
Include alternatives only where they explain the selection.

## Verification
What evidence supports the mechanism.
What still needs a prototype or an in-game check.
Observable checks that demonstrate the requirements are satisfied.

## Outstanding decisions
Unanswered questions, their consequences, and owning issues.
```
