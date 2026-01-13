import base64
import mimetypes
from pathlib import Path

import streamlit as st
from navigation import load_sidebar

# =========================
# Page setup (FIRST command)
# =========================
st.set_page_config(
    page_title="Interactive tool",
    layout="wide",
)

# --- Sidebar ---
load_sidebar()  # make sure load_sidebar() does NOT call st.set_page_config

# =========================
# Per-logo size controls
# =========================
# This is the cleanest way to control each logo separately:
# - box_height_px: fixed row height; logos are vertically centered within it (same middle line)
# - width_pct: max width as % of its column (each logo can differ)
# - height_pct: max height as % of the fixed box height (each logo can differ)
LOGOS = [
    {"path": "Tampere_uni_logo.png", "box_height_px": 100, "width_pct": 100, "height_pct": 100},
    {"path": "logo1.png",            "box_height_px": 90, "width_pct": 90, "height_pct": 90},
    {"path": "logo2.png",            "box_height_px": 100, "width_pct": 100, "height_pct": 100},
]

# Space between the text and the logo row
LOGO_ROW_TOP_PADDING_PX = 22


def img_to_data_uri(path: str) -> str:
    """Read an image file and return a data URI usable in <img src="...">."""
    p = Path(path)
    if not p.exists():
        return ""

    mime, _ = mimetypes.guess_type(str(p))
    if mime is None:
        mime = "image/png"

    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def logo_html(path: str, box_height_px: int, width_pct: int, height_pct: int) -> str:
    """
    A fixed-height box (shared middle line) with the image centered.
    width_pct controls max-width relative to the column.
    height_pct controls max-height relative to the box height.
    """
    data_uri = img_to_data_uri(path)
    if not data_uri:
        return f"""
        <div class="logo-box" style="height:{box_height_px}px;">
          <div style="font-size:12px; opacity:0.7;">Missing file: {path}</div>
        </div>
        """

    return f"""
    <div class="logo-box" style="height:{box_height_px}px;">
      <img
        src="{data_uri}"
        style="
          max-width: {width_pct}%;
          max-height: {height_pct}%;
          width: auto;
          height: auto;
          object-fit: contain;
          display: block;
        "
        alt="logo"
      />
    </div>
    """


# --- Title ---
st.title("Interactive tool")

# --- Intro Text ---
st.markdown(
    """
This interactive tool allows you to explore potential environmental and health impacts of different remote working scenarios in the Helsinki capital region.

The tool allows comparing emissions, travel patterns, and health impacts relative to three main scenarios: **S1 - No remote working; S2 - Current remote working; and S3 - Full remote working potential**. Additionally, by changing the percentage of the remote working population through the interactive sliders, approximations of the effects are shown for the chosen level of remote working by interpolating results from these base scenarios.

The **T-Winning Spaces 2035** project aims to point towards winning spatial solutions for future work, enabling the double twin transition of digital/green and virtual/physical transforming our societies by 2035. Within this remit, this tool allows interactive visualization of the results from Work Package 3, whose goal was to understand the health impacts associated with digital work futures, and quantify the possible changes to GHG emissions.  
More information: https://t-winning-spaces2035.com/

The tool was developed by members of the Urban Physics Research Group at Tampere University: **Petr Anashin, Alonso Espinosa Mireles de Villafranca**, and the group head, **Jonathon Taylor**.

*T-Winning Spaces 2035 is a project funded by the Research Council of Finland and has received funding from the European Union NextGenerationEU programme.*
"""
)

# --- CSS + spacing above logos ---
st.markdown(
    f"""
<style>
.logo-row-spacer {{
  height: {LOGO_ROW_TOP_PADDING_PX}px;
}}

.logo-box {{
  display: flex;
  align-items: center;       /* vertical centering -> same middle line */
  justify-content: center;   /* horizontal centering */
  width: 100%;
}}
</style>

<div class="logo-row-spacer"></div>
""",
    unsafe_allow_html=True,
)

# --- Image Layout ---
# Columns: [left margin, logo1, middle space, logo2, middle space, logo3, right margin]
col_empty1, col_img1, col_empty2, col_img2, col_empty3, col_img3, col_empty4 = st.columns(
    [0.02, 0.3, 0.04, 0.3, 0.02, 0.3, 0.02]
)

# --- Render each logo with its own percentages ---
with col_img1:
    L = LOGOS[0]
    st.markdown(logo_html(L["path"], L["box_height_px"], L["width_pct"], L["height_pct"]), unsafe_allow_html=True)

with col_img2:
    L = LOGOS[1]
    st.markdown(logo_html(L["path"], L["box_height_px"], L["width_pct"], L["height_pct"]), unsafe_allow_html=True)

with col_img3:
    L = LOGOS[2]
    st.markdown(logo_html(L["path"], L["box_height_px"], L["width_pct"], L["height_pct"]), unsafe_allow_html=True)
