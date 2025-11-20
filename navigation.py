# navigation.py
import streamlit as st

def load_sidebar():
    # Hide default Streamlit multipage navigation
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] div[data-testid="stSidebarNav"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ⭐ Main page button
    st.sidebar.markdown("### Home")
    st.sidebar.page_link("Main_page.py", label="About the interactive tool")
    # Your custom grouped navigation
    
    st.sidebar.markdown("### Grid maps")
    st.sidebar.page_link("pages/Emissions comparison.py", label="Emissions comparison")
    st.sidebar.page_link("pages/Remote workers comparison.py", label="Remote workers comparison")
    st.sidebar.page_link("pages/On-site workers comparison.py", label="On-site workers comparison")

    st.sidebar.markdown("### Traffic changes")
    st.sidebar.page_link("pages/Car passengers comparison.py", label="Car passengers comparison")
    st.sidebar.page_link("pages/Transit passengers comparison.py", label="Transit passengers comparison")

    st.sidebar.markdown("### Bar plots")
    st.sidebar.page_link("pages/Emission changes.py", label="Emission changes")
    st.sidebar.page_link("pages/Health impact assessment.py", label="Health impact assessment")
