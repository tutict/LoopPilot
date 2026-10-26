# Final RC Decision

- Phase: 12 final Release Candidate preparation
- Date: 2026-08-06
- Observed repository boundary: `aacbde449a6dbc8723d5c866033ac195017a90e5`
- Proposed candidate: `v1.0.0-rc1`
- Scope: final RC decision only; no protocol redesign, no new experiment, no new
  architecture, no lifecycle expansion, and no protocol concept added
- Evidence rule: gate and Finding classifications use committed evidence only
- Release recommendation: NOT READY FOR RC

## Decision Summary

LoopPilot should not become `v1.0.0-rc1` at this boundary. The protocol remains
frozen and the repository structure validates, but release acceptance remains
blocked by the absence of an accepted reference-host Host Acceptance Record, the
absence of independent Host Acceptance review, unresolved RC-blocking evidence
Findings, no candidate version section, and no RC-candidate-boundary validation
evidence.

This file records the Phase 12 working-tree decision. Committing it records the
audit and metadata correction only; it does not authorize or perform a tag,
release, deployment, or publication. A future RC candidate boundary still needs
its own validation evidence.

## Current RC Gates

| Gate | Status | Committed evidence basis |
| --- | --- | --- |
| `validate.py` passes at the RC boundary | UNVERIFIED | The committed RC checklist records Phase 11-A validation only, not an RC-boundary pass. Phase 12 validation was observed in this worktree and is recorded below, but it is not evidence for a future RC candidate commit boundary. |
| Full regression passes at the RC boundary | UNVERIFIED | The committed RC checklist records Phase 11-A regression only, not an RC-boundary pass. Phase 12 regression was observed in this worktree and is recorded below, but it is not evidence for a future RC candidate commit boundary. |
| Phase 11 independent review completed | BLOCKED | The committed RC checklist states no preserved independent review record exists. |
| Reference host has accepted Host Acceptance Record | BLOCKED | The committed Claude Code 2.1.220 record has verdict `unverified`; no committed `accepted` or `accepted-with-residuals` reference-host record exists. |
| Candidate hosts explicitly marked verified/unverified | READY | The committed README limitations list Claude Code, Codex, Gemini CLI, GitHub Copilot, and every other host as unverified. |
| No unresolved Major/Critical Finding | BLOCKED | The committed RC checklist records P11A-4 as a major RC blocker, and EVAL-001 records EV-1 and EV-2 as major blocking findings for host acceptance. |
| CHANGELOG contains candidate version section | BLOCKED | `CHANGELOG.md` has only `Unreleased`; no `v1.0.0-rc1` candidate section exists. |

No RC gate is `NOT APPLICABLE`.

## Host Acceptance

Status: UNVERIFIED.

Committed evidence shows Claude Code Host Acceptance cannot be completed as
accepted at this boundary:

- `evaluations/claude-code/host-acceptance-record-claude-code-2.1.220.md` is a
  committed Host Acceptance Record, but its verdict is `unverified`.
- The committed 2.1.220 record states the Skill was not loaded, all eight
  dimensions were `not-evaluated`, the lowest critical rubric score was not
  established, and no independent reviewer was obtainable.
- `evaluations/claude-code/EVAL-001/reviewer-report.md` states the review is not
  independent and identifies EV-1 and EV-2 as major findings blocking acceptance.
- The working-tree Claude Code 2.1.221 package remains uncommitted and lacks
  preserved `trace.md` and `score.md` for EVAL-002 and EVAL-003, so it cannot
  satisfy Host Acceptance.

Host Acceptance stays UNVERIFIED rather than being fabricated as ACCEPTED.

## Release Metadata

Phase 12 prepared stale-wording corrections only:

- `README.md` now distinguishes no accepted Host Acceptance Record from no Host
  Acceptance Record at all.
- `evaluations/claude-code/README.md` now acknowledges the committed 2.1.220
  unverified record while preserving unverified Claude Code status.
- `docs/release/v1.0-rc-checklist.md` now distinguishes no accepted or
  accepted-with-residuals record from no record at all.
- `docs/full-loop-migration-plan.md` now refers to no observed accepted Host
  Acceptance Record.
- `CHANGELOG.md` now says no gate is ticked, rather than no gate is satisfied,
  and records the stale-wording correction.

No candidate version section was added because the RC gates remain blocked. No
known limitation was weakened, and no migration rule was changed.

## Remaining Findings

Classifications below use committed evidence only.

| Finding | Status | Basis |
| --- | --- | --- |
| P11A-1 | Historical | Migration guidance exists in `docs/v1-migration.md`; the finding documents a Phase 11 compatibility behavior change, not a current RC acceptance blocker. |
| P11A-2 | Accepted residual | Section-level derived-status disclosure was retained to avoid schema change inside the feature freeze. No committed evidence marks it as RC-blocking. |
| P11A-3 | Accepted residual | The undeclared-copy check deliberately covers `.looppilot/` supporting artifacts only. No committed evidence marks it as RC-blocking. |
| P11A-4 | Blocking | The RC checklist explicitly states this major finding must be resolved or consciously accepted before the Release Candidate. No committed resolution or authorized acceptance exists. |
| P11A-5 | Blocking | The no-unresolved-Major/Critical gate still lacks a committed independent review evidence source, so the gate cannot be satisfied by absence. |
| P11A-6 | Accepted residual | Stable scenario IDs were out of scope for the governance-only change; no committed evidence marks this as RC-blocking. |
| STD-1 | Resolved | Phase 12 corrects the stale Claude Code README wording while preserving unverified acceptance status. |
| STD-2 | Historical | The committed EVAL-001 report says the RC checklist row remains accurate because the required evidence is an accepted or accepted-with-residuals record. |
| EV-1 | Blocking | The committed EVAL-001 report states the LoopPilot-loaded arm was never run and all eight acceptance dimensions are `not-evaluated`. |
| EV-2 | Blocking | The committed EVAL-001 report states no independent reviewer exists, so no dimension result can be certified. |
| EV-3 | Historical | The committed EVAL-001 report discloses a transient half-written-file validation failure and identifies the clean rerun as authoritative. |
| EV-4 | Historical | The committed EVAL-001 report records one narrow unavailable-Skill fixture observation without claiming protocol conformance. |

Phase 11-B findings from `RC-READINESS-REPORT.md` and untracked
EVAL-002/EVAL-003 package files align with the NOT READY decision. They cannot
satisfy or close an RC gate without committed traces, scores, and independent
review where required.

## Repository Validation

Observed in this Phase 12 worktree:

| Command | Result | Evidence boundary |
| --- | --- | --- |
| `git rev-parse HEAD` | `aacbde449a6dbc8723d5c866033ac195017a90e5` | Observed before edits. |
| `py -3.13 scripts\validate.py` | passed: `Static validation passed` | Phase 12 worktree evidence; not a future RC candidate-boundary pass. |
| `py -3.13 -m unittest discover -s tests -p "test_*.py" -q` | passed: 858 tests in 413.302s | Phase 12 worktree evidence; run required escalated temp-fixture write permission and is not a future RC candidate-boundary pass. |
| `git diff --check` | passed: exit 0 | Phase 12 worktree evidence; Git emitted line-ending normalization warnings for edited Markdown files. |

The validators are repository-structure checks. Per `docs/validation.md`, they do
not execute a host, score traces, verify reviewer independence, or prove host
compatibility.

## Release Recommendation

NOT READY FOR RC.

The next highest-value action is to obtain an independent reviewer and a complete
reference-host Host Acceptance package with preserved traces and scores, then
commit the accepted or accepted-with-residuals record together with release-boundary
validation evidence and a candidate CHANGELOG section. If that cannot be done,
LoopPilot must remain below `v1.0.0-rc1`.
