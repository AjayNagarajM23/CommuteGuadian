# CommuteGuadian

CommuteGuardian is a sophisticated multi-agent system designed for real-time urban issue reporting and intelligent travel advisories. It leverages AI to analyze user-submitted reports of city anomalies (like floods or road damage) and provides predictive travel advice by synthesizing this data with historical incidents and weather forecasts.

## 🌟 Features

-   **Real-time Anomaly Reporting**: Users can report civic issues by capturing an image and sharing their geolocation through an intuitive web interface.
-   **AI-Powered Analysis**: Submitted images are automatically analyzed by an AI agent to describe and categorize the event (e.g., 'Environmental Hazard', 'Structural Damage').
-   **Intelligent Travel Advisories**: A chat-based interface allows users to query for routes. The system analyzes the path against a database of reported incidents, historical news data, and future weather predictions to offer safe and efficient travel advice.
-   **Multi-Agent Architecture**: The system is built on a robust architecture of specialized AI agents for data ingestion, analysis, and prediction.
-   **Interactive UI**: A user-friendly Streamlit application provides a seamless experience for both reporting issues and receiving travel guidance.

## 🏗️ Architecture

The project consists of three core, decoupled services that communicate with each other:

1.  **Streamlit UI (Frontend)**: The central hub for user interaction, providing two main functionalities:
    *   **Report Tab**: Allows users to submit anomaly reports with images.
    *   **Chat Tab**: Offers an interface to chat with the prediction agent for travel advice.

2.  **Data Ingestion Service (Backend)**: A FastAPI server that runs on port `8000`.
    *   It receives anomaly reports from the UI.
    *   It uses specialized sub-agents to process the data: one for analyzing the image content and another for resolving the geographic coordinates to a physical address.
    *   The processed data is stored locally in `submission_history.csv` and is intended to be warehoused in a database like BigQuery for long-term analysis.

3.  **Prediction Service (Backend)**: A FastAPI server that runs on port `9900`.
    *   It receives chat queries from the UI (e.g., "How do I get from A to B?").
    *   It queries a BigQuery database to find relevant incidents along the user's proposed route.
    *   It enriches this data by fetching historical news articles and future weather forecasts.
    *   A final prediction agent synthesizes all this information to generate a comprehensive travel advisory, which is sent back to the user in the chat.

## 🚀 Getting Started

Follow these instructions to set up and run the CommuteGuardian project on your local machine.

### Prerequisites

-   Python 3.9+
-   `uv` (or `pip`) for package installation.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd travelling_in_city
```

### 2. Install Dependencies

All the required Python packages are listed in the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

The agents may require API keys or other configuration. Ensure you have a `.env` file in the relevant agent directories (`Data_ingestion_agents/Data_ingest_1/Agents/Sub_Agent_1/tools/` and `prediction_agent/`) with the necessary credentials.

## 🏃‍♀️ How to Run

You need to run the three main components of the application in three separate terminal windows.

### Terminal 1: Start the Data Ingestion Service

```bash
cd Data_ingestion_agents/Data_ingest_1
uvicorn app:app --host 0.0.0.0 --port 8000
```
This service will handle the anomaly reports submitted from the UI.

### Terminal 2: Start the Prediction Service

```bash
cd prediction_agent
uvicorn app:app --host 0.0.0.0 --port 9900
```
This service will handle the chat-based travel queries.

### Terminal 3: Start the Streamlit UI

```bash
cd streamlit_ui
streamlit run streamlit_app.py
```
Once this is running, you can access the CommuteGuardian application in your web browser at `http://localhost:8501`.
