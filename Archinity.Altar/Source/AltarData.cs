using System.Collections.Generic;
using RimWorld;
using Verse;

namespace Archinity
{
    [DefOf]
    public static class ArchinityDefOf
    {
        public static ThingDef Archinity_Altar;

        /// <summary>The draw table. See Defs/GenePoolDefs/GenePool_Archite.xml.</summary>
        public static GenePoolDef Archinity_ArchitePool;

        /// <summary>Applied to a recipient when the rite goes badly wrong.</summary>
        public static HediffDef Archinity_RiteShock;

        /// <summary>
        /// Cancels the hunger cost of implanted genes. The Archons feed you -
        /// gaining power at the altar is never paid for in metabolism, because
        /// the price is already denominated in other people.
        /// </summary>
        public static HediffDef Archinity_ArchiteSustenance;

        /// <summary>
        /// Read for its workType alone, so the fuel menu can ask exactly the
        /// question WorkGiver_CarryToBuilding will ask before it agrees to
        /// carry. Reading the def beats hardcoding "Warden" twice.
        /// </summary>
        public static WorkGiverDef Archinity_CarryToAltarWorkGiver;

        static ArchinityDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(ArchinityDefOf));
        }
    }

    /// <summary>
    /// Put on a ThingDef to make it usable in the altar.
    ///
    /// A "vector" is the missing primitive that forced this assembly to exist:
    /// an item whose meaning is one specific gene. Nothing in vanilla does
    /// this - Genepack rolls its contents in PostMake(), so a genepack placed
    /// in a hand-authored map still has random contents.
    ///
    /// With this, deterministic delivery stops being a quest problem: the item
    /// can sit in an authored ruin, a quest stash, a loot table or a trader's
    /// stock, and it always means the same thing.
    /// </summary>
    public class GeneVectorExtension : DefModExtension
    {
        /// <summary>The gene this vector grants. Null means the lottery.</summary>
        public GeneDef gene;

        /// <summary>
        /// Blood charge consumed. Roughly "how many people" - one adult human
        /// yields about 1.0. Scale this up hard for the late vectors; the last
        /// one should cost an atrocity.
        /// </summary>
        public float chargeCost = 1f;

        /// <summary>
        /// Hours the rite takes. Facilities cut this.
        /// </summary>
        public float baseHours = 12f;

        /// <summary>
        /// Only pawns carrying this gene may receive the vector. Used to keep
        /// the altar founders-only until the Descent Engine lifts the
        /// restriction in the Industrial era.
        /// </summary>
        public GeneDef requiresRecipientGene;
    }

    /// <summary>
    /// Put on a facility ThingDef to make it change how the altar behaves when
    /// linked. VQE Ancients' twelve lab facilities are reskinned into these by
    /// patch, so the whole rack of buildings gets new meaning without any of
    /// them being rebuilt.
    /// </summary>
    public class AltarFacilityExtension : DefModExtension
    {
        /// <summary>Multiplies the blood cost. Below 1 is a discount.</summary>
        public float chargeCostFactor = 1f;

        /// <summary>Multiplies rite duration.</summary>
        public float durationFactor = 1f;

        /// <summary>
        /// Shifts the outcome roll upward. This is how a fully-built altar
        /// becomes reliable late game instead of staying a coin flip.
        /// </summary>
        public float outcomeBonus = 0f;

        /// <summary>Biases the lottery toward genes of this category.</summary>
        public GeneCategory biasCategory = GeneCategory.None;

        /// <summary>Relative weight multiplier applied to the biased category.</summary>
        public float biasStrength = 0f;

        /// <summary>Extra options offered on a successful lottery draw.</summary>
        public int extraOptions = 0;
    }

    /// <summary>
    /// The summed effect of everything linked to an altar. Computed fresh each
    /// time rather than cached - facilities get built, broken and deconstructed,
    /// and a stale bonus is worse than a recomputed one.
    /// </summary>
    public struct AltarModifiers
    {
        public float chargeCostFactor;
        public float durationFactor;
        public float outcomeBonus;
        public int extraOptions;
        public Dictionary<GeneCategory, float> categoryBias;

        public static AltarModifiers For(Thing altar)
        {
            AltarModifiers m = new AltarModifiers
            {
                chargeCostFactor = 1f,
                durationFactor = 1f,
                outcomeBonus = 0f,
                extraOptions = 0,
                categoryBias = new Dictionary<GeneCategory, float>()
            };

            CompAffectedByFacilities comp = altar.TryGetComp<CompAffectedByFacilities>();
            if (comp == null)
            {
                return m;
            }

            foreach (Thing facility in comp.LinkedFacilitiesListForReading)
            {
                // A facility that is unpowered or broken is linked but inert.
                if (!facility.TryGetComp<CompFacility>()?.CanBeActive ?? true)
                {
                    continue;
                }
                AltarFacilityExtension ext = facility.def.GetModExtension<AltarFacilityExtension>();
                if (ext == null)
                {
                    continue;
                }
                m.chargeCostFactor *= ext.chargeCostFactor;
                m.durationFactor *= ext.durationFactor;
                m.outcomeBonus += ext.outcomeBonus;
                m.extraOptions += ext.extraOptions;
                if (ext.biasCategory != GeneCategory.None && ext.biasStrength > 0f)
                {
                    m.categoryBias.TryGetValue(ext.biasCategory, out float existing);
                    m.categoryBias[ext.biasCategory] = existing + ext.biasStrength;
                }
            }

            // A stack of discounts must never reach free. The blood floor is
            // the whole point of the machine.
            if (m.chargeCostFactor < 0.25f)
            {
                m.chargeCostFactor = 0.25f;
            }
            return m;
        }
    }
}
