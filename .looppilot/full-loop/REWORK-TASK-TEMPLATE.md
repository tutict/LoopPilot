# Rework Task TEMPLATE

Template Status: inactive

## Identity

- Rework Task ID: none
- Parent Task: none
- Loop ID: none
- Assigned Worker: none
- Revision: none
- Revision Budget: none
- Created: YYYY-MM-DD
- Created by: none

Active Rework Task IDs use the `TASK-NNN-R1`, `TASK-NNN-R2`, and later positive
revision pattern. `R0` is invalid.

## Originating Findings

- None.

## Required Outcome

- None.

## Allowed Scope

- None.

## Forbidden Scope

- None.

## Required Changes

- None.

## Required Verification

- None.

## Reviewer Reverification

- Required Reviewer: none
- Verification method: none
- Evidence required: none
- Substitute Reviewer reason: none

## Strategy Change

- Previous approach: none
- Why it failed: none
- New approach: none
- Material change: none

## Dependencies

- None.

## Authority

- Modify: no
- Delete: no
- Commit: inherited-no
- Push: inherited-no
- Release: inherited-no
- Deploy: inherited-no

## Escalation Conditions

- Revision budget exhausted
- Scope change required
- Architecture decision required
- Missing input
- Environment failure
- Finding conflict
- Budget exhaustion

## Completion Boundary

Completion of this Rework Task does not close a Finding or the Loop. The Worker
submits a new Delivery; an original or authorized equivalent Reviewer must reverify
it before the Supervisor may approve disposition and the Integrator may update
`FINDING-LEDGER.md`. The same failed approach must not be repeated without a
material strategy change.
