"""
Scan every loadable mod assembly for the symbols the Multiplayer mod swaps
under multifaction.

`MultiplayerWorldComp.SetFaction` swaps eight objects onto `Current.Game` when
the active player faction changes, and `Faction.OfPlayer` changes with the
pushed context:

    researchManager  outfitDatabase  drugPolicyDatabase  foodRestrictionDatabase
    playSettings     history         storyteller         storyWatcher

A mod breaks if it caches any of those - or `Faction.OfPlayer` - in a static
field or on a long-lived object (GameComponent, WorldComponent, ThingComp,
Harmony patch class). A mod that reads them fresh inside a method every time is
fine.

This is a RECALL tool, not a verdict tool. It reports that a symbol name appears
in an assembly's metadata, which means "referenced", not "cached". Triage of the
hits is a separate, manual, decompile-and-read job; see
docs/data/MULTIFACTION-SYMBOL-SCAN.md.

The hard part is picking the right files. The naive walk is wrong three ways,
and all three inflate the counts:

  * Dead legacy version trees. A mod shipping `1.2/Assemblies` or `v1.2/` or
    `Versions/v1.5/` still has those DLLs on disk; RimWorld 1.6 never loads
    them. Filtering on `/1.2/` alone misses `v1.2/` and `Versions/v1.5/`.
  * Build leftovers. Several mods ship `Source/.../obj/Debug/` next to the
    real assembly.
  * `Assembly-CSharp.dll`. RimFantasy ships a *publicized copy of RimWorld's
    own assembly* under `1.6/Source/.../obj/Debug/PublicizedAssemblies/`. It
    contains every RimWorld type, so it matches every needle.

So instead of walking for DLLs, this resolves the mod's declared load folders
for the target version - `LoadFolders.xml` when present, otherwise RimWorld's
default of the mod root plus a `1.6/` folder - and takes only
`<loadfolder>/Assemblies/*.dll` from those. Conditional `IfModActive` folders
are included, because we cannot know the active mod list from disk and a false
include is safer than a false exclude for a recall tool.

Run:  python tools/multifaction_scan.py [ROOT ...] [--version 1.6] [--csv OUT]

With no ROOT arguments it scans the workshop folder, the RimWorld Mods folder
and this repo.
"""

import argparse
import csv
import os
import re
import sys

WORKSHOP = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
LOCAL_MODS = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_ROOTS = [WORKSHOP, LOCAL_MODS, REPO]

# The eight swapped managers plus the faction pointer. Two metadata strings can
# betray each one:
#
#   G  the property getter - `Find.ResearchManager` emits a memberref named
#      `get_ResearchManager`, `Faction.OfPlayer` emits `get_OfPlayer`.
#   f  the backing field on `Game` (or `FactionManager.ofPlayer`), which mods
#      reach directly as `Current.Game.outfitDatabase`, or by reflection.
#   T  the bare type name, which is what a `[HarmonyPatch(typeof(Storyteller))]`
#      or a typed local leaves behind when the getter is never called.
#
# The `f` and `T` forms collide with any type or private field a mod happens to
# name `history` or `Storyteller`, so the report keeps the three apart: a `G`
# hit is strong evidence the swapped object is being fetched, `f` and `T` are
# weak. `OfPlayer` has no distinct type, so it has no `T`.
#
# Matching is on the NUL-terminated string as it sits in the metadata #Strings
# heap. Substring matching without the terminator is what made a bare
# `Storyteller` needle match every `StorytellerComp` in the bin.
NEEDLES = {
    "OfPlayer": ("get_OfPlayer", "ofPlayer", None),
    "ResearchManager": ("get_ResearchManager", "researchManager",
                        "ResearchManager"),
    "Storyteller": ("get_Storyteller", "storyteller", "Storyteller"),
    "StoryWatcher": ("get_StoryWatcher", "storyWatcher", "StoryWatcher"),
    "PlaySettings": ("get_PlaySettings", "playSettings", "PlaySettings"),
    "History": ("get_History", "history", "History"),
    "OutfitDatabase": ("get_OutfitDatabase", "outfitDatabase",
                       "OutfitDatabase"),
    "DrugPolicyDatabase": ("get_DrugPolicyDatabase", "drugPolicyDatabase",
                           "DrugPolicyDatabase"),
    "FoodRestrictionDatabase": ("get_FoodRestrictionDatabase",
                                "foodRestrictionDatabase",
                                "FoodRestrictionDatabase"),
}

# DLLs that are never mod code: the game's own assembly (publicized copies of
# it match every needle), and vendored redistributables that ship inside a mod's
# Assemblies folder.
SKIP_DLL = re.compile(
    r"^(Assembly-CSharp|UnityEngine|System\.|mscorlib|netstandard|"
    r"Newtonsoft\.Json|Mono\.|Krafs\.)", re.I)

# Directories that are build output or vendored packages, never load targets.
JUNK_DIR = re.compile(r"[\\/](obj|bin|packages|node_modules|\.git)[\\/]", re.I)


def read(path):
    try:
        with open(path, encoding="utf-8-sig", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""


def load_folders(mod_dir, version):
    """Resolve a mod's load folders for `version`, as absolute paths.

    RimWorld's rule, in the order it applies it: if `LoadFolders.xml` declares
    a `<v{version}>` block, that block is the complete and only answer - a mod
    with a LoadFolders.xml that omits the version loads nothing. Otherwise the
    mod root loads, and so does a `{version}` subfolder if one exists.
    """
    lf = None
    for name in os.listdir(mod_dir):
        if name.lower() == "loadfolders.xml":
            lf = os.path.join(mod_dir, name)
            break

    if lf:
        text = read(lf)
        block = re.search(r"<v%s\s*>(.*?)</v%s\s*>" % (re.escape(version),
                                                       re.escape(version)),
                          text, re.S | re.I)
        if not block:
            return []
        out = []
        for rel in re.findall(r"<li\b[^>]*>(.*?)</li>", block.group(1), re.S):
            rel = rel.strip().strip("/\\")
            path = mod_dir if not rel else os.path.join(mod_dir, *rel.split("/"))
            if os.path.isdir(path):
                out.append(path)
        return out

    out = [mod_dir]
    versioned = os.path.join(mod_dir, version)
    if os.path.isdir(versioned):
        out.append(versioned)
    return out


def mod_name(mod_dir):
    about = os.path.join(mod_dir, "About", "About.xml")
    m = re.search(r"<name>(.*?)</name>", read(about), re.S | re.I)
    name = m.group(1).strip() if m else ""
    base = os.path.basename(mod_dir)
    return "%s [%s]" % (name, base) if name else base


def assemblies(mod_dir, version):
    """Every loadable managed assembly of a mod, deduplicated by file name.

    Only `<loadfolder>/Assemblies/*.dll` counts. Two declared load folders can
    both carry an `Assemblies` folder (a base one plus an `IfModActive`
    overlay), so dedupe on the DLL's file name and keep the first.
    """
    found = {}
    for folder in load_folders(mod_dir, version):
        adir = os.path.join(folder, "Assemblies")
        if not os.path.isdir(adir):
            continue
        for fn in sorted(os.listdir(adir)):
            if not fn.lower().endswith(".dll") or SKIP_DLL.match(fn):
                continue
            path = os.path.join(adir, fn)
            if JUNK_DIR.search(path) or not os.path.isfile(path):
                continue
            found.setdefault(fn.lower(), path)
    return sorted(found.values())


def hits(paths):
    """Which needles appear in these assemblies' metadata, as "G", "f", "Gf".

    Managed metadata keeps member, type and field names in a UTF-8 string heap
    as NUL-terminated entries, so a raw byte scan for `name\\0` finds every name
    the assembly declares or references.

    It still over-reports: a name in the heap means the symbol is referenced
    somewhere in the assembly, NOT that it is cached in a static or on a
    long-lived object. Only reading the IL answers that. Treat a hit as "look
    here", never as a verdict.
    """
    blob = b""
    for path in paths:
        try:
            with open(path, "rb") as fh:
                blob += fh.read()
        except OSError:
            pass
    out = {}
    for key, forms in NEEDLES.items():
        mark = ""
        for name, letter in zip(forms, "GfT"):
            if name and (name + "\0").encode("ascii") in blob:
                mark += letter
        out[key] = mark
    return out


def mod_dirs(root):
    if not os.path.isdir(root):
        return []
    out = []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if os.path.isdir(path) and os.path.isdir(os.path.join(path, "About")):
            out.append(path)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("roots", nargs="*", default=None)
    ap.add_argument("--version", default="1.6")
    ap.add_argument("--csv")
    ap.add_argument("--markdown", action="store_true",
                    help="emit the table as Markdown, for pasting into "
                         "docs/data/MULTIFACTION-SYMBOL-SCAN.md")
    args = ap.parse_args()

    roots = args.roots or DEFAULT_ROOTS
    seen = set()
    rows = []
    scanned = 0

    for root in roots:
        for mod in mod_dirs(root):
            real = os.path.realpath(mod)
            if real in seen:
                continue
            seen.add(real)
            paths = assemblies(mod, args.version)
            if not paths:
                continue
            scanned += 1
            row = {"mod": mod_name(mod),
                   "dir": mod,
                   "dlls": len(paths)}
            row.update(hits(paths))
            rows.append(row)

    rows.sort(key=lambda r: r["mod"].lower())
    keys = list(NEEDLES)
    width = max(len(r["mod"]) for r in rows) if rows else 3
    short = {k: (k[:4] if k.endswith("Database") else k) for k in keys}

    if args.markdown:
        print("| mod | " + " | ".join(short[k] for k in keys) + " |")
        print("|---|" + "---|" * len(keys))
        for r in rows:
            if not any(r[k] for k in keys):
                continue
            print("| " + r["mod"] + " | " +
                  " | ".join(r[k] or "" for k in keys) + " |")
        print("\n%d of %d mod folders shipping a loadable %s assembly have at "
              "least one marker." % (sum(1 for r in rows if any(r[k]
                                                                for k in keys)),
                                     scanned, args.version))
        return 0

    header = "mod".ljust(width) + "  " + "  ".join(k[:9].rjust(9) for k in keys)
    print(header)
    print("-" * len(header))
    for r in rows:
        cells = "  ".join((r[k] or ".").rjust(9) for k in keys)
        print(r["mod"].ljust(width) + "  " + cells)
    print("-" * len(header))
    print("any".ljust(width) + "  " +
          "  ".join(str(sum(1 for r in rows if r[k])).rjust(9) for k in keys))
    print("getter".ljust(width) + "  " +
          "  ".join(str(sum(1 for r in rows if "G" in r[k])).rjust(9)
                    for k in keys))
    print("\nG = property getter referenced (strong).  "
          "f = field name present (weak, collides with mod-local fields).")
    print("%d mod folders ship a loadable %s assembly (of %d scanned)"
          % (scanned, args.version, len(seen)))

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, ["mod", "dir", "dlls"] + keys)
            w.writeheader()
            w.writerows(rows)
        print("wrote " + args.csv)

    return 0


if __name__ == "__main__":
    sys.exit(main())
