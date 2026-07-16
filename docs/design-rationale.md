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

## Evidence Before Completion

Agent confidence is not external evidence. Verification changes by task type: tests
and diffs for code, provenance and source comparison for research, brief coverage
for writing, reproducible calculations for analysis, and content inspection for file
work.

Planned checks, simulated traces, expected outputs, and unexecuted commands remain
non-evidence. When direct verification is unavailable, the outcome must expose the
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
