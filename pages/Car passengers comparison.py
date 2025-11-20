import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import json
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static
from navigation import load_sidebar

CARTO_DARK = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"

# ============================================================
# --- PAGE SETUP & STYLE ---
# ============================================================
st.set_page_config(layout="wide")
                   #page_title="Car passengers comparison"

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

/* --- Button Styling --- */
div[data-testid="stButton"] button {
    background-color: #FF4B4B !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 0.55em 1.6em !important;
    border: none !important;
    font-weight: 800 !important;
    font-size: 26px !important;
    font-family: "Source Sans Pro", sans-serif !important;
    white-space: nowrap !important;
    text-align: center !important;
    display: block !important;
    margin: 0 auto !important;
}
div[data-testid="stButton"] button:hover {
    background-color: #ff7373 !important;
}

/* --- Slider thinner + centered labels --- */
div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div {
    height: 2px !important;
}
div[data-testid="stSlider"] div[data-baseweb="slider"] div[role="slider"] {
    width: 12px !important;
    height: 12px !important;
}

/* Properly center min/max labels */
div[data-testid="stSlider"] div[data-testid="stTickBar"] > div:first-child > div,
div[data-testid="stSlider"] div[data-testid="stTickBar"] > div:last-child > div {
    transform: translateX(-50%) !important;
    text-align: center !important;
    display: inline-block !important;
    width: auto !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# --- NAV STATE ---
# ============================================================
if "mode" not in st.session_state:
    st.session_state.mode = "S3_S2"  # default page

# ============================================================
# --- UTILITIES ---
# ============================================================
def make_color_legend(title, colors, labels, reverse=False):
    if reverse:
        colors = list(reversed(colors))
        labels = list(reversed(labels))
    html = f"""
    <div style='margin-top:10px; line-height:16px;'>
        <b>{title}</b>
        <div style='margin-top:6px; display:flex; flex-wrap:wrap; row-gap:6px;'>
    """
    for c, l in zip(colors, labels):
        html += (
            f"<div style='display:inline-flex; align-items:center; margin-right:8px;'>"
            f"<div style='width:20px; height:12px; background:{c}; margin-right:5px;'></div>"
            f"<span style='display:inline-block; vertical-align:middle;'>{l}</span></div>"
        )
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)

def get_color(value, thresholds, palette, reverse=False, default="#888888"):
    if pd.isna(value):
        return default
    if reverse:
        palette = list(reversed(palette))
    if value <= thresholds[0]: return palette[0]
    elif value <= thresholds[1]: return palette[1]
    elif value <= thresholds[2]: return palette[2]
    elif value <= thresholds[3]: return palette[3]
    elif value <= thresholds[4]: return palette[4]
    elif value <= thresholds[5]: return palette[5]
    elif value <= thresholds[6]: return palette[6]
    else: return palette[-1]

def load_dataset(path):
    gdf = gpd.read_file(path)
    # Ensure WGS84 for kepler.gl
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(4326)
    return gdf

# Color palette (7 steps)
COLOR_PALETTE = ["#3B0A45", "#78001E", "#B52F0D", "#D65E00", "#E98000", "#F3A300", "#FFD400"]

# ============================================================
# --- MANUAL THRESHOLDS (EDIT THESE VALUES) ---
#   * thresholds must be sorted from lowest to highest
#   * percentage thresholds are in FRACTIONS, not percent
#     (e.g. -0.5 = -50%, 0.3 = +30%)
# ============================================================

# S3 vs S2 (mostly negative, lowest = brightest)
ABS_THRESHOLDS_S3S2 = [-110.0, -80, -60.0, -40.0, -25.0, -10.0, -5.0]
PERC_THRESHOLDS_S3S2 = [-0.55, -0.45, -0.35, -0.23, -0.10, -0.05, -0.01]

# S2 vs S1 (mostly positive, highest = brightest)
ABS_THRESHOLDS_S2S1 = [10.0, 25.0, 50.0, 75.0, 100.0, 150.0, 200.0]
PERC_THRESHOLDS_S2S1 = [0.2, 0.7, 1.4, 2.0, 3.0, 5.0, 7.0]

# ============================================================
# --- KEPLER CONFIG FOR LINESTRINGS ---
#   * Treat lines like "polygons" color-wise by using stroke colors
#   * thickness fixed at 0.5 as you requested
# ============================================================
def kepler_config_lines(data_id, palette):
    return {
        "version": "v1",
        "config": {
            "mapState": {"latitude": 60.26, "longitude": 25.5, "zoom": 8.6},
            "mapStyle": {
                        "id": "carto_dark",
                        "label": "Carto Dark",
                        "url": CARTO_DARK,  # style.json URL
                    },
            "visState": {
                "layers": [{
                    "id": f"{data_id}_layer",
                    "type": "geojson",
                    "config": {
                        "dataId": data_id,
                        "label": data_id,
                        "columns": {"geojson": "geometry_json"},
                        "isVisible": True,
                        "visConfig": {
                            "opacity": 0.9,
                            "stroked": True,     # important for LineStrings
                            "filled": False,     # polygons only; keep False for lines
                            "thickness": 0.5,    # requested line width
                            "colorRange": {"colors": palette},          # used by colorField (fill)
                            "strokeColorRange": {"colors": palette},    # used by strokeColorField
                        },
                    },
                    "visualChannels": {
                        # For lines we color via STROKE color channels:
                        "strokeColorField": {"name": "Colour code", "type": "string"},
                        "strokeColorScale": "ordinal",
                        # Leave fill color channels unused for lines
                    }
                }]
            }
        }
    }

# ============================================================
# --- PAGE 1: S3 vs S2 (mostly negative, lowest = brightest) ---
# ============================================================
if st.session_state.mode == "S3_S2":
    st.markdown("<h3>Difference in the number of car passengers at the selected percentage of the remote-working population VS at the remote-working population percentage in S3</h3>", unsafe_allow_html=True)

    if st.button("S2 vs S1 comparison"):
        st.session_state.mode = "S2_S1"
        st.rerun()

    # --- LINESTRING DATASETS ---
    gdf = load_dataset("Datasets/Traffic changes/s2_s3_cars_difference_rebounds_abs_change.gpkg")

    # Ensure percentage_change is float
    if "percentage_change" in gdf.columns:
        gdf["percentage_change"] = gdf["percentage_change"].astype(float)

    # Create 2 datasets and drop NaNs
    gdf_abs = gdf.dropna(subset=["absolute_change"]).copy()
    gdf_perc = gdf.dropna(subset=["percentage_change"]).copy()

    # --- Use manual thresholds instead of quantiles ---
    thresholds_abs = ABS_THRESHOLDS_S3S2
    thresholds_perc = PERC_THRESHOLDS_S3S2

    col_slider, _, _, _ = st.columns([0.35, 0.08, 0.07, 0.5])
    with col_slider:
        st.markdown("<p style='font-weight:600; margin-bottom:6px;'>The percentage of remote working population</p>", unsafe_allow_html=True)
        slider_val = st.slider("slider_s3s2", 24.0, 47.3, 47.3, 0.1, format="%.1f", label_visibility="collapsed")

    factor = (47.3 - slider_val) / (47.3 - 24.0)

    # Derived fields for ABS dataset
    gdf_abs["Absolute change in the number of car passengers"] = (
        gdf_abs["absolute_change"] * (1 - factor)
    ).round(1)

    # Derived fields for PERC dataset
    gdf_perc["Percentage change numeric"] = gdf_perc["percentage_change"] * (1 - factor) * 100
    gdf_perc["Percentage change formatted"] = gdf_perc["Percentage change numeric"].map(
        lambda v: f"{v:.1f}%"
    )

    # Lowest = brightest
    gdf_abs["color_abs_hex"] = gdf_abs["Absolute change in the number of car passengers"].apply(
        lambda v: get_color(v, thresholds_abs, COLOR_PALETTE, reverse=True)
    )
    gdf_perc["color_perc_hex"] = (gdf_perc["percentage_change"] * (1 - factor)).apply(
        lambda v: get_color(v, thresholds_perc, COLOR_PALETTE, reverse=True)
    )

    # GeoJSON string per row
    gdf_abs["geometry_json"] = gdf_abs["geometry"].apply(lambda geom: json.dumps(geom.__geo_interface__))
    gdf_perc["geometry_json"] = gdf_perc["geometry"].apply(lambda geom: json.dumps(geom.__geo_interface__))

    # Two views: absolute / percentage
    df_abs = gdf_abs[["Absolute change in the number of car passengers", "geometry_json"]].copy()
    df_abs["Colour code"] = gdf_abs["color_abs_hex"]

    df_perc = gdf_perc[["Percentage change formatted", "geometry_json"]].copy()
    df_perc["Colour code"] = gdf_perc["color_perc_hex"]

    # Build maps (LineString-aware)
    cfg_abs = kepler_config_lines("absolute_change", COLOR_PALETTE)
    cfg_perc = kepler_config_lines("percentage_change", COLOR_PALETTE)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Absolute Change**")
        map_abs = KeplerGl(height=380, data={"absolute_change": df_abs}, config=cfg_abs)
        keplergl_static(map_abs)
        make_color_legend(
            "Legend: Absolute change in the number of car passengers",
            COLOR_PALETTE[::-1], [f"≤ {v:.1f}" for v in thresholds_abs]
        )
    with col2:
        st.markdown("**Percentage Change**")
        map_perc = KeplerGl(height=380, data={"percentage_change": df_perc}, config=cfg_perc)
        keplergl_static(map_perc)
        make_color_legend(
            "Legend: Percentage change in the number of car passengers (%)",
            COLOR_PALETTE[::-1], [f"≤ {v*100:.1f}%" for v in thresholds_perc]
        )

# ============================================================
# --- PAGE 2: S2 vs S1 (mostly positive, highest = brightest) ---
# ============================================================
elif st.session_state.mode == "S2_S1":
    st.markdown("<h3>Difference in the number of car passengers at the selected percentage of the remote-working population VS at the remote-working population percentage in S2</h3>", unsafe_allow_html=True)

    if st.button("Back to S3 vs S2"):
        st.session_state.mode = "S3_S2"
        st.rerun()

    # --- LINESTRING DATASETS ---
    gdf = load_dataset("Datasets/Traffic changes/s1_s2_cars_difference_rebounds_abs_change.gpkg")

    # Ensure percentage_change is float
    if "percentage_change" in gdf.columns:
        gdf["percentage_change"] = gdf["percentage_change"].astype(float)

    # Create 2 datasets and drop NaNs
    gdf_abs = gdf.dropna(subset=["absolute_change"]).copy()
    gdf_perc = gdf.dropna(subset=["percentage_change"]).copy()

    # --- Use manual thresholds instead of quantiles ---
    thresholds_abs = ABS_THRESHOLDS_S2S1
    thresholds_perc = PERC_THRESHOLDS_S2S1

    col_slider, _, _, _ = st.columns([0.35, 0.08, 0.07, 0.5])
    with col_slider:
        st.markdown("<p style='font-weight:600; margin-bottom:6px;'>The percentage of remote working population</p>", unsafe_allow_html=True)
        slider_val = st.slider("slider_s2s1", 0.0, 24.0, 0.0, 0.1, format="%.1f", label_visibility="collapsed")

    factor = slider_val / 24.0

    # Derived fields for ABS dataset
    gdf_abs["Absolute change in the number of car passengers"] = (
        gdf_abs["absolute_change"] * (1 - factor)
    ).round(1)

    # Derived fields for PERC dataset
    gdf_perc["Percentage change numeric"] = gdf_perc["percentage_change"] * (1 - factor) * 100
    gdf_perc["Percentage change formatted"] = gdf_perc["Percentage change numeric"].map(
        lambda v: f"{v:.1f}%"
    )

    # Highest = brightest
    gdf_abs["color_abs_hex"] = gdf_abs["Absolute change in the number of car passengers"].apply(
        lambda v: get_color(v, thresholds_abs, COLOR_PALETTE)
    )
    gdf_perc["color_perc_hex"] = (gdf_perc["percentage_change"] * (1 - factor)).apply(
        lambda v: get_color(v, thresholds_perc, COLOR_PALETTE)
    )

    gdf_abs["geometry_json"] = gdf_abs["geometry"].apply(lambda geom: json.dumps(geom.__geo_interface__))
    gdf_perc["geometry_json"] = gdf_perc["geometry"].apply(lambda geom: json.dumps(geom.__geo_interface__))

    df_abs = gdf_abs[["Absolute change in the number of car passengers", "geometry_json"]].copy()
    df_abs["Colour code"] = gdf_abs["color_abs_hex"]

    df_perc = gdf_perc[["Percentage change formatted", "geometry_json"]].copy()
    df_perc["Colour code"] = gdf_perc["color_perc_hex"]

    cfg_abs = kepler_config_lines("absolute_change", COLOR_PALETTE)
    cfg_perc = kepler_config_lines("percentage_change", COLOR_PALETTE)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Absolute Change**")
        map_abs = KeplerGl(height=380, data={"absolute_change": df_abs}, config=cfg_abs)
        keplergl_static(map_abs)
        make_color_legend(
            "Legend: Absolute change in the number of car passengers",
            COLOR_PALETTE, [f"≤ {v:.1f}" for v in thresholds_abs]
        )
    with col2:
        st.markdown("**Percentage Change**")
        map_perc = KeplerGl(height=380, data={"percentage_change": df_perc}, config=cfg_perc)
        keplergl_static(map_perc)
        make_color_legend(
            "Legend: Percentage change in the number of car passengers (%)",
            COLOR_PALETTE, [f"≤ {v*100:.1f}%" for v in thresholds_perc]
        )
