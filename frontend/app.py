import streamlit as st
import requests
import uuid


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "https://cloud-talk-7vqxgmj8g-savee1.vercel.app/api"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CloudTalk",
    page_icon="☁️",
    layout="centered",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

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


# ============================================================
# HEADER
# ============================================================

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


# ============================================================
# SESSION INITIALIZATION
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:

    # Try to keep the same session ID in the browser URL
    existing_session = st.query_params.get("session_id")

    if existing_session:
        st.session_state.session_id = existing_session
    else:
        st.session_state.session_id = str(uuid.uuid4())
        st.query_params["session_id"] = st.session_state.session_id

if "chat_id" not in st.session_state:
    st.session_state.chat_id = None

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False


# ============================================================
# LOAD CHAT HISTORY FROM SUPABASE
# ============================================================

if not st.session_state.history_loaded:

    existing_chat_id = st.query_params.get("chat_id")

    if existing_chat_id:

        try:

            history_response = requests.get(
                API_URL,
                params={
                    "chat_id": existing_chat_id
                },
                timeout=30
            )

            if history_response.status_code == 200:

                history_data = history_response.json()

                saved_messages = history_data.get(
                    "messages",
                    []
                )

                st.session_state.messages = []

                for message in saved_messages:

                    role = message.get("role")
                    content = message.get("content")

                    if role in ["user", "assistant"] and content:

                        st.session_state.messages.append(
                            {
                                "role": role,
                                "content": content
                            }
                        )

                st.session_state.chat_id = existing_chat_id

        except Exception:
            pass

    st.session_state.history_loaded = True


# ============================================================
# SIDEBAR
# ============================================================

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
        - 🗄️ Supabase
        - 🔗 REST API
        - 🐙 GitHub
        """
    )

    st.divider()

    # ========================================================
    # CLEAR CHAT
    # ========================================================

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.chat_id = None
        st.session_state.history_loaded = True

        # Create completely new session
        new_session_id = str(uuid.uuid4())

        st.session_state.session_id = new_session_id

        # Remove old chat from URL
        st.query_params.clear()

        # Store new session
        st.query_params["session_id"] = new_session_id

        st.rerun()


# ============================================================
# DISPLAY SAVED / CURRENT MESSAGES
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


# ============================================================
# WELCOME MESSAGE
# ============================================================

if len(st.session_state.messages) == 0:

    st.info(
        "👋 Welcome to CloudTalk! "
        "Ask me anything and I'll process your request "
        "through the cloud."
    )


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "💬 Type your message..."
)


# ============================================================
# SEND MESSAGE
# ============================================================

if prompt:

    # --------------------------------------------------------
    # Add user message locally
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(prompt)


    # --------------------------------------------------------
    # AI RESPONSE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "☁️ Sending request to the cloud..."
        ):

            try:

                api_response = requests.post(
                    API_URL,
                    json={
                        "messages": st.session_state.messages,
                        "session_id": st.session_state.session_id
                    },
                    timeout=60
                )


                # ------------------------------------------------
                # Check API response
                # ------------------------------------------------

                if api_response.status_code != 200:

                    try:
                        error_data = api_response.json()

                        error_message = error_data.get(
                            "error",
                            "Unknown API error"
                        )

                    except Exception:

                        error_message = api_response.text


                    raise Exception(
                        f"API Error {api_response.status_code}: "
                        f"{error_message}"
                    )


                # ------------------------------------------------
                # Read JSON response
                # ------------------------------------------------

                data = api_response.json()

                response = data.get(
                    "response",
                    ""
                )

                returned_chat_id = data.get(
                    "chat_id"
                )


                if not response:

                    raise Exception(
                        "The CloudTalk API returned an empty response."
                    )


                # ------------------------------------------------
                # Save chat ID
                # ------------------------------------------------

                if returned_chat_id:

                    st.session_state.chat_id = returned_chat_id

                    # Put chat ID in browser URL
                    st.query_params["chat_id"] = returned_chat_id


                # ------------------------------------------------
                # Display AI response
                # ------------------------------------------------

                st.markdown(response)


                # ------------------------------------------------
                # Save assistant message locally
                # ------------------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response
                    }
                )


            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ The CloudTalk API took too long to respond."
                )


            except requests.exceptions.RequestException as e:

                st.error(
                    "❌ Unable to connect to the CloudTalk API."
                )

                st.caption(
                    str(e)
                )


            except Exception as e:

                st.error(
                    "❌ Something went wrong."
                )

                st.caption(
                    str(e)
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        ☁️ CloudTalk • Serverless AI Chatbot
        <br>
        Built using Python, Streamlit, Vercel, Groq & Supabase
    </div>
    """,
    unsafe_allow_html=True
)