# Contributing to LoopPilot

Thank you for improving LoopPilot. Contributions SHOULD keep the project compact,
host-neutral, evidence-based, and useful beyond programming tasks.

## Before Proposing a Change

1. Read [`SKILL.md`](SKILL.md) and the
   [design rationale](docs/design-rationale.md).
2. Identify the concrete failure mode or use case the change addresses.
3. Check whether the proposal belongs in the core skill or in supporting material.
4. Avoid host-specific API names unless the contribution includes a tested,
   clearly scoped adapter.

## Change Guidelines

- Keep instructions actionable and concise.
- Use `MUST`/`MUST NOT` for requirements and prohibitions, `SHOULD`/`SHOULD NOT`
  for recommendations, and `MAY` for permissions.
- Contributions MUST preserve host-native Goal and Plan behavior and MUST NOT add a
  competing planner.
- Completion claims MUST use observed evidence and classify Completed, Partially
  Completed, Blocked, and Budget Stop consistently.
- Keep autonomy bounded by authorization, reversibility, and available evidence.
- Runtime dependencies MUST NOT be added without demonstrated need and prior discussion.
- Example traces MUST be marked illustrative and MUST NOT imply that fictional
  commands or searches were executed.
- Keep relative links valid and Markdown lint friendly.

## Testing Documentation Changes

Before submitting a change:

1. Review the relevant cases in [`tests/scenarios.md`](tests/scenarios.md).
2. When an observed behavior trace exists, score it with the
   [evaluation rubric](tests/evaluation-rubric.md). Evaluators MUST NOT infer a score
   from specification prose or an illustrative trace.
3. Review activation exclusions, user interruptions, repeated-failure handling, and
   stop classifications when execution semantics change.
4. Inspect all changed Markdown and relative links.
5. Run an available Markdown linter if the environment already provides one.
6. Run `git diff --check`.

For the repository's repeatable maintenance checks, install the isolated development
dependency from `requirements-dev.txt`, run the Python unit tests, and run
`python scripts/validate.py`. Render both Mermaid diagrams with the pinned CLI as
described in [`docs/validation.md`](docs/validation.md). These tools are not
LoopPilot runtime dependencies.

Include the checks actually performed and any unverified behavior in the change
description.

## Pull Requests

Keep pull requests focused. Explain the user-visible behavior change, the evidence
supporting it, and any compatibility or safety implications. A proposal does not
need to implement a host adapter unless it claims host-specific compatibility.
