from crewai import Task
from agents.planner_agent import planner_agent
planner_task=Task(
  
     description="""
    Create a study plan for the following student request:

    {student_request}

    Break the subjects into daily tasks.
    Make the plan realistic for a student.
    Clearly mention what the student should study each day.""",
    expected_output="""
    A clear day-by-day study plan with:
    - Day number
    - Topics to study
    - Suggested focus for each day
    """,
    agent=planner_agent
)