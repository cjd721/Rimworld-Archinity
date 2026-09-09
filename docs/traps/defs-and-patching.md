# Traps: defs and patching

How a patch or a def file fails without saying so. The mechanism behind these is
`docs/engine/def-loading.md`.

Part of the trap register. **The index at `docs/TRAPS.md` is the file you read
before a diff**; this one carries the full entries for this group. Every entry here
fails with no error message. Cite by ID.

## Defs and patching

### T-01 — Never put `--` inside an XML comment

The entire file vanishes from the database, with no error naming the file, the def
or the cause: `--` terminates an XML comment early, and RimWorld drops the whole
file rather than reporting a parse failure against it. Use `=` for divider rules.

*Has bitten this project twice — once by an agent that had just written the warning
into a doc. 1.6.4871.*

### T-02 — PatchOperations run before `ParentName` inheritance resolves

Patches operate on raw XML, so a field declared only on an Abstract parent exists
only on the parent at patch time. A predicate written against a field you can see
in the merged database matches one abstract node instead of the twelve children you
meant. Match on `@ParentName` instead, and run `python tools/xpath.py '<xpath>'`
first — it prints the count and flags `ABSTRACT` nodes.

*`tools/xpath.py`; the def red–green loop in `CODING_STANDARDS.md`. 1.6.4871.*

### T-03 — Patch xpaths apply to the whole merged def database

There is no file or mod scoping on an xpath. `PatchOperationFindMod` only checks
that a mod is *active*; it does not scope the xpath it guards. An operation
intended for one mod's files silently edits defs from Core, the DLC and every other
mod that shares the shape. Confirm the node count before shipping, and annotate the
operation `<!-- expect: N -->` so `patch_check.py` holds it there.

*`tools/patch_check.py`. T-26 is the canonical victim, at 395 defs. 1.6.4871.*

### T-04 — Unresolvable cross-references are omitted, not set to null

The loader drops a reference it cannot resolve rather than nulling the field, so a
prerequisite list loses its entry and reads as "no prerequisite". Deleting a
`ResearchProjectDef` therefore leaves everything that required it buildable with
**no research prerequisite at all** — the exact opposite of the intent, and nothing
reports it. Order matters: neuter the referencing defs first, delete the research
last, and re-run `python tools/audit_research.py` after either half.

*Def-load behaviour; `tools/check_refs.py` exists for this class. 1.6.4871.*

### T-05 — `XmlInheritance` appends list children rather than replacing them

`XmlInheritance.RecursiveNodeCopyOverwriteElements` appends, so a `ParentName`
child's list silently contains the parent's entries as well as its own — a child's
`allowedStructures` merges with the parent's instead of overriding it.
`Inherit="False"` clears first. Assume merge, not override, whenever you inherit a
list.

*Same mechanism gives `Substructure` its full affordance list —
`docs/engine/gravship-and-substructure.md`. 1.6.4871.*

### T-06 — `Def.GetModExtension` returns the FIRST match

The lookup returns on first match rather than erroring on ambiguity, so a second
extension of the same type is silently ignored. Never
`PatchOperationAddModExtension` a second extension of a type a def already carries
— in particular a second `KCSG.CustomGenOption` onto a faction. Patch its
settlement def instead.

*`docs/engine/mods/kcsg.md`. 1.6.4871.*

---
