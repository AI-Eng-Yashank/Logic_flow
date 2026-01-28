import json
from typing import Optional
from groq_client import call_groq
from config import MODELS
from schemas import EvaluatorOutput


EVALUATOR_SYSTEM_PROMPT = """You are an answer quality evaluator. Your job is to validate if an answer is acceptable.

You must respond with ONLY valid JSON, no other text.

Checks to perform:
1. Is the answer relevant to the query?
2. If tool output was used, is the answer grounded in that output?
3. Does the answer violate any instructions (inventing facts, exposing reasoning)?

Output format:
{"pass": true | false, "issues": ["issue1", "issue2"]}

If no issues, return: {"pass": true, "issues": []}"""


def evaluate(user_query: str, answer: str, tool_result: Optional[str] = None) -> EvaluatorOutput:
    if tool_result:
        user_content = f"""User Query: {user_query}

Tool Result: {tool_result}

Answer to Evaluate: {answer}

Evaluate if this answer is acceptable."""
    else:
        user_content = f"""User Query: {user_query}

Answer to Evaluate: {answer}

Evaluate if this answer is acceptable."""

    response = call_groq(
        model=MODELS["evaluator"],
        system_prompt=EVALUATOR_SYSTEM_PROMPT,
        messages=user_content
    )
    
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    try:
        data = json.loads(cleaned)
        return EvaluatorOutput(
            pass_evaluation=data.get("pass", False),
            issues=data.get("issues", [])
        )
    except (json.JSONDecodeError, KeyError):
        return EvaluatorOutput(
            pass_evaluation=True,
            issues=[]
        )
