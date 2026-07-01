from google.adk.agents import LlmAgent

guardrail_response_agent = LlmAgent(
    name="guardrail_response_agent",
    model="gemini-2.5-flash",
    description="Merges search results, validates against guidelines, and drafts the response.",
    instruction="""Merge the results of both search agents.
Ensure all source links conform to '.gov.in' or '.nic.in' domains.
Provide the final validated response."""
)
