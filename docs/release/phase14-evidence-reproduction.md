# Phase 14.5 Evidence Reproduction

How the EVAL-005 redacted transcripts were produced, what the process
guarantees, and what it does not. This document exists so the preservation step
recorded in
[`phase14-evidence-preservation-plan.md`](phase14-evidence-preservation-plan.md)
can be audited without possessing the private inputs.

**This document preserves nothing new, scores nothing, and advances no gate.**
Host Acceptance remains UNVERIFIED, RC Gate 4 remains UNMET, and no protocol
artifact is touched. It records a process that already ran.

- Boundary: HEAD `cf4b3f6`, branch `main`, nothing pushed.
- Subject: [`EVAL-005/evidence/`](../../evaluations/claude-code/EVAL-005/evidence/README.md).

## 1. Decision: Reproduction Tooling Is Intentionally Omitted

The script that produced the EVAL-005 evidence is not moved into the repository.
It remains where it ran, under the gitignored `.tmp/phase14/redact.py`, and is
pinned here by digest only:

```text
redact.py  f17f4fa48a4b21c52d1bf2cc695396de3c836cd09d197e006ccc26dfdf3053cc
```

Three reasons, in order of weight.

**1. The inputs can never be supplied, so the tool can never be run.** Its only
inputs are the two unredacted host transcripts. Those are the private host data
the preservation plan deliberately excludes from the repository, and excluding
them is the point of the redaction — preserving the tool that consumes them does
not change that. A committed program whose inputs no auditor can hold is not
reproducible tooling; it is a specification written in Python. Since it can only
ever function as a specification, section 3 states the specification directly.

**2. Tracking it would weaken the evidence chain in either available form.** The
script that actually produced the committed artifacts does not meet the bar a
tracked evidence tool would have to meet: section 5 records two verified
fail-open behaviours. Committing a corrected version would place under `tools/`
a program that did not generate the committed files, so the digests in
[`evidence/README.md`](../../evaluations/claude-code/EVAL-005/evidence/README.md)
would not follow from it even given the inputs. Committing it verbatim would
ship, as project tooling, code this repository documents as failing that bar.
Neither form strengthens the chain; both invite a reader to trust a program
rather than check an artifact.

**3. Tracking it creates a standing private-data risk.** The script hardcodes
the source filenames and the `.tmp/phase14/evidence/` layout. As tracked
tooling it would read as a sanitiser for host transcripts generally, which it is
not — it is a one-shot transform fitted to two known files. The fail-open
behaviours in section 5 make the failure mode concrete: pointed at a fresh
transcript, it would pass unfamiliar content through unredacted and report
success. The risk is not that the current artifacts are unsafe; it is that a
future contributor could produce unsafe ones and believe the tool had cleared
them.

What is lost by omitting it: nobody can re-execute the transform. That loss is
already unavoidable under reason 1. What is kept: the transform's semantics,
below, stated at a precision that can be checked against the committed files.

## 2. Preservation Principles

The four principles in
[`phase14-evidence-preservation-plan.md`](phase14-evidence-preservation-plan.md)
§1 govern here unchanged — preserving is not accepting, a trace is not a verdict,
loading proof is not compliance, and an absent artifact is never reconstructed.
Reproduction adds two.

5. **Redaction removes; it never rewrites.** A redacted artifact may contain less
   than the original. It may never contain anything the original did not, beyond
   a token that is visibly a token. Positional `<redacted-unrelated-NNN>`
   placeholders qualify: no reader can mistake one for a value. A plausible
   substitute value would not.

6. **A digest is preserved in place of content only when the content is
   independently recoverable.** The injected `SKILL.md` body is replaced by a
   digest because a reader can recompute it from this repository. No other
   content class qualifies, and a digest may never stand in for content that
   exists nowhere else — that would record a claim in place of evidence.

## 3. The Transformation, As Performed

Audited against the committed outputs, not transcribed from the script's own
description. Every count in this section is verified in section 6.

**Inputs.** Two host-written session transcripts, JSONL, UTF-8 with BOM, held
under the gitignored `.tmp/phase14/evidence/`:

```text
agent-a9c71729e35b6ff97.jsonl  bd2e9a2900ee339519df0ad4aeefa5cdbd3ae4ad2a8e4e987b798f560ddbc2f8
agent-a4964684a94e5758e.jsonl  72a57a662573631c4b96e1f6f608131788ca327d325dca39aca8a80e76389e69
```

**Outputs.** `fixture-a.redacted.jsonl` (30 records) and
`implicit-fixture.redacted.jsonl` (29 records), one JSON object per line,
LF-terminated.

**Transformations.** Exactly three, applied per record. Everything else is
copied.

| # | Applies to | Action |
|---|---|---|
| T1 | `attachment.type == "skill_listing"` | Each `- ` entry in `content` whose name is not `loop-pilot` becomes `- <redacted-unrelated-NNN>`, `NNN` being its 1-based position. Lines following a redacted entry, up to the next `- `, are dropped with it. Lines before the first entry are kept. In parallel, each element of `names` other than `loop-pilot` becomes the same positional token |
| T2 | `message.content[]` blocks of `type == "thinking"` | Removed from the list, taking the block's `thinking` and `signature` fields with it |
| T3 | `message.content` strings, or `type == "text"` blocks, longer than 3000 characters | Replaced by a `<skill-body-not-duplicated chars="…" body-sha256="…"/>` descriptor, preceded by the `Base directory for this skill: …` line where one is present |

**Serialisation.** Records are re-emitted with `json.dumps(..., sort_keys=True,
ensure_ascii=False)`, LF newlines, no BOM. Key reordering is why the outputs are
not byte-identical to the inputs and why an auditor cannot diff them directly.

**Determinism.** The transform reads no clock, no random source, and no
environment. An independent re-run on 2026-08-11, two days after the original,
reproduced both outputs byte for byte — the `verify-out` digests in section 6
equal the committed ones.

## 4. Content Classes

**Removed.**

- Third-party Skill names and descriptions — 25 of 26 entries per listing, in
  both `content` and `names`. Verified absent from the outputs at entry level.
- Assistant reasoning — 5 `thinking` blocks per transcript, 10 total, with their
  cryptographic `signature` fields. Private chain-of-thought is not evidence.
- The injected `SKILL.md` body — one block, in Fixture A only, replaced per T3.

**Preserved.**

- Record count, order, and the complete `uuid` / `parentUuid` chain.
- All `timestamp`, `version`, `model`, and `type` fields.
- All `tool_use` and `tool_result` blocks, complete, including command text and
  command output.
- All assistant `text` blocks under the T3 threshold, verbatim.
- The `loop-pilot` listing entry, verbatim, at position 7 of 26 — the entry the
  reachability claim depends on.
- `skillCount: 26`, and `names` array length 26, so the redaction cannot conceal
  how much was redacted.

**Preserved deliberately, though host-identifying.** `cwd`
(`C:\Users\tutic\IdeaProjects\LoopPilot`, carrying the operator's account name),
`sessionId`, `agentId`, `gitBranch`, and the user-scope Skill install path. These
are already stated openly in
[`EVAL-005/environment.md`](../../evaluations/claude-code/EVAL-005/environment.md)
and are load-bearing: `cwd` and `isSidechain` are what establish that the
fixtures ran as separate non-self-observing contexts. They are operator
metadata, not third-party data, and the operator is the repository owner.

**Not preserved and not reconstructed.** The unredacted transcripts, the sandbox
end states, Fixture A's never-written final report, and every category B item in
the preservation plan's disposition table. Their absence is the record.

## 5. Guarantees Checked, and Guarantees Not Held

**Checked, and holding on the committed artifacts.**

- No third-party Skill name survives as a listing entry or `names` element.
- Entry count, array length, and ordering are preserved; `loop-pilot` sits at
  position 7 of 26 in both files.
- No `thinking` block survives; no `thinking` or `signature` key path exists in
  either output.
- No key path present in an output is absent from its input — the transform adds
  no field.
- The `uuid` / `parentUuid` chain is contiguous across all 30 and all 29 records.
- The `SKILL.md` body digest recomputes from `HEAD:SKILL.md` (section 6).
- Output is deterministic across independent runs.

**Not held. These are properties the process lacks, stated because a reader
would otherwise assume them.**

- **It does not fail closed on unfamiliar structure.** A record whose shape the
  transform does not recognise is copied through unchanged, and the run reports
  success. In these two files that is verifiably harmless: the only
  unrecognised attachment is `deferred_tools_delta`, whose `addedNames` are
  first-party host tool names (`WebFetch`, `NotebookEdit`, and six more). That
  is a property of these inputs, not a guarantee of the transform.
- **T3 is a size heuristic, not a content test.** Any text over 3000 characters
  is replaced by a `SKILL.md` descriptor whether or not it is `SKILL.md`. It
  fired exactly once, on the 17128-character injected body; the next-largest
  block in either transcript is 2422 characters, a margin of 578. The
  correctness of the outputs here does not generalise past that margin.
- **The descriptor's `chars` and its digest have different scopes.** `chars`
  counts the full 17128-character block including the `Base directory …`
  preamble; the digest covers the 17054-character normalised body after that
  preamble is stripped. The 74-character difference is preamble and trailing
  whitespace. Recomputing SHA-256 over 17128 characters will not reproduce the
  digest — follow section 6 instead.
- **No signature, no provenance.** The inputs were unsigned, operator-writable,
  and outside version control. The outputs are derived, so they inherit that and
  cannot prove their own source was unaltered. The one claim escaping this is
  the `SKILL.md` digest, recomputable from the repository alone.

## 6. Digest Verification Procedure

### 6.1 From this repository alone

This is the check that needs no private input. It confirms that the body the
host loaded is byte-identical to the repository's `SKILL.md`.

```bash
python - <<'EOF'
import hashlib, json, pathlib, re
text = pathlib.Path("SKILL.md").read_text(encoding="utf-8")
body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)
norm = body.replace("\r\n", "\n").replace("\r", "\n").strip()
print("recomputed:", hashlib.sha256(norm.encode("utf-8")).hexdigest())
p = "evaluations/claude-code/EVAL-005/evidence/fixture-a.redacted.jsonl"
rec = [json.loads(l) for l in pathlib.Path(p).read_text(encoding="utf-8").splitlines() if l.strip()][6]
print("descriptor:", re.search(r'body-sha256="([0-9a-f]{64})"', json.dumps(rec)).group(1))
EOF
```

Both lines must print
`530bbaf7718c4fc7ae54446621a9ab0d67363c8bf9e4c82e1306466aefcb146a`. The steps
are: strip YAML frontmatter, normalise CRLF and CR to LF, strip leading and
trailing whitespace, then SHA-256 of the UTF-8 bytes. `SKILL.md` is blob
`6e0f26a9e948659541f88fc066e4e70dfcb31b0b` and is byte-identical from
`aacbde449a6dbc8723d5c866033ac195017a90e5` through `cf4b3f6`, so the digest
anchors across that range without ambiguity.

### 6.2 Artifact digests

```bash
sha256sum evaluations/claude-code/EVAL-005/evidence/*.jsonl
```

```text
0f3d98c7b30d5e6ea34d55164f9972af01c31cb1cb59e384d11b6b53ee001371  fixture-a.redacted.jsonl
30f77b255ac9b52da1014b11b7f46975892d2ab5e35c20de6337d05919883fd1  implicit-fixture.redacted.jsonl
```

These match the values in `evidence/README.md` and the values produced by the
independent 2026-08-11 re-run. A mismatch means the committed evidence was
edited after preservation, which invalidates it — the files are append-never,
edit-never by design.

### 6.3 Structural invariants, checkable without the originals

```bash
python - <<'EOF'
import json, pathlib
for f, n in [("fixture-a.redacted.jsonl", 30), ("implicit-fixture.redacted.jsonl", 29)]:
    p = pathlib.Path("evaluations/claude-code/EVAL-005/evidence") / f
    r = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    names = r[2]["attachment"]["names"]
    think = sum(1 for x in r if isinstance(x.get("message"), dict)
                and isinstance(x["message"].get("content"), list)
                for b in x["message"]["content"] if b.get("type") == "thinking")
    chain = all(r[i + 1].get("parentUuid") == r[i].get("uuid") for i in range(len(r) - 1))
    print(f, len(r) == n, think == 0, len(names) == 26,
          names.index("loop-pilot") == 6,
          sum(1 for x in names if x.startswith("<redacted-unrelated-")) == 25,
          chain, {x.get("version") for x in r} == {"2.1.224"})
EOF
```

Every field after the filename must print `True`. This detects removal of
records, reappearance of reasoning, and tampering with the listing, none of
which requires the originals.

### 6.4 With the originals, if the operator still holds them

Only the operator can run this. Confirm the inputs still match the digests in
section 3, then re-derive the outputs per section 3 and compare against 6.2. A
divergence means either the originals or the committed copies changed; the
procedure identifies that a divergence exists, and cannot say which side moved.

## 7. Artifact Classification Rules

The rules the preservation plan applied, stated so a later artifact can be
classified the same way.

| Class | Rule | Disposition |
|---|---|---|
| **A — preservable** | A primary record exists, was written by a party other than the trace author, and can be redacted without destroying the claim it supports | Preserve, redacted per section 3, digests recorded, never edited afterwards |
| **B — not preservable** | No primary record exists, or the artifact has no provenance linking it to a specific execution | Leave absent. Writing it would be reconstruction, which principle 4 forbids |
| **C — future verification** | The claim needs a judgement, not an artifact — a rubric applied by an independent reviewer | Record as unverified. No accumulation of class A material converts a C item |

Three subsidiary rules govern redaction within class A:

- **Redact identity, preserve structure.** Remove what a name reveals; keep
  count, order, and position, because those are usually what the claim rests on.
- **Preserve what the claim depends on, verbatim.** If redacting an item would
  destroy the evidence, the item stays. `loop-pilot` at position 7 is the case
  in point.
- **Never redact toward a conclusion.** Redaction is applied by class, before
  anyone reads the result. Removing an item because of what it shows is
  falsification, not redaction.

Infrastructure evidence — the 429 termination, the 2.1.226 probe — is class A
but never merges into a behavioural evidence set, and never explains away a
missing artifact as though the artifact had existed.

## 8. What This Document Does Not Establish

It does not make EVAL-005 reproducible: the inputs are gone from any third
party's reach by design, and section 1 accepts that rather than working around
it. It does not certify that the originals were genuine, that the host obeyed
the protocol, or that any dimension passed. It records that a documented
transform, with two known fail-open behaviours that did not fire on these
inputs, produced two files whose structural invariants and one recomputable
digest still check out.

The remaining acceptance path is unchanged: two completed fixture runs, an
independent reviewer, and a Host Acceptance Record — none of which this document
advances.
