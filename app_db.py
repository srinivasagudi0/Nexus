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
    conn.close()
