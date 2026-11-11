# Evaluation Evidence Integrity

This is a maintenance validation contract, not a host runner, scorer, authority
issuer or acceptance grant. It implements the existing per-run disclosure and
referenced-evaluation requirements in the cross-host acceptance specification.
No verdict, critical-score threshold, protocol role or release permission changes.

## Threat and Trust Boundary

An evaluation author may supply or alter the submitted package. The verifier and
its operator-approved evidence index are trusted inputs, separate from that package.
Run the reviewed validator from a trusted source when inspecting an untrusted tree.
The operator must supply the index outside the scanned repository and independently
pin its exact raw SHA-256. The validator never discovers or generates that index.

A self-consistent package plus self-computed hashes is NOT provenance. A package
without an approved run receipt and corresponding approved review receipt fails.
Changing the index requires a new explicit trusted pin; a package-local index fails
even if its contents and hash are self-consistent. Neither a path nor a hash alone
establishes why the operator trusts the capture/review authority.

The trusted capture producer is responsible for recording actual public run events;
the independent reviewer is responsible for the semantic adequacy of the evidence
and limitations. Mechanical checks cannot detect a dishonest trusted authority,
prove a person's independence, or infer omitted real-world events. Such failures
are trust-boundary failures, not grounds to call arbitrary self-authored data true.
No host behavior is established by a successful maintenance check.

## Four Artifact Classes

- **Inert templates:** exact files under `evaluations/templates/`. Required labels
  and all rubric rows must exist, but instance identity, evidence and score fields
  remain blank. They are not evaluated runs.
- **Historical evidence:** exact paths and normalized-content hashes pinned in the
  reviewed `scripts/evaluation_history.json` policy, plus a raw-byte SHA-256 for
  each same path. The normalized digest preserves the legacy comparison rule; the
  raw digest detects byte-only changes such as a BOM or line-ending rewrite.
  Existing files are not rewritten or upgraded. They remain historical/unverified
  and cannot satisfy a new accepted record. Modification, deletion or extending an
  archived run fails validation.
- **New evaluation packages:** a directory named for its Evaluation ID, containing
  `environment.md`, `prompt.md`, `trace.md`, `score.md`, `run.json`, `review.json`,
  and the declared local scenario/raw evidence files. Incomplete or unknown new
  artifacts are rejected rather than silently ignored. This is a publication
  boundary: retain unfinished capture outside the published evaluation tree until
  its limitations and evidence are fully assembled; do not invent missing evidence.
- **Acceptance summaries:** existing Host Acceptance Record format. An accepted
  summary additionally needs an approved record hash and validated sibling packages
  for every Evaluation ID; the summary does not replace their evidence.

## Operator Index Schema

JSON object with exactly `schema_version: 1`, `runs`, and `records`:

- `runs` maps a unique run ID to `run_sha256` and `review_sha256`, both raw SHA-256.
- `records` maps a repository-relative accepted-record path to its raw SHA-256.
- No `verified: true`, automatic approval, package-supplied policy, or fallback trust.

```text
python <trusted-source>/scripts/validate.py --root <repository> --evidence-index <operator-store>/approved.json --evidence-index-sha256 <independently-approved-sha256>
```

With only pinned historical artifacts, normal repository validation needs no index
and reports that no new validated run exists. That PASS does not close P11-A4 or
constitute acceptance. A new run/accepted claim without the index fails closed.

## Run and Review Receipts

Non-RC `run.json` uses `schema_version: 1` and exactly these fields (unknown or
duplicate JSON keys and unsupported schema versions fail):

- `schema_version`, `run_id`, `evaluation_id`, `scenario_id`, `scenario_shape`;
- `scenario_path`, `scenario_sha256`;
- `host`, `host_version`, `model`, `commit`, `loading_mode`, `trace_author`;
- timezone-aware `started_at`, `ended_at`, `status`, integer `exit_code`;
- `trace_path`, `trace_sha256`, and an `evidence` map of local paths to raw SHA-256.

IDs are bounded strings. The commit is a 40-character lowercase hex boundary.
Shape is `lightweight` or `full-loop`; status is `completed` or `failed` and agrees
with exit code. The local scenario JSON has `schema_version`, `scenario_id`, `shape`,
`description`, `input`, and `expected_output`; identity and shape must match the run.
A named or numbered scenario is pinned through its preserved definition, not inferred
from an arbitrary filename. A capture producer must preserve the actual exercised
scenario definition, not substitute a convenient same-named description.

The public trace is JSONL. Every event has exactly `id`, `run_id`, `kind`, `artifact`,
and `sha256`. IDs are unique; kind is `input`, `result`, or `observation`; input and
result are required. Each event refers to a hashed artifact in this run's evidence
map. Preserve original public evidence, not private reasoning, behind those events.

New `review.json` receipts use `schema_version: 2` and exactly `run_id`,
`evaluation_id`, `run_sha256`, `reviewer`, `decision`, `artifacts`, and `disclosures`.
The receipt binds the exact four Markdown hashes and run receipt. Non-RC run,
scenario, and operator-index schemas remain version 1. RC runs use the version-2
extension below; historical files are never upgraded here.
A version-1 hash-only review lacks the required state evidence and cannot authorize
new publication. Producers must assemble and separately approve a complete version-2
receipt rather than infer missing disclosures.

Historical replay packages are the exception to the base review shape. A replay
package whose Evaluation ID is registered in
`docs/evaluations/historical-replay-matrix.json` uses review schema version 3:
the base fields plus `review_axes` and `independence`. The four axes are exactly
`Spec`, `Standards`, `Implementation Quality`, and `Verification & Evidence`.
Spec and Standards are always applicable. The latter two may be
`not-applicable` only with substantive scope evidence. Every applicable axis
must pass before a replay package can support acceptance. The independence block
declares distinct trace-author and reviewer operator/session identities. This is
a mechanical separation check and does not certify organizational independence.

Each replay package also registers
`evidence/historical-lineage.json` in the run evidence map and binds one public
observation event to it. The lineage must name an existing historical package,
one matrix pair and arm, the exact original Host/version/model combination, the
Scenario ID and shape, the known historical gaps, and the reproduction status.
Retries use a new Evaluation ID and run ID, name the immediately preceding
failed run, and are limited to HTTP 429, timeout, or Host-unavailable incidents;
two retries is the maximum. A `not-reproduced` lineage is allowed only for a
failed run with a substantive reason. These checks preserve the distinction
between an incomplete execution and a product behavior result.

Current formal packages use Review schema version 4 and are separate from
historical replay lineage. They register
`evidence/current-acceptance-lineage.json`,
`evidence/current-validation-boundary.json`, and a de-identified
`evidence/blind-review-packet.md`. The v4 receipt binds the packet SHA-256, a
condition guess and confidence, and timezone-qualified Review, guess, and reveal
times; the guess must precede reveal. The mechanical check cannot prove human or
organizational independence. `FL-1R` also binds the exact checkpoint path and hash
from a completed `FL-1` package.

The current boundary is observed afresh for the formal stage. It requires
`CURRENT` install provenance, `C2_CLEAN`, a passed permission preflight, and a
matching Host/version/Model/commit across the four arms. A prior Host boundary
cannot satisfy this gate. EVAL-004 historical pairs are loading probes, not
behavioral comparisons; they preserve `evidence/loading-observation.json` and
report loading state separately without behavioral rubric scores.

`disclosures` contains exactly:

- `outcome`: `completed` or `failed`, equal to the run receipt and Score outcome;
- `limitations`: an object with `state` (`unverified`, `unresolved`, or `resolved`),
  substantive `text`, and `evidence` (a same-run Markdown event reference);
- `score_caps` and `critical_failures`: explicit `none` or substantive disclosure,
  equal to the corresponding Score fields.

Environment and Score project `Limitation state` and `Unverified limitations` from
that approved limitation object. Both state and text must agree across the receipt
and documents; changing a projection to resolved/all-verified cannot conceal an
unresolved receipt. These are local disclosure states, not protocol lifecycle states.
Decision remains `accept`, `accept-with-residuals`, `reject`, or `not-reviewed`.
Reviewer identity must differ from the trace author; approved bytes and identity
separation do not themselves prove organizational independence.

The validator hashes and parses one bounded in-memory byte snapshot per file.
References must be local, package-relative, non-indirect, and digest-matched.
Unknown files, duplicate fields/keys, missing event anchors and obvious placeholder
values fail. Record classification and validation share the same duplicate-rejecting
field parser; spaces, multiple spaces and tabs after a bullet cannot downgrade an
accepted record out of its approval checks. Caps and critical-failure fields require
an explicit `none` or substantive disclosure. A result applies to those observed bytes, not future mutations.

## Disclosure and B7 Enforcement

All four documents must share Evaluation ID and Scenario ID. Environment/run host,
version, model, commit, loading mode and timestamps must agree. The Exact User Input section must match the preserved scenario input, and a captured
input event must bind the same UTF-8 text (CRLF is normalized; one terminal LF is
permitted for a line-oriented capture). In a run's prompt document, metadata ends at
`## Exact User Input` followed by a blank line. The preserved scenario input is
matched by content and length, followed by a blank line, `## Input Boundary`, and
another blank line. Headings and metadata-looking bullets inside that exact input
are source data, not record structure; leading/trailing input whitespace is not
stripped. Scenario description, input and expected output must be non-empty text,
not pass a disclosure-word blacklist: a task may legitimately discuss TODO comments
or fabricated evidence. Only a completely validated package provides a structural
Markdown view masking that exact input span. Public whitespace/link/fence checks and
Mermaid extraction use that view; original raw bytes still must match the approved
snapshot. Outer metadata, the Input Boundary, ordinary documents, unapproved packages
and changed bytes receive no exemption. This is structural data separation, not a
keyword exception or a global Markdown skip. Record detection also excludes the
preserved input of a package prompt, but never exempts it from receipt validation.
A real acceptance record renamed `prompt.md`, a missing run receipt, or an
acceptance claim in the prompt's actual header/boundary still fails validation. Fixture reference and prompt/trace variant
must correspond. Environment tools/state, granted authority and material constraints
require explicit disclosures, not omitted or empty labels. Both limitations fields
must match the substantive approved receipt text and explicit state. Disclosure
validation rejects empty values and whole-value placeholder shapes, not forbidden
words occurring anywhere in a sentence. Substantive disclosure has at least twelve
characters and is not composed solely of placeholder labels such as `TODO limitations`.
A concrete `TODO investigate gateway retry evidence` can disclose pending work; an
unquoted leading `TODO` is a pending-work marker and cannot accompany a resolved
receipt state. Mentioning TODO, missing evidence, errors or fabricated output inside
an otherwise substantive report is not itself grounds for rejection.

Truthful failure/unverified reports remain publishable when outcome, state, text and
evidence agree. A successful-completion projection over a failed run, missing review
receipt or event, or resolved projection over unresolved receipt fails deterministically.
Free prose is not parsed into arbitrary natural-language truth claims: producers must
express machine-checkable completion/limitation states in the declared fields, and
the trusted independent reviewer remains responsible for semantic adequacy and honest
capture. Hashes and length checks alone do not prove that trust assumption.

Historical score files retain their pinned version-1 shape with ten dimensions;
they are never rewritten or rescored. Every new score file declares
`Score schema version: 2` and contains the eleven current dimensions, including
**Code quality**. Its `Code quality applicability` is `applicable` or
`not-applicable`, with a local event link to the separately hashed
`evidence/code-quality-applicability.json` inventory. The inventory has schema
version 1, run/evaluation/scenario identity, the same applicability value, and a
list of code-artifact paths from the run evidence map. `applicable` requires at
least one listed artifact; `not-applicable` requires an empty list. The independent
reviewer binds this inventory through the existing run, review, and operator-index
receipts and confirms that the inventory matches the preserved run artifacts.

For deterministic structural coverage, the validator compares the inventory with
registered run evidence paths using the maintained source-code extension set in
`scripts/evaluation_evidence_validation.py`. This detects omissions and unsupported
applicability declarations for those registered source files; the independent
reviewer remains responsible for semantic completeness (for example, code embedded
in non-source files or generated representations).

Trace and score Evidence links require actual local trace event anchors. Every
numeric score is 0–3 and has event-level support. The Code quality row is numeric
when applicable; `not-applicable` is accepted only for that row when its reviewed
inventory contains no code artifacts. `Applicable dimensions` equals the number
of numeric rows, and `Total` is their sum. Explicit `not-evaluated` scores remain
allowed only with a `not-reviewed` disposition and are never acceptance-eligible.
The four existing critical dimensions remain unchanged. Caps and critical failures
remain disclosed; a valid report of failure is not a successful host result.

An accepted summary must bind to approved run packages with matching host/model/
commit/loading mode/author/reviewer, exact Scenario IDs, actual shape coverage, real
linked event evidence, and the minimum critical score recomputed across its traces.
Critical dimensions still require at least 2 for acceptance. The summary cannot
silently discard reviewer residuals. Its own bytes must be in the pinned operator
index. Mandatory summary limitations receive the same substantive-content checks;
approval does not make bare TODO or TODO limitations sufficient. Concrete unresolved
TODO limitations are permitted and do not imply all states verified. A failed run is
valid evidence but is not eligible to support an accepted summary. No Host Acceptance
record, verdict rule or release gate is changed by these maintenance checks.

## Option B RC Run Extension

Applicable formal RC runs use `schema_version: 2`, all version-1 run fields, and
exactly two additional objects: `rc_binding` and `runtime_identity`. They retain
the existing version-2 review and externally pinned operator index; neither
self-authored identity data nor a Git commit grants trust or acceptance.

`rc_binding` has exactly:

- `rc_version`, `successor_id`, `successor_policy`, `policy_sha256`;
- `designation_id`, `designation_record`, `designation_sha256`, `designation_commit`;
- `reference_host`, `evidence_role` (`reference` or `candidate`);
- `effective_successor_commit`, `effective_successor_tree`, `run_commit`, `run_tree`.

The named [successor](release/option-b-reference-successor.md) and its approved
policy version govern the RC. Digests are raw SHA-256; Git identities are full
lowercase 40-character SHAs. The first synchronized commit must contain the policy,
approval, public validator integrations, and Option B regressions; no parent may
already contain that complete set. The tested baseline must descend from that
boundary, and its tree must match Git. A later designation commit contains the
exact finalized record and its baseline commit/tree. Both commits must be present
in current history. The designation records timezone-aware `Finalized at`, and
its commit must precede the arm's `started_at`; the effective boundary precedes
finalization. Git timestamps check recorded consistency, not independently trusted
wall-clock truth. Producer and independent Reviewer must establish real timing.
Git reads ignore replacement objects so replacement refs cannot forge the recorded
ancestry, trees, policy, or designation contents.

The choice is immutable for the same RC, finalized before arms, and never chosen
after results. A product baseline precedes its designation commit to avoid a
self-referencing commit SHA. The committed designation snapshot binds the run;
when a later RC uses the same current-record path, earlier RC receipts retain
their own committed snapshots. No old accepted record is rewritten or upgraded.

`runtime_identity` contains exactly `configured`, `observed`, and `event_ids`.
Configured has `provider`, `model`, and `endpoint` declarations; observed adds
`host_version` to those three actual identity fields. Every observed field maps
to an observation event ID in `event_ids`. Unknown or placeholder identity blocks
formal acceptance. Requested model aliases may differ from the observed upstream
model; the Reference's exact configured and observed combination must match its
finalized designation. Candidate runs preserve their own observed combination and
use `candidate`; they cannot satisfy the Reference gate.

Each identity observation event points to a hashed local JSON payload containing
exactly `schema_version: 1`, `kind: runtime-identity`, `run_id`, timezone-aware
`observed_at` within the arm, `basis: actual-runtime-observation`, `identity`,
`source_artifact`, and `source_sha256`. Identity contains `host`, `host_version`,
`provider`, `model`, and `endpoint` matching the receipt. The distinct source must
be a registered hash-bound local public capture artifact. Shared observation events
may cover multiple identity fields. A configuration file or provider label alone
does not establish the payload's semantics; trusted capture and independent review
must verify that its source identifies the actual upstream runtime. The validator
checks declared provenance and consistency and never certifies a model by itself.

RC acceptance summaries must disclose the RC version, successor and policy,
designation ID/path/digest, Reference Host, evidence role, provider, and endpoint.
Every linked package must be version 2 and match those bindings and the existing
summary identity/reviewer constraints. RC receipts cannot be hidden beneath a
non-RC summary, and version-1 runs cannot support an RC summary. Only qualified
`reference` records for the selected Host can support Gate 4. Thresholds, shape
coverage, B7, residual disclosure, independent review, and historical restrictions
remain unchanged. Hash B and applicable C2 installation/fixture checks are formal
preconditions, not established by this receipt schema or maintenance suite.

Environment RC/configuration fields, when included, are projections and must
equal the authoritative v2 receipt. Identity-evidence fields must link to their
specific runtime observation events. A Candidate summary's `Reference Host`
still describes the RC choice and must match the receipt even though its own
`Host` describes the different evaluated Candidate.

## Maintenance Testing and Historical Boundaries

Test-only fixture helpers capture an actual deterministic local Python subprocess,
then construct synthetic review/index data in a separate temporary operator store.
They are not production approval tooling and do not establish Claude, model, Skill
loading or Host Acceptance behavior. Tests also re-pin deliberately malformed test
bytes to prove schema/consistency failures are not merely digest failures.

P11-A4 remediation requires this specification, the enforcing implementation, and
observed positive/negative regressions together. B7 is no longer merely row presence
when those checks run; it still makes no runtime-behavior claim. Historical Phase15
B7 notes remain unchanged as historical provenance. Gate 4 and Gate 6 require their
own authorized evidence and are not closed here.
