# Nexus AI

A project manager that never sleeps. You give it a high-level goal, and it breaks it down, tracks progress, and alerts you to roadblocks.

## What it does

- **Code Analysis** — upload a `.py`, `.txt`, or `.zip` file and get an AI-powered summary of risks and suggestions
- **Project Management** — create projects, add tasks by hand, or let AI decompose a goal into 4–7 subtasks automatically
- **Kanban board** — move tasks between To Do / Doing / Done with one click
- **Risk checker** — flags tasks that are overdue or due within 3 days so nothing sneaks up on you
- **Activity log** — every task change is recorded with a timestamp

## How to run

```bash
export OPENAI_API_KEY='your-key-here'
pip install -r requirements.txt
streamlit run app.py
```

Requires Python 3.9+ and an OpenAI API key.

## Stack

- [Streamlit](https://streamlit.io/) — UI
- [OpenAI API](https://platform.openai.com/) (gpt-4o) — code analysis and task generation
- SQLite — local storage for projects, tasks, and logs

---

## AI Declaration

This project was **mostly human built**.

All 78 commits were written by hand over 6 days (Apr 26 – May 1, 2026). The debugging process, architecture decisions, database schema, and UI layout were all figured out manually — you can see the real struggle in commit messages like *"IDK, why edit feature is not working so.."* and *"Should work and it took me a lot ti me to thios"*.

AI was used in two minor ways:
1. **GitHub Copilot** occasionally suggested commit message wording (e.g. the cleaner imperative-style ones like "Refactor SQLite database connection and schema setup") — these were accepted as-is for mundane refactors.
2. **A single final cleanup pass** — once the app was fully working, the messy working code was fed to an AI to remove unnecessary comments and tidy formatting (noted in the code: `#used AI to cleaan up the scrap i wrote`).

The OpenAI API is used as a **feature of the app** (code analysis, task generation) — not to write the app itself.