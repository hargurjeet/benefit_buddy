# Checklist: 001-Intake Agent Implementation

Chronological checklist for building and verifying the Intake Agent:

- [x] Define `UserProfile` Pydantic model in `intake_agent/agent.py`
- [x] Implement system prompt / instructions for profile extraction and income normalization
- [x] Configure `output_schema` or `after_model_callback` for incremental field extraction
- [x] Implement validation logic to check for completeness of state, occupation, annual_income, and family_details
- [x] Set `session.state.profile_complete = True` when all fields are populated
- [x] Add transition guard check in root pipeline (`agent.py`) to bypass `intake_agent` once state is frozen
- [x] Write unit tests for income normalization (verify "2.5 lakhs" -> `250000.0`, "60,000" -> `60000.0`)
- [ ] Run `adk run` to manually verify multi-turn conversation and successful handover to search phase

