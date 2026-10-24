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
- Static validation status: passed-at-reviewed-candidate-export
- Full regression status: passed-1141-tests-at-reviewed-candidate-export
- Independent review status: passed-standards-and-spec-for-candidate-implementation
- Release tag: not-created
- Remote branch: codex/option-b-rc-candidate; publication result recorded separately

This decision records RC candidate preparation. It does not record Host Acceptance,
does not satisfy Gate 4, and does not authorize a release tag, release publication,
deployment, or production traffic. The Reference designation is fixed separately
in the cited designation record; this file may be updated for candidate status only.
Historical RC decisions and Host Acceptance records are preserved unchanged.

The full candidate export passed 1,141 tests on CPython 3.13.13 with no failures
or skips. The implementation, test, policy, template, and Gate files were compared
byte-for-byte with that export before committing. Final status records and the
neutral shared-state export receive static checks separately. Publication and the
exact effective commit are observed after commit creation; this preparatory record
does not predict a successful push. Formal Host Acceptance, installation Hash B,
and the applicable existing C2 preconditions remain unverified.
