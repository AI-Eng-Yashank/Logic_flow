from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class ActionType(str, Enum):
    WEB_SEARCH = "web_search"
    MATH_SOLVER = "math_solver"
    DIRECT_ANSWER = "direct_answer"
    WIKIPEDIA_SEARCH = "wikipedia_search"
    ARXIV_SEARCH = "arxiv_search"
    FINANCE_TOOL = "finance_tool"
    WEATHER_TOOL = "weather_tool"


class RouterOutput(BaseModel):
    actions: List[ActionType]
    reason: str


class WebSearchResult(BaseModel):
    title: str
    snippet: str
    url: str


class EvaluatorOutput(BaseModel):
    pass_evaluation: bool
    issues: List[str]
