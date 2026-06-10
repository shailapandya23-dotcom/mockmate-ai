import json
import re

from google import genai

from utils.prompts import QUESTION_GEN_PROMPT, EVALUATION_PROMPT, SUMMARY_PROMPT


class GeminiClient:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash"

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
        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )
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
        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )
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
        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )
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
