# Copyright (c) 2026 MyCompany LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
from tavily_search_agent import tavily_search_agent

# 2. Parallel Search: Runs the web search, dataset search, and Tavily search concurrently
parallel_search = ParallelAgent(
    name="parallel_search",
    description="Run web search, dataset query, and Tavily search in parallel.",
    sub_agents=[web_search_agent, dataset_search_agent, tavily_search_agent]
)

# Root Agent: Pipelines the three stages sequentially
root_agent = SequentialAgent(
    name="benefit_buddy_pipeline",
    description="BenefitBuddy sequential pipeline that coordinates profile intake, parallel search, and guardrail validation.",
    sub_agents=[intake_agent, parallel_search, guardrail_response_agent]
)

from google.adk.apps import App

app = App(root_agent=root_agent, name="app")
