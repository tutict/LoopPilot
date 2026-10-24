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
- Independent review status: pending-for-rc1-preflight-facts
- Release tag: not-created
- Remote branch: codex/option-b-rc-candidate; publication result recorded separately
- Latest preflight record: docs/release/rc1-preflight-20261024.md

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
remain not run, and Gate 4 remains unmet. Fresh verification and fact review are
required for this update; the earlier implementation review is not reused as
formal behavior review or Phase 11/Gate 6 closure.
