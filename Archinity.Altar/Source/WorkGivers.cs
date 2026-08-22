using RimWorld;
using Verse;
using Verse.AI;

namespace Archinity
{
    /// <summary>
    /// Hauls an unwilling pawn into the altar.
    ///
    /// Everything here is inherited. WorkGiver_CarryToBuilding already handles
    /// reservation, reachability, the prisoner/downed check and issuing
    /// JobDefOf.CarryToBuilding - the same vanilla path the gene extractor and
    /// growth vat use. Subclassing it means the sacrifice runs on vanilla job
    /// code, which is why it needs no multiplayer handling of its own.
    /// </summary>
    public class WorkGiver_CarryToAltar : WorkGiver_CarryToBuilding
    {
        public override ThingRequest PotentialWorkThingRequest =>
            ThingRequest.ForDef(ArchinityDefOf.Archinity_Altar);
    }

    /// <summary>
    /// Hauls a gene vector into a waiting altar, so the rite has something to
    /// spend when a recipient walks in.
    /// </summary>
    public class WorkGiver_LoadAltar : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest =>
            ThingRequest.ForDef(ArchinityDefOf.Archinity_Altar);

        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !ModsConfig.BiotechActive;
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return FindVectorFor(pawn, t as Building_Altar, forced) != null;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            Building_Altar altar = t as Building_Altar;
            Thing vector = FindVectorFor(pawn, altar, forced);
            if (vector == null)
            {
                return null;
            }
            Job job = JobMaker.MakeJob(ArchinityJobDefOf.Archinity_LoadAltar, altar, vector);
            job.count = 1;
            return job;
        }

        private Thing FindVectorFor(Pawn pawn, Building_Altar altar, bool forced)
        {
            if (altar == null || !altar.WantsVector)
            {
                return null;
            }
            if (!pawn.CanReserveAndReach(altar, PathEndMode.Touch, Danger.Deadly,
                                         1, -1, null, forced))
            {
                return null;
            }
            if (pawn.Map.designationManager.DesignationOn(
                    altar, DesignationDefOf.Deconstruct) != null)
            {
                return null;
            }
            return GenClosest.ClosestThingReachable(
                pawn.Position,
                pawn.Map,
                ThingRequest.ForGroup(ThingRequestGroup.HaulableEver),
                PathEndMode.OnCell,
                TraverseParms.For(pawn),
                9999f,
                candidate => altar.CanAcceptVector(candidate)
                             && !candidate.IsForbidden(pawn)
                             && pawn.CanReserve(candidate, 1, -1, null, forced));
        }
    }

    [DefOf]
    public static class ArchinityJobDefOf
    {
        public static JobDef Archinity_LoadAltar;

        static ArchinityJobDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(ArchinityJobDefOf));
        }
    }

    /// <summary>
    /// Carry one vector to the altar and put it in. Modelled on the vanilla
    /// haul-to-container drivers.
    /// </summary>
    public class JobDriver_LoadAltar : JobDriver
    {
        private Building_Altar Altar => (Building_Altar)job.GetTarget(TargetIndex.A).Thing;
        private Thing Vector => job.GetTarget(TargetIndex.B).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(Altar, job, 1, -1, null, errorOnFailed)
                && pawn.Reserve(Vector, job, 1, 1, null, errorOnFailed);
        }

        protected override System.Collections.Generic.IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOnBurningImmobile(TargetIndex.A);
            this.FailOn(() => !Altar.WantsVector);

            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.ClosestTouch)
                .FailOnDespawnedNullOrForbidden(TargetIndex.B)
                .FailOnSomeonePhysicallyInteracting(TargetIndex.B);

            yield return Toils_Haul.StartCarryThing(
                TargetIndex.B, putRemainderInQueue: false, subtractNumTakenFromJobCount: true);

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

            Toil insert = ToilMaker.MakeToil("InsertVector");
            insert.initAction = delegate
            {
                if (pawn.carryTracker.CarriedThing != null)
                {
                    if (!Altar.TryAcceptVector(pawn.carryTracker.CarriedThing))
                    {
                        pawn.carryTracker.TryDropCarriedThing(
                            pawn.Position, ThingPlaceMode.Near, out Thing _);
                    }
                    else if (pawn.carryTracker.CarriedThing != null
                             && pawn.carryTracker.CarriedThing.stackCount <= 0)
                    {
                        pawn.carryTracker.innerContainer.Clear();
                    }
                }
            };
            insert.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return insert;
        }
    }
}
