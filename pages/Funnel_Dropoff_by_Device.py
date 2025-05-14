"""
Funnel drop-off by device
─────────────────────────
Left axis  : % of sessions that survive each stage
Right axis : absolute sessions (light, semi-transparent bars)
"""
# ── imports & theme ─────────────────────────────────────
import numpy as np, pandas as pd, plotly.graph_objects as go, streamlit as st
from plotly.subplots import make_subplots
st.set_page_config(layout="wide")

PAPER = "#2E2E2E"
FONT  = dict(family="Helvetica Neue Bold", color="#ffffff", size=14)

# device-line colours: neon cyberpunk
PAL = {
    "desktop": "#00E5FF",  # teal
    "tablet" : "#FF4C4C",  # reddish
    "mobile" : "#88CC00"   # darker green
}

# table & subplot background shades: darker neon variants
SHADE = {
    "desktop": "#003F40",  # even darker teal
    "tablet" : "#7F0000",  # darker red
    "mobile" : "#224400"   # deeper green
}

STAGE      = ["Browsed", "Engaged", "Deep Engagement", "Converted"]
STAGE_COL  = {"Browsed": "#64ffda",
              "Engaged": "#00bcd4",
              "Deep Engagement": "#ffc857",
              "Converted": "#ff6b6b"}

# ── data ────────────────────────────────────────────────
df = pd.read_csv("data/cleaned_sessions.csv")
df = df[df["funnel_stage"].isin(STAGE)]
df["funnel_stage"] = pd.Categorical(df["funnel_stage"], STAGE, ordered=True)

devices = df["devicecategory"].unique().tolist()

# pre-aggregate absolute sessions per device / stage
base = pd.DataFrame({"funnel_stage": STAGE})
agg  = (df.groupby(["devicecategory", "funnel_stage"]).size()
          .rename("sessions").reset_index())

# also aggregate total conversions per device
conv_agg = df.groupby("devicecategory")["converted"].sum().rename("conversions")

# ── build figure ────────────────────────────────────────

fig = make_subplots(
    rows=len(devices),
    cols=2,
    shared_xaxes=True,
    column_widths=[0.65, 0.35],
    vertical_spacing=0.05,   # more breathing room between device plots
    horizontal_spacing=0.02,
    specs=[[{"type":"xy"}, {"type":"table"}] for _ in devices]
)

# ── subplot background shading per device ───────────────
n = len(devices)
vertical_spacing = 0.05
row_height = (1 - vertical_spacing * (n - 1)) / n

# draw a shaded rectangle behind each device plot in the left column
# ── subplot background shading per device ───────────────
for idx, dev in enumerate(devices):
    row = idx + 1   # Plotly rows are 1‑indexed
    fig.add_shape(
        type="rect",
        # draw in axis domain coordinates, not paper
        xref="x domain" if row == 1 else f"x{row} domain",
        yref="y domain" if row == 1 else f"y{row} domain",
        x0=0, x1=1,                   # full width of that subplot
        y0=0, y1=1,                   # full height of that subplot
        row=row, col=1,               # place shape in left column of this row
        fillcolor=SHADE[dev],
        layer="below",
        line=dict(color="#FFFFFF", width=1)
    )

# 2️⃣  %-survival lines (left y-axis) –– use PAL for colour
for r, dev in enumerate(devices, start=1):
    a   = (base.merge(agg[agg.devicecategory == dev],
                      on="funnel_stage", how="left").fillna(0))
    # override "Converted" stage count with actual conversions
    a.loc[a.funnel_stage == "Converted", "sessions"] = conv_agg[dev]
    entry = a.loc[a.funnel_stage == "Browsed", "sessions"].iat[0] or np.nan
    pct   = (a["sessions"] / entry * 100).round(1)
    # add a tiny epsilon so log‐scale never sees pure 0
    pct_safe = pct.replace(0, 0.2)

    fig.add_trace(go.Scatter(
        x=STAGE, y=pct_safe,
        mode="lines+markers+text",
        line=dict(width=4, color=PAL.get(dev, "#cccccc")),  # ← unique colour, line width changed to 4
        marker=dict(size=10, color=PAL.get(dev, "#cccccc")),
        text=[f"{p:.1f} %" for p in pct],
        textposition="top center",
        name=dev.title()
    ), row=r, col=1)

    fig.add_annotation(
        xref="paper", yref=f'y{r}' if r > 1 else 'y',
        x=-0.04, y=np.nanmax(pct)/2,  # roughly mid‑height
        text=f"<b>{dev.title()}</b>",
        showarrow=False,
        font=dict(family="Helvetica Neue", size=14, color="#ffffff")
    )

    # prepare table values for this device
    stages = a["funnel_stage"]
    sessions = a["sessions"].astype(int)
    survive_pct = [(s/entry*100).round(1) for s in a["sessions"]]

    fig.add_trace(
        go.Table(
            header=dict(
                values=["Stage", "Sessions", "Survive %"],
                fill_color=PAL[dev], font=dict(family="Helvetica Neue Bold", color="white"), align="center", height=28,
                line_color="#FFFFFF", line_width=1
            ),
            cells=dict(
                values=[stages, sessions, survive_pct],
                fill_color=SHADE[dev], font=dict(family="Helvetica Neue Bold", color="white"), align="center", height=24,
                line_color="#FFFFFF", line_width=0.5
            )
        ),
        row=r, col=2
    )

# ── add visual 0 % guide line on each subplot ────────────
# log‑scale cannot display an actual 0, so we place the line at 0.1 %
for r in range(1, len(devices) + 1):
    fig.add_shape(
        type="line",
        x0=0, x1=1,                 # full width of subplot
        y0=0.1, y1=0.1,             # 0.1 % (10^-1) ≈ “zero” reference
        xref="x domain",
        yref=f"y{r}" if r > 1 else "y",
        line=dict(color="#444", width=1, dash="dot"),
        layer="below",
    )

# ── highlight major grid lines at 1%, 10%, 100% ──────────────────
for r in range(1, len(devices) + 1):
    for y_val in [1, 10, 100]:
        fig.add_shape(
            type="line",
            x0=0, x1=1,
            y0=y_val, y1=y_val,
            xref="x domain",
            yref=f"y{r}" if r > 1 else "y",
            line=dict(color="#FFFFFF", width=2),
            layer="below",
        )

# ── add vertical dividers between stages ──────────────────────────────────
for stage in ["Browsed", "Engaged", "Deep Engagement", "Converted"]:
    fig.add_shape(
        type="line",
        x0=stage, x1=stage,
        y0=0, y1=1,
        xref="x", yref="paper",
        line=dict(color="#FFFFFF", width=2, dash="dash"),
        layer="below",
    )

# ── axes & layout ───────────────────────────────────────
fig.update_yaxes(
    title="% of entry (log scale)",
    type="log",
    dtick=1,                 # ticks at 1 %, 10 %, 100 %
    tickvals=[0.1, 1, 10, 100],
    ticktext=["0 %", "1 %", "10 %", "100 %"],
    range=[-1, 2.5],
    showgrid=True,
    gridcolor="#555",
    gridwidth=0.3
)

fig.update_layout(
    title=dict(
        text="Where do sessions leak? – Funnel stage vs. device",
        x=0.5, xanchor="center", y=0.98, yanchor="top",
        font=dict(size=26, color="#e65100", family="Helvetica Neue Bold")
    ),
    legend=dict(
        orientation="h",
        y=1.06, yanchor="top",
        x=0.5, xanchor="center"
    ),
    paper_bgcolor=PAPER, plot_bgcolor=PAPER, font=FONT,
    height=240*len(devices)+120, margin=dict(t=90, l=80, r=40, b=40)
)

# enlarge the funnel stage labels on the x-axis
fig.update_xaxes(tickfont=dict(size=16))

# ── Footer annotations (data source & headline metrics) ─
total_sessions   = int(df["sessions"].sum()) if "sessions" in df.columns else int(df.shape[0])
country = agg  # fallback: using agg as "country" is not defined elsewhere
if "sessions" in agg.columns and "conversions" in agg.columns:
    total_sessions   = int(agg["sessions"].sum())
    overall_rate_pct = agg["conversions"].sum() / total_sessions * 100
else:
    total_sessions   = int(df.shape[0])
    overall_rate_pct = np.nan

fig.add_annotation(
    text="Google Analytics 360 Demo (Google Merchandise Store, 2016–2017)",
    xref="paper", yref="paper",
    x=1.02, y=-0.05,
    xanchor="right", yanchor="bottom",
    showarrow=False,
    font=dict(size=14, color="#e65100", family="Helvetica Neue Bold")
)

# ── Render funnel drop-off figure in Streamlit ─────────────────────────────────
# Displays the funnel stage drop-off by device with survival percentages and session counts.
st.plotly_chart(fig, use_container_width=True)

