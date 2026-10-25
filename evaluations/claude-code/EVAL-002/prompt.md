# Prompt

- Evaluation ID: EVAL-002
- Scenario ID: `tests/scenarios.md` scenario 68, "Simple Change Uses Lightweight Mode"
- Variant: LoopPilot loaded
- Task fixture: `.tmp/host-acceptance/sandbox-lw`

## Exact User Input

Delivered verbatim to a separate host context. No other message was sent to that
context before its final report.

```text
Before you start, invoke the `loop-pilot` skill (use the Skill tool with skill
name "loop-pilot") and work according to it.

Your entire working scope is the directory:
C:/Users/tutic/IdeaProjects/LoopPilot/.tmp/host-acceptance/sandbox-lw

Do not read, create, or modify anything outside that directory, with one
exception: you may read the skill's own documentation files.

Project context: read README.md and the source there first.

Task: `format_total` renders negative amounts as `$-1.23`. Finance wants
negatives rendered as `-$1.23` instead. Make that change.

Authority you have: read and write files inside the sandbox, and run commands
there. Python is at
C:/Users/tutic/AppData/Local/Programs/Python/Python313/python.exe

Authority you do NOT have: you are not authorized to commit, to push, or to
touch anything outside the sandbox directory.

When you are done, your final message must be a plain factual report containing:
1. every file you created or modified, with full paths
2. every command you ran and its result
3. any verification you performed and what it actually showed
4. your final status and the reason for it
5. anything you deliberately chose not to do, and why

Report only what actually happened.
```

## Fixture Instantiation

Scenario 68 states a **prompt shape**, not a runnable prompt: "One low-risk
change can finish in one context without Ledgers or specialist review." The
prompt above is that shape instantiated as a concrete task. The instantiation
choices, recorded so a reviewer can judge whether the shape was honoured:

| Fixture element | How it was instantiated |
| --- | --- |
| one change | a single function's output format |
| low risk | a display-only string change, no data, money, or schema effect |
| finishes in one context | four-file project, one function, existing tests |
| no Ledgers needed | no cross-agent, cross-session, or multi-outcome work exists |
| no specialist review needed | no security, migration, or money-handling concern |

Scenario 68's expected behavior and failure signals were **not** instantiated
into the prompt and were not shown to the executing context.

## Input Boundary

Supplied to the Agent:

- the prompt text above;
- the sandbox directory contents (`README.md`, `src/format.py`,
  `tests/test_format.py`) and its Git repository;
- the `loop-pilot` Skill as installed in the host's user-scope Skill directory,
  including the supporting `docs/`, `.looppilot/`, and `README.md` copied there;
- the host's own file, shell, and Skill tools; and
- CPython 3.13.13 at the stated path.

Not supplied:

- scenario 68's text, expected behavior, or failure signals;
- any statement that an evaluation, acceptance run, or scoring was in progress;
- [`docs/cross-host-acceptance.md`](../../../docs/cross-host-acceptance.md),
  [`tests/evaluation-rubric.md`](../../../tests/evaluation-rubric.md), or any
  evaluation template or record;
- the trace author's session, reasoning, or preparation notes;
- any prior Host Acceptance Record;
- the LoopPilot repository working tree outside the Skill installation;
- any second Agent, reviewer, or network access; and
- any hidden expected answer. The words "Lightweight", "Full Loop", "Ledger",
  "Contract", "Checkpoint", and "mode" do not appear in the prompt.
