# Evaluation Preparation

This directory prepares reproducible LoopPilot host evaluations. It contains no
evaluation results and makes no compatibility claim.

For each run, copy the templates and record:

- Host and Host version;
- Model;
- LoopPilot version or commit;
- Skill loading mode;
- Scenario ID and task fixture;
- exact prompt and input boundary;
- observable trace and evidence links;
- observed outcome;
- rubric score;
- code quality applicability and its evidence, using score schema version 2;
- reviewer decision; and
- evaluator notes and unverified limitations.

A run whose Scenario ID, evidence links, reviewer decision, or unverified
limitations are missing is an incomplete evaluation, not a weaker result. Report
it as incomplete rather than scoring around the gap.

Evaluators MUST keep observations separate from interpretation and preserve
user-visible and tool-visible evidence. They MUST NOT request or record private
chain-of-thought and MUST score each observed trace with [`tests/evaluation-rubric.md`](../tests/evaluation-rubric.md).

For an A/B comparison, evaluators SHOULD keep the task fixture, host, model, authority,
and available tools constant. They SHOULD change only whether and how LoopPilot is
loaded and MUST report both runs even when either run fails.

Score schema version 2 adds one global Code quality dimension. Score it when the
run preserves code artifacts; otherwise record `not-applicable` only when the
independent review confirms the run contains no code artifact. The dimension is
excluded from the applicable count and total when not applicable. It is not one of
the four critical dimensions and does not change Host Acceptance Record rows.

## Current Evidence Validation Boundary

New packages follow the [evidence integrity contract](../docs/evaluation-evidence-integrity.md).
Presence, values, cross-artifact links, raw evidence hashes and corresponding approved
run/review receipts are checked under an explicit operator-pinned index outside the
repository. The validator cannot turn self-authored hashes into observed evidence.
Pinned historical packages remain immutable, unverified and ineligible for new
accepted summaries; they are not silently upgraded to the current schema.

The read-only [historical audit](../docs/evaluations/historical-evaluation-audit.md)
and [v2 re-run runbook](../docs/evaluations/historical-v2-rerun-runbook.md)
cover the missing control arms, incomplete traces/scores, infrastructure
incidents, and independent four-axis review for EVAL-001 through EVAL-005. The
14-arm plan in
[`historical-replay-matrix.json`](../docs/evaluations/historical-replay-matrix.json)
is bound to the original Claude Code combinations. If that Host is unavailable,
those runs remain `not-reproduced`; the repository does not execute Claude Code
arms and Codex evidence must not be substituted into the historical matrix.

The separate
[`codex-replication-matrix.json`](../docs/evaluations/codex-replication-matrix.json)
defines fourteen new Codex scenario-replication arms, followed by the four
current formal arms. These results are reported as Codex-only comparisons; they
do not reproduce the Claude runs or establish cross-host equivalence. Follow
the [Codex replication runbook](../docs/evaluations/codex-replication-runbook.md)
for its distinct lineage, runtime identity, Reviewer, index-authority, and final
operator-approved evidence-index gates.

## Two-stage Codex replacement experiment

The separate replacement study has seven matched Codex scenario-replication pairs
(fourteen runs), followed by the four current formal arms. The five behavior
pairs are descriptive Codex-only comparisons. This eighteen-run study is distinct from RC3's declared four-arm rerun and does not
expand that candidate's scope. Two loading probes preserve a
`loaded`, `not-loaded`, or `not-observed` receipt and do not contribute
behavioral rubric scores. A 429, timeout, or unavailable Host remains an
Execution Infrastructure Incident and cannot satisfy an arm. The Claude
historical replay section remains `not-reproduced` when its original Host is
unavailable; Codex runs never count as Claude replay.

Follow the detailed
[Codex replication runbook](../docs/evaluations/codex-replication-runbook.md)
for the new matrix, separate lineage, pre-run authority receipt, packet export,
and final approved-index sequence. The older
[two-stage behavior validation runbook](../docs/evaluations/two-stage-behavior-validation-runbook.md)
retains the historical Claude boundary and the four formal-arm requirements.

The formal current stage has four loaded arms: `LW-1`, `FL-1`, `FL-1R`, and
`IMP-1`; `FL-1R` uses the checkpoint from `FL-1`. For the replacement
experiment, create and pin both a fresh Reviewer readiness receipt and the
pre-run evidence-index authority receipt before generating the randomized plan:

```text
python scripts/behavior_validation.py prepare-codex-replication-blind --experiment-id <id> \
  --reviewer-gate <external/reviewer-readiness.json> \
  --reviewer-gate-sha256 <receipt-sha256> \
  --index-authority <external/evidence-index-authority.json> \
  --index-authority-sha256 <authority-sha256> \
  --output <external/codex-blind-plan.json>
```

Each current package uses a v4 Review receipt with the blind packet hash and
timestamps for Review completion, condition guess, and unblinding. The guess must
precede reveal. The report command validates packages under the external operator
index, separates loading probes from behavior results, and never creates a Host
Acceptance verdict.

Export a de-identified public-evidence packet for the independent Reviewer with:

```text
python scripts/behavior_validation.py export-blind --package <repo/evaluations/...> \
  --blind-review-id <blind-id> --output <external/reviewer-packet>
```

```text
python scripts/behavior_validation.py report-codex-replication \
  --blind-plan <external/codex-blind-plan.json> \
  --blind-plan-sha256 <plan-sha256> \
  --reviewer-gate <external/reviewer-readiness.json> \
  --reviewer-gate-sha256 <receipt-sha256> \
  --index-authority <external/evidence-index-authority.json> \
  --index-authority-sha256 <authority-sha256> \
  --evidence-index <authority-pinned/approved-index.json> \
  --evidence-index-sha256 <final-index-sha256> \
  --output <external/codex-replication-report.json>
```
