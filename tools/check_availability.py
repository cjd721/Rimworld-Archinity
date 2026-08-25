"""
Score how obtainable a thing actually is, before we gate research behind it.

More Realistic Research turns research into a scavenger hunt: a project cannot
be started until you possess (reverse-engineering / theoretical) or consume
(experimental) specific items. That is the mechanic we want - it converts
research time into expedition time. It is also the mechanic that can brick a
playthrough, quietly, if the item we picked has no reliable source in this
particular load order.

This tool answers one question per candidate material:

    "How many INDEPENDENT ways can the player get one of these?"

Six routes are checked. A material that scores on only one route is a
single point of failure; two is acceptable; three or more is safe.

    CRAFT     a recipe produces it, gated on nothing or on a
              Neolithic/Medieval project (so it is reachable in-era)
    RAIDER    carried by a PawnKindDef that hostile factions field.
              THE BEST ROUTE for a medieval run: raids arrive on their own
              schedule, so this can never dry up, and "study the sword you
              took off a dead marauder" is exactly the intended fiction.
    TRADE     a stock generator names it, or its tradeTags / thingCategories
              match one a trader stocks, and tradeability permits buying
    QUEST     has thingSetMakerTags, so reward makers can roll it
    LOOT      named in some ThingSetMakerDef (raid loot, settlement loot,
              site loot, ancient containers)
    MAPGEN    placed by a structure layout, PrefabDef or scatterer
    HARVEST   a plant's harvest product, or an animal butcher/milk/egg product

Run:
    python tools/check_availability.py                 # score the planned list
    python tools/check_availability.py Steel Cloth ... # score specific defs
    python tools/check_availability.py --plan          # validate the leap plan
"""

import os
import re
import sys
from collections import defaultdict

try:
    from lxml import etree
except ImportError:
    sys.exit("needs lxml:  pip install lxml")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_research as A  # reuse active-mod discovery and inheritance resolution

EARLY_TIERS = {"Neolithic", "Medieval", "Undefined", ""}

# The materials the Medieval leap plan intends to require. Every one of these
# must score >= 2 routes, and the RAIDER route is preferred for flavour items.
PLAN = {
    "Leap 1": ["Leather_Plain", "Cloth", "WoodLog", "Steel",
               "MeleeWeapon_Club", "Bow_Short"],
    "Leap 2": ["Steel", "Silver", "MeleeWeapon_LongSword", "Bow_Great",
               "Apparel_FlakVest", "Jade"],
    "Leap 3": ["Steel", "Gold", "Apparel_PlateArmor", "Apparel_Duster",
               "MeleeWeapon_Gladius", "Bow_Recurve", "Chemfuel"],
}


def build(trees):
    things = A.build_defs(trees, "ThingDef")
    routes = defaultdict(set)
    notes = defaultdict(list)

    # ---- CRAFT ------------------------------------------------------------
    projects = A.build_defs(trees, "ResearchProjectDef")

    def proj_tier(name):
        f = projects.get(name, ({}, ""))[0]
        e = f.get("techLevel")
        return e.text.strip() if e is not None and e.text else "Undefined"

    for _, tree in trees:
        for rec in tree.xpath("//RecipeDef"):
            pre = [x.text.strip() for x in rec.xpath("researchPrerequisites/li") if x.text]
            single = rec.findtext("researchPrerequisite")
            if single:
                pre.append(single.strip())
            early = all(proj_tier(p) in EARLY_TIERS for p in pre)
            for prod in rec.xpath("products/*"):
                if isinstance(prod.tag, str):
                    if early:
                        routes[prod.tag].add("CRAFT")
                    else:
                        notes[prod.tag].append("craftable but gated on " + ",".join(pre))
        for td in tree.xpath("//ThingDef"):
            dn = td.findtext("defName")
            rp = td.findtext("recipeMaker/researchPrerequisite")
            if dn and (rp is None or proj_tier(rp.strip() if rp else "") in EARLY_TIERS):
                if td.find("recipeMaker") is not None:
                    routes[dn].add("CRAFT")

    # ---- RAIDER -----------------------------------------------------------
    # A thing is raider-carried if a PawnKindDef names it directly, or if it
    # carries a weaponTag / apparelTag that some pawnkind requests.
    wanted_wtags, wanted_atags = set(), set()
    for _, tree in trees:
        for pk in tree.xpath("//PawnKindDef"):
            for x in pk.xpath("weaponTags/li"):
                if x.text:
                    wanted_wtags.add(x.text.strip())
            for x in pk.xpath("apparelTags/li"):
                if x.text:
                    wanted_atags.add(x.text.strip())
            for xp in ("apparelRequired/li", "weaponMoney/li", "techHediffsTags/li"):
                for x in pk.xpath(xp):
                    if x.text:
                        routes[x.text.strip()].add("RAIDER")
    for name, (fields, _) in things.items():
        wt = {x.text.strip() for x in fields.get("weaponTags", []) if x.text}
        at = {x.text.strip() for x in fields.get("apparelTags", []) if x.text}
        if wt & wanted_wtags or at & wanted_atags:
            routes[name].add("RAIDER")

    # ---- TRADE ------------------------------------------------------------
    stock_tags, stock_cats = set(), set()
    for _, tree in trees:
        for n in tree.xpath("//TraderKindDef//tradeTag"):
            if n.text:
                stock_tags.add(n.text.strip())
        for n in tree.xpath("//TraderKindDef//categoryDef"):
            if n.text:
                stock_cats.add(n.text.strip())
        for n in tree.xpath("//TraderKindDef//thingDef"):
            if n.text:
                routes[n.text.strip()].add("TRADE")
    # ThingCategoryDefs form a tree, and StockGenerator_Category stocks a
    # category AND every category beneath it. Comparing names by equality
    # therefore misses the common case: nothing stocks "Leathers", but plenty
    # stocks "Textiles", and Leathers -> Textiles -> Manufactured -> Root.
    # Without walking that chain, ordinary leather scores as a single point of
    # failure, which is how this check first failed.
    cat_parent = {}
    for name, (fields, _) in A.build_defs(trees, "ThingCategoryDef").items():
        p = fields.get("parent")
        if p is not None and p.text:
            cat_parent[name] = p.text.strip()

    def with_ancestors(cats):
        out = set()
        for c in cats:
            seen = c
            while seen and seen not in out:
                out.add(seen)
                seen = cat_parent.get(seen)
        return out

    for name, (fields, _) in things.items():
        tr = fields.get("tradeability")
        if tr is not None and (tr.text or "").strip() in ("None", "Sellable"):
            continue
        tags = {x.text.strip() for x in fields.get("tradeTags", []) if x.text}
        cats = {x.text.strip() for x in fields.get("thingCategories", []) if x.text}
        if tags & stock_tags or with_ancestors(cats) & stock_cats:
            routes[name].add("TRADE")

    # ---- QUEST / LOOT / MAPGEN / HARVEST ----------------------------------
    for name, (fields, _) in things.items():
        if "thingSetMakerTags" in fields:
            routes[name].add("QUEST")
    for _, tree in trees:
        for n in tree.xpath("//ThingSetMakerDef//thingDefs/li"):
            if n.text:
                routes[n.text.strip()].add("LOOT")
        for n in tree.xpath("//PrefabDef/things/*"):
            if isinstance(n.tag, str):
                routes[n.tag].add("MAPGEN")
        for n in tree.xpath("//li[contains(text(),',')]"):
            txt = n.text or ""
            if len(txt) > 8 and "," in txt:
                for cell in txt.split(","):
                    cell = cell.strip()
                    if cell and cell != ".":
                        routes[re.sub(r"_(North|South|East|West)$", "", cell)].add("MAPGEN")
        for n in tree.xpath("//scatterThings/li") + tree.xpath("//thingDef"):
            if n.text:
                routes[n.text.strip()].add("MAPGEN")
    for name, (fields, _) in things.items():
        h = fields.get("plant")
        if h is not None and h.find("harvestedThingDef") is not None:
            t = h.findtext("harvestedThingDef")
            if t:
                routes[t.strip()].add("HARVEST")
        # Animal products. leatherDef / milkDef / egg defs live under <race>,
        # not at the top level, which is why a naive top-level lookup reports
        # Leather_Plain as unobtainable despite every hunt producing it.
        race = fields.get("race")
        if race is not None:
            for tag in ("leatherDef", "milkDef", "eggUnfertilizedDef",
                        "eggFertilizedDef", "meatDef"):
                v = race.findtext(tag)
                if v:
                    routes[v.strip()].add("HARVEST")
            for li in race.xpath("butcherProducts/*"):
                if isinstance(li.tag, str):
                    routes[li.tag].add("HARVEST")
        for li in fields.get("butcherProducts", []) if fields.get("butcherProducts") is not None else []:
            if isinstance(li.tag, str):
                routes[li.tag].add("HARVEST")

    return routes, notes, things


def main():
    trees = A.load_trees(A.active_roots())
    routes, notes, things = build(trees)

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        groups = {"requested": args}
    else:
        groups = PLAN

    print("\nroutes: CRAFT RAIDER TRADE QUEST LOOT MAPGEN HARVEST")
    print("verdict: 1 route = SINGLE POINT OF FAILURE, 2 = ok, 3+ = safe\n")
    worst = 0
    for group, mats in groups.items():
        print("=" * 76)
        print(group)
        print("=" * 76)
        for m in mats:
            r = sorted(routes.get(m, set()))
            exists = m in things
            if not exists:
                print("  %-34s  *** NO SUCH THINGDEF ***" % m)
                worst = max(worst, 3)
                continue
            if len(r) == 0:
                verdict = "UNOBTAINABLE"
                worst = max(worst, 3)
            elif len(r) == 1:
                verdict = "SINGLE POINT OF FAILURE"
                worst = max(worst, 2)
            elif len(r) == 2:
                verdict = "ok"
                worst = max(worst, 1)
            else:
                verdict = "safe"
            print("  %-34s %-38s %s" % (m, " ".join(r), verdict))
            for n in notes.get(m, [])[:1]:
                print("  %-34s   note: %s" % ("", n))
        print()
    return 1 if worst >= 2 else 0


if __name__ == "__main__":
    sys.exit(main())
