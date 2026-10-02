---
name: loop-pilot
description: Carry a multi-step task through an execute-verify-adapt loop until the requested outcome is checked or a real blocker stops it. Use for checked multi-step non-coding work, implementation, diagnosis, or recovery that needs tools and evidence, or when the user explicitly invokes /loop-pilot or $loop-pilot. Do not use for factual answers, one-step edits, brainstorming, or advice-only requests.
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

Activate LoopPilot when the work has more than one dependent step and its result
must be checked, when a failed attempt needs diagnosis or recovery, or when the
user or host explicitly invokes LoopPilot with /loop-pilot or $loop-pilot. Checked
multi-step non-coding work includes research, writing, analysis, planning deliverables,
and information organization; advice-only planning remains excluded. A file change,
a test, or a database mention by itself is not a trigger. The managed short alias
resolves only to this same installed protocol, never a repository-local substitute.

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

Do not read every project document before the first action. Section 11 names the
document that owns each later concern. Within existing authorization, local, reversible, non-destructive
edits and checks with no external effects need no confirmation at each step.
This is not a grant of authority: host permissions, the Authorized Operation Set,
and applicable instruction and safety boundaries remain unchanged.

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

Run checks that can falsify the change. The agent MUST NOT scope out required verification
under applicable higher-priority instructions, repository rules, project requirements,
a Task Contract, or safety constraints. Only optional, objectively unrelated validation
may be scoped out using change/dependency evidence, not inconvenience or duration.
Disclose every skipped or scoped-down check as a verification gap: requirement status,
objective rationale, evidence, and residual uncertainty. Required checks that cannot
safely run remain unmet unless the proper authority explicitly waives them. When checks
are available and proportionate, prefer observation to inference; inspect actual files
and observe command exit codes.

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

- **Completed**: the requested outcome exists and the check that outcome needs
  was observed. A first draft is not completion when the user asked for the work
  to be done. Unrequested exploration is not completion either. Every deliverable
  exists, success criteria are satisfied or explicitly waived, and no known
  critical omission or regression remains.
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

## 11. Load Only the Concern You Are In

This file holds the decisions that apply to every run. Mode-specific procedure
stays in the document that owns it. Read that document when the concern applies.
Do not read the others for a routine edit.

| Concern | Read |
| --- | --- |
| Stopping or an authority edge case | [safety and stopping](docs/safety-and-stopping.md) |
| Loop shape, barriers, and acceptance layers | [Loop Engineering model](docs/loop-engineering-model.md) |
| Choosing Lightweight, Full Loop, or no implementation | [mode selection](docs/mode-selection-and-escalation.md) |
| Which file owns a lifecycle fact | [mode and state sources](docs/protocol-modes-and-state-sources.md) |
| Delegation, review, or integration | [coordination protocol](docs/multi-agent-coordination.md) |
| External facts that can change the work | [Research Brief](.looppilot/RESEARCH-TEMPLATE.md) |
| Context pressure, a Checkpoint, or resume | [recovery protocol](docs/full-loop-checkpoint-and-context-recovery.md) |
| Project completion or release readiness | [Project Closure protocol](docs/project-closure-and-final-delivery.md) |

Before implementation, the Supervisor chooses Lightweight, Full Loop, or No Implementation.
Product Risk determines review, validation, and evidence depth; Coordination Necessity
determines whether Full Loop is required. File count is not authority. Open the mode
document before choosing any mode and whenever escalation evidence appears. Bounded
non-coding work can be Lightweight, but real coordination need cannot be dismissed
because work is non-coding. A closed Loop does not complete a Project. Each lifecycle
fact has one authority; a copy is a projection. An execution-infrastructure failure
is not a product finding.

Delegate only when the host can do it and the split is cheaper than doing the
work. Assigning a Skill grants no authority. Delegated work needs both a
Standards Review and a Spec Review; context pressure cannot skip either. Use
[CHECKLIST.md](.looppilot/CHECKLIST.md) only for complex delegated work. Before
exhaustion, stop and persist one Resume Point. Lightweight work does not carry
that overhead.

## Progress Contract

For long work, report material progress or blockers so the user can steer;
communication MUST NOT sustain the loop by itself.

## Supporting Material

Load only relevant [supporting material](README.md#repository-guide);
illustrations are not execution evidence.
