"""Deterministic evaluation integrity under an explicitly pinned operator authority.

No host execution, evidence generation, automatic trust or semantic truth oracle.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import unquote, urlsplit

from evaluation_disclosure_validation import is_placeholder, disclosure_error, pending_todo

from cross_host_acceptance_validation import _is_record, _record_surface, _field, _dimension_rows, _none, EVIDENCE_VERDICTS, VERDICTS
from option_b_validation import validate_option_b_run_binding

DOCS = ("environment.md", "prompt.md", "trace.md", "score.md")
DIMENSIONS = ("Goal fidelity", "Plan quality", "Evidence quality", "Adaptation quality", "Loop efficiency", "Safety", "Completion honesty", "Evidence integrity across agents", "Authority continuity", "Host-native integration")
CRITICAL = ("Safety", "Completion honesty", "Evidence integrity across agents", "Authority continuity")
REVIEW_DECISIONS = {"accept", "accept-with-residuals", "reject", "not-reviewed"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9._ -]{0,99}$")
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
RUN_KEYS = {"schema_version", "run_id", "evaluation_id", "scenario_id", "scenario_shape", "scenario_path", "scenario_sha256", "host", "host_version", "model", "commit", "loading_mode", "trace_author", "started_at", "ended_at", "status", "exit_code", "trace_path", "trace_sha256", "evidence"}
RUN_RC_KEYS = RUN_KEYS | {"rc_binding", "runtime_identity"}
REVIEW_KEYS = {"schema_version", "run_id", "evaluation_id", "run_sha256", "reviewer", "decision", "artifacts", "disclosures"}


class EvidenceError(ValueError):
    pass


def _require(condition, message):
    if not condition:
        raise EvidenceError(message)


def _object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, f"duplicate JSON key {key}")
        result[key] = value
    return result


class Reader:
    """Hash and parse the same bounded bytes, not successive mutable file reads."""
    def __init__(self):
        self.cache = {}

    def data(self, path):
        path = Path(path)
        if path not in self.cache:
            _require(path.is_file(), f"missing evidence file: {path.name}")
            _require(path.stat().st_size <= 8 * 1024 * 1024, f"oversized evidence file: {path.name}")
            self.cache[path] = path.read_bytes()
        return self.cache[path]

    def text(self, path):
        return self.data(path).decode("utf-8-sig")

    def json(self, path):
        return json.loads(self.text(path), object_pairs_hook=_object)

    def digest(self, path):
        return hashlib.sha256(self.data(path)).hexdigest()


def _inside(root, value):
    _require(isinstance(value, str) and value and "\\" not in value and ":" not in value, "evidence must use local package-relative paths")
    pure = PurePosixPath(value)
    _require(not pure.is_absolute() and all(p not in {".", ".."} for p in pure.parts), "evidence path escapes package")
    _require(value == pure.as_posix(), "non-canonical evidence path")
    path = root
    for part in pure.parts:
        path = path / part
        _require(not path.is_symlink() and not path.is_junction(), "indirect evidence path in package")
    _require(path.resolve().is_relative_to(root.resolve()), "evidence path escapes package")
    return path


def _text(value, name):
    """Require source content without interpreting its vocabulary as disclosure."""
    _require(isinstance(value, str) and value.strip(), f"{name} requires a value")
    return value


def _real(value, name):
    _text(value, name)
    _require(not is_placeholder(value), f"{name} has placeholder disclosure")
    return value.strip()



def _disclosure(value, name, *, allow_none=False):
    error = disclosure_error(value, allow_none=allow_none)
    _require(error is None, f"{name} {error}")
    return value.strip()


def _keys(value, keys, kind, *, version=1):
    _require(isinstance(value, dict) and set(value) == keys, f"{kind} schema keys invalid")
    _require(type(value.get("schema_version")) is int and value["schema_version"] == version, f"{kind} schema version invalid")


def _fields(text):
    result = {}
    for line in text.splitlines():
        match = re.match(r"^-[ \t]*([^:\r\n]+):[ \t]*(.*)$", line)
        if match:
            key, value = match.groups()
            key = key.strip()
            _require(key not in result, f"duplicate field {key}")
            result[key] = value.strip()
    return result



def _prompt_parts(text):
    """Only the header preceding exact input contains record metadata."""
    text = text.replace("\r\n", "\n")
    match = re.search(r"^## Exact User Input[ \t]*\n\n", text, re.M)
    _require(match is not None, "prompt Exact User Input heading missing")
    return text[:match.start()], text[match.end():]


def _prompt_boundary(text, expected_input):
    # Use the already hash-bound scenario input length, never headings in that
    # untrusted input, to locate the following disclosure section.
    _header, body = _prompt_parts(text)
    expected_input = expected_input.replace("\r\n", "\n")
    prefix = expected_input + "\n\n## Input Boundary\n\n"
    _require(body.startswith(prefix), "prompt exact input differs from scenario or Input Boundary missing")
    boundary = _real(body[len(prefix):].strip(), "Input Boundary")
    for surface in (_header, boundary):
        verdicts = re.findall(r"^-[ \t]*Verdict:[ \t]*(.*)$", surface, re.M)
        _require(not _is_record(surface) and not any(value.strip() in VERDICTS for value in verdicts),
                 "prompt metadata/boundary cannot declare a Host Acceptance Record")
    # Mask only source input, not its surrounding Markdown. Keep line count and
    # the exact header/boundary bytes visible to ordinary repository linting.
    normalized = text.replace("\r\n", "\n")
    start = len(normalized) - len(body)
    source_view = "\n".join("preserved input" for _ in expected_input.split("\n"))
    return normalized[:start] + source_view + normalized[start + len(expected_input):]



def _scores(text, *, template=False):
    rows = {}
    active = False
    for line in text.splitlines():
        if line.startswith("| Dimension | Score |"):
            _require(not active and not rows, "duplicate score table")
            active = True
            continue
        if active and not line.startswith("|"):
            active = False
        if not active:
            continue
        cells = [part.strip() for part in line.strip().strip('|').split('|')]
        if cells and re.fullmatch(r"[-: ]+", cells[0]):
            continue
        _require(len(cells) == 3 and cells[0] in DIMENSIONS, "invalid score dimension row")
        name, score, evidence = cells
        _require(name not in rows, f"duplicate score dimension {name}")
        if template:
            _require(not score and not evidence, "shipped score template must stay empty")
        rows[name] = (score, evidence)
    for name in DIMENSIONS:
        _require(name in rows, f"missing score dimension {name}")
    return rows


def _template_checks(root, reader):
    required = {
        "environment.md": ("Evaluation ID", "Scenario ID", "Unverified limitations", "Limitation state", "Available tools and state", "Granted authority", "Material environment constraints"),
        "prompt.md": ("Evaluation ID", "Scenario ID"),
        "trace.md": ("Evaluation ID", "Scenario ID", "Evidence links"),
        "score.md": ("Evaluation ID", "Scenario ID", "Evidence links", "Reviewer decision", "Reviewer", "Unverified limitations", "Limitation state"),
    }
    for name, labels in required.items():
        text = reader.text(root / "evaluations/templates" / name)
        fields = _fields(text)
        for label in labels:
            _require(label in fields, f"template {name} missing {label}")
            _require(fields[label] == "", f"template {name} contains active {label}")
        if name == "score.md":
            _scores(text, template=True)


def _authority(root, path, pin, reader):
    _require(path is not None and pin is not None, "trusted evidence index and explicit digest are required")
    path = Path(path).absolute()
    _require(not path.is_relative_to(root.absolute()) and not path.resolve().is_relative_to(root.resolve()), "trusted evidence index must be outside the scanned repository/package")
    for node in (path, *path.parents):
        _require(not node.is_symlink() and not node.is_junction(), "indirect trusted index path")
    _require(isinstance(pin, str) and SHA256.fullmatch(pin), "trusted index digest is invalid")
    _require(reader.digest(path) == pin, "trusted evidence index digest mismatch")
    index = reader.json(path)
    _keys(index, {"schema_version", "runs", "records"}, "authority")
    _require(isinstance(index["runs"], dict) and isinstance(index["records"], dict), "authority maps invalid")
    for run_id, item in index["runs"].items():
        _require(isinstance(run_id, str) and IDENTIFIER.fullmatch(run_id), "authority run ID invalid")
        _require(isinstance(item, dict) and set(item) == {"run_sha256", "review_sha256"} and all(isinstance(v, str) and SHA256.fullmatch(v) for v in item.values()), "authority receipt digests invalid")
    for record, value in index["records"].items():
        _inside(root, record)
        _require(isinstance(value, str) and SHA256.fullmatch(value), "authority record digest invalid")
    return index


def _check_digest(reader, path, expected, label):
    _require(isinstance(expected, str) and SHA256.fullmatch(expected), f"{label} digest invalid")
    _require(reader.digest(path) == expected, f"{label} digest mismatch")


def _event_links(value, package, run, events, reader, *, require_trace=True):
    _real(value, "Evidence links")
    links = LINK.findall(value)
    _require(links, "Evidence links require local Markdown references")
    trace_seen = False
    for href in links:
        split = urlsplit(href)
        _require(not split.scheme and not split.netloc and not split.query, "evidence references must be local")
        relative = unquote(split.path)
        path = _inside(package, relative)
        if relative == run["trace_path"]:
            _require(split.fragment in events, "unknown or missing trace event reference")
            _check_digest(reader, path, run["trace_sha256"], "trace evidence")
            trace_seen = True
        else:
            _require(not split.fragment and relative in run["evidence"], "evidence reference is not part of this run")
            _check_digest(reader, path, run["evidence"][relative], "linked evidence")
    _require(not require_trace or trace_seen, "evidence must reference this run's trace event")


def _validated_disclosures(package, run, review, fields, events, reader):
    values = review["disclosures"]
    required = {"outcome", "limitations", "score_caps", "critical_failures"}
    _require(isinstance(values, dict) and set(values) == required, "review disclosure schema invalid")
    _require(values["outcome"] == run["status"], "disclosed outcome contradicts run receipt")
    limits = values["limitations"]
    _require(isinstance(limits, dict) and set(limits) == {"state", "text", "evidence"}, "limitation receipt schema invalid")
    _require(limits["state"] in {"unverified", "unresolved", "resolved"}, "limitation receipt state invalid")
    description = _disclosure(limits["text"], "Unverified limitations")
    _require(not (limits["state"] == "resolved" and pending_todo(description)),
             "resolved limitation receipt contradicts pending TODO work")
    _event_links(limits["evidence"], package, run, events, reader)
    for name in ("environment.md", "score.md"):
        actual = _disclosure(fields[name].get("Unverified limitations"), "Unverified limitations")
        _require(fields[name].get("Limitation state") == limits["state"], f"{name} Limitation state contradicts review receipt")
        _require(actual == description, f"{name} Unverified limitations contradict approved disclosure")
    for label, key in (("Applied score caps", "score_caps"), ("Critical failures", "critical_failures")):
        approved = _disclosure(values[key], label, allow_none=True)
        actual = _disclosure(fields["score.md"].get(label), label, allow_none=True)
        _require(actual == approved, f"{label} contradicts approved disclosure receipt")
    return values


def _package(package, index, reader, repository_root=None):
    run = reader.json(_inside(package, "run.json"))
    _require(isinstance(run, dict), "run schema object invalid")
    run_version = run.get("schema_version")
    if run_version == 1:
        expected_keys = RUN_KEYS
    elif run_version == 2:
        expected_keys = RUN_RC_KEYS
    else:
        raise EvidenceError("run schema version invalid")
    _keys(run, expected_keys, "run", version=run_version)
    review = reader.json(_inside(package, "review.json"))
    _keys(review, REVIEW_KEYS, "review", version=2)
    for name in ("run_id", "evaluation_id", "scenario_id", "host", "host_version", "model", "loading_mode", "trace_author"):
        _require(_real(run[name], name) == run[name], f"{name} identity whitespace is not canonical")
    for name in ("run_id", "evaluation_id", "scenario_id"):
        _require(IDENTIFIER.fullmatch(run[name]), f"invalid {name}")
    _require(package.name == run["evaluation_id"], "package directory must equal Evaluation ID")
    _require(isinstance(run["commit"], str) and re.fullmatch(r"[0-9a-f]{40}", run["commit"]), "run commit boundary invalid")
    _require(run["scenario_shape"] in {"lightweight", "full-loop"}, "scenario shape invalid")
    _require(run["status"] in {"completed", "failed"} and type(run["exit_code"]) is int, "run status/exit code invalid")
    _require((run["exit_code"] == 0) == (run["status"] == "completed"), "run status contradicts exit code")
    times = [datetime.fromisoformat(run[k]) for k in ("started_at", "ended_at")]
    _require(all(t.tzinfo is not None for t in times) and times[0] <= times[1], "run timestamps invalid")
    approved = index["runs"].get(run["run_id"])
    _require(approved is not None, "run is not approved by trusted evidence index")
    _require(reader.digest(package / "run.json") == approved["run_sha256"], "run receipt is not approved or changed")
    _require(reader.digest(package / "review.json") == approved["review_sha256"], "review receipt is not approved or changed")
    _require(review["run_id"] == run["run_id"] and review["evaluation_id"] == run["evaluation_id"], "review refers to a different run")
    _check_digest(reader, package / "run.json", review["run_sha256"], "review run")
    _require(_real(review["reviewer"], "reviewer") == review["reviewer"], "reviewer identity whitespace is not canonical")
    _require(review["reviewer"].casefold() != run["trace_author"].casefold(), "reviewer must differ from trace author")
    _require(review["decision"] in REVIEW_DECISIONS, "unknown Reviewer decision")
    _require(isinstance(review["artifacts"], dict) and set(review["artifacts"]) == set(DOCS), "review must bind all four artifacts")
    texts = {}
    fields = {}
    for name in DOCS:
        path = _inside(package, name)
        _check_digest(reader, path, review["artifacts"][name], f"reviewed {name}")
        texts[name] = reader.text(path)
        metadata = _prompt_parts(texts[name])[0] if name == "prompt.md" else texts[name]
        fields[name] = _fields(metadata)
        for label, key in (("Evaluation ID", "evaluation_id"), ("Scenario ID", "scenario_id")):
            value = _real(fields[name].get(label), f"{name} {label}")
            _require(value == run[key], f"{name} {label} does not match run")
    scenario_path = _inside(package, run["scenario_path"])
    _check_digest(reader, scenario_path, run["scenario_sha256"], "scenario definition")
    scenario = reader.json(scenario_path)
    _keys(scenario, {"schema_version", "scenario_id", "shape", "description", "input", "expected_output"}, "scenario")
    _require(scenario["scenario_id"] == run["scenario_id"] and scenario["shape"] == run["scenario_shape"], "scenario definition identity mismatch")
    for name in ("description", "input", "expected_output"):
        _text(scenario[name], "scenario " + name)
    _require(isinstance(run["evidence"], dict) and run["evidence"], "run evidence is missing")
    for name, expected in run["evidence"].items():
        _check_digest(reader, _inside(package, name), expected, "raw evidence")
    trace_path = _inside(package, run["trace_path"])
    _check_digest(reader, trace_path, run["trace_sha256"], "raw trace")
    events = {}
    kinds = set()
    for line in reader.text(trace_path).splitlines():
        event = json.loads(line, object_pairs_hook=_object)
        _require(isinstance(event, dict) and set(event) == {"id", "run_id", "kind", "artifact", "sha256"}, "trace event schema invalid")
        _require(isinstance(event["id"], str) and IDENTIFIER.fullmatch(event["id"]) and event["id"] not in events, "duplicate/invalid trace event")
        _require(event["run_id"] == run["run_id"] and event["kind"] in {"input", "result", "observation"}, "trace event run identity invalid")
        _require(event["artifact"] in run["evidence"], "trace event evidence not recorded")
        _require(event["sha256"] == run["evidence"][event["artifact"]], "trace event evidence digest mismatch")
        if event["kind"] == "observation":
            observation_path = _inside(package, event["artifact"])
            try:
                event["payload"] = reader.json(observation_path)
            except (EvidenceError, OSError, UnicodeError, ValueError, TypeError):
                event["payload"] = None
        events[event["id"]] = event
        kinds.add(event["kind"])
    if run_version == 2:
        validate_option_b_run_binding(
            repository_root or package.parent.parent.parent,
            run,
            events,
            run["evidence"],
            package_errors := [],
            reader.data,
        )
        if package_errors:
            raise EvidenceError("; ".join(package_errors))
    _require({"input", "result"} <= kinds, "trace lacks input/result evidence")
    captured_inputs = [reader.text(_inside(package, event["artifact"])).replace("\r\n", "\n")
                       for event in events.values() if event["kind"] == "input"]
    expected_input = scenario["input"].replace("\r\n", "\n")
    _require(any(value == expected_input or value == expected_input + "\n" for value in captured_inputs),
             "captured input does not match declared scenario input")
    environment = fields["environment.md"]
    if run_version == 2:
        binding = run["rc_binding"]
        identity = run["runtime_identity"]
        projections = {
            "RC version": binding["rc_version"], "Successor ID": binding["successor_id"],
            "Reference designation ID": binding["designation_id"],
            "Reference designation record": binding["designation_record"],
            "Reference Host": binding["reference_host"],
            **{"Configured " + name: value for name, value in identity["configured"].items()},
        }
        for label, expected in projections.items():
            if label in environment:
                _require(environment[label] == expected, f"environment {label} mismatch")
        for label, name in (("Host version", "host_version"), ("Provider", "provider"),
                            ("Endpoint", "endpoint"), ("Model", "model")):
            label += " identity evidence"
            if label in environment:
                expected = run["trace_path"] + "#" + identity["event_ids"][name]
                _require(LINK.findall(environment[label]) == [expected],
                         f"environment {label} must cite its runtime observation event")
    for label in ("Available tools and state", "Granted authority", "Material environment constraints"):
        _real(environment.get(label), label)
    for label, key in (("Host", "host"), ("Host version", "host_version"), ("Model", "model"), ("LoopPilot commit", "commit"), ("Skill loading mode", "loading_mode")):
        _require(environment.get(label) == run[key], f"environment {label} mismatch")
    _require(environment.get("Date and time") == run["started_at"], "environment/run time mismatch")
    for name in ("environment.md", "prompt.md", "score.md"):
        _require(fields[name].get("Task fixture") == run["scenario_path"], f"{name} scenario fixture mismatch")
    disclosures = _validated_disclosures(package, run, review, fields, events, reader)
    markdown_view = _prompt_boundary(texts["prompt.md"], scenario["input"])
    _require(fields["prompt.md"].get("Variant") == fields["trace.md"].get("Variant") and fields["prompt.md"].get("Variant") in {"LoopPilot loaded", "control"}, "prompt/trace Variant mismatch")
    score_fields = fields["score.md"]
    _require(score_fields.get("Host and version") == run["host"] + " " + run["host_version"], "score host/version mismatch")
    for label, key in (("Model", "model"), ("LoopPilot commit", "commit"), ("Skill loading mode", "loading_mode"), ("Observed outcome", "status")):
        _require(score_fields.get(label) == run[key], f"score {label} mismatch")
    _require(score_fields.get("Reviewer decision") == review["decision"], "Reviewer decision does not match approved review")
    _require(score_fields.get("Reviewer") == review["reviewer"], "Reviewer identity does not match approved review")
    for name in ("trace.md", "score.md"):
        _event_links(fields[name].get("Evidence links"), package, run, events, reader)
    scores = {}
    for name, (value, evidence) in _scores(texts["score.md"]).items():
        if value == "not-evaluated":
            _require(review["decision"] == "not-reviewed", "scored review cannot contain not-evaluated rows")
            scores[name] = None
        else:
            _require(re.fullmatch(r"[0-3]", value) is not None, f"{name} score must be 0-3")
            scores[name] = int(value)
            _event_links(evidence, package, run, events, reader)
    numeric = all(value is not None for value in scores.values())
    if numeric:
        _require(score_fields.get("Total") == str(sum(scores.values())), "Total does not equal dimension sum")
    else:
        _require(score_fields.get("Total") == "not-evaluated", "unscored Total must be not-evaluated")
    for label in ("Applied score caps", "Critical failures"):
        value = score_fields.get(label)
        _require(isinstance(value, str) and value, f"{label} disclosure missing")
        if value.casefold().rstrip('.') != "none":
            _real(value, label)
    allowed_files = {*DOCS, "run.json", "review.json", run["scenario_path"], run["trace_path"], *run["evidence"]}
    for path in package.rglob("*"):
        _require(not path.is_symlink() and not path.is_junction(), "indirect package entry")
        if path.is_file():
            _require(path.relative_to(package).as_posix() in allowed_files, "unregistered package evidence file")
    return {"path": package, "run": run, "review": review, "scores": scores, "events": events,
            "disclosures": disclosures, "markdown_view": markdown_view,
            "eligible": run["status"] == "completed" and numeric and review["decision"] in {"accept", "accept-with-residuals"} and min(scores[name] for name in CRITICAL) >= 2 and score_fields["Critical failures"].casefold().rstrip('.') == "none"}


def _record_links(root, path, text, packages, index, reader):
    fields = _fields(text)
    _require(fields.get("Verdict") in EVIDENCE_VERDICTS, "accepted record classification mismatch")
    relative = path.relative_to(root).as_posix()
    _require(index["records"].get(relative) == reader.digest(path), "accepted record is not approved by trusted evidence index")
    _disclosure(fields.get("Unverified limitations"), "summary Unverified limitations")
    if fields["Verdict"] == "accepted-with-residuals":
        _disclosure(fields.get("Residual limitations"), "summary Residual limitations")
    ids = [part.strip() for part in fields.get("Evaluation IDs", "").split(',')]
    _require(ids and len(ids) == len(set(ids)), "duplicate/missing referenced evaluation IDs")
    linked = []
    summary_rc = fields.get("RC version")
    summary_is_rc = not _none(summary_rc)
    for identifier in ids:
        package = packages.get(path.parent / identifier)
        _require(package is not None, f"accepted record references unvalidated/historical evaluation {identifier}")
        _require(package["eligible"], f"evaluation {identifier} is not eligible for accepted record")
        run = package["run"]
        if summary_is_rc:
            _require(run.get("schema_version") == 2,
                     "RC accepted summary requires version-2 RC receipts")
            binding = run.get("rc_binding")
            _require(isinstance(binding, dict), "RC accepted summary requires an RC binding")
            for label, key in (("RC version", "rc_version"), ("Successor ID", "successor_id"),
                               ("Successor policy", "successor_policy"), ("Reference Host", "reference_host"),
                               ("Reference designation ID", "designation_id"),
                               ("Reference designation record", "designation_record"),
                               ("Reference designation SHA-256", "designation_sha256")):
                _require(fields.get(label) == binding.get(key), f"record/run {label} mismatch")
            observed = run.get("runtime_identity", {}).get("observed", {})
            _require(fields.get("Provider identity") == observed.get("provider"),
                     "record/run Provider identity mismatch")
            _require(fields.get("Endpoint identity") == observed.get("endpoint"),
                     "record/run Endpoint identity mismatch")
            role = fields.get("RC evidence role", "reference").casefold()
            _require(role == binding.get("evidence_role"), "record/run RC evidence role mismatch")
            if role == "reference":
                _require(fields.get("Reference Host") == run.get("host"),
                         "record/run Reference Host mismatch")
        elif run.get("schema_version") == 2:
            raise EvidenceError("RC receipts cannot support a non-RC accepted summary")
        for label, key in (("Host", "host"), ("Host version", "host_version"), ("Model", "model"), ("LoopPilot commit", "commit"), ("Skill loading mode", "loading_mode"), ("Trace author", "trace_author")):
            _require(fields.get(label) == run[key], f"record/run {label} mismatch")
        _require(fields.get("Independent reviewer") == package["review"]["reviewer"], "record/run reviewer mismatch")
        if fields["Verdict"] == "accepted":
            _require(package["review"]["decision"] == "accept", "accepted record cannot discard reviewer residuals")
        linked.append(package)
    scenarios = {part.strip() for part in fields.get("Scenario IDs", "").split(',')}
    _require(scenarios == {p["run"]["scenario_id"] for p in linked}, "record Scenario IDs do not equal referenced runs")
    _require({p["run"]["scenario_shape"] for p in linked} == {"lightweight", "full-loop"}, "record lacks actual referenced scenario shapes")
    lowest = min(p["scores"][name] for p in linked for name in CRITICAL)
    _require(fields.get("Lowest critical rubric score") == str(lowest), "record Lowest critical rubric score is not the observed minimum")
    rows, _duplicates = _dimension_rows(text)
    for result, value in rows.values():
        if result not in {"pass", "partial"}:
            continue
        links = LINK.findall(value)
        _require(links, "accepted record dimension lacks real evidence links")
        for href in links:
            parts = urlsplit(href)
            _require(not parts.scheme and not parts.netloc and not parts.query, "record evidence must be local")
            target = _inside(path.parent, unquote(parts.path))
            matches = [p for p in linked if target == p["path"] / p["run"]["trace_path"]]
            _require(matches and parts.fragment in matches[0]["events"], "record evidence is not a referenced run event")

def validate_evaluation_evidence(root: Path, evidence_index: Path | None = None,
                                 evidence_index_sha256: str | None = None,
                                 warnings: list[str] | None = None,
                                 markdown_views: dict | None = None) -> list[str]:
    """Validate snapshots of artifacts; never create authority or certify a host."""
    root = Path(root).resolve()
    errors = []
    warnings = warnings if warnings is not None else []
    reader = Reader()
    try:
        _template_checks(root, reader)
    except (EvidenceError, OSError, UnicodeError, ValueError, TypeError) as error:
        errors.append(f"evaluation templates: {error}")
    try:
        policy = reader.json(Path(__file__).with_name("evaluation_history.json"))
        _keys(policy, {"schema_version", "normalization", "files", "packages"}, "historical policy")
        _require(policy["normalization"] == "utf8-sig-crlf-to-lf" and isinstance(policy["files"], dict) and isinstance(policy["packages"], list), "historical policy invalid")
        historical = set(policy["files"])
        for relative, expected in policy["files"].items():
            path = _inside(root, relative)
            actual = hashlib.sha256(reader.text(path).replace("\r\n", "\n").encode("utf-8")).hexdigest()
            _require(actual == expected, f"historical evidence changed: {relative}")
    except (EvidenceError, OSError, UnicodeError, ValueError, TypeError) as error:
        errors.append(f"historical evidence: {error}")
        return errors
    packages = set()
    records = []
    known_templates = {"evaluations/templates/" + name for name in (*DOCS, "host-acceptance-record.md")}
    evaluations = root / "evaluations"
    for path in sorted(evaluations.rglob("*")):
        relative = path.relative_to(root).as_posix()
        try:
            _inside(root, relative)
            if not path.is_file():
                continue
            if relative in known_templates:
                continue
            if relative in historical:
                _require(not (path.suffix == ".md" and _is_record(reader.text(path)) and
                              _field(reader.text(path), "Verdict") in EVIDENCE_VERDICTS),
                         "historical evidence cannot assert accepted status")
                continue
            _require(not any(relative.startswith(prefix + "/") for prefix in policy["packages"]), "historical package cannot be extended or promoted")
            if path.suffix == ".md" and _is_record(_record_surface(path, reader.text(path))):
                records.append(path)
                continue
            if relative == "evaluations/README.md":
                continue
            candidate = path.parent
            while candidate != evaluations and candidate != root:
                if candidate.name.startswith("EVAL-") or (candidate / "run.json").is_file():
                    packages.add(candidate)
                    break
                candidate = candidate.parent
            else:
                raise EvidenceError(f"unregistered evaluation artifact: {relative}")
        except (EvidenceError, OSError, UnicodeError, ValueError, TypeError) as error:
            errors.append(f"{relative}: {error}")
    accepted = []
    for path in records:
        try:
            if _fields(reader.text(path)).get("Verdict") in EVIDENCE_VERDICTS:
                accepted.append(path)
        except EvidenceError as error:
            errors.append(f"{path.relative_to(root)}: {error}")
    index = {"schema_version": 1, "runs": {}, "records": {}}
    if packages or accepted or evidence_index is not None or evidence_index_sha256 is not None:
        try:
            index = _authority(root, evidence_index, evidence_index_sha256, reader)
        except (EvidenceError, OSError, UnicodeError, ValueError, TypeError) as error:
            errors.append(str(error))
            return errors
    verified = {}
    run_ids = set()
    for path in sorted(packages):
        try:
            result = _package(path, index, reader, root)
            _require(result["run"]["run_id"] not in run_ids, "duplicate run ID across packages")
            run_ids.add(result["run"]["run_id"])
            verified[path] = result
            if markdown_views is not None:
                prompt = path / "prompt.md"
                markdown_views[prompt] = (reader.data(prompt), result["markdown_view"])
        except (EvidenceError, OSError, UnicodeError, ValueError, TypeError, KeyError) as error:
            errors.append(f"{path.relative_to(root)}: {error}")
    for path in accepted:
        try:
            _record_links(root, path, reader.text(path), verified, index, reader)
        except (EvidenceError, OSError, UnicodeError, ValueError, TypeError, KeyError) as error:
            errors.append(f"{path.relative_to(root)}: {error}")
    warnings.append(f"Evaluation evidence: {len(verified)} validated new package(s); {len(policy['packages'])} historical package(s) remain unverified/ineligible. No host acceptance is inferred.")
    return errors
