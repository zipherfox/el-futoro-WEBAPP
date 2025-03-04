import streamlit as st
# --- Footer (static, outside of navigation) ---
def show_footer():
    st.markdown("---")
    st.write("Created with 🖤 by Zipherfox and friends")

# --- Main App Structure ---
st.set_page_config(layout="wide")  # Set layout for the entire app

# Create a container for the main content (pages)
main_container = st.container()
with main_container:
    nav = st.navigation([
        st.Page("Page/1_Calculator.py"),
        st.Page("Page/2_AI.py")
        ])
    nav.run()
show_footer()  # Display the footer outside of the navigation