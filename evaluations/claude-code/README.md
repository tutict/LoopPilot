# Claude Code Evaluation Preparation

Claude Code is the reference host for Cross-Host Acceptance, and its observed
Host Acceptance Record gates the v1.0 Release Candidate. No such record exists
yet, so the Claude Code acceptance status remains unverified.

Future runs SHOULD copy the shared templates, record the exact Claude Code
surface, version, model, and Skill loading mode, and preserve only observable
actions and outputs. The acceptance summary for one evaluated combination
belongs in a single record file under this directory whose title starts with
`Host Acceptance Record`, authored per the
[Cross-Host Acceptance procedure](../../docs/cross-host-acceptance.md), with a
trace author who is not the independent reviewer.

Evaluators SHOULD use matched LoopPilot-loaded and control fixtures where
practical, covering at least one Lightweight-shaped and one Full-Loop-shaped
scenario. They MUST NOT treat this directory, a static validation pass, or a
single successful task as a formal compatibility claim.
