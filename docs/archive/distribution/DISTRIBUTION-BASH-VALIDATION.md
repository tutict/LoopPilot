# LoopPilot Distribution Bash Validation

## Scope

This record contains Distribution-003-A evidence for the existing Bash
distribution implementation. It does not change protocol behavior, establish Host
Acceptance, create a Release Candidate, or authorize a release, tag, or push.

- Observed date: 2026-08-07
- Result: `PASS` for Git Bash 5.2.37 on the observed Windows environment
- Installation source commit: `a4c83f8b3ce90f6e388cf32b398a4d01667f9b66`
- Source version: `unreleased`
- Source boundary: detached worktree at `a4c83f8` with only the four verified
  Distribution-002.1 corrections overlaid

## Environment

| Component | Observed value |
|---|---|
| Operating system | Microsoft Windows NT 10.0.26200.0 |
| Git Bash | GNU Bash 5.2.37(1)-release, x86_64-pc-msys |
| Git Bash executable | `C:\Program Files\Git\bin\bash.exe` |
| Git | 2.51.0.windows.1 |
| Verification shell | Windows PowerShell 5.1 for independent state and SHA-256 assertions |
| Source | `.tmp/distribution-003-source-20260807` |
| Destination | `.tmp/distribution-003-bash-20260807/installed` |

## Commands

The Bash commands ran outside the restrictive process sandbox after the same
binary failed to initialize inside it:

```powershell
& 'C:\Program Files\Git\bin\bash.exe' -n `
  install.sh update.sh uninstall.sh distribution/loop-pilot.sh

& 'C:\Program Files\Git\bin\bash.exe' ./install.sh `
  --destination /c/Users/tutic/IdeaProjects/LoopPilot/.tmp/distribution-003-bash-20260807/installed

& 'C:\Program Files\Git\bin\bash.exe' ./update.sh `
  --destination /c/Users/tutic/IdeaProjects/LoopPilot/.tmp/distribution-003-bash-20260807/installed

& 'C:\Program Files\Git\bin\bash.exe' ./uninstall.sh `
  --destination /c/Users/tutic/IdeaProjects/LoopPilot/.tmp/distribution-003-bash-20260807/installed
```

After install, an independent PowerShell assertion expanded
`distribution/managed-files.txt` using tracked files for directory entries,
compared that set with every installation-state `FILE` row, and calculated SHA-256
for source and installed files. Similar assertions inspected update and uninstall
state without replacing the Bash entry points.

## Fresh Install

| Check | Observed result |
|---|---|
| Bash syntax | PASS for all three wrappers and `distribution/loop-pilot.sh`. |
| Clean destination | PASS; the destination did not exist before install. |
| Install exit | PASS, exit code 0. |
| Printed version | `unreleased` |
| Printed commit | `a4c83f8b3ce90f6e388cf32b398a4d01667f9b66` |
| Manifest expansion | 126 unique managed files. |
| Installation state | 126 `FILE` rows and 0 set differences. |
| File presence | 0 missing managed files. |
| State SHA-256 | 0 mismatches. |
| Source-to-install SHA-256 | 0 mismatches. |
| Manifest SHA-256 | State value matched the source manifest hash. |

## Update and Backup

The installed `README.md` received a local marker and `USER-NOTES.md` was created
as a user-owned file before `update.sh` ran.

| Check | Observed result |
|---|---|
| Update exit | PASS, exit code 0. |
| Customized file | README marker remained unchanged. |
| State flag | The README state row ended in `|1`. |
| State hash | README state SHA-256 matched the preserved customized file. |
| Customized rows | Exactly 1. |
| Backup | Exactly 1 README backup was created. |
| Backup integrity | Backup SHA-256 matched the customized README and contained the marker. |
| User file | `USER-NOTES.md` remained with its original content. |

## Uninstall and Cleanup

Self-uninstall ran from the installed `uninstall.sh`.

| Check | Observed result |
|---|---|
| Uninstall exit | PASS, exit code 0. |
| Installation state | Removed. |
| Unmodified managed files | Removed. |
| Remaining managed files | Exactly 1: the customized `README.md`, now user-owned. |
| User file | Preserved with its original content. |
| Backup | Preserved and still contained the customization. |

## Failed Attempts and Incident Classification

### D003-EII-001: Restricted Git Bash Initialization

Inside the normal process sandbox, even `bash.exe --version` failed before script
parsing:

```text
fatal error - couldn't create signal pipe, Win32 error 5
```

The identical executable returned its version and completed syntax, install,
update, and uninstall checks after approved execution outside that boundary. This
is an `Execution Infrastructure Incident`, not a product or protocol regression.

### D003-EII-002: WSL Enumeration Denied

Both `wsl.exe --status` and `wsl.exe --list --verbose` exited 1 with
`Wsl/EnumerateDistros/Service/E_ACCESSDENIED`. No WSL Bash result is claimed.

## Remaining Unverified

- Linux, macOS, WSL, and non-MSYS Bash implementations.
- Destination auto-detection in a live Bash host profile; this run used an explicit
  isolated destination.
- Host loading, which is recorded separately from Bash packaging behavior.

## Conclusion

The Distribution-002 Bash lifecycle gap is closed for the observed Git Bash
5.2.37 environment. Cross-platform Bash behavior remains unverified. No
`SKILL.md`, role, Mode, Ledger, Barrier, lifecycle, RC, tag, or release change was
made.
