# pages/session_duration_corelation.py
import streamlit as st
# Set Streamlit page configuration (must be first)
st.set_page_config(layout="wide")  # must be first

# load libraries
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ── CONSTANTS ─────────────────────────────────────────
DATA_PATH = "data/cleaned_sessions.csv"
PAPER_BG  = "#2E2E2E"
FONT      = dict(family="Helvetica Neue Bold", color="#FFFFFF", size=14)
DEVICE_COLORS = {
    "desktop": "#64ffda",
    "mobile":  "#00bcd4",
    "tablet":  "#ff6b6b",
}
# define session-duration buckets and labels
BINS   = [0, 10, 60, 180, 300, 600, 1200, 3600]
LABELS = ["<10s", "10–60s", "1–3m", "3–5m", "5–10m", "10–20m", "20–60m"]

# 1. Load data, filter unrealistic sessions, and assign buckets
df = pd.read_csv(DATA_PATH)
# drop sessions outside realistic range (1 to 3600 seconds) to avoid skewing analysis
df = df[df["timeonsite"].between(1, 3600)]
# assign bucket
df["bucket"] = pd.cut(df["timeonsite"], bins=BINS, labels=LABELS, right=False)

# 2. Aggregate sessions and conversions by bucket and device
# 'converted' is a boolean flag; count it for total sessions and sum for conversions
agg = (
    df
    .groupby(["bucket", "devicecategory"])
    .agg(
        sessions=("converted", "count"),
        conversions=("converted", "sum")
    )
    .reset_index()
)
agg["conv_rate"] = agg["conversions"] / agg["sessions"] * 100

# pivot tables for volumes and rates
pivot_vol = agg.pivot(index="bucket", columns="devicecategory", values="sessions").fillna(0)
pivot_cr  = agg.pivot(index="bucket", columns="devicecategory", values="conv_rate").fillna(0)

# 3. Build figure: grouped bars for volume + lines for conversion-rate
fig = go.Figure()

# Bars represent session volumes on secondary y-axis
for dev, col in DEVICE_COLORS.items():
    fig.add_trace(go.Bar(
        x=LABELS,
        y=pivot_vol.get(dev, []),
        name=f"{dev.title()} volume",
        marker_color=col,
        opacity=0.4,
        yaxis="y2",
        hovertemplate="%{y:,} sessions<extra></extra>"
    ))

# Lines represent conversion rates on primary y-axis
for dev, col in DEVICE_COLORS.items():
    fig.add_trace(go.Scatter(
        x=LABELS,
        y=pivot_cr.get(dev, []),
        name=f"{dev.title()} conv‑rate",
        mode="lines+markers",
        marker=dict(size=8, color=col),
        line=dict(width=3, color=col),
        hovertemplate="%{y:.1f}% conv<extra></extra>"
    ))

# 4. Configure layout, axes, and styling
fig.update_layout(
    # Title styling
    title=dict(
        text="Session Duration vs. Conversion by Device",
        x=0.5, xanchor="center", y=0.95, yanchor="top", font=dict(size=24, color="#e65100", family="Helvetica Neue Bold")
    ),
    # Background and font
    paper_bgcolor=PAPER_BG,
    plot_bgcolor=PAPER_BG,
    font=FONT,
    # Bar mode and legend positioning
    barmode="group",
    legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
    # Margins
    margin=dict(t=80, l=60, r=60, b=60),
    # X-axis styling
    xaxis=dict(
        title=dict(
            text="Session Duration Bucket",
            font=dict(color="#e65100", size=18)
        ),
        tickfont=dict(size=14)
    ),
    # Primary y-axis: conversion rate styling
    yaxis=dict(
        title=dict(
            text="Conversion Rate (%)",
            font=dict(color="#e65100", size=18)
        ),
        tickfont=dict(color="#FFFFFF"),
        range=[0, pivot_cr.values.max() * 1.1]
    ),
    # Secondary y-axis: session volume styling
    yaxis2=dict(
        title=dict(
            text="Sessions",
            font=dict(color="#e65100", size=18)
        ),
        tickfont=dict(color="#FFFFFF"),
        overlaying="y",
        side="right",
        position=1.0,
        range=[0, pivot_vol.values.max() * 1.1]
    )
)

# grid & zero‑lines for clarity
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor="#555", zeroline=True, zerolinecolor="#888")

# Add footer annotation with data source
fig.add_annotation(
    text="Google Analytics 360 Demo (Google Merchandise Store, 2016–2017)",
    xref="paper", yref="paper",
    x=1.045, y=-0.23,
    xanchor="right", yanchor="bottom",
    showarrow=False,
    font=dict(size=14, color="#e65100", family="Helvetica Neue Bold")
)

st.plotly_chart(fig, use_container_width=True, key="Session_Duration_vs_Conversion")