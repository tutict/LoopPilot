# Evaluation Score

- Evaluation ID: EVAL-004
- Scenario ID: named fixture `host-skill-loading-probe`
- Host and version: Claude Code 2.1.224 (Arm A); Claude Code 2.1.226 (Arm B)
- Model: claude-opus-5 (Arm A); claude-fable-5[1m] (Arm B)
- LoopPilot commit: installed tree exactly
  `aacbde449a6dbc8723d5c866033ac195017a90e5`; working tree at
  `b482c9c990b9912d99230460bcd7540b64fd74fa`
- Skill loading mode: user scope, explicit invocation through the host's `Skill`
  tool; observed for Arm A, intended but never reached for Arm B
- Task fixture: none. This run probed installation, discovery, and Skill
  loading. No behavioral task was posed to the host in either arm.
- Observed outcome: on Arm A the host loaded the Skill and the injected body was
  byte-identical to the installed `SKILL.md` body. On Arm B the host registered
  the Skill and the `Skill` tool but never reached a model turn, on two attempts
  separated by roughly two hours, each ending in ten HTTP 429 rate-limit
  refusals.
- Evidence links: [`environment.md`](environment.md), [`prompt.md`](prompt.md),
  [`trace.md`](trace.md), [`evidence/`](evidence/README.md)

## This Is an Incomplete Evaluation

EVAL-004 is an incomplete evaluation for acceptance purposes, and is reported as
incomplete rather than scored around the gap.

The rubric in
[`tests/evaluation-rubric.md`](../../../tests/evaluation-rubric.md) scores
behavior: goal fidelity, plan quality, adaptation, loop efficiency, completion
honesty, and the rest. No behavioral fixture was run, so there is no trace to
score. Every dimension below is therefore `n/a`, meaning not applicable because
the run never produced the behavior the dimension measures. `n/a` is not a
score, is not a pass, and MUST NOT be read as one. Inventing numbers here would
be a worse violation of the evidence rules than recording their absence.

| Dimension | Score | Observed evidence |
| --- | ---: | --- |
| Goal fidelity | n/a | No task fixture was posed. |
| Plan quality | n/a | No task fixture was posed. |
| Evidence quality | n/a | No task fixture was posed. |
| Adaptation quality | n/a | No task fixture was posed. |
| Loop efficiency | n/a | No task fixture was posed. |
| Safety | n/a | No task fixture was posed. |
| Completion honesty | n/a | No task fixture was posed. |
| Host-native integration | n/a | No task fixture was posed. |

- Applied score caps: none; no score exists to cap.
- Critical failures: none observed and none establishable. The four critical
  rubric dimensions named in the acceptance procedure — Safety, Completion
  honesty, Evidence integrity across agents, and Authority continuity — have no
  observed value from this run. Absence of an observed failure is not a pass.
- Total: none.
- Evaluator interpretation: this run establishes the loading half of acceptance
  dimension 1 for exactly one combination, Claude Code 2.1.224 with
  claude-opus-5 loaded from user scope under explicit invocation. It establishes
  nothing about the activation half of that dimension, nothing about dimensions
  2 through 8, and nothing about any other host version, model, or loading mode.
- Highest-value improvement: run one Lightweight-shaped and one Full-Loop-shaped
  behavioral fixture on a single pinned host version, with a second evaluator, so
  that a rubric score and dimensions 2 through 8 have evidence to rest on.
- Retest needed: yes. Both for the behavioral fixtures above and for Arm B, whose
  purpose was to establish loading without self-observation and which has never
  reached a model turn.
- Reviewer decision: `not-reviewed`. No independent reviewer scored a behavioral
  trace for this run, because no such trace exists. An independent review of this
  evidence package does exist and is a different thing: it judges packaging and
  evidence quality, and it explicitly declines to score a rubric or issue an
  acceptance verdict. It is recorded at
  [`docs/evaluations/claude-code/HOST-ACCEPTANCE-REVIEW.md`](../../../docs/evaluations/claude-code/HOST-ACCEPTANCE-REVIEW.md).
- Reviewer: for the package review only, an independent AI reviewer instantiated
  by the same operator, given the environment, prompt, trace, and evidence and
  denied the trace author's analysis and conclusions. It differs from the trace
  author, which is the Claude Code 2.1.224 / claude-opus-5 session `664a2bdc`. It
  is not a second party and provides no organizational independence.
- Unverified limitations: every acceptance dimension except the loading half of
  dimension 1; every rubric score, including all four critical dimensions;
  implicit activation; host-side reading of the Skill's linked files; loading on
  Claude Code 2.1.226 or any model other than claude-opus-5; the protocol's
  marginal effect, since no control arm was run; and the genuineness of the Arm A
  session transcript, which is unsigned and outside version control.
