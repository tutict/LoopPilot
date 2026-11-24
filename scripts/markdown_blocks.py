"""Bounded literal-code boundaries shared by maintenance validators."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CodeBlockScan:
    code_lines: frozenset[int]
    unclosed_fence: bool


def scan_code_blocks(lines: list[str]) -> CodeBlockScan:
    """Return zero-based literal-code lines and the fence-balance result."""
    code_lines: set[int] = set()
    fence_marker = None
    fence_length = 0
    fence_content_indent = 0
    indented_code_indent = None
    in_paragraph = False
    list_items = []  # Content column, marker column, marker kind.
    empty_item_indent = None
    for index, line in enumerate(lines):
        expanded_line = line.expandtabs(4)
        indentation = len(expanded_line) - len(expanded_line.lstrip(" "))
        if fence_marker is not None:
            fence = re.match(
                r"^ {0,3}(`{3,}|~{3,})(.*)$", expanded_line[fence_content_indent:]
            ) if indentation >= fence_content_indent else None
            if fence is not None:
                marker = fence.group(1)
                suffix = fence.group(2)
                if marker[0] == fence_marker and len(marker) >= fence_length and not suffix.strip():
                    fence_marker = None
                    fence_length = 0
                    in_paragraph = False
            code_lines.add(index)
            continue
        if indented_code_indent is not None and (
            not line.strip() or indentation >= indented_code_indent
        ):
            code_lines.add(index)
            continue
        indented_code_indent = None
        if not line.strip():
            # The marker line already counts as an empty item's first blank
            # line. A second blank line terminates that item.
            if empty_item_indent is not None:
                list_items.pop()
                empty_item_indent = None
            in_paragraph = False
            continue

        empty_item_indent = None
        # Code indentation is relative to the current list item's content column.
        # Keep parent columns so a nested item can return to its outer content.
        remaining_items = len(list_items)
        while remaining_items and indentation < list_items[remaining_items - 1][0]:
            remaining_items -= 1
        content_indent = list_items[remaining_items - 1][0] if remaining_items else 0
        content_line = expanded_line[content_indent:]
        thematic_break = re.match(
            r"^ {0,3}(?:(?:\* *){3,}|(?:- *){3,}|(?:_ *){3,})$", content_line
        )
        list_marker = None if thematic_break else re.match(
            r"^( {0,3})([-+*]|\d{1,9}[.)])(?:( +)|$)", content_line
        )
        if list_marker is not None:
            padding = len(list_marker.group(3) or "")
            marker = list_marker.group(2)
            offset = len(list_marker.group(1)) + len(marker) + (
                padding if 0 < padding <= 4 and content_line[list_marker.end():].strip() else 1
            )
            item_content = content_line[offset:]
            marker_indent = content_indent + len(list_marker.group(1))
            sibling_item = remaining_items < len(list_items) and (
                list_items[remaining_items][1:] == (marker_indent, marker[-1])
            )
            # Only a new list must satisfy paragraph-interruption rules;
            # subsequent items in an existing ordered list may start above 1.
            invalid_paragraph_interrupt = in_paragraph and not sibling_item and (
                not item_content.strip()
                or (marker[0].isdigit() and int(marker[:-1]) != 1)
            )
            if invalid_paragraph_interrupt:
                list_marker = None

        block_fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", content_line)
        paragraph_break = thematic_break or re.match(
            r"^ {0,3}(?:#{1,6}(?:\s|$)|[-=]+ *$|>)", content_line
        ) or (block_fence is not None and (
            block_fence.group(1)[0] != "`" or "`" not in block_fence.group(2)
        ))
        if (
            remaining_items < len(list_items) and in_paragraph
            and list_marker is None and not paragraph_break
        ):
            # A lazy paragraph continuation keeps its list container even
            # when the author omits that container's indentation.
            content_indent = list_items[-1][0]
            content_line = expanded_line
        else:
            del list_items[remaining_items:]
        if list_marker is not None:
            content_indent += offset
            list_items.append((content_indent, marker_indent, marker[-1]))
            content_line = item_content
            empty_item_indent = content_indent if not content_line.strip() else None
            in_paragraph = False
        fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", content_line)
        if fence is not None and (
            fence.group(1)[0] != "`" or "`" not in fence.group(2)
        ):
            fence_marker = fence.group(1)[0]
            fence_length = len(fence.group(1))
            fence_content_indent = content_indent
            in_paragraph = False
            code_lines.add(index)
            continue
        # Extra indentation cannot turn a paragraph continuation into code.
        content_indentation = len(content_line) - len(content_line.lstrip(" "))
        if content_indentation >= 4 and not in_paragraph:
            indented_code_indent = content_indent + 4
            code_lines.add(index)
            continue
        in_paragraph = bool(content_line.strip()) and re.match(
            r"^ {0,3}(?:#{1,6}(?:\s|$)|(?:\* *){3,}$|(?:- *){3,}$|(?:_ *){3,}$|=+ *$)",
            content_line
        ) is None
    return CodeBlockScan(frozenset(code_lines), fence_marker is not None)
