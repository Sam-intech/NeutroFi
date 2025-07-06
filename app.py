# app.py

import streamlit as st

st.set_page_config(page_title="NeuroFi", layout="centered")

# st.title("NeuroFi")

# st.markdown("Hello there, My name is Neu, I can help you analyse the crupyo market and get the best investment option for based on your prefernce. Just answers a few question to help me understand your preference and i will do the cast the spell.")

# Inject custom CSS
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

# Centered headings
st.markdown("<h1 class='centered-title'>NeuroFi</h1>", unsafe_allow_html=True)
st.markdown("<p class='centered-sub'>Hello there, My name Neu. I can help you analyse the crypto market and give the best recommendation based on your investment preference. Just answer a few question below for me to properly understand your preference.</p>", unsafe_allow_html=True)


# --- Input Form ---
with st.form("investment_form"):
    duration = st.selectbox(
        "🕒 How long do you want to invest?",
        ["1 month", "3 months", "6 months", "12 months", "12+ months"]
    )

    amount = st.number_input(
        "💰 How much do you want to invest (USD)?",
        min_value=10, step=10, value=100
    )

    risk = st.selectbox(
        "⚖️ What's your risk appetite?",
        ["Low", "Moderate", "High"]
    )

    category = st.multiselect(
        "📂 Which crypto sectors interest you?",
        ["Layer 1s", "DeFi", "NFTs", "Memecoins", "Privacy Coins", "AI Tokens", "Gaming", "Stablecoins"]
    )

    st.markdown("</div>", unsafe_allow_html=True)
    with st.container():
        submit = st.form_submit_button("Get Recommendations")

    # submitted = st.form_submit_button("Get Recommendations")

if submit:
    st.write("Processing your preferences... 🔄")
    # 🚧 Replace with actual backend call
    st.write({
        "Duration": duration,
        "Investment": amount,
        "Risk": risk,
        "Categories": category
    })


# Terms of Use
st.markdown("""
<div class='terms'>
    <a href='https://your-terms-link.com' target='_blank'>Terms of Use</a>
</div>
""", unsafe_allow_html=True)
