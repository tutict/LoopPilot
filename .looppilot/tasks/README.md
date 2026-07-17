# Delegated Task Protocol

## Positioning

This directory defines an optional, host-native delegation and supervision
protocol for hosts that support multiple Agents, delegated sessions, or equivalent
task assignment. LoopPilot does not create Agents, schedule concurrent work,
isolate processes, lock files, cancel sessions, or merge results. The host supplies
those capabilities when they exist.

Simple tasks MUST NOT be split across multiple Agents without a clear, documented
benefit. If coordination cost is likely to exceed the value of decomposition, the
current Agent SHOULD complete the task directly and leave
[`DELEGATION.md`](../DELEGATION.md) inactive.

## Roles and Accountability

### Supervisor

The Supervisor owns the parent Goal and the final integrated outcome. It reads the
latest user instruction and native Plan, decides whether delegation is worthwhile,
decomposes the work, checks dependencies and overlap, creates Task Contracts,
assigns Workers, selects sequence or parallelism, tracks status, sends submissions
to review, handles revisions or reassignment, and ensures parent-level verification.

Before assignment, the Supervisor MUST judge whether current external facts could
materially affect the work. When needed, it prepares a traceable
[`RESEARCH-TEMPLATE.md`](../RESEARCH-TEMPLATE.md) brief from authoritative sources.
It SHOULD inspect host-confirmed available Skills and assign the smallest relevant,
trusted, version-aware set with a recorded fallback. It MUST NOT invent or install a
Skill, assume every host exposes the same inventory, or treat selection as authority.

The Supervisor MUST NOT approve solely from Worker self-report, equate all
`approved` tasks with a completed parent Goal, silently merge conflicts, expand
authorization, or over-decompose simple work.

### Worker

A Worker owns only the Task Contract assigned to it. It checks current facts and
dependencies, works within `scope.allowed`, avoids `scope.forbidden`, produces the
specified deliverables, gathers observed evidence, reports risks and blockers, and
submits the result for review.

A Worker SHOULD reuse still-current Supervisor research but MUST verify that it
applies to the actual code and environment. A Worker MUST NOT invent, install, or
load a forbidden Skill, change the parent Goal, grant itself authority, inherit another
Agent's authority, modify forbidden areas, resolve cross-task conflicts privately,
mark its task `approved` or `integrated`, or announce parent completion.

### Reviewer

The Reviewer independently performs two axes. Standards Review checks instruction
priority, repository rules, safety, authority, scope, maintainability, source
quality, Skill discipline, context efficiency, and runtime-free platform neutrality.
Spec Review checks the objective, deliverables, success criteria, required evidence,
dependencies, research use, parent alignment, edge cases, omissions, and integration
readiness.

Each axis decides `pass`, `revision-requested`, `rejected`, or `blocked`. Overall
decisions remain `approved`, `revision-requested`, `rejected`, or `blocked`.
`approved` requires both axes to pass, required evidence to be observed, and no
blocking conflict. One strong axis cannot offset the other. The Reviewer MUST NOT
use a vague approval, treat Worker claims as verification, hide gaps, expand
authority, skip an axis under context pressure, or announce parent completion.

### Integrator

The Integrator incorporates reviewed work into the parent result. The Supervisor
MAY also serve as Integrator in this first protocol version, but integration remains
a distinct responsibility. The Integrator checks file, interface, and specification
conflicts; re-checks assumptions between tasks; runs combined regressions; and
verifies the parent success criteria.

The Integrator MUST NOT use last-writer-wins, silently overwrite conflict evidence,
integrate unreviewed work, equate `approved` with `integrated`, or skip parent-level
verification.

Multiple Agents MAY contribute, but one accountable Supervisor or Integrator MUST
own the final integrated result. If no final owner can be identified, the parent
Goal MUST NOT be marked completed.

## When Delegation Has Value

Delegation SHOULD be considered when work has independently reviewable
deliverables, non-overlapping modification scopes, clear dependencies, explicit
output interfaces, a useful independent review need, or genuinely different
specialist perspectives. Parallel benefit MUST exceed coordination and integration
cost.

Delegation SHOULD NOT be used for a one-step task, a small single-file edit, tightly
coupled work, work that cannot be independently accepted, work requiring every
Worker to edit the same core region, or a host that cannot reliably assign and
recover results.

Before parallel assignment, the Supervisor MUST check:

- file and resource overlap;
- satisfied input dependencies;
- explicit output interfaces;
- possible shared-state overwrite;
- independent acceptance criteria;
- whether one result changes another task's assumptions;
- failure and integration cost; and
- least-privilege authority for each task.

When multiple tasks concern the same core file, the preferred pattern is separate
suggestion-only tasks followed by one Integrator edit. Multiple Workers SHOULD NOT
concurrently write the same core file.

## Task Contract

Copy [`TASK-TEMPLATE.md`](TASK-TEMPLATE.md) for each real assignment. Name the file
for its stable ID, such as `TASK-001.md`, and name its review
`REVIEW-TASK-001.md`. Neither artifact contains a complete conversation, private
chain-of-thought, or a copy of the parent Plan.

Required fields have these meanings:

- `task_id`: a unique, stable identifier such as `TASK-001`; reassignment does not
  change it.
- `parent_goal`: the parent outcome the task serves; a Worker MUST NOT change it.
- `status`: current lifecycle state.
- `previous_status`: the immediately preceding state, or `none` for initial
  proposal. It makes the latest transition statically reviewable.
- `status_changed_by`: the logical role responsible for the latest transition.
- `assigned_role` and `assigned_to`: the bounded role and platform-neutral assignee.
- `objective`: one specific, independently reviewable outcome.
- `scope.allowed`: exact files, modules, resources, actions, or research areas that
  may be touched.
- `scope.forbidden`: explicit exclusions.
- `deliverables`: concrete artifacts or findings, never only "complete the task."
- `success_criteria`: observable acceptance conditions.
- `required_evidence`: diffs, tests, builds, sources, renders, file existence, or
  other reproducible evidence.
- `dependencies`: `none`, Task IDs, external inputs, permissions, or user decisions.
- `research_inputs`: Research Brief IDs, purposes, and required findings used by the
  Worker.
- `skill_assignment`: required, optional, forbidden, and fallback capabilities;
  required Skills record source, version, expected output, and observed
  `verified_available` state.
- `skill_selection`: considered, selected, and unavailable choices plus the
  Supervisor identity. Unavailable or forbidden Skills cannot be selected.
- `checklist_item`: a stable `ITEM-NNN` parent Checklist link, or `none` when a
  justified delegated task does not map one-to-one. Task IDs and Item IDs are not
  interchangeable.
- `authority`: explicit booleans for `read`, `modify`, `delete`, `commit`, `push`,
  `release`, `deploy`, and `external_communication`.
- `reviewer`: independent reviewer identity or logical role.
- `integration_owner`: the single owner responsible for integration.
- `revision_count`: number of returned revision cycles.
- `revision_budget`: a positive, task-specific revision limit selected by the
  Supervisor before assignment.
- `created` and `updated`: contract dates.

High-impact authority defaults to `false`. Assignment never implies push, release,
deployment, deletion, or external communication. Old authority in a Task Contract
is historical context until re-confirmed against the latest user instruction.

Delegation transfers responsibility for scoped work, not authority beyond the
explicit Task Contract and current user instruction.

## Status Lifecycle

Allowed task statuses are:

`proposed`, `assigned`, `in-progress`, `submitted`, `under-review`,
`revision-requested`, `approved`, `rejected`, `blocked`, `cancelled`, and
`integrated`.

Legal transitions are:

```text
none -> proposed
proposed -> assigned | cancelled
assigned -> in-progress | blocked | cancelled
in-progress -> submitted | blocked | cancelled
submitted -> under-review
under-review -> approved | revision-requested | rejected | blocked
revision-requested -> in-progress | cancelled
approved -> integrated | revision-requested
blocked -> assigned | in-progress | cancelled
rejected -> proposed | cancelled
integrated -> terminal
cancelled -> terminal
```

`approved` means the subtask passed independent review. `integrated` means reviewed
work was incorporated into the parent result and passed integration checks. They
MUST NOT be treated as synonyms.

Workers may advance assigned work to `in-progress`, `submitted`, or `blocked`. The
Supervisor moves `submitted` work to `under-review` when transferring it to the
Reviewer. Reviewers may set `approved`, `revision-requested`, `rejected`, or
`blocked`. Only the Supervisor or Integrator may set `integrated`. Supervisor-owned
planning transitions include `proposed`, `assigned`, `under-review`, and `cancelled`.

A task MUST NOT skip `under-review` before `approved`, skip `approved` before
`integrated`, resume after `cancelled`, or change after `integrated`. A correction
to integrated work requires a new Task Contract. If the parent Goal changes, the
Supervisor MUST pause, cancel, or rewrite affected contracts before work continues.

## Review and Correction

Use [`REVIEW-TEMPLATE.md`](REVIEW-TEMPLATE.md) for an independently checkable review
result. An `approved` decision MUST cite checked success criteria and observed
evidence. A `revision-requested` decision MUST identify the failed criterion,
missing evidence, scope violation or conflict, and the expected correction. A
`blocked` decision MUST name the missing input, permission, tool, or environment. A
`rejected` decision MUST explain why the result should not continue to revision or
integration.

The approval rule is:

```text
Standards Review = pass
AND Spec Review = pass
AND required evidence is observed
AND no unresolved blocking conflict exists
```

The Worker keeps the original Task ID, increments `revision_count`, and returns from
`revision-requested` to `in-progress`. The Supervisor SHOULD set a positive,
task-specific revision limit appropriate to risk and cost before assignment.
The Review Result remains with the task through a legal correction or rejected-task
restart until a later independent decision supersedes it; status changes MUST NOT
erase the criteria, evidence gaps, corrections, or rejection reason.
`revision_count` MUST NOT exceed that limit; when the budget is exhausted, the
Supervisor MUST change strategy, request a decision, or stop honestly.

When the same task fails repeatedly, the strategy MUST change materially. The
Supervisor MUST change the method, narrow the scope, change the Worker, request a
user decision, or stop as `blocked` or `budget-stopped`; it MUST NOT mechanically
reassign the same failed instruction to the same Worker.

## Conflict Handling

Before integration, the Supervisor and Integrator MUST check for overlapping files
or regions, contradictory rules, duplicate implementations, unmet dependencies,
changed assumptions, scope violations, stale shared state, authority inheritance,
and incompatible output formats.

Conflict decisions MUST NOT use last-writer-wins, silent overwrite, randomness, or
Worker confidence. The responsible role SHOULD:

1. mark the conflict;
2. preserve observable evidence from all affected tasks;
3. pause affected integration;
4. resolve it through the Supervisor, Reviewer, a dedicated integration task, or
   the user when necessary; and
5. re-run integration and parent-level verification.

Stable conflict resolutions MAY be recorded in [`DECISIONS.md`](../DECISIONS.md).
Ordinary review results belong with the task and SHOULD NOT be copied there.

## Parent Checklist and Budget Stop

A complex parent Goal SHOULD use [`CHECKLIST.md`](../CHECKLIST.md) as a compact
recovery index, not a second native Plan. Each delegated task SHOULD reference one
stable Checklist item. An item MAY aggregate multiple tasks through the Integrator,
but a task MUST NOT silently complete undeclared items. Reviewer approval leaves an
item `[ ]`; only parent integration verification permits `[x]` with
`Status: integrated` and observed evidence.

Context pressure is `unknown`, `normal`, `elevated`, `high`, or `critical`. At
`high`, the Supervisor SHOULD stop creating low-priority tasks, avoid new high-risk
work, finish the smallest verifiable unit, and persist Checklist, task status,
evidence, shared state, handoff, and one exact Resume Point. At `critical`, it MUST
persist and stop before forced interruption. Budget stop requires:

```text
Checklist Status: budget-stopped
Resume required: true
```

The stop record names completed and incomplete items, observed evidence, blockers,
the current task, one Resume Point, and the next highest-value action. Pressure
never skips either review axis, lowers criteria, expands authority, checks an
approved item, fabricates evidence, or calls partial work completed.

On resume, re-check the latest instruction, native Goal and Plan, files, Git,
Checklist, delegation, active contracts, and handoff. Revalidate `[x]` evidence and
correct stale state before continuing. Simple tasks MUST NOT create Checklist,
research, or Skill-routing overhead.

## Host and State Boundaries

[`DELEGATION.md`](../DELEGATION.md) is only a compact coordination summary; it does
not duplicate full contracts or a native Plan. [`HANDOFF.md`](../HANDOFF.md) is a
sequential continuity record, not an assignment. Neither mechanism transfers role
or authority.

Delegation state can be stale. Every resuming Agent MUST re-check the latest user
instruction, native state, files, tools, tests, active sessions, and authority.
Cancelled or narrowed work MUST NOT be reactivated from an old file.
