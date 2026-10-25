"""Maintenance-only native shell selection and owned temporary resources."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
import tempfile
import subprocess
from functools import lru_cache


def selected_shell(variable: str, discovered: str | None) -> str | None:
    if variable not in os.environ:
        return discovered
    selected = Path(os.environ[variable])
    if not selected.is_absolute() or not selected.is_file() or not os.access(selected, os.X_OK):
        raise RuntimeError(f"{variable} must name an existing absolute executable path")
    return str(selected.resolve())


def require_shells(powershell: str | None, bash: str | None) -> None:
    setting = os.environ.get("LOOPPILOT_TEST_REQUIRE_SHELLS", "0")
    if setting not in {"0", "1"}:
        raise RuntimeError("LOOPPILOT_TEST_REQUIRE_SHELLS must be 0 or 1")
    if setting == "1" and (not powershell or not bash):
        raise RuntimeError("Both PowerShell and Bash are required for this installation test job")


@lru_cache
def bash_shebang(executable: str) -> str:
    result = subprocess.run([executable, "-c", 'printf "%s" "$BASH"'],
                            capture_output=True, text=True, check=True)
    interpreter = result.stdout
    if not interpreter.startswith("/") or any(c.isspace() for c in interpreter):
        raise RuntimeError("Selected Bash must expose an absolute POSIX interpreter path for injection scripts")
    return "#!" + interpreter + "\n"


def installer_environment() -> dict[str, str]:
    # A child shell must discover modules for its own edition/version instead of
    # inheriting PowerShell 7's module path when Windows PowerShell 5 is selected.
    return {key: value for key, value in os.environ.items() if key.upper() != "PSMODULEPATH"}


def new_workspace(prefix: str, source_root: Path) -> Path:
    parent = Path(tempfile.gettempdir()).resolve()
    if parent.is_relative_to(source_root.resolve()):
        raise RuntimeError("Installation test temporary parent must be outside the source checkout")
    return Path(tempfile.mkdtemp(prefix=prefix, dir=parent)).resolve()


def cleanup_workspace(root: Path, parent: Path, prefix: str) -> None:
    # The caller captures the newly allocated root, not mutable fixture state.
    if not root.exists() and not root.is_symlink():
        return
    resolved = root.resolve()
    attributes = getattr(root.lstat(), "st_file_attributes", 0)
    if (root.is_symlink() or attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
            or resolved != root.absolute() or resolved.parent != parent.resolve()
            or not resolved.name.startswith(prefix)):
        raise RuntimeError("Refused cleanup outside the owned installation test workspace")

    def remove_readonly(function, path, error):
        target = Path(path)
        if not target.resolve().is_relative_to(resolved) or not isinstance(error, PermissionError):
            raise error
        target.chmod(stat.S_IWRITE | stat.S_IREAD)
        function(path)

    shutil.rmtree(resolved, onexc=remove_readonly)
