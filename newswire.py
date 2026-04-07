import re
from langchain_community.tools import DuckDuckGoSearchResults
from state import AgentState
import json

# def news_wire_node(state: AgentState):
#     print("--- 📡 News Wire: Investigating Catalysts ---")
#     search = DuckDuckGoSearchResults(backend="auto", num_results=10)
#     market = state["market_data"]
#     bullets = []

#     # Flatten assets to find top movers
#     flat = []
#     for cat in market.values():
#         for n, d in cat.items():
#             flat.append((n, d))
            
#     targets = sorted(flat, key=lambda x: abs(x[1]['pct']), reverse=True)[:4]

#     for name, data in targets:
#         query = f"why is {name} {data['t']} price moving today financial news"
#         try:
#             raw = search.invoke(query)
#             # Basic string cleaning for the dashboard
#             clean = str(raw).replace("[", "").replace("]", "")[:350]
#             bullets.append(f"**{name} ({data['pct']}%):** {clean}...")
#         except:
#             continue

#     return {"news_headlines": bullets}

def news_wire_node(state: AgentState):
    demo_mode = state.get('demo_mode', False)
    
    if demo_mode:
        print("--- 📡 News Wire: Demo Mode - Loading Static News ---")
        selected_scenario = state.get('selected_scenario', '2008 Financial Crisis')
        selected_date = state.get('selected_date', None)
        
        # Load scenarios
        with open('data/news_scenarios.json', 'r') as f:
            scenarios = json.load(f)['scenarios']
        
        scenario = next((s for s in scenarios if s['name'] == selected_scenario), scenarios[0])
        news_items = scenario['news']
        
        # Filter news up to selected date if provided
        if selected_date:
            filtered_news = []
            for item in news_items:
                if isinstance(item, dict):
                    headline = item['headline']
                else:
                    headline = item  # item is a string
                
                match = re.search(r'\[(\d{4}-\d{2}-\d{2})\]', headline)
                if match and match.group(1) <= selected_date:
                    filtered_news.append(item)
            news_items = filtered_news
        
        # Format as headlines with summaries and sources
        headlines = []
        for item in news_items:
            if isinstance(item, dict):
                formatted = f"**{item['headline']}**: {item['summary']} (Source: {item['source']})"
            else:
                formatted = f"**{item}**"  # item is just a headline string
            headlines.append(formatted)
        
        return {"news_headlines": headlines}
    
    else:
        print("--- 📡 News Wire: Live Search ---")
        search = DuckDuckGoSearchResults(backend="auto", num_results=10)
        market = state["market_data"]
        
        # Flatten and find only the MAX mover
        flat = [(n, d) for cat in market.values() for n, d in cat.items()]
        if not flat: return {"news_headlines": []}
        
        top_mover = max(flat, key=lambda x: abs(x[1]['pct']))

        # Only spend credits if the move is > 1.0%
        if abs(top_mover[1]['pct']) > 1.0:
            query = f"why is {top_mover[0]} moving today"
            try:
                raw = search.invoke(query)
                return {"news_headlines": [f"**{top_mover[0]}**: {str(raw)[:200]}"]}
            except: pass
            
        return {"news_headlines": ["No significant volatility detected. Credits saved."]}