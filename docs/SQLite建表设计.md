# SQLite 建表设计

## 1. 目标

本文件定义本地项目管理 Web App 第一版的 SQLite 数据库结构。数据库文件默认放在工作区根目录：

```text
ProjectWorkspace/app.sqlite
```

设计原则：

- 结构化信息存入 SQLite。
- 文件本体存入项目目录。
- 数据库中只保存相对路径。
- 第一版支持单人本地使用，不处理多人并发编辑。
- 删除优先使用软删除，降低误删风险。

## 2. 字段约定

### 2.1 通用字段

主要表都建议包含：

| 字段 | 说明 |
|---|---|
| id | 主键 |
| created_at | 创建时间 |
| updated_at | 更新时间 |
| deleted_at | 软删除时间，空值表示未删除 |

### 2.2 时间格式

- 日期字段使用 `YYYY-MM-DD` 文本。
- 时间戳字段使用 ISO 8601 文本。

### 2.3 路径格式

路径字段只保存相对工作区的路径，例如：

```text
projects/project-0001-高性能芯片测试平台/原始文件/任务书.pdf
```

## 3. 建表 SQL

### 3.1 projects

```sql
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    source TEXT,
    start_date TEXT,
    end_date TEXT,
    budget REAL,
    partners TEXT,
    owner TEXT,
    finance_owner TEXT,
    technical_contact TEXT,
    status TEXT NOT NULL DEFAULT '进行中',
    description TEXT,
    folder_path TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_deleted_at ON projects(deleted_at);
```

### 3.2 project_files

```sql
CREATE TABLE IF NOT EXISTS project_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    file_type TEXT,
    file_path TEXT NOT NULL,
    original_filename TEXT,
    file_size INTEGER,
    mime_type TEXT,
    note TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE INDEX IF NOT EXISTS idx_project_files_project_id ON project_files(project_id);
CREATE INDEX IF NOT EXISTS idx_project_files_category ON project_files(category);
CREATE INDEX IF NOT EXISTS idx_project_files_deleted_at ON project_files(deleted_at);
```

`category` 建议使用以下值：

| 值 | 说明 |
|---|---|
| raw_files | 原始文件 |
| papers | 论文附件 |
| patents | 专利附件 |
| meetings | 周会附件 |
| documents | 项目文档 |
| tests | 测试报告 |

### 3.3 milestones

```sql
CREATE TABLE IF NOT EXISTS milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    due_date TEXT,
    owner TEXT,
    target TEXT NOT NULL,
    assessment TEXT,
    status TEXT NOT NULL DEFAULT '未开始',
    note TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE INDEX IF NOT EXISTS idx_milestones_project_id ON milestones(project_id);
CREATE INDEX IF NOT EXISTS idx_milestones_due_date ON milestones(due_date);
CREATE INDEX IF NOT EXISTS idx_milestones_status ON milestones(status);
CREATE INDEX IF NOT EXISTS idx_milestones_deleted_at ON milestones(deleted_at);
```

`status` 建议使用：

- 未开始
- 进行中
- 已完成
- 延期

### 3.4 project_people

保存项目人员信息。

```sql
CREATE TABLE IF NOT EXISTS project_people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    sequence_no INTEGER,
    name TEXT NOT NULL,
    organization TEXT,
    responsibility TEXT,
    id_number TEXT,
    email TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

页面展示身份证号时需要脱敏，例如 `110XXX34`，避免直接暴露完整敏感信息。

### 3.5 papers

```sql
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    authors TEXT,
    venue TEXT,
    status TEXT NOT NULL DEFAULT '撰写中',
    submit_date TEXT,
    publish_date TEXT,
    pdf_path TEXT,
    note TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE INDEX IF NOT EXISTS idx_papers_project_id ON papers(project_id);
CREATE INDEX IF NOT EXISTS idx_papers_status ON papers(status);
CREATE INDEX IF NOT EXISTS idx_papers_deleted_at ON papers(deleted_at);
```

`status` 建议使用：

- 撰写中
- 投稿中
- 返修
- 已录用
- 已发表

### 3.6 patents

```sql
CREATE TABLE IF NOT EXISTS patents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    inventors TEXT,
    application_no TEXT,
    patent_type TEXT,
    status TEXT NOT NULL DEFAULT '撰写中',
    application_date TEXT,
    grant_date TEXT,
    pdf_path TEXT,
    note TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE INDEX IF NOT EXISTS idx_patents_project_id ON patents(project_id);
CREATE INDEX IF NOT EXISTS idx_patents_status ON patents(status);
CREATE INDEX IF NOT EXISTS idx_patents_application_no ON patents(application_no);
CREATE INDEX IF NOT EXISTS idx_patents_deleted_at ON patents(deleted_at);
```

`status` 建议使用：

- 撰写中
- 已提交
- 已公开
- 已授权

### 3.7 meetings

```sql
CREATE TABLE IF NOT EXISTS meetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    meeting_date TEXT,
    topic TEXT NOT NULL,
    attendees TEXT,
    minutes_path TEXT,
    action_items TEXT,
    note TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE INDEX IF NOT EXISTS idx_meetings_project_id ON meetings(project_id);
CREATE INDEX IF NOT EXISTS idx_meetings_meeting_date ON meetings(meeting_date);
CREATE INDEX IF NOT EXISTS idx_meetings_deleted_at ON meetings(deleted_at);
```

### 3.8 project_tests

表名使用 `project_tests`，避免和部分工具或上下文中的 `tests` 命名混淆。

```sql
CREATE TABLE IF NOT EXISTS project_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    test_date TEXT,
    owner TEXT,
    content TEXT,
    result TEXT,
    report_path TEXT,
    note TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE INDEX IF NOT EXISTS idx_project_tests_project_id ON project_tests(project_id);
CREATE INDEX IF NOT EXISTS idx_project_tests_test_date ON project_tests(test_date);
CREATE INDEX IF NOT EXISTS idx_project_tests_result ON project_tests(result);
CREATE INDEX IF NOT EXISTS idx_project_tests_deleted_at ON project_tests(deleted_at);
```

`result` 建议使用：

- 通过
- 未通过
- 部分通过
- 待确认

### 3.9 app_settings

保存本地 App 设置。

```sql
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT NOT NULL
);
```

建议第一版写入：

| key | value |
|---|---|
| workspace_path | 工作区绝对路径 |
| schema_version | 数据库结构版本 |
| last_backup_at | 最近备份时间 |

## 4. 初始化数据

```sql
INSERT OR IGNORE INTO app_settings (key, value, updated_at)
VALUES ('schema_version', '1', datetime('now'));
```

## 5. 软删除查询约定

默认列表查询都应该带上：

```sql
WHERE deleted_at IS NULL
```

例如：

```sql
SELECT *
FROM projects
WHERE deleted_at IS NULL
ORDER BY updated_at DESC;
```

## 6. 第一版迁移策略

第一版可以先使用简单 SQL 文件初始化数据库：

```text
backend/app/db/schema.sql
```

后续如果表结构变化，再引入 Alembic 或自定义迁移表。

建议增加迁移记录表：

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL
);
```

## 7. 备份策略

建议在以下时机备份 `app.sqlite`：

- App 启动时
- 执行数据库结构迁移前
- 用户手动点击备份
- 检测到同步冲突文件时

备份文件命名：

```text
backups/app-YYYY-MM-DD-HHMMSS.sqlite
```
