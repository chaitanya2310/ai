from crewai import Agent, LLM


llm = LLM(
    model="ollama/qwen3:4b    ",
    base_url="http://localhost:11434",
    temperature=0
)


planner_agent = Agent(
    role="Study Planner",

    goal="Create realistic and effective study plans for students.",

    backstory="""
    You are an experienced academic study planner.
    You help students organize their subjects,
    divide large topics into smaller tasks,
    and create practical daily study schedules.
    """,

    llm=llm,
    verbose=True,

    allow_delegation=False
)