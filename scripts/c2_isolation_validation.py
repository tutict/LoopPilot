#!/usr/bin/env python3
"""Check an installed LoopPilot Skill directory for acceptance-corpus material.

Phase 15 control C2 requires that no evaluation record, rubric, checklist,
acceptance document, or project memory index be reachable from a fixture
context. The installed Skill directory is reachable from every fixture context
by construction, because that is how ``SKILL.md`` resolves its relative
references, so that directory has to satisfy C2 exactly as the sandbox does.

This module verifies the property directly. Three consequences are deliberate:

* **It never reads ``.looppilot-installation``.** Every acceptance file became
  unmanaged when the payload manifest narrowed, and a managed-set computation
  cannot see an unmanaged file. ``status`` reporting ``CURRENT`` is therefore
  not a sufficient condition for C2 isolation; this check supplies the missing
  half rather than restating the existing one.
* **It matches path suffixes, not destination-relative paths.** A backed-up
  file lives at ``.looppilot-backups/<operation-id>/<original path>``, so a
  prohibited path appears below a backup root rather than at the tree root. A
  check comparing destination-relative paths for equality would enumerate a
  whole backed-up corpus and report nothing. Suffixes are generated to any
  depth, because a snapshot can itself contain a snapshot.
* **It asks what the tree contains, never how the tree was produced.** Any
  install, reinstall, or upgrade path is admissible when its result passes, and
  none is admissible because of its name.

The check reports; it decides nothing. A clean result is not Host Acceptance
evidence, does not score an acceptance dimension, and does not tick a gate.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

C2_ISOLATION_FILES = (
    "scripts/c2_isolation_validation.py",
    "tests/test_c2_isolation.py",
)

# Trees the official payload deliberately stops distributing. Kept identical to
# ``ACCEPTANCE_PREFIXES`` in ``tests/test_distribution.py``, which asserts the
# same corpus against the manifest; ``test_c2_isolation`` fails if they drift.
ACCEPTANCE_PREFIXES = (
    "evaluations/",
    "tests/",
    "scripts/",
    "docs/release/",
    "docs/evaluations/",
)
ACCEPTANCE_FILES = ("docs/cross-host-acceptance.md",)

# A project memory index is named by C2 alongside the acceptance artifacts, and
# is identified by filename because that is how a host discovers one.
MEMORY_INDEX_NAMES = ("CLAUDE.md", "MEMORY.md")

# Real records title themselves ``# Host Acceptance Record: <combination>``, so
# the heading is matched by prefix. This is a content check because C2 prohibits
# a prior record at *any* path, and a record moved out of ``evaluations/`` would
# defeat path matching alone.
RECORD_HEADING_PREFIX = "# Host Acceptance Record"

BACKUP_DIRECTORY = ".looppilot-backups"
STATE_FILE = ".looppilot-installation"

CLEAN_STATE = "C2_CLEAN"
CONTAMINATED_STATE = "C2_CONTAMINATED"


def _relative_paths(destination: Path) -> list[str]:
    """Enumerate every regular file under ``destination`` as a POSIX path.

    Hidden directories are included, symbolic links are never traversed, and no
    installation state is consulted. The walk is the whole point of the check:
    it is the difference between inspecting a tree and inspecting a manifest.
    """
    found: list[str] = []
    for parent, directories, files in os.walk(destination, followlinks=False):
        directories[:] = [
            name
            for name in directories
            if not (Path(parent) / name).is_symlink()
        ]
        for name in files:
            path = Path(parent) / name
            if path.is_symlink() or not path.is_file():
                continue
            found.append(path.relative_to(destination).as_posix())
    return sorted(found)


def _path_suffixes(relative: str) -> list[str]:
    """Return the segment-aligned suffixes of a relative POSIX path.

    ``a/b/c`` yields ``a/b/c``, ``b/c``, and ``c``. Generating every suffix is
    what lets a prohibited path be recognised at an arbitrary nesting depth,
    which is the shape backups and nested snapshots produce.
    """
    segments = relative.split("/")
    return ["/".join(segments[index:]) for index in range(len(segments))]


def _corpus_rule(relative: str) -> str | None:
    """Return the prohibited corpus entry this path matches, if any."""
    for suffix in _path_suffixes(relative):
        if suffix in ACCEPTANCE_FILES:
            return suffix
        for prefix in ACCEPTANCE_PREFIXES:
            if suffix.startswith(prefix):
                return prefix
    return None


def _declares_host_acceptance_record(path: Path) -> bool:
    """Report whether a Markdown file titles itself a Host Acceptance Record."""
    if path.suffix.lower() != ".md":
        return False
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return any(
        line.strip().startswith(RECORD_HEADING_PREFIX)
        for line in text.splitlines()
    )


def validate_c2_isolation(destination: Path) -> list[str]:
    """Return one ``rule|path`` finding per C2 violation in an installed tree.

    An empty list means the tree satisfies C2 by enumeration. It means nothing
    about whether the installation is synchronised with its source, which is a
    separate and independent property that ``status`` reports.
    """
    findings: list[str] = []
    for relative in _relative_paths(destination):
        rule = _corpus_rule(relative)
        if rule is not None:
            findings.append(f"acceptance-corpus:{rule}|{relative}")
            continue
        if Path(relative).name in MEMORY_INDEX_NAMES:
            findings.append(f"memory-index:{Path(relative).name}|{relative}")
            continue
        if _declares_host_acceptance_record(destination / relative):
            findings.append(f"host-acceptance-record|{relative}")
    return findings


def _report(destination: Path, findings: list[str]) -> list[str]:
    """Build the deterministic report lines for one destination."""
    enumerated = _relative_paths(destination)
    backups = [
        path
        for path in enumerated
        if BACKUP_DIRECTORY in path.split("/")
    ]
    state = CONTAMINATED_STATE if findings else CLEAN_STATE
    lines = [
        f"Destination: {destination}",
        f"Files enumerated: {len(enumerated)}",
        f"Files under {BACKUP_DIRECTORY}/: {len(backups)}",
        f"Installation state read: no ({STATE_FILE} not consulted)",
        f"State: {state}",
        f"Findings: {len(findings)}",
    ]
    lines.extend(findings)
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that an installed LoopPilot Skill directory carries no "
            "acceptance corpus. Reports a property of the tree; it does not "
            "check how the tree was installed, and it is not a synchronisation "
            "check."
        )
    )
    parser.add_argument(
        "--destination",
        required=True,
        type=Path,
        help="Installed Skill directory to enumerate.",
    )
    arguments = parser.parse_args(argv)

    destination = arguments.destination
    if not destination.is_dir():
        print(f"error: destination is not a directory: {destination}")
        return 2

    findings = validate_c2_isolation(destination)
    for line in _report(destination, findings):
        print(line)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
