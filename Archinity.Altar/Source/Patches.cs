using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using Multiplayer.API;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace Archinity
{
    [StaticConstructorOnStartup]
    public static class ArchinityMod
    {
        static ArchinityMod()
        {
            Harmony harmony = new Harmony("archinity.altar");
            harmony.PatchAll(Assembly.GetExecutingAssembly());
            NeutraliseArchonEquipmentGate();
            WarnAboutGenesMissingFromPool();

            // Determinism repairs to third-party mods. These name no Multiplayer
            // type, so they are safe to JIT with the Multiplayer mod absent, and
            // they are registered unconditionally on purpose: both machines then
            // run identical code whether or not this session happens to be co-op,
            // and neither repair is worse in singleplayer. Glittertech's is a save
            // -integrity fix that singleplayer wants on its own merits.
            if (ModIsLoaded("wiri.compositableloadouts"))
            {
                LoadoutSchedulingSync.Register(harmony);
            }

            if (ModIsLoaded("ushanka.glittertechexpansion"))
            {
                GlittershipChunkSync.Register(harmony);
            }

            if (!ModIsLoaded("rwmt.multiplayer"))
            {
                return;
            }

            // Order matters only in that both need Multiplayer present. Ours
            // first: it is the one that protects our own building.
            ArchinitySync.RegisterOurSyncMethods();

            if (ModIsLoaded("fluffy.pharmacist"))
            {
                PharmacistSync.Register(harmony);
            }
        }

        private static bool ModIsLoaded(string packageId)
        {
            return LoadedModManager.RunningModsListForReading.Any(
                m => m.PackageIdPlayerFacing.Equals(
                    packageId, StringComparison.OrdinalIgnoreCase));
        }

        /// <summary>
        /// Multiplayer Compatibility carries the only sync patch Pharmacist has,
        /// and against "Pharmacist: Represcribed" its constructor throws, so the
        /// whole patch is skipped and the mod runs unsynced. See
        /// tmp/scratch/pharmacist-mp-fix-2026-08-28.md.
        ///
        /// Both presence checks happen here, before any Multiplayer.API type is
        /// touched: if the Multiplayer mod is absent 0MultiplayerAPI.dll is not
        /// loaded, and merely JIT-ing a method that names MP would throw. Keeping
        /// that method uncalled keeps it unJITted.
        /// </summary>
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

    /// <summary>
    /// Restores the Multiplayer sync that Multiplayer Compatibility loses on
    /// "Pharmacist: Represcribed".
    ///
    /// MPCompat's Multiplayer.Compat.Pharmacist constructor does
    /// <c>AccessTools.StaticFieldRefAccess&lt;object&gt;(AccessTools.Field(type,
    /// "medicalCare"))</c>. Represcribed renamed that static to
    /// <c>PharmacistSettings.CareSettings</c>, so AccessTools.Field returns null
    /// and the constructor throws ArgumentNullException, which makes MPCompat
    /// discard the entire patch - no watched fields, no synced care selectors.
    ///
    /// This matters because the state is not cosmetic. CareSettings lives on a
    /// WorldComponent and is written to the save by ExposeData, and Represcribed
    /// reads it from HealthAIUtility.FindBestMedicine and
    /// WorkGiver_DoBill.GetMedicalCareCategory - both inside already-synced job
    /// and work-giver paths. One player nudging a slider therefore changes which
    /// medicine that player's simulation picks up, and the other client never
    /// hears about it.
    ///
    /// The statics below are registration handles written once at startup, in the
    /// same order on both machines. They are not a cache and nothing keys off
    /// client-local state.
    /// </summary>
    /// <summary>
    /// Registers OUR OWN [SyncMethod]s with Multiplayer.
    ///
    /// THIS IS NOT OPTIONAL AND ITS ABSENCE IS SILENT. A [SyncMethod] attribute
    /// does nothing on its own: Multiplayer never scans third-party assemblies
    /// for it. Verified in the decompiled Multiplayer.dll = the only paths into
    /// Sync.RegisterAllAttributes(Assembly) are the public MP.RegisterAll(...),
    /// which a mod must call itself, and one internal call scoped to
    /// Multiplayer's own assembly.
    ///
    /// Without this call, Building_Altar.SetSelectedPawn carries the attribute
    /// and still executes as a plain local method. It writes selectedPawn =
    /// scribed simulation state that the already-synced
    /// WorkGiver_CarryToBuilding.HasJobOnThing reads = on the clicking client
    /// only, with no error and no warning. That is a save-corrupting desync
    /// wearing the costume of a fix, and it is exactly what CODING_STANDARDS.md's
    /// loudness gate exists to catch.
    ///
    /// Separate class from ArchinityMod on purpose: naming an MP type is enough
    /// to fault the JIT when 0MultiplayerAPI.dll is not loaded, so the caller
    /// checks for the Multiplayer mod before this class is ever touched.
    /// </summary>
    public static class ArchinitySync
    {
        public static void RegisterOurSyncMethods()
        {
            try
            {
                MP.RegisterAll(Assembly.GetExecutingAssembly());
            }
            catch (Exception e)
            {
                // Loud, because the failure mode this guards is silent.
                Log.Error("[Archinity] MP.RegisterAll failed, so our [SyncMethod]s "
                    + "are NOT registered. The altar's fuel-nomination gizmo will "
                    + "write selectedPawn on one client only and desync the save. "
                    + "Do not use it. " + e);
            }
        }
    }

    public static class PharmacistSync
    {
        private const string Tag = "[Archinity] Pharmacist multiplayer sync: ";

        private static AccessTools.FieldRef<object> careSettingsRef;
        private static MethodInfo setDefaultsMethod;
        private static ISyncField diseaseMarginField;
        private static ISyncField diseaseThresholdField;
        private static ISyncField minorWoundsThresholdField;
        private static ISyncField searchRadiusField;

        internal static void Register(Harmony harmony)
        {
            if (!MP.enabled)
            {
                return;
            }

            // If MPCompat ever ships a fixed patch, its registrations land first
            // (Mod constructors all run before StaticConstructorOnStartup) and
            // ours would double-watch every field. Stand down instead.
            Type mpCompat = AccessTools.TypeByName("Multiplayer.Compat.Pharmacist");
            FieldInfo mpCompatHandle = mpCompat == null
                ? null
                : AccessTools.Field(mpCompat, "diseaseMarginField");
            if (mpCompatHandle != null && mpCompatHandle.GetValue(null) != null)
            {
                Log.Message(Tag + "Multiplayer Compatibility registered its own "
                            + "patch this run, so Archinity is standing down.");
                return;
            }

            Type settings = AccessTools.TypeByName("Pharmacist.PharmacistSettings");
            if (settings == null)
            {
                Warn("type Pharmacist.PharmacistSettings not found");
                return;
            }

            FieldInfo careSettings = AccessTools.Field(settings, "CareSettings");
            if (careSettings == null || !careSettings.IsStatic)
            {
                Warn("static field PharmacistSettings.CareSettings not found");
                return;
            }

            setDefaultsMethod = AccessTools.Method(settings, "SetDefaults");
            if (setDefaultsMethod == null)
            {
                Warn("method PharmacistSettings.SetDefaults not found");
                return;
            }

            Type careType = AccessTools.Inner(settings, "MedicalCare");
            if (careType == null)
            {
                Warn("nested type PharmacistSettings.MedicalCare not found");
                return;
            }

            Type window = AccessTools.TypeByName("Pharmacist.MainTabWindow_Pharmacist");
            MethodInfo drawOptions = window == null
                ? null
                : AccessTools.Method(window, "DrawOptions");
            if (drawOptions == null)
            {
                Warn("method MainTabWindow_Pharmacist.DrawOptions not found");
                return;
            }

            // Every field the options pane writes. _searchRadius is new in
            // Represcribed and MPCompat never covered it, but FindBestMedicine
            // reads it as a search distance, so it diverges just as loudly.
            diseaseMarginField = RegisterField(careType, "_diseaseMargin");
            diseaseThresholdField = RegisterField(careType, "_diseaseThreshold");
            minorWoundsThresholdField = RegisterField(careType, "_minorWoundsThreshold");
            searchRadiusField = RegisterField(careType, "_searchRadius");
            if (diseaseMarginField == null || diseaseThresholdField == null
                || minorWoundsThresholdField == null || searchRadiusField == null)
            {
                return;
            }

            careSettingsRef = AccessTools.StaticFieldRefAccess<object>(careSettings);
            MP.RegisterSyncWorker<object>(SyncCareSettings, careType,
                                          isImplicit: false, shouldConstruct: false);

            // The three float-menu callbacks inside DrawCareSelectors are the
            // only way a player edits the per-population care grid, and each is a
            // closure over its population/severity. Ordinals 0, 1 and 2 are the
            // three <>c__DisplayClass18_* lambdas, the same ordinals MPCompat
            // used. Registered one at a time so the log names exactly which
            // click paths are still unsynced if the mod is recompiled.
            for (int ordinal = 0; ordinal < 3; ordinal++)
            {
                try
                {
                    MP.RegisterSyncDelegateLambda(window, "DrawCareSelectors", ordinal);
                }
                catch (Exception e)
                {
                    Log.Error(Tag + "could not register lambda " + ordinal
                              + " of MainTabWindow_Pharmacist.DrawCareSelectors. "
                              + "Medical care grid edits made through that button "
                              + "will NOT reach the other player. " + e);
                }
            }

            harmony.Patch(drawOptions,
                prefix: new HarmonyMethod(typeof(PharmacistSync), nameof(PreDrawOptions)),
                postfix: new HarmonyMethod(typeof(PharmacistSync), nameof(PostDrawOptions)));
        }

        private static ISyncField RegisterField(Type careType, string name)
        {
            if (AccessTools.Field(careType, name) == null)
            {
                Warn("field PharmacistSettings.MedicalCare." + name + " not found");
                return null;
            }
            return MP.RegisterSyncField(careType, name);
        }

        private static void Warn(string what)
        {
            Log.Warning(Tag + what + ". Pharmacist's medical-care settings are "
                        + "scribed save state read from tending jobs, so they will "
                        + "diverge between the two clients. Re-check "
                        + "PharmacistReprescribed.dll against Patches.cs.");
        }

        // Set by the prefix, read by the postfix, on the UI thread only. A bare
        // MP.IsInMultiplayer test in both halves is not enough: if the prefix
        // bails the postfix must not close a watch that was never opened.
        private static bool watching;

        private static void PreDrawOptions()
        {
            watching = false;
            if (!MP.IsInMultiplayer)
            {
                return;
            }
            object care = CurrentCareSettings();
            if (care == null)
            {
                Warn("PharmacistSettings.CareSettings was null and SetDefaults did "
                     + "not fill it, so this options pane is unwatched");
                return;
            }
            MP.WatchBegin();
            watching = true;
            diseaseMarginField.Watch(care);
            diseaseThresholdField.Watch(care);
            minorWoundsThresholdField.Watch(care);
            searchRadiusField.Watch(care);
        }

        private static void PostDrawOptions()
        {
            if (watching)
            {
                watching = false;
                MP.WatchEnd();
            }
        }

        /// <summary>
        /// CareSettings is a singleton hanging off the world component, so there
        /// is nothing to write - the reader just picks the same object up again.
        /// </summary>
        private static void SyncCareSettings(SyncWorker sync, ref object obj)
        {
            if (!sync.isWriting)
            {
                obj = CurrentCareSettings();
            }
        }

        private static object CurrentCareSettings()
        {
            object care = careSettingsRef();
            if (care == null)
            {
                setDefaultsMethod.Invoke(null, null);
                care = careSettingsRef();
            }
            return care;
        }
    }

    /// <summary>
    /// Compositable Loadouts schedules its per-pawn loadout pass through
    /// <c>ThinkNode_LoadoutRealisation.nextUpdateTick</c>, a
    /// <c>Dictionary&lt;Pawn, int&gt;</c> that is never scribed, never cleared on
    /// load, and keyed by <b>Pawn object reference</b>. Multiplayer's
    /// SaveAndReload rebuilds every Pawn at every join point, so after a reload
    /// every lookup misses. A miss is defaulted to 0 - "update now" - and
    /// <c>SetPawnLastUpdated</c> then draws <c>Rand.Range(10000, 15000)</c>
    /// *inside* <c>TryIssueJobPackage</c>. That is an unequal draw against the
    /// tick-seeded stream Multiplayer hashes.
    ///
    /// This is not theoretical. It desynced a live two-player session on
    /// 2026-08-28: desync report Desync-01, tick 18216, pawn Human1189 - the host
    /// ran PickUpAndHaul's CheckIfPawnShouldUnloadInventory while the client ran
    /// SetPawnLastUpdated, and ThinkNode_LoadoutRealisation appears 4x in the
    /// client's traces and 0x in the host's. Every rejoin re-empties the
    /// dictionary, so it re-fired within seconds, indefinitely.
    ///
    /// The replacement is stateless. Eligibility becomes a pure function of
    /// TicksAbs and thingIDNumber, both synced simulation state. No dictionary to
    /// go stale, no Rand to draw unequally, and nothing a reload can reset on one
    /// machine and not the other.
    ///
    /// <b>Rand.PushState/PopState would not fix this.</b> The usual compat-layer
    /// wrap would hide the random-state divergence while leaving the pawn taking
    /// a different think-tree branch on each machine, which is real divergence,
    /// not just a hash mismatch. The schedule itself has to be deterministic.
    /// </summary>
    public static class LoadoutSchedulingSync
    {
        private const string Tag = "[Archinity] Compositable Loadouts scheduling: ";

        /// <summary>Mean of the original <c>Rand.Range(10000, 15000)</c>.</summary>
        private const int IntervalTicks = 12500;

        /// <summary>
        /// How long each pawn stays eligible within an interval. The original
        /// updated on the first job request past a per-pawn deadline; a stateless
        /// rule needs a window rather than an instant, because TryIssueJobPackage
        /// only runs when a job ends and would almost never land on one exact
        /// tick. 600 ticks is ten seconds - wide enough that a working colonist
        /// reliably asks for a job inside it, narrow enough to stay a ~4.8% duty
        /// cycle. A pawn may re-check more than once inside the window; the pass
        /// is a re-evaluation, so that costs a little work and changes nothing.
        /// </summary>
        private const int WindowTicks = 600;

        internal static void Register(Harmony harmony)
        {
            Type node = AccessTools.TypeByName("Inventory.ThinkNode_LoadoutRealisation");
            if (node == null)
            {
                Warn("type Inventory.ThinkNode_LoadoutRealisation not found");
                return;
            }

            MethodInfo needsUpdate = AccessTools.Method(
                node, "PawnNeedsUpdate", new[] { typeof(Pawn) });
            MethodInfo setUpdated = AccessTools.Method(
                node, "SetPawnLastUpdated", new[] { typeof(Pawn) });
            if (needsUpdate == null || setUpdated == null)
            {
                Warn("PawnNeedsUpdate and/or SetPawnLastUpdated not found on "
                     + "ThinkNode_LoadoutRealisation");
                return;
            }

            harmony.Patch(needsUpdate, prefix: new HarmonyMethod(AccessTools.Method(
                typeof(LoadoutSchedulingSync), nameof(NeedsUpdatePrefix))));
            harmony.Patch(setUpdated, prefix: new HarmonyMethod(AccessTools.Method(
                typeof(LoadoutSchedulingSync), nameof(SetUpdatedPrefix))));

            // Success is logged, not just failure. This patch is the difference
            // between a playable session and a desync loop, both players have to
            // be running it, and neither can tell by looking at the game. One line
            // in the log is how each of them confirms their own install.
            Log.Message(Tag + "loadout scheduling is deterministic "
                        + "(interval " + IntervalTicks + ", window " + WindowTicks + ").");
        }

        /// <summary>
        /// Replaces the dictionary lookup outright. Both terms are synced: TicksAbs
        /// is the shared clock and thingIDNumber is scribed with the pawn, so the
        /// two machines agree on every tick without storing anything.
        /// </summary>
        private static bool NeedsUpdatePrefix(Pawn pawn, ref bool __result)
        {
            if (pawn == null)
            {
                __result = false;
                return false;
            }
            int phase = (GenTicks.TicksAbs + pawn.thingIDNumber) % IntervalTicks;
            __result = phase >= 0 && phase < WindowTicks;
            return false;
        }

        /// <summary>
        /// The only caller of the dictionary's writer. With eligibility computed
        /// rather than stored there is nothing to write, and writing would
        /// reintroduce the Rand draw this patch exists to remove.
        /// </summary>
        private static bool SetUpdatedPrefix()
        {
            return false;
        }

        private static void Warn(string what)
        {
            Log.Warning(Tag + what + ". The mod's own scheduler is therefore still "
                        + "in force, and it draws Rand inside the think tree off a "
                        + "dictionary that a reload resets on one machine only. This "
                        + "WILL desync a multiplayer session. Re-check Inventory.dll "
                        + "against Patches.cs, or disable the mod.");
        }
    }

    /// <summary>
    /// Ushanka's Glittertech Expansion keeps its glittership-debris event timer in
    /// <c>WorldComponent_GlittershipChunk</c>, and two details make it desync under
    /// Multiplayer:
    ///
    /// 1. <c>Instance</c> is a static that survives Multiplayer's SaveAndReload. The
    ///    constructor early-returns when it is already set, so from the second load
    ///    onward the live component is the stale original and the freshly
    ///    constructed one is discarded. That is the "Duplicate
    ///    WorldComponent_GlittershipChunk detected. Ignoring." line in every log.
    ///
    /// 2. <c>ExposeData</c> scribes only <c>_didEvent</c>. <c>_ticksToFire</c> and
    ///    <c>_ticksPassed</c> are never saved, so the host carries values
    ///    accumulated since worldgen while a joining client starts from a fresh
    ///    roll, and the two evaluate <c>_ticksPassed % TICK_CHECK_INTERVAL</c> on
    ///    different ticks.
    ///
    /// Today this is latent: the tick body returns early until
    /// USH_GlittertechFabrication is researched. When that research lands, FireEvent
    /// runs PawnGroupMakerUtility.GeneratePawns and CellFinderLoose on one machine
    /// only - both heavy Rand consumers - and the save diverges.
    ///
    /// The prefix clears <c>Instance</c> so the constructor takes its normal full
    /// path on every load, and the postfix scribes the two timers under our own
    /// labels, so the author adding real persistence later cannot collide with us.
    /// </summary>
    public static class GlittershipChunkSync
    {
        private const string Tag = "[Archinity] Glittertech glittership chunk: ";

        private static FieldInfo instanceBackingField;
        private static FieldInfo ticksToFireField;
        private static FieldInfo ticksPassedField;

        internal static void Register(Harmony harmony)
        {
            Type comp = AccessTools.TypeByName("USH_GE.WorldComponent_GlittershipChunk");
            if (comp == null)
            {
                Warn("type USH_GE.WorldComponent_GlittershipChunk not found");
                return;
            }

            ConstructorInfo ctor = AccessTools.Constructor(comp, new[] { typeof(World) });
            MethodInfo expose = AccessTools.DeclaredMethod(comp, "ExposeData");
            instanceBackingField = AccessTools.Field(comp, "<Instance>k__BackingField");
            ticksToFireField = AccessTools.Field(comp, "_ticksToFire");
            ticksPassedField = AccessTools.Field(comp, "_ticksPassed");

            if (ctor == null || expose == null || instanceBackingField == null
                || ticksToFireField == null || ticksPassedField == null)
            {
                Warn("constructor, ExposeData, Instance backing field, _ticksToFire "
                     + "or _ticksPassed not found");
                return;
            }

            harmony.Patch(ctor, prefix: new HarmonyMethod(AccessTools.Method(
                typeof(GlittershipChunkSync), nameof(ClearInstancePrefix))));
            harmony.Patch(expose, postfix: new HarmonyMethod(AccessTools.Method(
                typeof(GlittershipChunkSync), nameof(ExposeDataPostfix))));

            Log.Message(Tag + "debris-event timer now reload-stable and scribed.");
        }

        /// <summary>
        /// Nulling the static before construction is what makes the author's own
        /// full-init path run every time, rather than us reaching in afterwards to
        /// repair a half-constructed object. World.FillComponents builds exactly one
        /// of these per World, so there is no case where the earlier instance should
        /// have won.
        /// </summary>
        private static void ClearInstancePrefix()
        {
            instanceBackingField.SetValue(null, null);
        }

        private static void ExposeDataPostfix(object __instance)
        {
            int toFire = (int)ticksToFireField.GetValue(__instance);
            int passed = (int)ticksPassedField.GetValue(__instance);

            Scribe_Values.Look(ref toFire, "Archinity_ticksToFire", 0);
            Scribe_Values.Look(ref passed, "Archinity_ticksPassed", 0);

            if (Scribe.mode != LoadSaveMode.LoadingVars)
            {
                return;
            }

            // A save written before this patch has no node, so Look leaves 0. The
            // constructor has already rolled a real delay by then and that roll is
            // the better value; only overwrite it when the save actually carried one.
            if (toFire > 0)
            {
                ticksToFireField.SetValue(__instance, toFire);
            }
            ticksPassedField.SetValue(__instance, passed);
        }

        private static void Warn(string what)
        {
            Log.Warning(Tag + what + ". The debris-event timer therefore stays "
                        + "unscribed behind a static that survives reloads, and the "
                        + "event will fire on one machine only once "
                        + "USH_GlittertechFabrication is researched. Re-check "
                        + "GlittertechExpansion.dll against Patches.cs.");
        }
    }
}
