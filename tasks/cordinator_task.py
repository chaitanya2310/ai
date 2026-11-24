from crewai import Task

from agents.cordinator_agent import coordinator_agent


def create_coordinator_task(specialist_results):

    return Task(
        description=f"""
        The specialist agents produced the following results:

        {specialist_results}

        Combine these results into one final answer for the student.

        Important rules:

        1. Keep the Tutor's explanation.
        2. Keep the Planner's study plan.
        3. Keep the Quiz Master's quiz.
        4. Do not invent information.
        5. Remove unnecessary repetition.
        6. Use clear headings when appropriate.
        """,

        expected_output="""
        One clear and well-organized final response
        combining the relevant specialist results.
        """,

        agent=coordinator_agent
    )