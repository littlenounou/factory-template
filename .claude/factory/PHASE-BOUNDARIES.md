# Phase boundaries (disclosed reference — reached from CLAUDE.md's Context Health pointer)

A **phase** is a chunk of work inside a session: the grilling, the implementation, the
review. Inside the factory, every `/feat-*` command is a phase and the ⏸ checkpoints are
boundaries. The boundary between two phases is the one place the question "what do I do
with this context?" belongs.

At a boundary, walk this ladder in order and take the first option that fits.

## 1. Continue

The next phase needs this conversation verbatim, or there is clearly room left. The only
option that keeps the session a **primary source** rather than a summary of one — which is
why it is the one to rule out first, deliberately, before reaching down the ladder.

*For the human, not the agent: Claude Code displays context usage; upstream treats roughly
150k tokens as the edge of sharp reasoning. A judgement aid for this option — never an
agent self-check.*

## 2. `/clear`

Nothing behind you is needed again. **The default at factory boundaries**: each step's
conclusions are already on disk under `<artifactsDir>/<slug>/`, and the next `/feat-*`
command re-reads them from files rather than from the window.

Strongest cases: after `/feat-grill` (the longest conversation in the line; `decisions.md`
holds the output) and after `/feat-spec` (planning ends, building starts; `brief.md` holds
the output).

## 3. Hand off

Reach for this when something must **travel**: another repo or directory, a colleague, a
side task forked mid-phase. What it buys is portability. The factory rarely needs it — the
artifacts dir is already a standing handoff document.

## 4. Subagent / slices

Tightly-scoped work goes to its own context window and reports back. In the factory the
builders already are subagents; oversized work is split via the brief's **Implementation
slices**, each slice running in its own builder context.

## 5. `/compact`

Bottom of the ladder: you must stay in THIS session, the history is too big, and nothing
above fits. A compacted session is confidently wrong about whatever the summary flattened,
so it is the last resort and it belongs at a boundary — compact between phases, with the
phase behind you finished.

## Mid-phase

There is nothing to decide mid-phase: continue, or split what is left into subagents. The
signals listed in `CLAUDE.md` are symptoms to surface as they happen, not triggers to
reshape context in flight.
