# Option B RC Candidate — Work Record

## Scope and plan

Supervisor and Integrator: `/root`. Implementation remains single-owner.
Mode: Lightweight with independent Standards and Spec review. This bounded policy
amendment does not require Full Loop Ledgers or new protocol roles.
The user authorized implementation, verification, commits, and a safe dedicated
branch push on 2026-10-24. This record is task context, not standing authority.
External research cannot settle this local policy change; remote and runtime facts
require separate observations.

1. Repair RC designation, receipt, and summary binding with negative regressions.
2. Synchronize the policy, templates, checklist, and candidate notes.
3. Obtain independent Standards and Spec decisions and resolve blocking findings.
4. Run required verification, commit, and recheck the committed boundary.
5. Inspect current remote refs and push only the dedicated candidate branch.

## Baseline

- Observed source repository: `C:/Users/tutic/IdeaProjects/LoopPilot`, branch `main`, clean tracked status.
- Observed starting commit: `1bc184cf7a8b1ffc613e101911985adfc93f6c9d`.
- Observed starting tree: `187fdc74006b84aa9fb49640b896106e1331053a`.
- Observed task branch: `codex/option-b-rc-candidate`.
- Observed target: `origin`, `https://github.com/tutict/LoopPilot.git`.
- Observed remote read: `main` is `aacbde449a6dbc8723d5c866033ac195017a90e5`;
  no candidate branch or RC tag was returned. Recheck before push. The source
  baseline contains 13 commits beyond that remote main; pushing the new branch
  makes that baseline reachable without updating remote main.
- Draft originally isolated in the app-managed worktree. Its out-of-sandbox writes
  repeatedly timed out in automatic approval. The draft remains preserved there.
- A local, independent clone under ignored `.tmp/option-b-rc-work-local` permits
  authorized edits without modifying the source checkout or its Git metadata.
- Only the fifteen task draft files were copied into that clone. No task commit
  or push exists yet; no unrelated change was copied.

## Independent review contract — TASK-001

- Parent goal: verified Option B successor and safely pushed, candidly labelled RC candidate.
- Assignee and independent Reviewer: `/root/option_b_review`.
- Objective: assess the complete task diff against repository Standards and the user's Spec.
- Allowed scope: read task instructions, approved defaults, repository rules, diff, and evidence; run non-destructive local checks.
- Forbidden scope: implementation edits, configuration changes, commit, push, release, deployment, credential disclosure, external communication, or parent-completion claims.
- Deliverable: separate Standards and Spec decisions with reproducible findings and evidence.
- Success criteria: C01–C08 hold; Gate 4 thresholds and Gate 5 disclosures remain; no retrospective or automatic-switch path; public validation covers the RC lifecycle and malformed evidence; no unrelated change.
- Required evidence: inspect final diff and tests; observe focused and public-entry checks; reconcile the Integrator's full verification results.
- Dependencies: revised implementation and final verification evidence from `/root`.
- Research inputs: none; this is a local contract change.
- Skill assignment: base host read/search/test tools; no Skill installation is authorized.
- Checklist item: this single-owner delivery has one independent review and no delegated implementation.
- Revision budget: three substantive correction rounds; change strategy if exhausted.
- Initial review: Standards `revision-requested`; Spec `revision-requested`.
- Initial evidence: Reviewer reported seven blocking binding/lifecycle/schema issues; 12 narrow unit tests passed without covering those defects. These are attributed observations, not final verification.
- Second independent review found two further projection gaps. Public-entry
  negative cases reproduced them; Candidate Reference and Environment projections
  now match receipts. The original and second judgments remain preserved.
- Final independent judgment: Standards pass, Spec pass, overall approved.
  The Reviewer inspected the full 1,141-test PASS, compared 20 relevant files with
  the export, verified 29 neutral shared-state files, ran static/Skill/whitespace
  checks, and inspected all 35 SVGs. No unresolved substantive finding remains.
  This does not close Phase 11, Gate 4, Gate 6, or behavioral acceptance.
- Task integration and review are archived under `docs/release/option-b-review/`.
  The shipped `.looppilot/` templates remain neutral and contain no task instance.

## Verification and delivery

- Observed focused suite: 39 tests passed on CPython 3.13.13 / PyYAML 6.0.3.
- Observed static validator, Skill quick validation, Python compilation, and
  diff whitespace checks passed at the draft boundary.
- Observed Mermaid CLI 11.16.0 rendered all 35 diagrams to nonempty SVGs.
- Interrupted full-suite attempts are not passes. Windows PowerShell lacked its
  standard module path; restoring it only for the test process made `Get-FileHash`
  available. Repository-internal TEMP caused old copytree fixtures to recurse.
  A system-TEMP checkout then exposed Git Bash's `/c/.../Temp` versus `/tmp`
  alias mismatch. No installer, original test assertion, model/provider/endpoint,
  or persistent configuration changed.
- Observed all 14 existing architecture/installer tests pass in the clean
  workspace-path verification checkout with external TEMP and standard modules.
- A public-entry C08 regression demonstrated that Git replacement refs could
  forge successor ancestry. Boundary reads now ignore replacement objects; the
  new negative case was observed failing before correction and passing after it.
- Full suite of 1,141 methods completed in 1808.177 seconds with exit 0, no
  failures/errors/skips, in
  `C:/Users/tutic/IdeaProjects/LoopPilot/.tmp/verify-rc-clean`; output is
  `.tmp/full-regression-1141.log` in the implementation checkout. All 19
  implementation, test, policy, template, and Gate files match the tested export
  byte-for-byte. Starting
  checkout discovery contained 1,098 methods; the historical 910 cases remain.
- Formal acceptance prerequisites remain unverified; Gate 4 is unmet.
- At this pre-publication reporting boundary, no task commit, push, tag, release,
  or formal acceptance is claimed. Git and the separate delivery record establish
  the exact committed/pushed SHA after those operations actually occur.

## Publication boundary

Full execution session `71663` completed successfully and independent review is
approved. Final reporting files and the restored neutral state receive static
checks before the commit; implementation bytes remain those tested. The first
qualifying commit establishes the branch-local successor boundary, not a release.
The latest task instruction permits a normal push of the dedicated candidate
branch after a fresh ref check; it grants no release or deployment authority.
Publication results are recorded separately after observation, avoiding a
self-referential commit claim. Future agents must recheck current user authority.

## Verification commands and limits

| Command/check | Observed result |
| --- | --- |
| `py -3.13 -m unittest discover -s tests -p 'test_*.py' -v` | 1,141 tests, 1808.177 seconds, OK; zero failures/errors/skips. |
| `py -3.13 scripts/validate.py` | PASS; zero new eligible Host Acceptance packages, five historical packages remain ineligible. |
| `git diff --check` | PASS. |
| `py -3.13 <skill-creator>/scripts/quick_validate.py .` | Skill valid; the installed system Skill creator script was used. |
| `py -3.13 -m compileall -q scripts tests` | PASS. |
| `py -3.13 scripts/validate.py --extract-mermaid <temporary-output>` plus pinned `mmdc` | Mermaid CLI 11.16.0: all 35 sources rendered, all 35 SVGs nonempty; Reviewer also parsed their XML. |

The full run used the clean workspace-path export, external Windows TEMP, and a
process-local standard Windows PowerShell module path. Its output is retained in
the implementation checkout's ignored `.tmp/full-regression-1141.log`; no raw log
is committed. Only final factual status/review reports advance after that run;
implementation and acceptance-contract bytes are compared with the tested export.
Final reporting and neutral-state changes are checked through the public static
validator. No required maintenance check is omitted or waived. Frontend checks
are conditionally inapplicable: this change affects only Python and Markdown and
there is no affected frontend package or TypeScript configuration.

Formal acceptance arms were not run. Actual runtime identity, installation Hash B,
applicable C2 preconditions, a trusted operator index and independent behavioral
review remain unverified; these are required before formal acceptance, not waived.
Gate 4 is unmet. Gate 5 retains explicit named-host unverified disclosures. Phase 11
review and Major/Critical disposition remain separate RC readiness conditions.
No release tag, GitHub Release, deployment, or compatibility claim is produced.

## Changed files and necessity

| File | Reason |
| --- | --- |
| `docs/release/option-b-reference-successor.md` | Single named C01–C08 amendment with unchanged gates, historical isolation, and forward boundary. |
| `docs/release/option-b-reference-approval.md` | Attribute the bounded one-time user authorization without inventing an approving identity or standing permission. |
| `docs/release/rc-candidate-reference.md` | Fix this RC to Codex before arms; distinguish unknown configured and actual identities from finalization. |
| `docs/release/rc-candidate-decision.md` | Record this candidate's unmet Gate 4, unrun acceptance, and non-release status without rewriting old decisions. |
| `docs/cross-host-acceptance.md` | Route applicable RCs to the successor while retaining earlier roles and all thresholds. |
| `docs/release/v1.0-rc-checklist.md` | Track the designated Reference, unchanged gates, current version section, and remaining formal prerequisites. |
| `docs/evaluation-evidence-integrity.md` | Define the exact v2 RC extension, observation provenance, Git/timing checks, and summary/environment binding. |
| `docs/validation.md` | Describe new maintenance coverage and the local Git-read boundary without claiming host behavior. |
| `evaluations/templates/environment.md` | Separate configuration declarations from actual identity-event projections. |
| `evaluations/templates/host-acceptance-record.md` | Carry RC/successor/designation identity and explicit Reference versus Candidate evidence role. |
| `scripts/option_b_validation.py` | Enforce policy/designation constraints, committed frozen combinations, raw Git ancestry, timing, and observed identity links. |
| `scripts/evaluation_evidence_validation.py` | Whitelist run schema versions, pass the real repository root, and bind v2 packages and readable projections to accepted summaries. |
| `scripts/cross_host_acceptance_validation.py` | Validate RC fields when present while preserving old and non-RC records. |
| `scripts/validate.py` | Register the bounded policy checker and required supporting files in the existing public entry point. |
| `tests/test_option_b_successor.py` | Check uniqueness, eligibility, timing declarations, unchanged thresholds, and successor binding. |
| `tests/test_option_b_evidence.py` | Exercise positive/negative public-entry RC lifecycles, history preservation, malformed data, identity projections, and Git replacement rejection. |
| `tests/option_b_fixture.py` | Build explicitly synthetic Git/receipt/index specimens around actual local subprocess output; no Host Acceptance claim. |
| `tests/test_cross_host_acceptance.py` | Add three RC-binding negatives and optional RC fields to the existing fixture without dropping old assertions. |
| `README.md` | Disclose this RC's selected Reference and all hosts' continuing unverified status. |
| `CHANGELOG.md` | Name the authorized development candidate and explicitly retain `NOT_RELEASE_READY`. |
| `docs/release/option-b-work-record.md` | Preserve scope, plan, baseline, verification boundaries, and per-file rationale. |
| `docs/release/option-b-review/TASK-001.md` | Archive the scoped implementation/review contract, not standing authority or live product state. |
| `docs/release/option-b-review/REVIEW-TASK-001.md` | Preserve the independent Standards/Spec decision and review history. |
| `docs/release/option-b-review/initial-review.md` | Preserve the original revision-requested judgment without rewriting it. |
| `docs/release/option-b-review/DELEGATION.md` | Archive coordination facts while restoring the shipped neutral templates. |

No historical evaluation, historical RC decision, Phase 15 boundary, installer,
distribution manifest/version, host/provider/model/endpoint configuration, Skill
core, protocol role, Ledger, threshold, release, or deployment is changed here.
