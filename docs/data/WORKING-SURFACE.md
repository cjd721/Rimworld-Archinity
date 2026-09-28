# The working surface — data contract

The working surface is the local page where the need tree, the tags, the strikes and the
suggestions of [the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119) live.
The method it serves is `docs/agents/need-sessions.md`. Run it with `tools/surface.cmd`
(or `python tools/surface_server.py`) and open http://127.0.0.1:8765.

Three files, kept apart:

1. **The inventory** — `docs/data/route-inventory.json`. Read-only reference, regenerated from
   `docs/CAPABILITIES.md` by `tools/route_inventory.py`. Cards, capability rows, routes.
   `docs/data/route-inventory.slice.json` is a verbatim 14-row subset, kept as a test fixture.
2. **The glosses** — `docs/data/capability-glosses.json`. A plain-language title and summary per
   capability and one plain line per route, agent-written from the cards and specs. The card and
   the spec win where they disagree. Read-only to the page.
3. **The surface state** — `docs/data/working-surface.json`. Conrad's working state. **The repo
   file is the state**: the page saves the whole file on every edit. It references inventory IDs
   only and never copies route text. It is working state, never the record of a decision.

**ID stability is the load-bearing rule.** Surface state points at inventory IDs, so a
regenerated inventory never renumbers an existing row or route: `route_inventory.py` fails
loudly instead, and `--accept-renumber` retires the old IDs for good.

## Inventory

```jsonc
{
  "schema": "archinity.route-inventory/1",
  "source": "docs/CAPABILITIES.md",
  "source_commit": "<git sha>",
  "cards": [{
    "id": "ALTAR",                         // short uppercase slug, unique
    "title": "The altar",
    "group": "Faith",                      // H2 section
    "parent_card": null,                   // "RELIGION" for the four Religion sub-cards
    "anchor": "docs/CAPABILITIES.md#the-altar",
    "possible": "…", "multiplayer": "…",   // card-level lines
    "story_can": ["…"], "story_cannot": ["…"],
    "spec": ["docs/specs/ALTAR.md"]
  }],
  "capabilities": [{
    "id": "ALTAR-01",                      // <CARD>-<nn>, in document order
    "card": "ALTAR",
    "text": "Charge that never spoils; the donor dies, the recipient lives",
    "possible": "…", "multiplayer": "…",   // row cells
    "spec_link": ["docs/specs/ALTAR.md#…"],
    "notes": []                            // card text about the row that is not a route
  }],
  "routes": [{
    "id": "ALTAR-01.A",                    // globally unique; see "Route IDs"
    "capability": "ALTAR-01",
    "label": "A (already built)",          // as the card prints it; may be null
    "group": null,                         // sub-heading inside the cell ("Offer", "Ending"), else null
    "summary": "one line: what it gets us",
    "carrier": "…",                        // null when unstated
    "kind": ["xml", "cs"],                 // subset of xml | patch | cs; null when unstated
    "weight": "easy",                      // easy | medium | hard | easy-medium | medium-hard | varies | null
    "weight_text": "Easy (mapped)",        // as printed
    "weight_mapped": true,
    "multiplayer": "…",                    // null when unstated and not inheritable
    "not_recommended": false,
    "as_specced": false,
    "fallback_only": false,
    "marks": [],                           // the card's italic qualifiers, verbatim
    "composes_with": [],                   // only where the card says so; may cross capabilities
    "source": ["docs/specs/ALTAR.md#…"],
    "provenance": { "summary": "explicit", "weight": "explicit", "multiplayer": "inherited" }
                                           // explicit | inherited | unstated, per normalised field
  }]
}
```

**Route IDs** are opaque: read a route's capability from its `capability` field, never from its
ID. A card's own route ID is kept bare where unique (`OS-1`, `AS-4`), card-prefixed where two cards
share it (`ERA.HF-4`, `ANDROIDS.HF-4`). Routes with no card-own ID are minted
`<capability>.<label>` (`ALTAR-01.A`, `CHURCH-07.U1`).

## Surface state

```jsonc
{
  "schema": "archinity.working-surface/1",
  "inventory_commit": "<source_commit of the inventory it was built against>",
  "exported_at": "ISO-8601",               // set on every save
  "needs": [{ "id": "N-001", "parent": null, "statement": "…", "description": "", "order": 0 }],
  "sessions": ["N-003", "N-007"],          // the session partition: need IDs that are sessions
  "tags": [{ "capability": "ALTAR-01", "need": "N-003", "note": "" }],
  "no_owner": [{ "capability": "ALTAR-04", "note": "" }],
  "route_global": [{ "route": "ALTAR-05.B", "state": "struck", "reason": "…" }],   // absent = viable
  "route_need": [{ "route": "…", "need": "N-003", "state": "suggested|rejected|open", "reason": "…", "reopen": "…" }],
  "capability_decision": [{
    "capability": "ALTAR-05",
    "state": "selected|open",
    "routes": ["ALTAR-05.A"],              // selected; may compose
    "decided_by": "#NNN",                  // required when selected
    "candidates": [], "known": "", "reopen": ""   // when open
  }],
  "notes": [{ "target": "ALTAR-01 | N-003", "text": "…" }],
  "followups": [{
    "id": "F-001",
    "target_type": "need|capability|route",
    "target": "FOUNDERS-03.A1",
    "kind": "wrong|dig",                   // "this is wrong" | "dig into this"
    "note": "…",
    "status": "open|done",
    "created": "ISO-8601"
  }]
}
```

**Follow-ups** are Conrad's flags for an agent to work later: a wrong need or capability goes back
to `docs/requirements/` and the spec, a vague route to a research ticket. The page never spawns an
agent.

**File format.** Two-space indent, UTF-8, trailing newline. Keys in the order shown, at the top
level and inside every item; unknown keys kept, sorted, after the known ones. Arrays keep insertion
order. Written atomically by the server. A save is refused if the file changed on disk since the
page loaded it, so an agent editing the file is never silently overwritten.

## Invariants

Enforced by the page. An agent writing the file directly must keep them.

- Exactly one root need (`parent: null`), the founding principle. It cannot move or be deleted.
  No cycles. `order` is 0..n-1 among siblings.
- **Sessions never nest.** Marking a need a session unmarks any session among its ancestors and
  descendants.
- Deleting a need moves its children up to its parent and removes its tags, `route_need` rows,
  session mark, note and follow-ups.
- `tags` is unique per (capability, need). `no_owner` only on an untagged capability; tagging one
  clears the mark. Untagging removes that need's `route_need` rows for the capability.
- `route_global`: a strike needs a reason. A selected route cannot be struck.
- `route_need` is unique per (route, need) and requires the capability to be tagged to that need.
  `suggested`/`rejected` need `reason`; `open` needs `reopen`. A struck route cannot be suggested.
- `capability_decision` is unique per capability. `selected`: at least one unstruck route of that
  capability and `decided_by` matching `#<number>`. `open`: `reopen` required, candidates are
  unstruck routes of that capability. Selecting routes the card does not say compose is allowed
  but flagged.
- `notes`: at most one per target. `followups`: `id` unique.

## Computed, never stored

- **Session of a need**: the nearest ancestor-or-self in `sessions`.
- **Owned / shared**: a capability's tagged needs fall in one session → owned; more than one →
  shared; none → unpartitioned.
- **Orphans**: capabilities with no tag and no `no_owner`; needs with no tag in their subtree.
- **A session's suggestion** for a capability: the union of `suggested` routes over its tagged needs.
- **Compose**: two routes compose if either lists the other in `composes_with`, or they sit in
  different `group`s of one capability (Offer + Ending).
- **Conflicts**, per shared capability: `conflict` (suggestion sets differ and do not all compose,
  or one session rejects what another suggests), `agree`, `compose`, `waiting` (fewer than two
  sessions have suggested) or `decided`.

## Server endpoints

- `GET /` — the page. `GET|PUT` the state file; `GET` the inventory and `/api/glosses`.
- `GET /api/doc?path=docs/…md&anchor=slug` — one markdown section, read-only, from under `docs/`
  only (traversal rejected), cut at the next heading of the same or higher level.
- Flags: `--port` (8765), `--inventory`, `--state`, `--glosses`.
