from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.database import initialize_database


DEFAULT_WORKSPACE_PATH = Path(__file__).resolve().parents[3] / "ProjectWorkspace"
WORKSPACE_ENV_VAR = "PROJECT_WORKSPACE_PATH"
PROJECT_SUBDIRECTORIES = [
    "任务分配与完成情况",
    "节点提醒",
    "论文-专利",
    "项目例会",
    "项目测试",
    "设备-IP-流片",
    "财务情况更新",
    "人员信息",
    "项目文档",
    "知识库",
]
CONFLICT_PATTERNS = [
    "conflict",
    "conflicted",
    "冲突",
    "副本",
]


class WorkspaceError(RuntimeError):
    pass


def normalize_workspace_path(workspace_path: Optional[Path] = None) -> Path:
    configured_path = os.getenv(WORKSPACE_ENV_VAR)
    path = workspace_path or (Path(configured_path) if configured_path else DEFAULT_WORKSPACE_PATH)
    return path.expanduser().resolve()


def initialize_workspace(workspace_path: Optional[Path] = None) -> dict:
    path = normalize_workspace_path(workspace_path)
    projects_path = path / "projects"
    backups_path = path / "backups"
    attachments_path = path / "attachments"
    database_path = path / "app.sqlite"

    try:
        path.mkdir(parents=True, exist_ok=True)
        projects_path.mkdir(exist_ok=True)
        backups_path.mkdir(exist_ok=True)
        attachments_path.mkdir(exist_ok=True)
        initialize_database(database_path)
    except OSError as exc:
        raise WorkspaceError(f"初始化工作区失败: {exc}") from exc

    return get_workspace_status(path)


def get_workspace_status(workspace_path: Optional[Path] = None) -> dict:
    path = normalize_workspace_path(workspace_path)
    database_path = path / "app.sqlite"
    projects_path = path / "projects"
    backups_path = path / "backups"

    latest_backup = _get_latest_backup(backups_path)

    return {
        "workspace_path": str(path),
        "database_path": str(database_path),
        "projects_path": str(projects_path),
        "initialized": database_path.exists() and projects_path.exists(),
        "conflict_files": find_conflict_files(path),
        "last_backup_at": _format_timestamp(latest_backup.stat().st_mtime) if latest_backup else None,
    }


def create_backup(workspace_path: Optional[Path] = None) -> dict:
    path = normalize_workspace_path(workspace_path)
    database_path = path / "app.sqlite"
    backups_path = path / "backups"

    if not database_path.exists():
        raise WorkspaceError("数据库不存在，请先初始化工作区")

    backups_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    backup_path = backups_path / f"app-{timestamp}.sqlite"

    try:
        shutil.copy2(database_path, backup_path)
    except OSError as exc:
        raise WorkspaceError(f"创建备份失败: {exc}") from exc

    return {"backup_path": str(backup_path.relative_to(path))}


def find_conflict_files(workspace_path: Path) -> list[str]:
    path = normalize_workspace_path(workspace_path)
    if not path.exists():
        return []

    conflict_files: list[str] = []
    for item in path.rglob("*"):
        if not item.is_file():
            continue
        name = item.name.lower()
        if any(pattern in name for pattern in CONFLICT_PATTERNS):
            conflict_files.append(str(item.relative_to(path)))

    return sorted(conflict_files)


def _get_latest_backup(backups_path: Path) -> Optional[Path]:
    if not backups_path.exists():
        return None

    backups = sorted(backups_path.glob("app-*.sqlite"), key=lambda item: item.stat().st_mtime)
    return backups[-1] if backups else None


def _format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).astimezone().isoformat(timespec="seconds")
