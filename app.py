import streamlit as st
from support import *

st.title("Nexus AI")
#upload box
code = st.file_uploader("Upload Code")
if code is not None:
    if st.button("Analyze"):
        code = extract_code(code)
        explanation = analyze_file_code(code)
        st.download_button(
            label="Download Explanation",
            data=explanation,
            file_name="code_analysis.txt",
            mime="text/plain"
        )
        st.subheader("Code Analysis:")
        st.code(explanation)
        
