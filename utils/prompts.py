QUESTION_GEN_PROMPT = """You are a senior technical interviewer at a top tech company. Generate {count} {difficulty} difficulty interview questions for the domain of {domain}.

Guidelines:
- Each question must be practical, scenario-based, and interview-oriented
- Avoid textbook definitions — test real problem-solving ability
- Questions should resemble what a candidate would face at Google, Meta, Amazon, or similar
- Cover different sub-topics within {domain}
- Questions should require analytical thinking, not just factual recall

{fmemory_exclusions}

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
