# Project State & Context

This file maintains the current progress and context of the BenefitBuddy project to make it easy for future sessions to pick up exactly where we left off.

---

## Current Progress (July 2, 2026)

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

4.  **Phase 4: Parallel Orchestration & Guardrail Response**
    *   Orchestrates local vector searches and online web search concurrently via `ParallelAgent` in `agent.py`.
    *   Aggregates both search results in `guardrail_response_agent/agent.py`.
    *   Applies a Python `after_model_callback` to dynamically verify and strip non-governmental URLs from final recommendations.
    *   Verified via: `python3 tests/test_guardrail_agent.py`.

---

## Next Session Goal: Phase 5 & 6

*   **Objective**: Implement **Phase 5: Guardrails & Security Layer** (e.g. prompt injection detector and red-teaming scripts).
