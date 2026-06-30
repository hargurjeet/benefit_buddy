from google.adk.agents import LlmAgent

intake_agent = LlmAgent(
    name="intake_agent",
    model="gemini-2.0-flash",
    description="Clarifies user profile details including state, occupation, income, and family details.",
    instruction="Prompt the user to collect and clarify profile details."
)
