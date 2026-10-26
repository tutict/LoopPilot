# LoopPilot Distribution-003 Report

## Scope

Distribution-003 closes the executable Bash gap where evidence permits and creates
a bounded real-host loading probe. It does not change protocol design or semantics,
create a Release Candidate, tag, release, or authorize a push.

- Observed date: 2026-08-07
- Overall result: `PARTIALLY VERIFIED`
- Installation source commit: `a4c83f8b3ce90f6e388cf32b398a4d01667f9b66`
- Source version: `unreleased`
- Protocol status: frozen and unchanged

## Environment

| Component | Observed value |
|---|---|
| Operating system | Microsoft Windows NT 10.0.26200.0 |
| Windows PowerShell | 5.1.26100.8972 |
| Python | 3.13.13 |
| Git | 2.51.0.windows.1 |
| Git Bash | 5.2.37(1)-release, x86_64-pc-msys |
| Claude Code | 2.1.223 |

## Installation Source

Acceptance used `.tmp/distribution-003-source-20260807`, a detached worktree at
`a4c83f8` with only these current Distribution-002.1 corrections overlaid:

- `distribution/managed-files.txt`
- `docs/installation.md`
- `INSTALLATION-VALIDATION.md`
- `tests/test_distribution.py`

This is a patched-source test boundary, not a claim that those corrections already
had a new commit during execution.

## Commands

The directly executed command families were:

```text
Git Bash --version and bash -n
Git Bash install.sh, update.sh, and installed uninstall.sh
Independent manifest, state, and SHA-256 assertions
LoopPilot PowerShell install into isolated Claude Code Skill directories
claude.exe --version and auth status
Claude Code stream-json initialization and bounded Skill/Read probes
Installed scripts/validate.py --root <installed-skill>
python scripts/validate.py
python -m unittest discover -s tests -p "test_*.py"
git diff --check
```

Exact installation paths and command forms are recorded in
`DISTRIBUTION-BASH-VALIDATION.md` and the Claude Code distribution load record.

## Distribution-003-A Result

| Area | Result | Evidence summary |
|---|---|---|
| Git Bash availability | PASS outside sandbox | Bash 5.2.37 returned version information. |
| Syntax | PASS | All Bash distribution scripts parsed. |
| Fresh install | PASS | 126 managed files and 126 state rows; 0 set, presence, or SHA-256 differences. |
| Update | PASS | Customized README preserved and marked `|1`; one matching backup created. |
| Uninstall | PASS | State and unmodified managed files removed; customized README, user file, and backup preserved. |

D002-F02 is closed for the observed Git Bash environment. WSL, Linux, macOS, and
other Bash implementations remain unverified.

## Distribution-003-B Result

Claude Code is the repository's reference host, but no host currently has an
accepted support claim.

| Area | Result | Evidence summary |
|---|---|---|
| Installed structure | PASS | Required Skill and supporting files existed. |
| Host discovery | PASS | Claude Code 2.1.223 initialization listed the isolated `loop-pilot` Skill and slash command. |
| Skill content load | UNVERIFIED | No Skill tool event occurred before service failure. |
| Static reference resolution | PASS | Installed existing validator passed. |
| Host reference read | UNVERIFIED | No Read tool event occurred. |

D002-F03 is partially addressed: real host discovery is observed, while content
loading and host-executed reference resolution remain unverified. No Host
Acceptance verdict changed.

## Failed Attempts and Classification

| ID | Classification | Observed failure | Impact |
|---|---|---|---|
| D003-EII-001 | Execution Infrastructure Incident | Git Bash inside sandbox failed before parsing with `Win32 error 5`. | Resolved for this audit by approved outside-sandbox execution. |
| D003-EII-002 | Execution Infrastructure Incident | WSL enumeration returned `E_ACCESSDENIED`. | WSL remains unverified. |
| D003-HCG-001 | Host Configuration Gap | Isolated Claude config was not logged in. | Discovery remained observable; model-driven loading was unavailable there. |
| D003-EII-003 | Execution Infrastructure Incident | Authenticated Claude call inside sandbox ended with certificate verification failure. | Same command reached the service outside sandbox. |
| D003-HCU-001 | Host Capability Unverified | Outside-sandbox Claude call exhausted ten HTTP 429 retries. | Skill and Read tool execution remain unverified. |

No failed attempt produced evidence of a Product Regression or LoopPilot protocol
defect.

## Repository Validation

Repository validation is recorded after the final Distribution-003 change set.

| Command | Result | Classification |
|---|---|---|
| `python scripts/validate.py` | FAIL: default `python` was GraalPy 3.12.8 without PyYAML. | Execution Infrastructure Incident; import stopped before repository validation. |
| `python -m unittest discover -s tests -p "test_*.py"` | FAIL/STOPPED: repeated dependency failures under the same GraalPy environment. | Execution Infrastructure Incident; not a completed product test result. |
| `py -3.13 scripts/validate.py` | PASS: `Static validation passed`. | No Product Regression. |
| `py -3.13 -m unittest discover -s tests -p "test_*.py"` inside sandbox | FAIL: 870 discovered, 861 temporary-directory `WinError 5` errors, 9 passes. | Execution Infrastructure Incident; errors occurred before assertions. |
| Same CPython discovery outside sandbox | PASS: 870/870 in 795.054 seconds. | No Product Regression. |
| `git diff --check` | PASS with only line-ending normalization warnings. | No whitespace regression. |

The outside-sandbox CPython result is the complete product-regression check. It
does not erase the failed default-interpreter or sandbox attempts; all three
boundaries remain recorded.

## Remaining Unverified

- Claude Code Skill content load and host-executed supporting-reference reads on
  2.1.223.
- Accepted Host Acceptance for Claude Code or any other host.
- WSL, Linux, macOS, and non-MSYS Bash lifecycle behavior.
- Distribution auto-detection against a live host profile.
- Remote CI behavior, RC creation, release, tag, and push.

## RC Gate Impact

Distribution-003 adds verified Git Bash lifecycle evidence and real Claude Code
discovery evidence. It does not satisfy independent Host Acceptance, authorize RC
preparation, or alter the current release gate. Host content loading remains an
explicit blocker for any claim that requires it.

## Conclusion

Distribution-003-A is verified on Git Bash 5.2.37. Distribution-003-B is partial:
discovery is observed, but content loading and host-level reference reads remain
unverified because the authenticated host service did not complete a model turn.
The overall result is `PARTIALLY VERIFIED` with no protocol change.
