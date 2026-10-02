---
name: lp
description: Short explicit alias for the installed LoopPilot protocol. Use only for /lp or $lp. Do not use for any other task.
---

# Installed LoopPilot Alias

This is the sole short-trigger owner, not a second protocol or a grant of authority.
It is managed at `<installation>/shortcuts/lp/SKILL.md`, not as a user-scope copy.

1. Use the host-confirmed path of this installed alias. Resolve `../../SKILL.md`
   relative to its own directory, in the same installation root selected for
   `/loop-pilot`. Frontmatter `name` alone never establishes identity.
2. Require that root's `.looppilot-installation` to list both `SKILL.md` and
   `shortcuts/lp/SKILL.md` with current SHA-256 hashes. Neither file may be locally
   customized, and the root MUST NOT be a repository checkout. The host must confirm
   that `/loop-pilot` selects this same installed root, not a different candidate.
3. If identity or resolution is missing, ambiguous, or inconsistent, stop and report
   the gap. MUST NOT search the current directory or repository, fall back to a
   repository-local Skill, or choose another installed body merely by name. Any
   explicit source override requires a new, session-scoped Owner instruction.
4. Read that canonical file and carry out the user's request under it. This alias
   supplies no execution, recovery, completion, or release authority.

The maintenance-only resolver tests this filesystem binding; it is not a runtime
requirement. Host command registration and discovery remain unverified until
separately observed. Do not claim this static contract proves host compatibility.
