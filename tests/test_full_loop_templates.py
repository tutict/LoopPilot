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
README = FULL_LOOP / "README.md"
LOOP_MAP = FULL_LOOP / "LOOP-MAP-TEMPLATE.md"
LOOP_CONTRACT = FULL_LOOP / "LOOP-CONTRACT-TEMPLATE.md"
TASK_LEDGER = FULL_LOOP / "TASK-LEDGER-TEMPLATE.md"
FINDING_LEDGER = FULL_LOOP / "FINDING-LEDGER-TEMPLATE.md"

MAP_PLACEHOLDER = (
    "| [ ] | LOOP-XXX | placeholder | planned | none | pending | pending | "
    "no | no | not-created | pending |"
)
VALID_LOOP_ROW = (
    "| [ ] | LOOP-001 | Account access | planned | none | contracts/LOOP-001.md | "
    "pending | no | no | not-created-not-required | pending |"
)
VALID_CLOSED_LOOP_ROW = (
    "| [x] | LOOP-001 | Account access | closed | none | contracts/LOOP-001.md | "
    "loops/LOOP-001/LOOP-CLOSURE.md | no | no | not-created-not-required | "
    "CHECKPOINT.md#loop-001 |"
)
UNAUTHORIZED_COMMIT_ROW = (
    "| [ ] | LOOP-001 | Account access | blocked | none | contracts/LOOP-001.md | "
    "pending | yes | no | not-created-not-authorized | pending |"
)
TASK_PLACEHOLDER = (
    "| None | None | None | no | proposed | none | none | pending | pending | none |"
)
VALID_TASK_ROW = (
    "| TASK-001 | Implement access | implementation | yes | proposed | none | "
    "none | pending | pending | none |"
)
FINDING_PLACEHOLDER = (
    "| None | None | suggestion | open | none | none | none | pending | pending | none |"
)
VALID_FINDING_ROW = (
    "| FINDING-001 | security | minor | open | security-reviewer | TASK-001 | "
    "none | pending | pending | none |"
)


class FullLoopTemplateTests(unittest.TestCase):
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

    def write_loop_rows(self, fixture: Path, rows: list[str], active: bool = True) -> None:
        path = fixture / LOOP_MAP
        text = path.read_text(encoding="utf-8")
        if active:
            text = text.replace("Status: inactive", "Status: active", 1)
        path.write_text(text.replace(MAP_PLACEHOLDER, "\n".join(rows), 1), encoding="utf-8")

    def write_task_rows(self, fixture: Path, rows: list[str], active: bool = True) -> None:
        path = fixture / TASK_LEDGER
        text = path.read_text(encoding="utf-8")
        if active:
            text = text.replace("Status: inactive", "Status: active", 1)
        path.write_text(text.replace(TASK_PLACEHOLDER, "\n".join(rows), 1), encoding="utf-8")

    def write_finding_rows(self, fixture: Path, rows: list[str], active: bool = True) -> None:
        path = fixture / FINDING_LEDGER
        text = path.read_text(encoding="utf-8")
        if active:
            text = text.replace("Status: inactive", "Status: active", 1)
        path.write_text(text.replace(FINDING_PLACEHOLDER, "\n".join(rows), 1), encoding="utf-8")

    # Required files

    def test_01_valid_template_collection_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_02_missing_full_loop_readme_is_rejected(self) -> None:
        self.assert_rejected(
            lambda fixture: (fixture / README).unlink(),
            "missing required file: .looppilot/full-loop/README.md",
        )

    def test_03_missing_loop_map_template_is_rejected(self) -> None:
        self.assert_rejected(
            lambda fixture: (fixture / LOOP_MAP).unlink(),
            "missing required file: .looppilot/full-loop/LOOP-MAP-TEMPLATE.md",
        )

    def test_04_missing_loop_contract_template_is_rejected(self) -> None:
        self.assert_rejected(
            lambda fixture: (fixture / LOOP_CONTRACT).unlink(),
            "missing required file: .looppilot/full-loop/LOOP-CONTRACT-TEMPLATE.md",
        )

    def test_05_missing_task_ledger_template_is_rejected(self) -> None:
        self.assert_rejected(
            lambda fixture: (fixture / TASK_LEDGER).unlink(),
            "missing required file: .looppilot/full-loop/TASK-LEDGER-TEMPLATE.md",
        )

    def test_06_missing_finding_ledger_template_is_rejected(self) -> None:
        self.assert_rejected(
            lambda fixture: (fixture / FINDING_LEDGER).unlink(),
            "missing required file: .looppilot/full-loop/FINDING-LEDGER-TEMPLATE.md",
        )

    # Loop Map

    def test_07_valid_inactive_loop_map_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_08_invalid_loop_map_status_is_rejected(self) -> None:
        self.assert_rejected(
            lambda fixture: self.replace_once(
                fixture / LOOP_MAP, "Status: inactive", "Status: running"
            ),
            "invalid Loop Map Status 'running'",
        )

    def test_09_invalid_loop_status_is_rejected(self) -> None:
        def mutate(fixture: Path) -> None:
            self.write_loop_rows(
                fixture, [VALID_LOOP_ROW.replace("| planned |", "| shipping |")]
            )

        self.assert_rejected(mutate, "invalid Loop status 'shipping'")

    def test_10_duplicate_loop_id_is_rejected(self) -> None:
        self.assert_rejected(
            lambda fixture: self.write_loop_rows(
                fixture, [VALID_LOOP_ROW, VALID_LOOP_ROW]
            ),
            "duplicate Loop ID 'LOOP-001'",
        )

    def test_11_checked_accepted_loop_is_rejected(self) -> None:
        row = VALID_CLOSED_LOOP_ROW.replace("| closed |", "| accepted |")
        self.assert_rejected(
            lambda fixture: self.write_loop_rows(fixture, [row]),
            "only a closed Loop may be checked",
        )

    def test_12_checked_committed_loop_is_rejected(self) -> None:
        row = VALID_CLOSED_LOOP_ROW.replace("| closed |", "| committed |")
        self.assert_rejected(
            lambda fixture: self.write_loop_rows(fixture, [row]),
            "only a closed Loop may be checked",
        )

    def test_13_checked_checkpointed_loop_is_rejected(self) -> None:
        row = VALID_CLOSED_LOOP_ROW.replace("| closed |", "| checkpointed |")
        self.assert_rejected(
            lambda fixture: self.write_loop_rows(fixture, [row]),
            "only a closed Loop may be checked",
        )

    def test_14_checked_cancelled_loop_is_rejected(self) -> None:
        row = VALID_CLOSED_LOOP_ROW.replace("| closed |", "| cancelled |")
        self.assert_rejected(
            lambda fixture: self.write_loop_rows(fixture, [row]),
            "only a closed Loop may be checked",
        )

    def test_15_unchecked_closed_loop_is_rejected(self) -> None:
        row = VALID_CLOSED_LOOP_ROW.replace("| [x] |", "| [ ] |")
        self.assert_rejected(
            lambda fixture: self.write_loop_rows(fixture, [row]),
            "closed Loop must be checked",
        )

    def test_16_closed_loop_without_closure_is_rejected(self) -> None:
        row = VALID_CLOSED_LOOP_ROW.replace(
            "loops/LOOP-001/LOOP-CLOSURE.md", "pending"
        )
        self.assert_rejected(
            lambda fixture: self.write_loop_rows(fixture, [row]),
            "closed Loop requires a Closure reference",
        )

    def test_17_closed_loop_without_checkpoint_is_rejected(self) -> None:
        row = VALID_CLOSED_LOOP_ROW.replace("CHECKPOINT.md#loop-001", "pending")
        self.assert_rejected(
            lambda fixture: self.write_loop_rows(fixture, [row]),
            "closed Loop requires a Checkpoint reference",
        )

    def test_18_valid_closed_loop_projection_passes(self) -> None:
        result = self.validate_fixture(
            lambda fixture: self.write_loop_rows(fixture, [VALID_CLOSED_LOOP_ROW])
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_19_inactive_map_with_real_loop_is_rejected(self) -> None:
        self.assert_rejected(
            lambda fixture: self.write_loop_rows(
                fixture, [VALID_LOOP_ROW], active=False
            ),
            "inactive template contains a real Loop",
        )

    def test_20_unauthorized_commit_is_expressed_honestly(self) -> None:
        result = self.validate_fixture(
            lambda fixture: self.write_loop_rows(
                fixture, [UNAUTHORIZED_COMMIT_ROW]
            )
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    # Loop Contract

    def assert_contract_heading_rejected(self, heading: str) -> None:
        self.assert_rejected(
            lambda fixture: self.replace_once(fixture / LOOP_CONTRACT, heading, ""),
            f"missing required heading {heading!r}",
        )

    def test_21_missing_objective_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("## Objective")

    def test_22_missing_included_changes_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("## Included Changes")

    def test_23_missing_excluded_changes_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("## Excluded Changes")

    def test_24_missing_grouping_rationale_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("## Grouping Rationale")

    def test_25_missing_business_rules_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("## Business Rules and Invariants")

    def test_26_missing_concern_matrix_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("## Engineering Concern Matrix")

    def test_27_missing_architecture_profile_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("## Architecture Profile")

    def test_28_missing_task_dag_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("## Task DAG")

    def test_29_missing_reviewer_matrix_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("## Reviewer Matrix")

    def test_30_missing_spec_review_is_rejected(self) -> None:
        self.assert_rejected(
            lambda fixture: self.replace_once(
                fixture / LOOP_CONTRACT, "- Spec Review", "- None"
            ),
            "Mandatory Axes missing Spec Review",
        )

    def test_31_missing_standards_review_is_rejected(self) -> None:
        self.assert_rejected(
            lambda fixture: self.replace_once(
                fixture / LOOP_CONTRACT, "- Standards Review", "- None"
            ),
            "Mandatory Axes missing Standards Review",
        )

    def test_32_missing_integration_strategy_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("## Integration Strategy")

    def test_33_missing_functional_acceptance_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("### Functional Acceptance")

    def test_34_missing_engineering_acceptance_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("### Engineering Acceptance")

    def test_35_missing_delivery_acceptance_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("### Delivery Acceptance")

    def test_36_missing_barrier_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("### Review Barrier")

    def test_37_missing_budget_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("## Budget")

    def test_38_missing_authority_is_rejected(self) -> None:
        self.assert_contract_heading_rejected("## Authority")

    def test_39_valid_empty_loop_contract_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_40_contract_cannot_store_loop_lifecycle_status(self) -> None:
        self.assert_rejected(
            lambda fixture: self.replace_once(
                fixture / LOOP_CONTRACT,
                "- Contract Status: inactive",
                "- Contract Status: executing",
            ),
            "invalid Contract Status 'executing'",
        )

    # Task Ledger

    def test_41_valid_inactive_task_ledger_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_42_invalid_task_status_is_rejected(self) -> None:
        row = VALID_TASK_ROW.replace("| proposed |", "| shipping |")
        self.assert_rejected(
            lambda fixture: self.write_task_rows(fixture, [row]),
            "invalid Task status 'shipping'",
        )

    def test_43_duplicate_task_id_is_rejected(self) -> None:
        self.assert_rejected(
            lambda fixture: self.write_task_rows(
                fixture, [VALID_TASK_ROW, VALID_TASK_ROW]
            ),
            "duplicate Task ID 'TASK-001'",
        )

    def test_44_invalid_rework_task_id_is_rejected(self) -> None:
        row = (
            "| TASK-001-RX | Fix access | rework | yes | proposed | none | "
            "TASK-001 | pending | pending | TASK-001 |"
        )
        self.assert_rejected(
            lambda fixture: self.write_task_rows(fixture, [row]),
            "invalid Rework Task ID 'TASK-001-RX'",
        )

    def test_45_inactive_task_ledger_cannot_name_worker(self) -> None:
        row = TASK_PLACEHOLDER.replace("| none | none | pending", "| worker-a | none | pending")
        self.assert_rejected(
            lambda fixture: self.write_task_rows(fixture, [row], active=False),
            "inactive template cannot name a real Worker",
        )

    def test_46_worker_cannot_be_ledger_authority(self) -> None:
        self.assert_rejected(
            lambda fixture: self.replace_once(
                fixture / TASK_LEDGER,
                "- Worker may update Ledger: no",
                "- Worker may update Ledger: yes",
            ),
            "missing Task Ledger invariant '- Worker may update Ledger: no'",
        )

    def test_47_task_contract_cannot_be_authoritative(self) -> None:
        self.assert_rejected(
            lambda fixture: self.replace_once(
                fixture / TASK_LEDGER,
                "Detailed Task Contracts do not own authoritative Task status.",
                "Detailed Task Contracts own authoritative Task status.",
            ),
            "Task Contract must not own authoritative Task status",
        )

    def test_48_integrated_task_cannot_map_to_loop_closed(self) -> None:
        self.assert_rejected(
            lambda fixture: self.replace_once(
                fixture / TASK_LEDGER,
                "Integrated Task effect on Loop: none",
                "Integrated Task effect on Loop: closed",
            ),
            "integrated Task must not map to Loop closed",
        )

    # Finding Ledger

    def test_49_valid_inactive_finding_ledger_passes(self) -> None:
        result = self.validate_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_50_invalid_finding_severity_is_rejected(self) -> None:
        row = VALID_FINDING_ROW.replace("| minor |", "| critical |")
        self.assert_rejected(
            lambda fixture: self.write_finding_rows(fixture, [row]),
            "invalid Finding severity 'critical'",
        )

    def test_51_invalid_finding_status_is_rejected(self) -> None:
        row = VALID_FINDING_ROW.replace("| open |", "| fixing |")
        self.assert_rejected(
            lambda fixture: self.write_finding_rows(fixture, [row]),
            "invalid Finding status 'fixing'",
        )

    def test_52_duplicate_finding_id_is_rejected(self) -> None:
        self.assert_rejected(
            lambda fixture: self.write_finding_rows(
                fixture, [VALID_FINDING_ROW, VALID_FINDING_ROW]
            ),
            "duplicate Finding ID 'FINDING-001'",
        )

    def test_53_inactive_ledger_cannot_contain_real_finding(self) -> None:
        self.assert_rejected(
            lambda fixture: self.write_finding_rows(
                fixture, [VALID_FINDING_ROW], active=False
            ),
            "inactive template contains a real Finding",
        )

    def test_54_integrator_cannot_accept_risk(self) -> None:
        self.assert_rejected(
            lambda fixture: self.replace_once(
                fixture / FINDING_LEDGER,
                "- Integrator may accept risk: no",
                "- Integrator may accept risk: yes",
            ),
            "missing Finding Ledger invariant '- Integrator may accept risk: no'",
        )

    def test_55_risk_accepted_requires_supervisor_decision(self) -> None:
        row = VALID_FINDING_ROW.replace("| open |", "| risk-accepted |")
        self.assert_rejected(
            lambda fixture: self.write_finding_rows(fixture, [row]),
            "risk-accepted Finding requires Supervisor Decision",
        )

    def test_56_duplicate_requires_original_finding(self) -> None:
        row = VALID_FINDING_ROW.replace("| open |", "| duplicate |")
        self.assert_rejected(
            lambda fixture: self.write_finding_rows(fixture, [row]),
            "duplicate Finding requires original Finding reference",
        )

    def test_57_closed_finding_requires_verification(self) -> None:
        row = VALID_FINDING_ROW.replace("| open |", "| closed |")
        self.assert_rejected(
            lambda fixture: self.write_finding_rows(fixture, [row]),
            "closed Finding requires verification semantics",
        )

    def test_58_unresolved_blocker_prevents_closure_ready(self) -> None:
        row = VALID_FINDING_ROW.replace("| minor |", "| blocker |")

        def mutate(fixture: Path) -> None:
            self.write_finding_rows(fixture, [row])
            path = fixture / FINDING_LEDGER
            self.replace_once(path, "- Blocker: 0", "- Blocker: 1")
            self.replace_once(path, "- Closure ready: no", "- Closure ready: yes")

        self.assert_rejected(mutate, "unresolved blocker prevents Closure readiness")

    # State-source discipline

    def assert_source_invariant_rejected(self, invariant: str, message: str) -> None:
        self.assert_rejected(
            lambda fixture: self.replace_once(fixture / README, invariant, ""),
            message,
        )

    def test_59_missing_loop_map_authority_is_rejected(self) -> None:
        invariant = "`LOOP-MAP.md` MUST be the only authoritative source of Loop status."
        self.assert_source_invariant_rejected(invariant, "missing state-source invariant")

    def test_60_missing_task_ledger_authority_is_rejected(self) -> None:
        invariant = (
            "`TASK-LEDGER.md` MUST be the only authoritative source of Task status "
            "within a Full Loop."
        )
        self.assert_source_invariant_rejected(invariant, "missing state-source invariant")

    def test_61_missing_finding_ledger_authority_is_rejected(self) -> None:
        invariant = (
            "`FINDING-LEDGER.md` MUST be the only authoritative source of Finding "
            "status within a Full Loop."
        )
        self.assert_source_invariant_rejected(invariant, "missing state-source invariant")

    def test_62_missing_checkpoint_authority_is_rejected(self) -> None:
        invariant = "`CHECKPOINT.md` MUST be the only authoritative recovery entry point."
        self.assert_source_invariant_rejected(invariant, "missing state-source invariant")

    def test_63_checklist_cannot_be_full_loop_task_authority(self) -> None:
        def mutate(fixture: Path) -> None:
            self.append(
                fixture / ".looppilot/README.md",
                "\nChecklist is the authoritative source of Task status in Full Loop Mode.\n",
            )

        self.assert_rejected(mutate, "Checklist must not be Full Loop Task authority")

    def test_64_valid_projection_statement_passes(self) -> None:
        def mutate(fixture: Path) -> None:
            self.append(
                fixture / ".looppilot/CHECKLIST.md",
                "\nProjection authorities: LOOP-MAP.md, TASK-LEDGER.md, FINDING-LEDGER.md.\n",
            )

        result = self.validate_fixture(mutate)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_65_closed_loop_requires_honest_commit_result(self) -> None:
        row = VALID_CLOSED_LOOP_ROW.replace("not-created-not-required", "pending")
        self.assert_rejected(
            lambda fixture: self.write_loop_rows(fixture, [row]),
            "closed Loop requires an honest Commit result",
        )


if __name__ == "__main__":
    unittest.main()
