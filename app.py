import streamlit as st
from support import *
import os
from app_db import create_tables, add_project, get_projects, get_project_by_id

# fix the edit project and edit task tonigh please i beg you, please please

# check if there is API key in environment variable if not ask user to go set it up
if "OPENAI_API_KEY" not in os.environ:
    st.warning("Please set up your OpenAI API key in the environment variable OPENAI_API_KEY to use this app.")
    st.stop()

# now that openai exists, lets set up db if not exists
create_tables()

st.title("Nexus AI")
st.caption("Nexus AI only .py, .txt, and .zip")


mode = st.sidebar.selectbox("Select Mode", ["Choose a mode","Code Analysis", "Project Management"])

if mode == "Code Analysis":    
    #upload box
    st.write("If you want to analyze projects that are with multiple files, please zip the project and upload the zip file.")
    code = st.file_uploader("Upload Code", type=["py", "txt", "zip"])
    if code is not None:
        if st.button("Analyze"):
            filename = (getattr(code, "name", "") or "").lower()
            if filename.endswith(".zip"):
                extracted_code = extract_zip(code)
            else:
                extracted_code = extract_code(code)

            explanation = analyze_file_code(extracted_code)
            st.download_button(
                label="Download Explanation",
                data=explanation,
                file_name="code_analysis.txt",
                mime="text/plain"
            )
            st.subheader("Code Analysis:")
            st.code(explanation)

if mode == "Project Management":
    # we can make so it asks if the project is new or already created so this wont happen and is kinda cool ig
    st.write("This feature is coming soon. Stay tuned! Placeholder for now even thouhg there is stuff.")
    mode = st.selectbox("Select Project Mode", ["Choose a mode", "Create a New Project", "View Existing Projects"])
    
    
    if mode == 'Create a New Project':
        st.subheader("Create a New Project")
        project_name = st.text_input("Project Name*")
        project_description = st.text_area("Project Description*")
        # lets take in the project files and i have no idea how to save it but should be zip file as I have zip file extraction ready and can just save it in the db as blob or something, but for now lets just take in the tasks as text input and then later on we can add the file upload and make it look nice, but for now this is good enough to get the flow right and then we can improve it later on, also this way we can have a better flow for adding tasks to existing projects which is good for the ux, so for now just do text input for tasks and then later on we can add the file upload and make it look nice, but for now lets just take it in and do nothin
        files = st.file_uploader("Upload Project Files (optional, .zip format recommended)", type=["zip"])
        # add a uploadfile button
        if st.button("Upload Files"):
            # call support.extract_zip
            with st.spinner("Uploading and extracting files..."):
                if files is not None:
                    file_name = getattr(files, "name", "").lower()
                    if file := extract_code(files):
                        pass  # Add any specific handling if needed
                    elif file_name.endswith(".zip"):
                        extracted_code = extract_zip(files)
                        st.success("Files uploaded and extracted successfully!")
                        # just for debugging
                        st.code(extracted_code)
                    else:
                        st.error("Please upload a .zip file for project files.")
            # do nothing

        #tasks_input = st.text_area("Tasks (one per line, format(please follow for now): title|details|status)")
        if st.button("Create Project"):
            if project_name and project_description:
                #tasks = []
                #for line in tasks_input.splitlines():
                #    parts = line.split("|")
                 #   if len(parts) >= 2:
                  #      task = {
                   #         "title": parts[0].strip(),
                    #        "details": parts[1].strip(),
                     #       "status": parts[2].strip() if len(parts) > 2 else "pending"
                      #  }
                       # tasks.append(task)
                add_project(project_name, project_description)
                st.success("Project created successfully!")
            else:
                st.error("Please provide a project name and at least one task.")
    
    if mode == 'View Existing Projects':
        # now lets go retrive the projects ft67
        # adding tasks will take place here instead of Project creation, so we can have a better flow, and also be able to edit projects and add tasks to them later on, which is good for the ux.
        projects_for_selectbox = get_projects()
        project_dict = {f"{proj[1]}" : proj[0] for proj in projects_for_selectbox}
        selected_project = st.selectbox("Select a Project", options=project_dict.keys())
        if selected_project:
            project_id = project_dict[selected_project]
            project = get_project_by_id(project_id)
            if project:
                left, right, corner = st.columns([3, 2, 2])
                with left:
                    st.subheader("Project Details")
                with right:
                    if st.button("Edit🛠️"):
                        edit_project_dialog(project)
                        #st.rerun() i am dumb to do this, this hsoul dbe done after so iwll put in suppport.py
                with corner:
                    if st.button("Delete Project 🗑 ️"):
                        # this should be easy cause just delete it
                        delete_project_support(project)
                        #st.info("This feature is under development, will be up as soon as possible.")
                st.markdown("---")


                st.write(f"**Name:** {project['name']}")
                st.write(f"**Description:** {project['description']}")
                st.write(f"**Created At:** {project['created_at']}")
                st.write(f"**Updated At:** {project['updated_at']}")
                st.subheader("**Tasks:**")
                # make it look good by adding apcing
                st.markdown("<br>", unsafe_allow_html=True)
                tasks = project["tasks"]
                if tasks:
                    for task in tasks:
                        task_left, task_middle, task_right = st.columns([3, 2, 1])
                        with task_left:
                            st.write(f"**{task[1]}**")
                            if task[2]:
                                st.write(task[2])
                        with task_middle:
                            st.write(task[3])
                        with task_right:
                            if st.button("Edit", key=f"edit-task-{task[0]}"):
                                edit_task_dialog(task)
                else:
                    st.write("No tasks found for this project.")    
                st.markdown("---")      
               
               
                left, right = st.columns([1, 3])
                with left:
                    #st.markdown("<br>", unsafe_allow_html=True)
                    st.write("**Add a new task:**")
                with right:
                    #st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Add +"):
                        add_task_dialog(project['id'])

                    
                  
                



                ## now that db is set and sent some projects into it shoudl be able to retrieve and view them here, next up is to make it
