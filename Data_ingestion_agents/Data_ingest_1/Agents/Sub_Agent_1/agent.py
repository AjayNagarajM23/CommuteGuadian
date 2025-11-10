from google.adk.agents import LlmAgent, SequentialAgent
from .tools.image_descriptor_tool import get_image_description
from .model import SubAgent1OutPut
from .agent_config import (
    AGENT_NAME_AGENT1,
    AGENT_MODEL_AGENT1,
    AGENT_DESCRIPTION_AGENT1,
    AGENT_INSTRUCTION_AGENT1,
    AGENT_NAME_AGENT2,
    AGENT_MODEL_AGENT2,
    AGENT_DESCRIPTION_AGENT2,
    AGENT_INSTRUCTION_AGENT2,)


# image_description_agent = LlmAgent(
#     name=AGENT_NAME_AGENT1,
#     model=AGENT_MODEL_AGENT1,
#     description=AGENT_DESCRIPTION_AGENT1,
#     instruction=AGENT_INSTRUCTION_AGENT1,
#     tools=[get_image_description],
#     output_key="raw_image_description",
# )

output_formatting_agent = LlmAgent(
    name=AGENT_NAME_AGENT2,
    model=AGENT_MODEL_AGENT2,
    description=AGENT_DESCRIPTION_AGENT2,
    instruction=AGENT_INSTRUCTION_AGENT2,
    output_schema=SubAgent1OutPut,
    output_key="image_processing_output",
)


root_agent = output_formatting_agent


