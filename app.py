import streamlit as st
from main_runner import run_trading_pipeline


# === Page congiguration ===
st.set_page_config(page_title="NeuroFi", layout="centered")

# === custom styling ===
st.markdown("""
    <style>
        .centered-title {
            text-align: center;
            margin-bottom: 0.2rem;
        }
        .centered-sub {
            text-align: center;
            color: gray;
            font-size: 1rem;
            margin-bottom: 2rem;
        }
        .form-container {
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
            padding: 1rem 2rem;
        }
        .center-button {
            display: flex;
            justify-content: center;
            margin-top: 1rem;
        }
        .terms {
            text-align: center;
            margin-top: 2rem;
            font-size: 0.9rem;
        }
    </style>
""", unsafe_allow_html=True)


# === Heading ===
st.markdown("<h1 class='centered-title'>NeuroFi</h1>", unsafe_allow_html=True)
st.markdown("<p class='centered-sub'>Hello there, My name Neu. I can help you analyse the crypto market and give the best recommendation based on your investment preference. Just answer a few question below for me to properly understand your preference.</p>", unsafe_allow_html=True)

# === Form ===
with st.form("investment_form"):
    coin_label = st.selectbox(
        "🪙 What cryptocurrency are interested in today", 
        ["Bitcoin (BTC)", "Ethereum (ETH)", "Ripple (XRP)", "Binance coin (BNB)", "Solana (SOL)",
        "Toncoin (TON)", "Cardano (ADA)", "Dogecoin (DOGE)", "Avalanche (AVAX)", "Shiba Inu (SHIB)", 
        "Cardano (ADA)", "Litecoin (LTC)", "Polkadot (DOT)", "Chainlink (LINK)", "Hyperliquid (HYPE)",
        "Stellar(XLM)", "Wrapped Bitcoin (WBTC)", "Avalanche (AVAX)", "Hedera (HBAR)", "TRON (TRX)"]
    )

    trader = st.selectbox(
        "What describes you best?",
        ["New buyer", "Exiting buyer"]
    )

    duration = st.selectbox(
        "⏳ Investment Duration", 
        ["Short-term (1-3 months)", "Medium-term (3-6 months)", "Long-term (6+ months)"]
        )

    submit = st.form_submit_button("Run Analytics")

# === Run Backend ===
if submit:
    with st.spinner("🔍 Give it a minute, Neu is analysing the market for you..."):
        coin_id = coin_label.split("(")[1].replace(")", "").strip().lower()  # Extract "BTC" → "btc"
        final_state = run_trading_pipeline(coin=coin_id)

    # === Display Output ===
    st.success("✅ Here's what I found!")

    if final_state:
        recommendation = final_state.get("final_recommendation", "No recommendation available.")
        confidence = final_state.get("research_confidence", "N/A")

        st.markdown(f"### 🧠 Recommendation: {recommendation}")
        st.markdown(f"**📊 Confidence Level:** {confidence}")

        # Optional advice or risk info
        risk_notes = final_state.get("risk_notes")
        if risk_notes:
            st.info(f"⚠️ Risk Notes: {risk_notes}")

        # Toggle to show news
        show_news = st.toggle("📰 Show News Report")
        if show_news:
            news = final_state.get("news_report", "No news available.")
            st.markdown(f"### 📰 News Report: {news}")
            # st.write(news)

    else:
        st.error("Something went wrong. Could not retrieve analysis.")


# === Other links ===
# Terms of Use
# st.markdown("""
# <div class='terms'>
#     <a href='https://your-terms-link.com' target='_blank'>Terms of Use</a>
# </div>
# """, unsafe_allow_html=True)
