# Phase 14.5 Evidence Reproduction Report

Closure report for Phase 14.5. The phase audited how the EVAL-005 redacted
transcripts were produced and decided whether the redaction tooling should enter
the repository.

- Boundary: HEAD `cf4b3f6`, branch `main`, 10 ahead of `origin/main`, nothing
  pushed, nothing committed by this phase.
- Companion: [`phase14-evidence-reproduction.md`](phase14-evidence-reproduction.md).

## Scope

In scope: auditing the transformation that produced
[`EVAL-005/evidence/`](../../evaluations/claude-code/EVAL-005/evidence/README.md),
deciding the disposition of the untracked `.tmp/phase14/redact.py`, and
recording the preservation methodology and its verification procedure.

Out of scope, and untouched: `SKILL.md` and every protocol semantic; roles,
modes, ledgers, lifecycle states, checkpoints, validators, and acceptance logic;
RC preparation; Host Acceptance records. No evidence was reconstructed, no
transcript was added, and no existing artifact was edited.

## Decision

**Option B — the redaction tooling is not preserved. The methodology is.**

The reasoning is recorded in full in
[`phase14-evidence-reproduction.md`](phase14-evidence-reproduction.md) §1;
in summary:

1. **Reproducibility is unattainable either way.** The transform's only inputs
   are the two unredacted host transcripts, which are the private data the
   redaction exists to exclude. A tracked program no auditor can feed is a
   specification in Python, so the specification is stated directly instead.
2. **Evidence integrity argues against tracking it.** The script that produced
   the committed artifacts has two verified fail-open behaviours. A corrected
   version would not be the program that generated the recorded digests; the
   verbatim version would ship code documented as failing the bar. Neither
   strengthens the chain.
3. **Tracking it would carry private-data risk forward.** It hardcodes the
   `.tmp/phase14/evidence/` layout and would read as a general transcript
   sanitiser, which it is not. Pointed at an unfamiliar transcript it passes
   unrecognised content through and reports success.

The script is pinned by digest — `f17f4fa48a4b21c52d1bf2cc695396de3c836cd09d197e006ccc26dfdf3053cc`
— so the operator's copy remains identifiable, and `tools/evidence/redaction/`
is deliberately not created.

### Audit findings

The transform was audited against the committed outputs rather than read from
its own docstring. It applies exactly three transformations — positional
redaction of 25 of 26 Skill listing entries, removal of 5 `thinking` blocks per
transcript, and replacement of the injected `SKILL.md` body with a digest
descriptor — and copies everything else, including the complete `uuid` chain,
all timestamps, and all tool calls and results.

Two guarantees a reader might assume are **not** held, both verified rather than
suspected:

- The transform does not fail closed. `deferred_tools_delta` attachments passed
  through unredacted; they proved to contain first-party host tool names only, so
  the committed artifacts are unaffected, but that is a property of these inputs.
- The body-replacement rule is a 3000-character size threshold, not a content
  test. It fired once, on the 17128-character body, with the next-largest block
  at 2422 characters.

One precision defect is recorded: the descriptor's `chars="17128"` counts the
full block, while its digest covers the 17054-character normalised body after
the preamble is stripped. The verification procedure documents the correct
scope. No artifact was edited to correct this — editing preserved evidence would
break the digests that make it evidence.

## Evidence Boundary

Nothing crossed the boundary in this phase. No transcript, redacted or
otherwise, was added; no private host data entered the repository; no artifact
under `evaluations/` was modified.

The unredacted originals remain outside version control under `.tmp/phase14/`
and still match their recorded digests. The two committed redacted copies remain
byte-identical to their preserved state. Everything class B in the preservation
plan — the sandbox end states, the EVAL-002/003 traces and scores, Fixture A's
final report — remains absent and unreconstructed.

Host-identifying metadata retained inside the committed evidence (`cwd`,
`sessionId`, `agentId`, `gitBranch`) is operator metadata already disclosed in
`EVAL-005/environment.md`, and is load-bearing for the non-self-observation
claim. It is documented, not newly introduced.

## Files Changed

Two files, both new, both documentation:

| File | Status | Why it belongs to Phase 14.5 |
|---|---|---|
| `docs/release/phase14-evidence-reproduction.md` | new | The task 4 deliverable: why tooling is omitted, the preservation principles, the audited transformation, the digest verification procedure, and the artifact classification rules |
| `docs/release/phase14.5-evidence-reproduction-report.md` | new | This report |

No existing file was modified. No file was deleted. No file entered
`tools/`, `evaluations/`, `scripts/`, or `tests/`.

**Not part of Phase 14.5.** The working tree also carries pre-existing
uncommitted work that this phase neither created nor touched, and that must not
be swept into a Phase 14.5 commit:

- Phase 12 validator work — `scripts/validate.py`,
  `scripts/cross_host_acceptance_validation.py`, `tests/test_validate.py`,
  `tests/test_cross_host_acceptance.py`, `CHANGELOG.md`, `docs/validation.md`,
  `docs/release/v1.0-rc-checklist.md`.
- Phase 14 preservation output — `evaluations/claude-code/EVAL-005/` and the
  three `docs/release/phase14-*.md` analysis, inventory, and plan documents.

## Validation Results

Run under CPython 3.13.13.

```text
$ python scripts/validate.py
Static validation passed                          exit 0

$ git diff --check
(no output)                                       exit 0
```

Preservation verification, per
[`phase14-evidence-reproduction.md`](phase14-evidence-reproduction.md) §6:

| Check | Result |
|---|---|
| §6.1 `SKILL.md` body digest, recomputed from working tree, from `HEAD:SKILL.md`, and read from the descriptor | All three agree: `530bbaf7…46a` |
| §6.2 Committed artifact digests | Match `evidence/README.md` and the independent 2026-08-11 re-run: `0f3d98c7…371`, `30f77b25…fd1` |
| §6.3 Structural invariants | 30 and 29 records; 0 `thinking` blocks; 26 names with 25 positional tokens and `loop-pilot` at position 7; contiguous `uuid` chain; `version` `2.1.224` throughout |
| §6.4 Originals still match recorded digests | `bd2e9a29…2f8` and `72a57a66…e69` unchanged |
| Determinism | An independent re-run reproduced both outputs byte for byte |
| Third-party name leakage | None: no redacted Skill name survives as a listing entry or `names` element in either file |

No test was modified. The existing validator verifies the new documents under
its Markdown rules — newline termination, whitespace, fence balance, and
relative link resolution — so no new check was required.

## Remaining Limitations

- **EVAL-005 is not reproducible by a third party, and this phase does not make
  it so.** The inputs are private by design. What an auditor gains is a
  checkable specification and three verification procedures, not the ability to
  re-derive the artifacts.
- **The historical transform's fail-open behaviours are recorded, not fixed.**
  Fixing them would require re-running a corrected transform, which would change
  the committed digests and destroy the artifacts' preserved state.
- **The redaction cannot prove its own inputs were genuine.** The originals were
  unsigned, operator-writable, and outside version control. The `SKILL.md`
  digest is the only claim in the package that escapes this.
- **Nothing here is behavioural evidence.** The audit establishes that a
  documented transform produced the committed files. It says nothing about
  whether the host obeyed the protocol.
- **The acceptance path is unchanged.** Two completed fixture runs, an
  independent reviewer, and a Host Acceptance Record remain outstanding, in that
  dependency order.

## Status After Phase 14.5

| Item | State |
|---|---|
| Host Acceptance | **UNVERIFIED** |
| RC Gate 4 | **UNMET** |
| RC preparation | Not started, not attempted |
| Release tag | None |
| Protocol changes | None. `SKILL.md` untouched |
| Host Acceptance Records | None created, none upgraded |
| Commits by this phase | None. Awaiting review |
