"""Validate Phase 4 Full Loop checkpoint and context-recovery contracts."""

from __future__ import annotations

import re
from pathlib import Path

from full_loop_validation import EMPTY_VALUES, _field, _normalized, _plain, _require_lines, _section_lines


FULL_LOOP_ROOT = ".looppilot/full-loop"
PHASE_FOUR_PROTOCOL = "docs/full-loop-checkpoint-and-context-recovery.md"
FULL_LOOP_RECOVERY_FILES = (
    f"{FULL_LOOP_ROOT}/CHECKPOINT-TEMPLATE.md",
    f"{FULL_LOOP_ROOT}/CONTEXT-COMPACTION-TEMPLATE.md",
    f"{FULL_LOOP_ROOT}/RESUME-VALIDATION-TEMPLATE.md",
    PHASE_FOUR_PROTOCOL,
)
CHECKPOINT_STATUSES = {
    "inactive", "draft", "ready", "budget-stopped", "resuming", "validated",
    "stale", "superseded", "blocked", "invalid",
}
CONTEXT_PRESSURES = {"unknown", "normal", "elevated", "high", "critical"}
BUDGET_STATES = {
    "unbounded-unknown", "bounded", "healthy", "constrained", "high-pressure",
    "critical", "budget-stopped", "exhausted", "not-applicable",
}
MANIFEST_STATUSES = {"inactive", "draft", "ready", "superseded", "invalid"}
RESUME_VALIDATION_STATUSES = {
    "inactive", "in-progress", "validated", "validated-with-corrections",
    "blocked", "invalid-checkpoint", "replan-required", "cancelled",
}
CHECKPOINT_ID_PATTERN = re.compile(r"^CHECKPOINT-\d{3,}$")
RESUME_ITEM_PATTERN = re.compile(
    r"^(?:TASK-\d{3,}(?:-R\d+)?|FINDING-\d{3,}|INTEGRATION-\d{3,}|"
    r"REVIEW-\d{3,}|BARRIER-[A-Z0-9-]+|VALIDATION-[A-Z0-9-]+)$"
)
GIT_HEAD_PATTERN = re.compile(r"^[0-9a-f]{7,64}$", re.IGNORECASE)
PLACEHOLDERS = EMPTY_VALUES | {
    "no", "unknown", "not-inspected", "not-evaluated", "not-created",
    "yyyy-mm-dd", "none.",
}

CHECKPOINT_HEADINGS = (
    "## Identity", "## Recovery Boundary", "## Current Execution State",
    "## Verified Completed Work", "## Unfinished Work", "## Open Blockers",
    "## Open Major Findings", "## Pending Decisions", "## Authority State",
    "## Required Context", "## Context Exclusions",
    "## Evidence Requiring Revalidation", "## Exact Resume Point",
    "## Next Highest-Value Action", "## Budget Stop Record",
    "## Recovery Readiness", "## Honesty Boundary",
)
MANIFEST_HEADINGS = (
    "## Identity", "## Current Objective", "## Must Load", "## Load On Demand",
    "## Must Not Load by Default", "## Authoritative Sources",
    "## Relevant Detailed Artifacts", "## Compacted Facts",
    "## Discarded or Archived Context", "## Uncertainty and Revalidation",
    "## Token and Context Rationale", "## Authority Note",
)
RESUME_HEADINGS = (
    "## Identity", "## Latest User Instruction Check", "## Repository Reality Check",
    "## Authoritative State Check", "## Referenced Artifact Check",
    "## Evidence Revalidation", "## Capability Check", "## Detected Conflicts",
    "## Corrections Applied", "## Invalidated Claims",
    "## Resume Point Validation", "## Validation Decision", "## Authority Note",
)


def _template_text(root: Path, filename: str, errors: list[str]) -> tuple[str, str]:
    location = f"{FULL_LOOP_ROOT}/{filename}"
    text = (root / location).read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or "TEMPLATE" not in lines[0]:
        errors.append(f"{location}: title must identify the file as TEMPLATE")
    if _field(text, "Template Status") != "inactive":
        errors.append(f"{location}: Template Status must remain inactive")
    return location, text


def _require_fields(text: str, fields: tuple[str, ...], location: str, errors: list[str]) -> None:
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


def _section_has_real_content(text: str, heading: str) -> bool:
    for line in _section_lines(text, heading):
        stripped = line.strip().lstrip("-").strip().rstrip(".")
        if not stripped or stripped.startswith("|") or stripped.startswith("There "):
            continue
        if stripped.casefold() not in PLACEHOLDERS:
            return True
    return False


def _table_has_real_row(text: str, heading: str) -> bool:
    rows = [line.strip() for line in _section_lines(text, heading) if line.strip().startswith("|")]
    for row in rows[2:]:
        cells = [_plain(cell).casefold() for cell in row.strip("|").split("|")]
        if cells and cells[0] not in PLACEHOLDERS:
            return True
    return False


def _section_text(text: str, heading: str) -> str:
    return "\n".join(_section_lines(text, heading))


def _invalid_private_reasoning_claim(text: str) -> bool:
    for line in text.splitlines():
        if not re.search(
            r"(?:must load|includes?|contains?|record(?:s|ed)?)[^\n]{0,60}"
            r"(?:private chain-of-thought|hidden reasoning)", line, re.IGNORECASE,
        ):
            continue
        if not re.search(
            r"(?:must not|does not|cannot|do not)[^\n]{0,60}"
            r"(?:private chain-of-thought|hidden reasoning)", line, re.IGNORECASE,
        ):
            return True
    return False


def _validate_resume_point(text: str, location: str, errors: list[str], required: bool) -> None:
    if text.splitlines().count("## Exact Resume Point") != 1:
        errors.append(f"{location}: exactly one primary Resume Point is required")
        return
    fields = (
        "Resume item", "Resume action", "Required inputs", "Required tool or capability",
        "Expected observable result", "Stop or escalation condition",
    )
    _require_fields(text, fields, location, errors)
    values = {field: _field(text, field, bullet=True) for field in fields}
    if not required:
        return
    for field in fields:
        if not _real(values[field]):
            errors.append(f"{location}: ready Checkpoint requires non-empty {field}")
    item = values["Resume item"]
    if _real(item) and not RESUME_ITEM_PATTERN.fullmatch(_plain(item or "")):
        errors.append(f"{location}: invalid Resume item format {item!r}")
    action = _normalized(values["Resume action"] or "").casefold()
    if any(phrase in action for phrase in (
        "continue previous work", "finish the task", "check what remains",
        "proceed as before", "resume normally",
    )):
        errors.append(f"{location}: Resume action is vague and not actionable")


def validate_checkpoint(root: Path, errors: list[str]) -> None:
    location, text = _template_text(root, "CHECKPOINT-TEMPLATE.md", errors)
    _require_lines(text, CHECKPOINT_HEADINGS, location, errors)
    _require_fields(text, (
        "Checkpoint ID", "Project ID", "Loop ID", "Checkpoint Status", "Verified HEAD",
        "Working tree", "Context Pressure", "Budget State", "Commit authorized",
        "Commit result", "Trigger", "Persisted state", "Authoritative state updated",
        "Recovery ready", "Resume Validation reference",
    ), location, errors)
    _require_declared_values(text, CHECKPOINT_STATUSES, "Checkpoint Status", location, errors)
    _require_declared_values(text, CONTEXT_PRESSURES, "Context Pressure", location, errors)
    _require_declared_values(text, BUDGET_STATES, "Budget State", location, errors)

    status = _field(text, "Checkpoint Status", bullet=True)
    if status not in CHECKPOINT_STATUSES:
        errors.append(f"{location}: invalid Checkpoint Status {status!r}")
        status = "invalid"
    checkpoint_id = _field(text, "Checkpoint ID", bullet=True)
    if _real(checkpoint_id) and not CHECKPOINT_ID_PATTERN.fullmatch(checkpoint_id or ""):
        errors.append(f"{location}: invalid Checkpoint ID {checkpoint_id!r}")
    pressure = _field(text, "Context Pressure", bullet=True)
    if pressure not in CONTEXT_PRESSURES:
        errors.append(f"{location}: invalid Context Pressure {pressure!r}")
    budget = _field(text, "Budget State", bullet=True)
    if budget not in BUDGET_STATES:
        errors.append(f"{location}: invalid Budget State {budget!r}")

    if status == "inactive":
        for field in ("Checkpoint ID", "Project ID", "Loop ID", "Verified HEAD"):
            if _real(_field(text, field, bullet=True)):
                errors.append(f"{location}: inactive template contains a real {field}")
        for field in ("Modify", "Delete", "Commit authorized", "Push", "Release", "Deploy"):
            if _field(text, field, bullet=True) == "yes":
                errors.append(f"{location}: inactive template fabricates {field} authority")

    ready = status in {"ready", "budget-stopped", "resuming", "validated"}
    _validate_resume_point(text, location, errors, required=ready)
    if ready:
        if not _real(checkpoint_id):
            errors.append(f"{location}: ready Checkpoint requires a Checkpoint ID")
        recovery = _section_text(text, "## Recovery Boundary")
        for source in ("PROJECT.md", "LOOP-MAP.md", "TASK-LEDGER.md", "FINDING-LEDGER.md", "CHECKPOINT.md"):
            if source not in recovery:
                errors.append(f"{location}: ready Checkpoint missing authoritative state source {source!r}")

    if status == "budget-stopped":
        if not _real(_field(text, "Trigger", bullet=True)):
            errors.append(f"{location}: budget-stopped Checkpoint requires Trigger")
        if not _real(_field(text, "Persisted state", bullet=True)):
            errors.append(f"{location}: budget-stopped Checkpoint requires persisted state")
        if not _real(_field(text, "Authoritative state updated", bullet=True)):
            errors.append(f"{location}: budget-stopped Checkpoint requires authoritative state update record")
        if not _section_has_real_content(text, "## Unfinished Work"):
            errors.append(f"{location}: budget-stopped Checkpoint requires unfinished work")
    if status == "validated" and not (
        _real(_field(text, "Resume Validation reference", bullet=True))
        or _field(text, "Verified", bullet=True) == "yes"
    ):
        errors.append(f"{location}: validated Checkpoint requires Resume Validation evidence")
    if status == "superseded" and not _real(_field(text, "Superseded by", bullet=True)):
        errors.append(f"{location}: superseded Checkpoint requires replacement reference")
    if status == "invalid" and _field(text, "Recovery ready", bullet=True) == "yes":
        errors.append(f"{location}: invalid Checkpoint cannot be recovery-ready")
    recovery_ready = _field(text, "Recovery ready", bullet=True)
    if status == "ready" and recovery_ready != "yes":
        errors.append(f"{location}: ready Checkpoint requires Recovery ready: yes")
    if recovery_ready == "yes" and status not in {"ready", "budget-stopped", "validated"}:
        errors.append(f"{location}: Checkpoint status {status!r} cannot claim recovery-ready")
    if _field(text, "Commit authorized", bullet=True) != "yes" and (
        _field(text, "Commit result", bullet=True) or ""
    ).casefold() in {"created", "committed", "commit-created"}:
        errors.append(f"{location}: created Commit requires explicit authorization")
    normalized = _normalized(text)
    for source in ("Loop", "Task", "Finding"):
        if re.search(rf"Checkpoint (?:owns|is the authority for) {source} status", normalized, re.I):
            errors.append(f"{location}: Checkpoint must not own {source} status")
    if _invalid_private_reasoning_claim(text):
        errors.append(f"{location}: Checkpoint must not contain private chain-of-thought")
    if "`CHECKPOINT.md` is the only authoritative recovery entry" not in text:
        errors.append(f"{location}: Checkpoint must declare the single Recovery authority")


def validate_manifest(root: Path, errors: list[str]) -> None:
    location, text = _template_text(root, "CONTEXT-COMPACTION-TEMPLATE.md", errors)
    _require_lines(text, MANIFEST_HEADINGS, location, errors)
    _require_fields(text, (
        "Manifest ID", "Checkpoint", "Manifest Status", "Context signal", "Selection rationale",
    ), location, errors)
    _require_declared_values(text, MANIFEST_STATUSES, "Manifest Status", location, errors)
    status = _field(text, "Manifest Status", bullet=True)
    if status not in MANIFEST_STATUSES:
        errors.append(f"{location}: invalid Manifest Status {status!r}")
        status = "invalid"
    checkpoint = _field(text, "Checkpoint", bullet=True)
    if status == "ready":
        if not _real(checkpoint) or not CHECKPOINT_ID_PATTERN.fullmatch(checkpoint or ""):
            errors.append(f"{location}: ready Manifest requires a Checkpoint reference")
        if not _table_has_real_row(text, "## Must Load"):
            errors.append(f"{location}: ready Manifest requires non-empty Must Load")
    excluded = _section_text(text, "## Must Not Load by Default")
    for source in ("PROJECT.md", "LOOP-MAP.md", "TASK-LEDGER.md", "FINDING-LEDGER.md", "CHECKPOINT.md"):
        if source in excluded:
            errors.append(f"{location}: Must Not Load cannot exclude current authority {source!r}")
    if "- Source:" not in _section_text(text, "## Compacted Facts"):
        errors.append(f"{location}: Compacted Facts must require Source")
    if re.search(r"must load[^\n]{0,60}(?:complete|full) (?:conversation|chat) history", text, re.I):
        errors.append(f"{location}: Manifest must not require complete conversation history")
    if re.search(r"Manifest (?:is|becomes|owns) (?:the )?(?:only )?Recovery authority", text, re.I):
        errors.append(f"{location}: Manifest must not be a Recovery authority")
    if re.search(r"(?<!not )(?:copy|include|duplicate)[^\n]{0,40}complete (?:Task |Finding )?Ledger", text, re.I):
        errors.append(f"{location}: Manifest must not duplicate a complete Ledger")
    if _invalid_private_reasoning_claim(text):
        errors.append(f"{location}: Manifest must not contain private chain-of-thought")
    if "`CHECKPOINT.md` remains the only authoritative recovery entry" not in text:
        errors.append(f"{location}: Manifest must defer to Checkpoint Recovery authority")


def validate_resume_report(root: Path, errors: list[str]) -> None:
    location, text = _template_text(root, "RESUME-VALIDATION-TEMPLATE.md", errors)
    _require_lines(text, RESUME_HEADINGS, location, errors)
    _require_fields(text, (
        "Validation ID", "Checkpoint", "Validation Status", "Scope changed", "Actual HEAD",
        "Expected HEAD", "Required Skills available", "Commit authority unchanged",
        "Checkpoint Resume Point", "Still applicable", "Revised Resume Point", "Decision",
        "Safe to resume",
    ), location, errors)
    _require_declared_values(text, RESUME_VALIDATION_STATUSES, "Validation Status", location, errors)
    status = _field(text, "Validation Status", bullet=True)
    if status not in RESUME_VALIDATION_STATUSES:
        errors.append(f"{location}: invalid Validation Status {status!r}")
        status = "invalid-checkpoint"
    safe = _field(text, "Safe to resume", bullet=True)
    if status in {"validated", "validated-with-corrections"} and safe != "yes":
        errors.append(f"{location}: validated Resume Report requires Safe to resume: yes")
    if status in {"blocked", "invalid-checkpoint", "replan-required", "cancelled"} and safe == "yes":
        errors.append(f"{location}: {status} Resume Report cannot be safe to resume")
    if status == "validated-with-corrections" and not _section_has_real_content(text, "## Corrections Applied"):
        errors.append(f"{location}: validated-with-corrections requires Corrections Applied")
    actual = _field(text, "Actual HEAD", bullet=True)
    expected = _field(text, "Expected HEAD", bullet=True)
    if (
        actual and expected and GIT_HEAD_PATTERN.fullmatch(actual)
        and GIT_HEAD_PATTERN.fullmatch(expected) and actual.casefold() != expected.casefold()
        and not (_section_has_real_content(text, "## Detected Conflicts") and (
            _section_has_real_content(text, "## Corrections Applied")
            or status in {"blocked", "invalid-checkpoint", "replan-required"}
        ))
    ):
        errors.append(f"{location}: actual HEAD conflicts with expected HEAD without resolution")
    if _field(text, "Scope changed", bullet=True) == "yes" and (
        _field(text, "Still applicable", bullet=True) == "yes"
        and not _real(_field(text, "Revised Resume Point", bullet=True))
    ):
        errors.append(f"{location}: changed Scope cannot unconditionally reuse the old Resume Point")
    if _field(text, "Commit authority unchanged", bullet=True) == "no" and re.search(
        r"(?:retain|inherit|continue using)[^\n]{0,40}commit (?:authority|permission)", text, re.I
    ):
        errors.append(f"{location}: changed commit authority must not be inherited")
    if status in {"validated", "validated-with-corrections"} and _field(
        text, "Required Skills available", bullet=True
    ) == "no":
        errors.append(f"{location}: unavailable required Skill prevents validated status")
    if re.search(r"Resume Validation (?:may|can|is authorized to) (?:expand|change) (?:Project |Loop )?Scope", text, re.I):
        errors.append(f"{location}: Resume Validation must not expand Scope")
    if re.search(r"Resume Validation (?:may|can|is authorized to) grant commit", text, re.I):
        errors.append(f"{location}: Resume Validation must not expand commit authority")
    if re.search(r"Resume (?:Report|Validation) (?:is|becomes|owns) (?:the )?(?:only )?Recovery authority", text, re.I):
        errors.append(f"{location}: Resume Report must not be a Recovery authority")
    if "`CHECKPOINT.md` remains the only authoritative recovery entry" not in text:
        errors.append(f"{location}: Resume Report must defer to Checkpoint Recovery authority")


def validate_phase_four_protocol(root: Path, errors: list[str]) -> None:
    text = (root / PHASE_FOUR_PROTOCOL).read_text(encoding="utf-8")
    location = PHASE_FOUR_PROTOCOL
    _require_lines(text, (
        "## Recovery Flow", "## Checkpoint Contract", "## Recovery Boundary",
        "## Context Pressure and Budget State", "## Minimal Safe Unit and Budget Stop",
        "## Context Compaction Manifest", "## Resume Validation",
        "## Fact Priority and Exact Resume Point", "## Artifact Boundaries",
        "## Staleness, Invalidity, and Supersession",
        "## Intra-Loop and Inter-Loop Recovery", "## Static Validation Boundary",
    ), location, errors)
    for pressure in CONTEXT_PRESSURES:
        if f"`{pressure}`" not in text:
            errors.append(f"{location}: missing Context Pressure {pressure!r}")
    for status in CHECKPOINT_STATUSES:
        if f"`{status}`" not in text:
            errors.append(f"{location}: missing Checkpoint Status {status!r}")
    normalized = _normalized(text)
    for invariant in (
        "Budget pressure MUST NOT skip Spec Review.",
        "Budget pressure MUST NOT skip Standards Review.",
        "exactly one primary Resume Point",
        "`CHECKPOINT.md` is the only authoritative recovery entry",
        "At `critical`", "At `high`",
    ):
        if _normalized(invariant) not in normalized:
            errors.append(f"{location}: missing recovery invariant {invariant!r}")
    for pattern, message in (
        (r"critical pressure (?:may|can|must|should) (?:create|start) (?:a )?(?:new )?Worker", "critical pressure must not create Workers"),
        (r"Budget Stop (?:may|can) skip Spec Review", "Budget Stop must not skip Spec Review"),
        (r"Budget Stop (?:may|can) skip Standards Review", "Budget Stop must not skip Standards Review"),
        (r"Budget Stop (?:may|can) mark partial[^\n]{0,30}completed", "Budget Stop must not mark partial work completed"),
        (r"Budget Stop (?:may|can) close (?:a )?(?:blocker )?Finding", "Budget Stop must not close Findings"),
        (r"Budget Stop (?:may|can) (?:grant|expand) push", "Budget Stop must not expand push authority"),
    ):
        if re.search(pattern, text, re.I):
            errors.append(f"{location}: {message}")


def validate_recovery_authority(root: Path, errors: list[str]) -> None:
    paths = (
        (".looppilot/full-loop/README.md", "Full Loop README"),
        (".looppilot/HANDOFF.md", "Handoff"),
        (".looppilot/CHECKLIST.md", "Checklist"),
        (f"{FULL_LOOP_ROOT}/LOOP-CLOSURE-TEMPLATE.md", "Closure"),
    )
    for relative, label in paths:
        text = (root / relative).read_text(encoding="utf-8")
        if re.search(
            rf"{label} (?:is|becomes|owns) (?:the )?(?:only )?Recovery authority", text, re.I
        ):
            errors.append(f"{relative}: {label} must not be a Recovery authority")
        if relative.endswith("README.md"):
            for subject in ("Manifest", "Resume Report", "Handoff", "Checklist", "Closure"):
                if re.search(
                    rf"{subject} (?:is|becomes|owns) (?:the )?(?:only )?Recovery authority",
                    text,
                    re.I,
                ):
                    errors.append(f"{relative}: {subject} must not be a Recovery authority")


def validate_full_loop_recovery(root: Path, errors: list[str]) -> None:
    """Validate Phase 4 contracts without performing recovery actions."""
    validate_checkpoint(root, errors)
    validate_manifest(root, errors)
    validate_resume_report(root, errors)
    validate_phase_four_protocol(root, errors)
    validate_recovery_authority(root, errors)
