import traceback
import uuid

import streamlit as st

from graph import graph
from memory import clear_context

st.title("Company Financials Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())

user_id = st.sidebar.text_input("Your name", value="guest")

if st.sidebar.button("New chat"):
    clear_context(st.session_state.session_id)
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())
    st.rerun()

for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

question = st.chat_input("Ask about sales, products, profit or expenses")

if question:
    st.chat_message("user").markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        box = st.empty()
        box.markdown("Thinking...")
        text = ""
        answer = ""
        used_sql = ""
        inputs = {"question": question, "user_id": user_id, "session_id": st.session_state.session_id}

        try:
            for mode, chunk in graph.stream(inputs, stream_mode=["messages", "updates"]):
                if mode == "messages":
                    message, metadata = chunk
                    if metadata.get("langgraph_node") == "answer" and message.content:
                        text += message.content
                        box.markdown(text)

                elif mode == "updates":
                    for update in chunk.values():
                        if not isinstance(update, dict):
                            continue
                        if update.get("answer"):
                            answer = update["answer"]
                        if update.get("category") == "safe" and update.get("sql"):
                            used_sql = update["sql"]
                        if update.get("feedback"):
                            text = ""

            answer = answer or text or "Sorry, I couldn't get an answer. Please try again."
        except Exception:
            answer = "Something went wrong while answering."
            st.error(traceback.format_exc())

        box.markdown(answer)
        if used_sql:
            with st.expander("SQL used"):
                st.code(used_sql, language="sql")

    st.session_state.messages.append({"role": "assistant", "content": answer})