from __future__ import annotations

import os
import hashlib
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import unittest
from urllib.parse import unquote, urlsplit
import uuid


ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = ROOT / ".tmp" / "distribution-tests"
POWERSHELL = shutil.which("powershell.exe") or shutil.which("pwsh")
GIT = shutil.which("git")
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")

# Trees the official payload deliberately stops distributing, so that a Skill
# installed from a clean checkout carries no acceptance corpus.
ACCEPTANCE_PREFIXES = (
    "evaluations/",
    "tests/",
    "scripts/",
    "docs/release/",
    "docs/evaluations/",
)
ACCEPTANCE_FILES = ("docs/cross-host-acceptance.md",)


def _find_bash() -> str | None:
    """Locate a Bash that can run the POSIX installer.

    On Windows the first ``bash`` on PATH is usually the WSL shim in
    ``System32``, which neither shares this filesystem's path convention nor is
    guaranteed to have a distribution installed. Git for Windows is preferred
    and the shim is skipped.
    """
    if os.name != "nt":
        return shutil.which("bash")
    git = shutil.which("git")
    candidates = []
    if git is not None:
        candidates.append(Path(git).resolve().parents[1] / "bin" / "bash.exe")
    candidates.append(Path(r"C:\Program Files\Git\bin\bash.exe"))
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    found = shutil.which("bash")
    if found is None:
        return None
    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    if Path(found).resolve().is_relative_to(Path(system_root).resolve()):
        return None
    return found


BASH = _find_bash()


def _posix_path(path: Path) -> str:
    """Translate a path for the Bash implementation on this platform.

    Git Bash and MSYS accept ``/c/dir/file`` for ``C:\\dir\\file``. The
    translation is done here rather than through ``cygpath`` because that helper
    lives outside the Windows PATH in a standard Git for Windows install.
    """
    if os.name != "nt":
        return str(path)
    resolved = Path(path).resolve()
    drive = resolved.drive.rstrip(":")
    if not drive:
        return resolved.as_posix()
    remainder = resolved.as_posix()[len(resolved.drive) :].lstrip("/")
    return f"/{drive.lower()}/{remainder}"


def _official_manifest_entries() -> list[str]:
    """Read the non-comment entries of the official manifest, in file order."""
    manifest = (ROOT / "distribution" / "managed-files.txt").read_text(encoding="utf-8")
    return [
        line.strip()
        for line in manifest.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _expand_official_manifest() -> set[str]:
    """Expand the official manifest the way both installers do.

    Literal entries stand for themselves and a trailing slash expands to the
    tracked files beneath that directory, falling back to a filesystem walk when
    Git is unavailable.
    """
    expanded: set[str] = set()
    for entry in _official_manifest_entries():
        if not entry.endswith("/"):
            expanded.add(entry)
            continue
        directory = ROOT / entry.rstrip("/")
        if GIT is not None:
            listing = subprocess.run(
                [GIT, "-C", str(ROOT), "ls-files", "--", entry],
                capture_output=True,
                text=True,
                check=True,
            )
            expanded.update(line for line in listing.stdout.splitlines() if line)
        else:
            expanded.update(
                path.relative_to(ROOT).as_posix()
                for path in directory.rglob("*")
                if path.is_file()
            )
    return expanded


def _relative_markdown_links(document: str) -> list[str]:
    """Return repository-relative targets of the relative links in a document."""
    text = (ROOT / document).read_text(encoding="utf-8")
    base = posixpath.dirname(document)
    targets: set[str] = set()
    for match in LINK_PATTERN.finditer(text):
        raw_target = match.group(1).strip()
        if raw_target.startswith("<") and raw_target.endswith(">"):
            raw_target = raw_target[1:-1]
        target = raw_target.split(maxsplit=1)[0]
        parsed = urlsplit(target)
        if parsed.scheme or target.startswith(("#", "//")):
            continue
        link = unquote(parsed.path)
        if not link:
            continue
        targets.add(posixpath.normpath(posixpath.join(base, link)))
    return sorted(targets)


class DistributionFixture(unittest.TestCase):
    """Isolated source-package fixtures shared by the distribution suites."""

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
        shell: str = "powershell",
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["GIT_CEILING_DIRECTORIES"] = str(ROOT)
        if shell == "powershell":
            if POWERSHELL is None:
                self.skipTest("PowerShell is unavailable")
            powershell_parameters = {"Operation": operation, "Destination": str(destination)}
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
                powershell_parameters["Force"] = True
        elif shell == "bash":
            if BASH is None:
                self.skipTest("Bash is unavailable")
            command = [
                BASH,
                _posix_path(source / "distribution" / "loop-pilot.sh"),
                operation,
                "--destination",
                _posix_path(destination),
            ]
            if force:
                command.append("--force")
        else:  # pragma: no cover - guards a programming error in the suite
            raise ValueError(f"unknown shell {shell!r}")
        # These pre-existing fixtures model explicit archives, not implicit
        # Git-identity fallback. Assertions and lifecycle expectations are unchanged.
        if not (source / ".git").exists() and operation != "uninstall":
            entries = set()
            for line in (source / "distribution/managed-files.txt").read_text().splitlines():
                entry = line.strip()
                if not entry or entry.startswith("#"):
                    continue
                if entry.endswith("/"):
                    entries.update(p.relative_to(source).as_posix() for p in (source / entry).rglob("*") if p.is_file())
                else:
                    entries.add(entry)
            # Invalid-path fixtures deliberately reach installer preflight rather
            # than failing while the test supplies its explicit archive identity.
            rows = []
            for entry in sorted(entries):
                path = source / entry
                if path.is_file():
                    rows.append(f"{entry}|{hashlib.sha256(path.read_bytes()).hexdigest()}\n")
            digest = hashlib.sha256("".join(rows).encode("utf-8")).hexdigest()
            command.extend(["-SourceMode", "archive", "-ArchiveSha256", digest] if shell == "powershell"
                           else ["--source-mode", "archive", "--archive-sha256", digest])
            if shell == "powershell":
                powershell_parameters.update(SourceMode="archive", ArchiveSha256=digest)
        if shell == "powershell":
            # Keep diagnostics machine-readable instead of depending on the
            # host's ANSI formatting and terminal-width wrapping. Exit codes,
            # installer arguments and every behavioral assertion stay intact.
            harness = self.work / "invoke-powershell.ps1"
            rows = []
            for name, value in powershell_parameters.items():
                literal = "$true" if value is True else "'" + value.replace("'", "''") + "'"
                rows.append(f"    {name} = {literal}\n")
            script = str(source / "distribution" / "loop-pilot.ps1").replace("'", "''")
            harness.write_text(
                "$ErrorActionPreference = 'Stop'\n$ErrorView = 'NormalView'\n"
                + "$parameters = @{\n" + "".join(rows) + "}\n"
                + f"& '{script}' @parameters\n", encoding="utf-8",
            )
            command = command[:6] + [str(harness)]
        return subprocess.run(
            command,
            check=check,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=environment,
        )


class DistributionLifecycleTests(DistributionFixture):

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
        entries = set(_official_manifest_entries())

        workflow = ".github/workflows/validate.yml"
        self.assertIn(workflow, entries)
        self.assertTrue((ROOT / workflow).is_file())

    def test_official_manifest_excludes_acceptance_corpus(self) -> None:
        """The installed payload must not carry the acceptance corpus.

        A Skill installed from a clean checkout is the second source a fixture
        could read the rubric, the scenarios, the verdict rules, or prior scores
        from. Removing it is what keeps an acceptance run uncontaminated, so the
        boundary is asserted rather than left to manifest review.
        """
        payload = _expand_official_manifest()
        self.assertTrue(payload)

        leaked = sorted(
            path
            for path in payload
            if path.startswith(ACCEPTANCE_PREFIXES) or path in ACCEPTANCE_FILES
        )
        self.assertEqual(leaked, [], f"acceptance material in payload: {leaked}")

    def test_skill_relative_references_resolve_in_managed_payload(self) -> None:
        """Every path SKILL.md sends a runtime agent to must be installed.

        This is the standing guard on the packaging boundary: narrowing the
        manifest must never silently strip a document the protocol depends on.
        """
        payload = _expand_official_manifest()
        self.assertIn("SKILL.md", payload)

        references = _relative_markdown_links("SKILL.md")
        self.assertTrue(references)

        unresolved = [target for target in references if target not in payload]
        self.assertEqual(
            unresolved, [], f"SKILL.md references outside the payload: {unresolved}"
        )

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
        reinstall = self._run(source_v1, "install", destination)
        self.assertIn("reinstall (no changes)", reinstall.stdout)
        self.assertEqual("user owned\n", user_file.read_text())

        # Retired-and-customized is a preserve case, not a conflict: the file
        # leaves the manifest, so nothing upstream competes with the local edit.
        retired_user = destination / "docs" / "retired-user.md"
        retired_user.write_text("retired local customization\n", encoding="ascii")
        upgraded = self._run(source_v2, "update", destination)
        self.assertIn("Installed version: 1.0.0-test2", upgraded.stdout)
        self.assertEqual("skill v2\n", (destination / "SKILL.md").read_text())
        self.assertEqual("keep v2\n", (destination / "docs" / "keep.md").read_text())
        self.assertFalse((destination / "docs" / "retired.md").exists())
        self.assertEqual("new v2\n", (destination / "docs" / "new.md").read_text())
        self.assertEqual("readme v2\n", (destination / "README.md").read_text())
        self.assertEqual("retired local customization\n", retired_user.read_text())
        state = (destination / ".looppilot-installation").read_text(encoding="ascii")
        self.assertIn("VERSION|1.0.0-test2", state)
        self.assertIn("COMMIT|" + "2" * 40, state)
        self.assertRegex(state, r"FILE\|SKILL\.md\|[0-9a-f]{64}\|0\|[0-9a-f]{64}")
        self.assertNotIn("FILE|docs/retired-user.md|", state)
        self.assertTrue(any((destination / ".looppilot-backups").rglob("keep.md")))
        self.assertTrue(any((destination / ".looppilot-backups").rglob("retired.md")))

        removed = self._run(source_v2, "uninstall", destination)
        self.assertIn("Removed files from version: 1.0.0-test2", removed.stdout)
        self.assertEqual("user owned\n", user_file.read_text())
        self.assertEqual("retired local customization\n", retired_user.read_text())
        self.assertFalse((destination / "docs" / "new.md").exists())
        self.assertFalse((destination / "SKILL.md").exists())
        self.assertFalse((destination / ".looppilot-installation").exists())
        self.assertTrue((destination / ".looppilot-backups").is_dir())

    def test_upgrade_refuses_conflicting_and_colliding_managed_files(self) -> None:
        """Distribution-004 supersedes the silent-preserve upgrade behavior.

        A managed file changed both locally and upstream, and a newly managed
        path colliding with pre-existing user content, are both conflicts. The
        update must refuse rather than report success.
        """
        source_v1, source_v2 = self._sources()
        destination = self.work / "installed"
        self._run(source_v1, "install", destination)

        colliding_file = destination / "README.md"
        colliding_file.write_text("preexisting readme\n", encoding="ascii")
        (destination / "SKILL.md").write_text("local customization\n", encoding="ascii")

        rejected = self._run(source_v2, "update", destination, check=False)
        self.assertNotEqual(0, rejected.returncode)
        combined = rejected.stdout + rejected.stderr
        self.assertIn("No managed file was changed.", combined)
        self.assertIn("SKILL.md", combined)
        self.assertEqual("local customization\n", (destination / "SKILL.md").read_text())
        self.assertEqual("preexisting readme\n", colliding_file.read_text())
        self.assertFalse((destination / "docs" / "new.md").exists())
        self.assertTrue((destination / "docs" / "retired.md").exists())
        state = (destination / ".looppilot-installation").read_text(encoding="ascii")
        self.assertIn("VERSION|1.0.0-test1", state)

        self._run(source_v2, "update", destination, force=True)
        self.assertEqual("skill v2\n", (destination / "SKILL.md").read_text())
        self.assertEqual("readme v2\n", colliding_file.read_text())
        backups = list((destination / ".looppilot-backups").rglob("SKILL.md"))
        self.assertTrue(
            any(path.read_text() == "local customization\n" for path in backups)
        )

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

        # SKILL.md changed upstream too, so the default update refuses.
        rejected = self._run(source_v2, "update", destination, check=False)
        self.assertNotEqual(0, rejected.returncode)
        self.assertEqual("local customization\n", skill.read_text())

        self._run(source_v2, "update", destination, force=True)
        self.assertEqual("skill v2\n", skill.read_text())
        state = (destination / ".looppilot-installation").read_text(encoding="ascii")
        self.assertRegex(state, r"FILE\|SKILL\.md\|[0-9a-f]{64}\|0\|[0-9a-f]{64}")
        backups = list((destination / ".looppilot-backups").rglob("SKILL.md"))
        self.assertGreaterEqual(len(backups), 1)
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


class DistributionSynchronizationTests(DistributionFixture):
    """Distribution-004 upgrade synchronization, run against every shell."""

    SHELLS = ("powershell", "bash")

    def _sync_sources(self) -> tuple[Path, Path]:
        # Built once per test: the same read-only sources drive every shell.
        cached = getattr(self, "_cached_sync_sources", None)
        if cached is not None:
            return cached
        source_v1 = self._make_source(
            "sync-v1",
            "1.0.0-sync1",
            "1",
            {
                "SKILL.md": "skill v1\n",
                "docs/keep.md": "keep v1\n",
                "docs/stable.md": "stable\n",
                "docs/gone.md": "gone v1\n",
                "docs/gone-custom.md": "gone custom baseline\n",
            },
            ["SKILL.md", "docs/"],
        )
        source_v2 = self._make_source(
            "sync-v2",
            "1.0.0-sync2",
            "2",
            {
                "SKILL.md": "skill v2\n",
                "README.md": "readme v2\n",
                "docs/keep.md": "keep v2\n",
                "docs/stable.md": "stable\n",
            },
            ["SKILL.md", "README.md", "docs/"],
        )
        self._cached_sync_sources = (source_v1, source_v2)
        return source_v1, source_v2

    @staticmethod
    def _reported(result: subprocess.CompletedProcess[str]) -> str:
        """Combined output.

        The shells route advisory messages differently: Bash prints warnings on
        stderr, while PowerShell's warning stream arrives on stdout under
        ``-File``. Both report; only the stream differs.
        """
        return result.stdout + result.stderr

    def _status(self, source: Path, destination: Path, shell: str) -> dict[str, str]:
        result = self._run(source, "status", destination, shell=shell)
        fields: dict[str, str] = {}
        for line in result.stdout.splitlines():
            if ": " in line:
                key, _, value = line.partition(": ")
                fields[key.strip()] = value.strip()
            elif "|" in line:
                action, _, path = line.partition("|")
                fields.setdefault(action.strip(), "")
                fields[action.strip()] += path.strip() + ";"
        return fields

    def _state_of(self, source: Path, destination: Path, shell: str) -> str:
        return self._status(source, destination, shell)["State"]

    def test_synchronization_states_across_shells(self) -> None:
        for shell in self.SHELLS:
            with self.subTest(shell=shell):
                source_v1, source_v2 = self._sync_sources()

                identical = self.work / f"identical-{shell}"
                self._run(source_v1, "install", identical, shell=shell)
                self.assertEqual("CURRENT", self._state_of(source_v1, identical, shell))

                self.assertEqual(
                    "UPDATE_AVAILABLE", self._state_of(source_v2, identical, shell)
                )

                local = self.work / f"local-{shell}"
                self._run(source_v1, "install", local, shell=shell)
                (local / "SKILL.md").write_text("mine\n", encoding="ascii")
                self.assertEqual(
                    "LOCAL_MODIFICATIONS", self._state_of(source_v1, local, shell)
                )

                conflicted = self.work / f"conflict-{shell}"
                self._run(source_v1, "install", conflicted, shell=shell)
                (conflicted / "SKILL.md").write_text("mine\n", encoding="ascii")
                self.assertEqual(
                    "CONFLICT", self._state_of(source_v2, conflicted, shell)
                )

    def test_safe_update_applies_adds_and_removals(self) -> None:
        for shell in self.SHELLS:
            with self.subTest(shell=shell):
                source_v1, source_v2 = self._sync_sources()
                destination = self.work / f"apply-{shell}"
                self._run(source_v1, "install", destination, shell=shell)
                user_file = destination / "user-notes.md"
                user_file.write_text("user owned\n", encoding="ascii")

                status = self._status(source_v2, destination, shell)
                self.assertEqual("UPDATE_AVAILABLE", status["State"])
                self.assertEqual("changed", status["Revision"])
                self.assertEqual("changed", status["Manifest"])
                self.assertIn("SKILL.md", status.get("UPDATE", ""))
                self.assertIn("README.md", status.get("ADD", ""))
                self.assertIn("docs/gone.md", status.get("REMOVE", ""))

                self._run(source_v2, "update", destination, shell=shell)

                self.assertEqual("skill v2\n", (destination / "SKILL.md").read_text())
                self.assertEqual("keep v2\n", (destination / "docs" / "keep.md").read_text())
                self.assertEqual("readme v2\n", (destination / "README.md").read_text())
                self.assertFalse((destination / "docs" / "gone.md").exists())
                self.assertEqual("user owned\n", user_file.read_text())
                self.assertEqual("CURRENT", self._state_of(source_v2, destination, shell))

    def test_conflict_blocks_update_and_force_resolves_it(self) -> None:
        for shell in self.SHELLS:
            with self.subTest(shell=shell):
                source_v1, source_v2 = self._sync_sources()
                destination = self.work / f"blocked-{shell}"
                self._run(source_v1, "install", destination, shell=shell)
                (destination / "SKILL.md").write_text("mine\n", encoding="ascii")

                rejected = self._run(
                    source_v2, "update", destination, shell=shell, check=False
                )
                self.assertNotEqual(0, rejected.returncode)
                self.assertIn("No managed file was changed.", self._reported(rejected))
                # The update must not have claimed success or partially applied.
                self.assertEqual("mine\n", (destination / "SKILL.md").read_text())
                self.assertFalse((destination / "README.md").exists())
                self.assertTrue((destination / "docs" / "gone.md").exists())
                state = (destination / ".looppilot-installation").read_text(encoding="ascii")
                self.assertIn("VERSION|1.0.0-sync1", state)

                self._run(source_v2, "update", destination, shell=shell, force=True)
                self.assertEqual("skill v2\n", (destination / "SKILL.md").read_text())
                backups = list((destination / ".looppilot-backups").rglob("SKILL.md"))
                self.assertTrue(any(path.read_text() == "mine\n" for path in backups))

    def test_customized_file_survives_update_and_keeps_its_baseline(self) -> None:
        for shell in self.SHELLS:
            with self.subTest(shell=shell):
                source_v1, source_v2 = self._sync_sources()
                destination = self.work / f"custom-{shell}"
                self._run(source_v1, "install", destination, shell=shell)
                # stable.md is byte-identical in both sources, so this is case 3.
                (destination / "docs" / "stable.md").write_text("mine\n", encoding="ascii")

                self._run(source_v2, "update", destination, shell=shell)
                self.assertEqual("mine\n", (destination / "docs" / "stable.md").read_text())

                state = (destination / ".looppilot-installation").read_text(encoding="ascii")
                row = next(
                    line
                    for line in state.splitlines()
                    if line.startswith("FILE|docs/stable.md|")
                )
                fields = row.split("|")
                self.assertEqual("1", fields[3], "customization flag must be recorded")
                # The baseline must remain upstream content, not the local edit,
                # so a later genuine upstream change is still detectable.
                self.assertNotEqual(fields[2], fields[4])

                # Still a customization, not a conflict, against the same source.
                self.assertEqual(
                    "LOCAL_MODIFICATIONS", self._state_of(source_v2, destination, shell)
                )

    def test_retired_customized_file_is_preserved_and_reported(self) -> None:
        for shell in self.SHELLS:
            with self.subTest(shell=shell):
                source_v1, source_v2 = self._sync_sources()
                destination = self.work / f"retire-{shell}"
                self._run(source_v1, "install", destination, shell=shell)
                retired = destination / "docs" / "gone-custom.md"
                retired.write_text("my retired edit\n", encoding="ascii")

                status = self._status(source_v2, destination, shell)
                self.assertIn("docs/gone-custom.md", status.get("REMOVE-PRESERVE", ""))

                result = self._run(source_v2, "update", destination, shell=shell)
                self.assertEqual("my retired edit\n", retired.read_text())
                self.assertIn(
                    "preserved retired customized file", self._reported(result)
                )
                # The unmodified retired file is still removed.
                self.assertFalse((destination / "docs" / "gone.md").exists())

    def test_interrupted_update_reports_recovery_and_retry_is_deterministic(self) -> None:
        for shell in self.SHELLS:
            with self.subTest(shell=shell):
                source_v1, source_v2 = self._sync_sources()
                destination = self.work / f"interrupted-{shell}"
                self._run(source_v1, "install", destination, shell=shell)

                # Simulate an update killed after backing up and half-writing.
                backup_id = "interrupted-backup"
                backup = destination / ".looppilot-backups" / backup_id / "docs"
                backup.mkdir(parents=True)
                shutil.copy2(destination / "docs" / "keep.md", backup / "keep.md")
                (destination / ".looppilot-transaction").write_text(
                    "BEGIN|{0}|1.0.0-sync2|{1}|{2}\n"
                    "REPLACE|docs/keep.md\n"
                    "CREATE|README.md\n".format(backup_id, "2" * 40, "0" * 64),
                    encoding="ascii",
                )
                (destination / "docs" / "keep.md").write_text("torn\n", encoding="ascii")
                (destination / "README.md").write_text("torn\n", encoding="ascii")

                status = self._status(source_v1, destination, shell)
                self.assertEqual("RECOVERY_REQUIRED", status["State"])
                self.assertEqual("yes", status["Interrupted update"])

                # Recovery rolls back, then the retry succeeds deterministically.
                self._run(source_v2, "update", destination, shell=shell)
                self.assertFalse((destination / ".looppilot-transaction").exists())
                self.assertEqual("keep v2\n", (destination / "docs" / "keep.md").read_text())
                self.assertEqual("readme v2\n", (destination / "README.md").read_text())
                self.assertEqual("CURRENT", self._state_of(source_v2, destination, shell))

                repeated = self._run(source_v2, "update", destination, shell=shell)
                self.assertIn("update complete", repeated.stdout)
                self.assertEqual("CURRENT", self._state_of(source_v2, destination, shell))

    def test_missing_state_with_payload_requires_recovery(self) -> None:
        for shell in self.SHELLS:
            with self.subTest(shell=shell):
                source_v1, _ = self._sync_sources()
                destination = self.work / f"nostate-{shell}"
                self._run(source_v1, "install", destination, shell=shell)
                (destination / ".looppilot-installation").unlink()

                self.assertEqual(
                    "RECOVERY_REQUIRED", self._state_of(source_v1, destination, shell)
                )

    def test_reinstall_and_uninstall_remain_correct_after_update(self) -> None:
        for shell in self.SHELLS:
            with self.subTest(shell=shell):
                source_v1, source_v2 = self._sync_sources()
                destination = self.work / f"cycle-{shell}"
                self._run(source_v1, "install", destination, shell=shell)
                user_file = destination / "user-notes.md"
                user_file.write_text("user owned\n", encoding="ascii")
                self._run(source_v2, "update", destination, shell=shell)

                reinstall = self._run(source_v2, "install", destination, shell=shell)
                self.assertIn("reinstall (no changes)", reinstall.stdout)
                self.assertEqual("CURRENT", self._state_of(source_v2, destination, shell))

                self._run(source_v2, "uninstall", destination, shell=shell)
                self.assertFalse((destination / "SKILL.md").exists())
                self.assertFalse((destination / "README.md").exists())
                self.assertFalse((destination / ".looppilot-installation").exists())
                # Unmanaged user content is never removed.
                self.assertEqual("user owned\n", user_file.read_text())
                self.assertTrue((destination / ".looppilot-backups").is_dir())

    def test_legacy_format_one_state_is_read_and_migrated(self) -> None:
        for shell in self.SHELLS:
            with self.subTest(shell=shell):
                source_v1, source_v2 = self._sync_sources()
                destination = self.work / f"legacy-{shell}"
                self._run(source_v1, "install", destination, shell=shell)

                state_path = destination / ".looppilot-installation"
                downgraded = []
                for line in state_path.read_text(encoding="ascii").splitlines():
                    if line.startswith("FORMAT|"):
                        downgraded.append("FORMAT|1")
                    elif line.startswith("FILE|"):
                        downgraded.append("|".join(line.split("|")[:4]))
                    else:
                        downgraded.append(line)
                state_path.write_text("\n".join(downgraded) + "\n", encoding="ascii")

                # A legacy uncustomized row still carries a usable baseline.
                self.assertEqual(
                    "UPDATE_AVAILABLE", self._state_of(source_v2, destination, shell)
                )
                self._run(source_v2, "update", destination, shell=shell)
                self.assertEqual("skill v2\n", (destination / "SKILL.md").read_text())
                migrated = state_path.read_text(encoding="ascii")
                self.assertIn("FORMAT|2", migrated)

    def test_status_requires_an_installation(self) -> None:
        for shell in self.SHELLS:
            with self.subTest(shell=shell):
                source_v1, _ = self._sync_sources()
                empty = self.work / f"empty-{shell}"
                empty.mkdir()
                rejected = self._run(
                    source_v1, "status", empty, shell=shell, check=False
                )
                self.assertNotEqual(0, rejected.returncode)
                self.assertIn(
                    "no compatible LoopPilot installation", self._reported(rejected)
                )


if __name__ == "__main__":
    unittest.main()
