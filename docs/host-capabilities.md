# Host Capability Levels

LoopPilot adapts to capabilities a host actually exposes. These levels describe
behavioral capacity, not certified product compatibility. LoopPilot MUST NOT infer support for a
named host unless a separate adapter and repeatable tests demonstrate it.

## Level 1: Prompt-Only Host

A prompt-only host has conversational context and text output but no native Plan,
tool execution, or durable task state.

LoopPilot can:

- make the Goal and success criteria explicit;
- apply action, evidence, and stop reasoning within the available context;
- ask the user to perform an external action and attribute the reported result; and
- produce a Completed, Partially Completed, Blocked, or Budget Stop report.

LoopPilot cannot reliably:

- execute external actions;
- directly verify evidence outside the conversation;
- preserve task state after context is lost;
- resume background work; or
- promise future asynchronous completion.

Keep any Plan short and proportional. When cross-context recovery is genuinely
needed, a compact text state MAY contain only the Goal, success criteria, completed
work, current action, blockers, and next action. Keep it in context unless the user
authorizes a durable artifact. The agent MUST NOT claim that this creates persistence the host
does not have.

## Level 2: Planning and Tool Host

A planning and tool host exposes a native Plan or task list plus file, command,
browser, application, or other tools.

LoopPilot SHOULD:

- inherit and update the native Goal, Plan, Todo, or task status;
- select actions from current native state;
- use actual tool results as direct execution evidence;
- run relevant verification through available tools;
- record blockers and verification gaps in the native representation; and
- replan there after failures, discoveries, or new user instructions.

LoopPilot MUST NOT mirror the Plan in a second private structure or invent generic
function names for reading Goals or updating Plans; use only verified host mechanisms.

## Level 3: Persistent Agent Host

A persistent host can retain Goals, Plans, Memory, task status, and resumable work
across execution windows.

LoopPilot SHOULD operate as a policy layer:

- reconcile new messages with persisted Goal and authority;
- resume from recorded evidence rather than replaying completed actions;
- update persistent Plan and outcome through native semantics;
- preserve provenance for verification and failures;
- communicate only material progress; and
- stop or resume according to capabilities the host actually supports.

LoopPilot MUST NOT duplicate persistence, Memory, scheduling, or recovery. Persistence does not
expand user authorization: commit, push, publish, deploy, sending, destructive
changes, and irreversible actions remain independently scoped.


## Shared-State Adaptation

The optional [shared-state protocol](../.looppilot/README.md) adapts to host
capabilities without replacing them:

- **Native state is sufficient:** the Agent SHOULD use the host Goal, Plan, Todo,
  memory, and resumable task state; `.looppilot/` is usually unnecessary.
- **A native Plan exists without durable recovery:** the Agent MAY write the minimum
  handoff needed to resume, while the native Plan remains authoritative.
- **The host is prompt-only or weakly stateful:** the Agent MAY keep a compact shared
  summary when the user and environment permit a durable artifact, but this does not
  create tools, scheduling, background execution, or reliable automatic recovery.

In every case, the receiving Agent MUST re-check the latest instruction, authority,
working tree, native state, and observed evidence before continuing.

## Capability Discovery

Before relying on a capability:

1. inspect the tools and state the host actually exposes;
2. distinguish documented behavior from inference;
3. select the lowest capability level clearly supported;
4. use direct evidence only when the host can actually observe it; and
5. downgrade gracefully when a tool or persistence feature is unavailable.

Prefer a truthful Level 1 adaptation over an unsupported Level 2 or Level 3 claim.
