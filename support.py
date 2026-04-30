from openai import OpenAI
import os
import streamlit as st
from app_db import update_task, get_project_by_id, update_project



# extract the code from the file
def extract_code(file):
    # Streamlit uploader returns an UploadedFile-like object with a .read() method.
    if hasattr(file, "read"):
        content = file.read()
        if isinstance(content, bytes):
            return content.decode("utf-8", errors="ignore")
        return str(content)

    # Fallback: allow passing a regular file path.
    with open(file, "r", encoding="utf-8") as f:
        return f.read()

def analyze_file_code(code):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior code reviewer. Return analysis in exactly this order:\n"
                    "Summary:\n"
                    "- ...\n\n"
                    "Risks:\n"
                    "- ...\n\n"
                    "Suggestions:\n"
                    "- ...\n\n"
                    "Use short bullet points. If nothing is notable in a section, write '- None'. "
                    "Do not add extra headings."
                ),
            },
            {
                "role": "user",
                "content": f"Analyze the following code:\n\n{code}",
            },
        ],
    )
    return response.choices[0].message.content


# extract zip file and return the code in the zip file as a string
def extract_zip(file):
    import zipfile
    import io

    if hasattr(file, "read"):
        with zipfile.ZipFile(io.BytesIO(file.read())) as z:
            code = ""
            for filename in z.namelist():
                if filename.endswith((".py", ".txt")):
                    with z.open(filename) as f:
                        content = f.read()
                        if isinstance(content, bytes):
                            code += content.decode("utf-8", errors="ignore") + "\n"
                        else:
                            code += str(content) + "\n"
            return code
    else:
        with zipfile.ZipFile(file, "r") as z:
            code = ""
            for filename in z.namelist():
                if filename.endswith((".py", ".txt")):
                    with z.open(filename) as f:
                        content = f.read()
                        if isinstance(content, bytes):
                            code += content.decode("utf-8", errors="ignore") + "\n"
                        else:
                            code += str(content) + "\n"
            return code

@st.dialog("Edit Task")
def edit_task_dialog(task):
    # task is a tuple: (id, title, details, status, created_at, updated_at)
    task_id = task[0]
    task_title = task[1]
    task_details = task[2]
    task_status = task[3]

    new_title = st.text_input("Title", value=task_title)
    new_details = st.text_area("Details", value=task_details)
    new_status = st.selectbox(
        "Status",
        ["pending", "in progress", "completed"],
        index=["pending", "in progress", "completed"].index(task_status),
    )

    if st.button("Save Changes"):
        update_task(task_id, new_title, new_details, new_status)
        st.success("Task updated successfully!")
# this shit doesnt work so lets move on and come back later

@st.dialog("Edit Project")
def edit_project_dialog(project):
    # expecting project is a dict: {'id','name','description','created_at','updated_at', ...}
    project_id = project["id"]
    project_name = project["name"]
    project_description = project["description"]

    new_name = st.text_input("Name", value=project_name)
    new_description = st.text_area("Description", value=project_description)

    if st.button("Save Changes"):
        update_project(project_id, new_name, new_description)
        st.success("Project updated successfully!")
        #import time
        #time.sleep(0.5) # experiment doont know if it works in real work and dont know If i can pass decimals
        # affter time rerun because evetything is cached
        # run directly after the change sdont wait and also will clean this up later
        st.rerun()

@st.dialog("Delete Proeject")
def delete_project_support(project):
    from app_db import delete_project
    st.write(project)  ## for debugging purpose only, forgot to unapotropbhe it
    st.warning("Delete Project")
    if st.button("Confirm"):
        delete_project(project)
    if st.button("Deny"): # forgot what the word is
        st.rerun()
