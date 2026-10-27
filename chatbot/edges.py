from state import ChatState

MAX_RETRIES = 3


def after_security(state: ChatState):
    return {"greeting": "greet", "preference": "preference", "off_topic": "off_topic", "ok": "schema"}.get(state["category"], "refuse")


def after_sql(state: ChatState):
    return "not_found_field" if state["sql"] == "CANNOT_ANSWER" else "sql_check"


def after_sql_check(state: ChatState):
    return "refuse" if state["category"] == "unsafe" else "run_query"


def after_query(state: ChatState):
    if state["sql_error"]:
        return "fallback" if state["retry_count"] > MAX_RETRIES else "sql"
    return "answer" if state["rows"] else "not_found_rows"


def after_validate(state: ChatState):
    if not state["feedback"]:
        return "memory_save"
    return "fallback" if state["retry_count"] > MAX_RETRIES else "answer"