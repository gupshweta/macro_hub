import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from state import AgentState
import json
import os

def get_active_ticker(symbol, category):
    """Finds the active contract for futures or returns the stock ticker."""
    if category == "EQUITIES" or symbol in ["LIT", "NVDA", "AAPL", "005930.KS", "2330.TW"]: return symbol
    
    # Month codes for Futures: J(Apr), K(May), M(Jun), N(Jul), Q(Aug), U(Sep)
    months = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]
    curr_m = datetime.now().month - 1
    year = "26"

    # Try Continuous (=F), then next month
    candidates = [f"{symbol}=F", f"{symbol}{months[(curr_m+1)%12]}{year}=F"]
    
    for ticker in candidates:
        try:
            # threads=False is critical for Mac/Streamlit stability
            d = yf.download(ticker, period="1d", progress=False, threads=False)
            if not d.empty: return ticker
        except:
            continue
    return f"{symbol}=F"

def scout_market_node(state: AgentState):
    demo_mode = state.get('demo_mode', False)
    
    universe = {
        "EQUITIES": {"S&P500": "^GSPC", "Nasdaq": "^IXIC", "Dow": "^DJI", "KOSPI_200": "^KS200", "Nifty_50": "^NSEI"},
        "TECH_HUBS": {"Samsung": "005930.KS", "TSMC": "2330.TW", "Semis_SOX": "^SOX", "NVDA": "NVDA", "AAPL": "AAPL"},
        "ENERGY": {"WTI_Crude": "CL", "Brent_Crude": "BZ", "Nat_Gas": "NG", "Heating_Oil": "HO"},
        "METALS": {"Gold": "GC", "Silver": "SI", "Platinum": "PL", "Palladium": "PA", "Copper": "HG", "Lithium": "LIT", "Aluminum": "ALI"},
        "RATES_FX": {"US_10Y": "^TNX", "USDKRW": "KRW=X", "DXY": "DX-Y.NYB", "EURUSD": "EUR=X", "GBPUSD": "GBP=X"}
    }
    
    if demo_mode:
        print("--- 🛰️ Scout: Demo Mode - Loading Static Data ---")
        selected_scenario = state.get('selected_scenario', '2008 Financial Crisis')
        selected_date = state.get('selected_date', None)
        
        # Load scenarios
        with open('data/news_scenarios.json', 'r') as f:
            scenarios = json.load(f)['scenarios']
        
        scenario = next((s for s in scenarios if s['name'] == selected_scenario), scenarios[0])
        scenario_date = selected_date if selected_date else scenario['date']
        
        # Load market data
        with open('data/market_data.json', 'r') as f:
            market_data = json.load(f)
        
        snapshot = {}
        for cat, assets in universe.items():
            cat_data = {}
            for name in assets.keys():
                if cat in market_data and name in market_data[cat]:
                    data = market_data[cat][name]
                    dates = sorted([d for d in data.keys() if d <= scenario_date])
                    if len(dates) >= 2:
                        curr_date = dates[-1]
                        prev_date = dates[-2]
                        curr = data[curr_date]['Close']
                        prev = data[prev_date]['Close']
                        change = ((curr - prev) / prev) * 100
                        cat_data[name] = {
                            "price": round(curr, 2), 
                            "pct": round(change, 2), 
                            "status": "LIVE", 
                            "t": assets[name]
                        }
            if cat_data:
                snapshot[cat] = cat_data
        
        return {"market_data": snapshot}
    
    else:
        print("--- 🛰️ Scout: Live yFinance Sync ---")
        
        snapshot = {}
        for cat, assets in universe.items():
            cat_data = {}
            for name, sym in assets.items():
                ticker = get_active_ticker(sym, cat)
                try:
                    df = yf.download(ticker, period="5d", interval="1d", progress=False, threads=False)
                    if df is None or df.empty or len(df) < 2: continue
                    
                    df = df.dropna()
                    # Use float() to ensure we have scalars, not Series
                    curr = float(df['Close'].iloc[-1])
                    prev = float(df['Close'].iloc[-2])
                    vol = float(df['Volume'].iloc[-1]) if 'Volume' in df.columns else 1.0

                    change = ((curr - prev) / prev) * 100
                    # Detect holiday status (e.g., Ram Navami today)
                    status = "CLOSED" if (vol == 0 or curr == prev) else "LIVE"
                    
                    cat_data[name] = {
                        "price": round(curr, 2), 
                        "pct": round(change, 2), 
                        "status": status, 
                        "t": ticker
                    }
                except:
                    continue
            if cat_data:
                snapshot[cat] = cat_data
                    
        return {"market_data": snapshot}