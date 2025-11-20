import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from navigation import load_sidebar

st.set_page_config(layout="wide")
                   #page_title="Emission changes"

st.markdown("""
<style>
/* Hide text of default Streamlit sidebar menu */
div[data-testid="stSidebarNav"] span,
div[data-testid="stSidebarNav"] a {
    color: transparent !important;      /* hides text */
    visibility: hidden !important;      /* prevents hover showing text */
}

/* Optionally remove spacing to collapse it */
div[data-testid="stSidebarNav"] ul {
    margin: 0 !important;
    padding: 0 !important;
}

</style>
""", unsafe_allow_html=True)

load_sidebar()

st.markdown("""
<style>
.block-container {padding-top: 3rem !important;}
div[data-testid="stButton"] button {
    background-color: #FF4B4B !important; color: white !important; border-radius: 8px !important;
    padding: 0.55em 1.6em !important; border: none !important; font-weight: 800 !important;
    font-size: 26px !important; font-family: "Source Sans Pro", sans-serif !important;
    white-space: nowrap !important; text-align: center !important; display: block !important; margin: 0 auto !important;
}
div[data-testid="stButton"] button:hover { background-color: #ff7373 !important; }
div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div { height: 2px !important; }
div[data-testid="stSlider"] div[data-baseweb="slider"] div[role="slider"] { width: 12px !important; height: 12px !important; }
div[data-testid="stSlider"] div[data-testid="stTickBar"] > div:first-child > div,
div[data-testid="stSlider"] div[data-testid="stTickBar"] > div:last-child > div {
    transform: translateX(-50%) !important; text-align: center !important; display: inline-block !important; width: auto !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h3>Daily CO2 emissions at the remote-working population percentage in S1, selected percentage of remote working population and in S3</h3>", unsafe_allow_html=True)

col_slider, _, _, _ = st.columns([0.35, 0.08, 0.07, 0.5])
with col_slider:
    st.markdown("<p style='font-weight:600; margin-bottom:6px;'>The percentage of remote working population</p>", unsafe_allow_html=True)
    slider_val = st.slider("slider_s3s2", 0.0, 47.3, 24.0, 0.1, format="%.1f", label_visibility="collapsed")

    # --- CUSTOM TICK FOR 24% ---
    tick_position = (24.0 - 0.0) / (47.3 - 0.0) * 100  # convert slider value to % position
    
    st.markdown(f"""
    <style>
    .custom-tick-container {{
        position: relative;
        height: 10px;
        margin-top: -22px;
    }}
    .custom-tick {{
        position: absolute;
        left: {tick_position}%;
        transform: translateX(-50%);
        font-size: 12px;
        color: #444;
        font-weight: 600;
    }}
    .custom-tick-line {{
        width: 1px;
        height: 14px;
        background-color: #444;
        margin: 0 auto;
    }}
    </style>
    
    <div class="custom-tick-container">
        <div class="custom-tick">
            <div class="custom-tick-line"></div>
            Current percentage
        </div>
    </div>
    """, unsafe_allow_html=True)

# Baseline values
s1_emissions = 509.2
s2_emissions = 436.7
s3_emissions = 364.5

# Compute selected value
if slider_val > 24:
    factor = (47.3 - slider_val) / (47.3 - 24.0)
    selected_emissions = round(s2_emissions + ((s3_emissions - s2_emissions) * (1 - factor)), 1)
elif slider_val < 24:
    factor = slider_val / 24.0
    selected_emissions = round(s2_emissions + ((s1_emissions - s2_emissions) * (1 - factor)), 1)
else:
    selected_emissions = s2_emissions

# Build table
emissions_table = pd.DataFrame({
    "Scenario": ["S1", "Selection", "S3"],
    "Emissions": [s1_emissions, selected_emissions, s3_emissions],
})

# Custom colors for each bar
color_map = {
    "S1": "#53ADD9",
    "Selection": "#7DD8D6",
    "S3": "#53ADD9"
}

chart = (
    alt.Chart(emissions_table)
    .mark_bar(size=55)  # smaller size -> more space between bars
    .encode(
        x=alt.X(
            "Scenario:N",
            sort=list(emissions_table["Scenario"]),
            axis=alt.Axis(title="Scenario", labelAngle=0)  # x-axis label + horizontal ticks
        ),
        y=alt.Y(
            "Emissions:Q",
            axis=alt.Axis(title="Daily CO₂ emissions (tonnes)"),
            scale=alt.Scale(domain=[0, 540])
        ),
        color=alt.Color(
            "Scenario:N",
            scale=alt.Scale(
                domain=list(color_map.keys()),
                range=list(color_map.values())
            ),
            legend=None  # optional: hide legend if not needed
        ),
        tooltip=[
            alt.Tooltip("Emissions:Q", title="Emissions (tonnes of CO₂)")
        ]
    )
    .properties(width=600, height=600)
)

#st.markdown("<div style='height:15;'></div>", unsafe_allow_html=True)

st.altair_chart(chart, use_container_width=False)
