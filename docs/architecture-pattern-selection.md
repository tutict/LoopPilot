# Architecture Pattern Selection

Architecture patterns are tools selected from actual project needs. The
[Project Engineering Context](project-engineering-context.md) and concern matrix
provide evidence for choosing them. A pattern name is not an acceptance criterion
by itself, and its absence is not a Finding without a relevant requirement or risk.

## OOP

Object-oriented design can clarify responsibility, information hiding, cohesion,
collaboration, and encapsulation of change. It does not require every behavior or
data structure to become a class. Use the smallest object model that makes ownership
and invariants clearer.

## Dependency Injection

Dependency injection can make dependency direction explicit, replace
infrastructure implementations, isolate tests, and manage lifetimes. Constructor
injection is the platform-neutral default when injection has value. Not every
object belongs in a container, and introducing a container requires a concrete
lifecycle or composition benefit.

## Domain-Driven Design

DDD is justified only when domain complexity supports its cost:

| Complexity | Suggested approach |
|---|---|
| Simple | Transaction script or layered architecture |
| Moderate | Modular architecture with selected domain patterns |
| Complex | Bounded contexts, aggregates, value objects, and domain events |

A simple CRUD system MUST NOT be forced into full DDD. Domain terms, invariants, or
value objects may still be useful without adopting the complete pattern set.

## MVVM

MVVM primarily structures presentation code in Flutter, Android, desktop
applications, and reactive Web interfaces. A ViewModel owns presentation state,
user intent, and view coordination. It MUST NOT absorb infrastructure
implementations, cross-domain business invariants, or unbounded data access, and it
MUST NOT redefine backend domain boundaries.

## Zero-Copy

Zero-copy is a performance optimization, not a default architecture requirement.
Consider it only when there is an explicit performance objective, a benchmark shows
copying or I/O is a material bottleneck, the workload involves large files,
proxies, streaming, messaging, or high-throughput transfer, and the implementation
and platform costs are acceptable.

The evidence sequence is:

```text
performance objective
-> baseline benchmark
-> identify copying or I/O bottleneck
-> evaluate zero-copy
-> implement
-> benchmark again
```

Without performance evidence, a Reviewer MUST NOT create a Finding merely because
zero-copy was not used. When the benchmark identifies a relevant hotspot, the
Supervisor MAY add a Performance Reviewer and explicit acceptance criteria.

## Fitness Rules

A selected pattern MUST identify the problem it solves, the affected boundary, its
cost, and how the result will be verified. Reviews reject both under-engineering
that violates real constraints and over-engineering that adds ceremony without
outcome, risk, or recovery value.
