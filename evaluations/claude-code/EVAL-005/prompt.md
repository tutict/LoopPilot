# Prompt

Both fixture prompts are **preserved verbatim** and are reproduced below. Each is
independently attested twice: as a file written before the run under the
gitignored `.tmp/phase14/` path, and as record 0 of the corresponding transcript
in [`evidence/`](evidence/README.md). The two agree byte for byte.

Nothing on this page is reconstructed.

## Fixture A — explicit invocation, Lightweight-shaped

Source: `.tmp/phase14/prompt-fixture-a.txt`, and record 0 of
`evidence/fixture-a.redacted.jsonl`.

```text
Use the LoopPilot skill for this task.

In C:\Users\tutic\IdeaProjects\LoopPilot\.tmp\phase14\fx-a there is a Python module `settings.py` with a unittest suite `test_settings.py`. One test fails.

The module's docstring is the specification. Make the failing test pass without breaking the others, and confirm the whole suite passes.

Use CPython at C:\Users\tutic\AppData\Local\Programs\Python\Python313\python.exe. Do not change the tests. Do not commit anything.

Report which LoopPilot mode you selected and why.
```

## Implicit fixture — no invocation instruction

Source: `.tmp/phase14/prompt-implicit.txt`, and record 0 of
`evidence/implicit-fixture.redacted.jsonl`.

```text
In C:\Users\tutic\IdeaProjects\LoopPilot\.tmp\phase14\fx-implicit there is a small Python module `textwrap_util.py` with a unittest suite `test_textwrap_util.py`. The suite is currently failing.

Please diagnose the cause, fix the module so the whole suite passes, and confirm that it passes.

Use CPython at C:\Users\tutic\AppData\Local\Programs\Python\Python313\python.exe. Do not change the tests.
```

The word `LoopPilot` appears in the implicit prompt only as part of the
repository path. No instruction to use, load, or invoke the Skill is present, and
no protocol vocabulary — `Lightweight`, `Full Loop`, `Ledger`, `Contract`,
`Checkpoint`, `Barrier`, `mode` — appears in it.

## Input Boundary

Supplied to each fixture context:

- the prompt text above, as its first and only user message;
- its own fixture directory under `.tmp/phase14/`;
- the `loop-pilot` Skill as installed in the host's user-scope Skill directory;
- the host's own file, shell, and `Skill` tools;
- CPython 3.13 at the stated path.

Not supplied to either context:

- any statement that an evaluation, acceptance run, or scoring was in progress;
- [`docs/cross-host-acceptance.md`](../../../docs/cross-host-acceptance.md),
  [`tests/evaluation-rubric.md`](../../../tests/evaluation-rubric.md), or any
  evaluation template, record, or rubric;
- the spawning session's conversation, reasoning, or preparation notes;
- any prior Host Acceptance Record;
- any second evaluator, reviewer, or network access;
- any hidden expected answer.
