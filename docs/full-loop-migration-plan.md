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

Add inactive templates for Project scope, Loop Map, Loop Contract, Task Ledger, and
Finding Ledger. Define identifiers, transitions, cross-references, and migration
from Lightweight delegation state. Keep validators structural rather than turning
them into a scheduler.

## Phase 3: Finding, Rework, Integration, and Loop Closure

Define Finding severity and disposition, bounded rework, Worker Delivery,
Integration Record, review reports, acceptance decisions, and Loop Closure. Add
static consistency checks and behavior evaluations without claiming a runtime
engine.

## Phase 4: Checkpoint and Context Recovery

Define the root Checkpoint, recovery ordering, stale-state reconciliation, context
pressure behavior, and evidence revalidation. Evaluate real recovery traces
separately from static template checks.

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
