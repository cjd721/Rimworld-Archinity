"""
Inventory every item and research project in the ACTIVE mod set.

Reads the live ModsConfig.xml (not the stale repo snapshot), maps each
packageId to its folder on disk, then walks the current-version def folders of
each mod in load order.

Emits two CSVs plus a per-mod summary:
  inventory-research.csv  defName, label, mod, techLevel, baseCost, tab, prereqs
  inventory-things.csv    defName, label, mod, kind, techLevel, category

Fields are resolved through the `ParentName` chain, because RimWorld defs
inherit and most mods put `techLevel` on an Abstract parent. Reading the raw
node reports Royalty's implant projects and all of Ushanka's Glittertech as
having no tech level at all, which is wrong and would misread how TechBlock
gates them.

"kind" is our own bucket, derived from the def's resolved fields, so that a
4,000-row dump can be sliced without reading all of it.

Run:  python tools/inventory.py [--out DIR]
"""

import csv
import os
import re
import sys

try:
    from lxml import etree
except ImportError:
    sys.exit("needs lxml:  pip install lxml")

DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
WORKSHOP = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
LOCAL_MODS = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods"
LIVE_CONFIG = os.path.expandvars(
    r"%LOCALAPPDATA%\..\LocalLow\Ludeon Studios"
    r"\RimWorld by Ludeon Studios\Config\ModsConfig.xml")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Folders for older game versions that are present but never loaded.
STALE = re.compile(r"[\\/]1\.[0-5][\\/]")

RESEARCH_TAGS = {"ResearchProjectDef",
                 "VFETribals.TribalResearchProjectDef",
                 "TribalResearchProjectDef"}


def parse(path):
    try:
        return etree.parse(path, etree.XMLParser(recover=True))
    except (etree.XMLSyntaxError, OSError):
        return None


def active_mods():
    tree = parse(LIVE_CONFIG)
    if tree is None:
        sys.exit("cannot read live ModsConfig at " + LIVE_CONFIG)
    return [li.text.strip().lower()
            for li in tree.findall(".//activeMods/li") if li.text]


def index_folders():
    """packageId -> (folder, display name)."""
    idx = {}
    for root in (DATA, LOCAL_MODS, WORKSHOP, REPO):
        if not os.path.isdir(root):
            continue
        for entry in sorted(os.listdir(root)):
            folder = os.path.join(root, entry)
            about = os.path.join(folder, "About", "About.xml")
            if not os.path.isfile(about):
                continue
            tree = parse(about)
            if tree is None:
                continue
            # Direct children only. Several Vanilla Expanded About.xml files
            # put <modDependencies> before <packageId>, so a .// search picks
            # up the dependency's packageId (brrainz.harmony) instead.
            pid = tree.findtext("./packageId")
            name = tree.findtext("./name") or entry
            if pid:
                idx.setdefault(pid.strip().lower(), (folder, name.strip()))
    return idx


def load_folders(folder, active):
    """The content roots this mod contributes, honouring LoadFolders.xml.

    Medieval Overhaul ships ~25 conditional folders under 1.6/Mods/<Other>,
    loaded only when that other mod is active. Walking 1.6/Defs alone misses
    every compatibility def it adds for Royalty, Biotech, Odyssey, VCE and
    VFE Medieval 2 - all of which are active here.
    """
    lf = os.path.join(folder, "LoadFolders.xml")
    if not os.path.isfile(lf):
        return [folder, os.path.join(folder, "1.6")]

    tree = parse(lf)
    if tree is None:
        return [folder, os.path.join(folder, "1.6")]

    node = tree.find(".//v1.6")
    if node is None:
        return [folder, os.path.join(folder, "1.6")]

    def listed(attr, li):
        raw = li.get(attr)
        if not raw:
            return None
        return [p.strip().lower() for p in raw.split(",") if p.strip()]

    out = []
    for li in node.findall("./li"):
        need = listed("IfModActive", li)
        if need and not any(p in active for p in need):
            continue
        block = listed("IfModNotActive", li)
        if block and any(p in active for p in block):
            continue
        rel = (li.text or "").strip().strip("/")
        out.append(os.path.join(folder, rel) if rel else folder)
    return out or [folder]


def def_files(folder, active):
    """Every def XML the game would actually load for this mod."""
    out = []
    for base in load_folders(folder, active):
        for sub in ("Defs", "Patches"):
            root = os.path.join(base, sub)
            if not os.path.isdir(root):
                continue
            for dp, _, fns in os.walk(root):
                if STALE.search(dp):
                    continue
                out.extend(os.path.join(dp, fn)
                           for fn in fns if fn.endswith(".xml"))
    return sorted(set(out))


class Registry:
    """Resolves def fields through the ParentName chain.

    Abstract def names are global across the whole merged database, not scoped
    to the mod that declared them, so one dict in load order is correct.
    """

    def __init__(self):
        self.by_name = {}
        self._trees = []      # keep trees alive; lxml nodes are views

    def note(self, tree):
        self._trees.append(tree)
        root = tree.getroot()
        if root is None or root.tag == "Patch":
            return
        for node in root.iter():
            if isinstance(node.tag, str) and node.get("Name"):
                self.by_name[node.get("Name")] = node

    def chain(self, node, limit=12):
        seen, out = set(), [node]
        cur = node
        while len(out) < limit:
            parent = cur.get("ParentName")
            if not parent or parent in seen:
                break
            seen.add(parent)
            cur = self.by_name.get(parent)
            if cur is None:
                break
            out.append(cur)
        return out

    def text(self, node, tag, default=""):
        for n in self.chain(node):
            v = n.findtext("./" + tag)
            if v and v.strip():
                return v.strip()
        return default

    def find(self, node, path):
        for n in self.chain(node):
            hit = n.find(path)
            if hit is not None:
                return hit
        return None

    def list(self, node, path):
        for n in self.chain(node):
            items = n.findall(path)
            if items:
                return [(li.text or "").strip() for li in items]
        return []


def classify(reg, node):
    """Our own coarse bucket for a ThingDef."""
    cls = (node.get("Class") or "").strip()
    if cls and cls != "ThingDef":
        return "class:" + cls.split(".")[-1]

    cats = reg.list(node, "./thingCategories/li")
    catblob = " ".join(cats).lower()

    if reg.find(node, "./plant") is not None:
        return "plant"
    if reg.find(node, "./race") is not None:
        return "pawn"
    if reg.find(node, "./apparel") is not None:
        return "apparel"
    if reg.find(node, "./verbs/li/verbClass") is not None or "weapon" in catblob:
        return "weapon"
    if reg.find(node, "./building") is not None:
        return "building"
    if reg.find(node, "./ingestible") is not None:
        return "food/drug"
    if "bodyparts" in catblob or "prosthe" in catblob:
        return "bodypart"
    if reg.find(node, "./projectile") is not None:
        return "projectile"
    if cats:
        return "item"

    parent = node.get("ParentName") or ""
    if "mote" in parent.lower():
        return "mote"
    if parent:
        return "parent:" + parent
    return "other"


def main():
    out_dir = REPO
    if "--out" in sys.argv:
        out_dir = sys.argv[sys.argv.index("--out") + 1]
    os.makedirs(out_dir, exist_ok=True)

    mods = active_mods()
    idx = index_folders()
    missing = [m for m in mods if m not in idx]

    # Pass 1: load every file once, registering abstracts in load order.
    reg = Registry()
    loaded = []      # (order, pid, name, tree)
    for order, pid in enumerate(mods):
        if pid not in idx:
            continue
        folder, name = idx[pid]
        for path in def_files(folder, set(mods)):
            tree = parse(path)
            if tree is None:
                continue
            reg.note(tree)
            loaded.append((order, pid, name, folder, path, tree))

    # Pass 2: harvest concrete defs with inheritance resolved.
    #
    # A few mods ship the same def in both <root>/Defs and <root>/1.6/Defs.
    # The game loads one; we would otherwise count both, which doubled
    # TechBlock's 11 projects to 22.
    research, things, summary = [], [], {}
    seen = set()
    for order, pid, name, folder, path, tree in loaded:
        root = tree.getroot()
        if root is None or root.tag == "Patch":
            continue
        slot = summary.setdefault((order, pid, name), [0, {}])
        for node in root.iter():
            if not isinstance(node.tag, str):
                continue
            dn = node.findtext("./defName")
            if not dn:
                continue
            dn = dn.strip()
            if (pid, node.tag, dn) in seen:
                continue
            seen.add((pid, node.tag, dn))
            rel = os.path.relpath(path, folder)
            if node.tag in RESEARCH_TAGS:
                slot[0] += 1
                research.append({
                    "order": order, "mod": name, "packageId": pid,
                    "defName": dn,
                    "label": reg.text(node, "label"),
                    "techLevel": reg.text(node, "techLevel", "(none)"),
                    "baseCost": reg.text(node, "baseCost", "0"),
                    "tab": reg.text(node, "tab", "Main"),
                    "techprints": reg.text(node, "techprintCount", "0"),
                    "bench": reg.text(node, "requiredResearchBuilding"),
                    "facilities": ";".join(
                        reg.list(node, "./requiredResearchFacilities/li")),
                    "prerequisites": ";".join(
                        reg.list(node, "./prerequisites/li")),
                    "file": rel,
                })
            elif node.tag == "ThingDef":
                kind = classify(reg, node)
                slot[1][kind] = slot[1].get(kind, 0) + 1
                things.append({
                    "order": order, "mod": name, "packageId": pid,
                    "defName": dn,
                    "label": reg.text(node, "label"),
                    "kind": kind,
                    "techLevel": reg.text(node, "techLevel", "(none)"),
                    "parent": node.get("ParentName") or "",
                    "categories": ";".join(
                        reg.list(node, "./thingCategories/li")),
                    "research": ";".join(filter(None, [
                        reg.text(node, "recipeMaker/researchPrerequisite"),
                        ";".join(reg.list(node, "./researchPrerequisites/li")),
                    ])),
                    "marketValue": reg.text(
                        node, "statBases/MarketValue", ""),
                    "file": rel,
                })

    def dump(rows, fname, fields):
        p = os.path.join(out_dir, fname)
        with open(p, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        return p

    p1 = dump(research, "inventory-research.csv",
              ["order", "mod", "packageId", "defName", "label", "techLevel",
               "baseCost", "techprints", "tab", "bench", "facilities",
               "prerequisites", "file"])
    p2 = dump(things, "inventory-things.csv",
              ["order", "mod", "packageId", "defName", "label", "kind",
               "techLevel", "marketValue", "parent", "categories", "research",
               "file"])

    print("active mods: %d   resolved: %d   MISSING FOLDER: %s"
          % (len(mods), len(mods) - len(missing), missing or "none"))
    print("research projects: %d    thingdefs: %d"
          % (len(research), len(things)))
    print()
    print("%-4s %-44s %6s %7s  %s"
          % ("#", "mod", "resch", "things", "top kinds"))
    print("-" * 120)
    for (order, pid, name), (rc, tc) in sorted(summary.items()):
        total = sum(tc.values())
        if rc == 0 and total == 0:
            continue
        top = ", ".join("%s:%d" % (k, v) for k, v in
                        sorted(tc.items(), key=lambda x: -x[1])[:5])
        print("%-4d %-44s %6d %7d  %s" % (order, name[:44], rc, total, top))
    print()
    print("wrote", p1)
    print("wrote", p2)


if __name__ == "__main__":
    main()
