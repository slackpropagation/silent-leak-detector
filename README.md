# Silent Leak Detector: Session Analysis Dashboard

This project provides a data-driven dashboard to analyze and visualize user engagement patterns across a digital platform, based on real session-level data exported from Google Analytics. It aims to uncover critical bottlenecks (“leaks”) in the user journey; specifically, where and why users disengage before converting. By breaking down behavior across dimensions like geography, traffic source, device type, session duration, and funnel stage, this tool helps marketing and product teams:

	•	Quantify user drop-off rates at each key step of the funnel (e.g., browsing, engagement, conversion)
	•	Identify low-performing combinations (e.g., mobile traffic from certain sources)
	•	Highlight high-converting segments worth prioritizing in future campaigns
	•	Provide visual insights to support optimization of UX, content strategy, and ad targeting

Ultimately, the dashboard acts as a “leak detector”—guiding teams toward practical interventions (like improving mobile UX or tailoring mid-funnel messaging) to maximize conversion and reduce wasted acquisition spend.

## Key Graphs & Insights

### 1. **Country Conversion Map**
This interactive global choropleth map displays the conversion rates by country, based on aggregated session-level data. Each country is shaded according to its conversion performance, making it easy to spot geographic trends at a glance.

The visualization helps teams:
	•	Compare how different markets perform in terms of conversion
	•	Identify high-potential regions that are currently underperforming
	•	Prioritize localization, UX improvements, or targeted campaigns based on regional performance

While a few countries—such as the United States and some Western European markets—achieve conversion rates above 1–2%, the majority of global traffic converts at less than 0.5%. This stark contrast suggests that expanding ad spend into low-performing regions without first addressing regional UX barriers (e.g., language, loading time, mobile performance) could lead to poor returns on investment. This visualization supports strategic decision-making around international growth and budget allocation.

![Country Conversion Map](outputs/country_conversion_map.png)

To assess how reliable each country’s conversion rate is, we calculated 95% confidence intervals. This helps distinguish statistically meaningful patterns from noise, especially for countries with fewer sessions.

#### Country Conversion Rates with 95% Confidence Intervals

| Country        | Sessions | Conversions | Conversion Rate (%) | 95% CI (Lower - Upper) |
|----------------|----------|-------------|----------------------|-------------------------|
| United States  | 4,136    | 95          | 2.30%                | 1.88% – 2.80%           |
| Israel         | 60       | 1           | 1.67%                | 0.29% – 8.86%           |
| Canada         | 308      | 1           | 0.32%                | 0.06% – 1.82%           |

### 2. **Funnel Waterfall by Device**

This graph illustrates the user journey through four progressive stages of engagement:
	1.	Browsed – The user visits the site but takes no meaningful action.
	2.	Engaged – The user clicks, scrolls, or navigates within the site.
	3.	Deep Engagement – The user triggers high-intent signals (e.g., watches a full video, views pricing, adds to cart).
	4.	Converted – The user completes a goal (e.g., signs up, makes a purchase).

The waterfall layout breaks down these stages by device type (desktop, mobile, tablet), showing how many users drop off at each step. This lets teams compare funnel efficiency across platforms.

Key insight:
The steepest drop-off happens immediately after the “Browsed” stage, with a large portion of users bouncing without interacting at all—indicating weak initial hooks or unclear CTAs. Only 10–14% reach the “Deep Engagement” stage, and conversion rates are close to zero across all devices. Mobile and tablet users tend to fall off faster than desktop users, highlighting possible UX friction or slower performance on smaller screens.

This chart helps teams pinpoint which funnel stages and device types need urgent attention, so they can prioritize fixes like faster load times, clearer value props, or device-optimized content.

![Funnel Drop-off](outputs/funnel_dropoff_by_device.png)

The following breakdown estimates the total revenue lost at each stage of the funnel by multiplying drop-offs with the average revenue per conversion (~$134). This quantifies the cost of user leakage.

#### Estimated Revenue Lost per Funnel Stage

| Stage                         | Drop-offs | Estimated Revenue Lost ($) |
|------------------------------|-----------|-----------------------------|
| Browsed → Engaged            | 7,239     | $973,164.23                 |
| Engaged → Deep Engagement    | 356       | $47,858.33                  |
| Deep Engagement → Converted  | 682       | $91,683.66                  |

I compared mid-funnel users who failed to convert with those who did. The gap in engagement time and pageviews offers clues to where deeper content or better UX could prevent abandonment.

#### Mid-Funnel Drop-Off Comparison

| Metric                       | Converted Users | Non-Converting Engaged Users |
|-----------------------------|------------------|-------------------------------|
| Average Pageviews           | 23.95            | 10.16                         |
| Average Time on Site (sec)  | 960.77           | 433.60                        |
| Top Source                  | (direct)         | (direct)                      |
| Top Device                  | desktop          | desktop                       |

### 3. **Session Duration vs Conversion**

This graph explores the relationship between how long a user stays on the site (session duration) and their likelihood to convert. Sessions are grouped into time buckets (e.g., 0–10 seconds, 1–5 minutes, etc.), and the corresponding conversion rate is calculated for each.

The purpose of this visualization is to help identify the optimal engagement window—the amount of time users typically spend before taking action—and where drop-offs or wasted traffic occur.

Sessions lasting less than 10 seconds almost never result in a conversion, suggesting that these users either bounced immediately due to poor first impressions or weren’t the right audience. Conversion rates begin to rise significantly in the 10–20 minute range, peaking during this window and then leveling off or even declining slightly beyond 30 minutes—possibly due to distraction, confusion, or fatigue.

This insight supports the idea that the first 30 seconds should quickly hook users, and the overall experience should aim to sustain engagement for 5–20 minutes. Strategies like guided navigation, interactive elements, and personalized content can help keep users in this high-conversion zone.

This chart is especially useful for UX and content teams who want to align design, layout, and information delivery with actual behavioral patterns.

![Session Duration vs Conversion](outputs/session_duration_vs_conversion.png)

### 4. **Source × Device Heatmap**

This heatmap breaks down conversion performance across two dimensions:
	•	Traffic source (e.g., direct, Google Calendar, Outlook, Instagram, paid ads)
	•	Device type (desktop, mobile, tablet)

Each cell represents the conversion rate for a specific source-device combo, color-coded from low to high. The top 10 most frequent sources are included to focus on the most impactful segments.

This visualization is designed to help answer questions like:
	•	Which sources bring high-quality traffic vs. high-volume but low-converting users?
	•	Do certain sources work better on desktop vs. mobile?
	•	Are there device-specific UX issues that may be suppressing conversion?
 
Sources like Google Calendar and Outlook—which are often overlooked in attribution—show surprisingly strong conversion rates, especially on desktop. However, the same sources underperform significantly on mobile and tablet, suggesting possible issues like poor responsiveness, slower load times, or misaligned landing pages on smaller screens.

The broader trend across the heatmap is that mobile and tablet users convert less frequently regardless of the source, pointing to a systemic issue with the mobile experience. This supports prioritizing device-specific optimizations and tailoring campaigns for the platforms where they perform best.

By combining both source and device views, this chart offers targeted optimization opportunities—such as reallocating spend, adjusting messaging by platform, or improving cross-device consistency.

![Source Device Heatmap](outputs/source_device_heatmap.png)

To evaluate performance, we compared your actual device-level conversion rates with public industry benchmarks. This reveals how each platform is performing relative to expected norms.

#### Device Conversion Rates vs. Industry Benchmarks

| Device  | Sessions | Conversions | Your Conversion Rate (%) | Industry Avg (%) | Delta |
|---------|----------|-------------|---------------------------|------------------|--------|
| Desktop | 6,111    | 88          | 1.44%                     | 2.5%             | -1.06% |
| Mobile  | 3,437    | 7           | 0.20%                     | 1.9%             | -1.70% |
| Tablet  | 452      | 2           | 0.44%                     | 2.2%             | -1.76% |

## Business Takeaways

This analysis identifies critical leaks, behavioral patterns, and high-impact opportunities across the user journey. It translates complex data into clear strategic priorities for marketing, UX, and product teams.

### Major Leak Points
	
•	Biggest leak: The most significant user drop-off occurs immediately after landing—between the “Browsed” and “Engaged” stages. A large portion of sessions end without any meaningful interaction, indicating weak first impressions, unclear CTAs, or misaligned landing page content.

### Optimization Goals
	
•	Key engagement window: Focus on retaining users within the 5–20 minute session range, where conversion probability sharply increases. Keeping users engaged for at least 1–2 minutes, and ideally up to 10–20, should be a priority.
•	Use this insight to inform content strategy, interaction design, and onboarding flow—especially on mobile where attention spans are shorter.

### High-Converting Patterns

•	Top-converting combinations:
•	Desktop + calendar.google.com
•	Desktop + outlook.live.com

These niche sources generate relatively fewer sessions but very high conversion rates, suggesting they attract highly qualified traffic. These should be prioritized for campaign expansion or lookalike audience modeling.

### Actionable Fixes

•	Improve mobile and tablet UX: Address widespread performance gaps across devices. Start by auditing speed, responsiveness, navigation, and form completion on mobile/tablet.
•	Target mid-funnel drop-off: Many users engage briefly but fail to reach “deep engagement.” Strengthen this middle layer with guided flows, product tours, and timely prompts.
•	Refine ad spend strategy: Shift focus toward source-device pairs with strong ROI. Avoid allocating budget to sources that generate volume but yield low engagement or conversions—especially on mobile.

## Folder Structure

```
silent-leak-detector/
├── data/
│   ├── cleaned_sessions.csv
│   └── raw_sessions.csv
├── outputs/
│   ├── country_conversion_map.png
│   ├── funnel_dropoff_by_device.png
│   ├── session_duration_vs_conversion.png
│   └── source_device_heatmap.png
├── pages/
│   ├── Country_Conversion_Map.py
│   ├── Funnel_Dropoff_by_Device.py
│   ├── Session_Duration_vs_Conversion.py
│   └── Source_x_Device_Heatmap.py
├── scripts/
│   └── clean_data.py
├── Homepage.py
├── leak_analysis.ipynb
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Setup & Requirements

- Python 3.10+
- Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

- To run the dashboard locally:
\`\`\`bash
streamlit run Homepage.py
\`\`\`

## Data Source

Session-level export from Google Analytics  
Date range: up to **May 13, 2025**  
Sensitive user info anonymized

## License

This project is licensed under the MIT License.  
You are free to use, modify, and distribute it with attribution.  
See the [LICENSE](LICENSE) file for full terms.
