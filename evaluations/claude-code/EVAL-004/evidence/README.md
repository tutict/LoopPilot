# EVAL-004 Preserved Evidence

These files exist so a later reader does not have to trust prose. Each is a
committed artifact behind a claim in [`../trace.md`](../trace.md).

## Files

| File | What it is |
|---|---|
| `arm-a-skill-invocation.json` | Sanitised excerpt of the Arm A host session transcript covering the Skill invocation. |
| `p1-discovery.redacted.jsonl` | Arm B1 discovery run, full stream-json output, 13 events. |
| `p2-loading.redacted.jsonl` | Arm B2 loading run, first attempt, full stream-json output, 13 events. |
| `p3-loading-retry.redacted.jsonl` | Arm B2 loading run, retry at a materially later time, full stream-json output, 13 events. |

## Redaction

The Arm B `system/init` events enumerate every Skill, slash command, and agent
registered on the operator's machine. Those names are unrelated third-party
tooling and are not evidence for anything claimed here, so each entry other than
`loop-pilot` is replaced with a positional `<redacted-unrelated-NNN>` token.
Array lengths, ordering, and the `loop-pilot` entries are preserved exactly,
which is what the discovery claim depends on. Every other field of every event
is untouched. The events are re-serialised with sorted keys, so the redacted
files are not byte-identical to the originals.

SHA-256 of the unredacted originals, recorded so the redaction can be audited
against them if they are still present under the gitignored `.tmp/` path:

```text
p1-discovery.jsonl      f6f870cb403c850e1f9577989233ba9f4509cd36b0f1351866719e63ac6657d0
p2-loading.jsonl        7b3b448e38d952143542f86ef178745d47e1f74735ea60282a2ac561f87ecb15
p3-loading-retry.jsonl  5f2764de905b30309421e9aa410fa0563725663eb284c61e91cc2767c97fe06e
```

## Arm A excerpt scope

`arm-a-skill-invocation.json` carries transcript entries 149, 150, and 151: the
`Skill` tool call, its tool result, and the envelope of the host-injected
content. Two deliberate exclusions:

- **Assistant reasoning is not copied.** Evaluators must not record private
  chain-of-thought, so only the observable tool envelope is preserved.
- **Entry 151's body is not duplicated.** That body is `SKILL.md`. It is
  described by character count and SHA-256 instead. A reader recomputes the
  expected value from the repository's own [`SKILL.md`](../../../../SKILL.md),
  which is the point: the digest is independently derivable, and the transcript
  is what ties it to a host event.

The excerpt preserves the `uuid` and `parentUuid` chain linking 149 to 150 to
151, and the `isMeta` flag on 151 marking it as host-injected rather than
user-typed.

## What these artifacts cannot establish

The Arm A source transcript lives in a host cache outside this repository, is
operator-writable, and is unsigned. This excerpt is a derived copy, so it
inherits that limitation and cannot prove the source was unaltered. The
unredacted Arm B originals sit under gitignored `.tmp/` and are transient.
