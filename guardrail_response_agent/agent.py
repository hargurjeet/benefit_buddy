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

def remove_hallucinations(text: str, search_combined: str) -> str:
    if not search_combined or not search_combined.strip():
        return text
        
    search_lower = search_combined.lower()
    sections = re.split(r'(?=^####\s+)', text, flags=re.MULTILINE)
    if len(sections) <= 1:
        return text
        
    sanitized_sections = [sections[0]]
    for section in sections[1:]:
        lines = section.split("\n")
        heading_line = lines[0]
        
        # Clean heading (remove #### and numbers/dots, e.g. "1. PM Kisan" -> "PM Kisan")
        clean_heading = re.sub(r'^####\s+(?:\d+\.\s+)?', '', heading_line).strip()
        clean_heading_lower = clean_heading.lower()
        
        # Verify if heading or key words are present in either search result
        clean_heading_words = re.findall(r'\b\w{4,}\b', clean_heading_lower)
        
        is_valid = False
        if clean_heading_lower in search_lower:
            is_valid = True
        elif clean_heading_words:
            # Check if any significant word of length >= 4 is in search index
            for word in clean_heading_words:
                if word in search_lower:
                    is_valid = True
                    break
        else:
            is_valid = (clean_heading_lower in search_lower)
            
        if is_valid:
            sanitized_sections.append(section)
        else:
            # Replace hallucination with warning
            sanitized_sections.append(f"#### [Scheme Recommendation Block Removed - Source validation failed for '{clean_heading}']\n\n")
            
    return "".join(sanitized_sections)

async def after_guardrail(callback_context, llm_response):
    if not llm_response.content or not llm_response.content.parts:
        return None
        
    text = "".join(part.text for part in llm_response.content.parts if part.text)
    if not text:
        return None
        
    # Sanitize any non-government URLs dynamically
    sanitized_text = sanitize_text_links(text)
    
    # Retrieve search results to check for hallucinations
    db_result = callback_context.state.get("dataset_search_result", "")
    web_result = callback_context.state.get("web_search_result", "")
    search_combined = f"{db_result}\n{web_result}"
    
    # Clean out any hallucinated scheme sections
    final_text = remove_hallucinations(sanitized_text, search_combined)
    
    llm_response.content.parts = [types.Part.from_text(text=final_text)]
    return llm_response

async def skip_if_profile_incomplete(callback_context):
    if callback_context.state.get("security_blocked") or not callback_context.state.get("profile_complete"):
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
