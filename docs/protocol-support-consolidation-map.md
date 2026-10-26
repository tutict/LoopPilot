# Protocol Support Consolidation Map

This review map records the bounded prose reductions in this cleanup. The comparison
source is `main` commit `5c4a52290de8e59527048e931f2334b06009c2c7` before the edits.
A row identifies the original paragraphs, the retained rules, and their reference
locations. The mode-selection owner retains its complete definitions and ordered
sequence unchanged; the two other documents shorten only their repeated summaries.
Existing headings, Mermaid blocks, deterministic cases, machine constraints, role
boundaries, conditions, exceptions, negations, and MUST/SHOULD/MAY strengths remain.

| Baseline location and old explanation | Retained rule in this change | Detailed rule / reference |
| --- | --- | --- |
| `docs/coordination-necessity-and-delegation-fallback.md`, `## Product Risk and Coordination Risk` (baseline lines 5–12): two paragraphs repeated the risk categories and the two-axis definitions. | Product Risk still sets appropriate Review, Validation, and Evidence Depth; Coordination Risk still concerns structured work between owners and determines whether Full Loop governance is justified; high product risk alone still does not require multiple Workers. The complete security, data, transaction, idempotency, sensitive-data, compatibility, partial-success, and production-impact categories remain in the unchanged owner. | Edited [summary](coordination-necessity-and-delegation-fallback.md#product-risk-and-coordination-risk) → [complete definitions](mode-selection-and-escalation.md#product-risk-and-coordination-necessity). |
| `docs/coordination-necessity-and-delegation-fallback.md`, `## Coordination Necessity` (baseline lines 29–34): the paragraph repeated the ordered reassessment before its evidence table. | Follow the existing order: Product Risk → required minimum review, validation, and evidence depth → Coordination Necessity → mode. Full Loop only when coordination requires it; otherwise Lightweight or the applicable non-Full-Loop path is allowed. Risk-only changes preserve mode; specialist review adds scrutiny rather than coordination. The pre-selection evidence table and all later cases, criteria, exceptions, and failure-budget rules remain unchanged. | Edited [Coordination Necessity](coordination-necessity-and-delegation-fallback.md#coordination-necessity) → [Authority and Timing](mode-selection-and-escalation.md#authority-and-timing). |
| `docs/multi-agent-coordination.md`, `## Proportional Delegation and Specialist Review` (baseline lines 420–436): the summary repeated the mode sequence and specialist list. | One-owner Lightweight and `MAY` use a risk-matched specialist; stop affected implementation when required on new risk/scope/specialist-review evidence; follow the unchanged order; risk-only changes preserve mode. Full Loop still requires coordination; otherwise Lightweight or the applicable non-Full-Loop path is allowed without dropping mandatory reviews, checks, or budget stops. Two or more Workers, independent integration proof, and needs beyond one owner plus bounded review remain; Reviewer presence alone does not require coordination. Full Loop selects only risk-matched specialists; 429/timeout/no-output remains an infrastructure incident that never permits fabricated Delivery or self-review and may block verification. | Edited [summary](multi-agent-coordination.md#proportional-delegation-and-specialist-review) → [ordered reassessment](mode-selection-and-escalation.md#authority-and-timing), [specialist-reviewed Lightweight](coordination-necessity-and-delegation-fallback.md#specialist-reviewed-lightweight), and the unchanged [risk-to-specialist table](mode-selection-and-escalation.md#specialist-reviewers). |

The mapping is a review aid, not a second protocol authority. If a summary conflicts
with an owning document, the owning document and the existing Task protocol govern.
Supervisor, Worker, Reviewer, and Integrator responsibilities remain in
[multi-agent coordination](multi-agent-coordination.md#roles-and-final-accountability);
legal transitions still refer to the existing
[Task protocol](../.looppilot/tasks/README.md#status-lifecycle). No new simultaneous
loading requirement is introduced. Independent maintenance Standards/Spec review
must assess semantic equivalence; passing static checks alone cannot prove it.

The unchanged portions of both edited support files retain their original bytes;
edited paragraphs use LF endings so ordinary Git whitespace checks remain active.
No Git whitespace setting, attribute, validator, or test assertion was relaxed.

## Size and serialization boundary

Whitespace-separated word counts, including the unchanged tables and code blocks,
are 1,228 → 1,191 for the coordination criteria and 2,860 → 2,824 for multi-agent
coordination: 73 fewer words across the two support documents. This is a text-size
observation, not a token count or a behavioral result. The two edited documents use
LF line endings so ordinary Git whitespace checks can validate them; that
serialization change carries no additional prose or rule change. The mode-selection
owner, `SKILL.md`, `AGENTS.md`, historical evidence policy, and all five report blobs
retain their original bytes.
