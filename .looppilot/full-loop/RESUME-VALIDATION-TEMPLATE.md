# RESUME VALIDATION REPORT TEMPLATE

Template Status: inactive

## Identity

- Validation ID: none
- Checkpoint: none
- Project ID: none
- Loop ID: none
- Performed: YYYY-MM-DD
- Performed by: none
- Validation Status: inactive

Allowed Validation Status values are `inactive`, `in-progress`, `validated`,
`validated-with-corrections`, `blocked`, `invalid-checkpoint`, `replan-required`,
and `cancelled`.

## Latest User Instruction Check

- Latest instruction identified: no
- Scope changed: unknown
- Requirements cancelled: unknown
- New constraints: none
- Result: not-evaluated

## Repository Reality Check

- Repository: none
- Branch: none
- Actual HEAD: none
- Expected HEAD: none
- Working tree: not-inspected
- Untracked files: not-inspected
- Result: not-evaluated

## Authoritative State Check

### Project

- Source: `PROJECT.md`
- Result: not-evaluated

### Loop Map

- Source: `LOOP-MAP.md`
- Result: not-evaluated

### Task Ledger

- Source: `TASK-LEDGER.md`
- Result: not-evaluated

### Finding Ledger

- Source: `FINDING-LEDGER.md`
- Result: not-evaluated

### Checkpoint

- Source: `CHECKPOINT.md`
- Result: not-evaluated

## Referenced Artifact Check

| Artifact | Exists | Current | Consistent | Result |
|---|---|---|---|---|
| None | no | no | no | pending |

## Evidence Revalidation

| Evidence | Reproduced | Result | Action |
|---|---|---|---|
| None | no | pending | none |

## Capability Check

- Required Skills available: unknown
- Required tools available: unknown
- Network access available: unknown
- Independent Reviewer available: unknown
- Commit authority unchanged: unknown
- Other authority unchanged: unknown

## Detected Conflicts

- None.

## Corrections Applied

- None.

## Invalidated Claims

- None.

## Resume Point Validation

- Checkpoint Resume Point: none
- Still applicable: unknown
- Inputs available: unknown
- Expected result still valid: unknown
- Revised Resume Point: none

## Validation Decision

- Decision: not-evaluated
- Reason: none
- Safe to resume: no
- Required escalation: none

## Authority Note

Resume Validation may correct stale recovery facts using the latest user
instruction and observable repository, file, tool, and Ledger reality. It cannot
expand Project or Loop Scope, change risk acceptance or Finding severity, or grant
modify, delete, commit, push, release, or deploy permission. It is evidence, not a
Recovery authority; `CHECKPOINT.md` remains the only authoritative recovery entry.
