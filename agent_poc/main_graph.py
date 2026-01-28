from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from state import AgentState, PlanStep
from schemas_dag import PlannerOutput, actionType
from planner import generate_plan
from answer_generator import generate_answer
from evaluator import evaluate
from memory import MemoryManager

# Import Tools
from tools.math_solver import solve_math
from tools.web_search import web_search
from tools.wikipedia_search import wikipedia_search
from tools.arxiv_search import arxiv_search
from tools.finance_tool import get_stock_price
from tools.weather_tool import get_weather


def plan_node(state: AgentState) -> Dict[str, Any]:
    """Node 1: Generate the plan"""
    query = state["input"]
    planner_output = generate_plan(query)
    
    # Convert Pydantic models to TypedDict for state
    plan_steps = []
    for step in planner_output.steps:
        plan_steps.append({
            "id": step.id,
            "tool": step.tool,
            "args": step.args,
            "dependency_ids": step.dependency_ids,
            "result": None,
            "status": "pending"
        })
        
    return {"plan": plan_steps}


def execute_node(state: AgentState) -> Dict[str, Any]:
    """Node 2: Execute ready steps"""
    plan = state["plan"]
    results = state.get("results", {})
    
    # Identify ready steps
    ready_steps = []
    for step in plan:
        if step["status"] == "pending":
            # Check dependencies
            deps_met = True
            for dep_id in step["dependency_ids"]:
                # Find result for dep_id
                # (Simple check: is it in results dict?)
                if str(dep_id) not in results:
                    deps_met = False
                    break
            
            if deps_met:
                ready_steps.append(step)
    
    if not ready_steps:
        return {}  # Nothing to do (or deadlock/done)

    # Execute ready steps (Serial for now, could be Parallel ThreadPool)
    new_results = {}
    for step in ready_steps:
        tool_name = step["tool"]
        raw_args = step["args"]
        
        # Variable Injection: Replace {step_X_result} with actual values
        for dep_id, val in results.items():
            placeholder = f"{{step_{dep_id}_result}}"
            if placeholder in raw_args:
                raw_args = raw_args.replace(placeholder, str(val))
        
        # Execute Tool
        output = None
        try:
            if tool_name == actionType.MATH_SOLVER:
                output = solve_math(raw_args)
            elif tool_name == actionType.WEB_SEARCH:
                output = web_search(raw_args)
                if output: output = "\n".join([f"{r.title}: {r.snippet}" for r in output])
            elif tool_name == actionType.WIKIPEDIA_SEARCH:
                res = wikipedia_search(raw_args)
                output = res.snippet if res else "No result"
            elif tool_name == actionType.ARXIV_SEARCH:
                res = arxiv_search(raw_args)
                output = res.snippet if res else "No result"
            elif tool_name == actionType.FINANCE_TOOL:
                res = get_stock_price(raw_args)
                output = res.snippet if res else "No result"
            elif tool_name == actionType.WEATHER_TOOL:
                res = get_weather(raw_args)
                output = res.snippet if res else "No result"
            elif tool_name == actionType.DIRECT_ANSWER:
                output = "Direct Answer Mode"
            else:
                output = "Unknown Tool"
        except Exception as e:
            output = f"Tool Error: {str(e)}"
            
        new_results[str(step["id"])] = output
        
        # Update status in plan (locally for this function scope, will be merged by LangGraph?)
        # LangGraph merges top-level keys. We need to return the updated plan list or results map.
        step["status"] = "done"
        step["result"] = output

    # Update overall results state
    # Merge new_results into existing results
    updated_results = results.copy()
    updated_results.update(new_results)
    
    return {"plan": plan, "results": updated_results}


def should_continue(state: AgentState) -> str:
    """Edge logic: Check if all steps are done"""
    plan = state["plan"]
    if not plan:
        return "solver" # No plan steps? Go straight to solver (e.g. direct answer)
        
    all_done = True
    for step in plan:
        if step["status"] != "done":
            all_done = False
            break
            
    if all_done:
        return "solver"
    else:
        return "executor" # Loop back


def solve_node(state: AgentState) -> Dict[str, Any]:
    """Node 3: Generate Final Answer"""
    query = state["input"]
    results = state.get("results", {})
    
    # Format context
    context_str = ""
    for step_id, val in results.items():
        context_str += f"Step {step_id} Output: {val}\n\n"
        
    answer = generate_answer(query, context_str, state.get("history", []))
    
    return {"final_answer": answer}


# Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("planner", plan_node)
workflow.add_node("executor", execute_node)
workflow.add_node("solver", solve_node)

workflow.set_entry_point("planner")

workflow.add_edge("planner", "executor")
workflow.add_conditional_edges(
    "executor",
    should_continue,
    {
        "executor": "executor",
        "solver": "solver"
    }
)
workflow.add_edge("solver", END)

app = workflow.compile()


def process_query_graph(user_query: str, memory_manager: MemoryManager) -> Dict[str, Any]:
    """Entry point for Streamlit"""
    
    initial_state = {
        "input": user_query,
        "plan": [],
        "results": {},
        "history": memory_manager.get_messages(),
        "final_answer": ""
    }
    
    final_state = app.invoke(initial_state)
    
    # Run Evaluator separately (keeps the graph clean, or could be a graph node)
    eval_result = evaluate(user_query, final_state["final_answer"])
    
    steps_export = []
    # format steps for UI
    for step in final_state["plan"]:
         steps_export.append({
             "step": f"Step {step['id']}: {step['tool']}",
             "input": step['args'],
             "output": str(step.get('result'))[:200] + "..."
         })
    
    # Store to memory if good
    if eval_result.pass_evaluation:
        memory_manager.add_user_message(user_query)
        memory_manager.add_ai_message(final_state["final_answer"])
        
    return {
        "answer": final_state["final_answer"],
        "steps": steps_export,
        "passed_evaluation": eval_result.pass_evaluation
    }
