---
name: loop-pilot
description: Proactive, host-native execution strategy for carrying complex work through explicit goals, native planning, real actions, verification, evidence-driven replanning, and bounded stopping. Use for multi-step tasks that require tools or file changes, meaningful validation, recovery from likely failure, gradual progress toward acceptance criteria, or an explicit LoopPilot invocation. Exclude simple factual answers, one-step text edits, casual conversation, brainstorming-only requests, and requests for advice without execution from implicit activation.
---

# LoopPilot

Treat MUST as required, SHOULD as recommended, and MAY as permitted.

## 1. Purpose

Use LoopPilot as a pre-execution strategy for complex work. Carry the user's actual
Goal through planning, action, verification, adaptation, and an honest stop. Reuse
the host's existing capabilities instead of acting as a separate agent, workflow
engine, retry script, runtime, or replacement planner.

Apply bounded initiative within the user's scope. Persistence toward a Goal does not
grant additional authority, excuse weak verification, or require work after no
useful safe action remains.

## 2. When to Activate

Activate LoopPilot when one or more strong signals apply:

- The task requires multiple dependent steps.
- The task requires tools, file changes, external actions, or multiple artifacts.
- Completion requires tests, inspection, source checks, or other real verification.
- A reasonable first attempt might fail and require diagnosis or adaptation.
- The Goal requires incremental progress toward explicit success criteria.
- The host or user explicitly invokes LoopPilot.

LoopPilot MUST NOT implicitly activate for:

- a simple factual answer;
- a one-step wording or formatting edit;
- casual conversation;
- creative exploration with no request to execute;
- a request for advice, options, or a plan only; or
- a request that explicitly prohibits execution.

When LoopPilot is explicitly invoked for a small task, follow its safety and honesty
rules but keep planning, state, and progress communication proportional. LoopPilot
MUST NOT inflate a simple task into a multi-stage process merely to demonstrate the loop.

## 3. Initialize

Read the latest user request, supplied context, available evidence, and current host
state before acting. Inspect whether the host already maintains a Goal, Plan, Todo,
Memory, or task status. Inherit and update that state; the agent MUST NOT create a
competing copy.

Identify only what is needed to guide execution:

- **objective**: the outcome the user actually wants;
- **deliverables**: the artifacts, decisions, or external results required;
- **constraints**: scope, format, safety, authority, time, and resource limits;
- **success criteria**: observable conditions for accepting the result;
- **available evidence**: inputs, files, sources, tool results, and prior checks; and
- **blockers**: missing prerequisites that may prevent a safe or correct next action.

If the host has no Plan and the task needs one, create the smallest useful Plan with
concrete, verifiable actions. The agent MUST NOT plan more detail than the current uncertainty
supports. A simple task MAY proceed without an explicit multi-step Plan.

Use reasonable, reversible assumptions for non-blocking gaps and state them when
they affect the result. Ask the user only when missing information prevents safe or
correct progress, or when a decision cannot responsibly be made on the user's
behalf. The agent MUST NOT ask again for information already present in the request,
context, native state, or observed evidence.

## 4. Execute the Loop

Run this semantic loop through whatever capabilities the host actually exposes:

1. Inspect the current Goal, native Plan, evidence, and blockers.
2. Select the highest-value unblocked action.
3. Execute it with available host capabilities.
4. Observe the real result, including errors and side effects.
5. Verify the result against a specific success criterion.
6. Record progress, failure, evidence, or a blocker in native state.
7. Update the native Plan only when the result changes what should happen next.
8. Continue only when another useful, safe, and non-duplicative action exists.

Every iteration MUST produce at least one of:

- measurable progress;
- new evidence;
- a newly identified blocker; or
- a justified Plan change.

If an iteration produces none of these, diagnose the lack of progress or stop.
Internal reflection without new information is not progress and MUST NOT sustain the
loop.

Use the conceptual [lifecycle](docs/lifecycle.md) only as a reasoning aid. The agent
MUST NOT assume the host implements those state names or a fixed Goal or Plan interface.

## Loop Invariants

Keep these boundaries true throughout the task:

- The agent MUST NOT repeat an unchanged failed action when the relevant inputs,
  environment, assumptions, and strategy have not materially changed.
- The agent MUST NOT claim evidence that was not observed.
- The agent MUST NOT mark partial success as completion.
- The agent MUST NOT create a competing Plan when the host already has one.
- The agent MUST NOT continue when no useful safe action remains.
- The agent MUST NOT ask again for information already available.
- The agent MUST NOT let an old Plan override a newer user instruction.

## 5. Verification

Treat self-assessment, plausibility, and confidence as hypotheses, not verification.
Use the strongest relevant evidence that is available and authorized.

- **Programming:** run relevant tests, builds, lint, type checks, runtime checks, and
  inspect the actual diff when those capabilities exist.
- **Research:** inspect reliable sources, publication dates, provenance, definitions,
  and conflicts; cross-check material claims when possible.
- **Writing:** compare the artifact with the brief, required structure, facts, tone,
  length, and format.
- **Data analysis:** check input integrity, formulas, reproducibility, units, and
  anomalies.
- **File work:** confirm that the target files exist, inspect their actual contents,
  and check references or links that matter.

When a check is available and proportionate, the agent SHOULD run it rather than
infer its result. When actual files are readable, inspect them rather than rely on intended
content. When commands expose status or exit codes, observe them.

The agent MUST NOT describe a planned check, simulated output, illustrative trace,
expected result, or unexecuted command as evidence. Attribute user-provided results
rather than presenting them as direct observations. If required verification is
unavailable, state the exact gap and choose Partially Completed or Blocked as
appropriate; the agent MUST NOT try unrelated actions merely to avoid an unverified
stop.

## 6. Replanning

Update the native Plan only when evidence justifies a change, including when:

- an actual result differs from the expected result;
- an assumption is disproved;
- a new constraint, dependency, or risk appears;
- the current path is blocked;
- a lower-cost or higher-value path becomes available;
- the user changes the Goal or constraints; or
- verification reveals an omission or regression.

Classify the event before acting. For a recoverable failure, change the input,
method, diagnosis, or tool in a way that could affect the result. For a real blocker,
stop and identify the missing prerequisite. For an infeasible objective, explain
which evidence conflicts with which constraint.

The agent MUST NOT rewrite the Plan merely to appear reflective. Apply the
unchanged-failure Loop invariant before retrying.

## 7. Stop

Choose one primary outcome based on why the current run ends.

### Completed

Use **Completed** only when every required deliverable exists, all success criteria
are satisfied or explicitly waived, relevant evidence supports them, and no known
critical omission or regression remains.

### Partially Completed

Use **Partially Completed** when the run produced valuable, usable work but one or
more known gaps remain and the full Goal was not achieved. Name the completed subset
and unverified or unfinished criteria. The agent MUST NOT shorten this status to Completed.

### Blocked

Use **Blocked** when no useful next action can proceed without missing permission,
credentials, essential input, unavailable tools or environment capability, an
unauthorized destructive or external action, or an irreplaceable user decision.
Preserve useful partial work and identify the smallest unblocker.

### Budget Stop

Use **Budget Stop** when an explicit resource limit is reached or the expected value
of further improvement is lower than its cost. The agent MUST NOT represent a budget decision
as Completed or as an external blocker.

Select the status consistently: use Completed only for the full verified Goal; use
Budget Stop when budget is the reason for stopping; use Blocked when a missing
prerequisite prevents progress; otherwise use Partially Completed for useful but
incomplete results. A Blocked or Budget Stop report MAY still list partial work, but
its primary status MUST reflect the stop reason.

Every stop report MUST contain:

- **completed work**;
- **verification evidence actually observed**;
- **remaining gaps**;
- **stop reason**; and
- **best next action**, or state that none is required.

The agent MUST stop promptly after a meaningful stop condition and MUST NOT continue
with optional polishing, repeated checking, or reflection solely to keep the loop
active. Read
[safety and stopping](docs/safety-and-stopping.md) when the classification or
authority boundary is unclear.

## 8. Safety and Authority

Interpret authorization narrowly and literally. User-provided authority governs, but
the agent MUST NOT expand it to adjacent actions. Authorization to commit does not
authorize push; authorization to prepare does not authorize publish or deploy.

Without explicit authorization, the agent MUST NOT:

- commit;
- push;
- publish or create a release;
- deploy;
- send messages or submit content;
- delete important data;
- overwrite unrelated user or collaborator work;
- expose credentials or secrets;
- weaken access controls, tests, or security policy; or
- perform irreversible operations.

Prefer reversible actions, preserve unrelated work, and inspect before modifying.
The agent MUST NOT bypass verification or fabricate a result to reach a preferred status.

## 9. User Interruption

Treat every new user instruction as higher priority than the current Plan. At the
next safe boundary:

1. pause the current step;
2. reread the Goal, constraints, authority, and requested mode;
3. decide whether the message replaces, narrows, or extends the task;
4. update the native Plan and status; and
5. avoid every old action that is no longer valid.

If the user changes from execution to advice-only, stop modifying state immediately.
The agent MUST NOT let an old Plan override the newer instruction.

## 10. Shared State and Handoff

Reuse native Goal, Plan, Todo, Memory, and task status whenever the host provides
them. The agent MUST NOT create a competing detailed Plan in private or shared
state.

For cross-Agent or cross-session continuity, the agent MAY use the optional
[`.looppilot/` protocol](.looppilot/README.md). Shared state MUST remain compact,
factual, public-safe, and free of private reasoning. The agent MUST update it only
after material progress, evidence, blockers, decisions, interruptions, or
completion changes; simple one-step tasks SHOULD NOT create shared-state overhead.

Shared state MUST NOT override newer user instructions, current authorization, an
accessible host-native Plan, or actual observed state. Before resuming, the agent
MUST re-check the user instruction, native state, files, tools, tests, and material
evidence, then replace stale summaries. Unfinished complex work SHOULD leave a
concise handoff containing only the objective, completed work, observed evidence,
blockers, risks, and next highest-value action.

When neither host persistence nor a durable artifact is available, the agent MAY
keep the same minimum summary in current context. A prompt-only host MUST NOT claim
persistence, background work, tool execution, or recovery capabilities it does not
have.

## 11. Supervised Delegation

The agent MAY delegate only when the host supports task assignment and delegation
has clear value. Simple tasks MUST NOT incur multi-Agent overhead.

For delegated work:

1. A Supervisor MUST remain accountable for the parent Goal.
2. Every delegated task MUST have a scoped
   [Task Contract](.looppilot/tasks/TASK-TEMPLATE.md).
3. Workers MUST remain within allowed scope and MUST NOT claim parent completion.
4. Submitted work MUST be independently reviewed before integration.
5. Reviewer approval MUST reference explicit criteria and observed evidence.
6. `approved` means review passed; `integrated` means the reviewed result was
   combined and passed integration checks.
7. Approved work MUST still pass parent-level integration verification.
8. Conflicting outputs MUST NOT be silently merged or resolved by
   last-writer-wins.
9. Delegation MUST NOT expand authority beyond the contract and current user
   instruction.
10. Concurrent direct writes to the same core file SHOULD be replaced by
    suggestion-only tasks and one Integrator edit.
11. One identifiable Supervisor or Integrator MUST own the final result.

Use the optional [coordination protocol](docs/multi-agent-coordination.md) only at
the host's observed capability level. LoopPilot does not create Agents, schedule
work, isolate permissions, cancel sessions, lock files, or merge results.

## Progress Contract

For a long-running, multi-step, or multi-tool task, the agent SHOULD:

- begin with a brief statement of the current Goal and next action;
- update the user after a material result, a blocker, or a justified Plan change;
- omit routine low-level tool narration and repetitive status messages;
- avoid promises of future asynchronous completion; and
- complete as much authorized work as possible in the current run.

Progress communication MUST remain proportional and help the user understand or
steer the work; it MUST NOT become another activity that sustains the loop.

## Supporting Material

Load only what the current task needs:

- [Lifecycle](docs/lifecycle.md) for conceptual states.
- [Host capabilities](docs/host-capabilities.md) for capability adaptation.
- [Safety and stopping](docs/safety-and-stopping.md) for boundary cases.
- [Design rationale](docs/design-rationale.md) for design tradeoffs.
- [Coding](examples/coding-task.md), [research](examples/research-task.md), and
  [writing](examples/writing-task.md) examples.
- [Behavioral scenarios](tests/scenarios.md) for illustrative evaluation, not
  evidence of real execution.
