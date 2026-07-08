# Catpaw 分析 Packet

这个 packet 是后续中文定性报告的输入材料，不是最终报告。

- 默认分析模式：`user-only`
- 输出语言约束：面向用户阅读的报告和 packet 正文必须使用中文；路径、命令、字段名和原始对话文本保持原样。
- CLI 已生成前 3 阶段；Codex 需要继续完成第 4、5、6 阶段。

## 资源

- User-only prompt：`C:\Users\<user>\.codex\skills\aci-analysis\assets\prompts\user-only-analysis.md`
- 会话深度 prompt：`C:\Users\<user>\.codex\skills\aci-analysis\assets\prompts\session-deep-analysis.md`
- 项目报告模板：`C:\Users\<user>\.codex\skills\aci-analysis\assets\templates\project-report.md`
- 会话报告模板：`C:\Users\<user>\.codex\skills\aci-analysis\assets\templates\session-report.md`

## 已生成输入

- User-only 数据：`<workspace>\pm_explore\.aci\catpaw-202607081412\01-数据归一化\user-only`
- User-only 定量报告：`<workspace>\pm_explore\.aci\catpaw-202607081412\02-定量统计\user-only\catpaw-user-messages-full.md`

## 阶段输出位置

- 全局定性报告：`<workspace>\pm_explore\.aci\catpaw-202607081412\04-全局定性报告\user-only\catpaw-global-user-insights.md`
- 项目定性报告目录：`<workspace>\pm_explore\.aci\catpaw-202607081412\05-项目定性报告\user-only`
- 典型会话报告目录：`<workspace>\pm_explore\.aci\catpaw-202607081412\06-典型会话报告\user-only`

## 摘要

- 会话数：50
- 轮次数：365
- 项目数：9
- 工具调用数：7309

## 默认选择规则

- 默认项目定性报告数量不超过 2 个，除非用户明确指定更多。
- 默认典型会话报告数量不超过 2 个，除非用户明确指定更多或传入具体会话 ID。
- 本次选择项目：ided--Project-<org>-<project-name>, ided--Project-<org>-langgraph_demo-zhipu2
- 本次选择典型会话：da042cb1-5b89-4ee7-9778-23eec3b6c2f8, f5f74c35-96c1-4c4a-a134-d0a94cd13f2b

## 项目映射

| 原始项目 | project-key | 会话数 | 轮次数 |
|---|---|---:|---:|
| ided--Project-OpenSourceFramwork-cc-src_2026-03-31(1) | `ided--Project-OpenSourceFramwork-cc-src_2026-03-31(1)` | 1 | 1 |
| ided--Project-sami-AgentCollabInsight | `ided--Project-sami-AgentCollabInsight` | 6 | 50 |
| ided--Project-sami-airia-product-design-tools-repo | `ided--Project-sami-airia-product-design-tools-repo` | 1 | 1 |
| ided--Project-<org>-content_system_explore | `ided--Project-<org>-content_system_explore` | 1 | 2 |
| ided--Project-<org>-<platform-name> | `ided--Project-<org>-<platform-name>` | 2 | 3 |
| ided--Project-<org>-<project-name> | `ided--Project-<org>-<project-name>` | 16 | 181 |
| ided--Project-<org>-langgraph_demo | `ided--Project-<org>-langgraph_demo` | 6 | 9 |
| ided--Project-<org>-langgraph_demo-zhipu2 | `ided--Project-<org>-langgraph_demo-zhipu2` | 16 | 117 |
| ided--Project-<org>-langgraph_demo-zhipu3 | `ided--Project-<org>-langgraph_demo-zhipu3` | 1 | 1 |

## 高频命令

- `/speckit-implement`: 10
- `/speckit-specify`: 7
- `/speckit-analyze`: 6
- `/speckit-clarify`: 5
- `/speckit-plan`: 5
- `/speckit-tasks`: 4
- `/speckit-constitution`: 3
- `/agent-test-evaluation`: 2
- `/aci-analysis`: 1
- `/create-skill`: 1

## 继续生成要求

1. 先读取本 packet、user-only prompt 和定量报告，写入全局定性报告。
2. 再读取选中的项目 packet，默认写入最多 2 份项目定性报告。
3. 最后读取选中的典型会话 packet，默认写入最多 2 份典型会话报告。
