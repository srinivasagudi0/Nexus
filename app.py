import streamlit as st
from support import *
import os
from app_db import conn, create_tables

# check if there is API key in environment variable if not ask user to go set it up
if "OPENAI_API_KEY" not in os.environ:
    st.warning("Please set up your OpenAI API key in the environment variable OPENAI_API_KEY to use this app.")
    st.stop()

# now that openai exists, lets set up db if not exists
create_tables(conn)

st.title("Nexus AI")
st.caption("Nexus AI only .py, .txt, and .zip")
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
