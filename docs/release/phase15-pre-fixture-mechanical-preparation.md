# Phase 15 Pre-Fixture Mechanical Preparation

A record of the three mechanical preparation steps authorized by the Owner after
the Authorized Operation Set decision: removal of the stale pinned-commit
checkout, creation of the transcript output directory, and execution of the
prescribed negative reachability probe. It is not an acceptance run, not a rubric
score, not a Host Acceptance Record, and not a Release Candidate.

**No state recorded here is upgraded.** Host Acceptance remains UNVERIFIED, RC
Gate 4 remains UNMET, no gate is ticked, and **no fixture was executed** — not
`LW-1`, `FL-1`, `FL-1R`, or `IMP-1`. This document creates no `EVAL-006`, no
`trace.md`, no `score.md`, and no Host Acceptance Record. It changes no
`SKILL.md`, no `AGENTS.md`, no activation protocol, no rubric, no scenario
semantics, no Distribution-004 semantics, no verdict rule, no acceptance
dimension, and no control C1–C8. It re-pins nothing.

- Boundary: HEAD `89b1a1f3b22badc9b300eab6c4a2906b47d1728f`, branch `main`,
  working tree dirty, nothing pushed.
- Governing surface design: [`phase15-execution-surface-design.md`](phase15-execution-surface-design.md).
- Primitive definition: [`successor-boundary-authorized-operation-set.md`](successor-boundary-authorized-operation-set.md).

All evidence below is **infrastructure evidence** under boundary §5.10, observed
outside any acceptance arm. None scores a dimension and none is admissible as
protocol behavior evidence.

## 1. P6 — Stale Pinned-Commit Checkout Removed

Design §3.2 requires the install source be deleted before the first arm *"so no
fixture can reach a checkout even by absolute path."* Prompt-contract §10.1
recorded that `%LOCALAPPDATA%\Temp\lp-accept\clone` was *"that checkout under
another name"* and retained it because B1 was believed unperformed. Design §14
closes B1, so the stated reason for retention no longer holds.

**Inspected before removal**, because a deletion is not reversible by argument:

| Property | Measured |
|---|---|
| `HEAD` | `89b1a1f3b22badc9b300eab6c4a2906b47d1728f` |
| `git status --porcelain` | empty — no uncommitted work |
| `git stash list` | 0 entries |
| `HEAD` reachable from the repository | **yes** — the checkout is reproducible, holding nothing unique |
| Size | 2.8 MB |

Removed. The path no longer exists. **P6 = PASS.**

## 2. Transcript Output Directory Created

Design §3.1's layout names `out\` for host-emitted transcripts. It did not
exist. Created at `%LOCALAPPDATA%\Temp\lp-accept\out\`. No other directory was
added, and the `sandbox\`, `prompts\`, and probe directories were not modified.

## 3. P9 — Negative Reachability Probe

Run exactly as design §4.4 prescribes: *"A throwaway session — `P-probe`, never
an acceptance arm — is launched in a sandbox with a prompt that instructs it to
attempt to read each prohibited path and report the raw tool result."*

### 3.1 Probe construction

| Property | Value |
|---|---|
| Sandbox | `lp-accept\p9-probe\`, created empty, **discarded after the run** per rule 1 |
| Never run in | `LW-1`, `FL-1`, `IMP-1` — rule 1 |
| Prompt | `lp-accept\p9-probe.prompt.txt`, 769 bytes, sha256 `6a62354930a1806b6f6ce4b744ee22bd30a545e11809797a551961ea8b7b9e75`, attested **before** the run |
| Image | Pinned `2.1.232` by absolute path, per correction §3.1 |
| Flag set | The frozen shape unchanged: `-p --session-id --model 'claude-opus-5[1M]' --output-format stream-json --verbose --setting-sources user --strict-mcp-config --permission-mode acceptEdits`. No flag added, removed, or reordered |
| Transcript | `lp-accept\out\p9-probe.jsonl`, 29 records, sha256 `b9f804442640718a5fd541458a5d793000e65b3708a2172f5e82ccf925549dc2` |

**Vocabulary.** Rule 4 requires the probe name no LoopPilot protocol vocabulary.
Applying prompt-contract §3's recorded interpretation — protocol vocabulary is
the protocol's internal constructs, `Lightweight`, `Full Loop`, `Ledger`,
`Contract`, `Checkpoint`, `Barrier` — the probe prompt carries none. It contains
file path names only, and path names are not constructs.

### 3.2 Host envelope

```text
claude_code_version : 2.1.232          (pinned image served the session)
permissionMode      : acceptEdits
cwd                 : …\lp-accept\p9-probe
message.model       : claude-opus-5    (satisfies P1's condition on this probe)
result              : is_error=false, subtype=success, num_turns=12
api_retry           : 1
Skill tool calls    : 0
```

### 3.3 Result — every prohibited path returned a host error

11 `Read` attempts, **11 `tool_result` records with `is_error: true`**, zero
successes.

| Path attempted | Host outcome |
|---|---|
| `tests/evaluation-rubric.md` | `File does not exist` |
| `tests/scenarios.md` | `File does not exist` |
| `evaluations/` | `File does not exist` |
| `docs/cross-host-acceptance.md` | `File does not exist` |
| `docs/release/phase15-acceptance-boundary.md` | `File does not exist` |
| `docs/release/phase15-execution-surface-design.md` | `File does not exist` |
| `docs/evaluations/claude-code/` | `File does not exist` |
| `MEMORY.md` | `File does not exist` |
| `CLAUDE.md` | `File does not exist` |
| `C:\…\LoopPilot\tests\evaluation-rubric.md` | **`system/permission_denied`** |
| `C:\…\LoopPilot\docs\cross-host-acceptance.md` | **`system/permission_denied`** |

Each "does not exist" result additionally carries the host's own note that the
working directory is the probe sandbox, so the negative is anchored to a cwd the
host reported rather than to one the operator asserted.

**The two absolute-path attempts are the stronger half.** Design §3.2's property
is that no fixture can reach a checkout *even by absolute path*. Those two
attempts test it directly, and the host refused both with first-party
`permission_denied` records. The property is now enforced twice over: the
checkout is gone (§1), and absolute reads into the repository are denied by the
surface.

**P9 = PASS**, in the scope §4.4 defines: it proves that the specific paths C2
names returned errors from that host, in that sandbox, at that time. §4.4 already
states the probe cannot prove a negative in general, and nothing here claims
more.

### 3.4 The probe did not consume the `IMP-1` observable

Zero `Skill` tool calls; the tool inventory is `Read` ×11 and nothing else. The
probe neither exercised nor pre-answered the implicit-activation question.

## 4. Post-Preparation Re-Verification

Measured after all three steps, to confirm the preparation disturbed nothing it
was not meant to touch.

| Check | Result |
|---|---|
| `sandbox\LW-1` | `C2_CLEAN`, `Findings: 0`, 33 files — unchanged |
| `sandbox\FL-1` | `C2_CLEAN`, `Findings: 0`, 42 files — unchanged |
| `sandbox\IMP-1` | `C2_CLEAN`, `Findings: 0`, 33 files — unchanged |
| Prompt digests | `5dbb51c9…`, `e66cde4b…`, `518e10ae…`, `73d1f21a…` — all four unchanged |
| Repository working tree | No file modified by the mechanical work; only the two new preparation documents are added |

**P8 = PASS**, re-measured rather than inherited. **P11 = PASS**, re-verified.

## 5. What This Document Does Not Do

It runs no fixture. It creates no `EVAL-006`, no trace, no score, and no Host
Acceptance Record. It ticks no RC gate. It selects no authorization mechanism —
that remains deferred under the Authorized Operation Set specification §7. It
modifies no protocol, rubric, scenario, dimension, verdict rule, or control, and
weakens no C2 control. It re-pins nothing.

The probe is infrastructure evidence and is never merged into a behavioural set.

Host Acceptance remains **UNVERIFIED**. RC Gate 4 remains **UNMET**. Release
Candidate remains **not approved**.
