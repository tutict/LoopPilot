# Option B Successor — RC Reference Host Policy

This is a named, bounded, forward-effective amendment to the Cross-Host Acceptance
procedure. It permits an applicable future RC to choose exactly one Reference Host
from Claude Code and Codex. It does not establish a general F2 process or a standing
capability-expansion policy.

- Successor ID: OPTION-B-REFERENCE-2026-10-24
- Policy version: option-b-successor-v1
- Authorization basis: one-time user authorization in the attached task dated 2026-10-24
- Effective boundary: the first commit containing this policy, approval record, validator, and regression tests
- Historical effect: no retrospective changes
- Reference Host choices: Claude Code, Codex
- Gate 4 threshold: unchanged
- Gate 5 disclosure: unchanged
- Automatic Reference switching: forbidden
- Historical verdict changes: forbidden
- Standing authority: none

## Scope and authority

This amendment is authorized for the single purpose and scope stated above. The
authorization record is [`option-b-reference-approval.md`](option-b-reference-approval.md).
Its boundary is this policy version and the first Git commit that contains this
policy together with the enforcing validator and regression tests. The branch
commit is a candidate boundary; it does not make this policy part of a published
or accepted v1.0 release. No rule in this file authorizes a later amendment or a
future general Skill expansion.

For an RC whose governing boundary predates this successor, the existing Reference
Host assignment remains in force. This policy applies only to an RC that identifies
this successor ID and version in its Reference designation record. Earlier RCs,
Host Acceptance Records, verdicts, review decisions, and archived packages keep
their recorded scope and status.

## C01 — Reference qualification

An applicable future RC MAY designate Claude Code or Codex as its one Reference
Host. No other host becomes eligible through this amendment. The selection is per
RC and grants neither host a compatibility verdict.

## C02 — Unique designation

Each applicable RC MUST have exactly one durable Reference designation, using
[`rc-candidate-reference.md`](rc-candidate-reference.md). It MUST identify the RC
version, this successor ID and version, a unique designation ID, the Reference
Host, and the other eligible Host's continuing Candidate role. The record MUST be
bound to the RC baseline and evidence package when those exist. A missing,
duplicated, contradictory, or untraceable designation leaves the RC blocked.

## C03 — Designation timing

The Reference Host choice MUST be fixed before the first formal acceptance arm.
Before that arm, the exact host version, model identity, provider and endpoint
identity, Skill loading mode, repository commit and tree, and evidence boundary
MUST also be recorded. Preparation checks are not formal acceptance arms. A failed
preparation check does not permit automatic reselection. A new designation requires
a separately recorded decision before any formal arm for that new RC boundary;
timestamps MUST NOT be backfilled. The preflight choice is immutable for that RC.
Finalize the combination only after observing its preparation evidence, record
`Finalized at` with a timezone, and commit it before an arm starts. The baseline
commit/tree identifies the tested product; the later designation commit records
that baseline without requiring a self-referencing Git SHA. A changed finalized
combination needs a new RC version, not reselection within the same RC.

## C04 — Gate 4 binding

Gate 4 MUST use an `accepted` or `accepted-with-residuals` Host Acceptance Record
for the Reference Host designated for that exact RC. The accepted record and every
supporting run MUST bind to the same RC version, successor ID, designation ID,
Reference Host, host version, model, loading mode, commit/tree, and approved
evidence/review receipts. Existing dimensions, scoring thresholds, evidence rules,
trusted-index requirements, and independent-review requirements remain unchanged.
An incomplete binding cannot satisfy Gate 4.

## C05 — Gate 5 and other Hosts

The other eligible host remains a Candidate Host for that RC. When Codex is the
Reference, Claude Code remains a Candidate; when Claude Code is the Reference,
Codex remains a Candidate. Existing requirements to record a Candidate Host's
accepted status or explicitly disclose its `unverified` status remain in force.
Gemini CLI, GitHub Copilot, and any other host retain their existing roles and
disclosures. Candidate acceptance remains desirable but is not itself a Gate 4
substitute or an additional RC gate.

## C06 — Run and evidence binding

Each formal RC run MUST carry an explicit RC binding in its run receipt. That
binding includes RC version, successor ID, Reference designation ID, Reference
Host, designation-record digest, and the Git tree for the run. The run receipt's
existing fields bind exact Host type, version, model, loading mode, commit, run ID,
timestamps, and raw evidence. Observation events MUST cite evidence for host
version, model identity, provider identity, and endpoint identity. The independent
review receipt and operator-approved evidence index MUST cover the resulting run
and artifacts. A requested model alias, configuration label, provider string,
endpoint string, or hash alone does not prove the upstream model or actual runtime
identity. Unknown identity stays unknown and blocks a formal arm that requires it.
The run schema and observation payload are defined in the
[evidence integrity contract](../evaluation-evidence-integrity.md). Candidate
records use the explicit `candidate` evidence role and bind the RC decision without
claiming that their own identity must equal the Reference combination.

Installation Hash B and the existing C2 installation/fixture isolation checks are
preconditions for applicable formal arms, not evidence from this candidate's
maintenance checks. This successor changes neither C2 nor Phase 15's local
authorized-operation set and adds no C2 probe arm. Apply the existing procedure's
required checks, disclose their exact scopes, and do not infer them from `CURRENT`.

## C07 — Historical isolation

The successor MUST NOT rewrite or promote a historical verdict, role, Host
Acceptance Record, finding, or archived evidence. Historical material cannot be
copied, relabeled, or resealed to satisfy a new RC. The existing evidence-history
policy and trusted operator index remain authoritative for their scopes.

## C08 — Forward effectiveness

The policy version, authorization basis, and effective Git boundary are identified
in the policy and approval record. It applies only to RC boundaries that contain
or explicitly bind this effective successor. It does not amend prior RCs or
acceptance results. The first commit containing the policy, its approval record,
the enforcing validator, and regression tests is the effective branch boundary;
the exact commit is established by Git history after that commit is created.
Pushing a candidate branch does not merge this policy into `main`, publish a
release, or satisfy any acceptance gate.
