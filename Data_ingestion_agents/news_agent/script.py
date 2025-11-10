import asyncio
import time
from itertools import product
from google.adk.agents import LlmAgent
from tool import google_search
import logging
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types


APP_NAME = "new_agent_app"
SESSION_ID = "default_session"
USER_ID = "default_user"

# Define all possible events and locations
events = [
    "water logging",
    "tree fall",
    "power outage",
    "traffic congestion",
    "signal failure",
    "road block",
    "potholes",
    "garbage pile-up",
    "sewage overflow",
    "fire incident",
    "metro delay",
    "construction debris",
    "noise complaint",
    "streetlight not working",
    "stray animal alert",
    "accident report",
    "protest",
    "road cave-in"
]

locations = [
    "Marathahalli",
    "Whitefield",
    "Koramangala",
    "Indiranagar",
    "Jayanagar",
    "HSR Layout",
    "Electronic City",
    "MG Road",
    "Hebbal",
    "Banashankari",
    "Rajajinagar",
    "Yelahanka",
    "Malleshwaram",
    "KR Puram",
    "Bellandur",
    "BTM Layout",
    "Basavanagudi",
    "Silk Board",
    "Sarjapur Road",
    "Majestic"
]
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


session_service = InMemorySessionService()
logger.info("Summarization Agent and InMemorySessionService initialized.")

def get_adk_runner(agent, app_name, session_service) -> Runner:
    """
    Provides a configured ADK Runner instance.
    """
    return Runner(agent=agent, session_service=session_service, app_name=app_name)

def get_message(user_message: str) -> types.Content:
    return types.Content(role="user", parts=[types.Part(text=user_message)])


def get_session_service():
    """
    Returns an instance of InMemorySessionService for managing user sessions.
    This is used to store and retrieve session data across requests.
    """
    logger.info("InMemorySessionService initialized.")
    return InMemorySessionService()

async def run_agent_with_combinations():
    """
    Runs the agent with all combinations of events and locations.
    """
    session_service = get_session_service()

    for event, location in product(events, locations):
        root_agent = LlmAgent(
            name="news_retrieval_agent",
            model="gemini-2.0-flash",
            description="An intelligent agent designed to retrieve recent news based on specific events and locations.",
            instruction=f"""
You are an anomaly detection search agent. Your primary task is to find recent news articles and other relevant online content that report on city anomalies based on the input location and event. These anomalies include, but are not limited to: floods, significant construction activities, fallen trees, and electricity outages.

**Tool Usage:**
You will use a hypothetical tool named `search_tool`.
This tool takes a `query` (string) as an argument.

**Input:** Event and Location details will be provided

**Action:** Use the 'search_tool' with a carefully constructed query to find relevant and *recent* articles. Focus on terms that indicate recency (e.g., "today," "yesterday," "this week," "recent news").

**Output:** The exact text description returned by the 'search_tool', which should ideally be snippets or summaries of recent articles.Limit the description to not more than 100 words.

**Example Input:**
"recent news about [floods] in [City Name]"

""",
     tools=[google_search],  # Add more tools here if needed in the future
        )

        user_input = f"Search for news related to city anomalies in Bangalore regions based on the event '{event}' and location '{location}'."

        runner = get_adk_runner(root_agent, APP_NAME, session_service=session_service)

        try:
            # Check if session exists
            existing_session = await session_service.get_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=SESSION_ID
            )

            if not existing_session:
                # Create a new session if it doesn't exist
                await session_service.create_session(
                    app_name=APP_NAME,
                    user_id=USER_ID,
                    session_id=SESSION_ID
                )
                logger.info(f"Created new session for user '{USER_ID}' with ID '{SESSION_ID}'.")
            else:
                logger.info(f"Using existing session for user '{USER_ID}' with ID '{SESSION_ID}'.")

            # The runner.run_async method is an async generator
            async for event_response in runner.run_async(
                user_id=USER_ID,
                session_id=SESSION_ID,
                new_message=get_message(user_input)
            ):
                logger.info(f"Received event response: {event_response}")

        except Exception as e:
            logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    while True:
        asyncio.run(run_agent_with_combinations())
        print("Waiting for 5 minutes before the next run...")
        time.sleep(300)  # Wait for 5 minutes (300 seconds)