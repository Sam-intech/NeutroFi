# main.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from toolkit.crypto_toolkit import MyCryptoToolKit
from agents.news_agent import create_crypto_news_analyst
from agents.fundamental_analysis_agent import create_fundamentals_analyst
from agents.technical_anlyst_agent import create_technical_analyst
from agents.social_media_agent import create_sentiment_analyst

# 🔐 API KEYS (Use .env or config file in production)
GEMINI_KEY = "AIzaSyD9AIb520LwBOthNsU7djw-MLGfOj1QTU0"
CRYPTOPANIC_KEY = "48db7f2185db91ce057c9ecde34b890ffe00a61f"
COINGECKO_KEY = "CG-udysTCRtHHSJHV9QbzKh1vcN"
REDDIT_CLIENT_ID = "YQqxZkPnVQIrQmETXX5Ptg"
REDDIT_SECRET = "kR7VeU5tHNzZ-WPOwCYkEpE1zdDK5w"
REDDIT_USER_AGENT = "sentiment"

# 🔧 LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_KEY,
    temperature=0.3,
)

# 🧰 TOOLKIT
toolkit = MyCryptoToolKit(
    cryptopanic_key=CRYPTOPANIC_KEY,
    coingecko_key=COINGECKO_KEY,
    reddit_id=REDDIT_CLIENT_ID,
    reddit_secret=REDDIT_SECRET,
    reddit_agent=REDDIT_USER_AGENT,
)

# === Define shared state
state = {
    "coin": "bitcoin",
    "company_of_interest": "bitcoin",  # Some agents use this key
    "trade_date": "2025-07-25",
    "messages": [HumanMessage(content="Analyze  for this coin.")],
}

# === Run individual agents

# ## 1. 📊 FUNDAMENTALS
# print("\n🔍 Running Fundamental Analyst...")
# fundamentals_agent = create_fundamentals_analyst(llm, toolkit)
# fund_result = fundamentals_agent(state)
# print("\n📊 FUNDAMENTALS REPORT:\n")
# print(fund_result["fundamentals_report"])

## 2. 📰 NEWS
print("\n🔍 Running News Analyst...")
news_agent = create_crypto_news_analyst(llm, toolkit)
news_result = news_agent(state)
print("\n📰 NEWS REPORT:\n")
print(news_result.content)


# ## 3. 📉 TECHNICAL
# print("\n🔍 Running Technical Analyst...")
# technical_agent = create_technical_analyst(llm, toolkit)
# tech_result = technical_agent(state)
# print("\n📉 TECHNICAL REPORT:\n")
# print(tech_result["technical_report"])

# ## 4. 💬 SENTIMENT
# print("\n🔍 Running Sentiment Analyst...")
# sentiment_agent = create_sentiment_analyst(llm, toolkit)
# sent_result = sentiment_agent(state)
# print("\n💬 SENTIMENT REPORT:\n")
# print(sent_result["sentiment_report"])
