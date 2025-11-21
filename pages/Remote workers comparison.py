import streamlit as st
import geopandas as gpd
import json
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static
from navigation import load_sidebar

CARTO_DARK = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"


# ============================================================
# --- PAGE SETUP & STYLE ---
# ============================================================
st.set_page_config(layout="wide")
#page_title="Remote workers comparison"

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
# --- INITIALIZE NAVIGATION STATE ---
# ============================================================
if "mode" not in st.session_state:
    st.session_state.mode = "S3_S2"   # default page

# ============================================================
# --- SHARED UTILITIES ---
# ============================================================
def make_color_legend(title, colors, labels, reverse=False):
    """Compact legend with consistent spacing, centered text, and larger vertical gaps between rows."""
    if reverse:
        colors = list(reversed(colors))
    html = f"""
    <div style='margin-top:10px; line-height:16px;'>
        <b>{title}</b>
        <div style='margin-top:6px; display:flex; flex-wrap:wrap; row-gap:6px;'>  <!-- increased row spacing -->
    """
    for c, l in zip(colors, labels):
        html += (
            f"<div style='display:inline-flex; align-items:center; margin-right:8px;'>"
            f"<div style='width:20px; height:12px; background:{c}; margin-right:5px;'></div>"
            f"<span style='display:inline-block; vertical-align:middle;'>{l}</span></div>"
        )
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)


def get_color(value, thresholds, palette, reverse=False):
    if reverse:
        if value <= thresholds[0]: return palette[-1]
        elif value <= thresholds[1]: return palette[-2]
        elif value <= thresholds[2]: return palette[-3]
        elif value <= thresholds[3]: return palette[-4]
        elif value <= thresholds[4]: return palette[-5]
        elif value <= thresholds[5]: return palette[-6]
        else: return palette[0]
    else:
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
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(4326)
    return gdf

COLOR_PALETTE = ["#3B0A45", "#78001E", "#B52F0D", "#D65E00", "#E98000", "#F3A300", "#FFD400"]

# ============================================================
# --- PAGE 1: S3 vs S2 ---
# ============================================================
if st.session_state.mode == "S3_S2":
    st.markdown("<h3>Difference in the number of remote workers at the selected percentage of the remote-working population VS at the remote-working population percentage in S3</h3>", unsafe_allow_html=True)

    # Centered button right under title
    if st.button("S2 vs S1 comparison"):
        st.session_state.mode = "S2_S1"
        st.rerun()

    gdf = load_dataset("Datasets/Grid maps/s2_s3_remote_workers_diff.gpkg")

    quantiles_abs = [0.25, 0.4, 0.6, 0.74, 0.8, 0.9, 0.97]
    thresholds_abs = gdf["absolute_change"].quantile(quantiles_abs).tolist()
    thresholds_perc = [0.15, 0.25, 0.4, 0.6, 0.85, 1, 1.15]

    # --- Slider layout below button ---
    col_slider, _, opacity_slider, _ = st.columns([0.35, 0.15, 0.35, 0.15])
    with col_slider:
        st.markdown("<p style='font-weight:600; margin-bottom:6px;'>The percentage of remote working population</p>", unsafe_allow_html=True)
        slider_val = st.slider("slider_s3s2", 24.0, 47.3, 47.3, 0.1, format="%.1f", label_visibility="collapsed")
    with opacity_slider:
        st.markdown("<p style='font-weight:600; margin-bottom:6px;'>Opacity</p>", unsafe_allow_html=True)
        opacity_val = st.slider("opacity_s3s2", float(0), float(1), float(0.8), float(0.01), label_visibility="collapsed")

    # --- Data transformation ---
    factor = (47.3 - slider_val) / (47.3 - 24.0)
    gdf["Absolute change in the number of remote workers"] = (gdf["absolute_change"] * (1 - factor)).round(1)
    gdf["Percentage change in the number of remote workers (%)"] = gdf["percentage_change"] * (1 - factor)
    gdf["color_abs_hex"] = gdf["Absolute change in the number of remote workers"].apply(lambda v: get_color(v, thresholds_abs, COLOR_PALETTE))
    gdf["color_perc_hex"] = gdf["Percentage change in the number of remote workers (%)"].apply(lambda v: get_color(v, thresholds_perc, COLOR_PALETTE))
    gdf["geometry_json"] = gdf["geometry"].apply(lambda g: json.dumps(g.__geo_interface__))
    gdf["Percentage change in the number of remote workers (%)"] = (gdf["Percentage change in the number of remote workers (%)"] * 100).round(1).astype(str) + " %"

    df_abs = gdf[["Absolute change in the number of remote workers", "geometry_json"]].copy()
    df_abs["Colour code"] = gdf["color_abs_hex"]
    df_perc = gdf[["Percentage change in the number of remote workers (%)", "geometry_json"]].copy()
    df_perc["Colour code"] = gdf["color_perc_hex"]

    # --- Kepler Configs ---
    kepler_config_abs = {
        "version": "v1",
        "config": {"mapState": {"latitude": 60.25, "longitude": 25.05, "zoom": 8.75},
                   "mapStyle": {
                # Use custom style instead of the built-in "dark"
                "styleType": "carto_dark",
                "mapStyles": [
                    {
                        "id": "carto_dark",
                        "label": "Carto Dark",
                        "url": CARTO_DARK,  # style.json URL
                    }
                ],
            },
                   "visState": {"layers": [{
                       "id": "abs_layer", "type": "geojson",
                       "config": {"dataId": "absolute_change", "columns": {"geojson": "geometry_json"},
                                  "isVisible": True,
                                  "visConfig": {"opacity": opacity_val, "filled": True,
                                                "colorRange": {"colors": COLOR_PALETTE}}},
                       "visualChannels": {"colorField": {"name": "Colour code", "type": "string"},
                                          "colorScale": "ordinal"},
                   }]}}
    }

    kepler_config_perc = {
        "version": "v1",
        "config": {"mapState": {"latitude": 60.25, "longitude": 24.91, "zoom": 8.7},
                   "mapStyle": {
                # Use custom style instead of the built-in "dark"
                "styleType": "carto_dark",
                "mapStyles": [
                    {
                        "id": "carto_dark",
                        "label": "Carto Dark",
                        "url": CARTO_DARK,  # style.json URL
                    }
                ],
            },
                   "visState": {"layers": [{
                       "id": "perc_layer", "type": "geojson",
                       "config": {"dataId": "percentage_change", "columns": {"geojson": "geometry_json"},
                                  "isVisible": True,
                                  "visConfig": {"opacity": opacity_val, "filled": True,
                                                "colorRange": {"colors": COLOR_PALETTE}}},
                       "visualChannels": {"colorField": {"name": "Colour code", "type": "string"},
                                          "colorScale": "ordinal"},
                   }]}}
    }

    # --- Two maps side by side ---
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Absolute Change**")
        map_abs = KeplerGl(height=380, data={"absolute_change": df_abs}, config=kepler_config_abs)
        keplergl_static(map_abs)
        make_color_legend("Legend: Absolute change in the number of remote workers",
                          COLOR_PALETTE, [f"≤ {v:.1f}" for v in thresholds_abs] + ["> max"])
    with col2:
        st.markdown("**Percentage Change**")
        map_perc = KeplerGl(height=380, data={"percentage_change": df_perc}, config=kepler_config_perc)
        keplergl_static(map_perc)
        make_color_legend("Legend: Percentage change in the number of remote workers (%)",
                          COLOR_PALETTE, [f"≤ {v*100:.0f}%" for v in thresholds_perc] + ["> max"])

# ============================================================
# --- PAGE 2: S2 vs S1 ---
# ============================================================
elif st.session_state.mode == "S2_S1":
    st.markdown("<h3>Difference in the number of remote workers at the selected percentage of the remote-working population VS at the remote-working population percentage in S2</h3>", unsafe_allow_html=True)

    # Centered back button
    if st.button("Back to S3 vs S2"):
        st.session_state.mode = "S3_S2"
        st.rerun()

    gdf = load_dataset("Datasets/Grid maps/s1_s2_remote_workers_diff.gpkg")
    quantiles_abs = [0.05, 0.15, 0.25, 0.4, 0.6, 0.8, 0.95]
    thresholds_abs = gdf["absolute_change"].quantile(quantiles_abs).tolist()

    col_slider, _, opacity_slider, _ = st.columns([0.35, 0.15, 0.35, 0.15])
    with col_slider:
        st.markdown("<p style='font-weight:600; margin-bottom:6px;'>The percentage of remote working population</p>", unsafe_allow_html=True)
        slider_val = st.slider("slider_s2s1", 0.0, 24.0, 0.0, 0.1, format="%.1f", label_visibility="collapsed")
    with opacity_slider:
        st.markdown("<p style='font-weight:600; margin-bottom:6px;'>Opacity</p>", unsafe_allow_html=True)
        opacity_val = st.slider("opacity_s3s2", float(0), float(1), float(0.8), float(0.01), label_visibility="collapsed")

    factor = slider_val / 24.0
    gdf["Absolute change in the number of remote workers"] = (gdf["absolute_change"] * (1 - factor)).round(1)
    gdf["color_abs_hex"] = gdf["Absolute change in the number of remote workers"].apply(
        lambda v: get_color(v, thresholds_abs, COLOR_PALETTE, reverse=True))
    gdf["geometry_json"] = gdf["geometry"].apply(lambda g: json.dumps(g.__geo_interface__))
    df_abs = gdf[["Absolute change in the number of remote workers", "geometry_json"]].copy()
    df_abs["Colour code"] = gdf["color_abs_hex"]

    kepler_config_abs = {
        "version": "v1",
        "config": {"mapState": {"latitude": 60.25, "longitude": 25.08, "zoom": 8.75},
                   "mapStyle": {
                        "id": "carto_dark",
                        "label": "Carto Dark",
                        "url": CARTO_DARK,  # style.json URL
                    },
                   "visState": {"layers": [{
                       "id": "abs_layer", "type": "geojson",
                       "config": {"dataId": "absolute_change", "columns": {"geojson": "geometry_json"},
                                  "isVisible": True,
                                  "visConfig": {"opacity": opacity_val, "filled": True,
                                                "colorRange": {"colors": COLOR_PALETTE}}},
                       "visualChannels": {"colorField": {"name": "Colour code", "type": "string"},
                                          "colorScale": "ordinal"},
                   }]}}
    }

    col1, col2 = st.columns([0.45, 0.55])
    with col1:
        st.markdown("**Absolute Change**")
        map_abs = KeplerGl(height=380, data={"absolute_change": df_abs}, config=kepler_config_abs)
        keplergl_static(map_abs)
        make_color_legend("Legend: Absolute change in the number of remote workers",
                          COLOR_PALETTE, [f"≤ {v:.1f}" for v in thresholds_abs] + ["> max"])
    with col2:
        st.empty()
