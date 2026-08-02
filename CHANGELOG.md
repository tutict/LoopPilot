# Changelog

All notable changes to this project will be documented in this file.

The project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

- Added the v1.0 Release Candidate checklist under `docs/release/`, required it
  as a repository file, and stated that ticking the checklist is not acceptance.
  No gate is satisfied and no candidate version section is created.
- Rejected a canonical lifecycle assertion copied into a supporting `.looppilot/`
  artifact outside a declared projection or closure section, so a duplicated
  lifecycle value without source, boundary, and derived-status metadata is
  invalid rather than undocumented. Semantic staleness of undeclared prose
  remains Reviewer work.
- Declared Scenario ID, input boundary, evidence links, reviewer decision, and
  unverified limitations in the evaluation and Host Acceptance Record templates,
  and disclosed that the validator does not yet enforce the added fields.
- Separated README claims into Implemented, Observed, and Unverified, and listed
  every candidate host, including Claude Code, as explicitly unverified.

- Added a reference-host evaluation preparation note for Claude Code without
  claiming any observed acceptance, and required it as a repository file.
- Consolidated the changelog into a single Unreleased section with the
  document preamble at the top.

- Defined the Cross-Host Acceptance procedure, per-host verdicts, the inactive
  Host Acceptance Record template, and the v1.0 Release Candidate checklist
  inside the feature freeze, without verifying any host or preparing a release.
- Added public structural validation and regression cases for Host Acceptance
  Records, and fixed three checkpoint-recovery test helpers that pytest
  collected as module-level tests.

- Finalized Phase 11 lifecycle authority, derived projection, finite Closure
  assertion, backward-compatible validation, and governance-surface reduction rules.
- Corrected the Phase 11 validator from four-axis independent review: committed
  snapshots stay valid through ancestor Git boundaries, superseded Review rounds
  no longer block Closure, authority pointers are no longer flagged as competing
  authorities, the Finding assertion grammar matches the frozen ID pattern, the
  repository-wide forbidden-Ledger scan is restored, migration warnings print
  on failing runs, role-authority declarations stay outside lifecycle-file
  scope, and non-canonical Ledger IDs receive migration guidance instead of an
  unexplained failure.
- Added the public lifecycle consistency validator, focused regression fixtures,
  migration guidance, and semantic Reviewer boundary without adding a runtime,
  role, mode, Ledger, status, severity, Barrier, acceptance layer, or authority.
- Feature-froze the v1 core protocol for Cross-Host Acceptance and Release
  Candidate preparation.

- Added Phase 9 baseline attribution, Verification Surface inventory, Product Risk
  versus Coordination Necessity, specialist-reviewed Lightweight, delegation
  fallback, verifiable Worker claims, and artifact-category accounting.
- Added read-only Final-Assignment evidence with explicit EXP-006 control-archive
  and dynamic-holdout limitations, without claiming comparative completion.
- Added four Phase 9 documents, inactive template fields, static validation, more
  than 76 public-entry fixture cases, 30 scenarios, rubric dimensions, and four
  Mermaid diagrams without adding runtime state or authority.
- Calibrated Lightweight and Full Loop selection from four bounded MMGH
  experiments using explicit evidence levels and cross-project limitations.
- Added the pre-implementation Mode Gate, Lightweight Artifact Budget and
  escalation, Execution Infrastructure Incident classification, risk-loaded
  specialist Review, four load profiles, and evidence-selected architecture
  guidance without adding runtime state or authority.
- Added Phase 7 public validation, 76 distinct regressions, 40 scenarios, rubric
  dimensions, five Mermaid diagrams, and explicit Phase 6 through Phase 8 status.

### Added

- Initial LoopPilot skill instructions.
- Conceptual lifecycle, host capability, safety, and design documentation.
- Illustrative coding, research, and writing traces.
- Behavioral scenarios and a 0-to-3 evaluation rubric.
- Contributor guidance and MIT license.
- Repeatable static validation with pinned PyYAML and Mermaid CLI versions.
- A minimal GitHub Actions validation workflow.
- Evaluation templates for future observed host traces and A/B scoring.
- Repository-level Agent instructions in `AGENTS.md`.
- An optional `.looppilot/` shared-state and cross-session continuity protocol.
- Inactive state, handoff, and decision templates.
- Stale-state, prompt-injection, evidence-integrity, and authority safeguards.
- Shared-state validation and regression tests.
- An optional host-native supervised delegation protocol with Supervisor, Worker,
  Reviewer, and Integrator responsibilities.
- Task Contract, Reviewer result, and delegation-state templates.
- Task lifecycle, revision, conflict, parallel-eligibility, authority-isolation,
  and parent-integration rules.
- Delegation validation, regression tests, behavioral scenarios, rubric dimensions,
  and a rendered multi-Agent coordination diagram.

- Conditional Supervisor research preparation and a traceable Research Brief.
- Host-confirmed minimal Skill selection, assignment, fallback, and supply-chain
  boundaries in Task Contracts.
- Mandatory Standards and Spec review axes with conjunctive approval rules.
- A parent Goal Checklist with integrated-only checkmarks, context-pressure levels,
  exact Resume Points, and proactive budget-stop behavior.
- Static validation and 36 public-entry regression cases for Checklist, Research,
  Skill routing, and dual review behavior.

- A first-stage Loop Engineering architecture defining Project, Loop, Task,
  Delivery, Review, Finding, Integration, Commit, Closure, and Checkpoint
  relationships.
- An inactive Project Engineering Context template, Engineering Concern Matrix,
  architecture pattern guidance, protocol modes and state sources, Project Closure
  target, and six-phase Full Loop migration plan.
- Minimal architecture validation, 22 public-CLI regression cases, four focused
  Mermaid diagrams, 15 behavior scenarios, and 14 evaluation dimensions.

- Static Phase 2 templates for Project Loop Map, Loop Contract, Task Ledger, and
  Finding Ledger with compatible status enums and single-source invariants.
- Structural Full Loop validation, 65 public-entry regression cases, 18 behavioral
  scenarios, 14 rubric dimensions, and two focused Mermaid diagrams.
- Honest commit-authorization exceptions, closed-only Loop checkmarks, thin Ledger
  projections, and explicit Supervisor decision versus Integrator recording.

- Six inactive Phase 3 templates covering Worker Delivery, Integration Record,
  Review Report, Finding Detail, Rework Task, and Loop Closure.
- Static Task-level Readiness, integrated-outcome review, Finding triage and
  deduplication, scoped Rework, Reviewer reverification, three-layer Acceptance,
  commit honesty, and Checkpoint relationship rules.
- A modular Phase 3 validator, public-entry regression fixtures, delivery-to-closure
  scenarios and rubric dimensions, and four focused Mermaid diagrams.
- Three inactive Phase 4 templates for the authoritative Checkpoint, subordinate
  Context Compaction Manifest, and Resume Validation Report.
- Static qualitative context pressure, Budget Stop, Minimal Safe Unit, one exact
  Resume Point, stale correction, supersession, and intra-/inter-Loop recovery rules.
- A modular Phase 4 validator, 72 public-entry regression cases, 38 behavioral
  scenarios, 26 rubric dimensions, and five focused Mermaid diagrams.
- Four inactive Phase 5 templates for Cross-Loop Validation, Project Acceptance,
  Release Readiness, and the Final Delivery Report.
- Static Goal-to-Evidence Mapping, project-level dual review and three-layer
  acceptance, remediation Loop routing, independent release authority, a Project
  Closure Gate, and a terminal Final Checkpoint boundary.
- A modular Phase 5 validator with 130 public-entry regression cases, 40 behavioral
  scenarios, 35 rubric dimensions, and five focused Mermaid diagrams.

### Changed

- Refactored the Skill into a stronger host-native execution contract.
- Added loop invariants, proportional progress communication, and compact state rules.
- Defined Completed, Partially Completed, Blocked, and Budget Stop outcomes.
- Tightened activation exclusions, verification integrity, replanning, and authority.
- Expanded counterexample scenarios and explicit rubric penalties.
- Clarified that lifecycle and pseudocode names are conceptual, not fixed host APIs.
- Aligned the writing example so absent optional recovery guidance is not a blocker.
- Standardized normative `MUST`, `SHOULD`, and `MAY` language where behavior is
  required, recommended, or optional.
- Consolidated the unchanged-failure rule around one explicit Loop invariant.
