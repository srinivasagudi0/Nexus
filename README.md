# Nexus
A project manager that never sleeps. You give it a high-level goal, and it breaks it down, tracks progress, and alerts you to roadblocks.


# What I am trying to acheive

"Nexus" — The Autonomous Project Manager
Imagine a project manager that never sleeps. You give it a high-level goal, and it breaks it down, tracks progress, and alerts you to roadblocks.

The "Cool" Factor: It feels like a living entity. You tell it "I want to launch a website," and it populates a Kanban board for you automatically.

The AI Call: * Task Decomposition: AI takes a goal and returns a JSON list of sub-tasks.

Risk Analysis: AI looks at your current tasks in SQLite and predicts which ones will be late.

The SQLite Role: A complex relational schema: Projects -> Tasks -> Logs.

The Streamlit UI: Use the streamlit-kanban component to visualize the tasks stored in your SQLite database.
