"""Deterministic second-repair regressions; no host acceptance or runtime."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

from test_distribution import BASH, GIT, POWERSHELL, ROOT, DistributionFixture, _posix_path


def payload_digest(root: Path, entries: list[str]) -> str:
    rows = [f"{p}|{hashlib.sha256((root / p).read_bytes()).hexdigest()}\n" for p in sorted(entries)]
    return hashlib.sha256("".join(rows).encode("utf-8")).hexdigest()


class ImmutableInstallerTests(DistributionFixture):
    def git(self, source, *args, input=None, env=None):
        result = subprocess.run([GIT, "-C", str(source), *args], input=input, env=env,
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def source(self, name, *, git=True, marker=False, object_format="sha1"):
        source = self._make_source(name, "snapshot-v2", "a", {"SKILL.md": "snapshot A\n"}, ["SKILL.md"])
        if git:
            if not marker:
                (source / "distribution/commit.txt").unlink()
            self.git(source, "init", "--object-format=" + object_format)
            self.git(source, "config", "user.name", "Isolated Installer Test")
            self.git(source, "config", "user.email", "fixture@example.invalid")
            self.git(source, "config", "core.autocrlf", "false")
            self.git(source, "add", ".")
            self.git(source, "commit", "-m", "synthetic source A")
        return source

    def tool(self, shell, source, dest, *, operation="install", mode=None, digest=None, force=False, race=False, corrupt_export=False, extra_export=False):
        env = os.environ.copy()
        env["GIT_CEILING_DIRECTORIES"] = str(ROOT)
        extra = []
        if shell == "bash":
            if not BASH:
                self.skipTest("Git Bash unavailable")
            command = [BASH, _posix_path(source / "distribution/loop-pilot.sh"), operation,
                       "--destination", _posix_path(dest)]
            if mode: extra += ["--source-mode", mode]
            if digest: extra += ["--archive-sha256", digest]
            if force: extra += ["--force"]
            command += extra
            if race:
                wrappers = self.work / (source.name + "-bin")
                wrappers.mkdir()
                # Real Git exports the pinned SHA after a deterministic worktree mutation.
                (wrappers / "git").write_text(
                    "#!/usr/bin/env bash\n"
                    "if [[ \" $* \" == *' archive '* ]]; then\n"
                    f"  printf 'worktree B\\n' > '{_posix_path(source / 'SKILL.md')}'\n"
                    f"  printf 'missing.txt\\n' > '{_posix_path(source / 'distribution/managed-files.txt')}'\n"
                    f"  printf 'changed-version\\n' > '{_posix_path(source / 'distribution/version.txt')}'\n"
                    "fi\n"
                    f"exec '{_posix_path(Path(GIT))}' \"$@\"\n", encoding="utf-8", newline="\n")
                command = [BASH, "-c", f'export PATH="{_posix_path(wrappers)}:$PATH"; exec bash '
                           f'"{_posix_path(source / "distribution/loop-pilot.sh")}" {operation} '
                           f'--destination "{_posix_path(dest)}"']
        else:
            if not POWERSHELL:
                self.skipTest("PowerShell unavailable")
            command = [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                       str(source / "distribution/loop-pilot.ps1"), "-Operation", operation,
                       "-Destination", str(dest)]
            if mode: extra += ["-SourceMode", mode]
            if digest: extra += ["-ArchiveSha256", digest]
            if force: extra += ["-Force"]
            command += extra
            if race:
                harness = self.work / (source.name + "-race.ps1")
                harness.write_text(
                    "function git {\n if ($args -contains 'archive') {\n"
                    f" [IO.File]::WriteAllText('{source / 'SKILL.md'}', \"worktree B`n\")\n"
                    f" [IO.File]::WriteAllText('{source / 'distribution/managed-files.txt'}', \"missing.txt`n\")\n"
                    f" [IO.File]::WriteAllText('{source / 'distribution/version.txt'}', \"changed-version`n\")\n"
                    " }\n"
                    f" & '{GIT}' @args\n}}\n"
                    f"& '{source / 'distribution/loop-pilot.ps1'}' -Operation {operation} -Destination '{dest}'\n",
                    encoding="utf-8")
                command = [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(harness)]
        if corrupt_export or extra_export:
            mutator = self.work / (source.name + "-mutate-export.py")
            mutator.write_text(
                "from pathlib import Path\nimport sys,zipfile,tarfile,io\n"
                "p=Path(next(a.split('=',1)[1] for a in sys.argv[1:] if a.startswith('--output=')))\n"
                "tmp=p.with_suffix('.changed')\n"
                "extra='--extra' in sys.argv[1:]\n"
                "if p.suffix=='.zip':\n"
                " with zipfile.ZipFile(p) as src, zipfile.ZipFile(tmp,'w') as dst:\n"
                "  for m in src.infolist(): dst.writestr(m,b'wrong exported payload' if m.filename=='SKILL.md' and not extra else src.read(m))\n"
                "  if extra: dst.writestr('docs/injected.md',b'not in recorded commit')\n"
                "else:\n"
                " with tarfile.open(p) as src, tarfile.open(tmp,'w') as dst:\n"
                "  for m in src.getmembers():\n"
                "   b=src.extractfile(m).read() if m.isfile() else None\n"
                "   if m.name=='SKILL.md' and not extra: b=b'wrong exported payload';m.size=len(b)\n"
                "   dst.addfile(m,io.BytesIO(b) if b is not None else None)\n"
                "  if extra:\n"
                "   b=b'not in recorded commit';m=tarfile.TarInfo('docs/injected.md');m.size=len(b);dst.addfile(m,io.BytesIO(b))\n"
                "tmp.replace(p)\n", encoding="utf-8")
            mutation_option = "--extra" if extra_export else ""
            if shell == "bash":
                wrappers = self.work / (source.name + "-bin")
                wrappers.mkdir()
                (wrappers / "git").write_text(
                    f"#!/usr/bin/env bash\n'{_posix_path(Path(GIT))}' \"$@\"\nrc=$?\n"
                    "if [[ \" $* \" == *' archive '* && $rc == 0 ]]; then\n"
                    f" '{_posix_path(Path(sys.executable))}' '{_posix_path(mutator)}' {mutation_option} \"$@\"\n rc=$?\nfi\nexit \"$rc\"\n",
                    encoding="utf-8", newline="\n")
                command = [BASH, "-c", f'export PATH="{_posix_path(wrappers)}:$PATH"; exec bash '
                           f'"{_posix_path(source / "distribution/loop-pilot.sh")}" install --destination "{_posix_path(dest)}"']
            else:
                harness = self.work / (source.name + "-bad-export.ps1")
                harness.write_text(
                    f"function git {{ & '{GIT}' @args; $code=$LASTEXITCODE;\n"
                    f"if (($args -contains 'archive') -and $code -eq 0) {{ & '{sys.executable}' '{mutator}' {mutation_option} @args; $code=$LASTEXITCODE }}\n"
                    "$global:LASTEXITCODE=$code }\n"
                    f"& '{source / 'distribution/loop-pilot.ps1'}' -Operation install -Destination '{dest}'\n",
                    encoding="utf-8")
                command = [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(harness)]
        return subprocess.run(command, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")

    def refused(self, result, dest):
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertFalse((dest / ".looppilot-installation").exists())
        self.assertFalse((dest / "SKILL.md").exists())

    def test_worktree_mutation_cannot_change_pinned_release_payload(self):
        for shell in ("bash", "powershell"):
            with self.subTest(shell=shell):
                source = self.source(shell)
                head = self.git(source, "rev-parse", "HEAD")
                expected = (source / "SKILL.md").read_bytes()
                digest = payload_digest(source, ["SKILL.md"])
                dest = self.work / (shell + "-installed")
                result = self.tool(shell, source, dest, race=True)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertNotEqual(expected, (source / "SKILL.md").read_bytes(), "archive boundary hook must execute")
                self.assertEqual(expected, (dest / "SKILL.md").read_bytes())
                state = (dest / ".looppilot-installation").read_text()
                self.assertIn("COMMIT|" + head, state)
                self.assertIn(f"PROVENANCE|git-release|{digest}|{digest}", state)
                self.assertIn("VERSION|snapshot-v2", state)

    def test_clean_release_provenance_chain_matches(self):
        for shell in ("bash", "powershell"):
            with self.subTest(shell=shell):
                source = self.source(shell)
                head = self.git(source, "rev-parse", "HEAD")
                digest = payload_digest(source, ["SKILL.md"])
                dest = self.work / (shell + "-installed")
                result = self.tool(shell, source, dest)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                state = (dest / ".looppilot-installation").read_text()
                self.assertIn("COMMIT|" + head, state)
                self.assertIn(f"PROVENANCE|git-release|{digest}|{digest}", state)
                self.assertEqual(digest, payload_digest(dest, ["SKILL.md"]))

    def test_dirty_release_is_refused(self):
        for shell in ("bash", "powershell"):
            source = self.source(shell)
            (source / "SKILL.md").write_text("dirty B")
            self.refused(self.tool(shell, source, self.work / (shell + "-dest")), self.work / (shell + "-dest"))

    def test_missing_git_never_implicitly_uses_commit_txt(self):
        for shell in ("bash", "powershell"):
            source = self.source(shell, git=False)
            self.refused(self.tool(shell, source, self.work / (shell + "-dest")), self.work / (shell + "-dest"))

    def test_invalid_git_head_with_stale_commit_txt_is_refused(self):
        for shell in ("bash", "powershell"):
            source = self.source(shell)
            (source / "distribution/commit.txt").write_text(self.git(source, "rev-parse", "HEAD"))
            (source / ".git/HEAD").write_text("invalid metadata\n")
            self.refused(self.tool(shell, source, self.work / (shell + "-dest")), self.work / (shell + "-dest"))

    def test_missing_head_ref_is_refused(self):
        for shell in ("bash", "powershell"):
            source = self.source(shell)
            (source / "distribution/commit.txt").write_text("a" * 40)
            (source / ".git/HEAD").write_text("ref: refs/heads/does-not-exist\n")
            self.refused(self.tool(shell, source, self.work / (shell + "-dest")), self.work / (shell + "-dest"))

    def test_missing_commit_object_is_refused(self):
        for shell in ("bash", "powershell"):
            source = self.source(shell)
            (source / "distribution/commit.txt").write_text("a" * 40)
            (source / ".git/HEAD").write_text("f" * 40 + "\n")
            self.refused(self.tool(shell, source, self.work / (shell + "-dest")), self.work / (shell + "-dest"))

    def test_noncommit_head_is_refused(self):
        for shell in ("bash", "powershell"):
            source = self.source(shell)
            blob = self.git(source, "rev-parse", "HEAD:SKILL.md")
            (source / "distribution/commit.txt").write_text("a" * 40)
            (source / ".git/HEAD").write_text(blob + "\n")
            self.refused(self.tool(shell, source, self.work / (shell + "-dest")), self.work / (shell + "-dest"))

    def test_conflicting_snapshot_commit_marker_is_refused(self):
        for shell in ("bash", "powershell"):
            source = self.source(shell, marker=True)
            self.refused(self.tool(shell, source, self.work / (shell + "-dest")), self.work / (shell + "-dest"))

    def test_archive_requires_explicit_digest(self):
        for shell in ("bash", "powershell"):
            source = self.source(shell, git=False)
            self.refused(self.tool(shell, source, self.work / (shell + "-dest"), mode="archive"), self.work / (shell + "-dest"))

    def test_explicit_archive_is_distinct_and_digest_bound(self):
        for shell in ("bash", "powershell"):
            with self.subTest(shell=shell):
                source = self.source(shell, git=False)
                digest = payload_digest(source, ["SKILL.md"])
                dest = self.work / (shell + "-installed")
                result = self.tool(shell, source, dest, mode="archive", digest=digest)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn(f"PROVENANCE|archive|{digest}|{digest}", (dest / ".looppilot-installation").read_text())
                bad = self.work / (shell + "-wrong-digest")
                self.refused(self.tool(shell, source, bad, mode="archive", digest="0" * 64), bad)

    def test_archive_mode_cannot_bypass_git_metadata(self):
        for shell in ("bash", "powershell"):
            source = self.source(shell)
            (source / ".git/HEAD").write_text("invalid\n")
            (source / "distribution/commit.txt").write_text("a" * 40)
            dest = self.work / (shell + "-dest")
            self.refused(self.tool(shell, source, dest, mode="archive", digest=payload_digest(source, ["SKILL.md"])), dest)

    def test_force_cannot_bypass_unresolved_identity(self):
        for shell in ("bash", "powershell"):
            source = self.source(shell, git=False)
            dest = self.work / (shell + "-dest")
            self.refused(self.tool(shell, source, dest, force=True), dest)


    def test_exported_payload_must_match_pinned_git_tree(self):
        for shell in ("bash", "powershell"):
            with self.subTest(shell=shell):
                source = self.source(shell)
                dest = self.work / (shell + "-dest")
                result = self.tool(shell, source, dest, corrupt_export=True)
                self.refused(result, dest)
                self.assertIn("snapshot content does not match pinned commit", result.stdout + result.stderr)

    def test_update_uses_pinned_snapshot_after_worktree_mutation(self):
        for shell in ("bash", "powershell"):
            with self.subTest(shell=shell):
                source = self.source(shell)
                dest = self.work / (shell + "-installed")
                first = self.tool(shell, source, dest)
                self.assertEqual(0, first.returncode, first.stdout + first.stderr)
                (source / "SKILL.md").write_text("committed update A2\n")
                self.git(source, "add", "SKILL.md")
                self.git(source, "commit", "-m", "synthetic committed update")
                head = self.git(source, "rev-parse", "HEAD")
                expected = (source / "SKILL.md").read_bytes()
                digest = payload_digest(source, ["SKILL.md"])
                result = self.tool(shell, source, dest, operation="update", race=True)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertNotEqual(expected, (source / "SKILL.md").read_bytes())
                self.assertEqual(expected, (dest / "SKILL.md").read_bytes())
                state = (dest / ".looppilot-installation").read_text()
                self.assertIn("COMMIT|" + head, state)
                self.assertIn(f"PROVENANCE|git-release|{digest}|{digest}", state)


    def test_extra_export_file_under_managed_directory_is_refused(self):
        for shell in ("bash", "powershell"):
            with self.subTest(shell=shell):
                source = self.source(shell)
                (source / "docs").mkdir()
                (source / "docs/kept.md").write_text("committed document\n")
                (source / "distribution/managed-files.txt").write_text("SKILL.md\ndocs/\n")
                self.git(source, "add", ".")
                self.git(source, "commit", "-m", "synthetic directory payload")
                dest = self.work / (shell + "-dest")
                result = self.tool(shell, source, dest, extra_export=True)
                self.refused(result, dest)
                self.assertIn("unexpected snapshot file", result.stdout + result.stderr)
                self.assertFalse((dest / "docs/injected.md").exists())


    def test_unsupported_git_object_format_is_refused(self):
        # Installation FORMAT 2 commits are explicitly 40-character SHA-1 IDs.
        for shell in ("bash", "powershell"):
            with self.subTest(shell=shell):
                source = self.source(shell, object_format="sha256")
                self.assertEqual(64, len(self.git(source, "rev-parse", "HEAD")))
                dest = self.work / (shell + "-dest")
                self.refused(self.tool(shell, source, dest), dest)
