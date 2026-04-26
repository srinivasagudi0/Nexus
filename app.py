import streamlit as st

st.title("Nexus AI")
#upload box
code = st.file_uploader("Upload Code")
if code is not None:
    if st.button("Analyze"):
        pass
