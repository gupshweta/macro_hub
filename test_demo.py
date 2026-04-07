from main import app

# Test demo mode
initial_input = {
    "market_data": {}, 
    "news_headlines": [], 
    "signals": [],
    "analysis": {},
    "current_focus": "Global Macro",
    "demo_mode": True,
    "selected_scenario": "2008 Financial Crisis"
}

res = app.invoke(initial_input)
print("Market Data:", res.get("market_data"))
print("News Headlines:", res.get("news_headlines"))
print("Signals:", res.get("signals"))