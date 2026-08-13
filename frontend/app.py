import streamlit as st
import sys
import os

# Allow Python to find the backend folder
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from backend.ai_service import get_ai_response


st.set_page_config(
    page_title="CloudTalk",
    page_icon="☁️",
    layout="centered"
)


st.title("☁️ CloudTalk")
st.subheader("Serverless AI Chatbot")

st.write(
    "Ask anything and get intelligent responses powered by AI."
)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat history
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
prompt = st.chat_input("Type your message...")


if prompt:

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)


    # Generate AI response
    with st.chat_message("assistant"):

        with st.spinner("CloudTalk is thinking... ☁️"):

            try:

                response = get_ai_response(
                    st.session_state.messages
                )

                st.markdown(response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

            except Exception as e:

                st.error(
                    "Sorry, something went wrong while "
                    "connecting to the AI."
                )

                st.error(str(e))