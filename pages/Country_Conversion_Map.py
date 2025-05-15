# Import libraries
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import pycountry
import streamlit as st

# 1. Configuration: paths, thresholds, colors, and fonts
DATA_PATH  = "data/cleaned_sessions.csv"               # input dataset
PNG_OUT    = Path("outputs/country_conversion_map.png") # optional export
MIN_SESS   = 100                                        # traffic filter

# Colour palette
DARK_BG    = "#18122B"  # almost-black (tables, etc.)
PAPER_BG   = "#2E2E2E"  # ChatGPT dark-gray (page & plot background)

# Global font
FONT       = dict(family="Helvetica Neue", color="#FFFFFF", size=16)


# 2. Load data
df = pd.read_csv(DATA_PATH)

# 3. Compute sessions, conversions, and conversion rate per country
country = (
    df.groupby("country")
      .agg(sessions=('converted', 'count'),
           conversions=('converted', 'sum'))
)
country["rate"] = country["conversions"] / country["sessions"] * 100
country = country[country["sessions"] >= MIN_SESS]  # drop tiny samples

# 4. Map country names to ISO-3 codes (for Plotly choropleth)
def iso3(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError:
        return None

country["iso3"] = country.index.map(iso3)
country = country.dropna(subset=["iso3"])            # keep valid codes


# 5. Build the choropleth figure
fig = go.Figure()

fig.add_trace(
    go.Choropleth(
        locations   = country["iso3"],
        z           = country["rate"],
        text        = country.index,
        # custom rainbow-ish scale ↓
        colorscale  = [
            [0.00, "#08306B"], [0.20, "#2171B5"], [0.40, "#41B6C4"],
            [0.50, "#FFFFBF"], [0.60, "#FEE08B"], [0.80, "#FC4E2A"],
            [1.00, "#B10026"]
        ],
        reversescale=False,
        marker_line_color="#FFFFFF",
        marker_line_width=0.5,

        # vertical color-bar (title drawn separately as annotation)
        colorbar=dict(
            x=0.037, y=0.15,              # bottom-left inside map
            xanchor="center", yanchor="bottom",
            len=0.60, thickness=25,
            tickfont=dict(size=18, color="#FFFFFF"),
            outlinecolor="#FFFFFF", outlinewidth=1
        ),
    )
)

# 6. Add custom colorbar label
fig.add_annotation(
    text="Conversion Rate (%)",
    textangle=-90, xref="paper", yref="paper",
    x=0.00, y=0.45,
    showarrow=False,
    font=dict(size=20, color="#FFFFFF", family="Helvetica Neue Bold")
)

# 7. Configure map projection and styling
fig.update_geos(
    projection_type="equirectangular",   # fast, rectangular projection
    projection_scale=1,                 # zoom factor
    bgcolor=PAPER_BG,                   # behind-globe colour
    showocean=True,  oceancolor="#08274A",
    showland=True,   landcolor="#0e0f1e",
    showcountries=False, coastlinewidth=0,
    showframe=False,
    domain=dict(x=[0, 1], y=[0, 1])     # map fills subplot
)

# 8. Configure layout, title, fonts, and margins
fig.update_layout(
    title=dict(
        text="Conversion Rate by Country (sessions ≥ 100)",
        x=0.5, y=0.98, xanchor="center",
        pad=dict(b=4),
        font=dict(size=28, color="#e65100", family="Helvetica Neue Bold")
    ),
    font=FONT,                          # default font for rest
    paper_bgcolor=PAPER_BG,
    plot_bgcolor=PAPER_BG,
    height=780,
    margin=dict(t=20, l=0, r=0, b=20)
)

# 9. Footer: source annotation and overall metrics
total_sessions   = int(country["sessions"].sum())
overall_rate_pct = country["conversions"].sum() / total_sessions * 100

fig.add_annotation(
    text="Google Analytics 360 Demo (Google Merchandise Store, 2016–2017)",
    xref="paper", yref="paper",
    x=0.01, y=-0.02,
    xanchor="left", yanchor="bottom",
    showarrow=False,
    font=dict(size=20, color="#e65100", family="Helvetica Neue Bold")
)

fig.add_annotation(
    text=f"Total sessions: {total_sessions:,}  •  Overall conv-rate: {overall_rate_pct:.2f} %",
    xref="paper", yref="paper",
    x=0.99, y=-0.02,
    xanchor="right", yanchor="bottom",
    showarrow=False,
    font=dict(size=20, color="#e65100", family="Helvetica Neue Bold")
)


# 10. Streamlit page configuration and render
st.set_page_config(layout="wide")

st.plotly_chart(fig, use_container_width=True)

# Page context and implementation details
st.markdown("""
#### **Graph Context**
This map visualizes conversion rates by country, filtering out any with fewer than 100 sessions to ensure statistical reliability. Country names are converted to ISO‑3 codes via the `pycountry` library for Plotly’s choropleth. A custom rainbow‑ish colorscale highlights performance from low (deep blue) to high (red) rates.  
The projection uses an equirectangular map on a dark background theme (`#2E2E2E`), with oceans and land styled in complementary shades.  
A rotated annotation serves as the vertical colorbar label, and footer annotations display total sessions and overall conversion rate for all included countries.  
Data is loaded from `data/cleaned_sessions.csv` and the figure can be optionally exported to `outputs/country_conversion_map.png`.
""")