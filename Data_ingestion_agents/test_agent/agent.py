import logging

from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from models import AgentResponse

# Load environment variables from .env file
# It's good practice to load these as early as possible.
from dotenv import load_dotenv
load_dotenv()

# --- Configuration ---
# Centralize configuration for easier management
APP_NAME = "my_agent_app"
AGENT_NAME = "api_agent"
AGENT_MODEL = "gemma3"
AGENT_DESCRIPTION = "An agent exposed via API for conversational queries."
AGENT_INSTRUCTION = """
    You are a helpful assistant.
    IMPORTANT: Your response MUST be valid JSON matching this structure:
        {
        "founding_date": {
            "description": "When the company was founded",
            "type": "string",
            "example": "2005-03-15"
        },
        "sectors": {
            "description": "What all industries it operates",
            "type": "List of strings",
            "example": ["Technology", "Financial Services", "Healthcare"]
        },
        "divisions": {
            "description": "What all divisions are there in the company",
            "type": "List of strings",
            "example": ["Software Development", "Hardware Engineering", "Customer Support"]
        },
        "locations": {
            "description": "Where all the company has its branches or operates",
            "type": "List of strings",
            "example": ["New York, USA", "London, UK", "Bengaluru, India"]
        }
    }

    DO NOT include any explanations or additional text outside the JSON response.
    Respond concisely and accurately.
"""

# --- Logging Setup ---
# Configure basic logging to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- ADK Agent and Session Service Initialization ---
# These are initialized globally as they are typically singletons for the application.
# For more complex scenarios (e.g., multiple agents), you might manage them differently.
root_agent = Agent(
    name=AGENT_NAME,
    model=AGENT_MODEL,
    description=AGENT_DESCRIPTION,
    instruction=AGENT_INSTRUCTION,
    output_schema=AgentResponse,
)

session_service = InMemorySessionService()
logger.info("ADK Agent and InMemorySessionService initialized.")

# --- Dependency for ADK Runner ---
# This function will be called by FastAPI to provide a Runner instance for each request.
# Using Depends ensures the Runner is correctly initialized with the global agent and session service.
def get_adk_runner() -> Runner:
    """
    Provides a configured ADK Runner instance.
    """
    return Runner(agent=root_agent, session_service=session_service, app_name=APP_NAME)

def get_message(user_message: str) -> types.Content:
    return types.Content(role="user", parts=[types.Part(text=user_message)])

