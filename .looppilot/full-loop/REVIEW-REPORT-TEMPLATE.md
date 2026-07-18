# Review Report TEMPLATE

Template Status: inactive

## Identity

- Review ID: none
- Review Level: none
- Project ID: none
- Loop ID: none
- Reviewer: none
- Reviewer Type: none
- Reviewed Integration: none
- Reviewed Cross-Loop Validation: none
- Reviewed Goal Mapping: none
- Reviewed Boundary: none
- Started: YYYY-MM-DD
- Completed: none
- Status: inactive

Allowed Review Level values for an active Review are `loop` and `project`.
Allowed Reviewer Type values are `spec`, `standards`, `domain`, `data`,
`concurrency`, `security`, `operations`, `performance`, `architecture`, `frontend`,
`compatibility`, `test`, `code-quality`, `accessibility`, `compliance`,
`factual-accuracy`, `citation`, `methodology`, `structure`, `visual`, and
`domain-expert`. Allowed Status values are `inactive`, `in-progress`, `completed`,
`blocked`, and `superseded`.

## Review Scope

- None.

## Evidence Reviewed

- Integration Record: none
- Diff or artifact boundary: none
- Tests: none
- Logs: none
- Research: none
- Architecture decisions: none
- Other: none

## Checks Performed

- None.

## Passed Checks

- None.

## Findings Created

- None.

## Coverage Limitations

- None.

## Standards Review Contribution

- Decision: not-evaluated
- Evidence: none
- Limitations: none

## Spec Review Contribution

- Decision: not-evaluated
- Evidence: none
- Limitations: none

## Reviewer Verdict

- Verdict: none
- Rationale: none

Allowed Verdict values for an active Review are `pass`, `pass-with-findings`,
`rework-required`, and `blocked`. Final Loop review requires both the Spec Review
and Standards Review axes to pass; a specialist contribution does not replace both
axes, and `pass-with-findings` does not dispose of Findings. Project-level Review
examines the integrated Project outcome and requires a Project ID, Cross-Loop
Validation, Goal-to-Evidence Mapping, and reviewed boundary; its Loop ID is
`not-applicable`. Project Spec and Project Standards remain separate mandatory axes.

## Reverification Requirements

- None.

## Authority Note

The Reviewer judges the reviewed boundary and may create Findings. This Review does
not modify implementation, change Scope, update authoritative Ledgers, accept risk,
authorize commit, push, release, or deploy, or close the Loop. Review Reports do
not own Finding status; `FINDING-LEDGER.md` remains authoritative.
Project-level Review also does not own Project status; `PROJECT.md` remains the only
Project status authority.
