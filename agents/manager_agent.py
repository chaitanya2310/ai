from crewai import Agent, LLM

llm = LLM(
    model="ollama/qwen3:4b    ",
    base_url="http://localhost:11434",
    temperature=0
)

manager_agent = Agent(
    role="Student Assistant Manager",

    goal="""
     Understand the student's request and delegate the work
     to the appropriate specialist agent.
    """,

    backstory="""
   You are the main coordinator of a Student Assistant system.

    You have three specialist agents:

    1. Student Tutor
       - Explains academic concepts
       - Answers student questions
       - Gives examples

    2. Study Planner
       - Creates study schedules
       - create exam preparation schedule
       - organize subjects and topics 

    3. Quiz Master
       - Creates quizzes
       - Creates practice questions
       - test student knowledge

    Analyze the meaning of the student's request and select the most appropriate specialist""",

    

    llm=llm,
    verbose=True,
    allow_delegation=True
)