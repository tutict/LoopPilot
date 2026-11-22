# RC Candidate Reference Designation — v1.0.0-rc3

- RC version: v1.0.0-rc3
- Successor ID: OPTION-B-REFERENCE-2026-10-24
- Successor policy: docs/release/option-b-reference-successor.md
- Policy version: option-b-successor-v1
- Reference designation ID: RC3-REF-CODEX-20261122
- Reference Host: Codex
- Other eligible Host: Claude Code
- Other Host role: Candidate Host, unverified disclosure retained
- Designation state: preflight-designation
- Designation date: 2026-11-22
- Finalized at: unknown
- Formal acceptance arms at designation: none
- Reference host version: unknown
- Model identity: unknown
- Provider identity: unknown
- Endpoint identity: unknown
- Configured model: gpt-6.1-sol
- Configured provider: custom
- Configured endpoint: https://api.hanbbq.top/v1
- Skill loading mode: unknown
- RC baseline commit: pending-before-formal-run
- RC baseline tree: pending-before-formal-run

Proposed product commit: 40f85debf7b59072cdd3b9a4fb446540299c0f36; proposed product tree: 799342167f450379908937b703a3a9fbac1f6f38.

The latest user accepted the reviewed Checkpoint candidate and authorized its
application, synchronized installation, necessary local commits, and a new RC
four-arm rerun. This preflight choice selects the existing Codex execution surface
for RC3 and is recorded before preparation and any formal arm. It is not a final
designation, Host Acceptance, release readiness or publication authority.

The product baseline contains the accepted eight-file candidate and the separately
reviewed pre-existing RC1 fixture isolation correction. All eight canonical source
hashes match the reviewed candidate; the official USER installation is synchronized.
The runtime remains dependency-free for Skill users; maintenance Python and
capture helpers are not part of the installed runtime.

## Identity and preparation boundary

The operator directly observed the configured relay at GET /v1/models and
POST /v1/responses, both HTTP 200. The relay asserted gpt-6.1-sol. Its response
reported 4,226 input tokens, including 4,216 instructions-context tokens, and five
output tokens. Upstream provider/model remain UNVERIFIED; this anomaly and the
prior suspected injected context must accompany interpretation.

The new independent Reviewer uses a distinct agent context and operator role under
the same human account and filesystem. Blinding is best effort. Fresh raw input
pins, relay-identity disposition, runtime/permissions/loading and fixture
observations must be confirmed before finalization and formal execution.

The new scope is exactly LW-1, FL-1, FL-1R and IMP-1. Prior replication captures,
loading confounds, original RC2 results and its not-run FL-1R remain unchanged.
The new four-arm plan is not an eighteen-arm replication report.

## RC2 preservation

RC2's finalized reference and decision remain at Git boundary
74030c203722aa3aa4f48025632bbb323b82174d. Their exact working and committed bytes
were separately preserved before this forward-only RC3 designation. Existing
historical packages, verdicts and review judgments are not reinterpreted.
