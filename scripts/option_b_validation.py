"""Validate the bounded Option B successor and the current RC designation."""

from __future__ import annotations

import hashlib
import re
import subprocess
from datetime import datetime
from pathlib import Path


OPTION_B_FILES = (
    "scripts/option_b_validation.py",
    "tests/test_option_b_successor.py",
    "tests/test_option_b_evidence.py",
    "tests/option_b_fixture.py",
    "docs/cross-host-acceptance.md",
    "docs/release/v1.0-rc-checklist.md",
    "docs/release/option-b-reference-successor.md",
    "docs/release/option-b-reference-approval.md",
    "docs/release/rc-candidate-reference.md",
    "docs/release/rc-candidate-decision.md",
    "evaluations/templates/host-acceptance-record.md",
    "evaluations/templates/environment.md",
    "scripts/evaluation_evidence_validation.py",
)

SUCCESSOR_ID = "OPTION-B-REFERENCE-2026-10-24"
SUCCESSOR_PATH = "docs/release/option-b-reference-successor.md"
REFERENCE_PATH = "docs/release/rc-candidate-reference.md"
DECISION_PATH = "docs/release/rc-candidate-decision.md"
ELIGIBLE_HOSTS = {"claude code", "codex"}
RC_VERSION = re.compile(r"^v\d+\.\d+\.\d+-rc\d+$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _metadata(text: str, location: str, errors: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("## "):
            break
        match = re.fullmatch(r"-[ \t]*([^:]+):[ \t]*(.*)", line)
        if not match:
            continue
        key, value = match.group(1).strip(), match.group(2).strip()
        if key in values:
            errors.append(f"{location}: duplicate metadata field {key!r}")
        values[key] = value
    return values


def _headings(text: str) -> set[str]:
    return {
        match.group(1).strip()
        for line in text.splitlines()
        if (match := re.match(r"^##[ \t]+(.+?)[ \t]*$", line))
    }


def _require(value: bool, message: str, errors: list[str]) -> None:
    if not value:
        errors.append(message)


def validate_option_b(root: Path, errors: list[str]) -> None:
    """Check policy and designation structure without claiming host acceptance."""
    root = Path(root)
    policy_path = root / SUCCESSOR_PATH
    approval_path = root / "docs/release/option-b-reference-approval.md"
    reference_path = root / REFERENCE_PATH
    decision_path = root / DECISION_PATH
    if not policy_path.is_file():
        errors.append(f"{SUCCESSOR_PATH}: required Option B successor policy is missing")
        return
    if not reference_path.is_file():
        errors.append(f"{REFERENCE_PATH}: required RC Reference designation is missing")
        return
    if not approval_path.is_file():
        errors.append("docs/release/option-b-reference-approval.md: bounded authorization record is missing")
        return
    if not decision_path.is_file():
        errors.append(f"{DECISION_PATH}: RC candidate decision is missing")
        return

    policy = policy_path.read_text(encoding="utf-8")
    policy_fields = _metadata(policy, SUCCESSOR_PATH, errors)
    policy_required = {
        "Successor ID": SUCCESSOR_ID,
        "Policy version": "option-b-successor-v1",
        "Reference Host choices": "Claude Code, Codex",
        "Gate 4 threshold": "unchanged",
        "Gate 5 disclosure": "unchanged",
        "Automatic Reference switching": "forbidden",
        "Historical verdict changes": "forbidden",
        "Standing authority": "none",
    }
    for field, expected in policy_required.items():
        _require(
            policy_fields.get(field, "").casefold() == expected.casefold(),
            f"{SUCCESSOR_PATH}: {field} must be {expected!r}",
            errors,
        )
    boundary = policy_fields.get("Effective boundary", "")
    _require(
        boundary == "the first commit containing this policy, approval record, validator, and regression tests",
        f"{SUCCESSOR_PATH}: effective boundary must name the first synchronized commit",
        errors,
    )
    _require(
        policy_fields.get("Authorization basis", "").casefold()
        == "one-time user authorization in the attached task dated 2026-10-24",
        f"{SUCCESSOR_PATH}: authorization basis must disclose the bounded task authorization",
        errors,
    )
    required_sections = {
        "C01 — Reference qualification",
        "C02 — Unique designation",
        "C03 — Designation timing",
        "C04 — Gate 4 binding",
        "C05 — Gate 5 and other Hosts",
        "C06 — Run and evidence binding",
        "C07 — Historical isolation",
        "C08 — Forward effectiveness",
    }
    missing = sorted(required_sections - _headings(policy))
    for heading in missing:
        errors.append(f"{SUCCESSOR_PATH}: missing requirement section {heading!r}")
    folded_policy = policy.casefold()
    for phrase in (
        "accepted-with-residuals",
        "candidate host",
        "before the first formal acceptance arm",
        "provider identity",
        "endpoint identity",
        "model identity",
        "commit and tree",
        "evidence index",
        "historical",
        "general f2 process",
    ):
        _require(
            phrase in folded_policy,
            f"{SUCCESSOR_PATH}: policy must explicitly preserve {phrase!r}",
            errors,
        )

    approval = approval_path.read_text(encoding="utf-8")
    approval_fields = _metadata(approval, "docs/release/option-b-reference-approval.md", errors)
    approval_expected = {
        "Decision ID": SUCCESSOR_ID,
        "Decision date": "2026-10-24",
        "Policy version": policy_fields.get("Policy version", ""),
        "RC-specific choice": "Codex for `v1.0.0-rc1`",
        "Gate 4 threshold": "unchanged",
        "Gate 5 disclosure": "unchanged",
        "Historical effect": "none",
        "Standing authority": "none",
    }
    for field, expected in approval_expected.items():
        _require(
            approval_fields.get(field, "").casefold() == expected.casefold(),
            f"docs/release/option-b-reference-approval.md: {field} must be {expected!r}",
            errors,
        )
    _require(
        approval_fields.get("Authorized action", "").casefold().startswith("implement a bounded, forward-effective successor"),
        "docs/release/option-b-reference-approval.md: authorized action must remain bounded to the successor",
        errors,
    )

    reference = reference_path.read_text(encoding="utf-8")
    fields = _metadata(reference, REFERENCE_PATH, errors)
    required = (
        "RC version",
        "Successor ID",
        "Reference designation ID",
        "Reference Host",
        "Other eligible Host",
        "Other Host role",
        "Designation state",
        "Designation date",
        "Formal acceptance arms at designation",
        "Reference host version",
        "Model identity",
        "Provider identity",
        "Endpoint identity",
        "Skill loading mode",
        "RC baseline commit",
        "RC baseline tree",
    )
    for field in required:
        _require(field in fields, f"{REFERENCE_PATH}: missing field {field!r}", errors)

    _require(
        bool(RC_VERSION.fullmatch(fields.get("RC version", ""))),
        f"{REFERENCE_PATH}: RC version must identify a versioned candidate",
        errors,
    )
    _require(
        fields.get("Successor ID") == SUCCESSOR_ID
        and fields.get("Successor policy") == SUCCESSOR_PATH,
        f"{REFERENCE_PATH}: designation must bind the Option B successor",
        errors,
    )
    designation_id = fields.get("Reference designation ID", "")
    _require(
        bool(re.fullmatch(r"RC\d+-REF-[A-Z0-9-]+", designation_id)),
        f"{REFERENCE_PATH}: Reference designation ID must be stable and RC-specific",
        errors,
    )
    reference_host = fields.get("Reference Host", "")
    _require(
        reference_host.casefold() in ELIGIBLE_HOSTS,
        f"{REFERENCE_PATH}: Reference Host must be Claude Code or Codex",
        errors,
    )
    if fields.get("RC version") == "v1.0.0-rc1":
        _require(reference_host == "Codex", f"{REFERENCE_PATH}: this RC is fixed to Codex", errors)
    _require(
        fields.get("Other eligible Host", "").casefold() in ELIGIBLE_HOSTS
        and fields.get("Other eligible Host", "").casefold() != reference_host.casefold(),
        f"{REFERENCE_PATH}: other eligible Host must be the distinct remaining eligible Host",
        errors,
    )
    _require(
        fields.get("Other Host role", "").casefold().startswith("candidate")
        and "unverified" in fields.get("Other Host role", "").casefold(),
        f"{REFERENCE_PATH}: non-Reference eligible Host must retain Candidate/unverified disclosure",
        errors,
    )
    state = fields.get("Designation state", "").casefold()
    _require(
        state in {"preflight-designation", "finalized-before-acceptance"},
        f"{REFERENCE_PATH}: unknown designation lifecycle state {state!r}",
        errors,
    )
    _require(
        bool(ISO_DATE.fullmatch(fields.get("Designation date", ""))),
        f"{REFERENCE_PATH}: Designation date must use YYYY-MM-DD",
        errors,
    )
    arms = fields.get("Formal acceptance arms at designation", "").casefold()
    if state == "preflight-designation":
        _require(
            arms == "none",
            f"{REFERENCE_PATH}: no formal arms may have started before designation is committed",
            errors,
        )
        for field in ("Reference host version", "Model identity", "Provider identity", "Endpoint identity", "Skill loading mode"):
            _require(
                fields.get(field, "").casefold() in {"unknown", "not observed"},
                f"{REFERENCE_PATH}: {field} must remain explicitly unknown until observed",
                errors,
            )
        for field in ("RC baseline commit", "RC baseline tree"):
            _require(
                fields.get(field, "").casefold() == "pending-before-formal-run",
                f"{REFERENCE_PATH}: {field} must be set from the committed RC baseline before any formal run",
                errors,
            )
    else:
        try:
            instant = datetime.fromisoformat(fields.get("Finalized at", ""))
            if instant.tzinfo is None:
                raise ValueError("missing timezone")
        except ValueError:
            errors.append(f"{REFERENCE_PATH}: finalized designation requires a timezone-aware ISO timestamp")
        _require(arms == "none", f"{REFERENCE_PATH}: no formal arms may have started at finalization", errors)
        for field in ("Reference host version", "Model identity", "Provider identity", "Endpoint identity", "Skill loading mode",
                      "Configured model", "Configured provider", "Configured endpoint"):
            _require(
                fields.get(field, "").casefold() not in {"unknown", "not observed", "none", "todo", ""},
                f"{REFERENCE_PATH}: finalized designation requires observed {field}",
                errors,
            )
        for field in ("RC baseline commit", "RC baseline tree"):
            _require(
                bool(SHA1.fullmatch(fields.get(field, ""))),
                f"{REFERENCE_PATH}: finalized designation requires a concrete {field}",
                errors,
            )
    decision = _metadata(decision_path.read_text(encoding="utf-8"), DECISION_PATH, errors)
    for field, expected in {
        "RC version": fields.get("RC version"),
        "Successor ID": SUCCESSOR_ID,
        "Reference designation record": REFERENCE_PATH,
        "Reference Host": reference_host,
        "Decision state": "candidate-prepared-not-release-ready",
        "Gate 4": "unmet",
        "Gate 5": "all-named-candidates-recorded-or-disclosed-unverified",
        "Acceptance status": "not-run",
        "Host/model identity status": "unverified",
        "Release tag": "not-created",
    }.items():
        _require(decision.get(field, "").casefold() == expected.casefold(),
                 f"{DECISION_PATH}: {field} must be {expected!r}", errors)


def reference_designation_fields(root: Path) -> dict[str, str]:
    """Read the current public RC designation fields for record/package binding."""
    path = Path(root) / REFERENCE_PATH
    if not path.is_file():
        return {}
    return _metadata(path.read_text(encoding="utf-8"), REFERENCE_PATH, [])


def _check(condition, message):
    if not condition:
        raise ValueError(message)


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "--no-replace-objects", *args], cwd=root, capture_output=True, timeout=15)
    _check(result.returncode == 0, "RC Git boundary is missing, foreign, or inconsistent")
    return result.stdout


def _time(value, label):
    _check(isinstance(value, str), f"{label} timestamp invalid")
    instant = datetime.fromisoformat(value)
    _check(instant.tzinfo is not None, f"{label} timestamp requires a timezone")
    return instant


def validate_option_b_run_binding(root, run, events, evidence, errors, read_bytes=None):
    """Fail closed on a formal RC binding; capture truth remains trusted review work."""
    try:
        _validate_rc_binding(Path(root).resolve(), run, events, evidence, read_bytes)
    except (ValueError, OSError, UnicodeError, subprocess.SubprocessError) as error:
        errors.append(str(error))


def _validate_rc_binding(root, run, events, evidence, read_bytes):
    binding = run.get("rc_binding")
    keys = {
        "rc_version", "successor_id", "successor_policy", "policy_sha256",
        "designation_id", "designation_record", "designation_sha256", "designation_commit",
        "reference_host", "evidence_role", "effective_successor_commit", "effective_successor_tree",
        "run_commit", "run_tree",
    }
    _check(isinstance(binding, dict) and set(binding) == keys, "Option B RC binding schema keys invalid")
    for key in keys:
        _check(isinstance(binding[key], str) and binding[key].strip() == binding[key] and binding[key],
               f"RC binding {key} requires canonical text; Git SHA fields must be strings")
    for key in ("effective_successor_commit", "effective_successor_tree", "designation_commit", "run_commit", "run_tree"):
        _check(SHA1.fullmatch(binding[key]), f"RC binding {key} must be a 40-character Git SHA")
    for key in ("policy_sha256", "designation_sha256"):
        _check(SHA256.fullmatch(binding[key]), f"RC binding {key} digest invalid")
    _check(binding["successor_id"] == SUCCESSOR_ID and binding["successor_policy"] == SUCCESSOR_PATH,
           "RC run does not bind the Option B successor")
    _check(binding["designation_record"] == REFERENCE_PATH, "RC designation record path mismatch")
    _check(binding["evidence_role"] in {"reference", "candidate"}, "RC evidence role invalid")

    # The recorded Git snapshot, rather than a mutable current-RC pointer, preserves
    # older RC designations when a later RC is prepared at the same public path.
    designation_bytes = _git(root, "show", binding["designation_commit"] + ":" + REFERENCE_PATH)
    _check(hashlib.sha256(designation_bytes).hexdigest() == binding["designation_sha256"],
           "RC receipt does not match the committed designation digest")
    metadata_errors = []
    fields = _metadata(designation_bytes.decode("utf-8"), REFERENCE_PATH, metadata_errors)
    _check(not metadata_errors, "; ".join(metadata_errors))
    current = reference_designation_fields(root)
    if current.get("RC version") == binding["rc_version"]:
        current_bytes = read_bytes(root / REFERENCE_PATH) if read_bytes else (root / REFERENCE_PATH).read_bytes()
        _check(current_bytes == designation_bytes, "current RC differs from its committed designation")
    for label, key in (("RC version", "rc_version"), ("Successor ID", "successor_id"),
                       ("Successor policy", "successor_policy"), ("Reference designation ID", "designation_id"),
                       ("Reference Host", "reference_host")):
        _check(fields.get(label) == binding[key], f"RC designation {label} mismatch")
    _check(fields.get("Designation state") == "finalized-before-acceptance",
           "RC formal run requires a finalized pre-arm designation")
    _check(fields.get("Formal acceptance arms at designation") == "none",
           "RC designation cannot follow an already started formal arm")
    _check(fields.get("Reference Host", "").casefold() in ELIGIBLE_HOSTS, "RC Reference Host ineligible")
    _check(fields.get("Policy version") == "option-b-successor-v1", "RC policy version mismatch")
    _check(RC_VERSION.fullmatch(binding["rc_version"]), "RC version invalid")
    if binding["rc_version"] == "v1.0.0-rc1":
        _check(binding["reference_host"] == "Codex", "this RC is fixed to Codex")
    history = _git(root, "log", "--format=%H", "HEAD", "--", REFERENCE_PATH).decode().splitlines()
    frozen_keys = ("Reference Host", "Reference designation ID", "Successor ID", "Policy version",
                   "Reference host version", "Model identity", "Provider identity", "Endpoint identity",
                   "Configured model", "Configured provider", "Configured endpoint", "Skill loading mode",
                   "RC baseline commit", "RC baseline tree", "Finalized at")
    for commit in history:
        prior_errors = []
        prior = _metadata(_git(root, "show", commit + ":" + REFERENCE_PATH).decode("utf-8"), REFERENCE_PATH, prior_errors)
        _check(not prior_errors, "duplicate RC designation metadata in Git history")
        if prior.get("RC version") != binding["rc_version"]:
            continue
        _check(prior.get("Reference Host") == fields.get("Reference Host")
               and prior.get("Reference designation ID") == fields.get("Reference designation ID"),
               "Reference choice is immutable for the same RC")
        if prior.get("Designation state") == "finalized-before-acceptance":
            _check(all(prior.get(key) == fields.get(key) for key in frozen_keys),
                   "RC finalized combination is immutable for the same RC")
    for label, key in (("RC baseline commit", "run_commit"), ("RC baseline tree", "run_tree")):
        _check(fields.get(label) == binding[key], f"RC designation {label} mismatch")
    _check(binding["run_commit"] == run.get("commit"), "RC binding/run commit mismatch")
    for commit, tree in ((binding["run_commit"], binding["run_tree"]),
                         (binding["effective_successor_commit"], binding["effective_successor_tree"])):
        _check(_git(root, "cat-file", "-t", commit).strip() == b"commit", "RC Git boundary is not a commit")
        _check(_git(root, "rev-parse", commit + "^{tree}").decode().strip() == tree,
               "RC Git tree does not match its commit")
    _git(root, "merge-base", "--is-ancestor", binding["effective_successor_commit"], binding["run_commit"])
    _git(root, "merge-base", "--is-ancestor", binding["run_commit"], binding["designation_commit"])
    _git(root, "merge-base", "--is-ancestor", binding["designation_commit"], "HEAD")

    boundary_files = (SUCCESSOR_PATH, "docs/release/option-b-reference-approval.md",
                      "scripts/option_b_validation.py", "scripts/cross_host_acceptance_validation.py",
                      "scripts/evaluation_evidence_validation.py", "scripts/validate.py",
                      "tests/test_option_b_successor.py", "tests/test_option_b_evidence.py")
    effective = binding["effective_successor_commit"]
    for name in boundary_files:
        _git(root, "cat-file", "-e", effective + ":" + name)
    parents = _git(root, "rev-list", "--parents", "-n", "1", effective).decode().split()[1:]
    for parent in parents:
        complete = all(subprocess.run(["git", "--no-replace-objects", "cat-file", "-e", parent + ":" + name],
                       cwd=root, capture_output=True, timeout=15).returncode == 0 for name in boundary_files)
        _check(not complete, "effective boundary is not the first synchronized successor commit")
    policy = _git(root, "show", effective + ":" + SUCCESSOR_PATH)
    _check(hashlib.sha256(policy).hexdigest() == binding["policy_sha256"], "effective successor policy digest mismatch")
    baseline_policy = _git(root, "show", binding["run_commit"] + ":" + SUCCESSOR_PATH)
    _check(policy == baseline_policy, "RC baseline uses a different successor policy")
    started = _time(run.get("started_at"), "formal arm")
    finalized = _time(fields.get("Finalized at"), "designation")
    committed = _time(_git(root, "show", "-s", "--format=%cI", binding["designation_commit"]).decode().strip(), "designation commit")
    effective_time = _time(_git(root, "show", "-s", "--format=%cI", effective).decode().strip(), "effective successor")
    _check(effective_time <= finalized <= committed < started,
           "RC designation must be finalized and committed before the formal arm")

    identity = run.get("runtime_identity")
    _check(isinstance(identity, dict) and set(identity) == {"configured", "observed", "event_ids"},
           "RC runtime identity schema keys invalid")
    expected = {"configured": {"provider", "model", "endpoint"},
                "observed": {"host_version", "provider", "model", "endpoint"}}
    for section, names in expected.items():
        values = identity[section]
        _check(isinstance(values, dict) and set(values) == names, f"RC runtime identity {section} fields invalid")
        for name, value in values.items():
            _check(isinstance(value, str) and value.strip() == value and value
                   and value.casefold() not in {"unknown", "not observed", "none", "todo", "n/a"},
                   f"RC runtime identity {section} {name} must be explicitly observed/disclosed")
    observed = identity["observed"]
    _check(run.get("host_version") == observed["host_version"], "RC receipt/observed host_version mismatch")
    _check(run.get("model") == observed["model"], "RC receipt/observed model mismatch")
    if binding["evidence_role"] == "reference":
        _check(run.get("host") == binding["reference_host"], "RC run host is not the designated Reference Host")
        for label, value in (("Reference host version", observed["host_version"]), ("Model identity", observed["model"]),
                             ("Provider identity", observed["provider"]), ("Endpoint identity", observed["endpoint"]),
                             ("Skill loading mode", run.get("loading_mode")),
                             *(("Configured " + key, value) for key, value in identity["configured"].items())):
            _check(fields.get(label) == value, f"RC designation {label} mismatch")
    else:
        _check(run.get("host") != binding["reference_host"], "selected Reference cannot be relabelled Candidate")
    event_ids = identity["event_ids"]
    _check(isinstance(event_ids, dict) and set(event_ids) == expected["observed"],
           "RC runtime identity observation events must cover host_version, provider, model, and endpoint")
    payload_keys = {"schema_version", "kind", "run_id", "observed_at", "basis", "identity", "source_artifact", "source_sha256"}
    for name, event_id in event_ids.items():
        _check(isinstance(event_id, str), f"RC runtime {name} observation event ID invalid")
        event = events.get(event_id)
        _check(isinstance(event, dict) and event.get("kind") == "observation",
               f"RC runtime {name} identity lacks a recorded observation event")
        _check(event.get("artifact") in evidence, "identity observation is not in the run evidence map")
        payload = event.get("payload")
        _check(isinstance(payload, dict) and set(payload) == payload_keys, "RC identity observation artifact schema invalid")
        _check(type(payload["schema_version"]) is int and payload["schema_version"] == 1
               and payload["kind"] == "runtime-identity", "RC identity observation schema version/kind invalid")
        _check(payload["basis"] == "actual-runtime-observation", "identity requires actual-runtime-observation basis")
        _check(payload["run_id"] == run.get("run_id"), "identity observation run mismatch")
        actual = payload["identity"]
        _check(isinstance(actual, dict) and set(actual) == {"host", *expected["observed"]}, "identity observation fields invalid")
        _check(actual[name] == observed[name], f"identity observation {name} mismatch")
        _check(actual["host"] == run.get("host"), "identity observation host mismatch")
        _check(actual == {"host": run.get("host"), **observed}, "identity observation combination mismatch")
        captured = _time(payload["observed_at"], "identity observation")
        _check(started <= captured <= _time(run.get("ended_at"), "formal arm end"), "identity observation time outside formal arm")
        source = payload["source_artifact"]
        _check(isinstance(source, str) and source != event["artifact"] and source in evidence
               and evidence[source] == payload["source_sha256"], "identity observation source missing or digest mismatch")
