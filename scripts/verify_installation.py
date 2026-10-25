#!/usr/bin/env python3
"""Maintenance-only platform installation evidence; never Host Acceptance."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULES = (
    "test_distribution", "test_repair_v2", "test_architecture_repair",
    "test_git_replacement_provenance", "test_c2_isolation",
    "test_installation_doc_consistency", "test_installer_portability", "test_installation_runner",
)


def run(command, env=None, cwd=ROOT):
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"Command exited {result.returncode}: {command}\n"
                           + result.stdout.decode("utf-8", errors="replace")
                           + result.stderr.decode("utf-8", errors="replace"))
    return result.stdout


def shell_info(path, powershell, output):
    args = [path, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"] if powershell else [path, "--version"]
    label = "powershell" if powershell else "bash"
    result = subprocess.run(args, cwd=ROOT, capture_output=True)
    for stream, content in (("stdout", result.stdout), ("stderr", result.stderr)):
        (output / f"{label}-version.{stream}.log").write_bytes(content)
    if result.returncode:
        raise RuntimeError(f"{label} version probe exited {result.returncode}: {path}")
    return {"path": path, "version": result.stdout.decode("utf-8", errors="replace").strip(),
            "exit_code": result.returncode}


def smoke(output, commit):
    from installer_test_support import cleanup_workspace, installer_environment, new_workspace
    from test_distribution import BASH, POWERSHELL, _expand_official_manifest, _posix_path

    env = installer_environment()
    # The maintenance observer prints the Unicode destination in its raw log.
    # Keep that child stream independent of Windows' legacy console code page.
    env["PYTHONIOENCODING"] = "utf-8"
    payload = sorted(_expand_official_manifest())
    assert {"README.md", "README.zh-CN.md"}.issubset(payload)
    blobs = {p: run(["git", "--no-replace-objects", "show", f"{commit}:{p}"]) for p in payload}
    hashes = {p: hashlib.sha256(b).hexdigest() for p, b in blobs.items()}
    digest = hashlib.sha256("".join(f"{p}|{hashes[p]}\n" for p in payload).encode("utf-8")).hexdigest()
    results = []
    work = new_workspace("lp-smoke-", ROOT)
    try:
        for shell, executable in (("powershell", POWERSHELL), ("bash", BASH)):
            dest = work / (shell + " install \u5b89\u88c5")
            dest.mkdir()
            sentinel = dest / "user.txt"
            sentinel.write_bytes(b"user-owned content\n")
            before_update = None
            for operation in ("install", "status", "update", "uninstall"):
                if shell == "powershell":
                    command = [executable, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                               str(ROOT / (operation + ".ps1")), "-Destination", str(dest)]
                else:
                    command = [executable, _posix_path(ROOT / (operation + ".sh")), "--destination", _posix_path(dest)]
                result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True)
                for stream, data in (("stdout", result.stdout), ("stderr", result.stderr)):
                    (output / f"{shell}-{operation}.{stream}.log").write_bytes(data)
                with (output / "commands.jsonl").open("a", encoding="utf-8") as journal:
                    journal.write(json.dumps({"observed_at": datetime.now(timezone.utc).isoformat(),
                                              "shell": shell, "operation": operation,
                                              "command": command, "cwd": str(ROOT),
                                              "exit_code": result.returncode}, ensure_ascii=True) + "\n")
                assert result.returncode == 0, (command, result.stdout, result.stderr)
                assert sentinel.read_bytes() == b"user-owned content\n"
                if operation == "uninstall":
                    assert not (dest / ".looppilot-installation").exists()
                    assert all(not (dest / p).exists() for p in payload)
                    continue
                for p in payload:
                    assert (dest / p).read_bytes() == blobs[p], (shell, operation, p)
                receipt = (dest / ".looppilot-installation").read_bytes()
                rows = receipt.decode("utf-8-sig").splitlines()
                assert f"COMMIT|{commit}" in rows
                assert f"PROVENANCE|git-release|{digest}|{digest}" in rows
                file_rows = [r.split("|") for r in rows if r.startswith("FILE|")]
                assert len(file_rows) == len(payload) and {r[1] for r in file_rows} == set(payload)
                assert all(r[2:] == [hashes[r[1]], "0", hashes[r[1]]] for r in file_rows)
                (output / f"{shell}-{operation}.receipt.txt").write_bytes(receipt)
                if operation in {"status", "update"}:
                    assert b"State: CURRENT" in result.stdout or operation == "update", result.stdout
                if operation == "install":
                    before_update = receipt
                    c2 = subprocess.run([sys.executable, str(ROOT / "scripts/c2_isolation_validation.py"),
                                         "--destination", str(dest)], cwd=ROOT, env=env, capture_output=True)
                    (output / f"{shell}-installed-c2.stdout.log").write_bytes(c2.stdout)
                    (output / f"{shell}-installed-c2.stderr.log").write_bytes(c2.stderr)
                    assert c2.returncode == 0 and b"C2_CLEAN" in c2.stdout, (c2.stdout, c2.stderr)
                if operation == "update":
                    assert receipt == before_update
            results.append({"shell": shell, "managed_files": len(payload), "payload_sha256": digest,
                            "operations": ["install", "status", "update", "uninstall"],
                            "receipt_and_payload": "exact committed bytes", "user_file": "preserved", "result": "PASS"})
    finally:
        cleanup_workspace(work, work.parent, "lp-smoke-")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--powershell", required=True)
    parser.add_argument("--bash", required=True)
    parser.add_argument("--powershell-major", type=int, choices=(5, 7), required=True)
    parser.add_argument("--bash-major", type=int)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--smoke-only", action="store_true", help="Full suite already ran in this job")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error("output directory already exists; preserve previous evidence")
    output.mkdir(parents=True)
    record = {"kind": "installation-maintenance-evidence; no operator trust or Host Acceptance",
              "started_at": datetime.now(timezone.utc).isoformat(),
              "platform": platform.platform(), "architecture": platform.machine(),
              "python": platform.python_version(),
              "requested_shells": {"powershell": args.powershell, "bash": args.bash},
              "result": "NOT_RUN"}
    try:
        if not __debug__:
            raise RuntimeError("Optimized Python disables verification assertions; run without -O or PYTHONOPTIMIZE")
        os.environ["LOOPPILOT_TEST_POWERSHELL"] = args.powershell
        os.environ["LOOPPILOT_TEST_BASH"] = args.bash
        os.environ["LOOPPILOT_TEST_REQUIRE_SHELLS"] = "1"
        sys.path.insert(0, str(ROOT / "tests"))
        from test_distribution import BASH, POWERSHELL

        record.update({"powershell": shell_info(POWERSHELL, True, output),
                       "bash": shell_info(BASH, False, output),
                       "git": run(["git", "--version"]).decode().strip(),
                       "commit": run(["git", "--no-replace-objects", "rev-parse", "HEAD"]).decode().strip(),
                       "tree": run(["git", "--no-replace-objects", "rev-parse", "HEAD^{tree}"]).decode().strip()})
        prefix = "5.1." if args.powershell_major == 5 else "7."
        assert record["powershell"]["version"].startswith(prefix)
        if args.bash_major:
            prefix = "3.2." if args.bash_major == 3 else str(args.bash_major) + "."
            assert f"version {prefix}" in record["bash"]["version"]
        assert not run(["git", "status", "--porcelain=v1"]), "source checkout must be clean"
        print(json.dumps(record), flush=True)
        if not args.smoke_only:
            suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in MODULES)
            with (output / "tests.log").open("w", encoding="utf-8") as log:
                result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
            record["tests"] = {"count": result.testsRun, "failures": len(result.failures),
                               "errors": len(result.errors), "skipped": len(result.skipped)}
            assert result.wasSuccessful() and not result.skipped, record["tests"]
        record["lifecycle"] = smoke(output, record["commit"])
        record["result"] = "PASS"
        return 0
    except Exception as error:
        record["result"] = "FAIL"
        record["error"] = str(error)
        print(str(error), file=sys.stderr)
        return 1
    finally:
        record["finished_at"] = datetime.now(timezone.utc).isoformat()
        record["files_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file()}
        (output / "result.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(record, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
