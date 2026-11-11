# Two-stage behavior validation runbook

## Status and decision boundary

This is an execution plan, not run evidence. No Host boundary, run, score, or
independent Reviewer assignment is asserted by this document. The operator must
record observed values and stop a stage when a required gate is unavailable.

The design contains 18 primary runs: fourteen historical replay arms and four
current formal arms. Each arm gets one primary run. A recorded Execution
Infrastructure Incident may receive at most two new-ID retries. A retry never
replaces or deletes the failed package.

## Gate before scoring

1. Secure an independent Reviewer who is not the run operator and can review
   de-identified evidence before learning arm assignments. Save an external
   `behavior-reviewer-readiness` receipt with experiment ID, operator and
   Reviewer operator/session IDs, distinct operator and Reviewer sessions,
   confirmation time, and scope. Hash the exact bytes and keep both receipt and
   pin outside the repository.
2. Generate the blind plan only after that receipt exists:

   ```text
   python scripts/behavior_validation.py prepare-blind --experiment-id <id> \
     --reviewer-gate <external/reviewer-readiness.json> \
     --reviewer-gate-sha256 <sha256> --output <external/blind-plan.json>
   ```

   Record the printed raw blind-plan SHA-256 in the external operator store.
   Keep the plan and mapping sidecar outside the repository; do not give either
   to the Reviewer before scoring and the condition guess are fixed.
3. For the current formal stage, re-observe the exact Host, Host version, Model,
   provider/endpoint, Skill digest and install provenance, commit/tree, tools,
   permissions, and isolated fixture root. Require `CURRENT`, `C2_CLEAN`, and a
   passing permission preflight. A stale or inaccessible combination blocks the
   current stage; do not substitute a different Host or version.

## Historical replay stage

Use [`historical-replay-matrix.json`](historical-replay-matrix.json) without
changing its Host/version/Model/loading-mode combinations. Run all seven matched
pairs with the randomized within-pair order in the blind plan. The control and
loaded arms share input, fixture, permissions, tools, and commit; only Skill
loading changes. Each arm uses an independent context.

Five pairs are behavior comparisons. The two EVAL-004 pairs are loading probes
and must preserve `evidence/loading-observation.json` with `loaded`, `not-loaded`,
or `not-observed`. Do not assign a behavioral rubric score to a loading probe.
Report its loading result separately from behavior. A failed probe does not count
as a successful behavior run.

If the original combination cannot be reproduced, preserve the attempt and mark
the lineage `not-reproduced` with evidence and a reason. Never substitute a newer
combination. HTTP 429, timeout, and unavailable-host events remain EII and do not
become product failures or successful observations.

## Current formal stage

Run `LW-1` (Scenario 68), `FL-1` (Scenario 69), `FL-1R` (Scenario 53), and
`IMP-1` (the named implicit-activation code fixture) using the matrix prompts and
coverage. These are all Skill-loaded arms; do not add a control arm. Run FL-1
before FL-1R. FL-1 must preserve its Checkpoint; FL-1R starts in a fresh context,
records the FL-1 run ID and checkpoint path/hash, and revalidates current reality.
Do not carry the previous conversation context into FL-1R.

Use one freshly observed current boundary across the four arms. Each package
registers `evidence/current-validation-boundary.json` and
`evidence/current-acceptance-lineage.json` as public trace observations. Every
run must bind the same Host/version/Model/commit/tree, Skill digest, tools,
permission mode, C2 status, install provenance, and fixture isolation boundary.

## Blind packet and four-axis Review

After preserving public run evidence, export each packet outside the repository:

```text
python scripts/behavior_validation.py export-blind --package <evaluations/<host>/<id>> \
  --blind-review-id <blind-id> --output <external/reviewer-packet>
```

The exporter verifies raw run evidence hashes, removes lineage and boundary
metadata, redacts standard identity fields, preserves the public task/evidence,
and emits a blank rubric sheet plus a source/hash manifest. Task or trace content
may still reveal the arm; never promise perfect blinding. Copy the exact
`blind-review-packet.md` bytes into the package at
`evidence/blind-review-packet.md`, register and hash it, then submit only that
packet and its blind ID to the Reviewer.

The Reviewer scores the evidence and completes all four axes: Spec, Standards,
Implementation Quality, and Verification & Evidence. Each axis is applicable for
these selected code-delivery scenarios. The Reviewer records a condition guess
and confidence after scoring but before unblinding, then records the reveal time.
`review.json` schema version 4 binds the packet hash and all timestamps. The
Reviewer operator and session must differ from the trace author/operator and
session. A self-review or missing receipt blocks the stage.

Code quality is scored when code artifacts are preserved. `not-applicable` is
valid only when the package evidence inventory proves there is no code artifact.
The code-quality score does not replace the existing four critical rubric
dimensions or any of the eight Host Acceptance dimensions.

## Validation and reporting

Keep the operator-approved index, reviewer-readiness receipt, blind plan, and
arm-to-blind-ID mapping outside the repository. Pin each file's raw SHA-256 in
the operator's trusted store. Validate packages and historical pins:

```text
python scripts/validate.py --root . --evidence-index <external/approved.json> \
  --evidence-index-sha256 <sha256>
python scripts/historical_evaluation_audit.py --root . --output <external/history-audit.json>
```

Produce the two-stage report only from a pinned plan, pinned reviewer gate, and
operator-approved run/review index:

```text
python scripts/behavior_validation.py report --blind-plan <external/blind-plan.json> \
  --blind-plan-sha256 <sha256> --reviewer-gate <external/reviewer-readiness.json> \
  --reviewer-gate-sha256 <sha256> --evidence-index <external/approved.json> \
  --evidence-index-sha256 <sha256> --output <external/behavior-report.json>
```

The report separates the five behavior pairs from the two loading probes and
lists current arms, eight-dimension coverage, per-run rubric scores, Code quality
applicability, Review decisions, condition guesses, EII, and missing runs. A
complete report is descriptive because there is one primary run per arm; it does
not calculate variance or claim a stable causal effect. A product behavior failure
is handled under the existing acceptance rules. An EII is neither product success
nor product failure.

Only the existing Host Acceptance Record, backed by all required run packages and
the existing eight-dimension and critical-score gates, can state Host Acceptance.
The behavior report never emits `accepted`; any missing required current arm leaves
the current stage `incomplete` or `blocked`.
