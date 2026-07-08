---
name: aci-codex-analysis
description: Codex-specific workflow for the portable ACI transcript analyzer. Use when Codex needs to parse, normalize, quantify, or prepare qualitative packets from local Codex session JSONL such as .codex/sessions or rollout-*.jsonl, including Skill, subagent, tool, cost, and Plan-mode analysis.
---

# ACI Codex Analysis

当数据源是 Codex session data 时，和 `$aci-analysis` 一起使用。默认只做 `user-only`，避免把完整 JSONL 放入上下文；输出产物正文必须使用中文。

## Input

接受 `.codex/sessions`、日期目录、包含 `rollout-*.jsonl` 的目录，或单个 `rollout-*.jsonl`。

## Command

```powershell
python <skills-root>\aci-analysis\scripts\aci_pipeline.py `
  --source codex `
  --input <codex-path> `
  --output <target-workspace>\.aci `
  --stages ingest,quantitative,packet `
  --mode user-only `
  --project-count 2 `
  --typical-count 2
```

## Workflow

1. 确认输入是否为 Codex JSONL 或 `.codex/sessions` 日期结构；不确定时回到 `$aci-analysis` 的 source 确认流程。
2. 遇到未知事件、Plan/Subagent/Skill 字段、成本或耗时字段时，读取 `references/codex-format-guide.md`。
3. CLI 生成 `01-数据归一化/user-only/*.json`、`02-定量统计/user-only/*.md`、`03-分析材料包/*.md`。
4. Codex 继续读取全局 packet，写 `04-全局定性报告/user-only/*.md`。
5. Codex 继续读取项目 packet，默认写最多 2 个 `05-项目定性报告/user-only/*.md`。
6. Codex 继续读取典型会话 packet，默认写最多 2 个 `06-典型会话报告/user-only/*.md`。
7. 只有用户明确要求工具调用、assistant 行为、成本、耗时、模型细节或 full 对照时，才追加 `--mode full,user-only`。

## Six Stages

- `01-数据归一化/user-only/*.json`
- `02-定量统计/user-only/*.md`
- `03-分析材料包/*.md`
- `04-全局定性报告/user-only/*.md`
- `05-项目定性报告/user-only/*.md`
- `06-典型会话报告/user-only/*.md`

## Notes

Codex 日志可能很大。优先使用 user-only packet 和摘要化会话材料，避免直接加载完整 raw JSONL。
