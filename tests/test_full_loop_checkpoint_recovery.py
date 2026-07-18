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
CHECKPOINT = FULL_LOOP / "CHECKPOINT-TEMPLATE.md"
MANIFEST = FULL_LOOP / "CONTEXT-COMPACTION-TEMPLATE.md"
RESUME = FULL_LOOP / "RESUME-VALIDATION-TEMPLATE.md"
PROTOCOL = Path("docs/full-loop-checkpoint-and-context-recovery.md")


class FullLoopCheckpointRecoveryTests(unittest.TestCase):
    def copy_repository(self, directory: str) -> Path:
        fixture = Path(directory) / "repository"
        copytree(
            REPOSITORY_ROOT,
            fixture,
            ignore=lambda _path, names: [
                name for name in names
                if name in {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", ".tmp"}
                or name.startswith(".tmp-") or name.startswith(".venv-")
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

    def mark_checkpoint_ready(self, fixture: Path, item: str = "TASK-004-R1") -> None:
        path = fixture / CHECKPOINT
        replacements = (
            ("- Checkpoint ID: none", "- Checkpoint ID: CHECKPOINT-004"),
            ("- Checkpoint Status: inactive", "- Checkpoint Status: ready"),
            ("- Recovery ready: no", "- Recovery ready: yes"),
            ("- Required references present: no", "- Required references present: yes"),
            ("- Exact Resume Point actionable: no", "- Exact Resume Point actionable: yes"),
            ("- Resume item: none", f"- Resume item: {item}"),
            ("- Resume action: none", "- Resume action: Run the required integration verification."),
            ("- Required inputs: none", "- Required inputs: current Task, Integration Record, and Finding Ledger"),
            ("- Required tool or capability: none", "- Required tool or capability: repository shell and test runner"),
            ("- Expected observable result: none", "- Expected observable result: observed test result recorded in the Integration Record"),
            ("- Stop or escalation condition: none", "- Stop or escalation condition: any failure outside authorized Rework scope"),
        )
        for old, new in replacements:
            self.replace_once(path, old, new)

    def mark_budget_stopped(self, fixture: Path) -> None:
        self.mark_checkpoint_ready(fixture)
        path = fixture / CHECKPOINT
        self.replace_once(path, "- Checkpoint Status: ready", "- Checkpoint Status: budget-stopped")
        self.replace_once(path, "## Unfinished Work\n\n- None.", "## Unfinished Work\n\n- TASK-004-R1 still requires integration verification.")
        self.replace_once(path, "- Trigger: none", "- Trigger: critical context pressure")
        self.replace_once(path, "- Persisted state: none", "- Persisted state: Task and Finding Ledgers saved")
        self.replace_once(path, "- Authoritative state updated: none", "- Authoritative state updated: yes")

    def mark_manifest_ready(self, fixture: Path) -> None:
        path = fixture / MANIFEST
        self.replace_once(path, "- Checkpoint: none", "- Checkpoint: CHECKPOINT-004")
        self.replace_once(path, "- Manifest Status: inactive", "- Manifest Status: ready")
        self.replace_once(
            path,
            "| None | none | none | no |",
            "| Current Task Ledger | `TASK-LEDGER.md` | validate active Task | yes |",
        )

    def mark_resume_validated(self, fixture: Path, corrected: bool = False) -> None:
        path = fixture / RESUME
        status = "validated-with-corrections" if corrected else "validated"
        self.replace_once(path, "- Validation Status: inactive", f"- Validation Status: {status}")
        self.replace_once(path, "- Safe to resume: no", "- Safe to resume: yes")
        self.replace_once(path, "- Required Skills available: unknown", "- Required Skills available: yes")
        if corrected:
            self.replace_once(path, "## Corrections Applied\n\n- None.", "## Corrections Applied\n\n- Corrected stale HEAD from observed Git state.")

    def test_valid_phase_four_template_collection_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_inactive_checkpoint_template_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_ready_checkpoint_passes(self) -> None:
        result = self.validate_fixture(self.mark_checkpoint_ready)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_budget_stopped_checkpoint_passes(self) -> None:
        result = self.validate_fixture(self.mark_budget_stopped)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_inactive_manifest_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_ready_manifest_passes(self) -> None:
        result = self.validate_fixture(self.mark_manifest_ready)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_inactive_resume_report_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_resume_report_with_corrections_passes(self) -> None:
        result = self.validate_fixture(lambda fixture: self.mark_resume_validated(fixture, corrected=True))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_blocked_resume_report_passes(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace_once(fixture / RESUME, "- Validation Status: inactive", "- Validation Status: blocked")

        result = self.validate_fixture(mutate)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_single_recovery_authority_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_budget_stop_protocol_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_task_resume_point_passes(self) -> None:
        result = self.validate_fixture(self.mark_checkpoint_ready)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_finding_reverification_resume_point_passes(self) -> None:
        result = self.validate_fixture(lambda fixture: self.mark_checkpoint_ready(fixture, "FINDING-007"))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_integration_verification_resume_point_passes(self) -> None:
        result = self.validate_fixture(lambda fixture: self.mark_checkpoint_ready(fixture, "INTEGRATION-003"))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


MISSING_CASES = (
    ("checkpoint_template", CHECKPOINT),
    ("context_compaction_template", MANIFEST),
    ("resume_validation_template", RESUME),
    ("phase_four_protocol", PROTOCOL),
)

SIMPLE_MUTATION_CASES = (
    ("checkpoint_invalid_status", CHECKPOINT, "- Checkpoint Status: inactive", "- Checkpoint Status: complete", "invalid Checkpoint Status"),
    ("invalid_checkpoint_recovery_ready", CHECKPOINT, "- Checkpoint Status: inactive\n- Replaces: none", "- Checkpoint Status: invalid\n- Replaces: none", "invalid Checkpoint cannot be recovery-ready", (("- Recovery ready: no", "- Recovery ready: yes"),)),
    ("superseded_checkpoint_without_reference", CHECKPOINT, "- Checkpoint Status: inactive", "- Checkpoint Status: superseded", "superseded Checkpoint requires replacement reference"),
    ("inactive_checkpoint_fake_head", CHECKPOINT, "- Verified HEAD: none", "- Verified HEAD: abc1234", "inactive template contains a real Verified HEAD"),
    ("inactive_checkpoint_fake_authority", CHECKPOINT, "- Commit authorized: no", "- Commit authorized: yes", "inactive template fabricates Commit authorized authority"),
    ("unauthorized_commit_created", CHECKPOINT, "- Commit result: not-created", "- Commit result: created", "created Commit requires explicit authorization"),
    ("checkpoint_owns_loop_status", CHECKPOINT, "it does not own Project Scope", "Checkpoint owns Loop status. It does not own Project Scope", "Checkpoint must not own Loop status"),
    ("checkpoint_owns_task_status", CHECKPOINT, "it does not own Project Scope", "Checkpoint owns Task status. It does not own Project Scope", "Checkpoint must not own Task status"),
    ("checkpoint_owns_finding_status", CHECKPOINT, "it does not own Project Scope", "Checkpoint owns Finding status. It does not own Project Scope", "Checkpoint must not own Finding status"),
    ("checkpoint_private_reasoning", CHECKPOINT, "## Honesty Boundary", "Checkpoint contains private chain-of-thought.\n\n## Honesty Boundary", "must not contain private chain-of-thought"),
    ("manifest_invalid_status", MANIFEST, "- Manifest Status: inactive", "- Manifest Status: active", "invalid Manifest Status"),
    ("manifest_must_not_loads_task_ledger", MANIFEST, "- Complete conversation history.", "- Current `TASK-LEDGER.md`.", "Must Not Load cannot exclude current authority"),
    ("manifest_is_recovery_authority", MANIFEST, "This Manifest is not a Recovery authority", "Manifest is the Recovery authority", "Manifest must not be a Recovery authority"),
    ("compacted_fact_without_source", MANIFEST, "  - Source: none", "  - Provenance: none", "Compacted Facts must require Source"),
    ("manifest_requires_complete_chat", MANIFEST, "Must Load contains the latest user instruction", "Must Load complete conversation history. Must Load contains the latest user instruction", "must not require complete conversation history"),
    ("manifest_private_reasoning", MANIFEST, "## Authority Note", "Manifest contains private chain-of-thought.\n\n## Authority Note", "must not contain private chain-of-thought"),
    ("resume_invalid_status", RESUME, "- Validation Status: inactive", "- Validation Status: complete", "invalid Validation Status"),
    ("resume_validation_expands_scope", RESUME, "Resume Validation may correct", "Resume Validation may expand Project Scope. Resume Validation may correct", "must not expand Scope"),
    ("resume_validation_grants_commit", RESUME, "Resume Validation may correct", "Resume Validation may grant commit authority. Resume Validation may correct", "must not expand commit authority"),
    ("manifest_second_recovery_authority", Path(".looppilot/full-loop/README.md"), "## Template Set", "Manifest is the Recovery authority.\n\n## Template Set", "Manifest must not be a Recovery authority"),
    ("resume_report_second_recovery_authority", RESUME, "Resume Validation may correct", "Resume Report is the Recovery authority. Resume Validation may correct", "Resume Report must not be a Recovery authority"),
    ("handoff_second_recovery_authority", Path(".looppilot/HANDOFF.md"), "# Agent Handoff", "# Agent Handoff\n\nHandoff is the Recovery authority.", "Handoff must not be a Recovery authority"),
    ("checklist_second_recovery_authority", Path(".looppilot/CHECKLIST.md"), "# Parent Goal Checklist", "# Parent Goal Checklist\n\nChecklist is the Recovery authority.", "Checklist must not be a Recovery authority"),
    ("closure_second_recovery_authority", FULL_LOOP / "LOOP-CLOSURE-TEMPLATE.md", "# Loop Closure TEMPLATE", "# Loop Closure TEMPLATE\n\nClosure is the Recovery authority.", "Closure must not be a Recovery authority"),
    ("critical_creates_worker", PROTOCOL, "At `critical`, do not create Workers", "Critical pressure may create a new Worker. At `critical`, do not create Workers", "critical pressure must not create Workers"),
    ("budget_stop_skips_spec", PROTOCOL, "Budget Stop triggers", "Budget Stop may skip Spec Review. Budget Stop triggers", "Budget Stop must not skip Spec Review"),
    ("budget_stop_skips_standards", PROTOCOL, "Budget Stop triggers", "Budget Stop may skip Standards Review. Budget Stop triggers", "Budget Stop must not skip Standards Review"),
    ("budget_stop_marks_partial_completed", PROTOCOL, "Budget Stop triggers", "Budget Stop may mark partial work completed. Budget Stop triggers", "Budget Stop must not mark partial work completed"),
    ("budget_stop_closes_finding", PROTOCOL, "Budget Stop triggers", "Budget Stop may close a blocker Finding. Budget Stop triggers", "Budget Stop must not close Findings"),
    ("budget_stop_expands_push", PROTOCOL, "Budget Stop triggers", "Budget Stop may grant push authority. Budget Stop triggers", "Budget Stop must not expand push authority"),
)

PREPARED_MUTATION_CASES = (
    ("ready_checkpoint_missing_resume_point", "ready", CHECKPOINT, "- Resume action: Run the required integration verification.", "- Resume action: none", "requires non-empty Resume action"),
    ("ready_checkpoint_missing_authority_source", "ready", CHECKPOINT, "- Loop status source: `LOOP-MAP.md`", "- Loop status source: none", "missing authoritative state source 'LOOP-MAP.md'"),
    ("budget_checkpoint_missing_trigger", "budget", CHECKPOINT, "- Trigger: critical context pressure", "- Trigger: none", "requires Trigger"),
    ("budget_checkpoint_missing_persisted_state", "budget", CHECKPOINT, "- Persisted state: Task and Finding Ledgers saved", "- Persisted state: none", "requires persisted state"),
    ("budget_checkpoint_missing_unfinished_work", "budget", CHECKPOINT, "- TASK-004-R1 still requires integration verification.", "- None.", "requires unfinished work"),
    ("budget_checkpoint_missing_resume_point", "budget", CHECKPOINT, "- Resume item: TASK-004-R1", "- Resume item: none", "requires non-empty Resume item"),
    ("resume_action_empty", "ready", CHECKPOINT, "- Resume action: Run the required integration verification.", "- Resume action: none", "requires non-empty Resume action"),
    ("resume_inputs_empty", "ready", CHECKPOINT, "- Required inputs: current Task, Integration Record, and Finding Ledger", "- Required inputs: none", "requires non-empty Required inputs"),
    ("resume_expected_result_empty", "ready", CHECKPOINT, "- Expected observable result: observed test result recorded in the Integration Record", "- Expected observable result: none", "requires non-empty Expected observable result"),
    ("resume_stop_condition_empty", "ready", CHECKPOINT, "- Stop or escalation condition: any failure outside authorized Rework scope", "- Stop or escalation condition: none", "requires non-empty Stop or escalation condition"),
    ("resume_continue_previous", "ready", CHECKPOINT, "- Resume action: Run the required integration verification.", "- Resume action: Continue previous work.", "Resume action is vague"),
    ("resume_finish_task", "ready", CHECKPOINT, "- Resume action: Run the required integration verification.", "- Resume action: Finish the task.", "Resume action is vague"),
    ("multiple_primary_resume_points", "ready", CHECKPOINT, "## Next Highest-Value Action", "## Exact Resume Point\n\n## Next Highest-Value Action", "exactly one primary Resume Point"),
    ("ready_manifest_missing_checkpoint", "manifest", MANIFEST, "- Checkpoint: CHECKPOINT-004", "- Checkpoint: none", "requires a Checkpoint reference"),
    ("ready_manifest_missing_must_load", "manifest", MANIFEST, "| Current Task Ledger | `TASK-LEDGER.md` | validate active Task | yes |", "| None | none | none | no |", "requires non-empty Must Load"),
    ("validated_resume_safe_no", "resume", RESUME, "- Safe to resume: yes", "- Safe to resume: no", "requires Safe to resume: yes"),
    ("validated_resume_skill_unavailable", "resume", RESUME, "- Required Skills available: yes", "- Required Skills available: no", "unavailable required Skill"),
    ("validated_with_corrections_missing_correction", "resume-corrected", RESUME, "- Corrected stale HEAD from observed Git state.", "- None.", "requires Corrections Applied"),
    ("budget_stop_missing_authoritative_update", "budget", CHECKPOINT, "- Authoritative state updated: yes", "- Authoritative state updated: none", "requires authoritative state update record"),
)


def _missing_test(name: str, relative: Path):
    def test(self: FullLoopCheckpointRecoveryTests) -> None:
        self.assert_rejected(lambda fixture: (fixture / relative).unlink(), f"missing required file: {relative.as_posix()}")
    test.__name__ = f"test_missing_{name}_is_rejected"
    return test


def _simple_mutation_test(name, relative, old, new, message, extra=()):
    def test(self: FullLoopCheckpointRecoveryTests) -> None:
        def mutate(fixture: Path) -> None:
            self.replace_once(fixture / relative, old, new)
            for extra_old, extra_new in extra:
                self.replace_once(fixture / relative, extra_old, extra_new)
        self.assert_rejected(mutate, message)
    test.__name__ = f"test_{name}_is_rejected"
    return test


def _prepared_mutation_test(name, preparation, relative, old, new, message):
    def test(self: FullLoopCheckpointRecoveryTests) -> None:
        def mutate(fixture: Path) -> None:
            if preparation == "ready":
                self.mark_checkpoint_ready(fixture)
            elif preparation == "budget":
                self.mark_budget_stopped(fixture)
            elif preparation == "manifest":
                self.mark_manifest_ready(fixture)
            elif preparation == "resume":
                self.mark_resume_validated(fixture)
            elif preparation == "resume-corrected":
                self.mark_resume_validated(fixture, corrected=True)
            self.replace_once(fixture / relative, old, new)
        self.assert_rejected(mutate, message)
    test.__name__ = f"test_{name}_is_rejected"
    return test


def _resume_status_test(name: str, status: str, safe: str, message: str):
    def test(self: FullLoopCheckpointRecoveryTests) -> None:
        def mutate(fixture: Path) -> None:
            path = fixture / RESUME
            self.replace_once(path, "- Validation Status: inactive", f"- Validation Status: {status}")
            self.replace_once(path, "- Safe to resume: no", f"- Safe to resume: {safe}")
        self.assert_rejected(mutate, message)
    test.__name__ = f"test_{name}_is_rejected"
    return test


def test_head_conflict(self: FullLoopCheckpointRecoveryTests) -> None:
    def mutate(fixture: Path) -> None:
        path = fixture / RESUME
        self.replace_once(path, "- Actual HEAD: none", "- Actual HEAD: abc1234")
        self.replace_once(path, "- Expected HEAD: none", "- Expected HEAD: def5678")
    self.assert_rejected(mutate, "actual HEAD conflicts with expected HEAD")


def test_scope_change_reuses_old_point(self: FullLoopCheckpointRecoveryTests) -> None:
    def mutate(fixture: Path) -> None:
        path = fixture / RESUME
        self.replace_once(path, "- Scope changed: unknown", "- Scope changed: yes")
        self.replace_once(path, "- Still applicable: unknown", "- Still applicable: yes")
    self.assert_rejected(mutate, "changed Scope cannot unconditionally reuse")


def test_commit_authority_inherited(self: FullLoopCheckpointRecoveryTests) -> None:
    def mutate(fixture: Path) -> None:
        path = fixture / RESUME
        self.replace_once(path, "- Commit authority unchanged: unknown", "- Commit authority unchanged: no")
        self.append(path, "\nRetain old commit authority.\n")
    self.assert_rejected(mutate, "changed commit authority must not be inherited")


for _name, _relative in MISSING_CASES:
    setattr(FullLoopCheckpointRecoveryTests, f"test_missing_{_name}_is_rejected", _missing_test(_name, _relative))
for _case in SIMPLE_MUTATION_CASES:
    setattr(FullLoopCheckpointRecoveryTests, f"test_{_case[0]}_is_rejected", _simple_mutation_test(*_case))
for _case in PREPARED_MUTATION_CASES:
    setattr(FullLoopCheckpointRecoveryTests, f"test_{_case[0]}_is_rejected", _prepared_mutation_test(*_case))
for _case in (
    ("blocked_resume_safe_yes", "blocked", "yes", "blocked Resume Report cannot be safe to resume"),
    ("invalid_checkpoint_resume_safe_yes", "invalid-checkpoint", "yes", "invalid-checkpoint Resume Report cannot be safe to resume"),
):
    setattr(FullLoopCheckpointRecoveryTests, f"test_{_case[0]}_is_rejected", _resume_status_test(*_case))

FullLoopCheckpointRecoveryTests.test_head_conflict_without_resolution_is_rejected = test_head_conflict
FullLoopCheckpointRecoveryTests.test_scope_change_reuses_old_point_is_rejected = test_scope_change_reuses_old_point
FullLoopCheckpointRecoveryTests.test_commit_authority_inherited_is_rejected = test_commit_authority_inherited


if __name__ == "__main__":
    unittest.main()
