---
name: aci-catpaw-analysis
description: CatPaw-specific workflow for the portable ACI transcript analyzer. Use when Codex needs to parse, normalize, quantify, or prepare qualitative packets from CatPaw transcript.txt data under .catpaw/projects, including CatPaw turn-boundary and tool-call parsing issues.
---

# ACI CatPaw Analysis

当数据源是 CatPaw transcript 时，和 `$aci-analysis` 一起使用。默认只做 `user-only`，输出产物正文必须使用中文。

## Input

接受 `.catpaw/projects` 根目录、项目目录、会话目录，或单个 `transcript.txt`。

## Command

```powershell
python <skills-root>\aci-analysis\scripts\aci_pipeline.py `
  --source catpaw `
  --input <catpaw-path> `
  --output <target-workspace>\.aci `
  --stages ingest,quantitative,packet `
  --mode user-only `
  --project-count 2 `
  --typical-count 2
```

## Workflow

1. 确认输入是否为 CatPaw transcript 结构；不确定时回到 `$aci-analysis` 的 source 确认流程。
2. 修改 transcript 分段、工具调用或轮次边界解析前，读取 `references/catpaw-format-guide.md`。
3. CLI 读取 transcript，解析 user/tool/assistant blocks，并生成前 3 阶段。
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

CatPaw 的关键风险是 transcript 边界和工具输出混入正文。定性报告默认只基于 user-only 材料。
