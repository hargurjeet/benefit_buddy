from google.adk.agents import LlmAgent
from tools.web_search_tool import web_search

async def skip_if_profile_incomplete(callback_context):
    if callback_context.state.get("security_blocked") or not callback_context.state.get("profile_complete"):
        callback_context._invocation_context.end_invocation = True
        return None
    return None

web_search_agent = LlmAgent(
    name="web_search_agent",
    model="gemini-2.5-flash",
    description="Search the web for up-to-date welfare schemes.",
    instruction="Search for government schemes using the web_search tool.",
    tools=[web_search],
    output_key="web_search_result",
    before_agent_callback=skip_if_profile_incomplete
)
