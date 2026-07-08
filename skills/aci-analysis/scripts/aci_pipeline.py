from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

from aci_skillkit.adapters import parse_source, user_only_session
from aci_skillkit.packets import write_packet
from aci_skillkit.reporting import write_quantitative_reports

STAGE_STRUCTURED = "01-数据归一化"
META_DIR = "_meta"
UNKNOWN_PROJECT = "_unknown-project"


def main() -> int:
    parser = argparse.ArgumentParser(description="Portable ACI transcript analysis pipeline.")
    parser.add_argument("--source", required=True, choices=["catpaw", "codex", "claude_code", "claude_code_sdk", "workbuddy"])
    parser.add_argument("--input", required=True, help="Raw source path.")
    parser.add_argument("--output", default=".aci", help="Output root. Defaults to ./.aci")
    parser.add_argument("--stages", default="ingest,quantitative,packet", help="Comma-separated stages.")
    parser.add_argument("--mode", default="user-only", help="Comma-separated output modes. Defaults to user-only; pass full,user-only to include full outputs.")
    parser.add_argument("--entrypoint", default="cli", choices=["cli", "sdk-py", "all"], help="Claude Code entrypoint filter. Defaults to cli; SDK is opt-in.")
    parser.add_argument("--project-count", type=int, default=2, help="Project packet/report count. Defaults to 2; pass a larger value only when explicitly requested.")
    parser.add_argument("--typical-count", type=int, default=2, help="Typical session packet/report count. Defaults to 2; pass a larger value only when explicitly requested.")
    parser.add_argument("--typical-session-id", action="append", default=[], help="Explicit typical session id to include. Can be repeated.")
    parser.add_argument("--run-id", help="Fixed run folder name for reproducible output, such as codex-202607071530.")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    input_path = Path(args.input).expanduser().resolve()
    output_root = Path(args.output).expanduser().resolve()
    stages = {s.strip() for s in args.stages.split(",") if s.strip()}
    modes = {m.strip() for m in args.mode.split(",") if m.strip()}
    output_root.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        "source": args.source,
        "input": str(input_path),
        "output_root": str(output_root),
        "stages": sorted(stages),
        "modes": sorted(modes),
        "runs": {},
        "errors": [],
    }

    try:
        loaded_run_root: Path | None = None
        if "ingest" in stages:
            sessions = parse_source(args.source, input_path, args.entrypoint)
        else:
            sessions, loaded_run_root = load_structured(args.source, output_root, args.run_id)

        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        source_groups = group_by_output_source(args.source, sessions)
        multi_source = len(source_groups) > 1

        for output_source, source_sessions in source_groups.items():
            run_id = build_run_id(output_source, args.run_id, timestamp, multi_source)
            if loaded_run_root and loaded_run_root.name == run_id:
                run_root = loaded_run_root
            elif "ingest" in stages:
                run_root = allocate_run_root(output_root, run_id)
                run_id = run_root.name
            else:
                run_root = loaded_run_root or allocate_run_root(output_root, run_id)
                run_id = run_root.name

            manifest = build_run_manifest(args, input_path, output_root, run_root, output_source, stages, modes)
            log_path = run_root / META_DIR / "logs" / f"{output_source}-pipeline.log"
            log_path.parent.mkdir(parents=True, exist_ok=True)

            project_groups, project_key_map = group_by_project(source_sessions)
            selected_projects = select_project_keys(project_groups, args.project_count)
            manifest["sessions"] = len(source_sessions)
            manifest["turns"] = sum(len(s.get("turns", [])) for s in source_sessions)
            manifest["project_key_map"] = project_key_map
            manifest["projects"] = build_project_manifest(project_groups)
            manifest["selected_projects"] = selected_projects

            if "ingest" in stages:
                written = write_structured(output_source, source_sessions, run_root, modes)
                manifest["structured"] = [str(path) for path in written]

            if "quantitative" in stages:
                reports = write_quantitative_reports(output_source, source_sessions, run_root, modes)
                manifest["reports"] = [str(path) for path in reports]

            if "packet" in stages:
                packets = write_packet(
                    output_source,
                    source_sessions,
                    run_root,
                    skill_root,
                    modes,
                    project_groups=project_groups,
                    project_key_map=project_key_map,
                    project_count=args.project_count,
                    typical_count=args.typical_count,
                    typical_session_ids=args.typical_session_id,
                )
                manifest["packet"] = str(packets[0]) if packets else None
                manifest["packets"] = [str(path) for path in packets]

            log_path.write_text("ACI pipeline completed.\n", encoding="utf-8")
            write_manifest(output_source, manifest, run_root)
            summary["runs"][output_source] = {
                "run_id": run_id,
                "run_root": str(run_root),
                "sessions": manifest["sessions"],
                "turns": manifest["turns"],
                "projects": manifest["projects"],
                "selected_projects": selected_projects,
            }

    except Exception as exc:
        summary["errors"].append(str(exc))
        fallback_log = output_root / META_DIR / "logs" / f"{args.source}-pipeline.log"
        fallback_log.parent.mkdir(parents=True, exist_ok=True)
        fallback_log.write_text(traceback.format_exc(), encoding="utf-8")
        print(f"ACI pipeline failed: {exc}", file=sys.stderr)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def build_run_manifest(
    args: argparse.Namespace,
    input_path: Path,
    output_root: Path,
    run_root: Path,
    source: str,
    stages: set[str],
    modes: set[str],
) -> dict[str, Any]:
    return {
        "source": source,
        "requested_source": args.source,
        "run_id": run_root.name,
        "run_started_at": datetime.now().isoformat(timespec="seconds"),
        "input": str(input_path),
        "output_root": str(output_root),
        "run_root": str(run_root),
        "stages": sorted(stages),
        "modes": sorted(modes),
        "project_count": args.project_count,
        "typical_count": args.typical_count,
        "sessions": 0,
        "turns": 0,
        "project_key_map": {},
        "projects": {},
        "selected_projects": [],
        "structured": [],
        "reports": [],
        "packets": [],
        "errors": [],
    }


def build_run_id(source: str, requested_run_id: str | None, timestamp: str, multi_source: bool) -> str:
    if not requested_run_id:
        return f"{source}-{timestamp}"
    if requested_run_id.startswith(f"{source}-") or not multi_source:
        return safe_path_part(requested_run_id, f"{source}-{timestamp}")
    return safe_path_part(f"{source}-{requested_run_id}", f"{source}-{timestamp}")


def allocate_run_root(output_root: Path, run_id: str) -> Path:
    base = safe_path_part(run_id, "aci-run")
    candidate = output_root / base
    if not candidate.exists():
        candidate.mkdir(parents=True, exist_ok=True)
        return candidate
    for index in range(2, 1000):
        candidate = output_root / f"{base}-{index:02d}"
        if not candidate.exists():
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
    raise FileExistsError(f"Unable to allocate run directory for {run_id}")


def write_structured(source: str, sessions: list[dict[str, Any]], run_root: Path, modes: set[str]) -> list[Path]:
    paths: list[Path] = []
    if "full" in modes:
        full_dir = run_root / STAGE_STRUCTURED / "full"
        full_dir.mkdir(parents=True, exist_ok=True)
        for session in sessions:
            path = full_dir / f"{safe_path_part(str(session['session_id']), 'session')}.json"
            path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
            paths.append(path)
    if "user-only" in modes:
        user_dir = run_root / STAGE_STRUCTURED / "user-only"
        user_dir.mkdir(parents=True, exist_ok=True)
        for session in sessions:
            user_session = user_only_session(session)
            path = user_dir / f"{safe_path_part(str(session['session_id']), 'session')}.json"
            path.write_text(json.dumps(user_session, ensure_ascii=False, indent=2), encoding="utf-8")
            paths.append(path)
    return paths


def group_by_output_source(requested_source: str, sessions: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for session in sessions:
        output_source = session.get("source_type") or requested_source
        groups.setdefault(output_source, []).append(session)
    return groups


def group_by_project(sessions: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, str]]:
    identities: list[str] = []
    for session in sessions:
        identity = project_identity(session)
        if identity not in identities:
            identities.append(identity)

    used: dict[str, str] = {}
    key_map: dict[str, str] = {}
    for identity in identities:
        base = safe_path_part(identity, UNKNOWN_PROJECT)
        key = base
        if key in used and used[key] != identity:
            digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:8]
            key = f"{base}-{digest}"
        used[key] = identity
        key_map[identity] = key

    projects: dict[str, list[dict[str, Any]]] = {}
    for session in sessions:
        key = key_map[project_identity(session)]
        projects.setdefault(key, []).append(session)
    return projects, key_map


def project_identity(session: dict[str, Any]) -> str:
    name = str(session.get("project_name") or "").strip()
    if name:
        return name
    project_dir = str(session.get("project_dir") or "").strip()
    if project_dir:
        path_name = Path(project_dir).name
        if path_name:
            return path_name
    return UNKNOWN_PROJECT


def build_project_manifest(project_groups: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, int]]:
    return {
        project_key: {
            "sessions": len(project_sessions),
            "turns": sum(len(s.get("turns", [])) for s in project_sessions),
        }
        for project_key, project_sessions in project_groups.items()
    }


def select_project_keys(project_groups: dict[str, list[dict[str, Any]]], project_count: int) -> list[str]:
    limit = max(0, project_count)
    weighted = sorted(
        project_groups.items(),
        key=lambda item: (
            len(item[1]),
            sum(len(s.get("turns", [])) for s in item[1]),
            item[0],
        ),
        reverse=True,
    )
    return [project_key for project_key, _ in weighted[:limit]]


def load_structured(source: str, output_root: Path, run_id: str | None = None) -> tuple[list[dict[str, Any]], Path | None]:
    candidates: list[Path] = []
    if run_id:
        candidates.append(output_root / run_id)
    candidates.extend(sorted(output_root.glob(f"{source}-*"), reverse=True))
    candidates.append(output_root / source)

    for run_root in candidates:
        if not run_root.exists():
            continue
        sessions = read_new_structured(run_root)
        if sessions:
            return sessions, run_root

    legacy_sessions = read_legacy_structured(source, output_root)
    if legacy_sessions:
        return legacy_sessions, None
    raise FileNotFoundError(f"No structured data for source {source} under {output_root}")


def read_new_structured(run_root: Path) -> list[dict[str, Any]]:
    stage_root = run_root / STAGE_STRUCTURED
    if not stage_root.exists():
        return []
    for mode in ("full", "user-only"):
        files = sorted(stage_root.glob(f"{mode}/*.json"))
        if files:
            return [json.loads(path.read_text(encoding="utf-8")) for path in files]
        project_files = sorted(stage_root.glob(f"*/{mode}/*.json"))
        if project_files:
            return [json.loads(path.read_text(encoding="utf-8")) for path in project_files]
    return []


def read_legacy_structured(source: str, output_root: Path) -> list[dict[str, Any]]:
    for mode in ("full", "user-only"):
        old_stage_dir = output_root / source / STAGE_STRUCTURED / mode
        if old_stage_dir.exists():
            files = sorted(old_stage_dir.glob("*.json"))
            if files:
                return [json.loads(path.read_text(encoding="utf-8")) for path in files]
        legacy_dir = output_root / "structured" / source / mode
        if legacy_dir.exists():
            files = sorted(legacy_dir.glob("*.json"))
            if files:
                return [json.loads(path.read_text(encoding="utf-8")) for path in files]
    return []


def write_manifest(source: str, manifest: dict[str, Any], run_root: Path) -> None:
    manifest_dir = run_root / META_DIR / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    (manifest_dir / f"{source}-run.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_path_part(value: str, fallback: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1F]+', "-", value)
    cleaned = re.sub(r"\s+", "-", cleaned).strip(" .-")
    return cleaned[:96] or fallback


if __name__ == "__main__":
    raise SystemExit(main())
