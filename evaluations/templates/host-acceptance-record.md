# Host Acceptance Record

- Host:
- Host version:
- Model:
- LoopPilot commit:
- Skill loading mode:
- Evaluation IDs: none
- Scenario coverage: none
- Scenario IDs: none
- Trace author: none
- Independent reviewer: none
- Lowest critical rubric score: none
- Date:
- Verdict: unverified
- Residual limitations: none
- Unverified limitations: none
- RC version:
- Successor ID:
- Successor policy:
- Reference designation ID:
- Reference designation record:
- Reference Host:
- Reference designation SHA-256:
- Provider identity:
- Endpoint identity:
- RC evidence role:

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

Apply [`docs/cross-host-acceptance.md`](../../docs/cross-host-acceptance.md).
The verdict is scoped to this exact host, host version, model, and loading mode.
For an Option B RC, fill the RC binding fields and set `RC evidence role` to
`reference` or `candidate`. Only the designated Reference's qualified record may
support Gate 4. Non-RC records leave these optional fields empty; old records are
not retrofitted. See the [successor](../../docs/release/option-b-reference-successor.md).
Keep observed evidence in the referenced evaluation runs; this record summarizes
and does not replace them.

Copy this file to `evaluations/<host>/` and keep the `Host Acceptance Record`
title, optionally qualified with the evaluated combination. Record `Date` as
`YYYY-MM-DD` and `LoopPilot commit` as a bare 40-character lowercase hexadecimal
SHA. `Trace author` names who produced the traces and MUST differ from
`Independent reviewer`. `Lowest critical rubric score` is the smallest score
observed across the rubric's critical dimensions on any scored trace. A
dimension scored `pass` or `partial` MUST cite its evidence in the same row.

`Scenario IDs` lists the numbered scenarios in
[`tests/scenarios.md`](../../tests/scenarios.md) or the named fixtures the
referenced runs exercised, so a later reader can reproduce them. `Residual
limitations` names disclosed shortfalls under an `accepted-with-residuals`
verdict; `Unverified limitations` names what this record does not establish at
all, including every `not-evaluated` dimension, untested host versions, and the
fact that a verdict never generalizes beyond its exact evaluated combination.
The public validator enforces these record disclosures and, for accepted claims,
validates linked evaluation packages under an explicit operator-pinned evidence
index. See [evidence integrity](../../docs/evaluation-evidence-integrity.md).
A structurally valid template is not a completed run or an acceptance decision.

For an RC-bound accepted or accepted-with-residuals record, the Option B fields
must identify the active successor, the RC designation record, the designated
Reference Host, and observed provider/endpoint identity evidence. Older
unverified records may omit these fields and remain historical disclosures.
