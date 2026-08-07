# LoopPilot Installation Validation

This document defines the Distribution-001 verification boundary. It validates
packaging behavior only. It does not validate host loading, agent behavior, Host
Acceptance, protocol effectiveness, or release readiness.

## Verification Method

`tests/test_distribution.py` creates isolated source-package fixtures with valid
version and commit metadata, invokes the existing distribution entry points, and
checks destination files, installation state, backups, and process results. The
fixtures exercise a manifest change between two source versions without modifying
protocol files in the repository.

Repository validation continues to use the existing validators. Distribution-001
adds no validator.

## Required Scenarios

| Scenario | Verification |
|---|---|
| Fresh install | All manifest files are copied, user files remain, state is created, and output prints version and commit. |
| Reinstall | An identical installation reports `reinstall (no changes)` without changing user content. |
| Upgrade | Unmodified files update, new files appear, retired unmodified files are removed, version and commit advance, and backups are retained. |
| Customized upgrade | Modified managed files and colliding user files are preserved by default and marked customized; force update backs them up before replacement. |
| Uninstall | Only matching, non-customized files recorded by state are removed; user and modified files remain. |
| Broken installation detection | Install detects an existing state whose payload differs and directs the user to update; update repairs a missing managed file. |
| Missing source detection | A manifest entry absent from the source package stops installation before destination writes. |
| Version mismatch detection | A valid old source version is handled as an upgrade; malformed or incomplete installed version metadata is rejected. |
| Manifest migration | Added and retired managed files are processed from old state without requiring an identical manifest hash. |
| Path safety | Non-regular managed paths and symbolic-link or reparse-point traversal are rejected before managed deletion or replacement. |

## Commands

PowerShell parser and native lifecycle tests:

```powershell
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile(
  (Resolve-Path 'distribution\loop-pilot.ps1'),
  [ref]$null,
  [ref]$errors
) | Out-Null
if ($errors.Count) { throw $errors }

py -3.13 -m unittest tests.test_distribution -q
```

Bash syntax and lifecycle tests on a Bash-capable system:

```bash
bash -n install.sh update.sh uninstall.sh distribution/loop-pilot.sh
python -m unittest tests.test_distribution -q
```

Existing repository checks:

```powershell
py -3.13 scripts\validate.py
py -3.13 -m unittest tests.test_validate -q
git diff --check
```

## Observed Results

The result table must contain only commands observed against the current working
tree. A parser pass does not substitute for lifecycle execution, and a native-shell
pass does not establish behavior on another shell.

| Check | Environment | Status | Evidence |
|---|---|---|---|
| PowerShell parser | Windows PowerShell | PASS | Observed after the complete Distribution-001 change set. |
| PowerShell lifecycle scenarios | Windows PowerShell | PASS | `tests.test_distribution`: 6/6 passed; live repository install, update, uninstall, and self-uninstall also completed. |
| Bash syntax | Git Bash or POSIX Bash | UNVERIFIED | The current sandbox denied Bash process initialization before parsing began. |
| Bash lifecycle scenarios | Git Bash or POSIX Bash | UNVERIFIED | No Bash lifecycle execution has completed in the current environment. |
| Existing static validator | Python 3.13 | PASS | `py -3.13 scripts\\validate.py` printed `Static validation passed`. |
| Validator regression tests | Python 3.13 | PASS | `tests.test_validate`: 2/2 passed; the focused cross-host suite remains environment-blocked by temporary-directory permissions. |
| Diff whitespace check | Git | PASS | `git diff --check` completed with exit code 0; Git emitted only existing LF/CRLF normalization warnings. |

The full repository discovery command was also attempted. It discovered 868 tests;
861 failed before assertions because this Windows environment denied creation and
cleanup of temporary fixture directories (`WinError 5`). A rerun outside the
sandbox was requested but the approval service returned `503 Service Unavailable`.
This is an execution-environment limitation, not evidence that those tests pass.

Any remaining `PENDING`, `UNVERIFIED`, or failed row must be reported honestly in
the Distribution-001 completion summary.
