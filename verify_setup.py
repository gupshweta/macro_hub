import sys
import pandas as pd
import yfinance as yf
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 1. Define a simple State for LangGraph
class AgentState(TypedDict):
    status: str
    data_points: int

def test_node(state: AgentState):
    print("--- LangGraph Node Executing ---")
    return {"status": "Active"}

# 2. Build a minimal Graph
workflow = StateGraph(AgentState)
workflow.add_node("tester", test_node)
workflow.add_edge(START, "tester")
workflow.add_edge("tester", END)
app = workflow.compile()

def run_verification():
    print(f"Python Version: {sys.version.split()[0]}")
    print("-" * 30)
    
    # Test Pandas
    df = pd.DataFrame({"Test": [1, 2, 3]})
    print(f"✅ Pandas: Version {pd.__version__} (DataFrame created)")

    # Test yfinance (Fetching KOSPI as a test)
    try:
        kospi = yf.Ticker("^KS11")
        price = kospi.fast_info['last_price']
        print(f"✅ yfinance: Success! Current KOSPI: {price:.2f}")
    except Exception as e:
        print(f"❌ yfinance: Failed to fetch data. Error: {e}")

    # Test LangGraph
    try:
        result = app.invoke({"status": "Inert", "data_points": 0})
        if result["status"] == "Active":
            print("✅ LangGraph: Graph compiled and executed successfully!")
    except Exception as e:
        print(f"❌ LangGraph: Failed. Error: {e}")

if __name__ == "__main__":
    run_verification()