from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluation_evidence_validation import (
    historical_replay_acceptance,
    historical_replay_lineage_errors,
    historical_replay_pair_errors,
    historical_replay_review_errors,
    validate_evaluation_evidence,
)
from evaluation_evidence_fixture import make_historical_replay_package, digest, save_json, reseal_for_schema_test


MATRIX = json.loads((ROOT / "docs/evaluations/historical-replay-matrix.json").read_text(encoding="utf-8"))


def specimen(pair_index=0, arm="control", *, evaluation_id=None):
    pair = MATRIX["pairs"][pair_index]
    arm_spec = pair[arm]
    identity = pair["original_combination"]
    evaluation_id = evaluation_id or arm_spec["evaluation_id"]
    run_id = "RUN-" + evaluation_id
    lineage = {
        "schema_version": 1,
        "kind": "historical-lineage",
        "pair_id": pair["pair_id"],
        "historical_evaluation_id": pair["historical_evaluation_id"],
        "scenario_id": pair["scenario_id"],
        "scenario_shape": pair["scenario_shape"],
        "arm": arm,
        "attempt": 1,
        "retry_of": None,
        "retry_reason": None,
        "replay_reason": "Fill missing matched evidence without changing the historical package.",
        "known_gaps": pair["known_gaps"],
        "original_combination": identity,
        "reproduction_status": "matched",
        "reproduction_reason": None,
        "blind_review_id": "BLIND-TEST-01-abcdef123456",
    }
    run = {
        "run_id": run_id,
        "evaluation_id": evaluation_id,
        "scenario_id": pair["scenario_id"],
        "scenario_shape": pair["scenario_shape"],
        "host": identity["host"],
        "host_version": identity["host_version"],
        "model": identity["model"],
        "commit": "a" * 40,
        "loading_mode": arm_spec["loading_mode"],
        "trace_author": "author-a",
        "status": "completed",
        "exit_code": 0,
    }
    review = {
        "schema_version": 3,
        "reviewer": "reviewer-b",
        "decision": "accept",
        "review_axes": {
            "Spec": {"applicability": "applicable", "decision": "pass", "evidence": "trace#result-1"},
            "Standards": {"applicability": "applicable", "decision": "pass", "evidence": "trace#result-1"},
            "Implementation Quality": {"applicability": "not-applicable", "decision": "not-applicable", "evidence": "trace#result-1"},
            "Verification & Evidence": {"applicability": "applicable", "decision": "pass", "evidence": "trace#result-1"},
        },
        "independence": {
            "trace_author_operator_id": "operator-a",
            "trace_author_session_id": "session-a",
            "reviewer_operator_id": "operator-b",
            "reviewer_session_id": "session-b",
            "basis": "Different named operator and isolated review session.",
        },
        "blind_review_id": "BLIND-TEST-01-abcdef123456",
        "review_packet_sha256": "e" * 64,
        "condition_guess": "unknown",
        "guess_confidence": "low",
    }
    return pair, lineage, run, review


class HistoricalReplayValidationTests(unittest.TestCase):
    def test_lineage_must_match_pinned_historical_combination_and_matrix_arm(self):
        _, lineage, run, _ = specimen()
        self.assertEqual([], historical_replay_lineage_errors(ROOT, lineage, run))

        run["host_version"] = "2.1.999"
        self.assertTrue(any("host_version" in error for error in historical_replay_lineage_errors(ROOT, lineage, run)))

    def test_lineage_scenario_arm_and_loading_mode_mismatches_fail(self):
        _, lineage, run, _ = specimen()
        lineage["scenario_id"] = "scenario 69"
        self.assertTrue(any("scenario" in error for error in historical_replay_lineage_errors(ROOT, lineage, run)))

        _, lineage, run, _ = specimen()
        run["loading_mode"] = "explicit"
        self.assertTrue(any("loading_mode" in error for error in historical_replay_lineage_errors(ROOT, lineage, run)))

    def test_not_reproduced_combo_cannot_be_published_as_a_run_package(self):
        _, lineage, run, _ = specimen()
        lineage["reproduction_status"] = "not-reproduced"
        lineage["reproduction_reason"] = "Pinned Host version is unavailable."
        self.assertTrue(any("not-reproduced" in error for error in historical_replay_lineage_errors(ROOT, lineage, run)))

    def test_retry_requires_new_attempt_identity_and_infrastructure_reason(self):
        pair, lineage, run, _ = specimen()
        lineage.update(attempt=2, retry_of="RUN-EVAL-006", retry_reason="product-failure")
        run["evaluation_id"] = "EVAL-020"
        run["run_id"] = "RUN-EVAL-020"
        self.assertTrue(any("retry_reason" in error for error in historical_replay_lineage_errors(ROOT, lineage, run)))

        lineage.update(retry_reason="http-429")
        self.assertEqual([], historical_replay_lineage_errors(ROOT, lineage, run))

    def test_replay_review_requires_four_axes_and_different_operator_and_session(self):
        _, _, run, review = specimen()
        self.assertEqual([], historical_replay_review_errors(review, run))

        review["review_axes"].pop("Standards")
        self.assertTrue(any("four" in error or "Standards" in error for error in historical_replay_review_errors(review, run)))

        _, _, run, review = specimen()
        review["independence"]["reviewer_operator_id"] = "operator-a"
        self.assertTrue(any("independence" in error for error in historical_replay_review_errors(review, run)))

        _, _, run, review = specimen()
        review["independence"]["reviewer_session_id"] = "session-a"
        self.assertTrue(any("independence" in error for error in historical_replay_review_errors(review, run)))

    def test_axis_na_requires_evidence_and_only_later_axes_may_be_na(self):
        _, _, run, review = specimen()
        review["review_axes"]["Spec"].update(applicability="not-applicable", decision="not-applicable")
        self.assertTrue(any("Spec" in error for error in historical_replay_review_errors(review, run)))

        _, _, run, review = specimen()
        review["review_axes"]["Implementation Quality"]["evidence"] = ""
        self.assertTrue(any("evidence" in error for error in historical_replay_review_errors(review, run)))

    def test_pair_mismatch_and_failed_429_cannot_support_new_acceptance(self):
        _, control_lineage, control_run, control_review = specimen(0, "control")
        _, loaded_lineage, loaded_run, loaded_review = specimen(0, "skill_loaded")
        packages = [
            {"lineage": control_lineage, "run": control_run, "review": control_review, "scores": {"Safety": 3}},
            {"lineage": loaded_lineage, "run": loaded_run, "review": loaded_review, "scores": {"Safety": 3}},
        ]
        self.assertEqual([], historical_replay_pair_errors(ROOT, packages))

        loaded_run["commit"] = "b" * 40
        self.assertTrue(any("commit" in error for error in historical_replay_pair_errors(ROOT, packages)))

        loaded_run["commit"] = control_run["commit"]
        loaded_run.update(status="failed", exit_code=429)
        self.assertEqual("blocked", historical_replay_acceptance(ROOT, packages)["status"])

    def test_missing_required_arms_leave_replay_acceptance_blocked(self):
        result = historical_replay_acceptance(ROOT, [])
        self.assertEqual("blocked", result["status"])
        self.assertEqual(14, len(result["missing_arms"]))

    def test_all_fourteen_eligible_arms_can_clear_the_experiment_gate(self):
        packages = []
        for pair_index in range(len(MATRIX["pairs"])):
            for arm in ("control", "skill_loaded"):
                _, lineage, run, review = specimen(pair_index, arm)
                packages.append({
                    "lineage": lineage,
                    "run": run,
                    "review": review,
                "scores": {"Code quality": "not-applicable"} if MATRIX["pairs"][pair_index]["evidence_type"] == "behavior" else {},
                "eligible": MATRIX["pairs"][pair_index]["evidence_type"] == "behavior",
                "loading_probe_eligible": MATRIX["pairs"][pair_index]["evidence_type"] == "loading-probe",
                "loading_observation": ("not-loaded" if arm == "control" else "loaded") if MATRIX["pairs"][pair_index]["evidence_type"] == "loading-probe" else None,
                    "code_artifacts": [],
                })

        result = historical_replay_acceptance(ROOT, packages, operator_index_fixed=True)

        self.assertEqual("accepted", result["status"])
        self.assertEqual(14, result["observed_arms"])
        self.assertEqual(14, len(result["selected_evaluation_ids"]))

    def test_evaluation_004_probe_pairs_require_loading_observation_and_do_not_require_behavior_score(self):
        pair_index = next(index for index, pair in enumerate(MATRIX["pairs"]) if pair["evidence_type"] == "loading-probe")
        packages = []
        for arm in ("control", "skill_loaded"):
            _, lineage, run, review = specimen(pair_index, arm)
            packages.append({
                "lineage": lineage, "run": run, "review": review, "scores": {},
                "eligible": False, "loading_probe_eligible": True,
                "loading_observation": "not-loaded" if arm == "control" else "loaded",
                "code_artifacts": [],
            })
        self.assertEqual([], historical_replay_pair_errors(ROOT, packages))
        packages[1]["loading_observation"] = None
        self.assertTrue(any("loading observation" in error.casefold() for error in historical_replay_pair_errors(ROOT, packages)))

    def test_complete_v2_replay_pair_passes_public_package_validation(self):
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            shutil.copytree(ROOT / "evaluations", root / "evaluations")
            (root / "docs/evaluations").mkdir(parents=True)
            shutil.copy2(ROOT / "docs/evaluations/historical-replay-matrix.json", root / "docs/evaluations/historical-replay-matrix.json")
            (root / "scripts").mkdir()
            shutil.copy2(ROOT / "scripts/evaluation_history.json", root / "scripts/evaluation_history.json")
            authority = Path(directory) / "operator/approved.json"
            make_historical_replay_package(root, authority, pair_index=0, arm="control")
            make_historical_replay_package(root, authority, pair_index=0, arm="skill_loaded")

            errors = validate_evaluation_evidence(root, authority, digest(authority), [])

        self.assertEqual([], errors)

    def test_planned_replay_id_without_lineage_is_rejected(self):
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            shutil.copytree(ROOT / "evaluations", root / "evaluations")
            (root / "docs/evaluations").mkdir(parents=True)
            shutil.copy2(ROOT / "docs/evaluations/historical-replay-matrix.json", root / "docs/evaluations/historical-replay-matrix.json")
            (root / "scripts").mkdir()
            shutil.copy2(ROOT / "scripts/evaluation_history.json", root / "scripts/evaluation_history.json")
            authority = Path(directory) / "operator/approved.json"
            package = make_historical_replay_package(root, authority, pair_index=0, arm="control")
            run_path = package / "run.json"
            run = json.loads(run_path.read_text(encoding="utf-8"))
            run["evidence"].pop("evidence/historical-lineage.json")
            events_path = package / "evidence/events.jsonl"
            events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
            events = [event for event in events if event["artifact"] != "evidence/historical-lineage.json"]
            events_path.write_text("".join(json.dumps(event, sort_keys=True) + "\n" for event in events), encoding="utf-8", newline="\n")
            run["trace_sha256"] = digest(events_path)
            save_json(run_path, run)
            reseal_for_schema_test(package, authority)

            errors = validate_evaluation_evidence(root, authority, digest(authority), [])

        self.assertIn("requires evidence/historical-lineage.json", "\n".join(errors))

    def test_infrastructure_failure_is_preserved_but_never_acceptance_eligible(self):
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            shutil.copytree(ROOT / "evaluations", root / "evaluations")
            (root / "docs/evaluations").mkdir(parents=True)
            shutil.copy2(ROOT / "docs/evaluations/historical-replay-matrix.json", root / "docs/evaluations/historical-replay-matrix.json")
            (root / "scripts").mkdir()
            shutil.copy2(ROOT / "scripts/evaluation_history.json", root / "scripts/evaluation_history.json")
            authority = Path(directory) / "operator/approved.json"
            make_historical_replay_package(root, authority, pair_index=0, arm="control", failed=True)
            packages = {}

            errors = validate_evaluation_evidence(root, authority, digest(authority), [], validated_packages=packages)

        self.assertEqual([], errors)
        package = next(iter(packages.values()))
        self.assertEqual("failed", package["run"]["status"])
        self.assertIn("http-429", package["incident_categories"])
        self.assertFalse(package["eligible"])
