# Phase 15 / B9 — Packaging Boundary Design

A design and impact analysis for separating the acceptance corpus from the
LoopPilot Skill's installed runtime payload, so that a Skill installed from a
pinned clean checkout can satisfy C2 without any change to `SKILL.md`, the
activation protocol, the acceptance rubric, or fixture semantics.

**Status: implemented.** §1–§8 are the design as written before implementation
and are preserved unedited; §9 is the as-built record, including two count
corrections and the owner decision on the disclosed residual. The implementation
changed `distribution/managed-files.txt` and added two tests. No fixture was
executed, no `EVAL-006` exists, no Host Acceptance Record was written. Host
Acceptance remains **UNVERIFIED**, RC Gate 4 remains **UNMET**.

- Boundary: HEAD `9006a241fc79ca68082dcc5d17407b55c95b9433`, branch `main`.
- Blocker addressed: **B9**, recorded in
  [`phase15-execution-surface-design.md`](phase15-execution-surface-design.md) §4.3.
- Authorization: P10 approved for the distribution managed-set / packaging
  boundary only.

## 1. P10 Decision

**B9 is solvable inside the authorized scope. No stop condition triggered.**

The stop clause required halting if `SKILL.md`, the activation protocol, the
rubric, or fixture semantics must change. None must. `SKILL.md` declares 14
relative references; all 14 resolve under the proposed payload, verified by
enumeration in §5. `AGENTS.md` likewise stays intact.

One residual is **not** resolvable in scope and is escalated rather than
absorbed: 17 markdown links in 4 non-protocol documents point at material the
proposal deliberately stops distributing (§5.3). Repairing them would mean
editing references, which the authorization forbids as a means of manufacturing
a C2 pass. They are disclosed, not repaired.

## 2. How the Acceptance Corpus Reaches a Fixture Today

The contamination has a single entry edge, and it is not an accident of layout.

```text
SKILL.md §Supporting Material
  └─▶ README.md#repository-guide          ← runtime-declared, must stay
        ├─▶ docs/cross-host-acceptance.md      the governing procedure
        ├─▶ docs/release/v1.0-rc-checklist.md  the gate definitions
        ├─▶ tests/evaluation-rubric.md         the rubric
        ├─▶ tests/scenarios.md                 the numbered fixture scenarios
        ├─▶ evaluations/README.md              prior traces and scores
        ├─▶ evaluations/claude-code/README.md
        └─▶ evaluations/templates/host-acceptance-record.md
```

`README.md#repository-guide` is the anchor `SKILL.md` line 353 sends a runtime
agent to, and the Repository Guide list itself enumerates the rubric, the
scenarios, and the evaluation corpus. So the corpus is not merely co-located
with the Skill — it is indexed by the document the Skill points at.

Measured closure at the pinned commit: `SKILL.md` reaches **78 files**
transitively, of which **14 are acceptance corpus**, every one of them via
`README.md`. Zero acceptance files are referenced by `SKILL.md` directly.

That asymmetry is what makes the problem tractable: the corpus is reachable
through an index, not through protocol text.

## 3. File Classification

### 3.1 True Skill runtime dependency — MUST remain installed

The 14 references `SKILL.md` declares, plus the documents they need:

| Path | Referenced from |
|---|---|
| `.looppilot/CHECKLIST.md` | SKILL.md §15 |
| `.looppilot/README.md` | SKILL.md §10 |
| `.looppilot/RESEARCH-TEMPLATE.md` | SKILL.md §13 |
| `.looppilot/tasks/TASK-TEMPLATE.md` | SKILL.md §12 |
| `README.md` | SKILL.md §Supporting Material |
| `docs/full-loop-checkpoint-and-context-recovery.md` | SKILL.md §15 |
| `docs/lifecycle.md` | SKILL.md §4 |
| `docs/loop-engineering-model.md` | SKILL.md §11 |
| `docs/mode-selection-and-escalation.md` | SKILL.md §11 |
| `docs/multi-agent-coordination.md` | SKILL.md §12 |
| `docs/project-closure-and-final-delivery.md` | SKILL.md §11 |
| `docs/protocol-load-profiles.md` | SKILL.md §11 |
| `docs/protocol-modes-and-state-sources.md` | SKILL.md §11 |
| `docs/safety-and-stopping.md` | SKILL.md §7 |

Plus the wider protocol and design documentation the Repository Guide indexes
(28 `docs/*.md` in total), `AGENTS.md`, `agents/`, `examples/`, `.looppilot/`
templates, the distribution scripts, `LICENSE`, and `CHANGELOG.md`.

### 3.2 Acceptance-only — MUST be stripped for C2

| Group | Files | Why it is acceptance material |
|---|---|---|
| `evaluations/` | 37 | Prior traces, scores, host acceptance records, and the templates that define them |
| `docs/release/` | 7 | Gate definitions, Phase 14 closure and evidence analyses, readiness audit |
| `docs/evaluations/` | 4 | Host acceptance records, decision, and review |
| `docs/cross-host-acceptance.md` | 1 | The governing acceptance procedure |
| `tests/evaluation-rubric.md` | 1 | The rubric |
| `tests/scenarios.md` | 1 | The numbered scenarios — **fixture semantics** |
| `tests/test_*.py` | 17 | `test_cross_host_acceptance.py` asserts record structure, verdicts, and dimensions |
| `scripts/*.py` | 11 | `cross_host_acceptance_validation.py` encodes the verdict rules, the `not-evaluated` prohibition, and the reviewer-independence check |
| `requirements-dev.txt` | 1 | Exists only to run the above |

`scripts/` and `tests/` are included deliberately, not as hygiene. A fixture that
read `scripts/cross_host_acceptance_validation.py` would learn the acceptance
rules as executable specification — 13 occurrences of verdict and dimension
vocabulary — which is exactly what C2 exists to prevent. Classifying them as
merely "non-runtime" would understate the exposure.

### 3.3 Deliberately retained despite being non-runtime

| Path | Reason |
|---|---|
| `.github/workflows/validate.yml` | `tests/test_distribution.py::test_official_manifest_includes_validator_workflow` asserts its presence in the manifest. It is a Distribution-004 contract decision, contains no acceptance material, and removing it is out of P10 scope |
| `CONTRIBUTING.md`, `INSTALLATION-VALIDATION.md`, `docs/validation.md` | Contribution and maintenance documentation, not acceptance material. `AGENTS.md` links to `docs/validation.md`, and `AGENTS.md` may not be modified — retaining it keeps `AGENTS.md` link-clean |

## 4. Proposed File Changes

**One file changes.** No script, no protocol document, no test assertion, no
rubric.

### 4.1 `distribution/managed-files.txt`

The manifest format supports literal paths and directory entries. It has **no
exclusion syntax**, so `docs/` cannot be kept while `docs/release/` is dropped.
Two implementations exist:

| Option | Change | Verdict |
|---|---|---|
| **A. Explicit `docs/` enumeration** | Replace the `docs/` directory entry with 28 literal paths | **Recommended.** No parser change; the payload becomes explicit and auditable |
| B. Add exclusion syntax | Extend the manifest grammar and both `loop-pilot.ps1` and `loop-pilot.sh` parsers | Rejected: a distribution *implementation* change, wider than P10, and it adds a format feature for one caller |

Option A additionally satisfies open review finding **F-8** in
[`HOST-ACCEPTANCE-REVIEW.md`](../evaluations/claude-code/HOST-ACCEPTANCE-REVIEW.md),
which recommends defining the payload set explicitly and naming the excluded
trees. This proposal is the first change that would close it.

Proposed content:

```text
# Official managed payload. Directory entries use tracked files in a Git checkout.
# Acceptance material is deliberately excluded: evaluations/, tests/, scripts/,
# docs/release/, docs/evaluations/, docs/cross-host-acceptance.md.
install.ps1
install.sh
update.ps1
update.sh
uninstall.ps1
uninstall.sh
status.ps1
status.sh
INSTALLATION-VALIDATION.md
distribution/managed-files.txt
distribution/version.txt
distribution/loop-pilot.ps1
distribution/loop-pilot.sh
.github/workflows/validate.yml
SKILL.md
README.md
AGENTS.md
CHANGELOG.md
CONTRIBUTING.md
LICENSE
docs/architecture-pattern-selection.md
docs/baseline-evidence-and-verification-surface.md
docs/coordination-necessity-and-delegation-fallback.md
docs/design-rationale.md
docs/evaluation-synthesis-and-protocol-calibration.md
docs/final-assignment-behavioral-evidence.md
docs/final-protocol-calibration.md
docs/full-loop-checkpoint-and-context-recovery.md
docs/full-loop-contracts-and-ledgers.md
docs/full-loop-delivery-review-and-closure.md
docs/full-loop-migration-plan.md
docs/host-capabilities.md
docs/installation.md
docs/lifecycle-authority-and-derived-projections.md
docs/lifecycle.md
docs/loop-engineering-model.md
docs/mmgh-behavioral-evidence.md
docs/mode-selection-and-escalation.md
docs/multi-agent-coordination.md
docs/phase9-second-protocol-calibration.md
docs/project-closure-and-final-delivery.md
docs/project-closure.md
docs/project-engineering-context.md
docs/protocol-load-profiles.md
docs/protocol-modes-and-state-sources.md
docs/safety-and-stopping.md
docs/v1-migration.md
docs/validation.md
agents/
.looppilot/
examples/
```

`requirements-dev.txt` is dropped with `scripts/` and `tests/`; it exists only to
install their dependencies.

## 5. Managed Set Before / After, and Reference-Closure Proof

### 5.1 Before / after

| | Before | After | Removed |
|---|---:|---:|---:|
| Manifest entries | 29 | 52 | — |
| Expanded files at the pin | **161** | **81** | **80** |

| Removed group | Files |
|---|---:|
| `evaluations/` | 37 |
| `tests/` (incl. rubric, scenarios, 17 test modules) | 19 |
| `scripts/` | 11 |
| `docs/release/` | 7 |
| `docs/evaluations/` | 4 |
| `docs/cross-host-acceptance.md` | 1 |
| `requirements-dev.txt` | 1 |

### 5.2 Closure proof — `SKILL.md` resolves completely

All 14 references `SKILL.md` declares, checked against the proposed payload:

```text
.looppilot/CHECKLIST.md                             RESOLVES
.looppilot/README.md                                RESOLVES
.looppilot/RESEARCH-TEMPLATE.md                     RESOLVES
.looppilot/tasks/TASK-TEMPLATE.md                   RESOLVES
README.md                                           RESOLVES
docs/full-loop-checkpoint-and-context-recovery.md   RESOLVES
docs/lifecycle.md                                   RESOLVES
docs/loop-engineering-model.md                      RESOLVES
docs/mode-selection-and-escalation.md               RESOLVES
docs/multi-agent-coordination.md                    RESOLVES
docs/project-closure-and-final-delivery.md          RESOLVES
docs/protocol-load-profiles.md                      RESOLVES
docs/protocol-modes-and-state-sources.md            RESOLVES
docs/safety-and-stopping.md                         RESOLVES

unresolved: 0 / 14
```

`AGENTS.md`'s single outbound reference, `docs/validation.md`, also resolves.

### 5.3 Disclosed residual — 17 dangling links in 4 documents

These are **not** repaired, because repairing them means editing references:

| Document | Dangling | Targets |
|---|---:|---|
| `README.md` | 13 | `docs/cross-host-acceptance.md`, `docs/release/v1.0-rc-checklist.md`, `evaluations/README.md`, `evaluations/claude-code/README.md`, `evaluations/templates/host-acceptance-record.md`, `tests/evaluation-rubric.md`, `tests/scenarios.md` |
| `CONTRIBUTING.md` | 2 | `tests/evaluation-rubric.md`, `tests/scenarios.md` |
| `docs/installation.md` | 1 | `docs/cross-host-acceptance.md` |
| `docs/full-loop-migration-plan.md` | 1 | `docs/cross-host-acceptance.md` |

Nine of the thirteen `README.md` links sit inside `#repository-guide`, the
anchor `SKILL.md` points at. A runtime agent following the Supporting Material
pointer would therefore see index entries whose targets are not installed.

**This is the one thing the proposal does not fix, and it is an owner
decision.** Three exits, none taken here:

| Exit | Cost |
|---|---|
| Accept as a documented packaging boundary — the installed tree is a runtime payload; undistributed development material is simply absent | No file edited. The Repository Guide becomes partially inaccurate inside the installed copy |
| Rewrite the 17 links as absolute repository URLs | Changes references in 4 documents. Not deletion, but still reference editing, which the authorization excludes as a route to C2 pass |
| Split the Repository Guide into runtime and development halves | Edits `README.md` structure; closest to "deleting references"; most likely to be read as engineering the surface to pass |

C2 is satisfied under all three, because C2 concerns reachability of acceptance
material, and under every exit the material is absent. The choice is about
documentation honesty in the installed copy, not about the control.

## 6. Distribution-004 Contract Impact

### 6.1 Already-supported behavior

Retiring managed files is a modelled operation, not a new one:

| Existing behavior | Test |
|---|---|
| Update applies additions and removals | `test_safe_update_applies_adds_and_removals` |
| A retired file the user customized is preserved and reported, never silently deleted | `test_retired_customized_file_is_preserved_and_reported` |
| Uninstall removes managed files and never touches unmanaged user content | `test_reinstall_and_uninstall_remain_correct_after_update` |

So an existing installation updating to the new manifest reports
`Files to remove: 80`, deletes unmodified copies, and preserves any the user
edited. No contract extension is required.

### 6.2 What changes observably

- `status.ps1` / `status.sh` will report a smaller managed set. The
  `RECOVERY_REQUIRED` state of the present hand-placed installation is unrelated
  and is still closed by the §8 clean reinstall in the execution-surface design.
- The installed tree drops from 161 to 81 files.
- `.looppilot-installation` records the same commit; only the payload narrows.

### 6.3 Documents that describe the old payload

`DISTRIBUTION-ACCEPTANCE-REPORT.md`, `DISTRIBUTION-003-REPORT.md`, and
`DISTRIBUTION-BASH-VALIDATION.md` describe the manifest as it stood at their
commits. They are preserved evidence and **must not be rewritten**. They become
historical descriptions of a superseded manifest, which is the normal and
correct outcome for dated evidence.

`docs/installation.md` describes the manifest mechanism generically — "the
authoritative list of managed payload roots" — and remains accurate. It needs
review, not necessarily change.

## 7. Test Impact and Required Test Design

### 7.1 Existing tests

| Test | Effect |
|---|---|
| `test_official_manifest_includes_validator_workflow` | **Passes** — `.github/workflows/validate.yml` is deliberately retained (§3.3) |
| All other `test_distribution.py` tests | Unaffected. They build synthetic sources with their own manifests and never assert the official payload's size or membership |

No existing test assertion needs to change. This was a design constraint, not an
observation: retaining `.github/workflows/validate.yml` was chosen partly to
keep it true.

### 7.2 New tests proposed (design only, not written)

Two tests, both in `tests/test_distribution.py`, both asserting the packaging
boundary rather than any acceptance outcome:

1. **`test_official_manifest_excludes_acceptance_corpus`** — expand the manifest
   against the tracked tree and assert no expanded path starts with
   `evaluations/`, `tests/`, `scripts/`, `docs/release/`, `docs/evaluations/`,
   or equals `docs/cross-host-acceptance.md`.
2. **`test_skill_relative_references_resolve_in_managed_payload`** — parse the
   relative markdown links in `SKILL.md`, expand the manifest, and assert every
   target is in the expanded set. This is §5.2 as a regression guard, so a
   future manifest edit cannot silently strip a runtime dependency.

The second test is the more valuable of the two: it converts the closure proof
from a one-time analysis into a standing invariant.

Neither test evaluates host behavior, scores a rubric dimension, or touches
acceptance state.

## 8. What This Does Not Do

It does not modify `SKILL.md`, `AGENTS.md`, protocol semantics, roles, modes,
Ledger, lifecycle, Checkpoint rules, authority or stopping rules, the acceptance
rubric, fixture semantics, or the acceptance boundary. It does not implement the
proposed manifest — §4.1 is a proposal, and `distribution/managed-files.txt` is
unchanged on disk. It creates no `EVAL-006`, runs no fixture, and writes no
Host Acceptance Record.

It does not make C2 satisfiable on its own either. C2 also requires the fixture
working directory to be outside the repository and free of acceptance material;
this proposal only removes the Skill directory as a second, independent source
of it.

Host Acceptance remains **UNVERIFIED**. RC Gate 4 remains **UNMET**.

## 9. Implementation Record

P10 approved Option A. What follows is what was built, measured against the
tracked tree rather than restated from §4–§7.

### 9.1 Files changed

| File | Change |
|---|---|
| `distribution/managed-files.txt` | The `docs/` directory entry replaced by 28 literal paths; `evaluations/`, `scripts/`, `tests/`, and `requirements-dev.txt` removed; header comment names the excluded trees |
| `tests/test_distribution.py` | Two boundary tests added (§9.4); `test_official_manifest_includes_validator_workflow` refactored onto a shared manifest reader with no change to what it asserts |

`SKILL.md`, `AGENTS.md`, the activation protocol, the rubric, and fixture
semantics are untouched. The stop clause never triggered. `tests/` is no longer
distributed, so the two new tests guard the boundary from the repository without
shipping inside the payload they describe.

### 9.2 Measured before / after

| | Before | After | Delta |
|---|---:|---:|---:|
| Manifest entries | 29 | **51** | +22 |
| Expanded payload files | 161 | **81** | **−80** |
| Files added to the payload | — | — | **0** |

**Correction to §5.1:** the entry count after the change is 51, not the 52 stated
there. The design table was off by one; the expanded file counts (161 → 81) were
correct and are confirmed exactly.

Removed groups, each matching §5.1:

| Removed group | Files |
|---|---:|
| `evaluations/` | 37 |
| `tests/` | 19 |
| `scripts/` | 11 |
| `docs/release/` | 7 |
| `docs/evaluations/` | 4 |
| `docs/cross-host-acceptance.md` | 1 |
| `requirements-dev.txt` | 1 |

Every literal manifest entry resolves to a tracked file, so neither installer
fails its `assert_source_file` preflight.

### 9.3 Reference closure, as measured

`SKILL.md`: **14 relative references, 0 unresolved.** `AGENTS.md`: **9 relative
references, 0 unresolved.**

**Correction to §5.2:** `AGENTS.md` was described as having a single outbound
reference (`docs/validation.md`). It has nine relative links; the other eight
target `.looppilot/` templates and `SKILL.md`. All nine resolve, so the
conclusion stands and the retention decision for `docs/validation.md` in §3.3
was correct.

### 9.4 Tests added

Both in `tests/test_distribution.py`, both asserting packaging structure and
neither touching acceptance state:

- `test_official_manifest_excludes_acceptance_corpus` — expands the manifest and
  fails if any payload path is under `evaluations/`, `tests/`, `scripts/`,
  `docs/release/`, or `docs/evaluations/`, or is `docs/cross-host-acceptance.md`.
- `test_skill_relative_references_resolve_in_managed_payload` — turns the §5.2
  closure proof into a standing invariant, so a later manifest edit cannot
  silently strip a document the protocol depends on.

### 9.5 Owner decision on the disclosed residual

**Exit 1 of §5.3 is taken: the residual is accepted and documented, not
repaired.**

The residual is a **documentation residual produced by the installed runtime
deliberately excluding the acceptance corpus** — a consequence of the packaging
boundary, not a defect in any document. Measured in the new payload:

| Document | Dangling occurrences | Distinct targets |
|---|---:|---:|
| `README.md` | 13 | 7 |
| `CONTRIBUTING.md` | 2 | 2 |
| `docs/installation.md` | 1 | 1 |
| `docs/full-loop-migration-plan.md` | 1 | 1 |
| **Total** | **17** | **11** |

§5.3 reported the 17 occurrences; the 11-distinct-target figure is added here.
Nine of `README.md`'s occurrences sit inside `#repository-guide`, the anchor
`SKILL.md` points at, so a runtime agent following Supporting Material sees index
entries whose targets are absent from its installation.

Explicitly not done, by instruction: the links were not rewritten to absolute
repository URLs, no reference was deleted, and the `README.md` Repository Guide
was not restructured. Each would have meant editing references to make the C2
control look satisfied, which is the failure mode the authorization forbids.

Two properties make the residual safe to carry:

- **The control is unaffected.** C2 concerns whether acceptance material is
  reachable from a fixture. Under every §5.3 exit the material is absent; the
  exits differ only in the honesty of the installed index.
- **Repository validation is unaffected.** `validate.py` resolves relative links
  against the repository tree, where all 17 targets still exist. The residual is
  a property of an installed copy only, so it produces no repository finding and
  cannot be mistaken for one.

The Repository Guide is therefore accurate about the repository and partially
inaccurate about an installation. That is the accepted cost, recorded here so a
later reader does not mistake it for drift and repair it.

### 9.6 Clean-checkout verification

Two clean clones of `9006a241` were made outside the repository: `pre-b9` at
HEAD, and `post-b9` with this change applied. Every result below is observed
output, not inference.

| Check | Result |
|---|---|
| Fresh install from `post-b9` (PowerShell) | 81 payload files + 1 state file; exit 0 |
| Fresh install from `post-b9` (Bash) | identical 81-file payload; exit 0 |
| `status.ps1` and `status.sh` on that installation | **CURRENT**, `Files current: 81`, 0 to add, remove, or conflict |
| Acceptance paths anywhere in a fresh installation | **0**, including hidden directories |
| `SKILL.md` closure inside the installed tree | 14 refs, 0 unresolved |
| `AGENTS.md` closure inside the installed tree | 9 refs, 0 unresolved |
| Documented residual inside the installed tree | 17 dangling occurrences in the 4 expected documents |
| `pre-b9` install then update to `post-b9` | `Files to remove: 80` applied; 79 acceptance files deleted |
| Retired file the operator had customized | preserved and reported: `preserved retired customized file as user-owned content` |
| Retired file left pristine | deleted, e.g. `tests/evaluation-rubric.md` |
| Status after that update | **CURRENT**, `Files current: 81` |
| Uninstall (PowerShell, after update) | exit 0; managed payload removed |
| Uninstall (Bash, after fresh install) | exit 0; **0 files remain** |

Cross-shell agreement holds: a Bash-installed tree reads `CURRENT` under
`status.ps1`. No Distribution-004 behavior regressed.

One cosmetic observation: the update removes retired files but not the
directories that held them, leaving 14 empty directories. They contain nothing
readable and have no bearing on the boundary.

### 9.7 Two findings the verification produced, neither closable in P10 scope

§4.4 of the execution-surface design asks that unreachability be verified rather
than asserted. Doing so surfaced two exposures that the manifest change does not
remove. Both are reported, not repaired. Both are classified against the boundary
text in
[`phase15-b12-b13-decision-analysis.md`](phase15-b12-b13-decision-analysis.md),
which finds neither of them a Gate 4 blocker and corrects the second one's
description below.

**B12 candidate — the acceptance *rules* survive in prose, in retained runtime
documentation.**

§3.2 excluded `scripts/cross_host_acceptance_validation.py` because it "encodes
the verdict rules, the `not-evaluated` prohibition, and the reviewer-independence
check". The same rules are described in prose in documents the payload keeps:

| Installed document | What it discloses |
|---|---|
| `docs/validation.md` | The four-value verdict enum; that there are eight dimension rows and a result enum; that a failed dimension forces `rejected` rather than `unverified`; that an accepted verdict needs a 40-character commit, both a Lightweight-shaped and a Full-Loop-shaped fixture, a trace author distinct from the reviewer, and **the lowest critical rubric score at 2 or higher** |
| `README.md` | Eight protocol dimensions; that the rubric uses **0-to-3 scoring** |
| `CONTRIBUTING.md` | That evaluators must not infer a score |

The eight dimension *names* do not leak, and no rubric text leaks. What leaks is
the scoring scale, the pass threshold, and the verdict vocabulary — enough for a
fixture to know what it is being measured against.

This is not closable under the present authorization. `docs/validation.md` is
retained precisely because `AGENTS.md` links to it (§3.3), and `AGENTS.md` may not
be modified; dropping the document would break a reference, and editing it is
reference editing. It needs an owner decision of the same kind P10 gave for B9.

**B13 candidate — an *upgraded* installation keeps the whole corpus under
`.looppilot-backups/`.**

The update that retires 80 files backs them up first, inside the installation
directory. After the upgrade the installed tree contained a
`.looppilot-backups/<id>/` holding `tests/evaluation-rubric.md`,
`tests/scenarios.md`, `scripts/cross_host_acceptance_validation.py`, and the
entire `evaluations/` corpus — 83 files, all readable, all inside the directory
a fixture would be pointed at. Uninstall does not remove them either; it removes
the managed payload and leaves backups and preserved user content by design.

This is existing Distribution-004 safety behavior working correctly, not a
regression, and B9 was never scoped to change it. Its consequence is narrow and
specific: **the B9 remedy holds for a fresh install into an empty destination and
not for an in-place upgrade.** Both fresh installs verified in §9.6 were clean;
the upgraded one was not.

The mitigation already exists in the plan. §8 of the execution-surface design
requires a clean reinstall to close B1. That reinstall is now also a C2
precondition rather than only a B1 fix, and the two blockers close together —
which is what §8 of that document already predicted about B1 and B9.

### 9.8 What the implementation still does not do

It does not run a fixture, create `EVAL-006`, write a Host Acceptance Record, or
produce a score. It does not make C2 satisfiable on its own — C2 also requires a
fixture working directory outside the repository, and now also a fresh install
rather than an upgrade (§9.7). Blockers B1, B7, B8, and B10 in
[`phase15-execution-surface-design.md`](phase15-execution-surface-design.md) are
untouched, and §9.7 adds two candidates to them.

Host Acceptance remains **UNVERIFIED**. RC Gate 4 remains **UNMET**.
