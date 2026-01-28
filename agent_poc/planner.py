from typing import List
from groq_client import call_groq
from config import MODELS
from schemas_dag import PlannerOutput
import json


PLANNER_SYSTEM_PROMPT = """You are an Agent Planner. Your job is to break down a user query into a Directed Acyclic Graph (DAG) of execution steps.

Available Tools:
- "web_search": News, current events, dynamic data.
- "wikipedia_search": Definitions, concepts, history, people.
- "arxiv_search": Scientific research papers.
- "finance_tool": Stock prices, market caps.
- "weather_tool": Weather forecasts (requires a City Name).
- "math_solver": Calculations (Logic: "{step_1} + 5").
- "direct_answer": If no tools are needed (chitchat).

Rules for Dependencies:
1. If a step requires information from another step (e.g., "Math" needs "Stock Price"), mark the ID of the first step in `dependency_ids`.
2. Use placeholders like `{step_1_result}` in the `args` field to refer to previous outputs.
3. Steps with NO dependencies (empty list) will run in PARALLEL.

Example 1: "Stock price of Apple and add 20%"
{
  "steps": [
    {"id": 1, "tool": "finance_tool", "args": "AAPL", "dependency_ids": []},
    {"id": 2, "tool": "math_solver", "args": "{step_1_result} * 1.20", "dependency_ids": [1]}
  ]
}

Example 2: "Weather in Tokyo and Paris"
{
  "steps": [
    {"id": 1, "tool": "weather_tool", "args": "Tokyo", "dependency_ids": []},
    {"id": 2, "tool": "weather_tool", "args": "Paris", "dependency_ids": []}
  ]
}

Output ONLY valid JSON matching the schema.
"""


def generate_plan(user_query: str) -> PlannerOutput:
    response = call_groq(
        model=MODELS["router"], # Using the small model for planning
        system_prompt=PLANNER_SYSTEM_PROMPT,
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
        return PlannerOutput(**data)
    except Exception as e:
        # Fallback for parsing errors
        print(f"Planner Error: {e}")
        return PlannerOutput(steps=[])
