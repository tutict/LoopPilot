# Observed Trace

- Evaluation ID:
- Variant: LoopPilot loaded | control

Record only user-visible or tool-visible events in order:

1. user input or interruption;
2. Agent-visible Goal or Plan summary, if exposed;
3. tool calls and observed results;
4. file or external-state changes;
5. tests, checks, and source evidence;
6. native task-status updates; and
7. final status and claims.

Evaluators MUST NOT request, reconstruct, or record private chain-of-thought. If an
event is not observable, they MUST mark it unavailable rather than infer it.
