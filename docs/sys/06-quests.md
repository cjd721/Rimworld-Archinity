# 06 — Quests & rewards

**Blocked by 05** (a quest that sends you to a faction needs the faction settled).

**Read `QUESTLINE.md` alongside this brief.** It defines the beats, acts and vectors this
document schedules; the two are not separable. Nothing here specifies beat *content* —
`QUESTLINE.md` does.

## What this system must do

Three jobs, in priority order:

1. **Keep the Chronicle's beats on their intended schedule** — already solved.
2. **Suppress competing quest noise** so the player is not buried under vanilla and
   third-party quests on top of ours.
3. **Deliver specific, named items reliably** as quest rewards, so research gating on
   quest-obtained items actually works.

## Do we need a custom storyteller? No.

Verified and settled. Chain quests call `CreateQuest()` directly and **bypass the
storyteller entirely**, so the Chronicle's pacing is already fully under our control.

A storyteller would only help with job 2 — suppressing competing noise — and the cheap
lever for that is quest incident frequency plus `rootSelectionWeight` patches. Not worth a
second assembly, which we have ruled out anyway.

`StorytellerUtility.GetProgressScore = freeColonistCount×1 + wealth×0.0001`. Research
contributes **nothing**, so `rootMinProgressScore` cannot be used to pace anything against
tech progress.

## Beat scheduling — the mechanism

VEF's `QuestChainExtension` + `GameComponent_QuestChains`. Beats gate on **research
completion, not day timers** (VEF postfixes `FinishProject`). `QuestChainExtension.requiredResearch`
blocking `TryScheduleQuest` is the only verified tech gate on quest appearance.

### The trap — recorded because it cost a session

**Killing VQE Ancients' questline: remove the `QuestChainExtension` modExtension from all
six quest defs. Nothing else works.**

- Stripping `conditionMinDaysSinceStart` **fires the quest on day 1** —
  `TryScheduleQuest` falls through to `quest.CreateQuest()` when no condition matches.
- Deleting the root def is worse — the other five name it in `conditionSucceedQuests`,
  unresolvable cross-references are omitted rather than nulled, their lists go empty, and
  **all five fire at once.**
- Removing the extension is clean: `QuestsInChains` filters on the extension being non-null,
  and `rootSelectionWeight` defaults to 0 so the storyteller cannot pick them up either.

Both verified against the decompile.

## Quest noise suppression

- `rootSelectionWeight 0` = give-only; the storyteller cannot select it. **This is the main
  lever.** Patch it onto quests we want gone.
- Ignorance Is Bliss `changeQuests` only swaps the threat faction — **it never suppresses**.
  Do not expect it to help.
- `QuestScriptDef.CanQuestOccurOnTile` reads `layerWhitelist` / `layerBlacklist` /
  `everAcceptableInSpace` / `neverPossibleInSpace` against the **player's** tile, not the
  site's. Relevant once the endgame moves to orbit.
- `[?] minRefireDays` and root-selection weighting internals are **not yet researched**.
  If global throttling is wanted beyond per-quest weights, that is an open research item.

## Fixed rewards — how to hand the player a named item

Deterministic rewards are the backbone of "I need item X, this quest gives it."

| Mechanism | Status |
|---|---|
| `QuestNode_SetItemStashContents` | **Verified, shipped** — Royalty `Script_Intro_Deserter.xml:90`. The safest option. |
| `QuestNode_GenerateThing` + `QuestNode_AddItemsReward` | Verified in code, **no shipped XML example**. Bypasses ThingSetMaker filters, budgets, techprint and `PlayerAcquirable` gates — the hard way to hand out out-of-tier items. |
| `QuestNode_GiveRewards` | **Can never be made fixed.** Do not try. |
| `ThingSetMaker_Count` / `_StackCount` | The only deterministic ThingSetMakers. There is no `ThingSetMaker_Fixed`. |

`QuestNode_GenerateThing` gotchas: must nest under a signal node or the item drops on
accept; needs `slate["map"]`; `stackCount` is unclamped against `stackLimit`; non-stuffable
things only.

## Site inventory for the Chronicle

Survives killing VQE's questline — only the scheduling extension is removed, not the content.

| Layout set | Count | Shape | Use |
|---|---:|---|---|
| `VQEA_AncientOvergroundComplex_1..12` | 12 | Surface complex | Act openers and closers |
| `VQEA_VaultLabModules` + `VQEA_SealedVault` | — | Underground, locked vault door + ramp | Medium beats |
| `VQEA_SidequestLabModules_1..10` | 10 | One small lab room | Small beats |

Six `SitePartDef`s with difficulty flavour already written: *abandoned*, *dangerous*,
*infested*, *reconnaissance*, *array*, *research vault*. Two map generators:
`VQEA_AncientComplex` (overground), `VQEA_SealedVault`.

## Side quests — the QoL item delivery channel

Per `sys/04`, a small set of high-value non-progression items are earned rather than
researched. Quests are one of the two supply routes (raiding is the other, see `sys/05`).

The design requirement from `Player Progression Ideology.txt` is that the player can
**reason about where to get a thing** — not guess. Whatever we build here must make the
source legible: the quest description, the research description, or both, should name what
it yields.

## Work items

- [ ] Strip `QuestChainExtension` from VQE Ancients' six quest defs. Do not touch conditions
      or delete defs.
- [ ] Build `Archinity.Chronicle` — not started. Beat scheduling on research completion.
- [ ] Author the beat quests per `QUESTLINE.md`. **Act I is settled and buildable now**;
      Acts III–VI wait on D3/D4/D5.
- [ ] Choose the fixed-reward mechanism per beat. Prefer `QuestNode_SetItemStashContents` —
      it has a shipped precedent.
- [ ] Sweep the load order for quests worth suppressing; patch `rootSelectionWeight` to 0.
- [ ] **Open research:** `minRefireDays` and global quest-frequency throttling. Only needed
      if per-quest weights prove insufficient in play.
- [ ] Author the side-quest set that supplies the `sys/04` QoL ledger. Keep it small.
- [ ] Make the item source legible to the player. Mechanism undecided — descriptions are
      the cheap option.
- [ ] Note: vanilla bug — `OpportunitySite_MechanoidPlatform` is gated on the **Insect**
      faction existing. Relevant if we prune factions in `sys/05`.
