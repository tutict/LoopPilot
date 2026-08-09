# LoopPilot Installation and Distribution

This document describes the packaging boundary established by Distribution-001
and extended through Distribution-004. It does not change the LoopPilot
protocol, establish Host Acceptance, or authorize a release.

## Source Repository Layout

The current repository separates distribution concerns from protocol content:

| Path | Distribution purpose |
|---|---|
| `install.ps1`, `install.sh` | Fresh installation and explicit reinstall entry points |
| `update.ps1`, `update.sh` | Managed-file upgrade entry points |
| `uninstall.ps1`, `uninstall.sh` | State-based removal entry points |
| `status.ps1`, `status.sh` | Read-only synchronization status entry points |
| `distribution/managed-files.txt` | Authoritative list of managed payload roots |
| `distribution/version.txt` | Version token printed and recorded by the installer |
| `distribution/loop-pilot.ps1` | Shared PowerShell implementation |
| `distribution/loop-pilot.sh` | Shared Bash implementation |
| `SKILL.md`, `AGENTS.md`, `docs/`, `.looppilot/` | Protocol instructions and supporting material |
| `examples/`, `evaluations/`, `scripts/`, `tests/` | Supporting examples, evidence, maintenance tools, and tests |
| `.github/workflows/validate.yml` | Workflow definition required by the existing repository validator |

The local `.git/`, `.claude/`, `.codex/`, `.tmp/`, caches, and other files not
named by `distribution/managed-files.txt` are not part of the installed payload.
The only managed `.github/` file is `.github/workflows/validate.yml`; other
`.github/` material remains repository-only unless the manifest names it. In a Git
checkout, a manifest directory expands only to files tracked by that checkout.
This prevents untracked local material from entering an install. In a release
archive without Git metadata, the archive contents under each manifest directory
are used.

## Installed Layout

An installation preserves the repository-relative paths required by `SKILL.md` and
the supporting documents:

```text
<destination>/
|-- SKILL.md
|-- AGENTS.md
|-- README.md
|-- install.ps1 / install.sh
|-- update.ps1 / update.sh
|-- uninstall.ps1 / uninstall.sh
|-- status.ps1 / status.sh
|-- distribution/
|-- docs/
|-- .looppilot/
|-- agents/
|-- examples/
|-- evaluations/
|-- .github/workflows/validate.yml
|-- scripts/
|-- tests/
|-- .looppilot-installation       generated
|-- .looppilot-transaction        generated only while an update is in progress
`-- .looppilot-backups/           generated only when a backup is needed
```

Empty directories are not significant and are not created or removed
independently.

## File Ownership

### Required managed files

Every regular file expanded from `distribution/managed-files.txt` is managed by
the installation. The manifest includes the executable Skill, its protocol and
shared-state references, distribution entry points, license and repository guides,
and the supporting files needed to keep repository-relative references intact.
Missing manifest sources stop installation before destination writes begin.

### Optional files

- `distribution/commit.txt` is optional source-package metadata. An archive without
  `.git/` must provide it as one lowercase 40-character Git commit identifier.
- `requirements-dev.txt`, `scripts/`, and `tests/` are not needed for host-native
  Skill invocation, but they are included in the complete managed payload for
  repeatable repository validation.
- `.github/workflows/validate.yml` is included because the existing repository
  validator requires it. Its presence in an installation does not install or run
  GitHub Actions.
- `examples/` and `evaluations/` are supporting material. They do not become
  observed Host Acceptance evidence merely because they are installed.

### Generated files

- `.looppilot-installation` records format, version, source commit, manifest
  hash, and one row per managed file holding the installed hash, the
  customization flag, and the upstream baseline hash. Users should not edit it.
- `.looppilot-transaction` exists only while an update is applying changes. Its
  presence means the previous update did not finish.
- `.looppilot-backups/<operation-id>/` contains files backed up before replacement
  or managed retirement. Backups are retained until the user reviews and removes
  them.

### User-owned files

Files not recorded in `.looppilot-installation` are user-owned. The scripts do not
delete or replace them. A modified or explicitly customized managed file is
preserved by default. If a file retires from a newer manifest, a preserved local
copy becomes user-owned because it is no longer listed in the new installation
state.

## Destination Selection

The scripts select the destination in this order:

1. `-Destination` or `--destination`.
2. `LOOPPILOT_INSTALL_DIR`.
3. A single detectable host skills parent, with `loop-pilot` appended.

The detectable parents are `$CLAUDE_CONFIG_DIR/skills`,
`$HOME/.claude/skills`, and `$HOME/.codex/skills`. If no parent or more than one
distinct parent is detectable, the command stops and requires an explicit
destination. Directory detection is packaging behavior, not evidence that the host
loads or follows LoopPilot.

## Install

Run the entry point from a complete LoopPilot source checkout or distribution
archive:

```powershell
.\install.ps1 -Destination "$HOME\.codex\skills\loop-pilot"
```

```bash
./install.sh --destination "$HOME/.codex/skills/loop-pilot"
```

Before copying, the installer validates the version, commit, manifest sources,
source hashes, destination path types, and symbolic-link boundary. It then checks
every managed destination for conflicts. A conflict stops the operation before any
payload file is copied or overwritten.

`-Force` or `--force` permits conflicting regular files to be backed up and
replaced. It never permits replacing a directory or traversing a symbolic link. An
identical existing installation is reported as `reinstall (no changes)`.

Successful output includes the installed version and source commit. The current
`distribution/version.txt` value is `unreleased`; that token is not a Release
Candidate claim.

## Installation State and the Source of Truth

The repository is authoritative. An installation is a managed projection of one
repository revision, never a second source of truth.

`.looppilot-installation` retains what an upgrade needs to compare three
versions of every managed file:

```text
BASE   = the upstream content recorded at the previous successful installation
LOCAL  = the file currently in the installation
REMOTE = the file currently in the source repository
```

Each `FILE` row is `path`, `installed hash`, `customized flag`, `baseline hash`.
`BASE` is the baseline hash and is kept distinct from the installed hash, so a
file preserved as a customization still remembers the upstream content it came
from and a later genuine upstream change stays detectable.

The state carries a schema version. Format `2` is current. A format `1` state
from an earlier installation is still read: an uncustomized row keeps its
recorded hash as `BASE`, while a customized row has no recoverable baseline and
its `BASE` is treated as unknown. An unknown baseline is resolved conservatively
toward conflict rather than toward overwriting local content. Updating a format
`1` installation rewrites it as format `2`.

No semantic version or release tag is required. The `unreleased` token is a
valid, updatable version.

## Synchronization Status

`status` is a read-only operation that reports whether an installation is
synchronized with the source. It answers, deterministically, whether the
installation is current, whether an update is available, whether local
modifications exist, whether conflicts exist, and whether recovery is required.

```powershell
.\status.ps1 -Destination "$HOME\.codex\skills\loop-pilot"
```

```bash
./status.sh --destination "$HOME/.codex/skills/loop-pilot"
```

The reported `State` is exactly one of:

| State | Meaning |
|---|---|
| `CURRENT` | Every managed file matches the source, and the recorded revision and manifest match it too. |
| `UPDATE_AVAILABLE` | At least one file can be updated, added, or removed safely, or the recorded revision or manifest has moved. No conflict exists. |
| `LOCAL_MODIFICATIONS` | Local edits exist, nothing upstream competes with them, and no update is pending. |
| `CONFLICT` | At least one managed file changed both locally and upstream, so no automatic resolution is safe. |
| `RECOVERY_REQUIRED` | A previous update did not finish, or the installation state is missing or unreadable while a payload is present. |

Those states are reported in that order of precedence: recovery outranks
conflict, conflict outranks an available update, and an available update
outranks local modifications. Counts per category and one `ACTION|path` line per
non-current file follow the summary, so the reason for a state is always visible.

`status` exits non-zero only when it cannot determine a state, such as when no
installation exists at the destination.

`status` compares an installation against a source package, so it is run from a
source checkout or archive and pointed at the installation, exactly like
`update`. It therefore needs a determinable source commit and shares the
existing rule for `install` and `update`: run it from a Git checkout, or supply
`distribution/commit.txt` in the source package. An installed copy contains no
`.git/` and is not given a `commit.txt`, so running `status` from inside an
installation against itself stops with the same source-commit error that
`install` and `update` produce there. Only `uninstall` reads state alone and
works from within an installation.

## Upgrade

Run the update script from the new source checkout or archive, targeting the
existing installation:

```powershell
.\update.ps1 -Destination "$HOME\.codex\skills\loop-pilot"
```

```bash
./update.sh --destination "$HOME/.codex/skills/loop-pilot"
```

The update requires a compatible `.looppilot-installation` state format. It does
not infer semantic version ordering. It applies the source package supplied by
the user and records that package's version and commit.

### Three-way update semantics

For every managed file:

| Case | Condition | Action |
|---|---|---|
| Unchanged | `LOCAL == BASE` and `REMOTE == BASE` | No action. |
| Safe upstream update | `LOCAL == BASE` and `REMOTE != BASE` | Replace `LOCAL` with `REMOTE`, after backup. |
| User customization | `LOCAL != BASE` and `REMOTE == BASE` | Preserve `LOCAL` and record it as customized. |
| Conflict | `LOCAL != BASE` and `REMOTE != BASE` | Never overwritten automatically. Reported as a conflict. |

A file whose `LOCAL` already equals `REMOTE` needs no action whatever the
baseline says. A missing managed file is restored.

### Conflict handling

An update that finds a conflict stops before changing any managed file, names
every conflicting path, and exits non-zero. It never reports success while a
conflict is unresolved. Resolve conflicts by reconciling the file yourself, or
pass `-Force` or `--force` to back up local content and take the source version.

A newly managed path that collides with pre-existing user content of different
content is also a conflict, because no baseline proves the local file came from
LoopPilot. This supersedes the earlier Distribution-001 behavior, which
preserved such a file silently and reported the update as successful.

### Additions and removals

- A managed file that does not exist locally is installed and its hash recorded.
- A file that leaves the manifest is backed up and removed when `LOCAL == BASE`.
- A file that leaves the manifest while locally modified is backed up,
  preserved, reported as a preserved local customization, and becomes
  user-owned because it is no longer in the new state.
- Files that were never managed are never removed. Removal only ever considers
  paths recorded in `.looppilot-installation`.

### Update transaction and recovery

An update is transactional enough that an interruption cannot look like success.
The order is: preflight, compare state, detect conflicts, back up, apply safe
changes, write the new state, verify hashes, then mark the transaction complete.

While changes are applied, `.looppilot-transaction` records the backup
identifier and every intended action before that action is performed. It is
removed only after the new state is written and the managed files are verified
against their expected hashes. If the process is interrupted, the journal
remains and `status` reports `RECOVERY_REQUIRED`.

The next `update` or `uninstall` rolls the installation back to its pre-update
content from the recorded backup, removes the journal, and then proceeds.
Recovery is therefore automatic, and retrying an interrupted update is
deterministic rather than dependent on how far the first attempt reached.

If an update fails partway for another reason, it does not report success and
the previous content remains available under `.looppilot-backups/<operation-id>/`.

The scripts use only regular file operations. They create no symbolic links and
depend on no shell redirection tricks, registry state, or sandbox bypasses.

### Cross-shell reporting difference

Both implementations report the same states, actions, and counts on standard
output. Advisory warnings differ by stream: Bash writes them to standard error,
while the PowerShell warning stream arrives on standard output when the script
is run with `-File`. Automation that inspects warning text should read both
streams.

## Uninstall

The uninstall entry point may be run from the installation itself or another
complete source package whose state format is compatible:

```powershell
.\uninstall.ps1 -Destination "$HOME\.codex\skills\loop-pilot"
```

```bash
./uninstall.sh --destination "$HOME/.codex/skills/loop-pilot"
```

Uninstall reads `.looppilot-installation` and removes only recorded files whose
current hashes still match their recorded hashes and whose customization flag is
clear. Missing files are ignored. Modified files, user-created files, backup files,
and directories are preserved. The state file is removed after processing, so all
preserved files are thereafter user-owned.

## Host Status

### Supported hosts

No host currently has committed evidence for an accepted Host Acceptance Record.
Accordingly, Distribution-001 makes no supported-host compatibility claim.

### Unverified hosts

Claude Code and Codex have destination auto-detection because their skills
directories are present in the current repository's host preparation material.
Their behavioral compatibility remains unverified. Gemini CLI, GitHub Copilot, and
all other hosts also remain unverified and require an explicit destination unless
one of the documented directory conventions applies.

See [Cross-Host Acceptance](cross-host-acceptance.md) for the separate evidence
requirements. Installation success must not be reported as Host Acceptance.

## Validation

The executable scenario matrix and current observed results are in
[`INSTALLATION-VALIDATION.md`](../INSTALLATION-VALIDATION.md). Repository protocol
validation remains defined separately in [validation](validation.md).
