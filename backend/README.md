# Backend

FastAPI backend for the local project management Web App.

如果是在另一台 Mac 上通过同步文件夹重新启动，请优先阅读：

```text
../docs/新Mac启动指南.md
```

## Install

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Run

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## First API Calls

Health check:

```text
GET /api/health
```

Initialize workspace:

```text
POST /api/workspace/init
```

```json
{
  "workspace_path": "../ProjectWorkspace"
}
```

Workspace status:

```text
GET /api/workspace/status?workspace_path=../ProjectWorkspace
```

## Workspace Path

By default, the app stores runtime data in the repository-level `ProjectWorkspace/` directory.

For server deployment, set:

```bash
export PROJECT_WORKSPACE_PATH=/data/ProjectWorkspace
```

Then start the production server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

On a server, keep SQLite and uploaded project files outside Git:

```text
/data/ProjectWorkspace/app.sqlite
/data/ProjectWorkspace/projects/
/data/ProjectWorkspace/backups/
```

See `../docs/阿里轻量云部署指南.md` for the full systemd and Nginx setup.
