# Claude Code Format Guide

## Scope

Use this guide when parsing Claude Code local JSONL data from `.claude/projects`.
The same skill covers CLI sessions and SDK automation sessions.

## Directory Shape

```text
.claude/projects/
  <encoded-project-path>/
    <session-uuid>.jsonl
    subagents/
```

`session-env` may exist but can be empty. Treat encoded project paths as approximate grouping keys.

## CLI vs SDK

- Read `entrypoint` when present.
- Use `entrypoint=cli` for interactive Claude Code sessions.
- Use `entrypoint=sdk-py` for SDK automation sessions.
- Keep CLI and SDK outputs separate: `claude_code` and `claude_code_sdk`.

## Parsing Rules

- Use `type=user` with string content as the primary turn boundary.
- Do not count `isMeta=true` messages as user turns; attach or ignore them as metadata.
- Do not include `isSidechain=true` messages in primary-session analysis.
- Tool results may appear in `type=user` records but semantically belong to assistant output.
- Preserve plaintext `thinking` as assistant text or reasoning blocks when useful.
- Preserve titles, model, version, token, and duration fields when available.

## Known Pitfalls

- User messages can be either real text or tool-result carriers.
- Subagent data can inflate counts if sidechain filtering is skipped.
- SDK sessions are usually short and numerous; analyze separately from CLI behavior.
- Claude Code may include special tools such as Agent, Skill, and `mcp__*`.

## Analysis Angles

- Deep multi-turn collaboration in CLI sessions.
- Edit/Read/Bash balance.
- Plan Mode usage.
- SpecKit or structured development flows.
- Model switching and version distribution.
- SDK automation patterns as separate from human-AI collaboration.
