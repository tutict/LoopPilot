import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate.py"


class WhitespaceValidationTests(unittest.TestCase):
    def test_trailing_whitespace_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "repository"
            copytree(
                REPOSITORY_ROOT,
                fixture,
                ignore=lambda _path, names: [
                    name for name in names if name in {".git", "__pycache__"}
                ],
            )
            readme = fixture / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8") + "trailing space  \n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(VALIDATOR), "--root", str(fixture)],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(1, result.returncode)
        self.assertIn("trailing whitespace", result.stdout)


if __name__ == "__main__":
    unittest.main()
