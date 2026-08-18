# Phase 15 Execution Surface Design

A design and executability audit for an acceptance execution surface that can
satisfy [`phase15-acceptance-boundary.md`](phase15-acceptance-boundary.md) §5.3,
§5.5, and controls C1–C8. It is not an acceptance run, not a rubric score, not a
Host Acceptance Record, and not a Release Candidate.

**No state recorded here is upgraded.** Host Acceptance remains UNVERIFIED, RC
Gate 4 remains UNMET, no gate is ticked, and no fixture was executed. This
document changes no protocol, no `SKILL.md`, no `AGENTS.md`, no validator, no
test, and no distribution behavior. It introduces no role, mode, Ledger,
lifecycle state, Checkpoint, or acceptance dimension. It does not weaken C1–C8,
§5.8, or §5.12; where a control cannot be met, it records that as a blocker
rather than relaxing the control.

- Boundary: HEAD `9006a241fc79ca68082dcc5d17407b55c95b9433`, branch `main`,
  working tree dirty (7 modified, 1 untracked), nothing pushed.
- Governing boundary: [`phase15-acceptance-boundary.md`](phase15-acceptance-boundary.md).
- Governing procedure: [`docs/cross-host-acceptance.md`](../cross-host-acceptance.md).
- Rubric: [`tests/evaluation-rubric.md`](../../tests/evaluation-rubric.md).

Host mechanism details in §3–§8 were read from `claude --help` on the `2.1.233`
binary at `~/.local/bin/claude.exe`, because the pinned `2.1.232` image is only
reachable as the running operator process. Flag availability at `2.1.232` is
therefore **assumed, not verified**, and P0 of the pre-flight checklist (§11)
exists to verify it before anything depends on it.

## 1. Current Blockers

B1–B8 were established by direct observation on 2026-08-15 against the pinned
combination. B9–B11 are new, found while auditing whether B1–B8 could be
designed around, and each one is a conflict between two requirements that are
individually mandatory.

| ID | Blocker | Evidence | Class |
|---|---|---|---|
| **B1** | `status.ps1` reports `RECOVERY_REQUIRED`, not `CURRENT` | 4 conflicted files, 101 to add, state format unreadable, `.looppilot-installation` absent | Precondition, §5.12 row 3 |
| **B2** | Fixture cwd would be the repository | Operator session cwd is `C:\Users\tutic\IdeaProjects\LoopPilot` | C1 |
| **B3** | Acceptance material reachable from cwd | rubric, `evaluations/`, boundary, procedure all resolve; project memory auto-injected | C2 |
| **B4** | Operator context is not fresh | ~95 records, operator turns throughout, §5.5 expectation table already read | C3, C5 |
| **B5** | IMP-1 unfalsifiable in operator context | context knows implicit activation is the hypothesis under test | C7 |
| **B6** | FL-1R requires session termination and a fresh session | §5.5, C8 | Topology |
| **B7** | Score template lacks 2 of 4 critical dimensions | `Evidence integrity across agents`, `Authority continuity` absent from template table | §5.7 |
| **B8** | No independent reviewer exists | operator is trace author; §5.8 excludes same-operator sub-contexts | §5.8 |
| **B9** | **The Skill install places acceptance material inside the fixture-reachable Skill directory** | installed dir already contains `docs/cross-host-acceptance.md` and `docs/release/v1.0-rc-checklist.md`; a clean install adds `tests/evaluation-rubric.md` and the whole `evaluations/` corpus | **C2 vs §5.3, unresolved** |
| **B10** | `--bare` buys C2/C3 isolation but may make IMP-1 structurally unobservable | `--bare` skips auto-memory and CLAUDE.md discovery, but its help text states *Skills still resolve via `/skill-name`* | C7 vs C2 |
| **B11** | `--exclude-dynamic-system-prompt-sections` breaks C4 | it relocates cwd, env, memory paths, and git status **into the first user message**, so record 0 would no longer equal the prompt | C4 |

B9 is the most serious finding in this document and is developed in §4.3. It is
not solvable by topology.

## 2. Required Execution Topology

The surface is four processes that never share a context, orchestrated by an
operator who is never inside any of them, and judged by a reviewer who is not
the operator.

```text
operator (this process, 2.1.232)          ← orchestrates, never enters a fixture
  │
  ├─ prepares  src/      clean worktree @ 9006a24        (§8)
  ├─ installs  ~/.claude/skills/loop-pilot from src/     (§8)
  ├─ writes    prompts/LW-1.txt, FL-1.txt, FL-1R.txt, IMP-1.txt   (C4)
  │
  ├─ spawns ─▶ [P-probe]  reachability probe, throwaway  (§4.4)
  ├─ spawns ─▶ [LW-1 ]  cwd=sandbox/LW-1   fresh session, exits
  ├─ spawns ─▶ [FL-1 ]  cwd=sandbox/FL-1   fresh session, exits at Checkpoint
  ├─ spawns ─▶ [FL-1R]  cwd=sandbox/FL-1   fresh session, NOT a resume  (§6)
  └─ spawns ─▶ [IMP-1]  cwd=sandbox/IMP-1  fresh session, protocol-blind (§7)
                              │
                              ▼
                    host-emitted .jsonl transcripts
                              │
                    operator redacts + indexes           (trace author role)
                              │
                              ▼
                    sealed reviewer package              (§9)
                              │
                              ▼
                    independent reviewer, not the operator
```

Three properties of this topology are load-bearing and are the reason it is
processes rather than sub-contexts:

1. **A separate OS process cannot inherit a conversation.** C3 is satisfied
   structurally, not by discipline.
2. **`-p` / `--print` is non-interactive and exits after one input.** C5 is
   satisfied structurally: there is no mechanism by which the operator could
   take a turn inside the arm, because the process is gone.
3. **Working directory is a process property.** C1 becomes a launch parameter
   rather than a request, which is what the EVAL-005 sidechains could not do —
   they inherited the repository cwd, which is the residual C1 exists to close.

**Why not subagents.** Phase 14 spawned sidechains (`isSidechain: true`,
`agent-*.jsonl`). They gave fresh contexts and non-self-observation, and that is
why class A survived. They cannot give C1: a subagent inherits the parent's
working directory, and no subagent mechanism accepts a cwd override. Worktree
isolation does not help, because a worktree of this repository is still this
repository. Subagents are therefore sufficient for loading evidence and
insufficient for any dimension 2–8 claim, exactly as §5.10 C1 states.

## 3. Repository Isolation Strategy (C1)

### 3.1 Layout

Every path below is outside the repository and outside the checkout used to
install.

```text
%LOCALAPPDATA%\Temp\lp-accept\
  src\                 clean detached worktree @ 9006a24    (install source only)
  sandbox\LW-1\        fixture working directory
  sandbox\FL-1\        fixture working directory, shared by FL-1 and FL-1R
  sandbox\IMP-1\       fixture working directory
  prompts\             prompt files, hashed before the run
  out\                 host-emitted transcripts
```

`sandbox\*` are the only directories any fixture process runs in. They start
empty except for whatever the fixture scenario legitimately requires, which for
scenarios 68, 69, and 53 is an ordinary small work tree with no LoopPilot
content in it.

### 3.2 Launch discipline

- Process working directory is set to the sandbox path **before** launch. It is
  not changed by the prompt.
- `--add-dir` is **never** passed. Its only effect would be to widen tool access,
  which is the opposite of C1.
- The install source `src\` is deleted after installation and before the first
  arm, so no fixture can reach a checkout even by absolute path.

### 3.3 Verification, not declaration

C1 is verified from the host's own output, after the fact:

| Check | Source | Pass condition |
|---|---|---|
| cwd is the sandbox | `cwd` field, every record of the arm transcript | equals the sandbox path exactly, on 100% of records |
| cwd is not the repository | same field | no record contains the repository path as a prefix |
| no widened access | launch command, recorded in `environment.md` | `--add-dir` absent |
| checkout gone | filesystem, timestamped before first arm | `src\` does not exist |

The cwd field is already the field EVAL-005 used to establish that its fixtures
ran as separate contexts, so this reuses an audited signal rather than inventing
one.

## 4. Context Isolation Strategy (C2)

### 4.1 What must be unreachable

`tests/evaluation-rubric.md`, `tests/scenarios.md`, `evaluations/` in any form,
`docs/cross-host-acceptance.md`, `docs/release/phase15-acceptance-boundary.md`,
this document, every prior Host Acceptance Record, and the project memory index.

### 4.2 Mechanisms

| Control | Mechanism | Effect |
|---|---|---|
| Project settings | cwd outside the repo | `.claude/settings.local.json` is never discovered |
| Project memory | cwd outside the repo | the memory index is keyed to the project directory; a different cwd resolves a different, empty one |
| `CLAUDE.md` | no `CLAUDE.md` is placed in any sandbox | nothing to discover |
| Setting sources | `--setting-sources user` | project and local sources excluded explicitly rather than incidentally |
| MCP | `--strict-mcp-config` with no `--mcp-config` | no external tool surface |
| Repository paths | §3.2, plus `src\` deleted | not reachable by relative or absolute path |

`--bare` is **not** adopted as the default mechanism. It would close the memory
and `CLAUDE.md` vectors more forcefully, but B10 makes it unsafe for IMP-1 and
§7.3 explains why using it for some arms and not others would make the arms
incomparable.

### 4.3 B9 — the unresolved conflict, stated plainly

**Superseded, and preserved unedited.** B9 was resolved after this section was
written: the payload manifest was narrowed and a fresh install now carries no
acceptance path, per
[`phase15-b9-packaging-boundary-design.md`](phase15-b9-packaging-boundary-design.md)
§9. The mutual exclusion this section states no longer holds, and the counts
below describe the superseded 161-file payload. The analysis is kept as written
because §4.4 check B exists to guard the property it identified.

§5.3 requires installing the Skill from a clean checkout at the pinned commit
using `install.ps1`. The distribution's managed set is 29 entries, and it
expands to a tree that includes acceptance material. This is observed, not
predicted:

```text
currently installed at ~/.claude/skills/loop-pilot  (60 files)
  docs/cross-host-acceptance.md            ← the governing acceptance procedure
  docs/release/v1.0-rc-checklist.md        ← the gate definitions

a clean install at 9006a24 additionally adds  (status.ps1 ADD list, 101 files)
  tests/evaluation-rubric.md               ← the rubric itself
  tests/scenarios.md                       ← the numbered scenarios
  evaluations/claude-code/EVAL-001..005/   ← every prior trace and score
  evaluations/templates/score.md           ← the scoring template
  docs/evaluations/claude-code/HOST-ACCEPTANCE-*.md
  docs/release/phase14-*.md
```

The Skill directory is reachable from every fixture context by construction —
that is how `SKILL.md` resolves its 60 relative references, and the Skill under
test cannot function without it. So a clean install per §5.3 puts the rubric,
the scenarios, and all five prior evaluation packages one relative path away
from a fixture that C2 requires cannot read any of them.

**A correctly installed Skill and a C2-compliant fixture context are mutually
exclusive under the current managed set.** Three exits exist, and this document
takes none of them:

| Exit | What it requires | Status |
|---|---|---|
| Trim the managed set so acceptance material is not distributed | `distribution/managed-files.txt` change | Forbidden: distribution implementation is frozen |
| Add an install profile that omits acceptance material | distribution implementation change | Forbidden, same reason |
| Scope C2 to the fixture working directory and record Skill-directory reachability as a disclosed residual | amending C2 | Forbidden: C1–C8 may not be weakened here |

This is an owner decision. Until it is made, **no dimension 2–8 claim can be
C2-clean**, and the surface designed in this document cannot produce
Gate-4-capable evidence no matter how well every other control is met.

Worth separating from the alarm: this does not mean a fixture *would* read those
files. It means the run could not evidence that it did not, and C2 exists
precisely because "it probably didn't" is not evidence.

### 4.4 Verifying unreachability rather than asserting it

C2 has **two scopes**, and this section originally checked only one. The fixture
working directory is the obvious scope. The installed user-scope Skill directory
is the other, because §4.3 establishes that it is reachable from every fixture
context by construction — that is how `SKILL.md` resolves its relative
references. A control verified in one scope and assumed in the other is assumed,
not verified.

Three checks, two static and one host-emitted. None is a claim by the operator.

**Static check A — the sandbox, before each arm.** Enumerate the sandbox tree
and every path reachable from it without traversing above it, and assert that no
prohibited filename appears. Assert that no `CLAUDE.md` exists in the sandbox or
any ancestor up to the drive root. Record the enumeration and its digest in
`environment.md`.

**Static check B — the installed Skill directory, before the first arm.**
Enumerate the whole installed tree and assert that no §4.1 path appears anywhere
in it. Run by
[`scripts/c2_isolation_validation.py`](../../scripts/c2_isolation_validation.py):

```text
python scripts/c2_isolation_validation.py --destination "$HOME\.claude\skills\loop-pilot"
```

The pass condition is `State: C2_CLEAN` with `Findings: 0` and exit status 0.
Four properties of that check are load-bearing:

1. **It enumerates the tree, not the manifest.** Every acceptance file became
   unmanaged when the payload manifest narrowed, so a managed-set computation
   cannot see one. The check never reads `.looppilot-installation`.
2. **It matches path suffixes, not destination-relative paths.** A backed-up
   file lives at `.looppilot-backups/<operation-id>/<original path>`, so a
   prohibited path appears below a backup root rather than at the tree root.
   Equality against the §4.1 list would enumerate a whole backed-up corpus and
   report nothing. Suffixes are generated to any depth, because a snapshot can
   contain a snapshot.
3. **It covers hidden directories and never traverses a symbolic link.**
   `.looppilot-backups/` is the exposure B13 named, and it is hidden by
   convention rather than by attribute.
4. **It verifies the property, not the procedure.** It asks what the tree
   contains, never how the tree was produced. Any install, reinstall, or upgrade
   path is admissible when its result passes, and none is admissible because of
   its name.

**`status` reporting `CURRENT` is not a sufficient condition for C2 isolation.**
`CURRENT` quantifies over managed files — `docs/installation.md` defines it as
"Every **managed** file matches the source, and the recorded revision and
manifest match it too" — and after the §4.3 manifest narrowing every acceptance
file is unmanaged. The two predicates therefore quantify over disjoint domains,
and neither implies the other: a tree can be `CURRENT` while holding the whole
corpus, and a C2-clean tree with one edited managed file reports
`LOCAL_MODIFICATIONS`. Both checks are required and neither substitutes for the
other. Measured, on two real installations built from the pinned commit:

| Tree | How it was produced | `status.ps1` | Static check B | Findings |
|---|---|---|---|---:|
| Clean install | destination absent, then `install.ps1` | **CURRENT** | **C2_CLEAN** | 0 |
| Upgraded install | pre-narrowing install, then `update.ps1` | **CURRENT** | **C2_CONTAMINATED** | **79** |

All 79 findings on the upgraded tree sit under `.looppilot-backups/<id>/`, and
none at a normal path — so property 2 is the only reason they are visible at
all. This is not a Distribution-004 defect: managed-set scoping is correct
behavior and is why user content survives upgrades. It is a statement about what
`CURRENT` can attest, and it must not be answered by changing what `status`
does.

**Negative reachability probe, host-emitted.** A throwaway session — `P-probe`,
never an acceptance arm — is launched in a sandbox with a prompt that instructs
it to attempt to read each prohibited path and report the raw tool result. Its
transcript then contains the host's own `tool_result` error envelopes as
first-party evidence of non-reachability.

Four rules keep the probe from contaminating what it verifies:

1. It runs in a sandbox that is discarded afterwards, never in `LW-1`, `FL-1`,
   or `IMP-1`.
2. It runs before the arms, and its sandbox is recreated empty for the real arm.
3. Its output is classified as infrastructure evidence under §5.10, never
   merged into a behavioural set.
4. It names no LoopPilot protocol vocabulary, so that it cannot be mistaken for,
   or contaminate, the IMP-1 observable.

The probe cannot prove a negative in general. It proves that the specific paths
C2 names returned errors from that host, in that sandbox, at that time — which
is what a checkable control needs and is strictly more than a declaration.

## 5. Fresh-Session Strategy (C3 / C5)

### 5.1 Invocation shape

Design only; not executed. One process per arm, launched with cwd set to the
arm's sandbox.

```text
claude -p
  --session-id <uuid-per-arm>
  --model claude-opus-5
  --output-format stream-json --verbose
  --setting-sources user
  --strict-mcp-config
  --permission-mode <fixed per arm, recorded>
  < prompts/<ARM>.txt
```

| Flag | Why |
|---|---|
| `-p` | non-interactive; the process exits after one input, which is what makes C5 structural |
| `--session-id` | the transcript is locatable deterministically, so evidence collection needs no guessing |
| `--model claude-opus-5` | pins the model at the arm boundary rather than inheriting an alias |
| `--output-format stream-json` | the host writes the trace; the operator never authors it |
| `--setting-sources user` | C2, §4.2 |

**Forbidden flags, and why each would void an arm:**

| Flag | Effect | Control violated |
|---|---|---|
| `--resume`, `--continue`, `--fork-session` | inherits a prior conversation | C3, and C8 for FL-1R |
| `--add-dir` | widens tool access | C1 |
| `--exclude-dynamic-system-prompt-sections` | moves cwd/env/memory/git into the **first user message** | C4 — record 0 would stop equalling the prompt (B11) |
| `--append-system-prompt`, `--system-prompt` | injects operator framing into the arm | C3, C5 |
| `--agents` | supplies operator-authored context | C3 |

### 5.2 C4 double attestation

1. Write the prompt to `prompts/<ARM>.txt` before the run; record its SHA-256.
2. After the run, extract record 0's user text from the transcript; hash it.
3. The two digests must be equal. A mismatch voids the arm — it means the host
   saw something other than the attested prompt.

B11 is the reason this check has teeth: there is a real, available flag that
would silently break it, so the check is not ceremonial.

### 5.3 What this does not close

C3 requires the context inherit no prior conversation. A fresh process
guarantees that. It does **not** guarantee the model brings no priors — nothing
can, and no control claims otherwise. The observable is the context, not the
weights.

## 6. FL-1R Lifecycle

FL-1R is the only path to dimension 6, and dimension 6 at `not-evaluated` is
forbidden under both evidence verdicts. So the fresh-session requirement is not
a convenience to be traded away; without it there is no Gate 4.

```text
[FL-1]   cwd = sandbox/FL-1   session S1
         runs scenario 69 to a Checkpoint
         process exits                      ← session terminated, not paused
              │
              │  the only thing that crosses: the filesystem
              │  sandbox/FL-1/.looppilot/ Checkpoint + work tree state
              ▼
[FL-1R]  cwd = sandbox/FL-1   session S2   (new --session-id)
         scenario 53, Resume Revalidates Reality
         NOT --resume, NOT --continue, NOT --fork-session
```

The distinction that makes this valid: `--resume` would carry S1's conversation
into S2, and dimension 6 would then be observing a context that already
remembers what it did. C8 requires the resume leg's only inputs be the
Checkpoint and the repository state. A new session in the same directory
delivers exactly that, which is the protocol's own Checkpoint machinery
exercised as designed rather than simulated.

**Verification that FL-1R was genuinely fresh:**

| Check | Pass condition |
|---|---|
| Session identity | `sessionId` of every FL-1R record ≠ S1 |
| Chain origin | FL-1R record 0 has no `parentUuid`, and its `uuid` appears nowhere in the FL-1 transcript |
| Record 0 content | equals `prompts/FL-1R.txt` byte for byte, per §5.2 |
| No resume flag | launch command recorded in `environment.md`; `--resume`/`--continue`/`--fork-session` absent |
| Checkpoint really crossed | the Checkpoint file FL-1R reads exists in `sandbox/FL-1/.looppilot/` with an mtime between S1 exit and S2 start |

**If FL-1 does not reach a Checkpoint, FL-1R does not run.** It is not
substituted, not simulated, and no Checkpoint is hand-written for it to resume
from — that would be reconstructing evidence. FL-1 blocked means FL-1R blocked
means dimension 6 `not-evaluated` means the record stays `unverified`.

## 7. Protocol-Blind IMP-1 Strategy (C7)

### 7.1 Prompt blindness, machine-checked

The prompt must contain no protocol vocabulary and must not name the Skill. C7
names the banned terms; the check is automated and runs before the arm:

```text
banned (case-insensitive, whole-word):
  LoopPilot, loop-pilot, Skill, activation, activate, rubric, acceptance,
  Lightweight, Full Loop, Ledger, Contract, Checkpoint, Barrier, mode,
  evaluation, fixture, protocol
```

The scan runs against `prompts/IMP-1.txt`, and its result plus the file digest
are recorded before the run. A hit voids the prompt, not the check.

### 7.2 Context blindness

The prompt is only half of C7. The context must also not *know* it is being
measured for implicit activation — which is precisely why IMP-1 cannot run in
the operator process (B5) and why no operator turn may enter it (C5). A fresh
`-p` process satisfies both: it receives the prompt and nothing else, and it
cannot be told anything afterwards.

### 7.3 B10 — the `--bare` tension

`--bare` is attractive for C2: it skips auto-memory and `CLAUDE.md`
auto-discovery outright. But its documented behavior states *Skills still
resolve via `/skill-name`*, which reads as explicit invocation only. If implicit
surfacing is disabled under `--bare`, then an IMP-1 run under `--bare` would
observe **nothing** — and a null observation from a mechanism that was switched
off is not evidence of non-activation. It would be the single most misreadable
artifact this run could produce.

Two consequences:

1. **IMP-1 must not run under `--bare`** unless P2 (§11) empirically shows
   implicit surfacing still occurs under it.
2. **All four arms use the same flag set.** Running explicit arms under `--bare`
   and IMP-1 without it would make the arms incomparable, and dimension 1's two
   halves would be evidenced against different host configurations.

P2 resolves this with a probe that uses an unrelated third-party Skill, never
`loop-pilot`, so that determining whether implicit surfacing works does not
consume the IMP-1 observable.

### 7.4 The result that must not be repaired

Implicit non-activation was already observed once, at `2.1.224`, and preserved
unscored. If IMP-1 at `2.1.232` also shows non-activation, that is a finding to
record, not a defect to fix. Tuning `SKILL.md` triggers or description wording
so a later implicit arm activates would destroy the observation and prove
nothing — §6 of the boundary states this, and it is repeated here because this
is the document that would otherwise be read as a licence to engineer the
surface until the arm passes.

## 8. Clean-Install Strategy (B1)

### 8.1 Why the current install cannot be repaired in place

`status.ps1` reports `RECOVERY_REQUIRED`, state format unreadable, installed
version and commit `unknown`, 4 conflicted files, 101 missing, and no
`.looppilot-installation`. There is no provenance to repair; there is only an
unprovenanced tree to replace.

### 8.2 Procedure

Design only; not executed. Every step is machine-checkable and none of it
touches the repository working tree.

```text
1.  git worktree add --detach %LOCALAPPDATA%\Temp\lp-accept\src 9006a241fc79…
2.  verify:  git -C src rev-parse HEAD == 9006a241fc79…
             git -C src status --porcelain  is empty
3.  clear the existing ~/.claude/skills/loop-pilot
4.  src\install.ps1 -Destination "$HOME\.claude\skills\loop-pilot"
5.  status.ps1 -Destination "$HOME\.claude\skills\loop-pilot"  MUST say CURRENT
6.  c2_isolation_validation.py --destination "$HOME\.claude\skills\loop-pilot"
                                                               MUST say C2_CLEAN
7.  verify .looppilot-installation exists and records commit 9006a241fc79…
8.  verify SKILL.md body-sha256 == 530bbaf7…46a
9.  git worktree remove src   (and confirm the path is gone, §3.2)
```

Step 1 is what keeps the 7 working-tree modifications out of the acceptance
surface: a detached worktree at the pinned commit is a clean tree by
construction, and `--porcelain` emptiness in step 2 proves it rather than
assuming it.

**Step 3 is deliberately not prescribed as a particular command, and step 6 is
why.** Step 5 alone cannot tell a clean destination from a contaminated one, so
naming a procedure here would substitute a believed-clean procedure for a
checked-clean result. Step 6 adjudicates instead. Two consequences follow from
the measurements in §4.4, and they are recorded as observations rather than as
rules:

- `uninstall.ps1` does not empty a destination. It removes recorded managed
  files and preserves "modified files, user-created files, backup files, and
  directories" by design, so on a directory that already holds unmanaged
  acceptance material it leaves that material in place and step 6 fails.
- `update.ps1` clears the normal paths and preserves what it removed under
  `.looppilot-backups/`, so it also fails step 6.

An operator therefore reaches step 6 green by removing the destination
directory, but that is the measured consequence of the gate rather than a
procedure this document mandates.

### 8.3 The frozen-combination caveat

The frozen combination names an *installed user-scope Skill*. Replacing the
current installation changes that leg. This is correct and required — §5.3 calls
the present installation's provenance not machine-checkable, and an
unprovenanced install cannot anchor an acceptance record — but it must be done
**before** the pin is asserted for the run, recorded in `environment.md`, and
never mid-run. §5.12 forbids mixing, and swapping the Skill between arms would
be exactly that.

### 8.4 What step 5 does not resolve

**`CURRENT` does not close B1 on its own, and never did.** It attests that the
managed projection matches the source, which is the provenance half of the
problem — it is what makes `.looppilot-installation` present and the commit
recorded. It attests nothing about the rest of the tree, and after the §4.3
manifest narrowing the acceptance corpus is entirely outside the projection it
quantifies over. Step 6 is what closes the other half, and §4.4 measures both
states to show the two checks are independent rather than redundant.

B9 is closed by the manifest change recorded in
[`phase15-b9-packaging-boundary-design.md`](phase15-b9-packaging-boundary-design.md)
§9, so the original form of this section — that a clean install *worsens* B9 by
adding the rubric, the scenarios, and the `evaluations/` corpus to the
fixture-reachable Skill directory — no longer describes the payload. A fresh
install now carries 81 files and no acceptance path. What survives of that
finding is narrower and is B13: the corpus persists on the **upgrade** path,
under `.looppilot-backups/`, which is precisely the state step 6 exists to
detect.

## 9. Independent-Review Strategy (B8)

### 9.1 What does not qualify

§5.8 is explicit, and the exclusions are not negotiable here: not the operator,
not a subagent the operator spawns, not a sub-context of the same model under
the same operator. The Phase 13 reviewer was the last of these, found real
errors, and said itself it had no organizational independence. Claiming
unavailable independent review scores *Reviewer-availability honesty* 0.

### 9.2 The reviewer input set, as a sealed package

The reviewer receives exactly this and nothing else:

```text
review-package/
  environment.md        host, version, model, loading mode, cwd, constraints
  prompt.md             the four prompts verbatim
  trace.md              excerpts anchored to record positions
  evidence/             redacted transcripts + README with digests
  evidence-index.md     every artifact, its verification type, its limits
  score.md              BLANK template
  evaluation-rubric.md  copy of tests/evaluation-rubric.md
  cross-host-acceptance.md
```

**Must not be included:** `phase15-acceptance-boundary.md`, this document, any
prior Host Acceptance Record, any prior `score.md`, the §5.5 expected-results
table, or any operator commentary. The boundary's expectation table in
particular would tell a reviewer which results were anticipated, which is the
difference between a review and a confirmation.

Machine-checkable in both directions: a manifest with per-file digests proves
what was delivered, and an assertion that the prohibited filenames are absent
from the package tree proves what was not.

### 9.3 Candidate reviewer paths

| Path | Independence | Practicality |
|---|---|---|
| A second person, not the operator, applying the rubric | Real, satisfies §5.8 | Requires a person; the project has one operator |
| A different organization or contracted reviewer | Strongest | Highest cost |
| Model instance under a **different** operator, who receives only the sealed package | Partial — different operator, different session, no shared context | Depends on a second human to run it; that human is the reviewer of record |
| Operator-spawned subagent | **None** | Explicitly excluded |

Only the first three are admissible. The third is the weakest admissible form
and its limitation must be disclosed in the record, because the reviewer of
record is the human who ran it, not the model.

### 9.4 The honest outcome if none is available

`Reviewer decision: not-reviewed`, and the record stays `unverified`. That is a
complete, correct result. It is not a failure of the run and it must not be
answered by promoting a weaker reviewer into the field.

**Reviewer independence gates the record, not the run.** The four arms can be
executed and preserved while no reviewer exists; the evidence does not spoil.
This is the one blocker that can be progressed entirely in parallel, and the one
most likely to remain open longest.

## 10. Score-Template Gap (B7)

### 10.1 The gap, precisely

`docs/cross-host-acceptance.md` names four critical rubric dimensions that must
each score 2 or higher on every scored trace, with the record disclosing the
lowest observed critical score.

| Critical dimension | Defined in rubric | Present in `evaluations/templates/score.md` |
|---|---|---|
| Safety | yes | **yes** |
| Completion honesty | yes | **yes** |
| Evidence integrity across agents | yes, line 22, full 0–3 anchors | **no** |
| Authority continuity | yes, line 23, full 0–3 anchors | **no** |

The rubric is complete. Only the template's dimension table is short. A
`score.md` filled from the template as it stands would disclose a lowest
critical score computed over two of four critical dimensions, resting on two
that were never scored.

### 10.2 Minimal fix, reported and not applied

Two rows added to the dimension table in
[`evaluations/templates/score.md`](../../evaluations/templates/score.md):

```text
| Evidence integrity across agents |  |  |
| Authority continuity |  |  |
```

Nothing else changes: no rubric text, no anchors, no validator, no weighting, no
new dimension. The rubric already defines both, so this transcribes an existing
definition into the form that collects it.

**Not applied here.** §5.7 states the freeze permits the fix and that the
boundary document does not perform it; that is permission for the class of
change, not an instruction to make it in this document, and this document is
limited to one new file. The fix is a prerequisite for scoring, not for
execution — arms may run and be preserved before it lands, and only `score.md`
authoring is blocked until it does.

## 11. Pre-Flight Checklist

Every item is machine-checkable and must pass before the arm it gates. An item
that cannot be checked is treated as failed.

| # | Gate | Pass condition | Gates |
|---|---|---|---|
| **P0** | Pinned binary flags | `2.1.232` supports `-p`, `--session-id`, `--setting-sources`, `--output-format stream-json`, `--strict-mcp-config`, `--model` | everything |
| **P1** | Host and model | `version` = `2.1.232` and `message.model` = `claude-opus-5` on 100% of records, every arm | everything |
| **P2** | Implicit surfacing works | probe with an unrelated Skill shows implicit surfacing under the chosen flag set | IMP-1 (B10) |
| **P3** | Clean checkout | `src` at `9006a241fc79…`, `git status --porcelain` empty | install |
| **P4** | Install state | `status.ps1` = `CURRENT`; `.looppilot-installation` present and naming the pinned commit; **and `c2_isolation_validation.py` reports `C2_CLEAN` with `Findings: 0`** | first arm (B1) |
| **P5** | Skill digest | installed body-sha256 = `530bbaf7…46a` | first arm |
| **P6** | Checkout removed | `src` does not exist | first arm (C1) |
| **P7** | cwd isolation | sandbox path outside the repository; no `CLAUDE.md` in it or any ancestor | each arm (C1) |
| **P8** | Static unreachability | no prohibited filename in the sandbox tree, per §4.4 check A. The Skill directory is the other C2 scope and is gated by P4 | each arm (C2) |
| **P9** | Probe unreachability | `P-probe` transcript shows host errors for every prohibited path | each arm (C2) |
| **P10** | **B9 resolved** | an owner decision exists on the Skill-directory acceptance material | **each arm (C2)** |
| **P11** | Prompt attested | prompt file digest recorded before the run | each arm (C4) |
| **P12** | IMP-1 vocabulary | banned-term scan on `prompts/IMP-1.txt` returns zero hits | IMP-1 (C7) |
| **P13** | Flag hygiene | no forbidden flag from §5.1 in any launch command | each arm |
| **P14** | Score template | both critical rows present | `score.md` authoring only (B7) |
| **P15** | Reviewer | an admissible reviewer per §9.3 is identified | record assembly only (B8) |

P10 has no defined pass condition in this document on purpose. It is the one
gate that requires a decision rather than a check, and inventing a threshold for
it here would be exactly the self-authorization §5.8 and §5.12 forbid.

## 12. Conditions Under Which Phase 15 May Execute

Execution of the four arms may begin when, and only when:

1. **P0–P9 and P11–P13 pass**, verified and recorded, not asserted. P4 now
   carries the Skill-directory C2 assertion as well as the provenance one, so
   the clean reinstall is gated on a checked property rather than on a named
   procedure.
2. **P10 is resolved.** The owner decision on B9 was taken and implemented: the
   payload manifest no longer carries the acceptance corpus, and a fresh install
   is verified C2-clean by enumeration. The residual the decision disclosed is
   recorded in
   [`phase15-b9-packaging-boundary-design.md`](phase15-b9-packaging-boundary-design.md)
   §9.5 and is a documentation residual, not a control failure.
3. **The pin holds at the moment of each launch.** §5.1 rule 1 is re-applied per
   arm, not once for the run.
4. **The operator accepts the trace-author role and only that role**, with
   scoring deferred to §9.

Two things explicitly do **not** block execution, and confusing them with
blockers would stall the run for no gain:

- **B7** blocks `score.md` authoring, not arm execution. Traces preserved before
  the template is fixed remain scorable afterwards.
- **B8** blocks the record, not the run. Arms may execute and be preserved with
  no reviewer in existence.

**Gate 4 remains unreachable even on a fully successful run** unless FL-1
reaches a Checkpoint and FL-1R resumes from it, because dimension 6 has no other
source and `not-evaluated` is forbidden under both evidence verdicts. A run that
completes LW-1, FL-1, and IMP-1 but not FL-1R is a legitimate, useful evidence
set and is not Gate-4-capable. That should be decided before the run, not
discovered after it.

## 13. Conditions Under Which Execution Must STOP

§5.12 governs unchanged. This section adds only the surface-specific triggers
this design introduces, and weakens none of the originals.

| Trigger | Action |
|---|---|
| `version` ≠ `2.1.232` or `model` ≠ `claude-opus-5`, at any arm boundary or mid-arm | Stop. Never merge two combinations. Re-pin and restart, or record `BLOCKED / EII` |
| `status.ps1` ≠ `CURRENT` before the first arm | Stop. Provenance is a precondition |
| `c2_isolation_validation.py` ≠ `C2_CLEAN` before the first arm | Stop. C2 failed in the Skill-directory scope. Clear the destination and reinstall; never proceed by disclosure, and never answer it by narrowing the check |
| Injected-body digest ≠ `530bbaf7…46a` | Stop. Loading unproven, every downstream claim void |
| Record 0 ≠ attested prompt digest | That arm is void. Re-run or record blocked |
| A forbidden flag appears in a launch command | That arm is void |
| `cwd` on any record is inside the repository | That arm is void — C1 failed |
| A prohibited path is reachable from a sandbox | Stop. C2 failed; do not proceed by disclosure |
| P10 unresolved | Do not start. Dimension 2–8 evidence would be unusable |
| IMP-1 banned-term scan returns a hit | Fix the prompt and re-attest before running; never run and disclose |
| FL-1 does not reach a Checkpoint | FL-1R does not run. No Checkpoint is authored for it |
| Rate limit, timeout, empty output | `BLOCKED / EII` for that arm, per §5.11 |
| Operator input enters a fixture context | That arm is void |
| Independent reviewer unavailable | `Reviewer decision: not-reviewed`, record stays `unverified`. No self-signing |
| Context or budget pressure | Stop at the earliest safe boundary, preserve evidence, record the exact reason |

A stop is a result. None of these may be converted into acceptance, and none may
be answered by editing LoopPilot so the observation disappears.

## 14. What This Document Does Not Establish

It establishes no host behavior, because no fixture ran. It does not close B7 or
B8. It creates no `EVAL-006`, no `trace.md`, no `score.md`, and no Host
Acceptance Record. It does not transfer the `2.1.224` evidence, does not revise
EVAL-001 through EVAL-005, and does not treat the current operator session,
`deepseek-v4-pro`, or any Phase 14 artifact as new acceptance evidence.

Two blockers it originally left open have since been closed, each by a separate
record rather than by this document's own argument. **B9** is closed by the
manifest narrowing in
[`phase15-b9-packaging-boundary-design.md`](phase15-b9-packaging-boundary-design.md)
§9. **B1** is closed by §4.4 check B and the P4 pass condition, which convert the
clean reinstall from an unverifiable procedure into a checked property; the
reasoning is recorded in
[`phase15-b1-clean-reinstall-decision-analysis.md`](phase15-b1-clean-reinstall-decision-analysis.md).
The distribution measurements behind both are packaging mechanics observed
outside any acceptance arm, and neither scores a dimension.

Host Acceptance remains **UNVERIFIED**. RC Gate 4 remains **UNMET**. Release
Candidate remains **not approved**.

The remaining blockers are B7, B8, and B10. B7 and B8 gate the score and the
record rather than the run; B10 is the one open tension that gates an arm, and
it gates only `IMP-1`.
