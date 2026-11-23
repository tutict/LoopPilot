# RC Candidate Decision — v1.0.0-rc3

- RC version: v1.0.0-rc3
- Successor ID: OPTION-B-REFERENCE-2026-10-24
- Reference designation record: docs/release/rc-candidate-reference.md
- Reference Host: Codex
- Decision state: candidate-prepared-not-release-ready
- Decision date: 2026-11-22
- Gate 4: unmet
- Gate 5: all-named-candidates-recorded-or-disclosed-unverified
- Acceptance status: not-run
- Host/model identity status: unverified
- Release tag: not-created

The latest user accepted the Checkpoint repair candidate and authorized
application, synchronized installation, necessary local commits and four formal
arms on a new RC. The RC3 product baseline is 40f85debf7b59072cdd3b9a4fb446540299c0f36 with tree
799342167f450379908937b703a3a9fbac1f6f38. The designation was finalized and committed before the four formal sessions.
The sessions and packet review are recorded in the [execution evidence](rc3-formal-execution-20261123.md).
The machine-readable `Acceptance status` field reports that there is no qualified
acceptance decision under the current candidate-decision schema. The RC3-bound
[Host Acceptance Record](../../evaluations/codex/host-acceptance-record-rc3.md)
records `unverified`.

Fresh source maintenance passed 1,288 tests plus required follow-ups of 72, 134,
89 and 3 tests, without skips. Static/Skill/diff checks passed, 35 canonical Mermaid
sources rendered successfully, and 31 historical raw pins matched. Independent
source review passed all four scoped axes. These checks do not supply formal
behavior acceptance, independent package approval, upstream identity or remote CI.

The official USER install is CURRENT with 84 managed files matching the committed
source, C2_CLEAN and a verified nested alias binding. Native preparation and the
four model sessions are recorded with their observed outcomes. Relay-asserted identity and
suspected extra input context remain disclosed; upstream identity is UNVERIFIED.

RC2 keeps its frozen combination and prior observations, including its not-run
FL-1R. Prior replication data cannot be relabelled as this new RC3 run. Claude Code
remains an unverified Candidate Host; its historical replay stays not-reproduced.
Gate 4 remains unmet. No release tag, publication or deployment is authorized.
