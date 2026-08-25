"""
Audit every research project against More Realistic Research's behaviour.

MRR (sae.researchmod) attaches "analysis" prerequisites to research projects.
Projects it does not list get requirements AUTO-GENERATED from their tech level,
and the generator picks study subjects from the things the project UNLOCKS.

That is the failure mode this script exists to find. For Industrial/Spacer the
generator demands you reverse-engineer the very thing the research unlocks; for
Ultra it demands you study it (Theoretical). If that thing cannot be obtained
without first completing the research, the project is permanently unresearchable
and the game says nothing.

Verified against decompiled ModResearchRimworld.dll (see docs/technical-findings):

    BuildAutoAnalysis(project):
        techLevel <= Neolithic          -> no analysis at all
        techprints or analyzed-things   -> no analysis (left to vanilla)
        no unlocked ThingDefs           -> no analysis
        Medieval                        -> Experimental on costList(unlocked[0])
        Industrial / Spacer             -> ReverseEngineering on ALL unlocked
                                           + Experimental on costList(unlocked[-1])
        Ultra                           -> Theoretical on ALL unlocked
                                           + Experimental on costList(unlocked[-1])

    points required = (int)techLevel - 3 / -2 / -1  for RE / Exp / Theo

Two further facts that shape the verdicts:

  * Reverse-engineering and Theoretical NEVER consume the item. Experimental
    consumes exactly one item per point.
  * Points are pooled PER TYPE, not per material. If a project's Experimental
    pool is {Steel, Plasteel, Glitterheart}, every point can be paid in steel.
    Auto-generation therefore cannot enforce a specific material.

Run:  python tools/audit_research.py
      python tools/audit_research.py --all     (list every project, not just risks)
"""

import os
import re
import sys
from collections import defaultdict

try:
    from lxml import etree
except ImportError:
    sys.exit("needs lxml:  pip install lxml")

DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
WORKSHOP = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODSCONFIG = os.path.join(REPO, "config", "ModsConfig.xml")
BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "audit_research_baseline.txt")

STALE = re.compile(r"[\\/]1\.[0-5][\\/]")

TECH = {"Undefined": 0, "Animal": 1, "Neolithic": 2, "Medieval": 3,
        "Industrial": 4, "Spacer": 5, "Ultra": 6, "Archotech": 7}
TECHNAME = {v: k for k, v in TECH.items()}

# MRR: points required for an auto-generated project, by analysis type.
RE_PTS = lambda t: t - 3
EXP_PTS = lambda t: t - 2
THEO_PTS = lambda t: t - 1


# --------------------------------------------------------------------------
# Work out which mod folders are actually loaded.
# --------------------------------------------------------------------------

def active_roots():
    """DLC dirs plus the workshop folder for every enabled packageId."""
    roots = [os.path.join(DATA, d) for d in
             ("Core", "Royalty", "Ideology", "Biotech", "Odyssey")
             if os.path.isdir(os.path.join(DATA, d))]

    want = set()
    if os.path.isfile(MODSCONFIG):
        tree = etree.parse(MODSCONFIG)
        for li in tree.xpath("//activeMods/li"):
            want.add((li.text or "").strip().lower())

    if os.path.isdir(WORKSHOP):
        for folder in os.listdir(WORKSHOP):
            about = os.path.join(WORKSHOP, folder, "About", "About.xml")
            if not os.path.isfile(about):
                continue
            try:
                pid = etree.parse(about).findtext("packageId") or ""
            except Exception:
                continue
            if pid.strip().lower() in want:
                roots.append(os.path.join(WORKSHOP, folder))

    roots.append(REPO)
    return roots


def load_trees(roots):
    trees = []
    for root in roots:
        for dirpath, _, files in os.walk(root):
            if STALE.search(dirpath) or f"{os.sep}.git{os.sep}" in dirpath:
                continue
            for fn in files:
                if not fn.endswith(".xml"):
                    continue
                path = os.path.join(dirpath, fn)
                try:
                    trees.append((path, etree.parse(path)))
                except Exception:
                    pass
    return trees


# --------------------------------------------------------------------------
# Def inheritance. techLevel on the glittertech projects lives on an abstract
# parent, so anything that reads the element directly gets it wrong.
# --------------------------------------------------------------------------

def build_defs(trees, tag):
    """Return {defName: resolved_element_dict} with ParentName inheritance applied."""
    by_name = {}     # Name= attribute -> node (abstract or not)
    concrete = []
    for path, tree in trees:
        for node in tree.xpath("//" + tag):
            nm = node.get("Name")
            if nm:
                by_name[nm] = node
            if node.get("Abstract", "").lower() != "true":
                concrete.append((path, node))

    def chain(node, seen=None):
        seen = seen or set()
        parent = node.get("ParentName")
        if parent and parent in by_name and parent not in seen:
            seen.add(parent)
            return chain(by_name[parent], seen) + [node]
        return [node]

    out = {}
    for path, node in concrete:
        merged = {}
        for link in chain(node):
            for child in link:
                if isinstance(child.tag, str):
                    merged[child.tag] = child
        dn = merged.get("defName")
        if dn is not None and dn.text:
            out[dn.text.strip()] = (merged, path)
    return out


# --------------------------------------------------------------------------

def load_merged():
    """The def database as RimWorld will actually build it.

    Reading raw def files audits content that will not exist in game. Our own
    patches delete every AM_* research project, for one, so auditing them for
    deadlocks reports risks in content the player can never reach - and any
    retier we ship is invisible, so tier totals lag reality.

    Returned in the (path, tree) shape the rest of this file expects, as a
    single merged tree. `//` xpaths behave identically against it.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import defdb
    root, report, _ = defdb.build(apply_our_patches=True,
                                  apply_thirdparty_patches=True)
    return [("<merged def database>", root)], report


def main():
    show_all = "--all" in sys.argv
    raw = "--raw" in sys.argv

    if raw:
        roots = active_roots()
        print("--raw: scanning %d active mod/DLC roots, no patches applied"
              % len(roots))
        trees = load_trees(roots)
        print("parsed %d xml files\n" % len(trees))
    else:
        print("building merged def database (patches applied) ...")
        trees, report = load_merged()
        print("  %d def files merged, %d patch operations applied"
              % (report.def_files, report.patch_ops_applied))
        notes = report.render()
        if notes:
            print("merge fidelity:")
            print(notes)
        print()

    projects = build_defs(trees, "ResearchProjectDef")
    things = build_defs(trees, "ThingDef")
    print("research projects: %d      thingdefs: %d" % (len(projects), len(things)))

    # ---- what MRR already hand-authors (its own file + ours) ----------------
    # The tag is "ResearchMakesSense.ManualAnalysisDef". The dot is part of the
    # tag name, not an XML namespace, so local-name() returns the whole string
    # and an equality test on "ManualAnalysisDef" silently matches nothing.
    listed = {}
    for path, tree in trees:
        for node in tree.iter():
            if not isinstance(node.tag, str):
                continue
            if node.tag.rsplit(".", 1)[-1] != "ManualAnalysisDef":
                continue
            proj = node.findtext("researchProject")
            if proj:
                listed[proj.strip()] = os.path.basename(path)

    # ---- UnlockedDefs, mirroring ResearchProjectDef.UnlockedDefs -----------
    unlocked = defaultdict(list)
    for name, (fields, _) in things.items():
        for li in fields.get("researchPrerequisites", []):
            if li.text:
                unlocked[li.text.strip()].append(name)
    for path, tree in trees:
        for rec in tree.xpath("//RecipeDef"):
            prereqs = [x.text.strip() for x in rec.xpath("researchPrerequisites/li") if x.text]
            single = rec.findtext("researchPrerequisite")
            if single:
                prereqs.append(single.strip())
            if not prereqs:
                continue
            for prod in rec.xpath("products/*"):
                if isinstance(prod.tag, str):
                    for p in prereqs:
                        unlocked[p].append(prod.tag)
        # recipeMaker on a ThingDef gates that thing behind a project
        for td in tree.xpath("//ThingDef"):
            dn = td.findtext("defName")
            rp = td.findtext("recipeMaker/researchPrerequisite")
            if dn and rp:
                unlocked[rp.strip()].append(dn.strip())
    for k in unlocked:
        unlocked[k] = sorted(set(unlocked[k]))

    # ---- obtainability index ----------------------------------------------
    # A thing you cannot build (because the research gates it) must be FOUND.
    # Collect every defName that appears in a place the world can hand you one.
    findable = set()
    for path, tree in trees:
        # KCSG / vanilla structure layout rows are comma-joined cell strings
        for li in tree.xpath("//li[contains(text(),',')]"):
            txt = li.text or ""
            if len(txt) > 8:
                for cell in txt.split(","):
                    cell = cell.strip()
                    if cell and cell != ".":
                        findable.add(re.sub(r"_(North|South|East|West)$", "", cell))
        # prefabs, thing set makers, trader stock, scatterers
        for xp in ("//PrefabDef/things/*", "//thingDefs/li", "//thingDef",
                   "//scatterThings/li", "//things/li", "//fixedThings/li"):
            for n in tree.xpath(xp):
                val = n.tag if xp.endswith("things/*") else (n.text or "").strip()
                if isinstance(val, str) and val and val != "li":
                    findable.add(val)
    # Traders. A building you cannot build can still be BOUGHT, either because
    # a stock generator names it outright or because its tradeTags /
    # thingCategories match one a trader stocks.
    # Deliberately tradeTag-only. Matching on thingCategories instead lets a
    # bulk-goods trader "stock" an Ultra-tech fabricator because they share the
    # BuildingsProduction category, which hid real deadlocks on the first pass.
    stock_tags = set()
    for path, tree in trees:
        for n in tree.xpath("//TraderKindDef//tradeTag"):
            if n.text:
                stock_tags.add(n.text.strip())
        for n in tree.xpath("//TraderKindDef//thingDef"):
            if n.text:
                findable.add(n.text.strip())

    for name, (fields, _) in things.items():
        # explicit reward-pool membership reaches the player through quests
        if "thingSetMakerTags" in fields:
            findable.add(name)
        tr = fields.get("tradeability")
        if tr is not None and (tr.text or "").strip() in ("None", "Sellable"):
            continue  # traders will never hand you one
        tags = {li.text.strip() for li in fields.get("tradeTags", []) if li.text}
        if tags & stock_tags:
            findable.add(name)

    # ---- classify every project -------------------------------------------
    rows = []
    for name, (fields, path) in sorted(projects.items()):
        tl_txt = (fields.get("techLevel").text.strip()
                  if fields.get("techLevel") is not None and fields["techLevel"].text
                  else "Undefined")
        tl = TECH.get(tl_txt, 0)
        unl = unlocked.get(name, [])

        if name in listed:
            rows.append((name, tl_txt, "HAND-AUTHORED", listed[name], []))
            continue
        if tl <= 2:
            rows.append((name, tl_txt, "no analysis", "tech level too low", []))
            continue
        if fields.get("techprints") is not None or fields.get("requiredAnalyzed") is not None:
            rows.append((name, tl_txt, "no analysis", "techprint/analyzed gated", []))
            continue
        if not unl:
            rows.append((name, tl_txt, "no analysis", "unlocks no ThingDef", []))
            continue

        # auto-generated. Which things must be STUDIED (not consumed)?
        if tl == 3:
            subjects, kind = [], "Experimental only"
        elif tl in (4, 5):
            subjects, kind = unl, "ReverseEngineering"
        else:
            subjects, kind = unl, "Theoretical"

        # Points pool PER TYPE, not per material: studying any one of the
        # unlocked things feeds the same counter. So the project is only
        # dead if EVERY candidate subject is unobtainable.
        blocked = [s for s in subjects if s not in findable]
        if len(blocked) < len(subjects):
            blocked = []
        rows.append((name, tl_txt, "AUTO: " + kind,
                     "%d pts" % (RE_PTS(tl) if tl in (4, 5) else THEO_PTS(tl)),
                     blocked))

    # ---- report ------------------------------------------------------------
    deadlocks = [r for r in rows if r[4]]

    # Accepted pre-existing deadlocks. These live in third-party research we
    # have not decided about yet, and they are not caused by any diff. A gate
    # that is permanently red gets ignored, which costs more than it catches -
    # so the baseline holds the known set and the gate fails only on NEW ones.
    # Shrink it deliberately as the research pass settles; never grow it to
    # silence something a change introduced.
    known = set()
    if os.path.isfile(BASELINE):
        with open(BASELINE, encoding="utf-8") as fh:
            known = {ln.split("#")[0].strip() for ln in fh
                     if ln.split("#")[0].strip()}

    if "--update-baseline" in sys.argv:
        with open(BASELINE, "w", encoding="utf-8") as fh:
            fh.write("# Accepted research deadlock risks. See audit_research.py.\n")
            fh.write("# Regenerate deliberately: python tools/audit_research.py "
                     "--update-baseline\n")
            for name, tl, kind, _n, _b in sorted(deadlocks):
                fh.write("%-42s # [%s] %s\n" % (name, tl, kind))
        print("\nbaseline updated: %d accepted deadlock(s) written to %s"
              % (len(deadlocks), os.path.relpath(BASELINE, REPO)))
        return 0

    fresh = [r for r in deadlocks if r[0] not in known]
    stale = sorted(known - {r[0] for r in deadlocks})
    print("\n" + "=" * 78)
    print("DEADLOCK RISKS  -  auto-generated projects whose study subject")
    print("                   never appears in any layout, prefab, loot table,")
    print("                   trader stock or reward pool")
    print("=" * 78)
    if not deadlocks:
        print("  none")
    for name, tl, kind, note, blocked in deadlocks:
        print("\n  %s  [%s]  %s (%s)" % (name, tl, kind, note))
        for b in blocked:
            print("        unobtainable study subject: %s" % b)

    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    buckets = defaultdict(int)
    for r in rows:
        buckets[r[2].split(":")[0]] += 1
    for k in sorted(buckets):
        print("  %-16s %d" % (k, buckets[k]))
    print("  %-16s %d" % ("DEADLOCK RISK", len(deadlocks)))
    print("  %-16s %d accepted, %d new"
          % ("  vs baseline", len(deadlocks) - len(fresh), len(fresh)))
    if stale:
        print("\n  %d baseline entr(y/ies) no longer deadlocked - remove from %s:"
              % (len(stale), os.path.relpath(BASELINE, REPO)))
        for s in stale:
            print("      %s" % s)
    if fresh:
        print("\n  NEW deadlock risk(s), not in the baseline:")
        for name, tl, kind, _n, _b in fresh:
            print("      %s  [%s]  %s" % (name, tl, kind))

    if "--tiers" in sys.argv:
        # TechBlock sets each TechLock's baseCost to a fraction of the
        # PREVIOUS tier's total. The setting names are offset by one tier:
        #   TB_SpacerTechLock  <- requiredPointsIndustrial x Industrial total
        #   TB_UltraTechLock   <- requiredPointsSpacer     x Spacer total
        #   TB_ArchoTechLock   <- requiredPointsUltra      x Ultra total
        # Editing the setting that sounds right will move the wrong gate.
        order = ["Neolithic", "Medieval", "Industrial", "Spacer", "Ultra", "Archotech"]
        per = defaultdict(list)
        for name, (fields, _) in projects.items():
            if name.startswith("TB_"):
                continue          # TechBlock's IsBlockTech() excludes these
            tl = fields.get("techLevel")
            v = tl.text.strip() if tl is not None and tl.text else "Undefined"
            bc = fields.get("baseCost")
            cost = float(bc.text) if bc is not None and bc.text else 0.0
            per[v].append((cost, name))
        print("\n" + "=" * 78)
        print("RESEARCH BY TIER  (baseCost; TechBlock sums these per tier)")
        print("=" * 78)
        totals = {}
        for tier in order:
            rows2 = sorted(per.get(tier, []), reverse=True)
            tot = sum(c for c, _ in rows2)
            totals[tier] = tot
            if not rows2:
                continue
            print("\n%s  -  %d projects, %s points total"
                  % (tier.upper(), len(rows2), format(int(tot), ",")))
            for cost, name in rows2:
                print("     %8s  %s" % (format(int(cost), ","), name))
        print("\n" + "=" * 78)
        print("TECHBLOCK GATE COSTS  (cost = fraction x PREVIOUS tier total,")
        print("                       reduced by in-tier research already done)")
        print("=" * 78)
        pairs = [("TB_MedievalTechLock", "Neolithic", "requiredPointsNeolithic"),
                 ("TB_IndustrialTechLock", "Medieval", "requiredPointsMedieval"),
                 ("TB_SpacerTechLock", "Industrial", "requiredPointsIndustrial"),
                 ("TB_UltraTechLock", "Spacer", "requiredPointsSpacer"),
                 ("TB_ArchoTechLock", "Ultra", "requiredPointsUltra")]
        print("  %-24s %-12s %-26s %10s %10s %10s"
              % ("gate", "sums tier", "setting to edit", "@0.75", "@0.65", "@0.60"))
        for gate, tier, setting in pairs:
            t = totals.get(tier, 0)
            print("  %-24s %-12s %-26s %10s %10s %10s"
                  % (gate, tier, setting,
                     format(int(t * .75), ","), format(int(t * .65), ","),
                     format(int(t * .60), ",")))

    if show_all:
        print("\n" + "=" * 78)
        print("ALL PROJECTS")
        print("=" * 78)
        for name, tl, kind, note, blocked in rows:
            flag = "  <-- RISK" if blocked else ""
            print("  %-40s %-10s %-24s %s%s" % (name, tl, kind, note, flag))

    return 1 if fresh else 0


if __name__ == "__main__":
    sys.exit(main())
