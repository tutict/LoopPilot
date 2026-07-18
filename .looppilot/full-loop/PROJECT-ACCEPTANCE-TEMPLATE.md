# Project Acceptance TEMPLATE

Template Status: inactive

## Identity

- Acceptance ID: none
- Project ID: none
- Prepared: none
- Prepared by: none
- Supervisor: none
- Integrator: none
- Acceptance Status: inactive
- Project boundary: none
- Delivery mode: none

Allowed Acceptance Status values are `inactive`, `draft`, `under-review`,
`accepted`, `accepted-with-risks`, `blocked`, `rejected`, and `superseded`.
Allowed Delivery mode values are `delivery-only` and `release-required` for an
active instance.

## Original User Goal

- None.

## Current Project Scope

### Included Scope

- None.

### Excluded Scope

- None.

### Approved Scope Changes

- None.

### Cancelled Requirements

- None.

## Goal-to-Evidence Mapping

| Requirement ID | Requirement Class | User Goal or Requirement | Responsible Loops | Delivered Outcome | Acceptance Evidence | Result |
|---|---|---|---|---|---|---|
| None | none | none | none | none | none | pending |

Active Requirement IDs use `REQ-001` or a stable identifier already defined by the
Project Engineering Context. Requirement Class is `mandatory`, `optional`,
`deferred`, `cancelled`, or `excluded`.

## Mandatory Loop Summary

| Loop ID | Required | Status Source | Closure | Final Status | Evidence |
|---|---|---|---|---|---|
| None | no | none | none | none | none |

## Cross-Loop Validation

- Validation: none
- Result: none
- Coverage limitations: none
- Blocking conditions: none

## Project Review Summary

### Project Spec Review

- Result: not-evaluated
- Reports: none
- Findings: none
- Limitations: none

### Project Standards Review

- Result: not-evaluated
- Reports: none
- Findings: none
- Limitations: none

### Conditional Project Reviews

- None.

Specialist Reviews may contribute evidence, but never replace either mandatory
Project Spec Review or Project Standards Review axis.

## Project-Level Finding Disposition

| Finding | Severity | Remediation Loop | Authoritative Status Source | Current Status | Decision |
|---|---|---|---|---|---|
| None | none | none | none | none | none |

Project Findings must be routed by the Supervisor to an existing, reopened, or new
remediation Loop, whose `FINDING-LEDGER.md` owns Finding status.

## Project Functional Acceptance

- Result: not-evaluated
- [ ] Original user goals are mapped.
- [ ] Required end-to-end flows are verified.
- [ ] Cross-Loop business invariants remain valid.
- [ ] Required exception and failure flows are verified.
- [ ] Cancelled and excluded work is not counted as delivered.

## Project Engineering Acceptance

- Result: not-evaluated
- [ ] Architecture remains coherent across Loops.
- [ ] Data and migration compatibility is verified.
- [ ] Identity, permission, and security behavior is coherent.
- [ ] Concurrency, idempotency, and ordering requirements are satisfied.
- [ ] Observability and audit requirements are satisfied.
- [ ] Required compatibility and evolution constraints are satisfied.
- [ ] Project-level technical risks are disclosed.

## Project Delivery Acceptance

- Result: not-evaluated
- [ ] Delivery mode is explicit.
- [ ] Deployment or handoff instructions are complete.
- [ ] Configuration and environment requirements are documented.
- [ ] Required rollback or compensation strategy is documented.
- [ ] Release readiness is assessed.
- [ ] Final Checkpoint is valid.
- [ ] Final Delivery Report is prepared.
- [ ] Deferred work and accepted risks are disclosed.

## Residual Risks

- None.

## Deferred Work

- None.

## Accepted Risks

- None.

## Release Relationship

- Release required: none
- Release Readiness: none
- Release authorized: no
- Release result: not-executed
- Deployment required: none
- Deployment authorized: no
- Deployment result: not-executed

## Final Recovery State

- Final Checkpoint: none
- Checkpoint status: none
- Recovery readiness: no
- Terminal Resume Point or reopen condition: none

## Final Delivery Report

- Report: none
- Report status: inactive
- Intended recipient: none

## Acceptance Decision

- Decision: none
- Decision by: none
- Decision evidence: none
- Required follow-up: none

## Project Status Projection

- Requested Project status: none
- Status authority: PROJECT.md
- Integrator update required: no
- Update evidence: none

The Supervisor owns Project Acceptance and risk disposition. The Integrator may
record an authorized projection in `PROJECT.md` only after the decision and evidence
are complete; this artifact never updates status by itself.

## Honesty Boundary

This Acceptance must not claim delivered work without evidence, count cancelled or
excluded work as complete, own Project status, or infer release or deployment
authorization from Project acceptance. A Project Blocker prevents acceptance.
