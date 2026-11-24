from crewai import Task
from agents.manager_agent import manager_agent


manager_task = Task(
    description="""
    Analyze the student's request:

    {student_request}

    Decide which specialist agents are required.

    Available specialists:

    TUTOR:
    Use when the student wants:
    - An explanation
    - An academic concept explained
    - Examples
    - Help understanding a topic

    PLANNER:
    Use when the student wants:
    - A study plan
    - An exam preparation schedule
    - A daily study schedule
    - Help organizing subjects or topics

    QUIZ:
    Use when the student wants:
    - A quiz
    - Practice questions
    - Questions to test knowledge
    - An assessment

    IMPORTANT:
    You can select ONE or MORE specialists.

    If only one specialist is needed, return one name.

    If multiple specialists are needed, return all required names.

    Examples:

    Request:
    "What is Python?"

    Return:
    TUTOR

    Request:
    "Create a 7-day Python study plan."

    Return:
    PLANNER

    Request:
    "Give me a Python quiz."

    Return:
    QUIZ

    Request:
    "Explain Python functions, create a 7-day study plan,
    and give me a quiz."

    Return:
    TUTOR, PLANNER, QUIZ

    Return ONLY the specialist names.
    Do not provide explanations.
    """,

    expected_output="""
    One or more specialist names:
    TUTOR
    PLANNER
    QUIZ

    Multiple names should be separated by commas.
    """,

    agent=manager_agent
)