# RC Candidate Decision — v1.0.0-rc2

- RC version: v1.0.0-rc2
- Successor ID: OPTION-B-REFERENCE-2026-10-24
- Reference designation record: docs/release/rc-candidate-reference.md
- Reference Host: Codex
- Decision state: candidate-prepared-not-release-ready
- Decision date: 2026-11-20
- Gate 4: unmet
- Gate 5: all-named-candidates-recorded-or-disclosed-unverified
- Acceptance status: not-run
- Host/model identity status: unverified
- Release tag: not-created

The operator selected commit `26f42eb9bfa368805b1fb58fd066ad651e5e7216` and tree
`0daf2c73da1913b207bb57f03196ad39a6cb317f` for RC2. The [designation](rc-candidate-reference.md)
records the Codex preflight choice. Claude Code remains an unverified Candidate
Host. The original Claude historical replay remains `not-reproduced`.

The selected baseline passed 1,280 maintenance tests across 36 modules, including
two module reruns after correcting their isolated test environment. The history
audit matched 31 of 31 pinned files. The operator's HB-1 binding covers the
USER-scope installation at this baseline, where the status was `CURRENT` and
installation isolation was `C2_CLEAN`.

Before running the [Codex experiment](../evaluations/codex-replication-runbook.md),
complete the RC2 runtime identity capture and finalize the designation. Review the
shared 18-arm boundary, verify exec-level C1 and fixture isolation, obtain the
independent Reviewer readiness receipt and operator index-authority receipt, and
pin the generated blind plan and mapping. Gate 4 remains open pending formal
Host Acceptance. The prior RC1 decision is preserved in Git at the selected
baseline commit above.
