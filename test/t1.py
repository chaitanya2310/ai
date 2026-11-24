
from app.database import (
    save_chat,
    save_memory,
    final_exact_answer
)
user_id="s101"
question = "What is Python?"
answer = "Python is a high-level programming language."

# Save the conversation
if save_chat(question, answer):
    print("Chat saved successfully.")

# Save the reusable memory
if save_memory(
    user_id=user_id,
    memory_text=f"Question: {question}\nAnswer: {answer}",
    question=question,
    answer=answer
):
    print("Memory saved successfully.")

# Retrieve an exact matching question
saved_answer = final_exact_answer(user_id,question)

if saved_answer:
    print("\nRetrieved answer:")
    print(saved_answer)
else:
    print("No saved answer found.")
