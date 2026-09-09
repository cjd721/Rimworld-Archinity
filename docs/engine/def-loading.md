# How the def database is built

The order in which RimWorld assembles defs, and what that order means for a patch.
Most of the traps in `docs/TRAPS.md` § *Defs and patching* are consequences of this
sequence — this file is the mechanism, the register is the rule.

Verified against RimWorld 1.6.4871.

## The sequence

1. **Merge.** Every active mod's defs are merged in load order
   (`config/ModsConfig.xml`), producing one database. Files, not mods, are the unit
   — a file that fails to parse drops out of the merge, and T-01 is the way that
   happens most often.
2. **Patch.** Every active mod's PatchOperations are applied, in load order, against
   that merged database. Operations run **in sequence**, so a later operation sees
   what earlier ones did — including ours seeing third-party patches, and our own
   operations seeing each other.
3. **Resolve inheritance.** `ParentName` / `Abstract` inheritance is resolved.
4. **Resolve cross-references.** defName references are bound to their targets.

`tools/patch_check.py` reproduces exactly this order, which is why it is the only
one of the five checks that reads the database the way the game does. See
`tools/README.md`.

## Patching happens before inheritance — step 2 precedes step 3

This is the single most consequential property of the sequence. At patch time an
Abstract parent's fields exist **only on the parent**; the children that will
inherit them have not been given them yet. A predicate written against the merged,
*resolved* database you can see in-game matches one abstract node rather than the
twelve children you meant (`docs/TRAPS.md` T-02). Match on `@ParentName` instead.

## An xpath has no scope

There is no file-level or mod-level scoping on an xpath: it addresses the whole
merged database from step 1. `PatchOperationFindMod` only checks that a mod is
*active* — it does not scope the xpath it guards (`docs/TRAPS.md` T-03). Medieval
Overhaul's `component_replace` is the production example, reaching 395 ThingDefs
across Core, four DLC and 47 mods (T-26).

The defence is a node count: `python tools/xpath.py '<xpath>'` before you write the
operation, and a `<!-- expect: N -->` annotation after, so `patch_check.py` holds it
there. The full red–green loop is in `CODING_STANDARDS.md`.

## Inheritance appends lists, it does not replace them

`XmlInheritance.RecursiveNodeCopyOverwriteElements` **appends** list children, so a
child def's list holds the parent's entries plus its own. `Inherit="False"` on the
list clears the parent's first (`docs/TRAPS.md` T-05).

This is load-bearing in both directions. It is why a KCSG child's
`allowedStructures` silently merges with its parent's, and equally why
`Substructure` — `ParentName="FloorBase"` — resolves to the full affordance list
`[Light, Medium, Heavy, Walkable, Substructure]` that lets a gravship fly. See
`docs/engine/gravship-and-substructure.md`.

## Unresolved references are dropped, not nulled

At step 4, a reference that does not resolve is **omitted from the list** rather
than set to null. A prerequisite list that loses its only entry therefore reads as
"no prerequisite" rather than "broken prerequisite", and nothing reports it
(`docs/TRAPS.md` T-04). Deleting a `ResearchProjectDef` strips the requirement off
everything that needed it, leaving those things buildable at once — the opposite of
the intent. Neuter referencing defs first; delete the research last.

## Mod extensions resolve to the first match

`Def.GetModExtension` returns the first extension of the requested type and does not
error on ambiguity, so a second one of the same type is inert (`docs/TRAPS.md`
T-06). Never add an extension of a type a def already carries.

## The two ways a patch fails

- **Zero matches.** RimWorld *does* log this, at load, buried in startup spam.
  `patch_check.py` fails on it up front. `<success>Always</success>` suppresses the
  engine's error entirely, so those operations are ones the game will **never**
  mention — `patch_check.py` downgrades them to a warning, since the author declared
  that matching nothing is acceptable, but a warning still means the operation is
  doing nothing. Find out whether an earlier operation already covered it or the
  predicate is wrong.
- **Wrong matches.** Entirely silent. The patch succeeds, on nodes you did not mean.
  Only a count catches this, which is the whole reason the `<!-- expect: N -->`
  annotation exists.
