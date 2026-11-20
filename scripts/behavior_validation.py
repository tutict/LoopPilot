"""Plan, blind, and summarize the two-stage LoopPilot behavior validation."""
from __future__ import annotations

import argparse
import base64
from datetime import datetime
import hashlib
import json
from pathlib import Path
import random
import re
import secrets
import sys
from pathlib import PurePosixPath

HISTORICAL_MATRIX_PATH = "docs/evaluations/historical-replay-matrix.json"
CURRENT_ACCEPTANCE_MATRIX_PATH = "docs/evaluations/current-acceptance-matrix.json"
CODEX_REPLICATION_MATRIX_PATH = "docs/evaluations/codex-replication-matrix.json"
EXPECTED_FORMAL_ARMS = {"LW-1", "FL-1", "FL-1R", "IMP-1"}
EXPECTED_PRIMARY_RUNS = 18
EXPECTED_CURRENT_ARMS = {
    "LW-1": ("scenario 68", "lightweight", "explicit", None, [1, 2, 3, 8], "prompts/LW-1.txt"),
    "FL-1": ("scenario 69", "full-loop", "explicit", None, [1, 2, 3, 4, 5, 7, 8], "prompts/FL-1.txt"),
    "FL-1R": ("scenario 53", "full-loop", "explicit", "FL-1", [3, 6, 8], "prompts/FL-1R.txt"),
    "IMP-1": ("named fixture: phase15-implicit-activation", "lightweight", "implicit", None, [1, 3, 8], "prompts/IMP-1.txt"),
}


def _load_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _dump_json(path: Path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _digest(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _historical_keys(root: Path) -> list[str]:
    matrix = _load_json(Path(root) / HISTORICAL_MATRIX_PATH)
    return [f"historical:{pair['pair_id']}:{arm}" for pair in matrix["pairs"] for arm in ("control", "skill_loaded")]


def _formal_keys(root: Path) -> list[str]:
    matrix = _load_json(Path(root) / CURRENT_ACCEPTANCE_MATRIX_PATH)
    return [f"current:{arm['arm_id']}" for arm in matrix["arms"]]


def _codex_replication_keys(root: Path) -> list[str]:
    matrix = _load_json(Path(root) / CODEX_REPLICATION_MATRIX_PATH)
    return [
        f"replication:{pair['pair_id']}:{arm}"
        for pair in matrix["pairs"]
        for arm in ("control", "skill_loaded")
    ]


def validate_codex_replication_matrix(root: Path) -> list[str]:
    """Validate the separate Codex replication design without running a Host."""
    root = Path(root)
    errors = []
    path = root / CODEX_REPLICATION_MATRIX_PATH
    try:
        matrix = _load_json(path)
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        return [f"Codex replication matrix unreadable: {error}"]

    if not isinstance(matrix, dict):
        return ["Codex replication matrix must be an object"]

    expected_top = {"schema_version", "kind", "purpose", "retry_policy", "pairs", "current_evaluation_ids"}
    if set(matrix) != expected_top:
        errors.append("Codex replication matrix schema keys invalid")
    if matrix.get("schema_version") != 1 or matrix.get("kind") != "codex-replication-matrix":
        errors.append("Codex replication matrix kind/version invalid")
    retry = matrix.get("retry_policy", {})
    retry_keys = {"max_retries", "new_evaluation_id_and_run_id_per_retry", "retry_only_execution_infrastructure_incidents", "retain_every_failed_attempt"}
    if not isinstance(retry, dict) or set(retry) != retry_keys or retry.get("max_retries") != 2 or not all(retry.get(key) is True for key in retry_keys - {"max_retries"}):
        errors.append("Codex replication retry policy invalid")

    pairs = matrix.get("pairs")
    expected_pairs = {
        "COD-RPL-EVAL-001-S43": ("EVAL-001", "scenario 43", "Requested Skill Is Unavailable", "lightweight", "behavior", "explicit"),
        "COD-RPL-EVAL-002-S68": ("EVAL-002", "scenario 68", "Simple Change Uses Lightweight Mode", "lightweight", "behavior", "explicit"),
        "COD-RPL-EVAL-003-S69": ("EVAL-003", "scenario 69", "High-Risk Multi-Stage Work Uses Full Loop Mode", "full-loop", "behavior", "explicit"),
        "COD-RPL-EVAL-004-ARM-A": ("EVAL-004", "host-skill-loading-probe-arm-a", "Host Skill loading probe, explicit invocation", "lightweight", "loading-probe", "explicit"),
        "COD-RPL-EVAL-004-ARM-B": ("EVAL-004", "host-skill-loading-probe-arm-b", "Host Skill loading probe, implicit invocation", "lightweight", "loading-probe", "implicit"),
        "COD-RPL-EVAL-005-FIXTURE-A": ("EVAL-005", "phase14-lightweight-explicit", "Phase 14 Lightweight explicit fixture", "lightweight", "behavior", "explicit"),
        "COD-RPL-EVAL-005-IMPLICIT": ("EVAL-005", "phase14-implicit-activation", "Phase 14 implicit activation fixture", "lightweight", "behavior", "implicit"),
    }
    expected_pair_ids = set(expected_pairs)
    if not isinstance(pairs, list) or len(pairs) != 7:
        errors.append("Codex replication matrix must define seven pairs")
        pairs = pairs if isinstance(pairs, list) else []
    seen_pairs = set()
    seen_evaluations = []
    behavior_count = 0
    loading_count = 0
    allowed_modes = {"not-loaded", "explicit", "implicit"}
    for pair in pairs:
        pair_keys = {"pair_id", "source_evaluation_id", "scenario_id", "scenario_title", "scenario_shape", "evidence_type", "prompt_path", "prompt_sha256", "control", "skill_loaded"}
        if not isinstance(pair, dict) or set(pair) != pair_keys:
            if isinstance(pair, dict) and "original_combination" in pair:
                errors.append("Codex replication original_combination is not allowed; Claude identity is provenance only")
            errors.append("Codex replication pair schema keys invalid")
            continue
        pair_id = pair["pair_id"]
        if not isinstance(pair_id, str):
            errors.append("Codex replication pair_id must be a string")
            continue
        if pair_id in seen_pairs:
            errors.append("duplicate Codex replication pair_id")
        seen_pairs.add(pair_id)
        expected_pair = expected_pairs.get(pair_id)
        if expected_pair is None:
            errors.append(f"unknown Codex replication pair_id: {pair_id}")
            continue
        actual_identity = (
            pair.get("source_evaluation_id"), pair.get("scenario_id"), pair.get("scenario_title"),
            pair.get("scenario_shape"), pair.get("evidence_type"),
        )
        if actual_identity != expected_pair[:5]:
            errors.append(f"Codex replication pair {pair_id} identity differs from the approved scenario seed")
        if pair.get("scenario_shape") not in {"lightweight", "full-loop"}:
            errors.append(f"Codex replication pair {pair_id} scenario shape invalid")
        if pair.get("evidence_type") not in {"behavior", "loading-probe"}:
            errors.append(f"Codex replication pair {pair_id} evidence type invalid")
        elif pair["evidence_type"] == "behavior":
            behavior_count += 1
        else:
            loading_count += 1
        prompt_path = pair.get("prompt_path", "")
        expected_prompt_path = f"docs/evaluations/codex-replication-prompts/{pair_id}.txt"
        prompt = root / prompt_path if isinstance(prompt_path, str) else root / "__invalid__"
        if not isinstance(prompt_path, str) or prompt_path != expected_prompt_path or not prompt.is_file():
            errors.append(f"Codex replication prompt path invalid: {pair_id}")
        elif hashlib.sha256(prompt.read_bytes()).hexdigest() != pair.get("prompt_sha256"):
            errors.append(f"Codex replication prompt digest mismatch: {pair_id}")
        for arm in ("control", "skill_loaded"):
            value = pair.get(arm)
            if not isinstance(value, dict) or set(value) != {"evaluation_id", "loading_mode"}:
                errors.append(f"Codex replication {arm} arm schema invalid: {pair_id}")
                continue
            evaluation_id = value.get("evaluation_id")
            seen_evaluations.append(evaluation_id)
            if value.get("loading_mode") not in allowed_modes:
                errors.append(f"Codex replication loading_mode invalid: {pair_id}")
            if arm == "control" and value.get("loading_mode") != "not-loaded":
                errors.append(f"Codex replication control arm must be not-loaded: {pair_id}")
        skill_loaded = pair.get("skill_loaded")
        if isinstance(skill_loaded, dict):
            if skill_loaded.get("loading_mode") == "not-loaded":
                errors.append(f"Codex replication Skill-loaded arm must declare a loading condition: {pair_id}")
            if skill_loaded.get("loading_mode") != expected_pair[5]:
                errors.append(f"Codex replication pair {pair_id} loading mode differs from the approved scenario seed")

    if seen_pairs != expected_pair_ids:
        errors.append("Codex replication pair set is incomplete")
    if behavior_count != 5 or loading_count != 2:
        errors.append("Codex replication matrix must contain five behavior pairs and two loading probes")
    if seen_evaluations != [f"EVAL-{number:03d}" for number in range(20, 34)]:
        errors.append("Codex replication Evaluation IDs must be EVAL-020 through EVAL-033 in pair order")
    current_ids = matrix.get("current_evaluation_ids")
    if current_ids != {"LW-1": "EVAL-034", "FL-1": "EVAL-035", "FL-1R": "EVAL-036", "IMP-1": "EVAL-037"}:
        errors.append("Codex replication current Evaluation IDs are invalid")
    return sorted(set(errors))


def validate_behavior_matrices(root: Path) -> list[str]:
    """Validate the historical and current experiment design without running a Host."""
    root = Path(root)
    errors = []
    try:
        historical = _load_json(root / HISTORICAL_MATRIX_PATH)
        current = _load_json(root / CURRENT_ACCEPTANCE_MATRIX_PATH)
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        return [f"behavior matrix unreadable: {error}"]

    pairs = historical.get("pairs") if isinstance(historical, dict) else None
    if not isinstance(pairs, list) or len(pairs) != 7:
        errors.append("historical behavior matrix must define seven pairs")
    historical_ids = []
    for pair in pairs or []:
        if not isinstance(pair, dict):
            errors.append("historical behavior matrix contains a non-object pair")
            continue
        pair_id = pair.get("pair_id")
        if not isinstance(pair_id, str) or not pair_id:
            errors.append("historical pair_id is missing")
        for arm_name in ("control", "skill_loaded"):
            arm = pair.get(arm_name, {})
            identifier = arm.get("evaluation_id") if isinstance(arm, dict) else None
            if identifier in historical_ids:
                errors.append("historical Evaluation IDs must be unique")
            historical_ids.append(identifier)
        if pair.get("scenario_shape") not in {"lightweight", "full-loop"}:
            errors.append(f"historical pair {pair_id} has invalid scenario shape")
        if pair.get("evidence_type") not in {"behavior", "loading-probe"}:
            errors.append(f"historical pair {pair_id} has invalid evidence_type")
        if pair.get("historical_evaluation_id") == "EVAL-004" and pair.get("evidence_type") != "loading-probe":
            errors.append("EVAL-004 loading probes must be reported separately from behavior results")

    arms = current.get("arms") if isinstance(current, dict) else None
    arm_ids = {arm.get("arm_id") for arm in arms or [] if isinstance(arm, dict)}
    if arm_ids != EXPECTED_FORMAL_ARMS:
        errors.append(f"current acceptance arms must be exactly {sorted(EXPECTED_FORMAL_ARMS)}")
    if len(arms or []) != 4:
        errors.append("current acceptance matrix must define four formal arms")
    for arm in arms or []:
        if not isinstance(arm, dict):
            errors.append("current acceptance matrix contains a non-object arm")
            continue
        arm_id = arm.get("arm_id")
        expected = EXPECTED_CURRENT_ARMS.get(arm_id)
        actual = (
            arm.get("scenario_id"), arm.get("scenario_shape"), arm.get("loading_mode"),
            arm.get("predecessor_arm_id"), arm.get("dimension_ids"), arm.get("prompt_path"),
        )
        if expected is None or actual != expected:
            errors.append(f"current arm {arm_id} identity or coverage differs from the selected four-arm plan")
        if not arm.get("scenario_id") or not arm.get("scenario_title"):
            errors.append(f"current arm {arm_id} must name Scenario ID and title")
        if arm.get("loading_mode") not in {"explicit", "implicit"}:
            errors.append(f"current arm {arm_id} has invalid loading mode")
        if arm_id == "FL-1R" and arm.get("predecessor_arm_id") != "FL-1":
            errors.append("FL-1R must depend on FL-1")
        if arm_id != "FL-1R" and arm.get("predecessor_arm_id") is not None:
            errors.append(f"current arm {arm_id} cannot declare a predecessor")
    if current.get("primary_run_count") != EXPECTED_PRIMARY_RUNS:
        errors.append("two-stage behavior plan must require 18 primary runs")
    if current.get("retry_policy", {}).get("max_retries") != 2:
        errors.append("two-stage behavior plan must allow at most two retries")
    if current.get("required_acceptance_dimensions") != list(range(1, 9)):
        errors.append("current formal arms must retain all eight Host Acceptance dimensions")
    if current.get("expected_partial_ceiling_dimensions") != [2, 4]:
        errors.append("current formal matrix must disclose the existing partial ceilings for dimensions 2 and 4")
    covered = {dimension for arm in arms or [] if isinstance(arm, dict) for dimension in arm.get("dimension_ids", [])}
    if covered != set(range(1, 9)):
        errors.append("current formal arms must cover all eight Host Acceptance dimensions")
    gate = current.get("preflight_gate", {})
    required_preflight = {"install_provenance": "CURRENT", "c2": "C2_CLEAN", "permissions": "pass", "reviewer_ready": True, "evidence_index_authority_fixed": True}
    if gate != required_preflight:
        errors.append("current formal preflight must retain install, C2, permission, Reviewer, and external-index gates")
    if (root / CODEX_REPLICATION_MATRIX_PATH).is_file():
        errors.extend(validate_codex_replication_matrix(root))
    return sorted(set(errors))


def _current_run_order(rng) -> list[str]:
    pending = ["LW-1", "FL-1", "FL-1R", "IMP-1"]
    complete = set()
    output = []
    while pending:
        ready = [arm for arm in pending if arm != "FL-1R" or "FL-1" in complete]
        chosen = rng.choice(ready)
        output.append(f"current:{chosen}")
        complete.add(chosen)
        pending.remove(chosen)
    return output


def _output_outside_root(root: Path, output: Path):
    root = Path(root).resolve()
    output = Path(output).absolute()
    if output.resolve().is_relative_to(root):
        raise ValueError("blind plan and reviewer materials must be stored outside the repository")
    for node in (output, *output.parents):
        if node.is_symlink() or node.is_junction():
            raise ValueError("blind plan output path cannot traverse symlinks or junctions")


def reviewer_gate_errors(gate: dict, experiment_id: str) -> list[str]:
    """Validate the externally pinned pre-run reviewer assignment receipt."""
    errors = []
    required = {
        "schema_version", "kind", "experiment_id", "operator_id", "operator_session_id", "reviewer_operator_id",
        "reviewer_session_id", "blind_review_confirmed", "readiness", "confirmed_at", "scope",
    }
    if not isinstance(gate, dict) or set(gate) != required:
        return ["reviewer readiness receipt schema is invalid"]
    if gate.get("schema_version") != 1 or gate.get("kind") != "behavior-reviewer-readiness":
        errors.append("reviewer readiness receipt kind/version is invalid")
    if gate.get("experiment_id") != experiment_id:
        errors.append("reviewer readiness experiment_id does not match the blind plan")
    for key in ("operator_id", "operator_session_id", "reviewer_operator_id", "reviewer_session_id", "scope"):
        if not isinstance(gate.get(key), str) or len(gate[key].strip()) < 3:
            errors.append(f"reviewer readiness {key} is missing")
    if gate.get("operator_id") == gate.get("reviewer_operator_id"):
        errors.append("reviewer readiness requires a different operator")
    if gate.get("operator_session_id") == gate.get("reviewer_session_id"):
        errors.append("reviewer readiness requires a different session")
    if gate.get("blind_review_confirmed") is not True or gate.get("readiness") != "ready":
        errors.append("reviewer readiness must confirm anonymous blind review before execution")
    try:
        observed_at = datetime.fromisoformat(gate["confirmed_at"])
        if observed_at.tzinfo is None:
            raise ValueError("timezone required")
    except (KeyError, TypeError, ValueError):
        errors.append("reviewer readiness confirmed_at must be a timezone-qualified timestamp")
    return sorted(set(errors))


def load_pinned_reviewer_gate(root: Path, path: Path, expected_sha256: str, experiment_id: str) -> tuple[dict, list[str]]:
    """Read a reviewer gate only from outside the repository and verify raw bytes."""
    errors = []
    try:
        _output_outside_root(root, path)
        raw = Path(path).read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
            return {}, ["reviewer readiness SHA-256 pin is invalid"]
        if actual != expected_sha256:
            return {}, ["reviewer readiness SHA-256 pin mismatch"]
        gate = json.loads(raw.decode("utf-8-sig"))
        errors.extend(reviewer_gate_errors(gate, experiment_id))
        return gate, errors
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        return {}, [f"reviewer readiness receipt is unreadable: {error}"]


def load_pinned_blind_plan(root: Path, path: Path, expected_sha256: str) -> tuple[dict, list[str]]:
    errors = []
    try:
        _output_outside_root(root, path)
        raw = Path(path).read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
            return {}, ["blind plan SHA-256 pin is invalid"]
        if actual != expected_sha256:
            return {}, ["blind plan SHA-256 pin mismatch"]
        plan = json.loads(raw.decode("utf-8-sig"))
        return plan, errors
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        return {}, [f"blind plan is unreadable: {error}"]


def reviewer_gate_binding_errors(plan: dict, gate: dict, receipt_sha256: str) -> list[str]:
    errors = reviewer_gate_errors(gate, plan.get("experiment_id"))
    binding = plan.get("reviewer_gate", {})
    if binding.get("receipt_sha256") != receipt_sha256:
        errors.append("blind plan reviewer receipt digest differs from the external gate")
    for key in ("operator_id", "operator_session_id", "reviewer_operator_id", "reviewer_session_id"):
        if binding.get(key) != gate.get(key):
            errors.append(f"blind plan reviewer gate {key} differs from the pinned receipt")
    return sorted(set(errors))


def _blind_value(value, identities):
    if isinstance(value, dict):
        hidden = {
            "run_id", "evaluation_id", "host", "host_version", "model", "commit",
            "loading_mode", "trace_author", "reviewer", "pair_id", "arm_id", "arm",
            "historical_evaluation_id", "boundary_id", "skill_sha256", "blind_review_id",
            "provider", "endpoint", "operator_id", "reviewer_operator_id", "reviewer_session_id",
        }
        return {
            key: "[redacted]" if key.casefold() in hidden else _blind_value(item, identities)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_blind_value(item, identities) for item in value]
    if isinstance(value, str):
        for identity in identities:
            if identity:
                value = value.replace(identity, "[redacted]")
        return value
    return value


def _blind_text(text: str, identities: list[str]) -> str:
    labels = (
        "Evaluation ID", "Run ID", "Host", "Host version", "Model", "LoopPilot commit",
        "Skill loading mode", "Variant", "Trace author", "Reviewer", "Pair ID", "Arm ID",
    )
    for label in labels:
        text = re.sub(rf"(?m)^(-\s*{re.escape(label)}:\s*).+$", rf"\1[redacted]", text, flags=re.IGNORECASE)
    for identity in identities:
        if identity:
            text = text.replace(identity, "[redacted]")
    return text


def export_blind_review_packet(repository_root: Path, package_path: Path, blind_review_id: str, output: Path) -> Path:
    """Create an external, condition-redacted reviewer packet from a run's public evidence."""
    repository_root = Path(repository_root).resolve()
    package_path = Path(package_path).resolve()
    _output_outside_root(repository_root, output)
    if not package_path.is_relative_to(repository_root) or not package_path.is_dir():
        raise ValueError("review packet source must be a package inside the repository")
    if not re.fullmatch(r"BLIND-[A-Za-z0-9-]{1,99}", blind_review_id):
        raise ValueError("blind_review_id is invalid")
    if Path(output).exists():
        raise ValueError("review packet output already exists")

    from evaluation_evidence_validation import Reader, _check_digest, _inside

    reader = Reader()
    run_path = _inside(package_path, "run.json")
    run = reader.json(run_path)
    if not isinstance(run, dict) or not isinstance(run.get("evidence"), dict):
        raise ValueError("review packet source has no valid run evidence map")
    identities = [
        run.get(key, "") for key in
        ("run_id", "evaluation_id", "host", "host_version", "model", "commit", "trace_author")
    ]
    withheld_tokens = ("lineage", "boundary", "loading-observation", "review.json")
    withheld = sorted(path for path in run["evidence"] if any(token in path.casefold() for token in withheld_tokens))
    source_paths = {"environment.md", "prompt.md", "trace.md", run.get("scenario_path"), run.get("trace_path"), *run["evidence"]}
    source_paths.discard(None)
    source_records = []
    output = Path(output).absolute()
    output.mkdir(parents=True, exist_ok=False)
    artifact_root = output / "artifacts"
    artifact_root.mkdir()
    for relative in sorted(source_paths):
        if relative in withheld or relative == "score.md":
            continue
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or "\\" in relative:
            raise ValueError("review packet source path is not package-relative")
        source = _inside(package_path, relative)
        if not source.is_file():
            raise ValueError(f"review packet source file is missing: {relative}")
        _require_size = source.stat().st_size <= 8 * 1024 * 1024
        if not _require_size:
            raise ValueError(f"review packet source file exceeds size limit: {relative}")
        original = source.read_bytes()
        expected = run["scenario_sha256"] if relative == run.get("scenario_path") else run["trace_sha256"] if relative == run.get("trace_path") else run["evidence"].get(relative)
        if expected is not None:
            _check_digest(reader, source, expected, "review packet source")
        packet_bytes = original
        try:
            content = original.decode("utf-8-sig")
        except UnicodeError:
            content = None
        if content is not None:
            if relative.endswith(".json"):
                try:
                    parsed = json.loads(content)
                    content = json.dumps(_blind_value(parsed, identities), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
                except (TypeError, ValueError):
                    content = _blind_text(content, identities)
            elif relative.endswith(".jsonl"):
                lines = []
                for line in content.splitlines():
                    if not line.strip():
                        continue
                    try:
                        event = json.loads(line)
                    except ValueError:
                        lines.append(_blind_text(line, identities))
                        continue
                    if any(token in str(event.get("artifact", "")).casefold() for token in withheld_tokens):
                        continue
                    lines.append(json.dumps(_blind_value(event, identities), ensure_ascii=False, sort_keys=True))
                content = "\n".join(lines) + "\n"
            else:
                content = _blind_text(content, identities)
            packet_bytes = content.encode("utf-8")
        destination = artifact_root.joinpath(*pure.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(packet_bytes)
        source_records.append({
            "source_path": relative,
            "source_sha256": hashlib.sha256(original).hexdigest(),
            "packet_path": destination.relative_to(output).as_posix(),
            "packet_sha256": hashlib.sha256(packet_bytes).hexdigest(),
            "redacted": packet_bytes != original,
        })

    from evaluation_evidence_validation import DIMENSIONS
    score_rows = "\n".join(f"| {name} |  |  |" for name in DIMENSIONS)
    (output / "review-score-sheet.md").write_text(
        "# Independent Blind Review Score Sheet\n\n"
        f"Blind review ID: {blind_review_id}\n\n"
        "Score only from the packet evidence. Record the score and event/artifact evidence before guessing the run condition.\n\n"
        "| Dimension | Score | Evidence |\n| --- | ---: | --- |\n" + score_rows + "\n",
        encoding="utf-8", newline="\n",
    )
    packet_sections = [
        "# Blind Review Packet",
        "",
        f"Blind review ID: {blind_review_id}",
        "",
        "Identity and lineage metadata are withheld. Task content or public trace text may still reveal the run condition.",
        "",
    ]
    for record in source_records:
        packet_file = output / record["packet_path"]
        try:
            artifact_text = packet_file.read_text(encoding="utf-8")
            longest_ticks = max((len(match.group(0)) for match in re.finditer(r"`+", artifact_text)), default=0)
            fence = "`" * max(3, longest_ticks + 1)
            packet_sections.extend([f"## {record['packet_path']}", "", fence, artifact_text.rstrip("\n"), fence, ""])
        except UnicodeError:
            artifact_base64 = base64.b64encode(packet_file.read_bytes()).decode("ascii")
            packet_sections.extend([f"## {record['packet_path']} (base64)", "", "```text", artifact_base64, "```", ""])
    packet_sections.extend(["## Independent reviewer score sheet", "", (output / "review-score-sheet.md").read_text(encoding="utf-8").rstrip(), ""])
    packet_path = output / "blind-review-packet.md"
    packet_path.write_text("\n".join(packet_sections), encoding="utf-8", newline="\n")
    manifest = {
        "schema_version": 1,
        "kind": "blind-review-packet-manifest",
        "blind_review_id": blind_review_id,
        "package_identity_redacted": True,
        "condition_assignment_withheld": True,
        "source_artifacts": source_records,
        "packet_path": "blind-review-packet.md",
        "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "withheld_until_unblinding": withheld,
        "limitations": "Task content or public trace text may still reveal the condition; blinding is not guaranteed against inference.",
    }
    _dump_json(output / "manifest.json", manifest)
    (output / "README.md").write_text(
        "# Blind Review Packet\n\n"
        f"Blind review ID: {blind_review_id}\n\n"
        "Review `blind-review-packet.md`, complete the score sheet inside it, then record a condition guess before unblinding. "
        "Identity and lineage metadata are withheld; task content may still reveal the condition.\n",
        encoding="utf-8", newline="\n",
    )
    return output


def prepare_blind_plan(
    root: Path,
    experiment_id: str,
    reviewer_gate: dict | None = None,
    reviewer_gate_sha256: str | None = None,
) -> dict:
    """Create a randomized run order and blind IDs for an external review store."""
    errors = validate_behavior_matrices(root)
    if errors:
        raise ValueError("; ".join(errors))
    if reviewer_gate is not None or reviewer_gate_sha256 is not None:
        gate_errors = reviewer_gate_errors(reviewer_gate, experiment_id)
        if not isinstance(reviewer_gate_sha256, str) or re.fullmatch(r"[0-9a-f]{64}", reviewer_gate_sha256) is None:
            gate_errors.append("reviewer readiness SHA-256 pin is invalid")
        if gate_errors:
            raise ValueError("; ".join(sorted(set(gate_errors))))
    internal_keys = _historical_keys(Path(root)) + _formal_keys(Path(root))
    rng = secrets.SystemRandom()
    historical = _load_json(Path(root) / HISTORICAL_MATRIX_PATH)
    pairs = [pair["pair_id"] for pair in historical["pairs"]]
    rng.shuffle(pairs)
    run_order = []
    for pair_id in pairs:
        pair_arms = [f"historical:{pair_id}:control", f"historical:{pair_id}:skill_loaded"]
        rng.shuffle(pair_arms)
        run_order.extend(pair_arms)
    run_order.extend(_current_run_order(rng))
    token = re.sub(r"[^A-Za-z0-9]+", "-", experiment_id).strip("-") or "EXPERIMENT"
    assignments = {}
    for index, internal_key in enumerate(internal_keys, start=1):
        random_suffix = secrets.token_hex(6)
        assignments[internal_key] = f"BLIND-{token}-{index:02d}-{random_suffix}"
    return {
        "schema_version": 1,
        "kind": "two-stage-behavior-validation-blind-plan",
        "experiment_id": experiment_id,
        "historical_primary_runs": 14,
        "current_primary_runs": 4,
        "primary_run_count": EXPECTED_PRIMARY_RUNS,
        "reviewer_gate": {
            "required": True,
            "status": "ready" if reviewer_gate is not None and reviewer_gate_sha256 else "pending",
            "blind_review": True,
            "operator_id": reviewer_gate.get("operator_id") if isinstance(reviewer_gate, dict) else None,
            "operator_session_id": reviewer_gate.get("operator_session_id") if isinstance(reviewer_gate, dict) else None,
            "reviewer_operator_id": reviewer_gate.get("reviewer_operator_id") if isinstance(reviewer_gate, dict) else None,
            "reviewer_session_id": reviewer_gate.get("reviewer_session_id") if isinstance(reviewer_gate, dict) else None,
            "receipt_sha256": reviewer_gate_sha256,
        },
        "run_order": run_order,
        "assignments": assignments,
        "historical_lineage": HISTORICAL_MATRIX_PATH,
        "current_matrix": CURRENT_ACCEPTANCE_MATRIX_PATH,
        "mapping_sha256": _digest(assignments),
    }


def prepare_codex_replication_blind_plan(
    root: Path,
    experiment_id: str,
    reviewer_gate: dict,
    reviewer_gate_sha256: str,
    index_authority: dict,
    index_authority_sha256: str,
) -> dict:
    """Create a randomized plan for Codex replication plus current formal arms.

    `index_authority` must already have been loaded by the pinned external
    authority reader; this function validates its experiment binding again.
    """
    errors = validate_behavior_matrices(root)
    if errors:
        raise ValueError("; ".join(errors))
    gate_errors = reviewer_gate_errors(reviewer_gate, experiment_id)
    if not isinstance(reviewer_gate_sha256, str) or re.fullmatch(r"[0-9a-f]{64}", reviewer_gate_sha256) is None:
        gate_errors.append("reviewer readiness SHA-256 pin is invalid")
    authority_keys = {"schema_version", "kind", "experiment_id", "operator_id", "evidence_index_path", "approved_at"}
    if not isinstance(index_authority, dict) or set(index_authority) != authority_keys:
        gate_errors.append("evidence-index authority schema is invalid")
    else:
        if index_authority.get("schema_version") != 1 or index_authority.get("kind") != "codex-evidence-index-authority":
            gate_errors.append("evidence-index authority kind/version is invalid")
        if index_authority.get("experiment_id") != experiment_id:
            gate_errors.append("evidence-index authority experiment ID mismatch")
    if not isinstance(index_authority_sha256, str) or re.fullmatch(r"[0-9a-f]{64}", index_authority_sha256) is None:
        gate_errors.append("evidence-index authority SHA-256 pin is invalid")
    if gate_errors:
        raise ValueError("; ".join(sorted(set(gate_errors))))

    matrix = _load_json(Path(root) / CODEX_REPLICATION_MATRIX_PATH)
    pair_ids = [pair["pair_id"] for pair in matrix["pairs"]]
    rng = secrets.SystemRandom()
    rng.shuffle(pair_ids)
    run_order = []
    for pair_id in pair_ids:
        pair_arms = [f"replication:{pair_id}:control", f"replication:{pair_id}:skill_loaded"]
        rng.shuffle(pair_arms)
        run_order.extend(pair_arms)
    run_order.extend(_current_run_order(rng))

    internal_keys = _codex_replication_keys(Path(root)) + _formal_keys(Path(root))
    token = re.sub(r"[^A-Za-z0-9]+", "-", experiment_id).strip("-") or "EXPERIMENT"
    assignments = {
        key: f"BLIND-{token}-{index:02d}-{secrets.token_hex(6)}"
        for index, key in enumerate(internal_keys, start=1)
    }
    plan = {
        "schema_version": 1,
        "kind": "codex-replication-validation-blind-plan",
        "experiment_id": experiment_id,
        "replication_primary_runs": 14,
        "current_primary_runs": 4,
        "primary_run_count": 18,
        "reviewer_gate": {
            "required": True,
            "status": "ready",
            "blind_review": True,
            "operator_id": reviewer_gate["operator_id"],
            "operator_session_id": reviewer_gate["operator_session_id"],
            "reviewer_operator_id": reviewer_gate["reviewer_operator_id"],
            "reviewer_session_id": reviewer_gate["reviewer_session_id"],
            "receipt_sha256": reviewer_gate_sha256,
        },
        "index_authority": {
            "required": True,
            "status": "fixed",
            "operator_id": index_authority["operator_id"],
            "evidence_index_path": index_authority["evidence_index_path"],
            "sha256": index_authority_sha256,
        },
        "run_order": run_order,
        "assignments": assignments,
        "replication_matrix": CODEX_REPLICATION_MATRIX_PATH,
        "current_matrix": CURRENT_ACCEPTANCE_MATRIX_PATH,
        "mapping_sha256": _digest(assignments),
    }
    plan_errors = validate_codex_replication_blind_plan(root, plan)
    if plan_errors:
        raise ValueError("; ".join(plan_errors))
    return plan


def validate_codex_replication_blind_plan(root: Path, plan: dict) -> list[str]:
    errors = validate_behavior_matrices(root)
    expected = set(_codex_replication_keys(Path(root)) + _formal_keys(Path(root)))
    assignments = plan.get("assignments", {}) if isinstance(plan, dict) else {}
    order = plan.get("run_order", []) if isinstance(plan, dict) else []
    if plan.get("kind") != "codex-replication-validation-blind-plan" or plan.get("primary_run_count") != 18:
        errors.append("Codex replication blind plan kind/run count invalid")
    if plan.get("replication_primary_runs") != 14 or plan.get("current_primary_runs") != 4:
        errors.append("Codex replication blind plan stage counts invalid")
    if set(assignments) != expected:
        errors.append("Codex blind assignments must cover fourteen replication and four current arms")
    if set(order) != expected or len(order) != len(expected):
        errors.append("Codex blind run_order must contain every primary run exactly once")
    blind_ids = list(assignments.values()) if isinstance(assignments, dict) else []
    if len(blind_ids) != len(set(blind_ids)):
        errors.append("Codex blind IDs must be unique")
    if plan.get("mapping_sha256") != _digest(assignments):
        errors.append("Codex blind mapping hash mismatch")
    reviewer_gate = plan.get("reviewer_gate", {})
    if reviewer_gate.get("required") is not True or reviewer_gate.get("blind_review") is not True or reviewer_gate.get("status") != "ready":
        errors.append("Codex reviewer gate must be ready before run-order generation")
    if (not reviewer_gate.get("operator_id") or not reviewer_gate.get("reviewer_operator_id")
            or reviewer_gate.get("operator_id") == reviewer_gate.get("reviewer_operator_id")
            or not reviewer_gate.get("operator_session_id") or not reviewer_gate.get("reviewer_session_id")
            or reviewer_gate.get("operator_session_id") == reviewer_gate.get("reviewer_session_id")):
        errors.append("Codex reviewer gate must name an independent Reviewer and session")
    index_authority = plan.get("index_authority", {})
    if index_authority.get("required") is not True or index_authority.get("status") != "fixed":
        errors.append("Codex evidence-index authority must be fixed before run-order generation")
    if not isinstance(index_authority.get("sha256"), str) or re.fullmatch(r"[0-9a-f]{64}", index_authority.get("sha256", "")) is None:
        errors.append("Codex evidence-index authority pin is invalid")
    if not reviewer_gate.get("receipt_sha256") or re.fullmatch(r"[0-9a-f]{64}", reviewer_gate.get("receipt_sha256", "")) is None:
        errors.append("Codex reviewer receipt pin is invalid")
    replication_matrix = _load_json(Path(root) / CODEX_REPLICATION_MATRIX_PATH)
    current_start = 14
    for pair in replication_matrix["pairs"]:
        control = f"replication:{pair['pair_id']}:control"
        loaded = f"replication:{pair['pair_id']}:skill_loaded"
        if control not in order or loaded not in order or abs(order.index(control) - order.index(loaded)) != 1:
            errors.append(f"Codex replication pair {pair['pair_id']} arms must be adjacent in randomized run_order")
    if any(not key.startswith("current:") for key in order[current_start:]):
        errors.append("all four current formal arms must follow the fourteen Codex replication runs")
    if "current:FL-1" in order and "current:FL-1R" in order and order.index("current:FL-1") > order.index("current:FL-1R"):
        errors.append("Codex run_order must place FL-1 before FL-1R")
    return sorted(set(errors))


def validate_blind_plan(root: Path, plan: dict) -> list[str]:
    errors = []
    errors.extend(validate_behavior_matrices(root))
    expected = set(_historical_keys(Path(root)) + _formal_keys(Path(root)))
    assignments = plan.get("assignments", {}) if isinstance(plan, dict) else {}
    order = plan.get("run_order", []) if isinstance(plan, dict) else []
    if set(assignments) != expected:
        errors.append("blind assignments must cover every one of the 18 primary runs")
    if set(order) != expected or len(order) != len(expected):
        errors.append("blind run_order must contain every primary run exactly once")
    blind_ids = list(assignments.values()) if isinstance(assignments, dict) else []
    if len(blind_ids) != len(set(blind_ids)):
        errors.append("blind IDs must be unique")
    if "current:FL-1" in order and "current:FL-1R" in order and order.index("current:FL-1") > order.index("current:FL-1R"):
        errors.append("run_order must place FL-1 before FL-1R")
    if plan.get("mapping_sha256") != _digest(assignments):
        errors.append("blind mapping hash mismatch")
    gate = plan.get("reviewer_gate", {})
    if gate.get("required") is not True or gate.get("blind_review") is not True:
        errors.append("reviewer gate must require anonymous blind review")
    if gate.get("status") != "ready" or not isinstance(gate.get("receipt_sha256"), str) or re.fullmatch(r"[0-9a-f]{64}", gate["receipt_sha256"]) is None:
        errors.append("reviewer readiness gate must be complete and externally hash-pinned before execution")
    if gate.get("operator_id") == gate.get("reviewer_operator_id") or gate.get("operator_session_id") == gate.get("reviewer_session_id") or not gate.get("reviewer_session_id"):
        errors.append("reviewer readiness gate must name an independent Reviewer and session")
    try:
        pair_ids = [pair["pair_id"] for pair in _load_json(Path(root) / HISTORICAL_MATRIX_PATH)["pairs"]]
        for pair_id in pair_ids:
            control = f"historical:{pair_id}:control"
            loaded = f"historical:{pair_id}:skill_loaded"
            if control not in order or loaded not in order or abs(order.index(control) - order.index(loaded)) != 1:
                errors.append(f"historical pair {pair_id} arms must be adjacent in randomized run_order")
        current_start = 14
        if any(not key.startswith("current:") for key in order[current_start:]):
            errors.append("all four current formal arms must follow the 14 historical replay runs")
    except (OSError, ValueError, TypeError, KeyError):
        errors.append("blind run_order cannot be checked against the historical matrix")
    return sorted(set(errors))


def _package_status(package: dict) -> str:
    run = package.get("run", {})
    incidents = package.get("incident_categories", [])
    lineage = package.get("lineage") or package.get("replication_lineage") or package.get("current_lineage") or {}
    if lineage.get("reproduction_status") == "not-reproduced":
        return "not-reproduced"
    if run.get("status") == "failed":
        return "infrastructure-interrupted" if incidents else "failed-run"
    if package.get("review", {}).get("decision") == "reject" or package.get("eligible") is False:
        return "behavior-failure-observed"
    if package.get("eligible") is True:
        return "complete"
    return "unverified"


def blind_assignment_errors(plan: dict, packages: list[dict]) -> list[str]:
    """Bind every run and Review receipt to the external randomized mapping."""
    errors = []
    assignments = plan.get("assignments", {}) if isinstance(plan, dict) else {}
    seen_blind_ids = set()
    seen_run_ids = set()
    for package in packages:
        kind = package.get("lineage_kind")
        lineage = package.get("current_lineage") or package.get("replication_lineage") or package.get("lineage") or {}
        if kind == "historical":
            key = f"historical:{lineage.get('pair_id')}:{lineage.get('arm')}"
        elif kind == "replication":
            key = f"replication:{lineage.get('pair_id')}:{lineage.get('arm')}"
        elif kind == "current":
            key = f"current:{lineage.get('arm_id')}"
        else:
            continue
        expected = assignments.get(key)
        run = package.get("run", {})
        review = package.get("review", {})
        actual = lineage.get("blind_review_id")
        if not expected:
            errors.append(f"blind plan has no assignment for {key}")
        elif actual != expected or review.get("blind_review_id") != expected:
            errors.append(f"run and Review blind IDs do not match the randomized assignment for {key}")
        run_id = run.get("run_id")
        if not run_id or run_id in seen_run_ids:
            errors.append("blind report packages must have unique observed run IDs")
        seen_run_ids.add(run_id)
        if actual:
            seen_blind_ids.add(actual)
    return sorted(set(errors))


def build_codex_replication_report(
    root: Path,
    packages: list[dict],
    blind_plan: dict,
    *,
    reviewer_ready: bool,
    evidence_index_authority_fixed: bool,
    current_preflight: dict,
    package_validation_errors: list[str] | None = None,
    reviewer_gate_errors: list[str] | None = None,
    external_index_errors: list[str] | None = None,
) -> dict:
    """Build a Codex-only replication report and a separate current gate view."""
    matrix_errors = validate_codex_replication_matrix(root)
    blind_errors = validate_codex_replication_blind_plan(root, blind_plan)
    assignment_errors = blind_assignment_errors(blind_plan, packages)
    package_validation_errors = list(package_validation_errors or [])
    reviewer_gate_errors = list(reviewer_gate_errors or [])
    if external_index_errors is None:
        external_index_errors = ["final approved evidence index was not validated"]
    else:
        external_index_errors = list(external_index_errors)

    gate = blind_plan.get("reviewer_gate", {}) if isinstance(blind_plan, dict) else {}
    reviewer_ready = bool(
        reviewer_ready and gate.get("status") == "ready" and not reviewer_gate_errors
    )
    authority_gate = bool(
        evidence_index_authority_fixed
        and blind_plan.get("index_authority", {}).get("status") == "fixed"
        and not blind_errors
    )
    final_index_gate = not external_index_errors
    replication_packages = [package for package in packages if package.get("lineage_kind") == "replication"]
    current_packages = [package for package in packages if package.get("lineage_kind") == "current"]
    from evaluation_evidence_validation import codex_replication_pair_errors, current_acceptance_pair_errors

    try:
        replication_pair_validation_errors = codex_replication_pair_errors(root, replication_packages)
    except (OSError, ValueError, TypeError, KeyError) as error:
        replication_pair_validation_errors = [f"Codex replication pair validation failed: {error}"]
    try:
        current_pair_errors = current_acceptance_pair_errors(root, current_packages)
    except (OSError, ValueError, TypeError, KeyError) as error:
        current_pair_errors = [f"current package validation could not load the matrix: {error}"]

    matrix = _load_json(Path(root) / CODEX_REPLICATION_MATRIX_PATH)
    replication_pairs = []
    required_replication_keys = set()
    for pair in matrix["pairs"]:
        members = [
            package for package in replication_packages
            if (package.get("replication_lineage") or {}).get("pair_id") == pair["pair_id"]
        ]
        by_arm = {
            arm: sorted(
                [package for package in members if (package.get("replication_lineage") or {}).get("arm") == arm],
                key=lambda package: (package.get("replication_lineage") or {}).get("attempt", 0),
            )
            for arm in ("control", "skill_loaded")
        }
        arms = {arm: attempts[-1] for arm, attempts in by_arm.items() if attempts}
        for arm in ("control", "skill_loaded"):
            required_replication_keys.add(f"replication:{pair['pair_id']}:{arm}")
        if set(arms) != {"control", "skill_loaded"}:
            status = "incomplete"
        elif any(_package_status(package) == "infrastructure-interrupted" for package in arms.values()):
            status = "infrastructure-interrupted"
        elif pair["evidence_type"] == "loading-probe" and any(
            arms[arm].get("loading_observation") not in {"loaded", "not-loaded", "not-observed"}
            for arm in ("control", "skill_loaded")
        ):
            status = "loading-observation-missing"
        elif pair["evidence_type"] == "loading-probe" and any(
            arms[arm].get("loading_observation") == "not-observed"
            for arm in ("control", "skill_loaded")
        ):
            status = "loading-probe-inconclusive"
        elif pair["evidence_type"] == "loading-probe" and all(
            arms[arm].get("loading_probe_eligible") for arm in ("control", "skill_loaded")
        ):
            status = "loading-probe-complete"
        elif pair["evidence_type"] == "loading-probe":
            status = "unverified"
        elif any(_package_status(package) == "behavior-failure-observed" for package in arms.values()):
            status = "behavior-failure-observed"
        elif all(_package_status(package) == "complete" for package in arms.values()):
            status = "complete"
        else:
            status = "unverified"
        incidents = sorted({incident for package in members for incident in package.get("incident_categories", [])})
        replication_pairs.append({
            "pair_id": pair["pair_id"],
            "source_evaluation_id": pair["source_evaluation_id"],
            "evidence_type": pair["evidence_type"],
            "status": status,
            "control_present": "control" in arms,
            "skill_loaded_present": "skill_loaded" in arms,
            "control_behavior_score_count": 0 if pair["evidence_type"] == "loading-probe" else int(bool(arms.get("control", {}).get("scores"))),
            "skill_loaded_behavior_score_count": 0 if pair["evidence_type"] == "loading-probe" else int(bool(arms.get("skill_loaded", {}).get("scores"))),
            "loading_observations": {
                arm: package.get("loading_observation") for arm, package in arms.items()
            } if pair["evidence_type"] == "loading-probe" else {},
            "behavioral_score_interpreted": pair["evidence_type"] == "behavior",
            "incidents": incidents,
            "claim_scope": "Codex-only",
        })

    observed_replication_keys = {
        f"replication:{(package.get('replication_lineage') or {}).get('pair_id')}:{(package.get('replication_lineage') or {}).get('arm')}"
        for package in replication_packages
    }
    replication_complete = (
        required_replication_keys <= observed_replication_keys
        and all(pair["status"] in {"complete", "behavior-failure-observed", "loading-probe-complete"} for pair in replication_pairs)
        and not assignment_errors
        and not package_validation_errors
        and not replication_pair_validation_errors
    )
    replication_status = "complete" if replication_complete else "incomplete"
    current_by_arm: dict[str, list[dict]] = {}
    for package in current_packages:
        lineage = package.get("current_lineage") or package.get("lineage") or {}
        arm_id = lineage.get("arm_id")
        if arm_id:
            current_by_arm.setdefault(arm_id, []).append(package)
    current_latest = {
        arm_id: max(attempts, key=lambda package: ((package.get("current_lineage") or package.get("lineage") or {}).get("attempt", 0)))
        for arm_id, attempts in current_by_arm.items()
    }
    current_matrix = _load_json(Path(root) / CURRENT_ACCEPTANCE_MATRIX_PATH)
    required_current = {f"current:{arm['arm_id']}" for arm in current_matrix["arms"]}
    current_keys = {f"current:{arm_id}" for arm_id in current_latest}
    preflight_ok = all(current_preflight.get(key) == value for key, value in (
        ("install_provenance", "CURRENT"), ("c2", "C2_CLEAN"), ("permissions", "pass")
    ))
    boundary_signatures = set()
    for package in [*replication_packages, *current_packages]:
        boundary = package.get("current_boundary")
        lineage = package.get("replication_lineage") or package.get("current_lineage") or package.get("lineage") or {}
        if boundary:
            boundary_signatures.add(json.dumps(boundary, sort_keys=True, separators=(",", ":")))
        if boundary and lineage.get("boundary_id") != boundary.get("boundary_id"):
            package_validation_errors.append("Codex/current lineage boundary_id differs from observed boundary")
    if len(boundary_signatures) > 1:
        package_validation_errors.append("Codex replication and current arms do not share one observed Host boundary")
    hard_gate_errors = (
        matrix_errors or blind_errors or assignment_errors or package_validation_errors
        or reviewer_gate_errors or external_index_errors
    )
    current_ready = bool(
        preflight_ok and reviewer_ready and authority_gate and final_index_gate
        and not hard_gate_errors and current_keys == required_current
        and all(_package_status(package) == "complete" for package in current_latest.values())
    )
    if current_ready:
        current_readiness = "ready-for-host-acceptance-record"
    elif not (preflight_ok and reviewer_ready and authority_gate and final_index_gate) or hard_gate_errors:
        current_readiness = "blocked"
    else:
        current_readiness = "incomplete"
    current_arm_results = []
    for arm in current_matrix["arms"]:
        package = current_latest.get(arm["arm_id"])
        current_arm_results.append({
            "arm_id": arm["arm_id"],
            "status": _package_status(package) if package else "uncompleted",
            "host_acceptance_dimension_ids": arm["dimension_ids"],
            "rubric_scores": package.get("scores", {}) if package else {},
            "blind_review_id": ((package.get("current_lineage") or package.get("lineage") or {}).get("blind_review_id")) if package else None,
        })
    return {
        "schema_version": 1,
        "kind": "codex-replication-experiment-report",
        "codex_replication": {
            "status": replication_status,
            "claim_scope": "Codex-only",
            "claims": "descriptive within-Codex comparisons only; results do not reproduce or establish Claude behavior",
            "primary_run_count": 14,
            "observed_arm_count": len(observed_replication_keys),
            "pairs": replication_pairs,
            "pair_validation_errors": replication_pair_validation_errors,
            "blind_assignment_errors": assignment_errors,
            "execution_infrastructure_incidents": sorted({incident for package in replication_packages for incident in package.get("incident_categories", [])}),
        },
        "historical_replay": {
            "status": "not-reproduced",
            "primary_run_count": 14,
            "observed_run_count": 0,
            "reason": "The original host was Claude Code; Codex replication packages are kept in a separate section and do not count as historical replay.",
        },
        "current_acceptance": {
            "readiness": current_readiness,
            "host_acceptance_verdict": "unverified",
            "may_claim_accepted": False,
            "acceptance_record_required": True,
            "required_arms": sorted(required_current),
            "observed_arms": sorted(current_keys),
            "preflight": current_preflight,
            "reviewer_ready": reviewer_ready,
            "evidence_index_authority_fixed": authority_gate,
            "final_approved_evidence_index_fixed": final_index_gate,
            "arm_results": current_arm_results,
            "pair_validation_errors": current_pair_errors,
            "package_validation_errors": package_validation_errors,
            "reviewer_gate_errors": reviewer_gate_errors,
            "external_index_errors": external_index_errors,
        },
        "gates": {
            "matrix_errors": matrix_errors,
            "blind_plan_errors": blind_errors,
            "blind_assignment_errors": assignment_errors,
            "reviewer_gate": reviewer_ready,
            "index_authority_gate": authority_gate,
            "final_evidence_index_gate": final_index_gate,
            "package_validation_gate": not package_validation_errors,
            "current_preflight_gate": preflight_ok,
        },
    }


def build_behavior_report(
    root: Path,
    packages: list[dict],
    blind_plan: dict,
    *,
    external_index_fixed: bool,
    reviewer_ready: bool,
    current_preflight: dict,
    package_validation_errors: list[str] | None = None,
    reviewer_gate_errors: list[str] | None = None,
    external_index_errors: list[str] | None = None,
) -> dict:
    """Build a conservative report from already validated package summaries."""
    matrix_errors = validate_behavior_matrices(root)
    blind_errors = validate_blind_plan(root, blind_plan)
    blind_assignment_error_list = blind_assignment_errors(blind_plan, packages)
    package_validation_errors = list(package_validation_errors or [])
    reviewer_gate_errors = list(reviewer_gate_errors or [])
    external_index_errors = list(external_index_errors or [])
    reviewer_gate = blind_plan.get("reviewer_gate", {}) if isinstance(blind_plan, dict) else {}
    reviewer_ready = bool(reviewer_ready and reviewer_gate.get("status") == "ready" and not blind_errors and not reviewer_gate_errors)
    historical_matrix = _load_json(Path(root) / HISTORICAL_MATRIX_PATH)
    historical_groups = []
    for pair in historical_matrix["pairs"]:
        members = [p for p in packages if p.get("lineage_kind") == "historical" and p.get("lineage", {}).get("pair_id") == pair["pair_id"]]
        by_arm = {
            arm: sorted(
                [p for p in members if p.get("lineage", {}).get("arm") == arm],
                key=lambda p: p.get("lineage", {}).get("attempt", 0),
            )
            for arm in ("control", "skill_loaded")
        }
        arms = {arm: attempts[-1] for arm, attempts in by_arm.items() if attempts}
        if set(arms) != {"control", "skill_loaded"}:
            status = "incomplete"
        elif any(_package_status(p) == "infrastructure-interrupted" for p in arms.values()):
            status = "infrastructure-interrupted"
        elif pair["evidence_type"] == "loading-probe" and any(p.get("loading_observation") not in {"loaded", "not-loaded", "not-observed"} for p in arms.values()):
            status = "loading-observation-missing"
        elif pair["evidence_type"] == "loading-probe" and any(p.get("loading_observation") == "not-observed" for p in arms.values()):
            status = "loading-probe-inconclusive"
        elif pair["evidence_type"] == "loading-probe" and all(p.get("loading_probe_eligible") or p.get("eligible") for p in arms.values()):
            status = "loading-probe-complete"
        elif pair["evidence_type"] == "loading-probe":
            status = "unverified"
        elif any(_package_status(p) == "behavior-failure-observed" for p in arms.values()):
            status = "behavior-failure-observed"
        elif all(_package_status(p) == "complete" for p in arms.values()):
            status = "complete"
        else:
            status = "unverified"
        incidents = sorted({incident for p in members for incident in p.get("incident_categories", [])})
        historical_groups.append({
            "pair_id": pair["pair_id"],
            "historical_evaluation_id": pair["historical_evaluation_id"],
            "evidence_type": pair.get("evidence_type", "behavior"),
            "status": status,
            "control_present": "control" in arms,
            "loaded_present": "skill_loaded" in arms,
            "control_score_count": 0 if pair["evidence_type"] == "loading-probe" else int(bool(arms.get("control", {}).get("scores"))),
            "loaded_score_count": 0 if pair["evidence_type"] == "loading-probe" else int(bool(arms.get("skill_loaded", {}).get("scores"))),
            "incidents": incidents,
            "loading_observations": {arm: value.get("loading_observation") for arm, value in arms.items()} if pair["evidence_type"] == "loading-probe" else {},
            "behavioral_score_interpreted": pair["evidence_type"] == "behavior",
        })

    current_packages = [p for p in packages if p.get("lineage_kind") == "current"]
    by_current_arm = {}
    for package in current_packages:
        lineage = package.get("current_lineage") or package.get("lineage") or {}
        arm_id = lineage.get("arm_id")
        if arm_id:
            by_current_arm.setdefault(arm_id, []).append(package)
    current_arms = {
        f"current:{arm_id}": max(attempts, key=lambda p: (p.get("current_lineage") or p.get("lineage") or {}).get("attempt", 0))
        for arm_id, attempts in by_current_arm.items()
    }
    required_current = {f"current:{arm}" for arm in EXPECTED_FORMAL_ARMS}
    current_keys = set(current_arms)
    preflight_ok = all(current_preflight.get(key) in {"CURRENT", "C2_CLEAN", "pass"} for key in ("install_provenance", "c2", "permissions"))
    from evaluation_evidence_validation import current_acceptance_pair_errors
    try:
        current_pair_errors = current_acceptance_pair_errors(root, current_packages) if not matrix_errors else ["current matrix is invalid; current arms cannot be summarized"]
    except (OSError, ValueError, TypeError, KeyError) as error:
        current_pair_errors = [f"current package validation could not load the matrix: {error}"]
    current_arms_ready = bool(
        not matrix_errors
        and not blind_errors
        and not current_pair_errors
        and not blind_assignment_error_list
        and not package_validation_errors
        and not external_index_errors
        and reviewer_ready
        and external_index_fixed
        and preflight_ok
        and current_keys == required_current
        and all(_package_status(package) == "complete" for package in current_arms.values())
    )
    current_failure = any(_package_status(package) == "behavior-failure-observed" for package in current_arms.values())
    current_verdict = "unverified"
    if current_arms_ready:
        readiness = "ready-for-host-acceptance-record"
    elif not preflight_ok or not reviewer_ready or not external_index_fixed or matrix_errors or blind_errors or blind_assignment_error_list or package_validation_errors or external_index_errors:
        readiness = "blocked"
    else:
        readiness = "incomplete"
    all_historical_arms = {key for key in _historical_keys(Path(root))}
    observed_historical_arms = {
        f"historical:{package.get('lineage', {}).get('pair_id')}:{package.get('lineage', {}).get('arm')}"
        for package in packages if package.get("lineage_kind") == "historical"
    }
    historical_capture_complete = all_historical_arms <= observed_historical_arms
    historical_behavior_complete = all(item["status"] in {"complete", "behavior-failure-observed"} for item in historical_groups if item["evidence_type"] == "behavior")
    historical_probes_complete = all(item["status"] == "loading-probe-complete" for item in historical_groups if item["evidence_type"] == "loading-probe")
    historical_status = (
        "complete" if historical_capture_complete and historical_behavior_complete and historical_probes_complete
        else "complete-with-infrastructure-interruptions" if historical_capture_complete and any(item["status"] == "infrastructure-interrupted" for item in historical_groups)
        else "incomplete"
    )
    historical_behavior_pairs = [item for item in historical_groups if item["evidence_type"] == "behavior"]
    historical_loading_probes = [item for item in historical_groups if item["evidence_type"] == "loading-probe"]
    current_matrix = _load_json(Path(root) / CURRENT_ACCEPTANCE_MATRIX_PATH)
    planned_dimension_details = {
        dimension: {
            "planned_arms": sorted(arm["arm_id"] for arm in current_matrix["arms"] if dimension in arm.get("dimension_ids", [])),
            "observed_arms": sorted(
                arm["arm_id"] for arm in current_matrix["arms"]
                if dimension in arm.get("dimension_ids", [])
                and f"current:{arm['arm_id']}" in current_arms
                and current_arms[f"current:{arm['arm_id']}"].get("run", {}).get("status") == "completed"
            ),
        }
        for dimension in range(1, 9)
    }
    planned_dimension_coverage = sorted(planned_dimension_details)
    current_arm_results = []
    current_incidents = set()
    current_incidents.update(incident for package in current_packages for incident in package.get("incident_categories", []))
    for arm_id in sorted(EXPECTED_FORMAL_ARMS):
        key = f"current:{arm_id}"
        package = current_arms.get(key)
        if package is None:
            current_arm_results.append({"arm_id": arm_id, "status": "uncompleted", "rubric_scores": {}, "code_quality": None, "incidents": []})
            continue
        incidents = sorted(package.get("incident_categories", []))
        current_incidents.update(incidents)
        current_arm_results.append({
            "arm_id": arm_id,
            "status": _package_status(package),
            "attempts": [
                {
                    "run_id": attempt.get("run", {}).get("run_id"),
                    "evaluation_id": attempt.get("run", {}).get("evaluation_id"),
                    "attempt": (attempt.get("current_lineage") or attempt.get("lineage") or {}).get("attempt"),
                    "status": attempt.get("run", {}).get("status"),
                    "exit_code": attempt.get("run", {}).get("exit_code"),
                    "incidents": sorted(attempt.get("incident_categories", [])),
                }
                for attempt in sorted(
                    by_current_arm.get(arm_id, []),
                    key=lambda item: (item.get("current_lineage") or item.get("lineage") or {}).get("attempt", 0),
                )
            ],
            "rubric_scores": package.get("scores", {}),
            "host_acceptance_dimension_ids": next(arm["dimension_ids"] for arm in current_matrix["arms"] if arm["arm_id"] == arm_id),
            "code_quality": {
                "applicability": package.get("code_quality_applicability"),
                "score": package.get("scores", {}).get("Code quality"),
            },
            "review_axes": package.get("review", {}).get("review_axes", {}),
            "blind_review_id": (package.get("current_lineage") or package.get("lineage") or {}).get("blind_review_id"),
            "reviewer_condition_guess": package.get("review", {}).get("condition_guess"),
            "reviewer_guess_confidence": package.get("review", {}).get("guess_confidence"),
            "incidents": incidents,
        })
    uncompleted_current_arms = [item["arm_id"] for item in current_arm_results if item["status"] not in {"complete", "behavior-failure-observed"}]
    return {
        "schema_version": 1,
        "kind": "two-stage-behavior-validation-report",
        "historical_replay": {
            "status": historical_status,
            "pairs": historical_groups,
            "primary_run_count": 14,
            "behaviorally_complete_pairs": sum(item["status"] in {"complete", "behavior-failure-observed"} for item in historical_groups),
            "behavior_pairs": historical_behavior_pairs,
            "loading_probes": historical_loading_probes,
            "execution_infrastructure_incidents": sorted({incident for item in historical_groups for incident in item["incidents"]}),
            "claims": "descriptive-only; one primary run per arm provides no variance or stable-effect estimate",
        },
        "current_acceptance": {
            "readiness": readiness,
            "host_acceptance_verdict": current_verdict,
            "may_claim_accepted": False,
            "acceptance_record_required": True,
            "required_arms": sorted(required_current),
            "observed_arms": sorted(current_keys),
            "preflight": current_preflight,
            "reviewer_ready": reviewer_ready,
            "external_index_fixed": external_index_fixed,
            "host_acceptance_dimension_coverage": planned_dimension_coverage,
            "host_acceptance_dimension_details": planned_dimension_details,
            "arm_results": current_arm_results,
            "uncompleted_arms": uncompleted_current_arms,
            "observed_behavior_failures": [item["arm_id"] for item in current_arm_results if item["status"] == "behavior-failure-observed"],
            "execution_infrastructure_incidents": sorted(current_incidents),
            "pair_validation_errors": current_pair_errors,
            "package_validation_errors": package_validation_errors,
            "reviewer_gate_errors": reviewer_gate_errors,
            "external_index_errors": external_index_errors,
            "expected_partial_ceiling_dimensions": current_matrix.get("expected_partial_ceiling_dimensions", []),
            "rubric_score_source": "run package score.md values; no automatic Host Acceptance verdict is inferred",
        },
        "gates": {
            "matrix_errors": matrix_errors,
            "blind_plan_errors": blind_errors,
            "blind_assignment_errors": blind_assignment_error_list,
            "reviewer_gate": reviewer_ready,
            "reviewer_gate_errors": reviewer_gate_errors,
            "external_index_gate": external_index_fixed,
            "external_index_errors": external_index_errors,
            "package_validation_gate": not package_validation_errors,
            "package_validation_errors": package_validation_errors,
            "current_preflight_gate": preflight_ok,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    design = sub.add_parser("validate-design")
    design.add_argument("--root", type=Path, default=Path.cwd())
    blind = sub.add_parser("prepare-blind")
    blind.add_argument("--root", type=Path, default=Path.cwd())
    blind.add_argument("--experiment-id", required=True)
    blind.add_argument("--reviewer-gate", type=Path, required=True, help="external reviewer-readiness receipt")
    blind.add_argument("--reviewer-gate-sha256", required=True, help="raw SHA-256 pin for the reviewer receipt")
    blind.add_argument("--output", type=Path, required=True)
    codex_blind = sub.add_parser("prepare-codex-replication-blind")
    codex_blind.add_argument("--root", type=Path, default=Path.cwd())
    codex_blind.add_argument("--experiment-id", required=True)
    codex_blind.add_argument("--reviewer-gate", type=Path, required=True, help="external reviewer-readiness receipt")
    codex_blind.add_argument("--reviewer-gate-sha256", required=True, help="raw SHA-256 pin for the reviewer receipt")
    codex_blind.add_argument("--index-authority", type=Path, required=True, help="external pinned evidence-index authority receipt")
    codex_blind.add_argument("--index-authority-sha256", required=True, help="raw SHA-256 pin for the evidence-index authority receipt")
    codex_blind.add_argument("--output", type=Path, required=True)
    report = sub.add_parser("report")
    report.add_argument("--root", type=Path, default=Path.cwd())
    report.add_argument("--blind-plan", type=Path, required=True)
    report.add_argument("--blind-plan-sha256", required=True)
    report.add_argument("--reviewer-gate", type=Path, required=True)
    report.add_argument("--reviewer-gate-sha256", required=True)
    report.add_argument("--evidence-index", type=Path, required=True)
    report.add_argument("--evidence-index-sha256", required=True)
    report.add_argument("--output", type=Path, required=True)
    codex_report = sub.add_parser("report-codex-replication")
    codex_report.add_argument("--root", type=Path, default=Path.cwd())
    codex_report.add_argument("--blind-plan", type=Path, required=True)
    codex_report.add_argument("--blind-plan-sha256", required=True)
    codex_report.add_argument("--reviewer-gate", type=Path, required=True)
    codex_report.add_argument("--reviewer-gate-sha256", required=True)
    codex_report.add_argument("--index-authority", type=Path, required=True)
    codex_report.add_argument("--index-authority-sha256", required=True)
    codex_report.add_argument("--evidence-index", type=Path, required=True)
    codex_report.add_argument("--evidence-index-sha256", required=True)
    codex_report.add_argument("--output", type=Path, required=True)
    export = sub.add_parser("export-blind")
    export.add_argument("--root", type=Path, default=Path.cwd())
    export.add_argument("--package", type=Path, required=True)
    export.add_argument("--blind-review-id", required=True)
    export.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "validate-design":
        errors = validate_behavior_matrices(args.root)
        if errors:
            for error in errors:
                print(error)
            return 1
        print("Behavior validation design is valid")
        return 0
    if args.command == "prepare-blind":
        _output_outside_root(args.root, args.output)
        mapping_path = args.output.with_name(args.output.stem + "-mapping.json")
        _output_outside_root(args.root, mapping_path)
        if args.output.exists() or mapping_path.exists():
            print("blind plan output or mapping already exists; choose a new path")
            return 1
        gate, gate_errors = load_pinned_reviewer_gate(args.root, args.reviewer_gate, args.reviewer_gate_sha256, args.experiment_id)
        if gate_errors:
            for error in gate_errors:
                print(error)
            return 1
        plan = prepare_blind_plan(args.root, args.experiment_id, gate, args.reviewer_gate_sha256)
        errors = validate_blind_plan(args.root, plan)
        if errors:
            for error in errors:
                print(error)
            return 1
        _dump_json(args.output, plan)
        _dump_json(mapping_path, {"assignments": plan["assignments"], "mapping_sha256": plan["mapping_sha256"]})
        print(json.dumps({
            "blind_plan": str(args.output),
            "blind_plan_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
            "mapping": str(mapping_path),
            "mapping_sha256": plan["mapping_sha256"],
        }, ensure_ascii=False))
        return 0
    if args.command == "prepare-codex-replication-blind":
        _output_outside_root(args.root, args.output)
        mapping_path = args.output.with_name(args.output.stem + "-mapping.json")
        _output_outside_root(args.root, mapping_path)
        if args.output.exists() or mapping_path.exists():
            print("Codex blind plan output or mapping already exists; choose a new path")
            return 1
        gate, gate_errors = load_pinned_reviewer_gate(args.root, args.reviewer_gate, args.reviewer_gate_sha256, args.experiment_id)
        if gate_errors:
            for error in gate_errors:
                print(error)
            return 1
        from evaluation_evidence_validation import load_external_evidence_index_authority as _load_authority_for_prepare
        authority, authority_errors = _load_authority_for_prepare(
            args.root, args.index_authority, args.index_authority_sha256, args.experiment_id
        )
        if authority_errors:
            for error in authority_errors:
                print(error)
            return 1
        plan = prepare_codex_replication_blind_plan(
            args.root, args.experiment_id, gate, args.reviewer_gate_sha256,
            authority, args.index_authority_sha256,
        )
        errors = validate_codex_replication_blind_plan(args.root, plan)
        if errors:
            for error in errors:
                print(error)
            return 1
        _dump_json(args.output, plan)
        _dump_json(mapping_path, {"assignments": plan["assignments"], "mapping_sha256": plan["mapping_sha256"]})
        print(json.dumps({
            "blind_plan": str(args.output),
            "blind_plan_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
            "mapping": str(mapping_path),
            "mapping_sha256": hashlib.sha256(mapping_path.read_bytes()).hexdigest(),
        }, ensure_ascii=False))
        return 0
    if args.command == "export-blind":
        try:
            packet = export_blind_review_packet(args.root, args.package, args.blind_review_id, args.output)
        except (OSError, ValueError, TypeError) as error:
            print(error)
            return 1
        print(packet)
        return 0
    if args.command == "report-codex-replication":
        plan, plan_errors = load_pinned_blind_plan(args.root, args.blind_plan, args.blind_plan_sha256)
        if plan_errors:
            for error in plan_errors:
                print(error)
            return 1
        try:
            from evaluation_evidence_validation import load_external_evidence_index_authority as _load_authority_for_report
            authority, authority_errors = _load_authority_for_report(
                args.root, args.index_authority, args.index_authority_sha256, plan.get("experiment_id", "")
            )
        except (OSError, ValueError, TypeError) as error:
            authority, authority_errors = {}, [str(error)]
        if authority_errors:
            for error in authority_errors:
                print(error)
            return 1
        plan_errors = validate_codex_replication_blind_plan(args.root, plan)
        plan_authority = plan.get("index_authority", {})
        if plan_authority.get("sha256") != args.index_authority_sha256:
            plan_errors.append("Codex blind plan index-authority digest differs from the pinned receipt")
        if plan_authority.get("evidence_index_path") != authority.get("evidence_index_path"):
            plan_errors.append("Codex blind plan evidence-index path differs from the pinned authority receipt")
        gate, reviewer_errors = load_pinned_reviewer_gate(
            args.root, args.reviewer_gate, args.reviewer_gate_sha256, plan.get("experiment_id", "")
        )
        reviewer_errors.extend(reviewer_gate_binding_errors(plan, gate, args.reviewer_gate_sha256))
        _output_outside_root(args.root, args.output)
        declared_index = Path(authority["evidence_index_path"]).resolve()
        supplied_index = Path(args.evidence_index).resolve()
        external_index_errors = []
        if supplied_index != declared_index:
            external_index_errors.append("final evidence index path differs from the pinned pre-run authority receipt")
        from evaluation_evidence_validation import validate_evaluation_evidence, validate_external_evidence_index

        external_index_errors.extend(validate_external_evidence_index(args.root, args.evidence_index, args.evidence_index_sha256))
        validated_packages = {}
        package_validation_errors = validate_evaluation_evidence(
            args.root, args.evidence_index, args.evidence_index_sha256, [], validated_packages=validated_packages
        )
        packages = list(validated_packages.values())
        boundaries = [
            package.get("current_boundary") for package in packages
            if package.get("current_boundary") is not None
        ]
        boundary = boundaries[0] if boundaries else {}
        current_preflight = {
            "install_provenance": boundary.get("install_provenance", "blocked"),
            "c2": boundary.get("c2_status", "blocked"),
            "permissions": boundary.get("permission_preflight", "not-run"),
        }
        result = build_codex_replication_report(
            args.root,
            packages,
            plan,
            reviewer_ready=not reviewer_errors,
            evidence_index_authority_fixed=not authority_errors and not plan_errors,
            current_preflight=current_preflight,
            package_validation_errors=package_validation_errors,
            reviewer_gate_errors=reviewer_errors,
            external_index_errors=external_index_errors,
        )
        if plan_errors:
            result["gates"]["blind_plan_errors"] = sorted(set(result["gates"]["blind_plan_errors"] + plan_errors))
            result["current_acceptance"]["readiness"] = "blocked"
        _dump_json(args.output, result)
        print(args.output)
        return 0 if result["codex_replication"]["status"] in {"complete", "complete-with-infrastructure-interruptions"} else 2
    plan, plan_errors = load_pinned_blind_plan(args.root, args.blind_plan, args.blind_plan_sha256)
    if plan_errors:
        for error in plan_errors:
            print(error)
        return 1
    gate, reviewer_errors = load_pinned_reviewer_gate(args.root, args.reviewer_gate, args.reviewer_gate_sha256, plan.get("experiment_id", ""))
    reviewer_errors.extend(reviewer_gate_binding_errors(plan, gate, args.reviewer_gate_sha256))
    _output_outside_root(args.root, args.output)
    from evaluation_evidence_validation import validate_evaluation_evidence, validate_external_evidence_index

    external_index_errors = validate_external_evidence_index(args.root, args.evidence_index, args.evidence_index_sha256)
    validated_packages = {}
    package_validation_errors = validate_evaluation_evidence(
        args.root,
        args.evidence_index,
        args.evidence_index_sha256,
        [],
        validated_packages=validated_packages,
    )
    packages = list(validated_packages.values())
    current_boundaries = [package.get("current_boundary") for package in packages if package.get("current_boundary")]
    current_boundary = current_boundaries[0] if current_boundaries and not external_index_errors else {}
    current_preflight = {
        "install_provenance": current_boundary.get("install_provenance", "blocked"),
        "c2": current_boundary.get("c2_status", "blocked"),
        "permissions": current_boundary.get("permission_preflight", "not-run"),
    }
    output = build_behavior_report(
        args.root,
        packages,
        plan,
        external_index_fixed=not external_index_errors and not package_validation_errors,
        reviewer_ready=not reviewer_errors,
        current_preflight=current_preflight,
        package_validation_errors=package_validation_errors,
        reviewer_gate_errors=reviewer_errors,
        external_index_errors=external_index_errors,
    )
    _dump_json(args.output, output)
    print(args.output)
    return 0 if output["current_acceptance"]["readiness"] == "ready-for-host-acceptance-record" else 2


if __name__ == "__main__":
    raise SystemExit(main())
