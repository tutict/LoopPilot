# EVAL-005 Preserved Evidence

Two redacted host transcripts. Each is a primary source behind a claim in
[`../trace.md`](../trace.md), so a later reader does not have to trust prose.

| File | Records | What it is |
|---|---|---|
| `fixture-a.redacted.jsonl` | 30 | Fixture A: explicit `Skill` invocation, Lightweight-shaped task, terminated by HTTP 429 before its final report |
| `implicit-fixture.redacted.jsonl` | 29 | Implicit fixture: no invocation instruction, ran to completion, zero `Skill` calls |

## Redaction

The host's `skill_listing` attachment enumerates 26 Skills registered on the
operator's machine. The 25 unrelated to LoopPilot are replaced with positional
`<redacted-unrelated-NNN>` tokens in both the `content` text and the `names`
array, and their multi-line descriptions are dropped with them. Entry count,
array length, and ordering are preserved exactly, and the `loop-pilot` entry is
preserved verbatim at position 7 of 26 — that entry is the reachability evidence
and redacting it would destroy the claim it supports.

Two further exclusions, following
[`../../EVAL-004/evidence/README.md`](../../EVAL-004/evidence/README.md):

- **Assistant reasoning is not copied.** Five `thinking` blocks per transcript
  are removed. Private chain-of-thought is not evidence and is not recorded.
- **The injected `SKILL.md` body is not duplicated.** Record `[6]` of Fixture A
  carried 17128 characters of `SKILL.md`. It is replaced by a
  `<skill-body-not-duplicated .../>` descriptor holding the character count and
  the body SHA-256, so a reader recomputes the expected value from the
  repository's own [`SKILL.md`](../../../../SKILL.md) instead of trusting a copy.

Every other field of every record is untouched, including the `uuid` /
`parentUuid` chains and all timestamps. Records are re-serialised with sorted
keys, so these files are **not** byte-identical to the originals.

## Digests

SHA-256 of the unredacted originals, recorded so the redaction can be audited
against them while they remain under the gitignored `.tmp/phase14/evidence/`
path:

```text
agent-a9c71729e35b6ff97.jsonl  bd2e9a2900ee339519df0ad4aeefa5cdbd3ae4ad2a8e4e987b798f560ddbc2f8
agent-a4964684a94e5758e.jsonl  72a57a662573631c4b96e1f6f608131788ca327d325dca39aca8a80e76389e69
```

SHA-256 of the redacted copies in this directory, as generated:

```text
fixture-a.redacted.jsonl         0f3d98c7b30d5e6ea34d55164f9972af01c31cb1cb59e384d11b6b53ee001371
implicit-fixture.redacted.jsonl  30f77b255ac9b52da1014b11b7f46975892d2ab5e35c20de6337d05919883fd1
```

## What these artifacts cannot establish

The source transcripts were written by the host into a cache outside version
control. They are unsigned and operator-writable. These redacted copies are
derived, so they inherit that limitation and cannot prove their own source was
unaltered. The one claim that escapes it is the `SKILL.md` body digest, which is
recomputable from this repository alone — the transcript is only what ties that
digest to a host event.
