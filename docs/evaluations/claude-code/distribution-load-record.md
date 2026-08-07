# Claude Code Distribution Load Record

## Scope

This Distribution-003-B record probes one installed LoopPilot package on Claude
Code. It is distribution evidence only and is not a Host Acceptance Record.

- Observed date: 2026-08-07
- Host: Claude Code 2.1.223
- Result: `PARTIALLY OBSERVED`
- Installation source commit: `a4c83f8b3ce90f6e388cf32b398a4d01667f9b66`
- Source version: `unreleased`

The repository currently declares no host with accepted support. Claude Code was
selected because it is the documented reference host, has destination preparation,
and was the user's preferred Distribution-003 probe target. Selection does not
upgrade it to a supported or accepted host.

## Environment and Installation

| Component | Observed value |
|---|---|
| Operating system | Microsoft Windows NT 10.0.26200.0 |
| Claude Code CLI | 2.1.223 |
| Isolated config | `.tmp/distribution-003-claude-profile-20260807` |
| Isolated installed Skill | `<isolated-config>/skills/loop-pilot` |
| Project installed Skill | `.tmp/distribution-003-claude-project-20260807/.claude/skills/loop-pilot` |
| Installation output | Version `unreleased`, commit `a4c83f8b3ce90f6e388cf32b398a4d01667f9b66` |

Both destinations were populated by the official PowerShell installer from the
same isolated corrective source. The project installation allowed use of the
existing authenticated host profile without modifying the user's live Skill
directory.

## Probe Commands

```powershell
claude.exe --version
claude.exe auth status --json

$env:CLAUDE_CONFIG_DIR = '<isolated-config>'
claude.exe -p 'Return the word probe.' `
  --output-format stream-json --verbose --no-session-persistence --tools ''

claude.exe -p '<bounded Skill and Read probe>' `
  --output-format stream-json --verbose --no-session-persistence `
  --permission-mode dontAsk --tools 'Skill,Read' --max-budget-usd 0.50

py -3.13 <isolated-installed-skill>\scripts\validate.py `
  --root <isolated-installed-skill>
```

No credential value was printed or recorded.

## Results

| Requirement | Result | Observed evidence |
|---|---|---|
| Installed directory structure | PASS | `SKILL.md`, `docs/lifecycle.md`, `docs/safety-and-stopping.md`, and `.looppilot/README.md` existed in the isolated installation. |
| Skill discovery | PASS | In an otherwise empty working directory, the isolated Claude config emitted a system initialization event containing `loop-pilot` in both `skills` and `slash_commands`. |
| Skill content loaded | UNVERIFIED | No `Skill` tool event completed. The authenticated call ended after ten HTTP 429 retries. |
| Supporting references present | PASS | The copied validator printed `Static validation passed`; required reference files existed. |
| Supporting references read by host | UNVERIFIED | No `Read` tool event completed because the model call never started. |
| Installed Skill identity | PASS | Installed frontmatter contained `name: loop-pilot`; installed and source `SKILL.md` blobs both hashed to `6e0f26a9e948659541f88fc066e4e70dfcb31b0b`. |

The discovery result is attributed to the isolated installation because the final
initialization probe used the isolated config from an empty directory and listed
one `loop-pilot` Skill. Static reference validation demonstrates that the
installation output is internally resolvable; it does not substitute for a host
`Read` event.

## Failed Attempts and Classification

### Host Configuration Gap D003-HCG-001

The isolated config reported:

```json
{"loggedIn":false,"authMethod":"none","apiProvider":"firstParty"}
```

It could initialize and discover the Skill but could not perform an authenticated
model turn. This is a `Host Configuration Gap`, not a LoopPilot defect.

### Execution Infrastructure Incident D003-EII-003

The authenticated project probe inside the process sandbox exhausted ten retries
and ended with:

```text
UNKNOWN_CERTIFICATE_VERIFICATION_ERROR
```

The same command outside the sandbox reached the service, so this is an execution
certificate boundary rather than a protocol or package failure.

### Host Capability Unverified D003-HCU-001

Outside the sandbox, the authenticated host initialized and discovered
`loop-pilot`, but all ten API attempts returned HTTP 429 and the command ended with:

```text
API Error: Request rejected (429) - Service Unavailable
```

No assistant model turn, `Skill` tool event, or `Read` tool event occurred. Skill
content loading and host-level supporting-reference resolution therefore remain
`Host Capability Unverified`. This evidence does not support classifying a
LoopPilot defect.

## Conclusion

Claude Code 2.1.223 discovered the isolated installed Skill. The package structure,
identity, and static relative references are verified. Content loading and
host-executed reference reads remain unverified because the authenticated service
was unavailable. No Host Acceptance status changes.
