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

from google.adk.agents import LlmAgent
from tools.tavily_search_tool import tavily_search, tavily_extract

async def skip_if_profile_incomplete(callback_context):
    """
    Prevents the agent from executing if the user's demographic profile intake is incomplete
    or if the request is blocked by the security guardrail.
    """
    if callback_context.state.get("security_blocked") or not callback_context.state.get("profile_complete"):
        callback_context._invocation_context.end_invocation = True
        return None
    return None

tavily_search_agent = LlmAgent(
    name="tavily_search_agent",
    model="gemini-2.5-flash",
    description="Search the web and extract guidelines using Tavily MCP for up-to-date welfare schemes.",
    instruction="""Search for government schemes using the tavily_search tool. 
If you find highly relevant scheme URLs that end in .gov.in or .nic.in, you can use the tavily_extract tool by passing a list of URLs to extract full detailed guidelines, eligibility criteria, checklists, and application steps for the final response.""",
    tools=[tavily_search, tavily_extract],
    output_key="tavily_search_result",
    before_agent_callback=skip_if_profile_incomplete
)
