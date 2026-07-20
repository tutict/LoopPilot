"""Validate Phase 7 evidence calibration without implementing a runtime."""

from __future__ import annotations

import re
from pathlib import Path

from full_loop_execution_validation import (
    CLOSURE_STATUSES,
    DELIVERY_STATUSES,
    INTEGRATION_STATUSES,
    REVIEWER_TYPES,
    REVIEW_STATUSES,
)
from full_loop_recovery_validation import (
    CHECKPOINT_STATUSES,
    MANIFEST_STATUSES,
    RESUME_VALIDATION_STATUSES,
)
from full_loop_validation import (
    CONTRACT_STATUSES,
    FINDING_SEVERITIES,
    FINDING_STATUSES,
    LEDGER_STATUSES,
    LOOP_MAP_STATUSES,
    LOOP_STATUSES,
)
from project_closure_validation import (
    ACCEPTANCE_STATUSES,
    READINESS_STATUSES,
    REPORT_STATUSES,
    VALIDATION_STATUSES,
)


EVALUATION_CALIBRATION_FILES = (
    "docs/evaluation-synthesis-and-protocol-calibration.md",
    "docs/mode-selection-and-escalation.md",
    "docs/protocol-load-profiles.md",
    "docs/mmgh-behavioral-evidence.md",
    "scripts/evaluation_calibration_validation.py",
    "tests/test_evaluation_calibration.py",
)

CORE_PROMPT_BASELINE_LINES = 547
CORE_PROMPT_MAX_LINES = 601

DOCUMENT_REQUIREMENTS = {
    "docs/evaluation-synthesis-and-protocol-calibration.md": (
        "## Evidence Levels",
        "### Observed",
        "### Repeated Pattern",
        "### Provisional Heuristic",
        "### Normative Invariant",
        "### Unverified",
        "documentation labels",
        "not lifecycle states",
        "strict same-task",
        "not generally validated",
        "Phase 8, Cross-project Replication and Controlled Comparison: not implemented",
    ),
    "docs/mode-selection-and-escalation.md": (
        "## Authority and Timing",
        "The Supervisor decides the mode",
        "The Integrator records that decision",
        "does not own Project Status or Loop Status",
        "before implementation",
        "## Lightweight Tendency",
        "file count is supporting evidence, not the decision authority",
        "## Full Loop Hard Triggers",
        "not an automatic runtime decision",
        "## Lightweight Escalation",
        "Major or Blocker Finding",
        "repass Contract Barrier",
        "## Lightweight Artifact Budget",
        "four to seven",
        "not a hard limit",
        "## Product, Protocol, and Infrastructure Boundary",
        "Execution Infrastructure Incident",
        "not a new role, Finding status, severity, Ledger, or authority",
        "Record incidents in a Worker Delivery, Integration Record, Review Report, Handoff, Results, or Checkpoint",
        "A 429 or timeout does not automatically become a Product Finding",
        "A Product Finding concerns",
        "A Protocol or Process Finding concerns",
        "Missing verification can block Review or Closure",
        "## Specialist Reviewers",
        "Spec and Standards are permanent independent axes",
        "SSRF",
        "foreign keys",
        "Web/Tauri",
        "runbooks",
        "screen readers",
        "Reviewers do not modify the implementation",
        "## Architecture Selection",
    ),
    "docs/protocol-load-profiles.md": (
        "## Core Profile",
        "## Lightweight Profile",
        "## Full Loop Profile",
        "Task and Finding Ledgers",
        "## Project Finalization Profile",
        "does not default to Full Loop history",
        "does not load this profile",
        "does not load all specialists by default",
        "only when multiple mandatory Loops",
        "verification required to resume",
    ),
    "docs/mmgh-behavioral-evidence.md": (
        "read-only evidence source",
        "not claim a strict A/B comparison",
        "not generally validated",
        "experiment/looppilot-mmgh-exp-001",
        "23ae0246c0fee309a728eb6c1c1dbaba8f50435d",
        "experiment/looppilot-mmgh-exp-002",
        "afa5540f385b06bd9ebf7c6cd6e7188915d05e96",
        "experiment/looppilot-mmgh-exp-003",
        "90177dad76d84dac5386bbd6e010e0c4a732aef4",
        "experiment/looppilot-mmgh-exp-004",
        "bf07d0f8b9e9a67b92bfb672c8953e2de79ded29",
        "54/60",
        "60/66",
        "72/78",
        "## Observed Outcomes",
        "## Repeated Patterns",
        "## Provisional Heuristics",
        "## Contradictions and Limits",
        "## Unverified Claims",
        "## Protocol Changes Supported",
        "## Protocol Changes Not Supported",
        "Unverified",
    ),
}

TEMPLATE_REQUIREMENTS = {
    ".looppilot/PROJECT-TEMPLATE.md": (
        "## Mode Selection",
        "- Candidate mode:",
        "- Mode evidence:",
        "- Full Loop hard triggers considered:",
        "- Artifact Budget target:",
        "- Escalation conditions:",
        "- Mode decision by Supervisor:",
        "- Mode decision recorded by Integrator:",
    ),
    ".looppilot/full-loop/LOOP-CONTRACT-TEMPLATE.md": (
        "## Mode Decision Context",
        "- Why Full Loop:",
        "- Rejected Lightweight rationale:",
        "- Expected protocol cost:",
        "- Active specialist Reviewers:",
        "- Recovery implications:",
    ),
    ".looppilot/full-loop/WORKER-DELIVERY-TEMPLATE.md": (
        "## Execution Infrastructure Incidents",
    ),
    ".looppilot/full-loop/INTEGRATION-RECORD-TEMPLATE.md": (
        "## Execution Infrastructure Incidents",
    ),
    ".looppilot/full-loop/REVIEW-REPORT-TEMPLATE.md": (
        "- Execution Infrastructure Incident evidence:",
        "does not modify the implementation",
    ),
    ".looppilot/full-loop/CHECKPOINT-TEMPLATE.md": (
        "- Current mode:",
        "## Execution Infrastructure Incidents Affecting Recovery",
    ),
    ".looppilot/full-loop/CONTEXT-COMPACTION-TEMPLATE.md": (
        "## Current Mode and Load Profile",
        "Lightweight recovery does not load Full Loop history by default",
    ),
}

FORBIDDEN_CLAIMS = (
    "Mode is selected after implementation",
    "File count is the decision authority",
    "Integrator decides the mode",
    "Mode Selection owns Project Status",
    "Mode Selection owns Loop Status",
    "Artifact Budget Status:",
    "Artifact Budget is a hard absolute limit",
    "Lightweight defaults to Task Ledger",
    "Lightweight defaults to Finding Ledger",
    "Lightweight defaults to Final Delivery Report",
    "Lightweight defaults to Release Readiness",
    "Lightweight defaults to complete Full Loop history",
    "Lightweight may continue after a Major Finding without escalation",
    "Lightweight may change a Rust contract without escalation",
    "Lightweight may continue after repeated correction without escalation",
    "Lightweight may continue after sensitive-data impact without escalation",
    "Lightweight exceeds seven artifacts without explanation or reassessment",
    "Worker timeout is automatically a Product Blocker",
    "No-output Worker has a completed Delivery",
    "Unavailable Reviewer is an independent Reviewer",
    "Infrastructure Ledger",
    "Full Loop automatically enables all specialist Reviewers",
    "Specialist Review replaces Spec and Standards",
    "Every Full Loop requires DDD",
    "A large DI framework is mandatory",
    "MVVM is mandatory without view coupling",
    "Zero-copy is required without benchmarks",
    "New top-level role:",
    "New authoritative Ledger:",
    "New Loop status:",
    "New Task status:",
    "New Finding status:",
    "New Finding severity:",
    "New Barrier:",
    "New Acceptance layer:",
    "New Recovery authority:",
    "The four experiments establish a strict A/B comparison",
    "MMGH proves universal protocol superiority",
    "MMGH certifies production security",
)

EXPECTED_ENUMS = {
    "Loop Map statuses": {
        "inactive", "active", "partially-completed", "blocked", "completed",
        "cancelled", "budget-stopped",
    },
    "Loop statuses": {
        "planned", "contracted", "executing", "implemented", "integrating",
        "integrated", "reviewing", "reworking", "accepted", "committed",
        "checkpointed", "closed", "blocked", "failed", "budget-exhausted",
        "cancelled", "replan-required",
    },
    "Contract statuses": {"inactive", "draft", "ready", "approved", "superseded"},
    "Ledger statuses": {
        "inactive", "active", "blocked", "completed", "cancelled", "budget-stopped",
    },
    "Finding severities": {"blocker", "major", "minor", "suggestion"},
    "Finding statuses": {
        "open", "triaged", "assigned", "in-rework", "ready-for-review",
        "verified", "closed", "deferred", "risk-accepted", "rejected",
        "duplicate", "reopened",
    },
    "Delivery statuses": {
        "completed", "partial", "blocked", "failed", "scope-change-required",
    },
    "Integration statuses": {
        "inactive", "collecting", "integrating", "blocked", "failed", "integrated",
    },
    "Review statuses": {"inactive", "in-progress", "completed", "blocked", "superseded"},
    "Closure statuses": {
        "inactive", "draft", "ready-for-acceptance", "accepted", "blocked", "superseded",
    },
    "Checkpoint statuses": {
        "inactive", "draft", "ready", "budget-stopped", "resuming", "validated",
        "stale", "superseded", "blocked", "invalid",
    },
    "Manifest statuses": {"inactive", "draft", "ready", "superseded", "invalid"},
    "Resume statuses": {
        "inactive", "in-progress", "validated", "validated-with-corrections",
        "blocked", "invalid-checkpoint", "replan-required", "cancelled",
    },
    "Cross-Loop validation statuses": {
        "inactive", "planned", "in-progress", "passed", "passed-with-limitations",
        "failed", "blocked", "superseded",
    },
    "Project acceptance statuses": {
        "inactive", "draft", "under-review", "accepted", "accepted-with-risks",
        "blocked", "rejected", "superseded",
    },
    "Release readiness statuses": {
        "inactive", "not-applicable", "in-progress", "ready",
        "ready-with-accepted-risks", "blocked", "cancelled", "superseded",
    },
    "Final report statuses": {"inactive", "draft", "ready", "issued", "superseded"},
}

EXPECTED_TASK_STATUSES = {
    "proposed", "assigned", "in-progress", "submitted", "under-review",
    "revision-requested", "approved", "rejected", "blocked", "cancelled",
    "integrated",
}
EXPECTED_REVIEWER_TYPES = {
    "spec", "standards", "domain", "data", "concurrency", "security",
    "operations", "performance", "architecture", "frontend", "compatibility",
    "test", "code-quality", "accessibility", "compliance", "factual-accuracy",
    "citation", "methodology", "structure", "visual", "domain-expert",
}


def _require(text: str, values: tuple[str, ...], location: str, errors: list[str]) -> None:
    normalized = re.sub(r"\s+", " ", text).casefold()
    for value in values:
        if re.sub(r"\s+", " ", value).casefold() not in normalized:
            errors.append(f"{location}: missing Phase 7 requirement {value!r}")


def _section_subheadings(text: str, heading: str) -> set[str]:
    lines = text.splitlines()
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return set()
    result: set[str] = set()
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if line.startswith("### "):
            result.add(line)
    return result


def validate_evaluation_calibration(
    root: Path,
    errors: list[str],
    logical_roles: set[str],
    task_statuses: set[str],
) -> None:
    """Check static Phase 7 contracts; never decide or execute a mode."""

    for location, requirements in DOCUMENT_REQUIREMENTS.items():
        path = root / location
        if path.is_file():
            _require(path.read_text(encoding="utf-8"), requirements, location, errors)

    for location, requirements in TEMPLATE_REQUIREMENTS.items():
        path = root / location
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            _require(text, requirements, location, errors)
            if "Template Status: inactive" in text and "Template Status: active" in text:
                errors.append(f"{location}: Phase 7 templates must remain inactive")

    markdown = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*.md"))
        if ".git" not in path.parts
    )
    for claim in FORBIDDEN_CLAIMS:
        if claim in markdown:
            errors.append(f"Phase 7 contradiction: {claim}")

    migration = (root / "docs/full-loop-migration-plan.md").read_text(encoding="utf-8")
    _require(
        migration,
        (
            "partially observed through MMGH EXP-001 to EXP-004; not generally validated",
            "## Phase 7: Evidence Synthesis and Protocol Calibration",
            "**Status: implemented statically.**",
            "## Phase 8: Cross-Project Replication and Controlled Comparison",
            "**Status: not implemented.**",
        ),
        "docs/full-loop-migration-plan.md",
        errors,
    )

    enum_values = {
        "Loop Map statuses": LOOP_MAP_STATUSES,
        "Loop statuses": LOOP_STATUSES,
        "Contract statuses": CONTRACT_STATUSES,
        "Ledger statuses": LEDGER_STATUSES,
        "Finding severities": FINDING_SEVERITIES,
        "Finding statuses": FINDING_STATUSES,
        "Delivery statuses": DELIVERY_STATUSES,
        "Integration statuses": INTEGRATION_STATUSES,
        "Review statuses": REVIEW_STATUSES,
        "Closure statuses": CLOSURE_STATUSES,
        "Checkpoint statuses": CHECKPOINT_STATUSES,
        "Manifest statuses": MANIFEST_STATUSES,
        "Resume statuses": RESUME_VALIDATION_STATUSES,
        "Cross-Loop validation statuses": VALIDATION_STATUSES,
        "Project acceptance statuses": ACCEPTANCE_STATUSES,
        "Release readiness statuses": READINESS_STATUSES,
        "Final report statuses": REPORT_STATUSES,
    }
    for name, expected in EXPECTED_ENUMS.items():
        if enum_values[name] != expected:
            errors.append(f"Phase 7 freeze: {name} changed")

    if logical_roles != {"supervisor", "worker", "reviewer", "integrator"}:
        errors.append("Phase 7 freeze: top-level roles changed")
    if task_statuses != EXPECTED_TASK_STATUSES:
        errors.append("Phase 7 freeze: Task statuses changed")
    if REVIEWER_TYPES != EXPECTED_REVIEWER_TYPES:
        errors.append("Phase 7 freeze: Reviewer types changed")

    allowed_ledgers = {"TASK-LEDGER-TEMPLATE.md", "FINDING-LEDGER-TEMPLATE.md"}
    unexpected_ledgers = {
        path.name
        for path in (root / ".looppilot").rglob("*-LEDGER.md")
        if path.name not in allowed_ledgers
    }
    if unexpected_ledgers:
        errors.append(
            "Phase 7 freeze: unexpected authoritative Ledger artifacts "
            + ", ".join(sorted(unexpected_ledgers))
        )

    contract = (root / ".looppilot/full-loop/LOOP-CONTRACT-TEMPLATE.md").read_text(
        encoding="utf-8"
    )
    barriers = _section_subheadings(contract, "## Barriers")
    expected_barriers = {
        "### Contract Barrier", "### Implementation Barrier",
        "### Integration Barrier", "### Review Barrier", "### Closure Barrier",
    }
    if barriers != expected_barriers:
        errors.append("Phase 7 freeze: Full Loop Barriers changed")
    acceptance = _section_subheadings(contract, "## Acceptance Criteria")
    if acceptance != {
        "### Functional Acceptance", "### Engineering Acceptance",
        "### Delivery Acceptance",
    }:
        errors.append("Phase 7 freeze: Loop acceptance layers changed")

    checkpoint = (root / ".looppilot/full-loop/CHECKPOINT-TEMPLATE.md").read_text(
        encoding="utf-8"
    )
    if "`CHECKPOINT.md` is the only authoritative recovery entry" not in checkpoint:
        errors.append("Phase 7 freeze: Checkpoint recovery authority changed")
    project = (root / ".looppilot/PROJECT-TEMPLATE.md").read_text(encoding="utf-8")
    if "`PROJECT.md` is the only authority for Project status" not in project:
        errors.append("Phase 7 freeze: PROJECT.md authority changed")

    line_count = sum(
        len((root / name).read_text(encoding="utf-8").splitlines())
        for name in ("SKILL.md", "AGENTS.md")
    )
    if line_count > CORE_PROMPT_MAX_LINES:
        errors.append(
            "Core prompt budget exceeded: "
            f"baseline {CORE_PROMPT_BASELINE_LINES}, maximum {CORE_PROMPT_MAX_LINES}, "
            f"observed {line_count}"
        )

    if not {"spec", "standards"} <= REVIEWER_TYPES:
        errors.append("Phase 7 freeze: permanent review axes changed")
