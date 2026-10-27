import uuid

import streamlit as st

from graph import graph

st.title("Company Financials Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())

user_id = st.sidebar.text_input("Your name", value="guest")

for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

question = st.chat_input("Ask about sales, products, profit or expenses")

if question:
    st.chat_message("user").markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        box = st.empty()
        text = ""
        answer = ""
        inputs = {"question": question, "user_id": user_id, "session_id": st.session_state.session_id}

        for mode, chunk in graph.stream(inputs, stream_mode=["messages", "updates"]):
            if mode == "messages" and chunk[1]["langgraph_node"] == "answer":
                text += chunk[0].content
                box.markdown(text)
            if mode == "updates":
                for update in chunk.values():
                    if update and "answer" in update:
                        answer = update["answer"]
                    if update and update.get("feedback"):
                        text = ""

        box.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})