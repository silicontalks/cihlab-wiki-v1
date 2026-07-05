# 新 Mac 启动指南

本文说明：当你把整个项目文件夹同步到另一台 Mac 后，如何在新的环境中重新启动本地项目管理 Web App。

## 1. 需要同步的内容

建议同步整个项目根目录，例如：

```text
cihlab-wiki-v1/
├── backend/
├── docs/
├── ProjectWorkspace/
├── 本地项目管理App规划.md
└── .gitignore
```

其中最重要的是：

| 路径 | 作用 |
|---|---|
| `backend/` | FastAPI 后端和 Web 页面代码 |
| `backend/requirements.txt` | Python 依赖列表 |
| `ProjectWorkspace/app.sqlite` | 本地 SQLite 数据库 |
| `ProjectWorkspace/projects/` | 每个项目的文件目录 |
| `ProjectWorkspace/backups/` | SQLite 备份 |

不要只同步 `backend/`，否则项目数据和文件不会一起过去。

## 2. 新 Mac 环境要求

新 Mac 需要有：

- Python 3.9 或更高版本
- 终端 Terminal
- 可以访问 Python 包安装源，首次安装依赖时需要网络

检查 Python：

```bash
python3 --version
```

如果没有 Python 3，可以先安装 Xcode Command Line Tools：

```bash
xcode-select --install
```

## 3. 第一次在新 Mac 上安装依赖

进入同步后的项目目录。

示例：

```bash
cd /path/to/cihlab-wiki-v1
```

创建后端虚拟环境：

```bash
cd backend
python3 -m venv .venv
```

激活虚拟环境：

```bash
source .venv/bin/activate
```

安装依赖：

```bash
python3 -m pip install -r requirements.txt
```

这一步只需要在新 Mac 第一次启动前执行。后续日常启动不需要重复安装，除非 `requirements.txt` 发生变化。

## 4. 启动 Web App

进入后端目录并激活虚拟环境：

```bash
cd /path/to/cihlab-wiki-v1/backend
source .venv/bin/activate
```

启动 FastAPI：

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

看到类似输出说明启动成功：

```text
Uvicorn running on http://127.0.0.1:8000
```

然后在浏览器打开：

```text
http://127.0.0.1:8000
```

API 文档地址：

```text
http://127.0.0.1:8000/docs
```

## 5. 日常启动简化版

如果已经安装过依赖，以后只需要：

```bash
cd /path/to/cihlab-wiki-v1/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

然后打开：

```text
http://127.0.0.1:8000
```

## 6. 停止服务

在终端中按：

```text
Ctrl + C
```

即可停止 Web App。

## 7. 同步软件使用注意事项

这个 App 当前是本地优先模式，数据库保存在：

```text
ProjectWorkspace/app.sqlite
```

同步软件可以同步它，但第一版不建议多台电脑同时编辑同一个工作区。

建议规则：

- 同一时间只在一台 Mac 上打开并编辑。
- 换另一台 Mac 使用前，先确认同步软件已经完成同步。
- 关闭旧 Mac 上的服务后，再在新 Mac 上启动。
- 如果同步软件生成冲突副本，需要先手动处理，避免数据分裂。

常见冲突文件名可能包含：

```text
conflict
conflicted
冲突
副本
```

## 8. 数据是否需要重新初始化

通常不需要。

如果你同步了完整的：

```text
ProjectWorkspace/
```

那么新 Mac 上会直接使用已有的：

```text
ProjectWorkspace/app.sqlite
```

和：

```text
ProjectWorkspace/projects/
```

只有在 `ProjectWorkspace/` 不存在，或者 `app.sqlite` 丢失时，App 才会重新初始化一个新的空工作区。

## 9. 登录账号与项目授权

当前默认账号为：

```text
账号：admin
密码：admin
```

账号、密码和项目授权只通过后台手动修改，不在 Web 页面里提供管理入口。相关数据在：

```text
ProjectWorkspace/app.sqlite
```

主要表：

| 表 | 作用 |
|---|---|
| `app_users` | 账号、密码、是否管理员 |
| `projects.created_by` | 项目创建者 |
| `project_access` | 额外授权某账号访问某项目 |
| `user_sessions` | 登录会话 |

管理员账号 `is_admin = 1` 可以访问所有项目。普通账号可以访问自己创建的项目，也可以访问 `project_access` 表里额外授权的项目。

进入项目根目录后，可以用 `sqlite3` 手动维护：

```bash
sqlite3 ProjectWorkspace/app.sqlite
```

修改 admin 密码示例：

```sql
UPDATE app_users
SET password = 'new-password', updated_at = datetime('now')
WHERE username = 'admin';
```

新增普通账号示例：

```sql
INSERT INTO app_users (username, password, display_name, is_admin, created_at, updated_at)
VALUES ('user1', 'password1', '用户1', 0, datetime('now'), datetime('now'));
```

授权普通账号访问某项目示例：

```sql
INSERT OR IGNORE INTO project_access (username, project_id, created_at)
VALUES ('user1', 5, datetime('now'));
```

取消授权示例：

```sql
DELETE FROM project_access
WHERE username = 'user1' AND project_id = 5;
```

查看项目 ID：

```sql
SELECT id, name, created_by FROM projects WHERE deleted_at IS NULL;
```

## 10. 常见问题

### 10.1 打开 `http://127.0.0.1:8000` 显示无法访问

说明后端服务没有启动，或者启动失败。

检查终端是否还在运行：

```text
Uvicorn running on http://127.0.0.1:8000
```

如果没有，重新执行：

```bash
cd /path/to/cihlab-wiki-v1/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 10.2 端口 8000 被占用

可以换一个端口，例如：

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

然后打开：

```text
http://127.0.0.1:8001
```

### 10.3 提示 `uvicorn: command not found`

通常是虚拟环境没有激活，先执行：

```bash
source .venv/bin/activate
```

如果仍然不行，重新安装依赖：

```bash
python3 -m pip install -r requirements.txt
```

### 10.4 页面能打开，但项目列表为空

优先检查：

```text
ProjectWorkspace/app.sqlite
ProjectWorkspace/projects/
```

是否已经同步到这台 Mac。

如果这两个路径不存在，说明同步目录不完整，或者打开的不是同一个项目根目录。

### 10.5 Python 依赖安装很慢或失败

可以先升级 pip：

```bash
python3 -m pip install --upgrade pip
```

再安装：

```bash
python3 -m pip install -r requirements.txt
```

如果网络环境不稳定，可以稍后重试。

## 11. 建议后续增加的一键启动脚本

后续可以增加一个 macOS 启动脚本，例如：

```text
start-mac.command
```

目标是双击后自动执行：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

这样新 Mac 配好依赖后，就不需要每次手动输入命令。
