# Changelog

All notable changes to this project will be documented in this file.

The project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
