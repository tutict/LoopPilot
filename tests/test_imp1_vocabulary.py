"""Regression tests for the IMP-1 banned-term scan required by gate P12.

The scan is the only thing standing between an implicit-activation arm and a
prompt that quietly tells the host what to do. These tests pin three properties
apart: that every term in the §7.1 list is actually wired up, that the scan does
not over-match inflections it was never given, and that the command-line exit
codes distinguish clean from contaminated from unusable input.

The positive control is deliberately written twice — once generated from
``BANNED_TERMS`` so no term can be silently unwired, and once as hard-coded
prose so a term silently *removed* from the list is still caught.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY_ROOT / "scripts" / "imp1_vocabulary_validation.py"

sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import imp1_vocabulary_validation as imp1  # noqa: E402


# Contains none of the seventeen banned terms. Checked by test_list_is_frozen
# against the list itself, so it cannot rot silently if §7.1 ever changes.
NEGATIVE_CONTROL = (
    "Please tidy the helper in util.py so the two functions share one code\n"
    "path, then run the unit tests and report exactly what changed.\n"
)

# Inflections and substrings that whole-word matching must NOT flag. Each one
# embeds a banned term but is not that term.
BOUNDARY_CONTROL = (
    "The Ledgers and modes were reactivated, and the protocols are skillful.\n"
)


def _write(directory: Path, name: str, body: str, encoding: str = "utf-8") -> Path:
    path = directory / name
    path.write_text(body, encoding=encoding)
    return path


class BannedTermScanTests(unittest.TestCase):
    """The scan itself, exercised directly."""

    def test_negative_control_is_clean(self) -> None:
        self.assertEqual(imp1.scan_text(NEGATIVE_CONTROL), [])

    def test_boundary_control_does_not_over_match(self) -> None:
        """Inflections are not banned; matching them would broaden §7.1."""
        self.assertEqual(imp1.scan_text(BOUNDARY_CONTROL), [])

    def test_every_listed_term_is_wired(self) -> None:
        """Generated positive control: each term must produce a finding."""
        text = "\n".join(f"line {index}: {term}" for index, term in enumerate(imp1.BANNED_TERMS))
        findings = imp1.scan_text(text)
        for term in imp1.BANNED_TERMS:
            self.assertTrue(
                any(finding.startswith(f"banned-term:{term}|") for finding in findings),
                f"{term} produced no finding",
            )

    def test_hard_coded_prose_positive_control(self) -> None:
        """Catches a term silently removed from the list."""
        text = "Load the Skill, follow the protocol, and write a Checkpoint.\n"
        found = {finding.split("|")[0].removeprefix("banned-term:") for finding in imp1.scan_text(text)}
        self.assertEqual(found, {"Skill", "protocol", "Checkpoint"})

    def test_matching_is_case_insensitive(self) -> None:
        self.assertEqual(len(imp1.scan_text("loOpPiLoT\n")), 1)

    def test_multi_word_term_spans_a_line_break(self) -> None:
        findings = imp1.scan_text("run this in Full\nLoop style\n")
        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].startswith("banned-term:Full Loop|"))

    def test_findings_report_line_numbers(self) -> None:
        findings = imp1.scan_text("clean first line\nnow the rubric\n")
        self.assertEqual(len(findings), 1)
        self.assertIn("|line 2|", findings[0])

    def test_list_is_frozen_at_seventeen_terms(self) -> None:
        """§7.1 lists seventeen terms; a change here must be a §7.1 change."""
        self.assertEqual(len(imp1.BANNED_TERMS), 17)


class CommandLineTests(unittest.TestCase):
    """Exit codes and report shape, exercised through the public entry point."""

    def _run(self, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--prompt", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_clean_prompt_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = _write(Path(directory), "IMP-1.txt", NEGATIVE_CONTROL)
            result = self._run(path)
        self.assertEqual(result.returncode, 0)
        self.assertIn("State: IMP1_VOCABULARY_CLEAN", result.stdout)
        self.assertIn("Findings: 0", result.stdout)
        self.assertIn("Terms checked: 17", result.stdout)

    def test_contaminated_prompt_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = _write(Path(directory), "IMP-1.txt", "use the Skill now\n")
            result = self._run(path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("State: IMP1_VOCABULARY_CONTAMINATED", result.stdout)
        self.assertIn("banned-term:Skill|", result.stdout)

    def test_byte_order_mark_does_not_hide_a_hit(self) -> None:
        """A BOM defeated an equivalent content check elsewhere; not here."""
        with tempfile.TemporaryDirectory() as directory:
            path = _write(Path(directory), "IMP-1.txt", "use the Skill now\n", encoding="utf-8-sig")
            result = self._run(path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("banned-term:Skill|", result.stdout)

    def test_missing_prompt_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self._run(Path(directory) / "absent.txt")
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
