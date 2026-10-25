"""Public-entry regressions with synthetic Git-backed RC evidence."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from evaluation_evidence_fixture import approve_record, digest, make_package, reseal_for_schema_test, save_json
from option_b_fixture import initialize, rc_package, summary, git, REFERENCE

ROOT = Path(__file__).resolve().parents[1]


class OptionBPublicEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT / ".tmp").mkdir(exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(dir=ROOT / ".tmp")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.snapshot = Path(cls.temp.name) / "snapshot"
        cls.boundary = initialize(cls.snapshot, ROOT)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / ".tmp")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        shutil.copytree(self.snapshot, self.root)
        self.authority = Path(self.temp.name) / "operator/approved.json"

    def check(self):
        command = [sys.executable, str(self.root / "scripts/validate.py"), "--root", str(self.root)]
        if self.authority.exists():
            command += ["--evidence-index", str(self.authority), "--evidence-index-sha256", digest(self.authority)]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertNotIn("Traceback", result.stdout + result.stderr)
        return result.returncode, result.stdout + result.stderr

    def reject(self, token):
        status, output = self.check()
        self.assertNotEqual(0, status, output)
        self.assertIn(token.casefold(), output.casefold())

    def package(self, **kwargs):
        return rc_package(self.root, self.authority, self.boundary, **kwargs)

    def mutate_run(self, package, change):
        path = package / "run.json"
        run = json.loads(path.read_text(encoding="utf-8"))
        change(run)
        save_json(path, run)
        reseal_for_schema_test(package, self.authority)

    def test_finalized_designation_without_arms_is_structurally_valid(self):
        status, output = self.check()
        self.assertEqual(0, status, output)

    def test_reference_summary_accepts_descendant_boundary_and_config_alias(self):
        packages = [self.package(number=i) for i in (1, 2)]
        summary(self.root, self.authority, packages)
        status, output = self.check()
        self.assertEqual(0, status, output)

    def test_candidate_summary_does_not_claim_reference_role(self):
        packages = [self.package(number=i, role="candidate", host="Claude Code") for i in (1, 2)]
        summary(self.root, self.authority, packages, role="candidate", host="Claude Code")
        status, output = self.check()
        self.assertEqual(0, status, output)

    def test_candidate_summary_cannot_change_rc_reference_host(self):
        packages = [self.package(number=i, role="candidate", host="Claude Code") for i in (1, 2)]
        path = summary(self.root, self.authority, packages, role="candidate", host="Claude Code")
        path.write_text(path.read_text(encoding="utf-8").replace("- Reference Host: Codex", "- Reference Host: Claude Code"), encoding="utf-8")
        approve_record(self.root, path, self.authority)
        self.reject("record/run Reference Host mismatch")

    def test_nested_package_resolves_repository_root(self):
        self.package(parent="option-b-test/nested")
        status, output = self.check()
        self.assertEqual(0, status, output)

    def test_unsupported_run_schema_version_is_rejected(self):
        package = make_package(self.root, self.authority)
        self.mutate_run(package, lambda run: run.update(schema_version=3))
        self.reject("run schema version invalid")

    def test_malformed_run_object_reports_error_without_crashing(self):
        package = self.package()
        save_json(package / "run.json", [])
        self.reject("run schema")

    def test_rc_summary_cannot_use_non_rc_receipts(self):
        packages = [make_package(self.root, self.authority, evaluation_id=f"EVAL-RC-{i:03}",
            scenario_id=f"rc-scenario-{i}", shape="lightweight" if i == 1 else "full-loop", host="Codex",
            host_version="fixture-host-1", model="fixture-upstream-model", commit=self.boundary["baseline"],
            loading_mode="explicit fixture load", parent="option-b-test") for i in (1, 2)]
        summary(self.root, self.authority, packages)
        self.reject("requires version-2 RC receipts")

    def test_rc_summary_must_match_receipt_designation_digest(self):
        packages = [self.package(number=i) for i in (1, 2)]
        path = summary(self.root, self.authority, packages)
        path.write_text(path.read_text(encoding="utf-8").replace(digest(self.root / REFERENCE), "0" * 64), encoding="utf-8")
        approve_record(self.root, path, self.authority)
        self.reject("record/run Reference designation SHA-256 mismatch")

    def test_rc_summary_requires_all_binding_fields(self):
        packages = [self.package(number=i) for i in (1, 2)]
        path = summary(self.root, self.authority, packages)
        path.write_text(path.read_text(encoding="utf-8").replace("- Reference designation ID: RC1-REF-CODEX-20261024\n", ""), encoding="utf-8")
        approve_record(self.root, path, self.authority)
        self.reject("Reference designation ID")

    def test_reference_receipt_cannot_claim_other_host(self):
        package = self.package()
        self.mutate_run(package, lambda run: run.update(host="Claude Code"))
        self.reject("not the designated Reference Host")

    def test_finalized_combination_mismatch_is_rejected(self):
        package = self.package()
        self.mutate_run(package, lambda run: run.update(loading_mode="different load"))
        self.reject("designation Skill loading mode mismatch")

    def test_unknown_observed_identity_blocks_formal_run(self):
        package = self.package()
        self.mutate_run(package, lambda run: run["runtime_identity"]["observed"].update(model="unknown"))
        self.reject("observed model")

    def test_missing_host_version_observation_is_rejected(self):
        package = self.package()
        self.mutate_run(package, lambda run: run["runtime_identity"]["event_ids"].pop("host_version"))
        self.reject("observation events")

    def test_model_observation_must_match_artifact_contents(self):
        package = self.package(role="candidate", host="Claude Code")
        def change(run):
            run["model"] = "different-upstream"
            run["runtime_identity"]["observed"]["model"] = "different-upstream"
        self.mutate_run(package, change)
        self.reject("identity observation")

    def test_malformed_nested_identity_reports_error(self):
        package = self.package()
        self.mutate_run(package, lambda run: run["runtime_identity"].update(observed=[]))
        self.reject("observed fields invalid")

    def test_formal_run_requires_pre_arm_finalization(self):
        package = self.package()
        self.mutate_run(package, lambda run: run.update(started_at="2030-01-02T07:00:00+00:00"))
        self.reject("before the formal arm")

    def test_fabricated_git_boundary_is_rejected(self):
        package = self.package()
        self.mutate_run(package, lambda run: run["rc_binding"].update(effective_successor_commit="c" * 40))
        self.reject("Git")

    def test_wrong_effective_tree_is_rejected(self):
        package = self.package()
        self.mutate_run(package, lambda run: run["rc_binding"].update(effective_successor_tree="d" * 40))
        self.reject("tree")

    def test_later_commit_cannot_be_mislabelled_first_effective_boundary(self):
        package = self.package()
        self.mutate_run(package, lambda run: run["rc_binding"].update(
            effective_successor_commit=self.boundary["baseline"], effective_successor_tree=self.boundary["tree"]))
        self.reject("first synchronized")

    def test_git_replacement_cannot_forge_successor_ancestry(self):
        unrelated = git(self.root, "commit-tree", self.boundary["effective_tree"], "-m", "synthetic unrelated root")
        replacement = git(self.root, "commit-tree", self.boundary["tree"], "-p", unrelated,
                          "-m", "synthetic replaced baseline parent", date="2030-01-01T09:00:00+00:00")
        git(self.root, "replace", self.boundary["baseline"], replacement)
        package = self.package()
        self.mutate_run(package, lambda run: run["rc_binding"].update(effective_successor_commit=unrelated))
        self.reject("Git")

    def test_reference_choice_cannot_be_changed_for_same_rc(self):
        path = self.root / REFERENCE
        text = path.read_text(encoding="utf-8").replace("- Reference Host: Codex", "- Reference Host: Claude Code").replace(
            "- Other eligible Host: Claude Code", "- Other eligible Host: Codex")
        path.write_text(text, encoding="utf-8")
        git(self.root, "add", REFERENCE)
        git(self.root, "commit", "-m", "synthetic forbidden switch")
        self.reject("Codex")

    def test_designation_cannot_be_uncommitted_or_replaced_after_pin(self):
        package = self.package()
        path = self.root / REFERENCE
        path.write_text(path.read_text(encoding="utf-8").replace("fixture-host-1", "changed-host"), encoding="utf-8")
        self.mutate_run(package, lambda run: run["rc_binding"].update(designation_sha256=digest(path)))
        self.reject("committed designation")

    def test_observation_rejects_configuration_only_basis(self):
        package = self.package()
        path = package / "evidence/runtime.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["basis"] = "configured-alias"
        save_json(path, value)
        self.repin_identity(package)
        self.reject("actual-runtime-observation")

    def repin_identity(self, package):
        run = json.loads((package / "run.json").read_text(encoding="utf-8"))
        path = package / "evidence/runtime.json"
        run["evidence"]["evidence/runtime.json"] = digest(path)
        trace = package / run["trace_path"]
        events = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]
        events[-1]["sha256"] = digest(path)
        trace.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
        run["trace_sha256"] = digest(trace)
        save_json(package / "run.json", run)
        reseal_for_schema_test(package, self.authority)

    def test_observation_source_digest_is_enforced(self):
        package = self.package()
        path = package / "evidence/runtime.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["source_sha256"] = "0" * 64
        save_json(path, value)
        self.repin_identity(package)
        self.reject("observation source")

    def test_unhashable_identity_event_id_reports_schema_error(self):
        package = self.package()
        self.mutate_run(package, lambda run: run["runtime_identity"]["event_ids"].update(model=[]))
        self.reject("observation event")

    def test_non_string_git_boundary_reports_schema_error(self):
        package = self.package()
        self.mutate_run(package, lambda run: run["rc_binding"].update(designation_commit=[]))
        self.reject("Git SHA")

    def test_wrong_baseline_cannot_use_reference_designation(self):
        package = self.package()
        self.mutate_run(package, lambda run: run["rc_binding"].update(run_tree=self.boundary["effective_tree"]))
        self.reject("designation RC baseline tree mismatch")

    def test_configuration_declaration_must_match_finalized_combination(self):
        package = self.package()
        self.mutate_run(package, lambda run: run["runtime_identity"]["configured"].update(model="different-alias"))
        self.reject("designation Configured model mismatch")

    def test_environment_rc_projection_cannot_contradict_receipt(self):
        package = self.package()
        path = package / "environment.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("- RC version: v1.0.0-rc1", "- RC version: v9.9.9-rc99")
        path.write_text(text, encoding="utf-8")
        reseal_for_schema_test(package, self.authority)
        self.reject("environment RC version mismatch")

    def test_unversioned_summary_cannot_hide_rc_reference_fields(self):
        packages = [self.package(number=i) for i in (1, 2)]
        path = summary(self.root, self.authority, packages)
        path.write_text(path.read_text(encoding="utf-8").replace("- RC version: v1.0.0-rc1", "- RC version: none"), encoding="utf-8")
        approve_record(self.root, path, self.authority)
        self.reject("RC version")

    def select_later_rc(self, host="Claude Code"):
        path = self.root / REFERENCE
        text = path.read_text(encoding="utf-8").replace("v1.0.0-rc1", "v1.0.0-rc2").replace("RC1-REF-CODEX", "RC2-REF-CLAUDE")
        if host == "Claude Code":
            text = text.replace("- Reference Host: Codex", "- Reference Host: Claude Code").replace(
                "- Other eligible Host: Claude Code", "- Other eligible Host: Codex")
        path.write_text(text, encoding="utf-8")
        decision = self.root / "docs/release/rc-candidate-decision.md"
        decision.write_text(decision.read_text(encoding="utf-8").replace("v1.0.0-rc1", "v1.0.0-rc2").replace(
            "- Reference Host: Codex", "- Reference Host: " + host), encoding="utf-8")
        git(self.root, "add", REFERENCE, "docs/release/rc-candidate-decision.md")
        git(self.root, "commit", "-m", "synthetic new RC choice", date="2030-01-02T08:03:00+00:00")

    def test_future_rc_can_choose_claude_as_reference(self):
        self.select_later_rc()
        boundary = dict(self.boundary, designation_commit=git(self.root, "rev-parse", "HEAD"))
        package = rc_package(self.root, self.authority, boundary, host="Claude Code")
        self.mutate_run(package, lambda run: run["rc_binding"].update(rc_version="v1.0.0-rc2",
            designation_id="RC2-REF-CLAUDE-20261024", reference_host="Claude Code"))
        environment = package / "environment.md"
        environment.write_text(environment.read_text(encoding="utf-8").replace("v1.0.0-rc1", "v1.0.0-rc2").replace(
            "RC1-REF-CODEX", "RC2-REF-CLAUDE").replace("- Reference Host: Codex", "- Reference Host: Claude Code"), encoding="utf-8")
        reseal_for_schema_test(package, self.authority)
        status, output = self.check()
        self.assertEqual(0, status, output)

    def test_later_rc_does_not_invalidate_earlier_rc_snapshots(self):
        packages = [self.package(number=i) for i in (1, 2)]
        summary(self.root, self.authority, packages)
        self.select_later_rc()
        status, output = self.check()
        self.assertEqual(0, status, output)

    def test_finalized_combination_cannot_be_changed_for_same_rc(self):
        path = self.root / REFERENCE
        path.write_text(path.read_text(encoding="utf-8").replace("fixture-host-1", "changed-host"), encoding="utf-8")
        git(self.root, "add", REFERENCE)
        git(self.root, "commit", "-m", "synthetic changed finalized version", date="2030-01-02T08:04:00+00:00")
        boundary = dict(self.boundary, designation_commit=git(self.root, "rev-parse", "HEAD"))
        package = rc_package(self.root, self.authority, boundary)
        def change(run):
            run["host_version"] = "changed-host"
            run["runtime_identity"]["observed"]["host_version"] = "changed-host"
            run["rc_binding"]["designation_sha256"] = digest(path)
        self.mutate_run(package, change)
        for name in ("environment.md", "score.md"):
            doc = package / name
            doc.write_text(doc.read_text(encoding="utf-8").replace("fixture-host-1", "changed-host"), encoding="utf-8")
        observed = package / "evidence/runtime.json"
        payload = json.loads(observed.read_text(encoding="utf-8"))
        payload["identity"]["host_version"] = "changed-host"
        save_json(observed, payload)
        self.repin_identity(package)
        self.reject("finalized combination is immutable")
