# RC3 formal execution evidence — 2026-11-23

RC3 used the product commit `40f85debf7b59072cdd3b9a4fb446540299c0f36`
and tree `799342167f450379908937b703a3a9fbac1f6f38`. The [Reference designation](rc-candidate-reference.md)
was finalized at `2026-11-23T11:28:47+08:00` and committed as `3b117ad08331b8b692481afe5d4a8c80ddcc8eeb`
before the first formal session. The initialization used four independently
confirmed input pins. The three native seed fixtures each had 84 managed files,
`CURRENT` installation, `C2_CLEAN`, passing source readability, and six observed
external-read denials. The preparation receipt SHA-256 is
`bc9321d4aefcbb77b91ff5e3e869df01450b1f0bbd08073bdab22ff405d722bd`.

## Runs

| Arm and evaluation | Scenario | Observed execution | Independent packet review |
| --- | --- | --- | --- |
| FL-1 / EVAL-039 | 69 | Explicit input, Skill body observed, 6 native tests passed, stage 3 deferred, root Checkpoint preserved | Package decision `reject`. Spec failed because the first stage commit included both implementations. The other three axes passed. |
| FL-1R / EVAL-040 | 53 | Explicit input, Skill body observed, 8 native tests passed, stage 3 completed in a fresh session | All four axes passed. Package decision `accept-with-residuals`. |
| LW-1 / EVAL-038 | 68 | Explicit input, Skill body observed, 6 native tests passed, test file unchanged | All four axes passed. Package decision `accept-with-residuals`. |
| IMP-1 / EVAL-041 | Named implicit-activation fixture | Input omitted invocation, agent read the Skill using a tool, 9 native tests passed | All four axes passed. Package decision `accept-with-residuals`. |

Capture verification matched the exact prompts, individual public capture hashes,
predecessor bytes, and native test result receipts. The selected configuration was
restored. All 4,840 preserved historical capture files matched their original hashes.
The four sessions are scoped to RC3. Historical experiments remain separately recorded.

## Recovery

FL-1R consumed the root Checkpoint produced by FL-1. Both preserved copies share
SHA-256 `7d2cca9f6e47e8c69e4ece6aa38bbb43df2d493c2f0b931764752cc4ad057547`.
The initial resume invocation stopped before making a model request. The controller
classified an authority reminder in a patch as an operation attempt. The operator
rechecked the original byte-pinned capture, Git state and actual command inventory.
A scoped resume verifier checked the predecessor and existing launch gates, and
FL-1R ran once. The original controller observation and the recheck are preserved.
The later Spec finding concerns the original FL-1 stage ordering.

## Review and trust

TASK-005 independently approved the scoped controller repair. TASK-006 independently
verified the preparation and designation boundary. TASK-010 recorded blind packet
judgments. TASK-011 completed the numeric core scores and fixed the condition
guesses before the Reviewer acknowledged the reveal. The operator and reviewer
contexts share one human account and filesystem. Packet task content may suggest
the condition. The scoring Reviewer replaced the pre-run readiness Reviewer. The
initial packet exporter altered code escapes and omitted
untracked source. Those packets and their reviews are retained as superseded evidence.
The current packets were rebuilt from the captures and include the result files.

The pre-run relay probe reported `gpt-6.1-sol` and 4,216 instructions-context tokens.
Per-run host metadata records the configured alias and provider label. Upstream
provider and model and per-arm relay response identity remain unverified.

The [Host Acceptance Record](../../evaluations/codex/host-acceptance-record-rc3.md)
records `unverified`. Gate 4 remains unmet. The operator's independent raw pin for
the final package index and qualifying current formal evidence are pending. The
private experiment store retains the captures, review material, and digest inventory.

Mechanical checks passed for the four staged v2 run/v4 review packages and their
collective checkpoint lineage. The evidence-index candidate SHA-256 is
`39be66e9579e747714a0fd82f33129bc998342e246a15127b5ec153ac7463f76`.
It awaits independent operator approval. The lowest critical rubric score was
`1` for FL-1's evidence integrity across agents. The 11-dimension score totals
were FL-1 26/33, FL-1R 31/33, LW-1 30/33, and IMP-1 29/33.
