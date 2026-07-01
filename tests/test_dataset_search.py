import os
import sys
import asyncio

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from tools.dataset_search_tool import dataset_search

# Mock classes to emulate ADK's Context/ToolContext behavior
class MockState(dict):
    pass

class MockToolContext:
    def __init__(self, state_dict):
        self.state = MockState(state_dict)

def run_test():
    # Make sure GEMINI_API_KEY is available
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is not set!")
        return

    print("Running Dataset Search Tool Verification test...")
    
    # 1. Test case: User is from Punjab
    print("\n--- Test Case 1: State Filter = Punjab, Query = 'loans for farmers' ---")
    mock_context_punjab = MockToolContext({
        "user_profile": {
            "state": "Punjab",
            "occupation": "Farmer",
            "annual_income": 300000.0,
            "family_details": "Two children"
        }
    })
    
    results_punjab = dataset_search("loans for farmers", tool_context=mock_context_punjab)
    print(results_punjab)
    
    # Verify that only Punjab or Central schemes were returned
    lines = results_punjab.split("\n")
    scopes = [line.split("State/Scope: ", 1)[1].strip() for line in lines if line.startswith("State/Scope:")]
    print(f"Retrieved scopes: {scopes}")
    
    invalid_scopes = [s for s in scopes if s.lower() not in ("punjab", "central")]
    if invalid_scopes:
        print(f"FAILED: Found invalid scopes in results: {invalid_scopes}")
    else:
        print("SUCCESS: Search output matches scope restrictions (Punjab & Central only).")

    # 2. Test case: User is from Andhra Pradesh
    print("\n--- Test Case 2: State Filter = Andhra Pradesh, Query = 'pension for old age' ---")
    mock_context_ap = MockToolContext({
        "user_profile": {
            "state": "Andhra pradesh",
            "occupation": "Retired",
            "annual_income": 120000.0,
            "family_details": "Self and wife"
        }
    })
    
    results_ap = dataset_search("pension for old age", tool_context=mock_context_ap)
    print(results_ap)
    
    lines_ap = results_ap.split("\n")
    scopes_ap = [line.split("State/Scope: ", 1)[1].strip() for line in lines_ap if line.startswith("State/Scope:")]
    print(f"Retrieved scopes: {scopes_ap}")
    
    invalid_scopes_ap = [s for s in scopes_ap if s.lower() not in ("andhra-pradesh", "andhra pradesh", "central")]
    if invalid_scopes_ap:
        print(f"FAILED: Found invalid scopes in results: {invalid_scopes_ap}")
    else:
        print("SUCCESS: Search output matches scope restrictions (Andhra Pradesh & Central only).")

if __name__ == "__main__":
    run_test()
