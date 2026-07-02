import os
import json
from typing import Optional
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google import genai
from google.genai import types

class UserProfile(BaseModel):
    state: Optional[str] = Field(None, description="The Indian state or UT of residence (e.g. Karnataka). Only set if explicitly provided.")
    occupation: Optional[str] = Field(None, description="Primary occupation/profession (e.g. Farmer). Only set if explicitly provided.")
    annual_income: Optional[float] = Field(None, description="Annual household income in INR (normalized to a numeric float, e.g. 300000.0). Only set if explicitly provided.")
    family_details: Optional[str] = Field(None, description="Details about dependents, number of children, school grades, etc. Only set if explicitly provided.")

def check_profile_completeness(profile: UserProfile) -> bool:
    return (
        profile.state is not None and
        profile.occupation is not None and
        profile.annual_income is not None and
        profile.family_details is not None
    )

from tools.security_tool import detect_prompt_injection

def get_latest_user_message(callback_context) -> str:
    for event in reversed(callback_context.session.events):
        if event.author == "user":
            if event.content and event.content.parts:
                text = "".join(part.text for part in event.content.parts if part.text)
                if text:
                    return text
    return ""

async def before_intake(callback_context):
    # Retrieve the user's latest message
    user_msg = get_latest_user_message(callback_context)
    if detect_prompt_injection(user_msg):
        callback_context.state['security_blocked'] = True
        callback_context._invocation_context.end_invocation = True
        return types.Content(
            role="model",
            parts=[types.Part.from_text(text="[Security Warning: Adversarial inputs or prompt overrides detected. Execution halted.]")]
        )

    # If the profile is already complete, mark the invocation as ended to transition immediately.
    if callback_context.state.get('profile_complete'):
        callback_context._invocation_context.end_invocation = True
        return None
    return None

async def after_intake(callback_context, llm_response):
    # Build conversation history between user and intake_agent
    history_lines = []
    for event in callback_context.session.events:
        if event.author in ("user", "intake_agent"):
            if event.content and event.content.parts:
                text = "".join(part.text for part in event.content.parts if part.text)
                if text:
                    role = "User" if event.author == "user" else "IntakeAgent"
                    history_lines.append(f"{role}: {text}")
                    
    # Also append the current response text to history
    if llm_response.content and llm_response.content.parts:
        resp_text = "".join(part.text for part in llm_response.content.parts if part.text)
        if resp_text:
            history_lines.append(f"IntakeAgent: {resp_text}")
            
    history_text = "\n".join(history_lines)
    
    # Run structured extraction using the Gemini Client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Skip extraction if API key is not set (e.g. in basic unit tests)
        return None
        
    client = genai.Client(api_key=api_key)
    try:
        # Load existing profile if any
        current_profile_dict = callback_context.state.get('user_profile', {})
        
        prompt = f"""
        Extract the current user profile from the conversation history.
        Ensure you only set fields if they are explicitly mentioned and certain.
        If a field is missing, ambiguous, or not yet stated, keep it null.
        
        Previous Profile State:
        {json.dumps(current_profile_dict)}
        
        Conversation History:
        {history_text}
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=UserProfile,
                system_instruction="You are a precise JSON profile extractor. Normalize income terms (e.g. 'lakhs') to raw floats."
            )
        )
        
        extracted_profile = UserProfile.model_validate_json(response.text)
        
        # Merge old and new profile data (favoring newly extracted non-null fields)
        merged_profile = {}
        for field in UserProfile.model_fields.keys():
            new_val = getattr(extracted_profile, field)
            old_val = current_profile_dict.get(field)
            merged_profile[field] = new_val if new_val is not None else old_val
            
        callback_context.state['user_profile'] = merged_profile
        
        # Validate profile completeness
        profile_obj = UserProfile(**merged_profile)
        if check_profile_completeness(profile_obj):
            callback_context.state['profile_complete'] = True
            
    except Exception as e:
        print(f"Error in extraction callback: {e}")
        
    return None

intake_agent = LlmAgent(
    name="intake_agent",
    model="gemini-2.5-flash",
    description="Clarifies user profile details including state, occupation, income, and family details.",
    instruction="""You are the Intake Agent for BenefitBuddy. Your goal is to gather a complete user profile.
    Ask the user questions to collect:
    1. State of residence in India (e.g., Karnataka)
    2. Occupation (e.g., Farmer, Student, Retired)
    3. Annual household income in INR
    4. Family details (number of dependents, school grades of children if any)
    
    Guidelines:
    - Converse in a warm, helpful, natural conversational tone.
    - Ask ONLY one clarifying question at a time.
    - Never ask for details the user has already provided.
    - Once the profile is complete, acknowledge it politely.
    """,
    before_agent_callback=before_intake,
    after_model_callback=after_intake
)
