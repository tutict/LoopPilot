import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate.py"


class DelegationValidationTests(unittest.TestCase):
    def run_validator(
        self, root: Path, *arguments: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable, str(VALIDATOR), "--root", str(root), *arguments
            ],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def copy_repository(self, directory: str) -> Path:
        fixture = Path(directory) / "repository"
        copytree(
            REPOSITORY_ROOT,
            fixture,
            ignore=lambda _path, names: [
                name for name in names if name in {".git", "__pycache__"}
            ],
        )
        return fixture

    def write_real_task(
        self,
        fixture: Path,
        task_id: str = "TASK-001",
        revision_budget: str = "2",
        filename: str | None = None,
    ) -> Path:
        template = fixture / ".looppilot" / "tasks" / "TASK-TEMPLATE.md"
        text = template.read_text(encoding="utf-8")
        replacements = (
            ("task_id: TASK-000", f"task_id: {task_id}"),
            (
                "parent_goal: Template only; no active parent Goal.",
                "parent_goal: Deliver the supervised delegation protocol.",
            ),
            ("status: proposed", "status: assigned"),
            ("previous_status: none", "previous_status: proposed"),
            ("assigned_to: none", "assigned_to: worker-a"),
            (
                "objective: Replace with one bounded, independently reviewable objective.",
                "objective: Validate one bounded protocol task.",
            ),
            (
                "    - Replace with exact files, modules, resources, or research areas.",
                "    - docs/multi-agent-coordination.md",
            ),
            (
                "    - Replace with explicit exclusions and prohibited actions.",
                "    - release and deployment",
            ),
            ("  - Replace with concrete artifacts or findings.", "  - Updated protocol."),
            ("  - Replace with an observable acceptance condition.", "  - Validator passes."),
            (
                "  - Replace with a reproducible check, diff, source, render, or tool result.",
                "  - python scripts/validate.py",
            ),
            ("reviewer: none", "reviewer: reviewer-a"),
            ("integration_owner: none", "integration_owner: integrator-a"),
            ("revision_budget: BOUNDED-LIMIT", f"revision_budget: {revision_budget}"),
            ("YYYY-MM-DD", "2026-07-16"),
            ("YYYY-MM-DD", "2026-07-16"),
        )
        for old, new in replacements:
            text = text.replace(old, new, 1)
        path = template.parent / (filename or f"{task_id}.md")
        path.write_text(text, encoding="utf-8")
        return path

    def write_real_review(
        self,
        fixture: Path,
        decision: str,
        task_id: str = "TASK-001",
        mark_criteria_checked: bool = False,
        reviewer: str = "reviewer-a",
        sync_task_status: bool = True,
    ) -> Path:
        template = fixture / ".looppilot" / "tasks" / "REVIEW-TEMPLATE.md"
        text = template.read_text(encoding="utf-8")
        axes_by_decision = {
            "approved": ("pass", "pass", "observed"),
            "revision-requested": ("pass", "revision-requested", "pending"),
            "rejected": ("rejected", "pass", "pending"),
            "blocked": ("blocked", "pass", "pending"),
        }
        standards, spec, evidence = axes_by_decision.get(
            decision, ("AXIS-DECISION", "AXIS-DECISION", "EVIDENCE-STATUS")
        )
        replacements = (
            ("task_id: TASK-000", f"task_id: {task_id}"),
            ("decision: DECISION", f"decision: {decision}"),
            ("standards_decision: AXIS-DECISION", f"standards_decision: {standards}"),
            ("spec_decision: AXIS-DECISION", f"spec_decision: {spec}"),
            ("required_evidence: EVIDENCE-STATUS", f"required_evidence: {evidence}"),
            ("Decision: AXIS-DECISION", f"Decision: {standards}"),
            ("Decision: AXIS-DECISION", f"Decision: {spec}"),
            ("reviewed: YYYY-MM-DD", "reviewed: 2026-07-16"),
            ("reviewer: none", f"reviewer: {reviewer}"),
        )
        for old, new in replacements:
            text = text.replace(old, new, 1)
        if mark_criteria_checked:
            text = text.replace(
                "Not yet checked.", "Verified against contract evidence."
            )
        if sync_task_status:
            task = template.parent / f"{task_id}.md"
            task_text = task.read_text(encoding="utf-8")
            task_replacements = (
                ("status: assigned", f"status: {decision}"),
                (
                    "previous_status: proposed",
                    "previous_status: under-review",
                ),
                (
                    "status_changed_by: supervisor",
                    "status_changed_by: reviewer",
                ),
            )
            for old, new in task_replacements:
                task_text = task_text.replace(old, new, 1)
            task.write_text(task_text, encoding="utf-8")
        path = template.parent / f"REVIEW-{task_id}.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_missing_delegation_template_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            delegation = fixture / ".looppilot" / "DELEGATION.md"
            if delegation.exists():
                delegation.unlink()

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "missing required file: .looppilot/DELEGATION.md",
            result.stdout,
        )

    def test_invalid_delegation_status_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            delegation = fixture / ".looppilot" / "DELEGATION.md"
            delegation.write_text(
                delegation.read_text(encoding="utf-8").replace(
                    "Status: inactive", "Status: paused", 1
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("DELEGATION.md: invalid Status 'paused'", result.stdout)


    def test_inactive_delegation_cannot_name_a_fictional_supervisor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            delegation = fixture / ".looppilot" / "DELEGATION.md"
            delegation.write_text(
                delegation.read_text(encoding="utf-8").replace(
                    "Supervisor: none", "Supervisor: agent-a", 1
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("DELEGATION.md: inactive template must remain empty", result.stdout)


    def test_missing_task_template_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task_template = fixture / ".looppilot" / "tasks" / "TASK-TEMPLATE.md"
            if task_template.exists():
                task_template.unlink()

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "missing required file: .looppilot/tasks/TASK-TEMPLATE.md",
            result.stdout,
        )


    def test_task_template_without_success_criteria_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task_template = fixture / ".looppilot" / "tasks" / "TASK-TEMPLATE.md"
            task_template.write_text(
                task_template.read_text(encoding="utf-8").replace(
                    "success_criteria:\n"
                    "  - Replace with an observable acceptance condition.\n",
                    "",
                    1,
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("TASK-TEMPLATE.md: missing required field 'success_criteria'", result.stdout)


    def test_task_template_without_required_evidence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task_template = fixture / ".looppilot" / "tasks" / "TASK-TEMPLATE.md"
            task_template.write_text(
                task_template.read_text(encoding="utf-8").replace(
                    "required_evidence:\n"
                    "  - Replace with a reproducible check, diff, source, "
                    "render, or tool result.\n",
                    "",
                    1,
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "TASK-TEMPLATE.md: missing required field 'required_evidence'",
            result.stdout,
        )


    def test_task_template_without_authority_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task_template = fixture / ".looppilot" / "tasks" / "TASK-TEMPLATE.md"
            authority = (
                "authority:\n"
                "  read: false\n"
                "  modify: false\n"
                "  delete: false\n"
                "  commit: false\n"
                "  push: false\n"
                "  release: false\n"
                "  deploy: false\n"
                "  external_communication: false\n"
            )
            task_template.write_text(
                task_template.read_text(encoding="utf-8").replace(
                    authority, "", 1
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("TASK-TEMPLATE.md: missing required field 'authority'", result.stdout)


    def test_invalid_task_status_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task_template = fixture / ".looppilot" / "tasks" / "TASK-TEMPLATE.md"
            task_template.write_text(
                task_template.read_text(encoding="utf-8").replace(
                    "status: proposed", "status: paused", 1
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("TASK-TEMPLATE.md: invalid task status 'paused'", result.stdout)


    def test_invalid_status_in_real_task_contract_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            task.write_text(
                task.read_text(encoding="utf-8").replace(
                    "status: assigned", "status: paused", 1
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("TASK-001.md: invalid task status 'paused'", result.stdout)

    def test_invalid_reviewer_decision_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            review_template = fixture / ".looppilot" / "tasks" / "REVIEW-TEMPLATE.md"
            review_template.write_text(
                review_template.read_text(encoding="utf-8").replace(
                    "decision: DECISION", "decision: looks-good", 1
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("REVIEW-TEMPLATE.md: invalid reviewer decision 'looks-good'", result.stdout)


    def test_approved_real_review_requires_checked_criteria_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            self.write_real_task(fixture)
            self.write_real_review(fixture, decision="approved")

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "approved review must cite checked success criteria and evidence",
            result.stdout,
        )

    def test_worker_cannot_set_initial_task_to_integrated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            text = task.read_text(encoding="utf-8")
            text = text.replace("status: assigned", "status: integrated", 1)
            text = text.replace("previous_status: proposed", "previous_status: approved", 1)
            text = text.replace(
                "status_changed_by: supervisor",
                "status_changed_by: worker",
                1,
            )
            task.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("TASK-001.md: worker cannot set task status 'integrated'", result.stdout)


    def test_approved_cannot_skip_under_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            text = task.read_text(encoding="utf-8")
            text = text.replace("status: assigned", "status: approved", 1)
            text = text.replace("previous_status: proposed", "previous_status: assigned", 1)
            text = text.replace(
                "status_changed_by: supervisor", "status_changed_by: reviewer", 1
            )
            task.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("invalid task transition 'assigned' -> 'approved'", result.stdout)


    def test_integrated_cannot_skip_approved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            text = task.read_text(encoding="utf-8")
            text = text.replace("status: assigned", "status: integrated", 1)
            text = text.replace("previous_status: proposed", "previous_status: under-review", 1)
            text = text.replace(
                "status_changed_by: supervisor", "status_changed_by: integrator", 1
            )
            task.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("invalid task transition 'under-review' -> 'integrated'", result.stdout)


    def test_cancelled_task_cannot_return_to_in_progress(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            text = task.read_text(encoding="utf-8")
            text = text.replace("status: assigned", "status: in-progress", 1)
            text = text.replace("previous_status: proposed", "previous_status: cancelled", 1)
            text = text.replace(
                "status_changed_by: supervisor", "status_changed_by: worker", 1
            )
            task.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("invalid task transition 'cancelled' -> 'in-progress'", result.stdout)


    def test_valid_assigned_to_in_progress_transition_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            text = task.read_text(encoding="utf-8")
            text = text.replace("status: assigned", "status: in-progress", 1)
            text = text.replace("previous_status: proposed", "previous_status: assigned", 1)
            text = text.replace(
                "status_changed_by: supervisor", "status_changed_by: worker", 1
            )
            task.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


    def test_assignment_cannot_implicitly_gain_push_authority(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task_template = fixture / ".looppilot" / "tasks" / "TASK-TEMPLATE.md"
            task_template.write_text(
                task_template.read_text(encoding="utf-8").replace(
                    "  push: false\n", "", 1
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("authority missing explicit field 'push'", result.stdout)


    def test_commit_true_and_push_false_are_independently_expressible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task_template = fixture / ".looppilot" / "tasks" / "TASK-TEMPLATE.md"
            task_template.write_text(
                task_template.read_text(encoding="utf-8").replace(
                    "  commit: false\n  push: false\n",
                    "  commit: true\n  push: false\n",
                    1,
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


    def test_invalid_task_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task_template = fixture / ".looppilot" / "tasks" / "TASK-TEMPLATE.md"
            task_template.write_text(
                task_template.read_text(encoding="utf-8").replace(
                    "task_id: TASK-000", "task_id: child-one", 1
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("TASK-TEMPLATE.md: invalid task_id 'child-one'", result.stdout)


    def test_review_template_requires_corrections_heading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            review_template = fixture / ".looppilot" / "tasks" / "REVIEW-TEMPLATE.md"
            review_template.write_text(
                review_template.read_text(encoding="utf-8").replace(
                    "### Required Corrections\n", "### Requested Changes\n", 1
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("Standards Review missing '### Required Corrections'", result.stdout)



    def test_valid_real_task_contract_is_checked_and_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            self.write_real_task(fixture)

            result = self.run_validator(fixture)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_real_task_cannot_retain_template_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            task.write_text(
                task.read_text(encoding="utf-8").replace(
                    "objective: Validate one bounded protocol task.",
                    "objective: Replace with one bounded, independently reviewable objective.",
                    1,
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn("real task retains placeholder field 'objective'", result.stdout)

    def test_real_task_requires_bounded_revision_budget(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            self.write_real_task(fixture, revision_budget="unlimited")

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "revision_budget must be a positive task-specific integer",
            result.stdout,
        )

    def test_real_task_revision_count_cannot_exceed_budget(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture, revision_budget="2")
            task.write_text(
                task.read_text(encoding="utf-8").replace(
                    "revision_count: 0",
                    "revision_count: 3",
                    1,
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "revision_count cannot exceed revision_budget",
            result.stdout,
        )

    def test_return_to_in_progress_requires_revision_increment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            text = task.read_text(encoding="utf-8")
            text = text.replace("status: assigned", "status: in-progress", 1)
            text = text.replace(
                "previous_status: proposed",
                "previous_status: revision-requested",
                1,
            )
            text = text.replace(
                "status_changed_by: supervisor",
                "status_changed_by: worker",
                1,
            )
            task.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "return from revision-requested must increment revision_count",
            result.stdout,
        )

    def test_revision_cycle_requires_retained_review_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            text = task.read_text(encoding="utf-8")
            text = text.replace("status: assigned", "status: in-progress", 1)
            text = text.replace(
                "previous_status: proposed",
                "previous_status: revision-requested",
                1,
            )
            text = text.replace(
                "status_changed_by: supervisor",
                "status_changed_by: worker",
                1,
            )
            text = text.replace("revision_count: 0", "revision_count: 1", 1)
            task.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "TASK-001.md: status 'in-progress' requires a Review Result",
            result.stdout,
        )

    def test_revision_cycle_accepts_retained_revision_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            review = self.write_real_review(
                fixture,
                decision="revision-requested",
                mark_criteria_checked=True,
            )
            review.write_text(
                review.read_text(encoding="utf-8").replace(
                    "### Required Corrections\n\n- None.",
                    "### Required Corrections\n\n"
                    "- Add the missing regression evidence.",
                    1,
                ),
                encoding="utf-8",
            )
            text = task.read_text(encoding="utf-8")
            text = text.replace(
                "status: revision-requested",
                "status: in-progress",
                1,
            )
            text = text.replace(
                "previous_status: under-review",
                "previous_status: revision-requested",
                1,
            )
            text = text.replace(
                "status_changed_by: reviewer",
                "status_changed_by: worker",
                1,
            )
            text = text.replace("revision_count: 0", "revision_count: 1", 1)
            task.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_rejected_restart_requires_retained_review_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            text = task.read_text(encoding="utf-8")
            text = text.replace("status: assigned", "status: proposed", 1)
            text = text.replace(
                "previous_status: proposed",
                "previous_status: rejected",
                1,
            )
            task.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "TASK-001.md: status 'proposed' requires a Review Result",
            result.stdout,
        )

    def test_rejected_restart_accepts_retained_rejection_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            review = self.write_real_review(
                fixture,
                decision="rejected",
            )
            review.write_text(
                review.read_text(encoding="utf-8").replace(
                    "### Findings\n\n- None.",
                    "### Findings\n\n"
                    "- The result cannot continue without a new approach.",
                    1,
                ),
                encoding="utf-8",
            )
            text = task.read_text(encoding="utf-8")
            text = text.replace("status: rejected", "status: proposed", 1)
            text = text.replace(
                "previous_status: under-review",
                "previous_status: rejected",
                1,
            )
            text = text.replace(
                "status_changed_by: reviewer",
                "status_changed_by: supervisor",
                1,
            )
            task.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_real_task_reviewer_must_be_independent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            task.write_text(
                task.read_text(encoding="utf-8").replace(
                    "reviewer: reviewer-a", "reviewer: worker-a", 1
                ),
                encoding="utf-8",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "Reviewer must be independent from assigned_to",
            result.stdout,
        )

    def test_revision_requested_review_requires_specific_corrections(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            self.write_real_task(fixture)
            self.write_real_review(
                fixture,
                decision="revision-requested",
                mark_criteria_checked=True,
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "revision-requested review requires specific corrections",
            result.stdout,
        )

    def test_valid_approved_real_review_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            self.write_real_task(fixture)
            self.write_real_review(
                fixture,
                decision="approved",
                mark_criteria_checked=True,
            )

            result = self.run_validator(fixture)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_real_review_cannot_retain_decision_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            self.write_real_task(fixture)
            self.write_real_review(
                fixture,
                decision="DECISION",
                sync_task_status=False,
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "REVIEW-TASK-001.md: invalid reviewer decision 'DECISION'",
            result.stdout,
        )

    def test_real_review_must_use_designated_reviewer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            self.write_real_task(fixture)
            self.write_real_review(
                fixture,
                decision="approved",
                mark_criteria_checked=True,
                reviewer="reviewer-b",
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "REVIEW-TASK-001.md: reviewer must match the Task Contract",
            result.stdout,
        )

    def test_review_decision_must_match_task_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            self.write_real_task(fixture)
            self.write_real_review(
                fixture,
                decision="approved",
                mark_criteria_checked=True,
                sync_task_status=False,
            )

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "REVIEW-TASK-001.md: decision 'approved' does not match "
            "task lifecycle",
            result.stdout,
        )

    def test_approved_task_requires_review_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            text = task.read_text(encoding="utf-8")
            text = text.replace("status: assigned", "status: approved", 1)
            text = text.replace(
                "previous_status: proposed",
                "previous_status: under-review",
                1,
            )
            text = text.replace(
                "status_changed_by: supervisor",
                "status_changed_by: reviewer",
                1,
            )
            task.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "TASK-001.md: status 'approved' requires a Review Result",
            result.stdout,
        )

    def test_integrated_task_requires_review_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            text = task.read_text(encoding="utf-8")
            text = text.replace("status: assigned", "status: integrated", 1)
            text = text.replace(
                "previous_status: proposed",
                "previous_status: approved",
                1,
            )
            text = text.replace(
                "status_changed_by: supervisor",
                "status_changed_by: integrator",
                1,
            )
            task.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "TASK-001.md: status 'integrated' requires a Review Result",
            result.stdout,
        )

    def test_approved_review_requires_success_and_evidence_checks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            self.write_real_task(fixture)
            review = self.write_real_review(
                fixture,
                decision="approved",
                mark_criteria_checked=True,
            )
            text = review.read_text(encoding="utf-8")
            text = text.replace(
                "- Success criteria: Verified against contract evidence.\n",
                "",
                1,
            )
            text = text.replace(
                "- Required evidence: Verified against contract evidence.\n",
                "",
                1,
            )
            review.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "approved review must cite checked success criteria and evidence",
            result.stdout,
        )

    def test_blocked_review_requires_missing_condition(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            self.write_real_task(fixture)
            self.write_real_review(fixture, decision="blocked")

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "blocked review must name the missing condition",
            result.stdout,
        )

    def test_integrated_task_accepts_approved_review_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            task = self.write_real_task(fixture)
            self.write_real_review(
                fixture,
                decision="approved",
                mark_criteria_checked=True,
            )
            text = task.read_text(encoding="utf-8")
            text = text.replace("status: approved", "status: integrated", 1)
            text = text.replace(
                "previous_status: under-review",
                "previous_status: approved",
                1,
            )
            text = text.replace(
                "status_changed_by: reviewer",
                "status_changed_by: integrator",
                1,
            )
            task.write_text(text, encoding="utf-8")

            result = self.run_validator(fixture)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_rejected_review_requires_explanation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            self.write_real_task(fixture)
            self.write_real_review(fixture, decision="rejected")

            result = self.run_validator(fixture)

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "rejected review must explain the rejection",
            result.stdout,
        )

    def test_valid_inactive_delegation_template_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)

            result = self.run_validator(fixture)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_delegation_mermaid_and_relative_links_are_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            output = Path(directory) / "mermaid"

            result = self.run_validator(
                fixture,
                "--extract-mermaid",
                str(output),
            )

            diagram = output / "docs-multi-agent-coordination-1.mmd"
            diagram_exists = diagram.is_file() and diagram.stat().st_size > 0

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertTrue(diagram_exists)


if __name__ == "__main__":
    unittest.main()
