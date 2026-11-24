from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from crewai import Crew, Process

from agents.manager_agent import manager_agent
from agents.cordinator_agent import coordinator_agent
from tasks.manager_task import manager_task
from tasks.router_task import create_task
from tasks.cordinator_task import create_coordinator_task
from router import route_request
try:
    from guardrails_validate.inputg import validate_input
except Exception as e:  # guardrail import must never stop the API from starting
    print(f"WARNING: input guardrail disabled: {e}", flush=True)

    def validate_input(text):
        return (bool(str(text).strip()), "ok")

from app.database import final_exact_answer, save_memory
from app.memory import search_memories, store_memory
from dashboard.dash_board_db import log_conversation, extract_topic
import time
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Student Assistant API", version="1.0.0")


class StudentRequest(BaseModel):
    question: str
    user_id: str = "student_1"


# The agents are shared module-level objects. CrewAI refuses to run the same
# agent twice at once ("Executor is already running"), so only one crew may
# run at a time. Extra requests simply wait their turn.
crew_lock = threading.Lock()


def run(agents, tasks, **kw):
    with crew_lock:
        return Crew(agents=agents, tasks=tasks,
                    process=Process.sequential, verbose=True).kickoff(**kw)


@app.get("/")
def home():
    return {"message": "Student Assistant API is running"}



@app.post("/ask")
def ask_student(request: StudentRequest, background: BackgroundTasks):
    ok, msg = validate_input(request.question)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    try:
        return _ask(request, background)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("ASK FAILED")
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


def _ask(request: StudentRequest, background: BackgroundTasks):
    print("Ask endpoint started ",flush=True)


    total_start = time.perf_counter()

    question = request.question.strip()
    user_id = request.user_id

    # 1. MySQL exact match
    print("mysql cache check completed",flush=True)

    start = time.perf_counter()
    cached = final_exact_answer(user_id, question)
    logger.info("MYSQL CACHE: %.2f sec",
                time.perf_counter() - start)

    if cached:
        background.add_task(log_conversation, user_id, question,
                            extract_topic(question), "cache", "mysql")
        return {
            "question": question,
            "source": "mysql",
            "agents": [],
            "answer": cached
        }

    # 2. Mem0 memory search
    print("memo search completed ",flush=True)
    start = time.perf_counter()
    context = search_memories(user_id, question)
    logger.info("MEM0 SEARCH: %.2f sec",
                time.perf_counter() - start)

    enriched = (
        f"{question}\n\nStudent background:\n{context}"
        if context else question
    )

    # 3. Route the request (rule-based: fast and predictable)
    agents = route_request(question)
    decision = ", ".join(a.role for a in agents)
    logger.info("ROUTED TO: %s", decision)

    # 4. Specialist agents
    print("specialist agent started", flush=True)
    start = time.perf_counter()

    tasks = [create_task(a, enriched) for a in agents]
    specialist_result = run(agents, tasks)

    logger.info("SPECIALISTS: %.2f sec", time.perf_counter() - start)

    # 5. Build the final answer WITHOUT letting a small LLM rewrite it
    titles = {"student tutor": "Explanation",
              "study planner": "Study Plan",
              "quiz master": "Quiz"}
    outputs = getattr(specialist_result, "tasks_output", None) or []
    if len(agents) == 1:
        answer = str(specialist_result)
    else:
        parts = []
        for a, out in zip(agents, outputs):
            title = titles.get(a.role.strip().lower(), a.role)
            parts.append(f"## {title}\n\n{getattr(out, 'raw', str(out))}")
        answer = "\n\n---\n\n".join(parts) or str(specialist_result)

    
    background.add_task(log_conversation, user_id, question,
                        extract_topic(question), decision, "agents")

    # 6. Save memory in background
    background.add_task(
        store_memory,
        user_id,
        question,
        answer
    )

    # 7. Save tutor answer to MySQL
    if len(agents) == 1 and agents[0].role.strip().lower() == "student tutor":
        start = time.perf_counter()
        save_memory(user_id, question, answer)

        logger.info("MYSQL SAVE: %.2f sec",
                    time.perf_counter() - start)

    logger.info("TOTAL API TIME: %.2f sec",
                time.perf_counter() - total_start)
    print(f"total time:{time.perf_counter()-total_start:.2f}seconds",flush=True)    
    return {
        "question": question,
        "source": "agents",
        "manager_decision": decision,
        "agents": [a.role for a in agents],
        "answer": answer
    }
@app.get("/test-print")
def test_print():

    print("HELLO FROM API TERMINAL", flush=True)

    return {"message": "Print test successful"}