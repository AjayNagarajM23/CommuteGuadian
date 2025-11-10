# ./adk_agent_samples/mcp_agent/agent.py
from google.adk.agents import LlmAgent, SequentialAgent

from .tool import tools
from .model import AddressDetailsOutput
from .agent_config import (
    APP_NAME,
    AGENT_NAME_1,
    AGENT_MODEL_1,
    AGENT_DESCRIPTION_1,
    AGENT_INSTRUCTION_1,
    AGENT_NAME_2,
    AGENT_MODEL_2,
    AGENT_DESCRIPTION_2,
    AGENT_INSTRUCTION_2
)


"""
This one might fail because of the Timeout error, so go to the 
.venv/lib/python3.12/site-packages/google/adk/tools/mcp_tool/mcp_session_manager.py timeout = 60 / 180 seconds
This one we have to do manually !!!
Refer : https://github.com/google/adk-python/issues/1086
"""
rev_geo_agent = LlmAgent(
    model=AGENT_MODEL_1,
    name=AGENT_NAME_1,
    description=AGENT_DESCRIPTION_1,
    instruction=AGENT_INSTRUCTION_1,
    tools=tools,
    # tools=[reverse_geocode_tool],
    output_key="raw_address",
)

address_formatter_agent = LlmAgent(
    model=AGENT_MODEL_2,
    name=AGENT_NAME_2,
    description=AGENT_DESCRIPTION_2,
    instruction=AGENT_INSTRUCTION_2,
    output_schema=AddressDetailsOutput,
    output_key="address_resolution_output",
)

address_resolution_agent = SequentialAgent(
    name="address_resolution_agent",
    description="A sequential agent that orchestrates the reverse geocoding and address formatting agents.",
    sub_agents=[rev_geo_agent, address_formatter_agent],
)

root_agent = address_resolution_agent