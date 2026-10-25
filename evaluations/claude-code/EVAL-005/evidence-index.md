# Evidence Index

Every artifact in this package, what verifies it, and what it cannot support.
Evidence IDs are labels for reference within EVAL-005; they confer no authority
and are not a protocol identifier scheme.

| Evidence ID | Artifact | Source | Verification type | Limitations |
|---|---|---|---|---|
| E5-1 | `evidence/fixture-a.redacted.jsonl` — 30 records, Fixture A | Host-written session transcript, sub-context `a9c71729e35b6ff97`, redacted per `trace.md` | Host-emitted record. Original SHA-256 `bd2e9a29…2f8` recorded; redacted copy is not byte-identical by design | Source is unsigned, operator-writable, outside version control. The copy cannot prove the original was unaltered |
| E5-2 | `evidence/implicit-fixture.redacted.jsonl` — 29 records, implicit fixture | Host-written session transcript, sub-context `a4964684a94e5758e`, redacted per `trace.md` | Host-emitted record. Original SHA-256 `72a57a66…e69` recorded | Same source limitation. Records a non-event (no invocation), which no digest can strengthen |
| E5-3 | Skill listing attachment, record `[2]` of E5-1 and E5-2 | Host, delivered before the first assistant turn | Host-emitted. `skillCount: 26`, `loop-pilot` preserved verbatim at position 7 | Proves the Skill was **advertised**. Advertisement is not loading and not activation |
| E5-4 | `Skill` invocation: `tool_use` `toolu_017FftxFfF14Jarq7bi2EaaP` and its result, records `[4]`–`[5]` of E5-1 | Host tool envelope | Host-emitted; the tool result `Launching skill: loop-pilot` is the host's own acknowledgement | Proves the call was made and accepted. Says nothing about what followed |
| E5-5 | Injected `SKILL.md` body descriptor, record `[6]` of E5-1 | Host-injected content, 17128 chars | **Digest, independently recomputable.** Normalised SHA-256 `530bbaf7…46a` matches installed copy and `HEAD:SKILL.md` | Proves byte identity of what was loaded. Loading is not protocol compliance |
| E5-6 | Mode declaration, record `[23]` of E5-1 | Executing context's own output | Preserved verbatim, unscored | A self-report. Its correctness is a rubric judgement no one here has made |
| E5-7 | Task outcome, records `[20]`–`[28]` of E5-1 | Command output inside the transcript | Observable command results: `EXIT=1` before, `Ran 9 tests` / `OK` / `EXIT=0` after | Shows the task succeeded. Task success is not protocol conformance |
| E5-8 | Absence of any `Skill` call across all 29 records of E5-2 | Structural property of the transcript | Verifiable by enumeration: tool calls are `Read`×2, `Bash`×4, `Edit`×2 | An observation, deliberately unscored. Not a dimension result and not a failure verdict |
| E5-9 | Termination record `[29]` of E5-1 | Host error envelope, `model: "<synthetic>"` | Host-emitted: `apiErrorStatus: 429`, `error: "rate_limit"`, `apiErrorIsTransient: false` | Infrastructure evidence only. Never convertible into host behaviour, and never an excuse for a missing artifact |
| E5-10 | `prompt.md` — both fixture prompts | Pre-run files under `.tmp/phase14/`, and record `[0]` of each transcript | **Doubly attested**: the two sources agree byte for byte | Records what was asked, not what was understood |
| E5-11 | `environment.md` — host, version, model, loading mode | Read from transcript fields, not declared from memory | `version: 2.1.224` on 30/30 and 29/29 records; `model: claude-opus-5` on all real assistant records | Scoped to exactly this combination; never generalises |

## Verification Type Legend

- **Host-emitted record** — written by the host, not by the executing context or
  the trace author. The strongest class present.
- **Digest, independently recomputable** — checkable against this repository
  alone, without trusting any transcript.
- **Self-report** — the executing context's own words. Preserved because it was
  asked for; carries no weight beyond being what was said.
- **Structural property** — verifiable by enumerating the transcript, not by
  reading prose.

## Coverage Against the Acceptance Dimensions

| Dimension | Status in this package |
|---|---|
| 1. Skill loading and activation | **Loading half only**, by E5-3/E5-4/E5-5. The activation half is not established: activation was explicit in Fixture A, and E5-8 records non-activation without judging it |
| 2–8 | `not-evaluated`. No rubric was applied and no trace was scored |

No dimension is `pass`. No dimension is `fail`. A dimension without preserved
evidence is `not-evaluated`, and absence of an observed failure is not a pass.
