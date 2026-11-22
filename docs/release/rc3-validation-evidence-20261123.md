# RC3 Validation Evidence — v1.0.0-rc3

- Evidence update date: 2026-11-23
- Product baseline: `40f85debf7b59072cdd3b9a4fb446540299c0f36`
- Product tree: `799342167f450379908937b703a3a9fbac1f6f38`
- Validation scope: local repository maintenance and RC3 preparation evidence
- Host Acceptance: not established

## Completed candidate-boundary receipt

The completed RC3 maintenance receipt at
`.tmp/rc3-four-arms-20261122/tests-maintenance.json` records the following
commands against the candidate boundary on 2026-11-22.

| Check | Result |
|---|---|
| Full repository regression | Exit 0, 1,288 tests, no skips |
| Phase 4 Checkpoint recovery follow-up | Exit 0, 72 tests, no skips |
| Phase 5 Project closure follow-up | Exit 0, 134 tests, no skips |
| Phase 7 evaluation calibration follow-up | Exit 0, 89 tests, no skips |
| YAML and validation negative follow-up | Exit 0, 3 tests, no skips |
| Static validator | Exit 0, `Static validation passed` |
| Skill quick validation | Exit 0, `Skill is valid!` |
| Historical evaluation audit | Exit 0 |
| Mermaid rendering | 35 sources rendered to non-empty outputs |
| Historical raw pins | 31 of 31 matched |

The receipt reports no failed checks. Its eight source hashes match the current
RC3 product baseline. The focused RC3 controller repair regression independently
reported 17 tests and `OK` in the preserved TASK-005 evidence.

## Fresh verification on 2026-11-23

- `scripts/validate.py` exited 0 and reported `Static validation passed`.
- `scripts/option_b_validation.py` exited 0.
- The Skill quick validator exited 0 and reported `Skill is valid!`.
- The staged and unstaged Git diffs passed `git diff --check` and
  `git diff --cached --check`.
- Three lifecycle regression tests covering the observed full-suite anomalies
  exited 0 with `OK`.

A later full-suite rerun was interrupted before completion and is not counted as
new PASS evidence. Two sandboxed attempts also encountered Windows temporary
workspace permission errors. The completed 2026-11-22 receipt remains the
candidate-boundary regression evidence, and these execution-infrastructure
incidents remain disclosed separately from product findings.

## Review boundary

This document supplies the maintenance evidence requested by TASK-005. The
independent Reviewer still owns rechecking the receipt, current hashes, and the
four review axes. This evidence does not change the review decision, finalize the
RC3 designation, create a Host Acceptance Record, satisfy Gate 4, or authorize a
release.
