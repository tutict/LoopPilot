"""IA04 procedural regressions: bounded static checks, never host behavior proof."""
from pathlib import Path
import copy
import importlib
import itertools
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
RULES = importlib.import_module("instruction_consistency_validation")
MODE = "docs/mode-selection-and-escalation.md"
ROUTES = (
    MODE,
    "docs/multi-agent-coordination.md",
    "docs/coordination-necessity-and-delegation-fallback.md",
    "docs/protocol-modes-and-state-sources.md",
    "docs/protocol-load-profiles.md",
    "docs/safety-and-stopping.md",
    "docs/loop-engineering-model.md",
    "docs/design-rationale.md",
)


class ModeReassessmentTests(unittest.TestCase):
    def fixture(self, temp):
        target = Path(temp) / "source"
        for name in ("AGENTS.md", *ROUTES):
            dest = target / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        return target

    def assert_ia04(self, errors):
        self.assertTrue(any("mode reassessment" in error for error in errors), errors)

    def mutate_prose(self, clause):
        for name in ROUTES:
            with self.subTest(path=name, clause=clause), tempfile.TemporaryDirectory() as temp:
                target = self.fixture(temp)
                path = target / name
                path.write_text(path.read_text(encoding="utf-8") + "\n" + clause + "\n", encoding="utf-8")
                self.assert_ia04(RULES.validate_instruction_consistency(target))

    def test_current_routed_documents_validate(self):
        self.assertEqual([], RULES.validate_instruction_consistency(ROOT))

    def test_canonical_procedure_orders_risk_review_then_coordination(self):
        text = (ROOT / MODE).read_text(encoding="utf-8")
        steps = re.findall(r"^\d+\. (.*(?:\n(?!\d+\.|\n).*)*)", text, re.MULTILINE)
        self.assertGreaterEqual(len(steps), 4, "explicit reassessment procedure required")
        for step, token in zip(steps, ("Product Risk", "minimum", "Coordination Necessity", "Full Loop")):
            self.assertIn(token, step)
        self.assertIn("Lightweight", steps[3])

    def test_all_independent_axes_positive_and_reverse_mode_mutations(self):
        for risk, coordination, specialist, kind in itertools.product(
                ("low", "high"), ("none", "required"), ("no", "yes"), ("coding", "non-coding")):
            with self.subTest(risk=risk, coordination=coordination, specialist=specialist, kind=kind):
                row = dict(case="probe", risk=risk, coordination=coordination,
                           specialist=specialist, kind=kind,
                           mode="Full Loop gate" if coordination == "required" else "Lightweight allowed",
                           review_floor="enhanced" if risk == "high" else "standard",
                           specialist_depth="targeted" if specialist == "yes" else "none")
                self.assertEqual([], RULES.check_mode_cases([row]))
                wrong = copy.deepcopy(row)
                wrong["mode"] = "Lightweight allowed" if coordination == "required" else "Full Loop gate"
                self.assertTrue(RULES.check_mode_cases([wrong]))

    def test_risk_only_changes_preserve_mode_and_raise_minimum(self):
        rows = RULES.parse_mode_cases((ROOT / RULES.COORDINATION).read_text(encoding="utf-8"))
        for row in rows:
            with self.subTest(case=row["case"]):
                changed = dict(row, risk="high", review_floor="enhanced")
                self.assertEqual(row["mode"], changed["mode"])
                self.assertEqual([], RULES.check_mode_cases([changed]))
                changed["review_floor"] = "standard"
                self.assertTrue(RULES.check_mode_cases([changed]))

    def test_high_risk_procedural_shortcuts_rejected(self):
        for clause in (
            "If newly discovered product risk is high, create a Full Loop Contract.",
            "When sensitive-data impact appears, the Supervisor must switch to Full Loop.",
            "New security risk requires Full Loop even with one implementation owner.",
            "Full Loop is mandatory when product risk increases.",
            "A TypeScript and Rust security contract selects Full Loop.",
        ):
            self.mutate_prose(clause)

    def test_data_integrity_risk_only_shortcuts_rejected(self):
        for clause in (
            "A SQLite partial-success boundary selects Full Loop.",
            "A migration boundary requires Full Loop even without coordination.",
            "Transaction corruption requires a Full Loop Contract.",
            "Duplicate writes require Full Loop with a single implementation owner.",
        ):
            with self.subTest(clause=clause):
                self.assert_ia04(RULES.check_mode_procedure(clause, MODE))

    def test_specialist_procedural_shortcuts_rejected(self):
        for clause in (
            "When a specialist Reviewer is needed, select Full Loop.",
            "Full Loop is required whenever Security Review becomes necessary.",
        ):
            self.mutate_prose(clause)

    def test_stop_or_preservation_must_not_imply_full_loop(self):
        for clause in (
            "Escalation records the reason, preserves existing evidence, and creates the formal Full Loop Contract.",
            "A hard trigger creates a Full Loop Contract before work resumes.",
            "Stop and create a Full Loop Contract before more implementation.",
        ):
            self.mutate_prose(clause)

    def test_coordination_required_cannot_be_downgraded(self):
        self.mutate_prose("When Coordination Necessity is required, continue Lightweight without a Full Loop gate.")

    def test_negative_and_conditional_risk_prose_remains_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            target = self.fixture(temp)
            path = target / MODE
            path.write_text(path.read_text(encoding="utf-8") + "\n" +
                            "High product risk alone MUST NOT require Full Loop.\n" +
                            "A specialist Reviewer does not require Full Loop.\n" +
                            "When coordination requires Full Loop, create a Full Loop Contract.\n",
                            encoding="utf-8")
            self.assertEqual([], RULES.validate_instruction_consistency(target))

    def test_mermaid_risk_and_specialist_bypasses_rejected(self):
        for source in ("New high product risk", "Specialist Reviewer needed", "Hard Trigger", "Preserve Lightweight Evidence"):
            for name in ROUTES:
                with self.subTest(source=source, path=name), tempfile.TemporaryDirectory() as temp:
                    target = self.fixture(temp)
                    path = target / name
                    path.write_text(path.read_text(encoding="utf-8") + f"\n```mermaid\nflowchart TD\n"
                                    f"    origin[{source}] --> detour[Assess boundary]\n"
                                    "    detour --> target[Create Full Loop Contract]\n```\n", encoding="utf-8")
                    self.assert_ia04(RULES.validate_instruction_consistency(target))

    def test_mermaid_no_coordination_branch_cannot_reach_full_loop(self):
        with tempfile.TemporaryDirectory() as temp:
            target = self.fixture(temp)
            path = target / MODE
            path.write_text(path.read_text(encoding="utf-8") + "\n```mermaid\nflowchart TD\n"
                            "    risk[Assess Product Risk] --> review[Set minimum review depth]\n"
                            "    review --> gate{Coordination required?}\n"
                            "    gate -->|No| wrong[Full Loop Contract]\n"
                            "    gate -->|Yes| other[Lightweight allowed]\n```\n", encoding="utf-8")
            self.assert_ia04(RULES.validate_instruction_consistency(target))

    def test_mermaid_positive_flow_accepts_arbitrary_ids_and_line_order(self):
        with tempfile.TemporaryDirectory() as temp:
            target = self.fixture(temp)
            path = target / MODE
            path.write_text(path.read_text(encoding="utf-8") + "\n```mermaid\nflowchart TD\n"
                            "    third -->|No| done[Lightweight allowed]\n"
                            "    third -->|Yes| full[Full Loop Contract]\n"
                            "    second --> third{Coordination required?}\n"
                            "    first[Assess Product Risk] --> second[Set minimum review depth]\n```\n", encoding="utf-8")
            self.assertEqual([], RULES.validate_instruction_consistency(target))

    def test_live_diagram_mutations_cannot_skip_reassessment_stages(self):
        text = (ROOT / MODE).read_text(encoding="utf-8")
        for old, new in (
            ("R --> V[Set minimum review validation and evidence depth]", "R --> G"),
            ("V --> G{Coordination required?}", "V --> F"),
            ("G{Coordination required?}", "G{Specialist review or coordination required?}"),
            ("G -->|Yes| F[Full Loop Contract Barrier]", "G -->|Yes| F[Full Loop Contract Barrier]\n    R -.-> F"),
            ("G -->|Yes| F[Full Loop Contract Barrier]", "G -->|Yes| F[Full Loop Contract Barrier]\n    P --> F"),
        ):
            with self.subTest(mutation=new):
                self.assertIn(old, text)
                self.assert_ia04(RULES.check_mode_procedure(text.replace(old, new, 1), MODE))

    def test_disconnected_cyclic_shortcut_is_not_silently_ignored(self):
        text = "```mermaid\nflowchart TD\n    a[New high risk] --> b[Full Loop Contract]\n    b --> a\n```\n"
        self.assert_ia04(RULES.check_mode_procedure(text, MODE))

    def test_wrapped_prose_shortcuts_are_not_hidden_by_formatting(self):
        for clause in (
            "When sensitive-data impact appears, the Supervisor\nmust switch to Full Loop.",
            "New high product risk\nrequires Full Loop even without coordination.",
            "Full Loop is mandatory\nwhen a specialist Reviewer becomes necessary.",
        ):
            with self.subTest(clause=clause):
                self.assert_ia04(RULES.check_mode_procedure(clause, MODE))

    def test_public_validator_rejects_procedure_bypass_with_valid_case_table(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "source"
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(
                ".git", ".claude", ".codex", ".agents", ".tmp", "__pycache__", ".pytest_cache"))
            path = target / MODE
            path.write_text(path.read_text(encoding="utf-8") + "\n```mermaid\nflowchart TD\n"
                            "    evidence[New high risk] --> contract[Create Full Loop Contract]\n```\n",
                            encoding="utf-8")
            self.assertEqual([], RULES.check_mode_cases(RULES.parse_mode_cases(
                (target / RULES.COORDINATION).read_text(encoding="utf-8"))))
            result = subprocess.run([sys.executable, "-B", str(target / "scripts/validate.py"),
                                     "--root", str(target)], capture_output=True, text=True)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("mode reassessment", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
