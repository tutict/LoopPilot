---
name: loop-pilot
description: Use when work has multiple dependent steps requiring verification (including implementation and multi-step non-coding work), when a failed attempt needs diagnosis or recovery, or when the user or host explicitly invokes /loop-pilot or $loop-pilot. Do not implicitly activate for simple factual answers, one-step wording or formatting edits, casual conversation, creative exploration with no request to execute, advice-only requests, or requests that prohibit execution.
---

# LoopPilot

Treat MUST as required, SHOULD as recommended, and MAY as permitted.

## 1. When to Activate

Activate LoopPilot when work has multiple dependent steps whose result must be
checked, when a failed attempt needs diagnosis or recovery, or when the user or host
explicitly invokes /loop-pilot or $loop-pilot. Checked multi-step non-coding work
includes research, writing, analysis, planning deliverables, and information
organization; advice-only planning remains excluded. A file change, test, or database
mention alone is not a trigger. The managed short alias resolves only to this
installed protocol, never a repository-local substitute.

LoopPilot MUST NOT implicitly activate for:

- a simple factual answer;
- a one-step wording or formatting edit;
- casual conversation;
- creative exploration with no request to execute;
- a request for advice, options, or a plan only; or
- a request that explicitly prohibits execution.

When explicitly invoked for a small task, keep planning, state, and progress
proportional; LoopPilot MUST NOT inflate a simple task into a multi-stage process
just to demonstrate the loop.

## 2. Purpose

Use LoopPilot as a pre-execution strategy for complex work. Carry the user's Goal
through planning, action, verification, adaptation, and an honest stop (section 7).
Reuse existing host capabilities instead of acting as a separate agent, workflow
engine, retry script, runtime, or replacement planner.

Apply bounded initiative within scope. Persistence never grants extra authority,
excuses weak verification, or justifies continuing when no useful safe action remains.

## 3. Initialize

Read the latest user request, supplied context, available evidence, and current host
state before acting. Reuse and update any existing host Goal, Plan, Todo, Memory, or
task status; the agent MUST NOT create a competing copy.

Do not read every project document before the first action; section 11 names the
document for each later concern. Within existing authorization, local, reversible,
non-destructive edits and checks with no external effects need no stepwise
confirmation. This is not a grant of authority: host permissions, the Authorized
Operation Set, and instruction or safety boundaries remain unchanged.

Identify only what is needed to execute:

- **objective**: the outcome the user wants;
- **deliverables**: required artifacts, decisions, or external results;
- **constraints**: scope, format, safety, authority, time, and resource limits;
- **success criteria**: observable acceptance conditions;
- **available evidence**: inputs, files, sources, tool results, and prior checks; and
- **blockers**: missing prerequisites blocking a safe or correct next step.

If the host has no Plan and the task needs one, create the smallest useful Plan with
concrete, verifiable actions. The agent MUST NOT plan beyond current uncertainty; a
simple task MAY proceed without a multi-step Plan.

Make reasonable, reversible assumptions for non-blocking gaps and state them when they
affect the result. Ask the user only when missing information blocks safe or correct
progress, or when a decision cannot responsibly be made on their behalf. The agent
MUST NOT ask again for information already present in the request, context, native
state, or observed evidence.

## 4. Execute the Loop

Run this loop through whatever capabilities the host actually exposes:

1. Inspect the Goal, native Plan, evidence, and blockers.
2. Select the highest-value unblocked action.
3. Execute it with available host capabilities.
4. Observe the real result, including errors and side effects.
5. Verify the result against a specific success criterion.
6. Record progress, failure, evidence, or blockers in native state.
7. Update the native Plan only when the result changes what happens next.
8. Continue only while another useful, safe, non-duplicative action exists.

Every iteration MUST produce measurable progress, new evidence, a new blocker, or a
justified Plan change. If none occurs, diagnose the stall or stop; internal reflection
without new information is not progress and MUST NOT sustain the loop.

Use the conceptual [lifecycle](docs/lifecycle.md) only as a reasoning aid. The agent
MUST NOT assume the host implements those state names or a fixed Goal or Plan
interface.

## Loop Invariants

Keep these boundaries true throughout the task:

- The agent MUST NOT repeat an unchanged failed action without a material change in
  inputs, environment, assumptions, or strategy.
- The agent MUST NOT claim unobserved evidence or mark partial success as completion.
- The agent MUST NOT create a competing Plan when the host already has one.
- The agent MUST NOT continue when no useful safe action remains.
- The agent MUST NOT ask again for information already available.
- The agent MUST NOT let an old Plan override a newer user instruction.
- The agent MUST NOT implement, commit, or fold later-stage deliverables into an
  earlier authorized stage.

## 5. Verification

Treat self-assessment, plausibility, and confidence as hypotheses, not verification.
Use the strongest available and authorized evidence.

- **Programming:** Run relevant available tests, builds, lint, type, and runtime
  checks, and inspect the diff. Report behavior separately from code quality. For code
  changes or required quality, review maintainability, APIs/types, error boundaries,
  complexity, and duplication against project conventions; tests alone do not
  establish quality. Avoid universal style rules or thresholds, and disclose
  unavailable quality checks.
  When tests conflict with an explicit user or project behavior contract, cite the
  governing source and verify a concrete case. Do not silently change implementation
  or tests just to make the suite green. Follow the authoritative contract, or stop
  and ask when the governing intent remains ambiguous.
  Before adding a guard, fallback, retry, exception handler, or state branch, name its
  requirement, contract, trust boundary, or concrete failure mode, scope it to that
  boundary, and preserve established behavior. Do not repeat already-enforced checks
  inside an unchanged trust boundary, catch and rethrow without cleanup, recovery, or
  useful context, mask failures or corrupted data with silent defaults lacking a
  degradation contract, or retry without stop limits and side-effect control. Retain
  necessary controls for security, data integrity, compatibility, concurrency, and
  partial-success risks.
- **Review:** Task, Loop, and Project Reviews record independent Spec, Standards,
  Implementation Quality, and Verification & Evidence decisions. Spec and Standards
  always apply. Implementation Quality applies to any produced or modified reviewable
  deliverable; Verification & Evidence applies when scope has a check, evidence, or
  completion claim. Only the latter two may be `not-applicable`, with cited scope or
  deliverable evidence; missing tools or evidence are gaps, not N/A reasons. Every
  applicable axis must pass; risk-based specialist review stays separate and cannot
  replace an axis.
- **Research:** Check reliable sources, dates, provenance, definitions, and conflicts;
  cross-check material claims when possible.
- **Writing:** Check the brief, structure, facts, tone, length, and format.
- **Data analysis:** Check input integrity, formulas, reproducibility, units, and
  anomalies.
- **File work:** Confirm target files exist, inspect actual contents, and check key
  references or links.

Run checks that can falsify the change. The agent MUST NOT scope out required
verification under applicable higher-priority instructions, repository rules, project
requirements, a Task Contract, or safety constraints. Only optional, objectively
unrelated validation may be scoped out using change/dependency evidence, not
inconvenience or duration. Disclose every skipped or scoped-down check as a
verification gap (requirement status, rationale, evidence, and residual uncertainty).
Required checks that cannot safely run stay unmet unless explicitly waived by proper
authority. Prefer direct observation (actual files and exit codes) over inference.

The agent MUST NOT present a planned check, simulated output, illustrative trace,
expected result, or unexecuted command as evidence. Attribute user-provided results
instead of reporting them as direct observations. If required verification is
unavailable, report the exact gap and choose Partially Completed or Blocked; the agent
MUST NOT run unrelated actions to avoid an unverified stop.

## 6. Replanning

Update the native Plan only when evidence justifies a change:

- actual results differ from expectations or an assumption is disproved;
- a new constraint, dependency, risk, blocker, omission, or regression appears;
- a lower-cost or higher-value path emerges; or
- the user changes the Goal or constraints.

Classify the event before acting. For a recoverable failure, change the input, method,
diagnosis, or tool so it can affect the outcome. For a real blocker, stop and name the
missing prerequisite. For an infeasible objective, state which evidence conflicts with
which constraint. The agent MUST NOT rewrite the Plan merely to appear reflective, and
MUST obey the unchanged-failure invariant before retrying.

## 7. Stop

Choose one primary outcome:

- **Completed**: every deliverable exists, required checks were observed, criteria are
  satisfied or explicitly waived, and no critical omission or regression remains. A
  first draft or unrequested exploration is not completion.
- **Partially Completed**: useful work exists, but the Goal is incomplete; name the
  completed subset and every unfinished or unverified criterion.
- **Blocked**: no useful action can proceed without a missing prerequisite or
  authority; preserve useful work and name the smallest unblocker.
- **Budget Stop**: an explicit resource limit was reached or further work is not worth
  its cost; never present this as Completed or as an external blocker.

Blocked and Budget Stop MAY report partial work, but the primary status MUST match the
actual stop reason. Every stop report MUST state:

- **completed work**;
- **verification evidence actually observed**;
- **remaining gaps**;
- **stop reason**; and
- **best next action** (or state none is required).

For an intentional later-session stop, the Supervisor/Integrator MUST persist root
`CHECKPOINT.md` using the [mode-specific contract](docs/full-loop-checkpoint-and-context-recovery.md#intentional-session-stops).
Read [safety and stopping](docs/safety-and-stopping.md) when classification or
authority is unclear.

## 8. Safety and Authority

Interpret authorization narrowly and literally; the agent MUST NOT expand it to
adjacent actions (commit does not authorize push; prepare does not authorize publish
or deploy). For staged or multi-loop work, deliver and commit only the currently
authorized stage; keep later-stage files, interfaces, and behavior untouched until
authorized, and disclose pending downstream checks rather than absorbing future stages
to turn a full suite green.

Without explicit authorization, the agent MUST NOT:

- commit, push, publish, create a release, or deploy;
- send external messages or submit external content;
- delete important data or overwrite unrelated user or collaborator work;
- expose credentials or secrets;
- weaken access controls, tests, or security policy; or
- perform irreversible operations.

Prefer reversible actions, preserve unrelated work, and inspect before modifying. The
agent MUST NOT bypass verification or fabricate results to reach a preferred status.

## 9. User Interruption

Treat every new user instruction as higher priority than the current Plan. At the next
safe boundary:

1. pause the current step;
2. reread the Goal, constraints, authority, and requested mode;
3. decide whether the message replaces, narrows, or extends the task;
4. update the native Plan and status; and
5. drop every old action that is no longer valid.

If the user switches from execution to advice-only, stop modifying state immediately.

## 10. Shared State and Handoff

Defer to native Goal, Plan, Todo, Memory, and task status; the agent MUST NOT create a
competing detailed Plan in private or shared state.

For cross-Agent or cross-session continuity, the agent MAY use the optional
[`.looppilot/` protocol](.looppilot/README.md). Keep shared state compact, factual,
public-safe, and free of private reasoning. Update it only after material progress,
evidence, blockers, decisions, interruptions, or completion changes; simple one-step
tasks SHOULD NOT add shared-state overhead.

Shared state MUST NOT override newer user instructions, current authorization, an
accessible native Plan, or observed state. Before resuming, read root `CHECKPOINT.md`
when present, re-check current instructions, native state, files, tools, tests, and
evidence, then replace stale summaries. Unfinished complex work SHOULD leave a concise
handoff of objective, completed work, evidence, blockers, risks, and next action.

Without host persistence or durable artifacts, keep the same minimum summary in
current context. A prompt-only host MUST NOT claim persistence, background work, tool
execution, or recovery capabilities it lacks.

## 11. Load Only the Concern You Are In

This file holds the decisions that apply to every run. Mode-specific procedure stays
in its owning document; read it only when that concern applies.

| Concern | Read |
| --- | --- |
| Stopping or an authority edge case | [safety and stopping](docs/safety-and-stopping.md) |
| Loop shape, barriers, and acceptance layers | [Loop Engineering model](docs/loop-engineering-model.md) |
| Choosing Lightweight, Full Loop, or no implementation | [mode selection](docs/mode-selection-and-escalation.md) |
| Which file owns a lifecycle fact | [mode and state sources](docs/protocol-modes-and-state-sources.md) |
| Delegation, review, or integration | [coordination protocol](docs/multi-agent-coordination.md) |
| External facts that can change the work | [Research Brief](.looppilot/RESEARCH-TEMPLATE.md) |
| Context pressure, an intentional session stop, a Checkpoint, or resume | [recovery protocol](docs/full-loop-checkpoint-and-context-recovery.md) |
| Project completion or release readiness | [Project Closure protocol](docs/project-closure-and-final-delivery.md) |
| Cross-task Skill evolution | [Skill evolution process](docs/skill-evolution.md) |

Cross-task Skill evolution is separate from in-task replanning. The agent MUST NOT
modify the active Skill during the task; follow the [Skill evolution process](docs/skill-evolution.md)
only at the task boundary.

Before implementation, the Supervisor chooses Lightweight, Full Loop, or No
Implementation. Product Risk determines review, validation, and evidence depth;
Coordination Necessity determines whether Full Loop is required. File count is not
authority. Open the mode document before choosing any mode and whenever escalation
evidence appears. Bounded non-coding work can be Lightweight, but real coordination
need cannot be dismissed because work is non-coding. A closed Loop does not complete a
Project. Each lifecycle fact has one authority; a copy is a projection. An
execution-infrastructure failure is not a product finding.

Delegate only when the host supports it and the split is cheaper than doing the work.
Assigning a Skill grants no authority. Delegated work needs all four Review axes under
their applicability rules; context pressure cannot skip an applicable axis. Use
[CHECKLIST.md](.looppilot/CHECKLIST.md) only for complex delegated work. Before
exhaustion, stop and persist one Resume Point; Lightweight work does not carry that
overhead.

## Progress Contract

For long work, report material progress or blockers so the user can steer;
communication MUST NOT sustain the loop by itself.

## Supporting Material

Load only relevant [supporting material](README.md#repository-guide); illustrations are
not execution evidence.
