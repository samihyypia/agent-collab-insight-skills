# Codex Format Guide

## Scope

Use this guide when parsing local Codex session JSONL from `.codex/sessions` or `rollout-*.jsonl`.
Codex logs can be large, so normalize first and analyze via packets.

## Directory Shape

```text
.codex/sessions/
  YYYY/MM/DD/
    rollout-*.jsonl
```

Some installations or exports may group sessions differently. Prefer recursive discovery of
`rollout-*.jsonl`.

## Parsing Rules

- Prefer explicit task or turn events such as `task_started` and `task_complete` when present.
- Treat user-message events as turn starts when explicit boundaries are absent.
- Map assistant text to text blocks.
- Map function calls/tool uses to `tool_use` blocks.
- Map function-call outputs/tool results to `tool_result` blocks.
- Preserve cost, duration, model, cwd/session name, and created time when available.
- Create user-only JSON by keeping session metadata and user message text only.

## Known Pitfalls

- Raw logs can exceed hundreds of MB; never load all raw files into model context.
- Reasoning payloads may be encrypted or not useful for qualitative analysis.
- Tool names vary by surface: shell, apply_patch, web_search, image_generation, subagent, skill.
- File names and event shapes may change; keep adapter logic defensive.

## Analysis Angles

- Skill creation and skill consumption behavior.
- Subagent delegation and parallelization.
- Plan ownership and user-authored implementation plans.
- Correction rate and correction granularity.
- Prompt/template reuse and batch expansion from prototypes.
- Chinese/English mismatch as workflow friction.
