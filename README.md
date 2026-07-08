# AgentCollab Insight Skills

> 把多源 Agent 对话日志转成协作画像的 Skill Pack —— 让每一次人机协作都可追溯、可度量、可洞察。

CatPaw、Codex、Claude Code、WorkBuddy……人与 Agent 的对话日志分散在本地各处，格式各异，却没有任何工具能把它们拉到一起，告诉你"你的协作模式到底是什么样"。AgentCollab Insight Skills 把这些异构日志归一化为统一数据格式，跑完一条六阶段流水线，产出定量统计与中文定性洞察报告。全程本地处理，零第三方依赖，即装即用。

**核心价值：**

- **看清协作全貌**：回答"我主要用 Agent 做什么""哪些项目对 Agent 依赖最重""办公中 Agent 帮我解决了哪些问题"，让分散的对话记录变成可回溯的协作档案。
- **发现效率瓶颈**：通过定量统计与定性洞察，识别高频低效的交互模式（如反复修改指令、工具调用冗余），为优化人机协作方式提供数据依据。
- **沉淀经验方法**：将一次性对话中的思路、决策、解决方案提取为结构化报告，避免有价值的协作经验随会话结束而流失。

**适合谁**：日常重度使用 AI 编程助手或办公助手，想回看自己的协作模式、发现效率瓶颈、沉淀经验方法的开发者与产品经理。

---

## 30 秒跑起来

### 1. 安装

```bash
git clone https://github.com/<your-username>/AgentCollabInsightSkills.git
cd AgentCollabInsightSkills
```

选择你使用的助手，复制 `skills/` 下的全部 Skill 到对应目录：

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

### 2. 发起分析

安装后，在 AI 编程助手中直接对话即可触发：

```
/aci-analysis 帮我分析我本地的 CatPaw 对话记录，生成 .aci 报告
```

AI 会自动调用 `$aci-analysis` 技能，识别数据源后运行完整流水线。将 `CatPaw` 换成 `Codex`、`Claude Code`、`WorkBuddy` 即可分析对应数据源。

> Claude Code 默认只处理 CLI 会话；如需分析 SDK 会话，明确告知 AI 即可。

### 3. 查看产物

分析完成后，`.aci/<source>-YYYYMMDDHHmm/` 下会生成六阶段产物。从 `04-全局定性报告` 开始读起——那是 AI 写给你的中文洞察报告。完整示例可参考 [`samples/catpaw-202607081412/`](samples/catpaw-202607081412/)。

---

## 它吃什么、吐什么

### 支持的数据源

| 数据源 | source 参数 | 原始数据位置 | 格式 |
|--------|-------------|-------------|------|
| CatPaw | `catpaw` | `.catpaw/projects/<project>/<session>/agent-transcripts/transcript.txt` | 纯文本 transcript |
| Codex | `codex` | `.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` | JSONL |
| Claude Code CLI | `claude_code` | `.claude/projects/<encoded-path>/<session-uuid>.jsonl` | JSONL |
| Claude Code SDK | `claude_code_sdk` | 同上，`entrypoint=sdk-py` | JSONL |
| WorkBuddy | `workbuddy` | `.workbuddy/projects/<encoded-cwd>/<conversation-id>.jsonl` | JSONL |

### 六阶段产物一览

| 阶段 | 执行者 | 产出 | 说明 |
|------|--------|------|------|
| 01-数据归一化 | 流水线 | JSON | 原始日志归一化为 Project/Session/Turn/Block 统一结构 |
| 02-定量统计 | 流水线 | Markdown | 会话数、轮次数、工具调用、项目分布、消息长度分布 |
| 03-分析材料包 | 流水线 | Markdown | 紧凑的分析 Packet，作为 AI 写报告的输入 |
| 04-全局定性报告 | AI | Markdown | 用户意图图谱、决策风格、协作模式等全局洞察 |
| 05-项目定性报告 | AI | Markdown | 单项目的协作画像与改进建议 |
| 06-典型会话报告 | AI | Markdown | 代表性会话的交互过程深度分析 |

产物目录结构：

```text
.aci/
  <source>-YYYYMMDDHHmm/
    01-数据归一化/
      user-only/*.json          # 仅用户消息
      full/*.json               # 含 AI 回答（仅 full 模式）
    02-定量统计/
      user-only/*.md            # 用户消息统计
      full/*.md                 # 全量统计（仅 full 模式）
    03-分析材料包/
      *-analysis-packet.md      # 全局 Packet
      *-project-*-packet.md     # 项目 Packet（默认 ≤2）
      *-session-*-packet.md     # 会话 Packet（默认 ≤2）
    04-全局定性报告/user-only/*.md
    05-项目定性报告/user-only/*.md
    06-典型会话报告/user-only/*.md
    _meta/
      manifests/<source>-run.json
      logs/<source>-pipeline.log
```

<details>
<summary>归一化 JSON 数据结构</summary>

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

</details>

---

## 怎么用

### 流水线参数

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

### Skill 组合使用

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

### 样例数据

仓库提供两类样例数据：

**真实分析产物**（`samples/`）—— 一次完整 CatPaw 分析的六阶段产物，所有敏感信息已脱敏（用户名、IP、域名、项目名、业务关键词等均替换为占位符），可安全公开。从这里开始阅读，能快速了解每阶段报告长什么样：

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

**开发测试夹具**（`skills/aci-analysis/assets/fixtures/`）—— 各数据源的最小化样例，用于适配器解析逻辑的单元测试：

| 数据源 | 夹具路径 | 说明 |
|--------|---------|------|
| CatPaw | `fixtures/catpaw/sample-project/` | 单条 transcript 样本 |
| Codex | `fixtures/codex/2026/07/07/` | 单条 rollout JSONL 样本 |
| Claude Code | `fixtures/claude_code/sample-project/` | CLI + SDK 各一条 JSONL |
| WorkBuddy | `fixtures/workbuddy/projects/sample-project/` | 单条 JSONL 样本 |

---

## 原理

### 流水线架构

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

### 项目结构

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

## 治理

### 隐私与安全

- **本地处理**：所有数据仅从本地磁盘读取，产物写入指定 `.aci` 目录。
- **默认脱敏**：默认 `user-only` 模式只提取用户消息文本，不加载 AI 回答正文。
- **不传原始数据**：除非用户明确要求，不会上传原始日志到任何远程服务。
- **可控共享**：可安全共享 `.aci` 中的 reports 和 packets，原始 full transcripts 默认不共享。
- **样例已脱敏**：`samples/` 中的数据已对所有敏感信息（用户名、IP、域名、项目名、业务关键词等）进行脱敏处理，可安全公开。
- **仅限本人数据**：本工具设计初衷是分析用户本人的 AI 编程助手对话日志。分析他人数据前，必须获得数据所有者的明确授权（详见[使用条款与免责声明](#使用条款与免责声明)）。
- **产物含敏感信息**：`.aci` 产物（含 user-only 模式）可能包含对话中的业务逻辑、代码片段、文件路径等敏感内容。共享产物前请确认已脱敏。
- **企业使用须知**：企业环境中批量分析员工对话日志前，应告知被分析者并遵守适用的劳动法与个人信息保护法规。

### 使用条款与免责声明

> **使用本工具即表示您已阅读并同意以下条款。**

#### 1. 使用范围

本工具设计用于分析**您本人**拥有的 AI 编程助手对话日志。您应确保对被分析的数据拥有合法的访问权和处理权。

#### 2. 分析他人数据的授权要求

如果您需要分析非本人产生的对话日志（包括但不限于同事、下属、客户的日志），您**必须**：

1. **事先告知**数据所有者其对话日志将被分析，并说明分析目的、范围和产物用途。
2. **取得明确同意**。口头或书面形式均可，但建议保留授权记录。
3. **遵守适用法律法规**。
4. **仅用于声明的目的**，不得将分析产物用于授权范围以外的用途。

#### 3. 禁止的行为

您**不得**利用本工具：

- 未经授权获取、分析他人的对话日志或个人信息。
- 以窃取、窥探、监控为目的分析他人数据。
- 将分析产物中包含的他人敏感信息（项目结构、业务逻辑、代码片段、文件路径等）向第三方泄露或公开。
- 将分析产物用于不正当竞争、商业间谍或任何违法活动。

#### 4. 企业使用场景

企业在使用本工具分析员工对话日志前，应：

- 制定内部使用政策，明确分析范围、目的和产物访问权限。
- 依据《劳动合同法》和《个人信息保护法》，告知员工并取得同意，或将相关条款纳入劳动合同 / 公司制度。
- 限制分析产物的访问范围，防止未授权人员接触。
- 定期清理 `.aci` 产物，避免不必要的数据留存。

#### 5. 数据跨境传输风险

如果您将 `.aci` 产物（含 user-only JSON 和 packet）交给境外 AI 服务（如 Codex、Claude 等）生成定性报告，可能导致他人个人信息或敏感数据跨境传输。请根据《个人信息保护法》第 38 条和《数据安全法》第 36 条评估合规要求。

#### 6. 免责声明

- 本工具作者不对您使用本工具的行为及其后果承担任何法律责任。
- 本工具不包含数据所有权验证机制，无法防止用户分析他人数据。**遵守法律和获取授权是您的责任，而非工具的责任。**
- 因不当使用本工具（包括但不限于未经授权分析他人数据）导致的任何法律纠纷、损失或处罚，由使用者自行承担全部责任。
- 本工具不对分析产物的准确性、完整性作出保证，产物内容仅供参考。

#### 7. 条款变更

本使用条款可能随项目演进进行更新。继续使用本工具即表示您接受更新后的条款。建议定期查阅本章节获取最新版本。

### 许可证

MIT License

---

## 对贡献者

### 开发与调试

**运行环境**

- Python 3.10+
- 无第三方依赖
- 支持 Windows / macOS / Linux

**项目结构约定**

- 新增数据源适配器：在 `adapters.py` 中添加 `parse_<source>()` 函数，并在 `parse_source()` 中注册。
- 修改报告格式：编辑 `reporting.py`（定量统计）或 `assets/templates/`（定性报告模板）。
- 修改分析维度：编辑 `assets/prompts/` 下的 Prompt 文件。

### 后续计划

**近期**

- **更多数据源适配器**：新增 Cursor、Trae、QoderCode、GitHub Copilot 等 Agent 平台的日志解析支持。
- **跨源合并分析**：支持同时导入多个平台的对话日志，生成跨平台协作画像，回答"我在哪个 Agent 上花的时间最多"等问题。

**中期**

- **HTML 可视化报告**：在 Markdown 报告基础上，额外生成可交互的 HTML 仪表板，支持图表筛选与下钻。
- **自定义分析维度**：允许用户通过自定义 Prompt 模板扩展定性分析维度，无需修改流水线代码。

**远期**

- **Skill Marketplace 分发**：通过 Agent Skill Marketplace 实现一键安装与版本更新。
- **多语言报告输出**：在中文报告基础上增加英文、日文等报告语言选项。

> 欢迎在 [Issues](https://github.com/samihyypia/agent-collab-insight-skills/issues) 中提交功能建议或反馈。
