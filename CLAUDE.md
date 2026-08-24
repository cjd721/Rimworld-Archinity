# Archinity

A suite of RimWorld 1.6 mods for one long two-player co-op playthrough on the
**Multiplayer** mod. Neolithic start, every tech era in order, endgame in orbit.

## How we work

You may be writing code, checking diffs, testing integrations, or you may be theory crafting, writing narrative, and figuring out what fun looks like in gameplay.

Be flexible to the task at hand. Do not bring technical jargon into the realm of imagination. When it is time to implement, carefully engineer the simplest solution.

## The constraint is desync, not C#

Def-only mods carry no simulation code, so they are inherently multiplayer-safe,
and that is why most of this project is pure XML. But XML is the usual answer,
not the rule. **Write the simplest, most elegant thing that achieves the goal
without violating a constraint.** The constraints are:

- **Desync.** Unsynced `Rand` calls and per-client cached state. Every `Rand` has
  to sit inside an already-synced job or tick that both clients execute
  identically, or the session desyncs.
- **Save integrity.** Two people play one save across months of real time. A
  broken save is worse than a missing feature, so small code that fails loudly
  beats clever code that fails quietly.
- **One assembly.** `Archinity.Altar` ships the Harmony assembly. Do not start a
  second one without an explicit decision.

Working test before proposing anything: **does this need a random number or a
client-local cache?** If no, code is cheap — GameComponents, stat parts, ITabs,
inspect strings, letters and synced designators all cost nothing. If yes, think
hard or push it into XML. The expensive thing was never writing the code, it was
debugging a desync in a live co-op session.

## Silent failures — these do not error, they just do not work

- **Never put `--` inside an XML comment.** RimWorld drops the entire file with
  no error naming the cause. Use `=` for divider rules. This has bitten twice,
  once by an agent that had just written the warning into a doc.
- **PatchOperations run on raw XML before `ParentName` inheritance resolves.**
  A predicate on a field declared only on an Abstract parent matches the parent,
  not its children. Match on `@ParentName` instead.
- **Unresolvable cross-references are omitted, not set to null.** Deleting a
  ResearchProjectDef therefore _strips the prerequisite_ off everything that
  required it, leaving those things buildable with no research at all — the
  opposite of the intent. Neuter referencing defs first, delete the research last.
- **Patch xpaths apply to the whole merged def database**, not to one mod's
  files. `PatchOperationFindMod` only checks that a mod is active; it does not
  scope the xpath. Confirm a predicate matches the node count you expect.

## Before claiming any def work is done

```bash
python tools/check_refs.py          # cross-mod defNames resolve
python tools/audit_research.py      # no research gated on unobtainable items
python tools/check_availability.py  # planned MRR materials have 2+ sources
python -c "from lxml import etree; import glob; [etree.parse(f) for f in glob.glob('**/*.xml', recursive=True)]"
```

`check_refs.py` validates defNames only. It passes on files that do not parse,
on fields that do not exist, and on defs nothing references. All four checks are
needed. `audit_research.py` reads raw defs and does **not** apply our own
PatchOperations, so its tier totals lag any retier we have shipped.

## Multiplayer

Both players need identical mods, identical load order (`config/ModsConfig.xml`)
**and identical mod settings** (`config/ModSettings/`). The third is the one
people miss — TechBlock, Ignorance Is Bliss and Medieval Overhaul are all
settings-driven, and a mismatch means divergent defs and an immediate desync.
Re-snapshot after any settings change.

## Agent skills

### Issue tracker

Issues live as GitHub issues on `cjd721/Rimworld-Archinity`, driven by the `gh`
CLI. `scratch/` is recon prose, not the tracker. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical roles, used verbatim as label strings. See
`docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and one `docs/adr/` at the repo root, both created
lazily. See `docs/agents/domain.md`.

## What earns a slot in this file

Only rules whose violation produces **no error message**. A noisy failure
teaches you itself. Everything else belongs in `docs/technical-findings.md`.
