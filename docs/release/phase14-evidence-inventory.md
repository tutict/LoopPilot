# Phase 14.1 Evidence Boundary Consolidation

This document inventories the acceptance evidence that already exists, so a
future independent reviewer can establish what each artifact does and does not
support without re-deriving it.

**It changes no acceptance status.** Host Acceptance remains UNVERIFIED, the
Phase 14 closure decision remains BLOCKED, no gate is ticked, and no verdict is
issued, revised, or upgraded here. It introduces no role, mode, lifecycle state,
or validator rule, and it is not itself acceptance evidence.

- Boundary: HEAD `672f3955495cb4b6fff332c11eb23882f8479279`, branch `main`,
  9 commits ahead of `origin/main`, nothing pushed.
- Companion analysis: [`phase14-closure-analysis.md`](phase14-closure-analysis.md).
- Gate definitions: [`v1.0-rc-checklist.md`](v1.0-rc-checklist.md).

## A. Evidence Inventory

Evidence IDs (`EI-n`) are row labels for reference **inside this document only**.
They are not a new identifier scheme and confer no authority.

Tracking status matters and is stated per row: artifacts marked *uncommitted* are
invisible to anyone who clones this repository, and artifacts marked *outside
version control* are invisible even to this working tree's history.

| Evidence ID | Source | Host / model / version | Evidence class | Verification level | Can support which RC gate | Limitations |
|---|---|---|---|---|---|---|
| EI-1 | `evaluations/claude-code/EVAL-001/` (committed) | Claude Code 2.1.220 / claude-opus-5, Skill **not loaded** | B — protocol behavior (control-shaped) | Self-authored trace, self-scored, non-independent review | None directly; contributes to *candidate hosts marked verified/unverified* | Scenario 43 only; protocol never loaded; all 8 dimensions `not-evaluated` |
| EI-2 | `host-acceptance-record-claude-code-2.1.220.md` (committed) | Claude Code 2.1.220 / claude-opus-5, not loaded | Record over EI-1 | Recorded, `unverified`, reviewer decision `not-reviewed` | *Candidate hosts marked verified/unverified* (partial) | Cannot satisfy *Host Acceptance Record completed*: no accepted verdict |
| EI-3 | `evaluations/claude-code/EVAL-002/` (**uncommitted**) | Claude Code 2.1.221 / claude-opus-5, loaded, explicit | B — intended, unrealised | `environment.md` + `prompt.md` only; **no trace, no score** | None | Incomplete evaluation; execution corroborated only by gitignored end state |
| EI-4 | `evaluations/claude-code/EVAL-003/` (**uncommitted**) | Claude Code 2.1.221 / claude-opus-5, loaded, explicit | B — intended, unrealised | `environment.md` + `prompt.md` only; **no trace, no score, no reviewer report** | None | Full-Loop-shaped fixture was prompted but no behavior is preserved |
| EI-5 | `host-acceptance-record-claude-code-2.1.221.md` (**uncommitted**) | Claude Code 2.1.221 / claude-opus-5, loaded, explicit | Record over EI-3/EI-4 | Recorded, `unverified`, `not-reviewed` | None | Its own evidence links point at uncommitted packages; record and packages form one commit unit that has not been committed |
| EI-6 | [`EVAL-004/`](../../evaluations/claude-code/EVAL-004/score.md) (committed) | Arm A: 2.1.224 / claude-opus-5. Arm B: 2.1.226 / claude-fable-5[1m] | A — reachability and loading | Arm A observed but **self-observing**; Arm B never reached a model turn | None | Establishes the loading half of dimension 1 only; every rubric dimension `n/a` |
| EI-7 | Phase 14 Fixture A transcript, `.tmp/phase14/evidence/agent-a9c71729e35b6ff97.jsonl` (**outside version control**) | Claude Code 2.1.224 / claude-opus-5, loaded, explicit | A — reachability, loading **and** invocation | Observed from a **non-self-observing** context; digest-anchored to HEAD | None while uncommitted | Run truncated by rate limit before its final report; no rubric applied |
| EI-8 | Phase 14 implicit fixture transcript, `.tmp/phase14/evidence/agent-a4964684a94e5758e.jsonl` (**outside version control**) | Claude Code 2.1.224 / claude-opus-5 | B — host behavior (non-activation) | Observed, complete, **deliberately unscored** | None | Records that LoopPilot was not invoked; must not be scored or read as a failure verdict |
| EI-9 | [`HOST-ACCEPTANCE-CLAUDE-CODE.md`](../evaluations/claude-code/HOST-ACCEPTANCE-CLAUDE-CODE.md) (committed) | Claude Code 2.1.224 | A — loading verification | Phase 13-A record; explicitly **not** an acceptance record | None | Self-limits: carries no verdict by construction |
| EI-10 | [`HOST-ACCEPTANCE-DECISION.md`](../evaluations/claude-code/HOST-ACCEPTANCE-DECISION.md) (committed) | Claude Code, all versions, all models | Decision document | Declares `UNVERIFIED` | None | Lives outside `evaluations/`; see audit finding AF-4 |
| EI-11 | [`HOST-ACCEPTANCE-REVIEW.md`](../evaluations/claude-code/HOST-ACCEPTANCE-REVIEW.md) (committed) | Reviews the EVAL-004 package | C — review, **package only** | Independent of the trace author; **not** organizationally independent | None | Judges packaging and evidence quality; explicitly declines to score a rubric or issue a verdict |
| EI-12 | [`distribution-load-record.md`](../evaluations/claude-code/distribution-load-record.md) (committed) | Claude Code 2.1.223 | Distribution evidence | `PARTIALLY OBSERVED` | None | Not acceptance evidence; a fifth host version, easily conflated with the others |
| EI-13 | Incidents INC-1/2/3 in the closure analysis, plus EVAL-004 Arm B | 2.1.224 and 2.1.226 | D — infrastructure | Recorded with raw evidence | None | Not host behavior; not a LoopPilot defect; never convertible into either |
| EI-14 | `SKILL.md` integrity digests (§A.1) | n/a | Supporting integrity | Recomputable from this repository alone | None alone; underpins EI-6 and EI-7 | Proves byte identity of the loaded artifact, nothing about behavior |

**No row in this table can satisfy any RC gate on its own.** That is the
inventory's principal result, not an omission in it.

### A.1 Two digests of the same file, both correct

Two different SHA-256 values for `SKILL.md` appear across the artifacts. They are
not in conflict; they measure different things, and neither record said so.

| Digest | Definition | Where used | Re-verified |
|---|---|---|---|
| `a432bc262b954ede6bbbba893be7ee9bc76da61270b08587ebff9b20d9981778` | Whole file, bytes as stored (17,648 bytes, LF) | EI-5 installation corroboration | Identical across working tree, installed copy, and the HEAD blob |
| `530bbaf7718c4fc7ae54446621a9ab0d67363c8bf9e4c82e1306466aefcb146a` | Body only: YAML frontmatter stripped, newlines normalised, trimmed | EI-6, EI-7 injected-body comparison | Identical across injected body, installed copy, and `HEAD:SKILL.md` |

The body-only form exists because a host injects the body without frontmatter, so
a whole-file digest cannot be compared against what the host actually loaded.
`SKILL.md` is byte-identical across the whole unpushed range — blob
`6e0f26a9e948659541f88fc066e4e70dfcb31b0b` — so both digests anchor to the same
artifact at both `aacbde44` and HEAD.

### A.2 Audit findings

Scope item 1 asked for duplicate evidence, missing metadata, unclear authority,
stale wording, and unsupported claims. Findings are recorded, not fixed; fixing
them is outside a documentation-only phase.

| ID | Category | Finding |
|---|---|---|
| AF-1 | Missing metadata | EI-3 and EI-4 lack `trace.md` and `score.md`; EI-4 also lacks a reviewer report. Already self-reported by the EVAL-002 reviewer report and by EI-5, so this is confirmation, not a new defect. |
| AF-2 | Evidence not in the repository | EI-3, EI-4, and EI-5 are uncommitted; EI-7 and EI-8 are outside version control entirely. **The strongest loading evidence the project has — EI-7 — is the least durable.** A reviewer given only a clone would see none of it. |
| AF-3 | Missing record | The 2.1.224 combination has the best evidence (EI-6, EI-7, EI-8) and **no Host Acceptance Record of any kind**. Records exist for 2.1.220 and 2.1.221 only. |
| AF-4 | Unclear authority | Acceptance-shaped documents live in two trees. Verdict single-authority is machine-checked under `evaluations/` only; EI-10 declares a host-wide decision under `docs/evaluations/` using the word *Decision* rather than *Verdict*, which the check does not scan. The declared direction is `UNVERIFIED`, so nothing is over-claimed, but a reviewer must be told which document is authoritative: **the record under `evaluations/` is.** |
| AF-5 | Stale wording | `evaluations/claude-code/README.md` describes the 2.1.220 not-loaded record as the state of play. Its conclusion is still correct — Claude Code is unverified — but it predates EI-5 through EI-8 and does not tell a reader that loading is now verified at 2.1.224. |
| AF-6 | Version sprawl | Five distinct Claude Code versions appear across the artifacts — 2.1.220, 2.1.221, 2.1.223, 2.1.224, 2.1.226 — each a separate acceptance combination that never generalises to another. |
| AF-7 | Unsupported claims | **None found.** Every dimension table inspected reads `not-evaluated` or `n/a`; EI-6 states explicitly that `n/a` is not a pass; EI-5 declines to promote installation evidence into its dimension table; EI-11 declines to issue a verdict. No artifact claims more than it observed. |
| AF-8 | Duplicate evidence | **No contradictory duplication found.** The two `SKILL.md` digests (§A.1) are the only apparent duplication and resolve to one artifact under two declared methodologies. |

## B. Evidence Authority Rules

These rules govern how the inventory above may be read. They restate existing
boundaries; none is new.

1. **Transcript evidence is not an acceptance decision.** A transcript records
   what happened. Acceptance is a decision made against a rubric by a reviewer.
   No volume of transcript converts into a verdict.
2. **Loading evidence is not protocol behavior evidence.** That the host loaded
   `SKILL.md` says nothing about whether it then selected a proportionate mode,
   respected authority and stopping rules, or handled shared state. EI-6 and EI-7
   are class A and stop there.
3. **A self-authored trace is not an independent review.** A context that
   observes itself, or a reviewer instantiated by the same operator from the same
   model, may catch real errors but supplies no organizational independence.
   EI-11 is a package review and says so itself.
4. **Discovery is not loading.** A host listing `loop-pilot` among its available
   Skills proves registration only. Loading requires the body to arrive in the
   context, and is established by digest comparison against the repository.
5. **Loading is not activation success.** The Skill body arriving proves
   availability, not that the host acts on it, and certainly not that it
   activates on an in-scope task without being told. EI-8 is the direct
   demonstration: same version, same model, same reachable Skill, and no
   invocation.

A corollary that follows from rules 4 and 5 and is worth stating outright, because
Phase 14 turned on it: **"LoopPilot was not invoked" and "LoopPilot could not be
invoked" are different findings.** EI-8 is the first. Neither EI-7 nor EI-8 is the
second.

## C. Remaining Evidence Gaps

| Gap | Current state | What would close it |
|---|---|---|
| **Lightweight fixture artifact** | Behavior was observed once (EI-7) but no `trace.md` or `score.md` exists, and the run was truncated before its report | One completed Lightweight-shaped run at a single pinned surface, preserved as a full package |
| **Full Loop fixture artifact** | **Never executed.** EI-4 prompted one; no behavior was preserved | One completed Full-Loop-shaped run, preserved as a full package |
| **Independent reviewer report** | Does not exist for any phase. EI-11 reviews packaging only and declines to score | A reviewer independent of the trace author scoring a behavioral trace |
| **Host Acceptance Record** | Two exist (2.1.220, 2.1.221), both `unverified`; **none exists for 2.1.224** | A record with all required fields populated, including a reviewer decision, for a combination that has a scored behavioral trace |

These four gaps are ordered by dependency: the two fixture artifacts are inputs to
the reviewer report, which is an input to the record. **No gap can be closed by
documentation, and none may be closed by relaxing a gate**, per the feature-freeze
scope in [`docs/cross-host-acceptance.md`](../cross-host-acceptance.md).

All four are blocked behind the same external condition recorded in the closure
analysis: no clean, live, non-contaminated execution surface exists at the pinned
combination. The independent reviewer gap is the exception — it does not depend on
the execution surface and can be progressed separately.

## D. Frozen Boundary

**No protocol change is required before these gaps are tested.**

The gaps in section C are evidence gaps, not specification gaps. Nothing in the
inventory shows a protocol defect, a missing capability, or an unmet
specification. AF-7 found no unsupported claim, and EI-8 — the one negative host
observation in the set — is a host behavior observation, not a LoopPilot defect.

Accordingly, and for the duration of this boundary:

- `SKILL.md` stays frozen at blob `6e0f26a9e948659541f88fc066e4e70dfcb31b0b`;
- no validator, test, role, mode, lifecycle state, or acceptance layer is added
  or altered to accommodate a gap;
- EI-8 in particular **must not** be answered by changing LoopPilot's activation
  wording, triggers, or description. Tuning the protocol to make a recorded host
  observation disappear would destroy the observation and prove nothing;
- the audit findings in §A.2 are recorded for a future authorized phase and are
  deliberately left unfixed here.

The correct next action remains the one recorded in the closure analysis: a single
owner decision on the acceptance boundary. This document exists so that when a
surface and a reviewer become available, the evidence they inherit is already
sorted, bounded, and honest about its own limits.
