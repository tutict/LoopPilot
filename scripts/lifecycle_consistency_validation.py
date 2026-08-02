"""Validate finite Full Loop lifecycle assertions without mutating state."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

LIFECYCLE_CONSISTENCY_FILES = (
    "scripts/lifecycle_consistency_validation.py",
    "tests/test_lifecycle_consistency.py",
    "docs/final-protocol-calibration.md",
    "docs/lifecycle-authority-and-derived-projections.md",
    "docs/v1-migration.md",
)
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
TASK_ID_FORM = re.compile(r"^TASK-\d{3,}(?:-R\d+)?$")
FINDING_ID_FORM = re.compile(r"^FINDING-\d{3,}$")
LOOP_ID_FORM = re.compile(r"^LOOP-\d{3,}$")
ASSERTION_PATTERNS = (
    re.compile(r"^Project\.status$"),
    re.compile(r"^Loop\[LOOP-\d{3,}\]\.status$"),
    re.compile(r"^Task\[TASK-\d{3,}(?:-R\d+)?\]\.(?:status|owner|revision)$"),
    re.compile(r"^Finding\[FINDING-\d{3,}\]\.(?:status|severity)$"),
    re.compile(r"^Git\.current_boundary$"),
    re.compile(r"^Integration\.decision$"),
    re.compile(r"^Review\.(?:Spec|Standards)$"),
    re.compile(r"^Closure\.decision$"),
    re.compile(r"^Checkpoint\.(?:current_boundary|next_action)$"),
)
ASSERTION_TOKEN_PATTERN = re.compile(
    "|".join(f"(?:{pattern.pattern[1:-1]})" for pattern in ASSERTION_PATTERNS)
)
DECLARED_SECTIONS = ("## Lifecycle Projections", "## Lifecycle Consistency")
AUTHORITY_FILES = {"PROJECT.md", "LOOP-MAP.md", "TASK-LEDGER.md", "FINDING-LEDGER.md", "CHECKPOINT.md"}
FORBIDDEN_LEDGER_FILES = {"LIFECYCLE-LEDGER.md", "ASSERTION-LEDGER.md", "STATE-DATABASE.md"}
AUTHORITY_DECLARATION_PATTERN = re.compile(
    r"^- (Project[^:]*|Loop[^:]*|Task[^:]*|Finding[^:]*|Recovery[^:]*|Lifecycle[^:]*) authority:[ \t]*(.*)$",
    re.MULTILINE | re.IGNORECASE,
)
DECLARED_AUTHORITY_MAP = (
    ("project", "PROJECT.md"),
    ("loop", "LOOP-MAP.md"),
    ("task", "TASK-LEDGER.md"),
    ("finding", "FINDING-LEDGER.md"),
    ("recovery", "CHECKPOINT.md"),
)


@dataclass(frozen=True)
class Fact:
    authority: str
    value: str


@dataclass(frozen=True)
class Projection:
    source: str
    assertion: str
    authority: str
    value: str
    boundary: str


def _plain(value: str) -> str:
    return value.strip().strip("`").strip()


def _same(left: str, right: str) -> bool:
    return " ".join(_plain(left).split()).casefold() == " ".join(_plain(right).split()).casefold()


def _field(text: str, name: str, *, bullet: bool = True) -> str | None:
    prefix = r"^-[ \t]*" if bullet else r"^"
    match = re.search(rf"{prefix}{re.escape(name)}:[ \t]*(.*)$", text, re.MULTILINE)
    return _plain(match.group(1)) if match else None


def _has_heading(text: str, heading: str) -> bool:
    """Match a real heading line, so prose that quotes the heading is not one."""
    return any(line.strip() == heading for line in text.splitlines())


def _section_lines(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    start = next(
        (index + 1 for index, line in enumerate(lines) if line.strip() == heading),
        None,
    )
    if start is None:
        return []
    result: list[str] = []
    level = len(heading) - len(heading.lstrip("#"))
    for line in lines[start:]:
        match = re.match(r"^(#+) ", line)
        if match and len(match.group(1)) <= level:
            break
        result.append(line)
    return result


def _section_field(text: str, heading: str, name: str) -> str | None:
    return _field("\n".join(_section_lines(text, heading)), name)


def _table(text: str, heading: str, required_headers: tuple[str, ...], location: str, errors: list[str]) -> list[dict[str, str]]:
    lines = [line.strip() for line in _section_lines(text, heading) if line.strip().startswith("|")]
    if len(lines) < 2:
        errors.append(f"{location}: {heading} requires a Markdown table")
        return []

    def cells(line: str) -> list[str]:
        return [_plain(cell) for cell in line.strip("|").split("|")]

    headers = cells(lines[0])
    missing = [header for header in required_headers if header not in headers]
    if missing:
        errors.append(f"{location}: {heading} missing columns {missing!r}")
        return []
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        values = cells(line)
        if len(values) != len(headers):
            errors.append(f"{location}: malformed row in {heading}")
            continue
        rows.append(dict(zip(headers, values)))
    return rows


def _git_head(root: Path) -> str | None:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False)
    value = result.stdout.strip()
    return value.lower() if result.returncode == 0 and SHA_PATTERN.fullmatch(value) else None


def _known_boundary(root: Path, head: str | None, value: str) -> bool:
    """A recorded boundary is the current HEAD or one of its ancestors.

    Recording a Closure is itself a commit, so a committed snapshot's boundary
    is necessarily behind live HEAD; ancestry keeps it valid without accepting
    fabricated or foreign SHAs.
    """
    if head is None:
        return True
    value = _plain(value)
    if not SHA_PATTERN.fullmatch(value):
        return False
    if _same(value, head):
        return True
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", value, "HEAD"],
        cwd=root, capture_output=True, text=True, check=False,
    )
    return result.returncode == 0


def _declared_authority_ok(fact: str, value: str) -> bool:
    """A declaration competes only when it names a non-canonical state file.

    Role or prose authority lines (for example a Supervisor decision right)
    claim no lifecycle state file and stay out of scope.
    """
    fact = fact.strip().casefold()
    named = set(re.findall(r"[A-Za-z0-9._-]+\.md", _plain(value)))
    if not named:
        return True
    for prefix, canonical in DECLARED_AUTHORITY_MAP:
        if fact.startswith(prefix):
            return named <= {canonical}
    return named <= AUTHORITY_FILES


def _read(path: Path, location: str, errors: list[str]) -> str | None:
    if not path.is_file():
        errors.append(f"{location}: missing authoritative file")
        return None
    return path.read_text(encoding="utf-8")


def _assertion_authority(assertion: str) -> str | None:
    if assertion == "Project.status": return "PROJECT.md"
    if assertion.startswith("Loop["): return "LOOP-MAP.md"
    if assertion.startswith("Task["): return "TASK-LEDGER.md"
    if assertion.startswith("Finding["): return "FINDING-LEDGER.md"
    if assertion == "Git.current_boundary": return "Git"
    if assertion == "Integration.decision": return "INTEGRATION-RECORD.md"
    if assertion.startswith("Review."): return "REVIEW-REPORT.md"
    if assertion == "Closure.decision": return "LOOP-CLOSURE.md"
    if assertion.startswith("Checkpoint."): return "CHECKPOINT.md"
    return None


def _valid_assertion(assertion: str) -> bool:
    return any(pattern.fullmatch(assertion) for pattern in ASSERTION_PATTERNS)


def _collect_authority(root: Path, loop_dir: Path, closure_text: str, errors: list[str], warnings: list[str]) -> dict[str, Fact]:
    facts: dict[str, Fact] = {}
    project_text = _read(root / ".looppilot" / "PROJECT.md", "PROJECT.md", errors)
    loop_map_text = _read(root / ".looppilot" / "LOOP-MAP.md", "LOOP-MAP.md", errors)
    task_text = _read(loop_dir / "TASK-LEDGER.md", "TASK-LEDGER.md", errors)
    finding_text = _read(loop_dir / "FINDING-LEDGER.md", "FINDING-LEDGER.md", errors)
    checkpoint_text = _read(root / ".looppilot" / "CHECKPOINT.md", "CHECKPOINT.md", errors)
    if project_text is not None:
        status = _field(project_text, "Status", bullet=False)
        if status is None: errors.append("PROJECT.md: missing Status")
        else: facts["Project.status"] = Fact("PROJECT.md", status)
    loop_id = _field(closure_text, "Loop ID") or loop_dir.name
    if loop_map_text is not None:
        rows = _table(loop_map_text, "## Loops", ("Loop ID", "Status"), "LOOP-MAP.md", errors)
        matches = [row for row in rows if _same(row["Loop ID"], loop_id)]
        if len(matches) != 1: errors.append(f"LOOP-MAP.md: expected one row for {loop_id!r}")
        elif not LOOP_ID_FORM.fullmatch(_plain(loop_id)):
            warnings.append(f"LOOP-MAP.md: non-canonical Loop ID {loop_id!r}; rename to LOOP-NNN before migrating to lifecycle assertions")
        else: facts[f"Loop[{loop_id}].status"] = Fact("LOOP-MAP.md", matches[0]["Status"])
    if task_text is not None:
        rows = _table(task_text, "## Task Summary", ("Task ID", "Status", "Worker"), "TASK-LEDGER.md", errors)
        if "| Revision |" not in task_text and "| Revision|" not in task_text:
            warnings.append("TASK-LEDGER.md: legacy ledger lacks Revision; add it before the next Closure")
        for row in rows:
            task_id = _plain(row["Task ID"])
            if task_id.casefold() == "none": continue
            if not TASK_ID_FORM.fullmatch(task_id):
                warnings.append(f"TASK-LEDGER.md: non-canonical Task ID {task_id!r}; rename to TASK-NNN before migrating to lifecycle assertions")
                continue
            facts[f"Task[{task_id}].status"] = Fact("TASK-LEDGER.md", row["Status"])
            facts[f"Task[{task_id}].owner"] = Fact("TASK-LEDGER.md", row["Worker"])
            if "Revision" in row: facts[f"Task[{task_id}].revision"] = Fact("TASK-LEDGER.md", row["Revision"])
    if finding_text is not None:
        rows = _table(finding_text, "## Finding Summary", ("Finding ID", "Severity", "Status"), "FINDING-LEDGER.md", errors)
        for row in rows:
            finding_id = _plain(row["Finding ID"])
            if finding_id.casefold() == "none": continue
            if not FINDING_ID_FORM.fullmatch(finding_id):
                warnings.append(f"FINDING-LEDGER.md: non-canonical Finding ID {finding_id!r}; rename to FINDING-NNN before migrating to lifecycle assertions")
                continue
            facts[f"Finding[{finding_id}].status"] = Fact("FINDING-LEDGER.md", row["Status"])
            facts[f"Finding[{finding_id}].severity"] = Fact("FINDING-LEDGER.md", row["Severity"])
    head = _git_head(root)
    if head is not None: facts["Git.current_boundary"] = Fact("Git", head)
    else: warnings.append("Git.current_boundary: Git HEAD unavailable; SHA equality not checked")
    integration_paths = sorted((loop_dir / "integration").glob("*.md"))
    integration_text = integration_paths[-1].read_text(encoding="utf-8") if integration_paths else None
    if integration_text is None: errors.append("INTEGRATION-RECORD.md: missing integration record")
    else:
        decision = _field(integration_text, "Barrier result") or _field(integration_text, "Status")
        if decision is None: errors.append("INTEGRATION-RECORD.md: missing integration decision")
        else: facts["Integration.decision"] = Fact("INTEGRATION-RECORD.md", decision)
    review_paths = sorted((loop_dir / "reviews").glob("*.md"))
    review_values: dict[str, list[str]] = {"Spec": [], "Standards": []}
    for review_path in review_paths:
        review_text = review_path.read_text(encoding="utf-8")
        status = _field(review_text, "Status")
        if status is not None and status.casefold() == "superseded":
            continue
        for axis in review_values:
            decision = _section_field(review_text, f"## {axis} Review Contribution", "Decision")
            if decision and decision.casefold() != "not-evaluated": review_values[axis].append(decision)
    for axis, values in review_values.items():
        if len({value.casefold() for value in values}) != 1: errors.append(f"REVIEW-REPORT.md: expected one current {axis} decision")
        else: facts[f"Review.{axis}"] = Fact("REVIEW-REPORT.md", values[0])
    closure_decision = _field(closure_text, "Decision")
    if closure_decision is None: errors.append("LOOP-CLOSURE.md: missing Closure decision")
    else: facts["Closure.decision"] = Fact("LOOP-CLOSURE.md", closure_decision)
    if checkpoint_text is not None:
        boundary = _field(checkpoint_text, "Verified HEAD")
        next_action = _field(checkpoint_text, "Resume action")
        if boundary is None: errors.append("CHECKPOINT.md: missing Verified HEAD")
        else: facts["Checkpoint.current_boundary"] = Fact("CHECKPOINT.md", boundary)
        if next_action is None: errors.append("CHECKPOINT.md: missing Resume action")
        else: facts["Checkpoint.next_action"] = Fact("CHECKPOINT.md", next_action)
    return facts


def _collect_projections(
    root: Path,
    loop_dir: Path,
    facts: dict[str, Fact],
    head: str | None,
    errors: list[str],
) -> dict[tuple[str, str], Projection]:
    projections: dict[tuple[str, str], Projection] = {}
    state_root = root / ".looppilot"
    for path in sorted(state_root.rglob("*.md")):
        if "-TEMPLATE" in path.name or path.name in AUTHORITY_FILES: continue
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(state_root)
        if "loops" in relative.parts and loop_dir not in path.parents:
            continue
        location = relative.as_posix()
        for match in AUTHORITY_DECLARATION_PATTERN.finditer(text):
            if not _declared_authority_ok(match.group(1), match.group(2)):
                errors.append(f"{location}: supporting artifact declares competing lifecycle authority")
        if not _has_heading(text, "## Lifecycle Projections"): continue
        boundary = _section_field(text, "## Lifecycle Projections", "Derived at Git boundary")
        if boundary is None or not SHA_PATTERN.fullmatch(boundary):
            errors.append(f"{location}: Lifecycle Projections require a 40-character Git boundary")
            boundary = "invalid"
        elif not _known_boundary(root, head, boundary): errors.append(f"{location}: lifecycle projection Git boundary drift")
        rows = _table(text, "## Lifecycle Projections", ("Assertion", "Authority", "Value"), location, errors)
        for row in rows:
            assertion = row["Assertion"]
            if not _valid_assertion(assertion): errors.append(f"{location}: invalid lifecycle assertion {assertion!r}"); continue
            expected_authority = _assertion_authority(assertion)
            if row["Authority"] != expected_authority:
                errors.append(f"{location}: {assertion} must reference {expected_authority}, not {row['Authority']}"); continue
            fact = facts.get(assertion)
            if fact is None: errors.append(f"{location}: {assertion} has no available authoritative value"); continue
            key = (location, assertion)
            if key in projections: errors.append(f"{location}: duplicate lifecycle projection for {assertion}"); continue
            projection = Projection(location, assertion, row["Authority"], row["Value"], boundary)
            projections[key] = projection
            if assertion == "Git.current_boundary":
                consistent = _known_boundary(root, head, projection.value)
            else:
                consistent = _same(projection.value, fact.value)
            if not consistent:
                errors.append(f"{location}: lifecycle consistency drift for {assertion}; authority wins and an existing Process Finding is required before Closure")
    return projections


def _validate_closure_snapshot(root: Path, closure_path: Path, closure_text: str, facts: dict[str, Fact], projections: dict[tuple[str, str], Projection], errors: list[str]) -> None:
    state_root = root / ".looppilot"
    location = closure_path.relative_to(state_root).as_posix()
    for field in ("Assertion snapshot", "Deterministic validation", "Semantic projection review", "Open consistency findings", "Snapshot Git boundary"):
        if _section_field(closure_text, "## Lifecycle Consistency", field) is None: errors.append(f"{location}: Lifecycle Consistency missing {field!r}")
    command = _section_field(closure_text, "## Lifecycle Consistency", "Deterministic validation")
    if command is not None and "scripts/validate.py" not in command: errors.append(f"{location}: lifecycle validation must use public scripts/validate.py")
    boundary = _section_field(closure_text, "## Lifecycle Consistency", "Snapshot Git boundary")
    head = _git_head(root)
    if boundary is not None:
        if not SHA_PATTERN.fullmatch(boundary): errors.append(f"{location}: Snapshot Git boundary must be a 40-character SHA")
        elif not _known_boundary(root, head, boundary): errors.append(f"{location}: closure snapshot Git boundary drift")
    rows = _table(closure_text, "## Lifecycle Consistency", ("Assertion", "Authority", "Projection", "Expected", "Observed", "Consistent"), location, errors)
    covered: set[str] = set(); referenced: set[tuple[str, str]] = set(); drift = False
    for row in rows:
        assertion = row["Assertion"]
        if not _valid_assertion(assertion): errors.append(f"{location}: invalid lifecycle assertion {assertion!r}"); continue
        if assertion in covered: errors.append(f"{location}: duplicate lifecycle assertion row {assertion!r}"); continue
        fact = facts.get(assertion)
        if fact is None:
            if assertion == "Git.current_boundary" and head is None:
                continue
            errors.append(f"{location}: {assertion} has no available authoritative value"); continue
        covered.add(assertion)
        if row["Authority"] != fact.authority: errors.append(f"{location}: {assertion} must use authority {fact.authority}")
        boundary_assertion = assertion == "Git.current_boundary"
        if boundary_assertion:
            expected_ok = _known_boundary(root, head, row["Expected"])
        else:
            expected_ok = _same(row["Expected"], fact.value)
        if not expected_ok: errors.append(f"{location}: {assertion} Expected does not match authority"); drift = True
        projection_name = row["Projection"]
        if projection_name == "authoritative-only": observed = row["Observed"] if boundary_assertion else fact.value
        else:
            key = (projection_name, assertion); projection = projections.get(key)
            if projection is None: errors.append(f"{location}: {assertion} references missing projection {projection_name!r}"); continue
            referenced.add(key); observed = projection.value
        if boundary_assertion:
            observed_ok = _known_boundary(root, head, row["Observed"]) and _same(row["Observed"], observed)
        else:
            observed_ok = _same(row["Observed"], observed)
        if not observed_ok:
            errors.append(f"{location}: {assertion} Observed does not match projection"); drift = True
        if boundary_assertion:
            consistent = _known_boundary(root, head, observed)
        else:
            consistent = _same(fact.value, observed)
        if row["Consistent"].casefold() != ("yes" if consistent else "no"): errors.append(f"{location}: {assertion} Consistent flag is incorrect")
        if not consistent: errors.append(f"{location}: lifecycle consistency drift for {assertion}; authority remains winning and Closure is not eligible"); drift = True
    missing = sorted(set(facts) - covered)
    if missing: errors.append(f"{location}: lifecycle assertion snapshot missing {missing!r}")
    unreferenced = sorted(set(projections) - referenced)
    if unreferenced: errors.append(f"{location}: lifecycle snapshot omits material projections {unreferenced!r}")
    semantic = _section_field(closure_text, "## Lifecycle Consistency", "Semantic projection review")
    closure_status = _field(closure_text, "Closure Status")
    if closure_status in {"ready-for-acceptance", "accepted"} and semantic != "pass": errors.append(f"{location}: Closure readiness requires semantic projection review pass")
    open_findings = _section_field(closure_text, "## Lifecycle Consistency", "Open consistency findings")
    if drift and open_findings is not None and open_findings.casefold() in {"none", "no"}: errors.append(f"{location}: lifecycle drift cannot declare no open consistency Findings")


def _declared_lines(lines: list[str]) -> set[int]:
    """Line indexes exempt from the undeclared-copy check.

    A declared lifecycle section carries the metadata, and a fenced block is
    format documentation rather than a live value, so both are exempt.
    """
    declared: set[int] = set()
    for index, line in enumerate(lines):
        if line.strip() not in DECLARED_SECTIONS:
            continue
        for offset in range(index + 1, len(lines)):
            if re.match(r"^#{1,2} ", lines[offset]):
                break
            declared.add(offset)
    fenced = False
    for index, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            declared.add(index)
        elif fenced:
            declared.add(index)
    return declared


def _validate_declared_projection_metadata(root: Path, errors: list[str]) -> None:
    """Reject a copied lifecycle value that carries no authority metadata.

    A supporting artifact may restate a lifecycle fact only inside a declared
    section, where it names its authority, its Git boundary, and its derived
    status. The same value written as free prose has no source location, no
    commit boundary, and no derived label, so it is invalid rather than merely
    undocumented. A fenced block documents the format rather than tracking a
    live value and is exempt. Semantic staleness of undeclared narrative stays
    Reviewer work.
    """
    state_root = root / ".looppilot"
    if not state_root.is_dir():
        return
    for path in sorted(state_root.rglob("*.md")):
        if "-TEMPLATE" in path.name or path.name in AUTHORITY_FILES:
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        declared = _declared_lines(lines)
        location = path.relative_to(state_root).as_posix()
        reported: set[str] = set()
        for index, line in enumerate(lines):
            if index in declared:
                continue
            for match in ASSERTION_TOKEN_PATTERN.finditer(line):
                assertion = match.group(0)
                if assertion in reported:
                    continue
                reported.add(assertion)
                errors.append(
                    f"{location}: lifecycle value {assertion} is copied without "
                    "authority metadata; declare it under "
                    "'## Lifecycle Projections' with its authority and Git boundary"
                )


def _validate_static_freeze(root: Path, errors: list[str]) -> None:
    state_root = root / ".looppilot"
    seen: set[str] = set()
    for path in sorted(root.rglob("*.md")):
        if any(part in {".git", "node_modules", ".venv", ".tmp"} for part in path.parts):
            continue
        if path.name in FORBIDDEN_LEDGER_FILES and path.name not in seen:
            seen.add(path.name)
            errors.append(f"Phase 11 forbidden lifecycle store: {path.name}")
    closure_path = state_root / "full-loop" / "LOOP-CLOSURE-TEMPLATE.md"
    if not closure_path.is_file():
        errors.append("LOOP-CLOSURE-TEMPLATE.md: missing Phase 11 template")
        closure = ""
    else:
        closure = closure_path.read_text(encoding="utf-8")
    for token in ("## Lifecycle Consistency", "- Assertion snapshot:", "- Deterministic validation:", "- Semantic projection review:", "- Open consistency findings:"):
        if closure and token not in closure: errors.append(f"LOOP-CLOSURE-TEMPLATE.md: missing Phase 11 requirement {token!r}")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in (root / "SKILL.md", root / "AGENTS.md", root / "docs" / "lifecycle-authority-and-derived-projections.md"))
    for heading in ("## Lifecycle Barrier", "## Consistency Barrier", "## Projection Barrier"):
        if heading in combined: errors.append(f"Phase 11 must not define a new Barrier: {heading}")


def validate_lifecycle_consistency(root: Path, errors: list[str], warnings: list[str]) -> None:
    """Validate static calibration and any real Full Loop closure snapshots."""
    _validate_static_freeze(root, errors)
    _validate_declared_projection_metadata(root, errors)
    loops_root = root / ".looppilot" / "loops"
    if not loops_root.is_dir(): return
    for closure_path in sorted(loops_root.rglob("LOOP-CLOSURE.md")):
        closure_text = closure_path.read_text(encoding="utf-8")
        if not _has_heading(closure_text, "## Lifecycle Consistency"):
            warnings.append(f"{closure_path.relative_to(root).as_posix()}: legacy Closure has no Lifecycle Consistency snapshot; migrate before its next closure decision")
            facts = _collect_authority(
                root, closure_path.parent, closure_text, warnings, warnings
            )
            _collect_projections(
                root, closure_path.parent, facts, _git_head(root), errors
            )
            continue
        facts = _collect_authority(root, closure_path.parent, closure_text, errors, warnings)
        projections = _collect_projections(
            root, closure_path.parent, facts, _git_head(root), errors
        )
        _validate_closure_snapshot(root, closure_path, closure_text, facts, projections, errors)
