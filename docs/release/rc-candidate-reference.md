# RC Candidate Reference Designation — v1.0.0-rc2

- RC version: v1.0.0-rc2
- Successor ID: OPTION-B-REFERENCE-2026-10-24
- Successor policy: docs/release/option-b-reference-successor.md
- Policy version: option-b-successor-v1
- Reference designation ID: RC2-REF-CODEX-20261120
- Reference Host: Codex
- Other eligible Host: Claude Code
- Other Host role: Candidate Host, unverified disclosure retained
- Designation state: preflight-designation
- Designation date: 2026-11-20
- Finalized at: unknown
- Formal acceptance arms at designation: none
- Reference host version: unknown
- Model identity: unknown
- Provider identity: unknown
- Endpoint identity: unknown
- Configured model: unknown
- Configured provider: unknown
- Configured endpoint: unknown
- Skill loading mode: unknown
- RC baseline commit: pending-before-formal-run
- RC baseline tree: pending-before-formal-run

On November 20, 2026, the operator selected `26f42eb9bfa368805b1fb58fd066ad651e5e7216`
(tree `0daf2c73da1913b207bb57f03196ad39a6cb317f`) for RC2 preparation and authorized
this local designation commit and external review drafts. That commit is the
selected product baseline. The fields above will bind it to the observed Codex
combination at finalization, under the [Option B successor](option-b-reference-successor.md).
The previous RC1 designation remains available at commit
`4ea607676bd9bd18dc49a7aa853b845defbaa958`.

## Preparation evidence

The selected USER-scope installation reported `CURRENT`, with 84 managed files
verified against the selected commit. The installation tree reported `C2_CLEAN`
with zero findings. The operator independently recomputed HB-1 as
`b9d974eee3f63be8084b9403bb37e580626deffb8059d7614419a9d7d775d9c4`.
The trusted external store holds the receipt and binding record in
`install-boundary-26f42eb/`. Re-observe the installation and fixture boundaries
for the formal experiment.

RC2 finalization requires a fresh, operator-observed runtime combination for the
selected execution surface. The November 19 RC1 relay capture remains historical
preparation evidence with upstream identity unverified. The [Codex replication
runbook](../evaluations/codex-replication-runbook.md) establishes the planned
loading conditions and the shared boundary for the 18 primary runs. The RC2
[decision record](rc-candidate-decision.md) tracks the remaining pre-run checks.
