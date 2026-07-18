"""Validate Phase 3 Full Loop delivery, review, rework, and closure templates."""

from __future__ import annotations

import re
from pathlib import Path

from full_loop_validation import (
    EMPTY_VALUES,
    FINDING_ID_PATTERN,
    FINDING_SEVERITIES,
    LOOP_ID_PATTERN,
    REWORK_TASK_ID_PATTERN,
    TASK_ID_PATTERN,
    _field,
    _normalized,
    _plain,
    _real,
    _require_lines,
    _section_lines,
    _table,
)


FULL_LOOP_ROOT = ".looppilot/full-loop"
PHASE_THREE_PROTOCOL = "docs/full-loop-delivery-review-and-closure.md"
FULL_LOOP_EXECUTION_FILES = (
    f"{FULL_LOOP_ROOT}/WORKER-DELIVERY-TEMPLATE.md",
    f"{FULL_LOOP_ROOT}/INTEGRATION-RECORD-TEMPLATE.md",
    f"{FULL_LOOP_ROOT}/REVIEW-REPORT-TEMPLATE.md",
    f"{FULL_LOOP_ROOT}/FINDING-TEMPLATE.md",
    f"{FULL_LOOP_ROOT}/REWORK-TASK-TEMPLATE.md",
    f"{FULL_LOOP_ROOT}/LOOP-CLOSURE-TEMPLATE.md",
    PHASE_THREE_PROTOCOL,
)

DELIVERY_STATUSES = {
    "completed",
    "partial",
    "blocked",
    "failed",
    "scope-change-required",
}
READINESS_RESULTS = {
    "ready-for-integration",
    "revision-required",
    "blocked",
    "rejected",
}
INTEGRATION_STATUSES = {
    "inactive",
    "collecting",
    "integrating",
    "blocked",
    "failed",
    "integrated",
}
REVIEWER_TYPES = {
    "spec",
    "standards",
    "domain",
    "data",
    "concurrency",
    "security",
    "operations",
    "performance",
    "architecture",
    "frontend",
    "compatibility",
    "test",
    "code-quality",
    "accessibility",
    "compliance",
    "factual-accuracy",
    "citation",
    "methodology",
    "structure",
    "visual",
    "domain-expert",
}
REVIEW_STATUSES = {
    "inactive",
    "in-progress",
    "completed",
    "blocked",
    "superseded",
}
REVIEW_VERDICTS = {"pass", "pass-with-findings", "rework-required", "blocked"}
CLOSURE_STATUSES = {
    "inactive",
    "draft",
    "ready-for-acceptance",
    "accepted",
    "blocked",
    "superseded",
}
REVIEW_ID_PATTERN = re.compile(r"^REVIEW-\d{3,}$")
PLACEHOLDER_VALUES = EMPTY_VALUES | {
    "not-run",
    "not-inspected",
    "yyyy-mm-dd",
    "no finding recorded",
}

WORKER_HEADINGS = (
    "## Identity",
    "## Task Contract Reference",
    "## Scope Confirmation",
    "### Authorized Scope",
    "### Actual Scope",
    "### Deviations",
    "## Changed Artifacts",
    "## Implementation Summary",
    "## Verification Performed",
    "## Skipped Verification",
    "## Evidence",
    "## Known Limitations",
    "## Requested Decisions",
    "## Integration Notes",
    "## Authority Note",
)
INTEGRATION_HEADINGS = (
    "## Identity",
    "## Inputs",
    "### Included Deliveries",
    "### Excluded Deliveries",
    "## Integration Order",
    "## File Ownership and Conflict Groups",
    "## Mechanical Conflicts",
    "## Semantic Conflicts Escalated",
    "## Build Verification",
    "## Integration Tests",
    "## Unintegrated Work",
    "## Integration Barrier Assessment",
    "## Authority Note",
)
REVIEW_HEADINGS = (
    "## Identity",
    "## Review Scope",
    "## Evidence Reviewed",
    "## Checks Performed",
    "## Findings Created",
    "## Coverage Limitations",
    "## Standards Review Contribution",
    "## Spec Review Contribution",
    "## Reviewer Verdict",
    "## Reverification Requirements",
    "## Authority Note",
)
FINDING_HEADINGS = (
    "## Identity",
    "## Affected Scope",
    "## Summary",
    "## Evidence",
    "## Expected Behavior",
    "## Actual Behavior",
    "## Risk",
    "## Required Outcome",
    "## Suggested Remediation",
    "## Verification Method",
    "## Rework Guidance",
    "## Limitations",
    "## Authority Note",
)
REWORK_HEADINGS = (
    "## Identity",
    "## Originating Findings",
    "## Required Outcome",
    "## Allowed Scope",
    "## Forbidden Scope",
    "## Required Changes",
    "## Required Verification",
    "## Reviewer Reverification",
    "## Strategy Change",
    "## Dependencies",
    "## Authority",
    "## Escalation Conditions",
    "## Completion Boundary",
)
CLOSURE_HEADINGS = (
    "## Identity",
    "## Objective Outcome",
    "## Included Changes Delivered",
    "## Excluded Changes Preserved",
    "## Completed Tasks",
    "## Integrated Boundary",
    "## Review Summary",
    "### Spec Review",
    "### Standards Review",
    "### Conditional Reviews",
    "## Finding Disposition",
    "## Acceptance",
    "### Functional Acceptance",
    "### Engineering Acceptance",
    "### Delivery Acceptance",
    "## Barrier Summary",
    "## Residual Risks",
    "## Deferred Work",
    "## Commit Result",
    "## Checkpoint Relationship",
    "## Next Loop Inputs",
    "## Workspace State",
    "## Closure Decision",
    "## Honesty Boundary",
)


def _template_text(root: Path, filename: str, errors: list[str]) -> tuple[str, str]:
    location = f"{FULL_LOOP_ROOT}/{filename}"
    text = (root / location).read_text(encoding="utf-8")
    first_line = text.splitlines()[0] if text.splitlines() else ""
    if "TEMPLATE" not in first_line:
        errors.append(f"{location}: title must identify the file as TEMPLATE")
    if _field(text, "Template Status") != "inactive":
        errors.append(f"{location}: Template Status must remain inactive")
    return location, text


def _placeholder(value: str | None) -> bool:
    return value is None or _plain(value).casefold() in PLACEHOLDER_VALUES


def _require_fields(
    text: str, fields: tuple[str, ...], location: str, errors: list[str]
) -> None:
    for name in fields:
        if _field(text, name, bullet=True) is None:
            errors.append(f"{location}: missing required field {name!r}")


def _require_declared_values(
    text: str, values: set[str], label: str, location: str, errors: list[str]
) -> None:
    for value in sorted(values):
        if f"`{value}`" not in text:
            errors.append(f"{location}: {label} declaration missing {value!r}")


def _section_has_real_content(text: str, heading: str) -> bool:
    for line in _section_lines(text, heading):
        stripped = line.strip().lstrip("-").strip().rstrip(".")
        if stripped and stripped.casefold() not in PLACEHOLDER_VALUES:
            return True
    return False


def _heading_lines(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return []
    level = len(heading) - len(heading.lstrip("#"))
    result: list[str] = []
    for line in lines[start:]:
        if line.startswith("#"):
            next_level = len(line) - len(line.lstrip("#"))
            if next_level <= level:
                break
        result.append(line)
    return result


def validate_worker_delivery(root: Path, errors: list[str]) -> None:
    location, text = _template_text(root, "WORKER-DELIVERY-TEMPLATE.md", errors)
    _require_lines(text, WORKER_HEADINGS, location, errors)
    _require_fields(
        text,
        ("Delivery ID", "Task ID", "Loop ID", "Worker", "Delivery Status"),
        location,
        errors,
    )
    status = _field(text, "Delivery Status", bullet=True)
    _require_declared_values(text, DELIVERY_STATUSES, "Delivery Status", location, errors)
    if status != "none" and status not in DELIVERY_STATUSES:
        errors.append(f"{location}: invalid Delivery Status {status!r}")
    for field in ("Delivery ID", "Task ID", "Loop ID", "Worker"):
        value = _field(text, field, bullet=True)
        if not _placeholder(value):
            errors.append(f"{location}: inactive template contains a real {field}")
    verification = "\n".join(_section_lines(text, "## Verification Performed"))
    if re.search(r"\|[^\n]+\|\s*(?:pass(?:ed)?|success)\s*\|", verification, re.I):
        errors.append(f"{location}: inactive template fabricates passing verification")
    if re.search(
        r"Delivery Status:\s*(?:approved|integrated|accepted|closed)\b", text, re.I
    ):
        errors.append(f"{location}: Worker Delivery claims an authority-only status")
    if "`TASK-LEDGER.md` remains the only Task status source." not in _normalized(text):
        errors.append(f"{location}: Delivery must not be a Task status authority")
    if re.search(r"Delivery (?:is|becomes|owns).{0,30}Task status (?:source|authority)", text, re.I):
        errors.append(f"{location}: Delivery must not be a Task status authority")


def validate_integration_record(root: Path, errors: list[str]) -> None:
    location, text = _template_text(root, "INTEGRATION-RECORD-TEMPLATE.md", errors)
    _require_lines(text, INTEGRATION_HEADINGS, location, errors)
    _require_fields(text, ("Integration ID", "Loop ID", "Integrator", "Status"), location, errors)
    status = _field(text, "Status", bullet=True)
    _require_declared_values(text, INTEGRATION_STATUSES, "Integration Status", location, errors)
    if status not in INTEGRATION_STATUSES:
        errors.append(f"{location}: invalid Integration Status {status!r}")
    for field in ("Integration ID", "Loop ID", "Integrator"):
        if not _placeholder(_field(text, field, bullet=True)):
            errors.append(f"{location}: inactive template contains a real {field}")
    build = "\n".join(_section_lines(text, "## Build Verification"))
    if re.search(r"\|[^\n]+\|\s*(?:pass(?:ed)?|success)\s*\|", build, re.I):
        errors.append(f"{location}: inactive template fabricates a passing build")
    if re.search(r"Integrator (?:may|can|is authorized to) accept risk", text, re.I):
        errors.append(f"{location}: Integrator must not accept risk")
    if re.search(r"Integrator (?:may|can|is authorized to) (?:change|modify) Scope", text, re.I):
        errors.append(f"{location}: Integrator must not change Scope")
    if re.search(r"integrated.{0,30}(?:means|maps? to|equals).{0,15}closed", text, re.I):
        errors.append(f"{location}: integrated must not map to Loop closed")
    if "`LOOP-MAP.md` remains the Loop status source." not in _normalized(text):
        errors.append(f"{location}: Integration Record must not be a Loop status authority")


def validate_review_report(root: Path, errors: list[str]) -> None:
    location, text = _template_text(root, "REVIEW-REPORT-TEMPLATE.md", errors)
    _require_lines(text, REVIEW_HEADINGS, location, errors)
    _require_fields(
        text,
        ("Review ID", "Loop ID", "Reviewer", "Reviewer Type", "Status", "Verdict"),
        location,
        errors,
    )
    reviewer_type = _field(text, "Reviewer Type", bullet=True)
    _require_declared_values(text, REVIEWER_TYPES, "Reviewer Type", location, errors)
    if reviewer_type != "none" and reviewer_type not in REVIEWER_TYPES:
        errors.append(f"{location}: invalid Reviewer Type {reviewer_type!r}")
    status = _field(text, "Status", bullet=True)
    _require_declared_values(text, REVIEW_STATUSES, "Review Status", location, errors)
    if status not in REVIEW_STATUSES:
        errors.append(f"{location}: invalid Review Status {status!r}")
    verdict = _field(text, "Verdict", bullet=True)
    _require_declared_values(text, REVIEW_VERDICTS, "Reviewer Verdict", location, errors)
    if verdict != "none" and verdict not in REVIEW_VERDICTS:
        errors.append(f"{location}: invalid Reviewer Verdict {verdict!r}")
    for field in ("Review ID", "Loop ID", "Reviewer"):
        if not _placeholder(_field(text, field, bullet=True)):
            errors.append(f"{location}: inactive template contains a real {field}")
    if re.search(r"Reviewer (?:may|can|is authorized to) modify implementation", text, re.I):
        errors.append(f"{location}: Reviewer must not modify implementation")
    if re.search(r"Reviewer (?:may|can|is authorized to) accept risk", text, re.I):
        errors.append(f"{location}: Reviewer must not accept risk")
    if re.search(r"Reviewer (?:may|can|is authorized to) update (?:the )?(?:authoritative )?Ledgers?", text, re.I):
        errors.append(f"{location}: Reviewer must not update authoritative Ledgers")
    if re.search(r"specialist.{0,60}automatically.{0,60}Spec.{0,30}Standards.{0,30}pass", text, re.I | re.S):
        errors.append(f"{location}: specialist Review must not automatically pass both axes")
    if "`FINDING-LEDGER.md` remains authoritative." not in _normalized(text):
        errors.append(f"{location}: Review Report must not own Finding status")


def validate_finding_detail(root: Path, errors: list[str]) -> None:
    location, text = _template_text(root, "FINDING-TEMPLATE.md", errors)
    _require_lines(text, FINDING_HEADINGS, location, errors)
    _require_fields(
        text,
        ("Finding ID", "Loop ID", "Review ID", "Category", "Severity"),
        location,
        errors,
    )
    if _field(text, "Status", bullet=True) is not None:
        errors.append(f"{location}: Finding Detail must not contain authoritative Status")
    finding_id = _field(text, "Finding ID", bullet=True)
    loop_id = _field(text, "Loop ID", bullet=True)
    review_id = _field(text, "Review ID", bullet=True)
    if finding_id != "none" and (finding_id is None or not FINDING_ID_PATTERN.fullmatch(finding_id)):
        errors.append(f"{location}: invalid Finding ID {finding_id!r}")
    if loop_id != "none" and (loop_id is None or not LOOP_ID_PATTERN.fullmatch(loop_id)):
        errors.append(f"{location}: invalid Loop ID {loop_id!r}")
    if review_id != "none" and (review_id is None or not REVIEW_ID_PATTERN.fullmatch(review_id)):
        errors.append(f"{location}: invalid Review ID {review_id!r}")
    severity = _field(text, "Severity", bullet=True)
    if severity != "none" and severity not in FINDING_SEVERITIES:
        errors.append(f"{location}: invalid Finding severity {severity!r}")
    if severity in {"blocker", "major"} and not _section_has_real_content(text, "## Required Outcome"):
        errors.append(f"{location}: blocker or major Finding requires a concrete Required Outcome")
    category = _field(text, "Category", bullet=True)
    if category == "other" and not _section_has_real_content(text, "## Summary"):
        errors.append(f"{location}: category other requires an explanation")
    summary = _normalized("\n".join(_section_lines(text, "## Summary"))).casefold()
    evidence = _normalized("\n".join(_section_lines(text, "## Evidence"))).casefold()
    if summary in {"code is bad.", "code is bad", "bad code.", "bad code"} and evidence in {
        "- none.",
        "- none",
        "none.",
        "none",
    }:
        errors.append(f"{location}: Finding must be specific and verifiable")
    if "Status is maintained only in `FINDING-LEDGER.md`." not in _normalized(text):
        errors.append(f"{location}: Finding Detail must not be a Finding status source")


def validate_rework_task(root: Path, errors: list[str]) -> None:
    location, text = _template_text(root, "REWORK-TASK-TEMPLATE.md", errors)
    _require_lines(text, REWORK_HEADINGS, location, errors)
    _require_fields(
        text,
        ("Rework Task ID", "Parent Task", "Loop ID", "Revision", "Revision Budget"),
        location,
        errors,
    )
    rework_id = _field(text, "Rework Task ID", bullet=True)
    parent = _field(text, "Parent Task", bullet=True)
    if rework_id != "none" and (rework_id is None or not REWORK_TASK_ID_PATTERN.fullmatch(rework_id)):
        errors.append(f"{location}: invalid Rework Task ID {rework_id!r}")
    if rework_id and rework_id.endswith("-R0"):
        errors.append(f"{location}: Rework Task revision must start at R1")
    if parent != "none" and (parent is None or not TASK_ID_PATTERN.fullmatch(parent)):
        errors.append(f"{location}: invalid Parent Task {parent!r}")
    if rework_id != "none" and parent == "none":
        errors.append(f"{location}: active Rework Task requires a Parent Task")
    revision = _field(text, "Revision", bullet=True)
    budget = _field(text, "Revision Budget", bullet=True)
    if revision != "none" and (revision is None or not revision.isdigit() or int(revision) < 1):
        errors.append(f"{location}: Revision must be a positive integer")
    if budget != "none" and (budget is None or not budget.isdigit() or int(budget) < 1):
        errors.append(f"{location}: Revision Budget must be a positive integer")
    if revision and budget and revision.isdigit() and budget.isdigit() and int(revision) > int(budget):
        errors.append(f"{location}: revision exceeds Revision Budget")
    if rework_id != "none" and not _section_has_real_content(text, "## Originating Findings"):
        errors.append(f"{location}: active Rework Task requires Originating Findings")
    previous = _field(text, "Previous approach", bullet=True)
    new = _field(text, "New approach", bullet=True)
    material = _field(text, "Material change", bullet=True)
    if (
        previous
        and new
        and not _placeholder(previous)
        and previous.casefold() == new.casefold()
        and material in {"no", "none"}
    ):
        errors.append(f"{location}: repeated failed approach requires a material Strategy Change")
    if re.search(r"Rework.{0,50}(?:closes|may close|can close).{0,20}Finding", text, re.I):
        errors.append(f"{location}: Rework Task must not close its Finding")
    for field in ("Commit", "Push", "Release", "Deploy"):
        value = _field(text, field, bullet=True)
        if value not in {"no", "inherited-no"}:
            errors.append(f"{location}: Rework {field} authority must be no or inherited-no")


def validate_loop_closure(root: Path, errors: list[str]) -> None:
    location, text = _template_text(root, "LOOP-CLOSURE-TEMPLATE.md", errors)
    _require_lines(text, CLOSURE_HEADINGS, location, errors)
    _require_fields(
        text,
        (
            "Loop ID",
            "Closure ID",
            "Closure Status",
            "Skipped verification",
            "Commit authorized",
            "Commit result",
            "Checkpoint status",
            "Checkpoint reference",
            "Recovery readiness",
        ),
        location,
        errors,
    )
    status = _field(text, "Closure Status", bullet=True)
    _require_declared_values(text, CLOSURE_STATUSES, "Closure Status", location, errors)
    if status not in CLOSURE_STATUSES:
        errors.append(f"{location}: invalid Closure Status {status!r}")
    for field in ("Loop ID", "Closure ID", "Supervisor", "Integrator"):
        if not _placeholder(_field(text, field, bullet=True)):
            errors.append(f"{location}: inactive template contains a real {field}")
    for barrier in (
        "Contract Barrier",
        "Implementation Barrier",
        "Integration Barrier",
        "Review Barrier",
        "Closure Barrier",
    ):
        if _field(text, barrier, bullet=True) is None:
            errors.append(f"{location}: missing required Barrier {barrier!r}")
    rows = _table(
        text,
        "## Finding Disposition",
        ("Finding", "Severity", "Final Status", "Decision", "Evidence"),
        location,
        errors,
    )
    if status in {"ready-for-acceptance", "accepted"}:
        for row in rows:
            if _plain(row["Finding"]).casefold() == "none":
                continue
            if (
                _plain(row["Severity"]).casefold() == "blocker"
                and _plain(row["Final Status"]).casefold()
                not in {"closed", "rejected", "duplicate"}
            ):
                errors.append(f"{location}: unresolved blocker prevents Closure readiness")
            if (
                _plain(row["Severity"]).casefold() == "major"
                and _plain(row["Final Status"]).casefold()
                not in {"closed", "risk-accepted", "deferred", "rejected", "duplicate"}
            ):
                errors.append(f"{location}: unresolved major requires an explicit disposition")
        for heading, label in (
            ("### Spec Review", "Spec Review"),
            ("### Standards Review", "Standards Review"),
        ):
            result = _field("\n".join(_heading_lines(text, heading)), "Result", bullet=True)
            if result != "pass":
                errors.append(f"{location}: {label} must pass before Closure readiness")
        for heading, label in (
            ("### Functional Acceptance", "Functional Acceptance"),
            ("### Engineering Acceptance", "Engineering Acceptance"),
            ("### Delivery Acceptance", "Delivery Acceptance"),
        ):
            lines = _heading_lines(text, heading)
            if not any("[x]" in line.casefold() for line in lines) or any(
                "[ ]" in line for line in lines
            ):
                errors.append(f"{location}: {label} must pass before Closure readiness")
        barriers = (
            "Contract Barrier",
            "Implementation Barrier",
            "Integration Barrier",
            "Review Barrier",
        )
        if status == "accepted":
            barriers += ("Closure Barrier",)
        for barrier in barriers:
            if _field(text, barrier, bullet=True) not in {"pass", "passed"}:
                errors.append(f"{location}: {barrier} must pass before {status}")
    recovery = _field(text, "Recovery readiness", bullet=True)
    checkpoint = _field(text, "Checkpoint status", bullet=True)
    checkpoint_ref = _field(text, "Checkpoint reference", bullet=True)
    if recovery == "yes" and (
        checkpoint not in {"created", "valid", "observed"} or not _real(checkpoint_ref or "")
    ):
        errors.append(f"{location}: recovery-ready requires a valid Checkpoint")
    commit_authorized = _field(text, "Commit authorized", bullet=True)
    commit_result = _field(text, "Commit result", bullet=True) or ""
    if commit_authorized != "yes" and commit_result.casefold() in {
        "created",
        "committed",
        "commit-created",
    }:
        errors.append(f"{location}: created Commit requires explicit authorization")
    if re.search(r"Closure accepted.{0,30}(?:means|sets|maps? to).{0,20}Loop closed", text, re.I):
        errors.append(f"{location}: Closure accepted must not set Loop closed")
    if "`LOOP-MAP.md` remains the only authoritative Loop status source" not in _normalized(text):
        errors.append(f"{location}: Loop Closure must not be a Loop status authority")


def validate_phase_three_protocol(root: Path, errors: list[str]) -> None:
    text = (root / PHASE_THREE_PROTOCOL).read_text(encoding="utf-8")
    required = (
        "## Worker Delivery",
        "## Task-Level Readiness",
        "## Integration Record",
        "## Loop-Level Review",
        "## Finding Detail and Triage",
        "## Rework and Reverification",
        "## Loop Closure",
        "## Authoritative State Projection",
        "## Static Validation Boundary",
    )
    _require_lines(text, required, PHASE_THREE_PROTOCOL, errors)
    for result in READINESS_RESULTS:
        if f"`{result}`" not in text:
            errors.append(f"{PHASE_THREE_PROTOCOL}: missing Readiness result {result!r}")
    for source in ("TASK-LEDGER.md", "FINDING-LEDGER.md", "LOOP-MAP.md", "CHECKPOINT.md"):
        if source not in text:
            errors.append(f"{PHASE_THREE_PROTOCOL}: missing state-source reference {source!r}")


def validate_full_loop_execution(root: Path, errors: list[str]) -> None:
    """Validate Phase 3 static contracts without executing any transitions."""

    validate_worker_delivery(root, errors)
    validate_integration_record(root, errors)
    validate_review_report(root, errors)
    validate_finding_detail(root, errors)
    validate_rework_task(root, errors)
    validate_loop_closure(root, errors)
    validate_phase_three_protocol(root, errors)
