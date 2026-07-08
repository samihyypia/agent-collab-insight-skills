# Full 定性分析 Prompt

> 仅当用户明确指定 full 模式时使用。将此 Prompt 与 `.aci/<source>-YYYYMMDDHHmm/01-数据归一化/full/` 下的结构化 JSON，以及 `03-分析材料包/` 中的相关 packet 一起交给 AI，生成中文定性分析报告。

## 输出语言约束

最终报告必须使用中文。元数据、代码、路径、命令、字段名和原始引用可以保留原文。

## 输入

你将收到完整结构化会话数据，可能包含：

- `session_id`, `session_name`, `source_type`, `model`, `created_at`：会话元信息。
- `turns[].user_message.text`：用户输入。
- `turns[].user_message.slash_command`：斜杠命令或 skill 命令。
- `turns[].assistant_message.blocks[]`：AI 回复、工具调用和工具结果。
- `cost_usd`, `duration_ms`：花费和耗时，如源数据提供。

## 任务

对会话进行全维度分析，并优先使用 `assets/templates/session-report.md` 或 packet 指定的目标格式。full 模式可以评价 assistant 行为、工具调用质量、成本、耗时和协作效率，但必须以证据为基础。

### 分析维度

1. **会话概览**：主题、阶段、关键命令和工具调用。
2. **阶段流程**：阶段划分、转换、收敛速度和缺失检查。
3. **技术决策**：决策列表、决策密度、类型分布和依赖链。
4. **交互模式**：用户意图、纠正模式、命令使用和工具调用模式。
5. **问题与解法**：问题列表、严重程度、解决方式和重复模式。
6. **效率指标**：基础指标、工具指标、交互指标和优化建议。
7. **最佳实践**：可复用协作模式 3-5 条。
8. **反模式**：识别低效交互方式 3-5 条。

## 输出格式

按 packet 指定的目标路径写出中文 Markdown 报告。避免大段空泛评价，使用表格、列表和具体轮次证据。
