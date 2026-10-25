# Environment

- Evaluation ID: EVAL-004
- Scenario ID: named fixture `host-skill-loading-probe`; no numbered scenario in
  [`tests/scenarios.md`](../../../tests/scenarios.md) describes a host
  installation and Skill-loading probe
- Date and time: 2026-08-09; the recorded Skill invocation carries host
  timestamp `2026-08-09T05:41:05.118Z` (UTC)
- Host: Claude Code
- Trace author: the Claude Code 2.1.224 / claude-opus-5 session operated by
  `tutict` on 2026-08-09, session id `664a2bdc-ac5f-473a-adbd-2294fc3965bf`.
- Self-observation: that same session is the Arm A subject, so Arm A is an
  observation of the observer. Arm B existed to remove that dependency and
  failed before any model turn on both of its attempts. Every Arm A claim
  therefore rests on artifacts the host wrote — its own session transcript — and
  on a digest recomputable from this repository alone, never on the session's
  narration of its own behavior. What this does not remove: a reader must trust
  that the named transcript file is genuine and unaltered, and that file lies
  outside version control.
- Host version: two host versions were exercised and are kept separate.
  - Arm A, in-session: `2.1.224`, as recorded in the `version` field of every
    entry of the host's own session transcript, including the entries carrying
    the Skill invocation.
  - Arm B, headless subprocess: `2.1.226`, as recorded in the
    `claude_code_version` field of the `system/init` event. `claude --version`
    on the same machine printed `2.1.226 (Claude Code)`.
- Model: differs per arm.
  - Arm A: `claude-opus-5`, recorded in the `message.model` field of all 91
    assistant entries in the session transcript.
  - Arm B: `claude-fable-5[1m]`, recorded in the `model` field of the
    `system/init` event. The invoking command passed `--model opus` in the
    discovery run and passed no `--model` flag in the loading run.
- LoopPilot commit: the installed Skill tree is exactly
  `aacbde449a6dbc8723d5c866033ac195017a90e5`. All 60 installed payload files
  hash-match that commit's blobs, and that commit contains exactly 60 payload
  files out of 114 tracked files. The repository working tree during the run was
  at HEAD `b482c9c990b9912d99230460bcd7540b64fd74fa`, which is a descendant of
  the installed commit, and carried uncommitted modifications to seven tracked
  files. Two of those seven, `docs/validation.md` and
  `docs/release/v1.0-rc-checklist.md`, are payload files; the installed copies
  of both remain pinned to `aacbde44` and were unaffected by the working-tree
  edits. The other five are `CHANGELOG.md`, `scripts/validate.py`,
  `scripts/cross_host_acceptance_validation.py`,
  `tests/test_validate.py`, and `tests/test_cross_host_acceptance.py`, none of
  which is part of the installed payload. `SKILL.md` was not modified.
- Skill loading mode: differs per arm, and Arm B never reached the loading it
  intended.
  - Arm A: loaded from the host's user-scope Skill directory,
    `C:\Users\tutic\.claude\skills\loop-pilot`, activated by explicit invocation
    through the host's `Skill` tool. Loading was observed.
  - Arm B: the same user-scope directory and the same explicit-invocation mode
    were intended, and the run registered the `Skill` tool and the `loop-pilot`
    name, but no invocation occurred. For Arm B only registration is
    established, never loading.

  Project scope
  `C:\Users\tutic\IdeaProjects\LoopPilot\.claude\skills\loop-pilot` does not
  exist, in either arm.
- Task fixture: installation, discovery, and Skill-loading verification only. No
  behavioral task fixture was run in either arm.
- Available tools and state:
  - Arm A: the host's full default tool set, in an authenticated interactive
    session whose working directory was the repository.
  - Arm B: `--tools ""` in the discovery run, so no tool was available; and
    `--tools "Skill"` in the loading run, so the `Skill` tool was the only
    available tool and no file-reading tool existed. Both runs used
    `--no-session-persistence` and an empty working directory,
    `.tmp/phase13/cwd`, containing zero entries.
- Granted authority: read and inspect the local machine and repository; run the
  host CLI as a bounded subprocess with a spend cap of USD 0.25 in the discovery
  run and USD 0.50 in the loading run. No commit, push, publish, or deploy
  authority was exercised by either arm.
- Material environment constraints:
  - Operating system: Microsoft Windows NT 10.0.26200.0, Windows 11 家庭版 中文版.
  - Host CLI path: `C:\Users\tutic\.local\bin\claude.exe`.
  - `apiKeySource` reported `none`; the account authenticated by an existing
    OAuth login. `ANTHROPIC_API_KEY` was not set in the environment.
  - Arm B ran as a nested subprocess launched from inside the live Arm A
    session, so both arms drew on the same account concurrently.
  - The Arm A session began under host version `2.1.224` while the CLI binary on
    disk reported `2.1.226`; the on-disk binary changed during the session's
    lifetime and the running session was not restarted.
- Unverified limitations:
  - No behavioral protocol dimension was exercised. Mode selection, authority
    and stopping, shared-state handling, Full Loop artifact handling, checkpoint
    recovery, lifecycle projections, and evidence honesty were not put under
    test by any fixture in this evaluation.
  - No Lightweight-shaped fixture and no Full-Loop-shaped fixture were run.
  - No control arm was run; nothing here isolates the protocol's marginal effect.
  - Whether the host activates the Skill implicitly on an in-scope task was not
    tested. Activation was explicit in Arm A.
  - Whether the host reads the Skill's linked supporting files on demand was not
    observed. Only the existence and resolvability of those targets was checked.
  - Arm B never reached a model turn on either of its two attempts, so no Arm B
    behavior beyond process initialization was observed. The loading claim rests
    on Arm A, which is self-observed.
  - The two arms are different host version and model combinations and no
    observation from one arm was carried to the other.
  - Whether the Arm A session transcript is genuine and unaltered. It is
    operator-writable, unsigned, and outside version control.
