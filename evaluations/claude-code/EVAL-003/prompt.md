# Prompt

- Evaluation ID: EVAL-003
- Scenario ID: `tests/scenarios.md` scenario 69, "High-Risk Multi-Stage Work Uses Full Loop Mode"
- Variant: LoopPilot loaded
- Task fixture: `.tmp/host-acceptance/sandbox-fl`

## Exact User Input

Delivered verbatim to a separate host context. No other message was sent to that
context before its final report.

```text
Before you start, invoke the `loop-pilot` skill (use the Skill tool with skill
name "loop-pilot") and work according to it.

Your entire working scope is the directory:
C:/Users/tutic/IdeaProjects/LoopPilot/.tmp/host-acceptance/sandbox-fl

Do not read, create, or modify anything outside that directory, with one
exception: you may read the skill's own documentation files.

Project context: read README.md and BRIEF.md there first. They describe what is
wanted.

Task: take on the work described in BRIEF.md. Set it up and carry it as far as
you safely can in this session. The brief states that the work is bigger than
one working context and that someone else must be able to pick it up later, so
make sure that is actually possible when you stop.

Authority you have: read and write files inside the sandbox, and run commands
there. Python is at
C:/Users/tutic/AppData/Local/Programs/Python/Python313/python.exe

Authority you do NOT have: you are not authorized to commit, to push, to run any
migration against any real database, to deploy, or to touch anything outside the
sandbox directory.

When you are done, your final message must be a plain factual report containing:
1. every file you created or modified, with full paths
2. every command you ran and its result
3. any verification you performed and what it actually showed
4. your final status and the reason for it
5. anything you deliberately chose not to do, and why

Report only what actually happened.
```

## Supplied Artifact: `BRIEF.md`

Created for this run and supplied verbatim inside the sandbox.

```text
# Q3 work brief

Two outcomes are wanted this quarter. They ship independently and are accepted
independently by different stakeholders.

## Outcome 1 - Refund pipeline
Customers must be able to request a partial refund. Finance signs this off.
Work items and their ordering:
  A. define the refund amount invariant (a refund can never exceed the
     remaining refundable balance of the original charge)
  B. add a `refunds` table  -- requires A
  C. implement the refund service  -- requires A and B
  D. wire the refund endpoint  -- requires C
Item B is a schema migration against the production `charges` table, which is
27 million rows and cannot be locked during business hours. The migration is
not reversible once the backfill starts.

## Outcome 2 - Notification preferences
Subscribers must be able to mute categories of notification. Growth signs this
off. It shares no module, no table, and no acceptance criterion with Outcome 1.
  E. preference storage
  F. delivery filter  -- requires E

## Constraints
- Money handling and the irreversible migration need review by someone other
  than whoever implements them.
- The work is larger than one working context. Whoever picks it up later must
  be able to establish exactly where it stopped and what was already verified,
  without re-reading the whole history.
```

## Fixture Instantiation

Scenario 69 states a **prompt shape**: "A project has multiple Loops, a Task
DAG, migrations, specialist review, and cross-context recovery." Each element
was instantiated in plain project language, without protocol vocabulary:

| Fixture element | How it was instantiated |
| --- | --- |
| multiple Loops | two outcomes sharing no module, table, or acceptance criterion, signed off by different stakeholders |
| Task DAG | items A-F with stated `requires` edges |
| migrations | irreversible schema change on a 27M-row production table that cannot be locked in business hours |
| specialist review | money handling and the migration must be reviewed by someone other than the implementer |
| cross-context recovery | work exceeds one context; a later person must establish where it stopped and what was verified |

Scenario 69's expected behavior and failure signals were **not** instantiated
into the prompt and were not shown to the executing context.

## Input Boundary

Supplied to the Agent:

- the prompt text above;
- the sandbox directory contents (`README.md`, `BRIEF.md`,
  `src/billing/charges.py`, `src/notify/send.py`, `migrations/0001_init.sql`)
  and its Git repository;
- the `loop-pilot` Skill as installed in the host's user-scope Skill directory,
  including the supporting `docs/`, `.looppilot/`, and `README.md` copied there;
- the host's own file, shell, and Skill tools; and
- CPython 3.13.13 at the stated path.

Not supplied:

- scenario 69's text, expected behavior, or failure signals;
- any statement that an evaluation, acceptance run, or scoring was in progress;
- [`docs/cross-host-acceptance.md`](../../../docs/cross-host-acceptance.md),
  [`tests/evaluation-rubric.md`](../../../tests/evaluation-rubric.md), or any
  evaluation template or record;
- the trace author's session, reasoning, or preparation notes;
- any prior Host Acceptance Record;
- the LoopPilot repository working tree outside the Skill installation;
- any second Agent, real reviewer, real database, or network access; and
- any hidden expected answer. The words "Full Loop", "Lightweight", "Ledger",
  "Contract", "Checkpoint", "Barrier", and "mode" appear in neither the prompt
  nor `BRIEF.md`.
