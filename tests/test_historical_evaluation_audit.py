from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from historical_evaluation_audit import audit_historical_evaluations


class HistoricalEvaluationAuditTests(unittest.TestCase):
    def test_current_historical_packages_are_intact_but_not_acceptance_eligible(self):
        report = audit_historical_evaluations(ROOT)

        self.assertEqual(31, report["integrity"]["pinned_files"])
        self.assertEqual(31, report["integrity"]["matched_files"])
        self.assertEqual([], report["integrity"]["missing_files"])
        self.assertEqual([], report["integrity"]["mismatched_files"])
        self.assertEqual(5, len(report["packages"]))
        for package in report["packages"]:
            self.assertTrue(package["historically_intact"], package["evaluation_id"])
            self.assertTrue(package["mechanically_readable"], package["evaluation_id"])
            self.assertFalse(package["behaviorally_evaluable"], package["evaluation_id"])
            self.assertFalse(package["acceptance_eligible"], package["evaluation_id"])
            self.assertEqual("not-evaluated", package["acceptance_status"])
        self.assertEqual(7, len(report["coverage"]))
        self.assertEqual(0, report["summary"]["complete_historical_pairs"])

    def test_audit_reports_missing_trace_score_review_and_incidents_per_package(self):
        report = audit_historical_evaluations(ROOT)
        by_id = {row["evaluation_id"]: row for row in report["packages"]}

        for evaluation_id in ("EVAL-002", "EVAL-003"):
            self.assertFalse(by_id[evaluation_id]["trace_reviewable"])
            self.assertFalse(by_id[evaluation_id]["score_recomputable"])
            self.assertFalse(by_id[evaluation_id]["independent_reviewer_present"])

        self.assertTrue(by_id["EVAL-004"]["infrastructure_incidents"])
        self.assertTrue(any(
            incident["category"] == "http-429"
            for incident in by_id["EVAL-004"]["infrastructure_incidents"]
        ))
        self.assertEqual("loading-only", by_id["EVAL-004"]["supportability"])

    def test_audit_does_not_change_historical_bytes(self):
        before = {
            path.relative_to(ROOT).as_posix(): path.read_bytes()
            for relative in json.loads(
                (ROOT / "scripts/evaluation_history.json").read_text(encoding="utf-8")
            )["files"]
            for path in [ROOT / relative]
        }

        audit_historical_evaluations(ROOT)

        after = {relative: (ROOT / relative).read_bytes() for relative in before}
        self.assertEqual(before, after)

    def test_extra_historical_package_file_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(
                    ".git", ".tmp", "verification-temp", ".four-axis-test-tmp",
                    "__pycache__", ".pytest_cache", "node_modules", ".venv",
                ),
            )
            extra = root / "evaluations/claude-code/EVAL-005/unregistered.md"
            extra.write_text("unregistered history\n", encoding="utf-8")

            report = audit_historical_evaluations(root)

        row = next(item for item in report["packages"] if item["evaluation_id"] == "EVAL-005")
        self.assertFalse(row["historically_intact"])
        self.assertIn("unregistered.md", row["extra_files"])

    def test_modified_or_deleted_historical_file_breaks_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(
                    ".git", ".tmp", "verification-temp", ".four-axis-test-tmp",
                    "__pycache__", ".pytest_cache", "node_modules", ".venv",
                ),
            )
            changed = root / "evaluations/claude-code/EVAL-001/prompt.md"
            changed.write_bytes(changed.read_bytes() + b"\nchanged\n")
            missing = root / "evaluations/claude-code/EVAL-002/environment.md"
            missing.unlink()

            report = audit_historical_evaluations(root)

        self.assertIn("evaluations/claude-code/EVAL-001/prompt.md", report["integrity"]["mismatched_files"])
        self.assertIn("evaluations/claude-code/EVAL-002/environment.md", report["integrity"]["missing_files"])
        self.assertFalse(next(row for row in report["packages"] if row["evaluation_id"] == "EVAL-001")["historically_intact"])
        self.assertFalse(next(row for row in report["packages"] if row["evaluation_id"] == "EVAL-002")["mechanically_readable"])

    def test_byte_only_change_is_detected_even_when_normalized_hash_is_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(
                    ".git", ".tmp", "verification-temp", ".four-axis-test-tmp",
                    "__pycache__", ".pytest_cache", "node_modules", ".venv",
                ),
            )
            path = root / "evaluations/claude-code/EVAL-001/environment.md"
            path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes())

            report = audit_historical_evaluations(root)

        self.assertIn("evaluations/claude-code/EVAL-001/environment.md", report["integrity"]["byte_mismatched_files"])
        row = next(item for item in report["packages"] if item["evaluation_id"] == "EVAL-001")
        self.assertIn("environment.md", row["byte_changed_files"])
        self.assertFalse(row["historically_intact"])
