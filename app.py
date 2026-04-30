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
        project_name = st.text_input("Project Name")
        project_description = st.text_area("Project Description")
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
                left, right, corner = st.columns([1, 1, 3])
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
                tasks =get_task_by_id(project['id'])
                try:    
                    st.write(tasks)
                except Exception as e:
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
