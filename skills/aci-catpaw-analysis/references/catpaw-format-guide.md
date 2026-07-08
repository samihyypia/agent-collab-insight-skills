# CatPaw Format Guide

## Scope

Use this guide when parsing CatPaw local conversation data from `.catpaw/projects`.
CatPaw stores plain-text transcripts, so parser safety depends on stateful boundary detection.

## Directory Shape

```text
.catpaw/projects/
  <encoded-project>/
    <session-id>/
      agent-transcripts/transcript.txt
      agent-tools/
      terminals/
```

The project directory name is an encoded path. Treat it as a stable grouping key, not a fully
reversible path.

## Transcript Markers

- `user:` starts a user message region.
- `<user_query>...</user_query>` wraps the actual user input.
- `[Thinking]` marks assistant reasoning text.
- `[Tool call] <name>` marks a tool call.
- `[Tool result] <name>` marks a tool result.
- `assistant:` marks assistant natural-language output.
- `<system_reminder>` is system context, not direct user intent.

## Parsing Rules

- Start a new turn when a real `user:` / `<user_query>` block starts.
- Ignore `user:` strings inside fenced code blocks or tool-call argument blocks.
- Keep a small lookahead window before cutting a turn boundary.
- If there is no native timestamp, use transcript file `mtime` as approximate `created_at`.
- Associate tool results with the nearest unmatched prior tool call by tool name when no explicit ID exists.
- Create user-only JSON by removing assistant blocks from full JSON.

## Known Pitfalls

- `user:` may appear inside code examples, command output, or tool parameters.
- CatPaw transcripts may omit structured tool-result IDs.
- Large sessions need summarization packets instead of direct context loading.
- PowerShell terminals may display Chinese incorrectly unless output is written as UTF-8.

## Analysis Angles

- SpecKit full-chain usage: clarify, plan, tasks, analyze, implement.
- Paste-error-fix loops across frontend, backend, SSE, curl, Docker, or build logs.
- "Validate then package" behavior where a workflow is turned into a reusable skill.
- Localization friction when generated artifacts need Chinese defaults.
