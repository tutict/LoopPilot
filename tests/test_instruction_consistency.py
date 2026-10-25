"""Finite documentation consistency checks, not a natural-language judge."""
from pathlib import Path
import copy
import importlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class InstructionConsistencyTests(unittest.TestCase):
    def module(self):
        self.assertTrue((ROOT / "scripts/instruction_consistency_validation.py").is_file(),
                        "deterministic consistency validator is required")
        return importlib.import_module("instruction_consistency_validation")

    def cases(self):
        return self.module().parse_mode_cases((ROOT / "docs/coordination-necessity-and-delegation-fallback.md").read_text(encoding="utf-8"))

    def minimal_copy(self, parent):
        target = Path(parent) / "source"
        for name in ("AGENTS.md", "docs/coordination-necessity-and-delegation-fallback.md", "docs/multi-agent-coordination.md"):
            dest = target / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        return target

    def test_current_instruction_domains_are_consistent(self):
        self.assertEqual([], self.module().validate_instruction_consistency(ROOT))

    def test_pre_edit_read_prohibitions_are_rejected(self):
        module = self.module()
        for clause in ("Do not read the repository before an edit.", "The agent must not inspect source before modifying."):
            with self.subTest(clause=clause), tempfile.TemporaryDirectory() as temp:
                target = self.minimal_copy(temp)
                with (target / "AGENTS.md").open("a", encoding="utf-8") as file:
                    file.write("\n" + clause + "\n")
                self.assertTrue(any("pre-edit inspection conflict" in e for e in module.validate_instruction_consistency(target)))

    def test_all_seven_structured_cases_validate(self):
        rows = self.cases()
        self.assertEqual({f"M{i}" for i in range(1, 8)}, {row["case"] for row in rows})
        self.assertEqual([], self.module().check_mode_cases(rows))

    def test_specialist_without_coordination_allows_lightweight(self):
        rows = self.cases()
        row = next(row for row in rows if row["case"] == "M4")
        self.assertEqual(("none", "yes", "Lightweight allowed"),
                         (row["coordination"], row["specialist"], row["mode"]))
        bad = copy.deepcopy(rows)
        next(r for r in bad if r["case"] == "M4")["mode"] = "Full Loop gate"
        self.assertTrue(self.module().check_mode_cases(bad))

    def test_high_risk_changes_review_depth_not_mode(self):
        rows = self.cases()
        row = next(r for r in rows if r["case"] == "M2")
        self.assertEqual(("high", "none", "Lightweight allowed", "enhanced"),
                         (row["risk"], row["coordination"], row["mode"], row["review_floor"]))
        for field, value in (("mode", "Full Loop gate"), ("review_floor", "standard")):
            bad = copy.deepcopy(rows)
            next(r for r in bad if r["case"] == "M2")[field] = value
            self.assertTrue(self.module().check_mode_cases(bad))

    def test_real_coordination_retains_full_loop_gate(self):
        rows = self.cases()
        for case in ("M3", "M5"):
            row = next(r for r in rows if r["case"] == case)
            self.assertEqual(("required", "Full Loop gate"), (row["coordination"], row["mode"]))
            bad = copy.deepcopy(rows)
            next(r for r in bad if r["case"] == case)["mode"] = "Lightweight allowed"
            self.assertTrue(self.module().check_mode_cases(bad))

    def test_noncoding_keeps_the_same_coordination_axis(self):
        rows = self.cases()
        for case, coordination, mode in (("M6", "none", "Lightweight allowed"), ("M7", "required", "Full Loop gate")):
            row = next(r for r in rows if r["case"] == case)
            self.assertEqual(("non-coding", coordination, mode), (row["kind"], row["coordination"], row["mode"]))
            bad = copy.deepcopy(rows)
            next(r for r in bad if r["case"] == case)["mode"] = "Full Loop gate" if coordination == "none" else "Lightweight allowed"
            self.assertTrue(self.module().check_mode_cases(bad))

    def test_specialist_escalation_contradiction_is_rejected(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as temp:
            target = self.minimal_copy(temp)
            with (target / "docs/multi-agent-coordination.md").open("a", encoding="utf-8") as file:
                file.write("\nLightweight work must escalate before it requires a specialist Reviewer.\n")
            self.assertTrue(any("specialist mode conflict" in e for e in module.validate_instruction_consistency(target)))

    def test_missing_case_is_rejected(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as temp:
            target = self.minimal_copy(temp)
            path = target / "docs/coordination-necessity-and-delegation-fallback.md"
            text = path.read_text()
            self.assertIn("| M2 |", text)
            path.write_text("\n".join(line for line in text.splitlines() if not line.startswith("| M2 |")) + "\n")
            self.assertTrue(module.validate_instruction_consistency(target))

    def test_public_validator_rejects_conflicting_clause(self):
        self.module()
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "source"
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", ".claude", ".codex", ".agents", ".tmp", "__pycache__", ".pytest_cache"))
            with (target / "AGENTS.md").open("a", encoding="utf-8") as file:
                file.write("\nDo not read the repository before an edit.\n")
            result = subprocess.run([sys.executable, str(target / "scripts/validate.py"), "--root", str(target)], capture_output=True, text=True)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("pre-edit inspection conflict", result.stdout + result.stderr)


    def test_specialist_adds_targeted_depth_without_changing_risk_floor(self):
        rows = self.cases()
        standard = next(r for r in rows if r["case"] == "M1")
        specialist = next(r for r in rows if r["case"] == "M4")
        self.assertIn("review_floor", specialist)
        self.assertEqual("standard", specialist["review_floor"])
        self.assertEqual(standard["review_floor"], specialist["review_floor"])
        self.assertEqual("targeted", specialist["specialist_depth"])
        self.assertEqual("none", standard["specialist_depth"])
        enhanced = copy.deepcopy(rows)
        row = next(r for r in enhanced if r["case"] == "M1")
        row["specialist"] = "yes"
        row["specialist_depth"] = "targeted"
        self.assertEqual([], self.module().check_mode_cases(enhanced))
        for field, value in (("mode", "Full Loop gate"), ("review_floor", "enhanced"), ("specialist_depth", "none")):
            invalid = copy.deepcopy(rows)
            next(r for r in invalid if r["case"] == "M4")[field] = value
            self.assertTrue(self.module().check_mode_cases(invalid))
