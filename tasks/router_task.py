from crewai import Task


def create_task(agent, student_request):

    role = agent.role.strip().lower()

    if role == "student tutor":

        return Task(
            description=f"""
            The student's request is:

            {student_request}

            Your responsibility is ONLY to handle the tutoring part.

            Explain the requested academic concept clearly.
            Use simple language and examples where useful.

            Do not create a study plan.
            Do not create a quiz.
            """,

            expected_output="""
            A clear, beginner-friendly explanation of the
            academic concept requested by the student.
            """,

            agent=agent
        )

    elif role == "study planner":

        return Task(
            description=f"""
            The student's request is:

            {student_request}

            Your responsibility is ONLY to handle the planning part.

            Create a practical study plan based on the student's
            request.

            Include relevant days, topics, and study activities.

            Do not create a quiz.
            """,

            expected_output="""
            A practical study plan containing relevant
            days, topics, and study activities.
            """,

            agent=agent
        )

    elif role == "quiz master":

        return Task(
            description=f"""
            The student's request is:

            {student_request}

            Your responsibility is ONLY to handle the quiz part.

            Create a useful quiz based on the requested topic.

            Include questions, options where appropriate,
            correct answers, and short explanations.

            Do not create a study plan.
            """,

            expected_output="""
            A useful quiz with questions, answers,
            and short explanations.
            """,

            agent=agent
        )

    else:
        raise ValueError(
            f"Unknown agent role: {agent.role}"
        )