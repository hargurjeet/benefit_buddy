from google.adk.agents import LlmAgent
from tools.web_search_tool import web_search

web_search_agent = LlmAgent(
    name="web_search_agent",
    model="gemini-2.0-flash",
    description="Search the web for up-to-date welfare schemes.",
    instruction="Search for government schemes using the web_search tool.",
    tools=[web_search],
    output_key="web_search_result"
)
