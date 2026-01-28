from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class actionType(str, Enum):
    WEB_SEARCH = "web_search"
    WIKIPEDIA_SEARCH = "wikipedia_search"
    ARXIV_SEARCH = "arxiv_search"
    FINANCE_TOOL = "finance_tool"
    WEATHER_TOOL = "weather_tool"
    MATH_SOLVER = "math_solver"
    DIRECT_ANSWER = "direct_answer"


class PlanStepModel(BaseModel):
    id: int = Field(description="Unique ID for this step (1, 2, 3...)")
    tool: actionType = Field(description="The tool to execute")
    args: str = Field(description="The input arguments for the tool. Use {step_ID_result} to reference previous results.")
    dependency_ids: List[int] = Field(description="List of step IDs that must complete before this step can run")


class PlannerOutput(BaseModel):
    steps: List[PlanStepModel] = Field(description="The ordered list of steps to execute")
