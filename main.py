from typing import Annotated, TypedDict, List, Dict, Any
import operator
import json

from langgraph.graph import END, START, StateGraph
from state import AgentState
from newswire import news_wire_node
from scout import scout_market_node
from strategist import strategist_node

# --- STEP 1: Define the Conditional Logic (The Credit Saver) ---
def should_analyze(state: AgentState):
    """
    Check if the market moved enough to justify spending Gemini API credits.
    """
    demo_mode = state.get('demo_mode', False)
    if demo_mode:
        print("--- 🟢 Demo Mode: Always Triggering Full Workflow ---")
        return "continue_to_llm"
    
    market = state.get("market_data", {})
    
    # Flatten all pct changes from the nested dictionary
    all_moves = []
    for category in market.values():
        for asset_data in category.values():
            # Support both 'pct' and 'pct_change' keys depending on scout version
            val = asset_data.get('pct') or asset_data.get('pct_change', 0)
            all_moves.append(abs(float(val)))
    
    # Threshold: Only trigger LLM if a move > 0.75% is detected
    significant = any(move > 0.75 for move in all_moves)
    
    if significant:
        print("--- 🟢 Volatility Detected: Triggering LLM Nodes ---")
        return "continue_to_llm"
    
    print("--- 🌙 Market Quiet: Skipping LLM to Save Credits ---")
    return "skip_to_end"

# --- STEP 2: Build the Graph ---
workflow = StateGraph(AgentState)

# Add your nodes
workflow.add_node("scout", scout_market_node)
workflow.add_node("newswire", news_wire_node)
workflow.add_node("strategist", strategist_node)

# --- STEP 3: Define the Logic Flow ---
workflow.add_edge(START, "scout")

# Conditional Routing: Scout -> News (only if moving) OR Scout -> END (if quiet)
workflow.add_conditional_edges(
    "scout",
    should_analyze,
    {
        "continue_to_llm": "newswire",
        "skip_to_end": END
    }
)

# Linear flow for LLM nodes to avoid parallel rate-limit hits
workflow.add_edge("newswire", "strategist")
workflow.add_edge("strategist", END)

# --- STEP 4: Compile ---
app = workflow.compile()

# --- STEP 5: Execution Logic (for Terminal testing) ---
if __name__ == "__main__":
    print("\n🚀 INITIALIZING CRUNCH-MODE AGENTIC RUN...")
    
    # Initialize state
    initial_input = {
        "market_data": {}, 
        "news_headlines": [], 
        "signals": [],
        "analysis": {},
        "current_focus": "Global Macro"
    }
    
    try:
        final_state = app.invoke(initial_input)

        print("\n" + "="*50)
        print("🎯 STRATEGIST'S UNPRICED ALPHA REPORT")
        print("="*50)
        
        if final_state.get("signals"):
            for signal in final_state["signals"]:
                print(f"• {signal}")
        else:
            print("No signals generated (System skipped LLM nodes to save quota).")

        print("\n--- 🔍 LATEST SCOUT DATA ---")
        print(json.dumps(final_state["market_data"], indent=2))
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        if "429" in str(e):
            print("💡 PRO-TIP: You hit your Gemini Daily Quota. Switch API keys or wait for reset.")