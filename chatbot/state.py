from typing import TypedDict

ChatState = TypedDict("ChatState", {
    "question": str,
    "user_id": str,
    "session_id": str,
    "history": list,
    "facts": list,
    "category": str,
    "fact": str,
    "schema": str,
    "sql": str,
    "sql_error": str,
    "columns": list,
    "rows": list,
    "answer": str,
    "feedback": str,
    "retry_count": int,
}, total=False)