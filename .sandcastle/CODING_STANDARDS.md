# Coding Standards

Loaded by the reviewer agent via `@.sandcastle/CODING_STANDARDS.md`. These are
the Archinity rules that a diff can violate. `CLAUDE.md` is the source of truth;
this file is the reviewer's checklist against it.

Archinity is a suite of RimWorld 1.6 mods for one long two-player co-op
playthrough on the **Multiplayer** mod. Most of it is pure XML defs. One C#
assembly ships: `Archinity.Altar`.

## The bar for a change

Simplest thing that achieves the goal without violating a constraint. XML is the
usual answer, not the rule. Reject unrequested scope, speculative abstraction,
and cleverness that buys nothing.

## Hard constraints — reject a diff that violates these

- **Desync.** Every `Rand` call must sit inside an already-synced job or tick
  that both clients execute identically. Unsynced `Rand` and per-client cached
  state desync the session. The test on any new code: *does this need a random
  number or a client-local cache?* If yes, it needs justification in the diff.
- **Save integrity.** Two people play one save across months of real time. Small
  code that fails loudly beats clever code that fails quietly. A broken save is
  worse than a missing feature.
- **One assembly.** `Archinity.Altar` ships the Harmony assembly. A diff that
  introduces a second assembly is rejected unless the issue explicitly decided
  to.

## Silent failures — these do not error, they just do not work

Flag every occurrence. None of these produce an error message, so they will not
be caught by running the game.

- **No `--` inside an XML comment.** RimWorld drops the entire file with no error
  naming the cause. Use `=` for divider rules.
- **PatchOperations run on raw XML, before `ParentName` inheritance resolves.**
  A predicate on a field declared only on an Abstract parent matches the parent,
  not its children. Match on `@ParentName` instead.
- **Unresolvable cross-references are omitted, not set to null.** Deleting a
  `ResearchProjectDef` *strips the prerequisite* off everything that required it,
  leaving those things buildable with no research at all — the opposite of the
  intent. Order is: neuter referencing defs first, delete the research last.
- **Patch xpaths apply to the whole merged def database**, not to one mod's
  files. `PatchOperationFindMod` only checks that a mod is active; it does not
  scope the xpath. A new predicate must be confirmed to match the node count the
  author expected.
- **Mod settings are part of the sync surface.** Both players need identical
  mods, identical load order (`config/ModsConfig.xml`) *and* identical mod
  settings (`config/ModSettings/`). TechBlock, Ignorance Is Bliss and Medieval
  Overhaul are settings-driven; a mismatch means divergent defs and an immediate
  desync. A diff that changes settings must re-snapshot them.

## Verification — a def change is not done until all four pass

```bash
python tools/check_refs.py          # cross-mod defNames resolve
python tools/audit_research.py      # no research gated on unobtainable items
python tools/check_availability.py  # planned MRR materials have 2+ sources
python -c "from lxml import etree; import glob; [etree.parse(f) for f in glob.glob('**/*.xml', recursive=True)]"
```

All four are needed and none subsumes another. `check_refs.py` validates
defNames only — it passes on files that do not parse, on fields that do not
exist, and on defs nothing references. `audit_research.py` reads raw defs and
does **not** apply our own PatchOperations, so its tier totals lag any retier
already shipped; treat a tier-total mismatch as expected, not as a finding.

Reject any diff claiming def work is complete without evidence that all four ran
clean.

## Facts over memory

Verify against decompiled source, not memory and not the wiki. Confident
assumptions have been wrong here repeatedly: a RimWorld year is 60 days not 365,
`Mech_Centipede` does not exist, `rootMinProgressScore` ignores research
entirely. `ilspycmd` is available for decompiling. Flag any assertion in the diff
or its commit message that reads as recalled rather than checked.

## Documentation

`CLAUDE.md` earns only rules whose violation produces **no error message** — a
noisy failure teaches you itself. Everything else belongs in
`docs/technical-findings.md`. A diff that adds a noisy-failure rule to
`CLAUDE.md` is misfiled.
