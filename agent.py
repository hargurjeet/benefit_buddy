import os
import sys

# Add project root and app folder to sys.path to support imports both locally and inside container deployments
project_root = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(project_root, "app")
for d in [app_dir, project_root]:
    if d not in sys.path:
        sys.path.insert(0, d)

from app.agent import (
    root_agent,
    parallel_search,
    intake_agent,
    web_search_agent,
    dataset_search_agent,
    guardrail_response_agent,
    tavily_search_agent,
)

