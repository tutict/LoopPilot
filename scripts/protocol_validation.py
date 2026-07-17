"""Static validation for research, Skill routing, reviews, and Checklists."""

from __future__ import annotations

import re
from pathlib import Path


TASK_ID_PATTERN = re.compile(r"^TASK-\d{3,}$")
ITEM_ID_PATTERN = re.compile(r"^ITEM-\d{3,}$")
CHECKLIST_STATUSES = {
    "inactive",
    "active",
    "paused",
    "budget-stopped",
    "partially-completed",
    "blocked",
    "completed",
    "cancelled",
}
ITEM_STATUSES = {
    "proposed",
    "ready",
    "assigned",
    "in-progress",
    "submitted",
    "under-review",
    "revision-requested",
    "approved",
    "integrated",
    "blocked",
    "deferred",
    "cancelled",
}
CONTEXT_PRESSURES = {"unknown", "normal", "elevated", "high", "critical"}
RESEARCH_STATUSES = {
    "inactive",
    "proposed",
    "in-progress",
    "ready",
    "conflicted",
    "blocked",
    "superseded",
}
AXIS_DECISIONS = {"pass", "revision-requested", "rejected", "blocked"}


def _field(text: str, name: str) -> str | None:
    match = re.search(rf"^{re.escape(name)}:[ \t]*(.*)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _bullet_field(text: str, name: str) -> str | None:
    match = re.search(rf"^- {re.escape(name)}:[ \t]*(.*)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _section(text: str, heading: str) -> list[str]:
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


def _axis_block(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return []
    block: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        block.append(line)
    return block


def _axis_subsection(text: str, axis: str, subsection: str) -> list[str]:
    block = _axis_block(text, axis)
    heading = f"### {subsection}"
    try:
        start = block.index(heading) + 1
    except ValueError:
        return []
    content: list[str] = []
    for line in block[start:]:
        if line.startswith("### "):
            break
        if line.strip():
            content.append(line.strip())
    return content


def _axis_decision(text: str, axis: str) -> str | None:
    for line in _axis_block(text, axis):
        if line.startswith("Decision:"):
            return line.removeprefix("Decision:").strip()
    return None


def _meaningful(lines: list[str]) -> bool:
    return any(
        line != "- None." and "Not yet checked" not in line
        for line in lines
    )


def _checked(lines: list[str], label: str) -> bool:
    prefix = f"- {label}:"
    for line in lines:
        if line.startswith(prefix):
            value = line.removeprefix(prefix).strip()
            return bool(value) and value != "None." and "Not yet checked" not in value
    return False


def _template_value(value: str | None) -> bool:
    return value is None or value.casefold() in {"none", "none.", "yyyy-mm-dd"}


def _checklist_items(text: str) -> list[tuple[str, str, dict[str, str]]]:
    pattern = re.compile(
        r"^- \[([ xX])\] `([^`]+)`[^\r\n]*(?:\r?\n((?:  - [^\r\n]*(?:\r?\n|$))*))?",
        re.MULTILINE,
    )
    items: list[tuple[str, str, dict[str, str]]] = []
    for match in pattern.finditer(text):
        metadata: dict[str, str] = {}
        for line in (match.group(3) or "").splitlines():
            field_match = re.match(r"^  - ([^:]+):[ \t]*(.*)$", line)
            if field_match:
                metadata[field_match.group(1)] = field_match.group(2).strip()
        items.append((match.group(1), match.group(2), metadata))
    return items


def validate_checklist(root: Path, errors: list[str]) -> None:
    location = ".looppilot/CHECKLIST.md"
    text = (root / location).read_text(encoding="utf-8")
    status = _field(text, "Status")
    if status not in CHECKLIST_STATUSES:
        errors.append(f"{location}: invalid Status {status!r}")
    pressure = _field(text, "Context pressure")
    if pressure not in CONTEXT_PRESSURES:
        errors.append(f"{location}: invalid Context pressure {pressure!r}")

    headings = (
        "## Parent Goal",
        "## Success Criteria",
        "## Work Items",
        "## Blocked Items",
        "## Deferred Items",
        "## Last Verified Evidence",
        "## Execution Budget",
        "## Resume Point",
        "## Stop Reason",
    )
    lines = set(text.splitlines())
    for heading in headings:
        if heading not in lines:
            errors.append(f"{location}: missing required heading {heading!r}")

    items = _checklist_items(text)
    seen: set[str] = set()
    for mark, item_id, metadata in items:
        if not ITEM_ID_PATTERN.fullmatch(item_id):
            errors.append(f"{location}: invalid Checklist item ID {item_id!r}")
        if item_id in seen:
            errors.append(f"{location}: duplicate Checklist item ID {item_id!r}")
        seen.add(item_id)
        item_status = metadata.get("Status")
        if item_status not in ITEM_STATUSES:
            errors.append(f"{location}: invalid item Status {item_status!r}")
            continue
        checked = mark.casefold() == "x"
        if checked and item_status == "approved":
            errors.append(f"{location}: approved item must remain unchecked")
        if item_status == "integrated" and not checked:
            errors.append(f"{location}: integrated item must be checked")
        if checked and item_status == "cancelled":
            errors.append(f"{location}: cancelled item must remain unchecked")
        if checked and item_status not in {"integrated", "cancelled", "approved"}:
            errors.append(f"{location}: checked item must have Status: integrated")
        evidence = metadata.get("Evidence", "")
        if checked and (
            not evidence or evidence.casefold() in {"pending", "none", "none."}
        ):
            errors.append(f"{location}: checked item requires observed evidence")
        task_id = metadata.get("Task", "none").strip("`")
        if task_id.casefold() != "none" and not TASK_ID_PATTERN.fullmatch(task_id):
            errors.append(f"{location}: Task must use a TASK-NNN identifier")

    if status == "inactive":
        inactive_markers = (
            "Goal ID: none",
            "Updated: YYYY-MM-DD",
            "Updated by: none",
            "Supervisor: none",
            "Integrator: none",
            "No active parent Goal.",
        )
        if any(marker not in text for marker in inactive_markers) or items or "- [x]" in text:
            errors.append(f"{location}: inactive template must remain empty")
    if status == "budget-stopped":
        if _field(text, "Resume required") != "true":
            errors.append(f"{location}: budget-stopped requires Resume required: true")
        if not _meaningful(_section(text, "## Resume Point")):
            errors.append(f"{location}: budget-stopped requires a Resume Point")
        if not _meaningful(_section(text, "## Stop Reason")):
            errors.append(f"{location}: budget-stopped requires a Stop Reason")
    if status == "completed" and any(
        line.startswith("- [ ]") for line in _section(text, "## Success Criteria")
    ):
        errors.append(f"{location}: completed checklist has an unchecked success criterion")


def validate_research(root: Path, errors: list[str]) -> None:
    location = ".looppilot/RESEARCH-TEMPLATE.md"
    text = (root / location).read_text(encoding="utf-8")
    status = _field(text, "Status")
    if status not in RESEARCH_STATUSES:
        errors.append(f"{location}: invalid Status {status!r}")
    headings = (
        "## Questions",
        "## Source Requirements",
        "## Sources",
        "## Findings",
        "## Source Conflicts",
        "## Implementation Implications",
        "## Worker Guidance",
        "## Unresolved Questions",
        "## Verification Boundary",
    )
    lines = set(text.splitlines())
    for heading in headings:
        if heading not in lines:
            errors.append(f"{location}: missing required heading {heading!r}")

    if status in {"ready", "conflicted"}:
        source_fields = (
            "Title",
            "Publisher",
            "URL or reference",
            "Source type",
            "Version or date",
            "Accessed",
            "Authority",
            "Relevance",
        )
        source_values = {field: _bullet_field(text, field) for field in source_fields}
        if _template_value(source_values["Title"]):
            errors.append(f"{location}: ready Research Brief requires a Source")
        for field in source_fields[1:]:
            if _template_value(source_values[field]):
                errors.append(f"{location}: Source requires {field}")
        if _template_value(_bullet_field(text, "Finding")):
            errors.append(f"{location}: ready Research Brief requires a Finding")
        for field in ("Supported by", "Confidence", "Applies to", "Limitations"):
            if _template_value(_bullet_field(text, field)):
                errors.append(f"{location}: Finding requires {field}")
    if status == "conflicted" and not _meaningful(_section(text, "## Source Conflicts")):
        errors.append(f"{location}: conflicted Research Brief requires Source Conflicts")
    if re.search(
        r"\bimplementation (?:is|was|has been) verified in the current "
        r"(?:repository|runtime|environment)\b",
        text,
        re.IGNORECASE,
    ):
        errors.append(
            f"{location}: Research Brief cannot claim local implementation verification"
        )


def _require_list(mapping: dict[object, object], key: str, location: str) -> list[object]:
    value = mapping.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{location}: {key!r} must be a list")
    return value


def validate_task_skill_routing(
    contract: dict[object, object], text: str, location: str
) -> None:
    research_inputs = _require_list(contract, "research_inputs", location)
    for entry in research_inputs:
        if not isinstance(entry, dict):
            raise ValueError(f"{location}: research_inputs entries must be mappings")
        for field in ("research_id", "purpose", "required_findings"):
            if field not in entry:
                raise ValueError(f"{location}: research input missing {field!r}")

    assignment = contract.get("skill_assignment")
    if not isinstance(assignment, dict):
        raise ValueError(f"{location}: skill_assignment must be a mapping")
    lists = {
        field: _require_list(assignment, field, f"{location} skill_assignment")
        for field in ("required", "optional", "forbidden", "fallback")
    }
    required: dict[str, bool] = {}
    for entry in lists["required"]:
        if not isinstance(entry, dict):
            raise ValueError(f"{location}: required Skill entries must be mappings")
        for field in (
            "skill",
            "purpose",
            "verified_available",
            "source",
            "version",
            "expected_output",
        ):
            if field not in entry:
                if field == "verified_available":
                    raise ValueError(f"{location}: required Skill missing 'verified_available'")
                raise ValueError(f"{location}: required Skill missing {field!r}")
        skill = entry["skill"]
        available = entry["verified_available"]
        if not isinstance(skill, str) or not skill.strip():
            raise ValueError(f"{location}: required Skill name must be non-empty")
        if not isinstance(available, bool):
            raise ValueError(f"{location}: verified_available must be boolean")
        required[skill] = available

    forbidden: set[str] = set()
    for entry in lists["forbidden"]:
        if not isinstance(entry, dict):
            raise ValueError(f"{location}: forbidden Skill entries must be mappings")
        skill = entry.get("skill")
        if not isinstance(skill, str) or not skill.strip() or "reason" not in entry:
            raise ValueError(f"{location}: forbidden Skill requires skill and reason")
        forbidden.add(skill)

    selection = contract.get("skill_selection")
    if not isinstance(selection, dict):
        raise ValueError(f"{location}: skill_selection must be a mapping")
    for field in ("considered", "selected", "verified_available"):
        _require_list(selection, field, f"{location} skill_selection")
    selected = selection["selected"]
    verified = selection["verified_available"]
    if not isinstance(selection.get("selected_by"), str):
        raise ValueError(f"{location}: skill_selection selected_by must be a string")
    if not all(isinstance(skill, str) and skill.strip() for skill in selected):
        raise ValueError(f"{location}: selected Skills must be non-empty strings")
    if not all(isinstance(skill, str) and skill.strip() for skill in verified):
        raise ValueError(f"{location}: verified Skills must be non-empty strings")

    unavailable = {skill for skill, available in required.items() if not available}
    for entry in selection["considered"]:
        if not isinstance(entry, dict):
            raise ValueError(f"{location}: considered Skill entries must be mappings")
        skill = entry.get("skill")
        status = entry.get("status")
        if not isinstance(skill, str) or not skill.strip():
            raise ValueError(f"{location}: considered Skill name must be non-empty")
        if status not in {"selected", "rejected", "unavailable"}:
            raise ValueError(f"{location}: invalid Skill selection status {status!r}")
        if status == "unavailable":
            unavailable.add(skill)
        if "reason" not in entry:
            raise ValueError(f"{location}: considered Skill requires a reason")

    selected_set = set(selected)
    if selected_set & unavailable:
        raise ValueError(f"{location}: unavailable Skill cannot be selected")
    if selected_set & forbidden:
        raise ValueError(f"{location}: forbidden Skill cannot be selected")
    if not selected_set <= set(verified):
        raise ValueError(f"{location}: selected Skill must be verified available")
    if "Skill assignment transfers no authority." not in text:
        raise ValueError(f"{location}: missing Skill assignment authority note")
    checklist_item = contract.get("checklist_item")
    if not isinstance(checklist_item, str) or (
        checklist_item != "none" and not ITEM_ID_PATTERN.fullmatch(checklist_item)
    ):
        raise ValueError(f"{location}: checklist_item must be none or ITEM-NNN")


def validate_review_protocol(
    review: dict[object, object], text: str, is_template: bool, location: str
) -> None:
    for field in ("standards_decision", "spec_decision", "required_evidence"):
        value = review.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{location}: missing required field {field!r}")
    standards = review["standards_decision"]
    spec = review["spec_decision"]
    evidence = review["required_evidence"]
    overall = review["decision"]
    if is_template:
        if standards != "AXIS-DECISION" or spec != "AXIS-DECISION":
            raise ValueError(f"{location}: template axis decisions must be AXIS-DECISION")
        if evidence != "EVIDENCE-STATUS":
            raise ValueError(f"{location}: template evidence must be EVIDENCE-STATUS")
    else:
        for axis, value in (("Standards", standards), ("Spec", spec)):
            if value not in AXIS_DECISIONS:
                raise ValueError(f"{location}: invalid {axis} Review decision {value!r}")
        if overall == "approved" and (standards != "pass" or spec != "pass"):
            raise ValueError(f"{location}: approved requires both review axes to pass")
        if overall == "approved" and evidence != "observed":
            raise ValueError(f"{location}: approved review requires observed evidence")
        axes = {standards, spec}
        if "blocked" in axes and overall != "blocked":
            raise ValueError(f"{location}: blocked review axis requires blocked overall")
        if "blocked" not in axes and "rejected" in axes and overall != "rejected":
            raise ValueError(f"{location}: rejected review axis requires rejected overall")
        if not axes & {"blocked", "rejected"} and "revision-requested" in axes:
            if overall != "revision-requested":
                raise ValueError(
                    f"{location}: revision-requested axis requires revision-requested overall"
                )

    headings = (
        "## Standards Review",
        "## Spec Review",
        "## Verification Gaps",
        "## Overall Decision Rationale",
        "## Authority Note",
    )
    lines = set(text.splitlines())
    for heading in headings:
        if heading not in lines:
            raise ValueError(f"{location}: missing {heading!r}")
    for axis, expected in (("## Standards Review", standards), ("## Spec Review", spec)):
        for subsection in ("Criteria Checked", "Findings", "Required Corrections"):
            if f"### {subsection}" not in _axis_block(text, axis):
                raise ValueError(f"{location}: {axis} missing '### {subsection}'")
        observed = _axis_decision(text, axis)
        if observed != expected:
            raise ValueError(f"{location}: {axis} Decision does not match frontmatter")

    normalized = " ".join(text.split())
    authority_note = (
        "This review grants no commit, push, release, deployment, deletion, Skill "
        "installation, or external-communication authority."
    )
    if authority_note not in normalized or re.search(
        r"\bauthoriz\w* Skill installation\b", normalized, re.IGNORECASE
    ):
        raise ValueError(f"{location}: review must not authorize Skill installation")
    if is_template:
        return

    standards_criteria = _axis_subsection(text, "## Standards Review", "Criteria Checked")
    spec_criteria = _axis_subsection(text, "## Spec Review", "Criteria Checked")
    corrections = (
        _axis_subsection(text, "## Standards Review", "Required Corrections")
        + _axis_subsection(text, "## Spec Review", "Required Corrections")
    )
    findings = (
        _axis_subsection(text, "## Standards Review", "Findings")
        + _axis_subsection(text, "## Spec Review", "Findings")
    )
    if overall == "approved" and (
        not _meaningful(standards_criteria)
        or not _meaningful(spec_criteria)
        or not _checked(spec_criteria, "Success criteria")
        or not _checked(spec_criteria, "Required evidence")
    ):
        raise ValueError(
            f"{location}: approved review must cite checked success criteria and evidence"
        )
    if overall == "revision-requested" and not _meaningful(corrections):
        raise ValueError(
            f"{location}: revision-requested review requires specific corrections"
        )
    if overall == "blocked" and not _meaningful(_section(text, "## Verification Gaps")):
        raise ValueError(f"{location}: blocked review must name the missing condition")
    if overall == "rejected" and not _meaningful(findings):
        raise ValueError(f"{location}: rejected review must explain the rejection")


def validate_repository_extensions(root: Path, errors: list[str]) -> None:
    validate_checklist(root, errors)
    validate_research(root, errors)
