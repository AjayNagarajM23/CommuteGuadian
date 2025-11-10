from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
import asyncio # Import asyncio


from models.anomaly_detection_request import AnomalyDetectionRequest
from models.anomaly_detection_response import CityAnomalyReport
from Agents.Sub_Agent_1.agent import root_agent
from Agents.Sub_Agent_2.agent import address_resolution_agent
from Agents.Sub_Agent_1.tools.image_descriptor_tool import get_image_description
from Agents.agent_runner import get_adk_runner, get_message, get_session_service

APP_NAME = "city_anomaly_detector_data_ingest_1"

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

session_service = get_session_service()

# --- FastAPI Application Initialization ---
app = FastAPI(
    title="ADK Agent API",
    description="API for interacting with a Google ADK agent.",
    version="1.0.0",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- API Endpoint ---
@app.post("/query", response_model=CityAnomalyReport, status_code=200)
async def query_agent(
    request: AnomalyDetectionRequest,
):
    """
    Processes an anomaly detection request using the ADK agents and returns a city anomaly report.

    - **time**: Unix timestamp of the anomaly event.
    - **latitude**: Latitude coordinate of the event.
    - **longitude**: Longitude coordinate of the event.
    - **image_data_base64: str = Field(..., description="Base64 encoded image data (JPEG, PNG, etc.).")**: URL of the image related to the anomaly.
    - **user_input**: Optional user-provided input or description.
    - **user_id**: Identifier for the user making the request.
    - **session_id**: Identifier for the conversation/session.
    """
    time = request.time
    latitude = request.latitude
    longitude = request.longitude
    image = request.image_data_base64
    user_input = request.user_input if request.user_input else ""
    user_id = request.user_id
    session_id = request.session_id

    runner1 = get_adk_runner(root_agent, APP_NAME, session_service)
    runner2 = get_adk_runner(address_resolution_agent, APP_NAME, session_service)
    
    logger.info(f"Received request from user '{user_id}', session '{session_id}'")

    try:
        # Check if session exists.
        existing_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )

        if not existing_session:
            # Create a new session if it doesn't exist.
            await session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id
            )
            logger.info(f"Created new session for user '{user_id}' with ID '{session_id}'.")
        else:
            logger.info(f"Using existing session for user '{user_id}' with ID '{session_id}'.")

        agent1_raw_response_text = "" 
        agent2_raw_response_text = ""

        description = await get_image_description(image)

        # Define async functions to get responses from each runner
        async def get_agent1_response():
            nonlocal agent1_raw_response_text
            async for event in runner1.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=get_message(description)
            ):
                if event.is_final_response():
                    agent1_raw_response_text = event.content.parts[0].text
            return agent1_raw_response_text

        async def get_agent2_response():
            nonlocal agent2_raw_response_text
            async for event in runner2.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=get_message(f"Latitude: {latitude}, Longitude: {longitude}")
            ):
                if event.is_final_response():
                    agent2_raw_response_text = event.content.parts[0].text
            return agent2_raw_response_text
        
        # Run both agents concurrently
        # The order of results in the list will correspond to the order of awaitables passed to gather
        results = await asyncio.gather(
            get_agent1_response(),
            get_agent2_response()
        )

        agent1_raw_response_text = results[0]
        agent2_raw_response_text = results[1]
                
        if not agent1_raw_response_text:
            logger.warning(f"Agent 1 did not produce a final response for session '{session_id}'.")
            raise HTTPException(status_code=500, detail="Agent 1 did not produce a response.")
        if not agent2_raw_response_text:
            logger.warning(f"Agent 2 did not produce a final response for session '{session_id}'.")
            raise HTTPException(status_code=500, detail="Agent 2 did not produce a response.")

        try:
            parsed_json_1 = json.loads(agent1_raw_response_text)
            parsed_json_2 = json.loads(agent2_raw_response_text)
            
            final_response = CityAnomalyReport(unix_timestamp=time, **parsed_json_1, **parsed_json_2)
            logger.info(f"Successfully parsed agent response into CityAnomalyReport model.")
            return final_response
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse agent response as JSON: {e}. Raw response: {agent1_raw_response_text}, {agent2_raw_response_text}", exc_info=True)
            raise HTTPException(status_code=500, detail="Agent returned invalid JSON.")
        except Exception as e:
            logger.error(f"Failed to validate agent response against CityAnomalyReport model: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Agent response did not match expected structure.")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing query for session '{session_id}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")