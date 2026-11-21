# RC Candidate Reference Designation — v1.0.0-rc2

- RC version: v1.0.0-rc2
- Successor ID: OPTION-B-REFERENCE-2026-10-24
- Successor policy: docs/release/option-b-reference-successor.md
- Policy version: option-b-successor-v1
- Reference designation ID: RC2-REF-CODEX-20261120
- Reference Host: Codex
- Other eligible Host: Claude Code
- Other Host role: Candidate Host, unverified disclosure retained
- Designation state: finalized-before-acceptance
- Designation date: 2026-11-20
- Finalized at: 2026-11-21T18:26:11+08:00
- Formal acceptance arms at designation: none
- Reference host version: 0.168.0
- Model identity: gpt-6.1-sol
- Provider identity: api.hanbbq.top
- Endpoint identity: https://api.hanbbq.top/v1
- Configured model: gpt-6.1-sol
- Configured provider: custom
- Configured endpoint: https://api.hanbbq.top/v1
- Skill loading mode: explicit, implicit
- RC baseline commit: 26f42eb9bfa368805b1fb58fd066ad651e5e7216
- RC baseline tree: 0daf2c73da1913b207bb57f03196ad39a6cb317f

On November 20, 2026, the operator selected `26f42eb9bfa368805b1fb58fd066ad651e5e7216`
(tree `0daf2c73da1913b207bb57f03196ad39a6cb317f`) as the RC2 product baseline. The designation commit records
this finalized combination after the preparation observations and before any
formal arm, under the [Option B successor](option-b-reference-successor.md).
RC1 remains separately designated and unchanged.

## RC2 identity decision and disclosure

On November 21, 2026, the responsible party accepted the relay-asserted identity
layer for RC2 with continuing disclosure. This decision is specific to RC2 and
does not establish upstream identity. The operator-side runtime probe observed
GET `/v1/models` and POST `/v1/responses`, both HTTP 200. The selected runtime
was configured as provider `custom`, model `gpt-6.1-sol`, and endpoint
`https://api.hanbbq.top/v1`. The relay response asserted model `gpt-6.1-sol`.
The upstream provider and model remain **UNVERIFIED**. Every run and summary
must preserve the relay-asserted label and upstream-unverified disclosure.

The minimal POST returned 4,227 input tokens, including relay-injected
instructions context reported by the probe evidence, and 5 output tokens under
the requested limit of 16. The capture also flags suspected hidden input
context. Preserve these anomalies when interpreting results. Credential values
are excluded from this designation and its cited evidence.

## Preparation evidence

The USER-scope installation was re-observed at the selected baseline. Installer
status was `CURRENT`; 84 of 84 managed files matched installed and committed
bytes; C2 was `C2_CLEAN` with zero findings. HB-1 matched the bound installation
receipt. The operator rotated the relay credential and locally propagated the
replacement to `arm-home-p5fix`; the key revocation itself is operator-attested.

The selected `arm-home-p5fix` run completed C1 P1–P6 and fixture-isolation
verification with six passing probes and no credential leak in captured
rollouts. P1 targeted the main checkout README and preserved the inner
`UnauthorizedAccessException` with OS error 5. The tools digest was uniform
across the six probes, and the permission profile was `c1arm` under Windows
sandbox `mxc`.

The 18-arm plan and operator-only mapping are generated, validated, and pinned.
The independent Reviewer disclosed session-level independence under the same
human account as the operator, knowledge of the design, and best-effort
blinding. These limitations must accompany the resulting report.

## Finalization authority

The responsible party's RC2 decision accepts relay-asserted identity with
continuing disclosure. The local designation finalization commit and formal
18-arm start are separately authorized in the RC2 preparation conversation.
That run authorization does not create an acceptance verdict or release status.
