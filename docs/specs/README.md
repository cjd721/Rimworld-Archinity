# Technical specifications

**What a technical specification owns:** how a system will satisfy its requirements —
state ownership, conversion hooks, persistence, synchronization, UI integration, the
existing machinery we reuse and the new code we must write.

This directory holds **resolved technical designs**, organized by coherent system. It is
not a place for fiction and not a place for gameplay rules; those are `docs/plot/` and
`docs/requirements/` respectively.

## Organize by system, not by mod or by ticket

Several capability tickets contribute to one spec. `RELIGION.md` can absorb the findings
of the Reverence, propagation, institution and Exaltation investigations. A sufficiently
substantial subsystem earns its own document when the content warrants it — do not
manufacture a document for every hook someone investigates.

## Where a research result goes

- **The issue** retains the investigation, the evidence and the resolution.
- **The system's spec** retains the supported mechanism, its constraints, the unresolved
  questions and the resulting design.
- **`docs/technical-findings.md`** retains broadly reusable engine and mod facts worth
  knowing outside the system, with a link rather than a copied investigation.

## Verified is not selected

An investigation can establish that a mechanism exists without settling the design. Say
**"verified available mechanism"**. It becomes an implementation commitment only once that
choice is made, and the Status section is where that distinction is recorded.

## Template

```markdown
# <System>

## Purpose and scope
Which requirements this implements, linked to their source.
What this document owns and where adjacent systems take over.

## Status
What is verified, what is selected, and what remains proposed.
Links to the capability issues that established these answers.

## Available mechanisms
Relevant vanilla, DLC and mod support.
What each provides, its limitations, and the evidence.
Include alternatives only where they explain the selection.

## Technical approach
How the selected mechanisms satisfy the requirements.
State ownership, transitions, defs, hooks and integration boundaries.
Distinguish existing behavior from changes we must build.

## Persistence and multiplayer
Save/load behavior, shared versus colony-specific state,
synchronization, randomness and async-time interactions.
Include only the concerns that apply to this system.

## Failure and recovery
What can fail, how failure is detected, and how play recovers.
Include campaign softlocks and silent integration failures where relevant.

## Verification
What evidence supports the mechanism.
What still needs a prototype or an in-game check.
Observable checks that demonstrate the requirements are satisfied.

## Outstanding decisions
Unanswered questions, their consequences, and owning issues.
```
