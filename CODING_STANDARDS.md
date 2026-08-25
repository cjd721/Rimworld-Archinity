# Coding Standards

**Read this before touching a def or a `.cs` file.** It is the whole
implementation brief: the hard constraints, the failures that produce no error
message, the verification commands, and how test discipline applies in a codebase
that is mostly XML.

Authors follow it. Reviewers check diffs against it. `CLAUDE.md` points here and
does not repeat it.

Archinity is a suite of RimWorld 1.6 mods for one long two-player co-op
playthrough on the **Multiplayer** mod.

---

## The bar for a change

The simplest thing that achieves the goal without violating a constraint. XML is
the usual answer, not the rule. Reject unrequested scope, speculative
abstraction, and cleverness that buys nothing.

### The two gates

Run these at **design time, across candidate solutions** — the job is to
eliminate what cannot work before the work starts, not to grade a finished diff.
Both must pass.

**Divergence.** Does it read anything that can differ between the two machines?
`ModSettings`, camera or viewport state, `Find.CurrentMap`, current selection,
`Prefs`, wall-clock time, a static cache with no key.

> `Rand` is **not** on that list. `Rand` reached from an already-synced tick or
> job is deterministic by construction — VFE Medieval 2 ships `Rand.Chance`
> inside the bill-completion path today and it works. `Rand` reached from an
> *unsynced* path is on the list, and the canonical shape is viewport-gated RNG:
> `if (GenView.ShouldSpawnMotesAt(...)) { Rand.Value; }` makes two clients draw a
> different number of values from the shared stream in the same tick.

**Loudness.** When it breaks, does it say so? Harmony throws at startup on a
missing target — loud. A PatchOperation matching zero nodes is loud under
`patch_check.py` and silent in game. A facility declaring `statFactors` is silent
everywhere. Between two solutions that both work, prefer the one whose failure
announces itself.

**Both pass ⇒ write it. Code is cheap** — GameComponents, stat parts, ITabs,
inspect strings, letters and synced designators all cost nothing. One fails ⇒
redesign or push it into XML. The expensive thing was never writing the code, it
was debugging a desync in a live co-op session, and these two gates are what
predict that.

**Permanence is deliberately not a gate.** Decided in
[#3](https://github.com/cjd721/Rimworld-Archinity/issues/3): once established,
this does not change, so a one-way door nobody walks through costs nothing. The
one place permanence still binds is **world creation** — see
[#18](https://github.com/cjd721/Rimworld-Archinity/issues/18).

> This replaces the older one-line test (*"does this need a random number or a
> client-local cache?"*), which named `Rand` as the primary danger. The parts-bin
> census of 51 settings-bearing assemblies found the reverse: client-local state
> was the dominant defect and raw `Rand` was almost never the defect on its own.

---

## Hard constraints — reject a diff that violates these

- **Desync.** Every `Rand` call must sit inside an already-synced job or tick that
  both clients execute identically. Unsynced `Rand` and per-client cached state
  desync the session. New code that needs either must justify it in the diff.
- **Save integrity.** Two people play one save across months of real time. Small
  code that fails loudly beats clever code that fails quietly. A broken save is
  worse than a missing feature.
- **One assembly of ours.** Everything we own ships in a single assembly under
  the `Archinity.Core` namespace, so our Harmony patches sit in one file and
  cannot fight each other across load order. A diff that introduces a second
  assembly *of ours* is rejected unless the issue explicitly decided to. A
  **recompiled third-party DLL does not count** — it is theirs, repaired, and the
  rule was never about DLL count in the abstract
  ([#3](https://github.com/cjd721/Rimworld-Archinity/issues/3)).
  > The assembly is currently `ArchinityAltar.dll` in `Archinity.Altar`. The
  > rename is decided and free until worldgen; which mod ships it waits on the
  > mod-structure decision.

---

## Silent failures — these do not error, they just do not work

Flag every occurrence. None of these produce an error message, so none of them
are caught by running the game.

- **Never put `--` inside an XML comment.** RimWorld drops the entire file with no
  error naming the cause. Use `=` for divider rules. This has bitten twice, once
  by an agent that had just written the warning into a doc.
- **PatchOperations run on raw XML, before `ParentName` inheritance resolves.** A
  predicate on a field declared only on an Abstract parent matches the parent, not
  its children. Match on `@ParentName` instead.
- **Unresolvable cross-references are omitted, not set to null.** Deleting a
  `ResearchProjectDef` therefore _strips the prerequisite_ off everything that
  required it, leaving those things buildable with no research at all — the
  opposite of the intent. Order is: neuter referencing defs first, delete the
  research last.
- **Patch xpaths apply to the whole merged def database**, not to one mod's files.
  `PatchOperationFindMod` only checks that a mod is active; it does not scope the
  xpath. Confirm a predicate matches the node count you expect —
  `python tools/xpath.py '<xpath>'` prints it.
- **Mod settings are part of the sync surface.** Both players need identical mods,
  identical load order (`config/ModsConfig.xml`) _and_ identical mod settings
  (`config/ModSettings/`). The third is the one people miss — TechBlock, Ignorance
  Is Bliss and Medieval Overhaul are all settings-driven, and a mismatch means
  divergent defs and an immediate desync. A diff that changes settings must
  re-snapshot them.

---

## Verification — a def change is not done until all five pass

```bash
python tools/check_refs.py          # cross-mod defNames resolve
python tools/audit_research.py      # no research gated on unobtainable items
python tools/check_availability.py  # planned MRR materials have 2+ sources
python tools/patch_check.py         # every PatchOperation matches what it should
python -c "from lxml import etree; import glob; [etree.parse(f) for f in glob.glob('**/*.xml', recursive=True)]"
```

All five are needed and none subsumes another. `check_refs.py` validates defNames
only — it passes on files that do not parse, on fields that do not exist, and on
defs nothing references.

`audit_research.py` reads the merged, patched database, so its tier totals now
reflect any retier we have shipped. It carries a **baseline** in
`tools/audit_research_baseline.txt`: 34 deadlock risks that live in third-party
research nobody has decided about yet. The gate fails only on deadlocks *not* in
that file. Shrink the baseline deliberately as the research pass settles; never
grow it to silence something a change introduced. `--update-baseline` rewrites it,
and `--raw` restores the old unpatched view for comparison.

`patch_check.py` is the one that reads the database the way RimWorld builds it:
every active mod's defs merged in load order, then every third-party patch
applied, then each of our operations measured against the result and applied in
sequence so later operations see what earlier ones did. It prints a **merge
fidelity** block first — unparseable files and any patch operation class it could
not apply. Read that before trusting a count. A handful of skipped operations out
of a thousand is noise; a large number means the baseline is wrong.

Reject any diff claiming def work is complete without evidence that all five ran
clean.

---

## Test discipline

The general reference is the `tdd` skill. This section is how it applies here,
which is not the same as how it applies to a TypeScript service.

### The red–green loop for def work

Def work has a real loop and most people skip it. **The match count is the test**,
and it is enforced rather than left to discipline.

1. **Red.** Before writing a PatchOperation, run its xpath and see what it
   matches today:

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

3. **Repeat.** `python tools/patch_check.py` now holds every annotated operation
   to its number, and fails the build when one drifts.

**Do not produce the annotation by running the tool and copying its number back.**
That is the tautological test: it asserts only that the tool agrees with itself
and can never disagree with the patch. The number has to be what you expected
*before* you looked — if the tool disagrees, one of you is wrong and that is the
entire value of the exercise.

Annotations are incremental. Unannotated operations are reported, not enforced,
so add them as you touch things rather than in one sweep. Use `--strict` to fail
on any operation that lacks one.

### Two ways a patch fails, only one of which the game mentions

- **Zero matches.** RimWorld does log it, at load, buried in startup spam you
  stopped reading months ago. `patch_check.py` fails on it up front.
- **Wrong matches.** Entirely silent. The patch succeeds, on nodes you did not
  mean. Only a count catches this, which is why the annotation exists.

`<success>Always</success>` suppresses RimWorld's error for the first case, so
those operations are ones the game will *never* mention. `patch_check.py` reports
a zero match on them as a **warning**, not a failure — the author declared that
matching nothing is acceptable — but a warning still means that operation is doing
nothing, so either an earlier operation already covered it or the predicate is
wrong. Find out which.

### The state of C# testing here

**There is no test harness for `Archinity.Altar`, and that is the current
reality, not an oversight to route around.** Do not fabricate one mid-task, and do
not claim tests were run when the verification was "it compiled."

If a change genuinely warrants automated tests, say so and propose the harness in
the issue. Adding a test project unasked is unrequested scope; silently shipping
untestable logic is worse. Raise it and let the decision get made.

### Where the seam is in this codebase

A **seam** is a public boundary you can observe behavior through without reaching
inside. Most of the assembly is welded to Verse statics and has no such boundary.
The one that does exist is **the line between pure decision logic and
Verse-coupled execution** — which gene the lottery draws, what a rite costs, what
the odds resolve to, versus spawning, jobs, and def lookups.

Keep that line clean. Push decisions into functions that take values and return
values, and leave the Verse-coupled half thin enough to read. That is worth doing
for its own sake — it is also the only thing that makes a harness cheap later, if
we decide we want one.

### What a good test is, if you write one

Tests verify behavior through public interfaces, not implementation details. Code
can change entirely; tests shouldn't. A good test reads like a specification and
survives refactors because it does not care about internal structure.

Test only at pre-agreed seams. Write down the seams under test and confirm them
before writing a test — you cannot test everything, and agreeing the boundary up
front is how effort lands on critical paths instead of every edge case.

### Anti-patterns

- **Implementation-coupled** — mocks internal collaborators, tests private
  methods, or verifies through a side channel. The tell: it breaks when you
  refactor but behavior has not changed.
- **Tautological** — the expected value is recomputed the way the code computes
  it, so the test passes by construction and can never disagree with the code.
  Expected values come from an independent source: a known-good literal, a worked
  example, the spec. This one bites hardest in a def project, where it is easy to
  assert that a value equals the value you just patched in.
- **Horizontal slicing** — all tests first, then all implementation. Bulk tests
  verify _imagined_ behavior. Work in **vertical slices**: one test, one
  implementation, repeat, each one responding to what the last cycle taught you.

### Rules of the loop

- **Red before green.** The failing check first, then only enough code to pass it.
  No anticipating future work and no speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation.
- **Refactoring is not part of the loop.** It belongs to review, not to the
  red–green cycle.

---

## Facts over memory

Verify against decompiled source, not memory and not the wiki. Confident
assumptions have been wrong here repeatedly: a RimWorld year is 60 days not 365,
`Mech_Centipede` does not exist, `rootMinProgressScore` ignores research entirely.
`ilspycmd` is available for decompiling.

Flag any assertion in a diff or commit message that reads as recalled rather than
checked.

---

## Documentation

- `CLAUDE.md` is a map, not a manual. It earns pointers and mode-switching rules,
  nothing else.
- **This file** owns everything about how code and defs get written — the rules an
  author follows and a reviewer checks a diff against.
- `CONTEXT.md` owns what the project's words *mean*, and nothing else. A term's
  definition goes there; the rule for applying it stays here. If you find yourself
  explaining a rule in `CONTEXT.md`, or defining a word here, they are swapped.
- `docs/technical-findings.md` owns verified facts, so they are never
  re-litigated.
- `docs/WAYSTONE.md` owns design intent. A diff does not get to change it.

A diff that files a rule in the wrong one of these is misfiled, even when the rule
is correct.
