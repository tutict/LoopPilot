"""Validate the first-stage Loop Engineering architecture contract."""

from __future__ import annotations

from pathlib import Path


PROJECT_TEMPLATE = ".looppilot/PROJECT-TEMPLATE.md"
ARCHITECTURE_DOCUMENTS = (
    "docs/loop-engineering-model.md",
    "docs/project-engineering-context.md",
    "docs/protocol-modes-and-state-sources.md",
    "docs/architecture-pattern-selection.md",
    "docs/project-closure.md",
    "docs/full-loop-migration-plan.md",
    "docs/full-loop-contracts-and-ledgers.md",
)
PROJECT_HEADINGS = (
    "## Problem",
    "## Users and Actors",
    "## Core Use Cases",
    "## Included Scope",
    "## Excluded Scope",
    "## Domain Model",
    "## Data",
    "## Concurrency",
    "## Identity and Permissions",
    "## Security",
    "## Observability",
    "## Delivery and Operations",
    "## Evolution",
    "## Team Boundaries",
    "## Architecture Profile",
    "## Engineering Concern Matrix",
    "## Project Acceptance Criteria",
    "## Full Loop Relationships",
)
PROJECT_SUBHEADINGS = (
    "### Entities",
    "### Value Objects",
    "### Aggregates",
    "### Domain Events",
    "### Business Invariants",
    "### Sources",
    "### Ownership",
    "### Lifecycle",
    "### Consistency",
    "### Retention",
    "### Migration",
    "### Shared Resources",
    "### Race Conditions",
    "### Idempotency",
    "### Ordering",
    "### Locking or Optimistic Concurrency",
    "### Authentication",
    "### Roles",
    "### Resource Ownership",
    "### Authorization Rules",
    "### Audit Requirements",
    "### Trust Boundaries",
    "### Sensitive Data",
    "### Input Risks",
    "### Secret Handling",
    "### Abuse Cases",
    "### Logs",
    "### Metrics",
    "### Traces",
    "### Audit Events",
    "### Alerts",
    "### Deployment",
    "### Configuration",
    "### Health Checks",
    "### Rollback",
    "### Gray Release",
    "### Data Rollback Limitations",
    "### API Compatibility",
    "### Schema Migration",
    "### Version Strategy",
    "### Deprecation",
    "### Extension Points",
    "### Module Ownership",
    "### Review Ownership",
    "### Integration Ownership",
    "### Release Responsibility",
    "### Domain Modeling",
    "### Backend Architecture",
    "### Frontend Architecture",
    "### Dependency Injection",
    "### Performance Strategy",
    "### Explicitly Rejected Patterns",
    "### Project Functional Acceptance",
    "### Project Engineering Acceptance",
    "### Project Delivery Acceptance",
    "### Project Identifier",
    "### Loop Map",
    "### Current Authoritative Files",
    "### Project Closure",
)
CONCERN_ROWS = (
    "Users",
    "Business Rules",
    "Data",
    "Concurrency",
    "Permissions",
    "Security",
    "Logging",
    "Monitoring",
    "Rollback",
    "Gray Release",
    "Operations",
    "Version Evolution",
    "Team Collaboration",
)
SINGLE_SOURCE_ROWS = (
    ("Project Scope", "PROJECT.md"),
    ("Loop list and Loop status", "LOOP-MAP.md"),
    ("Task status", "Current Loop TASK-LEDGER.md"),
    ("Finding status", "Current Loop FINDING-LEDGER.md"),
    ("Current recovery entry", "Root CHECKPOINT.md"),
)
CREDENTIAL_NAMES = (
    "api_key",
    "api key",
    "access_token",
    "access token",
    "token",
    "secret",
    "password",
    "cookie",
    "credential",
)
PLACEHOLDER_VALUES = {"none", "redacted", "placeholder", "<value>"}
POSITIVE_HOST_CLAIMS = tuple(
    f"full loop mode {verb} {host}".casefold()
    for verb in (
        "is validated on",
        "is verified on",
        "has been validated on",
        "has been verified on",
        "was validated on",
        "was verified on",
        "works on",
        "works with",
        "supports",
        "is compatible with",
        "is certified for",
        "is production-ready on",
        "is proven on",
    )
    for host in ("Codex", "Gemini CLI", "GitHub Copilot")
)
LOOP_DEFINITION = (
    "A Loop is a cohesive change set that can be independently implemented, "
    "integrated, reviewed, accepted, committed when authorized, and resumed "
    "from persisted state."
)


def _require_lines(
    text: str, required: tuple[str, ...], location: str, errors: list[str]
) -> None:
    lines = set(text.splitlines())
    for line in required:
        if line not in lines:
            errors.append(f"{location}: missing required heading {line!r}")


def _template_has_content(text: str) -> bool:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if (
            not line
            or line == "Status: inactive"
            or line == "`PROJECT.md` is the only authority for Project status."
            or line.startswith("#")
            or line.startswith("|")
            or (line.startswith("- ") and line.endswith(": none"))
        ):
            continue
        return True
    return False


def _contains_credential_assignment(text: str) -> bool:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        lowered = line.casefold()
        for name in CREDENTIAL_NAMES:
            for separator in (":", "="):
                prefix = name + separator
                if not lowered.startswith(prefix):
                    continue
                value = line[len(prefix) :].strip().casefold()
                if value and value not in PLACEHOLDER_VALUES and not value.startswith("<"):
                    return True
    return False


def validate_loop_engineering(root: Path, errors: list[str]) -> None:
    """Validate structural Phase 1 artifacts without simulating a workflow."""

    template_path = root / PROJECT_TEMPLATE
    template = template_path.read_text(encoding="utf-8")
    template_lines = set(template.splitlines())
    _require_lines(
        template, PROJECT_HEADINGS + PROJECT_SUBHEADINGS, PROJECT_TEMPLATE, errors
    )

    if "Status: inactive" not in template_lines:
        errors.append(f"{PROJECT_TEMPLATE}: must remain Status: inactive")
    if _template_has_content(template):
        errors.append(
            f"{PROJECT_TEMPLATE}: inactive template must remain blank"
        )
    if _contains_credential_assignment(template):
        errors.append(f"{PROJECT_TEMPLATE}: possible credential assignment")

    for concern in CONCERN_ROWS:
        expected = f"| {concern} | | | |"
        if expected not in template_lines:
            errors.append(
                f"{PROJECT_TEMPLATE}: Engineering Concern Matrix missing "
                f"blank row {concern!r}"
            )

    model_location = "docs/loop-engineering-model.md"
    model = (root / model_location).read_text(encoding="utf-8")
    if LOOP_DEFINITION not in " ".join(model.split()):
        errors.append(f"{model_location}: missing canonical Loop definition")
    for term in (
        "Project",
        "Loop",
        "Task",
        "Worker Delivery",
        "Review Report",
        "Finding",
        "Integration Record",
        "Loop Closure",
        "Checkpoint",
        "Commit Boundary",
        "Contract Barrier",
        "Closure Barrier",
        "Functional Acceptance",
        "Engineering Acceptance",
        "Delivery Acceptance",
    ):
        if term not in model:
            errors.append(f"{model_location}: missing required concept {term!r}")

    modes_location = "docs/protocol-modes-and-state-sources.md"
    modes = (root / modes_location).read_text(encoding="utf-8")
    mode_lines = set(modes.splitlines())
    _require_lines(
        modes,
        ("## Lightweight Mode", "## Full Loop Mode", "## Full Loop Sources of Truth"),
        modes_location,
        errors,
    )
    for state, source in SINGLE_SOURCE_ROWS:
        expected = f"| {state} | {source} |"
        if expected not in mode_lines:
            errors.append(
                f"{modes_location}: missing single source of truth for {state}"
            )

    for relative in ARCHITECTURE_DOCUMENTS:
        text = " ".join((root / relative).read_text(encoding="utf-8").split())
        folded = text.casefold()
        if any(claim in folded for claim in POSITIVE_HOST_CLAIMS):
            errors.append(
                f"{relative}: must not claim Full Loop Mode real-host validation"
            )
