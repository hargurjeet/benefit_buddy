import os
import sys

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

import asyncio
from google.genai import types
from guardrail_response_agent.agent import after_guardrail, sanitize_text_links

class MockContent:
    def __init__(self, text):
        self.parts = [types.Part.from_text(text=text)]

class MockLlmResponse:
    def __init__(self, text):
        self.content = MockContent(text)

class MockState(dict):
    pass

class MockCallbackContext:
    def __init__(self, state_dict):
        self.state = MockState(state_dict)

def test_link_sanitization():
    print("Running link sanitization callback tests...")
    
    # 1. Test case: Text containing a mix of valid government links and invalid blog links
    raw_text = """
    Here are the recommendations:
    1. PM Kisan Yojana: Access the official portal at https://pmkisan.gov.in/ to apply.
    2. Guide Blog: You can also read this unofficial guide at http://someblogsite.com/pm-kisan-registration for help.
    3. State Pension: Check status at https://sspension.punjab.gov.in/status.
    4. General Info: Avoid this spam site at https://spamlink.org/info.
    """
    
    print("\nOriginal generated response:")
    print(raw_text)
    
    sanitized_text = sanitize_text_links(raw_text)
    print("\nSanitized response:")
    print(sanitized_text)
    
    # Verify valid links are intact
    assert "https://pmkisan.gov.in/" in sanitized_text, "Failed: Valid gov.in link was incorrectly removed!"
    assert "https://sspension.punjab.gov.in/status" in sanitized_text, "Failed: Valid state gov.in link was incorrectly removed!"
    
    # Verify invalid links are removed
    assert "http://someblogsite.com/pm-kisan-registration" not in sanitized_text, "Failed: Invalid blog link was not removed!"
    assert "https://spamlink.org/info" not in sanitized_text, "Failed: Invalid spam link was not removed!"
    assert "[Link Removed - Only official government portals allowed]" in sanitized_text, "Failed: Warning placeholder was not inserted!"
    
    print("\nSUCCESS: Link sanitization math worked perfectly!")

async def test_callback_execution():
    print("\nRunning CallbackContext ADK callback wrapper test...")
    raw_text = "Apply here: https://externalblog.in/apply or official: https://india.gov.in/portal"
    
    mock_response = MockLlmResponse(raw_text)
    mock_context = MockCallbackContext({})
    
    result = await after_guardrail(mock_context, mock_response)
    resp_text = result.content.parts[0].text
    
    print(f"Sanitized result: {resp_text}")
    assert "https://externalblog.in/apply" not in resp_text
    assert "https://india.gov.in/portal" in resp_text
    print("SUCCESS: Callback wrapper executed and updated LlmResponse successfully!")

if __name__ == "__main__":
    test_link_sanitization()
    asyncio.run(test_callback_execution())
