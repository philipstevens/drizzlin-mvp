# NovaEV Global Expansion Assistant – Refactored Streamlit App

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI

# --- Setup and Config ---
st.set_page_config(page_title="Global Market Expansion", layout="wide")

st.markdown("""
<style>
section.main > div {padding-top: 2rem;}
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
</style>
""", unsafe_allow_html=True)

st.title("Global Market Expansion Platform")

# --- Try to load OpenAI API ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("❌ Missing or invalid OpenAI API key in `secrets.toml`.")
    st.stop()

# --- Mock Market Data ---
mock_data = {
    "Country": ["Norway", "UK", "Australia", "Germany", "Mexico", "India", "Brazil", "Thailand"],
    "EV_Adoption": [80, 20, 8, 25, 3, 5, 4, 7],
    "Tariffs": [0, 10, 5, 10, 20, 15, 12, 10],
    "Charging_Stations": [5000, 700, 300, 1500, 200, 400, 350, 220],
    "China_Sentiment": [0.8, 0.7, 0.6, 0.4, 0.5, 0.3, 0.6, 0.7],
    "Market_Size": [5, 8, 6, 9, 6, 10, 7, 6]
}
df = pd.DataFrame(mock_data)

# --- Tabs Layout ---
tab1, tab2, tab3 = st.tabs(["🌍 Market Discovery", "🎯 GTM Strategy", "📊 Monitor & Adapt"])

# === TAB 1: Market Selection ===
with tab1:
    priority = st.multiselect(
        "Select key priorities:",
        ["EV Adoption", "Low Import Tariffs", "Strong Infrastructure", "Positive China Sentiment", "Market Size"]
    )

    weights = {
        "EV Adoption": 0.4 if "EV Adoption" in priority else 0,
        "Tariffs": -0.2 if "Low Import Tariffs" in priority else 0,
        "Charging_Stations": 0.2 if "Strong Infrastructure" in priority else 0,
        "China_Sentiment": 0.2 if "Positive China Sentiment" in priority else 0,
        "Market_Size": 0.2 if "Market Size" in priority else 0
    }

    df["Score"] = (
        df["EV_Adoption"] * weights["EV Adoption"] +
        df["Tariffs"] * weights["Tariffs"] +
        df["Charging_Stations"] / 100 * weights["Charging_Stations"] +
        df["China_Sentiment"] * 10 * weights["China_Sentiment"] +
        df["Market_Size"] * weights["Market_Size"]
    )
    ranked = df.sort_values("Score", ascending=False)

    top_n = st.slider("Show top N markets:", min_value=3, max_value=len(ranked), value=5)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(ranked.head(top_n), use_container_width=True)
        top_country = ranked.iloc[0]["Country"]
        st.markdown(f"🏆 **Top-ranked market:** `{top_country}` with score **{ranked.iloc[0]['Score']:.2f}**")

    with col2:
        bar_fig = px.bar(
            ranked.head(top_n),
            x="Country",
            y="Score",
            color="Score",
            title="🏆 Top Markets by Weighted Score",
            labels={"Score": "Priority-Weighted Score"}
        )
        st.plotly_chart(bar_fig, use_container_width=True)

    # Map UI labels to actual DataFrame column names
    priority_map = {
        "EV Adoption": "EV_Adoption",
        "Low Import Tariffs": "Tariffs",
        "Strong Infrastructure": "Charging_Stations",
        "Positive China Sentiment": "China_Sentiment",
        "Market Size": "Market_Size"
    }

    selected_cols = [priority_map[k] for k in priority if k in priority_map]

    if len(selected_cols) >= 3:
        st.markdown("📊 **Top Market Profiles (Radar Chart)**")
        radar_data = ranked.head(top_n)[["Country"] + selected_cols]
        radar_data = radar_data.set_index("Country").T
        fig_radar = go.Figure()
        for col in radar_data.columns:
            fig_radar.add_trace(go.Scatterpolar(
                r=radar_data[col],
                theta=radar_data.index,
                fill='toself',
                name=col
            ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            showlegend=True
        )
        st.plotly_chart(fig_radar, use_container_width=True)
# === TAB 2: GTM Strategy ===
with tab2:

    selected_country = st.selectbox("Choose a target market:", df["Country"])
    country_data = df[df["Country"] == selected_country].iloc[0]

    product_type = st.text_input("Product Type", "Compact urban electric car")
    price_point = st.text_input("Price Point", "~$20,000 USD")
    target_demo = st.text_input("Target Demographic", "Urban professionals, 25–40, eco-conscious, value-focused")

    prompt = f"""
You are an expert global marketing consultant specializing in automotive go-to-market (GTM) strategies.
A Chinese electric vehicle company, NovaEV, wants to expand to the {country_data['Country']} market.

Market context data:
- EV Adoption Rate: {country_data['EV_Adoption']}%
- Vehicle Import Tariffs: {country_data['Tariffs']}%
- Charging Infrastructure: {country_data['Charging_Stations']} stations
- Public Sentiment towards Chinese Brands: Score {country_data['China_Sentiment']}/1
- Market Size Index: {country_data['Market_Size']} / 10

NovaEV's Product Profile:
- Type: {product_type}
- Price point: {price_point}
- Target: {target_demo}

Generate a GTM launch plan with:
1. Entry strategy
2. Positioning & messaging
3. Key content themes
4. Influencer/media recommendations (3+)
"""

    if st.button("🧠 Generate Strategy"):
        with st.spinner("Thinking like a strategist..."):
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a global marketing consultant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            st.success("Strategy ready!")
            st.markdown(response.choices[0].message.content)

# === TAB 3: Monitor Performance ===
with tab3:
    
    telemetry = {
        "Norway": {
            "CTR": [1.2, 1.5, 1.8, 2.2],
            "CPI": [20, 18, 15, 12],
            "Retention": [30, 35, 40, 42],
            "Media_Sentiment": [0.2, 0.25, 0.3, 0.35],
            "Engagement": [100, 120, 140, 160]
        },
        "UK": {
            "CTR": [1.0, 1.2, 1.3, 1.4],
            "CPI": [25, 24, 23, 22],
            "Retention": [25, 28, 30, 32],
            "Media_Sentiment": [0.1, 0.15, 0.18, 0.2],
            "Engagement": [90, 95, 100, 105]
        },
        "Germany": {
            "CTR": [0.8, 0.9, 1.0, 1.1],
            "CPI": [30, 29, 28, 27],
            "Retention": [20, 22, 25, 26],
            "Media_Sentiment": [0.15, 0.17, 0.18, 0.2],
            "Engagement": [80, 85, 87, 90]
        }
    }

    kpi_options = ["CTR (Click Through Rate)", "CPI (Cost per Install)",
                   "Retention", "Media Sentiment", "Engagement"]
    selected_kpi = st.selectbox("Select KPI to visualize:", kpi_options)

    kpi_map = {
        "CTR (Click Through Rate)": "CTR",
        "CPI (Cost per Install)": "CPI",
        "Retention": "Retention",
        "Media Sentiment": "Media_Sentiment",
        "Engagement": "Engagement"
    }
    metric = kpi_map[selected_kpi]

    fig_kpi = go.Figure()
    for region, stats in telemetry.items():
        fig_kpi.add_trace(go.Scatter(
            x=["Week 1", "Week 2", "Week 3", "Week 4"],
            y=stats[metric],
            name=region
        ))
    fig_kpi.update_layout(title=f"{selected_kpi} by Region", yaxis_title=selected_kpi)

    # Layout side by side
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig_kpi, use_container_width=True)
    with col2:
        st.subheader("Strategy Feedback")
        for region, stats in telemetry.items():
            trend = stats[metric][-1] - stats[metric][-2]
            if (metric in ["CTR", "Retention", "Media_Sentiment", "Engagement"] and trend > 0.3) or \
               (metric == "CPI" and trend < -2):
                note = "📈 Great momentum – double down on current messaging."
            elif (metric in ["CTR", "Retention", "Media_Sentiment", "Engagement"] and trend < 0.1) or \
                 (metric == "CPI" and trend > 1):
                note = "⚠️ Underwhelming – revise creative and reassess influencers."
            else:
                note = "✅ Stable – maintain course, watch for regional shifts."
            st.markdown(f"**{region}:** {note}")
