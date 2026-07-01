# BenefitBuddy Project Implementation Roadmap

This document outlines the step-by-step master plan for implementing the **BenefitBuddy** AI welfare navigator.

---

## 🛠️ Phase 1: Intake Agent (`001-intake-agent`)
*Goal: Conversational collection of user details without traditional web forms.*

### Steps:
- [ ] Define the `UserProfile` Pydantic model inside `intake_agent/agent.py`.
- [ ] Write system instruction guidelines in `intake_agent/agent.py` to extract:
  *   `state`
  *   `occupation`
  *   `annual_income` (needs normalization)
  *   `family_details`
- [ ] Implement an `after_model_callback` to process the raw model text, normalize values like `"3 lakhs"` to a numeric float `300000.0`, and update the state.
- [ ] Implement a validation check that sets `session.state.profile_complete = True` when all fields are successfully extracted.
- [ ] Configure `benefit_buddy_pipeline` in the root `agent.py` to check for completion and hand over execution.

---

## 📂 Phase 2: Local Database Ingestion & Search (`002-local-search`)
*Goal: Embed and query the local government schemes CSV database.*

### Steps:
- [ ] Run `setup_data.py` to fetch `"nitishabharathi/indian-government-schemes"` from Kaggle.
- [ ] Build a database indexing script (using Chroma or FAISS with Gemini embeddings) to ingest scheme details from the CSV file.
- [ ] Implement query logic in `tools/dataset_search_tool.py` to perform semantic vector searches.
- [ ] Update `dataset_search_agent/agent.py` to register the dataset search tool and store findings in `dataset_search_result`.

---

## 🌐 Phase 3: Web Search Tool Integration (`003-web-search`)
*Goal: Query the live web for fresh, real-time scheme updates.*

### Steps:
- [ ] Configure the Serper API client inside `tools/web_search_tool.py`.
- [ ] Update `web_search_agent/agent.py` to target search terms to official Indian government sites (e.g. appending `site:gov.in` to search inputs).
- [ ] Verify search response parsing and link collection.

---

## 🛡️ Phase 4: Parallel Orchestration & Guardrails (`004-guardrails`)
*Goal: Concurrently fetch web/local matches and validate sources.*

### Steps:
- [ ] Configure the `ParallelAgent` (`parallel_search`) to run both search agents concurrently in separate state branches.
- [ ] Implement merging and validation rules in `guardrail_response_agent/agent.py`.
- [ ] Enforce allowlist regex pattern checks ensuring all outbound links originate strictly from `.gov.in` or `.nic.in` domains.
- [ ] Output the formatted Markdown results containing verified scheme lists, eligibility descriptions, and cited links.

---

## 🧪 Phase 5: Evaluation & Testing (`005-evaluation-testing`)
*Goal: Validate that normalization, search retrieval, and guardrail logic are robust.*

### Steps:
- [ ] Set up a suite of mock citizen profiles testing varying incomes, states, and formatting.
- [ ] Run test execution cycles checking for:
  *   Accuracy of income parsing and normalization.
  *   Recall efficiency of vector search matching.
  *   Strict blocking of non-allowlisted URLs (red teaming).

---

## 🖥️ Phase 6: API and Interface (`006-deployment-ui`)
*Goal: Expose the agent via a web dashboard and program accessible API endpoint.*

### Steps:
- [ ] Build a FastAPI server wrapping the pipeline to accept user queries and stream agent events.
- [ ] Setup a React or Streamlit frontend interface displaying the conversation stream and a live profile card.

---

## 📈 Phase 7: Observability & Maintenance (`007-observability-maintenance`)
*Goal: Token optimization, latency improvements, and data updates.*

### Steps:
- [ ] Configure ADK's native OpenTelemetry integrations to track step durations and token expenditures.
- [ ] Schedule cron jobs to check Kaggle and government feeds, ensuring the vector database remains updated.
