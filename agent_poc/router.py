import json
from groq_client import call_groq
from config import MODELS
from schemas import RouterOutput, ActionType


ROUTER_SYSTEM_PROMPT = """You are a routing agent. Your ONLY job is to decide what action to take for a user query.

You must respond with ONLY valid JSON, no other text.

Available actions:
- "web_search": Use for current events, news, or general info not covered by other tools
- "wikipedia_search": Use for definitions, historical facts, scientific concepts, people, and general knowledge
- "arxiv_search": Use for searching scientific research papers (physics, CS, math, etc.)
- "finance_tool": Use for stock prices, market cap, and financial data (e.g., "AAPL price", "price of Bitcoin")
- "weather_tool": Use for current weather information for a specific city
- "math_solver": Use for mathematical calculations (numbers and operators only)
- "direct_answer": Use for simple chitchat (greetings) or questions about the agent itself

Rules:
- You MAY choose multiple actions if the query requires distinct information (e.g., "weather in Tokyo and stock price of Sony")
- Choose "direct_answer" ONLY if no other tool is relevant
- Do NOT answer the user's question
- Do NOT add any explanation outside the JSON

Output format:
{"actions": ["action1", "action2"], "reason": "brief explanation"}"""


def route(user_query: str) -> RouterOutput:
    response = call_groq(
        model=MODELS["router"],
        system_prompt=ROUTER_SYSTEM_PROMPT,
        messages=user_query
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
        # Handle both single action (legacy) and list of actions
        raw_actions = data.get("actions", [])
        if not raw_actions and "action" in data:
            raw_actions = [data["action"]]
            
        return RouterOutput(
            actions=[ActionType(a) for a in raw_actions],
            reason=data.get("reason", "")
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        return RouterOutput(
            actions=[ActionType.DIRECT_ANSWER],
            reason="Failed to parse router response, defaulting to direct answer"
        )
