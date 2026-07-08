# AgentCollab Insight Skills

> 面向 Agent 平台的对话分析 Skill Pack —— 让每一次人机协作都可追溯、可度量、可洞察。

随着 CatPaw、Codex、Claude Code 等 AI 编程助手和 WorkBuddy 等 AI 办公助手的普及，人与 Agent 的对话日志沉淀在本地各处，却缺乏统一的分析手段：无法回答"我主要用 Agent 做什么""协作效率如何""哪些项目依赖最重""日常办公中 Agent 帮我解决了哪些问题"等问题。AgentCollab Insight Skills 正是为弥合这一缺口而设计。

**核心价值：**

- **看清协作全貌**：回答"我主要用 Agent 做什么""哪些项目对 Agent 依赖最重""办公中 Agent 帮我解决了哪些问题"，让分散的对话记录变成可回溯的协作档案。
- **发现效率瓶颈**：通过定量统计与定性洞察，识别高频低效的交互模式（如反复修改指令、工具调用冗余），为优化人机协作方式提供数据依据。
- **沉淀经验与方法**：将一次性对话中的思路、决策、解决方案提取为结构化报告，避免有价值的协作经验随会话结束而流失。
- **数据自主可控**：所有分析在本地完成，敏感对话内容不离开设备，用户完全掌控数据的存储、共享与销毁。


**项目优势：**

- **跨平台统一**：一套 Skill 同时适配 CatPaw、Codex、Claude Code（编程类）和 WorkBuddy（办公协作类）四大 Agent 平台，将异构对话日志归一化为统一数据格式，无需为每个平台单独造轮子。
- **六阶段流水线**：数据归一化 → 定量统计 → 分析材料包 → 全局/项目/会话三级中文定性报告，全流程自动化，将碎片化对话转化为结构化的协作画像。
- **隐私优先，全程本地**：所有数据仅从本地磁盘读取，产物写入项目 `.aci` 目录，原始日志永不上传。默认 `user-only` 模式只提取用户消息，不将 AI 回答正文加载到上下文。
- **即装即用，零依赖**：以 Agent Skill 形式分发，安装后在任意支持的 Agent 平台中直接对话触发分析；Python 标准库实现，无需安装任何第三方包。
---

## 目录

- [核心特性](#核心特性)
- [支持的 AI 编程助手](#支持的-ai-编程助手)
- [架构概览](#架构概览)
- [项目结构](#项目结构)
- [安装](#安装)
- [快速开始](#快速开始)
- [样例数据](#样例数据)
- [流水线参数](#流水线参数)
- [六阶段产物](#六阶段产物)
- [隐私与安全](#隐私与安全)
- [Skill 组合使用](#skill-组合使用)
- [开发与调试](#开发与调试)
- [后续计划](#后续计划)
- [许可证](#许可证)

---

## 核心特性

- **多源适配**：统一解析 CatPaw transcript、Codex rollout JSONL、Claude Code CLI/SDK JSONL、WorkBuddy JSONL 四类日志格式。
- **六阶段流水线**：数据归一化 → 定量统计 → 分析材料包 → 全局定性报告 → 项目定性报告 → 典型会话报告。
- **隐私优先**：默认 `user-only` 模式，仅提取用户消息，不加载 AI 回答正文到上下文；原始日志永不上传。
- **中文输出**：所有面向用户阅读的 Markdown 产物默认使用中文；元数据、路径、命令参数保持原样。
- **Skill 原生**：以 Agent Skill 形式分发，支持 `$aci-analysis` 等技能调用。
- **零依赖**：Python 标准库实现，无需安装第三方包。
- **可复现**：每次运行生成独立 `<source>-YYYYMMDDHHmm` 目录，附带 manifest 和日志。

---

## 支持的 AI 编程助手

| 数据源 | source 参数 | 原始数据位置 | 格式 |
|--------|-------------|-------------|------|
| CatPaw | `catpaw` | `.catpaw/projects/<project>/<session>/agent-transcripts/transcript.txt` | 纯文本 transcript |
| Codex | `codex` | `.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` | JSONL |
| Claude Code CLI | `claude_code` | `.claude/projects/<encoded-path>/<session-uuid>.jsonl` | JSONL |
| Claude Code SDK | `claude_code_sdk` | 同上，`entrypoint=sdk-py` | JSONL |
| WorkBuddy | `workbuddy` | `.workbuddy/projects/<encoded-cwd>/<conversation-id>.jsonl` | JSONL |

> Claude Code 默认只处理 CLI 会话；SDK 是显式选择项，需用户明确指定。

---

## 架构概览

```text
┌──────────────────────────────────────────────────────────────┐
│                     用户发起分析请求                          │
│            （在 AI 编程助手中调用 Skill）                     │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│              aci-analysis（总控 Skill）                       │
│  选择 source adapter → 确认模式 → 运行前 3 阶段               │
└──────────────┬───────────────────────────────────────────────┘
               │
     ┌─────────┼─────────┬─────────────┬─────────────┐
     ▼         ▼         ▼             ▼             ▼
  catpaw     codex   claude_code   claude_code_sdk  workbuddy
 adapter    adapter    adapter        adapter       adapter
     │         │         │             │             │
     └─────────┴────┬────┴─────────────┴─────────────┘
                    │
                    ▼
          ┌─────────────────┐
          │   前 3 阶段      │  ← aci_pipeline.py
          │  (ingest →      │
          │   quantitative →│
          │   packet)       │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │  AI 后 3 阶段    │  ← AI 读取 packet
          │  (全局报告 →     │     + prompt + template
          │   项目报告 →     │     继续生成中文报告
          │   会话报告)      │
          └─────────────────┘
```

**设计理念**：流水线负责确定性的数据处理（解析、统计、材料包生成），AI 负责定性洞察（读 packet 后写报告）。两者职责分离，确保数据准确性和分析灵活性。

---

## 项目结构

```text
AgentCollabInsightSkills/
├── README.md
├── .gitignore
├── samples/                              # 脱敏样例数据（真实分析产物）
│   └── catpaw-202607081412/             # 一次完整 CatPaw 分析的六阶段产物
│       ├── 01-数据归一化/user-only/      # 归一化 JSON（已脱敏，保留 3 条）
│       ├── 02-定量统计/user-only/        # 定量统计报告
│       ├── 03-分析材料包/                # 分析 Packet
│       ├── 04-全局定性报告/user-only/    # 全局洞察报告
│       ├── 05-项目定性报告/user-only/    # 项目洞察报告
│       ├── 06-典型会话报告/user-only/    # 会话洞察报告
│       └── _meta/                        # 运行清单与日志
│
└── skills/
    ├── aci-analysis/                    # 总控 Skill + 流水线
    │   ├── SKILL.md                     # Skill 入口定义
    │   ├── agents/
    │   │   └── openai.yaml              # Agent 界面配置
    │   ├── scripts/
    │   │   ├── aci_pipeline.py          # 主流水线入口
    │   │   └── aci_skillkit/
    │   │       ├── __init__.py
    │   │       ├── adapters.py          # 多源适配器（catpaw/codex/claude_code/workbuddy）
    │   │       ├── reporting.py         # 定量统计报告生成
    │   │       └── packets.py           # 分析材料包生成
    │   ├── assets/
    │   │   ├── prompts/                 # AI 定性分析 Prompt
    │   │   │   ├── user-only-analysis.md
    │   │   │   ├── full-analysis.md
    │   │   │   └── session-deep-analysis.md
    │   │   ├── templates/               # 报告模板
    │   │   │   ├── project-report.md
    │   │   │   ├── session-report.md
    │   │   │   └── cross-project-report.md
    │   │   └── fixtures/                # 各源最小样例数据（用于开发测试）
    │   │       ├── catpaw/
    │   │       ├── claude_code/
    │   │       ├── codex/
    │   │       └── workbuddy/
    │   └── references/
    │       └── pipeline-guide.md        # 流水线设计文档
    │
    ├── aci-catpaw-analysis/             # CatPaw 源指南
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   └── references/catpaw-format-guide.md
    │
    ├── aci-claude-code-analysis/        # Claude Code 源指南
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   └── references/claude-code-format-guide.md
    │
    ├── aci-codex-analysis/              # Codex 源指南
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   └── references/codex-format-guide.md
    │
    └── aci-workbuddy-analysis/          # WorkBuddy 源指南
        ├── SKILL.md
        ├── agents/openai.yaml
        └── references/workbuddy-format-guide.md
```

---

## 安装

克隆仓库后，选择你使用的助手，将 `skills/` 目录下的全部 Skill 复制到对应安装路径：

```bash
git clone https://github.com/<your-username>/AgentCollabInsightSkills.git
cd AgentCollabInsightSkills
```

**macOS / Linux：**

| 助手 | 安装命令 |
|------|---------|
| CatPaw | `cp -R skills/*/ ~/.catpaw/skills/` |
| Codex | `cp -R skills/*/ ~/.codex/skills/` |
| Claude Code | `cp -R skills/*/ ~/.claude/skills/` |
| WorkBuddy | `cp -R skills/*/ ~/.workbuddy/skills/` |

**Windows (PowerShell)：**

| 助手 | 安装命令 |
|------|---------|
| CatPaw | `Get-ChildItem ./skills -Directory \| Copy-Item -Recurse -Destination ~/.catpaw/skills/` |
| Codex | `Get-ChildItem ./skills -Directory \| Copy-Item -Recurse -Destination ~/.codex/skills/` |
| Claude Code | `Get-ChildItem ./skills -Directory \| Copy-Item -Recurse -Destination ~/.claude/skills/` |
| WorkBuddy | `Get-ChildItem ./skills -Directory \| Copy-Item -Recurse -Destination ~/.workbuddy/skills/` |

安装后，在对应的 AI 编程助手中直接使用 `$aci-analysis` 等技能调用即可。

---

## 快速开始

安装完成后，在你的 AI 编程助手中直接对话即可触发分析：

### 分析 CatPaw 对话

```
/aci-analysis 帮我分析我本地的 CatPaw 对话记录，生成 .aci 报告
```

AI 会自动调用 `$aci-analysis` 技能，识别数据源为 `catpaw` 后运行完整流水线。

### 分析 Codex 对话

```
/aci-analysis 分析我的 Codex session 数据，生成定性洞察报告
```

### 分析 Claude Code 对话

```
/aci-analysis 帮我分析 Claude Code 的本地对话日志
```

> 默认只处理 CLI 会话；如需分析 SDK 会话，明确告知 AI 即可。

### 分析 WorkBuddy 对话

```
/aci-analysis 分析我的 WorkBuddy 对话记录
```

---

## 样例数据

仓库提供两类样例数据，方便了解产物格式和快速验证：

### 真实分析产物（`samples/`）

`samples/catpaw-202607081412/` 是一次完整的 CatPaw 分析运行结果，包含全部六阶段产物。所有敏感信息已脱敏处理（用户名、IP、域名、项目名、业务关键词等均替换为占位符）。

```text
samples/catpaw-202607081412/
  01-数据归一化/user-only/    # 3 条脱敏会话 JSON
  02-定量统计/user-only/      # 用户消息统计报告
  03-分析材料包/              # 全局 / 项目 / 会话 Packet
  04-全局定性报告/user-only/  # 用户意图图谱、决策风格、协作模式
  05-项目定性报告/user-only/  # 项目级协作画像与改进建议
  06-典型会话报告/user-only/  # 会话级交互深度分析
  _meta/                      # 运行清单与日志
```

### 开发测试夹具（`skills/aci-analysis/assets/fixtures/`）

各数据源的最小化样例数据，用于开发和调试适配器解析逻辑：

| 数据源 | 夹具路径 | 说明 |
|--------|---------|------|
| CatPaw | `fixtures/catpaw/sample-project/` | 单条 transcript 样本 |
| Codex | `fixtures/codex/2026/07/07/` | 单条 rollout JSONL 样本 |
| Claude Code | `fixtures/claude_code/sample-project/` | CLI + SDK 各一条 JSONL |
| WorkBuddy | `fixtures/workbuddy/projects/sample-project/` | 单条 JSONL 样本 |

---

## 流水线参数

Skill 被调用时，AI 会根据用户意图自动配置以下参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--source` | — | 数据源：`catpaw`、`codex`、`claude_code`、`claude_code_sdk`、`workbuddy` |
| `--input` | — | 原始数据路径，可以是根目录、项目目录、日期目录或单个文件 |
| `--output` | `./.aci` | 输出根目录 |
| `--stages` | `ingest,quantitative,packet` | 要执行的阶段，逗号分隔 |
| `--mode` | `user-only` | 输出模式：`user-only` 或 `full,user-only` |
| `--entrypoint` | `cli` | Claude Code 入口过滤：`cli`、`sdk-py`、`all` |
| `--project-count` | `2` | 项目定性报告数量 |
| `--typical-count` | `2` | 典型会话报告数量 |
| `--typical-session-id` | — | 指定要深挖的会话 ID，可重复传入 |
| `--run-id` | 自动生成 | 固定运行目录名，如 `codex-202607071530` |

> `full` 模式仅在用户明确指定时启用，会额外写入包含 AI 回答、工具调用、成本等全量信息的 `full/` 目录。

---

## 六阶段产物

每次运行会在 `.aci/<source>-YYYYMMDDHHmm/` 下生成以下结构：

```text
.aci/
  <source>-YYYYMMDDHHmm/
    01-数据归一化/
      user-only/*.json          # 归一化后的会话 JSON（仅用户消息）
      full/*.json               # 完整会话 JSON（含 AI 回答，仅 full 模式）
    02-定量统计/
      user-only/*.md            # 用户消息统计报告
      full/*.md                 # 全量统计报告（仅 full 模式）
    03-分析材料包/
      *-analysis-packet.md      # 全局分析 Packet
      *-project-*-packet.md     # 项目分析 Packet（默认最多 2 个）
      *-session-*-packet.md     # 典型会话 Packet（默认最多 2 个）
    04-全局定性报告/
      user-only/*.md            # 全局中文定性洞察（AI 生成）
    05-项目定性报告/
      user-only/*.md            # 项目级中文定性洞察（AI 生成）
    06-典型会话报告/
      user-only/*.md            # 会话级中文定性洞察（AI 生成）
    _meta/
      manifests/<source>-run.json   # 运行清单
      logs/<source>-pipeline.log    # 运行日志
```

> 完整的六阶段产物示例可参考 [`samples/catpaw-202607081412/`](samples/catpaw-202607081412/)。

### 各阶段说明

| 阶段 | 执行者 | 产出 | 说明 |
|------|--------|------|------|
| 01-数据归一化 | 流水线 | JSON | 读取原始记录，归一化为 Project/Session/Turn/Block 统一结构 |
| 02-定量统计 | 流水线 | Markdown | 生成中文定量报告：会话数、轮次数、工具调用、项目分布、消息长度分布 |
| 03-分析材料包 | 流水线 | Markdown | 生成紧凑的分析 Packet，作为后续 AI 写报告的输入 |
| 04-全局定性报告 | AI | Markdown | 基于全局 Packet 写用户意图图谱、决策风格、协作模式等洞察 |
| 05-项目定性报告 | AI | Markdown | 基于项目 Packet 写单项目的协作画像与改进建议 |
| 06-典型会话报告 | AI | Markdown | 基于会话 Packet 深度分析代表性会话的交互过程 |

### 归一化数据结构

```json
{
  "session_id": "string",
  "session_name": "string",
  "source_type": "codex",
  "project_name": "string",
  "project_dir": "string",
  "created_at": "ISO timestamp or null",
  "model": "string or null",
  "turns": [
    {
      "turn_index": 1,
      "user_message": {
        "text": "用户输入文本",
        "slash_command": "/command or @skill:name"
      },
      "assistant_message": {
        "blocks": [
          { "type": "text", "text": "..." },
          { "type": "tool_use", "name": "Edit", "input": "..." },
          { "type": "tool_result", "name": "Edit", "content": "..." }
        ]
      }
    }
  ]
}
```

> `user-only` 模式下，`assistant_message.blocks` 为空数组，仅保留用户消息。

---

## 隐私与安全

- **本地处理**：所有数据仅从本地磁盘读取，产物写入指定 `.aci` 目录。
- **默认脱敏**：默认 `user-only` 模式只提取用户消息文本，不加载 AI 回答正文。
- **不传原始数据**：除非用户明确要求，不会上传原始日志到任何远程服务。
- **可控共享**：可安全共享 `.aci` 中的 reports 和 packets，原始 full transcripts 默认不共享。
- **样例已脱敏**：`samples/` 中的数据已对所有敏感信息（用户名、IP、域名、项目名、业务关键词等）进行脱敏处理，可安全公开。

---

## Skill 组合使用

本 Skill Pack 采用「总控 + 源指南」的分层设计：

| Skill | 角色 | 调用方式 |
|-------|------|---------|
| `aci-analysis` | **总控**：流水线入口，协调所有阶段 | `$aci-analysis` |
| `aci-catpaw-analysis` | CatPaw 源指南：transcript 解析规则与陷阱 | `$aci-catpaw-analysis` |
| `aci-claude-code-analysis` | Claude Code 源指南：CLI/SDK 分离、meta/sidechain 过滤 | `$aci-claude-code-analysis` |
| `aci-codex-analysis` | Codex 源指南：rollout JSONL 解析、Skill/Subagent 识别 | `$aci-codex-analysis` |
| `aci-workbuddy-analysis` | WorkBuddy 源指南：user_query 提取、system-reminder 过滤 | `$aci-workbuddy-analysis` |

**工作流程**：

1. 用户发起分析请求 → `$aci-analysis` 被调用
2. 总控确认数据源后，按需加载对应源指南 Skill
3. 流水线执行前 3 阶段（确定性数据处理）
4. AI 读取 Packet + Prompt + Template，完成后 3 阶段（定性洞察报告）

---

## 开发与调试

### 运行环境

- Python 3.10+
- 无第三方依赖
- 支持 Windows / macOS / Linux

### 样例数据

- **真实产物**：`samples/` 下提供了一次完整 CatPaw 分析的脱敏产物，可直接浏览各阶段报告内容。
- **开发夹具**：`skills/aci-analysis/assets/fixtures/` 下提供了各源的最小化样例数据，用于适配器单元测试。

### 项目结构约定

- 新增数据源适配器：在 `adapters.py` 中添加 `parse_<source>()` 函数，并在 `parse_source()` 中注册。
- 修改报告格式：编辑 `reporting.py`（定量统计）或 `assets/templates/`（定性报告模板）。
- 修改分析维度：编辑 `assets/prompts/` 下的 Prompt 文件。

---

## 后续计划

### 近期

- **更多数据源适配器**：新增 Cursor、Trae、QoderCode、GitHub Copilot 等 Agent 平台的日志解析支持。
- **跨源合并分析**：支持同时导入多个平台的对话日志，生成跨平台协作画像，回答"我在哪个 Agent 上花的时间最多"等问题。

### 中期

- **HTML 可视化报告**：在 Markdown 报告基础上，额外生成可交互的 HTML 仪表板，支持图表筛选与下钻。
- **自定义分析维度**：允许用户通过自定义 Prompt 模板扩展定性分析维度，无需修改流水线代码。

### 远期

- **Skill Marketplace 分发**：通过 Agent Skill Marketplace 实现一键安装与版本更新。
- **多语言报告输出**：在中文报告基础上增加英文、日文等报告语言选项。

> 欢迎在 [Issues](https://github.com/samihyypia/agent-collab-insight-skills/issues) 中提交功能建议或反馈。

---

## 许可证

MIT License
