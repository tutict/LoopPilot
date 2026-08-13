# EVAL-005 — Phase 14 Fixture Evidence

Historical fixture evidence for Claude Code 2.1.224 / claude-opus-5, preserved so
that a future independent reviewer inherits primary sources rather than prose.

## This package is historical fixture evidence

It preserves what two fixture contexts did on 2026-08-09. It exists to make
transient host-cache transcripts durable and auditable. Preserving them changed
their durability, not their status: evidence that proved nothing before it was
packaged proves exactly as much afterwards.

## This package is not an acceptance record

It carries no verdict, no score, and no dimension result. It is not a Host
Acceptance Record and must never be cited as one. Under
[`docs/cross-host-acceptance.md`](../../../docs/cross-host-acceptance.md) a host
verdict lives in a Host Acceptance Record under `evaluations/`, and each fact has
exactly one authoritative source. **No Host Acceptance Record exists for Claude
Code 2.1.224.** One was not written here, because reviewer independence does not
exist and the required fields cannot be populated.

There is deliberately **no `score.md`** in this package. The rubric in
[`tests/evaluation-rubric.md`](../../../tests/evaluation-rubric.md) scores
behaviour against dimensions that no one has judged. Inventing numbers to fill
the file would be a worse violation of the evidence rules than recording their
absence.

## This package does not satisfy RC Gate 4

RC Gate 4 requires the reference host to hold an observed `accepted` or
`accepted-with-residuals` Host Acceptance Record. **That gate remains UNMET**, and
nothing here advances it. What the package establishes is narrower than it may
appear at a glance:

| Claim | Status |
|---|---|
| The host advertised the Skill to the context | Established |
| The host loaded `SKILL.md` byte-for-byte | Established, digest-verifiable from this repository |
| The host complied with the protocol | **Not established.** Loading is not compliance |
| The Lightweight fixture is accepted | **Not established.** Truncated by rate limit, never scored |
| Full Loop behaviour | **Not established.** No Full Loop fixture was executed |
| Independent review | **Not established.** No independent reviewer saw either run |

## Missing artifacts must not be reconstructed

Three artifacts a reader may expect are absent, and their absence is deliberate:

- **Fixture A's final report.** The run was terminated by a non-transient HTTP
  429 after its verification step and before its report. Writing one now from the
  transcript would be the trace author's narration wearing the fixture's voice.
- **`score.md`.** No rubric was applied and no reviewer exists.
- **A Host Acceptance Record for 2.1.224.** See above.

The governing rule, from the Phase 14.2 preservation plan: *where a primary
record exists, summarising it is legitimate because the summary can be checked
against the primary; where no primary record exists, writing the missing artifact
would manufacture evidence rather than preserve it.* Only a new execution can
produce what is missing here.

## Contents

| File | What it holds |
|---|---|
| [`environment.md`](environment.md) | Observed host, version, model, loading mode, and constraints, read from transcript fields |
| [`prompt.md`](prompt.md) | Both fixture prompts verbatim, each attested by two independent sources |
| [`trace.md`](trace.md) | Preserved excerpts anchored to record positions, plus the redaction method and original digests |
| [`evidence-index.md`](evidence-index.md) | Every artifact, its verification type, and its limitations |
| [`evidence/`](evidence/README.md) | The redacted transcripts themselves |

## Relationship to other records

- [`EVAL-004`](../EVAL-004/environment.md) established loading at the same host
  version, but its Arm A was **self-observing**: the observing session was itself
  the subject. Neither fixture here is self-observing. EVAL-005 does not revise
  EVAL-004; it is a separate run.
- The committed records for
  [2.1.220](../host-acceptance-record-claude-code-2.1.220.md) and
  `2.1.221` cover different combinations. **Nothing here generalises to another
  host version, model, or loading mode**, and nothing here revises them.
