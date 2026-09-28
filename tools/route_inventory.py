"""
The route inventory: docs/CAPABILITIES.md, normalised into one JSON file.

Every card, every capability row and every route on the capabilities document,
with a stable ID for each, written to docs/data/route-inventory.json for the
working surface to load (#200, the data contract settled on #199). Nothing is
researched and nothing is judged: every value is lifted from the card, and each
normalised route value says where it came from.

Run:
  python tools/route_inventory.py                    # regenerate the inventory
  python tools/route_inventory.py --check            # exit 1 if the file is stale
  python tools/route_inventory.py --accept-renumber  # retire vanished IDs

Parsing
-------
A card is an H3 heading under one of the five system groups (H2); the four
Religion sub-cards are H4, carrying `parent_card: "RELIGION"`. A capability is
one row of a card's table. A route is one piece of the row's Routes cell: the
cell is split on `<br>`, then on a bold label that follows ` · `, `, ` or `. `
(`**A**`, `**OC-C1**`, `**A (as specced)**`). A line ending in `:` with no label
("Cost:", "Map loaded:") heads a group; `Ceremony **A**` and `Shapes: **A**`
carry the group inline. A route's first ` · ` chunk is its summary; the chunks
after it are read for kind, weight, carrier and a route-level Multiplayer line.

Where a cell does not parse mechanically, a fix-up below says so, keyed by
capability or route ID, with the line it answers. Fix-ups rewrite the cell text
before parsing (CELL_FIXUPS), mark an unlabelled line as a note rather than a
route (NOTE_LINES), or set one route field (ROUTE_OVERRIDES). Each one fails
loudly if the text it expects is gone, so a fix-up never outlives its cause.
The JSON is never hand-edited.

Provenance
----------
Each route carries `provenance` for summary, carrier, kind, weight,
multiplayer and source:

  explicit   the route's own text states it ("(mapped)" weights included: the
             card states them)
  inherited  taken from the row (its MP cell, its Spec cell), from a group
             heading, or from a label list sharing one tail ("**SV-1** visit,
             **SV-3** ... · Medium")
  unstated   neither states it; the value is null. "weight not stated" is null

IDs, and how they stay stable
-----------------------------
Card IDs come from CARD_IDS below: a new card fails the run until it is given
one. A capability is `<CARD>-<nn>`. A route keeps the card's own ID where the
card gives a hyphenated one (`OC-C1`, `AE-5a`), prefixed `<CARD>.` only when
that label occurs more than once in the document; otherwise it is
`<capability>.<label>` (`ALTAR-02.A`), and an unlabelled route is
`<capability>.U<n>`. Every ID is unique across the document; the run asserts it.

The working surface stores these IDs, so regeneration must never renumber. On a
fresh build, capabilities are numbered in document order. After that the
existing inventory is the registry: an ID is carried forward whenever its
identity is unchanged (a capability's identity is its card plus its text; a
route's is its capability's identity plus its label, or its text when it has no
label), and anything new is minted after the highest number the card has ever
used (retired IDs included). Inserting, moving or deleting-then-restoring rows
therefore never moves an existing ID.

A capability or route whose identity vanished (removed, or reworded) would
orphan any surface state that points at it, so the run stops and names each
one. `--accept-renumber` accepts that: the vanished IDs are recorded under
`retired` and never reused, and a reworded row comes back under a new ID.
Migrate surface state that references a retired ID by hand.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_REL = "docs/CAPABILITIES.md"
DOC = os.path.join(REPO, *DOC_REL.split("/"))
OUT = os.path.join(REPO, "docs", "data", "route-inventory.json")
SLICE_OUT = os.path.join(REPO, "docs", "data", "route-inventory.slice.json")
SCHEMA = "archinity.route-inventory/1"

GROUPS = ("Faith", "Politics", "Glittertech", "World and space", "Colony")

# Heading text -> card ID. A card missing here stops the run: its ID is part of
# every capability ID under it, so it is chosen once, by hand.
CARD_IDS = {
    "The altar": "ALTAR",
    "Religion": "RELIGION",
    "Religion · Reverence and institutions": "REVERENCE",
    "Religion · The Church": "CHURCH",
    "Religion · The player faith and the founders": "FOUNDERS",
    "Religion · The Schism, revolt and changing faiths": "SCHISM",
    "The psychic track": "PSYCHIC",
    "Transcendence": "TRANSCENDENCE",
    "Faction politics": "POLITICS",
    "Territory": "TERRITORY",
    "Pressure": "PRESSURE",
    "Encounters": "ENCOUNTERS",
    "Trace and the Glitterite pursuit": "TRACE",
    "Spendable currencies: Influence and Intel": "CURRENCIES",
    "Hacking": "HACKING",
    "Androids": "ANDROIDS",
    "Research": "RESEARCH",
    "Era": "ERA",
    "Charting": "CHARTING",
    "World infrastructure": "INFRA",
    "Orbit": "ORBIT",
    "Gravship": "GRAVSHIP",
    "Colony management": "COLONY",
    "Shipped defaults and presets": "DEFAULTS",
    "Items and gear": "ITEMS",
    "Specialisation": "SPECIALISATION",
    "Quests": "QUESTS",
}

# --------------------------------------------------------------------------
# Fix-ups. Each is keyed by capability or route ID and cites the line it
# answers (line numbers as of the commit that added it). Every (old, new) pair
# must match exactly once, or the run fails.
# --------------------------------------------------------------------------

CELL_FIXUPS = {
    # L212: A2, A3, B3, B4, C3 and R1 are route labels printed without bold,
    # and "C4 and K6 are *not recommended*" names two more routes in a sentence.
    "FOUNDERS-03": [
        (" · A2 pawn kind", " · **A2** pawn kind"),
        (" · A3 genes", " · **A3** genes"),
        (" · B3 quest shuttle", " · **B3** quest shuttle"),
        (" · B4 present", " · **B4** present"),
        (" · C3 no sale", " · **C3** no sale"),
        (" · R1 no release", " · **R1** no release"),
        (". C4 and K6 are *not recommended* (silent no-ops)",
         "<br>**C4** *not recommended* (silent no-ops)"
         "<br>**K6** *not recommended* (silent no-ops)"),
    ],
    # L404: "**R0 / R3** ... R3 *not recommended*" is one label pair; kept as
    # one route (see ROUTE_OVERRIDES).
    # L408: the price and the four gates follow the routes as plain text.
    "TERRITORY-10": [
        ("<br>Price: a P4 debt at the target tier. Gates: TG-1 colony era, "
         "TG-2 parent climbed, TG-3 research, TG-4 price only",
         "<br>Price: a P4 debt at the target tier"
         "<br>**TG-1** colony era<br>**TG-2** parent climbed"
         "<br>**TG-3** research<br>**TG-4** price only"),
    ],
    # L410: "· Medium, plus **CF-C** rebind" joins three routes to CF-B with
    # "plus", which is not a separator the splitter reads.
    "TERRITORY-12": [
        ("· Medium, plus **CF-C** rebind", "· Medium<br>**CF-C** rebind"),
    ],
    # L452: "Size: ... . Frequency: ..." is two routes on one line.
    "PRESSURE-04": [
        ("term. Frequency:", "term<br>Frequency:"),
    ],
    # L1088: two unlabelled routes on one line, "XML: ... · or C#: ...".
    "SPECIALISATION-04": [
        (" · or C#: a reader", "<br>C#: a reader"),
    ],
    # L891: "**S1** quest site (spec recommends) · **S2** ..." — the weight
    # "both Medium" covers S1 and S2; handled in ROUTE_OVERRIDES.
    # L739: "Which clock it runs on:" heads routes A and B but ends the store's
    # line; it is moved onto its own line so it reads as a group heading.
    "ERA-03": [
        (". Which clock it runs on:<br>", "<br>Which clock it runs on:<br>"),
    ],
    # L538: route A is the list D1-D6 on its own lines, then its tail
    # "· ours · C# · Medium (mapped)" on a line of its own. D1-D6 are parts of
    # the one build, not alternatives; rejoined into one route.
    "TRACE-09": [
        ("**A (as specced)**<br>D1", "**A (as specced)** D1"),
        ("<br>D2", "; D2"), ("<br>D3", "; D3"), ("<br>D4", "; D4"),
        ("<br>D5", "; D5"), ("<br>D6", "; D6"),
        ("<br>· ours", " · ours"),
    ],
    # L411: "The routes compose" closes the RimPacts line; moved to a note.
    # "**OS-6**/**OS-7** on the faction's own schedule, or a fixed one" is two
    # routes under one label pair; split, sharing the one weight.
    "TERRITORY-13": [
        (". The routes compose", "<br>The routes compose"),
        ("**OS-6**/**OS-7** on the faction's own schedule, or a fixed one",
         "**OS-6** on the faction's own schedule, **OS-7** a fixed one"),
    ],
    # L305: C′ is a route named inside C's text ("...nowhere else; C′ draws a
    # second line..."); given its own label, sharing C's tail "· C# · Medium".
    "TRANSCENDENCE-03": [
        ("; C′ draws a second line", ", **C′** draws a second line"),
    ],
}

# Unlabelled lines in a Routes cell that are commentary on the routes, not a
# route. Keyed by capability ID; each entry is the line's opening text. Lines
# opening "Spec recommends" / "The spec recommends" are notes without listing.
NOTE_LINES = {
    "ERA-03": ["A and B compose"],                                 # L739
    "INFRA-02": ["The off-road half"],                             # L836
    "INFRA-09": ["The apparatus still clamps"],                    # L843
    "DEFAULTS-02": ["B carries no weapon"],                        # L1010
    "DEFAULTS-03": ["Spec would cost"],                            # L1011
    "DEFAULTS-04": ["The weapon alone drops"],                     # L1012
    "SPECIALISATION-07": ["The spec does not address"],            # L1091
    "TERRITORY-02": ["OC-N1 and OC-N2 were retired"],              # L400
    "TERRITORY-03": ["The kind rule is a filter"],                 # L401
    "TERRITORY-10": ["Price: a P4 debt"],                          # L408
    "TERRITORY-11": ["The attacker-takes outcome"],                # L409
    "TERRITORY-01": ["VFE Medieval 2's raid-on-fail is not a route"],  # L399
    "POLITICS-07": ["A `RoyalTitlePermitDef` worker is not selected"],  # L349
    "CHURCH-07": ["Vanilla `QuestNode_EndGame` is *not a route*"],  # L181
    "PRESSURE-03": ["A strategy with a high `minPawns`"],          # L451
    "PRESSURE-08": ["Kidnap and steal need code"],                 # L456
    "RESEARCH-03": ["A gate on `FinishProject` is no gate"],       # L696
    "QUESTS-05": ["VEF's contract window draws one pip"],          # L1131
    "TERRITORY-13": ["The routes compose"],                        # L411
}

# One field of one route, set by hand where the card's wording is not
# mechanical. Keys are route IDs; values are {field: (value, provenance)}.
ROUTE_OVERRIDES = {
    # L891: "**S1** quest site (spec recommends) · **S2** standing settlement,
    # which still needs S1 as fallback · both Medium" — "both" is S1 and S2.
    "ORBIT-08.S1": {"weight": ("medium", "inherited"),
                    "weight_text": ("both Medium", "inherited")},
    # L404: "R3 *not recommended*" marks only the R3 half of "R0 / R3".
    "TERRITORY-06.R0+R3": {"not_recommended": (False, None)},
    # L838: C5's Multiplayer is stated by reference, "as C2 + C3".
    "INFRA-04.C5": {"multiplayer": ("as C2 + C3", "explicit")},
    # L1128: N3 is "an icon only, not a route" — the card lists it but says
    # it is no way to deliver the capability.
    "QUESTS-02.N3": {"marks": (["an icon only, not a route"], None)},
    # L411, L352: RimPacts routes the card prints without a label. The label
    # is minted from the card's own first words; the ID stays as minted (U1).
    "TERRITORY-13.U1": {"label": ("RimPacts", None)},
    "POLITICS-10.U1": {"label": ("RimPacts", None)},
}

# Row MP cells that name routes in a shape the clause reader cannot map.
# Keyed by capability ID: {route label: clause text}; "*" is every other route.
# L399, L410, L494, L575, L886, L933 and L1086.
MP_OVERRIDES = {
    "TERRITORY-01": {
        "Build B (as specced)": "Build B: Yes (spec), condition: created from the world tick or a synced incident, the roll seeded (§0 P4), attendance a float-menu option (§0 P5) [I]",
        "*": "AS: Yes [I]: quest accept is synced, attendance is vanilla's visit-site option, the roll is P4",
    },
    "TERRITORY-12": {
        "MO-W2/W3/F2/F3": "Yes, except MO-F2 (With work)",
        "GV-6": "GV-6 (No)",
        "*": "Yes",
    },
    "ENCOUNTERS-04": {"V3": "V3 With work", "*": "Yes"},
    "CURRENCIES-04": {
        "Analysis": "Yes (analysis)",
        "Lore": "Yes (spec), condition: our lore object drops VEF's designate gizmo (T-61) (lore)",
    },
    "GRAVSHIP-04": {"Build (d)": "build (d) Unknown", "*": "Yes (spec)"},
    "SPECIALISATION-02": {"A–D": "A–D With work", "E": "E Yes", "F": "F Yes [I]"},
    # L886: the traders' clause says "trader", not the label "Traders".
    "ORBIT-03": {
        "Traders": "Yes (spec): the trader postfix is PRESSURE § The build › 4, under PRESSURE's conditional Yes; the scenario part is def-only XML (DEFAULTS § The build)",
        "Salvagers": "Yes (spec): the Salvagers prefix is PRESSURE route G (Yes)",
    },
}

# Composition the card states across rows: {route ID: [route IDs]}.
COMPOSES_OVERRIDES = {
    # L975: "composes with A" is route A of the row above (L974).
    "COLONY-03.D": ["COLONY-02.A"],
}

# --------------------------------------------------------------------------

NONLABEL_BOLD = {"No", "not", "two", "other than the Church", "does not"}
MARK_RE = re.compile(r"not recommended|partial|fallback|not selected|not a route"
                     r"|requirement|not for |recommended only|backstop",
                     re.I)
WEIGHT_WORD = re.compile(r"\b(Easy|Medium|Hard)\b")
KIND_CHUNK = re.compile(
    r"^(?:mostly\s+|our\s+)?(?:XML|C#|Harmony|patch|settings|dependency|~?\d+ lines)(?!\w)")
MP_CHUNK = re.compile(r"^(?:MP\b|Yes\b|With work\b|Unknown\b|No\b)")
CARRIER_RE = re.compile(
    r"\b(?:vanilla|ours|our|VEF|VFE|VFED|VRE|VGE|VVE|VOE|VIE|Odyssey|Ushanka|WTL"
    r"|World Tech Level|Vehicle Framework|Better|Compositable|Nice Bill Tab|NBT"
    r"|Worksites|KCSG|Deserters|RimPacts|Medieval Overhaul|More Realistic"
    r"|MP Compat|FT&V|mod|ritual outcome worker|capstone prerequisites"
    r"|Faction Territories)\b|`[\w.]+\.dll`")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
LABEL_AT = re.compile(r"^\*\*([^*]+)\*\*")
SPEC_REC = re.compile(r"(?:(?<=\.)|(?<=;))\s+((?:The spec|Spec) recommends\b.*)$")


class Fail(Exception):
    pass


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def gh_slug(title):
    """GitHub's heading anchor."""
    s = title.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def doc_link(target):
    """A link as written in CAPABILITIES.md -> a repo-relative path."""
    if target.startswith(("http://", "https://", "#")):
        return target if not target.startswith("#") else DOC_REL + target
    return "docs/" + target


def label_slug(label):
    s = label.replace("′", "prime").replace("C#", "Csharp")
    s = re.sub(r"\s*[–]\s*", "..", s)
    s = re.sub(r"\s*[/+]\s*", "+", s)
    s = s.replace("(", "").replace(")", "").replace(":", "")
    s = re.sub(r"\s+", "-", s.strip())
    return s


def base_label(label):
    """'A (as specced)' -> 'A'; '(as specced)' -> None; '(a)' -> '(a)'."""
    if label is None:
        return None
    lab = label.strip().rstrip(":").strip()
    if lab in ("(as specced)",):
        return None
    m = re.match(r"^(.+?)\s+\((as specced|already built|required|selected)\)$", lab)
    return m.group(1) if m else lab


# --------------------------------------------------------------------------
# Document parsing
# --------------------------------------------------------------------------

def parse_doc(text):
    lines = text.split("\n")
    cards, rows = [], []
    group = None
    card = None
    parent = None
    mode = None
    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        if line.startswith("## "):
            title = line[3:].strip()
            group = title if title in GROUPS else None
            card, mode = None, None
            continue
        if group is None:
            continue
        m = re.match(r"^(###|####) (.+)$", line)
        if m:
            level, title = m.group(1), m.group(2).strip()
            if title not in CARD_IDS:
                raise Fail(f"L{i}: card '{title}' has no ID in CARD_IDS; add one")
            cid = CARD_IDS[title]
            if level == "###":
                parent = cid
                pcard = None
            else:
                pcard = parent
            card = {"id": cid, "title": title, "group": group,
                    "parent_card": pcard, "anchor": DOC_REL + "#" + gh_slug(title),
                    "line": i, "possible": None, "multiplayer": None,
                    "story_can": [], "story_cannot": [], "spec": []}
            cards.append(card)
            mode = None
            continue
        if card is None:
            continue
        if line.startswith("**Possible?**"):
            card["possible"] = line[len("**Possible?**"):].strip()
            mode = "possible"
            continue
        if line.startswith("**Multiplayer?**"):
            card["multiplayer"] = line[len("**Multiplayer?**"):].strip()
            mode = "multiplayer"
            continue
        if line.startswith("**What the story can do with it**"):
            mode = "story_can"
            continue
        if line.startswith("**What it cannot do**"):
            mode = "story_cannot"
            continue
        if line.startswith("**Spec and tickets:**"):
            for t in LINK_RE.findall(line):
                p = doc_link(t)
                if p.startswith("docs/specs/") and p not in card["spec"]:
                    card["spec"].append(p)
            mode = None
            continue
        if line.startswith("| "):
            mode = None
            cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
            if cells[0] == "Capability" or set(cells[0]) <= set("-|"):
                continue
            if cells[0].startswith("---"):
                continue
            if len(cells) != 5:
                raise Fail(f"L{i}: table row has {len(cells)} cells, expected 5")
            rows.append({"card": card["id"], "line": i, "cells": cells})
            continue
        if line.startswith("|"):
            continue
        if mode in ("possible", "multiplayer"):
            if line.startswith("- "):
                card[mode] += "\n" + line
            else:
                mode = None
            continue
        if mode in ("story_can", "story_cannot"):
            if line.startswith("- "):
                card[mode].append(line[2:].strip())
            elif line.startswith("  ") and line.strip() and card[mode]:
                card[mode][-1] += "\n" + line.strip()
            continue
    return cards, rows


# --------------------------------------------------------------------------
# Route parsing
# --------------------------------------------------------------------------

def apply_fixups(cap_id, cell, used):
    for old, new in CELL_FIXUPS.get(cap_id, []):
        n = cell.count(old)
        if n != 1:
            raise Fail(f"CELL_FIXUPS[{cap_id}]: expected 1 match of {old!r}, found {n}")
        cell = cell.replace(old, new)
        used.add(("cell", cap_id, old))
    return cell


def split_pieces(seg):
    """One <br> line -> [(piece, joined_by_comma)] at bold-label boundaries."""
    seg = re.sub(r"\*\*/\*\*", "/", seg)          # **OU-A1**/**OU-A3** -> one label
    out, start = [], 0
    joins = []
    for m in re.finditer(r"( · |, |; |\. )(?=\*\*([^*]+)\*\*)", seg):
        if m.group(2).strip() in NONLABEL_BOLD:
            continue
        out.append(seg[start:m.start()])
        joins.append(m.group(1) == ", ")
        start = m.end()
    out.append(seg[start:])
    # a piece is comma-joined when the separator AFTER it was ", "
    return [(p.strip(), joins[k] if k < len(joins) else False)
            for k, p in enumerate(out)]


def split_top(s, sep=" · "):
    """Split on sep, but never inside parentheses or backticks."""
    out, depth, tick, start, i = [], 0, False, 0, 0
    while i < len(s):
        ch = s[i]
        if ch == "`":
            tick = not tick
        elif not tick and ch == "(":
            depth += 1
        elif not tick and ch == ")" and depth:
            depth -= 1
        elif not tick and depth == 0 and s.startswith(sep, i):
            out.append(s[start:i])
            i += len(sep)
            start = i
            continue
        i += 1
    out.append(s[start:])
    return out


def parse_attrs(chunks):
    """Tail chunks of one route -> dict of stated values (no provenance)."""
    a = {"kind": None, "kind_text": None, "weight": None, "weight_text": None,
         "weight_mapped": False, "carrier": None, "multiplayer": None,
         "as_shipped": False}
    rest = []
    for ch in chunks:
        c = ch.strip()
        if not c:
            continue
        if a["weight_text"] is None and (WEIGHT_WORD.match(c) or
                                         c.lower().startswith("weight not stated")):
            a["weight_text"] = c
            continue
        if KIND_CHUNK.match(c) or c == "none":
            kinds = []
            if c != "none" and not re.search(r"XML|C#|Harmony|patch|class|postfix"
                                             r"|prefix|lines|settings", c):
                rest.append(c)          # "dependency" alone names no kind
                continue
            if re.search(r"\bXML patch\b|\bpatch(es)?\b", c):
                kinds.append("patch")
            if re.search(r"\bXML\b(?! patch)", c):
                kinds.append("xml")
            if re.search(r"C#|Harmony|\bclass\b|postfix|prefix|\blines\b", c):
                kinds.append("cs")
            order = ["xml", "patch", "cs"]     # "settings" stays in kind_text
            a["kind"] = sorted(set((a["kind"] or []) + kinds), key=order.index)
            a["kind_text"] = c if a["kind_text"] is None else a["kind_text"] + " · " + c
            if c.startswith("our ") and a["carrier"] is None:
                a["carrier"] = c
            if a["weight_text"] is None and WEIGHT_WORD.search(c):
                a["weight_text"] = c
            continue
        if MP_CHUNK.match(c) and a["multiplayer"] is None:
            c = c.replace("**", "")
            a["multiplayer"] = c[3:].strip() if c.startswith("MP ") else c
            continue
        if c.startswith("as shipped"):
            a["as_shipped"] = True
            continue
        rest.append(c)
    for c in rest:
        if (a["carrier"] is None and CARRIER_RE.search(c) and not c.startswith("*")
                and "fallback" not in c):
            a["carrier"] = c
            break
    if a["multiplayer"] is None:
        for c in rest:
            m = re.search(r"\bMP (?:\*\*)?(?:No|Yes|Unknown|[Ww]ith work)\b.*", c)
            if m:
                a["multiplayer"] = m.group(0)[3:].replace("**", "").strip()
                break
    if a["weight_text"] is None:
        for c in rest:
            if WEIGHT_WORD.search(c) and not c.startswith("*"):
                a["weight_text"] = c
                break
    if a["weight_text"]:
        # "Medium *(mapped)*. XML alone gives ..." -> "Medium *(mapped)*"
        a["weight_text"] = re.split(r"(?<=[)*a-z])\.\s", a["weight_text"])[0]
    wt = a["weight_text"]
    if wt and not wt.lower().startswith("weight not stated"):
        levels = [w.lower() for w in WEIGHT_WORD.findall(wt)]
        distinct = list(dict.fromkeys(levels))
        if len(distinct) == 1:
            a["weight"] = distinct[0]
        elif len(distinct) == 2 and re.search(
                r"(Easy|Medium|Hard)\s*[–→]\s*(Easy|Medium|Hard)", wt):
            a["weight"] = distinct[0] + "-" + distinct[1]
        elif distinct:
            a["weight"] = "varies"
        a["weight_mapped"] = "(mapped" in wt
    elif wt:
        a["weight_text"] = wt
    return a


def summarise(text):
    s = text.strip().lstrip(".:;,· ").strip()
    s = SPEC_REC.sub("", s).strip()
    s = re.sub(r"^\*[^*]+\*:?\s*", "", s)     # a leading *not recommended* is a mark
    if len(s) > 160:
        m = re.search(r"(?<=[a-z0-9)`\]])\. (?=[A-Z])", s)
        if m and m.start() >= 20:
            s = s[:m.start() + 1]
    s = s.rstrip(" ·")
    return s or None


def parse_routes(cap_id, cell, notes_out, used):
    """A Routes cell -> list of raw route dicts (label, group, text, attrs)."""
    cell = apply_fixups(cap_id, cell, used)
    note_prefixes = NOTE_LINES.get(cap_id, [])
    routes = []
    group, group_attrs = None, None
    for seg in cell.split("<br>"):
        seg = seg.strip()
        if not seg:
            continue
        # A trailing "Spec recommends ..." sentence is a note, not route text.
        m = SPEC_REC.search(seg)
        if m and not re.match(r"^(The spec|Spec) recommends", seg):
            notes_out.append(m.group(1).strip())
            seg = seg[:m.start()].rstrip()
        if re.match(r"^(The spec|Spec) recommends\b", seg):
            notes_out.append(seg)
            continue
        hit = [p for p in note_prefixes if seg.startswith(p)]
        if hit:
            notes_out.append(seg)
            used.add(("note", cap_id, hit[0]))
            continue
        # A group heading on its own line: "Cost:", "Four vanilla levers ... :"
        if seg.endswith(":") and not LABEL_AT.match(seg) and "**" not in seg:
            head = seg[:-1].strip()
            parts = split_top(head)
            group = parts[0]
            group_attrs = parse_attrs(parts[1:]) if len(parts) > 1 else None
            if group_attrs and re.search(r"\ball XML\b", group):
                group_attrs["kind"] = ["xml"]       # "Four vanilla levers, all XML"
            continue
        # Inline group before a bold label: "Shapes: **A**", "Ceremony **A**"
        gm = re.match(r"^([A-Z][A-Za-z ,]{0,40}?):?\s+(?=\*\*)", seg)
        inline_group = None
        if gm and len(gm.group(1).split()) <= 5:
            inline_group = gm.group(1).strip()
            seg = seg[gm.end():]
            group, group_attrs = inline_group, None     # holds for later lines
        pieces = split_pieces(seg)
        pending = []
        seg_routes = []
        for piece, comma_joined in pieces:
            lm = LABEL_AT.match(piece)
            label, body = None, piece
            if lm and lm.group(1).strip() not in NONLABEL_BOLD:
                label = lm.group(1).strip().rstrip(":").strip()
                body = piece[lm.end():]
            elif not lm:
                # "Traders: vanilla's ...", "Size: ..." — a named, unbolded route
                pm = re.match(r"^([A-Z][A-Za-z# ]{0,24}?):\s+", piece)
                if pm and len(pm.group(1).split()) <= 2:
                    label = pm.group(1).strip()
                    body = piece[pm.end():]
            chunks = split_top(body)
            summary = summarise(chunks[0])
            if summary is None and label and re.fullmatch(r"[A-Z][a-z]+( [a-z]+)+", label):
                summary = label             # "**Own political tab** · a vanilla ..."
            r = {"label": label, "group": inline_group or group,
                 "text": norm(body.lstrip(".:;, ")),
                 "summary": summary,
                 "attrs": parse_attrs(chunks[1:]),
                 "group_attrs": group_attrs if not inline_group else None,
                 "shared": None, "run_tail": None, "raw": piece}
            pending.append(r)
            seg_routes.append(r)
            if not comma_joined:
                # Comma-joined labels share the last one's tail.
                last = pending[-1]
                for p in pending[:-1]:
                    p["shared"] = last
                routes.extend(pending)
                pending = []
        routes.extend(pending)
        # Two or more labelled routes with no tail of their own, closed by one
        # with a tail, read as a list sharing that tail's weight and kind
        # ("**RD-1** ... · **RD-7** ... · **RD-8** ... · Medium"). A single
        # untailed route before a tailed one is ambiguous and is left alone.
        run = []
        for r in seg_routes:
            a = r["attrs"]
            tailed = a["weight_text"] is not None or a["kind"] is not None
            if r["shared"] is not None or not r["label"]:
                run = []
                continue
            if not tailed:
                run.append(r)
                continue
            if len(run) >= 2:
                for p in run:
                    p["run_tail"] = r
            run = []
    return routes


# --------------------------------------------------------------------------
# Multiplayer, by row
# --------------------------------------------------------------------------

STATUS = r"(Yes|With work|with work|No|Unknown|with care)"


def expand_mentions(clause, labels):
    """Which of this row's route labels does a clause name?"""
    found = set()
    bases = {lab: base_label(lab) for lab in labels if base_label(lab)}
    # ranges written in the clause: J1–J4, A–C
    for m in re.finditer(r"\b([A-Z]{1,3}-?)(\d*)\s*–\s*(?:\1)?([A-Z]?)(\d*)\b", clause):
        pre, n1, l2, n2 = m.group(1), m.group(2), m.group(3), m.group(4)
        for lab, b in bases.items():
            if n1 and n2 and re.fullmatch(re.escape(pre) + r"(\d+)", b):
                if int(n1) <= int(re.fullmatch(re.escape(pre) + r"(\d+)", b).group(1)) <= int(n2):
                    found.add(lab)
            elif not n1 and not n2 and len(pre) == 1 and l2 and len(b) == 1:
                if pre <= b <= l2:
                    found.add(lab)
    for lab, b in bases.items():
        comps = [c.strip() for c in re.split(r"/|\+| – |–(?=[A-Z])", b)] if (
            "/" in b or "+" in b) else [b]
        for c in comps:
            if c.startswith("(") and c.endswith(")"):
                if c in clause:
                    found.add(lab)
                continue
            if re.search(r"(?<![\w#-])" + re.escape(c) + r"(?![\w#′-])", clause):
                found.add(lab)
    return found


def row_mp(cap_id, cell, routes, used):
    """-> {route index: (text, provenance)} from the row's MP cell."""
    labels = [r["label"] for r in routes if r["label"]]
    out = {}
    if cap_id in MP_OVERRIDES:
        used.add(("mp", cap_id, None))
        ov = MP_OVERRIDES[cap_id]
        for k, lab in enumerate(r["label"] for r in routes):
            if lab in ov:
                out[k] = ov[lab]
            elif "*" in ov:
                out[k] = ov["*"]
        missing = [lab for lab in ov if lab != "*" and lab not in labels]
        if missing:
            raise Fail(f"MP_OVERRIDES[{cap_id}]: no route labelled {missing}")
        return out, "inherited"
    if cell.strip() == "Per route":
        return out, "inherited"         # each route states its own, or nothing
    clauses = [c.strip() for c in re.split(r" · |; |\. (?=[A-Z(])", cell) if c.strip()]
    if len(clauses) == 1:
        # One clause naming routes, "Yes (F1, F5: with work under multifaction)",
        # qualifies the verdict; it does not withdraw it from the others.
        return {k: cell for k in range(len(routes))}, "inherited"
    mapped, default = {}, []
    for c in clauses:
        hits = expand_mentions(c, labels)
        if hits:
            for lab in hits:
                mapped.setdefault(lab, []).append(c)
        else:
            default.append(c)
    if not mapped:
        for k in range(len(routes)):
            out[k] = cell
        return out, "inherited"
    dflt = " ".join(default) if default else None
    for k, r in enumerate(routes):
        if r["label"] in mapped:
            out[k] = "; ".join(mapped[r["label"]])
        elif dflt and re.match(STATUS, dflt):
            out[k] = dflt
    return out, "inherited"


# --------------------------------------------------------------------------
# IDs
# --------------------------------------------------------------------------

def cap_key(card_id, text):
    return card_id + "\x1f" + norm(text)


def route_key(ckey, route):
    return ckey + "\x1f" + (("L:" + route["label"] + "\x1f" + (route["group"] or ""))
                            if route["label"] else "T:" + norm(route["text"]))


def assign_ids(cards, caps, existing, accept):
    """Mint or carry forward IDs. Returns (retired list)."""
    old_caps, old_routes, retired = {}, {}, []
    if existing:
        for c in existing.get("capabilities", []):
            old_caps[c["key"]] = c["id"]
        for r in existing.get("routes", []):
            old_routes[r["key"]] = r["id"]
        retired = list(existing.get("retired", []))
    used_ids = set(retired) | {c["id"] for c in caps} | {c["id"] for c in cards}

    # routes: card-own hyphenated labels stay bare unless they recur
    counts = {}
    for c in caps:
        for r in c["routes"]:
            b = base_label(r["label"])
            if b and re.match(r"^[A-Z]{1,3}-", b):
                counts[label_slug(b)] = counts.get(label_slug(b), 0) + 1
    for c in caps:
        taken = set()
        in_row = {}
        for r in c["routes"]:
            b = base_label(r["label"])
            if b:
                in_row[b] = in_row.get(b, 0) + 1
        ucount = max([int(m.group(1)) for x in list(old_routes.values()) + retired
                      for m in [re.match(re.escape(c["id"]) + r"\.U(\d+)$", x)] if m] + [0])
        for r in c["routes"]:
            r["key"] = route_key(c["key"], r)
            if r["key"] in old_routes:
                r["id"] = old_routes[r["key"]]
            else:
                b = base_label(r["label"])
                if b is None:
                    ucount += 1
                    rid = f"{c['id']}.U{ucount}"
                else:
                    s = label_slug(b)
                    if in_row[b] > 1 and r["group"]:
                        s = label_slug(r["group"]) + "-" + s
                    if re.match(r"^[A-Z]{1,3}-", b) and counts.get(label_slug(b), 0) == 1:
                        rid = s
                    elif re.match(r"^[A-Z]{1,3}-", b):
                        rid = f"{c['card']}.{s}"
                    else:
                        rid = f"{c['id']}.{s}"
                    if rid in used_ids or rid in taken:
                        rid = f"{c['id']}.{s}"
                n = 2
                base_rid = rid
                while rid in used_ids or rid in taken:
                    rid = f"{base_rid}-{n}"
                    n += 1
                r["id"] = rid
            taken.add(r["id"])
            used_ids.add(r["id"])

    # stability: every old identity must still be present
    new_cap_keys = {c["key"] for c in caps}
    new_route_keys = {r["key"] for c in caps for r in c["routes"]}
    gone = [(i, k) for k, i in old_caps.items() if k not in new_cap_keys]
    gone += [(i, k) for k, i in old_routes.items() if k not in new_route_keys]
    if gone and not accept:
        lines = "\n".join(f"  {i}: {k.split(chr(31))[1][:90]!r}"
                          + (f" / {k.split(chr(31))[-1][:40]!r}" if "." in i else "")
                          for i, k in sorted(gone))
        raise Fail(
            f"{len(gone)} existing ID(s) would vanish (row removed or reworded):\n"
            f"{lines}\n"
            "Surface state may point at them. Re-run with --accept-renumber to retire "
            "them (reworded rows get new IDs), and migrate the surface by hand.")
    for i, _ in gone:
        if i not in retired:
            retired.append(i)
    return sorted(retired)


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                          text=True, check=True).stdout.strip()


def resolve_composes(c, r):
    labs = []
    t = r["text"]
    for m in re.finditer(r"composes with ((?:[A-Z][\w′-]*)(?:\s*(?:,|and|or|\+)\s*[A-Z][\w′-]*)*)", t):
        labs += re.findall(r"[A-Z][\w′-]*", m.group(1))
    for m in re.finditer(r"\(adds to ([A-Z][\w′-]*(?: or [A-Z][\w′-]*)*)\)", t):
        labs += re.findall(r"[A-Z][\w′-]*", m.group(1))
    for m in re.finditer(r"\b([A-Z][\w′-]*) and ([A-Z][\w′-]*) compose\b", t):
        labs += [m.group(1), m.group(2)]
    by_label = {base_label(x["label"]): x["id"] for x in c["routes"] if x["label"]}
    out = []
    for lab in labs:
        rid = by_label.get(lab)
        if rid is None:
            return None     # unresolved; needs COMPOSES_OVERRIDES
        if rid != r["id"] and rid not in out:
            out.append(rid)
    return out


def build(existing, accept):
    with open(DOC, "rb") as f:
        raw = f.read()
    # Strict UTF-8 (a bad byte raises, never becomes U+FFFD); utf-8-sig drops a
    # BOM; CRLF and lone CR become LF so the hash and line numbers are stable.
    text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    if "�" in text:
        raise Fail(f"{DOC_REL} itself contains U+FFFD; fix the document")
    cards, rows = parse_doc(text)
    used = set()

    caps = []
    for row in rows:
        cap_text, possible, mp, routes_cell, spec = row["cells"]
        caps.append({"card": row["card"], "text": cap_text, "possible": possible,
                     "multiplayer": mp, "routes_cell": routes_cell,
                     "spec_link": [doc_link(t) for t in LINK_RE.findall(spec)],
                     "line": row["line"], "key": cap_key(row["card"], cap_text)})

    # IDs for capabilities are needed before fix-ups can be looked up; route
    # parsing does not depend on capability IDs, so do a first ID pass on
    # capabilities by building routes after a provisional parse.
    for c in caps:
        c["routes"] = []
    assign_caps_only(caps, existing)
    for c in caps:
        notes = []
        c["routes"] = parse_routes(c["id"], c["routes_cell"], notes, used)
        c["notes"] = notes
        if not c["routes"]:
            raise Fail(f"L{c['line']} {c['id']}: row has no route")
    retired = assign_ids(cards, caps, existing, accept)

    # fix-ups that matched nothing are stale
    for cap_id, pairs in CELL_FIXUPS.items():
        for old, _ in pairs:
            if ("cell", cap_id, old) not in used:
                raise Fail(f"CELL_FIXUPS[{cap_id}] unused: {old!r}")
    for cap_id, prefixes in NOTE_LINES.items():
        for p in prefixes:
            if ("note", cap_id, p) not in used:
                raise Fail(f"NOTE_LINES[{cap_id}] unused: {p!r}")
    for cap_id in MP_OVERRIDES:
        if cap_id not in {c["id"] for c in caps}:
            raise Fail(f"MP_OVERRIDES[{cap_id}]: no such capability")

    out_caps, out_routes = [], []
    all_route_ids = {r["id"] for c in caps for r in c["routes"]}
    for c in caps:
        mp_map, mp_prov = row_mp(c["id"], c["multiplayer"], c["routes"], used)
        out_caps.append({
            "id": c["id"], "card": c["card"], "text": c["text"],
            "possible": c["possible"], "multiplayer": c["multiplayer"],
            "spec_link": c["spec_link"], "notes": c["notes"],
            "line": c["line"], "key": c["key"],
        })
        for k, r in enumerate(c["routes"]):
            a = r["attrs"]
            src = r["shared"]["attrs"] if r["shared"] else None
            run = r["run_tail"]["attrs"] if r["run_tail"] else None
            ga = r["group_attrs"]
            prov = {}

            def pick(field, list_tail=False):
                if a[field] not in (None, False):
                    return a[field], "explicit"
                if src and src[field] not in (None, False):
                    return src[field], "inherited"
                if list_tail and run and run[field] not in (None, False):
                    return run[field], "inherited"
                if ga and ga[field] not in (None, False):
                    return ga[field], "inherited"
                return None, "unstated"

            weight, prov["weight"] = pick("weight", True)
            wtext = (a["weight_text"] or (src and src["weight_text"])
                     or (run and run["weight_text"])
                     or (ga and ga["weight_text"]) or None)
            if prov["weight"] == "unstated":
                wtext = a["weight_text"]         # e.g. "weight not stated"
            mapped = bool(wtext and "(mapped" in wtext and weight)
            kind, prov["kind"] = pick("kind", True)
            carrier, prov["carrier"] = pick("carrier")
            if a["multiplayer"]:
                mp, prov["multiplayer"] = a["multiplayer"], "explicit"
            elif src and src["multiplayer"]:
                mp, prov["multiplayer"] = src["multiplayer"], "inherited"
            elif k in mp_map:
                mp, prov["multiplayer"] = mp_map[k], mp_prov
            else:
                mp, prov["multiplayer"] = None, "unstated"
            summary = r["summary"]
            prov["summary"] = "explicit" if summary else "unstated"
            if not summary:
                # A route the card gives only a mark: the mark is its summary
                # ("not recommended: its donor code never runs"); failing
                # that, its group heading ("Release", "Map loaded").
                owners = [(r["text"], "explicit")]
                if r["shared"]:
                    owners.append((r["shared"]["text"], "inherited"))
                for t, pv in owners:
                    hit = [x.strip() for x in split_top(t)
                           if "*" in x and MARK_RE.search(x)]
                    if hit:
                        summary = hit[0].replace("*", "").strip(" ·")
                        prov["summary"] = pv
                        break
                if not summary and r["group"]:
                    summary, prov["summary"] = r["group"], "inherited"
            prov["source"] = "inherited" if c["spec_link"] else "unstated"
            full = r["raw"] + (" " + r["shared"]["raw"] if r["shared"] else "")
            italics = re.findall(r"\*([^*]+)\*", re.sub(r"\*\*[^*]+\*\*", "", full))
            marks = [m for m in italics if MARK_RE.search(m)]
            fallback = bool(re.search(r"fallback only|· fallback\b|· backstop\b"
                                      r"|a backstop only|the fallback if"
                                      r"|It is the fallback for", full))
            route = {
                "id": r["id"], "capability": c["id"],
                "label": r["label"], "group": r["group"],
                "summary": summary, "text": r["text"],
                "carrier": carrier, "kind": kind, "kind_text": a["kind_text"],
                "weight": weight, "weight_text": wtext, "weight_mapped": mapped,
                "multiplayer": mp,
                "not_recommended": any("not recommended" in m.lower() for m in marks),
                "marks": marks,
                "as_specced": bool(r["label"] and "as specced" in r["label"])
                or (r["label"] is None and r["raw"].startswith("**(as specced)**")),
                "fallback_only": fallback,
                "composes_with": [],
                "source": c["spec_link"],
                "line": c["line"],
                "provenance": prov,
                "key": r["key"],
            }
            if r["raw"].startswith("**(as specced)**"):
                route["label"] = "(as specced)"
            if r["id"] in COMPOSES_OVERRIDES:
                route["composes_with"] = COMPOSES_OVERRIDES[r["id"]]
                used.add(("composes", r["id"], None))
            else:
                comp = resolve_composes(c, r)
                if comp is None:
                    raise Fail(f"{r['id']}: 'compose' names a route outside its row; "
                               "add it to COMPOSES_OVERRIDES")
                route["composes_with"] = comp
            out_routes.append(route)

    by_id = {r["id"]: r for r in out_routes}
    # "A and B compose" as a row note: the two named routes compose.
    for c in out_caps:
        for n in c["notes"]:
            m = re.match(r"^([A-Z][\w′-]*) and ([A-Z][\w′-]*) compose\b", n)
            if not m:
                continue
            lab = {base_label(r["label"]): r["id"] for r in out_routes
                   if r["capability"] == c["id"] and r["label"]}
            x, y = lab.get(m.group(1)), lab.get(m.group(2))
            if not (x and y):
                raise Fail(f"{c['id']}: note {n!r} names a route not in its row")
            for s1, s2 in ((x, y), (y, x)):
                if s2 not in by_id[s1]["composes_with"]:
                    by_id[s1]["composes_with"].append(s2)
    # "The routes compose" (a row note): every route the card does not mark
    # not recommended composes with every other.
    for c in out_caps:
        if any(n.startswith("The routes compose") for n in c["notes"]):
            ok = [r["id"] for r in out_routes
                  if r["capability"] == c["id"] and not r["not_recommended"]]
            for rid in ok:
                by_id[rid]["composes_with"] = [x for x in ok if x != rid]
    for rid, fields in ROUTE_OVERRIDES.items():
        if rid not in by_id:
            raise Fail(f"ROUTE_OVERRIDES[{rid}]: no such route")
        for field, (value, prov) in fields.items():
            by_id[rid][field] = value
            if prov and field in by_id[rid]["provenance"]:
                by_id[rid]["provenance"][field] = prov
            if field == "marks":
                by_id[rid]["not_recommended"] = any(
                    "not recommended" in m.lower() for m in value)
    for rid, targets in COMPOSES_OVERRIDES.items():
        for t in [rid] + targets:
            if t not in all_route_ids:
                raise Fail(f"COMPOSES_OVERRIDES: no route {t}")
    # composition is symmetric where the card states it
    for r in out_routes:
        for t in r["composes_with"]:
            back = by_id[t]["composes_with"]
            if r["id"] not in back:
                back.append(r["id"])

    # uniqueness across the document
    ids = [c["id"] for c in cards if c["parent_card"] is None or True]
    ids += [c["id"] for c in out_caps] + [r["id"] for r in out_routes]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise Fail(f"duplicate IDs: {dup}")

    for c in cards:
        del c["line"]
    head = git("rev-parse", "HEAD")
    dirty = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", DOC_REL],
                           cwd=REPO, stderr=subprocess.DEVNULL).returncode != 0
    return {
        "schema": SCHEMA,
        "source": DOC_REL,
        "source_commit": head,
        "source_dirty": dirty,
        "source_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "counts": {"cards": len(cards), "capabilities": len(out_caps),
                   "routes": len(out_routes)},
        "cards": cards,
        "capabilities": out_caps,
        "routes": out_routes,
        "retired": retired,
    }


def assign_caps_only(caps, existing):
    """Capability IDs first: fix-ups are keyed by them."""
    old = {c["key"]: c["id"] for c in (existing or {}).get("capabilities", [])}
    retired = (existing or {}).get("retired", [])
    top, fresh = {}, {}
    for cid in list(old.values()) + [x for x in retired if "." not in x]:
        card, n = cid.rsplit("-", 1)
        if n.isdigit():
            top[card] = max(top.get(card, 0), int(n))
    for c in caps:
        if c["key"] in old:
            c["id"] = old[c["key"]]
        elif not old:
            fresh[c["card"]] = fresh.get(c["card"], 0) + 1
            c["id"] = f"{c['card']}-{fresh[c['card']]:02d}"
        else:
            top[c["card"]] = top.get(c["card"], 0) + 1
            c["id"] = f"{c['card']}-{top[c['card']]:02d}"


def make_slice(inv, cap_ids, note):
    """The inventory filtered to some capabilities, their cards and routes."""
    missing = [c for c in cap_ids if c not in {x["id"] for x in inv["capabilities"]}]
    if missing:
        raise Fail(f"--slice: no capability {missing}")
    keep = set(cap_ids)
    caps = [c for c in inv["capabilities"] if c["id"] in keep]
    routes = [r for r in inv["routes"] if r["capability"] in keep]
    card_ids = {c["card"] for c in caps}
    parents = {c["parent_card"] for c in inv["cards"]
               if c["id"] in card_ids and c["parent_card"]}
    cards = [c for c in inv["cards"] if c["id"] in card_ids | parents]
    return {
        "schema": inv["schema"], "source": inv["source"],
        "source_commit": inv["source_commit"], "source_dirty": inv["source_dirty"],
        "source_sha256": inv["source_sha256"], "retired": inv["retired"],
        "slice": note,
        "counts": {"cards": len(cards), "capabilities": len(caps),
                   "routes": len(routes)},
        "cards": cards, "capabilities": caps, "routes": routes,
    }


def dump(inv):
    out = json.dumps(inv, ensure_ascii=False, indent=2) + "\n"
    if "�" in out:
        raise Fail("output contains U+FFFD (a decoding error upstream)")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--accept-renumber", action="store_true",
                    help="retire IDs whose row or route vanished or was reworded")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the inventory is not what a run would write")
    ap.add_argument("--slice", metavar="ID,ID,...",
                    help="also write docs/data/route-inventory.slice.json: these "
                         "capabilities, their cards and routes, filtered verbatim")
    ap.add_argument("--slice-note", default="Filtered verbatim from "
                    "docs/data/route-inventory.json so every ID matches it.",
                    help="the slice file's 'slice' description")
    args = ap.parse_args()
    existing = None
    if os.path.isfile(OUT):
        with open(OUT, encoding="utf-8") as f:
            existing = json.load(f)
    try:
        inv = build(existing, args.accept_renumber)
    except Fail as e:
        print(f"route_inventory: FAILED\n{e}", file=sys.stderr)
        return 1
    text = dump(inv)
    if args.check:
        cur = open(OUT, encoding="utf-8").read() if existing else ""
        if cur != text:
            print("route_inventory: docs/data/route-inventory.json is stale")
            return 1
        print("route_inventory: up to date")
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    n = inv["counts"]
    print(f"route_inventory: {n['cards']} cards, {n['capabilities']} capabilities, "
          f"{n['routes']} routes -> docs/data/route-inventory.json")
    if args.slice:
        try:
            sl = make_slice(inv, [x.strip() for x in args.slice.split(",") if x.strip()],
                            args.slice_note)
        except Fail as e:
            print(f"route_inventory: FAILED\n{e}", file=sys.stderr)
            return 1
        with open(SLICE_OUT, "w", encoding="utf-8", newline="\n") as f:
            f.write(dump(sl))
        m = sl["counts"]
        print(f"route_inventory: slice {m['cards']} cards, {m['capabilities']} "
              f"capabilities, {m['routes']} routes -> docs/data/route-inventory.slice.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
