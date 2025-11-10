import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import  ValidationError

# ADK and Gemini imports
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService # Using InMemorySessionService for agent's internal session management
from google.adk.tools import FunctionTool # To define our custom tool
from google.genai import types

from models import AnomalyDetectionEvent, AnomalyDetectionRequest

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# --- Configuration ---
APP_NAME = "city_anomaly_detector"
AGENT_NAME = "anomaly_detection_agent"
AGENT_MODEL = "gemini-2.0-flash" # Gemini Flash supports multimodal input
AGENT_DESCRIPTION = "An agent designed to detect and report city anomalies from images and location data."
AGENT_INSTRUCTION = """
You are an expert anomaly detection system for city management.
Your primary task is to analyze an image, its geographic coordinates (latitude, longitude), and optional user input to identify and describe anomalies related to waste management, infrastructure damage, public safety hazards, or other urban issues.
You MUST use the 'detect_city_anomaly' tool to process the input and generate a structured JSON output.
Ensure the JSON output strictly adheres to the specified schema, including generating a unique event_id and current ingestion_timestamp.
Focus on providing clear, concise descriptions, accurate severity levels, and comprehensive lists of detected objects.
"""

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Register the custom tool with ADK
anomaly_detection_tool = FunctionTool(
    name="detect_city_anomaly",
    description="Detects city anomalies from an image, latitude, longitude, and optional user input, returning a structured JSON event.",
    func=detect_city_anomaly,
    # Define the input schema for the tool, so the LLM knows how to call it
    input_schema={
        "type": "OBJECT",
        "properties": {
            "image_data_base64": {"type": "STRING", "description": "Base64 encoded image data."},
            "latitude": {"type": "NUMBER", "description": "Latitude of the image location."},
            "longitude": {"type": "NUMBER", "description": "Longitude of the image location."},
            "user_input": {"type": "STRING", "description": "Optional additional context from the user.", "nullable": True}
        },
        "required": ["image_data_base64", "latitude", "longitude"]
    }
)

# --- FastAPI Application Initialization ---
app = FastAPI(
    title="City Anomaly Detection API",
    description="API for ingesting image-based anomaly reports in a city, powered by Google ADK and Gemini.",
    version="1.0.0",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # WARNING: Be specific in production!
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- ADK Agent and Session Service Initialization ---
my_agent = Agent(
    name=AGENT_NAME,
    model=AGENT_MODEL,
    description=AGENT_DESCRIPTION,
    instruction=AGENT_INSTRUCTION,
    tools=[anomaly_detection_tool], # Use our custom anomaly detection tool
)

session_service = InMemorySessionService()
logger.info("ADK Agent and InMemorySessionService initialized.")




# --- Dependency for ADK Runner ---
def get_adk_runner() -> Runner:
    """
    Provides a configured ADK Runner instance.
    """
    return Runner(agent=my_agent, session_service=session_service, app_name=APP_NAME)

# --- API Endpoint ---
@app.post("/report_anomaly", response_model=AnomalyDetectionEvent, status_code=200)
async def report_anomaly(
    request: AnomalyDetectionRequest,
    runner: Runner = Depends(get_adk_runner)
):
    """
    Submits an image and location data to the agent for anomaly detection.
    The detected anomaly event is returned in a structured JSON format.

    - **image_data_base64**: Base64 encoded image string.
    - **latitude**: Latitude of the image location.
    - **longitude**: Longitude of the image location.
    - **user_input**: Optional text input from the user.
    - **user_id**: Identifier for the user submitting the report.
    - **session_id**: Identifier for the conversation session.
    """
    user_id = request.user_id
    session_id = request.session_id

    logger.info(f"Received anomaly report from user '{user_id}', session '{session_id}'.")

    try:
        # Ensure session exists or create it
        existing_session = session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )

        if not existing_session:
            session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id
            )
            logger.info(f"Created new session for user '{user_id}' with ID '{session_id}'.")
        else:
            logger.info(f"Using existing session for user '{user_id}' with ID '{session_id}'.")

        # Construct the message for the agent to trigger the tool
        agent_message_parts = [
            types.Part(text="Please analyze the attached image and location for city anomalies."),
            types.Part(text=f"Location: Latitude {request.latitude}, Longitude {request.longitude}."),
            types.Part(text=f"User notes: {request.user_input if request.user_input else 'None'}."),
            types.Part(
                inline_data=types.Blob(
                    mime_type="image/jpeg", # Assuming JPEG; adjust if other types are expected
                    data=request.image_data_base64
                )
            )
        ]

        anomaly_event_data = None
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(role="user", parts=agent_message_parts)
        ):
            if event.is_final_response():
                # The final response from the agent should be the JSON string
                # returned by our `detect_city_anomaly` tool.
                response_content = event.content.parts[0].text
                try:
                    anomaly_event_data = AnomalyDetectionEvent.parse_raw(response_content)
                    logger.info(f"Agent successfully returned anomaly event: {anomaly_event_data.event_id}")
                except ValidationError as e:
                    logger.error(f"Agent's final response was not valid JSON or did not match schema: {e}", exc_info=True)
                    raise HTTPException(status_code=500, detail="Agent returned malformed or invalid anomaly data.")
                break
            elif event.is_tool_code():
                # This indicates the agent decided to call a tool.
                # The `detect_city_anomaly` tool is designed to return the final JSON.
                logger.info(f"Agent chose to execute tool: {event.tool_code.function_call.name}")
            elif event.is_model_response():
                # This is an intermediate model response, not the final structured output
                logger.debug(f"Intermediate model response: {event.content.parts[0].text}")


        if not anomaly_event_data:
            logger.warning(f"Agent did not produce a final anomaly event for session '{session_id}'.")
            raise HTTPException(status_code=500, detail="Agent failed to produce a valid anomaly detection event.")

        return anomaly_event_data

    except HTTPException:
        # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Error processing anomaly report for session '{session_id}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error during anomaly reporting: {e}")

# Example of how to run this application (for local testing):
# Save this code as `main.py`
# Install dependencies:
# `pip install fastapi uvicorn google-adk python-dotenv pydantic httpx`
# Ensure you have GOOGLE_API_KEY for Gemini API.
# Run the server: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
# You can then access the API documentation at http://localhost:8000/docs