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
