import pandas as pd
from datetime import datetime, timedelta, timezone
import asyncio # To run the async main function
import time

async def find_location_anomaly_match(locations: list) -> list:
    """
    Finds matching anomaly records from a Pandas DataFrame based on a list of street names.

    Args:
        locations: A list of street names to search for.

    Returns:
        A list of tuples, where each tuple represents a unique matching anomaly record.
    """
    # Return early if there's nothing to process

    df = pd.read_csv('/home/ajaynagaraj-m/travelling_in_city/streamlit_ui/submission_history.csv')

    if df.empty or not locations:
        return []

    # --- Data Validation ---
    # Ensure required columns exist to avoid errors
    required_cols = ['street_name', 'unix_timestamp', 'event_type', 'sub_event_type',
                     'area_name', 'city', 'description', 'severity_score']
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        raise ValueError(f"DataFrame is missing required columns: {missing_cols}")


    # --- Filtering Logic ---

    # 1. Filter by time
    # Get the timestamp for a very old date to replicate the original query's logic
    far_in_the_past_ts = (datetime.now(timezone.utc) - timedelta(hours=1000000)).timestamp()

    # Ensure the timestamp column is a numeric type before comparison
    df['unix_timestamp'] = pd.to_numeric(df['unix_timestamp'], errors='coerce')
    time_filtered_df = df[df['unix_timestamp'] >= far_in_the_past_ts].copy()

    if time_filtered_df.empty:
        return []

    # 2. Filter by location
    # Prepare input location strings for matching (case-insensitive and whitespace-stripped)
    clean_locations = [loc.strip().lower() for loc in locations]
    
    # Prepare the 'street_name' column in the DataFrame for an efficient, case-insensitive match
    time_filtered_df['processed_street_name'] = time_filtered_df['street_name'].astype(str).str.strip().str.lower()

    # Use .isin() for an efficient lookup of all locations at once
    matched_df = time_filtered_df[time_filtered_df['processed_street_name'].isin(clean_locations)]

    print("*"*100)
    print(clean_locations)
    print(time_filtered_df)
    print(matched_df)
    print("*"*100)
    # --- Process and Return Results ---

    # Define the columns for the final output, matching the original SELECT statement
    output_columns = [
        'event_type', 'sub_event_type', 'area_name', 'street_name',
        'city', 'description', 'severity_score'
    ]

    # Select the desired columns and remove duplicate rows to ensure unique matches
    unique_matches_df = matched_df[output_columns].drop_duplicates()

    # Convert the final DataFrame rows into a list of tuples for the return value
    matches = [tuple(row) for row in unique_matches_df.itertuples(index=False, name=None)]

    return matches

# --- Example Usage ---
async def main():
    # 1. Create a sample DataFrame that mimics your data structure
    data = {
        'event_type': ['Traffic', 'Infrastructure', 'Traffic', 'Weather'],
        'sub_event_type': ['Accident', 'Pothole', 'Accident', 'Flooding'],
        'area_name': ['Downtown', 'Suburbia', 'Downtown', 'Suburbia'],
        'street_name': ['Main St', 'Oak Avenue', ' Main St ', 'Elm Street'],
        'city': ['Metroburg', 'Townsville', 'Metroburg', 'Townsville'],
        'severity_score': [8, 5, 8, 7],
        'description': ['A two-car collision.', 'Large pothole reported.', 'A two-car collision.', 'Street is flooded.'],
        'unix_timestamp': [int(time.time()), int(time.time()) - 3600, int(time.time()) - 7200, int(time.time()) - 86400]
    }
    anomaly_df = pd.DataFrame(data)

    print("--- Sample DataFrame ---")
    print(anomaly_df)
    print("\n" + "="*30 + "\n")

    # 2. Define the locations to search for
    locations_to_find = ['main st', 'Maple Drive'] # Note the different casing and spacing

    # 3. Call the function with the DataFrame
    print(f"Searching for anomalies at: {locations_to_find}...")
    found_matches = await find_location_anomaly_match(locations_to_find, anomaly_df)

    # 4. Print the results
    if found_matches:
        print("\n--- Found Matches ---")
        for match in found_matches:
            print(match)
    else:
        print("\nNo matches found.")


if __name__ == "__main__":
    asyncio.run(main())