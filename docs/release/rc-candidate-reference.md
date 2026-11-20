# RC Candidate Reference Designation — v1.0.0-rc1

- RC version: v1.0.0-rc1
- Successor ID: OPTION-B-REFERENCE-2026-10-24
- Successor policy: docs/release/option-b-reference-successor.md
- Policy version: option-b-successor-v1
- Reference designation ID: RC1-REF-CODEX-20261024
- Reference Host: Codex
- Other eligible Host: Claude Code
- Other Host role: Candidate Host; unverified disclosure retained
- Designation state: finalized-before-acceptance
- Designation date: 2026-10-24
- Finalized at: 2026-11-19T18:51:08+08:00
- Formal acceptance arms at designation: none
- Reference host version: 0.168.0
- Model identity: gpt-6.1-sol
- Provider identity: api.hanbbq.top
- Endpoint identity: https://api.hanbbq.top/v1
- Configured model: gpt-6.1-sol
- Configured provider: custom
- Configured endpoint: https://api.hanbbq.top/v1
- Skill loading mode: explicit, implicit
- RC baseline commit: c6342cf115c285d0c8995a9cb62834518e7f0fd2
- RC baseline tree: 281ec23ea7dbb9a9c65765340ca93c4de3e4538d

This designation fixes the Reference Host for this RC before any formal
acceptance arm. It was finalized after the authorized responsible party
confirmed the canonical boundary (D1), accepted the relay-asserted identity
layer with disclosure (D2), and authorized one local designation commit (D3)
on 2026-11-19. No formal acceptance arm had started at finalization. The
Reference choice remains Codex for this RC; a different choice or finalized
combination requires a new RC version. The other eligible host, Claude Code,
remains a Candidate Host with its explicitly unverified status, governed by
the Cross-Host Acceptance procedure.

## Finalization authority and decisions

Decisions were given by the user (authorized responsible party) via
AskUserQuestion in the operator session; answers delivered
2026-11-19T18:42:12+08:00 and recorded verbatim in the operator external
store (`LoopPilot-rc-staging/formal-external/canonical-boundary-decision-record.md`
and `authorization-ledger.md`):

- D1 canonical boundary: `A: main@c6342cf`. The RC baseline commit/tree above
  is that boundary; the branch `codex/rc-history-byte-preservation` (3f7433c)
  is deferred as optional later hardening with its own authorization and
  Hash B re-bind cycle if merged.
- D2 identity gate: `接受 relay-asserted 层（含披露）`. This is a
  responsible-party risk acceptance of the relay-asserted evidence layer,
  not a claim of upstream proof. The upstream-unverified disclosure below
  remains mandatory in every run package, review receipt, and summary.
- D3 commit authorization: `授权：D1/D2 定稿后提交`. One local commit of this
  finalized record; no push, no tag, no release. Any further commit requires
  fresh item-specific authorization.
- The 18-arm boundary interpretation (shared install/designation/Hash B
  boundary plus one fresh current boundary for the four formal arms, with
  historical arms keeping matrix-pinned combinations) was not explicitly
  answered and must be re-confirmed at the pre-experiment boundary re-check.

## Identity evidence and disclosure

Operator-side capture at the final arm-home, 2026-11-19T18:36:54+08:00
(`LoopPilot-rc-staging/formal-external/identity-capture/relay-identity-probe-20261119.json`,
5925 bytes, SHA-256
`72f9ae7820b4d6ca62778712b7f18ccfed96b5f855f40af9c93b4fcb591e8cf9`):

- L1 configuration (observed): arm-home provider block `custom`, model
  `gpt-6.1-sol`, wire API `responses`, base URL `https://api.hanbbq.top/v1`;
  provider blocks identical across arm homes; credential present and bound
  digest-only (SHA-256
  `2f93cab9a0f81a48d692806ec97ca9f4770a7f02818f34bb9e9d7eff79aeb91d`),
  never echoed.
- L2 relay metadata (observed operator-side): GET /v1/models HTTP 200 and
  minimal POST /v1/responses HTTP 200 with TLS verification enabled; the
  response envelope asserts model `gpt-6.1-sol`. A relay can claim any
  upstream; these are relay-ASSERTED values.
- L3 Codex rollout echo (observed in existing rollouts): cli_version
  0.168.0 and turn_context model `gpt-6.1-sol` (Codex-asserted).
- Upstream true identity: UNVERIFIED. No upstream-side evidence exists
  through this relay.

Disclosed relay anomalies: input_tokens 4229 (cached 4072) for a minimal
prompt, indicating hidden context injection; output_tokens 46 despite
max_output_tokens 16; an opaque encrypted `x-codex-turn-state` session
header (truncated in stored evidence); a four-hop `x-request-id` chain.

Metadata token contract: the identity fields above are clean tokens because
a formal reference run's observed and configured identity must equal them
exactly (`scripts/option_b_validation.py`, `_validate_rc_binding`).
`Provider identity: api.hanbbq.top` names the relay service host actually
serving the runtime, observed via the TLS/HTTP exchange; `Configured
provider: custom` is the configuration label. Each formal reference arm must
record runtime-identity observation events (basis
`actual-runtime-observation`, captured within the arm window, with
digest-bound source artifacts) reproducing exactly this combination. D2
acceptance does not convert relay assertions into upstream proof; the
relay-asserted layer and upstream-unverified status must be disclosed
wherever this combination is cited.

## Installation boundary and Hash B

Re-observed 2026-11-19 at the USER-scope install
(`C:\Users\tutic\.agents\skills\loop-pilot`), main repo at the baseline
commit with a clean worktree:

- Installer status CURRENT; installed == source c6342cf; exit 0
  (`LoopPilot-rc-staging/install-boundary-p1/status-recheck-20261119.txt`).
- C2 isolation C2_CLEAN; 0 findings; 127 files enumerated; installation
  state file not consulted
  (`LoopPilot-rc-staging/install-boundary-p1/c2-recheck-20261119.log`).
- Historical pin audit at this boundary: 31/31 pinned == matched ==
  byte-matched; exit 0
  (`LoopPilot-rc-staging/formal-external/history-audit-c6342cf-20261119.json`).
- Hash B (HB-1), BOUND by operator approval and independent certutil
  recompute on 2026-11-16: SHA-256 of the exact install receipt bytes
  `25d9995ea9c31fd4a4b0fef6c2fe42e7e2a4aa9f6f95026a6d531c3f3242c128`
  (receipt `receipt-p1-c6342cf.txt`, 14543 bytes). Binding record:
  `LoopPilot-rc-staging/install-boundary-p1/hash-b-binding-record.md`
  (6106 bytes, SHA-256
  `c1b957d34481b003c909a9d91c91bc06d4df50e7e21fa6dc22650352611f9b07`).
  Hash B authority lives in the operator external store; this record
  references it and copies no authority.
- C1 exec-level verification: genuine access-denied signals were observed,
  with disclosed gaps (P1 never targeted the main repo at exec level; a
  plan-conformant re-run with inner-exception capture is still pending).
  This designation does not claim C1 closure.

## Timing, immutability, and limits

- Finalized at precedes the designation commit, which must precede the first
  formal arm start. The baseline commit c6342cf is the parent boundary of
  the designation commit and the commit/tree formal reference runs bind as
  their run boundary.
- Once finalized, the combination (Reference Host, designation ID, identity
  fields, loading mode, baseline commit/tree, Finalized at) is immutable for
  v1.0.0-rc1 across Git history; a changed combination needs a new RC
  version, not reselection within this RC. Timestamps are never backfilled.
- Skill loading mode declares the frozen matrix union for the four current
  arms (LW-1, FL-1, FL-1R explicit; IMP-1 implicit); each formal run's
  loading mode must be a member of this set.
- This record grants no acceptance verdict and ticks no gate: Gate 4 remains
  unmet, acceptance status not-run, release tag not-created, as recorded in
  `docs/release/rc-candidate-decision.md`. Preparation checks are not formal
  acceptance arms; a failed preparation check does not permit automatic
  reselection.
