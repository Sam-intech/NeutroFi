import requests
import json
import os


class FundamentalAnalystAgent:
    def __init__(
        self, coin_id: str, gemini_api_key: str = None, coingecko_api_key: str = None
    ):
        self.coin_id = coin_id
        self.gemini_api_key = gemini_api_key
        self.coingecko_api_key = coingecko_api_key
        self.base_url = "https://api.coingecko.com/api/v3"

        self.data = {}

    def fetch_data(self):
        """Fetch fundamental data using CoinGecko Demo API key."""
        params = {"localization": "false", "x_cg_demo_api_key": self.coingecko_api_key}

        try:
            coin_url = f"{self.base_url}/coins/{self.coin_id}"
            tickers_url = f"{self.base_url}/coins/{self.coin_id}/tickers"

            coin_resp = requests.get(coin_url, params=params)
            tickers_resp = requests.get(
                tickers_url, params={"x_cg_demo_api_key": self.coingecko_api_key}
            )

            if coin_resp.status_code != 200:
                print(
                    f"[❌] Coin data failed: {coin_resp.status_code} - {coin_resp.text}"
                )
                return
            if tickers_resp.status_code != 200:
                print(f"[⚠️] Ticker data failed: {tickers_resp.status_code}")

            coin_data = coin_resp.json()
            tickers_data = tickers_resp.json()

            self.data = {
                "Name": coin_data.get("name"),
                "Symbol": coin_data.get("symbol", "").upper(),
                "Market Cap (USD)": coin_data.get("market_data", {})
                .get("market_cap", {})
                .get("usd"),
                "Circulating Supply": coin_data.get("market_data", {}).get(
                    "circulating_supply"
                ),
                "Total Supply": coin_data.get("market_data", {}).get("total_supply"),
                "TVL (USD)": coin_data.get("market_data", {}).get("total_value_locked"),
                "Token Categories": coin_data.get("categories"),
                "Token Platforms": coin_data.get("platforms"),
                "Exchange Listings Count": len(tickers_data.get("tickers", [])),
            }

        except Exception as e:
            print(f"[❌] Exception fetching data: {e}")
            self.data = {}

    def print_raw_report(self):
        if not self.data:
            print("No data available. Run fetch_data() first.")
            return
        print("\n📊 Fundamental Metrics Report (Public Data Only):")
        for k, v in self.data.items():
            print(f"{k}: {v}")

    def generate_summary(self):
        if not self.gemini_api_key:
            print("[⚠️] Gemini API key not provided. Skipping summary.")
            return

        if not self.data:
            print("[⚠️] No data to summarize.")
            return

        prompt = (
            f"Here is public fundamental data for a cryptocurrency project:\n\n"
            f"{json.dumps(self.data, indent=2)}\n\n"
            f"Generate a concise summary of this coin’s fundamentals in professional tone."
        )

        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.gemini_api_key,
        }

        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                headers=headers,
                data=json.dumps(payload),
            )
            result = response.json()

            if "candidates" in result:
                summary = result["candidates"][0]["content"]["parts"][0]["text"]
                print("\n📝 Gemini Summary:\n" + summary)
            else:
                print("[❌] Gemini API returned no candidates.")
                print("Response:", json.dumps(result, indent=2))

        except Exception as e:
            print("[❌] Gemini summary failed:", e)
            print("Response:", response.text)


# 🔍 Example Run
if __name__ == "__main__":
    GEMINI_API_KEY = "AIzaSyAE9Igl3apFwKIcUTxZJKQfSOsB7-dAwmo"
    COINGECKO_API_KEY = "CG-udysTCRtHHSJHV9QbzKh1vcN"

    agent = FundamentalAnalystAgent(
        coin_id="ethereum",
        gemini_api_key=GEMINI_API_KEY,
        coingecko_api_key=COINGECKO_API_KEY,
    )

    agent.fetch_data()
    agent.print_raw_report()
    agent.generate_summary()
