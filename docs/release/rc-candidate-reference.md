# RC Candidate Reference Designation — v1.0.0-rc3

- RC version: v1.0.0-rc3
- Successor ID: OPTION-B-REFERENCE-2026-10-24
- Successor policy: docs/release/option-b-reference-successor.md
- Policy version: option-b-successor-v1
- Reference designation ID: RC3-REF-CODEX-20261122
- Reference Host: Codex
- Other eligible Host: Claude Code
- Other Host role: Candidate Host, unverified disclosure retained
- Designation state: finalized-before-acceptance
- Designation date: 2026-11-22
- Finalized at: 2026-11-23T11:28:47+08:00
- Formal acceptance arms at designation: none
- Reference host version: codex-cli 0.168.0
- Model identity: gpt-6.1-sol (relay-asserted; upstream model UNVERIFIED)
- Provider identity: custom (configured; upstream provider UNVERIFIED)
- Endpoint identity: https://api.hanbbq.top/v1 (configured relay endpoint)
- Configured model: gpt-6.1-sol
- Configured provider: custom
- Configured endpoint: https://api.hanbbq.top/v1
- Skill loading mode: explicit, implicit
- RC baseline commit: 40f85debf7b59072cdd3b9a4fb446540299c0f36
- RC baseline tree: 799342167f450379908937b703a3a9fbac1f6f38

This designation fixes Codex as the RC3 Reference Host before any formal
acceptance arm. It binds the observed host version, relay-asserted model,
configured provider and endpoint, both declared loading modes, and the RC3
product baseline. Upstream provider/model identity remains UNVERIFIED.

The relay was freshly observed at GET /v1/models and POST /v1/responses, both
HTTP 200. The selected alias was listed, the response asserted gpt-6.1-sol,
and the response reported 4,226 input tokens including 4,216 instructions-context
tokens. The suspected extra input context remains disclosed and accepted for
this RC3 boundary.

The operator confirmed the four exact external input pins and accepted the
relay-identity and extra-context disclosures before this designation. The
independent Reviewer uses a distinct agent context and operator role under the
same human account and filesystem. Blinding is best effort. Upstream identity is
not promoted by that confirmation.

The formal scope is exactly LW-1, FL-1, FL-1R and IMP-1. Prior replication
captures, loading confounds, original RC2 results and its not-run FL-1R remain
unchanged. The new four-arm plan is not an eighteen-arm replication report.

## RC2 preservation

RC2's finalized reference and decision remain at Git boundary
74030c203722aa3aa4f48025632bbb323b82174d. Their exact working and committed bytes
were separately preserved before this forward-only RC3 designation. Existing
historical packages, verdicts and review judgments are not reinterpreted.
