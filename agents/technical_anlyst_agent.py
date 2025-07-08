import requests
import pandas as pd
import pandas_ta as ta
import json

# 🔐 Replace with your Gemini API Key
GEMINI_API_KEY = "AIzaSyAE9Igl3apFwKIcUTxZJKQfSOsB7-dAwmo"


# 📊 Fetch historical price data from CoinGecko
def fetch_ohlc_data(coin_id="bitcoin", vs_currency="usd", days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": vs_currency,
        "days": days,  # DO NOT include 'interval=hourly' unless you are an enterprise user
    }
    headers = {"accept": "application/json"}

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        print("❌ Failed to fetch data:", response.status_code)
        print(response.text)
        return None

    data = response.json()
    prices = data.get("prices", [])
    if not prices:
        print("❌ No price data found.")
        return None

    df = pd.DataFrame(prices, columns=["timestamp", "close"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df


# 📈 Compute technical indicators safely
def analyze_technical_indicators(df):
    df["rsi"] = ta.rsi(df["close"], length=14)

    macd = ta.macd(df["close"])
    if macd is not None and "MACD_12_26_9" in macd and "MACDs_12_26_9" in macd:
        df["macd"] = macd["MACD_12_26_9"]
        df["macd_signal"] = macd["MACDs_12_26_9"]
    else:
        df["macd"] = df["macd_signal"] = pd.NA

    bb = ta.bbands(df["close"], length=20, std=2)
    if bb is not None and all(
        col in bb.columns for col in ["BBL_20_2.0", "BBU_20_2.0", "BBM_20_2.0"]
    ):
        df["bb_lower"] = bb["BBL_20_2.0"]
        df["bb_upper"] = bb["BBU_20_2.0"]
        df["bb_middle"] = bb["BBM_20_2.0"]
    else:
        df["bb_lower"] = df["bb_upper"] = df["bb_middle"] = pd.NA

    return df


# 📊 Generate Buy/Hold/Sell signal
def generate_signal(df):
    latest = df.iloc[-1]

    signal_details = {
        "rsi": round(latest["rsi"], 2) if pd.notna(latest["rsi"]) else None,
        "macd": round(latest["macd"], 4) if pd.notna(latest["macd"]) else None,
        "macd_signal": (
            round(latest["macd_signal"], 4) if pd.notna(latest["macd_signal"]) else None
        ),
        "close": round(latest["close"], 2),
        "bb_upper": (
            round(latest["bb_upper"], 2) if pd.notna(latest["bb_upper"]) else None
        ),
        "bb_lower": (
            round(latest["bb_lower"], 2) if pd.notna(latest["bb_lower"]) else None
        ),
    }

    signals = []

    # RSI logic
    if pd.notna(latest["rsi"]):
        if latest["rsi"] < 30:
            signals.append("RSI indicates oversold (BUY)")
        elif latest["rsi"] > 70:
            signals.append("RSI indicates overbought (SELL)")
        else:
            signals.append("RSI is neutral")
    else:
        signals.append("RSI not available")

    # MACD logic
    if pd.notna(latest["macd"]) and pd.notna(latest["macd_signal"]):
        if latest["macd"] > latest["macd_signal"]:
            signals.append("MACD crossover is bullish (BUY)")
        elif latest["macd"] < latest["macd_signal"]:
            signals.append("MACD crossover is bearish (SELL)")
        else:
            signals.append("MACD is neutral")
    else:
        signals.append("MACD not available")

    # Bollinger Band logic
    if pd.notna(latest["bb_lower"]) and pd.notna(latest["bb_upper"]):
        if latest["close"] < latest["bb_lower"]:
            signals.append("Price below lower Bollinger Band (BUY)")
        elif latest["close"] > latest["bb_upper"]:
            signals.append("Price above upper Bollinger Band (SELL)")
        else:
            signals.append("Price within Bollinger Band (HOLD)")
    else:
        signals.append("Bollinger Bands not available")

    # Final decision logic
    buy_count = sum("BUY" in s for s in signals)
    sell_count = sum("SELL" in s for s in signals)

    if buy_count >= 2:
        decision = "BUY"
    elif sell_count >= 2:
        decision = "SELL"
    else:
        decision = "HOLD"

    return {"decision": decision, "signals": signals, "latest_data": signal_details}


# 🧠 LLM Summary using Gemini
def call_llm_summary(coin_id, indicators, signals, decision):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    signal_text = "\n- " + "\n- ".join(signals)

    prompt = f"""
You are a crypto technical analyst.

Based on the following indicator values and technical signals for {coin_id.upper()}, write a short expert-level technical summary.

Indicators:
{json.dumps(indicators, indent=2)}

Signals:
{signal_text}

Final Decision: {decision}

Provide a natural language summary of the technical analysis and outlook for the coin.
"""

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except:
            return "⚠️ Gemini response received, but parsing failed."
    else:
        print("❌ Gemini API error:", response.status_code, response.text)
        return "⚠️ Gemini API failed."


# 🚀 Main agent function
def technical_analyst_agent(coin_id="bitcoin"):
    print(f"\n📊 Running Technical Analyst Agent for: {coin_id.upper()}")

    df = fetch_ohlc_data(coin_id)
    if df is None or len(df) < 30:
        return {"error": "Not enough data to compute indicators."}

    df = analyze_technical_indicators(df)
    analysis = generate_signal(df)
    summary = call_llm_summary(
        coin_id=coin_id,
        indicators=analysis["latest_data"],
        signals=analysis["signals"],
        decision=analysis["decision"],
    )

    analysis["summary"] = summary
    print(json.dumps(analysis, indent=2))
    return analysis


# ✅ Run the agent for popular coins
if __name__ == "__main__":
    for coin_id in ["bitcoin"]:
        technical_analyst_agent(coin_id)
