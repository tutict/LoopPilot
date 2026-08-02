# Validation

LoopPilot has no runtime dependency. The tools in this document are maintenance-only
checks for repository syntax and structure; they do not establish behavioral or host
compatibility.

## Static Checks

Create a temporary Python environment outside the repository, then run:

```text
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/validate.py
git diff --check
python <skill-creator>/scripts/quick_validate.py .
```

`scripts/validate.py` uses PyYAML rather than a handwritten YAML parser. It checks
required files, Skill frontmatter, YAML mappings and duplicate keys, Markdown code
fences, final newlines, trailing whitespace, relative links, the declared Skill word
range, and extractable Mermaid blocks. It also validates `AGENTS.md` and
`.looppilot/` shared-state status, inactive-template truthfulness, delegation and
Task Contract lifecycles, explicit authority, review identity, revision budgets,
required Review Results, and obvious credential assignments.

The protocol extension checks Checklist statuses, item IDs, integrated-only
checkmarks, observed evidence, completed criteria, and budget-stop recovery fields.
It checks Research Brief status, source provenance, dates or versions, conflicts,
findings, and the local-verification boundary. It also checks research and Skill
assignment fields, observed Skill availability, forbidden selections, authority
notes, Standards and Spec decisions, conjunctive approval, and observed evidence.

The Loop Engineering extension checks that the inactive Project template exists,
contains every required Project Engineering Context heading, includes a blank
Engineering Concern Matrix and Architecture Profile, remains inactive, and contains
no obvious credential assignment. It requires the architecture documents, canonical
Loop definition, both protocol modes, state sources, and honest named-host claims.

The Phase 2 Full Loop extension checks five inactive template files; Loop Map,
Contract, Task, and Finding enums; stable identifiers; duplicate IDs; closed-only
checkmarks; Closure and Checkpoint evidence; honest commit exceptions; mandatory
review axes; Task lifecycle compatibility; Finding dispositions; role authority;
and Checklist projection discipline. It validates fixed structures and explicit
invariants without executing transitions or changing a Ledger.

The Phase 3 extension checks six inactive detail templates and their protocol:
Worker Delivery scope and evidence honesty, Task-level Readiness vocabulary,
included and excluded integration inputs, mechanical versus semantic conflict
authority, Review types and dual-axis boundaries, Finding evidence and status-source
discipline, scoped Rework and revision budgets, Reviewer reverification, three-layer
Acceptance, five Barriers, commit authorization, Checkpoint honesty, and Closure
projection. It rejects explicit contradictions without deduplicating Findings,
inferring severity, assigning work, executing review, merging, committing, or
changing authoritative state.

The 22 Phase 1, 65 Phase 2, and 113 Phase 3 regression cases mutate repository
fixtures and invoke only the public validator CLI. All tests exercise the public entry point:

```text
python scripts/validate.py --root <fixture>
```

The Phase 4 extension adds 72 public-entry cases for three inactive recovery
templates, Checkpoint and Resume status rules, exact Resume Point actionability,
compaction boundaries, current-reality and permission revalidation, single Recovery
authority, and Budget Stop invariants. At that boundary the observed full
repository suite contained 364 tests.

The Phase 5 extension adds 130 public-entry cases for four inactive Project Closure
templates, Goal-to-Evidence structure, Cross-Loop Validation, Project-level Review,
three-layer Project Acceptance, remediation Loop routing, Release Readiness,
independent execution authority, the Final Checkpoint, the Final Delivery Report,
and Project status-source discipline. At that boundary the observed full
repository suite contained 494 tests.

The Phase 7 extension adds at least 76 distinct public-entry cases for evidence
levels, Mode Selection, Artifact Budget, escalation, incident classification,
risk-loaded specialist Review, load profiles, architecture proportionality, and
freeze invariants. At its implementation boundary, the Phase 7 focused suite
contained 89 tests and the observed full repository suite contained 583 tests.

The Phase 9 extension adds 175 public-entry cases, including an explicit 76-case
behavior matrix. The focused suite contains 175 tests, and the observed full
repository suite contained 758 tests at that boundary.

The Phase 11 extension reads current Full Loop authorities, explicit derived
projection tables, actual Git HEAD when available, and the finite Closure snapshot.
It compares status, owner, revision, Finding state, Git boundary, Integration,
Review, Closure, and Checkpoint values through the public entry point only. Review
reports whose `Status` is `superseded` are excluded from the current Review
decision, so reverification rounds do not block Closure. A recorded Git boundary
is accepted when it is the current HEAD or one of its ancestors, so a committed
snapshot stays valid while fabricated or foreign SHAs are rejected; whether an
ancestor boundary is still recent enough for its purpose remains Reviewer
judgment, not a machine decision. A supporting
artifact may declare a lifecycle authority line only when it names the canonical
authority file; naming any other owner is a competing-authority error. When a
repository contains a real Full Loop instance, its per-Loop `TASK-LEDGER.md` and
`FINDING-LEDGER.md` are expected authorities rather than forbidden Ledger
artifacts; this repository itself remains instance-free. It never
changes files, selects Mode, closes state, creates Findings, accepts a Project, or
schedules Agents. A legacy Closure without the new section passes with a migration
warning; once a snapshot or projection is declared, available exact values are
enforced. Lightweight projects without real Full Loop instances are unaffected.

The same extension rejects a canonical lifecycle assertion name written into a
supporting `.looppilot/` artifact outside a declared `## Lifecycle Projections`
or `## Lifecycle Consistency` section. Such a copy carries no source location,
no commit boundary, and no derived label, so it is invalid rather than merely
undocumented. This check runs on every repository, including a Lightweight one
with no `.looppilot/loops/` directory, and skips inactive templates and the
authority files themselves. It matches the declared assertion grammar only; it
does not judge whether undeclared narrative prose is stale, which stays Reviewer
work.

The validator reads repository files only. It does not inspect environment
variables, browse the web, scan host Skill directories, count tokens, or print
credentials.

The Cross-Host Acceptance extension checks the inactive Host Acceptance Record
template and any real record under `evaluations/`: required fields and their
values, `YYYY-MM-DD` dates, the four-value verdict enum, the eight dimension rows
and their result enum, cited evidence for every `pass` or `partial` dimension,
duplicate dimension rows, and the constraint that a failed dimension forces the
`rejected` verdict rather than hiding under `unverified`. For an `accepted` or
`accepted-with-residuals` verdict it additionally checks a bare 40-character
lowercase commit, referenced evaluation runs, scenario coverage naming both a
Lightweight-shaped and a Full-Loop-shaped fixture, a trace author distinct from
the independent reviewer, the lowest critical rubric score at 2 or higher, and
honest residual disclosure. Record detection matches the `Host Acceptance Record`
title even when it is qualified with the evaluated combination, and a file under
`evaluations/` that declares a verdict without that title is reported rather than
skipped. It validates record structure only; it does not run a host, score a
trace, or grant a verdict.

The evaluation templates additionally declare a Scenario ID, prompt and input
boundary, evidence links, reviewer decision, and unverified limitations for each
run, and the Host Acceptance Record template declares Scenario IDs and unverified
limitations. Those additional fields are template-declared disclosure confirmed
by an independent reviewer; the validator enforces the record fields listed
above and does not yet check them. `docs/release/v1.0-rc-checklist.md` is a
required repository file, so the Release Candidate gates cannot be silently
deleted; its ticks are not validated, because the checklist is not acceptance.

## Mermaid Rendering

Extract every diagram to a temporary directory and render it with the pinned CLI:

```text
python scripts/validate.py --extract-mermaid .tmp/mermaid
for diagram in .tmp/mermaid/*.mmd; do
  npx --yes --package @mermaid-js/mermaid-cli@11.16.0 mmdc -i "$diagram" -o "${diagram%.mmd}.svg"
done
```

Confirm every render exits successfully and every SVG is non-empty. Keep temporary
sources and outputs outside commits.

## Continuous Integration

The `Validate` GitHub Actions workflow repeats the Python tests, static validator,
real YAML and duplicate-key checks, every extracted Mermaid render, output-size
checks, and `git diff --check` on pushes and pull requests. It does not publish
generated artifacts, perform live research, scan host Skills, or calculate real
tokens. A local pass does not imply a remote workflow pass.

## Validation Boundary

These checks do not measure implicit activation accuracy, completion behavior,
replanning quality, or compatibility with a named host. Record such results only
from observed evaluation traces. Static checks also do not prove real Agent
creation, delegated-session recovery, Reviewer independence, concurrent isolation,
distributed locking, cancellation, automatic merge behavior, or parent outcomes.

They also do not prove Full Loop operation on a real Project, automatic
Project-to-Loop decomposition, business-complexity judgment, dynamic Reviewer
selection, automatic architecture-pattern choice, Commit and Checkpoint recovery,
or the Project Closure release flow.
They do not prove real network research, installed-Skill discovery on Codex, Gemini
CLI, or GitHub Copilot, automatic Skill-selection accuracy, real remaining-token
reads, context-pressure judgment, live budget stop and resume, or actual
dual-Reviewer independence. Those claims require observed host traces.

Phase 2 static checks also do not prove real Loop grouping, Grouping Rationale
quality, Task DAG generation, concurrent multi-Agent Ledger updates, Finding and
Rework closure, Integration Records, Loop Closure, automatic context recovery, or
commit and Checkpoint recovery. Project Closure, named-host compatibility, and A/B
behavior evaluation remain unverified.

Phase 3 static checks also do not prove real Worker Delivery behavior, multi-Agent
integration, concurrent conflict handling, Reviewer independence, severity
judgment, Finding deduplication accuracy, automatic Rework creation,
revision-budget stopping, automatic Loop Closure, commit-to-Checkpoint recovery,
context recycling, or Project Closure.

Phase 4 static checks also do not prove real token or context-pressure measurement,
automatic compaction or Checkpoint creation, automatic session or Agent takeover,
cross-session or cross-Agent recovery, automatic stale correction, optimal Must
Load selection, Resume Point generation quality, Git conflict recovery, concurrent
recovery, Commit-to-Checkpoint effectiveness, context reclamation, Project Closure,
named-host compatibility, or A/B behavior. Five recovery diagrams and all other
Mermaid blocks are syntax evidence only.

Phase 5 static checks also do not prove real Project Closure, automatic mandatory
Loop judgment, automatic Goal-to-Evidence Mapping or Requirement coverage,
cross-Loop test execution, Finding creation or routing, remediation Loop creation,
Project Reviewer independence, Project Acceptance generation quality, Release
Readiness judgment, version selection, tag or release creation, deployment,
migration, gray traffic, rollback, Final Delivery Report generation or recipient
usability, user acknowledgement, Final Checkpoint recovery effectiveness,
named-host compatibility, remote workflow results, or Phase 6 A/B behavior. Phase 5
and later diagrams, including every repository Mermaid block, are syntax evidence
only.

## Phase 7 Validation Boundary

Phase 7 adds public static checks for evidence levels, the Mode Gate, Lightweight
Artifact Budget, escalation, Execution Infrastructure Incidents, risk-loaded
specialists, load profiles, migration status, and freeze invariants. At the Phase 7
boundary, the checks did not inspect later EXP-005 or EXP-006 evidence. The checks
do not select a mode, score runtime risk, create a Loop or Finding, schedule a
Reviewer, read MMGH, analyze Git history, calculate tokens, accept risk, or prove
Full Loop superiority. Mermaid rendering and YAML parsing are evidence of syntax
only. Phase 9 records observed EXP-005 and incomplete EXP-006 evidence; strict A/B
comparison with archived final scoring, production behavior, automatic selection,
all-host compatibility, and security or data certification remain unverified.

## Phase 11 Validation Boundary

Phase 11 static checks demonstrate exact parsing and mismatch rejection for the
declared fixture format. They do not prove semantic contradiction detection,
optimal projection selection, automatic migration, real Reviewer independence,
cross-host behavior, longitudinal governance, production release, or deployment.
Semantic prose and acceptance interpretation remain Reviewer work. Missing Git
metadata is disclosed rather than fabricated.

## Cross-Host Acceptance Validation Boundary

The Cross-Host Acceptance checks validate record structure and verdict
constraints from repository files only. They do not execute an evaluation on any
host, observe activation, measure rubric scores, verify reviewer independence,
or prove compatibility with Claude Code, Codex, Gemini CLI, GitHub Copilot, or
any other host. A structurally valid record is a disclosure format, not
compatibility evidence; the evidence lives in the referenced evaluation runs.

## Phase 9 Validation Boundary

Phase 9 adds at least 76 public-entry fixture cases for baseline attribution,
Verification Surface inventory, Product Risk and Coordination Necessity,
specialist-reviewed Lightweight, delegation fallback, verifiable claims, artifact
accounting, technology-neutral examples, Final-Assignment evidence limits, and
freeze preservation. The checks inspect repository structure only. They do not
select a mode, execute Workers, verify a product baseline, run experiment arms,
infer test discovery, validate a dynamic holdout, score a comparison, or turn an
incomplete control archive into evidence.
