from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routers import auth, projects, workspace
from app.services.auth import current_auth_user


APP_DIR = Path(__file__).resolve().parent
WEB_DIR = APP_DIR / "web"

app = FastAPI(
    title="本地项目管理 Web App API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workspace.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api", dependencies=[Depends(current_auth_user)])
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
def read_app() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
