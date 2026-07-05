# FastAPI 接口设计

## 1. 目标

本文件定义本地项目管理 Web App 第一版的后端 API。后端采用 FastAPI，负责管理 SQLite 数据库、本地项目目录和文件访问。

第一版 API 只面向本机浏览器使用，默认监听：

```text
http://127.0.0.1:8000
```

## 2. 通用约定

### 2.1 数据格式

- 请求和响应默认使用 JSON。
- 文件上传使用 `multipart/form-data`。
- 日期字段使用 `YYYY-MM-DD`。
- 时间戳字段使用 ISO 8601 字符串，例如 `2026-07-02T10:30:00+08:00`。
- 数据库中保存文件相对路径，不保存系统绝对路径。

### 2.2 通用响应

列表接口建议返回：

```json
{
  "items": [],
  "total": 0
}
```

单条数据接口直接返回对象：

```json
{
  "id": 1,
  "name": "项目A"
}
```

错误响应使用 FastAPI 默认格式：

```json
{
  "detail": "错误说明"
}
```

### 2.3 常见状态码

| 状态码 | 说明 |
|---|---|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 204 | 删除成功，无返回内容 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 409 | 名称冲突、路径冲突或同步冲突 |
| 500 | 服务端错误 |

## 3. 工作区接口

工作区接口用于管理本地 `ProjectWorkspace/`。

### 3.1 获取工作区状态

```text
GET /api/workspace/status
```

响应：

```json
{
  "workspace_path": "/path/to/ProjectWorkspace",
  "database_path": "/path/to/ProjectWorkspace/app.sqlite",
  "projects_path": "/path/to/ProjectWorkspace/projects",
  "initialized": true,
  "conflict_files": [],
  "last_backup_at": "2026-07-02T10:30:00+08:00"
}
```

### 3.2 初始化工作区

```text
POST /api/workspace/init
```

请求：

```json
{
  "workspace_path": "/path/to/ProjectWorkspace"
}
```

行为：

- 创建 `app.sqlite`
- 创建 `projects/`
- 创建 `backups/`
- 执行数据库建表 SQL

### 3.3 创建数据库备份

```text
POST /api/workspace/backup
```

响应：

```json
{
  "backup_path": "backups/app-2026-07-02-103000.sqlite"
}
```

### 3.4 检查同步冲突

```text
GET /api/workspace/conflicts
```

响应：

```json
{
  "items": [
    {
      "path": "app (conflicted copy).sqlite",
      "type": "database",
      "message": "发现疑似同步冲突数据库"
    }
  ],
  "total": 1
}
```

## 4. 项目接口

### 4.1 获取项目列表

```text
GET /api/projects
```

查询参数：

| 参数 | 说明 |
|---|---|
| q | 按项目名称搜索 |
| status | 按项目状态筛选 |

响应：

```json
{
  "items": [
    {
      "id": 1,
      "name": "高性能芯片测试平台",
      "source": "企业合作",
      "start_date": "2026-07-01",
      "budget": 500000,
      "partners": "合作单位A",
      "owner": "负责人A",
      "status": "进行中",
      "folder_path": "projects/project-0001-高性能芯片测试平台"
    }
  ],
  "total": 1
}
```

### 4.2 创建项目

```text
POST /api/projects
```

请求：

```json
{
  "name": "高性能芯片测试平台",
  "source": "企业合作",
  "start_date": "2026-07-01",
  "end_date": null,
  "budget": 500000,
  "partners": "合作单位A",
  "owner": "负责人A",
  "status": "进行中",
  "description": "项目简介"
}
```

行为：

- 写入 `projects` 表。
- 生成项目目录，例如 `projects/project-0001-高性能芯片测试平台/`。
- 创建默认子目录：原始文件、里程碑、论文情况、专利情况、项目周会记录、项目文档、项目测试。

### 4.3 获取项目详情

```text
GET /api/projects/{project_id}
```

### 4.4 更新项目基本信息

```text
PATCH /api/projects/{project_id}
```

请求可以只传需要更新的字段：

```json
{
  "source": "国家项目",
  "budget": 800000,
  "status": "进行中"
}
```

### 4.5 重命名项目

```text
POST /api/projects/{project_id}/rename
```

请求：

```json
{
  "name": "新的项目名称"
}
```

行为：

- 更新项目显示名称。
- 同步更新项目目录名。
- 如果目标目录已存在，返回 `409`。

### 4.6 删除项目

```text
DELETE /api/projects/{project_id}
```

第一版建议做软删除：

- 设置 `deleted_at`
- 不直接删除项目目录

## 5. 文件接口

文件接口用于原始文件、论文 PDF、专利 PDF、项目文档、测试报告等。

### 5.1 获取项目文件列表

```text
GET /api/projects/{project_id}/files
```

查询参数：

| 参数 | 说明 |
|---|---|
| category | 文件分类，例如 `raw_files`、`papers`、`patents`、`documents`、`tests` |

### 5.2 添加文件记录并上传文件

```text
POST /api/projects/{project_id}/files
```

表单字段：

| 字段 | 说明 |
|---|---|
| category | 文件分类 |
| file_type | 文件类型 |
| title | 文件显示名称 |
| note | 备注 |
| file | 上传文件 |

行为：

- 将文件保存到项目对应子目录。
- 写入 `project_files` 表。
- 返回文件记录。

### 5.3 更新文件记录

```text
PATCH /api/files/{file_id}
```

请求：

```json
{
  "title": "任务书最终版",
  "file_type": "任务书",
  "note": "已确认"
}
```

### 5.4 删除文件

```text
DELETE /api/files/{file_id}
```

第一版建议：

- 默认只删除数据库记录。
- 文件移动到项目目录下的 `.trash/`。
- 后续再做永久删除。

### 5.5 下载文件

```text
GET /api/files/{file_id}/download
```

### 5.6 预览 PDF

```text
GET /api/files/{file_id}/preview
```

返回 PDF 文件流，前端使用浏览器内置 PDF 预览能力展示。

## 6. 里程碑接口

### 6.1 获取里程碑列表

```text
GET /api/projects/{project_id}/milestones
```

### 6.2 创建里程碑

```text
POST /api/projects/{project_id}/milestones
```

请求：

```json
{
  "due_date": "2026-09-30",
  "owner": "负责人A",
  "target": "完成第一版系统验证",
  "assessment": "提交测试报告并完成评审",
  "status": "未开始",
  "note": ""
}
```

### 6.3 更新里程碑

```text
PATCH /api/milestones/{milestone_id}
```

### 6.4 删除里程碑

```text
DELETE /api/milestones/{milestone_id}
```

## 7. 论文接口

### 7.1 获取论文列表

```text
GET /api/projects/{project_id}/papers
```

### 7.2 创建论文记录

```text
POST /api/projects/{project_id}/papers
```

请求：

```json
{
  "title": "论文标题",
  "authors": "作者A, 作者B",
  "venue": "会议或期刊",
  "status": "撰写中",
  "submit_date": null,
  "publish_date": null,
  "pdf_path": null,
  "note": ""
}
```

### 7.3 更新论文记录

```text
PATCH /api/papers/{paper_id}
```

### 7.4 删除论文记录

```text
DELETE /api/papers/{paper_id}
```

## 8. 专利接口

### 8.1 获取专利列表

```text
GET /api/projects/{project_id}/patents
```

### 8.2 创建专利记录

```text
POST /api/projects/{project_id}/patents
```

请求：

```json
{
  "title": "专利名称",
  "inventors": "发明人A, 发明人B",
  "application_no": null,
  "patent_type": "发明",
  "status": "撰写中",
  "application_date": null,
  "grant_date": null,
  "pdf_path": null,
  "note": ""
}
```

### 8.3 更新专利记录

```text
PATCH /api/patents/{patent_id}
```

### 8.4 删除专利记录

```text
DELETE /api/patents/{patent_id}
```

## 9. 周会接口

### 9.1 获取周会列表

```text
GET /api/projects/{project_id}/meetings
```

### 9.2 创建周会记录

```text
POST /api/projects/{project_id}/meetings
```

请求：

```json
{
  "meeting_date": "2026-07-02",
  "topic": "项目周会",
  "attendees": "成员A, 成员B",
  "minutes_path": null,
  "action_items": "行动项",
  "note": ""
}
```

### 9.3 更新周会记录

```text
PATCH /api/meetings/{meeting_id}
```

### 9.4 删除周会记录

```text
DELETE /api/meetings/{meeting_id}
```

## 10. 测试接口

### 10.1 获取测试列表

```text
GET /api/projects/{project_id}/tests
```

### 10.2 创建测试记录

```text
POST /api/projects/{project_id}/tests
```

请求：

```json
{
  "name": "测试项名称",
  "test_date": "2026-07-02",
  "owner": "负责人A",
  "content": "测试内容",
  "result": "通过",
  "report_path": null,
  "note": ""
}
```

### 10.3 更新测试记录

```text
PATCH /api/tests/{test_id}
```

### 10.4 删除测试记录

```text
DELETE /api/tests/{test_id}
```

## 11. 第一版接口开发顺序

建议按以下顺序实现：

1. `GET /api/health`
2. `POST /api/workspace/init`
3. `GET /api/workspace/status`
4. `GET /api/projects`
5. `POST /api/projects`
6. `GET /api/projects/{project_id}`
7. `PATCH /api/projects/{project_id}`
8. `POST /api/projects/{project_id}/rename`
9. `GET /api/projects/{project_id}/milestones`
10. `POST /api/projects/{project_id}/milestones`
11. `PATCH /api/milestones/{milestone_id}`
12. `DELETE /api/milestones/{milestone_id}`
13. 文件上传、下载和 PDF 预览接口

