# Full Loop Migration Plan

The first stage defines architecture and compatibility boundaries. Migration is
incremental so the existing Lightweight protocol remains usable and no fictional
active Project or Loop is created.

## Phase 1: Architecture Model and Templates

**Status: implemented statically; behaviorally unverified.**

Define the Loop object model, Project Engineering Context, protocol modes, sources
of truth, role boundaries, review model, Barriers, acceptance layers, pattern
selection, Project Closure target, inactive Project template, minimal validation,
and regression coverage.

## Phase 2: Loop Contract, Loop Map, and Ledgers

**Status: implemented statically; behaviorally unverified.**

Inactive Loop Map, Loop Contract, Task Ledger, and Finding Ledger templates now
define identifiers, state enums, transition semantics, authority, completion
projection, and compatibility with Lightweight delegation state. Static validators
check structural invariants without scheduling work or mutating state.

## Phase 3: Finding, Rework, Integration, and Loop Closure

**Status: implemented statically; behaviorally unverified.**

Inactive detailed Finding, bounded Rework Task, Worker Delivery, Integration Record,
Review Report, and Loop Closure templates now build on the Phase 2 enums without
redefining their authority. Static consistency checks and public-CLI fixtures cover
explicit invariants without claiming a runtime engine. See the
[Phase 3 protocol](full-loop-delivery-review-and-closure.md).

## Phase 4: Checkpoint and Context Recovery

**Status: implemented statically; behaviorally unverified.**

Static templates now define the root Checkpoint, Context Compaction Manifest,
Resume Validation Report, qualitative context pressure, Budget Stop, Minimal Safe
Unit, exact Resume Point, stale-state reconciliation, and intra- versus inter-Loop
recovery. The modular validator checks structural contradictions through the public
CLI without implementing recovery. See the
[Phase 4 protocol](full-loop-checkpoint-and-context-recovery.md).

Real token signals, automatic compaction, Checkpoint creation, new-session or Agent
takeover, cross-session recovery, Git conflict recovery, and recovery quality remain
behavioral evaluation work.

## Phase 5: Project Closure

**Status: implemented statically; behaviorally unverified.**

Inactive Cross-Loop Validation, Project Acceptance, Release Readiness, and Final
Delivery Report templates now define Goal-to-Evidence Mapping, Project-level dual
review, three-layer acceptance, remediation Loop routing, the Project Closure Gate,
independent release authorities, and the terminal recovery boundary. The modular
validator checks structural contradictions without accepting, closing, releasing,
deploying, or modifying Project state. See the
[Phase 5 protocol](project-closure-and-final-delivery.md).

## Phase 6: Real-Project Behavioral Evaluation

**Status: partially observed through MMGH EXP-001 to EXP-004; not generally validated.**

The four bounded experiments are evidence only. They do not prove every host,
automatic mode selection, Reviewer independence, or strict A/B behavior.

## Phase 7: Evidence Synthesis and Protocol Calibration

**Status: implemented statically.**

Phase 7 adds evidence levels, the Mode Selection Gate, Lightweight escalation and
artifact-budget guidance, incident classification, risk-loaded specialist Review,
load profiles, and static validation. It adds no role, status, Ledger, severity,
Barrier, acceptance layer, recovery authority, runtime, or Project instance.

## Phase 8-A: Cross-Project Replication

**Status: observed through Final-Assignment EXP-005.**

EXP-005 is a bounded Spring Boot and Flutter replication. It supports calibration
without providing universal or production evidence.

## Phase 8-B: Controlled Three-Mode Comparison

**Status: executed through EXP-006 arms; comparative archive incomplete.**

The Baseline, Lightweight, and Full Loop arm heads are observed. The Full Loop arm
is blocked and not delivered. The dynamic holdout remains partially unverified, and
the inspected control archive retains pre-registration and incidents rather than a
final comparative score report. See
[Final-Assignment evidence](final-assignment-behavioral-evidence.md).

## Phase 9: Second Evidence-Backed Protocol Calibration

**Status: implemented statically.**

Phase 9 adds baseline attribution, Verification Surface inventory, Product Risk
versus Coordination Necessity, bounded specialist-reviewed Lightweight, delegation
fallback, verifiable claims, and artifact-category accounting. It adds no runtime,
role, status, Ledger, or authority.

## Phase 10: Third-Project and/or Cross-Host Replication

**Status: not implemented.**

Future work may include another project or host, a fully archived control comparison,
dynamic holdout observation, and further recovery or Reviewer evidence.

## Migration Rules

- MUST NOT remove or move current shared-state files until a compatibility release
  defines their replacement and migration.
- MUST NOT create PROJECT.md, LOOP-MAP.md, CHECKPOINT.md, or LOOP-001 as pretend
  runtime state.
- MUST introduce inactive templates before active instances.
- MUST give each status one authoritative source before adding projections.
- MUST keep host-native Plans authoritative for current-context ordering.
- MUST preserve commit, push, release, and deployment as separate permissions.
- MUST treat static validation as structural evidence, not behavioral compatibility.
