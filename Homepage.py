import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Silent Leak Detector", layout="wide")

# === GitHub-style theme settings ===
sns.set_style("whitegrid")
sns.set_context("notebook", font_scale=1.1)
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#D0D7DE",
    "axes.labelcolor": "#24292F",
    "xtick.color": "#57606A",
    "ytick.color": "#57606A",
    "grid.color": "#D0D7DE",
    "text.color": "#24292F",
    "axes.titleweight": "bold",
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "font.family": "Helvetica Neue"
})

# Load data
df = pd.read_csv('data/cleaned_sessions.csv')

# Preprocessing
df['conversion_rate'] = df['converted']
df['funnel_stage'] = pd.Categorical(df['funnel_stage'],
    categories=['Bounced', 'Browsed', 'Engaged', 'Deep Engagement'],
    ordered=True
)

# Sidebar filters
st.sidebar.title("Filters")
device_filter = st.sidebar.multiselect("Device", options=df['devicecategory'].unique(), default=df['devicecategory'].unique())
country_filter = st.sidebar.multiselect("Country", options=df['country'].unique(), default=df['country'].unique())
source_filter = st.sidebar.multiselect("Traffic Source", options=df['source'].unique(), default=df['source'].unique())

# Apply filters
filtered = df[
    (df['devicecategory'].isin(device_filter)) &
    (df['country'].isin(country_filter)) &
    (df['source'].isin(source_filter))
]

# === KPI Cards ===
st.markdown("## Silent Leak Detector", unsafe_allow_html=True)
st.markdown("### Find out where attention goes to waste.", unsafe_allow_html=True)

total_sessions = int(filtered.shape[0])
total_conversions = int(filtered['converted'].sum())
overall_rate = round((total_conversions / total_sessions) * 100, 2) if total_sessions > 0 else 0

st.markdown("### Conversion Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Sessions", f"{total_sessions:,}")
col2.metric("Total Conversions", f"{total_conversions:,}")
col3.metric("Overall Conversion Rate", f"{overall_rate}%")

st.markdown(" ")
st.markdown("---")

# === Funnel Stage Summary ===
st.markdown("## Funnel Stage Summary")
funnel_summary = filtered.groupby('funnel_stage')['converted'].agg(['count', 'sum', 'mean']).rename(columns={
    'count': 'Sessions',
    'sum': 'Conversions',
    'mean': 'Conversion Rate'
})
funnel_summary['Conversion Rate'] = (funnel_summary['Conversion Rate'] * 100).round(2)
st.dataframe(funnel_summary)

st.markdown(" ")

st.markdown("## Country Conversion Map")
try:
    st.image("outputs/country_conversion_map.png", use_container_width=True)
except Exception as e:
    st.warning("Country conversion map not found.")

st.markdown("## Funnel Dropoff by Device")
try:
    st.image("outputs/funnel_dropoff_by_device.png", use_container_width=True)
except Exception as e:
    st.warning("Funnel waterfall chart not found.")

st.markdown("## Session Duration vs Conversion")
try:
    st.image("outputs/session_duration_vs_conversion.png", use_container_width=True)
except Exception as e:
    st.warning("Session duration correlation chart not found.")

st.markdown("## Source × Device Heatmap")
try:
    st.image("outputs/source_device_heatmap.png", use_container_width=True)
except Exception as e:
    st.warning("Source × Device heatmap not found.")

st.markdown(" ")
st.markdown("---")

# === Leak Scorecard ===
st.markdown("## Leak Scorecard")
scorecard = filtered.groupby(['devicecategory', 'funnel_stage']).agg(
    sessions=('converted', 'count'),
    conversions=('converted', 'sum'),
    conversion_rate=('converted', 'mean')
).reset_index()
scorecard['conversion_rate'] = (scorecard['conversion_rate'] * 100).round(2)

leaks = scorecard[
    (scorecard['funnel_stage'].isin(['Engaged', 'Deep Engagement'])) &
    (scorecard['conversion_rate'] < 1.0)
].sort_values(by='sessions', ascending=False)

st.dataframe(leaks)

st.markdown("---")
st.markdown(
    "<div style='display: flex; justify-content: space-between;'>"
    "<div style='color: white; font-size: 16px;'>Google Analytics 360 Demo (Google Merchandise Store, 2016–2017)</div>"
    "<div style='color: white; font-size: 16px;'>Total sessions: {:,} • Overall conv-rate: {:.2f}%</div>"
    "</div>".format(total_sessions, overall_rate),
    unsafe_allow_html=True
)
st.markdown("---")
st.caption("Built by Eray Yaman • 2025 Portfolio Project")