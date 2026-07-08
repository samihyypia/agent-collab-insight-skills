from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_source(source: str, input_path: Path, entrypoint: str = "all") -> list[dict[str, Any]]:
    if source == "catpaw":
        return parse_catpaw(input_path)
    if source == "codex":
        return parse_codex(input_path)
    if source in {"claude_code", "claude_code_sdk"}:
        ep = "sdk-py" if source == "claude_code_sdk" else entrypoint
        return parse_claude_code(input_path, ep)
    if source == "workbuddy":
        return parse_workbuddy(input_path)
    raise ValueError(f"Unsupported source: {source}")


def user_only_session(session: dict[str, Any]) -> dict[str, Any]:
    result = {k: v for k, v in session.items() if k != "turns"}
    result["turns"] = []
    for turn in session.get("turns", []):
        result["turns"].append(
            {
                "turn_index": turn.get("turn_index"),
                "user_message": turn.get("user_message", {}),
            }
        )
    return result


def discover_files(path: Path, pattern: str) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.rglob(pattern))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def safe_id(value: str | None, fallback: str) -> str:
    raw = value or fallback
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", raw).strip("-")
    return cleaned[:80] or fallback


def slash_command(text: str) -> str | None:
    stripped = text.strip()
    if stripped.startswith("/"):
        return stripped.split()[0]
    if stripped.startswith("@skill:"):
        return stripped.split()[0]
    return None


def make_turn(index: int, text: str) -> dict[str, Any]:
    return {
        "turn_index": index,
        "user_message": {"text": text.strip(), "slash_command": slash_command(text)},
        "assistant_message": {"blocks": []},
    }


def add_block(turn: dict[str, Any] | None, block: dict[str, Any]) -> None:
    if turn is not None:
        turn.setdefault("assistant_message", {}).setdefault("blocks", []).append(block)


def parse_catpaw(input_path: Path) -> list[dict[str, Any]]:
    files = discover_files(input_path, "transcript.txt")
    sessions = []
    for file_path in files:
        text = file_path.read_text(encoding="utf-8", errors="replace")
        session_dir = file_path.parent.parent if file_path.parent.name == "agent-transcripts" else file_path.parent
        project_dir = session_dir.parent
        turns: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        in_user = False
        user_lines: list[str] = []
        in_code = False
        last_tool_id = 0

        for line in text.splitlines():
            marker = line.strip()
            if marker.startswith("```"):
                in_code = not in_code
            if in_user:
                if "</user_query>" in line:
                    user_lines.append(line.split("</user_query>", 1)[0])
                    current = make_turn(len(turns) + 1, "\n".join(user_lines))
                    in_user = False
                elif marker not in {"<user_query>", "user:"}:
                    user_lines.append(line)
                continue
            if not in_code and (marker == "user:" or marker.startswith("<user_query>")):
                if current is not None:
                    turns.append(current)
                in_user = True
                user_lines = []
                if "<user_query>" in marker:
                    after = marker.split("<user_query>", 1)[1]
                    if "</user_query>" in after:
                        user_lines.append(after.split("</user_query>", 1)[0])
                        current = make_turn(len(turns) + 1, "\n".join(user_lines))
                        in_user = False
                continue
            if marker.startswith("[Tool call]"):
                last_tool_id += 1
                name = marker.replace("[Tool call]", "", 1).strip() or "unknown"
                add_block(current, {"type": "tool_use", "id": f"tool-{last_tool_id}", "name": name, "input": ""})
            elif marker.startswith("[Tool result]"):
                name = marker.replace("[Tool result]", "", 1).strip() or "unknown"
                add_block(current, {"type": "tool_result", "tool_use_id": f"tool-{last_tool_id}", "name": name, "content": ""})
            elif marker.startswith("assistant:"):
                content = marker.replace("assistant:", "", 1).strip()
                if content:
                    add_block(current, {"type": "text", "text": content})
            elif marker and current is not None and not marker.startswith("[Thinking]"):
                add_block(current, {"type": "text", "text": line})

        if current is not None:
            turns.append(current)
        if not turns and text.strip():
            turns.append(make_turn(1, text.strip()[:4000]))

        created_at = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc).isoformat()
        sessions.append(
            {
                "session_id": safe_id(session_dir.name, file_path.stem),
                "session_name": str(session_dir),
                "source_type": "catpaw",
                "project_name": project_dir.name,
                "project_dir": str(project_dir),
                "created_at": created_at,
                "model": None,
                "turns": turns,
            }
        )
    return sessions


def parse_codex(input_path: Path) -> list[dict[str, Any]]:
    files = discover_files(input_path, "rollout-*.jsonl")
    sessions = []
    for file_path in files:
        turns: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        model = None
        created_at = None
        for obj in read_jsonl(file_path):
            payload = obj.get("payload", obj)
            typ = str(payload.get("type") or obj.get("type") or "").lower()
            model = payload.get("model") or obj.get("model") or model
            created_at = payload.get("created_at") or obj.get("created_at") or created_at
            text = extract_text(payload)
            role = str(payload.get("role") or payload.get("author") or "").lower()
            if "user_message" in typ or role == "user":
                if current is not None:
                    turns.append(current)
                current = make_turn(len(turns) + 1, text)
            elif "function_call_output" in typ or "tool_result" in typ:
                add_block(current, {"type": "tool_result", "name": payload.get("name", "unknown"), "content": text})
            elif "function_call" in typ or "tool_use" in typ:
                add_block(current, {"type": "tool_use", "name": payload.get("name", "unknown"), "input": payload.get("arguments") or text})
            elif text and ("assistant" in typ or role == "assistant" or "message" in typ):
                add_block(current, {"type": "text", "text": text})
        if current is not None:
            turns.append(current)
        if turns:
            sessions.append(base_jsonl_session(file_path, "codex", turns, model, created_at))
    return sessions


def parse_claude_code(input_path: Path, entrypoint: str = "all") -> list[dict[str, Any]]:
    files = discover_files(input_path, "*.jsonl")
    sessions = []
    for file_path in files:
        turns: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        model = None
        created_at = None
        seen_entrypoint = None
        for obj in read_jsonl(file_path):
            if obj.get("isSidechain"):
                continue
            seen_entrypoint = obj.get("entrypoint") or seen_entrypoint
            if entrypoint != "all" and seen_entrypoint and seen_entrypoint != entrypoint:
                continue
            if obj.get("isMeta"):
                continue
            typ = obj.get("type")
            msg = obj.get("message", obj)
            role = msg.get("role") or typ
            model = msg.get("model") or obj.get("model") or model
            created_at = obj.get("timestamp") or msg.get("created_at") or created_at
            content = msg.get("content", obj.get("content"))
            if typ == "user" and isinstance(content, str):
                if current is not None:
                    turns.append(current)
                current = make_turn(len(turns) + 1, content)
            elif typ == "user" and isinstance(content, list):
                for item in content:
                    if item.get("type") == "tool_result":
                        add_block(current, {"type": "tool_result", "name": item.get("name", "unknown"), "content": extract_text(item)})
            elif role == "assistant" or typ == "assistant":
                for block in normalize_content_blocks(content):
                    add_block(current, block)
        if current is not None:
            turns.append(current)
        source_type = "claude_code_sdk" if seen_entrypoint == "sdk-py" else "claude_code"
        if entrypoint == "sdk-py":
            source_type = "claude_code_sdk"
        if turns:
            sessions.append(base_jsonl_session(file_path, source_type, turns, model, created_at, entrypoint=seen_entrypoint))
    return sessions


def parse_workbuddy(input_path: Path) -> list[dict[str, Any]]:
    files = discover_files(input_path, "*.jsonl")
    sessions = []
    for file_path in files:
        turns: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        created_at = None
        for obj in read_jsonl(file_path):
            typ = obj.get("type", "")
            msg = obj.get("message", obj)
            role = msg.get("role") or obj.get("role")
            created_at = obj.get("timestamp") or msg.get("created_at") or created_at
            content = msg.get("content", obj.get("content"))
            if role == "user" or typ == "user":
                text = extract_workbuddy_user_text(content)
                if current is not None:
                    turns.append(current)
                current = make_turn(len(turns) + 1, text)
            elif role == "assistant" or typ in {"assistant", "message"}:
                for block in normalize_content_blocks(content):
                    add_block(current, block)
            elif "function_call" in typ:
                add_block(current, {"type": "tool_use", "name": obj.get("name", "unknown"), "input": extract_text(obj)})
            elif "function_call_result" in typ or "tool_result" in typ:
                add_block(current, {"type": "tool_result", "name": obj.get("name", "unknown"), "content": extract_text(obj)})
        if current is not None:
            turns.append(current)
        if turns:
            sessions.append(base_jsonl_session(file_path, "workbuddy", turns, "auto", created_at))
    return sessions


def base_jsonl_session(
    file_path: Path,
    source_type: str,
    turns: list[dict[str, Any]],
    model: str | None,
    created_at: str | None,
    **extra: Any,
) -> dict[str, Any]:
    project_dir = file_path.parent
    data = {
        "session_id": safe_id(file_path.stem, "session"),
        "session_name": str(file_path),
        "source_type": source_type,
        "project_name": project_dir.name,
        "project_dir": str(project_dir),
        "created_at": created_at,
        "model": model,
        "turns": turns,
    }
    data.update({k: v for k, v in extra.items() if v is not None})
    return data


def extract_text(obj: Any) -> str:
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        parts = [extract_text(item) for item in obj]
        return "\n".join(part for part in parts if part)
    if isinstance(obj, dict):
        for key in ("text", "content", "message", "output", "arguments"):
            if key in obj:
                return extract_text(obj[key])
    return ""


def normalize_content_blocks(content: Any) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    if isinstance(content, str):
        if content.strip():
            blocks.append({"type": "text", "text": content})
        return blocks
    if not isinstance(content, list):
        text = extract_text(content)
        return [{"type": "text", "text": text}] if text else []
    for item in content:
        kind = item.get("type") if isinstance(item, dict) else None
        if kind in {"text", "output_text", "thinking"}:
            blocks.append({"type": "text", "text": extract_text(item)})
        elif kind in {"tool_use", "function_call"}:
            blocks.append({"type": "tool_use", "name": item.get("name", "unknown"), "input": item.get("input") or item.get("arguments") or ""})
        elif kind in {"tool_result", "function_call_result"}:
            blocks.append({"type": "tool_result", "name": item.get("name", "unknown"), "content": extract_text(item)})
    return [b for b in blocks if b.get("text") or b.get("name")]


def extract_workbuddy_user_text(content: Any) -> str:
    text = extract_text(content)
    match = re.search(r"<user_query>(.*?)</user_query>", text, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    text = re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.DOTALL)
    return text.strip()
