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

## Shared-State Protocol Changes

Contributions MUST keep stable rules and dynamic task state separate:

- `AGENTS.md` MUST contain only durable repository instructions.
- `.looppilot/` templates MUST define the protocol without fictional active work.
- Contributors MUST NOT commit user credentials, sensitive state, private
  chain-of-thought, complete conversations, or fabricated evidence.
- Shared files MUST remain subordinate to the latest user instruction and the
  host-native Goal and Plan.

A change to the shared-state protocol MUST review and update, when affected:

- `SKILL.md` and `README.md`;
- `docs/validation.md` and `scripts/validate.py`;
- `tests/scenarios.md`; and
- `tests/evaluation-rubric.md`.

## Delegation Protocol Changes

A change to supervised delegation MUST review and update every affected layer:

- `SKILL.md` and `AGENTS.md`;
- `.looppilot/DELEGATION.md` and `.looppilot/tasks/`;
- `README.md` and `docs/multi-agent-coordination.md`;
- lifecycle, host-capability, safety, rationale, and validation docs;
- `scripts/validate.py`;
- regression tests;
- behavioral scenarios and the evaluation rubric; and
- CI Mermaid extraction and rendering.

Contributions MUST preserve the distinction between handoff and delegation,
`approved` and `integrated`, scoped responsibility and explicit authority, and
protocol guidance and real runtime isolation. They MUST NOT claim that LoopPilot
creates, schedules, cancels, isolates, or merges Agents unless a separately tested
host capability actually does so.

Changes to research, Skill routing, dual review, Checklist, budget stop, or resume
must also update their templates and public-entry validator fixtures. They MUST NOT
add web crawlers, Skill installers, token-count services, host scans, or claims of
real named-host compatibility.

## Loop Engineering Architecture Changes

Changes to the first-stage architecture must preserve Lightweight Mode, keep Full
Loop artifacts inactive until a later migration phase, and maintain one source of
truth per state type. Detailed semantics belong in the architecture documents;
SKILL.md, AGENTS.md, and README.md should carry only routing and invariant rules.

When changing the Project template, modes, object model, role boundaries, Reviewer
Matrix, Barriers, acceptance, or migration plan, update public-CLI regression tests
and validation documentation. Do not turn structural validation into a scheduler,
Finding engine, commit gate, or host-compatibility claim.

## Full Loop Template Changes

Changes to Loop Map, Loop Contract, Task Ledger, Finding Ledger, Phase 3 detail
templates, state enums, or authority rules must update the relevant modular
validator, public-entry tests, and protocol documentation together. Templates must
remain inactive and must not contain real users, Loops, Tasks, Findings, evidence,
or authority.

Keep Ledgers as compact status projections. Do not duplicate Delivery or Review
content, make Checklist authoritative in Full Loop Mode, weaken role boundaries for
fixtures, create active instances, or turn the Phase 3 static validator into a
workflow engine. Worker, Reviewer, Supervisor, and Integrator authority boundaries
must remain intact.

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
`python scripts/validate.py`. Render every extracted Mermaid diagram with the pinned
CLI as described in [`docs/validation.md`](docs/validation.md). These tools are not
LoopPilot runtime dependencies.

Include the checks actually performed and any unverified behavior in the change
description.

## Pull Requests

Keep pull requests focused. Explain the user-visible behavior change, the evidence
supporting it, and any compatibility or safety implications. A proposal does not
need to implement a host adapter unless it claims host-specific compatibility.
