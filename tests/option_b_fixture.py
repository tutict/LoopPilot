"""Synthetic RC governance and trust around local test output; never acceptance."""
import json
import os
from pathlib import Path
import shutil
import subprocess

from evaluation_evidence_fixture import approve_record, digest, make_package, reseal_for_schema_test, save_json
from test_cross_host_acceptance import record

POLICY = "docs/release/option-b-reference-successor.md"
REFERENCE = "docs/release/rc-candidate-reference.md"
SUCCESSOR = "OPTION-B-REFERENCE-2026-10-24"
START = "2030-01-03T09:00:00+00:00"
END = "2030-01-03T09:01:00+00:00"


def git(root, *args, date="2030-01-01T08:00:00+00:00"):
    env = dict(os.environ, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date,
               GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    result = subprocess.run(["git", "-c", "core.autocrlf=false", "-c", "commit.gpgsign=false",
        "-c", "user.name=RC test fixture", "-c", "user.email=fixture@example.invalid", *args],
        cwd=root, env=env, capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)
    return result.stdout.strip()


def initialize(root, source):
    shutil.copytree(source, root, ignore=shutil.ignore_patterns(".git", ".tmp", "__pycache__"))
    git(root, "init", "-b", "fixture")
    git(root, "add", ".")
    git(root, "commit", "-m", "synthetic synchronized successor boundary")
    effective, effective_tree = git(root, "rev-parse", "HEAD"), git(root, "rev-parse", "HEAD^{tree}")
    (root / "fixture-boundary.txt").write_text("synthetic later baseline\n", encoding="utf-8")
    git(root, "add", "fixture-boundary.txt")
    git(root, "commit", "-m", "synthetic later RC baseline", date="2030-01-01T09:00:00+00:00")
    baseline, tree = git(root, "rev-parse", "HEAD"), git(root, "rev-parse", "HEAD^{tree}")
    fields = {
        "RC version": "v1.0.0-rc1", "Successor ID": SUCCESSOR, "Successor policy": POLICY,
        "Policy version": "option-b-successor-v1", "Reference designation ID": "RC1-REF-CODEX-20261024",
        "Reference Host": "Codex", "Other eligible Host": "Claude Code",
        "Other Host role": "Candidate Host; unverified disclosure retained",
        "Designation state": "finalized-before-acceptance", "Designation date": "2026-10-24",
        "Finalized at": "2030-01-02T08:00:00+00:00", "Formal acceptance arms at designation": "none",
        "Reference host version": "fixture-host-1", "Model identity": "fixture-upstream-model",
        "Provider identity": "fixture-provider", "Endpoint identity": "https://runtime.example.invalid",
        "Configured model": "fixture-request-alias", "Configured provider": "fixture-provider-label",
        "Configured endpoint": "https://configured.example.invalid", "Skill loading mode": "explicit fixture load",
        "RC baseline commit": baseline, "RC baseline tree": tree,
    }
    (root / REFERENCE).write_text("# RC Candidate Reference Designation — synthetic fixture\n\n" +
        "".join(f"- {key}: {value}\n" for key, value in fields.items()), encoding="utf-8")
    git(root, "add", REFERENCE)
    git(root, "commit", "-m", "synthetic pre-arm finalization", date="2030-01-02T08:01:00+00:00")
    return dict(effective=effective, effective_tree=effective_tree, baseline=baseline, tree=tree,
                designation_commit=git(root, "rev-parse", "HEAD"))


def rc_package(root, authority, boundary, *, number=1, role="reference", host="Codex", parent="option-b-test"):
    package = make_package(root, authority, evaluation_id=f"EVAL-RC-{number:03}", scenario_id=f"rc-scenario-{number}",
        shape="lightweight" if number == 1 else "full-loop", host=host, host_version="fixture-host-1",
        model="fixture-upstream-model", commit=boundary["baseline"], loading_mode="explicit fixture load", parent=parent)
    run = json.loads((package / "run.json").read_text(encoding="utf-8"))
    old_start = run["started_at"]
    run.update(schema_version=2, started_at=START, ended_at=END)
    run["rc_binding"] = {
        "rc_version": "v1.0.0-rc1", "successor_id": SUCCESSOR, "successor_policy": POLICY,
        "policy_sha256": digest(root / POLICY), "designation_id": "RC1-REF-CODEX-20261024",
        "designation_record": REFERENCE, "designation_sha256": digest(root / REFERENCE),
        "designation_commit": boundary["designation_commit"], "reference_host": "Codex", "evidence_role": role,
        "effective_successor_commit": boundary["effective"], "effective_successor_tree": boundary["effective_tree"],
        "run_commit": boundary["baseline"], "run_tree": boundary["tree"],
    }
    observed = dict(host_version="fixture-host-1", model="fixture-upstream-model", provider="fixture-provider",
                    endpoint="https://runtime.example.invalid")
    run["runtime_identity"] = {
        "configured": dict(model="fixture-request-alias", provider="fixture-provider-label", endpoint="https://configured.example.invalid"),
        "observed": observed, "event_ids": {key: "identity-1" for key in observed},
    }
    source = package / "evidence/runtime-source.txt"
    source.write_text("Synthetic upstream identity fixture; this is not actual Host Acceptance.\n", encoding="utf-8")
    save_json(package / "evidence/runtime.json", dict(schema_version=1, kind="runtime-identity", run_id=run["run_id"],
        observed_at=START, basis="actual-runtime-observation", identity={"host": host, **observed},
        source_artifact="evidence/runtime-source.txt", source_sha256=digest(source)))
    for name in ("runtime.json", "runtime-source.txt"):
        run["evidence"]["evidence/" + name] = digest(package / "evidence" / name)
    event = dict(id="identity-1", run_id=run["run_id"], kind="observation", artifact="evidence/runtime.json",
                 sha256=digest(package / "evidence/runtime.json"))
    with (package / run["trace_path"]).open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(event) + "\n")
    run["trace_sha256"] = digest(package / run["trace_path"])
    save_json(package / "run.json", run)
    environment = package / "environment.md"
    projection = {"RC version": "v1.0.0-rc1", "Successor ID": SUCCESSOR,
        "Reference designation ID": "RC1-REF-CODEX-20261024", "Reference designation record": REFERENCE,
        "Reference Host": "Codex", **{"Configured " + name: value for name, value in run["runtime_identity"]["configured"].items()}}
    projection.update({name + " identity evidence": "[runtime observation](evidence/events.jsonl#identity-1)"
                       for name in ("Host version", "Model", "Provider", "Endpoint")})
    environment.write_text(environment.read_text(encoding="utf-8").replace(old_start, START) +
        "\n" + "".join(f"- {key}: {value}\n" for key, value in projection.items()), encoding="utf-8")
    reseal_for_schema_test(package, authority)
    return package


def summary(root, authority, packages, *, role="reference", host="Codex"):
    run = json.loads((packages[0] / "run.json").read_text(encoding="utf-8"))
    text = record(Host=host, Host_version=run["host_version"], Model=run["model"], LoopPilot_commit=run["commit"],
        Skill_loading_mode=run["loading_mode"], Evaluation_IDs=", ".join(p.name for p in packages),
        Scenario_IDs=", ".join(json.loads((p / "run.json").read_text(encoding="utf-8"))["scenario_id"] for p in packages))
    values = {"RC version": "v1.0.0-rc1", "Successor ID": SUCCESSOR, "Successor policy": POLICY,
        "Reference designation ID": "RC1-REF-CODEX-20261024", "Reference designation record": REFERENCE,
        "Reference Host": "Codex", "Reference designation SHA-256": digest(root / REFERENCE),
        "Provider identity": "fixture-provider", "Endpoint identity": "https://runtime.example.invalid"}
    for key, value in values.items():
        text = text.replace(f"- {key}: none", f"- {key}: {value}")
    text = text.replace("## Dimension Results", f"- RC evidence role: {role}\n\n## Dimension Results")
    text = text.replace("trace reference", f"[trace]({packages[0].name}/evidence/events.jsonl#result-1)")
    path = packages[0].parent / "host-acceptance.md"
    path.write_text(text, encoding="utf-8")
    approve_record(root, path, authority)
    return path
