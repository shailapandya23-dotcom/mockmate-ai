import streamlit as st


def init_session_state():
    defaults = {
        "page": "setup",
        "questions": [],
        "current_q": 0,
        "answers": [],
        "evaluations": [],
        "domain": "DSA",
        "difficulty": "Medium",
        "total_questions": 5,
        "summary": None,
        "candidate_name": "",
        "interview_started": False,
        "all_evaluations_data": [],
        "session_history": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
