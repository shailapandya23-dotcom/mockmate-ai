import json
import os

QUESTION_MEMORY_PATH = "data/question_memory.json"
HISTORY_PATH = "data/history/history.json"


def load_question_memory():
    if not os.path.exists(QUESTION_MEMORY_PATH):
        return {}
    with open(QUESTION_MEMORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_question_memory(domain, questions):
    memory = load_question_memory()
    if domain not in memory:
        memory[domain] = []
    existing_hashes = set(memory[domain])
    for q in questions:
        q_hash = str(hash(q))
        if q_hash not in existing_hashes:
            memory[domain].append(q_hash)
            existing_hashes.add(q_hash)
    with open(QUESTION_MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def get_memory_exclusions(domain):
    memory = load_question_memory()
    if domain not in memory or not memory[domain]:
        return ""
    return "Previously used question hashes to avoid (do not generate similar questions): " + ", ".join(memory[domain][-50:])


def load_history():
    if not os.path.exists(HISTORY_PATH):
        return []
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_interview(record):
    history = load_history()
    history.append(record)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
