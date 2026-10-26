# LoopPilot Documentation Index

This is the source repository index. The official installation payload does not
include this index or `docs/archive/`; shipped READMEs use the explicit GitHub
source links below when a source-only document is needed.

## Current use

- [Installation and distribution guide](installation.md) — managed files, source
  verification, status, update, backup, and uninstall behavior.
- [Validation guide](validation.md) — repeatable maintenance checks and their
  evidence boundary.
- [Validate CI](https://github.com/tutict/LoopPilot/actions/workflows/validate.yml?query=branch%3Amain)
  — select the run for the relevant commit, then inspect its Ubuntu and Windows
  PowerShell 5.1/7 and macOS jobs and their named installation artifacts.
- [Host capabilities](host-capabilities.md) — capability levels and compatibility
  limits.
- [Safety and stopping](safety-and-stopping.md) — authorization and outcome rules.

## Protocol support

- [Mode selection and escalation](mode-selection-and-escalation.md) — the canonical
  ordered Product Risk, review-depth, Coordination Necessity, and mode sequence.
- [Coordination necessity and delegation fallback](coordination-necessity-and-delegation-fallback.md)
  — coordination criteria, deterministic cases, specialist-reviewed Lightweight,
  Worker failure budget, and ownership collapse.
- [Multi-Agent coordination](multi-agent-coordination.md) — Supervisor, Worker,
  Reviewer, and Integrator responsibilities, review, conflict, and integration.
- [Protocol modes and state sources](protocol-modes-and-state-sources.md) — mode
  boundaries and lifecycle authority.
- [Loop Engineering model](loop-engineering-model.md) — bounded Loop structure and
  inactive Full Loop target.
- [Full Loop delivery](full-loop-delivery-review-and-closure.md) and
  [recovery](full-loop-checkpoint-and-context-recovery.md) — delivery, review,
  rework, closure, Checkpoint, and resume contracts.

## Acceptance preparation

- [v1.0 RC checklist](release/v1.0-rc-checklist.md) — gates and required evidence.
- [RC candidate decision](release/rc-candidate-decision.md) — current candidate
  facts and status boundary.
- [RC maintenance verification](release/rc-maintenance-verification-20261025.md)
  — later packaging maintenance evidence, separate from formal acceptance.
- [Option B successor](release/option-b-reference-successor.md) — bounded Reference
  designation and successor rules.
- [Installation validation](../INSTALLATION-VALIDATION.md) — lifecycle scenarios
  and historical distribution observations.

## Historical archive

- [Archive index](archive/README.md) — original paths, moved paths, dates, Git
  boundaries, phases, and scopes for the five reports moved out of the repository
  root.
- [Release-readiness reports](archive/release-readiness/)
- [Distribution reports](archive/distribution/)

Historical reports preserve their original wording and conclusions. The archive
index supplies path mapping; it does not make historical observations current or
change any acceptance, Gate, or release decision.
