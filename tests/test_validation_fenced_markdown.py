"""Markdown validation must not interpret preserved evidence inside fenced blocks."""
import importlib.util
import sys
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("public_validate", ROOT / "scripts" / "validate.py")
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
sys.path.insert(0, str(ROOT / "scripts"))
spec.loader.exec_module(validator)


class FencedMarkdownValidationTests(unittest.TestCase):
    def check_document(self, source):
        path = ROOT / "tests" / f".fenced-markdown-{uuid.uuid4().hex}.md"
        try:
            path.write_text(source, encoding="utf-8")
            errors = []
            validator.validate_markdown_file(ROOT, path, errors)
            return errors
        finally:
            if path.exists():
                path.unlink()

    def test_code_fence_contents_are_not_linted_as_markdown(self):
        errors = self.check_document(
            "# Preserved evidence\n\n```text\n"
            "[C:/missing](C:/missing)  \n"
            "```\n"
        )
        self.assertEqual([], errors)

    def test_nested_generated_host_record_and_fenced_record_sample_keep_outer_receipt_link_active(self):
        source_record = ROOT / "evaluations/claude-code/host-acceptance-record-claude-code-2.1.221.md"
        record_lines = source_record.read_text(encoding="utf-8").splitlines()
        evaluated_at = record_lines.index("## Evaluated Combination")
        dimensions_at = record_lines.index("## Dimension Results")
        dimension_end = next(
            index for index in range(dimensions_at + 1, len(record_lines))
            if record_lines[index].startswith("Every dimension is")
        )
        header_fields = record_lines[1:evaluated_at]
        dimension_table = record_lines[dimensions_at:dimension_end]
        host_row = next(index for index, line in enumerate(dimension_table) if line.startswith("| Skill loading and activation |"))
        cells = dimension_table[host_row].split("|")
        cells[-2] = " [nested evidence](missing-nested-run.json)  "
        dimension_table[host_row] = "|".join(cells)

        record_path = ROOT / "tests" / f".fenced-run-receipt-{uuid.uuid4().hex}.json"
        record_path.write_text("{}\n", encoding="utf-8")
        receipt_name = record_path.name
        path = ROOT / "tests" / f".generated-host-record-{uuid.uuid4().hex}.md"
        indented_record = ["    " + line if line else "" for line in header_fields]
        indented_record.extend("    " + line if line else "" for line in dimension_table)
        document = (
            "# Imported cross-host acceptance record\n\n"
            "## Preserved generated record\n\n"
            + "\n".join(indented_record)
            + f"\n\nThe [run receipt](./{receipt_name}) is linked outside the preserved record.\n\n"
            "Generated record.md example:\n\n"
            "```markdown\n"
            "# Host Acceptance Record\n\n"
            "[Scenario source](../../tests/scenarios.md)\n"
            "[Run receipt](./runs/EVAL-example/run.json)\n"
            "```\n"
        )
        try:
            path.write_text(document, encoding="utf-8")
            errors = []
            validator.validate_markdown_file(ROOT, path, errors)
            self.assertEqual([], errors)

            path.write_text(document.replace(f"./{receipt_name}", "./missing-run-receipt.json"), encoding="utf-8")
            errors = []
            validator.validate_markdown_file(ROOT, path, errors)
            self.assertEqual(1, len(errors), errors)
            self.assertIn("broken relative link", errors[0])
            self.assertIn("missing-run-receipt.json", errors[0])
        finally:
            path.unlink(missing_ok=True)
            record_path.unlink(missing_ok=True)

    def test_markdown_outside_code_fence_is_still_linted(self):
        errors = self.check_document(
            "# Preserved evidence\n\n```text\n"
            "[C:/missing](C:/missing)  \n"
            "```\n\n[missing](missing.md)\ntrailing  \n"
        )
        self.assertTrue(any("broken relative link" in error for error in errors))
        self.assertTrue(any("trailing whitespace" in error for error in errors))

    def test_indented_paragraph_continuation_keeps_real_link_and_whitespace_checks(self):
        errors = self.check_document(
            "# Scope\n\nA paragraph continues on the next line:\n"
            "    [required evidence](missing-paragraph-evidence.json)  \n"
        )
        self.assertTrue(any("missing-paragraph-evidence.json" in error for error in errors), errors)
        self.assertTrue(any("trailing whitespace" in error for error in errors), errors)

    def test_indented_list_content_keeps_real_link_checks(self):
        for separator in ("", "\n"):
            with self.subTest(separator=separator):
                errors = self.check_document(
                    "# Scope\n\n- Evidence required:\n" + separator
                    + "    - [run](missing-list-run.json)\n"
                )
                self.assertTrue(any("missing-list-run.json" in error for error in errors), errors)

    def test_standalone_indented_code_preserves_literal_receipt_contents(self):
        errors = self.check_document(
            "# Preserved record\n\n"
            "    [literal evidence](missing-literal.json)  \n"
            "\n    literal trailing whitespace  \n"
            "\nA real [source](../SKILL.md) remains linked.\n"
        )
        self.assertEqual([], errors)

    def test_long_outer_fence_keeps_short_inner_fences_as_literal_text(self):
        errors = self.check_document(
            "# Preserved nested code\n\n````markdown\n"
            "```text\n[literal](missing-inner.md)  \n```\n"
            "````\n\n[real](missing-outer.md)\n"
        )
        self.assertEqual(1, len(errors), errors)
        self.assertIn("missing-outer.md", errors[0])

    def test_short_or_different_fence_marker_cannot_close_outer_fence(self):
        for closer in ("```", "~~~~"):
            with self.subTest(closer=closer):
                errors = self.check_document("# Preserved\n\n````text\nliteral\n" + closer + "\n")
                self.assertTrue(any("unbalanced Markdown code fences" in error for error in errors), errors)

    def test_tilde_fence_preserves_embedded_backticks_and_checks_outer_link(self):
        errors = self.check_document(
            "# Preserved\n\n~~~text\n```\n[literal](missing-inner.md)  \n"
            "~~~~\n\n[real](missing-outer.md)\n"
        )
        self.assertEqual(1, len(errors), errors)
        self.assertIn("missing-outer.md", errors[0])

    def test_whitespace_only_lines_outside_code_are_linted(self):
        for whitespace in ("   ", "\t"):
            with self.subTest(whitespace=whitespace):
                errors = self.check_document(
                    "# Scope\n\n" + whitespace + "\n[real](../SKILL.md)\n"
                )
                self.assertEqual(1, len(errors), errors)
                self.assertIn("trailing whitespace", errors[0])

    def test_whitespace_only_lines_inside_literal_code_are_preserved(self):
        for whitespace in ("   ", "\t"):
            for prefix, suffix in (
                ("```text\n", "\n```\n"),
                ("    literal\n", "\n    more literal\n"),
            ):
                with self.subTest(whitespace=whitespace, prefix=prefix):
                    errors = self.check_document(
                        "# Preserved\n\n" + prefix + whitespace + suffix
                    )
                    self.assertEqual([], errors)

    def test_backtick_info_string_cannot_hide_markdown(self):
        errors = self.check_document(
            "# Scope\n\n```has`backtick\n"
            "[real](missing-invalid-opener.md)  \n```\n"
        )
        self.assertTrue(any("missing-invalid-opener.md" in error for error in errors), errors)
        self.assertTrue(any("trailing whitespace" in error for error in errors), errors)
        self.assertTrue(any("unbalanced Markdown code fences" in error for error in errors), errors)

    def test_tilde_fence_info_can_contain_backticks(self):
        errors = self.check_document(
            "# Preserved\n\n~~~has`backtick\n"
            "[literal](missing-inner.md)  \n~~~\n\n"
            "[real](missing-outer.md)\n"
        )
        self.assertEqual(1, len(errors), errors)
        self.assertIn("missing-outer.md", errors[0])

    def test_list_contained_code_keeps_literal_contents_and_outer_links_separate(self):
        for marker in ("-", "10.", "1)"):
            for extra_indent in (0, 2, 3, 4):
                with self.subTest(marker=marker, extra_indent=extra_indent):
                    content_indent = " " * (len(marker) + 1)
                    code_indent = content_indent + " " * extra_indent
                    errors = self.check_document(
                        "# Scope\n\n" + marker + " Evidence example:\n\n"
                        + code_indent + "```text\n"
                        + code_indent + "[literal](missing-list-literal.json)  \n"
                        + code_indent + "```\n\n"
                        + content_indent + "[real](missing-list-evidence.json)\n"
                    )
                    self.assertEqual(1, len(errors), errors)
                    self.assertIn("missing-list-evidence.json", errors[0])

    def test_nested_list_fence_does_not_hide_outer_evidence(self):
        for marker in ("-", "1."):
            with self.subTest(marker=marker):
                parent_indent = " " * (len(marker) + 1)
                child_indent = parent_indent * 2
                code_indent = child_indent + "  "
                errors = self.check_document(
                    "# Scope\n\n" + marker + " Parent:\n"
                    + parent_indent + marker + " Evidence example:\n\n"
                    + code_indent + "```text\n"
                    + code_indent + "[literal](missing-nested-literal.json)  \n"
                    + code_indent + "```\n\n"
                    + child_indent + "[real](missing-nested-evidence.json)\n"
                )
                self.assertEqual(1, len(errors), errors)
                self.assertIn("missing-nested-evidence.json", errors[0])

    def test_list_marker_can_open_fence_on_same_line(self):
        for marker in ("-", "10."):
            with self.subTest(marker=marker):
                content_indent = " " * (len(marker) + 1)
                errors = self.check_document(
                    "# Scope\n\n" + marker + " ```text\n"
                    + content_indent + "[literal](missing-list-literal.json)  \n"
                    + content_indent + "```\n"
                    + content_indent + "[real](missing-list-evidence.json)\n"
                )
                self.assertEqual(1, len(errors), errors)
                self.assertIn("missing-list-evidence.json", errors[0])

    def test_list_paragraph_continuation_is_still_linted(self):
        for marker in ("-", "10."):
            with self.subTest(marker=marker):
                errors = self.check_document(
                    "# Scope\n\n" + marker + " Required evidence:\n"
                    + " " * (len(marker) + 5)
                    + "[real](missing-list-paragraph.json)  \n"
                )
                self.assertTrue(any("missing-list-paragraph.json" in error for error in errors), errors)
                self.assertTrue(any("trailing whitespace" in error for error in errors), errors)

    def test_empty_list_item_keeps_its_real_content_linted(self):
        for marker in ("-", "+", "*", "1.", "10."):
            with self.subTest(marker=marker):
                errors = self.check_document(
                    "# Scope\n\n" + marker + "\n"
                    + " " * (len(marker) + 3) + "[real](missing-empty-item.json)  \n"
                )
                self.assertEqual(2, len(errors), errors)
                self.assertTrue(any("missing-empty-item.json" in error for error in errors), errors)
                self.assertTrue(any("trailing whitespace" in error for error in errors), errors)
        errors = self.check_document(
            "# Scope\n\n- Parent:\n\n  +\n"
            "      [real](missing-nested-empty-item.json)  \n"
        )
        self.assertEqual(2, len(errors), errors)
        self.assertTrue(any("missing-nested-empty-item.json" in error for error in errors), errors)

    def test_thematic_break_precedes_list_detection(self):
        for separator in ("- - -", "---", "* * *", "___"):
            with self.subTest(separator=separator):
                errors = self.check_document(
                    "# Preserved\n\n" + separator + "\n\n"
                    "    [literal](missing-literal.json)  \n\n"
                    "[real](../SKILL.md)\n"
                )
                self.assertEqual([], errors)

    def test_invalid_list_start_cannot_hide_a_paragraph_continuation(self):
        for prefix, marker in (
            ("A paragraph continues:\n", "10."),
            ("- A paragraph continues:\n  ", "10."),
        ):
            with self.subTest(prefix=prefix, marker=marker):
                errors = self.check_document(
                    "# Scope\n\n" + prefix + marker
                    + "     [real](missing-invalid-list-start.json)  \n"
                )
                self.assertEqual(2, len(errors), errors)
                self.assertTrue(any("missing-invalid-list-start.json" in error for error in errors), errors)
                self.assertTrue(any("trailing whitespace" in error for error in errors), errors)

    def test_blank_line_terminates_an_item_that_started_blank(self):
        for separator in ("\n", "\n\n"):
            with self.subTest(separator=separator):
                errors = self.check_document(
                    "# Preserved\n\n-\n" + separator
                    + "    [literal](missing-terminated-item.json)  \n\n"
                    "[real](../SKILL.md)\n"
                )
                self.assertEqual([], errors)

    def test_blank_start_item_can_contain_literal_code(self):
        for marker in ("-", "1."):
            with self.subTest(marker=marker):
                content_indent = " " * (len(marker) + 1)
                errors = self.check_document(
                    "# Preserved\n\n" + marker + "\n"
                    + content_indent + "    [literal](missing-blank-start-code.json)  \n\n"
                    + content_indent + "[real](missing-blank-start-evidence.json)\n"
                )
                self.assertEqual(1, len(errors), errors)
                self.assertIn("missing-blank-start-evidence.json", errors[0])

    def test_bullet_item_starting_with_code_can_interrupt_a_paragraph(self):
        errors = self.check_document(
            "# Preserved\n\nA paragraph continues:\n"
            "-     [literal](missing-bullet-code.json)  \n\n"
            "  [real](missing-bullet-evidence.json)\n"
        )
        self.assertEqual(1, len(errors), errors)
        self.assertIn("missing-bullet-evidence.json", errors[0])

    def test_ordered_sibling_item_can_start_with_literal_code(self):
        for prefix, item_indent in (("", ""), ("- Parent:\n\n", "  ")):
            with self.subTest(prefix=prefix):
                errors = self.check_document(
                    "# Preserved\n\n" + prefix
                    + item_indent + "1. First item\n"
                    + item_indent + "2.     [literal](missing-sibling-code.json)  \n\n"
                    + item_indent + "   [real](missing-sibling-evidence.json)\n"
                )
                self.assertEqual(1, len(errors), errors)
                self.assertIn("missing-sibling-evidence.json", errors[0])

    def test_lazy_paragraph_continuation_keeps_its_list_container(self):
        for prefix, content_indent in (
            ("- Required evidence:\n", "    "),
            ("- Parent:\n  - Required evidence:\n", "      "),
        ):
            with self.subTest(prefix=prefix):
                errors = self.check_document(
                    "# Scope\n\n" + prefix + "lazy continuation\n\n"
                    + content_indent + "[real](missing-lazy-list-evidence.json)  \n"
                )
                self.assertEqual(2, len(errors), errors)
                self.assertTrue(any("missing-lazy-list-evidence.json" in error for error in errors), errors)
                self.assertTrue(any("trailing whitespace" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
