---
name: aci-analysis
description: Portable local analysis toolkit for AI coding assistant transcripts. Use when Codex needs to ingest, normalize, quantify, or prepare qualitative analysis packets for CatPaw, Codex, Claude Code CLI/SDK, or WorkBuddy conversation logs, with outputs written under a project-local .aci directory.
---

# ACI Analysis

将这个 skill 作为本地、私有、可迁移的 AI 编程助手对话分析总控入口。默认只处理 `user-only`，避免全量记录带来过高 token 成本；只有用户明确要求 full、assistant/tool/result/cost/duration/model 等细节时，才启用 `--mode full,user-only` 或 `--mode full`。面向用户阅读的 Markdown 产物必须使用中文；元数据、代码、文件名、路径、JSON 字段名和命令参数保持原样。

## Command

```powershell
python <skills-root>\aci-analysis\scripts\aci_pipeline.py `
  --source catpaw|codex|claude_code|claude_code_sdk|workbuddy `
  --input <raw-data-path> `
  --output <target-workspace>\.aci `
  --stages ingest,quantitative,packet `
  --mode user-only `
  --project-count 2 `
  --typical-count 2
```

可选传入 `--run-id <source>-YYYYMMDDHHmm` 固定运行目录。Claude Code 默认只处理 CLI；只有用户明确要求 SDK 时，才使用 `--source claude_code_sdk` 或 `--entrypoint sdk-py|all`，默认提示列表里不要主动列出 SDK。

## Workflow

1. 根据用户请求或路径选择 source adapter。若用户没有明确要求，先让用户确认，并只列出 `catpaw`、`codex`、`claude_code`、`workbuddy`。
2. 确认输入范围、输出目录和模式。默认 `user-only`；full 只在用户明确指定时启用。
3. 运行 CLI 生成前 3 阶段：`01-数据归一化`、`02-定量统计`、`03-分析材料包`。
4. 读取全局 packet、prompt 和模板，Codex 继续写 `04-全局定性报告`。
5. 读取项目 packet，Codex 默认写最多 2 个 `05-项目定性报告`，除非用户明确指定更多。
6. 读取典型会话 packet，Codex 默认写最多 2 个 `06-典型会话报告`，除非用户明确指定更多或指定会话 ID。

## Six Stages

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

- `01-数据归一化`：读取原始记录，归一化为 Project/Session/Turn/Block JSON。
- `02-定量统计`：生成中文定量报告，并保留项目分布。
- `03-分析材料包`：生成中文全局 packet、默认最多 2 个项目 packet、默认最多 2 个典型会话 packet。
- `04-全局定性报告`：Codex 基于全局 packet 写中文 user-only 全局洞察。
- `05-项目定性报告`：Codex 基于项目 packet 写中文 user-only 项目洞察，默认最多 2 个项目。
- `06-典型会话报告`：Codex 基于典型会话 packet 写中文会话洞察，默认最多 2 个会话。

full 模式只在用户显式指定时额外写入对应 `full/` 目录。

## Inputs

- `--source`：`catpaw`、`codex`、`claude_code`、`claude_code_sdk`、`workbuddy`。
- `--input`：原始数据路径，可以是根目录、项目目录、日期目录或单个会话文件。
- `--output`：目标 `.aci` 目录，默认 `./.aci`。
- `--run-id`：可选固定运行目录名；默认自动生成 `<source>-YYYYMMDDHHmm`。
- `--project-count`：默认 `2`；除非用户明确指定更多，否则不要超过 2。
- `--typical-count`：默认 `2`；除非用户明确指定更多，否则不要超过 2。
- `--typical-session-id`：可重复传入，用于指定要深挖的典型会话。

## Source Guides

仅在需要平台细节时加载：

- CatPaw：使用 `$aci-catpaw-analysis`
- Codex：使用 `$aci-codex-analysis`
- Claude Code CLI/SDK：使用 `$aci-claude-code-analysis`
- WorkBuddy：使用 `$aci-workbuddy-analysis`


## 使用须知

- 本工具仅限分析用户本人拥有的对话日志。分析他人数据前必须获得数据所有者的明确授权，并遵守《个人信息保护法》《数据安全法》等适用法律法规。
- `.aci` 产物（含 user-only 模式）可能包含对话中的敏感信息（业务逻辑、代码片段、文件路径等），共享前请确认已脱敏。
- 未经授权分析他人数据可能构成违法行为，由使用者承担全部法律责任。详见项目 README 中的「使用条款与免责声明」。