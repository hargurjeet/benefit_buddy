import os
import sys

# Add project root to sys.path to support imports both locally and inside container deployments
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from google.adk.agents import SequentialAgent, ParallelAgent
from intake_agent import intake_agent
from web_search_agent import web_search_agent
from dataset_search_agent import dataset_search_agent
from guardrail_response_agent import guardrail_response_agent

# 2. Parallel Search: Runs the web search and dataset search concurrently
parallel_search = ParallelAgent(
    name="parallel_search",
    description="Run web search and dataset query in parallel.",
    sub_agents=[web_search_agent, dataset_search_agent]
)

# Root Agent: Pipelines the three stages sequentially
root_agent = SequentialAgent(
    name="benefit_buddy_pipeline",
    description="BenefitBuddy sequential pipeline that coordinates profile intake, parallel search, and guardrail validation.",
    sub_agents=[intake_agent, parallel_search, guardrail_response_agent]
)
