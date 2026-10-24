import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from option_b_validation import validate_option_b  # noqa: E402


SUCCESSOR = """# Option B Successor Reference Policy

- Successor ID: OPTION-B-REFERENCE-2026-10-24
- Policy version: option-b-successor-v1
- Authorization basis: one-time user authorization in the attached task dated 2026-10-24
- Effective boundary: the first commit containing this policy, approval record, validator, and regression tests
- Historical effect: no retrospective changes
- Reference Host choices: Claude Code, Codex
- Gate 4 threshold: unchanged
- Gate 5 disclosure: unchanged
- Automatic Reference switching: forbidden
- Historical verdict changes: forbidden
- Standing authority: none

## C01 — Reference qualification

Future applicable RCs may designate Claude Code or Codex as the sole Reference Host.

## C02 — Unique designation

Each RC has exactly one traceable Reference designation.

## C03 — Designation timing

The designation is finalized before the first formal acceptance arm and cannot be changed automatically.

## C04 — Gate 4 binding

Gate 4 uses an accepted or accepted-with-residuals record for that RC's designated Reference Host.

## C05 — Gate 5 and other Hosts

The other eligible Host remains a Candidate Host and keeps its disclosure obligations.

## C06 — Run and evidence binding

The designation binds RC, successor, host version, model identity, provider identity, endpoint identity, loading mode, commit and tree, run IDs, evidence index, independent review, and verdict.

## C07 — Historical isolation

Historical verdicts and historical evidence cannot be promoted or relabeled.

## C08 — Forward effectiveness

This policy applies only after its effective boundary and never rewrites earlier RCs. It does not establish a general F2 process.
"""


REFERENCE = """# RC Candidate Reference Designation

- RC version: v1.0.0-rc1
- Successor ID: OPTION-B-REFERENCE-2026-10-24
- Successor policy: docs/release/option-b-reference-successor.md
- Reference designation ID: RC1-REF-CODEX
- Reference Host: Codex
- Other eligible Host: Claude Code
- Other Host role: Candidate Host; unverified disclosure retained
- Designation state: preflight-designation
- Designation date: 2026-10-24
- Formal acceptance arms at designation: none
- Reference host version: unknown
- Model identity: unknown
- Provider identity: unknown
- Endpoint identity: unknown
- Skill loading mode: unknown
- RC baseline commit: pending-before-formal-run
- RC baseline tree: pending-before-formal-run
"""


DECISION = """# RC Candidate Decision

- RC version: v1.0.0-rc1
- Successor ID: OPTION-B-REFERENCE-2026-10-24
- Reference designation record: docs/release/rc-candidate-reference.md
- Reference Host: Codex
- Decision state: candidate-prepared-not-release-ready
- Gate 4: unmet
- Gate 5: all-named-candidates-recorded-or-disclosed-unverified
- Acceptance status: not-run
- Host/model identity status: unverified
- Release tag: not-created
"""

APPROVAL = """# Option B Reference Successor — Authorization Record

- Decision ID: OPTION-B-REFERENCE-2026-10-24
- Decision date: 2026-10-24
- Policy version: option-b-successor-v1
- RC-specific choice: Codex for `v1.0.0-rc1`
- Gate 4 threshold: unchanged
- Gate 5 disclosure: unchanged
- Historical effect: none
- Standing authority: none
- Authorized action: implement a bounded, forward-effective successor allowing an applicable RC to designate one Reference Host from Claude Code or Codex
"""


class OptionBSuccessorTests(unittest.TestCase):
    def write_fixture(self, successor=SUCCESSOR, reference=REFERENCE):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "docs" / "release").mkdir(parents=True)
        (root / "docs" / "release" / "option-b-reference-successor.md").write_text(successor, encoding="utf-8")
        (root / "docs" / "release" / "option-b-reference-approval.md").write_text(APPROVAL, encoding="utf-8")
        (root / "docs" / "release" / "rc-candidate-reference.md").write_text(reference, encoding="utf-8")
        (root / "docs" / "release" / "rc-candidate-decision.md").write_text(DECISION, encoding="utf-8")
        self.addCleanup(temp.cleanup)
        return root

    def check(self, root):
        errors = []
        validate_option_b(root, errors)
        return errors

    def test_successor_and_codex_designation_pass(self):
        self.assertEqual([], self.check(self.write_fixture()))

    def test_reference_host_must_be_unique_and_eligible(self):
        reference = REFERENCE.replace("- Reference Host: Codex\n", "- Reference Host: Codex\n- Reference Host: Claude Code\n")
        errors = self.check(self.write_fixture(reference=reference))
        self.assertTrue(any("duplicate metadata field 'Reference Host'" in error for error in errors))

    def test_designation_must_precede_formal_acceptance(self):
        reference = REFERENCE.replace("- Formal acceptance arms at designation: none", "- Formal acceptance arms at designation: started")
        errors = self.check(self.write_fixture(reference=reference))
        self.assertTrue(any("no formal arms may have started" in error for error in errors))

    def test_reference_cannot_auto_switch(self):
        successor = SUCCESSOR.replace("- Automatic Reference switching: forbidden", "- Automatic Reference switching: allowed")
        errors = self.check(self.write_fixture(successor=successor))
        self.assertTrue(any("Automatic Reference switching" in error for error in errors))

    def test_successor_must_preserve_gate_thresholds(self):
        successor = SUCCESSOR.replace("- Gate 4 threshold: unchanged", "- Gate 4 threshold: relaxed")
        errors = self.check(self.write_fixture(successor=successor))
        self.assertTrue(any("Gate 4" in error for error in errors))

    def test_reference_record_must_bind_successor(self):
        reference = REFERENCE.replace("OPTION-B-REFERENCE-2026-10-24", "OTHER-SUCCESSOR")
        errors = self.check(self.write_fixture(reference=reference))
        self.assertTrue(any("bind the Option B successor" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
