# Option B Reference Successor — Authorization Record

- Decision ID: OPTION-B-REFERENCE-2026-10-24
- Decision date: 2026-10-24
- Approving authority: caller's one-time task instruction; personal identity not recorded
- Authorization source: attached user task, “LoopPilot — Option B Successor → RC Candidate → Safe Remote Push”
- Authorized action: implement a bounded, forward-effective successor allowing an applicable RC to designate one Reference Host from Claude Code or Codex
- RC-specific choice: Codex for `v1.0.0-rc1`
- Policy version: option-b-successor-v1
- Effective boundary rule: first commit containing the successor policy, this record, the enforcing validator, and regression tests
- Effective boundary commit: determined from the first qualifying commit in Git history
- Gate 4 threshold: unchanged
- Gate 5 disclosure: unchanged
- Historical effect: none
- Standing authority: none

## Limits

This authorization is one-time and applies only to the Option B Reference Host
qualification and the `v1.0.0-rc1` designation described in the associated
successor policy. It does not establish a general F2 approval process or authorize
future capability expansions. It does not waive any RC gate, Host Acceptance
dimension, evidence requirement, independent-review requirement, or existing
release/deployment boundary.

The task instruction does not expose a personal name or organization identity for
the approving caller. This record preserves that limitation instead of inventing
an identity. The task-specific instruction itself is the authorization evidence.
