# ided--Project-langgraph_demo-zhipu 项目 user-only 定性报告

> 会话数：16
> 用户轮次：117
> 数据源：`catpaw`
> 生成时间：2026-07-08 14:12

## 1. 项目概览

该项目围绕<业务智能体>平台建设展开，重点是把前端、Java 后台、FastAPI Agent Runner、Claude Agent SDK、Skills、Platform API、SQLite、OSS 文件链路整合成可运行系统。用户的工作方式明显偏架构驱动：先用 `/speckit-clarify`、`/speckit-plan`、`/speckit-tasks`、`/speckit-analyze` 明确系统边界，再进入阶段实现、联调、人工测试和问题修复。

与 `<project-name>` 的 UI 体验导向不同，本项目的核心难点是“跨服务职责分配 + Agent/Skills 工具契约 + 真实环境联调”。

## 2. 主题分布

| 主题 | 证据 |
|---|---|
| 多 Agent/Skills 能力设计 | `225ae7d5...` T1-T5、`f5f74c35...` T9-T16 |
| <业务功能>测试与分析资产 | `a34a69be...` T1-T6、`1a2afebf...` T1-T5 |
| Claude Agent SDK 接入 | `f5f74c35...` T9-T24 |
| 多服务启动与联调 | `f5f74c35...` T25-T42、`bc129711...` T1-T6 |
| Skills 参数与平台接口修复 | `f5f74c35...` T35-T37 |

## 3. 阶段流程

| 阶段 | 典型轮次 | 用户行为 |
|---|---|---|
| 澄清与选项确认 | `f5f74c35...` T1-T7 | 通过 clarify 快速选择关键方案 |
| 架构规划 | `f5f74c35...` T8-T16 | 明确 Java、FastAPI、SDK、Skills、OSS、SQLite 边界 |
| 任务生成与校正 | `f5f74c35...` T17-T24 | 要求中文任务、TDD、真实环境测试、统一目录路径 |
| 阶段实现 | `f5f74c35...` T25 | 执行 1-3 阶段 |
| 联调验证 | `f5f74c35...` T26-T34 | 启动三端应用，粘贴 curl、500 错误、渲染问题 |
| 工具契约修复 | `f5f74c35...` T35-T42 | 修复 CLI 参数、CORS、文件展示、会话更新时间等问题 |

## 4. 关键决策

| 决策 | 证据 | 影响 |
|---|---|---|
| Java 只做权限和会话记录，业务交给 FastAPI | `f5f74c35...` T9 | 降低 Java 侧复杂度，FastAPI 成为 Agent 主控层 |
| 不使用 LangGraph 和智谱 SDK，改用 ClaudeAgentSDK | `f5f74c35...` T9 | 确定核心 Agent 运行时 |
| 领域能力封装为 Skills，而不是 allowed_tools 或自定义工具函数 | `f5f74c35...` T10、T14 | 统一能力扩展机制 |
| 文件先由前端上传 OSS，再由后端/SDK处理 | `f5f74c35...` T12、T24 | 影响文件问答主链路和 CORS/下载策略 |
| FastAPI 消息存储使用 SQLite | `f5f74c35...` T12 | 支撑历史对话、工具调用记录和失败追踪 |
| 工具调用失败需要记录到 SQLite | `f5f74c35...` T37 | 为后续诊断和历史展示提供数据基础 |

## 5. 交互模式

用户在本项目中更像系统架构负责人。其输入经常包含多个约束点，例如 `f5f74c35...` T12 同时规定 OSS 文件传递、SQLite 存储、文件解析边界、PRD/spec/plan 修改范围。用户会快速识别 AI 对技术机制的误解，例如把 Skills 误写为 `allowed_tools`、把 Claude Agent SDK 误解为 Claude Code CLI、假设 SDK Read 可直接读取 OSS URL。

联调阶段，用户输入大量真实错误现场，包括 curl、HTTP 500、CORS、CLI usage error、无权限数据返回、系统事件未渲染等。这说明用户希望 AI 不只写代码，也要进入“真实系统运行闭环”。

## 6. 反复问题

1. Skills 与工具参数契约不稳定：`--pageSize`、`--includeRelations` 等参数和脚本实际接口不一致。
2. 多服务职责容易漂移：Java、FastAPI、SDK、Skills、Platform API 的边界需要用户反复校正。
3. 文件处理链路复杂：OSS URL、CORS、预签名、文件名展示、下载或详情查看都影响用户体验。
4. 历史消息和工具调用展示不完整：用户明确指出“历史对话中，工具调用的历史看不到了”（`f5f74c35...` T33）。

## 7. 项目建议

1. 为每个 Skill 建立 `contract.md`，列出命令、参数、示例、错误码、平台 API 映射，避免调用参数漂移。
2. 将 Java/FastAPI/SDK/Skills/SQLite/OSS 画成职责矩阵，并在 spec、plan、tasks 中引用同一份矩阵。
3. 为真实环境联调建立固定测试脚本，覆盖消息发送、历史读取、工具调用失败、文件上传、OSS 访问、会话重命名。
4. 在 SQLite 中统一记录消息事件、工具调用事件、错误事件和用户可见状态，避免历史对话丢失过程信息。

