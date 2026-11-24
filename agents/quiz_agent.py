from crewai import Agent, LLM


llm = LLM(
    model="ollama/qwen3:4b",
    base_url="http://localhost:11434",
    temperature=0
)


quiz_agent = Agent(
    role="Quiz Master",

    goal="Create useful quizzes to test a student's understanding.",

    backstory="""
    You are an experienced quiz creator and evaluator.
    You create questions appropriate for the student's level.
    You include a mixture of conceptual and practical questions.
    You clearly explain the correct answers.
    """,

    llm=llm,
    verbose=True,

    allow_delegation=False
)

