import arxiv
import sys
sys.path.insert(0, '..')
from schemas import WebSearchResult


def arxiv_search(query: str) -> WebSearchResult:
    try:
        # Construct client
        client = arxiv.Client()
        
        # Search for the query
        search = arxiv.Search(
            query=query,
            max_results=1,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = list(client.results(search))
        if not results:
            return None
            
        paper = results[0]
        
        return WebSearchResult(
            title=paper.title,
            snippet=f"Published: {paper.published.strftime('%Y-%m-%d')}\nAbstract: {paper.summary[:500]}...",
            url=paper.pdf_url
        )
    except Exception:
        pass
        
    return None
