"""Prompt source text is data, not evaluation metadata or a disclosure claim."""
import importlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from evaluation_evidence_fixture import digest, make_package, reseal_for_schema_test, save_json

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class EvaluationPromptContentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        shutil.copytree(ROOT / "evaluations", self.root / "evaluations")
        self.authority = Path(self.temp.name) / "operator/approved.json"
        self.package = make_package(self.root, self.authority)

    def check(self):
        errors = importlib.import_module("evaluation_evidence_validation").validate_evaluation_evidence(
            self.root, self.authority, digest(self.authority), [])
        importlib.import_module("cross_host_acceptance_validation").validate_cross_host_acceptance(self.root, errors)
        return errors

    def set_input(self, value, **scenario_changes):
        # Synthetic schema mutation, re-approved only by this isolated test operator.
        scenario_path = self.package / "evidence/scenario.json"
        scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
        prompt = self.package / "prompt.md"
        prompt.write_text(prompt.read_text(encoding="utf-8").replace(scenario["input"], value), encoding="utf-8")
        scenario.update(input=value, **scenario_changes)
        save_json(scenario_path, scenario)
        input_path = self.package / "evidence/input.txt"
        input_path.write_text(value, encoding="utf-8", newline="\n")
        run = json.loads((self.package / "run.json").read_text(encoding="utf-8"))
        run["scenario_sha256"] = digest(scenario_path)
        run["evidence"]["evidence/input.txt"] = digest(input_path)
        event_path = self.package / "evidence/events.jsonl"
        events = [json.loads(line) for line in event_path.read_text(encoding="utf-8").splitlines()]
        events[0]["sha256"] = digest(input_path)
        event_path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8", newline="\n")
        run["trace_sha256"] = digest(event_path)
        save_json(self.package / "run.json", run)
        reseal_for_schema_test(self.package, self.authority)

    def change_prompt(self, old, new):
        path = self.package / "prompt.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        reseal_for_schema_test(self.package, self.authority)

    def test_metadata_looking_input_is_preserved(self):
        self.set_input("Compute six times seven.\n- Evaluation ID: customer-ticket-42\n- Scenario ID: user-defined")
        self.assertEqual([], self.check())

    def test_markdown_headings_in_input_are_preserved(self):
        self.set_input("Compute six times seven.\n\n## Details\nExplain the result.")
        self.assertEqual([], self.check())

    def test_literal_input_boundary_and_input_headings_are_preserved(self):
        self.set_input("Document these literal headings:\n\n## Input Boundary\n\nExample.\n\n## Exact User Input\n\nSample.")
        self.assertEqual([], self.check())

    def test_task_vocabulary_is_not_placeholder_disclosure(self):
        self.set_input("Fix the TODO and FIXME comments; explain fabricated evidence.",
                       description="A task about TODO comments and fabricated evidence.",
                       expected_output="Code with TODO comments removed.")
        self.assertEqual([], self.check())

    def test_exact_input_edge_whitespace_is_preserved(self):
        self.set_input("\n  Compute six times seven.  \n")
        self.assertEqual([], self.check())

    def test_duplicate_actual_metadata_still_fails(self):
        self.change_prompt("# Prompt\n", "# Prompt\n- Evaluation ID: impostor\n")
        self.assertIn("duplicate field Evaluation ID", "\n".join(self.check()))

    def test_missing_real_boundary_cannot_use_heading_inside_input(self):
        value = "Compute six times seven.\n\n## Input Boundary\n\nThis is literal user input."
        self.set_input(value)
        self.change_prompt(value + "\n\n## Input Boundary\n\n", value + "\n\n")
        self.assertTrue(self.check())

    def test_extra_text_after_exact_input_still_fails(self):
        self.change_prompt("Compute six times seven locally.\n\n## Input Boundary",
                           "Compute six times seven locally.\nHidden extra input.\n\n## Input Boundary")
        self.assertTrue(self.check())

    def test_checklist_does_not_claim_field_presence_resolves_current_finding(self):
        text = (ROOT / "docs/release/v1.0-rc-checklist.md").read_text(encoding="utf-8")
        self.assertNotIn("P11A-4 disposition: resolved in the current Phase 12 worktree", text)
        self.assertIn("historical Phase 12", text)
        self.assertIn("evidence-integrity remediation", text)

    def test_literal_record_heading_is_input_not_acceptance(self):
        self.set_input("Explain this heading:\n# Host Acceptance Record")
        self.assertEqual([], self.check())

    def test_literal_verdict_is_input_not_acceptance(self):
        self.set_input("Explain this field:\n- Verdict: accepted")
        self.assertEqual([], self.check())

    def test_fenced_acceptance_example_is_input_not_a_record(self):
        self.set_input("Explain this example:\n```markdown\n# Host Acceptance Record\n- Verdict: accepted\n```")
        self.assertEqual([], self.check())

    def test_real_acceptance_record_named_prompt_still_fails(self):
        from test_cross_host_acceptance import record
        (self.package / "prompt.md").write_text(record(), encoding="utf-8")
        reseal_for_schema_test(self.package, self.authority)
        self.assertTrue(self.check())

    def test_acceptance_verdict_in_real_header_still_fails(self):
        self.change_prompt("# Prompt\n", "# Prompt\n- Verdict: accepted\n")
        self.assertTrue(self.check())

    def test_acceptance_claim_in_boundary_disclosure_still_fails(self):
        path = self.package / "prompt.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n- Verdict: accepted\n", encoding="utf-8")
        reseal_for_schema_test(self.package, self.authority)
        self.assertTrue(self.check())

    def test_prompt_filename_without_run_receipt_is_not_an_exemption(self):
        self.set_input("Explain this field:\n- Verdict: accepted")
        (self.package / "run.json").unlink()
        self.assertTrue(self.check())

    def test_public_validator_preserves_fenced_acceptance_input(self):
        import subprocess
        self.set_input("Explain this example:\n```markdown\n# Host Acceptance Record\n- Verdict: accepted\n```")
        shutil.copytree(ROOT, self.root, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".git", ".tmp", ".claude", ".codex", ".agents", "__pycache__", ".pytest_cache"))
        result = subprocess.run([sys.executable, str(ROOT / "scripts/validate.py"), "--root", str(self.root),
                                 "--evidence-index", str(self.authority), "--evidence-index-sha256", digest(self.authority)],
                                capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
