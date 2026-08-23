# Archon Asset Inventory

An inventory of ThingDefs (plus a handful of TerrainDefs / GeneDefs, flagged as such) available in the
currently-installed RimWorld 1.6 collection that could plausibly belong in an **Archon** questline —
either as **loot** in an Archon ruin's reward pool, or as **set dressing** in a hand-authored Archon
ruin map.

Scanned: **64 Steam Workshop mods** (`.../workshop/content/294100`) plus the base game `Data` folder
(Core, Royalty, Ideology, Biotech, Odyssey). Anomaly is **not installed**. Only `1.6/` def folders and
version-less def folders were read; `1.0`–`1.5` folders were ignored throughout.

Every `defName` below was read out of an actual XML file. Where a def is *not* a ThingDef it is marked
inline. Note that two different mods both use the `VREA_` prefix (Vanilla Races Expanded – Archon and
Vanilla Races Expanded – Android); source mods are attributed individually.

---

## Relics & artifacts

| defName | label | source mod | why it fits |
|---|---|---|---|
| `RelicInertCup` | chalice | Ideology (DLC) | Inert relic series, `techLevel Archotech` on the base. Perfect "recovered from the ruin" prize with no game effect — pure lore object. |
| `RelicInertPendant` | pendant | Ideology (DLC) | As above. |
| `RelicInertBox` | box | Ideology (DLC) | As above. |
| `RelicInertTablet` | tablet | Ideology (DLC) | Tablet reads as an Archon data-slab / commandment stone. |
| `RelicInertFragment` | fragment | Ideology (DLC) | A shard of something much larger — ideal "piece of the simulation substrate". |
| `RelicInertSwordHandle` | hilt | Ideology (DLC) | Hilt of a weapon whose blade was energy — very Archon. |
| `RelicInertArk` | ark | Ideology (DLC) | Largest of the inert relics; reads as a sealed container of divine origin. |
| `RelicInertCube` | cube | Ideology (DLC) | A featureless cube is the single most "archotech artefact" shape in the game. |
| `PsychicAnimalPulser` | psychic animal pulser | Core | `ArtifactBase`, `techLevel Archotech`. One-use godlike device. |
| `PsychicSoothePulser` | psychic soothe pulser | Core | Same family; an Archon "blessing" in a can. |
| `AIPersonaCore` | AI persona core | Core | Literally a fragment of a mind of an archotech-adjacent intelligence. Top-tier ruin prize. |
| `TechprofSubpersonaCore` | techprof subpersona core | Core | A subpersona — an Archon shard that *teaches*. Excellent quest reward. |
| `USH_PhilosophersStone` | philosopher's stone | Ushankas Glittertech Expansion | Name and concept are already "divine + impossible tech". |
| `USH_Glitterheart` | glitterheart | Ushankas Glittertech Expansion | MarketValue 1200 uncraftable-tier resource; reads as a reactor-heart relic. |
| `USH_Glittercore` | glittercore | Ushankas Glittertech Expansion | Refined exotic matter; good bulk treasure for a hoard. |
| `Gravitonium` | gravitonium | GravTech | `techLevel Ultra` exotic matter — the substance the ruin is built out of. |
| `Gravcore` | gravcore | Odyssey (DLC) | MarketValue 1250 spacer artefact; the thing the ruin's engines still run on. |
| `EmptyAICore` | empty AI persona core | GravTech | An *emptied* persona core is a fantastic story object: something left the ruin. |
| `DankPyon_Building_AncientCodex` | ancient codex | Medieval Overhaul | Lootable building-as-treasure. Reads as an Archon scripture. |
| `DankPyon_Building_SkullEmerald` | emerald skull | Medieval Overhaul | Gem-carved skull — uncanny reliquary object for a shrine niche. |
| `DankPyon_Building_SkullSapphire` | sapphire skull | Medieval Overhaul | As above. |
| `DankPyon_Building_SkullRuby` | ruby skull | Medieval Overhaul | As above. |
| `DankPyon_Building_SkullGold` | gold skull | Medieval Overhaul | As above. |
| `DankPyon_Building_ChaliceGold` | golden chalice | Medieval Overhaul | Altar-top offering vessel. |
| `DankPyon_CultOrb` | ancient orb | Medieval Overhaul | Glowing green sphere on a granite pedestal, described as pulsing with otherworldly energy, and it is a *quest linkable*. Probably the single best "the Archons left this here" prop in the collection. |

## Archotech devices & impossible machinery

| defName | label | source mod | why it fits |
|---|---|---|---|
| `ArchonexusCore` | archonexus core | Ideology (DLC) | The canonical archotech megastructure heart. If the ruin has a centre, this is it. |
| `GrandArchotechStructure` | grand archotech structure | Ideology (DLC) | Huge, unbuildable, alien-geometry structure. Pure Archon architecture. |
| `MajorArchotechStructure` | major archotech structure | Ideology (DLC) | Mid-size variant; use several to build a complex. |
| `MajorArchotechStructureStudiable` | (studiable variant) | Ideology (DLC) | Same visual but interactable — lets a pawn *study* the ruin. Ideal quest objective. |
| `ArchotechTower` | archotech tower | Ideology (DLC) | Vertical landmark; good silhouette for a ruin skyline. |
| `PsychicEmanator` | psychic emanator | Core | Uncraftable archotech artefact building that radiates wellbeing — an Archon "grace field". |
| `VanometricPowerCell` | vanometric power cell | Core | Free energy forever; explicitly described as archotech-built. |
| `InfiniteChemreactor` | infinite chemreactor | Core | Matter from nothing. Perfect Archon miracle-machine. |
| `VFE_SmallVanometricPowerCell` | small vanometric power cell | Vanilla Furniture Expanded - Power | Description explicitly says "developed by archotechs". |
| `VFE_LargeVanometricPowerCell` | large vanometric power cell | Vanilla Furniture Expanded - Power | As above, larger footprint for a reactor hall. |
| `VPE_ArchotechViolenceGenerator` | archotech violence generator | Vanilla Furniture Expanded - Power | Harvests psychic energy from dying humanoids. Horrifying, godlike, and named "archotech". |
| `USH_MountainRaiser` | mountain raiser | Ushankas Glittertech Expansion | A machine that raises stone out of the ground. Terraforming-as-casual-act = Archon. |
| `USH_MolecularDisassembler` | molecular disassembler | Ushankas Glittertech Expansion | Matter deconstruction bench; reads as ruin industry. |
| `USH_Telepad` | telepad | Ushankas Glittertech Expansion | Teleportation. Ideal "gate" prop between ruin sections. |
| `USH_MemoryPylon` | memory pylon | Ushankas Glittertech Expansion | Pylon that projects memories — extremely on-theme for a simulation-builder civilisation. |
| `USH_SolarFlareBank` | solar flare bank | Ushankas Glittertech Expansion | Weather control. |
| `USH_NeuroclearConsole` | Neuroclear console | Ushankas Glittertech Expansion | Mind-editing console. |
| `USH_ResearchProbe` | research probe | Ushankas Glittertech Expansion | Passive knowledge generation — a thinking machine still running. |
| `USH_GlittertechFabricator` | glittertech fabricator | Ushankas Glittertech Expansion | Ruin workshop centrepiece. |
| `USH_GlittertechRepairer` | glittertech repairer | Ushankas Glittertech Expansion | Self-repairing machinery — the ruin maintains itself. |
| `AdvShip_GravReactor` | The Singularity Reactor | GravTech | MarketValue 25000, the highest-value building found anywhere in the collection. A contained singularity is the perfect Archon power source. |
| `AdvShip_ComputerCore` | advanced gravship computer core | GravTech | MarketValue 15000. |
| `AdvShip_TimeFasterPod` | time acceleration pod | GravTech | Localised time dilation. Reality-editing tech. |
| `GravForge` | grav forge | GravTech | Can *copy an AI persona core* — mind duplication as a factory process. |
| `GravFieldPylon` | grav field pylon | GravTech | Field-projecting pylon; good for ringing a ruin plaza. |
| `AncientTerraformer` | ancient terraformer | Odyssey (DLC) | Ancient, gravcore-powered, malfunctioning, and it changes the *climate*. Excellent quest engine. |
| `AncientGravReactor` | ancient grav reactor | Odyssey (DLC) | Leaking containment shield — set dressing that hurts you. |
| `AncientGravEngine` | ancient grav engine | Odyssey (DLC) | Ultratech engine that lifted whole structures into orbit. |
| `CerebrexCore` | cerebrex core | Odyssey (DLC) | A planet-scale thinking mind with an AI persona core at its heart. The closest vanilla analogue to an Archon intelligence. |
| `CerebrexCore_Destroyed` | destroyed cerebrex core | Odyssey (DLC) | The *dead god* version — ideal centrepiece for a ruin. |
| `CerebrexStabilizer` | cerebrex stabilizer | Odyssey (DLC) | Remote invincibility field. Great multi-objective ruin layout. |
| `MechRelay` | mechanoid relay | Odyssey (DLC) | Planet-wide signal node. |
| `MechRelay_Crashed` | crashed mechanoid relay | Odyssey (DLC) | Broken variant for derelict maps. |
| `MechStabilizer` | relay stabilizer | Odyssey (DLC) | Shield projector guarding the above. |
| `VFES_LargeRepulsor` | large repulsor | Vanilla Furniture Expanded - Security | `techLevel Ultra` field projector; huge invisible dome. Good "the ruin is still defended" beat. |
| `VFES_SmallRepulsor` | small repulsor | Vanilla Furniture Expanded - Security | As above, room-scale. |
| `VFED_ImperialMegaHighShield` | imperial mega high-shield | Vanilla Factions Expanded - Deserters | Enormous shield dome; visually reads as ancient force-field infrastructure. |
| `VFED_ZeusCannon` | zeus cannon | Vanilla Factions Expanded - Deserters | God-named artillery piece; great as a ruined emplacement. |
| `VFED_Techprinter` | techprinter | Vanilla Factions Expanded - Deserters | Knowledge-printing machine — good "the Archons taught here" prop. |

## Psychic & mind

| defName | label | source mod | why it fits |
|---|---|---|---|
| `Apparel_PsychicShockLance` | psychic shock lance | Core | `techLevel Archotech` single-use psychic weapon. Prime ruin loot. |
| `Apparel_PsychicInsanityLance` | psychic insanity lance | Core | As above, nastier. |
| `Apparel_PsychicFoilHelmet` | psychic foil helmet | Core | Cheap, but thematically it's *shielding from* the Archons. |
| `VFED_PsychicAmplifier` | psychic amplifier | Vanilla Factions Expanded - Deserters | MarketValue 2000, upgrades an existing psylink. Excellent tiered quest reward. |
| `AnimusStone` | animus stone | Royalty (DLC) | MarketValue 5000 uncraftable psychic focus monolith. Reads perfectly as an Archon meditation node. |
| `Plant_TreeAnima` | anima tree | Royalty (DLC) | Psychically-linked tree; unnatural natural feature for an outdoor Archon shrine. |
| `Plant_TreeGauranlen` | gauranlen tree | Ideology (DLC) | As above, with dryad spawning — a living machine. |
| `NatureShrine_Large` | large nature shrine | Royalty (DLC) | Meditation focus; usable as an Archon "reflection point". |
| `NatureShrine_Small` | small nature shrine | Royalty (DLC) | As above. |
| `PsychicDroner` | psychic droner | Royalty (DLC) | Condition causer building — a ruin that broadcasts madness. |
| `PsychicSuppressor` | psychic suppressor | Royalty (DLC) | Ruin that dampens psychic ability — inverse flavour. |
| `PsychicDronerShipPart` | ship part (psychic droner) | Core | Crashed archotech-derived hardware, already coded as an assault objective. |
| `Apparel_PsyfocusRobe` | eltex robe | Royalty (DLC) | Eltex line is `techLevel Ultra`; robes read as priestly Archon vestments. |
| `Apparel_PsyfocusHelmet` | eltex helmet | Royalty (DLC) | As above. |
| `Apparel_EltexSkullcap` | eltex skullcap | Royalty (DLC) | As above. |
| `Apparel_PsyfocusVest` | eltex vest | Royalty (DLC) | As above. |
| `Apparel_PsyfocusShirt` | eltex shirt | Royalty (DLC) | As above. |
| `VREA_PsychicStorm` (WeatherDef + IncidentDef) | psychic storm | Vanilla Races Expanded - Archon | Not a ThingDef — a bespoke *weather* for Archon presence. Strongly recommended for the ruin map itself. |
| `VRE_Transcendent` (GeneDef) | transcendent | Vanilla Races Expanded - Archon | Archite gene. Loot as a genepack. |
| `VRE_InnatePsylink` (GeneDef) | natural psylink | Vanilla Races Expanded - Archon | Archite gene; born-psychic. |
| `VRE_PsychicAbility_MoreExtreme` (GeneDef) | extremely psy-sensitive | Vanilla Races Expanded - Archon | Archite gene. |

## Statues, idols, monuments & obelisks

| defName | label | source mod | why it fits |
|---|---|---|---|
| `DankPyon_ArchonSculpture2x2c` | grand archon sculpture | Medieval Overhaul | Already *named* archon. Drop-in centrepiece idol. |
| `DankPyon_ArchonObeliskSculpture2x2c` | grand archon obelisk sculpture | Medieval Overhaul | Archon obelisk. Best single set-dressing find in the whole scan. |
| `DankPyon_Obelisk2x2c` | grand obelisk | Medieval Overhaul | Plain obelisk for ranks/avenues. |
| `DankPyon_RNG2x2c` | grand dice god obelisk sculpture | Medieval Overhaul | "Dice god" reads beautifully as a simulation-architect deity. |
| `DankPyon_RNGLarge2x2c` | grand dice god sculpture | Medieval Overhaul | As above, statue form. |
| `DankPyon_Brazier2x2c` | ancient obelisk brazier | Medieval Overhaul | Lit obelisk — light + monument in one. |
| `DankPyon_Brazier1x1c` | ancient brazier | Medieval Overhaul | Ritual fire for approach paths. |
| `DankPyon_Ancient_Column` | ancient column | Medieval Overhaul | Colonnades. |
| `DankPyon_Ruined_AncientColumn` | ancient column (ruined) | Medieval Overhaul | Broken colonnades. |
| `DankPyon_Pedestal` | pedestal | Medieval Overhaul | Empty plinth — "something was taken from here". |
| `DankPyon_CultPedestal` | ancient pedestal | Medieval Overhaul | Quest-linkable plinth; pairs with `DankPyon_CultOrb`. |
| `DankPyon_Bust` | bust | Medieval Overhaul | Faces of the departed. |
| `DankPyon_ArmorStatue` | armor statue | Medieval Overhaul | Empty armour standing sentinel. |
| `DankPyon_Lootable_ArmorStatueNamed` | named armor statue | Medieval Overhaul | Lootable variant — a guarded relic. |
| `Statue` | statue | Odyssey (DLC) | Vanilla stone statue building, stuff-able in any material. |
| `VFEE_RoyalSculptureGrand` | grand imperial sculpture | Vanilla Factions Expanded - Empire | Imposing, formal, hierarchical — good for a throne hall. |
| `VFEE_RoyalSculptureLarge` | large imperial sculpture | Vanilla Factions Expanded - Empire | As above. |
| `VFEE_RoyalSculptureSmall` | small imperial sculpture | Vanilla Factions Expanded - Empire | As above. |
| `Altar_Grand` | grand altar | Ideology (DLC) | Stuff-able altar; the obvious ritual focus of an Archon temple. |
| `Altar_Large` | large altar | Ideology (DLC) | As above. |
| `Altar_Medium` | medium altar | Ideology (DLC) | As above. |
| `Altar_Small` | small altar | Ideology (DLC) | As above. |
| `Reliquary` | reliquary | Ideology (DLC) | Purpose-built relic display case. Put a `RelicInert*` inside. |
| `DankPyon_AncientReliquary` | ancient reliquary | Medieval Overhaul | Lootable reliquary — a filled one to be opened. |
| `DankPyon_AncientReliquaryEmpty` | ancient reliquary (empty) | Medieval Overhaul | Already-looted variant, for depth. |
| `IncenseShrine` | incense shrine | Ideology (DLC) | Small smoking shrine; good ambient clutter. |
| `Skullspike` | skullspike | Ideology (DLC) | Unsettling; useful if the Archons were worshipped by someone unpleasant. |
| `MonumentMarker` | monument marker | Royalty (DLC) | Ethereal def used to lay out a monument blueprint — useful *tooling* for authoring a ruin. |
| `Urn` | urn | Core | Small ash container; quiet grief-note in a temple. |
| `Sarcophagus` | sarcophagus | Core | Formal interment. Archon tombs. |

## Ruined / derelict tech (set dressing)

| defName | label | source mod | why it fits |
|---|---|---|---|
| `VQEA_RuinedArchitePathingArray` | ruined archite pathing array | Vanilla Quests Expanded - Ancients | Explicitly *archite* machinery, ruined. The single best-matched set-dressing family available. |
| `VQEA_RuinedArchiteRecycler` | ruined archite recycler | Vanilla Quests Expanded - Ancients | As above. |
| `VQEA_RuinedArchogenInjector` | ruined archogen injector | Vanilla Quests Expanded - Ancients | As above. |
| `VQEA_RuinedTraitSelectionPrism` | ruined trait selection prism | Vanilla Quests Expanded - Ancients | Shattered crystal lens array. Gorgeous ruin prop. |
| `VQEA_RuinedComplexityHarmonizer` | ruined complexity harmonizer | Vanilla Quests Expanded - Ancients | As above. |
| `VQEA_RuinedGenomicAttenuator` | ruined genomic attenuator | Vanilla Quests Expanded - Ancients | As above. |
| `VQEA_RuinedMutagenInhibitorCore` | ruined mutagen inhibitor core | Vanilla Quests Expanded - Ancients | Massive collapsed containment engine. |
| `VQEA_RuinedNeurostabilizerArray` | ruined neurostabilizer array | Vanilla Quests Expanded - Ancients | As above. |
| `VQEA_RuinedCognitiveRecoveryArray` | ruined cognitive recovery array | Vanilla Quests Expanded - Ancients | As above. |
| `VQEA_RuinedRejectionBufferCoil` | ruined rejection buffer coil | Vanilla Quests Expanded - Ancients | As above. |
| `VQEA_RuinedSpliceframeUplink` | ruined spliceframe uplink | Vanilla Quests Expanded - Ancients | As above. |
| `VQEA_RuinedAberrationRedirector` | ruined aberration redirector | Vanilla Quests Expanded - Ancients | As above. |
| `VQEA_RuinedRapidInfusionPump` | ruined rapid infusion pump | Vanilla Quests Expanded - Ancients | As above. |
| `VQEA_BustedControlPanel` | busted control panel | Vanilla Quests Expanded - Ancients | Sparks still flicker from the shattered screen. |
| `VQEA_VaultTerminal` | vault terminal | Vanilla Quests Expanded - Ancients | Inactive but faintly flickering. |
| `VQEA_VaultTerminalBank` | vault terminal bank | Vanilla Quests Expanded - Ancients | A wall of them. |
| `VQEA_BustedAncientWonderdoc` | busted ancient wonderdoc | Vanilla Quests Expanded - Ancients | The catastrophically failed miracle-machine. |
| `VQEA_AncientVaultWall` | ancient vault wall | Vanilla Quests Expanded - Ancients | Wall material for sealed Archon interiors. |
| `VQEA_LockedAncientVaultDoor` | locked ancient vault door | Vanilla Quests Expanded - Ancients | Gating a ruin's inner sanctum. |
| `VQEA_LockedAncientVaultDoor_Large` | locked ancient large vault door | Vanilla Quests Expanded - Ancients | Monumental version. |
| `VQEA_LockedVaultDoor` | sealed vault door | Vanilla Quests Expanded - Ancients | Entrance seal. |
| `VQEA_VaultRamp` | vault ramp | Vanilla Quests Expanded - Ancients | Descent into the ruin. |
| `AncientMegaCannonTripod` | (ancient mega cannon tripod) | Core | Wreckage at a scale humans never built. |
| `AncientMegaCannonBarrel` | (ancient mega cannon barrel) | Core | As above. |
| `AncientWarwalkerTorso` | (warwalker torso) | Core | Colossal fallen war machine. |
| `AncientWarwalkerLeg` | (warwalker leg) | Core | As above. |
| `AncientWarwalkerClaw` | (warwalker claw) | Core | As above. |
| `AncientWarwalkerFoot` | (warwalker foot) | Core | As above. |
| `AncientWarwalkerShell` | (warwalker shell) | Core | As above. |
| `AncientExostriderRemains` | ancient exostrider remains | Biotech (DLC) | Enormous mech corpse with a red pulse effecter. Great skyline silhouette. |
| `AncientExostriderHead` | ancient exostrider head | Biotech (DLC) | As above. |
| `AncientExostriderLeg` | ancient exostrider leg | Biotech (DLC) | As above. |
| `AncientExostriderCannon` | ancient exostrider cannon | Biotech (DLC) | As above. |
| `AncientSystemRack` | ancient system rack | Core | Server racks; the ruin was a *computer*. |
| `AncientDisplayBank` | ancient display bank | Core | Wall of dead screens. |
| `AncientMachine` | ancient machine | Core | Generic but unbuildable-tier machinery. |
| `AncientDestroyedConsole` | (destroyed console) | Odyssey (DLC) | Smashed control surface. |
| `AncientDestroyedConsoleLarge` | (destroyed console, large) | Odyssey (DLC) | As above. |
| `AncientBlastDoor` | ancient blast door | Odyssey (DLC) | Ultratech polymer door, hackable. |
| `AncientFortifiedWall` | fortified wall | Odyssey (DLC) | Ultratech polymer wall — build the ruin shell out of it. |
| `AncientSecurityTerminal` | ancient security terminal | Odyssey (DLC) | Hackable objective prop. |
| `AncientHatch` | ancient stockpile entrance | Odyssey (DLC) | Hatch into a pocket-map sublevel. Structurally ideal for a layered Archon ruin. |
| `AncientHatchExit` | ancient stockpile exit | Odyssey (DLC) | The paired ladder back up. |
| `AncientTunnelerHusk` | ancient tunneler husk | Odyssey (DLC) | Vast boring machine, dead. |
| `AncientTunnelerClaw` | ancient tunneler claw | Odyssey (DLC) | As above. |
| `AncientExcavator` | ancient excavator | Odyssey (DLC) | As above. |
| `AncientDrillPlatform` | ancient drill platform | Odyssey (DLC) | As above. |
| `VFED_FlagshipChunk` | flagship chunk | Vanilla Factions Expanded - Deserters | Fallen capital-ship debris. |
| `USH_GlittershipChunk` | glitterworld debris | Ushankas Glittertech Expansion | Impossible-tech wreckage with its own pulse effecters and ambience sound. |
| `VQEA_DestroyedGravExtender` | destroyed grav field extender | Vanilla Gravship Expanded - Ch.1 | Broken gravitic hardware. |
| `VQEA_DestroyedLargeThruster` | destroyed large thruster | Vanilla Gravship Expanded - Ch.1 | As above. |
| `VQEA_DestroyedSmallThruster` | destroyed small thruster | Vanilla Gravship Expanded - Ch.1 | As above. |
| `VQEA_DestroyedSmallHeatsink` | destroyed small heatsink | Vanilla Gravship Expanded - Ch.1 | As above. |
| `VGE_MechanoidGravEngine` | mechanoid grav engine | Vanilla Gravship Expanded - Ch.1 | Non-human engine design. |
| `VGE_MassDriver` | mass driver | Vanilla Gravship Expanded - Ch.1 | Orbital-scale weapon emplacement. |
| `VGE_HeavyChargeAnnihilator` | heavy charge annihilator | Vanilla Gravship Expanded - Ch.1 | As above. |
| `ShipChunk` | ship chunk | Core | Cheap filler debris. |
| `ChunkMechanoidSlag` | (mechanoid slag chunk) | Core | Cheap filler debris. |

## Containers & lootables

| defName | label | source mod | why it fits |
|---|---|---|---|
| `AncientHermeticCrate` | ancient hermetic crate | Core | Sealed since before recorded history; has its own opening sound. |
| `AncientCryptosleepPod` | ancient cryptosleep pod | Core | Someone is still inside. Best single narrative container in the game. |
| `AncientSealedContainer` | ancient sealed container | Odyssey (DLC) | Openable reward container. |
| `AncientSealedContainer_GravshipUpgrade` | (sealed container, upgrade) | Odyssey (DLC) | Rewards a gravship upgrade — a gift from the builders. |
| `AncientSealedCrate` | ancient sealed crate | Odyssey (DLC) | Openable reward container. |
| `AncientSealedCrate_Gravlite` | (sealed crate, gravlite) | Odyssey (DLC) | Yields exotic panelling. |
| `AncientSafe` | ancient safe | Odyssey (DLC) | Hackable high-value container. |
| `VQEA_ArchiteCapsuleContainment` | archite capsule containment | Vanilla Quests Expanded - Ancients | "Still hums softly when approached", releases an archite capsule. Ideal Archon reliquary-as-loot-container. |
| `VQEA_ArchiteCapsuleContainment_Empty` | archite capsule containment (empty) | Vanilla Quests Expanded - Ancients | Already-emptied variant for storytelling. |
| `VQEA_AncientGenepackCrate` | ancient genepack crate | Vanilla Quests Expanded - Ancients | Hackable — yields genepacks. |
| `VQEA_AncientOrganBox` | ancient organ box | Vanilla Quests Expanded - Ancients | Cooled organ storage; unsettling. |
| `USH_Glittercrate` | glitterworld crate | Ushankas Glittertech Expansion | Sky-delivered impossible-tech crate; has a dedicated reward def (`USH_RewardGlittercrate`). |
| `DankPyon_LootableChest_RoyalChest` | royal chest | Medieval Overhaul | Ornate treasure chest. |
| `DankPyon_CultShelf` | explorer's archive | Medieval Overhaul | Archive shelving for a lore room. |
| `VFED_BiosecuredCrate` | biosecured crate | Vanilla Factions Expanded - Deserters | Sterile, sealed, official-looking. |
| `AncientLockerBank` | ancient locker bank | Core | Filler storage. |
| `AncientSpacerCrate` | ancient spacer crate | Core | Filler storage. |

## Genetic material & archite

| defName | label | source mod | why it fits |
|---|---|---|---|
| `ArchiteCapsule` | archite capsule | Biotech (DLC) | Archite nanomachines in a jar. Canonically archotech-made. The definitive Archon consumable. |
| `Genepack` | genepack | Biotech (DLC) | Container for Archon gene sets (see `VRE_*` genes above). |
| `Xenogerm` | xenogerm | Biotech (DLC) | Pre-assembled Archon genetics as one-shot loot. |
| `HumanEmbryo` | embryo | Biotech (DLC) | Preserved Archon lineage in a ruin nursery. |
| `HumanOvum` | ovum | Biotech (DLC) | As above. |
| `VRE_Archon` (XenotypeDef) | archon | Vanilla Races Expanded - Archon | The xenotype itself — use for ruin-guardian pawns and for genepack contents. |
| `VRE_LeapjumpLegs` (GeneDef) | leapjump legs | Vanilla Races Expanded - Archon | Archite-tier movement gene. |
| `VQEA_ArchogenInjector` | archogen injector | Vanilla Quests Expanded - Ancients | Working archite injection pod, MarketValue 1450. The functional centrepiece of an Archon gene-lab. |
| `VQEA_ArchitePathingArray` | archite pathing array | Vanilla Quests Expanded - Ancients | Working version, MarketValue 1565. |
| `VQEA_TraitSelectionPrism` | trait selection prism | Vanilla Quests Expanded - Ancients | Crystalline multi-lens console that splits outcomes into "selectable possibility streams" — reads directly as simulation-authoring hardware. |
| `VQEA_MutagenInhibitorCore` | mutagen inhibitor core | Vanilla Quests Expanded - Ancients | Massive tri-core containment engine. |
| `VQEA_ComplexityHarmonizer` | complexity harmonizer | Vanilla Quests Expanded - Ancients | Working version. |
| `VQEA_ArchiteRecycler` | archite recycler | Vanilla Quests Expanded - Ancients | Working version. |
| `VQEA_GenomicAttenuator` | genomic attenuator | Vanilla Quests Expanded - Ancients | Working version. |
| `VQEA_AberrationRedirector` | aberration redirector | Vanilla Quests Expanded - Ancients | Working version. |
| `VQEA_SpliceframeUplink` | spliceframe uplink | Vanilla Quests Expanded - Ancients | Working version. |
| `VQEA_NeurostabilizerArray` | neurostabilizer array | Vanilla Quests Expanded - Ancients | Working version. |
| `VQEA_CognitiveRecoveryArray` | cognitive recovery array | Vanilla Quests Expanded - Ancients | Working version. |
| `VQEA_RejectionBufferCoil` | rejection buffer coil | Vanilla Quests Expanded - Ancients | Working version. |
| `VQEA_RapidInfusionPump` | rapid infusion pump | Vanilla Quests Expanded - Ancients | Working version. |
| `SubcoreRipscanner` | (subcore ripscanner) | Biotech (DLC) | Destructively copies a mind. Deeply Archon-adjacent horror. |

## Implants, bionics & serums

| defName | label | source mod | why it fits |
|---|---|---|---|
| `ArchotechEye` | archotech eye | Core | `techLevel Archotech`, MarketValue 2800. Cannot be crafted — only found. Textbook ruin loot. |
| `ArchotechArm` | archotech arm | Core | As above. |
| `ArchotechLeg` | archotech leg | Core | As above. |
| `MechSerumHealer` | healer mech serum | Core | Uncraftable miracle cure. |
| `MechSerumResurrector` | resurrector mech serum | Core | Raises the dead. Nothing says "godlike" louder. |
| `Luciferium` | luciferium | Core | Archotech-mechanite drug with a permanent hook. Great cursed-gift loot. |
| `USH_Glitterlink` | glitterlink | Ushankas Glittertech Expansion | `techLevel Ultra` neural implant. |
| `USH_MemoryProjector` | memory projector | Ushankas Glittertech Expansion | Implant that replays memories — on-theme for a simulation civilisation. |
| `USH_CryogenicNexus` | cryogenic nexus | Ushankas Glittertech Expansion | Ultra-tier implant. |
| `USH_TelepadIntegrator` | telepad integrator | Ushankas Glittertech Expansion | Personal teleportation implant. |
| `USH_GoldenSkinReplacement` | golden skin replacement | Ushankas Glittertech Expansion | Gold-skinned ascendants — strong visual language for Archon-touched pawns. |
| `USH_PlasteelSkinReplacement` | plasteel skin replacement | Ushankas Glittertech Expansion | As above, colder variant. |
| `USH_GoldenTeethReplacement` | golden teeth replacement | Ushankas Glittertech Expansion | Cosmetic ascendancy marker. |
| `USH_PlasteelTeethReplacement` | plasteel teeth replacement | Ushankas Glittertech Expansion | As above. |
| `USH_GammaSerum` | gamma serum | Ushankas Glittertech Expansion | `techLevel Ultra` drug. |
| `USH_Shimmertalk` | shimmertalk | Ushankas Glittertech Expansion | `techLevel Ultra` social drug. |
| `USH_AddictionRemover` | addiction remover | Ushankas Glittertech Expansion | `techLevel Ultra` — a machine-god undoing a human flaw. |
| `USH_MemoryCellPositive` | memory cell | Ushankas Glittertech Expansion | Stored memories as physical loot. Extremely usable for lore delivery. |
| `USH_MemoryCellNegative` | memory cell | Ushankas Glittertech Expansion | The bad memories. |
| `USH_MemoryCellEmpty` | memory cell (empty) | Ushankas Glittertech Expansion | Blank medium. |
| `GravSpine` | grav spine | GravTech | MarketValue 2300 exotic prosthetic. |
| `GravArmor` | grav armor | GravTech | Subdermal field armour. |
| `GravHands` | grav hands | GravTech | MarketValue 3600. |
| `GravStomach` | gravcore stomach | GravTech | Body powered by a gravcore. |
| `VREA_PersonaSubcore` | persona subcore | Vanilla Races Expanded - Android | MarketValue 2000. A bottled mind. |
| `SubcoreHigh` | high subcore | Biotech (DLC) | MarketValue 1000. |
| `NanostructuringChip` | nano structuring chip | Biotech (DLC) | MarketValue 1500 uncraftable mech component. |
| `PowerfocusChip` | powerfocus chip | Biotech (DLC) | MarketValue 1000 uncraftable mech component. |
| `AM_QuantumMatrixChip` | quantum matrix chip (tier 6) | Alpha Mechs | "Quantum-restructuring micro-organ", MarketValue 2200. Perfect top-tier ruin drop. |
| `AM_StellarProcessingChip` | stellar processing chip (tier 5) | Alpha Mechs | "Voidlink-focusing" micro-organ. |
| `AM_HyperLinkageChip` | hyper-linkage chip (tier 4) | Alpha Mechs | Beamcasting-band synchroniser. |
| `SentienceCatalyst` | sentience catalyst | Odyssey (DLC) | Mechanites that grant an animal a mind. Very Archon. |
| `VAEA_Apparel_RessurectorBelt` | ressurector belt | Vanilla Apparel Expanded — Accessories | `techLevel Ultra`, MarketValue 1700. Wearable resurrection. |

## Apparel & weapons

| defName | label | source mod | why it fits |
|---|---|---|---|
| `VREA_Apparel_Archoplate` | archoplate | Vanilla Races Expanded - Archon | `techLevel Archotech`, MarketValue 6250. "A suit of mystical armor created out of unidentified materials… hums with psychic energy." The single most on-theme apparel item installed. |
| `VREA_MeleeWeapon_ArchobladeBladelink` | archoblade | Vanilla Races Expanded - Archon | `techLevel Archotech`, MarketValue 6700, persona weapon, phases through armour. The definitive Archon relic weapon. |
| `MeleeWeapon_MonoSwordBladelink` | persona monosword | Royalty (DLC) | Persona weapons carry an onboard mind — an Archon shard bound into steel. |
| `MeleeWeapon_ZeusHammerBladelink` | persona zeushammer | Royalty (DLC) | As above; god-named. |
| `MeleeWeapon_PlasmaSwordBladelink` | persona plasmasword | Royalty (DLC) | As above. |
| `MeleeWeapon_MonoSword` | monosword | Royalty (DLC) | `techLevel Ultra` base version. |
| `MeleeWeapon_Zeushammer` | zeushammer | Royalty (DLC) | As above. |
| `GravHammerBladelink` | persona grav hammer | GravTech | MarketValue 5200 persona weapon that manipulates gravity. |
| `GravHammer` | grav hammer | GravTech | `techLevel Ultra`, MarketValue 4200. |
| `GravRifle` | grav rifle | GravTech | `techLevel Ultra`, MarketValue 4800. |
| `GravBlaster` | grav blaster | GravTech | `techLevel Ultra`, MarketValue 3600, shockwave on impact. |
| `GravBeamCannon` | grav beam cannon | GravTech | `techLevel Ultra`; inflicts a "spatial rip" injury. Reality-tearing weapon. |
| `Apparel_GravBelt` | grav shield belt | GravTech | `techLevel Ultra`, MarketValue 1800. |
| `Apparel_GravPack` | grav pack | GravTech | `techLevel Ultra`, MarketValue 2300. |
| `VFEE_MeleeWeapon_ToxbladeBladelink` | persona toxblade | Vanilla Factions Expanded - Empire | MarketValue 2000 persona weapon. |
| `VFEE_Apparel_ArmorAbsolver` | absolver armor | Vanilla Factions Expanded - Empire | MarketValue 3200; "absolver" carries the right religious register. |
| `OrbitalTargeterBombardment` | orbital bombardment targeter | Core | Calling fire from the sky = divine judgement. |
| `OrbitalTargeterPowerBeam` | orbital power beam targeter | Core | As above. |
| `USH_UpgradeDamage` / `USH_UpgradeRange` / `USH_UpgradeSpeed` / `USH_UpgradeStability` / `USH_UpgradeArmor` | upgrade lens (power / spotting / quickdraw / stability / piercing) | Ushankas Glittertech Expansion | Five modular "lenses" that improve a weapon. Great granular ruin loot that isn't just another gun. |

## Ambient, lights & terrain

| defName | label | source mod | why it fits |
|---|---|---|---|
| `AncientMegastructure` (TerrainDef) | ancient megastructure | Odyssey (DLC) | A *natural* terrain type representing the surface of something built at planetary scale. The best floor in the game for an Archon ruin. |
| `MechanoidPlatform` (TerrainDef) | mechanoid platform | Odyssey (DLC) | Alien, non-human decking. |
| `OrbitalPlatform` (TerrainDef) | orbital platform | Odyssey (DLC) | As above. |
| `Substructure` (TerrainDef) | gravship substructure | Odyssey (DLC) | Gravitic foundation plating. |
| `AncientTile` (TerrainDef) | ancient tile | Core | Weathered ceremonial flooring. |
| `AncientConcrete` (TerrainDef) | ancient concrete | Core | Bulk ruin surfacing. |
| `AncientBridge` (TerrainDef) | ancient bridge | Core | Spans over water/void. |
| `AncientEmergencyLight_Red` | (emergency light, red) | Odyssey (DLC) | The ruin is still alarmed about something. |
| `AncientEmergencyLight_Blue` | (emergency light, blue) | Odyssey (DLC) | Cold, inhuman illumination. |
| `AncientEmergencyLight_Green` | (emergency light, green) | Odyssey (DLC) | As above. |
| `AncientLamp` | ancient lamp | Core | Baseline ruin lighting. |
| `AncientLamppost` | ancient lamppost | Core | Outdoor ruin lighting. |
| `VQEA_AncientVaultLamp` | ancient vault lamp | Vanilla Quests Expanded - Ancients | "Emits a steady, cold light." Exactly right for interiors. |
| `VQEA_AncientSunLamp` | ancient sun lamp | Vanilla Quests Expanded - Ancients | Artificial daylight still burning underground. |
| `USH_AwareGlitterpanel` | Aware glitterpanel | Ushankas Glittertech Expansion | A panel that is *aware*. Superb creepy ambient object. |
| `USH_NeuralGlitterpanel` | neural glitterpanel | Ushankas Glittertech Expansion | Thinking wall-surface. |
| `USH_DarkGlitterpanel` | dark glitterpanel | Ushankas Glittertech Expansion | Light-absorbing panel. |
| `USH_LightGlitterpanel` | light glitterpanel | Ushankas Glittertech Expansion | Emissive panel. |
| `USH_FabricsGlitterpanel` | fabrics glitterpanel | Ushankas Glittertech Expansion | Textured variant. |
| `AncientHeatVent` | (ancient heat vent) | Odyssey (DLC) | The ruin still breathes. |
| `AncientSmokeVent` | (ancient smoke vent) | Odyssey (DLC) | As above. |
| `AncientToxVent` | (ancient tox vent) | Odyssey (DLC) | Poisonous exhalation. |
| `LifeSupportUnit` | (life support unit) | Odyssey (DLC) | Something is still being kept alive in here. |
| `GeothermalVent` | (geothermal vent) | Odyssey (DLC) | Natural power tap for an outdoor ruin. |
| `MineableObsidian` | (mineable obsidian) | Odyssey (DLC) | Black glass rock; strong visual for an unnatural site. |
| `VGE_Compressed_Vacstone` | compressed vacstone | Vanilla Gravship Expanded - Ch.1 | Unnatural compressed rock. |
| `VQEA_CreepyBabyToy` | creepy baby toy | Vanilla Quests Expanded - Ancients | "Something makes it unsettling to look at." Cheap, effective horror beat. |
| `VQEA_EmptyContainment` | empty containment | Vanilla Quests Expanded - Ancients | "Whatever was inside got out long ago." |
| `VREA_PsychicStorm` (WeatherDef) | psychic storm | Vanilla Races Expanded - Archon | Custom weather tied to Archon presence — apply to the ruin map. |
| `DankPyon_Fountain2x2c` | large fountain | Medieval Overhaul | Formal plaza water feature for a temple courtyard. |

---

## Gaps

Where the current collection is thin, and what would fill it.

**1. Genuinely eldritch / reality-warping content — the largest gap.**
There is nothing installed that reads as *cosmic horror* or *unstable reality*: no void nodes, no
monoliths, no anomalous entities, no metalhorror, no unnatural darkness, no "the geometry is wrong"
props. Every "creepy" item found is merely dusty or broken.
- **Anomaly** (official DLC, 1.6-compatible) is the direct fix. It ships the void monolith, obelisks,
  gray flesh, unnatural corpses, bioferrite structures, void provocations, and a whole entity roster.
  For a civilisation that "built the universe as a simulation", Anomaly's void material is by far the
  best fit available and it is first-party, so no compatibility risk.

**2. Psycasts and psychic infrastructure.**
Royalty's five eltex garments plus two lances is the entire psychic loot pool. There are no psycast
neurotrainers, no psychic focus buildings beyond the anima tree / animus stone, and no psycaster
progression to reward.
- **Vanilla Psycasts Expanded** (`VanillaExpanded.VPsycastsE`) — confidently exists and is
  1.6-supported. Notably, the installed *Vanilla Races Expanded - Archon* mod already ships a
  `1.6/VPsycastsE/` folder defining a `VREA_Transcendent` psycaster path with `VREA_PsychicLance`,
  `VREA_PsychicThrow` and `VREA_PsychicWarp` abilities — **those Archon psycasts are dormant until
  VPE is installed.** Installing it unlocks Archon-specific content you already own.

**3. Ideology structures, relics and ritual furniture.**
Ideology itself provides only four altar sizes, one reliquary, one incense shrine and eight inert
relics. For a religion-flavoured questline that is a small vocabulary.
- **Vanilla Ideology Expanded - Memes and Structures** (`VanillaExpanded.VIEMS`) — confidently exists;
  adds a large set of ideological buildings and structures.
- **Alpha Memes** (Sarg Bjornson) — confidently exists; adds many memes plus associated ritual props.
  I have not verified its 1.6 status first-hand.

**4. Readables and lore delivery.**
The only readable ThingDefs available are Core's `Novel`, `TextBook` and `Schematic`, plus Medieval
Overhaul's `DankPyon_Building_AncientCodex` and `DankPyon_CultBook`. There is no "ancient data slate",
"recovered log" or lore-book item to seed exposition with.
- **Vanilla Books Expanded** (`VanillaExpanded.VBooksE`) — confidently exists. Whether it has a 1.6
  release, I am not certain.
- Failing that, this is cheap to author in-house: a custom `Book`-parented ThingDef with a fixed
  description is a few dozen lines of XML and will read better than any borrowed asset.

**5. Statues and monuments that are *not* medieval or imperial.**
Every good idol/obelisk found comes from Medieval Overhaul (stone, hand-carved) or VFE Empire
(baroque, gilded). There is no smooth, seamless, machine-made monumental sculpture — which is what an
archotech civilisation would actually leave behind. Ideology's `GrandArchotechStructure` /
`ArchotechTower` are the only assets with the right visual language, and there are only four of them.
- I do not know of a mod I can name with confidence that fills this specifically. Recolouring /
  restyling `DankPyon_ArchonObeliskSculpture2x2c` via a `ThingStyleDef`, or authoring 3–4 bespoke
  textures, is likely the better path.

**6. Ruin map generation tooling.**
`Vanilla Quests Expanded - Ancients` and `Ushankas Glittertech Expansion` both ship `SymbolDef`,
`StructureLayoutDef` and `TiledStructureDef` content that shows how to hand-author a site; Medieval
Overhaul has an extensive `SymbolDef` library too. These are good references to copy from.
- **Vanilla Base Generation Expanded** (`VanillaExpanded.BaseGenExpanded`) — confidently exists and is
  the framework several of these build on; worth adding if you intend to hand-author ruin layouts
  rather than place things manually.

**7. Not a gap, but a note.**
*Save Our Ship 2* is referenced by patch files in two installed mods (`Replace Stuff - Continued`,
`GravTech`) but is **not itself installed**. It carries a lot of archotech-tier content. I am not
confident about its current 1.6 status, so I am flagging rather than recommending it.
