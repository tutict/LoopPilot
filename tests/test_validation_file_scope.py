"""Repository validation excludes generated trees but keeps live YAML checks."""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("file_scope_validate", ROOT / "scripts/validate.py")
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)


class ValidationFileScopeTests(unittest.TestCase):
    def write(self, root, relative, text):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_generated_yaml_is_outside_repository_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for ignored in (".git", ".tmp", ".venv", "node_modules", "__pycache__"):
                self.write(root, f"{ignored}/invalid.yaml", "key: [\n")
                self.write(root, f"docs/{ignored}/duplicate.yml", "key: 1\nkey: 2\n")
            errors = []
            validator.validate_yaml_files(root, errors)
        self.assertEqual([], errors)

    def test_live_hidden_yaml_and_duplicate_keys_remain_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in (".github/workflows/test.yml", ".looppilot/data.yaml", "agents/openai.yaml"):
                self.write(root, relative, "key: 1\nkey: 2\n")
            errors = []
            validator.validate_yaml_files(root, errors)
        self.assertEqual(3, len(errors), errors)
        self.assertTrue(all("duplicate key 'key'" in error for error in errors), errors)
        for relative in (".github/workflows/test.yml", ".looppilot/data.yaml", "agents/openai.yaml"):
            self.assertTrue(any(relative in error for error in errors), errors)

    def test_markdown_uses_the_same_generated_directory_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for ignored in (".git", ".tmp", ".venv", "node_modules", "__pycache__"):
                self.write(root, f"{ignored}/invalid.md", "[broken](missing.md)\n")
                self.write(root, f"docs/{ignored}/invalid.md", "[broken](missing.md)\n")
            live = {".github/guide.md", ".looppilot/notes.md", "docs/.tmp.md", "docs/guide.md"}
            for relative in live:
                self.write(root, relative, "# Live document\n")
            discovered = {path.relative_to(root).as_posix() for path in validator.markdown_files(root)}
        self.assertEqual(live, discovered)

    def test_uppercase_extensions_preserve_native_platform_matching(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write(root, ".github/workflows/live.YML", "key: 1\nkey: 2\n")
            self.write(root, "docs/GUIDE.MD", "# Live document\n")
            errors = []
            validator.validate_yaml_files(root, errors)
            discovered = {path.relative_to(root).as_posix() for path in validator.markdown_files(root)}
        if os.name == "nt":
            self.assertEqual(1, len(errors), errors)
            self.assertIn(".github/workflows/live.YML", errors[0])
            self.assertEqual({"docs/GUIDE.MD"}, discovered)
        else:
            self.assertEqual([], errors)
            self.assertEqual(set(), discovered)

    def test_public_cli_ignores_temporary_yaml_and_still_rejects_live_yaml(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "repository"
            shutil.copytree(
                ROOT,
                fixture,
                ignore=shutil.ignore_patterns(
                    ".git", ".tmp", ".venv", "node_modules", "__pycache__",
                    "verification-temp", ".four-axis-test-tmp",
                ),
            )
            self.write(fixture, ".tmp/probe/invalid.yaml", "key: [\n")
            self.write(fixture, "node_modules/probe/duplicate.yml", "key: 1\nkey: 2\n")
            command = [sys.executable, str(ROOT / "scripts/validate.py"), "--root", str(fixture)]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Static validation passed", result.stdout)

            self.write(fixture, ".github/workflows/live-probe.yml", "key: 1\nkey: 2\n")
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("duplicate key 'key'", result.stdout)
            self.assertIn("live-probe.yml", result.stdout)


if __name__ == "__main__":
    unittest.main()
