import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate.py"


class SharedStateValidationTests(unittest.TestCase):
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

    def test_missing_agents_instructions_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            agents = fixture / "AGENTS.md"
            if agents.exists():
                agents.unlink()

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("missing required file: AGENTS.md", result.stdout)

    def test_missing_handoff_template_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            handoff = fixture / ".looppilot" / "HANDOFF.md"
            if handoff.exists():
                handoff.unlink()

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "missing required file: .looppilot/HANDOFF.md",
            result.stdout,
        )

    def test_invalid_state_status_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            state = fixture / ".looppilot" / "STATE.md"
            state.write_text(
                state.read_text(encoding="utf-8").replace(
                    "Status: inactive", "Status: paused", 1
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("STATE.md: invalid Status 'paused'", result.stdout)

    def test_invalid_handoff_status_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            handoff = fixture / ".looppilot" / "HANDOFF.md"
            handoff.write_text(
                handoff.read_text(encoding="utf-8").replace(
                    "Status: none", "Status: paused", 1
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("HANDOFF.md: invalid Status 'paused'", result.stdout)

    def test_placeholder_template_cannot_claim_an_active_task(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            state = fixture / ".looppilot" / "STATE.md"
            state.write_text(
                state.read_text(encoding="utf-8").replace(
                    "Status: inactive", "Status: active", 1
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "STATE.md: template placeholders cannot declare Status 'active'",
            result.stdout,
        )

    def test_missing_shared_state_heading_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            state = fixture / ".looppilot" / "STATE.md"
            state.write_text(
                state.read_text(encoding="utf-8").replace(
                    "## Verified Evidence\n\n- None.\n\n", "", 1
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "STATE.md: missing required heading '## Verified Evidence'",
            result.stdout,
        )

    def test_inactive_empty_templates_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)

            result = self.run_validator(fixture)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_active_shared_state_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            state = fixture / ".looppilot" / "STATE.md"
            text = state.read_text(encoding="utf-8")
            text = text.replace("Status: inactive", "Status: active", 1)
            text = text.replace("Updated: YYYY-MM-DD", "Updated: 2026-07-16", 1)
            text = text.replace("Updated by: none", "Updated by: test-agent", 1)
            text = text.replace(
                "No active shared task.", "Validate a real shared task.", 1
            )
            state.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_shared_state_relative_links_are_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            handoff = fixture / ".looppilot" / "HANDOFF.md"
            handoff.write_text(
                handoff.read_text(encoding="utf-8")
                + "\n[Shared-state protocol](README.md)\n",
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_obvious_secret_assignment_in_shared_state_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            state = fixture / ".looppilot" / "STATE.md"
            state.write_text(
                state.read_text(encoding="utf-8")
                + "\nOPENAI_API_KEY=live-looking-value\n",
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "STATE.md: possible credential assignment in shared state",
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
