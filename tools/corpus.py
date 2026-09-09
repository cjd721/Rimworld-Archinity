"""
The corpus: every mod on disk, whether or not it is active.

Capability research asks "does anything already carry this?" A *negative* answer
to that question is only worth something if the search was wide. Every other
tool here narrows to the active set before it starts:

    defdb.load_order()      reads config/ModsConfig.xml
    patch_check.py          builds on defdb
    audit_research.py       builds on defdb
    inventory.py            "the ACTIVE mod set", by its own docstring

That is correct for those tools - they answer "what will RimWorld build from
today's load order". It is exactly wrong for research. VFE Empire and VFE
Deserters are not in ModsConfig, and they are the named donor systems for
Exaltation, Influence, Intel and Trace. An agent that asks the active database
"what carries Honor" is told "nothing", and concludes we must write it. That
false negative costs an assembly.

`docs/data/PARTS-BIN.md` says it outright: the active/inactive split "carries
zero weight". This tool is that sentence, executable.

It does not search content - the agent's own grep is ripgrep and is faster than
anything here. It answers the two questions grep cannot:

    which mod is this hit in, and is it active?

Note that ripgrep must be told to search binaries (-a) and that most of the
corpus ships assemblies rather than source, so a wide pass over `.cs` files
alone covers roughly a fifth of it. See docs/agents/capability-research.md.

Run:
  python tools/corpus.py                     # table to stdout
  python tools/corpus.py --write             # rewrite docs/data/MOD-SNAPSHOT.md
  python tools/corpus.py --check             # diff disk against the snapshot
  python tools/corpus.py --which <path>...   # attribute paths to their mods
  python tools/corpus.py --inactive          # only the mods the tools cannot see

--which takes a mod root, a file, or many of either, and reads paths from stdin
with `-` so a whole wide pass is attributed in one call. It accepts raw ripgrep
output (`path:line:match`), and collapses many hits to one row per mod:

  rg -a -l "TryAffectGoodwillWith" <roots> -g '*.dll' \
    | python tools/corpus.py --which -

--write commits a *version pin*. Workshop mods update themselves; a finding
cited against "the version on disk in September" is unreconstructable later,
and this project has already been bitten once - VEF dropped its Multiplayer
integration in the 1.6 build. --check tells you which mods have moved under a
finding since the pin was taken.
"""

import argparse
import os
import re
import sys
from datetime import datetime, timezone

from lxml import etree

PARSER = etree.XMLParser(recover=True, remove_blank_text=True)

# The table is full of em dashes and mod names are not ASCII. A Windows console
# defaults to cp1252 and mangles both; the snapshot file is written utf-8
# regardless, but --check and --which print straight to stdout.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
WORKSHOP = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
LOCAL = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods"

# Our own mods live in the repo; the repo copy is the truth, not the export.
OURS = ("Archinity.Origins", "Archinity.Pacing", "Archinity.Drifters",
        "Archinity.Glitterites", "Archinity.Altar")

VERSION = "1.6"
SNAPSHOT = os.path.join(REPO, "docs", "data", "MOD-SNAPSHOT.md")


def active_ids():
    """Lowercased packageIds in ModsConfig, in load order."""
    path = os.path.join(REPO, "config", "ModsConfig.xml")
    if not os.path.isfile(path):
        return []
    tree = etree.parse(path, PARSER)
    return [li.text.strip().lower()
            for li in tree.findall(".//activeMods/li") if li.text]


def _text(root, tag):
    node = root.find(tag)
    return node.text.strip() if node is not None and node.text else ""


def read_about(mod_root):
    """packageId, name, author, supportedVersions from About/About.xml.

    packageId must be a DIRECT child of <ModMetaData>. A descendant search
    picks up the ids inside <modDependencies> instead, which files a mod under
    one of its dependencies and leaves the real mod unfindable. defdb.py
    carries the same warning; it was a real bug there.
    """
    about = os.path.join(mod_root, "About", "About.xml")
    if not os.path.isfile(about):
        return None
    try:
        root = etree.parse(about, PARSER).getroot()
    except etree.XMLSyntaxError:
        return None
    pid = _text(root, "packageId").lower()
    if not pid:
        return None
    versions = [li.text.strip() for li in root.findall("supportedVersions/li")
                if li is not None and li.text]
    return {"packageId": pid,
            "name": _text(root, "name") or os.path.basename(mod_root),
            "author": _text(root, "author"),
            "supported": versions}


def _supports_current(mod_root, about):
    """Does this mod actually load under 1.6?

    Three ways a mod can say yes, and About.xml is only the first. A mod with a
    loadFolders.xml entry for the version, or a version-named content folder,
    loads regardless of what supportedVersions claims - and several in the bin
    support 1.6 that way without updating About.xml.
    """
    if VERSION in about["supported"]:
        return True
    if os.path.isdir(os.path.join(mod_root, VERSION)):
        return True
    lf = os.path.join(mod_root, "loadFolders.xml")
    if os.path.isfile(lf):
        try:
            root = etree.parse(lf, PARSER).getroot()
        except etree.XMLSyntaxError:
            return False
        if root.find("v%s" % VERSION) is not None:
            return True
    return False


VERSION_DIR = re.compile(r"^\d+\.\d+$")


def _code_layout(mod_root):
    """Where a mod's C# lives, and *for which game version*.

    Never answers a bare yes. VFE Empire ships 176 .cs files under `1.4/Source/`
    and none under `1.5/` or `1.6/`, while shipping a distinct VFEEmpire.dll for
    each of the three. An agent told "source: yes" reads two-version-stale code
    while the game runs the 1.6 assembly. Issue #73 already made exactly that
    mistake, citing a 1.4 line count as a 1.6 fact.

    So: source is recorded per version, and `stale_source` is set when a mod
    ships source but none of it is for the version we run. That is the signal to
    decompile the shipped assembly instead of reading the source next to it.
    """
    buckets = {}

    def note(key, filename):
        flags = buckets.setdefault(key, {"cs": False, "dll": False})
        low = filename.lower()
        if low.endswith(".cs"):
            flags["cs"] = True
        elif low.endswith(".dll"):
            flags["dll"] = True

    try:
        entries = sorted(os.listdir(mod_root))
    except OSError:
        return [], [], False

    for name in entries:
        sub = os.path.join(mod_root, name)
        if not os.path.isdir(sub):
            continue
        key = name if VERSION_DIR.match(name) else "root"
        for _, dirs, files in os.walk(sub):
            # Textures and Languages are the bulk of 1.7GB and hold no code.
            dirs[:] = [d for d in dirs
                       if d.lower() not in ("textures", "languages", "sounds")]
            for f in files:
                note(key, f)
            flags = buckets.get(key, {})
            if flags.get("cs") and flags.get("dll"):
                break

    source = sorted(k for k, v in buckets.items() if v["cs"])
    dll = sorted(k for k, v in buckets.items() if v["dll"])
    stale = bool(source) and VERSION not in source and "root" not in source
    return source, dll, stale


def scan():
    """Every mod on disk, keyed by packageId. First base wins, as RimWorld does."""
    active = active_ids()
    active_set = set(active)
    mods = {}

    for base, origin in ((DATA, "core"), (WORKSHOP, "workshop"), (LOCAL, "local")):
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            root = os.path.join(base, name)
            if not os.path.isdir(root):
                continue
            about = read_about(root)
            if not about or about["packageId"] in mods:
                continue
            source, dll, stale = _code_layout(root)
            mods[about["packageId"]] = {
                **about,
                "origin": origin,
                "folder": name,
                "path": root,
                "active": about["packageId"] in active_set,
                "supports": _supports_current(root, about),
                "source": source,
                "dll": dll,
                "stale_source": stale,
                "mtime": datetime.fromtimestamp(
                    os.path.getmtime(root), timezone.utc).strftime("%Y-%m-%d"),
            }

    # The repo copy of our own mods overrides any installed export.
    for name in OURS:
        root = os.path.join(REPO, name)
        about = read_about(root)
        if not about:
            continue
        source, dll, stale = _code_layout(root)
        mods[about["packageId"]] = {
            **about, "origin": "ours", "folder": name, "path": root,
            "active": about["packageId"] in active_set, "supports": True,
            "source": source, "dll": dll, "stale_source": stale,
            "mtime": datetime.fromtimestamp(
                os.path.getmtime(root), timezone.utc).strftime("%Y-%m-%d"),
        }
    return mods


def which(path, mods):
    """Attribute a file path to the mod that owns it. The longest root wins.

    The mod root itself attributes to that mod — a wide pass hands us directories
    as often as files. A `rg` hit of the form `path:line:text` is trimmed to the
    path, so the output of a grep can be piped straight in.
    """
    path = path.strip().strip('"').strip("'")
    if not path:
        return None
    # rg emits "path:line:match"; keep chopping trailing :field until a path exists.
    while not os.path.exists(path) and ":" in path:
        head = path.rsplit(":", 1)[0]
        if head == path or (len(head) <= 2 and head.endswith(":")):
            break                       # bare drive letter, e.g. "C:"
        path = head
    path = os.path.abspath(path)
    best = None
    for mod in mods.values():
        root = os.path.abspath(mod["path"])
        if path.lower() == root.lower() or \
           path.lower().startswith(root.lower() + os.sep):
            if best is None or len(root) > len(best["path"]):
                best = mod
    return best


def which_many(paths, mods):
    """Attribute a batch of paths — the output of a wide pass — to their mods.

    One row per mod, not per hit: a grep with forty hits in three mods is a
    three-line answer. Unattributed paths are reported, never silently dropped,
    because a path that belongs to no mod is usually a broken sweep.
    """
    hits, orphans = {}, []
    for p in paths:
        mod = which(p, mods)
        if mod is None:
            orphans.append(p)
            continue
        hits.setdefault(mod["packageId"], {"mod": mod, "n": 0})["n"] += 1

    rows = sorted(hits.values(),
                  key=lambda h: (h["mod"]["active"], -h["n"],
                                 h["mod"]["name"].lower()))
    print("%d path(s) → %d mod(s)" % (len(paths), len(rows)))
    print()
    for h in rows:
        mod, flags = h["mod"], []
        if not mod["active"]:
            flags.append("INACTIVE — invisible to defdb/patch_check/inventory")
        if not mod["supports"]:
            flags.append("does not load under %s" % VERSION)
        if mod["stale_source"]:
            flags.append("⚠ source is %s only — STALE, decompile the dll"
                         % ", ".join(mod["source"]))
        elif not mod["source"]:
            flags.append("no source — decompile the dll")
        print("%4d  %s  (`%s`)" % (h["n"], mod["name"], mod["packageId"]))
        for f in flags:
            print("      %s" % f)
    if orphans:
        print()
        print("%d path(s) attributed to no mod:" % len(orphans))
        for p in orphans[:10]:
            print("      %s" % p)
        if len(orphans) > 10:
            print("      ... and %d more" % (len(orphans) - 10))
        print("      A path owned by no mod usually means the sweep is wrong,")
        print("      not that the corpus is empty. Check the roots.")
    return 0


def render(mods, inactive_only=False):
    rows = sorted(mods.values(), key=lambda m: (not m["active"], m["name"].lower()))
    if inactive_only:
        rows = [r for r in rows if not r["active"]]

    out = []
    out.append("# Mod snapshot — the corpus on disk")
    out.append("")
    out.append("Generated by `python tools/corpus.py --write`. **Do not hand-edit.**")
    out.append("")
    out.append("This is the corpus capability research searches, and a **version pin**:")
    out.append("a finding cited against a mod is cited against the version recorded here.")
    out.append("Run `python tools/corpus.py --check` to see what has moved since.")
    out.append("")
    out.append("`Act` — in `config/ModsConfig.xml`. **An inactive mod is invisible to")
    out.append("`defdb.py`, `patch_check.py`, `audit_research.py` and `inventory.py`,**")
    out.append("and the active split carries no weight for research (`PARTS-BIN.md`).")
    out.append("`1.6` — loads under 1.6, by About.xml, a version folder or loadFolders.")
    out.append("`Src` — **the game version the shipped C# source is for**, never a bare")
    out.append("yes. A version that is not %s is marked **⚠ stale**: that source does" % VERSION)
    out.append("not describe the assembly the game loads, so decompile the %s dll instead" % VERSION)
    out.append("(`ilspycmd`). VFE Empire ships 176 .cs under `1.4/Source/` and a distinct")
    out.append("dll for each of 1.4/1.5/1.6 — reading its source is reading 1.4.")
    out.append("`Dll` — the version folders shipping an assembly.")
    out.append("")
    total = len(mods)
    n_active = sum(1 for m in mods.values() if m["active"])
    n_16 = sum(1 for m in mods.values() if m["supports"])
    n_stale = sum(1 for m in mods.values() if m["stale_source"])
    out.append("**%d mods on disk. %d active, %d inactive. %d load under %s.**"
               % (total, n_active, total - n_active, n_16, VERSION))
    out.append("")
    out.append("**%d ship C# source that is not for %s — decompile, do not read.**"
               % (n_stale, VERSION))
    out.append("")
    out.append("| Mod | packageId | Act | 1.6 | Src | Dll | Origin | Updated |")
    out.append("| --- | --- | :-: | :-: | :-: | :-: | --- | --- |")
    tick = lambda b: "yes" if b else "—"

    def code(versions, stale=False):
        if not versions:
            return "—"
        label = ", ".join(v for v in versions)
        return ("%s ⚠" % label) if stale else label

    for m in rows:
        out.append("| %s | `%s` | %s | %s | %s | %s | %s | %s |" % (
            m["name"].replace("|", "\\|"), m["packageId"], tick(m["active"]),
            tick(m["supports"]), code(m["source"], m["stale_source"]),
            code(m["dll"]), m["origin"], m["mtime"]))
    out.append("")
    return "\n".join(out)


def parse_snapshot():
    """packageId -> updated date, from the committed snapshot."""
    if not os.path.isfile(SNAPSHOT):
        return None
    pins = {}
    with open(SNAPSHOT, encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("| ") or "`" not in line:
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 8:
                continue
            pins[cells[1].strip("`")] = cells[7]
    return pins


def check(mods):
    pins = parse_snapshot()
    if pins is None:
        print("No snapshot at %s. Run --write to take one." % SNAPSHOT)
        return 1
    added, moved, gone = [], [], []
    for pid, m in mods.items():
        if pid not in pins:
            added.append((pid, m))
        elif pins[pid] != m["mtime"]:
            moved.append((pid, m, pins[pid]))
    for pid in pins:
        if pid not in mods:
            gone.append(pid)

    if not (added or moved or gone):
        print("Corpus matches the snapshot. %d mods." % len(mods))
        return 0
    if moved:
        print("UPDATED since the pin — findings citing these may be stale:")
        for pid, m, was in moved:
            print("  %-45s %s -> %s" % (pid, was, m["mtime"]))
    if added:
        print("\nNEW since the pin — never surveyed:")
        for pid, m in added:
            print("  %-45s %s" % (pid, m["name"]))
    if gone:
        print("\nGONE since the pin — findings citing these have no source:")
        for pid in gone:
            print("  %s" % pid)
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true",
                    help="rewrite docs/data/MOD-SNAPSHOT.md")
    ap.add_argument("--check", action="store_true",
                    help="diff the disk against the committed snapshot")
    ap.add_argument("--which", metavar="PATH", nargs="*",
                    help="which mod owns these paths, and are they active. "
                         "Pass '-' (or no argument) to read paths from stdin, so a "
                         "wide pass can be attributed in one call: "
                         "rg -a -l Foo <roots> | python tools/corpus.py --which -")
    ap.add_argument("--inactive", action="store_true",
                    help="only mods the other tools cannot see")
    args = ap.parse_args()

    mods = scan()

    if args.which is not None:
        paths = [p for p in args.which if p != "-"]
        if not paths or any(p == "-" for p in args.which):
            paths += [ln for ln in (l.strip() for l in sys.stdin) if ln]
        if not paths:
            print("Nothing to attribute. Pass paths, or pipe them with --which -")
            return 1
        if len(paths) > 1:
            return which_many(paths, mods)
        mod = which(paths[0], mods)
        if not mod:
            print("No mod owns that path.")
            return 1
        print("%s  (`%s`)" % (mod["name"], mod["packageId"]))
        print("  active:   %s" % ("yes" if mod["active"]
                                  else "NO — invisible to defdb/patch_check/inventory"))
        print("  loads %s: %s" % (VERSION, "yes" if mod["supports"] else "no"))
        if not mod["source"]:
            print("  source:   none — decompile: ilspycmd <dll>")
        elif mod["stale_source"]:
            print("  source:   %s only — STALE, does not describe the %s assembly."
                  % (", ".join(mod["source"]), VERSION))
            print("            decompile instead: ilspycmd <dll>")
        else:
            print("  source:   %s" % ", ".join(mod["source"]))
        print("  dll:      %s" % (", ".join(mod["dll"]) or "none"))
        print("  updated:  %s" % mod["mtime"])
        print("  path:     %s" % mod["path"])
        return 0

    if args.check:
        return check(mods)

    text = render(mods, inactive_only=args.inactive)
    if args.write:
        os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)
        with open(SNAPSHOT, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("Wrote %s (%d mods)." % (SNAPSHOT, len(mods)))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
