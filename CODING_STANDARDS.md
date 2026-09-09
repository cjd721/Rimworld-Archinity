# Coding Standards

**Read this before touching a def or a `.cs` file.** It is how code and defs get
written here: the bar for a change, the hard constraints, and the discipline that
catches what the game will not tell you.

Authors follow it. Reviewers check diffs against it. It stays **lean and
project-agnostic** — it states rules, and points at the files that carry instances.
A rule about *how to work* belongs here; a fact about *how RimWorld behaves* does
not.

Archinity is a suite of RimWorld 1.6 mods for one long two-player co-op playthrough
on the **Multiplayer** mod.

---

## The bar for a change

The simplest thing that achieves the goal without violating a constraint. XML is
the usual answer, not the rule. Reject unrequested scope, speculative abstraction,
and cleverness that buys nothing.

### The two gates

Run these at **design time, across candidate solutions** — the job is to eliminate
what cannot work before the work starts, not to grade a finished diff. Both must
pass.

**Divergence.** Does it read anything that can differ between the two machines?
`ModSettings`, camera or viewport state, `Find.CurrentMap`, current selection,
`Prefs`, wall-clock time, a static cache with no key.

> `Rand` is **not** on that list. `Rand` reached from an already-synced tick or job
> is deterministic by construction — VFE Medieval 2 ships `Rand.Chance` inside the
> bill-completion path today and it works. `Rand` reached from an *unsynced* path is
> on the list, and the canonical shape is viewport-gated RNG:
> `if (GenView.ShouldSpawnMotesAt(...)) { Rand.Value; }` makes two clients draw a
> different number of values from the shared stream in the same tick.
>
> The evidence under this gate — what is on the synced tick, why lockstep makes
> `Rand` safe, and Multiplayer's own list of paths that must not touch the shared
> stream — is `docs/engine/determinism.md`.

**Loudness.** When it breaks, does it say so? Harmony throws at startup on a missing
target — loud. A PatchOperation matching zero nodes is loud under `patch_check.py`
and silent in game. A facility declaring `statFactors` is silent everywhere. Between
two solutions that both work, prefer the one whose failure announces itself.

**Both pass ⇒ write it. Code is cheap** — GameComponents, stat parts, ITabs, inspect
strings, letters and synced designators all cost nothing. One fails ⇒ redesign or
push it into XML. The expensive thing was never writing the code, it was debugging a
desync in a live co-op session, and these two gates are what predict that.

**Permanence is deliberately not a gate.** Decided in
[#3](https://github.com/cjd721/Rimworld-Archinity/issues/3): once established, this
does not change, so a one-way door nobody walks through costs nothing. The one place
permanence still binds is **world creation** — see
[#18](https://github.com/cjd721/Rimworld-Archinity/issues/18) and `docs/TRAPS.md`
T-07.

> This replaces the older one-line test (*"does this need a random number or a
> client-local cache?"*), which named `Rand` as the primary danger. The parts-bin
> census of 51 settings-bearing assemblies found the reverse: client-local state was
> the dominant defect and raw `Rand` was almost never the defect on its own.

---

## Hard constraints — reject a diff that violates these

- **Desync.** Every `Rand` call must sit inside an already-synced job or tick that
  both clients execute identically. Unsynced `Rand` and per-client cached state
  desync the session. New code that needs either must justify it in the diff.
- **Save integrity.** Two people play one save across months of real time. Small
  code that fails loudly beats clever code that fails quietly. A broken save is
  worse than a missing feature.
- **One assembly of ours.** Everything we own ships in a single assembly under the
  `Archinity.Core` namespace, so our Harmony patches sit in one file and cannot
  fight each other across load order. A diff that introduces a second assembly *of
  ours* is rejected unless the issue explicitly decided to. A **recompiled
  third-party DLL does not count** — it is theirs, repaired, and the rule was never
  about DLL count in the abstract
  ([#3](https://github.com/cjd721/Rimworld-Archinity/issues/3)).
  > The assembly is currently `ArchinityAltar.dll` in `Archinity.Altar`. The rename
  > is decided and free until worldgen; which mod ships it waits on the
  > mod-structure decision.

---

## Silent failures

**Read `docs/TRAPS.md` before writing a def or a `.cs` file. Flag every occurrence
in review, and cite the ID.**

That register is the standing list of behaviours that fail with **no error message
at all** — not in the log, not on screen, not by running the game. There are
currently 32, spanning def patching, world creation, multiplayer, buildings, rituals
and worldgen layouts. Several would take a playthrough to notice and one of them
(T-07, the faction roster) cannot be repaired without a new world.

No instances live in this file. A rule that generalizes belongs here; the behaviour
that motivated it belongs in the register, with the mechanism in `docs/engine/`.

---

## Verification — a def change is not done until all five pass

```bash
python tools/check_refs.py          # cross-mod defNames resolve
python tools/audit_research.py      # no research gated on unobtainable items
python tools/check_availability.py  # planned MRR materials have 2+ sources
python tools/patch_check.py         # every PatchOperation matches what it should
python -c "from lxml import etree; import glob; [etree.parse(f) for f in glob.glob('**/*.xml', recursive=True)]"
```

All five are needed and none subsumes another — `check_refs.py` alone passes on
files that do not parse, on fields that do not exist, and on defs nothing
references. What each one actually checks, the `audit_research.py` baseline and how
to read `patch_check.py`'s merge-fidelity block are in `tools/README.md`.

**Reject any diff claiming def work is complete without evidence that all five ran
clean.**

---

## Test discipline

The general reference is the `tdd` skill — red before green, one vertical slice at a
time, test through public interfaces, refactoring belongs to review rather than the
loop. This section is only what differs in a codebase that is mostly XML.

### The red–green loop for def work

Def work has a real loop and most people skip it. **The match count is the test**,
and it is enforced rather than left to discipline.

1. **Red.** Before writing a PatchOperation, run its xpath and see what it matches
   today:

   ```bash
   python tools/xpath.py '/Defs/ResearchProjectDef[techLevel="Medieval"]'
   ```

   It prints the count and identifies each matched node — defName, whether it is
   `ABSTRACT`, and its `ParentName`. A predicate meant to hit twelve children that
   instead hits one abstract parent is obvious here and silent everywhere else.

2. **Green.** Write the number into the patch as an annotation directly above the
   operation, then write the operation:

   ```xml
   <!-- expect: 12 -->
   <Operation Class="PatchOperationReplace">
   ```

3. **Repeat.** `python tools/patch_check.py` now holds every annotated operation to
   its number, and fails the build when one drifts.

**Do not produce the annotation by running the tool and copying its number back.**
That is the tautological test: it asserts only that the tool agrees with itself and
can never disagree with the patch. The number has to be what you expected *before*
you looked — if the tool disagrees, one of you is wrong and that is the entire value
of the exercise. This anti-pattern bites hardest in a def project, where it is easy
to assert that a value equals the value you just patched in; expected values come
from an independent source — a known-good literal, a worked example, the spec.

Annotations are incremental: unannotated operations are reported, not enforced, so
add them as you touch things rather than in one sweep.

Why a wrong match is silent while a zero match is merely buried —
`docs/engine/def-loading.md`.

### The state of C# testing here

**There is no test harness for `Archinity.Altar`, and that is the current reality,
not an oversight to route around.** Do not fabricate one mid-task, and do not claim
tests were run when the verification was "it compiled."

If a change genuinely warrants automated tests, say so and propose the harness in
the issue. Adding a test project unasked is unrequested scope; silently shipping
untestable logic is worse. Raise it and let the decision get made.

### Where the seam is in this codebase

A **seam** is a public boundary you can observe behavior through without reaching
inside. Most of the assembly is welded to Verse statics and has no such boundary.
The one that does exist is **the line between pure decision logic and Verse-coupled
execution** — which gene the lottery draws, what a rite costs, what the odds resolve
to, versus spawning, jobs, and def lookups.

Keep that line clean. Push decisions into functions that take values and return
values, and leave the Verse-coupled half thin enough to read. That is worth doing
for its own sake — it is also the only thing that makes a harness cheap later, if we
decide we want one. If you do write a test, agree the seam under test before writing
it.

---

## Facts over memory

Verify against decompiled source, not memory and not the wiki. Confident assumptions
have been wrong here repeatedly: a RimWorld year is 60 days not 365,
`Mech_Centipede` does not exist, `rootMinProgressScore` ignores research entirely.
`ilspycmd` is available for decompiling.

Confirm you are reading the assembly that actually loads — several mods ship more
than one build, and most of the mod set has a second copy on disk (`docs/TRAPS.md`
T-22).

Flag any assertion in a diff or commit message that reads as recalled rather than
checked. When a verified fact is worth keeping, file it in `docs/engine/` so it is
never re-litigated.

---

## Documentation

- `CLAUDE.md` is a map, not a manual. It earns pointers and mode-switching rules,
  nothing else.
- **This file** owns the rules an author follows and a reviewer checks a diff
  against. It does not own instances.
- `docs/TRAPS.md` owns every behaviour that fails **silently**, as a numbered
  register cited by ID.
- `docs/engine/` owns verified engine and mod mechanisms, filed by subject.
- `tools/README.md` owns how the verification tools behave.
- `CONTEXT.md` owns what the project's words *mean*, and nothing else. A term's
  definition goes there; the rule for applying it stays here. If you find yourself
  explaining a rule in `CONTEXT.md`, or defining a word here, they are swapped.
- `docs/PLOT.md` summarizes the campaign and links its era chapters in `docs/plot/`.
- `docs/requirements/` states what each campaign system must do; `docs/specs/`
  states how it will do it, and is what implementation reads.
- `docs/progression/` carries the domain grids: what becomes available, and when.
- `docs/COSMOLOGY.md` explains the fictional mechanisms for writers.

A diff that files a rule in the wrong one of these is misfiled, even when the rule
is correct. The two questions that route almost everything: **does it fail
silently?** (register, not engine docs) and **is it a rule or a fact?** (here, not
`docs/engine/`).
