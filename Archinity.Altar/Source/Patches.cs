using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace Archinity
{
    [StaticConstructorOnStartup]
    public static class ArchinityMod
    {
        static ArchinityMod()
        {
            new Harmony("archinity.altar").PatchAll(Assembly.GetExecutingAssembly());
            NeutraliseArchonEquipmentGate();
            WarnAboutGenesMissingFromPool();
        }

        /// <summary>
        /// VRE-Archon blocks its archoblade and archoplate behind a hardcoded
        /// check for VRE_Transcendent - which in this campaign is the very last
        /// thing you ever get, so the gear would arrive with nothing left to
        /// fight. Their block list is a public static HashSet, so emptying it
        /// disables their gate cleanly and ours (see CanEquipPatch) takes over.
        ///
        /// Reflection rather than an assembly reference: this must not become a
        /// hard dependency, and it must not throw if they rename anything.
        /// </summary>
        private static void NeutraliseArchonEquipmentGate()
        {
            try
            {
                Type gate = GenTypes.GetTypeInAnyAssembly(
                    "VREArchon.VREArchon_EquipmentUtility_CanEquip_Postfix");
                FieldInfo field = gate?.GetField(
                    "blockedWeapons", BindingFlags.Public | BindingFlags.Static);
                if (field?.GetValue(null) is HashSet<ThingDef> blocked)
                {
                    ArchonGatedEquipment.AddRange(blocked);
                    blocked.Clear();
                }
            }
            catch (Exception e)
            {
                Log.Warning("[Archinity] Could not rebind the archon equipment "
                            + "gate; VRE-Archon's own restriction stays in force. "
                            + e.Message);
            }
        }

        /// <summary>
        /// A newly-added mod can introduce archite genes at any time, and one
        /// missing from the pool would silently never appear in the lottery.
        /// Better a startup warning than a gene nobody ever sees.
        /// </summary>
        private static void WarnAboutGenesMissingFromPool()
        {
            GenePoolDef pool = ArchinityDefOf.Archinity_ArchitePool;
            if (pool == null)
            {
                return;
            }
            List<string> missing = new List<string>();
            foreach (GeneDef g in pool.MissingArchiteGenes())
            {
                missing.Add(g.defName);
            }
            if (missing.Count > 0)
            {
                Log.Warning("[Archinity] " + missing.Count + " archite gene(s) are not "
                    + "in Archinity_ArchitePool and will never be offered: "
                    + string.Join(", ", missing)
                    + ". Re-run tools/survey_archite.py and add them.");
            }
        }

        /// <summary>Equipment we took over gating for.</summary>
        public static readonly List<ThingDef> ArchonGatedEquipment = new List<ThingDef>();
    }

    /// <summary>
    /// Our replacement for VRE-Archon's equipment gate. Same two items, earlier
    /// key - whichever gene the pool nominates rather than Transcendent.
    /// </summary>
    [HarmonyPatch(typeof(EquipmentUtility), nameof(EquipmentUtility.CanEquip),
        new[] { typeof(Thing), typeof(Pawn), typeof(string), typeof(bool) },
        new[] { ArgumentType.Normal, ArgumentType.Normal, ArgumentType.Out, ArgumentType.Normal })]
    public static class CanEquipPatch
    {
        [HarmonyPriority(Priority.Last)]
        public static void Postfix(ref bool __result, Thing thing, Pawn pawn,
                                   ref string cantReason)
        {
            if (!__result || thing == null || pawn == null)
            {
                return;
            }
            if (!ArchinityMod.ArchonGatedEquipment.Contains(thing.def))
            {
                return;
            }
            GeneDef key = ArchinityDefOf.Archinity_ArchitePool?.archonEquipmentGene;
            if (key == null)
            {
                return;
            }
            if (pawn.genes == null || !pawn.genes.HasActiveGene(key))
            {
                __result = false;
                cantReason = "Archinity_NeedsArchonAttunement".Translate(key.LabelCap);
            }
        }
    }

    /// <summary>
    /// The founders can make others like themselves - but not equal to
    /// themselves.
    ///
    /// ReimplantXenogerm calls SetXenotype first, which copies the whole
    /// XenotypeDef gene list onto the recipient, so there is no way to make a
    /// gene "not transfer" purely through endogene/xenogene placement. Stripping
    /// afterwards is the honest fix, and it buys the line the campaign wants:
    /// I can make you like me, I cannot make you deathless.
    /// </summary>
    [HarmonyPatch(typeof(GeneUtility), nameof(GeneUtility.ReimplantXenogerm))]
    public static class ReimplantXenogermPatch
    {
        public static void Postfix(Pawn caster, Pawn recipient)
        {
            GenePoolDef pool = ArchinityDefOf.Archinity_ArchitePool;
            if (pool == null || recipient?.genes == null)
            {
                return;
            }

            foreach (GeneDef gene in pool.founderOnlyGenes)
            {
                if (gene == null)
                {
                    continue;
                }
                Gene held = recipient.genes.GetGene(gene);
                if (held != null)
                {
                    recipient.genes.RemoveGene(held);
                }
            }

            foreach (GeneDef gene in pool.conversionAddsGenes)
            {
                if (gene != null && !recipient.genes.HasActiveGene(gene))
                {
                    recipient.genes.AddGene(gene, xenogene: true);
                }
            }
        }
    }
}
