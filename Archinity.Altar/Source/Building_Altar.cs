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
    /// BOTH ENTRIES RUN ON VANILLA JOBS, but neither of them has a UI in the
    /// base class - Building_Enterable ships no insert-pawn gizmo and no float
    /// menu, and SelectPawn is never called from anywhere in it. So the two
    /// surfaces below exist purely to reach vanilla:
    ///
    ///   Willing   - GetFloatMenuOptions issues JobDefOf.EnterBuilding as an
    ///               ordered job and never touches selectedPawn.
    ///   Unwilling - a gizmo nominates the fuel by writing selectedPawn, which
    ///               is what wakes WorkGiver_CarryToBuilding up.
    ///
    /// The difference matters for multiplayer. TryTakeOrderedJob is synced by
    /// Multiplayer natively, so the willing path needs nothing. selectedPawn is
    /// scribed state, so the unwilling path needs SetSelectedPawn to be a
    /// SyncMethod.
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

        // ---- entry surfaces -------------------------------------------------

        /// <summary>
        /// Willing entry. Modelled on Building_GrowthVat's own float menu, with
        /// one deliberate difference: the vat calls SelectPawn, which writes
        /// selectedPawn before ordering the job. We only order the job.
        ///
        /// That is the whole multiplayer argument. Pawn_JobTracker.TryTakeOrderedJob
        /// is a registered SyncMethod, so the order crosses the wire and both
        /// clients run the same job, and the job is what writes selectedPawn.
        /// JobDriver_EnterBuilding.MakeNewToils writes it twice: its FIRST toil
        /// sets Building.SelectedPawn = pawn before the pawn has moved, and its
        /// last toil calls TryAcceptPawn on arrival, which sets it again. Both
        /// writes sit inside the already-synced job, so both clients make them.
        /// Setting it here instead would be a one-client write to scribed state.
        /// </summary>
        public override IEnumerable<FloatMenuOption> GetFloatMenuOptions(Pawn selPawn)
        {
            foreach (FloatMenuOption option in base.GetFloatMenuOptions(selPawn))
            {
                yield return option;
            }

            if (!selPawn.CanReach(this, PathEndMode.InteractionCell, Danger.Deadly))
            {
                yield return new FloatMenuOption(
                    "CannotEnterBuilding".Translate(this) + ": "
                        + "NoPath".Translate().CapitalizeFirst(),
                    null);
                yield break;
            }

            AcceptanceReport report = CanAcceptPawn(selPawn);
            if (report.Accepted)
            {
                yield return FloatMenuUtility.DecoratePrioritizedTask(
                    new FloatMenuOption("EnterBuilding".Translate(this), delegate
                    {
                        selPawn.jobs.TryTakeOrderedJob(
                            JobMaker.MakeJob(JobDefOf.EnterBuilding, this), JobTag.Misc);
                    }),
                    selPawn, this);
            }
            else if (!report.Reason.NullOrEmpty())
            {
                // CanAcceptPawn already distinguishes all seven refusals. Say
                // which one it was rather than greying the option out mutely.
                yield return new FloatMenuOption(
                    "CannotEnterBuilding".Translate(this) + ": " + report.Reason.CapitalizeFirst(),
                    null);
            }
        }

        /// <summary>
        /// Unwilling entry. Fuel does not volunteer, so somebody has to carry it,
        /// and WorkGiver_CarryToBuilding does not lift a finger until
        /// SelectedPawn is set. Nominating that pawn is the only thing this
        /// command does.
        /// </summary>
        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo gizmo in base.GetGizmos())
            {
                yield return gizmo;
            }

            Command_Action nominate = new Command_Action
            {
                defaultLabel = "Archinity_AltarSelectFuel".Translate(),
                defaultDesc = "Archinity_AltarSelectFuelDesc".Translate(),
                icon = Building_GrowthVat.InsertPawnIcon.Texture,
                action = OpenFuelMenu
            };
            // The two refusals that apply to every candidate at once belong on
            // the button, not repeated down a list of identical grey rows.
            if (Working || ContainedPawn != null)
            {
                nominate.Disable("Archinity_AltarOccupied".Translate());
            }
            else if (charge >= MaxCharge)
            {
                nominate.Disable("Archinity_AltarFull".Translate());
            }
            yield return nominate;
        }

        private void OpenFuelMenu()
        {
            List<FloatMenuOption> options = new List<FloatMenuOption>();
            foreach (Pawn candidate in base.Map.mapPawns.AllPawnsSpawned)
            {
                if (!IsFuel(candidate) || !(bool)CanAcceptPawn(candidate))
                {
                    continue;
                }
                Pawn target = candidate;
                if (!CanBeHauledToAltar(target))
                {
                    options.Add(new FloatMenuOption(
                        target.LabelCap + ": " + "Archinity_AltarFuelWalksFree".Translate(),
                        null));
                    continue;
                }
                options.Add(new FloatMenuOption(
                    target.LabelCap, delegate { SetSelectedPawn(target); }, target, Color.white));
            }
            if (!options.Any())
            {
                options.Add(new FloatMenuOption("NoViablePawns".Translate(), null));
            }
            if (selectedPawn != null)
            {
                options.Add(new FloatMenuOption("CommandCancelLoad".Translate(), delegate
                {
                    SetSelectedPawn(null);
                }));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        /// <summary>
        /// What WorkGiver_CarryToBuilding.HasJobOnThing will actually agree to
        /// lift, mirrored from the decompiled source rather than assumed: a
        /// prisoner, a downed pawn, one that cannot move, or one barred from the
        /// work type. An upright, mobile slave is none of those, so nominating
        /// one would leave the order standing with nobody ever coming for it.
        /// IsFuel accepts slaves, so this second question has to be asked.
        /// </summary>
        public static bool CanBeHauledToAltar(Pawn p)
        {
            if (p == null)
            {
                return false;
            }
            WorkTypeDef workType = ArchinityDefOf.Archinity_CarryToAltarWorkGiver?.workType;
            return p.IsPrisonerOfColony
                || p.Downed
                || !p.health.capacities.CapableOf(PawnCapacityDefOf.Moving)
                || (workType != null && p.WorkTypeIsDisabled(workType));
        }

        /// <summary>
        /// selectedPawn is scribed simulation state, so writing it from a gizmo
        /// callback would diverge the two clients immediately. Multiplayer's
        /// attribute is inert when the mod is absent, which is what keeps this a
        /// soft dependency.
        ///
        /// Re-checked here rather than trusted from the menu: the command is
        /// built on one client and executed on both, and the map can move
        /// between those two moments. When the re-check refuses, it says so -
        /// a silent no-op looks identical to a broken button.
        ///
        /// Messaging from a SyncMethod is safe as long as the message is not
        /// historical. Multiplayer's SilenceMessagesNotTargetedAtMe prefixes
        /// Messages.Message and drops any non-historical message raised while a
        /// synced command is executing on a client that did not issue it, so
        /// historical:false posts the refusal exactly once, to the player who
        /// clicked. (It also keeps the message off the shared unique-ID stream.)
        /// </summary>
        [Multiplayer.API.SyncMethod]
        public void SetSelectedPawn(Pawn p)
        {
            if (p != null)
            {
                AcceptanceReport report = CanAcceptPawn(p);
                string refusal = null;
                if (!IsFuel(p))
                {
                    refusal = "Archinity_AltarNoLongerFuel".Translate();
                }
                else if (!report.Accepted)
                {
                    // Every refusal CanAcceptPawn returns carries a reason.
                    refusal = report.Reason;
                }
                else if (!CanBeHauledToAltar(p))
                {
                    refusal = "Archinity_AltarFuelWalksFree".Translate();
                }
                if (refusal != null)
                {
                    Messages.Message(
                        "Archinity_AltarNominateRejected".Translate(p.LabelShortCap, refusal),
                        new LookTargets(p), MessageTypeDefOf.RejectInput, historical: false);
                    return;
                }
            }
            selectedPawn = p;
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
