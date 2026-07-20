import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = Path("docs/evaluation-synthesis-and-protocol-calibration.md")
MODE = Path("docs/mode-selection-and-escalation.md")
LOAD = Path("docs/protocol-load-profiles.md")
MMGH = Path("docs/mmgh-behavioral-evidence.md")


@dataclass(frozen=True)
class Case:
    name: str
    operation: str = "noop"
    path: Path = MODE
    old: str = ""
    new: str = ""
    error: str | None = None


CASES = (
    Case("legal_phase_7_documents_pass", "append", EVIDENCE, new="\nThe public document set is complete.\n"),
    Case("missing_evidence_synthesis_rejected", "delete", EVIDENCE, error="missing required file"),
    Case("missing_mode_selection_rejected", "delete", MODE, error="missing required file"),
    Case("missing_load_profiles_rejected", "delete", LOAD, error="missing required file"),
    Case("missing_mmgh_evidence_rejected", "delete", MMGH, error="missing required file"),
    Case("observed_definition_required", "replace", EVIDENCE, "### Observed", "### Direct Evidence", "missing Phase 7 requirement"),
    Case("repeated_pattern_definition_required", "replace", EVIDENCE, "### Repeated Pattern", "### Repetition", "missing Phase 7 requirement"),
    Case("provisional_heuristic_definition_required", "replace", EVIDENCE, "### Provisional Heuristic", "### Guidance", "missing Phase 7 requirement"),
    Case("normative_invariant_definition_required", "replace", EVIDENCE, "### Normative Invariant", "### Rule", "missing Phase 7 requirement"),
    Case("unverified_definition_required", "replace", EVIDENCE, "### Unverified", "### Unknown", "missing Phase 7 requirement"),
    Case("single_experiment_universal_rule_rejected", "append", EVIDENCE, new="\nMMGH proves universal protocol superiority.\n", error="Phase 7 contradiction"),
    Case("strict_ab_claim_rejected", "append", EVIDENCE, new="\nThe four experiments establish a strict A/B comparison.\n", error="Phase 7 contradiction"),
    Case("production_security_certification_rejected", "append", MMGH, new="\nMMGH certifies production security.\n", error="Phase 7 contradiction"),
    Case("legal_provisional_claim_passes", "append", EVIDENCE, new="\nA bounded local change provisionally favors Lightweight.\n"),
    Case("legal_mode_selection_rules_pass", "append", MODE, new="\nThe Gate precedes implementation.\n"),
    Case("mode_after_implementation_rejected", "append", MODE, new="\nMode is selected after implementation.\n", error="Phase 7 contradiction"),
    Case("file_count_as_authority_rejected", "append", MODE, new="\nFile count is the decision authority.\n", error="Phase 7 contradiction"),
    Case("missing_lightweight_conditions_rejected", "replace", MODE, "## Lightweight Tendency", "## Local Change Guidance", "missing Phase 7 requirement"),
    Case("missing_hard_triggers_rejected", "replace", MODE, "## Full Loop Hard Triggers", "## Full Loop Guidance", "missing Phase 7 requirement"),
    Case("missing_escalation_rejected", "replace", MODE, "## Lightweight Escalation", "## Scope Growth", "missing Phase 7 requirement"),
    Case("integrator_mode_decision_rejected", "append", MODE, new="\nIntegrator decides the mode.\n", error="Phase 7 contradiction"),
    Case("mode_project_status_ownership_rejected", "append", MODE, new="\nMode Selection owns Project Status.\n", error="Phase 7 contradiction"),
    Case("bounded_low_risk_lightweight_passes", "append", MODE, new="\nA single pure helper with direct tests selects Lightweight.\n"),
    Case("typescript_rust_security_full_loop_passes", "append", MODE, new="\nA TypeScript and Rust security contract selects Full Loop.\n"),
    Case("sqlite_partial_success_full_loop_passes", "append", MODE, new="\nA SQLite partial-success boundary selects Full Loop.\n"),
    Case("no_real_gap_stops_implementation", "append", MODE, new="\nNo observed implementation gap selects No Implementation.\n"),
    Case("artifact_budget_heuristic_passes", "append", MODE, new="\nThe budget remains provisional.\n"),
    Case("artifact_budget_status_rejected", "append", MODE, new="\nArtifact Budget Status: active\n", error="Phase 7 contradiction"),
    Case("artifact_budget_hard_limit_rejected", "append", MODE, new="\nArtifact Budget is a hard absolute limit.\n", error="Phase 7 contradiction"),
    Case("lightweight_default_ledgers_rejected", "append", LOAD, new="\nLightweight defaults to Task Ledger.\n", error="Phase 7 contradiction"),
    Case("unexplained_budget_excess_rejected", "append", MODE, new="\nLightweight exceeds seven artifacts without explanation or reassessment.\n", error="Phase 7 contradiction"),
    Case("budget_excess_escalation_passes", "append", MODE, new="\nNine growing artifacts are preserved before Full Loop escalation.\n"),
    Case("lightweight_final_report_default_rejected", "append", LOAD, new="\nLightweight defaults to Final Delivery Report.\n", error="Phase 7 contradiction"),
    Case("bounded_minor_correction_passes", "append", MODE, new="\nA bounded Minor receives one documented correction.\n"),
    Case("major_without_escalation_rejected", "append", MODE, new="\nLightweight may continue after a Major Finding without escalation.\n", error="Phase 7 contradiction"),
    Case("rust_contract_without_escalation_rejected", "append", MODE, new="\nLightweight may change a Rust contract without escalation.\n", error="Phase 7 contradiction"),
    Case("sensitive_data_without_escalation_rejected", "append", MODE, new="\nLightweight may continue after sensitive-data impact without escalation.\n", error="Phase 7 contradiction"),
    Case("repeated_correction_without_escalation_rejected", "append", MODE, new="\nLightweight may continue after repeated correction without escalation.\n", error="Phase 7 contradiction"),
    Case("contract_barrier_after_escalation_passes", "append", MODE, new="\nEscalation preserves evidence and repasses the Contract Barrier.\n"),
    Case("worker_429_incident_passes", "append", MODE, new="\nWorker 429 is recorded as an Execution Infrastructure Incident.\n"),
    Case("timeout_product_blocker_rejected", "append", MODE, new="\nWorker timeout is automatically a Product Blocker.\n", error="Phase 7 contradiction"),
    Case("fabricated_no_output_delivery_rejected", "append", MODE, new="\nNo-output Worker has a completed Delivery.\n", error="Phase 7 contradiction"),
    Case("false_independent_reviewer_rejected", "append", MODE, new="\nUnavailable Reviewer is an independent Reviewer.\n", error="Phase 7 contradiction"),
    Case("tool_failure_disclosure_passes", "append", MODE, new="\nTool failure blocks verification and is disclosed.\n"),
    Case("infrastructure_ledger_rejected", "append", MODE, new="\nInfrastructure Ledger\n", error="Phase 7 contradiction"),
    Case("protocol_status_finding_passes", "append", MODE, new="\nAn illegal protocol status enters the existing Finding Ledger.\n"),
    Case("product_data_finding_passes", "append", MODE, new="\nIncorrect durable data semantics enters the existing Finding Ledger.\n"),
    Case("spec_standards_axes_pass", "append", MODE, new="\nSpec and Standards remain separate.\n"),
    Case("all_specialists_default_rejected", "append", MODE, new="\nFull Loop automatically enables all specialist Reviewers.\n", error="Phase 7 contradiction"),
    Case("provider_security_compatibility_passes", "append", MODE, new="\nProvider trust loads Security and Compatibility Review.\n"),
    Case("transaction_data_compatibility_passes", "append", MODE, new="\nTransaction behavior loads Data and Compatibility Review.\n"),
    Case("ui_focus_accessibility_passes", "append", MODE, new="\nA focus-impacting UI change loads Accessibility Review.\n"),
    Case("specialist_replacing_axes_rejected", "append", MODE, new="\nSpecialist Review replaces Spec and Standards.\n", error="Phase 7 contradiction"),
    Case("core_profile_passes", "append", LOAD, new="\nCore is always minimal.\n"),
    Case("lightweight_profile_passes", "append", LOAD, new="\nLightweight retains direct evidence.\n"),
    Case("full_loop_profile_passes", "append", LOAD, new="\nFull Loop loads scoped contracts.\n"),
    Case("project_finalization_profile_passes", "append", LOAD, new="\nFinalization requires a real project boundary.\n"),
    Case("lightweight_full_history_default_rejected", "append", LOAD, new="\nLightweight defaults to complete Full Loop history.\n", error="Phase 7 contradiction"),
    Case("lightweight_release_default_rejected", "append", LOAD, new="\nLightweight defaults to Release Readiness.\n", error="Phase 7 contradiction"),
    Case("full_loop_without_ledgers_rejected", "replace", LOAD, "Task and Finding Ledgers", "Task summaries", "missing Phase 7 requirement"),
    Case("multi_loop_finalization_cross_validation_passes", "append", LOAD, new="\nMultiple mandatory Loops load Cross-Loop Validation for finalization.\n"),
    Case("evidence_selected_oop_passes", "append", MODE, new="\nOOP is selected for observed ownership and invariant needs.\n"),
    Case("mandatory_ddd_rejected", "append", MODE, new="\nEvery Full Loop requires DDD.\n", error="Phase 7 contradiction"),
    Case("default_large_di_rejected", "append", MODE, new="\nA large DI framework is mandatory.\n", error="Phase 7 contradiction"),
    Case("uncoupled_mvvm_rejected", "append", MODE, new="\nMVVM is mandatory without view coupling.\n", error="Phase 7 contradiction"),
    Case("unbenchmarked_zero_copy_rejected", "append", MODE, new="\nZero-copy is required without benchmarks.\n", error="Phase 7 contradiction"),
    Case("new_top_level_role_rejected", "append", MODE, new="\nNew top-level role: Mode Governor\n", error="Phase 7 contradiction"),
    Case("new_authoritative_ledger_rejected", "append", MODE, new="\nNew authoritative Ledger: Mode Ledger\n", error="Phase 7 contradiction"),
    Case("new_loop_status_rejected", "append", MODE, new="\nNew Loop status: calibrated\n", error="Phase 7 contradiction"),
    Case("new_task_status_rejected", "append", MODE, new="\nNew Task status: incident\n", error="Phase 7 contradiction"),
    Case("new_finding_status_rejected", "append", MODE, new="\nNew Finding status: infrastructure\n", error="Phase 7 contradiction"),
    Case("new_severity_rejected", "append", MODE, new="\nNew Finding severity: infrastructure\n", error="Phase 7 contradiction"),
    Case("new_barrier_rejected", "append", MODE, new="\nNew Barrier: Mode Barrier\n", error="Phase 7 contradiction"),
    Case("new_acceptance_layer_rejected", "append", MODE, new="\nNew Acceptance layer: Calibration Acceptance\n", error="Phase 7 contradiction"),
    Case("checkpoint_recovery_authority_passes", "append", LOAD, new="\nCheckpoint remains the recovery authority.\n"),
    Case("project_status_authority_passes", "append", EVIDENCE, new="\nPROJECT.md remains the Project authority.\n"),
    Case("incident_recording_locations_required", "replace", MODE, "Record incidents in a Worker Delivery", "Record incidents in a Delivery", "missing Phase 7 requirement"),
    Case("timeout_boundary_required", "replace", MODE, "A 429 or timeout does not automatically become a Product\nFinding", "A 429 is a Product Finding", "missing Phase 7 requirement"),
    Case("verification_disclosure_required", "replace", MODE, "Missing\nverification can block Review or Closure", "Verification is always complete", "missing Phase 7 requirement"),
    Case("security_ssrf_trigger_required", "replace", MODE, "SSRF", "network requests", "missing Phase 7 requirement"),
    Case("data_foreign_key_trigger_required", "replace", MODE, "foreign keys", "data keys", "missing Phase 7 requirement"),
    Case("compatibility_web_tauri_trigger_required", "replace", MODE, "Web/Tauri", "host UI", "missing Phase 7 requirement"),
    Case("operations_runbook_trigger_required", "replace", MODE, "runbooks", "operations notes", "missing Phase 7 requirement"),
    Case("accessibility_screen_reader_trigger_required", "replace", MODE, "screen readers", "assistive output", "missing Phase 7 requirement"),
    Case("mmgh_observed_outcomes_required", "replace", MMGH, "## Observed Outcomes", "## Outcomes", "missing Phase 7 requirement"),
    Case("mmgh_protocol_changes_boundary_required", "replace", MMGH, "## Protocol Changes Not Supported", "## Unsupported", "missing Phase 7 requirement"),
    Case("task_status_enum_freeze_rejected", "replace", Path("scripts/validate.py"), '    "integrated",\n}', '    "integrated",\n    "calibrated",\n}', "Phase 7 freeze: Task statuses changed"),
    Case("reviewer_type_enum_freeze_rejected", "replace", Path("scripts/full_loop_execution_validation.py"), '    "domain-expert",\n}', '    "domain-expert",\n    "mode-governance",\n}', "Phase 7 freeze: Reviewer types changed"),
    Case("new_ledger_artifact_rejected", "create", Path(".looppilot/full-loop/MODE-LEDGER.md"), error="unexpected authoritative Ledger artifacts"),
)


class EvaluationCalibrationTests(unittest.TestCase):
    maxDiff = None

    def copy_repository(self, directory: str) -> Path:
        fixture = Path(directory) / "repository"
        copytree_ignore = shutil.ignore_patterns(
            ".git", "__pycache__", ".pytest_cache", "node_modules", ".venv",
            ".tmp", ".venv-*", ".tmp-*",
        )
        shutil.copytree(REPOSITORY_ROOT, fixture, ignore=copytree_ignore)
        return fixture

    def run_validator(self, fixture: Path) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, str(fixture / "scripts" / "validate.py"), "--root", str(fixture)],
            cwd=fixture,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def exercise(self, case: Case) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            path = fixture / case.path
            if case.operation == "delete":
                path.unlink()
            elif case.operation == "replace":
                text = path.read_text(encoding="utf-8")
                self.assertIn(case.old, text)
                path.write_text(text.replace(case.old, case.new, 1), encoding="utf-8")
            elif case.operation == "append":
                path.write_text(path.read_text(encoding="utf-8") + case.new, encoding="utf-8")
            elif case.operation == "create":
                path.write_text("# MODE-LEDGER\n", encoding="utf-8")
            elif case.operation != "noop":
                self.fail(f"unknown operation: {case.operation}")

            result = self.run_validator(fixture)
            output = result.stdout + result.stderr
            if case.error is None:
                self.assertEqual(0, result.returncode, output)
            else:
                self.assertEqual(1, result.returncode, output)
                self.assertIn(case.error, output)


def _make_test(case: Case):
    def test(self: EvaluationCalibrationTests) -> None:
        self.exercise(case)

    test.__name__ = f"test_{case.name}"
    test.__doc__ = case.name.replace("_", " ")
    return test


if len(CASES) < 76 or len({case.name for case in CASES}) != len(CASES):
    raise RuntimeError("Phase 7 requires at least 76 distinct regression cases")

for _index, _case in enumerate(CASES, start=1):
    setattr(
        EvaluationCalibrationTests,
        f"test_{_index:03d}_{_case.name}",
        _make_test(_case),
    )


if __name__ == "__main__":
    unittest.main()
