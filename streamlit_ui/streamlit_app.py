import streamlit as st
import requests
import time
import base64
import pandas as pd
import os
from streamlit_js_eval import streamlit_js_eval

# Note: This application requires 'streamlit-js-eval' and 'pandas'.
# Install them using: pip install streamlit-js-eval pandas

st.set_page_config(
   page_title="CommuteGuardian",
   page_icon="icon.jpeg", # Local image file
   layout="centered"
)

# --- Initialize Session State ---
# This ensures that our variables persist across reruns.

# For Data Ingestion Tab
if 'responses_df' not in st.session_state:
    try:
        st.session_state.responses_df = pd.read_csv("submission_history.csv")
    except FileNotFoundError:
        st.session_state.responses_df = pd.DataFrame()

if 'latitude' not in st.session_state:
    st.session_state.latitude = 37.42200
if 'longitude' not in st.session_state:
    st.session_state.longitude = -122.08400
if 'location_fetched' not in st.session_state:
    st.session_state.location_fetched = False

# For Chat Tab
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []


# --- Create Tabs ---
tab1, tab2 = st.tabs(["Report", "Chat"])


# ==============================================================================
# --- TAB 1: DATA INGESTION ---
# ==============================================================================
with tab1:
    st.header("Report Issues")
    st.write("This UI sends a request with image and location data to the data ingestion agent and appends the history to a local CSV file.")

    # --- Automatic Geolocation on Load ---
    if not st.session_state.location_fetched:
        st.info("Fetching your live location for the Data Ingestion tab... Please grant permission if prompted.")
        loc = streamlit_js_eval(js_expressions='''
            new Promise(resolve => {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(position => {
                        resolve({
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        });
                    }, error => {
                        resolve({error: error.message});
                    });
                } else {
                    resolve({error: "Geolocation is not supported by this browser."});
                }
            })
        ''', key="get_location")

        if isinstance(loc, dict) and 'error' not in loc:
            st.session_state.latitude = loc["latitude"]
            st.session_state.longitude = loc["longitude"]
            st.session_state.location_fetched = True
            st.rerun() # Rerun to update the input fields with fetched location
        elif isinstance(loc, dict) and 'error' in loc:
            st.error(f"Could not get location: {loc['error']}")
            st.session_state.location_fetched = True

    # --- 

    captured_image = None

    captured_image = st.camera_input("Capture Image")

    # --- Other Inputs ---
    st.number_input("Latitude", key="latitude", format="%.5f")
    st.number_input("Longitude", key="longitude", format="%.5f")
    user_input = st.text_input("User Input", value="string", key="ingestion_user_input")
    user_id = st.text_input("User ID", value="anonymous_reporter", key="ingestion_user_id")
    session_id = st.text_input("Session ID", value="default_anomaly_session", key="ingestion_session_id")

    if st.button("Submit to Ingestion Agent"):
        payload = {
            "time": time.time(),
            "latitude": st.session_state.latitude,
            "longitude": st.session_state.longitude,
            "user_input": user_input,
            "user_id": user_id,
            "session_id": session_id
        }

        image_provided = False
        if captured_image is not None:
            img_bytes = captured_image.getvalue()
            mime_type = "image/jpeg"
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            payload["image_data_base64"] = f"data:{mime_type};base64,{img_base64}"
            image_provided = True

        if image_provided:
            try:
                st.info("Sending request to the backend...")
                response = requests.post("http://0.0.0.0:8000/query", json=payload)
                response.raise_for_status()
                st.success("Request sent successfully!")

                response_data = response.json()
                st.json(response_data)

                new_entry_df = pd.DataFrame([response_data])
                file_path = "submission_history.csv"
                new_entry_df.to_csv(
                    file_path,
                    mode='a',
                    header=not os.path.exists(file_path),
                    index=False
                )
                st.success(f"Response appended to {file_path}")

                st.session_state.responses_df = pd.concat(
                    [st.session_state.responses_df, new_entry_df],
                    ignore_index=True
                )

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please provide an image (either URL or camera capture).")

    # --- Display the full history ---
    st.subheader("Submission History")
    if not st.session_state.responses_df.empty:
        st.dataframe(st.session_state.responses_df)
    else:
        st.write("No submissions have been made yet. The submission_history.csv will be created after the first successful submission.")


# ==============================================================================
# --- TAB 2: CHAT ---
# ==============================================================================
with tab2:
    st.header("Chat ")
    st.write("Enter your message below to chat with the AI agent.")

    # Add inputs for user_id and session_id for the chat
    chat_user_id = st.text_input("User ID", value="anonymous_reporter", key="chat_user_id")
    chat_session_id = st.text_input("Session ID", value="default_anomaly_session", key="chat_session_id")
    st.divider()

    # Display chat messages from history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask about your route... e.g., 'I want to go from tata elxsi ltd hoodi to silkboard'"):
        # Add user message to chat history and display
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in a streaming fashion
        with st.chat_message("assistant"):
            try:
                # Construct payload according to the new schema
                chat_payload = {
                    "user_input": prompt,
                    "user_id": chat_user_id,
                    "session_id": chat_session_id
                }
                
                # Send request to the chat backend
                response = requests.post("http://0.0.0.0:9900/query", json=chat_payload)
                response.raise_for_status() # Raise an exception for bad status codes

                response_data = response.json()
                
                # Extract the final output from the response
                final_output = response_data.get("final_output", "Sorry, I received an unexpected response format.")

                # Helper function to yield words for a streaming effect
                def stream_data(text):
                    for word in text.split(" "):
                        yield word + " "
                        time.sleep(0.02) # Adjust sleep time for desired speed

                # Use st.write_stream to display the response with a typewriter effect
                st.write_stream(stream_data(final_output))

                # Add the complete assistant response to chat history after streaming
                st.session_state.chat_messages.append({"role": "assistant", "content": final_output})

            except requests.exceptions.RequestException as e:
                error_message = f"Failed to get a response from the chat agent: {e}"
                st.error(error_message)
                # Add the error to the chat history so it's visible in the UI
                st.session_state.chat_messages.append({"role": "assistant", "content": error_message})