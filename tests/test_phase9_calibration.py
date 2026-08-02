import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PHASE9 = Path("docs/phase9-second-protocol-calibration.md")
BASELINE = Path("docs/baseline-evidence-and-verification-surface.md")
COORDINATION = Path("docs/coordination-necessity-and-delegation-fallback.md")
FINAL_ASSIGNMENT = Path("docs/final-assignment-behavioral-evidence.md")


@dataclass(frozen=True)
class Case:
    name: str
    operation: str = "noop"
    path: Path = PHASE9
    old: str = ""
    new: str = ""
    error: str | None = None


DOCUMENT_TOKENS = (
    (PHASE9, "evidence -> contradiction -> bounded calibration"),
    (PHASE9, "Only Lightweight and Full Loop are modes."),
    (PHASE9, "Product Risk and Coordination Necessity are independent."),
    (PHASE9, "The Lightweight four-to-seven target counts Governance Artifacts"),
    (PHASE9, "External reference\nverification was unavailable"),
    (BASELINE, "## Repository Baseline"),
    (BASELINE, "## Environment-Corrected Baseline"),
    (BASELINE, "## Scope-Focused Baseline"),
    (BASELINE, "Pre-existing\nfailure attribution MUST be established before claiming a regression."),
    (BASELINE, "## Verification Surface"),
    (BASELINE, "A successful test command proves only the tests it actually selected."),
    (COORDINATION, "## Product Risk and Coordination Risk"),
    (COORDINATION, "High product risk\ndoes not by itself prove that multiple Workers are required."),
    (COORDINATION, "## Coordination Necessity"),
    (COORDINATION, "Lightweight MAY load a risk-matched specialist Reviewer"),
    (COORDINATION, "## Worker Failure Budget"),
    (COORDINATION, "no more than two unsuccessful\nWorker attempts"),
    (COORDINATION, "## Ownership Collapse in Full Loop"),
    (COORDINATION, "Reviewer and Integrator roles MUST NOT become code implementers"),
    (COORDINATION, "## Verifiable Worker Claims"),
    (COORDINATION, "Worker summary is not evidence."),
    (FINAL_ASSIGNMENT, "66dbeb5c99c9cac707f089767428c6c4bbd8836e"),
    (FINAL_ASSIGNMENT, "6b24209f79aed7476b2ad3b54ac4385f06cfe730"),
    (FINAL_ASSIGNMENT, "2ac9919bebe71e45445a2f3d22caa8cb43ab8436"),
    (FINAL_ASSIGNMENT, "6e0ab5f55bcf8c93aa4f36e02af1aedd78ff2207"),
    (FINAL_ASSIGNMENT, "604c4f93b4978e3fd0755a2ba09b3093f54c0d19"),
    (FINAL_ASSIGNMENT, "a75aa0d801857d6e6b08957c74bcb28f7286ca9cd38de401c6798b67ef4bcc15"),
    (FINAL_ASSIGNMENT, "dynamic H-7 single-row persistence holdout is unverified"),
    (FINAL_ASSIGNMENT, "Control archival is\ntherefore incomplete"),
)

TEMPLATE_TOKENS = (
    (Path(".looppilot/PROJECT-TEMPLATE.md"), "## Baseline Evidence"),
    (Path(".looppilot/PROJECT-TEMPLATE.md"), "- Repository Baseline:"),
    (Path(".looppilot/PROJECT-TEMPLATE.md"), "- Environment-Corrected Baseline:"),
    (Path(".looppilot/PROJECT-TEMPLATE.md"), "- Scope-Focused Baseline:"),
    (Path(".looppilot/PROJECT-TEMPLATE.md"), "## Verification Surface"),
    (Path(".looppilot/PROJECT-TEMPLATE.md"), "- Actual discovery:"),
    (Path(".looppilot/PROJECT-TEMPLATE.md"), "- Unreached tests:"),
    (Path(".looppilot/PROJECT-TEMPLATE.md"), "- Product Risk:"),
    (Path(".looppilot/PROJECT-TEMPLATE.md"), "- Coordination Necessity:"),
    (Path(".looppilot/full-loop/LOOP-CONTRACT-TEMPLATE.md"), "## Coordination Necessity"),
    (Path(".looppilot/full-loop/LOOP-CONTRACT-TEMPLATE.md"), "- Why multiple Workers are required:"),
    (Path(".looppilot/full-loop/LOOP-CONTRACT-TEMPLATE.md"), "- Fallback Worker:"),
    (Path(".looppilot/full-loop/LOOP-CONTRACT-TEMPLATE.md"), "- Worker failure budget:"),
    (Path(".looppilot/full-loop/LOOP-CONTRACT-TEMPLATE.md"), "- Ownership-collapse condition:"),
    (Path(".looppilot/full-loop/WORKER-DELIVERY-TEMPLATE.md"), "## Verifiable Claims"),
    (Path(".looppilot/full-loop/WORKER-DELIVERY-TEMPLATE.md"), "| Claim | Evidence | Verification | Git Boundary |"),
    (Path(".looppilot/full-loop/WORKER-DELIVERY-TEMPLATE.md"), "## Unverified Claims"),
    (Path(".looppilot/full-loop/INTEGRATION-RECORD-TEMPLATE.md"), "## Delegation Health"),
    (Path(".looppilot/full-loop/INTEGRATION-RECORD-TEMPLATE.md"), "- Worker attempts:"),
    (Path(".looppilot/full-loop/INTEGRATION-RECORD-TEMPLATE.md"), "- Unsuccessful attempts:"),
    (Path(".looppilot/full-loop/INTEGRATION-RECORD-TEMPLATE.md"), "- Failure budget:"),
    (Path(".looppilot/full-loop/INTEGRATION-RECORD-TEMPLATE.md"), "- Ownership collapsed:"),
    (Path(".looppilot/full-loop/INTEGRATION-RECORD-TEMPLATE.md"), "- Fallback Worker:"),
    (Path(".looppilot/full-loop/CHECKPOINT-TEMPLATE.md"), "- Successful Deliveries:"),
    (Path(".looppilot/full-loop/CHECKPOINT-TEMPLATE.md"), "- Failed delegation attempts:"),
    (Path(".looppilot/full-loop/CHECKPOINT-TEMPLATE.md"), "- Current implementation owner:"),
)

MODE_TOKENS = (
    "## Product Risk and Coordination Necessity",
    "High product risk\ndoes not by itself prove that multiple Workers are required.",
    "four to seven Governance Artifacts",
    "Examples: TypeScript/Rust or Web/Tauri.",
    "A passing command proves only the tests it actually selected;",
)

LOAD_TOKENS = (
    "baseline attribution and Verification Surface",
    "Lightweight MAY add a risk-matched",
    "delegation failure budget",
    "ownership fallback",
)

MIGRATION_TOKENS = (
    "## Phase 8-A: Cross-Project Replication",
    "## Phase 8-B: Controlled Three-Mode Comparison",
    "comparative archive incomplete",
    "## Phase 9: Second Evidence-Backed Protocol Calibration",
    "## Phase 10: Third-Project and/or Cross-Host Replication",
)

FORBIDDEN_CLAIMS = (
    "Product Risk automatically requires Full Loop",
    "Security Reviewer present => Full Loop",
    "Unsuccessful Workers MAY retry indefinitely.",
    "Worker summary is sufficient evidence",
    "EXP-006 fully dynamically validated",
    "H-7 holdout verified",
    "Experiment conclusion: Lightweight is superior to Full Loop.",
    "New Phase 9 mode: calibration",
    "New Phase 9 Ledger: calibration",
    "New Phase 9 status: calibration",
    "New Phase 9 severity: calibration",
    "New Phase 9 Barrier: calibration",
    "New Phase 9 Acceptance layer: calibration",
    "New Phase 9 Recovery authority: calibration",
)


def _legal_case(name: str, statement: str) -> Case:
    return Case(name, "append", PHASE9, new=f"\n{statement}\n")


def _rejected_case(name: str, statement: str) -> Case:
    return Case(name, "append", PHASE9, new=f"\n{statement}\n", error="Phase 9 contradiction")


BEHAVIOR_CASES = (
    # Baseline: 1-7
    _legal_case("green_repository_baseline_legal", "Observed Repository Baseline: green."),
    _legal_case("red_repository_baseline_legal", "Observed Repository Baseline: red."),
    _legal_case(
        "environment_corrected_baseline_legal",
        "Observed Environment-Corrected Baseline after a service prerequisite.",
    ),
    _legal_case(
        "scope_focused_baseline_legal",
        "Observed Scope-Focused Baseline for the bounded change.",
    ),
    _rejected_case(
        "preexisting_failure_as_regression_rejected",
        "A pre-existing failure is always a new regression.",
    ),
    _rejected_case(
        "environment_correction_product_change_rejected",
        "Environment correction MAY change product implementation.",
    ),
    Case(
        "new_baseline_ledger_rejected",
        "create",
        Path(".looppilot/full-loop/BASELINE-LEDGER.md"),
        error="Phase 9 forbidden Ledger artifact",
    ),

    # Verification Surface: 8-14
    _legal_case("maven_include_recorded", "Maven actual test includes are recorded."),
    _legal_case("maven_exclude_recorded", "Maven actual test excludes are recorded."),
    _legal_case("unreached_unit_tests_disclosed", "Unit tests not reached by default are disclosed."),
    _rejected_case(
        "green_maven_means_all_tests_rejected",
        "mvn test exit 0 proves every repository test passed.",
    ),
    _legal_case("flutter_filter_disclosed", "A filtered Flutter test run is disclosed."),
    _legal_case("cargo_ignored_tests_disclosed", "Cargo ignored tests are disclosed."),
    _legal_case("pytest_filter_disclosed", "A filtered pytest run is disclosed."),

    # Product Risk and Coordination Necessity: 15-22
    _legal_case(
        "high_product_risk_single_owner_lightweight",
        "A high-product-risk bounded change with one owner uses Lightweight and deep Review.",
    ),
    _legal_case(
        "security_local_fix_lightweight_review",
        "A bounded local security fix uses Lightweight plus Security Review.",
    ),
    _legal_case(
        "transaction_single_owner_data_review",
        "A single-owner transaction change with deterministic proof uses Lightweight plus Data Review.",
    ),
    _legal_case(
        "multiple_owners_integration_full_loop",
        "Multiple owners with non-trivial integration ordering use Full Loop.",
    ),
    _rejected_case(
        "workers_without_independent_value_rejected",
        "Multiple Workers without independent delivery value require Full Loop.",
    ),
    _rejected_case("file_count_only_full_loop_rejected", "File count alone selects Full Loop."),
    _rejected_case("security_keyword_only_full_loop_rejected", "Security keyword alone selects Full Loop."),
    _rejected_case(
        "full_loop_without_coordination_rationale_rejected",
        "Full Loop requires no Coordination Necessity rationale.",
    ),

    # Specialist-reviewed Lightweight: 23-27
    _legal_case("lightweight_data_review_legal", "Lightweight uses bounded Data Review."),
    _legal_case(
        "lightweight_compatibility_review_legal",
        "Lightweight uses bounded Compatibility Review.",
    ),
    _legal_case("lightweight_security_review_legal", "Lightweight uses bounded Security Review."),
    _rejected_case(
        "specialist_replaces_axes_rejected",
        "A specialist Reviewer replaces Spec and Standards.",
    ),
    _rejected_case(
        "specialist_automatically_full_loop_rejected",
        "A specialist Reviewer automatically creates Full Loop.",
    ),

    # Lightweight escalation: 28-32
    _rejected_case(
        "major_without_escalation_rejected",
        "Lightweight continues after a Major Finding without escalation.",
    ),
    _rejected_case(
        "new_owner_without_reassessment_rejected",
        "New implementation owners do not require mode reassessment.",
    ),
    _rejected_case(
        "integration_record_without_escalation_rejected",
        "A required Integration Record does not require escalation.",
    ),
    _rejected_case(
        "correction_budget_without_escalation_rejected",
        "Lightweight may continue after corrections exceed the budget.",
    ),
    _legal_case(
        "lightweight_continues_without_escalation_trigger",
        "No escalation trigger is present, so Lightweight continues.",
    ),

    # Worker failure budget: 33-39
    _legal_case("zero_failed_worker_attempts_legal", "Zero unsuccessful Worker attempts is within budget."),
    _legal_case("one_failed_worker_attempt_legal", "One unsuccessful Worker attempt is within budget."),
    _legal_case(
        "two_failed_attempts_require_decision",
        "Two unsuccessful Worker attempts require fallback, reassignment, or block.",
    ),
    _rejected_case(
        "third_unrecorded_worker_attempt_rejected",
        "A third unsuccessful Worker attempt needs no record.",
    ),
    _legal_case("fallback_worker_legal", "A designated fallback Worker is recorded."),
    _rejected_case("failed_delivery_deletion_rejected", "Failed Worker Deliveries MAY be deleted."),
    _rejected_case(
        "ownership_collapse_revision_reset_rejected",
        "Ownership collapse resets the Task revision count.",
    ),

    # Role boundaries: 40-44
    _rejected_case(
        "reviewer_implementation_rejected",
        "Reviewer MAY implement product code during fallback.",
    ),
    _rejected_case(
        "integrator_implementation_rejected",
        "Integrator MAY implement product code during fallback.",
    ),
    _rejected_case(
        "supervisor_unrecorded_implementation_rejected",
        "Supervisor MAY implement without recording ownership.",
    ),
    _legal_case(
        "fallback_worker_implementation_legal",
        "The designated fallback Worker owns implementation.",
    ),
    _legal_case(
        "integrator_records_ownership_change",
        "The Integrator records the changed ownership boundary.",
    ),

    # Worker claims: 45-51
    _legal_case("claim_with_code_evidence_legal", "A Worker claim cites exact code evidence."),
    _legal_case("claim_with_test_evidence_legal", "A Worker claim cites exact test evidence."),
    _rejected_case("test_claim_without_command_rejected", "A test-passed claim needs no command evidence."),
    _rejected_case("cross_user_claim_without_evidence_rejected", "Cross-user 403 behavior needs no evidence."),
    _legal_case(
        "unsupported_claim_marked_unverified",
        "An unsupported Worker claim remains in Unverified Claims.",
    ),
    _legal_case(
        "contaminated_claim_becomes_protocol_finding",
        "An unsupported claim that contaminated authority becomes a Protocol Finding.",
    ),
    _rejected_case(
        "unsupported_claim_as_eii_rejected",
        "An unsupported Worker claim is an Execution Infrastructure Incident.",
    ),

    # Artifact accounting: 52-56
    _legal_case(
        "three_artifact_categories_legal",
        "Product, Governance, and Evaluation Artifacts are reported separately.",
    ),
    _legal_case(
        "six_governance_artifacts_lightweight",
        "Six Governance Artifacts remain within the Lightweight target.",
    ),
    _legal_case(
        "ten_evaluation_artifacts_do_not_consume_budget",
        "Ten Evaluation Artifacts do not consume the Governance Artifact target.",
    ),
    _rejected_case(
        "ten_governance_artifacts_without_explanation_rejected",
        "Ten Governance Artifacts need no explanation or reassessment.",
    ),
    _rejected_case("artifact_budget_state_rejected", "Artifact Budget is a lifecycle state."),

    # Technology neutrality: 57-60
    _rejected_case(
        "generic_typescript_rust_requirement_rejected",
        "Generic protocol rules require TypeScript/Rust.",
    ),
    _legal_case("typescript_rust_example_legal", "Example: a TypeScript/Rust boundary."),
    _legal_case("flutter_spring_example_legal", "Example: a Flutter/Spring boundary."),
    _rejected_case("tauri_template_binding_rejected", "Templates default to Tauri."),

    # Experiment evidence: 61-68
    _legal_case(
        "exp006_single_controlled_run_legal",
        "EXP-006 is one bounded controlled run with archive limitations.",
    ),
    _rejected_case("exp006_statistical_proof_rejected", "EXP-006 is statistically proven."),
    _legal_case(
        "lightweight_best_under_fixed_conditions_legal",
        "Lightweight performed best under the fixed EXP-006 task and conditions.",
    ),
    _rejected_case(
        "lightweight_universal_superiority_rejected",
        "Lightweight is universally superior to Full Loop.",
    ),
    _rejected_case("h7_verified_rejected", "H-7 final single-row persistence is verified."),
    _legal_case("h7_unverified_legal", "H-7 final single-row persistence remains unverified."),
    _rejected_case("blocked_full_loop_delivered_rejected", "The blocked Full Loop arm was delivered."),
    _legal_case(
        "blocked_closure_honest_legal",
        "The blocked Full Loop arm remains not delivered.",
    ),

    # Freeze invariants: 69-76
    _rejected_case("new_mode_rejected", "New Phase 9 mode: calibration"),
    _rejected_case("new_role_rejected", "New Phase 9 role: calibration"),
    _rejected_case("new_ledger_rejected", "New Phase 9 Ledger: calibration"),
    _rejected_case("new_task_status_rejected", "New Phase 9 status: calibration"),
    _rejected_case("new_severity_rejected", "New Phase 9 severity: calibration"),
    _rejected_case("new_barrier_rejected", "New Phase 9 Barrier: calibration"),
    _rejected_case("new_acceptance_rejected", "New Phase 9 Acceptance layer: calibration"),
    _legal_case(
        "checkpoint_authority_preserved",
        "CHECKPOINT.md remains the only recovery authority.",
    ),
)

def _required_cases(prefix: str, entries: tuple[tuple[Path, str], ...]) -> tuple[Case, ...]:
    return tuple(
        Case(
            f"{prefix}_{index:03d}",
            "replace",
            path,
            token,
            "removed Phase 9 requirement",
            "missing Phase 9 requirement",
        )
        for index, (path, token) in enumerate(entries, start=1)
    )


CASES = (
    Case("legal_phase9_structure_passes", "append", PHASE9, new="\nStatic calibration remains bounded.\n"),
    *BEHAVIOR_CASES,
    *(Case(
        f"missing_phase9_file_{index:02d}",
        "delete",
        Path(path),
        error="No module named 'phase9_calibration_validation'" if index == 5 else "missing required file",
    ) for index, path in enumerate((
        "docs/phase9-second-protocol-calibration.md",
        "docs/baseline-evidence-and-verification-surface.md",
        "docs/coordination-necessity-and-delegation-fallback.md",
        "docs/final-assignment-behavioral-evidence.md",
        "scripts/phase9_calibration_validation.py",
        "tests/test_phase9_calibration.py",
    ), start=1)),
    *_required_cases("document_requirement", DOCUMENT_TOKENS),
    *_required_cases("template_requirement", TEMPLATE_TOKENS),
    *_required_cases("mode_requirement", tuple((Path("docs/mode-selection-and-escalation.md"), token) for token in MODE_TOKENS)),
    *_required_cases("load_requirement", tuple((Path("docs/protocol-load-profiles.md"), token) for token in LOAD_TOKENS)),
    *_required_cases("migration_requirement", tuple((Path("docs/full-loop-migration-plan.md"), token) for token in MIGRATION_TOKENS)),
    Case("phase9_scenario_start_required", "replace", Path("tests/scenarios.md"), "## 234. High Product Risk With One Owner", "## scenario removed", "missing Phase 9 requirement"),
    Case("phase9_scenario_end_required", "replace", Path("tests/scenarios.md"), "## 263. Phase 10 Evidence Stays Separately Attributed", "## scenario removed", "missing Phase 9 requirement"),
    Case("phase9_rubric_baseline_required", "replace", Path("tests/evaluation-rubric.md"), "Attributes Repository, Environment-Corrected, and Scope-Focused evidence before a regression claim.", "Baseline unknown", "missing Phase 9 requirement"),
    Case("phase9_rubric_coordination_required", "replace", Path("tests/evaluation-rubric.md"), "Shows why multiple owners, integration, recovery, or rework governance is actually needed.", "Coordination unknown", "missing Phase 9 requirement"),
    Case("phase9_rubric_closure_required", "replace", Path("tests/evaluation-rubric.md"), "States missing Deliveries, verification, acceptance, and remaining authority precisely.", "Closure unknown", "missing Phase 9 requirement"),
    *(Case(f"forbidden_claim_{index:02d}", "append", PHASE9, new=f"\n{claim}\n", error="Phase 9 contradiction") for index, claim in enumerate(FORBIDDEN_CLAIMS, start=1)),
    *(Case(f"forbidden_ledger_{name.lower().replace('-', '_').replace('.', '_')}", "create", Path(".looppilot/full-loop") / name, error="Phase 9 forbidden Ledger artifact") for name in (
        "BASELINE-LEDGER.md", "CLAIM-LEDGER.md", "EVIDENCE-LEDGER.md",
    )),
    Case("core_prompt_budget_enforced", "append", Path("SKILL.md"), new="\n" + ("budget evidence\n" * 32), error="Phase 9 core prompt budget exceeded"),
)


class Phase9CalibrationTests(unittest.TestCase):
    maxDiff = None

    def copy_repository(self, directory: str) -> Path:
        fixture = Path(directory) / "repository"
        shutil.copytree(
            REPOSITORY_ROOT,
            fixture,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", ".tmp",
            ),
        )
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
                path.write_text("# forbidden artifact\n", encoding="utf-8")
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
    def test(self: Phase9CalibrationTests) -> None:
        self.exercise(case)

    test.__name__ = f"test_{case.name}"
    return test


if len(BEHAVIOR_CASES) != 76 or len({case.name for case in BEHAVIOR_CASES}) != 76:
    raise RuntimeError("Phase 9 behavior matrix requires exactly 76 distinct invariant cases")
if len(CASES) < 76 or len({case.name for case in CASES}) != len(CASES):
    raise RuntimeError("Phase 9 requires at least 76 distinct regression cases")

for _index, _case in enumerate(CASES, start=1):
    setattr(Phase9CalibrationTests, f"test_{_index:03d}_{_case.name}", _make_test(_case))


if __name__ == "__main__":
    unittest.main()
