import streamlit as st
from scrape import WebScraper
import pandas as pd
import json
import io
import zipfile
from datetime import datetime


st.set_page_config(
    page_title="ScrapeX",
    layout="wide",
)


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
    }

    :root {
        --bg: #ffffff;
        --surface: #fafafa;
        --border: #e5e5e5;
        --text: #111111;
        --muted: #6b7280;
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    .title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .subtitle {
        font-size: 13px;
        color: var(--muted);
        margin-bottom: 20px;
    }

    .metric-row {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
    }

    .metric {
        padding: 10px 14px;
        border: 1px solid var(--border);
        border-radius: 6px;
        background: var(--surface);
        min-width: 100px;
    }

    .metric-label {
        font-size: 11px;
        color: var(--muted);
        text-transform: uppercase;
    }

    .metric-value {
        font-size: 16px;
        font-weight: 600;
    }

    .section {
        margin-top: 20px;
    }

    .stTextInput input {
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
    }

    .stButton button {
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        background: white !important;
    }

    .stDownloadButton button {
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        background: white !important;
    }

    .streamlit-expanderHeader {
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }

    .streamlit-expanderContent {
        border: 1px solid var(--border) !important;
        border-top: none !important;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid var(--border);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


def metric(label, value):
    return f"""
    <div class="metric">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """


def build_zip(data: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("data.json", json.dumps(data, indent=2))
        zf.writestr("text.txt", data.get("text_content", ""))

        if data.get("links"):
            zf.writestr("links.csv", pd.DataFrame(data["links"]).to_csv(index=False))

        if data.get("images"):
            zf.writestr("images.csv", pd.DataFrame(data["images"]).to_csv(index=False))

        if data.get("headers"):
            zf.writestr("headers.csv", pd.DataFrame(data["headers"]).to_csv(index=False))

    buf.seek(0)
    return buf.read()


def display_data(data):
    word_count = len(data.get("text_content", "").split())

    st.markdown(
        f"""
        <div class="metric-row">
            {metric("Links", len(data.get("links", [])))}
            {metric("Images", len(data.get("images", [])))}
            {metric("Headers", len(data.get("headers", [])))}
            {metric("Words", word_count)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.download_button("Download ZIP", build_zip(data), "data.zip")

    with st.expander("Metadata", expanded=True):
        st.json(data.get("metadata", {}))

    with st.expander("Headers"):
        st.dataframe(pd.DataFrame(data.get("headers", [])))

    with st.expander("Links"):
        links = data.get("links", [])
    if links:
        df = pd.DataFrame(links)
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "url": st.column_config.LinkColumn("URL"),
                "text": st.column_config.TextColumn("Text"),
            },
            hide_index=True,
        )

    with st.expander("Images"):
        images = data.get("images", [])
    if images:
        df = pd.DataFrame(images)
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "src": st.column_config.LinkColumn("Image URL"),
                "alt": st.column_config.TextColumn("Alt"),
            },
            hide_index=True,
        )

    with st.expander("Text"):
        st.text_area("", data.get("text_content", "")[:2000], height=250)


def main():
    st.markdown('<div class="title">ScrapeX</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Web Scraper</div>', unsafe_allow_html=True)

    if "data" not in st.session_state:
        st.session_state.data = None

    with st.sidebar:
        wait = st.slider("Wait time", 1, 15, 5)

    col1, col2 = st.columns([5, 1])

    with col1:
        url = st.text_input("", placeholder="https://example.com")

    with col2:
        run = st.button("Scrape")

    if run and url:
        scraper = WebScraper()
        with st.spinner("Scraping..."):
            result = scraper.scrape_website(url, wait)

        if result:
            st.session_state.data = result
            st.success("Scraped successfully")
        else:
            st.error("Failed")

    if st.session_state.data:
        display_data(st.session_state.data)


if __name__ == "__main__":
    main()