"""Validate Phase 9 static calibration without creating a runtime."""

from __future__ import annotations

import re
from pathlib import Path


PHASE9_CALIBRATION_FILES = (
    "docs/phase9-second-protocol-calibration.md",
    "docs/baseline-evidence-and-verification-surface.md",
    "docs/coordination-necessity-and-delegation-fallback.md",
    "docs/final-assignment-behavioral-evidence.md",
    "scripts/phase9_calibration_validation.py",
    "tests/test_phase9_calibration.py",
)

CORE_PROMPT_BASELINE_LINES = 562
CORE_PROMPT_MAX_LINES = 590

DOCUMENT_REQUIREMENTS = {
    "docs/phase9-second-protocol-calibration.md": (
        "evidence -> contradiction -> bounded calibration",
        "Only Lightweight and Full Loop are modes.",
        "Product Risk and Coordination Necessity are independent.",
        "Worker natural-language summaries update authoritative state only when a claim",
        "The Lightweight four-to-seven target counts Governance Artifacts",
        "External reference verification was unavailable",
    ),
    "docs/baseline-evidence-and-verification-surface.md": (
        "## Repository Baseline",
        "## Environment-Corrected Baseline",
        "## Scope-Focused Baseline",
        "A red repository baseline does not automatically block delivery.",
        "Pre-existing failure attribution MUST be established before claiming a regression.",
        "## Verification Surface",
        "A successful test command proves only the tests it actually selected.",
        "BASELINE-LEDGER.md",
    ),
    "docs/coordination-necessity-and-delegation-fallback.md": (
        "## Product Risk and Coordination Risk",
        "High product risk does not by itself prove that multiple Workers are required.",
        "## Coordination Necessity",
        "Lightweight MAY load a risk-matched specialist Reviewer",
        "## Worker Failure Budget",
        "no more than two unsuccessful Worker attempts",
        "## Ownership Collapse in Full Loop",
        "Reviewer and Integrator roles MUST NOT become code implementers",
        "## Verifiable Worker Claims",
        "Worker summary is not evidence.",
    ),
    "docs/final-assignment-behavioral-evidence.md": (
        "## EXP-005",
        "66dbeb5c99c9cac707f089767428c6c4bbd8836e",
        "## EXP-006",
        "6b24209f79aed7476b2ad3b54ac4385f06cfe730",
        "2ac9919bebe71e45445a2f3d22caa8cb43ab8436",
        "6e0ab5f55bcf8c93aa4f36e02af1aedd78ff2207",
        "604c4f93b4978e3fd0755a2ba09b3093f54c0d19",
        "a75aa0d801857d6e6b08957c74bcb28f7286ca9cd38de401c6798b67ef4bcc15",
        "Blocked /\nnot delivered",
        "dynamic H-7 single-row persistence holdout is unverified",
        "archival is therefore incomplete",
    ),
}

TEMPLATE_REQUIREMENTS = {
    ".looppilot/PROJECT-TEMPLATE.md": (
        "## Baseline Evidence",
        "- Repository Baseline:",
        "- Environment-Corrected Baseline:",
        "- Scope-Focused Baseline:",
        "## Verification Surface",
        "- Actual discovery:",
        "- Unreached tests:",
        "- Product Risk:",
        "- Coordination Necessity:",
    ),
    ".looppilot/full-loop/LOOP-CONTRACT-TEMPLATE.md": (
        "- Product Risk and required review depth:",
        "## Coordination Necessity",
        "- Why multiple Workers are required:",
        "- Fallback Worker:",
        "- Worker failure budget:",
        "- Ownership-collapse condition:",
    ),
    ".looppilot/full-loop/WORKER-DELIVERY-TEMPLATE.md": (
        "## Verifiable Claims",
        "| Claim | Evidence | Verification | Git Boundary |",
        "## Unverified Claims",
    ),
    ".looppilot/full-loop/INTEGRATION-RECORD-TEMPLATE.md": (
        "## Delegation Health",
        "- Worker attempts:",
        "- Unsuccessful attempts:",
        "- Failure budget:",
        "- Ownership collapsed:",
        "- Fallback Worker:",
    ),
    ".looppilot/full-loop/CHECKPOINT-TEMPLATE.md": (
        "- Successful Deliveries:",
        "- Failed delegation attempts:",
        "- Current implementation owner:",
    ),
}

FORBIDDEN_CLAIMS = (
    "Product Risk automatically requires Full Loop",
    "Security Reviewer present => Full Loop",
    "Unsuccessful Workers MAY retry indefinitely.",
    "Worker summary is sufficient evidence",
    "EXP-006 fully dynamically validated",
    "H-7 holdout verified",
    "Experiment conclusion: Lightweight is superior to Full Loop.",
    "New Phase 9 mode:",
    "New Phase 9 Ledger:",
    "New Phase 9 status:",
    "New Phase 9 severity:",
    "New Phase 9 Barrier:",
    "New Phase 9 Acceptance layer:",
    "New Phase 9 Recovery authority:",
)

BEHAVIOR_FORBIDDEN_CLAIMS = (
    "A pre-existing failure is always a new regression.",
    "Environment correction MAY change product implementation.",
    "mvn test exit 0 proves every repository test passed.",
    "Multiple Workers without independent delivery value require Full Loop.",
    "File count alone selects Full Loop.",
    "Security keyword alone selects Full Loop.",
    "Full Loop requires no Coordination Necessity rationale.",
    "A specialist Reviewer replaces Spec and Standards.",
    "A specialist Reviewer automatically creates Full Loop.",
    "Lightweight continues after a Major Finding without escalation.",
    "New implementation owners do not require mode reassessment.",
    "A required Integration Record does not require escalation.",
    "Lightweight may continue after corrections exceed the budget.",
    "A third unsuccessful Worker attempt needs no record.",
    "Failed Worker Deliveries MAY be deleted.",
    "Ownership collapse resets the Task revision count.",
    "Reviewer MAY implement product code during fallback.",
    "Integrator MAY implement product code during fallback.",
    "Supervisor MAY implement without recording ownership.",
    "A test-passed claim needs no command evidence.",
    "Cross-user 403 behavior needs no evidence.",
    "An unsupported Worker claim is an Execution Infrastructure Incident.",
    "Ten Governance Artifacts need no explanation or reassessment.",
    "Artifact Budget is a lifecycle state.",
    "Generic protocol rules require TypeScript/Rust.",
    "Templates default to Tauri.",
    "EXP-006 is statistically proven.",
    "Lightweight is universally superior to Full Loop.",
    "H-7 final single-row persistence is verified.",
    "The blocked Full Loop arm was delivered.",
    "New Phase 9 role: calibration",
)

FORBIDDEN_ARTIFACTS = {
    "BASELINE-LEDGER.md",
    "CLAIM-LEDGER.md",
    "EVIDENCE-LEDGER.md",
}


def _require(text: str, values: tuple[str, ...], location: str, errors: list[str]) -> None:
    normalized = re.sub(r"\s+", " ", text).casefold()
    for value in values:
        expected = re.sub(r"\s+", " ", value).casefold()
        if expected not in normalized:
            errors.append(f"{location}: missing Phase 9 requirement {value!r}")


def validate_phase9_calibration(root: Path, errors: list[str]) -> None:
    """Check Phase 9 structure and honesty; never select a mode or run work."""

    for location, requirements in DOCUMENT_REQUIREMENTS.items():
        path = root / location
        if path.is_file():
            _require(path.read_text(encoding="utf-8"), requirements, location, errors)

    for location, requirements in TEMPLATE_REQUIREMENTS.items():
        path = root / location
        if path.is_file():
            _require(path.read_text(encoding="utf-8"), requirements, location, errors)

    mode = root / "docs/mode-selection-and-escalation.md"
    if mode.is_file():
        _require(
            mode.read_text(encoding="utf-8"),
            (
                "## Product Risk and Coordination Necessity",
                "High product risk does not by itself prove that multiple Workers are required.",
                "four to seven Governance Artifacts",
                "Examples: TypeScript/Rust or Web/Tauri.",
                "A passing command proves only the tests it actually selected;",
            ),
            "docs/mode-selection-and-escalation.md",
            errors,
        )

    load_profiles = root / "docs/protocol-load-profiles.md"
    if load_profiles.is_file():
        _require(
            load_profiles.read_text(encoding="utf-8"),
            (
                "baseline attribution and Verification Surface",
                "Lightweight MAY add a risk-matched",
                "delegation failure budget",
                "ownership fallback",
            ),
            "docs/protocol-load-profiles.md",
            errors,
        )

    migration = root / "docs/full-loop-migration-plan.md"
    if migration.is_file():
        _require(
            migration.read_text(encoding="utf-8"),
            (
                "## Phase 8-A: Cross-Project Replication",
                "## Phase 8-B: Controlled Three-Mode Comparison",
                "comparative archive incomplete",
                "## Phase 9: Second Evidence-Backed Protocol Calibration",
                "## Phase 10: Third-Project and/or Cross-Host Replication",
            ),
            "docs/full-loop-migration-plan.md",
            errors,
        )

    scenarios = root / "tests/scenarios.md"
    rubric = root / "tests/evaluation-rubric.md"
    if scenarios.is_file():
        _require(
            scenarios.read_text(encoding="utf-8"),
            ("## 234. High Product Risk With One Owner", "## 263. Phase 10 Evidence Stays Separately Attributed"),
            "tests/scenarios.md",
            errors,
        )
    if rubric.is_file():
        _require(
            rubric.read_text(encoding="utf-8"),
            ("Attributes Repository, Environment-Corrected, and Scope-Focused evidence before a regression claim.", "Shows why multiple owners, integration, recovery, or rework governance is actually needed.", "States missing Deliveries, verification, acceptance, and remaining authority precisely."),
            "tests/evaluation-rubric.md",
            errors,
        )

    markdown = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*.md"))
        if ".git" not in path.parts
    )
    for claim in (*FORBIDDEN_CLAIMS, *BEHAVIOR_FORBIDDEN_CLAIMS):
        if claim in markdown:
            errors.append(f"Phase 9 contradiction: {claim}")

    artifacts = {
        path.name
        for path in root.rglob("*.md")
        if path.name in FORBIDDEN_ARTIFACTS
    }
    if artifacts:
        errors.append("Phase 9 forbidden Ledger artifact: " + ", ".join(sorted(artifacts)))

    line_count = sum(
        len((root / name).read_text(encoding="utf-8").splitlines())
        for name in ("SKILL.md", "AGENTS.md")
    )
    if line_count > CORE_PROMPT_MAX_LINES:
        errors.append(
            "Phase 9 core prompt budget exceeded: "
            f"baseline {CORE_PROMPT_BASELINE_LINES}, maximum {CORE_PROMPT_MAX_LINES}, "
            f"observed {line_count}"
        )
