import praw
import re
import json
import google.generativeai as genai
import requests


# 🔐 1. SET UP API KEYS
REDDIT_CLIENT_ID = "YQqxZkPnVQIrQmETXX5Ptg"
REDDIT_SECRET = "kR7VeU5tHNzZ-WPOwCYkEpE1zdDK5w"
REDDIT_USER_AGENT = "sentiment"

GEMINI_API_KEY = "AIzaSyAE9Igl3apFwKIcUTxZJKQfSOsB7-dAwmo"


# 🔌 2. CONFIGURE GEMINI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")


# 🔌 3. CONFIGURE REDDIT
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)


# 📥 FETCH REDDIT POSTS FOR COINS
def fetch_reddit_posts(coin_symbol, subreddit_list=None, limit=20):
    if subreddit_list is None:
        subreddit_list = [
            "CryptoCurrency",
            "CryptoMarkets",
            "Bitcoin",
            "ethereum",
            "altcoin",
        ]

    results = []
    for sub in subreddit_list:
        for post in reddit.subreddit(sub).search(coin_symbol, sort="new", limit=limit):
            combined = f"{post.title} {post.selftext}"
            if len(combined.strip()) > 20:
                results.append(combined)
    return results


# 🧼 CLEAN TEXTS
def clean_texts(texts):
    cleaned = []
    for text in texts:
        text = re.sub(r"http\S+|www\S+|https\S+", "", text)
        text = re.sub(r"@\w+|#\w+", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        cleaned.append(text)
    return cleaned


# 🧾 BUILD PROMPT FOR GEMINI
def build_prompt(coin_symbol, posts):
    text_block = "\n\n".join(posts[:20])
    return f"""
You are a sentiment analysis agent focused on cryptocurrency.

Analyze the following Reddit posts about the coin "{coin_symbol}". 
Classify each post as Positive, Negative, or Neutral.
Summarize key reasons behind the sentiment and give an overall conclusion.

Return ONLY the result in this JSON format (no extra explanation or markdown):
{{
  "coin": "{coin_symbol}",
  "positive_count": int,
  "negative_count": int,
  "neutral_count": int,
  "notable_reasons": [str],
  "overall_sentiment": "Positive | Neutral | Negative",
  "summary": str
}}

Posts:
{text_block}
"""


# 🌐 CALL GEMINI REST API
def call_gemini_rest(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        print("❌ Gemini API error:", response.status_code, response.text)
        return None


# 💾 OPTIONAL: SAVE TO FILE
def save_to_file(data, path="sentiment_logs/"):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{path}{data['coin']}_{date}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


# 🚀 MAIN AGENT FUNCTION
def sentiment_analyst_agent(coin_symbol="BTC"):
    print(f"📊 Running sentiment analysis for: {coin_symbol}")

    posts = fetch_reddit_posts(coin_symbol)
    if not posts:
        print("⚠️ No posts found.")
        return {"error": "No Reddit posts found."}

    cleaned = clean_texts(posts)
    prompt = build_prompt(coin_symbol, cleaned)

    raw_output = call_gemini_rest(prompt)
    if not raw_output:
        return {"error": "Gemini model failed to return output."}

    # 🧹 Remove any accidental markdown (```json)
    cleaned_output = re.sub(r"```json|```", "", raw_output.strip())

    try:
        result = json.loads(cleaned_output)
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print("⚠️ Could not parse Gemini output. Raw:\n", raw_output)
        return {"raw_output": raw_output}


# ✅ RUN FOR ONE OR MULTIPLE COINS
if __name__ == "__main__":
    for coin in ["BTC", "ETH", "SOL", "DOGE"]:
        sentiment_analyst_agent(coin)
