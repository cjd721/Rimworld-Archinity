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

## `route_inventory.py`

Not a gate. Parses `docs/CAPABILITIES.md` into `docs/data/route-inventory.json`: every
card, capability row and route, with a stable ID each, for the working surface (#200,
#199). Regenerate after editing the capabilities document; never hand-edit the JSON.

```bash
python tools/route_inventory.py                    # regenerate
python tools/route_inventory.py --check            # exit 1 if the JSON is stale
python tools/route_inventory.py --accept-renumber  # retire IDs of removed or reworded rows
```

- **IDs never move.** The existing JSON is the registry: an unchanged row or route keeps
  its ID wherever it moves in the document, and new ones are minted after the card's
  highest number. A row or route that vanished or was reworded stops the run, because
  surface state may point at it; `--accept-renumber` retires those IDs for good.
- **Cells that do not parse mechanically** are handled by the fix-up tables at the top of
  the script, each citing its line. A fix-up whose text is gone fails the run.
- **A new card** fails the run until it has an ID in `CARD_IDS`.
- Every route value carries provenance: `explicit` (the route states it), `inherited`
  (from the row, a group heading or a shared label list) or `unstated` (null).

## The rest

`defdb.py` is the shared database loader the checks build on. `inventory.py`,
`survey_archite.py` and `make_faction_icons.py` are one-off surveys and asset
tooling, not gates.

## `surface_server.py`

Not a gate. Serves the working surface (#199), `tools/surface/index.html`, on
127.0.0.1. The surface state **is** `docs/data/working-surface.json`: the page loads it and
saves the whole file after every edit, atomically and in a fixed key order. A save is refused
if the file changed on disk since the page loaded it, so an agent's edit to the file is never
overwritten; reload the page to pick it up.

```bash
python tools/surface_server.py                                                  # full inventory, http://127.0.0.1:8765
python tools/surface_server.py --inventory docs/data/route-inventory.slice.json # the 14-row slice
python tools/surface_server.py --state path/to/scratch.json                     # try things without touching the real file
```

`--port` and `--state` override the defaults; `--state` may be absolute. The slice,
`docs/data/route-inventory.slice.json`, is 14 rows filtered verbatim from the full inventory,
so its IDs match it. `GET /api/doc?path=docs/…md&anchor=slug` serves one markdown section,
read-only, from under `docs/` only; the page uses it to render spec sections in its panel.
`GET /api/glosses` serves `docs/data/capability-glosses.json` (override with `--glosses`); the page
leads with each gloss title and falls back to the card's wording when the file or an entry is missing.
`GET /api/agent-state` serves the agent's assessment, `docs/data/working-surface.agent.json`
(override with `--agent-state`), read-only: a PUT to it is refused, and a missing file means no
assessment yet. The page's **Mine | Agent's** toggle shows it with every edit control off.
