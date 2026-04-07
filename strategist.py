from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from state import AgentState

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI # New Import
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState

load_dotenv()

def strategist_node(state: AgentState):
    print("--- 🧠 Strategist (Gemini): Calculating Unpriced Alpha ---")
    
    # We use Gemini 3 Flash: it's free and perfect for reasoning
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview", 
        temperature=0,
        google_api_key="AIzaSyC3vIJXkAkAadY2RSDdxhnN5LvX_ZfbHwM"
    )
    
    market_summary = str(state['market_data'])
    news_summary = "\n".join(state['news_headlines'])
    
    prompt = ChatPromptTemplate.from_template("""
        You are a Senior Global Macro Strategist. Compare the Market Data and News.
        Identify "Unpriced" gaps where news is big but price hasn't moved.
        
        DATA: {market_data}
        NEWS: {news_headlines}
        
        Return a list of Alpha Signals.
    """)
    
    chain = prompt | llm
    response = chain.invoke({"market_data": market_summary, "news_headlines": news_summary})
    
    return {"signals": [response.content]}