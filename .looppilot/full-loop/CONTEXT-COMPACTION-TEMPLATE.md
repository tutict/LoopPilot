# CONTEXT COMPACTION MANIFEST TEMPLATE

Template Status: inactive

## Identity

- Manifest ID: none
- Checkpoint: none
- Project ID: none
- Loop ID: none
- Created: YYYY-MM-DD
- Created by: none
- Manifest Status: inactive

Allowed Manifest Status values are `inactive`, `draft`, `ready`, `superseded`,
and `invalid`.

## Current Objective

- None.

## Must Load

| Artifact | Source | Reason | Revalidate |
|---|---|---|---|
| None | none | none | no |

Must Load contains the latest user instruction, the active Project and Loop
contracts, authoritative Map and Ledgers, the current Checkpoint, current Scope and
invariants, open blocker or major Findings, authority, and evidence needed by the
exact Resume Point. It stays minimal and sufficient.

## Load On Demand

| Artifact | Trigger | Reason |
|---|---|---|
| None | none | none |

Load detailed Deliveries, Reviews, Rework records, ADRs, research, closed Findings,
or earlier Loop Closure evidence only when the Resume Point, a conflict, or
revalidation requires them.

## Must Not Load by Default

- Complete conversation history.
- Private chain-of-thought or hidden reasoning.
- Superseded drafts, large raw logs, and all artifacts from closed Loops.
- Unrelated files, closed low-risk work, and evidence that cannot affect resume.

This exclusion is a default context choice, not deletion or loss of evidence.

## Authoritative Sources

| State | Authority |
|---|---|
| Project scope | `PROJECT.md` |
| Loop status | `LOOP-MAP.md` |
| Task status | `TASK-LEDGER.md` |
| Finding status | `FINDING-LEDGER.md` |
| Recovery entry | `CHECKPOINT.md` |

## Relevant Detailed Artifacts

| Artifact | Relationship | Load class |
|---|---|---|
| None | none | on-demand |

## Compacted Facts

- FACT-000:
  - Statement: none
  - Source: none
  - Verified: no
  - Revalidate when: none

Only observable or explicitly decided facts may be compacted. Every fact requires
a Source, does not replace its original evidence, and cannot redefine status.

## Discarded or Archived Context

- None.

## Uncertainty and Revalidation

- None.

## Token and Context Rationale

- Context signal: unavailable or unverified
- Selection rationale: none
- Sufficiency risk: none
- Over-compaction risk: none
- Under-compaction risk: none

The Manifest explains why selected context is sufficient without claiming an exact
token balance or automatic compaction.

## Authority Note

This Manifest is not a Recovery authority or status source. It selects context for
the Checkpoint, does not duplicate complete Ledgers, does not expand Scope or
permissions, and does not start a session, load files, compact a model, or execute
the Resume Point. `CHECKPOINT.md` remains the only authoritative recovery entry.
