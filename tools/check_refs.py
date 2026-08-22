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


def check_wellformed():
    """Parse every XML file we ship.

    RimWorld does not report a def file that fails to parse. It drops the whole
    file and carries on, so the defs simply never exist and the damage surfaces
    somewhere else entirely as unresolved references - or as nothing at all.

    The classic cause is a double hyphen inside an XML comment, which is
    illegal, and which separator rules like <!-- ===== --> produce by accident
    the moment they are drawn with hyphens.

    Returns the number of broken files.
    """
    import xml.etree.ElementTree as ET

    broken = 0
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__",
                                                        "obj", "bin")]
        for fn in filenames:
            if not fn.endswith(".xml"):
                continue
            path = os.path.join(dirpath, fn)
            try:
                ET.parse(path)
            except ET.ParseError as exc:
                print("  BROKEN  %s" % os.path.relpath(path, REPO))
                print("          %s" % exc)
                print("          (a double hyphen inside an XML comment "
                      "is the usual cause)")
                broken += 1
    return broken


def main():
    print("parsing shipped XML ...")
    broken = check_wellformed()
    if broken:
        print("\n%d file(s) would be silently dropped by RimWorld. "
              "Fix before loading." % broken)
        return 1
    print("  all files parse\n")

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
        # Everything Archinity.Altar reaches into another mod for. The twelve
        # facilities matter most: a typo there silently produces an altar that
        # nothing can link to, with no error anywhere.
        "altar":       ["Archinity_Altar", "Archinity_ArchitePool",
                        "Archinity_RiteShock", "Archinity_ArchiteSustenance",
                        "Archinity_LoadAltar", "MinifiedThing",
                        "Deathless", "Ageless", "Deathrest",
                        "XenogermReimplanter",
                        "VQEA_PlasteelSkin", "VQEA_PerfectVision",
                        "VQEA_Electromagnetized",
                        "VQEA_NeurostabilizerArray", "VQEA_CognitiveRecoveryArray",
                        "VQEA_RapidInfusionPump", "VQEA_ArchiteRecycler",
                        "VQEA_GenomicAttenuator", "VQEA_RejectionBufferCoil",
                        "VQEA_SpliceframeUplink", "VQEA_MutagenInhibitorCore",
                        "VQEA_TraitSelectionPrism", "VQEA_AberrationRedirector",
                        "VQEA_ComplexityHarmonizer", "VQEA_ArchitePathingArray"],
        "ascension":   ["USH_Glitterheart", "USH_GlittershipChunk",
                        "Archinity_GlittershipDebris", "ChunkSlagSteel",
                        "USH_RewardGlittercrate", "Opportunity_AbandonedPlatform",
                        "Opportunity_OrbitalWreck", "OrbitalScanner",
                        "Reward_GravshipUpgrade",
                        "USH_GlittertechFabrication", "USH_LightGlitterpanelsRes",
                        "USH_DarkGlitterpanelsRes", "USH_GlittertechUtilitiesRes",
                        "USH_TelepadRes", "USH_MolecularDisassemblerRes",
                        "USH_HeavyGlittertechRes", "USH_GlittertechAlchemyRes",
                        "USH_NeuromodifiersBasicsRes", "USH_DeepMindScanningRes",
                        "USH_TeethRes", "USH_OverclockRes", "USH_SkinRes",
                        "USH_CombatSkilltrainersRes", "USH_EngineeringSkilltrainersRes",
                        "USH_IntellectualSkilltrainersRes", "USH_SurvivalSkilltrainersRes",
                        "USH_ResurrectorRes", "USH_ResearchProbe",
                        "USH_Glitterheart", "USH_Glittercore"],
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
