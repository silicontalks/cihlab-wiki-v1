PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_by TEXT NOT NULL DEFAULT 'admin',
    source TEXT,
    start_date TEXT,
    end_date TEXT,
    budget REAL,
    partners TEXT,
    owner TEXT,
    finance_owner TEXT,
    technical_contact TEXT,
    paper_target_count INTEGER NOT NULL DEFAULT 0,
    patent_target_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT '进行中',
    description TEXT,
    folder_path TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
CREATE INDEX IF NOT EXISTS idx_projects_created_by ON projects(created_by);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_deleted_at ON projects(deleted_at);

CREATE TABLE IF NOT EXISTS app_users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    display_name TEXT,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_app_users_deleted_at ON app_users(deleted_at);

CREATE TABLE IF NOT EXISTS project_access (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    project_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(username, project_id),
    FOREIGN KEY (username) REFERENCES app_users(username),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE INDEX IF NOT EXISTS idx_project_access_username ON project_access(username);
CREATE INDEX IF NOT EXISTS idx_project_access_project_id ON project_access(project_id);

CREATE TABLE IF NOT EXISTS user_sessions (
    token TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    FOREIGN KEY (username) REFERENCES app_users(username)
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_username ON user_sessions(username);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

INSERT OR IGNORE INTO app_users (username, password, display_name, is_admin, created_at, updated_at)
VALUES ('admin', 'admin', '管理员', 1, datetime('now'), datetime('now'));

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

CREATE INDEX IF NOT EXISTS idx_project_people_project_id ON project_people(project_id);
CREATE INDEX IF NOT EXISTS idx_project_people_sequence_no ON project_people(sequence_no);
CREATE INDEX IF NOT EXISTS idx_project_people_deleted_at ON project_people(deleted_at);

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

CREATE TABLE IF NOT EXISTS project_progress_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    subject_name TEXT,
    task_name TEXT NOT NULL,
    owner TEXT,
    start_date TEXT,
    end_date TEXT,
    progress_percent INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT '未开始',
    progress_note TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE INDEX IF NOT EXISTS idx_project_progress_tasks_project_id ON project_progress_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_project_progress_tasks_start_date ON project_progress_tasks(start_date);
CREATE INDEX IF NOT EXISTS idx_project_progress_tasks_end_date ON project_progress_tasks(end_date);
CREATE INDEX IF NOT EXISTS idx_project_progress_tasks_deleted_at ON project_progress_tasks(deleted_at);

CREATE TABLE IF NOT EXISTS equipment_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    plan_time TEXT,
    budget REAL,
    supplier TEXT,
    closure_material_requirements TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE INDEX IF NOT EXISTS idx_equipment_plans_project_id ON equipment_plans(project_id);
CREATE INDEX IF NOT EXISTS idx_equipment_plans_plan_time ON equipment_plans(plan_time);
CREATE INDEX IF NOT EXISTS idx_equipment_plans_deleted_at ON equipment_plans(deleted_at);

CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    sequence_no INTEGER,
    title TEXT NOT NULL,
    authors TEXT,
    label_type TEXT,
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

CREATE TABLE IF NOT EXISTS patents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    sequence_no INTEGER,
    title TEXT NOT NULL,
    inventors TEXT,
    application_no TEXT,
    label_type TEXT,
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

CREATE TABLE IF NOT EXISTS meetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    meeting_date TEXT,
    topic TEXT NOT NULL,
    attendees TEXT,
    progress_path TEXT,
    action_items_path TEXT,
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

CREATE TABLE IF NOT EXISTS project_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    subject_name TEXT,
    metric_name TEXT,
    expected_midterm_metric TEXT,
    expected_final_metric TEXT,
    third_party_test INTEGER NOT NULL DEFAULT 0,
    test_outline_summary TEXT,
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

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL
);

INSERT OR IGNORE INTO app_settings (key, value, updated_at)
VALUES ('schema_version', '1', datetime('now'));

INSERT OR IGNORE INTO schema_migrations (version, name, applied_at)
VALUES (1, 'initial_schema', datetime('now'));
