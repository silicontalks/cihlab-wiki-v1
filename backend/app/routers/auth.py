from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Cookie, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.services.auth import AuthError, get_user_by_token, login_user, logout_user, public_user


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


@router.post("/login")
def login(payload: LoginRequest, response: Response, workspace_path: Optional[str] = None) -> dict:
    try:
        result = login_user(payload.username, payload.password, Path(workspace_path) if workspace_path else None)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    response.set_cookie(
        "session_token",
        result["token"],
        httponly=True,
        samesite="lax",
        max_age=14 * 24 * 60 * 60,
    )
    return result


@router.post("/logout")
def logout(response: Response, workspace_path: Optional[str] = None, session_token: Optional[str] = Cookie(None)) -> dict:
    logout_user(session_token, Path(workspace_path) if workspace_path else None)
    response.delete_cookie("session_token")
    return {"ok": True}


@router.get("/me")
def read_current_user(workspace_path: Optional[str] = None, session_token: Optional[str] = Cookie(None)) -> dict:
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    try:
        user = get_user_by_token(session_token, Path(workspace_path) if workspace_path else None)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return {"user": public_user(user)}
