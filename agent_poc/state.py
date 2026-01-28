from typing import List, Dict, Any, TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator


class PlanStep(TypedDict):
    id: int
    tool: str
    args: str
    dependency_ids: List[int]
    result: Any
    status: str  # "pending", "done", "error"


class AgentState(TypedDict):
    input: str
    plan: List[PlanStep]
    results: Dict[str, Any]  # Key: step_id, Value: result
    history: List[BaseMessage]
    final_answer: str
