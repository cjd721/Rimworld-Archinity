"""
Cross-reference checker for Archinity defs.

RimWorld reports unresolved def references at startup, but only after a full
load, and the errors scroll past in a wall of unrelated logspam. This catches
typos and wrong-mod assumptions before the game ever sees them.

It scans the active mod set (Core + DLCs + every subscribed workshop mod's
current-version folders) for <defName> declarations, then checks that a given
list of names actually resolves.

Run:  python tools/check_refs.py
"""

import os
import re
import sys

DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
WORKSHOP = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFNAME = re.compile(r"<defName>\s*([A-Za-z0-9_.]+)\s*</defName>")
# Folders for older game versions that are present but never loaded.
STALE = re.compile(r"[\\/]1\.[0-5][\\/]")


def harvest(root):
    found = set()
    for dp, _, fns in os.walk(root):
        if STALE.search(dp):
            continue
        for fn in fns:
            if not fn.endswith(".xml"):
                continue
            try:
                with open(os.path.join(dp, fn), encoding="utf-8-sig",
                          errors="ignore") as fh:
                    found.update(DEFNAME.findall(fh.read()))
            except OSError:
                pass
    return found


def main():
    known = set()
    for root in (DATA, WORKSHOP, REPO):
        known |= harvest(root)
    print("known defNames in scope: %d\n" % len(known))

    # Every cross-mod name Archinity relies on. Grouped so a failure tells you
    # which assumption broke, not just that something is missing.
    checks = {
        "xenotypes":   ["Starjack", "Genie", "Hussar", "Baseliner"],
        "cultures":    ["Astropolitan"],
        "memes":       ["Shipborn", "Structure_Animist", "Nudism", "Blindsight",
                        "AnimalPersonhood", "TreeConnection", "Tunneler",
                        "Rancher", "Darkness", "Supremacist", "Loyalist",
                        "Structure_Ideological", "Structure_Archist",
                        "Structure_TheistAbstract", "Structure_TheistEmbodied"],
        "traders":     ["Orbital_BulkGoods", "Orbital_CombatSupplier",
                        "Orbital_Exotic"],
        "apparel":     ["Apparel_VacsuitHelmet", "Apparel_VacsuitChildren",
                        "Apparel_ShieldBelt", "Apparel_PowerArmor",
                        "Apparel_PowerArmorHelmet"],
        "loot things": ["Silver", "MedicineIndustrial", "ComponentIndustrial",
                        "ComponentSpacer", "MealSurvivalPack", "Neutroamine",
                        "Plasteel", "HemogenPack", "Pemmican",
                        "MedicineHerbal", "WoodLog"],
        "styles":      ["Techist"],
        "pacing tgts": ["VRE_Archons", "VQEA_InjectionBlacklist",
                        "VRE_Transcendent", "Orbit",
                        "TB_MedievalTheory", "TB_IndustrialTheory"],
        "ours":        ["Archinity_ArchonianSanguophage",
                        "Archinity_SeedOfArchinity",
                        "Archinity_FreeCompanies",
                        "Archinity_FC_Deckhand", "Archinity_FC_Child",
                        "Archinity_FC_Gunner", "Archinity_FC_Corsair",
                        "Archinity_FC_Heavy", "Archinity_FC_Voidwright",
                        "Archinity_FC_FreeCaptain",
                        "Archinity_NamerFactionFreeCompanies",
                        "Archinity_NamerSettlementFreeCompanies",
                        "Archinity_FreeCompaniesRaidLootMaker"],
        "glitterites": ["Archinity_Glitterites", "Archinity_GL_Warden",
                        "Archinity_GL_Lector", "Archinity_GL_Magistrate",
                        "Archinity_GL_Technician",
                        "Archinity_NamerFactionGlitterites",
                        "Archinity_NamerSettlementGlitterites",
                        "Archinity_GlitteritesRaidLootMaker",
                        "USH_AncientGlittertechSoldier",
                        "USH_GlittertechQuestBase", "USH_GlittertechOutpost",
                        "USH_GlittertechFacility", "AncientsHostile",
                        "Mech_Scyther", "Mech_Lancer", "Mech_Pikeman",
                        "Mech_CentipedeBlaster", "Mech_CentipedeGunner",
                        "Mech_CentipedeBurner", "Mech_Militor",
                        "Mech_Legionary", "Mech_Scorcher",
                        "Mech_Centurion",
                        "AM_Daggersnout", "AM_Aura",
                        "AM_Phalanx", "AM_Fireworm", "AM_Goliath",
                        "AM_Siegebreaker", "AM_Demolisher", "Highmate",
                        "MedicineUltratech", "DeathAcidifier", "Uranium",
                        "Apparel_PowerArmor", "Apparel_PowerArmorHelmet"],
    }

    missing_total = 0
    for group, names in checks.items():
        missing = [n for n in names if n not in known]
        missing_total += len(missing)
        status = "MISSING: " + ", ".join(missing) if missing else "ok"
        print("  %-12s %s" % (group, status))

    print()
    if missing_total:
        print("%d unresolved reference(s). Fix before loading." % missing_total)
        return 1
    print("all references resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
