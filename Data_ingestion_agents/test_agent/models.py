from pydantic import BaseModel, Field
from typing import List, Optional

# # --- Pydantic Models for Anomaly Event Schema ---
# class Geocode(BaseModel):
#     latitude: float = Field(..., description="Latitude coordinate.")
#     longitude: float = Field(..., description="Longitude coordinate.")

# class AnomalyDetectionEvent(BaseModel):
#     event_id: str = Field(..., description="Unique identifier for the anomaly event.")
#     source_media_uri: str = Field(..., description="Name or URI of the source image.")
#     ingestion_timestamp: str = Field(..., description="Timestamp of when the event was ingested (ISO 8601 format).")
#     event_type: str = Field(..., description="Type of anomaly detected (e.g., waste_management, infrastructure_damage).")
#     description: str = Field(..., description="Detailed description of the anomaly.")
#     confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the detection (0.0 to 1.0).")
#     severity_level: str = Field(..., description="Severity level of the anomaly (e.g., low, medium, high, critical).")
#     location_description: str = Field(..., description="Textual description of the location.")
#     geocode: Geocode = Field(..., description="Geographic coordinates of the anomaly.")
#     detected_objects: List[str] = Field(..., description="List of objects detected in the image related to the anomaly.")
#     extracted_text: str = Field(..., description="Any text extracted from the image.")
#     status: str = Field(..., description="Current status of the anomaly (e.g., new_unverified, under_review, resolved).")

# # --- Pydantic Models for Request ---
# class AnomalyDetectionRequest(BaseModel):
#     """
#     Represents the request body for submitting an anomaly report.
#     """
#     image_data_base64: str = Field(..., description="Base64 encoded image data (JPEG, PNG, etc.).")
#     latitude: float = Field(..., description="Latitude coordinate of the image location.")
#     longitude: float = Field(..., description="Longitude coordinate of the image location.")
#     user_input: Optional[str] = Field(None, description="Optional additional context or notes from the user.")
#     user_id: str = Field("anonymous_reporter", description="A unique identifier for the user reporting the anomaly.")
#     session_id: str = Field("default_anomaly_session", description="A unique identifier for the conversation session.")

# --- Pydantic Models for Request and Response ---
class QueryRequest(BaseModel):
    """
    Represents the request body for the /query endpoint.
    """
    user_message: str = Field(..., description="The user's message to the agent.")
    user_id: str = Field("default_user", description="A unique identifier for the user.")
    session_id: str = Field("default_session", description="A unique identifier for the conversation session.")

class QueryResponse(BaseModel):
    """
    Represents the response body for the /query endpoint.
    """
    response: str = Field(..., description="The agent's response to the user's message.")
    user_id: str = Field(..., description="The user ID associated with the response.")
    session_id: str = Field(..., description="The session ID associated with the response.")

class AgentResponse(BaseModel):
    """
    Represents the agents output
    """

    founding_date: str = Field(
        description="When the company was founded"
    )
    sectors: List[str] = Field( # Corrected: Specify the type within List (e.g., List[str])
        description="What all industries it operates"
    )
    divisions: List[str] = Field( # Corrected: Specify the type within List (e.g., List[str])
        description="What all divisions are there in the company"
    )
    locations: List[str] = Field( # Corrected: Typo "loactions" changed to "locations", specify type
        description="Where all the company has it's branches or operates"
    )