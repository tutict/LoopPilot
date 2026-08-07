from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = ROOT / ".tmp" / "distribution-tests"
POWERSHELL = shutil.which("powershell.exe") or shutil.which("pwsh")


class DistributionLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.work = WORK_ROOT / uuid.uuid4().hex
        self.work.mkdir(parents=True)
        self.addCleanup(self._cleanup_work)

    def _cleanup_work(self) -> None:
        shutil.rmtree(self.work, ignore_errors=True)

    def _make_source(
        self,
        name: str,
        version: str,
        commit_character: str,
        files: dict[str, str],
        manifest: list[str],
    ) -> Path:
        source = self.work / name
        distribution = source / "distribution"
        distribution.mkdir(parents=True)
        shutil.copy2(ROOT / "distribution" / "loop-pilot.ps1", distribution)
        shutil.copy2(ROOT / "distribution" / "loop-pilot.sh", distribution)
        (distribution / "version.txt").write_text(version + "\n", encoding="ascii")
        (distribution / "commit.txt").write_text(
            commit_character * 40 + "\n", encoding="ascii"
        )
        (distribution / "managed-files.txt").write_text(
            "\n".join(manifest) + "\n", encoding="ascii"
        )
        for relative, content in files.items():
            path = source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="ascii")
        return source

    def _run(
        self,
        source: Path,
        operation: str,
        destination: Path,
        *,
        force: bool = False,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        if POWERSHELL is None:
            self.skipTest("PowerShell is unavailable")
        command = [
            POWERSHELL,
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(source / "distribution" / "loop-pilot.ps1"),
            "-Operation",
            operation,
            "-Destination",
            str(destination),
        ]
        if force:
            command.append("-Force")
        environment = os.environ.copy()
        environment["GIT_CEILING_DIRECTORIES"] = str(ROOT)
        return subprocess.run(
            command,
            check=check,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=environment,
        )

    def _sources(self) -> tuple[Path, Path]:
        source_v1 = self._make_source(
            "source-v1",
            "1.0.0-test1",
            "1",
            {
                "SKILL.md": "skill v1\n",
                "docs/keep.md": "keep v1\n",
                "docs/retired.md": "retired v1\n",
                "docs/retired-user.md": "retired user baseline\n",
            },
            ["SKILL.md", "docs/"],
        )
        source_v2 = self._make_source(
            "source-v2",
            "1.0.0-test2",
            "2",
            {
                "SKILL.md": "skill v2\n",
                "README.md": "readme v2\n",
                "docs/keep.md": "keep v2\n",
                "docs/new.md": "new v2\n",
            },
            ["SKILL.md", "README.md", "docs/"],
        )
        return source_v1, source_v2

    def test_official_manifest_includes_validator_workflow(self) -> None:
        manifest = (ROOT / "distribution" / "managed-files.txt").read_text(
            encoding="utf-8"
        )
        entries = {
            line.strip()
            for line in manifest.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }

        workflow = ".github/workflows/validate.yml"
        self.assertIn(workflow, entries)
        self.assertTrue((ROOT / workflow).is_file())

    def test_fresh_reinstall_upgrade_and_uninstall_preserve_user_content(self) -> None:
        source_v1, source_v2 = self._sources()
        destination = self.work / "installed"

        fresh = self._run(source_v1, "install", destination)
        self.assertIn("Installed version: 1.0.0-test1", fresh.stdout)
        self.assertIn("Installed commit: " + "1" * 40, fresh.stdout)
        self.assertTrue((destination / ".looppilot-installation").is_file())
        self.assertEqual("keep v1\n", (destination / "docs" / "keep.md").read_text())

        user_file = destination / "user-notes.md"
        user_file.write_text("user owned\n", encoding="ascii")
        colliding_file = destination / "README.md"
        colliding_file.write_text("preexisting readme\n", encoding="ascii")
        reinstall = self._run(source_v1, "install", destination)
        self.assertIn("reinstall (no changes)", reinstall.stdout)
        self.assertEqual("user owned\n", user_file.read_text())

        (destination / "SKILL.md").write_text("local customization\n", encoding="ascii")
        retired_user = destination / "docs" / "retired-user.md"
        retired_user.write_text("retired local customization\n", encoding="ascii")
        upgraded = self._run(source_v2, "update", destination)
        self.assertIn("Installed version: 1.0.0-test2", upgraded.stdout)
        self.assertEqual("local customization\n", (destination / "SKILL.md").read_text())
        self.assertEqual("keep v2\n", (destination / "docs" / "keep.md").read_text())
        self.assertFalse((destination / "docs" / "retired.md").exists())
        self.assertEqual("new v2\n", (destination / "docs" / "new.md").read_text())
        self.assertEqual("preexisting readme\n", colliding_file.read_text())
        self.assertEqual("retired local customization\n", retired_user.read_text())
        state = (destination / ".looppilot-installation").read_text(encoding="ascii")
        self.assertIn("VERSION|1.0.0-test2", state)
        self.assertIn("COMMIT|" + "2" * 40, state)
        self.assertRegex(state, r"FILE\|SKILL\.md\|[0-9a-f]{64}\|1")
        self.assertRegex(state, r"FILE\|README\.md\|[0-9a-f]{64}\|1")
        self.assertNotIn("FILE|docs/retired-user.md|", state)
        self.assertTrue(any((destination / ".looppilot-backups").rglob("keep.md")))
        self.assertTrue(any((destination / ".looppilot-backups").rglob("retired.md")))

        removed = self._run(source_v2, "uninstall", destination)
        self.assertIn("Removed files from version: 1.0.0-test2", removed.stdout)
        self.assertEqual("local customization\n", (destination / "SKILL.md").read_text())
        self.assertEqual("user owned\n", user_file.read_text())
        self.assertEqual("preexisting readme\n", colliding_file.read_text())
        self.assertEqual("retired local customization\n", retired_user.read_text())
        self.assertFalse((destination / "docs" / "new.md").exists())
        self.assertFalse((destination / ".looppilot-installation").exists())
        self.assertTrue((destination / ".looppilot-backups").is_dir())

    def test_conflict_preflight_is_atomic_and_force_creates_backup(self) -> None:
        source_v1, _ = self._sources()
        destination = self.work / "installed"
        conflict = destination / "docs" / "retired.md"
        conflict.parent.mkdir(parents=True)
        conflict.write_text("preexisting\n", encoding="ascii")

        rejected = self._run(source_v1, "install", destination, check=False)
        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("no files were copied or overwritten", rejected.stderr)
        self.assertFalse((destination / "SKILL.md").exists())
        self.assertEqual("preexisting\n", conflict.read_text())

        self._run(source_v1, "install", destination, force=True)
        self.assertEqual("retired v1\n", conflict.read_text())
        backups = list((destination / ".looppilot-backups").rglob("retired.md"))
        self.assertEqual(1, len(backups))
        self.assertEqual("preexisting\n", backups[0].read_text())

    def test_missing_file_is_detected_and_update_repairs_it(self) -> None:
        source_v1, source_v2 = self._sources()
        destination = self.work / "installed"
        self._run(source_v1, "install", destination)
        missing = destination / "docs" / "keep.md"
        missing.unlink()

        rejected = self._run(source_v1, "install", destination, check=False)
        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("use update.ps1", rejected.stderr)
        self._run(source_v1, "update", destination)
        self.assertEqual("keep v1\n", missing.read_text())

    def test_generated_state_path_type_is_rejected_before_copy(self) -> None:
        source_v1, _ = self._sources()
        destination = self.work / "installed"
        (destination / ".looppilot-installation").mkdir(parents=True)

        rejected = self._run(source_v1, "install", destination, check=False)
        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("state path must be a regular file", rejected.stderr)
        self.assertFalse((destination / "SKILL.md").exists())

    def test_force_update_backs_up_and_replaces_customized_file(self) -> None:
        source_v1, source_v2 = self._sources()
        destination = self.work / "installed"
        self._run(source_v1, "install", destination)
        skill = destination / "SKILL.md"
        skill.write_text("local customization\n", encoding="ascii")

        self._run(source_v2, "update", destination)
        self.assertEqual("local customization\n", skill.read_text())
        self._run(source_v2, "update", destination, force=True)
        self.assertEqual("skill v2\n", skill.read_text())
        state = (destination / ".looppilot-installation").read_text(encoding="ascii")
        self.assertRegex(state, r"FILE\|SKILL\.md\|[0-9a-f]{64}\|0")
        backups = list((destination / ".looppilot-backups").rglob("SKILL.md"))
        self.assertGreaterEqual(len(backups), 2)
        self.assertTrue(
            all(path.read_text() == "local customization\n" for path in backups)
        )

    def test_missing_source_and_invalid_version_state_are_rejected(self) -> None:
        source_v1, source_v2 = self._sources()
        destination = self.work / "installed"
        (source_v1 / "SKILL.md").unlink()
        rejected_source = self._run(source_v1, "install", destination, check=False)
        self.assertNotEqual(0, rejected_source.returncode)
        self.assertIn("manifest file is missing", rejected_source.stderr)
        self.assertFalse(destination.exists())

        self._run(source_v2, "install", destination)
        state_path = destination / ".looppilot-installation"
        state = state_path.read_text(encoding="ascii")
        state_path.write_text(
            state.replace("VERSION|1.0.0-test2", "VERSION|invalid version"),
            encoding="ascii",
        )
        rejected_state = self._run(source_v2, "update", destination, check=False)
        self.assertNotEqual(0, rejected_state.returncode)
        self.assertIn("incompatible or incomplete", rejected_state.stderr)


if __name__ == "__main__":
    unittest.main()
