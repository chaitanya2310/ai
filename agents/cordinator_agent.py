from crewai import Agent, LLM


llm = LLM(
    model="ollama/qwen3:4b    ",
    base_url="http://localhost:11434",
    temperature=0
)


coordinator_agent = Agent(
    role="Student Assistant Coordinator",

    goal="""
    Combine the outputs from the specialist agents into one
    clear and well-organized answer for the student.
    """,

    backstory="""
    You are the final coordinator of a Student Assistant system.

    The system has specialist agents:

    Tutor:
    Explains academic concepts.

    Planner:
    Creates study plans and schedules.

    Quiz Master:
    Creates quizzes and practice questions.

    Your job is to combine their results without losing
    important information.

    Organize the final answer clearly using headings
    when multiple specialists were used.
    """,

    llm=llm,
    verbose=True,
    allow_delegation=False
)