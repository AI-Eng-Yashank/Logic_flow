from typing import Dict, Any, Optional
from router import route
from answer_generator import generate_answer
from evaluator import evaluate
from schemas import ActionType
from tools.math_solver import solve_math
from tools.web_search import web_search
from tools.wikipedia_search import wikipedia_search
from tools.arxiv_search import arxiv_search
from tools.finance_tool import get_stock_price
from tools.weather_tool import get_weather
from memory import MemoryManager


FALLBACK_MESSAGE = "Unable to confidently answer. Please refine the question."


def process_query(user_query: str, memory_manager: Optional[MemoryManager] = None) -> Dict[str, Any]:
    steps = []
    tool_result: Optional[str] = None
    
    # 1. Router (Stateless)
    router_output = route(user_query)
    steps.append({
        "step": "Router",
        "actions": [a.value for a in router_output.actions],
        "reason": router_output.reason
    })
    
    # 2. Tool Execution (Parallel/Sequential Loop)
    tool_results_list = []
    
    for action in router_output.actions:
        single_tool_result = None
        tool_name = action.value
        
        if action == ActionType.MATH_SOLVER:
            math_expression = user_query
            for prefix in ["what is", "calculate", "compute", "solve", "evaluate"]:
                if math_expression.lower().startswith(prefix):
                    math_expression = math_expression[len(prefix):].strip()
                    break
            math_expression = math_expression.rstrip("?").strip()
            
            result = solve_math(math_expression)
            single_tool_result = f"[Math Tool]: {str(result)}"
        
        elif action == ActionType.WEB_SEARCH:
            search_results = web_search(user_query)
            if search_results:
                formatted_results = []
                for i, r in enumerate(search_results, 1):
                    formatted_results.append(f"{i}. {r.title}\n   {r.snippet}\n   URL: {r.url}")
                single_tool_result = f"[Web Search]:\n" + "\n".join(formatted_results)
            else:
                single_tool_result = "[Web Search]: No results found."

        elif action == ActionType.WIKIPEDIA_SEARCH:
            wiki_result = wikipedia_search(user_query)
            if wiki_result:
                single_tool_result = f"[Wikipedia]:\nTitle: {wiki_result.title}\nSummary: {wiki_result.snippet}\nURL: {wiki_result.url}"
            else:
                single_tool_result = "[Wikipedia]: No page found."

        elif action == ActionType.ARXIV_SEARCH:
            arxiv_result = arxiv_search(user_query)
            if arxiv_result:
                single_tool_result = f"[ArXiv]:\nTitle: {arxiv_result.title}\nAbstract: {arxiv_result.snippet}\nURL: {arxiv_result.url}"
            else:
                single_tool_result = "[ArXiv]: No paper found."

        elif action == ActionType.FINANCE_TOOL:
            finance_result = get_stock_price(user_query)
            if finance_result:
                single_tool_result = f"[Finance]:\n{finance_result.snippet}"
            else:
                single_tool_result = "[Finance]: Could not find stock info."

        elif action == ActionType.WEATHER_TOOL:
            weather_result = get_weather(user_query)
            if weather_result:
                single_tool_result = f"[Weather]:\n{weather_result.snippet}"
            else:
                single_tool_result = "[Weather]: Could not find weather info."
        
        elif action == ActionType.DIRECT_ANSWER:
            steps.append({
                "step": "Tool",
                "output": "No tool required (direct answer)"
            })
            continue

        if single_tool_result:
            tool_results_list.append(single_tool_result)
            steps.append({
                "step": f"Tool: {tool_name}",
                "input": user_query,
                "output": single_tool_result
            })

    # Combine all tool results
    if tool_results_list:
        tool_result = "\n\n".join(tool_results_list)
    
    # 3. Answer Generator (With History)
    history = memory_manager.get_messages() if memory_manager else []
    answer = generate_answer(user_query, tool_result, history)
    
    steps.append({
        "step": "Answer Generator",
        "output": answer[:100] + "..." if len(answer) > 100 else answer
    })
    
    # 4. Evaluator (Stateless check of current answer)
    eval_result = evaluate(user_query, answer, tool_result)
    steps.append({
        "step": "Evaluator",
        "pass": eval_result.pass_evaluation,
        "issues": eval_result.issues
    })
    
    if eval_result.pass_evaluation:
        final_answer = answer
        # Update memory only on success
        if memory_manager:
            memory_manager.add_user_message(user_query)
            memory_manager.add_ai_message(final_answer)
    else:
        final_answer = FALLBACK_MESSAGE
    
    return {
        "answer": final_answer,
        "steps": steps,
        "passed_evaluation": eval_result.pass_evaluation
    }
