# RC Candidate Decision — v1.0.0-rc1

- RC version: v1.0.0-rc1
- Successor ID: OPTION-B-REFERENCE-2026-10-24
- Reference designation record: docs/release/rc-candidate-reference.md
- Reference Host: Codex
- Decision state: candidate-prepared-not-release-ready
- Decision date: 2026-10-24
- Gate 4: unmet
- Gate 5: all-named-candidates-recorded-or-disclosed-unverified
- Acceptance status: not-run
- Host/model identity status: unverified
- Static validation status: passed-for-rc1-preflight-20261024
- Full regression status: passed-fresh-1141-tests-for-rc1-preflight-20261024
- Independent review status: approved-facts-submission-461b9ba; not-formal-behavior-review
- Release tag: not-created
- Historical candidate branch: `codex/option-b-rc-candidate`; merged by [PR #1](https://github.com/tutict/LoopPilot/pull/1) into `main` at `1191cad05056edab46fe4beb9fb8982549e4fad5`, then deleted remotely
- Installation-maintenance merge boundary: `main` at `5c4a52290de8e59527048e931f2334b06009c2c7`, after [PR #2](https://github.com/tutict/LoopPilot/pull/2) on 2026-10-25
- Current source and checks: [main](https://github.com/tutict/LoopPilot/tree/main) and [Validate CI](https://github.com/tutict/LoopPilot/actions/workflows/validate.yml?query=branch%3Amain)
- Latest preflight record: docs/release/rc1-preflight-20261024.md
- Facts review record: docs/release/rc1-preflight-review-20261024/REVIEW-TASK-002.md

This decision records RC candidate preparation. It does not record Host Acceptance,
does not satisfy Gate 4, and does not authorize a release tag, release publication,
deployment, or production traffic. The Reference designation is fixed separately
in the cited designation record; this file may be updated for candidate status only.
Historical RC decisions and Host Acceptance records are preserved unchanged.

The previous candidate export passed 1,141 tests on CPython 3.13.13 with no failures
or skips. The implementation, test, policy, template, and Gate files were compared
byte-for-byte with that export before committing. Final status records and the
neutral shared-state export receive static checks separately. Publication and the
exact effective commit are observed after commit creation; this preparatory record
does not predict a successful push. Formal Host Acceptance, installation Hash B,
and the applicable existing C2 preconditions remain unverified.

## Latest preflight facts

The [2026-10-24 preflight](rc1-preflight-20261024.md) records actual component
versions and installation checks. The existing live install is at `1bc184c…` and
reports `UPDATE_AVAILABLE` against `061ca98…`. A new temporary candidate install
reports `CURRENT`; both actually enumerated installed trees report `C2_CLEAN`.
The temporary install has not been selected as the formal loading surface.

Trusted actual provider/model/endpoint evidence and an independently approved
operator index remain unavailable. No expected Hash B binding or finalized
Codex arm/combination was established. The Reference remains Codex, formal arms
remain not run, and Gate 4 remains unmet. This task freshly passed 1,141 tests
and the required maintenance checks. Independent Standards/Spec review approved
actual facts submission `461b9baeb15855d19b0a315edda5d6f083df6ddb`; its original
response is preserved with the review. That approval is not formal behavior
review or Phase 11/Gate 6 closure. Publication is observed separately after the
final review/status archive commit exists.

## Subsequent maintenance facts

The 1,141-test preflight result above retains its 2026-10-24 date and facts-submission
boundary `461b9baeb15855d19b0a315edda5d6f083df6ddb`; it is not a test count for
current `main`. The separate [2026-10-25 maintenance record](rc-maintenance-verification-20261025.md)
attributes 1,163 tests and the native installation matrix to maintenance head
`c65d607d995c29e1d366716fdabd4064dae5c1f8`, merged by PR #2. Later maintenance
results do not change the original preflight facts, formal **NOT_RUN** acceptance,
Gate 4 **UNMET**, or RC **NOT_RELEASE_READY**.
