from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .reporting import one_line, source_slug, title_source

STAGE_STRUCTURED = "01-数据归一化"
STAGE_QUANTITATIVE = "02-定量统计"
STAGE_PACKET = "03-分析材料包"
STAGE_GLOBAL_REPORT = "04-全局定性报告"
STAGE_PROJECT_REPORT = "05-项目定性报告"
STAGE_SESSION_REPORT = "06-典型会话报告"


def write_packet(
    source: str,
    sessions: list[dict[str, Any]],
    run_root: Path,
    skill_root: Path,
    modes: set[str],
    project_groups: dict[str, list[dict[str, Any]]],
    project_key_map: dict[str, str],
    project_count: int = 2,
    typical_count: int = 2,
    typical_session_ids: list[str] | None = None,
) -> list[Path]:
    packet_dir = run_root / STAGE_PACKET
    packet_dir.mkdir(parents=True, exist_ok=True)
    prompt_dir = skill_root / "assets" / "prompts"
    template_dir = skill_root / "assets" / "templates"
    selected_projects = select_project_keys(project_groups, project_count)
    selected_sessions = select_typical_sessions(sessions, typical_count, typical_session_ids)

    main_packet = packet_dir / f"{source_slug(source)}-analysis-packet.md"
    main_packet.write_text(
        "\n".join(
            build_global_packet_lines(
                source,
                sessions,
                run_root,
                prompt_dir,
                template_dir,
                modes,
                project_groups,
                project_key_map,
                selected_projects,
                selected_sessions,
            )
        )
        + "\n",
        encoding="utf-8",
    )

    project_packets = [
        write_project_packet(source, project_key, project_groups[project_key], run_root, packet_dir, prompt_dir, template_dir, modes)
        for project_key in selected_projects
        if project_key in project_groups
    ]
    session_packets = [
        write_session_packet(source, session, run_root, packet_dir, prompt_dir, template_dir, modes)
        for session in selected_sessions
    ]
    return [main_packet, *project_packets, *session_packets]


def build_global_packet_lines(
    source: str,
    sessions: list[dict[str, Any]],
    run_root: Path,
    prompt_dir: Path,
    template_dir: Path,
    modes: set[str],
    project_groups: dict[str, list[dict[str, Any]]],
    project_key_map: dict[str, str],
    selected_projects: list[str],
    selected_sessions: list[dict[str, Any]],
) -> list[str]:
    include_full = "full" in modes
    lines = [
        f"# {title_source(source)} 分析 Packet",
        "",
        "这个 packet 是后续中文定性报告的输入材料，不是最终报告。",
        "",
        f"- 默认分析模式：`{'full + user-only' if include_full else 'user-only'}`",
        "- 输出语言约束：面向用户阅读的报告和 packet 正文必须使用中文；路径、命令、字段名和原始对话文本保持原样。",
        "- CLI 已生成前 3 阶段；Codex 需要继续完成第 4、5、6 阶段。",
        "",
        "## 资源",
        "",
        f"- User-only prompt：`{prompt_dir / 'user-only-analysis.md'}`",
        f"- 会话深度 prompt：`{prompt_dir / 'session-deep-analysis.md'}`",
        f"- 项目报告模板：`{template_dir / 'project-report.md'}`",
        f"- 会话报告模板：`{template_dir / 'session-report.md'}`",
        "",
        "## 已生成输入",
        "",
        f"- User-only 数据：`{run_root / STAGE_STRUCTURED / 'user-only'}`",
        f"- User-only 定量报告：`{run_root / STAGE_QUANTITATIVE / 'user-only' / (source_slug(source) + '-user-messages-full.md')}`",
        "",
        "## 阶段输出位置",
        "",
        f"- 全局定性报告：`{run_root / STAGE_GLOBAL_REPORT / 'user-only' / (source_slug(source) + '-global-user-insights.md')}`",
        f"- 项目定性报告目录：`{run_root / STAGE_PROJECT_REPORT / 'user-only'}`",
        f"- 典型会话报告目录：`{run_root / STAGE_SESSION_REPORT / 'user-only'}`",
        "",
        "## 摘要",
        "",
        f"- 会话数：{len(sessions)}",
        f"- 轮次数：{sum(len(s.get('turns', [])) for s in sessions)}",
        f"- 项目数：{len(project_groups)}",
        f"- 工具调用数：{tool_call_count(sessions)}",
        "",
        "## 默认选择规则",
        "",
        "- 默认项目定性报告数量不超过 2 个，除非用户明确指定更多。",
        "- 默认典型会话报告数量不超过 2 个，除非用户明确指定更多或传入具体会话 ID。",
        f"- 本次选择项目：{', '.join(selected_projects) if selected_projects else '无'}",
        f"- 本次选择典型会话：{', '.join(str(s.get('session_id', 'unknown')) for s in selected_sessions) if selected_sessions else '无'}",
        "",
        "## 项目映射",
        "",
        "| 原始项目 | project-key | 会话数 | 轮次数 |",
        "|---|---|---:|---:|",
    ]
    reverse_map = {key: identity for identity, key in project_key_map.items()}
    for project_key, project_sessions in sorted(project_groups.items()):
        identity = reverse_map.get(project_key, project_key)
        lines.append(
            f"| {identity} | `{project_key}` | {len(project_sessions)} | {sum(len(s.get('turns', [])) for s in project_sessions)} |"
        )

    lines.extend(["", "## 高频命令", ""])
    commands = command_counter(sessions)
    if commands:
        for command, count in commands.most_common(20):
            lines.append(f"- `{command}`: {count}")
    else:
        lines.append("- 未检测到 slash 或 skill 命令。")

    lines.extend(["", "## 继续生成要求", ""])
    lines.extend(
        [
            "1. 先读取本 packet、user-only prompt 和定量报告，写入全局定性报告。",
            "2. 再读取选中的项目 packet，默认写入最多 2 份项目定性报告。",
            "3. 最后读取选中的典型会话 packet，默认写入最多 2 份典型会话报告。",
        ]
    )
    if include_full:
        lines.extend(
            [
                "",
                "用户已显式请求 full 模式；如需要，可把 full 报告写入对应 `full/` 目录。",
            ]
        )
    return lines


def select_project_keys(project_groups: dict[str, list[dict[str, Any]]], project_count: int) -> list[str]:
    weighted = sorted(
        project_groups.items(),
        key=lambda item: (
            len(item[1]),
            sum(len(s.get("turns", [])) for s in item[1]),
            item[0],
        ),
        reverse=True,
    )
    return [project_key for project_key, _ in weighted[: max(0, project_count)]]


def select_typical_sessions(
    sessions: list[dict[str, Any]],
    typical_count: int = 2,
    typical_session_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    if typical_session_ids:
        by_id = {str(session.get("session_id")): session for session in sessions}
        return [by_id[session_id] for session_id in typical_session_ids if session_id in by_id]
    return sorted(sessions, key=session_weight, reverse=True)[: max(0, typical_count)]


def session_weight(session: dict[str, Any]) -> tuple[int, int, str]:
    turns = session.get("turns", [])
    user_chars = sum(len(turn.get("user_message", {}).get("text", "")) for turn in turns)
    return (len(turns), user_chars, str(session.get("session_id", "")))


def write_project_packet(
    source: str,
    project_key: str,
    sessions: list[dict[str, Any]],
    run_root: Path,
    packet_dir: Path,
    prompt_dir: Path,
    template_dir: Path,
    modes: set[str],
) -> Path:
    path = packet_dir / f"{source_slug(source)}-project-{safe_filename(project_key)}-packet.md"
    lines = [
        f"# {title_source(source)} 项目 Packet",
        "",
        "这个 packet 用于生成单个项目的中文定性报告。",
        "",
        "- 输出语言约束：面向用户阅读的报告正文必须使用中文。",
        f"- 项目：`{project_key}`",
        f"- 会话数：{len(sessions)}",
        f"- 轮次数：{sum(len(s.get('turns', [])) for s in sessions)}",
        "",
        "## 资源",
        "",
        f"- User-only prompt：`{prompt_dir / 'user-only-analysis.md'}`",
        f"- 项目报告模板：`{template_dir / 'project-report.md'}`",
        f"- User-only 数据目录：`{run_root / STAGE_STRUCTURED / 'user-only'}`",
        "",
        "## 输出位置",
        "",
        f"- `{run_root / STAGE_PROJECT_REPORT / 'user-only' / (source_slug(source) + '-project-' + safe_filename(project_key) + '-user-insights.md')}`",
        "",
        "## 示例轮次",
        "",
    ]
    for session in sorted(sessions, key=session_weight, reverse=True)[:5]:
        lines.append(f"### {session.get('session_id', 'unknown')}")
        for turn in session.get("turns", [])[:5]:
            text = turn.get("user_message", {}).get("text", "")
            lines.append(f"- T{turn.get('turn_index')}: {one_line(text, 300)}")
        lines.append("")
    if "full" in modes:
        lines.extend(
            [
                "## Full 模式",
                "",
                f"- 用户已显式请求 full；可选输出：`{run_root / STAGE_PROJECT_REPORT / 'full' / (source_slug(source) + '-project-' + safe_filename(project_key) + '-full-insights.md')}`",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_session_packet(
    source: str,
    session: dict[str, Any],
    run_root: Path,
    packet_dir: Path,
    prompt_dir: Path,
    template_dir: Path,
    modes: set[str],
) -> Path:
    session_id = str(session.get("session_id", "unknown"))
    safe_id = safe_filename(session_id)
    path = packet_dir / f"{source_slug(source)}-session-{safe_id}-packet.md"
    turns = session.get("turns", [])
    project_name = str(session.get("project_name") or session.get("project_dir") or "_unknown-project")
    lines = [
        f"# {title_source(source)} 典型会话 Packet",
        "",
        "这个 packet 用于生成单个典型会话的中文定性报告。",
        "",
        "- 输出语言约束：面向用户阅读的报告正文必须使用中文。",
        f"- 项目：`{project_name}`",
        f"- 会话 ID：`{session_id}`",
        f"- 轮次数：{len(turns)}",
        f"- 工具调用数：{tool_call_count([session])}",
        "",
        "## 资源",
        "",
        f"- 会话深度 prompt：`{prompt_dir / 'session-deep-analysis.md'}`",
        f"- 会话报告模板：`{template_dir / 'session-report.md'}`",
        f"- User-only 结构化数据：`{run_root / STAGE_STRUCTURED / 'user-only' / (safe_id + '.json')}`",
        "",
        "## 输出位置",
        "",
        f"- `{run_root / STAGE_SESSION_REPORT / 'user-only' / (source_slug(source) + '-session-' + safe_id + '-user-insights.md')}`",
        "",
        "## 命令摘要",
        "",
    ]
    commands = command_counter([session])
    if commands:
        for command, count in commands.most_common(20):
            lines.append(f"- `{command}`: {count}")
    else:
        lines.append("- 未检测到 slash 或 skill 命令。")

    lines.extend(["", "## 用户轮次", ""])
    for turn in turns[:50]:
        text = turn.get("user_message", {}).get("text", "")
        lines.append(f"- T{turn.get('turn_index')}: {one_line(text, 500)}")
    if len(turns) > 50:
        lines.append(f"- ... packet 预览中省略了另外 {len(turns) - 50} 个轮次。")

    if "full" in modes:
        lines.extend(
            [
                "",
                "## Full 模式",
                "",
                f"- 用户已显式请求 full；可选输出：`{run_root / STAGE_SESSION_REPORT / 'full' / (source_slug(source) + '-session-' + safe_id + '-full-insights.md')}`",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def command_counter(sessions: list[dict[str, Any]]) -> Counter:
    return Counter(
        turn.get("user_message", {}).get("slash_command")
        for session in sessions
        for turn in session.get("turns", [])
        if turn.get("user_message", {}).get("slash_command")
    )


def safe_filename(value: str) -> str:
    return "".join(char if char.isalnum() or char in "-_." else "-" for char in value)[:120] or "unknown"


def tool_call_count(sessions: list[dict[str, Any]]) -> int:
    return sum(
        1
        for session in sessions
        for turn in session.get("turns", [])
        for block in turn.get("assistant_message", {}).get("blocks", [])
        if block.get("type") == "tool_use"
    )
