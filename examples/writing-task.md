# Illustrative Writing Trace

> This is a fictional trace for explaining LoopPilot behavior. No real document was
> drafted, reviewed, or delivered.

## User Request

> Write a one-page migration announcement for existing customers. Use a calm,
> direct tone, include the deadline and support channel, and make it ready for legal
> review.

## Goal

**Objective:** Produce a concise customer announcement that covers operationally
important migration information without making unsupported promises.

**Deliverables:** A one-page draft and a requirement-coverage check.

**Constraints:** Calm and direct tone; existing customers; no invented legal claims;
ready for review rather than approved for publication.

**Success criteria:**

1. State what changes and who is affected.
2. State the migration deadline and required customer action.
3. Include the supplied support channel.
4. Explain service impact and include any rollback or recovery guidance supplied in
   the brief.
5. Fit the requested length and tone.
6. Label the result as awaiting legal review.

**Available evidence:** Assume a fictional product brief containing the deadline,
support address, service-impact window, and recovery instructions.

**Unresolved blockers:** None in the illustrative setup.

## Initial Native Plan

1. Extract claims and mandatory content from the brief.
2. Draft a headline, context, action steps, impact note, support line, and review
   label.
3. Check requirement coverage, factual consistency, tone, and length.
4. Revise any failed criterion and repeat the targeted check.

## Execution and First Verification

**Illustrative action:** Produce a compact draft with the deadline, three customer
steps, and the support address.

**Illustrative requirement check:**

```text
what changes and audience: present
deadline and action: present
support channel: present
service impact: present
recovery guidance: missing
length and tone: pass
legal-review label: present
```

The fictional brief supplies recovery guidance, so the draft is incomplete. Fluent
prose does not compensate for the missing guidance.

## Replanning After the Coverage Failure

Classify the omission as a recoverable writing failure. Update the plan to:

1. retrieve the recovery wording from the supplied brief;
2. add it adjacent to the service-impact paragraph;
3. re-check only the affected factual and coverage criteria; and
4. re-read the full draft for length and tone regression.

The agent MUST NOT invent recovery steps. If the brief did not supply them, omit the
optional guidance and note that omission; it would not block completion of the
requested draft.

## Second Execution and Verification

**Illustrative action:** Add the brief's recovery guidance and tighten the context
paragraph to preserve the one-page limit.

**Illustrative evidence:** The second coverage check marks all six criteria present,
and the fictional word-count and tone review remain within the brief. Legal approval
is not claimed because it has not occurred.

## Ending Report

```text
Status: Completed
Completed work: one-page announcement with supplied recovery guidance and coverage review.
Verification evidence: illustrative brief-to-draft coverage, factual consistency, tone, and
length checks.
Remaining gaps: none within the requested draft scope; legal review and publication
remain separate future work.
Stop reason: the requested review-ready deliverable is complete; publication
was outside scope.
Best next action: submit the draft to the authorized legal reviewer.
```
