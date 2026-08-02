import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Case:
    name: str
    operation: str
    assertion: str = ""
    value: str = ""
    source: str = "HANDOFF.md"
    authority: str = ""
    expected_error: str | None = None
    warning: str | None = None


CASES = (
    Case("simple_lightweight_without_lifecycle_machinery", "repository"),
    Case("full_consistent_closure", "consistent"),
    Case("support_document_without_duplicated_state", "reference"),
    Case("handoff_authority_reference", "reference", source="HANDOFF.md"),
    Case("handoff_matching_snapshot", "projection", "Task[TASK-001].status", "integrated"),
    Case("checklist_procedural_reference", "reference", source="CHECKLIST.md"),
    Case("context_checkpoint_reference", "reference", source="loops/LOOP-001/CONTEXT.md"),
    Case("legacy_closure_warns_and_passes", "legacy", warning="legacy Closure has no Lifecycle Consistency snapshot"),
    Case("legacy_declared_stale_projection_fails", "legacy_stale", "Task[TASK-001].status", "pending", expected_error="lifecycle consistency drift"),
    Case("semantic_handoff_contradiction_remains_reviewer_work", "semantic_prose"),
    Case("project_status_requires_project_authority", "projection", "Project.status", "active", authority="HANDOFF.md", expected_error="must reference PROJECT.md"),
    Case("loop_status_requires_loop_map_authority", "projection", "Loop[LOOP-001].status", "closed", authority="PROJECT.md", expected_error="must reference LOOP-MAP.md"),
    Case("task_status_requires_task_ledger_authority", "projection", "Task[TASK-001].status", "integrated", authority="HANDOFF.md", expected_error="must reference TASK-LEDGER.md"),
    Case("task_owner_requires_task_ledger_authority", "projection", "Task[TASK-001].owner", "worker-a", authority="HANDOFF.md", expected_error="must reference TASK-LEDGER.md"),
    Case("task_revision_requires_task_ledger_authority", "projection", "Task[TASK-001].revision", "2", authority="HANDOFF.md", expected_error="must reference TASK-LEDGER.md"),
    Case("finding_status_requires_finding_ledger_authority", "projection", "Finding[FINDING-001].status", "closed", authority="RESULTS.md", expected_error="must reference FINDING-LEDGER.md"),
    Case("finding_severity_requires_finding_ledger_authority", "projection", "Finding[FINDING-001].severity", "major", authority="RESULTS.md", expected_error="must reference FINDING-LEDGER.md"),
    Case("recovery_boundary_requires_checkpoint_authority", "projection", "Checkpoint.current_boundary", "HEAD", authority="Git", expected_error="must reference CHECKPOINT.md"),
    Case("support_cannot_declare_competing_authority", "competing", expected_error="declares competing lifecycle authority"),
    Case("handoff_status_drift_exp008_fixture", "projection", "Task[TASK-001].status", "under-review", expected_error="lifecycle consistency drift"),
    Case("handoff_revision_drift_exp008_fixture", "projection", "Task[TASK-001].revision", "1", expected_error="lifecycle consistency drift"),
    Case("checklist_static_pending_drift", "projection", "Task[TASK-001].status", "pending", source="CHECKLIST.md", expected_error="lifecycle consistency drift"),
    Case("results_stale_finding_status", "projection", "Finding[FINDING-001].status", "open", source="loops/LOOP-001/RESULTS.md", expected_error="lifecycle consistency drift"),
    Case("projection_requires_git_boundary", "projection_no_boundary", "Task[TASK-001].status", "integrated", expected_error="require a 40-character Git boundary"),
    Case("projection_git_boundary_drift", "projection_old_boundary", "Task[TASK-001].status", "integrated", expected_error="projection Git boundary drift"),
    Case("unknown_assertion_rejected", "unknown_assertion", expected_error="invalid lifecycle assertion"),
    Case("task_status_assertion_drift", "projection", "Task[TASK-001].status", "blocked", expected_error="lifecycle consistency drift"),
    Case("task_owner_assertion_drift", "projection", "Task[TASK-001].owner", "worker-b", expected_error="lifecycle consistency drift"),
    Case("task_revision_assertion_drift", "projection", "Task[TASK-001].revision", "3", expected_error="lifecycle consistency drift"),
    Case("finding_status_assertion_drift", "projection", "Finding[FINDING-001].status", "verified", expected_error="lifecycle consistency drift"),
    Case("finding_severity_assertion_drift", "projection", "Finding[FINDING-001].severity", "minor", expected_error="lifecycle consistency drift"),
    Case("git_assertion_drift", "projection_old_value", "Git.current_boundary", expected_error="lifecycle consistency drift"),
    Case("integration_decision_drift", "projection", "Integration.decision", "pending", source="loops/LOOP-001/RESULTS.md", expected_error="lifecycle consistency drift"),
    Case("review_decision_drift", "projection", "Review.Standards", "rework-required", source="loops/LOOP-001/RESULTS.md", expected_error="lifecycle consistency drift"),
    Case("closure_decision_drift", "projection", "Closure.decision", "blocked", source="loops/LOOP-001/RESULTS.md", expected_error="lifecycle consistency drift"),
    Case("checkpoint_next_action_drift", "projection", "Checkpoint.next_action", "retry old worker", source="loops/LOOP-001/CONTEXT.md", expected_error="lifecycle consistency drift"),
    Case("missing_mandatory_assertion", "missing_assertion", "Task[TASK-001].owner", expected_error="snapshot missing"),
    Case("projection_cannot_change_expected_authority_value", "expected_drift", "Task[TASK-001].status", "pending", expected_error="Expected does not match authority"),
    Case("closure_observed_must_match_projection", "observed_drift", "Task[TASK-001].status", "pending", expected_error="Observed does not match projection"),
    Case("closure_uses_public_validator", "private_command", expected_error="must use public scripts/validate.py"),
    Case("ready_closure_requires_semantic_review", "semantic_pending", expected_error="requires semantic projection review pass"),
    Case("closure_covers_material_projection", "omitted_projection", "Task[TASK-001].status", "integrated", expected_error="omits material projections"),
    Case("closure_snapshot_git_boundary_drift", "closure_old_boundary", expected_error="closure snapshot Git boundary drift"),
    Case("lifecycle_assertions_do_not_create_ledger", "new_ledger", expected_error="forbidden lifecycle store"),
    Case("lifecycle_check_does_not_create_barrier", "new_barrier", expected_error="must not define a new Barrier"),
    Case("exp009_membership_correct_lifecycle_wrong", "projection", "Finding[FINDING-001].status", "open", source="loops/LOOP-001/RESULTS.md", expected_error="lifecycle consistency drift"),
    Case("exp010_product_green_governance_stale", "exp010", "Task[TASK-001].status", "under-review", source="loops/LOOP-001/RESULTS.md", expected_error="lifecycle consistency drift"),
    Case("committed_consistent_closure_still_passes", "committed"),
    Case("support_authority_pointer_is_not_competing", "authority_pointer"),
    Case("superseded_review_round_does_not_block_closure", "superseded_review"),
    Case("legacy_ledger_without_revision_warns", "legacy_no_revision", warning="lacks Revision"),
    Case("short_finding_prefix_assertion_rejected", "short_finding_prefix", expected_error="invalid lifecycle assertion"),
    Case("role_authority_line_is_not_competing", "role_authority"),
    Case("non_canonical_ledger_ids_warn_for_migration", "legacy_short_ids", warning="non-canonical Finding ID"),
    Case("undeclared_lifecycle_copy_is_invalid", "undeclared", expected_error="copied without authority metadata"),
    Case("undeclared_copy_invalid_without_full_loop", "undeclared_lightweight", expected_error="copied without authority metadata"),
    Case("declared_projection_metadata_is_accepted", "projection", "Task[TASK-001].owner", "worker-a"),
    Case("fenced_format_example_is_not_a_copy", "undeclared_fenced"),
)


class LifecycleConsistencyTests(unittest.TestCase):
    maxDiff = None

    def copy_repository(self, directory: str) -> Path:
        fixture = Path(directory) / "repository"
        shutil.copytree(
            REPOSITORY_ROOT,
            fixture,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", ".tmp"
            ),
        )
        return fixture

    def command(self, fixture: Path, *args: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            list(args), cwd=fixture, env=environment, capture_output=True,
            text=True, check=False,
        )

    def initialize_git(self, fixture: Path) -> str:
        for args in (
            ("git", "init", "-q"),
            ("git", "config", "user.name", "LoopPilot Test"),
            ("git", "config", "user.email", "test@example.invalid"),
            ("git", "add", "."),
            ("git", "commit", "-q", "-m", "fixture baseline"),
        ):
            result = self.command(fixture, *args)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        result = self.command(fixture, "git", "rev-parse", "HEAD")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result.stdout.strip()

    def write(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.rstrip() + "\n", encoding="utf-8")

    def facts(self, head: str) -> dict[str, tuple[str, str]]:
        return {
            "Project.status": ("PROJECT.md", "active"),
            "Loop[LOOP-001].status": ("LOOP-MAP.md", "closed"),
            "Task[TASK-001].status": ("TASK-LEDGER.md", "integrated"),
            "Task[TASK-001].owner": ("TASK-LEDGER.md", "worker-a"),
            "Task[TASK-001].revision": ("TASK-LEDGER.md", "2"),
            "Finding[FINDING-001].status": ("FINDING-LEDGER.md", "closed"),
            "Finding[FINDING-001].severity": ("FINDING-LEDGER.md", "major"),
            "Git.current_boundary": ("Git", head),
            "Integration.decision": ("INTEGRATION-RECORD.md", "pass"),
            "Review.Spec": ("REVIEW-REPORT.md", "pass"),
            "Review.Standards": ("REVIEW-REPORT.md", "pass"),
            "Closure.decision": ("LOOP-CLOSURE.md", "accepted"),
            "Checkpoint.current_boundary": ("CHECKPOINT.md", head),
            "Checkpoint.next_action": ("CHECKPOINT.md", "prepare release candidate"),
        }

    def closure(self, head: str, projections: dict[str, tuple[str, str]]) -> str:
        rows = []
        for assertion, (authority, expected) in self.facts(head).items():
            if assertion in projections:
                source, observed = projections[assertion]
            else:
                source, observed = "authoritative-only", expected
            consistent = "yes" if observed.casefold() == expected.casefold() else "no"
            rows.append(
                f"| {assertion} | {authority} | {source} | {expected} | {observed} | {consistent} |"
            )
        return "\n".join((
            "# Loop Closure",
            "",
            "- Loop ID: LOOP-001",
            "- Closure Status: accepted",
            "",
            "## Lifecycle Consistency",
            "",
            "- Assertion snapshot: present",
            "- Deterministic validation: `python scripts/validate.py`",
            "- Semantic projection review: pass",
            "- Open consistency findings: none",
            f"- Snapshot Git boundary: {head}",
            "",
            "| Assertion | Authority | Projection | Expected | Observed | Consistent |",
            "|---|---|---|---|---|---|",
            *rows,
            "",
            "## Closure Decision",
            "",
            "- Decision: accepted",
        ))

    def create_full_loop(self, fixture: Path, head: str) -> None:
        state = fixture / ".looppilot"
        loop = state / "loops" / "LOOP-001"
        self.write(state / "PROJECT.md", "# Project\n\nStatus: active")
        self.write(state / "LOOP-MAP.md", "# Loop Map\n\n## Loops\n\n| Loop ID | Status |\n|---|---|\n| LOOP-001 | closed |")
        self.write(loop / "TASK-LEDGER.md", "# Task Ledger\n\n## Task Summary\n\n| Task ID | Status | Worker | Revision |\n|---|---|---|---|\n| TASK-001 | integrated | worker-a | 2 |")
        self.write(loop / "FINDING-LEDGER.md", "# Finding Ledger\n\n## Finding Summary\n\n| Finding ID | Severity | Status |\n|---|---|---|\n| FINDING-001 | major | closed |")
        self.write(state / "CHECKPOINT.md", f"# Checkpoint\n\n- Verified HEAD: {head}\n- Resume action: prepare release candidate")
        self.write(loop / "integration" / "INTEGRATION-RECORD.md", "# Integration\n\n- Status: integrated\n- Barrier result: pass")
        self.write(loop / "reviews" / "REVIEW-001.md", "# Review\n\n## Spec Review Contribution\n\n- Decision: pass\n\n## Standards Review Contribution\n\n- Decision: pass")
        self.write(loop / "LOOP-CLOSURE.md", self.closure(head, {}))

    def add_projection(
        self, fixture: Path, head: str, assertion: str, value: str,
        source: str, authority: str = "", boundary: str | None = None,
        update_closure: bool = True,
    ) -> None:
        facts = self.facts(head)
        if not authority:
            authority = facts.get(assertion, ("TASK-LEDGER.md", ""))[0]
        path = fixture / ".looppilot" / source
        prefix = path.read_text(encoding="utf-8").rstrip() + "\n\n" if path.exists() else "# Supporting Artifact\n\n"
        boundary_line = "" if boundary == "missing" else f"- Derived at Git boundary: {boundary or head}\n\n"
        self.write(path, prefix + "## Lifecycle Projections\n\n" + boundary_line + "| Assertion | Authority | Value |\n|---|---|---|\n" + f"| {assertion} | {authority} | {value} |")
        if update_closure:
            closure = fixture / ".looppilot" / "loops" / "LOOP-001" / "LOOP-CLOSURE.md"
            self.write(closure, self.closure(head, {assertion: (source, value)}))

    def validate(self, fixture: Path) -> subprocess.CompletedProcess[str]:
        return self.command(
            fixture, sys.executable, str(fixture / "scripts" / "validate.py"),
            "--root", str(fixture),
        )

    def exercise(self, case: Case) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            head = self.initialize_git(fixture)
            if case.operation not in {"repository", "undeclared_lightweight"}:
                self.create_full_loop(fixture, head)
            closure = fixture / ".looppilot" / "loops" / "LOOP-001" / "LOOP-CLOSURE.md"
            if case.operation == "reference":
                path = fixture / ".looppilot" / case.source
                if path.exists():
                    self.write(path, path.read_text(encoding="utf-8") + "\nCurrent task: see TASK-LEDGER.md -> TASK-001")
                else:
                    self.write(path, "# Context\n\nCurrent recovery: see CHECKPOINT.md")
            elif case.operation in {"projection", "exp010"}:
                value = head if case.value == "HEAD" else case.value
                self.add_projection(fixture, head, case.assertion, value, case.source, case.authority)
                if case.operation == "exp010":
                    path = fixture / ".looppilot" / case.source
                    self.write(path, path.read_text(encoding="utf-8") + "\nProduct tests: 100/100 pass.\nIntegration: green.")
            elif case.operation == "projection_no_boundary":
                self.add_projection(fixture, head, case.assertion, case.value, case.source, boundary="missing")
            elif case.operation == "projection_old_boundary":
                self.add_projection(fixture, head, case.assertion, case.value, case.source, boundary="0" * 40)
            elif case.operation == "projection_old_value":
                self.add_projection(fixture, head, case.assertion, "0" * 40, case.source)
            elif case.operation == "unknown_assertion":
                self.add_projection(fixture, head, "Task[TASK-X].status", "integrated", case.source)
            elif case.operation == "legacy":
                self.write(closure, "# Legacy Closure\n\n- Loop ID: LOOP-001\n- Decision: accepted")
            elif case.operation == "legacy_stale":
                self.add_projection(
                    fixture, head, case.assertion, case.value, case.source
                )
                self.write(closure, "# Legacy Closure\n\n- Loop ID: LOOP-001\n- Decision: accepted")
            elif case.operation == "semantic_prose":
                handoff = fixture / ".looppilot" / "HANDOFF.md"
                self.write(
                    handoff,
                    handoff.read_text(encoding="utf-8")
                    + "\nNarrative claim: Project accepted despite exact values matching.",
                )
            elif case.operation == "competing":
                handoff = fixture / ".looppilot" / "HANDOFF.md"
                self.write(handoff, handoff.read_text(encoding="utf-8") + "\n- Task status authority: HANDOFF.md")
            elif case.operation == "missing_assertion":
                text = closure.read_text(encoding="utf-8")
                line = next(line for line in text.splitlines() if line.startswith(f"| {case.assertion} |"))
                self.write(closure, text.replace(line + "\n", "", 1))
            elif case.operation == "expected_drift":
                text = closure.read_text(encoding="utf-8")
                old = "| Task[TASK-001].status | TASK-LEDGER.md | authoritative-only | integrated | integrated | yes |"
                self.write(closure, text.replace(old, old.replace("| integrated | integrated |", "| pending | integrated |"), 1))
            elif case.operation == "observed_drift":
                self.add_projection(fixture, head, case.assertion, "integrated", case.source)
                text = closure.read_text(encoding="utf-8")
                self.write(closure, text.replace("| integrated | integrated | yes |", "| integrated | pending | yes |", 1))
            elif case.operation == "private_command":
                self.write(closure, closure.read_text(encoding="utf-8").replace("python scripts/validate.py", "python scripts/lifecycle_consistency_validation.py"))
            elif case.operation == "semantic_pending":
                self.write(closure, closure.read_text(encoding="utf-8").replace("Semantic projection review: pass", "Semantic projection review: not-evaluated"))
            elif case.operation == "omitted_projection":
                self.add_projection(fixture, head, case.assertion, case.value, case.source, update_closure=False)
            elif case.operation == "closure_old_boundary":
                self.write(closure, closure.read_text(encoding="utf-8").replace(head, "0" * 40, 1))
            elif case.operation == "new_ledger":
                self.write(fixture / ".looppilot" / "full-loop" / "LIFECYCLE-LEDGER.md", "# Forbidden")
            elif case.operation == "new_barrier":
                path = fixture / "docs" / "lifecycle-authority-and-derived-projections.md"
                self.write(path, path.read_text(encoding="utf-8") + "\n## Lifecycle Barrier\n")
            elif case.operation == "committed":
                for args in (("git", "add", "."), ("git", "commit", "-q", "-m", "record closure")):
                    result = self.command(fixture, *args)
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            elif case.operation == "authority_pointer":
                self.write(
                    fixture / ".looppilot" / "loops" / "LOOP-001" / "DELIVERY.md",
                    "# Delivery\n\n- Task status authority: `TASK-LEDGER.md`\n- Finding status authority: `FINDING-LEDGER.md`",
                )
            elif case.operation == "superseded_review":
                self.write(
                    fixture / ".looppilot" / "loops" / "LOOP-001" / "reviews" / "REVIEW-000.md",
                    "# Review\n\n- Status: superseded\n\n## Spec Review Contribution\n\n- Decision: pass\n\n## Standards Review Contribution\n\n- Decision: rework-required",
                )
            elif case.operation == "legacy_no_revision":
                self.write(
                    fixture / ".looppilot" / "loops" / "LOOP-001" / "TASK-LEDGER.md",
                    "# Task Ledger\n\n## Task Summary\n\n| Task ID | Status | Worker |\n|---|---|---|\n| TASK-001 | integrated | worker-a |",
                )
                self.write(closure, "# Legacy Closure\n\n- Loop ID: LOOP-001\n- Decision: accepted")
            elif case.operation == "short_finding_prefix":
                self.add_projection(fixture, head, "Finding[F-001].status", "closed", case.source)
            elif case.operation == "role_authority":
                self.write(
                    fixture / ".looppilot" / "loops" / "LOOP-001" / "LOOP-CONTRACT.md",
                    "# Loop Contract\n\n- Task assignment authority: Supervisor\n- Finding triage authority: Supervisor\n- Recovery execution authority: Supervisor",
                )
            elif case.operation == "legacy_short_ids":
                self.write(
                    fixture / ".looppilot" / "loops" / "LOOP-001" / "FINDING-LEDGER.md",
                    "# Finding Ledger\n\n## Finding Summary\n\n| Finding ID | Severity | Status |\n|---|---|---|\n| F-001 | major | closed |",
                )
                self.write(closure, "# Legacy Closure\n\n- Loop ID: LOOP-001\n- Decision: accepted")
            elif case.operation in {"undeclared", "undeclared_lightweight"}:
                handoff = fixture / ".looppilot" / "HANDOFF.md"
                self.write(
                    handoff,
                    handoff.read_text(encoding="utf-8")
                    + "\nTask[TASK-001].status is integrated.",
                )
            elif case.operation == "undeclared_fenced":
                readme = fixture / ".looppilot" / "full-loop" / "README.md"
                self.write(
                    readme,
                    readme.read_text(encoding="utf-8")
                    + "\n```text\nTask[TASK-001].status\n```",
                )
            elif case.operation not in {"repository", "consistent"}:
                self.fail(f"unknown operation {case.operation}")

            result = self.validate(fixture)
            output = result.stdout + result.stderr
            if case.expected_error:
                self.assertEqual(1, result.returncode, output)
                self.assertIn(case.expected_error, output)
            else:
                self.assertEqual(0, result.returncode, output)
                self.assertIn("Static validation passed", output)
            if case.warning:
                self.assertIn(case.warning, output)

    def test_validator_does_not_modify_files_or_create_finding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.copy_repository(directory)
            head = self.initialize_git(fixture)
            self.create_full_loop(fixture, head)
            self.add_projection(
                fixture, head, "Task[TASK-001].status", "blocked", "HANDOFF.md"
            )
            before = {
                path.relative_to(fixture): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in fixture.rglob("*") if path.is_file() and ".git" not in path.parts
            }
            before_findings = {
                path.relative_to(fixture)
                for path in fixture.rglob("FINDING-*.md")
            }
            result = self.validate(fixture)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            after = {
                path.relative_to(fixture): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in fixture.rglob("*") if path.is_file() and ".git" not in path.parts
            }
            self.assertEqual(before, after)
            after_findings = {
                path.relative_to(fixture)
                for path in fixture.rglob("FINDING-*.md")
            }
            self.assertEqual(before_findings, after_findings)


def _make_test(case: Case):
    def test(self: LifecycleConsistencyTests) -> None:
        self.exercise(case)
    return test


if len(CASES) < 36 or len({case.name for case in CASES}) != len(CASES):
    raise RuntimeError("Phase 11 requires at least 36 distinct lifecycle cases")

for index, case in enumerate(CASES, start=1):
    setattr(LifecycleConsistencyTests, f"test_{index:03d}_{case.name}", _make_test(case))


if __name__ == "__main__":
    unittest.main()
