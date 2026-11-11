# Review Report TEMPLATE

Template Status: inactive

- Review Schema Version: 2

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
Allowed Reviewer Type values are `four-axis`, `spec`, `standards`, `domain`, `data`,
`concurrency`, `security`, `operations`, `performance`, `architecture`, `frontend`,
`compatibility`, `test`, `code-quality`, `accessibility`, `compliance`,
`factual-accuracy`, `citation`, `methodology`, `structure`, `visual`, and
`domain-expert`. Allowed Status values are `inactive`, `in-progress`, `completed`,
`blocked`, and `superseded`.

Review Schema Version 2 uses the four-axis structure. Risk-selected professional
reviews are recorded separately as conditional contributions; they never replace
an axis decision.

## Review Scope

- None.

## Evidence Reviewed

- Integration Record: none
- Execution Infrastructure Incident evidence: none
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

## Lifecycle Consistency Review

- Supporting artifact contradiction check: not-evaluated
- Exact fields checked: status, owner, revision, Finding state, Git boundary,
  review decision, and Closure decision
- Semantic projection review: not-evaluated
- Evidence: none
- Limitations: none

Does any supporting artifact contradict authoritative lifecycle state? Deterministic
equality belongs to `scripts/validate.py`; misleading prose, Scope meaning, and
acceptance interpretation remain Reviewer judgment.

## Findings Created

- None.

## Coverage Limitations

- None.

Review may cite an Execution Infrastructure Incident and disclose missing
verification. An incident is not automatically a Finding; a Product or Protocol
Finding requires evidence of that defect. The Reviewer does not modify the
implementation.

## Standards Review Contribution

- Decision: not-evaluated
- Evidence: none
- Limitations: none

## Spec Review Contribution

- Decision: not-evaluated
- Evidence: none
- Limitations: none

## Implementation Quality Review Contribution

- Decision: not-evaluated
- Applicability evidence: none
- Evidence: none
- Limitations: none

## Verification & Evidence Review Contribution

- Decision: not-evaluated
- Applicability evidence: none
- Evidence: none
- Limitations: none

## Reviewer Verdict

- Verdict: none
- Rationale: none

Allowed Verdict values for an active Review are `pass`, `pass-with-findings`,
`rework-required`, and `blocked`. Every applicable Spec, Standards, Implementation
Quality, and Verification & Evidence axis must pass; only the latter two may be
`not-applicable`, supported by scope or deliverable evidence. A specialist
contribution does not replace the four axes, and `pass-with-findings` does not
dispose of Findings. Project-level Review
examines the integrated Project outcome and requires a Project ID, Cross-Loop
Validation, Goal-to-Evidence Mapping, and reviewed boundary; its Loop ID is
`not-applicable`. Each axis records an independent decision.

## Reverification Requirements

- None.

## Authority Note

The Reviewer judges the reviewed boundary and may create Findings. This Review does
not modify implementation, change Scope, update authoritative Ledgers, accept risk,
authorize commit, push, release, or deploy, or close the Loop. Review Reports do
not own Finding status; `FINDING-LEDGER.md` remains authoritative.
Project-level Review also does not own Project status; `PROJECT.md` remains the only
Project status authority.
