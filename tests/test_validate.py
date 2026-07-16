import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate.py"


class ValidateRepositoryTests(unittest.TestCase):
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
