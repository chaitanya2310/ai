from crewai import Crew, Process
from agents.cordinator_agent import coordinator_agent
from tasks.cordinator_task import create_coordinator_task

from agents.manager_agent import manager_agent
from tasks.manager_task import manager_task

from router import get_agents
from tasks.router_task import create_task

from app.database import final_exact_answer, save_memory, save_chat
from app.memory import search_memories, store_memory
from guardrails_validate.inputg import validate_input

student_request = input("\nEnter your request: ")

is_valid, validation_message = validate_input(student_request)

if not is_valid:
    print(f"Invalid input: {validation_message}")
    raise SystemExit(1)

# =========================
# STEP 1: Manager
# =========================

manager_crew = Crew(
    agents=[manager_agent],
    tasks=[manager_task],
    process=Process.sequential,
    verbose=True
)

manager_result = manager_crew.kickoff(
    inputs={
        "student_request": student_request
    }
)

decision = str(manager_result).strip()

print("\n==============================")
print("MANAGER DECISION")
print("==============================")
print(decision)


# =========================
# STEP 2: Router
# =========================

selected_agents = get_agents(decision)

if not selected_agents:
    print("\nNo specialist was selected.")
    exit()


print("\n==============================")
print("SELECTED AGENTS")
print("==============================")

for agent in selected_agents:
    print("-", agent.role)


# =========================
# STEP 3: Create tasks
# =========================

specialist_tasks = []

for agent in selected_agents:
    print(f"\n creating task for :{agent.role}")

    task = create_task(
        agent,
        student_request
    )

    specialist_tasks.append(task)


# =========================
# STEP 4: Run specialists
# =========================

specialist_crew = Crew(
    agents=selected_agents,
    tasks=specialist_tasks,
    process=Process.sequential,
    verbose=True
)

result = specialist_crew.kickoff()
# =========================
# STEP 5: Coordinator
# =========================

coordinator_task = create_coordinator_task(
    result
)

coordinator_crew = Crew(
    agents=[coordinator_agent],
    tasks=[coordinator_task],
    process=Process.sequential,
    verbose=True
)

final_result = coordinator_crew.kickoff()


# =========================
# STEP 6: Final Answer
# =========================

print("\n==============================")
print("FINAL ANSWER")
print("==============================")

print(final_result)

