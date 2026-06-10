import json
import os
from datetime import datetime

import streamlit as st

from utils.llm_client import LLMClient
from utils.session import init_session_state
from utils.storage import (
    load_question_memory,
    save_question_memory,
    get_memory_exclusions,
)
from utils.pdf_generator import generate_pdf


def get_llm_config():
    provider = (
        st.secrets.get("LLM_PROVIDER")
        or os.environ.get("LLM_PROVIDER")
        or "gemini"
    ).lower()

    if provider == "groq":
        api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
        model = st.secrets.get("GROQ_MODEL") or os.environ.get("GROQ_MODEL")
    else:
        api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        model = st.secrets.get("GEMINI_MODEL") or os.environ.get("GEMINI_MODEL")

    return provider, api_key, model


def configure_from_secrets():
    for key in ("LLM_PROVIDER", "GEMINI_API_KEY", "GEMINI_MODEL", "GROQ_API_KEY", "GROQ_MODEL"):
        if key in st.secrets:
            os.environ[key] = st.secrets[key]


def get_llm_client():
    provider, api_key, model = get_llm_config()
    if not api_key:
        return None
    return LLMClient(api_key=api_key, provider=provider, model=model)

st.set_page_config(
    page_title="MockMate AI — Technical Interview Simulator",
    page_icon="\U0001f3af",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .stApp {
        background-color: #FFFFFF;
    }

    h1, h2, h3 {
        color: #2D3436 !important;
    }
    h1 {
        border-bottom: 3px solid #DC3545;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    h2 {
        border-bottom: 2px solid #FFCDD2;
        padding-bottom: 0.3rem;
        margin-bottom: 0.8rem;
    }

    div[data-testid="metric-container"] {
        background: #FFFFFF;
        border: 1px solid #FFCDD2;
        border-left: 4px solid #DC3545;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(220, 53, 69, 0.06);
        transition: transform 0.15s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(220, 53, 69, 0.1);
    }
    div[data-testid="metric-container"] label {
        color: #2D3436 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="metric-container"] div[data-testid="metric-value"] {
        color: #DC3545 !important;
        font-weight: 700 !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #DC3545, #C0392B);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 6px rgba(220, 53, 69, 0.2);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #C0392B, #A93226);
        color: white;
        box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
        transform: translateY(-1px);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    .stButton > button[kind="secondary"] {
        background: white;
        color: #DC3545;
        border: 2px solid #DC3545;
        box-shadow: none;
    }
    .stButton > button[kind="secondary"]:hover {
        background: #FFF5F5;
        color: #C0392B;
        border-color: #C0392B;
        box-shadow: none;
    }

    .stProgress > div {
        background-color: #FFCDD2;
        border-radius: 10px;
        height: 10px;
    }
    .stProgress > div > div {
        background-color: #DC3545;
        border-radius: 10px;
    }

    .stTextArea textarea {
        border: 2px solid #FFCDD2;
        border-radius: 10px;
        font-size: 0.95rem;
        transition: border-color 0.2s ease;
    }
    .stTextArea textarea:focus {
        border-color: #DC3545;
        box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.1);
    }

    section[data-testid="stSidebar"] {
        background: #FFF5F5;
        border-right: 1px solid #FFCDD2;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #2D3436;
    }

    div[data-testid="stSelectbox"] > div {
        border-radius: 8px;
        border-color: #FFCDD2;
    }
    div[data-testid="stSelectbox"] > div:focus-within {
        border-color: #DC3545;
        box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.1);
    }

    div.stExpander {
        border: 1px solid #FFCDD2;
        border-radius: 10px;
        background: #FFFFFF;
    }
    div.stExpander > details > summary {
        font-weight: 600;
        color: #DC3545;
    }

    .stMarkdown hr {
        border-color: #FFCDD2;
        margin: 1.5rem 0;
    }

    .question-card {
        background: #FFFFFF;
        border: 1px solid #FFCDD2;
        border-left: 4px solid #DC3545;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(220, 53, 69, 0.08);
    }
    .question-card p {
        font-size: 1.15rem;
        line-height: 1.6;
        color: #2D3436;
        margin: 0;
    }

    .score-high {
        color: #27AE60 !important;
        font-weight: 700;
    }
    .score-mid {
        color: #F39C12 !important;
        font-weight: 700;
    }
    .score-low {
        color: #DC3545 !important;
        font-weight: 700;
    }

    .sidebar-logo {
        font-size: 1.5rem;
        font-weight: 800;
        color: #DC3545;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #FFCDD2;
        margin-bottom: 1rem;
    }
    .sidebar-logo span {
        font-size: 1rem;
        font-weight: 400;
        color: #2D3436;
        display: block;
    }

    .setup-card {
        background: #FFFFFF;
        border: 1px solid #FFCDD2;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 16px rgba(220, 53, 69, 0.06);
        height: 100%;
    }
    .setup-card h3 {
        color: #DC3545 !important;
        margin-top: 0;
    }

    div[data-testid="column"] {
        padding: 0 0.5rem;
    }

    .stDataFrame {
        border: 1px solid #FFCDD2;
        border-radius: 10px;
    }

    .stAlert {
        border-left: 4px solid #DC3545;
        border-radius: 8px;
    }

    .feedback-section {
        background: #FFF5F5;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
    }
    .feedback-section strong {
        color: #DC3545;
    }

    @media (max-width: 768px) {
        .setup-card {
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .question-card {
            padding: 1rem;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

init_session_state()
configure_from_secrets()

# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-logo">\U0001f3af MockMate <span>AI Interview Simulator</span></div>', unsafe_allow_html=True)

    st.markdown("### Navigation")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("\U0001f3e0 Home", use_container_width=True, type="secondary"):
            st.session_state.page = "setup"
            st.rerun()
    with col2:
        if st.button("\U0001f4ca History", use_container_width=True, type="secondary"):
            st.session_state.page = "history"
            st.rerun()

    if st.session_state.page == "interview" and st.session_state.questions:
        st.markdown("---")
        total = st.session_state.total_questions
        current = st.session_state.current_q + 1
        st.markdown(f"### Progress")
        st.progress(min(current / total, 1.0))
        st.markdown(
            f"<p style='text-align:center;font-size:0.9rem;color:#2D3436;'>"
            f"Question <strong>{current}</strong> of <strong>{total}</strong></p>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.75rem;color:#999;text-align:center;'>"
        "Powered by Groq / Gemini</p>",
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------------
# Page: Setup
# -------------------------------------------------------------------
def show_setup_page():
    st.markdown("# \U0001f3af MockMate AI")
    st.markdown(
        "<p style='font-size:1.1rem;color:#636e72;margin-bottom:2rem;'>"
        "Practice technical interviews with AI-powered evaluation and feedback.</p>",
        unsafe_allow_html=True,
    )

    provider, api_key, _ = get_llm_config()
    if not api_key:
        key_name = "GROQ_API_KEY" if provider == "groq" else "GEMINI_API_KEY"
        st.error(
            f"\U000026a0 API key not configured. Set `{key_name}` in Streamlit secrets.",
            icon="\U0001f512",
        )
        return

    st.markdown("### \U00002699\ufe0f Configure Your Interview")

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container():
            st.markdown('<div class="setup-card">', unsafe_allow_html=True)
            st.markdown("### \U0001f4da Domain")
            domain = st.selectbox(
                "Select domain",
                ["DSA", "DBMS", "OS", "CN", "ML", "Mixed"],
                index=["DSA", "DBMS", "OS", "CN", "ML", "Mixed"].index(
                    st.session_state.domain
                ),
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        with st.container():
            st.markdown('<div class="setup-card">', unsafe_allow_html=True)
            st.markdown("### \U0001f522 Difficulty")
            difficulty = st.selectbox(
                "Select difficulty",
                ["Easy", "Medium", "Hard"],
                index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty),
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        with st.container():
            st.markdown('<div class="setup-card">', unsafe_allow_html=True)
            st.markdown("### \U0001f4ca Questions")
            q_count = st.selectbox(
                "Number of questions",
                [5, 10, 20],
                index=[5, 10, 20].index(st.session_state.total_questions),
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.domain = domain
    st.session_state.difficulty = difficulty
    st.session_state.total_questions = q_count

    st.markdown("---")

    _, center, _ = st.columns([1, 2, 1])
    with center:
        start_disabled = not api_key
        if st.button(
            "\U000025b6 Start Interview",
            use_container_width=True,
            disabled=start_disabled,
            type="primary",
        ):
            with st.spinner("Generating interview questions..."):
                try:
                    client = get_llm_client()
                    if not client:
                        st.error("API key not configured.")
                        st.stop()
                    memory_exclusions = get_memory_exclusions(domain)
                    questions = client.generate_questions(
                        domain, difficulty, q_count, memory_exclusions
                    )
                    if not questions or len(questions) == 0:
                        st.error("Failed to generate questions. Please try again.")
                        st.stop()

                    st.session_state.questions = questions
                    st.session_state.current_q = 0
                    st.session_state.answers = []
                    st.session_state.evaluations = []
                    st.session_state.summary = None
                    st.session_state.interview_started = True
                    st.session_state.page = "interview"

                    save_question_memory(domain, questions)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating questions: {str(e)}")
                    st.info(
                        "Make sure your API key is valid and has access to the Gemini API."
                    )

# -------------------------------------------------------------------
# Page: Interview
# -------------------------------------------------------------------
def show_interview_page():
    if not st.session_state.questions:
        st.error("No questions loaded. Please start a new interview.")
        if st.button("\U0001f504 Start Over"):
            st.session_state.page = "setup"
            st.rerun()
        return

    q_idx = st.session_state.current_q
    total = st.session_state.total_questions

    if q_idx >= len(st.session_state.questions):
        st.session_state.page = "dashboard"
        st.rerun()
        return

    st.markdown(f"## Question {q_idx + 1} of {total}")

    with st.container():
        st.markdown(
            f'<div class="question-card"><p>{st.session_state.questions[q_idx]}</p></div>',
            unsafe_allow_html=True,
        )

    already_answered = q_idx < len(st.session_state.evaluations)

    if not already_answered:
        answer = st.text_area(
            "Your Answer",
            height=200,
            placeholder="Type your answer here... Be as detailed as possible.",
            key=f"answer_input_{q_idx}",
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("\U0001f504 Submit Answer", use_container_width=True, type="primary"):
                if not answer.strip():
                    st.error("Please write an answer before submitting.")
                else:
                    with st.spinner("Evaluating your answer..."):
                        try:
                            client = get_llm_client()
                            if not client:
                                st.error("API key not configured.")
                                st.stop()
                            eval_data = client.evaluate_answer(
                                st.session_state.questions[q_idx], answer
                            )
                            st.session_state.evaluations.append(eval_data)
                            st.session_state.answers.append(answer)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error evaluating answer: {str(e)}")
    else:
        eval_data = st.session_state.evaluations[q_idx]

        st.markdown("### \U0001f4cb Evaluation")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            val = eval_data.get("technical_accuracy", 5)
            css = "score-high" if val >= 8 else ("score-mid" if val >= 6 else "score-low")
            st.markdown(
                f'<div class="{css}" style="text-align:center;font-size:2rem;font-weight:700;">{val}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("<p style='text-align:center;font-size:0.85rem;color:#636e72;'>Technical<br>Accuracy</p>", unsafe_allow_html=True)
        with m2:
            val = eval_data.get("clarity", 5)
            css = "score-high" if val >= 8 else ("score-mid" if val >= 6 else "score-low")
            st.markdown(
                f'<div class="{css}" style="text-align:center;font-size:2rem;font-weight:700;">{val}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("<p style='text-align:center;font-size:0.85rem;color:#636e72;'>Clarity</p>", unsafe_allow_html=True)
        with m3:
            val = eval_data.get("depth", 5)
            css = "score-high" if val >= 8 else ("score-mid" if val >= 6 else "score-low")
            st.markdown(
                f'<div class="{css}" style="text-align:center;font-size:2rem;font-weight:700;">{val}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("<p style='text-align:center;font-size:0.85rem;color:#636e72;'>Depth</p>", unsafe_allow_html=True)
        with m4:
            val = eval_data.get("communication", 5)
            css = "score-high" if val >= 8 else ("score-mid" if val >= 6 else "score-low")
            st.markdown(
                f'<div class="{css}" style="text-align:center;font-size:2rem;font-weight:700;">{val}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("<p style='text-align:center;font-size:0.85rem;color:#636e72;'>Communication</p>", unsafe_allow_html=True)

        overall = eval_data.get("overall", 5)
        css = "score-high" if overall >= 8 else ("score-mid" if overall >= 6 else "score-low")
        st.markdown(
            f"<p style='text-align:center;font-size:1.2rem;'>Overall Score: "
            f"<span class='{css}'>{overall}/10</span></p>",
            unsafe_allow_html=True,
        )

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f'<div class="feedback-section"><strong>\U00002b06 Strengths</strong><br>'
                f'{eval_data.get("strengths", "N/A")}</div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f'<div class="feedback-section"><strong>\U0001f4a1 Areas to Improve</strong><br>'
                f'{eval_data.get("improvements", "N/A")}</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<div class="feedback-section"><strong>\U0001f4ac Detailed Feedback</strong><br>'
            f'{eval_data.get("feedback", "N/A")}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="feedback-section" style="border-left-color: #27AE60;">'
            f'<strong>\U00002705 Model Answer</strong><br>'
            f'{eval_data.get("model_answer", "N/A")}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        if q_idx < total - 1:
            _, center, _ = st.columns([1, 2, 1])
            with center:
                if st.button("\u27a1\ufe0f Next Question", use_container_width=True, type="primary"):
                    st.session_state.current_q += 1
                    st.rerun()
        else:
            _, center, _ = st.columns([1, 2, 1])
            with center:
                if st.button("\U0001f3af View Results", use_container_width=True, type="primary"):
                    with st.spinner("Generating your performance summary..."):
                        try:
                            client = get_llm_client()
                            if not client:
                                st.error("API key not configured.")
                                st.stop()
                            summary = client.generate_summary(
                                st.session_state.domain,
                                st.session_state.difficulty,
                                total,
                                st.session_state.evaluations,
                            )
                            st.session_state.summary = summary
                        except Exception as e:
                            st.error(f"Error generating summary: {str(e)}")
                            avg = sum(
                                e.get("overall", 5) for e in st.session_state.evaluations
                            ) / max(len(st.session_state.evaluations), 1)
                            st.session_state.summary = {
                                "overall_score": round(avg, 1),
                                "skill_breakdown": {},
                                "strongest_areas": ["N/A"],
                                "weakest_areas": ["N/A"],
                                "recommended_topics": ["N/A"],
                                "learning_path": ["N/A"],
                            }
                    st.session_state.page = "dashboard"
                    st.rerun()

# -------------------------------------------------------------------
# Page: Dashboard
# -------------------------------------------------------------------
def show_dashboard_page():
    if not st.session_state.summary:
        st.error("No summary data available. Please complete an interview first.")
        if st.button("\U0001f504 Start New Interview"):
            st.session_state.page = "setup"
            st.rerun()
        return

    summary = st.session_state.summary
    evaluations = st.session_state.evaluations
    questions = st.session_state.questions

    st.markdown("# \U0001f3c6 Your Performance Dashboard")
    st.markdown("---")

    overall = summary.get("overall_score", 0)
    css = "score-high" if overall >= 8 else ("score-mid" if overall >= 6 else "score-low")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            f"<div style='text-align:center;padding:2rem;background:#FFF5F5;border-radius:16px;border:1px solid #FFCDD2;'>"
            f"<p style='font-size:0.9rem;color:#636e72;margin:0;text-transform:uppercase;letter-spacing:1px;'>Overall Score</p>"
            f"<p style='font-size:4rem;font-weight:800;margin:0.5rem 0;' class='{css}'>{overall}</p>"
            f"<p style='font-size:1.2rem;color:#636e72;'>out of 10</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown("### \U0001f4ca Skill Breakdown")
        skills = summary.get("skill_breakdown", {})
        if skills:
            for label, key in [
                ("Technical Accuracy", "technical_accuracy"),
                ("Clarity", "clarity"),
                ("Depth", "depth"),
                ("Communication", "communication"),
            ]:
                val = skills.get(key, 0)
                val_css = "score-high" if val >= 8 else ("score-mid" if val >= 6 else "score-low")
                st.markdown(
                    f"<p style='margin:0.5rem 0;font-size:0.9rem;color:#2D3436;'>{label}</p>"
                    f"<div style='background:#FFCDD2;border-radius:8px;height:12px;width:100%;'>"
                    f"<div style='background:#DC3545;border-radius:8px;height:12px;width:{val*10}%;'></div>"
                    f"</div>"
                    f"<p style='margin:0 0 0.8rem 0;text-align:right;font-size:0.85rem;' class='{val_css}'>{val}/10</p>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("Skill breakdown not available.")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### \U00002b06 Strongest Areas")
        for area in summary.get("strongest_areas", []):
            st.markdown(f"- {area}")
        st.markdown("### \U0001f4a1 Areas for Improvement")
        for area in summary.get("weakest_areas", []):
            st.markdown(f"- {area}")

    with col2:
        st.markdown("### \U0001f4da Recommended Topics")
        for topic in summary.get("recommended_topics", []):
            st.markdown(f"- {topic}")
        st.markdown("### \U0001f4d6 Learning Path")
        for i, step in enumerate(summary.get("learning_path", []), 1):
            st.markdown(f"**{i}.** {step}")

    st.markdown("---")

    st.markdown("### \U0001f5b8\ufe0f Download PDF Report")
    name = st.text_input(
        "Enter your name for the report",
        value=st.session_state.candidate_name,
        placeholder="e.g., John Doe",
    )
    if name:
        st.session_state.candidate_name = name

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if name and st.button("\U0001f4c4 Generate PDF Report", use_container_width=True, type="primary"):
            with st.spinner("Generating your PDF report..."):
                try:
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    pdf_buffer = generate_pdf(
                        candidate_name=name,
                        domain=st.session_state.domain,
                        difficulty=st.session_state.difficulty,
                        question_count=st.session_state.total_questions,
                        overall_score=overall,
                        summary=summary,
                        evaluations=evaluations,
                        questions=questions,
                    )
                    filename = f"MockMate_Report_{name.replace(' ', '_')}_{date_str}.pdf"

                    st.download_button(
                        label="\U0001f4e5 Download PDF",
                        data=pdf_buffer,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True,
                    )

                    history_record = {
                        "candidate_name": name,
                        "date": date_str,
                        "domain": st.session_state.domain,
                        "difficulty": st.session_state.difficulty,
                        "question_count": st.session_state.total_questions,
                        "final_score": overall,
                        "pdf_filename": filename,
                    }
                    st.session_state.session_history.append(history_record)
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
        elif not name:
            st.info("Enter your name above to enable PDF download.")

    st.markdown("---")
    _, center, _ = st.columns([1, 2, 1])
    with center:
        if st.button("\U0001f504 Start New Interview", use_container_width=True, type="secondary"):
            st.session_state.page = "setup"
            st.session_state.interview_started = False
            st.rerun()

# -------------------------------------------------------------------
# Page: History
# -------------------------------------------------------------------
def show_history_page():
    st.markdown("# \U0001f4ca Interview History")
    st.markdown("---")

    history = st.session_state.session_history

    if not history:
        st.info("No interviews completed in this session. Start your first interview!")
        _, center, _ = st.columns([1, 2, 1])
        with center:
            if st.button("\U000025b6 Start Interview", use_container_width=True, type="primary"):
                st.session_state.page = "setup"
                st.rerun()
        return

    st.markdown(f"**{len(history)}** interview(s) in this session.")

    for i, record in enumerate(reversed(history)):
        score = record.get("final_score", 0)
        css = "score-high" if score >= 8 else ("score-mid" if score >= 6 else "score-low")
        with st.expander(
            f"**{record.get('candidate_name', 'Unknown')}** — "
            f"{record.get('domain', 'N/A')} | "
            f"{record.get('difficulty', 'N/A')} | "
            f"Score: <span class='{css}'>{score}/10</span>",
            expanded=(i == 0),
        ):
            det1, det2 = st.columns(2)
            with det1:
                st.markdown(f"**Date:** {record.get('date', 'N/A')}")
                st.markdown(f"**Domain:** {record.get('domain', 'N/A')}")
                st.markdown(f"**Difficulty:** {record.get('difficulty', 'N/A')}")
            with det2:
                st.markdown(f"**Questions:** {record.get('question_count', 0)}")
                st.markdown(f"**Score:** {score}/10")
                pdf_fn = record.get("pdf_filename", "")
                if pdf_fn:
                    st.markdown(f"**Report:** {pdf_fn}")

# -------------------------------------------------------------------
# Router
# -------------------------------------------------------------------
page = st.session_state.page

if page == "setup":
    show_setup_page()
elif page == "interview":
    show_interview_page()
elif page == "dashboard":
    show_dashboard_page()
elif page == "history":
    show_history_page()
