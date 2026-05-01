# Nexus AI

A project manager that never sleeps. You give it a high‑level goal, and it breaks it down, tracks progress, and alerts you to roadblocks.

## What it does

- Code Analysis — upload a .py, .txt, or .zip file and get an AI‑powered summary of risks and suggestions
- Project Management — create projects, add tasks manually, or let AI decompose a goal into 4–7 subtasks automatically
- Kanban board — move tasks between To Do / Doing / Done with one click
- Risk checker — flags tasks that are overdue or due within 3 days so nothing sneaks up on you
- Activity log — every task change is recorded with a timestamp


## AI Declaration

Nexus AI is mostly human‑built. All the core logic - the database schema, Kanban board, file upload pipeline, risk checker, all the weird edge cases ; was written by hand over about six days. If you look at the commit history, you can literally see the real debugging process happening in real time.

Once everything finally worked, I ran a quick AI cleanup pass to remove the messy comments and fix formatting. Trust me, without that cleanup, only God knew how half of it worked, first I knew, then slowly only God knew, so cleaning it up was kinda necessary if anyone else was ever going to use it.

GitHub Copilot only suggested a couple of boring refactor commit messages.
