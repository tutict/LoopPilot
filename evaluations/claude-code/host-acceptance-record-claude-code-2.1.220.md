# Host Acceptance Record: Claude Code 2.1.220, claude-opus-5, Skill not loaded

- Host: Claude Code
- Host version: 2.1.220
- Model: claude-opus-5
- LoopPilot commit: 882df4968e8862835e93fe5fdd4d28690565ed4d
- Skill loading mode: not loaded; no `loop-pilot` Skill in project or user scope, no `CLAUDE.md`
- Evaluation IDs: EVAL-001
- Scenario coverage: one fixture only, control-shaped; neither a Lightweight-shaped nor a Full-Loop-shaped protocol fixture was exercised
- Scenario IDs: `tests/scenarios.md` scenario 43, "Requested Skill Is Unavailable"
- Trace author: Claude Code 2.1.220 / claude-opus-5 agent session operated by `tutict`
- Independent reviewer: none obtainable in this session; see the reviewer report
- Lowest critical rubric score: not established; self-scored only and not independently reviewed
- Date: 2026-08-03
- Verdict: unverified
- Residual limitations: none claimed; this record makes no acceptance claim, so it discloses unverified limitations rather than residuals
- Unverified limitations: see the list below

## Evaluated Combination

| Element | Value |
| --- | --- |
| Host | Claude Code |
| Host version | 2.1.220 |
| Model | claude-opus-5 (Opus 5, 1M context) |
| Skill loading mode | not loaded |
| Execution environment | local CLI session; PowerShell 5.1 and Git Bash; CPython 3.13.13 invoked through the `py -3.13` launcher because the default `python` on PATH is GraalPy 3.12.8 |
| Operating system | Windows 11 Home China, 10.0.26200 |
| Repository | `https://github.com/tutict/LoopPilot.git`, branch `main`, HEAD `882df4968e8862835e93fe5fdd4d28690565ed4d` |
| Scenario ID | `tests/scenarios.md` scenario 43 |

## Prompt Boundary

Recorded in [`EVAL-001/prompt.md`](EVAL-001/prompt.md). Supplied to the Agent:
the repository working tree, the operator's acceptance instruction, shell and
file tools, and the session's own context. Not supplied: any installed
`loop-pilot` Skill, any `CLAUDE.md`, any second evaluator, any prior Host
Acceptance Record, and any network access. No hidden expected answer was added
beyond the fixture text already present in the repository.

## Observed Trace

Recorded in [`EVAL-001/trace.md`](EVAL-001/trace.md). In summary, the host was
asked to operate under a `loop-pilot` Skill, could not confirm one in either
documented scope, recorded it as unavailable, and did not fabricate, install, or
substitute it. It continued on base-host capability for the parts of the
instruction that do not depend on the Skill and blocked the parts that do.

## Observed Deviations

None from the fixture. Scenario 43's expected behavior was observed in full and
no listed failure signal fired. No behavior contradicting a LoopPilot claim was
observed, and `README.md` already directs users to expose `SKILL.md` through the
host's own mechanism rather than claiming automatic loading.

The material deviation is from the **acceptance procedure**, not from the host:
the LoopPilot-loaded arm required by every acceptance dimension could not be
run, and no independent reviewer was available.

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

Every dimension is `not-evaluated` because the protocol was never loaded into
the host, so no dimension has preserved evidence of protocol behavior. No
dimension is `fail`: nothing observed shows a protocol-relevant behavior this
host cannot deliver. Base-host behavior was scored separately in
[`EVAL-001/score.md`](EVAL-001/score.md) and is deliberately not promoted into
this table.

## Evidence Links

- [`EVAL-001/environment.md`](EVAL-001/environment.md) — host surface, captured
  and re-verified by direct command output
- [`EVAL-001/prompt.md`](EVAL-001/prompt.md) — prompt and input boundary
- [`EVAL-001/trace.md`](EVAL-001/trace.md) — observed trace
- [`EVAL-001/score.md`](EVAL-001/score.md) — rubric scores, self-scored and
  unreviewed
- [`EVAL-001/reviewer-report.md`](EVAL-001/reviewer-report.md) — Spec, Standards,
  and Evidence review, explicitly not independent

## Reviewer Decision

`not-reviewed`. No evaluator independent of the trace author was available, so
no acceptance verdict can be certified. Recording `unverified` is the required
outcome, not a weaker form of acceptance.

## Unverified Limitations

- Every one of the eight acceptance dimensions. None was evaluated.
- Whether Claude Code loads and activates LoopPilot at all when `SKILL.md` is
  installed through the host's documented Skill mechanism.
- Whether the host selects a proportionate mode, respects the protocol's
  authority and stopping rules, handles `.looppilot/` shared state, uses Full
  Loop artifacts as authority, resumes from a Checkpoint, or labels lifecycle
  projections.
- Any fixture other than scenario 43, including every Lightweight-shaped and
  Full-Loop-shaped scenario that an acceptance verdict requires.
- Any other host version, model, or Skill loading mode. This record covers
  exactly Claude Code 2.1.220 with claude-opus-5 and no loaded Skill, and never
  generalizes to a later version, another model, another loading mode, or hosts
  as a class.
- Whether the self-scored rubric results in `EVAL-001/score.md` survive
  independent review.
- Production reliability, longitudinal behavior, release, and deployment.

## Scope

Apply [`docs/cross-host-acceptance.md`](../../docs/cross-host-acceptance.md).
The verdict is scoped to this exact host, host version, model, and loading mode.
Observed evidence lives in the referenced evaluation run; this record summarizes
and does not replace it.

This record does not satisfy the Release Candidate condition that the reference
host hold an observed `accepted` or `accepted-with-residuals` record. That gate
remains unmet.
