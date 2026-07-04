import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

from duckduckgo_search import DDGS

def web_search(query: str) -> str:
    """
    Search the web for up-to-date information on government welfare schemes.
    
    Args:
        query: The search query (e.g., scheme name or eligibility question).
        
    Returns:
        A search results summary with sources from official portals.
    """
    # Force the query to strictly retrieve results from *.gov.in or *.nic.in domains
    government_scoped_query = f"{query} (site:gov.in OR site:nic.in)"
    
    try:
        with DDGS() as ddgs:
            results = ddgs.text(government_scoped_query, max_results=5)
            
        if not results:
            return "No search results found on official portals."
            
        output_parts = []
        for idx, result in enumerate(results):
            title = result.get("title", "No Title")
            snippet = result.get("body", "No description available.").replace("\n", " ")
            link = result.get("href", "")
            output_parts.append(
                f"{idx + 1}. Source Title: {title}\n"
                f"   Link: {link}\n"
                f"   Summary: {snippet}\n"
            )
            
        return "\n".join(output_parts)
        
    except Exception as e:
        return f"Error executing DuckDuckGo search: {str(e)}"
