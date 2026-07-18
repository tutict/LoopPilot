# Cross-Loop Validation TEMPLATE

Template Status: inactive

## Identity

- Validation ID: none
- Project ID: none
- Performed: none
- Performed by: none
- Validation Status: inactive
- Project boundary: none
- Verified HEAD or artifact boundary: none

Allowed Validation Status values are `inactive`, `planned`, `in-progress`,
`passed`, `passed-with-limitations`, `failed`, `blocked`, and `superseded`.

## Included Loops

| Loop ID | Required | Loop Status | Closure | Commit Boundary | Included |
|---|---|---|---|---|---|
| None | no | none | none | none | no |

## Excluded or Non-Mandatory Loops

- None.

## Cross-Loop Dependencies

| Source Loop | Target Loop | Dependency | Expected Contract | Result |
|---|---|---|---|---|
| None | none | none | none | pending |

## End-to-End User Flows

| Flow ID | User or Actor | Participating Loops | Expected Outcome | Evidence | Result |
|---|---|---|---|---|---|
| None | none | none | none | none | pending |

## Requirement Coverage

| Requirement ID | User Goal | Implementing Loops | Integrated Outcome | Evidence | Result |
|---|---|---|---|---|---|
| None | none | none | none | none | pending |

## Interface and Contract Compatibility

- None.

## Data and Migration Compatibility

- None.

## Identity, Permission, and Security Compatibility

- None.

## Concurrency, Idempotency, and Ordering

- None.

## Configuration and Environment Compatibility

- None.

## Observability Continuity

- None.

## Performance and Capacity

- None.

## Deployment Ordering

- None.

## Rollback and Compensation Relationships

- None.

## Version and API Evolution

- None.

## Documentation Consistency

- None.

## Validation Performed

| Command, Scenario, or Inspection | Result | Evidence |
|---|---|---|
| None | not-run | none |

## Skipped or Not-Applicable Validation

- None.

## Project-Level Findings

| Finding Reference | Severity | Target Remediation Loop | Status Source |
|---|---|---|---|
| None | none | none | none |

Project Findings are triaged by the Supervisor and their authoritative status is
recorded in the target Loop's `FINDING-LEDGER.md`; this artifact is not a parallel
Project Finding Ledger.

## Coverage Limitations

- None.

## Validation Decision

- Decision: none
- Reason: none
- Blocking conditions: none
- Required remediation: none

Closed mandatory Loops are prerequisites, not sufficient evidence for `passed`.
The integrated outcome and relevant cross-Loop risks require observed validation.

## Authority Note

This Validation records cross-Loop evidence. It does not own Project, Loop, Task,
Finding, Release, Deployment, or Recovery status. `PROJECT.md` remains the only
Project status authority, and `CHECKPOINT.md` remains the Recovery authority.
