# Prompt

- Evaluation ID: EVAL-004
- Scenario ID: named fixture `host-skill-loading-probe`
- Variant: LoopPilot loaded
- Task fixture: installation, discovery, and Skill-loading verification

## Exact User Input

### Arm A, in-session explicit invocation, host 2.1.224, model claude-opus-5

The operating session was driving a repository task. At the point of the
invocation the session issued no natural-language prompt to itself; it called
the host's `Skill` tool directly. The exact recorded tool input, transcribed
from the host session transcript, entry 149, was:

```json
{"skill": "loop-pilot"}
```

The instruction that authorized this call was the operator's Phase 13-A
requirement, quoted verbatim from the operator's message:

```text
3. Skill loading

执行真实 Skill invocation。

记录：

- prompt
- invocation method
- loaded content evidence
- returned behavior
```

No other prompt text was supplied to the `Skill` tool. The tool takes a skill
name, not a natural-language prompt.

### Arm B1, headless discovery probe, host 2.1.226, model claude-fable-5[1m]

Exact prompt file contents:

```text
Reply with exactly the single token DISCOVERY_PROBE_OK and nothing else.
```

Exact command:

```powershell
claude -p $p --output-format stream-json --verbose --no-session-persistence `
  --tools "" --model opus --no-session-persistence --max-budget-usd 0.25
```

### Arm B2, headless loading probe, host 2.1.226, model claude-fable-5[1m]

Exact prompt file contents:

```text
Invoke the loop-pilot Skill using the Skill tool, then answer strictly from the text the Skill tool returned.

Report exactly these four items, each on its own line:

L1: the full title text of section 15, without the number.
L2: the four primary outcome names listed under section 7, comma-separated, in document order.
L3: the complete sentence from section 11 that contains the phrase "Governance Artifact target".
L4: the two-word title of the unnumbered heading that appears between section 4 and section 5.

Rules:
- You have no file-reading tool. Do not guess, reconstruct, or infer any answer from the Skill name or description.
- If the Skill tool does not return the Skill body text, reply with exactly SKILL_LOAD_FAILED and nothing else.
- If any single item is not present in the returned text, write NOT_FOUND for that line.
```

Exact command:

```powershell
claude -p $p --output-format stream-json --verbose --no-session-persistence `
  --tools "Skill" --permission-mode dontAsk --max-budget-usd 0.50
```

The four requested items were chosen because each appears only in the body of
[`SKILL.md`](../../../SKILL.md) and none appears in the Skill frontmatter
`name` or `description` that a host exposes for discovery. With `--tools "Skill"`
the run had no file-reading tool, so the prompt is answerable only from content
the `Skill` tool returned.

## Input Boundary

Supplied to Arm A: the operator's Phase 13 task message, the repository working
tree, the host's default tool set, and the host's own registered Skill
directory. The session had already read `SKILL.md` from the repository before
the invocation, so Arm A does not establish that the answer content could only
have come from the Skill tool. Arm A's evidence is the recorded tool call and
the recorded injected content, not a reconstruction quiz.

Supplied to Arm B1: the prompt above and no tools. Supplied to Arm B2: the
prompt above and the `Skill` tool only. Both Arm B runs started in an empty
working directory with no repository files, no project-scope Skill directory,
no `CLAUDE.md`, and no prior conversation.

Not supplied to any arm: expected answers, evaluator hints, the contents of
`SKILL.md` as prompt text, or any statement of what the run was meant to show.
