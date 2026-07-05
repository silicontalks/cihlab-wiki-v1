from __future__ import annotations

import secrets
from contextvars import ContextVar
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Query, status

from app.database import connect
from app.services.workspace import normalize_workspace_path


SESSION_DAYS = 14
_current_user: ContextVar[Optional[dict]] = ContextVar("current_user", default=None)


class AuthError(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def login_user(username: str, password: str, workspace_path: Optional[Path] = None) -> dict:
    workspace = normalize_workspace_path(workspace_path)
    database_path = workspace / "app.sqlite"
    username_value = username.strip()
    with connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM app_users
            WHERE username = ? AND deleted_at IS NULL
            """,
            (username_value,),
        ).fetchone()
        if not row or row["password"] != password:
            raise AuthError("账号或密码不正确")
        token = secrets.token_urlsafe(32)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)).astimezone().isoformat(timespec="seconds")
        connection.execute(
            """
            INSERT INTO user_sessions (token, username, created_at, expires_at)
            VALUES (?, ?, ?, ?)
            """,
            (token, username_value, now_iso(), expires_at),
        )
        connection.commit()
    return {"token": token, "user": public_user(dict(row)), "expires_at": expires_at}


def logout_user(token: Optional[str], workspace_path: Optional[Path] = None) -> None:
    if not token:
        return
    workspace = normalize_workspace_path(workspace_path)
    database_path = workspace / "app.sqlite"
    with connect(database_path) as connection:
        connection.execute("DELETE FROM user_sessions WHERE token = ?", (token,))
        connection.commit()


def get_user_by_token(token: str, workspace_path: Optional[Path] = None) -> dict:
    workspace = normalize_workspace_path(workspace_path)
    database_path = workspace / "app.sqlite"
    with connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT u.*
            FROM user_sessions s
            JOIN app_users u ON u.username = s.username
            WHERE s.token = ?
              AND u.deleted_at IS NULL
              AND s.expires_at > ?
            """,
            (token, now_iso()),
        ).fetchone()
    if not row:
        raise AuthError("请先登录")
    return dict(row)


def public_user(user: dict) -> dict:
    return {
        "username": user["username"],
        "is_admin": bool(user.get("is_admin")),
        "display_name": user.get("display_name") or user["username"],
    }


def set_current_user(user: Optional[dict]) -> None:
    _current_user.set(user)


def get_current_user() -> Optional[dict]:
    return _current_user.get()


def is_admin(user: Optional[dict] = None) -> bool:
    current = user if user is not None else get_current_user()
    return bool(current and current.get("is_admin"))


def current_username() -> str:
    user = get_current_user()
    return str(user["username"]) if user else "admin"


def require_auth_context(
    workspace_path: Optional[str] = None,
    session_token: Optional[str] = Cookie(None),
    token: Optional[str] = Query(None),
) -> dict:
    auth_token = session_token or token
    if not auth_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    try:
        user = get_user_by_token(auth_token, Path(workspace_path) if workspace_path else None)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    set_current_user(user)
    return user


def current_auth_user(_: dict = Depends(require_auth_context)) -> dict:
    return _
