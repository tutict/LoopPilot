# Contributing to LoopPilot

Thank you for improving LoopPilot. Contributions should keep the project compact,
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
- Use `MUST` for requirements, `SHOULD` for recommendations, and `MAY` for
  permissions.
- Preserve host-native Goal and Plan behavior; do not add a competing planner.
- Require observed evidence for completion and use Completed, Partially Completed,
  Blocked, and Budget Stop consistently.
- Keep autonomy bounded by authorization, reversibility, and available evidence.
- Do not add runtime dependencies without a demonstrated need and prior discussion.
- Mark example traces as illustrative; never imply that fictional commands or
  searches were executed.
- Keep relative links valid and Markdown lint friendly.

## Testing Documentation Changes

Before submitting a change:

1. Check the relevant cases in [`tests/scenarios.md`](tests/scenarios.md).
2. Score the behavior with the
   [evaluation rubric](tests/evaluation-rubric.md) when semantics change.
3. Check activation exclusions, user interruptions, repeated-failure handling, and
   stop classifications when execution semantics change.
4. Inspect all changed Markdown and relative links.
5. Run an available Markdown linter if the environment already provides one.
6. Run `git diff --check`.

Include the checks actually performed and any unverified behavior in the change
description.

## Pull Requests

Keep pull requests focused. Explain the user-visible behavior change, the evidence
supporting it, and any compatibility or safety implications. A proposal does not
need to implement a host adapter unless it claims host-specific compatibility.
