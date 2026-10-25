"""Regression tests for the C2 isolation check on an installed Skill directory.

The check exists because ``status`` reporting ``CURRENT`` is not a sufficient
condition for C2 isolation: after the payload manifest narrowed, every
acceptance file is unmanaged, and a managed-set computation cannot see an
unmanaged file. These tests pin the two states apart — a tree that is
synchronised and clean, and a tree that is synchronised and contaminated — and
guard the two matching properties that a naive implementation drops.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY_ROOT / "scripts" / "c2_isolation_validation.py"

sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))
sys.path.insert(0, str(REPOSITORY_ROOT / "tests"))

import c2_isolation_validation as c2  # noqa: E402
import test_distribution  # noqa: E402


# The shape of a real clean installation, reduced to one file per payload root.
CLEAN_PAYLOAD = (
    "SKILL.md",
    "AGENTS.md",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "INSTALLATION-VALIDATION.md",
    "install.ps1",
    "status.ps1",
    "distribution/managed-files.txt",
    "distribution/loop-pilot.ps1",
    "docs/installation.md",
    "docs/validation.md",
    "docs/safety-and-stopping.md",
    ".looppilot/README.md",
    ".looppilot/tasks/TASK-TEMPLATE.md",
    "agents/reviewer.md",
    "examples/full-loop.md",
    ".github/workflows/validate.yml",
    ".looppilot-installation",
)

BACKUP_ID = ".looppilot-backups/20260817T101500Z-update"


def _tree(root: Path, paths: tuple[str, ...], body: str = "content\n") -> Path:
    """Materialise a set of relative paths as regular files under ``root``."""
    for relative in paths:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return root


class C2IsolationRuleTests(unittest.TestCase):
    """Rule-level behaviour, exercised directly against the validator."""

    def setUp(self) -> None:
        self.work = Path(tempfile.mkdtemp(prefix="c2-isolation-"))
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)

    def test_clean_payload_shape_reports_no_findings(self) -> None:
        destination = _tree(self.work / "clean", CLEAN_PAYLOAD)

        self.assertEqual(c2.validate_c2_isolation(destination), [])

    def test_acceptance_corpus_at_normal_paths_is_detected(self) -> None:
        """The shape produced by installing over an existing tree.

        Those files are unmanaged after the manifest narrowed, so nothing in
        the installation state describes them and only enumeration finds them.
        """
        destination = _tree(
            self.work / "normal",
            CLEAN_PAYLOAD
            + (
                "tests/evaluation-rubric.md",
                "tests/scenarios.md",
                "scripts/cross_host_acceptance_validation.py",
                "docs/cross-host-acceptance.md",
                "docs/release/v1.0-rc-checklist.md",
                "docs/evaluations/claude-code/decision.md",
                "evaluations/claude-code/EVAL-005/trace.md",
            ),
        )

        findings = c2.validate_c2_isolation(destination)

        self.assertEqual(len(findings), 7)
        self.assertTrue(
            all(finding.startswith("acceptance-corpus:") for finding in findings),
            findings,
        )

    def test_backup_snapshot_acceptance_artifacts_are_detected(self) -> None:
        """The exposure a destination-relative equality check would miss."""
        backed_up = (
            f"{BACKUP_ID}/tests/evaluation-rubric.md",
            f"{BACKUP_ID}/tests/scenarios.md",
            f"{BACKUP_ID}/scripts/cross_host_acceptance_validation.py",
            f"{BACKUP_ID}/docs/cross-host-acceptance.md",
            f"{BACKUP_ID}/evaluations/claude-code/EVAL-005/score.md",
        )
        destination = _tree(self.work / "upgraded", CLEAN_PAYLOAD + backed_up)

        findings = c2.validate_c2_isolation(destination)

        self.assertEqual(len(findings), len(backed_up))
        for relative in backed_up:
            self.assertTrue(
                any(finding.endswith(f"|{relative}") for finding in findings),
                f"{relative} not reported: {findings}",
            )

    def test_destination_relative_equality_would_miss_the_backups(self) -> None:
        """Pin why suffix matching is load-bearing rather than defensive.

        A backed-up rubric's destination-relative path is not the rubric's own
        path, so equality against the prohibited corpus finds nothing. The
        suffix rule is what closes the difference.
        """
        relative = f"{BACKUP_ID}/tests/evaluation-rubric.md"

        self.assertNotIn(relative, c2.ACCEPTANCE_FILES)
        self.assertFalse(relative.startswith(c2.ACCEPTANCE_PREFIXES))
        self.assertEqual(c2._corpus_rule(relative), "tests/")

    def test_nested_snapshot_is_detected_at_any_depth(self) -> None:
        """A snapshot can contain a snapshot, so depth is not bounded."""
        relative = (
            f"{BACKUP_ID}/{BACKUP_ID}/nested/deeper/"
            "evaluations/claude-code/EVAL-001/trace.md"
        )
        destination = _tree(self.work / "nested", CLEAN_PAYLOAD + (relative,))

        findings = c2.validate_c2_isolation(destination)

        self.assertEqual(findings, [f"acceptance-corpus:evaluations/|{relative}"])

    def test_installation_state_is_not_consulted(self) -> None:
        """A state file describing only clean files must not suppress findings.

        This is the property that separates the check from ``status``: the
        acceptance corpus is unmanaged, so a managed-set view of this tree is
        complete and clean while the tree itself is not.
        """
        contaminated = f"{BACKUP_ID}/tests/evaluation-rubric.md"
        destination = _tree(
            self.work / "stateful", CLEAN_PAYLOAD + (contaminated,)
        )
        (destination / ".looppilot-installation").write_text(
            "FORMAT|2\n"
            + "".join(f"FILE|{path}|hash|0|hash\n" for path in CLEAN_PAYLOAD),
            encoding="utf-8",
        )

        findings = c2.validate_c2_isolation(destination)

        self.assertEqual(findings, [f"acceptance-corpus:tests/|{contaminated}"])

    def test_host_acceptance_record_is_detected_outside_evaluations(self) -> None:
        """C2 prohibits a prior record at any path, so content decides."""
        destination = _tree(self.work / "record", CLEAN_PAYLOAD)
        (destination / "docs" / "notes.md").write_text(
            "# Host Acceptance Record: Claude Code 2.1.232, claude-opus-5\n",
            encoding="utf-8",
        )

        findings = c2.validate_c2_isolation(destination)

        self.assertEqual(findings, ["host-acceptance-record|docs/notes.md"])

    def test_memory_index_is_detected(self) -> None:
        destination = _tree(
            self.work / "memory", CLEAN_PAYLOAD + ("CLAUDE.md", "docs/MEMORY.md")
        )

        findings = c2.validate_c2_isolation(destination)

        self.assertEqual(
            findings,
            [
                "memory-index:CLAUDE.md|CLAUDE.md",
                "memory-index:MEMORY.md|docs/MEMORY.md",
            ],
        )

    def test_similarly_named_payload_paths_are_not_false_positives(self) -> None:
        """Segment alignment, so ``docs/release-notes.md`` is not ``docs/release/``."""
        destination = _tree(
            self.work / "lookalike",
            CLEAN_PAYLOAD
            + (
                "docs/release-notes.md",
                "docs/evaluations-overview.md",
                "evaluations.md",
                "docs/cross-host-acceptance-summary.md",
            ),
        )

        self.assertEqual(c2.validate_c2_isolation(destination), [])


class C2IsolationBoundaryTests(unittest.TestCase):
    """The check and the packaging boundary must describe one corpus."""

    def test_corpus_definition_matches_the_distribution_boundary(self) -> None:
        self.assertEqual(
            c2.ACCEPTANCE_PREFIXES, test_distribution.ACCEPTANCE_PREFIXES
        )
        self.assertEqual(c2.ACCEPTANCE_FILES, test_distribution.ACCEPTANCE_FILES)

    def test_official_payload_produces_no_finding(self) -> None:
        """Every managed payload path must pass, or a clean install cannot.

        This is the false-positive guard: adding, say, ``examples/tests/`` to
        the payload would make a correct clean install report contaminated.
        """
        payload = test_distribution._expand_official_manifest()
        self.assertTrue(payload)

        matched = sorted(
            path for path in payload if c2._corpus_rule(path) is not None
        )
        self.assertEqual(matched, [], f"payload paths match the corpus: {matched}")

    def test_installed_payload_documents_declare_no_record(self) -> None:
        """No retained runtime document may look like a Host Acceptance Record."""
        payload = test_distribution._expand_official_manifest()

        declaring = sorted(
            path
            for path in payload
            if path.endswith(".md")
            and c2._declares_host_acceptance_record(REPOSITORY_ROOT / path)
        )
        self.assertEqual(declaring, [])


class C2IsolationEntryPointTests(unittest.TestCase):
    """The command-line entry point, which is what a pre-flight gate runs."""

    def setUp(self) -> None:
        self.work = Path(tempfile.mkdtemp(prefix="c2-isolation-cli-"))
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)

    def _run(self, destination: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--destination", str(destination)],
            capture_output=True,
            text=True,
        )

    def test_clean_tree_exits_zero_and_reports_clean(self) -> None:
        destination = _tree(self.work / "clean", CLEAN_PAYLOAD)

        result = self._run(destination)

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("State: C2_CLEAN", result.stdout)
        self.assertIn("Findings: 0", result.stdout)
        self.assertIn("Installation state read: no", result.stdout)

    def test_contaminated_tree_exits_one_and_names_the_paths(self) -> None:
        relative = f"{BACKUP_ID}/tests/evaluation-rubric.md"
        destination = _tree(self.work / "dirty", CLEAN_PAYLOAD + (relative,))

        result = self._run(destination)

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("State: C2_CONTAMINATED", result.stdout)
        self.assertIn("Findings: 1", result.stdout)
        self.assertIn(relative, result.stdout)
        self.assertIn("Files under .looppilot-backups/: 1", result.stdout)

    def test_missing_destination_exits_two(self) -> None:
        result = self._run(self.work / "absent")

        self.assertEqual(result.returncode, 2)
        self.assertIn("not a directory", result.stdout)


if __name__ == "__main__":
    unittest.main()
