import streamlit as st
from pathlib import Path
from base64 import b64encode
import time
from main_runner import run_trading_pipeline

# === Helper: embed local image if exists ===
def embed_image(path: Path) -> str:
    if path.exists():
        data = path.read_bytes()
        return f"data:image/png;base64,{b64encode(data).decode()}"
    return ""

faviconimg = embed_image(Path("assets/Neulogo.png"))

# === Page configuration ===
st.set_page_config(
    page_title="NeutroFi — AI Crypto Advisor",
    page_icon=faviconimg,
    layout="centered",
)

# === Load external CSS ===
with open("assets/form.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# === Session State ===
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None
if "fade_class" not in st.session_state:
    st.session_state.fade_class = "form-container"

# === Reset Function ===
def reset_form():
    st.session_state.show_results = False
    st.session_state.analysis_data = None
    st.session_state.fade_class = "form-container"

# === Run Analysis Function ===
def run_analysis(coin, trader, duration):
    # Trigger fade-out animation
    st.session_state.fade_class = "form-container fade-out"
    st.session_state.animating = True

    with st.spinner("🔍 Give it a minute, Neu is analysing the market for you"):
        time.sleep(0.6)  # Simulate processing delay
        data = run_trading_pipeline(coin=coin)

        if not isinstance(data, dict):
            st.error(f"Unexpected backend output type: {type(data)}. Expected dict.")
            st.stop()

        st.session_state.analysis_data = data
        st.session_state.show_results = True
        st.session_state.animating = False
        st.rerun()

# === PAGE TITLE ===
st.markdown("<h1 style='text-align:center;'>Your Investment Preferences</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#a3b1c6;'>Tell NeuroFi about your goals and risk appetite so our agents can analyze the market for you.</p>", unsafe_allow_html=True)

# === FORM or RESULTS ===
if not st.session_state.show_results:
    fade_class = st.session_state.fade_class if "fade_class" in st.session_state else "form-container"
    # st.markdown(f"<div class='{st.session_state.fade_class}'>", unsafe_allow_html=True)
    st.markdown(f"<div class='{fade_class}'>", unsafe_allow_html=True)
    with st.form("analysis_form", clear_on_submit=False):
        coin_label = st.selectbox(
            "🪙 What cryptocurrency are interested in today",
            [
                "Bitcoin (BTC)", "Ethereum (ETH)", "Ripple (XRP)", "Binance coin (BNB)", "Solana (SOL)",
                "Toncoin (TON)", "Cardano (ADA)", "Dogecoin (DOGE)", "Avalanche (AVAX)", "Shiba Inu (SHIB)",
                "Litecoin (LTC)", "Polkadot (DOT)", "Chainlink (LINK)", "Hyperliquid (HYPE)",
                "Stellar (XLM)", "Wrapped Bitcoin (WBTC)", "Hedera (HBAR)", "TRON (TRX)"
            ]
        )

        trader = st.radio(
            "What describes you best?",
            ["New buyer", "Exiting buyer"]
        )

        duration = st.selectbox(
            "⏳ Investment Duration",
            ["Short-term (1-3 months)", "Medium-term (3-6 months)", "Long-term (6+ months)"],
            help="How long do you plan to hold this asset?"
        )


        submit = st.form_submit_button("Run Analytics", use_container_width=True)
        if submit:
            run_analysis(coin_label, trader, duration)
    st.markdown("</div>", unsafe_allow_html=True)

else:
    data = st.session_state.analysis_data
    recommendation = data["final_decision"]
    # recommendation = data["final_decision"]["holder"]
    # buyer = data["final_decision"]["buyer"]
    # conf = data["final_decision"]["confidence"]

    st.markdown("<div class='results-container'>", unsafe_allow_html=True)
    # Final Decision Card
    st.markdown(f"""
    <div class='decision-card {recommendation}'>
        <h4>📈 Neu's Recommendation: <span>{recommendation}</span></h4>
    </div>
    """, unsafe_allow_html=True)

    # Research Summary
    st.markdown(f"<div class='summary-card'>{data['research_summary']}</div>", unsafe_allow_html=True)

    # Risk Notes
    st.markdown(f"<div class='risk-card'>{data['risk_notes']}</div>", unsafe_allow_html=True)

    # Tab Bar for Reports
    st.markdown(f"<div class='reports-section'>", unsafe_allow_html=True)
    tab_labels = ["News", "Fundamentals", "Technical", "Sentiment"]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        st.markdown(data["reports"]["news"]["raw"])

    with tabs[1]:
        st.markdown(data["reports"]["fundamentals"]["raw"])

    with tabs[2]:
        st.markdown(data["reports"]["technical"]["raw"])

    with tabs[3]:
        st.markdown(data["reports"]["sentiment"]["raw"])
    st.markdown("</div>", unsafe_allow_html=True)

    # Try Another Coin Button
    st.button("🔄 Try another coin", use_container_width=True, on_click=reset_form)
    st.markdown("</div>", unsafe_allow_html=True)

# === Footer ===
with st.container(key="footer"):
    st.markdown(
        """
        <div class='footer'>
          <hr style='border-color:rgba(255,255,255,.08); border-width:0 0 1px; margin:2rem 0'>
          <div class='disclaimer'>
            <strong>Disclaimer:</strong> NeutroFi provides information and analysis only and is <em>not</em> financial advice. Crypto assets are highly volatile.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
