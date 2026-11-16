"""M01-M20 loading-mode combination regressions through the public validator.

Synthetic Git-backed fixtures only (tests/option_b_fixture.py); no host
behavior and no acceptance claim. Matrix tokens are the frozen vocabulary
{explicit, implicit}. M12 demonstrates the candidate exemption with a
candidate-only record because a single record cannot mix evidence roles.
M13 exercises the pre-successor regime, where descriptive loading-mode
values keep the byte-identical equality rule (no tokenization).
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from evaluation_evidence_fixture import approve_record, digest, make_package
from option_b_fixture import initialize, rc_package, summary
from test_cross_host_acceptance import record

ROOT = Path(__file__).resolve().parents[1]
LEGACY_VALUE = "loaded, user scope, explicit invocation"


class LoadingModeCombinationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT / ".tmp").mkdir(exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(dir=ROOT / ".tmp")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.snapshot = Path(cls.temp.name) / "snapshot"
        cls.boundary = initialize(cls.snapshot, ROOT)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / ".tmp")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        shutil.copytree(self.snapshot, self.root)
        self.authority = Path(self.temp.name) / "operator/approved.json"
        self.authority.parent.mkdir(parents=True)
        self.boundary = dict(type(self).boundary)

    def custom_designation(self, mode):
        snapshot = Path(self.temp.name) / "custom-snapshot"
        self.boundary = initialize(snapshot, ROOT, loading_mode=mode)
        self.root = Path(self.temp.name) / "custom-repository"
        shutil.copytree(snapshot, self.root)

    def check(self):
        command = [sys.executable, str(self.root / "scripts/validate.py"), "--root", str(self.root),
                   "--evidence-index", str(self.authority), "--evidence-index-sha256", digest(self.authority)]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertNotIn("Traceback", result.stdout + result.stderr)
        return result.returncode, result.stdout + result.stderr

    def expect_pass(self):
        status, output = self.check()
        self.assertEqual(0, status, output)

    def expect_fail(self, token):
        status, output = self.check()
        self.assertNotEqual(0, status, output)
        self.assertIn(token.casefold(), output.casefold())

    def set_record_mode(self, path, value):
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        path.write_text("".join(f"- Skill loading mode: {value}\n" if line.startswith("- Skill loading mode: ")
                                else line for line in lines), encoding="utf-8")
        approve_record(self.root, path, self.authority)

    def test_m01_single_mode_control(self):
        packages = [rc_package(self.root, self.authority, self.boundary, number=i) for i in (1, 2)]
        summary(self.root, self.authority, packages)
        self.expect_pass()

    def test_m02_mixed_under_set_designation(self):
        self.custom_designation("explicit, implicit")
        packages = [rc_package(self.root, self.authority, self.boundary, number=i) for i in (1, 2)]
        packages.append(rc_package(self.root, self.authority, self.boundary, number=3, loading_mode="implicit"))
        summary(self.root, self.authority, packages)
        self.expect_pass()

    def test_m03_run_outside_designation_set(self):
        packages = [rc_package(self.root, self.authority, self.boundary, number=i) for i in (1, 2)]
        packages.append(rc_package(self.root, self.authority, self.boundary, number=3, loading_mode="implicit"))
        summary(self.root, self.authority, packages)
        self.expect_fail("designation Skill loading mode mismatch")

    def test_m04_record_subset_of_union(self):
        self.custom_designation("explicit, implicit")
        packages = [rc_package(self.root, self.authority, self.boundary, number=i) for i in (1, 2)]
        packages.append(rc_package(self.root, self.authority, self.boundary, number=3, loading_mode="implicit"))
        path = summary(self.root, self.authority, packages)
        self.set_record_mode(path, "explicit")
        self.expect_fail("record/run Skill loading mode mismatch")

    def test_m05_record_superset_of_union(self):
        self.custom_designation("explicit, implicit")
        packages = [rc_package(self.root, self.authority, self.boundary, number=i) for i in (1, 2)]
        path = summary(self.root, self.authority, packages)
        self.set_record_mode(path, "explicit, implicit")
        self.expect_fail("record/run Skill loading mode mismatch")

    def test_m06_record_non_canonical_order_rejected(self):
        self.custom_designation("explicit, implicit")
        packages = [rc_package(self.root, self.authority, self.boundary, number=i) for i in (1, 2)]
        packages.append(rc_package(self.root, self.authority, self.boundary, number=3, loading_mode="implicit"))
        path = summary(self.root, self.authority, packages)
        self.set_record_mode(path, "implicit, explicit")
        self.expect_fail("record/run Skill loading mode mismatch")

    def test_m07_record_duplicates_rejected(self):
        self.custom_designation("explicit, implicit")
        packages = [rc_package(self.root, self.authority, self.boundary, number=i) for i in (1, 2)]
        packages.append(rc_package(self.root, self.authority, self.boundary, number=3, loading_mode="implicit"))
        path = summary(self.root, self.authority, packages)
        self.set_record_mode(path, "explicit, explicit, implicit")
        self.expect_fail("record/run Skill loading mode mismatch")

    def test_m08_designation_whitespace_normalized(self):
        self.custom_designation("explicit,implicit")
        packages = [rc_package(self.root, self.authority, self.boundary, number=i) for i in (1, 2)]
        packages.append(rc_package(self.root, self.authority, self.boundary, number=3, loading_mode="implicit"))
        summary(self.root, self.authority, packages)
        self.expect_pass()

    def test_m09_implicit_only_shape_coverage(self):
        self.custom_designation("implicit")
        package = rc_package(self.root, self.authority, self.boundary, number=1, loading_mode="implicit")
        summary(self.root, self.authority, [package])
        self.expect_fail("scenario shapes")

    def test_m10_single_shape_explicit_coverage(self):
        package = rc_package(self.root, self.authority, self.boundary, number=1)
        summary(self.root, self.authority, [package])
        self.expect_fail("scenario shapes")

    def test_m11_candidate_cannot_satisfy_declared_mode_coverage(self):
        # A mixed-role record is rejected by role consistency before coverage;
        # the coverage rule itself is exercised with reference runs in M18.
        self.custom_designation("explicit, implicit")
        reference = rc_package(self.root, self.authority, self.boundary, number=1)
        candidate = rc_package(self.root, self.authority, self.boundary, number=2,
                               role="candidate", host="Claude Code", loading_mode="implicit")
        summary(self.root, self.authority, [reference, candidate])
        self.expect_fail("record/run RC evidence role mismatch")

    def test_m12_candidate_only_record_exempt_from_designation_set(self):
        packages = [rc_package(self.root, self.authority, self.boundary, number=i,
                               role="candidate", host="Claude Code", loading_mode="implicit") for i in (1, 2)]
        summary(self.root, self.authority, packages, role="candidate", host="Claude Code")
        self.expect_pass()

    def test_m13_legacy_descriptive_pre_successor_byte_identical(self):
        packages = [make_package(self.root, self.authority, evaluation_id=f"EVAL-LEGACY-{i:03}",
                    scenario_id=f"legacy-scenario-{i}", shape="lightweight" if i == 1 else "full-loop",
                    loading_mode=LEGACY_VALUE) for i in (1, 2)]
        runs = [json.loads((p / "run.json").read_text(encoding="utf-8")) for p in packages]
        text = record(Skill_loading_mode=LEGACY_VALUE,
                      Evaluation_IDs=", ".join(p.name for p in packages),
                      Scenario_IDs=", ".join(r["scenario_id"] for r in runs))
        text = text.replace("trace reference", f"[trace]({packages[0].name}/evidence/events.jsonl#result-1)")
        path = packages[0].parent / "host-acceptance.md"
        path.write_text(text, encoding="utf-8")
        approve_record(self.root, path, self.authority)
        self.expect_pass()

    def test_m14_case_sensitive_tokens_fail_closed(self):
        self.custom_designation("explicit, Implicit")
        packages = [rc_package(self.root, self.authority, self.boundary, number=i) for i in (1, 2)]
        summary(self.root, self.authority, packages)
        self.expect_fail("unknown tokens")

    def test_m15_empty_designation_fails_closed(self):
        self.custom_designation("")
        rc_package(self.root, self.authority, self.boundary, number=1)
        self.expect_fail("combination is empty")

    def test_m16_unknown_designation_token_fails_closed(self):
        self.custom_designation("banana")
        packages = [rc_package(self.root, self.authority, self.boundary, number=i) for i in (1, 2)]
        summary(self.root, self.authority, packages)
        self.expect_fail("unknown tokens")

    def test_m17_descriptive_comma_value_rejected_as_new_designation(self):
        self.custom_designation(LEGACY_VALUE)
        packages = [rc_package(self.root, self.authority, self.boundary, number=i) for i in (1, 2)]
        summary(self.root, self.authority, packages)
        self.expect_fail("unknown tokens")

    def test_m18_record_covers_only_explicit_under_mixed_declaration(self):
        self.custom_designation("explicit, implicit")
        packages = [rc_package(self.root, self.authority, self.boundary, number=i) for i in (1, 2)]
        path = summary(self.root, self.authority, packages)
        self.set_record_mode(path, "explicit")
        self.expect_fail("record does not cover declared Skill loading mode combination")

    def test_m19_unknown_extra_designation_token_with_matching_runs(self):
        self.custom_designation("explicit, implicit, banana")
        packages = [rc_package(self.root, self.authority, self.boundary, number=i) for i in (1, 2)]
        packages.append(rc_package(self.root, self.authority, self.boundary, number=3, loading_mode="implicit"))
        summary(self.root, self.authority, packages)
        self.expect_fail("unknown tokens")

    def test_m20_unknown_token_in_record_value(self):
        self.custom_designation("explicit, implicit")
        packages = [rc_package(self.root, self.authority, self.boundary, number=i) for i in (1, 2)]
        packages.append(rc_package(self.root, self.authority, self.boundary, number=3, loading_mode="implicit"))
        path = summary(self.root, self.authority, packages)
        self.set_record_mode(path, "explicit, implicit, banana")
        self.expect_fail("record/run Skill loading mode mismatch")


if __name__ == "__main__":
    unittest.main()