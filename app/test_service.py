import json
import re

from crewai import Crew, Process
from agents.quiz_agent import quiz_agent
from tasks.quiz_task import create_mcq_task
from schemas.quiz_schema import MCQQuiz


def _extract_quiz(result):
    """Get an MCQQuiz from the crew result (pydantic first, raw JSON fallback)."""
    if getattr(result, "pydantic", None) is not None:
        return MCQQuiz.model_validate(result.pydantic)

    raw = str(getattr(result, "raw", result))
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("Model did not return JSON.")
    return MCQQuiz.model_validate(json.loads(match.group(0)))


def _validate(quiz, total_questions):
    if len(quiz.questions) != total_questions:
        raise ValueError(
            f"Expected {total_questions} questions, got {len(quiz.questions)}.")
    for q in quiz.questions:
        keys = {o.key for o in q.options}
        if keys != {"A", "B", "C", "D"}:
            raise ValueError("Every question must have options A, B, C, D.")


def generate_mcq_test(topic, difficulty, total_questions, retries=3):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            task = create_mcq_task(topic, difficulty, total_questions)
            crew = Crew(agents=[quiz_agent], tasks=[task],
                        process=Process.sequential, verbose=True)
            quiz = _extract_quiz(crew.kickoff())
            _validate(quiz, total_questions)
            return quiz.model_dump()
        except Exception as e:  # small local models often miss the format
            last_error = e
            print(f"MCQ attempt {attempt} failed: {e}", flush=True)
    raise ValueError(f"Could not generate a valid test: {last_error}")