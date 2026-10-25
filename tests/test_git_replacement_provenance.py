"""Genuine, disposable Git replacement attacks against both installer shells."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shlex
import shutil
import stat
import subprocess
import tempfile
import unittest

from test_distribution import BASH, GIT, POWERSHELL, ROOT, _posix_path


PAYLOAD_A = b"original payload A\n"
PAYLOAD_B = b"replacement payload B\n"


def digest(payload: bytes) -> str:
    row = f"SKILL.md|{hashlib.sha256(payload).hexdigest()}\n"
    return hashlib.sha256(row.encode("ascii")).hexdigest()


class ReplacementCases:
    """Shared behavior cases; only the two concrete shell classes are discovered."""

    def setUp(self):
        if not GIT or not self.shell_path:
            self.skipTest("Git or the requested installer shell is unavailable")
        self.temp_parent = Path(tempfile.gettempdir()).resolve()
        # Short paths also leave room for Windows Git object and snapshot names.
        self.work = Path(tempfile.mkdtemp(prefix="lpr-", dir=self.temp_parent)).resolve()
        self.addCleanup(self.cleanup_work)
        self.source = self.work / "s"
        self.dest = self.work / "d"
        self.source.mkdir()
        self.env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
        # Do not pass PowerShell 7's module path into Windows PowerShell 5.
        self.env = {k: v for k, v in self.env.items() if k.upper() != "PSMODULEPATH"}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_AUTHOR_DATE="2020-01-01T00:00:00+0000",
                        GIT_COMMITTER_DATE="2020-01-01T00:00:00+0000",
                        PYTHONDONTWRITEBYTECODE="1")
        distribution = self.source / "distribution"
        distribution.mkdir()
        for name in ("loop-pilot.sh", "loop-pilot.ps1"):
            shutil.copyfile(ROOT / "distribution" / name, distribution / name)
        (distribution / "version.txt").write_bytes(b"replacement-test\n")
        (distribution / "managed-files.txt").write_bytes(b"SKILL.md\n")
        (self.source / "SKILL.md").write_bytes(PAYLOAD_A)
        self.git("init", "--object-format=sha1")
        for key, value in (("user.name", "Replacement Fixture"),
                           ("user.email", "fixture@example.invalid"),
                           ("core.autocrlf", "false"), ("commit.gpgsign", "false"),
                           ("core.hooksPath", str(self.work / "no-hooks"))):
            self.git("config", key, value)
        self.git("add", ".")
        self.git("commit", "-m", "synthetic A")
        self.a = self.git("rev-parse", "HEAD")
        self.blob_a = self.git("rev-parse", "HEAD:SKILL.md")
        self.blob_b = self.git("hash-object", "-w", "--stdin", input=PAYLOAD_B.decode("ascii"))
        tree_rows = self.git("ls-tree", "HEAD").replace(self.blob_a, self.blob_b)
        self.tree_a = self.git("rev-parse", "HEAD^{tree}")
        self.tree_b = self.git("mktree", input=tree_rows + "\n")
        self.b = self.git("commit-tree", self.tree_b, "-p", self.a, input="synthetic B\n")
        self.assertNotEqual(self.a, self.b)
        self.assertEqual("", self.git("status", "--porcelain=v1"))
        self.assertEqual(PAYLOAD_B.decode().strip(), self.git("show", f"{self.b}:SKILL.md"))

    def cleanup_work(self):
        resolved = self.work.resolve()
        if resolved.parent != self.temp_parent or not resolved.name.startswith("lpr-"):
            raise RuntimeError("refused cleanup outside the disposable fixture")
        def remove_readonly(function, path, error):
            target = Path(path).resolve()
            if not target.is_relative_to(resolved) or not isinstance(error, PermissionError):
                raise error
            target.chmod(stat.S_IWRITE | stat.S_IREAD)
            function(path)

        shutil.rmtree(resolved, onexc=remove_readonly)

    def git(self, *args, input=None):
        if not self.source.resolve().is_relative_to(self.work):
            raise RuntimeError("synthetic Git operations must remain inside the fixture")
        # Binary stdin avoids Windows newline conversion in mktree names/blobs.
        result = subprocess.run([GIT, "-C", str(self.source), *args],
                                input=input.encode("utf-8") if input is not None else None,
                                env=self.env, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr.decode("utf-8", errors="replace"))
        return result.stdout.decode("utf-8").strip()

    def assert_real_replacement(self, original, replacement):
        self.assertEqual(replacement, self.git("rev-parse", f"{self.env.get('GIT_REPLACE_REF_BASE', 'refs/replace/')}{original}"))
        self.assertNotEqual(self.git("--no-replace-objects", "cat-file", "-p", original),
                            self.git("cat-file", "-p", original))
        self.assertEqual(self.git("--no-replace-objects", "cat-file", "-p", replacement),
                         self.git("cat-file", "-p", original))

    def install(self, *, operation="install", injection=None, archive=False):
        """Only schedule a race; all object/ref operations still run real Git.

        injection=(command boundary, original object, replacement object, mutate
        worktree). The boundary is reached synchronously, with no sleeps/polling.
        """
        marker = self.work / "injected"
        if self.shell == "bash":
            # Git Bash can map native TEMP to /tmp rather than /c/.../Temp.
            # Enter its physical source path before invoking the relative script.
            source_dir = shlex.quote(self.source.as_posix())
            destination = shlex.quote(_posix_path(self.dest))
            extra = f" --source-mode archive --archive-sha256 {digest(PAYLOAD_A)}" if archive else ""
            command = [BASH, "-c", f"cd -P {source_dir} && exec bash ./distribution/loop-pilot.sh {operation} --destination {destination}{extra}"]
            if injection:
                boundary, original, replacement, mutate = injection
                wrapper_dir = self.work / "bin"
                wrapper_dir.mkdir()
                q = lambda p: shlex.quote(_posix_path(Path(p)))
                wrapper = wrapper_dir / "git"
                wrapper.write_text(
                    "#!/usr/bin/env bash\nset -e\n"
                    f"if [[ \" $* \" == *' {boundary} '* && ! -e {q(marker)} ]]; then\n"
                    f"  {q(GIT)} -C {q(self.source)} replace {original} {replacement}\n"
                    + (f"  printf 'replacement payload B\\n' > {q(self.source / 'SKILL.md')}\n" if mutate else "")
                    + f"  printf 'injected\\n' > {q(marker)}\nfi\n"
                    f"exec {q(GIT)} \"$@\"\n", encoding="utf-8", newline="\n")
                wrapper.chmod(0o755)
                command[2] = f"export PATH={q(wrapper_dir)}:$PATH; " + command[2]
        else:
            command = [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                       str(self.source / "distribution/loop-pilot.ps1"), "-Operation", operation,
                       "-Destination", str(self.dest)]
            if archive:
                command += ["-SourceMode", "archive", "-ArchiveSha256", digest(PAYLOAD_A)]
            if injection:
                boundary, original, replacement, mutate = injection
                q = lambda p: "'" + str(p).replace("'", "''") + "'"
                harness = self.work / "race.ps1"
                harness.write_text(
                    "$ErrorActionPreference = 'Stop'\nfunction git {\n"
                    f" if (($args -contains '{boundary}') -and !(Test-Path -LiteralPath {q(marker)})) {{\n"
                    f"  & {q(GIT)} -C {q(self.source)} replace {original} {replacement}\n"
                    "  if ($LASTEXITCODE -ne 0) { throw 'replacement injection failed' }\n"
                    + (f"  [IO.File]::WriteAllText({q(self.source / 'SKILL.md')}, \"replacement payload B`n\")\n" if mutate else "")
                    + f"  [IO.File]::WriteAllText({q(marker)}, 'injected')\n }}\n"
                    f" & {q(GIT)} @args\n $global:LASTEXITCODE = $LASTEXITCODE\n}}\n"
                    f"& {q(self.source / 'distribution/loop-pilot.ps1')} -Operation {operation} -Destination {q(self.dest)}\n",
                    encoding="utf-8")
                command = [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(harness)]
        result = subprocess.run(command, env=self.env, capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        if injection:
            self.assertTrue(marker.is_file(), result.stdout + result.stderr)
            self.assert_real_replacement(injection[1], injection[2])
        return result

    def assert_original_receipt(self):
        self.assertEqual(PAYLOAD_A, (self.dest / "SKILL.md").read_bytes())
        state = (self.dest / ".looppilot-installation").read_text(encoding="utf-8")
        self.assertIn(f"COMMIT|{self.a}\n", state)
        self.assertIn(f"PROVENANCE|git-release|{digest(PAYLOAD_A)}|{digest(PAYLOAD_A)}\n", state)
        self.assertNotIn(f"COMMIT|{self.b}\n", state)

    def assert_refused(self, result):
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertFalse(self.dest.exists(), result.stdout + result.stderr)
        self.assertIn("replacement refs", result.stdout + result.stderr)

    def assert_safe_race(self, result):
        if result.returncode:
            self.assertFalse(self.dest.exists(), result.stdout + result.stderr)
            self.assertRegex(result.stdout + result.stderr,
                             "dirty Git source|snapshot content does not match pinned commit|replacement refs")
        else:
            self.assert_original_receipt()

    def test_clean_a_installs_original_bytes_and_receipt(self):
        result = self.install()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assert_original_receipt()

    def test_static_commit_replacement_refuses_apparently_clean_b(self):
        self.git("replace", self.a, self.b)
        self.git("read-tree", self.b)
        (self.source / "SKILL.md").write_bytes(PAYLOAD_B)
        self.assert_real_replacement(self.a, self.b)
        self.assertEqual("", self.git("status", "--porcelain=v1"))
        self.assert_refused(self.install())

    def test_static_unrelated_replacement_refuses_clean_a(self):
        self.git("replace", self.b, self.a)
        self.assert_real_replacement(self.b, self.a)
        self.assertEqual("", self.git("status", "--porcelain=v1"))
        self.assert_refused(self.install())

    def test_static_packed_replacement_refuses_even_when_disabled_in_environment(self):
        self.git("replace", self.b, self.a)
        self.git("pack-refs", "--all")
        self.assertFalse((self.source / ".git/refs/replace" / self.b).exists())
        self.assert_real_replacement(self.b, self.a)
        self.env["GIT_NO_REPLACE_OBJECTS"] = "1"
        self.assert_refused(self.install())

    def test_static_selected_replacement_namespace_refuses_clean_a(self):
        self.env["GIT_REPLACE_REF_BASE"] = "refs/test-replace/"
        self.git("replace", self.b, self.a)
        self.assert_real_replacement(self.b, self.a)
        self.assertEqual("", self.git("status", "--porcelain=v1"))
        self.assert_refused(self.install())

    def test_static_default_refs_refuse_with_another_selected_namespace(self):
        self.git("replace", self.b, self.a)
        self.assert_real_replacement(self.b, self.a)
        self.env["GIT_REPLACE_REF_BASE"] = "refs/test-replace/"
        self.assert_refused(self.install())

    def test_commit_replacement_after_preflight_never_mislabels_b(self):
        self.assert_safe_race(self.install(injection=("ls-tree", self.a, self.b, True)))

    def test_commit_replacement_at_export_never_mislabels_b(self):
        # An export-only race leaves A's worktree unchanged. Raw/no-replace
        # export must produce A, not merely detect B after exporting it.
        result = self.install(injection=("archive", self.a, self.b, False))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assert_original_receipt()

    def test_tree_replacement_at_export_never_mislabels_b(self):
        # An export-only race leaves A's worktree unchanged. Raw/no-replace
        # export must produce A, not merely detect B after exporting it.
        result = self.install(injection=("archive", self.tree_a, self.tree_b, False))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assert_original_receipt()

    def test_blob_replacement_at_export_never_mislabels_b(self):
        # An export-only race leaves A's worktree unchanged. Raw/no-replace
        # export must produce A, not merely detect B after exporting it.
        result = self.install(injection=("archive", self.blob_a, self.blob_b, False))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assert_original_receipt()

    def test_update_race_preserves_original_bytes_and_receipt(self):
        result = self.install()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        before = {p.relative_to(self.dest): p.read_bytes() for p in self.dest.rglob("*") if p.is_file()}
        result = self.install(operation="update", injection=("ls-tree", self.a, self.b, True))
        self.assert_original_receipt()
        if result.returncode:
            self.assertEqual(before, {p.relative_to(self.dest): p.read_bytes()
                                      for p in self.dest.rglob("*") if p.is_file()})

    def test_explicit_archive_remains_digest_bound_and_distinct(self):
        # Build a separate non-Git archive, rather than deleting fixture Git metadata.
        archive_source = self.work / "a"
        shutil.copytree(self.source, archive_source, ignore=shutil.ignore_patterns(".git"))
        self.source = archive_source
        (self.source / "distribution/commit.txt").write_text(self.a + "\n", encoding="ascii")
        result = self.install(archive=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(PAYLOAD_A, (self.dest / "SKILL.md").read_bytes())
        state = (self.dest / ".looppilot-installation").read_text(encoding="utf-8")
        self.assertIn(f"COMMIT|{self.a}\n", state)
        self.assertIn(f"PROVENANCE|archive|{digest(PAYLOAD_A)}|{digest(PAYLOAD_A)}\n", state)


class BashReplacementTests(ReplacementCases, unittest.TestCase):
    shell = "bash"
    shell_path = BASH


class PowerShellReplacementTests(ReplacementCases, unittest.TestCase):
    shell = "powershell"
    shell_path = POWERSHELL


if __name__ == "__main__":
    unittest.main()
