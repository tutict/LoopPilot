"""Public input structure and receipt-bound disclosure regression cases."""
import importlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from evaluation_evidence_fixture import make_package, reseal_for_schema_test, save_json, digest, approve_record
import test_evaluation_prompt_content as prompt_cases

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class DisclosureSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        shutil.copytree(ROOT / "evaluations", self.root / "evaluations")
        self.authority = Path(self.temp.name) / "operator/approved.json"
        self.package = make_package(self.root, self.authority)

    def check(self):
        return importlib.import_module("evaluation_evidence_validation").validate_evaluation_evidence(
            self.root, self.authority, digest(self.authority), [])

    def field(self, name, label, value):
        path = self.package / name
        text = path.read_text(encoding="utf-8")
        pattern = rf"(?m)^- {re.escape(label)}:.*$"
        text = re.sub(pattern, lambda _: f"- {label}: {value}", text) if re.search(pattern, text) else text + f"\n- {label}: {value}\n"
        path.write_text(text, encoding="utf-8", newline="\n")

    def limits(self, text, state="unverified"):
        for name in ("environment.md", "score.md"):
            self.field(name, "Unverified limitations", text)
            self.field(name, "Limitation state", state)
        review_path = self.package / "review.json"
        review = json.loads(review_path.read_text(encoding="utf-8"))
        if "disclosures" in review:
            review["disclosures"]["limitations"].update(text=text, state=state)
            save_json(review_path, review)
        reseal_for_schema_test(self.package, self.authority)

    def failed_run(self):
        observed = subprocess.run([sys.executable, "-c", "import sys; print('gateway timeout (local specimen)'); sys.exit(7)"], capture_output=True)
        self.assertEqual(7, observed.returncode)
        output = self.package / "evidence/stdout.txt"
        output.write_bytes(observed.stdout)
        run_path = self.package / "run.json"
        run = json.loads(run_path.read_text(encoding="utf-8"))
        run.update(status="failed", exit_code=observed.returncode)
        run["evidence"]["evidence/stdout.txt"] = digest(output)
        events_path = self.package / "evidence/events.jsonl"
        events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
        events[1]["sha256"] = digest(output)
        events_path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8", newline="\n")
        run["trace_sha256"] = digest(events_path)
        save_json(run_path, run)
        failure = "The local process failed with gateway timeout output; no real gateway was contacted."
        self.field("score.md", "Observed outcome", "failed")
        self.field("score.md", "Critical failures", failure)
        self.field("score.md", "Reviewer decision", "reject")
        review_path = self.package / "review.json"
        review = json.loads(review_path.read_text(encoding="utf-8"))
        review["decision"] = "reject"
        if "disclosures" in review:
            review["disclosures"].update(outcome="failed", critical_failures=failure)
        save_json(review_path, review)
        self.limits("The local run failed; missing gateway retry evidence remains unverified.", "unresolved")

    def test_real_failed_process_and_matching_disclosure_pass(self):
        self.failed_run()
        self.assertEqual([], self.check())

    def test_honest_failure_words_are_not_placeholder_detection(self):
        self.failed_run()
        self.limits("The agent fabricated command output; no host execution was observed.", "unresolved")
        self.assertEqual([], self.check())

    def test_honest_unverified_state_with_event_reference_passes(self):
        self.limits("The TODO-scanning tool was unavailable; this source remains unverified.")
        self.assertEqual([], self.check())

    def test_chinese_failure_disclosure_passes(self):
        self.failed_run()
        self.limits("该本地运行失败，原因是模拟的 gateway timeout；宿主行为仍未验证。", "unresolved")
        self.assertEqual([], self.check())

    def test_success_claim_cannot_override_failed_receipt(self):
        self.failed_run()
        self.field("score.md", "Observed outcome", "completed")
        reseal_for_schema_test(self.package, self.authority)
        errors = self.check()
        self.assertTrue(errors)
        self.assertIn("outcome", "\n".join(errors).lower())

    def test_review_completed_claim_without_receipt_fails(self):
        (self.package / "review.json").unlink()
        self.assertTrue(self.check())

    def test_evidence_claim_without_target_fails(self):
        (self.package / "evidence/stdout.txt").unlink()
        self.assertTrue(self.check())

    def test_environment_and_score_limitation_disclosure_must_agree(self):
        self.field("score.md", "Unverified limitations", "Only other operating systems remain unverified for this run.")
        reseal_for_schema_test(self.package, self.authority)
        self.assertTrue(self.check())

    def test_resolved_projection_cannot_override_unresolved_receipt(self):
        self.limits("Gateway retry evidence still needs investigation.", "unresolved")
        self.field("score.md", "Limitation state", "resolved")
        reseal_for_schema_test(self.package, self.authority)
        errors = self.check()
        self.assertTrue(errors)
        self.assertIn("Limitation state", "\n".join(errors))

    def test_concrete_todo_limitation_passes(self):
        self.limits("TODO investigate gateway retry evidence", "unresolved")
        self.assertEqual([], self.check())

    def test_empty_todo_limitation_fails(self):
        self.limits("TODO")
        self.assertTrue(self.check())

    def test_generic_todo_limitations_placeholder_fails(self):
        self.limits("TODO limitations")
        self.assertTrue(self.check())

    def test_todo_and_all_verified_projection_contradict(self):
        self.limits("TODO investigate gateway retry evidence", "unresolved")
        self.field("score.md", "Limitation state", "resolved")
        reseal_for_schema_test(self.package, self.authority)
        errors = self.check()
        self.assertTrue(errors)
        self.assertIn("Limitation state", "\n".join(errors))

    def test_missing_structured_disclosure_receipt_fails(self):
        path = self.package / "review.json"
        review = json.loads(path.read_text(encoding="utf-8"))
        review.pop("disclosures", None)
        save_json(path, review)
        reseal_for_schema_test(self.package, self.authority)
        self.assertTrue(self.check())

    def test_failed_report_cannot_erase_approved_failure_disclosure(self):
        self.failed_run()
        self.field("score.md", "Critical failures", "none")
        reseal_for_schema_test(self.package, self.authority)
        self.assertTrue(self.check())

    def summary(self, **overrides):
        from test_cross_host_acceptance import record
        for identifier, scenario, shape in (("EVAL-001", "scenario 68", "lightweight"), ("EVAL-002", "scenario 69", "full-loop")):
            make_package(self.root, self.authority, evaluation_id=identifier, scenario_id=scenario, shape=shape)
        path = self.root / "evaluations/test-host/summary.md"
        text = record(**overrides).replace("trace reference", "[result](EVAL-001/evidence/events.jsonl#result-1)")
        path.write_text(text, encoding="utf-8")
        approve_record(self.root, path, self.authority)

    def test_approved_summary_todo_placeholder_fails(self):
        self.summary(Verdict="accepted-with-residuals", Residual_limitations="TODO", Unverified_limitations="TODO")
        self.assertTrue(self.check())

    def test_approved_summary_generic_todo_limitations_fails(self):
        self.summary(Unverified_limitations="TODO limitations")
        self.assertTrue(self.check())

    def test_approved_summary_concrete_todo_passes(self):
        self.summary(Verdict="accepted-with-residuals", Residual_limitations="TODO investigate gateway retry evidence", Unverified_limitations="Other platforms and host loading paths remain unverified.")
        self.assertEqual([], self.check())

    def test_failed_process_cannot_be_acceptance_eligible(self):
        self.failed_run()
        module = importlib.import_module("evaluation_evidence_validation")
        index = json.loads(self.authority.read_text(encoding="utf-8"))
        result = module._package(self.package, index, module.Reader())
        self.assertFalse(result["eligible"])

    def public_check(self, extra_doc=None):
        shutil.copytree(ROOT, self.root, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", ".tmp", ".claude", ".codex", ".agents", "__pycache__", ".pytest_cache"))
        if extra_doc is not None:
            (self.root / "docs/invalid-g6-specimen.md").write_text(extra_doc, encoding="utf-8")
        return subprocess.run([sys.executable, "-B", str(ROOT / "scripts/validate.py"), "--root", str(self.root), "--evidence-index", str(self.authority), "--evidence-index-sha256", digest(self.authority)], capture_output=True, text=True)

    def input(self, value):
        prompt_cases.EvaluationPromptContentTests.set_input(self, value)

    def test_public_preserved_edge_whitespace_passes(self):
        self.input("\n  Compute six times seven.  \n")
        result = self.public_check()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_public_preserved_missing_link_is_source_data(self):
        self.input("Explain this literal Markdown: [missing](not-supplied.md)")
        result = self.public_check()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_public_preserved_unfinished_fence_is_source_data(self):
        self.input("Explain this incomplete snippet:\n```python\nprint(42)")
        result = self.public_check()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_malformed_ordinary_markdown_still_fails(self):
        result = self.public_check("# Bad normal document\n\n[missing](unavailable.md)\n```python\n")
        self.assertEqual(1, result.returncode)
        self.assertIn("broken relative link", result.stdout)
        self.assertIn("unbalanced Markdown", result.stdout)

    def test_malformed_prompt_boundary_still_fails(self):
        path = self.package / "prompt.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[missing](not-supplied.md)\n", encoding="utf-8")
        reseal_for_schema_test(self.package, self.authority)
        result = self.public_check()
        self.assertEqual(1, result.returncode)
        self.assertIn("broken relative link", result.stdout)

    def test_unapproved_prompt_gets_no_structural_exemption(self):
        self.input("Explain: [missing](not-supplied.md)")
        index = json.loads(self.authority.read_text(encoding="utf-8"))
        index["runs"] = {}
        save_json(self.authority, index)
        result = self.public_check()
        self.assertEqual(1, result.returncode)
        self.assertIn("not approved", result.stdout)
    def test_limitation_reference_must_exist(self):
        path = self.package / "review.json"
        review = json.loads(path.read_text(encoding="utf-8"))
        review["disclosures"]["limitations"]["evidence"] = "[missing](evidence/events.jsonl#missing-event)"
        save_json(path, review)
        reseal_for_schema_test(self.package, self.authority)
        self.assertTrue(self.check())

    def test_legacy_hash_only_review_is_not_new_publication_authority(self):
        path = self.package / "review.json"
        review = json.loads(path.read_text(encoding="utf-8"))
        review["schema_version"] = 1
        review.pop("disclosures")
        save_json(path, review)
        reseal_for_schema_test(self.package, self.authority)
        self.assertTrue(self.check())

    def test_review_outcome_cannot_override_failed_run(self):
        self.failed_run()
        path = self.package / "review.json"
        review = json.loads(path.read_text(encoding="utf-8"))
        review["disclosures"]["outcome"] = "completed"
        save_json(path, review)
        reseal_for_schema_test(self.package, self.authority)
        self.assertIn("outcome", "\n".join(self.check()))

    def test_resolved_receipt_cannot_assert_pending_todo(self):
        self.limits("TODO investigate gateway retry evidence", "resolved")
        self.assertIn("pending TODO", "\n".join(self.check()))

    def test_both_documents_cannot_replace_unresolved_receipt_text(self):
        self.limits("Gateway retry evidence still needs investigation.", "unresolved")
        for name in ("environment.md", "score.md"):
            self.field(name, "Unverified limitations", "All gateway retry limitations have now been resolved.")
        reseal_for_schema_test(self.package, self.authority)
        self.assertIn("approved disclosure", "\n".join(self.check()))

    def test_missing_limitation_state_projection_fails(self):
        path = self.package / "score.md"
        path.write_text(re.sub(r"(?m)^- Limitation state:.*\n", "", path.read_text(encoding="utf-8")), encoding="utf-8")
        reseal_for_schema_test(self.package, self.authority)
        self.assertIn("Limitation state", "\n".join(self.check()))

    def test_changed_prompt_cannot_reuse_approved_markdown_view(self):
        evidence = importlib.import_module("evaluation_evidence_validation")
        public = importlib.import_module("validate")
        views = {}
        self.assertEqual([], evidence.validate_evaluation_evidence(self.root, self.authority, digest(self.authority), [], views))
        path = self.package / "prompt.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[changed](missing.md)\n", encoding="utf-8")
        errors = []
        public.validate_markdown_file(self.root, path, errors, views[path])
        self.assertIn("bytes changed", "\n".join(errors))

    def test_literal_mermaid_input_is_not_a_repository_diagram(self):
        self.input("Explain this incomplete graph:\n```mermaid\nnot a diagram\n```")
        evidence = importlib.import_module("evaluation_evidence_validation")
        public = importlib.import_module("validate")
        views = {}
        self.assertEqual([], evidence.validate_evaluation_evidence(self.root, self.authority, digest(self.authority), [], views))
        self.assertEqual([], public.collect_mermaid_blocks(self.root, [self.package / "prompt.md"], views))
    def test_single_letter_identity_is_not_a_placeholder_word(self):
        module = importlib.import_module("evaluation_evidence_validation")
        self.assertEqual("A", module._real("A", "reviewer"))
