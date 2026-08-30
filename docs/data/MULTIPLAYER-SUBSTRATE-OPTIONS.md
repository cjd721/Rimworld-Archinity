# Multiplayer Substrate Options

**Research date:** 2026-08-28
**Question:** we have assumed `rwmt/Multiplayer` (MP) is the substrate. Is that
assumption wrong? **RimWorld Together** (RWT) was named as a candidate.
**Method:** cloned and read RWT's source and decompiled its shipped client
assembly, rather than relying on forum accounts. Companion document:
`MULTIFACTION-FIELD-EVIDENCE.md`.

## Evidence labelling

- **[VERIFIED-CODE]** — read from RWT's repository (`RimWorld-Together/Rimworld-Together`,
  branch `development`, cloned 2026-08-28) or its decompiled `RTClient.dll`.
- **[OFFICIAL]** — the mod's own `About.xml`, README, wiki, or store page.
- **[COMMUNITY]** — forum/Reddit/review anecdote. Unverified.
- **[ABSENCE]** — searched, found nothing. Absence of *reports*, not proof.
- **[SPECULATION]** — my inference.

---

## 1. VERDICT — the hypothesis is CONFIRMED, and more strongly than stated

**RimWorld Together is not a co-op substrate for one shared colony. It is an
asynchronous multi-colony server where each player runs their own independently
simulated game, and colonies interact through discrete events.**

This is not a matter of degree. It is a different genre of mod.

### 1.1 One save file per player, on the server — **[VERIFIED-CODE]**

`Source/Server/PacketManagers/PM_Saves.cs` keys saves by username:

```csharp
public static bool CheckIfUserHasSave(ServerClient client)
{
    string[] saves = Directory.GetFiles(Master.SavesPath);
    foreach (string save in saves)
        if (Path.GetFileNameWithoutExtension(save) == client.GetData<FL_Player>().Username)
            return true;
    return false;
}

public static void ResetPlayerData(ServerClient client, string username)
{
    BackupManager.BackupUser(username);
    string path = Path.Combine(Master.SavesPath, username + CommonValues.DefaultSaveFormat);
    if (File.Exists(path)) File.Delete(path);
    FL_Site[] playerSites = PM_Sites.GetAllSitesFromUsername(username);
    // ... deletes that user's sites and settlements
}
```

**Each player has their own save, their own colony, their own simulation.** The
server is a persistence and message-routing layer, not a simulation authority.

### 1.2 The server's vocabulary is inter-colony diplomacy — **[VERIFIED-CODE]**

The complete packet-manager set (`Source/Server/PacketManagers/`) is:

```
PM_Aid          PM_Caravan      PM_Chat        PM_Events      PM_GameParameter
PM_Guilds       PM_Handshake    PM_Information PM_Leaderboard PM_Login
PM_Map          PM_Market       PM_Mods        PM_Pollution   PM_Raid
PM_Recount      PM_Rivers       PM_Roads       PM_Saves       PM_ServerPassword
PM_SettlementCustomization      PM_Settlements PM_Sites       PM_Synchronous
PM_Transfers    PM_Version      PM_World       PM_WorldObject PM_Zoom
```

Note what is present — `Market`, `Guilds`, `Leaderboard`, `Raid`, `Aid`,
`Transfers` — and what is **absent**: no tick synchronisation, no command queue,
no RNG state, no desync detection. There is nothing resembling MP's lockstep.

### 1.3 The authors describe it this way themselves — **[OFFICIAL]**

`About/About.xml`:

> "Join a playstyle in which other players will actually be able to **affect**
> you! Chat with them, trade with them, **spy on them, raid them**, build sites
> with them or even **visit them** in real time!"

and, in the same file, self-classified:

> "an **early access** community project"

### 1.4 The "synchronous session" — real, but not what we need — **[VERIFIED-CODE]**

RWT does have a real-time mode. It is far narrower than the name suggests.
From the decompiled `RTClient.PacketManagers.Synchronous.PM_Synchronous`:

**It is invite-based and strictly two-party.** The flow is
`Ask → Accept/Reject → Start → Action`, and the server routes actions to exactly
one counterpart (`SynchronousClientID`, singular).

**The guest downloads a snapshot of the host's map and instantiates a local
copy:**

```csharp
private static void SetMap(SynchronousSide side, PKT_Synchronous data)
{
    if (side == SynchronousSide.Host) { SessionManager.SynchronousMap = Find.AnyPlayerHomeMap; return; }
    SessionManager.SynchronousMap =
        MapSaveLoader.StringToMap(Serializer.ConvertBytesToObject<FL_Map>(data.Data, compression: false), enforceIDs: true);
    foreach (Pawn item in SessionManager.SynchronousMap.mapPawns.AllPawns.Where(f => f.Faction == Faction.OfPlayer))
    {
        if (data.CurrentType == PKT_Synchronous.Type.Visit) item.SetFactionDirect(SessionManager.AllyFaction);
        else                                                item.SetFactionDirect(SessionManager.EnemyFaction);
    }
}
```

**Three findings here are decisive:**

1. **The visitor's pawns are re-factioned to `AllyFaction` or `EnemyFaction`.**
   The two players are *never* one faction. Even at maximum togetherness, RWT
   models this as two factions meeting.
2. **The guest arrives as a caravan** —
   `CaravanEnterMapUtility.Enter(SessionManager.ChosenCaravan, ...)`. Being
   together requires world travel.
3. **You cannot save.** Both host and guest are shown, verbatim:

   > `"Game will be unable to save while in synchronous!"`

**A mode that blocks saving cannot host a 600-day campaign.** It is a bounded
encounter you enter, resolve, and leave.

**What it syncs is discrete actions, not simulation:** the entire hook set is
`PlayerDraft`, `PlayerJob`, `PlayerDestroy`, `PlayerHediff`, `PlayerMentalState`,
`PlayerGameSpeed`, `PlayerWeather`. **[SPECULATION, well-grounded]** Mirroring
*jobs* rather than deterministic ticks means the two copies drift continuously
and by design; there is no mechanism that could detect or correct it. RWT has no
desync class because it has abandoned the guarantee that would produce one.

---

## 2. Does the architecture dissolve or relocate our problems?

**It dissolves the multifaction problem completely — by removing the shared
simulation that created it.**

| Problem from the multifaction audit | Under RWT |
|---|---|
| `Faction.OfPlayer` context swapping | **Gone.** One player faction per process. |
| Synthetic Spectator faction | **Gone.** No such concept. |
| Eight swapped managers (`ResearchManager` etc.) | **Gone.** Each client has one of each. |
| `FactionContext.Push` / `RecacheFactions` traps | **Gone.** |
| Deterministic-lockstep desyncs | **Gone.** No lockstep to break. |
| Silent, save-corrupting faction bugs | **Gone.** |

**But the cost is the thing we actually want.** There is no shared colony. The
two players do not co-operate on one settlement; they run two settlements and
trade, raid, visit, and message each other. Every want on the user's list that
depends on *one shared colony* becomes either free-by-irrelevance or impossible.

**Answering the specific sub-questions:**

- **Can two players be on the same map at once?** **[VERIFIED-CODE]** Yes, but
  only inside a synchronous session: temporary, invite-based, caravan-mediated,
  two-party, **unsaveable**, and with the visitor's pawns belonging to a
  different faction.
- **Is real-time co-op on one colony possible?** **[VERIFIED-CODE]** **No.** Not
  as a persistent mode. The save block alone forecloses it.
- **Is it asynchronous "two colonies that visit each other"?** **[VERIFIED-CODE
  + OFFICIAL]** Yes. Exactly that.

---

## 3. Scoring RWT against the user's actual wants

The user's list, item by item.

| Want | RWT | Why |
|---|---|---|
| See only **my own pawns** in the colonist bar | **Free (trivially)** | You only *have* your own pawns. **[VERIFIED-CODE]** |
| See only **my own quests** | **Free** | Separate `QuestManager` per client. |
| See only **my own letters** | **Free** | Separate `LetterStack` per client. |
| **No cross-contamination of mood** | **Free — and total** | Separate colonies, separate `ThoughtWorker` evaluation. This is the want RWT satisfies most completely. |
| **No UI collisions** (build orders, designators) | **Free** | Separate processes; no shared designator state. |
| **Shared research progress** | **IMPOSSIBLE without building it from scratch** | See below. |
| **Two concurrent research projects** | **Impossible** (same reason) | |
| One shared colony (the campaign's premise) | **Impossible** | Architectural. |

### The research finding — **[VERIFIED-CODE]**, and it is disqualifying

I grepped both halves of RWT for research handling:

- Decompiled `RTClient.dll` (187 files): **zero** references to `ResearchManager`
  or `ResearchProjectDef`.
- `Source/Server` (81 files): **zero** case-insensitive matches for "research".

The **only** research-adjacent code in the entire mod is one difficulty
parameter:

```csharp
Current.Game.storyteller.difficulty.researchSpeedFactor = file.ResearchSpeedFactor;
```

**RWT has no research sharing of any kind, and no channel through which to add
it.** Every colony researches independently. Building shared research would mean
inventing a sync protocol, adding packet types on both client and server, and
reconciling two independently-ticking `ResearchManager`s with no common clock —
a distributed-consistency problem, not a Harmony patch.

**Net:** RWT gives us five of the user's wants for free, but it gives them by
deleting the shared colony that is the campaign's entire premise. It cannot
deliver shared research, and it cannot deliver one colony. **The five "free"
wins are free because the thing they were meant to make bearable no longer
exists.**

---

## 4. Maturity, activity, and mod compatibility

### 4.1 Health — genuinely good, better than expected — **[VERIFIED-CODE / OFFICIAL]**

Via GitHub API, 2026-08-28:

| Metric | RWT | MP |
|---|---|---|
| Stars | 253 | 665 |
| Forks | 62 | — |
| Open issues | **4** | ~200+ (982 total lifetime) |
| Last push | **2026-08-27** (yesterday) | 2026-08-03 |
| Latest release | `26.8.16.1_(1)`, **2026-08-21** | `v0.11.5`, 2026-04-29 |
| Releases in 2026 | **15** | 5 |
| Archived | No | No |

RWT ships more often than MP and its issue tracker is nearly empty. **[SPECULATION]**
Four open issues against 253 stars more likely reflects a small user base and/or
triage-by-Discord than an absence of bugs — read it as "not abandoned", not as
"nearly bug-free". Subscriber and open-issue comparisons are in §4.3.

> **Read §4.4 before treating the release cadence as good news.** Field evidence
> shows RWT's *server-side save format* has broken across version upgrades more
> than once, so a two-week release cadence is a hazard for a long campaign rather
> than a reassurance. This corrects the framing in this subsection.

**[OFFICIAL]** `About.xml` declares `<supportedVersions>1.5, 1.6</supportedVersions>`
and `loadAfter` includes `Ludeon.Rimworld.Odyssey`, so 1.6 + current DLC is
genuinely targeted, not aspirational.

### 4.2 Mod compatibility — structurally better than MP, and this is real

**[VERIFIED-CODE]** RWT needs **no per-mod compatibility shims**. There is no
analogue of `rwmt/Multiplayer-Compatibility` in the repo, and none is needed:
because each player simulates their own colony independently, a mod's behaviour
never has to match another client's tick-for-tick. Determinism is simply not a
requirement.

This is a genuine architectural advantage and it directly addresses the 125-mod
risk that dominates the MP analysis. What RWT must agree on is only that both
players **loaded the same mods** — enforced by `PM_Mods` with per-mod
`ModType.Required` / `ModType.Optional` (**[VERIFIED-CODE]**,
`PM_Mods.cs:81`), plus a forbidden list **[OFFICIAL]**, README.

**One concrete incompatibility — [VERIFIED-CODE]**, `About.xml`:

```xml
<incompatibleWith><li>jikulopo.prepatcher</li></incompatibleWith>
```

Worth flagging because **MP hard-*requires* `zetrith.prepatcher`**. The package
ids differ (`jikulopo` is a fork), so this is not automatically a head-on
collision, but the two mods have opposite postures toward Prepatcher and are not
plausibly co-installable.

**[SPECULATION]** The mod-agnosticism is only as good as the synchronous
session, which *does* serialise a whole map across the wire
(`MapSaveLoader.StringToMap`). A map full of modded things must deserialise
correctly on the other client. That is a much weaker requirement than
determinism, but it is not nothing.

### 4.3 User base — RWT is real, but roughly a quarter of MP

**[OFFICIAL]** Steam Web API `GetPublishedFileDetails`, queried 2026-08-28:

| | RWT (3005289691) | MP (2606448745) |
|---|---|---|
| Current subscribers | **113,243** | **463,524** |
| Lifetime subscribers | 203,353 | 730,205 |
| Favourites (current) | 8,171 | 32,719 |
| Unique visitors | 302,387 | 767,346 |
| Ratings count | 1,689 | 6,806 |
| Posted | 2023-07-16 | 2021-09-19 |
| Last updated | 2026-08-20 | 2026-06-08 |
| `banned` flag | 0 | 0 |

**RWT is ~24% of MP's current subscriber base.** Not niche, but clearly the
smaller ecosystem — which matters for how much community troubleshooting exists
when something breaks.

**Correction worth recording:** fetching the Steam HTML for RWT twice produced a
"removed for violating Content Guidelines" string. That is boilerplate markup in
the page, not a status. The API returns `banned: 0, result: 1` for both mods.
**Both are live.** Anyone re-running this research will hit the same trap.

**[OFFICIAL]** Issue-tracker asymmetry: MP carries **105 open issues**; RWT
carries **4**. Combined with the subscriber ratio, **[SPECULATION]** RWT's near-empty
tracker reflects a smaller user base plus Discord-first triage, not a
near-bug-free mod.

### 4.4 IMPORTANT CORRECTION — high release cadence is a *liability* here

In §4.1 I read RWT's 15 releases in 2026 as a health signal. **The field evidence
inverts that for our use case**, and this is the most decision-relevant finding
the community research produced.

**[OFFICIAL, RWT issue tracker]** Server version upgrades are the documented
main threat to a long RWT save:

- **#312** (2026-08-21) — a `FactionDef` → `FactionDefName` rename **turned all
  NPC world objects hostile** on server upgrade.
- **#302** (2026-04) — a JSON format migration **broke existing servers on
  auto-update**.
- **#301** — `SyncLocalSave` **overwrote user backups**, preventing rollback.
- **#273** — viewing another player's settlement caused **duplicate load IDs and
  corruption**.

**[SPECULATION, well-grounded]** For a 600-day campaign this is a serious risk
class that MP largely does not have: MP is a client-side mod whose saves are
plain RimWorld saves, whereas RWT's server owns a bespoke on-disk format
(`Master.SavesPath`, site/settlement files, `ModConfig.json`) that has already
broken across versions more than once — including one incident that destroyed the
backups you would roll back to. Shipping every two weeks against a format like
that is a hazard, not a reassurance, unless the server version is pinned and
Steam auto-update disabled.

### 4.5 Mod-agnosticism is real but not total — **[OFFICIAL]**

Confirmed via the RWT wiki (`Adding_Mods_and_DLCs`): three server-side
categories — **Required/Enforced**, **Optional**, **Forbidden** — and since
v26.6.8.1 a server may allow any mods if no required list is set. The wiki
advises enforcing anything touching **factions, biomes, or world events**. DLCs
are configured by hand-editing `ModConfig.json`.

The structural claim in §4.2 holds: **RWT ships no per-mod shim layer**, against
`rwmt/Multiplayer-Compatibility`'s **198 per-mod source files** (counted
2026-08-28). RWT maintains a blocklist instead.

But the exemption is not total. **[OFFICIAL]** Documented breakage classes: mods
that relocate save folders break upload; other complex multiplayer mods are hard
incompatible; **mods bypassing vanilla caravan code break raid/spy/visit**. And
concretely, issues **#303/#305** (2026-04) are **Humanoid Alien Races framework
incompatibility, re-broken after a prior fix** — a major framework that required
targeted work despite the architecture.

**[ABSENCE]** No official statement of a mod-count ceiling exists, and **no
primary source confirms or denies 100+ mods** on RWT. Commercial host marketing
pages claim heavy modlists work; those are low-trust and are not counted here.
Also note the official `RimWorld-Together/Incompatibilities` repo **now 404s** —
the canonical blocklist is missing or moved, and the surviving Fandom mirror was
unfetchable (HTTP 402). **Searched, could not retrieve.**

### 4.6 Long-campaign accounts — **[ABSENCE]**

**No substantive account of a long RWT campaign with hours or in-game day counts
was found**, across Reddit (crawler-blocked), YouTube, Ludeon, and Steam. YouTube
returned setup guides and one playlist explicitly marked "(Hiatus)". This is
absence of evidence, not evidence of absence — but it means **neither substrate
has a documented 600-day precedent.**

**A sourcing warning that also corrects my earlier round:** much search-engine
material attributed to "RimWorld Together" (crash-every-5-minutes,
desync-every-2-3-minutes, async-time bugged since 1.4) is in fact about
*Zetrith's MP*. Summarisers conflate the two mods routinely. No clean,
RWT-attributable review anecdote was recovered. Treat any second-hand RWT
stability claim as suspect unless it names the mod's own version scheme.

### 4.7 One apparent contradiction, resolved

**[OFFICIAL]** The RWT wiki's *Introduction* states players "co-exist on the
world map instead of traditional coop play", that **time runs independently per
player**, and that real-time syncing is *planned* — corroborated by open issue
**#310 "[FEAT] Time synchronization"** (2026-06-17, still open). On its face this
conflicts with the synchronous-session code I read in §1.4.

**Resolution — [SPECULATION], but the readings are compatible and the code is
authoritative:** these describe two different things. #310 concerns **global,
persistent time synchronisation** — making both players' independently ticking
colonies advance on a common clock, which genuinely does not exist. What I
verified in shipped code is a **temporary, bounded encounter** with its own
action mirroring, which is not global time sync and does not require it.

**Both facts point the same way:** normal RWT play has each colony ticking on its
own clock, and the synchronous session is a bracketed exception you enter and
leave. That is the asynchronous architecture, confirmed from two independent
directions. The wiki does not refute §1.4; it describes the steady state that
§1.4's session is an exception to.

### 4.8 Known-broken surface — **[OFFICIAL]**, issue tracker themes

Connection/KeepAlive drops on alt-tab (#279); trade window errors (#276/#277);
**sending pawns as aid corrupts them (#296, still open)**; an idle empty server
burning 30–40% CPU (#282/#287); non-admins able to enable dev mode (#270); UI
tabs unresponsive (#272); colony-move NREs (#268). Turnaround is fast — 4 open of
~40 sampled.

---

## 5. Other options

**[VERIFIED-CODE]** GitHub survey by stars, 2026-08-28. **Only two live projects
exist.** Everything else is dead:

| Project | Stars | Last push | Status / approach |
|---|---|---|---|
| `rwmt/Multiplayer` | 665 | 2026-08-03 | **LIVE.** Deterministic lockstep, one simulation. The incumbent. |
| `RimWorld-Together/Rimworld-Together` | 253 | 2026-08-27 | **LIVE.** Client-server, one colony per player, event sync. |
| `Zetrith/Multiplayer` | 453 | 2020-07-18 | **DEAD.** The original; `rwmt` is the continuation fork. Not a separate option. |
| `D12-Dev/OpenWorld` | 97 | 2023-05-05 | **DEAD.** "A Free Multiplayer Mod For Rimworld". |
| `Longwelwind/Phi` | 48 | 2019-03-04 | **DEAD.** Item/pawn exchange between separate colonies — an early, narrower ancestor of the RWT model. Instructive only as precedent that the asynchronous approach long predates RWT. |
| `havietisov/RimAlong` | 29 | 2019-01-10 | **DEAD**, self-labelled "[Ceased]". |
| `pardeike/RimBattle` | 4 | 2021-04-19 | **DEAD.** Multi-team mod by the Harmony author; described in MP issue #9 as incomplete/broken. |
| `AriAlavi/rimlink` | 3 | 2021-07-06 | **DEAD.** File-sync desync workaround, not a multiplayer layer. |
| `reuyu/rimworld-HybridMultiplayer` | 0 | 2026-01-06 | **Negligible.** 0 stars, empty README, "Multiplayer + Rimworld-Together". Not a maintained option. |
| `coolnether123/RimworldMultiplayer` | 10 | 2025-12-08 | **Semi-alive MP fork** for 1.6. The only third-party MP fork with any activity; not a distinct architecture. Worth knowing exists if we ever need a patch MP upstream won't take. |
| `StateofDisarray/RimworldMultiplayer` | 0 | 2025-07-12 | **Effectively dead** MP fork for 1.6. |
| "Rimworld Multiplayer 2025" (Workshop 3408292453) | — | 2025-01-16 | **Dead.** 0 subscribers, 1,050 views. Named only to rule it out. |

**Conclusion: the choice is genuinely binary — MP or RWT.** There is no third
live substrate and no promising fork to adopt. **[ABSENCE]** I searched GitHub by
stars and by keyword; a private or unlisted project would not appear.

---

## 6. The honest comparison

Against the user's want-list plus cost, failure mode, mod risk, and 600-day
plausibility. Grounding for the MP columns is in `MULTIFACTION-FIELD-EVIDENCE.md`.

| | **MP shared + our presentation layer** | **MP multifaction** | **RimWorld Together** |
|---|---|---|---|
| Only my pawns in colonist bar | **Build it** — ~30-line Postfix on `ColonistBar.CheckRecacheEntries`; MP ships a faction-keyed reference implementation to copy | Free (MP's `hideOtherPlayersInColonistBar`) | **Free** (you only have your own) |
| Only my quests | **Build it** — copy MP's 3 `MainTabWindow_Quests` patches, re-key to owner | Free (`hideOtherPlayersQuests`) | **Free** |
| Only my letters | **Build it** — copy `LetterStackReceiveOnlyMyFaction`, re-key | Free | **Free** |
| Shared research | **Free** (one `ResearchManager`) | **Lost** — split per faction; and MP shipped a bug losing it on reconnect (#585) | **Impossible** — zero research code in the mod |
| Two concurrent projects | **Build it** — ~40-line Prefix on `ResearchPerformed`; progress is already a per-project dictionary | Not applicable | **Impossible** without inventing a sync protocol |
| No mood cross-contamination | **NOT POSSIBLE** — one faction, one colony, shared thoughts. The known hard limit | **Free** — separate colonies | **Free and total** |
| No UI collisions | **Partly** — MP syncs designators with no arbitration; needs bespoke work | Mostly free | **Free** (separate processes) |
| One shared colony | **Yes** | Sort of (two colonies) | **No** — architecturally impossible |
| **(a) Engineering cost** | **Medium.** ~5 client-local patches, all with MP reference implementations; plus a synced ownership tag and the research prefix | **Very high.** Unsanctioned internals, no public API, no prior art, patterns 4-5 unfixable | **Low for what it gives, infinite for what we want.** Shared research is a research project |
| **(b) Failure mode** | **VISIBLE.** UI caches, never serialised, never read by the tick path. Wrong pixel this frame, one client, fixed by reload | **SILENT.** Deterministic, invisible to `CheckForDesync` (RNG-only), written identically into both saves. The worst profile | **VISIBLE but lossy.** No desync class at all; synchronous sessions drift by design and cannot be saved |
| **(c) Mod-set risk (125 mods)** | **High.** Determinism required of every mod; no documented shared game above ~10 mods | **Extreme.** Determinism *plus* faction-context correctness; compat ratings are blind to multifaction | **Low.** Mod-agnostic by architecture — its single best property |
| **(d) 600-day campaign plausible?** | **Plausible but undocumented.** No published shared campaign with a day count; failures are recoverable | **Not advisable.** Silent divergence accumulates with no rollback point | **Not our game, and riskier than it looks.** A 600-day two-colony server is plausible *only* with the server version pinned — upgrades have broken saves and destroyed backups (§4.4). A 600-day shared colony is not available at all |

**[ABSENCE]** Note for all three columns: **neither substrate has a documented
600-day precedent.** No published campaign with a day count was found for MP
shared mode, MP multifaction, or RWT. Whichever we choose, we are the experiment.

### Recommendation

**[SPECULATION, but tightly grounded in the verified findings above]**

**RWT is not a substitute for MP for this campaign, and the assumption we have
been carrying is correct.** It should be rejected on architecture, not on
maturity — its mod-agnosticism is a real advantage we cannot get anywhere else,
and it is actively maintained. But it cannot host one shared colony, it cannot
share research (zero research code exists in it), and its only real-time mode
cannot save. Adopting it would mean abandoning the premise of the campaign, not
implementing it differently.

Two caveats to the "healthier than MP" reading, both from field evidence: RWT is
**~24% of MP's subscriber base** (§4.3), so there is far less community
troubleshooting to draw on; and its **high release cadence is a liability**, not
an asset, because its bespoke server save format has broken across upgrades and
one incident destroyed the backups needed to roll back (§4.4).

**The pivot already chosen — MP shared mode plus a client-local presentation
layer — remains the best available option**, and this investigation strengthens
rather than weakens it: the alternative that dissolves our problems does so only
by dissolving the campaign.

**The one thing RWT proves that is worth carrying forward:** the wants "only my
pawns / my quests / my letters" are *free* when the simulation is separate and
*constructed* when it is shared. Our presentation layer is buying, at medium
engineering cost, the subjective experience RWT gets structurally. That trade is
sound — but it comes with a hard limit that should be stated plainly and
accepted before work starts: **shared mood is not solvable by a presentation
layer.** RWT is the only option that fixes it, and its price is the shared colony
itself.

## Sources

- [RimWorld-Together/Rimworld-Together](https://github.com/RimWorld-Together/Rimworld-Together) — cloned `development`, 2026-08-28
- [RWT Steam Workshop 3005289691](https://steamcommunity.com/sharedfiles/filedetails/?id=3005289691) · [RWT wiki](https://rimworldtogether.wiki.gg/)
- [rwmt/Multiplayer](https://github.com/rwmt/Multiplayer) · [MP Steam Workshop 2606448745](https://steamcommunity.com/sharedfiles/filedetails/?id=2606448745)
- Decompiled `Source/Assemblies/RTClient.dll` (187 files) via `ilspycmd`
- [RWT wiki: Adding Mods and DLCs](https://rimworldtogether.wiki.gg/wiki/Adding_Mods_and_DLCs) · [RWT wiki: Introduction](https://rimworldtogether.wiki.gg/wiki/Introduction)
- Steam Web API `GetPublishedFileDetails` for 3005289691 and 2606448745, queried 2026-08-28
- RWT issue tracker: #273, #296, #301, #302, #303, #305, #310, #312
- Companion analysis: `docs/data/MULTIFACTION-FIELD-EVIDENCE.md`
