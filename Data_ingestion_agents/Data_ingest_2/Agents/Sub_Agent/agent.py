# ./adk_agent_samples/mcp_agent/agent.py
import os
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

from .tool import google_search
from .model import CityAnomalyReport
from .agent_config import (
    AGENT_NAME_1,
    AGENT_MODEL_1,
    AGENT_DESCRIPTION_1,
    AGENT_INSTRUCTION_1,
    AGENT_NAME_2,
    AGENT_MODEL_2,
    AGENT_DESCRIPTION_2,
    AGENT_INSTRUCTION_2
)

search_agent = LlmAgent(
    model=AGENT_MODEL_1,
    name=AGENT_NAME_1,
    description=AGENT_DESCRIPTION_1,
    instruction=AGENT_INSTRUCTION_1,
    tools=[google_search],
    output_key="search_results",
)

out_put_formatter = LlmAgent(
    model=AGENT_MODEL_2,
    name=AGENT_NAME_2,
    description=AGENT_DESCRIPTION_2,
    instruction=AGENT_INSTRUCTION_2,
    output_schema=CityAnomalyReport,
    output_key="city_anomaly_report_output",
)

root_agent = SequentialAgent(
    name="city_anomaly_report_agent",
    description="A sequential agent that orchestrates the search and anomaly report formatting agents.",
    sub_agents=[search_agent, out_put_formatter],
)