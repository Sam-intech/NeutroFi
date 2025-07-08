import requests
import json
from datetime import datetime


class FinanceNewsAnalystAgent:
    def __init__(self, cryptopanic_api_key: str, gemini_api_key: str = None):
        self.api_key = cryptopanic_api_key
        self.gemini_api_key = gemini_api_key
        self.base_url = "https://cryptopanic.com/api/developer/v2/posts/"

    def fetch_news(self, currencies=None, filter_type="hot", kind="news", public=True):
        """Fetch news for specific coin(s) or market-wide if currencies is None."""
        params = {
            "auth_token": self.api_key,
            "filter": filter_type,
            "kind": kind,
        }
        if public:
            params["public"] = "true"
        if currencies:
            params["currencies"] = currencies

        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code != 200:
                print(f"[❌] API Error {response.status_code}: {response.text}")
                return []

            results = response.json().get("results", [])
            parsed_news = []

            for post in results:
                title = post.get("title", "").strip()
                published = post.get("published_at")
                url = (
                    post.get("url")
                    or post.get("original_url")
                    or "https://cryptopanic.com/"
                )
                source = post.get("source", {}).get("title", "Unknown")
                if not title or not published:
                    continue
                parsed_news.append(
                    {
                        "Title": title,
                        "Source": source,
                        "Published": published,
                        "URL": url,
                    }
                )
            return parsed_news

        except Exception as e:
            print(f"[❌] Exception while fetching news: {e}")
            return []

    def print_news_digest(self, news_data, label="News"):
        if not news_data:
            print(f"No {label.lower()} available.")
            return

        print(f"\n📰 {label} Digest ({len(news_data)} items):\n")
        for i, item in enumerate(news_data, 1):
            pub_time = datetime.fromisoformat(
                item["Published"].replace("Z", "+00:00")
            ).strftime("%b %d %Y %H:%M UTC")
            print(f"{i}. {item['Title']} ({item['Source']})")
            print(f"   Published: {pub_time}")
            print(f"   🔗 {item['URL']}\n")

    def generate_summary(self, news_data, label="Market"):
        if not self.gemini_api_key:
            print(f"[⚠️] Gemini API key not set. Skipping {label} summary.")
            return

        if not news_data:
            print(f"[⚠️] No {label.lower()} news to summarize.")
            return

        headlines = "\n".join(
            [f"- {item['Title']} ({item['Source']})" for item in news_data]
        )

        prompt = (
            f"The following are the most important {label.lower()} crypto news headlines:\n\n{headlines}\n\n"
            f"Summarize the overall market sentiment and highlight any risks or opportunities."
        )

        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.gemini_api_key,
        }

        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            res = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                headers=headers,
                data=json.dumps(payload),
            )
            result = res.json()
            if "candidates" in result:
                summary = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"\n📈 Gemini {label} Summary:\n" + summary)
            else:
                print(f"[❌] Gemini returned no content for {label}.")
        except Exception as e:
            print(f"[❌] Gemini {label} summary failed: {e}")


# ========== Example Usage ==========
if __name__ == "__main__":
    CRYPTOPANIC_API_KEY = "48db7f2185db91ce057c9ecde34b890ffe00a61f"
    GEMINI_API_KEY = "AIzaSyAE9Igl3apFwKIcUTxZJKQfSOsB7-dAwmo"  # Optional

    agent = FinanceNewsAnalystAgent(CRYPTOPANIC_API_KEY, GEMINI_API_KEY)

    # Specific coin news
    eth_news = agent.fetch_news(currencies="ETH")
    agent.print_news_digest(eth_news, label="Ethereum News")
    agent.generate_summary(eth_news, label="Ethereum")

    # Market-wide news
    market_news = agent.fetch_news(currencies=None)
    agent.print_news_digest(market_news, label="Market News")
    agent.generate_summary(market_news, label="Market")
