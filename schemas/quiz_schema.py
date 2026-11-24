
from pydantic import BaseModel, Field
from typing import Literal


class MCQOption(BaseModel):
    key: Literal["A", "B", "C", "D"]
    text: str


class MCQQuestion(BaseModel):
    question: str

    options: list[MCQOption] = Field(
        min_length=4,
        max_length=4
    )

    correct_answer: Literal["A", "B", "C", "D"]

    explanation: str


class MCQQuiz(BaseModel):
    topic: str
    questions: list[MCQQuestion]
