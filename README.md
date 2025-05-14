# Silent Leak Detector: Session Analysis Dashboard

This project visualizes user engagement and conversion patterns using real web session data.  
It is designed to help identify where major leaks occur in the user journey—from traffic sources to final conversion—and recommend data-driven solutions.

---

## Key Graphs & Insights

### 1. **Country Conversion Map**
A global choropleth showing conversion rates by country.  
**Key insight**: While a few markets (like the U.S.) convert above 1–2%, most sit under 0.5%. Investing in these low-performing countries without improving UX could waste resources.

### 2. **Funnel Waterfall by Device**
Visualizes where users drop off in the funnel: Browsed → Engaged → Deep Engagement → Converted.  
**Key insight**: Most sessions drop right after browsing. Only ~10–14% make it to “Deep Engagement,” and nearly 0% convert.

### 3. **Session Duration vs Conversion**
Analyzes how long users stay on-site before converting.  
**Key insight**: Visits under 10 seconds rarely convert. Conversion peaks between 10–20 minutes and then plateaus. Keeping users engaged for 5–20 minutes is critical.

### 4. **Source × Device Heatmap**
Color-coded heatmap of top 10 traffic sources and their performance across devices.  
**Key insight**: Some sources (e.g., Google Calendar, Outlook) convert well—but mostly on desktop. Mobile/tablet performance is weak across the board.

---

## Business Takeaways

- **Biggest leak**: Drop-off between Browsed and Engaged stages.
- **Key goal**: Push more users into the 5–20 minute engagement range.
- **Top-converting combos**: Desktop + calendar.google.com and desktop + outlook.live.com.
- **Actionable fixes**:
  - Improve mobile and tablet experiences.
  - Customize content for mid-funnel engagement.
  - Prioritize ad spend on high-conversion source-device combos.

---

## Folder Structure

```
📦 silent-leak-detector/
├── data/
│   └── cleaned_sessions.csv
├── pages/
│   ├── country_conversion_map.py
│   ├── funnel_waterfall.py
│   ├── session_duration_correlation.py
│   └── source_device_heatmap.py
├── outputs/
│   └── *.png (optional export)
└── README.md
```

---

## Setup & Requirements

- Python 3.10+
- Install dependencies:
```bash
pip install -r requirements.txt
```

- To run the dashboard locally:
```bash
streamlit run Home.py
```

---

## Data Source

Session-level export from Google Analytics  
Date range: up to **May 13, 2025**  
Sensitive user info anonymized

---

## License

MIT. Free to use, share, and adapt.

---
