<p align="center">
  <h1 align="center">🎯 MockMate AI</h1>
  <p align="center">
    <em>AI-Powered Technical Interview Simulator</em>
  </p>
</p>

<p align="center">
  <a href="https://mockmate-ai-sp.streamlit.app/">
    <img src="https://img.shields.io/badge/Live_App-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live App">
  </a>
  <img src="https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/AI-Groq_|_Gemini-10B981?style=for-the-badge" alt="AI">
  <img src="https://img.shields.io/badge/PDF-ReportLab-DC3545?style=for-the-badge" alt="PDF">
</p>

---

## 🚀 How to Use

**Step 1** — Go to the [live app](https://mockmate-ai-sp.streamlit.app/)

**Step 2** — Configure your interview:
- Pick a **Domain**: `DSA` `DBMS` `OS` `CN` `ML` `Mixed`
- Pick **Difficulty**: `Easy` `Medium` `Hard`
- Pick **Question Count**: `5` `10` `20`

**Step 3** — Click **Start Interview**. AI generates practical, scenario-based questions instantly.

**Step 4** — Answer each question. Submit to get scored on **4 metrics** plus a **model answer** for comparison.

**Step 5** — View your **Dashboard** with overall score, skill breakdown, strengths, weaknesses, and a personalized learning path.

**Step 6** — **Download PDF Scorecard** — enter your name and get a professional report.

---

## ⚙️ Architecture

<pre>
                    ┌──────────────┐
                    │   🎯 User    │
                    │   Selects    │
                    │ Domain/Diff  │
                    │ /Count       │
                    └──────┬───────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │    Streamlit App 🖥️     │
              │   (app.py — 4 pages)    │
              │                         │
              │  ┌───┐ ┌──────┐ ┌─────┐ │
              │  │Setup││Interview││Dash.│ │
              │  └───┘ └──────┘ └─────┘ │
              └──────────┬──────────────┘
                         │
               ┌─────────┴──────────┐
               ▼                    ▼
     ┌──────────────────┐  ┌──────────────┐
     │  🤖 AI Engine    │  │  📄 Report   │
     │  (Groq / Gemini)  │  │  Generator   │
     │                  │  │  (ReportLab)  │
     │ • Generates Qs   │  └──────┬───────┘
     │ • Evaluates ans  │         │
     │ • Creates summ.  │         ▼
     └──────────────────┘  ┌──────────────┐
                           │  PDF Report  │
                           │  Scorecard   │
                           └──────────────┘
</pre>

---

## ✨ Features

### 🎓 Interview Experience
- **6 Domains** — DSA, DBMS, OS, CN, ML, or Mixed
- **3 Difficulty Levels** — Easy, Medium, Hard
- **Flexible Length** — 5, 10, or 20 questions
- **Scenario-Based** — Practical, interview-style questions (no textbook definitions)
- **Question Memory** — AI avoids repeating similar questions across sessions

### 📊 AI Evaluation
After each answer, you get scored on **4 metrics** (1–10):

| Metric | What it measures |
|---|---|
| **Technical Accuracy** | Is the content correct and precise? |
| **Clarity** | How clear and logical is the structure? |
| **Depth** | Does it show deep understanding? |
| **Communication** | How effectively is it delivered? |

Plus: ✅ **Overall Score** · 💪 **Strengths** · 📈 **Areas to Improve** · 💬 **Detailed Feedback** · 📝 **Model Answer**

### 📈 Performance Dashboard
- **Overall Score** — Color-coded (green / orange / red)
- **Skill Breakdown** — Visual bars for all 4 metrics
- **Strengths & Weaknesses** — AI-identified patterns across all answers
- **Learning Path** — 5-step personalized recommendation

### 📄 PDF Scorecard
Professional report including:
- Candidate name, Date, Domain, Difficulty, Question count
- Overall score & skill breakdown
- Strengths & areas for improvement
- Learning recommendations
- Question-wise evaluation table

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit (red/white theme) |
| **Backend** | Python 3.14, Session State |
| **AI** | Groq API / Google Gemini |
| **Reports** | ReportLab (PDF) |
| **Storage** | JSON files |

---

## 🔗 Links

- **Live App** → [mockmate-ai-sp.streamlit.app](https://mockmate-ai-sp.streamlit.app/)
- **GitHub** → [shailapandya23-dotcom/mockmate-ai](https://github.com/shailapandya23-dotcom/mockmate-ai)
