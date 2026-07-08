# Claude Code 单会话深度分析 Prompt

> 将此 Prompt 与单个会话的精简结构化数据一起交给 AI，生成会话级深度分析报告。
> 此 Prompt 同时覆盖 full 模式（含 AI 回答）和 user-only 模式（仅用户输入）。
> 定量统计由代码生成（见 `02-定量统计/`），本 Prompt 只负责定性洞察。

---

**输出语言约束**：最终报告必须使用中文。元数据、代码、路径、命令、字段名和原始引用可以保留原文。

## 输入

你将收到一个会话的精简结构化数据，包含以下字段：

### 会话元信息
- `session_id`, `session_name`(cwd), `project_dir`, `entrypoint`, `model`, `version`, `created_at`
- `ai_title`, `custom_title` — 会话标题

### 轮次数据 `turns[]`
每轮包含：
- `turn_index` — 轮次序号
- `timestamp` — 时间戳
- `user_message.text` — 用户输入（可能含 `<command-message>` 斜杠命令）
- `assistant_summary` — AI 回复摘要（full 模式有值，user-only 模式为 null）
  - `text_preview` — 文本回复前 200 字
  - `tool_calls` — 工具调用列表 `[{"tool": "Edit", "target": "file.vue", "success": true}]`
  - `thinking_preview` — thinking 块前 150 字（如有）
  - `has_error` — 是否有工具执行错误
- `duration_ms` — 轮次耗时
- `token_usage` — Token 用量

### Claude Code 特有元素

| 元素 | 说明 |
|------|------|
| 斜杠命令 | `/speckit-specify`, `/speckit-clarify`, `/speckit-plan`, `/speckit-implement`, `/model`, `/plan` |
| SpecKit 工作流 | specify → clarify → plan → implement 四阶段规格驱动开发 |
| Plan Mode | `/plan` 进入计划模式，AI 先出方案再执行 |
| 模型切换 | `/model` 切换 Opus/Sonnet/Haiku，按任务复杂度分层 |
| Thinking 块 | Claude 的明文推理过程，反映 AI 的思考质量 |
| 上下文续接 | "This session is being continued..." 长会话上下文溢出后的续接 |
| 工具集 | Edit, Read, Bash, PowerShell, Write, Glob, Grep, Agent, Skill, WebFetch, Task* |

---

## 任务

### Full 模式（含 AI 回答）

请对单个会话进行全维度深度分析，按以下结构输出：

#### 1. 会话概览
- 基本统计表（轮数、工具调用数、模型、耗时、Token 用量）
- 斜杠命令清单（命令 + 出现轮次）
- 工具调用统计表（工具名 + 次数 + 成功/失败）
- 会话主题概述（2-3 句话）

#### 2. 阶段流程分析
- 阶段划分表（阶段名 + 起始轮 + 结束轮 + 描述）
- 阶段转换分析（每次转换的触发因素）
- 收敛速度评估（每阶段的收敛情况）

#### 3. 技术决策
- 逐个列出关键技术决策（ADR 风格：轮次、决策内容、理由、影响范围）
- 决策汇总表
- 决策分析（密度、类型分布、依赖链）

#### 4. 交互模式分析
- 用户意图分布表（意图 + 次数 + 典型示例）
- 纠正模式分析（纠正次数、类型、纠正率）
- 工具调用模式（工具使用策略、工具链组合）
- Thinking 分析（AI 推理质量、推理深度）
- Plan Mode / SpecKit 工作流分析（如适用）

#### 5. 问题与解法
- 问题列表表（编号 + 类别 + 严重程度 + 发现轮次 + 描述 + 解决轮次）
- 问题详情（每个问题一个小节）
- 问题模式分析（反复出现的问题、根本原因）

#### 6. 效率指标
- 效率统计表（总轮数、总耗时、工具成功率、调试迭代次数、纠正率、缓存命中率）
- 效率评估星级表（成本/时间/工具/交互/整体，1-5 星）
- 优化建议（3-5 条）

#### 7. 最佳实践
- 从本会话中提取的可复用协作模式（3-5 条，附引用轮次）

#### 8. 反模式
- 识别的低效交互方式（2-4 条，附引用轮次）

---

### User-Only 模式（仅用户输入）

当 `assistant_summary` 为 null 时，切换为 user-only 分析模式：

#### 1. 用户意图轨迹
- 逐轮列出用户意图（轮次 + 原文摘要 + 意图分类）
- 意图演进分析（用户目标如何在会话中变化）

#### 2. 决策风格
- 方案选择模式（快速选择 vs 详细讨论）
- 主动 vs 被动（用户主动提出 vs 回应 AI）

#### 3. 协作模式画像
- 指令风格（极简指令 / 详细描述 / 错误粘贴 / 方案选择）
- 控制粒度（宏观方向 / 微观细节）
- 迭代节奏（快速试错 / 深度规划）

#### 4. 痛点与摩擦
- 从用户消息中识别的挫折感信号
- 反复出现的问题模式
- 效率瓶颈

#### 5. 用户成熟度评估
- 工具熟练度（斜杠命令、模型切换、Plan Mode 的使用）
- 协作策略（是否形成了稳定的工作流）
- 评分（新手 → 熟练 → 专家）

---

## 分析原则

- **基于数据** — 所有结论都要有数据支撑，引用具体轮次编号（如 T3、T7）
- **关注 thinking** — Claude Code 的 thinking 块是明文，分析 AI 的推理质量和深度
- **关注 Token 效率** — 分析缓存命中率、输入/输出比
- **关注 SpecKit/Plan Mode** — 这些是 Claude Code 的特色工作流，重点分析
- **关注上下文续接** — 长会话的 context continuation 是重要特征
- **关注错误链** — Claude Code 会话常出现编译错误链，分析根因
- **客观中立** — 不美化也不苛责，如实反映协作过程
- **可操作性** — 建议要具体，避免空洞表述
- **结构化** — 使用表格、列表，避免大段文字
- **中文输出** — 全部使用中文

## 输出格式

使用 `templates/session-report.md` 模板格式，输出 Markdown 报告。

报告文件名格式：
- Full: `claude-code-session-{session_id前8位}-analysis.md`
- User-only: `claude-code-session-{session_id前8位}-user-insights.md`
