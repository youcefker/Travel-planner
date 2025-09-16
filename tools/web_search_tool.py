# travel_planneer/tools/web_search_tool.py
import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import Tool

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def safe_web_search(query: str) -> str:
    """
    Safely perform web search with error handling.
    Input: search query string
    Output: search results as string
    """
    try:
        if not query or not isinstance(query, str):
            return "Error: Query must be a non-empty string"
        
        query = query.strip()
        if not query:
            return "Error: Query cannot be empty"
        
        print(f"🔍 Web searching: '{query}'")
        
        # Configure the Tavily search tool
        search_tool = TavilySearchResults(
            api_key=TAVILY_API_KEY,
            max_results=5
        )
        
        results = search_tool.invoke(query)
        print(f"✅ Found {len(results) if isinstance(results, list) else 1} results")
        
        return str(results)
        
    except Exception as e:
        error_msg = f"Error searching for '{query}': {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

# Create the tool
web_search_tool = Tool(
    name="WebSearchTool",
    func=safe_web_search,
    description=(
        "Search the web for information. "
        "Input: search query as a string. "
        "Output: search results as formatted text."
    )
)