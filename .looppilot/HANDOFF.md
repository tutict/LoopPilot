# Agent Handoff

Status: none
Updated: YYYY-MM-DD
From: none
To: next available agent

## Current Objective

No active handoff.

## Authority Pointers

- Project: see `PROJECT.md`.
- Loop: see `LOOP-MAP.md`.
- Current Task status, owner, and revision: see the current `TASK-LEDGER.md`.
- Finding status and severity: see the current `FINDING-LEDGER.md`.
- Recovery boundary and exact Resume Point: see root `CHECKPOINT.md`.

## Completed

- None.

## Observed Evidence

- None.

## Remaining Work

- None.

## Blockers

- None.

## Risks and Constraints

- None.

## Current Mode and Incidents

- Current mode: none
- Load profile: none
- Execution Infrastructure Incidents affecting resume: none

Load only current-mode context. Do not import Full Loop history into a
Lightweight handoff by default, and do not relabel an incident as a Product
Finding without evidence.

## Checklist Status

- Procedure projection only; see `CHECKLIST.md`.

## Resume Point

- See the exact Resume Point in root `CHECKPOINT.md` when recovery is active.

## Context Pressure

- See root `CHECKPOINT.md` when recovery is active.

## Active Research Brief

- None.

## Active Skill Assignments

- None.

## Recommended Next Action

- None.

## Do Not Assume

- The receiving Agent MUST re-check the latest user instruction and authorization.
- The receiving Agent MUST re-check the working tree, native Plan, files, tests,
  and actual tool state.
- The receiving Agent MUST label inference as `inference` and unchecked information
  as `unverified`.
- The receiving Agent MUST NOT treat a handoff as authority for consequential action.
- A handoff is not a Task Contract and does not assign or transfer Supervisor,
  Worker, Reviewer, or Integrator responsibility.
- In Full Loop Mode, a handoff MAY reference the current Checkpoint but MUST NOT
  become a second Recovery authority or override its exact Resume Point.
- A handoff MAY reference Project Acceptance or a Final Delivery Report but MUST
  NOT imply Project closure, release authority, deployment, or user acknowledgement.
- A necessary copied lifecycle value MUST be labelled as a derived projection with
  its authority and observed Git boundary; otherwise use an authority pointer.
