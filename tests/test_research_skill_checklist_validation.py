import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate.py"

CHECKLIST_TEMPLATE = """# Parent Goal Checklist

Goal ID: none
Status: inactive
Updated: YYYY-MM-DD
Updated by: none
Supervisor: none
Integrator: none
Source of truth: current user instruction and host-native Plan

## Parent Goal

No active parent Goal.

## Success Criteria

- [ ] None.

## Work Items

- [ ] None.

## Blocked Items

- None.

## Deferred Items

- None.

## Last Verified Evidence

- None.

## Execution Budget

Budget mode: bounded
Context pressure: unknown
Resume required: false
Last compaction: none

## Resume Point

- None.

## Stop Reason

- None.
"""

RESEARCH_TEMPLATE = """# Research Brief

Research ID: none
Parent Goal: none
Prepared: YYYY-MM-DD
Prepared by: none
Status: inactive

## Questions

- None.

## Source Requirements

- Prefer official documentation, standards, primary repositories, and original research.

## Sources

### SOURCE-001

- Title: None.
- Publisher: None.
- URL or reference: None.
- Source type: None.
- Version or date: None.
- Accessed: None.
- Authority: None.
- Relevance: None.

## Findings

### FINDING-001

- Finding: None.
- Supported by: None.
- Confidence: None.
- Applies to: None.
- Limitations: None.

## Source Conflicts

- None.

## Implementation Implications

- None.

## Worker Guidance

- None.

## Unresolved Questions

- None.

## Verification Boundary

Research evidence does not prove that the implementation works in the
current repository or runtime.
"""

VALID_TASK = """---
task_id: TASK-001
parent_goal: Deliver the supervised delegation protocol.
status: assigned
previous_status: proposed
status_changed_by: supervisor
assigned_role: worker
assigned_to: worker-a
objective: Validate one bounded protocol task.
scope:
  allowed:
    - docs/multi-agent-coordination.md
  forbidden:
    - release and deployment
deliverables:
  - Updated protocol.
success_criteria:
  - Validator passes.
required_evidence:
  - python scripts/validate.py
dependencies:
  - none
research_inputs: []
skill_assignment:
  required:
    - skill: example-skill
      purpose: Validate the fixture.
      verified_available: true
      source: host skill inventory
      version: "1"
      expected_output: Validation evidence.
  optional: []
  forbidden:
    - skill: unsafe-skill
      reason: Outside task authority.
  fallback:
    - strategy: Use host base capabilities.
skill_selection:
  considered:
    - skill: example-skill
      status: selected
      reason: Relevant and confirmed available.
  selected:
    - example-skill
  verified_available:
    - example-skill
  selected_by: supervisor-a
checklist_item: ITEM-001
authority:
  read: true
  modify: true
  delete: false
  commit: false
  push: false
  release: false
  deploy: false
  external_communication: false
reviewer: reviewer-a
integration_owner: integrator-a
revision_count: 0
revision_budget: 2
created: 2026-07-16
updated: 2026-07-16
---

# Task Contract

Skill assignment transfers no authority. The Worker MUST NOT install unavailable
Skills or load a forbidden Skill.

## Worker Submission

- Deliverables produced: None.
- Evidence observed: None.
- Risks or blockers: None.
- Unfinished items: None.
- Conflict notes: None.
"""

VALID_REVIEW = """---
task_id: TASK-001
decision: approved
standards_decision: pass
spec_decision: pass
required_evidence: observed
reviewed: 2026-07-16
reviewer: reviewer-a
---

# Review Result

## Standards Review

Decision: pass

### Criteria Checked

- Instruction compliance: Verified against current instructions.
- Repository standards: Verified by static validation.
- Safety and authority: No authority expansion observed.
- Scope compliance: Work remained in scope.
- Maintainability: Structure follows repository patterns.
- Source quality: Not applicable to this task.
- Skill-use discipline: Assigned Skills were confirmed.
- Context efficiency: No unnecessary Skills were loaded.

### Findings

- None.

### Required Corrections

- None.

## Spec Review

Decision: pass

### Criteria Checked

- Objective: Satisfied.
- Deliverables: Produced.
- Success criteria: Observed.
- Required evidence: Observed by the Reviewer.
- Dependencies: Satisfied.
- Research usage: Appropriate.
- Parent-goal alignment: Confirmed.
- Integration readiness: Ready.

### Findings

- None.

### Required Corrections

- None.

## Verification Gaps

- None.

## Overall Decision Rationale

- Both review axes passed and required evidence was observed.

## Authority Note

This review grants no commit, push, release, deployment, deletion, Skill
installation, or external-communication authority.
"""


class ResearchSkillChecklistValidationTests(unittest.TestCase):
    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--root", str(root)],
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
        checklist = fixture / ".looppilot" / "CHECKLIST.md"
        research = fixture / ".looppilot" / "RESEARCH-TEMPLATE.md"
        if not checklist.exists():
            checklist.write_text(CHECKLIST_TEMPLATE, encoding="utf-8")
        if not research.exists():
            research.write_text(RESEARCH_TEMPLATE, encoding="utf-8")
        return fixture

    def validate_fixture(self, mutator=None) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            if mutator is not None:
                mutator(fixture)
            return self.run_validator(fixture)

    @staticmethod
    def replace(path: Path, old: str, new: str) -> None:
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"fixture text not found in {path}: {old!r}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    @staticmethod
    def write_valid_task(fixture: Path, text: str = VALID_TASK) -> Path:
        path = fixture / ".looppilot" / "tasks" / "TASK-001.md"
        path.write_text(text, encoding="utf-8")
        return path

    @staticmethod
    def write_approved_task_and_review(
        fixture: Path, review_text: str = VALID_REVIEW
    ) -> None:
        task = VALID_TASK.replace("status: assigned", "status: approved", 1)
        task = task.replace("previous_status: proposed", "previous_status: under-review", 1)
        task = task.replace("status_changed_by: supervisor", "status_changed_by: reviewer", 1)
        ResearchSkillChecklistValidationTests.write_valid_task(fixture, task)
        review = fixture / ".looppilot" / "tasks" / "REVIEW-TASK-001.md"
        review.write_text(review_text, encoding="utf-8")

    @staticmethod
    def make_ready_research(fixture: Path) -> Path:
        path = fixture / ".looppilot" / "RESEARCH-TEMPLATE.md"
        text = path.read_text(encoding="utf-8")
        replacements = (
            ("Research ID: none", "Research ID: RESEARCH-001"),
            ("Parent Goal: none", "Parent Goal: Validate current API behavior."),
            ("Prepared: YYYY-MM-DD", "Prepared: 2026-07-16"),
            ("Prepared by: none", "Prepared by: supervisor-a"),
            ("Status: inactive", "Status: ready"),
            ("- Title: None.", "- Title: Official API documentation"),
            ("- Publisher: None.", "- Publisher: Example Foundation"),
            ("- URL or reference: None.", "- URL or reference: https://example.com/api"),
            ("- Source type: None.", "- Source type: official documentation"),
            ("- Version or date: None.", "- Version or date: 2.0"),
            ("- Accessed: None.", "- Accessed: 2026-07-16"),
            ("- Authority: None.", "- Authority: primary"),
            ("- Relevance: None.", "- Relevance: Defines the required API."),
            ("- Finding: None.", "- Finding: Version 2.0 requires explicit input."),
            ("- Supported by: None.", "- Supported by: SOURCE-001"),
            ("- Confidence: None.", "- Confidence: high"),
            ("- Applies to: None.", "- Applies to: version 2.0"),
            ("- Limitations: None.", "- Limitations: Runtime behavior remains unverified."),
        )
        for old, new in replacements:
            text = text.replace(old, new, 1)
        path.write_text(text, encoding="utf-8")
        return path

    def test_01_valid_inactive_checklist_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_02_invalid_checklist_status_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace(
                fixture / ".looppilot" / "CHECKLIST.md",
                "Status: inactive",
                "Status: running",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("CHECKLIST.md: invalid Status 'running'", result.stdout)

    def test_03_invalid_context_pressure_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace(
                fixture / ".looppilot" / "CHECKLIST.md",
                "Context pressure: unknown",
                "Context pressure: extreme",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("CHECKLIST.md: invalid Context pressure 'extreme'", result.stdout)

    def test_04_checked_approved_item_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace(
                fixture / ".looppilot" / "CHECKLIST.md",
                "- [ ] None.",
                "- [x] `ITEM-001` Reviewed work.\n"
                "  - Status: approved\n"
                "  - Task: `TASK-001`\n"
                "  - Evidence: observed review",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("approved item must remain unchecked", result.stdout)

    def test_05_unchecked_integrated_item_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace(
                fixture / ".looppilot" / "CHECKLIST.md",
                "- [ ] None.",
                "- [ ] `ITEM-001` Integrated work.\n"
                "  - Status: integrated\n"
                "  - Task: `TASK-001`\n"
                "  - Evidence: python scripts/validate.py passed",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("integrated item must be checked", result.stdout)

    def test_06_checked_item_without_evidence_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace(
                fixture / ".looppilot" / "CHECKLIST.md",
                "- [ ] None.",
                "- [x] `ITEM-001` Integrated work.\n"
                "  - Status: integrated\n"
                "  - Task: `TASK-001`\n"
                "  - Evidence: pending",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("checked item requires observed evidence", result.stdout)

    def test_07_budget_stopped_without_resume_point_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            path = fixture / ".looppilot" / "CHECKLIST.md"
            self.replace(path, "Status: inactive", "Status: budget-stopped")
            self.replace(path, "Resume required: false", "Resume required: true")
            self.replace(path, "## Stop Reason\n\n- None.", "## Stop Reason\n\n- Budget exhausted.")

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("budget-stopped requires a Resume Point", result.stdout)

    def test_08_budget_stopped_requires_resume_flag(self) -> None:
        def mutate(fixture: Path) -> None:
            path = fixture / ".looppilot" / "CHECKLIST.md"
            self.replace(path, "Status: inactive", "Status: budget-stopped")
            self.replace(path, "## Resume Point\n\n- None.", "## Resume Point\n\n- Re-run validation.")
            self.replace(path, "## Stop Reason\n\n- None.", "## Stop Reason\n\n- Budget exhausted.")

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("budget-stopped requires Resume required: true", result.stdout)

    def test_09_completed_checklist_with_open_success_criterion_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace(
                fixture / ".looppilot" / "CHECKLIST.md",
                "Status: inactive",
                "Status: completed",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("completed checklist has an unchecked success criterion", result.stdout)

    def test_10_checked_cancelled_item_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace(
                fixture / ".looppilot" / "CHECKLIST.md",
                "- [ ] None.",
                "- [x] `ITEM-001` Cancelled work.\n"
                "  - Status: cancelled\n"
                "  - Task: none\n"
                "  - Evidence: user cancelled requirement",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("cancelled item must remain unchecked", result.stdout)

    def test_11_valid_integrated_item_passes(self) -> None:
        def mutate(fixture: Path) -> None:
            path = fixture / ".looppilot" / "CHECKLIST.md"
            self.replace(path, "Status: inactive", "Status: active")
            self.replace(
                path,
                "- [ ] None.",
                "- [x] `ITEM-001` Integrated work.\n"
                "  - Status: integrated\n"
                "  - Task: `TASK-001`\n"
                "  - Evidence: python scripts/validate.py passed",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_12_valid_budget_stopped_checklist_passes(self) -> None:
        def mutate(fixture: Path) -> None:
            path = fixture / ".looppilot" / "CHECKLIST.md"
            self.replace(path, "Status: inactive", "Status: budget-stopped")
            self.replace(path, "Resume required: false", "Resume required: true")
            self.replace(path, "## Resume Point\n\n- None.", "## Resume Point\n\n- Re-run validation.")
            self.replace(path, "## Stop Reason\n\n- None.", "## Stop Reason\n\n- Budget exhausted.")

        result = self.validate_fixture(mutate)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_13_inactive_template_contains_no_real_work(self) -> None:
        def mutate(fixture: Path) -> None:
            text = (fixture / ".looppilot" / "CHECKLIST.md").read_text(encoding="utf-8")
            self.assertNotIn("ITEM-", text)
            self.assertNotIn("- [x]", text)

        result = self.validate_fixture(mutate)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_14_valid_inactive_research_template_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_15_invalid_research_status_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.replace(
                fixture / ".looppilot" / "RESEARCH-TEMPLATE.md",
                "Status: inactive",
                "Status: finished",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("RESEARCH-TEMPLATE.md: invalid Status 'finished'", result.stdout)

    def test_16_ready_research_without_source_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            path = self.make_ready_research(fixture)
            self.replace(path, "- Title: Official API documentation", "- Title: None.")

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("ready Research Brief requires a Source", result.stdout)

    def test_17_ready_research_without_finding_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            path = self.make_ready_research(fixture)
            self.replace(path, "- Finding: Version 2.0 requires explicit input.", "- Finding: None.")

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("ready Research Brief requires a Finding", result.stdout)

    def test_18_source_without_version_or_date_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            path = self.make_ready_research(fixture)
            self.replace(path, "- Version or date: 2.0", "- Version or date: None.")

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("Source requires Version or date", result.stdout)

    def test_19_conflicted_research_without_conflict_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            path = self.make_ready_research(fixture)
            self.replace(path, "Status: ready", "Status: conflicted")

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("conflicted Research Brief requires Source Conflicts", result.stdout)

    def test_20_research_cannot_claim_local_implementation_verification(self) -> None:
        def mutate(fixture: Path) -> None:
            path = self.make_ready_research(fixture)
            self.replace(
                path,
                "- Finding: Version 2.0 requires explicit input.",
                "- Finding: The implementation is verified in the current repository.",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("Research Brief cannot claim local implementation verification", result.stdout)

    def test_21_valid_ready_research_brief_passes(self) -> None:
        result = self.validate_fixture(self.make_ready_research)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_22_task_without_research_inputs_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.write_valid_task(fixture, VALID_TASK.replace("research_inputs: []\n", "", 1))

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("TASK-001.md: missing required field 'research_inputs'", result.stdout)

    def test_23_task_without_skill_assignment_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            start = VALID_TASK.index("skill_assignment:\n")
            end = VALID_TASK.index("skill_selection:\n")
            self.write_valid_task(fixture, VALID_TASK[:start] + VALID_TASK[end:])

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("TASK-001.md: missing required field 'skill_assignment'", result.stdout)

    def test_24_task_without_checklist_item_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.write_valid_task(fixture, VALID_TASK.replace("checklist_item: ITEM-001\n", "", 1))

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("TASK-001.md: missing required field 'checklist_item'", result.stdout)

    def test_25_required_skill_without_availability_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.write_valid_task(
                fixture,
                VALID_TASK.replace("      verified_available: true\n", "", 1),
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("required Skill missing 'verified_available'", result.stdout)

    def test_26_unavailable_skill_cannot_be_selected(self) -> None:
        def mutate(fixture: Path) -> None:
            text = VALID_TASK.replace("      verified_available: true", "      verified_available: false", 1)
            text = text.replace("status: selected", "status: unavailable", 1)
            self.write_valid_task(fixture, text)

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("unavailable Skill cannot be selected", result.stdout)

    def test_27_forbidden_skill_cannot_be_selected(self) -> None:
        def mutate(fixture: Path) -> None:
            text = VALID_TASK.replace(
                "  selected:\n    - example-skill",
                "  selected:\n    - example-skill\n    - unsafe-skill",
                1,
            )
            self.write_valid_task(fixture, text)

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("forbidden Skill cannot be selected", result.stdout)

    def test_28_valid_skill_assignment_passes(self) -> None:
        result = self.validate_fixture(self.write_valid_task)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_29_skill_assignment_does_not_expand_commit_or_push_authority(self) -> None:
        def mutate(fixture: Path) -> None:
            path = self.write_valid_task(fixture)
            text = path.read_text(encoding="utf-8")
            self.assertIn("  commit: false", text)
            self.assertIn("  push: false", text)

        result = self.validate_fixture(mutate)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_30_review_without_standards_axis_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            review = VALID_REVIEW.replace("## Standards Review", "## Policy Review", 1)
            self.write_approved_task_and_review(fixture, review)

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("missing '## Standards Review'", result.stdout)

    def test_31_review_without_spec_axis_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            review = VALID_REVIEW.replace("## Spec Review", "## Product Review", 1)
            self.write_approved_task_and_review(fixture, review)

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("missing '## Spec Review'", result.stdout)

    def test_32_spec_revision_prevents_approval(self) -> None:
        def mutate(fixture: Path) -> None:
            review = VALID_REVIEW.replace("spec_decision: pass", "spec_decision: revision-requested", 1)
            review = review.replace("## Spec Review\n\nDecision: pass", "## Spec Review\n\nDecision: revision-requested", 1)
            self.write_approved_task_and_review(fixture, review)

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("approved requires both review axes to pass", result.stdout)

    def test_33_standards_blocked_prevents_approval(self) -> None:
        def mutate(fixture: Path) -> None:
            review = VALID_REVIEW.replace("standards_decision: pass", "standards_decision: blocked", 1)
            review = review.replace("## Standards Review\n\nDecision: pass", "## Standards Review\n\nDecision: blocked", 1)
            self.write_approved_task_and_review(fixture, review)

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("approved requires both review axes to pass", result.stdout)

    def test_34_two_passed_axes_allow_approval(self) -> None:
        result = self.validate_fixture(self.write_approved_task_and_review)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_35_approval_without_observed_evidence_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            review = VALID_REVIEW.replace("required_evidence: observed", "required_evidence: pending", 1)
            self.write_approved_task_and_review(fixture, review)

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("approved review requires observed evidence", result.stdout)

    def test_36_review_cannot_authorize_skill_installation(self) -> None:
        def mutate(fixture: Path) -> None:
            review = VALID_REVIEW.replace(
                "This review grants no commit, push, release, deployment, deletion, Skill\n"
                "installation, or external-communication authority.",
                "This review authorizes Skill installation.",
                1,
            )
            self.write_approved_task_and_review(fixture, review)

        result = self.validate_fixture(mutate)
        self.assertEqual(1, result.returncode)
        self.assertIn("review must not authorize Skill installation", result.stdout)


if __name__ == "__main__":
    unittest.main()
