from typing import List
from duckduckgo_search import DDGS
import sys
sys.path.insert(0, '..')
from schemas import WebSearchResult


def web_search(query: str) -> List[WebSearchResult]:
    results = []
    
    try:
        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, max_results=3))
            
            for item in search_results:
                result = WebSearchResult(
                    title=item.get("title", ""),
                    snippet=item.get("body", ""),
                    url=item.get("href", "")
                )
                results.append(result)
    except Exception:
        pass
    
    return results
