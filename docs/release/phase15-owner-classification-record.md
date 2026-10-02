# Phase 15 Owner Classification Record

An Owner classification of the host permission denial measured during Phase 15
preparation. It is not an acceptance run, not a rubric score, not a Host
Acceptance Record, and not a Release Candidate.

**No state recorded here is upgraded.** Host Acceptance remains UNVERIFIED, RC
Gate 4 remains UNMET, no gate is ticked, and **no fixture was executed** — not
`LW-1`, `FL-1`, `FL-1R`, or `IMP-1`. This document creates no `EVAL-006`, no
`trace.md`, no `score.md`, and no Host Acceptance Record. It changes no
`SKILL.md`, no `AGENTS.md`, no activation protocol, no rubric semantics, no
scenario, no verdict rule, no C2 semantics, no Distribution-004 semantics, and no
RC Gate state. It amends no control C1–C8 and weakens none. It re-pins nothing —
not the host version, not the model, not the binary, not the Skill, not the
commit, not the execution surface. It introduces no role, mode, Ledger, lifecycle
state, Checkpoint, or acceptance dimension, and no authorization mechanism.

- Boundary: HEAD `89b1a1f3b22badc9b300eab6c4a2906b47d1728f`, branch `main`,
  working tree dirty, nothing pushed.
- Governing boundary: [`phase15-acceptance-boundary.md`](phase15-acceptance-boundary.md).
- Governing surface design: [`phase15-execution-surface-design.md`](phase15-execution-surface-design.md).
- Governing correction: [`phase15-execution-surface-correction.md`](phase15-execution-surface-correction.md).
- Prompt contract: [`phase15-fixture-prompt-contract.md`](phase15-fixture-prompt-contract.md).

## 1. Precondition Check Performed Before Recording

The Owner instruction required verification that this classification can be
recorded without changing the frozen execution surface, and that recording be
abandoned rather than performed if it would require modifying governing
specification text. Both were checked before this file was written.

| Property | Result | Basis |
|---|---|---|
| Governing text modified | **No** | Nothing in §5.10, §5.11, §5.12, §6, §12, §13, the rubric, the scenarios, or the prompt contract is edited. This document is additive |
| Installed Skill tree reachable | **No** | `distribution/managed-files.txt` lines 3–4 exclude `docs/release/` from the payload by name. A document here cannot enter a fresh install |
| P4 / `C2_CLEAN`, P5 disturbed | **No** | Both were measured on the installed tree, which is untouched. The payload exclusion above is why this remains true |
| Validator obligation added | **No** | `scripts/validate.py` names one literal under `docs/release/`, `v1.0-rc-checklist.md`. It performs no directory scan of `docs/release/` |
| Frozen surface touched | **No** | Pinned binary, model, Skill loading mode, commit `89b1a1f`, body digest `530bbaf7…46a`, flag set, prompt files and digests are neither read nor written by recording |

Recording was therefore performed. Had any row failed, the instruction required a
report instead of an edit.

## 2. Owner Decision, Recorded

| Field | Value |
|---|---|
| Classification question | Does a host permission denial of a prompt-authorized operation under the frozen execution surface constitute **A. INFRASTRUCTURE BLOCKED / EII** or **B. ENVIRONMENT-CONSENT OUTCOME**? |
| **Decision** | **Branch A — INFRASTRUCTURE BLOCKED / EII** |
| Scope | This Phase 15 run, at the frozen combination, under `--permission-mode acceptEdits` |
| Not a behavioral FAIL | Affirmed. No dimension is recorded `fail` from any blocked arm |
| Not an environment-consent outcome | Affirmed. The denial is not reinterpreted as consent |
| Authorization expanded | **None.** No `--allowedTools`, no `--setting-sources` change, no project or local settings, no interactive grant, no allowlist, no mode change |
| Re-pinning | **None.** Model, binary, Skill, commit, and execution surface are unchanged |
| Fixtures executed | **None** |

## 3. Scope Honesty — This Is a Classification, Not a Reading

Stated explicitly, and load-bearing, because the opposite claim would be a
retroactive rewrite of text this decision does not touch.

**Boundary §5.11 does not literally enumerate this trigger.** Its stated scope is
*"if the pinned host cannot be launched, or an arm dies of a rate limit, timeout,
or empty output."* The measured event is none of those four: the pinned host
launched, emitted a well-formed `init` record, resolved its sandbox `cwd`,
reported its own version, and exited `subtype: success`.

Therefore:

- This is the **Owner classification decision for this run**.
- It is **not** a claim that §5.11 already mechanically implied it.
- It is **not** an amendment to §5.11. The text of §5.11 is unchanged, and its
  stated scope still reads as it did.
- It sets no precedent that binds a later run, a later boundary, or a later host
  combination. A future permission denial is classified when it occurs, by
  whoever owns that run.

Nothing in this document narrows, widens, or restates §5.11's written scope.

## 4. Consequences

Each follows from Branch A as chosen. Items 1–9 are the Owner's; the citations
record where the consequence already lives.

1. **All four arms are blocked at the infrastructure boundary.** `LW-1`, `FL-1`,
   `FL-1R`, and `IMP-1` each carry an authored workflow requiring an operation
   the frozen permission surface cannot authorize. All four authored prompts
   require a test run; `FL-1` additionally requires stage commits. Arm result for
   each: `BLOCKED / EII`.
2. **Every behavioral dimension remains `not-evaluated` for this run.** All
   eight, per §5.11: *"every dimension the arm would have evidenced stays
   `not-evaluated`."* No dimension is `pass`, none is `partial`, none is `fail`.
3. **No behavioral `fail` may be recorded from a blocked arm.** §5.11: *"a `fail`
   asserts an observed protocol-relevant behaviour the host could not deliver,
   and an incident observed no behaviour."*
4. **Host Acceptance remains UNVERIFIED.** §5.11: *"the record's verdict stays
   `unverified`. It never becomes `rejected`."*
5. **RC Gate 4 remains UNMET and unreachable for this run.**
   `scripts/cross_host_acceptance_validation.py` allows `{pass}` under `accepted`
   and `{pass, partial}` under `accepted-with-residuals`; `not-evaluated` is
   forbidden under both evidence verdicts.
6. **No `EVAL-006`, `trace.md`, `score.md`, or Host Acceptance Record is
   created.** Boundary §5.9: *"absent artifacts stay absent. No `score.md`,
   report, or record is written for an arm that did not produce one."*
7. **No synthetic Checkpoint is created or preserved to make `FL-1R` runnable.**
   Surface-design §6: *"no Checkpoint is hand-written for it to resume from —
   that would be reconstructing evidence."*
8. **`FL-1R` does not run**, even though `.looppilot/` state is technically
   writable under `acceptEdits`. Surface-design §6: *"if `FL-1` does not reach a
   Checkpoint, `FL-1R` does not run. It is not substituted, not simulated."*
9. **The denial is recorded separately as infrastructure evidence**, per §5 below
   and boundary §5.10, and is never treated as behavioral evidence.
10. **The scope-honesty statement in §3 stands as part of this decision**, not as
    commentary on it.

## 5. The Denial, Recorded as Infrastructure Evidence

Preserved under boundary §5.10 as **Host capability** — *"what the binary can do
before any LoopPilot content exists."* It is separated from **Protocol
behavior** and is never merged into a behavioural set. It scores no dimension and
is not admissible as protocol behavior evidence.

Measured by the `p-permprobe` infrastructure probe recorded in prompt-contract
§10.2 and §11, run on the pinned image under the exact §7 launch shape, in a
throwaway directory that is not `LW-1`, `FL-1`, or `IMP-1`.

**Host envelope, as emitted:**

```text
claude_code_version : 2.1.232
permissionMode      : acceptEdits
terminal outcome    : subtype: success, 15 turns
denial records      : 4 × system/permission_denied
```

**Exact operations, by outcome:**

| Operation | Outcome |
|---|---|
| `Edit` — rewrite a source file | allowed |
| `Read`, `Glob` | allowed |
| `Bash: ls -la`, `git status --short`, `git log`, `git diff`, `python --version` | allowed |
| `Bash: python -m unittest discover -s . -p "test_*.py"` | **DENIED** — *"This command requires approval"* |
| `PowerShell:` the same test command | **DENIED** |
| `Bash: git add calc.py` | **DENIED** |
| `Bash: git add … && git commit -m …` | **DENIED** |

The interpreter is not the obstacle: `python --version` ran and returned
`GraalPy 3.12.8`. The gated operations are executing the suite, and separately,
mutating the index or the history.

**The probe did not consume the `IMP-1` observable.** Its transcript contains
zero `Skill` tool calls; its tool inventory is `Bash` ×8, `Read` ×3,
`PowerShell` ×1, `Glob` ×1, `Edit` ×1. Its prompt carries no LoopPilot protocol
vocabulary, satisfying surface-design §4.4 rule 4.

## 6. What Branch A Makes Unreachable Rather Than Resolved

One question was identified as unresolved in the existing text and **is not
resolved here**:

> Whether an uncommitted, unverified `.looppilot/` Checkpoint constitutes
> *"`FL-1` reaches a Checkpoint"* under surface-design §6.

Branch A makes this question **unreachable for this run**, because `FL-1` is
blocked at the infrastructure boundary and `FL-1R` does not run. It remains
**UNRESOLVED** in the specification. Nothing here decides it, and the two
passages that point opposite ways — surface-design §6's mtime-based file check
and prompt-contract §6.2's committed-and-green stopping point — are left exactly
as written for whoever reaches the question next.

## 7. Preserved Blockers and Findings

Carried forward unchanged. Nothing in this document closes, downgrades, or
reinterprets any of them.

| ID | Finding | State |
|---|---|---|
| **B7 / P14** | `evaluations/templates/score.md` is short the `Evidence integrity across agents` and `Authority continuity` rows. Blocks `score.md` authoring, not arm execution | **Open, unchanged** |
| **B8 / P15** | No reviewer independent of the trace author exists. Blocks the record, not the run | **Open, unchanged** |
| **P4** | `status.ps1` = `CURRENT` **and** `c2_isolation_validation.py` = `C2_CLEAN`, `Findings: 0`, measured at the pinned commit — correction §6.6 | **PASS, preserved** |
| **P7** | Sandbox paths outside the repository; no `CLAUDE.md` in any sandbox or any ancestor to the drive root, nine per arm — prompt-contract §9 | **PASS, preserved** |
| **P13** | No forbidden flag in any launch shape; all eight plus `--bare` confirmed present on the pinned image, so the prohibition guards a real hazard — prompt-contract §7 | **PASS, preserved** |

**Disclosed labelling gap.** The Owner instruction additionally named `N1`, `N2`,
and `N3` for preservation. **No such identifiers exist anywhere in this
repository**, so no mapping is asserted here — inventing one would be exactly the
fabrication this record exists to avoid. The unnumbered non-blocking findings
currently open in Phase 15 preparation are preserved by content regardless of
label, and are listed so nothing is lost either way:

- **Prompt-contract §10.1** — a clean checkout at the pinned commit sits at
  `%LOCALAPPDATA%\Temp\lp-accept\clone`, beside the sandboxes and outside P8
  check A's reach, holding every §4.1 prohibited path. §3.2 requires it gone
  before any first arm.
- **Prompt-contract §10.4** — `FL-1`'s authored task is a lighter trigger than
  scenario 69's stated prompt shape. Disclosed rather than engineered around.
- **Correction §6.6** — `c2_isolation_validation.py`'s `# Host Acceptance Record`
  content rule decodes as `utf-8`, so a file carrying a UTF-8 BOM escapes it.
  Recorded rather than fixed.
- **Correction §6.5** — the `SKILL.md` whole-file digest diverges under
  `core.autocrlf=true`. No gate reads it; the body digest is equal.
- **Correction §5.1, §5.2** — model context capability and endpoint
  configuration, both reclassified as environment information, not acceptance
  findings.
- **B12, B13** — classifications and their disclosed residuals in
  [`phase15-b12-b13-decision-analysis.md`](phase15-b12-b13-decision-analysis.md).

If `N1`–`N3` denote specific items above, the Owner may bind the labels; this
record does not bind them.

## 8. What This Document Does Not Do

It runs no fixture. It creates no `EVAL-006`, no trace, no score, and no Host
Acceptance Record. It ticks no RC gate. It performs no reinstall and mutates no
installed tree. It modifies no `SKILL.md`, `AGENTS.md`, activation protocol,
rubric, scenario, fixture semantics, Distribution-004 semantics, acceptance
dimension, or verdict rule. It amends no control C1–C8 and weakens none. It
re-pins nothing.

It does not "fix" the specification to enable execution. It modifies §5.10,
§5.11, §6, §12, §13, or any other governing text nowhere and in no respect. It
creates no acceptance dimension, no evidence gate, and no new check. It
introduces and implies no authorization mechanism.

It does not claim Phase 15 failed behaviorally. **No behavior was observed**, so
no behavioral claim of any polarity is available. The correct state is
infrastructure blocked, with every behavioral dimension not evaluated.

## 9. Status

```text
NOT_READY_FOR_PHASE15_FIXTURES
INFRASTRUCTURE BLOCKED / EII
Host Acceptance: UNVERIFIED
RC Gate 4: UNMET
```

Release Candidate remains **not approved**.
