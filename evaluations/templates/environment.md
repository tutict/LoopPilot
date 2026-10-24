# Environment

- Evaluation ID:
- Scenario ID:
- Date and time:
- Host:
- Host version:
- Model:
- LoopPilot commit:
- Skill loading mode:
- Task fixture:
- Available tools and state:
- Granted authority:
- Material environment constraints:
- Limitation state:
- Unverified limitations:
- RC version:
- Successor ID:
- Reference designation ID:
- Reference designation record:
- Reference Host:
- Configured model:
- Configured provider:
- Configured endpoint:
- Host version identity evidence:
- Provider identity evidence:
- Endpoint identity evidence:
- Model identity evidence:

`Scenario ID` references the numbered scenario in
[`tests/scenarios.md`](../../tests/scenarios.md) or the named fixture the run
exercises, so a later reader can reproduce the same case. `Unverified
limitations` names what this environment could not establish, such as an
unavailable tool, an unobservable host feature, or a state the evaluator could
not inspect.

`Limitation state` and `Unverified limitations` project the same approved
version-2 review receipt. Use `unverified`, `unresolved`, or `resolved` explicitly;
do not replace an unresolved receipt with a resolved prose claim. See the
[evidence integrity contract](../../docs/evaluation-evidence-integrity.md).

The RC fields apply only to successor-bound runs. Distinguish configuration
declarations from the observed runtime identity, and preserve hash-bound public
identity source artifacts; a requested alias is insufficient. Unknown identity
blocks formal acceptance. The version-2 run receipt owns the RC binding and
runtime observation events; these fields are its readable projection.
