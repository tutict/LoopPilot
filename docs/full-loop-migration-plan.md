# Full Loop Migration Plan

The first stage defines architecture and compatibility boundaries. Migration is
incremental so the existing Lightweight protocol remains usable and no fictional
active Project or Loop is created.

## Phase 1: Architecture Model and Templates

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

Static templates now define the root Checkpoint, Context Compaction Manifest,
Resume Validation Report, qualitative context pressure, Budget Stop, Minimal Safe
Unit, exact Resume Point, stale-state reconciliation, and intra- versus inter-Loop
recovery. The modular validator checks structural contradictions through the public
CLI without implementing recovery. See the
[Phase 4 protocol](full-loop-checkpoint-and-context-recovery.md).

Real token signals, automatic compaction, Checkpoint creation, new-session or Agent
takeover, cross-session recovery, Git conflict recovery, and recovery quality remain
behavioral evaluation work. Phase 4 does not implement Phase 5 Project Closure.

## Phase 5: Project Closure

Add project-level acceptance, cross-Loop integration evidence, security and
operations review, final delivery reporting, and explicit release authorities.
Project Release automation remains separate.

## Phase 6: Real-Host Behavioral Evaluation

Run observed evaluations on each named host for mode selection, Loop decomposition,
Reviewer Matrix fitness, multi-Agent coordination, Checkpoint recovery, and
authority boundaries. Publish only host and version claims supported by dated
traces.

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
