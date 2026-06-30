# Specification: 001-Intake Agent

## Overview
The Intake Agent is a conversational LlmAgent responsible for multi-turn user profile collection using natural language (Vibe Coding interface). It eliminates traditional forms.

## User Persona & Inputs
The agent interacts with citizens who provide unstructured text inputs (e.g., "I am a 58-year-old farmer from Karnataka...").

## Target State Schema to Extract
The agent must converse with the user until it can accurately populate the following session-state fields:
- `state` (e.g., Karnataka)
- `occupation` (e.g., Farmer)
- `annual_income` (numeric value, normalized from expressions like 'lakhs')
- `family_details` (e.g., dependents, children's school grades)

## Acceptance Criteria
1. The agent must maintain state across turns using ADK session-state keys.
2. If any critical variable (state, occupation, income) is missing or ambiguous, the agent must ask a clarifying question rather than making assumptions.
3. Once the profile is complete, it must freeze the state and signal the orchestration pipeline to transition to the `parallel_search` block.
