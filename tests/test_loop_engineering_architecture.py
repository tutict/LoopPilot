import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate.py"
PROJECT_TEMPLATE = ".looppilot/PROJECT-TEMPLATE.md"
MODE_DOCUMENT = "docs/protocol-modes-and-state-sources.md"


class LoopEngineeringArchitectureTests(unittest.TestCase):
    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--root", str(root)],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def copy_repository(self, directory: str) -> Path:
        fixture = Path(directory) / "repository"
        copytree(
            REPOSITORY_ROOT,
            fixture,
            ignore=lambda _path, names: [
                name for name in names if name in {".git", "__pycache__"}
            ],
        )
        return fixture

    def validate_fixture(self, mutator=None) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            if mutator is not None:
                mutator(fixture)
            return self.run_validator(fixture)

    @staticmethod
    def remove_once(path: Path, value: str) -> None:
        text = path.read_text(encoding="utf-8")
        if value not in text:
            raise AssertionError(f"fixture text not found in {path}: {value!r}")
        path.write_text(text.replace(value, "", 1), encoding="utf-8")

    def assert_missing_heading_rejected(self, heading: str) -> None:
        def mutate(fixture: Path) -> None:
            self.remove_once(fixture / PROJECT_TEMPLATE, heading)

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn(f"missing required heading {heading!r}", result.stdout)

    def test_01_project_template_exists(self) -> None:
        def check(fixture: Path) -> None:
            self.assertTrue((fixture / PROJECT_TEMPLATE).is_file())

        result = self.validate_fixture(check)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_02_missing_problem_is_rejected(self) -> None:
        self.assert_missing_heading_rejected("## Problem")

    def test_03_missing_users_and_actors_is_rejected(self) -> None:
        self.assert_missing_heading_rejected("## Users and Actors")

    def test_04_missing_domain_model_is_rejected(self) -> None:
        self.assert_missing_heading_rejected("## Domain Model")

    def test_05_missing_data_is_rejected(self) -> None:
        self.assert_missing_heading_rejected("## Data")

    def test_06_missing_concurrency_is_rejected(self) -> None:
        self.assert_missing_heading_rejected("## Concurrency")

    def test_07_missing_identity_and_permissions_is_rejected(self) -> None:
        self.assert_missing_heading_rejected("## Identity and Permissions")

    def test_08_missing_security_is_rejected(self) -> None:
        self.assert_missing_heading_rejected("## Security")

    def test_09_missing_observability_is_rejected(self) -> None:
        self.assert_missing_heading_rejected("## Observability")

    def test_10_missing_delivery_and_operations_is_rejected(self) -> None:
        self.assert_missing_heading_rejected("## Delivery and Operations")

    def test_11_missing_evolution_is_rejected(self) -> None:
        self.assert_missing_heading_rejected("## Evolution")

    def test_12_missing_team_boundaries_is_rejected(self) -> None:
        self.assert_missing_heading_rejected("## Team Boundaries")

    def test_13_missing_architecture_profile_is_rejected(self) -> None:
        self.assert_missing_heading_rejected("## Architecture Profile")

    def test_14_missing_engineering_concern_matrix_is_rejected(self) -> None:
        self.assert_missing_heading_rejected("## Engineering Concern Matrix")

    def test_15_valid_empty_template_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_16_active_project_template_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            path = fixture / PROJECT_TEMPLATE
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace("Status: inactive", "Status: active", 1),
                encoding="utf-8",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("must remain Status: inactive", result.stdout)

    def test_17_missing_lightweight_mode_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.remove_once(fixture / MODE_DOCUMENT, "## Lightweight Mode")

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("missing required heading '## Lightweight Mode'", result.stdout)

    def test_18_missing_full_loop_mode_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.remove_once(fixture / MODE_DOCUMENT, "## Full Loop Mode")

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("missing required heading '## Full Loop Mode'", result.stdout)

    def test_19_missing_task_state_source_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.remove_once(
                fixture / MODE_DOCUMENT,
                "| Task status | Current Loop TASK-LEDGER.md |",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("missing single source of truth for Task status", result.stdout)

    def test_20_real_host_validation_claim_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            path = fixture / "docs/loop-engineering-model.md"
            path.write_text(
                path.read_text(encoding="utf-8")
                + chr(10)
                + "Full Loop Mode is validated on Codex."
                + chr(10),
                encoding="utf-8",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn(
            "must not claim Full Loop Mode real-host validation", result.stdout
        )


    def test_21_host_works_claim_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            path = fixture / "docs/loop-engineering-model.md"
            path.write_text(
                path.read_text(encoding="utf-8")
                + chr(10)
                + "Full Loop Mode works on Codex."
                + chr(10),
                encoding="utf-8",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn(
            "must not claim Full Loop Mode real-host validation", result.stdout
        )

    def test_22_host_support_claim_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            path = fixture / "docs/loop-engineering-model.md"
            path.write_text(
                path.read_text(encoding="utf-8")
                + chr(10)
                + "Full Loop Mode supports Gemini CLI."
                + chr(10),
                encoding="utf-8",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn(
            "must not claim Full Loop Mode real-host validation", result.stdout
        )
if __name__ == "__main__":
    unittest.main()
