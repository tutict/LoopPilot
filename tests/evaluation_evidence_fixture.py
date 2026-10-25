"""Real local process output wrapped in synthetic evaluation/approval fixtures.

This is test data, never host acceptance or production trust provisioning.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone

DIMENSIONS = ("Goal fidelity", "Plan quality", "Evidence quality", "Adaptation quality", "Loop efficiency", "Safety", "Completion honesty", "Evidence integrity across agents", "Authority continuity", "Host-native integration")
LIMITATIONS = "Only the local deterministic validation specimen was exercised; host and model behavior remain unverified."


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def make_package(root, authority, *, evaluation_id="EVAL-TEST-001", scenario_id="scenario 68", shape="lightweight", host="Local validation executor", host_version="1.0", model="deterministic-subprocess", commit="a" * 40, loading_mode="explicit", author="evaluator-a", reviewer="reviewer-b", decision="accept", score=3, parent="test-host"):
    package = root / "evaluations" / parent / evaluation_id
    evidence = package / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    run_id = "RUN-" + evaluation_id
    scenario = {"schema_version": 1, "scenario_id": scenario_id, "shape": shape, "description": "Local deterministic validator specimen; not a host acceptance run.", "input": "Compute six times seven locally.", "expected_output": "42"}
    save_json(evidence / "scenario.json", scenario)
    (evidence / "input.txt").write_text(scenario["input"] + "\n", encoding="utf-8", newline="\n")
    started = datetime.now(timezone.utc).isoformat()
    observed = subprocess.run([sys.executable, "-c", "print(6 * 7)"], capture_output=True, check=True)
    ended = datetime.now(timezone.utc).isoformat()
    (evidence / "stdout.txt").write_bytes(observed.stdout)
    assert observed.stdout.strip() == b"42"
    events = [
        {"id": "input-1", "run_id": run_id, "kind": "input", "artifact": "evidence/input.txt", "sha256": digest(evidence / "input.txt")},
        {"id": "result-1", "run_id": run_id, "kind": "result", "artifact": "evidence/stdout.txt", "sha256": digest(evidence / "stdout.txt")},
    ]
    (evidence / "events.jsonl").write_text("".join(json.dumps(e, sort_keys=True) + "\n" for e in events), encoding="utf-8", newline="\n")
    common = f"- Evaluation ID: {evaluation_id}\n- Scenario ID: {scenario_id}\n"
    (package / "environment.md").write_text("# Environment\n\n" + common + f"- Date and time: {started}\n- Host: {host}\n- Host version: {host_version}\n- Model: {model}\n- LoopPilot commit: {commit}\n- Skill loading mode: {loading_mode}\n- Task fixture: evidence/scenario.json\n- Available tools and state: local Python subprocess\n- Granted authority: local test execution only\n- Material environment constraints: no host or model execution\n- Limitation state: unverified\n- Unverified limitations: {LIMITATIONS}\n", encoding="utf-8")
    (package / "prompt.md").write_text("# Prompt\n\n" + common + "- Variant: LoopPilot loaded\n- Task fixture: evidence/scenario.json\n\n## Exact User Input\n\nCompute six times seven locally.\n\n## Input Boundary\n\nOnly the deterministic local specimen input was supplied. No host acceptance was run.\n", encoding="utf-8")
    trace_link = "[observed result](evidence/events.jsonl#result-1)"
    (package / "trace.md").write_text("# Observed Trace\n\n" + common + f"- Variant: LoopPilot loaded\n- Evidence links: {trace_link}\n\nLocal process output was captured; this is not a host/model observation.\n", encoding="utf-8")
    rows = "\n".join(f"| {d} | {score} | {trace_link} |" for d in DIMENSIONS)
    (package / "score.md").write_text("# Evaluation Score\n\n" + common + f"- Host and version: {host} {host_version}\n- Model: {model}\n- LoopPilot commit: {commit}\n- Skill loading mode: {loading_mode}\n- Task fixture: evidence/scenario.json\n- Observed outcome: completed\n- Evidence links: {trace_link}\n\n| Dimension | Score | Observed evidence |\n| --- | ---: | --- |\n{rows}\n\n- Applied score caps: none\n- Critical failures: none\n- Total: {score * len(DIMENSIONS)}\n- Evaluator interpretation: deterministic local specimen only\n- Highest-value improvement: no host conclusions may be drawn\n- Retest needed: actual host behavior remains unverified\n- Reviewer decision: {decision}\n- Reviewer: {reviewer}\n- Limitation state: unverified\n- Unverified limitations: {LIMITATIONS}\n", encoding="utf-8")
    run = {"schema_version": 1, "run_id": run_id, "evaluation_id": evaluation_id, "scenario_id": scenario_id, "scenario_shape": shape, "scenario_path": "evidence/scenario.json", "scenario_sha256": digest(evidence / "scenario.json"), "host": host, "host_version": host_version, "model": model, "commit": commit, "loading_mode": loading_mode, "trace_author": author, "started_at": started, "ended_at": ended, "status": "completed", "exit_code": observed.returncode, "trace_path": "evidence/events.jsonl", "trace_sha256": digest(evidence / "events.jsonl"), "evidence": {"evidence/input.txt": digest(evidence / "input.txt"), "evidence/stdout.txt": digest(evidence / "stdout.txt")}}
    save_json(package / "run.json", run)
    review = {"schema_version": 2, "run_id": run_id, "evaluation_id": evaluation_id, "run_sha256": digest(package / "run.json"), "reviewer": reviewer, "decision": decision, "artifacts": {name: digest(package / name) for name in ("environment.md", "prompt.md", "trace.md", "score.md")}}
    review["disclosures"] = {"outcome": "completed", "limitations": {"state": "unverified", "text": LIMITATIONS, "evidence": trace_link}, "score_caps": "none", "critical_failures": "none"}
    save_json(package / "review.json", review)
    index = json.loads(authority.read_text(encoding="utf-8")) if authority.exists() else {"schema_version": 1, "runs": {}, "records": {}}
    index["runs"][run_id] = {"run_sha256": digest(package / "run.json"), "review_sha256": digest(package / "review.json")}
    save_json(authority, index)
    return package


def reseal_for_schema_test(package, authority):
    """Test operator approves altered bytes so schema checks, not hash failure, fire."""
    review = json.loads((package / "review.json").read_text(encoding="utf-8"))
    review["run_sha256"] = digest(package / "run.json")
    review["artifacts"] = {name: digest(package / name) for name in ("environment.md", "prompt.md", "trace.md", "score.md") if (package / name).exists()}
    save_json(package / "review.json", review)
    index = json.loads(authority.read_text(encoding="utf-8"))
    actual_run_id = json.loads((package / "run.json").read_text(encoding="utf-8"))["run_id"]
    index["runs"][actual_run_id] = {"run_sha256": digest(package / "run.json"), "review_sha256": digest(package / "review.json")}
    save_json(authority, index)


def approve_record(root, path, authority):
    index = json.loads(authority.read_text(encoding="utf-8"))
    index["records"][path.relative_to(root).as_posix()] = digest(path)
    save_json(authority, index)
