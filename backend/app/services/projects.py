from __future__ import annotations

import csv
import io
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Optional

from app.database import connect, initialize_database, rows_to_dicts
from app.services.auth import current_username, get_current_user, is_admin
from app.services.workspace import PROJECT_SUBDIRECTORIES, WorkspaceError, normalize_workspace_path


class ProjectError(RuntimeError):
    pass


def list_projects(workspace_path: Optional[Path] = None, q: Optional[str] = None, status: Optional[str] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    filters = ["deleted_at IS NULL"]
    params: list[str] = []
    user = get_current_user()
    if not user:
        raise ProjectError("请先登录")

    if q:
        filters.append("name LIKE ?")
        params.append(f"%{q}%")
    if status:
        filters.append("status = ?")
        params.append(status)
    if not is_admin(user):
        filters.append(
            """
            (
                created_by = ?
                OR EXISTS (
                    SELECT 1
                    FROM project_access
                    WHERE project_access.project_id = projects.id
                      AND project_access.username = ?
                )
            )
            """
        )
        params.extend([user["username"], user["username"]])

    where_clause = " AND ".join(filters)
    with connect(database_path) as connection:
        items = rows_to_dicts(
            connection.execute(
                f"""
                SELECT *
                FROM projects
                WHERE {where_clause}
                ORDER BY updated_at DESC, id DESC
                """,
                params,
            )
        )

    return {"items": items, "total": len(items)}


def get_project(project_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM projects WHERE id = ? AND deleted_at IS NULL",
            (project_id,),
        ).fetchone()

    if not row:
        raise ProjectError("项目不存在")
    project = dict(row)
    _assert_project_access(project, database_path)
    return project


def create_project(payload: dict, workspace_path: Optional[Path] = None) -> dict:
    workspace = normalize_workspace_path(workspace_path)
    database_path = _ensure_database(workspace)
    now = _now()
    name = payload["name"].strip()
    if not name:
        raise ProjectError("项目名称不能为空")

    with connect(database_path) as connection:
        next_id = _next_project_id(connection)
        folder_name = f"project-{next_id:04d}-{_safe_folder_name(name)}"
        folder_path = Path("projects") / folder_name
        absolute_folder_path = workspace / folder_path
        if absolute_folder_path.exists():
            raise ProjectError("项目目录已存在")

        try:
            absolute_folder_path.mkdir(parents=True)
            for subdirectory in PROJECT_SUBDIRECTORIES:
                (absolute_folder_path / subdirectory).mkdir()
        except OSError as exc:
            raise ProjectError(f"创建项目目录失败: {exc}") from exc

        try:
            cursor = connection.execute(
                """
                INSERT INTO projects (
                    name, created_by, source, start_date, end_date, budget, partners, owner,
                    finance_owner, technical_contact, paper_target_count, patent_target_count,
                    status, description,
                    folder_path, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    current_username(),
                    payload.get("source"),
                    payload.get("start_date"),
                    payload.get("end_date"),
                    payload.get("budget"),
                    payload.get("partners"),
                    payload.get("owner"),
                    payload.get("finance_owner"),
                    payload.get("technical_contact"),
                    int(payload.get("paper_target_count") or 0),
                    int(payload.get("patent_target_count") or 0),
                    payload.get("status") or "进行中",
                    payload.get("description"),
                    folder_path.as_posix(),
                    now,
                    now,
                ),
            )
            connection.commit()
        except Exception:
            shutil.rmtree(absolute_folder_path, ignore_errors=True)
            raise

        project_id = int(cursor.lastrowid)

    return get_project(project_id, workspace)


def update_project(project_id: int, payload: dict, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)
    allowed_fields = [
        "source",
        "start_date",
        "end_date",
        "budget",
        "partners",
        "owner",
        "finance_owner",
        "technical_contact",
        "paper_target_count",
        "patent_target_count",
        "status",
        "description",
    ]
    updates = {key: payload[key] for key in allowed_fields if key in payload}
    if not updates:
        return get_project(project_id, workspace_path)

    assignments = ", ".join([f"{key} = ?" for key in updates])
    values = list(updates.values()) + [_now(), project_id]
    with connect(database_path) as connection:
        cursor = connection.execute(
            f"""
            UPDATE projects
            SET {assignments}, updated_at = ?
            WHERE id = ? AND deleted_at IS NULL
            """,
            values,
        )
        connection.commit()

    if cursor.rowcount == 0:
        raise ProjectError("项目不存在")
    return get_project(project_id, workspace_path)


def rename_project(project_id: int, name: str, workspace_path: Optional[Path] = None) -> dict:
    workspace = normalize_workspace_path(workspace_path)
    database_path = _ensure_database(workspace)
    project = get_project(project_id, workspace)
    new_name = name.strip()
    if not new_name:
        raise ProjectError("项目名称不能为空")

    old_relative_path = Path(project["folder_path"])
    old_path = workspace / old_relative_path
    prefix = old_relative_path.name.split("-", 2)[:2]
    folder_name = "-".join(prefix + [_safe_folder_name(new_name)])
    new_relative_path = Path("projects") / folder_name
    new_path = workspace / new_relative_path

    if new_path != old_path and new_path.exists():
        raise ProjectError("目标项目目录已存在")

    try:
        if old_path.exists() and new_path != old_path:
            old_path.rename(new_path)
    except OSError as exc:
        raise ProjectError(f"重命名项目目录失败: {exc}") from exc

    with connect(database_path) as connection:
        connection.execute(
            """
            UPDATE projects
            SET name = ?, folder_path = ?, updated_at = ?
            WHERE id = ? AND deleted_at IS NULL
            """,
            (new_name, new_relative_path.as_posix(), _now(), project_id),
        )
        connection.commit()

    return get_project(project_id, workspace)


def delete_project(project_id: int, delete_folder: bool = False, workspace_path: Optional[Path] = None) -> dict:
    workspace = normalize_workspace_path(workspace_path)
    database_path = _ensure_database(workspace)
    project = get_project(project_id, workspace)
    now = _now()
    folder_deleted = False

    if delete_folder:
        folder_path = workspace / Path(project["folder_path"])
        if folder_path.exists():
            try:
                shutil.rmtree(folder_path)
                folder_deleted = True
            except OSError as exc:
                raise ProjectError(f"删除项目文件夹失败: {exc}") from exc

    with connect(database_path) as connection:
        cursor = connection.execute(
            """
            UPDATE projects
            SET deleted_at = ?, updated_at = ?
            WHERE id = ? AND deleted_at IS NULL
            """,
            (now, now, project_id),
        )
        connection.commit()

    if cursor.rowcount == 0:
        raise ProjectError("项目不存在")

    return {
        "id": project_id,
        "deleted": True,
        "folder_deleted": folder_deleted,
        "folder_path": project["folder_path"],
    }


def get_project_knowledge(project_id: int, workspace_path: Optional[Path] = None) -> dict:
    workspace = normalize_workspace_path(workspace_path)
    project = get_project(project_id, workspace)
    knowledge_path = _knowledge_file_path(workspace, project)
    if not knowledge_path.exists():
        return {
            "content": "",
            "file_path": str(knowledge_path.relative_to(workspace)),
        }

    return {
        "content": knowledge_path.read_text(encoding="utf-8"),
        "file_path": str(knowledge_path.relative_to(workspace)),
    }


def save_project_knowledge(project_id: int, content: str, workspace_path: Optional[Path] = None) -> dict:
    workspace = normalize_workspace_path(workspace_path)
    project = get_project(project_id, workspace)
    knowledge_path = _knowledge_file_path(workspace, project)
    knowledge_path.parent.mkdir(parents=True, exist_ok=True)
    knowledge_path.write_text(content, encoding="utf-8")

    return {
        "content": content,
        "file_path": str(knowledge_path.relative_to(workspace)),
    }


def get_project_meeting_workspace(project_id: int, workspace_path: Optional[Path] = None) -> dict:
    workspace = normalize_workspace_path(workspace_path)
    database_path = _ensure_database(workspace)
    project = get_project(project_id, workspace)
    items = _list_meetings(database_path, project_id)
    latest = items[0] if items else None
    last_action_content = ""
    if latest and latest.get("action_items_path"):
        action_path = workspace / Path(latest["action_items_path"])
        if action_path.exists():
            last_action_content = action_path.read_text(encoding="utf-8")

    return {
        "last_meeting_date": latest.get("meeting_date") if latest else None,
        "last_action_items": last_action_content,
        "items": items,
        "total": len(items),
    }


def save_project_meeting(
    project_id: int,
    meeting_date: str,
    progress: str,
    action_items: str,
    workspace_path: Optional[Path] = None,
) -> dict:
    workspace = normalize_workspace_path(workspace_path)
    database_path = _ensure_database(workspace)
    project = get_project(project_id, workspace)
    date_value = str(meeting_date or "").strip()
    if not date_value:
        raise ProjectError("请填写本次日期")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_value):
        raise ProjectError("日期格式应为 YYYY-MM-DD")

    meeting_dir = workspace / Path(project["folder_path"]) / "项目例会"
    meeting_dir.mkdir(parents=True, exist_ok=True)
    progress_path = meeting_dir / f"{date_value}-Progress.md"
    action_path = meeting_dir / f"{date_value}-Action-Items.md"
    progress_path.write_text(progress or "", encoding="utf-8")
    action_path.write_text(action_items or "", encoding="utf-8")

    now = _now()
    relative_progress = progress_path.relative_to(workspace).as_posix()
    relative_action = action_path.relative_to(workspace).as_posix()
    with connect(database_path) as connection:
        existing = connection.execute(
            """
            SELECT id
            FROM meetings
            WHERE project_id = ? AND meeting_date = ? AND deleted_at IS NULL
            """,
            (project_id, date_value),
        ).fetchone()
        if existing:
            meeting_id = int(existing["id"])
            connection.execute(
                """
                UPDATE meetings
                SET topic = ?, progress_path = ?, action_items_path = ?,
                    action_items = ?, updated_at = ?
                WHERE id = ?
                """,
                ("项目例会", relative_progress, relative_action, action_items, now, meeting_id),
            )
        else:
            cursor = connection.execute(
                """
                INSERT INTO meetings (
                    project_id, meeting_date, topic, progress_path, action_items_path,
                    action_items, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (project_id, date_value, "项目例会", relative_progress, relative_action, action_items, now, now),
            )
            meeting_id = int(cursor.lastrowid)
        connection.commit()

    return get_project_meeting(meeting_id, workspace)


def get_project_meeting(meeting_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM meetings WHERE id = ? AND deleted_at IS NULL",
            (meeting_id,),
        ).fetchone()
    if not row:
        raise ProjectError("例会记录不存在")
    record = dict(row)
    get_project(int(record["project_id"]), workspace_path)
    return record


def get_project_meeting_file(
    meeting_id: int,
    file_kind: str,
    workspace_path: Optional[Path] = None,
) -> tuple[Path, dict]:
    workspace = normalize_workspace_path(workspace_path)
    record = get_project_meeting(meeting_id, workspace)
    field = "progress_path" if file_kind == "progress" else "action_items_path"
    if not record.get(field):
        raise ProjectError("例会文件不存在")
    file_path = workspace / Path(record[field])
    if not file_path.exists():
        raise ProjectError("例会文件不存在或已被移动")
    return file_path, record


def list_project_milestones(project_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)

    with connect(database_path) as connection:
        items = rows_to_dicts(
            connection.execute(
                """
                SELECT *
                FROM milestones
                WHERE project_id = ? AND deleted_at IS NULL
                ORDER BY due_date IS NULL, due_date ASC, id ASC
                """,
                (project_id,),
            )
        )

    return {"items": items, "total": len(items)}


def create_project_milestone(project_id: int, payload: dict, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)
    now = _now()
    target = payload.get("target", "").strip()
    if not target:
        raise ProjectError("节点目标不能为空")

    with connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO milestones (
                project_id, due_date, owner, target, assessment, status,
                note, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                payload.get("due_date"),
                payload.get("owner"),
                target,
                payload.get("assessment"),
                payload.get("status") or "未开始",
                payload.get("note"),
                now,
                now,
            ),
        )
        connection.commit()
        milestone_id = int(cursor.lastrowid)

    return get_project_milestone(milestone_id, workspace_path)


def get_project_milestone(milestone_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM milestones WHERE id = ? AND deleted_at IS NULL",
            (milestone_id,),
        ).fetchone()

    if not row:
        raise ProjectError("节点不存在")
    record = dict(row)
    get_project(int(record["project_id"]), workspace_path)
    return record


def update_project_milestone(milestone_id: int, payload: dict, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project_milestone(milestone_id, workspace_path)
    allowed_fields = ["due_date", "owner", "target", "assessment", "status", "note"]
    updates = {key: payload[key] for key in allowed_fields if key in payload}
    if not updates:
        return get_project_milestone(milestone_id, workspace_path)
    if "target" in updates and not str(updates["target"] or "").strip():
        raise ProjectError("节点目标不能为空")

    assignments = ", ".join([f"{key} = ?" for key in updates])
    values = list(updates.values()) + [_now(), milestone_id]
    with connect(database_path) as connection:
        cursor = connection.execute(
            f"""
            UPDATE milestones
            SET {assignments}, updated_at = ?
            WHERE id = ? AND deleted_at IS NULL
            """,
            values,
        )
        connection.commit()

    if cursor.rowcount == 0:
        raise ProjectError("节点不存在")
    return get_project_milestone(milestone_id, workspace_path)


def list_raw_files(project_id: int, workspace_path: Optional[Path] = None) -> dict:
    return list_project_files_by_category(project_id, "raw_files", workspace_path)


def list_project_files_by_category(project_id: int, category: str, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)

    with connect(database_path) as connection:
        items = rows_to_dicts(
            connection.execute(
                """
                SELECT *
                FROM project_files
                WHERE project_id = ? AND category = ? AND deleted_at IS NULL
                ORDER BY created_at DESC, id DESC
                """,
                (project_id, category),
            )
        )

    return {"items": items, "total": len(items)}


def save_raw_file(
    project_id: int,
    filename: str,
    file_obj: BinaryIO,
    content_type: Optional[str],
    workspace_path: Optional[Path] = None,
) -> dict:
    return save_project_file_by_category(
        project_id,
        "raw_files",
        "项目文档",
        filename,
        file_obj,
        content_type,
        workspace_path,
    )


def save_project_file_by_category(
    project_id: int,
    category: str,
    subdirectory: str,
    filename: str,
    file_obj: BinaryIO,
    content_type: Optional[str],
    workspace_path: Optional[Path] = None,
) -> dict:
    workspace = normalize_workspace_path(workspace_path)
    database_path = _ensure_database(workspace)
    project = get_project(project_id, workspace)
    now = _now()
    safe_filename = _safe_file_name(filename)
    target_dir = workspace / Path(project["folder_path"]) / subdirectory
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = _unique_file_path(target_dir / safe_filename)

    try:
        with target_path.open("wb") as output:
            shutil.copyfileobj(file_obj, output)
    except OSError as exc:
        raise ProjectError(f"保存文件失败: {exc}") from exc

    relative_path = target_path.relative_to(workspace).as_posix()
    with connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO project_files (
                project_id, category, title, file_type, file_path,
                original_filename, file_size, mime_type, note,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                category,
                Path(filename).name,
                target_path.suffix.lstrip(".").lower(),
                relative_path,
                filename,
                target_path.stat().st_size,
                content_type,
                None,
                now,
                now,
            ),
        )
        connection.commit()
        file_id = int(cursor.lastrowid)

    return get_project_file(file_id, workspace)


def list_progress_tasks(project_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)
    with connect(database_path) as connection:
        items = rows_to_dicts(
            connection.execute(
                """
                SELECT *
                FROM project_progress_tasks
                WHERE project_id = ? AND deleted_at IS NULL
                ORDER BY start_date IS NULL, start_date ASC, id ASC
                """,
                (project_id,),
            )
        )
    return {"items": items, "total": len(items)}


def create_progress_task(project_id: int, payload: dict, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)
    task_name = str(payload.get("task_name") or "").strip()
    if not task_name:
        raise ProjectError("任务名称不能为空")
    progress_percent = _clamp_percent(payload.get("progress_percent"))
    now = _now()
    with connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO project_progress_tasks (
                project_id, subject_name, task_name, owner, start_date, end_date,
                progress_percent, status, progress_note, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                payload.get("subject_name"),
                task_name,
                payload.get("owner"),
                payload.get("start_date"),
                payload.get("end_date"),
                progress_percent,
                payload.get("status") or _status_from_percent(progress_percent),
                payload.get("progress_note"),
                now,
                now,
            ),
        )
        connection.commit()
        task_id = int(cursor.lastrowid)
    return get_progress_task(task_id, workspace_path)


def update_progress_task(task_id: int, payload: dict, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_progress_task(task_id, workspace_path)
    allowed_fields = [
        "subject_name",
        "task_name",
        "owner",
        "start_date",
        "end_date",
        "progress_percent",
        "status",
        "progress_note",
    ]
    updates = {key: payload[key] for key in allowed_fields if key in payload}
    if "task_name" in updates and not str(updates["task_name"] or "").strip():
        raise ProjectError("任务名称不能为空")
    if "progress_percent" in updates:
        updates["progress_percent"] = _clamp_percent(updates["progress_percent"])
    if not updates:
        return get_progress_task(task_id, workspace_path)
    assignments = ", ".join([f"{key} = ?" for key in updates])
    values = list(updates.values()) + [_now(), task_id]
    with connect(database_path) as connection:
        cursor = connection.execute(
            f"""
            UPDATE project_progress_tasks
            SET {assignments}, updated_at = ?
            WHERE id = ? AND deleted_at IS NULL
            """,
            values,
        )
        connection.commit()
    if cursor.rowcount == 0:
        raise ProjectError("任务不存在")
    return get_progress_task(task_id, workspace_path)


def get_progress_task(task_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM project_progress_tasks WHERE id = ? AND deleted_at IS NULL",
            (task_id,),
        ).fetchone()
    if not row:
        raise ProjectError("任务不存在")
    record = dict(row)
    get_project(int(record["project_id"]), workspace_path)
    return record


def list_equipment_plans(project_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)
    with connect(database_path) as connection:
        items = rows_to_dicts(
            connection.execute(
                """
                SELECT *
                FROM equipment_plans
                WHERE project_id = ? AND deleted_at IS NULL
                ORDER BY plan_time IS NULL, plan_time ASC, id ASC
                """,
                (project_id,),
            )
        )
    return {"items": items, "total": len(items)}


def create_equipment_plan(project_id: int, payload: dict, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)
    now = _now()
    with connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO equipment_plans (
                project_id, plan_time, budget, supplier,
                closure_material_requirements, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                payload.get("plan_time"),
                payload.get("budget"),
                payload.get("supplier"),
                payload.get("closure_material_requirements"),
                now,
                now,
            ),
        )
        connection.commit()
        plan_id = int(cursor.lastrowid)
    return get_equipment_plan(plan_id, workspace_path)


def update_equipment_plan(plan_id: int, payload: dict, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_equipment_plan(plan_id, workspace_path)
    allowed_fields = ["plan_time", "budget", "supplier", "closure_material_requirements"]
    updates = {key: payload[key] for key in allowed_fields if key in payload}
    if not updates:
        return get_equipment_plan(plan_id, workspace_path)
    assignments = ", ".join([f"{key} = ?" for key in updates])
    values = list(updates.values()) + [_now(), plan_id]
    with connect(database_path) as connection:
        cursor = connection.execute(
            f"""
            UPDATE equipment_plans
            SET {assignments}, updated_at = ?
            WHERE id = ? AND deleted_at IS NULL
            """,
            values,
        )
        connection.commit()
    if cursor.rowcount == 0:
        raise ProjectError("设备/IP/流片规划不存在")
    return get_equipment_plan(plan_id, workspace_path)


def get_equipment_plan(plan_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM equipment_plans WHERE id = ? AND deleted_at IS NULL",
            (plan_id,),
        ).fetchone()
    if not row:
        raise ProjectError("设备/IP/流片规划不存在")
    record = dict(row)
    get_project(int(record["project_id"]), workspace_path)
    return record


def list_project_papers(project_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)

    with connect(database_path) as connection:
        items = rows_to_dicts(
            connection.execute(
                """
                SELECT *
                FROM papers
                WHERE project_id = ? AND deleted_at IS NULL
                ORDER BY sequence_no IS NULL, sequence_no ASC, id ASC
                """,
                (project_id,),
            )
        )

    return {"items": items, "total": len(items)}


def save_project_paper(
    project_id: int,
    payload: dict,
    filename: str,
    file_obj: BinaryIO,
    content_type: Optional[str],
    workspace_path: Optional[Path] = None,
) -> dict:
    workspace = normalize_workspace_path(workspace_path)
    database_path = _ensure_database(workspace)
    project = get_project(project_id, workspace)
    title = str(payload.get("title") or "").strip()
    if not title:
        raise ProjectError("论文名称不能为空")
    now = _now()
    target_path = _save_upload_to_project(workspace, project, "论文-专利/论文", filename, file_obj)

    with connect(database_path) as connection:
        sequence_no = payload.get("sequence_no")
        if sequence_no is None:
            sequence_no = _next_publication_sequence(connection, "papers", project_id)
        cursor = connection.execute(
            """
            INSERT INTO papers (
                project_id, sequence_no, title, authors, label_type, status,
                pdf_path, note, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                sequence_no,
                title,
                payload.get("authors"),
                payload.get("label_type"),
                payload.get("status") or "已上传",
                target_path.relative_to(workspace).as_posix(),
                payload.get("note"),
                now,
                now,
            ),
        )
        connection.commit()
        paper_id = int(cursor.lastrowid)

    return get_project_paper(paper_id, workspace)


def get_project_paper(paper_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM papers WHERE id = ? AND deleted_at IS NULL",
            (paper_id,),
        ).fetchone()
    if not row:
        raise ProjectError("论文记录不存在")
    record = dict(row)
    get_project(int(record["project_id"]), workspace_path)
    return record


def get_project_paper_path(paper_id: int, workspace_path: Optional[Path] = None) -> tuple[Path, dict]:
    workspace = normalize_workspace_path(workspace_path)
    record = get_project_paper(paper_id, workspace)
    if not record.get("pdf_path"):
        raise ProjectError("论文文件不存在")
    file_path = workspace / Path(record["pdf_path"])
    if not file_path.exists():
        raise ProjectError("论文文件不存在或已被移动")
    return file_path, record


def delete_project_paper(paper_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project_paper(paper_id, workspace_path)
    now = _now()
    with connect(database_path) as connection:
        cursor = connection.execute(
            """
            UPDATE papers
            SET deleted_at = ?, updated_at = ?
            WHERE id = ? AND deleted_at IS NULL
            """,
            (now, now, paper_id),
        )
        connection.commit()
    if cursor.rowcount == 0:
        raise ProjectError("论文记录不存在")
    return {"id": paper_id, "deleted": True}


def list_project_patents(project_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)

    with connect(database_path) as connection:
        items = rows_to_dicts(
            connection.execute(
                """
                SELECT *
                FROM patents
                WHERE project_id = ? AND deleted_at IS NULL
                ORDER BY sequence_no IS NULL, sequence_no ASC, id ASC
                """,
                (project_id,),
            )
        )

    return {"items": items, "total": len(items)}


def save_project_patent(
    project_id: int,
    payload: dict,
    filename: str,
    file_obj: BinaryIO,
    content_type: Optional[str],
    workspace_path: Optional[Path] = None,
) -> dict:
    workspace = normalize_workspace_path(workspace_path)
    database_path = _ensure_database(workspace)
    project = get_project(project_id, workspace)
    title = str(payload.get("title") or "").strip()
    if not title:
        raise ProjectError("专利名称不能为空")
    now = _now()
    target_path = _save_upload_to_project(workspace, project, "论文-专利/专利", filename, file_obj)

    with connect(database_path) as connection:
        sequence_no = payload.get("sequence_no")
        if sequence_no is None:
            sequence_no = _next_publication_sequence(connection, "patents", project_id)
        cursor = connection.execute(
            """
            INSERT INTO patents (
                project_id, sequence_no, title, inventors, application_no,
                label_type, status, pdf_path, note, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                sequence_no,
                title,
                payload.get("inventors"),
                payload.get("application_no"),
                payload.get("label_type"),
                payload.get("status") or "已上传",
                target_path.relative_to(workspace).as_posix(),
                payload.get("note"),
                now,
                now,
            ),
        )
        connection.commit()
        patent_id = int(cursor.lastrowid)

    return get_project_patent(patent_id, workspace)


def get_project_patent(patent_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM patents WHERE id = ? AND deleted_at IS NULL",
            (patent_id,),
        ).fetchone()
    if not row:
        raise ProjectError("专利记录不存在")
    record = dict(row)
    get_project(int(record["project_id"]), workspace_path)
    return record


def get_project_patent_path(patent_id: int, workspace_path: Optional[Path] = None) -> tuple[Path, dict]:
    workspace = normalize_workspace_path(workspace_path)
    record = get_project_patent(patent_id, workspace)
    if not record.get("pdf_path"):
        raise ProjectError("专利文件不存在")
    file_path = workspace / Path(record["pdf_path"])
    if not file_path.exists():
        raise ProjectError("专利文件不存在或已被移动")
    return file_path, record


def delete_project_patent(patent_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project_patent(patent_id, workspace_path)
    now = _now()
    with connect(database_path) as connection:
        cursor = connection.execute(
            """
            UPDATE patents
            SET deleted_at = ?, updated_at = ?
            WHERE id = ? AND deleted_at IS NULL
            """,
            (now, now, patent_id),
        )
        connection.commit()
    if cursor.rowcount == 0:
        raise ProjectError("专利记录不存在")
    return {"id": patent_id, "deleted": True}


def get_project_file(file_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM project_files WHERE id = ? AND deleted_at IS NULL",
            (file_id,),
        ).fetchone()

    if not row:
        raise ProjectError("文件不存在")
    record = dict(row)
    get_project(int(record["project_id"]), workspace_path)
    return record


def get_project_file_path(file_id: int, workspace_path: Optional[Path] = None) -> tuple[Path, dict]:
    workspace = normalize_workspace_path(workspace_path)
    record = get_project_file(file_id, workspace)
    file_path = workspace / Path(record["file_path"])
    if not file_path.exists():
        raise ProjectError("文件不存在或已被移动")
    return file_path, record


def list_project_tests(project_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)
    with connect(database_path) as connection:
        items = rows_to_dicts(
            connection.execute(
                """
                SELECT *
                FROM project_tests
                WHERE project_id = ? AND deleted_at IS NULL
                ORDER BY id ASC
                """,
                (project_id,),
            )
        )
    return {"items": items, "total": len(items)}


def create_project_test(project_id: int, payload: dict, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)
    subject_name = str(payload.get("subject_name") or payload.get("name") or "").strip()
    if not subject_name:
        raise ProjectError("课题/待测物名称不能为空")
    now = _now()
    with connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO project_tests (
                project_id, name, subject_name, metric_name,
                expected_midterm_metric, expected_final_metric,
                third_party_test, test_outline_summary, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                subject_name,
                subject_name,
                payload.get("metric_name"),
                payload.get("expected_midterm_metric"),
                payload.get("expected_final_metric"),
                1 if payload.get("third_party_test") else 0,
                payload.get("test_outline_summary"),
                now,
                now,
            ),
        )
        connection.commit()
        test_id = int(cursor.lastrowid)
    return get_project_test(test_id, workspace_path)


def update_project_test(test_id: int, payload: dict, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project_test(test_id, workspace_path)
    allowed_fields = [
        "subject_name",
        "metric_name",
        "expected_midterm_metric",
        "expected_final_metric",
        "third_party_test",
        "test_outline_summary",
    ]
    updates = {key: payload[key] for key in allowed_fields if key in payload}
    if "subject_name" in updates and not str(updates["subject_name"] or "").strip():
        raise ProjectError("课题/待测物名称不能为空")
    if "third_party_test" in updates:
        updates["third_party_test"] = 1 if updates["third_party_test"] else 0
    if "subject_name" in updates:
        updates["name"] = updates["subject_name"]
    if not updates:
        return get_project_test(test_id, workspace_path)

    assignments = ", ".join([f"{key} = ?" for key in updates])
    values = list(updates.values()) + [_now(), test_id]
    with connect(database_path) as connection:
        cursor = connection.execute(
            f"""
            UPDATE project_tests
            SET {assignments}, updated_at = ?
            WHERE id = ? AND deleted_at IS NULL
            """,
            values,
        )
        connection.commit()
    if cursor.rowcount == 0:
        raise ProjectError("测试记录不存在")
    return get_project_test(test_id, workspace_path)


def import_project_tests_csv(
    project_id: int,
    filename: str,
    file_obj: BinaryIO,
    workspace_path: Optional[Path] = None,
) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)
    text = file_obj.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    created: list[dict] = []

    with connect(database_path) as connection:
        for row in reader:
            subject_name = _csv_value(row, "课题/待测物名称", "subject_name", "name")
            if not subject_name:
                continue
            now = _now()
            third_party = _parse_bool(_csv_value(row, "是否第三方测试", "third_party_test"))
            cursor = connection.execute(
                """
                INSERT INTO project_tests (
                    project_id, name, subject_name, metric_name,
                    expected_midterm_metric, expected_final_metric,
                    third_party_test, test_outline_summary, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    subject_name,
                    subject_name,
                    _csv_value(row, "指标名称", "metric_name"),
                    _csv_value(row, "预期中期指标", "expected_midterm_metric"),
                    _csv_value(row, "预期完成指标", "expected_final_metric"),
                    1 if third_party else 0,
                    _csv_value(row, "测试大纲缩略版", "test_outline_summary"),
                    now,
                    now,
                ),
            )
            created.append({"id": int(cursor.lastrowid), "name": subject_name})
        connection.commit()

    return {"filename": filename, "created": len(created), "items": created}


def get_project_test(test_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM project_tests WHERE id = ? AND deleted_at IS NULL",
            (test_id,),
        ).fetchone()
    if not row:
        raise ProjectError("测试记录不存在")
    record = dict(row)
    get_project(int(record["project_id"]), workspace_path)
    return record


def list_project_people(project_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)

    with connect(database_path) as connection:
        items = rows_to_dicts(
            connection.execute(
                """
                SELECT *
                FROM project_people
                WHERE project_id = ? AND deleted_at IS NULL
                ORDER BY sequence_no IS NULL, sequence_no ASC, id ASC
                """,
                (project_id,),
            )
        )
    return {"items": items, "total": len(items)}


def create_project_person(project_id: int, payload: dict, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)
    name = str(payload.get("name") or "").strip()
    if not name:
        raise ProjectError("姓名不能为空")
    now = _now()

    with connect(database_path) as connection:
        sequence_no = payload.get("sequence_no")
        if sequence_no is None:
            sequence_no = _next_person_sequence(connection, project_id)
        cursor = connection.execute(
            """
            INSERT INTO project_people (
                project_id, sequence_no, name, organization, responsibility,
                id_number, email, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                sequence_no,
                name,
                payload.get("organization"),
                payload.get("responsibility"),
                payload.get("id_number"),
                payload.get("email"),
                now,
                now,
            ),
        )
        connection.commit()
        person_id = int(cursor.lastrowid)

    return get_project_person(person_id, workspace_path)


def import_project_people_csv(
    project_id: int,
    filename: str,
    file_obj: BinaryIO,
    workspace_path: Optional[Path] = None,
) -> dict:
    database_path = _ensure_database(workspace_path)
    get_project(project_id, workspace_path)
    raw = file_obj.read()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    created: list[dict] = []

    with connect(database_path) as connection:
        next_sequence = _next_person_sequence(connection, project_id)
        for row in reader:
            name = _csv_value(row, "姓名", "name")
            if not name:
                continue
            sequence_text = _csv_value(row, "序号", "sequence_no")
            sequence_no = _parse_int(sequence_text) if sequence_text else next_sequence
            next_sequence = max(next_sequence, (sequence_no or 0) + 1)
            now = _now()
            cursor = connection.execute(
                """
                INSERT INTO project_people (
                    project_id, sequence_no, name, organization, responsibility,
                    id_number, email, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    sequence_no,
                    name,
                    _csv_value(row, "单位", "organization"),
                    _csv_value(row, "负责内容", "responsibility"),
                    _csv_value(row, "身份证号", "id_number"),
                    _csv_value(row, "邮件", "email"),
                    now,
                    now,
                ),
            )
            created.append({"id": int(cursor.lastrowid), "name": name})
        connection.commit()

    return {
        "filename": filename,
        "created": len(created),
        "items": created,
    }


def get_project_person(person_id: int, workspace_path: Optional[Path] = None) -> dict:
    database_path = _ensure_database(workspace_path)
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM project_people WHERE id = ? AND deleted_at IS NULL",
            (person_id,),
        ).fetchone()
    if not row:
        raise ProjectError("人员记录不存在")
    record = dict(row)
    get_project(int(record["project_id"]), workspace_path)
    return record


def _assert_project_access(project: dict, database_path: Path) -> None:
    user = get_current_user()
    if not user:
        raise ProjectError("请先登录")
    if is_admin(user):
        return
    username = str(user["username"])
    if project.get("created_by") == username:
        return
    with connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM project_access
            WHERE username = ? AND project_id = ?
            """,
            (username, project["id"]),
        ).fetchone()
    if not row:
        raise ProjectError("无权访问该项目")


def _ensure_database(workspace_path: Optional[Path] = None) -> Path:
    workspace = normalize_workspace_path(workspace_path)
    database_path = workspace / "app.sqlite"
    if not database_path.exists():
        initialize_database(database_path)
        (workspace / "projects").mkdir(parents=True, exist_ok=True)
        (workspace / "backups").mkdir(parents=True, exist_ok=True)
        (workspace / "attachments").mkdir(parents=True, exist_ok=True)
    return database_path


def _next_project_id(connection) -> int:
    row = connection.execute("SELECT seq FROM sqlite_sequence WHERE name = 'projects'").fetchone()
    return int(row["seq"]) + 1 if row else 1


def _list_meetings(database_path: Path, project_id: int) -> list[dict]:
    with connect(database_path) as connection:
        return rows_to_dicts(
            connection.execute(
                """
                SELECT *
                FROM meetings
                WHERE project_id = ? AND deleted_at IS NULL
                ORDER BY meeting_date DESC, id DESC
                """,
                (project_id,),
            )
        )


def _next_person_sequence(connection, project_id: int) -> int:
    row = connection.execute(
        """
        SELECT MAX(sequence_no) AS max_sequence
        FROM project_people
        WHERE project_id = ? AND deleted_at IS NULL
        """,
        (project_id,),
    ).fetchone()
    return int(row["max_sequence"] or 0) + 1


def _next_publication_sequence(connection, table: str, project_id: int) -> int:
    row = connection.execute(
        f"""
        SELECT MAX(sequence_no) AS max_sequence
        FROM {table}
        WHERE project_id = ? AND deleted_at IS NULL
        """,
        (project_id,),
    ).fetchone()
    return int(row["max_sequence"] or 0) + 1


def _save_upload_to_project(workspace: Path, project: dict, subdirectory: str, filename: str, file_obj: BinaryIO) -> Path:
    safe_filename = _safe_file_name(filename)
    target_dir = workspace / Path(project["folder_path"]) / subdirectory
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = _unique_file_path(target_dir / safe_filename)
    try:
        with target_path.open("wb") as output:
            shutil.copyfileobj(file_obj, output)
    except OSError as exc:
        raise ProjectError(f"保存文件失败: {exc}") from exc
    return target_path


def _csv_value(row: dict, *keys: str) -> Optional[str]:
    normalized = {str(key).strip(): value for key, value in row.items()}
    for key in keys:
        value = normalized.get(key)
        if value is not None and str(value).strip() != "":
            return str(value).strip()
    return None


def _parse_int(value: Optional[str]) -> Optional[int]:
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(float(str(value).strip()))
    except ValueError:
        return None


def _parse_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "是", "第三方", "需要", "需要第三方测试"}


def _clamp_percent(value) -> int:
    try:
        number = int(float(value or 0))
    except (TypeError, ValueError):
        return 0
    return max(0, min(100, number))


def _status_from_percent(value: int) -> str:
    return "已完成" if value >= 100 else "进行中" if value > 0 else "未开始"


def _safe_folder_name(name: str) -> str:
    safe_name = re.sub(r'[\\/:*?"<>|]+', "-", name.strip())
    safe_name = re.sub(r"\s+", " ", safe_name)
    return safe_name[:80] or "未命名项目"


def _safe_file_name(name: str) -> str:
    safe_name = re.sub(r'[\\/:*?"<>|]+', "-", Path(name).name.strip())
    safe_name = re.sub(r"\s+", " ", safe_name)
    return safe_name or "未命名文件"


def _unique_file_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    index = 1
    while True:
        candidate = parent / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def _knowledge_file_path(workspace: Path, project: dict) -> Path:
    return workspace / Path(project["folder_path"]) / "知识库" / "知识库.md"


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
