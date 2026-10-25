"""Real native packaging regressions; no runtime or Host Acceptance claims."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import unittest

from test_distribution import BASH, GIT, POWERSHELL, ROOT, DistributionFixture, _posix_path
from installer_test_support import bash_shebang, cleanup_workspace, new_workspace


class SourceLineEndingTests(DistributionFixture):
    def git(self, source, *args):
        result = subprocess.run([GIT, "-C", str(source), *args], capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result.stdout.strip()

    def source(self, name, payload, mode, *, binary=False, convert=False):
        source = self._make_source(name, "portability-test", "a", {"SKILL.md": "seed\n"}, ["SKILL.md"])
        (source / "distribution/commit.txt").unlink()
        # Keep fixture script bytes executable independently of checkout EOLs.
        script = source / "distribution/loop-pilot.sh"
        script.write_bytes(script.read_bytes().replace(b"\r\n", b"\n"))
        (source / "SKILL.md").write_bytes(payload)
        if binary:
            (source / ".gitattributes").write_bytes(b"SKILL.md -text\n")
        self.git(source, "init")
        for key, value in (("user.name", "Portability Fixture"), ("user.email", "fixture@example.invalid"),
                           ("core.autocrlf", "false"), ("commit.gpgsign", "false"),
                           ("core.hooksPath", str(self.work / "no-hooks"))):
            self.git(source, "config", key, value)
        self.git(source, "add", ".")
        self.git(source, "commit", "-m", "controlled source bytes")
        self.git(source, "config", "core.autocrlf", mode)
        if convert:
            self.git(source, "checkout-index", "--force", "--all")
        self.assertEqual("", self.git(source, "status", "--porcelain=v1"))
        return source

    def install(self, shell, source, destination):
        return self._run(source, "install", destination, shell=shell, check=False)

    def assert_receipt(self, source, destination, payload):
        commit = self.git(source, "rev-parse", "HEAD")
        digest = hashlib.sha256(f"SKILL.md|{hashlib.sha256(payload).hexdigest()}\n".encode("ascii")).hexdigest()
        state = (destination / ".looppilot-installation").read_text(encoding="utf-8")
        self.assertIn(f"COMMIT|{commit}\n", state)
        self.assertIn(f"PROVENANCE|git-release|{digest}|{digest}\n", state)

    def test_exact_committed_lf_crlf_and_mixed_bytes_survive_git_filters(self):
        for mode in ("false", "true", "input"):
            for label, payload in (("lf", b"alpha\nbeta\n"), ("crlf", b"alpha\r\nbeta\r\n"),
                                   ("mixed", b"alpha\r\nbeta\n")):
                for shell in ("powershell", "bash"):
                    with self.subTest(mode=mode, endings=label, shell=shell):
                        source = self.source(f"{mode}-{label}-{shell}", payload, mode)
                        dest = self.work / f"{mode}-{label}-{shell}-installed"
                        result = self.install(shell, source, dest)
                        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                        self.assertEqual(payload, (dest / "SKILL.md").read_bytes())
                        self.assert_receipt(source, dest, payload)
                        self.assertEqual(mode, self.git(source, "config", "--get", "core.autocrlf"))

    def test_converted_worktree_installs_original_blob_bytes(self):
        for mode in ("false", "true", "input"):
            for shell in ("powershell", "bash"):
                with self.subTest(mode=mode, shell=shell):
                    source = self.source(f"converted-{mode}-{shell}", b"alpha\nbeta\n", mode, convert=True)
                    dest = self.work / f"converted-{mode}-{shell}-installed"
                    result = self.install(shell, source, dest)
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertEqual(b"alpha\nbeta\n", (dest / "SKILL.md").read_bytes())

    def test_text_disabled_preserves_binary_bytes(self):
        payload = b"alpha\x00\r\nbeta\n"
        for shell in ("powershell", "bash"):
            with self.subTest(shell=shell):
                source = self.source(f"binary-{shell}", payload, "true", binary=True)
                dest = self.work / f"binary-{shell}-installed"
                result = self.install(shell, source, dest)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertEqual(payload, (dest / "SKILL.md").read_bytes())

    def test_git_source_and_destination_paths_with_spaces_and_chinese(self):
        for shell in ("powershell", "bash"):
            with self.subTest(shell=shell):
                payload = b"original\r\nsource bytes\n"
                source = self.source("source space \u6e90-" + shell, payload, "true")
                dest = self.work / ("destination space \u76ee\u6807-" + shell)
                result = self.install(shell, source, dest)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertEqual(payload, (dest / "SKILL.md").read_bytes())
                self.assert_receipt(source, dest, payload)

    def test_real_edits_still_refused_even_when_hidden_from_status(self):
        for hidden in (False, True):
            for shell in ("powershell", "bash"):
                with self.subTest(hidden=hidden, shell=shell):
                    source = self.source(f"edited-{hidden}-{shell}", b"original\r\nbytes\n", "true")
                    if hidden:
                        self.git(source, "update-index", "--assume-unchanged", "SKILL.md")
                    (source / "SKILL.md").write_bytes(b"different content\n")
                    dest = self.work / f"edited-{hidden}-{shell}-installed"
                    result = self.install(shell, source, dest)
                    self.assertNotEqual(0, result.returncode)
                    self.assertFalse(dest.exists(), result.stdout + result.stderr)

    def faulty_hash(self, shell, source, dest, stage, output, code, operation):
        env = os.environ.copy()
        env.pop("PSMODULEPATH", None)
        env.pop("PSModulePath", None)
        env["GIT_CEILING_DIRECTORIES"] = str(ROOT)
        marker = self.work / "hash-injected"
        if marker.exists():
            marker.unlink()
        q = lambda value: "'" + str(value).replace("'", "''") + "'"
        if shell == "powershell":
            if not POWERSHELL:
                self.skipTest("PowerShell unavailable")
            harness = self.work / "faulty-hash.ps1"
            harness.write_text(
                "function git {\n"
                " $filtered = ($args -contains 'hash-object') -and ($args -contains '--path=SKILL.md')\n"
                " $raw = ($args -contains 'hash-object') -and ($args -contains '--no-filters') -and ($args[-1] -eq " + q(source / "SKILL.md") + ")\n"
                + (" if ($filtered) { '" + "0" * 40 + "'; $global:LASTEXITCODE=0; return }\n" if stage == "raw" else "")
                + " if ($" + stage + ") { [IO.File]::WriteAllText(" + q(marker) + ",'injected'); [Console]::Out.Write(" + q(output) + f"); $global:LASTEXITCODE={code}; return }}\n"
                + " & " + q(GIT) + " @args; $global:LASTEXITCODE=$LASTEXITCODE\n}\n"
                + "& " + q(source / "distribution/loop-pilot.ps1") + " -Operation " + operation + " -Destination " + q(dest) + "\n",
                encoding="utf-8-sig",
            )
            command = [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(harness)]
        else:
            if not BASH:
                self.skipTest("Bash unavailable")
            directory = self.work / "faulty-git-bin"
            directory.mkdir(exist_ok=True)
            wrapper = directory / "git"
            # Resolve the physical working-file spelling inside the selected Bash.
            ps = lambda path: shlex.quote(_posix_path(Path(path)))
            wrapper.write_text(
                bash_shebang(BASH)
                + f"target=$(cd -P {ps(source)} && pwd)/SKILL.md\n"
                + "filtered=0; raw=0; hashing=0\n"
                + "for arg in \"$@\"; do case \"$arg\" in hash-object) hashing=1 ;; --path=SKILL.md) filtered=1 ;; --no-filters) raw=1 ;; esac; done\n"
                + "if [ $hashing = 0 ]; then filtered=0; raw=0; fi\n"
                + "if [ $raw = 1 ] && [ ! \"${!#}\" -ef \"$target\" ]; then raw=0; fi\n"
                + ("if [ $filtered = 1 ]; then printf '%s\\n' '" + "0" * 40 + "'; exit 0; fi\n" if stage == "raw" else "")
                + f"if [ ${stage} = 1 ]; then printf injected > {ps(marker)}; printf '%s' {shlex.quote(output)}; exit {code}; fi\n"
                + f"exec {ps(GIT)} \"$@\"\n", encoding="utf-8", newline="\n",
            )
            wrapper.chmod(0o755)
            command = [BASH, "-c", f'export PATH={ps(directory)}:$PATH; exec "$BASH" {ps(source / "distribution/loop-pilot.sh")} {operation} --destination {ps(dest)}']
        result = subprocess.run(command, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertTrue(marker.is_file(), result.stdout + result.stderr)
        return result

    def hash_failure_cases(self, stage):
        for shell in ("powershell", "bash"):
            for operation in ("install", "update"):
                for number, (output, code) in enumerate((("", 17), ("", 0), ("invalid-hash\n", 0), ("a" * 40 + "\n" + "b" * 40 + "\n", 0))):
                    with self.subTest(stage=stage, shell=shell, operation=operation, fault=number):
                        name = f"{stage}-{shell}-{operation}-{number}"
                        source = self.source(name, b"original\r\nbytes\n", "true")
                        dest = self.work / (name + "-installed")
                        before = None
                        if operation == "update":
                            initial = self.install(shell, source, dest)
                            self.assertEqual(0, initial.returncode, initial.stdout + initial.stderr)
                            before = {p.relative_to(dest): p.read_bytes() for p in dest.rglob("*") if p.is_file()}
                        result = self.faulty_hash(shell, source, dest, stage, output, code, operation)
                        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                        if before is None:
                            self.assertFalse(dest.exists())
                        else:
                            self.assertEqual(before, {p.relative_to(dest): p.read_bytes() for p in dest.rglob("*") if p.is_file()})

    def test_failed_or_malformed_filtered_hash_never_approves_raw_fallback(self):
        self.hash_failure_cases("filtered")

    def test_failed_or_malformed_raw_hash_refuses_install_and_update(self):
        self.hash_failure_cases("raw")

    def test_export_corruption_is_refused_after_successful_raw_source_verification(self):
        from test_repair_v2 import ImmutableInstallerTests
        for shell in ("powershell", "bash"):
            with self.subTest(shell=shell):
                source = self.source("export-" + shell, b"original\r\nbytes\n", "true")
                self.assertNotEqual(self.git(source, "rev-parse", "HEAD:SKILL.md"),
                                    self.git(source, "hash-object", "--path=SKILL.md", str(source / "SKILL.md")))
                dest = self.work / ("export-" + shell + "-installed")
                result = ImmutableInstallerTests.tool(self, shell, source, dest, corrupt_export=True)
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn("snapshot content does not match pinned commit", result.stdout + result.stderr)
                self.assertFalse(dest.exists())


class BashEntrypointTests(DistributionFixture):
    def test_all_wrappers_keep_the_initial_bash_with_a_shadow_on_path(self):
        if not BASH:
            self.skipTest("Bash is unavailable")
        source = self._make_source("source with space", "portability-test", "a", {"SKILL.md": "payload\n"}, ["SKILL.md"])
        for name in ("install.sh", "status.sh", "update.sh", "uninstall.sh"):
            (source / name).write_bytes((ROOT / name).read_bytes().replace(b"\r\n", b"\n"))
        script = source / "distribution/loop-pilot.sh"
        script.write_bytes(script.read_bytes().replace(b"\r\n", b"\n"))
        fake = self.work / "shadow-bin"
        fake.mkdir()
        shadow = fake / "bash"
        shadow.write_bytes(b"#!/bin/sh\nexit 88\n")
        shadow.chmod(0o755)
        digest = hashlib.sha256(
            f"SKILL.md|{hashlib.sha256((source / 'SKILL.md').read_bytes()).hexdigest()}\n".encode("ascii")
        ).hexdigest()
        dest = self.work / "installed space \u5b89\u88c5"
        environment = os.environ.copy()
        environment["GIT_CEILING_DIRECTORIES"] = str(ROOT)
        for operation in ("install", "status", "update", "uninstall"):
            with self.subTest(operation=operation):
                command = [BASH, "-c", f"export PATH={shlex.quote(_posix_path(fake))}:$PATH; exec "
                           f'"$BASH" {shlex.quote(_posix_path(source / (operation + ".sh")))} '
                           f"--destination {shlex.quote(_posix_path(dest))} --source-mode archive --archive-sha256 {digest}"]
                result = subprocess.run(command, env=environment, capture_output=True, text=True, encoding="utf-8", errors="replace")
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                if operation != "uninstall":
                    self.assertEqual((source / "SKILL.md").read_bytes(), (dest / "SKILL.md").read_bytes())
        self.assertFalse((dest / ".looppilot-installation").exists())


class TestEnvironmentSelectionTests(unittest.TestCase):
    def probe(self, overrides):
        env = {k: v for k, v in os.environ.items() if not k.startswith("LOOPPILOT_TEST_")}
        env.update(overrides)
        code = "import sys,json;sys.path.insert(0,'tests');import test_distribution as t;print(json.dumps({'powershell':t.POWERSHELL,'bash':t.BASH}))"
        return subprocess.run([sys.executable, "-B", "-c", code], cwd=ROOT, env=env,
                              capture_output=True, text=True, encoding="utf-8", errors="replace")

    def test_invalid_explicit_shell_paths_fail_without_fallback(self):
        for key in ("LOOPPILOT_TEST_POWERSHELL", "LOOPPILOT_TEST_BASH"):
            with self.subTest(variable=key):
                result = self.probe({key: str(ROOT / "nonexistent-shell-executable")})
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn(key, result.stderr)

    def test_explicit_shell_paths_win_over_default_discovery(self):
        # This check concerns selection, not certification of a shell version.
        selected = str(Path(sys.executable).resolve())
        result = self.probe({"LOOPPILOT_TEST_POWERSHELL": selected, "LOOPPILOT_TEST_BASH": selected})
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual({"powershell": selected, "bash": selected}, json.loads(result.stdout))

    def test_required_shells_cannot_be_silently_skipped(self):
        result = self.probe({"PATH": "", "LOOPPILOT_TEST_REQUIRE_SHELLS": "1"})
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("required", result.stderr.lower())


class TemporaryResourceTests(DistributionFixture):
    def test_fixture_workspace_is_outside_the_source_checkout(self):
        self.assertFalse(self.work.resolve().is_relative_to(ROOT.resolve()), self.work)

    def test_cleanup_preserves_parallel_workspace_and_unrelated_sibling(self):
        first = new_workspace("lp-own-", ROOT)
        second = new_workspace("lp-own-", ROOT)
        self.addCleanup(cleanup_workspace, first, first.parent, "lp-own-")
        self.addCleanup(cleanup_workspace, second, second.parent, "lp-own-")
        (first / "owned.txt").write_bytes(b"first")
        preserved = second / "keep.txt"
        preserved.write_bytes(b"second")
        cleanup_workspace(first, first.parent, "lp-own-")
        self.assertFalse(first.exists())
        self.assertEqual(b"second", preserved.read_bytes())

    def test_cleanup_refuses_a_foreign_root(self):
        with self.assertRaises(RuntimeError):
            cleanup_workspace(self.work, self.work.parent, "not-the-created-prefix-")
        self.assertTrue(self.work.is_dir())

    def test_cleanup_refuses_redirected_workspace_and_preserves_the_target(self):
        allocated = new_workspace("lp-redirect-", ROOT)
        target = new_workspace("lp-redirect-", ROOT)
        original = allocated.with_name(allocated.name + "-original")
        self.addCleanup(cleanup_workspace, target, target.parent, "lp-redirect-")
        sentinel = target / "keep.txt"
        sentinel.write_bytes(b"must survive redirected cleanup\n")
        allocated.rename(original)
        try:
            if os.name == "nt":
                if not POWERSHELL:
                    self.fail("PowerShell is required to verify the Windows junction cleanup boundary")
                q = lambda p: "'" + str(p).replace("'", "''") + "'"
                result = subprocess.run([POWERSHELL, "-NoProfile", "-Command",
                                         f"New-Item -ItemType Junction -Path {q(allocated)} -Target {q(target)} -ErrorAction Stop | Out-Null"],
                                        capture_output=True, text=True)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            else:
                allocated.symlink_to(target, target_is_directory=True)
            with self.assertRaises(RuntimeError):
                cleanup_workspace(allocated, allocated.parent, "lp-redirect-")
            self.assertEqual(b"must survive redirected cleanup\n", sentinel.read_bytes())
        finally:
            if allocated.is_symlink():
                allocated.unlink()
            elif allocated.exists() and getattr(allocated.lstat(), "st_file_attributes", 0) & 0x400:
                allocated.rmdir()  # Remove the junction itself, never its target.
            original.rename(allocated)
            cleanup_workspace(allocated, allocated.parent, "lp-redirect-")
