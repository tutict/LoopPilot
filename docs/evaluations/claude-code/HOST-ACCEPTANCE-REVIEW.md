# Host Acceptance Review: Claude Code

- Package under review: `evaluations/claude-code/EVAL-004/` (`environment.md`, `prompt.md`, `trace.md`)
- Subject question: does the Claude Code host actually load the `loop-pilot` Skill
- Reviewer: independent AI reviewer, instantiated by the same operator (see "Limits of This Review")
- Review date: 2026-08-09
- Repository boundary at review time: `b482c9c990b9912d99230460bcd7540b64fd74fa`, working tree dirty
- Reference rules applied: `docs/cross-host-acceptance.md`, `evaluations/README.md`, `evaluations/templates/*.md`, `tests/evaluation-rubric.md`, `tests/scenarios.md`

## Verdict

- Spec: PASS
- Standards: FAIL
- Evidence: PASS-WITH-FINDINGS

This review judges an evidence package. It does not issue an acceptance verdict,
does not score a rubric, and does not authorize any record or Release Candidate
gate. No Finding below is a Finding against the frozen v1 protocol; every one of
them is against the packaging or the method of this evaluation, so none of them
feeds Release Candidate condition 6.

## Spec: PASS

The package sets out to show installation integrity, Skill discovery, and Skill
loading. For the one combination where a host turn actually occurred, it does
show loading, and I reproduced every load-bearing number myself.

What is established:

- Installation integrity. The installed tree at `C:\Users\tutic\.claude\skills\loop-pilot`
  is 60 files, every one of which hashes to the blob of the same path at commit
  `aacbde449a6dbc8723d5c866033ac195017a90e5`, and the installed `SKILL.md` is
  byte-identical to the repository `SKILL.md`. Independently confirmed.
- Discovery, host `2.1.226`, model `claude-fable-5[1m]`, headless. The
  `system/init` event lists `loop-pilot` among 42 registered skills and 68 slash
  commands. That is name-level registration and nothing more, which is exactly
  how the package uses it.
- Loading, host `2.1.224`, model `claude-opus-5`, user-scope, explicit `Skill`
  tool invocation. Transcript entry 149 is a `tool_use` for `Skill` with input
  `{"skill": "loop-pilot"}`; entry 150 is its `tool_result` with the text
  `Launching skill: loop-pilot`; entry 151 is a host-injected `isMeta` user-role
  turn of 17128 characters whose body, after the normalization the trace
  documents, is byte-identical to the installed `SKILL.md` body. Independently
  confirmed, including both SHA-256 values.

Against the acceptance criteria, the right criterion is dimension 1 of
`docs/cross-host-acceptance.md`: "the host loads `SKILL.md` in the declared mode
and activates on an in-scope task without fabricating a trigger." Only the first
clause is supported. Implicit activation on an in-scope task was never exercised,
which `environment.md` discloses. A later record may therefore read this package
as support for dimension 1 `partial` at most, never `pass`, and only for
`Claude Code 2.1.224` + `claude-opus-5` + user-scope explicit invocation.

What is claimed is matched by what was observed. The package makes no verdict
claim, no compatibility claim, and no generalization. It explicitly states that
Arm A "does not establish that the answer content could only have come from the
Skill tool" and that no behavioral consequence of loading was observed. Both
statements are true, and the second is the honest thing to say.

The omission that matters is method, not honesty: the only arm designed to prove
loading independently of the observing session (Arm B2) was attempted once,
failed on infrastructure, and was never retried, even though the package itself
records a probable self-inflicted cause. See Finding F-3. Because the package
discloses the resulting gap rather than papering over it, this reduces the
strength of the conclusion without invalidating it.

## Standards: FAIL

The failure is narrow and cheaply remediable, and it is the only reason this axis
is not a pass.

`docs/cross-host-acceptance.md`, Evidence Requirements: "Every acceptance run MUST
record the environment, prompt, trace, and score templates, and MUST score the
trace with the shared rubric." `evaluations/README.md`: a run whose reviewer
decision is missing "is an incomplete evaluation, not a weaker result. Report it
as incomplete rather than scoring around the gap."

EVAL-004 contains `environment.md`, `prompt.md`, and `trace.md`. There is no
`score.md`, no rubric score, no `Reviewer decision`, no named `Reviewer`, and no
named trace author anywhere in the package. The package also never declares
itself an incomplete evaluation. `trace.md` section 7 does record "Any
rubric-scored behavioral trace. Unavailable: no behavioral fixture was run",
which is the correct disclosure of the underlying fact, but it is not the
required record. The public validator does not check this — `docs/validation.md`
scopes it to Host Acceptance Record structure only — so it falls to the reviewer,
and I will not pass it.

I note in mitigation that the score template's dimensions are behavioral
(`Goal fidelity`, `Plan quality`, and so on) and are genuinely not scoreable from
an installation and loading probe. Inventing numbers would be a worse violation
than omitting them. The correct resolution is a `score.md` that records
`Observed outcome`, `Reviewer decision: not-reviewed`, an explicit statement that
no behavioral fixture was run and the 0-to-3 dimensions are therefore not
applicable, and the unverified limitations — not a fabricated score sheet.

Everything else on this axis is strong, and some of it is better than the
repository requires:

- Scope discipline under the v1 feature freeze: the package adds no role, mode,
  Ledger, Barrier, or acceptance layer, proposes no protocol change, and reads
  as pure observation.
- Observation separated from interpretation: content is marked as transcribed,
  a dedicated "Events marked unavailable" section exists, and interpretation is
  confined to a small number of clearly signposted sentences.
- Safety and authority: read-only inspection, bounded spend caps of USD 0.25 and
  USD 0.50, `--no-session-persistence`, an empty working directory for the
  subprocess arms, and an explicit statement that no commit, push, publish, or
  deploy authority was exercised. Nothing in the package contradicts that, and
  the transcript shows only read-shaped commands against the host artifacts.
- No private chain-of-thought is requested or recorded.
- Combination scoping: handled well. See question 2 below.
- Scenario ID: a named fixture, `host-skill-loading-probe`. Permitted by
  `docs/cross-host-acceptance.md`, and the claim that no numbered scenario in
  `tests/scenarios.md` covers a host installation and Skill-loading probe is
  correct — all 301 numbered scenarios are behavioral prompt shapes.

## Evidence: PASS-WITH-FINDINGS

Nothing in the package is fabricated. Every load-bearing digest, length, count,
and field I could re-derive reproduced exactly, including four SHA-256 values, a
60-file blob comparison, a 14-of-14 link resolution, and the full field set of
both Arm B `system/init` events. The observed / unavailable / inferred separation
is good, and the single most contaminating fact — that the observing session had
already read `SKILL.md` before invoking the Skill — is volunteered by the package
rather than discovered by me. I verified that disclosure is true: the session
issued `Read` on the repository `SKILL.md` at transcript line 84, and the body
text appears at lines 85 and 89, well before the injection at line 151.

The axis does not reach a clean PASS for two reasons. First, none of the decisive
raw artifacts is preserved in version control (F-2): the Arm A transcript lives
in a host cache directory outside the repository, and the Arm B outputs live
under gitignored `.tmp/`. I could check them only because I am running on the
operator's machine; a future reader with the repository alone can verify exactly
one thing, the normalized body digest, and must take everything else on trust.
`tests/scenarios.md` scenario 292 encodes the project's own position on
unpreserved evidence. Second, four small factual statements do not survive
re-checking (F-4 through F-7) and one key term is undefined (F-8). None of them
changes the conclusion; two of them cut against the author's own case rather than
for it, which is itself a signal of good faith.

## The Five Required Questions

### 1. Does the package prove loading, or only discovery?

It proves loading, and it keeps the two apart correctly.

Discovery evidence and loading evidence are structurally different in this
package and are never substituted for each other. The discovery evidence is the
`skills` array in Arm B1's `system/init` event: the host knows a Skill named
`loop-pilot` exists. That array contains names, not bodies, and the package never
treats it as more.

The loading evidence is the injection at Arm A entry 151: a host-authored,
`isMeta`-flagged user-role turn carrying 17128 characters that begin
`Base directory for this skill: C:\Users\tutic\.claude\skills\loop-pilot` and
continue with the complete `SKILL.md` body. I recomputed the entry's SHA-256 as
`73bf663576e892ebbe5aba04c70066fc7d6101a0a2a2d38c256d0e53187241af` and, after
stripping the prepended base-directory line, normalizing line endings and
trimming, `530bbaf7718c4fc7ae54446621a9ab0d67363c8bf9e4c82e1306466aefcb146a` at
length 17054 — identical to the value I derived independently from the repository
`SKILL.md` by stripping its 592-character frontmatter. Body-level content entered
the session; a name did not.

The precise limit, which the package states and I endorse: what is proven is that
the host constructed and recorded the Skill body as a turn in the session's
message stream. It is not proven that the model consumed the bytes or changed
behavior because of them, because no task was posed after the invocation and no
behavioral consequence was observed. `trace.md` section 6 says exactly this. So
the claim that survives is "the host injects the Skill body on explicit `Skill`
invocation in this combination", not "the host's model demonstrably operated
under LoopPilot".

### 2. Are the two arms kept separate correctly?

Yes, and this is the strongest part of the package.

The arms differ in host version (`2.1.224` versus `2.1.226`), model
(`claude-opus-5` versus `claude-fable-5[1m]`), and surface (live interactive
session versus headless subprocess). Each fact is sourced from the artifact
belonging to its own arm: Arm A's version from the `version` field of its own
transcript entries, Arm B's from the `claude_code_version` field of its own
`system/init`. `environment.md` states outright that no observation from one arm
was carried to the other, and I found no place where it was.

The package also catches the trap that would have caused the error. It discloses
that the Arm A session began under `2.1.224` while the on-disk binary already
reported `2.1.226`, that the binary changed during the session's lifetime, and
that the session was not restarted. Without that disclosure, a reader would
naturally attach the `claude --version` output in `trace.md` section 1 to Arm A
and record the loading result against the wrong version. The package does not
make that mistake, and it makes the mistake impossible for a careful reader to
make. That behavior matches `tests/scenarios.md` scenarios 290 and 291.

One nit rather than a defect: `environment.md` states "Skill loading mode" as a
single fact for the whole evaluation, though Arm B never loaded anything and only
ever established registration. Splitting that bullet per arm would remove the
last place where a hurried reader could over-read the loading claim (F-11).

### 3. Is the self-observation problem in Arm A disclosed and mitigated?

Disclosed in substance, mitigated well enough that it does not undermine the
claim, but not eliminated and not fully named.

Disclosure: `prompt.md` records that the operating session "issued no
natural-language prompt to itself; it called the host's `Skill` tool directly",
and that the session had already read `SKILL.md` before the invocation, so Arm A
"does not establish that the answer content could only have come from the Skill
tool". `environment.md` records that Arm B ran as a nested subprocess launched
from inside the live Arm A session. A reader can assemble the fact that the
evaluator and the subject were the same session, though the package never says
so in one sentence and never names a trace author (F-9).

Mitigation, which is real and which I tested: the decisive artifact is not the
agent's narration but the host's own transcript, and the expected value of the
injected content is derivable from the repository alone. That combination means
the author could not have produced a passing result by writing prose. I went
further and checked the artifact for tampering signals. The `uuid`/`parentUuid`
chain across entries 148 to 152 is intact and coherent; entry 151 carries
`isMeta: true`; the millisecond timestamps interleave in an order consistent with
host generation and inconsistent with hand editing, including the small oddity
that entry 151 (`.125Z`) precedes entry 150 (`.126Z`), which the package
transcribes faithfully rather than tidying up; the marker string
`Base directory for this skill` appears nowhere in the transcript before line
151; and every in-session tool call touching that `.jsonl` path was a read. I
found no evidence of fabrication.

What remains, and what a record must carry forward: no independent party observed
the run, the one arm designed to remove the self-observation problem never
produced a model turn, and the package names no trace author and no reviewer. So
the correct characterization is "self-observed, corroborated by a host-authored
artifact and a repository-derivable digest", not "independently observed".

### 4. Are the HTTP 429 failures classified honestly and attributed correctly?

Honestly classified, correctly attributed, and correctly kept out of the product
column.

The package records ten `system/api_retry` events per run with
`"error_status":429` and `"error":"rate_limit"`, a `<synthetic>` assistant
message reading `API Error: Request rejected (429) · Service Unavailable`, a
result event with `is_error` true and `total_cost_usd` 0, and then moves every
dependent claim into "Events marked unavailable". I confirmed all of these fields
against the raw stream-json files. At no point is the failure described as a
LoopPilot defect, a protocol defect, or a host incompatibility, and no dimension
is scored around it. That is exactly what `tests/evaluation-rubric.md` requires
of Infrastructure-incident classification, whose 0-level is precisely turning a
429 into a Product Finding.

Two gaps, neither of them dishonesty. The package never applies the project's own
category name, Execution Infrastructure Incident, to the event (F-12). More
substantively, it records the probable cause in `environment.md` — Arm B ran as a
nested subprocess of the live Arm A session, so "both arms drew on the same
account concurrently" — but never connects that fact to the 429s it caused, and
never states that no retry was attempted (F-3). Both raw output files exist, both
timestamped minutes apart, and there is no third attempt. Since a retry after the
interactive session went idle might have produced the decisive result, the
package should either run it or say plainly that it chose not to.

### 5. Does anything overclaim relative to what a reader can verify?

The conclusion does not overclaim. Five statements of supporting detail do.

- "Every entry in this transcript, including these three, records `version`
  `2.1.224`" is false as written. 59 of the 272 entries carry no `version` field
  at all — types `mode`, `permission-mode`, `last-prompt`, `file-history-snapshot`,
  `file-history-delta`. The true and equally useful claim is that all 200
  `assistant` and `user` message entries record `2.1.224` and none records any
  other version (F-4).
- "All 91 assistant entries" and "Before the invocation the transcript held 142
  entries. After it, 158" describe different snapshots of a file that was still
  growing. At line 158 there were 74 assistant entries; the count reaches 91 only
  at line 190; the file now holds 272 lines and 133 assistant entries, all
  `claude-opus-5`. The claim was true when taken and is not reproducible as
  written (F-5).
- "Twelve stream-json events" for Arm B2 contradicts its own enumeration in the
  same sentence, which sums to thirteen. The file contains thirteen (F-6).
- "seven tracked files unrelated to the installed Skill payload" is contradicted
  by `trace.md` section 1, which correctly records that two of those seven are
  payload files. I verified both statements: seven tracked files are modified,
  and `docs/validation.md` and `docs/release/v1.0-rc-checklist.md` are among the
  60 installed files (F-7).
- "payload files present at that commit: 60" rests on an undefined term. That
  commit tracks 114 files; the installed set is `SKILL.md`, `README.md`, `docs/`,
  and `.looppilot/`, and excludes 54 tracked files including `tests/`, `scripts/`,
  `examples/`, `agents/`, `evaluations/`, `AGENTS.md`, `CHANGELOG.md`, and
  `LICENSE`. The repository's own later `distribution/managed-files.txt` defines
  a materially larger managed payload, so the word invites a misreading (F-8).

The reachability boundary should also be stated plainly, because the package
states it only for the digest: a reader holding this repository and nothing else
can verify exactly one claim in the package — that
`530bbaf7718c4fc7ae54446621a9ab0d67363c8bf9e4c82e1306466aefcb146a` is the
normalized body digest of `SKILL.md`. Every other claim requires the operator's
machine, and two of the three artifact classes are transient there.

## Independent Verification Performed

Every check below was run by me against primary artifacts, not against the
package's prose. Results are stated as returned.

| Check | Result |
| --- | --- |
| `git rev-parse HEAD` | `b482c9c990b9912d99230460bcd7540b64fd74fa` — matches |
| `git merge-base --is-ancestor aacbde44... HEAD` | exit 0 — matches |
| `aacbde44...:SKILL.md` and `HEAD:SKILL.md` blobs | both `6e0f26a9e948659541f88fc066e4e70dfcb31b0b`; worktree `git hash-object SKILL.md` identical — matches |
| Installed vs repository `SKILL.md` | both `a432bc262b954ede6bbbba893be7ee9bc76da61270b08587ebff9b20d9981778`, both 17648 bytes, mtime `2026-08-03T13:53:25.852` — matches |
| Installed tree size | 60 files — matches |
| Installed files vs commit blobs | 60 checked, 0 missing at that commit, 0 mismatched — matches |
| Installed files vs working tree | 4 differ: `README.md`, `docs/full-loop-migration-plan.md`, `docs/validation.md`, `docs/release/v1.0-rc-checklist.md` — matches |
| Modified tracked files in working tree | 7 — matches count; 2 of them are installed payload files, contradicting `environment.md` |
| Project-scope skill directory | absent — matches |
| Relative links in installed `SKILL.md` | 14 found, 14 resolve, 0 unresolved — matches |
| Frontmatter length | 591 characters to the closing `---`, 592 including its newline — matches the "592 removed" figure |
| Repository-derived normalized body | length 17054, `530bbaf7718c4fc7ae54446621a9ab0d67363c8bf9e4c82e1306466aefcb146a` — matches |
| Transcript entry 149 | `assistant`, `tool_use` `Skill`, input `{"skill": "loop-pilot"}`, `2026-08-09T05:41:05.118Z`, version `2.1.224` — matches |
| Transcript entry 150 | `user`, `tool_result`, text `Launching skill: loop-pilot`, `...05.126Z` — matches |
| Transcript entry 151 | `user`, `isMeta: true`, single text block of 17128 characters, first line is the base-directory line, `...05.125Z` — matches |
| Entry 151 raw SHA-256 | `73bf663576e892ebbe5aba04c70066fc7d6101a0a2a2d38c256d0e53187241af` — matches |
| Entry 151 normalized SHA-256 and length | `530bbaf7...146a`, 17054 — matches, and equals the repository-derived value |
| `version` field across all transcript entries | 59 entries have none; all 200 message entries are `2.1.224` — package claim overstated |
| Assistant entry count | 74 at line 158, 91 at line 190, 133 now; all `claude-opus-5` — package count is a later snapshot |
| Prior exposure of `SKILL.md` in session | `Read` at line 84, body text at lines 85 and 89 — confirms the package's own contamination disclosure |
| Transcript chain integrity | `uuid`/`parentUuid` intact across 148-152; only read-shaped tool calls touched the transcript path |
| Arm B1 `p1-discovery.jsonl` | 13 events; init `2.1.226`, `claude-fable-5[1m]`, `tools: []`, `permissionMode: default`, `apiKeySource: none`, 42 skills incl. `loop-pilot`, 68 slash commands incl. `loop-pilot`; 10 retries `429`/`rate_limit`; `<synthetic>` assistant; result `is_error` true, cost 0 — matches |
| Arm B2 `p2-loading.jsonl` | 13 events, not twelve; init `tools: ['Skill']`, `permissionMode: dontAsk`; same 429 pattern; `num_turns` 1, cost 0; no `Skill` tool call, no tool result, no model answer — matches except the event count |
| Arm B prompt files on disk | byte-for-byte identical to the text quoted in `prompt.md` — matches |
| Arm B working directory | `.tmp/phase13/cwd` exists and is empty — matches |
| Arm B artifact preservation | `.tmp/` is gitignored (`git check-ignore` confirms); files exist on disk but are outside version control |
| Probe answerability of L1-L4 | all four items exist in the body — section 15 "Token-Aware Checklist and Budget Stop"; section 7 outcomes Completed, Partially Completed, Blocked, Budget Stop; the section 11 sentence containing "Governance Artifact target"; the unnumbered heading "Loop Invariants" between sections 4 and 5 — and none appears in the frontmatter `name` or `description`; the probe design was sound |
| `tests/scenarios.md` | 301 numbered scenarios, none an installation or Skill-loading probe — supports the named-fixture Scenario ID |
| EVAL package structure | EVAL-001 has 5 files incl. `score.md` and `reviewer-report.md`; EVAL-004 has 3 and neither |

What I could not check: process exit codes for the Arm B runs (post hoc, though
consistent with `is_error` true); the wall-clock invocation of either Arm B
command; whether the host actually transmitted entry 151 to the model; whether
the transcript was altered before I read it, since it is operator-writable and
carries no signature; and anything about implicit activation, since none was ever
attempted.

## Findings

| ID | Severity | Axis | Finding | What would have to change |
| --- | --- | --- | --- | --- |
| F-1 | major | Standards | No `score.md`, no rubric score, no `Reviewer decision`, no named `Reviewer`, no named trace author, and no self-declaration of incompleteness, against explicit MUSTs in `docs/cross-host-acceptance.md` and `evaluations/README.md`. Not validator-enforced, so it is the reviewer's to catch. | Add `evaluations/claude-code/EVAL-004/score.md` from the template recording `Observed outcome`, `Reviewer decision: not-reviewed`, a named trace author, `Unverified limitations`, and an explicit statement that no behavioral fixture was run so the 0-to-3 dimensions are not applicable. Do not fabricate scores. State in the package that EVAL-004 is an incomplete evaluation for acceptance purposes. |
| F-2 | major | Evidence | No decisive raw artifact is preserved in version control. The Arm A transcript sits in a host cache outside the repository and the Arm B outputs sit under gitignored `.tmp/`. Both are transient; a future reader can verify only the repository-derived digest. | Copy `p1-discovery.jsonl` and `p2-loading.jsonl` (about 6.6 KB each) into the evaluation directory, and preserve transcript entries 149 and 150 verbatim plus entry 151's two SHA-256 values and character count as a committed excerpt. Entry 151's body need not be duplicated, since it is `SKILL.md`. |
| F-3 | major | Spec | The only arm that could establish loading independently of the observing session failed once on infrastructure and was never retried, although the package records a probable self-inflicted cause (nested subprocess sharing the account with the live session). The loading claim therefore rests entirely on self-observation. | Re-run Arm B2 outside the live session, or at a different time, and record the outcome; or state explicitly that no retry was attempted, that the probable cause was concurrent account load, and that the loading claim is self-observed only. |
| F-4 | minor | Evidence | "Every entry in this transcript ... records `version` `2.1.224`" is false; 59 entries carry no `version` field. | Restate as: every `assistant` and `user` message entry records `2.1.224` and none records another version. |
| F-5 | minor | Evidence | Entry counts are taken from different snapshots of a growing file, so "142/158 entries" and "91 assistant entries" cannot both be re-derived. | State the exact file length at which each count was taken, or express counts over a fixed, preserved excerpt. |
| F-6 | minor | Evidence | Arm B2 is reported as "Twelve stream-json events" while the same sentence enumerates thirteen; the file has thirteen. | Correct to thirteen. |
| F-7 | minor | Evidence | `environment.md` calls the seven modified tracked files "unrelated to the installed Skill payload", contradicted by `trace.md` section 1 and by the files themselves. | Replace with: two of the seven are payload files whose installed copies remain pinned to `aacbde44...` and were unaffected by the working-tree edits. |
| F-8 | minor | Evidence | "payload files present at that commit: 60" uses an undefined term; the commit tracks 114 files and the repository's own `distribution/managed-files.txt` defines a larger managed payload. | Define the payload set explicitly as `SKILL.md`, `README.md`, `docs/`, and `.looppilot/`, and name the excluded trees. |
| F-9 | minor | Standards | The package never states in one place that the observing session was also the subject, and names no trace author. | Add one sentence naming the self-observation and its mitigation, and name the trace author in `environment.md` and `score.md`. |
| F-10 | minor | Evidence | `trace.md` section 1 is titled "observed before any host invocation", but the Arm A host session was already live at 142 entries and ran those commands. | Retitle as observed from inside the live Arm A session, before the Skill invocation. |
| F-11 | minor | Standards | `environment.md` states one "Skill loading mode" for the whole evaluation though Arm B established registration only. | Split the bullet per arm: observed loading for Arm A, intended but never reached for Arm B. |
| F-12 | minor | Evidence | The 429 incident is correctly excluded from Product Findings but is never labelled with the project's own category, and its probable cause is recorded elsewhere without ever being connected to it. | Label it an Execution Infrastructure Incident and state the probable cause and its verification effect in the same place. |

Counts: 0 blocker, 3 major, 9 minor. None is a Finding against the frozen v1
protocol.

## Limits of This Review

I am an AI reviewer instantiated by the same operator who produced the package,
running in the same repository, on the same machine, with the same tools, under
the same parent orchestration, and on a model from the same family as the Arm A
subject. That is worth stating first, because it bounds everything else.

What independence I do provide:

- I re-derived every load-bearing number from primary artifacts rather than
  reading them from the package: four SHA-256 values, the 60-file blob
  comparison, the link resolution, the transcript entries, and the Arm B event
  fields. Where the package and the artifacts disagreed, I reported the artifact.
- I did not read the package author's own analysis or conclusions. I did not open
  anything under `docs/evaluations/` other than to write this file. One filename
  in that directory appeared incidentally in `git status` output; I did not open
  it and it played no part in any judgment here.
- I formed the three axis values before writing them down and was given no target
  answer, and I found and reported errors the package did not disclose.

What independence I do not provide:

- No organizational independence and no second party. If the operator's framing,
  environment, or account is wrong in some systematic way, I inherit that error.
- No second machine, second account, second host installation, or second model
  family. I verified the artifacts that exist; I did not reproduce the experiment.
- I cannot prove the Arm A transcript was not altered before I read it. It is
  operator-writable and unsigned. I checked chain integrity, `isMeta` flags,
  timestamp interleaving, marker uniqueness, and in-session write attempts, and
  found no tampering signal, which is evidence but not proof.
- My own verification of Arm B is itself unreproducible for a later reader. I
  read the raw files from `.tmp/`, which is gitignored and transient. If those
  files are cleaned up, F-2 becomes unrecoverable and Arm B reduces to prose.
- I could observe no Arm B model behavior because none exists, no implicit
  activation because none was attempted, and no behavioral consequence of loading
  because the package deliberately posed no task after the invocation.
- I did not run the host, did not score any rubric, and did not evaluate any
  dimension other than the loading half of dimension 1.

Finally, a scope reminder that this review inherits from the procedure it applies:
nothing here supports a claim about `Claude Code 2.1.226`, about
`claude-fable-5[1m]`, about project-scope or plugin loading modes, about implicit
activation, or about Claude Code as a class. The loading observation belongs to
`Claude Code 2.1.224` + `claude-opus-5` + user-scope directory + explicit `Skill`
tool invocation, and to nothing else.
