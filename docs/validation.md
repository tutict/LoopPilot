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
authority, and Budget Stop invariants. The complete suite contains 364 tests.

The Phase 5 extension adds 130 public-entry cases for four inactive Project Closure
templates, Goal-to-Evidence structure, Cross-Loop Validation, Project-level Review,
three-layer Project Acceptance, remediation Loop routing, Release Readiness,
independent execution authority, the Final Checkpoint, the Final Delivery Report,
and Project status-source discipline. The complete suite contains 494 tests.

The Phase 7 extension adds at least 76 distinct public-entry cases for evidence
levels, Mode Selection, Artifact Budget, escalation, incident classification,
risk-loaded specialist Review, load profiles, architecture proportionality, and
freeze invariants. The current Phase 7 focused suite contains 89 tests and the
observed full repository suite contains 583 tests.

The validator reads repository files only. It does not inspect environment
variables, browse the web, scan host Skill directories, count tokens, or print
credentials.

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
named-host compatibility, remote workflow results, or Phase 6 A/B behavior. Five
Phase 5 diagrams and all 24 Mermaid blocks are syntax evidence only.

## Phase 7 Validation Boundary

Phase 7 adds public static checks for evidence levels, the Mode Gate, Lightweight
Artifact Budget, escalation, Execution Infrastructure Incidents, risk-loaded
specialists, load profiles, migration status, and freeze invariants. The checks
do not select a mode, score runtime risk, create a Loop or Finding, schedule a
Reviewer, read MMGH, analyze Git history, calculate tokens, accept risk, or prove
Full Loop superiority. Mermaid rendering and YAML parsing are evidence of syntax
only. Strict A/B comparison, second-project replication, production behavior,
automatic selection, all-host compatibility, and security or data certification
remain unverified.
