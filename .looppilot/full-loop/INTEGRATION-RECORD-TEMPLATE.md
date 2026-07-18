# Integration Record TEMPLATE

Template Status: inactive

## Identity

- Integration ID: none
- Loop ID: none
- Integrator: none
- Started: YYYY-MM-DD
- Completed: none
- Status: inactive
- Integrated boundary: none

Allowed Status values are `inactive`, `collecting`, `integrating`, `blocked`,
`failed`, and `integrated`.

## Inputs

### Included Deliveries

| Task ID | Delivery ID | Readiness | Included |
|---|---|---|---|
| None | none | pending | no |

### Excluded Deliveries

- None.

## Integration Order

- None.

## File Ownership and Conflict Groups

| Path or Artifact | Owner Task | Other Tasks | Resolution |
|---|---|---|---|
| None | none | none | none |

## Applied Changes

- None.

## Mechanical Conflicts

- None.

## Semantic Conflicts Escalated

- None.

## Build Verification

| Command | Result | Evidence |
|---|---|---|
| None | not-run | none |

## Integration Tests

| Command or Scenario | Result | Evidence |
|---|---|---|
| None | not-run | none |

## Data and Migration Verification

- None.

## Security and Permission Verification

- None.

## Observability Verification

- None.

## Unintegrated Work

- None.

## Integration Limitations

- None.

## Integration Barrier Assessment

- Contract references complete: not-evaluated
- Mandatory Deliveries included: not-evaluated
- Mechanical conflicts resolved: not-evaluated
- Semantic conflicts escalated: not-evaluated
- Build passed: not-evaluated
- Required integration tests passed: not-evaluated
- Integration Record complete: not-evaluated
- Barrier result: not-evaluated

## Authority Note

The Integrator records integration facts, readiness projections, and mechanical
resolutions only. Semantic conflicts go to the Supervisor. This record does not
change Scope, accept risk, reject or rewrite Reviewer Findings, authorize commit,
push, release, or deployment, or own Loop status. `integrated` does not mean
`accepted`, `closed`, or `[x]`; `LOOP-MAP.md` remains the Loop status source.
