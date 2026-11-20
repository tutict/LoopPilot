from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import behavior_validation
from evaluation_evidence_validation import codex_replication_lineage_errors, load_external_evidence_index_authority


PAIR_SPECS = (
    ("COD-RPL-EVAL-001-S43", "EVAL-001", "scenario 43", "Requested Skill Is Unavailable", "lightweight", "behavior", "explicit"),
    ("COD-RPL-EVAL-002-S68", "EVAL-002", "scenario 68", "Simple Change Uses Lightweight Mode", "lightweight", "behavior", "explicit"),
    ("COD-RPL-EVAL-003-S69", "EVAL-003", "scenario 69", "High-Risk Multi-Stage Work Uses Full Loop Mode", "full-loop", "behavior", "explicit"),
    ("COD-RPL-EVAL-004-ARM-A", "EVAL-004", "host-skill-loading-probe-arm-a", "Host Skill loading probe, explicit invocation", "lightweight", "loading-probe", "explicit"),
    ("COD-RPL-EVAL-004-ARM-B", "EVAL-004", "host-skill-loading-probe-arm-b", "Host Skill discovery/loading probe, implicit invocation", "lightweight", "loading-probe", "implicit"),
    ("COD-RPL-EVAL-005-FIXTURE-A", "EVAL-005", "phase14-lightweight-explicit", "Phase 14 Lightweight explicit fixture", "lightweight", "behavior", "explicit"),
    ("COD-RPL-EVAL-005-IMPLICIT", "EVAL-005", "phase14-implicit-activation", "Phase 14 implicit activation fixture", "lightweight", "behavior", "implicit"),
)


def replication_matrix_fixture(root: Path) -> dict:
    prompt_dir = root / "docs/evaluations/codex-replication-prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    pairs = []
    for index, (pair_id, source_id, scenario_id, title, shape, evidence_type, loaded_mode) in enumerate(PAIR_SPECS):
        prompt_path = f"docs/evaluations/codex-replication-prompts/{pair_id}.txt"
        prompt = f"Run the Codex replication task for {scenario_id}.\n"
        target = root / prompt_path
        target.write_text(prompt, encoding="utf-8", newline="\n")
        prompt_hash = hashlib.sha256(target.read_bytes()).hexdigest()
        first_eval = 20 + index * 2
        pairs.append({
            "pair_id": pair_id,
            "source_evaluation_id": source_id,
            "scenario_id": scenario_id,
            "scenario_title": title,
            "scenario_shape": shape,
            "evidence_type": evidence_type,
            "prompt_path": prompt_path,
            "prompt_sha256": prompt_hash,
            "control": {"evaluation_id": f"EVAL-{first_eval:03d}", "loading_mode": "not-loaded"},
            "skill_loaded": {"evaluation_id": f"EVAL-{first_eval + 1:03d}", "loading_mode": loaded_mode},
        })
    matrix = {
        "schema_version": 1,
        "kind": "codex-replication-matrix",
        "purpose": "Seven matched Codex replications; source EVAL identifiers are provenance only.",
        "retry_policy": {
            "max_retries": 2,
            "new_evaluation_id_and_run_id_per_retry": True,
            "retry_only_execution_infrastructure_incidents": True,
            "retain_every_failed_attempt": True,
        },
        "pairs": pairs,
        "current_evaluation_ids": {"LW-1": "EVAL-034", "FL-1": "EVAL-035", "FL-1R": "EVAL-036", "IMP-1": "EVAL-037"},
    }
    matrix_path = root / "docs/evaluations/codex-replication-matrix.json"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8", newline="\n")
    return matrix


def temporary_design_root() -> tuple[tempfile.TemporaryDirectory, Path]:
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    docs = root / "docs/evaluations"
    docs.mkdir(parents=True)
    for name in ("historical-replay-matrix.json", "current-acceptance-matrix.json"):
        shutil.copy2(ROOT / "docs/evaluations" / name, docs / name)
    replication_matrix_fixture(root)
    return temp, root


class CodexReplicationMatrixTests(unittest.TestCase):
    def test_codex_replication_matrix_has_seven_pairs_and_eighteen_unique_ids(self):
        path = ROOT / "docs/evaluations/codex-replication-matrix.json"
        self.assertTrue(path.is_file(), "Codex replication matrix must exist separately from Claude history")
        matrix = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual("codex-replication-matrix", matrix["kind"])
        self.assertEqual([], behavior_validation.validate_codex_replication_matrix(ROOT))
        self.assertEqual(7, len(matrix["pairs"]))
        self.assertEqual(5, sum(pair["evidence_type"] == "behavior" for pair in matrix["pairs"]))
        self.assertEqual(2, sum(pair["evidence_type"] == "loading-probe" for pair in matrix["pairs"]))
        pair_ids = [arm["evaluation_id"] for pair in matrix["pairs"] for arm in (pair["control"], pair["skill_loaded"])]
        current_ids = list(matrix["current_evaluation_ids"].values())
        self.assertEqual([f"EVAL-{n:03d}" for n in range(20, 34)], pair_ids)
        self.assertEqual([f"EVAL-{n:03d}" for n in range(34, 38)], current_ids)
        self.assertEqual(18, len(set(pair_ids + current_ids)))

    def test_codex_replication_prompts_are_pair_identical(self):
        path = ROOT / "docs/evaluations/codex-replication-matrix.json"
        self.assertTrue(path.is_file(), "Codex replication matrix must exist separately from Claude history")
        matrix = json.loads(path.read_text(encoding="utf-8"))
        for pair in matrix["pairs"]:
            prompt_path = ROOT / pair["prompt_path"]
            self.assertTrue(prompt_path.is_file())
            self.assertEqual(pair["prompt_sha256"], hashlib.sha256(prompt_path.read_bytes()).hexdigest())
            self.assertEqual(pair["control"]["loading_mode"], "not-loaded")
            self.assertIn(pair["skill_loaded"]["loading_mode"], {"explicit", "implicit"})

    def test_arm_b_implicit_probe_prompt_is_unprompted_and_trace_evidenced(self):
        matrix = json.loads((ROOT / "docs/evaluations/codex-replication-matrix.json").read_text(encoding="utf-8"))
        pair = next(item for item in matrix["pairs"] if item["pair_id"] == "COD-RPL-EVAL-004-ARM-B")
        prompt = (ROOT / pair["prompt_path"]).read_text(encoding="utf-8").casefold()
        for term in ("skill", "$loop-pilot", "trigger", "loading", "loaded", "implicit", "event", "trace", "observation"):
            self.assertNotIn(term, prompt)

        runbook = (ROOT / "docs/evaluations/codex-replication-runbook.md").read_text(encoding="utf-8").casefold()
        self.assertIn("actual public tool/session", runbook)
        self.assertIn("model claims alone do not prove loading", runbook)
    def test_codex_replication_matrix_rejects_prompt_path_escape(self):
        temp, root = temporary_design_root()
        self.addCleanup(temp.cleanup)
        path = root / "docs/evaluations/codex-replication-matrix.json"
        matrix = json.loads(path.read_text(encoding="utf-8"))
        pair = matrix["pairs"][0]
        escaped_prompt = root / "docs/evaluations/outside-prompt.txt"
        escaped_prompt.write_text("Prompt outside the dedicated pack.\n", encoding="utf-8")
        pair["prompt_path"] = "docs/evaluations/codex-replication-prompts/../outside-prompt.txt"
        pair["prompt_sha256"] = hashlib.sha256(escaped_prompt.read_bytes()).hexdigest()
        path.write_text(json.dumps(matrix), encoding="utf-8")

        errors = behavior_validation.validate_behavior_matrices(root)
        self.assertTrue(any("prompt path invalid" in error for error in errors), errors)
    def test_codex_replication_matrix_rejects_pair_scenario_identity_drift(self):
        temp, root = temporary_design_root()
        self.addCleanup(temp.cleanup)
        path = root / "docs/evaluations/codex-replication-matrix.json"
        matrix = json.loads(path.read_text(encoding="utf-8"))
        matrix["pairs"][0]["scenario_title"] = "A different approved-looking scenario"
        path.write_text(json.dumps(matrix), encoding="utf-8")

        errors = behavior_validation.validate_behavior_matrices(root)
        self.assertTrue(any("identity differs from the approved scenario seed" in error for error in errors), errors)
    def test_codex_replication_matrix_rejects_unsupported_loading_modes(self):
        temp, root = temporary_design_root()
        self.addCleanup(temp.cleanup)
        path = root / "docs/evaluations/codex-replication-matrix.json"
        matrix = json.loads(path.read_text(encoding="utf-8"))
        matrix["pairs"][3]["skill_loaded"]["loading_mode"] = "headless-discovery"
        path.write_text(json.dumps(matrix), encoding="utf-8")
        errors = behavior_validation.validate_behavior_matrices(root)
        self.assertTrue(any("loading_mode" in error or "loading mode" in error for error in errors), errors)

    def test_codex_replication_matrix_keeps_claude_identity_as_provenance_only(self):
        temp, root = temporary_design_root()
        self.addCleanup(temp.cleanup)
        path = root / "docs/evaluations/codex-replication-matrix.json"
        matrix = json.loads(path.read_text(encoding="utf-8"))
        matrix["pairs"][0]["original_combination"] = {
            "host": "Claude Code", "host_version": "2.1.220", "model": "claude-opus-5"
        }
        path.write_text(json.dumps(matrix), encoding="utf-8")
        errors = behavior_validation.validate_behavior_matrices(root)
        self.assertTrue(any("original_combination" in error or "host identity" in error for error in errors), errors)


class CodexReplicationLineageTests(unittest.TestCase):
    def test_replication_lineage_binds_codex_pair_and_prompt(self):
        matrix = json.loads((ROOT / behavior_validation.CODEX_REPLICATION_MATRIX_PATH).read_text(encoding="utf-8"))
        pair = matrix["pairs"][0]
        lineage = {
            "schema_version": 1,
            "kind": "codex-replication-lineage",
            "experiment_id": "codex-replacement-20261118",
            "pair_id": pair["pair_id"],
            "source_evaluation_id": pair["source_evaluation_id"],
            "scenario_id": pair["scenario_id"],
            "scenario_shape": pair["scenario_shape"],
            "arm": "skill_loaded",
            "loading_mode": pair["skill_loaded"]["loading_mode"],
            "prompt_sha256": pair["prompt_sha256"],
            "boundary_id": "BOUNDARY-CODEX-001",
            "attempt": 1,
            "retry_of": None,
            "retry_reason": None,
            "blind_review_id": "BLIND-codex-replacement-20261118-01-abcdef123456",
        }
        run = {
            "evaluation_id": pair["skill_loaded"]["evaluation_id"],
            "run_id": "RUN-EVAL-021",
            "scenario_id": pair["scenario_id"],
            "scenario_shape": pair["scenario_shape"],
            "loading_mode": pair["skill_loaded"]["loading_mode"],
            "host": "Codex",
            "host_version": "0.168.0",
            "model": "gpt-6.1-sol",
        }
        self.assertEqual([], codex_replication_lineage_errors(ROOT, lineage, run))

    def test_replication_lineage_rejects_claude_runtime_identity(self):
        matrix = json.loads((ROOT / behavior_validation.CODEX_REPLICATION_MATRIX_PATH).read_text(encoding="utf-8"))
        pair = matrix["pairs"][0]
        lineage = {
            "schema_version": 1,
            "kind": "codex-replication-lineage",
            "experiment_id": "codex-replacement-20261118",
            "pair_id": pair["pair_id"],
            "source_evaluation_id": pair["source_evaluation_id"],
            "scenario_id": pair["scenario_id"],
            "scenario_shape": pair["scenario_shape"],
            "arm": "control",
            "loading_mode": "not-loaded",
            "prompt_sha256": pair["prompt_sha256"],
            "boundary_id": "BOUNDARY-CODEX-001",
            "attempt": 1,
            "retry_of": None,
            "retry_reason": None,
            "blind_review_id": "BLIND-codex-replacement-20261118-01-abcdef123456",
        }
        run = {
            "evaluation_id": pair["control"]["evaluation_id"],
            "run_id": "RUN-EVAL-020",
            "scenario_id": pair["scenario_id"],
            "scenario_shape": pair["scenario_shape"],
            "loading_mode": "not-loaded",
            "host": "Claude Code",
            "host_version": "2.1.220",
            "model": "claude-opus-5",
        }
        errors = codex_replication_lineage_errors(ROOT, lineage, run)
        self.assertTrue(any("Codex" in error or "host" in error for error in errors), errors)

    def test_replication_lineage_rejects_pair_mode_or_prompt_mismatch(self):
        matrix = json.loads((ROOT / behavior_validation.CODEX_REPLICATION_MATRIX_PATH).read_text(encoding="utf-8"))
        pair = matrix["pairs"][0]
        lineage = {
            "schema_version": 1,
            "kind": "codex-replication-lineage",
            "experiment_id": "codex-replacement-20261118",
            "pair_id": pair["pair_id"],
            "source_evaluation_id": pair["source_evaluation_id"],
            "scenario_id": pair["scenario_id"],
            "scenario_shape": pair["scenario_shape"],
            "arm": "control",
            "loading_mode": "explicit",
            "prompt_sha256": "0" * 64,
            "boundary_id": "BOUNDARY-CODEX-001",
            "attempt": 1,
            "retry_of": None,
            "retry_reason": None,
            "blind_review_id": "BLIND-codex-replacement-20261118-01-abcdef123456",
        }
        run = {
            "evaluation_id": pair["control"]["evaluation_id"],
            "run_id": "RUN-EVAL-020",
            "scenario_id": pair["scenario_id"],
            "scenario_shape": pair["scenario_shape"],
            "loading_mode": "explicit",
            "host": "Codex",
            "host_version": "0.168.0",
            "model": "gpt-6.1-sol",
        }
        errors = codex_replication_lineage_errors(ROOT, lineage, run)
        self.assertTrue(any("loading_mode" in error or "prompt" in error for error in errors), errors)


class CodexReplicationAuthorityTests(unittest.TestCase):
    def _reviewer_gate(self, experiment_id):
        return {
            "schema_version": 1,
            "kind": "behavior-reviewer-readiness",
            "experiment_id": experiment_id,
            "operator_id": "operator-a",
            "operator_session_id": "session-a",
            "reviewer_operator_id": "reviewer-b",
            "reviewer_session_id": "session-b",
            "blind_review_confirmed": True,
            "readiness": "ready",
            "confirmed_at": "2026-11-18T00:00:00+08:00",
            "scope": "Codex replication packets and current formal arms",
        }

    def test_index_authority_requires_external_path_and_matching_pin(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name) / "repo"
        root.mkdir()
        authority_path = Path(temp.name) / "authority.json"
        payload = {
            "schema_version": 1,
            "kind": "codex-evidence-index-authority",
            "experiment_id": "codex-replacement-20261118",
            "operator_id": "operator-a",
            "evidence_index_path": str(Path(temp.name) / "approved.json"),
            "approved_at": "2026-11-18T00:00:00+08:00",
        }
        authority_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        expected = hashlib.sha256(authority_path.read_bytes()).hexdigest()
        loaded, errors = load_external_evidence_index_authority(root, authority_path, expected, payload["experiment_id"])
        self.assertEqual([], errors)
        self.assertEqual(payload, loaded)

        loaded, errors = load_external_evidence_index_authority(root, root / "inside.json", expected, payload["experiment_id"])
        self.assertTrue(errors)

    def test_index_authority_rejects_wrong_experiment_symlink_and_index_path(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name) / "repo"
        root.mkdir()
        authority_path = Path(temp.name) / "authority.json"
        payload = {
            "schema_version": 1,
            "kind": "codex-evidence-index-authority",
            "experiment_id": "wrong-experiment",
            "operator_id": "operator-a",
            "evidence_index_path": str(root / "approved.json"),
            "approved_at": "2026-11-18T00:00:00+08:00",
        }
        authority_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        expected = hashlib.sha256(authority_path.read_bytes()).hexdigest()
        _, errors = load_external_evidence_index_authority(root, authority_path, expected, "codex-replacement-20261118")
        self.assertTrue(any("experiment" in error or "evidence index" in error for error in errors), errors)
        payload["experiment_id"] = "codex-replacement-20261118"
        payload["evidence_index_path"] = str(root / "approved.json")
        authority_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        expected = hashlib.sha256(authority_path.read_bytes()).hexdigest()
        _, errors = load_external_evidence_index_authority(root, authority_path, expected, payload["experiment_id"])
        self.assertTrue(any("outside" in error for error in errors), errors)
        payload["evidence_index_path"] = str(Path(temp.name) / "approved-index.json")
        authority_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        expected = hashlib.sha256(authority_path.read_bytes()).hexdigest()
        symlink = Path(temp.name) / "authority-link.json"
        try:
            symlink.symlink_to(authority_path)
        except OSError as error:
            self.skipTest(f"symlink creation unavailable on this Windows host: {error}")
        _, errors = load_external_evidence_index_authority(root, symlink, expected, payload["experiment_id"])
        self.assertTrue(any("indirect" in error for error in errors), errors)

    def test_codex_blind_plan_binds_authority_and_new_experiment(self):
        experiment_id = "codex-replacement-20261118"
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        authority_path = Path(temp.name) / "authority.json"
        authority = {
            "schema_version": 1,
            "kind": "codex-evidence-index-authority",
            "experiment_id": experiment_id,
            "operator_id": "operator-a",
            "evidence_index_path": str(Path(temp.name) / "approved.json"),
            "approved_at": "2026-11-18T00:00:00+08:00",
        }
        authority_path.write_text(json.dumps(authority, indent=2) + "\n", encoding="utf-8")
        authority_sha = hashlib.sha256(authority_path.read_bytes()).hexdigest()
        gate = self._reviewer_gate(experiment_id)
        plan = behavior_validation.prepare_codex_replication_blind_plan(
            ROOT, experiment_id, gate, "a" * 64, authority, authority_sha
        )
        self.assertEqual(experiment_id, plan["experiment_id"])
        self.assertEqual(18, len(plan["assignments"]))
        self.assertEqual(14, sum(key.startswith("replication:") for key in plan["assignments"]))
        self.assertEqual(4, sum(key.startswith("current:") for key in plan["assignments"]))
        for pair_id in [pair["pair_id"] for pair in json.loads((ROOT / behavior_validation.CODEX_REPLICATION_MATRIX_PATH).read_text(encoding="utf-8"))["pairs"]]:
            control = f"replication:{pair_id}:control"
            loaded = f"replication:{pair_id}:skill_loaded"
            self.assertEqual(1, abs(plan["run_order"].index(control) - plan["run_order"].index(loaded)))
        self.assertLess(plan["run_order"].index("current:FL-1"), plan["run_order"].index("current:FL-1R"))
        self.assertEqual(authority_sha, plan["index_authority"]["sha256"])

    def test_codex_blind_plan_rejects_self_reviewer_after_generation(self):
        plan = self._plan("codex-plan-reviewer-independence-20261118")
        plan["reviewer_gate"]["reviewer_operator_id"] = plan["reviewer_gate"]["operator_id"]
        errors = behavior_validation.validate_codex_replication_blind_plan(ROOT, plan)
        self.assertTrue(any("independent Reviewer" in error for error in errors), errors)

    def test_cli_prepares_external_codex_plan_and_mapping(self):
        experiment_id = "codex-replacement-cli-20261118"
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        external = Path(temp.name)
        reviewer_path = external / "reviewer.json"
        reviewer = self._reviewer_gate(experiment_id)
        reviewer_path.write_text(json.dumps(reviewer, indent=2) + "\n", encoding="utf-8")
        reviewer_sha = hashlib.sha256(reviewer_path.read_bytes()).hexdigest()
        authority_path = external / "authority.json"
        authority = {
            "schema_version": 1,
            "kind": "codex-evidence-index-authority",
            "experiment_id": experiment_id,
            "operator_id": "operator-a",
            "evidence_index_path": str(external / "approved-index.json"),
            "approved_at": "2026-11-18T00:00:00+08:00",
        }
        authority_path.write_text(json.dumps(authority, indent=2) + "\n", encoding="utf-8")
        authority_sha = hashlib.sha256(authority_path.read_bytes()).hexdigest()
        plan_path = external / "blind-plan.json"
        command = [
            sys.executable, str(ROOT / "scripts/behavior_validation.py"), "prepare-codex-replication-blind",
            "--root", str(ROOT), "--experiment-id", experiment_id,
            "--reviewer-gate", str(reviewer_path), "--reviewer-gate-sha256", reviewer_sha,
            "--index-authority", str(authority_path), "--index-authority-sha256", authority_sha,
            "--output", str(plan_path),
        ]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        mapping_path = external / "blind-plan-mapping.json"
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        self.assertEqual(18, len(plan["assignments"]))
        self.assertEqual(plan["assignments"], mapping["assignments"])
        self.assertEqual(plan["mapping_sha256"], mapping["mapping_sha256"])

    def _plan(self, experiment_id="codex-report-test-20261118"):
        authority = {
            "schema_version": 1,
            "kind": "codex-evidence-index-authority",
            "experiment_id": experiment_id,
            "operator_id": "operator-a",
            "evidence_index_path": str(Path(tempfile.gettempdir()) / "codex-report-approved.json"),
            "approved_at": "2026-11-18T00:00:00+08:00",
        }
        gate = self._reviewer_gate(experiment_id)
        return behavior_validation.prepare_codex_replication_blind_plan(
            ROOT, experiment_id, gate, "a" * 64, authority, "b" * 64
        )

    def _replication_package(self, plan, pair, arm, *, loading_observation=None):
        arm_spec = pair[arm]
        key = f"replication:{pair['pair_id']}:{arm}"
        blind_id = plan["assignments"][key]
        lineage = {
            "pair_id": pair["pair_id"],
            "source_evaluation_id": pair["source_evaluation_id"],
            "scenario_id": pair["scenario_id"],
            "scenario_shape": pair["scenario_shape"],
            "arm": arm,
            "boundary_id": "BOUNDARY-CODEX-001",
            "blind_review_id": blind_id,
            "attempt": 1,
        }
        run = {
            "run_id": f"RUN-{arm}-{pair['pair_id']}",
            "evaluation_id": arm_spec["evaluation_id"],
            "scenario_id": pair["scenario_id"],
            "scenario_shape": pair["scenario_shape"],
            "status": "completed",
            "exit_code": 0,
        }
        return {
            "lineage_kind": "replication",
            "replication_lineage": lineage,
            "lineage": None,
            "current_lineage": None,
            "current_boundary": None,
            "run": run,
            "review": {"blind_review_id": blind_id, "decision": "accept", "condition_guess": "unknown", "guess_confidence": "low", "review_axes": {}},
            "eligible": True,
            "scores": {"Safety": 3, "Completion honesty": 3, "Evidence integrity across agents": 3, "Authority continuity": 3},
            "evidence_type": pair["evidence_type"],
            "loading_observation": loading_observation,
            "loading_probe_eligible": loading_observation in {"loaded", "not-loaded", "not-observed"},
            "incident_categories": [],
        }

    def test_report_separates_codex_replication_from_unreproduced_claude_history(self):
        plan = self._plan()
        report = behavior_validation.build_codex_replication_report(
            ROOT, [], plan, reviewer_ready=True, evidence_index_authority_fixed=True,
            current_preflight={"install_provenance": "blocked", "c2": "blocked", "permissions": "not-run"},
            external_index_errors=None,
        )
        self.assertEqual("not-reproduced", report["historical_replay"]["status"])
        self.assertEqual("Codex-only", report["codex_replication"]["claim_scope"])
        self.assertEqual(7, len(report["codex_replication"]["pairs"]))
        self.assertEqual("unverified", report["current_acceptance"]["host_acceptance_verdict"])
        self.assertFalse(report["current_acceptance"]["may_claim_accepted"])
        current_only = behavior_validation.build_codex_replication_report(
            ROOT, [], plan, reviewer_ready=True, evidence_index_authority_fixed=True,
            current_preflight={"install_provenance": "CURRENT", "c2": "C2_CLEAN", "permissions": "pass"},
            external_index_errors=[],
        )
        self.assertEqual("incomplete", current_only["current_acceptance"]["readiness"])

    def test_replication_loading_probes_never_receive_behavior_scores(self):
        plan = self._plan("codex-loading-report-test-20261118")
        matrix = json.loads((ROOT / behavior_validation.CODEX_REPLICATION_MATRIX_PATH).read_text(encoding="utf-8"))
        pair = next(item for item in matrix["pairs"] if item["evidence_type"] == "loading-probe")
        packages = [
            self._replication_package(plan, pair, "control", loading_observation="not-loaded"),
            self._replication_package(plan, pair, "skill_loaded", loading_observation="loaded"),
        ]
        report = behavior_validation.build_codex_replication_report(
            ROOT, packages, plan, reviewer_ready=True, evidence_index_authority_fixed=True,
            current_preflight={"install_provenance": "blocked", "c2": "blocked", "permissions": "not-run"},
            external_index_errors=None,
        )
        item = next(x for x in report["codex_replication"]["pairs"] if x["pair_id"] == pair["pair_id"])
        self.assertEqual("loading-probe-complete", item["status"])
        self.assertFalse(item["behavioral_score_interpreted"])
        self.assertEqual({"control": "not-loaded", "skill_loaded": "loaded"}, item["loading_observations"])

    def test_blind_assignment_errors_binds_replication_ids(self):
        plan = self._plan("codex-replication-blind-binding-20261118")
        matrix = json.loads((ROOT / behavior_validation.CODEX_REPLICATION_MATRIX_PATH).read_text(encoding="utf-8"))
        pair = matrix["pairs"][0]
        package = self._replication_package(plan, pair, "control")
        self.assertEqual([], behavior_validation.blind_assignment_errors(plan, [package]))
        package["review"]["blind_review_id"] = "BLIND-WRONG-01-abcdef123456"
        errors = behavior_validation.blind_assignment_errors(plan, [package])
        self.assertTrue(any("replication" in error for error in errors), errors)

    def test_index_authority_does_not_substitute_for_final_approved_index(self):
        plan = self._plan("codex-index-gate-test-20261118")
        report = behavior_validation.build_codex_replication_report(
            ROOT, [], plan, reviewer_ready=True, evidence_index_authority_fixed=True,
            current_preflight={"install_provenance": "CURRENT", "c2": "C2_CLEAN", "permissions": "pass"},
            external_index_errors=None,
        )
        self.assertTrue(report["gates"]["index_authority_gate"])
        self.assertFalse(report["gates"]["final_evidence_index_gate"])
        self.assertEqual("blocked", report["current_acceptance"]["readiness"])

    def test_report_cli_rejects_final_index_path_different_from_pinned_authority(self):
        experiment_id = "codex-report-cli-20261118"
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        external = Path(temp.name)
        reviewer_path = external / "reviewer.json"
        reviewer = self._reviewer_gate(experiment_id)
        reviewer_path.write_text(json.dumps(reviewer, indent=2) + "\n", encoding="utf-8")
        reviewer_sha = hashlib.sha256(reviewer_path.read_bytes()).hexdigest()
        authority_path = external / "authority.json"
        declared_index = external / "approved-authorized.json"
        authority = {
            "schema_version": 1,
            "kind": "codex-evidence-index-authority",
            "experiment_id": experiment_id,
            "operator_id": "operator-a",
            "evidence_index_path": str(declared_index),
            "approved_at": "2026-11-18T00:00:00+08:00",
        }
        authority_path.write_text(json.dumps(authority, indent=2) + "\n", encoding="utf-8")
        authority_sha = hashlib.sha256(authority_path.read_bytes()).hexdigest()
        plan = behavior_validation.prepare_codex_replication_blind_plan(
            ROOT, experiment_id, reviewer, reviewer_sha, authority, authority_sha
        )
        plan_path = external / "blind-plan.json"
        plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        plan_sha = hashlib.sha256(plan_path.read_bytes()).hexdigest()
        other_index = external / "other-approved.json"
        other_index.write_text(json.dumps({"schema_version": 1, "runs": {}, "records": {}}, indent=2) + "\n", encoding="utf-8")
        other_sha = hashlib.sha256(other_index.read_bytes()).hexdigest()
        output = external / "report.json"
        command = [
            sys.executable, str(ROOT / "scripts/behavior_validation.py"), "report-codex-replication",
            "--root", str(ROOT), "--blind-plan", str(plan_path), "--blind-plan-sha256", plan_sha,
            "--reviewer-gate", str(reviewer_path), "--reviewer-gate-sha256", reviewer_sha,
            "--index-authority", str(authority_path), "--index-authority-sha256", authority_sha,
            "--evidence-index", str(other_index), "--evidence-index-sha256", other_sha,
            "--output", str(output),
        ]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertFalse(report["gates"]["final_evidence_index_gate"])
        self.assertTrue(any("differs from the pinned" in error for error in report["current_acceptance"]["external_index_errors"]))


if __name__ == "__main__":
    unittest.main()
