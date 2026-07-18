# Full Loop Mode Templates

## Purpose

This directory contains static protocol templates for Full Loop Mode. It represents
how a Project can be divided into independently acceptable Loops and how Loop, Task,
and Finding status can have one authority. It does not run a workflow, create an
active Project, or prove host compatibility.

## When to Use

Use Full Loop Mode when work justifies multiple independent Loops, a Task DAG,
multiple Workers or Reviewers, Finding and rework cycles, cross-context recovery,
independent acceptance, or a Commit Boundary.

## When Not to Use

Do not use these templates for a one-line edit, a small single-file change,
low-risk work that can finish in one context, or any task where protocol cost is
greater than delivery and recovery value. Such work remains in Lightweight Mode.

## Template Versus Instance

Files named `*-TEMPLATE.md` are inactive protocol templates. A real Full Loop
Project copies them into the authoritative instance names defined below. A template
MUST NOT be treated as active state, and placeholder identifiers MUST NOT be treated
as real Projects, Loops, Tasks, Findings, evidence, or authority.

These phases do not create `PROJECT.md`, `LOOP-MAP.md`, `CHECKPOINT.md`, a
`.looppilot/loops/` directory, or a fictional `LOOP-001`.

## Authoritative State Sources

| State | Authority |
|---|---|
| Project scope and engineering context | `PROJECT.md` |
| Loop list and Loop status | `LOOP-MAP.md` |
| Task status within a Loop | `TASK-LEDGER.md` |
| Finding status within a Loop | `FINDING-LEDGER.md` |
| Current recovery entry point | `CHECKPOINT.md` |

`LOOP-MAP.md` MUST be the only authoritative source of Loop status.
`TASK-LEDGER.md` MUST be the only authoritative source of Task status within a Full Loop.
`FINDING-LEDGER.md` MUST be the only authoritative source of Finding status within a Full Loop.
`CHECKPOINT.md` MUST be the only authoritative recovery entry point.

Detailed contracts, deliveries, reviews, and findings MUST NOT independently
redefine authoritative status. They store content, evidence, rationale,
deliverables, and review conclusions. A Checklist MAY summarize state but MUST NOT
override an authoritative Ledger. Every projection MUST identify its authority.

The responsible role supplies the decision or evidence for a transition. The
Integrator records that transition in the authoritative source. Observable Git,
file, build, test, and tool state overrides stale Markdown, and conflicts MUST be
corrected instead of silently reconciled.

## Template Set

- [Loop Map](LOOP-MAP-TEMPLATE.md) projects Project-level Loop ordering and status.
- [Loop Contract](LOOP-CONTRACT-TEMPLATE.md) defines one Loop's stable delivery contract.
- [Task Ledger](TASK-LEDGER-TEMPLATE.md) owns Task status within one Full Loop.
- [Finding Ledger](FINDING-LEDGER-TEMPLATE.md) owns Finding status within one Full Loop.
- [Worker Delivery](WORKER-DELIVERY-TEMPLATE.md) reports Task-scoped output and evidence.
- [Integration Record](INTEGRATION-RECORD-TEMPLATE.md) records selected Deliveries,
  conflicts, and integration facts.
- [Review Report](REVIEW-REPORT-TEMPLATE.md) records Reviewer judgment and limitations.
- [Finding Detail](FINDING-TEMPLATE.md) records evidence and required outcome.
- [Rework Task](REWORK-TASK-TEMPLATE.md) scopes correction without expanding authority.
- [Loop Closure](LOOP-CLOSURE-TEMPLATE.md) summarizes acceptance and closure evidence.

The static relationship is:

```text
LOOP-CONTRACT
    -> TASK-LEDGER + Task Contracts
    -> WORKER DELIVERIES
    -> INTEGRATION RECORD
    -> REVIEW REPORTS
    -> FINDING DETAILS + FINDING LEDGER
    -> REWORK TASKS
    -> REVERIFICATION
    -> LOOP CLOSURE
    -> LOOP-MAP closed projection
```

Task-level Readiness permits a Delivery to enter integration; it is not Loop-level
Review. Worker self-report does not satisfy Integration, and integrated status does
not satisfy Review. Spec and Standards must both pass, conditional Reviewers
contribute where the Matrix requires them, and Reviewer reverification precedes
Finding closure.

These files remain static protocol templates. They do not create Agents, update
status, integrate branches, commit, or recover context. The detailed
[Phase 3 protocol](../../docs/full-loop-delivery-review-and-closure.md) defines the
delivery-to-closure relationships and their static validation boundary.
