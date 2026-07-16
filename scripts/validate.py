#!/usr/bin/env python3
"""Run deterministic maintenance checks for the LoopPilot repository."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from yaml.constructor import ConstructorError


REQUIRED_FILES = (
    "SKILL.md",
    "AGENTS.md",
    ".looppilot/README.md",
    ".looppilot/STATE.md",
    ".looppilot/HANDOFF.md",
    ".looppilot/DECISIONS.md",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "agents/openai.yaml",
    ".github/workflows/validate.yml",
    "requirements-dev.txt",
    "scripts/validate.py",
    "docs/validation.md",
    "evaluations/README.md",
    "docs/host-capabilities.md",
    "evaluations/codex/README.md",
    "evaluations/templates/environment.md",
    "evaluations/templates/prompt.md",
    "evaluations/templates/trace.md",
    "evaluations/templates/score.md",
    "docs/lifecycle.md",
    "docs/safety-and-stopping.md",
    "tests/evaluation-rubric.md",
    "tests/scenarios.md",
)
SKILL_WORD_RANGE = range(1500, 2501)
FRONTMATTER_PATTERN = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
MERMAID_PATTERN = re.compile(
    r"^```mermaid[ \t]*\r?\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL
)
UPDATED_PATTERN = re.compile(
    r"^Updated:[ \t]*(?:YYYY-MM-DD|\d{4}-\d{2}-\d{2})[ \t]*$", re.MULTILINE
)
STATUS_PATTERN = re.compile(r"^Status:[ \t]*(\S+)[ \t]*$", re.MULTILINE)
CREDENTIAL_ASSIGNMENT_PATTERN = re.compile(
    r"^[ \t]*(?:[a-z][a-z0-9_]*_)?(?:api[_ -]?key|access[_ -]?token|token|"
    r"secret|password|cookie|credential)[ \t]*[:=][ \t]*"
    r"(?!none(?:\s|$)|redacted(?:\s|$)|placeholder(?:\s|$)|<)[^\s`]+",
    re.IGNORECASE | re.MULTILINE,
)
STATE_STATUSES = {
    "inactive",
    "active",
    "partially-completed",
    "blocked",
    "completed",
    "budget-stopped",
    "cancelled",
}
HANDOFF_STATUSES = {"none", "active", "completed", "superseded"}
SHARED_STATE_HEADINGS = {
    ".looppilot/README.md": (
        "## Purpose",
        "## It Is Not",
        "## When to Create or Update",
        "## Source of Truth",
        "## Status Values",
        "## Native Plan Relationship",
        "## Evidence and Update Discipline",
        "## File Responsibilities",
    ),
    ".looppilot/STATE.md": (
        "## Objective",
        "## Success Criteria",
        "## Current Progress",
        "## Verified Evidence",
        "## Blockers",
        "## Native Plan Relationship",
        "## Next Action",
    ),
    ".looppilot/HANDOFF.md": (
        "## Current Objective",
        "## Completed",
        "## Observed Evidence",
        "## Remaining Work",
        "## Blockers",
        "## Risks and Constraints",
        "## Recommended Next Action",
        "## Do Not Assume",
    ),
    ".looppilot/DECISIONS.md": (
        "## Active Decisions",
        "## Superseded Decisions",
    ),
}


class UniqueKeySafeLoader(yaml.SafeLoader):
    """SafeLoader variant that rejects duplicate mapping keys."""


def construct_unique_mapping(
    loader: UniqueKeySafeLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[object, object]:
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping
)


@dataclass(frozen=True)
class MermaidBlock:
    source: Path
    number: int
    content: str

    @property
    def filename(self) -> str:
        stem = "-".join(self.source.with_suffix("").parts)
        return f"{stem}-{self.number}.mmd"


def parse_yaml_mapping(path: Path, text: str) -> dict[object, object]:
    """Parse YAML safely, reject duplicate keys, and require a mapping root."""
    data = yaml.safe_load(text)
    yaml.load(text, Loader=UniqueKeySafeLoader)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    return data


def non_empty_string(mapping: dict[object, object], key: str, location: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location}: {key!r} must be a non-empty string")
    return value


def validate_skill_frontmatter(root: Path, errors: list[str]) -> None:
    path = root / "SKILL.md"
    match = FRONTMATTER_PATTERN.match(path.read_text(encoding="utf-8"))
    if not match:
        errors.append("SKILL.md: missing or malformed YAML frontmatter")
        return
    try:
        metadata = parse_yaml_mapping(path, match.group(1))
        if set(metadata) != {"name", "description"}:
            raise ValueError("SKILL.md frontmatter: only name and description are allowed")
        name = non_empty_string(metadata, "name", "SKILL.md frontmatter")
        non_empty_string(metadata, "description", "SKILL.md frontmatter")
        if name != "loop-pilot":
            raise ValueError("SKILL.md frontmatter: name must be 'loop-pilot'")
    except (ConstructorError, ValueError, yaml.YAMLError) as error:
        errors.append(str(error))


def validate_openai_yaml(root: Path, errors: list[str]) -> None:
    path = root / "agents" / "openai.yaml"
    try:
        data = parse_yaml_mapping(path, path.read_text(encoding="utf-8"))
        if set(data) != {"interface"}:
            raise ValueError("agents/openai.yaml: only 'interface' is expected")
        interface = data.get("interface")
        if not isinstance(interface, dict):
            raise ValueError("agents/openai.yaml: 'interface' must be a mapping")
        if set(interface) != {"display_name", "short_description", "default_prompt"}:
            raise ValueError("agents/openai.yaml: unexpected or missing interface field")
        non_empty_string(interface, "display_name", "agents/openai.yaml interface")
        description = non_empty_string(
            interface, "short_description", "agents/openai.yaml interface"
        )
        prompt = non_empty_string(
            interface, "default_prompt", "agents/openai.yaml interface"
        )
        if not 25 <= len(description) <= 64:
            raise ValueError("agents/openai.yaml: short_description must be 25-64 characters")
        if "$loop-pilot" not in prompt:
            raise ValueError("agents/openai.yaml: default_prompt must mention $loop-pilot")
    except (ConstructorError, ValueError, yaml.YAMLError) as error:
        errors.append(str(error))


def validate_yaml_files(root: Path, errors: list[str]) -> None:
    paths = sorted((*root.rglob("*.yaml"), *root.rglob("*.yml")))
    for path in paths:
        try:
            parse_yaml_mapping(path, path.read_text(encoding="utf-8"))
        except (ConstructorError, ValueError, yaml.YAMLError) as error:
            errors.append(str(error))


def validate_status(
    root: Path, relative: Path, allowed: set[str], errors: list[str]
) -> str | None:
    text = (root / relative).read_text(encoding="utf-8")
    match = STATUS_PATTERN.search(text)
    if not match:
        errors.append(f"{relative.as_posix()}: missing Status field")
        return None
    status = match.group(1)
    if status not in allowed:
        errors.append(f"{relative.as_posix()}: invalid Status {status!r}")
    return status


def validate_shared_state(root: Path, errors: list[str]) -> None:
    state_path = Path(".looppilot/STATE.md")
    state_status = validate_status(
        root, state_path, STATE_STATUSES, errors
    )
    state_text = (root / state_path).read_text(encoding="utf-8")
    if state_status in STATE_STATUSES - {"inactive"} and any(
        marker in state_text
        for marker in ("Updated: YYYY-MM-DD", "Updated by: none", "No active shared task.")
    ):
        errors.append(
            f"{state_path.as_posix()}: template placeholders cannot declare "
            f"Status {state_status!r}"
        )

    handoff_path = Path(".looppilot/HANDOFF.md")
    handoff_status = validate_status(
        root, handoff_path, HANDOFF_STATUSES, errors
    )
    handoff_text = (root / handoff_path).read_text(encoding="utf-8")
    if handoff_status in HANDOFF_STATUSES - {"none"} and any(
        marker in handoff_text
        for marker in ("Updated: YYYY-MM-DD", "From: none", "No active handoff.")
    ):
        errors.append(
            f"{handoff_path.as_posix()}: template placeholders cannot declare "
            f"Status {handoff_status!r}"
        )

    decisions_path = Path(".looppilot/DECISIONS.md")
    for relative in (state_path, handoff_path, decisions_path):
        text = (root / relative).read_text(encoding="utf-8")
        if not UPDATED_PATTERN.search(text):
            errors.append(
                f"{relative.as_posix()}: missing or invalid Updated field"
            )

    updater_patterns = {
        state_path: re.compile(r"^Updated by:[ \t]*\S+", re.MULTILINE),
        handoff_path: re.compile(r"^From:[ \t]*\S+", re.MULTILINE),
        decisions_path: re.compile(r"^Updated by:[ \t]*\S+", re.MULTILINE),
    }
    for relative, pattern in updater_patterns.items():
        text = (root / relative).read_text(encoding="utf-8")
        if not pattern.search(text):
            errors.append(f"{relative.as_posix()}: missing updater identifier")

    for relative_text, headings in SHARED_STATE_HEADINGS.items():
        relative = Path(relative_text)
        text = (root / relative).read_text(encoding="utf-8")
        if CREDENTIAL_ASSIGNMENT_PATTERN.search(text):
            errors.append(
                f"{relative.as_posix()}: possible credential assignment in shared state"
            )
        lines = set(text.splitlines())
        for heading in headings:
            if heading not in lines:
                errors.append(
                    f"{relative.as_posix()}: missing required heading {heading!r}"
                )


def markdown_files(root: Path) -> list[Path]:
    ignored = {".git", ".venv", "node_modules", "__pycache__"}
    return sorted(
        path
        for path in root.rglob("*.md")
        if not any(part in ignored for part in path.relative_to(root).parts)
    )


def validate_markdown_file(root: Path, path: Path, errors: list[str]) -> None:
    relative = path.relative_to(root)
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    if not raw.endswith(b"\n"):
        errors.append(f"{relative}: file must end with a newline")
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.endswith((" ", "\t")):
            errors.append(f"{relative}:{line_number}: trailing whitespace")
    fence_count = sum(1 for line in text.splitlines() if line.lstrip().startswith("```"))
    if fence_count % 2:
        errors.append(f"{relative}: unbalanced Markdown code fences")
    for match in LINK_PATTERN.finditer(text):
        raw_target = match.group(1).strip()
        if raw_target.startswith("<") and raw_target.endswith(">"):
            raw_target = raw_target[1:-1]
        target = raw_target.split(maxsplit=1)[0]
        parsed = urlsplit(target)
        if parsed.scheme or target.startswith(("#", "//")):
            continue
        link_path = unquote(parsed.path)
        if not link_path:
            continue
        resolved = (path.parent / link_path).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{relative}: relative link escapes repository: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{relative}: broken relative link: {target}")


def collect_mermaid_blocks(root: Path, files: list[Path]) -> list[MermaidBlock]:
    blocks: list[MermaidBlock] = []
    for path in files:
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        for number, match in enumerate(MERMAID_PATTERN.finditer(text), start=1):
            blocks.append(MermaidBlock(relative, number, match.group(1).rstrip() + "\n"))
    return blocks


def extract_mermaid(blocks: list[MermaidBlock], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for block in blocks:
        (output / block.filename).write_text(block.content, encoding="utf-8", newline="\n")


def validate_repository(root: Path, extract_directory: Path | None = None) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")
    if errors:
        return errors

    validate_shared_state(root, errors)
    validate_yaml_files(root, errors)
    validate_skill_frontmatter(root, errors)
    validate_openai_yaml(root, errors)

    files = markdown_files(root)
    for path in files:
        validate_markdown_file(root, path, errors)

    skill_words = len((root / "SKILL.md").read_text(encoding="utf-8").split())
    if skill_words not in SKILL_WORD_RANGE:
        errors.append(
            f"SKILL.md: expected 1500-2500 words, observed {skill_words}"
        )

    blocks = collect_mermaid_blocks(root, files)
    sources = {block.source.as_posix() for block in blocks}
    for required_source in ("README.md", "docs/lifecycle.md"):
        if required_source not in sources:
            errors.append(f"{required_source}: expected at least one Mermaid block")
    if extract_directory is not None and not errors:
        extract_mermaid(blocks, extract_directory.resolve())
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (defaults to the parent of scripts/)",
    )
    parser.add_argument(
        "--extract-mermaid",
        type=Path,
        help="write extracted Mermaid sources to this directory after validation",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        errors = validate_repository(args.root, args.extract_mermaid)
    except (OSError, UnicodeError) as error:
        errors = [str(error)]
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Static validation passed")
    if args.extract_mermaid is not None:
        print(f"Mermaid sources written to {args.extract_mermaid.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
