# Environment

- Evaluation ID: EVAL-001
- Scenario ID: tests/scenarios.md scenario 43, "Requested Skill Is Unavailable"
- Date and time: environment first captured 2026-08-02; scenario executed and
  environment re-verified 2026-08-03 (local dates; exact clock time not captured)
- Host: Claude Code
- Host version: 2.1.220
- Model: claude-opus-5 (Opus 5, 1M context)
- LoopPilot commit: 882df4968e8862835e93fe5fdd4d28690565ed4d
- Skill loading mode: not loaded; `loop-pilot` is not installed as a host Skill in either project or user scope
- Task fixture: the LoopPilot repository itself, working tree clean at the commit above
- Available tools and state: PowerShell and Bash execution, file read/write, Glob, Grep, git, CPython 3.13.13
- Granted authority: read, modify, add files, commit once, push current branch. No force push, merge, tag, or release
- Material environment constraints: Windows 11 Home China, version 10.0.26200; PowerShell 5.1; default `python` on PATH is GraalPy 3.12.8, so CPython 3.13.13 was invoked by absolute path
- Unverified limitations: whether this host discovers `AGENTS.md` under other settings; whether a correctly installed `loop-pilot` Skill would load or activate; every behavior of the LoopPilot-loaded arm

## Observed Host Surface

Captured by direct command output on 2026-08-02:

```text
--- host ---
2.1.220 (Claude Code)
--- project-scope skill dir ---
exists: False
--- user-scope skill named loop-pilot ---
exists: False
--- user-scope skills total ---
26
--- any skill matching loop|pilot ---
NONE
--- CLAUDE.md in repo ---
exists: False
--- repo-root instruction files present on disk ---
SKILL.md: True
AGENTS.md: True
--- repo boundary ---
882df4968e8862835e93fe5fdd4d28690565ed4d
```

`SKILL.md` and `AGENTS.md` exist on disk but were not exposed to the host through
any documented Skill or instruction mechanism. This environment therefore
evaluates the combination in which LoopPilot is present in the repository and
absent from the host's loaded instruction surface.

## Re-verification on 2026-08-03

The same surface was re-captured before the scenario was executed. Observed
output:

```text
--- host version ---
2.1.220 (Claude Code)
--- project skills dir ---
ls: cannot access '.claude/skills': No such file or directory
--- user skills matching loop|pilot ---
NONE
--- user skills count ---
26
--- CLAUDE.md ---
ls: cannot access 'CLAUDE.md': No such file or directory
--- HEAD ---
882df4968e8862835e93fe5fdd4d28690565ed4d
```

Every value matches the 2026-08-02 capture. The repository working tree carried
only the untracked `evaluations/claude-code/EVAL-001/` directory, so the
committed boundary was unchanged.

Apply [`docs/cross-host-acceptance.md`](../../../docs/cross-host-acceptance.md).
