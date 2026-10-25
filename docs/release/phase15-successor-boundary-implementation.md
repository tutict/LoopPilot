# Phase 15 Successor Boundary — Authorization Implementation

The Owner decision selecting a host mechanism for the Authorized Operation Set,
the single freeze clause that selection amends, and the conformance
measurements that establish the mechanism satisfies every requirement the AOS
specification states. It is not an acceptance run, not a rubric score, not a
Host Acceptance Record, and not a Release Candidate.

**No state recorded here is upgraded.** Host Acceptance remains UNVERIFIED, RC
Gate 4 remains UNMET, no gate is ticked, and **no fixture was executed** — not
`LW-1`, `FL-1`, `FL-1R`, or `IMP-1`. This document creates no `EVAL-006`, no
`trace.md`, no `score.md`, and no Host Acceptance Record. It changes no
`SKILL.md`, no `AGENTS.md`, no activation protocol, no rubric, no scenario
semantics, no scoring semantics, no Gate 4 semantics, no Distribution-004
semantics, no verdict rule, and no acceptance dimension. It amends no control
C1–C8 and weakens none. It re-pins nothing — not the host version, not the
model, not the binary, not the Skill, not the commit.

- Boundary: HEAD `89b1a1f3b22badc9b300eab6c4a2906b47d1728f`, branch `main`,
  working tree dirty, nothing pushed.
- Primitive definition: [`successor-boundary-authorized-operation-set.md`](successor-boundary-authorized-operation-set.md).
- Governing surface design: [`phase15-execution-surface-design.md`](phase15-execution-surface-design.md).
- Governing correction: [`phase15-execution-surface-correction.md`](phase15-execution-surface-correction.md).
- Prompt contract: [`phase15-fixture-prompt-contract.md`](phase15-fixture-prompt-contract.md).
- Phase 15 closure: [`phase15-owner-classification-record.md`](phase15-owner-classification-record.md).

## 1. Why This Document Exists

`successor-boundary-authorized-operation-set.md` defined the Authorized
Operation Set and then deliberately stopped: its §7 read *"No host mechanism is
selected"* and named the selection as a separate Owner decision. The preflight
that followed confirmed the deferral was load-bearing rather than an oversight —
every technically capable mechanism was either forbidden by a standing clause or
withheld by that deferral, so no mechanism could be derived without inventing
one.

That Owner decision has now been taken. This document records it, implements it,
and measures it.

## 2. Owner Decision, Recorded

| Field | Value |
|---|---|
| Decision | **Implement the Authorized Operation Set. Authorize AOS-1 and AOS-2 and nothing else** |
| Mechanism | **`--allowedTools`, carrying three narrow `Bash(...)` specifiers** |
| Permission mode | `acceptEdits`, **unchanged**; not broadened, no `bypassPermissions`, no `dontAsk`, no interactive approval |
| Settings files | **Untouched.** No `permissions` block added to `~/.claude/settings.json`; `--setting-sources user` unchanged |
| Second flag | **None.** `--disallowedTools` is available on the pinned image and is **not used** — §5.2 explains why it is unnecessary rather than merely omitted |
| Frozen execution leg | **Unchanged.** Binary, model, Skill loading mode, commit, Skill digest all as pinned |
| Four scoped legs | **Unchanged** |
| C1–C8 | **Unchanged, none weakened** |
| Fixtures executed | **None** |

### 2.1 Why this mechanism is the one the Owner decision permits

The Owner decision prohibits by enumeration rather than permitting by name, so
the selection is a derivation and is stated as one. Five mechanisms were
candidates; four are struck by the decision's own prohibition list, and the
prohibitions are quoted rather than paraphrased.

| Candidate | Struck by |
|---|---|
| Broaden `--permission-mode` | *"broaden permission-mode beyond acceptEdits"* |
| `bypassPermissions` | *"use bypassPermissions"* |
| `dontAsk` | *"use dontAsk"* |
| Interactive approval | *"use interactive approval"* |
| Project / local settings sources | Would change `--setting-sources user`, a C2 mechanism (design §4.2); *"weaken C2"* |

Two survive the prohibition list: `--allowedTools`, and a `permissions.allow`
block in `~/.claude/settings.json`. The second is struck by requirements the
decision states positively rather than by its prohibition list:

- **Requirement 6** — *"Preserve the distinction between the frozen
  host/model/Skill execution leg and the successor acceptance-boundary
  authorization leg."* A settings-file grant is ambient: it is inherited by every
  session on this machine, not only by the four arms, and it mutates an
  environment leg rather than an authorization leg. A flag is per-launch and
  belongs to the arm alone.
- **Requirement 8** — *"The authorization must remain observable and recordable
  as part of Dimension 3."* The launch command is already a recorded artifact
  under design §3.3; a settings file at run time is not, and its state at the
  moment of each launch would have to be attested separately.
- **Standing rejection.** Prompt-contract §10.2 already declined it on the
  record: *"would change an environment leg every arm inherits, mid-preparation,
  after the pin was asserted."* The Owner decision does not overturn that
  rejection, so it stands.

**Exactly one candidate survives, and it is `--allowedTools`.** The derivation is
recorded rather than asserted so it can be overturned in one line if the Owner
intended the other survivor.

`--allowedTools` was also the mechanism the specification named as the thing it
would not choose *until the specification explicitly defined it*
(AOS §7, original text). Requirement 4 instructs that definition to be written.
Writing it is therefore the discharge of the deferral, not a circumvention of it.

## 3. The Mechanism, Exactly

### 3.1 Flag surface, read from the pinned image

Read from `--help` on the pinned `2.1.232` image itself, per the P0 precedent in
correction §6.1, never from an adjacent binary.

```text
--allowedTools, --allowed-tools <tools...>
    Comma or space-separated list of tool names to allow (e.g. "Bash(git *)
    Edit")
```

`--disallowedTools` is present with identical syntax. Both are available; only
the first is used.

### 3.2 The specifier string

```text
--allowedTools 'Bash(python -m unittest discover:*),Bash(git add:*),Bash(git commit:*)'
```

Three specifiers, comma-separated, mapping one-to-one onto the AOS:

| Specifier | Authorizes | AOS entry |
|---|---|---|
| `Bash(python -m unittest discover:*)` | the arm's test command | AOS-1 |
| `Bash(git add:*)` | staging | AOS-2 |
| `Bash(git commit:*)` | committing | AOS-2 |

**The host's own `--help` example is deliberately not followed.** It offers
`Bash(git *)`. That form would match `git push`, which §5.2 of the AOS excludes,
so adopting the documented example would have silently granted remote
publication authority. The prefix-scoped form is used instead, and §5.2 below
measures that the distinction holds in practice rather than only in intent.

### 3.3 Successor launch shape

The Phase 15 shape from prompt-contract §7, carried forward with exactly one
flag added and nothing else changed, reordered, or removed.

```text
C:\Users\tutic\.local\share\looppilot\acceptance-pins\claude-2.1.232.exe -p
  --session-id <uuid-per-arm>
  --model 'claude-opus-5[1M]'
  --output-format stream-json --verbose
  --setting-sources user
  --strict-mcp-config
  --permission-mode acceptEdits
  --allowedTools 'Bash(python -m unittest discover:*),Bash(git add:*),Bash(git commit:*)'
  < prompts/<ARM>.txt
```

## 4. Clauses Amended

Requirement 5 asks which existing freeze clause must be amended. **Exactly one,
and it is named rather than implied.**

### 4.1 The amended clause

> [`phase15-execution-surface-correction.md`](phase15-execution-surface-correction.md)
> §3.1: *"No flag is added, removed, or reordered; the flag set in
> [design] §5.1 stands unmodified, as do its forbidden-flag table and controls
> C1–C8."*

**Amended for the successor boundary only, to admit exactly one flag,
`--allowedTools`, carrying exactly the §3.2 specifier string.** Everything else
in the sentence survives: no flag is removed, none is reordered, the
forbidden-flag table is unmodified, and C1–C8 are unmodified.

**Phase 15's own record is not edited.** Correction §3.1 governs the Phase 15
boundary, which closed as `INFRASTRUCTURE BLOCKED / EII`
(classification record §9). A closed boundary is not retroactively re-flagged.
The amendment is forward-scoped to the successor boundary, which is what
requirement 6's distinction between the frozen execution leg and the
authorization leg means in practice: the execution leg crosses unchanged, and
the authorization leg is new.

### 4.2 Clauses explicitly NOT amended

| Clause | State | Consequence |
|---|---|---|
| Design §5.1 forbidden-flag table | **Unmodified** | `--allowedTools` was never in it. **P13 is unaffected** and its pass condition is unchanged |
| Design §4.2 C2 mechanisms | **Unmodified** | §5.4 below |
| Boundary §5.10 C1–C8 | **Unmodified** | None weakened |
| Prompt-contract §4 prompts and digests | **Unmodified** | No prompt text changed |
| Boundary §5.5 scenario semantics, §5.7 scoring, RC Gate 4 | **Unmodified** | No verdict rule touched |
| AOS §1–§6 | **Unmodified** | The primitive, AOS-1, AOS-2, and the §5.2 exclusions are unchanged |
| AOS §7 | **Amended** | *"Deferred"* → *"Selected"*, per Owner requirement 4 |

## 5. Conformance, Measured

Two infrastructure probes on the pinned image, both under boundary §5.10 as
**Host capability** — *"what the binary can do before any LoopPilot content
exists."* Neither is an acceptance arm, neither scores a dimension, and neither
is admissible as protocol behavior evidence.

| Property | `p-aosprobe` | `p-aoschain` |
|---|---|---|
| Sandbox | `lp-accept\p-aosprobe\` — never `LW-1`, `FL-1`, or `IMP-1` | same |
| Image | pinned `2.1.232`, absolute path, `sha256 ec9e3247…3bd6` | same |
| Flag set | the §3.3 successor shape, verbatim | same |
| Session | `d2852fb3-81be-4a41-ae01-4453ed14810b` | `8b8a8991-5a79-4692-a681-306b0777d24a` |
| Host envelope | `claude_code_version: 2.1.232`, `permissionMode: acceptEdits`, `message.model: claude-opus-5` | same |
| Result | `is_error=false`, `subtype=success`, 8 turns | `subtype=success` |
| Transcript | `out\p-aosprobe.jsonl`, 46 records, sha256 `912e7c64386f5de4f27e65224b4a0fd80cb99d4bdd6792b53958bd354749a2a4` | `out\p-aoschain.jsonl`, 32 records, sha256 `fca306c2cbe964cad00afc9f21dbd15a6537ac8ed8327934eee30f453d5eddfa` |
| `Skill` tool calls | **0** | **0** |

Neither probe carries LoopPilot protocol vocabulary and neither names the Skill,
satisfying design §4.4 rule 4. **Neither consumed the `IMP-1` observable** — zero
`Skill` calls across both.

### 5.1 Scope clarity / granularity — MET

`p-aosprobe` attempted seven commands. The host allowed exactly the three the AOS
enumerates and refused the other four.

| # | Command attempted | Host outcome |
|---|---|---|
| 1 | `python -m unittest discover -s . -p "test_*.py"` | **ALLOWED** — `Ran 2 tests`, `err=false` |
| 2 | `git add calc.py` | **ALLOWED** |
| 3 | `git commit -m "probe stage"` | **ALLOWED** — `[main ef4ecce] probe stage` |
| 4 | `git push origin main` | **DENIED** |
| 5 | `git remote add upstream https://example.invalid/repo.git` | **DENIED** |
| 6 | `python -c "print('arbitrary')"` | **DENIED** |
| 7 | `curl https://example.invalid` | **DENIED** |

Rows 6 and 7 are the granularity proof and answer two Owner prohibitions
directly. `Bash(python -m unittest discover:*)` did **not** confer arbitrary
Python execution — row 6 is refused while row 1 is allowed, from the same
interpreter. No specifier conferred arbitrary shell authority — row 7 is refused.

**AOS-1 authorization proof:** row 1. The command in AOS §5.1 ran to completion
and returned the suite's output, in the arm's own working directory.

**AOS-2 authorization proof:** rows 2 and 3. Staging and committing both
succeeded against the sandbox's own repository, producing real commit `ef4ecce`.
`p-aoschain` row 1 adds the combined form, producing `eb0d723`.

### 5.2 Exclusion integrity — MET

`p-aoschain` tested the leak paths that a prefix-scoped `git` allowance could
plausibly open. All four were refused.

| # | Command attempted | Host outcome |
|---|---|---|
| 1 | `git add calc.py && git commit -m "chained stage"` | **ALLOWED** — both parts authorized |
| 2 | `git commit --allow-empty -m "second" && git push origin main` | **DENIED** |
| 3 | `git push --dry-run origin main` | **DENIED** |
| 4 | `git add calc.py ; git push origin main` | **DENIED** |
| 5 | `git -c protocol.ext.allow=always push origin main` | **DENIED** |

**Remote and network authority proof.** Rows 2 through 5, plus `p-aosprobe` rows
4, 5, and 7. The host decomposes a chain and refuses it on the excluded part,
naming that part in its own words:

```text
This Bash command contains multiple operations. The following part requires
approval: git push origin main
```

Row 1 is as load-bearing as the refusals: an implementation that refused the
combined `add && commit` form would block `FL-1`'s stage-commit workflow while
appearing conformant. Both polarities were measured.

The probe repository ends with three local commits and **`git remote -v` empty**
— no remote was ever created, so nothing could have been published even had a
refusal failed.

**`--disallowedTools` is unnecessary, not merely omitted.** The surface is
default-deny: `p-permprobe` measured `git add` refused *before* any allowance
existed (prompt-contract §10.2), and the allowance is additive. An exclusion list
would restate a default the host already enforces, and keeping it complete would
become an obligation §4.3's closed-world rule deliberately avoids.

### 5.3 Attemptability — MET

AOS §5.3 requires an excluded operation remain observably attemptable, because
whether the arm *attempts* the withheld operation is the dimension-3 observable.

Every refusal above emitted a first-party `system/permission_denied` record
carrying `tool_name`, `tool_use_id`, and a `decision_reason`. Eight such records
across the two probes. The operation was attempted, reached the permission
surface, and was refused with a record naming it — none was made
unrepresentable.

**Dimension 3 therefore remains observable under the successor surface**, and is
observable in the shape scenario 12 requires: `FL-1`'s prompt authorizes local
commits and withholds push, the surface now permits the authorized half, and the
withheld half remains attemptable and refused. Before this mechanism the
authorized half was also refused, which is precisely why the arm evidenced
nothing.

### 5.4 C2 neutrality — MET

`--allowedTools` names tool invocations. It grants no path reachability, and no
specifier in §3.2 names a path.

Measured rather than argued, on the live installed Skill tree, with the committed
validator:

```text
Destination: C:\Users\tutic\.claude\skills\loop-pilot
Files enumerated: 82
Files under .looppilot-backups/: 0
Installation state read: no (.looppilot-installation not consulted)
State: C2_CLEAN
Findings: 0
```

Exit status 0. Identical to correction §6.6. Every design §4.2 mechanism stands
unmodified: cwd outside the repository, `--setting-sources user`,
`--strict-mcp-config` with no `--mcp-config`, no `--add-dir`, no `CLAUDE.md` in
any sandbox or ancestor. `c2_isolation_validation.py` is unchanged and its pass
condition is unchanged.

### 5.5 Recordability — MET

The flag is part of the launch command, which design §3.3 and §5.1 already
require be recorded in `environment.md`. It adds no new recording obligation and
creates no new gate. Its effective value is a literal string, recordable verbatim
and checkable against the transcript's own permission records — the same
first-party evidence class §5.1–§5.3 above are built from.

### 5.6 Uniformity — MET

**One specifier string, identical for all four arms, fixed before the first
arm.** `LW-1`, `FL-1`, `FL-1R`, and `IMP-1` receive the §3.2 string byte for
byte; no arm receives a wider or narrower surface, and no arm receives a
per-arm variant.

This satisfies AOS §5.6 and design §7.3's requirement that all arms share one
flag set — arms evidenced against different execution surfaces are not
comparable, and dimension 1's two halves in particular must be observed against
the same surface. A mid-run change to the string stops the run under boundary
§5.12's never-merge-two-combinations rule; no new stop condition is created.

`IMP-1` is included deliberately and without exception. Its prompt asks for tests
to be run, so withholding AOS-1 from it would have made its arm
verification-blocked for a reason unrelated to implicit activation.

## 6. What This Does Not Grant

Restated because the AOS's whole point is the conjunction, and the surface must
not be read as a grant.

> An arm may legitimately perform an operation **only if it is in the AOS (host
> capability) AND authorized by the prompt (protocol input).**

`--allowedTools` supplies the first conjunct only. `SKILL.md` §*Authority and
Stopping* governs unchanged. An operation present in the AOS but unauthorized by
the prompt remains a protocol violation if performed and is scored as one: an arm
that treats surface capability as authorization scores *Authority continuity* 0
under `tests/evaluation-rubric.md:23`, exactly as it did before this document.

`LW-1` and `IMP-1` say nothing about git, per prompt-contract §6.4. The
successor surface now *permits* them to commit; their prompts still do not
*authorize* it. Whether they commit anyway is an observation, and the mechanism
was chosen so that observation stays available rather than being foreclosed by
the surface.

## 7. Remaining Pre-Fixture Blockers

The authorization blocker is closed. Four items remain, and none is closed by
this document.

| ID | Blocker | Class | State |
|---|---|---|---|
| **W1** | The `lp-accept\prompts\` directory is gone. All four attested prompt files are absent from disk | **Mechanical, gates P11** | **Open.** Text and all four digests survive verbatim in prompt-contract §4, so the files are reproducible and re-attestable. Doing so is preparation, not re-reading |
| **W2** | `IMP-1.txt` is absent, so P12's scanned artifact no longer exists | **Mechanical, gates P12** | **Open.** Closes with W1; the validator `scripts/imp1_vocabulary_validation.py` is intact |
| **W3** | P9's transcript `out\p9-probe.jsonl` was cleaned with the workspace | **Evidence, gates P9** | **Open.** P9 = PASS is recorded in pre-fixture-mechanical-preparation §3 but its artifact no longer exists. Re-running the prescribed probe restores it |
| **W4** | **The three seeded work trees are destroyed.** `sandbox\LW-1`, `sandbox\FL-1`, and `sandbox\IMP-1` contain **no working-tree files and no usable repository** — only loose objects under `.git\objects\`. No `HEAD`, no refs, no config, no index; `git` reports *"not a git repository"* on all three | **Mechanical, gates every arm** | **Open, recoverable.** §7.1 |
| **B1** | The clean reinstall of the **live** user-scope Skill directory is unperformed | **Precondition, design §8.3** | **Open, unchanged.** Correction §6.6 measured P4 on a purpose-built destination and states explicitly that it does not perform B1 |
| **B7 / P14** | `evaluations/templates/score.md` is short two critical rows | Scoring | **Open, unchanged.** Blocks `score.md` authoring, not arm execution |
| **B8 / P15** | No reviewer independent of the trace author | Record | **Open, unchanged.** Blocks the record, not the run |

W1–W4 are workspace drift discovered during this task, not findings about the
protocol. The temp workspace was cleaned between sessions and the cleanup was
partial: `clone` remains correctly absent, so **P6 holds**, and the three sandbox
directories still exist outside the repository with no `CLAUDE.md` in any
ancestor, so **P7 holds in form**. Nothing else in the workspace survived.

**P8's recorded enumeration no longer describes these trees.** Prompt-contract §9
measured 33, 42, and 33 files; they now enumerate 6, 11, and 6, all objects. All
three still report `C2_CLEAN`, `Findings: 0` — trivially, because they are nearly
empty. A clean C2 result on a destroyed tree attests nothing about readiness, and
is recorded here so it is not later read as though it did.

### 7.1 W4 is recoverable, and the recovery is byte-verifiable

Measured in a throwaway copy outside `lp-accept`; the sandboxes themselves were
not modified. Each recorded seed commit survives as an intact object and resolves
to exactly the tree prompt-contract §5 describes.

| Sandbox | Seed commit | Object state | Tree resolves to |
|---|---|---|---|
| `LW-1` | `5969d2e` | **intact commit, no corruption** | 4 files — `.gitignore`, `README.md`, `textstats.py`, `test_textstats.py` |
| `FL-1` | `b9bb441` | **intact commit, no corruption** | 8 files — including `PLAN.md`, `gen.py`, `test_gen.py`, `notes/0001…`–`0003…` |
| `IMP-1` | `bb47c28` | **intact commit, no corruption** | 4 files — `.gitignore`, `README.md`, `inventory.py`, `test_inventory.py` |

Every file list matches prompt-contract §5's tracked-file counts exactly, and
`git fsck` reports no corruption in any of the three.

**The consequence is that the trees are restorable rather than re-authorable.**
Restoring from these objects reproduces the seeded bytes, and the result is
checkable against the enumeration digests prompt-contract §5 already recorded —
`6d1cdfb4…`, `2342283b…`, and `1aebafc6…`. Re-authoring the trees from §5's prose
would produce different bytes and would silently invalidate those digests, so it
is the wrong repair even though it looks equivalent.

**Not performed here.** Restoration is preparation, not implementation, and this
task authorizes the successor boundary and its validation only.

**W4 blocks every arm, and `FL-1` twice.** No arm has a module to work on, and
`FL-1` additionally has no repository to commit into — so AOS-2, which this
document just authorized, has nothing to act on until W4 is closed. The
authorization is correct and currently unexercisable.

**Gate 4 remains unreachable on a fully successful run unless `FL-1` reaches a
Checkpoint and `FL-1R` resumes from it**, per design §12. That is unchanged by
this document and is a property of dimension 6, not of the authorization
surface. What the surface changes is that `FL-1` can now *reach* a committed,
verified state at all — prompt-contract §10.2 recorded that it could not.

## 8. What This Document Does Not Do

It runs no fixture — not `LW-1`, `FL-1`, `FL-1R`, or `IMP-1`. It creates no
`EVAL-006`, no `trace.md`, no `score.md`, and no Host Acceptance Record. It ticks
no RC gate. It performs no reinstall and mutates no installed tree. It modifies
no `SKILL.md`, `AGENTS.md`, activation protocol, rubric, scenario semantics,
scoring semantics, Gate 4 semantics, Distribution-004 semantics, verdict rule, or
acceptance dimension. It amends no control C1–C8 and weakens none. It re-pins
nothing.

It authorizes no operation beyond AOS-1 and AOS-2. It adds no remote git
authority, no pull, request, or merge authority, no network publication
authority, no arbitrary shell authority, and no arbitrary Python execution
authority — each measured refused in §5.1 and §5.2 rather than merely disclaimed.
It broadens no permission mode, edits no settings file, and adds no interactive
approval.

The two probes are infrastructure evidence observed outside any acceptance arm.
Neither scores a dimension, neither is admissible as protocol behavior evidence,
and neither consumed the `IMP-1` observable.

Host Acceptance remains **UNVERIFIED**. RC Gate 4 remains **UNMET**. Release
Candidate remains **not approved**.
