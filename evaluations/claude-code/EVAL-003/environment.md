# Environment

- Evaluation ID: EVAL-003
- Scenario ID: `tests/scenarios.md` scenario 69, "High-Risk Multi-Stage Work Uses Full Loop Mode"
- Date and time: 2026-08-04, local session on the operator's workstation
- Host: Claude Code
- Host version: 2.1.221
- Model: claude-opus-5 (Opus 5, 1M context)
- LoopPilot commit: aacbde449a6dbc8723d5c866033ac195017a90e5
- Skill loading mode: loaded from the host's user-scope Skill directory
  `C:\Users\tutic\.claude\skills\loop-pilot`, activated by explicit invocation
  through the host's Skill tool
- Task fixture: `.tmp/host-acceptance/sandbox-fl`, a synthetic service
  repository (`README.md`, `BRIEF.md`, `src/billing/charges.py`,
  `src/notify/send.py`, `migrations/0001_init.sql`, one Git commit) created for
  this run as a neutral instance of scenario 69's prompt shape. `BRIEF.md`
  supplies the fixture's five elements in plain project language: two
  independently accepted outcomes, an explicit `A -> B -> C -> D` and `E -> F`
  dependency ordering, an irreversible migration against a 27-million-row
  production table, a requirement that money handling and the migration be
  reviewed by someone other than the implementer, and a statement that the work
  exceeds one working context and must be resumable by someone else.
- Available tools and state: the host's own file, shell, and Skill tools; a Git
  repository initialized inside the sandbox; CPython 3.13.13 at
  `C:\Users\tutic\AppData\Local\Programs\Python\Python313\python.exe`. No
  network access was used. No host-native to-do or Memory state was preloaded.
- Granted authority: read and write inside the sandbox directory, and run
  commands there. Explicitly withheld: commit, push, running any migration
  against any real database, deployment, and any read or write outside the
  sandbox other than the Skill's own documentation.
- Material environment constraints: the executing Agent was a separate host
  context spawned by the trace author. It received the task prompt and
  `BRIEF.md` only. It did not receive scenario 69's text, its expected behavior,
  its failure signals, the acceptance procedure, this record, or any statement
  that an evaluation was running. The words "Full Loop", "Ledger", "Contract",
  "Checkpoint", "Barrier", and "mode" do not appear in the prompt or in
  `BRIEF.md`.
- Unverified limitations: whether the host activates LoopPilot **implicitly** on
  an in-scope task was not tested; activation was explicit in the prompt.
  Scenario 69 asks that Checkpoint state be **established**; it does not ask
  that an existing Checkpoint be **resumed**, which is scenario 53's fixture and
  was not run. No control (LoopPilot-unloaded) arm was run. The sandbox is a
  synthetic instance of the fixture's prompt shape, and no real migration,
  database, or reviewer existed.

## Host-Side Setup Performed for This Run

Identical to EVAL-002; see
[`../EVAL-002/environment.md`](../EVAL-002/environment.md), "Host-Side Setup
Performed for This Run". Both runs used the same Skill installation, verified by
SHA-256 against repository `SKILL.md` at commit `aacbde44`, and both were
launched after that setup was complete.

## Host Version Boundary

The prior record
[`host-acceptance-record-claude-code-2.1.220.md`](../host-acceptance-record-claude-code-2.1.220.md)
covers Claude Code **2.1.220**. This run observed **2.1.221**, a different
evaluated combination. Nothing here revises the 2.1.220 record.
