import json
import os

import redis
from dotenv import load_dotenv

load_dotenv()

client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)

MAX_TURNS = 10            # keep the last 10 questions in the context window
MAX_ANSWER_CHARS = 300    # store a short version of each answer
SESSION_TTL = 30 * 60     # forget the chat after 30 minutes of no activity


# Short-term memory: the context window for one chat session

def get_context(session_id):
    turns = client.lrange(f"chat:{session_id}", 0, -1)
    return [json.loads(turn) for turn in turns]


def save_turn(session_id, question, answer, sql=""):
    key = f"chat:{session_id}"
    turn = {"question": question, "answer": answer[:MAX_ANSWER_CHARS], "sql": sql}
    client.rpush(key, json.dumps(turn))
    client.ltrim(key, -MAX_TURNS, -1)
    client.expire(key, SESSION_TTL)


def clear_context(session_id):
    client.delete(f"chat:{session_id}")


# Long-term memory: facts about the user, kept across chats

def get_facts(user_id):
    return list(client.smembers(f"memory:{user_id}"))


def add_fact(user_id, fact):
    client.sadd(f"memory:{user_id}", fact)