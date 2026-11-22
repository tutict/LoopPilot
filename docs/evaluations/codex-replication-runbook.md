# Codex Replication Runbook

This runbook defines a new Codex-only replication study. It does not replay or
replace the original Claude Code host/version/model combinations. The original
Claude historical replay status remains `not-reproduced` and the historical
packages remain unchanged.

The study has fourteen matched Codex replication arms across seven scenario
seeds, followed by the four current formal arms `LW-1`, `FL-1`, `FL-1R`, and
`IMP-1`. Reports keep the Codex replication section separate from both Claude
historical evidence and current Host Acceptance. Codex results do not establish
Claude behavior or cross-host equivalence. The RC3 release records define a separate
four-arm rerun. Those arms do not require the fourteen descriptive replication runs,
and results from that study cannot be relabelled as RC3 evidence.

## Claim boundary and evidence sections

Every replication package records the observed Codex runtime identity and the
shared current boundary. `source_evaluation_id` is provenance for the scenario
seed only. It does not assert that Codex reproduced the source host. The report
labels comparisons `Codex-only` and describes the seven matched pairs without
combining their scores with the Claude packages.

The report has three separate sections:

- `codex_replication`: seven pair states, five behavior comparisons, two
  loading-only observations, retries, and execution-infrastructure incidents.
- `historical_replay`: `not-reproduced`, with zero Codex packages counted as
  Claude historical runs.
- `current_acceptance`: four formal arms and their existing readiness gates.
  The report never creates a Host Acceptance verdict.

## Matrix and matched-pair controls

Use `codex-replication-matrix.json` and its exact prompt files. Do not edit the
Claude `historical-replay-matrix.json`. The control and Skill-loaded arms in each
pair use identical scenario input bytes, fixture, Codex boundary, permissions,
tools, and operator authority. Only the declared Skill-loading condition may
differ. Each arm gets a fresh Codex context and a new Evaluation ID from
`EVAL-020` through `EVAL-033`. Current formal IDs are reserved as `EVAL-034`
through `EVAL-037`.

The five behavior pairs are scored under the existing rubric. The two loading
probes remain unscored behaviorally and preserve
`evidence/loading-observation.json`. The Codex explicit surface is the observed
`$loop-pilot` Skill trigger. The Codex implicit surface must be observed in a
fresh context with no Skill name or invocation token in the task prompt. Record
`loaded`, `not-loaded`, or `not-observed` from the actual public tool/session
trace; model claims alone do not prove loading. If the runtime does not expose a
loading event or the surface cannot be reproduced, preserve the attempt and
record the probe as inconclusive/unavailable. Do not substitute Claude's
headless-discovery mode.

## Gates before the first run

1. Choose a new experiment ID. The prior reviewer receipt and blind plan are
   bound to a different ID and scope and do not authorize this experiment.
2. Obtain fresh independent Reviewer readiness for the new experiment and
   scope. Save the exact external receipt and independently pin its raw bytes.
3. The operator creates an external `codex-evidence-index-authority` receipt
   containing the experiment ID, operator ID, absolute final evidence-index
   path, and timezone-qualified approval time. Pin its raw bytes. The declared
   final index path must be outside the repository and contain no symlink or
   junction component.
4. Generate the separate plan and assignment sidecar:

   ```text
   python scripts/behavior_validation.py prepare-codex-replication-blind \
     --experiment-id <new-id> \
     --reviewer-gate <external/reviewer-readiness.json> \
     --reviewer-gate-sha256 <raw-receipt-sha256> \
     --index-authority <external/evidence-index-authority.json> \
     --index-authority-sha256 <raw-authority-sha256> \
     --output <external/codex-blind-plan.json>
   ```

   Independently pin the raw plan bytes and the complete mapping-sidecar bytes.
   Keep both files outside the repository and withhold all assignments from the
   Reviewer until scores and condition guesses are fixed. Pair members remain
   adjacent in randomized order; all seven pairs precede current arms, and
   `FL-1` precedes `FL-1R`.
5. Capture trusted upstream runtime identity outside Codex self-report. Finalize
   the Codex designation and verify one common `CURRENT` install, `C2_CLEAN`
   state, passing P1–P6 permission probes, tools digest, permission mode,
   commit/tree, Skill digest, and isolated fixture boundary. All eighteen arms
   must use that same observed boundary.
6. Record external index authority as fixed before runs; this pins the owner and
   destination only. It does not approve run packages that do not exist yet.

If any gate is absent, do not start a run.

## Run order, attempts, and packages

Run all seven pairs in the generated order, then the four formal arms. Preserve
exact prompt bytes and verify them against the first public input event. A run
package includes the normal artifacts, four-axis review, runtime identity,
current validation boundary, blind packet, and
`evidence/codex-replication-lineage.json` for replication arms. Replication
lineage binds source EVAL provenance, pair, arm, prompt digest, Codex loading
condition, observed boundary ID, attempt, retry, and blind ID. It contains no
Claude host identity.

For each loading probe, preserve a loading observation supported by the public
session trace. Do not award behavior rubric scores to those two probes. For
behavior runs, keep scenario/task bytes equal inside a pair. HTTP 429, timeout,
and unavailable-host events are execution-infrastructure incidents. At most
two new-ID retries are permitted for such incidents; retain every failed
attempt and never retry a product behavior failure.

Run `FL-1` before `FL-1R`. FL-1R starts in a fresh Codex context, binds the
observed FL-1 run ID and checkpoint path/hash, and revalidates the shared
boundary. Do not inherit conversation context or reconstruct a missing
checkpoint.

## Blind Review and final evidence index

Export one de-identified packet per reviewable package. The independent Reviewer
scores Spec, Standards, Implementation Quality, and Verification & Evidence;
each applicable axis needs evidence from that package. The Reviewer records a
condition guess and confidence before unblinding. Blinding is best-effort and
must not be described as perfect.

After run and Review artifacts exist, the operator creates the final approved
index at the authority-pinned path. It binds exact raw `run.json` and
`review.json` bytes and is independently pinned. The report command validates
both the earlier authority receipt and this final index; a fixed path alone
cannot satisfy package approval.

```text
python scripts/behavior_validation.py report-codex-replication \
  --blind-plan <external/codex-blind-plan.json> \
  --blind-plan-sha256 <raw-plan-sha256> \
  --reviewer-gate <external/reviewer-readiness.json> \
  --reviewer-gate-sha256 <raw-receipt-sha256> \
  --index-authority <external/evidence-index-authority.json> \
  --index-authority-sha256 <raw-authority-sha256> \
  --evidence-index <authority-pinned/approved-index.json> \
  --evidence-index-sha256 <raw-final-index-sha256> \
  --output <external/codex-replication-report.json>
```

Validate the completed packages with `scripts/validate.py` and retain the
read-only Claude historical audit separately. A complete Codex replication
report is descriptive; it does not claim variance, causal certainty, Claude
compatibility, Host Acceptance, or release readiness.
