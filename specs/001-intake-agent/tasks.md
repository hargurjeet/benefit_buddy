# Checklist: 001-Intake Agent Implementation

Chronological checklist for building and verifying the Intake Agent:

- [ ] Define `UserProfile` Pydantic model in `intake_agent/agent.py`
- [ ] Implement system prompt / instructions for profile extraction and income normalization
- [ ] Configure `output_schema` or `after_model_callback` for incremental field extraction
- [ ] Implement validation logic to check for completeness of state, occupation, annual_income, and family_details
- [ ] Set `session.state.profile_complete = True` when all fields are populated
- [ ] Add transition guard check in root pipeline (`agent.py`) to bypass `intake_agent` once state is frozen
- [ ] Write unit tests for income normalization (verify "2.5 lakhs" -> `250000.0`, "60,000" -> `60000.0`)
- [ ] Run `adk run` to manually verify multi-turn conversation and successful handover to search phase
