import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = Path("evaluations") / "claude-code" / "host-acceptance.md"


def record(**overrides: str) -> str:
    fields = {
        "Host": "Claude Code",
        "Host version": "2.1.0",
        "Model": "claude-example",
        "LoopPilot commit": "a" * 40,
        "Skill loading mode": "explicit",
        "Evaluation IDs": "EVAL-001, EVAL-002",
        "Scenario coverage": "lightweight-fix, full-loop-feature",
        "Trace author": "evaluator-a",
        "Independent reviewer": "reviewer-b",
        "Lowest critical rubric score": "3",
        "Date": "2026-07-30",
        "Verdict": "accepted",
        "Residual limitations": "none",
    }
    dimensions = {
        "Skill loading and activation": "pass",
        "Mode selection": "pass",
        "Authority and stopping": "pass",
        "Shared-state handling": "pass",
        "Full Loop artifact handling": "pass",
        "Checkpoint recovery": "pass",
        "Lifecycle projections": "pass",
        "Evidence honesty": "pass",
    }
    title = "# Host Acceptance Record"
    for name, value in overrides.items():
        key = name.replace("_", " ")
        if key == "TITLE":
            title = value
            continue
        if key in fields:
            fields[key] = value
        else:
            matches = [d for d in dimensions if d.casefold() == key.casefold()]
            if len(matches) != 1:
                raise KeyError(name)
            dimensions[matches[0]] = value
    lines = [title, ""]
    lines += [
        f"- {name}: {value}".rstrip()
        for name, value in fields.items()
        if value != "OMIT"
    ]
    lines += ["", "## Dimension Results", "", "| Dimension | Result | Evidence |", "| --- | --- | --- |"]
    lines += [
        f"| {name} | {value} | trace reference |"
        for name, value in dimensions.items()
        if value != "OMIT"
    ]
    return "\n".join(lines) + "\n"


UNVERIFIED_STUB = {
    "Verdict": "unverified",
    "LoopPilot commit": "none",
    "Evaluation IDs": "none",
    "Scenario coverage": "none",
    "Trace author": "none",
    "Independent reviewer": "none",
    "Lowest critical rubric score": "none",
    "Skill loading and activation": "not-evaluated",
    "Mode selection": "not-evaluated",
    "Authority and stopping": "not-evaluated",
    "Shared-state handling": "not-evaluated",
    "Full Loop artifact handling": "not-evaluated",
    "Checkpoint recovery": "not-evaluated",
    "Lifecycle projections": "not-evaluated",
    "Evidence honesty": "not-evaluated",
}


@dataclass(frozen=True)
class Case:
    name: str
    expected_error: str | None = None
    overrides: dict[str, str] | None = None
    operation: str = "record"


CASES = (
    Case("repository_without_records_passes", operation="repository"),
    Case("accepted_record_passes"),
    Case(
        "accepted_with_residuals_passes",
        overrides={
            "Verdict": "accepted-with-residuals",
            "Residual_limitations": "prompt-only continuity remains weak",
            "Checkpoint_recovery": "partial",
        },
    ),
    Case("rejected_record_passes", overrides={"Verdict": "rejected", "Checkpoint_recovery": "fail"}),
    Case("unverified_stub_skips_accepted_requirements", overrides=dict(UNVERIFIED_STUB)),
    Case("unknown_verdict_is_rejected", overrides={"Verdict": "compatible"}, expected_error="unknown acceptance verdict"),
    Case(
        "unknown_verdict_still_reports_dimension_errors",
        overrides={"Verdict": "compatible", "Mode_selection": "green"},
        expected_error="unknown result 'green'",
    ),
    Case("missing_host_field_is_rejected", overrides={"Host": "OMIT"}, expected_error="missing field 'Host'"),
    Case("missing_dimension_row_is_rejected", overrides={"Checkpoint_recovery": "OMIT"}, expected_error="missing dimension row 'Checkpoint recovery'"),
    Case("unknown_dimension_result_is_rejected", overrides={"Mode_selection": "green"}, expected_error="unknown result 'green'"),
    Case("accepted_with_failed_dimension_is_rejected", overrides={"Authority_and_stopping": "fail"}, expected_error="forbids dimension result 'fail'"),
    Case(
        "accepted_with_residuals_forbids_failed_dimension",
        overrides={
            "Verdict": "accepted-with-residuals",
            "Residual_limitations": "checkpoint recovery is unreliable",
            "Checkpoint_recovery": "fail",
        },
        expected_error="forbids dimension result 'fail'",
    ),
    Case("accepted_with_partial_dimension_is_rejected", overrides={"Mode_selection": "partial"}, expected_error="forbids dimension result 'partial'"),
    Case("accepted_with_not_evaluated_dimension_is_rejected", overrides={"Evidence_honesty": "not-evaluated"}, expected_error="forbids dimension result 'not-evaluated'"),
    Case("accepted_requires_full_commit_boundary", overrides={"LoopPilot_commit": "abc1234"}, expected_error="requires a 40-character lowercase"),
    Case("accepted_requires_evaluation_runs", overrides={"Evaluation_IDs": "none"}, expected_error="requires at least one referenced evaluation run"),
    Case("accepted_requires_scenario_coverage", overrides={"Scenario_coverage": "none"}, expected_error="requires disclosed scenario coverage"),
    Case(
        "accepted_requires_full_loop_fixture",
        overrides={"Scenario_coverage": "one lightweight typo fix"},
        expected_error="requires a full loop-shaped fixture",
    ),
    Case(
        "accepted_requires_lightweight_fixture",
        overrides={"Scenario_coverage": "one full-loop delivery"},
        expected_error="requires a lightweight-shaped fixture",
    ),
    Case("accepted_requires_independent_reviewer", overrides={"Independent_reviewer": "none"}, expected_error="requires an independent reviewer"),
    Case("accepted_requires_trace_author", overrides={"Trace_author": "none"}, expected_error="requires a named trace author"),
    Case(
        "reviewer_cannot_review_own_traces",
        overrides={"Trace_author": "reviewer-b"},
        expected_error="also authored them",
    ),
    Case(
        "accepted_requires_critical_rubric_score",
        overrides={"Lowest_critical_rubric_score": "none"},
        expected_error="requires the lowest critical rubric score",
    ),
    Case(
        "critical_rubric_score_below_two_is_rejected",
        overrides={"Lowest_critical_rubric_score": "1"},
        expected_error="requires every critical rubric dimension at 2 or higher",
    ),
    Case(
        "accepted_cannot_carry_residuals",
        overrides={"Residual_limitations": "flaky activation"},
        expected_error="cannot carry residual limitations",
    ),
    Case(
        "residual_none_with_period_is_accepted",
        overrides={"Residual_limitations": "None."},
    ),
    Case(
        "accepted_with_residuals_requires_disclosure",
        overrides={
            "Verdict": "accepted-with-residuals",
            "Checkpoint_recovery": "partial",
        },
        expected_error="requires disclosed residual limitations",
    ),
    Case(
        "empty_identity_field_is_rejected",
        overrides={"Host_version": ""},
        expected_error="field 'Host version' requires a value",
    ),
    Case(
        "non_iso_date_is_rejected",
        overrides={"Date": "July 30 2026"},
        expected_error="must use YYYY-MM-DD",
    ),
    Case(
        "failed_dimension_under_unverified_is_rejected",
        overrides={**UNVERIFIED_STUB, "Checkpoint_recovery": "fail"},
        expected_error="requires the rejected verdict",
    ),
    Case(
        "rejected_without_failed_dimension_is_rejected",
        overrides={"Verdict": "rejected"},
        expected_error="requires at least one failed dimension",
    ),
    Case(
        "qualified_record_title_is_still_validated",
        overrides={"TITLE": "# Host Acceptance Record: Claude Code 2.1.0", "Evaluation_IDs": "none"},
        expected_error="requires at least one referenced evaluation run",
    ),
    Case(
        "verdict_without_record_heading_is_rejected",
        overrides={"TITLE": "# Claude Code Notes"},
        expected_error="without a '# Host Acceptance Record' heading",
    ),
    Case(
        "nested_templates_directory_is_still_validated",
        operation="nested_template_record",
        expected_error="requires at least one referenced evaluation run",
    ),
    Case("pass_without_evidence_is_rejected", operation="blank_evidence", expected_error="without preserved evidence"),
    Case("duplicate_dimension_row_is_rejected", operation="duplicate_row", expected_error="duplicate dimension row 'Mode selection'"),
    Case("template_verdict_must_stay_unverified", operation="template_verdict", expected_error="template verdict must stay unverified"),
    Case("template_dimensions_stay_not_evaluated", operation="template_dimension", expected_error="must stay not-evaluated"),
    Case("template_missing_field_is_rejected", operation="template_field", expected_error="template missing field 'Trace author'"),
    Case("missing_template_is_rejected", operation="remove_template", expected_error="host-acceptance-record.md"),
    Case("missing_protocol_document_is_rejected", operation="remove_doc", expected_error="cross-host-acceptance.md"),
)


class CrossHostAcceptanceTests(unittest.TestCase):
    maxDiff = None

    def copy_repository(self, directory: str) -> Path:
        fixture = Path(directory) / "repository"
        shutil.copytree(
            REPOSITORY_ROOT,
            fixture,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", ".tmp"
            ),
        )
        return fixture

    def validate(self, fixture: Path) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, str(fixture / "scripts" / "validate.py"), "--root", str(fixture)],
            cwd=fixture, env=environment, capture_output=True, text=True, check=False,
        )

    def write(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def exercise(self, case: Case) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            template = fixture / "evaluations" / "templates" / "host-acceptance-record.md"
            if case.operation == "record":
                self.write(fixture / RECORD_PATH, record(**(case.overrides or {})))
            elif case.operation == "nested_template_record":
                self.write(
                    fixture / "evaluations" / "claude-code" / "templates" / "record.md",
                    record(Evaluation_IDs="none"),
                )
            elif case.operation == "blank_evidence":
                text = record().replace(
                    "| Mode selection | pass | trace reference |",
                    "| Mode selection | pass |  |",
                )
                self.write(fixture / RECORD_PATH, text)
            elif case.operation == "duplicate_row":
                text = record().replace(
                    "| Mode selection | pass | trace reference |",
                    "| Mode selection | pass | trace reference |\n| Mode selection | fail | trace reference |",
                )
                self.write(fixture / RECORD_PATH, text)
            elif case.operation == "template_verdict":
                text = template.read_text(encoding="utf-8")
                self.write(template, text.replace("- Verdict: unverified", "- Verdict: accepted"))
            elif case.operation == "template_dimension":
                text = template.read_text(encoding="utf-8")
                self.write(template, text.replace("| Mode selection | not-evaluated |", "| Mode selection | pass |"))
            elif case.operation == "template_field":
                text = template.read_text(encoding="utf-8")
                self.write(template, text.replace("- Trace author: none\n", ""))
            elif case.operation == "remove_template":
                template.unlink()
            elif case.operation == "remove_doc":
                (fixture / "docs" / "cross-host-acceptance.md").unlink()
            elif case.operation != "repository":
                self.fail(f"unknown operation {case.operation}")

            result = self.validate(fixture)
            output = result.stdout + result.stderr
            if case.expected_error:
                self.assertEqual(1, result.returncode, output)
                self.assertIn(case.expected_error, output)
            else:
                self.assertEqual(0, result.returncode, output)
                self.assertIn("Static validation passed", output)


def _make_test(case: Case):
    def test(self: CrossHostAcceptanceTests) -> None:
        self.exercise(case)
    return test


if len({case.name for case in CASES}) != len(CASES):
    raise RuntimeError("Cross-Host Acceptance cases must be distinct")

for index, case in enumerate(CASES, start=1):
    setattr(CrossHostAcceptanceTests, f"test_{index:03d}_{case.name}", _make_test(case))


if __name__ == "__main__":
    unittest.main()
