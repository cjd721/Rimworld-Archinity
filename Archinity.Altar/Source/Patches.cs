using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using Multiplayer.API;
using RimWorld;
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
}
