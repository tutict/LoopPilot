"""Real local process output wrapped in synthetic evaluation/approval fixtures.

This is test data, never host acceptance or production trust provisioning.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone

CORE_DIMENSIONS = ("Goal fidelity", "Plan quality", "Evidence quality", "Adaptation quality", "Loop efficiency", "Safety", "Completion honesty", "Evidence integrity across agents", "Authority continuity", "Host-native integration")
LIMITATIONS = "Only the local deterministic validation specimen was exercised; host and model behavior remain unverified."
REPLAY_MATRIX = Path(__file__).resolve().parents[1] / "docs/evaluations/historical-replay-matrix.json"
CURRENT_MATRIX = Path(__file__).resolve().parents[1] / "docs/evaluations/current-acceptance-matrix.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def make_package(root, authority, *, evaluation_id="EVAL-TEST-001", scenario_id="scenario 68", shape="lightweight", host="Local validation executor", host_version="1.0", model="deterministic-subprocess", commit="a" * 40, loading_mode="explicit", author="evaluator-a", reviewer="reviewer-b", decision="accept", score=3, code_quality_applicability="not-applicable", code_quality_score=3, parent="test-host"):
    package = root / "evaluations" / parent / evaluation_id
    evidence = package / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    run_id = "RUN-" + evaluation_id
    scenario = {"schema_version": 1, "scenario_id": scenario_id, "shape": shape, "description": "Local deterministic validator specimen; not a host acceptance run.", "input": "Compute six times seven locally.", "expected_output": "42"}
    save_json(evidence / "scenario.json", scenario)
    (evidence / "input.txt").write_text(scenario["input"] + "\n", encoding="utf-8", newline="\n")
    code_artifacts = []
    if code_quality_applicability == "applicable":
        code_path = evidence / "normalize_labels.py"
        code_path.write_text("def normalize_labels(values):\n    return list(values)\n", encoding="utf-8", newline="\n")
        code_artifacts.append("evidence/normalize_labels.py")
    applicability_payload = {
        "schema_version": 1,
        "kind": "code-quality-applicability",
        "run_id": run_id,
        "evaluation_id": evaluation_id,
        "scenario_id": scenario_id,
        "applicability": code_quality_applicability,
        "code_artifacts": code_artifacts,
    }
    save_json(evidence / "code-quality-applicability.json", applicability_payload)
    started = datetime.now(timezone.utc).isoformat()
    observed = subprocess.run([sys.executable, "-c", "print(6 * 7)"], capture_output=True, check=True)
    ended = datetime.now(timezone.utc).isoformat()
    (evidence / "stdout.txt").write_bytes(observed.stdout)
    assert observed.stdout.strip() == b"42"
    events = [
        {"id": "input-1", "run_id": run_id, "kind": "input", "artifact": "evidence/input.txt", "sha256": digest(evidence / "input.txt")},
        {"id": "result-1", "run_id": run_id, "kind": "result", "artifact": "evidence/stdout.txt", "sha256": digest(evidence / "stdout.txt")},
        {"id": "code-quality-applicability", "run_id": run_id, "kind": "observation", "artifact": "evidence/code-quality-applicability.json", "sha256": digest(evidence / "code-quality-applicability.json")},
    ]
    if code_artifacts:
        code_path = package / code_artifacts[0]
        events.append({"id": "code-artifact-1", "run_id": run_id, "kind": "observation", "artifact": code_artifacts[0], "sha256": digest(code_path)})
    (evidence / "events.jsonl").write_text("".join(json.dumps(e, sort_keys=True) + "\n" for e in events), encoding="utf-8", newline="\n")
    common = f"- Evaluation ID: {evaluation_id}\n- Scenario ID: {scenario_id}\n"
    (package / "environment.md").write_text("# Environment\n\n" + common + f"- Date and time: {started}\n- Host: {host}\n- Host version: {host_version}\n- Model: {model}\n- LoopPilot commit: {commit}\n- Skill loading mode: {loading_mode}\n- Task fixture: evidence/scenario.json\n- Available tools and state: local Python subprocess\n- Granted authority: local test execution only\n- Material environment constraints: no host or model execution\n- Limitation state: unverified\n- Unverified limitations: {LIMITATIONS}\n", encoding="utf-8")
    (package / "prompt.md").write_text("# Prompt\n\n" + common + "- Variant: LoopPilot loaded\n- Task fixture: evidence/scenario.json\n\n## Exact User Input\n\nCompute six times seven locally.\n\n## Input Boundary\n\nOnly the deterministic local specimen input was supplied. No host acceptance was run.\n", encoding="utf-8")
    trace_link = "[observed result](evidence/events.jsonl#result-1)"
    applicability_link = "[applicability evidence](evidence/events.jsonl#code-quality-applicability)"
    code_quality_link = "[code artifact](evidence/events.jsonl#code-artifact-1)" if code_artifacts else applicability_link
    (package / "trace.md").write_text("# Observed Trace\n\n" + common + f"- Variant: LoopPilot loaded\n- Evidence links: {trace_link}\n\nLocal process output was captured; this is not a host/model observation.\n", encoding="utf-8")
    code_score = code_quality_score if code_quality_applicability == "applicable" else "not-applicable"
    rows = "\n".join(f"| {d} | {score} | {trace_link} |" for d in CORE_DIMENSIONS)
    rows += f"\n| Code quality | {code_score} | {code_quality_link} |"
    applicable_dimensions = len(CORE_DIMENSIONS) + (code_quality_applicability == "applicable")
    total = score * len(CORE_DIMENSIONS) + (code_quality_score if code_quality_applicability == "applicable" else 0)
    (package / "score.md").write_text("# Evaluation Score\n\n" + common + f"- Score schema version: 2\n- Host and version: {host} {host_version}\n- Model: {model}\n- LoopPilot commit: {commit}\n- Skill loading mode: {loading_mode}\n- Task fixture: evidence/scenario.json\n- Observed outcome: completed\n- Evidence links: {trace_link}\n- Code quality applicability: {code_quality_applicability}\n- Code quality applicability evidence: {applicability_link}\n\n| Dimension | Score | Observed evidence |\n| --- | ---: | --- |\n{rows}\n\n- Applied score caps: none\n- Critical failures: none\n- Applicable dimensions: {applicable_dimensions}\n- Total: {total}\n- Evaluator interpretation: deterministic local specimen only\n- Highest-value improvement: no host conclusions may be drawn\n- Retest needed: actual host behavior remains unverified\n- Reviewer decision: {decision}\n- Reviewer: {reviewer}\n- Limitation state: unverified\n- Unverified limitations: {LIMITATIONS}\n", encoding="utf-8")
    evidence_files = {path.relative_to(package).as_posix(): digest(path) for path in evidence.iterdir() if path.is_file() and path.name != "events.jsonl"}
    run = {"schema_version": 1, "run_id": run_id, "evaluation_id": evaluation_id, "scenario_id": scenario_id, "scenario_shape": shape, "scenario_path": "evidence/scenario.json", "scenario_sha256": digest(evidence / "scenario.json"), "host": host, "host_version": host_version, "model": model, "commit": commit, "loading_mode": loading_mode, "trace_author": author, "started_at": started, "ended_at": ended, "status": "completed", "exit_code": observed.returncode, "trace_path": "evidence/events.jsonl", "trace_sha256": digest(evidence / "events.jsonl"), "evidence": evidence_files}
    save_json(package / "run.json", run)
    review = {"schema_version": 2, "run_id": run_id, "evaluation_id": evaluation_id, "run_sha256": digest(package / "run.json"), "reviewer": reviewer, "decision": decision, "artifacts": {name: digest(package / name) for name in ("environment.md", "prompt.md", "trace.md", "score.md")}}
    review["disclosures"] = {"outcome": "completed", "limitations": {"state": "unverified", "text": LIMITATIONS, "evidence": trace_link}, "score_caps": "none", "critical_failures": "none"}
    save_json(package / "review.json", review)
    index = json.loads(authority.read_text(encoding="utf-8")) if authority.exists() else {"schema_version": 1, "runs": {}, "records": {}}
    index["runs"][run_id] = {"run_sha256": digest(package / "run.json"), "review_sha256": digest(package / "review.json")}
    save_json(authority, index)
    return package


def make_current_acceptance_package(root, authority, *, arm_id, predecessor_run_id=None, parent="current-host"):
    matrix = json.loads(CURRENT_MATRIX.read_text(encoding="utf-8"))
    arm = next(item for item in matrix["arms"] if item["arm_id"] == arm_id)
    evaluation_id = f"EVAL-CURRENT-{arm_id}"
    package = make_package(
        root,
        authority,
        evaluation_id=evaluation_id,
        scenario_id=arm["scenario_id"],
        shape=arm["scenario_shape"],
        host="Current validation host",
        host_version="current-1",
        model="current-model",
        commit="a" * 40,
        loading_mode=arm["loading_mode"],
        code_quality_applicability="not-applicable",
        parent=parent,
    )
    run_path = package / "run.json"
    run = json.loads(run_path.read_text(encoding="utf-8"))
    evidence = package / "evidence"
    packet = evidence / "blind-review-packet.md"
    packet.write_text("De-identified evidence packet for independent blind review.\n", encoding="utf-8", newline="\n")
    checkpoint = evidence / "checkpoint.json"
    checkpoint.write_text(json.dumps({"checkpoint": "FL-1 observed checkpoint"}, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    boundary = {
        "schema_version": 1,
        "kind": "current-validation-boundary",
        "boundary_id": "BOUNDARY-CURRENT-001",
        "observed_at": "2026-11-10T00:00:00+00:00",
        "host": run["host"],
        "host_version": run["host_version"],
        "model": run["model"],
        "provider": "fixture-provider",
        "endpoint": "fixture-endpoint",
        "commit": run["commit"],
        "git_tree": "b" * 40,
        "skill_sha256": "c" * 64,
        "install_provenance": "CURRENT",
        "c2_status": "C2_CLEAN",
        "permission_preflight": "pass",
        "permission_mode": "acceptEdits",
        "tools_digest": "d" * 64,
        "fixture_root": str(Path(root).parent / "current-fixture").replace("\\", "/"),
    }
    lineage = {
        "schema_version": 1,
        "kind": "current-acceptance-lineage",
        "boundary_id": boundary["boundary_id"],
        "arm_id": arm_id,
        "scenario_id": arm["scenario_id"],
        "scenario_shape": arm["scenario_shape"],
        "loading_mode": arm["loading_mode"],
        "predecessor_run_id": predecessor_run_id,
        "predecessor_checkpoint_path": "evidence/checkpoint.json" if predecessor_run_id else None,
        "predecessor_checkpoint_sha256": digest(checkpoint) if predecessor_run_id else None,
        "blind_review_id": f"BLIND-CURRENT-{arm_id}-01-abcdef123456",
        "attempt": 1,
        "retry_of": None,
        "retry_reason": None,
    }
    save_json(evidence / "current-validation-boundary.json", boundary)
    save_json(evidence / "current-acceptance-lineage.json", lineage)
    run["evidence"].update({
        "evidence/blind-review-packet.md": digest(packet),
        "evidence/checkpoint.json": digest(checkpoint),
        "evidence/current-validation-boundary.json": digest(evidence / "current-validation-boundary.json"),
        "evidence/current-acceptance-lineage.json": digest(evidence / "current-acceptance-lineage.json"),
    })
    events_path = evidence / "events.jsonl"
    events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
    events.extend([
        {"id": "current-boundary", "run_id": run["run_id"], "kind": "observation", "artifact": "evidence/current-validation-boundary.json", "sha256": digest(evidence / "current-validation-boundary.json")},
        {"id": "current-lineage", "run_id": run["run_id"], "kind": "observation", "artifact": "evidence/current-acceptance-lineage.json", "sha256": digest(evidence / "current-acceptance-lineage.json")},
        {"id": "checkpoint", "run_id": run["run_id"], "kind": "observation", "artifact": "evidence/checkpoint.json", "sha256": digest(checkpoint)},
    ])
    events_path.write_text("".join(json.dumps(event, sort_keys=True) + "\n" for event in events), encoding="utf-8", newline="\n")
    run["trace_sha256"] = digest(events_path)
    save_json(run_path, run)
    review_path = package / "review.json"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    review.update({
        "schema_version": 4,
        "review_axes": {
            "Spec": {"applicability": "applicable", "decision": "pass", "evidence": "[result](evidence/events.jsonl#result-1)"},
            "Standards": {"applicability": "applicable", "decision": "pass", "evidence": "[result](evidence/events.jsonl#result-1)"},
            "Implementation Quality": {"applicability": "not-applicable", "decision": "not-applicable", "evidence": "[result](evidence/events.jsonl#result-1)"},
            "Verification & Evidence": {"applicability": "applicable", "decision": "pass", "evidence": "[result](evidence/events.jsonl#result-1)"},
        },
        "independence": {
            "trace_author_operator_id": "operator-a", "trace_author_session_id": "session-a",
            "reviewer_operator_id": "operator-b", "reviewer_session_id": "session-b", "basis": "Separate operator and session identities.",
        },
        "blind_review_id": lineage["blind_review_id"],
        "review_packet_sha256": digest(packet),
        "condition_guess": "unknown",
        "guess_confidence": "low",
        "review_completed_at": "2026-11-10T01:00:00+00:00",
        "condition_guess_recorded_at": "2026-11-10T01:01:00+00:00",
        "condition_revealed_at": "2026-11-10T01:02:00+00:00",
    })
    review["run_sha256"] = digest(run_path)
    review["artifacts"] = {name: digest(package / name) for name in ("environment.md", "prompt.md", "trace.md", "score.md")}
    save_json(review_path, review)
    index = json.loads(authority.read_text(encoding="utf-8"))
    index["runs"][run["run_id"]] = {"run_sha256": digest(run_path), "review_sha256": digest(review_path)}
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


def make_historical_replay_package(root, authority, *, pair_index=0, arm="control", failed=False):
    """Build a local replay specimen for public validator tests only."""
    matrix = json.loads(REPLAY_MATRIX.read_text(encoding="utf-8"))
    pair = matrix["pairs"][pair_index]
    arm_spec = pair[arm]
    loading_probe = pair["evidence_type"] == "loading-probe"
    identity = pair["original_combination"]
    package = make_package(
        root,
        authority,
        evaluation_id=arm_spec["evaluation_id"],
        scenario_id=pair["scenario_id"],
        shape=pair["scenario_shape"],
        host=identity["host"],
        host_version=identity["host_version"],
        model=identity["model"],
        loading_mode=arm_spec["loading_mode"],
        parent="claude-code",
    )
    lineage_path = package / "evidence/historical-lineage.json"
    run_id = "RUN-" + arm_spec["evaluation_id"]
    lineage = {
        "schema_version": 1,
        "kind": "historical-lineage",
        "pair_id": pair["pair_id"],
        "historical_evaluation_id": pair["historical_evaluation_id"],
        "scenario_id": pair["scenario_id"],
        "scenario_shape": pair["scenario_shape"],
        "arm": arm,
        "attempt": 1,
        "retry_of": None,
        "retry_reason": None,
        "replay_reason": "Fill missing matched control and Skill-loaded evidence without changing history.",
        "known_gaps": pair["known_gaps"],
        "original_combination": identity,
        "reproduction_status": "matched",
        "reproduction_reason": None,
        "blind_review_id": f"BLIND-{pair['pair_id']}-01-{run_id[-6:].lower():0>12}",
    }
    save_json(lineage_path, lineage)
    run_path = package / "run.json"
    run = json.loads(run_path.read_text(encoding="utf-8"))
    run["evidence"]["evidence/historical-lineage.json"] = digest(lineage_path)
    events_path = package / "evidence/events.jsonl"
    events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
    events.append({"id": "historical-lineage", "run_id": run["run_id"], "kind": "observation", "artifact": "evidence/historical-lineage.json", "sha256": digest(lineage_path)})
    if loading_probe:
        observation_path = package / "evidence/loading-observation.json"
        observation = {
            "schema_version": 1,
            "kind": "skill-loading-observation",
            "run_id": run["run_id"],
            "evaluation_id": run["evaluation_id"],
            "scenario_id": run["scenario_id"],
            "loading_mode": run["loading_mode"],
            "result": "not-observed" if failed else "not-loaded" if arm == "control" else "loaded",
            "observed_at": run["started_at"],
            "basis": "The public host event stream recorded the loading probe result.",
        }
        save_json(observation_path, observation)
        run["evidence"]["evidence/loading-observation.json"] = digest(observation_path)
        events.append({"id": "loading-observation", "run_id": run["run_id"], "kind": "observation", "artifact": "evidence/loading-observation.json", "sha256": digest(observation_path)})
    if failed:
        run["status"] = "failed"
        run["exit_code"] = 429
        output = package / "evidence/stdout.txt"
        output.write_text("HTTP 429 rate_limit\n", encoding="utf-8", newline="\n")
        run["evidence"]["evidence/stdout.txt"] = digest(output)
        events[1]["sha256"] = digest(output)
    events_path.write_text("".join(json.dumps(event, sort_keys=True) + "\n" for event in events), encoding="utf-8", newline="\n")
    run["trace_sha256"] = digest(events_path)
    save_json(run_path, run)
    variant = "control" if arm == "control" else "LoopPilot loaded"
    for name in ("prompt.md", "trace.md"):
        path = package / name
        path.write_text(path.read_text(encoding="utf-8").replace("- Variant: LoopPilot loaded", f"- Variant: {variant}"), encoding="utf-8", newline="\n")
    score_path = package / "score.md"
    score_text = score_path.read_text(encoding="utf-8").replace("- Variant: LoopPilot loaded", f"- Variant: {variant}")
    if failed:
        score_text = score_text.replace("- Observed outcome: completed", "- Observed outcome: failed")
        score_text = score_text.replace("- Reviewer decision: accept", "- Reviewer decision: reject")
        score_text = score_text.replace("- Critical failures: none", "- Critical failures: HTTP 429 rate_limit interrupted this run before a complete behavioral result.")
        for dimension in CORE_DIMENSIONS:
            score_text = score_text.replace(f"| {dimension} | 3 |", f"| {dimension} | not-evaluated |")
        score_text = score_text.replace("- Total: 30", "- Total: not-evaluated")
    elif loading_probe:
        for dimension in CORE_DIMENSIONS:
            score_text = score_text.replace(f"| {dimension} | 3 |", f"| {dimension} | not-evaluated |")
        score_text = score_text.replace("- Total: 30", "- Total: not-evaluated")
        score_text = score_text.replace("- Evaluator interpretation: deterministic local specimen only", "- Evaluator interpretation: host loading probe only; behavioral rubric not evaluated")
    score_path.write_text(score_text, encoding="utf-8", newline="\n")
    review_path = package / "review.json"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    review["schema_version"] = 3
    review["decision"] = "reject" if failed else "accept"
    review["review_axes"] = {
        "Spec": {"applicability": "applicable", "decision": "fail" if failed else "pass", "evidence": "[result](evidence/events.jsonl#result-1)"},
        "Standards": {"applicability": "applicable", "decision": "pass", "evidence": "[result](evidence/events.jsonl#result-1)"},
        "Implementation Quality": {"applicability": "not-applicable", "decision": "not-applicable", "evidence": "[result](evidence/events.jsonl#result-1)"},
        "Verification & Evidence": {"applicability": "applicable", "decision": "pass", "evidence": "[result](evidence/events.jsonl#result-1)"},
    }
    review["independence"] = {
        "trace_author_operator_id": "operator-a",
        "trace_author_session_id": "session-a",
        "reviewer_operator_id": "operator-b",
        "reviewer_session_id": "session-b",
        "basis": "Review occurred in a separate operator-owned session.",
    }
    review["blind_review_id"] = lineage["blind_review_id"]
    review["review_packet_sha256"] = "a" * 64
    review["condition_guess"] = "unknown"
    review["guess_confidence"] = "low"
    if failed:
        review["disclosures"]["outcome"] = "failed"
        review["disclosures"]["critical_failures"] = "HTTP 429 rate_limit interrupted this run before a complete behavioral result."
        review["disclosures"]["limitations"]["state"] = "unresolved"
        review["disclosures"]["limitations"]["text"] = "The host rate limit interrupted the run; complete behavioral evidence remains unverified."
        for name in ("environment.md", "score.md"):
            path = package / name
            text = path.read_text(encoding="utf-8").replace("- Limitation state: unverified", "- Limitation state: unresolved")
            text = text.replace(LIMITATIONS, review["disclosures"]["limitations"]["text"])
            path.write_text(text, encoding="utf-8", newline="\n")
    review["run_sha256"] = digest(run_path)
    review["artifacts"] = {name: digest(package / name) for name in ("environment.md", "prompt.md", "trace.md", "score.md")}
    save_json(review_path, review)
    index = json.loads(authority.read_text(encoding="utf-8"))
    index["runs"][run["run_id"]] = {"run_sha256": digest(run_path), "review_sha256": digest(review_path)}
    save_json(authority, index)
    return package
