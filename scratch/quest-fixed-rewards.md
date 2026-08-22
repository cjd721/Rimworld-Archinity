# Fixed / deterministic QuestScriptDef rewards in pure XML (RimWorld 1.6)

**Verdict: YES.** A `QuestScriptDef` can deliver an exact, named, fixed-count item set on quest
success with zero C#. The mechanism is `QuestNode_GenerateThing` (builds the exact `Thing`) +
`QuestNode_AddItemsReward` (registers it as a real quest Reward and generates the delivery
`QuestPart_DropPods`), gated inside a signal node so it fires on success.

Everything below is confirmed from decompiled `Assembly-CSharp.dll` (RimWorld 1.6, ilspycmd) and
from shipped Core/Royalty/Odyssey def XML. Anything I could not confirm is flagged explicitly.

---

## 1. The recommended pattern

```xml
<?xml version="1.0" encoding="utf-8"?>
<Defs>
  <QuestScriptDef>
    <defName>Archinity_FixedRewardExample</defName>
    <rootSelectionWeight>0</rootSelectionWeight> <!-- give-only, not storyteller-selectable -->
    <root Class="QuestNode_Sequence">
      <nodes>

        <!-- 1. Build the exact reward items. No filters, no loot table, no RNG. -->
        <li Class="QuestNode_GenerateThing">
          <def>ArchiteCapsule</def>
          <stackCount>2</stackCount>
          <addToList>fixedRewardItems</addToList>
        </li>
        <li Class="QuestNode_GenerateThing">
          <def>VQEA_ArchogenInjector</def>
          <stackCount>1</stackCount>
          <addToList>fixedRewardItems</addToList>
        </li>

        <!-- 2. Deliver them when the success signal fires. -->
        <li Class="QuestNode_AllSignals">
          <inSignals>
            <li>site.SurveyCompleted</li>   <!-- your own success signal -->
          </inSignals>
          <node Class="QuestNode_Sequence">
            <nodes>
              <li Class="QuestNode_AddItemsReward">
                <items>$fixedRewardItems</items>
              </li>
              <li Class="QuestNode_End">
                <outcome>Success</outcome>
              </li>
            </nodes>
          </node>
        </li>

      </nodes>
    </root>
  </QuestScriptDef>
</Defs>
```

This is structurally identical to Odyssey's shipped
`Data/Odyssey/Defs/QuestScriptDefs/Script_Site.xml:176-203` — the only difference is that Odyssey
fills the slate var with a random `QuestNode_GenerateThingSet`, and we fill it with deterministic
`QuestNode_GenerateThing` calls.

---

## 2. Evidence — decompiled source

### 2.1 `QuestNode_GenerateThing` is fully XML-drivable and 100% deterministic

`RimWorld.QuestGen.QuestNode_GenerateThing` (Assembly-CSharp.dll):

```csharp
public class QuestNode_GenerateThing : QuestNode
{
    [NoTranslate] public SlateRef<string> storeAs;
    [NoTranslate] public SlateRef<string> addToList;
    public SlateRef<ThingDef> def;
    public SlateRef<int?> stackCount;
    public SlateRef<IEnumerable<Thing>> contents;

    protected override bool TestRunInt(Slate slate) => true;

    protected override void RunInt()
    {
        Slate slate = QuestGen.slate;
        Thing thing = ThingMaker.MakeThing(def.GetValue(slate));
        thing.stackCount = stackCount.GetValue(slate) ?? 1;
        if (contents.GetValue(slate) != null)
            thing.TryGetInnerInteractableThingOwner()?.TryAddRangeOrTransfer(contents.GetValue(slate));
        if (storeAs.GetValue(slate) != null)
            QuestGen.slate.Set(storeAs.GetValue(slate), thing);
        if (addToList.GetValue(slate) != null)
            QuestGenUtility.AddToOrMakeList(slate, addToList.GetValue(slate), thing);
    }
}
```

Key points:
- `ThingMaker.MakeThing(def)` — no `ThingSetMaker`, no filter, no market-value budget, no
  `ThingSetMakerUtility.GetAllowedThingDefs` gate. It bypasses **all** the reward-generator
  eligibility rules (`PlayerAcquirable`, techprint checks, royal-title checks, `maxThingMarketValue`).
- `thing.stackCount = stackCount ?? 1` — assigned raw, **not** clamped to `def.stackLimit`.
  For `ArchiteCapsule` (`Biotech/Defs/ThingDefs_Items/Items_Various.xml:84,105` — `stackLimit` 25)
  a count of 2 is safe. If you ever want more than `stackLimit`, emit multiple
  `QuestNode_GenerateThing` nodes instead of one oversized stack.
- No `stuff` argument is passed, so **stuffable** defs would get `null` stuff. Fine for
  ArchiteCapsule / injectors (non-stuffable). Do not use this node for stuffable items unless you
  verify the def is non-stuffable.
- `TestRunInt` returns `true` unconditionally — the node can never veto quest generation.

**Caveat (unconfirmed):** no shipped Core/DLC XML uses `QuestNode_GenerateThing`
(`grep -rn "GenerateThing" Data/**/*.xml` returns only `QuestNode_GenerateThingSet` hits in
`Core/Defs/QuestScriptDefs/Scripts_Utility_RewardsCore.xml:111`,
`Odyssey/.../Script_OrbitalFugitive.xml:112`, `Odyssey/.../Script_Site.xml:176`).
So the node is code-verified but not XML-precedented. Nothing in its code path requires C#.

### 2.2 `QuestNode_AddItemsReward` accepts an arbitrary `Thing` list and generates the delivery

`RimWorld.QuestGen.QuestNode_AddItemsReward`:

```csharp
public SlateRef<IEnumerable<Thing>> items;
[NoTranslate] public SlateRef<string> inSignalChoiceUsed;
public SlateRef<RewardsGeneratorParams> parms;
public bool generateQuestParts = true;

protected override void RunInt()
{
    Slate slate = QuestGen.slate;
    RewardsGeneratorParams value = parms.GetValue(QuestGen.slate);
    IEnumerable<Thing> value2 = items.GetValue(slate);
    if (value2.EnumerableNullOrEmpty()) return;

    QuestPart_Choice questPart_Choice = new QuestPart_Choice();
    questPart_Choice.inSignalChoiceUsed = QuestGenUtility.HardcodedSignalWithQuestID(inSignalChoiceUsed.GetValue(slate));
    QuestPart_Choice.Choice choice = new QuestPart_Choice.Choice();
    Reward_Items reward_Items = new Reward_Items();
    reward_Items.items.AddRange(value2);          // <-- our exact things, verbatim
    choice.rewards.Add(reward_Items);
    questPart_Choice.choices.Add(choice);
    QuestGen.quest.AddPart(questPart_Choice);
    if (!generateQuestParts) return;
    foreach (QuestPart item in reward_Items.GenerateQuestParts(0, value, null, null, null, null))
        QuestGen.quest.AddPart(item);
}
```

Note it does **not** call `Reward_Items.InitFromValue(...)` — that is the randomizing path
(`ThingSetMakerDefOf.Reward_ItemsStandard.root.Generate(...)`, plus the chance-based
`PsychicAmplifier` insertion). `AddItemsReward` skips it entirely. `parms` is only read for
`giveToCaravan` and letter overrides in `GenerateQuestParts`, and its `ConfigError()` (which would
complain about `rewardValue <= 0`) is never invoked here — so omitting `<parms>` is safe.

### 2.3 `Reward_Items.GenerateQuestParts` — how the items actually arrive

```csharp
if (parms.giveToCaravan) {
    QuestPart_GiveToCaravan q = new QuestPart_GiveToCaravan();
    q.inSignal = slate.Get<string>("inSignal");
    q.Things = items;
    yield return q;
} else {
    QuestPart_DropPods dropPods = new QuestPart_DropPods();
    dropPods.inSignal = slate.Get<string>("inSignal");
    ...
    dropPods.mapParent = slate.Get<Map>("map").Parent;
    dropPods.useTradeDropSpot = true;
    dropPods.Things = items;
    yield return dropPods;
}
slate.Set("itemsReward_items", items);
slate.Set("itemsReward_totalMarketValue", TotalMarketValue);
```

It reads `slate["inSignal"]`. That is why the node **must** be nested inside a signal node — see 2.4.

### 2.4 Why nesting inside `QuestNode_AllSignals` / `QuestNode_Signal` is required

`QuestGenUtility.RunInnerNode` (Assembly-CSharp, `QuestGenUtility`):

```csharp
public static void RunInnerNode(QuestNode node, string innerNodeInSignal)
{
    Slate.VarRestoreInfo restoreInfo = QuestGen.slate.GetRestoreInfo("inSignal");
    QuestGen.slate.Set("inSignal", innerNodeInSignal);
    try { node.Run(); }
    finally { QuestGen.slate.Restore(restoreInfo); }
}
```

`QuestNode_AllSignals.RunInt()` and `QuestNode_Signal.RunInt()` both build a
`QuestPart_PassAll` / `QuestPart_Pass`, generate `OuterNodeCompleted` as its `outSignal`, and call
`QuestGenUtility.RunInnerNode(node, outSignal)`. So inside the `<node>` the slate's `inSignal` is
the success signal, and `Reward_Items`' `QuestPart_DropPods` correctly fires on success rather than
on quest accept.

If you put `QuestNode_AddItemsReward` at the top level of the root sequence with
`generateQuestParts` true, `slate["inSignal"]` is the quest's **initiate** signal and the pods will
drop the moment the player accepts. That is the trap.

### 2.5 Real shipped example — Odyssey

`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Odyssey\Defs\QuestScriptDefs\Script_Site.xml:176-203`:

```xml
        <li Class="QuestNode_GenerateThingSet">
          <thingSetMaker>Reward_GravshipUpgrade</thingSetMaker>
          <storeAs>upgradeItem</storeAs>
        </li>

        <!-- Send rewards and end after survey has been completed -->
        <li Class="QuestNode_AllSignals">
          <inSignals>
            <li>site.SurveyCompleted</li>
          </inSignals>
          <node Class="QuestNode_Delay">
            <delayTicks>300</delayTicks>
            <node Class="QuestNode_Sequence">
              <nodes>
                <li Class="QuestNode_Letter">
                  <label TKey="LetterLabelSurveySiteQuestCompleted">Quest completed</label>
                  <letterDef>PositiveEvent</letterDef>
                  <text TKey="LetterTextSurveySiteQuestCompleted">You have successfully completed the quest '[resolvedQuestName]'!</text>
                </li>
                <li Class="QuestNode_AddItemsReward">
                  <items>$upgradeItem</items>
                </li>
                <li Class="QuestNode_End">
                  <outcome>Success</outcome>
                </li>
              </nodes>
            </node>
          </node>
        </li>
```

Same shape at `Data\Odyssey\Defs\QuestScriptDefs\Script_OrbitalFugitive.xml:112-124`
(`fugitive.Destroyed` → `QuestNode_AddItemsReward`).

### 2.6 Real shipped example of a *guaranteed named item list* in pure XML — Royalty

`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Royalty\Defs\QuestScriptDefs\Intro\Script_Intro_Deserter.xml:90-96`:

```xml
        <!-- Site item stash contents -->
        <li Class="QuestNode_SetItemStashContents">
          <items>
            <li>PsychicAmplifier</li>
            <li>PsychicAmplifier</li>
          </items>
        </li>
```

`QuestNode_SetItemStashContents.items` is `SlateRef<IEnumerable<ThingDef>>` and its `categories`
branch (the randomizing one) is simply left unset. Proof that vanilla itself ships a
deterministic, hand-listed, named-item quest payout with no C#. (Delivery here is via an item
stash on a site map, not drop pods.)

---

## 3. Why inline XML lists work inside `SlateRef<T>` fields

This is the mechanism that makes list-valued quest node fields authorable in XML.

`Verse.DirectXmlToObject.InnerTextWithReplacedNewlinesOrXML`:

```csharp
public static string InnerTextWithReplacedNewlinesOrXML(XmlNode xmlNode)
{
    if (xmlNode.ChildNodes.Count == 1 && xmlNode.FirstChild.NodeType == XmlNodeType.Text)
        return xmlNode.InnerText.Replace("\\n", "\n");
    return xmlNode.InnerXml;
}
```

`DirectXmlToObjectNew.EmitIlToCreateSlateRef` calls exactly that, so a `SlateRef` field with
element children stores the raw **InnerXml** string. At quest-gen time
`SlateRef<T>.TryGetConvertedValue` hands that string to `ConvertHelper.Convert`, which does:

```csharp
if (IsXml(obj) && !to.IsPrimitive) {
    ...
    xmlDocument.LoadXml("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<root>\n" + text + "\n</root>");
    object result = DirectXmlToObject.GetObjectFromXmlMethod(type)(xmlDocument.DocumentElement, arg2: true);
    DirectXmlCrossRefLoader.ResolveAllWantedCrossReferences(FailMode.LogErrors);
    return result;
}
```

and, for a bare string against a Def type:

```csharp
if (text != null && GenTypes.IsDef(to)) { ... return GenDefDatabase.GetDef(to, text); }
```

So `<def>ArchiteCapsule</def>` on `SlateRef<ThingDef>` resolves, and nested `<li>` lists resolve
into `List<T>`. Shipped confirmation of inline-XML-into-SlateRef:
`Data/Core/Defs/QuestScriptDefs/Script_TradeRequest.xml:117-127`, where
`QuestNode_GiveRewards.parms` (`SlateRef<RewardsGeneratorParams>`) is authored as a nested XML
block containing a `<disallowedThingDefs>` `<li>` list.

---

## 4. Alternative patterns (verified, ranked)

### 4.1 `QuestNode_DropPods` with `contentsDefs` — leanest, but no reward UI entry

`RimWorld.QuestGen.QuestNode_DropPods` exposes:

```csharp
public SlateRef<IEnumerable<Thing>> contents;
public SlateRef<IEnumerable<ThingDefCountClass>> contentsDefs;
[NoTranslate] public SlateRef<string> inSignal;
```

and `QuestPart_DropPods.Notify_QuestSignalReceived` materializes them:

```csharp
for (int i = 0; i < thingDefs.Count; i++) {
    Thing thing = ThingMaker.MakeThing(thingDefs[i].thingDef, GenStuff.RandomStuffByCommonalityFor(thingDefs[i].thingDef));
    thing.stackCount = thingDefs[i].count;
    tmpThingsToDrop.Add(thing);
}
```

XML:

```xml
<li Class="QuestNode_DropPods">
  <inSignal>site.SurveyCompleted</inSignal>
  <contentsDefs>
    <li><thingDef>ArchiteCapsule</thingDef><count>2</count></li>
    <li><thingDef>VQEA_ArchogenInjector</thingDef><count>1</count></li>
  </contentsDefs>
  <useTradeDropSpot>true</useTradeDropSpot>
</li>
```

Trade-offs:
- Deterministic in count and def, but `GenStuff.RandomStuffByCommonalityFor` randomizes **stuff**
  for stuffable defs (irrelevant for non-stuffable ones).
- No `Reward_Items` object, so the reward does **not** show in the quest's reward stack in the UI.
- `QuestNode_DropPods.TestRunInt` requires `slate.Exists("map")`.
- **Unconfirmed:** `contentsDefs` has zero usages in any shipped Core/DLC XML
  (`grep -rn "contentsDefs" Data --include=*.xml` → no hits). Code path is verified; XML
  precedent is not.

### 4.2 `ThingSetMakerDef` with `ThingSetMaker_StackCount`, single `thingDef`, degenerate `countRange`

Deterministic **only** in the degenerate configuration. From
`RimWorld.ThingSetMaker_StackCount.Generate`:

```csharp
int num2 = Mathf.Max(intRange.RandomInRange, 1);
...
num4 -= (thing.stackCount = Mathf.Clamp(num5, 1, thing.def.stackLimit));
```

With `<countRange>2~2</countRange>` and a filter allowing exactly one `thingDef`, output is exactly
one stack of 2. Shipped shape (`Data/Core/Defs/ThingSetMakerDefs/ThingSetMakers_MapGen.xml:185-194`):

```xml
          <thingSetMaker Class="ThingSetMaker_StackCount">
            <fixedParams>
              <filter>
                <thingDefs>
                  <li>Luciferium</li>
                </thingDefs>
              </filter>
              <countRange>5~20</countRange>
            </fixedParams>
          </thingSetMaker>
```

Then `QuestNode_GenerateThingSet` → `storeAs` → `QuestNode_AddItemsReward`.

**Why I do not recommend it:** `ThingSetMakerUtility.GetAllowedThingDefs` applies extra gates that
can silently empty the set — `x.PlayerAcquirable`, `CanGenerate(x)` (`category == Item &&
EverHaulable && !destroyOnDrop && graphicData != null`), techprint/royal-title checks when
`makingFaction` is set, and `maxThingMarketValue`. A modded item that fails any of these produces
an empty (silently missing) reward. `QuestNode_GenerateThing` has none of these gates.

### 4.3 There is **no** `ThingSetMaker_Fixed`

Full enumeration of `ThingSetMaker_*` in Assembly-CSharp (1.6):

`ThingSetMaker` (abstract), `_Conditional`, `_Conditional_FactionRelation`,
`_Conditional_MakingFaction`, `_Conditional_MinMaxTotalMarketValue`,
`_Conditional_ResearchFinished`, `_RandomOption`, `_SubTree`, `_Sum`, `_Count`, `_MarketValue`,
`_Nutrition`, `_Pawn`, `_StackCount`, `_MapGen_AncientPodContents`, `_Books`, `_Meteorite`,
`_RandomGeneralGoods`, `_RefugeePod`, `_ResourcePod`, `_Techprints`, `_TraderStock`.

Deterministic-capable: only `_Count` and `_StackCount` when constrained to one `thingDef` and a
degenerate `countRange` (`_Sum`/`_SubTree` inherit determinism from their children). Everything
else randomizes.

### 4.4 `QuestNode_GiveRewards` cannot be made fixed

`QuestNode_GiveRewards` delegates to `Quest.GiveRewards(RewardsGeneratorParams, ...)`, which runs
the full `RewardsGenerator` and calls `Reward_Items.InitFromValue` → `Reward_ItemsStandard`
`ThingSetMakerDef`. `RewardsGeneratorParams` exposes only `rewardValue`, `disallowedThingDefs`,
and allow-flags — no whitelist, no fixed list. Not usable for a fixed reward.

---

## 5. Vanilla Expanded Framework — nothing relevant

`.../294100/2023507013/1.6/Assemblies/VEF.dll` contains only:

- `VEF.Sounds.QuestNode_ForceMusic`
- `VEF.Storyteller.QuestNode_GetFaction`
- `VEF.Storyteller.QuestNode_Site`
- three Harmony patch classes (`VanillaExpandedFramework_QuestNode_GetFaction_IsGoodFaction_Patch`,
  `..._QuestNode_GetPawn_IsGoodPawn_Patch`, `..._QuestNode_Root_DistressCall`)
- `VEF.AnimalBehaviours.VanillaExpandedFramework_QuestNode_GetPawnKind_SetVars_CanHandle_Patch`

No reward-related quest nodes. VEF adds nothing here; vanilla already suffices.

---

## 6. Gotchas checklist

1. **Nest the reward node inside a signal node.** Otherwise `slate["inSignal"]` is the quest
   initiate signal and pods drop on accept. (2.4)
2. **`QuestNode_AddItemsReward` needs `slate["map"]`** — `Reward_Items.GenerateQuestParts` does
   `slate.Get<Map>("map").Parent`. Standard quest roots set this; a `QuestNode_GetMap` earlier in
   the sequence guarantees it.
3. **Don't exceed `def.stackLimit`** in a single `QuestNode_GenerateThing` — `stackCount` is
   assigned unclamped. Emit multiple nodes instead.
4. **Non-stuffable defs only** for `QuestNode_GenerateThing` (no `stuff` is passed).
5. **`addToList` vs `storeAs`**: `addToList` builds a `List<Thing>` across multiple nodes
   (`QuestGenUtility.AddToOrMakeList`); `storeAs` sets a single `Thing`. `AddItemsReward.items` is
   `SlateRef<IEnumerable<Thing>>` — `ConvertHelper` will wrap a single `Thing` into a list, so
   either works, but `addToList` is correct for multi-item rewards.
6. **`QuestPart_DropPods.Cleanup` destroys undelivered items** (`destroyItemsOnCleanup = true` by
   default). Expected behaviour on quest failure.
7. `QuestNode_GenerateThing` also has a `contents` field that stuffs things into a container's
   inner `ThingOwner` — useful if you want the reward inside a crate.

---

## 7. Evidence file paths

| What | Path |
|---|---|
| Assembly decompiled | `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll` |
| Odyssey reward-on-success pattern | `...\RimWorld\Data\Odyssey\Defs\QuestScriptDefs\Script_Site.xml:176-203` |
| Odyssey reward-on-success pattern 2 | `...\RimWorld\Data\Odyssey\Defs\QuestScriptDefs\Script_OrbitalFugitive.xml:112-124` |
| Vanilla fixed named-item list | `...\RimWorld\Data\Royalty\Defs\QuestScriptDefs\Intro\Script_Intro_Deserter.xml:90-96` |
| Inline XML into SlateRef precedent | `...\RimWorld\Data\Core\Defs\QuestScriptDefs\Script_TradeRequest.xml:117-127` |
| Single-def StackCount precedent | `...\RimWorld\Data\Core\Defs\ThingSetMakerDefs\ThingSetMakers_MapGen.xml:185-194` |
| Randomized reward util (contrast) | `...\RimWorld\Data\Core\Defs\QuestScriptDefs\Scripts_Utility_RewardsCore.xml:95-140` |
| ArchiteCapsule def (`stackLimit` 25) | `...\RimWorld\Data\Biotech\Defs\ThingDefs_Items\Items_Various.xml:84,105` |
| VEF assembly (no relevant nodes) | `...\workshop\content\294100\2023507013\1.6\Assemblies\VEF.dll` |
