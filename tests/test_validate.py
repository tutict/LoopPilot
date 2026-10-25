import subprocess
import sys
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate.py"


class ValidateRepositoryTests(unittest.TestCase):
    def test_temporary_markdown_is_outside_validation_boundary(self) -> None:
        temporary_file = REPOSITORY_ROOT / ".tmp" / "validator-ignore.md"
        temporary_file.write_text(
            "[broken](missing.md)\n",
            encoding="utf-8",
        )
        try:
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), "--root", str(REPOSITORY_ROOT)],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        finally:
            temporary_file.unlink()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Static validation passed", result.stdout)

    def test_current_repository_passes_static_validation(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--root", str(REPOSITORY_ROOT)],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Static validation passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
