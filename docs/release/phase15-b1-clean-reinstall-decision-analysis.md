# Phase 15 / B1 — Clean-Reinstall Semantics Decision Analysis

A determination of whether the existing Phase 15 text already fixes the meaning
of "clean reinstall" in
[`phase15-acceptance-boundary.md`](phase15-acceptance-boundary.md) §5.3, and — if
it does not — a statement of the specification gap and the minimal owner decision
that closes it.

**Status: §7 Option 1 implemented.** §1–§10 are the analysis as written before
implementation and are preserved unedited; §11 is the as-built record and
supersedes §10 where the two disagree. The implementation amended §4.4, §8, §11,
§12, §13, and §14 of the execution-surface design and added one script and one
test module. It modifies no `SKILL.md`, `AGENTS.md`, activation protocol,
rubric, fixture semantics, or Distribution-004 installation, update, or backup
semantics, and it does not amend C2 itself. No fixture was executed — not
`LW-1`, `FL-1`, `FL-1R`, or `IMP-1` — no `EVAL-006` exists, and no score or Host
Acceptance Record was written. Host Acceptance remains **UNVERIFIED**, RC Gate 4
remains **UNMET**.

Every measurement in §1–§10 is quoted from an existing preserved record. The
measurements in §11 were taken during implementation; they are distribution
mechanics observed outside any acceptance arm, and none of them is Host
Acceptance evidence.

- Boundary: HEAD `9006a241fc79ca68082dcc5d17407b55c95b9433`, branch `main`.
- Blocker addressed: **B1**, recorded in
  [`phase15-execution-surface-design.md`](phase15-execution-surface-design.md) §1
  and §8, carrying a C2 precondition added by
  [`phase15-b9-packaging-boundary-design.md`](phase15-b9-packaging-boundary-design.md)
  §9.7.
- Frozen inputs: **B9 CLOSED**; **B12 not a C2 failure**; **B13 upgrade-path
  contamination, not a Gate 4 blocker**, per
  [`phase15-b12-b13-decision-analysis.md`](phase15-b12-b13-decision-analysis.md).

## 1. The Question, Stated Exactly

Does the existing text already **require**, uniquely, that a §5.3 clean reinstall:

| | Property |
|---|---|
| **(a)** | the entire destination is deleted first |
| **(b)** | installation is from a pinned clean checkout |
| **(c)** | the resulting installation directory contains no `.looppilot-backups/` |

"Uniquely" is the operative word. A reading that the text *permits* is not a
requirement the text *imposes*. B1 is a precondition gate under §5.12 row 3, and
a gate whose pass condition admits materially different outcomes is not a gate.

## 2. What the Governing Text Actually Says

Three layers of text could answer the question. All three were read in full.

### 2.1 `docs/cross-host-acceptance.md` — silent

The governing procedure contains exactly one installation-related statement:

> Acceptance is scoped to one host, host version, model, and Skill loading mode

It names *Skill loading mode* as a scope field. It defines no installation
procedure, no reinstall, and no directory-content requirement. It contributes
nothing to (a), (b), or (c).

### 2.2 `phase15-acceptance-boundary.md` §5.3 — the operative text

§5.3 in full is three elements: a command, a check, and a rationale.

| Element | Text |
|---|---|
| **Command** | "Install from a checkout at the pinned commit using the documented entry point in `docs/installation.md`: `.\install.ps1 -Destination "$HOME\.claude\skills\loop-pilot"`" |
| **Check** | "Then verify with `status.ps1` and require it to report `CURRENT` before the first arm." |
| **Rationale** | "…it carries **no `.looppilot-installation` state file** … Its provenance is therefore not machine-checkable. **A clean reinstall from the pinned commit is required so the installation is traceable.**" |

Three properties of that text decide the classification.

**The phrase "clean reinstall" occurs once and is never defined.** It is not
elaborated, not cross-referenced, and not given a pass condition of its own.

**The stated purpose is traceability, not decontamination.** The defect §5.3
names is a missing state file. The remedy's stated goal is that "the installation
is traceable". A purposive reading therefore selects any procedure ending in a
valid `.looppilot-installation` recording the pinned commit — which paths B, D,
and E all satisfy (§3.2). The rationale does not reach tree contents at all.

**The string `backups` occurs zero times in the entire boundary document.**
Verified by enumeration over `phase15-acceptance-boundary.md`. Property (c) has
no textual basis anywhere in the boundary.

### 2.3 `docs/installation.md` — incorporated by reference, and it points the other way

§5.3 does not merely cite `docs/installation.md`; it instructs the operator to use
"**the documented entry point in** `docs/installation.md`". That document is
therefore part of the operative text, and it works against reading (a), not for it.

| Line | Text | Effect on the reading |
|---|---|---|
| 13 | "`install.ps1`, `install.sh` \| Fresh installation and **explicit reinstall** entry points" | "Reinstall" is a term of art meaning *running `install.ps1`*, not *deleting a directory* |
| 141 | "An identical existing installation is reported as `reinstall (no changes)`." | The only elaboration of "reinstall" describes an **in-place, destination-preserved** operation — the opposite of (a) |
| 59 | `.looppilot-backups/` appears in the **Installed Layout**, "generated only when a backup is needed" | A backups directory is a documented, legitimate component of an installation |
| 95–97 | "`.looppilot-backups/<operation-id>/` contains files backed up before replacement … **Backups are retained until the user reviews and removes them.**" | Retention is by design; nothing treats its presence as a defect |
| 316–320 | Uninstall "removes only recorded files … Modified files, user-created files, **backup files**, and directories are preserved." | No documented entry point can empty a destination |

The last row is decisive on its own. **LoopPilot documents no operation that
produces an empty destination.** `uninstall.ps1` explicitly preserves backup files
and directories. Property (a) therefore requires a raw filesystem deletion that
lies outside the entire documented distribution interface — while §5.3 instructs
the operator to use a *documented entry point*. The text cannot be read as
mandating an operation its own referenced document does not offer.

### 2.4 The operationalizing document presents both readings as interchangeable

This is the sharpest evidence, and it is not interpretive.
`phase15-execution-surface-design.md` §8.2 is the procedure written to satisfy
§5.3. Its step 3 reads:

```text
3.  uninstall.ps1 the existing ~/.claude/skills/loop-pilot   (or move it aside)
```

That is a disjunction between two procedures with different C2 outcomes:

- `uninstall.ps1` is **path D**, measured as leaving 80 acceptance files at
  readable paths.
- "move it aside" is equivalent to **path E**, measured as clean.

The document that exists to operationalize §5.3 offers a contaminating and a
non-contaminating procedure as equivalent alternatives, in a parenthetical, with
no criterion for choosing. A specification whose own operationalization is
indifferent between the two has not determined the semantics.

## 3. Property-by-Property Determination

### 3.1 Result

| Property | Determined by existing text? | Basis |
|---|---|---|
| **(a)** delete entire destination first | **No** | §5.3 names no removal step; "reinstall" is defined in-place at `installation.md:141`; no documented entry point can empty a destination; §8.2 offers path D and path E as alternatives |
| **(b)** install from pinned clean checkout | **Yes** | §5.3 "Install from a checkout at the pinned commit"; operationalized by §8.2 steps 1–2 as a detached worktree at `9006a241…` with `git status --porcelain` empty, and gated by P3 |
| **(c)** no `.looppilot-backups/` in the installation | **No** | Zero occurrences of `backups` in the boundary; `installation.md` documents the directory as legitimate installed layout and its retention as intended |

**One of three properties is determined.** (b) holds. (a) and (c) do not.

### 3.2 The fork is reached by construction, and the text is silent at it

§5.3's literal command is **not executable** against the starting condition §5.3
itself records. Per the measured path table in
[`phase15-b12-b13-decision-analysis.md`](phase15-b12-b13-decision-analysis.md)
§2.2, reproduced here without re-measurement:

| Path | Operation | Acceptance files at normal paths | Files under `.looppilot-backups/` | `status.ps1` |
|---|---|---:|---:|---|
| **A** | `install.ps1`, no `-Force`, over existing tree | — | — | **refuses**, atomic, nothing copied |
| **B** | `install.ps1 -Force` over existing tree | **80** | 3 | **CURRENT** |
| **C** | `update.ps1` from a pre-B9 installation | 0 | **83** | **CURRENT** |
| **D** | `uninstall.ps1` then `install.ps1 -Force` | **80** | 3 | **CURRENT** |
| **E** | remove the destination, then `install.ps1` | **0** | **0** | **CURRENT** |

Path A is the literal §5.3 command. It **refuses**. The observed precondition
§5.3 records — a payload present, no state file — guarantees the refusal is hit,
so the operator is forced off the literal text every time. §5.3 supplies no rule
for which departure to take, and paths B, D, and E all satisfy its stated check.

**Three admissible procedures, one prescribed check, and outcomes differing by 80
readable acceptance files.** That is the gap.

## 4. `CURRENT` ≠ C2-clean

This is proved twice: once from the definition, once from measurement. Neither
proof requires running anything.

### 4.1 From the definition of `CURRENT`

`docs/installation.md:195` defines the state:

> `CURRENT` — Every **managed** file matches the source, and the recorded
> revision and manifest match it too.

The quantifier ranges over the **managed set**. `docs/installation.md:99–105`
completes the picture: "Files not recorded in `.looppilot-installation` are
user-owned. The scripts do not delete or replace them." Unmanaged content is
outside what `status` computes, by design.

B9 reclassified **80 files from managed to unmanaged** (`phase15-b9…` §9.2:
161 → 81). Every acceptance file is now unmanaged. Therefore:

```text
CURRENT   ranges over:  { managed files } matches source
C2-clean  ranges over:  { every file in the tree } ∉ prohibited corpus
```

The two predicates quantify over **disjoint domains** after B9. `CURRENT` says
nothing about any file it no longer manages, and every file C2 cares about is now
such a file. No implication can exist in either direction.

### 4.2 From measurement

The recorded observation, `phase15-b12-b13-decision-analysis.md` §2.3:

> It reported `CURRENT`, `Files current: 81`, `Files to remove: 0` on a tree
> containing `tests/evaluation-rubric.md`, `tests/scenarios.md`,
> `docs/cross-host-acceptance.md`, and all five prior evaluation packages at
> their ordinary readable paths.

From the §3.2 table: `CURRENT` is observed on **B, C, D, and E**. Of those, only
**E** is C2-clean. So `CURRENT` is true in both C2-clean and C2-contaminated
states, which refutes `CURRENT → C2-clean` by counterexample.

### 4.3 The two predicates are logically independent

The converse also fails. A directory can be C2-clean and not `CURRENT` — one
edited managed file yields `LOCAL_MODIFICATIONS` on a tree holding no acceptance
material at all.

**`CURRENT` and C2-clean are logically independent.** Neither implies the other.
Both are required. Neither substitutes for the other, and the acceptance
procedure currently checks only the first.

### 4.4 What this means for the pre-flight gate

`phase15-execution-surface-design.md` §11 gates B1 at **P4**:

> `status.ps1` = `CURRENT`, `.looppilot-installation` present and naming the
> pinned commit

Neither conjunct is a tree-content assertion. Both are satisfied by paths B and
D. **P4 as written cannot detect the property B1 now exists to guarantee.**

This is not a Distribution-004 defect. Managed-set scoping is correct behavior and
is the reason user content survives upgrades. It is a statement about what
`CURRENT` can attest, and it must not be answered by changing what `status` does.

## 5. C2-clean, Stated Separately as a Checkable Predicate

C2 and its operationalization already exist; this section only assembles them
into the predicate the missing check would evaluate. It introduces no new
requirement.

C2 (`phase15-acceptance-boundary.md` §5.10):

> **C2.** No evaluation record, rubric, checklist, acceptance document, or
> project memory index is reachable from the fixture working directory.

Operationalized by `phase15-execution-surface-design.md` §4.1 as an explicit
prohibited list, and extended by `phase15-b9…` §3.2, which classified
`scripts/*.py` and `tests/test_*.py` as acceptance material because they encode
the acceptance rules as executable specification.

**C2-clean(D)** holds for a directory `D` if and only if, enumerating **every**
regular file under `D` at any depth, including hidden directories:

| # | Criterion |
|---|---|
| 1 | No path under `evaluations/` |
| 2 | Not `tests/evaluation-rubric.md`, not `tests/scenarios.md`, no `tests/test_*.py` |
| 3 | No path under `scripts/` |
| 4 | No path under `docs/release/` |
| 5 | No path under `docs/evaluations/` |
| 6 | Not `docs/cross-host-acceptance.md` |
| 7 | No prior Host Acceptance Record at any path |
| 8 | No project memory index |
| 9 | Criteria 1–8 hold for paths **nested under `.looppilot-backups/`** as well as at their ordinary locations |
| 10 | The enumeration covers the **entire tree**, not the managed projection |

Criteria 9 and 10 are the two that a naive implementation drops, and dropping
either silently reproduces the exposure the check exists to catch.

**Criterion 9 requires suffix matching, not exact relative-path matching.** A
backed-up file lives at `.looppilot-backups/<operation-id>/<original-path>` — so
the rubric appears as `.looppilot-backups/<id>/tests/evaluation-rubric.md`, which
does **not** equal `tests/evaluation-rubric.md`. A check comparing
destination-relative paths for equality would enumerate all 83 backed-up
acceptance files and report zero hits. That is the difference between a check that
works and one that looks like it works.

Two scopes must both satisfy the predicate, and only one is currently checked
anywhere:

| Scope | Currently verified? |
|---|---|
| Fixture working directory (sandbox) | **Yes** — §4.4 static check and the `P-probe` negative reachability probe |
| Installed user-scope Skill directory | **No** — §4.4's static check enumerates "the sandbox tree and every path reachable from it **without traversing above it**", which excludes the Skill directory |

The Skill directory is reachable from every fixture context by construction —
`phase15-execution-surface-design.md` §4.3 establishes this, because it is how
`SKILL.md` resolves its relative references. So the unchecked scope is not a
hypothetical exposure; it is the one C2 was written about.

## 6. The Specification Gap

Stated minimally, so it can be decided rather than debated:

> **§5.3 requires a "clean reinstall" without defining it. Three procedures
> satisfy every check the acceptance procedure prescribes — `install.ps1 -Force`
> (B), `uninstall.ps1` then install (D), and destination removal then install
> (E) — and they differ by 80 readable acceptance files inside the Skill
> directory that every fixture context can reach. The prescribed verification,
> `status.ps1` = `CURRENT` plus P4's state-file conjunct, is provably incapable
> of distinguishing them, because after B9 every acceptance file is unmanaged and
> `CURRENT` quantifies only over managed files.**

Two corollaries follow, and neither is resolvable by reading the text harder:

1. **B1 cannot be closed by executing §5.3 as written.** An operator who complies
   fully may land on B or D and pass P4 with a contaminated Skill directory.
2. **B1 and B13 close together or not at all.** `phase15-b12-b13…` §2.6 already
   established this. This document adds *why*: the shared cause is that the
   procedure is unspecified and the property is unchecked, not that the backups
   directory is hazardous.

## 7. Minimal Owner Decision

One decision is required. It is an amendment to acceptance-execution text, which
`phase15-execution-surface-design.md` §4.3 forbids this class of document from
performing, so it is offered and not taken.

### D-B1 — How is a §5.3 clean reinstall made verifiable?

| | Option 1 — verify the property **(recommended)** | Option 2 — fix the procedure |
|---|---|---|
| **Change** | Extend §4.4's static check to enumerate the installed Skill directory in full and assert C2-clean per §5; add it as a pass condition on P4 | State in §5.3 that the destination must not exist immediately before `install.ps1` runs |
| **Constrains** | The result | The procedure |
| **Verifies** | The property C2 names | Nothing — no check is added |
| **Touches distribution behavior** | No | No |
| **New principle?** | No — §4.4 already applies exactly this reasoning to the sandbox; this extends it to a directory it did not cover | No |
| **Residual** | None for this gap | An installation contaminated by any other route still passes P4 unchanged |

**Option 1 is recommended, and it is also the smaller change.** It adds one
assertion and constrains no procedure. Under it the words "clean reinstall" stop
carrying load: paths B, D, and E are admitted or rejected on their measured
result rather than on their name, and as measured only E passes. It checks the
property that matters instead of a procedure believed to produce it — the same
reasoning §4.4 already applies to the sandbox, and the same reasoning
`phase15-b12-b13…` §2.6 gave when it called this remedy the stronger of the two.

Option 2 is additionally awkward on its own terms: `docs/installation.md`
provides no entry point that empties a destination, so §5.3 would prescribe an
operation outside the documented interface it directs the operator to use.

The options are compatible. If both are taken, Option 1 is the load-bearing one
and Option 2 becomes a procedural note.

### Explicitly outside this decision

- **No Distribution-004 change.** Backup creation, retention, managed-set scoping,
  and uninstall preservation are correct and stay as they are.
- **No `distribution/managed-files.txt` change.** B9 is closed; the manifest is
  not reopened.
- **No `status` change.** `CURRENT` is correct about what it measures. The remedy
  adds a second, separate assertion; it does not redefine the first.
- **No protocol, rubric, or fixture-semantics change**, and no amendment to C2
  itself — the control's text is adequate; only its verification scope is short.

## 8. A Note on B1's Recorded Evidence

`phase15-execution-surface-design.md` §1 records B1's evidence as "4 conflicted
files, 101 to add, state format unreadable, `.looppilot-installation` absent".

Those figures are bound to the pre-B9 manifest. The arithmetic is internally
consistent across two independent documents — §5.3's 60 installed files plus
§8.1's 101 to add equals the 161-file expansion that `phase15-b9…` §9.2 records
for the old manifest — and B9 reduced that expansion to 81. The `101 to add`
figure therefore cannot survive the manifest change.

**This is inference from recorded numbers, not measurement.** Nothing was
re-measured here. The observation is recorded only so that a later reader does
not treat the stale count as current, and because it means B1's evidence needs
re-derivation against the new manifest whichever option D-B1 takes. The blocker
itself is unaffected: `RECOVERY_REQUIRED` and the absent state file are
manifest-independent.

## 9. Consolidated Answers

| Question | Answer |
|---|---|
| Does §5.3 require deleting the entire destination first? | **No.** No removal step is named; `installation.md:141` defines "reinstall" in place; no documented entry point can empty a destination; §8.2 offers path D and path E as alternatives |
| Does §5.3 require installing from a pinned clean checkout? | **Yes.** The one property of the three that is determined, gated by P3 |
| Does §5.3 require the absence of `.looppilot-backups/`? | **No.** Zero occurrences of `backups` in the boundary; `installation.md` documents the directory as legitimate and its retention as intended |
| Is the text sufficient to uniquely determine the semantics? | **No.** Three procedures satisfy every prescribed check and differ by 80 readable acceptance files |
| Does `CURRENT` imply C2-clean? | **No**, proved from the definition (disjoint quantification domains after B9) and by counterexample (B, C, D observed `CURRENT` while contaminated). The predicates are logically independent |
| Is the Skill directory currently checked for C2? | **No.** §4.4's static check is scoped to the sandbox and explicitly does not traverse above it |
| **B1 status** | **SPECIFICATION GAP.** Not closed, and not closable by executing §5.3 as written |

## 10. What This Document Does Not Do

It performs no installation, no uninstall, no update, and no status query. It runs
no fixture — not `LW-1`, `FL-1`, `FL-1R`, or `IMP-1`. It creates no `EVAL-006`,
no score, and no Host Acceptance Record. It ticks no RC gate.

It modifies no `SKILL.md`, `AGENTS.md`, activation protocol, rubric, fixture
semantics, acceptance semantics, or Distribution-004 backup semantics, and it
amends neither C2, §5.3, §4.4, nor P4. It takes no owner decision; §7 offers one.

It reopens none of the frozen conclusions: B9 stays **CLOSED**, B12 stays **not a
C2 failure**, B13 stays **upgrade-path contamination and not a Gate 4 blocker**.
B7, B8, and B10 are untouched.

No measurement in this document is new, and none of it is Host Acceptance
evidence. Every figure is quoted from a preserved record and is distribution
mechanics observed outside any acceptance arm.

Host Acceptance remains **UNVERIFIED**. RC Gate 4 remains **UNMET**. Release
Candidate remains **not approved**.

## 11. Implementation Record

Option 1 of §7 was authorized and built. What follows is what exists, measured
rather than restated from §7.

### 11.1 What was built

| File | Change |
|---|---|
| `scripts/c2_isolation_validation.py` | New. Enumerates an installed Skill directory and reports `C2_CLEAN` / `C2_CONTAMINATED` with one `rule\|path` finding per violation. Exit 0 clean, 1 contaminated, 2 unusable destination |
| `tests/test_c2_isolation.py` | New. 15 tests over the rule set, the packaging boundary, and the command-line entry point |
| `phase15-execution-surface-design.md` §4.4 | Static check split into scope A (sandbox, unchanged) and scope B (installed Skill directory, new); the `CURRENT` ≠ C2-clean statement and its measurements added |
| …§8.2, §8.4 | Clean-install procedure gains step 6; step 3 deliberately left unprescribed; §8.4's claim that `CURRENT` closes B1 corrected |
| …§11 P4, P8 | P4 gains the `C2_CLEAN` conjunct; P8 records that the Skill directory is P4's scope |
| …§12, §13, §14 | P10 recorded resolved; a stop condition added for a contaminated Skill directory; closure status updated |

No distribution script, manifest, protocol document, rubric, test assertion, or
acceptance verdict changed. The corpus definition is duplicated from
`tests/test_distribution.py` deliberately and a test fails if the two drift.

The check is deliberately **not** wired into `scripts/validate.py`. That
validator checks the repository, and the repository legitimately contains the
acceptance corpus; running this check there would fail by construction. It is a
pre-flight gate pointed at an installation, in the same shape as `status`.
`scripts/validate.py` passes and the full suite is green at 898 passed with 20
subtests passed.

### 11.2 The ten predicates, as machine checks

| # | Predicate | Mechanism | Rule emitted |
|---|---|---|---|
| 1 | No path under `evaluations/` | suffix match | `acceptance-corpus:evaluations/` |
| 2 | No `tests/evaluation-rubric.md`, `tests/scenarios.md`, `tests/test_*.py` | suffix match on `tests/`, which is broader and covers all three | `acceptance-corpus:tests/` |
| 3 | No path under `scripts/` | suffix match | `acceptance-corpus:scripts/` |
| 4 | No path under `docs/release/` | suffix match | `acceptance-corpus:docs/release/` |
| 5 | No path under `docs/evaluations/` | suffix match | `acceptance-corpus:docs/evaluations/` |
| 6 | Not `docs/cross-host-acceptance.md` | suffix match | `acceptance-corpus:docs/cross-host-acceptance.md` |
| 7 | No prior Host Acceptance Record at any path | content: a level-1 heading beginning `# Host Acceptance Record` | `host-acceptance-record` |
| 8 | No project memory index | basename `CLAUDE.md` or `MEMORY.md` | `memory-index` |
| 9 | 1–8 hold under `.looppilot-backups/` too | suffixes generated to unbounded depth | — |
| 10 | Enumeration covers the whole tree | `os.walk`, hidden directories included, symlinks never traversed, `.looppilot-installation` never read | — |

**All ten are machine-checked.** Two carry limits worth stating rather than
implying:

- Predicate 8 identifies a memory index by filename, so an index under some
  other name is not caught. This is the same limit §4.4's original sandbox check
  already carried, and it is not widened here.
- Predicate 7's content check keys on the heading real records use. A record
  stripped of that heading would still be caught by predicates 1–6 if it sits
  under a corpus path, and not otherwise.

Predicate 2 is implemented as the whole `tests/` tree rather than the three
named files, matching the corpus B9 §3.2 removed and the constant
`tests/test_distribution.py` already asserts against the manifest.

### 11.3 Controls, measured

Two real installations were built from the pinned commit outside the repository,
using detached worktrees at `9006a241fc79…`: a `pre-b9` source carrying the
161-file manifest and a `post-b9` source carrying the narrowed 81-file manifest.
The live user-scope installation was not touched.

| | Positive control | Negative control |
|---|---|---|
| Produced by | destination absent, then `install.ps1` from `post-b9` | `install.ps1` from `pre-b9`, then `update.ps1` from `post-b9` |
| Files in tree | 82 (81 payload + state) | 163 |
| Files under `.looppilot-backups/` | 0 | 81 |
| Acceptance files at normal paths | 0 | 0 |
| `status.ps1` | **CURRENT** | **CURRENT** |
| Check B | **`C2_CLEAN`**, exit 0 | **`C2_CONTAMINATED`**, exit 1 |
| Findings | **0** | **79** |

**The two trees are indistinguishable to `status` and separated by check B.**
That is the property D-B1 was taken to obtain, and it is now observed rather
than argued.

Findings on the negative control, by rule:

```text
37  acceptance-corpus:evaluations/
19  acceptance-corpus:tests/
11  acceptance-corpus:scripts/
 7  acceptance-corpus:docs/release/
 4  acceptance-corpus:docs/evaluations/
 1  acceptance-corpus:docs/cross-host-acceptance.md
──
79  total, of which 79 sit under .looppilot-backups/<id>/ and 0 at a normal path
```

Three properties of that result are worth recording:

1. **The group counts reproduce B9 §9.2's removal table exactly** — 37, 19, 11,
   7, 4, 1. The check finds the corpus B9 stopped distributing, neither more nor
   less.
2. **Every finding is suffix-only.** Zero findings sit at a normal path, so a
   destination-relative equality check would have enumerated all 81 backed-up
   files and reported a clean tree. Predicate 9 is the whole difference between
   detection and a false pass.
3. **Precision is exact.** The two backed-up files *not* flagged are
   `distribution/managed-files.txt`, backed up because B9 changed it, and
   `requirements-dev.txt`, retired from the manifest but not acceptance
   material. 79 corpus + 2 non-corpus = the 81 files present.

The positive control additionally confirms no false positive from suffix
matching against a real payload, and
`test_official_payload_produces_no_finding` holds that as a standing invariant
so a later manifest addition such as `examples/tests/` cannot silently make a
correct clean install report contaminated.

**A third measurement, against the live installation rather than a control.**
Run read-only on `C:\Users\tutic\.claude\skills\loop-pilot`, the destination P4
will gate, the check reports `C2_CONTAMINATED` over 60 enumerated files with
exactly two findings:

```text
acceptance-corpus:docs/cross-host-acceptance.md|docs/cross-host-acceptance.md
acceptance-corpus:docs/release/|docs/release/v1.0-rc-checklist.md
```

Those are the same two files
[`phase15-b9-packaging-boundary-design.md`](phase15-b9-packaging-boundary-design.md)
§4.3 identified by hand, so the check reproduces an independent manual
observation on a tree neither control produced. The live installation therefore
fails P4 twice over and on independent grounds — `status.ps1` reports
`RECOVERY_REQUIRED` rather than `CURRENT`, and the tree is not C2-clean — which
is the correct outcome and the reason §8's clean reinstall is a pre-run step.
Nothing about that installation was modified.

### 11.4 What the implementation closes, and what it does not

**B1 is closed.** The clean reinstall is no longer an undefined procedure
verified by an insufficient check. It is a checked property: P4 fails unless the
installed tree enumerates clean, whatever produced it. The three procedures §5.3
admitted are now adjudicated on their measured result — as measured, only
destination removal passes — and §5.3's own wording did not have to be amended
to get there.

**B13 is closed as a consequence**, in the only scope that ever mattered for
Gate 4. An upgraded installation still retains the corpus under
`.looppilot-backups/`, which remains correct Distribution-004 behavior and a
real operational hazard for an operator who upgrades; it can no longer reach an
acceptance run, because P4 now rejects it.

**Not closed, and untouched:** B7, B8, B10. **Not created:** any `EVAL-006`,
trace, score, or Host Acceptance Record. **Not changed:** any acceptance
verdict, dimension result, or RC gate.

### 11.5 No new ambiguity was introduced

The authorization required stopping if the change produced fresh specification
ambiguity. It did not, and the reason is structural: the amendment adds an
assertion and removes none, constrains no procedure, and defines its pass
condition as a program's exit status rather than as prose. The one place where a
reader could previously choose between readings — §8.2 step 3 — is now
explicitly unprescribed, with the choice resolved by step 6's measured result
instead of by the step's wording.

Host Acceptance remains **UNVERIFIED**. RC Gate 4 remains **UNMET**.
