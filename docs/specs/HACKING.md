# Hacking

## Purpose and scope

Implements the hacking half of
[`docs/requirements/GLITTERTECH.md`](../requirements/GLITTERTECH.md) §*Hacking Becomes a
Second Technology Front* — tiered targets, remote operation, a reward curve that keeps
adding verbs, and named campaign artifacts that unlock qualitative hacking research.
Established by
[#58](https://github.com/cjd721/Rimworld-Archinity/issues/58).

**This document owns** the intrusion loop: what a hackable target is, how a hack is
started and resolved, what a completed or detected intrusion reports, what gates which
classes of target, and the hacking-specific readout.

**Adjacent systems take over at four boundaries.**

- **Trace** — [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56) /
  [`TRACE.md`](TRACE.md) owns the number, its bands, its decay and how a hack moves it.
  This document owns only the *emission*; § *The intrusion report* is the contract
  between them, and it has now been consumed rather than merely offered.
- **The Analysis research gate** — [`RESEARCH.md`](RESEARCH.md), from
  [#67](https://github.com/cjd721/Rimworld-Archinity/issues/67) (closed; the mechanism is
  settled, the pricing is not). Artifact → research unlock is entirely that mechanism; this
  document consumes it and adds nothing. **Whether Analysis is priced in Intel is open**, and
  it moves this document's cost — see § *Outstanding decisions*.
- **Cross-cutting campaign UI** —
  [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61). A main tab, a political
  surface or a shared pressure readout is theirs. A per-target or per-hacker hacking
  readout is here.
- **Intel as a currency** — [`CURRENCIES.md`](CURRENCIES.md). Hacking *produces* data
  items; what they are worth and what spends them is not settled here.

---

## The build

**Ushanka's Hacking Expansion carries the front.** `Ushanka.HackingExpansion`, workshop
`3573344880`, 1.6-only, `1.6/Assemblies/HackingExpansion.dll`, depending on Harmony and
VEF. It is a **verified available mechanism** for tiered targets, remote operation,
mid-map faction flip, a data-extraction economy and an extensible verb set. We do not
write a hacking system; we write an Ultra rung on top of it, plus the two things it does
not carry — a cross-map relay and a Trace emission.

Everything below marked *(reuse)* already exists and runs. Everything marked *(new)* is
ours.

### Targets and the hackable set *(reuse)*

A hackable thing is a `Thing` carrying `RimWorld.CompHackable`. Vanilla supplies the
whole state machine: `progress`, a public `defence`, `Hack(amount, hacker,
suppressMessages)`, a lockout with a permanent variant, and `IsHacked` **[V]**.

Ushanka attaches the comps **in code, not XML**. `USH_HE.Patch_DefOfHelper_RebindAllDefOfs`
is a postfix on `Verse.DefOfHelper.RebindAllDefOfs` that walks `DefDatabase<ThingDef>` and
`DefDatabase<PawnKindDef>` and appends **[V]**:

| Condition | Comps appended | Gate |
|---|---|---|
| any `ThingDef` already carrying `CompHackable` (`ShouldBeDataSource`) | `CompProperties_DataSourceProtected` | **none — ungated by any setting** |
| a turret `ThingDef` — has `building.turretGunDef`, no `CompMannable`, no `CompInteractable`, no `CompHackable`, and has `CompPowerTrader` **or** is EMP-stunnable | `CompProperties_TurretHackable` + `CompProperties_DataSourceProtected` | `HE_Mod.Settings.EnableTurretsHacking` |
| a mechanoid or drone `PawnKindDef` (`race.race.IsMechanoid \|\| IsDrone`), not already hackable | `CompProperties_MechanoidHackable` + `CompProperties_DataSourceProtected` | `HE_Mod.Settings.EnableMechHacking` |

`defence` is derived, not authored: a turret's from its `CostList` market value (or
`building.combatPower * 2.5`), a mech's from `combatPower * baseBodySize + 80`, both
×60 ticks **[V]**. **Glitterite hack difficulty therefore falls out of Glitterite cost
for free, with nothing to author.**

**The base the injector runs against is small: twelve `ThingDef`s ship with
`CompProperties_Hackable`, and all twelve are Ideology or Odyssey content** — **Core,
Royalty and Biotech ship zero** **[V]**. Anything hackable in a Core-plus-Royalty-plus-Biotech
set exists only because Ushanka's injector put it there. One def that a substring search
returns and that is **not** in the twelve: `CerebrexStabilizer` carries
`CompProperties_HackableEffecter`, a `CompProperties_EffecterBase` — a different type with a
different base, not a `CompHackable` carrier **[V]**. Any counting pass over this set must
match the type, not the substring `Hackable`.

Three consequences bind everything downstream and are easy to miss:

1. **No XML anywhere declares `CompProperties_TurretHackable` or
   `CompProperties_MechanoidHackable`** — a corpus-wide sweep of both roots finds zero
   **[I]** (a sweep is a string result, not a read). A `PatchOperation` written against
   those comps matches nothing, and a zero match is not a loud failure the way a
   misauthored one is. **This is not T-03** — T-03 is the *over*-match case, an xpath
   applying to the whole merged database; the register carries no entry for the zero-match
   case and none is claimed here. Def-side work must target `CompHackable`, or run after
   the injector.
2. **Turret and mech injection are gated on `HE_Mod.Settings`; the data-source append is
   not** — see § *Persistence and multiplayer*, which is where that becomes a hazard
   rather than a note. The asymmetry matters: pinning both settings makes the second and
   third rows agree between clients and does **nothing** about the first, which fires on
   every `CompHackable` def whenever Ushanka is loaded at all.
3. **`CompProperties_DataSourceProtected` therefore lands on every hackable thing in the
   game**, ours included, without anyone opting in. Every `CompHackable` def the campaign
   authors inherits a hackset and an outcome table by default.

### Tiering *(reuse, with one patch)*

`USH_HE.HacksetDef` is a plain `Def` — `minDefense`, `weight`, `stealthMultiplier`,
`List<HackingOutcomeDef> hackingOutcomes`. Four ship: outdated firewall (200), ICE
(6000), core-command ICE (30000), black ICE (30000, `stealthMultiplier 0.4`) **[V]**.
`CompDataSourceProtected` picks one at `PostSpawnSetup` and applies its outcomes to the
*hacker* as the hack runs.

**We add two Ultra bands** above black ICE — Glitterite protocol and Archon ICE — as
pure XML.

**One patch is required, and it is not optional.**
`USH_HE.CyberUtils.GetHacksetDef` selects
`Where(d => compHackable.Props.defence > d.minDefense)` and then
`RandomElementByWeight(d => d.weight)` **[V]**. It does **not** take the highest band the
target qualifies for — it rolls weighted-randomly across *every* band the target
qualifies for, so a Glitterite reactor can come up "outdated firewall". Adding Ultra
bands without fixing this makes Ultra targets *more* random, not harder. A Harmony
postfix on `GetHacksetDef` returning the highest qualifying `minDefense` (falling back to
the shipped roll below an authored threshold) is ~15 lines.

### Gating target classes by research *(new)*

The requirement is that *research* opens classes of target — defenses, then reactors,
then low-tier mechs, then strong mechs, then androids. Ushanka gates on **target
hardness only**; nothing reads the research state **[V]**. This is the second patch.

- A `DefModExtension` — `Arch_HackTargetClassExtension { HackTargetClass targetClass; }` —
  is added to target defs by XML.
- A postfix on `RimWorld.CompHackable.CanHackNow(Pawn)` returns
  `"Arch_HackClassNotUnderstood".Translate()` when the class's mapped
  `ResearchProjectDef` is unfinished.
- **The display is free.** `CanHackNow`'s `AcceptanceReport.Reason` is already rendered in
  three places: the float-menu refusal, `CompHackable`'s inspect string, and the targeter
  mouse label — `USH_HE.Hediff_Cyberlink.DoTargeting` prints
  `"CannotChooseHacker" + ": " + reason` in red under the cursor **[V]**.

~40 lines. Ushanka already postfixes the same method
(`USH_HE.Patch_CompHackable_CanHackNow`), so the shape is proven in place.

### New verbs *(reuse)*

The verbs are `USH_HE.Ability_Cyber` subclasses on VEF's ability system — eight ship:
Disarm, Discharge, ForkBomb, HijackSubcore, ShortCircuit, VirtualDataRipper,
VirtualICEBreaker, Zapcode **[V]**. Their range is `pawn.GetRemoteHackRadius()`, so they
inherit the remote seam automatically.

They are **learned by hacking**, not bought: `USH_HE.Hediff_LearningAbility` accumulates
hack work and, at `learningPoints`, removes itself and calls
`CompAbilities.GiveAbility(ext.abilityDef)` with a letter **[V]**. The hediff is installed
by a `USH_ExecData_*` item recovered from a protected data source.

**That is the requirement's "named campaign artifacts unlock qualitative hacking research"
already built.** Our Ultra rung re-gates the eight shipped verbs behind Glitterite
ExecData items and Ultra research — **new verbs at zero code cost**. A genuinely novel
verb (disable a facility's defence grid as one act) is a new `Ability_Cyber` subclass at
~30–60 lines each; none is required for the ladder to work.

### Turning a hostile thing friendly, mid-map *(reuse)*

**Vanilla ships this already, and ships it remotely.** `RimWorld.CompAncientSecurityTerminal.OnHacked` — Odyssey's `AncientSecurityTerminal` — on completion gathers every un-hacked `AncientBlastDoor` and `Turret_AncientArmoredTurret` **on the map**, picks one weighted 0.75 turret / 0.25 door, and — when the pick `is Building_Turret` **and** `hacker != null` **and** `Rand.Chance(0.5f)` — calls `comp.parent.SetFaction(hacker.Faction)` and unfogs it; otherwise it hacks the pick to disabled, with three distinct letters **[V]**. **All three conditions gate the seizure**: a null hacker takes the disable branch, which is why a copy of this shape must decide what it does when nobody is attributable.

That is *hack here, effect there*, in base `Assembly-CSharp`. It is the shipped mechanism this design copies with **two pieces replaced — targeted instead of random, research-gated instead of a coin flip** — and it is the reference implementation for the `SetFactionDirect` defect in § *Failure and recovery*.

On top of it, Ushanka adds two mechanisms, and the difference between them matters **[V]**:

- **Turret** — `USH_HE.CompTurretHackable.OnHacked` calls
  `parent.SetFactionDirect(hacker.Faction)`, resets the hack progress, and wakes any
  `CompCanBeDormant`. One hack, permanent flip, no ability needed.
- **Mechanoid** — `USH_HE.CompMechanoidHackable.OnHacked` does **not** flip faction. It
  applies the `USH_Disabled` hediff. Seizing it is a *second* act: the
  `USH_HijackSubcore` ability, whose `Ability_HijackSubcore.Cast` calls
  `mech.SetFaction(Faction.OfPlayer)` and removes `USH_Disabled`, and which refuses any
  target not already `USH_Disabled`.

So *"a mission that once required killing every defender may later allow seizing a
mechanoid"* is a two-step the player earns: hack to disable, then hijack to own. That is
better than the requirement asked for and we should not flatten it.

**`SetFactionDirect` on the turret path is a defect we inherit** — see
§ *Failure and recovery*.

### The cross-map relay *(new — the one genuine absence)*

The requirement: *"Field pawns can carry remote-hacking equipment that allows skilled
hackers at home to operate through them."*

What exists **[V]**:

- **Stat radius.** `USH_RemoteHackingDistance`, default 0, raised by the
  `USH_RemoteAccessPort` implant to 7.9 / 13.9 / 19.9 cells.
  `USH_HE.JobDriver_RemoteHack` walks the hacker to within that radius instead of to the
  target, and `USH_HE.Patch_CompHackable_CanHackNow` / `_ValidateHacker` let the
  `"NoPath"` rejection through for a pawn who can hack remotely. **This is the same pawn
  standing further away.**
- **The Cyberpod.** `USH_HE.Building_Cyberpod` is a `Building_Casket` holding one pawn
  with a cyberlink. `MapComponent_CyberpodManager.GetAllHackables` enumerates
  `map.mapPawns.AllPawnsSpawned` plus both `listerBuildings` lists, and
  `Building_Cyberpod.CanBeHacked` imposes **no distance check at all** — only `Fogged()`
  and a black-ICE refusal. A sealed colonist at base hacks anything unfogged **on its own
  map, at unlimited range**, consuming fuel and power.

**The gap is exactly one word: map.** On a Charting away-site the home hacker cannot
participate, because `MapComponent_CyberpodManager`'s `map` is the pod's own.

**The build moves the statistics, not the job.** The field pawn performs the hack — it is
on the target's map, so every reservation, path, job and tick stays local and stays
MP-safe. A relay item in its inventory names a home hacker, and two `StatPart`s
substitute the home hacker's numbers:

| Piece | What it does |
|---|---|
| `Arch_HackRelay`, a new `ThingDef` carrying `CompProperties_HackRelay` | holds a scribed `Pawn` reference to the home hacker; one gizmo to choose them; valid only while the home hacker is inside a `Building_Cyberpod` on a player home map |
| `Archinity.Core.StatPart_HackRelay`, registered by `PatchOperationAdd` on **both** `HackingSpeed` and `HackingStealth` | `TransformValue` returns the linked home hacker's value when the carrier holds an active relay; `ExplanationPart` says *"operating through &lt;pawn&gt;"* |

Why a `StatPart` and not a Harmony patch on the job: **every** consumer picks it up with
no further work — vanilla `JobDriver_Hack`, Ushanka's `JobDriver_RemoteHack`, the
Cyberpod's own `Hack()`, and vanilla's lockout roll, which reads
`hacker.GetStatValue(StatDefOf.HackingStealth)` *inside* `CompHackable.Hack` where a job
patch could not reach it **[V]**. It is also loud: a `StatPart` shows in the pawn's stat
report with its explanation string, so the player can see the relay is live. ~80 lines
including the comp.

**The alternative, and why it is not selected.** Biotech's mechanitor system is the other
shipped shape for *operating something you are not next to*, and it is closer than it
looks: `MechanitorUtility.CanControlMech` has **no map check at all** — overseer relation
and bandwidth only **[V]**. The map boundary is enforced one level up by
`Pawn_MechanitorTracker.CanControlMechs`, which refuses an unspawned pawn and refuses one
inside a `Building` by name **[V]**; *Mechanitor Control Range Extension* (shipped inside
Mechanoids: Total Warfare) postfixes exactly that getter to re-enable control for an
off-map caravan member, which is a live precedent for the seam **[V]**. Copying it would
also give a bandwidth-style cap on simultaneous remote operations.

**What separates them: the `StatPart` build never moves a job across a map boundary and
the mechanitor build does.** The latter requires the hack *job* to run for a pawn whose
map the driver is not on — cross-map reservations, pathing and ticking — which is both the
expensive part and the multiplayer-dangerous part. Several hundred lines against ~80, for
a capacity limit the requirement does not ask for. Revisit only if it does.

**Composition marked as the method asks:** every mechanism above is **[V]**; the claim
that they compose into a working relay is **[I]** until built.

### The intrusion report *(new — the interface #56 consumes)*

See § *What #56 needs from hacking*, below. Mechanism: one `GameComponent`
(`Archinity.Core.HackIntrusionLog`), one `ThingComp` (`CompHackIntrusion`) injected
alongside Ushanka's, one Harmony postfix on `CompHackable.LockOut`. ~70 lines.

**No Harmony patch is needed for the success case.** `CompHackable.ProcessHacked` calls
`OnHacked`, and `OnHacked` broadcasts `foreach (ThingComp allComp in parent.AllComps)
allComp.Notify_Hacked(hacker)` **near its start, not at the end of `ProcessHacked`** **[V]**;
`Verse.ThingComp.Notify_Hacked(Pawn hacker = null)` is `public virtual` **[V]**. A comp of ours on
the hacked thing is called exactly once per completed hack, with the hacker, and can read
everything else off `parent`.

**Where in `OnHacked` it fires is load-bearing for the report.** Because the broadcast is early,
our comp sees `parent` **before** the rest of `OnHacked` runs — drops, graphic swap, quest signals
and any faction change have not happened yet. Read only what is already true at that moment
(`defence`, `progress`, the target's identity, the hacker); anything that is a *result* of the hack
must be read later or not at all.

### Display

| Surface | Who builds it |
|---|---|
| Per-target hack progress, hacked/locked state | vanilla `CompHackable.CompInspectStringExtra` + `SpecialDisplayStats` **[V]** — nothing to build |
| Which hackset guards this target, active or dormant, which outcomes an ICE breaker disabled | `USH_HE.CompDataSourceProtected.CompInspectStringExtra` **[V]** — nothing to build |
| Full outcome probability table on the info card | `HacksetDef.SpecialDisplayStats` + `GetOutcomesDescription` **[V]** — nothing to build |
| Why this target refuses to be hacked | `AcceptanceReport.Reason`, three surfaces **[V]** — free, and it carries our research gate |
| **What this intrusion will cost in Trace, before it starts** | the same `CanHackNow` postfix plus `CompHackable`'s inspect string — **~10 lines**, counted in [`TRACE.md`](TRACE.md) § D3, not below |
| Remote reach, and whether a relay is live | the `USH_RemoteHackingDistance` stat row plus our `StatPart` explanations — free |
| **Intrusion history** — the last N reports: target, depth, detected | **ours**, `ITab_Cyberpod_Intrusions` on `Building_Cyberpod`, ~60 lines |

The intrusion history is deliberately an `ITab` and not a main tab. A main tab is
cross-cutting campaign UI and belongs to
[#61](https://github.com/cjd721/Rimworld-Archinity/issues/61); a readout attached to the
hacking apparatus is ours. If #61 later claims a pressure surface, the zero-cost fallback
is a letter on each `Network`/`Command` intrusion and the `ITab` can go.

### Cost

| Piece | XML / patch / new C# | Estimate | Lands in |
|---|---|---|---|
| Two Ultra `HacksetDef`s and their `HackingOutcomeDef`s (reusing shipped `workerClass`es) | XML | ~120 | `Archinity.Glitterites/Defs/Hacking/Hacksets_Ultra.xml` |
| Ultra hacking research, gated by `requiredAnalyzed` on Glitterite exemplars (#67's mechanism) | XML | ~80, **zero C# only if Analysis stays unpriced** — see *Outstanding decisions* | `Archinity.Glitterites/Defs/Hacking/Research_Hacking.xml`, `Patches/Analysis_Hacking.xml` |
| ExecData items re-granting the eight shipped verbs at Ultra | XML | ~100 | `Archinity.Glitterites/Defs/Hacking/ExecData_Ultra.xml` |
| `Arch_HackTargetClassExtension` on target defs; `StatPart` registration on two stats | XML patch | ~70 | `Archinity.Glitterites/Patches/Hacking_*.xml` |
| Hackset selector → highest qualifying band | Harmony postfix on `CyberUtils.GetHacksetDef` | ~15 | `ArchinityAltar.dll` |
| Research → target-class gate | Harmony postfix on `CompHackable.CanHackNow(Pawn)` | ~40 | same |
| `CompHackRelay` + `StatPart_HackRelay` | new C# | ~80 | same |
| `HackIntrusionLog` + `CompHackIntrusion` + `LockOut` postfix | new C# | ~70 | same |
| `ITab_Cyberpod_Intrusions` | new C# | ~60 | same |
| Multiplayer sync registrations (six delegates — five of Ushanka's, one of ours) | new C#, `Multiplayer.API` | ~30 | same |
| **Total** | | **~370 XML, ~295 C#** — plus two Harmony postfixes if Analysis is priced | one assembly, per `CODING_STANDARDS.md` |

---

## What #56 needs from hacking

[#56](https://github.com/cjd721/Rimworld-Archinity/issues/56) is downstream and consumes
this. Stated as a contract so it does not have to re-derive anything.

**1. What an intrusion is.** One `CompHackable`, on one `Thing`, carried from
`progress == 0` to a terminal state. It is **not** a tick and **not** a job — a pawn may
start, abandon and resume, and that is still one intrusion. The unit #56 counts is the
terminal event, never the work.

**2. What it can succeed or fail at.** Three terminal states; vanilla already carries all
three **[V]**:

| State | Source | Emitted |
|---|---|---|
| **Succeeded** | `CompHackable.ProcessHacked` ran — `progress >= defence` | `ThingComp.Notify_Hacked(hacker)` on our comp, no patch needed; it fires early in `OnHacked`, so the report is emitted before the hack's own effects |
| **Detected** | `CompHackable.LockOut(hacker)` ran; sets `lockedOutUntilTick` or `lockedOutPermanently` | Harmony postfix on `LockOut`, which is `public` |
| **Abandoned** | progress made, job ended, neither of the above | not emitted; #56 should not need it |

**Detection is not a roll anyone has to design.** Vanilla already rolls it, once per 3000
progress, as `Rand.MTBEventOccurs(hacker.GetStatValue(StatDefOf.HackingStealth), amount *
60f, 1f)` inside `CompHackable.Hack` **[V]**, and Ushanka scales it per hackset through
`HacksetDef.stealthMultiplier` — 1.0 for an outdated firewall, 0.4 for black ICE **[V]**.
**Deeper ICE is likelier to notice you, already, for free.**

**3. The signal a pursuit number can read.** `Archinity.Core.HackIntrusionLog`, a
`GameComponent`, raising:

```csharp
public readonly struct IntrusionReport {
    public readonly Thing          target;     // what was hacked
    public readonly Pawn           hacker;     // who, or null
    public readonly IntrusionDepth depth;      // Local | Device | Network | Command
    public readonly float          defence;    // target CompHackable.defence
    public readonly bool           detected;   // the target noticed
    public readonly bool           succeeded;  // completed, vs locked out
    public readonly int            tick;
}
public event Action<IntrusionReport> IntrusionCompleted;
```

**4. Where the "isolated door does not count" line sits, and why it is not a heuristic.**
`depth` is a **property of the target, declared in XML** on
`Arch_IntrusionDepthExtension`, defaulting to `Local`. An isolated door is authored
`Local`; a mechanoid, reactor, defence grid or command core is authored `Network` or
`Command`. #56 never has to infer network-ness from `defence`, a def name or a comp type.

**5. What is deliberately not mine.** The Trace number, its bands, its decay, its
display, its pursuit rules, and the function from `(depth, defence, detected, succeeded)`
to a Trace increment. **I emit every intrusion including `Local` ones, flagged** — so #56
decides to ignore them, rather than me deciding they never happened. The same event feeds
the intrusion history readout, which is mine, so the `Local` ones must exist.

> **#56 has answered, and the answer confirms this contract rather than amending it.**
> [`TRACE.md`](TRACE.md) § *What changes it* subscribes `WorldComponent_Trace` to
> `IntrusionCompleted` and looks the increment up in `TraceDef.intrusionRows` by `depth`,
> scaled by a curve on `defence`. **The `Local` row is authored `onSuccess: 0,
> onDetected: 0`** — so `GLITTERTECH.md`'s *"a basic isolated door need not matter"* is an
> authored number rather than a special case in either document, and neither spec
> hardcodes which depths count. `detected` is consumed as it stands; nothing new rolls it.

**6. One thing #56 asks back, and it is ten lines.**
[`docs/requirements/GLITTERTECH.md`](../requirements/GLITTERTECH.md) requires the player
to *"see the risk before committing to an intrusion"*. The
`CompHackable.CanHackNow(Pawn)` postfix in § *Gating target classes by research* is
already the seam vanilla renders in three places **[V]**, and `CompHackable`'s inspect
string is already in this document's display table. **The target's authored
`IntrusionDepth` and its Trace cost are appended there** — on a patch this cost table
already carries. [`TRACE.md`](TRACE.md) § D3 counts the ten lines, not this document.

---

## Persistence and multiplayer

### Persistence

- **Vanilla holds the target state.** `CompHackable.PostExposeData` scribes thirteen
  fields including `progress`, `defence`, `hacked`, `lockedOutUntilTick`,
  `lockedOutPermanently` and `autohack` **[V]**.
- **Ushanka holds the extraction state.** `CompDataSource.PostExposeData` scribes
  `_outputThings` (`LookMode.Deep`), the selected output index and both ripping flags;
  `CompDataSourceProtected` adds the chosen `HacksetDef`, the ICE-breaker flag and the
  active flag **[V]**. `WorldComponent_HacksetsLetter` scribes two one-shot letter
  flags.
- **`HackIntrusionLog` loads clean into a save that predates it.** `Game.ExposeData`
  calls `Game.FillComponents` on the loading path, and `FillComponents` instantiates
  every non-abstract `GameComponent` subclass missing from the save **[V]**. The log
  arrives empty; nothing else changes.
- **The relay must be a new `ThingDef`, not a comp bolted onto an existing item.**
  **T-34** is the nearest register entry — a `comps` list edit dropping the comp and reading
  its fields as defaults on the next load — but it is **`HediffDef` / `HediffWithComps`-specific
  and does not generalise to `ThingDef` as cited here**. It is an analogy, not authority for
  the `ThingDef` case, which has not been read. The decision does not rest on it: a fresh def
  costs nothing and never raises the question.
- Ushanka's def-injection runs at `RebindAllDefOfs`, i.e. **after** XML patching and
  before any save is read, so injected comps are present on load. They are invisible to
  `tools/defdb.py`, `tools/patch_check.py` and `tools/xpath.py`, which all read the merged
  XML database.

### Multiplayer

**`Rand` is not the problem here.** Every `Rand` on the hack path sits inside an
already-synced tick or job and passes the Divergence gate as
`CODING_STANDARDS.md` states it **[V]**: vanilla's lockout MTB inside
`CompHackable.Hack` reached from `JobDriver_Hack`'s tick action; Ushanka's outcome MTB and
`RandomElementByWeight` inside `CompDataSourceProtected.Hack`, reached from a Harmony
postfix on the same method; the Cyberpod's draws inside `Building_Cyberpod.Tick`; hackset
selection and output counts inside `PostSpawnSetup` during map generation.

**Two real hazards.**

**(a) Ushanka has no Multiplayer Compatibility entry. Five of its delegates need one, and
one more is ours.**
`rwmt.MultiplayerCompatibility` (workshop `1629973374`) contains zero hits for
`ushanka` or `hacking` **[I]** — that is a sweep of the mod's contents, not a read of every
entry; its `hack` hits are all *What The Hack*. Multiplayer
itself syncs only four things about `CompHackable` — `CompGetGizmosExtra` lambda ordinals
1, 7 and 8, plus `EndLockout`, the last three debug-only **[V]**. The vanilla player-facing
hack path is safe *because it terminates in `TryTakeOrderedJob`*, which Multiplayer syncs
— not because the gizmo is synced **[V]**.

Ushanka's state-mutating delegates that terminate in **neither** a Job nor a registered
sync:

| Site | Mutates |
|---|---|
| `Building_Cyberpod` "ignore autohack" `Command_Toggle` | `_ignoreAutoHack` |
| `Building_Cyberpod` start/stop-waking `Command_Action`s | `_isWakingUp`, `_wakeUpTicksPassed` |
| `Building_Cyberpod` hack-target `Command_Action` → targeter callback | `TryToStartHacking(..., force: true)` |
| `CompDataSource` rip-designation `Command_Action` | `_designatedForRipping`, adds a `Designation` |
| `CompDataSource` choose-output `FloatMenuOption` | `_currentOutputIndex`, `_progress` |
| *(ours)* the relay's choose-home-hacker gizmo | the scribed `Pawn` reference |

**Five of those six rows are Ushanka's and inherited; the last is new and exists only because
we build the relay.** The distinction matters for the ledger: declining Ushanka removes five,
not six. Note also that **row 2 is plural** — start-waking and stop-waking are two separate
`Command_Action`s — so the number of `RegisterLambdaMethod` ordinals is larger than the number
of rows. "Six delegates" in the cost table counts rows.

`USH_HE.Hediff_Cyberlink`'s hack gizmo and `CompResearchGiver`'s float menu both end in
`TryTakeOrderedJob` and are **safe as shipped** **[V]**.

An MpCompat entry is 10–40 lines — `[MpCompatFor(packageId)]`, a ctor taking
`ModContentPack`, one `MpCompat.RegisterLambdaMethod` per gizmo lambda ordinal **[V]**.
**We write the equivalent in our own assembly against `Multiplayer.API`.** Not because a
standard forbids the alternative: `CODING_STANDARDS.md` § *One assembly of ours* governs
assemblies **of ours** and explicitly carves a recompiled third-party DLL **out** of the rule,
so it says nothing either way about a class inside `Multiplayer_Compat.dll`. The reason is
narrower and practical — that file is someone else's mod, so putting a class in it means either
an upstream contribution or a maintained fork, and which of those we do is the sourcing
ledger's ([#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)) call, not this spec's.
`Multiplayer.API` is a reference our single assembly can already take, so it is the option that
needs no decision from anyone. Both forms resolve by string type name and lambda ordinal and
**break silently on an upstream refactor** — so the registrations belong in one file with
a comment naming the Ushanka version they were read against.

**(b) A mod setting decides which comps exist on which defs — T-67.**
`ShouldTurretBeHackable` returns false unless `HE_Mod.Settings.EnableTurretsHacking`, and
`ShouldMechBeHackable` unless `HE_Mod.Settings.EnableMechHacking` **[V]**. **T-18** is the
general rule — mod settings are part of the sync surface — and this is a sharper instance of
it rather than an exception to it: these settings do not merely change behaviour at runtime,
they change the **def database** at `RebindAllDefOfs`. **T-67** is the register entry for that
specific form. Two clients with different values hold different comp lists on the same
`ThingDef`s, hence different `defence` values, different `ExposeData` shapes and a desync with
no error message. Both must be pinned identical before a session.

**And pinning both settings is not a complete mitigation.** The third injection —
`ShouldBeDataSource`, which appends `CompProperties_DataSourceProtected` to **every**
`CompHackable` `ThingDef` — is **gated by no setting at all** **[V]**. It fires whenever
Ushanka is loaded. So the settings pin closes the turret and mech rows and leaves the
data-source row open, where the divergence is no longer *settings* parity but *mod-presence and
mod-version* parity across clients. The check before a session is therefore both: identical
settings **and** identical Ushanka builds. **T-67** covers both halves.

---

## Failure and recovery

**`SetFactionDirect` leaves a seized turret mis-indexed until the next load — T-68.**
`USH_HE.CompTurretHackable.OnHacked` calls `parent.SetFactionDirect(hacker.Faction)`
**[V]**, while both `Ability_HijackSubcore` on the mech path and vanilla's own
`CompAncientSecurityTerminal.OnHacked` call the full `Thing.SetFaction` **[V]**. **Two of
the three seizure paths agree and Ushanka's turret path is the odd one out** — vanilla is
the reference implementation and it does it correctly. `Thing.SetFaction` does three
things `SetFactionDirect` does not: `Map.attackTargetsCache.UpdateTarget(t)` for an
`IAttackTarget`, a `ChangedFactionToPlayer` quest signal, and
`Map.events.Notify_ThingFactionChanged` **[V]**. `AttackTargetsCache.RegisterTarget`
builds `targetsHostileToFaction` by snapshotting `thing.HostileTo(faction)` at
registration, and only `UpdateTarget` refreshes it **[V]**. A turret seized by the hack
path therefore stays in the player's hostile bucket and stays out of the raiders' —
**the colony's own pawns may keep treating it as a target and the raiders may not** —
until something else calls `UpdateTarget`. Reloading the save re-registers every target
and the symptom vanishes, which is what makes it expensive to find. Detection is by
observation only; nothing logs. Recovery in play is a save/load. The repair is a prefix
on `CompTurretHackable.OnHacked` substituting `SetFaction`, ~5 lines.

**`ResetHackProgress` fails silently if RimWorld renames a field — T-69.**
`USH_HE.CompHackableExtensions.ResetHackProgress` reflects into **ten** private fields of
`CompHackable` by string name — including `autohack` — and writes each as
`AccessTools.Field(...)?.SetValue(...)` **[V]**. `AccessTools.Field` returns `null` on a miss
and the null-conditional swallows it, so a rename makes the reset a partial no-op inside a
`try` that only logs on a throw — and a null never throws. The visible consequence is a seized
turret stuck at `hacked == true`, permanently un-re-hackable, with a clean log. It is correct
against 1.6.4566 today. **T-69 is registered against the pattern, not only this call site**:
`AccessTools.Field(...)?.SetValue(...)` is a silent no-op after any rename, and our own
reflection must not copy it.

**A campaign softlock is possible and cheap to prevent.** If an Ultra hacking research
project's `requiredAnalyzed` names an exemplar reachable only by first performing a hack
that project unlocks, the branch is unreachable and **silent** — `requiredAnalyzed` failure
presents as a locked project, not an error. `tools/audit_research.py` is the existing check
and must run over the Ultra rung. Note **T-40**: `requiredAnalyzed` is nulled without
Biotech, and the project then becomes free rather than blocked.

**Recoverable by design.** A lockout expires (`CompHackable.CompTick` → `EndLockout`)
unless `lockoutPermanently`; a failed intrusion loses progress, not the target; black ICE
is the one outcome class that can kill the hacker, and it is both flagged in the inspect
string and warned about at designation time by
`CompDataSourceProtected.UpdateDesignation` **[V]**.

---

## Status

**Evidence class: READ.** Settled by vanilla defs, the decompiled 1.6
`Assembly-CSharp.dll`, `HackingExpansion.dll` with its matching 1.6 source,
`Multiplayer.dll` and `Multiplayer_Compat.dll`, and a two-root wide pass validated
against known positives. No stub run, no launch. **Anomaly is not installed and was not
searched** — see § *Available mechanisms*, *Residual gap*.

**Verified available mechanism**, not yet an implementation commitment:

- Ushanka's Hacking Expansion as the carrier for the whole front — **verified**.
- Vanilla `CompHackable` as the target state machine — **verified**.
- `ThingComp.Notify_Hacked` as the completion broadcast — **verified**.
- `requiredAnalyzed` as the artifact → research gate, from
  [#67](https://github.com/cjd721/Rimworld-Archinity/issues/67) — **verified and selected
  there**, at zero C# **conditional on Analysis staying unpriced**.
- The `StatPart` relay, the research-class gate and the intrusion log — **proposed**,
  **[I]** as compositions; each mechanism they use is **[V]**.

Whether Ushanka's Hacking Expansion ships is
[#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s decision, not this
document's. **If it is declined, the front is roughly 1,500 lines of new C# and the
requirement should be re-scoped instead** — that is the number the ledger needs.

---

## Available mechanisms

### Vanilla 1.6 — `Assembly-CSharp.dll`

| Mechanism | Provides | Limitation |
|---|---|---|
| `RimWorld.CompHackable` | progress, `defence`, lockout (timed and permanent), `IsHacked`, `hackingStartedSignal` / `hackingCompletedSignal`, `"HackingStarted"` and `"Hacked"` quest signals, `BroadcastCompSignal`, `dropOnHacked` | no tiering, no research awareness, no notion of intrusion depth |
| `CompProperties_Hackable` | `defence`, `intellectualSkillPrerequisite`, `lockoutDurationHoursRange`, `lockoutPermanently`, `onlyRemotelyHackable`, `completedQuest`, `dropOnHacked`, hacked/unhacked graphics and letters | `onlyRemotelyHackable` means *"cannot be hacked by walking up"* — it **hides** the hack UI, it is not a remote-hacking capability **[V]** |
| `ThingComp.Notify_Hacked(Pawn)` | `public virtual`, called on every comp of the hacked thing exactly once, **early in `OnHacked`** **[V]**. **Uncontested** — a corpus-wide sweep returns zero overrides outside vanilla **[I]**, a sweep result rather than a read | success only; says nothing about detection |
| `CompAncientSecurityTerminal.OnHacked` (Odyssey) | the shipped *hack here, effect there* precedent: flips a random map turret to the hacker's faction via `SetFaction`, or disables a door | random target, `Rand.Chance(0.5f)`, two hard-coded defs |
| `JobDriver_Hack`, `WorkGiver_Hack`, `JobDefOf.Hack` | the hack is a Job, so Multiplayer syncs it through `TryTakeOrderedJob` | **no `Designator_Hack` and no `DesignationDefOf.Hack` exist in 1.6** **[V]** |
| `HackUtility.IsCapableOfHacking` | subhuman / skill-disabled / manipulation gates | |
| `StatDefOf.HackingSpeed`, `StatDefOf.HackingStealth` | work per tick; the lockout MTB | `HackingStealth` is consumed **only** by `CompHackable.Hack` **[V]** |
| `Thing.SetFaction` vs `SetFactionDirect` | attack-target reindex, quest signals, map event | see § *Failure and recovery* |
| `Game.FillComponents` | a new `GameComponent` loads clean into an old save | |
| `RimWorld.StatPart` | `TransformValue` + `ExplanationPart`, applied to every consumer of a stat | |

### Ushanka's Hacking Expansion — `3573344880`

1.6-only, one source tree matching the shipped assembly, depends on Harmony and VEF.
Namespace `USH_HE`. Carries `HacksetDef` (4 shipped), `HackingOutcomeDef` + 17 workers,
`Building_Cyberpod` + `MapComponent_CyberpodManager`, `JobDriver_RemoteHack`,
`CompTurretHackable` / `CompMechanoidHackable` / `CompDataSource` /
`CompDataSourceProtected` / `CompICEBreaker` / `CompResearchGiver` / `CompBlackBox` /
`CompAncientCyberdeck`, eight `Ability_Cyber` verbs, `Hediff_Cyberlink`,
`Hediff_LearningAbility`, four `ResearchProjectDef`s (Industrial → Spacer),
`DelayedRaidUtility`, and two map GenSteps.

**What it does not carry, and where each shaped the build:**

- **No research-driven target tiering.** `GetHacksetDef` reads the *target's* `defence`,
  never the player's research **[V]**. → the class gate, ~40 lines.
- **No band ordering.** Weighted-random across all qualifying bands, not the highest
  **[V]**. → the selector postfix, ~15 lines.
- **No Ultra rung.** Four projects, topping out at `USH_ExecData` at `techLevel Spacer`
  **[V]**. → the Ultra XML.
- **No cross-map operation.** The Cyberpod's reach is unlimited *within its own map*; the
  remote stat tops out at 19.9 cells **[V]**. → the relay `StatPart`.
- **No Trace emission of any kind.** Its only retaliation is
  `DelayedRaidUtility.TriggerDelayedRaid`, called from exactly two places —
  `CompAncientCyberdeck` and `CompBlackBox` — which spawns a `SignalAction_Incident` and a
  `SignalSchedulerMapComponent` to fire a one-off raid from the owning faction after a
  delay **[V]**. That is a per-building consequence, not a persistent pursuit variable, and
  it is **not** the mechanism #56 wants. → the intrusion log.
- **No Multiplayer Compatibility entry** **[I]** (a sweep of MpCompat's contents). → five sync
  registrations for its delegates; a sixth is ours, for the relay gizmo.

### Ruled out

- **Nothing else in the corpus carries remote or tiered hacking.** A two-root wide pass
  over both `steamapps/workshop/content/294100/` and
  `steamapps/common/RimWorld/Mods/`, excluding `**/obj/**`, returns Ushanka as the **sole**
  carrier of `RemoteHack`, `Hackset` and `ICEBreaker` **[V]**. `Telepresence`,
  `RemoteControl`, `ProxyPawn`, `PuppetPawn`, `TryHackMechanoid`, `Reprogram` and
  `CaptureMech` return **zero hits corpus-wide** **[I]** — a name sweep proves nobody used
  those names, not that nobody built the behaviour. **Cross-map hacking exists nowhere**,
  which is why the relay owes a build.
- **The other `CompHackable` referents add no mechanism we want.** VEF holds TypeRefs only
  and defines no hacking type and no hackable def; Multiplayer holds sync registrations;
  GravTech adds one vanilla-comp hackable; Vanilla Gravship Expanded's
  `CompHackableEscapePod.OnHacked` rolls a content table; Better Traders Guild postfixes
  `CompHackable.OnHacked` for a settlement faction reaction and ships its own hackable
  hatch **[V]**. The last is the only one that touches a method we also touch — different
  method from our seam, no collision expected, and recorded as cargo under that mod in
  `docs/data/MOD-VERDICTS.md` rather than treated as a verdict here.
- **VPE Puppeteer** (`vanillaexpanded.vpe.puppeteer`) carries a one-pawn-drives-another
  relation (`Hediff_Puppeteer`, `puppetCapacity`, `TryTransferMind`) but it is a psycast
  over a pawn relation, not a hack relay, and it does not move a hack **[I]** — established from
the mod's own metadata and a sweep of its type names, not a tier-4 read of the assembly.
- **`sae.researchmod`** is declined by [#67](https://github.com/cjd721/Rimworld-Archinity/issues/67); nothing here revives it.

**Residual gap:** **Anomaly is not installed** — `common/RimWorld/Data/` holds Core,
Royalty, Ideology, Biotech and Odyssey only. No Anomaly content was searched. Nothing in
this design depends on it, but a hackable Anomaly def would not have been seen.

---

## Verification

**Read, with a path and a `Type.Method` anchor, on
[#58](https://github.com/cjd721/Rimworld-Archinity/issues/58):** vanilla `CompHackable`,
`CompProperties_Hackable`, `HackUtility`, `JobDriver_Hack`, `WorkGiver_Hack`,
`Thing.SetFaction`, `AttackTargetsCache.RegisterTarget` / `UpdateTarget`,
`Game.FillComponents`, `ThingComp.Notify_Hacked`, `StatPart`; Ushanka's
`Patch_DefOfHelper_RebindAllDefOfs`, `CyberUtils`, `HacksetDef`, `HackingOutcomeDef`,
`Building_Cyberpod`, `MapComponent_CyberpodManager`, `JobDriver_RemoteHack`,
`CompTurretHackable`, `CompMechanoidHackable`, `CompDataSource`,
`CompDataSourceProtected`, `Hediff_Cyberlink`, `Hediff_LearningAbility`,
`Ability_Cyber`, `Ability_HijackSubcore`, `CompHackableExtensions`,
`DelayedRaidUtility`, `ResearchPrerequisitesResolver`; Multiplayer's `SyncMethods.Init`;
`Multiplayer_Compat.dll`'s entry inventory.

**Needs a prototype or an in-game check before this is built:**

1. **Does `DefOfHelper.RebindAllDefOfs(false)` run more than once per session?** If it
   does, `ShouldBeDataSource` has no already-present guard and appends a second
   `CompProperties_DataSourceProtected` on every pass, while `TryGetComp` returns only the
   first — a silent divergence in the shape of **T-06**. **[I]**, one log check.
2. **Does the `StatPart` relay actually reach vanilla's lockout roll?** The roll reads
   `hacker.GetStatValue(StatDefOf.HackingStealth)` on the field pawn; the `StatPart` must
   transform it. Observable: seize a target with a relay live and confirm the stat report
   shows the *home* hacker's stealth.
3. **Does injecting our comp alongside Ushanka's survive `PawnKindDef.race.comps`?** Mech
   comps are appended to the shared race `ThingDef`, not per-kind — two `PawnKindDef`s
   sharing a race would append twice. **[I]**.
4. **Two-client parity on `HE_Mod.Settings`.** The § *Persistence and multiplayer* (b)
   hazard needs one deliberate mismatched-settings session to confirm the desync mode and
   whether anything is logged. **RUN**, and the only RUN item here.

**Observable checks that the requirements are satisfied:**

- A Glitterite reactor refuses a hack with a legible reason until its research is done,
  and accepts it afterwards.
- A hacked Glitterite turret fires on its former owners within the same tick, without a
  reload.
- A colonist sealed in a Cyberpod at home drives a hack on a Charting away-site through a
  field pawn carrying a relay, and the field pawn's stat report names them.
- A `Network` intrusion appears in the intrusion history with `detected` set correctly;
  an isolated door appears flagged `Local`.

---

## Outstanding decisions

| Question | Consequence | Owner |
|---|---|---|
| Does Ushanka's Hacking Expansion ship? | if not, ~1,500 lines of new C# and the requirement is re-scoped | [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) |
| The `HackTargetClass` catalogue and its research map — which classes exist, in what order | authoring; the mechanism does not depend on the answer | [#47](https://github.com/cjd721/Rimworld-Archinity/issues/47) authoring, against a requirements line that does not yet exist |
| `defence` values for the Ultra bands, `minDefense` thresholds, ExecData learning costs | balance | map [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2) *Not yet specified* |
| ~~The function from `IntrusionReport` to a Trace increment, and whether `Local` contributes at all~~ | **Answered.** `TraceDef.intrusionRows`, keyed on `depth`, scaled by a curve on `defence`; `Local` is authored zero. The contract above is unchanged — this document still emits everything and flags it. | **Closed** by [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56) / [`TRACE.md`](TRACE.md) |
| **Whether Ultra hacking research costs Intel on top of its exemplar.** The `requiredAnalyzed` gate is XML and free *under the unpriced default*; [`RESEARCH.md`](RESEARCH.md) and [`CURRENCIES.md`](CURRENCIES.md) both hold the question **open** and both record that a priced answer costs **two Harmony postfixes** — `CompAnalyzable.OnAnalyzed` and `CompInteractable.CanInteract`. Hacking is the side that makes it non-trivial: `GLITTERTECH.md` asks for artifacts *"combined with sufficient Intel/research"*, which reads as a price | the cost row's "zero C#" is conditional, not settled. **This document does not resolve it** | Open requirements parameter owned by [`docs/requirements/GLITTERTECH.md`](../requirements/GLITTERTECH.md), tracked as the Analysis-pricing question in [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2). [#67](https://github.com/cjd721/Rimworld-Archinity/issues/67) is closed and settled only the mechanism |
| **How far `docs/requirements/CHARTING.md` carries the protocol artifact.** It **does** name *"unique protocols"* among the deterministic core rewards of a Charting beat — an earlier draft of this spec said it did not, and that was wrong. What it does not carry is hacking, intrusion, or an away-site hack as a beat activity; `GLITTERTECH.md` supplies those with *"Campaign-critical Charting sites can contain unique protocol artifacts that must be brought home"* | the artifact itself has a requirements home; the relay and the away-site intrusion still do not | **no open ticket owns this**; the gap is stated here rather than handed anywhere. Raised on [#58](https://github.com/cjd721/Rimworld-Archinity/issues/58) |
| Whether the intrusion readout stays an `ITab` or folds into a campaign pressure surface | display only; the letter fallback costs nothing | [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61) |
