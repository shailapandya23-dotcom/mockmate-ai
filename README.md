# MockMate AI

An AI-powered technical interview simulator. Practice realistic interview questions across multiple domains with instant AI evaluation, personalized feedback, and downloadable PDF scorecards.

> **Live App:** [mockmate-ai-sp.streamlit.app](https://mockmate-ai-sp.streamlit.app/)

---

## How to Use

1. **Get a free API key** — Sign up at [console.groq.com](https://console.groq.com) (no credit card needed) and create a key
2. **Enter your key** — Paste it into the sidebar of the app
3. **Configure your interview** — Choose a domain (DSA, DBMS, OS, CN, ML, or Mixed), difficulty (Easy, Medium, Hard), and number of questions (5, 10, or 20)
4. **Start Interview** — AI instantly generates practical, scenario-based questions
5. **Answer each question** — Type your response, submit, and get scored on Technical Accuracy, Clarity, Depth, and Communication. A model answer is shown so you can compare
6. **View your Dashboard** — After all questions, see your overall score, skill breakdown, strongest and weakest areas, recommended topics, and a personalized learning path
7. **Download PDF Scorecard** — Enter your name and download a professional report with all results

## Features

- **6 Domains** — DSA, DBMS, OS, CN, ML, or Mixed
- **3 Difficulty Levels** — Easy, Medium, Hard
- **Flexible Length** — 5, 10, or 20 questions
- **4-Metric Evaluation** — Technical Accuracy, Clarity, Depth, Communication (each scored 1–10)
- **Model Answer** — See a correct answer after every response
- **Performance Dashboard** — Overall score, skill breakdown, strengths, weaknesses, learning path
- **PDF Scorecard** — Professional report with candidate name, date, domain, and question-wise evaluation
- **Auto-clearing History** — Session-based history (clears when you close the tab)

## Tech Stack

- **Python** + **Streamlit** — Web application
- **Groq API / Google Gemini** — AI question generation & evaluation
- **ReportLab** — PDF report generation
