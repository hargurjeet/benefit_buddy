# Copyright (c) 2026 MyCompany LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

from tools.tavily_search_tool import tavily_extract

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
    
    # Execute extraction
    test_urls = ["https://pmkisan.gov.in/"]
    print(f"Running Tavily Extract for URLs: {test_urls}...")
    
    results = tavily_extract(test_urls)
    
    print("\n--- Tavily Extract Results (First 500 chars) ---")
    print(results[:500] + "...")
    print("-------------------------------------------------")
    
    # Validate result
    if "Error executing" in results or "Error:" in results:
        print("FAILED: Tavily extract returned an error.")
        sys.exit(1)
    elif "No content extracted" in results:
        print("FAILED: No content extracted.")
        sys.exit(1)
    elif len(results) < 50:
        print("FAILED: Extracted content is too short.")
        sys.exit(1)
    else:
        print("SUCCESS: Tavily extract executed successfully via the MCP server!")

    # Test security filter: trying to extract a non-government URL
    bad_urls = ["https://google.com/"]
    print(f"\nTesting security boundary filter for URLs: {bad_urls}...")
    security_test_result = tavily_extract(bad_urls)
    print(f"Security test result: {security_test_result}")
    if "Error: No official government URLs" in security_test_result:
        print("SUCCESS: Security boundary filter correctly blocked non-government domain extraction!")
    else:
        print("FAILED: Security boundary filter allowed a non-government domain!")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
