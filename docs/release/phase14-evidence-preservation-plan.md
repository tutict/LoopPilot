# Phase 14.2 Evidence Preservation Plan

A plan for converting existing acceptance evidence from transient, local-only
artifacts into auditable repository evidence.

**This document moves no files, commits nothing, and modifies no existing
artifact.** It proposes a boundary; executing it is a separate authorized action.
Host Acceptance remains UNVERIFIED, the Phase 14 decision remains BLOCKED, no
gate is ticked, and nothing here creates a PASS or an RC approval.

- Boundary: HEAD `672f3955495cb4b6fff332c11eb23882f8479279`, branch `main`,
  9 ahead of `origin/main`, nothing pushed.
- Companions: [`phase14-closure-analysis.md`](phase14-closure-analysis.md),
  [`phase14-evidence-inventory.md`](phase14-evidence-inventory.md).

## 1. Preservation Principles

These three govern every disposition below.

1. **Preserving evidence does not equal acceptance.** Committing an artifact
   changes its durability, not its status. A transcript that proves nothing
   before it is committed proves exactly as much afterwards. Nothing in this plan
   advances any RC gate.
2. **A historical trace does not equal a reviewer verdict.** A trace records what
   happened. A verdict is a judgement made against a rubric by a reviewer
   independent of the trace author. No amount of preserved trace becomes a
   verdict by accumulation, and none of the preserved material may be summarised
   as though it were one.
3. **Loading proof does not equal protocol compliance.** That the host received
   `SKILL.md` byte-for-byte says nothing about whether it then obeyed the
   protocol. The strongest evidence in this plan is loading evidence, and it
   stops there.

A fourth principle follows from the three above and governs what may be
*written* during preservation:

4. **An absent artifact is never reconstructed.** Where a primary record exists,
   a summary of it is legitimate because it can be checked against the primary.
   Where no primary record exists, writing the missing artifact from memory would
   manufacture evidence, not preserve it. This is the line that separates
   category A from category B below, and it is not negotiable.

## 2. Evidence Disposition

### 2.1 Classification

**A — safe to preserve as historical evidence:** Fixture A transcript, implicit
fixture transcript, EVAL-002 and EVAL-003 package files as they stand, the
2.1.221 record, the 2.1.226 infrastructure probe, the EVAL-004 package and its
review.

**B — invalid as repository evidence:** the gitignored sandbox end states, any
reconstructed `trace.md` or `score.md` for EVAL-002/EVAL-003, Fixture A's
never-written final report, and the 0-byte agent output file.

**C — requires future independent verification:** every acceptance dimension 2–8
claim, the behavioural meaning of Fixture A's mode declaration, the meaning of
the implicit fixture's non-activation, the genuineness of the unsigned
transcripts, and any Host Acceptance Record for 2.1.224.

### 2.2 Disposition table

| Evidence | Current location | Repository status | Preserve? | Reason | Future requirement |
|---|---|---|---|---|---|
| **Fixture A transcript** (2.1.224 / claude-opus-5) | `.tmp/phase14/evidence/agent-a9c71729e35b6ff97.jsonl` | Outside version control (gitignored) | **Yes — A**, redacted first | Strongest loading evidence the project holds, and the only non-self-observing instance. Digest-anchored to `HEAD:SKILL.md`, so a reader can re-verify it from the repository alone | Redact 25 unrelated third-party Skill names per the EVAL-004 method; record the unredacted original's SHA-256; never edit afterwards, since editing breaks the digest that makes it evidence |
| **Implicit fixture transcript** (2.1.224 / claude-opus-5) | `.tmp/phase14/evidence/agent-a4964684a94e5758e.jsonl` | Outside version control (gitignored) | **Yes — A**, redacted first | Complete, uninterrupted host behaviour observation; the control that makes Fixture A interpretable | Same redaction. Preserve **unscored**. A reviewer, not this plan, decides what non-activation means for dimension 1 |
| **EVAL-002** (2.1.221, Lightweight-shaped) | `evaluations/claude-code/EVAL-002/` | Uncommitted | **Yes — A**, as-is | `environment.md`, `prompt.md`, and its reviewer report are accurate and already self-labelled as design, not observed behaviour | Commit unchanged. Its missing `trace.md`/`score.md` are category B and must stay missing until a re-run produces them |
| **EVAL-003** (2.1.221, Full-Loop-shaped) | `evaluations/claude-code/EVAL-003/` | Uncommitted | **Yes — A**, as-is | Same: an accurate record of a fixture that was designed and prompted | Commit unchanged. It has no reviewer report of its own; the EVAL-002 report covers both and says so |
| **Host Acceptance Record 2.1.220** | `evaluations/claude-code/host-acceptance-record-claude-code-2.1.220.md` | Committed | **Yes — A**, already preserved | Accurate `unverified` record; all dimensions `not-evaluated` | None. Do not revise |
| **Host Acceptance Record 2.1.221** | `evaluations/claude-code/host-acceptance-record-claude-code-2.1.221.md` | Uncommitted | **Yes — A**, with EVAL-002/003 | Accurate `unverified` record. Its own text states record and packages form one commit unit; committing it alone would break its evidence links | Commit in the same unit as EVAL-002 and EVAL-003 |
| **Host Acceptance Record 2.1.224** | Does not exist | n/a | **No — C** | AF-3. The combination with the strongest evidence has no record, and one cannot be written now: reviewer independence is absent and the required fields cannot be populated | Create only after a scored behavioural trace and an independent reviewer exist |
| **EVAL-004 package** | `evaluations/claude-code/EVAL-004/` | Committed | **Yes — A**, already preserved | Loading evidence with a documented redaction method and recorded digests; the model this plan follows | None. Its Arm A self-observation limit stands as written |
| **EVAL-004 review** | [`HOST-ACCEPTANCE-REVIEW.md`](../evaluations/claude-code/HOST-ACCEPTANCE-REVIEW.md) | Committed | **Yes — A**, already preserved | Honest package review that declines to score or issue a verdict | **C:** it is not the independent behavioural review the RC gate requires, and must never be counted as one |
| **2.1.226 infrastructure probe** | `.tmp/phase14/out/probe.jsonl` | Outside version control | **Yes — A**, redacted, strictly scoped | Documents why the pinned surface became unusable | Heavier redaction than the fixtures: it enumerates slash commands, agents, plugin paths, and memory paths. Label as 2.1.226 infrastructure only; **never merge into the 2.1.224 evidence set** |
| **Sandbox end states** | `.tmp/host-acceptance/sandbox-lw`, `sandbox-fl` (87 files) | Outside version control | **No — B** | End states with no provenance linking them to any specific execution. Committing them would create the appearance of behavioural evidence where none was preserved | None. They are superseded by a re-run, not by preservation |
| **EVAL-002/003 `trace.md`, `score.md`** | Do not exist | n/a | **No — B** | Writing them now would be reconstruction from memory. Principle 4 forbids it | Only a re-run creates them |
| **Fixture A final report** | Never written (run truncated by rate limit) | n/a | **No — B** | Does not exist and must not be synthesised from the transcript. The transcript is the evidence; a report inferred from it would be the trace author's narration wearing the fixture's voice | Only a re-run creates it |
| **Fixture A agent output file** | `…\tasks\a9c71729e35b6ff97.output` | Outside version control | **No — B** | 0 bytes. Carries no information | None |

## 3. Commit Boundary Proposal

This is a proposal. It is not executed here, and the owner decides whether and
when to execute it.

### 3.1 What should enter the repository before independent review

Two commit units, in this order. Both are additive and neither touches an
existing artifact.

**Unit 1 — the 2.1.221 package that already exists.** `EVAL-002/`, `EVAL-003/`,
and `host-acceptance-record-claude-code-2.1.221.md`, committed together and
unchanged. They are accurate, self-limiting, and already state their own gaps.

**Unit 2 — a new evaluation package for the Phase 14 fixtures**, holding:

- the redacted Fixture A and implicit fixture transcripts;
- an `environment.md` and `prompt.md`, both derivable from preserved primary
  sources — the prompts exist verbatim at `.tmp/phase14/prompt-fixture-a.txt`
  and `.tmp/phase14/prompt-implicit.txt`, and the environment is recoverable
  from the transcripts' own `version`, `model`, and `cwd` fields;
- an evidence index recording the unredacted originals' SHA-256 values and the
  redaction method, following
  [`EVAL-004/evidence/README.md`](../../evaluations/claude-code/EVAL-004/evidence/README.md);
- a `trace.md` **only** as an index into the preserved transcript, anchored to
  record positions so every line can be checked against the primary source.

Deliberately **not** in unit 2: any `score.md`, any dimension table with a
non-`not-evaluated` value, and any Host Acceptance Record. Nothing in the Phase 14
material supports them.

Two mechanical preconditions apply to unit 2, both consequences of existing
validation rather than new rules: a file under `evaluations/` must not declare a
recognised verdict unless it is a Host Acceptance Record, and every relative link
must resolve. `scripts/validate.py` already passes with the uncommitted EVAL-002,
EVAL-003, and 2.1.221 files present on disk, so unit 1 is verified to be
committable as-is.

### 3.2 What must remain outside until recreated

Nothing on this list may be authored, reconstructed, or inferred. Each requires a
new execution to exist at all.

| Item | Why it cannot be preserved | What recreates it |
|---|---|---|
| EVAL-002/EVAL-003 `trace.md` and `score.md` | No primary record was preserved | Re-running both fixtures with trace capture |
| Fixture A's final report and rubric score | The run was truncated before either existed | Re-running the Lightweight fixture to completion |
| All Full Loop behavioural evidence | Never executed | Running the Full Loop fixture |
| Sandbox end states as evidence | No provenance | Superseded by a traced re-run |
| A 2.1.224 Host Acceptance Record | Reviewer independence absent; required fields unpopulatable | An independent reviewer scoring a behavioural trace |
| Any dimension 2–8 result | No behavioural evidence exists for any of them | The fixtures above, then review |

The 429 incidents stay recorded as infrastructure evidence permanently. They are
never promoted into host behaviour, and never explain away a missing artifact as
though the artifact existed.

## 4. Remaining Acceptance Path

Unchanged from the closure analysis. Four items, in dependency order. No item is
added, and none is removed by anything in this plan.

1. **Lightweight fixture** — one completed run, preserved as a full package.
2. **Full Loop fixture** — one completed run, preserved as a full package.
3. **Independent reviewer** — a reviewer independent of the trace author, scoring
   a behavioural trace.
4. **Host Acceptance Record** — all required fields populated, including a
   reviewer decision, for a combination that has a scored trace.

Items 1 and 2 remain blocked on the execution-surface decision recorded in the
closure analysis. Item 3 does not depend on that surface and may proceed in
parallel. Item 4 depends on all three.

Executing this preservation plan advances none of these four. It makes the
evidence that already exists durable and auditable, so that when a reviewer
arrives there is something honest to review — and so that what is missing stays
visibly missing.
