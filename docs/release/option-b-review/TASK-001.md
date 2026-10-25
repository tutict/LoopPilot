---
task_id: TASK-001
parent_goal: Implement the bounded Option B successor and safely push a verified RC candidate.
status: integrated
previous_status: approved
status_changed_by: integrator
assigned_role: worker
assigned_to: /root
objective: Produce the scoped Option B implementation for independent Standards and Spec review.
scope:
  allowed:
    - Option B policy, RC designation and candidate records, related documentation, validators and tests.
  forbidden:
    - Historical evidence or verdict changes, provider/model/endpoint changes, automatic Reference switching, relaxed gates, release or deployment.
deliverables:
  - Reviewed task diff with reproducible verification and honest candidate status.
success_criteria:
  - C01-C08 hold and all required repository checks pass; blocking review findings are resolved independently.
required_evidence:
  - Public-entry positive and negative RC regressions, full suite, static and Skill validation, Mermaid renders, final diff.
dependencies:
  - User-approved six implementation defaults dated 2026-10-24.
research_inputs: []
skill_assignment:
  required: []
  optional: []
  forbidden: []
  fallback:
    - strategy: Use base read/search/test tools; do not install Skills.
skill_selection:
  considered: []
  selected: []
  verified_available: []
  selected_by: /root
checklist_item: none
authority:
  read: true
  modify: true
  delete: false
  commit: false
  push: false
  release: false
  deploy: false
  external_communication: false
reviewer: /root/option_b_review
integration_owner: /root
revision_count: 2
revision_budget: 3
created: 2026-10-24
updated: 2026-10-24
---

# Task Contract

The latest user instruction, not this file, authorizes consequential parent actions.
The independent Reviewer has read/test authority only and MUST NOT edit implementation.
Skill assignment transfers no authority.

## Worker Submission

- Deliverables produced: Revised policy, RC receipt/summary binding, synchronized documentation, and 37 passing focused regressions.
- Evidence observed: Full regression: 1141 PASS, zero failures/errors/skips; independent Standards and Spec both PASS; reviewed implementation integrated.
- Risks or blockers: Formal Host identity and acceptance remain unverified.
- Unfinished items: None within this implementation task; parent publication is reported separately.
- Conflict notes: None; implementation has one owner.

## Recorded integration

Observed on 2026-10-24: the independent Reviewer approved both axes; the Integrator verified all 1141 tests and the neutral export. This archived record is historical context, not current authority, host acceptance, parent completion, or permission for future operations.
