import os

import streamlit as st

from app_db import (
    add_log,
    add_project,
    add_task,
    create_tables,
    delete_project,
    get_logs_for_task,
    get_project_by_id,
    get_projects,
    get_tasks_by_status,
    update_project,
    update_task,
)
from support import analyze_file_code, find_risks, get_code_from_upload, make_tasks_from_goal

#used AI to cleaan up the scrap i wrote and deleted unnecessary essary comments because they are very useful

statuses = ["pending", "in progress", "completed"]

st.set_page_config(page_title="Nexus AI", layout="wide")

# need the key or the AI stuff won't work
if not os.environ.get("OPENAI_API_KEY"):
    st.title("Nexus AI")
    st.error("OPENAI_API_KEY is missing. Set it first, then run the app again.")
    st.code("export OPENAI_API_KEY='your-api-key-here'\nstreamlit run app.py")
    st.stop()

create_tables()

st.title("Nexus AI")
st.caption("Upload code, make tasks, and check if anything is getting late.")

page = st.sidebar.selectbox("Select Mode", ["Code Analysis", "Project Management"])


if page == "Code Analysis":
    st.subheader("Code Analysis")
    st.write("Upload a .py, .txt, or .zip file.")

    file = st.file_uploader("Upload Code", type=["py", "txt", "zip"])

    if file is not None:
        if st.button("Analyze"):
            code, msg = get_code_from_upload(file)
            if msg != "":
                st.error(msg)
            else:
                with st.spinner("Asking OpenAI..."):
                    answer, err = analyze_file_code(code)

                if err:
                    st.error(err)
                else:
                    st.subheader("Code Analysis")
                    st.code(answer)
                    st.download_button(
                        "Download Analysis",
                        answer,
                        file_name="code_analysis.txt",
                        mime="text/plain",
                    )


if page == "Project Management":
    st.subheader("Project Management")

    tab1, tab2 = st.tabs(["Create Project", "View Projects"])

    with tab1:
        name = st.text_input("Project Name")
        desc = st.text_area("Project Description")

        if st.button("Create Project"):
            if name.strip() == "":
                st.error("Please add a project name.")
            else:
                new_id = add_project(name.strip(), desc.strip())
                st.success("Project created with id " + str(new_id) + ".")

    with tab2:
        projects = get_projects()

        if len(projects) == 0:
            st.info("No projects yet.")
        else:
            # making the select box options
            choices = {}
            for x in projects:
                label = x["name"] + " #" + str(x["id"])
                choices[label] = x["id"]

            picked = st.selectbox("Select a Project", list(choices.keys()))
            project_id = choices[picked]
            project = get_project_by_id(project_id)

            st.markdown("### " + project["name"])
            if project["description"]:
                st.write(project["description"])
            else:
                st.write("No description yet.")
            st.caption("Created: " + project["created_at"] + " | Updated: " + project["updated_at"])

            with st.expander("Edit project"):
                name2 = st.text_input("Name", value=project["name"])
                desc2 = st.text_area("Description", value=project["description"] or "")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Save project"):
                        update_project(project_id, name2, desc2)
                        st.success("Saved project.")
                        st.rerun()
                with c2:
                    if st.button("Delete project"):
                        delete_project(project_id)
                        st.success("Deleted project.")
                        st.rerun()

            st.markdown("### Add Task")
            with st.form("task-form"):
                title = st.text_input("Task title")
                details = st.text_area("Task details")
                status = st.selectbox("Task status", statuses)
                due = st.text_input("Due date (YYYY-MM-DD)")
                go = st.form_submit_button("Add Task")

                if go:
                    if title.strip() == "":
                        st.error("Please add a task title.")
                    else:
                        task_id = add_task(project_id, title.strip(), details.strip(), status, due.strip() or None)
                        add_log(task_id, "Task was added by hand.")
                        st.success("Added task.")
                        st.rerun()

            st.markdown("### AI Task Decomposition")
            goal = st.text_area("Goal text", value=project["description"] or "", key="goalbox")
            if st.button("Generate subtasks with AI"):
                if goal.strip() == "":
                    st.error("Please type a goal first.")
                else:
                    with st.spinner("Making tasks..."):
                        tasks, err = make_tasks_from_goal(goal)

                    if err:
                        st.error(err)
                    elif not tasks:
                        st.warning("The AI did not make any tasks.")
                    else:
                        count = 0
                        for task in tasks:
                            task_id = add_task(
                                project_id,
                                task["title"],
                                task.get("details", ""),
                                "pending",
                                task.get("due_date") or None,
                            )
                            add_log(task_id, "AI created this task from the project goal.")
                            count = count + 1
                        st.success("Added " + str(count) + " AI tasks.")
                        st.rerun()

            project = get_project_by_id(project_id)

            st.markdown("### Risk Check")
            risks = find_risks(project["tasks"])
            if len(risks) == 0:
                st.success("No deadline risks found right now.")
            else:
                for x in risks:
                    if x["level"] == "High":
                        st.error(x["message"])
                    else:
                        st.warning(x["message"])

            st.markdown("### Kanban")
            piles = get_tasks_by_status(project_id)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("#### To Do")
                for task in piles["pending"]:
                    st.markdown("**" + task["title"] + "**")
                    if task["details"]:
                        st.write(task["details"])
                    if task["due_date"]:
                        st.caption("Due: " + task["due_date"])
                    else:
                        st.caption("Due: No due date")

                    if st.button("Doing", key="doing-" + str(task["id"])):
                        update_task(task["id"], status="in progress")
                        add_log(task["id"], "Moved to Doing.")
                        st.rerun()
                    if st.button("Done", key="done-" + str(task["id"])):
                        update_task(task["id"], status="completed")
                        add_log(task["id"], "Moved to Done.")
                        st.rerun()

                    with st.expander("Edit " + task["title"]):
                        t = st.text_input("Title", value=task["title"], key="title-" + str(task["id"]))
                        d = st.text_area("Details", value=task["details"] or "", key="details-" + str(task["id"]))
                        dd = st.text_input("Due date (YYYY-MM-DD)", value=task["due_date"] or "", key="due-" + str(task["id"]))
                        s = st.selectbox("Status", statuses, index=0, key="status-" + str(task["id"]))
                        if st.button("Save task", key="save-" + str(task["id"])):
                            update_task(task["id"], t, d, s, dd)
                            add_log(task["id"], "Task was updated.")
                            st.rerun()
                        logs = get_logs_for_task(task["id"])
                        for log in logs:
                            st.caption(log["created_at"] + " - " + log["message"])
                    st.markdown("---")

            with col2:
                st.markdown("#### Doing")
                for task in piles["in progress"]:
                    st.markdown("**" + task["title"] + "**")
                    if task["details"]:
                        st.write(task["details"])
                    if task["due_date"]:
                        st.caption("Due: " + task["due_date"])
                    else:
                        st.caption("Due: No due date")

                    if st.button("To Do", key="todo-" + str(task["id"])):
                        update_task(task["id"], status="pending")
                        add_log(task["id"], "Moved to To Do.")
                        st.rerun()
                    if st.button("Done", key="done2-" + str(task["id"])):
                        update_task(task["id"], status="completed")
                        add_log(task["id"], "Moved to Done.")
                        st.rerun()

                    with st.expander("Edit " + task["title"]):
                        t = st.text_input("Title", value=task["title"], key="title2-" + str(task["id"]))
                        d = st.text_area("Details", value=task["details"] or "", key="details2-" + str(task["id"]))
                        dd = st.text_input("Due date (YYYY-MM-DD)", value=task["due_date"] or "", key="due2-" + str(task["id"]))
                        s = st.selectbox("Status", statuses, index=1, key="status2-" + str(task["id"]))
                        if st.button("Save task", key="save2-" + str(task["id"])):
                            update_task(task["id"], t, d, s, dd)
                            add_log(task["id"], "Task was updated.")
                            st.rerun()
                        logs = get_logs_for_task(task["id"])
                        for log in logs:
                            st.caption(log["created_at"] + " - " + log["message"])
                    st.markdown("---")

            with col3:
                st.markdown("#### Done")
                for task in piles["completed"]:
                    st.markdown("**" + task["title"] + "**")
                    if task["details"]:
                        st.write(task["details"])
                    if task["due_date"]:
                        st.caption("Due: " + task["due_date"])
                    else:
                        st.caption("Due: No due date")

                    if st.button("To Do", key="todo3-" + str(task["id"])):
                        update_task(task["id"], status="pending")
                        add_log(task["id"], "Moved to To Do.")
                        st.rerun()
                    if st.button("Doing", key="doing3-" + str(task["id"])):
                        update_task(task["id"], status="in progress")
                        add_log(task["id"], "Moved to Doing.")
                        st.rerun()

                    with st.expander("Edit " + task["title"]):
                        t = st.text_input("Title", value=task["title"], key="title3-" + str(task["id"]))
                        d = st.text_area("Details", value=task["details"] or "", key="details3-" + str(task["id"]))
                        dd = st.text_input("Due date (YYYY-MM-DD)", value=task["due_date"] or "", key="due3-" + str(task["id"]))
                        s = st.selectbox("Status", statuses, index=2, key="status3-" + str(task["id"]))
                        if st.button("Save task", key="save3-" + str(task["id"])):
                            update_task(task["id"], t, d, s, dd)
                            add_log(task["id"], "Task was updated.")
                            st.rerun()
                        logs = get_logs_for_task(task["id"])
                        for log in logs:
                            st.caption(log["created_at"] + " - " + log["message"])
                    st.markdown("---")
