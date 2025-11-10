from google import genai
from google.genai import types
import requests
import logging
import asyncio # Import asyncio for running async functions
import base64
import re
from dotenv import load_dotenv
load_dotenv()

# Configure logging
# It's good practice to get a logger by name, typically using __name__
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Set the minimum level of messages to log

# Create a handler (e.g., to output logs to the console)
# You could also use FileHandler to log to a file
handler = logging.StreamHandler()

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

PROMPT = """
Identify all significant city events and anomalies. Detail the type, Explanation, and describe the severeness  of each. 
Focus on any elements indicating damage, disruption, or unusual activity (e.g., structural issues, traffic 
incidents, environmental hazards, utility problems, public safety concerns, weather impacts). Be concise but 
specific about what makes each an anomaly. if there is no anomaly in the image return Normal.
"""

async def get_image_description(base64_image_string: str) -> str:
    logger.info("Attempting to describe image from base64 string.")

    try:
        # --- FIX ---
        # Check if the data URI prefix exists
        match = re.match(r'data:(image/\w+);base64,(.*)', base64_image_string)
        if match:
            # If it exists, extract mime type and data
            mime_type, base64_data = match.groups()
        else:
            # If it doesn't exist, assume a default mime type and use the whole string
            logger.warning("Base64 string does not have a data URI prefix. Assuming image/jpeg.")
            mime_type = "image/jpeg" # Or another sensible default
            base64_data = base64_image_string
        # --- END FIX ---

        image_bytes = base64.b64decode(base64_data)
        logger.debug(f"Successfully decoded base64 string with MIME type: {mime_type}")

    except (base64.binascii.Error, TypeError) as e:
        logger.error(f"Failed to decode base64 string. Error: {e}")
        return f"Error: Could not decode base64 string. {e}"
    except Exception as e:
        logger.error(f"An unexpected error occurred during base64 processing. Error: {e}")
        return f"Error: An unexpected error occurred. {e}"


    try:
        image = types.Part.from_bytes(
            data=image_bytes, mime_type=mime_type
        )
        logger.debug("Successfully created image Part object.")
    except Exception as e:
        logger.error(f"Failed to create image Part object. Error: {e}")
        return f"Error: Failed to process image data. {e}"

    try:
        # Note: The genai library's default client is synchronous.
        # For a truly async operation in a larger application, you might use
        # an async client if available or run this synchronous call in a thread pool
        # to avoid blocking the asyncio event loop.
        # For this script, we'll call it directly.
        client = client = genai.Client()
        
        # The generate_content method itself is not awaitable with the standard client.
        # To avoid a TypeError, we run the synchronous call in a thread pool.
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[PROMPT, image],
        )
        
        logger.info("Successfully generated content from Gemini Flash model.")
        return response.text
    except Exception as e:
        logger.error(f"Failed to generate content from Gemini Flash model. Error: {e}")
        return f"Error: Failed to get image description from model. {e}"

# Example usage
async def main():
    # This is a sample 1x1 pixel red dot JPEG as a base64 string.
    # Replace with your actual base64 encoded image string for testing.
    test_base64_image = (
        "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcG"
        "BwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwM"
        "DAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcI"
        "CQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo"
        "0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5us"
        "LDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QA"
        "tREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg"
        "5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcb"
        "HyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD9/KKKKAP/2Q=="
    )
    
    # Configure your API key
    # genai.configure(api_key="YOUR_API_KEY")

    description = await get_image_description(test_base64_image)
    print("\n--- Image Description ---")
    print(description)

if __name__ == "__main__":
    # Note: You need to have the GOOGLE_API_KEY environment variable set,
    # or configure the API key directly via genai.configure(api_key="...")
    asyncio.run(main())