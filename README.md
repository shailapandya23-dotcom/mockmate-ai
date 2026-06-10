# MockMate AI

An AI-powered technical interview simulator built with **Streamlit** and **Google Gemini API**. Practice realistic interview questions across multiple domains with instant AI evaluation and personalized feedback.

## Features

- **Multi-domain interviews** — DSA, DBMS, OS, CN, ML, or Mixed
- **Adjustable difficulty** — Easy, Medium, or Hard
- **Flexible length** — 5, 10, or 20 questions
- **AI evaluation** — Scores on Technical Accuracy, Clarity, Depth, and Communication
- **Performance dashboard** — Overall score, skill breakdown, strengths, weaknesses, learning path
- **PDF scorecard** — Download a professional report with question-wise evaluation
- **Question memory** — Avoids repeating similar questions across sessions
- **Interview history** — View past interview results

## Live Demo

[Deploy to Streamlit Cloud](https://streamlit.io/cloud) using this repository.

## Tech Stack

- **Python** — Core language
- **Streamlit** — Web framework
- **Groq API** (default) or **Google Gemini** — Question generation & answer evaluation
- **ReportLab** — PDF report generation
- **JSON** — Local data storage

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/shailapandya23-dotcom/mockmate-ai.git
cd mockmate-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get a free API key

**Recommended: Groq** (free, no credit card, 30 req/min)

Go to [console.groq.com](https://console.groq.com), sign up, and create an API key.

**Alternative: Google Gemini** (free tier with limits)

Go to [Google AI Studio](https://aistudio.google.com/apikey) and create an API key.

### 4. Configure your API key

Create `.streamlit/secrets.toml`:

```toml
# For Groq (recommended):
LLM_PROVIDER = "groq"
GROQ_API_KEY = "gsk_your-groq-api-key"

# For Google Gemini:
# LLM_PROVIDER = "gemini"
# GEMINI_API_KEY = "your-gemini-api-key"
```

### 5. Run the app

```bash
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in
3. Click **New app** → select this repository
4. Set main file to `app.py`
5. In **Settings → Secrets**, add:

   ```toml
   LLM_PROVIDER = "groq"
   GROQ_API_KEY = "gsk_your-groq-api-key"
   ```

6. Click **Deploy**

## Project Structure

```
mockmate-ai/
├── app.py                       # Main Streamlit application
├── requirements.txt             # Python dependencies
├── .streamlit/
│   ├── config.toml              # Streamlit theme & server config
│   └── secrets.example.toml     # Example secrets file
├── data/
│   ├── question_memory.json     # Tracks used questions (auto-created)
│   └── history/
│       └── history.json         # Interview history (auto-created)
    └── utils/
        ├── llm_client.py            # Groq/Gemini API wrapper + prompt templates
        ├── pdf_generator.py         # PDF report generation
        ├── session.py               # Session state management
        └── storage.py               # JSON file I/O
```
