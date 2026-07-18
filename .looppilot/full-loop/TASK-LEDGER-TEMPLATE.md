# Task Ledger TEMPLATE

Loop ID: none
Status: inactive
Updated: YYYY-MM-DD
Updated by: none
Integrator: none

## Authority

- Task status authority: `TASK-LEDGER.md`
- Decision authority: Supervisor
- Recording authority: Integrator
- Worker may update Ledger: no
- Reviewer may update Ledger: no

## Task Summary

| Task ID | Title | Type | Mandatory | Status | Worker | Dependencies | Delivery | Review Readiness | Rework Of |
|---|---|---|---|---|---|---|---|---|---|
| None | None | None | no | proposed | none | none | pending | pending | none |

## Dependency Notes

- None.

## Contract Barrier Status

- Not evaluated.

## Implementation Barrier Status

- Not evaluated.

## Blocked Tasks

- None.

## Cancelled Tasks

- None.

## Ledger Notes

- Detailed Task Contracts do not own authoritative Task status.
- Worker Deliveries store implementation and evidence, not authoritative status.
- Existing Task Contract status semantics remain compatible: `approved` means the
  Task passed its independent check and is ready for integration; `integrated`
  means its result entered the unified Loop result.
- Integrated Task effect on Loop: none; Loop closure remains an independently
  recorded `LOOP-MAP.md` transition after the Closure Barrier.
