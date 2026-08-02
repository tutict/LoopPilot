"""Validate Cross-Host Acceptance records without claiming host compatibility."""

from __future__ import annotations

import re
from pathlib import Path

CROSS_HOST_ACCEPTANCE_FILES = (
    "scripts/cross_host_acceptance_validation.py",
    "tests/test_cross_host_acceptance.py",
    "docs/cross-host-acceptance.md",
    "evaluations/templates/host-acceptance-record.md",
)
RECORD_TITLE = "Host Acceptance Record"
RECORD_HEADING = f"# {RECORD_TITLE}"
VERDICTS = {"unverified", "rejected", "accepted-with-residuals", "accepted"}
EVIDENCE_VERDICTS = {"accepted", "accepted-with-residuals"}
DIMENSION_RESULTS = {"pass", "partial", "fail", "not-evaluated"}
EVIDENCE_RESULTS = {"pass", "partial"}
REQUIRED_FIELDS = (
    "Host",
    "Host version",
    "Model",
    "LoopPilot commit",
    "Skill loading mode",
    "Evaluation IDs",
    "Scenario coverage",
    "Trace author",
    "Independent reviewer",
    "Lowest critical rubric score",
    "Date",
    "Verdict",
    "Residual limitations",
)
IDENTITY_FIELDS = ("Host", "Host version", "Model", "Skill loading mode", "Date")
REQUIRED_DIMENSIONS = (
    "Skill loading and activation",
    "Mode selection",
    "Authority and stopping",
    "Shared-state handling",
    "Full Loop artifact handling",
    "Checkpoint recovery",
    "Lifecycle projections",
    "Evidence honesty",
)
REQUIRED_FIXTURE_SHAPES = ("lightweight", "full loop")
MINIMUM_CRITICAL_SCORE = 2
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SCORE_PATTERN = re.compile(r"^[0-3]$")


def _field(text: str, name: str) -> str | None:
    match = re.search(
        rf"^-[ \t]*{re.escape(name)}:[ \t]*(.*)$", text, re.MULTILINE
    )
    return match.group(1).strip() if match else None


def _dimension_rows(text: str) -> tuple[dict[str, tuple[str, str]], list[str]]:
    """Return the first row per dimension plus every duplicated dimension name."""
    rows: dict[str, tuple[str, str]] = {}
    duplicates: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] not in REQUIRED_DIMENSIONS:
            continue
        if cells[0] in rows:
            duplicates.append(cells[0])
            continue
        rows[cells[0]] = (cells[1], cells[2] if len(cells) >= 3 else "")
    return rows, duplicates


def _none(value: str | None) -> bool:
    """Treat the repository's ``none``, ``None.``, and ``N/A`` styles as empty."""
    if value is None:
        return True
    return value.strip().rstrip(".").casefold() in {"none", "no", "n/a", "na", ""}


def _is_record(text: str) -> bool:
    """Match a level-1 heading that names a Host Acceptance Record.

    A real record is scoped to one host, version, model, and loading mode, so a
    qualified title such as ``# Host Acceptance Record: Claude Code 2.1.0`` is
    the natural authoring choice and MUST stay validated.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#") or stripped.startswith("##"):
            continue
        title = stripped.lstrip("#").strip()
        if title == RECORD_TITLE or title.startswith(RECORD_TITLE):
            return True
    return False


def _validate_record(location: str, text: str, errors: list[str]) -> None:
    fields = {name: _field(text, name) for name in REQUIRED_FIELDS}
    for name, value in fields.items():
        if value is None:
            errors.append(f"{location}: Host Acceptance Record missing field {name!r}")
    for name in IDENTITY_FIELDS:
        value = fields.get(name)
        if value is not None and _none(value):
            errors.append(
                f"{location}: Host Acceptance Record field {name!r} requires a value"
            )
    date = fields.get("Date")
    if date is not None and not _none(date) and not DATE_PATTERN.fullmatch(date):
        errors.append(f"{location}: Date {date!r} must use YYYY-MM-DD")

    verdict = fields.get("Verdict")
    if verdict is not None and verdict not in VERDICTS:
        errors.append(f"{location}: unknown acceptance verdict {verdict!r}")
        verdict = None

    rows, duplicates = _dimension_rows(text)
    for dimension in sorted(set(duplicates)):
        errors.append(f"{location}: duplicate dimension row {dimension!r}")
    for dimension in REQUIRED_DIMENSIONS:
        row = rows.get(dimension)
        if row is None:
            errors.append(f"{location}: missing dimension row {dimension!r}")
            continue
        result, evidence = row
        if result not in DIMENSION_RESULTS:
            errors.append(
                f"{location}: dimension {dimension!r} has unknown result {result!r}"
            )
        elif result in EVIDENCE_RESULTS and _none(evidence):
            errors.append(
                f"{location}: dimension {dimension!r} records {result!r} without "
                "preserved evidence; use not-evaluated"
            )

    failed = sorted(
        dimension
        for dimension, (result, _) in rows.items()
        if result == "fail"
    )
    if verdict is not None and verdict != "rejected" and failed:
        errors.append(
            f"{location}: verdict {verdict} cannot carry failed dimension "
            f"{failed[0]!r}; a failed dimension requires the rejected verdict"
        )
    if verdict == "rejected" and not failed:
        errors.append(
            f"{location}: verdict rejected requires at least one failed dimension"
        )

    if verdict not in EVIDENCE_VERDICTS:
        return

    commit = fields.get("LoopPilot commit")
    if commit is None or not SHA_PATTERN.fullmatch(commit):
        errors.append(
            f"{location}: verdict {verdict} requires a 40-character lowercase "
            "hexadecimal LoopPilot commit"
        )
    if _none(fields.get("Evaluation IDs")):
        errors.append(
            f"{location}: verdict {verdict} requires at least one referenced evaluation run"
        )
    coverage = fields.get("Scenario coverage")
    if _none(coverage):
        errors.append(
            f"{location}: verdict {verdict} requires disclosed scenario coverage"
        )
    else:
        folded = re.sub(r"[-_]+", " ", coverage.casefold())
        missing = [shape for shape in REQUIRED_FIXTURE_SHAPES if shape not in folded]
        for shape in missing:
            errors.append(
                f"{location}: verdict {verdict} requires a {shape}-shaped fixture "
                "in the disclosed scenario coverage"
            )
    author = fields.get("Trace author")
    reviewer = fields.get("Independent reviewer")
    if _none(author):
        errors.append(
            f"{location}: verdict {verdict} requires a named trace author"
        )
    if _none(reviewer):
        errors.append(
            f"{location}: verdict {verdict} requires an independent reviewer"
        )
    if (
        not _none(author)
        and not _none(reviewer)
        and author.casefold() == reviewer.casefold()
    ):
        errors.append(
            f"{location}: verdict {verdict} requires a reviewer who did not "
            f"produce the traces; {reviewer!r} also authored them"
        )
    score = fields.get("Lowest critical rubric score")
    if _none(score) or not SCORE_PATTERN.fullmatch(score or ""):
        errors.append(
            f"{location}: verdict {verdict} requires the lowest critical rubric "
            "score as a 0-3 integer"
        )
    elif int(score) < MINIMUM_CRITICAL_SCORE:
        errors.append(
            f"{location}: verdict {verdict} requires every critical rubric "
            f"dimension at {MINIMUM_CRITICAL_SCORE} or higher, observed {score}"
        )

    allowed = {"pass"} if verdict == "accepted" else {"pass", "partial"}
    for dimension in REQUIRED_DIMENSIONS:
        row = rows.get(dimension)
        if row is not None and row[0] in DIMENSION_RESULTS and row[0] not in allowed:
            errors.append(
                f"{location}: verdict {verdict} forbids dimension result {row[0]!r} for {dimension!r}"
            )
    residuals = fields.get("Residual limitations")
    if verdict == "accepted" and not _none(residuals):
        errors.append(
            f"{location}: verdict accepted cannot carry residual limitations; use accepted-with-residuals"
        )
    if verdict == "accepted-with-residuals" and _none(residuals):
        errors.append(
            f"{location}: verdict accepted-with-residuals requires disclosed residual limitations"
        )


def validate_cross_host_acceptance(root: Path, errors: list[str]) -> None:
    """Validate the acceptance template and any real Host Acceptance Records."""
    template = root / "evaluations" / "templates" / "host-acceptance-record.md"
    if template.is_file():
        text = template.read_text(encoding="utf-8")
        if not _is_record(text):
            errors.append(
                "evaluations/templates/host-acceptance-record.md: missing record heading"
            )
        if _field(text, "Verdict") != "unverified":
            errors.append(
                "evaluations/templates/host-acceptance-record.md: template verdict must stay unverified"
            )
        for name in REQUIRED_FIELDS:
            if _field(text, name) is None:
                errors.append(
                    "evaluations/templates/host-acceptance-record.md: "
                    f"template missing field {name!r}"
                )
        rows, _ = _dimension_rows(text)
        for dimension, (result, _evidence) in rows.items():
            if result != "not-evaluated":
                errors.append(
                    "evaluations/templates/host-acceptance-record.md: "
                    f"template dimension {dimension!r} must stay not-evaluated"
                )
    evaluations = root / "evaluations"
    if not evaluations.is_dir():
        return
    for path in sorted(evaluations.rglob("*.md")):
        relative = path.relative_to(root)
        if relative.parts[:2] == ("evaluations", "templates"):
            continue
        text = path.read_text(encoding="utf-8")
        location = relative.as_posix()
        if not _is_record(text):
            verdict = _field(text, "Verdict")
            if verdict is not None and verdict in VERDICTS:
                errors.append(
                    f"{location}: declares acceptance verdict {verdict!r} without "
                    f"a {RECORD_HEADING!r} heading"
                )
            continue
        _validate_record(location, text, errors)
