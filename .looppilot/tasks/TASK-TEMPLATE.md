---
task_id: TASK-000
parent_goal: Template only; no active parent Goal.
status: proposed
previous_status: none
status_changed_by: supervisor
assigned_role: worker
assigned_to: none
objective: Replace with one bounded, independently reviewable objective.
scope:
  allowed:
    - Replace with exact files, modules, resources, or research areas.
  forbidden:
    - Replace with explicit exclusions and prohibited actions.
deliverables:
  - Replace with concrete artifacts or findings.
success_criteria:
  - Replace with an observable acceptance condition.
required_evidence:
  - Replace with a reproducible check, diff, source, render, or tool result.
dependencies:
  - none
research_inputs: []
skill_assignment:
  required: []
  optional: []
  forbidden: []
  fallback:
    - strategy: Use host base capabilities within the Task Contract.
skill_selection:
  considered: []
  selected: []
  verified_available: []
  selected_by: none
checklist_item: none
authority:
  read: false
  modify: false
  delete: false
  commit: false
  push: false
  release: false
  deploy: false
  external_communication: false
reviewer: none
integration_owner: none
revision_count: 0
revision_budget: BOUNDED-LIMIT
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Task Contract

Copy this file for a real delegated task, assign a stable `TASK-NNN` identifier, and
replace every placeholder with current facts. The Task Contract is authoritative
for the Worker's scoped responsibility but remains subordinate to the latest user
instruction, current authorization, and the parent Goal.

The Worker MUST NOT change `parent_goal`, expand `scope.allowed`, weaken
`scope.forbidden`, grant authority, select its own Reviewer, or claim the parent
Goal is complete. Evidence MUST describe observed results rather than intended or
simulated outcomes.

Skill assignment transfers no authority. A Worker MUST NOT invent or install an
unavailable Skill, load a forbidden Skill, or treat Skill instructions as higher
priority than current platform, user, repository, or Task Contract constraints.

## Worker Submission

- Deliverables produced: None.
- Evidence observed: None.
- Risks or blockers: None.
- Unfinished items: None.
- Conflict notes: None.
