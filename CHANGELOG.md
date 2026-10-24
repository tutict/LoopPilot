# Changelog

All notable changes to this project will be documented in this file.

The project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1.0.0-rc1 — 2026-10-24 (development candidate; NOT_RELEASE_READY)

- Added the bounded `OPTION-B-REFERENCE-2026-10-24` successor: each applicable
  future RC chooses one Reference from Claude Code and Codex before formal arms.
  This RC chooses Codex; actual runtime identity and formal acceptance remain
  unverified. Gate 4 is unmet; no release tag or accepted RC is declared.
- Bound version-2 RC run receipts and accepted summaries to the committed
  designation, successor Git boundary, exact observed identity, public source
  events, and existing operator-approved review receipts. Version-1 non-RC
  packages remain supported; historical artifacts remain pinned and ineligible.
- Added public-entry positive/negative regressions and synchronized candidate
  records, templates, checklist, and validation documentation. Thresholds and
  Candidate disclosures are unchanged. Static PASS never substitutes for Host
  Acceptance, installation Hash B, or C2 isolation checks.

## Unreleased

- Recognized /lp, $lp, and $loop-pilot as explicit LoopPilot invocations, and added the installable short skill shortcuts/lp so a host can expose the /lp command without renaming the protocol skill.
- Routed mode-specific LoopPilot procedure out of the always-loaded skill body. SKILL.md now states the decisions that apply to every run and names the document that owns each later concern. Its description triggers on checked multi-step work, diagnosis, recovery, or an explicit invocation. AGENTS.md reads a document only for the concern it governs. Local reversible work inside the latest user request does not need stepwise confirmation; commit, push, release, deploy, deletion, and external messages still do.
- Added `scripts/c2_isolation_validation.py`, which enumerates an installed Skill
  directory and reports whether it carries acceptance material. It walks the
  whole tree rather than the managed-file manifest, never reads
  `.looppilot-installation`, and matches path suffixes to any depth, so a corpus
  preserved under `.looppilot-backups/<operation-id>/` is detected instead of
  being invisible to a destination-relative comparison. Measured on two real
  installations from one commit: a fresh install into an absent destination
  reports `CURRENT` and `C2_CLEAN`, while the same commit reached by upgrade
  reports `CURRENT` and `C2_CONTAMINATED` with 79 findings, all of them under a
  backup root. `status` reporting `CURRENT` is therefore not a sufficient
  condition for isolation — it quantifies over managed files, and the acceptance
  corpus is unmanaged — and the acceptance pre-flight now asserts both
  properties. No installer, manifest, or backup behavior changed.

- Narrowed the official distribution payload to the Skill runtime by enumerating
  `docs/` explicitly and dropping `evaluations/`, `tests/`, `scripts/`,
  `docs/release/`, `docs/evaluations/`, `docs/cross-host-acceptance.md`, and
  `requirements-dev.txt`, so an installed Skill carries no acceptance rubric,
  scenarios, verdict rules, or prior scores. The payload falls from 161 files to
  81; every `SKILL.md` and `AGENTS.md` relative reference still resolves, and two
  tests now assert both properties. Retiring the removed files is existing update
  behavior, so a customized copy is still preserved and reported rather than
  deleted. Documented residual: 17 links in `README.md`, `CONTRIBUTING.md`,
  `docs/installation.md`, and `docs/full-loop-migration-plan.md` point at
  material an installation no longer contains. They remain valid in the
  repository and were deliberately left unedited.
- Added the v1.0 Release Candidate checklist under `docs/release/`, required it
  as a repository file, and stated that ticking the checklist is not acceptance.
  No gate is ticked and no candidate version section is created.
- Corrected release-preparation wording to distinguish an unverified Host
  Acceptance Record from an accepted Host Acceptance Record.
- Extended the existing acceptance validator to require Host Acceptance Record
  `Scenario IDs` and `Unverified limitations` disclosures, with regression cases
  for missing fields and empty accepted-verdict disclosures.
- Added the two critical rubric rows, Evidence integrity across agents and Authority continuity, to `evaluations/templates/score.md`. No score was authored and no Release Candidate gate was ticked.
- Kept gitignored `.tmp/` validation artifacts outside the Markdown validation
  boundary so temporary traces and rendered sources cannot create repository
  findings.
- Rejected a canonical lifecycle assertion copied into a supporting `.looppilot/`
  artifact outside a declared projection or closure section, so a duplicated
  lifecycle value without source, boundary, and derived-status metadata is
  invalid rather than undocumented. Semantic staleness of undeclared prose
  remains Reviewer work.
- Declared Scenario ID, input boundary, evidence links, reviewer decision, and
  unverified limitations in the evaluation and Host Acceptance Record templates,
  with the existing validator enforcing the Host Acceptance Record disclosures.
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
