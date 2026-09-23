# Transcendence

## Purpose and scope

How a founder claims a self-authored title, receives `VRE_Transcendent`, meets the
Administrator and chooses whether to enter the new reality or stay — and how that
one-time state is recorded per founder and survives a save.

Requirements, both halves:

- [`docs/requirements/ALTAR.md`](../requirements/ALTAR.md) § *Saved state and remaining
  work* — "Track actual founder psylink/channel progression and the final claimed title."
  That sentence covers the **claimed title** and nothing else this document builds.
- [`docs/plot/ENDING.md`](../plot/ENDING.md) § *Ascension, the Administrator and the
  Postgame*, which owns the **Administrator encounter** and terminal **enter-or-stay**
  choice. There is no standing re-offer. [#48](https://github.com/cjd721/Rimworld-Archinity/issues/48) owns the final authored scene.

Established by [#50](https://github.com/cjd721/Rimworld-Archinity/issues/50), which
absorbed [#79](https://github.com/cjd721/Rimworld-Archinity/issues/79).

**Founder psylink progression.** The same requirements sentence names founder
psylink/channel progression beside the claimed title. Its capability is in
[`PSYCHIC.md`](PSYCHIC.md) ([#162](https://github.com/cjd721/Rimworld-Archinity/issues/162),
[#163](https://github.com/cjd721/Rimworld-Archinity/issues/163)); its design and any field here are
[#31](https://github.com/cjd721/Rimworld-Archinity/issues/31) / [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.

**This document owns the per-founder state store.**
[#134](https://github.com/cjd721/Rimworld-Archinity/issues/134)'s route A1 ([`RELIGION.md`](RELIGION.md)
§ *Founders — who they are, beats that require them, flows that refuse them*) and
[`PSYCHIC.md`](PSYCHIC.md) F1 read it; nothing builds a second one *for founder state*.
`VRE_Transcendent` is a shipped gene and needs no fields here.

Adjacent systems take over at: psychic-rank titles, if the ranks carry titles at all — a
`RoyalTitleDef` rung must sit on a faction **other than the Church**, because
`Pawn_RoyaltyTracker.titles` holds one title per (pawn, faction) and a rung on the Church's
ladder would silently overwrite the Church title ([`PSYCHIC.md`](PSYCHIC.md) § *What raises
psylink rank besides the altar* › *Open questions*) — the altar's charge and vector machinery
(`Archinity.Altar`), and volunteer eligibility ([#49](https://github.com/cjd721/Rimworld-Archinity/issues/49)
closed; volunteer-side state is [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s).

---

## The build — title and encounter state

Three verified vanilla mechanisms carry almost all of this, and one small comp is
the only new state.

| | |
|---|---|
| **Mechanism** | A `HediffComp` on a founder-only `HediffDef`, implementing `Verse.IRenameable`; a `Dialog_Rename<T>` subclass for the epithet; a vanilla `Dialog_NodeTree` for the Administrator and the enter-or-stay choice. *Enter* rolls credits by the verified non-terminal route (§4; ending the game under Multiplayer is [#182](https://github.com/cjd721/Rimworld-Archinity/issues/182)); *Stay* closes the tree with no pawn mutation. |
| **State** | `CompFounderRecord` — one instance per founder, living on the `Archinity_FounderRecord` hediff. Plus `Pawn_StoryTracker.title`, a vanilla per-pawn string, as the display projection of the epithet. |
| **Persistence** | `HediffWithComps.ExposeData` → `CompExposeData()` for the comp; `Scribe_Values.Look(ref title, "title")` in `Pawn_StoryTracker.ExposeData` for the display copy. A save that predates the feature has no hediff and no `title`; both read as "nothing claimed". **No migration code.** |
| **Change** | The `RenamableLabel` setter (claim); the altar's rite completion (grant `VRE_Transcendent`); the Administrator dialog's terminal *Enter the new reality* option. *Stay* changes nothing beyond recording that the scene was seen. |
| **Display** | `Pawn.LabelNoCount` renders `"Name, TitleShortCap"`, so the epithet is free on the **inspect-pane header** (`InspectPaneUtility.AdjustedLabelFor` → `Thing.LabelCap` → `LabelNoCount`) and in anything built from `LabelCap` / `LabelNoCountColored` [V]. It is **not** on the colonist bar and **not** on the in-world map label — both draw `LabelShortCap`, which carries no title [V]. Letters and tooltips are per-surface **[I]**. Plus the hediff row in the Health tab, the altar's refusal text, and the credits screen. |
| **Cost** | ~185 lines of new C# in the assembly we already ship (`ArchinityAltar.dll`), and ~65 lines of XML. No new assembly, and no third-party reference — see *Persistence and multiplayer* for the one we would need only if the recommended design fails. |

### 1. The store — `CompFounderRecord`

```
HediffDef Archinity_FounderRecord      (XML)
  defName:      Archinity_FounderRecord
  label:        "transcendent"
  description:  required — HediffDef.ConfigErrors yields "has no description!" without one
  hediffClass:  HediffWithComps        <-- REQUIRED. The field defaults to typeof(Hediff),
                                           which holds no comps; ConfigErrors then yields
                                           "has comps but hediffClass is not HediffWithComps
                                           or subclass thereof" and the whole store is inert
  isBad: false, everCurableByItem: false, tendable: false,
  comps: [ { compClass: Archinity.CompFounderRecord } ]

class CompFounderRecord : HediffComp, IRenameable   (C#)
```

Both `hediffClass` and `description` are **loud** omissions — they surface as config
errors at load, not as silent misbehaviour. They are listed because the sketch without
them does not work, not because they are subtle.

Applied to a founder the first time anything needs to record something about
them — normally at *Claim Yourself*. Under [#134](https://github.com/cjd721/Rimworld-Archinity/issues/134)'s
route A1 (recommended, not selected; selection [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119))
the record is stamped at game start and lazy creation becomes migration. A1 also needs
`duplicationAllowed: false` (**T-113**). See [`RELIGION.md`](RELIGION.md) § *Founders — who
they are, beats that require them, flows that refuse them* › *A1 — founder record stamped at
game start*, and
[`PSYCHIC.md`](PSYCHIC.md) F1.

**Fields, v1.** Every Scribe key carries the `archinity_` prefix, for the reason
in *Persistence* below.

| Field | Scribe key | Meaning |
|---|---|---|
| `string claimedTitle` | `archinity_claimedTitle` | The epithet the player typed. Authoritative; `story.title` is a copy. |
| `bool titleClaimed` | `archinity_titleClaimed` | *Claim Yourself* has been performed. **The gate reads this, never the string** — see below. |
| `int transcendedTick` | `archinity_transcendedTick` | `-1` until the final rite completes on this founder. |
| `bool administratorSeen` | `archinity_administratorSeen` | The once-only Administrator encounter has been shown to this founder. |

**Why the flag and the string are different facts.** `Pawn_StoryTracker.title` is
writable by vanilla's own rename-colonist window (`Dialog_NamePawn` sets
`pawn.story.Title = CurPawnTitle`), so a non-empty title proves nothing about the
rite. `titleClaimed` is the only prerequisite the altar may read.

**For anyone extending this store — the two rules.**

1. **Add fields to `CompFounderRecord`. Do not create a second store *for founder
   state*.** The comp already travels with the pawn across maps, caravans and corpses, is
   already scribed, and is already multiplayer-serializable.

   **Scope caveat.** `Archinity_FounderRecord` is a *founder-only* hediff. Volunteer
   eligibility is evaluated on pawns who will never carry it (`requirements/ALTAR.md`
   § *Conversion and certainty*). Rule 1 does not reach those pawns and does not forbid a
   per-volunteer store; volunteer-side state is [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s
   ([#49](https://github.com/cjd721/Rimworld-Archinity/issues/49) closed with the capability answered). What a
   volunteer rule reads *here* is the founder side of the rite.
2. **Prefix every new Scribe key `archinity_`, and never remove or reorder the
   `comps` list on `Archinity_FounderRecord`.** `HediffWithComps.ExposeData` calls
   `comps[i].CompExposeData()` in a **flat, shared Scribe namespace with no
   per-comp node** — two comps on one hediff using the same key silently
   overwrite each other, and a comp dropped from the def silently loses its saved
   data on the next load. **T-34** (`docs/TRAPS.md`).

### 2. The epithet — one synced write, no multiplayer code of ours

`IRenameable` is the whole trick. Multiplayer registers, for **every** loaded type
implementing `Verse.IRenameable` that its serializer can handle, that type's
declared `RenamableLabel` property **setter** as a sync method
(`Multiplayer.Client.SyncMethods`, in a `LongEventHandler.ExecuteWhenFinished`
block, over `typeof(IRenameable).AllImplementing()` — which enumerates
`GenTypes.AllTypes`, mod assemblies included). `HediffComp` is registered in MP's
sync dictionary with `isImplicit: true`, so our subclass resolves through the
hierarchy and `CanHandle` passes.

**So the setter is the synced write, and everything the claim does lives inside it:**

```csharp
public string RenamableLabel
{
    get => claimedTitle ?? string.Empty;
    set
    {
        claimedTitle  = value;
        titleClaimed  = true;
        Pawn.story.title = value;   // the field, not the Title property
    }
}
public string BaseLabel    => Pawn.LabelShortCap;
public string InspectLabel => RenamableLabel;
```

Assign `story.title` (the public field), **not** `story.Title` (the property): the
property's setter is `title = null; if (value != Title && !value.NullOrEmpty())
title = value;`, and `Title` falls back to the backstory title — so setting an
epithet that happens to equal the founder's backstory title stores `null`.

**The dialog.**

```csharp
class Dialog_ClaimSelf : Dialog_Rename<CompFounderRecord>
```

`Dialog_Rename<T>` (Verse, 1.6) is generic over `IRenameable`, gives us the text
field, focus handling, Enter-to-accept and `NameIsValid`, and does exactly two
things on accept: `renaming.RenamableLabel = curName;` then `OnRenamed(curName)`.
Override `NameIsValid` (non-empty, not whitespace) and `MaxNameLength`; **leave
`OnRenamed` empty.**

> `OnRenamed` runs locally and immediately on the clicking client while the synced
> setter is still in flight. Any state change put there happens on one client
> only, with no error. Multiplayer had to register
> `Dialog_RenameBuildingStorage_CreateNew.OnRenamed` as a separate sync method for
> exactly this reason — with a target transformer, which is the corroborating evidence
> that it bites in practice. **T-52.** The rule that follows: leave `OnRenamed` empty,
> and put every effect of the claim inside the `RenamableLabel` setter, which is the
> whole synced write.

**Where the dialog is opened, and by whom.** From a `Command_Action` on the
founder (or a float-menu option on the altar) — a gizmo action, which runs on the
clicking client only. It therefore appears for whichever player clicked, which is
the correct answer to "the right player": the player who initiated the act. Never
open it from inside a synced method; a window added there opens on every client.

**Two players cannot end up with two strings.** Both may open the dialog; both
dialogs are local; both submissions go through the same registered setter; the
server orders them; both clients apply both in the same order and converge on the
same final value. The setter can also guard on `titleClaimed` and refuse a second claim;
either way is trivial (see *Outstanding decisions*).

### 3. The gate

```csharp
public static bool HasClaimedSelf(Pawn p) =>
    p?.health.hediffSet.GetFirstHediffOfDef(ArchinityDefOf.Archinity_FounderRecord)
       ?.TryGetComp<CompFounderRecord>()?.titleClaimed == true;
```

(`HediffUtility.TryGetComp<T>(this Hediff)` is a vanilla extension method.)

Called from a new clause in `Building_Altar.CanAcceptPawn`, alongside the existing
vector and charge clauses, returning a translated refusal
(`Archinity_AltarSelfNotClaimed`). Entry into the altar is
`Building_Enterable.SelectPawn`, which Multiplayer registers as a sync method in
**`Multiplayer.Client.SyncDelegates`** (`SyncMethod.Register(typeof(Building_Enterable),
"SelectPawn")`) — *not* in `SyncMethods` — and which `Building_Altar` does not override,
so the gate needs no synchronisation work at all.

### 4. The Administrator and the choice

[`plot/ENDING.md`](../plot/ENDING.md) § *Ascension, the Administrator and the Postgame* gives
one choice, after the Administrator encounter:

> **Enter the new reality**: trigger RimWorld's victory/end-game condition and roll credits.
> **Stay in this reality**: close the scene and continue the colony indefinitely. The founder
> remains present and transcendent; no pawn state, map state or inventory changes.

The choice rides on the Administrator's `Dialog_NodeTree` as two `DiaOption`s. There is no
standing re-offer at the altar.

**The Administrator encounter itself** is a vanilla `Dialog_NodeTree`, shown once per
founder behind `administratorSeen`, opened from synced code with a map context.

> **The dialog is replayed for free. Its options are not.**
>
> MP converts a `Dialog_NodeTree` opened from synced code into a map-scoped
> `PersistentDialog` (`Multiplayer.Client.CancelDialogNodeTree`, a prefix on
> `WindowStack.Add`) and replays it to every client via
> `Multiplayer.Client.ForceShowDialogs`. A bespoke `Window` gets none of that — which is
> still the reason to use the vanilla type.
>
> **What is not free is each `DiaOption.action`.** `PersistentDialog` reconstructs every
> option's delegate through `Multiplayer.Client.DelegateSerialization`, whose
> `IsDeclaringTypeAllowed` walks to the delegate method's outermost declaring type, then
> up its `BaseType` chain, and requires a member of a hardcoded 15-entry array:
> `Ability`, `AbilityComp`, `Command`, `ThingComp`, `Dialog_BeginRitual`, `LordToil`,
> `Precept`, `SocialCardUtility`, `Letter`, `FactionDialogMaker`, `GenGameEnd`,
> `IncidentWorker`, `QuestPart`, `ResearchManager`, `ShipUtility`. Anything else throws
> `"Delegate deserialization: method not allowed"` **on load**. `Building_Altar` walks
> `Building → Thing → object`; `CompFounderRecord` walks `HediffComp → object`.
> **Neither is on the list.** See
> [`docs/engine/determinism.md`](../engine/determinism.md) § *MP serialises the
> comms-console dialogue, options included* [V].
>
> **Three rules for the Administrator's options, therefore:**
>
> 1. ***Stay in this reality*** **carries no action at all** — `resolveTree = true` and
>    nothing else. A delegate-free option is scribed as plain values (`text`, `resolveTree`,
>    `disabled`, `disabledReason`, `clickSound`) and cannot fail this check. Staying *is*
>    closing the dialog, so this costs nothing to arrange.
> 2. ***Enter the new reality*** **carries the only delegate, and it must be declared on an
>    allowed type.** The cheapest host is a `ThingComp` on the altar's `ThingDef` —
>    `ThingComp` is on the array — so the lambda's outermost declaring type is
>    `Archinity.CompAltarThreshold`, whose base chain reaches `ThingComp` and passes. Do
>    **not** declare it on `Building_Altar` or on `CompFounderRecord`. The field-type rule
>    applies on top: capture only the founder `Pawn` (an `ILoadReferenceable`) and
>    primitives.
> 3. ***Both*** **options set `resolveTree = true`** — **T-97** — and the option with the
>    delegate needs it most. `Multiplayer.Client.WindowStackTryRemove` is the **only** path
>    that removes a `PersistentDialog` from `mapDialogs`, and it fires from
>    `WindowStack.TryRemove` only when `Multiplayer.InInterface` is false — which, inside the
>    `[SyncMethod]` `PersistentDialog.Click`, it is. What actually triggers that close is
>    `Verse.DiaOption.Activate`'s `if (resolveTree) OwningDialog.Close();`, which runs
>    **before** `action()` [V], so the cleanup does not depend on *Enter*'s action
>    succeeding. **Without `resolveTree`, *Enter the new reality* runs its action and strands
>    its `PersistentDialog`**, and `Multiplayer.Client.ForceShowDialogs` re-adds it on every
>    `MapDrawer.DrawMapMesh` — re-offering an answered ending forever, and, because
>    `ForceShowDialogs` only ever shows `mapDialogs.First()`, hiding every later dialog on
>    that map behind it. Silent, with no log line on either client.

**What *Enter* calls.** The verified route is non-terminal. From the synced tick:

```csharp
ShipCountdown.InitiateCountdown("Archinity_TranscendenceCredits".Translate(...));
```

What that vanilla call actually does: fades to white over 7.2s, then
`GameVictoryUtility.ShowCredits(customLaunchString, SongDefOf.EndCreditsSong)`.
`ShowCredits`'s `exitToMainMenu` parameter **defaults to `false`**, and
`Screen_Credits.PostClose` only calls `GenScene.GoToMainMenu()` when it is true.
Closing the credits sets `Find.TickManager.CurTimeSpeed = TimeSpeed.Normal` and
**returns the player to the live colony.** The overload taking a string touches no ship and
destroys nothing, `InitiateCountdown` resets `timeLeft` on every call, and two mods in the
corpus already ship this exact pattern (VFE Deserters' flagship ending; RimPacts' strategy
victory).

Whether *Enter* can instead end the game for both players under Multiplayer — credits that
exit both clients to the main menu, or the `GameEnder` / `GenGameEnd` path — is
[#182](https://github.com/cjd721/Rimworld-Archinity/issues/182). If no ending route proves safe, `ENDING.md`'s
fallback frames the same scene as the founder staying until ready.

### 5. Where the player sees it

| Surface | Mechanism | New code |
|---|---|---|
| `"Aria, She Who Does Not Ask"` in the **inspect-pane header** | `InspectPaneUtility.AdjustedLabelFor` → `Thing.LabelCap` → `Pawn.LabelNoCount`, which appends `story.TitleShortCap` [V] | none |
| Anywhere else built from `LabelCap` / `LabelNoCountColored` — including our own letter and dialog text, where we choose the accessor | the same call [V] | none |
| **Not the colonist bar, and not the in-world map label** | `GenMapUI.DrawPawnLabel` → `GetPawnLabel` → `pawn.LabelShortCap`, and `Verse.Pawn.LabelShort` is `LabelPrefix + Name.ToStringShort` — **no title**. The bar's only `TooltipHandler.TipRegion` is over the status icons, not over the name [V] | n/a — not available at any price here |
| Vanilla letters and tooltips generally | **[I], per surface.** Vanilla mixes `LabelShort`, `Name.ToStringShort` and `LabelCap`; only the `LabelCap` ones carry the epithet, and which is which has not been enumerated | none |
| Health tab row, "Transcendent" | the `Archinity_FounderRecord` hediff, `CompLabelInBracketsExtra` | ~10 lines |
| "X has not claimed a title" when the altar refuses | `Building_Altar.CanAcceptPawn` refusal string | ~5 lines |
| The claim, the transcendence, the Administrator and the enter-or-stay choice | letters + one `Dialog_NodeTree` with two `DiaOption`s | ~30 lines + XML |
| *Enter the new reality* | `Screen_Credits`, with our text above the credit roll (the ending beyond the credits is [#182](https://github.com/cjd721/Rimworld-Archinity/issues/182)) | ~5 lines |

The claimed epithet and any Church title **coexist without contention**: nothing in
`Pawn.LabelNoCount` reads `pawn.royalty`, and `RoyalTitleDef` titles render in the
bio tab's own Titles section via `royalty.MainTitle()`. They occupy different
surfaces. Stripping the Church title at Claim Yourself is also possible: VFED's
`JoinDeserters` strips Church titles ([`RELIGION.md`](RELIGION.md) § *The Schism — revealed, taking the Church's
ground, allied for good* › *Route C — VFE Deserters as shipped*) [V]; the vanilla call it uses is [I].

### Cost

| Piece | Kind | Estimate | Lands in |
|---|---|---|---|
| `HediffDef Archinity_FounderRecord` (incl. `hediffClass`, `description`) + `HediffCompProperties` | XML | ~25 lines | `Archinity.Altar/Defs/HediffDefs/` (new) |
| `CompProperties` for `CompAltarThreshold` on the altar `ThingDef` | XML | ~5 lines | `Archinity.Altar/Defs/ThingDefs/` |
| Keyed strings (refusals, letters, credits text, both `DiaOption` labels) | XML | ~35 lines | `Archinity.Altar/Languages/English/Keyed/` |
| `CompFounderRecord : HediffComp, IRenameable` + `CompExposeData` | new C# | ~70 | `Archinity.Altar/Source/FounderRecord.cs` (new) |
| `FounderRecord` static accessors (`For`, `HasClaimedSelf`, `Ensure`) | new C# | ~30 | same file |
| `Dialog_ClaimSelf : Dialog_Rename<CompFounderRecord>` | new C# | ~25 | same file |
| Claim gizmo on the founder | new C# | ~20 | `Archinity.Altar/Source/Patches.cs` |
| `CanAcceptPawn` clause (the claimed-title gate) | new C# | ~5 | `Archinity.Altar/Source/Building_Altar.cs` |
| Rite completion: set `transcendedTick`, build the Administrator `Dialog_NodeTree`, `InitiateCountdown` | new C# | ~20 | `Archinity.Altar/Source/Building_Altar.cs` |
| `CompAltarThreshold : ThingComp` — the allowed declaring type hosting the *Enter* option's action | new C# | ~15 | `Archinity.Altar/Source/Building_Altar.cs` |

**~185 lines of C# into the assembly we already ship, plus ~65 lines of XML. No
new assembly of ours, and — on the recommended design — no reference to
Multiplayer at all.**

---

## Persistence and multiplayer

### Save and load

- **The comp.** `HediffWithComps.ExposeData` calls `InitializeComps()` on
  `LoadSaveMode.LoadingVars` and then `comps[i].CompExposeData()` on each. Comps
  are rebuilt from the **def**, then hydrated from the save.
- **A save that predates the feature** has no `Archinity_FounderRecord` hediff at
  all, so `HasClaimedSelf` is false and every field reads its default. Nothing to
  migrate, nothing to version.
- **The display copy** rides vanilla's own `Scribe_Values.Look(ref title, "title")`
  inside `Pawn_StoryTracker.ExposeData` — a Core key that has been in the save
  format for years.
- **The failure mode is the flat comp namespace.** Because comps share one Scribe
  node, dropping or renaming a comp on this hediff silently discards its saved
  fields, and two comps sharing a key silently clobber. Hence the `archinity_`
  prefix rule and the never-reorder rule above. **T-34**.

### Multiplayer

**Everything on the critical path is either already synced by Multiplayer or
deliberately client-local — with one exception, the Administrator's options.**

| Path | How it is safe |
|---|---|
| Typing the epithet | The dialog is a local window opened from a gizmo action. Only `RenamableLabel`'s setter crosses the wire, and MP registers it automatically for every `IRenameable` type it can serialize. |
| Our comp being serializable | MP registers `HediffComp` with `isImplicit: true` and identifies an instance as (parent `HediffWithComps`, `props.compClass` index). `CompSerialization.hediffCompTypes` is built from `AllSubclassesNonAbstractOrdered(typeof(HediffComp))`, so our class is in it. |
| Entering the altar | `Multiplayer.Client.SyncDelegates`, `SyncMethod.Register(typeof(Building_Enterable), "SelectPawn")`; `Building_Altar` inherits it unmodified. |
| The rite completing | `Building_Altar.Tick` — the synced tick, already the altar's home. |
| *Enter the new reality* (credits) | MP prefixes out `ShipCountdown.ShipCountdownUpdate` (the real-time path) and drives the countdown from `ConstantTicker.TickShipCountdown` instead, calling `CountdownEnded()` on every client from the synced tick. `CancelCancelCountdown` blocks cancellation during play. Ending the game beyond the credits under MP is [#182](https://github.com/cjd721/Rimworld-Archinity/issues/182). |
| The Administrator scene — **the dialog** | A `Dialog_NodeTree` opened from synced code becomes a map-scoped MP `PersistentDialog` and is replayed to every client. Free. |
| The Administrator scene — **the two options** | **Not free.** `DelegateSerialization.IsDeclaringTypeAllowed` admits only 15 declaring types, and neither `Building_Altar` (`Building → Thing`) nor `HediffComp` is among them; a delegate declared on either throws `"Delegate deserialization: method not allowed"` on load. *Stay in this reality* is built with **no action**; *Enter the new reality* hosts its action on `CompAltarThreshold : ThingComp`, and `ThingComp` **is** on the list. Constraint and array recorded in [`docs/engine/determinism.md`](../engine/determinism.md) § *MP serialises the comms-console dialogue, options included* [V]; §4 above states the rules. |
| The credits themselves | `Screen_Credits` is pure UI; `MakeEndCredits` only reads shared state, so both clients build identical text. Its `CurTimeSpeed` write on close is inert — MP replaces `TickManager.TickManagerUpdate` wholesale and drives time by server vote. |

**Divergence gate.** The claim dialog reads nothing that differs between machines:
no `ModSettings`, no `Find.CurrentMap`, no `Prefs`, no wall clock, no `Rand`. The
only value it produces is a string the player typed, and that string reaches the
simulation exclusively through a registered sync method. **Passes.**

**Loudness gate.** A missing sync registration is *not* loud by itself — but
Multiplayer ships a dev debug action, **Dump IRenameable types**, that prints
"Synced IRenameable types" and "Unsynced IRenameable types". `CompFounderRecord`
appearing in the second list is the whole test. **Passes, with the check named.**
The delegate-allowlist failure in the row above is loud by contrast: it throws on load.

**`forcePause` does not pause a multiplayer session.** `Dialog_Rename` sets
`forcePause = true`, and `Find.WindowStack.WindowsForcePause` is consulted by MP in
exactly one place — the time-control hotkey handler — never by its tick loop. One
player typing an epithet does not stop the other's colony. Harmless here; a trap
anywhere it is relied on. **T-53.** Two precisions from the register entry: because
`TickPatch` replaces `TickManagerUpdate` wholesale, vanilla's whole
`Paused` → `ForcePaused` → `WindowsForcePause` chain is *skipped*, not merely ignored —
and MP's single read suppresses only the four speed-change hotkeys, since `TogglePause`
is handled above the guard and still fires.

**The engine fact.** MP's blanket registration of every `IRenameable` `RenamableLabel`
setter is [`docs/engine/determinism.md`](../engine/determinism.md) § *Every `IRenameable` label
setter is a sync method*, and its trap is **T-52** (`docs/traps/multiplayer.md`).

**If a future piece of this system needs a sync method we cannot get for free**,
the route is `Multiplayer.API` — `0MultiplayerAPI.dll` ships inside the Multiplayer
mod, its `MP` static constructor falls back to a `Dummy` implementation when the
Multiplayer assembly is absent, and `MP.enabled` is then false. Reference it, ship
it, guard on `MP.enabled`, call `MP.RegisterSyncMethod`. It is theirs, not a second
assembly of ours. **The recommended design needs none of this, which is why it is not in
the cost table.**

---

## Failure and recovery

| Failure | Detection | Recovery |
|---|---|---|
| Comp is unsynced (MP changed its registration, or `RenamableLabel` is declared on a base class rather than the comp) | Dev action *Dump IRenameable types* lists it under "Unsynced" | Register explicitly with `MP.RegisterSyncMethod` behind `MP.enabled` |
| A `DiaOption` action is declared on `Building_Altar` or `CompFounderRecord` | **Loud, but late** — `"Delegate deserialization: method not allowed"`, thrown on *load*, not at click, so it survives a whole playtest that never reloads | Move the action onto `CompAltarThreshold : ThingComp`, or drop the action and make the option `resolveTree`-only. §4 |
| *Enter the new reality* built without `resolveTree = true` | **Silent — T-97.** *Enter*'s action runs, the dialog never closes inside the synced `Click`, so `WindowStackTryRemove` never fires and `ForceShowDialogs` re-offers the answered ending on every map draw — and hides every later `PersistentDialog` behind it, since only `mapDialogs.First()` is shown | §4 rule 3. `resolveTree = true` on **both** options, without exception |
| A player renames the founder with vanilla's rename window and wipes `story.title` | The label reverts to the backstory title | Nothing breaks: `claimedTitle` is authoritative and `titleClaimed` still gates the rite. Re-mirror on load, or leave it; both are correct |
| The `comps` list on `Archinity_FounderRecord` is edited and the comp is dropped | **Silent.** Fields read as defaults on the next load and the founder appears never to have claimed anything | Prevention only: never edit that list. **T-34** |
| `hediffClass` left at its default `Verse.Hediff` | Loud — `ConfigErrors`: "has comps but hediffClass is not HediffWithComps or subclass thereof". The store never initialises | Set `hediffClass: HediffWithComps`. §1 |
| Both founders claim titles in the same tick | Two commands, server-ordered | Both apply; each founder's comp is a different target. No interaction |

**No campaign softlock exists on this path.** Every gate reads a stored boolean,
and the failure of any single piece degrades to "the altar refuses and says why".

---

## Status

**Evidence class: READ.** Settled from 1.6 defs and decompiled assemblies —
`Assembly-CSharp.dll` (1.6.4871), `Multiplayer.dll` and `MultiplayerCommon.dll`
(`rwmt.multiplayer`, under `AssembliesCustom/`, not the usual path), `VFED.dll`
(`oskarpotocki.vfe.deserters`), `RimPacts.dll` (`wowgag.rimpacts`),
`0MultiplayerAPI.dll`. Corpus verified against `docs/data/MOD-SNAPSHOT.md` at the
start and end of the investigation.

**Verified available mechanisms** — read at source, not selected by this document
alone:

- `Pawn_StoryTracker.title` as a vanilla, scribed, per-pawn free-text title, and
  `Pawn.LabelNoCount` as its display — on the surfaces that call `LabelCap`, which the
  colonist bar does not.
- **No mod in the corpus writes `Pawn_StoryTracker.Title`**, so writing the field collides
  with nothing (see *There is no mod donor…* below for the derivation) [V].
- `Verse.Dialog_Rename<T>` and `Verse.IRenameable` as the text-entry surface.
- Multiplayer's blanket registration of `RenamableLabel` setters.
- Multiplayer's 15-type delegate allowlist as a **hard constraint** on `DiaOption` actions
  inside a `PersistentDialog`, recorded in `docs/engine/determinism.md`.
- `ShipCountdown.InitiateCountdown(string)` → `GameVictoryUtility.ShowCredits(…,
  exitToMainMenu: false)` as a non-terminal victory, and MP's synced ticking of it. Ending
  the game from *Enter* under Multiplayer is not verified: [#182](https://github.com/cjd721/Rimworld-Archinity/issues/182).
- `RoyalTitleDef.Awardable => favorCost > 0` — **confirmed at source**, closing the
  "corroborated, not verified" flag [#21](https://github.com/cjd721/Rimworld-Archinity/issues/21)
  left open.

**Proposed, and [I] until compiled**: that `CompFounderRecord` composes these into
the behaviour described. The mechanisms are each [V]; the composition is not.

**Selected**: nothing; selection is [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.

---

## Available mechanisms

### Vanilla already ships a per-pawn free-text title

`Pawn_StoryTracker.title` is a plain `public string`, scribed by
`Scribe_Values.Look(ref title, "title")`, in **Core** with no DLC gate. `Title`
returns it when set and falls back to the backstory title otherwise;
`Pawn.LabelNoCount` and `LabelNoCountColored` render `Name + ", " +
story.TitleShortCap`. Vanilla's own `Dialog_NamePawn` writes it.

**But `LabelNoCount` is not the label everywhere.** `Verse.Pawn.LabelShort` is
`LabelPrefix + Name.ToStringShort` and carries no title at all, and it is what
`GenMapUI.GetPawnLabel` — and therefore the colonist bar and the in-world map label —
draws [V]. The epithet's storage, persistence and *inspect-pane* display are free; its
display on the bar is not available at all, at any price, without patching vanilla's
label path.

That is still the single largest saving in the design: the only thing we add is the record
that the *rite* happened.

### `Dialog_Rename<T>` is the text-entry surface, and the multiplayer answer

In 1.6, `Verse.Dialog_Rename` is generic: `Dialog_Rename<T> where T : class,
IRenameable`. Its accept path is
`renaming.RenamableLabel = curName; OnRenamed(curName);` — with a `renaming != null`
guard, so even a null target is legal.

`Dialog_Rename.MaxNameLength` is **28**, but the input gate is
`text.Length < MaxNameLength`, so the longest accepted name is **27 characters** [V].
Any cap we choose is an override of that constant, and the effective value is always one
below the number written.

The multiplayer half is the find. `Multiplayer.Client.SyncMethods` registers the
declared `RenamableLabel` setter of **every** `IRenameable` implementor MP can
serialize, enumerated from `GenTypes.AllTypes` via
`TypeCache.CacheTypeHierarchy`'s `interfaceImplementations` map — mod assemblies
included, with no cooperation from the mod. Nine mods in the corpus carry the
`RenamableLabel` identifier in their assemblies (VEF, Adaptive Storage Framework,
VPE, Vanilla Gravship Expanded, Compositable Loadouts and others) — a metadata-heap
hit, so *implementing* versus merely *consuming* is **[I]**; either way the path is
live rather than theoretical.

### There is no mod donor for a player-authored pawn title

The wide pass, both roots, `.dll`, `obj/` excluded:

- `Dialog_NamePawn` / `NamePawnDialog` → **Multiplayer only**, and only to
  auto-resolve an expired baby-birth letter deterministically
  (`SyncDelegates.SetBabyName` generates the name from `thingIDNumber` rather than
  syncing typed text).
- `CustomTitle` / `customTitle` / `claimedTitle` / `selfTitle`, ASCII **and**
  UTF-16LE → RimPacts (a diplomacy pact label) and Compositable Loadouts (a loadout
  name). Neither is a per-pawn epithet.

**How strong that sweep actually is.** #50's resolution claimed each pass was
"control-validated against a known positive in vanilla's `Assembly-CSharp.dll`". That
claim is **not reproducible for the UTF-16LE passes**: `rg -a --encoding utf-16le` misses
strings provably present in the `#US` heap, and does so non-uniformly —
[#103](https://github.com/cjd721/Rimworld-Archinity/issues/103). Read the ASCII half as
validated and the UTF-16LE half as **unvalidated**. The prescribed form in
`docs/agents/capability-research.md` is the broken one; the working form interleaves nulls
into the pattern.

**The negative survives anyway, by a stronger route, and so does the check that matters.**
Intersect the assemblies that reference `Pawn_StoryTracker` with those that carry
`set_Title`: of **146** referencing assemblies, only **EdB Prepare Carefully** and
**Multiplayer** also carry `set_Title`, and **neither writes `story.Title`** [V]. That is
both halves at once —

- *the donor question*: nothing in the corpus ships a player-authored per-pawn title, so
  the build above has to supply it;
- *the collision question*, which the original resolution never ran and which is the one
  that matters for a field we intend to write: **nothing in the corpus writes the field we
  are writing.** No third-party mod will overwrite a claimed epithet.

### Multiplayer suppresses the one vanilla naming dialog it cannot sync

`Multiplayer.Client.Patches.SuppressGravshipNamingDialog` prefixes
`Building_GravEngine.UpdateSubstructureIfNeeded` and forces
`haveShownNameDialog = true` whenever a MP client exists — the gravship naming
window simply never appears in multiplayer.

That is the shape of the hazard this ticket was written against, and it is the
reason the design routes through `IRenameable` rather than inventing a window: the
generic path is supported, the ad-hoc one gets suppressed.

### The declinable victory is vanilla, and two mods already ship it

- `GameVictoryUtility.ShowCredits(string victoryText, SongDef endCreditsSong, bool
  exitToMainMenu = false, float songStartDelay = 5f)` — **the default is to stay in
  the game.**
- `Screen_Credits.PostClose` calls `GenScene.GoToMainMenu()` **only** when
  `exitToMainMenu`. Otherwise `WindowUpdate`'s close path restores
  `TimeSpeed.Normal` and play resumes.
- `ShipCountdown.InitiateCountdown(string launchString)` is a public static with no
  ship and no destruction — the whole fade-and-credits sequence, callable from
  anywhere.
- `VFED.MapComponent_FlagshipFight.DamageFlagship` calls it with a custom string and
  then keeps mutating world state (defeating factions, reassigning settlements),
  proving the game continues.
- RimPacts calls `GameVictoryUtility.ShowCredits(…, false, 2.5f)` on its strategy
  victory, in a `try/catch` that logs and carries on.

`GameEnder` is the only vanilla thing that ends a game for real, and it triggers
solely on "no free colonists anywhere", never on a victory.

### What was ruled out, and why

- **A `GameComponent` with a `Dictionary<Pawn, …>`.** MP can serialize a
  `GameComponent` (`isImplicit: true`), so multiplayer is not the objection.
  Persistence is: scribing pawn *references* in a collection depends on cross-ref
  resolution, and an entry whose pawn is not saved elsewhere resolves to null and is
  dropped **with no error**. Against the loudness gate, a store that travels inside
  the pawn beats a store that points at one.
- **A `ThingComp` on `Human`.** Requires patching a `CompProperties` onto every
  humanlike `ThingDef` in the corpus, gives the comp to every pawn in the world, and
  still misses any race a mod adds later. (Note this is a different thing from
  `CompAltarThreshold`, which sits on *the altar*, is one def, and exists only to be an
  allowed delegate host.)
- **A custom `Window` with a text field.** Buys nothing over `Dialog_Rename<T>` and
  loses MP's automatic registration, the focus handling and the validation report.
- **A custom `ChoiceLetter` for the enter-or-stay choice.** MP registers letter
  options one type at a time (`SyncMethod.LambdaInGetter(typeof(ChoiceLetter_…),
  "Choices", n)`); a custom letter's options are **not** synced and would need
  explicit registration. The Administrator's `Dialog_NodeTree` carries the choice
  instead (§4) — replayed for free, at the cost of the declaring-type rule, which is a
  cheaper constraint than per-option sync registration.
- **`Pawn_RoyaltyTracker.SetTitle` for the epithet.** Confirmed unusable, as #21
  said: `SetTitle(Faction, RoyalTitleDef, bool, bool, bool)` takes a **def**. It
  remains the carrier if psychic ranks carry titles (`PSYCHIC.md` § *What raises psylink
  rank besides the altar* › *Open questions*; on a faction other than the Church), which is
  a different thing on a different surface.

---

## Verification

**Already read (no further work needed):**

| Claim | Anchor |
|---|---|
| `title` is a scribed public string on `Pawn_StoryTracker` | `Assembly-CSharp.dll`, `RimWorld.Pawn_StoryTracker.ExposeData` |
| the epithet displays wherever `LabelCap` is used | `Verse.Pawn.LabelNoCount`; `Verse.InspectPaneUtility.AdjustedLabelFor` |
| the epithet does **not** display on the colonist bar or the map label | `Verse.Pawn.LabelShort`; `Verse.GenMapUI.GetPawnLabel`, `GenMapUI.DrawPawnLabel` |
| no other mod writes the title (collision check) | of 146 assemblies referencing `Pawn_StoryTracker`, only EdB Prepare Carefully and Multiplayer also carry `set_Title`, and neither writes `story.Title` [V] |
| `Dialog_Rename<T>` accept path and null-target guard | `Verse.Dialog_Rename\`1.DoWindowContents` |
| the real name cap is 27, not 28 | `Verse.Dialog_Rename.MaxNameLength` (28) against its `text.Length < MaxNameLength` gate |
| MP registers every `IRenameable` setter | `Multiplayer.Client.SyncMethods` (static init) |
| `HediffComp` is MP-serializable implicitly | `Multiplayer.Client.SyncDictRimWorld` |
| a `PersistentDialog` option's delegate must be declared on one of 15 types | `Multiplayer.Client.DelegateSerialization.allowedDeclaringTypes`, `IsDeclaringTypeAllowed`; `docs/engine/determinism.md` § *MP serialises the comms-console dialogue, options included* |
| comps share one flat Scribe node | `Verse.HediffWithComps.ExposeData` |
| `hediffClass` defaults to `Verse.Hediff` and rejects comps | `Verse.HediffDef.ConfigErrors` |
| `SelectPawn` is synced | `Multiplayer.Client.SyncDelegates`, `SyncMethod.Register(typeof(Building_Enterable), "SelectPawn")` |
| credits do not end the game | `RimWorld.GameVictoryUtility.ShowCredits`, `RimWorld.Screen_Credits.PostClose` |
| MP ticks the countdown deterministically | `Multiplayer.Client.ConstantTicker.TickShipCountdown`, `ShipCountdownUpdatePatch` |
| `Awardable => favorCost > 0` | `RimWorld.RoyalTitleDef.Awardable` |

**Needs a run, and exactly this much:**

1. **One client, dev mode.** Run Multiplayer's debug action **Dump IRenameable
   types** with `Archinity.Altar` loaded. `Archinity.CompFounderRecord` must appear
   under *Synced IRenameable types*. If it appears under *Unsynced*, the automatic
   path failed and the `MP.RegisterSyncMethod` fallback is required. **This single
   check is the entire automatic-sync risk.**
2. **Two clients.** Player A opens the claim dialog and types an epithet; **B then selects
   the founder and B's inspect-pane header must read `"Name, epithet"`**, and
   `Multiplayer > Desync info` must report no desync. (Do **not** test this on the
   colonist bar — the bar draws `LabelShortCap` and will never show the epithet even on a
   correct build.)
3. **Two clients, and a reload.** Trigger the rite; confirm the Administrator
   `Dialog_NodeTree` appears on both clients with both options. **Save while the dialog is
   open and reload** — this is the only way the delegate allowlist is exercised, and a
   wrongly-hosted action throws `"Delegate deserialization: method not allowed"` here and
   nowhere else. Then take *Enter the new reality* and confirm both clients see the fade and
   the credits; what follows the credits is #182's route.
4. **Save/load.** Claim, save, quit, reload; confirm the epithet and the flag survive, and
   that loading a pre-feature save produces no error and no claimed title.

---

## Outstanding decisions

| Question | Consequence | Owner |
|---|---|---|
| *Claim Yourself*: one-way, or re-typeable later | Both are possible: the setter guards on `titleClaimed`, or it does not (§2). Mechanically trivial either way | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119); capability answered here |
| Maximum epithet length | `Dialog_Rename`'s constant is 28 and the real cap is **27**; `Pawn_StoryTracker` imposes none, and `Pawn.LabelNoCount` will render whatever it is given. Overflow risk is on the inspect pane and in letter text, not the colonist bar. | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) |
| The Church title at *Claim Yourself* | Keeping both needs nothing — they coexist without contention (§5). Stripping is possible: VFED's `JoinDeserters` strips Church titles (`RELIGION.md` § *The Schism — revealed, taking the Church's ground, allied for good* › *Route C — VFE Deserters as shipped*) [V]; the vanilla call it uses is [I]. `ENDING.md` says only that the founder no longer *receives* a title | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119); capability answered here |
| Volunteer eligibility as a rite prerequisite | Reads `CompFounderRecord` for the *founder* side. Volunteer-side state needs its own home — see rule 1's scope caveat. | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) ([#49](https://github.com/cjd721/Rimworld-Archinity/issues/49) closed with the capability answered) |
| **Founder psylink / channel progression** | `requirements/ALTAR.md` § *Saved state and remaining work* requires it tracked, in the same sentence that requires the claimed title. **This spec has no field for it.** Capability: `PSYCHIC.md` ([#162](https://github.com/cjd721/Rimworld-Archinity/issues/162), [#163](https://github.com/cjd721/Rimworld-Archinity/issues/163)); the comp is its natural home under rule 1. | Design and any field here: [#31](https://github.com/cjd721/Rimworld-Archinity/issues/31) / [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) |
