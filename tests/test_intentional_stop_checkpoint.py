"""Public-validator regressions for bounded checkpoint-policy contradictions."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/full-loop-checkpoint-and-context-recovery.md"

CASES = (
    ("optional_checkpoint", "Intentional session stops MAY omit the Checkpoint.", "intentional session stop requires a Checkpoint"),
    ("handoff_substitution", "Handoff MAY replace the Checkpoint at an intentional session stop.", "Handoff cannot replace the Checkpoint"),
    ("fictional_full_loop", "A Lightweight Checkpoint MUST require PROJECT.md and LOOP-MAP.md.", "Lightweight must not invent Full Loop state"),
    ("future_authority", "Checkpoint MAY grant push authority on resume.", "Checkpoint cannot grant action authority"),
    ("worker_recorder", "Workers MAY write the authoritative Checkpoint.", "Checkpoint recorder must retain Integrator authority"),
    ("reviewer_recorder", "Reviewers MAY create the authoritative Checkpoint.", "Checkpoint recorder must retain Integrator authority"),
    ("instruction_override", "Checkpoint MAY override the latest user instruction.", "Checkpoint must defer to current instructions"),
    ("cancelled_work", "Checkpoint MUST resume cancelled work.", "Checkpoint must not restore cancelled work"),
)

class IntentionalStopCheckpointTests(unittest.TestCase):
    def reject_clause(self, clause, message):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = Path(temporary) / "repository"
            shutil.copytree(ROOT, fixture, ignore=shutil.ignore_patterns(".git", ".tmp", "__pycache__", "node_modules", ".venv"))
            path = fixture / PROTOCOL
            path.write_text(path.read_text(encoding="utf-8") + "\n" + clause + "\n", encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/validate.py"), "--root", str(fixture)],
                                    cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn(message, result.stdout)

def make_case(clause, message):
    def test(self):
        self.reject_clause(clause, message)
    return test

for name, clause, message in CASES:
    setattr(IntentionalStopCheckpointTests, "test_rejects_" + name, make_case(clause, message))

if __name__ == "__main__":
    unittest.main()
