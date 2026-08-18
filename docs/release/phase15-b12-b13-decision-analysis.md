# Phase 15 / B12 and B13 — Owner Decision Analysis

Two findings surfaced while verifying the B9 packaging boundary. This document
classifies each against the **text** of the Phase 15 acceptance boundary, rather
than against an intuition about what isolation ought to mean.

**This document changes no protocol file.** It modifies no `SKILL.md`,
`AGENTS.md`, rubric, fixture, acceptance semantics, or Distribution-004 backup
semantics. No fixture was run, no `EVAL-006` exists, no score and no Host
Acceptance Record were written. Host Acceptance remains **UNVERIFIED**, RC Gate 4
remains **UNMET**.

- Findings recorded in
  [`phase15-b9-packaging-boundary-design.md`](phase15-b9-packaging-boundary-design.md)
  §9.7.
- Governing text: [`phase15-acceptance-boundary.md`](phase15-acceptance-boundary.md)
  §5 and its controls C1–C8;
  [`phase15-execution-surface-design.md`](phase15-execution-surface-design.md) §4;
  [`docs/cross-host-acceptance.md`](../cross-host-acceptance.md).

## 1. B12 — Acceptance vocabulary in retained runtime documentation

### 1.1 The distinction that has to be made first

Two different things get called "acceptance material", and conflating them is
what would turn a documentation observation into a false gate failure.

| | What it is | Present in the payload after B9? |
|---|---|---|
| **Readable acceptance corpus** | The rubric, the numbered scenarios, prior traces and scores, Host Acceptance Records, the governing procedure, the verdict rules as executable code | **No.** All 80 files removed and verified absent from a fresh install |
| **Natural-language description of acceptance concepts** | Prose in runtime documentation that names verdicts, dimensions, and thresholds while containing none of the corpus | **Yes**, in `docs/validation.md`, `README.md`, `CONTRIBUTING.md` |

The second is B12. Its most substantive instance is `docs/validation.md`, which
describes the validator's Cross-Host Acceptance extension: the four-value verdict
enum, that there are eight dimension rows, that a failed dimension forces
`rejected`, and that an accepted verdict needs the lowest critical rubric score
at 2 or higher. `README.md` adds that the rubric uses 0-to-3 scoring. The eight
dimension **names** do not appear, and no rubric text appears.

### 1.2 What C2 actually says

> **C2.** No evaluation record, rubric, checklist, acceptance document, or
> project memory index is reachable from the fixture working directory.

Two properties of that sentence decide the classification. Its subjects are
**artifact classes** — record, rubric, checklist, document, index — and its
predicate is **reachable**. It is a statement about which files a context can
open. It says nothing about what a context may know, infer, or have been trained
on.

`phase15-execution-surface-design.md` §4.1 then operationalizes C2 as an explicit
list, under the heading *What must be unreachable*:

```text
tests/evaluation-rubric.md
tests/scenarios.md
evaluations/ in any form
docs/cross-host-acceptance.md
docs/release/phase15-acceptance-boundary.md
docs/release/phase15-execution-surface-design.md
every prior Host Acceptance Record
the project memory index
```

`docs/validation.md`, `README.md`, and `CONTRIBUTING.md` are not on it.

### 1.3 What the verification method proves about the intent

§4.4 defines how C2 is checked, and both checks are path-based:

- The static check enumerates the sandbox tree and asserts that **no prohibited
  filename appears**.
- The negative reachability probe instructs a throwaway session to **attempt to
  read each prohibited path** and preserves the host's `tool_result` error
  envelopes.

Neither check inspects vocabulary, and neither could. A control whose entire
verification apparatus is filename enumeration and path reads is a file-isolation
control. If C2 had meant conceptual isolation, §4.4 would be unable to verify it
and the boundary would have shipped an unverifiable requirement.

### 1.4 The boundary has a vocabulary control, and it is not C2

C7 is the only vocabulary rule in the entire boundary:

> **C7.** The implicit arm's prompt carries no protocol vocabulary — not
> `Lightweight`, `Full Loop`, `Ledger`, `Contract`, `Checkpoint`, `Barrier`, or
> `mode` — and names the Skill nowhere.

Three differences from C2, all of them deliberate. C7 governs **the prompt**, not
the filesystem. It governs **protocol** vocabulary, not acceptance vocabulary. It
applies to **one arm**, because the thing it protects is a specific observable —
whether the host activates without being told to. The words "vocabulary",
"knowledge", "conceptual", and "aware" appear nowhere else in the boundary
document, and `docs/cross-host-acceptance.md` contains no isolation requirement
of any kind.

So the boundary already knows how to write a vocabulary control when it wants
one, and it wrote exactly one, scoped narrowly, for a stated reason.

### 1.5 Classification

**B12 is not a C2 failure, and not a failure of any control C1 through C8.**

The rule in force is file isolation. The acceptance corpus is unreachable, which
is what C2 requires and what §9.6 of the B9 record verified by enumeration. That
`docs/validation.md` describes acceptance concepts in prose does not make it an
evaluation record, a rubric, a checklist, an acceptance document, or a project
memory index.

Because the existing rules do **not** require conceptual isolation, the stop
condition for B12 does not trigger and no new owner decision is forced.

### 1.6 Disclosed residual and the narrow interpretive gap

Two things are worth stating plainly rather than filing as closed.

**The residual is real but out of C2's scope.** A fixture that opened
`docs/validation.md` would learn the scoring scale, the pass threshold, and the
verdict vocabulary. That is not nothing. It is simply not what C2 controls, and
"this feels like it should count" is not a basis for declaring a gate failure
when the operative text says otherwise.

**One interpretive gap exists and is disclosed, not resolved.** C2's category
term "acceptance document" is broader than §4.1's file list. Someone could argue
that the Cross-Host Acceptance section of `docs/validation.md` is an acceptance
document in miniature. Under the text as written — category words operationalized
by an explicit list, verified by filename enumeration — it is not prohibited. The
owner may wish to close that gap explicitly in either direction. Doing so is a
boundary amendment, which §4.3 of the execution-surface design already forbids
this class of document from performing.

Not done here, deliberately: nothing was removed from the manifest to make this
finding disappear, and no wording in `docs/validation.md`, `README.md`, or
`CONTRIBUTING.md` was edited. Dropping `docs/validation.md` would break the
`AGENTS.md` reference that §3.3 of the B9 record retained it for, and `AGENTS.md`
may not be modified.

## 2. B13 — `.looppilot-backups/` and the upgrade path

### 2.1 Three states that must not be conflated

| State | What it is | Where it lives |
|---|---|---|
| **Fresh clean install** | `install.ps1` into an empty destination at the pinned commit | `$HOME\.claude\skills\loop-pilot` |
| **In-place upgrade** | `update.ps1`, or `install.ps1` over an existing tree | the same directory, with history |
| **Acceptance fixture execution** | An arm running in a sandbox | the fixture working directory, elsewhere |

C2 constrains what is reachable **from the fixture working directory**. The
sandbox is created empty per arm and discarded, so it never contains
`.looppilot-backups/` — that is not where the exposure is. The exposure is the
user-scope Skill directory, which §4.3 of the execution-surface design already
establishes is reachable from every fixture context by construction, because that
is how `SKILL.md` resolves its relative references.

### 2.2 Every transition path, measured

Reproduced on a clone of the pinned commit, with the observed real-world starting
condition: a payload present and no `.looppilot-installation` state file.

| Path | Operation | Acceptance files at normal paths | Files under `.looppilot-backups/` | `status.ps1` |
|---|---|---:|---:|---|
| **A** | `install.ps1`, no `-Force`, over existing tree | — | — | **refuses**, atomic, nothing copied |
| **B** | `install.ps1 -Force` over existing tree | **80** | 3 | **CURRENT** |
| **C** | `update.ps1` from a pre-B9 installation | 0 | **83** | **CURRENT** |
| **D** | `uninstall.ps1` then `install.ps1 -Force` | **80** | 3 | **CURRENT** |
| **E** | remove the destination, then `install.ps1` | **0** | **0** | **CURRENT** |

Only **E** produces a C2-clean Skill directory: 81 payload files, one state file,
no backups directory, no acceptance path anywhere.

### 2.3 The finding that matters more than the backups

The original B13 report named `.looppilot-backups/` as the exposure. Measurement
shows the backup directory is the *milder* case. Paths B and D are worse, and for
a reason that is a direct consequence of B9:

Narrowing the manifest reclassified 80 files from **managed** to **unmanaged**.
Distribution-004 never touches unmanaged content — by design, because that is
what protects user files. So on a directory that already held them:

- `install` does not remove them; it only writes the managed set.
- `uninstall` does not remove them; it only removes the managed set.
- `status` does not report them; its plan is computed over the managed set.

Only `update` computes a removal list, which is why path C clears the normal
paths — and it preserves what it removed under `.looppilot-backups/`.

**Consequently `status.ps1 = CURRENT` does not discriminate between a clean Skill
directory and one holding the entire acceptance corpus.** It reported `CURRENT`,
`Files current: 81`, `Files to remove: 0` on a tree containing
`tests/evaluation-rubric.md`, `tests/scenarios.md`, `docs/cross-host-acceptance.md`,
and all five prior evaluation packages at their ordinary readable paths.

This is not a Distribution-004 defect. Managed-set scoping is correct behavior
and the reason user content survives upgrades. It is a statement about what the
`CURRENT` check can and cannot attest.

### 2.4 Does the acceptance protocol require an upgrade-installed Skill?

No. Checked against every place the question could be answered:

| Source | What it requires | Upgrade required? |
|---|---|---|
| §5.1 pin table | Skill loading mode = "Installed, user-scope Skill directory" | No — a **location**, not an install history |
| §5.3 installation method | `install.ps1` from a checkout at the pinned commit; a **clean reinstall** because the present installation is hand-placed and untraceable; `status.ps1` = `CURRENT` before the first arm | No — it requires the opposite |
| The eight acceptance dimensions | Loading and activation, mode selection, authority and stopping, shared state, Full Loop artifacts, Checkpoint recovery, lifecycle projections, evidence honesty | **None concerns installation or upgrade** |
| `tests/evaluation-rubric.md` | Its only install-related dimension scores the **host** inventing or auto-installing a Skill | No |
| Boundary §6 non-goals | Explicitly forbids performing "Distribution-005 or any packaging experiment" | Upgrade validation is excluded, not required |

The word "upgrade" appears three times in the boundary document, never as a
requirement on the Skill under test.

### 2.5 Classification

**B13 is upgrade-path contamination outside the acceptance execution boundary. It
is not a Gate 4 blocker.**

The acceptance protocol requires a fresh clean install, evaluates protocol
behavior rather than distribution mechanics, and explicitly excludes packaging
experiments. An upgraded installation is not the artifact under test, so an
exposure that exists only on the upgrade path cannot block the gate.

It remains a real operational hazard for any operator who upgrades rather than
reinstalls, and it is recorded as such rather than dismissed.

### 2.6 Does B1's clean reinstall close B13?

**Under one reading of "clean reinstall", yes. Under the other, no — and the
prescribed verification cannot tell them apart.**

§5.3 prescribes `install.ps1 -Destination "$HOME\.claude\skills\loop-pilot"`
followed by `status.ps1` reporting `CURRENT`. Against the measured paths:

- If "clean reinstall" means **path E** — remove the destination, then install —
  it closes B13 completely. Verified: no backups directory, no acceptance path,
  `CURRENT`.
- If it means **path B or D** — force-install over the existing tree, or
  uninstall then install — B13 is **not** closed. 80 acceptance files remain at
  readable paths and `status.ps1` still reports `CURRENT`.
- Path A refuses outright, so an operator meeting B1 must choose between
  `-Force` and clearing the directory. The document does not say which, and the
  observed starting condition guarantees the fork is reached.

So B1 and B13 close together only if the reinstall is specified as
destination-removal-first. **The `CURRENT` precondition cannot verify it**, which
means §5.3's stated check is necessary but not sufficient for C2.

`phase15-execution-surface-design.md` §4.4 does not currently cover the gap
either: its static check enumerates "the sandbox tree and every path reachable
from it without traversing above it", which is the fixture working directory, not
the user-scope Skill directory.

Two candidate remedies exist, both of which amend acceptance-execution text and
therefore **belong to the owner, and neither is applied here**:

1. State the reinstall as destination-removal-first in §5.3, so path E is the
   only compliant reading.
2. Extend §4.4's static check to enumerate the installed Skill directory and
   assert that no §4.1 filename appears in it, so the property is verified rather
   than assumed. The negative reachability probe would then target the
   Skill-directory paths as well as the sandbox ones.

The second is the stronger of the two, because it checks the property that
matters instead of the procedure believed to produce it — the same reasoning
§4.4 already applies to the sandbox.

## 3. Consolidated answers

| Question | Answer |
|---|---|
| **B12 classification** | Not a C2 failure and not a failure of C1–C8. C2 is file isolation, operationalized as an explicit path list and verified by filename enumeration. The only vocabulary control, C7, governs the implicit arm's prompt and protocol vocabulary. Residual and one interpretive gap disclosed |
| **B13 classification** | Upgrade-path contamination outside the acceptance execution boundary. Not a Gate 4 blocker. The protocol requires a fresh clean install, scores protocol behavior only, and excludes packaging experiments |
| **Does B1 close B13?** | Only under the destination-removal-first reading. Paths B and D satisfy B1's stated `CURRENT` check while leaving 80 acceptance files readable, so the prescribed verification cannot distinguish a clean Skill directory from a contaminated one |
| **Exact remaining blockers** | **B1** clean reinstall, now carrying a C2 precondition and needing its reading fixed; **B7** score template missing 2 of 4 critical dimensions; **B8** no independent reviewer; **B10** `--bare` tension for IMP-1. **B9 closed.** **B12 and B13 classified, not blocking.** New owner decision offered on §5.3 and §4.4 wording, not taken |
| **Is a fresh clean acceptance surface structurally possible now?** | **Yes for the explicit arms, for the first time.** Path E plus a sandbox outside the repository yields a Skill directory and a working directory that both satisfy C2 by enumeration. B7 and B8 gate the score and the record, not the run. B10 remains a genuine open tension for IMP-1 only |

The last row is the substantive change. Before B9, §4.3 stated that "a correctly
installed Skill and a C2-compliant fixture context are mutually exclusive under
the current managed set". That is no longer true. The exclusion is dissolved, and
what stands between the current state and a C2-clean surface is a documented
reinstall procedure rather than a structural contradiction.

## 4. What this document does not do

It runs no fixture — not `LW-1`, `FL-1`, `FL-1R`, or `IMP-1`. It creates no
`EVAL-006`, no score, and no Host Acceptance Record. It ticks no RC gate. It
modifies no `SKILL.md`, `AGENTS.md`, rubric, fixture semantics, acceptance
semantics, or Distribution-004 backup semantics, and it amends neither C2 nor
§5.3 nor §4.4. It does not treat the distribution validation reported here as
Host Acceptance evidence: every measurement above is distribution mechanics
observed outside any acceptance arm, and none of it scores a dimension.

B7, B8, and B10 are untouched.

Host Acceptance remains **UNVERIFIED**. RC Gate 4 remains **UNMET**.
