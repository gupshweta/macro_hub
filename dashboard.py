import streamlit as st
from main import app # Ensure your LangGraph 'app' is imported here
from datetime import datetime
import json
import time

st.set_page_config(layout="wide", page_title="Macro Hub")

# Load scenarios
try:
    with open('data/news_scenarios.json', 'r') as f:
        scenarios_data = json.load(f)
    scenarios = {s['name']: s for s in scenarios_data['scenarios']}
except:
    scenarios = {}

# Sidebar for controls
with st.sidebar:
    st.title("🛰️ Control Center")
    
    demo_mode = st.checkbox("Demo Mode", value=True)
    
    selected_scenario = None
    selected_date = None
    if demo_mode:
        scenario_names = list(scenarios.keys())
        selected_scenario = st.selectbox("Select Scenario", scenario_names, index=0)
        if selected_scenario and selected_scenario in scenarios:
            st.markdown(f"**Blurb:** {scenarios[selected_scenario]['blurb']}")
            
            # Extract date range from news headlines
            import re
            news_dates = []
            for item in scenarios[selected_scenario]['news']:
                if isinstance(item, dict):
                    headline = item['headline']
                else:
                    headline = item  # item is a string
                
                match = re.search(r'\[(\d{4}-\d{2}-\d{2})\]', headline)
                if match:
                    news_dates.append(match.group(1))
            
            if news_dates:
                min_date_str = min(news_dates)
                max_date_str = max(news_dates)
                min_date = datetime.strptime(min_date_str, "%Y-%m-%d").date()
                max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
                selected_date = st.slider(
                    "Select Date",
                    min_value=min_date,
                    max_value=max_date,
                    value=max_date,
                    format="YYYY-MM-DD"
                )
    
    # Check if date or scenario changed since last sync
    current_config = f"{selected_scenario}_{selected_date}"
    last_config = st.session_state.get('last_config', '')
    
    config_changed = current_config != last_config
    
    # Check cooldown period (prevent rapid clicks)
    last_click = st.session_state.get('last_click_time', 0)
    cooldown_seconds = 5  # 5 second cooldown
    can_click = (time.time() - last_click) > cooldown_seconds
    
    if st.button("🔄 Sync Global Tapes", use_container_width=True, disabled=not can_click):
        if can_click:
            st.session_state.last_click_time = time.time()
            # Prepare initial state
            initial_input = {
                "market_data": {}, 
                "news_headlines": [], 
                "signals": [],
                "analysis": {},
                "current_focus": "Global Macro",
                "demo_mode": demo_mode
            }
            if demo_mode and selected_scenario:
                initial_input["selected_scenario"] = selected_scenario
                if selected_date:
                    initial_input["selected_date"] = selected_date.strftime("%Y-%m-%d")
            
            # Trigger the full LangGraph workflow
            res = app.invoke(initial_input)
            st.session_state.res = res
            st.session_state.last_config = current_config

st.title("🌍 Global Macro Command Center")

# Show cooldown status
if not can_click:
    remaining = int(cooldown_seconds - (time.time() - last_click))
    st.info(f"⏳ Please wait {remaining} seconds before syncing again...")

# Check if we need to show sync message
if config_changed and demo_mode and 'res' in st.session_state:
    st.warning("⚠️ Date or scenario changed! Click 'Sync Global Tapes' to update the analysis with the new settings.")

if "res" in st.session_state:
    res = st.session_state.res
    tab1, tab2 = st.tabs(["📊 Market & 'The Why'", "🧠 Alpha Intelligence"])

    with tab1:
        # Loop through categories found by the Scout
        for category, assets in res["market_data"].items():
            num_cols = len(assets)
            
            # SAFETY CHECK: Prevent StreamlitInvalidColumnSpecError (0 columns)
            if num_cols > 0:
                st.subheader(f"📍 {category.replace('_', ' ')}")
                cols = st.columns(num_cols)
                
                for i, (name, data) in enumerate(assets.items()):
                    icon = "🌙" if data['status'] == "CLOSED" else "🟢"
                    with cols[i]:
                        st.metric(
                            label=f"{icon} {name}", 
                            value=f"{data['price']}", 
                            delta=f"{data['pct']}%"
                        )
        
        st.divider()
        st.header("📡 News Wire: Key Move Drivers")
        if res.get("news_headlines"):
            for bullet in res["news_headlines"]:
                st.markdown(bullet)
        else:
            st.info("No high-volatility news catalysts detected.")

    with tab2:
        st.header("🧠 Strategist: Unpriced Analysis")
        if res.get("signals"):
            for s in res["signals"]:
                st.success(s)
        else:
            st.warning("No unpriced signals generated in this cycle.")
else:
    st.info("Click 'Sync Global Tapes' in the sidebar to begin.")