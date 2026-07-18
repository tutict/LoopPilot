# CHECKPOINT TEMPLATE

Template Status: inactive

## Identity

- Checkpoint ID: none
- Project ID: none
- Loop ID: none
- Created: YYYY-MM-DD
- Created by: none
- Verified: none
- Verified by: none
- Checkpoint Status: inactive
- Replaces: none
- Superseded by: none

Allowed Checkpoint Status values are `inactive`, `draft`, `ready`,
`budget-stopped`, `resuming`, `validated`, `stale`, `superseded`, `blocked`,
and `invalid`. Active IDs use `CHECKPOINT-NNN` with at least three digits.

## Recovery Boundary

- Repository: none
- Branch: none
- Verified HEAD: none
- Working tree: not-inspected
- Uncommitted changes: none
- Diff boundary: none
- Integrated boundary: none
- Latest Loop Closure: none
- Project scope source: `PROJECT.md`
- Loop status source: `LOOP-MAP.md`
- Task status source: `TASK-LEDGER.md`
- Finding status source: `FINDING-LEDGER.md`
- Recovery authority: `CHECKPOINT.md`

## Current Execution State

- Current Loop: none
- Loop status observed in Loop Map: none
- Current Barrier: none
- Active Task or Rework: none
- Integration state: none
- Review state: none
- Closure state: none
- Context Pressure: unknown
- Budget State: unbounded-unknown

Context Pressure values are `unknown`, `normal`, `elevated`, `high`, and
`critical`. Budget State values are `unbounded-unknown`, `bounded`, `healthy`,
`constrained`, `high-pressure`, `critical`, `budget-stopped`, `exhausted`, and
`not-applicable`.

## Verified Completed Work

- None.

## Unfinished Work

- None.

## Open Blockers

- None.

## Open Major Findings

- None.

## Pending Decisions

- None.

## Authority State

- Modify: no
- Delete: no
- Commit authorized: no
- Commit result: not-created
- Push: no
- Release: no
- Deploy: no
- Authority source: latest user instruction and applicable platform rules

Authority is current and action-specific. This record cannot grant or inherit
modify, delete, commit, push, release, or deploy permission.

## Required Context

| Priority | Artifact | Why required | Verified |
|---|---|---|---|
| None | none | none | no |

## Context Exclusions

- Complete conversation history.
- Superseded drafts and closed low-level work unless a conflict requires them.
- Private chain-of-thought or hidden reasoning.

## Evidence Requiring Revalidation

| Evidence | Source | Reason | Required action |
|---|---|---|---|
| None | none | none | none |

## Exact Resume Point

- Resume item: none
- Resume action: none
- Required inputs: none
- Required tool or capability: none
- Expected observable result: none
- Stop or escalation condition: none

There MUST be exactly one primary Resume Point. It must use a stable Item, Task,
Finding, Barrier, or validation identifier and must not depend on unsaved chat or
private reasoning.

## Next Highest-Value Action

- None.

## Budget Stop Record

- Trigger: none
- Pressure level: unknown
- Minimal safe unit: none
- Persisted state: none
- Authoritative state updated: none
- Reviews still required: Spec Review and Standards Review
- Failed or skipped verification: none
- Stop decision: none

At `high` pressure, finish only the smallest safe verifiable unit and persist its
boundary. At `critical` pressure, stop new Worker creation, Rework, Integration,
and code modification; persist observed state and stop. Budget pressure MUST NOT
skip Spec Review or Standards Review, hide failures, mark partial work completed,
close Findings, expand authority, or mark a Loop closed.

## Recovery Readiness

- Recovery ready: no
- Resume Validation reference: none
- Required references present: no
- Exact Resume Point actionable: no
- Unresolved recovery conflicts: none

## Honesty Boundary

`CHECKPOINT.md` is the only authoritative recovery entry. It indexes a verified
boundary and one exact Resume Point; it does not own Project Scope, Loop status,
Task status, or Finding status. It is not a Commit, Loop Closure, Ledger, Handoff,
Checklist, conversation transcript, automatic context compactor, or recovery
runtime. An inactive template contains no real Project, Loop, Git HEAD, evidence,
authority, or recovery-readiness claim.
