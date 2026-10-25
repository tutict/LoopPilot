from pathlib import Path
import importlib
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class InstallationDocConsistencyTests(unittest.TestCase):
    def module(self):
        self.assertTrue((ROOT / "scripts/installation_doc_validation.py").exists())
        return importlib.import_module("installation_doc_validation")

    def fixture(self, parent):
        root = Path(parent)
        for name in ("docs/installation.md", "distribution/managed-files.txt"):
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, root / name)
        return root

    def test_current_layout_matches_manifest(self):
        self.assertEqual([], self.module().validate_installation_documentation(ROOT))

    def test_undeclared_evaluation_directory_is_rejected(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(tmp)
            file = root / "docs/installation.md"
            file.write_text(file.read_text(encoding="utf-8").replace("|-- examples/", "|-- evaluations/\n|-- examples/"))
            self.assertTrue(module.validate_installation_documentation(root))

    def test_missing_managed_root_is_rejected(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(tmp)
            file = root / "docs/installation.md"
            self.assertIn("|-- LICENSE\n", file.read_text(encoding="utf-8"))
            file.write_text(file.read_text(encoding="utf-8").replace("|-- LICENSE\n", ""))
            self.assertTrue(module.validate_installation_documentation(root))

    def test_new_manifest_entry_requires_doc_update(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(tmp)
            with (root / "distribution/managed-files.txt").open("a") as file:
                file.write("new-managed.md\n")
            self.assertTrue(module.validate_installation_documentation(root))

    def test_generated_receipts_are_not_claimed_as_payload(self):
        self.assertEqual([], self.module().validate_installation_documentation(ROOT))
        self.assertNotIn(".looppilot-installation", self.module().manifest_display_entries(ROOT))
