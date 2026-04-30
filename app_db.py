# We will be storing the data in sqlite and In the file named 'app.db'

#Define the SQLite schema with three linked tables: projects, tasks (belongs to projects), and logs(belongs to tasks).
import sqlite3  
import streamlit as st

@st.cache_resource
def get_db_connection():
    """Create a database connection that can be used across all threads"""
    conn = sqlite3.connect('app.db', check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    # added it in get_db_connection

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
def add_project(name, description):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO projects (name, description) VALUES (?, ?)", (name, description))
    project_id = cur.lastrowid

    #for task in tasks:
     #   title = task['title']
      #  details = task.get('details', '')
       # status = task.get('status', 'pending')

        #cur.execute("INSERT INTO tasks (project_id, title, details, status) VALUES (?, ?, ?, ?)", 
         #           (project_id, title, details, status))
        #task_id = cur.lastrowid

        #logs = task.get('logs', [])
        #for log in logs:
         #   message = log['message']
          #  cur.execute("INSERT INTO logs (task_id, message) VALUES (?, ?)", (task_id, message))

    conn.commit()

#retrieval
def get_projects():
    """Retrieve all projects from the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, description, created_at, updated_at FROM projects")
    projects = cur.fetchall()
    return projects

def get_project_by_id(project_id):
    """Retrieve a specific project by ID with all its tasks"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get project details
    cur.execute("SELECT id, name, description, created_at, updated_at FROM projects WHERE id = ?", (project_id,))
    project = cur.fetchone()
    
    if not project:
        return None
    
    # Get tasks for this project
    cur.execute("SELECT id, title, details, status, created_at, updated_at FROM tasks WHERE project_id = ?", (project_id,))
    tasks = cur.fetchall()
    return {
        "id": project[0],
        "name": project[1],
        "description": project[2],
        "created_at": project[3],
        "updated_at": project[4],
        "tasks": tasks
    }


def update_task(task_id, title=None, details=None, status=None):
    """Update a task's title, details, or status"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if details is not None:
        updates.append("details = ?")
        params.append(details)
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    
    if not updates:
        return  # Nothing to update
    
    params.append(task_id)
    query = f"UPDATE tasks SET {', '.join(updates)}, updated_at = datetime('now') WHERE id = ?"
    cur.execute(query, params)
    cur.execute("UPDATE projects SET updated_at = datetime('now') WHERE id = (SELECT project_id FROM tasks WHERE id = ?)", (task_id,))
    conn.commit()
    # forgot which one to close so closed both
    # i shouldnt have to close the connection here because it is cached and shared across threads, closing it would cause issues when other parts of the app try to use it later, so I will just close the cursor and leave the connection open for reuse.    

def update_project(project_id, name=None, description=None):
    """Update a project's name or description"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    updates = []
    params = []
    
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    
    if not updates:
        return  # Nothing to update
    
    params.append(project_id)
    query = f"UPDATE projects SET {', '.join(updates)}, updated_at = datetime('now') WHERE id = ?"
    cur.execute(query, params)
    conn.commit()
    # i shouldnt have to close the connection here because it is cached and shared across threads, closing it would cause issues when other parts of the app try to use it later, so I will just close the cursor and leave the connection open for reuse.    

## now delete delete a project and all its associated tasks and logs
def delete_project(project_id): 
    # this will obivously add projects to the db 😅
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM logs WHERE task_id IN (SELECT id FROM tasks WHERE project_id = ?)", (project_id,))
    cur.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
    cur.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    import streamlit as st
    st.rerun()
# I will not close the connection like I did last time.

def add_task(project_id, title, details="", status="pending"):
    """Add a new task to a project"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (project_id, title, details, status) VALUES (?, ?, ?, ?)", 
                (project_id, title, details, status))
    task_id = cur.lastrowid
    cur.execute("UPDATE projects SET updated_at = datetime('now') WHERE id = ?", (project_id,))
    conn.commit()
    return task_id

def get_task_by_id(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, details, status, created_at, updated_at FROM tasks WHERE id = ?", (task_id,))
    task = cur.fetchone()
    if task:
        return {
            "id": task[0],
            "title": task[1],
            "details": task[2],
            "status": task[3],
            "created_at": task[4],
            "updated_at": task[5]
        }
    return None
