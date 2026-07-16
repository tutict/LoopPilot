import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate.py"


class ValidationFailureTests(unittest.TestCase):
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

    def test_duplicate_yaml_key_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            openai_yaml = fixture / "agents" / "openai.yaml"
            openai_yaml.write_text(
                openai_yaml.read_text(encoding="utf-8")
                + "\ninterface:\n  display_name: duplicate\n",
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("duplicate key 'interface'", result.stdout)


if __name__ == "__main__":
    unittest.main()
