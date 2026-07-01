import os
import sys

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from tools.web_search_tool import web_search

def run_test():
    print("Running DuckDuckGo Web Search Tool Verification test...")
    
    # Test query
    query = "PM Kisan Yojana updates 2026"
    print(f"\nSearching web for: '{query}'...")
    results = web_search(query)
    
    print("\n--- Search Results ---")
    print(results)
    print("----------------------")
    
    # Assertions on output
    if "Error executing" in results:
        print("FAILED: Web search returned an error.")
    elif "No search results" in results:
        print("FAILED: No search results returned.")
    else:
        # Check that links are indeed government domains
        lines = results.split("\n")
        links = [line.split("Link: ", 1)[1].strip() for line in lines if line.strip().startswith("Link:")]
        print(f"Retrieved links: {links}")
        
        non_gov_links = []
        for link in links:
            # Simple check if domain ends with .gov.in or .nic.in
            # (or contains it as a domain section)
            domain_part = link.split("//", 1)[-1].split("/", 1)[0]
            if not (domain_part.endswith(".gov.in") or domain_part.endswith(".nic.in")):
                non_gov_links.append(link)
                
        if non_gov_links:
            print(f"FAILED: Non-government links found in results: {non_gov_links}")
        else:
            print("SUCCESS: Web search executed successfully and restricted links to .gov.in/.nic.in!")

if __name__ == "__main__":
    run_test()
