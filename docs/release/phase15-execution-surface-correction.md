# Phase 15 Execution Surface Correction

An owner decision on host-version drift, the minimum invocation-shape correction
it implies, and the verification of the preserved executable that the correction
depends on. It is not an acceptance run, not a rubric score, not a Host
Acceptance Record, and not a Release Candidate.

**No state recorded here is upgraded.** Host Acceptance remains UNVERIFIED, RC
Gate 4 remains UNMET, no gate is ticked, and no fixture was executed. This
document changes no protocol, no `SKILL.md`, no `AGENTS.md`, no activation
protocol, no rubric, no fixture semantics, no Distribution-004 semantics, no
acceptance dimension, and no verdict rule. It introduces no role, mode, Ledger,
lifecycle state, Checkpoint, or acceptance dimension. It re-pins nothing.

- Boundary: HEAD `9006a241fc79ca68082dcc5d17407b55c95b9433`, branch `main`,
  working tree dirty (9 modified, 7 untracked), nothing pushed.
- Governing boundary: [`phase15-acceptance-boundary.md`](phase15-acceptance-boundary.md).
- Governing surface design: [`phase15-execution-surface-design.md`](phase15-execution-surface-design.md).
- Companions: [`phase15-b9-packaging-boundary-design.md`](phase15-b9-packaging-boundary-design.md),
  [`phase15-b1-clean-reinstall-decision-analysis.md`](phase15-b1-clean-reinstall-decision-analysis.md),
  [`phase15-b12-b13-decision-analysis.md`](phase15-b12-b13-decision-analysis.md).

## 1. Owner Decision, Recorded

Recorded before any fixture, per boundary §5.1 rule 1, which requires a stale pin
be corrected or re-affirmed and the change recorded *before* any fixture starts.

| Field | Value |
|---|---|
| Decision | **Option A — retain the frozen pin at Claude Code `2.1.232`** |
| Re-pin to `2.1.233`? | **No** |
| Model | `claude-opus-5`, unchanged |
| Skill loading mode | Installed, user-scope Skill directory, unchanged |
| LoopPilot commit | `9006a241fc79ca68082dcc5d17407b55c95b9433`, unchanged |
| Skill body digest | `530bbaf7718c4fc7ae54446621a9ab0d67363c8bf9e4c82e1306466aefcb146a`, unchanged |
| Owner rationale | The observed drift is in the default PATH surface. The pinned `2.1.232` executable remains directly instantiable at its preserved version-manager path, so the frozen acceptance combination remains available and has not been superseded |

Boundary §5.1 rule 1 is satisfied in its re-affirming branch rather than its
re-pinning branch: the pin was re-examined against a fresh observation, and the
observation did not displace it.

## 2. Version-Drift Observation

### 2.1 Correction to the observation as stated

The decision was issued against an observed default/PATH version of `2.1.233`.
**The observed default/PATH version at the time of verification is `2.1.234`.**
Drift continued between the observation and the decision, and the record carries
what was measured rather than what was asserted.

The `2.1.233` reading was not wrong; it was superseded. It is the version of the
**operator process** that issued and is executing this decision, evidenced by
`AI_AGENT=claude-code_2-1-233_agent` in the operator environment. That process
was launched from `~/.local/bin/claude.exe` while that path still held `2.1.233`.
The file at that path has since been replaced, with `~/.local/bin/claude.exe.old.1787023739651`
retained beside it as the displaced `2.1.233` image.

This does not weaken the decision. It strengthens its stated rationale: the
default surface has now drifted twice past the pin while the pinned executable
remained instantiable, which is precisely the asymmetry the decision relies on.

### 2.2 Measured state of the version-manager directory

All four images are byte-distinct except where noted, verified by SHA-256.

| Path | `--version` | SHA-256 | Role |
|---|---|---|---|
| `~/.local/share/claude/versions/2.1.232` | `2.1.232 (Claude Code)` | `ec9e3247…3bd6` | **Preserved pin** |
| `~/.local/share/claude/versions/2.1.233` | `2.1.233 (Claude Code)` | `8ae35d41…fabd` | Operator process image, preserved |
| `~/.local/share/claude/versions/2.1.234` | `2.1.234 (Claude Code)` | `3f877e78…eb1b` | Current default |
| `~/.local/bin/claude.exe` | `2.1.234 (Claude Code)` | `3f877e78…eb1b` | **PATH surface — byte-identical to `2.1.234`** |

The PATH surface is the drifted surface, and it is drifted by *substitution*, not
by indirection: `~/.local/bin/claude.exe` is a full 324 MB image, not a shim.

### 2.3 Decision record, in the form requirement 5 specifies

```text
observed default/PATH version : 2.1.234   (corrected from 2.1.233; see §2.1)
preserved pinned executable   : 2.1.232   (~/.local/share/claude/versions/2.1.232)
decision                      : retain 2.1.232
reason                        : the pinned executable remains independently
                                instantiable; default-surface drift does not
                                supersede the frozen acceptance boundary
```

Verified independently instantiable in §3, at the level of a host-emitted
`claude_code_version` field rather than a `--version` string.

## 3. Invocation-Shape Correction

### 3.1 The change, and its exact scope

The only thing changed is **which file object each Phase 15 arm executes**. Every
arm invokes the preserved image by absolute path instead of resolving `claude`
through `PATH`. No flag is added, removed, or reordered; the flag set in
[`phase15-execution-surface-design.md`](phase15-execution-surface-design.md) §5.1
stands unmodified, as do its forbidden-flag table and controls C1–C8.

```text
before   claude -p --session-id … --model claude-opus-5 …
after    <pinned-absolute-path> -p --session-id … --model claude-opus-5 …
```

### 3.2 The absolute path, and a platform caveat that is not cosmetic

The preserved image is stored **without a file extension**:

```text
C:\Users\tutic\.local\share\claude\versions\2.1.232
```

It is a valid `PE32+ executable for MS Windows 6.00 (console), x86-64`. Whether
it can be invoked at that path depends on the launching shell, and the failure
mode in one of them is silent.

| Launcher | Extension-less path | Result |
|---|---|---|
| Git Bash / MSYS | invoked directly | **Works.** Host emitted `claude_code_version: "2.1.232"` |
| PowerShell | `& $exe --version` | **Silently fails.** No output, no exception, `$LASTEXITCODE` unset |
| PowerShell | byte-identical copy with `.exe` suffix | **Works.** `2.1.232 (Claude Code)`, exit 0 |

**The PowerShell failure produces no error.** An operator scripting arm launches
in PowerShell — the shell the installation entry points already use — would
observe an empty result and no diagnostic. Any launcher that cannot demonstrate
a host-emitted `claude_code_version` of `2.1.232` must be treated as not having
launched the pinned image.

Where a suffixed path is required, the copy's SHA-256 must equal the preserved
image's `ec9e32479bc887809003c91384c6c3a26e7691856d1916f72f6f6d21800f3bd6`.
Measured equal for the copy used in this verification. A copy is a second
artifact, and its identity is established by digest, never by filename.

### 3.3 Verification of the preserved executable

Requirement 4's four checks, each answered from a measurement rather than an
assertion.

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Reports exactly Claude Code `2.1.232` | **PASS** | `--version` → `2.1.232 (Claude Code)`; and host-emitted `"claude_code_version":"2.1.232"` in the `system/init` record of a `stream-json` session |
| 2 | Is executable | **PASS** | PE32+ console x86-64; launched, initialised, and completed a session at exit 0 |
| 3 | Does not resolve through `PATH` | **PASS** | Not a symlink and not a shim — a 319 MB image with digest `ec9e3247…3bd6`, byte-distinct from the PATH surface `3f877e78…eb1b`. The host emitted `2.1.232` while `PATH` held `2.1.234`, so resolution demonstrably did not occur |
| 4 | Can instantiate the pinned model | **PASS** | §4. Claude Opus 5 instantiated at exit 0 with a completed turn. The environment requires the 1M context capability to be encoded in the requested string |

Check 3 is answered more strongly than it was posed. It was asked against
`2.1.233`; the surface it had to be proven independent of is now `2.1.234`, and
independence was established against the surface actually present.

## 4. Model Instantiation

### 4.1 What was measured

A throwaway probe, in a sandbox outside the repository, with the arm flag set and
a prompt carrying no protocol vocabulary. Classified as infrastructure evidence
under boundary §5.10 and never merged into a behavioural set. It is not an
acceptance arm and evidences no dimension.

| Probe | Image | `--model` | Exit | Outcome |
|---|---|---|---|---|
| 1 | `2.1.232` | `claude-opus-5` | 1 | **API Error 400.** `terminal_reason: api_error` |
| 2 | `2.1.234` | `claude-opus-5` | 1 | **API Error 400**, identical message |
| 3 | `2.1.232` | `claude-opus-5[1M]` | 0 | Completed turn, `stop_reason: end_turn` |

The 400 payload requests that a 1M-context variant be enabled and the call
retried.

### 4.2 Classification

**Not an EII, not a defect of the pinned binary, and not a blocker.**

- Not an EII. Boundary §5.11 scopes the label to a host that cannot be launched,
  or an arm dying of a rate limit, timeout, or empty output. The pinned host
  launched correctly, emitted a well-formed `init` record, resolved the sandbox
  cwd, and reported its own version.
- Not version-specific. Probe 2 reproduces the 400 on `2.1.234`. Retaining
  `2.1.232` neither causes nor worsens it, and re-pinning would not have resolved
  it — an independent confirmation that the owner decision was correct on its own
  terms.
- **Owner classification: an environment capability requirement.** This
  environment requires the 1M context capability to be encoded in the requested
  model string. Model identity is unchanged at Claude Opus 5, per §5.1.

### 4.3 The launch shape this implies

Every arm requests the model in the form this environment requires, and records
model identity as Claude Opus 5 with 1M context capability:

```text
<pinned-absolute-path> -p
  --session-id <uuid-per-arm>
  --model 'claude-opus-5[1M]'
  --output-format stream-json --verbose
  --setting-sources user
  --strict-mcp-config
  --permission-mode <fixed per arm, recorded>
  < prompts/<ARM>.txt
```

This is a change of requested string to satisfy an environment capability, **not**
a re-pin: the pin's model leg remains Claude Opus 5, P1 is unmodified, and
boundary §5.1 rule 3 is unmodified. No fixture was run.

## 5. Environment Observations

Both were surfaced by the §4 probes and were **reclassified by owner decision as
environment information, not acceptance findings**. The measurements below are
unchanged; only their standing is. Neither creates an acceptance dimension, an
evidence gate, or a Gate 4 blocker, and neither is carried forward as a blocker
anywhere in this document.

### 5.1 Model identity and context capability

`~/.claude/settings.json` sets, in its `env` block,
`ANTHROPIC_DEFAULT_OPUS_MODEL = claude-opus-5[1M]` together with
`ANTHROPIC_DEFAULT_OPUS_MODEL_NAME = claude-opus-5`, and the same pairing for the
Fable, Sonnet, and Haiku aliases. Every Phase 15 arm inherits this, because §5.1
launches every arm with `--setting-sources user`.

Measured on probe 3, which requested `claude-opus-5[1M]` explicitly:

| Field | Emitted value |
|---|---|
| `system/init` → `model` | `claude-opus-5[1m]` |
| **`assistant` → `message.model`** | **`claude-opus-5`** |
| `result` → `modelUsage` key | `claude-opus-5[1m]` |
| `modelUsage[…].canonicalModel` | `claude-opus-5` |
| `modelUsage[…].contextWindow` | `1000000` |

Pre-flight gate **P1** reads: `message.model` = `claude-opus-5` on 100% of
records. Probe 3 satisfies P1 exactly.

**Owner classification.** Model identity for this acceptance is **Claude Opus 5**.
`1M` is a **context-window capability**, not a model identity, even though this
environment requires it to be encoded in the requested model string. It follows
that:

- `message.model = claude-opus-5` is **not** evidence of model substitution;
- `[1M]` is **not** required to appear in `message.model`;
- **P1 is unmodified**, and boundary §5.1 rule 3 is unmodified;
- no context-window evidence dimension is created.

The requested-string requirement is an environment capability issue. Recorded in
the form the environment evidence needs, and no further:

```text
Model              : Claude Opus 5
Context capability : 1M
```

`modelUsage` and the `init` record both carry the requested string. That is
recorded as environment information; no gate reads it and none is changed to.

### 5.2 Endpoint configuration

`ANTHROPIC_BASE_URL = https://anyrouter.top` with `ANTHROPIC_AUTH_TOKEN` set.
Emitted alongside it:

| Field | Emitted value | What it attests |
|---|---|---|
| `apiKeySource` | `none` | No `ANTHROPIC_API_KEY`; the token arrives by another variable |
| `modelUsage[…].provider` | `firstParty` | The **API protocol shape** — first-party wire format as opposed to Bedrock, Vertex, or Foundry |

**Owner classification: environment information, not a Gate 4 blocker.** The test
applied is whether the existing Phase 15 boundary explicitly requires an official
Anthropic endpoint. It does not. `docs/cross-host-acceptance.md` scopes acceptance
to *one host, host version, model, and Skill loading mode* — four legs, and
endpoint is not among them. No acceptance document names an endpoint, a base URL,
or a provider as a scoped leg or a required property.

Endpoint provenance is therefore **not** inferred into a requirement from
telemetry fields, no endpoint-provenance acceptance requirement is created, and
neither the protocol nor the rubric is modified. The two values above are
recorded as environment information and carried no further.

## 6. Preparation Status

Requirement 7's sequence, reported against what was actually reached.

| Step | Status | Detail |
|---|---|---|
| **P0** — flags on the actual `2.1.232` | **PASS** | §6.1 |
| **P2 / B10** — implicit surfacing under the chosen flag set | **PASS** | §6.2 |
| **P3** — clean checkout at the pinned commit | **PASS** | §6.3 |
| **P4** — install state, `CURRENT` **and** `C2_CLEAN` | **FAIL** | §6.4 |
| **P5** — Skill body digest | **PASS** | §6.5 |
| **B1** — clean reinstall | **NOT PERFORMED** | §6.4; blocked by P4 |

### 6.1 P0 — verified against the pinned image, not an adjacent one

The surface design read its flag surface from the `2.1.233` binary and recorded
flag availability at `2.1.232` as *assumed, not verified*. That assumption is now
discharged by reading `--help` from the pinned image itself.

Every required flag is present: `-p` / `--print`, `--session-id <uuid>`,
`--setting-sources <sources>`, `--output-format <format>` with a `stream-json`
choice, `--strict-mcp-config`, `--model <model>`, `--permission-mode <mode>`, and
`--verbose`. All were additionally exercised end to end by probe 3.

Every forbidden flag is also present — `--resume`, `--continue`,
`--fork-session`, `--add-dir`, `--exclude-dynamic-system-prompt-sections`,
`--append-system-prompt`, `--system-prompt`, `--agents` — so gate **P13** guards
a real hazard rather than a hypothetical one.

`--bare` is present, carrying the same *Skills still resolve via `/skill-name`*
text that B10 was raised against. It is not used; §6.2 resolves B10 without it.

### 6.2 P2 / B10 — PASS

Run per the existing execution-surface design's stated probe: an **unrelated
third-party Skill, never `loop-pilot`**, so that establishing whether implicit
surfacing works does not consume the IMP-1 observable. No new model or telemetry
investigation was introduced.

Design §4.2 had already declined `--bare` as the default mechanism, so the
question P2 actually gates is whether implicit surfacing occurs under the
**chosen** flag set. It does.

| Property | Value |
|---|---|
| Image | pinned `2.1.232`, absolute path |
| Flag set | `-p --model 'claude-opus-5[1M]' --output-format stream-json --verbose --setting-sources user --strict-mcp-config --permission-mode acceptEdits`; **no `--bare`** |
| cwd | throwaway sandbox outside the repository; no `CLAUDE.md` in it or any ancestor |
| Prompt | names no Skill and carries no protocol vocabulary |
| **Observed** | **`Skill` tool called with `{"skill":"dataviz"}`**, unprompted, followed by seven reads of that Skill's bundled references |
| Exit | 0 |

The bundled-reference paths the host resolved are rooted at
`…\bundled-skills\2.1.232\…`, which independently corroborates that the pinned
image served the session.

**B10 is resolved.** Implicit surfacing is available on the pinned image under the
adopted flag set, so `IMP-1` is structurally observable and all four arms can
share one flag set without `--bare`. The `--bare` auth concern raised earlier is
moot, because `--bare` is not used.

### 6.3 P3 — PASS

`git worktree add --detach` at the pinned commit, verified rather than assumed:
`rev-parse HEAD` = `9006a241fc79ca68082dcc5d17407b55c95b9433`, and
`git status --porcelain` empty.

### 6.4 P4 — FAIL, and B1 therefore not performed

**The B9 manifest narrowing is not committed at the pinned commit.**
`distribution/managed-files.txt` is a modified, uncommitted working-tree file. At
`9006a24` the manifest still carries the **directory entries** `docs/`,
`evaluations/`, `scripts/`, and `tests/`; the working-tree version replaces them
with enumerated per-file entries.

Measured, both installs into pristine empty destinations — path E, the only path
[`phase15-b12-b13-decision-analysis.md`](phase15-b12-b13-decision-analysis.md)
§2.2 found clean:

| Install source | Manifest entries | Files | `status.ps1` | C2 scope B | Findings |
|---|---:|---:|---|---|---:|
| **Checkout at pinned commit `9006a24`** | 29 | 162 | **CURRENT** | **C2_CONTAMINATED** | **79** |
| Working tree (B9 narrowing, uncommitted) | 51 | 82 | — | **C2_CLEAN** | **0** |

The diagnosis is exact: the manifest is the whole cause, and nothing else
contributes.

**This is an existing stop condition, not a new one.** Gate P4 already requires
`C2_CLEAN` with `Findings: 0`, and surface-design §13 row 3 already reads: *stop;
never proceed by disclosure, and never answer it by narrowing the check.* No new
gate, dimension, or check was created to produce this result.

**Clearing the destination does not fix it.** Both measurements used empty
destinations. The contamination originates in the manifest at the pinned commit,
not in destination residue, so the remedy §13 names — clear and reinstall — is
inapplicable here.

Two corollaries worth recording:

- **`status.ps1 = CURRENT` is necessary and not sufficient, now measured on the
  pinned payload itself.** The pinned-commit install reports `State: CURRENT`,
  `Installed commit: 9006a241fc79…`, `Revision: unchanged`, `Manifest: unchanged`
  — correct provenance on every field — while holding 79 acceptance-corpus files.
  Previously this property was measured only on the upgrade path; it now holds on
  the clean-install path from the pinned commit.
- **`.looppilot-installation` records `COMMIT|9006a241fc79…` for both installs**,
  because `install.ps1` reads `rev-parse HEAD` and a dirty working tree does not
  change it. The state file therefore cannot distinguish a 162-file
  pinned-commit payload from an 82-file working-tree payload.

**B1 was not performed.** Neither available source satisfies both §5.3 and P4:
installing from the pinned commit fails P4, and installing from the working tree
violates §5.3 and §8.2 step 2, which require a checkout at the pinned commit with
empty porcelain. Choosing between them is a boundary amendment and belongs to the
owner. The real Skill directory was left exactly as found — 60 files, unmodified.

### 6.5 P5 — PASS

Verified on both install paths. `git worktree add` under this host's
`core.autocrlf=true` injects CRLF, so the checkout's `SKILL.md` is 18,002 bytes
against the repository's 17,648, and the **whole-file** digest is `f2d22128…8db2`
rather than the `a432bc26…1778` recorded in boundary §5.2.

**No gate reads the whole-file digest.** P5's pass condition is the **body**
digest, which §5.2 defines as newline-normalised and calls "the only one
comparable against what a host injects". Measured on both the LF and CRLF forms:

```text
body-sha256 = 530bbaf7718c4fc7ae54446621a9ab0d67363c8bf9e4c82e1306466aefcb146a
```

Equal to the pinned value in both cases. The whole-file divergence is recorded as
a disclosed discrepancy in §5.2's second digest only; it fails nothing and is not
promoted to a blocker.

## 7. Decision

```text
NOT_READY_FOR_PHASE15_FIXTURES — P4 / C2_CLEAN unmet
```

`READY_FOR_PHASE15_FIXTURES` is **not** reported. Surface-design §12 condition 1
requires P0–P9 and P11–P13 to pass; P4 fails.

Established: the host-version leg, the model leg, P0, P2/B10, P3, and P5. The
owner's decision to retain `2.1.232` is correct and is not the cause of the
blockage — the blockage is a repository state, not a host state.

Not established: P4. One owner decision is open, and it is the only one.

**How may the pinned commit's install be made `C2_CLEAN`?** Surface-design §12
condition 2 asserts that "the payload manifest no longer carries the acceptance
corpus, and a fresh install is verified C2-clean by enumeration". That assertion
is true of the **working tree** and false of the **pinned commit**, which is the
gap this section records. Both candidate resolutions amend something the current
instructions preserve — the pinned commit on one hand, §5.3 and §8.2 on the other
— so neither is taken here.

Nothing in this section creates an acceptance dimension, an evidence gate, or a
new check. P4 and §13 row 3 both pre-exist; they fired.

## 8. What This Document Does Not Do

It runs no fixture — not `LW-1`, `FL-1`, `FL-1R`, or `IMP-1`. It creates no
`EVAL-006`, no trace, no score, and no Host Acceptance Record. It ticks no RC
gate. It performs no reinstall and mutates no installed tree. It modifies no
`SKILL.md`, `AGENTS.md`, activation protocol, rubric, fixture semantics,
Distribution-004 semantics, acceptance dimension, or verdict rule. It amends no
control C1–C8 and weakens none. It re-pins nothing — not the host version, not
the model, not the commit, not the Skill digest.

The probes in §4 and §6.2 are infrastructure evidence observed outside any
acceptance arm. None scores a dimension, and none is admissible as protocol
behavior evidence. The §6.2 probe deliberately used an unrelated third-party
Skill so that the `IMP-1` observable remains unconsumed.

It creates no acceptance dimension, no evidence gate, and no endpoint-provenance
or context-window requirement. Every gate cited here — P0, P2, P3, P4, P5, and
§13's stop conditions — pre-exists in
[`phase15-execution-surface-design.md`](phase15-execution-surface-design.md).

B7, B8, and B10 are untouched.

Host Acceptance remains **UNVERIFIED**. RC Gate 4 remains **UNMET**. Release
Candidate remains **not approved**.
