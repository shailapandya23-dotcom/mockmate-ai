import json
import os
import re
import time

from google import genai
from google.genai import errors as genai_errors

QUESTION_GEN_PROMPT = """You are a senior technical interviewer at a top tech company. Generate {count} {difficulty} difficulty interview questions for the domain of {domain}.

Guidelines:
- Each question must be practical, scenario-based, and interview-oriented
- Avoid textbook definitions — test real problem-solving ability
- Questions should resemble what a candidate would face at Google, Meta, Amazon, or similar
- Cover different sub-topics within {domain}
- Questions should require analytical thinking, not just factual recall

{memory_exclusions}

Return ONLY a valid JSON array of strings with exactly {count} questions. Example format:
["Question 1 text?", "Question 2 text?", ...]

No other text before or after the JSON array."""

EVALUATION_PROMPT = """You are a senior technical interviewer evaluating a candidate's response.

Question: {question}

Candidate's Answer: {answer}

Evaluate the answer on these criteria:
1. Technical Accuracy (1-10): Is the technical content correct and precise?
2. Clarity (1-10): How clearly and logically is the answer structured?
3. Depth (1-10): Does the answer demonstrate deep understanding beyond surface level?
4. Communication (1-10): How effectively is the answer communicated (language, conciseness)?

Be honest and constructive. Provide specific, actionable feedback.

Return your evaluation as a valid JSON object with exactly this structure (no markdown, no code blocks):
{{
    "technical_accuracy": <integer 1-10>,
    "clarity": <integer 1-10>,
    "depth": <integer 1-10>,
    "communication": <integer 1-10>,
    "overall": <float (average of all four)>,
    "strengths": "<string - 1-2 specific strengths>",
    "improvements": "<string - 1-2 specific areas to improve>",
    "feedback": "<string - 2-3 sentences of detailed feedback>"
}}"""

SUMMARY_PROMPT = """You are a senior technical interviewer generating a final performance report.

Domain: {domain}
Difficulty: {difficulty}
Total Questions: {count}

Here are the per-question evaluations:
{evaluations_json}

Based on ALL evaluations above, generate a comprehensive final summary.

Return your summary as a valid JSON object with exactly this structure (no markdown, no code blocks):
{{
    "overall_score": <float 0.0-10.0>,
    "skill_breakdown": {{
        "technical_accuracy": <float>,
        "clarity": <float>,
        "depth": <float>,
        "communication": <float>
    }},
    "strongest_areas": ["<area 1>", "<area 2>", "<area 3>"],
    "weakest_areas": ["<area 1>", "<area 2>", "<area 3>"],
    "recommended_topics": ["<topic 1>", "<topic 2>", "<topic 3>"],
    "learning_path": ["<step 1>", "<step 2>", "<step 3>", "<step 4>", "<step 5>"]
}}

Derive the overall_score and skill_breakdown as averages/composites from the evaluations provided."""


class GeminiClient:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
        self.max_retries = 3

    def _call_with_retry(self, prompt):
        for attempt in range(self.max_retries + 1):
            try:
                return self.client.models.generate_content(
                    model=self.model, contents=prompt
                )
            except genai_errors.ClientError as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    if attempt < self.max_retries:
                        delay = (2 ** attempt) * 5
                        time.sleep(delay)
                        continue
                if "404" in str(e) or "NOT_FOUND" in str(e):
                    raise RuntimeError(
                        f'Model "{self.model}" not found. Available models: '
                        'gemini-2.0-flash, gemini-2.0-flash-lite, gemini-1.5-pro. '
                        "Set GEMINI_MODEL in Secrets to one of these."
                    ) from e
                raise
            except Exception:
                raise

    def _extract_json(self, text):
        json_match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
        if json_match:
            text = json_match.group(1).strip()
        else:
            brace_match = re.search(r"\{.*\}", text, re.DOTALL)
            if brace_match:
                text = brace_match.group(0)
        return json.loads(text)

    def generate_questions(self, domain, difficulty, count, memory_exclusions=""):
        prompt = QUESTION_GEN_PROMPT.format(
            count=count,
            difficulty=difficulty,
            domain=domain,
            memory_exclusions=memory_exclusions,
        )
        response = self._call_with_retry(prompt)
        try:
            questions = self._extract_json(response.text)
        except Exception:
            lines = [
                q.strip().strip('"').strip("'")
                for q in response.text.strip().split("\n")
                if q.strip()
            ]
            questions = [q for q in lines if q and not q.startswith("[") and not q.endswith("]")]

        if not isinstance(questions, list):
            questions = [str(questions)]
        return questions[:count]

    def evaluate_answer(self, question, answer):
        prompt = EVALUATION_PROMPT.format(question=question, answer=answer)
        response = self._call_with_retry(prompt)
        try:
            result = self._extract_json(response.text)
        except Exception:
            return {
                "technical_accuracy": 5,
                "clarity": 5,
                "depth": 5,
                "communication": 5,
                "overall": 5.0,
                "strengths": "Evaluation parsing failed.",
                "improvements": "Evaluation parsing failed.",
                "feedback": response.text[:500],
            }
        required_keys = [
            "technical_accuracy",
            "clarity",
            "depth",
            "communication",
            "overall",
            "strengths",
            "improvements",
            "feedback",
        ]
        for key in required_keys:
            if key not in result:
                result[key] = "" if key in ("strengths", "improvements", "feedback") else 5
        return result

    def generate_summary(self, domain, difficulty, count, evaluations):
        evaluations_json = json.dumps(evaluations, indent=2)
        prompt = SUMMARY_PROMPT.format(
            domain=domain,
            difficulty=difficulty,
            count=count,
            evaluations_json=evaluations_json,
        )
        response = self._call_with_retry(prompt)
        try:
            result = self._extract_json(response.text)
        except Exception:
            avg = sum(e.get("overall", 5) for e in evaluations) / max(len(evaluations), 1)
            return {
                "overall_score": round(avg, 1),
                "skill_breakdown": {
                    "technical_accuracy": round(
                        sum(e.get("technical_accuracy", 5) for e in evaluations)
                        / max(len(evaluations), 1),
                        1,
                    ),
                    "clarity": round(
                        sum(e.get("clarity", 5) for e in evaluations)
                        / max(len(evaluations), 1),
                        1,
                    ),
                    "depth": round(
                        sum(e.get("depth", 5) for e in evaluations)
                        / max(len(evaluations), 1),
                        1,
                    ),
                    "communication": round(
                        sum(e.get("communication", 5) for e in evaluations)
                        / max(len(evaluations), 1),
                        1,
                    ),
                },
                "strongest_areas": ["General knowledge"],
                "weakest_areas": ["Areas to review"],
                "recommended_topics": ["Review core concepts"],
                "learning_path": [
                    "Review fundamental concepts",
                    "Practice with mock interviews",
                    "Study advanced topics",
                    "Build practical projects",
                    "Review and revise",
                ],
            }
        return result
