# ACI Pipeline Guide

## Audience

这个 skill pack 面向想分析本地 AI 编程助手对话记录的个人开发者和 power user。团队可以复用同一套 skills，并共享脱敏后的 `.aci` 产物。

## Privacy Defaults

- 只从本地磁盘读取原始助手日志。
- 所有产物写入指定 `.aci` 目录。
- 默认共享 reports、packets 或 user-only JSON，不共享 raw full transcripts。
- 除非用户明确要求，不上传原始数据。

## Default Report Mode

默认报告模式是 `user-only`，优先分析用户意图、决策风格、协作模式和需求演进。只有用户明确要求分析 assistant 行为、工具调用、成本、耗时、模型或完整上下文时，才使用 `--mode full,user-only` 或 `--mode full`。

## Output Language

所有面向用户阅读的 `.aci` Markdown 产物默认使用中文，包括定量报告、分析 packet、典型会话 packet 和最终定性报告。元数据、代码、文件名、路径、命令参数、JSON 字段名和原始对话文本保持原样。

## Source-Time Layout

默认输出按 `<source>-YYYYMMDDHHmm` 组织。CLI 生成前 3 阶段；第 4、5、6 阶段由 Codex 读取 packet、prompt 和模板后继续写出。

```text
.aci/
  <source>-YYYYMMDDHHmm/
    01-数据归一化/user-only/*.json
    02-定量统计/user-only/*.md
    03-分析材料包/*.md
    04-全局定性报告/user-only/*.md
    05-项目定性报告/user-only/*.md
    06-典型会话报告/user-only/*.md
    _meta/manifests/<source>-run.json
    _meta/logs/<source>-pipeline.log
```

full 模式只在用户显式指定时额外写入对应 `full/` 目录。新运行不双写旧目录。

## Six Stages

1. `01-数据归一化`：读取原始记录，归一化为 Project/Session/Turn/Block JSON。
2. `02-定量统计`：生成中文定量报告，并包含项目分布。
3. `03-分析材料包`：生成中文全局 packet、默认最多 2 个项目 packet、默认最多 2 个典型会话 packet。
4. `04-全局定性报告`：Codex 基于全局 packet 写中文 user-only 全局洞察。
5. `05-项目定性报告`：Codex 基于项目 packet 写中文 user-only 项目洞察，默认最多 2 个项目。
6. `06-典型会话报告`：Codex 基于典型会话 packet 写中文会话洞察，默认最多 2 个会话。

## Data Contract

Normalized sessions 使用这个形状：

```json
{
  "session_id": "string",
  "session_name": "string",
  "source_type": "codex",
  "project_name": "string",
  "created_at": "ISO timestamp or null",
  "turns": [
    {
      "turn_index": 1,
      "user_message": {"text": "string", "slash_command": "optional"},
      "assistant_message": {"blocks": []}
    }
  ]
}
```

Full JSON 保留 assistant 与 tool blocks。User-only JSON 只保留 metadata 和 user text。

## Qualitative Packet Contract

Packets 不是最终报告，而是后续 AI 写作阶段的紧凑输入，包含：

- source、run、project summary
- output paths
- quantitative highlights
- sample user turns
- prompt/template assets
- required report destinations
