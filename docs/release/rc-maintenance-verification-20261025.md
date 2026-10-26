# RC Maintenance Verification — 2026-10-25

This record summarizes the packaging-maintenance verification that followed the
merged Option B candidate on 2026-10-25. It is a dated maintenance fact record, not formal Host
Acceptance, a Gate 4 decision, or release authority.

## Git and workflow boundary

| Item | Observed value |
| --- | --- |
| Maintenance merge into `main` | `5c4a52290de8e59527048e931f2334b06009c2c7` |
| Reviewed maintenance head | `c65d607d995c29e1d366716fdabd4064dae5c1f8` |
| Reviewed tree | `a4d86dc0fa2dc6bd6cc1fe980c01edda10965e6d` |
| Actual PR checkout recorded by installation artifacts | `3e9aeacf034059e5e81e9d865ff2bdc484493068`; tree `a4d86dc0fa2dc6bd6cc1fe980c01edda10965e6d` |
| Pull request | [PR #2](https://github.com/tutict/LoopPilot/pull/2) |
| Ubuntu workflow | [run 40171417400](https://github.com/tutict/LoopPilot/actions/runs/40171417400) |
| Push workflow | [run 40171414788](https://github.com/tutict/LoopPilot/actions/runs/40171414788) |

The maintenance head was merged into `main`. The PR workflow's `headSha` names
`c65d607…`; its installation artifacts record the actual PR checkout `3e9aeac…`
with the same tree. These are distinct Git identities. Results below are attributed
to the PR workflow and its artifacts; the push run is a separate observation.
The workflow pages link the generated job artifacts; this summary records only the
observed counts and boundaries needed by the candidate record.

## Observed maintenance results

| Environment | Actual tools recorded | Result |
| --- | --- | --- |
| Ubuntu Linux x86_64 | Python 3.12.15; `/opt/microsoft/powershell/7/pwsh` 7.6.6; `/usr/bin/bash` 5.2.21 | Full repository suite: 1,163 tests passed; required follow-up suites (72, 130, 89, and 1) passed; 35 Mermaid diagrams rendered. |
| Windows Server 2025 AMD64 / Windows PowerShell 5.1 | Python 3.12.10; Windows PowerShell 5.1.26100.33648; Git Bash 5.3.15 | 117 installation tests passed, zero failures/errors/skips; eight official lifecycle operations passed; 83 managed files checked. |
| Windows Server 2025 AMD64 / PowerShell 7 | Python 3.12.10; PowerShell 7.6.7; Git Bash 5.3.15 | 117 installation tests passed, zero failures/errors/skips; eight official lifecycle operations passed; 83 managed files checked. |
| macOS 15.7.9 arm64 | Python 3.12.10; `/bin/bash` 3.2.57; PowerShell 7.6.5 | 117 installation tests passed, zero failures/errors/skips; eight official lifecycle operations passed; 83 managed files checked. |

Required shell skips were zero in every installation row. These results cover the
recorded operating systems, architectures, executable paths, and versions only; they
do not generalize to other hosts or architectures. The checks are packaging and
repository-maintenance evidence, not behavior evidence for Codex or another AI host.

## Evidence sources

The Ubuntu full-suite count and follow-up counts come from the `validate` job log
of run 40171417400. The 117-test counts, tool versions, eight lifecycle operations,
83 managed files, and exact payload checks come from each artifact's `result.json`:

- [installation-ubuntu](https://github.com/tutict/LoopPilot/actions/runs/40171417400/artifacts/12590772022)
- [installation-windows-powershell-5](https://github.com/tutict/LoopPilot/actions/runs/40171417400/artifacts/12591340364)
- [installation-windows-powershell-7](https://github.com/tutict/LoopPilot/actions/runs/40171417400/artifacts/12590283206)
- [installation-macos-system-bash](https://github.com/tutict/LoopPilot/actions/runs/40171417400/artifacts/12590252272)

The artifacts and logs were re-read on 2026-10-26. Their file digests and PASS rows
are packaging-maintenance evidence, with no operator trust or formal Host Acceptance.
The earlier [1,141-test preflight](rc1-preflight-20261024.md) remains attributed to
2026-10-24 and its original facts-submission boundary.

## Acceptance boundary

- Reference Host remains **Codex** under `OPTION-B-REFERENCE-2026-10-24`.
- Formal acceptance remains **NOT_RUN**.
- Gate 4 remains **UNMET**.
- RC candidate status remains **NOT_RELEASE_READY**.
- No release tag or GitHub Release was created by this maintenance verification.
