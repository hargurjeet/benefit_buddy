import os
import sys
import re
import asyncio
from urllib.parse import urlparse

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

def load_env():
    env_path = os.path.join(project_root, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip().strip("'").strip('"')
                    os.environ[key.strip()] = val

from agent import root_agent

async def test_guardrail_flow():
    load_env()
    # Make sure GEMINI_API_KEY is available
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is not set!")
        print("Please export GEMINI_API_KEY=your_key in your terminal first.")
        return

    print("Initializing ADK Runner for root agent pipeline...")
    runner = Runner(
        agent=root_agent,
        app_name="guardrail_test",
        session_service=InMemorySessionService(),
        auto_create_session=True
    )

    user_id = "test_user_guardrail"
    session_id = "test_session_guardrail"

    # Profile turns to complete intake and trigger search/guardrail phases
    messages = [
        "Hi, I am a farmer from Punjab.",
        "My annual income is 3 Lakhs.",
        "I have two kids in grade 3 and 7."
    ]

    final_response_text = ""

    for i, msg in enumerate(messages, 1):
        print(f"\n--- Turn {i} ---")
        print(f"User: {msg}")
        
        content = types.Content(role="user", parts=[types.Part.from_text(text=msg)])
        
        events = list(runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ))
        
        for event in events:
            if event.content and event.content.parts:
                text = "".join(part.text for part in event.content.parts if part.text)
                if text:
                    # Print agent responses (IntakeAgent in early turns, GuardrailResponseAgent in the final turn)
                    print(f"Agent: {text}")
                    final_response_text = text

    print("\n--- Final Pipeline Output ---")
    print(final_response_text)
    print("------------------------------")

    # Assertions to ensure no external (non-government) domains made it through
    url_pattern = r'https?://[^\s\)\*\`\"\']+'
    found_links = re.findall(url_pattern, final_response_text)
    print(f"Links found in final response: {found_links}")
    
    invalid_links = []
    for link in found_links:
        try:
            parsed = urlparse(link)
            domain = parsed.netloc.lower()
            if ":" in domain:
                domain = domain.split(":", 1)[0]
            if not (domain.endswith(".gov.in") or domain.endswith(".nic.in")):
                invalid_links.append(link)
        except Exception:
            invalid_links.append(link)

    assert not invalid_links, f"FAILED: Disallowed non-government links found in response: {invalid_links}"
    
    # Check that at least one official scheme link was recommended
    assert len(found_links) > 0, "FAILED: No official links recommended in response!"
    
    print("\nSUCCESS: End-to-end integration test executed successfully!")
    print("Verification passed: final response strictly respects domain filters without any mock setups.")

if __name__ == "__main__":
    asyncio.run(test_guardrail_flow())
