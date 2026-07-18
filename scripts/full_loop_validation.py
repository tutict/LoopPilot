"""Validate Phase 2 Full Loop templates and authoritative state projections."""

from __future__ import annotations

import re
from pathlib import Path

from engineering_validation import CONCERN_ROWS


FULL_LOOP_ROOT = ".looppilot/full-loop"
FULL_LOOP_FILES = (
    f"{FULL_LOOP_ROOT}/README.md",
    f"{FULL_LOOP_ROOT}/LOOP-MAP-TEMPLATE.md",
    f"{FULL_LOOP_ROOT}/LOOP-CONTRACT-TEMPLATE.md",
    f"{FULL_LOOP_ROOT}/TASK-LEDGER-TEMPLATE.md",
    f"{FULL_LOOP_ROOT}/FINDING-LEDGER-TEMPLATE.md",
)
LOOP_MAP_STATUSES = {
    "inactive",
    "active",
    "partially-completed",
    "blocked",
    "completed",
    "cancelled",
    "budget-stopped",
}
LOOP_STATUSES = {
    "planned",
    "contracted",
    "executing",
    "implemented",
    "integrating",
    "integrated",
    "reviewing",
    "reworking",
    "accepted",
    "committed",
    "checkpointed",
    "closed",
    "blocked",
    "failed",
    "budget-exhausted",
    "cancelled",
    "replan-required",
}
CONTRACT_STATUSES = {"inactive", "draft", "ready", "approved", "superseded"}
LEDGER_STATUSES = {
    "inactive",
    "active",
    "blocked",
    "completed",
    "cancelled",
    "budget-stopped",
}
TASK_TYPES = {
    "implementation",
    "contract",
    "research",
    "integration",
    "test",
    "documentation",
    "migration",
    "operations",
    "rework",
    "review-support",
}
FINDING_SEVERITIES = {"blocker", "major", "minor", "suggestion"}
FINDING_STATUSES = {
    "open",
    "triaged",
    "assigned",
    "in-rework",
    "ready-for-review",
    "verified",
    "closed",
    "deferred",
    "risk-accepted",
    "rejected",
    "duplicate",
    "reopened",
}
LOOP_ID_PATTERN = re.compile(r"^LOOP-\d{3,}$")
TASK_ID_PATTERN = re.compile(r"^TASK-\d{3,}$")
REWORK_TASK_ID_PATTERN = re.compile(r"^TASK-\d{3,}-R\d+$")
FINDING_ID_PATTERN = re.compile(r"^FINDING-\d{3,}$")
COMMIT_VALUES = {"yes", "no", "not-applicable"}
EMPTY_VALUES = {"", "none", "pending", "placeholder", "not-evaluated"}

README_HEADINGS = (
    "## Purpose",
    "## When to Use",
    "## When Not to Use",
    "## Template Versus Instance",
    "## Authoritative State Sources",
    "## Template Set",
)
LOOP_MAP_HEADINGS = (
    "## Authority",
    "## Project Goal",
    "## Loop Ordering",
    "## Loops",
    "## Grouping Rationale",
    "## Cross-Loop Dependencies",
    "## Deferred Loops",
    "## Cancelled Loops",
    "## Completion Projection Rules",
    "## Project Acceptance Relationship",
)
CONTRACT_HEADINGS = (
    "## Identity",
    "## Objective",
    "## User and System Outcomes",
    "## Included Changes",
    "## Excluded Changes",
    "## Grouping Rationale",
    "## Engineering Context References",
    "## Business Rules and Invariants",
    "## Engineering Concern Matrix",
    "## Architecture Profile",
    "## Task DAG",
    "## Worker Plan",
    "## Reviewer Matrix",
    "## Integration Strategy",
    "## Acceptance Criteria",
    "## Barriers",
    "## Budget",
    "## Authority",
    "## Risks and Open Decisions",
)
CONTRACT_SUBHEADINGS = (
    "### Mandatory Axes",
    "### Conditional Reviewers",
    "### Functional Acceptance",
    "### Engineering Acceptance",
    "### Delivery Acceptance",
    "### Contract Barrier",
    "### Implementation Barrier",
    "### Integration Barrier",
    "### Review Barrier",
    "### Closure Barrier",
)
TASK_LEDGER_HEADINGS = (
    "## Authority",
    "## Task Summary",
    "## Dependency Notes",
    "## Contract Barrier Status",
    "## Implementation Barrier Status",
    "## Blocked Tasks",
    "## Cancelled Tasks",
    "## Ledger Notes",
)
FINDING_LEDGER_HEADINGS = (
    "## Authority",
    "## Finding Summary",
    "## Severity Summary",
    "## Open Blockers",
    "## Accepted Risks",
    "## Deferred Findings",
    "## Duplicate Relationships",
    "## Review Barrier Status",
    "## Closure Barrier Relationship",
    "## Ledger Notes",
)
SOURCE_INVARIANTS = (
    "`LOOP-MAP.md` MUST be the only authoritative source of Loop status.",
    "`TASK-LEDGER.md` MUST be the only authoritative source of Task status within a Full Loop.",
    "`FINDING-LEDGER.md` MUST be the only authoritative source of Finding status within a Full Loop.",
    "`CHECKPOINT.md` MUST be the only authoritative recovery entry point.",
)


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _plain(value: str) -> str:
    return value.strip().strip("`").strip()


def _field(text: str, name: str, bullet: bool = False) -> str | None:
    prefix = r"^-[ \t]*" if bullet else r"^"
    match = re.search(
        rf"{prefix}{re.escape(name)}:[ \t]*(.*)$", text, re.MULTILINE
    )
    return _plain(match.group(1)) if match else None


def _require_lines(
    text: str, required: tuple[str, ...], location: str, errors: list[str]
) -> None:
    lines = set(text.splitlines())
    for line in required:
        if line not in lines:
            errors.append(f"{location}: missing required heading {line!r}")


def _section_lines(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return []
    result: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        result.append(line)
    return result


def _table(
    text: str,
    heading: str,
    expected_headers: tuple[str, ...],
    location: str,
    errors: list[str],
) -> list[dict[str, str]]:
    table_lines = [
        line.strip()
        for line in _section_lines(text, heading)
        if line.strip().startswith("|")
    ]
    if len(table_lines) < 2:
        errors.append(f"{location}: {heading} requires a Markdown table")
        return []

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip("|").split("|")]

    headers = cells(table_lines[0])
    missing = [header for header in expected_headers if header not in headers]
    if missing:
        errors.append(f"{location}: {heading} missing columns {missing!r}")
        return []
    rows: list[dict[str, str]] = []
    for line in table_lines[2:]:
        values = cells(line)
        if len(values) != len(headers):
            errors.append(f"{location}: malformed row in {heading}")
            continue
        rows.append(dict(zip(headers, values)))
    return rows


def _real(value: str) -> bool:
    return _plain(value).casefold() not in EMPTY_VALUES | {"loop-xxx"}


def validate_full_loop_readme(root: Path, errors: list[str]) -> None:
    location = f"{FULL_LOOP_ROOT}/README.md"
    text = (root / location).read_text(encoding="utf-8")
    _require_lines(text, README_HEADINGS, location, errors)
    for invariant in SOURCE_INVARIANTS:
        if invariant not in text:
            errors.append(f"{location}: missing state-source invariant {invariant!r}")
    for filename in (
        "LOOP-MAP-TEMPLATE.md",
        "LOOP-CONTRACT-TEMPLATE.md",
        "TASK-LEDGER-TEMPLATE.md",
        "FINDING-LEDGER-TEMPLATE.md",
    ):
        if filename not in text:
            errors.append(f"{location}: missing template reference {filename!r}")


def validate_loop_map(root: Path, errors: list[str]) -> None:
    location = f"{FULL_LOOP_ROOT}/LOOP-MAP-TEMPLATE.md"
    text = (root / location).read_text(encoding="utf-8")
    if "TEMPLATE" not in text.splitlines()[0]:
        errors.append(f"{location}: title must identify the file as TEMPLATE")
    _require_lines(text, LOOP_MAP_HEADINGS, location, errors)
    document_status = _field(text, "Status")
    if document_status not in LOOP_MAP_STATUSES:
        errors.append(f"{location}: invalid Loop Map Status {document_status!r}")

    rows = _table(
        text,
        "## Loops",
        (
            "Complete",
            "Loop ID",
            "Title",
            "Status",
            "Depends On",
            "Contract",
            "Closure",
            "Commit Required",
            "Commit Authorized",
            "Commit Result",
            "Checkpoint",
        ),
        location,
        errors,
    )
    seen: set[str] = set()
    for row in rows:
        loop_id = _plain(row["Loop ID"])
        status = _plain(row["Status"]).casefold()
        checked = _plain(row["Complete"]).casefold() == "[x]"
        if _plain(row["Complete"]).casefold() not in {"[ ]", "[x]"}:
            errors.append(f"{location}: Loop {loop_id!r} has invalid checkbox")
        if loop_id.casefold() in {"none", "loop-xxx"}:
            continue
        if not LOOP_ID_PATTERN.fullmatch(loop_id):
            errors.append(f"{location}: invalid Loop ID {loop_id!r}")
        if loop_id in seen:
            errors.append(f"{location}: duplicate Loop ID {loop_id!r}")
        seen.add(loop_id)
        if document_status == "inactive":
            errors.append(f"{location}: inactive template contains a real Loop")
        if status not in LOOP_STATUSES:
            errors.append(f"{location}: invalid Loop status {status!r}")
        if checked and status != "closed":
            errors.append(f"{location}: only a closed Loop may be checked")
        if status == "closed" and not checked:
            errors.append(f"{location}: closed Loop must be checked")
        if status == "closed":
            if not _real(row["Closure"]):
                errors.append(f"{location}: closed Loop requires a Closure reference")
            if not _real(row["Checkpoint"]):
                errors.append(f"{location}: closed Loop requires a Checkpoint reference")

        required = _plain(row["Commit Required"]).casefold()
        authorized = _plain(row["Commit Authorized"]).casefold()
        result = _plain(row["Commit Result"])
        result_folded = result.casefold()
        if required not in COMMIT_VALUES:
            errors.append(f"{location}: invalid Commit Required value {required!r}")
        if authorized not in COMMIT_VALUES:
            errors.append(f"{location}: invalid Commit Authorized value {authorized!r}")
        if required == "yes" and authorized == "no":
            if result != "not-created-not-authorized":
                errors.append(f"{location}: unauthorized required commit must be recorded honestly")
            if status == "closed":
                errors.append(f"{location}: required but unauthorized commit cannot be closed")
        if status == "closed" and result_folded in EMPTY_VALUES | {"not-created"}:
            errors.append(f"{location}: closed Loop requires an honest Commit result")
        if status == "closed" and required == "yes":
            if authorized != "yes" or result_folded in {
                "not-created-not-authorized",
                "not-created-not-required",
                "not-applicable",
            }:
                errors.append(f"{location}: closed required commit needs an observed result")
        if required == "not-applicable" and (
            authorized != "not-applicable" or result != "not-applicable"
        ):
            errors.append(f"{location}: not-applicable commit fields must agree")


def validate_loop_contract(root: Path, errors: list[str]) -> None:
    location = f"{FULL_LOOP_ROOT}/LOOP-CONTRACT-TEMPLATE.md"
    text = (root / location).read_text(encoding="utf-8")
    if "TEMPLATE" not in text.splitlines()[0]:
        errors.append(f"{location}: title must identify the file as TEMPLATE")
    _require_lines(text, CONTRACT_HEADINGS + CONTRACT_SUBHEADINGS, location, errors)
    contract_status = _field(text, "Contract Status", bullet=True)
    if contract_status not in CONTRACT_STATUSES:
        errors.append(f"{location}: invalid Contract Status {contract_status!r}")
    loop_id = _field(text, "Loop ID", bullet=True)
    if loop_id is None:
        errors.append(f"{location}: missing Loop ID field")
    elif loop_id.casefold() not in {"none", "loop-xxx"} and not LOOP_ID_PATTERN.fullmatch(loop_id):
        errors.append(f"{location}: invalid Loop ID {loop_id!r}")
    if contract_status == "inactive" and loop_id and loop_id.casefold() not in {"none", "loop-xxx"}:
        errors.append(f"{location}: inactive template contains an active Contract")
    if _field(text, "Loop Status", bullet=True) is not None:
        errors.append(f"{location}: Loop Contract must not own Loop lifecycle status")
    if _field(text, "Loop status source", bullet=True) != "LOOP-MAP.md":
        errors.append(f"{location}: Loop status source must be LOOP-MAP.md")

    matrix_rows = _table(
        text,
        "## Engineering Concern Matrix",
        ("Concern", "Impact", "Required Work", "Reviewer"),
        location,
        errors,
    )
    matrix_concerns = {
        _plain(row["Concern"]) for row in matrix_rows
    }
    for concern in CONCERN_ROWS:
        if concern not in matrix_concerns:
            errors.append(
                f"{location}: Engineering Concern Matrix missing {concern!r}"
            )

    normalized = _normalized(text)
    for field in (
        "OOP",
        "Dependency Injection",
        "Domain Modeling",
        "Frontend Architecture",
        "Performance Strategy",
        "Rejected Patterns",
        "Branch or worktree",
        "Merge order",
        "File ownership",
        "Conflict ownership",
        "Shared files",
        "Integration task",
        "Context budget",
        "Revision budget",
        "Maximum active Workers",
        "Maximum concurrent conflict groups",
        "Stop conditions",
        "Budget-stop persistence requirements",
        "Modify",
        "Delete",
        "Commit required",
        "Commit authorized",
        "Push authorized",
        "Release authorized",
        "Deploy authorized",
    ):
        if _field(text, field, bullet=True) is None:
            errors.append(f"{location}: missing required field {field!r}")
    if "- Spec Review" not in text:
        errors.append(f"{location}: Mandatory Axes missing Spec Review")
    if "- Standards Review" not in text:
        errors.append(f"{location}: Mandatory Axes missing Standards Review")
    conditional = "\n".join(_section_lines(text, "### Conditional Reviewers"))
    if re.search(r"\b(?:all|every)\b.*\bmandatory\b", conditional, re.IGNORECASE):
        errors.append(f"{location}: Conditional Reviewers must be risk-driven")
    if contract_status == "inactive" and re.search(
        r"^- (?:Commit authorized|Push authorized|Release authorized|Deploy authorized): yes$",
        text,
        re.MULTILINE,
    ):
        errors.append(f"{location}: inactive template must not grant authority")
    if "This template grants no authority." not in normalized:
        errors.append(f"{location}: missing template authority boundary")


def validate_task_ledger(
    root: Path, errors: list[str], task_statuses: set[str]
) -> None:
    location = f"{FULL_LOOP_ROOT}/TASK-LEDGER-TEMPLATE.md"
    text = (root / location).read_text(encoding="utf-8")
    if "TEMPLATE" not in text.splitlines()[0]:
        errors.append(f"{location}: title must identify the file as TEMPLATE")
    _require_lines(text, TASK_LEDGER_HEADINGS, location, errors)
    ledger_status = _field(text, "Status")
    if ledger_status not in LEDGER_STATUSES:
        errors.append(f"{location}: invalid Task Ledger Status {ledger_status!r}")
    rows = _table(
        text,
        "## Task Summary",
        (
            "Task ID",
            "Title",
            "Type",
            "Mandatory",
            "Status",
            "Worker",
            "Dependencies",
            "Delivery",
            "Review Readiness",
            "Rework Of",
        ),
        location,
        errors,
    )
    seen: set[str] = set()
    for row in rows:
        task_id = _plain(row["Task ID"])
        worker = _plain(row["Worker"])
        if ledger_status == "inactive" and worker.casefold() not in EMPTY_VALUES:
            errors.append(f"{location}: inactive template cannot name a real Worker")
        if task_id.casefold() == "none":
            continue
        if "-R" in task_id and not REWORK_TASK_ID_PATTERN.fullmatch(task_id):
            errors.append(f"{location}: invalid Rework Task ID {task_id!r}")
        elif "-R" not in task_id and not TASK_ID_PATTERN.fullmatch(task_id):
            errors.append(f"{location}: invalid Task ID {task_id!r}")
        if task_id in seen:
            errors.append(f"{location}: duplicate Task ID {task_id!r}")
        seen.add(task_id)
        if ledger_status == "inactive":
            errors.append(f"{location}: inactive template contains a real Task")
        task_type = _plain(row["Type"]).casefold()
        if task_type not in TASK_TYPES:
            errors.append(f"{location}: invalid Task type {task_type!r}")
        task_status = _plain(row["Status"]).casefold()
        if task_status not in task_statuses:
            errors.append(f"{location}: invalid Task status {task_status!r}")
        if REWORK_TASK_ID_PATTERN.fullmatch(task_id):
            rework_of = _plain(row["Rework Of"])
            if not TASK_ID_PATTERN.fullmatch(rework_of):
                errors.append(f"{location}: Rework Task requires a base Task ID")

    required_lines = (
        "- Task status authority: `TASK-LEDGER.md`",
        "- Recording authority: Integrator",
        "- Worker may update Ledger: no",
        "- Reviewer may update Ledger: no",
        "- Detailed Task Contracts do not own authoritative Task status.",
    )
    lines = set(text.splitlines())
    for line in required_lines:
        if line not in lines:
            errors.append(f"{location}: missing Task Ledger invariant {line!r}")
    if re.search(
        r"Detailed Task Contracts? (?:own|are|maintain).{0,40}authoritative Task status",
        text,
        re.IGNORECASE,
    ):
        errors.append(f"{location}: Task Contract must not own authoritative Task status")
    if "Integrated Task effect on Loop: none" not in _normalized(text):
        errors.append(f"{location}: integrated Task must not map to Loop closed")


def validate_finding_ledger(root: Path, errors: list[str]) -> None:
    location = f"{FULL_LOOP_ROOT}/FINDING-LEDGER-TEMPLATE.md"
    text = (root / location).read_text(encoding="utf-8")
    if "TEMPLATE" not in text.splitlines()[0]:
        errors.append(f"{location}: title must identify the file as TEMPLATE")
    _require_lines(text, FINDING_LEDGER_HEADINGS, location, errors)
    ledger_status = _field(text, "Status")
    if ledger_status not in LEDGER_STATUSES:
        errors.append(f"{location}: invalid Finding Ledger Status {ledger_status!r}")
    rows = _table(
        text,
        "## Finding Summary",
        (
            "Finding ID",
            "Category",
            "Severity",
            "Status",
            "Reviewer",
            "Affected Task",
            "Rework Task",
            "Decision",
            "Verification",
            "Duplicate Of",
        ),
        location,
        errors,
    )
    seen: set[str] = set()
    unresolved_blockers = 0
    for row in rows:
        finding_id = _plain(row["Finding ID"])
        if finding_id.casefold() == "none":
            continue
        if not FINDING_ID_PATTERN.fullmatch(finding_id):
            errors.append(f"{location}: invalid Finding ID {finding_id!r}")
        if finding_id in seen:
            errors.append(f"{location}: duplicate Finding ID {finding_id!r}")
        seen.add(finding_id)
        if ledger_status == "inactive":
            errors.append(f"{location}: inactive template contains a real Finding")
        severity = _plain(row["Severity"]).casefold()
        status = _plain(row["Status"]).casefold()
        if severity not in FINDING_SEVERITIES:
            errors.append(f"{location}: invalid Finding severity {severity!r}")
        if status not in FINDING_STATUSES:
            errors.append(f"{location}: invalid Finding status {status!r}")
        if severity == "blocker" and status not in {"closed", "rejected", "duplicate"}:
            unresolved_blockers += 1
        if status == "risk-accepted" and "supervisor" not in row["Decision"].casefold():
            errors.append(f"{location}: risk-accepted Finding requires Supervisor Decision")
        if status == "duplicate":
            original = _plain(row["Duplicate Of"])
            if not FINDING_ID_PATTERN.fullmatch(original) or original == finding_id:
                errors.append(f"{location}: duplicate Finding requires original Finding reference")
        if status == "closed" and not _real(row["Verification"]):
            errors.append(f"{location}: closed Finding requires verification semantics")

    blocker_text = _field(text, "Blocker", bullet=True)
    try:
        blocker_count = int(blocker_text) if blocker_text is not None else None
    except ValueError:
        blocker_count = None
    if blocker_count is None:
        errors.append(f"{location}: Severity Summary requires an integer Blocker count")
    elif blocker_count != unresolved_blockers:
        errors.append(f"{location}: Blocker count does not match unresolved blocker rows")
    closure_ready = _field(text, "Closure ready", bullet=True)
    if closure_ready not in {"yes", "no"}:
        errors.append(f"{location}: Closure ready must be yes or no")
    elif closure_ready == "yes" and unresolved_blockers:
        errors.append(f"{location}: unresolved blocker prevents Closure readiness")

    required_lines = (
        "- Finding status authority: `FINDING-LEDGER.md`",
        "- Triage and disposition authority: Supervisor",
        "- Recording authority: Integrator",
        "- Integrator may accept risk: no",
        "- Integrator may lower severity: no",
        "- Detailed Finding files do not own authoritative Finding status.",
    )
    lines = set(text.splitlines())
    for line in required_lines:
        if line not in lines:
            errors.append(f"{location}: missing Finding Ledger invariant {line!r}")


def validate_state_source_discipline(root: Path, errors: list[str]) -> None:
    checklist = (root / ".looppilot/CHECKLIST.md").read_text(encoding="utf-8")
    expected = (
        "A human-readable projection and recovery aid, not the authoritative Task, "
        "Finding, or Loop state source."
    )
    if expected not in _normalized(checklist):
        errors.append(".looppilot/CHECKLIST.md: missing Full Loop projection boundary")

    paths = [
        root / "README.md",
        root / ".looppilot/README.md",
        *root.joinpath("docs").glob("*.md"),
        *root.joinpath(".looppilot/full-loop").glob("*.md"),
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            folded = line.casefold()
            if (
                "checklist" in folded
                and "authoritative" in folded
                and "task status" in folded
                and "not authoritative" not in folded
                and "must not" not in folded
            ):
                errors.append(
                    f"{path.relative_to(root).as_posix()}: Checklist must not be Full Loop Task authority"
                )


def validate_no_active_phase_two_instances(root: Path, errors: list[str]) -> None:
    for relative in (
        ".looppilot/PROJECT.md",
        ".looppilot/LOOP-MAP.md",
        ".looppilot/CHECKPOINT.md",
    ):
        if (root / relative).exists():
            errors.append(f"{relative}: Phase 2 must not create an active instance")
    if (root / ".looppilot/loops").exists():
        errors.append(".looppilot/loops: Phase 2 must not create active Loop instances")


def validate_full_loop(
    root: Path, errors: list[str], task_statuses: set[str]
) -> None:
    """Validate Phase 2 structure without executing a workflow."""

    validate_full_loop_readme(root, errors)
    validate_loop_map(root, errors)
    validate_loop_contract(root, errors)
    validate_task_ledger(root, errors, task_statuses)
    validate_finding_ledger(root, errors)
    validate_state_source_discipline(root, errors)
    validate_no_active_phase_two_instances(root, errors)
