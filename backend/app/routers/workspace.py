from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.workspace import (
    WorkspaceError,
    create_backup,
    get_workspace_status,
    initialize_workspace,
)


router = APIRouter(prefix="/workspace", tags=["workspace"])


class WorkspaceInitRequest(BaseModel):
    workspace_path: Optional[str] = Field(default=None, min_length=1)


@router.get("/status")
def read_workspace_status(workspace_path: Optional[str] = None) -> dict:
    try:
        return get_workspace_status(Path(workspace_path) if workspace_path else None)
    except WorkspaceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/init", status_code=status.HTTP_201_CREATED)
def init_workspace(payload: WorkspaceInitRequest) -> dict:
    try:
        return initialize_workspace(Path(payload.workspace_path) if payload.workspace_path else None)
    except WorkspaceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/backup")
def backup_workspace(workspace_path: Optional[str] = None) -> dict:
    try:
        return create_backup(Path(workspace_path) if workspace_path else None)
    except WorkspaceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/conflicts")
def read_workspace_conflicts(workspace_path: Optional[str] = None) -> dict:
    try:
        status_data = get_workspace_status(Path(workspace_path) if workspace_path else None)
        items = [
            {
                "path": path,
                "type": "database" if path.endswith(".sqlite") else "file",
                "message": "发现疑似同步冲突文件",
            }
            for path in status_data["conflict_files"]
        ]
        return {"items": items, "total": len(items)}
    except WorkspaceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
