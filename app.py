import streamlit as st
from pathlib import Path
from base64 import b64encode

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
    page_icon= faviconimg,
    layout="wide",
)

# === Load external CSS === 
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



# -----------------------------------------------------------------------------------------------
# === Main app container ===
with st.container(key="page"):

    # Navigation
    with st.container(key="nav"):
        logo_data = embed_image(Path("assets/Neulogo.png"))
        github = embed_image(Path("assets/gitimg.webp"))

        st.markdown("<nav class='nav'>", unsafe_allow_html=True)
        with st.container(key="nav_left"):
            logo_data = embed_image(Path("assets/Neulogo.png"))
            if logo_data:
                st.markdown(f"<img class='logo' src='{logo_data}' alt='NeuroFi logo' />", unsafe_allow_html=True)
            else:
                st.markdown("<div class='logo'>🧠</div>", unsafe_allow_html=True)
        with st.container(key="nav_right"):
            github = embed_image(Path("assets/gitimg.webp"))
            st.markdown(f"<a href='https://github.com/bhavadharanik/NeutroFi' target='_blank'><img class='logo' src='{github}' alt='NeuroFi logo' /></a>", unsafe_allow_html=True)
        st.markdown("</nav>", unsafe_allow_html=True)

    # Hero Section
    with st.container(key="hero"):
        st.markdown(
            """
            <div class="hero">
              <span class="badge">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 12c2.5-.5 3.5-1.5 4-4 .5 2.5 1.5 3.5 4 4-2.5.5-3.5 1.5-4 4-.5-2.5-1.5-3.5-4-4Z" stroke="currentColor"/></svg>
                Multi‑Agent AI for Crypto
              </span>
              <h1 class="title">Decide when to <span style="color:var(--accent)">Buy</span> or <span style="color:#f59e0b">Hold</span> — with explainable insight</h1>
              <p class="subtitle">NeutroFi analyzes fundamentals, technicals, sentiment, and news, then delivers a single, transparent recommendation for your timeframe and risk profile.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # KPI Section
    with st.container(key="kpis"):
        st.markdown(
            """
            <section class='kpis'>
              <div class='kpi'><p>Avg decision latency</p><h3>~6.2s</h3></div>
              <div class='kpi'><p>Coverage</p><h3>Top 200 coins</h3></div>
              <div class='kpi'><p>Explainability</p><h3>4-agent breakdown</h3></div>
            </section>
            """,
            unsafe_allow_html=True,
        )

    # Features Section
    with st.container(key="features"):
        st.markdown(
            """
            <section class='grid'>
              <div class='card'><h4>Multi-Signal Analysis</h4><p>Fundamentals, technicals, sentiment, and news — each agent produces a concise report. No black boxes.</p></div>
              <div class='card'><h4>Aligned to Your Horizon</h4><p>Pick short, medium, or long term. The trader agent tunes entries, stops, and conviction to your horizon.</p></div>
              <div class='card'><h4>Actionable & Explainable</h4><p>Get a Buy/Hold verdict with a confidence score, key drivers, and links to where you can purchase.</p></div>
            </section>
            """,
            unsafe_allow_html=True,
        )

    # How it Works Section
    with st.container(key="how"):
        st.markdown(
            """
            <div id='how' style='margin-top:2.25rem'>
              <h3>How NeutroFi works</h3>
              <ol>
                <li><b>You choose</b> coin, timeframe, and risk level.</li>
                <li><b>Agents analyze</b> market data, tokenomics, social chatter, and news.</li>
                <li><b>Debate & risk check</b> consolidate bull/bear views with guardrails.</li>
                <li><b>Verdict</b> — Buy or Hold with rationale and next steps.</li>
              </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # CTA Section
    with st.container(key="cta"):
        st.markdown("<div id='get-started' style='text-align:center; margin-top:2rem'>", unsafe_allow_html=True)
        if st.button("Get Analysis", type="primary", use_container_width=True, key="cta_button"):
            try:
                st.switch_page("pages/form.py")
            except Exception:
                st.session_state["__target_page"] = "pages/form.py"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Footer Section
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


# === End of app.py ===