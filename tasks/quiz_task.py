from crewai import Task
from agents.quiz_agent import quiz_agent
from schemas.quiz_schema import MCQQuiz


def create_mcq_task(topic, difficulty, total_questions):
    """Build a quiz Task. This must be a FUNCTION (it needs arguments)."""
    return Task(
        description=f"""
        Create a multiple choice test.

        Topic: {topic}
        Difficulty: {difficulty}
        Number of questions: exactly {total_questions}

        Rules:
        - Every question has exactly 4 options with keys A, B, C, D.
        - correct_answer must be one of "A", "B", "C", "D".
        - Include a short explanation for every question.
        - Return ONLY valid JSON, no extra text, no markdown fences.

        JSON format:
        {{
          "topic": "{topic}",
          "questions": [
            {{
              "question": "...",
              "options": [
                {{"key": "A", "text": "..."}},
                {{"key": "B", "text": "..."}},
                {{"key": "C", "text": "..."}},
                {{"key": "D", "text": "..."}}
              ],
              "correct_answer": "A",
              "explanation": "..."
            }}
          ]
        }}
        """,
        expected_output="A JSON object matching the MCQ quiz format.",
        agent=quiz_agent,
        output_pydantic=MCQQuiz,
    )