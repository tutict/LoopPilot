"""Validate the complete historical control/Skill-loaded replay experiment."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from evaluation_evidence_validation import (
    historical_replay_acceptance,
    validate_evaluation_evidence,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--evidence-index", type=Path, required=True, help="operator-approved index outside the repository")
    parser.add_argument("--evidence-index-sha256", required=True, help="independently approved raw SHA-256 of the index")
    args = parser.parse_args(argv)

    package_results = {}
    warnings = []
    errors = validate_evaluation_evidence(
        args.root,
        args.evidence_index,
        args.evidence_index_sha256,
        warnings,
        validated_packages=package_results,
    )
    result = historical_replay_acceptance(
        args.root,
        list(package_results.values()),
        operator_index_fixed=not errors,
    )
    report = {
        "schema_version": 1,
        "acceptance_type": "historical-replay-experiment",
        "host_acceptance_record": False,
        **result,
        "validation_errors": errors,
        "warnings": warnings,
    }
    sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    if errors:
        return 1
    return 0 if result["status"] == "accepted" else 2


if __name__ == "__main__":
    raise SystemExit(main())
