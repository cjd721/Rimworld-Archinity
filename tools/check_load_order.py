"""
Validate config/ModsConfig.xml against the load-order rules the mods declare.

This implements RimWorld's OWN algorithm, not a guess at it. Decompiled from
Verse.ModsConfig.TrySortMods (1.6.4871):

    foreach mod i:
        foreach before in i.LoadBefore + i.ForceLoadBefore:
            if that mod is active: AddEdge(indexOf(before), i)
        foreach after in i.LoadAfter + i.ForceLoadAfter:
            if that mod is active: AddEdge(i, indexOf(after))
    if graph.FindCycle() != -1: refuse
    else: Reorder(graph.TopologicalSort())

AddEdge(x, y) encodes "y must come before x". So the constraints are:

    i declares loadBefore m   ->  i must precede m
    i declares loadAfter  m   ->  m must precede i

Two details that matter and are easy to get wrong:

  * modDependencies is NOT part of the sort. RimWorld checks dependencies are
    present, and separately checks order only through the four fields above.
    A mod can hard-depend on another and declare no ordering at all.

  * loadAfterByVersion / loadBeforeByVersion REPLACE the plain lists for the
    running version. ModMetaData.Init does:
        list3 = loadAfterByVersion?.GetItemForVersion(currentVersionWithoutBuild)
        if (list3 != null) loadAfter = list3;
    so a mod with a 1.6-specific block does not also apply its generic one.

Matching is on packageId, case-insensitive, ignoring the "_steam" postfix
RimWorld appends to a workshop copy that is shadowed by a local one.

Usage:
    python tools/check_load_order.py            # report violations
    python tools/check_load_order.py --fix      # rewrite into a valid order
"""

import os
import re
import sys
from collections import defaultdict

try:
    from lxml import etree
except ImportError:
    sys.exit("needs lxml:  pip install lxml")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODSCONFIG = os.path.join(REPO, "config", "ModsConfig.xml")
VERSION = "1.6"

ROOTS = [
    r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100",
    r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data",
    r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods",
]

STEAM_POSTFIX = "_steam"


def norm(pid):
    pid = (pid or "").strip().lower()
    return pid[: -len(STEAM_POSTFIX)] if pid.endswith(STEAM_POSTFIX) else pid


def texts(node, tag):
    if node is None:
        return []
    child = node.find(tag)
    if child is None:
        return []
    return [norm(li.text) for li in child.findall("li") if li is not None and li.text]


def by_version(node, tag):
    """<tagByVersion><v1.6><li>..</li></v1.6></tagByVersion>, or None."""
    if node is None:
        return None
    holder = node.find(tag)
    if holder is None:
        return None
    for child in holder:
        if not isinstance(child.tag, str):
            continue
        if child.tag.lstrip("v") == VERSION:
            return [norm(li.text) for li in child.findall("li") if li is not None and li.text]
    return None


def load_metadata():
    """packageId -> {'name':..., 'before':[...], 'after':[...]}"""
    meta = {}
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for d in os.listdir(root):
            about = os.path.join(root, d, "About", "About.xml")
            if not os.path.isfile(about):
                continue
            try:
                tree = etree.parse(about)
            except Exception:
                continue
            r = tree.getroot()
            pid_node = r.find("packageId")
            if pid_node is None or not pid_node.text:
                continue
            pid = norm(pid_node.text)
            if pid in meta:
                continue  # first wins; duplicates are the local/steam pair

            before = by_version(r, "loadBeforeByVersion")
            if before is None:
                before = texts(r, "loadBefore")
            after = by_version(r, "loadAfterByVersion")
            if after is None:
                after = texts(r, "loadAfter")

            name_node = r.find("name")
            meta[pid] = {
                "name": name_node.text.strip() if name_node is not None and name_node.text else pid,
                "before": before + texts(r, "forceLoadBefore"),
                "after": after + texts(r, "forceLoadAfter"),
            }
    return meta


def read_active():
    raw = open(MODSCONFIG, encoding="utf-8-sig").read()
    block = re.search(r"<activeMods>(.*?)</activeMods>", raw, re.S).group(1)
    return [x.strip() for x in re.findall(r"<li>(.*?)</li>", block) if x.strip()], raw


def build_constraints(active, meta):
    """List of (earlier, later, why). Only pairs where BOTH are active."""
    present = {norm(a) for a in active}
    out = []
    for a in active:
        pid = norm(a)
        m = meta.get(pid)
        if not m:
            continue
        for other in m["before"]:
            if other in present and other != pid:
                out.append((pid, other, f"{pid} declares loadBefore {other}"))
        for other in m["after"]:
            if other in present and other != pid:
                out.append((other, pid, f"{pid} declares loadAfter {other}"))
    return out


def main():
    fix = "--fix" in sys.argv
    active, raw = read_active()
    meta = load_metadata()

    print(f"active mods       : {len(active)}")
    unknown = [a for a in active if norm(a) not in meta]
    if unknown:
        print(f"  NOT FOUND ON DISK: {unknown}")

    cons = build_constraints(active, meta)
    print(f"ordering rules    : {len(cons)}  (only pairs where both mods are active)")

    pos = {norm(a): i for i, a in enumerate(active)}
    violations = [(e, l, why) for (e, l, why) in cons if pos[e] > pos[l]]

    if not violations:
        print("\nOK  every declared rule is satisfied by the current order.")
    else:
        print(f"\n{len(violations)} VIOLATION(S):\n")
        for e, l, why in violations:
            print(f"  {why}")
            print(f"      {e:44s} is at #{pos[e]+1}")
            print(f"      {l:44s} is at #{pos[l]+1}   <- must come after")

    if not fix:
        if violations:
            print("\nRe-run with --fix to rewrite config/ModsConfig.xml into a valid order.")
        return 1 if violations else 0

    # ---- Stable topological sort, preserving the hand-authored order --------
    succ = defaultdict(set)
    indeg = defaultdict(int)
    for e, l, _ in cons:
        if l not in succ[e]:
            succ[e].add(l)
            indeg[l] += 1

    order = [norm(a) for a in active]
    rank = {p: i for i, p in enumerate(order)}
    ready = sorted([p for p in order if indeg[p] == 0], key=lambda p: rank[p])
    result = []
    while ready:
        p = ready.pop(0)
        result.append(p)
        for nxt in sorted(succ[p], key=lambda x: rank[x]):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                ready.append(nxt)
        ready.sort(key=lambda x: rank[x])

    if len(result) != len(order):
        stuck = [p for p in order if p not in result]
        print(f"\nCYCLE - cannot sort. Involved: {stuck}")
        return 2

    original_case = {norm(a): a for a in active}
    body = "\n".join(f"    <li>{original_case[p]}</li>" for p in result)
    new = re.sub(r"(<activeMods>).*?(  </activeMods>)",
                 lambda m: m.group(1) + "\n" + body + "\n" + m.group(2),
                 raw, flags=re.S)
    open(MODSCONFIG, "w", encoding="utf-8", newline="").write(new)
    moved = sum(1 for i, p in enumerate(result) if order[i] != p)
    print(f"\nrewrote config/ModsConfig.xml - {moved} position(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
