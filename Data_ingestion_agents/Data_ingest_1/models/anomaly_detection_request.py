from pydantic import BaseModel, Field
from typing import Optional


# # --- Pydantic Models for Request ---
class AnomalyDetectionRequest(BaseModel):
    """
    Represents the request body for submitting an anomaly report.
    """
    time: float = Field(..., description="Timestamp of the anomaly report in ISO 8601 format.")
    latitude: float = Field(..., description="Latitude coordinate of the image location.")
    longitude: float = Field(..., description="Longitude coordinate of the image location.")
    image_data_base64: str = Field(..., description="Base64 encoded image data (JPEG, PNG, etc.).")
    user_input: Optional[str] = Field(None, description="Optional additional context or notes from the user.")
    user_id: str = Field("anonymous_reporter", description="A unique identifier for the user reporting the anomaly.")
    session_id: str = Field("default_anomaly_session", description="A unique identifier for the conversation session.")
