---
name: aci-workbuddy-analysis
description: WorkBuddy-specific workflow for the portable ACI transcript analyzer. Use when Codex needs to parse, normalize, quantify, or prepare qualitative packets from local WorkBuddy .workbuddy/projects JSONL data, including user_query extraction, system-reminder filtering, Skill usage, service error, and Windows compatibility analysis.
---

# ACI WorkBuddy Analysis

当数据源是 WorkBuddy JSONL 时，和 `$aci-analysis` 一起使用。默认只做 `user-only`，输出产物正文必须使用中文。

## Input

接受 `.workbuddy/projects` 根目录、项目目录、日期目录，或单个 WorkBuddy JSONL 文件。

## Command

```powershell
python <skills-root>\aci-analysis\scripts\aci_pipeline.py `
  --source workbuddy `
  --input <workbuddy-path> `
  --output <target-workspace>\.aci `
  --stages ingest,quantitative,packet `
  --mode user-only `
  --project-count 2 `
  --typical-count 2
```

## Workflow

1. 确认输入是否为 WorkBuddy 顶层 JSONL 或 `.workbuddy/projects` 结构；不确定时回到 `$aci-analysis` 的 source 确认流程。
2. 修改 `<user_query>`、`<system-reminder>`、function call/result 或错误解析前，读取 `references/workbuddy-format-guide.md`。
3. CLI 提取 user query、过滤 system reminder、映射 function call/result，并生成前 3 阶段。
4. Codex 继续写 `04-全局定性报告/user-only/*.md`。
5. Codex 默认写最多 2 个 `05-项目定性报告/user-only/*.md`。
6. Codex 默认写最多 2 个 `06-典型会话报告/user-only/*.md`。
7. 只有用户明确要求 assistant/tool/result 全量细节时，才追加 `--mode full,user-only`。

## Six Stages

- `01-数据归一化/user-only/*.json`
- `02-定量统计/user-only/*.md`
- `03-分析材料包/*.md`
- `04-全局定性报告/user-only/*.md`
- `05-项目定性报告/user-only/*.md`
- `06-典型会话报告/user-only/*.md`

## Notes

WorkBuddy 报告应特别关注 Skill 使用、服务错误、Windows 兼容性问题和用户重复修正模式。
