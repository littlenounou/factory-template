---
description: Plan an effort bigger than one feature as a map of decision tickets, burned down one per run, handing off paste-ready /feat-new lines.
argument-hint: <epic-slug> ["<description>" to chart | [ticket] to work]
---
Epic planning for `$1`.

The epic PLANS; the features DO. Every ticket holds a question whose resolution is a
decision, never a slice of the build. The map is done when nothing is left to decide
before features start — then it hands off `/feat-new` lines and stops. The pull to just
build something is the signal that you have reached the edge of the map.

Everything lives in `<artifactsDir>/epics/$1/` (`artifactsDir` from
`.claude/factory/project.json`): `map.md` plus `tickets/NN-<name>.md`. The map is the
epic's state — there is no `state.json` — and this command writes only inside its epic
folder, leaving `.active` and every feature untouched, so it may run mid-feature.

**Mode.** If `<artifactsDir>/epics/$1/map.md` exists → WORK (an optional second token names
a ticket). Otherwise → CHART, and the rest of "$ARGUMENTS" is the description (required).

**Refer by name.** In everything the human reads, a ticket is its title, linked to its
file — never a bare number.

## Map and ticket format
`map.md` is an INDEX, not a store: each decision lives in exactly one place, its ticket.
```
# <epic title>
Status: charting | cleared
## Destination        — what reaching the end looks like; 1–2 lines; fixes the scope
## Notes              — domain, standing preferences, ❓ Needs-human-input items
## Decisions so far   — one line per answered or delegated ticket:
                        - [<title>](tickets/NN-name.md) — <gist>
## Not yet specified  — fog: in-scope questions not yet sharp enough to ticket
## Out of scope       — one line each: gist + why, linking the closed ticket if any
## Feature breakdown  — written when the map clears (see WORK step 6)
```
Ticket `tickets/NN-<name>.md`, sized to one session:
```
# <title>
Type: research | grilling | prototype
Status: open | closed | out-of-scope | delegated
Blocked by: <ticket titles, or `human — <what>`, or none>
## Question
## Resolution         — added on close: the answer, or the feature that now owns
                        the question; assets linked, not pasted
```
The FRONTIER is every open ticket whose blockers are all closed, in NN order.

**Ticket types.**
- **research** (AFK) — a fact a decision waits on. Resolve with the built-in **Explore**
  subagent IN THE BACKGROUND, one per ticket, in parallel; you write its findings into the
  ticket. When Explore is denied web access, do the lookup in the main session.
- **grilling** (HITL) — the decision itself. Use `/feat-grill`'s round shape (frontier
  rounds, `❓ Q<n>` / `➡️` recommendation). Only the human answers the human's side.
- **prototype** (HITL) — the question is "how should it look / behave". A text prototype
  (outline, flow, sample output) goes in the Resolution. A code prototype is built by the
  human in EXPLORE Mode under `prototype/` and linked; the ticket closes once they react.

A step only a human can do (sign up for a service, pull sample data) is not a ticket: add
`❓ Needs-human-input: <what>` to Notes and set `Blocked by: human — <what>` on the ticket
that waits for it. It rejoins the frontier when the human reports it done.

**Fog or ticket?** Ticket when you can state the question precisely now, even if it is
blocked. Leave it in Not yet specified when you cannot; one patch may graduate into
several tickets, or none. Work beyond the Destination is Out of scope, never fog.

**Three ways a ticket closes.** Answered; out of scope (beyond the Destination); or
**delegated** — it moves one feature only, so that feature's `/feat-grill` settles it. A
question that shapes the split between features, or that several depend on, stays with the
epic. The last two drop work from the map without answering it, so the human rules on each
one (WORK step 3).

## CHART — `/feat-epic <epic-slug> "<description>"`
1. GUARD: `$1` must not be `epics` and must not be an existing feature folder
   `<artifactsDir>/$1/` — epics and features share one slug namespace. STOP if either.
2. Read root `CLAUDE.md` and `<artifactsDir>/MEMORY.md` (if present). A `[durable]`
   decision there is settled; re-open it only with new evidence, and say so.
3. **Name the destination.** Grill (round shape above) until the Destination is agreed.
4. **Map the frontier.** Grill again BREADTH-FIRST: fan out across the whole space for the
   open decisions and the questions takeable now. If this surfaces no fog, the effort fits
   the normal line: write nothing, give paste-ready `/feat-new` line(s), and stop.
5. Write `map.md` (Status `charting`, Decisions so far empty, fog in Not yet specified),
   then the tickets you can specify now, then wire `Blocked by` in a SECOND pass.
6. Dispatch every research ticket (see Ticket types) and record what returns.
7. Stop. Charting resolves no HITL ticket.

## WORK — `/feat-epic <epic-slug> [ticket]`
1. Read `map.md` only; open a ticket's body when you need it.
2. Dispatch every research ticket on the frontier in the background, then choose ONE HITL
   ticket: the named one, else the first on the frontier. If no HITL ticket is on the
   frontier but fog remains, grill breadth-first to graduate it into tickets.
3. Resolve it by its type. In the same round, put any ticket you would drop from the map —
   the one in hand included — to the human as one more `❓` with a `➡️` recommendation:
   out of scope, or delegated to a named feature.
4. Record an answered ticket: write the Resolution, set Status `closed`, append its line to
   Decisions so far.
5. Update the map from the answers: create newly surfaced tickets (then wire them);
   graduate fog the answer made specifiable, removing it from Not yet specified; close each
   dropped ticket the human ruled on — out of scope (Status `out-of-scope`, its line in Out
   of scope) or delegated (Status `delegated`, its Decisions-so-far line reading
   `delegated to <feature-slug> — <the open question>`); rewrite or delete tickets the
   decision invalidated.
6. **Clear the map** when no open ticket and no fog remain: agree the split in one final
   grilling round — features, build order, what depends on what — then write Feature
   breakdown, one entry per feature, in build order:
   `/feat-new <slug> <one-line description> [epic: $1]`, plus `after: <slugs>` if any and
   `open: <ticket titles>` for every question delegated to that feature.
   Each slug is new: not `epics`, not this epic, not an existing feature. Set Status
   `cleared`. This command creates no feature folder; the human runs the lines.
7. Stop after one HITL ticket. The seam between tickets is a phase boundary
   (`.claude/factory/PHASE-BOUNDARIES.md`).

## Close every run
Name the files written, then every ticket dropped this run and where it went, then the next
command: `/feat-epic $1` while Status is `charting`; once `cleared`, the first `/feat-new`
line of Feature breakdown. End with this reminder, verbatim: "Epic and feature slugs share one namespace — a `/feat-new` slug may not be
`epics` or an epic's slug."

End with the Fail-Loud block: ✅ Verified (tickets resolved, research recorded, map updated)
/ ⚠️ Skipped-Uncertain (research left open, blockers you could not settle) /
❓ Needs-human-input.
