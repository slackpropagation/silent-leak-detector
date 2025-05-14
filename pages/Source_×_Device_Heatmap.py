import streamlit as st

st.set_page_config(layout="wide")  

# ── Imports & Theme ──────────────────────────────────
import pandas as pd
import plotly.express as px

PAPER_BG = "#2E2E2E"
FONT     = dict(family="Helvetica Neue Bold", color="#FFFFFF", size=16)
DATA_PATH = "data/cleaned_sessions.csv"

# ── Load & Aggregate ─────────────────────────────────
df = pd.read_csv(DATA_PATH)

# Compute conversion rate (%) by source × device
pivot = (
    df
    .groupby(["source", "devicecategory"])["converted"]
    .mean()           # fraction of sessions that converted
    .mul(100)         # to percent
    .round(1)         # one decimal
    .reset_index()
    .pivot(index="source", columns="devicecategory", values="converted")
    .fillna(0)
)

# Remove traffic sources with 0% conversion across all devices
pivot = pivot.loc[(pivot > 0).any(axis=1)]

# Compute average conversion rate across devices for sorting
pivot["avg_conv"] = pivot.mean(axis=1)
# Sort descending and keep only the top 10 sources
pivot = pivot.sort_values("avg_conv", ascending=False).head(10).drop(columns="avg_conv")

# Rename device columns to title case (e.g. 'desktop' → 'Desktop')
pivot.columns = pivot.columns.str.title()
# Map specific traffic source keys to friendly names
source_map = {
    'calendar.google.com': 'Google Calendar',
    'outlook.live.com': 'Microsoft Outlook',
    'google': 'Google',
    'dfa': 'Google Display Ads',        # remap DFA doubleclick traffic
    '(direct)': 'Direct Traffic',         # remap no-referrer direct visits
}
pivot.index = [source_map.get(src, src) for src in pivot.index]

# ── Build Heatmap ───────────────────────────────────
colorscale = [
    [0.00, "#08306B"],
    [0.20, "#2171B5"],
    [0.40, "#41B6C4"],
    [0.50, "#FFFFBF"],
    [0.60, "#FEE08B"],
    [0.80, "#FC4E2A"],
    [1.00, "#B10026"]
]

fig = px.imshow(
    pivot,
    color_continuous_scale=colorscale,
    text_auto=True,
    labels=dict(x="Device Category", y="Traffic Source", color="Conv‑Rate (%)"),
    aspect="auto"
)

# build per-cell HTML colored text
z = fig.data[0].z  # 2D array of values
threshold = pivot.values.max() * 0.5  # choose threshold
text_html = [
    [
        f"<span style='color:{'black' if val >= threshold else 'white'}'>{val}</span>"
        for val in row
    ]
    for row in z
]
fig.data[0].text = text_html
fig.data[0].texttemplate = "%{text}"
fig.data[0].textfont = dict(size=18, family="Helvetica Neue Bold")

# draw thin white lines between cells
fig.update_traces(xgap=1, ygap=1)

# ── Add white outlines between heatmap cells ────────
nrows, ncols = pivot.shape
grid_shapes = []

# vertical lines
for i in range(ncols + 1):
    x = i / ncols
    grid_shapes.append(dict(
        type="line", xref="paper", yref="paper",
        x0=x, x1=x, y0=0, y1=1,
        line=dict(color="#FFFFFF", width=0.5)
    ))
    
# horizontal lines
for j in range(nrows + 1):
    y = j / nrows
    grid_shapes.append(dict(
        type="line", xref="paper", yref="paper",
        x0=0, x1=1, y0=y, y1=y,
        line=dict(color="#FFFFFF", width=0.5)
    ))
    
# merge with existing shapes
fig.update_layout(shapes=tuple(fig.layout.shapes) + tuple(grid_shapes))

# ── Style & Layout ──────────────────────────────────
border_shape = dict(
    type="rect",
    xref="paper", yref="paper",
    x0=0, y0=0, x1=1, y1=1,
    line=dict(color="#FFFFFF", width=1)
)

all_shapes = tuple(fig.layout.shapes) + (border_shape,)

fig.update_layout(
    title=dict(
        text="Top 10 Traffic Sources by Conversion Rate and Device",
        x=0.5, xanchor="center", y=0.95, yanchor="top",
        font=dict(size=24, color="#e65100", family="Helvetica Neue Bold"),
        pad=dict(b=0)  # reduce space below the title
    ),
    paper_bgcolor=PAPER_BG,
    plot_bgcolor=PAPER_BG,
    font=FONT,
    margin=dict(l=60, r=80, t=60, b=40),
    shapes=all_shapes,
)

# bring x‑axis tick labels closer to the heatmap
fig.update_xaxes(ticklabelstandoff=-10)

# Enlarge axis titles with bold text and font
fig.update_xaxes(
    title=dict(
        text="<b>Device Category</b>",
        font=dict(size=20, color="#e65100", family="Helvetica Neue Bold")
    ),
    tickfont=dict(size=14, color="#FFFFFF", family="Helvetica Neue Bold")
)
fig.update_yaxes(
    title=dict(
        text="<b>Traffic Source</b>",
        font=dict(size=20, color="#e65100", family="Helvetica Neue Bold")
    ),
    tickfont=dict(size=14, color="#FFFFFF", family="Helvetica Neue Bold")
)


# ── Adjust colorbar to our spec ────────────────────────
fig.update_coloraxes(
    colorbar_title_text=None,
    colorbar_tickfont=dict(size=12, color="#FFFFFF", family="Helvetica Neue Bold"),
    colorbar_outlinecolor="#FFFFFF",
    colorbar_outlinewidth=1,
    colorbar_lenmode="fraction",
    colorbar_len=1,
    colorbar_thickness=20,
    colorbar_x=1.01,
    colorbar_xanchor="left",
    colorbar_y=0.5,
    colorbar_yanchor="middle",
)

# Manual vertical colorbar label on inner side
fig.add_annotation(
    text="Conversion Rate (%)",
    textangle=-90,
    xref="paper", yref="paper",
    x=1.015, y=0.5,               # just inside the bar
    xanchor="center", yanchor="middle",
    showarrow=False,
    font=dict(size=18, color="#FFFFFF", family="Helvetica Neue Bold")
)

# ── Footer annotations (data source & headline metrics) ─
total_sessions = len(df)
overall_rate_pct = df["converted"].mean() * 100

fig.add_annotation(
    text="Google Analytics 360 Demo (Google Merchandise Store, 2016–2017)",
    xref="paper", yref="paper",
    x=1.08, y=-0.21,
    xanchor="right", yanchor="bottom",
    showarrow=False,
    font=dict(size=14, color="#e65100", family="Helvetica Neue Bold")
)

# ── 5️⃣ Render ───────────────────────────────────────────
st.plotly_chart(fig, use_container_width=True, key="source_device_heatmap")