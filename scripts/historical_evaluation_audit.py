"""Read-only integrity and evidence audit for pinned historical evaluations."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


POLICY_PATH = Path("scripts/evaluation_history.json")
MATRIX_PATH = Path("docs/evaluations/historical-replay-matrix.json")
CORE_DIMENSIONS = (
    "Goal fidelity", "Plan quality", "Evidence quality", "Adaptation quality",
    "Loop efficiency", "Safety", "Completion honesty",
    "Evidence integrity across agents", "Authority continuity",
    "Host-native integration",
)
INCIDENT_PATTERNS = (
    ("http-429", re.compile(r"\b429\b|rate[_ -]?limit", re.IGNORECASE)),
    ("timeout", re.compile(r"\btime[ -]?out\b|\btimed out\b", re.IGNORECASE)),
    ("host-unavailable", re.compile(r"host(?:\s+is|\s+was|\s+became)?\s+unavailable|command not found", re.IGNORECASE)),
)


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _normalized_digest(path: Path) -> str:
    text = path.read_bytes().decode("utf-8-sig").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _package_files(package: Path) -> set[str]:
    if not package.is_dir():
        return set()
    result = set()
    for path in package.rglob("*"):
        if path.is_file() or path.is_symlink() or path.is_junction():
            result.add(path.relative_to(package).as_posix())
    return result


def _fields(text: str) -> dict[str, str]:
    fields = {}
    for line in text.splitlines():
        match = re.match(r"^-\s*([^:\r\n]+):\s*(.*)$", line)
        if match:
            fields.setdefault(match.group(1).strip(), match.group(2).strip())
    return fields


def _score_recomputable(text: str) -> bool:
    rows = {}
    for line in text.splitlines():
        cells = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] in CORE_DIMENSIONS:
            if cells[0] in rows or not re.fullmatch(r"[0-3]", cells[1]):
                return False
            rows[cells[0]] = int(cells[1])
    fields = _fields(text)
    if set(rows) != set(CORE_DIMENSIONS):
        return False
    applicable = fields.get("Applicable dimensions")
    total = fields.get("Total")
    return applicable == str(len(CORE_DIMENSIONS)) and total == str(sum(rows.values()))


def _independent_reviewer(package: Path) -> bool:
    report_path = package / "reviewer-report.md"
    score_path = package / "score.md"
    environment_path = package / "environment.md"
    if not (report_path.is_file() and score_path.is_file() and environment_path.is_file()):
        return False
    report = report_path.read_text(encoding="utf-8-sig").casefold()
    score = _fields(score_path.read_text(encoding="utf-8-sig"))
    environment = _fields(environment_path.read_text(encoding="utf-8-sig"))
    reviewer = score.get("Reviewer", "").casefold()
    author = environment.get("Trace author", "").casefold()
    if not reviewer or reviewer in {"none", "not available", "unknown"}:
        return False
    if author and reviewer == author:
        return False
    blockers = (
        "independence: absent", "not an independent review", "same operator",
        "not-reviewed", "independence does not exist", "no second evaluator",
    )
    if any(phrase in report for phrase in blockers):
        return False
    return bool(re.search(r"independence:\s*(present|verified)|independent reviewer.{0,40}(confirmed|verified)", report))


def _incidents(package: Path, relative_files: set[str]) -> list[dict]:
    incidents = {}
    for relative in sorted(relative_files):
        path = package / relative
        try:
            text = path.read_bytes().decode("utf-8-sig")
        except (OSError, UnicodeError):
            continue
        for category, pattern in INCIDENT_PATTERNS:
            count = len(pattern.findall(text))
            if count:
                incidents[(relative, category)] = {
                    "artifact": relative,
                    "category": category,
                    "occurrences": count,
                }
    return list(incidents.values())


def _readability(package: Path, expected: set[str]) -> tuple[bool, list[str]]:
    errors = []
    for relative in sorted(expected):
        path = package / relative
        if not path.is_file():
            continue
        try:
            path.read_bytes().decode("utf-8-sig")
        except (OSError, UnicodeError) as error:
            errors.append(f"{relative}: {type(error).__name__}")
    return not errors and all((package / relative).is_file() for relative in expected), errors


def audit_historical_evaluations(root: Path) -> dict:
    """Inspect pinned historical bytes and evidence without changing any file."""
    root = Path(root).resolve()
    policy = _json(root / POLICY_PATH)
    matrix = _json(root / MATRIX_PATH)
    pinned = policy["files"]
    expected_packages = policy["packages"]
    raw_pins = policy.get("raw_files", {})
    if not isinstance(raw_pins, dict) or set(raw_pins) != set(pinned):
        raise ValueError("historical raw-byte pins must cover the same file set as normalized pins")
    matched_files = []
    missing_files = []
    mismatched_files = []
    byte_mismatched_files = []
    for relative, expected in sorted(pinned.items()):
        path = root / relative
        if not path.is_file():
            missing_files.append(relative)
        else:
            try:
                actual = _normalized_digest(path)
            except (OSError, UnicodeError):
                mismatched_files.append(relative)
            else:
                (matched_files if actual == expected else mismatched_files).append(relative)
                if raw_pins:
                    raw_actual = hashlib.sha256(path.read_bytes()).hexdigest()
                    if raw_actual != raw_pins.get(relative):
                        byte_mismatched_files.append(relative)

    packages = []
    all_extra_files = []
    for package_relative in expected_packages:
        package = root / package_relative
        prefix = package_relative.rstrip("/") + "/"
        expected = {name[len(prefix):] for name in pinned if name.startswith(prefix)}
        actual = _package_files(package)
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        changed = sorted(
            name for name in expected & actual
            if _normalized_digest(package / name) != pinned[f"{prefix}{name}"]
        )
        byte_changed = sorted(
            name for name in expected & actual
            if raw_pins.get(f"{prefix}{name}") and hashlib.sha256((package / name).read_bytes()).hexdigest() != raw_pins[f"{prefix}{name}"]
        )
        readable, read_errors = _readability(package, expected)
        trace_path = package / "trace.md"
        trace_text = ""
        if trace_path.is_file():
            try:
                trace_text = trace_path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError):
                readable = False
                read_errors.append("trace.md: unreadable")
        trace_reviewable = bool(trace_text.strip()) and len(trace_text.splitlines()) >= 4
        score_path = package / "score.md"
        try:
            score_text = score_path.read_text(encoding="utf-8-sig") if score_path.is_file() else ""
        except (OSError, UnicodeError):
            score_text = ""
            readable = False
            read_errors.append("score.md: unreadable")
        score_recomputable = bool(score_text) and _score_recomputable(score_text)
        independent = _independent_reviewer(package)
        incidents = _incidents(package, actual)
        historically_intact = not missing and not changed and not byte_changed and not extra
        behaviorally_evaluable = (
            trace_reviewable and score_recomputable and independent and not incidents
        )
        public_loading_evidence = bool(
            any(relative.startswith("evidence/") for relative in actual)
            and re.search(r"skill|loading|invocation", " ".join((trace_text, *[str(item) for item in incidents])), re.IGNORECASE)
        )
        if behaviorally_evaluable:
            supportability = "behavioral-conclusion"
        elif public_loading_evidence:
            supportability = "loading-only"
        elif trace_reviewable:
            supportability = "limited-behavior-observation"
        else:
            supportability = "unscorable"
        package_result = {
            "evaluation_id": package.name,
            "package": package_relative,
            "expected_files": len(expected),
            "present_files": len(expected & actual),
            "missing_files": missing,
            "changed_files": changed,
            "byte_changed_files": byte_changed,
            "extra_files": extra,
            "read_errors": read_errors,
            "historically_intact": historically_intact,
            "mechanically_readable": readable,
            "trace_reviewable": trace_reviewable,
            "score_recomputable": score_recomputable,
            "independent_reviewer_present": independent,
            "infrastructure_incidents": incidents,
            "supportability": supportability,
            "behaviorally_evaluable": behaviorally_evaluable,
            "acceptance_eligible": False,
            "acceptance_status": "not-evaluated",
            "classifications": {
                "historically-intact": historically_intact,
                "mechanically-readable": readable,
                "behaviorally-evaluable": behaviorally_evaluable,
                "acceptance-eligible": False,
            },
        }
        packages.append(package_result)
        all_extra_files.extend(f"{package_relative}/{name}" for name in extra)

    coverage = []
    for pair in matrix["pairs"]:
        prior = pair["prior_coverage"]
        control = prior["control"]
        loaded = prior["skill_loaded"]
        coverage.append({
            "pair_id": pair["pair_id"],
            "historical_evaluation_id": pair["historical_evaluation_id"],
            "scenario_id": pair["scenario_id"],
            "control": control,
            "skill_loaded": loaded,
            "historical_pair_complete": control == "observed" and loaded == "observed",
            "note": prior["note"],
        })

    summary = {
        "historical_packages": len(packages),
        "intact_packages": sum(row["historically_intact"] for row in packages),
        "readable_packages": sum(row["mechanically_readable"] for row in packages),
        "behaviorally_evaluable_packages": sum(row["behaviorally_evaluable"] for row in packages),
        "acceptance_eligible_packages": 0,
        "planned_pairs": len(coverage),
        "complete_historical_pairs": sum(row["historical_pair_complete"] for row in coverage),
        "control_arms_observed": sum(row["control"] == "observed" for row in coverage),
        "skill_loaded_arms_observed": sum(row["skill_loaded"] != "missing" for row in coverage),
    }
    return {
        "schema_version": 1,
        "policy": POLICY_PATH.as_posix(),
        "integrity": {
            "pinned_files": len(pinned),
            "matched_files": len(matched_files),
            "matched_file_paths": matched_files,
            "missing_files": missing_files,
            "mismatched_files": mismatched_files,
            "byte_mismatched_files": byte_mismatched_files,
            "byte_matched_files": len(pinned) - len(missing_files) - len(byte_mismatched_files),
            "extra_files": sorted(all_extra_files),
        },
        "packages": packages,
        "coverage": coverage,
        "summary": summary,
        "acceptance_boundary": "Historical packages remain unverified and cannot support new Host Acceptance. Only new, externally pinned v2 packages can be evaluated for a new decision.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--output", type=Path, help="write deterministic JSON report to this path")
    args = parser.parse_args(argv)
    report = audit_historical_evaluations(args.root)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(rendered)
    return 0 if not report["integrity"]["missing_files"] and not report["integrity"]["mismatched_files"] and not report["integrity"]["byte_mismatched_files"] and not report["integrity"]["extra_files"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
