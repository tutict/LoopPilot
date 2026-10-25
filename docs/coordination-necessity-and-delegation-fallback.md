# Coordination Necessity and Delegation Fallback

## Product Risk and Coordination Risk

Product Risk concerns the harm or complexity of the change itself: security, data,
transactions, idempotency, sensitive data, compatibility, partial success, or
production impact. It determines appropriate Review Depth, Validation Depth, and
Evidence Depth.

Coordination Risk concerns whether safe delivery requires structured work between
owners. It determines whether Full Loop governance is justified. High product risk
does not by itself prove that multiple Workers are required.

```mermaid
flowchart TD
    C[Worker Claim] --> E{Verifiable evidence?}
    E -->|Yes| V[Verified claim]
    E -->|No| U[Unverified claim]
    V --> A[Eligible for authoritative update]
    U --> L[Delivery limitation or Finding if authority was contaminated]
```

Full Loop SHOULD be selected when stronger coordination governance is required to
deliver safely, not merely because a change is important. This is a provisional,
evidence-backed heuristic, not a mathematical rule or Normative Invariant.

## Coordination Necessity

Use the [ordered mode reassessment](mode-selection-and-escalation.md#authority-and-timing):
assess Product Risk, set the minimum review, validation, and evidence depth, then
reassess Coordination Necessity. Select Full Loop only when coordination requires
it; otherwise Lightweight or the applicable non-Full-Loop path remains allowed.
Risk-only changes preserve mode; specialist review adds scrutiny, not coordination
by definition. Before selecting Full Loop, record the following:

| Question | Evidence |
| --- | --- |
| Multiple implementation owners required | |
| Independent Worker value | |
| File ownership can be separated | |
| Deliverables can be independently verified | |
| Integration ordering is non-trivial | |
| Dedicated Integration Record required | |
| Active recovery required | |
| Formal Rework likely | |
| Single-owner implementation would be unsafe or opaque | |
| Expected coordination cost | |
| Coordination benefit | |

Use the resulting evidence proportionally:

- High product risk and low coordination necessity tends to Lightweight with
  appropriate Review.
- High product risk and high coordination necessity tends to Full Loop.
- Low product risk and high coordination necessity requires Full Loop when the
  actual need cannot be safely expressed by one owner plus bounded review.
- Low product risk and low coordination necessity tends to Lightweight.

File count remains supporting evidence only.

## Specialist-Reviewed Lightweight

Lightweight MAY load a risk-matched specialist Reviewer, including Security, Data,
Compatibility, Accessibility, or Operations. It remains Lightweight; a
specialist-reviewed Lightweight configuration is not a new mode or state. Spec and
Standards remain permanent review axes and specialists do not replace them.

Stop affected implementation and escalate for mode reassessment when a Major or
Blocker Finding appears, multiple
implementation owners become necessary, a dedicated Integration Record is needed,
cross-responsibility coordination emerges, corrections exceed the recorded budget,
the Change Contract becomes dishonest, active recovery is required, or formal
Rework cannot be expressed honestly in Lightweight. The presence of a Security
Reviewer alone does not require Full Loop. Preserve evidence, reassess risk and its
minimum checks, then coordination; do not send a stop directly to a Full Loop
Contract. A non-Full-Loop decision does not permit continuing past unresolved stop
conditions, required review or verification gaps, or the correction/resource budget.

### Deterministic Mode Cases

These finite maintenance cases make the existing two-axis rule checkable. They do
not create a runtime decision engine, a third mode, or authority for a Worker.
The Supervisor still evaluates scope, hard triggers, Findings and boundary evidence;
the Integrator records the decision. `required` coordination means real governance
that cannot be safely expressed by one owner plus bounded review, not merely several
steps or reviewer presence. `Full Loop gate` means evaluate and satisfy the existing
Contract Barrier for that coordination need. Risk sets review, validation and evidence
depth. Non-coding work has the same coordination rule.

| Case | Product risk | Coordination need | Specialist Reviewer | Work type | Permitted path | Risk-required minimum | Additional specialist review |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M1 | low | none | no | coding | Lightweight allowed | standard | none |
| M2 | high | none | no | coding | Lightweight allowed | enhanced | none |
| M3 | low | required | no | coding | Full Loop gate | standard | none |
| M4 | low | none | yes | coding | Lightweight allowed | standard | targeted |
| M5 | high | required | yes | coding | Full Loop gate | enhanced | targeted |
| M6 | low | none | no | non-coding | Lightweight allowed | standard | none |
| M7 | low | required | no | non-coding | Full Loop gate | standard | none |

The public maintenance validator checks these relationships, bounded procedural
shortcut clauses, and ordered risk/review/coordination paths in routed Mermaid
mode diagrams. It is a bounded deterministic check, not natural-language or
host behavior validation. The risk-required minimum is a floor, not actual performed
depth or a maximum. Specialist review adds targeted domain scrutiny above that floor;
it does not rewrite the risk floor or change mode by itself. The additional-review
column describes the case's assigned scope, not evidence that review has occurred.
Specialists never substitute for Spec or Standards or automatically prove coordination need.

## Worker Failure Budget

The same delegated responsibility SHOULD default to no more than two unsuccessful
Worker attempts. This is a provisional coordination-cost heuristic, not a platform
limit or a new Task status.

An unsuccessful attempt includes no output, no verifiable Delivery, clear scope
failure, an Agent or tool failure with no useful artifact, or a Delivery that fails
the Task Contract minimum. A valid Finding, ordinary Reviewer-requested Rework, or
an environment error discovered before the Worker begins does not consume this
budget.

At the budget, the Supervisor chooses one of: reassign to one designated fallback
Worker, collapse implementation ownership to one Worker, or block the Task/Loop.
Do not retry indefinitely and do not rewrite revision history to hide failures.

```mermaid
flowchart TD
    D[Delegated responsibility] --> A[Unsuccessful attempt]
    A --> B{Two attempts reached?}
    B -->|No| D
    B -->|Yes| S[Supervisor records coordination degradation]
    S --> F[Designated fallback Worker or single owner]
    S --> X[Block Task or Loop]
    F --> R[Independent Review remains]
```

## Ownership Collapse in Full Loop

Ownership collapse preserves Full Loop governance while reducing implementation
ownership. The Supervisor records the degradation and the designated fallback
Worker; the Integrator records the changed ownership boundary. The Reviewer remains
independent. The Task Ledger, Finding Ledger, Integration, Review, Closure, and
their existing authorities remain in force.

Reviewer and Integrator roles MUST NOT become code implementers merely because
Workers failed. A Supervisor taking over implementation without an ownership record,
resetting task revisions, or deleting failed Deliveries is also prohibited.

## Verifiable Worker Claims

Worker Deliveries use this table for material factual claims:

| Claim | Evidence | Verification | Git Boundary |
| --- | --- | --- | --- |

They also state:

```md
## Unverified Claims

- None.
```

A Worker summary is not evidence. A material claim must be located in a file, code,
test, command, log, commit, database assertion, or authoritative external source.
Unsupported claims discovered before an authoritative decision go in Delivery
limitations. Claims that already contaminated Task, Integration, or Review decisions
become a Protocol or Process Finding, not an Execution Infrastructure Incident or
Product Finding by default. Do not create `CLAIM-LEDGER.md` or
`EVIDENCE-LEDGER.md`.
