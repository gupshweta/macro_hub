from typing import Annotated, TypedDict, List, Dict, Any
import operator

class AgentState(TypedDict):
    market_data: Dict[str, Any]
    news_headlines: Annotated[List[str], operator.add]
    analysis: Dict[str, Any]
    signals: List[str]
    current_focus: str
    demo_mode: bool
    selected_scenario: str
    selected_date: str