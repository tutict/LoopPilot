"""Architecture repair properties; static contracts are not host acceptance."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import yaml
from test_distribution import DistributionFixture, GIT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class ArchitectureContractTests(unittest.TestCase):
    def test_shipped_templates_are_neutral_and_session_independent(self):
        for path, status, marker in (
            (".looppilot/STATE.md", "inactive", "No active shared task."),
            (".looppilot/HANDOFF.md", "none", "No active handoff."),
        ):
            with self.subTest(path=path):
                content = text(path)
                self.assertIn(f"Status: {status}\n", content)
                self.assertIn("Updated: YYYY-MM-DD\n", content)
                self.assertIn(marker, content)
                self.assertNotRegex(content, r"(?i)codex|claude|[0-9a-f]{40,64}|20\d\d-\d\d-\d\d|Status: active")
                self.assertNotRegex(content, r"(?i)(?:closure|release|deployment) (?:complete|approved|ready)")
        state = text(".looppilot/STATE.md")
        for section in ("Success Criteria", "Current Progress", "Verified Evidence", "Blockers", "Next Action"):
            self.assertIn(f"## {section}\n\n- None.\n", state)
        handoff = text(".looppilot/HANDOFF.md")
        for section in ("Completed", "Observed Evidence", "Remaining Work", "Blockers", "Risks and Constraints", "Recommended Next Action"):
            self.assertIn(f"## {section}\n\n- None.\n", handoff)

    def test_template_recovery_and_authority_guards(self):
        state = " ".join(text(".looppilot/STATE.md").split())
        handoff = " ".join(text(".looppilot/HANDOFF.md").split())
        self.assertIn("Inactive state is not recovery-ready", state)
        self.assertIn("MUST defer to an accessible native Plan", state)
        self.assertIn("not copy Task Contracts", state)
        self.assertIn("second Recovery authority", handoff)
        self.assertIn("NOT imply Project closure, release authority, deployment", handoff)
        self.assertIn("derived projection", handoff)
        self.assertIn("MUST defer to an accessible native Plan and host execution authority", handoff)

    def test_verification_scoping_preserves_mandatory_authority(self):
        for path in ("SKILL.md", "AGENTS.md", "docs/safety-and-stopping.md"):
            content = " ".join(text(path).split())
            with self.subTest(path=path):
                self.assertIn("higher-priority", content)
                self.assertIn("Task Contract", content)
                self.assertIn("MUST NOT scope out required verification", content)
                self.assertNotIn("only because a standing instruction says to test", content)
        core = " ".join(text("SKILL.md").split())
        self.assertIn("objectively unrelated", core)
        self.assertIn("verification gap", core)
        self.assertIn("every skipped or scoped-down check", core)
        self.assertIn("inconvenience or duration", core)

    def test_two_axes_and_non_coding_cases(self):
        core = " ".join(text("SKILL.md").split())
        self.assertIn("Product Risk determines review, validation, and evidence depth", core)
        self.assertIn("Coordination Necessity determines whether Full Loop is required", core)
        self.assertIn("before choosing any mode", core)
        self.assertIn("escalation evidence appears", core)
        doc = text("docs/mode-selection-and-escalation.md")
        for scenario in ("High product risk / low coordination", "Low product risk / high coordination", "Multi-step non-coding / low coordination", "Multi-step non-coding / real coordination"):
            self.assertIn(scenario, doc)
        for token in ("shared factual state", "multi-role dependency", "parallel Workers", "Integrator coordination", "dependency chain", "explicit coordination requirement"):
            self.assertIn(token, doc)
        for path in ("SKILL.md", "README.md"):
            self.assertIn("multi-step non-coding", text(path))

    def test_no_confirmation_does_not_grant_permission(self):
        core = " ".join(text("SKILL.md").split())
        self.assertIn("not a grant of authority", core)
        self.assertIn("local, reversible, non-destructive", core)
        self.assertIn("no external effects", core)
        self.assertIn("host permissions", core)

    def test_single_shortcut_owner_and_no_repository_fallback(self):
        core = yaml.safe_load(text("SKILL.md").split("---", 2)[1])
        alias = yaml.safe_load(text("shortcuts/lp/SKILL.md").split("---", 2)[1])
        self.assertEqual("lp", alias["name"])
        self.assertIn("/lp", alias["description"])
        self.assertNotRegex(core["description"], r"(?<!\w)(?:/lp|\$lp)(?!\w)")
        contract = " ".join(text("shortcuts/lp/SKILL.md").split())
        self.assertIn("../../SKILL.md", contract)
        self.assertIn("MUST NOT search the current directory or repository", contract)
        self.assertIn("missing, ambiguous, or inconsistent", contract)
        self.assertIn(".looppilot-installation", contract)
        self.assertIn("shortcuts/lp/SKILL.md", text("distribution/managed-files.txt").splitlines())


class ShortcutResolutionTests(unittest.TestCase):
    def test_installed_alias_equals_canonical_despite_repository_shadow(self):
        from shortcut_validation import resolve_installed_shortcut
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "installed"
            alias = root / "shortcuts/lp/SKILL.md"
            alias.parent.mkdir(parents=True)
            alias.write_text(text("shortcuts/lp/SKILL.md"), encoding="utf-8")
            canonical = root / "SKILL.md"
            canonical.write_text(text("SKILL.md"), encoding="utf-8")
            rows = ["FORMAT|2", "VERSION|test", "COMMIT|" + "a" * 40, "MANIFEST|" + "b" * 64]
            for file in (alias, canonical):
                digest = hashlib.sha256(file.read_bytes()).hexdigest()
                rows.append(f"FILE|{file.relative_to(root).as_posix()}|{digest}|0|{digest}")
            (root / ".looppilot-installation").write_text("\n".join(rows) + "\n")
            shadow = Path(tmp) / "repository/SKILL.md"
            shadow.parent.mkdir()
            shadow.write_text("---\nname: loop-pilot\n---\nWrong protocol")
            self.assertEqual(canonical.resolve(), resolve_installed_shortcut(alias, long_command=canonical))
            with self.assertRaises(ValueError):
                resolve_installed_shortcut(alias, long_command=shadow)
            original_state = (root / ".looppilot-installation").read_text()
            (root / ".looppilot-installation").write_text(original_state + rows[-1] + "\n")
            with self.assertRaises(ValueError):
                resolve_installed_shortcut(alias, long_command=canonical)
            (root / ".looppilot-installation").write_text(original_state)
            canonical.write_text("changed", encoding="utf-8")
            with self.assertRaises(ValueError):
                resolve_installed_shortcut(alias, long_command=canonical)

    def test_repository_shortcut_and_out_of_band_copy_fail_closed(self):
        from shortcut_validation import resolve_installed_shortcut
        with self.assertRaises(ValueError):
            resolve_installed_shortcut(ROOT / "shortcuts/lp/SKILL.md", long_command=ROOT / "SKILL.md")
        with tempfile.TemporaryDirectory() as tmp:
            alias = Path(tmp) / "skills/lp/SKILL.md"
            alias.parent.mkdir(parents=True)
            alias.write_text(text("shortcuts/lp/SKILL.md"), encoding="utf-8")
            canonical = Path(tmp) / "skills/loop-pilot/SKILL.md"
            with self.assertRaises(ValueError):
                resolve_installed_shortcut(alias, long_command=canonical)


class InstallerProvenanceTests(DistributionFixture):
    def make_git_source(self, name):
        if not GIT:
            self.skipTest("Git unavailable")
        source = self._make_source(name, "test", "a", {"SKILL.md": "canonical\n"}, ["SKILL.md"])
        # The fixture is now a Git release source, not a publisher archive.
        (source / "distribution/commit.txt").unlink()
        for args in (("init",), ("config", "core.autocrlf", "false"), ("config", "user.name", "Test Fixture"), ("config", "user.email", "fixture@example.invalid"), ("add", "."), ("commit", "-m", "isolated test fixture")):
            subprocess.run([GIT, "-C", str(source), *args], check=True, capture_output=True)
        return source

    def test_clean_install_records_actual_head_and_content(self):
        for shell in ("powershell", "bash"):
            with self.subTest(shell=shell):
                source = self.make_git_source(shell)
                dest = self.work / (shell + "-installed")
                self._run(source, "install", dest, shell=shell)
                head = subprocess.check_output([GIT, "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
                state = (dest / ".looppilot-installation").read_text()
                self.assertIn("COMMIT|" + head, state)
                self.assertEqual((source / "SKILL.md").read_bytes(), (dest / "SKILL.md").read_bytes())

    def test_dirty_sources_refused_before_destination_mutation(self):
        for shell in ("powershell", "bash"):
            for kind in ("unstaged", "staged", "untracked"):
                with self.subTest(shell=shell, kind=kind):
                    source = self.make_git_source(shell + kind)
                    if kind == "untracked":
                        (source / "extra.txt").write_text("dirty")
                    else:
                        (source / "SKILL.md").write_text("dirty")
                        if kind == "staged":
                            subprocess.run([GIT, "-C", str(source), "add", "SKILL.md"], check=True)
                    dest = self.work / (shell + kind + "-installed")
                    result = self._run(source, "install", dest, shell=shell, check=False)
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn("dirty Git source", result.stdout + result.stderr)
                    self.assertFalse(dest.exists())

    def test_dirty_update_preserves_existing_installation(self):
        for shell in ("powershell", "bash"):
            with self.subTest(shell=shell):
                source = self.make_git_source(shell)
                dest = self.work / (shell + "-installed")
                self._run(source, "install", dest, shell=shell)
                before = {p.relative_to(dest): p.read_bytes() for p in dest.rglob("*") if p.is_file()}
                (source / "SKILL.md").write_text("dirty")
                result = self._run(source, "update", dest, shell=shell, check=False)
                self.assertNotEqual(0, result.returncode)
                self.assertEqual(before, {p.relative_to(dest): p.read_bytes() for p in dest.rglob("*") if p.is_file()})


    def test_managed_alias_install_status_and_uninstall(self):
        from shortcut_validation import resolve_installed_shortcut
        for shell in ("powershell", "bash"):
            with self.subTest(shell=shell):
                files = {"SKILL.md": text("SKILL.md"), "shortcuts/lp/SKILL.md": text("shortcuts/lp/SKILL.md")}
                source = self._make_source(shell, "test", "a", files, list(files))
                dest = self.work / (shell + "-installed")
                self._run(source, "install", dest, shell=shell)
                canonical = dest / "SKILL.md"
                alias = dest / "shortcuts/lp/SKILL.md"
                self.assertEqual(canonical.resolve(), resolve_installed_shortcut(alias, long_command=canonical))
                self._run(source, "status", dest, shell=shell)
                self._run(source, "uninstall", dest, shell=shell)
                self.assertFalse(alias.exists())
                self.assertFalse(canonical.exists())

    def test_assume_unchanged_managed_content_is_not_clean_provenance(self):
        for shell in ("powershell", "bash"):
            with self.subTest(shell=shell):
                source = self.make_git_source(shell)
                subprocess.run([GIT, "-C", str(source), "update-index", "--assume-unchanged", "SKILL.md"], check=True)
                (source / "SKILL.md").write_text("hidden dirty content")
                dest = self.work / (shell + "-installed")
                result = self._run(source, "install", dest, shell=shell, check=False)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("dirty Git source", result.stdout + result.stderr)
                self.assertFalse(dest.exists())

    def test_archive_does_not_inherit_parent_repository_head(self):
        for shell in ("powershell", "bash"):
            with self.subTest(shell=shell):
                parent = self.make_git_source(shell)
                source = self._make_source(shell + "/archive", "test", "b", {"SKILL.md": "archive\n"}, ["SKILL.md"])
                dest = self.work / (shell + "-installed")
                self._run(source, "install", dest, shell=shell)
                state = (dest / ".looppilot-installation").read_text()
                self.assertIn("COMMIT|" + "b" * 40, state)
                head = subprocess.check_output([GIT, "-C", str(parent), "rev-parse", "HEAD"], text=True).strip()
                self.assertNotIn("COMMIT|" + head, state)
