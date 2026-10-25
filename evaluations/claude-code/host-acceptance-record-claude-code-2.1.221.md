# Host Acceptance Record: Claude Code 2.1.221, claude-opus-5, Skill loaded, explicit invocation

- Host: Claude Code
- Host version: 2.1.221
- Model: claude-opus-5 (Opus 5, 1M context), as declared by the run packages
- LoopPilot commit: aacbde449a6dbc8723d5c866033ac195017a90e5
- Skill loading mode: loaded from the host's user-scope Skill directory,
  activated by explicit invocation through the host's Skill tool
- Evaluation IDs: EVAL-002, EVAL-003; both are incomplete evaluations, see below
- Scenario coverage: one Lightweight-shaped and one Full-Loop-shaped fixture
  were selected and prompted, but no trace or score was preserved, so coverage
  is declared design, not observed evidence
- Scenario IDs: `tests/scenarios.md` scenario 68, "Simple Change Uses
  Lightweight Mode"; scenario 69, "High-Risk Multi-Stage Work Uses Full Loop
  Mode"
- Trace author: the 2026-08-04 Claude Code 2.1.221 / claude-opus-5 session
  operated by `tutict`, which spawned one separate executing context per run,
  as declared in the run packages
- Independent reviewer: none obtainable; the Phase 11-B audit session reviewed
  the packages, is not independent, and had no trace to review
- Lowest critical rubric score: not established; no trace was scored
- Date: 2026-08-04
- Verdict: unverified
- Residual limitations: none claimed; this record makes no acceptance claim,
  so it discloses unverified limitations rather than residuals
- Unverified limitations: see the list below

## Evaluated Combination

| Element | Value |
| --- | --- |
| Host | Claude Code |
| Host version | 2.1.221 |
| Model | claude-opus-5 (Opus 5, 1M context) |
| Skill loading mode | loaded, user scope, explicit invocation |
| Execution environment | local CLI session; separate spawned context per run; CPython 3.13.13 |
| Operating system | Windows 11 Home China, 10.0.26200 |
| Repository | `https://github.com/tutict/LoopPilot.git`, branch `main`, HEAD `aacbde449a6dbc8723d5c866033ac195017a90e5` |
| Scenario IDs | `tests/scenarios.md` scenarios 68 and 69 |

This combination differs from the prior record
[`host-acceptance-record-claude-code-2.1.220.md`](host-acceptance-record-claude-code-2.1.220.md)
in host version and loading mode. Neither record generalizes to the other.

## Package Contents and Gaps

Preserved evidence for this combination consists of exactly four files, all
uncommitted at the time this record was written:
[`EVAL-002/environment.md`](EVAL-002/environment.md),
[`EVAL-002/prompt.md`](EVAL-002/prompt.md),
[`EVAL-003/environment.md`](EVAL-003/environment.md), and
[`EVAL-003/prompt.md`](EVAL-003/prompt.md).

No `trace.md` and no `score.md` exists for either run. The acceptance
procedure requires every acceptance run to record the environment, prompt,
trace, and score templates, and `evaluations/README.md` requires an evaluation
missing those elements to be reported as incomplete rather than scored around
the gap. Both runs are therefore incomplete evaluations. Sandbox end states
under gitignored `.tmp/host-acceptance/` corroborate that the runs executed
but are not preserved acceptance evidence. See
[`EVAL-002/reviewer-report.md`](EVAL-002/reviewer-report.md), Findings EV-5
through EV-7 and HI-1 through HI-2.

## What the Audit Session Verified Directly

Verified by direct command output on 2026-08-04, at repository HEAD
`aacbde449a6dbc8723d5c866033ac195017a90e5` with a clean tracked working tree:

- The `loop-pilot` Skill is installed in the host's user-scope Skill directory
  and registered with the host.
- The installed `SKILL.md` is byte-identical to the repository copy, SHA-256
  `a432bc262b954ede6bbbba893be7ee9bc76da61270b08587ebff9b20d9981778`.
- `SKILL.md` contains exactly 14 relative references and all 14 resolve from
  the installed Skill directory; the installed `docs/`, `.looppilot/`, and
  `README.md` are byte-identical to the repository.

These observations verify the installation state, not host behavior. They were
made by a session running model claude-fable-5, which is a different evaluated
combination; they are recorded here as installation corroboration only and are
deliberately not promoted into the dimension table.

## Dimension Results

| Dimension | Result | Evidence |
| --- | --- | --- |
| Skill loading and activation | not-evaluated |  |
| Mode selection | not-evaluated |  |
| Authority and stopping | not-evaluated |  |
| Shared-state handling | not-evaluated |  |
| Full Loop artifact handling | not-evaluated |  |
| Checkpoint recovery | not-evaluated |  |
| Lifecycle projections | not-evaluated |  |
| Evidence honesty | not-evaluated |  |

Every dimension is `not-evaluated` because no trace preserves protocol
behavior for this combination. A dimension without preserved evidence is
`not-evaluated`, not `pass`. No dimension is `fail`: nothing preserved shows a
protocol-relevant behavior this host cannot deliver. The Skill-loading
observation quoted in `EVAL-002/environment.md` is loading setup evidence, not
an activation-on-task trace, and is deliberately not promoted into this table.

## Reviewer Decision

`not-reviewed`. No evaluator independent of the trace author exists, and no
trace exists for any reviewer to certify. Recording `unverified` is the
required outcome, not a weaker form of acceptance.

## Unverified Limitations

- Every one of the eight acceptance dimensions. None has preserved evidence.
- Whether either run occurred exactly as declared. No trace was preserved;
  only prompts, environment declarations, and gitignored end states exist.
- Every rubric score for this combination, including all four critical
  dimensions.
- Whether the host activates LoopPilot implicitly on an in-scope task;
  activation was explicit in both prompts.
- Whether a fresh host process picks up the installed Skill without an
  existing session.
- The protocol's marginal effect: no control arm was run for either fixture.
- Any fixture other than scenarios 68 and 69, including scenario 53's
  resume-an-existing-Checkpoint fixture, which was not run.
- Any other host version, model, or Skill loading mode. This record covers
  exactly Claude Code 2.1.221 with claude-opus-5 and the Skill loaded from
  user scope under explicit invocation, and never generalizes to a later
  version, another model, another loading mode, or hosts as a class.
- Production reliability, longitudinal behavior, release, and deployment.

## Scope

Apply [`docs/cross-host-acceptance.md`](../../docs/cross-host-acceptance.md).
The verdict is scoped to this exact host, host version, model, and loading
mode. Observed evidence lives in the referenced evaluation packages; this
record summarizes and does not replace them. The packages and this record
belong in one commit unit; committing this record without the packages breaks
its evidence links.

This record does not satisfy the Release Candidate condition that the
reference host hold an observed `accepted` or `accepted-with-residuals`
record. That gate remains unmet.
