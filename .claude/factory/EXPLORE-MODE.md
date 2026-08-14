# EXPLORE Mode (disclosed reference — reached from CLAUDE.md's pointer)

Active from the moment the user says `explore mode` / `prototype` / `spike` /
`let's try it out` / `let's do a POC` / `let's see if this is feasible`, until they say
`let's commit to this direction` / `let's do this properly`.

`/feat-*` commands are always Default Mode; this file never applies inside the factory.

## Rule adjustments while active

| Rule | Behavior in EXPLORE Mode |
|------|--------------------------|
| Rule 3 (Think Before Coding) | **Weakened**: stop and ask for architecture-affecting decisions; decide small things yourself |
| Rule 4 (Simplicity First) | **Weakened**: quick scaffolding now, simplify later |
| Rule 5 (Surgical Changes) | **Disabled**: broad changes are fine during exploration |
| Rule 6 (Goal-Driven Execution) | **Weakened**: "it runs" counts as success |
| Rule 7 (Tests Verify Intent) | **Disabled**: tests are optional during exploration |
| Rule 8 (Match Conventions) | **Weakened**: new styles are fair game inside `prototype/`; conventions still hold elsewhere |
| Rule 10 (Checkpoint) | **Weakened**: report at demoable milestones |

## Still on, in every mode

- **Rule 0 (Fail Loud)** — a misleading exploration conclusion poisons every decision built on it.
- **Rule 1 (Pick a Side, Flag the Other)**
- **Rule 2 (Read Before You Write)**
- **Rule 9 (Use the Model Only for Judgment Calls)**

## Leaving EXPLORE Mode

1. Return to Default Mode.
2. List what the exploration skipped: tests, edge cases, documentation, error handling.
3. The user decides what to backfill and what to abandon.
4. Keep the prototype as runnable evidence where it stands; promoting it to production is
   a decision the user makes explicitly.
