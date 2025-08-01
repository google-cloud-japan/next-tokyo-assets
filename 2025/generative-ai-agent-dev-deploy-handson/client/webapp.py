import streamlit as st
from vertexai import agent_engines

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
            response_placeholder = st.empty()
            full_response = ""
            for event in agent.stream_query(user_id=user_id, message=message):
                response_placeholder.markdown(event)
    else:
        st.warning("Please enter a User ID and a message.")
