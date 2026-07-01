# Project State & Context

This file maintains the current progress and context of the BenefitBuddy project to make it easy for future sessions to pick up exactly where we left off.

---

## Current Progress (July 1, 2026)

We are building **BenefitBuddy**, an AI welfare navigator, using the Google ADK 2.0 framework.
The following phases are completed and verified:

1.  **Phase 1: Intake Agent**
    *   Extracts and structures user demographics (state, income, occupation, family).
    *   Normalizes income values (converts monthly to annual, handles terms like "lakh").
    *   Verified via: `python3 tests/test_intake_agent.py`.

2.  **Phase 2: Local Ingestion & Search**
    *   Downloads scheme dataset to `/data/` using `setup_data.py`.
    *   Generates 768-dimension vectors for all 1,524 schemes using `gemini-embedding-2` in `index_data.py`, caching them to `data/scheme_index.json`.
    *   Performs state-filtered cosine similarity search (central + user state candidates) in under 2ms.
    *   Verified via: `python3 tests/test_dataset_search.py`.

3.  **Phase 3: Web Search Integration**
    *   Uses the `ddgs` library to query online government sources.
    *   Enforces the project constitution by dynamically appending `(site:gov.in OR site:nic.in)` search constraints.
    *   Verified via: `python3 tests/test_web_search.py`.

---

## Next Session Goal: Phase 4

*   **Objective**: Implement the **Aggregator & Guardrail Response Agent** (`guardrail_response_agent/agent.py`).
*   **Role**: Merges the findings from the local dataset search (`dataset_search_result`) and the live web search (`web_search_result`), filters them based on `constitution.md` guidelines, and formats the final recommended welfare list and eligibility checklist for the user.
