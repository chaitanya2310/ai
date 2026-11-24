
import re

from agents.tutor_agent import tutor_agent
from agents.planner_agent import planner_agent
from agents.quiz_agent import quiz_agent

PLAN_RE = re.compile(
    r"\b(study plan|plan|schedule|timetable|roadmap|revision plan|"
    r"\d+\s*-?\s*(day|days|week|weeks|month|months))\b", re.I)
QUIZ_RE = re.compile(
    r"\b(quiz|mcq|mcqs|practice questions?|test me|test my|"
    r"questions? (on|about)|assessment)\b", re.I)
TUTOR_RE = re.compile(
    r"\b(explain|what is|what are|what's|teach|describe|how does|how do|"
    r"why|difference|meaning|define|understand|tell me|about)\b", re.I)


def route_request(question: str):
    """Rule-based routing: only the agents the student really asked for."""
    wants_plan = bool(PLAN_RE.search(question))
    wants_quiz = bool(QUIZ_RE.search(question))
    wants_tutor = bool(TUTOR_RE.search(question)) or not (wants_plan or wants_quiz)

    # "give me a quiz about java" contains "about" but is NOT a tutor request
    if (wants_plan or wants_quiz) and not re.search(
            r"\b(explain|what is|what are|what's|teach|describe|how does|"
            r"how do|why|difference|meaning|define|understand)\b",
            question, re.I):
        wants_tutor = False

    agents = []
    if wants_tutor:
        agents.append(tutor_agent)
    if wants_plan:
        agents.append(planner_agent)
    if wants_quiz:
        agents.append(quiz_agent)
    return agents


def get_agents(decision):  # kept for backward compatibility
    decision = decision.upper()
    selected = []
    if "TUTOR" in decision:
        selected.append(tutor_agent)
    if "PLANNER" in decision:
        selected.append(planner_agent)
    if "QUIZ" in decision:
        selected.append(quiz_agent)
    return selected