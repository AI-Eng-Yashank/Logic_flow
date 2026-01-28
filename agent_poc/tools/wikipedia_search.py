import wikipedia
import sys
sys.path.insert(0, '..')
from schemas import WebSearchResult


def wikipedia_search(query: str) -> WebSearchResult:
    try:
        # Get the summary of the first result
        summary = wikipedia.summary(query, sentences=3)
        page = wikipedia.page(query)
        
        return WebSearchResult(
            title=page.title,
            snippet=summary,
            url=page.url
        )
    except wikipedia.exceptions.DisambiguationError as e:
        # Fallback to the first option if ambiguous
        try:
            option = e.options[0]
            summary = wikipedia.summary(option, sentences=3)
            page = wikipedia.page(option)
            return WebSearchResult(
                title=page.title,
                snippet=summary,
                url=page.url
            )
        except Exception:
            pass
    except Exception:
        pass
        
    return None
