from __future__ import annotations

import json
from pathlib import Path
import copy
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from behavior_validation import (
    CURRENT_ACCEPTANCE_MATRIX_PATH,
    build_behavior_report,
    blind_assignment_errors,
    prepare_blind_plan,
    reviewer_gate_errors,
    load_pinned_blind_plan,
    load_pinned_reviewer_gate,
    validate_behavior_matrices,
    validate_blind_plan,
)
from evaluation_evidence_validation import (
    current_acceptance_boundary_errors,
    current_acceptance_lineage_errors,
    current_acceptance_pair_errors,
    formal_review_errors,
)

CURRENT_BOUNDARY = {
    "schema_version": 1,
    "kind": "current-validation-boundary",
    "boundary_id": "BOUNDARY-001",
    "observed_at": "2026-11-10T00:00:00+00:00",
    "host": "Claude Code",
    "host_version": "2.1.240",
    "model": "claude-opus-5",
    "provider": "anthropic",
    "endpoint": "configured",
    "commit": "a" * 40,
    "git_tree": "b" * 40,
    "skill_sha256": "c" * 64,
    "install_provenance": "CURRENT",
    "c2_status": "C2_CLEAN",
    "permission_preflight": "pass",
    "permission_mode": "acceptEdits",
    "tools_digest": "d" * 64,
    "fixture_root": "C:/temp/lp-accept",
}


def current_package(arm_id, *, predecessor_run_id=None):
    matrix = json.loads((ROOT / CURRENT_ACCEPTANCE_MATRIX_PATH).read_text(encoding="utf-8"))
    arm = next(item for item in matrix["arms"] if item["arm_id"] == arm_id)
    run_id = f"RUN-{arm_id}"
    blind_id = f"BLIND-{arm_id}-01-abcdef123456"
    lineage = {
        "schema_version": 1,
        "kind": "current-acceptance-lineage",
        "boundary_id": CURRENT_BOUNDARY["boundary_id"],
        "arm_id": arm_id,
        "scenario_id": arm["scenario_id"],
        "scenario_shape": arm["scenario_shape"],
        "loading_mode": arm["loading_mode"],
        "predecessor_run_id": predecessor_run_id,
        "predecessor_checkpoint_path": "evidence/checkpoint.json" if predecessor_run_id else None,
        "predecessor_checkpoint_sha256": "f" * 64 if predecessor_run_id else None,
        "blind_review_id": blind_id,
        "attempt": 1,
        "retry_of": None,
        "retry_reason": None,
    }
    review = {
        "schema_version": 4,
        "reviewer": f"reviewer-{arm_id}",
        "decision": "accept",
        "review_axes": {
            "Spec": {"applicability": "applicable", "decision": "pass", "evidence": "trace#1"},
            "Standards": {"applicability": "applicable", "decision": "pass", "evidence": "trace#1"},
            "Implementation Quality": {"applicability": "applicable", "decision": "pass", "evidence": "trace#1"},
            "Verification & Evidence": {"applicability": "applicable", "decision": "pass", "evidence": "trace#1"},
        },
        "independence": {
            "trace_author_operator_id": "operator-a", "trace_author_session_id": "session-a",
            "reviewer_operator_id": "operator-b", "reviewer_session_id": "session-b", "basis": "Separate operator and session identities.",
        },
        "blind_review_id": blind_id,
        "review_packet_sha256": "e" * 64,
        "condition_guess": "unknown",
        "guess_confidence": "low",
        "review_completed_at": "2026-11-10T01:00:00+00:00",
        "condition_guess_recorded_at": "2026-11-10T01:01:00+00:00",
        "condition_revealed_at": "2026-11-10T01:02:00+00:00",
    }
    run = {
        "run_id": run_id,
        "evaluation_id": f"EVAL-CURRENT-{arm_id}",
        "scenario_id": arm["scenario_id"],
        "scenario_shape": arm["scenario_shape"],
        "host": CURRENT_BOUNDARY["host"],
        "host_version": CURRENT_BOUNDARY["host_version"],
        "model": CURRENT_BOUNDARY["model"],
        "commit": CURRENT_BOUNDARY["commit"],
        "loading_mode": arm["loading_mode"],
        "status": "completed",
        "exit_code": 0,
        "evidence": {
            "evidence/checkpoint.json": "f" * 64,
        },
    }
    scores = {name: 3 for name in (
        "Goal fidelity", "Plan quality", "Evidence quality", "Adaptation quality",
        "Loop efficiency", "Safety", "Completion honesty", "Evidence integrity across agents",
        "Authority continuity", "Host-native integration", "Code quality",
    )}
    return {
        "lineage_kind": "current",
        "current_arm_id": f"current:{arm_id}",
        "current_lineage": lineage,
        "lineage": lineage,
        "current_boundary": dict(CURRENT_BOUNDARY),
        "run": run,
        "review": review,
        "scores": scores,
        "code_quality_applicability": "applicable",
        "code_artifacts": ["evidence/change.py"],
        "eligible": True,
        "incident_categories": [],
        "integrity_validated": True,
    }


def valid_reviewer_gate(experiment_id):
    return {
        "schema_version": 1,
        "kind": "behavior-reviewer-readiness",
        "experiment_id": experiment_id,
        "operator_id": "operator-runner",
        "operator_session_id": "session-runner",
        "reviewer_operator_id": "operator-independent-reviewer",
        "reviewer_session_id": "session-independent-reviewer",
        "blind_review_confirmed": True,
        "readiness": "ready",
        "confirmed_at": "2026-11-10T00:00:00+00:00",
        "scope": "Independent reviewer confirmed readiness for all 18 blinded run reviews.",
    }


def bind_blind_assignments(packages, plan):
    for package in packages:
        if package["lineage_kind"] == "historical":
            lineage = package["lineage"]
            key = f"historical:{lineage['pair_id']}:{lineage['arm']}"
        else:
            lineage = package["current_lineage"]
            key = f"current:{lineage['arm_id']}"
        blind_id = plan["assignments"][key]
        lineage["blind_review_id"] = blind_id
        package["review"]["blind_review_id"] = blind_id


class BehaviorValidationPlanTests(unittest.TestCase):
    def test_current_acceptance_matrix_has_the_four_gate_arms(self):
        errors = validate_behavior_matrices(ROOT)
        self.assertEqual([], errors)

        matrix = json.loads((ROOT / CURRENT_ACCEPTANCE_MATRIX_PATH).read_text(encoding="utf-8"))
        arms = {arm["arm_id"]: arm for arm in matrix["arms"]}
        self.assertEqual({"LW-1", "FL-1", "FL-1R", "IMP-1"}, set(arms))
        self.assertEqual("FL-1", arms["FL-1R"]["predecessor_arm_id"])
        self.assertEqual("scenario 53", arms["FL-1R"]["scenario_id"])
        self.assertEqual("implicit", arms["IMP-1"]["loading_mode"])

    def test_matrix_rejects_missing_gate_arm_or_broken_resume_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs/evaluations").mkdir(parents=True)
            historical = json.loads((ROOT / "docs/evaluations/historical-replay-matrix.json").read_text(encoding="utf-8"))
            current = json.loads((ROOT / CURRENT_ACCEPTANCE_MATRIX_PATH).read_text(encoding="utf-8"))
            (root / "docs/evaluations/historical-replay-matrix.json").write_text(json.dumps(historical), encoding="utf-8")
            current["arms"] = [arm for arm in current["arms"] if arm["arm_id"] != "FL-1R"]
            (root / CURRENT_ACCEPTANCE_MATRIX_PATH).write_text(json.dumps(current), encoding="utf-8")

            errors = validate_behavior_matrices(root)

        self.assertTrue(any("FL-1R" in error for error in errors))

    def test_blind_plan_assigns_unique_ids_and_respects_resume_order(self):
        plan = prepare_blind_plan(ROOT, "BEHAVIOR-TEST-001", valid_reviewer_gate("BEHAVIOR-TEST-001"), "a" * 64)
        errors = validate_blind_plan(ROOT, plan)
        self.assertEqual([], errors)
        self.assertEqual(18, len(plan["run_order"]))
        self.assertEqual(18, len(plan["assignments"]))
        ids = list(plan["assignments"].values())
        self.assertEqual(len(ids), len(set(ids)))
        self.assertLess(plan["run_order"].index("current:FL-1"), plan["run_order"].index("current:FL-1R"))

    def test_blind_plan_rejects_duplicate_blind_id_and_missing_arm(self):
        plan = prepare_blind_plan(ROOT, "BEHAVIOR-TEST-002", valid_reviewer_gate("BEHAVIOR-TEST-002"), "a" * 64)
        keys = list(plan["assignments"])
        plan["assignments"][keys[1]] = plan["assignments"][keys[0]]
        plan["run_order"].remove(keys[-1])
        errors = validate_blind_plan(ROOT, plan)
        self.assertTrue(any("unique" in error for error in errors))
        self.assertTrue(any("run_order" in error or "arm" in error for error in errors))

    def test_report_never_promotes_historical_packages_to_host_acceptance(self):
        plan = prepare_blind_plan(ROOT, "BEHAVIOR-TEST-003", valid_reviewer_gate("BEHAVIOR-TEST-003"), "a" * 64)
        report = build_behavior_report(
            ROOT,
            [],
            plan,
            external_index_fixed=False,
            reviewer_ready=False,
            current_preflight={"install_provenance": "blocked", "c2": "blocked", "permissions": "not-run"},
        )
        self.assertEqual("incomplete", report["historical_replay"]["status"])
        self.assertEqual("blocked", report["current_acceptance"]["readiness"])
        self.assertEqual("unverified", report["current_acceptance"]["host_acceptance_verdict"])
        self.assertFalse(report["current_acceptance"]["may_claim_accepted"])

    def test_completed_behavior_failure_is_distinguished_from_eii(self):
        plan = prepare_blind_plan(ROOT, "BEHAVIOR-TEST-004", valid_reviewer_gate("BEHAVIOR-TEST-004"), "a" * 64)
        pair = json.loads((ROOT / "docs/evaluations/historical-replay-matrix.json").read_text(encoding="utf-8"))["pairs"][0]
        control_arm = f"historical:{pair['pair_id']}:control"
        loaded_arm = f"historical:{pair['pair_id']}:skill_loaded"
        control = {"lineage_kind": "historical", "lineage": {"pair_id": pair["pair_id"], "arm": "control"}, "run": {"run_id": "RUN-A", "evaluation_id": "EVAL-006", "status": "completed", "exit_code": 0}, "review": {"decision": "accept"}, "scores": {"Safety": 3}, "eligible": True, "incident_categories": []}
        loaded = {"lineage_kind": "historical", "lineage": {"pair_id": pair["pair_id"], "arm": "skill_loaded"}, "run": {"run_id": "RUN-B", "evaluation_id": "EVAL-007", "status": "completed", "exit_code": 0}, "review": {"decision": "reject"}, "scores": {"Safety": 1}, "eligible": False, "incident_categories": []}
        bind_blind_assignments([control, loaded], plan)

        report = build_behavior_report(ROOT, [control, loaded], plan, external_index_fixed=True, reviewer_ready=True, current_preflight={"install_provenance": "CURRENT", "c2": "C2_CLEAN", "permissions": "pass"})

        pair_result = next(item for item in report["historical_replay"]["pairs"] if item["pair_id"] == pair["pair_id"])
        self.assertEqual("behavior-failure-observed", pair_result["status"])
        self.assertEqual(1, pair_result["control_score_count"])
        self.assertEqual("unverified", report["current_acceptance"]["host_acceptance_verdict"])

    def test_eii_does_not_become_a_behavior_failure_or_success(self):
        plan = prepare_blind_plan(ROOT, "BEHAVIOR-TEST-005", valid_reviewer_gate("BEHAVIOR-TEST-005"), "a" * 64)
        pair = json.loads((ROOT / "docs/evaluations/historical-replay-matrix.json").read_text(encoding="utf-8"))["pairs"][0]
        control = {"lineage_kind": "historical", "lineage": {"pair_id": pair["pair_id"], "arm": "control"}, "run": {"run_id": "RUN-A", "evaluation_id": "EVAL-006", "status": "completed", "exit_code": 0}, "review": {"decision": "accept"}, "scores": {"Safety": 3}, "eligible": True, "incident_categories": []}
        loaded = {"lineage_kind": "historical", "lineage": {"pair_id": pair["pair_id"], "arm": "skill_loaded"}, "run": {"run_id": "RUN-B", "evaluation_id": "EVAL-007", "status": "failed", "exit_code": 429}, "review": {"decision": "reject"}, "scores": {}, "eligible": False, "incident_categories": ["http-429"]}
        bind_blind_assignments([control, loaded], plan)

        report = build_behavior_report(ROOT, [control, loaded], plan, external_index_fixed=True, reviewer_ready=True, current_preflight={"install_provenance": "CURRENT", "c2": "C2_CLEAN", "permissions": "pass"})

        pair_result = next(item for item in report["historical_replay"]["pairs"] if item["pair_id"] == pair["pair_id"])
        self.assertEqual("infrastructure-interrupted", pair_result["status"])
        self.assertIn("http-429", pair_result["incidents"])

    def test_current_four_complete_arms_reach_record_readiness_but_not_auto_acceptance(self):
        plan = prepare_blind_plan(ROOT, "BEHAVIOR-TEST-006", valid_reviewer_gate("BEHAVIOR-TEST-006"), "a" * 64)
        packages = [current_package(arm_id) for arm_id in ("LW-1", "FL-1", "IMP-1")]
        packages.append(current_package("FL-1R", predecessor_run_id="RUN-FL-1"))
        bind_blind_assignments(packages, plan)
        report = build_behavior_report(
            ROOT,
            packages,
            plan,
            external_index_fixed=True,
            reviewer_ready=True,
            current_preflight={"install_provenance": "CURRENT", "c2": "C2_CLEAN", "permissions": "pass"},
        )
        self.assertEqual("ready-for-host-acceptance-record", report["current_acceptance"]["readiness"])
        self.assertFalse(report["current_acceptance"]["may_claim_accepted"])
        self.assertEqual(set(range(1, 9)), set(report["current_acceptance"]["host_acceptance_dimension_coverage"]))
        self.assertEqual(4, len(report["current_acceptance"]["arm_results"]))
        self.assertTrue(all(result["attempts"][0]["attempt"] == 1 for result in report["current_acceptance"]["arm_results"]))
        self.assertEqual(2, len(report["historical_replay"]["loading_probes"]))
        self.assertEqual(5, len(report["historical_replay"]["behavior_pairs"]))

    def test_blind_report_rejects_arm_identity_without_matching_external_mapping(self):
        plan = prepare_blind_plan(ROOT, "BEHAVIOR-TEST-010", valid_reviewer_gate("BEHAVIOR-TEST-010"), "a" * 64)
        package = current_package("LW-1")
        bind_blind_assignments([package], plan)
        package["review"]["blind_review_id"] = "BLIND-OTHER"
        self.assertTrue(any("randomized assignment" in error for error in blind_assignment_errors(plan, [package])))

    def test_report_retains_failed_retry_attempt_and_incident(self):
        plan = prepare_blind_plan(ROOT, "BEHAVIOR-TEST-011", valid_reviewer_gate("BEHAVIOR-TEST-011"), "a" * 64)
        packages = [current_package(arm_id) for arm_id in ("LW-1", "FL-1", "IMP-1")]
        packages.append(current_package("FL-1R", predecessor_run_id="RUN-FL-1"))
        retry = copy.deepcopy(packages[1])
        retry["current_lineage"]["attempt"] = 2
        retry["lineage"]["attempt"] = 2
        retry["current_lineage"]["retry_of"] = retry["run"]["run_id"]
        retry["lineage"]["retry_of"] = retry["run"]["run_id"]
        retry["current_lineage"]["retry_reason"] = "timeout"
        retry["lineage"]["retry_reason"] = "timeout"
        retry["run"]["run_id"] = "RUN-FL-1-RETRY-2"
        retry["run"]["evaluation_id"] = "EVAL-CURRENT-FL-1-RETRY-2"
        retry["run"]["status"] = "failed"
        retry["run"]["exit_code"] = 1
        retry["incident_categories"] = ["timeout"]
        retry["eligible"] = False
        packages.append(retry)
        bind_blind_assignments(packages, plan)
        report = build_behavior_report(
            ROOT, packages, plan, external_index_fixed=True, reviewer_ready=True,
            current_preflight={"install_provenance": "CURRENT", "c2": "C2_CLEAN", "permissions": "pass"},
        )
        fl1 = next(item for item in report["current_acceptance"]["arm_results"] if item["arm_id"] == "FL-1")
        self.assertEqual(2, len(fl1["attempts"]))
        self.assertEqual("failed", fl1["attempts"][1]["status"])
        self.assertIn("timeout", report["current_acceptance"]["execution_infrastructure_incidents"])

    def test_current_lineage_binds_formal_arm_and_resume_predecessor(self):
        lineage = {
            "schema_version": 1,
            "kind": "current-acceptance-lineage",
            "boundary_id": "BOUNDARY-001",
            "arm_id": "FL-1R",
            "scenario_id": "scenario 53",
            "scenario_shape": "full-loop",
            "loading_mode": "explicit",
            "predecessor_run_id": "RUN-FL-1",
            "predecessor_checkpoint_path": "evidence/checkpoint.json",
            "predecessor_checkpoint_sha256": "f" * 64,
            "blind_review_id": "BLIND-FL-1R-01-abcdef123456",
            "attempt": 1,
            "retry_of": None,
            "retry_reason": None,
        }
        run = {"run_id": "RUN-FL-1R", "scenario_id": "scenario 53", "scenario_shape": "full-loop", "loading_mode": "explicit"}
        self.assertEqual([], current_acceptance_lineage_errors(ROOT, lineage, run, predecessor_run_ids={"RUN-FL-1"}))
        lineage["predecessor_run_id"] = None
        self.assertTrue(any("predecessor" in error for error in current_acceptance_lineage_errors(ROOT, lineage, run, predecessor_run_ids=set())))

    def test_current_boundary_rejects_drift_and_failed_preflight(self):
        boundary = {
            "schema_version": 1,
            "kind": "current-validation-boundary",
            "boundary_id": "BOUNDARY-001",
            "observed_at": "2026-11-10T00:00:00+00:00",
            "host": "Claude Code",
            "host_version": "2.1.232",
            "model": "claude-opus-5",
            "provider": "anthropic",
            "endpoint": "configured",
            "commit": "a" * 40,
            "git_tree": "b" * 40,
            "skill_sha256": "c" * 64,
            "install_provenance": "CURRENT",
            "c2_status": "C2_CLEAN",
            "permission_preflight": "pass",
            "permission_mode": "acceptEdits",
            "tools_digest": "d" * 64,
            "fixture_root": "C:/temp/lp-accept",
        }
        run = {"host": "Claude Code", "host_version": "2.1.232", "model": "claude-opus-5", "commit": "a" * 40}
        self.assertEqual([], current_acceptance_boundary_errors(boundary, run))
        boundary["c2_status"] = "blocked"
        self.assertTrue(any("C2" in error for error in current_acceptance_boundary_errors(boundary, run)))

    def test_formal_review_requires_blind_guess_and_review_packet_hash(self):
        review = {
            "schema_version": 4,
            "reviewer": "reviewer-b",
            "decision": "accept",
            "review_axes": {
                "Spec": {"applicability": "applicable", "decision": "pass", "evidence": "trace#1"},
                "Standards": {"applicability": "applicable", "decision": "pass", "evidence": "trace#1"},
                "Implementation Quality": {"applicability": "not-applicable", "decision": "not-applicable", "evidence": "trace#1"},
                "Verification & Evidence": {"applicability": "applicable", "decision": "pass", "evidence": "trace#1"},
            },
            "independence": {
                "trace_author_operator_id": "operator-a", "trace_author_session_id": "session-a",
                "reviewer_operator_id": "operator-b", "reviewer_session_id": "session-b", "basis": "Separate operator and session.",
            },
            "blind_review_id": "BLIND-LW-1-01-abcdef123456",
            "review_packet_sha256": "e" * 64,
            "condition_guess": "unknown",
            "guess_confidence": "low",
            "review_completed_at": "2026-11-10T01:00:00+00:00",
            "condition_guess_recorded_at": "2026-11-10T01:01:00+00:00",
            "condition_revealed_at": "2026-11-10T01:02:00+00:00",
        }
        self.assertEqual([], formal_review_errors(review, {"trace_author": "author-a"}))
        review["review_packet_sha256"] = "bad"
        self.assertTrue(any("packet" in error for error in formal_review_errors(review, {"trace_author": "author-a"})))

    def test_current_acceptance_requires_all_four_formal_arms(self):
        package = current_package("LW-1")
        errors = current_acceptance_pair_errors(ROOT, [package])
        self.assertTrue(any("required" in error or "missing" in error for error in errors))

    def test_complete_current_matrix_binds_shared_boundary_and_resume_checkpoint(self):
        packages = [current_package(arm) for arm in ("LW-1", "FL-1", "IMP-1")]
        packages.append(current_package("FL-1R", predecessor_run_id="RUN-FL-1"))
        errors = current_acceptance_pair_errors(ROOT, packages)
        self.assertEqual([], errors)

        packages[-1]["current_boundary"]["skill_sha256"] = "f" * 64
        errors = current_acceptance_pair_errors(ROOT, packages)
        self.assertTrue(any("boundary" in error.casefold() for error in errors))

    def test_current_retry_limit_and_code_quality_na_are_enforced(self):
        original = current_package("LW-1")
        retries = []
        previous_id = original["run"]["run_id"]
        for attempt in range(2, 5):
            retry = copy.deepcopy(original)
            retry["current_lineage"]["attempt"] = attempt
            retry["lineage"]["attempt"] = attempt
            retry["current_lineage"]["retry_of"] = previous_id
            retry["lineage"]["retry_of"] = previous_id
            retry["current_lineage"]["retry_reason"] = "timeout"
            retry["lineage"]["retry_reason"] = "timeout"
            retry["run"]["run_id"] = f"RUN-LW-1-RETRY-{attempt}"
            retry["run"]["evaluation_id"] = f"EVAL-CURRENT-LW-1-RETRY-{attempt}"
            retry["run"]["status"] = "failed"
            retry["run"]["exit_code"] = 1
            retry["incident_categories"] = ["timeout"]
            retry["eligible"] = False
            retries.append(retry)
            previous_id = retry["run"]["run_id"]
        errors = current_acceptance_pair_errors(ROOT, [original, *retries])
        self.assertTrue(any("two-retry limit" in error for error in errors))

        invalid = current_package("LW-1")
        invalid["code_quality_applicability"] = "not-applicable"
        invalid["scores"]["Code quality"] = "not-applicable"
        self.assertTrue(any("N/A conflicts with code evidence" in error for error in current_acceptance_pair_errors(ROOT, [invalid])))

    def test_formal_review_requires_guess_before_unblinding(self):
        review = {
            "schema_version": 4,
            "reviewer": "reviewer-b",
            "decision": "accept",
            "review_axes": {
                "Spec": {"applicability": "applicable", "decision": "pass", "evidence": "trace#1"},
                "Standards": {"applicability": "applicable", "decision": "pass", "evidence": "trace#1"},
                "Implementation Quality": {"applicability": "not-applicable", "decision": "not-applicable", "evidence": "trace#1"},
                "Verification & Evidence": {"applicability": "applicable", "decision": "pass", "evidence": "trace#1"},
            },
            "independence": {
                "trace_author_operator_id": "operator-a", "trace_author_session_id": "session-a",
                "reviewer_operator_id": "operator-b", "reviewer_session_id": "session-b", "basis": "Separate operator and session identities.",
            },
            "blind_review_id": "BLIND-LW-1-01-abcdef123456",
            "review_packet_sha256": "e" * 64,
            "condition_guess": "control",
            "guess_confidence": "medium",
            "review_completed_at": "2026-11-10T01:00:00+00:00",
            "condition_guess_recorded_at": "2026-11-10T01:01:00+00:00",
            "condition_revealed_at": "2026-11-10T01:02:00+00:00",
        }
        self.assertEqual([], formal_review_errors(review, {"trace_author": "author-a"}))
        review["condition_revealed_at"] = "2026-11-10T00:59:00+00:00"
        self.assertTrue(any("before" in error.casefold() for error in formal_review_errors(review, {"trace_author": "author-a"})))

    def test_reviewer_readiness_gate_rejects_self_review_and_wrong_experiment(self):
        gate = valid_reviewer_gate("BEHAVIOR-TEST-007")
        self.assertEqual([], reviewer_gate_errors(gate, "BEHAVIOR-TEST-007"))
        gate["reviewer_operator_id"] = gate["operator_id"]
        self.assertTrue(any("different operator" in error for error in reviewer_gate_errors(gate, "BEHAVIOR-TEST-007")))
        gate = valid_reviewer_gate("BEHAVIOR-TEST-007")
        gate["reviewer_session_id"] = gate["operator_session_id"]
        self.assertTrue(any("different session" in error for error in reviewer_gate_errors(gate, "BEHAVIOR-TEST-007")))
        gate = valid_reviewer_gate("OTHER-EXPERIMENT")
        self.assertTrue(any("experiment_id" in error for error in reviewer_gate_errors(gate, "BEHAVIOR-TEST-007")))

    def test_pinned_review_materials_require_external_paths_and_matching_hashes(self):
        import hashlib

        with tempfile.TemporaryDirectory() as directory:
            external = Path(directory) / "reviewer.json"
            gate = valid_reviewer_gate("BEHAVIOR-TEST-009")
            external.write_text(json.dumps(gate), encoding="utf-8")
            pin = hashlib.sha256(external.read_bytes()).hexdigest()
            self.assertEqual([], load_pinned_reviewer_gate(ROOT, external, pin, "BEHAVIOR-TEST-009")[1])
            self.assertTrue(any("pin mismatch" in error for error in load_pinned_reviewer_gate(ROOT, external, "0" * 64, "BEHAVIOR-TEST-009")[1]))
            with tempfile.TemporaryDirectory(dir=ROOT, prefix=".tmp-reviewer-gate-") as inside_directory:
                inside = Path(inside_directory) / "reviewer.json"
                inside.write_text(json.dumps(gate), encoding="utf-8")
                inside_pin = hashlib.sha256(inside.read_bytes()).hexdigest()
                self.assertTrue(any("outside" in error for error in load_pinned_reviewer_gate(ROOT, inside, inside_pin, "BEHAVIOR-TEST-009")[1]))

    def test_blind_plan_requires_a_pinned_ready_reviewer_before_execution_order_is_valid(self):
        plan = prepare_blind_plan(ROOT, "BEHAVIOR-TEST-008")
        errors = validate_blind_plan(ROOT, plan)
        self.assertTrue(any("reviewer" in error.casefold() for error in errors))


if __name__ == "__main__":
    unittest.main()
