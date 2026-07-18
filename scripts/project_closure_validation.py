"""Validate Phase 5 Project closure and final-delivery static contracts."""

from __future__ import annotations

import re
from pathlib import Path

from full_loop_validation import (
    EMPTY_VALUES,
    FINDING_SEVERITIES,
    LOOP_ID_PATTERN,
    _field,
    _normalized,
    _plain,
    _require_lines,
    _section_lines,
    _table,
)


FULL_LOOP_ROOT = ".looppilot/full-loop"
PROJECT_CLOSURE_PROTOCOL = "docs/project-closure-and-final-delivery.md"
PROJECT_CLOSURE_FILES = (
    f"{FULL_LOOP_ROOT}/CROSS-LOOP-VALIDATION-TEMPLATE.md",
    f"{FULL_LOOP_ROOT}/PROJECT-ACCEPTANCE-TEMPLATE.md",
    f"{FULL_LOOP_ROOT}/RELEASE-READINESS-TEMPLATE.md",
    f"{FULL_LOOP_ROOT}/FINAL-DELIVERY-REPORT-TEMPLATE.md",
    PROJECT_CLOSURE_PROTOCOL,
    "scripts/project_closure_validation.py",
    "tests/project_closure_case_matrix.py",
    "tests/test_project_closure_final_delivery.py",
)

VALIDATION_STATUSES = {
    "inactive", "planned", "in-progress", "passed", "passed-with-limitations",
    "failed", "blocked", "superseded",
}
ACCEPTANCE_STATUSES = {
    "inactive", "draft", "under-review", "accepted", "accepted-with-risks",
    "blocked", "rejected", "superseded",
}
READINESS_STATUSES = {
    "inactive", "not-applicable", "in-progress", "ready",
    "ready-with-accepted-risks", "blocked", "cancelled", "superseded",
}
REPORT_STATUSES = {"inactive", "draft", "ready", "issued", "superseded"}
DELIVERY_MODES = {"delivery-only", "release-required"}
REQUIREMENT_CLASSES = {"mandatory", "optional", "deferred", "cancelled", "excluded"}
REQUIREMENT_ID_PATTERN = re.compile(r"^REQ-\d{3,}$")
PLACEHOLDERS = EMPTY_VALUES | {
    "none.", "not-run", "not-applicable", "not-evaluated", "not-executed",
    "unknown", "yyyy-mm-dd", "no active project delivery.",
}

CROSS_LOOP_HEADINGS = (
    "## Identity", "## Included Loops", "## Excluded or Non-Mandatory Loops",
    "## Cross-Loop Dependencies", "## End-to-End User Flows",
    "## Requirement Coverage", "## Interface and Contract Compatibility",
    "## Data and Migration Compatibility",
    "## Identity, Permission, and Security Compatibility",
    "## Concurrency, Idempotency, and Ordering",
    "## Configuration and Environment Compatibility", "## Observability Continuity",
    "## Performance and Capacity", "## Deployment Ordering",
    "## Rollback and Compensation Relationships", "## Version and API Evolution",
    "## Documentation Consistency", "## Validation Performed",
    "## Skipped or Not-Applicable Validation", "## Project-Level Findings",
    "## Coverage Limitations", "## Validation Decision", "## Authority Note",
)
ACCEPTANCE_HEADINGS = (
    "## Identity", "## Original User Goal", "## Current Project Scope",
    "### Included Scope", "### Excluded Scope", "### Approved Scope Changes",
    "### Cancelled Requirements", "## Goal-to-Evidence Mapping",
    "## Mandatory Loop Summary", "## Cross-Loop Validation",
    "## Project Review Summary", "### Project Spec Review",
    "### Project Standards Review", "### Conditional Project Reviews",
    "## Project-Level Finding Disposition", "## Project Functional Acceptance",
    "## Project Engineering Acceptance", "## Project Delivery Acceptance",
    "## Residual Risks", "## Deferred Work", "## Accepted Risks",
    "## Release Relationship", "## Final Recovery State",
    "## Final Delivery Report", "## Acceptance Decision",
    "## Project Status Projection", "## Honesty Boundary",
)
READINESS_HEADINGS = (
    "## Identity", "## Version and Identity", "## Artifacts",
    "## Build and Test Evidence", "## Data and Migration",
    "## Configuration and Secrets", "## Feature Flags and Gray Release",
    "## Operations and Observability", "## Security and Compliance",
    "## Rollback and Recovery", "## Documentation", "## Authority",
    "## Readiness Gaps", "## Accepted Risks", "## Readiness Decision",
    "## Execution Result", "## Authority Note",
)
REPORT_HEADINGS = (
    "## Report Identity", "## Executive Summary", "## Original Goal",
    "## Delivered Outcomes", "## Loop Summary", "## Verification Summary",
    "### Cross-Loop Validation", "### Project Spec Review",
    "### Project Standards Review", "### Project Acceptance",
    "## Delivered Artifacts", "## Usage or Handoff Instructions",
    "## Deployment and Release State", "## Configuration and Environment",
    "## Operations and Monitoring", "## Rollback and Recovery",
    "## Deferred Work", "## Accepted Risks", "## Known Limitations",
    "## Excluded and Cancelled Work", "## Final Recovery Boundary",
    "## Unverified Items", "## Final Decision", "## Honesty Boundary",
)


def _template_text(root: Path, filename: str, errors: list[str]) -> tuple[str, str]:
    location = f"{FULL_LOOP_ROOT}/{filename}"
    text = (root / location).read_text(encoding="utf-8")
    first = text.splitlines()[0] if text.splitlines() else ""
    if "TEMPLATE" not in first:
        errors.append(f"{location}: title must identify the file as TEMPLATE")
    if _field(text, "Template Status") != "inactive":
        errors.append(f"{location}: Template Status must remain inactive")
    return location, text


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


def _real(value: str | None) -> bool:
    return value is not None and _plain(value).casefold() not in PLACEHOLDERS


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


def _section_field(text: str, heading: str, name: str) -> str | None:
    section = "\n".join(_heading_lines(text, heading))
    return _field(section, name, bullet=True)


def _section_has_real_content(text: str, heading: str) -> bool:
    for line in _heading_lines(text, heading):
        stripped = line.strip()
        if not stripped or stripped.startswith("|") or stripped.startswith("#"):
            continue
        stripped = stripped.lstrip("-").strip().rstrip(".")
        if ":" in stripped:
            stripped = stripped.split(":", 1)[1].strip()
        if stripped.casefold() not in PLACEHOLDERS:
            return True
    return False


def _has_checked_item(text: str, heading: str) -> bool:
    return any(line.strip().startswith("- [x]") for line in _heading_lines(text, heading))


def _all_items_checked(text: str, heading: str) -> bool:
    items = [line.strip() for line in _heading_lines(text, heading) if line.strip().startswith("- [")]
    return bool(items) and all(line.startswith("- [x]") for line in items)


def _result_failed(value: str) -> bool:
    return _plain(value).casefold() in {"fail", "failed", "blocked", "rejected"}


def validate_cross_loop(root: Path, errors: list[str]) -> None:
    location, text = _template_text(root, "CROSS-LOOP-VALIDATION-TEMPLATE.md", errors)
    _require_lines(text, CROSS_LOOP_HEADINGS, location, errors)
    _require_fields(
        text,
        (
            "Validation ID", "Project ID", "Performed", "Performed by",
            "Validation Status", "Project boundary", "Verified HEAD or artifact boundary",
            "Decision", "Reason", "Blocking conditions", "Required remediation",
        ),
        location,
        errors,
    )
    _require_declared_values(text, VALIDATION_STATUSES, "Validation Status", location, errors)
    status = _field(text, "Validation Status", bullet=True)
    if status not in VALIDATION_STATUSES:
        errors.append(f"{location}: invalid Validation Status {status!r}")
        status = "blocked"
    included = _table(
        text,
        "## Included Loops",
        ("Loop ID", "Required", "Loop Status", "Closure", "Commit Boundary", "Included"),
        location,
        errors,
    )
    _table(
        text,
        "## Cross-Loop Dependencies",
        ("Source Loop", "Target Loop", "Dependency", "Expected Contract", "Result"),
        location,
        errors,
    )
    _table(
        text,
        "## End-to-End User Flows",
        ("Flow ID", "User or Actor", "Participating Loops", "Expected Outcome", "Evidence", "Result"),
        location,
        errors,
    )
    _table(
        text,
        "## Requirement Coverage",
        ("Requirement ID", "User Goal", "Implementing Loops", "Integrated Outcome", "Evidence", "Result"),
        location,
        errors,
    )
    performed = _table(
        text,
        "## Validation Performed",
        ("Command, Scenario, or Inspection", "Result", "Evidence"),
        location,
        errors,
    )
    findings = _table(
        text,
        "## Project-Level Findings",
        ("Finding Reference", "Severity", "Target Remediation Loop", "Status Source"),
        location,
        errors,
    )
    if status == "inactive":
        for field in ("Validation ID", "Project ID", "Performed by", "Project boundary"):
            if _real(_field(text, field, bullet=True)):
                errors.append(f"{location}: inactive template contains a real {field}")
        for row in included:
            if _real(row.get("Loop ID")):
                errors.append(f"{location}: inactive template contains a real Loop")
    if status in {"passed", "passed-with-limitations"}:
        real_performed = [row for row in performed if _real(row.get("Command, Scenario, or Inspection"))]
        if not real_performed:
            errors.append(f"{location}: {status} requires observed Validation Performed evidence")
        if any(_result_failed(row.get("Result", "")) for row in real_performed):
            errors.append(f"{location}: {status} cannot contain failed validation")
        mandatory = [
            row for row in included
            if row.get("Required", "").casefold() == "yes"
            and row.get("Included", "").casefold() == "yes"
        ]
        if not mandatory:
            errors.append(f"{location}: {status} requires included mandatory Loops")
        for row in mandatory:
            if row.get("Loop Status", "").casefold() != "closed":
                errors.append(f"{location}: included mandatory Loop must be closed")
            if not _real(row.get("Closure")) or not _real(row.get("Commit Boundary")):
                errors.append(f"{location}: included mandatory Loop requires Closure and boundary evidence")
        for row in findings:
            if row.get("Severity", "").casefold() == "blocker":
                errors.append(f"{location}: passed Validation cannot contain a Project Blocker")
    if status == "passed-with-limitations" and not _section_has_real_content(
        text, "## Coverage Limitations"
    ):
        errors.append(f"{location}: passed-with-limitations requires a disclosed limitation")
    if status == "failed" and re.search(r"Project (?:is|status:) ready", text, re.I):
        errors.append(f"{location}: failed Validation must not claim Project ready")
    if re.search(r"all (?:mandatory )?Loops (?:are )?closed.{0,80}(?:therefore|automatically).{0,40}passed", text, re.I | re.S):
        errors.append(f"{location}: closed Loops must not automatically pass Cross-Loop Validation")
    normalized = _normalized(text)
    if "`PROJECT.md` remains the only Project status authority" not in normalized:
        errors.append(f"{location}: Cross-Loop Validation must not own Project status")
    if re.search(r"Validation (?:owns|is|becomes).{0,40}Project status", text, re.I):
        errors.append(f"{location}: Cross-Loop Validation must not own Project status")


def _validate_goal_mapping(text: str, location: str, errors: list[str]) -> None:
    rows = _table(
        text,
        "## Goal-to-Evidence Mapping",
        (
            "Requirement ID", "Requirement Class", "User Goal or Requirement",
            "Responsible Loops", "Delivered Outcome", "Acceptance Evidence", "Result",
        ),
        location,
        errors,
    )
    seen: set[str] = set()
    for row in rows:
        requirement = row.get("Requirement ID", "")
        if not _real(requirement):
            continue
        if not REQUIREMENT_ID_PATTERN.fullmatch(requirement):
            errors.append(f"{location}: invalid Requirement ID {requirement!r}")
        if requirement in seen:
            errors.append(f"{location}: duplicate Requirement ID {requirement!r}")
        seen.add(requirement)
        classification = row.get("Requirement Class", "").casefold()
        if classification not in REQUIREMENT_CLASSES:
            errors.append(f"{location}: invalid Requirement Class {classification!r}")
        result = row.get("Result", "").casefold()
        if result in {"passed", "delivered"}:
            if classification in {"cancelled", "excluded"}:
                errors.append(f"{location}: {classification} Requirement cannot be counted as passed")
            if not _real(row.get("Responsible Loops")):
                errors.append(f"{location}: delivered Requirement requires a responsible Loop")
            if not _real(row.get("Acceptance Evidence")):
                errors.append(f"{location}: delivered Requirement requires acceptance evidence")
        if classification == "mandatory":
            for field in ("Responsible Loops", "Delivered Outcome", "Acceptance Evidence"):
                if not _real(row.get(field)):
                    errors.append(f"{location}: mandatory Requirement missing mapping field {field!r}")
        if classification == "deferred" and not _section_has_real_content(text, "## Deferred Work"):
            errors.append(f"{location}: deferred Requirement must be disclosed")


def _project_findings_block_acceptance(text: str, location: str, errors: list[str]) -> None:
    rows = _table(
        text,
        "## Project-Level Finding Disposition",
        (
            "Finding", "Severity", "Remediation Loop", "Authoritative Status Source",
            "Current Status", "Decision",
        ),
        location,
        errors,
    )
    for row in rows:
        if not _real(row.get("Finding")):
            continue
        severity = row.get("Severity", "").casefold()
        status = row.get("Current Status", "").casefold()
        if severity not in FINDING_SEVERITIES:
            errors.append(f"{location}: invalid Project Finding severity {severity!r}")
        if not _real(row.get("Remediation Loop")) or not LOOP_ID_PATTERN.fullmatch(
            row.get("Remediation Loop", "")
        ):
            errors.append(f"{location}: Project Finding requires a remediation Loop")
        if "FINDING-LEDGER.md" not in row.get("Authoritative Status Source", ""):
            errors.append(f"{location}: Project Finding must use a Loop Finding Ledger")
        if severity == "blocker" and status not in {"closed", "rejected", "duplicate"}:
            errors.append(f"{location}: Project Blocker prevents Project Acceptance")
        if severity == "major" and status not in {
            "closed", "deferred", "risk-accepted", "rejected", "duplicate",
        }:
            errors.append(f"{location}: Project Major requires disposition")


def validate_project_acceptance(root: Path, errors: list[str]) -> None:
    location, text = _template_text(root, "PROJECT-ACCEPTANCE-TEMPLATE.md", errors)
    _require_lines(text, ACCEPTANCE_HEADINGS, location, errors)
    _require_fields(
        text,
        (
            "Acceptance ID", "Project ID", "Prepared", "Prepared by", "Supervisor",
            "Integrator", "Acceptance Status", "Project boundary", "Delivery mode",
            "Validation", "Result", "Coverage limitations", "Blocking conditions",
            "Final Checkpoint", "Checkpoint status", "Recovery readiness",
            "Terminal Resume Point or reopen condition", "Report", "Report status",
            "Decision", "Decision by", "Decision evidence", "Requested Project status",
            "Status authority", "Integrator update required", "Update evidence",
        ),
        location,
        errors,
    )
    _require_declared_values(text, ACCEPTANCE_STATUSES, "Acceptance Status", location, errors)
    status = _field(text, "Acceptance Status", bullet=True)
    if status not in ACCEPTANCE_STATUSES:
        errors.append(f"{location}: invalid Acceptance Status {status!r}")
        status = "blocked"
    mode = _field(text, "Delivery mode", bullet=True)
    if status != "inactive" and mode not in DELIVERY_MODES:
        errors.append(f"{location}: active Acceptance requires a valid Delivery mode")
    _validate_goal_mapping(text, location, errors)
    loop_rows = _table(
        text,
        "## Mandatory Loop Summary",
        ("Loop ID", "Required", "Status Source", "Closure", "Final Status", "Evidence"),
        location,
        errors,
    )
    _project_findings_block_acceptance(text, location, errors)
    if status == "inactive":
        for field in ("Acceptance ID", "Project ID", "Supervisor", "Integrator", "Project boundary"):
            if _real(_field(text, field, bullet=True)):
                errors.append(f"{location}: inactive template contains a real {field}")
    if status in {"accepted", "accepted-with-risks"}:
        mandatory_loops = [
            row for row in loop_rows
            if _plain(row.get("Required", "")).lower() in {"yes", "true", "required", "mandatory"}
        ]
        if not mandatory_loops:
            errors.append(f"{location}: accepted Project requires mandatory Loop evidence")
        for row in mandatory_loops:
            if _plain(row.get("Final Status", "")).lower() != "closed":
                errors.append(f"{location}: accepted Project requires every mandatory Loop closed")
            if "LOOP-MAP.md" not in row.get("Status Source", ""):
                errors.append(f"{location}: mandatory Loop status must come from LOOP-MAP.md")
            if not _real(row.get("Closure")) or not _real(row.get("Evidence")):
                errors.append(f"{location}: mandatory Loop requires Closure and evidence")
        if _section_field(text, "### Project Spec Review", "Result") != "pass":
            errors.append(f"{location}: accepted Project requires Project Spec Review pass")
        if _section_field(text, "### Project Standards Review", "Result") != "pass":
            errors.append(f"{location}: accepted Project requires Project Standards Review pass")
        if _section_field(text, "## Cross-Loop Validation", "Result") not in {
            "passed", "passed-with-limitations",
        }:
            errors.append(f"{location}: accepted Project requires Cross-Loop Validation pass")
        for heading, label in (
            ("## Project Functional Acceptance", "Functional"),
            ("## Project Engineering Acceptance", "Engineering"),
            ("## Project Delivery Acceptance", "Delivery"),
        ):
            if _section_field(text, heading, "Result") != "pass" or not _all_items_checked(text, heading):
                errors.append(f"{location}: accepted Project requires {label} Acceptance pass")
        if not _real(_section_field(text, "## Final Recovery State", "Final Checkpoint")):
            errors.append(f"{location}: accepted Project requires Final Checkpoint")
        if _section_field(text, "## Final Recovery State", "Checkpoint status") not in {"ready", "validated"}:
            errors.append(f"{location}: accepted Project requires a ready or validated Final Checkpoint")
        if not _real(_section_field(text, "## Final Delivery Report", "Report")):
            errors.append(f"{location}: accepted Project requires Final Delivery Report")
        if _section_field(text, "## Final Delivery Report", "Report status") not in {"ready", "issued"}:
            errors.append(f"{location}: accepted Project requires a ready Final Delivery Report")
        if mode == "release-required" and _section_field(
            text, "## Release Relationship", "Release result"
        ) not in {"released", "created", "executed"}:
            errors.append(f"{location}: release-required Project has an unsatisfied release obligation")
    if status == "accepted-with-risks":
        if not _section_has_real_content(text, "## Accepted Risks"):
            errors.append(f"{location}: accepted-with-risks requires disclosed risks")
        if not _real(_section_field(text, "## Acceptance Decision", "Decision by")):
            errors.append(f"{location}: accepted-with-risks requires authorized risk decision")
    if status == "blocked" and _section_field(
        text, "## Project Status Projection", "Requested Project status"
    ) in {"closed", "completed"}:
        errors.append(f"{location}: blocked Acceptance must not request Project closed")
    if re.search(r"Project accepted.{0,80}(?:therefore|automatically).{0,50}Release authorized", text, re.I | re.S):
        errors.append(f"{location}: Project Acceptance must not infer release authorization")
    if _section_field(text, "## Project Status Projection", "Status authority") != "PROJECT.md":
        errors.append(f"{location}: PROJECT.md must remain the Project status authority")
    if re.search(r"Project Acceptance (?:owns|is|becomes).{0,40}Project status", text, re.I):
        errors.append(f"{location}: Project Acceptance must not own Project status")


def validate_release_readiness(root: Path, errors: list[str]) -> None:
    location, text = _template_text(root, "RELEASE-READINESS-TEMPLATE.md", errors)
    _require_lines(text, READINESS_HEADINGS, location, errors)
    _require_fields(
        text,
        (
            "Readiness ID", "Project ID", "Prepared", "Prepared by", "Readiness Status",
            "Delivery mode", "Release scope", "Candidate boundary", "Rollback",
            "Health checks", "Security Review", "Commit authorized", "Push authorized",
            "Tag authorized", "Release authorized", "Deploy authorized", "Migrate authorized",
            "Traffic change authorized", "Rollback authorized", "Decision", "Decision by",
            "Evidence", "Risk acceptance authority", "Tag result", "Release result",
            "Deployment result", "Migration result", "Traffic change result", "Rollback result",
        ),
        location,
        errors,
    )
    _require_declared_values(text, READINESS_STATUSES, "Readiness Status", location, errors)
    status = _field(text, "Readiness Status", bullet=True)
    if status not in READINESS_STATUSES:
        errors.append(f"{location}: invalid Readiness Status {status!r}")
        status = "blocked"
    mode = _field(text, "Delivery mode", bullet=True)
    if status == "not-applicable" and mode != "delivery-only":
        errors.append(f"{location}: not-applicable Release Readiness requires delivery-only mode")
    if status in {"ready", "ready-with-accepted-risks"}:
        if mode not in DELIVERY_MODES:
            errors.append(f"{location}: ready Release Readiness requires a Delivery mode")
        if _section_has_real_content(text, "## Readiness Gaps"):
            errors.append(f"{location}: ready Release Readiness cannot contain readiness gaps")
        for heading, label in (
            ("## Rollback and Recovery", "rollback"),
            ("## Operations and Observability", "operations evidence"),
            ("## Security and Compliance", "security review"),
        ):
            if not _section_has_real_content(text, heading):
                errors.append(f"{location}: ready Release Readiness requires {label}")
        if _section_field(text, "## Authority", "Release authorized") == "no" and _section_field(
            text, "## Execution Result", "Release result"
        ) not in {"not-executed", "not-executed-not-authorized"}:
            errors.append(f"{location}: unauthorized release must remain not executed")
    if status == "ready-with-accepted-risks":
        if not _section_has_real_content(text, "## Accepted Risks"):
            errors.append(f"{location}: ready-with-accepted-risks requires disclosed risks")
        if not _real(_section_field(text, "## Readiness Decision", "Risk acceptance authority")):
            errors.append(f"{location}: ready-with-accepted-risks requires risk acceptance authority")
    pairs = (
        ("Tag authorized", "Tag result", {"created", "tag-created"}, "tag"),
        ("Release authorized", "Release result", {"created", "released", "executed"}, "release"),
        ("Deploy authorized", "Deployment result", {"deployed", "executed"}, "deployment"),
        ("Migrate authorized", "Migration result", {"migrated", "executed"}, "migration"),
        ("Traffic change authorized", "Traffic change result", {"changed", "executed"}, "traffic change"),
        ("Rollback authorized", "Rollback result", {"rolled-back", "executed"}, "rollback"),
    )
    for authority, result_name, executed, label in pairs:
        if _section_field(text, "## Authority", authority) != "yes" and _section_field(
            text, "## Execution Result", result_name
        ) in executed:
            errors.append(f"{location}: {label} execution requires independent authority")
    if re.search(r"Push authorized: yes.{0,100}(?:therefore|implies).{0,50}Release authorized: yes", text, re.I | re.S):
        errors.append(f"{location}: Push authority must not imply Release authority")
    if re.search(r"Release authorized: yes.{0,100}(?:therefore|implies).{0,50}Deploy authorized: yes", text, re.I | re.S):
        errors.append(f"{location}: Release authority must not imply Deploy authority")
    if re.search(r"Readiness (?:executes|creates|publishes) (?:the )?release", text, re.I):
        errors.append(f"{location}: Readiness must not execute release")
    if re.search(r"Readiness (?:owns|is|becomes).{0,40}Project status", text, re.I):
        errors.append(f"{location}: Release Readiness must not own Project status")


def validate_final_report(root: Path, errors: list[str]) -> None:
    location, text = _template_text(root, "FINAL-DELIVERY-REPORT-TEMPLATE.md", errors)
    _require_lines(text, REPORT_HEADINGS, location, errors)
    _require_fields(
        text,
        (
            "Report ID", "Project ID", "Prepared", "Prepared by", "Report Status",
            "Intended recipient", "Delivery boundary", "Acceptance", "Release authorized",
            "Release result", "Deployment authorized", "Deployment result",
            "Final Checkpoint", "Verified HEAD or artifact boundary", "Working tree state",
            "Recovery readiness", "Reopen condition", "Project Acceptance",
            "Project status source", "Delivery acknowledged", "Delivery evidence",
            "Further action required",
        ),
        location,
        errors,
    )
    _require_declared_values(text, REPORT_STATUSES, "Report Status", location, errors)
    status = _field(text, "Report Status", bullet=True)
    if status not in REPORT_STATUSES:
        errors.append(f"{location}: invalid Report Status {status!r}")
        status = "draft"
    _table(
        text,
        "## Delivered Outcomes",
        ("Requirement", "Delivered Outcome", "Responsible Loops", "Evidence", "Result"),
        location,
        errors,
    )
    _table(
        text,
        "## Loop Summary",
        ("Loop ID", "Outcome", "Closure", "Final Status", "Commit or Artifact Boundary"),
        location,
        errors,
    )
    if status == "inactive":
        for field in ("Report ID", "Project ID", "Prepared by", "Intended recipient", "Delivery boundary"):
            if _real(_field(text, field, bullet=True)):
                errors.append(f"{location}: inactive template contains a real {field}")
    if status in {"ready", "issued"} and not _real(
        _section_field(text, "### Project Acceptance", "Acceptance")
    ):
        errors.append(f"{location}: ready Final Delivery Report requires Project Acceptance")
    if status == "issued":
        if not _real(_field(text, "Intended recipient", bullet=True)):
            errors.append(f"{location}: issued Final Delivery Report requires a real recipient")
        if not _real(_section_field(text, "## Final Decision", "Delivery evidence")):
            errors.append(f"{location}: issued Final Delivery Report requires delivery evidence")
    if _section_field(text, "## Deployment and Release State", "Release authorized") != "yes" and _section_field(
        text, "## Deployment and Release State", "Release result"
    ) in {"released", "created", "executed"}:
        errors.append(f"{location}: Final Report must not claim an unauthorized release")
    if _section_field(text, "## Deployment and Release State", "Deployment authorized") != "yes" and _section_field(
        text, "## Deployment and Release State", "Deployment result"
    ) in {"deployed", "executed"}:
        errors.append(f"{location}: Final Report must not claim an unauthorized deployment")
    if _section_field(text, "## Final Decision", "Project status source") != "PROJECT.md":
        errors.append(f"{location}: Final Report must not own Project status")
    if re.search(r"Final (?:Delivery )?Report (?:owns|is|becomes).{0,40}Project status", text, re.I):
        errors.append(f"{location}: Final Report must not own Project status")
    for line in text.splitlines():
        lowered = line.casefold()
        if any(negative in lowered for negative in ("must not", "does not", "without")):
            continue
        if re.search(r"(?:copy|include|append).{0,40}(?:complete|full) (?:Task |Finding )?Ledger", line, re.I):
            errors.append(f"{location}: Final Report must not copy a complete Ledger")
        if re.search(r"(?:copy|include|append).{0,40}(?:complete|full) (?:chat|conversation) history", line, re.I):
            errors.append(f"{location}: Final Report must not copy complete conversation history")


def validate_project_template(root: Path, errors: list[str]) -> None:
    location = ".looppilot/PROJECT-TEMPLATE.md"
    text = (root / location).read_text(encoding="utf-8")
    for heading in (
        "## Delivery Mode", "## Project Closure Relationships",
        "### Mandatory Loops", "### Cross-Loop Validation",
        "### Release Requirement", "### Final Checkpoint",
        "### Final Delivery Report", "### Project Status Authority",
        "### Project Closure Gate",
    ):
        if heading not in text.splitlines():
            errors.append(f"{location}: missing Phase 5 heading {heading!r}")
    if _field(text, "Status") != "inactive":
        errors.append(f"{location}: Project template must remain inactive")
    if "`PROJECT.md` is the only authority for Project status" not in _normalized(text):
        errors.append(f"{location}: PROJECT.md must remain the Project status authority")


def validate_project_closure_protocol(root: Path, errors: list[str]) -> None:
    location = PROJECT_CLOSURE_PROTOCOL
    text = (root / location).read_text(encoding="utf-8")
    required = (
        "Project Closure", "Delivery-only", "Release-required", "Cross-Loop Validation",
        "Goal-to-Evidence Mapping", "Project Spec Review", "Project Standards Review",
        "Project Functional Acceptance", "Project Engineering Acceptance",
        "Project Delivery Acceptance", "Project Closure Gate", "remediation Loop",
        "Final Checkpoint", "Final Delivery Report", "Release Readiness",
        "PROJECT.md", "LOOP-MAP.md", "TASK-LEDGER.md", "FINDING-LEDGER.md",
        "CHECKPOINT.md", "Phase 6",
    )
    for phrase in required:
        if phrase not in text:
            errors.append(f"{location}: missing Project Closure protocol term {phrase!r}")
    for value in VALIDATION_STATUSES | ACCEPTANCE_STATUSES | READINESS_STATUSES | REPORT_STATUSES:
        if f"`{value}`" not in text:
            errors.append(f"{location}: missing status declaration {value!r}")
    normalized = _normalized(text)
    invariants = (
        "`PROJECT.md` is the only authority for Project status",
        "`LOOP-MAP.md` is the only authority for Loop status",
        "`TASK-LEDGER.md` is the only authority for Task status",
        "`FINDING-LEDGER.md` is the only authority for Finding status",
        "`CHECKPOINT.md` is the only Recovery authority",
    )
    for invariant in invariants:
        if invariant not in normalized:
            errors.append(f"{location}: missing state-source invariant {invariant!r}")
    if "five Loop Barriers remain unchanged" not in normalized:
        errors.append(f"{location}: Project Closure Gate must not alter the five Loop Barriers")
    for line in text.splitlines():
        lowered = line.casefold()
        if "project finding ledger" not in lowered:
            continue
        if any(negative in lowered for negative in ("must not", "does not", "do not", "not create", "not maintain")):
            continue
        if re.search(r"(?:create|maintain|use|stores? status in).{0,30}Project Finding Ledger", line, re.I):
            errors.append(f"{location}: Project Finding must not use a parallel Project Finding Ledger")
    if "PROJECT-CLOSED" not in text or "Validate a new explicit user instruction" not in text:
        errors.append(f"{location}: missing terminal Final Checkpoint reopen condition")
    if "does not automate" not in text or "behaviorally unverified" not in text:
        errors.append(f"{location}: protocol must disclose its static validation boundary")


def validate_project_closure(root: Path, errors: list[str]) -> None:
    """Validate Phase 5 artifacts without executing or mutating Project state."""
    validate_cross_loop(root, errors)
    validate_project_acceptance(root, errors)
    validate_release_readiness(root, errors)
    validate_final_report(root, errors)
    validate_project_template(root, errors)
    validate_project_closure_protocol(root, errors)
