from google.adk.agents import LlmAgent
from tools.tavily_search_tool import tavily_search

async def skip_if_profile_incomplete(callback_context):
    """
    Prevents the agent from executing if the user's demographic profile intake is incomplete
    or if the request is blocked by the security guardrail.
    """
    if callback_context.state.get("security_blocked") or not callback_context.state.get("profile_complete"):
        callback_context._invocation_context.end_invocation = True
        return None
    return None

tavily_search_agent = LlmAgent(
    name="tavily_search_agent",
    model="gemini-2.5-flash",
    description="Search the web using Tavily MCP for up-to-date welfare schemes.",
    instruction="Search for government schemes using the tavily_search tool.",
    tools=[tavily_search],
    output_key="tavily_search_result",
    before_agent_callback=skip_if_profile_incomplete
)
