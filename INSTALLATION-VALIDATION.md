# LoopPilot Installation Validation

This document defines the Distribution-001 verification boundary and records later
distribution corrections through Distribution-003. It validates packaging behavior
only. It does not validate agent behavior, Host Acceptance, protocol effectiveness,
or release readiness.

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
| Fresh install | All manifest files are copied, user files remain, state is created, output prints version and commit, and the installed existing validator passes against the installed root. |
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

Installed-package validation after a fresh install:

```powershell
py -3.13 <destination>\scripts\validate.py --root <destination>
```

This command must use the validator copied into the installation. A missing
required file, including `.github/workflows/validate.yml`, is an installation
failure rather than a validator exception.

## Observed Results

The result table must contain only commands observed against the current working
tree. A parser pass does not substitute for lifecycle execution, and a native-shell
pass does not establish behavior on another shell.

| Check | Environment | Status | Evidence |
|---|---|---|---|
| PowerShell parser | Windows PowerShell | PASS | Observed after the complete Distribution-001 change set. |
| PowerShell lifecycle scenarios | Windows PowerShell | PASS | `tests.test_distribution`: 7/7 passed after Distribution-002.1; live repository install, update, uninstall, and self-uninstall also completed. |
| Bash syntax | Git Bash 5.2.37 on Windows | PASS | All three Bash wrappers and `distribution/loop-pilot.sh` parsed successfully outside the restrictive sandbox. The sandbox-only `Win32 error 5` remains recorded as an Execution Infrastructure Incident. |
| Bash lifecycle scenarios | Git Bash 5.2.37 on Windows | PASS | Distribution-003 observed fresh install, 126-file manifest/state/hash integrity, customization preservation, backup creation, self-uninstall, user-content preservation, and state cleanup. |
| Installed existing validator | Windows PowerShell and Python 3.13 | PASS | A fresh isolated Distribution-002.1 installation included `.github/workflows/validate.yml`; its copied validator printed `Static validation passed`. |
| Existing static validator | Python 3.13 | PASS | `py -3.13 scripts\\validate.py` printed `Static validation passed`. |
| Full repository tests | CPython 3.13 | PASS | The approved outside-sandbox run completed 870/870 tests in 795.054 seconds. The normal sandbox run had 861 pre-assertion temporary-directory permission errors and 9 passes. |
| Diff whitespace check | Git | PASS | `git diff --check` completed with exit code 0; Git emitted only existing LF/CRLF normalization warnings. |

The user-requested `python` command resolved to GraalPy 3.12.8 without PyYAML.
`python scripts/validate.py` therefore stopped at import with
`ModuleNotFoundError: No module named 'yaml'`; its full discovery run was stopped
after repeated instances of the same dependency failure. These are execution
environment results, not product failures. CPython 3.13 supplied the repository's
declared dependency and provided the complete passing suite above.

Any remaining `PENDING`, `UNVERIFIED`, or failed row must be reported honestly in
the applicable distribution completion summary. Git Bash evidence does not imply
Linux, macOS, WSL, or another Bash implementation was tested.
