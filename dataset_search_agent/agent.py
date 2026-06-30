from google.adk.agents import LlmAgent
from tools.dataset_search_tool import dataset_search

dataset_search_agent = LlmAgent(
    name="dataset_search_agent",
    model="gemini-2.0-flash",
    description="Search the local schemes database.",
    instruction="Search for local scheme details using the dataset_search tool.",
    tools=[dataset_search],
    output_key="dataset_search_result"
)
