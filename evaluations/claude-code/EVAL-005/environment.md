# Environment

Observed facts only. Every value below is read from the preserved transcripts'
own fields or recomputed from this repository; nothing is declared from memory.

- Evaluation ID: EVAL-005
- Scenario ID: named fixtures `phase14-lightweight-explicit` and
  `phase14-implicit-activation`. Neither corresponds to a numbered scenario in
  [`tests/scenarios.md`](../../../tests/scenarios.md).
- Date and time: the transcripts carry host timestamps from
  `2026-08-09T16:07:51Z` to `2026-08-09T16:55:22Z` (UTC).
- Host: Claude Code
- Host version: `2.1.224`, recorded in the `version` field of **every** record of
  both transcripts — 30 of 30 and 29 of 29.
- Model: `claude-opus-5`, recorded in the `message.model` field of all 17 real
  assistant records in Fixture A and all 18 in the implicit fixture. Fixture A
  carries one further assistant record whose model is `<synthetic>`; that is the
  host's own error envelope, not a model turn.
- Skill loading mode: installed in the host's user-scope Skill directory
  `C:\Users\tutic\.claude\skills\loop-pilot`. Fixture A activated it by explicit
  invocation through the host's `Skill` tool. The implicit fixture was given no
  instruction to invoke it.
- LoopPilot commit: `SKILL.md` is blob
  `6e0f26a9e948659541f88fc066e4e70dfcb31b0b`, byte-identical from
  `aacbde449a6dbc8723d5c866033ac195017a90e5` through
  `672f3955495cb4b6fff332c11eb23882f8479279`. The digest in `trace.md` therefore
  anchors to both without ambiguity.
- Execution context: both fixtures ran as background sub-contexts spawned by a
  parent Claude Code session, each recorded with `isSidechain: true` and its own
  `agentId`. Each context's first message is its fixture prompt; neither
  inherited the parent conversation.
- Working directory: `C:\Users\tutic\IdeaProjects\LoopPilot`, git branch `main`.
- Task fixtures: two synthetic Python modules with unittest suites, created for
  these runs under the gitignored `.tmp/phase14/` path — `fx-a/settings.py` with
  `test_settings.py` (9 tests, 1 failing at start), and
  `fx-implicit/textwrap_util.py` with `test_textwrap_util.py` (6 tests, 2 failing
  at start). CPython 3.13 at
  `C:\Users\tutic\AppData\Local\Programs\Python\Python313\python.exe`.
- Available tools: the host's own file, shell, and `Skill` tools. No network
  access was used.

## Trace Author and Self-Observation

The trace author is the Claude Code 2.1.224 / claude-opus-5 session that spawned
both fixtures. **Neither fixture is self-observing**: each ran in a separate
context whose transcript the author did not write. This distinguishes EVAL-005
from [`EVAL-004`](../EVAL-004/environment.md) Arm A, where the observing session
was itself the subject.

What that does not remove: the author still selected the fixtures, wrote the
prompts, and assembled this package, and both fixture contexts ran with the
LoopPilot repository as their working directory and the project's memory index
available. Their observed reads were confined to the Skill's own documentation
and their own fixture directories — no evaluation record, rubric, checklist, or
acceptance document was read by either.

## Material Environment Constraints

- Fixture A was terminated mid-run by the host with a non-transient HTTP 429
  (`error: "rate_limit"`) at `16:55:22.526Z`, after its verification step and
  before its final report. Its report does not exist and is not reconstructed.
- The parent session was terminated by the same condition minutes later.
- The transcripts are unsigned, were written by the host into a cache outside
  version control, and are operator-writable. The redacted copies in
  `evidence/` inherit that limitation: they cannot prove their own source was
  unaltered.

## Unverified Limitations

- Every acceptance dimension except the loading half of dimension 1.
- Every rubric score, including all four critical dimensions. No score exists.
- Whether Fixture A's declared mode was correct. It is recorded, not judged.
- What the implicit fixture's non-activation means for dimension 1. It is
  recorded, not judged.
- The protocol's marginal effect: no control arm was run for either fixture.
- Any other host version, model, or loading mode. This package covers exactly
  Claude Code 2.1.224 with claude-opus-5, and never generalises.
