import os
import sys
import asyncio
import readline  # Enables line editing and input history in the terminal
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from agent import root_agent

async def run_terminal_chat():
    # Load environment variables from the project root .env file
    env_path = os.path.join(project_root, ".env")
    load_dotenv(dotenv_path=env_path)
    
    # Ensure GEMINI_API_KEY is available
    if not os.environ.get("GEMINI_API_KEY"):
        print("\033[91mError: GEMINI_API_KEY environment variable is not set!\033[0m")
        print("Please export GEMINI_API_KEY=your_key in your terminal or ensure it is present in your .env file.")
        return

    print("\033[94m==================================================")
    print("      BenefitBuddy Terminal Chat Client           ")
    print("==================================================\033[0m")
    print("Initializing ADK Runner for root agent pipeline...")
    
    runner = Runner(
        agent=root_agent,
        app_name="terminal_chat",
        session_service=InMemorySessionService(),
        auto_create_session=True
    )

    user_id = "terminal_user"
    session_id = "terminal_session"

    print("\n\033[92mBenefitBuddy:\033[0m Hello! I am BenefitBuddy, your assistant for government schemes.")
    print("To get started, please tell me about yourself (e.g., state, occupation, income, family details).")
    print("\033[90m(Type 'exit' or 'quit' to end the conversation.)\033[0m\n")

    while True:
        try:
            user_input = input("\033[1mYou:\033[0m ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting chat. Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("\033[92mBenefitBuddy:\033[0m Goodbye!")
            break

        content = types.Content(role="user", parts=[types.Part.from_text(text=user_input)])
        
        print("\033[90mBenefitBuddy: Thinking...\033[0m", end="\r")
        try:
            # Run the sequential pipeline step
            events = list(runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            ))
            
            # Clear the "Thinking..." line
            print(" " * 40, end="\r")
            
            # Accumulate all responses
            agent_response = ""
            for event in events:
                if event.content and event.content.parts:
                    text = "".join(part.text for part in event.content.parts if part.text)
                    if text:
                        agent_response += text
            
            if agent_response:
                print(f"\033[92mBenefitBuddy:\033[0m {agent_response}\n")
            else:
                print("\033[93mBenefitBuddy: (No response returned from the pipeline)\033[0m\n")
                
            # Retrieve the session state so we can show the extracted profile variables
            session = await runner.session_service.get_session(
                app_name="terminal_chat",
                user_id=user_id,
                session_id=session_id
            )
            profile = session.state.get("user_profile", {})
            complete = session.state.get("profile_complete", False)
            if profile:
                print(f"\033[90m[Session State | Complete: {complete} | Extracted Profile: {profile}]\033[0m\n")
                
        except Exception as e:
            # Clear the "Thinking..." line in case of error
            print(" " * 40, end="\r")
            print(f"\033[91mError running agent: {e}\033[0m\n")

if __name__ == "__main__":
    try:
        asyncio.run(run_terminal_chat())
    except KeyboardInterrupt:
        print("\nGoodbye!")
