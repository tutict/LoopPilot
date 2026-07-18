import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate.py"
FULL_LOOP = Path(".looppilot/full-loop")
WORKER = FULL_LOOP / "WORKER-DELIVERY-TEMPLATE.md"
INTEGRATION = FULL_LOOP / "INTEGRATION-RECORD-TEMPLATE.md"
REVIEW = FULL_LOOP / "REVIEW-REPORT-TEMPLATE.md"
FINDING = FULL_LOOP / "FINDING-TEMPLATE.md"
REWORK = FULL_LOOP / "REWORK-TASK-TEMPLATE.md"
CLOSURE = FULL_LOOP / "LOOP-CLOSURE-TEMPLATE.md"
PROTOCOL = Path("docs/full-loop-delivery-review-and-closure.md")


class FullLoopDeliveryReviewClosureTests(unittest.TestCase):
    def copy_repository(self, directory: str) -> Path:
        fixture = Path(directory) / "repository"
        copytree(
            REPOSITORY_ROOT,
            fixture,
            ignore=lambda _path, names: [
                name
                for name in names
                if name
                in {
                    ".git",
                    "__pycache__",
                    ".pytest_cache",
                    "node_modules",
                    ".venv",
                    ".tmp",
                }
                or name.startswith(".tmp-")
                or name.startswith(".venv-")
            ],
        )
        return fixture

    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--root", str(root)],
            cwd=REPOSITORY_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def validate_fixture(self, mutator=None) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            if mutator is not None:
                mutator(fixture)
            return self.run_validator(fixture)

    @staticmethod
    def replace_once(path: Path, old: str, new: str) -> None:
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"fixture text not found in {path}: {old!r}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    @staticmethod
    def append(path: Path, text: str) -> None:
        path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")

    def assert_rejected(self, mutator, message: str) -> None:
        result = self.validate_fixture(mutator)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(message, result.stdout)

    def test_valid_phase_three_template_collection_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_blocked_closure_passes(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace_once(
                fixture / CLOSURE,
                "- Closure Status: inactive",
                "- Closure Status: blocked",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_unauthorized_commit_expression_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_unresolved_blocker_prevents_ready_closure(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace_once(
                fixture / CLOSURE,
                "- Closure Status: inactive",
                "- Closure Status: ready-for-acceptance",
            )
            self.replace_once(
                fixture / CLOSURE,
                "| None | none | none | none | none |",
                "| FINDING-001 | blocker | open | pending | evidence |",
            )

        self.assert_rejected(mutate, "unresolved blocker prevents Closure readiness")

    def test_major_finding_requires_concrete_outcome(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace_once(fixture / FINDING, "- Severity: none", "- Severity: major")

        self.assert_rejected(mutate, "requires a concrete Required Outcome")

    def test_other_finding_category_requires_explanation(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace_once(fixture / FINDING, "- Category: none", "- Category: other")

        self.assert_rejected(mutate, "category other requires an explanation")

    def test_active_rework_requires_originating_finding(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace_once(
                fixture / REWORK,
                "- Rework Task ID: none",
                "- Rework Task ID: TASK-001-R1",
            )

        self.assert_rejected(mutate, "active Rework Task requires Originating Findings")

    def mark_acceptance(self, path: Path) -> None:
        for _ in range(3):
            self.replace_once(path, "- [ ] None.", "- [x] Verified.")

    def pass_preclosure_barriers(self, path: Path) -> None:
        for barrier in ("Contract", "Implementation", "Integration", "Review"):
            self.replace_once(
                path,
                f"- {barrier} Barrier: not-evaluated",
                f"- {barrier} Barrier: passed",
            )

    def test_ready_closure_requires_all_acceptance_layers(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace_once(
                fixture / CLOSURE,
                "- Closure Status: inactive",
                "- Closure Status: ready-for-acceptance",
            )

        self.assert_rejected(mutate, "Functional Acceptance must pass before Closure readiness")

    def test_ready_closure_requires_standards_pass(self) -> None:
        def mutate(fixture: Path) -> None:
            path = fixture / CLOSURE
            self.replace_once(path, "- Closure Status: inactive", "- Closure Status: ready-for-acceptance")
            self.mark_acceptance(path)
            self.replace_once(path, "- Result: not-evaluated", "- Result: pass")
            self.pass_preclosure_barriers(path)

        self.assert_rejected(mutate, "Standards Review must pass before Closure readiness")

    def test_ready_closure_requires_spec_pass(self) -> None:
        def mutate(fixture: Path) -> None:
            path = fixture / CLOSURE
            self.replace_once(path, "- Closure Status: inactive", "- Closure Status: ready-for-acceptance")
            self.mark_acceptance(path)
            self.pass_preclosure_barriers(path)

        self.assert_rejected(mutate, "Spec Review must pass before Closure readiness")

    def test_accepted_closure_requires_closure_barrier(self) -> None:
        def mutate(fixture: Path) -> None:
            path = fixture / CLOSURE
            self.replace_once(path, "- Closure Status: inactive", "- Closure Status: accepted")
            self.mark_acceptance(path)
            for _ in range(2):
                self.replace_once(path, "- Result: not-evaluated", "- Result: pass")
            self.pass_preclosure_barriers(path)

        self.assert_rejected(mutate, "Closure Barrier must pass before accepted")

    def test_unresolved_major_requires_explicit_disposition(self) -> None:
        def mutate(fixture: Path) -> None:
            path = fixture / CLOSURE
            self.replace_once(path, "- Closure Status: inactive", "- Closure Status: ready-for-acceptance")
            self.replace_once(
                path,
                "| None | none | none | none | none |",
                "| FINDING-001 | major | open | pending | evidence |",
            )

        self.assert_rejected(mutate, "unresolved major requires an explicit disposition")


MISSING_CASES = (
    ("worker_delivery", WORKER),
    ("integration_record", INTEGRATION),
    ("review_report", REVIEW),
    ("finding_detail", FINDING),
    ("rework_task", REWORK),
    ("loop_closure", CLOSURE),
    ("phase_three_protocol", PROTOCOL),
)


MUTATION_CASES = (
    # Worker Delivery
    ("worker_invalid_status", WORKER, "- Delivery Status: none", "- Delivery Status: running", "invalid Delivery Status"),
    ("worker_claims_approved", WORKER, "- Delivery Status: none", "- Delivery Status: approved", "authority-only status"),
    ("worker_claims_integrated", WORKER, "- Delivery Status: none", "- Delivery Status: integrated", "authority-only status"),
    ("worker_claims_accepted", WORKER, "- Delivery Status: none", "- Delivery Status: accepted", "authority-only status"),
    ("worker_claims_closed", WORKER, "- Delivery Status: none", "- Delivery Status: closed", "authority-only status"),
    ("worker_missing_scope", WORKER, "## Scope Confirmation", "## Scope Omitted", "missing required heading '## Scope Confirmation'"),
    ("worker_missing_changed_artifacts", WORKER, "## Changed Artifacts", "## Artifacts Omitted", "missing required heading '## Changed Artifacts'"),
    ("worker_missing_verification", WORKER, "## Verification Performed", "## Checks Omitted", "missing required heading '## Verification Performed'"),
    ("worker_missing_skipped_verification", WORKER, "## Skipped Verification", "## Skips Omitted", "missing required heading '## Skipped Verification'"),
    ("worker_missing_evidence", WORKER, "## Evidence", "## Proof Omitted", "missing required heading '## Evidence'"),
    ("worker_missing_limitations", WORKER, "## Known Limitations", "## Limits Omitted", "missing required heading '## Known Limitations'"),
    ("worker_missing_requested_decisions", WORKER, "## Requested Decisions", "## Decisions Omitted", "missing required heading '## Requested Decisions'"),
    ("worker_fake_test_pass", WORKER, "| None | not-run | none |", "| unit tests | passed | none |", "fabricates passing verification"),
    ("worker_is_task_authority", WORKER, "`TASK-LEDGER.md` remains the only Task\nstatus source.", "Delivery is the Task status source.", "Delivery must not be a Task status authority"),
    ("worker_real_task_in_template", WORKER, "- Task ID: none", "- Task ID: TASK-001", "inactive template contains a real Task ID"),
    ("worker_real_worker_in_template", WORKER, "- Worker: none", "- Worker: worker-a", "inactive template contains a real Worker"),
    # Integration Record
    ("integration_invalid_status", INTEGRATION, "- Status: inactive", "- Status: ready", "invalid Integration Status"),
    ("integration_missing_included", INTEGRATION, "### Included Deliveries", "### Inputs Omitted", "missing required heading '### Included Deliveries'"),
    ("integration_missing_excluded", INTEGRATION, "### Excluded Deliveries", "### Exclusions Omitted", "missing required heading '### Excluded Deliveries'"),
    ("integration_missing_order", INTEGRATION, "## Integration Order", "## Order Omitted", "missing required heading '## Integration Order'"),
    ("integration_missing_mechanical", INTEGRATION, "## Mechanical Conflicts", "## Mechanical Omitted", "missing required heading '## Mechanical Conflicts'"),
    ("integration_missing_semantic", INTEGRATION, "## Semantic Conflicts Escalated", "## Semantic Omitted", "missing required heading '## Semantic Conflicts Escalated'"),
    ("integration_missing_build", INTEGRATION, "## Build Verification", "## Build Omitted", "missing required heading '## Build Verification'"),
    ("integration_missing_tests", INTEGRATION, "## Integration Tests", "## Tests Omitted", "missing required heading '## Integration Tests'"),
    ("integration_missing_unintegrated", INTEGRATION, "## Unintegrated Work", "## Work Omitted", "missing required heading '## Unintegrated Work'"),
    ("integration_missing_barrier", INTEGRATION, "## Integration Barrier Assessment", "## Barrier Omitted", "missing required heading '## Integration Barrier Assessment'"),
    ("integration_accepts_risk", INTEGRATION, "The Integrator records integration facts", "The Integrator may accept risk. The Integrator records integration facts", "Integrator must not accept risk"),
    ("integration_changes_scope", INTEGRATION, "The Integrator records integration facts", "The Integrator may change Scope. The Integrator records integration facts", "Integrator must not change Scope"),
    ("integration_maps_closed", INTEGRATION, "`integrated` does not mean\n`accepted`, `closed`, or `[x]`", "`integrated` means `closed`", "integrated must not map to Loop closed"),
    ("integration_fake_build_pass", INTEGRATION, "| None | not-run | none |", "| build | passed | none |", "fabricates a passing build"),
    ("integration_is_loop_authority", INTEGRATION, "`LOOP-MAP.md` remains the Loop status source.", "Integration Record is the Loop status source.", "Integration Record must not be a Loop status authority"),
    # Review Report
    ("review_invalid_type", REVIEW, "- Reviewer Type: none", "- Reviewer Type: pirate", "invalid Reviewer Type"),
    ("review_invalid_status", REVIEW, "- Status: inactive", "- Status: running", "invalid Review Status"),
    ("review_invalid_verdict", REVIEW, "- Verdict: none", "- Verdict: maybe", "invalid Reviewer Verdict"),
    ("review_missing_scope", REVIEW, "## Review Scope", "## Scope Omitted", "missing required heading '## Review Scope'"),
    ("review_missing_evidence", REVIEW, "## Evidence Reviewed", "## Evidence Omitted", "missing required heading '## Evidence Reviewed'"),
    ("review_missing_checks", REVIEW, "## Checks Performed", "## Checks Omitted", "missing required heading '## Checks Performed'"),
    ("review_missing_findings", REVIEW, "## Findings Created", "## Findings Omitted", "missing required heading '## Findings Created'"),
    ("review_missing_coverage", REVIEW, "## Coverage Limitations", "## Coverage Omitted", "missing required heading '## Coverage Limitations'"),
    ("review_missing_standards", REVIEW, "## Standards Review Contribution", "## Standards Omitted", "missing required heading '## Standards Review Contribution'"),
    ("review_missing_spec", REVIEW, "## Spec Review Contribution", "## Spec Omitted", "missing required heading '## Spec Review Contribution'"),
    ("review_modifies_implementation", REVIEW, "The Reviewer judges", "The Reviewer may modify implementation. The Reviewer judges", "Reviewer must not modify implementation"),
    ("review_accepts_risk", REVIEW, "The Reviewer judges", "The Reviewer may accept risk. The Reviewer judges", "Reviewer must not accept risk"),
    ("review_updates_ledger", REVIEW, "The Reviewer judges", "The Reviewer may update authoritative Ledgers. The Reviewer judges", "Reviewer must not update authoritative Ledgers"),
    ("review_specialist_auto_axes", REVIEW, "Final Loop review requires", "A specialist automatically makes Spec and Standards pass. Final Loop review requires", "specialist Review must not automatically pass both axes"),
    ("review_is_finding_authority", REVIEW, "`FINDING-LEDGER.md` remains authoritative.", "Review Report owns Finding status.", "Review Report must not own Finding status"),
    # Finding Detail
    ("finding_missing_review_id", FINDING, "- Review ID: none", "- Source Review: none", "missing required field 'Review ID'"),
    ("finding_missing_evidence", FINDING, "## Evidence", "## Evidence Omitted", "missing required heading '## Evidence'"),
    ("finding_missing_expected", FINDING, "## Expected Behavior", "## Expected Omitted", "missing required heading '## Expected Behavior'"),
    ("finding_missing_actual", FINDING, "## Actual Behavior", "## Actual Omitted", "missing required heading '## Actual Behavior'"),
    ("finding_missing_risk", FINDING, "## Risk", "## Risk Omitted", "missing required heading '## Risk'"),
    ("finding_missing_outcome", FINDING, "## Required Outcome", "## Outcome Omitted", "missing required heading '## Required Outcome'"),
    ("finding_missing_verification", FINDING, "## Verification Method", "## Verification Omitted", "missing required heading '## Verification Method'"),
    ("finding_contains_status", FINDING, "- Severity: none", "- Severity: none\n- Status: closed", "must not contain authoritative Status"),
    ("finding_is_status_source", FINDING, "Status is maintained only in `FINDING-LEDGER.md`.", "Status is maintained in this detail.", "Finding Detail must not be a Finding status source"),
    ("finding_vague", FINDING, "No Finding recorded.", "Code is bad.", "Finding must be specific and verifiable"),
    ("finding_invalid_id", FINDING, "- Finding ID: none", "- Finding ID: ISSUE-1", "invalid Finding ID"),
    ("finding_invalid_review_id", FINDING, "- Review ID: none", "- Review ID: REVIEW-X", "invalid Review ID"),
    ("finding_invalid_severity", FINDING, "- Severity: none", "- Severity: critical", "invalid Finding severity"),
    # Rework Task
    ("rework_invalid_id", REWORK, "- Rework Task ID: none", "- Rework Task ID: TASK-001-FIX", "invalid Rework Task ID"),
    ("rework_r0", REWORK, "- Rework Task ID: none", "- Rework Task ID: TASK-001-R0", "revision must start at R1"),
    ("rework_invalid_parent", REWORK, "- Parent Task: none", "- Parent Task: TASK-X", "invalid Parent Task"),
    ("rework_missing_parent", REWORK, "- Parent Task: none", "- Original Task: none", "missing required field 'Parent Task'"),
    ("rework_missing_findings", REWORK, "## Originating Findings", "## Findings Omitted", "missing required heading '## Originating Findings'"),
    ("rework_missing_allowed", REWORK, "## Allowed Scope", "## Allowed Omitted", "missing required heading '## Allowed Scope'"),
    ("rework_missing_forbidden", REWORK, "## Forbidden Scope", "## Forbidden Omitted", "missing required heading '## Forbidden Scope'"),
    ("rework_missing_required_verification", REWORK, "## Required Verification", "## Verification Omitted", "missing required heading '## Required Verification'"),
    ("rework_missing_reverification", REWORK, "## Reviewer Reverification", "## Reverification Omitted", "missing required heading '## Reviewer Reverification'"),
    ("rework_missing_strategy", REWORK, "## Strategy Change", "## Strategy Omitted", "missing required heading '## Strategy Change'"),
    ("rework_missing_escalation", REWORK, "## Escalation Conditions", "## Escalation Omitted", "missing required heading '## Escalation Conditions'"),
    ("rework_missing_authority", REWORK, "## Authority", "## Authority Omitted", "missing required heading '## Authority'"),
    ("rework_missing_completion", REWORK, "## Completion Boundary", "## Completion Omitted", "missing required heading '## Completion Boundary'"),
    ("rework_revision_over_budget", REWORK, "- Revision: none\n- Revision Budget: none", "- Revision: 2\n- Revision Budget: 1", "revision exceeds Revision Budget"),
    ("rework_repeats_strategy", REWORK, "- Previous approach: none\n- Why it failed: none\n- New approach: none\n- Material change: none", "- Previous approach: retry\n- Why it failed: same error\n- New approach: retry\n- Material change: no", "repeated failed approach requires a material Strategy Change"),
    ("rework_closes_finding", REWORK, "Completion of this Rework Task does not close a Finding", "Completion of this Rework Task closes a Finding", "Rework Task must not close its Finding"),
    ("rework_commit_yes", REWORK, "- Commit: inherited-no", "- Commit: yes", "Rework Commit authority must be no or inherited-no"),
    ("rework_push_yes", REWORK, "- Push: inherited-no", "- Push: yes", "Rework Push authority must be no or inherited-no"),
    # Loop Closure
    ("closure_invalid_status", CLOSURE, "- Closure Status: inactive", "- Closure Status: complete", "invalid Closure Status"),
    ("closure_missing_spec", CLOSURE, "### Spec Review", "### Spec Omitted", "missing required heading '### Spec Review'"),
    ("closure_missing_standards", CLOSURE, "### Standards Review", "### Standards Omitted", "missing required heading '### Standards Review'"),
    ("closure_missing_findings", CLOSURE, "## Finding Disposition", "## Findings Omitted", "missing required heading '## Finding Disposition'"),
    ("closure_missing_functional", CLOSURE, "### Functional Acceptance", "### Functional Omitted", "missing required heading '### Functional Acceptance'"),
    ("closure_missing_engineering", CLOSURE, "### Engineering Acceptance", "### Engineering Omitted", "missing required heading '### Engineering Acceptance'"),
    ("closure_missing_delivery", CLOSURE, "### Delivery Acceptance", "### Delivery Omitted", "missing required heading '### Delivery Acceptance'"),
    ("closure_missing_contract_barrier", CLOSURE, "- Contract Barrier: not-evaluated", "- Contract gate: not-evaluated", "missing required Barrier 'Contract Barrier'"),
    ("closure_missing_implementation_barrier", CLOSURE, "- Implementation Barrier: not-evaluated", "- Implementation gate: not-evaluated", "missing required Barrier 'Implementation Barrier'"),
    ("closure_missing_integration_barrier", CLOSURE, "- Integration Barrier: not-evaluated", "- Integration gate: not-evaluated", "missing required Barrier 'Integration Barrier'"),
    ("closure_missing_review_barrier", CLOSURE, "- Review Barrier: not-evaluated", "- Review gate: not-evaluated", "missing required Barrier 'Review Barrier'"),
    ("closure_missing_closure_barrier", CLOSURE, "- Closure Barrier: not-evaluated", "- Closure gate: not-evaluated", "missing required Barrier 'Closure Barrier'"),
    ("closure_recovery_without_checkpoint", CLOSURE, "- Recovery readiness: no", "- Recovery readiness: yes", "recovery-ready requires a valid Checkpoint"),
    ("closure_unauthorized_commit_created", CLOSURE, "- Commit result: not-created-not-required", "- Commit result: created", "created Commit requires explicit authorization"),
    ("closure_accepted_sets_closed", CLOSURE, "`accepted` is only a\nClosure decision; it does not set Loop status to `closed`", "Closure accepted sets Loop closed", "Closure accepted must not set Loop closed"),
    ("closure_hides_skipped_verification", CLOSURE, "- Skipped verification: none", "- Verification omissions: hidden", "missing required field 'Skipped verification'"),
    ("closure_is_loop_authority", CLOSURE, "`LOOP-MAP.md` remains the only authoritative Loop status source", "Loop Closure is the authoritative Loop status source", "Loop Closure must not be a Loop status authority"),
)


def _missing_test(name: str, relative: Path):
    def test(self: FullLoopDeliveryReviewClosureTests) -> None:
        self.assert_rejected(
            lambda fixture: (fixture / relative).unlink(),
            f"missing required file: {relative.as_posix()}",
        )

    test.__name__ = f"test_missing_{name}_is_rejected"
    return test


def _mutation_test(name: str, relative: Path, old: str, new: str, message: str):
    def test(self: FullLoopDeliveryReviewClosureTests) -> None:
        self.assert_rejected(
            lambda fixture: self.replace_once(fixture / relative, old, new),
            message,
        )

    test.__name__ = f"test_{name}_is_rejected"
    return test


for _name, _relative in MISSING_CASES:
    setattr(
        FullLoopDeliveryReviewClosureTests,
        f"test_missing_{_name}_is_rejected",
        _missing_test(_name, _relative),
    )

for _case in MUTATION_CASES:
    setattr(
        FullLoopDeliveryReviewClosureTests,
        f"test_{_case[0]}_is_rejected",
        _mutation_test(*_case),
    )


if __name__ == "__main__":
    unittest.main()
