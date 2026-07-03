import os
import sys
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from tools.tavily_search_tool import tavily_search

def run_test():
    # Load .env file
    env_path = os.path.join(project_root, ".env")
    load_dotenv(dotenv_path=env_path)
    
    # Verify key exists
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("FAILED: TAVILY_API_KEY is not set in the environment or .env file!")
        sys.exit(1)
        
    print(f"Using Tavily API Key: {api_key[:5]}...{api_key[-5:]}")
    
    # Execute query
    query = "PM Kisan Yojana eligibility rules 2026"
    print(f"Running Tavily Search for query: '{query}'...")
    
    results = tavily_search(query)
    
    print("\n--- Tavily Search Results ---")
    print(results)
    print("------------------------------")
    
    if "Error executing" in results or "Error:" in results:
        print("FAILED: Tavily search returned an error.")
        sys.exit(1)
    elif "No search results" in results:
        print("FAILED: No search results returned.")
        sys.exit(1)
    else:
        print("SUCCESS: Tavily search executed successfully via the MCP server!")

if __name__ == "__main__":
    run_test()
