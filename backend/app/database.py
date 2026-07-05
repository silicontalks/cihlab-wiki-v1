import sqlite3
from pathlib import Path
from typing import Iterator


SCHEMA_PATH = Path(__file__).parent / "db" / "schema.sql"


def initialize_database(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        ensure_auth_tables(connection)
        ensure_project_columns(connection)
        ensure_people_table(connection)
        ensure_publication_columns(connection)
        ensure_meeting_columns(connection)
        ensure_test_columns(connection)
        ensure_progress_tasks_table(connection)
        ensure_equipment_plans_table(connection)


def ensure_project_columns(connection: sqlite3.Connection) -> None:
    columns = {row[1] for row in connection.execute("PRAGMA table_info(projects)").fetchall()}
    migrations = {
        "created_by": "ALTER TABLE projects ADD COLUMN created_by TEXT NOT NULL DEFAULT 'admin'",
        "finance_owner": "ALTER TABLE projects ADD COLUMN finance_owner TEXT",
        "technical_contact": "ALTER TABLE projects ADD COLUMN technical_contact TEXT",
        "paper_target_count": "ALTER TABLE projects ADD COLUMN paper_target_count INTEGER NOT NULL DEFAULT 0",
        "patent_target_count": "ALTER TABLE projects ADD COLUMN patent_target_count INTEGER NOT NULL DEFAULT 0",
    }
    for column, statement in migrations.items():
        _add_column_if_missing(connection, "projects", columns, column, statement)
    connection.execute("CREATE INDEX IF NOT EXISTS idx_projects_created_by ON projects(created_by)")
    connection.commit()


def ensure_auth_tables(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS app_users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            display_name TEXT,
            is_admin INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            deleted_at TEXT
        )
        """
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_app_users_deleted_at ON app_users(deleted_at)")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS project_access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            project_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(username, project_id),
            FOREIGN KEY (username) REFERENCES app_users(username),
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        """
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_project_access_username ON project_access(username)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_project_access_project_id ON project_access(project_id)")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS user_sessions (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES app_users(username)
        )
        """
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_username ON user_sessions(username)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at)")
    connection.execute(
        """
        INSERT OR IGNORE INTO app_users (username, password, display_name, is_admin, created_at, updated_at)
        VALUES ('admin', 'admin', '管理员', 1, datetime('now'), datetime('now'))
        """
    )
    connection.commit()


def ensure_people_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
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
        )
        """
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_project_people_project_id ON project_people(project_id)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_project_people_sequence_no ON project_people(sequence_no)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_project_people_deleted_at ON project_people(deleted_at)")
    connection.commit()


def ensure_publication_columns(connection: sqlite3.Connection) -> None:
    paper_columns = {row[1] for row in connection.execute("PRAGMA table_info(papers)").fetchall()}
    paper_migrations = {
        "sequence_no": "ALTER TABLE papers ADD COLUMN sequence_no INTEGER",
        "label_type": "ALTER TABLE papers ADD COLUMN label_type TEXT",
    }
    for column, statement in paper_migrations.items():
        _add_column_if_missing(connection, "papers", paper_columns, column, statement)

    patent_columns = {row[1] for row in connection.execute("PRAGMA table_info(patents)").fetchall()}
    patent_migrations = {
        "sequence_no": "ALTER TABLE patents ADD COLUMN sequence_no INTEGER",
        "label_type": "ALTER TABLE patents ADD COLUMN label_type TEXT",
    }
    for column, statement in patent_migrations.items():
        _add_column_if_missing(connection, "patents", patent_columns, column, statement)
    connection.commit()


def ensure_meeting_columns(connection: sqlite3.Connection) -> None:
    columns = {row[1] for row in connection.execute("PRAGMA table_info(meetings)").fetchall()}
    migrations = {
        "progress_path": "ALTER TABLE meetings ADD COLUMN progress_path TEXT",
        "action_items_path": "ALTER TABLE meetings ADD COLUMN action_items_path TEXT",
    }
    for column, statement in migrations.items():
        _add_column_if_missing(connection, "meetings", columns, column, statement)
    connection.commit()


def ensure_test_columns(connection: sqlite3.Connection) -> None:
    columns = {row[1] for row in connection.execute("PRAGMA table_info(project_tests)").fetchall()}
    migrations = {
        "subject_name": "ALTER TABLE project_tests ADD COLUMN subject_name TEXT",
        "metric_name": "ALTER TABLE project_tests ADD COLUMN metric_name TEXT",
        "expected_midterm_metric": "ALTER TABLE project_tests ADD COLUMN expected_midterm_metric TEXT",
        "expected_final_metric": "ALTER TABLE project_tests ADD COLUMN expected_final_metric TEXT",
        "third_party_test": "ALTER TABLE project_tests ADD COLUMN third_party_test INTEGER NOT NULL DEFAULT 0",
        "test_outline_summary": "ALTER TABLE project_tests ADD COLUMN test_outline_summary TEXT",
    }
    for column, statement in migrations.items():
        _add_column_if_missing(connection, "project_tests", columns, column, statement)
    connection.commit()


def ensure_progress_tasks_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
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
        )
        """
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_project_progress_tasks_project_id ON project_progress_tasks(project_id)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_project_progress_tasks_start_date ON project_progress_tasks(start_date)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_project_progress_tasks_end_date ON project_progress_tasks(end_date)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_project_progress_tasks_deleted_at ON project_progress_tasks(deleted_at)")
    connection.commit()


def ensure_equipment_plans_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
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
        )
        """
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_equipment_plans_project_id ON equipment_plans(project_id)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_equipment_plans_plan_time ON equipment_plans(plan_time)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_equipment_plans_deleted_at ON equipment_plans(deleted_at)")
    connection.commit()


def _add_column_if_missing(
    connection: sqlite3.Connection,
    table: str,
    known_columns: set[str],
    column: str,
    statement: str,
) -> None:
    if column in known_columns:
        return
    latest_columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()}
    if column in latest_columns:
        known_columns.add(column)
        return
    try:
        connection.execute(statement)
        known_columns.add(column)
    except sqlite3.OperationalError as exc:
        if "duplicate column name" not in str(exc).lower():
            raise


def connect(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    ensure_auth_tables(connection)
    ensure_project_columns(connection)
    ensure_people_table(connection)
    ensure_publication_columns(connection)
    ensure_meeting_columns(connection)
    ensure_test_columns(connection)
    ensure_progress_tasks_table(connection)
    ensure_equipment_plans_table(connection)
    return connection


def rows_to_dicts(rows: Iterator[sqlite3.Row]) -> list[dict]:
    return [dict(row) for row in rows]
