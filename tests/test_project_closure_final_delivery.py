import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree

from tests.project_closure_case_matrix import MISSING_CASES, REJECTION_CASES


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate.py"
FULL_LOOP = Path(".looppilot/full-loop")
CROSS_LOOP = FULL_LOOP / "CROSS-LOOP-VALIDATION-TEMPLATE.md"
ACCEPTANCE = FULL_LOOP / "PROJECT-ACCEPTANCE-TEMPLATE.md"
READINESS = FULL_LOOP / "RELEASE-READINESS-TEMPLATE.md"
REPORT = FULL_LOOP / "FINAL-DELIVERY-REPORT-TEMPLATE.md"
REVIEW = FULL_LOOP / "REVIEW-REPORT-TEMPLATE.md"
PROTOCOL = Path("docs/project-closure-and-final-delivery.md")


class ProjectClosureFinalDeliveryTests(unittest.TestCase):
    def copy_repository(self, directory: str) -> Path:
        fixture = Path(directory) / "repository"
        copytree(
            REPOSITORY_ROOT,
            fixture,
            ignore=lambda _path, names: [
                name
                for name in names
                if name
                in {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", ".tmp"}
                or name.startswith(".tmp-")
                or name.startswith(".venv-")
            ],
        )
        return fixture

    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--root", str(root)],
            cwd=REPOSITORY_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def validate_fixture(self, mutator=None) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            if mutator is not None:
                mutator(fixture)
            return self.run_validator(fixture)

    @staticmethod
    def replace_once(path: Path, old: str, new: str) -> None:
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"fixture text not found in {path}: {old!r}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    @staticmethod
    def append(path: Path, text: str) -> None:
        path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")

    def assert_rejected(self, mutator, message: str) -> None:
        result = self.validate_fixture(mutator)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(message, result.stdout)

    def mark_cross_loop_passed(self, fixture: Path, limitations: bool = False) -> None:
        path = fixture / CROSS_LOOP
        replacements = (
            ("- Validation ID: none", "- Validation ID: VALIDATION-001"),
            ("- Project ID: none", "- Project ID: PROJECT-001"),
            ("- Performed: none", "- Performed: 2026-07-18"),
            ("- Performed by: none", "- Performed by: project reviewer"),
            (
                "- Validation Status: inactive",
                f"- Validation Status: {'passed-with-limitations' if limitations else 'passed'}",
            ),
            ("- Project boundary: none", "- Project boundary: integrated main"),
            (
                "- Verified HEAD or artifact boundary: none",
                "- Verified HEAD or artifact boundary: 0123456789abcdef",
            ),
            (
                "| None | no | none | none | none | no |",
                "| LOOP-001 | yes | closed | CLOSURE-001 | 0123456 | yes |",
            ),
            (
                "| None | not-run | none |",
                "| end-to-end scenario | pass | observed test output |",
            ),
            ("- Decision: none", "- Decision: pass"),
            ("- Reason: none", "- Reason: integrated evidence passed"),
        )
        for old, new in replacements:
            self.replace_once(path, old, new)
        if limitations:
            self.replace_once(
                path,
                "## Coverage Limitations\n\n- None.",
                "## Coverage Limitations\n\n- Remote production traffic was not exercised.",
            )

    def mark_acceptance_accepted(self, fixture: Path, with_risks: bool = False) -> None:
        path = fixture / ACCEPTANCE
        text = path.read_text(encoding="utf-8")
        text = text.replace("- [ ]", "- [x]")
        replacements = (
            ("- Acceptance ID: none", "- Acceptance ID: ACCEPTANCE-001"),
            ("- Project ID: none", "- Project ID: PROJECT-001"),
            ("- Prepared: none", "- Prepared: 2026-07-18"),
            ("- Prepared by: none", "- Prepared by: integrator"),
            ("- Supervisor: none", "- Supervisor: supervisor"),
            ("- Integrator: none", "- Integrator: integrator"),
            (
                "- Acceptance Status: inactive",
                f"- Acceptance Status: {'accepted-with-risks' if with_risks else 'accepted'}",
            ),
            ("- Project boundary: none", "- Project boundary: 0123456789abcdef"),
            ("- Delivery mode: none", "- Delivery mode: delivery-only"),
            (
                "| None | none | none | none | none | none | pending |",
                "| REQ-001 | mandatory | deliver user flow | LOOP-001 | integrated flow | cross-loop test | passed |",
            ),
            (
                "| None | no | none | none | none | none |",
                "| LOOP-001 | yes | LOOP-MAP.md | CLOSURE-001 | closed | observed closure |",
            ),
            ("- Validation: none", "- Validation: VALIDATION-001"),
            ("- Result: none", "- Result: passed"),
            (
                "### Project Spec Review\n\n- Result: not-evaluated",
                "### Project Spec Review\n\n- Result: pass",
            ),
            (
                "### Project Standards Review\n\n- Result: not-evaluated",
                "### Project Standards Review\n\n- Result: pass",
            ),
            (
                "## Project Functional Acceptance\n\n- Result: not-evaluated",
                "## Project Functional Acceptance\n\n- Result: pass",
            ),
            (
                "## Project Engineering Acceptance\n\n- Result: not-evaluated",
                "## Project Engineering Acceptance\n\n- Result: pass",
            ),
            (
                "## Project Delivery Acceptance\n\n- Result: not-evaluated",
                "## Project Delivery Acceptance\n\n- Result: pass",
            ),
            ("- Final Checkpoint: none", "- Final Checkpoint: CHECKPOINT-001"),
            ("- Checkpoint status: none", "- Checkpoint status: ready"),
            ("- Recovery readiness: no", "- Recovery readiness: yes"),
            (
                "- Terminal Resume Point or reopen condition: none",
                "- Terminal Resume Point or reopen condition: PROJECT-CLOSED",
            ),
            ("- Report: none", "- Report: FINAL-REPORT-001"),
            ("- Report status: inactive", "- Report status: ready"),
            ("- Decision: none", "- Decision: accept"),
            ("- Decision by: none", "- Decision by: supervisor"),
            ("- Decision evidence: none", "- Decision evidence: acceptance record"),
            ("- Requested Project status: none", "- Requested Project status: closed"),
            ("- Integrator update required: no", "- Integrator update required: yes"),
            ("- Update evidence: none", "- Update evidence: pending PROJECT.md update"),
        )
        for old, new in replacements:
            if old not in text:
                raise AssertionError(f"fixture text not found in {path}: {old!r}")
            text = text.replace(old, new, 1)
        if with_risks:
            text = text.replace(
                "## Accepted Risks\n\n- None.",
                "## Accepted Risks\n\n- Minor documentation lag accepted by the Supervisor.",
                1,
            )
        path.write_text(text, encoding="utf-8")

    def mark_release_ready(self, fixture: Path, with_risks: bool = False) -> None:
        path = fixture / READINESS
        replacements = (
            ("- Readiness ID: none", "- Readiness ID: READINESS-001"),
            ("- Project ID: none", "- Project ID: PROJECT-001"),
            (
                "- Readiness Status: inactive",
                f"- Readiness Status: {'ready-with-accepted-risks' if with_risks else 'ready'}",
            ),
            ("- Delivery mode: none", "- Delivery mode: release-required"),
            ("- Release scope: none", "- Release scope: package artifacts"),
            ("- Candidate boundary: none", "- Candidate boundary: 0123456789abcdef"),
            ("- Code rollback: none", "- Code rollback: restore the previous package"),
            ("- Health checks: none", "- Health checks: observed staging health check"),
            ("- Security Review: none", "- Security Review: pass"),
            ("- Release result: not-executed", "- Release result: not-executed-not-authorized"),
            ("- Decision: none", "- Decision: ready"),
            ("- Decision by: none", "- Decision by: supervisor"),
            ("- Evidence: none", "- Evidence: build and review records"),
        )
        for old, new in replacements:
            self.replace_once(path, old, new)
        if with_risks:
            self.replace_once(
                path,
                "## Accepted Risks\n\n- None.",
                "## Accepted Risks\n\n- Minor changelog formatting risk accepted.",
            )
            self.replace_once(
                path,
                "- Risk acceptance authority: none",
                "- Risk acceptance authority: supervisor decision",
            )

    def mark_report_ready(self, fixture: Path, issued: bool = False) -> None:
        path = fixture / REPORT
        replacements = (
            ("- Report ID: none", "- Report ID: FINAL-REPORT-001"),
            ("- Project ID: none", "- Project ID: PROJECT-001"),
            ("- Prepared: none", "- Prepared: 2026-07-18"),
            ("- Prepared by: none", "- Prepared by: integrator"),
            ("- Report Status: inactive", f"- Report Status: {'issued' if issued else 'ready'}"),
            ("- Intended recipient: none", "- Intended recipient: maintenance team"),
            ("- Delivery boundary: none", "- Delivery boundary: 0123456789abcdef"),
            ("- Acceptance: none", "- Acceptance: ACCEPTANCE-001"),
            ("- Project Acceptance: none", "- Project Acceptance: accepted"),
        )
        for old, new in replacements:
            self.replace_once(path, old, new)
        if issued:
            self.replace_once(
                path,
                "- Delivery evidence: none",
                "- Delivery evidence: observed repository handoff acknowledgement",
            )

    def mark_project_review(self, fixture: Path, reviewer_type: str = "spec") -> None:
        path = fixture / REVIEW
        replacements = (
            ("- Review ID: none", "- Review ID: REVIEW-201"),
            ("- Review Level: none", "- Review Level: project"),
            ("- Project ID: none", "- Project ID: PROJECT-001"),
            ("- Loop ID: none", "- Loop ID: not-applicable"),
            ("- Reviewer: none", "- Reviewer: independent reviewer"),
            ("- Reviewer Type: none", f"- Reviewer Type: {reviewer_type}"),
            (
                "- Reviewed Cross-Loop Validation: none",
                "- Reviewed Cross-Loop Validation: VALIDATION-001",
            ),
            ("- Reviewed Goal Mapping: none", "- Reviewed Goal Mapping: ACCEPTANCE-001"),
            ("- Reviewed Boundary: none", "- Reviewed Boundary: 0123456789abcdef"),
            ("- Status: inactive", "- Status: completed"),
            ("- Verdict: none", "- Verdict: pass"),
        )
        for old, new in replacements:
            self.replace_once(path, old, new)

    def test_001_valid_phase_five_template_collection_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_002_valid_cross_loop_passed_instance(self) -> None:
        result = self.validate_fixture(self.mark_cross_loop_passed)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_003_valid_cross_loop_passed_with_limitations_instance(self) -> None:
        result = self.validate_fixture(lambda fixture: self.mark_cross_loop_passed(fixture, True))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_004_valid_project_acceptance_instance(self) -> None:
        result = self.validate_fixture(self.mark_acceptance_accepted)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_005_valid_project_acceptance_with_risks_instance(self) -> None:
        result = self.validate_fixture(lambda fixture: self.mark_acceptance_accepted(fixture, True))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_006_valid_release_ready_without_execution_instance(self) -> None:
        result = self.validate_fixture(self.mark_release_ready)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_007_valid_release_ready_with_risks_instance(self) -> None:
        result = self.validate_fixture(lambda fixture: self.mark_release_ready(fixture, True))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_008_valid_delivery_only_not_applicable_release(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace_once(fixture / READINESS, "- Readiness Status: inactive", "- Readiness Status: not-applicable")
            self.replace_once(fixture / READINESS, "- Delivery mode: none", "- Delivery mode: delivery-only")

        result = self.validate_fixture(mutate)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_009_valid_ready_final_delivery_report(self) -> None:
        result = self.validate_fixture(self.mark_report_ready)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_010_valid_issued_final_delivery_report(self) -> None:
        result = self.validate_fixture(lambda fixture: self.mark_report_ready(fixture, True))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_011_valid_project_spec_review(self) -> None:
        result = self.validate_fixture(self.mark_project_review)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_012_valid_project_standards_review(self) -> None:
        result = self.validate_fixture(lambda fixture: self.mark_project_review(fixture, "standards"))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


def _apply_setup(test: ProjectClosureFinalDeliveryTests, fixture: Path, setup: str | None) -> None:
    if setup == "cross":
        test.mark_cross_loop_passed(fixture)
    elif setup == "cross-limitations":
        test.mark_cross_loop_passed(fixture, True)
    elif setup == "acceptance":
        test.mark_acceptance_accepted(fixture)
    elif setup == "acceptance-risks":
        test.mark_acceptance_accepted(fixture, True)
    elif setup == "acceptance-blocked":
        test.replace_once(fixture / ACCEPTANCE, "- Acceptance Status: inactive", "- Acceptance Status: blocked")
        test.replace_once(fixture / ACCEPTANCE, "- Delivery mode: none", "- Delivery mode: delivery-only")
    elif setup == "review":
        test.mark_project_review(fixture)
    elif setup == "review-specialist":
        test.mark_project_review(fixture, "security")
    elif setup == "loop-review":
        path = fixture / REVIEW
        for old, new in (
            ("- Review ID: none", "- Review ID: REVIEW-201"),
            ("- Review Level: none", "- Review Level: loop"),
            ("- Loop ID: none", "- Loop ID: LOOP-001"),
            ("- Reviewer: none", "- Reviewer: independent reviewer"),
            ("- Reviewer Type: none", "- Reviewer Type: spec"),
            ("- Status: inactive", "- Status: completed"),
            ("- Verdict: none", "- Verdict: pass"),
        ):
            test.replace_once(path, old, new)
    elif setup == "readiness":
        test.mark_release_ready(fixture)
    elif setup == "readiness-risks":
        test.mark_release_ready(fixture, True)
    elif setup == "readiness-na":
        test.replace_once(fixture / READINESS, "- Readiness Status: inactive", "- Readiness Status: not-applicable")
        test.replace_once(fixture / READINESS, "- Delivery mode: none", "- Delivery mode: delivery-only")
    elif setup == "report":
        test.mark_report_ready(fixture)
    elif setup == "report-issued":
        test.mark_report_ready(fixture, True)


def _missing_test(relative: Path):
    def test(self: ProjectClosureFinalDeliveryTests) -> None:
        def mutate(fixture: Path) -> None:
            (fixture / relative).unlink()

        self.assert_rejected(mutate, f"missing required file: {relative.as_posix()}")

    return test


def _rejection_test(case):
    _name, setup, relative, old, new, message = case

    def test(self: ProjectClosureFinalDeliveryTests) -> None:
        def mutate(fixture: Path) -> None:
            _apply_setup(self, fixture, setup)
            path = fixture / relative
            if old is None:
                self.append(path, new)
            else:
                self.replace_once(path, old, new)

        self.assert_rejected(mutate, message)

    return test


_case_number = 13
for _name, _relative in MISSING_CASES:
    setattr(
        ProjectClosureFinalDeliveryTests,
        f"test_{_case_number:03d}_{_name}",
        _missing_test(_relative),
    )
    _case_number += 1

for _case in REJECTION_CASES:
    setattr(
        ProjectClosureFinalDeliveryTests,
        f"test_{_case_number:03d}_{_case[0]}",
        _rejection_test(_case),
    )
    _case_number += 1


if __name__ == "__main__":
    unittest.main()
