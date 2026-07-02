import re
from urllib.parse import urlparse
from google.adk.agents import LlmAgent
from google.genai import types

def sanitize_text_links(text: str) -> str:
    # Match standard URLs (http/https)
    # The regex matches characters that are valid in URL paths but stops at common markdown delimiters
    url_pattern = r'https?://[^\s\)\*\`\"\']+'
    
    def replace_url(match):
        url = match.group(0)
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove port numbers if any (e.g. localhost:8000 -> localhost)
            if ":" in domain:
                domain = domain.split(":", 1)[0]
                
            # Allow official government subdomains (e.g. pmkisan.gov.in, nic.in)
            if domain.endswith(".gov.in") or domain.endswith(".nic.in"):
                return url
        except Exception:
            pass
        # If invalid or raised parsing error, block and replace it
        return "[Link Removed - Only official government portals allowed]"
        
    return re.sub(url_pattern, replace_url, text)

async def after_guardrail(callback_context, llm_response):
    # Retrieve the generated response text
    if not llm_response.content or not llm_response.content.parts:
        return None
        
    text = "".join(part.text for part in llm_response.content.parts if part.text)
    if not text:
        return None
        
    # Sanitize any non-government URLs dynamically
    sanitized_text = sanitize_text_links(text)
    
    # Save the sanitized text back in place
    llm_response.content.parts = [types.Part.from_text(text=sanitized_text)]
    return llm_response

async def skip_if_profile_incomplete(callback_context):
    if not callback_context.state.get("profile_complete"):
        callback_context._invocation_context.end_invocation = True
        return None
    return None

guardrail_response_agent = LlmAgent(
    name="guardrail_response_agent",
    model="gemini-2.5-flash",
    description="Synthesizes search results, checks eligibility, and enforces link guardrails.",
    instruction="""You are the Aggregator & Guardrail Response Agent for BenefitBuddy. Your task is to provide the final advice to the user.

First, read the session state keys from the conversation context:
1. `user_profile`: The user's collected demographic profile (state, occupation, normalized annual income, and family details).
2. `dataset_search_result`: Discovered schemes from the local vector database.
3. `web_search_result`: Fresh scheme updates and guidelines from online portals.

Your final output MUST follow these guidelines:
- Summarize the user's demographic profile we are matching against (State, Income, Occupation, Family Size).
- Evaluate the user's eligibility for each of the schemes found in `dataset_search_result` and `web_search_result` (match state, income limits, occupation, etc.).
- ONLY recommend schemes for which the user meets the eligibility criteria. If they do not qualify for any, explain why.
- Provide details, benefits, and an actionable Next Steps checklist for each qualified scheme.
- Every recommended scheme must include its official source link.
- Under our strict project constitution, YOU MUST ONLY output links originating from .gov.in or .nic.in domains. Never include external non-government blog links or articles.

Deliver your response in a highly structured, professional, and clear Markdown format.""",
    before_agent_callback=skip_if_profile_incomplete,
    after_model_callback=after_guardrail
)
