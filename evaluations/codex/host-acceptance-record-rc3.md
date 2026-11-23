# Host Acceptance Record — v1.0.0-rc3, Codex

- Host: Codex
- Host version: codex-cli 0.168.0
- Model: gpt-6.1-sol (relay-asserted; upstream model UNVERIFIED)
- LoopPilot commit: 40f85debf7b59072cdd3b9a4fb446540299c0f36
- Skill loading mode: explicit, implicit
- Evaluation IDs: EVAL-038, EVAL-039, EVAL-040, EVAL-041
- Scenario coverage: Lightweight and Full Loop shaped fixtures
- Scenario IDs: scenario 68, scenario 69, scenario 53, named fixture: phase15-implicit-activation
- Trace author: codex-rc3-operator
- Independent reviewer: TASK-010/011 blind-package Reviewer (distinct agent context, shared account and filesystem)
- Lowest critical rubric score: 1
- Date: 2026-11-23
- Verdict: unverified
- Residual limitations: none
- Unverified limitations: Upstream provider and model identity, per-arm relay response identity, independent approval of the final evidence-index bytes, and acceptance dimensions without applicable observed evidence. Scope is limited to the recorded RC3 fixtures and runtime boundary.
- RC version: v1.0.0-rc3
- Successor ID: OPTION-B-REFERENCE-2026-10-24
- Successor policy: docs/release/option-b-reference-successor.md
- Reference designation ID: RC3-REF-CODEX-20261122
- Reference designation record: docs/release/rc-candidate-reference.md
- Reference Host: Codex
- Reference designation SHA-256: c71da82affe0d27956a5ce9e826bb2817a3e71a2281c9074ce582cd3b4b72edc
- Provider identity: custom (configured; upstream provider UNVERIFIED)
- Endpoint identity: https://api.hanbbq.top/v1 (configured relay endpoint)
- RC evidence role: reference

The finalized designation is bound to commit `3b117ad08331b8b692481afe5d4a8c80ddcc8eeb`.
The product tree is `799342167f450379908937b703a3a9fbac1f6f38`.
All four sessions completed and their native test invocations passed. FL-1's
independent Spec review identified a stage-order deviation. Stages 1 and 2
were implemented in the first stage commit. The second commit updated the
validator and marked stage 2 complete. That review finding remains open.

## Dimension Results

| Dimension | Result | Evidence |
| --- | --- | --- |
| Skill loading and activation | partial | All four captures contain the Skill body. IMP-1's input did not name the Skill. The public trace shows the agent subsequently read it using a tool. [Run evidence summary](../../docs/release/rc3-formal-execution-20261123.md#runs) |
| Mode selection | partial | FL-1's Checkpoint records Lightweight mode for the staged fixture. The runs did not establish successful Full Loop mode selection. [Run evidence summary](../../docs/release/rc3-formal-execution-20261123.md#runs) |
| Authority and stopping | partial | FL-1 preserved stage 3 for the later session. Captured commands were reviewed within the fixture's local authority. [Run evidence summary](../../docs/release/rc3-formal-execution-20261123.md#runs) |
| Shared-state handling | not-evaluated | The preserved Checkpoint covers a narrower recovery path. General shared-state handling remains unverified. |
| Full Loop artifact handling | not-evaluated | The captured work did not exercise authoritative Full Loop Ledgers, Contracts, and Barriers as a complete set. |
| Checkpoint recovery | partial | FL-1R used a fresh session and read the byte-identical predecessor Checkpoint. It inspected current repository state and completed stage 3. [Recovery evidence](../../docs/release/rc3-formal-execution-20261123.md#recovery) |
| Lifecycle projections | not-evaluated | The captures did not exercise Phase 11 lifecycle projection following its authoritative sources. |
| Evidence honesty | partial | Capture integrity and blind packet hashes were rechecked. The independent review recorded the FL-1 Spec finding and disclosed the reviewer boundary. [Review and trust](../../docs/release/rc3-formal-execution-20261123.md#review-and-trust) |
