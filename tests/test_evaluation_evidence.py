from pathlib import Path
import importlib
import json
import shutil
import sys
import tempfile
import unittest

from evaluation_evidence_fixture import make_package, reseal_for_schema_test, save_json, digest, approve_record

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class EvaluationEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        shutil.copytree(ROOT / "evaluations", self.root / "evaluations")
        self.authority = Path(self.temp.name) / "operator" / "approved.json"
        self.package = make_package(self.root, self.authority)

    def check(self, path="default", pin="default"):
        self.assertTrue((ROOT / "scripts/evaluation_evidence_validation.py").exists(), "evidence validator must exist")
        module = importlib.import_module("evaluation_evidence_validation")
        authority = self.authority if path == "default" else path
        expected = digest(authority) if pin == "default" and authority else (None if pin == "default" else pin)
        return module.validate_evaluation_evidence(self.root, authority, expected, [])

    def mutate(self, name, old, new):
        file = self.package / name
        text = file.read_text(encoding="utf-8")
        self.assertIn(old, text)
        file.write_text(text.replace(old, new, 1), encoding="utf-8")
        reseal_for_schema_test(self.package, self.authority)

    def rejected(self, token):
        errors = self.check()
        self.assertTrue(errors)
        self.assertIn(token.casefold(), "\n".join(errors).casefold())

    def test_complete_locally_observed_specimen_passes(self):
        self.assertEqual(b"42", (self.package / "evidence/stdout.txt").read_bytes().strip())
        self.assertEqual([], self.check())

    def test_no_trusted_index_is_not_provenance(self):
        self.assertTrue(self.check(path=None))

    def test_wrong_trusted_index_pin_fails(self):
        self.assertTrue(self.check(pin="0" * 64))

    def test_package_supplied_trust_index_is_rejected(self):
        local = self.package / "self-approved.json"
        shutil.copyfile(self.authority, local)
        self.assertTrue(self.check(path=local, pin=digest(local)))

    def test_unapproved_coherent_run_is_rejected(self):
        index = json.loads(self.authority.read_text(encoding="utf-8"))
        index["runs"] = {}
        save_json(self.authority, index)
        self.rejected("not approved")

    def test_missing_scenario_label_fails_even_with_approved_bytes(self):
        self.mutate("prompt.md", "- Scenario ID: scenario 68\n", "")
        self.rejected("Scenario ID")

    def test_cross_artifact_scenario_mismatch_fails(self):
        self.mutate("environment.md", "scenario 68", "scenario 69")
        self.rejected("Scenario ID")

    def test_missing_trace_evidence_links_fails(self):
        self.mutate("trace.md", "- Evidence links: [observed result](evidence/events.jsonl#result-1)\n", "")
        self.rejected("Evidence links")

    def test_missing_score_evidence_links_fails(self):
        self.mutate("score.md", "- Evidence links: [observed result](evidence/events.jsonl#result-1)\n", "")
        self.rejected("Evidence links")

    def test_missing_reviewer_decision_fails(self):
        self.mutate("score.md", "- Reviewer decision: accept\n", "")
        self.rejected("Reviewer decision")

    def test_missing_unverified_limitations_fails(self):
        text = (self.package / "environment.md").read_text(encoding="utf-8")
        line = next(line for line in text.splitlines() if line.startswith("- Unverified limitations:"))
        self.mutate("environment.md", line, "")
        self.rejected("Unverified limitations")

    def test_placeholder_disclosure_fails_even_if_pinned(self):
        text = (self.package / "score.md").read_text(encoding="utf-8")
        line = next(line for line in text.splitlines() if line.startswith("- Unverified limitations:"))
        self.mutate("score.md", line, "- Unverified limitations: TODO fabricated placeholder")
        self.rejected("placeholder")

    def test_missing_raw_evidence_fails(self):
        (self.package / "evidence/stdout.txt").unlink()
        self.rejected("evidence")

    def test_changed_raw_evidence_fails(self):
        (self.package / "evidence/stdout.txt").write_text("made up output")
        self.rejected("digest")

    def test_unknown_trace_event_fails(self):
        self.mutate("score.md", "events.jsonl#result-1", "events.jsonl#missing-event")
        self.rejected("event")

    def test_external_evidence_url_is_not_followed(self):
        self.mutate("score.md", "evidence/events.jsonl#result-1", "https://example.invalid/trace")
        self.rejected("local")

    def test_evidence_path_escape_is_rejected(self):
        self.mutate("score.md", "evidence/events.jsonl#result-1", "../../outside.jsonl#result-1")
        self.rejected("package")

    def test_reviewer_must_differ_from_trace_author(self):
        self.mutate("score.md", "- Reviewer: reviewer-b", "- Reviewer: evaluator-a")
        review = json.loads((self.package / "review.json").read_text(encoding="utf-8"))
        review["reviewer"] = "evaluator-a"
        save_json(self.package / "review.json", review)
        reseal_for_schema_test(self.package, self.authority)
        self.rejected("reviewer")

    def test_review_must_reference_this_run(self):
        review = json.loads((self.package / "review.json").read_text(encoding="utf-8"))
        review["run_id"] = "RUN-OTHER"
        save_json(self.package / "review.json", review)
        reseal_for_schema_test(self.package, self.authority)
        self.rejected("run")

    def test_unapproved_review_modification_fails(self):
        self.mutate("score.md", "- Reviewer decision: accept", "- Reviewer decision: reject")
        # Restore an incorrect operator pin for the changed review, not a fake default trust.
        index = json.loads(self.authority.read_text(encoding="utf-8"))
        next(iter(index["runs"].values()))["review_sha256"] = "0" * 64
        save_json(self.authority, index)
        self.rejected("approved")

    def test_b7_missing_evidence_integrity_dimension_fails(self):
        self.mutate("score.md", "| Evidence integrity across agents | 3 | [observed result](evidence/events.jsonl#result-1) |\n", "")
        self.rejected("Evidence integrity across agents")

    def test_b7_missing_authority_dimension_fails(self):
        self.mutate("score.md", "| Authority continuity | 3 | [observed result](evidence/events.jsonl#result-1) |\n", "")
        self.rejected("Authority continuity")

    def test_b7_score_range_is_enforced(self):
        self.mutate("score.md", "| Authority continuity | 3 |", "| Authority continuity | 9 |")
        self.rejected("score")

    def test_b7_score_requires_event_evidence(self):
        self.mutate("score.md", "| Authority continuity | 3 | [observed result](evidence/events.jsonl#result-1) |", "| Authority continuity | 3 | |")
        self.rejected("evidence")

    def test_total_is_recomputed(self):
        self.mutate("score.md", "- Total: 30", "- Total: 29")
        self.rejected("Total")

    def test_duplicate_fields_are_not_first_match_wins(self):
        self.mutate("environment.md", "- Scenario ID: scenario 68", "- Scenario ID: scenario 68\n- Scenario ID: scenario 69")
        self.rejected("duplicate")

    def test_duplicate_json_keys_are_rejected(self):
        file = self.package / "run.json"
        file.write_text('{"schema_version":1,"schema_version":1}')
        self.rejected("duplicate")

    def test_template_field_presence_is_enforced(self):
        file = self.root / "evaluations/templates/score.md"
        file.write_text(file.read_text(encoding="utf-8").replace("- Reviewer decision:\n", ""))
        self.rejected("Reviewer decision")

    def test_template_b7_rows_are_enforced(self):
        file = self.root / "evaluations/templates/score.md"
        file.write_text(file.read_text(encoding="utf-8").replace("| Authority continuity |  |  |\n", ""))
        self.rejected("Authority continuity")

    def test_historical_evidence_cannot_be_silently_rewritten(self):
        file = self.root / "evaluations/claude-code/EVAL-001/environment.md"
        file.write_text(file.read_text(encoding="utf-8") + "\nUnapproved revised history.\n")
        self.rejected("historical")

    def test_unregistered_files_cannot_hide_an_evaluation(self):
        file = self.root / "evaluations/hidden/renamed.txt"
        file.parent.mkdir()
        file.write_text("Evaluation ID: FAKE\nclaimed complete evaluation")
        self.rejected("unregistered")


    def summary(self, **overrides):
        from test_cross_host_acceptance import record
        for identifier, scenario, shape in (("EVAL-001", "scenario 68", "lightweight"), ("EVAL-002", "scenario 69", "full-loop")):
            make_package(self.root, self.authority, evaluation_id=identifier, scenario_id=scenario, shape=shape)
        path = self.root / "evaluations/test-host/host-acceptance.md"
        path.write_text(record(**overrides).replace("trace reference", "[trace](EVAL-001/evidence/events.jsonl#result-1)"), encoding="utf-8")
        approve_record(self.root, path, self.authority)
        return path

    def test_approved_summary_of_consistent_runs_passes(self):
        self.summary()
        self.assertEqual([], self.check())

    def test_accepted_summary_requires_separate_approval(self):
        self.summary()
        index = json.loads(self.authority.read_text(encoding="utf-8"))
        index["records"] = {}
        save_json(self.authority, index)
        self.rejected("record is not approved")

    def test_summary_scenario_set_cannot_be_fabricated(self):
        self.summary(Scenario_IDs="scenario 68, scenario 999")
        self.rejected("Scenario IDs")

    def test_historical_runs_cannot_be_promoted_by_summary(self):
        from test_cross_host_acceptance import record
        path = self.root / "evaluations/claude-code/new-acceptance.md"
        path.write_text(record(), encoding="utf-8")
        approve_record(self.root, path, self.authority)
        self.rejected("historical evaluation")

    def test_summary_minimum_is_recomputed(self):
        self.summary(Lowest_critical_rubric_score="2")
        self.rejected("observed minimum")

    def test_b7_low_score_cannot_back_accepted_summary(self):
        self.summary()
        package = self.root / "evaluations/test-host/EVAL-001"
        score = package / "score.md"
        score.write_text(score.read_text(encoding="utf-8").replace("| Authority continuity | 3 |", "| Authority continuity | 1 |").replace("- Total: 30", "- Total: 28"), encoding="utf-8")
        reseal_for_schema_test(package, self.authority)
        self.rejected("not eligible")

    def test_summary_cannot_reference_unlisted_run_event(self):
        path = self.summary()
        path.write_text(path.read_text(encoding="utf-8").replace("EVAL-001/evidence/events.jsonl", "EVAL-TEST-001/evidence/events.jsonl"), encoding="utf-8")
        approve_record(self.root, path, self.authority)
        self.rejected("referenced run event")

    def test_summary_cannot_discard_review_residuals(self):
        self.summary()
        package = self.root / "evaluations/test-host/EVAL-001"
        score = package / "score.md"
        score.write_text(score.read_text(encoding="utf-8").replace("- Reviewer decision: accept\n", "- Reviewer decision: accept-with-residuals\n"), encoding="utf-8")
        review = json.loads((package / "review.json").read_text(encoding="utf-8"))
        review["decision"] = "accept-with-residuals"
        save_json(package / "review.json", review)
        reseal_for_schema_test(package, self.authority)
        self.rejected("discard reviewer residuals")

    def test_hash_and_parser_use_the_same_observed_bytes(self):
        self.check()
        module = importlib.import_module("evaluation_evidence_validation")
        reader = module.Reader()
        file = self.package / "evidence/stdout.txt"
        original_hash = reader.digest(file)
        original_text = reader.text(file)
        file.write_text("changed after observed snapshot", encoding="utf-8")
        self.assertEqual(original_hash, reader.digest(file))
        self.assertEqual(original_text, reader.text(file))
        self.assertNotEqual(original_hash, module.Reader().digest(file))
        self.rejected("digest")


    def test_exact_input_cannot_hide_mismatch_elsewhere(self):
        self.mutate("prompt.md", "## Exact User Input\n\nCompute six times seven locally.\n\n## Input Boundary", "## Exact User Input\n\nA different request.\n\n## Input Boundary\n\nOriginal definition says: Compute six times seven locally.")
        self.rejected("input")

    def test_empty_score_caps_are_not_disclosure(self):
        self.mutate("score.md", "- Applied score caps: none", "- Applied score caps:")
        self.rejected("score caps")

    def test_placeholder_critical_failure_disclosure_fails(self):
        self.mutate("score.md", "- Critical failures: none", "- Critical failures: TODO")
        self.rejected("Critical failures")

    def test_principal_whitespace_cannot_hide_self_review(self):
        run = json.loads((self.package / "run.json").read_text(encoding="utf-8"))
        run["trace_author"] = "reviewer-b "
        save_json(self.package / "run.json", run)
        reseal_for_schema_test(self.package, self.authority)
        self.rejected("trace_author")


    def test_captured_input_must_match_declared_scenario(self):
        file = self.package / "evidence/input.txt"
        file.write_text("A different actual input.\n", encoding="utf-8")
        run = json.loads((self.package / "run.json").read_text(encoding="utf-8"))
        run["evidence"]["evidence/input.txt"] = digest(file)
        events_file = self.package / "evidence/events.jsonl"
        events = [json.loads(line) for line in events_file.read_text(encoding="utf-8").splitlines()]
        events[0]["sha256"] = digest(file)
        events_file.write_text("".join(json.dumps(event, sort_keys=True) + "\n" for event in events), encoding="utf-8")
        run["trace_sha256"] = digest(events_file)
        save_json(self.package / "run.json", run)
        reseal_for_schema_test(self.package, self.authority)
        self.rejected("captured input")


    def test_public_tab_verdict_cannot_bypass_approval(self):
        import subprocess
        from test_cross_host_acceptance import record
        shutil.copytree(ROOT, self.root, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", ".tmp", ".claude", ".codex", ".agents", "__pycache__", ".pytest_cache"))
        path = self.root / "evaluations/test-host/bypass.md"
        path.write_text(record().replace("- Verdict: accepted", "-\tVerdict: accepted"), encoding="utf-8")
        result = subprocess.run([sys.executable, str(ROOT / "scripts/validate.py"), "--root", str(self.root), "--evidence-index", str(self.authority), "--evidence-index-sha256", digest(self.authority)], capture_output=True, text=True)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("record is not approved", result.stdout + result.stderr)

    def test_record_cannot_extend_historical_package(self):
        from test_cross_host_acceptance import record, UNVERIFIED_STUB
        path = self.root / "evaluations/claude-code/EVAL-001/extra-record.md"
        path.write_text(record(**UNVERIFIED_STUB), encoding="utf-8")
        self.rejected("historical package")

    def test_environment_context_cannot_be_omitted(self):
        for field in ("Available tools and state", "Granted authority", "Material environment constraints"):
            with self.subTest(field=field):
                file = self.package / "environment.md"
                original = file.read_text(encoding="utf-8")
                file.write_text("\n".join(line for line in original.splitlines() if not line.startswith("- " + field + ":")) + "\n", encoding="utf-8")
                reseal_for_schema_test(self.package, self.authority)
                self.rejected(field)
                file.write_text(original, encoding="utf-8")
                reseal_for_schema_test(self.package, self.authority)

    def test_environment_context_cannot_be_placeholder(self):
        self.mutate("environment.md", "- Granted authority: local test execution only", "- Granted authority: TODO")
        self.rejected("Granted authority")
