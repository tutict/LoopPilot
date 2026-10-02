# Prompt

- Evaluation ID:
- Scenario ID:
- Variant: LoopPilot loaded | control
- Task fixture:

## Exact User Input

Evaluators MUST record the exact user-visible prompt and supplied artifacts and
MUST NOT add hidden expected answers or evaluator hints.

## Input Boundary

Record what was and was not supplied to the Agent: files, prior conversation,
loaded instructions, and available tools. Anything outside this boundary MUST
NOT be treated as available to the run when the trace is scored.

For new run packages, keep the section headings and blank-line separators shown
above. Preserve the exact scenario input, including its own headings, bullets and
edge whitespace. Validation locates the final Input Boundary section using the
hash-bound scenario input length, not a heading found inside user input. See the
[evidence integrity contract](../../docs/evaluation-evidence-integrity.md).
