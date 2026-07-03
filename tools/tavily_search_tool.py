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
import json
import asyncio
import threading
import warnings
from urllib.parse import urlparse

# Suppress all library-level warnings in this tool's context
warnings.filterwarnings("ignore")

from google.adk.tools import ToolContext
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def query_tavily_mcp(query: str, api_key: str) -> str:
    """
    Connects to the remote Tavily MCP server over Streamable HTTP (SSE),
    executes the search query, and formats the output.
    """
    # Remote HTTP transport endpoint
    url = f"https://mcp.tavily.com/mcp/?tavilyApiKey={api_key}"
    
    async with streamable_http_client(url) as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize connection with the remote server
            await session.initialize()
            
            # Execute search with tavily_search tool, restricting to government portals
            result = await session.call_tool(
                "tavily_search",
                arguments={
                    "query": query,
                    "include_domains": ["gov.in", "nic.in"],
                    "max_results": 5
                }
            )
            
            # Parse responses
            output_parts = []
            if result and result.content:
                for content_part in result.content:
                    if hasattr(content_part, 'text') and content_part.text:
                        output_parts.append(content_part.text)
                    elif isinstance(content_part, dict) and content_part.get("text"):
                        output_parts.append(content_part.get("text"))
                    else:
                        output_parts.append(str(content_part))
            
            raw_text = "\n".join(output_parts)
            
            # Parse Tavily JSON output and format it consistently with DuckDuckGo results
            try:
                data = json.loads(raw_text)
                if isinstance(data, dict) and "results" in data:
                    formatted_results = []
                    for idx, item in enumerate(data.get("results", [])):
                        title = item.get("title", "No Title")
                        link = item.get("url", "")
                        content = item.get("content", "No description available.")
                        formatted_results.append(
                            f"{idx + 1}. Source Title: {title}\n"
                            f"   Link: {link}\n"
                            f"   Summary: {content}\n"
                        )
                    if formatted_results:
                        return "\n".join(formatted_results)
            except Exception:
                pass
                
            return raw_text

def run_async_in_thread(coro):
    """
    Runs an asynchronous coroutine in a separate thread with a new event loop.
    This prevents 'asyncio.run() cannot be called from a running event loop' errors.
    """
    result = None
    exception = None

    def worker():
        nonlocal result, exception
        try:
            result = asyncio.run(coro)
        except Exception as e:
            exception = e

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

    if exception:
        raise exception
    return result

def tavily_search(query: str) -> str:
    """
    Search the web for up-to-date Indian government welfare schemes using the Tavily MCP Search service.
    Only official portals (ending in .gov.in or .nic.in) are queried.
    
    Args:
        query: The search terms or questions to lookup (e.g., scheme name or eligibility criteria).
        
    Returns:
        A list of top relevant scheme details and benefits from official sites.
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY environment variable is not set."
        
    try:
        # Run the async query in a separate thread to avoid event loop conflicts
        results = run_async_in_thread(query_tavily_mcp(query, api_key))
        if not results:
            return "No search results returned from Tavily."
        return results
    except Exception as e:
        return f"Error executing Tavily search via MCP: {str(e)}"

async def query_tavily_extract_mcp(urls: list[str], api_key: str) -> str:
    """
    Connects to the remote Tavily MCP server and calls tavily_extract.
    """
    url = f"https://mcp.tavily.com/mcp/?tavilyApiKey={api_key}"
    async with streamable_http_client(url) as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # Execute extract tool on remote server
            result = await session.call_tool(
                "tavily_extract",
                arguments={
                    "urls": urls,
                    "extract_depth": "basic",
                    "format": "markdown"
                }
            )
            
            output_parts = []
            if result and result.content:
                for content_part in result.content:
                    if hasattr(content_part, 'text') and content_part.text:
                        output_parts.append(content_part.text)
                    elif isinstance(content_part, dict) and content_part.get("text"):
                        output_parts.append(content_part.get("text"))
                    else:
                        output_parts.append(str(content_part))
            
            return "\n".join(output_parts)

def tavily_extract(urls: list[str]) -> str:
    """
    Extract clean markdown or text content from one or more URLs.
    Supports official portals (ending in .gov.in or .nic.in).
    
    Args:
        urls: A list of URL strings to extract content from.
        
    Returns:
        The extracted page content in clean markdown format.
    """
    # Enforce gov.in/nic.in filter at the tool layer for security/guardrails
    allowed_urls = []
    for u in urls:
        try:
            parsed = urlparse(u)
            domain = parsed.netloc.lower()
            if ":" in domain:
                domain = domain.split(":", 1)[0]
            if domain.endswith(".gov.in") or domain.endswith(".nic.in"):
                allowed_urls.append(u)
        except Exception:
            pass
            
    if not allowed_urls:
        return "Error: No official government URLs (.gov.in or .nic.in) provided for extraction."
        
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY environment variable is not set."
        
    try:
        results = run_async_in_thread(query_tavily_extract_mcp(allowed_urls, api_key))
        if not results:
            return "No content extracted from the provided URLs."
        return results
    except Exception as e:
        return f"Error executing Tavily extract via MCP: {str(e)}"

