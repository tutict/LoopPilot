"""Finite manifest-to-guide consistency; no installer behavior changes."""
from pathlib import Path, PurePosixPath
import re

GENERATED = {".looppilot-installation", ".looppilot-transaction", ".looppilot-backups/"}


def manifest_display_entries(root: Path) -> set[str]:
    entries = set()
    for line in (root / "distribution/managed-files.txt").read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        path = PurePosixPath(entry)
        if path.is_absolute() or ".." in path.parts or "\\" in entry:
            raise ValueError("invalid managed manifest path")
        if path.parts[0] in {"docs", "distribution"}:
            entries.add(path.parts[0] + "/")
        else:
            entries.add(entry)
    return entries


def validate_installation_documentation(root: Path) -> list[str]:
    try:
        text = (root / "docs/installation.md").read_text(encoding="utf-8")
        match = re.findall(r"<!-- managed-layout:start -->\s*```text\n(.*?)```\s*<!-- managed-layout:end -->", text, re.S)
        if len(match) != 1:
            return ["installation guide requires one managed-layout block"]
        actual, generated = set(), set()
        for line in match[0].splitlines():
            if line == "<destination>/":
                continue
            if not line.startswith(("|-- ", "`-- ")):
                return ["invalid installation guide tree row"]
            row = line[4:]
            if "       generated" in row:
                entry = row.split("       generated", 1)[0]
                if entry not in GENERATED or entry in generated:
                    return ["invalid generated installation entry"]
                generated.add(entry)
            else:
                for entry in row.split(" / "):
                    if entry in actual:
                        return ["duplicate installation guide managed entry"]
                    actual.add(entry)
        expected = manifest_display_entries(root)
        if actual != expected:
            return [f"installation guide/manifest mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}"]
        if generated != GENERATED:
            return ["installation guide generated receipt entries incomplete"]
        return []
    except (OSError, UnicodeError, ValueError) as error:
        return [f"installation documentation: {error}"]
