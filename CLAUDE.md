# Archinity

A suite of RimWorld 1.6 mods for one long two-player co-op playthrough on the
**Multiplayer** mod. Neolithic start, every tech era in order, endgame in orbit.

Read `docs/VISION.md` first — it holds the intent that cannot be recovered from
the code. Then `docs/technical-findings.md` for facts already verified against
decompiled source. Check `docs/HANDOFF.md` for open decisions before starting
anything.

**Verify against decompiled source, not memory and not the wiki.** Several
confident assumptions have turned out wrong here: a RimWorld year is 60 days
not 365, `Mech_Centipede` does not exist, `rootMinProgressScore` ignores
research entirely. `ilspycmd` is installed for decompiling.

## XML defs by default

Def-only mods carry no simulation code, so they are inherently multiplayer-safe.
That is why almost everything here is pure XML.

`Archinity.Altar` is the one exception and ships a Harmony assembly. Anything
added to it must be deterministic across clients — every `Rand` call has to sit
inside an already-synced job or tick that both clients execute identically, or
the session desyncs. Do not start a second assembly without an explicit decision.

## Silent failures — these do not error, they just do not work

- **Never put `--` inside an XML comment.** RimWorld drops the entire file with
  no error naming the cause. Use `=` for divider rules. This has bitten twice,
  once by an agent that had just written the warning into a doc.
- **PatchOperations run on raw XML before `ParentName` inheritance resolves.**
  A predicate on a field declared only on an Abstract parent matches the parent,
  not its children. Match on `@ParentName` instead.
- **Unresolvable cross-references are omitted, not set to null.** Deleting a
  ResearchProjectDef therefore *strips the prerequisite* off everything that
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

## What earns a slot in this file

Only rules whose violation produces **no error message**. A noisy failure
teaches you itself. Everything else belongs in `docs/technical-findings.md`.
