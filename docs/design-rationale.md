# Design Rationale

LoopPilot is deliberately small: a proactive execution policy expressed in Markdown,
with no runtime, service, CLI, or separate orchestration layer.

## Goal-Driven, Not Iteration-Driven

A fixed retry count measures attempts rather than progress. LoopPilot ties every
iteration to the user's Goal and observable success criteria. An iteration is useful
only when it advances the Goal, adds evidence, identifies a blocker, or justifies a
Plan change. Reflection and status narration cannot keep the loop alive by
themselves.

## Host-Native, Not a Second Planner

Hosts differ in how they expose Goals, Plans, tools, and persistence. A universal
second planner would duplicate state and create synchronization failures. LoopPilot
therefore specifies semantics and reuses verified native capabilities without
inventing common APIs.

When no native Plan exists, a minimal task-local Plan is enough. When no persistence
exists, compact state may help within available context, but it cannot manufacture
durable recovery or background work.


## Static Rules, Dynamic State

LoopPilot does not use one large `CLAUDE.md`-style file for both permanent rules and
current task history. [`AGENTS.md`](../AGENTS.md) holds stable repository
instructions, while [`.looppilot/`](../.looppilot/README.md) provides optional,
minimal task-local continuity.

The separation matches their different lifecycles: stable rules change through
reviewed repository edits, while task state expires as work, evidence, instructions,
and authority change. Keeping them separate reduces merge conflicts and context
growth, makes each change easier to audit, and prevents an old task or handoff from
polluting a new task.

## Supervision, Review, and Integration

Delegation creates a new failure mode: every contributor can finish a local part
while no one owns the correctness of the whole. LoopPilot therefore keeps one
Supervisor accountable for the parent Goal and one identifiable Supervisor or
Integrator accountable for the final combined result.

A handoff is not sufficient. Handoff transfers compact continuity to a later Agent;
delegation creates bounded responsibility under a still-active parent Goal. A Task
Contract is needed because the Worker requires explicit scope, deliverables,
evidence, dependencies, Reviewer, integration owner, and authority.

Independent Review and integration are separate gates. `approved` establishes that
one subtask satisfies its contract. `integrated` establishes that reviewed work
coexists with other outputs and passes parent-level verification. Keeping the
statuses separate exposes conflicts and combined regressions that no isolated
review can detect.

LoopPilot defines this as a protocol rather than an automatic multi-Agent runtime.
Hosts differ in assignment, parallelism, cancellation, persistence, permission
isolation, and merge behavior. A repository runtime would duplicate host
orchestration, introduce new security boundaries, and falsely imply compatibility.
The protocol instead adapts to observed host capabilities and states the remaining
runtime limits.

## Research, Skill Routing, and Dual Review

Research belongs with the Supervisor because shared, current source work can shape
task boundaries before Workers duplicate effort. A traceable brief lets Workers
reuse findings while preserving source authority, version differences, conflicts,
and the boundary between external evidence and local verification. Research remains
conditional so a well-specified local task does not create browsing ceremony.

Only confirmed available Skills may be assigned because a universal registry would
be another fictional runtime contract. Selecting the smallest relevant set reduces
supply-chain exposure and context growth. Recording unavailable, forbidden, and
fallback options makes absence explicit without installing anything or granting
authority.

Standards and Spec review answer different questions: whether the work obeys the
system's constraints, and whether it solves the contracted problem. Keeping both
axes explicit prevents strong functional output from masking unsafe or
unmaintainable work, and prevents polished standards compliance from masking a
missing requirement.

## Checklist and Proactive Budget Stop

The parent Checklist is not a second Plan. The native Plan stays dynamic and
detailed; the Checklist stores only stable deliverables, integration state,
evidence, pressure, and one Resume Point. Restricting `[x]` to integrated work keeps
Reviewer approval distinct from parent completion.

A proactive budget stop preserves recoverability before the host forces a context
loss. Qualitative pressure works across hosts that expose different or no token
signals. Stopping early is a controlled pause, never permission to weaken review,
evidence, success criteria, authority, or completion honesty.

## Engineering Context Before Decomposition

A file-oriented split can hide shared invariants, data contracts, permissions, and
operational risks. Loop boundaries therefore follow user outcomes, business
cohesion, dependencies, integration risk, and recoverability. The
[Project Engineering Context](project-engineering-context.md) makes those inputs
explicit before Task decomposition.

The protocol has two depths. Lightweight Mode protects simple work from ceremony.
Full Loop Mode is reserved for work whose risk and recovery needs justify contracts,
Ledgers, Findings, Closure, and Checkpoint artifacts. Architecture patterns are
selected by fitness; none is a universal compliance target.
## Evidence Before Completion

Agent confidence is not external evidence. Verification changes by task type: tests
and diffs for code, provenance and source comparison for research, brief coverage
for writing, reproducible calculations for analysis, and content inspection for file
work.

Planned checks, simulated traces, expected outputs, and unexecuted commands remain
non-evidence. When direct verification is unavailable, the outcome MUST expose the
gap rather than convert confidence into completion.

## Adaptive, Not Mechanically Persistent

Failures can reveal incorrect assumptions, new constraints, or a poor path.
LoopPilot replans only when such evidence changes what should happen next. Rewriting
a Plan merely to appear reflective wastes context and hides stagnation. Repeated
unchanged failure requires new evidence, a materially different strategy, or a stop.

## Four Honest Outcomes

Completed is reserved for the full verified Goal. Partially Completed preserves
valuable incomplete work without overstating it. Blocked identifies a missing
prerequisite. Budget Stop records a resource or diminishing-return boundary. These
outcomes separate work quality from the reason execution ended.

## Bounded Authority

"Continue until done" is a persistence requirement, not unlimited permission.
Commit, push, publish, deploy, sending, destructive changes, credential handling,
and irreversible actions remain independently authorized. New user instructions
override old Plans.

## Broad Task Coverage

The core loop avoids programming-specific syntax. Domain examples show how evidence
changes across coding, research, and writing while Goal, Plan, action, verification,
replanning, and stop semantics remain stable.

## Progressive Disclosure

The executable rules stay in [SKILL.md](../SKILL.md). Lifecycle, capability, safety,
examples, and evaluation material live in separate files loaded only when relevant.
This keeps the triggered Skill focused while preserving inspectable rationale.

## Conceptual Models, Not Interface Contracts

Lifecycle state names and README pseudocode provide shared vocabulary for evaluation.
A host does not need those labels, transitions, functions, or storage fields.
Behavioral equivalence matters more than representation.

## Thin Ledgers and One Authority

Full Loop Ledgers are deliberately narrow. The Loop Map stores Loop projection,
Task Ledger stores Task projection, and Finding Ledger stores Finding projection;
Contracts, Deliveries, Reviews, Finding Detail, Rework Tasks, and Closure retain richer content and
evidence. This prevents the same status from drifting across files and avoids
turning Markdown into a workflow database.

Task-level Readiness is deliberately narrower than Loop-level Review. Integration
records what was combined and which checks ran; it does not prove the outcome meets
the Spec or Standards. Likewise, Closure summarizes acceptance but cannot own Loop
status. These separations keep bookkeeping from becoming business judgment.

A separate Contract Status avoids copying Loop lifecycle state. Supervisor decisions
and Integrator recording remain separate so factual bookkeeping cannot silently
become scope change, risk acceptance, or authority expansion. Lightweight Mode
avoids all Ledger ceremony when recovery value does not justify it.

## Minimal Recovery Index

Checkpoint is separated from Commit and Closure because each answers a different
question: code fact boundary, accepted outcome, and recovery entry. Keeping only one
Checkpoint authority prevents Handoff, Checklist, Manifest, and Resume Report from
drifting into competing state. A Manifest is separate because context selection may
change without changing recovery status; a Resume Report is separate because
validation evidence should not silently rewrite the entry it evaluates.

Qualitative pressure avoids dependence on fictional token APIs. Stopping at a
Minimal Safe Unit protects honesty under pressure without weakening Review or
Acceptance. Exact Resume Points trade a little structure for cross-context
actionability, while Lightweight Mode avoids that cost when recovery has no value.
