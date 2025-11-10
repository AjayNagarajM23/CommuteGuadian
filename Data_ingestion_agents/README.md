## Data Ingestion Agents Documentation

This documentation describes the components within the `Data_ingestion_agents` folder, specifically focusing on the two data ingestion applications (`Data_ingest_1` and `Data_ingest_2`) and the data models used for anomaly detection.

### 1. `Data_ingest_1` Application

*   **Description:** This FastAPI application (`Data_ingestion_agents/Data_ingest_1/app.py`) is designed to process anomaly detection requests. It utilizes two sub-agents: an `image_processing_agent` and an `address_resolution_agent`. It takes an `AnomalyDetectionRequest` as input, processes the image and location information using the respective agents, and returns a `CityAnomalyReport` containing the combined results.
*   **Endpoint:** `/query` (POST)
*   **Request Model:** `AnomalyDetectionRequest`
*   **Response Model:** `CityAnomalyReport`
*   **Functionality:**
    *   Receives anomaly detection requests with timestamp, location, image URL, and optional user input.
    *   Initializes or retrieves a user session.
    *   Runs the `image_processing_agent` and `address_resolution_agent` concurrently.
    *   Combines the outputs from both agents into a single `CityAnomalyReport`.
    *   Handles potential errors during agent execution or JSON parsing.

### 2. `Data_ingest_2` Application

*   **Description:** This FastAPI application (`Data_ingestion_agents/Data_ingest_2/app.py`) is another data ingestion point. It uses a `root_agent` to process anomaly detection requests. Similar to `Data_ingest_1`, it takes an `AnomalyDetectionRequest` and returns a `CityAnomalyReport`.
*   **Endpoint:** `/query` (POST)
*   **Request Model:** `AnomalyDetectionRequest`
*   **Response Model:** `CityAnomalyReport`
*   **Functionality:**
    *   Receives anomaly detection requests with user input, user ID, and session ID.
    *   Initializes or retrieves a user session.
    *   Runs the `root_agent` to process the user input.
    *   Parses the agent's JSON response into a `CityAnomalyReport`.
    *   Handles potential errors during agent execution or JSON parsing.

### 3. Data Models

*   **`AnomalyDetectionRequest`** (`Data_ingestion_agents/Data_ingest_1/models/anomaly_detection_request.py`)
    *   **Description:** Represents the input structure for an anomaly detection request.
    *   **Fields:**
        *   `time` (float): Unix timestamp of the anomaly report.
        *   `latitude` (float): Latitude coordinate of the image location.
        *   `longitude` (float): Longitude coordinate of the image location.
        *   `image_url` (str): URL of the image to be analyzed.
        *   `user_input` (Optional[str]): Optional additional context from the user.
        *   `user_id` (str): Unique identifier for the user (defaults to "anonymous_reporter").
        *   `session_id` (str): Unique identifier for the conversation session (defaults to "default_anomaly_session").

*   **`CityAnomalyReport`** (`Data_ingestion_agents/Data_ingest_1/models/anomaly_detection_response.py`)
    *   **Description:** Represents the output structure for a city anomaly report, combining anomaly details and location information.
    *   **Fields:**
        *   `unix_timestamp` (float): The Unix timestamp from the user request.
        *   `event_type` (str): Classification of the detected anomaly (e.g., 'Structural Damage', 'Environmental Hazard').
        *   `description` (str): A detailed description of the observed anomaly.
        *   `severity_level` (str): Assessed severity of the anomaly ('Low', 'Medium', 'High').
        *   `latitude` (float): Latitude coordinate of the anomaly location.
        *   `longitude` (float): Longitude coordinate of the anomaly location.
        *   `formatted_address` (str): Full human-readable address.
        *   `house_number` (Optional[str]): House or building number.
        *   `street_name` (Optional[str]): Street name.
        *   `area_name` (Optional[str]): Local area or neighborhood name.
        *   `city` (Optional[str]): City or town name.
        *   `district` (Optional[str]): District or county name.
        *   `state` (Optional[str]): State or province name.
        *   `country` (Optional[str]): Country name.
        *   `country_code` (Optional[str]): Two-letter ISO country code.
        *   `postal_code` (Optional[str]): Postal or ZIP code.
