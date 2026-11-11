# Historical Evaluation v2 Re-run Runbook

This runbook turns the gaps in EVAL-001 through EVAL-005 into a new, auditable
experiment. It does not rewrite, rescore, or promote a historical package. The
historical package remains the source of its original bytes and hash; the v2
package is a separate observation linked through
`evidence/historical-lineage.json`.

The repository provides the audit and validation boundary. An operator with the
original Host, version, model, credentials, tools, and loading surface must run
the 14 arms in [`historical-replay-matrix.json`](historical-replay-matrix.json).
If the original combination cannot be started, stop that arm and record
`reproduction_status: not-reproduced`; do not substitute another Host version,
model, or loading mode.

## Before an arm

1. Run the read-only history audit:

   ```text
   python scripts/historical_evaluation_audit.py --root . --output .tmp/historical-audit-report.json
   ```

   A clean audit must report 31 pinned files, 31 matching files, no missing or
   mismatched files, and five historical packages. The report is evidence about
   preservation and package gaps only; it is not Host Acceptance.

2. Select one matrix pair and one arm. Keep the historical Host, Host version,
   model, commit boundary, scenario, permissions, tools, and fixture fixed.
   The control and Skill-loaded arms may differ only in the loading condition.

3. Start a fresh context for every arm. Do not pass the other arm's transcript,
   score, prompt hints, or evaluator interpretation into the context. Write the
   exact prompt before execution and verify it against the first public input
   event after the run.

4. Use a new Evaluation ID and run ID. A retry is a new package and a new run
   ID, with `attempt` 2 or 3 and `retry_of` naming the immediately preceding
   failed run. A retry is permitted only for an Execution Infrastructure
   Incident: HTTP 429, timeout, or host unavailability. At most two retries are
   allowed; preserve every failed package.

## Package contents

Each completed or failed arm is a self-contained package with:

```text
environment.md
prompt.md
trace.md
score.md
run.json
review.json
evidence/
  scenario.json
  events.jsonl
  code-quality-applicability.json
  historical-lineage.json
  <raw public artifacts>
```

`run.json` and `review.json` are approved through an operator index stored
outside the repository. The index is independently pinned by its raw SHA-256;
the package must not contain a substitute index.

`historical-lineage.json` uses schema version 1 and records the matrix pair,
historical Evaluation ID, exact Scenario ID and shape, `control` or
`skill_loaded` arm, original Host/version/model combination, replay reason,
known historical gaps, attempt and retry relation, and whether the original
combination was reproduced. It is a public observation event and is included in
the run evidence map.

`review.json` uses schema version 3 for replay packages. It retains the normal
run binding and disclosures and adds four required Review axes:

- `Spec` and `Standards`, always applicable;
- `Implementation Quality`, applicable when the run produces a reviewable
  deliverable and otherwise N/A with scope evidence; and
- `Verification & Evidence`, applicable when the run has a verification or
  evidence obligation and otherwise N/A with scope evidence.

Every applicable axis must be `pass` for an accepting review. A failed axis
requires a `reject` review decision. The declaration includes separate operator
and session identities for the trace author and reviewer. The mechanical check
enforces the declared separation; it cannot prove organizational independence.

## Code quality and failures

Use score schema version 2. When the run preserves code artifacts, score Code
quality. Record `not-applicable` only when the reviewed applicability inventory
contains no code artifacts. The row remains outside the applicable count and
total in that case. Code quality is not a Host Acceptance critical dimension.

An HTTP 429, timeout, or unavailable Host is an Execution Infrastructure
Incident. Preserve the error envelope, actual exit code, and limitations. Do not
record it as a product failure, do not claim success, and do not create a score
from an incomplete trace. A failed run may be mechanically valid evidence but
is never acceptance-eligible.

## Pair and acceptance checks

After each package is assembled, run the normal validator with the external
operator index. The validator checks lineage, exact Scenario/Host/version/model/
commit/loading identity, evidence event anchors, Code quality applicability,
four-axis Review structure, and reviewer identity declarations.

Before a new Host Acceptance summary is considered, all 14 matrix arms must have
complete packages or explicit failed/not-reproduced evidence. A missing required
arm leaves the experiment `unverified` or `blocked`. Historical packages remain
outside the new index and cannot satisfy the gate.

The repository does not execute Claude Code re-runs. The final experiment report
must state which arms were actually observed, which were blocked by
infrastructure, and which conclusions are limited to loading evidence. A
descriptive comparison must not claim a LoopPilot effect when the matched arms
are incomplete or the observed difference is unstable.
