from google.adk.agents import LlmAgent
from tools.dataset_search_tool import dataset_search

async def skip_if_profile_incomplete(callback_context):
    if callback_context.state.get("security_blocked") or not callback_context.state.get("profile_complete"):
        callback_context._invocation_context.end_invocation = True
        return None
    return None

dataset_search_agent = LlmAgent(
    name="dataset_search_agent",
    model="gemini-2.5-flash",
    description="Search the local schemes database.",
    instruction="Search for local scheme details using the dataset_search tool.",
    tools=[dataset_search],
    output_key="dataset_search_result",
    before_agent_callback=skip_if_profile_incomplete
)
