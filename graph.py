from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage
from agents.news_agent import create_crypto_news_analyst
from agents.fundamental_analysis_agent import create_fundamentals_analyst
from agents.technical_anlyst_agent import create_technical_analyst
from agents.social_media_agent import create_sentiment_analyst
from agents.research_analyst_agent import create_research_analyst_agent
from agents.risk_management_agent import create_risk_manager_agent
from toolkit.crypto_toolkit import MyCryptoToolKit
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# 🔐 API KEYS (Use .env or config file in production)
GEMINI_KEY = "AIzaSyD50Yl53Z26HaFNbt1f-68aemVUBCILk1c"
CRYPTOPANIC_KEY = "48db7f2185db91ce057c9ecde34b890ffe00a61f"
COINGECKO_KEY = "CG-udysTCRtHHSJHV9QbzKh1vcN"
REDDIT_CLIENT_ID = "YQqxZkPnVQIrQmETXX5Ptg"
REDDIT_SECRET = "kR7VeU5tHNzZ-WPOwCYkEpE1zdDK5w"
REDDIT_USER_AGENT = "sentiment"

# 🔧 LLM
from langchain_google_genai import ChatGoogleGenerativeAI

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GEMINI_KEY,
        temperature=0.3,
    )
except Exception as e:
    print(f"[ERROR] Failed to initialize Gemini LLM: {e}")
    exit(1)

# 🧰 TOOLKIT
try:
    toolkit = MyCryptoToolKit(
        cryptopanic_key=CRYPTOPANIC_KEY,
        coingecko_key=COINGECKO_KEY,
        reddit_id=REDDIT_CLIENT_ID,
        reddit_secret=REDDIT_SECRET,
        reddit_agent=REDDIT_USER_AGENT,
    )
except Exception as e:
    print(f"[ERROR] Failed to initialize toolkit: {e}")
    exit(1)


# Define state schema
class AgentState(TypedDict):
    coin: str
    trade_date: str
    messages: List[BaseMessage]
    news_report: Optional[str]
    fundamentals_report: Optional[str]
    technical_report: Optional[str]
    sentiment_report: Optional[str]
    research_summary: Optional[str]
    research_decision: Optional[str]
    research_confidence: Optional[float]
    risk_notes: Optional[str]
    final_recommendation: Optional[str]


# Initialize graph
workflow = StateGraph(AgentState)


# Define nodes with message reset
def news_node(state):
    state["messages"] = [
        HumanMessage(content=f"Fetch and analyze recent news for {state['coin']}.")
    ]
    return create_crypto_news_analyst(llm, toolkit)(state)


def fundamentals_node(state):
    state["messages"] = [
        HumanMessage(content=f"Fetch and analyze fundamentals for {state['coin']}.")
    ]
    return create_fundamentals_analyst(llm, toolkit)(state)


def technical_node(state):
    state["messages"] = [
        HumanMessage(
            content=f"Fetch and analyze technical indicators for {state['coin']}."
        )
    ]
    return create_technical_analyst(llm, toolkit)(state)


def sentiment_node(state):
    state["messages"] = [
        HumanMessage(
            content=f"Fetch and analyze social media sentiment for {state['coin']}."
        )
    ]
    return create_sentiment_analyst(llm, toolkit)(state)


def research_node(state):
    state["messages"] = [
        HumanMessage(content=f"Generate research report for {state['coin']}.")
    ]
    return create_research_analyst_agent(llm)(state)


def risk_node(state):
    state["messages"] = [
        HumanMessage(content=f"Conduct risk analysis for {state['coin']}.")
    ]
    return create_risk_manager_agent(llm)(state)


# === Build Graph ===
def trading_graph(llm, toolkit):
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("news", news_node)
    workflow.add_node("fundamentals", fundamentals_node)
    workflow.add_node("technical", technical_node)
    workflow.add_node("sentiment", sentiment_node)
    workflow.add_node("research", research_node)
    workflow.add_node("risk", risk_node)

    # Edges (sequential)
    workflow.add_edge("news", "fundamentals")
    workflow.add_edge("fundamentals", "technical")
    workflow.add_edge("technical", "sentiment")
    workflow.add_edge("sentiment", "research")
    workflow.add_edge("research", "risk")
    workflow.add_edge("risk", END)

    # Set entry point
    workflow.set_entry_point("news")

    return workflow.compile()


graph = trading_graph(llm, toolkit)
