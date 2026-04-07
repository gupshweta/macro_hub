import yfinance as yf
import json
from datetime import datetime
import os

# Expanded universe
universe = {
    "EQUITIES": {"S&P500": "^GSPC", "Nasdaq": "^IXIC", "Dow": "^DJI", "KOSPI_200": "^KS200", "Nifty_50": "^NSEI"},
    "TECH_HUBS": {"Samsung": "005930.KS", "TSMC": "2330.TW", "Semis_SOX": "^SOX", "NVDA": "NVDA", "AAPL": "AAPL"},
    "ENERGY": {"WTI_Crude": "CL", "Brent_Crude": "BZ", "Nat_Gas": "NG", "Heating_Oil": "HO"},
    "METALS": {"Gold": "GC", "Silver": "SI", "Platinum": "PL", "Palladium": "PA", "Copper": "HG", "Lithium": "LIT", "Aluminum": "ALI"},
    "RATES_FX": {"US_10Y": "^TNX", "USDKRW": "KRW=X", "DXY": "DX-Y.NYB", "EURUSD": "EUR=X", "GBPUSD": "GBP=X"}
}

def get_active_ticker(symbol, category):
    """Finds the active contract for futures or returns the stock ticker."""
    if category == "EQUITIES" or symbol in ["LIT", "NVDA", "AAPL", "005930.KS", "2330.TW"]: return symbol
    
    # For futures, try continuous
    candidates = [f"{symbol}=F"]
    for ticker in candidates:
        try:
            d = yf.download(ticker, period="1d", progress=False, threads=False)
            if not d.empty: return ticker
        except:
            continue
    return symbol  # fallback

market_data = {}

for cat, assets in universe.items():
    print(f"Downloading {cat}...")
    cat_data = {}
    for name, sym in assets.items():
        ticker = get_active_ticker(sym, cat)
        try:
            # Download from 2010 to 2026 to reduce size
            df = yf.download(ticker, start="2010-01-01", end="2026-12-31", progress=False, threads=False)
            if df.empty:
                print(f"  {name}: No data")
                continue
            df = df.dropna()
            # Convert to dict with date as key
            data = {}
            for date, row in df.iterrows():
                data[str(date.date())] = {
                    "Open": float(row['Open']),
                    "High": float(row['High']),
                    "Low": float(row['Low']),
                    "Close": float(row['Close']),
                    "Volume": int(row['Volume']) if 'Volume' in row else 0
                }
            cat_data[name] = data
            print(f"  {name}: {len(data)} days")
        except Exception as e:
            print(f"  {name}: Error {e}")
    market_data[cat] = cat_data

# Save to JSON
with open("data/market_data.json", "w") as f:
    json.dump(market_data, f, indent=2)

print("Market data downloaded and saved.")