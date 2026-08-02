# Evaluation Preparation

This directory prepares reproducible LoopPilot host evaluations. It contains no
evaluation results and makes no compatibility claim.

For each run, copy the templates and record:

- Host and Host version;
- Model;
- LoopPilot version or commit;
- Skill loading mode;
- Scenario ID and task fixture;
- exact prompt and input boundary;
- observable trace and evidence links;
- observed outcome;
- rubric score;
- reviewer decision; and
- evaluator notes and unverified limitations.

A run whose Scenario ID, evidence links, reviewer decision, or unverified
limitations are missing is an incomplete evaluation, not a weaker result. Report
it as incomplete rather than scoring around the gap.

Evaluators MUST keep observations separate from interpretation and preserve
user-visible and tool-visible evidence. They MUST NOT request or record private
chain-of-thought and MUST score each observed trace with [`tests/evaluation-rubric.md`](../tests/evaluation-rubric.md).

For an A/B comparison, evaluators SHOULD keep the task fixture, host, model, authority,
and available tools constant. They SHOULD change only whether and how LoopPilot is
loaded and MUST report both runs even when either run fails.
