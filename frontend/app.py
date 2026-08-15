import streamlit as st
import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from backend.ai_service import get_ai_response

st.set_page_config(
    page_title="CloudTalk",
    page_icon="☁️",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    .main {
        padding-top: 1rem;
    }

    .cloud-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }

    .cloud-icon {
        font-size: 3.5rem;
    }

    .cloud-title {
        font-size: 2.6rem;
        font-weight: 700;
        margin-bottom: 0;
    }

    .cloud-subtitle {
        font-size: 1.05rem;
        color: #777;
        margin-top: 0.2rem;
    }

    .status-card {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        background-color: #fafafa;
    }

    .status-online {
        color: #16a34a;
        font-weight: 600;
    }

    .status-label {
        font-size: 0.9rem;
        color: #555;
    }

    .sidebar-title {
        font-size: 1.4rem;
        font-weight: 700;
    }

    .sidebar-text {
        color: #666;
        line-height: 1.5;
    }

    .footer {
        text-align: center;
        color: #888;
        font-size: 0.8rem;
        padding: 2rem 0 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="cloud-header">
        <div class="cloud-icon">☁️</div>
        <div class="cloud-title">CloudTalk</div>
        <div class="cloud-subtitle">
            Your AI Assistant Powered by Serverless Cloud Computing
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown(
        '<div class="sidebar-title">☁️ CloudTalk</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-text">
        CloudTalk is an AI chatbot whose backend runs as a
        serverless cloud function.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### ☁️ Cloud Status")

    st.markdown(
        """
        <div class="status-card">
            <div class="status-online">🟢 Online</div>
            <div class="status-label">Cloud API</div>
        </div>

        <div class="status-card">
            <div class="status-online">🟢 Active</div>
            <div class="status-label">Serverless Backend</div>
        </div>

        <div class="status-card">
            <div class="status-online">🟢 Connected</div>
            <div class="status-label">AI Service</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### 🚀 Technology")

    st.markdown(
        """
        - 🐍 Python
        - 🎈 Streamlit
        - ☁️ Vercel Serverless Functions
        - 🤖 Groq AI
        - 🔗 REST API
        - 🐙 GitHub
        """
    )

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if len(st.session_state.messages) == 0:
    st.info(
        "👋 Welcome to CloudTalk! "
        "Ask me anything and I'll process your request "
        "through the cloud."
    )

prompt = st.chat_input("💬 Type your message...")

if prompt:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("☁️ Sending request to the cloud..."):
            try:
                response = get_ai_response(
    st.session_state.messages,
    st.session_state.session_id
)

                st.markdown(response)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response
                    }
                )

            except Exception as e:
                st.error(
                    "❌ Unable to connect to the CloudTalk AI service."
                )
                st.caption(str(e))

st.markdown(
    """
    <div class="footer">
        ☁️ CloudTalk • Serverless AI Chatbot
        <br>
        Built using Python, Streamlit, Vercel & Groq
    </div>
    """,
    unsafe_allow_html=True
)