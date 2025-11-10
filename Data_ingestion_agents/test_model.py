import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import json
import base64

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError

import google as genai
from google.genai import types # Still needed for types.Part and types.GenerationConfig

from dotenv import load_dotenv
load_dotenv()

# --- Configuration (kept for consistency, but some agent-specific ones might be less relevant) ---
APP_NAME = "Data_ingestion_App_1k"
AGENT_MODEL = "gemini-2.0-flash" # Still needed for the direct LLM call

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Pydantic Models for Anomaly Event Schema (Our desired output format) ---
class Geocode(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate.")
    longitude: float = Field(..., description="Longitude coordinate.")

class AnomalyDetectionEvent(BaseModel):
    event_id: str = Field(..., description="Unique identifier for the anomaly event.")
    source_media_uri: str = Field(..., description="Name or URI of the source image.")
    ingestion_timestamp: str = Field(..., description="Timestamp of when the event was ingested (ISO 8601 format).")
    event_type: str = Field(..., description="Type of anomaly detected (e.g., waste_management, infrastructure_damage).")
    description: str = Field(..., description="Detailed description of the anomaly.")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the detection (0.0 to 1.0).")
    severity_level: str = Field(..., description="Severity level of the anomaly (e.g., low, medium, high, critical).")
    location_description: str = Field(..., description="Textual description of the location.")
    geocode: Geocode = Field(..., description="Geographic coordinates of the anomaly.")
    detected_objects: List[str] = Field(..., description="List of objects detected in the image related to the anomaly.")
    extracted_text: str = Field(..., description="Any text extracted from the image.")
    status: str = Field(..., description="Current status of the anomaly (e.g., new_unverified, under_review, resolved).")

# --- Core Anomaly Detector Function (formerly an ADK Tool) ---
# This function now stands alone and is directly callable by FastAPI.
async def process_image_for_anomaly(
    image_data_base64: str,
    latitude: float,
    longitude: float,
    user_input: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyzes an image and location to detect city anomalies and
    generates a structured JSON output using Gemini's multimodal capabilities
    and response schema.
    """
    logger.info("Processing image for anomaly detection directly...")

    prompt_text = (
        "Analyze the provided image and the given location details. "
        "Identify any anomalies related to city management (e.g., waste, infrastructure, public safety). "
        "Consider the latitude and longitude: "
        f"Latitude: {latitude}, Longitude: {longitude}. "
        f"User provided additional context: {user_input if user_input else 'None'}. "
        "Generate a structured JSON object describing the anomaly. "
        "Ensure all fields in the schema are populated accurately. "
        "For 'event_id', use a placeholder or let the system generate it. "
        "For 'ingestion_timestamp', use a placeholder or let the system generate it. "
        "For 'source_media_uri', use 'uploaded_image'. "
        "For 'confidence_score', provide a value between 0.0 and 1.0 based on your certainty. "
        "For 'severity_level', choose from 'low', 'medium', 'high', 'critical'. "
        "For 'status', use 'new_unverified'."
    )

    client = genai.Client()

    response_schema_obj = types.Schema.from_dict({
        "type": "OBJECT",
        "properties": {
            "event_id": {"type": "STRING"},
            "source_media_uri": {"type": "STRING"},
            "ingestion_timestamp": {"type": "STRING"},
            "event_type": {"type": "STRING"},
            "description": {"type": "STRING"},
            "confidence_score": {"type": "NUMBER"},
            "severity_level": {"type": "STRING"},
            "location_description": {"type": "STRING"},
            "geocode": {
                "type": "OBJECT",
                "properties": {
                    "latitude": {"type": "NUMBER"},
                    "longitude": {"type": "NUMBER"}
                },
                "propertyOrdering": ["latitude", "longitude"]
            },
            "detected_objects": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            "extracted_text": {"type": "STRING"},
            "status": {"type": "STRING"}
        },
        "propertyOrdering": [
            "event_id", "source_media_uri", "ingestion_timestamp", "event_type",
            "description", "confidence_score", "severity_level", "location_description",
            "geocode", "detected_objects", "extracted_text", "status"
        ]
    })

    try:
        response = await client.models.generate_content_async(
            model=AGENT_MODEL, # Using AGENT_MODEL as the LLM model name
            contents=[
                types.Part.from_text(prompt_text),
                types.Part.from_bytes(
                    data=base64.b64decode(image_data_base64),
                    mime_type='image/jpeg',
                ),
            ],
            generation_config=types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=response_schema_obj
            )
        )

        json_str = response.text
        if not json_str:
            raise ValueError("LLM response content is empty or not text.")

        anomaly_event_data = {}
        try:
            anomaly_event_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM: {e}. Raw response: {json_str}")
            raise ValueError(f"LLM returned malformed JSON: {json_str}")

        anomaly_event_data["event_id"] = str(uuid.uuid4())
        anomaly_event_data["ingestion_timestamp"] = datetime.now(timezone.utc).isoformat(timespec='milliseconds') + 'Z'
        anomaly_event_data["source_media_uri"] = "uploaded_image"

        if "geocode" not in anomaly_event_data or not isinstance(anomaly_event_data["geocode"], dict):
            anomaly_event_data["geocode"] = {"latitude": latitude, "longitude": longitude}
        else:
            anomaly_event_data["geocode"]["latitude"] = latitude
            anomaly_event_data["geocode"]["longitude"] = longitude

        try:
            validated_event = AnomalyDetectionEvent(**anomaly_event_data)
            logger.info(f"Successfully generated and validated anomaly event: {validated_event.event_id}")
            return validated_event.dict()
        except ValidationError as e:
            logger.error(f"Generated JSON does not match schema: {e.errors()}", exc_info=True)
            raise ValueError(f"LLM generated invalid schema: {e.errors()}")

    except genai.types.APIError as e:
        logger.error(f"Gemini API error: {e.message} (Code: {e.code})", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e.message}")
    except Exception as e:
        logger.error(f"Unexpected error in process_image_for_anomaly: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {e}")

# --- FastAPI Application Initialization ---
app = FastAPI(
    title="Direct Anomaly Detection API",
    description="API for ingesting image-based anomaly reports directly via Gemini.",
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

# --- Pydantic Models for Request and Response ---
class QueryRequest(BaseModel):
    """
    Represents the request body for the /query endpoint for anomaly detection.
    """
    image_data_base64: str = Field(..., description="Base64 encoded image data (JPEG, PNG, etc.).")
    latitude: float = Field(..., description="Latitude coordinate of the image location.")
    longitude: float = Field(..., description="Longitude coordinate of the image location.")
    user_input: Optional[str] = Field(None, description="Optional additional context or notes from the user.")
    user_id: str = Field("default_user", description="A unique identifier for the user.")
    session_id: str = Field("default_session", description="A unique identifier for the conversation session.")

class QueryResponse(AnomalyDetectionEvent):
    """
    Represents the response body for the /query endpoint, which is an AnomalyDetectionEvent.
    """
    pass

# --- API Endpoint ---
@app.post("/query", response_model=QueryResponse, status_code=200)
async def query_endpoint( # Renamed to avoid conflict with `query_agent` if ADK was still used
    request: QueryRequest
):
    """
    Processes an image and location data directly using the Gemini model for anomaly detection
    and returns the structured anomaly event.

    - **image_data_base64**: Base64 encoded image string.
    - **latitude**: Latitude of the image location.
    - **longitude**: Longitude of the image location.
    - **user_input**: Optional text input from the user.
    - **user_id**: Identifier for the user submitting the report (for logging/tracking, not session).
    - **session_id**: Identifier for the conversation session (for logging/tracking, not session).
    """
    user_id = request.user_id
    session_id = request.session_id # Session ID is now just for logging/tracking, not ADK session management

    logger.info(f"Received direct anomaly detection request from user '{user_id}', session '{session_id}'.")

    try:
        # Directly call the anomaly processing function
        anomaly_event_data = await process_image_for_anomaly(
            image_data_base64=request.image_data_base64,
            latitude=request.latitude,
            longitude=request.longitude,
            user_input=request.user_input
        )
        return AnomalyDetectionEvent(**anomaly_event_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing anomaly report for session '{session_id}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error during anomaly reporting: {e}")

# Example of how to run this application (for local testing):
# Save this code as `main.py`
# Install dependencies:
# `pip install fastapi uvicorn python-dotenv pydantic google-generativeai`
# Ensure you have GOOGLE_API_KEY for Gemini API.
# Run the server: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
# You can then access the API documentation at http://localhost:8000/docs
