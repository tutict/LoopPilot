# MMGH Behavioral Evidence

## Scope and Source Discipline

MMGH was used as a read-only evidence source for four bounded experiments. The
evidence was checked in the local repository through Git objects, experiment
Results, Observations, Scorecards, authoritative Ledgers, Review Reports,
Closures, Checkpoints, and relevant product diffs. Local and local-tracking refs
matched at inspection time. Remote authentication was unavailable, so live
remote identity remains unverified and the failed check is an Execution
Infrastructure Incident.

This document contains no MMGH secret, credential, user file content, private
Worker record, or complete log. It does not claim a strict A/B comparison,
general superiority, production safety certification, or complete MMGH
re-architecture.

Phase 6 is partially observed through these experiments and not generally
validated.

## Verified Experiment Boundaries

| Experiment | Mode | Branch | Final SHA | Score | Boundary |
| --- | --- | --- | --- | --- | --- |
| EXP-001 | Full Loop | `experiment/looppilot-mmgh-exp-001` | `23ae0246c0fee309a728eb6c1c1dbaba8f50435d` | 54/60 | Workspace Snapshot Reconciliation Boundary |
| EXP-002 | Lightweight | `experiment/looppilot-mmgh-exp-002` | `afa5540f385b06bd9ebf7c6cd6e7188915d05e96` | 60/66 | Desktop Window Lifecycle Projection |
| EXP-003 | Full Loop | `experiment/looppilot-mmgh-exp-003` | `90177dad76d84dac5386bbd6e010e0c4a732aef4` | 72/78 | Provider Security Contract Alignment |
| EXP-004 | Full Loop | `experiment/looppilot-mmgh-exp-004` | `bf07d0f8b9e9a67b92bfb672c8953e2de79ded29` | 72/78 | Storage Mutation Result and Cache Publication |

## EXP-001 Observed Evidence

- A pure snapshot reconciliation policy was extracted from `App.tsx` and covered
  by five focused behavior tests.
- Independent Spec Review passed. Standards Review found one Major process
  defect: the Task Ledger used the illegal status `review-ready`.
- Formal rework corrected that process defect and the original Reviewer
  reverified it.
- Two implementation Worker attempts produced no usable result and the
  Supervisor performed a disclosed fallback.
- The experiment recorded roughly 32 protocol or experiment files and roughly
  2,375 lines, demonstrating substantial Full Loop cost for a small extraction.
- No real cross-session recovery or controlled comparison was performed.

## EXP-002 Observed Evidence

- A single-owner desktop lifecycle hook stayed within TypeScript and avoided
  Rust, SQLite, security, permissions, and network trust.
- Mode evidence scored 7/24 with no Full Loop hard trigger; six focused tests
  supported the change.
- One Minor malformed-payload visibility guard omission was corrected within the
  bounded Lightweight scope.
- No independent Reviewer was used because delegation was judged disproportionate;
  the disclosed verdicts were Supervisor self-review rather than independent
  Review.
- The experiment used roughly six protocol or experiment files and 552 lines.
- Recovery loaded nine Must Load files plus its manifest rather than the complete
  prior history.

## EXP-003 Observed Evidence

- TypeScript and Rust shared a strict default trusted-host contract and DNS
  endpoint normalization boundary.
- Independent Spec, Standards, Security, and Compatibility Reviews passed; no
  Product Finding was recorded.
- One Major recovery-process Finding was corrected through `TASK-005-R1` and
  reverified by the original Reviewer.
- The recorded Scorecard was 72/78 and the pre-final boundary contained 24 files
  and about 1,274 lines.
- Real providers, real keys, DNS rebinding, redirect chains, penetration tests,
  and production trust behavior were not verified.

## EXP-004 Observed Evidence

- The change addressed a SQLite mutation already committed when snapshot cache
  refresh failed, while preserving the original web record on persistence
  error.
- Rust RED/GREEN evidence showed one commit and no duplicate retry in the
  injected condition.
- Independent Spec, Standards, Data, and Compatibility Reviews passed with zero
  Findings and no Rework.
- The Full Loop mode score was 21/28 and the Scorecard was 72/78.
- Early Workers encountered 429 or tool failures before a file-backed Delivery;
  the Supervisor fallback and verification limitation were disclosed.
- The first-push evidence boundary recorded 28 protocol/report files and a diff
  of 989 additions and 291 deletions. Schema, dependencies, permissions,
  secrets, release, and deployment were outside scope.

## Observed Outcomes

EXP-001 directly observed governance value, one Major process correction, Worker
fallback, and high protocol cost for a small extraction. EXP-002 directly observed
a bounded Lightweight correction with lower protocol cost and no independent
Review. EXP-003 observed cross-runtime specialist Review and one recovery-process
rework. EXP-004 observed transaction and partial-success evidence, zero Product
Findings, and disclosed Worker infrastructure failures.

## Repeated Patterns

- Full Loop produced explicit contract, Review, and recovery control evidence in
  EXP-001, EXP-003, and EXP-004 with material protocol cost.
- Agent or tool failure did not itself establish a Product Finding in EXP-001 and
  EXP-004.
- Checkpoint evidence preserved bounded recovery facts without loading complete
  history in EXP-002 and the Full Loop experiments.

## Provisional Heuristics

Bounded single-owner local changes tend toward Lightweight. Cross-runtime trust,
transaction, partial-success, useful multi-Worker, specialist-review, or active
recovery needs tend toward Full Loop. Four to seven Lightweight artifacts is a
cost-control target. These remain revisable and are not automatic decisions.

## Contradictions and Limits

The experiments used different tasks, risks, and protocol depths. EXP-002 shows
lower Lightweight overhead, while EXP-001 shows Full Loop cost for a small
extraction; neither is a controlled comparator for EXP-003 or EXP-004. Local refs
matched local tracking refs, but live remote identity was not verified.

## Unverified Claims

Strict same-task Baseline/Lightweight/Full Loop comparison, second-project
replication, exact token accounting, long-term maintenance, automatic selection,
all-host compatibility, production behavior, and security or data certification
remain unverified.

## Protocol Changes Supported

The evidence supports a pre-implementation Mode Gate, a provisional Lightweight
Artifact Budget, explicit escalation, risk-loaded specialist Review, proportional
load profiles, and a separate Execution Infrastructure Incident classification.

## Protocol Changes Not Supported

The evidence does not support a new role, Ledger, status, severity, Barrier,
acceptance layer, recovery authority, automatic mode or Reviewer runtime,
mandatory architecture pattern, universal Full Loop preference, release, or
deployment authority.

## Synthesis Limits

Observed outcomes remain tied to named experiments; repeated evidence supports
only provisional guidance. Authority and evidence honesty remain Normative
Invariants independently of this evaluation.
