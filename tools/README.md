# Verification tools

**A def change is not done until all five checks pass.**

```bash
python tools/check_refs.py          # cross-mod defNames resolve
python tools/audit_research.py      # no research gated on unobtainable items
python tools/check_availability.py  # planned MRR materials have 2+ sources
python tools/patch_check.py         # every PatchOperation matches what it should
python -c "from lxml import etree; import glob; [etree.parse(f) for f in glob.glob('**/*.xml', recursive=True)]"
```

All five are needed and none subsumes another. `CODING_STANDARDS.md` carries the
rule; this file carries how each one behaves.

## `check_refs.py`

Validates defNames only. It **passes** on files that do not parse, on fields that do
not exist, and on defs nothing references — which is why the raw `lxml` parse above
is a separate gate rather than a redundant one.

## `audit_research.py`

Reads the **merged, patched** database, so its tier totals reflect any retier we
have shipped.

It carries a **baseline** in `audit_research_baseline.txt`: 34 deadlock risks living
in third-party research nobody has decided about yet. The gate fails only on
deadlocks *not* in that file.

- Shrink the baseline deliberately as the research pass settles.
- **Never grow it to silence something a change introduced.**
- `--update-baseline` rewrites it; `--raw` restores the old unpatched view for
  comparison.

## `patch_check.py`

The only check that reads the database the way RimWorld builds it: every active
mod's defs merged in load order, then every third-party patch applied, then each of
our operations measured against the result and applied in sequence, so later
operations see what earlier ones did. The sequence itself is documented in
`docs/engine/def-loading.md`.

It prints a **merge fidelity** block first — unparseable files, and any patch
operation class it could not apply. **Read that before trusting a count.** A handful
of skipped operations out of a thousand is noise; a large number means the baseline
is wrong and every count below it is suspect.

It also enforces the `<!-- expect: N -->` annotations described in
`CODING_STANDARDS.md` § *Test discipline*:

- An annotated operation whose match count has drifted **fails**.
- An unannotated operation is **reported, not enforced** — annotations are
  incremental, added as you touch things. `--strict` fails on any operation lacking
  one.
- A zero match on an operation carrying `<success>Always</success>` is a **warning**,
  not a failure: the author declared that matching nothing is acceptable. A warning
  still means that operation is doing nothing, so find out whether an earlier
  operation already covered it or the predicate is wrong.

## `xpath.py`

The red half of the def red–green loop.

```bash
python tools/xpath.py '/Defs/ResearchProjectDef[techLevel="Medieval"]'
```

Prints the match count and identifies each matched node — defName, whether it is
`ABSTRACT`, and its `ParentName`. A predicate meant to hit twelve children that
instead hits one abstract parent is obvious here and silent everywhere else; that
failure is `docs/TRAPS.md` T-02.

## The rest

`defdb.py` is the shared database loader the checks build on. `inventory.py`,
`survey_archite.py` and `make_faction_icons.py` are one-off surveys and asset
tooling, not gates.
