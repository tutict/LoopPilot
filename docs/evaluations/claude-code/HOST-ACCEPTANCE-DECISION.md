# Host Acceptance Decision: Claude Code

- Decision: **UNVERIFIED**
- Scope of this decision: Claude Code, all versions, all models, all Skill
  loading modes
- Decision date: 2026-08-09
- Repository boundary: `b482c9c990b9912d99230460bcd7540b64fd74fa`, plus the
  Phase 13 commits that carry this document
- Evidence considered: [`HOST-ACCEPTANCE-CLAUDE-CODE.md`](HOST-ACCEPTANCE-CLAUDE-CODE.md),
  [`HOST-ACCEPTANCE-REVIEW.md`](HOST-ACCEPTANCE-REVIEW.md), and
  [`evaluations/claude-code/EVAL-004/`](../../../evaluations/claude-code/EVAL-004/score.md)

## The Rule Applied

`ACCEPTED` is permitted only when the independent review returns Spec `PASS`,
Standards `PASS`, and Evidence `PASS` or `PASS-WITH-FINDINGS`. Otherwise the
status stays `UNVERIFIED`.

That rule is a gate, not a grant. Passing it makes acceptance permissible; it
does not make acceptance earned. The conditions in
[`docs/cross-host-acceptance.md`](../../cross-host-acceptance.md) remain in
force on top of it, and this decision applies both.

## Review Result

| Axis | Result |
|---|---|
| Spec | PASS |
| Standards | **FAIL** |
| Evidence | PASS-WITH-FINDINGS |

Findings: 0 blocker, 3 major, 9 minor. None is a Finding against the frozen v1
protocol; every one is against this evaluation's packaging or method, so none
feeds Release Candidate condition 6.

## Decision

**UNVERIFIED.** Two independent reasons, either of which alone is sufficient.

**First, the gate is not met.** Standards returned `FAIL`. The reviewer's F-1
found the package missing `score.md`, any rubric score, a reviewer decision, a
named trace author, and any self-declaration of incompleteness, against explicit
MUSTs in the acceptance procedure and in `evaluations/README.md`. The public
validator does not check those, which is why a reviewer had to.

**Second, and more fundamentally, the underlying protocol conditions are not
met, and no amount of remediation to this package could meet them.** An
`accepted` verdict requires every acceptance dimension to be `pass`;
`accepted-with-residuals` requires every dimension to be `pass` or `partial`.
EVAL-004 exercised no behavioral fixture at all:

- Dimension 1, Skill loading and activation: the loading half is observed for
  one combination. The activation half — activating on an in-scope task without
  fabricating a trigger — was never exercised, because activation was explicit
  in every arm. `partial` at most, never `pass`.
- Dimensions 2 through 8 — mode selection, authority and stopping, shared-state
  handling, Full Loop artifact handling, checkpoint recovery, lifecycle
  projections, evidence honesty: all `not-evaluated`. A dimension without
  preserved evidence is `not-evaluated`, which is not `pass` and not `partial`.
- No rubric score exists, so the requirement that all four critical dimensions
  score 2 or higher cannot be met.
- No Lightweight-shaped and no Full-Loop-shaped fixture was run, and an accepted
  verdict requires both.

So the honest position is not "acceptance was blocked by a packaging defect".
Acceptance was never in reach. Phase 13 verified that the host loads the Skill.
It did not evaluate whether the host follows the protocol, which is what
acceptance measures.

## What Changed, and What Did Not

**Changed.** The blocking question at the start of Phase 13 was that Skill
loading had never been verified on any host. It is now verified, for exactly
one combination — Claude Code 2.1.224 with claude-opus-5, loaded from user scope
under explicit invocation — with the host-injected body proven byte-identical to
the installed `SKILL.md` body. Discovery, separately, is verified on Claude Code
2.1.226.

**Not changed.** No host verdict. Every Claude Code combination remains
`unverified`, which for combinations without a record is the default and not a
downgrade. This document creates no Host Acceptance Record and changes none.
Host verdicts live in records under `evaluations/`, and publishing a second
document that declared a verdict would create exactly the lifecycle drift the
protocol forbids.

**Explicitly not inferred.** Discovery on 2.1.226 was not read as loading on
2.1.226. Loading on 2.1.224 was not carried to 2.1.226, to claude-fable-5[1m],
or to Claude Code as a class. A verdict is scoped to one host, version, model,
and loading mode.

## Finding Disposition

Applied to the evidence package after the review was written, and before either
was committed. The review therefore describes the package as it stood when
reviewed; this list is the difference.

| ID | Severity | Disposition |
|---|---|---|
| F-1 | major | Fixed. Added `score.md` recording every rubric dimension as `n/a` with the reason, `Reviewer decision: not-reviewed`, a named trace author, and an explicit declaration that EVAL-004 is an incomplete evaluation. No score was fabricated. |
| F-2 | major | Fixed. Added a committed `evidence/` directory holding a sanitised Arm A transcript excerpt and the full stream-json output of all three Arm B runs, with the unredacted originals' SHA-256 values recorded. Third-party inventory names in the `system/init` events are redacted; counts, ordering, and the `loop-pilot` entries are preserved, and the redaction is documented. |
| F-3 | major | Partly fixed. Arm B2 was retried at a materially later time and reproduced the identical failure, so the condition is persistent rather than transient. The loading claim still rests on self-observation and now says so explicitly. Not fully resolvable without a second machine or account. |
| F-4 | minor | Fixed. "Every entry records version 2.1.224" was false. Restated against a fixed 158-entry boundary: 121 entries carry a version field, all `2.1.224`; 37 carry none. |
| F-5 | minor | Fixed. All counts are now stated against the 158-entry boundary, with a note that the transcript grows while the session runs. The assistant-entry count is corrected from 91 to 74. |
| F-6 | minor | Fixed. Corrected from twelve stream-json events to thirteen. |
| F-7 | minor | Fixed. "Seven files unrelated to the installed Skill payload" was false; two of the seven are payload files. Both are now named, with the note that their installed copies remain pinned to `aacbde44`. |
| F-8 | minor | Fixed. "Payload" is now defined as `SKILL.md`, `README.md`, `docs/`, and `.looppilot/`, with all 54 non-payload files enumerated by tree. |
| F-9 | minor | Fixed. Trace author named in `environment.md`, `trace.md`, and `score.md`, with the self-observation problem and its mitigation stated in one place. |
| F-10 | minor | Fixed. Section 1 retitled to say the commands ran from inside the live Arm A session before the Skill invocation, not before all host activity. |
| F-11 | minor | Fixed. `Skill loading mode` split per arm: observed loading for Arm A, registration only for Arm B. |
| F-12 | minor | Fixed. The 429 incident is now labelled an Execution Infrastructure Incident where it is described, with its probable cause and verification effect stated alongside it. |

One correction was made while fixing F-8 and is recorded here because it was an
error introduced during remediation, not one the reviewer found: an initial
exclusion list named a `distribution/` tree that does not exist at `aacbde44`
and omitted `examples/`. It was caught by checking the commit rather than
trusting the draft, and corrected before commit.

The review was not re-run against the corrected package. Every correction above
is either a factual fix the reviewer specified or a disclosure the reviewer
asked for, and none of them adds a new claim. Standards would plausibly clear on
a re-review, and it would not change this decision, because the protocol
conditions in the section above are independent of packaging.

## Release Candidate Effect

Gate 4 of the Release Candidate checklist requires the reference host to hold an
observed `accepted` or `accepted-with-residuals` Host Acceptance Record at a
commit boundary contained in the release.

**Gate 4 remains UNMET.** No such record exists for Claude Code or for any host.

This decision ticks no gate, creates no candidate version, and authorizes no
tag, release, or deployment.

## Smallest Path to a Real Acceptance Verdict

Not a plan, and not authorized by this document. Recorded so the remaining
distance is explicit rather than rediscovered:

1. Pin one host version and one model, and do not let the CLI update mid-run.
2. Run one Lightweight-shaped and one Full-Loop-shaped fixture from
   [`tests/scenarios.md`](../../../tests/scenarios.md), preserving environment,
   prompt, trace, and score for each.
3. Run at least one fixture that activates the Skill without explicit
   invocation, so dimension 1's activation half has evidence.
4. Have an evaluator who is not the trace author score both traces against the
   rubric, and record the lowest critical score.
5. Write one Host Acceptance Record under `evaluations/` for that exact
   combination, and let its verdict follow the dimension results.

Steps 2 through 4 are the work Phase 13 did not do and did not claim to do.
