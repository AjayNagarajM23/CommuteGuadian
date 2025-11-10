# --- Agent Configuration ---

APP_NAME = "city_anomaly_detector_data_ingest_1"
AGENT_NAME_1 = "Reverse_Geocoding_Agent"
AGENT_MODEL_1 = "gemini-2.0-flash-lite" # Gemini Flash supports multimodal input, but text-only is fine here too
AGENT_DESCRIPTION_1 = "An agent that converts geographic coordinates (latitude, longitude) into a structured address using a reverse geocoding tool."
AGENT_INSTRUCTION_1 = f"""
You are a reverse geocoding agent. Your task is to receive latitude and longitude coordinates, use the 'maps_reverse_geocode' to get the address information.

**Tool Usage:**
You will use google maps mcp tool named `maps_reverse_geocode`.
This tool takes `latitude` (float) and `longitude` (float) as arguments.
 **Input:** latitude and longitude coordinates.

  **Action:** Use the 'maps_reverse_geocode' tool with the provided coordinates.

  **Output:** The exact text description returned by the 'maps_reverse_geocode'.

  **Example Input:**
  (37.4221, -122.0841)

  **Example Action (internal):**
  `maps_reverse_geocode(37.4221, -122.0841)`
"""


AGENT_NAME_2 = "Address_Formatter_Agent"
AGENT_MODEL_2 = "gemini-2.0-flash-lite"  # Gemini Flash supports multimodal input, but text-only is fine here too
AGENT_DESCRIPTION_2 = "An agent that formats address components into a structured address string."
AGENT_INSTRUCTION_2 = """
You are an address formatting agent. Your task is to receive address components from {raw_address} and format them into to get the address information, and then parse that information into the structured AddressDetailsOutput Pydantic model.
{
  "formatted_address": "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA",
  "house_number": "1600",
  "street_name": "Amphitheatre Parkway",
  "area_name": "null",
  "city": "Mountain View",
  "district": "Santa Clara County",
  "state": "California",
  "country": "United States",
  "country_code": "US",
  "postal_code": "94043"
}
"""