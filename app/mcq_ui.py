import streamlit as st
from app.test_service import generate_mcq_test
from dashboard.dash_board_db import log_quiz_score, USER_ID


def render_mcq_page():

    st.title("📝 Multiple Choice Test")

    # Step 1: Enter test details
    if "mcq_quiz" not in st.session_state:
        st.session_state.mcq_quiz = None

    if "mcq_submitted" not in st.session_state:
        st.session_state.mcq_submitted = False

    if "mcq_score" not in st.session_state:
        st.session_state.mcq_score = None

    # Step 2: Generate test
    if st.session_state.mcq_quiz is None:

        topic = st.text_input(
            "Enter your test topic",
            placeholder="Example: Python Functions"
        )

        difficulty = st.selectbox(
            "Select difficulty",
            ["Easy", "Medium", "Hard"]
        )

        total_questions = st.selectbox(
            "Number of questions",
            [5, 10, 15, 20]
        )

        if st.button("Generate MCQ Test"):

            if not topic.strip():
                st.warning("Please enter a topic.")

            else:
                with st.spinner("Generating your test..."):

                    try:
                        quiz = generate_mcq_test(
                            topic=topic,
                            difficulty=difficulty,
                            total_questions=total_questions
                        )

                        st.session_state.mcq_quiz = quiz
                        st.session_state.mcq_difficulty = difficulty
                        st.rerun()

                    except Exception as e:
                        st.error(f"Test generation failed: {e}")

    # Step 3: Display questions
    else:

        quiz = st.session_state.mcq_quiz

        st.subheader(f"Topic: {quiz['topic']}")
        st.write(f"Total Questions: {len(quiz['questions'])}")

        if not st.session_state.mcq_submitted:

            with st.form("mcq_test_form"):

                for index, question in enumerate(
                    quiz["questions"], start=1
                ):

                    st.markdown(
                        f"**Question {index}: {question['question']}**"
                    )

                    option_map = {
                        option["key"]: option["text"]
                        for option in question["options"]
                    }

                    st.radio(
                        "Choose your answer:",
                        options=["Select an answer", "A", "B", "C", "D"],
                        format_func=lambda key, options=option_map: (
                            "Select an answer"
                            if key == "Select an answer"
                            else f"{key}. {options[key]}"
                        ),
                        key=f"mcq_answer_{index}"
                    )

                    st.divider()

                submitted = st.form_submit_button("Submit Test")

            if submitted:

                answers = []
                unanswered = []

                for index in range(1, len(quiz["questions"]) + 1):

                    answer = st.session_state[
                        f"mcq_answer_{index}"
                    ]

                    if answer == "Select an answer":
                        unanswered.append(index)

                    answers.append(answer)

                if unanswered:
                    st.warning(
                        f"Please answer all questions. "
                        f"Unanswered: {unanswered}"
                    )

                else:
                    score = 0

                    for question, answer in zip(
                        quiz["questions"], answers
                    ):
                        if answer == question["correct_answer"]:
                            score += 1

                    st.session_state.mcq_score = score
                    log_quiz_score(
                        USER_ID, quiz["topic"],
                        st.session_state.get("mcq_difficulty", ""),
                        score, len(quiz["questions"]))
                    st.session_state.mcq_submitted = True
                    st.rerun()

        # Step 4: Display score and explanations
        else:

            score = st.session_state.mcq_score
            total = len(quiz["questions"])
            percentage = (score / total) * 100

            st.success("Test completed!")

            st.metric("Your Score", f"{score}/{total}")
            st.metric("Percentage", f"{percentage:.2f}%")

            for index, question in enumerate(
                quiz["questions"], start=1
            ):

                user_answer = st.session_state[
                    f"mcq_answer_{index}"
                ]

                correct_answer = question["correct_answer"]

                st.markdown(
                    f"**Question {index}: {question['question']}**"
                )

                st.write(f"Your answer: {user_answer}")
                st.write(f"Correct answer: {correct_answer}")

                if user_answer == correct_answer:
                    st.success("Correct!")
                else:
                    st.error("Incorrect!")

                st.info(
                    f"Explanation: {question['explanation']}"
                )

                st.divider()

            if st.button("Take Another Test"):

                st.session_state.mcq_quiz = None
                st.session_state.mcq_submitted = False
                st.session_state.mcq_score = None
                st.rerun()
