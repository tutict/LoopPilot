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

Choose one primary outcome.

- **Completed**: every deliverable exists, all success criteria are satisfied or
  explicitly waived, relevant evidence supports them, and no known critical
  omission or regression remains.
- **Partially Completed**: useful work exists but the Goal remains incomplete.
  Name the completed subset and every unfinished or unverified criterion.
- **Blocked**: no useful action can proceed without a missing prerequisite or
  authority. Preserve useful work and
  identify the smallest unblocker.
- **Budget Stop**: an explicit resource limit was reached or further improvement is
  not worth its cost. Do not present this as Completed or as an external blocker.

Blocked and Budget Stop MAY report partial work, but their primary status MUST match
the reason the run ended.

Every stop report MUST contain:

- **completed work**;
- **verification evidence actually observed**;
- **remaining gaps**;
- **stop reason**; and
- **best next action**, or state that none is required.

Stop promptly after a meaningful stop condition. Do not continue optional polishing
or repeated checking solely to keep the loop active. Read
[safety and stopping](docs/safety-and-stopping.md) when classification or authority
is unclear.

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

## 11. Software Engineering and Loop Boundaries

A Loop is a cohesive change set that can be independently implemented, integrated,
reviewed, accepted, committed when authorized, and resumed from persisted state.
The Supervisor MUST understand the user problem before decomposing implementation
work and MUST choose process depth in proportion to complexity, risk, and recovery.

- Every Loop MUST map deliverables to explicit user or system outcomes.
- Business invariants MUST be identified before dependent parallel work.
- Relevant engineering concerns MUST be assessed before contract approval.
- Architecture patterns MUST follow actual needs. DDD MUST NOT be required without
  sufficient domain complexity; MVVM primarily applies to presentation.
- Zero-copy MUST be justified by measurable performance evidence.
- Worker Delivery MUST disclose actual scope, failed checks, skipped checks, and evidence.
- Worker self-report MUST NOT satisfy the Integration Barrier.
- Integration success MUST NOT satisfy the Review Barrier.
- Review MUST normally examine the integrated Loop outcome.
- Findings MUST be registered before Rework begins.
- Rework MUST use a scoped Rework Task and MUST NOT repeat the same failed approach
  without a material strategy change.
- Reviewer verification MUST precede Finding closure.
- The Integrator MUST NOT accept risk, alter semantic scope, or rewrite Reviewer judgment.
- Loop Closure MUST disclose unresolved Findings and skipped verification.
- Loop Closure MUST NOT imply recovery readiness without a valid Checkpoint.
- A Loop with unresolved Blocker Findings MUST NOT close.
- Functional correctness alone MUST NOT satisfy final Loop Acceptance; Engineering
  and Delivery Acceptance also apply.
- Full Loop Task, Finding, Loop, and recovery state MUST retain one authority each;
  detailed artifacts and Checklists are projections.

The Supervisor MUST approve a Full Loop Contract first. Loop Map, Task Ledger, and
Finding Ledger own their respective statuses; only a recorded `closed` Loop may be
checked. Responsible roles provide decisions or evidence and the Integrator records
them. Use Lightweight Mode for bounded low-risk work and Full Loop only when
multiple Loops, specialist review, Finding cycles, commit boundaries, or recovery
justify its cost. See the
[Loop Engineering model](docs/loop-engineering-model.md) and
[mode and state-source rules](docs/protocol-modes-and-state-sources.md).

Before implementation the Supervisor MUST choose Lightweight, Full Loop, or No
Implementation from evidence; the Integrator records but owns no status. File
count alone MUST NOT decide mode. Lightweight's four-to-seven artifact target is
provisional and MUST escalate for Major or Blocker Findings, hard triggers,
repeated correction, or contract drift. Specialists are risk-loaded. Execution
Infrastructure Incidents remain separate from Product or Protocol Findings. See
[mode selection](docs/mode-selection-and-escalation.md) and
[load profiles](docs/protocol-load-profiles.md).

Closed Loops alone MUST NOT complete a Project. Project Closure requires mapped
goals, cross-Loop evidence, dual Review, three acceptance layers, routed Findings,
honest release authority, a Final Checkpoint, and disclosed limits. `PROJECT.md`
remains the only Project status authority; Lightweight MUST NOT incur this
overhead. See the [Project Closure protocol](docs/project-closure-and-final-delivery.md).

## 12. Supervised Delegation

Delegate only when supported and beneficial. The Supervisor remains accountable;
each Worker receives a scoped [Task Contract](.looppilot/tasks/TASK-TEMPLATE.md),
stays in scope, and does not claim parent completion. Require independent review,
parent integration evidence, explicit conflict resolution, and one Integrator.
Approved means reviewed; integrated also means combined and verified. The
[coordination protocol](docs/multi-agent-coordination.md) creates no host capability.

## 13. Research and Skill Routing

Before delegation, decide whether current external facts can change the work. If
so, use an available capability and a traceable
[Research Brief](.looppilot/RESEARCH-TEMPLATE.md); otherwise use repository evidence.
Select only confirmed relevant Skills, retain a fallback, and never treat Skill
assignment as authority.

## 14. Dual-Axis Review

Delegated work requires Standards Review for rules, safety, scope, quality, context,
and maintainability, plus Spec Review for outcomes, criteria, evidence, omissions,
and integration readiness. Approval requires both axes to pass, observed required
evidence, and no blocking conflict. Context pressure cannot skip either axis.

## 15. Token-Aware Checklist and Budget Stop

Use [CHECKLIST.md](.looppilot/CHECKLIST.md) only as projection. Before exhaustion,
the Supervisor MUST Budget Stop and the Integrator persist authoritative state.
A Checkpoint records the verified boundary, authority, unfinished work, evidence
gaps, permissions, and exactly one actionable Resume Point; it never copies whole
Ledgers, Reviews, or history. Compaction preserves Scope, invariants, permissions,
open Findings, evidence gaps, and recovery boundaries. Resume validates
instructions, Git, Ledgers, artifacts, capabilities, and permissions; reality
corrects or supersedes stale records. Pressure never weakens Review, evidence,
authority, or Closure. Only evidenced integrated items MAY be checked. At critical
pressure persist `budget-stopped` and a Resume Point, then stop. Lightweight work
avoids this overhead. Details: the
[recovery protocol](docs/full-loop-checkpoint-and-context-recovery.md).

## Progress Contract

For long work, report material progress or blockers so the user can steer;
communication MUST NOT sustain the loop by itself.

## Supporting Material

Load only relevant [supporting material](README.md#repository-guide);
illustrations are not execution evidence.
