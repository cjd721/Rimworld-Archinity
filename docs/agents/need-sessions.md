# Selecting routes by narrative need

How [the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119) turns
`docs/CAPABILITIES.md` — about 200 capability rows and 450–500 routes — into the best route
baseline the story supports before any act is written. Three stages, in order:

1. **Tree passes** — Conrad alone, on the working surface. Build the need tree, tag
   capabilities to needs, strike the routes that are obviously out. Sorting and elimination
   only; nothing is chosen.
2. **Need sessions** — Conrad with an agent, one per top-level branch of the tree. Select the
   routes each branch owns where the story gives a reason to; suggest routes for the ones it
   shares; leave the rest honestly open.
3. **The conflict pass** — Conrad with an agent. Review every shared capability, reading
   each branch's suggestion side by side, and select where the story supports a choice.

Acts, beats and grids follow, written against what is selected. Each act then sharpens what
was left open — see [Handing on what is open](#handing-on-what-is-open).

## Vocabulary

- **Need** — something the campaign must deliver to the player, in the story's terms: _the
  colony is worshipped as gods_. A node in the **need tree**, whose root is the campaign's
  founding principle. See `CONTEXT.md`.
- **The working surface** — the artifact where the tree, the tags, the strikes and the
  suggestions live. It is **working state**, never the record of a decision. It is a local page
  whose state is `docs/data/working-surface.json`; its data contract, and how to run it, are in
  `docs/data/WORKING-SURFACE.md`.
- **Owned** and **shared** — computed from the **final session partition**, below.
- **Open** — a capability with no selection yet because the story that would decide it is
  unwritten. Not a failure; see [Leave honest gaps](#leave-honest-gaps).

## Route state

Three layers, kept apart:

| Layer               | Values                                                                 | Set by                                                      |
| ------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------- |
| Global, per route   | viable · struck                                                        | Tree pass 3; a need session may strike, only Conrad reopens |
| Per need, per route | suggested · rejected, each with a reason; or **open** for this need, with what should reopen it | Need sessions                                               |
| Per capability      | **selected** route(s), with `decided_by` — the ticket that decided it; or **open**, with its surviving candidates, what is known, and the story question or act that should reopen it | Need sessions (owned), the conflict pass (shared), later the acts |

A route struck globally is gone for every need. A route rejected for one need may still be
suggested by another.

## The session partition

A need session covers one node. **By default it is a top-level branch**; it splits into its
children only when it is too much for one sitting. Roughly 15 capability rows or 40 surviving
routes is the point to consider it — a heuristic; complexity matters more than the count.

Once a node is split, **the parent is no longer a session**; its children are. Ownership is
read off that final partition:

- **Owned** — every need tagged to the capability falls inside one actual session.
- **Shared** — its tagged needs fall in more than one session.

A shared capability is only a **conflict** when its sessions' suggestions are incompatible.
Where they agree, or compose, the conflict pass confirms the selection without debate.

## Running a need session

**Grilling, with Conrad.** Call the Skill tool for `grilling` and `domain-modeling`. Conrad
decides; the agent prepares, presents and recommends.

### Before the session — the agent, alone

1. Load the node from the working surface's by-need view: every capability tagged under it,
   its surviving routes, and Conrad's pass notes.
2. Mark each capability **owned** or **shared** against the current partition, naming the
   other sessions that share it.
3. Pull the passages in `docs/PLOT.md`, `docs/plot/` and `docs/requirements/` where this need
   shows up. Cite them; do not summarise the chapters. **PLOT.md's _at a glance_ table is
   unreliable on when systems become available** — read it for story, not for gating.
4. Order the capabilities so the ones others depend on come first.
5. If an existing ticket's question falls under this node, it is this session's input.
   Answer its question here, in its own words, and close it against this session.

### In the session

1. **Restate the need as it plays.** Draft two or three sentences of what this need looks like
   across the whole campaign, from the node and the passages; Conrad corrects it. This is the
   yardstick every route below is weighed against. Settle it before any route.
2. **Walk the capabilities in order.** For each, present the surviving routes as **what the
   player experiences under this need**, not how they are built. Weight and Multiplayer, one
   line each. Recommend one — or say that the story does not yet give a reason to.
   - **Owned:** Conrad selects, or leaves it open. A selection may compose routes the card
     says compose.
   - **Shared:** Conrad suggests a route **for this need**, with a reason written for his
     future self — _"A: more believable pawn worship"_ — or records it as open for this need.
     Nothing is selected.
   - **Where it is known, settle how it comes into play** — always on, research, an unlock, a
     beat — and what gating costs to build. Many systems cannot be gated cheaply; say so.
3. **Dig only when a choice is stuck on a fact.** If picking between routes needs something
   below route depth, send a subagent to read the spec section or the carrier's source, and
   take the next capability while it reads. Never guess a shape. A choice stuck on *story* is
   not a dig — it is open.
4. **Record the edges as they come up.**
   - A capability tagged here comes off the tag, with a one-line reason, only when it is
     known not to serve this need. If it may serve it but the unwritten story prevents a
     judgment, it stays tagged and open.
   - A beat or act idea goes in a _For the acts_ list. It is not written as a beat.

### Leave honest gaps

Select a route when the material that exists gives Conrad a reason to choose it. When
materially different routes depend on story that has not been written, leave the capability
**open**: record the surviving candidates, what is known, and — when it can be named — the
story question or act that should reopen it. **Do not choose a placeholder route.**

> Open: routes A and C give different versions of the Church's betrayal, and no act has yet
> established whether betrayal precedes the first rite. Revisit when that act is outlined.

If even the missing question cannot be named, say so:

> Open: this capability's narrative use is not visible yet. Revisit when its era is outlined.

**Orphans may persist.** A capability with no need and a need with no capability are
discovery queues, not errors. Classify one — a missing capability, a new requirement, a need
to drop — and ticket it only once enough story exists to state what is missing.

### Close

- Post the resolution comment: the restated need; a table of capability · owned/shared ·
  selected, suggested or open · reason (or, if open, candidates and what reopens it) · how it
  comes into play; then _For the acts_.
- Mark selections (with `decided_by`), suggestions and open items on the working surface.
- **Do not edit specs.** Selected routes go into `docs/specs/` in one sweep after the conflict
  pass, so the conflict pass never has to undo a spec.
- **Not this session's:** beats, numbers and balance, affordance sheets, selecting a shared
  capability.
- **Done** when every capability in the node is selected, suggested, removed from the need,
  or recorded as open. Open items do not keep a session alive.
- **Too big:** split only when volume stopped the work — never because an answer is
  genuinely unknowable. Split what is left by child node into new tickets and repartition.

## The conflict pass

Its agenda is the surface's conflicts view. It may be one ticket or several; split a large one
into batches that follow dependency, never alphabetically. Each resolution records the
selection, the reason, and which suggestions it overrode. A shared capability whose
suggestions give no reason to choose stays open, with the same record as above.

## Handing on what is open

Open items and orphans become inputs to the act work. Record enough context and a revisit
trigger that a later agent can resume each one without this session's conversation.
