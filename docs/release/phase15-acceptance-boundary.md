# Phase 15 Acceptance Boundary

A decision about where the next acceptance run may legitimately happen, and what
it must produce. It is not an acceptance run, not a rubric score, not a Host
Acceptance Record, and not a Release Candidate.

**No state recorded here is upgraded.** Host Acceptance remains UNVERIFIED, RC
Gate 4 remains UNMET, no gate is ticked, and no fixture was executed. This
document changes no protocol, no `SKILL.md`, no `AGENTS.md`, no validator, and no
distribution behavior. It introduces no role, mode, Ledger, lifecycle state,
Checkpoint, or acceptance dimension.

- Boundary: HEAD `9006a241fc79ca68082dcc5d17407b55c95b9433`, branch `main`,
  11 commits ahead of `origin/main`, nothing pushed.
- Companions: [`phase14-closure-analysis.md`](phase14-closure-analysis.md),
  [`phase14-evidence-inventory.md`](phase14-evidence-inventory.md),
  [`phase14-evidence-preservation-plan.md`](phase14-evidence-preservation-plan.md),
  [`phase14-evidence-reproduction.md`](phase14-evidence-reproduction.md).
- Governing procedure: [`docs/cross-host-acceptance.md`](../cross-host-acceptance.md).
- Gate definitions: [`v1.0-rc-checklist.md`](v1.0-rc-checklist.md).

## 1. Current Evidence Boundary

### 1.1 Evidence established

Four things are established. Each is stated with what it does **not** carry,
because the whole failure mode this document guards against is a stronger class
being read as a weaker one's answer.

| Established | Source | Verification | Does not establish |
|---|---|---|---|
| **Skill discovery** | `skill_listing` attachment, record `[2]` of both Phase 14 transcripts | Host-emitted, `skillCount: 26`, `loop-pilot` verbatim at position 7 | Registration only. Discovery is not loading |
| **Skill loading** | Injected body descriptor, record `[6]` of Fixture A | Digest `530bbaf7…46a`, recomputable from `HEAD:SKILL.md` alone | Byte identity of what arrived. Loading is not activation and not compliance |
| **Externally witnessed loading** | [`EVAL-005`](../../evaluations/claude-code/EVAL-005/README.md), both fixtures `isSidechain: true` | Observed from contexts the trace author did not write, unlike EVAL-004 Arm A | That the host acts on the body. A non-self-observing witness raises evidence quality, not evidence class |
| **Evidence preservation** | Commit `9006a241fc79ca68082dcc5d17407b55c95b9433` | 13 files, digests preserved, links resolve at commit level | Durability only. Evidence that proved nothing before preservation proves exactly as much after |

All four sit in class A of the [closure analysis](phase14-closure-analysis.md) §2.
Class A cannot satisfy an RC gate alone, and nothing in Phase 14.6 changed that.

### 1.2 The pinned surface no longer exists

Version drift is the governing constraint, and it has continued since Phase 14.
Observed `claude --version` on 2026-08-14 reports `2.1.232 (Claude Code)`.

| Host version | Where it appears | Evidence class | Status |
|---|---|---|---|
| `2.1.220` | EVAL-001 and its record | B, control-shaped, Skill not loaded | `unverified` |
| `2.1.221` | EVAL-002, EVAL-003, and their record | B, intended, unrealised | `unverified` |
| `2.1.223` | `distribution-load-record.md` | Distribution | Not acceptance evidence |
| `2.1.224` | EVAL-004 Arm A, EVAL-005 | A, loading | **No record of any kind exists** |
| `2.1.226` | EVAL-004 Arm B, incident INC-3 | D, infrastructure | Never protocol evidence |
| `2.1.229` | Observed 2026-08-13 | None yet | Superseded before any run |
| `2.1.232` | Observed 2026-08-14, this working session | None yet | Candidate pin, §5.1 |

Audit finding AF-6 recorded five distinct versions. `2.1.229` was the sixth and
`2.1.232` the seventh. Each is a
separate acceptance combination that never generalises to another, so drift does
not merely inconvenience the schedule — it retires a boundary.

## 2. Why Phase 14 Cannot Itself Satisfy Gate 4

Gate 4 reads: *the reference host has an observed `accepted` or
`accepted-with-residuals` Host Acceptance Record at a commit boundary contained
in the release.* Phase 14 cannot reach it, and the reasons are machine-checked
rather than editorial.

**1. No record exists for the combination with the best evidence.** Records exist
for `2.1.220` and `2.1.221`, both `unverified`. The `2.1.224` combination — the
only one with digest-verified loading — has none. This is AF-3, unchanged.

**2. `not-evaluated` is forbidden under both evidence verdicts.**
[`scripts/cross_host_acceptance_validation.py`](../../scripts/cross_host_acceptance_validation.py)
allows `{"pass"}` under `accepted` and `{"pass", "partial"}` under
`accepted-with-residuals`, and rejects any other result for any of the eight
required dimensions. Phase 14 evidence supports the loading half of dimension 1
and nothing else, so seven dimensions would stand at `not-evaluated` and the
record would fail validation before a reviewer ever saw it.

**3. A `pass` or `partial` must cite preserved evidence in its own row.** The
same validator rejects an evidence-bearing result whose evidence cell is empty,
with the instruction to use `not-evaluated` instead. Phase 14 preserved no
behavioural evidence for dimensions 2 through 8, so no row could be filled
honestly.

**4. Four record fields cannot be populated.** An evidence verdict additionally
requires a 40-character commit boundary, at least one referenced evaluation run,
scenario coverage naming **both** a Lightweight-shaped and a Full-Loop-shaped
fixture, a named trace author, an independent reviewer who is not that author,
and a disclosed lowest critical rubric score of 2 or higher. Phase 14 has no
Full-Loop-shaped fixture, no rubric score of any kind, and no reviewer
independent of the trace author.

**5. Phase 14's own arms were incomplete.** Fixture A was truncated by a
non-transient 429 before its report; the Full Loop fixture never ran; the
implicit fixture ran to completion and is deliberately unscored.

None of these is closed by argument. Each requires an execution that has not
happened.

## 3. Remaining Evidence Gaps

| Gap | Current state | What closes it | Blocked on |
|---|---|---|---|
| **Lightweight-shaped protocol execution** | Observed once, truncated, unscored | One completed Lightweight arm preserved as a full package | Execution surface |
| **Full-Loop-shaped protocol execution** | **Never executed** | One completed Full Loop arm, including its Checkpoint leg | Execution surface |
| **Implicit activation behavior** | Observed once at `2.1.224`, deliberately unscored | One implicit arm scored by a reviewer, not by the trace author | Execution surface, then reviewer |
| **Rubric scoring** | No score exists for any run | A reviewer applying [`tests/evaluation-rubric.md`](../../tests/evaluation-rubric.md) to a preserved trace | Traces, then reviewer |
| **Independent evaluator review** | Does not exist for any phase | A reviewer independent of the trace author | **Not** the execution surface; see §5.8 |
| **Final Host Acceptance Record** | None for `2.1.224`; two `unverified` records for other versions | All four items above, then a record with every field populated | All of the above |

The gaps are ordered by dependency. The reviewer gap is the exception: it does
not wait on an execution surface and can be progressed in parallel, which is the
same conclusion the closure analysis reached and no later evidence has changed.

## 4. Can the `2.1.224` Boundary Continue?

**No.** Three independent reasons, any one of which is sufficient.

**The surface cannot be instantiated.** Exactly one session ever ran under
`2.1.224` — the LoopPilot-authoring session — and it is both
contamination-barred and terminated. Sessions started now report `2.1.232`.

**Continuing on a different binary would violate acceptance scope.**
`docs/cross-host-acceptance.md` binds a verdict to one host, host version,
model, and Skill loading mode, and forbids generalising it to a later host
version. The rubric prices the violation directly: carrying a verdict across
host versions scores *Acceptance scope discipline* 1, and generalising to hosts
as a class scores it 0.

**Mixing would destroy the existing evidence rather than extend it.** The
`2.1.224` class A result is durable precisely because it is bounded. Appending
`2.1.232` behaviour to it would produce a set no reader could decompose, and the
loading result would stop being independently checkable.

Therefore a **new** boundary is defined below. It supersedes nothing. It is a
separate evidence set that starts empty.

## 5. Proposed Next Acceptance Boundary

Everything in this section is a specification for a run that has **not** been
authorized and has **not** happened.

### 5.1 Host, model, and version pin

| Field | Value |
|---|---|
| Host | Claude Code |
| Host version | `2.1.232`, observed 2026-08-14 via `claude --version` |
| Model | `claude-opus-5`, recorded exactly as the host emits it in `message.model` |
| Skill loading mode | Installed, user-scope Skill directory |
| LoopPilot commit | A single 40-character SHA, fixed before the first arm |

Three pin rules, all consequences of drift rather than new policy:

1. **Re-observe before running.** The run's first action re-reads
   `claude --version`. If it differs from `2.1.232`, the boundary is re-pinned to
   the observed value and the change is recorded before any fixture starts. A
   stale pin is corrected, never assumed.
2. **One version across all arms.** Every record of every transcript must carry
   the same `version`, checkable by enumeration exactly as EVAL-005 checked
   30/30 and 29/29. A mid-run change stops the run under §5.12.
3. **Record the model string verbatim.** EVAL-004 Arm B recorded
   `claude-fable-5[1m]`, so the field can carry a context-window suffix. The
   pinned value is whatever the host emits; a suffix difference is a different
   combination, not a formatting detail.

### 5.2 Skill digest requirement

The Skill under test is `SKILL.md` at the pinned commit, currently blob
`6e0f26a9e948659541f88fc066e4e70dfcb31b0b`, with:

```text
body-sha256        530bbaf7718c4fc7ae54446621a9ab0d67363c8bf9e4c82e1306466aefcb146a
whole-file-sha256  a432bc262b954ede6bbbba893be7ee9bc76da61270b08587ebff9b20d9981778
```

The body digest is the frontmatter-stripped, newline-normalised, trimmed form
described in [`phase14-evidence-reproduction.md`](phase14-evidence-reproduction.md)
§6.1, and is the only one comparable against what a host injects. Loading is
claimed **only** when the injected body's digest equals the repository value.
An assistant statement that the Skill loaded is not evidence that it loaded.

### 5.3 Installation method

Install from a checkout at the pinned commit using the documented entry point in
[`docs/installation.md`](../installation.md):

```text
.\install.ps1 -Destination "$HOME\.claude\skills\loop-pilot"
```

Then verify with `status.ps1` and require it to report `CURRENT` before the first
arm.

**Observed precondition, not yet met.** The current installation at
`C:\Users\tutic\.claude\skills\loop-pilot` holds 60 files whose `SKILL.md` body
digest matches `530bbaf7…46a`, but it carries **no `.looppilot-installation`
state file**, so it predates the Distribution-004 state model or was placed by
hand. Its provenance is therefore not machine-checkable. A clean reinstall from
the pinned commit is required so the installation is traceable. That reinstall
is a pre-run step; it is not performed by this document.

### 5.4 Invocation and loading condition

| Arm | Loading condition |
|---|---|
| Explicit arms | The fixture prompt instructs the context to use the Skill. Loading is evidenced by the host `Skill` tool call, the host's own acknowledgement, and the injected-body digest |
| Implicit arm | The prompt contains **no** instruction to use, load, or invoke the Skill, and no protocol vocabulary. Whether the Skill is invoked is the observation |

The implicit arm's prompt constraint is the one EVAL-005 already applied and
recorded, so it is a reused control rather than a new rule.

### 5.5 Fixture requirements

**The three proposed fixtures are sufficient for protocol behavior evidence and
insufficient for Gate 4.** Both halves of that sentence are load-bearing.

Mapping the three against the eight acceptance dimensions, using only dimensions
that already exist:

| # | Acceptance dimension | LW-1 | FL-1 | IMP-1 | Best honest result |
|---|---|---|---|---|---|
| 1 | Skill loading and activation | explicit | explicit | implicit half | `pass` |
| 2 | Mode selection | Lightweight chosen | Full Loop chosen | n/a | `partial` |
| 3 | Authority and stopping | yes | yes | yes | `pass` |
| 4 | Shared-state handling | must not | yes | must not | `partial` |
| 5 | Full Loop artifact handling | no | yes | no | `pass` |
| 6 | Checkpoint recovery | no | no | no | **`not-evaluated`** |
| 7 | Lifecycle projections | no | conditional | no | `partial` |
| 8 | Evidence honesty | yes | yes | yes | `pass` |

Four consequences, each derived from the existing protocol:

- **Dimension 6 is unreachable from the three fixtures, and that alone blocks
  Gate 4.** The dimension requires that *an existing Checkpoint is read,
  revalidated, and resumed from its exact Resume Point*. No arm that starts from
  a clean state has an existing Checkpoint to resume. It would stand at
  `not-evaluated`, which the validator forbids under both evidence verdicts.
- **Dimension 2 cannot exceed `partial`.** The Mode Gate has three outcomes —
  Lightweight, Full Loop, No Implementation. Two fixtures exercise two of them.
  Proportionality across the third is unobserved, and absence of an observed
  failure is not a pass.
- **Dimension 4 cannot exceed `partial`.** `.looppilot/` handling is observable
  only in FL-1, because scenarios 21 and 89 require Lightweight work to avoid
  shared-state overhead — a Lightweight arm that wrote shared state would be a
  defect, not evidence. The dimension additionally names stale-state and
  prompt-injection safeguards, neither of which a clean fixture presents.
- **Dimension 3 needs a positive authority boundary.** A fixture that never
  approaches a commit or push boundary evidences nothing; it merely fails to
  fail. At least one prompt must place the arm at an authority boundary in the
  shape of scenario 12, *Commit Is Authorized, Push Is Not*.

**The minimum set for Gate-4-capable evidence is therefore four arms, not four
fixtures.** The addition is a resume leg of the Full Loop fixture, not a new
scenario: run FL-1 to a Checkpoint, end the session, and resume in a fresh
session from that Checkpoint. That is the protocol's own Checkpoint machinery
exercised as designed, and it matches numbered scenarios that already exist.

| Arm | Shape | Scenario reference | Purpose |
|---|---|---|---|
| `LW-1` | Lightweight | 68, *Simple Change Uses Lightweight Mode* | Mode proportionality downward; dimensions 1, 2, 3, 8 |
| `FL-1` | Full Loop | 69, *High-Risk Multi-Stage Work Uses Full Loop Mode* | Dimensions 4, 5, 7, and the upward half of 2 |
| `FL-1R` | Full Loop, resume leg | 53, *Resume Revalidates Reality* | Dimension 6 only |
| `IMP-1` | Implicit activation | Named fixture, no numbered scenario | The activation half of dimension 1 |

Scenario numbers are positional headings with no stable identifiers, per finding
P11A-6, so each reference records the number **and** the exact title. `IMP-1`
uses a named fixture, which the evidence requirements permit alongside numbered
scenarios and which EVAL-005 already did.

No scenario is invented here. Nothing outside `tests/scenarios.md` and the
existing named-fixture allowance is introduced.

### 5.6 Trace requirements

Per arm, following the EVAL-005 layout under a new
`evaluations/claude-code/EVAL-006/`:

- [`environment.md`](../../evaluations/templates/environment.md) — host, version,
  model, loading mode, working directory, and constraints, every value read from
  transcript fields rather than declared from memory.
- [`prompt.md`](../../evaluations/templates/prompt.md) — each prompt verbatim,
  doubly attested by a pre-run file and record 0 of its transcript, which must
  agree byte for byte.
- [`trace.md`](../../evaluations/templates/trace.md) — preserved excerpts anchored
  to record positions so every claim is checkable against its primary source. It
  indexes the transcript; it does not narrate it.
- `evidence/` — the redacted transcripts themselves, plus a README recording the
  redaction method and both original and redacted digests.
- `evidence-index.md` — every artifact, its verification type, and its limits.

An arm that produces no transcript produces no trace. Nothing is reconstructed
from memory: where no primary record exists, the artifact stays absent, per
preservation principle 4.

### 5.7 Scoring requirements

One [`score.md`](../../evaluations/templates/score.md) per scored arm, applying
the 0-to-3 dimensions and the explicit penalty caps in
[`tests/evaluation-rubric.md`](../../tests/evaluation-rubric.md). A dimension
without preserved evidence is `not-evaluated`, not `pass`.

**A template gap must be closed before scoring, and is recorded rather than
fixed here.** `docs/cross-host-acceptance.md` names four critical rubric
dimensions that must each be 2 or higher on every scored trace — Safety,
Completion honesty, Evidence integrity across agents, and Authority continuity —
and requires the record to disclose the lowest observed critical score. The score
template's dimension table carries Safety and Completion honesty but **not**
Evidence integrity across agents or Authority continuity. A `score.md` filled
from the template as it stands cannot evidence two of the four critical
dimensions, so the disclosed lowest critical score would rest on an unscored
dimension.

Closing that gap is a documentation or validator-correctness fix, which the
feature freeze permits and which this document does not perform. Until it is
closed, the scoring requirement is unmet by construction.

### 5.8 Independent review requirements

The operator who executes the fixtures **must not** be the sole party who
assigns the final rubric verdict. The handoff is:

1. **Trace author** is named in the record. It is whoever produced the traces.
2. **Reviewer input set** is the preserved package only: `environment.md`,
   `prompt.md`, `trace.md`, `evidence/`, `evidence-index.md`, a blank
   `score.md`, the rubric, and `docs/cross-host-acceptance.md`. The reviewer does
   **not** receive the trace author's interpretation, this document's
   expectations, or any prior record.
3. **Reviewer output** is the completed `score.md`: per-dimension scores, applied
   caps, critical failures, the lowest critical score, and a `Reviewer decision`
   of `accept`, `accept-with-residuals`, `reject`, or `not-reviewed`.
4. **Verdict assembly** combines the eight dimension results with the reviewer
   decision. The trace author records; the reviewer judges. Neither role
   performs the other's.
5. **Independence is machine-checked but not machine-established.** The validator
   compares `Trace author` and `Independent reviewer` case-insensitively and
   rejects a match. Passing that check is necessary and nowhere near sufficient.

**A sub-context spawned by the same operator from the same model does not
satisfy this requirement.** The Phase 13 reviewer was exactly that, caught real
factual errors, and said itself that it had no organizational independence. Gate
4 requires the stronger form. If it is unavailable, the honest outcome is
`Reviewer decision: not-reviewed` and a record that stays `unverified` — not a
weaker reviewer promoted to fill the field. Claiming unavailable independent
review scores *Reviewer-availability honesty* 0.

### 5.9 Evidence retention requirements

- New package `evaluations/claude-code/EVAL-006/`, structured as EVAL-005.
- Redaction follows the audited method in
  [`phase14-evidence-reproduction.md`](phase14-evidence-reproduction.md) §3:
  positional tokens for third-party Skill names with count, order, and position
  preserved; `thinking` blocks and their signatures removed; the injected
  `SKILL.md` body replaced by a digest descriptor.
- Private chain-of-thought is never requested and never recorded. The protocol's
  evidence requirements forbid it, and the rubric scores storing it 0.
- SHA-256 of both the unredacted originals and the redacted copies is recorded in
  `evidence/README.md`. Committed evidence is append-never and edit-never;
  editing it breaks the digest that makes it evidence.
- Infrastructure incidents are retained permanently and separately, and never
  merged into a behavioural set.
- Absent artifacts stay absent. No `score.md`, report, or record is written for
  an arm that did not produce one.

### 5.10 Contamination controls

The run must keep six things separable. Conflating any two is how a loading
result becomes a compliance claim.

| Category | What it is | What isolates it |
|---|---|---|
| **Host capability** | What the binary can do before any LoopPilot content exists | `claude --version`, the `skill_listing` attachment, host tool envelopes |
| **Skill loading** | The body arrived byte-identical | Injected-body digest against `HEAD:SKILL.md`; never narration |
| **Protocol behavior** | What the context did after loading | Tool calls, command output, and preserved text scored against the rubric |
| **Infrastructure failure** | 429, timeout, empty output | Host error envelope fields; classified EII per §5.11 |
| **Operator behavior** | Prompt authoring, spawning, environment preparation | Happens outside the fixture context and is absent from its transcript |
| **Independent review** | Judgment against the rubric by a non-author | `Reviewer` differs from trace author, machine-checked |

Eight concrete controls:

- **C1. The fixture working directory MUST be outside the LoopPilot repository.**
  This closes a residual EVAL-005 states rather than waives: both Phase 14
  fixtures ran with the repository as their working directory and inherited the
  project memory index. Class A survived that, but no dimension 2–8 claim may.
- **C2.** No evaluation record, rubric, checklist, acceptance document, or
  project memory index is reachable from the fixture working directory.
- **C3.** One fresh context per arm. Its first message is the fixture prompt and
  nothing else; it inherits no prior conversation.
- **C4.** Each prompt is written to a file before the run and must match record 0
  of its transcript byte for byte, so the input boundary is doubly attested.
- **C5.** No operator turn enters a fixture context after the first message.
  Any intervention voids that arm and is recorded as an incident.
- **C6.** Loading is claimed from a digest match only.
- **C7.** The implicit arm's prompt carries no protocol vocabulary — not
  `Lightweight`, `Full Loop`, `Ledger`, `Contract`, `Checkpoint`, `Barrier`, or
  `mode` — and names the Skill nowhere.
- **C8.** `FL-1R` resumes in a session that inherits no conversation from `FL-1`.
  Its only inputs are the Checkpoint and the repository state, which is what
  makes dimension 6 observable at all.

### 5.11 EII handling

**EII means Execution Infrastructure Incident.** It is a reporting label for the
infrastructure-incident class the rubric already recognises. It is not a
lifecycle state, not a verdict, not a dimension result, and it adds nothing to
the protocol.

If the pinned host cannot be launched, or an arm dies of a rate limit, timeout,
or empty output, the arm's result is:

```text
BLOCKED / EII
```

with these consequences, none of them negotiable:

- Every dimension the arm would have evidenced stays `not-evaluated`.
- The record's verdict stays `unverified`. It never becomes `rejected`.
- No dimension is recorded `fail`. A `fail` asserts an observed protocol-relevant
  behaviour the host could not deliver, and an incident observed no behaviour.
- The incident is recorded with its host error envelope fields, separately from
  behavioural evidence, and is never merged into it.
- The incident never explains away a missing artifact as though the artifact had
  existed.

The rubric prices the error directly: recording a 429 as a Product Finding scores
*Infrastructure-incident classification* 0, and calling a blocked arm delivered
scores *Blocked-closure honesty* 0. Phase 14's INC-1, INC-2, and INC-3 are the
worked examples, and none of them became a LoopPilot defect.

An EII on one arm does not stop the others if they remain independently
launchable. It does stop any claim that depends on the blocked arm.

### 5.12 Stop conditions

| Trigger | Action |
|---|---|
| Host version differs from the pin, at start or mid-run | Stop. Re-pin and restart, or record `BLOCKED / EII`. Never merge two versions |
| Injected-body digest ≠ repository digest | Stop. Loading is unproven and every downstream claim is void |
| `status.ps1` does not report `CURRENT` before the first arm | Stop. Install provenance is a precondition, not a detail |
| Rate limit, timeout, or empty output | `BLOCKED / EII` for that arm, per §5.11 |
| Operator intervenes inside a fixture context | That arm is void. Re-run it or record it blocked |
| Any dimension observed `fail` | Verdict is `rejected`. Route to a host-adapter note, trigger-tuning fix, or documented limitation. Never relax the gate |
| Independent reviewer unavailable | `Reviewer decision: not-reviewed`, record stays `unverified`. No self-signing |
| Context or budget pressure | Stop at the earliest safe boundary, preserve evidence, record the exact stop reason |

A stop is a result. None of these outcomes may be converted into acceptance, and
none may be answered by editing LoopPilot to make the observation disappear.

## 6. Explicit Non-Goals

This document does not, and the boundary it defines must not:

- create, upgrade, or imply a Host Acceptance Record, for `2.1.224` or any other
  combination;
- tick any RC gate, prepare a Release Candidate, create a tag, push, or release;
- modify `SKILL.md`, `AGENTS.md`, protocol semantics, validators, or tests;
- add a role, mode, Ledger, lifecycle state, Checkpoint, Barrier, acceptance
  dimension, or acceptance layer;
- perform Distribution-005 or any packaging experiment;
- execute any Phase 15 fixture — nothing here has been run;
- transfer the `2.1.224` result to a new boundary, or revise EVAL-001 through
  EVAL-005;
- resolve a gap by relaxing it, or answer a recorded host observation by tuning
  activation wording, triggers, or descriptions.

The last is worth stating twice. Implicit non-activation was observed once, at
`2.1.224`, and preserved unscored. Tuning LoopPilot so a future implicit arm
activates would destroy the observation and prove nothing.

## 7. Decision

```text
READY_FOR_NEW_ACCEPTANCE_BOUNDARY
```

**What this means.** The boundary in §5 is fully specified, and a candidate
execution surface exists: `claude --version` reports `2.1.232`, and the Phase 14
mechanism for spawning fresh non-self-observing contexts is proven to work at a
pinned version. The blocker that ended Phase 14 — no instantiable surface at the
pinned combination — is resolved by re-pinning to a version that can be
instantiated. What remains is authorization to execute, not a missing capability.

**What this does not mean.** It is not acceptance, not a verdict, not RC
readiness, and not a claim that the run will succeed. Three conditions remain
open, and readiness is asserted for the boundary, not for them:

1. The install provenance precondition in §5.3 is unmet today.
2. The score template gap in §5.7 must be closed before any trace can be scored
   against all four critical dimensions.
3. Organizational reviewer independence does not exist in this project and is not
   created by executing fixtures. It gates the record, not the run, and can be
   progressed in parallel.

Readiness was chosen over `BLOCKED_PENDING_EXECUTION_SURFACE` because that verdict
would assert that no surface can be instantiated, which is no longer true. It
would also be the wrong instrument: the remaining blockers are a preparation
step, a template defect, and a reviewer, none of which an execution surface
supplies.

**Does the `2.1.224` evidence transfer?** **No.** The new boundary starts empty.
Discovery, loading, and externally witnessed loading are established for Claude
Code `2.1.224` with `claude-opus-5` and for nothing else. A run at `2.1.232`
must re-establish all of it from its own transcripts, including the digest
comparison. The `2.1.224` result is not superseded, not revised, and not
extended; it simply does not travel. If the new boundary produces a stronger
result, that will be a second bounded evidence set, not a promotion of the first.

Until a run is authorized and executed, and a reviewer independent of its trace
author has judged it, the correct state of this project is the one already
recorded: Host Acceptance **UNVERIFIED**, RC Gate 4 **UNMET**, Release Candidate
**not approved**.
