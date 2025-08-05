import streamlit as st
from vertexai import agent_engines
import json

st.title("Agent Client")

# Agentの初期化
agent = agent_engines.get("projects/gossy-workstations/locations/us-central1/reasoningEngines/5943722365245456384")

# ユーザーIDの入力
user_id = st.text_input("Enter your User ID", "USER_ID")

# メッセージの入力
message = st.text_input("Enter your message", "Hello?")

if st.button("Send"):
    if user_id and message:
        st.write("Agent response:")
        with st.spinner("Waiting for agent..."):
            # The stream can yield different types. We will handle them as they come.
            for event in agent.stream_query(user_id=user_id, message=message):
                if isinstance(event, dict):
                    # If the event is a dictionary, display it as formatted JSON.
                    st.subheader("Formatted Dictionary Response")
                    st.json(event)
                else:
                    # As a fallback, display any other type as plain text.
                    st.subheader("Other Response")
                    st.text(str(event))
    else:
        st.warning("Please enter a User ID and a message.")
