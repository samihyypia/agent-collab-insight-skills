from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

STAGE_QUANTITATIVE = "02-定量统计"


def write_quantitative_reports(
    source: str,
    sessions: list[dict[str, Any]],
    run_root: Path,
    modes: set[str],
) -> list[Path]:
    report_paths: list[Path] = []
    if "full" in modes:
        full_dir = run_root / STAGE_QUANTITATIVE / "full"
        full_dir.mkdir(parents=True, exist_ok=True)
        report_paths.append(write_full_stats(source, sessions, full_dir))
    if "user-only" in modes:
        user_dir = run_root / STAGE_QUANTITATIVE / "user-only"
        user_dir.mkdir(parents=True, exist_ok=True)
        report_paths.append(write_user_messages(source, sessions, user_dir))
    return report_paths


def write_full_stats(source: str, sessions: list[dict[str, Any]], out_dir: Path) -> Path:
    total_turns = sum(len(s.get("turns", [])) for s in sessions)
    tools = Counter()
    projects = Counter()
    slash = Counter()
    for session in sessions:
        projects[project_label(session)] += 1
        for turn in session.get("turns", []):
            cmd = turn.get("user_message", {}).get("slash_command")
            if cmd:
                slash[cmd] += 1
            for block in turn.get("assistant_message", {}).get("blocks", []):
                if block.get("type") == "tool_use":
                    tools[block.get("name", "unknown")] += 1

    lines = [
        f"# {title_source(source)} 定量统计",
        "",
        "## 全局指标",
        "",
        f"- 会话数：{len(sessions)}",
        f"- 轮次数：{total_turns}",
        f"- 工具调用数：{sum(tools.values())}",
        f"- 项目数：{len(projects)}",
        "",
        "## 项目分布",
        "",
    ]
    lines.extend(table_from_counter(projects, "项目", "会话数"))
    lines.extend(["", "## 工具调用", ""])
    lines.extend(table_from_counter(tools, "工具", "调用次数"))
    lines.extend(["", "## Slash / Skill 命令", ""])
    lines.extend(table_from_counter(slash, "命令", "次数"))
    lines.extend(["", "## 最大会话", ""])
    session_sizes = Counter({s.get("session_id", "unknown"): len(s.get("turns", [])) for s in sessions})
    lines.extend(table_from_counter(session_sizes, "会话", "轮次数", limit=20))

    path = out_dir / f"{source_slug(source)}-quantitative-stats.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_user_messages(source: str, sessions: list[dict[str, Any]], out_dir: Path) -> Path:
    lengths = Counter()
    projects = defaultdict(int)
    lines = [f"# {title_source(source)} 用户消息", "", "## 消息", ""]
    for session in sessions:
        projects[project_label(session)] += 1
        lines.append(f"### {session.get('session_id', 'unknown')}")
        lines.append("")
        lines.append(f"- 项目：`{project_label(session)}`")
        for turn in session.get("turns", []):
            text = turn.get("user_message", {}).get("text", "").strip()
            lengths[bucket(len(text))] += 1
            lines.append(f"- T{turn.get('turn_index')}: {one_line(text, 500)}")
        lines.append("")
    lines.extend(["## 项目分布", ""])
    lines.extend(table_from_counter(Counter(projects), "项目", "会话数"))
    lines.extend(["", "## 长度分布", ""])
    lines.extend(table_from_counter(lengths, "长度", "消息数"))

    path = out_dir / f"{source_slug(source)}-user-messages-full.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def table_from_counter(counter: Counter, left: str, right: str, limit: int = 30) -> list[str]:
    if not counter:
        return ["无数据。"]
    lines = [f"| {left} | {right} |", "|---|---:|"]
    for key, value in counter.most_common(limit):
        lines.append(f"| {key} | {value} |")
    return lines


def bucket(length: int) -> str:
    if length < 50:
        return "<50"
    if length < 200:
        return "50-199"
    if length < 1000:
        return "200-999"
    return "1000+"


def one_line(text: str, limit: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def title_source(source: str) -> str:
    return source.replace("_", " ").title()


def source_slug(source: str) -> str:
    return source.replace("_", "-")


def project_label(session: dict[str, Any]) -> str:
    return str(session.get("project_name") or session.get("project_dir") or "_unknown-project")
