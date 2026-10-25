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
release, a manifest directory expands only inside the validated export of the
pinned Git commit. Working-tree payload files are not copied. Explicit archive
mode separately snapshots its declared manifest and requires a caller-supplied
payload SHA-256; it never substitutes for failed Git identity resolution.

## Installed Layout

An installation preserves the repository-relative paths required by `SKILL.md` and
the supporting documents:

<!-- managed-layout:start -->
```text
<destination>/
|-- SKILL.md
|-- AGENTS.md
|-- README.md
|-- README.zh-CN.md
|-- CHANGELOG.md
|-- CONTRIBUTING.md
|-- LICENSE
|-- INSTALLATION-VALIDATION.md
|-- .github/workflows/validate.yml
|-- .looppilot/
|-- agents/
|-- distribution/
|-- docs/
|-- examples/
|-- install.ps1
|-- install.sh
|-- shortcuts/lp/SKILL.md
|-- status.ps1
|-- status.sh
|-- uninstall.ps1
|-- uninstall.sh
|-- update.ps1
|-- update.sh
|-- .looppilot-installation       generated
|-- .looppilot-transaction       generated only during update
`-- .looppilot-backups/       generated only when needed
```
<!-- managed-layout:end -->

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

- `distribution/commit.txt` is publisher metadata used only in explicit archive
  mode; it is not verified Git identity. Release mode never falls back to it. A
  conflicting marker in a pinned Git export is rejected.
- `requirements-dev.txt`, `scripts/`, and `tests/` are development/maintenance-only
  and are not installed by the official managed manifest. `evaluations/`,
  `docs/release/`, `docs/evaluations/`, and `docs/cross-host-acceptance.md` are also
  excluded from that payload; repository presence is not installation authority.
- `.github/workflows/validate.yml` is included because the existing repository
  validator requires it. Its presence in an installation does not install or run
  GitHub Actions.
- `examples/` is managed illustrative material, not observed acceptance evidence.
  `evaluations/` stores evaluation preparation/history separately and is not shipped.
  A temporary source export may contain tracked development/evaluation files; only
  manifest-selected files enter the installed payload. Generated installation receipts
  are separate from committed source files and do not establish Host Acceptance.

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

By default, run the entry point from a complete, clean Git source checkout.
The installer pins and exports the resolved commit before reading payload metadata:

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
rule for `install` and `update`: use a clean exact-root Git source, or explicitly
select archive mode with its expected payload digest. A commit.txt alone is never
sufficient. Default release mode refuses an installed copy without Git metadata.
Only `uninstall` reads destination state alone and works from within an installation.

## Upgrade

Run the update script from the new clean Git source, targeting the existing
installation. Archive sources require the explicit options described below:

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

## Short Alias Binding

`shortcuts/lp/SKILL.md` is the single short-trigger owner. It is part of the managed
manifest, installed, statused, updated, and uninstalled with the canonical package.
It adds no second protocol body and is not copied into a sibling user-scope `lp`
Skill directory. The alias must be loaded from this installed nested path; it
binds `../../SKILL.md` to the same installation used by `/loop-pilot`, requires
matching non-customized FILE hashes in `.looppilot-installation`, and rejects a
repository checkout, missing identity, ambiguity, or a different long-command root.
There is no cwd or repository fallback. A frontmatter name is not source identity.

Old out-of-band user-scope `lp` copies must be moved out of Skill discovery with
path/hash receipts before any later host observation. Installing this payload does
not authorize overwriting or deleting such copies. The maintenance-only
`shortcut_validation.py` models filesystem binding; it is not shipped or required
at runtime. Host discovery and command registration are separate, unverified
behavior until actually observed. A host without nested discovery must report the
alias unavailable rather than introduce another trigger owner or fallback body.

## Source Provenance

Release mode is the default for install, update and status. It requires an exact-root
Git repository, resolves `HEAD^{commit}` once, verifies the object and clean status,
and checks tracked working content against that pinned tree (including changes hidden
by assume-unchanged). Invalid HEAD, missing refs/objects or unavailable Git metadata
refuse release installation; commit.txt is never a fallback. Force does not override
source identity or cleanliness. The clean check is a preflight observation, not a live worktree claim or the copy
source. Another actor may change the original checkout afterward; the pinned SHA
remains the selected source.
The current receipt format uses 40-character SHA-1 commit identities; unsupported
Git object formats are refused rather than producing an unreadable receipt. Payload
content digests remain SHA-256.

Both native installers export the resolved SHA with `git archive` into a private
owned temporary directory (tar in Bash, ZIP in PowerShell). Regular exported files
must match the pinned Git blob identities, without clean/smudge filtering. The file
set must also exactly match the pinned tree: additional files are rejected before
manifest expansion, including additions below a directory entry. Symlinks,
submodules, omitted export-ignore files and changed export-subst content are rejected
rather than silently changing payload identity. Only then is the snapshot made
read-only for this pipeline. Manifest expansion, version/commit marker validation,
source hashes and all subsequent copy operations read that snapshot, never the
original working-tree payload. Each copied file must match its snapshot hash. A
worktree edit after the clean boundary cannot change the selected payload or version.

### Explicit Archive Mode

Archive mode is a separate, digest-bound path, not repository release provenance:

```powershell
.\install.ps1 -SourceMode archive -ArchiveSha256 "<expected-payload-sha256>" -Destination "<destination>"
```

```bash
./install.sh --source-mode archive --archive-sha256 '<expected-payload-sha256>' --destination '<destination>'
```

The same options apply to update and status. The source must not have its own Git
metadata. It must contain publisher-supplied commit.txt; output and installation state
label that commit as archive provenance, not verified Git identity. Manifest-selected
files and metadata are copied to a private snapshot, then its payload digest must
match the expected digest before destination mutation. Do not compute the expected
digest from untrusted content and mistake that for independent attestation.

### Receipt and Digest Semantics

Payload SHA-256 hashes UTF-8 records `relative/path|lowercase-file-sha256` followed
by LF, in ordinal path order, for every unique managed payload file. Source snapshot
and installed digests use that same representation. A fresh uncustomized installation
has matching digests. Updates may preserve explicitly flagged local customizations;
then the installed digest differs and FILE rows retain their source baselines and
customized flags. Such local bytes are not represented as unchanged Git bytes.

Current writers extend format 2 with one validated optional row:

```text
PROVENANCE|git-release-or-archive|source-snapshot-sha256|installed-payload-sha256
```

Current readers still accept old format 1/2 states without that row and identify their
mode as legacy-unverified. Older strict readers may reject the new extension; use the
matching current installer/status/uninstaller. The alias maintenance validator accepts
and validates this row but does not turn it into host acceptance or authenticity.

Snapshots are disposed only within their verified owned temporary paths. Read-only
staging is an implementation boundary, not a sandbox against privileged local actors.
No Python or other Skill runtime dependency is introduced; these are native installer
operations. Installation and provenance checks do not authorize release or prove host
command discovery.
