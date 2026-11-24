
# app/memory.py - Mem0 + Ollama + Chroma

from mem0 import Memory

memory = Memory.from_config({
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.2",
            "temperature": 0,
            "ollama_base_url": "http://localhost:11434"
        }
    },

    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": "http://localhost:11434"
        }
    },

    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "student_memory",
            "path": "./mem0_db"
        }
    }
})


def search_memories(user_id, question, top_k=3):
    try:
        res = memory.search(
            question,
            top_k=top_k,
            filters={"user_id": user_id}
        )

        return "\n".join(
            f"- {m['memory']}" for m in res["results"]
        )

    except Exception as e:
        print(f"mem0 search failed: {e}")
        return ""


def store_memory(user_id, question, answer):
    try:
        memory.add(
            [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer[:1500]}
            ],
            user_id=user_id
        )

    except Exception as e:
        print(f"mem0 add failed: {e}")
