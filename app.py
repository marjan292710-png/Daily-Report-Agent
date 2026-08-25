import streamlit as st
import os
from datetime import datetime

import serpapi
from google import genai


# =============================================
# DAILY REPORT AGENT
# TECHBUDDY AI ACADEMY
# =============================================

st.set_page_config(
    page_title="Daily Report Agent",
    page_icon="📰",
    layout="centered"
)


# =============================================
# API CLIENTS
# =============================================

GEMINI_KEY = st.secrets.get("GEMINI_API_KEY")
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY")

if not GEMINI_KEY:
    st.error("GEMINI_API_KEY is missing from Streamlit Secrets.")
    st.stop()

if not SERPAPI_KEY:
    st.error("SERPAPI_KEY is missing from Streamlit Secrets.")
    st.stop()

client = genai.Client(
    api_key=GEMINI_KEY
)


# =============================================
# PAGE HEADER
# =============================================

st.title("📰 Daily Report Agent")

st.caption(
    "AI-powered reports using Gemini + real-time web search"
)

st.divider()


# =============================================
# REPORT TOPICS
# =============================================

topic_options = [
    "Latest Technology News Pakistan",
    "Artificial Intelligence News",
    "Freelancing AI Tools Tips",
    "AI Business Opportunities",
    "Python Programming News"
]

selected_topic = st.selectbox(
    "Choose a report topic",
    topic_options
)


# =============================================
# CUSTOM TOPIC
# =============================================

custom_topic = st.text_input(
    "Or enter your own topic",
    placeholder="Example: latest Minecraft news"
)

if custom_topic.strip():
    report_topic = custom_topic.strip()
else:
    report_topic = selected_topic


# =============================================
# GENERATE REPORT FUNCTION
# =============================================

def generate_report(topic):

    date = datetime.now().strftime(
        "%A, %d %B %Y — %H:%M"
    )

    subject = (
        f"Daily {topic.title()} Report — "
        f"{datetime.now().strftime('%d %b %Y')}"
    )

    # =========================================
    # WEB SEARCH
    # =========================================

    search_client = serpapi.Client(
        api_key=SERPAPI_KEY
    )

    results = search_client.search({
        "q": topic,
        "num": 5
    })

    snippets = []

    for result in results.get(
        "organic_results",
        []
    ):

        title = result.get(
            "title",
            ""
        )

        snippet = result.get(
            "snippet",
            ""
        )

        snippets.append(
            f"{title}: {snippet}"
        )

    search_results = "\n".join(
        snippets
    )

    # =========================================
    # GEMINI PROMPT
    # =========================================

    prompt = f"""
Write a professional daily news report for:

"{topic}"

Current date and time:

{date}

Search results:

{search_results}

Format the report like this:

DAILY REPORT — {date}

Topic: {topic}

KEY STORIES:

• [story 1]
• [story 2]
• [story 3]

SUMMARY:

[2-sentence overall summary]

ACTION ITEMS:

• [one thing to watch out for]
• [one opportunity this creates]

Keep the report clear, useful, and concise.

Only use information supported by the search results.
"""

    # =========================================
    # GEMINI
    # =========================================

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    report = response.text

    return subject, report


# =============================================
# GENERATE BUTTON
# =============================================

if st.button(
    "🚀 Generate Report",
    type="primary",
    use_container_width=True
):

    with st.spinner(
        "🔎 Searching the web and generating your report..."
    ):

        try:

            subject, report = generate_report(
                report_topic
            )

            st.session_state.report = report
            st.session_state.subject = subject

        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )


# =============================================
# DISPLAY REPORT
# =============================================

if "report" in st.session_state:

    st.divider()

    st.subheader(
        st.session_state.subject
    )

    st.markdown(
        st.session_state.report
    )

    # =========================================
    # DOWNLOAD REPORT
    # =========================================

    st.download_button(
        label="📥 Download Report",
        data=st.session_state.report,
        file_name="daily_report.txt",
        mime="text/plain",
        use_container_width=True
    )