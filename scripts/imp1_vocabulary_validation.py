#!/usr/bin/env python3
"""Scan a Phase 15 ``IMP-1`` prompt for the protocol vocabulary C7 bans.

Gate **P12** of the pre-flight checklist in
``docs/release/phase15-execution-surface-design.md`` §11 reads: *banned-term scan
on ``prompts/IMP-1.txt`` returns zero hits*. The term list is fixed by §7.1 and
is reproduced here verbatim; this module implements that scan and nothing else.

The implicit arm exists to observe whether the host surfaces the Skill without
being told to. A prompt that names the Skill, or that carries protocol
vocabulary, destroys the observable before the arm runs — which is why §13
requires a hit to be fixed and re-attested rather than run and disclosed.

Three implementation decisions are deliberate and auditable:

* **The list is not extended.** ``BANNED_TERMS`` is §7.1's list, in §7.1's
  order. Adding a term here would silently tighten C7 beyond what the design
  specifies, and the design is the authority.
* **Whole-word means word boundaries, and inflections are not matched.**
  ``Ledgers`` does not match ``Ledger`` and ``modes`` does not match ``mode``.
  Stem matching would forbid words §7.1 does not forbid, which is exactly the
  broadening the previous point rules out. A reviewer who wants inflections
  banned must change §7.1 first.
* **Whitespace inside a multi-word term is flexible.** ``Full Loop`` matches
  across a line break. This can only make the scan stricter — it admits no term
  the list omits — so it cannot produce a false clean result.

The check reports; it decides nothing. A clean result is not evidence that
``IMP-1`` may run, does not score an acceptance dimension, and does not tick a
gate.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Reproduced verbatim from phase15-execution-surface-design.md §7.1. Do not add
# to this tuple without amending §7.1 first; see the module docstring.
BANNED_TERMS = (
    "LoopPilot",
    "loop-pilot",
    "Skill",
    "activation",
    "activate",
    "rubric",
    "acceptance",
    "Lightweight",
    "Full Loop",
    "Ledger",
    "Contract",
    "Checkpoint",
    "Barrier",
    "mode",
    "evaluation",
    "fixture",
    "protocol",
)

CLEAN_STATE = "IMP1_VOCABULARY_CLEAN"
CONTAMINATED_STATE = "IMP1_VOCABULARY_CONTAMINATED"


def _pattern(term: str) -> re.Pattern[str]:
    """Compile one banned term into a case-insensitive whole-word pattern."""
    parts = [re.escape(part) for part in term.split()]
    return re.compile(r"\b" + r"\s+".join(parts) + r"\b", re.IGNORECASE)


PATTERNS = tuple((term, _pattern(term)) for term in BANNED_TERMS)


def scan_text(text: str) -> list[str]:
    """Return one ``banned-term:<term>|line <n>|<matched text>`` per hit.

    Every term is scanned against the whole text, so a prompt carrying two
    distinct banned terms reports two findings rather than stopping at the
    first. Findings are ordered by term, then by position, so the output is
    deterministic for a given input.
    """
    findings: list[str] = []
    for term, pattern in PATTERNS:
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            findings.append(f"banned-term:{term}|line {line}|{match.group(0)}")
    return findings


def _report(prompt: Path, text: str, findings: list[str]) -> list[str]:
    """Build the deterministic report lines for one prompt file."""
    state = CONTAMINATED_STATE if findings else CLEAN_STATE
    lines = [
        f"Prompt: {prompt}",
        f"Characters scanned: {len(text)}",
        f"Terms checked: {len(BANNED_TERMS)}",
        f"State: {state}",
        f"Findings: {len(findings)}",
    ]
    lines.extend(findings)
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Scan a Phase 15 IMP-1 prompt for the protocol vocabulary banned by "
            "the execution-surface design §7.1. Reports hits; it does not "
            "decide whether the arm may run."
        )
    )
    parser.add_argument(
        "--prompt",
        required=True,
        type=Path,
        help="Prompt file to scan, normally prompts/IMP-1.txt.",
    )
    arguments = parser.parse_args(argv)

    prompt = arguments.prompt
    if not prompt.is_file():
        print(f"error: prompt is not a file: {prompt}")
        return 2

    text = prompt.read_text(encoding="utf-8-sig")
    findings = scan_text(text)
    for line in _report(prompt, text, findings):
        print(line)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
