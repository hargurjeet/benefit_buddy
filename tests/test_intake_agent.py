import os
import sys
import json
import asyncio

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from intake_agent.agent import intake_agent

async def test_flow():
    # Make sure GEMINI_API_KEY is available
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is not set!")
        print("Please export GEMINI_API_KEY=your_key in your terminal first.")
        return

    print("Initializing ADK Runner for Intake Agent...")
    runner = Runner(
        agent=intake_agent,
        app_name="intake_test",
        session_service=InMemorySessionService(),
        auto_create_session=True
    )

    user_id = "test_user"
    session_id = "test_session"

    # Multi-turn inputs containing unstructured profile details
    messages = [
        "Hi, I am a farmer from Punjab.",
        "My annual income is 3 Lakhs.",
        "I have two kids in grade 3 and 7."
    ]

    for i, msg in enumerate(messages, 1):
        print(f"\n--- Turn {i} ---")
        print(f"User: {msg}")
        
        # Build user message content
        content = types.Content(role="user", parts=[types.Part.from_text(text=msg)])
        
        # Invoke agent turn
        events = list(runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ))
        
        # Print responses
        for event in events:
            if event.content and event.content.parts:
                text = "".join(part.text for part in event.content.parts if part.text)
                if text:
                    print(f"IntakeAgent: {text}")

        # Retrieve and display current session state
        session = await runner.session_service.get_session(
            app_name="intake_test",
            user_id=user_id,
            session_id=session_id
        )
        print("\nCurrent Extracted State:")
        print(json.dumps(session.state, indent=2))

    print("\n--- Final Test Status ---")
    session = await runner.session_service.get_session(
        app_name="intake_test",
        user_id=user_id,
        session_id=session_id
    )
    profile = session.state.get("user_profile", {})
    complete = session.state.get("profile_complete", False)
    
    print(f"Profile Extracted: {profile}")
    print(f"Profile Complete: {complete}")
    if complete and profile.get("annual_income") == 300000.0:
        print("SUCCESS: Profile complete and income normalized correctly!")
    else:
        print("FAILED: Profile is incomplete or income normalization failed.")

if __name__ == "__main__":
    asyncio.run(test_flow())
