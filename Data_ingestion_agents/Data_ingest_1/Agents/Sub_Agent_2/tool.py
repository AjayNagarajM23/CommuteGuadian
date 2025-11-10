"""
Temp tool logic for testing, instead of using the Google Maps MCP toolset
"""

def reverse_geocode_tool(longitude:float, latitude:float) -> dict:
    print(f"Reverse geocoding for coordinates: {longitude}, {latitude}")
    return {
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
The actual tool logic for production
"""
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
import os
from dotenv import load_dotenv

load_dotenv()

google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
if not google_maps_api_key:
    # Fallback or direct assignment for testing - NOT RECOMMENDED FOR PRODUCTION
    google_maps_api_key = "YOUR_GOOGLE_MAPS_API_KEY_HERE" # Replace if not using env var
    if google_maps_api_key == "YOUR_GOOGLE_MAPS_API_KEY_HERE":
        print("WARNING: GOOGLE_MAPS_API_KEY is not set. Please set it as an environment variable or in the script.")
        # You might want to raise an error or exit if the key is crucial and not found.
tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-google-maps",
                    ],
                    # Pass the API key as an environment variable to the npx process
                    # This is how the MCP server for Google Maps expects the key.
                    env={
                        "GOOGLE_MAPS_API_KEY": google_maps_api_key
                    },
                ),
                timeout=180.0
            ),
            # You can filter for specific Maps tools if needed:
            tool_filter=['maps_reverse_geocode']
        )
    ]