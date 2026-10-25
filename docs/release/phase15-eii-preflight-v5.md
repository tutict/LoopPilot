# Phase 15 Gateway Probe eii-preflight-v5

A bounded recovery probe. It is not an acceptance arm, not a score, and not a Host Acceptance Record.

## Observed

- Time: started 2026-09-22T23:34:26Z, stopped 2026-09-22T23:35:56Z.
- Image: pinned `claude-2.1.232.exe`, `--version` reported `2.1.232 (Claude Code)` with PATH emptied. SHA-256 `ec9e32479bc887809003c91384c6c3a26e7691856d1916f72f6f6d21800f3bd6`.
- Requested model: `claude-fable-5-1[1M]`. Init record model: `claude-fable-5-1[1m]`.
- Session: `2c774141-4c9e-460a-a877-d1906f3e2e5b`.
- Prompt: the existing minimal acknowledgement probe, copied byte for byte from eii-preflight-v4. It names no LoopPilot work.
- Transcript: 8 records, 7 `api_retry` / `rate_limit` / HTTP 429, 0 assistant records, 0 Skill tool calls.
- Stop: wall clock 90 seconds. No result event was emitted.

## Harness defect

The first watcher raised a sharing violation while reading the live transcript and exited without stopping the host. A second watcher stopped that same process at the planned deadline. The rate-limit records are host-emitted. The absence of a later host result is partly because the process was killed, and partly because every observed request had already returned 429.

## Effect

Gateway recovery remains **not verified**. No acceptance arm was launched. Host Acceptance remains unverified, and no Release Candidate gate is ticked.

Raw files: `C:/Users/tutic/.local/share/looppilot/phase15-evidence/eii-preflight-v5/`.
