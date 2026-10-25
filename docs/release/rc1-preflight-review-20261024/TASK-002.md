---
task_id: TASK-002
parent_goal: Advance RC1 through honest preflight and publish verified new facts without premature acceptance.
status: integrated
previous_status: approved
status_changed_by: integrator
assigned_role: worker
assigned_to: /root
objective: Record and independently verify current RC1 preconditions, source captures, blockers and safe boundaries.
scope:
  allowed:
    - docs/release/rc1-preflight-20261024.md, its evidence and review archive, and the current candidate decision pointer.
  forbidden:
    - Host/provider/model/endpoint/proxy/auth configuration changes, live Skill replacement, threshold/validator changes, historical evidence edits, formal arms before prerequisites, release or deployment.
deliverables:
  - Source-linked preflight matrix, captured public-safe evidence, unchanged-boundary proof, fresh maintenance verification, independent review.
success_criteria:
  - Every precondition has a source, observed check, evidence, status, launch consequence and smallest unblocker; no unsupported acceptance claim.
required_evidence:
  - Fresh full tests, public validator, compilation, Skill and whitespace checks, evidence digests and boundary checks.
dependencies:
  - Current user preflight task and its no-evidence reply; baseline 061ca98.
research_inputs:
  - research_id: RESEARCH-002
    purpose: Distinguish Codex configuration/controller metadata from actual runtime evidence.
    required_findings: Official sources do not certify local upstream identity; see the preflight report Research Brief.
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
revision_count: 0
revision_budget: 3
created: 2026-10-24
updated: 2026-10-24
---

# Task Contract

This real task is bounded to the current user instruction and recorded preflight facts. The Task Contract is authoritative
for the Worker's scoped responsibility but remains subordinate to the latest user
instruction, current authorization, and the parent Goal.

In Full Loop Mode, the current Task Ledger owns project lifecycle status, owner,
and revision. This frontmatter records the delegated contract workflow; any copied
lifecycle value is a derived projection of that Ledger, and the Ledger wins on
conflict. It does not become a competing authority.

The Worker MUST NOT change `parent_goal`, expand `scope.allowed`, weaken
`scope.forbidden`, grant authority, select its own Reviewer, or claim the parent
Goal is complete. Evidence MUST describe observed results rather than intended or
simulated outcomes.

Skill assignment transfers no authority. A Worker MUST NOT invent or install an
unavailable Skill, load a forbidden Skill, or treat Skill instructions as higher
priority than current platform, user, repository, or Task Contract constraints.

## Worker Submission

- Deliverables produced: Current preflight matrix, 21-entry evidence checksum manifest, original public captures, and candidate fact pointer in facts submission commit 461b9baeb15855d19b0a315edda5d6f083df6ddb (tree e2a5b41ac2433260a775f0400702c02126f45b59).
- Evidence observed: Fresh 1,141 tests passed; static validator, Skill check, compilation, 35 Mermaid renders, staged whitespace, evidence/index byte comparison and baseline ancestry checks passed. Full regression log SHA-256 is 15ff00438b0314f2c47050204c9ca8af45ae490692f5bb4e7b034eb388f99288.
- Risks or blockers: Actual provider/model/endpoint, formal loading/Hash B, complete isolation, trusted operator index, applicable Codex procedure and admissible behavior review remain unproven; formal arms remain NOT_RUN.
- Unfinished items: None within the facts-review task. Formal acceptance remains blocked and parent publication is tracked separately.
- Conflict notes: None.

## Review scope and authority

The independent Reviewer may read/search the task diff, normative sources, public captures and verification logs and run non-destructive local checks. It MUST NOT edit implementation or facts, alter configuration, install tools, commit, push, release, deploy, issue operator trust, or claim formal behavior review or parent completion. Only the parent acts under current user authority.

Research Brief RESEARCH-002 is in docs/release/rc1-preflight-20261024.md. No Skill is required for the Reviewer; base read/search/test tools suffice. No parallel implementation or parent Checklist is needed.

## Recorded independent decision

The Integrator records the Reviewer's actual decision for commit 461b9baeb15855d19b0a315edda5d6f083df6ddb: Standards pass, Spec pass, required evidence observed, overall approved; no unresolved substantive finding or required correction. This approval is bounded to facts, not formal behavior or parent completion. The original final response and the structured Review Result are archived with this task at delivery.

## Integration Evidence

The parent reran static validation, Skill validation and whitespace checks successfully after recording the actual review. All 21 evidence digests and the evidence manifest remain byte-identical to the approved facts commit. The original Reviewer text is retained as escaped JSON. An Integrator transcription omitted a comma from the template's mandatory authority sentence; the unchanged validator rejected that derived note, and restoring the exact template sentence passed. No original Reviewer judgment, protocol or validator was changed. The completed task/review/coordination records are archived before restoring neutral shipped state. Only fact preparation/review is integrated; the parent goal remains blocked on formal-acceptance prerequisites.
