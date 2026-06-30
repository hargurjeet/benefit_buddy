# Technical Plan: 001-Intake Agent Blueprint

This document details the technical implementation plan for the **Intake Agent** inside the BenefitBuddy orchestration pipeline.

## 1. State Schema Definition
We will use a Pydantic model to define the target profile schema. This structure will be updated incrementally in the `session.state` during the conversation turns.

```python
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    state: str = Field(description="Indian State/UT of residence (normalized, e.g., 'Karnataka', 'Tamil Nadu').")
    occupation: str = Field(description="Primary occupation/profession (e.g., 'Farmer', 'Unemployed', 'Student').")
    annual_income: float = Field(description="Annual household income in INR (numeric float normalized from terms like '3 Lakhs' -> 300000.0).")
    family_details: str = Field(description="Dependents, number of children, and their school grades if applicable.")
```

## 2. Dialog and Extraction Flow
The Intake Agent operates as an `LlmAgent` in `chat` mode.
- **Turn-by-turn update**: We will register an `after_model_callback` that runs a secondary JSON extraction pass (or uses Gemini structured outputs) to extract any updated profile fields from the current turn and merges them into `session.state.user_profile`.
- **Normalization**: Prompt instructions will enforce converting linguistic income expressions (e.g., "1.5 lakhs", "2L", "50k") into plain numbers (e.g., `150000.0`, `200000.0`, `50000.0`).

## 3. State Freezing & Transition Signaling
- **Completion Check**: After each user turn, the extraction callback validates if all 4 required fields are filled and clear of placeholders.
- **Freeze State**: Once valid, the agent sets `session.state.profile_complete = True` and locks modifications.
- **Sequential Handover**: In ADK 2.0, the pipeline coordinator (`benefit_buddy_pipeline`) checks `session.state.profile_complete`. When `True`, the pipeline proceeds to the `parallel_search` block.
