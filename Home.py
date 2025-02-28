import streamlit as st

st.title("Home")
nav = st.navigation([
    st.Page("Page/1_Calculator.py"),
    st.Page("Page/2_AI.py")
    ])
nav.run()