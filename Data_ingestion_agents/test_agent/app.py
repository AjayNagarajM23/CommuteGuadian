from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
import json # Import the json module

from google.adk.runners import Runner

from models import QueryRequest, QueryResponse, AgentResponse # Assuming AgentResponse is correctly imported from models.py
from agent import get_adk_runner, session_service, APP_NAME, get_message

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
@app.post("/query", response_model=AgentResponse, status_code=200)
async def query_agent(
    request: QueryRequest,
    runner: Runner = Depends(get_adk_runner) # Inject the runner
):
    """
    Processes a user query using the ADK agent and returns a response.

    - **user_message**: The text message from the user.
    - **user_id**: An identifier for the user (defaults to "default_user").
    - **session_id**: An identifier for the conversation session (defaults to "default_session").
    """
    user_id = request.user_id
    session_id = request.session_id
    user_message = request.user_message

    logger.info(f"Received query from user '{user_id}', session '{session_id}': '{user_message}'")

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

        agent_raw_response_text = "" # Rename to be clearer it's the raw string from agent
        # The runner.run_async method is an async generator
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=get_message(user_message)
        ):
            if event.is_final_response():
                agent_raw_response_text = event.content.parts[0].text
                logger.info(f"Agent raw response for session '{session_id}': '{agent_raw_response_text}'")
                break
        
        if not agent_raw_response_text:
            logger.warning(f"Agent did not produce a final response for session '{session_id}'.")
            raise HTTPException(status_code=500, detail="Agent did not produce a response.")

        # --- NEW LOGIC: Parse JSON string and create AgentResponse instance ---
        try:
            # Assuming agent_raw_response_text is a valid JSON string
            parsed_json = json.loads(agent_raw_response_text)
            # Create an instance of AgentResponse from the parsed dictionary
            final_response = AgentResponse(**parsed_json)
            logger.info(f"Successfully parsed agent response into AgentResponse model.")
            return final_response
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse agent response as JSON: {e}. Raw response: {agent_raw_response_text}", exc_info=True)
            raise HTTPException(status_code=500, detail="Agent returned invalid JSON.")
        except Exception as e:
            logger.error(f"Failed to validate agent response against AgentResponse model: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Agent response did not match expected structure.")

    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing query for session '{session_id}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

