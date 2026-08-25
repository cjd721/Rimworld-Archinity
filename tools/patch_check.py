"""
Match-count checker for every PatchOperation Archinity ships.

THE GAP THIS FILLS

check_refs.py and audit_research.py read raw def files. Neither of them applies
a PatchOperation, so nothing in the toolchain has ever verified what the def
database looks like *after* our patches land. Three of the four silent failures
in CODING_STANDARDS.md are about patches matching something other than what the
author expected, so that is the hole this closes.

TWO FAILURES, ONLY ONE OF WHICH THE GAME REPORTS

  Zero matches.  RimWorld does log this, but at load time, in the middle of a
                 wall of unrelated logspam, long after you stopped looking.
                 Caught here instead, before the game runs.

  Wrong matches. Completely silent. The patch succeeds, on nodes you did not
                 mean. This is the Abstract/ParentName trap: a predicate on a
                 field declared only on the parent matches the parent, not its
                 children, and nothing anywhere says so. A count is the only
                 thing that catches it.

THE EXPECTATION ANNOTATION

Write the count you expect in an XML comment directly above the operation:

    <!-- expect: 3 -->
    <Operation Class="PatchOperationReplace">

That turns the red-green loop in CODING_STANDARDS.md into something a machine
checks. Operations without an annotation are reported but not enforced, so
adding them is incremental. Never write the annotation by running the tool and
copying its number back - that is the tautological test, and it asserts only
that the tool agrees with itself.

Run:  python tools/patch_check.py [--strict] [--fast]

  --strict  also fail on operations that carry no expect: annotation
  --fast    skip third-party patches; much quicker, less accurate baseline
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import defdb
from defdb import etree

EXPECT = re.compile(r"expect\s*:\s*(\d+)", re.I)


def expected_count(op):
    """Read an <!-- expect: N --> comment sitting above this operation."""
    prev = op.getprevious()
    while prev is not None and isinstance(prev, etree._Comment):
        match = EXPECT.search(prev.text or "")
        if match:
            return int(match.group(1))
        prev = prev.getprevious()
    return None


def main():
    strict = "--strict" in sys.argv
    fast = "--fast" in sys.argv

    print("building merged def database ...")
    defs_root, report, our_patches = defdb.build(
        apply_our_patches=False,
        apply_thirdparty_patches=not fast,
        verbose=True,
    )

    if fast:
        print("  --fast: third-party patches NOT applied; counts are a "
              "lower-fidelity baseline")
    print()

    notes = report.render()
    if notes:
        print("merge fidelity:")
        print(notes)
        print()

    if not our_patches:
        print("no Archinity patch files found - nothing to check.")
        return 1

    failures = 0
    warnings = 0
    annotated = 0
    unannotated = 0
    checked = 0
    active = report.active_ids

    for path in sorted(our_patches):
        rel = os.path.relpath(path, defdb.REPO)
        try:
            patch_tree = etree.parse(path, defdb.PARSER)
        except etree.XMLSyntaxError as exc:
            print("  BROKEN  %s\n          %s" % (rel, exc))
            failures += 1
            continue

        print(rel)
        for label, op in defdb.iter_operations(patch_tree.getroot(),
                                               active_ids=active,
                                               root=defs_root):
            xpath_node = op.find("xpath")
            if xpath_node is None or not (xpath_node.text or "").strip():
                continue
            xpath = xpath_node.text.strip()
            checked += 1

            try:
                matched = len(defs_root.xpath(xpath))
            except etree.XPathEvalError as exc:
                print("    FAIL  %s\n          invalid xpath: %s"
                      % (label, exc))
                print("          %s" % xpath)
                failures += 1
                continue

            want = expected_count(op)
            short = xpath if len(xpath) <= 88 else xpath[:85] + "..."
            # <success>Always</success> is the author declaring that matching
            # nothing is acceptable. It also suppresses RimWorld's own load
            # error, so these are the operations the game will never mention.
            tolerated = (op.findtext("success") or "").strip().lower() == "always"

            if matched == 0 and tolerated:
                print("    warn  %-28s matched 0   (success: Always)" % label)
                print("          %s" % short)
                print("          does nothing. Either an earlier operation "
                      "already covered it, or the predicate is wrong -")
                print("          the game will not tell you which, because "
                      "success Always suppresses the error.")
                warnings += 1
            elif matched == 0:
                print("    FAIL  %s  matched 0" % label)
                print("          %s" % short)
                print("          patch will do nothing; RimWorld logs this at "
                      "load, buried in the startup spam")
                failures += 1
            elif want is None:
                print("    ----  %-28s matched %d   (no expect: annotation)"
                      % (label, matched))
                print("          %s" % short)
                unannotated += 1
            elif matched != want:
                print("    FAIL  %s  matched %d, expected %d"
                      % (label, matched, want))
                print("          %s" % short)
                print("          if the new count is correct, the patch's "
                      "intent changed - update the annotation deliberately")
                failures += 1
            else:
                print("    ok    %-28s matched %d" % (label, matched))
                annotated += 1

            # Apply it, so later operations in the same file see its effect,
            # exactly as they will in game.
            defdb.apply_operation(defs_root, op, report, active)
        print()

    print("%d operation(s) checked: %d annotated, %d unannotated, "
          "%d warning(s), %d failure(s)."
          % (checked, annotated, unannotated, warnings, failures))

    if failures:
        print("\n%d failing operation(s). Fix before loading." % failures)
        return 1
    if strict and unannotated:
        print("\n--strict: %d operation(s) carry no expect: annotation."
              % unannotated)
        return 1
    if not report.trustworthy():
        print("\nAll operations matched, but see the merge fidelity notes "
              "above before trusting the counts.")
    else:
        print("\nall operations match their expected node counts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
