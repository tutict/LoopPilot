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
  reviewed `scripts/evaluation_history.json` policy. Existing files are not rewritten
  or upgraded. They remain historical/unverified and cannot satisfy a new accepted
  record. Modification, deletion or extending an archived run fails validation.
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

`run.json` has exactly these fields (unknown or duplicate JSON keys fail):

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
The receipt binds the exact four Markdown hashes and run receipt. Run, scenario and
operator-index schemas remain version 1; historical files are never upgraded here.
A version-1 hash-only review lacks the required state evidence and cannot authorize
new publication. Producers must assemble and separately approve a complete version-2
receipt rather than infer missing disclosures.

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

Trace and score Evidence links require actual local trace event anchors. Every
numeric score is 0–3 and has event-level support; all ten current rubric dimensions
must be present once, including **Evidence integrity across agents** and **Authority
continuity**. Total is recomputed. Explicit `not-evaluated` scores are allowed only
with a `not-reviewed` disposition and are never acceptance-eligible. Caps and
critical failures remain disclosed; a valid report of failure is not a successful
host result.

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
