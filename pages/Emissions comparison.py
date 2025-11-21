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
#page_title="Emissions comparison"

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
    st.session_state.mode = "S3_S2"  # default page

# ============================================================
# --- SHARED UTILITIES ---
# ============================================================
def make_color_legend(title, colors, labels, reverse=False):
    """Compact legend with consistent spacing, centered text, and larger vertical gaps between rows."""
    if reverse:
        colors = list(reversed(colors))
        labels = list(reversed(labels))
    html = f"""
    <div style='margin-top:0px; line-height:16px;'>
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


def get_color(value, thresholds, palette, reverse=False):
    """Assign colors by threshold range. If reverse=True, lowest values = brightest colors."""
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
    """Load GeoPackage safely and convert to EPSG:4326."""
    gdf = gpd.read_file(path)
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(4326)
    return gdf


COLOR_PALETTE = ["#3B0A45", "#78001E", "#B52F0D", "#D65E00", "#E98000", "#F3A300", "#FFD400"]

# ============================================================
# --- MANUAL THRESHOLDS (EDIT THESE) ---
#   * ABS thresholds are in kg (after /1000 conversion)
#   * PERC thresholds are in PERCENT points (we /100 for internal use)
# ============================================================

# S3 vs S2: mostly negative changes, lowest = brightest
ABS_THRESHOLDS_S3S2 = [-32.0, -22.0, -12.0, -6.0, -3.0, -0.5, 2]
# Example percentage thresholds (%). Change to your own.
PERC_THRESHOLDS_S3S2 = [-40, -30, -22, -15, -8 ,-2, 5]

# S2 vs S1: mostly positive changes, highest = brightest
ABS_THRESHOLDS_S2S1 = [2, 4, 8, 13.0, 21.0, 30.0, 41]
# Example percentage thresholds (%). Change to your own.
PERC_THRESHOLDS_S2S1 = [2.5, 5, 11, 18, 25, 35, 45]

# ============================================================
# --- PAGE 1: S3 vs S2 (mostly negative, lowest = brightest) ---
# ============================================================
if st.session_state.mode == "S3_S2":
    st.markdown("<h3>Difference in the amount of CO2 emissions at the selected percentage of the remote-working population VS at the remote-working population percentage in S3</h3>", unsafe_allow_html=True)

    if st.button("S2 vs S1 comparison"):
        st.session_state.mode = "S2_S1"
        st.rerun()

    gdf = load_dataset("Datasets/Grid maps/s2_s3_emissions_diff.gpkg")
    gdf["absolute_change"] = gdf["absolute_change"] / 1000

    # Use manual thresholds (ABS + PERC)
    thresholds_abs = ABS_THRESHOLDS_S3S2
    # Convert percent thresholds to fractions for internal use
    thresholds_perc = [v / 100.0 for v in PERC_THRESHOLDS_S3S2]

    col_slider, _, opacity_slider, _ = st.columns([0.35, 0.15, 0.35, 0.15])
    with col_slider:
        st.markdown("<p style='font-weight:600; margin-bottom:6px;'>The percentage of remote working population</p>", unsafe_allow_html=True)
        slider_val = st.slider("slider_s3s2", 24.0, 47.3, 47.3, 0.1, format="%.1f", label_visibility="collapsed")
    with opacity_slider:
        st.markdown("<p style='font-weight:600; margin-bottom:6px;'>Opacity</p>", unsafe_allow_html=True)
        opacity_val = st.slider("opacity_s3s2", float(0), float(1), float(0.8), float(0.01), label_visibility="collapsed")

    factor = (47.3 - slider_val) / (47.3 - 24.0)
    gdf["Absolute change in the amount of CO2 emissions, kg"] = (gdf["absolute_change"] * (1 - factor)).round(1)
    gdf["Percentage change numeric"] = gdf["percentage_change"] * (1 - factor) * 100  # numeric %
    gdf["Percentage change formatted"] = gdf["Percentage change numeric"].map(lambda v: f"{v:.1f}%")

    # Lowest = brightest for S3 vs S2
    gdf["color_abs_hex"] = gdf["Absolute change in the amount of CO2 emissions, kg"].apply(
        lambda v: get_color(v, thresholds_abs, COLOR_PALETTE, reverse=True)
    )
    gdf["color_perc_hex"] = (gdf["percentage_change"] * (1 - factor)).apply(
        lambda v: get_color(v, thresholds_perc, COLOR_PALETTE, reverse=True)
    )

    gdf["geometry_json"] = gdf["geometry"].apply(lambda g: json.dumps(g.__geo_interface__))

    df_abs = gdf[["Absolute change in the amount of CO2 emissions, kg", "geometry_json"]].copy()
    df_abs["Colour code"] = gdf["color_abs_hex"]

    df_perc = gdf[["Percentage change formatted", "geometry_json"]].copy()
    df_perc["Colour code"] = gdf["color_perc_hex"]

    kepler_config = lambda data_id: {
    "version": "v1",
    "config": {
        "mapState": {
            "latitude": 60.25,
            "longitude": 25.05,
            "zoom": 8.75,
            "bearing": 0,
            "pitch": 0,
        },
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
        "visState": {
            "layers": [{
                "id": f"{data_id}_layer",
                "type": "geojson",
                "config": {
                    "dataId": data_id,
                    "columns": {"geojson": "geometry_json"},
                    "isVisible": True,
                    "visConfig": {
                        "opacity": opacity_val,
                        "filled": True,
                        "colorRange": {"colors": COLOR_PALETTE},
                    },
                },
                "visualChannels": {
                    "colorField": {"name": "Colour code", "type": "string"},
                    "colorScale": "ordinal",
                },
            }],
        },
        "options": {
            "centerMap": False,   # <- don't auto-fit to data bounds
            "readOnly": False,    # or True if you don't want the user to pan/zoom
        },
    },
    }

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Absolute Change**")
        map_abs = KeplerGl(height=380, data={"absolute_change": df_abs}, config=kepler_config("absolute_change"))
        keplergl_static(map_abs)
        make_color_legend(
            "Legend: Absolute change in the amount of CO2 emissions, kg",
            COLOR_PALETTE[::-1], [f"≤ {v:.1f}" for v in thresholds_abs], reverse=False
        )
    with col2:
        st.markdown("**Percentage Change**")
        map_perc = KeplerGl(height=380, data={"percentage_change": df_perc}, config=kepler_config("percentage_change"))
        keplergl_static(map_perc)
        make_color_legend(
            "Legend: Percentage change in the amount of CO2 emissions (%)",
            COLOR_PALETTE[::-1], [f"≤ {v:.1f}%" for v in PERC_THRESHOLDS_S3S2], reverse=False
        )

# ============================================================
# --- PAGE 2: S2 vs S1 (mostly positive, highest = brightest) ---
# ============================================================
elif st.session_state.mode == "S2_S1":
    st.markdown("<h3>Difference in the amount of CO2 emissions at the selected percentage of the remote-working population VS at the remote-working population percentage in S3</h3>", unsafe_allow_html=True)

    if st.button("Back to S3 vs S2"):
        st.session_state.mode = "S3_S2"
        st.rerun()

    gdf = load_dataset("Datasets/Grid maps/s1_s2_emissions_diff.gpkg")
    gdf["absolute_change"] = gdf["absolute_change"] / 1000

    # Use manual thresholds (ABS + PERC)
    thresholds_abs = ABS_THRESHOLDS_S2S1
    thresholds_perc = [v / 100.0 for v in PERC_THRESHOLDS_S2S1]

    col_slider, _, opacity_slider, _ = st.columns([0.35, 0.15, 0.35, 0.15])
    with col_slider:
        st.markdown("<p style='font-weight:600; margin-bottom:6px;'>The percentage of remote working population</p>", unsafe_allow_html=True)
        slider_val = st.slider("slider_s2s1", 0.0, 24.0, 0.0, 0.1, format="%.1f", label_visibility="collapsed")
    with opacity_slider:
        st.markdown("<p style='font-weight:600; margin-bottom:6px;'>Opacity</p>", unsafe_allow_html=True)
        opacity_val = st.slider("opacity_s3s2", float(0), float(1), float(0.8), float(0.01), label_visibility="collapsed")

    factor = slider_val / 24.0
    gdf["Absolute change in the amount of CO2 emissions, kg"] = (gdf["absolute_change"] * (1 - factor)).round(1)
    gdf["Percentage change numeric"] = gdf["percentage_change"] * (1 - factor) * 100
    gdf["Percentage change formatted"] = gdf["Percentage change numeric"].map(lambda v: f"{v:.1f}%")

    # Highest = brightest for S2 vs S1
    gdf["color_abs_hex"] = gdf["Absolute change in the amount of CO2 emissions, kg"].apply(
        lambda v: get_color(v, thresholds_abs, COLOR_PALETTE)
    )
    gdf["color_perc_hex"] = (gdf["percentage_change"] * (1 - factor)).apply(
        lambda v: get_color(v, thresholds_perc, COLOR_PALETTE)
    )

    gdf["geometry_json"] = gdf["geometry"].apply(lambda g: json.dumps(g.__geo_interface__))

    df_abs = gdf[["Absolute change in the amount of CO2 emissions, kg", "geometry_json"]].copy()
    df_abs["Colour code"] = gdf["color_abs_hex"]

    df_perc = gdf[["Percentage change formatted", "geometry_json"]].copy()
    df_perc["Colour code"] = gdf["color_perc_hex"]

    kepler_config = lambda data_id: {
    "version": "v1",
    "config": {
        "mapState": {
            "latitude": 60.25,
            "longitude": 25.05,
            "zoom": 8.75,
            "bearing": 0,
            "pitch": 0,
        },
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
        "visState": {
            "layers": [{
                "id": f"{data_id}_layer",
                "type": "geojson",
                "config": {
                    "dataId": data_id,
                    "columns": {"geojson": "geometry_json"},
                    "isVisible": True,
                    "visConfig": {
                        "opacity": opacity_val,
                        "filled": True,
                        "colorRange": {"colors": COLOR_PALETTE},
                    },
                },
                "visualChannels": {
                    "colorField": {"name": "Colour code", "type": "string"},
                    "colorScale": "ordinal",
                },
            }],
        },
        "options": {
            "centerMap": False,   # <- don't auto-fit to data bounds
            "readOnly": False,    # or True if you don't want the user to pan/zoom
        },
    },
}

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Absolute Change**")
        map_abs = KeplerGl(height=380, data={"absolute_change": df_abs}, config=kepler_config("absolute_change"))
        keplergl_static(map_abs)
        make_color_legend(
            "Legend: Absolute change in the amount of CO2 emissions, kg",
            COLOR_PALETTE, [f"≤ {v:.1f}" for v in thresholds_abs]
        )
    with col2:
        st.markdown("**Percentage Change**")
        map_perc = KeplerGl(height=380, data={"percentage_change": df_perc}, config=kepler_config("percentage_change"))
        keplergl_static(map_perc)
        make_color_legend(
            "Legend: Percentage change in the amount of CO2 emissions (%)",
            COLOR_PALETTE, [f"≤ {v:.1f}%" for v in PERC_THRESHOLDS_S2S1]
        )
