# WorkBuddy Format Guide

## Scope

Use this guide when parsing WorkBuddy local JSONL from `.workbuddy/projects`.
WorkBuddy messages are top-level JSONL records without the same wrapper shape as Codex.

## Directory Shape

```text
.workbuddy/projects/
  <encoded-cwd>/
    <conversation-id>.jsonl
```

Use the encoded cwd as the project grouping key.

## Parsing Rules

- Use `message` records with `role=user` as turn boundaries.
- Extract actual user intent from `<user_query>...</user_query>`.
- Filter `<system-reminder>...</system-reminder>` context from user-only analysis.
- Map function-call records to `tool_use` blocks.
- Map function-call-result records to `tool_result` blocks.
- Default model can be recorded as `auto` when no concrete model is exposed.
- Skip `reasoning` and `file-history-snapshot` by default unless the user asks about them.

## Known Pitfalls

- User messages may contain thousands of characters of system context.
- Service-level 500 errors can dominate task success even when individual tool calls succeed.
- Windows compatibility issues may appear around MCP, GTK/PDF tooling, Chromium, or sandboxing.
- WorkBuddy skill commands may use `@skill:...`, `@scene#...`, or media-style markers.

## Analysis Angles

- Skill-driven design workflows.
- One-shot versus iterative session behavior.
- Service error rate and task completion rate.
- Short-command / long-PRD message split.
- Windows compatibility friction.
