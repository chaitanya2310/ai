from crewai import Agent,LLM
llm=LLM(model="ollama/qwen3:4b ",base_url="http://localhost:11434",temperature=0)
tutor_agent=Agent(
    role="student tutor",
    goal="explain academic concepts clearly and simply",
    backstory="""
    You are an experienced student tutor.
    You explain difficult concepts using simple language,
    examples, and step-by-step explanations.
    You adap""",
    llm=llm,
    verbose=True,
    allow_delegation=False


)