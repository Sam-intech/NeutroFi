import requests
import pandas as pd
import pandas_ta as ta


class TechnicalAnalystAgent:
    def __init__(self, coingecko_api_key: str = None):
        self.coingecko_api_key = coingecko_api_key
        self.base_url = "https://api.coingecko.com/api/v3"
        # Map common coin names to CoinGecko IDs
        self.coin_id_map = {
            "bitcoin": "bitcoin",
            "btc": "bitcoin",
            "ethereum": "ethereum",
            "eth": "ethereum",
            "solana": "solana",
            "sol": "solana",
            "ripple": "ripple",
            "xrp": "ripple",
            "cardano": "cardano",
            "ada": "cardano",
        }

    def fetch_ohlc_data(self, coin_id="bitcoin", vs_currency="usd", days=30):
        """Fetch OHLC data from CoinGecko."""
        coin_id = self.coin_id_map.get(coin_id.lower(), coin_id.lower())
        url = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": vs_currency,
            "days": days,
            "x_cg_demo_api_key": self.coingecko_api_key,
        }
        headers = {"accept": "application/json"}

        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code != 200:
                return {"error": f"Failed to fetch OHLC: {response.status_code}"}

            data = response.json()
            prices = data.get("prices", [])
            if not prices:
                return {"error": "No OHLC price data found."}

            df = pd.DataFrame(prices, columns=["timestamp", "close"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)

            return df
        except Exception as e:
            return {"error": f"Failed to fetch OHLC data: {str(e)}"}

    def compute_indicators(self, df):
        """Compute technical indicators (RSI, MACD, Bollinger Bands)."""
        try:
            indicators = {}

            # RSI
            df["rsi"] = ta.rsi(df["close"], length=14)
            indicators["rsi"] = (
                round(df["rsi"].iloc[-1], 2) if not df["rsi"].isna().iloc[-1] else None
            )

            # MACD
            macd = ta.macd(df["close"])
            indicators["macd"] = (
                round(macd["MACD_12_26_9"].iloc[-1], 4)
                if not macd["MACD_12_26_9"].isna().iloc[-1]
                else None
            )
            indicators["macd_signal"] = (
                round(macd["MACDs_12_26_9"].iloc[-1], 4)
                if not macd["MACDs_12_26_9"].isna().iloc[-1]
                else None
            )

            # Bollinger Bands
            bb = ta.bbands(df["close"], length=20, std=2)
            indicators["bb_lower"] = (
                round(bb["BBL_20_2.0"].iloc[-1], 2)
                if not bb["BBL_20_2.0"].isna().iloc[-1]
                else None
            )
            indicators["bb_upper"] = (
                round(bb["BBU_20_2.0"].iloc[-1], 2)
                if not bb["BBU_20_2.0"].isna().iloc[-1]
                else None
            )
            indicators["bb_middle"] = (
                round(bb["BBM_20_2.0"].iloc[-1], 2)
                if not bb["BBM_20_2.0"].isna().iloc[-1]
                else None
            )

            indicators["close"] = (
                round(df["close"].iloc[-1], 2)
                if not df["close"].isna().iloc[-1]
                else None
            )

            return indicators

        except Exception as e:
            return {"error": f"Failed to compute indicators: {str(e)}"}
