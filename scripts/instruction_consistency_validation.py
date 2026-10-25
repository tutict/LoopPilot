"""Bounded static instruction invariants; not a runtime planner or AI judge."""
from pathlib import Path
import re

COORDINATION = "docs/coordination-necessity-and-delegation-fallback.md"
FIELDS = ("case", "risk", "coordination", "specialist", "kind", "mode", "review_floor", "specialist_depth")


def parse_mode_cases(text: str) -> list[dict[str, str]]:
    rows = []
    for line in text.splitlines():
        if re.match(r"^\| M\d+ \|", line):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) != len(FIELDS):
                raise ValueError("mode case must have eight fields")
            rows.append(dict(zip(FIELDS, cells)))
    return rows


def check_mode_cases(rows: list[dict[str, str]]) -> list[str]:
    errors = []
    for row in rows:
        if (row.get("risk") not in {"low", "high"}
                or row.get("coordination") not in {"none", "required"}
                or row.get("specialist") not in {"no", "yes"}
                or row.get("kind") not in {"coding", "non-coding"}):
            errors.append("invalid structured mode input")
            continue
        # Finite documentation relation: neither risk nor reviewer/kind selects mode.
        expected_mode = "Full Loop gate" if row["coordination"] == "required" else "Lightweight allowed"
        expected_floor = "enhanced" if row["risk"] == "high" else "standard"
        if row.get("mode") != expected_mode:
            errors.append(f"{row['case']}: coordination must determine the mode path")
        if row.get("review_floor") != expected_floor:
            errors.append(f"{row['case']}: product risk must determine the minimum review floor")
        expected_extra = "targeted" if row["specialist"] == "yes" else "none"
        if row.get("specialist_depth") != expected_extra:
            errors.append(f"{row['case']}: specialist scope must be distinct from the risk floor")
    return errors


# IA04 routes only; this is a finite documentation check, not a language judge.
MODE_ROUTES = (
    "docs/mode-selection-and-escalation.md",
    "docs/multi-agent-coordination.md",
    COORDINATION,
    "docs/protocol-modes-and-state-sources.md",
    "docs/protocol-load-profiles.md",
    "docs/safety-and-stopping.md",
    "docs/loop-engineering-model.md",
    "docs/design-rationale.md",
)


def check_mode_procedure(text: str, path: str) -> list[str]:
    """Reject bounded imperative shortcuts and unguarded mode-diagram paths.

    Prose checks recognize explicit trigger/action clauses, not arbitrary semantics.
    The diagram check supports the simple one-edge-per-line flowcharts used by the
    routed docs. Node names and declaration order have no authority; every path to
    Full Loop must pass risk, minimum review, then the Yes coordination branch.
    """
    errors = []
    prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    trigger = (r"\b(?:risk|sensitive.data|security|specialist|hard trigger|escalation|stop|"
               r"preserv\w*|major|blocker|sqlite|transaction\w*|migration|partial.success|"
               r"corrupt\w*|duplicate writes|idempotenc\w*|permission\w*|network trust|"
               r"cross.language|cross.runtime)\b")
    action = (r"\b(?:creat\w*|select\w*|switch\w*|requir\w*|mandat\w*|escalat\w*) "
              r"(?:(?:a|the|formal|new|to|into) )*full loop\b"
              r"|\bfull loop (?:is|becomes) (?:required|mandatory)\b"
              r"|\bevaluate full loop first\b")
    # Join wrapped prose, but keep list/table/paragraph boundaries independent.
    prose = re.sub(r"(?<!\n)\n(?!\s*(?:\n|[-#|]|\d+\.))", " ", prose)
    for raw in re.split(r"[.!?\n]+", prose):
        clause = " ".join(raw.lower().split())
        if "full loop" not in clause:
            continue
        # A positive coordination condition is needed, not merely the word
        # 'coordination' (e.g. 'even without coordination' is still a shortcut).
        guarded = re.search(r"(?:if|when|only (?:if|when)) (?:that )?coordination (?:requires|is required)"
                            r"|high coordination necessity requires full loop", clause)
        negated = re.search(r"(?:must not|does not|do not|never|not a|not direct|without requiring)[^.]*full loop", clause)
        if re.search(trigger, clause) and re.search(action, clause) and not (guarded or negated):
            errors.append(f"mode reassessment: unguarded trigger-to-Full-Loop clause: {path}")
        if re.search(r"coordination (?:necessity )?(?:is )?required.*(?:continue|retain|select) lightweight", clause):
            errors.append(f"mode reassessment: required coordination bypasses Full Loop: {path}")

    for block in re.findall(r"```mermaid\s*\n(.*?)```", text, re.DOTALL):
        if not re.search(r"full loop", block, re.IGNORECASE):
            continue
        nodes = {}
        gates = set()
        for match in re.finditer(r'\b(\w+)(\[[^\]\n]*\]|\{[^}\n]*\})', block):
            node, label = match.groups()
            nodes[node] = label[1:-1].strip('"').lower()
            if label.startswith("{") and re.fullmatch(r"coordination(?: necessity)? required\?", nodes[node]):
                gates.add(node)
        # Labels cannot contain edges; strip them before reading endpoint IDs.
        bare = re.sub(r'\[[^\]\n]*\]|\{[^}\n]*\}', '', block)
        edges = []
        for line in bare.splitlines():
            if not re.search(r"--|\.->|==", line):
                continue
            match = re.fullmatch(r"\s*(\w+)\s*-->\s*(?:\|([^|]*)\|\s*)?(\w+)\s*", line)
            if match is None:
                errors.append(f"mode reassessment: unsupported mode-diagram edge: {path}")
                continue
            source, label, target = match.groups()
            edges.append((source, (label or "").strip().lower(), target))
        endpoints = set(nodes) | {n for source, _, target in edges for n in (source, target)}
        # Starting at every risk node as well as entries catches bypasses in cycles.
        entries = endpoints - {target for _, _, target in edges}
        entries |= {node for node, label in nodes.items() if "product risk" in label}
        pending = [(node, 0) for node in entries]
        seen = set()
        while pending:
            node, stage = pending.pop()
            if (node, stage) in seen:
                continue
            seen.add((node, stage))
            label = nodes.get(node, "")
            if "product risk" in label:
                stage = 1
            elif "minimum" in label and "review" in label and stage == 1:
                stage = 2
            if "full loop" in label and stage != 3:
                errors.append(f"mode reassessment: Full Loop path bypasses risk/review/coordination gate: {path}")
            if "lightweight" in label and stage == 3:
                errors.append(f"mode reassessment: required coordination routes to Lightweight: {path}")
            for source, branch, target in edges:
                if source == node:
                    next_stage = stage
                    if node in gates:
                        next_stage = 3 if stage == 2 and branch == "yes" else 0
                    pending.append((target, next_stage))
        reached = {node for node, _ in seen}
        if any("full loop" in label and node not in reached for node, label in nodes.items()):
            errors.append(f"mode reassessment: Full Loop cycle has no assessed entry: {path}")
    return list(dict.fromkeys(errors))


def validate_instruction_consistency(root: Path) -> list[str]:
    errors = []
    paths = ("AGENTS.md", COORDINATION, "docs/multi-agent-coordination.md")
    texts = {}
    for path in paths:
        file = root / path
        if not file.is_file():
            errors.append(f"instruction consistency: missing {path}")
            continue
        texts[path] = " ".join(file.read_text(encoding="utf-8").lower().split())
    agents = texts.get("AGENTS.md", "")
    if re.search(r"\b(?:do not|must not|never) (?:read|inspect) (?:the )?(?:repository|source|files) (?:before|prior to) (?:an? )?(?:edit(?:ing)?|modif(?:y|ying))\b", agents):
        errors.append("pre-edit inspection conflict: relevant inspection must precede modification")
    if "inspect -> understand applicable rules -> modify" not in agents:
        errors.append("instruction consistency: missing inspect/rules/modify ordering")
    for path in (COORDINATION, "docs/multi-agent-coordination.md"):
        if re.search(r"\blightweight\b[^.]*\bmust escalate\b[^.]*\bspecialist reviewer\b", texts.get(path, "")):
            errors.append(f"specialist mode conflict: {path}")
    for path in MODE_ROUTES:
        file = root / path
        if file.is_file():
            errors.extend(check_mode_procedure(file.read_text(encoding="utf-8"), path))
    if (root / COORDINATION).is_file():
        try:
            rows = parse_mode_cases((root / COORDINATION).read_text(encoding="utf-8"))
        except ValueError as error:
            errors.append(str(error))
        else:
            if len(rows) != 7 or {row["case"] for row in rows} != {f"M{i}" for i in range(1, 8)}:
                errors.append("instruction consistency: seven distinct mode cases M1-M7 required")
            errors.extend(check_mode_cases(rows))
    return errors
