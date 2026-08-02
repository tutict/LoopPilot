# Final Protocol Calibration

Phase 11 calibrates the v1 protocol candidate from existing behavioral evidence. It
does not start another product experiment or treat experiment reports as universal
proof. The initial repository boundary is
`2275e747e73936ebb8f0b24e5fb901a619b6adf8`.

## Scope

The permitted protocol changes are limited to lifecycle authority, derived
projections, closure-relevant lifecycle assertions, closure consistency, and
removal of duplicated mutable lifecycle values. Roles, modes, Ledgers, status and
severity vocabularies, Barriers, acceptance layers, and Recovery authority remain
frozen.

## Evidence Classification

### Observed

- EXP-008 reported `BLOCKED-WITH-VERIFIED-PARTIAL-DELIVERY`: a product-valid
  partial delivery whose Full Loop Closure was `NOT-CLOSEABLE`, with stale
  lifecycle projections among its governance problems. Its reported
  approximately 71 governance files and 4,709 lines describe that archived
  experiment; they are not a general protocol cost constant.
- EXP-009 reported `RECOVERY-ACCEPTED-WITH-DISCLOSED-RESIDUALS` and contradicted
  the claim that correct membership, hashes, and counts are sufficient for
  current lifecycle values.
- GamePulse EXP-010 lives in a separate local experiment repository, not in
  LoopPilot, at commit `6b075fc1606c0cc3fb47a6a3592b2bef28e6dcaf`. Its product
  boundary passed 35 test files and 100 tests plus typecheck and build, while
  independent Standards review reopened lifecycle drift; the archived verdict is
  `BLOCKED-WITH-VERIFIED-PARTIAL-DELIVERY` with
  `FINAL FULL LOOP BEHAVIORAL ACCEPTANCE: FAIL`.

The EXP-008 and EXP-009 statements above are attributed to their archived
experiment reports supplied for Phase 11. The EXP-010 statements were also checked
against the local GamePulse experiment artifacts. None proves cross-host behavior.

### Repeated Pattern

Across EXP-008, EXP-009, and the different GamePulse project in EXP-010, mutable
lifecycle values copied into supporting artifacts became stale or remained stale
after membership-oriented correction. This is evidence of a repeated stale
projection risk when the same lifecycle fact is manually owned in several files.
It is no longer treated as an isolated documentation mistake. It does not imply
that every Full Loop will drift.

### Provisional Heuristic

- Lightweight's four-to-seven Governance Artifact target remains a cost heuristic.
- The default budget of two unsuccessful Worker attempts remains provisional.
- Ownership collapse remains behaviorally under-exercised.
- Governance surface reduction is supported as a direction, but minimum file count
  is not an acceptance rule.

### Normative Invariant

- Each lifecycle fact has one authoritative source.
- Project, Loop, Task, Finding, and Recovery authority remain in `PROJECT.md`,
  `LOOP-MAP.md`, `TASK-LEDGER.md`, `FINDING-LEDGER.md`, and `CHECKPOINT.md`.
- Supporting artifacts cannot override authoritative state.
- Functional success cannot replace Engineering and Delivery Acceptance.
- Commit, acceptance, release readiness, release, and deployment remain distinct.

### Unverified

- Universal protocol correctness and longitudinal governance behavior.
- Behavioral acceptance on any host, including the Claude Code reference host as
  well as Codex, Gemini CLI, GitHub Copilot, and others.
- Automatic lifecycle reconciliation, Finding creation, or state mutation.
- Production release and deployment behavior.

## Calibration Evidence Table

| Rule | EXP-008 | EXP-009 | EXP-010 | Classification |
|---|---|---|---|---|
| Single lifecycle authority | tension in copied projections | supported by recovery comparison | tension after product-green integration | repeated-pattern-backed calibration |
| Fixed membership sufficient | contradicted by stale values | contradicted by F-001 | insufficient for closure consistency | rejected |
| Derived projections | needed to reduce copied ownership | needed after membership recovery | needed across Handoff and recovery summaries | calibrated rule |
| Lifecycle assertions | retrospectively useful | need shown by post-recovery drift | need shown at multiple barriers | calibrated closure check; statically implemented, behaviorally unverified |
| New Ledger required | no evidence | no evidence | no evidence | rejected |
| Full Loop model redesign | unsupported | unsupported | unsupported | rejected |
| Governance surface reduction | tension | supported directionally | tension recurred; no surface measurement recorded | provisional and supported direction |

## Calibration Decision

LoopPilot v1 protocol candidate incorporates repeated cross-project evidence that
lifecycle state should remain single-authority and supporting artifacts should be
treated as derived projections whose closure-relevant values are checked for
consistency. Lifecycle Assertions are a finite validation view, not a Ledger,
status, Barrier, acceptance layer, or runtime.

Large-scale protocol experimentation stops after Phase 11. If validation and
independent review pass, the next phase is Cross-Host Acceptance and Release
Candidate preparation, not EXP-011.
