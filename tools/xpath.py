"""
Ad-hoc xpath query against the merged def database.

This is the RED half of the loop in CODING_STANDARDS.md. Before writing a
PatchOperation, run its xpath here and see what it actually matches. That
number is your assertion; write it into the patch as <!-- expect: N --> and
patch_check.py will hold you to it.

It is also the fastest way to catch the Abstract/ParentName trap, because the
matched nodes are printed with their defName - so a predicate that was meant to
hit twelve children and instead hit one abstract parent is obvious on sight
rather than silent in game.

Run:  python tools/xpath.py '<xpath>' [--ours] [--fast] [-n N]

  --ours   also apply Archinity's own patches, showing the tree as it ends up
           rather than the baseline a new patch is about to act on
  --fast   skip third-party patches (quicker, lower fidelity)
  -n N     show N matches (default 10)

Quote the xpath in single quotes; it contains characters your shell will eat.

  python tools/xpath.py '/Defs/ResearchProjectDef[techLevel="Medieval"]'
  python tools/xpath.py '/Defs/ThingDef[@ParentName="BaseBed"]/statBases'
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import defdb
from defdb import etree


def describe(node):
    """A one-line identity for a matched node."""
    if not isinstance(node, etree._Element):
        return repr(node)

    owner = node
    name = None
    while owner is not None:
        found = owner.find("defName")
        if found is not None and found.text:
            name = found.text.strip()
            break
        owner = owner.getparent()

    tag = node.tag
    abstract = node.get("Abstract") or (owner.get("Abstract") if owner is not None else None)
    parent_name = node.get("ParentName") or (owner.get("ParentName") if owner is not None else None)

    bits = []
    if name:
        bits.append(name)
    elif owner is not None and owner.get("Name"):
        bits.append("Name=%s" % owner.get("Name"))
    if owner is not None and owner is not node:
        bits.append("in <%s>" % owner.tag)
    if abstract and str(abstract).lower() == "true":
        bits.append("ABSTRACT")
    if parent_name:
        bits.append("ParentName=%s" % parent_name)

    text = (node.text or "").strip()
    if text and len(node) == 0:
        bits.append("= %s" % (text if len(text) <= 40 else text[:37] + "..."))

    return "<%s>  %s" % (tag, "  ".join(bits))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print(__doc__.strip())
        return 2

    limit = 10
    if "-n" in sys.argv:
        try:
            limit = int(sys.argv[sys.argv.index("-n") + 1])
        except (IndexError, ValueError):
            pass

    xpath = args[0]
    ours = "--ours" in sys.argv
    fast = "--fast" in sys.argv

    print("building merged def database ...")
    defs_root, report, _ = defdb.build(
        apply_our_patches=ours,
        apply_thirdparty_patches=not fast,
        verbose=True,
    )
    print("  archinity patches %s\n" % ("applied" if ours else "held back"))

    notes = report.render()
    if notes:
        print("merge fidelity:")
        print(notes)
        print()

    try:
        matches = defs_root.xpath(xpath)
    except etree.XPathEvalError as exc:
        print("invalid xpath: %s" % exc)
        return 1

    if not isinstance(matches, list):
        print("%s\n  => %r" % (xpath, matches))
        return 0

    print("%s\n" % xpath)
    print("  matched %d node(s)" % len(matches))
    if matches:
        print()
        for node in matches[:limit]:
            print("    %s" % describe(node))
        if len(matches) > limit:
            print("    ... and %d more  (-n %d to see them)"
                  % (len(matches) - limit, len(matches)))

    print("\n  write this into the patch as:  <!-- expect: %d -->" % len(matches))
    return 0


if __name__ == "__main__":
    sys.exit(main())
