# v1 Migration

Phase 11 is backward compatible. Existing Full Loop history is not rewritten and
historical closed Loops are not reopened solely because they predate Lifecycle
Assertions.

For an existing active Full Loop:

1. Confirm `PROJECT.md`, `LOOP-MAP.md`, the current `TASK-LEDGER.md` and
   `FINDING-LEDGER.md`, and root `CHECKPOINT.md` are the authority sources.
2. Add the `Revision` column to the Task Ledger when it is absent; do not create a
   revision Ledger.
3. Replace unnecessary mutable values in Handoff, Checklist, Context Compaction,
   Delivery, Integration, Review, and Results with authority references.
4. For a necessary snapshot, declare `## Lifecycle Projections`, its authority,
   and the observed 40-character Git boundary.
5. Before the next Closure decision, add the finite `## Lifecycle Consistency`
   snapshot from the current template and run `python scripts/validate.py`.
6. Route drift through the existing Process Finding and rework/reverification
   flow. Authority remains unchanged unless its own authorized transition occurs.

The public validator warns when a legacy `LOOP-CLOSURE.md` has no Lifecycle
Consistency section. Absence alone is not a hard failure, but a declared
`## Lifecycle Projections` table is validated even in a legacy Loop. Once the
Closure section is present, its available authority and exact projection values
are validated as well. A recorded Git boundary stays valid after the Closure is
committed: the validator accepts the current HEAD or any of its ancestors and
rejects unknown SHAs. A simple Lightweight project without `.looppilot/loops/`
loads no Full Loop closure machinery.

A canonical assertion name written into a supporting `.looppilot/` artifact
outside a declared section is a hard failure, not a warning, because such a copy
records no authority, no boundary, and no derived status. This applies to
Lightweight repositories too. Migrating an existing artifact means one of three
edits: replace the copy with an authority reference, move it into a
`## Lifecycle Projections` table with its boundary, or move a format example
into a fenced block. Ordinary prose that names a Task or Finding without using
the assertion grammar is unaffected.

Do not add `LIFECYCLE-LEDGER.md`, `ASSERTION-LEDGER.md`, `STATE-DATABASE.md`, a
state graph, database, daemon, or automatic correction service. LoopPilot remains
a host-native, filesystem protocol with no runtime dependency.
