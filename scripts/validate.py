#!/usr/bin/env python3
"""Run deterministic maintenance checks for the LoopPilot repository."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from yaml.constructor import ConstructorError
from engineering_validation import validate_loop_engineering
from full_loop_execution_validation import (
    FULL_LOOP_EXECUTION_FILES,
    validate_full_loop_execution,
)
from full_loop_validation import FULL_LOOP_FILES, validate_full_loop
from protocol_validation import (
    validate_repository_extensions,
    validate_review_protocol,
    validate_task_skill_routing,
)


REQUIRED_FILES = (
    "SKILL.md",
    "AGENTS.md",
    ".looppilot/README.md",
    ".looppilot/STATE.md",
    ".looppilot/HANDOFF.md",
    ".looppilot/DECISIONS.md",
    ".looppilot/CHECKLIST.md",
    ".looppilot/RESEARCH-TEMPLATE.md",
    ".looppilot/PROJECT-TEMPLATE.md",
    "README.md",
    ".looppilot/DELEGATION.md",
    ".looppilot/tasks/README.md",
    ".looppilot/tasks/TASK-TEMPLATE.md",
    ".looppilot/tasks/REVIEW-TEMPLATE.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "agents/openai.yaml",
    ".github/workflows/validate.yml",
    "requirements-dev.txt",
    "scripts/validate.py",
    "scripts/protocol_validation.py",
    "scripts/engineering_validation.py",
    "scripts/full_loop_validation.py",
    "scripts/full_loop_execution_validation.py",
    "docs/validation.md",
    "docs/loop-engineering-model.md",
    "docs/project-engineering-context.md",
    "docs/protocol-modes-and-state-sources.md",
    "docs/architecture-pattern-selection.md",
    "docs/project-closure.md",
    "docs/full-loop-migration-plan.md",
    "docs/full-loop-contracts-and-ledgers.md",
    "evaluations/README.md",
    "docs/host-capabilities.md",
    "evaluations/codex/README.md",
    "evaluations/templates/environment.md",
    "evaluations/templates/prompt.md",
    "evaluations/templates/trace.md",
    "evaluations/templates/score.md",
    "docs/lifecycle.md",
    "docs/multi-agent-coordination.md",
    "docs/safety-and-stopping.md",
    "tests/evaluation-rubric.md",
    "tests/scenarios.md",
    "tests/test_loop_engineering_architecture.py",
    "tests/test_full_loop_templates.py",
    "tests/test_full_loop_delivery_review_closure.py",
    *FULL_LOOP_FILES,
    *FULL_LOOP_EXECUTION_FILES,
)
SKILL_WORD_RANGE = range(1500, 2501)
FRONTMATTER_PATTERN = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
MERMAID_PATTERN = re.compile(
    r"^```mermaid[ \t]*\r?\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL
)
UPDATED_PATTERN = re.compile(
    r"^Updated:[ \t]*(?:YYYY-MM-DD|\d{4}-\d{2}-\d{2})[ \t]*$", re.MULTILINE
)
STATUS_PATTERN = re.compile(r"^Status:[ \t]*(\S+)[ \t]*$", re.MULTILINE)
TASK_ID_PATTERN = re.compile(r"^TASK-\d{3,}$")
DATE_PATTERN = re.compile(r"^(?:YYYY-MM-DD|\d{4}-\d{2}-\d{2})$")
CREDENTIAL_ASSIGNMENT_PATTERN = re.compile(
    r"^[ \t]*(?:[a-z][a-z0-9_]*_)?(?:api[_ -]?key|access[_ -]?token|token|"
    r"secret|password|cookie|credential)[ \t]*[:=][ \t]*"
    r"(?!none(?:\s|$)|redacted(?:\s|$)|placeholder(?:\s|$)|<)[^\s`]+",
    re.IGNORECASE | re.MULTILINE,
)
STATE_STATUSES = {
    "inactive",
    "active",
    "partially-completed",
    "blocked",
    "completed",
    "budget-stopped",
    "cancelled",
}
HANDOFF_STATUSES = {"none", "active", "completed", "superseded"}
DELEGATION_STATUSES = {
    "inactive",
    "planning",
    "delegating",
    "executing",
    "reviewing",
    "integrating",
    "partially-completed",
    "blocked",
    "completed",
    "cancelled",
    "budget-stopped",
}
TASK_STATUSES = {
    "proposed",
    "assigned",
    "in-progress",
    "submitted",
    "under-review",
    "revision-requested",
    "approved",
    "rejected",
    "blocked",
    "cancelled",
    "integrated",
}
REVIEW_DECISIONS = {
    "approved",
    "revision-requested",
    "rejected",
    "blocked",
}
AUTHORITY_FIELDS = (
    "read",
    "modify",
    "delete",
    "commit",
    "push",
    "release",
    "deploy",
    "external_communication",
)
TASK_REQUIRED_FIELDS = (
    "task_id",
    "parent_goal",
    "status",
    "previous_status",
    "status_changed_by",
    "assigned_role",
    "assigned_to",
    "objective",
    "scope",
    "deliverables",
    "success_criteria",
    "required_evidence",
    "dependencies",
    "research_inputs",
    "skill_assignment",
    "skill_selection",
    "checklist_item",
    "authority",
    "reviewer",
    "integration_owner",
    "revision_count",
    "revision_budget",
    "created",
    "updated",
)
TASK_LIST_FIELDS = (
    "deliverables",
    "success_criteria",
    "required_evidence",
    "dependencies",
)
TASK_TRANSITIONS = {
    "none": {"proposed"},
    "proposed": {"assigned", "cancelled"},
    "assigned": {"in-progress", "blocked", "cancelled"},
    "in-progress": {"submitted", "blocked", "cancelled"},
    "submitted": {"under-review"},
    "under-review": {
        "approved",
        "revision-requested",
        "rejected",
        "blocked",
    },
    "revision-requested": {"in-progress", "cancelled"},
    "approved": {"integrated", "revision-requested"},
    "blocked": {"assigned", "in-progress", "cancelled"},
    "rejected": {"proposed", "cancelled"},
    "integrated": set(),
    "cancelled": set(),
}
TASK_STATUS_OWNERS = {
    "proposed": {"supervisor"},
    "assigned": {"supervisor"},
    "in-progress": {"worker"},
    "submitted": {"worker"},
    "under-review": {"supervisor"},
    "revision-requested": {"reviewer"},
    "approved": {"reviewer"},
    "rejected": {"reviewer"},
    "blocked": {"worker", "reviewer"},
    "cancelled": {"supervisor"},
    "integrated": {"supervisor", "integrator"},
}
LOGICAL_ROLES = {"supervisor", "worker", "reviewer", "integrator"}
REVIEW_REQUIRED_HEADINGS = (
    "## Standards Review",
    "## Spec Review",
    "## Verification Gaps",
    "## Overall Decision Rationale",
    "## Authority Note",
)
SHARED_STATE_HEADINGS = {
    ".looppilot/README.md": (
        "## Purpose",
        "## It Is Not",
        "## When to Create or Update",
        "## Research, Skills, and Parent Checklist",
        "## Source of Truth",
        "## Status Values",
        "## Native Plan Relationship",
        "## Evidence and Update Discipline",
        "## File Responsibilities",
    ),
    ".looppilot/STATE.md": (
        "## Objective",
        "## Success Criteria",
        "## Current Progress",
        "## Verified Evidence",
        "## Blockers",
        "## Native Plan Relationship",
        "## Delegation Relationship",
        "## Checklist Relationship",
        "## Research Relationship",
        "## Context Pressure",
        "## Next Action",
    ),
    ".looppilot/HANDOFF.md": (
        "## Current Objective",
        "## Completed",
        "## Observed Evidence",
        "## Remaining Work",
        "## Blockers",
        "## Risks and Constraints",
        "## Checklist Status",
        "## Resume Point",
        "## Context Pressure",
        "## Active Research Brief",
        "## Active Skill Assignments",
        "## Recommended Next Action",
        "## Do Not Assume",
    ),
    ".looppilot/DECISIONS.md": (
        "## Active Decisions",
        "## Superseded Decisions",
    ),
    ".looppilot/DELEGATION.md": (
        "## Parent Goal",
        "## Active Assignments",
        "## Review Queue",
        "## Revision Queue",
        "## Blocked Tasks",
        "## Conflicts",
        "## Integration Status",
        "## Research Status",
        "## Skill Assignment Summary",
        "## Checklist Status",
        "## Budget Status",
        "## Next Coordination Action",
    ),
}


class UniqueKeySafeLoader(yaml.SafeLoader):
    """SafeLoader variant that rejects duplicate mapping keys."""


def construct_unique_mapping(
    loader: UniqueKeySafeLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[object, object]:
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping
)


@dataclass(frozen=True)
class TaskContractSummary:
    task_id: str
    status: str
    previous_status: str
    status_changed_by: str
    assigned_to: str
    reviewer: str
    revision_count: int


@dataclass(frozen=True)
class MermaidBlock:
    source: Path
    number: int
    content: str

    @property
    def filename(self) -> str:
        stem = "-".join(self.source.with_suffix("").parts)
        return f"{stem}-{self.number}.mmd"


def parse_yaml_mapping(path: Path, text: str) -> dict[object, object]:
    """Parse YAML safely, reject duplicate keys, and require a mapping root."""
    data = yaml.safe_load(text)
    yaml.load(text, Loader=UniqueKeySafeLoader)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    return data


def parse_markdown_frontmatter(path: Path) -> dict[object, object]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        raise ValueError(f"{path.name}: missing or malformed YAML frontmatter")
    return parse_yaml_mapping(path, match.group(1))


def non_empty_string(mapping: dict[object, object], key: str, location: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location}: {key!r} must be a non-empty string")
    return value


def validate_skill_frontmatter(root: Path, errors: list[str]) -> None:
    path = root / "SKILL.md"
    match = FRONTMATTER_PATTERN.match(path.read_text(encoding="utf-8"))
    if not match:
        errors.append("SKILL.md: missing or malformed YAML frontmatter")
        return
    try:
        metadata = parse_yaml_mapping(path, match.group(1))
        if set(metadata) != {"name", "description"}:
            raise ValueError("SKILL.md frontmatter: only name and description are allowed")
        name = non_empty_string(metadata, "name", "SKILL.md frontmatter")
        non_empty_string(metadata, "description", "SKILL.md frontmatter")
        if name != "loop-pilot":
            raise ValueError("SKILL.md frontmatter: name must be 'loop-pilot'")
    except (ConstructorError, ValueError, yaml.YAMLError) as error:
        errors.append(str(error))


def validate_openai_yaml(root: Path, errors: list[str]) -> None:
    path = root / "agents" / "openai.yaml"
    try:
        data = parse_yaml_mapping(path, path.read_text(encoding="utf-8"))
        if set(data) != {"interface"}:
            raise ValueError("agents/openai.yaml: only 'interface' is expected")
        interface = data.get("interface")
        if not isinstance(interface, dict):
            raise ValueError("agents/openai.yaml: 'interface' must be a mapping")
        if set(interface) != {"display_name", "short_description", "default_prompt"}:
            raise ValueError("agents/openai.yaml: unexpected or missing interface field")
        non_empty_string(interface, "display_name", "agents/openai.yaml interface")
        description = non_empty_string(
            interface, "short_description", "agents/openai.yaml interface"
        )
        prompt = non_empty_string(
            interface, "default_prompt", "agents/openai.yaml interface"
        )
        if not 25 <= len(description) <= 64:
            raise ValueError("agents/openai.yaml: short_description must be 25-64 characters")
        if "$loop-pilot" not in prompt:
            raise ValueError("agents/openai.yaml: default_prompt must mention $loop-pilot")
    except (ConstructorError, ValueError, yaml.YAMLError) as error:
        errors.append(str(error))


def validate_yaml_files(root: Path, errors: list[str]) -> None:
    paths = sorted((*root.rglob("*.yaml"), *root.rglob("*.yml")))
    for path in paths:
        try:
            parse_yaml_mapping(path, path.read_text(encoding="utf-8"))
        except (ConstructorError, ValueError, yaml.YAMLError) as error:
            errors.append(str(error))


def require_non_empty_list(
    mapping: dict[object, object], key: str, location: str
) -> list[object]:
    value = mapping.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{location}: {key!r} must be a non-empty list")
    return value


def validate_task_date(
    contract: dict[object, object], key: str, location: str
) -> None:
    value = contract.get(key)
    if isinstance(value, date):
        return
    if not isinstance(value, str) or not DATE_PATTERN.fullmatch(value):
        raise ValueError(f"{location}: {key!r} must be YYYY-MM-DD")


def is_template_placeholder(value: object) -> bool:
    return isinstance(value, str) and (
        value.startswith("Replace with")
        or value.startswith("Template only")
    )


def validate_task_contract_file(
    path: Path, errors: list[str], is_template: bool
) -> TaskContractSummary | None:
    location = path.name
    try:
        text = path.read_text(encoding="utf-8")
        contract = parse_markdown_frontmatter(path)
        for field in TASK_REQUIRED_FIELDS:
            if field not in contract:
                raise ValueError(
                    f"{location}: missing required field {field!r}"
                )

        for field in (
            "parent_goal",
            "assigned_to",
            "objective",
            "reviewer",
            "integration_owner",
        ):
            non_empty_string(contract, field, location)

        for field in TASK_LIST_FIELDS:
            require_non_empty_list(contract, field, location)

        validate_task_skill_routing(contract, text, location)

        scope = contract["scope"]
        if not isinstance(scope, dict):
            raise ValueError(f"{location}: scope must be a mapping")
        for field in ("allowed", "forbidden"):
            require_non_empty_list(scope, field, f"{location} scope")

        authority = contract["authority"]
        if not isinstance(authority, dict):
            raise ValueError(f"{location}: authority must be a mapping")
        for field in AUTHORITY_FIELDS:
            if field not in authority:
                raise ValueError(
                    f"{location}: authority missing explicit field {field!r}"
                )
            if not isinstance(authority[field], bool):
                raise ValueError(
                    f"{location}: authority {field!r} must be boolean"
                )

        task_id = non_empty_string(contract, "task_id", location)
        if not TASK_ID_PATTERN.fullmatch(task_id):
            raise ValueError(f"{location}: invalid task_id {task_id!r}")
        if is_template:
            if task_id != "TASK-000":
                raise ValueError(
                    f"{location}: template task_id must be 'TASK-000'"
                )
        elif path.name != f"{task_id}.md":
            raise ValueError(
                f"{location}: filename must match task_id {task_id!r}"
            )

        status = non_empty_string(contract, "status", location)
        if status not in TASK_STATUSES:
            raise ValueError(f"{location}: invalid task status {status!r}")

        previous = non_empty_string(
            contract, "previous_status", location
        )
        if previous not in TASK_TRANSITIONS or status not in TASK_TRANSITIONS[previous]:
            raise ValueError(
                f"{location}: invalid task transition {previous!r} -> {status!r}"
            )

        changed_by = non_empty_string(
            contract, "status_changed_by", location
        )
        if changed_by not in LOGICAL_ROLES:
            raise ValueError(
                f"{location}: invalid status owner {changed_by!r}"
            )
        if changed_by == "worker" and status in {"approved", "integrated"}:
            raise ValueError(
                f"{location}: worker cannot set task status {status!r}"
            )
        if changed_by not in TASK_STATUS_OWNERS[status]:
            raise ValueError(
                f"{location}: role {changed_by!r} cannot set status {status!r}"
            )

        assigned_role = non_empty_string(
            contract, "assigned_role", location
        )
        if assigned_role not in LOGICAL_ROLES:
            raise ValueError(
                f"{location}: invalid assigned_role {assigned_role!r}"
            )
        if is_template and (
            status != "proposed"
            or previous != "none"
            or changed_by != "supervisor"
            or assigned_role != "worker"
        ):
            raise ValueError(
                f"{location}: template must start as a proposed Worker task"
            )


        revision_count = contract["revision_count"]
        if (
            isinstance(revision_count, bool)
            or not isinstance(revision_count, int)
            or revision_count < 0
        ):
            raise ValueError(
                f"{location}: revision_count must be a non-negative integer"
            )
        revision_budget = contract["revision_budget"]
        if is_template:
            if revision_budget != "BOUNDED-LIMIT":
                raise ValueError(
                    f"{location}: template revision_budget must be 'BOUNDED-LIMIT'"
                )
        elif (
            isinstance(revision_budget, bool)
            or not isinstance(revision_budget, int)
            or revision_budget <= 0
        ):
            raise ValueError(
                f"{location}: revision_budget must be a positive "
                "task-specific integer"
            )
        if not is_template:
            if revision_count > revision_budget:
                raise ValueError(
                    f"{location}: revision_count cannot exceed revision_budget"
                )
            if (
                previous == "revision-requested"
                and status == "in-progress"
                and revision_count == 0
            ):
                raise ValueError(
                    f"{location}: return from revision-requested must "
                    "increment revision_count"
                )
        validate_task_date(contract, "created", location)
        validate_task_date(contract, "updated", location)

        if not is_template:
            for field in ("parent_goal", "objective"):
                if is_template_placeholder(contract[field]):
                    raise ValueError(
                        f"{location}: real task retains placeholder field {field!r}"
                    )
            for field in TASK_LIST_FIELDS:
                if any(is_template_placeholder(item) for item in contract[field]):
                    raise ValueError(
                        f"{location}: real task retains placeholder field {field!r}"
                    )
            for field in ("allowed", "forbidden"):
                if any(is_template_placeholder(item) for item in scope[field]):
                    raise ValueError(
                        f"{location}: real task retains placeholder scope {field!r}"
                    )

            assigned_to = non_empty_string(contract, "assigned_to", location)
            reviewer = non_empty_string(contract, "reviewer", location)
            integration_owner = non_empty_string(
                contract, "integration_owner", location
            )
            if status != "proposed" and assigned_to.casefold() == "none":
                raise ValueError(f"{location}: active task requires assigned_to")
            if reviewer.casefold() == "none":
                raise ValueError(f"{location}: real task requires a Reviewer")
            if integration_owner.casefold() == "none":
                raise ValueError(
                    f"{location}: real task requires an integration owner"
                )
            if (
                assigned_to.casefold() != "none"
                and assigned_to.casefold() == reviewer.casefold()
            ):
                raise ValueError(
                    f"{location}: Reviewer must be independent from assigned_to"
                )
            for field in ("created", "updated"):
                if contract[field] == "YYYY-MM-DD":
                    raise ValueError(
                        f"{location}: real task requires an actual {field} date"
                    )
        return TaskContractSummary(
            task_id=task_id,
            status=status,
            previous_status=previous,
            status_changed_by=changed_by,
            assigned_to=contract["assigned_to"],
            reviewer=contract["reviewer"],
            revision_count=revision_count,
        )
    except (ConstructorError, ValueError, yaml.YAMLError) as error:
        errors.append(str(error))
        return None


def validate_task_contracts(
    root: Path, errors: list[str]
) -> dict[str, TaskContractSummary]:
    directory = root / ".looppilot" / "tasks"
    template = directory / "TASK-TEMPLATE.md"
    paths = [
        template,
        *(
            path
            for path in sorted(directory.glob("TASK-*.md"))
            if path != template
        ),
    ]
    task_contracts: dict[str, TaskContractSummary] = {}
    for path in paths:
        summary = validate_task_contract_file(
            path, errors, is_template=path == template
        )
        if summary is None or path == template:
            continue
        if summary.task_id in task_contracts:
            errors.append(
                f"{path.name}: duplicate task_id {summary.task_id!r}"
            )
        task_contracts[summary.task_id] = summary
    return task_contracts


def validate_delegation_protocol(root: Path, errors: list[str]) -> None:
    path = root / ".looppilot" / "tasks" / "README.md"
    text = path.read_text(encoding="utf-8")
    required_fragments = (
        "Simple tasks MUST NOT be split across multiple Agents",
        "`approved` means the subtask passed independent review.",
        "`integrated` means reviewed",
        "Delegation transfers responsibility for scoped work, not authority",
        "last-writer-wins",
        "one accountable Supervisor or Integrator MUST",
    )
    for fragment in required_fragments:
        if fragment not in text:
            errors.append(
                f".looppilot/tasks/README.md: missing required protocol "
                f"semantics {fragment!r}"
            )


def meaningful_review_section(lines: list[str]) -> bool:
    return bool(lines) and lines != ["- None."] and not any(
        "Not yet checked" in line for line in lines
    )


def checked_review_item(lines: list[str], label: str) -> bool:
    prefix = f"- {label}:"
    for line in lines:
        if not line.startswith(prefix):
            continue
        value = line.removeprefix(prefix).strip()
        return bool(value) and value != "None." and "Not yet checked" not in value
    return False


def review_decision_matches_task(
    decision: str, task: TaskContractSummary
) -> bool:
    if task.status in {"approved", "revision-requested", "rejected"}:
        return decision == task.status
    if task.status == "blocked" and task.status_changed_by == "reviewer":
        return decision == "blocked"
    if task.status == "integrated":
        return decision == "approved" and task.previous_status == "approved"
    if task.previous_status in REVIEW_DECISIONS:
        return (
            decision == task.previous_status
            and task.status in TASK_TRANSITIONS[task.previous_status]
        )
    if (
        decision == "revision-requested"
        and task.revision_count > 0
        and task.status
        in {
            "in-progress",
            "submitted",
            "under-review",
            "blocked",
            "cancelled",
        }
    ):
        return True
    if decision == "rejected" and task.status in {
        "proposed",
        "assigned",
        "in-progress",
        "submitted",
        "under-review",
        "blocked",
        "cancelled",
    }:
        return True
    return False


def validate_review_file(
    path: Path,
    errors: list[str],
    is_template: bool,
    task_contracts: dict[str, TaskContractSummary],
) -> str | None:
    location = path.name
    try:
        review = parse_markdown_frontmatter(path)
        task_id = non_empty_string(review, "task_id", location)
        if not TASK_ID_PATTERN.fullmatch(task_id):
            raise ValueError(f"{location}: invalid task_id {task_id!r}")

        reviewer = non_empty_string(review, "reviewer", location)
        validate_task_date(review, "reviewed", location)
        decision = non_empty_string(review, "decision", location)
        if is_template:
            if decision != "DECISION":
                if decision not in REVIEW_DECISIONS:
                    raise ValueError(
                        f"{location}: invalid reviewer decision {decision!r}"
                    )
                raise ValueError(
                    f"{location}: template decision must be 'DECISION'"
                )
            if task_id != "TASK-000":
                raise ValueError(
                    f"{location}: template must use TASK-000"
                )
        else:
            if decision not in REVIEW_DECISIONS:
                raise ValueError(
                    f"{location}: invalid reviewer decision {decision!r}"
                )
            if task_id not in task_contracts:
                raise ValueError(
                    f"{location}: review references unknown task_id {task_id!r}"
                )
            task = task_contracts[task_id]
            if path.name != f"REVIEW-{task_id}.md":
                raise ValueError(
                    f"{location}: filename must match reviewed task_id {task_id!r}"
                )
            if reviewer.casefold() == "none":
                raise ValueError(f"{location}: real review requires a Reviewer")
            if reviewer.casefold() != task.reviewer.casefold():
                raise ValueError(
                    f"{location}: reviewer must match the Task Contract"
                )
            if reviewer.casefold() == task.assigned_to.casefold():
                raise ValueError(
                    f"{location}: Reviewer must be independent from assigned_to"
                )
            if review["reviewed"] == "YYYY-MM-DD":
                raise ValueError(
                    f"{location}: real review requires an actual reviewed date"
                )
            if not review_decision_matches_task(decision, task):
                raise ValueError(
                    f"{location}: decision {decision!r} does not match "
                    f"task lifecycle at status {task.status!r}"
                )

        text = path.read_text(encoding="utf-8")
        validate_review_protocol(review, text, is_template, location)

        lines = set(text.splitlines())
        for heading in REVIEW_REQUIRED_HEADINGS:
            if heading not in lines:
                raise ValueError(f"{location}: missing {heading!r}")

        if not is_template and "## Standards Review" not in text:
            criteria = markdown_section_lines(text, "## Criteria Checked")
            findings = markdown_section_lines(text, "## Findings")
            corrections = markdown_section_lines(text, "## Required Corrections")
            gaps = markdown_section_lines(
                text, "## Remaining Verification Gaps"
            )
            if decision == "approved":
                has_required_checks = (
                    checked_review_item(criteria, "Success criteria")
                    and checked_review_item(criteria, "Required evidence")
                )
                if (
                    not meaningful_review_section(criteria)
                    or not has_required_checks
                ):
                    raise ValueError(
                        f"{location}: approved review must cite checked "
                        "success criteria and evidence"
                    )
            if (
                decision == "revision-requested"
                and not meaningful_review_section(corrections)
            ):
                raise ValueError(
                    f"{location}: revision-requested review requires "
                    "specific corrections"
                )
            if decision == "blocked" and not meaningful_review_section(gaps):
                raise ValueError(
                    f"{location}: blocked review must name the missing condition"
                )
            if decision == "rejected" and not meaningful_review_section(findings):
                raise ValueError(
                    f"{location}: rejected review must explain the rejection"
                )
        return None if is_template else task_id
    except (ConstructorError, ValueError, yaml.YAMLError) as error:
        errors.append(str(error))
        return None


def validate_review_results(
    root: Path,
    task_contracts: dict[str, TaskContractSummary],
    errors: list[str],
) -> None:
    directory = root / ".looppilot" / "tasks"
    template = directory / "REVIEW-TEMPLATE.md"
    paths = [
        template,
        *(
            path
            for path in sorted(directory.glob("REVIEW-*.md"))
            if path != template
        ),
    ]
    reviewed_task_ids: set[str] = set()
    for path in paths:
        task_id = validate_review_file(
            path,
            errors,
            is_template=path == template,
            task_contracts=task_contracts,
        )
        if task_id is not None:
            reviewed_task_ids.add(task_id)

    for task in task_contracts.values():
        requires_review = task.status in {
            "approved",
            "integrated",
            "revision-requested",
            "rejected",
        } or (
            task.status == "blocked"
            and task.status_changed_by == "reviewer"
        )
        requires_review = requires_review or (
            task.previous_status in REVIEW_DECISIONS
        )
        requires_review = requires_review or (
            task.revision_count > 0
            and task.status
            in {
                "in-progress",
                "submitted",
                "under-review",
                "blocked",
                "cancelled",
            }
        )
        if requires_review and task.task_id not in reviewed_task_ids:
            errors.append(
                f"{task.task_id}.md: status {task.status!r} requires "
                "a Review Result"
            )


def validate_status(
    root: Path, relative: Path, allowed: set[str], errors: list[str]
) -> str | None:
    text = (root / relative).read_text(encoding="utf-8")
    match = STATUS_PATTERN.search(text)
    if not match:
        errors.append(f"{relative.as_posix()}: missing Status field")
        return None
    status = match.group(1)
    if status not in allowed:
        errors.append(f"{relative.as_posix()}: invalid Status {status!r}")
    return status


def markdown_section_lines(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return []
    content: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if line.strip():
            content.append(line.strip())
    return content


def validate_shared_state(root: Path, errors: list[str]) -> None:
    delegation_path = Path(".looppilot/DELEGATION.md")
    delegation_status = validate_status(
        root, delegation_path, DELEGATION_STATUSES, errors
    )
    delegation_text = (root / delegation_path).read_text(encoding="utf-8")
    inactive_sections = {
        "## Parent Goal": ["No active delegated goal."],
        "## Active Assignments": ["- None."],
        "## Review Queue": ["- None."],
        "## Revision Queue": ["- None."],
        "## Blocked Tasks": ["- None."],
        "## Conflicts": ["- None."],
        "## Integration Status": ["- Not started."],
        "## Research Status": ["- None."],
        "## Skill Assignment Summary": ["- None."],
        "## Checklist Status": ["- Inactive; no parent Checklist is active."],
        "## Budget Status": ["- Context pressure unknown; no budget stop is active."],
        "## Next Coordination Action": ["- None."],
    }
    if delegation_status == "inactive":
        empty_fields = (
            "Updated: YYYY-MM-DD",
            "Supervisor: none",
            "Integrator: none",
        )
        if any(marker not in delegation_text for marker in empty_fields) or any(
            markdown_section_lines(delegation_text, heading) != expected
            for heading, expected in inactive_sections.items()
        ):
            errors.append(
                f"{delegation_path.as_posix()}: inactive template must remain empty"
            )
    elif delegation_status in DELEGATION_STATUSES and any(
        marker in delegation_text
        for marker in (
            "Updated: YYYY-MM-DD",
            "Supervisor: none",
            "No active delegated goal.",
        )
    ):
        errors.append(
            f"{delegation_path.as_posix()}: template placeholders cannot declare "
            f"Status {delegation_status!r}"
        )

    state_path = Path(".looppilot/STATE.md")
    state_status = validate_status(
        root, state_path, STATE_STATUSES, errors
    )
    state_text = (root / state_path).read_text(encoding="utf-8")
    if state_status in STATE_STATUSES - {"inactive"} and any(
        marker in state_text
        for marker in ("Updated: YYYY-MM-DD", "Updated by: none", "No active shared task.")
    ):
        errors.append(
            f"{state_path.as_posix()}: template placeholders cannot declare "
            f"Status {state_status!r}"
        )

    handoff_path = Path(".looppilot/HANDOFF.md")
    handoff_status = validate_status(
        root, handoff_path, HANDOFF_STATUSES, errors
    )
    handoff_text = (root / handoff_path).read_text(encoding="utf-8")
    if handoff_status in HANDOFF_STATUSES - {"none"} and any(
        marker in handoff_text
        for marker in ("Updated: YYYY-MM-DD", "From: none", "No active handoff.")
    ):
        errors.append(
            f"{handoff_path.as_posix()}: template placeholders cannot declare "
            f"Status {handoff_status!r}"
        )

    decisions_path = Path(".looppilot/DECISIONS.md")
    for relative in (
        delegation_path, state_path, handoff_path, decisions_path
    ):
        text = (root / relative).read_text(encoding="utf-8")
        if not UPDATED_PATTERN.search(text):
            errors.append(
                f"{relative.as_posix()}: missing or invalid Updated field"
            )

    updater_patterns = {
        state_path: re.compile(r"^Updated by:[ \t]*\S+", re.MULTILINE),
        handoff_path: re.compile(r"^From:[ \t]*\S+", re.MULTILINE),
        decisions_path: re.compile(r"^Updated by:[ \t]*\S+", re.MULTILINE),
    }
    for field in ("Supervisor", "Integrator"):
        if not re.search(rf"^{field}:[ \t]*\S+", delegation_text, re.MULTILINE):
            errors.append(
                f"{delegation_path.as_posix()}: missing {field} identifier"
            )
    for relative, pattern in updater_patterns.items():
        text = (root / relative).read_text(encoding="utf-8")
        if not pattern.search(text):
            errors.append(f"{relative.as_posix()}: missing updater identifier")

    for relative_text, headings in SHARED_STATE_HEADINGS.items():
        relative = Path(relative_text)
        text = (root / relative).read_text(encoding="utf-8")
        if CREDENTIAL_ASSIGNMENT_PATTERN.search(text):
            errors.append(
                f"{relative.as_posix()}: possible credential assignment in shared state"
            )
        lines = set(text.splitlines())
        for heading in headings:
            if heading not in lines:
                errors.append(
                    f"{relative.as_posix()}: missing required heading {heading!r}"
                )


def markdown_files(root: Path) -> list[Path]:
    ignored = {".git", ".venv", "node_modules", "__pycache__"}
    return sorted(
        path
        for path in root.rglob("*.md")
        if not any(part in ignored for part in path.relative_to(root).parts)
    )


def validate_markdown_file(root: Path, path: Path, errors: list[str]) -> None:
    relative = path.relative_to(root)
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    if not raw.endswith(b"\n"):
        errors.append(f"{relative}: file must end with a newline")
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.endswith((" ", "\t")):
            errors.append(f"{relative}:{line_number}: trailing whitespace")
    fence_count = sum(1 for line in text.splitlines() if line.lstrip().startswith("```"))
    if fence_count % 2:
        errors.append(f"{relative}: unbalanced Markdown code fences")
    for match in LINK_PATTERN.finditer(text):
        raw_target = match.group(1).strip()
        if raw_target.startswith("<") and raw_target.endswith(">"):
            raw_target = raw_target[1:-1]
        target = raw_target.split(maxsplit=1)[0]
        parsed = urlsplit(target)
        if parsed.scheme or target.startswith(("#", "//")):
            continue
        link_path = unquote(parsed.path)
        if not link_path:
            continue
        resolved = (path.parent / link_path).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{relative}: relative link escapes repository: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{relative}: broken relative link: {target}")


def collect_mermaid_blocks(root: Path, files: list[Path]) -> list[MermaidBlock]:
    blocks: list[MermaidBlock] = []
    for path in files:
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        for number, match in enumerate(MERMAID_PATTERN.finditer(text), start=1):
            blocks.append(MermaidBlock(relative, number, match.group(1).rstrip() + "\n"))
    return blocks


def extract_mermaid(blocks: list[MermaidBlock], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for block in blocks:
        (output / block.filename).write_text(block.content, encoding="utf-8", newline="\n")


def validate_repository(root: Path, extract_directory: Path | None = None) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")
    if errors:
        return errors

    validate_shared_state(root, errors)
    validate_repository_extensions(root, errors)
    validate_loop_engineering(root, errors)
    validate_full_loop(root, errors, TASK_STATUSES)
    validate_full_loop_execution(root, errors)
    validate_yaml_files(root, errors)
    validate_skill_frontmatter(root, errors)
    validate_openai_yaml(root, errors)
    task_contracts = validate_task_contracts(root, errors)
    validate_delegation_protocol(root, errors)
    validate_review_results(root, task_contracts, errors)

    files = markdown_files(root)
    for path in files:
        validate_markdown_file(root, path, errors)

    skill_words = len((root / "SKILL.md").read_text(encoding="utf-8").split())
    if skill_words not in SKILL_WORD_RANGE:
        errors.append(
            f"SKILL.md: expected 1500-2500 words, observed {skill_words}"
        )

    blocks = collect_mermaid_blocks(root, files)
    sources = {block.source.as_posix() for block in blocks}
    for required_source in (
        "README.md",
        "docs/lifecycle.md",
        "docs/multi-agent-coordination.md",
        "docs/loop-engineering-model.md",
        "docs/protocol-modes-and-state-sources.md",
        "docs/project-closure.md",
        "docs/full-loop-contracts-and-ledgers.md",
        "docs/full-loop-delivery-review-and-closure.md",
    ):
        if required_source not in sources:
            errors.append(f"{required_source}: expected at least one Mermaid block")
    if extract_directory is not None and not errors:
        extract_mermaid(blocks, extract_directory.resolve())
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (defaults to the parent of scripts/)",
    )
    parser.add_argument(
        "--extract-mermaid",
        type=Path,
        help="write extracted Mermaid sources to this directory after validation",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        errors = validate_repository(args.root, args.extract_mermaid)
    except (OSError, UnicodeError) as error:
        errors = [str(error)]
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Static validation passed")
    if args.extract_mermaid is not None:
        print(f"Mermaid sources written to {args.extract_mermaid.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
