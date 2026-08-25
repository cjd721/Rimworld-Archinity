"""
Merged def database for Archinity tooling.

The other checkers read raw def files. That is fine for asking "does this
defName exist", but it cannot answer the question a PatchOperation actually
raises: *what does my xpath match in the database RimWorld will really build?*

RimWorld builds that database by concatenating every active mod's def files
into one <Defs> root in load order, then running every PatchOperation against
that single merged tree. This module reproduces those two steps well enough to
count nodes, which is all our verification needs.

What it does faithfully:
  - load order from config/ModsConfig.xml
  - LoadFolders.xml, including IfModActive / IfModNotActive
  - the default folder rule when a mod ships no LoadFolders.xml
  - the vanilla PatchOperation classes we and most mods use

What it does NOT do, and must not be trusted for:
  - ParentName inheritance. Patches run before it resolves, so for patch
    checking this is correct; for anything else the tree is pre-inheritance.
  - PatchOperation classes implemented in C# by other mods. Every one of these
    is COUNTED AND REPORTED, never silently skipped. Read the skip report
    before trusting a result.

Not run directly. See patch_check.py and xpath.py.
"""

import os
import re
import sys

try:
    from lxml import etree
except ImportError:
    sys.exit("lxml is required:  pip install lxml")

VERSION = "1.6"

DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
WORKSHOP = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
LOCAL = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Our own mod folders, so a caller can hold them back and measure against the
# rest of the world before applying them.
OURS = ("Archinity.Altar", "Archinity.Drifters", "Archinity.Glitterites",
        "Archinity.Origins", "Archinity.Pacing")

PARSER = etree.XMLParser(remove_blank_text=False, recover=False,
                         resolve_entities=False)


class Report:
    """Everything the merge could not do faithfully, so callers can say so."""

    def __init__(self):
        self.unparseable = []       # (path, error)
        self.skipped_ops = {}       # class name -> count
        self.missing_mods = []      # packageIds in ModsConfig with no folder
        self.def_files = 0
        self.patch_ops_applied = 0
        # packageIds AND display names of active mods, both lowercased, so
        # FindMod resolves the same way here as it does during the build.
        self.active_ids = set()

    def skip(self, cls):
        self.skipped_ops[cls] = self.skipped_ops.get(cls, 0) + 1

    def trustworthy(self):
        return not self.unparseable and not self.skipped_ops

    def render(self, indent="  "):
        out = []
        if self.missing_mods:
            out.append("%sactive mods with no folder found: %s"
                       % (indent, ", ".join(self.missing_mods)))
        if self.unparseable:
            out.append("%s%d file(s) failed to parse and were skipped:"
                       % (indent, len(self.unparseable)))
            for path, err in self.unparseable[:5]:
                out.append("%s  %s  (%s)" % (indent, path, err))
            if len(self.unparseable) > 5:
                out.append("%s  ... and %d more"
                           % (indent, len(self.unparseable) - 5))
        if self.skipped_ops:
            total = sum(self.skipped_ops.values())
            out.append("%s%d patch operation(s) of unimplemented classes were "
                       "NOT applied:" % (indent, total))
            for cls, n in sorted(self.skipped_ops.items(),
                                 key=lambda kv: -kv[1]):
                out.append("%s  %-52s %d" % (indent, cls, n))
            out.append("%sthe merged tree is approximate to that degree."
                       % indent)
        return "\n".join(out)


# ---------------------------------------------------------------- mod index

def load_order():
    """Active packageIds, lowercased, in load order."""
    path = os.path.join(REPO, "config", "ModsConfig.xml")
    tree = etree.parse(path, PARSER)
    return [li.text.strip().lower()
            for li in tree.findall(".//activeMods/li") if li.text]


def _package_id(mod_root):
    """The mod's own packageId.

    Must be a DIRECT child of <ModMetaData>. A descendant search picks up the
    packageIds inside <modDependencies> instead, which silently indexes a mod
    under one of its dependencies' names and leaves the real mod unfindable.
    """
    about = os.path.join(mod_root, "About", "About.xml")
    if not os.path.isfile(about):
        return None
    try:
        tree = etree.parse(about, PARSER)
    except etree.XMLSyntaxError:
        return None
    node = tree.getroot().find("packageId")
    return node.text.strip().lower() if node is not None and node.text else None


def index_mods():
    """packageId -> mod folder, across Data, the workshop and local Mods."""
    index = {}
    for base in (DATA, WORKSHOP, LOCAL):
        if not os.path.isdir(base):
            continue
        for name in os.listdir(base):
            root = os.path.join(base, name)
            if not os.path.isdir(root):
                continue
            pid = _package_id(root)
            if pid and pid not in index:
                index[pid] = root
    # The repo copy wins over any installed copy of our own mods, so the
    # checks measure what is committed rather than what was last exported.
    for name in OURS:
        root = os.path.join(REPO, name)
        pid = _package_id(root)
        if pid:
            index[pid] = root
    return index


def content_dirs(mod_root, active_ids):
    """The folders RimWorld will actually read from this mod, in order.

    LoadFolders.xml wins when present. Otherwise the convention every mod in
    the load order follows: the mod root, plus a folder named for the game
    version if one exists.
    """
    lf = None
    for name in ("LoadFolders.xml", "loadFolders.xml"):
        candidate = os.path.join(mod_root, name)
        if os.path.isfile(candidate):
            lf = candidate
            break

    if lf is None:
        dirs = [mod_root]
        versioned = os.path.join(mod_root, VERSION)
        if os.path.isdir(versioned):
            dirs.append(versioned)
        return dirs

    try:
        tree = etree.parse(lf, PARSER)
    except etree.XMLSyntaxError:
        return [mod_root]

    block = tree.find("v%s" % VERSION)
    if block is None:
        return [mod_root]

    dirs = []
    for li in block.findall("li"):
        need = (li.get("IfModActive") or "").strip().lower()
        deny = (li.get("IfModNotActive") or "").strip().lower()
        if need and need not in active_ids:
            continue
        if deny and deny in active_ids:
            continue
        rel = (li.text or "").strip()
        path = mod_root if rel in ("", "/") else os.path.join(mod_root, rel)
        if os.path.isdir(path):
            dirs.append(path)
    return dirs or [mod_root]


def _xml_files(folder, subdir):
    root = os.path.join(folder, subdir)
    if not os.path.isdir(root):
        return
    for dirpath, dirnames, filenames in sorted(os.walk(root)):
        dirnames.sort()
        for fn in sorted(filenames):
            if fn.lower().endswith(".xml"):
                yield os.path.join(dirpath, fn)


# ------------------------------------------------------------ patch engine

def _elements(parent):
    """Child elements only.

    A bare `for child in parent` also yields XML comments, which have no Class
    attribute and would be miscounted as unimplemented operations - and, worse,
    shift the index of every real operation after them.
    """
    if parent is None:
        return []
    return [c for c in parent if isinstance(c, etree._Element)
            and not isinstance(c, (etree._Comment, etree._ProcessingInstruction))]


def _detach(node):
    parent = node.getparent()
    if parent is not None:
        parent.remove(node)


def _value_children(op):
    value = op.find("value")
    return list(value) if value is not None else []


def _apply_leaf(root, op, report):
    """Apply one operation. Returns the number of nodes its xpath matched."""
    cls = (op.get("Class") or "").strip()
    xpath_node = op.find("xpath")
    if xpath_node is None or not (xpath_node.text or "").strip():
        report.skip(cls or "<no Class>")
        return 0

    try:
        targets = root.xpath(xpath_node.text.strip())
    except etree.XPathEvalError:
        report.skip("%s <bad xpath>" % cls)
        return 0

    if not isinstance(targets, list):
        return 0

    if cls == "PatchOperationReplace":
        for t in targets:
            parent = t.getparent()
            if parent is None:
                continue
            idx = parent.index(t)
            parent.remove(t)
            for i, child in enumerate(_value_children(op)):
                import copy
                parent.insert(idx + i, copy.deepcopy(child))
    elif cls == "PatchOperationRemove":
        for t in targets:
            _detach(t)
    elif cls == "PatchOperationAdd":
        order = (op.findtext("order") or "Append").strip()
        import copy
        for t in targets:
            children = [copy.deepcopy(c) for c in _value_children(op)]
            if order == "Prepend":
                for i, child in enumerate(children):
                    t.insert(i, child)
            else:
                t.extend(children)
    elif cls == "PatchOperationInsert":
        order = (op.findtext("order") or "Prepend").strip()
        import copy
        for t in targets:
            parent = t.getparent()
            if parent is None:
                continue
            idx = parent.index(t) + (1 if order == "Append" else 0)
            for i, child in enumerate(_value_children(op)):
                parent.insert(idx + i, copy.deepcopy(child))
    elif cls == "PatchOperationAttributeSet" or cls == "PatchOperationAttributeAdd":
        name = (op.findtext("attribute") or "").strip()
        val = (op.findtext("value") or "").strip()
        for t in targets:
            if name and (cls == "PatchOperationAttributeSet"
                         or t.get(name) is None):
                t.set(name, val)
    elif cls == "PatchOperationAttributeRemove":
        name = (op.findtext("attribute") or "").strip()
        for t in targets:
            if name:
                t.attrib.pop(name, None)
    elif cls == "PatchOperationAddModExtension":
        import copy
        for t in targets:
            ext = t.find("modExtensions")
            if ext is None:
                ext = etree.SubElement(t, "modExtensions")
            ext.extend(copy.deepcopy(c) for c in _value_children(op))
    elif cls == "PatchOperationTest":
        pass  # match count is the whole point; nothing to mutate
    else:
        report.skip(cls)
        return len(targets)

    report.patch_ops_applied += 1
    return len(targets)


def apply_operation(root, op, report, active_ids):
    """Apply an operation, walking Sequence / FindMod / Conditional wrappers."""
    cls = (op.get("Class") or "").strip()

    if cls == "PatchOperationSequence":
        for child in _elements(op.find("operations")):
            apply_operation(root, child, report, active_ids)
        return

    # For FindMod and Conditional, <match> and <nomatch> ARE operations -
    # they carry their own Class attribute. Iterating their children walks
    # <xpath> and <value> instead, which silently does nothing at all.
    if cls == "PatchOperationFindMod":
        names = [(li.text or "").strip().lower()
                 for li in _elements(op.find("mods"))]
        # FindMod matches on mod *name* or packageId depending on the mod
        # author; we accept either, since active_ids carries both.
        hit = any(n in active_ids for n in names)
        branch = op.find("match") if hit else op.find("nomatch")
        if branch is not None:
            apply_operation(root, branch, report, active_ids)
        return

    if cls == "PatchOperationConditional":
        xpath_node = op.find("xpath")
        hit = False
        if xpath_node is not None and (xpath_node.text or "").strip():
            try:
                hit = bool(root.xpath(xpath_node.text.strip()))
            except etree.XPathEvalError:
                report.skip("PatchOperationConditional <bad xpath>")
                return
        branch = op.find("match") if hit else op.find("nomatch")
        if branch is not None:
            apply_operation(root, branch, report, active_ids)
        return

    _apply_leaf(root, op, report)


def iter_operations(patch_root, active_ids=None, root=None):
    """Yield (label, element) for every leaf operation, flattening wrappers.

    Pass active_ids and root to resolve FindMod and Conditional, so only the
    branch that will actually run is yielded. Without them both branches are
    walked, which enumerates more than the game will ever execute - fine for
    listing, wrong for anything that then applies what it yielded.
    """
    def branches(node, cls, short, trail):
        if cls == "PatchOperationFindMod" and active_ids is not None:
            names = [(li.text or "").strip().lower()
                     for li in _elements(node.find("mods"))]
            taken = "match" if any(n in active_ids for n in names) else "nomatch"
        elif cls == "PatchOperationConditional" and root is not None:
            xp = node.findtext("xpath")
            hit = False
            if xp and xp.strip():
                try:
                    hit = bool(root.xpath(xp.strip()))
                except etree.XPathEvalError:
                    hit = False
            taken = "match" if hit else "nomatch"
        else:
            taken = None

        for name in ("match", "nomatch"):
            if taken is not None and name != taken:
                continue
            branch = node.find(name)
            if branch is not None:
                yield from walk(branch, trail + ["%s.%s" % (short, name)])

    def walk(node, trail):
        cls = (node.get("Class") or "").strip()
        short = cls.replace("PatchOperation", "") or "?"
        if cls == "PatchOperationSequence":
            for i, child in enumerate(_elements(node.find("operations"))):
                yield from walk(child, trail + ["Sequence[%d]" % i])
            return
        if cls in ("PatchOperationFindMod", "PatchOperationConditional"):
            # <match>/<nomatch> are operations themselves, not containers.
            yield from branches(node, cls, short, trail)
            return
        yield (" > ".join(trail + [short]) if trail else short), node

    ops = [e for e in _elements(patch_root) if e.tag == "Operation"]
    for i, op in enumerate(ops):
        yield from walk(op, ["Operation[%d]" % i])


# ------------------------------------------------------------------- build

def build(apply_our_patches=False, apply_thirdparty_patches=True,
          verbose=False):
    """Return (defs_root, report, our_patch_files).

    Every active mod's defs are merged, ours included - RimWorld loads all
    defs before it runs any patch, so our own defs are part of the world a
    patch measures itself against. Excluding them makes every patch that
    targets something we ship report zero matches, which is a false alarm.

    What is held back is our *patches*. apply_our_patches=False leaves the
    tree in the state our patches are about to act on, which is the baseline
    a match count means anything against.
    """
    report = Report()
    order = load_order()
    index = index_mods()

    active_ids = set(order)
    # FindMod is often written against the display name, not the packageId.
    for pid, root_dir in index.items():
        if pid in active_ids:
            about = os.path.join(root_dir, "About", "About.xml")
            try:
                name = etree.parse(about, PARSER).findtext(".//name")
                if name:
                    active_ids.add(name.strip().lower())
            except (OSError, etree.XMLSyntaxError):
                pass

    report.active_ids = active_ids
    ours_roots = {os.path.join(REPO, n) for n in OURS}
    defs_root = etree.Element("Defs")
    patch_files = []
    our_patch_files = []

    for pid in order:
        mod_root = index.get(pid)
        if mod_root is None:
            report.missing_mods.append(pid)
            continue
        is_ours = mod_root in ours_roots

        for folder in content_dirs(mod_root, active_ids):
            for path in _xml_files(folder, "Defs"):
                try:
                    tree = etree.parse(path, PARSER)
                except etree.XMLSyntaxError as exc:
                    report.unparseable.append(
                        (os.path.relpath(path, os.path.dirname(mod_root)),
                         str(exc).split("(")[0].strip()))
                    continue
                report.def_files += 1
                for child in tree.getroot():
                    defs_root.append(child)
            found = _xml_files(folder, "Patches")
            if is_ours:
                our_patch_files.extend(found)
            else:
                patch_files.extend(found)

    if apply_our_patches:
        patch_files.extend(our_patch_files)

    if verbose:
        print("  merged %d def files from %d mods"
              % (report.def_files, len(order) - len(report.missing_mods)))

    if apply_thirdparty_patches:
        for path in patch_files:
            try:
                patch_tree = etree.parse(path, PARSER)
            except etree.XMLSyntaxError:
                continue
            for op in patch_tree.getroot().findall("Operation"):
                apply_operation(defs_root, op, report, active_ids)
        if verbose:
            print("  applied %d third-party patch operations"
                  % report.patch_ops_applied)

    return defs_root, report, our_patch_files
