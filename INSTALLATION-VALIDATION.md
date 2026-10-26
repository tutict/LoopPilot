# LoopPilot Installation Validation

This document defines the Distribution-001 verification boundary and records later
distribution corrections through Distribution-004. It validates packaging behavior
only. It does not validate agent behavior, Host Acceptance, protocol effectiveness,
or release readiness.

## Current Verification Entry Points

Use the [installation guide](docs/installation.md) for current managed-layout and
lifecycle instructions, and the [validation guide](docs/validation.md) for the full
maintenance checks. The [Validate workflow](https://github.com/tutict/LoopPilot/actions/workflows/validate.yml?query=branch%3Amain)
runs the Ubuntu workflow and Windows PowerShell 5.1/7 and macOS installation matrix.
Select the run for the commit being checked and inspect its `installation-ubuntu`,
`installation-windows-powershell-5`, `installation-windows-powershell-7`, and
`installation-macos-system-bash` artifacts. Missing shells, skips, failures, and
unavailable artifacts are verification gaps, never PASS.

The Required Scenarios and Distribution-004 Synchronization Scenarios below retain
the lifecycle constraints. Observed Results, Distribution Evidence Lineage, and the
recorded commands preserve the original Distribution-001 through Distribution-004
execution boundaries; their counts, installed-file lists, limitations, and
environments are historical results. In particular, the historical copied-validator
scenario describes an older payload: the current manifest excludes `scripts/`,
`tests/`, and acceptance material, as explained in the installation guide.
The source-only [archive index](https://github.com/tutict/LoopPilot/blob/main/docs/archive/README.md)
maps the old report names, and the separate
[2026-10-25 maintenance record](https://github.com/tutict/LoopPilot/blob/main/docs/release/rc-maintenance-verification-20261025.md)
records later cross-platform checks. Historical PASS or UNVERIFIED rows do not
describe a later commit or replace its required verification.

## Verification Method

`tests/test_distribution.py` creates isolated source-package fixtures with valid
version and commit metadata, invokes the existing distribution entry points, and
checks destination files, installation state, backups, and process results. The
fixtures exercise a manifest change between two source versions without modifying
protocol files in the repository.

Distribution-004 runs its synchronization suite against both shipped
implementations. Every scenario in the Distribution-004 table below executes once
through `distribution/loop-pilot.ps1` and once through `distribution/loop-pilot.sh`,
as a `subTest` per shell, so a divergence between them fails the suite rather than
going unnoticed. A shell that is genuinely unavailable is skipped and reported as
skipped, never as a pass.

Repository validation continues to use the existing validators. Distribution-001
adds no validator, and neither does Distribution-004.

## Required Scenarios

| Scenario | Verification |
|---|---|
| Fresh install | All manifest files are copied, user files remain, state is created, output prints version and commit, and the installed existing validator passes against the installed root. |
| Reinstall | An identical installation reports `reinstall (no changes)` without changing user content. |
| Upgrade | Unmodified files update, new files appear, retired unmodified files are removed, version and commit advance, and backups are retained. |
| Customized upgrade | Modified managed files are preserved by default and marked customized; force update backs them up before replacement. |
| Uninstall | Only matching, non-customized files recorded by state are removed; user and modified files remain. |
| Broken installation detection | Install detects an existing state whose payload differs and directs the user to update; update repairs a missing managed file. |
| Missing source detection | A manifest entry absent from the source package stops installation before destination writes. |
| Version mismatch detection | A valid old source version is handled as an upgrade; malformed or incomplete installed version metadata is rejected. |
| Manifest migration | Added and retired managed files are processed from old state without requiring an identical manifest hash. |
| Path safety | Non-regular managed paths and symbolic-link or reparse-point traversal are rejected before managed deletion or replacement. |

## Distribution-004 Synchronization Scenarios

Each row runs against PowerShell and Bash.

| Scenario | Expected | Verification |
|---|---|---|
| Identical repository and installation | `CURRENT` | `status` reports `CURRENT` with zero pending actions immediately after install. |
| Repository changed, local untouched | `UPDATE_AVAILABLE`, then a successful update | `status` reports the state, the changed revision and manifest, and the per-file `UPDATE`, `ADD`, and `REMOVE` actions; the update applies them and returns to `CURRENT`. |
| Local customization only | `LOCAL_MODIFICATIONS` | A file edited locally while upstream is unchanged is reported as locally modified, not as an update. |
| Repository and local both modified | `CONFLICT` | Reported as a conflict; the update refuses, names the file, changes no managed file, and leaves the recorded version untouched. |
| Repository adds a managed file | Installed automatically | A newly managed file absent locally is copied and its hash recorded. |
| Repository removes an unchanged managed file | Removed safely | A retired file matching its baseline is backed up and deleted. |
| Repository removes a customized file | Customization preserved | A retired file that differs from its baseline is backed up, preserved, and reported as a preserved local customization. |
| Manifest hash mismatch | Detected | `status` reports `Manifest: changed` and contributes to `UPDATE_AVAILABLE`. |
| Source revision changed | Detected | `status` reports `Revision: changed` and the differing installed and source commits. |
| Interrupted update | `RECOVERY_REQUIRED` | A residual transaction journal makes `status` report recovery and `Interrupted update: yes`. |
| Recovery and retry | Deterministic | The next update rolls back from the recorded backup, removes the journal, applies the update, reaches `CURRENT`, and a repeated update stays `CURRENT`. |
| Missing installation state with payload present | `RECOVERY_REQUIRED` | Deleting the state file while managed files remain is reported as recovery, not as a fresh install. |
| Reinstall after update | Remains correct | Reinstalling the same source reports `reinstall (no changes)` and stays `CURRENT`. |
| Uninstall after update | Removes only managed files | Recorded, unmodified managed files are removed; unmanaged user files and backups remain. |
| Legacy format 1 state | Read and migrated | An uncustomized format 1 row keeps a usable baseline, the update succeeds, and the state is rewritten as format 2. |
| Baseline retention across a preserving update | Baseline stays upstream | After a customization is preserved, the recorded baseline still differs from the installed hash, so a later upstream change remains detectable. |
| Status without an installation | Rejected | `status` against an empty destination exits non-zero and reports no compatible installation. |
| Unmanaged user files | Never deleted | User-created files survive update, forced update, and uninstall in every scenario above that creates them. |

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
bash -n install.sh update.sh uninstall.sh status.sh distribution/loop-pilot.sh
python -m unittest tests.test_distribution -q
```

Synchronization status against an installation:

```powershell
.\status.ps1 -Destination <destination>
```

```bash
./status.sh --destination <destination>
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

The result table preserves commands observed against the Distribution-004 working
tree at its recorded boundary. A parser pass does not substitute for lifecycle
execution, and a native-shell pass does not establish behavior on another shell.

| Check | Environment | Status | Evidence |
|---|---|---|---|
| PowerShell parser | Windows PowerShell | PASS | All five PowerShell files parsed after the complete Distribution-004 change set: `distribution\loop-pilot.ps1`, `install.ps1`, `update.ps1`, `uninstall.ps1`, and `status.ps1`. |
| PowerShell lifecycle scenarios | Windows PowerShell | PASS | `tests.test_distribution`: 18/18 passed after Distribution-004. Distribution-002.1 previously observed 7/7 with the same harness, together with a live repository install, update, uninstall, and self-uninstall. Distribution-004 additionally observed a live repository install, `status`, local customization, and uninstall against a temporary destination. |
| Bash syntax | Git Bash 5.2.37 on Windows | PASS | `bash -n install.sh update.sh uninstall.sh status.sh distribution/loop-pilot.sh` exited 0 outside the restrictive sandbox. The sandbox-only `Win32 error 5` remains recorded as an Execution Infrastructure Incident. |
| Bash lifecycle scenarios | Git Bash 5.2.37 on Windows | PASS | Distribution-003 observed fresh install, 126-file manifest/state/hash integrity, customization preservation, backup creation, self-uninstall, user-content preservation, and state cleanup. Distribution-004 additionally runs all ten synchronization scenarios through `distribution/loop-pilot.sh` as `shell='bash'` subtests, with zero skips. |
| Distribution-004 synchronization scenarios | Windows PowerShell and Git Bash 5.2.37 | PASS | Every scenario in the Distribution-004 table executed on both shells in one suite run, 20 shell-level subtests, no divergence between implementations. |
| Live install at repository scale | Windows PowerShell and Python 3.13 | PASS | Installing the current repository placed 141 managed files with version `unreleased` and commit `317dd975145c6193f4af0b0479f31357c06f1245`; `status` then reported `CURRENT`, `State format: 2`, `Revision: unchanged`, `Manifest: unchanged`, and 141 current files. `status.ps1` and `status.sh` were both present in the installation. |
| Status from inside an installation | Windows PowerShell | Documented limitation | Running the installed `status.ps1` against its own installation stops with `cannot determine a 40-character source commit`, because an installed copy has no `.git/` and no `distribution/commit.txt`. This is the pre-existing rule that already governs `install` and `update`; `status` compares against a source package and is run from one. |
| Installed existing validator | Windows PowerShell and Python 3.13 | PASS | Distribution-002.1 first established this row when a fresh isolated installation included `.github/workflows/validate.yml` and its copied validator printed `Static validation passed`. Distribution-004 re-observed the same result: the copied validator in the live 141-file installation printed `Static validation passed` against the installed root. |
| Existing static validator | Python 3.13 | PASS | `scripts\validate.py` printed `Static validation passed` with exit code 0. |
| Full repository tests | CPython 3.13 | PASS | The outside-sandbox run completed 881/881 tests in 768.260 seconds with exit code 0. The count rose from 870 because Distribution-004 added ten synchronization tests and one conflict-refusal test. |
| Diff whitespace check | Git | PASS | `git diff --check` completed with exit code 0; Git emitted only existing LF/CRLF normalization warnings. |

## Distribution Evidence Lineage

Each stage is retained so a later reader can see what was established when, and
what a later stage replaced. A superseded behavior is recorded, not deleted.

| Stage | What it established |
|---|---|
| Distribution-001 | The packaging boundary: manifest, version and commit metadata, installation state, entry points, path safety, and the original install, update, and uninstall lifecycle. |
| Distribution-002 | Corrections to that lifecycle, carried into the scenario table above. |
| Distribution-002.1 | The `tests.test_distribution` harness passing 7/7, a live repository install, update, uninstall, and self-uninstall, and a fresh isolated installation whose copied validator printed `Static validation passed` with `.github/workflows/validate.yml` present. |
| Distribution-003 | Bash parity: syntax across the wrappers and shared implementation, plus a Git Bash lifecycle covering a fresh install, 126-file manifest, state and hash integrity, customization preservation, backup creation, self-uninstall, user-content preservation, and state cleanup. |
| Distribution-004 | Installed-Skill upgrade synchronization: the five synchronization states, the three-way BASE/LOCAL/REMOTE comparison, state format 2 with a preserved baseline, the transaction journal with rollback recovery, the `status` operation, and both-shell execution of every synchronization scenario. |

## Distribution-004 Behavior Change

Distribution-004 supersedes one documented Distribution-001 upgrade behavior, and
the change is recorded here rather than left to be discovered.

Previously, a managed file modified both locally and upstream was preserved
silently and the update reported success. A newly managed path colliding with
different pre-existing user content was handled the same way. Both are now
conflicts: the update stops before changing any managed file, names every
conflicting path, and exits non-zero, because an update must not claim success
while a conflict is unresolved. `-Force` and `--force` still back up local
content and take the source version.

Two existing regression tests encoded the superseded contract and were rewritten
to assert refusal followed by a forced resolution. The two contracts are
incompatible, so this is a deliberate replacement rather than a regression.

The state schema moved from format `1` to format `2` so that a preserved
customization no longer destroys its upstream baseline. Format `1` states are
still read. An uncustomized format `1` row keeps its recorded hash as the
baseline; a customized format `1` row has no recoverable baseline and is
resolved conservatively toward conflict rather than toward overwriting local
content.

The user-requested `python` command resolved to GraalPy 3.12.8 without PyYAML.
`python scripts/validate.py` therefore stopped at import with
`ModuleNotFoundError: No module named 'yaml'`; its full discovery run was stopped
after repeated instances of the same dependency failure. These are execution
environment results, not product failures. CPython 3.13 supplied the repository's
declared dependency and provided the complete passing suite above.

Any remaining `PENDING`, `UNVERIFIED`, or failed row must be reported honestly in
the applicable distribution completion summary. Git Bash evidence does not imply
Linux, macOS, WSL, or another Bash implementation was tested. The Bash results
above were produced by Git Bash on Windows only; no Linux, macOS, WSL, or
alternative Bash implementation was exercised, so those environments remain
UNVERIFIED.
