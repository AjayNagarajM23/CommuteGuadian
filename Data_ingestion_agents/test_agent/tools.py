import os
import uuid
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from pydantic import ValidationError


# --- Custom ADK Tool: Anomaly Detector ---
async def detect_city_anomaly(
    image_data_base64: str,
    latitude: float,
    longitude: float,
    user_input: Optional[str] = None
) -> Dict[str, Any]:
    """
    ADK Tool: Analyzes an image and location to detect city anomalies and
    generates a structured JSON output using Gemini's multimodal capabilities
    and response schema.
    """
    logger.info("Calling detect_city_anomaly tool...")

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

    chat_history = []
    chat_history.append({
        "role": "user",
        "parts": [
            {"text": prompt_text},
            {
                "inlineData": {
                    "mimeType": "image/jpeg", # Assuming JPEG, but could be dynamic
                    "data": image_data_base64
                }
            }
        ]
    })

    # Define the JSON schema for the response
    response_schema = {
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
    }

    payload = {
        "contents": chat_history,
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }
    }

    api_key = os.getenv("GOOGLE_API_KEY", "") # Use environment variable for API key
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{AGENT_MODEL}:generateContent?key={api_key}"

    try:
        import httpx # Assuming httpx is available in the environment

        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload, timeout=60.0) # Added timeout
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            result = response.json()

        if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
            json_str = result["candidates"][0]["content"]["parts"][0].get("text")
            if not json_str:
                raise ValueError("LLM response content is empty or not text.")

            # Parse the JSON string
            anomaly_event_data = {}
            try:
                anomaly_event_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from LLM: {e}. Raw response: {json_str}")
                raise ValueError(f"LLM returned malformed JSON: {json_str}")

            # Add dynamic fields
            anomaly_event_data["event_id"] = str(uuid.uuid4())
            anomaly_event_data["ingestion_timestamp"] = datetime.now(timezone.utc).isoformat(timespec='milliseconds') + 'Z'
            anomaly_event_data["source_media_uri"] = "uploaded_image" # Consistent naming

            # Ensure geocode is correctly structured, LLM might return it flat or slightly off
            if "geocode" not in anomaly_event_data or not isinstance(anomaly_event_data["geocode"], dict):
                anomaly_event_data["geocode"] = {"latitude": latitude, "longitude": longitude}
            else:
                anomaly_event_data["geocode"]["latitude"] = latitude
                anomaly_event_data["geocode"]["longitude"] = longitude

            # Validate against Pydantic model
            try:
                validated_event = AnomalyDetectionEvent(**anomaly_event_data)
                logger.info(f"Successfully generated and validated anomaly event: {validated_event.event_id}")
                return validated_event.dict()
            except ValidationError as e:
                logger.error(f"Generated JSON does not match schema: {e.errors()}", exc_info=True)
                raise ValueError(f"LLM generated invalid schema: {e.errors()}")
        else:
            raise ValueError("LLM response structure is unexpected or content is missing.")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during LLM call: {e.response.status_code} - {e.response.text}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"LLM API error: {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Network error during LLM call: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Network error communicating with LLM: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in detect_city_anomaly tool: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {e}")