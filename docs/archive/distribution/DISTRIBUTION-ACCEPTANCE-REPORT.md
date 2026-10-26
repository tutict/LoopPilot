# LoopPilot Distribution Acceptance Report

## Scope

This report records Distribution-002 acceptance evidence for the committed
Distribution-001 implementation and the scoped Distribution-002.1 correction of
D002-F01. It validates packaging and installation output only. It does not change
the protocol, establish Host Acceptance, create a Release Candidate, or authorize
a release or tag.

- Observed date: 2026-08-07
- Distribution source commit: `a4c83f8b3ce90f6e388cf32b398a4d01667f9b66`
- Source version token: `unreleased`
- Original Distribution-002 source boundary: isolated detached worktree at commit
  `a4c83f8`
- Overall result: `PARTIALLY VERIFIED`. D002-F01 is corrected and verified in the
  current working tree; Bash execution remains `UNVERIFIED`.

## Distribution-003 Follow-up

The status above is the historical Distribution-002.1 boundary. Distribution-003
later executed the Git Bash lifecycle successfully and recorded the evidence in
`DISTRIBUTION-BASH-VALIDATION.md`. It also observed Claude Code Skill discovery but
did not observe a successful Skill content load because authenticated host calls
ended with HTTP 429. See `DISTRIBUTION-003-REPORT.md` and
`docs/evaluations/claude-code/distribution-load-record.md` for the current
distribution status. This follow-up does not change Host Acceptance.

## Distribution-002.1 Boundary

Distribution-002.1 used an isolated detached worktree at `a4c83f8` with only the
following current, uncommitted corrective files overlaid from the main working
tree:

- `distribution/managed-files.txt`
- `docs/installation.md`
- `INSTALLATION-VALIDATION.md`
- `tests/test_distribution.py`

This is an observed patched-source boundary, not a claim that the correction has
a new Git commit. The isolated source reported commit `a4c83f8` because that is its
committed base.

| Component | Observed value |
|---|---|
| Corrective source | `.tmp/distribution-002-1-source-20260807` |
| Corrective destination | `.tmp/distribution-002-1-acceptance-20260807/host/.codex/skills/loop-pilot` |
| Corrective source status | Exactly the four files listed above were modified. |
| Protocol files | `SKILL.md` and `AGENTS.md` were not overlaid or modified. |

## D002-F01 Classification and Correction

The committed distribution contract classifies
`.github/workflows/validate.yml` as required distribution material:

1. `docs/installation.md` states that `requirements-dev.txt`, `scripts/`, and
   `tests/` are installed for repeatable repository validation.
2. The committed `scripts/validate.py` lists
   `.github/workflows/validate.yml` in `REQUIRED_FILES` and stops when a required
   file is missing.

The workflow therefore is not repository-only development material within the
existing complete-payload contract. Distribution-002.1 adds that single file to
`distribution/managed-files.txt`, documents the `.github/` exception, adds the
installed-validator expectation, and adds an official-manifest regression test.
No protocol or validator behavior changed.

## Distribution-002.1 Evidence

The correction was tested with a new synthetic destination. The prior
Distribution-002 installation and its 125-file result remain historical evidence;
the following results are the corrective rerun.

| Check | Observed result |
|---|---|
| Fresh install | PASS; output reported version `unreleased` and commit `a4c83f8b3ce90f6e388cf32b398a4d01667f9b66`. |
| Manifest expansion | 126 unique managed files. |
| Installation state | 126 `FILE` rows; 0 set differences from the expanded manifest. |
| File presence | 0 missing managed files. |
| File integrity | 0 state-hash mismatches and 0 source-to-installed SHA-256 mismatches. |
| Manifest integrity | State manifest hash matched the corrective source manifest hash. |
| Workflow packaging | `.github/workflows/validate.yml` was both managed and installed; SHA-256 was `87f6dac3d78de53ef9becdaf2070689835c34e353932031d40b642313e2cdbb0`. |
| Installed validator | PASS; `py -3.13 <destination>\\scripts\\validate.py --root <destination>` printed `Static validation passed`. |
| Distribution tests | PASS; `tests.test_distribution` ran 7/7 tests. |
| Self-uninstall | PASS; installation state was removed and 0 managed files remained. |
| Workflow cleanup | PASS; `.github/workflows/validate.yml` did not remain after uninstall. |
| Generated content | 10 validator-generated Python cache files remained non-managed, consistent with the existing ownership rule. |

D002-F01 is therefore `RESOLVED` in the current working tree and verified against
the isolated corrective source boundary. Commit status remains separate from this
acceptance result.

## Environment

| Component | Observed value |
|---|---|
| Operating system | Microsoft Windows NT 10.0.26200.0 |
| Windows PowerShell | 5.1.26100.8972 |
| Python | 3.13.13 |
| Git | 2.51.0.windows.1 |
| Bash candidate | `C:\Program Files\Git\bin\bash.exe` |
| Source worktree | `.tmp/distribution-002-source-a082a28bd2ed4e0dba2878c4bc555f96` |
| Synthetic host layout | `.tmp/distribution-002-acceptance-f2aa739d98b94b40b01a0f185ab64f0a/host/.codex/skills/loop-pilot` |

The synthetic `.codex/skills/loop-pilot` path verifies installed layout only. No
Codex or other host process loaded the installed Skill during this phase.

## Implementation Review

No redesign was required or performed. Review of Distribution-001 identified these
verification gaps:

1. The committed package had not been validated from a clean source boundary into
   a fresh synthetic host directory.
2. The installed manifest, state rows, and per-file hashes had not been recorded as
   acceptance evidence.
3. The complete installed tree had not been checked for required Skill files and
   relative Markdown references.
4. Bash syntax and lifecycle execution remained unverified.
5. Actual host loading after installation remained unverified.

The audit also discovered one distribution consistency Finding, documented under
Incidents and Findings. No protocol Finding was observed.

## Commands Executed

The following command families were executed against the isolated source and
synthetic destination. Long PowerShell assertions are summarized by the data they
checked rather than copied as raw logs.

```powershell
git worktree add --detach <source> a4c83f8
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass `
  -File <source>\install.ps1 -Destination <destination>
```

PowerShell then expanded `distribution/managed-files.txt`, compared the expanded
set with every `FILE` state row, hashed every installed file with SHA-256, compared
the manifest hash, and compared installed version and commit metadata with the
source.

```powershell
py -3.13 <destination>\scripts\validate.py --root <destination>
```

The complete installed validator returned nonzero because
`.github/workflows/validate.yml` was absent. The existing validator's Markdown-file
validation path was then run directly against the installed root:

```powershell
py -3.13 -c "... markdown_files(root); validate_markdown_file(...) ..."
```

Update and uninstall were executed after adding a local README customization and a
user-owned file:

```powershell
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass `
  -File <source>\update.ps1 -Destination <destination>
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass `
  -File <destination>\uninstall.ps1 -Destination <destination>
```

Bash syntax and lifecycle were attempted in one process:

```powershell
& 'C:\Program Files\Git\bin\bash.exe' -lc `
  'bash -n install.sh update.sh uninstall.sh distribution/loop-pilot.sh; `
   ./install.sh ...; ./update.sh ...; ./uninstall.sh ...'
```

Repository checks:

```powershell
py -3.13 scripts\validate.py
py -3.13 -m unittest tests.test_distribution tests.test_validate -q
git diff --check
git hash-object SKILL.md
git rev-parse a4c83f8:SKILL.md
```

## Installation Evidence

| Check | Observed result |
|---|---|
| Fresh destination | Installation completed in a newly generated synthetic host root. |
| Manifest expansion | 125 unique managed files. |
| Installation state | 125 `FILE` rows; file set matched the expanded manifest. |
| File integrity | 0 missing files and 0 SHA-256 mismatches. |
| Manifest integrity | State manifest hash matched the source manifest hash. |
| Version detection | Source, output, and state reported `unreleased`. |
| Commit detection | Source, output, and state reported `a4c83f8b3ce90f6e388cf32b398a4d01667f9b66`. |
| Source isolation | Detached source worktree remained clean after acceptance. |

The installer did not copy the uncommitted Host Acceptance material present in the
main working tree because acceptance used the detached committed source.

## Update and Backup Evidence

Before update, the installed `README.md` was modified and `USER-NOTES.md` was added
as user-owned content.

| Check | Observed result |
|---|---|
| Update command | Completed with version `unreleased` and commit `a4c83f8...`. |
| Customization handling | Modified `README.md` was preserved. |
| State customization flag | `README.md` state row ended with `|1`. |
| Backup | One README backup existed and contained the local customization. |
| User-owned content | `USER-NOTES.md` remained unchanged. |
| Regression scenarios | `tests.test_distribution` passed all 6 lifecycle tests, including two-version upgrade, manifest migration, force update, missing-file repair, conflict preflight, and uninstall preservation. |

## Installed Skill Output

The following required installation outputs were observed:

- `SKILL.md`
- `AGENTS.md`
- `README.md`
- `docs/lifecycle.md`
- `docs/safety-and-stopping.md`
- `docs/installation.md`
- `.looppilot/README.md`
- `distribution/managed-files.txt`
- all six install, update, and uninstall entry points

`SKILL.md` began with frontmatter, contained `name: loop-pilot`, and contained a
description field. The existing Markdown validator inspected 84 installed Markdown
files and reported 0 Markdown or relative-reference errors.

These checks verify packaging prerequisites only. They do not prove that Codex,
Claude Code, or another host discovered, loaded, invoked, or followed the Skill.

## Uninstall and Cleanup Evidence

Uninstall was run from the installed `uninstall.ps1` entry point.

| Check | Observed result |
|---|---|
| Installation state | `.looppilot-installation` removed. |
| Unmodified managed files | Removed. |
| Modified managed files | Only customized `README.md` remained from the 125-file managed set. |
| User-owned file | `USER-NOTES.md` remained. |
| Backups | `.looppilot-backups/` remained. |
| Validator-generated files | 11 `scripts/__pycache__/*.pyc` files remained as untracked, user-generated content. |

The initial cleanup assertion expected only README and the user note to remain and
therefore failed when it encountered the Python cache. Rechecking against the
authoritative manifest showed that no unmodified managed file remained. Preserving
the cache is consistent with uninstall's rule to remove only state-recorded files,
but it means running validation inside an installation can leave content that
uninstall intentionally does not clean.

## Repository Validation

| Check | Result |
|---|---|
| `py -3.13 scripts\validate.py` | PASS: `Static validation passed`. |
| Distribution and validator focused tests | PASS: 9/9 after Distribution-002.1. |
| PowerShell parser | PASS. |
| `git diff --check` | PASS; only existing LF/CRLF normalization warnings were emitted. |
| `SKILL.md` blob | Unchanged from `a4c83f8`: `6e0f26a9e948659541f88fc066e4e70dfcb31b0b`. |
| `AGENTS.md` blob | Unchanged from `a4c83f8`. |

Distribution-002 changed no protocol behavior.

## Verified Behavior

- Fresh PowerShell installation from a clean committed source.
- Explicit destination handling in a synthetic `.codex/skills/loop-pilot` layout.
- Manifest expansion and state-file set equality.
- Per-file installed SHA-256 integrity.
- Version and commit detection.
- Required Skill file and frontmatter presence.
- Installed Markdown and relative-reference resolution.
- PowerShell update execution.
- Backup creation and content.
- Default preservation and state marking of a customized managed file.
- Preservation of unrelated user content.
- State-based PowerShell self-uninstall and managed-file cleanup.
- Existing repository static validation and focused regression tests.

## Unverified Behavior

- Bash syntax: the Bash process did not initialize.
- `install.sh`, `update.sh`, and `uninstall.sh`: no command body executed.
- Cross-host loading after installation.
- Host discovery, invocation, and behavioral compliance.
- Destination auto-detection against a real host profile; acceptance used an
  explicit destination to avoid writing to live host directories.
- Behavior on Linux, macOS, WSL, or another Bash-capable environment.

No Host Acceptance status changed as a result of this audit.

## Incidents and Findings

### Infrastructure Incident D002-I01

The initial `git worktree add` was denied by the sandbox when Git attempted to write
`.git/worktrees` metadata. The same scoped command succeeded after approved
execution outside that sandbox boundary. This did not affect the source commit.

### Infrastructure Incident D002-I02

Git Bash exited before parsing or executing scripts:

```text
fatal error - couldn't create signal pipe, Win32 error 5
```

The Bash lifecycle remains `UNVERIFIED`; no success was simulated.

### Acceptance Harness Incident D002-I03

The first cleanup assertion did not account for Python bytecode generated when the
installed validator was imported. A manifest-based recheck replaced that incorrect
expectation and observed that only the customized README remained from the managed
set.

### Distribution Finding D002-F01

The original Distribution-002 installed package could not run the complete
existing repository validator:

```text
ERROR: missing required file: .github/workflows/validate.yml
```

`scripts/validate.py` lists that workflow as required and returns before Markdown
validation when any required file is missing. Distribution-001 intentionally
excludes `.github/` from `distribution/managed-files.txt`, while the installation
guide says the complete payload includes maintenance tools for repeatable repository
validation. Those statements were not consistent in Distribution-002.

This was a Distribution Finding, not a protocol change or Host Acceptance result.
Distribution-002 recorded it without changing the manifest or validator.

**Distribution-002.1 disposition: RESOLVED.** The correction and its observed
evidence are recorded above. The installed existing validator now passes without
changing validator behavior.

### Remaining Item D002-F02

**Status: UNVERIFIED.** Git Bash still has no successful initialization or script
execution evidence. Distribution-002.1 did not retry or simulate Bash behavior.

### Remaining Item D002-F03

**Status: UNVERIFIED and outside Distribution-002.1 scope.** No real host loading
was executed. Structurally valid installed output is not Host Acceptance.

## Remaining Risks

1. Bash behavior may differ from the verified PowerShell implementation.
2. Installed validation can generate user-owned Python cache files that uninstall
   correctly preserves but users may not expect.
3. A structurally correct Skill directory does not prove a host can discover or
   load it.
4. Auto-detection remains unaccepted in a live host profile.

## Conclusion

Distribution-002.1 resolves only D002-F01. The corrected PowerShell package passes
fresh installation, manifest and hash integrity, its installed existing validator,
and managed cleanup verification. The overall distribution result remains
`PARTIALLY VERIFIED` because Bash execution is `UNVERIFIED`. Real host loading was
not executed and remains outside this distribution correction.
