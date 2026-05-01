import sqlite3


DB_NAME = "app.db"
STATUSES = ["pending", "in progress", "completed"]


def get_db_connection(db_path=DB_NAME):
    db = sqlite3.connect(db_path, check_same_thread=False)
    db.execute("PRAGMA foreign_keys = ON")
    db.row_factory = sqlite3.Row
    return db


def create_tables(db_path=DB_NAME):
    db = get_db_connection(db_path)
    cur = db.cursor()

    # making the three tables the app needs
    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        details TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        due_date TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
    )
    """)

    migrate_tables(db)
    db.commit()
    db.close()


def migrate_tables(db):
    cur = db.cursor()
    cur.execute("PRAGMA table_info(tasks)")
    rows = cur.fetchall()
    found_it = False
    for x in rows:
        if x["name"] == "due_date":
            found_it = True
    if not found_it:
        cur.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")


def add_project(name, description="", db_path=DB_NAME):
    db = get_db_connection(db_path)
    cur = db.cursor()
    cur.execute("INSERT INTO projects (name, description) VALUES (?, ?)", (name, description))
    num = cur.lastrowid
    db.commit()
    db.close()
    return num


def get_projects(db_path=DB_NAME):
    db = get_db_connection(db_path)
    cur = db.cursor()
    cur.execute("SELECT id, name, description, created_at, updated_at FROM projects ORDER BY updated_at DESC")
    rows = cur.fetchall()
    stuff = []
    for row in rows:
        stuff.append(dict(row))
    db.close()
    return stuff


def get_project_by_id(project_id, db_path=DB_NAME):
    db = get_db_connection(db_path)
    cur = db.cursor()

    cur.execute("SELECT id, name, description, created_at, updated_at FROM projects WHERE id = ?", (project_id,))
    row = cur.fetchone()
    if row is None:
        db.close()
        return None

    project = dict(row)

    cur.execute("""
    SELECT id, project_id, title, details, status, due_date, created_at, updated_at
    FROM tasks
    WHERE project_id = ?
    ORDER BY id
    """, (project_id,))
    rows = cur.fetchall()
    tasks = []
    for x in rows:
        tasks.append(dict(x))

    project["tasks"] = tasks
    db.close()
    return project


def update_project(project_id, name=None, description=None, db_path=DB_NAME):
    db = get_db_connection(db_path)
    cur = db.cursor()

    if name is not None and description is not None:
        cur.execute(
            "UPDATE projects SET name = ?, description = ?, updated_at = datetime('now') WHERE id = ?",
            (name, description, project_id),
        )
    elif name is not None:
        cur.execute(
            "UPDATE projects SET name = ?, updated_at = datetime('now') WHERE id = ?",
            (name, project_id),
        )
    elif description is not None:
        cur.execute(
            "UPDATE projects SET description = ?, updated_at = datetime('now') WHERE id = ?",
            (description, project_id),
        )

    db.commit()
    db.close()


def delete_project(project_id, db_path=DB_NAME):
    db = get_db_connection(db_path)
    cur = db.cursor()
    cur.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    db.commit()
    db.close()


def add_task(project_id, title, details="", status="pending", due_date=None, db_path=DB_NAME):
    if status not in STATUSES:
        status = "pending"

    db = get_db_connection(db_path)
    cur = db.cursor()
    cur.execute("""
    INSERT INTO tasks (project_id, title, details, status, due_date)
    VALUES (?, ?, ?, ?, ?)
    """, (project_id, title, details, status, due_date))
    num = cur.lastrowid
    cur.execute("UPDATE projects SET updated_at = datetime('now') WHERE id = ?", (project_id,))
    db.commit()
    db.close()
    return num


def update_task(task_id, title=None, details=None, status=None, due_date=None, db_path=DB_NAME):
    if status is not None and status not in STATUSES:
        status = "pending"

    db = get_db_connection(db_path)
    cur = db.cursor()

    if title is not None:
        cur.execute("UPDATE tasks SET title = ?, updated_at = datetime('now') WHERE id = ?", (title, task_id))
    if details is not None:
        cur.execute("UPDATE tasks SET details = ?, updated_at = datetime('now') WHERE id = ?", (details, task_id))
    if status is not None:
        cur.execute("UPDATE tasks SET status = ?, updated_at = datetime('now') WHERE id = ?", (status, task_id))
    if due_date is not None:
        if due_date == "":
            due_date = None
        cur.execute("UPDATE tasks SET due_date = ?, updated_at = datetime('now') WHERE id = ?", (due_date, task_id))

    cur.execute(
        "UPDATE projects SET updated_at = datetime('now') WHERE id = (SELECT project_id FROM tasks WHERE id = ?)",
        (task_id,),
    )
    db.commit()
    db.close()


def get_task_by_id(task_id, db_path=DB_NAME):
    db = get_db_connection(db_path)
    cur = db.cursor()
    cur.execute("""
    SELECT id, project_id, title, details, status, due_date, created_at, updated_at
    FROM tasks
    WHERE id = ?
    """, (task_id,))
    row = cur.fetchone()
    db.close()
    if row is None:
        return None
    return dict(row)


def get_tasks_by_status(project_id, db_path=DB_NAME):
    # put tasks into the right pile
    project = get_project_by_id(project_id, db_path)
    piles = {"pending": [], "in progress": [], "completed": []}
    if project is None:
        return piles

    for task in project["tasks"]:
        status = task["status"]
        if status not in piles:
            status = "pending"
        piles[status].append(task)
    return piles


def add_log(task_id, message, db_path=DB_NAME):
    db = get_db_connection(db_path)
    cur = db.cursor()
    cur.execute("INSERT INTO logs (task_id, message) VALUES (?, ?)", (task_id, message))
    num = cur.lastrowid
    db.commit()
    db.close()
    return num


def get_logs_for_task(task_id, db_path=DB_NAME):
    db = get_db_connection(db_path)
    cur = db.cursor()
    cur.execute("SELECT id, task_id, message, created_at FROM logs WHERE task_id = ? ORDER BY id", (task_id,))
    rows = cur.fetchall()
    stuff = []
    for row in rows:
        stuff.append(dict(row))
    db.close()
    return stuff
