# We will be storing the data in sqlite and In the file named 'app.db'

#Define the SQLite schema with three linked tables: projects, tasks (belongs to projects), and logs(belongs to tasks).
import sqlite3  

conn = sqlite3.connect('app.db')


def create_tables(conn):
    cur = conn.cursor()

    cur.execute("PRAGMA foreign_keys = ON;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            details TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        );
    """)

    conn.commit()

# to add a project into a db, we need name, description, tasks, and logs(is optional) 
# i guess the is goood enough for now, I will test it out later, I will go call into app.py now anyways
def add_project(conn, name, description, tasks):
    cur = conn.cursor()
    cur.execute("INSERT INTO projects (name, description) VALUES (?, ?)", (name, description))
    project_id = cur.lastrowid

    for task in tasks:
        title = task['title']
        details = task.get('details', '')
        status = task.get('status', 'pending')
        cur.execute("INSERT INTO tasks (project_id, title, details, status) VALUES (?, ?, ?, ?)", 
                    (project_id, title, details, status))
        task_id = cur.lastrowid

        logs = task.get('logs', [])
        for log in logs:
            message = log['message']
            cur.execute("INSERT INTO logs (task_id, message) VALUES (?, ?)", (task_id, message))

    conn.commit()
