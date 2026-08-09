# Host Loading Verification: Claude Code

## What This Document Is

This is the Phase 13-A host loading verification record for the reference host,
Claude Code. It reports whether the host installs, discovers, and actually loads
the `loop-pilot` Skill.

It is deliberately **not** a Host Acceptance Record and carries no acceptance
verdict. Under [`docs/cross-host-acceptance.md`](../../cross-host-acceptance.md)
a host verdict lives in a Host Acceptance Record under `evaluations/`, and each
lifecycle fact has exactly one authoritative source. Publishing a second
document that declared a host verdict would create the drift the protocol
forbids. Host verdicts therefore remain where they already live; this record
supplies loading evidence to them and changes no verdict by itself.

Underlying evidence package:
[`evaluations/claude-code/EVAL-004/`](../../../evaluations/claude-code/EVAL-004/environment.md),
comprising `environment.md`, `prompt.md`, `trace.md`, `score.md`, and a
committed [`evidence/`](../../../evaluations/claude-code/EVAL-004/evidence/README.md)
directory. That package declares itself an **incomplete evaluation** for
acceptance purposes: no behavioral fixture was run, so no rubric score exists
and no reviewer scored a behavioral trace.

An independent review of the package, restricted to the environment, prompt,
trace, and evidence and denied this document, is recorded in
[`HOST-ACCEPTANCE-REVIEW.md`](HOST-ACCEPTANCE-REVIEW.md). Its findings were
applied to the package after it was written; the sequence and the corrections
are recorded in [`HOST-ACCEPTANCE-DECISION.md`](HOST-ACCEPTANCE-DECISION.md).

## Two Combinations, Kept Separate

The verification exercised two different host version and model combinations.
An acceptance result is scoped to one host, host version, model, and loading
mode, and never generalizes across versions or models. They are reported
separately throughout and nothing observed in one is carried to the other.

| | Arm A | Arm B |
|---|---|---|
| Invocation | in-session, explicit `Skill` tool call | headless `claude -p` subprocess |
| Host version | 2.1.224 | 2.1.226 |
| Model | claude-opus-5 | claude-fable-5[1m] |
| Working directory | the repository | empty directory, zero entries |
| Loading mode | user scope, explicit invocation | user scope, explicit invocation |

The host version difference is not an authoring choice. The Arm A session began
under 2.1.224 and the CLI binary on disk was replaced with 2.1.226 during the
session's lifetime without the running session restarting. `claude --version`
reports the on-disk binary, 2.1.226; the session transcript records 2.1.224 on
every entry, including the entries carrying the Skill invocation. The transcript
is the authority for what the running session was, so Arm A is recorded as
2.1.224.

## 1. Skill Installation Location

| Item | Observed value |
|---|---|
| Host | Claude Code |
| Host version | 2.1.224 (Arm A session), 2.1.226 (on-disk binary and Arm B) |
| Operating system | Microsoft Windows NT 10.0.26200.0, Windows 11 家庭版 中文版 |
| Host CLI path | `C:\Users\tutic\.local\bin\claude.exe` |
| Installation path | `C:\Users\tutic\.claude\skills\loop-pilot` (user scope) |
| Project-scope path | `C:\Users\tutic\IdeaProjects\LoopPilot\.claude\skills\loop-pilot` — absent |
| Installed files | 60 |
| Skill SHA-256 | `a432bc262b954ede6bbbba893be7ee9bc76da61270b08587ebff9b20d9981778` |

That digest is `SKILL.md` as installed, 17648 bytes. The repository copy of
[`SKILL.md`](../../../SKILL.md) hashes identically, so the installed Skill and
the repository Skill are the same bytes.

The installed tree's Git boundary is commit
`aacbde449a6dbc8723d5c866033ac195017a90e5`. All 60 installed files hash-match
that commit's blobs and that commit carries exactly 60 payload files, so the
installation is that commit exactly and not a mixture. That commit is an
ancestor of the working-tree HEAD `b482c9c990b9912d99230460bcd7540b64fd74fa`,
and `SKILL.md` is the identical blob at both commits, so the loading evidence
applies unchanged to `SKILL.md` at HEAD.

Four installed files differ from the working tree: `README.md`,
`docs/full-loop-migration-plan.md`, `docs/validation.md`, and
`docs/release/v1.0-rc-checklist.md`. Each installed copy matches
`aacbde44`; the working tree has moved on. This is installation staleness
against HEAD, not corruption, and it does not touch `SKILL.md`.

All 14 relative references in the installed `SKILL.md` resolve to existing files
under the installation base directory. Only target existence was checked. No
host read of any target was observed, so host-side reference resolution remains
unverified.

## 2. Skill Discovery

Discovered: yes, on both combinations.

**Arm B, host 2.1.226.** A fresh headless process started in an empty directory
with no repository files, no project-scope Skill directory, and no `CLAUDE.md`
emitted a `system/init` stream-json event listing `loop-pilot` in both its
`skills` array (42 entries) and its `slash_commands` array (68 entries).
Because the working directory was empty, discovery is attributable to the
user-scope installation and to nothing in the project.

**Arm A, host 2.1.224.** The host accepted a `Skill` tool call whose input was
`{"skill": "loop-pilot"}` and resolved that name to the installed Skill,
returning content from the installation base directory. Name resolution against
the registry is discovery; it is reported here as observed rather than inferred
because the resolution itself is recorded in the transcript.

**Discovery mechanism.** The host enumerates its user-scope Skill directory at
process start, registers each Skill by the `name` field of its YAML frontmatter,
and exposes the registered name both as an invocable Skill and as a slash
command. The registered name `loop-pilot` matches the `name` field of the
installed `SKILL.md`.

**Discovery is not loading.** A `system/init` event proves the host indexed the
Skill's frontmatter. It proves nothing about whether the host will inject the
Skill body when invoked. Section 3 establishes loading separately, and only on
the combination where it was actually observed.

## 3. Skill Loading

Loaded: yes on Arm A, host 2.1.224 with model claude-opus-5. Not established on
Arm B.

### Arm A, observed and verified

- **Prompt.** The `Skill` tool takes a skill name, not natural language. The
  exact recorded tool input was `{"skill": "loop-pilot"}`. The instruction that
  authorized the call was the operator's Phase 13-A requirement to perform a
  real Skill invocation.
- **Invocation method.** Explicit invocation through the host's native `Skill`
  tool, inside an authenticated interactive session, from the user-scope
  installation. Not implicit activation.
- **Loaded content evidence.** The host emitted `Launching skill: loop-pilot`
  and then injected a 17128-character message whose first line was
  `Base directory for this skill: C:\Users\tutic\.claude\skills\loop-pilot`.
  Stripping that prepended line, stripping the installed file's 592-character
  YAML frontmatter, and normalising line endings makes the injected content and
  the installed file byte-identical, both hashing to
  `530bbaf7718c4fc7ae54446621a9ab0d67363c8bf9e4c82e1306466aefcb146a`.
  The whole exchange is preserved in the host's own on-disk session transcript
  at entries 149, 150, and 151, with host timestamps at
  `2026-08-09T05:41:05Z`.
- **Returned behavior.** The host returned the Skill's instructional text and
  declared the base directory that makes the Skill's 14 relative references
  resolvable. It returned protocol text, not an answer, which is the correct
  behavior for a Skill load.

This establishes the load end to end: the content the host injected is provably
the content of the installed file, and the host itself named the installation
directory it loaded from.

### The self-observation problem, and what limits it

Arm A's evaluating session is also its subject. That is a real weakness and it
is why the claim rests on artifacts rather than on the session's own account of
itself:

- The tool call, the tool result, and the injected content are recorded in the
  host's transcript file on disk, written by the host, not by the evaluator.
- The expected digest is recomputable from this repository alone, because the
  installed and repository `SKILL.md` are byte-identical. A third party can
  derive `530bbaf7…` without access to the operator's machine, then check it
  against the transcript.
- The session had already read `SKILL.md` before invoking the Skill. Arm A
  therefore proves nothing by content recall, and no recall-based claim is made
  from it. Arm B was designed to remove that objection entirely by denying the
  run any file-reading tool; Arm B did not complete.

What remains unmitigated: a reader must trust that the named transcript file is
the session's genuine transcript. That file is outside this repository.

### Arm B, not established

Arm B was the stronger design. With `--tools "Skill"` the run had no
file-reading tool, so the four requested items — each present only in the
`SKILL.md` body and absent from the frontmatter a host exposes for discovery —
could only have been answered from content the `Skill` tool returned. The run
never reached a model turn, on either of two attempts separated by roughly two
hours. No `Skill` tool call occurred and the four items were never answered.

Both attempts did register the `Skill` tool as available and did list
`loop-pilot` among registered skills, so the failure sits at the model-call
boundary rather than in tool availability or Skill registration.

Loading on host 2.1.226 with model claude-fable-5[1m] is therefore **not
established**. The Arm A result does not transfer to it: different host version,
different model.

Because Arm B never completed, the loading claim rests on Arm A alone and is
self-observed. That is the single largest weakness in this record, and it was
not for want of trying to remove it.

## 4. Failure Classification

Both Arm B runs, and the later retry of the loading run, ended identically: ten
`system/api_retry` events, attempts 1 through 10 of 10, each
`"error_status":429` with `"error":"rate_limit"`, then a synthetic assistant
message reading `API Error: Request rejected (429) · Service Unavailable`, then
a result event with `is_error` true and zero cost.

**Cause: C, Execution Infrastructure Incident.** Not a LoopPilot defect, and the
protocol keeps Execution Infrastructure Incidents separate from Product and
Protocol Findings. The reasoning:

- It is not **A, a host configuration gap**. The account was authenticated and
  working: the Arm A session was executing successfully throughout, and the
  headless process initialized, read its configuration, and enumerated the
  Skill registry correctly. This is materially different from the earlier
  Distribution-003 gap `D003-HCG-001`, where the isolated profile reported
  `loggedIn:false`. Here nothing was misconfigured.
- It is **C**. Arm B was launched as a nested subprocess from inside the live
  Arm A session, so both drew on the same account concurrently, and every
  attempt was refused with a rate-limit status. The refusal came from the
  serving infrastructure under concurrent load created by the harness itself,
  not from the host binary, the installation, the Skill, or the protocol.

**Consequence: B, Host Capability Unverified.** The cause is C; the resulting
state of the unobserved behavior is B. Whether host 2.1.226 with model
claude-fable-5[1m] loads Skill content remains unverified. An incident explains
why evidence is absent; it never substitutes for the evidence.

**One retry was made, and it reproduced.** The loading probe was re-run at a
materially later time, after roughly two hours had elapsed and the account's
recent request history had changed, which is a material change of conditions
rather than a repeat of an unchanged failed action. It failed identically. The
failure is therefore persistent in this environment, not a transient blip, and
no further retry was attempted because a third identical attempt would repeat an
unchanged failed action with no material change to distinguish it.

## 5. What This Does and Does Not Establish

Established, on host 2.1.224 with model claude-opus-5, user-scope installation,
explicit invocation:

- The installed Skill is byte-identical to the repository Skill and pins to a
  known commit.
- The host discovers the Skill from user scope.
- The host loads the Skill body, and the loaded bytes provably match the
  installed file.
- The host supplies a base directory under which all 14 relative references
  resolve.

Not established, and not to be read into the above:

- **Activation on an in-scope task.** Acceptance dimension 1 requires the host
  to load `SKILL.md` *and* activate on an in-scope task without fabricating a
  trigger. Only the loading half was observed; activation was explicit in every
  arm. Dimension 1 is at most partially evidenced, and is not `pass`.
- **Acceptance dimensions 2 through 8.** Mode selection, authority and stopping,
  shared-state handling, Full Loop artifact handling, checkpoint recovery,
  lifecycle projections, and evidence honesty were not exercised by any fixture.
  Each remains `not-evaluated`, which is not `pass`.
- **Rubric scores.** No behavioral trace was produced, so no critical rubric
  dimension has a score.
- **Fixture coverage.** No Lightweight-shaped and no Full-Loop-shaped fixture was
  run. An accepted verdict requires both.
- **Loading on host 2.1.226**, on any other host version, on any other model, or
  under implicit activation.
- **Host-side reading of the Skill's linked supporting files.** Only target
  existence was checked.

The direct consequence is that this evidence, however clean, cannot by itself
support an `accepted` or `accepted-with-residuals` verdict, because those
require every dimension to be `pass` or at least `partial`, plus rubric scores,
plus both fixture shapes, plus an independent reviewer. Phase 13-A closes the
loading question that was blocking. It does not close acceptance.
