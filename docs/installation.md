# LoopPilot Installation and Distribution

This document describes the Distribution-001 packaging boundary. It does not
change the LoopPilot protocol, establish Host Acceptance, or authorize a release.

## Source Repository Layout

The current repository separates distribution concerns from protocol content:

| Path | Distribution purpose |
|---|---|
| `install.ps1`, `install.sh` | Fresh installation and explicit reinstall entry points |
| `update.ps1`, `update.sh` | Managed-file upgrade entry points |
| `uninstall.ps1`, `uninstall.sh` | State-based removal entry points |
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

- `.looppilot-installation` records format, version, source commit, manifest hash,
  installed file hashes, and customization flags. Users should not edit it.
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
not infer semantic version ordering. It applies the source package supplied by the
user and records that package's version and commit.

- An unmodified managed file is backed up and replaced when its source changes.
- A missing managed file is restored.
- A locally modified managed file is backed up and preserved by default.
- A new managed path that collides with user content is backed up and preserved as
  a customization by default.
- A retired, unmodified managed file is backed up and removed.
- A retired, modified managed file is backed up, preserved, and becomes user-owned.
- `-Force` or `--force` backs up and replaces customized files that remain in the
  new manifest.

The new state file is written atomically after managed-file processing completes.
Backups are never silently overwritten or removed by update.

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
