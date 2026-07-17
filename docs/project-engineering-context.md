# Project Engineering Context

Engineering work starts with the user problem, not a file list. Before decomposing
implementation, the Supervisor establishes enough context to explain who is
affected, which outcomes matter, which business invariants cannot change, and which
engineering risks constrain delivery. The inactive
[Project template](../.looppilot/PROJECT-TEMPLATE.md) provides the first-stage
capture structure.

## Context Areas

**Problem, users, and use cases** define the user-visible outcome, participating
actors, positive paths, exceptional paths, included scope, and excluded scope.
Deliverables and acceptance criteria MUST map back to these outcomes.

**Domain model** identifies relevant entities, value objects, aggregates, domain
events, and business invariants. These concepts are selected for explanatory and
consistency value; they do not force DDD.

**Data** covers sources, ownership, lifecycle, consistency, retention, and
migration. A data change also considers privacy, compatibility, rollback limits,
and operational recovery.

**Concurrency** covers shared resources, races, idempotency, ordering, and the need
for locking or optimistic concurrency. The absence of concurrency work SHOULD be a
reasoned result, not an assumption.

**Identity and permissions** cover authentication, roles, resource ownership,
authorization rules, and audit requirements. Functional behavior is incomplete
when required access boundaries are not defined.

**Security** records trust boundaries, sensitive data, input risks, secret handling,
and abuse cases. Security requirements feed Tasks, acceptance criteria, and risk
review only when relevant.

**Observability** covers logs, metrics, traces, audit events, and alerts needed to
operate or investigate the result.

**Delivery and operations** cover deployment, configuration, health checks,
rollback, gray release, and data rollback limitations.

**Evolution** covers API compatibility, schema migration, version strategy,
deprecation, and extension points.

**Team boundaries** identify module, review, integration, and release ownership.
They clarify responsibility without granting commit, push, release, or deployment
authority.

## Engineering Concern Matrix

The Supervisor assesses every relevant dimension before the Contract Barrier.
Only a concern with real impact creates a Task, acceptance criterion, Reviewer,
Finding, or architecture decision. Empty or not-applicable dimensions do not create
ceremonial work.

| Concern | Impact | Required Work | Reviewer |
|---|---|---|---|
| Users | | | |
| Business Rules | | | |
| Data | | | |
| Concurrency | | | |
| Permissions | | | |
| Security | | | |
| Logging | | | |
| Monitoring | | | |
| Rollback | | | |
| Gray Release | | | |
| Operations | | | |
| Version Evolution | | | |
| Team Collaboration | | | |

The Project template keeps the matrix blank and inactive. An active Project fills
only observed or explicitly supplied facts, labels unknowns, and links resulting
work to the Loop Map or decisions rather than duplicating their state.

## Business Invariants and Contracts

Business invariants MUST be identified before dependent parallel work begins.
Interfaces and data contracts that multiple Tasks share MUST be stable enough to
cross the Contract Barrier. When an invariant or contract is uncertain, the
Supervisor either resolves it, serializes dependent work, or narrows the Loop.

A Loop boundary is based on business cohesion, dependency and integration risk, not
a mechanical frontend/backend split. Work that shares a user model, security rule,
transaction boundary, or acceptance flow MAY belong in one Loop even when it spans
modules. Independent outcomes with separate contracts and acceptance can be
separate Loops.

## Reviewer Matrix

Spec Review and Standards Review remain mandatory axes for every reviewed Loop.
The Supervisor adds specialist review in proportion to the concern matrix:

| Reviewer | Trigger |
|---|---|
| Domain Reviewer | Complex business state, invariants, or DDD |
| Data Reviewer | Schema, migration, consistency, retention, or privacy |
| Concurrency Reviewer | Concurrent requests, locks, messages, idempotency, or ordering |
| Security Reviewer | Authentication, authorization, input, secrets, or sensitive data |
| Operations Reviewer | Deployment, rollback, gray release, monitoring, or recovery |
| Performance Reviewer | An explicit performance objective or measured hotspot |
| Architecture Reviewer | Cross-module boundaries or a major pattern change |
| Frontend Reviewer | MVVM, state synchronization, interaction, or accessibility |
| Compatibility Reviewer | API, schema, or version evolution |

Specialist Findings feed the applicable Spec or Standards decision. A simple Loop
MUST NOT load every specialist. Reviewers receive the relevant integrated diff,
test and build results, and only the context needed for their assigned risk.

## Readiness and Loop Review

Task-level Readiness Check evaluates scope compliance, Delivery completeness,
required evidence, obvious blockers, and merge readiness. It permits integration;
it does not accept the Loop.

Loop-level review starts after the Integration Barrier and examines the unified
result. It runs both permanent axes, activates required specialists, creates
Findings, drives bounded rework, and supplies evidence for the Supervisor's
three-layer acceptance decision.
