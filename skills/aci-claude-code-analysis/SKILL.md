---
name: aci-claude-code-analysis
description: Claude Code-specific workflow for the portable ACI transcript analyzer. Use when Codex needs to parse, normalize, separate CLI and SDK sessions, quantify, or prepare qualitative packets from local Claude Code .claude/projects JSONL data.
---

# ACI Claude Code Analysis

当数据源是 Claude Code 时，和 `$aci-analysis` 一起使用。默认只处理 Claude Code CLI；SDK 是显式选择项，默认不提示、不纳入。输出产物正文必须使用中文。

## Input

接受 `.claude/projects`、编码后的项目目录，或单个 Claude Code JSONL 文件。

## Command

```powershell
python <skills-root>\aci-analysis\scripts\aci_pipeline.py `
  --source claude_code `
  --input <claude-code-path> `
  --output <target-workspace>\.aci `
  --entrypoint cli `
  --stages ingest,quantitative,packet `
  --mode user-only `
  --project-count 2 `
  --typical-count 2
```

只有用户明确要求 SDK 自动化会话时，才使用 `--source claude_code_sdk` 或 `--entrypoint sdk-py|all`。

## Workflow

1. 确认输入是否为 `.claude/projects`、项目目录或 JSONL；只是泛称 Claude 时不要自动假设 SDK。
2. 修改 CLI/SDK 过滤、meta/sidechain 过滤或 tool_result 映射前，读取 `references/claude-code-format-guide.md`。
3. CLI 生成 `01-数据归一化/user-only/*.json`、`02-定量统计/user-only/*.md`、`03-分析材料包/*.md`。
4. Codex 继续写 `04-全局定性报告/user-only/*.md`。
5. Codex 默认写最多 2 个 `05-项目定性报告/user-only/*.md`。
6. Codex 默认写最多 2 个 `06-典型会话报告/user-only/*.md`。
7. 只有用户明确要求 assistant thinking、工具结果、模型、耗时分析或 full 对照时，才追加 `--mode full,user-only`。

## Six Stages

- `01-数据归一化/user-only/*.json`
- `02-定量统计/user-only/*.md`
- `03-分析材料包/*.md`
- `04-全局定性报告/user-only/*.md`
- `05-项目定性报告/user-only/*.md`
- `06-典型会话报告/user-only/*.md`

显式请求 SDK 时，额外输出 `claude_code_sdk-YYYYMMDDHHmm/` 运行目录和对应六阶段产物。

## Notes

Claude Code 的 tool result 可能存放在 user 类型记录中，但语义上属于 assistant 输出。不要把 `isMeta` 或 `isSidechain` 消息计为主会话用户轮次。
