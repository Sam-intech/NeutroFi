from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage
from agents.news_agent import create_crypto_news_analyst
from agents.fundamental_analysis_agent import create_fundamentals_analyst
from agents.technical_anlyst_agent import create_technical_analyst
from agents.social_media_agent import create_sentiment_analyst
from toolkit.crypto_toolkit import MyCryptoToolKit
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# 🔐 API KEYS
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
CRYPTOPANIC_KEY = os.getenv("CRYPTOPANIC_KEY")
COINGECKO_KEY = os.getenv("COINGECKO_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

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


# Initialize state
coin = "bitcoin"
trade_date = "2025-07-25"
state = {
    "coin": coin,
    "trade_date": trade_date,
    "messages": [],
    "news_report": None,
    "fundamentals_report": None,
    "technical_report": None,
    "sentiment_report": None,
}

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


# Add nodes
workflow.add_node("news", news_node)
workflow.add_node("fundamentals", fundamentals_node)
workflow.add_node("technical", technical_node)
workflow.add_node("sentiment", sentiment_node)

# Define edges (sequential execution)
workflow.add_edge("news", "fundamentals")
workflow.add_edge("fundamentals", "technical")
workflow.add_edge("technical", "sentiment")
workflow.add_edge("sentiment", END)

# Set entry point
workflow.set_entry_point("news")

# Compile and run graph
graph = workflow.compile()
result = graph.invoke(state)

# Print results
print("Final State:")
print("\n📰 NEWS REPORT:\n", result["news_report"])
print("\n📊 FUNDAMENTALS REPORT:\n", result["fundamentals_report"])
print("\n📉 TECHNICAL REPORT:\n", result["technical_report"])
print("\n💬 SENTIMENT REPORT:\n", result["sentiment_report"])
