using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace Archinity
{
    /// <summary>
    /// The altar. One machine, one philosophy.
    ///
    /// It holds a charge measured in lives. A prisoner or slave hauled inside
    /// is drained and dies, and the charge stays in the building - so it never
    /// spoils and never needs refrigeration, which is the whole reason the
    /// charge lives here rather than in hemogen packs.
    ///
    /// A free colonist who walks in willingly spends that charge, plus a
    /// vector, and comes out changed. The recipient is never the one who dies.
    /// The price is always paid by somebody else.
    ///
    /// ENTRY IS ENTIRELY VANILLA. Willing entry uses JobDefOf.EnterBuilding via
    /// Building_Enterable.SelectPawn; unwilling entry uses JobDefOf.CarryToBuilding
    /// via WorkGiver_CarryToBuilding. Both are vanilla jobs, so the Multiplayer
    /// mod syncs them natively and this class needs no custom command gizmos.
    /// </summary>
    public class Building_Altar : Building_Enterable, IThingHolderWithDrawnPawn
    {
        /// <summary>Lives held. One drained adult human is worth about 1.</summary>
        private float charge;

        private int ticksRemaining;
        private bool draining;

        /// <summary>An adult human is the unit. Everything else scales off body size.</summary>
        private const float ChargePerBodySize = 1f;

        /// <summary>Draining takes a while. It is not a quick death.</summary>
        private const int DrainTicks = 7500;

        public const float MaxCharge = 200f;

        public float Charge => charge;

        // The vector rides in the base class's own container alongside the
        // occupant. A second ThingOwner would have to be registered as a child
        // holder, and Building_Enterable.GetChildHolders is not virtual - so
        // reusing innerContainer keeps save/load, despawn-drop and map search
        // all working on the vanilla path.
        private Pawn ContainedPawn => innerContainer.OfType<Pawn>().FirstOrDefault();

        public Thing LoadedVector => innerContainer.FirstOrDefault(
            t => t.def.HasModExtension<GeneVectorExtension>());

        public GeneVectorExtension LoadedVectorExtension =>
            LoadedVector?.def.GetModExtension<GeneVectorExtension>();

        public override bool IsContentsSuspended => false;

        public float HeldPawnDrawPos_Y => DrawPos.y + 0.03658537f;
        public float HeldPawnBodyAngle => base.Rotation.Opposite.AsAngle;
        public PawnPosture HeldPawnPosture => PawnPosture.LayingOnGroundFaceUp;

        public override Vector3 PawnDrawOffset =>
            IntVec3.West.RotatedBy(base.Rotation).ToVector3() / def.size.x;

        /// <summary>
        /// Slaves and prisoners are fuel. Free colonists are recipients. The
        /// distinction is made from the pawn's own status rather than from a
        /// mode toggle, which keeps the building free of custom gizmos - and it
        /// matches the fiction: you do not sacrifice your own, and you do not
        /// give the gift to cattle.
        /// </summary>
        public static bool IsFuel(Pawn p)
        {
            return p != null && (p.IsPrisonerOfColony || p.IsSlaveOfColony);
        }

        public override AcceptanceReport CanAcceptPawn(Pawn p)
        {
            if (p == null || !p.RaceProps.Humanlike)
            {
                return "Archinity_AltarNotHumanlike".Translate();
            }
            if (Working || ContainedPawn != null)
            {
                return "Archinity_AltarOccupied".Translate();
            }

            if (IsFuel(p))
            {
                return charge >= MaxCharge
                    ? (AcceptanceReport)"Archinity_AltarFull".Translate()
                    : (AcceptanceReport)true;
            }

            // From here on the pawn is a recipient, not fuel.
            GeneVectorExtension ext = LoadedVectorExtension;
            if (ext == null)
            {
                return "Archinity_AltarNoVector".Translate();
            }
            if (ext.requiresRecipientGene != null &&
                (p.genes == null || !p.genes.HasActiveGene(ext.requiresRecipientGene)))
            {
                return "Archinity_AltarRecipientUnworthy".Translate(
                    ext.requiresRecipientGene.LabelCap);
            }
            if (ext.gene != null && p.genes != null && p.genes.HasActiveGene(ext.gene))
            {
                return "Archinity_AltarAlreadyHasGene".Translate(ext.gene.LabelCap);
            }
            float cost = ext.chargeCost * AltarModifiers.For(this).chargeCostFactor;
            if (charge < cost)
            {
                return "Archinity_AltarNotEnoughCharge".Translate(
                    charge.ToString("0.#"), cost.ToString("0.#"));
            }
            return true;
        }

        public override void TryAcceptPawn(Pawn pawn)
        {
            if (!(bool)CanAcceptPawn(pawn))
            {
                return;
            }
            selectedPawn = pawn;
            bool reselect = pawn.DeSpawnOrDeselect();
            if (innerContainer.TryAddOrTransfer(pawn))
            {
                draining = IsFuel(pawn);
                startTick = Find.TickManager.TicksGame;
                AltarModifiers mods = AltarModifiers.For(this);
                if (draining)
                {
                    ticksRemaining = DrainTicks;
                }
                else
                {
                    GeneVectorExtension ext = LoadedVectorExtension;
                    ticksRemaining = Mathf.Max(
                        1, Mathf.RoundToInt(ext.baseHours * 2500f * mods.durationFactor));
                }
            }
            if (reselect)
            {
                Find.Selector.Select(pawn, playSound: false, forceDesignatorDeselect: false);
            }
        }

        protected override void Tick()
        {
            base.Tick();
            if (!Working)
            {
                return;
            }
            ticksRemaining--;
            if (ticksRemaining <= 0)
            {
                Finish();
            }
        }

        private void Finish()
        {
            Pawn occupant = ContainedPawn;
            startTick = -1;
            ticksRemaining = 0;
            selectedPawn = null;

            if (occupant == null)
            {
                draining = false;
                return;
            }

            if (draining)
            {
                DrainAndKill(occupant);
                draining = false;
                return;
            }

            PerformRite(occupant);
        }

        /// <summary>
        /// The sacrifice. Body size is the yield, so an ordinary adult is worth
        /// about one charge and an animal a fraction of that - which is why
        /// "fifty people or several hundred animals" is the shape of the
        /// endgame cost rather than a number pulled from nowhere.
        /// </summary>
        private void DrainAndKill(Pawn victim)
        {
            float yield = victim.BodySize * ChargePerBodySize;
            charge = Mathf.Min(MaxCharge, charge + yield);

            innerContainer.Remove(victim);
            victim.Kill(null);

            // The corpse is left in the altar's cell so it can be hauled away
            // and so the act leaves something behind to look at.
            if (victim.Corpse != null && !victim.Corpse.Spawned)
            {
                GenPlace.TryPlaceThing(victim.Corpse, base.Position, base.Map, ThingPlaceMode.Near);
            }

            Messages.Message(
                "Archinity_AltarDrained".Translate(victim.LabelShortCap, yield.ToString("0.#")),
                new TargetInfo(base.Position, base.Map), MessageTypeDefOf.NeutralEvent);
        }

        /// <summary>
        /// The rite. A named vector is deterministic - you always know which
        /// gene you are getting, and the roll never decides whether you get
        /// something. On a critical failure the vector is returned intact and
        /// only the blood and the pawn's time are lost, so a bad roll never
        /// destroys a quest reward.
        /// </summary>
        private void PerformRite(Pawn recipient)
        {
            GeneVectorExtension ext = LoadedVectorExtension;
            Thing vector = LoadedVector;
            if (ext == null || vector == null)
            {
                EjectRecipient(recipient);
                return;
            }

            AltarModifiers mods = AltarModifiers.For(this);
            charge = Mathf.Max(0f, charge - ext.chargeCost * mods.chargeCostFactor);

            bool critical = Rand.Value > Mathf.Clamp01(0.75f + mods.outcomeBonus);

            if (critical)
            {
                // The vector survives; the pawn does not walk it off.
                if (ArchinityDefOf.Archinity_RiteShock != null)
                {
                    recipient.health.AddHediff(ArchinityDefOf.Archinity_RiteShock);
                }
                Messages.Message(
                    "Archinity_AltarRiteFailed".Translate(recipient.LabelShortCap),
                    new TargetInfo(base.Position, base.Map), MessageTypeDefOf.NegativeEvent);
                EjectRecipient(recipient);
                return;
            }

            if (ext.gene != null)
            {
                GrantGene(recipient, ext.gene);
            }

            innerContainer.Remove(vector);
            vector.Destroy();

            Messages.Message(
                "Archinity_AltarRiteSucceeded".Translate(
                    recipient.LabelShortCap, ext.gene?.LabelCap ?? "?"),
                new TargetInfo(base.Position, base.Map), MessageTypeDefOf.PositiveEvent);
            EjectRecipient(recipient);
        }

        /// <summary>
        /// Genes arrive as xenogenes so that the founders' innate endogenes stay
        /// distinguishable from everything earned at the altar.
        /// </summary>
        public static void GrantGene(Pawn pawn, GeneDef gene)
        {
            if (pawn?.genes == null || gene == null || pawn.genes.HasActiveGene(gene))
            {
                return;
            }
            pawn.genes.AddGene(gene, xenogene: true);

            // Power gained here is never paid for in hunger.
            if (ArchinityDefOf.Archinity_ArchiteSustenance != null &&
                !pawn.health.hediffSet.HasHediff(ArchinityDefOf.Archinity_ArchiteSustenance))
            {
                pawn.health.AddHediff(ArchinityDefOf.Archinity_ArchiteSustenance);
            }
        }

        private void EjectRecipient(Pawn pawn)
        {
            innerContainer.Remove(pawn);
            GenPlace.TryPlaceThing(pawn, base.Position, base.Map, ThingPlaceMode.Near);
        }

        // ---- vector loading -------------------------------------------------

        public bool WantsVector => LoadedVector == null && !Working;

        public bool CanAcceptVector(Thing t)
        {
            return WantsVector
                && t != null
                && t.def.GetModExtension<GeneVectorExtension>() != null;
        }

        public bool TryAcceptVector(Thing t)
        {
            if (!CanAcceptVector(t))
            {
                return false;
            }
            Thing one = t.SplitOff(1);
            return innerContainer.TryAdd(one);
        }

        public override string GetInspectString()
        {
            List<string> parts = new List<string>();
            string basic = base.GetInspectString();
            if (!basic.NullOrEmpty())
            {
                parts.Add(basic);
            }
            parts.Add("Archinity_AltarCharge".Translate(
                charge.ToString("0.#"), MaxCharge.ToString("0")));
            Thing vector = LoadedVector;
            parts.Add(vector != null
                ? "Archinity_AltarVectorLoaded".Translate(vector.LabelCap).ToString()
                : "Archinity_AltarVectorEmpty".Translate().ToString());
            if (Working)
            {
                parts.Add(draining
                    ? "Archinity_AltarDraining".Translate(
                        ticksRemaining.ToStringTicksToPeriod()).ToString()
                    : "Archinity_AltarRiteInProgress".Translate(
                        ticksRemaining.ToStringTicksToPeriod()).ToString());
            }
            return string.Join("\n", parts);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref charge, "charge", 0f);
            Scribe_Values.Look(ref ticksRemaining, "ticksRemaining", 0);
            Scribe_Values.Look(ref draining, "draining", false);
        }
    }
}
