import uuid

from langgraph.graph import StateGraph, START, END

from state import ChatState
from nodes import (
    memory_load_node, security_node, greet_node, preference_node, off_topic_node, refuse_node,
    schema_node, sql_node, sql_check_node, run_query_node, answer_node, validate_node,
    not_found_field_node, not_found_rows_node, fallback_node, memory_save_node,
)
from edges import after_security, after_sql, after_sql_check, after_query, after_validate

builder = StateGraph(ChatState)

builder.add_node("memory_load", memory_load_node)
builder.add_node("security", security_node)
builder.add_node("greet", greet_node)
builder.add_node("preference", preference_node)
builder.add_node("off_topic", off_topic_node)
builder.add_node("refuse", refuse_node)
builder.add_node("schema", schema_node)
builder.add_node("sql", sql_node)
builder.add_node("sql_check", sql_check_node)
builder.add_node("run_query", run_query_node)
builder.add_node("answer", answer_node)
builder.add_node("validate", validate_node)
builder.add_node("not_found_field", not_found_field_node)
builder.add_node("not_found_rows", not_found_rows_node)
builder.add_node("fallback", fallback_node)
builder.add_node("memory_save", memory_save_node)

builder.add_edge(START, "memory_load")
builder.add_edge("memory_load", "security")
builder.add_conditional_edges("security", after_security)
builder.add_edge("schema", "sql")
builder.add_conditional_edges("sql", after_sql)
builder.add_conditional_edges("sql_check", after_sql_check)
builder.add_conditional_edges("run_query", after_query)
builder.add_edge("answer", "validate")
builder.add_conditional_edges("validate", after_validate)

for node in ["greet", "preference", "off_topic", "refuse", "not_found_field", "not_found_rows", "fallback"]:
    builder.add_edge(node, "memory_save")
builder.add_edge("memory_save", END)

graph = builder.compile()


if __name__ == "__main__":
    user_id = input("Your name: ").strip() or "guest"
    session_id = str(uuid.uuid4())
    while True:
        question = input("\nYou: ").strip()
        if question in ("quit", "exit"):
            break
        result = graph.invoke({"question": question, "user_id": user_id, "session_id": session_id})
        print("Bot:", result["answer"])
        if result.get("sql_error") or result.get("feedback"):
            print("DEBUG sql_error:", result.get("sql_error"))
            print("DEBUG feedback:", result.get("feedback"))