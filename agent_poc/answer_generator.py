from typing import List, Optional
from langchain_core.messages import BaseMessage, HumanMessage
from groq_client import call_groq
from config import MODELS


ANSWER_SYSTEM_PROMPT = """You are a helpful assistant that provides clear, accurate, and concise answers.

Rules:
- If tool results are provided, base your answer on them
- Maintian conversation continuity based on history
- Do NOT invent facts
- Do NOT expose your chain-of-thought
- Be direct and helpful
- Use clear, simple language"""


def generate_answer(user_query: str, tool_result: Optional[str] = None, history: List[BaseMessage] = []) -> str:
    # Prepare current context
    if tool_result:
        current_content = f"""User Query: {user_query}

Tool Result:
{tool_result}

Provide a clear, concise answer based on the tool result."""
    else:
        current_content = f"""User Query: {user_query}

Provide a clear, concise answer."""

    # Combine history + current message
    messages = history.copy()
    messages.append(HumanMessage(content=current_content))

    response = call_groq(
        model=MODELS["answer_generator"],
        system_prompt=ANSWER_SYSTEM_PROMPT,
        messages=messages
    )
    
    return response.strip()
