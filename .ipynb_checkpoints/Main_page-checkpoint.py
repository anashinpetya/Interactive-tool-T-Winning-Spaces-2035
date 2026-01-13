import streamlit as st
from navigation import load_sidebar

# --- Page setup (should be the first Streamlit command) ---
st.set_page_config(
    page_title="Interactive tool",
    layout="wide",
)

# --- Sidebar ---
load_sidebar()   # custom menu; make sure load_sidebar() does NOT call st.set_page_config

# --- Title ---
st.title("Interactive tool")

#st.markdown("<div style='height:2px;'></div>", unsafe_allow_html=True)

# --- Intro Text ---
st.markdown("""
This interactive tool allows you to explore potential environmental and health impacts of different remote working scenarios in the Helsinki capital region.

The tool allows comparing emissions, travel patterns, and health impacts relative to three main scenarios: **S1 - No remote working; S2 - Current remote working; and S3 - Full remote working potential**. Additionally, by changing the percentage of the remote working population through the interactive sliders, approximations of the effects are shown for the chosen level of remote working by interpolating results from these base scenarios.

The **T-Winning Spaces 2035** project aims to point towards winning spatial solutions for future work, enabling the double twin transition of digital/green and virtual/physical transforming our societies by 2035. Within this remit, this tool allows interactive visualization of the results from Work Package 3, whose goal was to understand the health impacts associated with digital work futures, and quantify the possible changes to GHG emissions.  
More information: https://t-winning-spaces2035.com/

The tool was developed by members of **the Urban Physics Research Group at Tampere University: Petr Anashin, Alonso Espinosa Mireles de Villafranca**, and the group head, **Jonathon Taylor**.

*T-Winning Spaces 2035 is a project funded by the Research Council of Finland and has received funding from the European Union NextGenerationEU programme.*
""")

# --- Empty line / vertical space under the text ---
st.markdown("<div style='height:2px;'></div>", unsafe_allow_html=True)

# --- Image Layout ---
# Columns: [left margin, logo1, middle space, logo2, right margin]
col_empty1, col_img1, col_empty2, col_img2, col_empty3 = st.columns(
    [0.175, 0.35, 0.05, 0.25, 0.175]
)

with col_img1:
    # small padding above first logo
    st.markdown("<div style='padding-top:19px;'>", unsafe_allow_html=True)
    st.image("logo1.png", width='stretch')
    st.markdown("</div>", unsafe_allow_html=True)

with col_img2:
    # adjust padding-top here if you want this logo lower/higher
    #st.markdown("<div style='padding-bottom:10px;'>", unsafe_allow_html=True)
    st.image("logo2.png", width='stretch')
    #st.markdown("</div>", unsafe_allow_html=True)
