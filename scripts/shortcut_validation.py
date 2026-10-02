"""Maintenance-only alias binding check; not a host command resolver or runtime."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path


def resolve_installed_shortcut(alias: Path, *, long_command: Path) -> Path:
    """Return the one canonical file, or reject an unbound/customized alias.

    This models the filesystem part of the written alias contract. The caller
    must separately verify that the host selects this installation for the long
    command. It cannot establish host discovery, permissions or acceptance.
    """
    alias = Path(alias).absolute()
    if alias.parts[-3:] != ("shortcuts", "lp", "SKILL.md"):
        raise ValueError("alias is not in the managed installed layout")
    root = alias.parents[2]
    canonical = root / "SKILL.md"
    state = root / ".looppilot-installation"
    if (root / ".git").exists() or not state.is_file():
        raise ValueError("repository or missing installation identity")
    for path in (alias, canonical, state, alias.parent, alias.parent.parent, root):
        if path.is_symlink() or path.is_junction():
            raise ValueError("indirect installation paths are not accepted")
    if canonical.resolve() != Path(long_command).resolve():
        raise ValueError("short and long commands select different canonical sources")
    metadata: dict[str, str] = {}
    files: dict[str, list[str]] = {}
    provenance_seen = False
    for row in state.read_text(encoding="utf-8-sig").splitlines():
        fields = row.split("|")
        if fields[0] == "PROVENANCE":
            if (provenance_seen or len(fields) != 4 or fields[1] not in {"git-release", "archive"}
                    or not all(re.fullmatch(r"[0-9a-f]{64}", value) for value in fields[2:])):
                raise ValueError("malformed installation provenance")
            provenance_seen = True
        elif fields[0] == "FILE":
            if len(fields) != 5 or fields[1] in files:
                raise ValueError("ambiguous or malformed installation identity")
            files[fields[1]] = fields
        else:
            if len(fields) != 2 or fields[0] in metadata:
                raise ValueError("ambiguous or malformed installation metadata")
            metadata[fields[0]] = fields[1]
    if (set(metadata) != {"FORMAT", "VERSION", "COMMIT", "MANIFEST"}
            or metadata["FORMAT"] != "2"
            or not metadata["VERSION"]
            or not re.fullmatch(r"[0-9a-f]{40}", metadata["COMMIT"])
            or not re.fullmatch(r"[0-9a-f]{64}", metadata["MANIFEST"])):
        raise ValueError("missing or malformed installation metadata")
    for relative in ("SKILL.md", "shortcuts/lp/SKILL.md"):
        fields = files.get(relative)
        path = root / relative
        if not fields or not path.is_file() or fields[3] != "0":
            raise ValueError("missing or customized canonical source")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if fields[2] != digest or fields[4] != digest:
            raise ValueError("inconsistent installed content digest")
    return canonical.resolve()
