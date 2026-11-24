import datetime

import pandas as pd
import streamlit as st

from dashboard.dash_board_db import (
    get_day_conversations, get_daily_counts, get_quiz_history, get_topic_stats,
)


def _show(df):
    """st.dataframe that works on old and new Streamlit versions."""
    try:
        st.dataframe(df, hide_index=True, width="stretch")
    except TypeError:
        st.dataframe(df, hide_index=True, use_container_width=True)


def _score_badge(pct):
    if pd.isna(pct):
        return "no test yet"
    icon = "🟢" if pct >= 75 else "🟡" if pct >= 50 else "🔴"
    return f"{icon} {pct:.0f}%"


def render_dashboard_page(user_id):
    st.title("📊 Student Dashboard")

    day = st.date_input("Select a day", value=datetime.date.today())

    convs = get_day_conversations(user_id, day)
    stats = get_topic_stats(user_id)
    history = get_quiz_history(user_id)

    if convs is None or stats is None or history is None:
        st.error("Cannot connect to MySQL. Check that MySQL is running and "
                 "MYSQL_PASSWORD in .env is correct.")
        return

    # ---- summary numbers
    tests_taken = len(history)
    avg_all = history["percentage"].astype(float).mean() if tests_taken else None
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Questions that day", len(convs))
    c2.metric("Topics that day", convs["topic"].nunique() if len(convs) else 0)
    c3.metric("Tests taken (all time)", tests_taken)
    c4.metric("Average score", f"{avg_all:.0f}%" if avg_all is not None else "-")

    # ---- topics of the selected day, with score
    st.subheader(f"📚 Topics on {day:%d %b %Y}")
    if convs.empty:
        st.info("No conversations on this day.")
    else:
        day_topics = (convs.assign(k=convs["topic"].str.lower())
                      .groupby("k", as_index=False)
                      .agg(Topic=("topic", "first"), questions=("question", "count")))
        if not stats.empty:
            s = stats.assign(k=stats["topic"].str.lower())[["k", "avg_score"]]
            day_topics = day_topics.merge(s, on="k", how="left")
        else:
            day_topics["avg_score"] = float("nan")
        day_topics["Score"] = day_topics["avg_score"].apply(_score_badge)
        _show(day_topics[["Topic", "questions", "Score"]]
                     .rename(columns={"questions": "Questions"}))

        st.subheader("💬 Conversations")
        _show(convs.rename(columns={"time": "Time", "topic": "Topic",
                                  "question": "Question", "agents": "Answered by"}))

    st.divider()

    # ---- overall topic scores
    st.subheader("🎯 Score by topic (all time)")
    if stats.empty:
        st.info("Nothing yet. Ask a question or take an MCQ test.")
    else:
        table = stats.copy()
        table["Score"] = table["avg_score"].apply(_score_badge)
        _show(table.rename(columns={"topic": "Topic",
                                  "questions_asked": "Questions asked",
                                  "tests_taken": "Tests taken",
                                  "best_score": "Best %"})
            [["Topic", "Questions asked", "Tests taken", "Score", "Best %"]])

        scored = stats.dropna(subset=["avg_score"])
        if not scored.empty:
            st.caption("Average test score (%) per topic")
            st.bar_chart(scored.set_index("topic")["avg_score"])

        weak = scored[scored["avg_score"] < 50]
        if not weak.empty:
            st.warning("Needs more practice: " + ", ".join(weak["topic"]))

    # ---- activity + quiz history
    counts = get_daily_counts(user_id, 14)
    if counts is not None and not counts.empty:
        st.subheader("📈 Questions per day (last 14 days)")
        st.bar_chart(counts.set_index("day")["questions"])

    st.subheader("📝 Recent tests")
    if history.empty:
        st.info("No tests taken yet.")
    else:
        _show(history.rename(columns={"taken_at": "Taken at", "topic": "Topic",
                                    "difficulty": "Difficulty", "score": "Score",
                                    "percentage": "%"}))