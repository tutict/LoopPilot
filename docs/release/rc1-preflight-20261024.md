# RC1 Preflight — 2026-10-24

This is a factual preflight record, not a Host Acceptance Record, trusted operator
index, approval of a runtime combination, or behavioral verdict. Formal arms were
not started. Gate 4 remains unmet and the candidate is `NOT_RELEASE_READY`.

## Scope and current baseline

- Observed baseline: `061ca98daf0b87b282930a0c130e395150a20a61`.
- Observed tree: `059359ba807b4bbf50b993b1d843129dd6264118`.
- Observed initial remote candidate: the same commit; remote main remained
  `aacbde449a6dbc8723d5c866033ac195017a90e5`; no `v1.0.0-rc1` tag was returned.
- Task branch: `codex/rc1-preflight-20261024`, created from that candidate.
- Successor: `OPTION-B-REFERENCE-2026-10-24` / `option-b-successor-v1`.
- Fixed RC Reference: Codex. Its designation is still preflight, not finalized.
- Supervisor, author and Integrator: `/root`; independent Reviewer:
  `/root/option_b_review`. Implementation review is separate from behavior review.

Mode decision: bounded Lightweight non-coding work with one owner and independent
fact/authority review. Evidence risk requires deep checks; there is no parallel
implementation, Project, Loop, Ledger or coordination dependency requiring Full
Loop. No product behavior, threshold, validator or Host configuration change is
proposed. This record is context, not standing authorization.

Plan: refresh baseline; inspect current rules; collect public-safe observations;
stop dependent arms on unmet preconditions; independently review the facts and run
fresh required maintenance verification; commit/push only verified useful records.

## Normative sources

- [Successor C01–C08](option-b-reference-successor.md): qualification, immutable
  per-RC choice, pre-arm finalization, exact identity and Git binding, history.
- [Current designation](rc-candidate-reference.md): Codex fixed, actual combination
  still unknown, no arms started, no finalization timestamp.
- [Cross-Host Acceptance](../cross-host-acceptance.md): eight dimensions, critical
  scores at least 2, shape coverage, independent review and unchanged RC gates.
- [Evidence integrity](../evaluation-evidence-integrity.md): v2 RC receipts,
  actual identity observations, distinct source artifacts, external operator index
  and an independently approved raw SHA-256; self-computed hashes grant no trust.
- [Installation](../installation.md): generated receipt, source commit and managed
  file provenance. The receipt is not itself behavioral acceptance.
- [Existing Phase 15 boundary](phase15-acceptance-boundary.md) §§5.2–5.4, 5.10,
  and [surface design](phase15-execution-surface-design.md) §§4.4, 11–13: loading
  digest, `CURRENT`, installation and fixture isolation, fresh contexts, prompt
  attestation and stop conditions. Their concrete executable/flags/model pin is
  Claude Code-specific; Option B does not turn that local plan into a Codex plan.

## Observed evidence inventory

Files are under [the preflight evidence directory](rc1-preflight-evidence-20261024/observations.json).
[SHA256SUMS.json](rc1-preflight-evidence-20261024/SHA256SUMS.json) is an integrity
manifest only, explicitly carrying no authority. Scoped `.gitattributes` preserves
the exact captured bytes and recognizes Windows CRLF only for the named captured
files. It retains blank-at-eol, blank-at-eof and space-before-tab checks and readable
diffs; reports and the checksum manifest keep their ordinary whitespace rules.
No capture is normalized, and no operator index was created or selected by the author.

| ID | Actual command/check | Preserved evidence and observed result |
| --- | --- | --- |
| E01 | `git rev-parse HEAD 'HEAD^{tree}'`, status, branch/remote listing, `git ls-remote --heads --tags origin ...` | Baseline and refs above; clean initial worktree; fresh remote reads, not cached tracking assumptions. |
| E02 | PATH `codex.cmd --version` | [Probe record](rc1-preflight-evidence-20261024/cli-version-probes.json): exit 0, `codex-cli 0.160.0`; exact stdout preserved. |
| E03 | app-bundled absolute `codex.exe --version`; OS process/executable inspection | Exit 0, `codex-cli 0.164.0-alpha.11.1`; [running process](rc1-preflight-evidence-20261024/running-codex-component.json) points to that image. Binary SHA-256 is in observations. Windows reports `10.0.26300`. |
| E04 | Whitelisted first `session_meta` fields of this chat's historical rollout | Initial 2026-10-12 metadata reports `0.162.0-alpha.17.2`. It is historical controller metadata, not the current binary or an upstream attestation. Full conversations and reasoning were not copied. |
| E05 | Read-only selected configuration fields, with origin-only URL redaction | Configuration declarations exist. Their values remain in a local ignored redacted capture and are deliberately not published as actual provider/model/endpoint identity. Authentication fields were not exported. |
| E06 | Existing `status.ps1 -Destination <live Skill>` | The host tool reported an initial manifest provenance rejection, but its redirected file is empty: the original error is not archived there. A separately labelled [new native reproduction](rc1-preflight-evidence-20261024/source-rejection-reproduction.json) exited 1 and preserves exact stderr; the later process-only Git-filter-controlled check exited 0 and reported `UPDATE_AVAILABLE`. |
| E07 | Native `pwsh -NoProfile -File <pinned source>/status.ps1 -Destination <live Skill>` | [Command/exit](rc1-preflight-evidence-20261024/live-status-command.json), [stdout](rc1-preflight-evidence-20261024/live-status.stdout.log): installed commit `1bc184c…`, source `061ca98…`; 79 current, 3 updatable, zero locally modified/conflicted files. |
| E08 | `py -3.13 -B scripts/c2_isolation_validation.py --destination <live Skill>` | [Live C2](rc1-preflight-evidence-20261024/live-c2.log): exit 0, 83 files, no backup files, `C2_CLEAN`, zero findings. The checker does not read the installation receipt. |
| E09 | Official `install.ps1` into a previously absent temporary destination, then native `status.ps1` | [Staging record](rc1-preflight-evidence-20261024/staged-installation.json), exact stdout files: both exit 0; pinned `061ca98…`, `CURRENT`, 82 managed files current, zero updatable/modified/conflicted. This does not select a runtime loading surface. |
| E10 | Existing C2 checker on the temporary candidate installation | [Staged C2](rc1-preflight-evidence-20261024/stage-c2.log): exit 0, 83 files, no backups, `C2_CLEAN`, zero findings. No fixture or new C2 probe arm ran. |
| E11 | SHA-256 of generated installation receipts and normalized Skill bodies | Raw receipts preserved. Live receipt `92b84d724e3ab4120a57154182851b7bbd7824f2ac24941dbd6490712af7f0c9`; staged receipt `79ee60e7cd617a617079c233507be8fe626cb1a92321f8285a8190f58179b38a`. Source/live body match at `a869d5119d9ec06dbf4f1330290809747254bb94ad3b42a828b5d9e65d60c218`; installed bytes are not an injected-body event. |
| E12 | Caller response to the missing-evidence request | Attributed user fact: trusted runtime identity evidence and independently approved operator index are not currently available. No expected Hash B binding was supplied. This does not assert that no such file exists anywhere on the machine. |
| E13 | Absolute app-core `codex.exe exec --help` | Exit 0; advertises `--json`, `--ephemeral`, `--sandbox`, `--cd` and `--skip-git-repo-check`. Help stdout/stderr are retained locally under `.tmp/rc1-preflight-20261024/`; no model turn started and no runtime loading or isolation property was established. |

The installed-surface `status` result is a prerequisite failure even though the
native command exits 0: the rule requires the reported state `CURRENT`.
`CHANGELOG.md`, `docs/validation.md` and `README.md` are the three updatable files.
The live Skill, its receipt, and provider/model/endpoint/proxy/auth configuration
were not updated by this task. The live receipt was rechecked unchanged after
the isolated install. Raw private configuration was not copied into this evidence.

## Preconditions and shortest safe unblockers

Status values describe the named scope only. PASS on a component or installed tree
does not imply PASS on the whole formal-arm prerequisite.

| Condition | Status | Source and checks | Blocks formal arms? | Missing evidence, boundary owner, minimum safe action |
| --- | --- | --- | --- | --- |
| Baseline, successor applicability and unique Codex choice | PASS | E01; successor C01/C02/C08 and current designation | No by itself | Re-read refs and fixed choice before any future launch. No retrospective role changes. |
| Available component versions and OS | PASS | E02–E04; actual executable/version and process observation | Not sufficient alone | Different surfaces are observed, not interchangeable. Re-observe the exact selected image before launch. |
| Finalized formal Host/version combination | BLOCKED | C03/C06; designation remains preflight | Yes | No finalized Codex execution surface/combination or committed timestamp. Supervisor must record the evidenced combination before arms, after the other prerequisites pass. |
| Actual provider identity | BLOCKED | E04/E05/E12; evidence-integrity runtime-identity contract | Yes | Only client/controller labels exist. Trusted capture producer/operator must supply a credential-free runtime provenance source and traceable trust basis. |
| Actual upstream model | BLOCKED | E05/E12; successor C06 | Yes | A configured/requested model is not an upstream identity event. Supply independently reviewable actual response/runtime identity evidence; do not infer it from an alias or assistant self-description. |
| Actual endpoint | BLOCKED | E05/E12; successor C06 | Yes | Configured URL origin does not attest the connected peer, routing or upstream. Supply public-safe trusted transport/runtime evidence without enabling new logging or changing configuration here. |
| Skill loading mode and injected body | BLOCKED | E11; cross-host dimension 1 and existing loading rule | Yes | Installed/source body bytes match, but no fresh formal-context load event or injected-body digest exists. Establish the actual selected loading surface and preserve its public loading observation. |
| Live install synchronized with the candidate | FAIL | E07; existing `CURRENT` requirement | Yes for this live surface | It is at `1bc184c…`, not the effective successor baseline. Use a verified authorized candidate installation/loading surface before finalization; no live update was silently performed. |
| Named installation Hash B | BLOCKED | E11/E12; current successor/checklist name it | Yes | Receipt digests were measured, but an authoritative expected RC binding was not provided. Operator must identify the existing Hash B definition/source and independently bind the selected verified receipt. This task does not invent a definition or bless its own hash. |
| C2 installed-directory scope | PASS | E08/E10; existing checker and surface-design §4.4 scope B | No within this scope | Both actually enumerated trees are clean. Recheck the selected tree before launch; `CURRENT` alone does not establish C2. |
| Complete fixture/host isolation | NOT_RUN | Existing C1/C2/C3 and relevant arm prerequisites | Yes | No formal sandbox/arm was selected or launched. Apply the governing Codex procedure's existing isolation requirements; do not import Claude-specific flags or invent another C2 arm. |
| Trusted operator index and independent digest | BLOCKED | E12; evidence-integrity trust boundary/operator schema | Yes under this task | No operator-supplied external path, independently approved SHA-256 or actual evidence linkage is available. Operator must provide the trusted input; author-generated checksums or synthetic test indexes cannot substitute. |
| Exact applicable Codex arm procedure | BLOCKED | Search of cross-host/Codex preparation/successor/Phase 15 sources; E13 | Yes | Inspected concrete Phase 15 launch plan pins Claude Code. Advertised Codex flags do not establish an executable/loading/public-event/isolation mapping. The Supervisor must validate a concrete Codex plan under existing rules once its inputs are available; only a change of scope/threshold/control would require another governance decision. No general Phase 15 procedure or new approval requirement is inferred. |
| Independent behavior review | NOT_RUN | Cross-host review requirement; no formal trace exists; existing surface-design §9.3 | Blocks a qualified record; this task also requires its prerequisites before an arm | Independent Agent fact review is separately assigned and is not behavior review. The inspected Phase 15 sealed-review path expressly excludes operator-spawned subagents and requires a separate person/operator; that local rule is not silently rewritten or generalized. Establish an admissible reviewer path for the actual Codex procedure and its sealed evidence basis; no self-signing or role invention. |
| Finalization, Git/run/arm IDs and ordering | BLOCKED | C03/C04/C06; current designation and no-arm observation | Yes | No complete combination or actual arm exists. Finalize and commit only after the missing facts are evidenced; do not backfill time or generate placeholder formal receipts. |

No formal acceptance arm ran. In particular, the historical Claude-specific
`LW-1`, `FL-1`, `FL-1R` and `IMP-1` plan was not translated or executed as Codex.
No Checkpoint, score, accepted summary, review receipt or trusted index was
manufactured. Their absence stays absence; it is not a rejected host result.

## Observed incident and inference boundaries

- Observed: a default Git content check rejected the manifest despite a clean
  checkout; its blob and working-file bytes were identical. Git's default
  `hash-object --path` produced `3588a2b2695d33dd9a86613112a8a24be18fabf9`, while
  raw-byte processing produced the recorded blob `2139bf2a3d55051466eed4a658b2142400cc02a4`.
  [Byte diagnostic](rc1-preflight-evidence-20261024/source-byte-diagnostic.json).
- Evidence gap: the initial redirected failure file is zero bytes; that initial
  error and wrapper status are attributed to the author's host tool observation,
  not to preserved native-process output. The new controlled reproduction is a
  different capture and is never backfilled as the original. Its exact exit 1,
  command and nonempty [stderr](rc1-preflight-evidence-20261024/source-rejection-reproduction.stderr.log)
  support the reproducible failure. This optional diagnostic gap does not replace
  any required formal evidence or remove any launch blocker.
- Observed: the unchanged installer/status check succeeded using an exact-blob
  temporary checkout with `core.autocrlf=false` only in the Git subprocess
  environment. No persistent source/global `core.autocrlf` setting or Host
  configuration changed; the new evidence directory's attributes only preserve
  its capture bytes. The earlier
  wrapper reported 128 after output, but that was not a measured native
  `status.ps1` exit; E07 preserves the actual native exit 0.
- Inferred from that controlled comparison: the initial provenance failure is
  an execution-environment/Git-filter interaction, not evidence that user files
  were edited or that the successor's gates should change. An existing installer
  compatibility concern may warrant separate examination; this does not establish
  a defect in the new successor or authorize a repair/threshold change. No Product
  or Protocol Finding is created here.
- Unverified: the source of earlier Host/provider configuration drift. Different
  version sources and current declarations do not identify who changed it or why.
  No historical configuration was restored or used as the new RC baseline.

## Research Brief — RESEARCH-002

Prepared 2026-10-24 by `/root`. These fetched official sources describe Codex
capabilities/configuration; they do not authorize actions or attest this machine.

| Source | Inspected information | Relevance and limit |
| --- | --- | --- |
| [OpenAI configuration reference](https://developers.openai.com/codex/config-file/config-reference.md) | `model_provider` is a configured provider ID; provider `base_url` is a configured API address | A declaration is not an observed upstream identity. No settings are changed here. |
| [Official non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode.md) | `--json` emits lifecycle/item JSONL events; item types can include reasoning | Event streaming is not automatically upstream identity attestation. Future capture must exclude private reasoning and secrets; no model request was started here. |
| [Official app-server protocol](https://learn.chatgpt.com/docs/app-server.md) | `initialize` describes user agent/platform; thread metadata includes a provider label | Controller metadata alone does not certify the actual provider, model or endpoint. No app-server thread/turn was started by this check. |

Official indexes were searched for this topic before reading the matching pages.
No current official information establishes the missing local runtime identity,
operator trust or this RC's behavioral verdict. Local evidence is required.

## Review, validation and publication

Fresh maintenance verification completed for this task. The previous task's
1,141-test PASS is historical evidence and was not reused. The independent
Standards/Spec review of the actual facts commit is still pending; preliminary
fact review found no remaining substantive issue after the capture-gap correction.

| Actual check | Fresh observed result |
| --- | --- |
| `py -3.13 -m unittest discover -s tests -p 'test_*.py' -v` | 1,141 tests in 1257.559 seconds, exit 0, OK; zero failures/errors/skips. |
| `py -3.13 -B scripts/validate.py` | PASS; zero new validated evaluation packages; historical packages remain ineligible. |
| `py -3.13 -m compileall -q scripts tests` | PASS. |
| `git diff --check` | PASS. |
| `py -3.13 <skill-creator>/scripts/quick_validate.py .` | Skill valid. |
| Current Mermaid extraction and pinned `mmdc` 11.16.0 | All 35 sources freshly rendered; every SVG nonempty. |
| Code/protocol/history and capture comparison | 99 protected paths and all 20 observation/capture/receipt files match the tested export byte-for-byte. The storage descriptor and its checksum were updated solely for exact-file CRLF recognition. |
| Specific evidence-related coverage | The fresh full run includes all 40 Option B policy/public-receipt cases, Cross-Host Acceptance, evidence integrity/disclosure, C2, immutable-install and Git-replacement regressions. No new formal package exists to validate. |

The fresh full run used
`C:/Users/tutic/IdeaProjects/LoopPilot/.tmp/rc1-preflight-verification-20261024`,
with neutral shipped `.looppilot/` files, CPython 3.13.13 / PyYAML 6.0.3, external
TEMP, and standard Windows PowerShell modules supplied only to that test process.
Its full log is retained outside commits at
`.tmp/rc1-preflight-20261024/fresh-full-regression.log` in the implementation
worktree. Final reporting clarifications receive static and independent fact
review; code and captured evidence remain the tested bytes. No required
maintenance verification is omitted or waived. There is no affected frontend.

The optional initial diagnostic's missing raw capture remains explicitly disclosed
above. Actual runtime/Hash B/index/isolation/reviewer prerequisites are still
unmet, not waived by maintenance PASS. Phase 11 and Gate 6 remain separate.

Only this report, its public-safe preflight captures and the current candidate
fact pointer are proposed for publication. Configuration declarations remain
local/ignored. A useful verified facts commit may be pushed normally after review;
the candidate must remain `NOT_RELEASE_READY`, with no release tag or deployment.

## Resume point

Fresh full verification session `65966` completed with exit 0; inspect
`.tmp/rc1-preflight-20261024/fresh-full-regression.log` for its actual result.
Static, compilation, Skill, whitespace and 35 fresh Mermaid renders also passed.
The preliminary Reviewer confirmed the qualified original-capture gap and all
21 checksums, with no remaining substantive preliminary fact/scope finding.
Final review must inspect the actual facts commit after fresh checks complete;
it is not granted by these preliminary observations. Complete that review and
record its decision without changing implementation or evidence bytes. Preserve this
report's blocked/not-run boundaries, archive completed coordination records and
recheck the remote target before any publication. Formal arms remain stopped
until the missing trusted identity, selected installation/Hash B, applicable
Codex procedure, isolation, index and ordering prerequisites are actually met.
