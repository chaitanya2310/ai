from crewai import Task
from agents.tutor_agent import tutor_agent

tutor_task = Task(
    description="""
    Analyze the student's request:

    {student_request}

    If the request requires an explanation of an academic concept,
    provide a beginner-friendly explanation.

    Use simple language and examples.
    """,

    expected_output="""
    A clear and beginner-friendly explanation relevant
    to the student's request.
    """,

    agent=tutor_agent
)