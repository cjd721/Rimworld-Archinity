using System.Collections.Generic;
using System.Linq;
using Verse;

namespace Archinity
{
    /// <summary>
    /// What a gene is FOR. Facilities linked to the altar bias the draw toward
    /// one of these, which is what turns a rack of identical stackable
    /// buildings into a tuned altar - a war-altar draws differently from an
    /// artisan-altar.
    /// </summary>
    public enum GeneCategory
    {
        None,
        Combat,
        Work,
        Mind,
        Body,
        Survival,
        Social
    }

    /// <summary>
    /// One archite gene's place in the lottery.
    ///
    /// Tier and category are hand-assigned because the game's own numbers
    /// cannot separate these genes: biostatMet is 0 for every archite gene but
    /// one, and biostatCpx is 3 for 35 of the 50 in our load order. Deathless
    /// (cpx 7) and a purely cosmetic gene (cpx 3) are indistinguishable to any
    /// automatic rule, so the ranking is authored. See docs/archite-gene-pool.md.
    /// </summary>
    public class GenePoolEntry
    {
        public GeneDef gene;

        /// <summary>1 (trivial) to 5 (campaign-defining).</summary>
        public int tier = 1;

        public GeneCategory category = GeneCategory.None;

        /// <summary>
        /// Never offered by the lottery at any tier. Reserved genes exist only
        /// as named quest vectors, or - for Deathless and Ageless - not at all,
        /// so that nothing the colony builds can ever match the two founders.
        /// </summary>
        public bool reserved = false;
    }

    /// <summary>
    /// The whole draw table, as a single def so it can be read and edited in
    /// one place rather than smeared across 50 patches.
    /// </summary>
    public class GenePoolDef : Def
    {
        public List<GenePoolEntry> entries = new List<GenePoolEntry>();

        /// <summary>
        /// Genes the founders keep to themselves. Stripped from anyone they
        /// convert via xenogerm reimplantation.
        /// </summary>
        public List<GeneDef> founderOnlyGenes = new List<GeneDef>();

        /// <summary>
        /// Genes forced onto a convert that the founders themselves do not
        /// carry. Deathrest lives here: every vampire the colony makes must go
        /// into the ground periodically, and the two originals never do.
        /// Differentiation by what you lack.
        /// </summary>
        public List<GeneDef> conversionAddsGenes = new List<GeneDef>();

        /// <summary>
        /// Carrying this permits the archon-tier weapon and armour that
        /// VRE-Archon otherwise locks behind VRE_Transcendent. Rebound so the
        /// gear becomes usable in the Ultra era instead of at the very end,
        /// when there would be nothing left to use it for.
        /// </summary>
        public GeneDef archonEquipmentGene;

        private Dictionary<GeneDef, GenePoolEntry> lookup;

        public GenePoolEntry EntryFor(GeneDef gene)
        {
            if (gene == null)
            {
                return null;
            }
            if (lookup == null)
            {
                lookup = new Dictionary<GeneDef, GenePoolEntry>();
                foreach (GenePoolEntry e in entries)
                {
                    if (e.gene != null)
                    {
                        lookup[e.gene] = e;
                    }
                }
            }
            return lookup.TryGetValue(gene, out GenePoolEntry found) ? found : null;
        }

        /// <summary>
        /// Genes this pawn could actually receive: in the pool, not reserved,
        /// within the tier band, and not already carried.
        /// </summary>
        public IEnumerable<GenePoolEntry> Available(Pawn pawn, int minTier, int maxTier)
        {
            foreach (GenePoolEntry e in entries)
            {
                if (e.reserved || e.gene == null || e.tier < minTier || e.tier > maxTier)
                {
                    continue;
                }
                if (pawn?.genes != null && pawn.genes.HasActiveGene(e.gene))
                {
                    continue;
                }
                yield return e;
            }
        }

        /// <summary>
        /// Every archite gene in the load order that the pool forgot. Logged
        /// once at startup: a new mod can add archite genes at any time, and a
        /// gene missing from the pool would silently never appear.
        /// </summary>
        public IEnumerable<GeneDef> MissingArchiteGenes()
        {
            HashSet<GeneDef> known = new HashSet<GeneDef>(
                entries.Where(e => e.gene != null).Select(e => e.gene));
            foreach (GeneDef g in DefDatabase<GeneDef>.AllDefsListForReading)
            {
                if (g.biostatArc > 0 && !known.Contains(g))
                {
                    yield return g;
                }
            }
        }
    }
}
